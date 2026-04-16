"""Tests for the OU Mean-Reversion strategy.

Strategy rules from [algo_trading_chan, p.47-48, ch.2] and
[quant_trading_chan, p.140-142]:

1. Compute rolling z-score on log(close) over `lookback` bars.
2. Compute rolling ADF λ coefficient from regression Δlog(p) ~ log(p_{t-1}).
3. Long entry when z < −z_entry AND λ < 0 (mean-reversion confirmed).
4. Exit when z ≥ z_exit, or after max_hold bars, or stop-loss hit.

All tests use synthetic OHLCV; no network.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.ou_mean_rev import OUMeanRevStrategy


def _ohlcv_from_close(close: pd.Series, spread_bps: float = 1.0) -> pd.DataFrame:
    close = close.astype(float)
    half = close * spread_bps * 1e-4
    open_ = close.shift(1).fillna(close.iloc[0])
    return pd.DataFrame(
        {
            "open": open_,
            "high": close + half,
            "low": close - half,
            "close": close,
            "volume": 1_000_000.0,
        },
        index=close.index,
    )


def _sine_close(
    n: int = 1500,
    period: int = 40,
    amplitude: float = 5.0,
    baseline: float = 100.0,
    freq: str = "h",
) -> pd.Series:
    idx = pd.date_range("2021-01-01", periods=n, freq=freq)
    t = np.arange(n)
    return pd.Series(baseline + amplitude * np.sin(2 * np.pi * t / period), index=idx)


def _dip_and_recover(
    n_warmup: int = 100,
    n_dip: int = 10,
    n_recover: int = 50,
    baseline: float = 100.0,
    dip_depth: float = 8.0,
    freq: str = "h",
) -> pd.Series:
    """Flat → sharp dip → recover to baseline."""
    warmup = np.full(n_warmup, baseline)
    dip = np.linspace(baseline, baseline - dip_depth, n_dip)
    recover = np.linspace(baseline - dip_depth, baseline, n_recover)
    values = np.concatenate([warmup, dip, recover])
    idx = pd.date_range("2021-01-01", periods=len(values), freq=freq)
    return pd.Series(values, index=idx)


def _run_strategy(strategy, data: dict[str, pd.DataFrame], cash: float = 100_000.0):
    from ai_trade.backtest.engine.execution import ExecutionConfig, ExecutionSimulator
    from ai_trade.backtest.engine.runner import Runner

    runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
    return runner.run(strategy=strategy, data=data, initial_cash=cash)


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------


def test_validation_lookback_too_small():
    data = {"SPY": _ohlcv_from_close(_sine_close(n=200))}
    with pytest.raises(ValueError, match="lookback"):
        OUMeanRevStrategy(data=data, symbol="SPY", lookback=5)


def test_validation_z_entry_non_positive():
    data = {"SPY": _ohlcv_from_close(_sine_close(n=200))}
    with pytest.raises(ValueError, match="z_entry"):
        OUMeanRevStrategy(data=data, symbol="SPY", z_entry=-1.0)


def test_validation_unknown_symbol():
    data = {"SPY": _ohlcv_from_close(_sine_close(n=200))}
    with pytest.raises(KeyError, match="QQQ"):
        OUMeanRevStrategy(data=data, symbol="QQQ")


# ---------------------------------------------------------------------------
# Indicator correctness
# ---------------------------------------------------------------------------


def test_zscore_computed_on_log_close():
    close = _sine_close(n=500, period=40, amplitude=5.0, baseline=100.0)
    data = {"SPY": _ohlcv_from_close(close)}
    strat = OUMeanRevStrategy(data=data, symbol="SPY", lookback=60)

    ind = strat._indicators["SPY"]
    # Log(close) matches
    np.testing.assert_allclose(ind["log_close"].values, np.log(close.values))
    # First `lookback - 1` rows of z_score are NaN (rolling min_periods=60
    # produces first value at index 59).
    assert ind["z_score"].iloc[:59].isna().all()
    # After warmup window completes, z_score is finite.
    assert ind["z_score"].iloc[60:].notna().all()


def test_adf_lambda_sign_for_mean_reverting_series():
    """For a sine wave (mean-reverting), λ should be negative."""
    close = _sine_close(n=1000, period=40, amplitude=5.0, baseline=100.0)
    data = {"SPY": _ohlcv_from_close(close)}
    strat = OUMeanRevStrategy(data=data, symbol="SPY", lookback=80)

    ind = strat._indicators["SPY"]
    # Ignore NaN warmup
    lam = ind["adf_lambda"].dropna()
    # Majority should be negative for mean-reverting series
    assert (lam < 0).mean() > 0.5


# ---------------------------------------------------------------------------
# Entry/Exit behaviour
# ---------------------------------------------------------------------------


def test_enters_long_on_dip():
    """Strategy enters a long position when price dips below −z_entry σ."""
    close = _dip_and_recover(n_warmup=200, n_dip=20, n_recover=60, dip_depth=4.0)
    data = {"SPY": _ohlcv_from_close(close)}
    strat = OUMeanRevStrategy(
        data=data, symbol="SPY", lookback=60, z_entry=1.5,
        stop_pct=0.10, max_hold=50,
    )
    result = _run_strategy(strat, data)
    # Should produce at least one trade.
    assert len(result.trades) >= 1


def test_no_entry_when_lambda_non_negative():
    """If the series is not mean-reverting (λ ≥ 0), no entries occur.

    Use a strictly monotonic upward series — no dips to buy.
    """
    idx = pd.date_range("2021-01-01", periods=500, freq="h")
    close = pd.Series(100.0 + 0.1 * np.arange(500), index=idx)
    data = {"SPY": _ohlcv_from_close(close)}
    strat = OUMeanRevStrategy(
        data=data, symbol="SPY", lookback=60, z_entry=1.5,
    )
    result = _run_strategy(strat, data)
    assert len(result.trades) == 0


def test_exits_at_zscore_mean():
    """Strategy exits when z-score crosses z_exit (default 0).

    Uses a sine wave (clearly mean-reverting → λ < 0) so entries fire
    and the subsequent upswing produces a z > 0 exit.
    """
    close = _sine_close(n=800, period=120, amplitude=5.0, baseline=100.0)
    data = {"SPY": _ohlcv_from_close(close)}
    strat = OUMeanRevStrategy(
        data=data, symbol="SPY", lookback=80, z_entry=1.5,
        z_exit=0.0, stop_pct=0.20, max_hold=200,
    )
    result = _run_strategy(strat, data)
    # Entry + exit = at least one closed trade
    assert len(result.trades) >= 2


def test_time_stop_forces_exit():
    """If neither z-exit nor stop triggers, max_hold forces an exit.

    Sine wave entries fire; tiny max_hold ensures time-stop fires before
    z crosses above z_exit.
    """
    close = _sine_close(n=800, period=240, amplitude=5.0, baseline=100.0)
    data = {"SPY": _ohlcv_from_close(close)}
    strat = OUMeanRevStrategy(
        data=data, symbol="SPY", lookback=80, z_entry=1.5,
        z_exit=5.0, stop_pct=0.50, max_hold=5,  # z_exit huge, stop huge
    )
    result = _run_strategy(strat, data)
    # Expect at least one full round-trip forced by time-stop
    assert len(result.trades) >= 2


def test_grid_configs_has_four():
    from ai_trade.backtest.grid.ou_mean_rev_config import ou_mean_rev_grid_configs

    configs = ou_mean_rev_grid_configs()
    assert len(configs) == 4
    # All combinations unique
    pairs = [(c.lookback, c.z_entry) for c in configs]
    assert len(set(pairs)) == 4
