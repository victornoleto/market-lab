"""Iter 007 — Vol-managed SPY+TLT × time-series momentum overlay: 3 configs.

Pre-committed blend cfg: ``vt15_L21_cap20`` (iter 006's spy_real / ndx_real
local top: target_vol=0.15, lookback=21, max_leverage=2.0).

Momentum overlay grid (3 configs, all skip=21 per ``[ml_for_algo_trading,
ch.4 p.86]``):
  * M1 ``mom252_skip21`` — 12-1 canonical (Jegadeesh-Titman 1993,
    Moskowitz-Ooi-Pedersen 2012).
  * M2 ``mom126_skip21`` — 6-1 shorter trend.
  * M3 ``mom378_skip21`` — 18-1 longer trend.

Dataset shape identical to iter 006 (same TLT-aligned windows). Signal
uses per-dataset equity leg adjusted close (SPY for edu/spy, QQQ for
ndx).

Citations
---------
* ``[ml_for_algo_trading, ch.4 p.86]`` — 12-1 skip-a-month canonical.
* ``[algo_trading_chan, p.133, 164, ch.6]`` — time-series momentum.
* ``[risk_parity, p.10-11, ch.1]`` — inverse-variance weights (base).
* Moreira & Muir (2017), *JoF* 72(4) 1611-1644 — vol-managed × momentum.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]

sys.path.insert(0, str(ITER_DIR))
from momentum_overlay import apply_blend_with_momentum_overlay  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
OUT_DIR = ITER_DIR

# ---------------------------------------------------------------------------
# Fixed blend cfg + momentum overlay grid
# ---------------------------------------------------------------------------

BLEND_CFG = {"target_vol": 0.15, "lookback": 21, "max_leverage": 2.0}
BLEND_ID = "vt15_L21_cap20"

OVERLAY_CONFIGS: list[dict] = [
    {"cfg_id": "mom252_skip21", "lookback": 252, "skip": 21},
    {"cfg_id": "mom126_skip21", "lookback": 126, "skip": 21},
    {"cfg_id": "mom378_skip21", "lookback": 378, "skip": 21},
]

COST_BPS_PER_LEG = 0.0002

# ---------------------------------------------------------------------------
# Datasets (identical windows to iter 006)
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


def load_paired(eq: str, bd: str, start: str, end: str) -> tuple[pd.DataFrame, pd.Series]:
    """Return aligned (returns_df, equity_price_series)."""
    df_eq = pd.read_parquet(TIINGO_DIR / f"{eq}.parquet")
    df_bd = pd.read_parquet(TIINGO_DIR / f"{bd}.parquet")
    mask_eq = (df_eq.index >= start) & (df_eq.index <= end)
    mask_bd = (df_bd.index >= start) & (df_bd.index <= end)
    p_eq = df_eq.loc[mask_eq, "adj_close"]
    p_bd = df_bd.loc[mask_bd, "adj_close"]
    joined_price = pd.concat({"eq": p_eq, "bd": p_bd}, axis=1, join="inner").dropna()
    r = joined_price.pct_change().dropna()
    r.columns = [eq, bd]
    # Price signal = equity price aligned with returns index.
    price_signal = joined_price["eq"].loc[r.index]
    return r, price_signal


@dataclass
class RunMetrics:
    dataset: str
    cfg_id: str
    overlay_lookback: int
    overlay_skip: int
    bars: int
    sharpe: float
    cagr: float
    mdd: float
    final_equity: float
    gate_on_frac: float
    scale_median_when_on: float
    n_gate_transitions: int
    turnover_annual: float


def run_config(
    returns: pd.DataFrame, price_signal: pd.Series, overlay: dict,
) -> tuple[RunMetrics, pd.Series]:
    eq_col, bd_col = returns.columns
    net, pos_eq, pos_bd, scale, gate = apply_blend_with_momentum_overlay(
        returns[eq_col], returns[bd_col], price_signal,
        blend_cfg=BLEND_CFG,
        overlay_cfg={"lookback": overlay["lookback"], "skip": overlay["skip"]},
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    eq = (1.0 + net).cumprod()

    gate_valid = gate.dropna()
    gate_on = float(gate_valid.mean())
    scale_when_on = scale.loc[gate_valid.index][gate_valid > 0]
    scale_median_on = float(scale_when_on.median()) if len(scale_when_on) > 0 else 0.0
    transitions = int((gate_valid.astype(float).diff().abs() > 0).sum())

    dpos_eq = pos_eq.diff().abs().fillna(pos_eq.iloc[0])
    dpos_bd = pos_bd.diff().abs().fillna(pos_bd.iloc[0])
    turnover = float((dpos_eq + dpos_bd).sum() * 252.0 / len(dpos_eq))

    m = RunMetrics(
        dataset="",
        cfg_id=overlay["cfg_id"],
        overlay_lookback=overlay["lookback"],
        overlay_skip=overlay["skip"],
        bars=len(net),
        sharpe=_sharpe(net),
        cagr=_cagr(eq),
        mdd=_max_drawdown(eq),
        final_equity=float(eq.iloc[-1]),
        gate_on_frac=gate_on,
        scale_median_when_on=scale_median_on,
        n_gate_transitions=transitions,
        turnover_annual=turnover,
    )
    return m, net


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


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "blend_cfg": BLEND_CFG,
        "blend_id": BLEND_ID,
        "overlay_configs": OVERLAY_CONFIGS,
        "cost_bps_per_leg": COST_BPS_PER_LEG,
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
    }

    paired: dict[str, tuple[pd.DataFrame, pd.Series]] = {}
    for ds_name, ds in DATASETS.items():
        r, price = load_paired(
            ds["equity_symbol"], ds["bond_symbol"], ds["start"], ds["end"]
        )
        paired[ds_name] = (r, price)
        bench_series = r.iloc[:, 0]  # equity leg b&h
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        print(
            f"[{ds_name}] {ds['equity_symbol']}+{ds['bond_symbol']} "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars) "
            f"equity_bench Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%}"
        )

    for ds_name, (r, price) in paired.items():
        print(f"\n=== {ds_name} ({len(r)} bars) ===")
        all_results["runs"][ds_name] = {}
        all_results["returns_series"][ds_name] = {}
        bench_sharpe = all_results["benchmarks"][ds_name]["sharpe"]

        for overlay in OVERLAY_CONFIGS:
            m, net = run_config(r, price, overlay)
            m_dict = {
                "cfg_id": m.cfg_id,
                "overlay_lookback": m.overlay_lookback,
                "overlay_skip": m.overlay_skip,
                "bars": m.bars,
                "sharpe": m.sharpe,
                "cagr": m.cagr,
                "mdd": m.mdd,
                "final_equity": m.final_equity,
                "gate_on_frac": m.gate_on_frac,
                "scale_median_when_on": m.scale_median_when_on,
                "n_gate_transitions": m.n_gate_transitions,
                "turnover_annual": m.turnover_annual,
            }
            all_results["runs"][ds_name][m.cfg_id] = m_dict
            all_results["returns_series"][ds_name][m.cfg_id] = {
                "index": [str(t.date()) for t in net.index],
                "net_returns": net.round(10).tolist(),
            }
            edge = m.sharpe - bench_sharpe
            print(
                f"  {m.cfg_id:16s} Sharpe={m.sharpe:+.3f} (Δ={edge:+.3f}) "
                f"CAGR={m.cagr:+.2%} MDD={m.mdd:.2%} "
                f"gate_on={m.gate_on_frac:.1%} transitions={m.n_gate_transitions}"
            )

    out_path = OUT_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
