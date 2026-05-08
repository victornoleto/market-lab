"""Unit tests for equal-notional sector momentum (iter 003).

Sizing primitive: `position_size_shares_equal_notional`. Signal primitives
are imported from ``sector_momentum_clenow`` and tested there; this module
focuses on the sizing change + strategy integration.

Citations:
* `[stocks_on_the_move, p.60, p.66-67, p.70-77, p.82, p.98-99]` — ranking
  and regime
* `[advances_fin_ml, p.298-299]` — 1/N prior motivation
* Jegadeesh-Titman (1993) — cross-sectional momentum with equal-weight
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from market_lab.backtest.engine.execution import ExecutionConfig, ExecutionSimulator
from market_lab.backtest.engine.runner import Runner
from market_lab.backtest.strategies.sector_momentum_equal_notional import (
    SectorMomentumEqualNotional,
    position_size_shares_equal_notional,
)


# ---------------------------------------------------------------------------
# Equal-notional sizing primitive
# ---------------------------------------------------------------------------


class TestEqualNotionalSizing:
    def test_basic_100k_top5_unlevered(self):
        """$100k equity, K=5, leverage=1.0, price=$100 → $20k per slot →
        200 shares."""
        shares = position_size_shares_equal_notional(
            equity=100_000.0, price=100.0, k_total=5, leverage=1.0
        )
        assert shares == 200

    def test_leverage_2x_doubles_shares(self):
        """$100k × 2.0 leverage, K=5, price=$100 → $40k per slot → 400."""
        shares = position_size_shares_equal_notional(
            equity=100_000.0, price=100.0, k_total=5, leverage=2.0
        )
        assert shares == 400

    def test_top_k_3_vs_5_inverse_proportional(self):
        """Halving K roughly scales shares by K_old/K_new (~5/3)."""
        k3 = position_size_shares_equal_notional(
            equity=100_000.0, price=100.0, k_total=3, leverage=1.0
        )
        k5 = position_size_shares_equal_notional(
            equity=100_000.0, price=100.0, k_total=5, leverage=1.0
        )
        # k3=floor(33333/100)=333, k5=floor(20000/100)=200 → ratio exactly 5/3.
        assert k3 == 333
        assert k5 == 200

    def test_floor_rounding_for_fractional_shares(self):
        """$100k, K=7, price=$150 → target_notional=$14285.7 →
        14285.7 / 150 = 95.24 → floor to 95."""
        shares = position_size_shares_equal_notional(
            equity=100_000.0, price=150.0, k_total=7, leverage=1.0
        )
        assert shares == 95

    def test_zero_price_returns_zero(self):
        assert (
            position_size_shares_equal_notional(
                equity=100_000.0, price=0.0, k_total=5, leverage=1.0
            )
            == 0
        )

    def test_zero_equity_returns_zero(self):
        assert (
            position_size_shares_equal_notional(
                equity=0.0, price=100.0, k_total=5, leverage=1.0
            )
            == 0
        )

    def test_zero_k_returns_zero(self):
        assert (
            position_size_shares_equal_notional(
                equity=100_000.0, price=100.0, k_total=0, leverage=1.0
            )
            == 0
        )

    def test_nan_price_returns_zero(self):
        assert (
            position_size_shares_equal_notional(
                equity=100_000.0, price=float("nan"), k_total=5, leverage=1.0
            )
            == 0
        )

    def test_deployment_full_at_k_eq_universe(self):
        """When top_k = universe_size, the portfolio deploys leverage × equity
        fully across all positions (ignoring integer-floor leakage)."""
        equity = 100_000.0
        price = 100.0
        k = 11  # 11 SPDR sectors
        leverage = 1.0
        shares = position_size_shares_equal_notional(
            equity=equity, price=price, k_total=k, leverage=leverage
        )
        # Each position = floor(100000*1.0/11/100) = floor(90.909) = 90
        assert shares == 90
        # Total deployed across 11 positions
        deployed = shares * price * k
        # 90 * 100 * 11 = 99000 = 99% of equity (1% floor leakage)
        assert deployed / equity == pytest.approx(0.99, abs=1e-9)


# ---------------------------------------------------------------------------
# Strategy integration (engine smoke)
# ---------------------------------------------------------------------------


class TestStrategyIntegration:
    """End-to-end smoke: 3 synthetic sectors + SPY regime."""

    @pytest.fixture
    def synthetic_data(self):
        rng = np.random.default_rng(0)
        n = 400
        idx = pd.bdate_range("2020-01-01", periods=n)

        def make_series(start: float, drift: float, noise: float = 0.005) -> pd.DataFrame:
            rets = rng.normal(drift, noise, size=n)
            close = start * np.exp(np.cumsum(rets))
            return pd.DataFrame({
                "open": close * (1 - 0.001),
                "high": close * 1.005,
                "low": close * 0.995,
                "close": close,
                "volume": 1e6,
            }, index=idx)

        return {
            "XLK": make_series(100, 0.0008),  # strongest
            "XLF": make_series(100, 0.0004),  # medium
            "XLP": make_series(100, 0.0001),  # weakest
            "SPY": make_series(300, 0.0005),
        }

    def test_runs_cleanly(self, synthetic_data):
        strat = SectorMomentumEqualNotional(
            universe=["XLK", "XLF", "XLP"],
            regime_symbol="SPY",
            top_k=2,
            buy_leverage=1.0,
        )
        runner = Runner(executor=ExecutionSimulator(config=ExecutionConfig()))
        result = runner.run(strat, synthetic_data, initial_cash=100_000.0)
        assert len(result.equity_curve) > 0
        assert result.final_equity > 0

    def test_favors_strongest_trend(self, synthetic_data):
        """Top-1 concentration → XLK trades dominate over XLP (weakest)."""
        strat = SectorMomentumEqualNotional(
            universe=["XLK", "XLF", "XLP"],
            regime_symbol="SPY",
            top_k=1,
            buy_leverage=1.0,
        )
        runner = Runner(executor=ExecutionSimulator(config=ExecutionConfig()))
        result = runner.run(strat, synthetic_data, initial_cash=100_000.0)
        xlk_trades = sum(1 for t in result.trades if t.symbol == "XLK")
        xlp_trades = sum(1 for t in result.trades if t.symbol == "XLP")
        assert xlk_trades >= xlp_trades

    def test_full_deployment_vs_atr_risk_parity(self, synthetic_data):
        """The core iter 003 claim: equal-notional deploys substantially more
        capital than ATR-risk-parity on a sector universe with low per-bar vol.

        With top_k=3 and buy_leverage=1.0, equal-notional should aim for ~100%
        equity deployment (minus floor-rounding leakage). Compare to the
        Clenow ATR-risk-parity variant from iter 002 on the same synthetic
        data — measure exposure/equity at final bar.
        """
        from market_lab.backtest.strategies.sector_momentum_clenow import (
            SectorMomentumClenow,
        )

        strat_eq = SectorMomentumEqualNotional(
            universe=["XLK", "XLF", "XLP"],
            regime_symbol="SPY",
            top_k=3,
            buy_leverage=1.0,
        )
        strat_clenow = SectorMomentumClenow(
            universe=["XLK", "XLF", "XLP"],
            regime_symbol="SPY",
            top_k=3,
            buy_leverage=1.0,
        )
        runner = Runner(executor=ExecutionSimulator(config=ExecutionConfig()))
        res_eq = runner.run(strat_eq, synthetic_data, initial_cash=100_000.0)
        res_clenow = runner.run(strat_clenow, synthetic_data, initial_cash=100_000.0)

        # Compute final exposure = sum of (volume * last_close) / final_equity.
        last_ts = synthetic_data["XLK"].index[-1]
        last_closes = {sym: float(df["close"].iloc[-1]) for sym, df in synthetic_data.items()}

        def exposure_ratio(result, positions_at_end):
            gross = 0.0
            for sym, vol in positions_at_end.items():
                if sym in last_closes:
                    gross += abs(vol) * last_closes[sym]
            return gross / max(result.final_equity, 1e-9)

        # The Portfolio positions on the BacktestResult reflect the end state;
        # grab them via the portfolio snapshot if available, else reconstruct
        # from trades.
        def positions_from_trades(trades):
            positions: dict[str, float] = {}
            for t in trades:
                sign = 1.0 if t.side == "buy" else -1.0
                positions[t.symbol] = positions.get(t.symbol, 0.0) + sign * t.volume
            return {s: v for s, v in positions.items() if abs(v) > 1e-9}

        pos_eq = positions_from_trades(res_eq.trades)
        pos_cl = positions_from_trades(res_clenow.trades)
        exp_eq = exposure_ratio(res_eq, pos_eq)
        exp_cl = exposure_ratio(res_clenow, pos_cl)

        # Equal-notional should deploy substantially more than ATR-risk-parity.
        # The exact threshold depends on synthetic ATR, but at 10 bps and
        # ATR~0.5% of price, Clenow exposure should be ≪ equal-notional's.
        # For a conservative integration check: equal-notional > 2 × Clenow.
        assert exp_eq > 2 * exp_cl, (
            f"equal-notional should deploy more capital than ATR-risk-parity "
            f"on a low-vol universe; got eq={exp_eq:.2f} vs clenow={exp_cl:.2f}"
        )


# ---------------------------------------------------------------------------
# Cross-lib numpy reference (G7 gate primitive)
# ---------------------------------------------------------------------------


class TestNumpyG7Reference:
    """Pure-numpy equity-curve reference for G7 parity checking.

    The reference re-implements the entire equal-notional rebalance logic
    without the Runner/Portfolio/ExecutionSimulator stack. Trades are booked
    at close prices with no transaction costs (identical to the runner when
    ExecutionConfig uses zero costs). The comparison must agree to ±3pp CAGR
    on a toy universe — same acceptance bar as G7 on real data.
    """

    @staticmethod
    def _numpy_simulate(
        closes: dict[str, np.ndarray],
        regime_closes: np.ndarray,
        index: pd.DatetimeIndex,
        *,
        top_k: int,
        buy_leverage: float,
        lookback_slope: int,
        lookback_trend: int,
        lookback_regime: int,
        gap_threshold: float,
        rebalance_weekday: int,
    ) -> np.ndarray:
        """Return equity curve as np.ndarray aligned with ``index``."""
        n = len(index)
        symbols = list(closes.keys())
        equity = 100_000.0
        cash = equity
        positions = {s: 0 for s in symbols}
        equity_curve = np.zeros(n, dtype=float)
        last_rebalance_date: pd.Timestamp | None = None
        rebalance_counter = 0

        for i in range(n):
            ts = index[i]

            # Mark-to-market equity
            mtm = sum(positions[s] * closes[s][i] for s in symbols)
            equity = cash + mtm
            equity_curve[i] = equity

            # Only rebalance on the chosen weekday.
            if ts.weekday() != rebalance_weekday:
                continue
            if last_rebalance_date is not None and (ts - last_rebalance_date).days < 5:
                continue
            if i + 1 < max(lookback_slope, lookback_trend, lookback_regime):
                continue
            last_rebalance_date = ts
            rebalance_counter += 1

            # Compute scores + disqualifiers.
            scores: dict[str, float] = {}
            disq: set[str] = set()
            for s in symbols:
                series = closes[s][: i + 1]
                if len(series) < max(lookback_slope, lookback_trend):
                    disq.add(s)
                    continue
                window = series[-lookback_slope:]
                y = np.log(window)
                x = np.arange(lookback_slope, dtype=float)
                xm, ym = x.mean(), y.mean()
                cov = ((x - xm) * (y - ym)).sum()
                var_x = ((x - xm) ** 2).sum()
                var_y = ((y - ym) ** 2).sum()
                slope_m = cov / var_x if var_x > 0 else 0.0
                annualized = math.exp(slope_m) ** 250 - 1
                r2 = (cov ** 2) / (var_x * var_y) if (var_x > 0 and var_y > 0) else 0.0
                scores[s] = annualized * r2
                # Trend disqualifier
                trend_win = series[-lookback_trend:]
                if series[-1] < trend_win.mean():
                    disq.add(s)
                # Gap disqualifier
                gap_win = series[-lookback_slope:]
                daily_moves = np.abs(np.diff(gap_win) / gap_win[:-1])
                if daily_moves.size and daily_moves.max() > gap_threshold:
                    disq.add(s)

            # Top-K
            eligible = [(s, sc) for s, sc in scores.items() if s not in disq and math.isfinite(sc)]
            eligible.sort(key=lambda p: (-p[1], p[0]))
            top = [s for s, _ in eligible[:top_k]]

            # Regime
            regime_win = regime_closes[: i + 1]
            regime_on = (
                len(regime_win) >= lookback_regime
                and regime_win[-1] > regime_win[-lookback_regime:].mean()
            )

            # Sell leg — exit anything held not in top / disqualified
            for s in list(positions.keys()):
                if positions[s] > 0 and (s not in top or s in disq):
                    cash += positions[s] * closes[s][i]
                    positions[s] = 0

            # Buy leg — regime gate
            if regime_on:
                for s in top:
                    if positions[s] > 0:
                        continue
                    price = closes[s][i]
                    if price <= 0:
                        continue
                    target_notional = equity * buy_leverage / top_k
                    shares = int(math.floor(target_notional / price))
                    if shares > 0 and cash >= shares * price:
                        cash -= shares * price
                        positions[s] = shares

            # Periodic resize for survivors (every 2nd rebalance).
            if rebalance_counter % 2 == 0:
                for s in top:
                    if positions[s] > 0:
                        price = closes[s][i]
                        target_notional = equity * buy_leverage / top_k
                        target_shares = int(math.floor(target_notional / price))
                        diff = target_shares - positions[s]
                        if diff > 0 and cash >= diff * price:
                            cash -= diff * price
                            positions[s] += diff
                        elif diff < 0:
                            cash += (-diff) * price
                            positions[s] += diff

        # Final MTM
        equity_curve[-1] = cash + sum(positions[s] * closes[s][-1] for s in symbols)
        return equity_curve

    def test_numpy_ref_matches_engine_cagr_within_3pp(self):
        """Engine vs numpy reference on a toy 3-sector universe: ±3pp CAGR."""
        rng = np.random.default_rng(11)
        n = 600
        index = pd.bdate_range("2018-01-02", periods=n)

        def make(drift: float, start: float = 100.0, noise: float = 0.01):
            rets = rng.normal(drift, noise, size=n)
            close = start * np.exp(np.cumsum(rets))
            return close

        closes = {
            "XLK": make(0.0008),
            "XLF": make(0.0004),
            "XLP": make(0.0001),
        }
        spy_close = make(0.0004, start=300.0, noise=0.008)

        # numpy reference
        np_equity = self._numpy_simulate(
            closes=closes,
            regime_closes=spy_close,
            index=index,
            top_k=2,
            buy_leverage=1.0,
            lookback_slope=90,
            lookback_trend=100,
            lookback_regime=200,
            gap_threshold=0.15,
            rebalance_weekday=2,
        )

        # engine
        def to_ohlc(close_arr):
            return pd.DataFrame({
                "open":  close_arr * (1 - 0.001),
                "high":  close_arr * 1.005,
                "low":   close_arr * 0.995,
                "close": close_arr,
                "volume": 1e6,
            }, index=index)

        data = {s: to_ohlc(c) for s, c in closes.items()}
        data["SPY"] = to_ohlc(spy_close)

        strat = SectorMomentumEqualNotional(
            universe=["XLK", "XLF", "XLP"],
            regime_symbol="SPY",
            top_k=2,
            buy_leverage=1.0,
            lookback_slope=90,
            lookback_trend=100,
            lookback_regime=200,
            gap_threshold=0.15,
            rebalance_weekday=2,
        )
        # Zero-cost execution — matches the no-cost numpy reference.
        exec_cfg = ExecutionConfig(half_spread=0.0, slippage=0.0, commission_per_unit=0.0)
        runner = Runner(executor=ExecutionSimulator(config=exec_cfg))
        result = runner.run(strat, data, initial_cash=100_000.0)

        def cagr_from_equity(eq):
            if len(eq) < 2:
                return 0.0
            total_ret = eq[-1] / eq[0]
            years = len(eq) / 252.0
            if years <= 0:
                return 0.0
            return total_ret ** (1 / years) - 1

        np_cagr = cagr_from_equity(np_equity[max(90, 100, 200):])
        engine_eq = result.equity_curve.to_numpy()
        engine_cagr = cagr_from_equity(engine_eq[max(90, 100, 200):])

        # G7 spec bar: ±3 pp CAGR
        assert abs(np_cagr - engine_cagr) < 0.03, (
            f"numpy ref CAGR {np_cagr:.4%} vs engine CAGR {engine_cagr:.4%} "
            f"diff {np_cagr - engine_cagr:.4%}"
        )
