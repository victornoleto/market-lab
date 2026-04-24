"""Iter 014 — EBP (Excess Bond Premium) credit-cycle overlay on iter 008 blend.

Applies a single pre-committed binary-haircut gate on the **equity leg
only** of iter 008's vol-managed SPY+TLT blend, driven by the rolling
z-score of the Gilchrist-Zakrajšek (2012) Excess Bond Premium.

Structural distinctions vs iter 009/012/013 (all closed — vol-proxy
cointegration):

* EBP is the **residual** of corporate bond spreads AFTER stripping
  expected defaults (GZ2012 decomposition). It captures investor
  risk-appetite changes, not equity realised vol.
* Mandatory pre-validation gate (see ``pre_validation.py``) measures
  |ρ(EBP_z, σ²_port)| over 60d rolling windows. If fraction of bars
  with |ρ| > 0.30 exceeds 20 % on any dataset, iteration aborts BEFORE
  running the full backtest — avoids spending DSR budget on a signal
  that shares the same cointegration failure mode as iter 009/012/013.

Pipeline (at each bar ``t``, if pre-validation passed):

    1. Run iter 006 blend → un-gated (s_t, w_spy_t, w_tlt_t).
    2. ebp_z_t = rolling-252 z-score of EBP, already lagged 1 bar.
    3. gate_t  = 0.5 if ebp_z_{t-1} ≥ threshold (1.0) else 1.0.
    4. pos_spy_t = s_t · w_spy_t · gate_t   (asymmetric — SPY only)
       pos_tlt_t = s_t · w_tlt_t            (bond leg unchanged)
    5. gross_t  = pos_spy_t · r_spy[t] + pos_tlt_t · r_tlt[t]
    6. cost_t   = (|Δpos_spy| + |Δpos_tlt|) · cost_bps_per_leg
    7. net_t    = gross_t − cost_t

Citations
---------
* `[adaptive_markets, p.131-132, ch.11]` — Lo's credit cycle as distinct
  axis; countercyclical capital buffers concept motivates credit-signal
  overlays on market portfolios.
* `[adaptive_markets, p.244-246, ch.7]` — 1998 LTCM fixed-income-arb
  attrition (18 % vs 9 % baseline) — canonical pure credit-event that
  preceded equity stress.
* `[risk_parity, p.23-24, ch.2]` — HY bonds co-move with equity at the
  Sharpe level; motivates using EBP (the *residual*), not raw HY spread.
* `[systematic_trading, p.144, ch.9]` — tier-2 half-exposure haircut.
* `[advances_fin_ml, p.162-164]` — `σ̂_{t-1}` lag (no look-ahead),
  extended to macro monthly EBP aligned to daily bars.
* Gilchrist & Zakrajšek (2012), *AER* 102(4), 1692-1720. DOI
  10.1257/aer.102.4.1692 — EBP decomposition + business-cycle
  forecasting power.
"""

from __future__ import annotations

from pathlib import Path
import sys

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
    "cfg_id": "ebp_z252_t100_h50_eq",
    "indicator": "ebp_monthly",
    "zscore_window": 252,      # 1y trailing stability baseline
    "threshold": 1.0,          # z ≥ 1.0 upper-tail credit stress
    "haircut": 0.5,            # tier-2 half-exposure [systematic_trading p.144]
    "applied_to": "equity",    # SPY leg only (bond flight-to-quality preserved)
    "lag_bars": 1,             # no look-ahead [advances_fin_ml p.162-164]
    "align_method": "month_forward_fill",
}


# ---------------------------------------------------------------------------
# EBP alignment + lag
# ---------------------------------------------------------------------------


def load_ebp_daily(
    ebp_path: Path,
    align_index: pd.DatetimeIndex,
    *,
    lag_bars: int = 1,
    column: str = "ebp",
) -> pd.Series:
    """Load monthly EBP, forward-fill to daily index, then lag.

    Monthly series contains one observation per month (GZ2012 convention:
    value indexed at month-start). Forward-fill carries each month's
    value through all daily bars in that month until the next month's
    value becomes known. Then shift by ``lag_bars`` to guarantee no bar
    sees the current month's value before it is realistically
    "published" (GZ2012 estimate is typically available with ~1-month
    delay; 1-bar daily shift is a conservative minimum).
    """
    df = pd.read_parquet(ebp_path)
    if column not in df.columns:
        raise ValueError(
            f"expected '{column}' col in {ebp_path}, got {df.columns.tolist()}"
        )
    s = df[column].astype(float)
    # Forward-fill to daily calendar — each month's value holds through
    # until the next month-start observation lands in ``align_index``.
    s_on_eq = s.reindex(align_index, method="ffill")
    if lag_bars > 0:
        s_on_eq = s_on_eq.shift(lag_bars)
    s_on_eq.name = f"{column}_ffill_lag{lag_bars}"
    return s_on_eq


# ---------------------------------------------------------------------------
# Z-score
# ---------------------------------------------------------------------------


def compute_ebp_zscore(
    ebp_daily: pd.Series,
    *,
    window: int = 252,
) -> pd.Series:
    """Rolling trailing-window z-score of the EBP series.

    At bar ``t``, z uses bars ``[t-window+1, t]`` (inclusive) — i.e. the
    window ending at ``t`` itself. Since the INPUT series is already
    lagged (see ``load_ebp_daily``), this is still strict no-lookahead:
    bar ``t``'s value is a lagged month-value, so including it in the
    window does not leak future.
    """
    if window < 2:
        raise ValueError(f"window must be ≥ 2, got {window}")
    roll = ebp_daily.rolling(window, min_periods=window)
    mu = roll.mean()
    sigma = roll.std(ddof=0)
    z = (ebp_daily - mu) / sigma.where(sigma > 0)
    z.name = "ebp_z"
    return z


# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------


def compute_gate_series(
    ebp_z: pd.Series,
    *,
    threshold: float = 1.0,
    haircut: float = 0.5,
) -> pd.Series:
    """Binary gate — haircut when z ≥ threshold (upper-tail stress)."""
    gate = pd.Series(1.0, index=ebp_z.index, dtype=float)
    gate.loc[ebp_z >= threshold] = haircut
    gate.loc[ebp_z.isna()] = 1.0
    gate.name = "gate"
    return gate


# ---------------------------------------------------------------------------
# Asymmetric blend + credit overlay
# ---------------------------------------------------------------------------


def apply_blend_with_credit_overlay(
    r_spy: pd.Series,
    r_tlt: pd.Series,
    *,
    ebp_z_lagged: pd.Series,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    threshold: float,
    haircut: float,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """Blend + EBP credit overlay. Returns (net, pos_spy_g, pos_tlt, scale, gate).

    Asymmetric: only the SPY leg is haircut. Bond leg keeps un-gated
    weight (preserves flight-to-quality). Costs are recomputed on the
    gated positions.
    """
    _, pos_spy_base, pos_tlt_base, scale = apply_blend_variance_target(
        r_spy, r_tlt,
        target_vol=target_vol,
        lookback=lookback,
        max_leverage=max_leverage,
        periods_per_year=periods_per_year,
        cost_bps_per_leg=cost_bps_per_leg,
    )

    z_valid = ebp_z_lagged.reindex(scale.index)
    gate = pd.Series(1.0, index=scale.index, dtype=float)
    gate.loc[z_valid >= threshold] = haircut
    gate.loc[z_valid.isna()] = 1.0

    pos_spy_g = pos_spy_base * gate
    pos_tlt_g = pos_tlt_base  # bond leg unchanged

    r_spy_v = r_spy.loc[scale.index].astype(float)
    r_tlt_v = r_tlt.loc[scale.index].astype(float)
    gross = pos_spy_g * r_spy_v + pos_tlt_g * r_tlt_v

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
    "apply_blend_with_credit_overlay",
    "compute_ebp_zscore",
    "compute_gate_series",
    "load_ebp_daily",
]
