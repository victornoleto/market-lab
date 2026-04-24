"""Iter 024 — Bond-curve carry duration timing backtests on 3 datasets.

**Pre-committed cfg** ``bcdt_w90_60_t10y3m_sma21_ramp100bps_v1`` —
see hypothesis.md. NO grid, NO sweep, NO post-hoc selection. Single
config across 3 datasets.

Cumulative n_trials advance: 4276 → 4277 (+1 cfg).
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
from bond_carry_duration_timing import apply_bond_carry_duration_timing  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
MACRO_PATH = ROOT / "data" / "external" / "macro" / "t10y3m_daily.parquet"

# ---------------------------------------------------------------------------
# Pre-committed single config
# ---------------------------------------------------------------------------

CFG: dict = {
    "cfg_id": "bcdt_w90_60_t10y3m_sma21_ramp100bps_v1",
    "eq_w": 0.9,                         # NTSX prospectus equity leg
    "bd_w": 0.6,                         # NTSX prospectus bond leg
    "smoothing_days": 21,                # 21-day SMA (monthly emulation)
    "lag_bars": 1,                       # no look-ahead
    "ramp_max_bps": 100.0,               # 0bps→0%, 100bps→100% TLT
    "rebalance_bars": 21,                # monthly rebalance
    "carry_signal": "T10Y3M",            # FRED 10Y minus 3M
}
COST_BPS_PER_LEG = 0.0002  # 2 bps per unit ∆position (matches iter 023 cost model)

# ---------------------------------------------------------------------------
# Datasets — SHV-inception aligned (2007-01-11)
# ---------------------------------------------------------------------------

DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "bond_long_symbol": "TLT",
        "bond_short_symbol": "SHV",
        "start": "2007-01-11",
        "end": "2026-04-15",
        "role": "SPY+TLT+SHV ~19y (SHV-inception-aligned)",
    },
    "spy_real": {
        "equity_symbol": "SPY",
        "bond_long_symbol": "TLT",
        "bond_short_symbol": "SHV",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "SPY+TLT+SHV 17y post-GFC",
    },
    "ndx_real": {
        "equity_symbol": "QQQ",
        "bond_long_symbol": "TLT",
        "bond_short_symbol": "SHV",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "QQQ+TLT+SHV 16y tech-heavy",
    },
}


def load_streams(ds: dict) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    df_eq = pd.read_parquet(TIINGO_DIR / f"{ds['equity_symbol']}.parquet")
    df_tlt = pd.read_parquet(TIINGO_DIR / f"{ds['bond_long_symbol']}.parquet")
    df_shv = pd.read_parquet(TIINGO_DIR / f"{ds['bond_short_symbol']}.parquet")
    df_sig = pd.read_parquet(MACRO_PATH)

    start = pd.Timestamp(ds["start"])
    end = pd.Timestamp(ds["end"])

    def _slice(df, col):
        m = (df.index >= start) & (df.index <= end)
        return df.loc[m, col]

    p_eq = _slice(df_eq, "adj_close")
    p_tlt = _slice(df_tlt, "adj_close")
    p_shv = _slice(df_shv, "adj_close")
    sig = _slice(df_sig, "term_spread")

    # Inner-join on dates, then compute returns.
    prices = pd.concat(
        {"eq": p_eq, "tlt": p_tlt, "shv": p_shv, "sig": sig},
        axis=1, join="inner",
    ).dropna()

    r_eq = prices["eq"].pct_change()
    r_tlt = prices["tlt"].pct_change()
    r_shv = prices["shv"].pct_change()
    sig_aligned = prices["sig"].copy()
    # Drop the first NaN row (pct_change).
    valid = r_eq.notna() & r_tlt.notna() & r_shv.notna()
    return (
        r_eq.loc[valid],
        r_tlt.loc[valid],
        r_shv.loc[valid],
        sig_aligned.loc[valid],
    )


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


def run_single_cfg(
    r_eq: pd.Series, r_tlt: pd.Series, r_shv: pd.Series, sig: pd.Series,
) -> tuple[dict, pd.Series, pd.DataFrame, pd.Series]:
    net, positions, scale, alloc_tlt = apply_bond_carry_duration_timing(
        r_eq, r_tlt, r_shv, sig,
        eq_w=CFG["eq_w"], bd_w=CFG["bd_w"],
        smoothing_days=CFG["smoothing_days"], lag_bars=CFG["lag_bars"],
        ramp_max_bps=CFG["ramp_max_bps"], rebalance_bars=CFG["rebalance_bars"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    eq = (1.0 + net).cumprod()
    summary = {
        "cfg_id": CFG["cfg_id"],
        **{k: v for k, v in CFG.items() if k != "cfg_id"},
        "sharpe": float(_sharpe(net)),
        "cagr": float(_cagr(eq)),
        "mdd": float(_max_drawdown(eq)),
        "n_bars": int(len(net)),
        "first_date": str(net.index[0].date()),
        "last_date": str(net.index[-1].date()),
        "alloc_tlt_mean": float(alloc_tlt.mean()),
        "alloc_tlt_std": float(alloc_tlt.std(ddof=0)),
        "alloc_shv_frac_bars": float((alloc_tlt < 0.5).mean()),
        "turnover_per_year_bond_legs": float(
            (positions["TLT"].diff().abs().sum() +
             positions["SHV"].diff().abs().sum()) /
            (len(net) / 252.0)
        ),
    }
    return summary, net, positions, alloc_tlt


def main() -> None:
    print("Iter 024 — Bond-Carry Duration Timing single-cfg run")
    print(f"cfg = {CFG['cfg_id']}")
    print(f"cost = {COST_BPS_PER_LEG * 1e4:.0f} bps/leg/Δpos")
    print()

    runs: dict[str, dict[str, dict]] = {}
    benchmarks: dict[str, dict] = {}
    returns_series: dict[str, dict[str, dict]] = {}
    leg_corrs: dict[str, dict] = {}

    for ds_name, ds in DATASETS.items():
        print(f"=== {ds_name} ({ds['role']}) ===")
        r_eq, r_tlt, r_shv, sig = load_streams(ds)
        print(f"  loaded {len(r_eq)} bars: {r_eq.index[0].date()} → {r_eq.index[-1].date()}")
        print(f"  T10Y3M range: [{sig.min():.3f}, {sig.max():.3f}] %")

        summary, net, positions, alloc = run_single_cfg(r_eq, r_tlt, r_shv, sig)
        bench = benchmark_metrics(r_eq.loc[net.index])

        runs[ds_name] = {summary["cfg_id"]: summary}
        benchmarks[ds_name] = bench
        returns_series[ds_name] = {
            summary["cfg_id"]: {
                "index": [d.isoformat() for d in net.index],
                "net_returns": net.tolist(),
                "alloc_tlt": alloc.tolist(),
            }
        }
        leg_corrs[ds_name] = {
            "eq_tlt": float(r_eq.loc[net.index].corr(r_tlt.loc[net.index])),
            "eq_shv": float(r_eq.loc[net.index].corr(r_shv.loc[net.index])),
            "tlt_shv": float(r_tlt.loc[net.index].corr(r_shv.loc[net.index])),
        }

        print(f"  Sharpe={summary['sharpe']:.4f}  CAGR={summary['cagr']*100:.2f}%  MDD={summary['mdd']*100:.2f}%")
        print(f"  vs bench:  Sharpe={bench['sharpe']:.4f}  CAGR={bench['cagr']*100:.2f}%  MDD={bench['mdd']*100:.2f}%")
        print(f"  alloc_TLT mean={summary['alloc_tlt_mean']:.3f}, SHV-mode-bars={summary['alloc_shv_frac_bars']*100:.1f}%")
        print(f"  bond-leg turnover = {summary['turnover_per_year_bond_legs']:.2f} / yr (Kill #D check)")
        print()

    out = {
        "iteration": "024-2026-04-24-2033-bond-carry-duration-timing",
        "cumulative_n_trials_post": 4276 + 1,
        "cost_bps_per_leg": COST_BPS_PER_LEG,
        "configs": [CFG],
        "datasets": {k: {kk: vv for kk, vv in v.items() if kk != "data"}
                     for k, v in DATASETS.items()},
        "runs": runs,
        "benchmarks": benchmarks,
        "leg_correlations": leg_corrs,
        "returns_series": returns_series,
    }
    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"results.json written ({out_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
