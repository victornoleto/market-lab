"""Core simulator for the weekly momentum study.

Rules implemented here:

* rank assets by adjusted-close return over ``lookback_days``;
* compute the signal on Thursday close by default;
* hold equal-weight top-K, with the initial config using ``top_k=1``;
* if the new top asset is already held, do nothing;
* if the top asset changes, sell after ``sell_delay_days`` trading bars and buy
  after the configured settlement delay.
* if ``require_positive_momentum`` is true and every ranked asset has return
  ``<= 0``, target cash (or ``defensive_asset`` if configured and available).
* if ``market_filter_sma_days`` is set, only hold risk assets when the market
  filter series is above its SMA at signal time.

The model is a close-to-close research proxy because Tiingo adjusted-close is
the canonical cached series in this repo. A target that becomes effective on a
Monday is applied to that Monday's close-to-close return; this approximates a
Monday execution with daily bars and should be cross-checked with open/close
data before any operational interpretation. Momentum ranking citation:
``[stocks_on_the_move, p.60]``. Weekly cadence citation:
``[stocks_on_the_move, p.98-99]``.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable
from typing import Literal

import pandas as pd

from studies._shared.scoring import compute_metrics as _compute_metrics

MarketFilterType = Literal["none", "sma", "ema"]


@dataclass(frozen=True)
class WeeklyMomentumConfig:
    """Configuration for cross-sectional weekly momentum.

    Default timing is honest for daily data: compute the signal on Thursday
    close, sell on Friday, and buy on Monday if ``settlement_delay_days=0``.
    ``settlement_delay_days=1`` keeps the portfolio in cash on Monday and buys
    Tuesday. This avoids using Friday close to decide a Friday sale.
    """

    lookback_days: int = 4
    signal_weekday: int = 3  # Thursday, 0=Monday ... 4=Friday
    sell_delay_days: int = 1
    top_k: int = 1
    settlement_delay_days: int = 0
    allow_negative_momentum: bool = False
    defensive_asset: str | None = None
    market_filter_type: MarketFilterType = "none"
    market_filter_days: int | None = None
    market_filter_symbol: str = "SPY"
    initial_cash: float = 10_000.0

    def __post_init__(self) -> None:
        if self.lookback_days < 1:
            raise ValueError("lookback_days must be >= 1")
        if self.top_k < 1:
            raise ValueError("top_k must be >= 1")
        if self.sell_delay_days < 1:
            raise ValueError("sell_delay_days must be >= 1 for daily-bar honesty")
        if self.settlement_delay_days < 0:
            raise ValueError("settlement_delay_days must be >= 0")
        if not 0 <= self.signal_weekday <= 6:
            raise ValueError("signal_weekday must be in 0..6")
        if self.market_filter_type not in {"none", "sma", "ema"}:
            raise ValueError("market_filter_type must be 'none', 'sma', or 'ema'")
        if self.market_filter_type == "none" and self.market_filter_days is not None:
            raise ValueError("market_filter_days must be None when market_filter_type='none'")
        if self.market_filter_type != "none" and (
            self.market_filter_days is None or self.market_filter_days < 2
        ):
            raise ValueError("market_filter_days must be >= 2 when market filter is enabled")
        if self.initial_cash <= 0:
            raise ValueError("initial_cash must be > 0")

    @property
    def require_positive_momentum(self) -> bool:
        """Backwards-compatible alias for the inverted public parameter."""
        return not self.allow_negative_momentum


@dataclass(frozen=True)
class WeeklyMomentumResult:
    returns: pd.Series
    equity: pd.Series
    weights: pd.DataFrame
    trades: pd.DataFrame
    metrics: dict[str, float]


def momentum_scores(prices: pd.DataFrame, asof: pd.Timestamp, lookback_days: int) -> pd.Series:
    """Return cross-sectional trailing returns as of ``asof``.

    Score = ``price_t / price_{t-lookback_days} - 1``. Assets lacking either
    endpoint are excluded. Citation: cross-sectional momentum ranking baseline
    ``[stocks_on_the_move, p.60]``.
    """
    if lookback_days < 1:
        raise ValueError("lookback_days must be >= 1")

    hist = prices.loc[:pd.Timestamp(asof)]
    if len(hist) <= lookback_days:
        return pd.Series(dtype=float)
    scores = hist.iloc[-1] / hist.iloc[-(lookback_days + 1)] - 1.0
    scores = scores.replace([float("inf"), float("-inf")], pd.NA).dropna()
    return scores.astype(float).sort_values(ascending=False)


def top_symbols(scores: pd.Series, top_k: int) -> list[str]:
    """Return deterministic top-K symbols, breaking score ties alphabetically."""
    if top_k < 1:
        raise ValueError("top_k must be >= 1")
    if scores.empty:
        return []
    ranked = sorted(scores.items(), key=lambda item: (-float(item[1]), str(item[0])))
    return [str(symbol) for symbol, _ in ranked[:top_k]]


def target_symbols(
    scores: pd.Series,
    top_k: int,
    allow_negative_momentum: bool = False,
    defensive_asset: str | None = None,
    available_symbols: set[str] | None = None,
    require_positive_momentum: bool | None = None,
) -> list[str]:
    """Return desired holdings for the next cycle.

    If every score is non-positive and ``allow_negative_momentum`` is disabled,
    the strategy goes to cash by returning ``[]``. If ``defensive_asset`` is set
    and available in the price frame, that asset is returned instead.
    Absolute-momentum cash filters are a defensive overlay on cross-sectional
    momentum, consistent with trend/risk filters used to avoid bear regimes
    `[stocks_on_the_move, p.66-67, p.81]`.
    """
    if require_positive_momentum is not None:
        allow_negative_momentum = not require_positive_momentum
    if scores.empty:
        return []
    if not allow_negative_momentum and float(scores.max()) <= 0.0:
        if defensive_asset is None:
            return []
        if available_symbols is None or defensive_asset in available_symbols:
            return [defensive_asset]
        return []
    return top_symbols(scores, top_k)


def trading_date_after(
    index: pd.DatetimeIndex,
    after: pd.Timestamp,
    bars_after: int,
) -> pd.Timestamp | None:
    """Trading date ``bars_after`` bars after ``after``.

    ``bars_after=1`` returns the next trading date. ``bars_after=2`` skips one
    trading date and returns the second one.
    """
    if bars_after < 1:
        raise ValueError("bars_after must be >= 1")
    future = index[index > pd.Timestamp(after)]
    offset = bars_after - 1
    if len(future) <= offset:
        return None
    return pd.Timestamp(future[offset])


def simulate_weekly_momentum(
    prices: pd.DataFrame,
    config: WeeklyMomentumConfig | None = None,
    market_filter_prices: pd.Series | None = None,
    universe_by_date: Callable[[pd.Timestamp], set[str]] | None = None,
) -> WeeklyMomentumResult:
    """Simulate the weekly cross-sectional momentum strategy.

    Input prices should be adjusted close, one column per ticker. The optional
    ``universe_by_date`` filters the ranking universe at signal time, allowing a
    point-in-time membership approximation while preserving the same cached
    price frame. This is still not a delisted survivorship-free feed.
    """
    cfg = config or WeeklyMomentumConfig()
    clean_prices = _prepare_prices(prices)
    if clean_prices.empty:
        raise ValueError("prices must contain at least one non-empty asset series")

    returns = clean_prices.pct_change(fill_method=None).fillna(0.0)
    weights = pd.DataFrame(0.0, index=clean_prices.index, columns=clean_prices.columns)
    market_filter = _prepare_market_filter(market_filter_prices, clean_prices.index)
    market_filter_line = _market_filter_line(market_filter, cfg)

    current: list[str] = []
    pending_target: list[str] = []
    pending_sell_date: pd.Timestamp | None = None
    pending_buy_date: pd.Timestamp | None = None
    trade_rows: list[dict[str, object]] = []

    for ts in clean_prices.index:
        if pending_buy_date is not None and ts >= pending_buy_date:
            if pending_target:
                current = list(pending_target)
                trade_rows.append({
                    "date": ts,
                    "action": "buy",
                    "symbols": ",".join(current),
                })
            pending_target = []
            pending_buy_date = None

        if current:
            # If a held symbol has no price on this date, keep that sleeve in
            # cash rather than assuming a zero-return stale mark. Delisting
            # returns still require a survivorship-free feed `[advances_fin_ml, p.208-211]`.
            live = [sym for sym in current if sym in weights.columns and pd.notna(clean_prices.loc[ts, sym])]
            if live:
                weights.loc[ts, live] = 1.0 / len(current)

        if pending_sell_date is not None and ts >= pending_sell_date:
            if current:
                trade_rows.append({
                    "date": ts,
                    "action": "sell",
                    "symbols": ",".join(current),
                })
            current = []
            pending_sell_date = None
            if pending_target:
                buy_date = trading_date_after(
                    clean_prices.index,
                    ts,
                    bars_after=1 + cfg.settlement_delay_days,
                )
                if buy_date is not None:
                    pending_buy_date = buy_date

        if ts.weekday() != cfg.signal_weekday:
            continue

        available_symbols = _available_symbols(clean_prices.columns, ts, universe_by_date)
        signal_prices = clean_prices[list(available_symbols)] if available_symbols else clean_prices.iloc[:, 0:0]
        scores = momentum_scores(signal_prices, ts, cfg.lookback_days)
        if not market_filter_allows_risk(market_filter, market_filter_line, ts):
            target = _defensive_target(cfg.defensive_asset, set(clean_prices.columns))
        else:
            target = target_symbols(
                scores,
                top_k=cfg.top_k,
                allow_negative_momentum=cfg.allow_negative_momentum,
                defensive_asset=cfg.defensive_asset,
                available_symbols=available_symbols,
            )
        if target == current:
            continue
        if not target and not current:
            continue

        sell_date = trading_date_after(clean_prices.index, ts, bars_after=cfg.sell_delay_days)
        if sell_date is not None:
            pending_target = target
            pending_sell_date = sell_date

    strategy_returns = (weights * returns).sum(axis=1).rename("weekly_momentum_return")
    equity = (1.0 + strategy_returns).cumprod() * cfg.initial_cash
    equity.name = "weekly_momentum_equity"
    trades = pd.DataFrame(trade_rows, columns=["date", "action", "symbols"])
    metrics = compute_basic_metrics(equity, strategy_returns)
    return WeeklyMomentumResult(
        returns=strategy_returns,
        equity=equity,
        weights=weights,
        trades=trades,
        metrics=metrics,
    )


def _available_symbols(
    columns: pd.Index,
    ts: pd.Timestamp,
    universe_by_date: Callable[[pd.Timestamp], set[str]] | None,
) -> set[str]:
    all_symbols = {str(symbol) for symbol in columns}
    if universe_by_date is None:
        return all_symbols
    return all_symbols & {str(symbol) for symbol in universe_by_date(pd.Timestamp(ts))}


def compute_basic_metrics(equity: pd.Series, returns: pd.Series) -> dict[str, float]:
    """Reuse the canonical study metric helper for quick iteration."""
    return _compute_metrics(equity, returns)


def market_filter_allows_risk(
    market_filter: pd.Series | None,
    market_filter_line: pd.Series | None,
    ts: pd.Timestamp,
) -> bool:
    """True when the market regime filter permits risk-on holdings.

    SPY/SMA regime filters are standard trend-risk overlays; this study uses
    them as a crash-risk filter, consistent with trend filters in Clenow's stock
    momentum framework `[stocks_on_the_move, p.66-67, p.81]`.
    """
    if market_filter is None or market_filter_line is None:
        return True
    ts = pd.Timestamp(ts)
    if ts not in market_filter.index or ts not in market_filter_line.index:
        return False
    price = market_filter.loc[ts]
    line = market_filter_line.loc[ts]
    if pd.isna(price) or pd.isna(line):
        return False
    return bool(float(price) > float(line))


def _prepare_prices(prices: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise TypeError("prices index must be a DatetimeIndex")
    out = prices.copy()
    out.index = pd.DatetimeIndex(out.index).tz_localize(None) if out.index.tz else out.index
    out = out.sort_index()
    out = out[~out.index.duplicated(keep="last")]
    out = out.apply(pd.to_numeric, errors="coerce")
    out = out.dropna(axis=1, how="all")
    return out


def _prepare_market_filter(
    market_filter_prices: pd.Series | None,
    index: pd.DatetimeIndex,
) -> pd.Series | None:
    if market_filter_prices is None:
        return None
    s = pd.to_numeric(market_filter_prices.copy(), errors="coerce")
    if not isinstance(s.index, pd.DatetimeIndex):
        raise TypeError("market_filter_prices index must be a DatetimeIndex")
    s.index = pd.DatetimeIndex(s.index).tz_localize(None) if s.index.tz else s.index
    return s.sort_index().reindex(index).ffill()


def _market_filter_line(
    market_filter: pd.Series | None,
    config: WeeklyMomentumConfig,
) -> pd.Series | None:
    if market_filter is None or config.market_filter_type == "none":
        return None
    if config.market_filter_type == "sma":
        return market_filter.rolling(config.market_filter_days).mean()
    return market_filter.ewm(span=config.market_filter_days, adjust=False).mean()


def _defensive_target(defensive_asset: str | None, available_symbols: set[str]) -> list[str]:
    if defensive_asset is not None and defensive_asset in available_symbols:
        return [defensive_asset]
    return []
