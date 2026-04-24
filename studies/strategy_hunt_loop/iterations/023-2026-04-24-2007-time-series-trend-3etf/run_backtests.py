"""Iter 023 — 3-asset time-series trend backtests on 3 real-data datasets.

**Pre-committed cfg** ``ts_trend_L252_skip21_vol10_cap20`` — see
``hypothesis.md``. NO grid, NO sweep, NO post-hoc selection. Single
pre-committed cfg combining canonical 12-1 momentum (Moskowitz-Ooi-
Pedersen 2012 / `[algo_trading_chan, p.164]`) with per-asset vol-target
(`[systematic_trading, p.40, ch.2]`) and total-leverage cap 2.0
(`[systematic_trading, p.170-171, ch.11]`).

Cumulative n_trials advance after iter 023: 4273 → 4276 (+3 = 1 cfg ×
3 datasets).

Citations
---------
* `[algo_trading_chan, p.164, ch.6]` — Moskowitz-Yao-Pedersen 2012 / 12-1.
* `[systematic_trading, p.40, ch.2]` — vol standardisation primitive.
* `[systematic_trading, p.170-171, ch.11]` — IDM ≤ 2.5 leverage cap.
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
from trend_3etf import apply_trend_3etf  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"

# ---------------------------------------------------------------------------
# Pre-committed single config (literature-anchored)
# ---------------------------------------------------------------------------

CFG: dict = {
    "cfg_id": "ts_trend_L252_skip21_vol10_cap20",
    "signal_lookback": 252,         # 12-month formation [Moskowitz 2012]
    "signal_skip": 21,              # skip-a-month [Jegadeesh-Titman 1993]
    "vol_lookback": 21,             # iter 016 / Carver canonical
    "target_vol_per_asset": 0.10,   # 10 % per leg, ~17 % aggregate uncorr
    "max_leverage": 2.0,            # match iter 016 cap
    "cost_bps_per_leg": 0.0002,     # 2 bps per leg ∆position (matches iter 016)
    "rebalance": "daily",
}
COST_BPS_PER_LEG = CFG["cost_bps_per_leg"]

# ---------------------------------------------------------------------------
# Datasets (real Tiingo prices, 3-leg basket)
# ---------------------------------------------------------------------------

DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "bond_symbol": "TLT",
        "gold_symbol": "GLD",
        "start": "2006-01-03",
        "end": "2026-04-15",
        "role": "SPY+TLT+GLD ~20y multi-asset trend basket",
    },
    "spy_real": {
        "equity_symbol": "SPY",
        "bond_symbol": "TLT",
        "gold_symbol": "GLD",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "SPY+TLT+GLD post-GFC 17y",
    },
    "ndx_real": {
        "equity_symbol": "QQQ",
        "bond_symbol": "TLT",
        "gold_symbol": "GLD",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "QQQ+TLT+GLD tech-heavy 16y",
    },
}


def load_three_returns(eq: str, bd: str, gd: str, start: str, end: str) -> pd.DataFrame:
    """Load three asset return streams aligned on a common DatetimeIndex."""
    frames = {}
    for col, sym in (("eq", eq), ("bd", bd), ("gd", gd)):
        df = pd.read_parquet(TIINGO_DIR / f"{sym}.parquet")
        m = (df.index >= start) & (df.index <= end)
        frames[col] = df.loc[m, "adj_close"]
    p = pd.concat(frames, axis=1, join="inner").dropna()
    r = p.pct_change().dropna()
    r.columns = [eq, bd, gd]
    return r


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


def run_single_cfg(returns: pd.DataFrame) -> tuple[dict, pd.Series, pd.DataFrame, pd.Series, pd.DataFrame]:
    eq_col, bd_col, gd_col = returns.columns
    net, positions, total_gross, signals = apply_trend_3etf(
        returns,
        signal_lookback=CFG["signal_lookback"],
        signal_skip=CFG["signal_skip"],
        vol_lookback=CFG["vol_lookback"],
        target_vol_per_asset=CFG["target_vol_per_asset"],
        max_leverage=CFG["max_leverage"],
        cost_bps_per_leg=CFG["cost_bps_per_leg"],
    )
    eq_curve = (1.0 + net).cumprod()
    cap_hit = float(
        np.isclose(total_gross.to_numpy(float), CFG["max_leverage"], atol=1e-9).mean()
    )
    # Signal activity per leg (fraction of bars where |signal| > 0).
    signal_active = {
        col: float((signals[col].abs() > 0).mean()) for col in signals.columns
    }
    signal_long = {
        col: float((signals[col] > 0).mean()) for col in signals.columns
    }
    signal_short = {
        col: float((signals[col] < 0).mean()) for col in signals.columns
    }
    # Time-in-shorts proxy: at least one leg short.
    any_short = float((signals < 0).any(axis=1).mean())

    turnover_per_leg = {}
    for c in positions.columns:
        dpos = positions[c].diff().abs().fillna(positions[c].iloc[0].__abs__())
        turnover_per_leg[c] = float(dpos.sum() * 252.0 / len(dpos))
    turnover_total = float(sum(turnover_per_leg.values()))

    m = {
        "cfg_id": CFG["cfg_id"],
        **{k: CFG[k] for k in [
            "signal_lookback", "signal_skip", "vol_lookback",
            "target_vol_per_asset", "max_leverage",
        ]},
        "bars": int(len(net)),
        "sharpe": float(_sharpe(net)),
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "scale_mean": float(total_gross.mean()),
        "scale_median": float(total_gross.median()),
        "scale_min": float(total_gross.min()),
        "scale_max": float(total_gross.max()),
        "scale_cap_hit_frac": cap_hit,
        "scale_zero_frac": float((total_gross < 1e-6).mean()),
        "signal_active_frac_per_leg": signal_active,
        "signal_long_frac_per_leg": signal_long,
        "signal_short_frac_per_leg": signal_short,
        "any_short_frac_total": any_short,
        "turnover_annual_per_leg": turnover_per_leg,
        "turnover_annual_total": turnover_total,
    }
    return m, net, positions, total_gross, signals


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": [CFG],
        "cost_bps_per_leg": COST_BPS_PER_LEG,
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "leg_correlations": {},
        "pre_committed": True,
        "iter_label": "023-2026-04-24-2007-time-series-trend-3etf",
    }

    triples: dict[str, pd.DataFrame] = {}
    for ds_name, ds in DATASETS.items():
        r = load_three_returns(
            ds["equity_symbol"], ds["bond_symbol"], ds["gold_symbol"],
            ds["start"], ds["end"],
        )
        triples[ds_name] = r
        # Equity-leg buy-hold benchmark (matches iter 016 / scoring frozen bench).
        bench_series = r.iloc[:, 0]
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        # Pairwise leg correlations.
        corrs = r.corr()
        all_results["leg_correlations"][ds_name] = {
            f"{a}_{b}": float(corrs.iloc[i, j])
            for i, a in enumerate(r.columns)
            for j, b in enumerate(r.columns)
            if i < j
        }
        print(
            f"[{ds_name}] {ds['equity_symbol']}+{ds['bond_symbol']}+{ds['gold_symbol']} "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars) "
            f"equity_bench Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%}"
        )

    for ds_name, r in triples.items():
        print(f"\n=== {ds_name} ({len(r)} bars) — single cfg {CFG['cfg_id']} ===")
        m, net, positions, total_gross, signals = run_single_cfg(r)
        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in net.index],
                "net_returns": net.round(10).tolist(),
            }
        }
        bench_sharpe = all_results["benchmarks"][ds_name]["sharpe"]
        edge = m["sharpe"] - bench_sharpe
        print(
            f"  {m['cfg_id']:32s} Sharpe={m['sharpe']:+.4f} (Δ={edge:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"scale[mean/med/min/max]={m['scale_mean']:.2f}/{m['scale_median']:.2f}/"
            f"{m['scale_min']:.2f}/{m['scale_max']:.2f} "
            f"cap_hit={m['scale_cap_hit_frac']:.2%}"
        )
        cols = list(signals.columns)
        print(
            f"    signal_long_frac:  "
            + " ".join(f"{c}={m['signal_long_frac_per_leg'][c]:.2%}" for c in cols)
        )
        print(
            f"    signal_short_frac: "
            + " ".join(f"{c}={m['signal_short_frac_per_leg'][c]:.2%}" for c in cols)
        )
        print(
            f"    any_short_frac={m['any_short_frac_total']:.2%}  "
            f"turnover/yr={m['turnover_annual_total']:.3f}"
        )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
