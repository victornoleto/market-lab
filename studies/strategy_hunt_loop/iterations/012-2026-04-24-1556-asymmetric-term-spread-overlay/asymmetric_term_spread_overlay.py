"""Iter 012 — Asymmetric T10Y3M macro overlay (equity-leg-only haircut).

Structural distinctions vs iter 009 (dead-end):

* ``smoothing_window = 5`` (not 21) — preserves the 6-18 month recession
  lead-time that was erased by 21-day EMA smoothing.
* Haircut applied to the **SPY leg only**; TLT leg retains full weight.
  Respects the −0.30 SPY-TLT correlation: flight-to-quality rally on
  bonds during recession is preserved.

Pipeline (at each bar t):

    1. Run iter 006 blend → un-gated (s_t, w_spy_t, w_tlt_t).
    2. gate_t = 1.0 if EMA5(T10Y3M)_{t-1} > 0 else 0.5
    3. pos_spy_t = s_t · w_spy_t · gate_t   (HAIRCUT HERE)
       pos_tlt_t = s_t · w_tlt_t            (NO haircut on bond leg)
    4. gross_t  = pos_spy_t · r_spy[t] + pos_tlt_t · r_tlt[t]
    5. cost_t   = (|Δpos_spy_gated| + |Δpos_tlt_base|) · cost_bps_per_leg
    6. net_t    = gross_t − cost_t

Citations
---------
* `[regime_change, p.5-6, ch.2]` — regime-change principle.
* `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag (no look-ahead),
  extended here to macro series T10Y3M_{t-1}.
* `[systematic_trading, p.144, ch.9]` — tier-2 half-exposure haircut.
* `[risk_parity, p.80-81, ch.4]` — negative SPY-TLT correlation motivates
  the asymmetric (bond-preserving) haircut.
* Estrella & Mishkin (1998) — 10Y-3M Treasury spread canonical recession
  predictor, 6-18 month lead.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ITER006_DIR = ITER_DIR.parent / "006-2026-04-24-1027-vol-managed-60-40"

sys.path.insert(0, str(ITER006_DIR))
from stock_bond_blend import apply_blend_variance_target  # noqa: E402


# ---------------------------------------------------------------------------
# Pre-committed overlay configuration (see hypothesis.md § Pre-committed)
# ---------------------------------------------------------------------------

OVERLAY_CFG: dict = {
    "cfg_id": "ts_inv5_h50_eq",
    "indicator": "t10y3m_daily",
    "smoothing_window": 5,     # 5-day EMA — preserves 6-18m lead
    "threshold": 0.0,          # classical yield-curve inversion
    "haircut": 0.5,            # tier-2 half-exposure [systematic_trading p.144]
    "applied_to": "equity",    # SPY leg only — bond leg retains full weight
    "lag_bars": 1,             # no look-ahead [advances_fin_ml p.162-164]
}


# ---------------------------------------------------------------------------
# T10Y3M loading / smoothing
# ---------------------------------------------------------------------------


def load_term_spread_daily(
    t10y3m_path: Path,
    align_index: pd.DatetimeIndex,
    *,
    smoothing_window: int = 5,
    lag_bars: int = 1,
) -> pd.Series:
    """Load T10Y3M, reindex onto equity calendar, lag, then EMA-smooth.

    The lag is applied **before** smoothing so the smoothed value at bar
    ``t`` is a function only of bars ``[t - span, t - 1]`` — strict
    no-lookahead.
    """
    df = pd.read_parquet(t10y3m_path)
    if "term_spread" not in df.columns:
        raise ValueError(
            f"expected 'term_spread' col in {t10y3m_path}, "
            f"got {df.columns.tolist()}"
        )
    ts_raw = df["term_spread"].astype(float)
    ts_on_eq = ts_raw.reindex(align_index, method="ffill")
    ts_lagged = ts_on_eq.shift(lag_bars)
    ts_ema = ts_lagged.ewm(span=smoothing_window, adjust=False).mean()
    ts_ema.name = f"t10y3m_ema{smoothing_window}_lag{lag_bars}"
    return ts_ema


def compute_gate_series(
    ts_ema_lagged: pd.Series,
    *,
    threshold: float = 0.0,
    haircut: float = 0.5,
) -> pd.Series:
    """Binary gate: haircut if signal ≤ threshold else 1.0 (NaN → 1.0)."""
    gate = pd.Series(1.0, index=ts_ema_lagged.index, dtype=float)
    gate.loc[ts_ema_lagged <= threshold] = haircut
    gate.loc[ts_ema_lagged.isna()] = 1.0
    gate.name = "gate"
    return gate


# ---------------------------------------------------------------------------
# Asymmetric overlay — equity leg only
# ---------------------------------------------------------------------------


def apply_blend_with_asymmetric_overlay(
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
    """Blend + asymmetric equity-only haircut.

    Returns (net, pos_spy_gated, pos_tlt_UNGATED, scale, gate).

    The haircut is applied ONLY to ``pos_spy``; ``pos_tlt`` keeps the
    un-gated weight from the base blend — this is the entire structural
    distinction vs iter 009.
    """
    # Un-gated blend gives (pos_spy_base, pos_tlt_base, scale).
    _, pos_spy_base, pos_tlt_base, scale = apply_blend_variance_target(
        r_spy, r_tlt,
        target_vol=target_vol,
        lookback=lookback,
        max_leverage=max_leverage,
        periods_per_year=periods_per_year,
        cost_bps_per_leg=cost_bps_per_leg,
    )

    ts_valid = ts_ema_lagged.reindex(scale.index)
    gate = pd.Series(1.0, index=scale.index, dtype=float)
    gate.loc[ts_valid <= threshold] = haircut
    gate.loc[ts_valid.isna()] = 1.0

    # ASYMMETRIC: only SPY leg is haircut; TLT leg unchanged.
    pos_spy_g = pos_spy_base * gate
    pos_tlt_g = pos_tlt_base  # no haircut

    r_spy_valid = r_spy.loc[scale.index].astype(float)
    r_tlt_valid = r_tlt.loc[scale.index].astype(float)
    gross = pos_spy_g * r_spy_valid + pos_tlt_g * r_tlt_valid

    dpos_spy = pos_spy_g.diff().abs().fillna(pos_spy_g.iloc[0])
    dpos_tlt = pos_tlt_g.diff().abs().fillna(pos_tlt_g.iloc[0])
    cost = (dpos_spy + dpos_tlt) * cost_bps_per_leg
    net = (gross - cost).astype(float)

    net.name = "net"
    pos_spy_g.name = "pos_spy_gated"
    pos_tlt_g.name = "pos_tlt_ungated"
    gate.name = "gate"
    return net, pos_spy_g, pos_tlt_g, scale, gate


__all__ = [
    "OVERLAY_CFG",
    "apply_blend_with_asymmetric_overlay",
    "compute_gate_series",
    "load_term_spread_daily",
]
