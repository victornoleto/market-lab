"""Iter 071 — SPY short-term mean-reversion stream (Connors-Alvarez RSI(2)).

Connors-Alvarez (2009) canonical RSI(2) buy-the-dip strategy with Chan
`[algo_trading_chan, p.95, ch.4]` 200-day SMA momentum filter. The stream
is structurally calm-aggressive: ON only when SPY > SMA200 and SPY is
in an extreme 1-2 day dip (RSI2 < threshold); OFF (cash earning rf_d)
during stress regimes. The combination produces high conditional Sharpe
in calm/bull markets and ~zero exposure in crashes — the structural
opposite of iter 046 + r_qqqt's defensive profile.

Strategy rules
--------------

    pos[t] = 0  while warming up (pre-SMA200 well-defined)
    if pos[t-1] == 0:                            # not in trade
        pos[t] = 1 if (SPY[t-1] > SMA200[t-1]
                       AND RSI2[t-1] < threshold) else 0
    else:                                         # in trade
        pos[t] = 0 if (SPY[t-1] > SMA_exit[t-1]) else 1

    r_mr[t] = pos[t] * r_spy[t] + (1 - pos[t]) * rf_d - cost[t]
    cost[t] = cost_bps * 1e-4 * |pos[t] - pos[t-1]|

All signals are at t-1, applied at t — strict no-peek per
`[advances_fin_ml, p.162-164]`.

Citations
---------
* `[algo_trading_chan, p.95, ch.4]` — Chan: momentum filter (price
  above long-term MA) on mean-reversion entry signal. Reduces fakeouts
  from genuinely bad fundamental drops.
* `[algo_trading_chan, p.153-154, ch.6]` — Chan: mean-reversion +
  momentum are explicitly complementary in a diversified portfolio.
* `[algo_trading_chan, p.183-184, ch.8]` — Chan: NEVER apply in-
  sample stop-losses to mean-reversion (they always lower backtest
  performance); set above max IS drawdown for regime hedge only.
* Connors, L., & Alvarez, C. (2009). *Short Term Trading Strategies
  That Work*. ISBN 978-0-9755513-2-7. Canonical RSI(2) rule set.
* Lo & MacKinlay (1988), DOI 10.1093/rfs/1.1.41 — empirical short-
  horizon mean-reversion in equity returns.
* `[advances_fin_ml, p.162-164]` — strict shift(1) on signal.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def wilder_rsi(prices: pd.Series, period: int = 2) -> pd.Series:
    """Wilder's RSI on a price series.

    Implements the canonical recursive smoothing:

        RS = avg_gain / avg_loss
        RSI = 100 - 100 / (1 + RS)

    where avg_gain[t] and avg_loss[t] are computed via Wilder's
    exponential smoothing (alpha = 1/period). The first `period`
    bars are seeded with the simple average of the up- and
    down-moves.

    Parameters
    ----------
    prices : pd.Series
        Adjusted-close prices indexed by date.
    period : int, default 2
        RSI lookback. Connors-Alvarez canonical = 2.

    Returns
    -------
    pd.Series
        RSI values in [0, 100], indexed on prices.index. The first
        `period` entries are NaN (warmup).

    Raises
    ------
    ValueError
        If `period <= 0`.
    """
    if period <= 0:
        raise ValueError(f"period must be > 0; got {period}")

    delta = prices.astype(float).diff()
    gains = delta.clip(lower=0.0)
    losses = (-delta).clip(lower=0.0)

    # Wilder smoothing via ewm with alpha=1/period, adjust=False.
    # Seeded on the simple mean of the first `period` bars.
    avg_gain = gains.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    avg_loss = losses.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()

    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    # When avg_loss == 0 and avg_gain > 0 → RS = inf → RSI = 100.
    rsi = rsi.where(~(avg_loss.eq(0.0) & avg_gain.gt(0.0)), 100.0)
    # When both avg_gain and avg_loss are zero (flat) → RSI undefined; use 50.
    rsi = rsi.where(~(avg_loss.eq(0.0) & avg_gain.eq(0.0)), 50.0)
    return rsi


def compute_spy_mr_returns(
    prices: pd.Series,
    *,
    rsi_period: int = 2,
    rsi_threshold: float = 5.0,
    sma_filter: int = 200,
    exit_sma: int = 5,
    rf: float = 0.02,
    cost_bps: float = 5.0,
) -> pd.Series:
    """Daily net returns of SPY short-term mean-reversion stream.

    Implements Connors-Alvarez (2009) RSI(2) dip-buy with Chan p.95
    momentum gate. Position is binary (0 or 1) — fully long SPY when
    in trade, fully cash earning rf_d otherwise.

    Parameters
    ----------
    prices : pd.Series
        SPY adjusted-close prices indexed by date.
    rsi_period : int, default 2
        RSI lookback (Connors canonical = 2).
    rsi_threshold : float, default 5.0
        Entry threshold; long iff `RSI2[t-1] < threshold` AND gate is
        on. Connors canonical = 5; selective variants use 3 or 10.
    sma_filter : int, default 200
        Long-term momentum gate; `SPY[t-1] > SMA(sma_filter)[t-1]`
        required for entry (Chan `[algo_trading_chan, p.95]`).
    exit_sma : int, default 5
        Exit signal: `SPY[t-1] > SMA(exit_sma)[t-1]` clears the
        position. Connors canonical = 5.
    rf : float, default 0.02
        Annual risk-free rate; converted to per-day with 252-day
        compounding.
    cost_bps : float, default 5.0
        Linear cost per unit of `|Δposition|`, in basis points.

    Returns
    -------
    pd.Series
        Daily net returns indexed on prices.index[1:] (one bar lost
        to pct_change). During the warmup period the position is 0
        (cash) and returns equal rf_d.

    Raises
    ------
    ValueError
        If any parameter is out of valid range or if `prices` has
        fewer than 2 valid points.
    """
    if rsi_period <= 0:
        raise ValueError(f"rsi_period must be > 0; got {rsi_period}")
    if not (0.0 <= rsi_threshold <= 100.0):
        raise ValueError(
            f"rsi_threshold must be in [0, 100]; got {rsi_threshold}"
        )
    if sma_filter <= 0:
        raise ValueError(f"sma_filter must be > 0; got {sma_filter}")
    if exit_sma <= 0:
        raise ValueError(f"exit_sma must be > 0; got {exit_sma}")
    if cost_bps < 0:
        raise ValueError(f"cost_bps must be >= 0; got {cost_bps}")
    if len(prices) < 2:
        raise ValueError(f"prices must have ≥ 2 points; got {len(prices)}")

    rf_d = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    px = prices.astype(float)
    rets = px.pct_change()

    # Signals at t-1 (shift(1) applied at the END so position[t] uses px[t-1])
    rsi = wilder_rsi(px, period=rsi_period)
    sma_long = px.rolling(sma_filter).mean()
    sma_short = px.rolling(exit_sma).mean()

    # State-tracking position: previous-day signals decide today's pos.
    rsi_prev = rsi.shift(1).values
    px_prev = px.shift(1).values
    sma_long_prev = sma_long.shift(1).values
    sma_short_prev = sma_short.shift(1).values
    n = len(px)
    pos = np.zeros(n, dtype=float)

    # Iterate with state. pos[0] = 0 (cash). pos[t] depends on pos[t-1] +
    # signals at t-1 (which depend only on prices ≤ t-1 → no peek).
    for t in range(1, n):
        prev_pos = pos[t - 1]
        # If any signal is NaN (warmup), stay in cash.
        if (
            np.isnan(rsi_prev[t]) or np.isnan(px_prev[t])
            or np.isnan(sma_long_prev[t]) or np.isnan(sma_short_prev[t])
        ):
            pos[t] = 0.0
            continue
        gate = px_prev[t] > sma_long_prev[t]
        if prev_pos == 0.0:
            pos[t] = 1.0 if (gate and rsi_prev[t] < rsi_threshold) else 0.0
        else:
            pos[t] = 0.0 if (px_prev[t] > sma_short_prev[t]) else 1.0

    pos_prev = np.concatenate([[0.0], pos[:-1]])
    turnover = np.abs(pos - pos_prev)
    cost = (cost_bps * 1e-4) * turnover

    rets_arr = rets.values
    # net_full has the same length as prices; drop the first NaN bar
    net_full = pos * np.where(np.isnan(rets_arr), 0.0, rets_arr) \
        + (1.0 - pos) * rf_d - cost
    out = pd.Series(net_full[1:], index=px.index[1:], name="r_spy_mr")
    return out
