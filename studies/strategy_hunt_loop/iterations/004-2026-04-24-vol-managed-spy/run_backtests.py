"""Iter 004 — Vol-managed SPY: 36 configs × 3 datasets.

Grid:
  * target_vol    ∈ {0.10, 0.15, 0.20}
  * lookback      ∈ {21, 63, 126, 252}
  * max_leverage  ∈ {1.5, 2.0, 3.0}
= 36 configs

Mechanism (single-asset, returns-level):
  * r_t      = unscaled daily return (SPY/QQQ/SPYSIM close.pct_change)
  * σ̂_{t-1} = rolling std over [t-L, t-1] × √252
  * s_t     = clip(target_vol / σ̂_{t-1}, 0, max_leverage)
  * gross_t = s_t · r_t
  * cost_t  = |s_t - s_{t-1}| · 0.0002   # 2 bps round-trip, SPY-tight
  * net_t   = gross_t - cost_t

Citations:
  * [systematic_trading, p.40 ch.2, p.107-111, p.144-146 ch.9] — vol standardisation
  * [advances_fin_ml, p.162-164] — σ̂_{t-1} lag (no look-ahead)
  * Moreira & Muir (2017), JoF 72(4) 1611-1644 — vol-managed alpha

Datasets:
  * educational: SPYSIM synth 1986-01-02 → 2026-04-17 (testfolio cache)
  * spy_real:    Tiingo SPY    2009-06-25 → 2026-04-20
  * ndx_real:    Tiingo QQQ    2010-02-12 → 2026-04-20

Writes:
  * results.json — per-(dataset, config) metrics + full net-return series
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd

from ai_trade.backtest.metrics.performance import (
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)
from ai_trade.backtest.metrics.vol_target import apply_vol_target

ROOT = Path(__file__).resolve().parents[4]  # → /var/www/pessoal/ai-trade
TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
TESTFOLIO_DIR = ROOT / "data" / "testfolio" / "cache"
OUT_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Grid
# ---------------------------------------------------------------------------

TARGET_VOLS = (0.10, 0.15, 0.20)
LOOKBACKS = (21, 63, 126, 252)
MAX_LEVS = (1.5, 2.0, 3.0)

CONFIGS: list[dict] = [
    {
        "cfg_id": f"tv{int(tv * 100):02d}_L{lb}_cap{int(cap * 10):02d}",
        "target_vol": tv,
        "lookback": lb,
        "max_leverage": cap,
    }
    for tv, lb, cap in product(TARGET_VOLS, LOOKBACKS, MAX_LEVS)
]

COST_BPS_ROUNDTRIP = 0.0002  # 2 bps per unit of scale change, Inter-tight SPY

# ---------------------------------------------------------------------------
# Datasets
# ---------------------------------------------------------------------------

DATASETS: dict[str, dict] = {
    "educational": {
        "source": "testfolio_spysim",
        "start": "1986-01-02",
        "end": "2026-04-20",
        "role": "SPYSIM synth 40y — longest OOS window, dot-com + GFC + COVID",
    },
    "spy_real": {
        "source": "tiingo_spy",
        "start": "2009-06-25",
        "end": "2026-04-20",
        "role": "SPY real 17y post-GFC",
    },
    "ndx_real": {
        "source": "tiingo_qqq",
        "start": "2010-02-12",
        "end": "2026-04-20",
        "role": "QQQ real 16y tech-heavy",
    },
}


def load_returns(source: str, start: str, end: str) -> pd.Series:
    """Load daily returns for a dataset (educational/spy/ndx)."""
    if source == "testfolio_spysim":
        df = pd.read_parquet(TESTFOLIO_DIR / "history.parquet")
        price = df.loc[start:end, "SPYSIM"]
    elif source == "tiingo_spy":
        df = pd.read_parquet(TIINGO_DIR / "SPY.parquet")
        # adj_close matches the frozen benchmarks in scoring.BENCHMARKS
        # (Sharpe 0.90, CAGR 14.97%, MDD 33.70% for 2009-06-25→2026-04-20).
        price = df.loc[(df.index >= start) & (df.index <= end), "adj_close"]
    elif source == "tiingo_qqq":
        df = pd.read_parquet(TIINGO_DIR / "QQQ.parquet")
        price = df.loc[(df.index >= start) & (df.index <= end), "adj_close"]
    else:
        raise ValueError(f"unknown source: {source}")
    r = price.pct_change().dropna()
    r.name = source
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
    turnover_annual: float  # sum(|Δs|) * 252 / n_bars


def run_config(returns: pd.Series, cfg: dict) -> tuple[RunMetrics, pd.Series]:
    scaled_gross, scale = apply_vol_target(
        returns,
        target_vol=cfg["target_vol"],
        lookback=cfg["lookback"],
        max_leverage=cfg["max_leverage"],
    )
    # Execution cost: proportional to |Δscale| per bar.
    dscale = scale.diff().abs().fillna(scale.iloc[0])  # first bar is a fill from 0
    cost = dscale * COST_BPS_ROUNDTRIP
    net = (scaled_gross - cost).astype(float)
    net.name = scaled_gross.name

    eq = (1.0 + net).cumprod()
    cap_hit = float(
        np.isclose(scale.to_numpy(float), cfg["max_leverage"], rtol=1e-9, atol=1e-12).mean()
    )
    turnover_annual = float(dscale.sum() * 252.0 / len(dscale))

    m = RunMetrics(
        dataset="",  # filled by caller
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
        turnover_annual=turnover_annual,
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": CONFIGS,
        "cost_bps_roundtrip": COST_BPS_ROUNDTRIP,
        "benchmarks": {},
        "runs": {},
        "returns_series": {},  # per-config net returns, for gate computation
    }

    # Cache raw returns per dataset to reuse across 36 configs.
    raw_returns: dict[str, pd.Series] = {}
    for ds_name, ds in DATASETS.items():
        r = load_returns(ds["source"], ds["start"], ds["end"])
        raw_returns[ds_name] = r
        bench = benchmark_metrics(r)
        all_results["benchmarks"][ds_name] = bench
        print(
            f"[{ds_name}] {ds['source']} {bench['first']} → {bench['last']} "
            f"({bench['n_bars']} bars) "
            f"Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%}"
        )

    for ds_name, r in raw_returns.items():
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
                f"scale_med={m.scale_median:.2f} cap_hit={m.scale_cap_hit_frac:.1%}"
            )

    out_path = OUT_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
