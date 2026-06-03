"""TDD tests for studies.return_stacked_core.run_iter."""
import pandas as pd
import pytest

from studies.return_stacked_core.run_iter import portfolio_returns_from_config


def test_portfolio_returns_from_simple_config():
    """50% SPYSIM + 50% IEFSIM should return a Series with valid date range for lh_56y."""
    config = {"SPYSIM": 0.50, "IEFSIM": 0.50}
    returns = portfolio_returns_from_config(config, dataset="lh_56y")
    assert isinstance(returns, pd.Series)
    assert len(returns) > 9000  # 40y x 252


def test_portfolio_returns_weights_must_sum_to_1():
    """Configs must sum to ~1.0 (notional > 1 is fine via stacking ETFs)."""
    with pytest.raises(ValueError, match="weights"):
        portfolio_returns_from_config({"SPYSIM": 0.30, "IEFSIM": 0.30}, dataset="lh_56y")


def test_portfolio_returns_with_synth_ticker():
    """Config can reference NTSXSIM (synth) and resolve via proxies.py."""
    config = {"NTSXSIM": 1.0}
    returns = portfolio_returns_from_config(config, dataset="lh_56y")
    assert len(returns) > 9000
