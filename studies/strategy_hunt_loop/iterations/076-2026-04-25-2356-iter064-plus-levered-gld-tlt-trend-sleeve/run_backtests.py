"""Iter 076 — Run iter 064 + LEVERED GLD/TLT trend sleeve ensemble on 3 datasets × 20 cfgs.

Architecture:
  1. Load iter 064 saved daily-return stream per dataset.
  2. For each ``target_vol`` ∈ {0.10, 0.15, 0.20, 0.25, 0.30}, compute
     the LEVERED GLD/TLT trend sleeve daily-return stream once per
     dataset (Faber 2007 SMA-200 trend filter, 21d inverse-vol sized,
     leg_cap=3.0, borrow_rate=4.5%, equal-weight blend).
  3. For each (target_vol × w_sleeve) cfg pair (4 × 5 = 20 cfgs),
     linearly blend at ``r_076[t] = w_064 · r_064[t] + w_sleeve · r_sleeve[t]``.
  4. Save streams + per-cfg metrics + crosslib parity to results.json.

Note: iter 076 uses 4 target_vol levels {0.15, 0.20, 0.25, 0.30}
because target_vol=0.10 with leg_cap=3.0 + borrow=0.045 reduces to the
unlevered iter 075 case (no excess pos → no drag) and would duplicate
known iter 075 results without testing the leverage hypothesis. The
iter 075 baseline is preserved in the iter 075 results.json for direct
comparison.

n_trials_per_iter = 20 (per-iteration v2 DSR convention).
cumulative_n_trials advance: 4402 → 4462 (+60 = 20 cfgs × 3 datasets).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
sys.path.insert(0, str(ITER_DIR))

from iter076_sleeve import (  # noqa: E402
    ITER_064_CFG_ID,
    combine_iter064_with_sleeve,
    compute_sleeve_returns,
    load_iter064_stream,
    load_price,
)
from numpy_reference_iter076 import (  # noqa: E402
    combine_iter064_with_sleeve_np,
    compute_sleeve_returns_np,
)

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"

# Sweep grid: 4 target_vol × 5 w_sleeve = 20 cfgs
TARGET_VOL_GRID = [0.15, 0.20, 0.25, 0.30]
WEIGHT_GRID = [0.15, 0.25, 0.35, 0.45, 0.50]

# Frozen sleeve hyperparameters (NOT swept, except target_vol above)
LEG_CAP = 3.0
BORROW_RATE_ANNUAL = 0.045
SMA_LOOKBACK = 200
VOL_LOOKBACK = 21


def cfg_id_for(target_vol: float, w_sleeve: float) -> str:
    return (
        f"iter076_lev_tv{int(round(target_vol * 100)):03d}_"
        f"w{int(round(w_sleeve * 100)):03d}"
    )


CONFIGS: list[dict] = [
    {
        "cfg_id": cfg_id_for(tv, w),
        "target_vol": float(tv),
        "leg_cap": LEG_CAP,
        "borrow_rate_annual": BORROW_RATE_ANNUAL,
        "w_sleeve": float(w),
        "w_064": float(round(1.0 - w, 6)),
        "leg_a_iter": "064",
        "leg_a_cfg_id": ITER_064_CFG_ID,
        "leg_b_iter": "076-sleeve",
        "leg_b_cfg_id": (
            f"gld_tlt_sma200_volt{int(round(tv * 100)):03d}_"
            f"cap{int(LEG_CAP * 10):02d}_borrow{int(BORROW_RATE_ANNUAL * 1000):03d}"
        ),
        "primary_citation": (
            "[leverage_for_the_long_run, ch.5] (Hsiao-Williams 2017 borrow primitive) + "
            "Faber (2007) SSRN 962461 + [stocks_on_the_move, p.81] + "
            "[risk_parity, ch.5] (Asness-Frazzini-Pedersen 2012 FAJ 68(1)) + "
            "Erb-Harvey (2006) FAJ 62(2) DOI 10.2469/faj.v62.i2.4084 + "
            "[volatility_trading, p.218] + Markowitz (1952) JoF 7(1) "
            "DOI 10.1111/j.1540-6261.1952.tb01525.x + "
            "Frazzini-Pedersen (2014) JFE 111(1) DOI 10.1016/j.jfineco.2013.10.005 + "
            "[advances_fin_ml, p.222-223] (DSR per-iter v2)"
        ),
    }
    for tv in TARGET_VOL_GRID
    for w in WEIGHT_GRID
]

DATASETS: dict[str, dict] = {
    "educational": {
        "bench_ticker": "SPY",
        "start": "2006-01-03",
        "end": "2026-04-15",
        "role": "20y combined; iter 064 + LEVERED GLD/TLT-trend sleeve",
    },
    "spy_real": {
        "bench_ticker": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "17y post-GFC; iter 064 + LEVERED GLD/TLT-trend sleeve",
    },
    "ndx_real": {
        "bench_ticker": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "16y; iter 064 + LEVERED GLD/TLT-trend sleeve; bench QQQ",
    },
}


def load_prices_window(symbol: str, start: str, end: str) -> pd.Series:
    df = pd.read_parquet(TIINGO_DIR / f"{symbol}.parquet")
    m = (df.index >= start) & (df.index <= end)
    return df.loc[m, "adj_close"].astype(float)


def benchmark_metrics(returns: pd.Series) -> dict:
    eq = (1.0 + returns).cumprod()
    return {
        "sharpe": float(_sharpe(returns)),
        "cagr": float(_cagr(eq)),
        "mdd": float(_max_drawdown(eq)),
        "n_bars": int(len(returns)),
        "first": str(returns.index[0].date()),
        "last": str(returns.index[-1].date()),
    }


def markowitz_residual(
    r_a: pd.Series, r_b: pd.Series, *, w_a: float, w_b: float,
    observed_sharpe: float,
) -> tuple[float, dict]:
    common = r_a.index.intersection(r_b.index)
    a = r_a.loc[common].values
    b = r_b.loc[common].values
    mu_a = float(np.mean(a))
    mu_b = float(np.mean(b))
    var_a = float(np.var(a, ddof=0))
    var_b = float(np.var(b, ddof=0))
    cov_ab = float(np.cov(a, b, ddof=0)[0, 1])
    mu_p = w_a * mu_a + w_b * mu_b
    var_p = (w_a ** 2) * var_a + (w_b ** 2) * var_b + 2 * w_a * w_b * cov_ab
    sigma_p = float(np.sqrt(var_p))
    formula_sharpe = (mu_p / sigma_p) * np.sqrt(252.0) if sigma_p > 1e-12 else 0.0
    return observed_sharpe - formula_sharpe, {
        "formula_sharpe": float(formula_sharpe),
        "observed_sharpe": float(observed_sharpe),
        "mu_a": mu_a, "mu_b": mu_b,
        "sigma_a": float(np.sqrt(var_a)), "sigma_b": float(np.sqrt(var_b)),
        "corr_ab": float(cov_ab / (np.sqrt(var_a * var_b) + 1e-18)),
        "n_bars_used": int(len(common)),
    }


def run_single_cfg(
    r_064: pd.Series, sleeves_by_tv: dict[float, pd.Series], cfg: dict,
) -> tuple[dict, pd.Series]:
    r_sleeve = sleeves_by_tv[cfg["target_vol"]]
    combined = combine_iter064_with_sleeve(
        r_064, r_sleeve, w_064=cfg["w_064"], w_sleeve=cfg["w_sleeve"],
    )
    eq_curve = (1.0 + combined).cumprod()
    common = combined.index
    r_064_a = r_064.loc[common]
    r_sleeve_a = r_sleeve.loc[common]
    corr_legs = float(r_064_a.corr(r_sleeve_a))
    obs_sharpe = float(_sharpe(combined))
    residual, mw = markowitz_residual(
        r_064_a, r_sleeve_a,
        w_a=cfg["w_064"], w_b=cfg["w_sleeve"],
        observed_sharpe=obs_sharpe,
    )
    m = {
        "cfg_id": cfg["cfg_id"],
        "target_vol": cfg["target_vol"],
        "w_064": cfg["w_064"],
        "w_sleeve": cfg["w_sleeve"],
        "leg_cap": cfg["leg_cap"],
        "borrow_rate_annual": cfg["borrow_rate_annual"],
        "bars": int(len(combined)),
        "sharpe": obs_sharpe,
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "corr_064_sleeve": corr_legs,
        "r_064_sharpe": float(_sharpe(r_064_a)),
        "r_064_cagr": float(_cagr((1.0 + r_064_a).cumprod())),
        "r_064_mdd": float(_max_drawdown((1.0 + r_064_a).cumprod())),
        "r_sleeve_sharpe": float(_sharpe(r_sleeve_a)),
        "r_sleeve_cagr": float(_cagr((1.0 + r_sleeve_a).cumprod())),
        "r_sleeve_mdd": float(_max_drawdown((1.0 + r_sleeve_a).cumprod())),
        "markowitz_residual_sharpe": residual,
        "markowitz_detail": mw,
    }
    return m, combined


def cross_lib_check_for_cfg(
    r_064_aligned: pd.Series, sleeves_aligned: dict[float, pd.Series], cfg: dict,
) -> dict:
    r_sleeve_aligned = sleeves_aligned[cfg["target_vol"]]
    pd_out = combine_iter064_with_sleeve(
        r_064_aligned, r_sleeve_aligned,
        w_064=cfg["w_064"], w_sleeve=cfg["w_sleeve"],
    )
    np_out = combine_iter064_with_sleeve_np(
        r_064_aligned.values, r_sleeve_aligned.values,
        w_064=cfg["w_064"], w_sleeve=cfg["w_sleeve"],
    )
    eq_pd = np.cumprod(1.0 + pd_out.values)
    eq_np = np.cumprod(1.0 + np_out)
    n = len(pd_out)
    cagr_pd = float(eq_pd[-1]) ** (252.0 / n) - 1.0
    cagr_np = float(eq_np[-1]) ** (252.0 / n) - 1.0
    return {
        "cagr_pandas": cagr_pd,
        "cagr_numpy": cagr_np,
        "abs_diff_pp": abs(cagr_pd - cagr_np) * 100.0,
        "max_abs_return_diff": float(np.max(np.abs(pd_out.values - np_out))),
        "n_bars_compared": n,
    }


def cross_lib_check_sleeve(
    prices_gld: pd.Series, prices_tlt: pd.Series, target_vol: float,
) -> dict:
    """G7 parity for the sleeve itself at the given target_vol."""
    pd_out = compute_sleeve_returns(
        prices_gld, prices_tlt,
        sma_lookback=SMA_LOOKBACK, vol_lookback=VOL_LOOKBACK,
        target_vol=target_vol, leg_cap=LEG_CAP,
        borrow_rate_annual=BORROW_RATE_ANNUAL,
    )
    common = prices_gld.index.intersection(prices_tlt.index)
    np_out = compute_sleeve_returns_np(
        prices_gld.loc[common].values,
        prices_tlt.loc[common].values,
        sma_lookback=SMA_LOOKBACK, vol_lookback=VOL_LOOKBACK,
        target_vol=target_vol, leg_cap=LEG_CAP,
        borrow_rate_annual=BORROW_RATE_ANNUAL,
    )
    eq_pd = np.cumprod(1.0 + pd_out.values)
    eq_np = np.cumprod(1.0 + np_out)
    n = len(pd_out)
    cagr_pd = float(eq_pd[-1]) ** (252.0 / n) - 1.0
    cagr_np = float(eq_np[-1]) ** (252.0 / n) - 1.0
    return {
        "cagr_pandas": cagr_pd,
        "cagr_numpy": cagr_np,
        "abs_diff_pp": abs(cagr_pd - cagr_np) * 100.0,
        "max_abs_return_diff": float(np.max(np.abs(pd_out.values - np_out))),
        "n_bars_compared": n,
        "target_vol": target_vol,
    }


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": CONFIGS,
        "sleeve_params": {
            "sma_lookback": SMA_LOOKBACK,
            "vol_lookback": VOL_LOOKBACK,
            "leg_cap": LEG_CAP,
            "borrow_rate_annual": BORROW_RATE_ANNUAL,
            "target_vol_grid": TARGET_VOL_GRID,
            "weight_grid": WEIGHT_GRID,
        },
        "benchmarks": {},
        "runs": {ds: {} for ds in DATASETS},
        "returns_series": {ds: {} for ds in DATASETS},
        "subcomponent_returns": {},
        "crosslib": {ds: {} for ds in DATASETS},
        "crosslib_sleeve": {ds: {} for ds in DATASETS},
        "pre_committed": True,
        "iter_label": "076-2026-04-25-2356-iter064-plus-levered-gld-tlt-trend-sleeve",
        "n_trials_per_iter": len(CONFIGS),
    }

    gld_full = load_price("GLD")
    tlt_full = load_price("TLT")

    for ds_name, ds in DATASETS.items():
        r_064 = load_iter064_stream(ds_name)

        bench_p = load_prices_window(ds["bench_ticker"], ds["start"], ds["end"])
        bench_series = bench_p.pct_change().dropna()
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench

        ds_start = r_064.index[0]
        ds_end = r_064.index[-1]
        gld = gld_full.loc[(gld_full.index >= ds_start) & (gld_full.index <= ds_end)]
        tlt = tlt_full.loc[(tlt_full.index >= ds_start) & (tlt_full.index <= ds_end)]

        # Compute one sleeve per target_vol level
        sleeves_by_tv: dict[float, pd.Series] = {}
        for tv in TARGET_VOL_GRID:
            sleeve = compute_sleeve_returns(
                gld, tlt,
                sma_lookback=SMA_LOOKBACK, vol_lookback=VOL_LOOKBACK,
                target_vol=tv, leg_cap=LEG_CAP,
                borrow_rate_annual=BORROW_RATE_ANNUAL,
            )
            sleeves_by_tv[tv] = sleeve
            cl = cross_lib_check_sleeve(gld, tlt, tv)
            all_results["crosslib_sleeve"][ds_name][f"tv{int(round(tv*100)):03d}"] = cl

        common = r_064.index.intersection(sleeves_by_tv[TARGET_VOL_GRID[0]].index)
        # Sleeve crosslib summary line per dataset
        max_diff_pp = max(
            all_results["crosslib_sleeve"][ds_name][k]["abs_diff_pp"]
            for k in all_results["crosslib_sleeve"][ds_name]
        )
        print(
            f"\n=== {ds_name} ===\n"
            f"  iter 064 stream: [{r_064.index[0].date()} → {r_064.index[-1].date()}] ({len(r_064)} bars)\n"
            f"  sleeve target_vol grid: {TARGET_VOL_GRID}\n"
            f"  inner-join:      [{common[0].date()} → {common[-1].date()}] ({len(common)} bars)\n"
            f"  benchmark {ds['bench_ticker']:>4}: Sharpe={bench['sharpe']:.4f} "
            f"CAGR={bench['cagr']:.2%} MDD={bench['mdd']:.2%}\n"
            f"  sleeve crosslib (max across {len(TARGET_VOL_GRID)} tv): "
            f"CAGR Δpp={max_diff_pp:.6f}"
        )

        # Save iter 064 stream + each sleeve once per dataset
        sub = {
            "r_064": {
                "index": [str(t.date()) for t in r_064.loc[common].index],
                "net_returns": [round(float(x), 10) for x in r_064.loc[common].tolist()],
            },
        }
        for tv in TARGET_VOL_GRID:
            sl = sleeves_by_tv[tv].loc[common]
            sub[f"r_sleeve_tv{int(round(tv*100)):03d}"] = {
                "index": [str(t.date()) for t in sl.index],
                "net_returns": [round(float(x), 10) for x in sl.tolist()],
            }
        all_results["subcomponent_returns"][ds_name] = sub

        r_064_aligned = r_064.loc[common]
        sleeves_aligned = {tv: sleeves_by_tv[tv].loc[common] for tv in TARGET_VOL_GRID}

        for cfg in CONFIGS:
            m, combined = run_single_cfg(r_064, sleeves_by_tv, cfg)
            all_results["runs"][ds_name][cfg["cfg_id"]] = m
            all_results["returns_series"][ds_name][cfg["cfg_id"]] = {
                "index": [str(t.date()) for t in combined.index],
                "net_returns": [round(float(x), 10) for x in combined.tolist()],
            }
            cl = cross_lib_check_for_cfg(r_064_aligned, sleeves_aligned, cfg)
            all_results["crosslib"][ds_name][cfg["cfg_id"]] = cl
            edge_frozen = m["sharpe"] - {
                "educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955,
            }[ds_name]
            print(
                f"  {cfg['cfg_id']:42s} S={m['sharpe']:+.4f} "
                f"(Δ frozen={edge_frozen:+.4f}) CAGR={m['cagr']:+.2%} "
                f"MDD={m['mdd']:.2%} corr(064,sl)={m['corr_064_sleeve']:+.3f} "
                f"sleeve_S={m['r_sleeve_sharpe']:+.3f} "
                f"sleeve_CAGR={m['r_sleeve_cagr']:+.2%} "
                f"G7 Δpp={cl['abs_diff_pp']:.6f}"
            )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(
        json.dumps(all_results, indent=2, default=str), encoding="utf-8",
    )
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
