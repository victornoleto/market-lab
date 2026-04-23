"""Tests for ``backtest.strategies.ranking_br``.

All tests use synthetic OHLCV — no network. The base class
:class:`MonthlyRankingStrategy` is abstract; we test it through D1/D4
concrete subclasses plus a minimal stub (``_StubRanker``) that exposes the
selection/order-emission path deterministically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.data.br_tickers import UniverseConfig
from ai_trade.backtest.engine.execution import Bar
from ai_trade.backtest.engine.portfolio import Portfolio
from ai_trade.backtest.strategies.ranking_br import (
    D1ClenowBR,
    D4LowvolMomBR,
    MonthlyRankingStrategy,
)


# ---------------------------------------------------------------------------
# Synthetic data helpers
# ---------------------------------------------------------------------------
def _build_series(
    start: str,
    periods: int,
    daily_drift: float = 0.0,
    daily_vol: float = 0.01,
    seed: int = 0,
    base_price: float = 50.0,
    volume: float = 1_000_000.0,
) -> pd.DataFrame:
    """Geometric-Brownian-ish daily OHLCV with configurable drift/vol."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range(start=start, periods=periods)
    rets = rng.normal(daily_drift, daily_vol, periods)
    prices = base_price * np.exp(np.cumsum(rets))
    df = pd.DataFrame(
        {
            "open": prices,
            "high": prices * 1.005,
            "low": prices * 0.995,
            "close": prices,
            "adj_close": prices,
            "volume": volume,
        },
        index=idx,
    )
    df.index.name = "date"
    return df


def _bars_at(ts: pd.Timestamp, data: dict[str, pd.DataFrame]) -> dict[str, Bar]:
    """Build ``{symbol: Bar}`` dict for a given timestamp from the data store."""
    bars: dict[str, Bar] = {}
    for sym, df in data.items():
        if ts not in df.index:
            continue
        row = df.loc[ts]
        bars[sym] = Bar(
            symbol=sym,
            timestamp=ts,
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=float(row["volume"]),
        )
    return bars


# ---------------------------------------------------------------------------
# Stub subclass for base-class mechanics
# ---------------------------------------------------------------------------
@dataclass
class _StubRanker(MonthlyRankingStrategy):
    """Returns a pre-specified score dict — isolates selection/order logic."""

    stub_scores: dict[str, float] = field(default_factory=dict)

    def compute_scores(self, universe, ts, bars):
        # Respect the universe: caller must have filtered the scoring set.
        return {k: v for k, v in self.stub_scores.items() if k in universe}


# ---------------------------------------------------------------------------
# Base class: rebalance trigger + selection + inertia + sector cap
# ---------------------------------------------------------------------------
class TestMonthlyTrigger:
    def test_first_bar_of_month_triggers(self):
        data = {"PETR4.SA": _build_series("2024-01-01", 60)}
        strat = _StubRanker(data=data, n_top=1)
        bars = _bars_at(pd.Timestamp("2024-01-02"), data)
        assert strat.should_rebalance(pd.Timestamp("2024-01-02"), bars) is True

    def test_second_bar_of_same_month_does_not(self):
        data = {"PETR4.SA": _build_series("2024-01-01", 60)}
        strat = _StubRanker(data=data, n_top=1)
        strat.should_rebalance(pd.Timestamp("2024-01-02"), _bars_at(pd.Timestamp("2024-01-02"), data))
        assert strat.should_rebalance(
            pd.Timestamp("2024-01-03"),
            _bars_at(pd.Timestamp("2024-01-03"), data),
        ) is False

    def test_new_month_triggers_again(self):
        data = {"PETR4.SA": _build_series("2024-01-01", 60)}
        strat = _StubRanker(data=data, n_top=1)
        strat.should_rebalance(pd.Timestamp("2024-01-02"), _bars_at(pd.Timestamp("2024-01-02"), data))
        bars_feb = _bars_at(pd.Timestamp("2024-02-01"), data)
        assert strat.should_rebalance(pd.Timestamp("2024-02-01"), bars_feb) is True


class TestSelectionAndSectorCap:
    """Use _StubRanker with known scores to verify _pick_targets logic."""

    def _setup(self, n_top=5, sector_cap=None, inertia=0.0):
        # Use 10 tickers from IBrX100 spread across sectors
        tickers = [
            "PETR4.SA", "VALE3.SA",         # Energy, Materials
            "ITUB4.SA", "BBDC4.SA",         # Financials, Financials
            "WEGE3.SA", "EMBR3.SA",         # Industrials, Industrials
            "ABEV3.SA", "JBSS3.SA",         # Consumer Staples, Consumer Staples
            "RDOR3.SA", "HAPV3.SA",         # Health Care, Health Care
        ]
        data = {t: _build_series("2023-01-01", 300, seed=i, volume=10_000_000) for i, t in enumerate(tickers)}
        # Scores descending: first ticker in list gets highest score.
        scores = {t: float(10 - i) for i, t in enumerate(tickers)}
        strat = _StubRanker(
            data=data,
            n_top=n_top,
            sector_cap_pct=sector_cap,
            position_inertia_pct=inertia,
            stub_scores=scores,
        )
        return strat, tickers

    def test_pick_top_n_no_cap(self):
        strat, tickers = self._setup(n_top=3, sector_cap=None)
        picks = strat._pick_targets(strat.stub_scores)
        assert picks == tickers[:3]

    def test_sector_cap_limits_per_sector(self):
        """With 25% sector cap and n_top=4, max per sector = floor(4*0.25)=1.
        So picks should be top-scoring across distinct sectors.
        """
        strat, tickers = self._setup(n_top=4, sector_cap=0.25)
        picks = strat._pick_targets(strat.stub_scores)
        from ai_trade.backtest.data.br_tickers import sector_of
        sectors = [sector_of(t) for t in picks]
        # No duplicate sectors in the 4 picks
        assert len(set(sectors)) == len(sectors)
        # Still 4 positions
        assert len(picks) == 4

    def test_inertia_prefers_previously_held(self):
        """When previously-held tickers all stay within the inertia pool,
        a new top-ranked name does NOT displace them.

        Setup: n_top=3, inertia=50% → inertia_pool = top 5 by score.
        Previously held = [PETR4, VALE3, ITUB4] (tickers[:3]).
        New top score goes to BBDC4 (rank 1 after boost). But PETR4/VALE3/
        ITUB4 remain in the top 5, so inertia keeps them — BBDC4 gets
        excluded despite being the single top-scored name.
        """
        strat, tickers = self._setup(n_top=3, sector_cap=None, inertia=0.5)
        strat._last_targets = tickers[:3]  # [PETR4, VALE3, ITUB4]
        new_scores = dict(strat.stub_scores)
        new_scores["BBDC4.SA"] = 20.0  # boost to rank 1
        strat.stub_scores = new_scores
        picks = strat._pick_targets(new_scores)
        assert picks == ["PETR4.SA", "VALE3.SA", "ITUB4.SA"]
        assert "BBDC4.SA" not in picks

    def test_inertia_lets_boundary_new_in_if_held_drops_out_of_pool(self):
        """Inertia only protects held tickers still in the inertia pool.
        If a held ticker drops below the pool, its slot opens up.
        """
        strat, tickers = self._setup(n_top=3, sector_cap=None, inertia=0.1)
        # inertia_cutoff = ceil(3 * 1.1) = 4 → pool = top 4
        strat._last_targets = ["PETR4.SA", "VALE3.SA", "ITUB4.SA"]
        # Crash ITUB4 to last place; promote BBDC4 to rank 1.
        new_scores = dict(strat.stub_scores)
        new_scores["ITUB4.SA"] = 0.1
        new_scores["BBDC4.SA"] = 20.0
        picks = strat._pick_targets(new_scores)
        # Pool = top 4: BBDC4 (20), PETR4 (10), VALE3 (9), WEGE3 (6).
        # held_first = [PETR4, VALE3] (ITUB4 dropped out of pool).
        # fresh = [BBDC4, WEGE3, EMBR3, ...].
        # Pick 3 → [PETR4, VALE3, BBDC4].
        assert picks == ["PETR4.SA", "VALE3.SA", "BBDC4.SA"]


class TestBaseValidation:
    def test_rejects_non_positive_n_top(self):
        with pytest.raises(ValueError, match="n_top must be > 0"):
            _StubRanker(data={}, n_top=0)

    def test_rejects_bad_sector_cap(self):
        with pytest.raises(ValueError, match="sector_cap_pct"):
            _StubRanker(data={}, n_top=5, sector_cap_pct=1.5)

    def test_rejects_negative_inertia(self):
        with pytest.raises(ValueError, match="position_inertia_pct"):
            _StubRanker(data={}, n_top=5, position_inertia_pct=-0.1)

    def test_rejects_unknown_sizing(self):
        with pytest.raises(ValueError, match="sizing"):
            _StubRanker(data={}, n_top=5, sizing="kelly")


# ---------------------------------------------------------------------------
# Lead D1 Clenow
# ---------------------------------------------------------------------------
class TestD1Clenow:
    def test_trend_filter_excludes_below_sma(self):
        """Downtrend stock (price below SMA100) is excluded from ranking."""
        up = _build_series("2023-01-01", 300, daily_drift=0.002, daily_vol=0.01, seed=1)
        down = _build_series("2023-01-01", 300, daily_drift=-0.002, daily_vol=0.01, seed=2)
        data = {"UP.SA": up, "DOWN.SA": down}
        ts = up.index[-1]
        bars = _bars_at(ts, data)
        strat = D1ClenowBR(
            data=data, n_top=2, sector_cap_pct=None, lookback=90, sma_stock_period=100,
            universe_config=UniverseConfig(min_median_notional_brl=1.0),
        )
        scores = strat.compute_scores(list(data.keys()), ts, bars)
        assert "UP.SA" in scores
        assert "DOWN.SA" not in scores, "stock below SMA100 must be filtered"

    def test_gap_filter_excludes_jumpy_stock(self):
        """Stock with a >15% single-day move is filtered out.

        Strong drift (0.004/day) + low vol (0.003) keeps both stocks
        comfortably above SMA100 so the trend filter doesn't confound
        the gap filter. Inject a one-day 20% jump in JUMPY only.
        """
        base = _build_series(
            "2023-01-01", 300, daily_drift=0.004, daily_vol=0.003, seed=10
        )
        jumpy = base.copy()
        gap_day = base.index[-50]
        # Scale the close-and-beyond by 1.20 — produces a single-day 20% jump.
        jumpy.loc[gap_day:, ["open", "high", "low", "close", "adj_close"]] *= 1.20
        data = {"CLEAN.SA": base, "JUMPY.SA": jumpy}
        ts = base.index[-1]
        bars = _bars_at(ts, data)
        strat = D1ClenowBR(
            data=data, n_top=2, sector_cap_pct=None, lookback=90, sma_stock_period=100,
            max_gap_pct=0.15,
            universe_config=UniverseConfig(min_median_notional_brl=1.0),
        )
        scores = strat.compute_scores(list(data.keys()), ts, bars)
        assert "CLEAN.SA" in scores, f"CLEAN should pass filters; got {scores}"
        assert "JUMPY.SA" not in scores, "20% gap must trip gap filter"

    def test_insufficient_history_skipped(self):
        short = _build_series("2024-03-01", 50, daily_drift=0.001, seed=20)
        long_ok = _build_series("2023-01-01", 300, daily_drift=0.001, seed=21)
        data = {"SHORT.SA": short, "LONG.SA": long_ok}
        ts = long_ok.index[-1]
        bars = _bars_at(ts, data)
        # ts not in short's index, so it won't appear in bars anyway —
        # also test with ts that IS in short: insufficient history still skipped.
        ts_short = short.index[-1]
        bars_short = _bars_at(ts_short, data)
        strat = D1ClenowBR(
            data=data, n_top=2, sector_cap_pct=None, lookback=90,
            universe_config=UniverseConfig(min_median_notional_brl=1.0),
        )
        scores = strat.compute_scores(list(data.keys()), ts_short, bars_short)
        # SHORT has only 50 bars, needs ≥ max(90, 100) — skipped
        assert "SHORT.SA" not in scores

    def test_scores_ordered_by_momentum(self):
        """Stronger uptrend → higher score."""
        strong = _build_series("2023-01-01", 300, daily_drift=0.003, daily_vol=0.005, seed=30)
        weak = _build_series("2023-01-01", 300, daily_drift=0.0005, daily_vol=0.005, seed=31)
        data = {"STRONG.SA": strong, "WEAK.SA": weak}
        ts = strong.index[-1]
        bars = _bars_at(ts, data)
        strat = D1ClenowBR(
            data=data, n_top=2, sector_cap_pct=None, lookback=90,
            universe_config=UniverseConfig(min_median_notional_brl=1.0),
        )
        scores = strat.compute_scores(list(data.keys()), ts, bars)
        assert scores["STRONG.SA"] > scores["WEAK.SA"]


# ---------------------------------------------------------------------------
# Lead D4 Low-vol + Mom hybrid
# ---------------------------------------------------------------------------
class TestD4LowvolMom:
    def test_two_stage_prefers_low_vol_within_top_momentum(self):
        """Within the top-K by momentum, the lower-vol name wins on the re-rank."""
        # Both have similar drift (so they rank high on momentum),
        # but HIGH_VOL has 2× vol of LOW_VOL.
        high_vol = _build_series("2023-01-01", 300, daily_drift=0.002, daily_vol=0.02, seed=40)
        low_vol = _build_series("2023-01-01", 300, daily_drift=0.002, daily_vol=0.005, seed=41)
        data = {"HIGH_VOL.SA": high_vol, "LOW_VOL.SA": low_vol}
        ts = high_vol.index[-1]
        bars = _bars_at(ts, data)
        strat = D4LowvolMomBR(
            data=data, n_top=2, sector_cap_pct=None,
            slope_lookback=180, pre_n=5, vol_lookback=90,
            universe_config=UniverseConfig(min_median_notional_brl=1.0),
        )
        scores = strat.compute_scores(list(data.keys()), ts, bars)
        # Scores are negative vol (higher = less vol). LOW_VOL should outrank HIGH_VOL.
        assert scores["LOW_VOL.SA"] > scores["HIGH_VOL.SA"]

    def test_only_top_momentum_survives_to_vol_stage(self):
        """Stocks outside top-pre_n by momentum are not scored at all."""
        # 3 tickers: strong, medium, weak drift. pre_n=2 → only top-2 momentum survive.
        strong = _build_series("2023-01-01", 300, daily_drift=0.003, daily_vol=0.005, seed=50)
        medium = _build_series("2023-01-01", 300, daily_drift=0.001, daily_vol=0.005, seed=51)
        weak = _build_series("2023-01-01", 300, daily_drift=0.0001, daily_vol=0.005, seed=52)
        data = {"STRONG.SA": strong, "MEDIUM.SA": medium, "WEAK.SA": weak}
        ts = strong.index[-1]
        bars = _bars_at(ts, data)
        strat = D4LowvolMomBR(
            data=data, n_top=2, sector_cap_pct=None,
            slope_lookback=180, pre_n=2, vol_lookback=60,
            universe_config=UniverseConfig(min_median_notional_brl=1.0),
        )
        scores = strat.compute_scores(list(data.keys()), ts, bars)
        assert "WEAK.SA" not in scores  # filtered out at stage 1
        assert "STRONG.SA" in scores
        assert "MEDIUM.SA" in scores


# ---------------------------------------------------------------------------
# End-to-end: Portfolio interaction via on_rebalance
# ---------------------------------------------------------------------------
class TestOrderEmission:
    def test_first_rebalance_opens_positions(self):
        strong = _build_series("2023-01-01", 300, daily_drift=0.003, daily_vol=0.005, seed=60, volume=10_000_000)
        medium = _build_series("2023-01-01", 300, daily_drift=0.002, daily_vol=0.005, seed=61, volume=10_000_000)
        data = {"PETR4.SA": strong, "VALE3.SA": medium}
        ts = strong.index[-1]
        bars = _bars_at(ts, data)
        portfolio = Portfolio(initial_cash=100_000.0)
        strat = D1ClenowBR(
            data=data, n_top=2, sector_cap_pct=None, lookback=90,
            universe_config=UniverseConfig(min_median_notional_brl=1_000_000.0),
        )
        # Force the rebalance path (base marks month consumed on first call)
        strat.should_rebalance(ts, bars)
        orders = strat.on_rebalance(ts, bars, portfolio, {})
        assert len(orders) == 2
        assert all(o.side == "buy" for o in orders)
        assert {o.symbol for o in orders} == {"PETR4.SA", "VALE3.SA"}

    def test_empty_universe_exits_all(self):
        """When no tickers pass the liquidity filter, exit everything."""
        # Very illiquid data — below universe threshold.
        data = {"ILLIQ.SA": _build_series("2023-01-01", 300, daily_drift=0.001, volume=100.0)}
        ts = data["ILLIQ.SA"].index[-1]
        bars = _bars_at(ts, data)
        portfolio = Portfolio(initial_cash=100_000.0)
        # Pretend we had a position open
        portfolio.open_position("ILLIQ.SA", "long", volume=100, price=50.0, timestamp=ts)
        strat = D1ClenowBR(
            data=data, n_top=1, sector_cap_pct=None, lookback=90,
            universe_config=UniverseConfig(min_median_notional_brl=1_000_000.0),  # too high
        )
        strat.should_rebalance(ts, bars)
        orders = strat.on_rebalance(ts, bars, portfolio, {})
        assert len(orders) == 1
        assert orders[0].side == "sell"
        assert orders[0].symbol == "ILLIQ.SA"

    def test_no_order_for_ticker_without_bar_cross_calendar(self):
        """Regression: multi-market universe where US ticker has no bar on
        a BR-trading day (e.g., 2012-01-02 US observance holiday vs BR open)
        must NOT emit a sell order for the US position — Runner raises if
        order.symbol is not in bars that timestamp.

        Scenario: portfolio holds ROST (US) and PETR4.SA (BR). Rebalance
        day has bar only for PETR4.SA. Target set = {VALE3.SA}. Strategy
        should emit sell for PETR4.SA (bar present) but NOT for ROST.
        """
        from ai_trade.backtest.engine.execution import Bar

        data = {
            "PETR4.SA": _build_series("2023-01-01", 300, daily_drift=0.002, seed=70, volume=10_000_000),
            "VALE3.SA": _build_series("2023-01-01", 300, daily_drift=0.003, seed=71, volume=10_000_000),
            "ROST": _build_series("2023-01-01", 300, daily_drift=0.001, seed=72, volume=10_000_000),
        }
        ts = data["PETR4.SA"].index[-1]
        # Build bars without ROST (simulating US holiday).
        bars = {
            "PETR4.SA": Bar(symbol="PETR4.SA", timestamp=ts,
                            open=50.0, high=50.5, low=49.5, close=50.0, volume=10_000_000),
            "VALE3.SA": Bar(symbol="VALE3.SA", timestamp=ts,
                            open=60.0, high=60.5, low=59.5, close=60.0, volume=10_000_000),
        }
        portfolio = Portfolio(initial_cash=100_000.0)
        portfolio.open_position("ROST", "long", volume=100, price=120.0, timestamp=ts)
        portfolio.open_position("PETR4.SA", "long", volume=500, price=45.0, timestamp=ts)

        strat = D1ClenowBR(
            data=data, n_top=1, sector_cap_pct=None, lookback=90,
            universe_config=UniverseConfig(min_median_notional_brl=1_000_000.0),
        )
        strat.should_rebalance(ts, bars)
        orders = strat.on_rebalance(ts, bars, portfolio, {})
        # Must not include any order for ROST (no bar).
        order_symbols = {o.symbol for o in orders}
        assert "ROST" not in order_symbols, (
            f"ROST has no bar yet strategy emitted order; got {order_symbols}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
