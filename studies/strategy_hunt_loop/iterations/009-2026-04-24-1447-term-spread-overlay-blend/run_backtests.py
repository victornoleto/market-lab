"""Iter 009 — Backtests for term-spread overlay on vol-managed SPY+TLT blend.

Pre-committed overlay cfg ``ts_inv21_h50`` × pre-committed blend cfg
``vt15_L21_cap20`` × 3 datasets = 3 new trials.

Cumulative n_trials advance: 4240 → 4243.

Citations
---------
* `[regime_change, p.5-6, ch.2]` — regime-change principle.
* `[systematic_trading, p.144, p.170-171, ch.11]` — target_vol / IDM cap /
  tier-2 half-exposure de-lever.
* `[risk_parity, p.10-11, ch.1]` — naïve risk parity.
* Moreira & Muir (2017), *JoF* 72(4) — variance-scaling form.
* Estrella & Mishkin (1998) — 10Y-3M Treasury spread recession predictor.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ITER008_DIR = ITER_DIR.parent / "008-2026-04-24-1411-single-cfg-ex-ante-blend"
ROOT = ITER_DIR.parents[3]

sys.path.insert(0, str(ITER_DIR))
sys.path.insert(0, str(ITER008_DIR))

from term_spread_overlay import (  # noqa: E402
    OVERLAY_CFG,
    apply_blend_with_overlay,
    compute_gate_series,
    load_term_spread_daily,
)

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
MACRO_DIR = ROOT / "data" / "external" / "macro"
T10Y3M_PATH = MACRO_DIR / "t10y3m_daily.parquet"

# ---------------------------------------------------------------------------
# Pre-committed blend cfg (inherits iter 008's literature-anchored cfg)
# ---------------------------------------------------------------------------

BLEND_CFG: dict = {
    "cfg_id": "vt15_L21_cap20",
    "target_vol": 0.15,
    "lookback": 21,
    "max_leverage": 2.0,
}
COST_BPS_PER_LEG = 0.0002

# Combined cfg label: blend × overlay
COMBINED_CFG_ID = f"{BLEND_CFG['cfg_id']}+{OVERLAY_CFG['cfg_id']}"

# ---------------------------------------------------------------------------
# Datasets (identical to iter 008)
# ---------------------------------------------------------------------------

DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "bond_symbol": "TLT",
        "start": "2002-07-26",
        "end": "2026-04-15",
        "role": "SPY+TLT 24y — longest TLT-available window",
    },
    "spy_real": {
        "equity_symbol": "SPY",
        "bond_symbol": "TLT",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "SPY+TLT 17y post-GFC",
    },
    "ndx_real": {
        "equity_symbol": "QQQ",
        "bond_symbol": "TLT",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "QQQ+TLT 16y tech-heavy",
    },
}


def load_paired_returns(eq: str, bd: str, start: str, end: str) -> pd.DataFrame:
    df_eq = pd.read_parquet(TIINGO_DIR / f"{eq}.parquet")
    df_bd = pd.read_parquet(TIINGO_DIR / f"{bd}.parquet")
    mask_eq = (df_eq.index >= start) & (df_eq.index <= end)
    mask_bd = (df_bd.index >= start) & (df_bd.index <= end)
    p_eq = df_eq.loc[mask_eq, "adj_close"]
    p_bd = df_bd.loc[mask_bd, "adj_close"]
    joined = pd.concat({"eq": p_eq, "bd": p_bd}, axis=1, join="inner").dropna()
    r = joined.pct_change().dropna()
    r.columns = [eq, bd]
    return r


def benchmark_metrics(returns: pd.Series) -> dict:
    eq = (1.0 + returns).cumprod()
    return {
        "sharpe": _sharpe(returns),
        "cagr": _cagr(eq),
        "mdd": _max_drawdown(eq),
        "n_bars": len(returns),
        "first": str(returns.index[0].date()),
        "last": str(returns.index[-1].date()),
    }


def run_single_cfg(
    returns: pd.DataFrame,
    ts_ema_lagged: pd.Series,
) -> tuple[dict, pd.Series, pd.Series, pd.Series]:
    eq_col, bd_col = returns.columns
    net, pos_spy, pos_tlt, scale, gate = apply_blend_with_overlay(
        returns[eq_col],
        returns[bd_col],
        ts_ema_lagged=ts_ema_lagged,
        target_vol=BLEND_CFG["target_vol"],
        lookback=BLEND_CFG["lookback"],
        max_leverage=BLEND_CFG["max_leverage"],
        haircut=OVERLAY_CFG["haircut"],
        threshold=OVERLAY_CFG["threshold"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    eq = (1.0 + net).cumprod()
    gate_fire_rate = float((gate < 1.0).mean())
    # Orthogonality diagnostic: correlation between binary gate and blend scale.
    # Lower correlation => more orthogonal overlay signal.
    try:
        rho = float(gate.corr(scale))
    except Exception:
        rho = float("nan")
    # Overlap of gate-firing bars with the bottom-20% blend-scale bars.
    s20 = scale.quantile(0.20)
    bottom20 = scale <= s20
    gate_fire = gate < 1.0
    if int(bottom20.sum()) > 0 and int(gate_fire.sum()) > 0:
        overlap_numer = int((bottom20 & gate_fire).sum())
        overlap_denom = int(gate_fire.sum())
        overlap_frac = overlap_numer / overlap_denom
    else:
        overlap_frac = float("nan")

    cap_hit = float(
        np.isclose(scale.to_numpy(float), BLEND_CFG["max_leverage"], rtol=1e-9, atol=1e-12).mean()
    )
    w_spy_median = float((pos_spy / (scale * gate).replace(0.0, np.nan)).median())
    dpos_spy = pos_spy.diff().abs().fillna(pos_spy.iloc[0])
    dpos_tlt = pos_tlt.diff().abs().fillna(pos_tlt.iloc[0])
    turnover = float((dpos_spy + dpos_tlt).sum() * 252.0 / len(dpos_spy))

    m = {
        "cfg_id": COMBINED_CFG_ID,
        "blend_cfg": BLEND_CFG,
        "overlay_cfg": OVERLAY_CFG,
        "bars": len(net),
        "sharpe": float(_sharpe(net)),
        "cagr": float(_cagr(eq)),
        "mdd": float(_max_drawdown(eq)),
        "final_equity": float(eq.iloc[-1]),
        "scale_mean": float(scale.mean()),
        "scale_median": float(scale.median()),
        "scale_cap_hit_frac": cap_hit,
        "w_spy_median": w_spy_median,
        "turnover_annual": turnover,
        "gate_fire_rate": gate_fire_rate,
        "gate_scale_corr": rho,
        "gate_bottom20_overlap_frac": overlap_frac,
    }
    return m, net, gate, scale


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "blend_cfg": BLEND_CFG,
        "overlay_cfg": OVERLAY_CFG,
        "combined_cfg_id": COMBINED_CFG_ID,
        "cost_bps_per_leg": COST_BPS_PER_LEG,
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "gate_series": {},
        "leg_correlations": {},
        "pre_committed": True,
        "reference_iter": "008-2026-04-24-1411-single-cfg-ex-ante-blend",
        "macro_source": str(T10Y3M_PATH.relative_to(ROOT)),
    }

    paired: dict[str, pd.DataFrame] = {}
    for ds_name, ds in DATASETS.items():
        r = load_paired_returns(ds["equity_symbol"], ds["bond_symbol"], ds["start"], ds["end"])
        paired[ds_name] = r
        bench_series = r.iloc[:, 0]  # equity-leg b&h benchmark
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        corr = float(r.corr().iloc[0, 1])
        all_results["leg_correlations"][ds_name] = corr
        print(
            f"[{ds_name}] {ds['equity_symbol']}+{ds['bond_symbol']} "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars) "
            f"equity_bench Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%} ρ_stockbond={corr:+.3f}"
        )

    for ds_name, r in paired.items():
        print(f"\n=== {ds_name} ({len(r)} bars) — {COMBINED_CFG_ID} ===")
        ts_ema_lagged = load_term_spread_daily(T10Y3M_PATH, r.index)
        m, net, gate, scale = run_single_cfg(r, ts_ema_lagged)
        all_results["runs"][ds_name] = {COMBINED_CFG_ID: m}
        all_results["returns_series"][ds_name] = {
            COMBINED_CFG_ID: {
                "index": [str(t.date()) for t in net.index],
                "net_returns": net.round(10).tolist(),
            }
        }
        all_results["gate_series"][ds_name] = {
            "index": [str(t.date()) for t in gate.index],
            "gate": gate.round(4).tolist(),
            "scale": scale.round(6).tolist(),
        }
        bench_sharpe = all_results["benchmarks"][ds_name]["sharpe"]
        edge = m["sharpe"] - bench_sharpe
        print(
            f"  {m['cfg_id']:40s} Sharpe={m['sharpe']:+.4f} (Δ={edge:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"gate_fire={m['gate_fire_rate']:.1%} "
            f"ρ(gate,scale)={m['gate_scale_corr']:+.3f} "
            f"overlap_bottom20={m['gate_bottom20_overlap_frac']:.1%}"
        )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
