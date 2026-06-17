"""Cross-sectional momentum scoring and simulation engine.

Ported and consolidated from ``studies/momentum_13612_universes/{core,extensive}.py``
with the extra ``mom_12_1`` score mode from ``studies/momentum``. At each
month-end the configured universe is ranked by a chosen score, the top-N names
are held (equal- or inverse-vol weighted), and weights apply only to *subsequent*
daily returns to avoid look-ahead `[advances_fin_ml, p.31-34]`. The ranking
signal and monthly cadence are anchored in `[stocks_on_the_move, p.60]` and
`[stocks_on_the_move, p.98-99]`. Every added degree of freedom (score shaping,
lookback profile, weighting, offset) is explicit because broad grids must pay
multiple-testing costs `[advances_fin_ml, p.273-275]`.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace
from typing import Literal

import numpy as np
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

ScoreMode = Literal[
    "raw_13612",
    "mom_12_1",
    "vol_adjusted_13612",
    "clenow_trend",
    "composite_mom_lowvol",
]
WeightMode = Literal["equal", "inverse_vol"]
EligibleByDate = Mapping[pd.Timestamp, set[str]]

SCORE_MODES: tuple[ScoreMode, ...] = (
    "raw_13612",
    "mom_12_1",
    "vol_adjusted_13612",
    "clenow_trend",
    "composite_mom_lowvol",
)


@dataclass(frozen=True)
class LookbackProfile:
    """A named tuple of lookback months feeding the raw-momentum score.

    ``mom_3_6_12`` is just ``raw_13612`` under the ``lb3_6_12`` profile; the
    classical 13612 is ``lb1_3_6_12`` `[stocks_on_the_move, p.60]`.
    """

    label: str
    months: tuple[int, ...]


def parse_lookback_profile(token: str) -> LookbackProfile:
    """Parse ``"1_3_6_12"`` -> ``LookbackProfile("lb1_3_6_12", (1, 3, 6, 12))``."""
    months = tuple(int(part) for part in str(token).split("_") if part)
    if not months or any(month <= 0 for month in months):
        raise ValueError(f"invalid lookback profile: {token!r}")
    if len(set(months)) != len(months):
        raise ValueError(f"lookback months must be unique: {token!r}")
    label = "lb" + "_".join(str(month) for month in months)
    return LookbackProfile(label=label, months=months)


@dataclass(frozen=True)
class StrategyConfig:
    """One momentum strategy configuration."""

    name: str
    universe: str
    assets: tuple[str, ...]
    top_n: int
    rebalance_months: int
    rebalance_offset: int
    score_mode: ScoreMode
    lookback: LookbackProfile = LookbackProfile("lb1_3_6_12", (1, 3, 6, 12))
    weight_mode: WeightMode = "equal"
    absolute_filter: bool = False
    vol_window_days: int = 126
    trend_window_days: int = 126
    rank_buffer: int = 0  # 0 = pick top_n fresh each rebalance; >0 = hysteresis band (turnover cut)

    def __post_init__(self) -> None:
        if self.top_n <= 0:
            raise ValueError("top_n must be positive")
        if self.rank_buffer < 0:
            raise ValueError("rank_buffer must be >= 0")
        if self.rebalance_months <= 0:
            raise ValueError("rebalance_months must be positive")
        if not 0 <= self.rebalance_offset < self.rebalance_months:
            raise ValueError("rebalance_offset must be in [0, rebalance_months)")
        if self.score_mode not in SCORE_MODES:
            raise ValueError(f"unknown score_mode {self.score_mode!r}")
        if self.weight_mode not in {"equal", "inverse_vol"}:
            raise ValueError(f"unknown weight_mode {self.weight_mode!r}")

    @property
    def mechanism(self) -> str:
        """Human-readable mechanism label for grouping plots/PBO."""
        if self.absolute_filter:
            return f"{self.score_mode}_abs_cash"
        if self.weight_mode == "inverse_vol":
            return f"{self.score_mode}_inverse_vol"
        return self.score_mode


@dataclass(frozen=True)
class ScoreBundle:
    """Precomputed score and volatility frames for one universe/lookback."""

    monthly_prices: pd.DataFrame
    scores: dict[str, pd.DataFrame]
    monthly_vol: pd.DataFrame


@dataclass(frozen=True)
class SimulationResult:
    """Return stream plus diagnostics for one config."""

    returns: pd.Series
    daily_weights: pd.DataFrame
    rebalance_weights: pd.DataFrame
    turnover: dict[str, float]


@dataclass(frozen=True)
class PanelCache:
    """Per-phase precompute of the daily panel reused by every config.

    ``canonicalize_columns(prices).sort_index()`` and the full-panel
    ``pct_change`` are identical for every config in a phase, so computing them
    once (and, under fork, sharing them copy-on-write) instead of per config is a
    pure speedup with bit-identical results.
    """

    daily: pd.DataFrame
    asset_returns: pd.DataFrame


def build_panel_cache(prices: pd.DataFrame) -> "PanelCache":
    """Canonical sorted daily panel + its daily returns, computed once per phase."""
    daily = canonicalize_columns(prices).sort_index()
    return PanelCache(daily=daily, asset_returns=daily.pct_change(fill_method=None).fillna(0.0))


@dataclass(frozen=True)
class TaxResult:
    """After-tax return stream and annual-tax diagnostics."""

    returns: pd.Series
    summary: dict[str, object]


# --- scoring primitives -----------------------------------------------------

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
    """Equal-weighted multi-window return momentum.

    All lookback components must exist, enforcing a minimum-history convention
    so the cross-sectional rank does not implicitly favor young listings
    `[stocks_on_the_move, p.60]`.
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


def mom_12_1_scores(monthly_prices: pd.DataFrame) -> pd.DataFrame:
    """12-month momentum excluding the most recent month (reversal-robust)."""
    prices = canonicalize_columns(monthly_prices).astype(float)
    return prices.shift(1) / prices.shift(12) - 1.0


def rank_scores(scores: pd.Series) -> list[str]:
    """Return symbols ranked by score desc, breaking ties alphabetically."""
    clean = scores.dropna().astype(float)
    ranked = sorted(clean.items(), key=lambda item: (-float(item[1]), str(item[0])))
    return [str(symbol) for symbol, _score in ranked]


def realized_volatility(prices: pd.DataFrame, window_days: int = 126) -> pd.DataFrame:
    """Annualized rolling realized volatility from adjusted-close returns."""
    returns = prices.pct_change(fill_method=None)
    return returns.rolling(window_days, min_periods=window_days).std() * np.sqrt(
        TRADING_DAYS_PER_YEAR
    )


def clenow_trend_scores(prices: pd.DataFrame, window_days: int = 126) -> pd.DataFrame:
    """Rolling exponential-regression slope times R².

    Annualizes the log-price regression slope and multiplies by R² to reward
    smooth trends rather than noisy jumps `[stocks_on_the_move, p.70-77, p.98]`.
    """
    if window_days < 3:
        raise ValueError("trend window must be >= 3")
    log_prices = np.log(prices.astype(float).replace(0.0, np.nan))
    out = pd.DataFrame(index=prices.index, columns=prices.columns, dtype=float)
    x = np.arange(window_days, dtype=float)
    sum_x = float(x.sum())
    sum_x2 = float((x * x).sum())
    x_centered_ss = sum_x2 - (sum_x * sum_x / window_days)
    weights = x[::-1]
    ones = np.ones(window_days, dtype=float)

    for column in log_prices.columns:
        y = log_prices[column].to_numpy(dtype=float)
        finite = np.isfinite(y).astype(float)
        y_filled = np.where(np.isfinite(y), y, 0.0)
        count = np.convolve(finite, ones, mode="valid")
        sum_y = np.convolve(y_filled, ones, mode="valid")
        sum_y2 = np.convolve(y_filled * y_filled, ones, mode="valid")
        sum_xy = np.convolve(y_filled, weights, mode="valid")

        valid = count == window_days
        slope = np.full_like(sum_y, np.nan, dtype=float)
        r2 = np.full_like(sum_y, np.nan, dtype=float)
        if valid.any():
            numerator = sum_xy[valid] - (sum_x * sum_y[valid] / window_days)
            slope[valid] = numerator / x_centered_ss
            y_centered_ss = sum_y2[valid] - (sum_y[valid] * sum_y[valid] / window_days)
            denom = x_centered_ss * y_centered_ss
            ok = denom > 1e-12
            valid_indices = np.flatnonzero(valid)
            r2_values = np.full(len(valid_indices), np.nan, dtype=float)
            r2_values[ok] = (numerator[ok] * numerator[ok]) / denom[ok]
            r2[valid_indices] = r2_values

        score = (np.exp(slope * TRADING_DAYS_PER_YEAR) - 1.0) * r2
        padded = np.full(len(y), np.nan, dtype=float)
        padded[window_days - 1 :] = score
        out[column] = padded
    return out


def composite_momentum_lowvol(raw_momentum: pd.DataFrame, monthly_vol: pd.DataFrame) -> pd.DataFrame:
    """70/30 cross-sectional rank blend of momentum and low volatility
    `[systematic_trading, p.137-148]`."""
    mom_rank = raw_momentum.rank(axis=1, pct=True)
    lowvol_rank = (-monthly_vol).rank(axis=1, pct=True)
    return 0.70 * mom_rank + 0.30 * lowvol_rank


def precompute_scores(
    prices: pd.DataFrame,
    assets: tuple[str, ...],
    vol_window_days: int = 126,
    trend_window_days: int = 126,
    lookback_months: tuple[int, ...] = (1, 3, 6, 12),
) -> ScoreBundle:
    """Precompute every score frame used by the grid for one lookback profile.

    Each extra lookback profile is another tested degree of freedom and must be
    accounted for in the research surface `[advances_fin_ml, p.273-275]`.
    """
    daily = canonicalize_columns(prices).sort_index()
    available = [asset.upper() for asset in assets if asset.upper() in daily.columns]
    monthly_prices = daily[available].resample("ME").last()
    raw = momentum_13612u(monthly_prices, available, lookback_months=lookback_months)
    monthly_vol = realized_volatility(daily[available], vol_window_days).resample("ME").last()
    vol_adjusted = raw / monthly_vol.replace(0.0, np.nan)
    clenow = clenow_trend_scores(daily[available], trend_window_days).resample("ME").last()
    composite = composite_momentum_lowvol(raw, monthly_vol)
    mom_12_1 = mom_12_1_scores(monthly_prices)
    return ScoreBundle(
        monthly_prices=monthly_prices,
        scores={
            "raw_13612": raw,
            "mom_12_1": mom_12_1,
            "vol_adjusted_13612": vol_adjusted,
            "clenow_trend": clenow,
            "composite_mom_lowvol": composite,
        },
        monthly_vol=monthly_vol,
    )


# --- weights / simulation ---------------------------------------------------

def is_rebalance_month(date: pd.Timestamp, frequency_months: int, offset: int) -> bool:
    """Calendar-month rebalance selector with all offsets testable."""
    month_zero = pd.Timestamp(date).month - 1
    return (month_zero - offset) % frequency_months == 0


def eligible_assets_for_date(
    eligible_by_date: EligibleByDate | None,
    rebalance_date: pd.Timestamp,
) -> set[str] | None:
    """Return the date-specific eligible universe, if one is configured."""
    if eligible_by_date is None:
        return None
    ts = pd.Timestamp(rebalance_date)
    eligible = eligible_by_date.get(ts)
    if eligible is None:
        eligible = eligible_by_date.get(ts.to_period("M").to_timestamp("M"))
    return {str(asset).upper() for asset in eligible} if eligible is not None else set()


def monthly_weights(
    bundle: ScoreBundle,
    config: StrategyConfig,
    eligible_by_date: EligibleByDate | None = None,
) -> pd.DataFrame:
    """Build rebalance-date target weights for one config."""
    assets = [a.upper() for a in config.assets if a.upper() in bundle.monthly_prices.columns]
    scores = bundle.scores[config.score_mode].reindex(columns=assets)
    monthly_vol = bundle.monthly_vol.reindex(columns=assets)
    weights = pd.DataFrame(0.0, index=scores.index, columns=assets)
    buffer = max(int(config.rank_buffer), 0)
    held: list[str] = []  # carried across rebalances only when a ranking buffer is active

    for rebalance_date in scores.index:
        if not is_rebalance_month(rebalance_date, config.rebalance_months, config.rebalance_offset):
            continue
        row = scores.loc[rebalance_date].copy()
        eligible = eligible_assets_for_date(eligible_by_date, pd.Timestamp(rebalance_date))
        if eligible is not None:
            if not eligible:
                continue
            row = row.where(row.index.to_series().astype(str).str.upper().isin(eligible), np.nan)
        ranked = rank_scores(row)
        if len(ranked) < config.top_n:
            continue
        if buffer > 0:
            # Hysteresis: keep a held name until it drops out of the top (top_n + buffer); only then
            # replace it with the best non-held candidate. Cuts turnover `[stocks_on_the_move, p.98-99]`.
            pool = [a for a in ranked if float(row[a]) > 0.0] if config.absolute_filter else ranked
            keep_set = set(pool[: config.top_n + buffer])
            chosen = [a for a in held if a in keep_set][: config.top_n]
            for asset in pool:
                if len(chosen) >= config.top_n:
                    break
                if asset not in chosen:
                    chosen.append(asset)
            held = list(chosen)
        else:
            chosen = ranked[: config.top_n]
            if config.absolute_filter:
                chosen = [asset for asset in chosen if float(row[asset]) > 0.0]
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
    return weights.loc[weights.sum(axis=1) > 0.0]


def daily_weights_from_monthly(prices: pd.DataFrame, monthly_weights_frame: pd.DataFrame) -> pd.DataFrame:
    """Forward-fill month-end target weights onto the daily price index."""
    daily_index = pd.DatetimeIndex(prices.index)
    weights = monthly_weights_frame.reindex(daily_index, method="ffill").fillna(0.0)
    return weights.reindex(columns=monthly_weights_frame.columns, fill_value=0.0)


def _returns_from_daily_weights(
    daily: pd.DataFrame,
    daily_weights: pd.DataFrame,
    name: str,
    asset_returns: pd.DataFrame | None = None,
    cost_bps: float = 0.0,
) -> pd.Series:
    # asset_returns precomputed (PanelCache) is identical to recomputing it here
    # column-by-column; selecting the same columns keeps the sum bit-identical.
    cols = daily_weights.columns
    rets = asset_returns[cols] if asset_returns is not None else daily[cols].pct_change(fill_method=None).fillna(0.0)
    gross = (daily_weights.shift(1).fillna(0.0) * rets).sum(axis=1)
    if cost_bps > 0.0:
        # Linear transaction cost: cost_bps per unit of weight traded (buys+sells), charged on the
        # day weights change (no look-ahead). cost_bps=0 -> gross returns unchanged (bit-identical).
        traded = daily_weights.diff().abs().sum(axis=1).fillna(0.0)
        gross = gross - (cost_bps / 10000.0) * traded
    active = daily_weights.sum(axis=1) > 0.0
    if not active.any():
        return gross.iloc[0:0].rename(name)
    first_signal = active[active].index[0]
    return gross[gross.index >= first_signal].rename(name)


def simulate_config(
    prices: pd.DataFrame,
    bundle: ScoreBundle,
    config: StrategyConfig,
    eligible_by_date: EligibleByDate | None = None,
    panel: PanelCache | None = None,
    cost_bps: float = 0.0,
) -> SimulationResult:
    """Simulate one configuration with a single (fixed) rebalance offset.

    ``panel`` (optional) supplies the once-per-phase canonical daily frame and
    daily returns; without it they are computed here as before (bit-identical).
    ``cost_bps`` (optional) charges a linear transaction cost per unit traded;
    0 = gross of costs (default, unchanged).
    """
    daily = panel.daily if panel is not None else canonicalize_columns(prices).sort_index()
    rebalance_weights = monthly_weights(bundle, config, eligible_by_date=eligible_by_date)
    if rebalance_weights.empty:
        empty = pd.Series(dtype=float, name=config.name)
        return SimulationResult(empty, pd.DataFrame(), rebalance_weights, empty_turnover())
    daily_weights = daily_weights_from_monthly(daily, rebalance_weights)
    returns = _returns_from_daily_weights(
        daily, daily_weights, config.name,
        asset_returns=panel.asset_returns if panel is not None else None, cost_bps=cost_bps,
    )
    return SimulationResult(
        returns=returns,
        daily_weights=daily_weights,
        rebalance_weights=rebalance_weights,
        turnover=turnover_diagnostics(rebalance_weights, returns.index),
    )


def simulate_staggered_offsets(
    prices: pd.DataFrame,
    bundle: ScoreBundle,
    config: StrategyConfig,
    eligible_by_date: EligibleByDate | None = None,
) -> SimulationResult:
    """Equal-capital sleeves across every rebalance offset.

    Tests the mechanism without selecting a lucky rebalance month after the
    fact: each offset is one sleeve, the portfolio holds the equal-weight
    average of sleeve weights, and performance starts only after all sleeves
    have a first signal. Reduces timing-luck exposure `[advances_fin_ml,
    p.273-275]` while keeping the monthly cadence `[stocks_on_the_move, p.98-99]`.
    """
    daily = canonicalize_columns(prices).sort_index()
    sleeve_frames: list[pd.DataFrame] = []
    for offset in range(config.rebalance_months):
        sleeve_config = replace(config, rebalance_offset=offset)
        rebalance_weights = monthly_weights(bundle, sleeve_config, eligible_by_date=eligible_by_date)
        if rebalance_weights.empty:
            continue
        sleeve_frames.append(daily_weights_from_monthly(daily, rebalance_weights))

    if not sleeve_frames:
        empty = pd.Series(dtype=float, name=config.name)
        return SimulationResult(empty, pd.DataFrame(), pd.DataFrame(), empty_turnover())

    columns = sorted({column for frame in sleeve_frames for column in frame.columns})
    daily_weights = pd.DataFrame(0.0, index=daily.index, columns=columns)
    for frame in sleeve_frames:
        aligned = frame.reindex(index=daily.index, columns=columns, fill_value=0.0).fillna(0.0)
        daily_weights = daily_weights.add(aligned, fill_value=0.0)
    daily_weights /= float(config.rebalance_months)

    asset_returns = daily[daily_weights.columns].pct_change(fill_method=None).fillna(0.0)
    gross = (daily_weights.shift(1).fillna(0.0) * asset_returns).sum(axis=1)
    target_exposure = min(1.0, len(sleeve_frames) / float(config.rebalance_months))
    full = daily_weights.sum(axis=1) >= target_exposure - 1e-12
    if full.any():
        first_signal = full[full].index[0]
    else:
        active = daily_weights.sum(axis=1) > 0.0
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


def simulate_config_holdings_loop(
    prices: pd.DataFrame,
    bundle: ScoreBundle,
    config: StrategyConfig,
    eligible_by_date: EligibleByDate | None = None,
) -> pd.Series:
    """Independent holdings-loop reference for the cross-library CAGR check.

    Recomputes the fixed-offset return stream with an explicit per-day loop
    rather than the vectorized shift, so a mismatch flags an engine bug
    `[advances_fin_ml, p.31-34]`.
    """
    daily = canonicalize_columns(prices).sort_index()
    rebalance_weights = monthly_weights(bundle, config, eligible_by_date=eligible_by_date)
    if rebalance_weights.empty:
        return pd.Series(dtype=float, name=config.name)
    daily_weights = daily_weights_from_monthly(daily, rebalance_weights)
    asset_returns = daily[daily_weights.columns].pct_change(fill_method=None).fillna(0.0)
    current = pd.Series(0.0, index=daily_weights.columns)
    returns: list[float] = []
    dates: list[pd.Timestamp] = []
    active_seen = False
    for current_date in daily.index:
        day_return = float((current * asset_returns.loc[current_date]).sum())
        if active_seen:
            returns.append(day_return)
            dates.append(pd.Timestamp(current_date))
        target = daily_weights.loc[current_date].astype(float)
        if target.sum() > 0.0:
            active_seen = True
        if active_seen:
            current = target
    return pd.Series(returns, index=pd.DatetimeIndex(dates), name=config.name)


# --- turnover ---------------------------------------------------------------

def empty_turnover() -> dict[str, float]:
    return {
        "n_rebalances": 0.0,
        "annual_turnover": float("nan"),
        "avg_turnover_per_rebalance": float("nan"),
        "avg_names_changed": float("nan"),
        "avg_holding_months": float("nan"),
        "avg_gross_exposure": float("nan"),
    }


def turnover_diagnostics(weights: pd.DataFrame, return_index: pd.DatetimeIndex) -> dict[str, float]:
    """Compute turnover and approximate holding-period diagnostics."""
    if weights.empty:
        return empty_turnover()
    cash = 1.0 - weights.sum(axis=1)
    with_cash = weights.copy()
    with_cash["__CASH__"] = cash
    prev = pd.Series(0.0, index=with_cash.columns)
    turnovers: list[float] = []
    names_changed: list[float] = []
    prev_names: set[str] = set()
    entry_dates: dict[str, pd.Timestamp] = {}
    holding_months: list[float] = []

    for date, row in with_cash.iterrows():
        turnover = 0.5 * float((row.astype(float) - prev).abs().sum())
        turnovers.append(turnover)
        current_names = {str(col) for col, value in row.items() if col != "__CASH__" and value > 1e-12}
        names_changed.append(float(len(prev_names ^ current_names)))
        for asset in current_names - prev_names:
            entry_dates[asset] = pd.Timestamp(date)
        for asset in prev_names - current_names:
            entered = entry_dates.pop(asset, pd.Timestamp(date))
            holding_months.append((pd.Timestamp(date) - entered).days / 30.4375)
        prev = row.astype(float)
        prev_names = current_names

    final_date = pd.Timestamp(return_index[-1]) if len(return_index) else pd.Timestamp(weights.index[-1])
    for entered in entry_dates.values():
        holding_months.append((final_date - entered).days / 30.4375)

    years = max((final_date - pd.Timestamp(weights.index[0])).days / 365.25, 1e-9)
    return {
        "n_rebalances": float(len(weights)),
        "annual_turnover": float(np.nansum(turnovers) / years),
        "avg_turnover_per_rebalance": float(np.nanmean(turnovers)),
        "avg_names_changed": float(np.nanmean(names_changed[1:])) if len(names_changed) > 1 else 0.0,
        "avg_holding_months": float(np.nanmean(holding_months)) if holding_months else float("nan"),
        "avg_gross_exposure": float(weights.sum(axis=1).mean()),
    }


# --- Brazil annual foreign capital-gains tax --------------------------------

def apply_br_foreign_annual_tax(
    returns: pd.Series,
    daily_weights: pd.DataFrame,
    initial_value: float = 10_000.0,
    tax_rate: float = 0.15,
) -> TaxResult:
    """Apply Brazil's annual 15% tax on realized foreign capital gains.

    Nets realized gains/losses per calendar year, carries losses forward, and
    subtracts 15% when a positive taxable amount settles the next year. Does not
    force a final liquidation of unrealized positions; only realized P&L caused
    by rebalances is taxed.
    """
    clean_returns = returns.dropna().astype(float)
    if clean_returns.empty:
        return TaxResult(clean_returns, empty_tax_summary())

    weights = daily_weights.reindex(clean_returns.index, method="ffill").fillna(0.0).astype(float)
    weights = weights.reindex(columns=daily_weights.columns, fill_value=0.0)
    prev_weights = weights.shift(1).fillna(0.0)
    sold_fractions = (prev_weights - weights).clip(lower=0.0).sum(axis=1).to_numpy(dtype=float)
    bought_fractions = (weights - prev_weights).clip(lower=0.0).sum(axis=1).to_numpy(dtype=float)
    prev_exposures = prev_weights.sum(axis=1).to_numpy(dtype=float)

    portfolio_value = float(initial_value)
    prev_value = float(initial_value)
    cost_basis = 0.0
    loss_carryforward = 0.0
    events: list[dict[str, float | int]] = []
    total_tax_paid = 0.0
    last_year: int | None = None
    annual_realized = 0.0
    net_returns: list[float] = []

    def settle_year(year: int, annual_gross: float) -> None:
        nonlocal portfolio_value, loss_carryforward, total_tax_paid
        taxable = annual_gross + loss_carryforward
        tax = max(0.0, taxable) * tax_rate
        if tax > 0.0:
            portfolio_value -= tax
            total_tax_paid += tax
            loss_carryforward = 0.0
        else:
            loss_carryforward = taxable
        events.append(
            {
                "year": year,
                "annual_realized_pnl": annual_gross,
                "taxable": taxable,
                "tax_paid": tax,
                "loss_carryforward_out": loss_carryforward,
                "portfolio_value_after_tax": portfolio_value,
            }
        )

    for idx, (date, daily_return) in enumerate(clean_returns.items()):
        current_year = int(pd.Timestamp(date).year)
        if last_year is not None and current_year != last_year:
            settle_year(last_year, annual_realized)
            annual_realized = 0.0
        last_year = current_year

        sold_fraction = float(sold_fractions[idx])
        bought_fraction = float(bought_fractions[idx])
        prev_exposure = float(prev_exposures[idx])
        if sold_fraction > 1e-12 and prev_exposure > 1e-12:
            sold_fraction = min(sold_fraction, prev_exposure)
            sold_value = sold_fraction * portfolio_value
            basis_ratio = min(sold_fraction / prev_exposure, 1.0)
            cost_sold = cost_basis * basis_ratio
            annual_realized += sold_value - cost_sold
            cost_basis = max(0.0, cost_basis - cost_sold)
        if bought_fraction > 1e-12:
            cost_basis += bought_fraction * portfolio_value

        portfolio_value *= 1.0 + float(daily_return)
        net_returns.append(portfolio_value / prev_value - 1.0)
        prev_value = portfolio_value

    if last_year is not None:
        pre_settlement = portfolio_value
        settle_year(last_year, annual_realized)
        if net_returns and pre_settlement > 0.0:
            net_returns[-1] = (1.0 + net_returns[-1]) * (portfolio_value / pre_settlement) - 1.0

    out = pd.Series(net_returns, index=clean_returns.index, name=f"{returns.name}_after_tax")
    summary = {
        "initial_value": initial_value,
        "terminal_value": portfolio_value,
        "total_tax_paid": total_tax_paid,
        "tax_paid_pct_initial": total_tax_paid / initial_value,
        "tax_events": len(events),
        "years_taxed": sum(1 for event in events if float(event["tax_paid"]) > 0.0),
        "loss_carryforward_final": loss_carryforward,
        "events": events,
    }
    return TaxResult(out, summary)


def empty_tax_summary() -> dict[str, object]:
    return {
        "initial_value": 10_000.0,
        "terminal_value": 10_000.0,
        "total_tax_paid": 0.0,
        "tax_paid_pct_initial": 0.0,
        "tax_events": 0,
        "years_taxed": 0,
        "loss_carryforward_final": 0.0,
        "events": [],
    }


# --- equity / metrics / benchmark -------------------------------------------

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
            "start": "n/a", "end": "n/a", "n_obs": 0, "years": 0.0,
            "cagr": 0.0, "mdd": 0.0, "vol": 0.0, "sharpe": 0.0,
            "sortino": 0.0, "calmar": 0.0, "terminal": 1.0,
        }
    equity = equity_from_returns(clean, start_value=1.0)
    years = len(clean) / periods_per_year
    # A return <= -1 (only reachable from corrupt non-positive prices) drives equity
    # non-positive and makes the power-based metrics complex; guard so one bad config
    # returns total-loss sentinels instead of aborting a whole (parallel) run.
    eq = equity.to_numpy(dtype=float)
    ok = bool(np.isfinite(eq).all() and (eq > 0.0).all())
    return {
        "start": str(clean.index[0].date()),
        "end": str(clean.index[-1].date()),
        "n_obs": int(len(clean)),
        "years": float(years),
        "cagr": float(cagr(equity, periods_per_year)) if ok else -1.0,
        "mdd": -float(max_drawdown(equity)) if ok else -1.0,
        "vol": float(volatility(clean, periods_per_year)),
        "sharpe": float(sharpe(clean, periods_per_year)),
        "sortino": float(sortino(clean, periods_per_year)),
        "calmar": float(calmar(equity, periods_per_year)) if ok else -1.0,
        "terminal": float(equity.iloc[-1]) if ok else 0.0,
    }


def benchmark_returns_for(
    strategy_returns: pd.Series, benchmark_prices: pd.DataFrame, benchmark_symbol: str = "SPY"
) -> tuple[pd.Series, pd.Series]:
    """Align strategy returns with benchmark returns on common dates."""
    clean_strategy = strategy_returns.dropna().astype(float)
    if clean_strategy.empty:
        return clean_strategy, clean_strategy.rename(benchmark_symbol)
    cols = {str(col).upper(): col for col in benchmark_prices.columns}
    col = cols.get(benchmark_symbol.upper(), benchmark_prices.columns[0])
    bench_prices = benchmark_prices[col].astype(float).sort_index()
    bench_prices.index = pd.DatetimeIndex(bench_prices.index).tz_localize(None)
    bench_prices = bench_prices.reindex(clean_strategy.index, method="ffill").dropna()
    aligned_strategy = clean_strategy.reindex(bench_prices.index).dropna()
    bench_prices = bench_prices.reindex(aligned_strategy.index).dropna()
    aligned_strategy = aligned_strategy.reindex(bench_prices.index).dropna()
    bench = bench_prices.pct_change(fill_method=None).fillna(0.0).rename(benchmark_symbol.upper())
    return aligned_strategy, bench


def make_config_name(
    universe: str, mechanism: str, lookback_label: str, top_n: int, rebalance_months: int, offset: int
) -> str:
    return f"momv2_{universe}_{mechanism}_{lookback_label}_top{top_n}_reb{rebalance_months}_off{offset}"
