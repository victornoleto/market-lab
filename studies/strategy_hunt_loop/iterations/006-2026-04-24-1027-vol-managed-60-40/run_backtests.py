"""Iter 006 — Vol-managed SPY+TLT (QQQ+TLT) blend: 12 configs × 3 datasets.

Grid (same shape as iter 005 for comparability):
  * target_vol    ∈ {0.15, 0.20}
  * lookback      ∈ {21, 63, 126}
  * max_leverage  ∈ {1.5, 2.0}     (both ≤ IDM ceiling 2.5)
= 12 configs

Mechanism (two-leg inverse-variance + Moreira-Muir portfolio scaling):
  * w_spy_t     = (1/σ²_spy_{t-1}) / (1/σ²_spy_{t-1} + 1/σ²_tlt_{t-1})
  * σ²_port     = w_spy²·σ²_spy + w_tlt²·σ²_tlt + 2·w_spy·w_tlt·cov
  * s_t         = clip(target_vol² / σ²_port_{t-1}, 0, cap)
  * pos_spy_t   = s_t · w_spy_t,   pos_tlt_t = s_t · w_tlt_t
  * gross_t     = pos_spy_t · r_spy_t + pos_tlt_t · r_tlt_t
  * cost_t      = (|ΔPos_spy| + |ΔPos_tlt|) · 0.0002
  * net_t       = gross_t − cost_t

Citations
---------
* `[risk_parity, p.10-11, ch.1]` — naïve risk parity / inverse-variance.
* Moreira & Muir (2017), *JoF* 72(4), 1611-1644 — variance-scaling.
* `[systematic_trading, p.170-171, ch.11]` — IDM ≤ 2.5 cap.
* `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag.

Datasets (windows reflect TLT cache availability):
  * educational: SPY+TLT   2002-07-26 → 2026-04-15 (24y, longest with TLT)
  * spy_real:    SPY+TLT   2009-06-25 → 2026-04-15 (17y, frozen)
  * ndx_real:    QQQ+TLT   2010-02-12 → 2026-04-15 (16y, frozen)

Benchmark note: educational slot custom benchmark = SPY b&h 2002-2026;
spy_real + ndx_real use the frozen scoring.BENCHMARKS (SPY 0.90 / QQQ
0.955). TLT last bar is 2026-04-15 (1 trading day earlier than SPY/QQQ
2026-04-20), so we truncate to the TLT end.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]

sys.path.insert(0, str(ITER_DIR))
from stock_bond_blend import apply_blend_variance_target  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
OUT_DIR = ITER_DIR

# ---------------------------------------------------------------------------
# Grid
# ---------------------------------------------------------------------------

TARGET_VOLS = (0.15, 0.20)
LOOKBACKS = (21, 63, 126)
MAX_LEVS = (1.5, 2.0)

CONFIGS: list[dict] = [
    {
        "cfg_id": f"vt{int(tv * 100):02d}_L{lb}_cap{int(cap * 10):02d}",
        "target_vol": tv,
        "lookback": lb,
        "max_leverage": cap,
    }
    for tv, lb, cap in product(TARGET_VOLS, LOOKBACKS, MAX_LEVS)
]

COST_BPS_PER_LEG = 0.0002  # 2 bps per unit of per-leg position change.

# ---------------------------------------------------------------------------
# Datasets
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
    # Align on intersection of trading days.
    joined = pd.concat(
        {"eq": p_eq, "bd": p_bd}, axis=1, join="inner"
    ).dropna()
    r = joined.pct_change().dropna()
    r.columns = [eq, bd]
    return r


# ---------------------------------------------------------------------------
# Per-config backtest
# ---------------------------------------------------------------------------


@dataclass
class RunMetrics:
    dataset: str
    cfg_id: str
    target_vol: float
    lookback: int
    max_leverage: float
    bars: int
    sharpe: float
    cagr: float
    mdd: float
    final_equity: float
    scale_mean: float
    scale_median: float
    scale_cap_hit_frac: float
    w_spy_median: float
    turnover_annual: float


def run_config(returns: pd.DataFrame, cfg: dict) -> tuple[RunMetrics, pd.Series]:
    eq_col, bd_col = returns.columns
    net, pos_spy, pos_tlt, scale = apply_blend_variance_target(
        returns[eq_col], returns[bd_col],
        target_vol=cfg["target_vol"],
        lookback=cfg["lookback"],
        max_leverage=cfg["max_leverage"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    eq = (1.0 + net).cumprod()
    cap_hit = float(
        np.isclose(
            scale.to_numpy(float), cfg["max_leverage"], rtol=1e-9, atol=1e-12
        ).mean()
    )
    w_spy_median = float((pos_spy / scale).median())
    dpos_spy = pos_spy.diff().abs().fillna(pos_spy.iloc[0])
    dpos_tlt = pos_tlt.diff().abs().fillna(pos_tlt.iloc[0])
    turnover = float((dpos_spy + dpos_tlt).sum() * 252.0 / len(dpos_spy))

    m = RunMetrics(
        dataset="",
        cfg_id=cfg["cfg_id"],
        target_vol=cfg["target_vol"],
        lookback=cfg["lookback"],
        max_leverage=cfg["max_leverage"],
        bars=len(net),
        sharpe=_sharpe(net),
        cagr=_cagr(eq),
        mdd=_max_drawdown(eq),
        final_equity=float(eq.iloc[-1]),
        scale_mean=float(scale.mean()),
        scale_median=float(scale.median()),
        scale_cap_hit_frac=cap_hit,
        w_spy_median=w_spy_median,
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
        "configs": CONFIGS,
        "cost_bps_per_leg": COST_BPS_PER_LEG,
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "leg_correlations": {},
    }

    paired: dict[str, pd.DataFrame] = {}
    for ds_name, ds in DATASETS.items():
        r = load_paired_returns(
            ds["equity_symbol"], ds["bond_symbol"], ds["start"], ds["end"]
        )
        paired[ds_name] = r
        # Benchmark per slot: SPY/QQQ b&h over the same window (not 60/40!)
        # — scoring.py BENCHMARKS dict for spy_real/ndx_real is frozen at
        # this exact definition; educational custom bench is equity-leg b&h.
        bench_series = r.iloc[:, 0]  # first col = equity leg returns
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
        print(f"\n=== {ds_name} ({len(r)} bars) ===")
        all_results["runs"][ds_name] = {}
        all_results["returns_series"][ds_name] = {}
        bench_sharpe = all_results["benchmarks"][ds_name]["sharpe"]

        for cfg in CONFIGS:
            m, net = run_config(r, cfg)
            m_dict = {
                "cfg_id": m.cfg_id,
                "target_vol": m.target_vol,
                "lookback": m.lookback,
                "max_leverage": m.max_leverage,
                "bars": m.bars,
                "sharpe": m.sharpe,
                "cagr": m.cagr,
                "mdd": m.mdd,
                "final_equity": m.final_equity,
                "scale_mean": m.scale_mean,
                "scale_median": m.scale_median,
                "scale_cap_hit_frac": m.scale_cap_hit_frac,
                "w_spy_median": m.w_spy_median,
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
                f"scale_med={m.scale_median:.2f} cap_hit={m.scale_cap_hit_frac:.1%} "
                f"w_spy_med={m.w_spy_median:.2f}"
            )

    out_path = OUT_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
