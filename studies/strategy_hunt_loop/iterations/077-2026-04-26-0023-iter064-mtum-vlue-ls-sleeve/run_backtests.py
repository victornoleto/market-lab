"""Iter 077 — Run iter 064 + MTUM/VLUE long-short sleeve ensemble on 3 datasets × 20 cfgs.

Architecture (mirrors iter 075/076 driver):
  1. Load iter 064 saved daily-return stream per dataset.
  2. Compute the MTUM−VLUE long-short sleeve daily-return stream once
     per (target_vol, leg_cap) tuple per dataset (5 vol-targets × 1 cap).
  3. For each of 20 cfgs (5 target_vol × 4 w_sleeve), linearly blend at
     ``r_077[t] = w_064 · r_064[t] + w_sleeve · r_sleeve[t]``.
  4. Save streams + per-cfg metrics + crosslib parity to results.json.

n_trials_per_iter = 20 (per-iteration v2 DSR convention).
cumulative_n_trials advance: 4462 → 4522 (+60 = 20 cfgs × 3 datasets).
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

from mtum_vlue_sleeve import (  # noqa: E402
    ITER_064_CFG_ID,
    combine_iter064_with_sleeve,
    compute_sleeve_returns,
    load_iter064_stream,
    load_price,
)
from numpy_reference_iter077 import (  # noqa: E402
    combine_iter064_with_sleeve_np,
    compute_sleeve_returns_np,
)

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"

TARGET_VOLS = [0.06, 0.08, 0.10, 0.12, 0.15]
W_SLEEVES = [0.10, 0.20, 0.30, 0.40]
LEG_CAP = 1.5
SHORT_BORROW_RATE = 0.01  # 1%/yr — retail-margin securities-lending fee on liquid ETFs
TRANS_COST_BPS = 5.0      # 5 bps on |Δposition|, matches iter 075 tc
VOL_LOOKBACK = 21


def cfg_id_for(tv: float, w: float) -> str:
    return f"iter077_lsfac_tv{int(round(tv * 100)):03d}_w{int(round(w * 100)):03d}"


CONFIGS: list[dict] = [
    {
        "cfg_id": cfg_id_for(tv, w),
        "target_vol": float(tv),
        "leg_cap": float(LEG_CAP),
        "w_sleeve": float(w),
        "w_064": float(round(1.0 - w, 6)),
        "short_borrow_rate": float(SHORT_BORROW_RATE),
        "trans_cost_bps": float(TRANS_COST_BPS),
        "primary_citation": (
            "Carhart (1997) JoF 52(1) DOI 10.1111/j.1540-6261.1997.tb03808.x "
            "+ Asness-Moskowitz-Pedersen (2013) JoF 68(3) DOI 10.1111/jofi.12021 "
            "+ [advances_fin_ml, ch.3, p.222-223] "
            "+ [volatility_trading, p.218] "
            "+ Frazzini-Pedersen (2014) JFE 111(1) DOI 10.1016/j.jfineco.2013.10.005 "
            "+ Markowitz (1952) JoF 7(1)"
        ),
    }
    for tv in TARGET_VOLS for w in W_SLEEVES
]

DATASETS: dict[str, dict] = {
    "educational": {
        "bench_ticker": "SPY",
        "start": "2006-01-03",
        "end": "2026-04-15",
        "role": "20y combined; sleeve off pre-2013-04 (MTUM/VLUE inception)",
    },
    "spy_real": {
        "bench_ticker": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "17y post-GFC; sleeve off pre-2013-04 (3.8y warmup)",
    },
    "ndx_real": {
        "bench_ticker": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "16y; sleeve off pre-2013-04 (3.2y warmup); bench QQQ",
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
        "mu_a": mu_a,
        "mu_b": mu_b,
        "sigma_a": float(np.sqrt(var_a)),
        "sigma_b": float(np.sqrt(var_b)),
        "corr_ab": float(cov_ab / (np.sqrt(var_a * var_b) + 1e-18)),
        "n_bars_used": int(len(common)),
    }


def run_single_cfg(
    r_064: pd.Series, sleeves_by_tv: dict[float, pd.Series],
    bench_returns: pd.Series,
    cfg: dict,
) -> tuple[dict, pd.Series]:
    r_sleeve = sleeves_by_tv[cfg["target_vol"]]
    combined = combine_iter064_with_sleeve(
        r_064, r_sleeve, w_064=cfg["w_064"], w_sleeve=cfg["w_sleeve"],
    )
    eq_curve = (1.0 + combined).cumprod()
    common = combined.index
    r_064_a = r_064.reindex(common).fillna(0.0)
    r_sleeve_a = r_sleeve.reindex(common).fillna(0.0)
    corr_legs = float(r_064_a.corr(r_sleeve_a))
    bench_a = bench_returns.reindex(common).fillna(0.0)
    corr_sleeve_bench = float(r_sleeve_a.corr(bench_a))
    obs_sharpe = float(_sharpe(combined))
    residual, mw = markowitz_residual(
        r_064_a, r_sleeve_a,
        w_a=cfg["w_064"], w_b=cfg["w_sleeve"],
        observed_sharpe=obs_sharpe,
    )
    m = {
        "cfg_id": cfg["cfg_id"],
        "target_vol": cfg["target_vol"],
        "leg_cap": cfg["leg_cap"],
        "w_064": cfg["w_064"],
        "w_sleeve": cfg["w_sleeve"],
        "bars": int(len(combined)),
        "sharpe": obs_sharpe,
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "corr_064_sleeve": corr_legs,
        "corr_sleeve_bench": corr_sleeve_bench,
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
    r_064: pd.Series, r_sleeve: pd.Series, cfg: dict,
) -> dict:
    """G7 parity check on the convex-blend math.

    Compares pandas and numpy combine on the inner-join of the two
    legs (where both have data). The phase-in logic (pre-sleeve =
    full iter 064 weight) is pure pandas date-handling and is tested
    separately by ``test_combine_phase_in_preserves_iter064_pre_sleeve``;
    the numpy reference operates only on aligned arrays.
    """
    common = r_064.index.intersection(r_sleeve.index)
    a = r_064.loc[common].astype(float)
    b = r_sleeve.loc[common].astype(float)
    # On the inner-join the pandas combine collapses to pure convex blend
    # (sleeve_present everywhere ⇒ eff_w_064 = w_064 throughout).
    pd_out = combine_iter064_with_sleeve(
        a, b, w_064=cfg["w_064"], w_sleeve=cfg["w_sleeve"],
    )
    np_out = combine_iter064_with_sleeve_np(
        a.values, b.values,
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
    prices_mtum: pd.Series, prices_vlue: pd.Series, target_vol: float,
) -> dict:
    """G7 parity for the sleeve itself (per target_vol)."""
    pd_out = compute_sleeve_returns(
        prices_mtum, prices_vlue,
        vol_lookback=VOL_LOOKBACK, target_vol=target_vol, leg_cap=LEG_CAP,
        short_borrow_rate=SHORT_BORROW_RATE, trans_cost_bps=TRANS_COST_BPS,
    )
    common = prices_mtum.index.intersection(prices_vlue.index)
    np_out = compute_sleeve_returns_np(
        prices_mtum.loc[common].values,
        prices_vlue.loc[common].values,
        vol_lookback=VOL_LOOKBACK, target_vol=target_vol, leg_cap=LEG_CAP,
        short_borrow_rate=SHORT_BORROW_RATE, trans_cost_bps=TRANS_COST_BPS,
    )
    eq_pd = np.cumprod(1.0 + pd_out.values)
    eq_np = np.cumprod(1.0 + np_out)
    n = len(pd_out)
    cagr_pd = float(eq_pd[-1]) ** (252.0 / n) - 1.0
    cagr_np = float(eq_np[-1]) ** (252.0 / n) - 1.0
    return {
        "target_vol": target_vol,
        "cagr_pandas": cagr_pd,
        "cagr_numpy": cagr_np,
        "abs_diff_pp": abs(cagr_pd - cagr_np) * 100.0,
        "max_abs_return_diff": float(np.max(np.abs(pd_out.values - np_out))),
        "n_bars_compared": n,
    }


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": CONFIGS,
        "sleeve_params": {
            "vol_lookback": VOL_LOOKBACK,
            "leg_cap": LEG_CAP,
            "short_borrow_rate": SHORT_BORROW_RATE,
            "trans_cost_bps": TRANS_COST_BPS,
        },
        "benchmarks": {},
        "runs": {ds: {} for ds in DATASETS},
        "returns_series": {ds: {} for ds in DATASETS},
        "subcomponent_returns": {},
        "crosslib": {ds: {} for ds in DATASETS},
        "crosslib_sleeve": {ds: [] for ds in DATASETS},
        "pre_committed": True,
        "iter_label": "077-2026-04-26-0023-iter064-mtum-vlue-ls-sleeve",
        "n_trials_per_iter": len(CONFIGS),
    }

    mtum_full = load_price("MTUM")
    vlue_full = load_price("VLUE")

    for ds_name, ds in DATASETS.items():
        r_064 = load_iter064_stream(ds_name)

        bench_p = load_prices_window(ds["bench_ticker"], ds["start"], ds["end"])
        bench_series = bench_p.pct_change().dropna()
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench

        # Restrict MTUM/VLUE prices to the dataset window inferred from r_064.
        ds_start = r_064.index[0]
        ds_end = r_064.index[-1]
        mtum = mtum_full.loc[(mtum_full.index >= ds_start) & (mtum_full.index <= ds_end)]
        vlue = vlue_full.loc[(vlue_full.index >= ds_start) & (vlue_full.index <= ds_end)]

        sleeves_by_tv: dict[float, pd.Series] = {}
        for tv in TARGET_VOLS:
            sleeve = compute_sleeve_returns(
                mtum, vlue,
                vol_lookback=VOL_LOOKBACK, target_vol=tv, leg_cap=LEG_CAP,
                short_borrow_rate=SHORT_BORROW_RATE, trans_cost_bps=TRANS_COST_BPS,
            )
            sleeves_by_tv[tv] = sleeve
            cl_sleeve = cross_lib_check_sleeve(mtum, vlue, tv)
            all_results["crosslib_sleeve"][ds_name].append(cl_sleeve)

        s_default = sleeves_by_tv[TARGET_VOLS[0]]
        common = r_064.index.union(s_default.index)
        print(
            f"\n=== {ds_name} ===\n"
            f"  iter 064 stream: [{r_064.index[0].date()} → {r_064.index[-1].date()}] ({len(r_064)} bars)\n"
            f"  MTUM/VLUE sleeve start: [{s_default.index[0].date()} → {s_default.index[-1].date()}] ({len(s_default)} bars)\n"
            f"  union join: [{common[0].date()} → {common[-1].date()}] ({len(common)} bars)\n"
            f"  benchmark {ds['bench_ticker']:>4}: Sharpe={bench['sharpe']:.4f} "
            f"CAGR={bench['cagr']:.2%} MDD={bench['mdd']:.2%}"
        )
        # Print sleeve standalone metrics for each target_vol (key diagnostic)
        for tv in TARGET_VOLS:
            s = sleeves_by_tv[tv]
            s_post = s[s != 0.0]  # skip warmup zeros to gauge "live" Sharpe
            if len(s_post) > 30:
                eq_s = (1.0 + s).cumprod()
                print(
                    f"  sleeve tv={tv:.2f}: "
                    f"Sharpe={float(_sharpe(s)):+.3f} "
                    f"CAGR={float(_cagr(eq_s)):+.2%} "
                    f"MDD={float(_max_drawdown(eq_s)):.2%} "
                    f"realized_vol={s.std()*np.sqrt(252):.3f}"
                )

        # Save subcomponent streams (one set per dataset, default tv=0.10)
        all_results["subcomponent_returns"][ds_name] = {
            "r_064": {
                "index": [str(t.date()) for t in r_064.index],
                "net_returns": [round(float(x), 10) for x in r_064.tolist()],
            },
            "r_sleeve_tv010": {
                "index": [str(t.date()) for t in sleeves_by_tv[0.10].index],
                "net_returns": [round(float(x), 10) for x in sleeves_by_tv[0.10].tolist()],
            },
        }

        # For the cross-lib check, align each cfg's series to a common index.
        # We use the union of iter 064 + sleeve for each cfg's check.
        for cfg in CONFIGS:
            m, combined = run_single_cfg(r_064, sleeves_by_tv, bench_series, cfg)
            all_results["runs"][ds_name][cfg["cfg_id"]] = m
            all_results["returns_series"][ds_name][cfg["cfg_id"]] = {
                "index": [str(t.date()) for t in combined.index],
                "net_returns": [round(float(x), 10) for x in combined.tolist()],
            }
            r_sleeve = sleeves_by_tv[cfg["target_vol"]]
            cl = cross_lib_check_for_cfg(r_064, r_sleeve, cfg)
            all_results["crosslib"][ds_name][cfg["cfg_id"]] = cl
            edge_frozen = m["sharpe"] - {
                "educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955,
            }[ds_name]
            print(
                f"  {cfg['cfg_id']:42s} S={m['sharpe']:+.4f} "
                f"(Δ frozen={edge_frozen:+.4f}) CAGR={m['cagr']:+.2%} "
                f"MDD={m['mdd']:.2%} corr(064,sleeve)={m['corr_064_sleeve']:+.3f} "
                f"corr(sleeve,bench)={m['corr_sleeve_bench']:+.3f} "
                f"sleeve_S={m['r_sleeve_sharpe']:+.3f} "
                f"Mres={m['markowitz_residual_sharpe']:+.5f} "
                f"G7 Δpp={cl['abs_diff_pp']:.6f}"
            )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(
        json.dumps(all_results, indent=2, default=str), encoding="utf-8",
    )
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
