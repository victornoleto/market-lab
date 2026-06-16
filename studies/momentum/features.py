"""Feature precomputation for momentum strategy families."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


TRADING_DAYS_PER_YEAR = 252


@dataclass(frozen=True)
class FeatureBundle:
    monthly_prices: pd.DataFrame
    monthly_vol: pd.DataFrame
    scores: dict[str, pd.DataFrame]


def canonicalize_prices(prices: pd.DataFrame) -> pd.DataFrame:
    out = prices.copy().sort_index()
    out.columns = [str(column).upper() for column in out.columns]
    return out.astype(float)


def momentum_score(monthly_prices: pd.DataFrame, lookbacks: Iterable[int]) -> pd.DataFrame:
    """Mean of configured monthly returns `[stocks_on_the_move, p.60]`."""
    prices = canonicalize_prices(monthly_prices)
    components = [prices / prices.shift(int(months)) - 1.0 for months in lookbacks]
    return pd.concat(components, keys=range(len(components))).groupby(level=1).mean()


def mom_12_1(monthly_prices: pd.DataFrame) -> pd.DataFrame:
    """12-month momentum excluding the most recent month."""
    prices = canonicalize_prices(monthly_prices)
    return prices.shift(1) / prices.shift(12) - 1.0


def realized_volatility(prices: pd.DataFrame, window_days: int) -> pd.DataFrame:
    returns = canonicalize_prices(prices).pct_change(fill_method=None)
    return returns.rolling(window_days, min_periods=window_days).std() * np.sqrt(
        TRADING_DAYS_PER_YEAR
    )


def clenow_trend_scores(prices: pd.DataFrame, window_days: int) -> pd.DataFrame:
    """Annualized log-price regression slope times R².

    This is the Clenow adjusted-slope style trend score, rewarding smooth trends
    over jumpy returns `[stocks_on_the_move, p.70-77, p.98]`.
    """
    if window_days < 3:
        raise ValueError("trend window must be >= 3")
    log_prices = np.log(canonicalize_prices(prices).replace(0.0, np.nan))
    out = pd.DataFrame(index=log_prices.index, columns=log_prices.columns, dtype=float)
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


def composite_momentum_lowvol(momentum: pd.DataFrame, monthly_vol: pd.DataFrame) -> pd.DataFrame:
    """70/30 cross-sectional rank blend of momentum and low realized vol."""
    mom_rank = momentum.rank(axis=1, pct=True)
    lowvol_rank = (-monthly_vol).rank(axis=1, pct=True)
    return 0.70 * mom_rank + 0.30 * lowvol_rank


def precompute_features(
    prices: pd.DataFrame,
    *,
    score_modes: Iterable[str],
    raw_lookbacks: Iterable[int] = (1, 3, 6, 12),
    mom_3_6_12_lookbacks: Iterable[int] = (3, 6, 12),
    vol_window_days: int = 126,
    trend_window_days: int = 126,
) -> FeatureBundle:
    """Precompute all requested monthly score frames for one universe."""
    daily = canonicalize_prices(prices)
    monthly_prices = daily.resample("ME").last()
    monthly_vol = realized_volatility(daily, vol_window_days).resample("ME").last()
    raw = momentum_score(monthly_prices, raw_lookbacks)
    scores: dict[str, pd.DataFrame] = {}
    requested = set(score_modes)
    if "raw_13612" in requested or "vol_adjusted" in requested or "mom_lowvol_composite" in requested:
        scores["raw_13612"] = raw
    if "mom_12_1" in requested:
        scores["mom_12_1"] = mom_12_1(monthly_prices)
    if "mom_3_6_12" in requested:
        scores["mom_3_6_12"] = momentum_score(monthly_prices, mom_3_6_12_lookbacks)
    if "clenow_trend" in requested:
        scores["clenow_trend"] = clenow_trend_scores(daily, trend_window_days).resample("ME").last()
    if "vol_adjusted" in requested:
        scores["vol_adjusted"] = raw / monthly_vol.replace(0.0, np.nan)
    if "mom_lowvol_composite" in requested:
        scores["mom_lowvol_composite"] = composite_momentum_lowvol(raw, monthly_vol)
    missing = requested - set(scores)
    if missing:
        raise ValueError(f"unknown score modes: {sorted(missing)}")
    return FeatureBundle(monthly_prices=monthly_prices, monthly_vol=monthly_vol, scores=scores)
