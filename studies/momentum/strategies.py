"""Momentum strategy simulation helpers."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal

import numpy as np
import pandas as pd

from studies.momentum.features import FeatureBundle, canonicalize_prices


ScoreMode = Literal[
    "raw_13612",
    "mom_12_1",
    "mom_3_6_12",
    "clenow_trend",
    "vol_adjusted",
    "mom_lowvol_composite",
]
WeightMode = Literal["equal", "inverse_vol", "capped_inverse_vol"]


@dataclass(frozen=True)
class StrategyConfig:
    name: str
    universe: str
    assets: tuple[str, ...]
    score_mode: ScoreMode
    top_n: int
    rebalance_months: int
    rebalance_offset: int
    weight_mode: WeightMode = "equal"
    absolute_filter: bool = False
    staggered_offsets: bool = False
    weight_cap: float = 0.25

    @property
    def mechanism(self) -> str:
        parts = [self.score_mode, self.weight_mode]
        if self.absolute_filter:
            parts.append("abs")
        if self.staggered_offsets:
            parts.append("staggered")
        return "+".join(parts)


@dataclass(frozen=True)
class SimulationResult:
    returns: pd.Series
    daily_weights: pd.DataFrame
    rebalance_weights: pd.DataFrame
    turnover: dict[str, float]


def rank_scores(scores: pd.Series) -> list[str]:
    clean = scores.dropna().astype(float)
    ranked = sorted(clean.items(), key=lambda item: (-float(item[1]), str(item[0])))
    return [str(symbol) for symbol, _score in ranked]


def is_rebalance_month(timestamp: pd.Timestamp, frequency_months: int, offset: int) -> bool:
    month_zero = pd.Timestamp(timestamp).month - 1
    return (month_zero - offset) % frequency_months == 0


def rebalance_weights_for_config(bundle: FeatureBundle, config: StrategyConfig) -> pd.DataFrame:
    assets = [asset.upper() for asset in config.assets if asset.upper() in bundle.monthly_prices.columns]
    scores = bundle.scores[config.score_mode].reindex(columns=assets)
    monthly_vol = bundle.monthly_vol.reindex(columns=assets)
    weights = pd.DataFrame(0.0, index=scores.index, columns=assets)
    for rebalance_date in scores.index:
        if not is_rebalance_month(rebalance_date, config.rebalance_months, config.rebalance_offset):
            continue
        score_row = scores.loc[rebalance_date]
        ranked = rank_scores(score_row)
        if len(ranked) < config.top_n:
            continue
        chosen = ranked[: config.top_n]
        if config.absolute_filter:
            chosen = [asset for asset in chosen if float(score_row[asset]) > 0.0]
        if not chosen:
            continue
        weights.loc[rebalance_date, chosen] = weight_vector(
            chosen,
            monthly_vol.loc[rebalance_date, chosen],
            mode=config.weight_mode,
            top_n=config.top_n,
            weight_cap=config.weight_cap,
        )
    weights = weights.loc[weights.sum(axis=1) > 0.0]
    if weights.empty:
        return weights
    used_columns = weights.columns[weights.abs().sum(axis=0) > 1e-12]
    return weights.loc[:, used_columns]


def weight_vector(
    assets: list[str],
    vol: pd.Series,
    *,
    mode: WeightMode,
    top_n: int,
    weight_cap: float,
) -> pd.Series:
    if mode == "equal":
        return pd.Series(1.0 / top_n, index=assets, dtype=float)
    inv = (1.0 / vol.astype(float).replace(0.0, np.nan)).replace([np.inf, -np.inf], np.nan)
    inv = inv.dropna()
    if len(inv) != len(assets) or float(inv.sum()) <= 0.0:
        return pd.Series(1.0 / top_n, index=assets, dtype=float)
    raw = inv / inv.sum()
    if mode == "inverse_vol":
        return raw.reindex(assets).fillna(0.0)
    if mode == "capped_inverse_vol":
        return cap_and_redistribute(raw.reindex(assets).fillna(0.0), weight_cap)
    raise ValueError(f"unknown weight mode: {mode}")


def cap_and_redistribute(weights: pd.Series, cap: float) -> pd.Series:
    """Cap weights and redistribute excess to uncapped names."""
    if cap <= 0.0 or cap >= 1.0:
        return weights / weights.sum()
    out = weights.copy().astype(float)
    for _ in range(len(out) + 1):
        over = out > cap
        if not over.any():
            total = float(out.sum())
            return out / total if total > 0.0 else out
        excess = float((out[over] - cap).sum())
        out[over] = cap
        under = ~over
        if not under.any() or float(out[under].sum()) <= 0.0:
            total = float(out.sum())
            return out / total if total > 0.0 else out
        out[under] += excess * out[under] / float(out[under].sum())
    total = float(out.sum())
    return out / total if total > 0.0 else out


def daily_weights_from_rebalances(prices: pd.DataFrame, rebalance_weights: pd.DataFrame) -> pd.DataFrame:
    daily_index = pd.DatetimeIndex(prices.index)
    weights = rebalance_weights.reindex(daily_index, method="ffill").fillna(0.0)
    return weights.reindex(columns=rebalance_weights.columns, fill_value=0.0)


def simulate_strategy(
    prices: pd.DataFrame,
    bundle: FeatureBundle,
    config: StrategyConfig,
    *,
    daily_prices: pd.DataFrame | None = None,
    daily_returns: pd.DataFrame | None = None,
) -> SimulationResult:
    daily = daily_prices if daily_prices is not None else canonicalize_prices(prices)
    if config.staggered_offsets:
        return simulate_staggered(daily, bundle, config, daily_returns=daily_returns)
    rebalance_weights = rebalance_weights_for_config(bundle, config)
    return simulate_from_rebalance_weights(
        daily, rebalance_weights, config.name, daily_returns=daily_returns
    )


def simulate_staggered(
    daily: pd.DataFrame,
    bundle: FeatureBundle,
    config: StrategyConfig,
    *,
    daily_returns: pd.DataFrame | None = None,
) -> SimulationResult:
    sleeves: list[pd.DataFrame] = []
    for offset in range(config.rebalance_months):
        sleeve_config = replace(config, rebalance_offset=offset, staggered_offsets=False)
        rebalance_weights = rebalance_weights_for_config(bundle, sleeve_config)
        if not rebalance_weights.empty:
            sleeves.append(daily_weights_from_rebalances(daily, rebalance_weights))
    if not sleeves:
        empty = pd.Series(dtype=float, name=config.name)
        return SimulationResult(empty, pd.DataFrame(), pd.DataFrame(), empty_turnover())
    columns = sorted({column for frame in sleeves for column in frame.columns})
    daily_weights = pd.DataFrame(0.0, index=daily.index, columns=columns)
    for frame in sleeves:
        daily_weights += frame.reindex(index=daily.index, columns=columns, fill_value=0.0)
    daily_weights /= float(config.rebalance_months)
    return simulate_from_daily_weights(daily, daily_weights, config.name, daily_returns=daily_returns)


def simulate_from_rebalance_weights(
    daily: pd.DataFrame,
    rebalance_weights: pd.DataFrame,
    name: str,
    *,
    daily_returns: pd.DataFrame | None = None,
) -> SimulationResult:
    if rebalance_weights.empty:
        empty = pd.Series(dtype=float, name=name)
        return SimulationResult(empty, pd.DataFrame(), rebalance_weights, empty_turnover())
    daily_weights = daily_weights_from_rebalances(daily, rebalance_weights)
    result = simulate_from_daily_weights(daily, daily_weights, name, daily_returns=daily_returns)
    return SimulationResult(result.returns, result.daily_weights, rebalance_weights, result.turnover)


def simulate_from_daily_weights(
    daily: pd.DataFrame,
    daily_weights: pd.DataFrame,
    name: str,
    *,
    daily_returns: pd.DataFrame | None = None,
) -> SimulationResult:
    if daily_weights.empty:
        empty = pd.Series(dtype=float, name=name)
        return SimulationResult(empty, daily_weights, pd.DataFrame(), empty_turnover())
    used_columns = daily_weights.columns[daily_weights.abs().sum(axis=0) > 1e-12]
    if len(used_columns) == 0:
        empty = pd.Series(dtype=float, name=name)
        return SimulationResult(empty, daily_weights.iloc[0:0], pd.DataFrame(), empty_turnover())
    daily_weights = daily_weights.loc[:, used_columns]
    if daily_returns is None:
        returns = daily[daily_weights.columns].pct_change(fill_method=None).fillna(0.0)
    else:
        returns = daily_returns.reindex(index=daily.index, columns=daily_weights.columns).fillna(0.0)
    gross = (daily_weights.shift(1).fillna(0.0) * returns).sum(axis=1)
    active = daily_weights.sum(axis=1) > 0.0
    if not active.any():
        empty = gross.iloc[0:0].rename(name)
        return SimulationResult(empty, daily_weights.iloc[0:0], pd.DataFrame(), empty_turnover())
    first_signal = active[active].index[0]
    gross = gross[gross.index >= first_signal].rename(name)
    daily_weights = daily_weights.loc[gross.index]
    changed = daily_weights.diff().abs().sum(axis=1) > 1e-12
    if len(changed):
        changed.iloc[0] = daily_weights.iloc[0].sum() > 1e-12
    rebalance_weights = daily_weights.loc[changed]
    return SimulationResult(
        returns=gross,
        daily_weights=daily_weights,
        rebalance_weights=rebalance_weights,
        turnover=turnover_diagnostics(rebalance_weights, gross.index),
    )


def holdings_loop_returns(
    prices: pd.DataFrame,
    rebalance_weights: pd.DataFrame,
    name: str,
    *,
    daily_prices: pd.DataFrame | None = None,
    daily_returns: pd.DataFrame | None = None,
) -> pd.Series:
    """Independent previous-holdings loop to catch look-ahead regressions."""
    daily = daily_prices if daily_prices is not None else canonicalize_prices(prices)
    if rebalance_weights.empty:
        return pd.Series(dtype=float, name=name)
    daily_weights = daily_weights_from_rebalances(daily, rebalance_weights)
    if daily_returns is None:
        asset_returns = daily[daily_weights.columns].pct_change(fill_method=None).fillna(0.0)
    else:
        asset_returns = daily_returns.reindex(index=daily.index, columns=daily_weights.columns).fillna(0.0)
    current = pd.Series(0.0, index=daily_weights.columns)
    values: list[float] = []
    dates: list[pd.Timestamp] = []
    active_seen = False
    for current_date in daily.index:
        value = float((current * asset_returns.loc[current_date]).sum())
        if active_seen:
            values.append(value)
            dates.append(pd.Timestamp(current_date))
        target = daily_weights.loc[current_date].astype(float)
        if target.sum() > 0.0:
            active_seen = True
        if active_seen:
            current = target
    return pd.Series(values, index=pd.DatetimeIndex(dates), name=name)


def empty_turnover() -> dict[str, float]:
    return {
        "n_rebalances": 0.0,
        "annual_turnover": float("nan"),
        "avg_turnover_per_rebalance": float("nan"),
        "avg_names_changed": float("nan"),
        "avg_gross_exposure": float("nan"),
    }


def turnover_diagnostics(weights: pd.DataFrame, return_index: pd.DatetimeIndex) -> dict[str, float]:
    if weights.empty:
        return empty_turnover()
    with_cash = weights.copy()
    with_cash["__CASH__"] = 1.0 - weights.sum(axis=1)
    prev = pd.Series(0.0, index=with_cash.columns)
    turnovers: list[float] = []
    names_changed: list[float] = []
    prev_names: set[str] = set()
    for _date, row in with_cash.iterrows():
        row = row.astype(float)
        turnovers.append(0.5 * float((row - prev).abs().sum()))
        names = {str(col) for col, value in row.items() if col != "__CASH__" and value > 1e-12}
        names_changed.append(float(len(prev_names ^ names)))
        prev = row
        prev_names = names
    final_date = pd.Timestamp(return_index[-1]) if len(return_index) else pd.Timestamp(weights.index[-1])
    years = max((final_date - pd.Timestamp(weights.index[0])).days / 365.25, 1e-9)
    return {
        "n_rebalances": float(len(weights)),
        "annual_turnover": float(np.nansum(turnovers) / years),
        "avg_turnover_per_rebalance": float(np.nanmean(turnovers)),
        "avg_names_changed": float(np.nanmean(names_changed[1:])) if len(names_changed) > 1 else 0.0,
        "avg_gross_exposure": float(weights.sum(axis=1).mean()),
    }
