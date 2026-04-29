"""TDD tests for studies.long_term_portfolio.synths.

Each synth function gets:
- a smoke test (returns non-empty Series with DatetimeIndex)
- a formula test (sample input -> sample output with known math)
- where applicable, a no-free-lunch sanity test (Sharpe should not be implausibly inflated)
"""
import numpy as np
import pandas as pd
import pytest

from studies.long_term_portfolio.synths import _annual_drag_to_daily


def test_annual_drag_to_daily_75bps():
    """75bps/y annual drag = 75/(252*10000) decimal/day."""
    result = _annual_drag_to_daily(0.0075)
    assert abs(result - 0.0000297619) < 1e-8
