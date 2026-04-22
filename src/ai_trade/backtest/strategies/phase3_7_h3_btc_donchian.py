"""Phase 3.7 — H3.a: BTC Donchian ensemble independent signal.

Single-asset trend-following Donchian breakout on BTCUSD daily, reformulated
from Zarattini-Pagani-Barbon (2025) — "Catching Crypto Trends: A Tactical
Approach for Bitcoin and Altcoins" — `[zarattini_pagani_barbon_2025]`.

Why **independent** and not rotational
--------------------------------------

The base paper is a rotational top-20 crypto strategy. Our Pepperstone
universe only covers **BTC + ETH** (the N=2 cash-CFD crypto slate at retail
2:1), which neutralizes the rotation benefit. Phase 3.7-2 data-sprint §6.3
therefore REFORMULATES H3 as an **independent signal per asset**: one
Donchian ensemble on BTC + one on ETH, sized and validated separately.

This H3.a module is the **BTC leg**; ``phase3_7_h3_eth_donchian`` (H3.b) is
the symmetric ETH leg.

Signal — Donchian ensemble multi-lookback
------------------------------------------

For each bar ``t`` and each ``N ∈ {10, 20, 40}``:

* ``upper_N[t-1] = max(high over [t-N, t-1])``
* ``lower_N[t-1] = min(low  over [t-N, t-1])``

* **Long entry** if ``position == flat`` and
  ``close[t] > max(upper_{10,20,40}[t-1])`` — all three Donchian channels
  must be broken at once. Requiring ALL lookbacks to agree is the ensemble
  confirmation filter: it reduces false breakouts (a 10-bar breakout alone
  is noisy; a 40-bar breakout alone is slow). `[universal_trend_tactics,
  p.295-299]` is the canonical Turtle 20-day; we extend to {10, 20, 40}
  per Zarattini-Pagani-Barbon ensemble formulation.
* **Short entry** (symmetric): if ``position == flat`` and
  ``close[t] < min(lower_{10,20,40}[t-1])``.

**Exits — whichever first:**
* **ATR(20) trailing stop, ``k`` multiplier** `[universal_trend_tactics,
  p.338-343]`. Long exits when
  ``close[t] < highest_close_since_entry − k · ATR_{20}[t-1]``. Short is
  symmetric (close > lowest_close_since_entry + k · ATR).
* **Time stop ≤ 2 trading days** — force-flatten at close on day t if
  position opened ≥ 2 bars ago. This is the Pepperstone-swap-budget
  constraint: long crypto swap is −0.05556%/day (= −20%/yr), so
  ``max_hold = 2`` caps long swap cost at ≤ 0.11% per trade — acceptable
  friction. Short swap is +0.02083%/day (= +7.5%/yr) so pays us; we cap
  it identically for symmetry (not necessity).

**Sizing — vol-targeted fixed-fraction:**
``position_notional = risk_pct × equity / ATR_{20}[t-1]`` capped at
``max_leverage`` (default 1.0 unleveraged; leverage=2.0 tested as a cell
variant). `[universal_trend_tactics, p.291]` — Penfold uses 2% per trade
for single-instrument; we sweep ``{0.005, 0.010, 0.015}``.

Look-ahead audit
----------------

Every decision at bar ``t`` uses only data up through bar ``t-1``:

* ``upper_N[t-1]`` = rolling max of ``high`` over the prior ``N`` bars,
  exclusive of ``t`` — implemented as ``high.rolling(N).max().shift(1)``.
* ``lower_N[t-1]`` = rolling min of ``low`` (shifted).
* ``ATR_{20}[t-1]`` = Wilder ATR over prior 20 bars, shifted by 1.
* ``trailing_max/min`` = running extremum of closes **since entry**,
  updated AFTER the exit check each bar.
* Returns use the F2 alignment: ``daily_ret[t] = prev_weight[t-1] ×
  ret[t]`` per `[advances_fin_ml, p.31-34]`.

Cost model — Pepperstone BTCUSD CFD rota A (NO DARF)
----------------------------------------------------

* **Commission:** 0 (crypto CFDs are commission-free on Pepperstone
  Razor for retail).
* **Spread:** 5 bps per side (conservative internal proxy — Pepperstone
  doesn't publish BTC/USD spread per-tick-size but cTrader desk data +
  public review snapshots suggest 3-7 bps per side in normal conditions;
  we assume 5 bps and document). Round-trip = 10 bps.
* **Swap long:** −0.05556%/day on long notional (Pepperstone published
  rate ≡ −20%/yr) applied **daily while open** (not just at entry/exit)
  — this is material for the 2-day hold envelope.
* **Swap short:** +0.02083%/day on short notional (+7.5%/yr credit).
* **Leverage cap:** 2:1 retail per ASIC/CySEC/DFSA.
* **No DARF:** per mandate §2.2 rota A + user decision 2026-04-22, we
  do NOT model 15% BR capital-gains tax on Pepperstone CFD flow.

**Cost×2 sensitivity (gate 13):** spread ×2 (20 bps round-trip), swap
long ×2 (−0.11111%/day), swap short ×0.5 (punish us — +0.01042%/day).

Cite
----
* `[zarattini_pagani_barbon_2025]` — Donchian ensemble base design,
  Sharpe >1.5 net, alpha 10.8%/yr vs BTC buy-hold (rotational version).
* `[universal_trend_tactics, p.295-299, p.338-343]` — Turtle Donchian +
  ATR trailing stop canonical.
* `[advances_fin_ml, p.31-34]` — F2 alignment `prev_weight × ret`.
* `docs/investment-mandate.md §2.4, §3.1` — 13-gate rota A + cost model.
* Phase 3.7-2 data-sprint §6.3 — independent-per-asset rationale.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

__all__ = [
    "H3BTCDonchianConfig",
    "H3BTCDonchianResult",
    "compute_atr_wilder_daily",
    "compute_donchian_bands",
    "simulate_h3_btc_donchian",
]

TRADING_DAYS_PER_YEAR_CRYPTO = 365  # crypto is 24/7 — full calendar days.
SECONDS_PER_YEAR = 365.25


@dataclass(frozen=True)
class H3BTCDonchianConfig:
    """Immutable H3.a BTC Donchian ensemble config.

    Parameters
    ----------
    lookbacks : tuple[int, ...]
        Donchian lookbacks for the ensemble (entry requires all to break).
        Default ``(10, 20, 40)`` matches Zarattini-Pagani-Barbon 2025
        framing and brackets the canonical Turtle 20-day
        `[universal_trend_tactics, p.295-299]`.
    atr_period : int
        Wilder ATR period for trailing stop + sizing. Default 20.
        `[universal_trend_tactics, p.338-343]`.
    atr_multiplier : float
        ``k`` in the ATR trail. Default 2.0 (canonical Turtle k=2).
    max_hold_days : int
        Time stop — force flatten after this many bars open. Default 2
        to cap long swap cost at ≤ 0.11% per trade.
    risk_per_trade : float
        Fraction of equity risked per trade (size = risk · equity / ATR).
        Default 0.010 = 1% per trade. Sweep ``{0.005, 0.010, 0.015}``.
    max_leverage : float
        Gross notional cap in units of equity. Pepperstone crypto retail
        allows 2:1. Default 1.0 (unleveraged). Cell variant 2.0 tested
        in the grid.
    spread_bps_per_side : float
        Per-side spread fraction in basis points. Default 5.0 (10 bps
        round-trip) — Pepperstone BTC-USD internal proxy.
    commission_bps : float
        Per-side commission. 0 for Pepperstone Razor crypto.
    swap_long_daily : float
        Daily swap fraction on long notional. Default −0.0005556 (Pepperstone
        −20%/yr published).
    swap_short_daily : float
        Daily swap fraction on short notional (credited). Default
        +0.0002083 (Pepperstone +7.5%/yr).
    allow_short : bool
        Whether short entries are enabled. Default True.
    """

    lookbacks: tuple[int, ...] = (10, 20, 40)
    atr_period: int = 20
    atr_multiplier: float = 2.0
    max_hold_days: int = 2
    risk_per_trade: float = 0.010
    max_leverage: float = 1.0
    spread_bps_per_side: float = 5.0
    commission_bps: float = 0.0
    swap_long_daily: float = -0.0005556
    swap_short_daily: float = 0.0002083
    allow_short: bool = True

    def __post_init__(self) -> None:
        if not self.lookbacks or min(self.lookbacks) < 2:
            raise ValueError(f"lookbacks must be non-empty, all ≥ 2, got {self.lookbacks}")
        if self.atr_period < 2:
            raise ValueError(f"atr_period must be ≥ 2, got {self.atr_period}")
        if self.atr_multiplier <= 0:
            raise ValueError(f"atr_multiplier must be > 0, got {self.atr_multiplier}")
        if self.max_hold_days < 1:
            raise ValueError(f"max_hold_days must be ≥ 1, got {self.max_hold_days}")
        if not 0 < self.risk_per_trade <= 0.10:
            raise ValueError(
                f"risk_per_trade must be in (0, 0.10], got {self.risk_per_trade}"
            )
        if self.max_leverage <= 0 or self.max_leverage > 2.0:
            raise ValueError(
                f"max_leverage must be in (0, 2.0], got {self.max_leverage}"
            )


@dataclass
class H3BTCDonchianResult:
    """Output of one H3.a BTC Donchian run."""

    daily_returns: pd.Series  # net-of-cost daily returns (F2 aligned)
    gross_returns: pd.Series  # pre-cost daily returns
    weights: pd.Series         # per-bar signed weight on BTC (−max_lev..+max_lev)
    entries_long: pd.Series    # bool; True on long entry bar
    entries_short: pd.Series   # bool; True on short entry bar
    exits: pd.Series           # bool; True on exit bar
    exit_reason: pd.Series     # str; {"", "atr_trail", "time_stop", "opposite"}
    hold_lengths: list[int]
    trade_pnls: list[float]    # per-trade compound PnL (fraction)
    cum_spread_pct: float
    cum_commission_pct: float
    cum_swap_pct: float
    n_trades: int
    n_long_trades: int
    n_short_trades: int

    def sharpe(self, periods_per_year: int = TRADING_DAYS_PER_YEAR_CRYPTO) -> float:
        r = self.daily_returns.dropna()
        if r.empty:
            return 0.0
        sd = float(r.std(ddof=1))
        return float(r.mean() / sd * np.sqrt(periods_per_year)) if sd > 0 else 0.0

    def cagr(self, periods_per_year: int = TRADING_DAYS_PER_YEAR_CRYPTO) -> float:
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


def compute_atr_wilder_daily(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 20,
) -> pd.Series:
    """Wilder ATR (1978) on daily crypto bars.

    Same convention as `phase3_6_k_universal_trend.compute_atr_wilder`:
    Wilder smoothing ≡ EMA with ``alpha = 1/period``.
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


def compute_donchian_bands(
    high: pd.Series,
    low: pd.Series,
    lookbacks: tuple[int, ...],
) -> tuple[pd.Series, pd.Series]:
    """Ensemble Donchian upper/lower bands (shifted t-1).

    Returns (upper_ensemble, lower_ensemble) where:
    * ``upper_ensemble[t]`` = max over lookbacks of ``high.rolling(N).max().shift(1)``
    * ``lower_ensemble[t]`` = min over lookbacks of ``low.rolling(N).min().shift(1)``

    Entry requires ``close[t] > upper_ensemble[t]`` — breakout of the
    SLOWEST channel is the binding condition when all agree.
    """
    uppers = []
    lowers = []
    for N in lookbacks:
        uppers.append(high.rolling(window=N, min_periods=N).max().shift(1))
        lowers.append(low.rolling(window=N, min_periods=N).min().shift(1))
    upper = pd.concat(uppers, axis=1).max(axis=1)
    lower = pd.concat(lowers, axis=1).min(axis=1)
    return upper, lower


def simulate_h3_btc_donchian(
    btc_daily: pd.DataFrame,
    config: H3BTCDonchianConfig,
) -> H3BTCDonchianResult:
    """Run one H3.a BTC Donchian ensemble simulation (single asset).

    Parameters
    ----------
    btc_daily : pd.DataFrame
        BTC daily OHLC with columns ``open, high, low, close, adj_close``
        (Tiingo format). Index must be DatetimeIndex; crypto bars include
        weekends.
    config : H3BTCDonchianConfig
        Cell configuration.

    Returns
    -------
    H3BTCDonchianResult
    """
    for col in ("open", "high", "low", "close", "adj_close"):
        if col not in btc_daily.columns:
            raise ValueError(f"btc_daily missing column {col}")

    d = btc_daily.copy()
    d.index = pd.DatetimeIndex(d.index).normalize()
    d = d[~d.index.duplicated(keep="last")].sort_index()

    close = d["close"].astype(float)
    high = d["high"].astype(float)
    low = d["low"].astype(float)
    adj = d["adj_close"].astype(float)

    # Use simple ``close.pct_change`` for the return series — BTC spot
    # has no dividend / split, so adj_close ≡ close for Tiingo crypto
    # (verified on the parquet). Use close for internal consistency.
    ret = close.pct_change(fill_method=None).fillna(0.0)

    atr = compute_atr_wilder_daily(high, low, close, period=config.atr_period)
    atr_prev = atr.shift(1)

    upper_ens, lower_ens = compute_donchian_bands(high, low, config.lookbacks)

    idx = close.index
    n_bars = len(idx)

    weight = np.zeros(n_bars, dtype=float)
    entries_long = np.zeros(n_bars, dtype=bool)
    entries_short = np.zeros(n_bars, dtype=bool)
    exits = np.zeros(n_bars, dtype=bool)
    exit_reason = np.full(n_bars, "", dtype=object)

    # State
    pos = 0  # −1/0/+1
    entry_bar = -1
    trailing_max = 0.0
    trailing_min = 0.0
    current_weight = 0.0
    hold_lengths: list[int] = []
    trade_pnls: list[float] = []
    current_trade_entry_equity = 1.0
    equity_path = 1.0  # synthetic tracking for trade-pnl bookkeeping
    n_trades = 0
    n_long_trades = 0
    n_short_trades = 0

    close_v = close.to_numpy()
    atr_prev_v = atr_prev.to_numpy()
    upper_v = upper_ens.to_numpy()
    lower_v = lower_ens.to_numpy()
    ret_v = ret.to_numpy()

    for t in range(n_bars):
        c_t = close_v[t]
        atr_p = atr_prev_v[t]
        u_t = upper_v[t]
        l_t = lower_v[t]

        if not np.isfinite(c_t):
            weight[t] = 0.0
            continue

        # --- Step 1: if in position, check exits (ATR trail or time) ---
        if pos != 0:
            bars_open = t - entry_bar
            exited = False
            reason = ""

            if pos > 0:
                if np.isfinite(atr_p) and atr_p > 0:
                    stop = trailing_max - config.atr_multiplier * atr_p
                    if c_t < stop:
                        exited = True
                        reason = "atr_trail"
                if not exited and bars_open >= config.max_hold_days:
                    exited = True
                    reason = "time_stop"
            else:  # pos < 0
                if np.isfinite(atr_p) and atr_p > 0:
                    stop = trailing_min + config.atr_multiplier * atr_p
                    if c_t > stop:
                        exited = True
                        reason = "atr_trail"
                if not exited and bars_open >= config.max_hold_days:
                    exited = True
                    reason = "time_stop"

            if exited:
                exits[t] = True
                exit_reason[t] = reason
                hold_lengths.append(int(bars_open))
                trade_pnls.append(float(equity_path / current_trade_entry_equity - 1.0))
                pos = 0
                current_weight = 0.0
                weight[t] = 0.0
                # Continue — no new entry on the same bar.
                # Update equity for any return already applied this bar
                # (prev_weight × ret happens at aggregation, not here).
                continue
            else:
                # Hold — update trailing extremum AFTER confirming no exit.
                if pos > 0 and c_t > trailing_max:
                    trailing_max = c_t
                if pos < 0 and c_t < trailing_min:
                    trailing_min = c_t
                weight[t] = current_weight
                continue

        # --- Step 2: flat — check for new entry ---
        if not (np.isfinite(u_t) and np.isfinite(l_t) and np.isfinite(atr_p) and atr_p > 0):
            weight[t] = 0.0
            continue

        if c_t > u_t:
            # Long entry.
            entries_long[t] = True
            pos = +1
            entry_bar = t
            trailing_max = c_t
            trailing_min = c_t
            # size: risk_per_trade × equity / ATR; units are fraction of
            # notional per unit of equity. We parameterize in the same
            # way as Family K: position_fraction = r × price / (k × ATR).
            size = config.risk_per_trade * c_t / (config.atr_multiplier * atr_p)
            size = min(size, config.max_leverage)
            current_weight = +size
            weight[t] = current_weight
            current_trade_entry_equity = equity_path
            n_trades += 1
            n_long_trades += 1
        elif config.allow_short and c_t < l_t:
            entries_short[t] = True
            pos = -1
            entry_bar = t
            trailing_max = c_t
            trailing_min = c_t
            size = config.risk_per_trade * c_t / (config.atr_multiplier * atr_p)
            size = min(size, config.max_leverage)
            current_weight = -size
            weight[t] = current_weight
            current_trade_entry_equity = equity_path
            n_trades += 1
            n_short_trades += 1
        else:
            weight[t] = 0.0

        # At end of bar, update synthetic equity path with today's return
        # applied to the PREVIOUS bar's weight (F2 alignment).
        if t > 0:
            equity_path *= (1.0 + weight[t - 1] * ret_v[t])

    # Close open position at end-of-series.
    if pos != 0 and entry_bar >= 0:
        hold_lengths.append(int(n_bars - 1 - entry_bar))
        trade_pnls.append(float(equity_path / current_trade_entry_equity - 1.0))

    weights = pd.Series(weight, index=idx, name="weight")
    prev_weights = weights.shift(1).fillna(0.0)
    gross_ret = prev_weights * ret

    # --- Costs ---
    # Spread + commission on absolute weight changes.
    weight_changes = (weights - prev_weights).abs()
    spread_rt = 2.0 * config.spread_bps_per_side / 10_000.0
    commission_rt = 2.0 * config.commission_bps / 10_000.0
    spread_drag = weight_changes * spread_rt
    commission_drag = weight_changes * commission_rt
    # Swap: applied DAILY on prev_weight's open notional.
    long_exposure = prev_weights.clip(lower=0.0)
    short_exposure = (-prev_weights).clip(lower=0.0)
    swap_drag = (
        long_exposure * abs(config.swap_long_daily)
        - short_exposure * config.swap_short_daily  # short swap is CREDIT
    )

    net_ret = gross_ret - spread_drag - commission_drag - swap_drag

    entries_long_s = pd.Series(entries_long, index=idx, name="entries_long")
    entries_short_s = pd.Series(entries_short, index=idx, name="entries_short")
    exits_s = pd.Series(exits, index=idx, name="exits")
    exit_reason_s = pd.Series(exit_reason, index=idx, name="exit_reason")

    return H3BTCDonchianResult(
        daily_returns=net_ret,
        gross_returns=gross_ret,
        weights=weights,
        entries_long=entries_long_s,
        entries_short=entries_short_s,
        exits=exits_s,
        exit_reason=exit_reason_s,
        hold_lengths=hold_lengths,
        trade_pnls=trade_pnls,
        cum_spread_pct=float(spread_drag.sum()),
        cum_commission_pct=float(commission_drag.sum()),
        cum_swap_pct=float(swap_drag.sum()),
        n_trades=int(n_trades),
        n_long_trades=int(n_long_trades),
        n_short_trades=int(n_short_trades),
    )
