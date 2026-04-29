"""Synthetic ETF returns for the long-term portfolio sweep iter 027-039.

All synths return pd.Series of daily returns (decimal, e.g. 0.0123 = +1.23%).
Each function citation links to a book or paper that justifies the formula.
INCOMPLETE flag in docstring means the synth makes simplifying assumptions
that should be disclosed in any iter's final_report.md.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.ai_trade.backtest.data.testfolio_loader import (
    load_testfolio_frame,
    load_testfolio_series,
)

TRADING_DAYS_PER_YEAR = 252


def _annual_drag_to_daily(annual_drag_decimal: float) -> float:
    """Convert annual drag in decimal form to daily multiplicative drag.

    e.g. 75bps/y = 0.0075 -> 0.0075 / 252 ~= 2.98e-5 daily.
    """
    return annual_drag_decimal / TRADING_DAYS_PER_YEAR
