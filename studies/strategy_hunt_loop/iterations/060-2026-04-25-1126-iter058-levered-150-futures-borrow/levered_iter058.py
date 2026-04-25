"""Iter 060 — 1.5× external leverage on iter 058 saved stream at 2.5% borrow.

Pure-leverage transform on iter 058's TOP-K #1 saved combined stream
(iter 046 + HYG_TSM at w=0.10), applied at futures-implied financing
rate (2.5% = T-bill 2.0% + 0.5% Treasury futures roll cost) instead of
iter 056's 3.5% retail Reg-T margin.

Mechanics::

    daily_borrow = (1 + borrow_rate_annual) ** (1 / 252) - 1
    r_lev[t] = lev * r_058[t] - (lev - 1) * daily_borrow

Linear transform — no per-bar regime conditioning, no perturbation of
iter 058's combined stream. ``lev = 1.0`` returns iter 058 net unchanged.
``borrow_rate_annual = rf`` preserves Sharpe exactly (zero spread → zero
drag).

Citations
---------
* `[leverage_for_the_long_run, ch.5]` — Hsiao-Williams 2017 NTSX
  architecture: Treasury-futures financing achieves leverage at
  T-bill + 30-50bps instead of retail Reg-T spread (T-bill + 150bps).
* `[risk_parity, ch.5]` — iter 058 base architecture inherited verbatim
  via saved daily return stream.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
* Frazzini-Pedersen (2014), JFE 111(1) 1-25, DOI 10.1016/j.jfineco.2013.10.005 —
  borrow frictions on levered low-vol strategies. Iter 056 vindicated
  empirically at 3.5% retail spread; this iteration probes the 2.5%
  futures-implied analog.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

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

    ``(1 + borrow_rate_annual) ** (1 / 252) - 1``. For 2.5% annual this
    is ≈ 9.81e-5 per bar (vs iter 056's 1.367e-4 at 3.5%).
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
        Daily simple net returns of the underlying strategy (iter 058's
        combined stream loaded from its saved JSON).
    lev : float
        Leverage multiplier. Must be ``> 0``. ``lev = 1.0`` is identity.
    borrow_rate_annual : float
        Annualized borrow rate (e.g. 0.025 for 2.5%). Must be ``>= 0``.

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
    levered.name = (
        returns.name + "_levered" if returns.name else "levered_return"
    )
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


__all__ = [
    "apply_leverage_pd",
    "apply_leverage_np",
    "daily_borrow_from_annual",
]
