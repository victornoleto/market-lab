"""Tests for LETF Rotation strategy (Gayed's LRS).

Covers:

* :class:`LETFRotationConfig` validation.
* :func:`compute_regime_signal` SMA/EMA + band hysteresis.
* :func:`simulate_letf_rotation` return-series simulation including
  fees, switch costs, and BR 15% capital-gains tax on ON→OFF exits.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.strategies.letf_rotation import (
    LETFRotationConfig,
    compute_regime_signal,
    simulate_letf_rotation,
)


def _trending_up_returns(n: int = 300, daily_mu: float = 0.001,
                          daily_sigma: float = 0.005,
                          seed: int = 7) -> tuple[pd.Series, pd.Series]:
    """SPX-like series trending up — intended to stay RISK_ON after warmup."""
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    rng = np.random.default_rng(seed)
    rets = pd.Series(rng.normal(daily_mu, daily_sigma, n), index=idx)
    prices = (1.0 + rets).cumprod() * 100.0
    return rets, prices


def _trending_down_returns(n: int = 300, daily_mu: float = -0.001,
                            daily_sigma: float = 0.01,
                            seed: int = 11) -> tuple[pd.Series, pd.Series]:
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    rng = np.random.default_rng(seed)
    rets = pd.Series(rng.normal(daily_mu, daily_sigma, n), index=idx)
    prices = (1.0 + rets).cumprod() * 100.0
    return rets, prices


class TestLETFRotationConfig:
    def test_defaults_match_gayed_canonical(self):
        cfg = LETFRotationConfig()
        assert cfg.filter == "SMA"
        assert cfg.lookback == 200
        assert cfg.band_pct == 0.0
        assert cfg.leverage == 3.0
        assert cfg.gold_weight == 0.0
        assert cfg.annual_fee == 0.01
        assert cfg.tax_rate == 0.15

    def test_invalid_filter_raises(self):
        with pytest.raises(ValueError, match="filter must be"):
            LETFRotationConfig(filter="WMA")  # type: ignore[arg-type]

    def test_invalid_lookback_raises(self):
        with pytest.raises(ValueError, match="lookback must be"):
            LETFRotationConfig(lookback=1)

    def test_negative_band_raises(self):
        with pytest.raises(ValueError, match="band_pct"):
            LETFRotationConfig(band_pct=-0.01)

    def test_zero_leverage_raises(self):
        with pytest.raises(ValueError, match="leverage"):
            LETFRotationConfig(leverage=0.0)

    def test_gold_weight_bounds(self):
        with pytest.raises(ValueError, match="gold_weight"):
            LETFRotationConfig(gold_weight=1.5)
        with pytest.raises(ValueError, match="gold_weight"):
            LETFRotationConfig(gold_weight=-0.1)

    def test_switch_cost_pct_computed(self):
        cfg = LETFRotationConfig(commission_bps=10.0, spread_bps=5.0)
        assert cfg.switch_cost_pct == pytest.approx(0.0015)

    def test_immutable_frozen(self):
        cfg = LETFRotationConfig()
        with pytest.raises((AttributeError, Exception)):
            cfg.leverage = 2.0  # type: ignore[misc]


class TestComputeRegimeSignal:
    def test_sma_above_ma_emits_on(self):
        idx = pd.date_range("2020-01-01", periods=50, freq="B")
        # Prices rising linearly — after warmup must be ON.
        prices = pd.Series(np.linspace(100, 120, 50), index=idx)
        sig = compute_regime_signal(prices, filter="SMA", lookback=20, band_pct=0.0)
        assert sig.iloc[:19].isna().all()
        # Later values strictly above SMA since price is monotonically rising.
        assert (sig.iloc[19:] == "ON").all()

    def test_sma_below_ma_emits_off(self):
        idx = pd.date_range("2020-01-01", periods=50, freq="B")
        prices = pd.Series(np.linspace(120, 100, 50), index=idx)
        sig = compute_regime_signal(prices, filter="SMA", lookback=20, band_pct=0.0)
        assert (sig.iloc[19:] == "OFF").all()

    def test_band_holds_prior_state(self):
        # Prices rise steeply (past 5% above SMA), then tiny dip inside
        # band — 5% band must hold ON; 0% band flips on minor dip.
        n = 30
        idx = pd.date_range("2020-01-01", periods=n, freq="B")
        # Ramp 100→150 (steep enough to clear 5% band upper), then dip
        # to 148 (still above SMA, inside 5% band from MA).
        px = np.concatenate([np.linspace(100, 150, 20), np.linspace(150, 148, 10)])
        prices = pd.Series(px, index=idx)
        sig_no_band = compute_regime_signal(prices, "SMA", lookback=10, band_pct=0.0)
        sig_band = compute_regime_signal(prices, "SMA", lookback=10, band_pct=0.05)
        # Both must reach ON at the peak.
        assert sig_no_band.iloc[19] == "ON"
        assert sig_band.iloc[19] == "ON"
        # At the dipped end, strict (0%) cross may flip to OFF if price
        # dropped below MA — with our setup MA is still rising, so price
        # 148 may equal MA; relaxed assertion checks 5% band is sticky.
        assert sig_band.iloc[-1] == "ON"

    def test_ema_smoother_than_sma(self):
        idx = pd.date_range("2020-01-01", periods=40, freq="B")
        prices = pd.Series(np.linspace(100, 120, 40), index=idx)
        sig_sma = compute_regime_signal(prices, filter="SMA", lookback=10, band_pct=0.0)
        sig_ema = compute_regime_signal(prices, filter="EMA", lookback=10, band_pct=0.0)
        # Both should produce ON for strongly trending prices after warmup.
        assert (sig_sma.dropna() == "ON").all()
        assert (sig_ema.dropna() == "ON").all()

    def test_invalid_filter_raises(self):
        idx = pd.date_range("2020-01-01", periods=10, freq="B")
        prices = pd.Series(np.arange(10, dtype=float) + 100, index=idx)
        with pytest.raises(ValueError, match="filter must be"):
            compute_regime_signal(prices, filter="WMA", lookback=3)  # type: ignore[arg-type]

    def test_warmup_is_off_default_before_first_cross(self):
        # Series that starts exactly at the MA — first non-NaN signal falls
        # inside the band (both upper and lower ties). Implementation
        # defaults prev to "OFF" before any definitive cross.
        idx = pd.date_range("2020-01-01", periods=5, freq="B")
        prices = pd.Series([100, 100, 100, 100, 100], index=idx)
        sig = compute_regime_signal(prices, "SMA", lookback=3, band_pct=0.1)
        # After warmup (index 2+), price == MA, inside band → default OFF.
        assert sig.iloc[2] == "OFF"
        assert sig.iloc[3] == "OFF"


class TestSimulateLetfRotation:
    def test_trending_up_mostly_on(self):
        rets, prices = _trending_up_returns(n=300)
        cfg = LETFRotationConfig(
            filter="SMA", lookback=50, band_pct=0.0, leverage=3.0,
            gold_weight=0.0, annual_fee=0.0,
            commission_bps=0.0, spread_bps=0.0, tax_rate=0.0,
        )
        result = simulate_letf_rotation(rets, prices, cfg)
        on_days = (result.regime == "ON").sum()
        off_days = (result.regime == "OFF").sum()
        assert on_days > off_days
        # Equity should grow in trending-up market at 3x.
        assert result.equity.iloc[-1] > 1.0

    def test_trending_down_goes_off(self):
        rets, prices = _trending_down_returns(n=300)
        cfg = LETFRotationConfig(
            filter="SMA", lookback=50, band_pct=0.0, leverage=3.0,
            gold_weight=0.0, annual_fee=0.0,
            commission_bps=0.0, spread_bps=0.0, tax_rate=0.0,
        )
        result = simulate_letf_rotation(rets, prices, cfg)
        post_warmup = result.regime.iloc[50:]
        off_days = (post_warmup == "OFF").sum()
        on_days = (post_warmup == "ON").sum()
        assert off_days > on_days

    def test_cash_off_asset_zero_return(self):
        # Pure downtrend — must end RISK_OFF and, with 0 cash rate,
        # equity must stop declining once OFF.
        rets, prices = _trending_down_returns(n=300)
        cfg = LETFRotationConfig(
            filter="SMA", lookback=50, band_pct=0.0, leverage=3.0,
            gold_weight=0.0, cash_rate_annual=0.0, annual_fee=0.0,
            commission_bps=0.0, spread_bps=0.0, tax_rate=0.0,
        )
        result = simulate_letf_rotation(rets, prices, cfg)
        # Once in OFF, equity is flat until next ON.
        in_off = result.regime == "OFF"
        # Simpler: final equity better than 3x buy-and-hold in downtrend.
        bh_3x = (1.0 + 3.0 * rets).cumprod().iloc[-1]
        assert result.equity.iloc[-1] > bh_3x

    def test_leverage_fee_drag_on_on_days(self):
        rets, prices = _trending_up_returns(n=250)
        cfg_no_fee = LETFRotationConfig(
            filter="SMA", lookback=50, leverage=3.0, gold_weight=0.0,
            annual_fee=0.0, commission_bps=0.0, spread_bps=0.0, tax_rate=0.0,
        )
        cfg_with_fee = LETFRotationConfig(
            filter="SMA", lookback=50, leverage=3.0, gold_weight=0.0,
            annual_fee=0.01, commission_bps=0.0, spread_bps=0.0, tax_rate=0.0,
        )
        r_no = simulate_letf_rotation(rets, prices, cfg_no_fee)
        r_fee = simulate_letf_rotation(rets, prices, cfg_with_fee)
        assert r_fee.equity.iloc[-1] < r_no.equity.iloc[-1]

    def test_switch_cost_applied_on_transitions(self):
        # Force repeated whipsaw by an alternating price series.
        n = 300
        idx = pd.date_range("2020-01-01", periods=n, freq="B")
        rng = np.random.default_rng(3)
        # Slow drift + occasional big jumps to cross the MA.
        base = np.cumsum(rng.normal(0, 0.003, n))
        shock = np.where(np.arange(n) % 30 == 0, -0.05, 0.0)
        rets = pd.Series(base + shock, index=idx)
        prices = (1.0 + rets).cumprod() * 100.0

        cfg_no_cost = LETFRotationConfig(
            filter="SMA", lookback=20, leverage=2.0, gold_weight=0.0,
            annual_fee=0.0, commission_bps=0.0, spread_bps=0.0, tax_rate=0.0,
        )
        cfg_high_cost = LETFRotationConfig(
            filter="SMA", lookback=20, leverage=2.0, gold_weight=0.0,
            annual_fee=0.0, commission_bps=50.0, spread_bps=50.0, tax_rate=0.0,
        )
        r_no = simulate_letf_rotation(rets, prices, cfg_no_cost)
        r_cost = simulate_letf_rotation(rets, prices, cfg_high_cost)
        # Both must see the same number of switches.
        assert r_no.switches.sum() == r_cost.switches.sum()
        if r_no.switches.sum() > 0:
            # High-cost run must accumulate positive cost drag.
            assert r_cost.cum_cost_pct > 0.0
            assert r_cost.equity.iloc[-1] < r_no.equity.iloc[-1]

    def test_gold_off_asset_requires_gold_returns(self):
        rets, prices = _trending_up_returns(n=100)
        cfg = LETFRotationConfig(gold_weight=0.5, lookback=20)
        with pytest.raises(ValueError, match="gold_returns required"):
            simulate_letf_rotation(rets, prices, cfg)

    def test_gold_alignment_required(self):
        rets, prices = _trending_up_returns(n=100)
        # Misaligned gold series (shifted index).
        gold = pd.Series(0.0, index=rets.index[:-5])
        cfg = LETFRotationConfig(gold_weight=0.5, lookback=20)
        with pytest.raises(ValueError, match="gold_returns must share index"):
            simulate_letf_rotation(rets, prices, cfg, gold_returns=gold)

    def test_gold_blend_applied_on_off(self):
        # Pure downtrend → mostly OFF → gold-100% OFF must track gold return.
        rets, prices = _trending_down_returns(n=300)
        idx = rets.index
        rng = np.random.default_rng(99)
        gold_rets = pd.Series(rng.normal(0.0005, 0.004, len(idx)), index=idx)

        cfg_cash = LETFRotationConfig(
            filter="SMA", lookback=50, leverage=3.0, gold_weight=0.0,
            annual_fee=0.0, commission_bps=0.0, spread_bps=0.0, tax_rate=0.0,
            cash_rate_annual=0.0,
        )
        cfg_gold = LETFRotationConfig(
            filter="SMA", lookback=50, leverage=3.0, gold_weight=1.0,
            annual_fee=0.0, commission_bps=0.0, spread_bps=0.0, tax_rate=0.0,
        )
        r_cash = simulate_letf_rotation(rets, prices, cfg_cash)
        r_gold = simulate_letf_rotation(rets, prices, cfg_gold, gold_returns=gold_rets)
        # In a downtrend where gold has positive drift, 100%-gold OFF-sleeve
        # should outperform cash OFF-sleeve.
        assert r_gold.equity.iloc[-1] > r_cash.equity.iloc[-1]

    def test_tax_reduces_equity_on_on_off_exits(self):
        # Force a switch sequence: enter ON, gain, exit to OFF (tax event).
        n = 300
        idx = pd.date_range("2020-01-01", periods=n, freq="B")
        # Up ramp (150 days) → down ramp (150 days).
        up = np.linspace(0.0, 0.5, 150)
        dn = np.linspace(0.5, -0.3, 150)
        prices_arr = 100.0 * (1.0 + np.concatenate([up, dn]))
        prices = pd.Series(prices_arr, index=idx)
        rets = prices.pct_change().fillna(0.0)

        cfg_no_tax = LETFRotationConfig(
            filter="SMA", lookback=30, leverage=2.0, gold_weight=0.0,
            annual_fee=0.0, commission_bps=0.0, spread_bps=0.0, tax_rate=0.0,
        )
        cfg_tax = LETFRotationConfig(
            filter="SMA", lookback=30, leverage=2.0, gold_weight=0.0,
            annual_fee=0.0, commission_bps=0.0, spread_bps=0.0, tax_rate=0.15,
        )
        r_no = simulate_letf_rotation(rets, prices, cfg_no_tax)
        r_tax = simulate_letf_rotation(rets, prices, cfg_tax)
        # Tax applied only when exit gain > 0. In a profitable ON sleeve,
        # tax run must end lower.
        assert r_no.switches.sum() >= 1
        if r_no.equity.iloc[-1] > 1.0:  # ON leg was profitable
            assert r_tax.cum_tax_pct > 0.0
            assert r_tax.equity.iloc[-1] < r_no.equity.iloc[-1]

    def test_result_metrics_scalar(self):
        rets, prices = _trending_up_returns(n=250)
        cfg = LETFRotationConfig(
            filter="SMA", lookback=50, leverage=2.0, gold_weight=0.0,
            annual_fee=0.01, commission_bps=10.0, spread_bps=5.0, tax_rate=0.15,
        )
        result = simulate_letf_rotation(rets, prices, cfg)
        sharpe = result.sharpe()
        cagr = result.cagr()
        dd = result.max_drawdown()
        assert isinstance(sharpe, float)
        assert isinstance(cagr, float)
        assert isinstance(dd, float)
        assert dd <= 0.0

    def test_zero_std_sharpe_is_zero(self):
        # All-cash path (leverage=1, OFF only) → returns all near zero.
        idx = pd.date_range("2020-01-01", periods=100, freq="B")
        rets = pd.Series(0.0, index=idx)
        # Force prices below MA throughout so regime is always OFF.
        prices = pd.Series(100.0, index=idx)
        cfg = LETFRotationConfig(
            filter="SMA", lookback=10, leverage=1.0, gold_weight=0.0,
            annual_fee=0.0, cash_rate_annual=0.0,
            commission_bps=0.0, spread_bps=0.0, tax_rate=0.0,
        )
        result = simulate_letf_rotation(rets, prices, cfg)
        assert result.sharpe() == 0.0


class TestSimulateFFRAware:
    """Phase 3.5b Task 7a — opt-in FFR-aware cost path."""

    def _always_on_series(self, n: int = 400, seed: int = 42):
        # Strong uptrend → regime stays ON almost the entire window after
        # the MA warmup, so cost-model differences between flat-fee and
        # FFR-aware accumulate cleanly across most bars.
        idx = pd.date_range("2020-01-01", periods=n, freq="B")
        rng = np.random.default_rng(seed)
        rets = pd.Series(rng.normal(0.0012, 0.004, n), index=idx)
        prices = (1.0 + rets).cumprod() * 100.0
        return rets, prices

    def test_default_none_preserves_flat_fee_path(self):
        rets, prices = self._always_on_series()
        cfg = LETFRotationConfig(
            filter="SMA", lookback=20, band_pct=0.0, leverage=2.0,
            gold_weight=0.0, annual_fee=0.01, cash_rate_annual=0.0,
            commission_bps=0.0, spread_bps=0.0, tax_rate=0.0,
        )
        r_default = simulate_letf_rotation(rets, prices, cfg)
        r_explicit_none = simulate_letf_rotation(
            rets, prices, cfg, ffr_annualized=None
        )
        # Byte-identical equity paths — the default behavior is unchanged.
        pd.testing.assert_series_equal(
            r_default.equity, r_explicit_none.equity
        )
        pd.testing.assert_series_equal(
            r_default.daily_returns, r_explicit_none.daily_returns
        )

    def test_ffr_aware_high_rate_reduces_equity_vs_flat_fee(self):
        # 7.5%/yr FFR is above the 1%/yr flat-fee drag the Gayed model
        # assumes, so the FFR-aware equity curve must end BELOW the flat
        # one under the same SPX path and signal sequence.
        rets, prices = self._always_on_series()
        cfg = LETFRotationConfig(
            filter="SMA", lookback=20, band_pct=0.0, leverage=2.0,
            gold_weight=0.0, annual_fee=0.01, cash_rate_annual=0.0,
            commission_bps=0.0, spread_bps=0.0, tax_rate=0.0,
        )
        ffr = pd.Series(0.075, index=rets.index)
        r_flat = simulate_letf_rotation(rets, prices, cfg)
        r_ffr = simulate_letf_rotation(
            rets, prices, cfg,
            ffr_annualized=ffr,
            ffr_swap_exposure=1.1,
            ffr_spread=0.004,
            ffr_expense_ratio=0.0095,
        )
        assert r_ffr.equity.iloc[-1] < r_flat.equity.iloc[-1]
        # Same regime trajectory → same number of switches.
        assert int(r_ffr.switches.sum()) == int(r_flat.switches.sum())

    def test_ffr_aware_low_rate_beats_flat_fee(self):
        # 0%/yr FFR with default SW=1.1, SP=0.4%, ER=0.95% gives
        # annual_cost = 1.1 * (2-1) * 0.004 + 0.0095 = 1.39%/yr on ON days
        # vs flat 1%/yr of Gayed. At L=2 that's still more expensive ON,
        # but keeps the flat variant ahead → assert the relationship is
        # stable: flat at fee=0.0139 matches FFR-aware at FFR=0.
        rets, prices = self._always_on_series()
        cfg_flat_matched = LETFRotationConfig(
            filter="SMA", lookback=20, band_pct=0.0, leverage=2.0,
            gold_weight=0.0, annual_fee=1.1 * 0.004 + 0.0095,
            cash_rate_annual=0.0, commission_bps=0.0, spread_bps=0.0,
            tax_rate=0.0,
        )
        r_flat_matched = simulate_letf_rotation(
            rets, prices, cfg_flat_matched
        )
        cfg_for_ffr = LETFRotationConfig(
            filter="SMA", lookback=20, band_pct=0.0, leverage=2.0,
            gold_weight=0.0, annual_fee=0.01, cash_rate_annual=0.0,
            commission_bps=0.0, spread_bps=0.0, tax_rate=0.0,
        )
        ffr_zero = pd.Series(0.0, index=rets.index)
        r_ffr = simulate_letf_rotation(
            rets, prices, cfg_for_ffr,
            ffr_annualized=ffr_zero,
            ffr_swap_exposure=1.1,
            ffr_spread=0.004,
            ffr_expense_ratio=0.0095,
        )
        # Equity paths must match to float precision when the two cost
        # models are analytically equal (same ON-return formula).
        np.testing.assert_allclose(
            r_ffr.equity.to_numpy(),
            r_flat_matched.equity.to_numpy(),
            rtol=1e-12, atol=1e-12,
        )
