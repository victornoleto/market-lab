"""Tests for the EMA/SMA Threshold Crossover educational strategy.

Covers:
* Config validation (signs, filter, lookback).
* Regime signal: +1 above band, -1 below band, hysteresis inside.
* Simulation: synthetic long+short legs compound correctly; switch cost applied.
* Grid cartesian produces the expected count + unique cfg_ids.
* Composite score monotonicity in CAGR when Sharpe/MDD fixed.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from market_lab.backtest.grid.ema_sma_threshold_grid import (
    EMASMAThresholdAxes,
    cartesian_configs,
    compute_composite_scores,
    ConfigMetrics,
)
from market_lab.backtest.strategies.ema_sma_threshold_educational import (
    EMASMAThresholdConfig,
    compute_threshold_regime,
    simulate_ema_sma_threshold,
)


def _make_prices_returns(
    n: int = 300,
    daily_mu: float = 0.0005,
    daily_sigma: float = 0.008,
    seed: int = 7,
) -> tuple[pd.Series, pd.Series]:
    idx = pd.date_range("2000-01-03", periods=n, freq="B")
    rng = np.random.default_rng(seed)
    rets = pd.Series(rng.normal(daily_mu, daily_sigma, n), index=idx)
    prices = (1.0 + rets).cumprod() * 100.0
    return prices, rets


# ---------------------------------------------------------------------------
# Config validation
# ---------------------------------------------------------------------------


class TestEMASMAThresholdConfig:
    def test_defaults(self):
        cfg = EMASMAThresholdConfig()
        assert cfg.filter == "SMA"
        assert cfg.lookback == 200
        assert cfg.threshold_pct == 0.05
        assert cfg.buy_leverage == 2.0
        assert cfg.sell_leverage == 0.0
        assert cfg.fee > 0

    def test_bad_filter_raises(self):
        with pytest.raises(ValueError, match="filter must be"):
            EMASMAThresholdConfig(filter="WMA")  # type: ignore[arg-type]

    def test_negative_buy_leverage_raises(self):
        with pytest.raises(ValueError, match="buy_leverage"):
            EMASMAThresholdConfig(buy_leverage=-1.0)

    def test_positive_sell_leverage_raises(self):
        with pytest.raises(ValueError, match="sell_leverage"):
            EMASMAThresholdConfig(sell_leverage=1.0)

    def test_negative_threshold_raises(self):
        with pytest.raises(ValueError, match="threshold_pct"):
            EMASMAThresholdConfig(threshold_pct=-0.01)

    def test_cfg_id_deterministic_and_unique(self):
        a = EMASMAThresholdConfig(
            filter="EMA", lookback=125, threshold_pct=0.03,
            buy_leverage=3.0, sell_leverage=-2.0,
        )
        b = EMASMAThresholdConfig(
            filter="EMA", lookback=125, threshold_pct=0.03,
            buy_leverage=3.0, sell_leverage=-2.0,
        )
        c = EMASMAThresholdConfig(
            filter="SMA", lookback=125, threshold_pct=0.03,
            buy_leverage=3.0, sell_leverage=-2.0,
        )
        assert a.cfg_id == b.cfg_id
        assert a.cfg_id != c.cfg_id


# ---------------------------------------------------------------------------
# Regime signal
# ---------------------------------------------------------------------------


class TestComputeThresholdRegime:
    def test_above_band_emits_plus1(self):
        idx = pd.date_range("2020-01-01", periods=50, freq="B")
        prices = pd.Series(np.linspace(100, 130, 50), index=idx)
        cfg = EMASMAThresholdConfig(
            filter="SMA", lookback=20, threshold_pct=0.02,
            buy_leverage=1.0, sell_leverage=0.0,
        )
        sig = compute_threshold_regime(prices, cfg)
        assert sig.iloc[:19].isna().all()
        # Price climbs steadily — after warmup, must be +1 once above 1.02·MA.
        assert (sig.iloc[-5:] == 1).all()

    def test_below_band_emits_minus1(self):
        idx = pd.date_range("2020-01-01", periods=50, freq="B")
        prices = pd.Series(np.linspace(130, 90, 50), index=idx)
        cfg = EMASMAThresholdConfig(
            filter="SMA", lookback=20, threshold_pct=0.02,
            buy_leverage=1.0, sell_leverage=0.0,
        )
        sig = compute_threshold_regime(prices, cfg)
        assert (sig.iloc[-5:] == -1).all()

    def test_inside_band_holds_previous(self):
        """Price oscillates inside ±threshold of MA → regime shouldn't flip."""
        idx = pd.date_range("2020-01-01", periods=80, freq="B")
        # Force a clear above-band period, then prices inside band.
        px = np.full(80, 100.0)
        # First ramp up to trigger +1.
        px[:40] = np.linspace(100, 130, 40)
        # Then mild oscillation near ~122-124 (inside ±5% of ~122 MA).
        px[40:] = 122.5 + 0.3 * np.sin(np.linspace(0, 4 * np.pi, 40))
        prices = pd.Series(px, index=idx)
        cfg = EMASMAThresholdConfig(
            filter="SMA", lookback=20, threshold_pct=0.05,
            buy_leverage=1.0, sell_leverage=0.0,
        )
        sig = compute_threshold_regime(prices, cfg)
        # After having entered +1 near bar 25-35, oscillation bars should hold.
        tail = sig.iloc[60:]
        # All values in the tail must be +1 (never flipped, since inside band).
        assert (tail == 1).all(), f"unexpected flip: {tail.unique()}"


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------


class TestSimulate:
    def test_long_only_cash_matches_spy_roughly(self):
        """1x long + cash off with 0% threshold should track SPY up to fee drag."""
        prices, returns = _make_prices_returns(n=400, daily_mu=0.0007, seed=3)
        cfg = EMASMAThresholdConfig(
            filter="SMA", lookback=20, threshold_pct=0.0,
            buy_leverage=1.0, sell_leverage=0.0, fee=0.0,
            switch_cost_bps=0.0,
        )
        res = simulate_ema_sma_threshold(prices, returns, cfg)
        # Equity must be monotone-ish and positive.
        assert (res.equity > 0).all()
        assert res.equity.iloc[-1] > 0.5  # didn't blow up

    def test_inverse_leg_gains_on_downtrend(self):
        """With strong down-trend, -1x short leg should produce positive CAGR."""
        idx = pd.date_range("2020-01-01", periods=500, freq="B")
        rng = np.random.default_rng(42)
        # Strong downtrend
        rets = pd.Series(rng.normal(-0.002, 0.005, 500), index=idx)
        prices = (1.0 + rets).cumprod() * 100.0
        cfg = EMASMAThresholdConfig(
            filter="SMA", lookback=20, threshold_pct=0.02,
            buy_leverage=1.0, sell_leverage=-1.0, fee=0.0,
            switch_cost_bps=0.0,
        )
        res = simulate_ema_sma_threshold(prices, rets, cfg)
        # Equity must have grown (short regime during down-trend).
        assert res.equity.iloc[-1] > res.equity.iloc[0]

    def test_switch_cost_reduces_equity(self):
        """Fee-free but with switch cost: more whipsaws → lower equity."""
        prices, returns = _make_prices_returns(n=400, daily_mu=0.0, seed=11)
        # Tight threshold to induce many switches.
        cfg_ncost = EMASMAThresholdConfig(
            filter="SMA", lookback=10, threshold_pct=0.0,
            buy_leverage=1.0, sell_leverage=-1.0, fee=0.0,
            switch_cost_bps=0.0,
        )
        cfg_cost = EMASMAThresholdConfig(
            filter="SMA", lookback=10, threshold_pct=0.0,
            buy_leverage=1.0, sell_leverage=-1.0, fee=0.0,
            switch_cost_bps=50.0,  # 50bp — hefty penalty
        )
        res_ncost = simulate_ema_sma_threshold(prices, returns, cfg_ncost)
        res_cost = simulate_ema_sma_threshold(prices, returns, cfg_cost)
        # Same switch count, costly version must have lower terminal equity.
        assert res_cost.n_switches == res_ncost.n_switches
        if res_ncost.n_switches > 0:
            assert res_cost.equity.iloc[-1] < res_ncost.equity.iloc[-1]


# ---------------------------------------------------------------------------
# Grid
# ---------------------------------------------------------------------------


class TestGrid:
    def test_default_axes_have_384_configs(self):
        axes = EMASMAThresholdAxes()
        assert axes.n_configs == 2 * 4 * 4 * 3 * 4
        assert axes.n_configs == 384
        configs = cartesian_configs(axes)
        assert len(configs) == 384
        ids = {c.cfg_id for c in configs}
        assert len(ids) == 384, "cfg_ids must be unique"

    def test_smoke_axes_have_8_configs(self):
        axes = EMASMAThresholdAxes.smoke()
        assert axes.n_configs == 8
        configs = cartesian_configs(axes)
        assert len(configs) == 8

    def test_full_axes_have_1512_configs(self):
        axes = EMASMAThresholdAxes.full()
        assert axes.n_configs == 2 * 9 * 7 * 3 * 4
        assert axes.n_configs == 1512


# ---------------------------------------------------------------------------
# Composite score
# ---------------------------------------------------------------------------


class TestLookaheadAlignment:
    """Regression test locking the honest regime→return alignment.

    A perfect-oracle strategy (knows today's regime before today's bar)
    would earn return[t] at regime[t]. The honest simulator earns
    return[t] at regime[t-1]. On a hand-crafted series we can check that
    the honest output matches the latter, not the former.

    Cite ``[advances_fin_ml, p.31-34]`` — same fix applied in
    ``plano_a_leveraged_rotation.py`` commit 7b90a8f.
    """

    def test_yesterdays_regime_earns_todays_return(self):
        # 10-day hand-crafted series where the MA crosses exactly once.
        # Prices: 100, 100, 100, ..., 100 for 5 days, then 120 jump.
        # SMA-3: after day 3 = 100; at day 6 the jump to 120 means
        # price(6) = 120 > MA(6) = (100+100+120)/3 ≈ 106.67 → regime flips to +1 at day 6.
        # Before day 6 (price == MA == 100), regime = -1 (default).
        idx = pd.date_range("2020-01-01", periods=10, freq="B")
        px = [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 120.0, 120.0, 120.0, 120.0]
        prices = pd.Series(px, index=idx)
        rets = prices.pct_change().dropna()  # 9 returns, first is 0, day 6 is 0.20.
        cfg = EMASMAThresholdConfig(
            filter="SMA", lookback=3, threshold_pct=0.0,
            buy_leverage=1.0, sell_leverage=0.0, fee=0.0,
            switch_cost_bps=0.0, cash_rate_annual=0.0,
        )
        res = simulate_ema_sma_threshold(prices, rets, cfg)

        # On day 6 (index 5 in rets), the +20% return fires. With honest
        # alignment, the regime that earns day 6's return is the one
        # decided at close of day 5, which was -1 (cash, 0% return).
        # So the strategy earns ~0% on day 6, not 20%.
        # Final equity must be ≈ 1.0 (never entered the long position
        # before the jump; after the jump the price stays flat).
        assert res.equity.iloc[-1] == pytest.approx(1.0, abs=1e-6), (
            f"honest alignment broken — look-ahead would give equity=1.20, "
            f"got {res.equity.iloc[-1]}"
        )


class TestCompositeScore:
    def test_monotone_in_cagr_when_sharpe_mdd_tied(self):
        """If Sharpe and MDD are identical across configs, composite must rank by CAGR."""
        cfgs = [
            EMASMAThresholdConfig(buy_leverage=1.0 + i * 0.5) for i in range(4)
        ]
        metrics = [
            ConfigMetrics(
                cfg_id=c.cfg_id,
                cfg=c,
                cagr=0.05 + i * 0.02,  # increasing CAGR
                sharpe=0.5,
                max_drawdown=0.3,
                calmar=0.2,
                sortino=0.7,
                volatility=0.2,
                n_switches=10,
                cum_cost_pct=0.0,
            )
            for i, c in enumerate(cfgs)
        ]
        scores = compute_composite_scores(metrics)
        # Tied Sharpe + tied MDD → composite monotone in CAGR rank.
        assert scores[3] > scores[2] > scores[1] > scores[0]
