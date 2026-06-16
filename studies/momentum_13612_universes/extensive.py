"""Extensive US-only 13612 research grid helpers.

The grid tests score shaping, risk weighting and rebalance timing around the
same cross-sectional momentum thesis. Each added degree of freedom is explicit
because broad grids must pay multiple-testing costs `[advances_fin_ml,
p.273-275]`. Score choices are grounded as follows: raw cross-sectional
momentum `[stocks_on_the_move, p.60]`, Clenow's smooth trend slope times R²
`[stocks_on_the_move, p.70-77, p.98]`, and volatility normalization / inverse
volatility sizing `[systematic_trading, p.137-148]`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Literal

import numpy as np
import pandas as pd

from market_lab.backtest.metrics.performance import sharpe
from market_lab.backtest.validation.dsr import dsr, psr
from market_lab.backtest.validation.walk_forward import walk_forward_splits
from studies.momentum_13612_universes.core import (
    TRADING_DAYS_PER_YEAR,
    canonicalize_columns,
    daily_weights_from_monthly,
    equity_from_returns,
    metrics_from_returns,
    momentum_13612u,
    rank_scores,
)


ScoreMode = Literal[
    "raw_13612",
    "vol_adjusted_13612",
    "clenow_trend",
    "composite_mom_lowvol",
]
WeightMode = Literal["equal", "inverse_vol"]
EligibleByDate = Mapping[pd.Timestamp, set[str]]
RELATIVE_EQUITY_HORIZONS = (3, 5, 10, 15, 20)
RELATIVE_EQUITY_WEIGHTS = {3: 0.10, 5: 0.15, 10: 0.25, 15: 0.25, 20: 0.25}


@dataclass(frozen=True)
class ExtensiveConfig:
    """One extensive-grid configuration."""

    name: str
    universe: str
    assets: tuple[str, ...]
    top_n: int
    rebalance_months: int
    rebalance_offset: int
    score_mode: ScoreMode
    weight_mode: WeightMode = "equal"
    absolute_filter: bool = False
    vol_window_days: int = 126
    trend_window_days: int = 126

    def __post_init__(self) -> None:
        if self.top_n <= 0:
            raise ValueError("top_n must be positive")
        if self.rebalance_months <= 0:
            raise ValueError("rebalance_months must be positive")
        if not 0 <= self.rebalance_offset < self.rebalance_months:
            raise ValueError("rebalance_offset must be in [0, rebalance_months)")
        if self.score_mode not in {
            "raw_13612",
            "vol_adjusted_13612",
            "clenow_trend",
            "composite_mom_lowvol",
        }:
            raise ValueError(f"unknown score_mode {self.score_mode!r}")
        if self.weight_mode not in {"equal", "inverse_vol"}:
            raise ValueError(f"unknown weight_mode {self.weight_mode!r}")

    @property
    def mechanism(self) -> str:
        """Human-readable mechanism label for grouping plots."""
        if self.absolute_filter:
            return "raw_abs_cash"
        if self.weight_mode == "inverse_vol":
            return "raw_inverse_vol"
        return self.score_mode


@dataclass(frozen=True)
class ScoreBundle:
    """Precomputed score and volatility frames for one universe."""

    monthly_prices: pd.DataFrame
    scores: dict[str, pd.DataFrame]
    monthly_vol: pd.DataFrame


@dataclass(frozen=True)
class SimulationResult:
    """Return stream plus diagnostics for one extensive-grid config."""

    returns: pd.Series
    daily_weights: pd.DataFrame
    rebalance_weights: pd.DataFrame
    turnover: dict[str, float]


@dataclass(frozen=True)
class TaxResult:
    """After-tax return stream and annual-tax diagnostics."""

    returns: pd.Series
    summary: dict[str, object]


def precompute_scores(
    prices: pd.DataFrame,
    assets: tuple[str, ...],
    vol_window_days: int = 126,
    trend_window_days: int = 126,
    lookback_months: tuple[int, ...] = (1, 3, 6, 12),
) -> ScoreBundle:
    """Precompute all score frames used by the extensive grid.

    ``lookback_months`` is intentionally explicit for heatmap diagnostics; each
    extra window is another tested degree of freedom and must be accounted for in
    the research surface `[advances_fin_ml, p.273-275]`.
    """
    daily = canonicalize_columns(prices).sort_index()
    available = [asset.upper() for asset in assets if asset.upper() in daily.columns]
    monthly_prices = daily[available].resample("ME").last()
    raw = momentum_13612u(monthly_prices, available, lookback_months=lookback_months)
    monthly_vol = realized_volatility(daily[available], vol_window_days).resample("ME").last()
    vol_adjusted = raw / monthly_vol.replace(0.0, np.nan)
    clenow = clenow_trend_scores(daily[available], trend_window_days).resample("ME").last()
    composite = composite_momentum_lowvol(raw, monthly_vol)
    return ScoreBundle(
        monthly_prices=monthly_prices,
        scores={
            "raw_13612": raw,
            "vol_adjusted_13612": vol_adjusted,
            "clenow_trend": clenow,
            "composite_mom_lowvol": composite,
        },
        monthly_vol=monthly_vol,
    )


def realized_volatility(prices: pd.DataFrame, window_days: int = 126) -> pd.DataFrame:
    """Annualized rolling realized volatility from adjusted-close returns."""
    returns = prices.pct_change(fill_method=None)
    return returns.rolling(window_days, min_periods=window_days).std() * np.sqrt(
        TRADING_DAYS_PER_YEAR
    )


def clenow_trend_scores(prices: pd.DataFrame, window_days: int = 126) -> pd.DataFrame:
    """Rolling exponential-regression slope times R² score.

    The score annualizes the log-price regression slope and multiplies by R² to
    reward smooth trends rather than noisy jumps `[stocks_on_the_move,
    p.70-77, p.98]`.
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
    """70/30 cross-sectional rank blend of momentum and low volatility."""
    mom_rank = raw_momentum.rank(axis=1, pct=True)
    lowvol_rank = (-monthly_vol).rank(axis=1, pct=True)
    return 0.70 * mom_rank + 0.30 * lowvol_rank


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


def extensive_monthly_weights(
    bundle: ScoreBundle,
    config: ExtensiveConfig,
    eligible_by_date: EligibleByDate | None = None,
) -> pd.DataFrame:
    """Build rebalance-date weights for one extensive-grid config."""
    assets = [asset.upper() for asset in config.assets if asset.upper() in bundle.monthly_prices.columns]
    scores = bundle.scores[config.score_mode].reindex(columns=assets)
    monthly_vol = bundle.monthly_vol.reindex(columns=assets)
    weights = pd.DataFrame(0.0, index=scores.index, columns=assets)

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


def is_rebalance_month(date: pd.Timestamp, frequency_months: int, offset: int) -> bool:
    """Calendar-month rebalance selector with all offsets testable."""
    month_zero = pd.Timestamp(date).month - 1
    return (month_zero - offset) % frequency_months == 0


def simulate_extensive_config(
    prices: pd.DataFrame,
    bundle: ScoreBundle,
    config: ExtensiveConfig,
    eligible_by_date: EligibleByDate | None = None,
) -> SimulationResult:
    """Simulate one extensive-grid configuration."""
    daily = canonicalize_columns(prices).sort_index()
    rebalance_weights = extensive_monthly_weights(bundle, config, eligible_by_date=eligible_by_date)
    if rebalance_weights.empty:
        empty = pd.Series(dtype=float, name=config.name)
        return SimulationResult(empty, pd.DataFrame(), rebalance_weights, empty_turnover())
    daily_weights = daily_weights_from_monthly(daily, rebalance_weights)
    asset_returns = daily[daily_weights.columns].pct_change(fill_method=None).fillna(0.0)
    gross = (daily_weights.shift(1).fillna(0.0) * asset_returns).sum(axis=1)
    active = daily_weights.sum(axis=1) > 0.0
    if not active.any():
        returns = gross.iloc[0:0].rename(config.name)
    else:
        first_signal = active[active].index[0]
        returns = gross[gross.index >= first_signal].rename(config.name)
    return SimulationResult(
        returns=returns,
        daily_weights=daily_weights,
        rebalance_weights=rebalance_weights,
        turnover=turnover_diagnostics(rebalance_weights, returns.index),
    )


def simulate_staggered_offsets(
    prices: pd.DataFrame,
    bundle: ScoreBundle,
    config: ExtensiveConfig,
    eligible_by_date: EligibleByDate | None = None,
) -> SimulationResult:
    """Simulate equal-capital sleeves across every rebalance offset.

    The goal is to test the mechanism without selecting a lucky rebalance month
    after the fact. Each offset becomes one sleeve, the portfolio holds the
    equal-weight average of sleeve weights, and performance starts only after all
    sleeves have received their first signal. This keeps the monthly momentum
    cadence `[stocks_on_the_move, p.98-99]` while reducing timing-luck exposure
    in broad grids `[advances_fin_ml, p.273-275]`.
    """
    daily = canonicalize_columns(prices).sort_index()
    sleeve_frames: list[pd.DataFrame] = []
    for offset in range(config.rebalance_months):
        sleeve_config = replace(config, rebalance_offset=offset)
        rebalance_weights = extensive_monthly_weights(bundle, sleeve_config, eligible_by_date=eligible_by_date)
        if rebalance_weights.empty:
            continue
        sleeve = daily_weights_from_monthly(daily, rebalance_weights)
        sleeve_frames.append(sleeve)

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
    for asset, entered in entry_dates.items():
        del asset
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


def apply_br_foreign_annual_tax(
    returns: pd.Series,
    daily_weights: pd.DataFrame,
    initial_value: float = 10_000.0,
    tax_rate: float = 0.15,
) -> TaxResult:
    """Apply Brazil's annual 15% tax on realized foreign capital gains.

    The model nets realized gains and losses per calendar year, carries losses
    forward, and subtracts 15% from the portfolio when a positive taxable amount
    is settled in the next year. It does **not** force a final liquidation of
    unrealized positions; only realized P&L caused by rebalances is taxed.
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


def relative_equity_metrics(strategy_returns: pd.Series, benchmark_returns: pd.Series) -> dict[str, float]:
    """Strategy-vs-benchmark equity diagnostics."""
    if strategy_returns.empty or benchmark_returns.empty:
        return {
            "pct_time_above_benchmark": float("nan"),
            "min_relative_equity": float("nan"),
            "terminal_relative": float("nan"),
        }
    strategy_eq = equity_from_returns(strategy_returns, start_value=1.0)
    benchmark_eq = equity_from_returns(benchmark_returns, start_value=1.0)
    aligned = pd.concat({"strategy": strategy_eq, "benchmark": benchmark_eq}, axis=1).dropna()
    ratio = aligned["strategy"] / aligned["benchmark"]
    post = ratio.iloc[min(252, max(len(ratio) - 1, 0)) :]
    if post.empty:
        post = ratio
    return {
        "pct_time_above_benchmark": float((post > 1.0).mean()),
        "min_relative_equity": float(post.min()),
        "terminal_relative": float(ratio.iloc[-1]),
    }


def rolling_relative_equity_windows(
    strategy_returns: pd.Series,
    benchmark_returns: pd.Series,
    horizon_years: int,
) -> pd.DataFrame:
    """Monthly rolling relative-equity windows reset at each start date.

    Each window compares growth of `$1` in the strategy vs `$1` in the benchmark
    from the same start date. This avoids letting prior outperformance mask a
    weak later start, which is the rolling-start robustness concern in
    `[testing_tuning, p.327-335]`.
    """
    if horizon_years <= 0:
        raise ValueError("horizon_years must be positive")
    aligned = pd.concat(
        {
            "strategy": strategy_returns.dropna().astype(float),
            "benchmark": benchmark_returns.dropna().astype(float),
        },
        axis=1,
    ).dropna()
    if aligned.empty:
        return pd.DataFrame(
            columns=[
                "start",
                "end",
                "n_obs",
                "pct_time_above_benchmark",
                "terminal_relative",
                "min_relative_equity",
                "relative_mdd",
            ]
        )

    first_month_end = aligned.index[0].to_period("M").to_timestamp("M")
    last_date = pd.Timestamp(aligned.index[-1])
    starts = pd.date_range(first_month_end, last_date, freq="ME")
    rows: list[dict[str, object]] = []
    min_obs = int(horizon_years * TRADING_DAYS_PER_YEAR * 0.75)
    for start in starts:
        end = pd.Timestamp(start) + pd.DateOffset(years=horizon_years)
        if end > last_date:
            continue
        window = aligned.loc[(aligned.index > start) & (aligned.index <= end)]
        if len(window) < min_obs:
            continue
        strategy_eq = (1.0 + window["strategy"]).cumprod()
        benchmark_eq = (1.0 + window["benchmark"]).cumprod()
        ratio_body = strategy_eq / benchmark_eq
        ratio = pd.concat([pd.Series([1.0], index=[pd.Timestamp(start)]), ratio_body])
        relative_drawdown = ratio / ratio.cummax() - 1.0
        rows.append(
            {
                "start": pd.Timestamp(start),
                "end": pd.Timestamp(end),
                "n_obs": int(len(window)),
                "pct_time_above_benchmark": float((ratio >= 1.0).mean()),
                "terminal_relative": float(ratio.iloc[-1]),
                "min_relative_equity": float(ratio.min()),
                "relative_mdd": float(relative_drawdown.min()),
            }
        )
    return pd.DataFrame(rows)


def empty_rolling_relative_equity_metrics(
    horizons: tuple[int, ...] = RELATIVE_EQUITY_HORIZONS,
) -> dict[str, float]:
    out = {
        "rolling_rel_score": float("nan"),
        "rolling_rel_p25_score": float("nan"),
        "rolling_rel_min_score": float("nan"),
    }
    for horizon in horizons:
        prefix = f"rel_{horizon}y"
        out.update(
            {
                f"{prefix}_windows": 0.0,
                f"{prefix}_above_mean": float("nan"),
                f"{prefix}_above_p25": float("nan"),
                f"{prefix}_above_min": float("nan"),
                f"{prefix}_terminal_median": float("nan"),
                f"{prefix}_min_relative_p25": float("nan"),
                f"{prefix}_relative_mdd_median": float("nan"),
            }
        )
    return out


def rolling_relative_equity_metrics(
    strategy_returns: pd.Series,
    benchmark_returns: pd.Series,
    horizons: tuple[int, ...] = RELATIVE_EQUITY_HORIZONS,
    weights: dict[int, float] | None = None,
) -> dict[str, float]:
    """Aggregate monthly rolling Strategy/SPY dominance diagnostics.

    The horizon score is the mean percentage of days where the reset relative
    equity curve is at or above `1.0`. Longer horizons receive larger default
    weights to emphasize durable dominance over short noisy windows
    `[testing_tuning, p.327-335]`.
    """
    weights = weights or RELATIVE_EQUITY_WEIGHTS
    out = empty_rolling_relative_equity_metrics(horizons)
    weighted_means: list[tuple[float, float]] = []
    weighted_p25: list[tuple[float, float]] = []
    horizon_mins: list[float] = []

    for horizon in horizons:
        windows = rolling_relative_equity_windows(strategy_returns, benchmark_returns, horizon)
        prefix = f"rel_{horizon}y"
        out[f"{prefix}_windows"] = float(len(windows))
        if windows.empty:
            continue
        above = windows["pct_time_above_benchmark"].to_numpy(dtype=float)
        terminals = windows["terminal_relative"].to_numpy(dtype=float)
        mins = windows["min_relative_equity"].to_numpy(dtype=float)
        relative_mdds = windows["relative_mdd"].to_numpy(dtype=float)
        above_mean = float(np.nanmean(above))
        above_p25 = float(np.nanpercentile(above, 25))
        above_min = float(np.nanmin(above))
        out.update(
            {
                f"{prefix}_above_mean": above_mean,
                f"{prefix}_above_p25": above_p25,
                f"{prefix}_above_min": above_min,
                f"{prefix}_terminal_median": float(np.nanmedian(terminals)),
                f"{prefix}_min_relative_p25": float(np.nanpercentile(mins, 25)),
                f"{prefix}_relative_mdd_median": float(np.nanmedian(relative_mdds)),
            }
        )
        weight = float(weights.get(horizon, 0.0))
        if weight > 0.0:
            weighted_means.append((above_mean, weight))
            weighted_p25.append((above_p25, weight))
        horizon_mins.append(above_min)

    if weighted_means:
        total_weight = sum(weight for _value, weight in weighted_means)
        out["rolling_rel_score"] = sum(value * weight for value, weight in weighted_means) / total_weight
    if weighted_p25:
        total_weight = sum(weight for _value, weight in weighted_p25)
        out["rolling_rel_p25_score"] = sum(value * weight for value, weight in weighted_p25) / total_weight
    if horizon_mins:
        out["rolling_rel_min_score"] = float(np.nanmin(horizon_mins))
    return out


def walk_forward_diagnostic(returns: pd.Series) -> dict[str, float]:
    """Compact 8-window positive-OOS diagnostic."""
    n = len(returns)
    window = n // 9
    if window < 63:
        return {"wf_windows": 0.0, "wf_positive": 0.0, "wf_pass": 0.0}
    oos_returns: list[float] = []
    for _, test_range in walk_forward_splits(n, window, window, window):
        r = returns.iloc[list(test_range)]
        oos_returns.append(float((1.0 + r).prod() - 1.0))
        if len(oos_returns) >= 8:
            break
    positive = sum(value > 0.0 for value in oos_returns)
    return {
        "wf_windows": float(len(oos_returns)),
        "wf_positive": float(positive),
        "wf_pass": float(len(oos_returns) >= 8 and positive >= 6),
    }


def result_row(
    config: ExtensiveConfig,
    simulation: SimulationResult,
    benchmark_prices: pd.DataFrame,
    n_trials: int,
    ranked_returns: pd.Series | None = None,
    tax_summary: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build one flat result row for CSV/JSON reports."""
    ranked_returns = ranked_returns if ranked_returns is not None else simulation.returns
    strategy_returns, bench_returns = benchmark_returns_for(ranked_returns, benchmark_prices)
    gross_returns, _gross_bench = benchmark_returns_for(simulation.returns, benchmark_prices)
    metrics = metrics_from_returns(strategy_returns)
    gross_metrics = metrics_from_returns(gross_returns)
    bench_metrics = metrics_from_returns(bench_returns)
    rel = relative_equity_metrics(strategy_returns, bench_returns)
    rolling_rel = rolling_relative_equity_metrics(strategy_returns, bench_returns)
    wf = walk_forward_diagnostic(strategy_returns)
    p_value = 1.0
    if len(strategy_returns) >= 3:
        arr = strategy_returns.to_numpy(dtype=float)
        if n_trials >= 2:
            p_value = float(dsr(arr, n_trials=n_trials).p_value)
        else:
            p_value = 1.0 - float(psr(arr, benchmark=0.0))
    oos = strategy_returns.iloc[int(len(strategy_returns) * 0.70) :]
    fwd = strategy_returns[strategy_returns.index >= "2020-01-01"]
    return {
        "name": config.name,
        "universe": config.universe,
        "mechanism": config.mechanism,
        "score_mode": config.score_mode,
        "weight_mode": config.weight_mode,
        "absolute_filter": config.absolute_filter,
        "top_n": config.top_n,
        "rebalance_months": config.rebalance_months,
        "rebalance_offset": config.rebalance_offset,
        "start": metrics["start"],
        "end": metrics["end"],
        "n_obs": metrics["n_obs"],
        "cagr": metrics["cagr"],
        "after_tax_cagr": metrics["cagr"],
        "gross_cagr": gross_metrics["cagr"],
        "tax_drag_cagr": float(gross_metrics["cagr"]) - float(metrics["cagr"]),
        "mdd": metrics["mdd"],
        "after_tax_mdd": metrics["mdd"],
        "gross_mdd": gross_metrics["mdd"],
        "vol": metrics["vol"],
        "after_tax_vol": metrics["vol"],
        "gross_vol": gross_metrics["vol"],
        "sharpe": metrics["sharpe"],
        "after_tax_sharpe": metrics["sharpe"],
        "gross_sharpe": gross_metrics["sharpe"],
        "sortino": metrics["sortino"],
        "calmar": metrics["calmar"],
        "after_tax_calmar": metrics["calmar"],
        "gross_calmar": gross_metrics["calmar"],
        "terminal": metrics["terminal"],
        "after_tax_terminal": metrics["terminal"],
        "gross_terminal": gross_metrics["terminal"],
        "spy_cagr": bench_metrics["cagr"],
        "spy_mdd": bench_metrics["mdd"],
        "spy_vol": bench_metrics["vol"],
        "spy_sharpe": bench_metrics["sharpe"],
        "excess_cagr": float(metrics["cagr"]) - float(bench_metrics["cagr"]),
        "excess_sharpe": float(metrics["sharpe"]) - float(bench_metrics["sharpe"]),
        "mdd_delta": float(metrics["mdd"]) - float(bench_metrics["mdd"]),
        "vol_delta": float(metrics["vol"]) - float(bench_metrics["vol"]),
        "pct_time_above_spy": rel["pct_time_above_benchmark"],
        "min_relative_equity": rel["min_relative_equity"],
        "terminal_relative": rel["terminal_relative"],
        **rolling_rel,
        "dsr_p_value": p_value,
        "oos_sharpe": float(sharpe(oos, TRADING_DAYS_PER_YEAR)) if len(oos) else float("nan"),
        "fwd_sharpe": float(sharpe(fwd, TRADING_DAYS_PER_YEAR)) if len(fwd) else float("nan"),
        "total_tax_paid": float((tax_summary or {}).get("total_tax_paid", 0.0)),
        "tax_paid_pct_initial": float((tax_summary or {}).get("tax_paid_pct_initial", 0.0)),
        "tax_events": int((tax_summary or {}).get("tax_events", 0)),
        "years_taxed": int((tax_summary or {}).get("years_taxed", 0)),
        "loss_carryforward_final": float(
            (tax_summary or {}).get("loss_carryforward_final", 0.0)
        ),
        **wf,
        **simulation.turnover,
    }


def make_config_name(
    universe: str,
    mechanism: str,
    top_n: int,
    rebalance_months: int,
    offset: int,
) -> str:
    return f"mom13612_{universe}_{mechanism}_top{top_n}_reb{rebalance_months}_off{offset}"
