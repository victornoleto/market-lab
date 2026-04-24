"""Iter 009 — Term-spread (T10Y3M) macro overlay on iter 008's blend.

Applies a single pre-committed binary gate on top of the iter 008
vol-managed SPY+TLT blend. The gate uses the 21-bar EMA of the 10Y-3M
Treasury spread, lagged by 1 bar (no look-ahead), with threshold=0.0
and haircut=0.5.

Pipeline (at each bar ``t``):

    1. Run iter 008 blend to get (s_t, w_spy_t, w_tlt_t).
    2. gate_t = 1.0 if EMA21(T10Y3M)_{t-1} > 0 else 0.5
    3. pos_spy_t = s_t · w_spy_t · gate_t
       pos_tlt_t = s_t · w_tlt_t · gate_t
    4. gross_t  = pos_spy_t · r_spy[t] + pos_tlt_t · r_tlt[t]
    5. cost_t   = (|Δpos_spy| + |Δpos_tlt|) · cost_bps_per_leg
    6. net_t    = gross_t - cost_t

Citations
---------
* `[regime_change, p.5-6, ch.2]` — regime change principle.
* `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag (no look-ahead),
  extended here to macro series T10Y3M_{t-1}.
* `[systematic_trading, p.144, ch.9]` — tier-2 half-exposure de-lever.
* Estrella & Mishkin (1998) — 10Y-3M Treasury spread canonical
  recession predictor.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ITER008_DIR = ITER_DIR.parent / "008-2026-04-24-1411-single-cfg-ex-ante-blend"
ITER006_DIR = ITER_DIR.parent / "006-2026-04-24-1027-vol-managed-60-40"

sys.path.insert(0, str(ITER006_DIR))
from stock_bond_blend import apply_blend_variance_target  # noqa: E402


# ---------------------------------------------------------------------------
# Pre-committed overlay configuration (see hypothesis.md § Pre-committed)
# ---------------------------------------------------------------------------

OVERLAY_CFG: dict = {
    "cfg_id": "ts_inv21_h50",
    "indicator": "t10y3m_daily",
    "smoothing_window": 21,   # ≈ 1 trading month (monthly emulation)
    "threshold": 0.0,         # classical yield curve inversion
    "haircut": 0.5,           # tier-2 half-exposure de-lever [systematic_trading, p.144]
    "lag_bars": 1,            # no look-ahead [advances_fin_ml, p.162-164]
}


def load_term_spread_daily(
    t10y3m_path: Path,
    align_index: pd.DatetimeIndex,
) -> pd.Series:
    """Load T10Y3M, reindex onto equity calendar, lag 1 bar, EMA-smooth.

    Returns the lagged EMA21 series aligned to ``align_index``.
    """
    df = pd.read_parquet(t10y3m_path)
    if "term_spread" not in df.columns:
        raise ValueError(f"expected 'term_spread' col in {t10y3m_path}, got {df.columns.tolist()}")
    ts_raw = df["term_spread"].astype(float)
    # Reindex onto trading-day calendar (equity index). Forward-fill over
    # any NaN (e.g., Fed holidays the equity market trades through).
    ts_on_eq = ts_raw.reindex(align_index, method="ffill")
    # Lag 1 bar — value known at close of bar t-1 used to size bar t.
    ts_lagged = ts_on_eq.shift(OVERLAY_CFG["lag_bars"])
    # EMA21 smoothing (span = 21).
    ts_ema = ts_lagged.ewm(
        span=OVERLAY_CFG["smoothing_window"],
        adjust=False,
    ).mean()
    ts_ema.name = "t10y3m_ema21_lag1"
    return ts_ema


def compute_gate_series(ts_ema_lagged: pd.Series) -> pd.Series:
    """Binary gate: 1.0 if term-spread EMA > threshold else haircut."""
    gate = pd.Series(1.0, index=ts_ema_lagged.index, dtype=float)
    gate.loc[ts_ema_lagged <= OVERLAY_CFG["threshold"]] = OVERLAY_CFG["haircut"]
    # NaN in EMA (bootstrapping bars before smoothing has enough data) →
    # default to 1.0 (no haircut). This affects < 21 bars per run; these
    # are dropped anyway by the blend's lookback warm-up.
    gate.loc[ts_ema_lagged.isna()] = 1.0
    gate.name = "gate"
    return gate


def apply_blend_with_overlay(
    r_spy: pd.Series,
    r_tlt: pd.Series,
    *,
    ts_ema_lagged: pd.Series,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    haircut: float,
    threshold: float,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """Blend + term-spread overlay. Returns (net, pos_spy, pos_tlt, scale, gate)."""
    # Run iter 008 blend un-gated.
    net_blend, pos_spy, pos_tlt, scale = apply_blend_variance_target(
        r_spy, r_tlt,
        target_vol=target_vol,
        lookback=lookback,
        max_leverage=max_leverage,
        periods_per_year=periods_per_year,
        cost_bps_per_leg=cost_bps_per_leg,  # kept identical; gate applied below
    )
    # Recompute from scratch so costs match gated positions, not un-gated ones.
    ts_on_valid = ts_ema_lagged.reindex(scale.index)
    gate = pd.Series(1.0, index=scale.index, dtype=float)
    gate.loc[ts_on_valid <= threshold] = haircut
    gate.loc[ts_on_valid.isna()] = 1.0

    pos_spy_g = pos_spy * gate
    pos_tlt_g = pos_tlt * gate

    a_v = r_spy.loc[scale.index].astype(float)
    b_v = r_tlt.loc[scale.index].astype(float)
    gross = pos_spy_g * a_v + pos_tlt_g * b_v

    dpos_spy = pos_spy_g.diff().abs().fillna(pos_spy_g.iloc[0])
    dpos_tlt = pos_tlt_g.diff().abs().fillna(pos_tlt_g.iloc[0])
    cost = (dpos_spy + dpos_tlt) * cost_bps_per_leg
    net = (gross - cost).astype(float)

    net.name = "net"
    pos_spy_g.name = "pos_spy_gated"
    pos_tlt_g.name = "pos_tlt_gated"
    gate.name = "gate"
    return net, pos_spy_g, pos_tlt_g, scale, gate
