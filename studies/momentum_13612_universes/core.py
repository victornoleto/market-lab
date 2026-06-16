"""Pure monthly 1/3/6/12 cross-sectional momentum engine.

This study deliberately separates the raw 13612 ranking effect from HAA's TIP
canary and defensive sleeve. At each month-end it ranks the configured universe
by equal-weighted 1, 3, 6 and 12 month total returns, holds the top-N assets at
equal weight, and applies those weights only to subsequent daily returns. The
ranking signal and monthly cadence are anchored in `[stocks_on_the_move, p.60]`
and `[stocks_on_the_move, p.98-99]`; the shifted-weight simulation prevents the
look-ahead class described in `[advances_fin_ml, p.31-34]`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from market_lab.backtest.metrics.performance import (
    cagr,
    calmar,
    max_drawdown,
    sharpe,
    sortino,
    volatility,
)


TRADING_DAYS_PER_YEAR = 252
DEFAULT_START_VALUE = 10_000.0


@dataclass(frozen=True)
class Momentum13612Config:
    """Specification for a pure 13612 top-N rotation.

    ``lookback_months=(1, 3, 6, 12)`` uses full 12-month history before an asset
    can receive a finite score. ``top_n`` is explicit so robustness grids pay the
    multiple-testing cost downstream `[advances_fin_ml, p.273-275]`.
    """

    name: str
    assets: tuple[str, ...]
    top_n: int = 10
    lookback_months: tuple[int, int, int, int] = (1, 3, 6, 12)
    min_assets: int | None = None

    def __post_init__(self) -> None:
        if self.top_n <= 0:
            raise ValueError("top_n must be positive")
        if not self.assets:
            raise ValueError("assets cannot be empty")
        if any(month <= 0 for month in self.lookback_months):
            raise ValueError("lookback_months must be positive")
        if len(set(self.lookback_months)) != len(self.lookback_months):
            raise ValueError("lookback_months must be unique")

    @property
    def min_required_assets(self) -> int:
        return self.min_assets or self.top_n


def canonicalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with uppercase ticker columns for stable matching."""
    out = frame.copy()
    out.columns = [str(col).upper() for col in out.columns]
    return out


def momentum_13612u(
    monthly_prices: pd.DataFrame,
    assets: Iterable[str],
    lookback_months: tuple[int, ...] = (1, 3, 6, 12),
) -> pd.DataFrame:
    """Equal-weighted 1/3/6/12-month return momentum.

    All lookback components must exist. This enforces the 13-month minimum
    history convention and avoids implicitly favoring younger listings in a
    cross-sectional rank `[stocks_on_the_move, p.60]`.
    """
    assets_tuple = tuple(str(asset).upper() for asset in assets)
    prices = canonicalize_columns(monthly_prices)
    scores = pd.DataFrame(index=prices.index, columns=assets_tuple, dtype=float)
    for asset in assets_tuple:
        if asset not in prices.columns:
            continue
        p = prices[asset].astype(float)
        components = [p / p.shift(months) - 1.0 for months in lookback_months]
        scores[asset] = pd.concat(components, axis=1).mean(axis=1, skipna=False)
    return scores


def rank_scores(scores: pd.Series) -> list[str]:
    """Return symbols ranked by score desc, breaking ties alphabetically."""
    clean = scores.dropna().astype(float)
    ranked = sorted(clean.items(), key=lambda item: (-float(item[1]), str(item[0])))
    return [str(symbol) for symbol, _score in ranked]


def monthly_top_n_weights(prices: pd.DataFrame, config: Momentum13612Config) -> pd.DataFrame:
    """Build month-end pure top-N target weights.

    There is intentionally no cash or absolute-momentum filter here. Even if all
    scores are negative, the strategy holds the least-bad top-N names so the test
    isolates the requested cross-sectional 13612 effect.
    """
    daily = canonicalize_columns(prices).sort_index()
    assets = tuple(str(asset).upper() for asset in config.assets)
    available = [asset for asset in assets if asset in daily.columns]
    if len(available) < config.min_required_assets:
        raise KeyError(
            f"{config.name}: only {len(available)} requested assets are present; "
            f"min_required_assets={config.min_required_assets}"
        )

    monthly = daily[available].resample("ME").last()
    scores = momentum_13612u(monthly, available, config.lookback_months)
    weights = pd.DataFrame(0.0, index=monthly.index, columns=available)

    for rebalance_date in monthly.index:
        ranked = rank_scores(scores.loc[rebalance_date])
        if len(ranked) < config.min_required_assets:
            continue
        chosen = ranked[: config.top_n]
        slot_weight = 1.0 / config.top_n
        for asset in chosen:
            weights.loc[rebalance_date, asset] = slot_weight
    return weights


def daily_weights_from_monthly(
    prices: pd.DataFrame, monthly_weights: pd.DataFrame
) -> pd.DataFrame:
    """Forward-fill month-end target weights onto the daily price index."""
    daily_index = pd.DatetimeIndex(prices.index)
    weights = monthly_weights.reindex(daily_index, method="ffill").fillna(0.0)
    return weights.reindex(columns=monthly_weights.columns, fill_value=0.0)


def simulate_momentum_gross(
    prices: pd.DataFrame, config: Momentum13612Config
) -> tuple[pd.Series, pd.DataFrame]:
    """Simulate gross daily returns using previous weights times current returns."""
    daily = canonicalize_columns(prices).sort_index()
    monthly_weights = monthly_top_n_weights(daily, config)
    daily_weights = daily_weights_from_monthly(daily, monthly_weights)
    asset_returns = daily[daily_weights.columns].pct_change(fill_method=None).fillna(0.0)
    gross = (daily_weights.shift(1).fillna(0.0) * asset_returns).sum(axis=1)
    active = daily_weights.sum(axis=1) > 0.0
    if not active.any():
        return gross.iloc[0:0].rename(config.name), daily_weights
    first_signal = active[active].index[0]
    gross = gross[gross.index >= first_signal]
    gross.name = config.name
    return gross, daily_weights


def simulate_momentum_holdings_loop(
    prices: pd.DataFrame, config: Momentum13612Config
) -> pd.Series:
    """Independent holdings-loop gross-return reference for cross-checks."""
    daily = canonicalize_columns(prices).sort_index()
    monthly_weights = monthly_top_n_weights(daily, config)
    daily_weights = daily_weights_from_monthly(daily, monthly_weights)
    asset_returns = daily[daily_weights.columns].pct_change(fill_method=None).fillna(0.0)

    current_weights = pd.Series(0.0, index=daily_weights.columns)
    returns: list[float] = []
    dates: list[pd.Timestamp] = []
    active_seen = False
    for current_date in daily.index:
        daily_return = float((current_weights * asset_returns.loc[current_date]).sum())
        if active_seen:
            returns.append(daily_return)
            dates.append(pd.Timestamp(current_date))

        target = daily_weights.loc[current_date].astype(float)
        if target.sum() > 0.0:
            active_seen = True
        if active_seen:
            current_weights = target

    out = pd.Series(returns, index=pd.DatetimeIndex(dates), name=config.name)
    return out


def equity_from_returns(returns: pd.Series, start_value: float = DEFAULT_START_VALUE) -> pd.Series:
    """Compounded equity curve from daily returns."""
    clean = returns.dropna().astype(float)
    if clean.empty:
        return pd.Series(dtype=float, name="equity")
    start = pd.Series([start_value], index=[clean.index[0] - pd.Timedelta(days=1)])
    compounded = (1.0 + clean).cumprod() * start_value
    equity = pd.concat([start, compounded])
    equity.name = "equity"
    return equity


def metrics_from_returns(
    returns: pd.Series, periods_per_year: int = TRADING_DAYS_PER_YEAR
) -> dict[str, float | str]:
    """Standard performance metrics for a daily-return series."""
    clean = returns.dropna().astype(float)
    if clean.empty:
        return {
            "start": "n/a",
            "end": "n/a",
            "n_obs": 0,
            "years": 0.0,
            "cagr": 0.0,
            "mdd": 0.0,
            "vol": 0.0,
            "sharpe": 0.0,
            "sortino": 0.0,
            "calmar": 0.0,
            "terminal": 1.0,
        }
    equity = equity_from_returns(clean, start_value=1.0)
    years = len(clean) / periods_per_year
    return {
        "start": str(clean.index[0].date()),
        "end": str(clean.index[-1].date()),
        "n_obs": int(len(clean)),
        "years": float(years),
        "cagr": float(cagr(equity, periods_per_year)),
        "mdd": -float(max_drawdown(equity)),
        "vol": float(volatility(clean, periods_per_year)),
        "sharpe": float(sharpe(clean, periods_per_year)),
        "sortino": float(sortino(clean, periods_per_year)),
        "calmar": float(calmar(equity, periods_per_year)),
        "terminal": float(equity.iloc[-1]),
    }
