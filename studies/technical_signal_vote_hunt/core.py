"""Core utilities for the technical signal vote hunt.

Stage 1 is close-only and uses testfolio long-history price series. Stage 2 uses
Tiingo adjusted OHLC on real ETF inception windows. Signal
choices cite the project knowledge base: moving-average trend filters follow
Gayed `[leverage_for_the_long_run, p.13]`; RSI/MACD/ROC definitions follow
Kaufman `[trading_systems_methods, p.382-386]`; realized-vol gates follow the
LETF volatility decay rationale `[leverage_for_the_long_run, p.5-6]`.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252


@dataclass(frozen=True)
class BranchSpec:
    """One branch/risk-on leg in the Stage 1 grid."""

    branch: str
    signal_ticker: str
    risk_on_ticker: str
    benchmark_ticker: str
    risk_on_label: str


STAGE1_BRANCHES: tuple[BranchSpec, ...] = (
    BranchSpec("SPY", "SPYSIM", "SSOSIM", "SPYSIM", "SSO_2x"),
    BranchSpec("SPY", "SPYSIM", "UPROSIM", "SPYSIM", "UPRO_3x"),
    BranchSpec("QQQ", "QQQSIM", "QLDSIM", "QQQSIM", "QLD_2x"),
    BranchSpec("QQQ", "QQQSIM", "TQQQSIM", "QQQSIM", "TQQQ_3x"),
)


def daily_returns(prices: pd.Series) -> pd.Series:
    """Close-to-close simple returns."""
    return prices.astype(float).pct_change().replace([np.inf, -np.inf], np.nan)


def equity_from_returns(returns: pd.Series, base: float = 10_000.0) -> pd.Series:
    """Compound daily returns into an equity curve."""
    return (1.0 + returns.fillna(0.0)).cumprod() * base


def sma(prices: pd.Series, period: int) -> pd.Series:
    return prices.rolling(period, min_periods=period).mean()


def ema(prices: pd.Series, period: int) -> pd.Series:
    return prices.ewm(span=period, min_periods=period, adjust=False).mean()


def rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Wilder-style RSI approximation using rolling average gains/losses."""
    delta = prices.diff()
    gain = delta.clip(lower=0.0).rolling(period, min_periods=period).mean()
    loss = (-delta.clip(upper=0.0)).rolling(period, min_periods=period).mean()
    rs = gain / loss.replace(0.0, np.nan)
    out = 100.0 - (100.0 / (1.0 + rs))
    return out.fillna(50.0).where(gain.notna())


def stoch_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    r = rsi(prices, period)
    lo = r.rolling(period, min_periods=period).min()
    hi = r.rolling(period, min_periods=period).max()
    return (r - lo) / (hi - lo).replace(0.0, np.nan) * 100.0


def macd(prices: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    """MACD(12,26,9)."""
    line = ema(prices, 12) - ema(prices, 26)
    signal = line.ewm(span=9, min_periods=9, adjust=False).mean()
    hist = line - signal
    return line, signal, hist


def realized_vol(returns: pd.Series, window: int = 21) -> pd.Series:
    return returns.rolling(window, min_periods=window).std() * np.sqrt(TRADING_DAYS_PER_YEAR)


def ar1(returns: pd.Series, window: int = 30) -> pd.Series:
    def _corr(x: np.ndarray) -> float:
        if len(x) < 2 or np.any(np.isnan(x)):
            return np.nan
        a = x[:-1]
        b = x[1:]
        if np.std(a) <= 1e-12 or np.std(b) <= 1e-12:
            return 0.0
        return float(np.corrcoef(a, b)[0, 1])

    return returns.rolling(window, min_periods=window).apply(_corr, raw=True)


def build_close_only_signals(prices: pd.Series) -> dict[str, pd.Series]:
    """Build Stage 1 binary close-only signals on one underlying price series."""
    px = prices.astype(float)
    ret = daily_returns(px)
    out: dict[str, pd.Series] = {}

    for period in (5, 10, 20, 50, 100, 150, 200, 250):
        ma = sma(px, period)
        out[f"px_gt_sma{period}"] = _binary(px > ma, ma.notna())
        ea = ema(px, period)
        out[f"px_gt_ema{period}"] = _binary(px > ea, ea.notna())

    for short, long in ((20, 100), (50, 200), (100, 250), (50, 150)):
        s = sma(px, short)
        l = sma(px, long)
        out[f"sma{short}_gt_sma{long}"] = _binary(s > l, s.notna() & l.notna())

    macd_line, macd_signal, macd_hist = macd(px)
    out["macd_gt_signal"] = _binary(macd_line > macd_signal, macd_signal.notna())
    out["macd_hist_gt_0"] = _binary(macd_hist > 0.0, macd_hist.notna())

    for period in (10, 20, 60, 120):
        roc = px.pct_change(period)
        out[f"roc{period}_gt_0"] = _binary(roc > 0.0, roc.notna())

    r = rsi(px, 14)
    out["rsi14_gt_50"] = _binary(r > 50.0, r.notna())
    out["rsi14_rising"] = _binary(r.diff() > 0.0, r.notna() & r.shift(1).notna())

    srsi = stoch_rsi(px, 14)
    out["stochrsi14_gt_50"] = _binary(srsi > 50.0, srsi.notna())

    rv21 = realized_vol(ret, 21)
    out["rv21_lt_40"] = _binary(rv21 < 0.40, rv21.notna())
    rv_pct = rv21.rolling(1260, min_periods=252).rank(pct=True)
    out["rv21_pct_lt_50"] = _binary(rv_pct < 0.50, rv_pct.notna())
    out["rv21_pct_lt_70"] = _binary(rv_pct < 0.70, rv_pct.notna())

    a1 = ar1(ret, 30)
    out["ar1_30_gt_0"] = _binary(a1 > 0.0, a1.notna())
    return out


def adjusted_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    """Build split/dividend-adjusted OHLC from Tiingo daily bars.

    Tiingo provides raw OHLC plus adjusted close. High/low indicators must use
    adjusted OHLC so their levels are consistent with adjusted-close returns
    `[quant_trading_chan, p.37]`.
    """
    required = {"open", "high", "low", "close", "adj_close"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"missing OHLC columns: {sorted(missing)}")
    factor = df["adj_close"].astype(float) / df["close"].astype(float)
    out = pd.DataFrame(index=df.index)
    out["open"] = df["open"].astype(float) * factor
    out["high"] = df["high"].astype(float) * factor
    out["low"] = df["low"].astype(float) * factor
    out["close"] = df["adj_close"].astype(float)
    out["volume"] = df["volume"].astype(float) if "volume" in df.columns else np.nan
    return out


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)
    vals = pd.concat(
        [(high - low).abs(), (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    )
    return vals.max(axis=1)


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Average True Range, used as a volatility/range filter `[trading_systems_methods, p.732-733]`."""
    return true_range(high, low, close).rolling(period, min_periods=period).mean()


def adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """ADX trend-strength approximation `[trading_systems_methods, p.443-445]`."""
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0.0), up_move, 0.0), index=high.index)
    minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0.0), down_move, 0.0), index=high.index)
    tr = true_range(high, low, close)
    atr_sum = tr.rolling(period, min_periods=period).sum().replace(0.0, np.nan)
    plus_di = 100.0 * plus_dm.rolling(period, min_periods=period).sum() / atr_sum
    minus_di = 100.0 * minus_dm.rolling(period, min_periods=period).sum() / atr_sum
    dx = 100.0 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0.0, np.nan)
    return dx.rolling(period, min_periods=period).mean()


def stochastic_k(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Fast stochastic %K `[trading_systems_methods, p.394-396]`."""
    lo = low.rolling(period, min_periods=period).min()
    hi = high.rolling(period, min_periods=period).max()
    return 100.0 * (close - lo) / (hi - lo).replace(0.0, np.nan)


def williams_r(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Williams %R `[trading_systems_methods, p.397-398]`."""
    lo = low.rolling(period, min_periods=period).min()
    hi = high.rolling(period, min_periods=period).max()
    return -100.0 * (hi - close) / (hi - lo).replace(0.0, np.nan)


def cci(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
    """Commodity Channel Index `[trading_systems_methods, p.407-409]`."""
    typical = (high + low + close) / 3.0
    ma = typical.rolling(period, min_periods=period).mean()

    def _mad(x: np.ndarray) -> float:
        return float(np.mean(np.abs(x - np.mean(x))))

    mad = typical.rolling(period, min_periods=period).apply(_mad, raw=True)
    return (typical - ma) / (0.015 * mad.replace(0.0, np.nan))


def ultimate_oscillator(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    short: int = 7,
    medium: int = 14,
    long: int = 28,
) -> pd.Series:
    """Ultimate Oscillator `[trading_systems_methods, p.399-401]`."""
    prev_close = close.shift(1)
    bp = close - pd.concat([low, prev_close], axis=1).min(axis=1)
    tr = pd.concat([high, prev_close], axis=1).max(axis=1) - pd.concat([low, prev_close], axis=1).min(axis=1)

    def _avg(window: int) -> pd.Series:
        return bp.rolling(window, min_periods=window).sum() / tr.rolling(window, min_periods=window).sum().replace(0.0, np.nan)

    return 100.0 * (4.0 * _avg(short) + 2.0 * _avg(medium) + _avg(long)) / 7.0


def build_ohlc_signals(ohlc: pd.DataFrame) -> dict[str, pd.Series]:
    """Build Stage 2 OHLC-derived binary signals on adjusted daily bars."""
    high = ohlc["high"].astype(float)
    low = ohlc["low"].astype(float)
    close = ohlc["close"].astype(float)
    out: dict[str, pd.Series] = {}

    adx14 = adx(high, low, close, 14)
    out["adx14_gt_20"] = _binary(adx14 > 20.0, adx14.notna())
    out["adx14_gt_25"] = _binary(adx14 > 25.0, adx14.notna())

    atr14_pct = atr(high, low, close, 14) / close
    out["atr14_pct_lt_3"] = _binary(atr14_pct < 0.03, atr14_pct.notna())
    out["atr14_pct_lt_5"] = _binary(atr14_pct < 0.05, atr14_pct.notna())

    stoch14 = stochastic_k(high, low, close, 14)
    out["stoch14_gt_50"] = _binary(stoch14 > 50.0, stoch14.notna())
    out["stoch14_gt_80"] = _binary(stoch14 > 80.0, stoch14.notna())

    wr14 = williams_r(high, low, close, 14)
    out["willr14_gt_m50"] = _binary(wr14 > -50.0, wr14.notna())

    cci20 = cci(high, low, close, 20)
    out["cci20_gt_0"] = _binary(cci20 > 0.0, cci20.notna())
    out["cci20_gt_100"] = _binary(cci20 > 100.0, cci20.notna())

    ult = ultimate_oscillator(high, low, close)
    out["ultosc_gt_50"] = _binary(ult > 50.0, ult.notna())

    for period in (20, 55):
        prior_high = high.rolling(period, min_periods=period).max().shift(1)
        out[f"close_gt_prior_high{period}"] = _binary(close > prior_high, prior_high.notna())

    ema13 = ema(close, 13)
    bull_power = high - ema13
    bear_power = low - ema13
    out["bull_power_gt_0"] = _binary(bull_power > 0.0, ema13.notna())
    out["bear_power_gt_0"] = _binary(bear_power > 0.0, ema13.notna())
    return out


def vote_signal(signals: list[pd.Series], k: int) -> pd.Series:
    """Return 1 when at least k component signals are true; lag elsewhere."""
    if not signals:
        raise ValueError("vote_signal requires at least one signal")
    if k < 1 or k > len(signals):
        raise ValueError(f"invalid k={k} for {len(signals)} signals")
    df = pd.concat(signals, axis=1)
    valid = ~df.isna().any(axis=1)
    out = (df.sum(axis=1) >= k).astype(float)
    out[~valid] = np.nan
    return out


def simulate_on_off(
    signal: pd.Series,
    on_returns: pd.Series,
    off_returns: pd.Series,
) -> pd.Series:
    """Simulate close-to-close ON/OFF returns with a 1-day signal lag.

    The lag avoids same-close look-ahead: signal[t-1] earns return[t]
    `[advances_fin_ml, p.31-34]`.
    """
    aligned = pd.concat(
        {"sig": signal, "on": on_returns, "off": off_returns}, axis=1, sort=False
    ).dropna()
    is_on = aligned["sig"].shift(1).fillna(0.0).eq(1.0)
    return pd.Series(np.where(is_on, aligned["on"], aligned["off"]), index=aligned.index)


def build_t3d_k2_signal(prices: pd.Series) -> pd.Series:
    """T3d-K2 transplant signal on the supplied underlying."""
    sigs = build_close_only_signals(prices)
    return vote_signal(
        [
            sigs["px_gt_sma250"],
            sigs["px_gt_sma100"],
            sigs["rv21_lt_40"],
            sigs["ar1_30_gt_0"],
        ],
        k=2,
    )


def build_rearm_gate(master_signal: pd.Series, t_crash: int = 35, d_arm: int = 60) -> pd.Series:
    """Post-crash rearm gate used for iter030-like branch-native controls.

    A rearm window opens when the master signal flips OFF->ON after at least
    `t_crash` consecutive OFF days, matching the documented iter030 state
    machine `[leverage_for_the_long_run, p.6-7, ch.3]`.
    """
    sig = master_signal.fillna(0.0).astype(float)
    off_count = 0
    rearm_left = 0
    values: list[float] = []
    prev = 0.0
    for cur in sig:
        if cur <= 0.0:
            off_count += 1
            rearm_left = 0
            values.append(0.0)
        else:
            if prev <= 0.0 and off_count >= t_crash:
                rearm_left = d_arm
            values.append(1.0 if rearm_left > 0 else 0.0)
            if rearm_left > 0:
                rearm_left -= 1
            off_count = 0
        prev = cur
    out = pd.Series(values, index=master_signal.index)
    out[master_signal.isna()] = np.nan
    return out


def simulate_iter030_like(
    master_signal: pd.Series,
    on_returns: pd.Series,
    off_returns: pd.Series,
    lrs_factor: float = 1.20,
) -> pd.Series:
    """Branch-native iter030-like control: T3d-K2 + T35D60 + LRS1.20.

    This is a transparent transplant benchmark for this study, not a claim of
    bit-exact equivalence to the original QLD/ZROZ post-close backtest.
    """
    rearm = build_rearm_gate(master_signal)
    aligned = pd.concat(
        {"sig": master_signal, "rearm": rearm, "on": on_returns, "off": off_returns},
        axis=1,
        sort=False,
    ).dropna()
    sig_lag = aligned["sig"].shift(1).fillna(0.0).eq(1.0)
    rearm_lag = aligned["rearm"].shift(1).fillna(0.0).eq(1.0)
    on_leg = np.where(rearm_lag, aligned["on"] * lrs_factor, aligned["on"])
    daily = np.where(sig_lag, on_leg, aligned["off"])
    return pd.Series(daily, index=aligned.index)


def _binary(condition: pd.Series, valid: pd.Series) -> pd.Series:
    out = condition.astype(float)
    out[~valid] = np.nan
    return out
