"""Iter 074 — Run iter 016 + iter 064 saved-stream ensemble on 3 datasets × 7 cfgs.

Loads the iter 016 saved combined stream and the iter 064 saved combined
stream from each iter's `results.json`, then forms 7 weighted blends over
``w_016 ∈ {0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80}`` (with
``w_064 = 1 - w_016``).

cumulative_n_trials advance: 4360 → 4381 (+21 = 7 cfgs × 3 datasets,
matching iter 073's per-dataset trial counting).

Citations
---------
* Markowitz (1952), JoF 7(1) — closed-form convex combination Sharpe.
* `[risk_parity, ch.5]` — iter 016 base preserved verbatim via saved stream.
* Faber (2007) SSRN 962461 — iter 064 base (QQQ-200d trend filter).
* `[volatility_trading, p.218]` — iter 064 → iter 046 → iter 039 VRP leg.
* Whaley (2009), JPM 35(3), DOI 10.3905/JPM.2009.35.3.098 — VIX gate.
* Moreira-Muir (2017), JoF 72(4), DOI 10.1111/jofi.12513 — vol-mgmt rule.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
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

from iter074_ensemble import (  # noqa: E402
    ITER_016_CFG_ID,
    ITER_064_CFG_ID,
    combine_iter016_iter064,
    load_iter016_stream,
    load_iter064_stream,
)
from numpy_reference_iter074 import combine_iter016_iter064_np  # noqa: E402

from market_lab.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"

# Pre-committed weight grid: 7 cfgs over w_016 ∈ {0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80}
WEIGHT_GRID = [0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80]


def cfg_id_for_weight(w_016: float) -> str:
    return f"iter074_ensemble_w016_{int(round(w_016 * 100)):03d}"


CONFIGS: list[dict] = [
    {
        "cfg_id": cfg_id_for_weight(w),
        "w_016": float(w),
        "w_064": float(round(1.0 - w, 6)),
        "leg_a_iter": "016",
        "leg_a_cfg_id": ITER_016_CFG_ID,
        "leg_b_iter": "064",
        "leg_b_cfg_id": ITER_064_CFG_ID,
        "primary_citation": (
            "Markowitz (1952) JoF 7(1) + [risk_parity, ch.5] (iter 016 leg) + "
            "Faber (2007) SSRN 962461 + [volatility_trading, p.218] "
            "(iter 064 leg via iter 046)"
        ),
    }
    for w in WEIGHT_GRID
]

DATASETS: dict[str, dict] = {
    "educational": {
        "bench_ticker": "SPY",
        "start": "2006-01-03",
        "end": "2026-04-15",
        "role": "20y combined; iter 016 + iter 064 inner-join",
    },
    "spy_real": {
        "bench_ticker": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "17y post-GFC combined",
    },
    "ndx_real": {
        "bench_ticker": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "16y; bench QQQ",
    },
}


def load_prices(symbol: str, start: str, end: str) -> pd.Series:
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
    r_a: pd.Series,
    r_b: pd.Series,
    *,
    w_a: float,
    w_b: float,
    observed_sharpe: float,
) -> tuple[float, dict]:
    """Closed-form Sharpe of convex combo, residual vs observed."""
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
    r_016: pd.Series,
    r_064: pd.Series,
    cfg: dict,
) -> tuple[dict, pd.Series]:
    combined = combine_iter016_iter064(
        r_016, r_064, w_016=cfg["w_016"], w_064=cfg["w_064"],
    )
    eq_curve = (1.0 + combined).cumprod()

    common = combined.index
    r_016_aligned = r_016.loc[common]
    r_064_aligned = r_064.loc[common]

    corr_legs = float(r_016_aligned.corr(r_064_aligned))
    corr_combined_064 = float(combined.corr(r_064_aligned))
    corr_combined_016 = float(combined.corr(r_016_aligned))

    obs_sharpe = float(_sharpe(combined))
    residual, mw_detail = markowitz_residual(
        r_016_aligned, r_064_aligned,
        w_a=cfg["w_016"], w_b=cfg["w_064"],
        observed_sharpe=obs_sharpe,
    )

    m = {
        "cfg_id": cfg["cfg_id"],
        "w_016": cfg["w_016"],
        "w_064": cfg["w_064"],
        "bars": int(len(combined)),
        "sharpe": obs_sharpe,
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "corr_016_064": corr_legs,
        "corr_combined_016": corr_combined_016,
        "corr_combined_064": corr_combined_064,
        "r_016_sharpe": float(_sharpe(r_016_aligned)),
        "r_016_cagr": float(_cagr((1.0 + r_016_aligned).cumprod())),
        "r_016_mdd": float(_max_drawdown((1.0 + r_016_aligned).cumprod())),
        "r_064_sharpe": float(_sharpe(r_064_aligned)),
        "r_064_cagr": float(_cagr((1.0 + r_064_aligned).cumprod())),
        "r_064_mdd": float(_max_drawdown((1.0 + r_064_aligned).cumprod())),
        "markowitz_residual_sharpe": residual,
        "markowitz_detail": mw_detail,
    }
    return m, combined


def cross_lib_check_for_cfg(
    r_016_aligned: pd.Series,
    r_064_aligned: pd.Series,
    cfg: dict,
) -> dict:
    """G7 parity: pandas blend vs pure-numpy reference, CAGR Δ ≤ 3 pp."""
    pd_out = combine_iter016_iter064(
        r_016_aligned, r_064_aligned,
        w_016=cfg["w_016"], w_064=cfg["w_064"],
    )
    np_out = combine_iter016_iter064_np(
        r_016_aligned.values, r_064_aligned.values,
        w_016=cfg["w_016"], w_064=cfg["w_064"],
    )
    eq_pd = np.cumprod(1.0 + pd_out.values)
    eq_np = np.cumprod(1.0 + np_out)
    n = len(pd_out)
    cagr_pd = float(eq_pd[-1]) ** (252.0 / n) - 1.0
    cagr_np_val = float(eq_np[-1]) ** (252.0 / n) - 1.0
    return {
        "cagr_pandas": cagr_pd,
        "cagr_numpy": cagr_np_val,
        "abs_diff_pp": abs(cagr_pd - cagr_np_val) * 100.0,
        "max_abs_return_diff": float(np.max(np.abs(pd_out.values - np_out))),
        "n_bars_compared": n,
    }


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": CONFIGS,
        "benchmarks": {},
        "runs": {ds: {} for ds in DATASETS},
        "returns_series": {ds: {} for ds in DATASETS},
        "subcomponent_returns": {},
        "crosslib": {ds: {} for ds in DATASETS},
        "pre_committed": True,
        "iter_label": "074-2026-04-25-1724-iter016-iter064-ensemble",
    }

    for ds_name, ds in DATASETS.items():
        r_016 = load_iter016_stream(ds_name)
        r_064 = load_iter064_stream(ds_name)

        bench_p = load_prices(ds["bench_ticker"], ds["start"], ds["end"])
        bench_series = bench_p.pct_change().dropna()
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        common = r_016.index.intersection(r_064.index)
        print(
            f"\n=== {ds_name} ===\n"
            f"  iter 016 stream: [{r_016.index[0].date()} → {r_016.index[-1].date()}] ({len(r_016)} bars)\n"
            f"  iter 064 stream: [{r_064.index[0].date()} → {r_064.index[-1].date()}] ({len(r_064)} bars)\n"
            f"  inner-join:     [{common[0].date()} → {common[-1].date()}] ({len(common)} bars)\n"
            f"  benchmark {ds['bench_ticker']:>4}: Sharpe={bench['sharpe']:.4f} "
            f"CAGR={bench['cagr']:.2%} MDD={bench['mdd']:.2%}"
        )

        # Save subcomponent streams (single set per dataset)
        all_results["subcomponent_returns"][ds_name] = {
            "r_016": {
                "index": [str(t.date()) for t in r_016.loc[common].index],
                "net_returns": [round(float(x), 10) for x in r_016.loc[common].tolist()],
            },
            "r_064": {
                "index": [str(t.date()) for t in r_064.loc[common].index],
                "net_returns": [round(float(x), 10) for x in r_064.loc[common].tolist()],
            },
        }

        # Reuse aligned series for crosslib check (same per cfg, just diff weights)
        r_016_aligned = r_016.loc[common]
        r_064_aligned = r_064.loc[common]

        for cfg in CONFIGS:
            m, combined = run_single_cfg(r_016, r_064, cfg)
            all_results["runs"][ds_name][cfg["cfg_id"]] = m
            all_results["returns_series"][ds_name][cfg["cfg_id"]] = {
                "index": [str(t.date()) for t in combined.index],
                "net_returns": [round(float(x), 10) for x in combined.tolist()],
            }
            cl = cross_lib_check_for_cfg(r_016_aligned, r_064_aligned, cfg)
            all_results["crosslib"][ds_name][cfg["cfg_id"]] = cl

            edge_frozen = m["sharpe"] - {
                "educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955,
            }[ds_name]
            print(
                f"  {cfg['cfg_id']:32s} S={m['sharpe']:+.4f} "
                f"(Δ frozen={edge_frozen:+.4f}) CAGR={m['cagr']:+.2%} "
                f"MDD={m['mdd']:.2%} corr(016,064)={m['corr_016_064']:+.3f} "
                f"Markowitz res={m['markowitz_residual_sharpe']:+.5f} "
                f"G7 Δpp={cl['abs_diff_pp']:.6f}"
            )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(
        json.dumps(all_results, indent=2, default=str), encoding="utf-8",
    )
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
