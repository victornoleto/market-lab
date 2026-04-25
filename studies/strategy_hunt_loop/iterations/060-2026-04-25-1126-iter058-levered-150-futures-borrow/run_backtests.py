"""Iter 060 — Run 1.5× levered iter 058 saved stream at 2.5% futures borrow.

Single pre-committed cfg ``iter058_levered_150_borrow_250bps``. No grid,
no sweep. cumulative_n_trials advance: 4329 → 4330 (+1).

Borrow rate 2.5% = T-bill 2.0% + 0.5% Treasury futures roll cost
(NTSX-style mechanism per Hsiao-Williams 2017). Pre-committed; not
optimized.

Citations
---------
* `[leverage_for_the_long_run, ch.5]` — Hsiao-Williams 2017 NTSX
  architecture (futures-implied financing).
* `[risk_parity, ch.5]` — iter 058 base preserved verbatim.
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
* Frazzini-Pedersen (2014) — borrow frictions on levered low-vol.
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

from levered_iter058 import apply_leverage_pd  # noqa: E402
from numpy_reference_iter060 import compute_levered_returns_np  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
ITER_058_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "058-2026-04-25-1044-hyg-credit-carry-3rd-stream"
ITER_058_RESULTS = ITER_058_DIR / "results.json"

CFG: dict = {
    "cfg_id": "iter058_levered_150_borrow_250bps",
    "lev": 1.5,
    "borrow_rate_annual": 0.025,
    "rf": 0.02,
    "iter058_cfg_id": "iter046_plus_hyg_tsm_w010_lookback90",
    "rebalance": "daily; 1.5× notional on iter 058 combined stream, financed at 2.5% futures-implied",
    "funding_cost_modeled": True,
    "borrow_rate_source": (
        "NTSX-style Treasury-futures roll cost (T-bill 2.0% + 0.5% roll); "
        "Hsiao-Williams 2017 [leverage_for_the_long_run, ch.5]"
    ),
    "primary_citation": (
        "[leverage_for_the_long_run, ch.5] + [risk_parity, ch.5] + "
        "[advances_fin_ml, p.31-34]"
    ),
}

DATASETS: dict[str, dict] = {
    "educational": {
        "bench_ticker": "SPY",
        "start": "2006-01-03",
        "end": "2026-04-15",
        "role": "20y combined; HYG limits effective start to ~2007-04",
    },
    "spy_real": {
        "bench_ticker": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "17y post-GFC; primary frozen-bench window",
    },
    "ndx_real": {
        "bench_ticker": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "16y; bench QQQ; tightest CAGR floor 15.35%",
    },
}


def load_prices(symbol: str, start: str, end: str) -> pd.Series:
    df = pd.read_parquet(TIINGO_DIR / f"{symbol}.parquet")
    m = (df.index >= start) & (df.index <= end)
    return df.loc[m, "adj_close"].astype(float)


def load_iter058_returns(ds_name: str) -> pd.Series:
    if not ITER_058_RESULTS.exists():
        raise FileNotFoundError(
            f"iter 058 results.json not found at {ITER_058_RESULTS}"
        )
    with ITER_058_RESULTS.open() as f:
        results = json.load(f)
    cfg_id = CFG["iter058_cfg_id"]
    series = results["returns_series"][ds_name][cfg_id]
    idx = pd.to_datetime(series["index"])
    vals = np.array(series["net_returns"], dtype=float)
    return pd.Series(vals, index=idx, name="r_058")


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


def run_single_cfg(r_058: pd.Series) -> tuple[dict, pd.Series]:
    """Apply leverage transform to iter 058 saved stream."""
    levered = apply_leverage_pd(
        r_058, lev=CFG["lev"], borrow_rate_annual=CFG["borrow_rate_annual"],
    )
    eq_curve = (1.0 + levered).cumprod()

    sigma_unlev = float(r_058.std(ddof=0)) * np.sqrt(252.0)
    sharpe_unlev = float(_sharpe(r_058))
    cagr_unlev = float(_cagr((1.0 + r_058).cumprod()))
    mdd_unlev = float(_max_drawdown((1.0 + r_058).cumprod()))

    rolling21_min = float(levered.rolling(21).sum().min())

    # Predicted Sharpe drag (daily-form formula).
    daily_borrow = (1.0 + CFG["borrow_rate_annual"]) ** (1.0 / 252.0) - 1.0
    rf_daily = CFG["rf"] / 252.0
    sigma_daily = sigma_unlev / np.sqrt(252.0)
    sharpe_drag_pred = (
        np.sqrt(252.0) * (CFG["lev"] - 1.0) * (daily_borrow - rf_daily)
        / (CFG["lev"] * sigma_daily)
    )

    m = {
        "cfg_id": CFG["cfg_id"],
        "lev": CFG["lev"],
        "borrow_rate_annual": CFG["borrow_rate_annual"],
        "rf": CFG["rf"],
        "bars": int(len(levered)),
        "sharpe": float(_sharpe(levered)),
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "rolling21_worst": rolling21_min,
        "r_058_sharpe": sharpe_unlev,
        "r_058_cagr": cagr_unlev,
        "r_058_mdd": mdd_unlev,
        "r_058_sigma_annual": sigma_unlev,
        "sharpe_drag_predicted": float(sharpe_drag_pred),
        "sharpe_drag_observed": float(sharpe_unlev - _sharpe(levered)),
        "daily_borrow": float(daily_borrow),
    }
    return m, levered


def cross_lib_check(r_058: pd.Series) -> dict:
    """G7 parity: pandas leverage transform vs pure-numpy reference.

    Both wrap ``apply_leverage_*`` so parity is exact by construction.
    """
    pd_out = apply_leverage_pd(
        r_058, lev=CFG["lev"], borrow_rate_annual=CFG["borrow_rate_annual"],
    )
    np_out = compute_levered_returns_np(
        r_058.values, lev=CFG["lev"],
        borrow_rate_annual=CFG["borrow_rate_annual"],
    )
    n = min(len(pd_out), len(np_out))
    pd_arr = pd_out.values[-n:]
    np_arr = np_out[-n:]
    eq_pd = np.cumprod(1.0 + pd_arr)
    eq_np = np.cumprod(1.0 + np_arr)
    cagr_pd = float(eq_pd[-1]) ** (252.0 / n) - 1.0
    cagr_np_val = float(eq_np[-1]) ** (252.0 / n) - 1.0
    return {
        "cagr_pandas": cagr_pd,
        "cagr_numpy": cagr_np_val,
        "abs_diff_pp": abs(cagr_pd - cagr_np_val) * 100.0,
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
        "iter_label": "060-2026-04-25-1126-iter058-levered-150-futures-borrow",
    }

    for ds_name, ds in DATASETS.items():
        r_058 = load_iter058_returns(ds_name)

        bench_p = load_prices(ds["bench_ticker"], ds["start"], ds["end"])
        bench_series = bench_p.pct_change().dropna()
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        print(
            f"[{ds_name}] iter058 stream {r_058.index[0].date()} → "
            f"{r_058.index[-1].date()} ({len(r_058)} bars), "
            f"bench={ds['bench_ticker']} "
            f"Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%}"
        )

        print(f"\n=== {ds_name} — cfg {CFG['cfg_id']} ===")
        m, levered = run_single_cfg(r_058)
        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in levered.index],
                "net_returns": [round(float(x), 10) for x in levered.tolist()],
            }
        }
        all_results["subcomponent_returns"][ds_name] = {
            "r_058": {
                "index": [str(t.date()) for t in r_058.index],
                "net_returns": [round(float(x), 10) for x in r_058.tolist()],
            }
        }
        edge_frozen = m["sharpe"] - {
            "educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955,
        }[ds_name]
        print(
            f"  levered Sharpe={m['sharpe']:+.4f} (Δ frozen={edge_frozen:+.4f}, "
            f"Δ058={m['sharpe'] - m['r_058_sharpe']:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%}"
        )
        print(
            f"  r_058 Sharpe={m['r_058_sharpe']:+.4f} CAGR={m['r_058_cagr']:+.2%} "
            f"MDD={m['r_058_mdd']:.2%} σ_annual={m['r_058_sigma_annual']:.4f}"
        )
        print(
            f"  Sharpe drag: predicted={m['sharpe_drag_predicted']:+.4f} "
            f"observed={m['sharpe_drag_observed']:+.4f}"
        )

        cl = cross_lib_check(r_058)
        all_results["crosslib"][ds_name] = cl
        print(
            f"    G7 cross-lib (lev transform): CAGR pd={cl['cagr_pandas']:+.4%} "
            f"np={cl['cagr_numpy']:+.4%} Δ={cl['abs_diff_pp']:.4f} pp "
            f"(n_compared={cl['n_bars_compared']})"
        )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(
        json.dumps(all_results, indent=2, default=str), encoding="utf-8",
    )
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
