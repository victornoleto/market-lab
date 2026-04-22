"""Phase 3.7 — H3.b: ETH Donchian ensemble independent signal (Pepperstone CFD).

Independent-per-asset adaptation of Zarattini-Pagani-Barbon 2025 (SSRN
5209907 — "Noise-Adjusted Intraday Momentum Strategies Applied to
Cryptocurrencies"). The paper runs a cross-sectional **top-20 crypto
rotation**; Pepperstone only offers **BTC + ETH** CFDs (Phase 3.7-2 audit
§6.3), so rotation (picking top-N via momentum) is neutralized when
N=2 fixed. We reformulate the H3 signal as **Donchian channel ensemble
trend-follower on ETH daily**, allocated independently of BTC (H3.a is
the separate BTC sibling).

This is H3.b — the ETH leg. A parallel subagent handles H3.a (BTC).

Signal — Donchian ensemble
--------------------------

Let ``N ∈ {10, 20, 40}``. For each lookback:

    upper_N_{t-1} = max(high over [t-N, t-1])
    lower_N_{t-1} = min(low  over [t-N, t-1])

Entry:

* Long  if ``close_t > max(upper_{10,20,40}_{t-1})`` and position == flat
* Short if ``close_t < min(lower_{10,20,40}_{t-1})`` and position == flat

Exit: **ATR trailing stop (2 × ATR_{20})** OR **time-stop at 2 trading
days** (crypto 7d/wk — whichever first).

Position sizing: ``position = risk_pct × equity / ATR_{20, t-1}``, clipped
at 2:1 leverage; grid tests ``risk_pct ∈ {0.5%, 1.0%, 1.5%}``.

Cost model (Pepperstone ETHUSD — rota A, no DARF)
-------------------------------------------------

* Commission: **0** (crypto CFD)
* Spread one-way: **6 bps** default (5-8 bps range; ETH typically wider
  than BTC — we use conservative 6 bps as center).
* Swap long: **−0.05556%/day** (≈ −20%/yr annualized).
* Swap short: **+0.02083%/day** (≈ +7.5%/yr annualized).
* Swap is applied DAILY on OPEN NOTIONAL (absolute value of weight).
* Leverage retail cap: **2:1**.
* Cost×2 sensitivity: spread × 2 (12 bps) + long swap × 2 (−0.111%/day).

Look-ahead audit
----------------

* Donchian bands use ``rolling(N).max()``/``rolling(N).min()`` on
  ``high``/``low`` through bar ``t-1`` (shifted by 1).
* ATR(20) is Wilder smoothing on TR through bar ``t-1`` (shifted by 1).
* Entry/exit decisions at bar ``t`` use ``close_t`` vs bands defined by
  t-1 data.
* Daily return alignment: ``daily_return[t] = prev_weight[t-1] ×
  ret[t]`` via F2-patched ``weights.shift(1).fillna(0.0)``
  `[advances_fin_ml, p.31-34]`.

Windows (per hunt prompt)
-------------------------

* IS:  2016-01-01 → 2020-06-30 (4.5y) — includes 2018 bear + DeFi setup.
* OOS: 2020-07-01 → 2023-06-30 (3y)  — DeFi summer, COVID, Merge, FTX,
  2023 recovery.
* FWD: 2023-07-01 → 2026-04-14 (2.75y) — post-Merge + ETF speculation.

Crypto trades 24/7, so **weekend bars are real bars** — we do NOT filter
weekdays. This matches Tiingo's ETH daily feed (28.5% weekend ratio
validated in Phase 3.7-2 integrity suite).

Citations
---------

* **Signal base:** Zarattini, Pagani, Barbon 2025 — SSRN 5209907 —
  `[zarattini_pagani_barbon_2025]` (literature sprint §T5).
* **Donchian ensemble + multi-lookback trend:**
  `[universal_trend_tactics, p.295-299]` (Turtle System 4-week breakout),
  `[universal_trend_tactics, p.338-343]` (ATR trailing stop = Wilder).
* **Lookahead alignment:** `[advances_fin_ml, p.31-34]`.
* **CSCV/PBO + DSR:** `[advances_fin_ml, p.208-211, p.275]`.
* **Stationary bootstrap:** `[advances_fin_ml, p.196-202]`.
* **13-gate framework:** `docs/investment-mandate.md §2.4, §3.1`.
* **Crypto swap costs (Pepperstone):** Phase 3.7-3 hunt prompt H3.b
  (6 bps spread ETH, −0.05556%/d long, +0.02083%/d short, 2:1 cap).
* **Independent-per-asset adaptation rationale:** Phase 3.7-2 data
  sprint §6.3.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

__all__ = [
    "H3EthDonchianConfig",
    "H3EthDonchianResult",
    "compute_atr_wilder",
    "simulate_h3_eth_donchian",
]

# Crypto trades 7 days/week → 365 bars/year (vs 252 for TradFi).
BARS_PER_YEAR_CRYPTO = 365


@dataclass(frozen=True)
class H3EthDonchianConfig:
    """Immutable configuration for one H3.b ETH Donchian ensemble cell.

    Parameters
    ----------
    donchian_lookbacks : tuple[int, ...]
        Donchian channel lookbacks (days). Ensemble breakout uses
        ``max(upper_N)`` across these; ensemble breakdown uses
        ``min(lower_N)``. Default (10, 20, 40) per hunt prompt H3.b.
        `[universal_trend_tactics, p.295-299]` (Turtle benchmark N=20).
    atr_period : int
        Wilder ATR period in days. Default 20.
    atr_multiplier : float
        Trailing-stop multiplier ``k``. Long exit when ``close_t <
        trail_peak − k × ATR_{t-1}``; short exit symmetric.
        `[universal_trend_tactics, p.338-343]`
    time_stop_days : int
        Max bars in position before forced exit (swap-budget hygiene).
        Default 2 (hunt prompt: ≤ 2d compatible with Pepperstone
        −0.0556%/d long swap).
    risk_per_trade : float
        Fraction of equity risked per trade. Position notional weight =
        ``risk_per_trade × 1 / (ATR_{t-1} / price)``. Grid tests
        {0.005, 0.010, 0.015}. `[universal_trend_tactics, p.291]`
    max_leverage : float
        Cap on |weight|. 2.0 = 2:1 (Pepperstone retail crypto cap).
    spread_one_way : float
        One-way spread as fraction of notional. 6e-4 = 6 bps (ETHUSD
        Pepperstone, 5-8 bps range; conservative center).
    commission_round_trip : float
        Round-trip commission. 0 for crypto CFD.
    swap_daily_long : float
        Daily swap applied to long open notional. Sign-correct:
        −5.556e-4 = −0.05556%/day (−20%/yr annualized).
    swap_daily_short : float
        Daily swap applied to short open notional. +2.083e-4 =
        +0.02083%/day (+7.5%/yr annualized, credit).
    tax_rate : float
        Capital-gains tax. 0.0 per mandate §2.2 rota A (no DARF
        modeled on Pepperstone per user decision 2026-04-22).
    allow_short : bool
        If False, disable short entries. Default True (crypto CFD
        supports shorts + positive swap credit).
    """

    donchian_lookbacks: tuple[int, ...] = (10, 20, 40)
    atr_period: int = 20
    atr_multiplier: float = 2.0
    time_stop_days: int = 2
    risk_per_trade: float = 0.010
    max_leverage: float = 2.0
    spread_one_way: float = 6.0e-4
    commission_round_trip: float = 0.0
    swap_daily_long: float = -5.556e-4
    swap_daily_short: float = 2.083e-4
    tax_rate: float = 0.0
    allow_short: bool = True

    def __post_init__(self) -> None:
        if not self.donchian_lookbacks:
            raise ValueError("donchian_lookbacks must be non-empty")
        if any(n < 2 for n in self.donchian_lookbacks):
            raise ValueError(
                f"donchian_lookbacks must all be >= 2, got {self.donchian_lookbacks}"
            )
        if self.atr_period < 2:
            raise ValueError(f"atr_period must be >= 2, got {self.atr_period}")
        if self.atr_multiplier <= 0:
            raise ValueError(
                f"atr_multiplier must be > 0, got {self.atr_multiplier}"
            )
        if self.time_stop_days < 1:
            raise ValueError(
                f"time_stop_days must be >= 1, got {self.time_stop_days}"
            )
        if not 0 < self.risk_per_trade <= 0.10:
            raise ValueError(
                f"risk_per_trade must be in (0, 0.10], got {self.risk_per_trade}"
            )
        if self.max_leverage <= 0:
            raise ValueError(
                f"max_leverage must be > 0, got {self.max_leverage}"
            )
        if self.spread_one_way < 0:
            raise ValueError(
                f"spread_one_way must be >= 0, got {self.spread_one_way}"
            )


@dataclass
class H3EthDonchianResult:
    """Output of one H3.b ETH simulation."""

    daily_returns: pd.Series  # net daily returns (prev_weight × ret − costs)
    gross_returns: pd.Series
    weights: pd.Series  # signed weight ∈ [−max_lev, +max_lev]
    entries: pd.Series  # +1 long entry, −1 short entry, 0 else
    exits: pd.Series  # True on exit bar
    hold_lengths: list[int] = field(default_factory=list)
    entry_bars: list[pd.Timestamp] = field(default_factory=list)
    exit_reasons: list[str] = field(default_factory=list)
    n_trades: int = 0
    n_long: int = 0
    n_short: int = 0
    cum_spread_pct: float = 0.0
    cum_commission_pct: float = 0.0
    cum_swap_pct: float = 0.0
    ticker: str = "ETHUSD"

    def sharpe(self, periods_per_year: int = BARS_PER_YEAR_CRYPTO) -> float:
        r = self.daily_returns.dropna()
        if r.empty:
            return 0.0
        sd = float(r.std(ddof=1))
        return (
            float(r.mean() / sd * np.sqrt(periods_per_year))
            if sd > 0
            else 0.0
        )

    def cagr(self, periods_per_year: int = BARS_PER_YEAR_CRYPTO) -> float:
        r = self.daily_returns.dropna()
        if len(r) < 2:
            return 0.0
        n = len(r)
        eq = float((1.0 + r).prod())
        if eq <= 0:
            return -1.0
        return eq ** (periods_per_year / n) - 1.0

    def max_drawdown(self) -> float:
        r = self.daily_returns.dropna()
        if r.empty:
            return 0.0
        eq = (1.0 + r).cumprod()
        peak = eq.cummax()
        return float((eq / peak - 1.0).min())

    def median_hold_days(self) -> float:
        if not self.hold_lengths:
            return float("nan")
        return float(np.median(self.hold_lengths))


def compute_atr_wilder(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 20,
) -> pd.Series:
    """Wilder ATR — canonical 1978 specification.

    ``TR_t = max(high_t − low_t, |high_t − close_{t-1}|,
                 |low_t − close_{t-1}|)``
    Wilder smoothing = EMA with ``alpha = 1/period``.

    Returns the full ATR series. First ``period-1`` values are NaN.
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
    atr = tr.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    return atr


def simulate_h3_eth_donchian(
    bars: pd.DataFrame,
    config: H3EthDonchianConfig,
    ticker: str = "ETHUSD",
) -> H3EthDonchianResult:
    """Run one H3.b ETH Donchian ensemble simulation.

    Parameters
    ----------
    bars : pd.DataFrame
        Daily OHLCV DataFrame with columns ``open, high, low, close,
        adj_close, volume`` and a DatetimeIndex (one row per crypto
        trading day; crypto trades 7d/wk).
    config : H3EthDonchianConfig
        Immutable grid cell.
    ticker : str
        Reported ticker (default "ETHUSD").

    Returns
    -------
    H3EthDonchianResult
    """
    required_cols = ("open", "high", "low", "close", "adj_close")
    for col in required_cols:
        if col not in bars.columns:
            raise ValueError(f"bars missing column '{col}' — got {bars.columns.tolist()}")

    df = bars.copy()
    df.index = pd.DatetimeIndex(df.index).normalize()
    df = df[~df.index.duplicated(keep="last")].sort_index()

    close = df["close"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)
    adj_close = df["adj_close"].astype(float)
    returns = adj_close.pct_change(fill_method=None)

    # Ensemble bands: max of upper channels, min of lower channels,
    # shifted by 1 to use strictly prior-bar data.
    upper_bands: list[pd.Series] = []
    lower_bands: list[pd.Series] = []
    for n in config.donchian_lookbacks:
        upper_bands.append(
            high.rolling(window=n, min_periods=n).max().shift(1)
        )
        lower_bands.append(
            low.rolling(window=n, min_periods=n).min().shift(1)
        )
    upper_ensemble = pd.concat(upper_bands, axis=1).max(axis=1)
    lower_ensemble = pd.concat(lower_bands, axis=1).min(axis=1)

    atr = compute_atr_wilder(high, low, close, period=config.atr_period)
    atr_prev = atr.shift(1)

    idx = df.index
    n_bars = len(idx)

    weights = np.zeros(n_bars, dtype=float)
    entries = np.zeros(n_bars, dtype=np.int8)
    exits = np.zeros(n_bars, dtype=bool)

    # State
    pos = 0  # -1, 0, +1 direction (magnitude is in current_weight)
    current_weight = 0.0
    trail_peak = 0.0  # max close since entry (long) OR min close since entry (short)
    seg_len = 0
    hold_lengths: list[int] = []
    entry_bars: list[pd.Timestamp] = []
    exit_reasons: list[str] = []
    n_trades = 0
    n_long = 0
    n_short = 0

    close_v = close.to_numpy()
    upper_v = upper_ensemble.to_numpy()
    lower_v = lower_ensemble.to_numpy()
    atr_prev_v = atr_prev.to_numpy()

    for t in range(n_bars):
        c_t = close_v[t]
        up = upper_v[t]
        lo = lower_v[t]
        a_prev = atr_prev_v[t]

        if not np.isfinite(c_t):
            if pos != 0:
                # Force close on missing data.
                exits[t] = True
                if seg_len > 0:
                    hold_lengths.append(int(seg_len))
                    exit_reasons.append("missing_data")
                pos = 0
                current_weight = 0.0
                seg_len = 0
            weights[t] = 0.0
            continue

        # If in position — check exit first (trail stop or time stop).
        if pos != 0:
            exited = False
            exit_reason = ""
            if np.isfinite(a_prev) and a_prev > 0:
                if pos > 0:
                    # Update trailing peak with today's close before
                    # testing — no look-ahead since we are using close_t
                    # only after deciding exit rule. The Turtle / Penfold
                    # convention tests exit on close_t against trail peak
                    # known at t-1 first, THEN update peak for next bar.
                    stop_level = trail_peak - config.atr_multiplier * a_prev
                    if c_t < stop_level:
                        exited = True
                        exit_reason = "atr_trail"
                else:  # pos < 0
                    stop_level = trail_peak + config.atr_multiplier * a_prev
                    if c_t > stop_level:
                        exited = True
                        exit_reason = "atr_trail"

            # Time stop.
            if not exited and seg_len >= config.time_stop_days:
                exited = True
                exit_reason = "time_stop"

            if exited:
                exits[t] = True
                if seg_len > 0:
                    hold_lengths.append(int(seg_len))
                    exit_reasons.append(exit_reason)
                pos = 0
                current_weight = 0.0
                seg_len = 0
                weights[t] = 0.0
                # Re-evaluate entry this bar? No — paper convention is
                # one trade per bar; skip to next bar.
                continue

            # Still in position — carry weight; update trail peak.
            weights[t] = current_weight
            if pos > 0 and c_t > trail_peak:
                trail_peak = c_t
            elif pos < 0 and c_t < trail_peak:
                trail_peak = c_t
            seg_len += 1
            continue

        # Flat — check entry signals.
        if not (np.isfinite(up) and np.isfinite(lo) and np.isfinite(a_prev) and a_prev > 0):
            weights[t] = 0.0
            continue

        # Position sizing per hunt prompt literal:
        #   position = risk_pct × equity / ATR_{20, t-1}   (in shares/units)
        #   notional fraction w = shares × price / equity
        #                       = risk_pct × price / ATR_{t-1}
        # Clipped to ±max_leverage (2:1 Pepperstone retail crypto cap).
        # The atr_multiplier is used ONLY for the trailing-stop exit
        # distance, NOT for sizing (which is 1-ATR implied per the
        # prompt formula).
        denom = a_prev
        if denom <= 0:
            weights[t] = 0.0
            continue
        raw_w = config.risk_per_trade * c_t / denom
        w = float(min(raw_w, config.max_leverage))
        if w <= 0:
            weights[t] = 0.0
            continue

        if c_t > up:
            # Long entry.
            pos = 1
            current_weight = w
            trail_peak = c_t
            seg_len = 1
            entries[t] = 1
            entry_bars.append(idx[t])
            n_trades += 1
            n_long += 1
            weights[t] = w
        elif config.allow_short and c_t < lo:
            pos = -1
            current_weight = -w
            trail_peak = c_t
            seg_len = 1
            entries[t] = -1
            entry_bars.append(idx[t])
            n_trades += 1
            n_short += 1
            weights[t] = -w
        else:
            weights[t] = 0.0

    # Flush any open position at the end.
    if pos != 0 and seg_len > 0:
        hold_lengths.append(int(seg_len))
        exit_reasons.append("end_of_data")

    weights_s = pd.Series(weights, index=idx, name="weight")
    entries_s = pd.Series(entries, index=idx, name="entry")
    exits_s = pd.Series(exits, index=idx, name="exit")

    # --- Returns with F2-patched prev_weight × ret alignment ---
    prev_w = weights_s.shift(1).fillna(0.0)
    gross_ret = prev_w * returns.fillna(0.0)

    # --- Costs ---
    # Spread on weight changes (|Δw|).
    weight_changes = (weights_s - weights_s.shift(1).fillna(0.0)).abs()
    spread_drag = weight_changes * config.spread_one_way
    commission_drag = weight_changes * config.commission_round_trip

    # Swap applied daily on OPEN NOTIONAL (prev_weight, sign-aware).
    prev_long = prev_w.clip(lower=0.0)
    prev_short = (-prev_w).clip(lower=0.0)
    swap_drag = (
        prev_long * (-config.swap_daily_long)
        - prev_short * config.swap_daily_short
    )
    # Sign convention: swap_daily_long is negative → flip to positive cost;
    # swap_daily_short is positive (credit) → subtract from cost.

    net_ret = gross_ret - spread_drag - commission_drag - swap_drag

    return H3EthDonchianResult(
        daily_returns=net_ret,
        gross_returns=gross_ret,
        weights=weights_s,
        entries=entries_s,
        exits=exits_s,
        hold_lengths=hold_lengths,
        entry_bars=entry_bars,
        exit_reasons=exit_reasons,
        n_trades=int(n_trades),
        n_long=int(n_long),
        n_short=int(n_short),
        cum_spread_pct=float(spread_drag.sum()),
        cum_commission_pct=float(commission_drag.sum()),
        cum_swap_pct=float(swap_drag.sum()),
        ticker=ticker,
    )
