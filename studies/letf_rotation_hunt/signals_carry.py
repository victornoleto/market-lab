"""Per-asset carry forecast for T5b — Carver framework.

carry_raw[t]    = expected_yield[t] - leverage[asset] * FFR[t]
carry_norm[t]   = (carry_raw / rolling_std(carry_raw, 252)) * scalar
forecast[t]     = carry_norm.clip(-20, 20)

Citation: [systematic_trading, ch.9 p.180-190];
spec docs/specs/2026-05-08-t5-expansion-design.md §3.1.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt import data_loader_yields as dly


@dataclass(frozen=True)
class _AssetCarryConfig:
    yield_kind: str   # "equity_div", "bond_cmt", "none"
    yield_key: str    # e.g. "SPY", "30y", or ""
    leverage: float
    asset_class: str  # "equity", "bond", "gold"


_ASSET_CARRY_MAP: dict[str, _AssetCarryConfig] = {
    "UPRO": _AssetCarryConfig("equity_div", "SPY", 3.0, "equity"),
    "QLD":  _AssetCarryConfig("equity_div", "QQQ", 2.0, "equity"),
    "TQQQ": _AssetCarryConfig("equity_div", "QQQ", 3.0, "equity"),
    "TMF":  _AssetCarryConfig("bond_cmt",   "30y", 3.0, "bond"),
    "ZROZ": _AssetCarryConfig("bond_cmt",   "30y", 1.0, "bond"),
    "UGL":  _AssetCarryConfig("none",       "",    2.0, "gold"),
}

# Initial scalars; calibrated empirically in Task 11.
_CARRY_SCALAR_BY_CLASS: dict[str, float] = {
    "equity": 10.0,
    "bond": 10.0,
    "gold": 0.0,
}


def compute_carry_forecast(
    asset: str, asset_prices: pd.Series, ffr_daily: pd.Series, fdm: float = 1.0,
) -> pd.Series:
    if asset not in _ASSET_CARRY_MAP:
        raise ValueError(f"asset {asset!r} not in carry map; add to _ASSET_CARRY_MAP")
    cfg = _ASSET_CARRY_MAP[asset]
    if cfg.asset_class == "gold":
        return pd.Series(0.0, index=asset_prices.index, name=f"carry_{asset}")

    yield_series = _load_yield_for_asset(asset).reindex(asset_prices.index).ffill()
    # ffr_daily must be daily pct returns (e.g., from load_ffr_daily()); annualized here.
    ffr_annual = _ffr_daily_to_annual(ffr_daily).reindex(asset_prices.index).ffill()

    carry_raw = yield_series - cfg.leverage * ffr_annual
    # min_periods=126 means ~6 months of history before emitting a forecast;
    # earlier bars are NaN and dropped by callers via .dropna().
    carry_std = carry_raw.rolling(window=252, min_periods=126).std()
    scalar = _CARRY_SCALAR_BY_CLASS[cfg.asset_class]
    carry_norm = (carry_raw / carry_std) * scalar * fdm
    return carry_norm.clip(-20.0, 20.0).rename(f"carry_{asset}")


def _load_yield_for_asset(asset: str) -> pd.Series:
    cfg = _ASSET_CARRY_MAP[asset]
    if cfg.yield_kind == "equity_div":
        return dly.load_dividend_yield(cfg.yield_key)
    if cfg.yield_kind == "bond_cmt":
        return dly.load_constant_maturity_yield(cfg.yield_key)
    raise ValueError(f"yield_kind {cfg.yield_kind!r} not supported for asset {asset!r}")


def _ffr_daily_to_annual(ffr_daily: pd.Series) -> pd.Series:
    """ffr_daily is daily pct return ≈ FFR/252. Re-annualize."""
    return ffr_daily * 252.0


def compose_ewmac_carry(
    ewmac: pd.Series, carry: pd.Series, fdm: float = 1.41,
) -> pd.Series:
    """50/50 blend of EWMAC and carry forecasts with FDM.

    Both inputs must already be individually scaled to SD≈10.
    FDM=1.41 = 2-forecast diversification multiplier [Carver ch.9 p.185],
    [Carver Table 49 p.285].
    """
    blended = (ewmac + carry) / 2.0 * fdm
    return blended.clip(-20.0, 20.0)
