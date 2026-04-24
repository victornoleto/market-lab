"""Iter 023 — Time-series trend-following on 3-asset basket.

Mechanism (structurally different from iter 016/022):
-----------------------------------------------------
For each asset i ∈ {equity, TLT, GLD}, at bar t:

    signal_i[t]   = sign( Σ_{s=t-lookback-skip+1}^{t-skip} log(1 + r_i[s]) )
    σ̂_i[t-1]     = rolling σ of r_i over [t-vol_lookback, t-1] × √252
    raw_pos_i[t] = signal_i[t] · target_vol_per_asset / σ̂_i[t-1]
    gross[t]      = Σ_i |raw_pos_i[t]|
    shrink[t]     = min(1, max_leverage / gross[t])   if gross > 0
    pos_i[t]      = raw_pos_i[t] · shrink[t]
    net[t]        = Σ_i pos_i[t] · r_i[t] − Σ_i |Δpos_i[t]| · cost_bps

Crucially each leg is vol-targeted INDEPENDENTLY (no σ²_port feedback),
so the scale feedback that absorbed every overlay tried on iter 016 base
(iter 014/017/019/020/021/022) no longer applies. Short positions are
permitted when the trend signal is negative, breaking iter 016's
structural long-only geometry.

Citations
---------
* `[algo_trading_chan, p.164, ch.6]` — Moskowitz-Yao-Pedersen 2012 /
  12-month time-series momentum lookback + ~21-day rebalance; "the
  12-month lookback has academic support across many asset classes.
  Curve-fit risk: low (published, replicated across many markets)".
* `[systematic_trading, p.40, ch.2]` — volatility standardisation as
  the primitive for applying one trading rule across instruments.
* `[systematic_trading, p.159-160, ch.10]` — volatility scalar per
  instrument: position = target_vol / instrument_vol.
* `[systematic_trading, p.170-171, ch.11]` — IDM ≤ 2.5 leverage cap.
* `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag discipline.

Papers:
* Moskowitz, Ooi, Pedersen (2012). "Time Series Momentum." JFE 104(2).
* Hurst, Ooi, Pedersen (2017). "A Century of Evidence on Trend-Following
  Investing." JPM 44(1).
* Baltas, Kosowski (2020). "Demystifying Time-Series Momentum Strategies."
  Management Science 66(10).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_trend_signal(
    returns: pd.DataFrame,
    *,
    lookback: int = 252,
    skip: int = 21,
) -> pd.DataFrame:
    """Time-series momentum sign signal (Moskowitz-Ooi-Pedersen 2012).

    Parameters
    ----------
    returns : pd.DataFrame
        Simple daily returns, one column per asset.
    lookback : int
        Formation window in bars (default 252 = 12 months).
    skip : int
        Skip-a-month offset in bars (default 21 = 1 month). The feature
        at bar t uses returns from bar (t - lookback - skip + 1) to bar
        (t - skip). This skip prevents 1-month-reversal contamination
        (Jegadeesh-Titman 1993).

    Returns
    -------
    pd.DataFrame
        signal in {-1, 0, +1}, same index/columns as ``returns``. NaN
        for bars before (lookback + skip) warmup.

    Citations
    ---------
    * `[algo_trading_chan, p.164, ch.6]` — 12-month TSM lookback.
    * `[stocks_on_the_move, p.58, p.60]` — Jegadeesh-Titman 1993 anchor.
    """
    if lookback < 2:
        raise ValueError(f"lookback must be ≥ 2, got {lookback}")
    if skip < 0:
        raise ValueError(f"skip must be ≥ 0, got {skip}")

    log_r = np.log1p(returns.astype(float))
    # Rolling-sum window ending at t uses bars [t-lookback+1, t];
    # shift by (skip + 0) pushes value at t to use bars ending at (t - skip).
    # To avoid touching r[t] itself (ensuring signal[t] depends only on past),
    # we shift by skip — the rolling sum at (t - skip) uses bars
    # [t - skip - lookback + 1, t - skip], max bar = t - skip ≤ t - 1 when skip ≥ 1.
    feature = log_r.rolling(lookback, min_periods=lookback).sum().shift(skip)
    signal = np.sign(feature).astype(float)
    return signal


def apply_trend_3etf(
    returns: pd.DataFrame,
    *,
    signal_lookback: int = 252,
    signal_skip: int = 21,
    vol_lookback: int = 21,
    target_vol_per_asset: float = 0.10,
    max_leverage: float = 2.0,
    cost_bps_per_leg: float = 0.0002,
    periods_per_year: int = 252,
) -> tuple[pd.Series, pd.DataFrame, pd.Series, pd.DataFrame]:
    """Three-asset time-series trend-following with per-asset vol-target.

    Parameters
    ----------
    returns : pd.DataFrame
        Simple daily returns with exactly 3 columns (equity, bond, gold).
    signal_lookback, signal_skip : int
        12-1 momentum formation (252/21 canonical per Moskowitz 2012).
    vol_lookback : int
        Rolling σ̂ window (21-day canonical per iter 016 / Carver).
    target_vol_per_asset : float
        Annualised vol target per leg BEFORE cap (default 10 %).
    max_leverage : float
        Total gross-exposure cap; Σ_i |pos_i[t]| ≤ max_leverage
        (IDM ≤ 2.5 per Carver ch.11, we default to 2.0 to match iter 016).
    cost_bps_per_leg : float
        Linear cost per unit of per-leg ∆position (default 2 bps).
    periods_per_year : int
        Annualisation factor (default 252).

    Returns
    -------
    (net_returns, positions, total_gross, signals)
        * ``net_returns`` : pd.Series of net daily returns (after cost).
        * ``positions`` : pd.DataFrame of per-leg positions (signed).
        * ``total_gross`` : pd.Series of Σ_i |pos_i|.
        * ``signals`` : pd.DataFrame of trend signs in {-1, 0, +1}.
        All indexed on the valid bars (warmup dropped).

    Raises
    ------
    ValueError
        If ``returns`` does not have exactly 3 columns, params are out
        of domain, or there are fewer than ``signal_lookback +
        signal_skip + 1`` overlapping bars.
    """
    if signal_lookback < 2:
        raise ValueError(f"signal_lookback must be ≥ 2, got {signal_lookback}")
    if signal_skip < 0:
        raise ValueError(f"signal_skip must be ≥ 0, got {signal_skip}")
    if vol_lookback < 2:
        raise ValueError(f"vol_lookback must be ≥ 2, got {vol_lookback}")
    if target_vol_per_asset <= 0:
        raise ValueError(f"target_vol_per_asset must be > 0, got {target_vol_per_asset}")
    if max_leverage <= 0:
        raise ValueError(f"max_leverage must be > 0, got {max_leverage}")
    if returns.shape[1] != 3:
        raise ValueError(
            f"returns must have exactly 3 asset columns, got {returns.shape[1]}"
        )

    r = returns.astype(float).dropna(how="any")
    required_bars = signal_lookback + signal_skip + 1
    if len(r) <= required_bars:
        raise ValueError(
            f"need > {required_bars} overlapping bars, got {len(r)}"
        )

    # Trend signal per leg.
    signals = compute_trend_signal(r, lookback=signal_lookback, skip=signal_skip)

    # Per-asset σ̂_{t-1} (rolling 21-day std annualised, shifted 1).
    ann_sigma = (
        r.rolling(vol_lookback, min_periods=vol_lookback).std(ddof=0)
        * np.sqrt(periods_per_year)
    ).shift(1)

    # Raw per-asset position = signal × target_vol / σ̂.
    # Where σ̂ is 0 or NaN, position is NaN (propagated).
    raw_pos = signals * (target_vol_per_asset / ann_sigma.replace(0.0, np.nan))

    # Drop warmup NaN rows (bars before max(signal_warmup, vol_warmup)).
    valid = raw_pos.dropna(how="any")
    if len(valid) == 0:
        raise ValueError("no valid bars after warmup; increase dataset length")

    # Enforce leverage cap via proportional shrink.
    gross_raw = valid.abs().sum(axis=1)
    shrink = (max_leverage / gross_raw).clip(upper=1.0)
    # When gross_raw == 0, shrink → inf by division; handle by setting 1.
    shrink = shrink.where(gross_raw > 0.0, 1.0)
    positions = valid.mul(shrink, axis=0)

    total_gross = positions.abs().sum(axis=1).rename("total_gross")

    # P&L aggregation + cost.
    r_valid = r.loc[positions.index]
    gross_ret = (positions * r_valid).sum(axis=1)
    dpos = positions.diff()
    # First-bar Δpos = |initial position| (built up from zero).
    dpos.iloc[0] = positions.iloc[0].abs()
    cost = dpos.abs().sum(axis=1) * cost_bps_per_leg
    net = (gross_ret - cost).astype(float)
    net.name = "net"

    return net, positions, total_gross, signals.loc[positions.index]
