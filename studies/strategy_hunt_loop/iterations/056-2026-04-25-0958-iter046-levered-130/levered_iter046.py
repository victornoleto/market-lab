"""Iter 056 — 1.3× external leverage on iter 046 combined stream with retail borrow.

Pure-leverage transform on iter 046's TOP-K #1 50/50 convex combo
(iter 041 regime stack + iter 039 VRP basket). No perturbation of
sub-strategy params — only ``lev`` and ``borrow_rate_annual`` are new.

Mechanics::

    daily_borrow = (1 + borrow_rate_annual) ** (1 / 252) - 1
    r_lev[t] = lev * r_046[t] - (lev - 1) * daily_borrow

This represents borrowing ``(lev - 1)`` units of equity at the annual
broker margin rate to deploy a total of ``lev`` units of capital into
the iter 046 strategy. Sharpe is preserved modulo a small spread drag
``(lev - 1) * (rf_borrow - rf) / (lev * sigma)``; CAGR scales by
``lev`` minus geometric drag ``lev * (lev - 1) * sigma^2 / 2`` minus
the borrow cost ``(lev - 1) * borrow``.

Reductions (proven in TDD):

* ``lev = 1.0`` → returns iter 046 net unchanged (independent of borrow).
* ``lev = 2.0`` with ``borrow_rate_annual = 0`` → exactly ``2 * r_046``.
* Borrow cost subtracted is independent of the per-bar return (constant
  daily drag per bar) — it does NOT compound through the strategy's
  regime gates.

Citations
---------
* `[risk_parity, ch.5]` — iter 046 base architecture inherited verbatim.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
* Frazzini-Pedersen (2014), JFE 111(1) 1-25, DOI 10.1016/j.jfineco.2013.10.005 —
  margin/borrow frictions on levered low-vol strategies (justifies
  modeling the spread vs assuming risk-free borrow).
* IBKR Pro Tier 1 margin schedule (public) — 3.5% effective borrow rate
  at 2025 yields = T-bill 2.0% + 1.5% institutional spread.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_046_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "046-2026-04-25-0553-iter039-overlay-on-iter041"
if str(ITER_046_DIR) not in sys.path:
    sys.path.append(str(ITER_046_DIR))

from combined_041_039 import compute_combined_returns  # noqa: E402

DAYS_PER_YEAR = 252


def _validate_leverage_inputs(lev: float, borrow_rate_annual: float) -> None:
    if lev <= 0:
        raise ValueError(f"lev must be > 0; got {lev}")
    if borrow_rate_annual < 0:
        raise ValueError(
            f"borrow_rate_annual must be >= 0; got {borrow_rate_annual}"
        )


def daily_borrow_from_annual(borrow_rate_annual: float) -> float:
    """Convert annual borrow rate to daily compounded equivalent.

    ``(1 + borrow_rate_annual) ** (1 / 252) - 1``. For 3.5% annual this
    is ≈ 1.367e-4 per bar.
    """
    if borrow_rate_annual < 0:
        raise ValueError(
            f"borrow_rate_annual must be >= 0; got {borrow_rate_annual}"
        )
    return (1.0 + borrow_rate_annual) ** (1.0 / DAYS_PER_YEAR) - 1.0


def apply_leverage_pd(
    returns: pd.Series,
    *,
    lev: float,
    borrow_rate_annual: float,
) -> pd.Series:
    """Pandas leverage transform: r_lev = lev * r - (lev-1) * daily_borrow.

    Parameters
    ----------
    returns : pd.Series
        Daily simple net returns of the underlying strategy.
    lev : float
        Leverage multiplier. Must be ``> 0``. ``lev = 1.0`` is identity.
    borrow_rate_annual : float
        Annualized borrow rate (e.g. 0.035 for 3.5%). Must be ``>= 0``.
        Only the differential ``(lev - 1) * daily_borrow`` is subtracted;
        when ``lev == 1.0`` the borrow drag is zero by construction.

    Returns
    -------
    pd.Series
        Levered net returns on the same index as ``returns``.

    Raises
    ------
    ValueError
        If ``lev <= 0`` or ``borrow_rate_annual < 0``.
    """
    _validate_leverage_inputs(lev, borrow_rate_annual)
    daily_borrow = daily_borrow_from_annual(borrow_rate_annual)
    levered = lev * returns - (lev - 1.0) * daily_borrow
    levered.name = returns.name + "_levered" if returns.name else "levered_return"
    return levered


def apply_leverage_np(
    returns: np.ndarray,
    *,
    lev: float,
    borrow_rate_annual: float,
) -> np.ndarray:
    """Pure-numpy leverage transform; mirror of ``apply_leverage_pd``."""
    _validate_leverage_inputs(lev, borrow_rate_annual)
    daily_borrow = daily_borrow_from_annual(borrow_rate_annual)
    arr = np.asarray(returns, dtype=float)
    return lev * arr - (lev - 1.0) * daily_borrow


def compute_levered_returns(
    eq_prices: pd.Series,
    bd_prices: pd.Series,
    gld_prices: pd.Series,
    basket_prices: dict[str, pd.Series],
    iv_series: pd.Series,
    *,
    lev: float = 1.3,
    borrow_rate_annual: float = 0.035,
    # iter 046 sub-strategy params (forwarded verbatim)
    w_041: float = 0.5,
    w_039: float = 0.5,
    calm_weights: Mapping[str, float] | None = None,
    stress_weights: Mapping[str, float] | None = None,
    vix_threshold: float = 20.0,
    cost_bps_per_leg: float = 0.0002,
    rf: float = 0.02,
    harvest_notional: float = 1.0,
    weights: dict[str, float] | None = None,
    iv_scales: dict[str, float] | None = None,
    k_long_pct: float = 0.95,
    k_short_pct: float = 0.90,
    dte_days: int = 21,
    cost_bps_per_roll: float = 5.0,
) -> tuple[pd.Series, pd.Series]:
    """Compute the 1.3× levered iter 046 stream.

    Returns
    -------
    (r_levered, r_046) : tuple of pd.Series
        ``r_levered`` : leveraged net daily returns (post-borrow).
        ``r_046`` : underlying iter 046 combined return (for diagnostic
        / correlation analysis).
    """
    _validate_leverage_inputs(lev, borrow_rate_annual)
    r_046, _, _ = compute_combined_returns(
        eq_prices, bd_prices, gld_prices, basket_prices, iv_series,
        w_041=w_041, w_039=w_039,
        calm_weights=calm_weights, stress_weights=stress_weights,
        vix_threshold=vix_threshold,
        cost_bps_per_leg=cost_bps_per_leg,
        rf=rf, harvest_notional=harvest_notional,
        weights=weights, iv_scales=iv_scales,
        k_long_pct=k_long_pct, k_short_pct=k_short_pct,
        dte_days=dte_days, cost_bps_per_roll=cost_bps_per_roll,
    )
    r_levered = apply_leverage_pd(
        r_046, lev=lev, borrow_rate_annual=borrow_rate_annual,
    )
    r_levered.name = "iter056_levered_return"
    r_046.name = "iter046_underlying_return"
    return r_levered, r_046


__all__ = [
    "compute_levered_returns",
    "apply_leverage_pd",
    "apply_leverage_np",
    "daily_borrow_from_annual",
]
