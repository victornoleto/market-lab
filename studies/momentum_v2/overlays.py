"""Moving-average overlays and staggered offsets for the evolution phase.

Ported from ``studies/momentum_13612_universes/run_stocks_evolution.py``. These
are stress diagnostics applied to broad-phase finalists, not free winner-picking
parameters `[advances_fin_ml, p.273-275]`. The market 200-day regime gate and
stock 100-day trend filter follow Clenow `[stocks_on_the_move, p.66-67,
p.81-82, p.98-99]`; daily market cash rotation is also a Gayed-style
volatility-regime test `[leverage_for_the_long_run, p.9, p.13, p.16]`.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Literal

import numpy as np
import pandas as pd

from studies.momentum_v2.core import (
    TRADING_DAYS_PER_YEAR,
    EligibleByDate,
    ScoreBundle,
    SimulationResult,
    StrategyConfig,
    canonicalize_columns,
    daily_weights_from_monthly,
    eligible_assets_for_date,
    rank_scores,
    turnover_diagnostics,
)


def vol_target_returns(
    returns: pd.Series,
    target_vol: float = 0.15,
    lookback_days: int = 63,
    max_leverage: float = 1.0,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> pd.Series:
    """Scale a daily-return stream to a target annualized volatility (de-risk only).

    Exposure on day *t* uses the realized vol of the trailing ``lookback_days``
    returns known **as of t-1** (``.shift(1)``), so there is no look-ahead
    `[advances_fin_ml, p.31-34]`. Scale is capped at ``max_leverage`` (default
    1.0 = never lever up; only cut exposure when vol is high), with the unused
    fraction implicitly in cash at 0%. Volatility scaling follows
    `[systematic_trading, p.137-148]`.
    """
    clean = returns.dropna().astype(float)
    if clean.empty:
        return clean
    realized = clean.rolling(lookback_days, min_periods=lookback_days).std() * np.sqrt(periods_per_year)
    scale = (target_vol / realized.replace(0.0, np.nan)).clip(upper=max_leverage)
    scale = scale.shift(1).fillna(0.0)
    out = (clean * scale).rename(f"{returns.name}_vt{int(round(target_vol * 100))}")
    return out

OverlayMode = Literal[
    "none",
    "market_sma200_monthly",
    "market_sma200_daily",
    "stock_sma100",
    "market_sma200_monthly_stock_sma100",
    "market_sma200_daily_stock_sma100",
]
OffsetMode = Literal["fixed", "staggered"]

OVERLAYS: tuple[OverlayMode, ...] = (
    "none",
    "market_sma200_monthly",
    "market_sma200_daily",
    "stock_sma100",
    "market_sma200_monthly_stock_sma100",
    "market_sma200_daily_stock_sma100",
)
OFFSET_MODES: tuple[OffsetMode, ...] = ("fixed", "staggered")


def overlay_uses_stock_filter(overlay: OverlayMode) -> bool:
    return "stock_sma100" in overlay


def overlay_uses_monthly_market(overlay: OverlayMode) -> bool:
    return "market_sma200_monthly" in overlay


def overlay_uses_daily_market(overlay: OverlayMode) -> bool:
    return "market_sma200_daily" in overlay


def market_regime(
    benchmark_prices: pd.DataFrame, daily_index: pd.DatetimeIndex
) -> tuple[pd.Series, pd.Series]:
    """SPY > SMA200 regime flags for daily and month-end overlays."""
    spy_col = "SPY" if "SPY" in benchmark_prices.columns else benchmark_prices.columns[0]
    spy = benchmark_prices[spy_col].astype(float).sort_index()
    sma = spy.rolling(200, min_periods=200).mean()
    daily = (spy > sma).reindex(daily_index, method="ffill").fillna(False).astype(bool)
    monthly = daily.resample("ME").last().astype(bool)
    return daily, monthly


def stock_trend_ok(prices: pd.DataFrame, window_days: int = 100) -> pd.DataFrame:
    """Per-stock price > SMA100 filter used as a buy-eligibility screen."""
    daily = canonicalize_columns(prices).sort_index().astype(float)
    sma = daily.rolling(window_days, min_periods=window_days).mean()
    return (daily > sma).resample("ME").last().fillna(False).astype(bool)


def monthly_weights_with_overlay(
    bundle: ScoreBundle,
    config: StrategyConfig,
    overlay: OverlayMode,
    monthly_market_ok: pd.Series,
    monthly_stock_ok: pd.DataFrame,
    eligible_by_date: EligibleByDate | None = None,
) -> pd.DataFrame:
    """Build monthly weights with optional SPY/stock trend filters."""
    assets = [a.upper() for a in config.assets if a.upper() in bundle.monthly_prices.columns]
    scores = bundle.scores[config.score_mode].reindex(columns=assets)
    monthly_vol = bundle.monthly_vol.reindex(columns=assets)
    weights = pd.DataFrame(0.0, index=scores.index, columns=assets)
    rebalance_dates: list[pd.Timestamp] = []

    for rebalance_date in scores.index:
        if (pd.Timestamp(rebalance_date).month - 1 - config.rebalance_offset) % config.rebalance_months != 0:
            continue
        rebalance_dates.append(pd.Timestamp(rebalance_date))
        if overlay_uses_monthly_market(overlay) and not bool(
            monthly_market_ok.reindex([rebalance_date]).fillna(False).iloc[0]
        ):
            continue
        row = scores.loc[rebalance_date].copy()
        eligible = eligible_assets_for_date(eligible_by_date, pd.Timestamp(rebalance_date))
        if eligible is not None:
            if not eligible:
                continue
            row = row.where(row.index.to_series().astype(str).str.upper().isin(eligible), np.nan)
        if overlay_uses_stock_filter(overlay):
            ok = monthly_stock_ok.reindex(index=[rebalance_date], columns=assets).fillna(False).iloc[0]
            row = row.where(ok.astype(bool), np.nan)
        ranked = rank_scores(row)
        if config.absolute_filter:
            ranked = [asset for asset in ranked if float(row[asset]) > 0.0]
        chosen = ranked[: config.top_n]
        if not chosen:
            continue
        if config.weight_mode == "inverse_vol":
            vol = monthly_vol.loc[rebalance_date, chosen].astype(float).replace(0.0, np.nan)
            inv = (1.0 / vol).replace([np.inf, -np.inf], np.nan).dropna()
            if len(inv) == len(chosen) and float(inv.sum()) > 0.0:
                for asset, value in (inv / inv.sum()).items():
                    weights.loc[rebalance_date, str(asset)] = float(value)
                continue
        slot_weight = 1.0 / config.top_n
        for asset in chosen:
            weights.loc[rebalance_date, asset] = slot_weight
    if not rebalance_dates:
        return weights.iloc[0:0]
    return weights.loc[pd.DatetimeIndex(rebalance_dates)]


def simulate_evolved(
    prices: pd.DataFrame,
    bundle: ScoreBundle,
    config: StrategyConfig,
    overlay: OverlayMode,
    offset_mode: OffsetMode,
    daily_market_ok: pd.Series,
    monthly_market_ok: pd.Series,
    monthly_stock_ok: pd.DataFrame,
    eligible_by_date: EligibleByDate | None = None,
) -> SimulationResult:
    """Simulate one evolved finalist with fixed or staggered offsets + overlay."""
    daily = canonicalize_columns(prices).sort_index()
    offsets = range(config.rebalance_months) if offset_mode == "staggered" else (config.rebalance_offset,)
    sleeve_frames: list[pd.DataFrame] = []
    for offset in offsets:
        cfg = replace(config, rebalance_offset=offset)
        monthly = monthly_weights_with_overlay(
            bundle,
            cfg,
            overlay,
            monthly_market_ok=monthly_market_ok,
            monthly_stock_ok=monthly_stock_ok,
            eligible_by_date=eligible_by_date,
        )
        sleeve = daily_weights_from_monthly(daily, monthly)
        if overlay_uses_daily_market(overlay):
            sleeve = sleeve.where(daily_market_ok.reindex(sleeve.index).fillna(False), 0.0)
        sleeve_frames.append(sleeve)

    columns = sorted({column for frame in sleeve_frames for column in frame.columns})
    daily_weights = pd.DataFrame(0.0, index=daily.index, columns=columns)
    for frame in sleeve_frames:
        daily_weights = daily_weights.add(
            frame.reindex(index=daily.index, columns=columns, fill_value=0.0).fillna(0.0),
            fill_value=0.0,
        )
    daily_weights /= float(len(sleeve_frames))
    asset_returns = daily[daily_weights.columns].pct_change(fill_method=None).fillna(0.0)
    gross = (daily_weights.shift(1).fillna(0.0) * asset_returns).sum(axis=1)
    active = daily_weights.sum(axis=1) > 0.0
    if not active.any():
        empty = pd.Series(dtype=float, name=config.name)
        return SimulationResult(empty, pd.DataFrame(), pd.DataFrame(), turnover_diagnostics(pd.DataFrame(), pd.DatetimeIndex([])))
    first_signal = active[active].index[0]
    returns = gross[gross.index >= first_signal].rename(config.name)
    daily_weights = daily_weights.loc[returns.index]
    changed = daily_weights.diff().abs().sum(axis=1) > 1e-12
    if len(changed):
        changed.iloc[0] = daily_weights.iloc[0].sum() > 1e-12
    rebalance_weights = daily_weights.loc[changed]
    return SimulationResult(
        returns=returns,
        daily_weights=daily_weights,
        rebalance_weights=rebalance_weights,
        turnover=turnover_diagnostics(rebalance_weights, returns.index),
    )
