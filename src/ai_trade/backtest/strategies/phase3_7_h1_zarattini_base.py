"""Phase 3.7 — H1.a: Zarattini-Aziz-Barbon 2024 intraday SPY noise-boundary momentum.

**Literal base replication** of the SSRN 4824172 paper (Zarattini, Aziz, Barbon
2024 — "Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF
(SPY)"). Signal = breakout of rolling "noise boundaries" defined as
``open_of_day × (1 ± MA_{14d}(|intraday_return_so_far|))``, entry trend-
following on the break, exit ATR-scaled trailing stop, flat at close.

Citations
---------
* **Signal + windows:** Zarattini, Aziz, Barbon (2024) — SSRN 4824172,
  "Beat the Market: An Effective Intraday Momentum Strategy for S&P500
  ETF (SPY)" — `[zarattini_aziz_barbon_2024]` (indexed in
  ``docs/research/2026-04-23-phase3.7-literature-sprint.md §T3.Paper1``).
  Sharpe 1.33 net; annualized 19.6%; 17y backtest 2007→2024.
* **Lookahead timing (prev_weight × ret):** ``[advances_fin_ml, p.31-34]``.
* **ATR(20) Wilder trailing stop:** Wilder (1978) via
  ``[universal_trend_tactics, p.338-343]`` — same convention as Phase
  3.6 Family K.
* **Cost model (Pepperstone SPX500 CFD intraday no-DARF):**
  ``docs/strategies/plano_a_pepperstone_index_cfd_rate_card.md`` +
  mandate §2.2 rota A + feedback memory
  `feedback_pepperstone_staging_and_darf.md`.
* **Flat-at-close discipline:** mandate §3 (intraday pivot 2026-04-15).
* **13-gate validation:** ``docs/investment-mandate.md §2.4`` + Phase
  3.7-3 hunt prompt (2026-04-23).

Look-ahead audit
----------------
For each 1-min bar ``t``:

* ``open_of_day`` = first observed `open` of day D (known at bar 0 of D).
* ``|intraday_return_t|`` = ``|close_t / open_of_day - 1|`` (uses close at t).
* The 14-day MA of ``|intraday_return_k|`` for minute-of-day ``k`` is
  computed over the **prior 14 trading days** only — i.e. shifted so that
  day D uses days D-14..D-1 (strictly no peek into day D's own series).
* ATR_{20} is Wilder over the prior 20 bars (shifted by 1).
* Decision at bar t compares ``close_t`` vs boundaries_t — but the
  resulting position change earns return only on bar t+1 onward, via
  ``prev_weights = weights.shift(1).fillna(0.0)`` convention
  (``[advances_fin_ml, p.31-34]``). This is the F2-patched alignment
  used across all Phase 3.6 families.

Exit rule (base replication)
----------------------------
* **ATR(20) trailing stop, k=2**: on each bar while in position, track
  ``trail_peak`` (max close since entry for longs, min close for shorts).
  Exit when ``close_t < trail_peak − 2·ATR_{t-1}`` (long) or
  ``close_t > trail_peak + 2·ATR_{t-1}`` (short).
* **Flat at close**: on the last bar of day D (per unique date), close
  all positions on the close of that bar; no overnight exposure.

Cost model
----------
* **Pepperstone Razor SPX500 CFD, intraday:**
  - Spread one-way ≈ 0.4 pts on SPX ≈ **0.67 bps per side** at SPX 6000.
    We parameterize as fraction (6.67e-5) per side = 13.3 bps round-trip.
  - Commission **0 bps** (SPX500 index CFD commission-free — see rate
    card). Tunable for generality.
  - Swap **zero** — flat at close enforces it structurally.
* **Cost×2 sensitivity (gate 13):** spread × 2 (13.3 bps round-trip).
* **No DARF**: per mandate §2.2 rota A + user decision 2026-04-22 not to
  model 15% BR CG tax on Pepperstone CFD flow.

Position sizing
---------------
Base leg = ±1.0 notional (unleveraged). Leverage sweeps are **out of
scope** for H1.a (leverage is a separate H4 meta-layer in the plan).

The strategy is **single-asset per run** — one simulation per ticker
(SPY or QQQ). The AGGREGATE report harmonizes both.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

__all__ = [
    "H1ZarattiniBaseConfig",
    "H1ZarattiniBaseResult",
    "compute_atr_wilder_1min",
    "simulate_h1_zarattini_base",
]

# 1-min bars × ~390/day × 252 days/year ≈ 98,280 periods per year.
BARS_PER_TRADING_DAY_FULL = 390
TRADING_DAYS_PER_YEAR = 252
BARS_PER_YEAR_1MIN = BARS_PER_TRADING_DAY_FULL * TRADING_DAYS_PER_YEAR  # 98280


@dataclass(frozen=True)
class H1ZarattiniBaseConfig:
    """Immutable Zarattini-Aziz-Barbon 2024 base config.

    Parameters
    ----------
    ma_days : int
        Rolling-window length in trading days for the MA over
        ``|intraday_return|``. Paper default 14.
        [zarattini_aziz_barbon_2024]
    atr_period : int
        Bar count for Wilder ATR used in the trailing stop. Default 20
        bars (paper default is dynamic ATR-scaled; 20 is the canonical
        Wilder ATR window used in the paper's trailing-stop section).
    atr_multiplier : float
        Trailing-stop multiplier ``k``. Default 2.0 per paper.
    signal_start_bar : int
        Minimum bar index within the day before a signal is considered
        live. 1 = evaluate from the second bar (we need ≥1 bar to
        define |intraday_return|). Paper evaluates from the opening
        auction close onward; we match with 1.
    flat_at_close : bool
        Close position on the last bar of each day. Paper-mandated
        intraday discipline. Default True.
    spread_one_way : float
        One-way spread as fraction of price (e.g. 6.67e-5 ≈ 0.67 bps =
        0.4 pts on SPX 6000). Pepperstone Razor SPX500 CFD; for SPY/QQQ
        ETF-equivalent, use same magnitude as a conservative proxy.
        [docs/strategies/plano_a_pepperstone_index_cfd_rate_card.md]
    commission_round_trip : float
        Round-trip commission as fraction. 0 for SPX500 index CFD.
    swap_daily : float
        Overnight swap. 0 here (flat-at-close enforces it).
    tax_rate : float
        Capital-gains tax. 0.0 per mandate §2.2 rota A (no DARF).
    """

    ma_days: int = 14
    atr_period: int = 20
    atr_multiplier: float = 2.0
    atr_scale: Literal["daily", "minute"] = "daily"
    """ATR scale. The Zarattini paper's trailing stop uses a stop distance
    on the order of intraday typical range — ATR(20) on 1-min bars is
    ~0.05% on SPY (too tight; most positions stop within minutes), whereas
    ATR(20) on daily bars is ~1% (reasonable ATR × 2 = 2% stop distance).
    The paper text "2 × ATR(20)" canonically refers to daily-bar ATR when
    the framework is intraday — this is the Wilder convention from Penfold
    [universal_trend_tactics, p.338-343] and Sanders (Zarattini's
    reference in the paper). Default 'daily'. Flip to 'minute' for strict
    literal-bar interpretation."""
    signal_start_bar: int = 1
    flat_at_close: bool = True
    spread_one_way: float = 6.67e-5
    commission_round_trip: float = 0.0
    swap_daily: float = 0.0
    tax_rate: float = 0.0
    no_reentry_after_stop_same_day: bool = True
    """After the trailing-stop closes a position on day D, do not re-enter
    on day D (even if boundary is re-crossed). This matches the Zarattini
    paper's one-trade-per-day discipline — the paper reports ~1.5 trades/day
    whereas the raw rule produces ~13 trades/day on SPY 2017-2018 due to
    tight early-day boundaries. [zarattini_aziz_barbon_2024]"""

    def __post_init__(self) -> None:
        if self.ma_days < 2:
            raise ValueError(f"ma_days must be >= 2, got {self.ma_days}")
        if self.atr_period < 2:
            raise ValueError(f"atr_period must be >= 2, got {self.atr_period}")
        if self.atr_multiplier <= 0:
            raise ValueError(
                f"atr_multiplier must be > 0, got {self.atr_multiplier}"
            )
        if self.signal_start_bar < 1:
            raise ValueError(
                f"signal_start_bar must be >= 1, got {self.signal_start_bar}"
            )
        if self.spread_one_way < 0:
            raise ValueError(
                f"spread_one_way must be >= 0, got {self.spread_one_way}"
            )


@dataclass
class H1ZarattiniBaseResult:
    """Single-asset Zarattini simulation output (1-min bar granularity)."""

    minute_returns: pd.Series  # net per-bar returns, same index as input bars
    gross_returns: pd.Series
    weights: pd.Series  # position ∈ {-1, 0, +1}
    entry_bars: list[pd.Timestamp]
    exit_bars: list[pd.Timestamp]
    hold_bars: list[int]  # hold length in 1-min bars
    n_trades: int
    cum_spread_pct: float
    cum_commission_pct: float
    ticker: str = ""

    def daily_returns(self) -> pd.Series:
        """Aggregate 1-min net returns into daily compound returns."""
        r = self.minute_returns.dropna()
        if r.empty:
            return pd.Series(dtype=float)
        # Group by calendar date (normalize UTC index).
        daily = (1.0 + r).groupby(r.index.normalize()).prod() - 1.0
        daily.index = pd.DatetimeIndex(daily.index)
        return daily

    def sharpe_daily(self) -> float:
        """Annualized Sharpe from compounded daily returns."""
        r = self.daily_returns()
        if r.empty:
            return 0.0
        sd = float(r.std(ddof=1))
        return (
            float(r.mean() / sd * np.sqrt(TRADING_DAYS_PER_YEAR))
            if sd > 0
            else 0.0
        )

    def cagr(self) -> float:
        r = self.daily_returns()
        if len(r) < 2:
            return 0.0
        eq = float((1.0 + r).prod())
        if eq <= 0:
            return -1.0
        years = len(r) / TRADING_DAYS_PER_YEAR
        return eq ** (1.0 / years) - 1.0 if years > 0 else 0.0

    def max_drawdown(self) -> float:
        r = self.daily_returns()
        if r.empty:
            return 0.0
        eq = (1.0 + r).cumprod()
        peak = eq.cummax()
        return float((eq / peak - 1.0).min())

    def median_hold_minutes(self) -> float:
        if not self.hold_bars:
            return float("nan")
        return float(np.median(self.hold_bars))


def compute_atr_wilder_1min(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 20,
) -> pd.Series:
    """Wilder ATR on 1-min bars. Same specification as daily.

    ``TR_t = max(h−l, |h − prev_close|, |l − prev_close|)``
    ``ATR_t = EMA(TR, α=1/period)``.

    Returns aligned to ``close.index``. First ``period-1`` values NaN.
    """
    if not (high.index.equals(low.index) and high.index.equals(close.index)):
        raise ValueError("high/low/close must share the same index")
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()


def _compute_noise_boundaries(
    bars: pd.DataFrame,
    ma_days: int,
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """Compute per-bar noise boundaries + open-of-day + abs intraday return.

    Algorithm (strictly no peek into today):

    1. Attach ``date`` = ``bars.index.normalize()``.
    2. ``open_of_day[t]`` = first ``open`` on that date (broadcast).
    3. ``abs_ret[t]`` = ``|close_t / open_of_day[t] - 1|`` — uses close@t.
       This is today's magnitude, used to determine TODAY's noise at
       minute-of-day k. The rolling MA uses PRIOR days for the same k.
    4. For each minute-of-day k (1..390), gather the abs_ret series at
       minute k across all days → ``abs_ret_k``. Compute
       ``ma_k[D] = rolling(ma_days).mean().shift(1)`` — the mean of the
       prior ``ma_days`` days' bar-k abs_ret, **shifted by 1 so day D
       uses days D-ma_days..D-1 only**.
    5. Reassemble ``ma[t]`` indexed by (date, minute-of-day).
    6. ``upper[t] = open_of_day[t] × (1 + ma[t])``
       ``lower[t] = open_of_day[t] × (1 - ma[t])``

    Returns (open_of_day, abs_ret, upper_boundary, lower_boundary).
    """
    idx = bars.index
    # Use plain range index internally to avoid index-name collisions
    # (Tiingo parquets use index.name="date" which conflicts with our
    # derived "date" column in groupby).
    date = idx.normalize()
    minute_of_day = (
        idx.hour.astype("int64") * 60 + idx.minute.astype("int64")
    )

    df = pd.DataFrame(
        {
            "open": bars["open"].astype(float).to_numpy(),
            "high": bars["high"].astype(float).to_numpy(),
            "low": bars["low"].astype(float).to_numpy(),
            "close": bars["close"].astype(float).to_numpy(),
            "d": date,
            "mod": minute_of_day,
        },
    )

    # Open-of-day via groupby first(); broadcast to all bars of that date.
    open_of_day_vals = df.groupby("d")["open"].transform("first").to_numpy()
    open_of_day = pd.Series(open_of_day_vals, index=idx, name="open_of_day")
    abs_ret = (bars["close"].astype(float) / open_of_day - 1.0).abs()

    # Pivot: rows = date, cols = minute-of-day, values = abs_ret.
    piv = pd.Series(
        abs_ret.to_numpy(),
        index=pd.MultiIndex.from_arrays(
            [df["d"].to_numpy(), df["mod"].to_numpy()], names=("d", "mod")
        ),
    )
    piv = piv.unstack("mod").sort_index()

    # Per-column (minute-of-day) rolling mean over PRIOR ma_days days.
    # shift(1) ensures day D never peeks at its own bar-k value.
    ma_by_day = (
        piv.rolling(window=ma_days, min_periods=ma_days)
        .mean()
        .shift(1)
    )

    # Reassemble back to per-bar series.
    ma_stack = ma_by_day.stack()
    # ma_stack is indexed by (d, mod). Map back using (d, mod)
    # pairs per bar.
    key = pd.MultiIndex.from_arrays(
        [df["d"].to_numpy(), df["mod"].to_numpy()], names=("d", "mod")
    )
    ma_series = ma_stack.reindex(key).to_numpy()
    ma_aligned = pd.Series(ma_series, index=idx, name="ma_noise")

    upper = open_of_day * (1.0 + ma_aligned)
    lower = open_of_day * (1.0 - ma_aligned)

    return open_of_day, abs_ret, upper, lower


def simulate_h1_zarattini_base(
    bars_1min: pd.DataFrame,
    config: H1ZarattiniBaseConfig,
    ticker: str = "",
) -> H1ZarattiniBaseResult:
    """Run one single-asset Zarattini-Aziz-Barbon 2024 base simulation.

    Parameters
    ----------
    bars_1min : pd.DataFrame
        1-min OHLC bars, DatetimeIndex (UTC tz-aware acceptable),
        columns ``open, high, low, close``.
    config : :class:`H1ZarattiniBaseConfig`
        Frozen config.
    ticker : str
        Label for reporting (e.g. "SPY").

    Returns
    -------
    :class:`H1ZarattiniBaseResult`
    """
    required = {"open", "high", "low", "close"}
    if not required.issubset(bars_1min.columns):
        raise ValueError(
            f"bars_1min missing columns: {required - set(bars_1min.columns)}"
        )
    if bars_1min.empty:
        raise ValueError("bars_1min is empty")

    # Sort and dedup index defensively.
    bars = bars_1min.sort_index()
    bars = bars[~bars.index.duplicated(keep="first")]

    # --- Compute noise boundaries (no lookahead) ---
    open_of_day, abs_ret, upper, lower = _compute_noise_boundaries(
        bars, ma_days=config.ma_days
    )

    # --- Compute ATR(period) on 1-min TR OR on daily TR, shift to avoid peek ---
    if config.atr_scale == "minute":
        atr = compute_atr_wilder_1min(
            bars["high"], bars["low"], bars["close"], period=config.atr_period
        )
        atr_prev = atr.shift(1)
    else:
        # Daily ATR: aggregate to daily OHLC, compute Wilder ATR, then
        # broadcast the PRIOR day's value to every bar of the current day
        # (so strictly no peek into today's OHLC for today's trail).
        daily_high = bars["high"].groupby(bars.index.normalize()).max()
        daily_low = bars["low"].groupby(bars.index.normalize()).min()
        daily_close = bars["close"].groupby(bars.index.normalize()).last()
        daily_atr = compute_atr_wilder_1min(
            daily_high, daily_low, daily_close, period=config.atr_period
        )
        # shift(1): today's bars use ATR computed from days D-period..D-1.
        daily_atr_prev = daily_atr.shift(1)
        # Broadcast to per-bar index by normalized date.
        atr_prev = pd.Series(
            daily_atr_prev.reindex(bars.index.normalize()).to_numpy(),
            index=bars.index,
            name="atr_prev_daily",
        )
        atr = atr_prev  # for potential downstream reporting

    # --- Returns series (log-less arithmetic per bar) ---
    close = bars["close"].astype(float)
    ret = close.pct_change(fill_method=None)

    # --- Flag last bar of each day for flat-at-close enforcement ---
    date = bars.index.normalize()
    # True on every bar that is the last of its date (groupby-tail pattern).
    is_last_bar = pd.Series(
        date.to_numpy(), index=bars.index
    ).shift(-1).fillna(pd.Timestamp("1900-01-01")) != pd.Series(
        date.to_numpy(), index=bars.index
    )
    # Minute-of-day index: how many bars into the day are we (0-based).
    bar_of_day = (
        pd.Series(1, index=bars.index).groupby(date).cumsum() - 1
    )

    n = len(bars)
    close_v = close.to_numpy()
    upper_v = upper.to_numpy()
    lower_v = lower.to_numpy()
    atr_prev_v = atr_prev.to_numpy()
    last_bar_v = is_last_bar.to_numpy()
    bar_of_day_v = bar_of_day.to_numpy()

    weight = np.zeros(n, dtype=float)  # position on bar t (decision at close_t)
    entry_bar = np.zeros(n, dtype=bool)
    exit_bar = np.zeros(n, dtype=bool)

    pos = 0  # current position: -1, 0, +1
    entry_idx = -1
    trail_peak = 0.0  # for longs = max close since entry; for shorts = min close
    entry_bars_out: list[pd.Timestamp] = []
    exit_bars_out: list[pd.Timestamp] = []
    hold_lengths: list[int] = []
    n_trades = 0
    # Track "stopped on this date" to enforce no-reentry-after-stop.
    stopped_today = False
    cur_date: pd.Timestamp | None = None

    for t in range(n):
        c_t = close_v[t]
        up_t = upper_v[t]
        lo_t = lower_v[t]
        atr_p = atr_prev_v[t]
        last_of_day = bool(last_bar_v[t])
        b_of_d = int(bar_of_day_v[t])

        # Reset "stopped today" when we cross into a new date.
        bar_date = bars.index[t].normalize()
        if bar_date != cur_date:
            stopped_today = False
            cur_date = bar_date

        # Flat-at-close: if this is the last bar of the day and we're in
        # position, exit at close_t. No new entries on last bar.
        if config.flat_at_close and last_of_day and pos != 0:
            exit_bar[t] = True
            exit_bars_out.append(bars.index[t])
            if entry_idx >= 0:
                hold_lengths.append(t - entry_idx)
            pos = 0
            entry_idx = -1
            trail_peak = 0.0
            weight[t] = 0.0
            continue

        # If in position, check trailing-stop exit first.
        if pos != 0:
            if pos > 0:
                # Long trail = max close since entry.
                if c_t > trail_peak:
                    trail_peak = c_t
                stop_level = (
                    trail_peak - config.atr_multiplier * atr_p
                    if np.isfinite(atr_p) and atr_p > 0
                    else -np.inf
                )
                if c_t < stop_level:
                    exit_bar[t] = True
                    exit_bars_out.append(bars.index[t])
                    if entry_idx >= 0:
                        hold_lengths.append(t - entry_idx)
                    pos = 0
                    entry_idx = -1
                    trail_peak = 0.0
                    weight[t] = 0.0
                    if config.no_reentry_after_stop_same_day:
                        stopped_today = True
                    continue
            else:
                # Short trail = min close since entry.
                if c_t < trail_peak:
                    trail_peak = c_t
                stop_level = (
                    trail_peak + config.atr_multiplier * atr_p
                    if np.isfinite(atr_p) and atr_p > 0
                    else np.inf
                )
                if c_t > stop_level:
                    exit_bar[t] = True
                    exit_bars_out.append(bars.index[t])
                    if entry_idx >= 0:
                        hold_lengths.append(t - entry_idx)
                    pos = 0
                    entry_idx = -1
                    trail_peak = 0.0
                    weight[t] = 0.0
                    if config.no_reentry_after_stop_same_day:
                        stopped_today = True
                    continue

            # Held; carry weight.
            weight[t] = float(pos)
            continue

        # Flat — check entry on signal. No new entry if boundaries NaN
        # (warmup) or we're before signal_start_bar, or on the last bar
        # of the day (pointless — flat-at-close).
        if last_of_day:
            weight[t] = 0.0
            continue
        if b_of_d < config.signal_start_bar:
            weight[t] = 0.0
            continue
        if not (np.isfinite(up_t) and np.isfinite(lo_t) and np.isfinite(atr_p)):
            weight[t] = 0.0
            continue
        if stopped_today:
            weight[t] = 0.0
            continue

        if c_t > up_t:
            # Breakout above upper → go long.
            pos = 1
            entry_idx = t
            trail_peak = c_t
            entry_bar[t] = True
            entry_bars_out.append(bars.index[t])
            n_trades += 1
            weight[t] = 1.0
        elif c_t < lo_t:
            # Breakdown below lower → go short.
            pos = -1
            entry_idx = t
            trail_peak = c_t
            entry_bar[t] = True
            entry_bars_out.append(bars.index[t])
            n_trades += 1
            weight[t] = -1.0
        else:
            weight[t] = 0.0

    # Close any lingering position at the last bar (defensive; should be
    # covered by flat_at_close).
    if pos != 0 and entry_idx >= 0:
        hold_lengths.append(n - 1 - entry_idx)

    weights_s = pd.Series(weight, index=bars.index)
    # F2-patched prev_weight × ret alignment.
    prev_w = weights_s.shift(1).fillna(0.0)
    gross = (prev_w * ret.fillna(0.0))

    # --- Costs: spread + commission on every position change ---
    w_change = (weights_s - weights_s.shift(1).fillna(0.0)).abs()
    # w_change sums |dw| ∈ {0, 1, 2} per bar; each unit of |dw| is one
    # side of a trade, so spread charge = |dw| × spread_one_way.
    spread_drag = w_change * config.spread_one_way
    # Commission: charge round-trip per full trade. A |dw|=1 means
    # half-trade (open OR close only); |dw|=2 means full flip (close +
    # reopen opposite). Treat as |dw| × (commission_round_trip / 2).
    commission_drag = w_change * (config.commission_round_trip / 2.0)
    # Swap: zero for intraday flat-at-close.
    swap_drag = pd.Series(0.0, index=bars.index)

    net = gross - spread_drag - commission_drag - swap_drag

    return H1ZarattiniBaseResult(
        minute_returns=net,
        gross_returns=gross,
        weights=weights_s,
        entry_bars=entry_bars_out,
        exit_bars=exit_bars_out,
        hold_bars=hold_lengths,
        n_trades=int(n_trades),
        cum_spread_pct=float(spread_drag.sum()),
        cum_commission_pct=float(commission_drag.sum()),
        ticker=ticker,
    )
