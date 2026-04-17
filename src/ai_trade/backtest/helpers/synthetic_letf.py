"""Synthetic leveraged ETF returns — pre-UPRO/SSO backtest helper.

UPRO (3x SPY) launched 2009-06; SSO (2x SPY) launched 2006-06. For the
Phase 3 Lead B1 grid (LETF rotation) the IS split is 1970-2000, so we
synthesize daily leveraged returns from the underlying index using the
formula prescribed by Gayed:

    r_synth[t] = L * r_SPX_TR[t] - annual_fee / 252

where ``L`` is the leverage factor (1.25, 2, 3), ``r_SPX_TR`` is the
daily total-return of the S&P 500 (with dividends reinvested), and
``annual_fee`` is the ETF expense ratio + borrowing drag. Gayed uses
1% per year for pre-2021 modelling and 0.95% for post-2021, to match
the actual UPRO expense ratio (0.95% as of 2021).

Citations
---------

* Synthetic leveraged return formula, daily drag applied as
  ``fee / 252``: ``[leverage_for_the_long_run, p.16]`` (footnote 22).
* Expense-ratio assumption 1% / 0.95%:
  ``[leverage_for_the_long_run, p.16]`` (footnote 23).
* Daily re-leveraging compounding mechanism:
  ``[leverage_for_the_long_run, p.4]`` (core thesis).

Notes
-----

The formula assumes perfect daily re-leveraging and ignores the
"negative leverage premium" (performance lag) observed empirically
vs UPRO/SSO; Gayed quantifies the gap at roughly 2-3% annual for the
3x LRS (26.3% theoretical vs 24.2% UPRO-implemented over 2009-2020,
see p.21, Table 12). For Phase 3 we report both theoretical and
ETF-lag-adjusted results at the end-of-grid stage; this helper is
the theoretical half.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = [
    "DEFAULT_ANNUAL_FEE",
    "TRADING_DAYS_PER_YEAR",
    "synthesize_letf_returns",
    "synthesize_letf_prices",
]


TRADING_DAYS_PER_YEAR = 252
"""Gayed uses 252 trading days; aligned across all Phase 3 compounding."""

DEFAULT_ANNUAL_FEE = 0.01
"""1% pre-2021 (UPRO expense ratio + borrowing drag as cited). Use 0.0095
for post-2021 fidelity; caller must pass explicitly."""


def synthesize_letf_returns(
    spx_tr_returns: pd.Series,
    leverage: float,
    annual_fee: float = DEFAULT_ANNUAL_FEE,
) -> pd.Series:
    """Daily synthetic LETF returns from SPX total-return series.

    Implements ``r_synth[t] = L * r_SPX_TR[t] - annual_fee / 252`` per
    ``[leverage_for_the_long_run, p.16]``.

    Parameters
    ----------
    spx_tr_returns : pd.Series
        Daily total-return of S&P 500 (with dividends). Index must be
        datetime-like. Values as decimal (e.g. 0.01 for +1%).
    leverage : float
        Leverage factor. Typical values 1.0, 1.25, 2.0, 3.0. Must be
        positive.
    annual_fee : float
        Annualized expense ratio / borrowing cost. Applied as
        ``fee / 252`` per trading day. Default 1% per Gayed p.16.

    Returns
    -------
    pd.Series
        Synthetic daily leveraged returns, same index as input.

    Raises
    ------
    ValueError
        If ``leverage`` is not positive.
    """
    if leverage <= 0:
        raise ValueError(f"leverage must be > 0, got {leverage}")

    daily_drag = annual_fee / TRADING_DAYS_PER_YEAR
    return leverage * spx_tr_returns - daily_drag


def synthesize_letf_prices(
    spx_tr_returns: pd.Series,
    leverage: float,
    annual_fee: float = DEFAULT_ANNUAL_FEE,
    start_value: float = 100.0,
) -> pd.Series:
    """Cumulative price series of synthetic LETF starting at ``start_value``.

    Convenience wrapper — compounds :func:`synthesize_letf_returns`
    into a price path. Useful when a strategy needs a "fake"
    close-price series to reuse SMA/EMA logic designed for prices.

    Parameters
    ----------
    spx_tr_returns : pd.Series
        Daily total-return series. Must not contain NaN in the first
        value; NaN values elsewhere are treated as 0 (no price change
        that day) to keep the path continuous.
    leverage : float
        Leverage factor. See :func:`synthesize_letf_returns`.
    annual_fee : float
        Annual fee drag. See :func:`synthesize_letf_returns`.
    start_value : float
        Starting price. Default 100.0.

    Returns
    -------
    pd.Series
        Cumulative price path, same index as input.
    """
    synth_rets = synthesize_letf_returns(
        spx_tr_returns, leverage, annual_fee
    ).fillna(0.0)
    cumulative = (1.0 + synth_rets).cumprod() * start_value
    return cumulative.astype(float)
