"""Iter 067 — Run σ⁻² variance-target overlay (cap=1.0) on iter 064 saved stream.

Single pre-committed cfg `iter064_vt_cap10_lookback21_target_full`.
cumulative_n_trials advance: 4336 → 4337 (+1).

Loads the iter 064 saved combined return stream (the current TOP-K #1
strategy: 0.9 × iter_046 + 0.1 × QQQ_200d_trend, score 90 STRONG) and
applies the Moreira-Muir variance-target overlay with σ_target equal to
the dataset's full-window annualised σ of r_064 and cap=1.0 (no leverage).

Citations
---------
* Moreira & Muir (2017), JoF 72(4) — σ⁻² scaling primitive.
* `[volatility_trading, p.218]` — Sinclair, σ⁻² sizing.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* `[advances_fin_ml, p.162-164]` — strict shift(1) on σ̂.
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

from variance_target_overlay import apply_variance_target_overlay  # noqa: E402
from numpy_reference_iter067 import apply_variance_target_overlay_np  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

ITER_064_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "064-2026-04-25-1315-iter058-qqq-trend-substitution"
ITER_064_RESULTS = ITER_064_DIR / "results.json"
TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"

CFG: dict = {
    "cfg_id": "iter064_vt_cap10_lookback21_target_full",
    "lookback": 21,
    "cap": 1.0,
    "cost_bps": 5.0,
    "rf": 0.0,  # iter 064 stream is already net of rf treatment
    "rebalance": "daily; sigma_target = full-window σ_064 per dataset",
    "primary_citation": (
        "Moreira-Muir 2017 + [volatility_trading, p.218] + "
        "[advances_fin_ml, p.162-164]"
    ),
    "iter064_cfg_id": "iter046_plus_qqq_trend_w010_lookback200",
}

DATASETS: dict[str, dict] = {
    "educational": {
        "bench_ticker": "SPY",
        "iter064_first": "2006-01-04",
        "iter064_last":  "2026-04-15",
        "frozen_sharpe_bench": 0.68,
        "frozen_cagr_bench": 0.1147,
        "frozen_mdd_bench": 0.5514,
    },
    "spy_real": {
        "bench_ticker": "SPY",
        "iter064_first": "2009-06-26",
        "iter064_last":  "2026-04-15",
        "frozen_sharpe_bench": 0.90,
        "frozen_cagr_bench": 0.1497,
        "frozen_mdd_bench": 0.3370,
    },
    "ndx_real": {
        "bench_ticker": "QQQ",
        "iter064_first": "2010-02-16",
        "iter064_last":  "2026-04-15",
        "frozen_sharpe_bench": 0.955,
        "frozen_cagr_bench": 0.1918,
        "frozen_mdd_bench": 0.3512,
    },
}


def load_iter064_stream(ds_name: str) -> pd.Series:
    """Load iter 064's saved combined return stream for a dataset."""
    if not ITER_064_RESULTS.exists():
        raise FileNotFoundError(f"iter 064 results.json missing: {ITER_064_RESULTS}")
    with ITER_064_RESULTS.open() as f:
        results = json.load(f)
    cfg_id = CFG["iter064_cfg_id"]
    series = results["returns_series"][ds_name][cfg_id]
    idx = pd.to_datetime(series["index"])
    vals = np.array(series["net_returns"], dtype=float)
    return pd.Series(vals, index=idx, name="r_064")


def load_bench_returns(symbol: str, start: str, end: str) -> pd.Series:
    df = pd.read_parquet(TIINGO_DIR / f"{symbol}.parquet")
    m = (df.index >= start) & (df.index <= end)
    p = df.loc[m, "adj_close"].astype(float)
    return p.pct_change().dropna()


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


def run_single_cfg(r_064: pd.Series) -> tuple[dict, pd.Series, pd.Series]:
    """Apply variance-target overlay; return metrics dict + (combined, scale)."""
    sigma_target = float(r_064.std(ddof=0)) * float(np.sqrt(252.0))

    combined, scale = apply_variance_target_overlay(
        r_064,
        sigma_target=sigma_target,
        lookback=CFG["lookback"],
        cap=CFG["cap"],
        cost_bps=CFG["cost_bps"],
    )
    eq_curve = (1.0 + combined).cumprod()

    aligned_064 = r_064.loc[combined.index]
    eq_064 = (1.0 + aligned_064).cumprod()

    corr_overlay_064 = float(combined.corr(aligned_064))
    rolling21_min = float(combined.rolling(21).sum().min())

    delta_scale_inner = scale.diff().abs().fillna(0.0)
    n_flips = int((delta_scale_inner > 1e-9).sum())
    pct_capped = float((np.abs(scale - CFG["cap"]) < 1e-9).mean())

    m = {
        "cfg_id": CFG["cfg_id"],
        "sigma_target_used": sigma_target,
        "lookback": CFG["lookback"],
        "cap": CFG["cap"],
        "cost_bps": CFG["cost_bps"],
        "bars": int(len(combined)),
        "sharpe": float(_sharpe(combined)),
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "r_064_sharpe": float(_sharpe(aligned_064)),
        "r_064_cagr": float(_cagr(eq_064)),
        "r_064_mdd": float(_max_drawdown(eq_064)),
        "scale_mean": float(scale.mean()),
        "scale_min": float(scale.min()),
        "scale_max": float(scale.max()),
        "scale_median": float(scale.median()),
        "scale_q05": float(scale.quantile(0.05)),
        "scale_q95": float(scale.quantile(0.95)),
        "pct_at_cap": pct_capped,
        "n_meaningful_flips": n_flips,
        "corr_overlay_064": corr_overlay_064,
        "rolling21_worst": rolling21_min,
        "total_turnover": float(scale.iloc[0] + scale.diff().abs().sum()),
    }
    return m, combined, scale


def cross_lib_check(r_064: pd.Series) -> dict:
    """G7 parity: pandas vs numpy reference, ΔCAGR ≤ 3 pp."""
    sigma_target = float(r_064.std(ddof=0)) * float(np.sqrt(252.0))

    pd_out, _ = apply_variance_target_overlay(
        r_064,
        sigma_target=sigma_target,
        lookback=CFG["lookback"],
        cap=CFG["cap"],
        cost_bps=CFG["cost_bps"],
    )
    np_out, _ = apply_variance_target_overlay_np(
        r_064.values,
        sigma_target=sigma_target,
        lookback=CFG["lookback"],
        cap=CFG["cap"],
        cost_bps=CFG["cost_bps"],
    )
    n = min(len(pd_out), len(np_out))
    pd_arr = pd_out.values[-n:]
    np_arr = np_out[-n:]

    eq_pd = np.cumprod(1.0 + pd_arr)
    eq_np = np.cumprod(1.0 + np_arr)
    cagr_pd = float(eq_pd[-1]) ** (252.0 / n) - 1.0
    cagr_np = float(eq_np[-1]) ** (252.0 / n) - 1.0
    return {
        "cagr_pandas": cagr_pd,
        "cagr_numpy": cagr_np,
        "abs_diff_pp": abs(cagr_pd - cagr_np) * 100.0,
        "max_abs_return_diff": float(np.max(np.abs(pd_arr - np_arr))),
        "n_bars_compared": n,
    }


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": [CFG],
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "subcomponent_returns": {},
        "crosslib": {},
        "pre_committed": True,
        "iter_label": "067-2026-04-25-1436-iter064-vol-target-cap10",
    }

    for ds_name, ds in DATASETS.items():
        r_064 = load_iter064_stream(ds_name)
        # Bench from Tiingo for transparency (matches iter 064's frozen bench).
        bench_returns = load_bench_returns(
            ds["bench_ticker"],
            str(r_064.index[0].date()),
            str(r_064.index[-1].date()),
        )
        all_results["benchmarks"][ds_name] = benchmark_metrics(bench_returns)

        print(f"\n=== {ds_name} ===")
        print(
            f"r_064 stream {r_064.index[0].date()} → {r_064.index[-1].date()} "
            f"({len(r_064)} bars)"
        )

        m, combined, scale = run_single_cfg(r_064)
        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in combined.index],
                "net_returns": [round(float(x), 10) for x in combined.tolist()],
            }
        }
        all_results["subcomponent_returns"][ds_name] = {
            "r_064": {
                "index": [str(t.date()) for t in r_064.index],
                "net_returns": [round(float(x), 10) for x in r_064.tolist()],
            },
            "scale": {
                "index": [str(t.date()) for t in scale.index],
                "values": [round(float(x), 10) for x in scale.tolist()],
            },
        }
        edge_frozen = m["sharpe"] - ds["frozen_sharpe_bench"]
        edge_064 = m["sharpe"] - m["r_064_sharpe"]
        print(
            f"  sigma_target = σ_064 = {m['sigma_target_used']:.4f} "
            f"({m['sigma_target_used']*100:.2f}% ann)"
        )
        print(
            f"  scale: mean={m['scale_mean']:.4f} min={m['scale_min']:.4f} "
            f"max={m['scale_max']:.4f} q05={m['scale_q05']:.4f} "
            f"q95={m['scale_q95']:.4f} pct_at_cap={m['pct_at_cap']:.2%}"
        )
        print(
            f"  iter 067: Sharpe={m['sharpe']:+.4f} (Δ frozen={edge_frozen:+.4f}, "
            f"Δ064={edge_064:+.4f}) CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"corr(067,064)={m['corr_overlay_064']:+.4f}"
        )
        print(
            f"  iter 064 in-window: Sharpe={m['r_064_sharpe']:+.4f} "
            f"CAGR={m['r_064_cagr']:+.2%} MDD={m['r_064_mdd']:.2%}"
        )

        cl = cross_lib_check(r_064)
        all_results["crosslib"][ds_name] = cl
        print(
            f"    G7 cross-lib: CAGR pd={cl['cagr_pandas']:+.4%} "
            f"np={cl['cagr_numpy']:+.4%} Δ={cl['abs_diff_pp']:.6f} pp "
            f"(n_compared={cl['n_bars_compared']})"
        )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(
        json.dumps(all_results, indent=2, default=str), encoding="utf-8",
    )
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
