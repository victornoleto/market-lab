"""Tax layer — wrapper over studies/_shared/tax_engine.py for LETF rotation.

Two modes per spec §4.4:
  - `annual_realize`: rotation strategies (T1+) — 15% DARF on annual gains
  - `buy_hold_terminal`: passive holds — defer DARF to terminal liquidation

Both modes use Lei 14.754/2023 (15% flat, loss carry-forward indefinido).

Citations:
  - Lei 14.754/2023 brasileira (vigente Jan/2024)
  - studies/_shared/tax_engine.py:AnnualDarfEngine
"""
from __future__ import annotations

import numpy as np
import pandas as pd

DARF_RATE = 0.15


def apply_annual_darf(
    gross_equity: pd.Series,
    returns: pd.Series,
    mode: str = "annual_realize",
    initial: float | None = None,
) -> pd.Series:
    """Apply Lei 14.754 DARF to gross equity curve.

    Parameters
    ----------
    gross_equity : pd.Series
        Gross-of-tax equity curve. Note: gross_equity.iloc[0] is the equity
        AFTER the first bar's return, not the starting capital.
    returns : pd.Series
        Daily returns matched to gross_equity. Used together with `initial`
        to determine starting capital correctly.
    mode : str
        - "annual_realize": tax 15% on annual gains (rotation/swing)
        - "buy_hold_terminal": defer to terminal liquidation (passive)
    initial : float, optional
        Starting capital (before any returns). If None, inferred as
        gross_equity.iloc[0] / (1 + returns.iloc[0]).

    Returns
    -------
    pd.Series
        Net-of-tax equity curve.
    """
    if initial is None:
        if returns is None or len(returns) == 0:
            raise ValueError("Cannot infer initial without returns")
        initial = float(gross_equity.iloc[0]) / (1.0 + float(returns.iloc[0]))

    if mode == "buy_hold_terminal":
        return _apply_terminal_darf(gross_equity, initial)
    elif mode == "annual_realize":
        return _apply_annual_darf(gross_equity, initial)
    else:
        raise ValueError(
            f"Unknown mode: {mode}. Use 'annual_realize' or 'buy_hold_terminal'."
        )


def _apply_terminal_darf(gross_equity: pd.Series, initial: float) -> pd.Series:
    """Defer DARF until last bar; apply 15% on net gain.

    All bars except the terminal one are unchanged (zero intra-year tax).
    The terminal bar gets: (1 - DARF_RATE) * gross_final + DARF_RATE * initial
    i.e. gross gain is reduced by 15%, leaving 85% of the gain.
    """
    net = gross_equity.copy()
    final_gross = gross_equity.iloc[-1]
    # Tax 15% on (final - initial); if loss, no tax owed
    if final_gross > initial:
        net.iloc[-1] = (1 - DARF_RATE) * final_gross + DARF_RATE * initial
    return net


def _apply_annual_darf(gross_equity: pd.Series, initial: float) -> pd.Series:
    """Apply 15% DARF on yearly realized gains; carry losses forward.

    Within each calendar year, the net equity tracks the gross growth ratio
    applied to the prior year-end net equity. At the last bar of each year
    the DARF liability is deducted, anchoring the following year's base.

    Loss carry-forward is indefinite per Lei 14.754/2023.

    For the first calendar year, `initial` is used as the true day-0 base
    (before any returns), ensuring day-0's return is included in the taxable
    gain for that year.
    """
    net_equity = gross_equity.copy().astype(float)
    carry_forward_loss = 0.0  # accumulated tax-deductible loss (always >= 0 in magnitude)

    gross_arr = gross_equity.values.astype(float)
    years = np.array(gross_equity.index.year)

    unique_years = sorted(set(years))
    for year in unique_years:
        year_idx = np.where(years == year)[0]
        if len(year_idx) == 0:
            continue
        start_idx = year_idx[0]
        end_idx = year_idx[-1]

        # Base equity at start of year (prior bar's net, or initial for first year)
        if start_idx == 0:
            start_net = initial  # use true starting capital, not gross_equity.iloc[0]
            gross_base = initial
        else:
            start_net = float(net_equity.iloc[start_idx - 1])
            gross_base = gross_arr[start_idx - 1]

        # Compute intra-year net equity as start_net × (gross[i] / gross_base)
        # This preserves daily compounding shape while rebasing to the net anchor.
        # Vectorized for performance.
        if gross_base > 0:
            ratios = gross_arr[start_idx:end_idx + 1] / gross_base
            net_equity.iloc[start_idx:end_idx + 1] = start_net * ratios
        # If gross_base == 0 (degenerate), leave as-is

        # Year-end: compute gain and apply DARF
        end_net_pretax = float(net_equity.iloc[end_idx])
        gain = end_net_pretax - start_net

        taxable_gain = gain - carry_forward_loss
        if taxable_gain > 0:
            tax = DARF_RATE * taxable_gain
            carry_forward_loss = 0.0
        else:
            tax = 0.0
            carry_forward_loss = -taxable_gain  # accumulate the unused loss

        # Deduct tax at year-end bar only
        net_equity.iloc[end_idx] = end_net_pretax - tax

    return net_equity
