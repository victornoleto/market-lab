"""Iter 038 — VIX-regime-gated 3-leg static stack runner.

**Pre-committed cfg** ``regime_lev_vix_lt20_lo10_hi17`` — see
`hypothesis.md`. NO grid, NO sweep, NO post-hoc selection.

Mechanism: keep iter 037's 0.60/0.45/0.45 SPY/IEF/GLD weights; modulate
total leverage between 1.70× (low-vol regime: VIX_{t-1} < 20) and
1.00× (high-vol regime: VIX_{t-1} ≥ 20). Average leverage settles at
≈ 1.47-1.49 across the 3 datasets — leverage-neutral on average vs
iter 037's 1.50, so any Sharpe uplift is pure regime-timing per
Moreira-Muir 2017 Table IV.

Cumulative n_trials advance after iter 038: 4300 → 4303 (+3).

Citations
---------
* `[advances_fin_ml, ch.17-18]` — regime detection / Markov-switching.
* `[advances_fin_ml, p.162-164]` — no-lookahead lag rule (1-day shift).
* Moreira-Muir (2017), JF 72(4), DOI 10.1111/jofi.12513 — vol-managed Sharpe uplift.
* `[volatility_trading, p.217-218]` — Sinclair, VIX 20 threshold.
* `[risk_parity, ch.5]` + Asness-Frazzini-Pedersen (2012) FAJ 68(1) SSRN 1728082 — base.
* Erb-Harvey (2006), FAJ 62(2), DOI 10.2469/faj.v62.n2.4084 — gold strategic role.
* Asness-Moskowitz-Pedersen (2013), JF 68(3), DOI 10.1111/jofi.12021 — orthogonality.
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
from regime_lev_stack_3leg import apply_regime_lev_stack_3leg  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
VIX_PATH = ROOT / "data" / "external" / "macro" / "vix_daily.parquet"

# ---------------------------------------------------------------------------
# Pre-committed single config
# ---------------------------------------------------------------------------

CFG: dict = {
    "cfg_id": "regime_lev_vix_lt20_lo10_hi17",
    "threshold": 20.0,
    "lev_lo": 1.70,
    "lev_hi": 1.00,
    "base_weights": (0.60, 0.45, 0.45),
    "rebalance": "daily",
    "regime_signal": "VIX level (1-day lag)",
    "funding_cost_modeled": False,
}
COST_BPS_PER_LEG = 0.0002

# ---------------------------------------------------------------------------
# Datasets — iter 037 windows verbatim (apples-to-apples for the deltas)
# ---------------------------------------------------------------------------

DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "bond_symbol": "IEF",
        "gold_symbol": "GLD",
        "start": "2004-11-19",
        "end": "2026-04-15",
        "role": "SPY+IEF+GLD 21y (GLD-aligned, matches iter 035/036/037)",
    },
    "spy_real": {
        "equity_symbol": "SPY",
        "bond_symbol": "IEF",
        "gold_symbol": "GLD",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "SPY+IEF+GLD 17y post-GFC",
    },
    "ndx_real": {
        "equity_symbol": "QQQ",
        "bond_symbol": "IEF",
        "gold_symbol": "GLD",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "QQQ+IEF+GLD 16y tech-heavy",
    },
}


def load_triple_returns(
    eq: str, bd: str, gld: str, start: str, end: str,
) -> pd.DataFrame:
    df_eq = pd.read_parquet(TIINGO_DIR / f"{eq}.parquet")
    df_bd = pd.read_parquet(TIINGO_DIR / f"{bd}.parquet")
    df_gld = pd.read_parquet(TIINGO_DIR / f"{gld}.parquet")
    m_eq = (df_eq.index >= start) & (df_eq.index <= end)
    m_bd = (df_bd.index >= start) & (df_bd.index <= end)
    m_gld = (df_gld.index >= start) & (df_gld.index <= end)
    p = pd.concat({
        "eq": df_eq.loc[m_eq, "adj_close"],
        "bd": df_bd.loc[m_bd, "adj_close"],
        "gld": df_gld.loc[m_gld, "adj_close"],
    }, axis=1, join="inner").dropna()
    r = p.pct_change().dropna()
    r.columns = [eq, bd, gld]
    return r


def load_vix(start: str, end: str) -> pd.Series:
    """Load VIX daily close, padded a few days before `start` so that
    the 1-day lag has a value at the first return-bar."""
    df = pd.read_parquet(VIX_PATH)
    pad_start = (pd.Timestamp(start) - pd.Timedelta(days=10)).strftime("%Y-%m-%d")
    m = (df.index >= pad_start) & (df.index <= end)
    return df.loc[m, "VIX"]


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


def run_single_cfg(returns: pd.DataFrame, vix: pd.Series) -> tuple[dict, pd.Series, pd.DataFrame, pd.Series, pd.Series]:
    eq_col, bd_col, gld_col = returns.columns
    net, positions, scale, regime = apply_regime_lev_stack_3leg(
        returns[eq_col], returns[bd_col], returns[gld_col], vix,
        threshold=CFG["threshold"],
        lev_lo=CFG["lev_lo"],
        lev_hi=CFG["lev_hi"],
        base_weights=CFG["base_weights"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    eq_curve = (1.0 + net).cumprod()
    low_vol_frac = float((scale > 1.5).mean())
    high_vol_frac = float((scale < 1.5).mean())
    avg_lev = float(scale.mean())

    # Count regime flips (where ∆scale != 0).
    flip_mask = scale.diff().abs() > 1e-9
    n_flips = int(flip_mask.sum())

    turnover_per_leg: dict[str, float] = {}
    for c in positions.columns:
        dpos = positions[c].diff().abs().fillna(positions[c].iloc[0])
        turnover_per_leg[c] = float(dpos.sum() * 252.0 / len(dpos))
    turnover_total = float(sum(turnover_per_leg.values()))

    m = {
        "cfg_id": CFG["cfg_id"],
        "threshold": CFG["threshold"],
        "lev_lo": CFG["lev_lo"],
        "lev_hi": CFG["lev_hi"],
        "base_weights": list(CFG["base_weights"]),
        "bars": int(len(net)),
        "sharpe": float(_sharpe(net)),
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "scale_mean": avg_lev,
        "scale_median": float(scale.median()),
        "low_vol_frac": low_vol_frac,
        "high_vol_frac": high_vol_frac,
        "n_regime_flips": n_flips,
        "turnover_annual_per_leg": turnover_per_leg,
        "turnover_annual_total": turnover_total,
    }
    return m, net, positions, scale, regime


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": [{**CFG, "base_weights": list(CFG["base_weights"])}],
        "cost_bps_per_leg": COST_BPS_PER_LEG,
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "leg_correlations": {},
        "regime_summary": {},
        "pre_committed": True,
        "iter_label": "038-2026-04-25-0246-regime-lev-vix",
    }

    triples: dict[str, pd.DataFrame] = {}
    vixes: dict[str, pd.Series] = {}
    for ds_name, ds in DATASETS.items():
        r = load_triple_returns(
            ds["equity_symbol"], ds["bond_symbol"], ds["gold_symbol"],
            ds["start"], ds["end"],
        )
        triples[ds_name] = r
        v = load_vix(ds["start"], ds["end"])
        vixes[ds_name] = v
        bench_series = r.iloc[:, 0]
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        corr_mat = r.corr()
        eq_col, bd_col, gld_col = r.columns
        all_results["leg_correlations"][ds_name] = {
            "eq_bd": float(corr_mat.loc[eq_col, bd_col]),
            "eq_gld": float(corr_mat.loc[eq_col, gld_col]),
            "bd_gld": float(corr_mat.loc[bd_col, gld_col]),
        }
        # VIX summary on the return-window
        v_aligned = v.reindex(r.index, method="ffill").fillna(20.0)
        v_lag = v_aligned.shift(1).fillna(v_aligned.iloc[0])
        all_results["regime_summary"][ds_name] = {
            "vix_first": str(v_aligned.index[0].date()),
            "vix_last": str(v_aligned.index[-1].date()),
            "vix_mean": float(v_aligned.mean()),
            "vix_median": float(v_aligned.median()),
            "low_vol_frac_lagged": float((v_lag < CFG["threshold"]).mean()),
        }
        print(
            f"[{ds_name}] {ds['equity_symbol']}+{ds['bond_symbol']}+{ds['gold_symbol']} "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars) "
            f"equity_bench Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%}"
        )
        rs = all_results["regime_summary"][ds_name]
        print(
            f"  VIX mean={rs['vix_mean']:.2f}, median={rs['vix_median']:.2f}, "
            f"low_vol_frac={rs['low_vol_frac_lagged']:.3f}"
        )

    for ds_name, r in triples.items():
        print(f"\n=== {ds_name} ({len(r)} bars) — single cfg {CFG['cfg_id']} ===")
        m, net, positions, scale, regime = run_single_cfg(r, vixes[ds_name])
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
            f"  {m['cfg_id']:36s} Sharpe={m['sharpe']:+.4f} (Δ={edge:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"avg_lev={m['scale_mean']:.3f} flips={m['n_regime_flips']}"
        )
        print(
            f"    low_vol_frac={m['low_vol_frac']:.3f} "
            f"high_vol_frac={m['high_vol_frac']:.3f} "
            f"turnover/yr total={m['turnover_annual_total']:.4f}"
        )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
