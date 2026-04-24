"""Iter 007 — Time-series momentum overlay on vol-managed SPY+TLT blend.

Wraps iter 006's ``apply_blend_variance_target`` with a binary
momentum gate on an equity price signal. When the canonical 12-1
(skip-a-month) momentum is positive, deploy the full blend; otherwise
hold cash.

Formulation (at bar ``t``):

    mom_t = price_t_minus_skip / price_t_minus_skip_minus_lookback - 1
    gate_t = 1 if mom_t > 0 else 0

    # Lag gate by one additional bar (same convention as σ̂_{t-1} in
    # iter 006 — no look-ahead on decision at bar t):
    gate_eff_t = gate_{t-1}

    scale_eff_t = scale_blend_t * gate_eff_t
    pos_spy_t   = scale_eff_t * w_spy_t
    pos_tlt_t   = scale_eff_t * w_tlt_t

    gross_t     = pos_spy_t * r_spy_t + pos_tlt_t * r_tlt_t
    cost_t      = (|Δpos_spy| + |Δpos_tlt|) * cost_bps_per_leg
    net_t       = gross_t - cost_t

The momentum ``mom_t`` uses the ``price_signal`` passed in — typically
the equity leg's adjusted-close price series. Skip-a-month (`skip=21`)
is the canonical protocol from
``[ml_for_algo_trading, ch.4 p.86]``.

Citations
---------
* ``[ml_for_algo_trading, ch.4 p.86]`` — 12-month return excluding most
  recent month.
* ``[algo_trading_chan, p.133, 164, ch.6]`` — time-series momentum;
  lookback=252 per Moskowitz-Ooi-Pedersen (2012).
* ``[advances_fin_ml, p.162-164]`` — signal lag / no look-ahead.
* Iter 006 ``stock_bond_blend.py`` — base blend mechanism.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

_ITER_006_DIR = (
    Path(__file__).resolve().parents[1]
    / "006-2026-04-24-1027-vol-managed-60-40"
)
sys.path.insert(0, str(_ITER_006_DIR))

from stock_bond_blend import apply_blend_variance_target  # noqa: E402


def time_series_momentum_gate(
    prices: pd.Series,
    *,
    lookback: int,
    skip: int,
) -> pd.Series:
    """Binary momentum gate on a price series (skip-a-month protocol).

    At bar ``t``, the raw signal is ``mom_t = price_{t-skip} /
    price_{t-skip-lookback} - 1``. The gate is ``1`` iff ``mom_t > 0``.

    Parameters
    ----------
    prices : pd.Series
        Price series (adjusted close). Index is assumed monotonic.
    lookback : int
        Momentum return window in bars (e.g., 252 for 12-month).
    skip : int
        Number of most-recent bars to exclude (e.g., 21 for 1-month
        skip). Passing ``skip=0`` gives absolute momentum without skip.

    Returns
    -------
    pd.Series
        {0, 1}-valued gate aligned with ``prices.index``. The first
        ``lookback + skip`` bars are NaN (insufficient history).

    Raises
    ------
    ValueError
        If the series has fewer than ``lookback + skip + 1`` bars.
    """
    if lookback < 1:
        raise ValueError(f"lookback must be ≥ 1, got {lookback}")
    if skip < 0:
        raise ValueError(f"skip must be ≥ 0, got {skip}")
    warmup = lookback + skip
    if len(prices) <= warmup:
        raise ValueError(
            f"need > {warmup} bars (lookback + skip), got {len(prices)}"
        )

    p = prices.astype(float)
    # Shift by `skip` to get price at t-skip; divide by price at
    # t-skip-lookback (an additional `lookback` shift).
    price_skip = p.shift(skip)
    price_skip_back = p.shift(skip + lookback)
    mom = (price_skip / price_skip_back) - 1.0
    gate = (mom > 0).astype(float)
    # Mask warmup bars as NaN (no signal yet).
    gate.iloc[:warmup] = np.nan
    gate.name = "gate"
    return gate


def apply_blend_with_momentum_overlay(
    r_eq: pd.Series,
    r_bd: pd.Series,
    price_signal: pd.Series,
    *,
    blend_cfg: dict,
    overlay_cfg: dict,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """Apply time-series momentum gate to the vol-managed blend.

    Parameters
    ----------
    r_eq, r_bd : pd.Series
        Equity and bond daily return streams. Must share index.
    price_signal : pd.Series
        Price path used for the momentum gate (typically equity leg
        adjusted close). Must share index with the returns.
    blend_cfg : dict
        Passed to ``apply_blend_variance_target`` — ``target_vol``,
        ``lookback``, ``max_leverage``.
    overlay_cfg : dict
        ``lookback`` and ``skip`` for the momentum gate.
    periods_per_year, cost_bps_per_leg : see base blend.

    Returns
    -------
    (net, pos_eq, pos_bd, scale, gate)
        Net returns, per-leg positions, effective scale (after gate),
        gate series — all aligned on the intersection index.
    """
    if not r_eq.index.equals(r_bd.index):
        raise ValueError(
            "r_eq and r_bd must share the same index "
            f"(eq {r_eq.index[0]}→{r_eq.index[-1]} vs "
            f"bd {r_bd.index[0]}→{r_bd.index[-1]})"
        )
    if not price_signal.index.equals(r_eq.index):
        raise ValueError(
            "price_signal must align with r_eq/r_bd index "
            f"(signal {price_signal.index[0]}→{price_signal.index[-1]} vs "
            f"returns {r_eq.index[0]}→{r_eq.index[-1]})"
        )

    # Compute base blend without cost adjustment so we can recompute
    # costs *after* the overlay multiplies through the scale — otherwise
    # cost is computed on the pre-overlay position sequence, which is
    # wrong when the gate flips.
    # Strategy: call base blend with zero cost, get base positions;
    # multiply by lagged gate; recompute cost on the overlaid positions.
    net_base, pos_eq_base, pos_bd_base, scale_base = apply_blend_variance_target(
        r_eq, r_bd,
        target_vol=blend_cfg["target_vol"],
        lookback=blend_cfg["lookback"],
        max_leverage=blend_cfg["max_leverage"],
        periods_per_year=periods_per_year,
        cost_bps_per_leg=0.0,
    )

    gate = time_series_momentum_gate(
        price_signal,
        lookback=overlay_cfg["lookback"],
        skip=overlay_cfg["skip"],
    )

    # Lag the gate by one bar so decision at bar t uses only signal
    # computed from prices up to t-skip (additional 1-bar shift makes
    # the gate strictly causal wrt returns at bar t).
    gate_eff = gate.shift(1)

    # Restrict to overlap of blend output and gate-effective index.
    common_idx = scale_base.index.intersection(gate_eff.dropna().index)
    if len(common_idx) == 0:
        raise ValueError(
            "overlay warmup + blend warmup consume entire series — "
            "increase history or shorten lookbacks"
        )

    gate_v = gate_eff.loc[common_idx].astype(float)
    scale_ov = scale_base.loc[common_idx] * gate_v
    pos_eq = pos_eq_base.loc[common_idx] * gate_v
    pos_bd = pos_bd_base.loc[common_idx] * gate_v

    r_eq_v = r_eq.loc[common_idx].astype(float)
    r_bd_v = r_bd.loc[common_idx].astype(float)
    gross = pos_eq * r_eq_v + pos_bd * r_bd_v

    # Recompute cost on overlaid positions. Initial-bar cost = |pos[0]|
    # (opening the position from flat).
    dpos_eq = pos_eq.diff().abs()
    dpos_bd = pos_bd.diff().abs()
    dpos_eq.iloc[0] = abs(float(pos_eq.iloc[0]))
    dpos_bd.iloc[0] = abs(float(pos_bd.iloc[0]))
    cost = (dpos_eq + dpos_bd) * cost_bps_per_leg
    net = (gross - cost).astype(float)

    net.name = "net"
    pos_eq.name = "pos_eq"
    pos_bd.name = "pos_bd"
    scale_ov.name = "scale"
    gate_eff.name = "gate"
    return net, pos_eq, pos_bd, scale_ov, gate_eff
