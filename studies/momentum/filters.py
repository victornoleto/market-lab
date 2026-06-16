"""Configurable universe filters for momentum screens."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd


@dataclass(frozen=True)
class FilterConfig:
    """Configurable filter thresholds for one universe slice."""

    min_history_months: int = 36
    min_price: float = 5.0
    min_median_dollar_volume: float = 1_000_000.0
    liquidity_lookback_days: int = 252
    min_trading_days_per_year: int = 180
    max_stale_days: int = 14

    @classmethod
    def from_dict(cls, raw: dict) -> "FilterConfig":
        return cls(
            min_history_months=int(raw.get("min_history_months", cls.min_history_months)),
            min_price=float(raw.get("min_price", cls.min_price)),
            min_median_dollar_volume=float(
                raw.get("min_median_dollar_volume", cls.min_median_dollar_volume)
            ),
            liquidity_lookback_days=int(
                raw.get("liquidity_lookback_days", cls.liquidity_lookback_days)
            ),
            min_trading_days_per_year=int(
                raw.get("min_trading_days_per_year", cls.min_trading_days_per_year)
            ),
            max_stale_days=int(raw.get("max_stale_days", cls.max_stale_days)),
        )


@dataclass(frozen=True)
class FilterResult:
    prices: pd.DataFrame
    volumes: pd.DataFrame
    metadata: pd.DataFrame
    diagnostics: pd.DataFrame


def apply_filters(
    prices: pd.DataFrame,
    volumes: pd.DataFrame,
    metadata: pd.DataFrame,
    config: FilterConfig,
    *,
    as_of: date | None = None,
) -> FilterResult:
    """Apply history, liquidity, stale and price filters."""
    if prices.empty:
        return FilterResult(prices, volumes, metadata, pd.DataFrame())
    clean_prices = prices.sort_index().astype(float)
    clean_volumes = volumes.reindex_like(clean_prices).astype(float)
    effective_as_of = pd.Timestamp(as_of) if as_of else pd.Timestamp(clean_prices.index.max())
    rows: list[dict[str, object]] = []

    for symbol in clean_prices.columns:
        series = clean_prices[symbol].dropna()
        if series.empty:
            rows.append(_diag(symbol, False, "no_price_data"))
            continue
        first = pd.Timestamp(series.index.min())
        last = pd.Timestamp(series.index.max())
        history_months = (last - first).days / 30.4375
        years = max((last - first).days / 365.25, 1e-9)
        obs_per_year = len(series) / years
        last_price = float(series.iloc[-1])
        stale_days = int((effective_as_of - last).days)
        vol = clean_volumes[symbol].reindex(series.index)
        dollar_volume = (series * vol).dropna()
        recent_dollar_volume = dollar_volume.tail(config.liquidity_lookback_days)
        median_dollar_volume = (
            float(recent_dollar_volume.median()) if not recent_dollar_volume.empty else 0.0
        )
        reasons: list[str] = []
        if history_months < config.min_history_months:
            reasons.append("history")
        if last_price < config.min_price:
            reasons.append("price")
        if median_dollar_volume < config.min_median_dollar_volume:
            reasons.append("liquidity")
        if obs_per_year < config.min_trading_days_per_year:
            reasons.append("sparse")
        if stale_days > config.max_stale_days:
            reasons.append("stale")
        rows.append(
            {
                "yf_symbol": symbol,
                "pass_filter": not reasons,
                "reason": ",".join(reasons) if reasons else "pass",
                "first_date": first.date().isoformat(),
                "last_date": last.date().isoformat(),
                "history_months": history_months,
                "n_obs": int(len(series)),
                "obs_per_year": obs_per_year,
                "last_price": last_price,
                "stale_days": stale_days,
                "median_dollar_volume": median_dollar_volume,
            }
        )
    diagnostics = pd.DataFrame(rows).sort_values("yf_symbol")
    keep = diagnostics.loc[diagnostics["pass_filter"], "yf_symbol"].astype(str).tolist()
    filtered_prices = clean_prices.reindex(columns=keep).dropna(how="all")
    filtered_volumes = clean_volumes.reindex(index=filtered_prices.index, columns=keep)
    filtered_metadata = metadata[metadata["yf_symbol"].isin(keep)].copy()
    return FilterResult(filtered_prices, filtered_volumes, filtered_metadata, diagnostics)


def _diag(symbol: str, passed: bool, reason: str) -> dict[str, object]:
    return {"yf_symbol": symbol, "pass_filter": passed, "reason": reason}
