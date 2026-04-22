"""Phase 3.8 B5 — Faber 10-mo GTAA single-asset SPY (unleveraged, rota B Inter).

Literal reproduction of Meb Faber's 2007 GTAA (Global Tactical Asset
Allocation) restricted to a **single asset** (SPY) and **unleveraged**:
at each month-end, if the SPY close is above its 10-month SMA, hold
100% SPY next month; otherwise hold 100% cash. No UPRO/SSO, no
multi-asset basket, no trend-strength scaling. This is the
lowest-turnover, lowest-complexity end of the Plano B hunt — the
"exhaustion" test after B1-B4 all failed.

Thesis (literal Faber 2007 / Gayed cousin)
------------------------------------------

* Faber's 10-month SMA applied to SPY is the canonical 2007 GTAA
  specification. At monthly resolution, ``SMA(close, 10)`` is
  evaluated on the **last trading day of the month**, and the
  resulting regime determines next-month exposure (100% SPY or 100%
  cash). `[phase3_7_literature_sprint §T3]` — Faber 2007 reproduction
  anchor; `[trading_evolved, p.211-212]` — Clenow's exposition of the
  10-month rule as a "trend filter at index level" with honest OOS
  caveat.
* The daily-trading-day equivalent of Faber's monthly 10-month SMA is
  ``SMA-210`` (``10 × 21`` trading days per month), which Gayed cites
  as within the same regime-signal family as his canonical ``SMA-200``
  `[leverage_for_the_long_run, p.13-14]`. B5 V4 uses this daily
  approximation as a robustness arm of the monthly canon.
* Turnover budget: Faber reports ~1-2 round-trips per year at monthly
  cadence. Our 4-config grid bounds the empirical turnover tightly
  (< 3 trades/yr on SPY is the halt threshold in the plan).

B1 vs B5 — what is different
----------------------------

B1 (SMA-200 daily canonical) rotates between **leveraged LETF** and
cash on a **daily** signal. B5 is the **unleveraged single-asset SPY**
analog at **monthly** cadence (V1 Faber canon), with one daily-rebal
variant (V4) as a sensitivity. The DARF helper is identical (reused
from :mod:`phase3_8_b1_gayed_canonical`). The CAGR ceiling is much
lower by construction (unleveraged SPY) — B5 is deliberately a
"Folclore-candidate" test of whether low-turnover SPY-GTAA clears the
hard-statistics gates even when the tier is sub-Válido.

Signal (literal, t-1-safe)
--------------------------

Monthly variants (V1/V2/V3)::

    # Identify the last trading day of each calendar month ("month-end").
    # Build the month-end close series (prices.resample('M').last() at
    # month-end positions).
    # At each month-end T:
    #   sma_N_T = SMA(monthly_close_series, N=sma_months).at[T]
    #   raw_regime_T = 1 if close_T > sma_N_T else 0
    # Shift raw_regime forward by ONE MONTH so raw_regime_T gates
    # month M+1 (i.e. the first trading day after T through the next
    # month-end). In the daily weights series, this is expressed as
    # "at each trading day d, the weight is the most recent month-end's
    # raw_regime ONE month old".

Daily variant (V4)::

    # Canonical daily SMA-N (210 trading days), shifted (t-1):
    #   sma_210_{t-1} = SMA(daily_close, 210).shift(1).iloc[t]
    #   regime_t = 1 if close_{t-1} > sma_210_{t-1} else 0
    # Weight is re-evaluated every trading day (daily rebal).

Lookahead audit
---------------

Monthly variants:

* The regime at month-end ``T`` is computed from ``close_T`` and its
  10-month SMA ``SMA(monthly_close, 10)_T`` — both known at the T
  close. We never use the **next month's** close to set the
  **current** month's regime. Execution is shifted: the weight
  ``w_{M+1}`` is applied on the first trading day **after** ``T``,
  i.e. from ``T+1`` (next trading day) onward until the next month-end.
  This shift is enforced by ``daily_weights_t = last_rebal_weight`` —
  at any ``t``, the active weight was chosen at the **most recent
  past** month-end, strictly before ``t``.
* DARF year-end realization uses ``apply_darf_year_end`` (reused from
  B1). Tax at end-of-year ``Y`` is computed only from the equity
  path realized through day ``Y_last`` — the next year's path never
  influences year ``Y``'s tax.

Daily variant:

* Identical audit as B1 SMA-200: the regime uses ``close.shift(1) >
  SMA.shift(1)``, so the position on bar ``t`` was decided from data
  strictly through ``t-1``.

Citations sweep
---------------

* Faber 2007 GTAA 10-month monthly: ``[phase3_7_literature_sprint §T3]``
  (Phase 3.7 literature sprint summary anchor).
* Faber/Clenow 10-month SMA index filter (with 2008-hindsight caveat):
  ``[trading_evolved, p.211-212]``.
* SMA-200 daily equivalent ≈ SMA-10-month monthly:
  ``[leverage_for_the_long_run, p.13-14]`` (Gayed Table 8 / cousin).
* F2-alignment ``prev_weight × ret``: ``[advances_fin_ml, p.31-34]``.
* Rota B Inter cost model + DARF 15% year-end:
  ``docs/investment-mandate.md §4.6``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

from ai_trade.backtest.helpers.synthetic_letf import TRADING_DAYS_PER_YEAR
from ai_trade.backtest.strategies.phase3_8_b1_gayed_canonical import (
    apply_darf_year_end,
)

log = logging.getLogger(__name__)

__all__ = [
    "B5Config",
    "B5Result",
    "apply_darf_year_end",
    "compute_monthly_regime",
    "compute_daily_regime",
    "simulate_b5",
]


RebalKind = Literal["monthly", "daily"]


@dataclass(frozen=True)
class B5Config:
    """Immutable config for a single B5 variant backtest.

    Parameters
    ----------
    sma_months : int
        Monthly SMA window in calendar months (monthly variants) OR the
        equivalent daily window in trading days is ``sma_months * 21``
        (daily variant V4). Faber canon = 10.
    rebal : {"monthly", "daily"}
        Cadence. "monthly" = Faber canonical (last-trading-day-of-month
        signal, held until next month-end). "daily" = SMA-210 daily
        rebalance (Gayed SMA-200 cousin).
    cash_rate_annual : float
        Flat annualized cash-sleeve return (RISK_OFF days). Default
        0.04 (same proxy as B1 per mandate §4.6, shared long-term
        3-mo T-bill approximation).
    spy_expense_ratio : float
        SPY annualized expense ratio (0.09%/yr). Subtracted from the
        gross on-regime return daily (already embedded in real SPY
        adj_close? No — SPY adj_close is total return net of ER, so
        we set this to 0 by default to avoid double-counting; it is
        exposed for the cost×2 gate where we deliberately double-fee).
    commission_bps : float
        Per-switch commission (bps of notional). Inter=0.
    spread_bps : float
        Per-switch bid-ask spread (bps of notional). Default 5.0.
    tax_rate : float
        Year-end DARF rate on realized net gain. Default 0.15 (rota B
        Inter per mandate §4.6). 0.0 for ablation.
    """

    sma_months: int = 10
    rebal: RebalKind = "monthly"
    cash_rate_annual: float = 0.04
    spy_expense_ratio: float = 0.0  # SPY total-return is ex-ER already
    commission_bps: float = 0.0
    spread_bps: float = 5.0
    tax_rate: float = 0.15

    def __post_init__(self) -> None:
        if self.sma_months <= 0:
            raise ValueError(f"sma_months must be > 0, got {self.sma_months}")
        if self.rebal not in ("monthly", "daily"):
            raise ValueError(
                f"rebal must be 'monthly' or 'daily', got {self.rebal!r}"
            )
        if self.tax_rate < 0:
            raise ValueError(f"tax_rate must be >= 0, got {self.tax_rate}")

    @property
    def switch_cost_pct(self) -> float:
        """Combined commission+spread per regime switch, fraction."""
        return (self.commission_bps + self.spread_bps) / 10_000.0

    @property
    def daily_sma_window(self) -> int:
        """Daily-variant SMA window in trading days (``sma_months * 21``)."""
        return self.sma_months * 21


@dataclass
class B5Result:
    """Output of :func:`simulate_b5`.

    Attributes
    ----------
    equity : pd.Series
        Daily equity curve starting at 1.0, post-tax.
    daily_returns : pd.Series
        Net daily return series (derived from equity).
    regime : pd.Series
        0/1 series — 1 iff the MA regime is ON at t (shifted).
    exposure : pd.Series
        Weight on SPY per day (0.0 or 1.0 — **unleveraged**).
    switches : pd.Series
        True on days where exposure changed vs prior day.
    cum_cost_pct : float
        Total switch-cost drag.
    cum_tax_pct : float
        Total DARF paid.
    """

    equity: pd.Series
    daily_returns: pd.Series
    regime: pd.Series
    exposure: pd.Series
    switches: pd.Series
    cum_cost_pct: float = 0.0
    cum_tax_pct: float = 0.0

    def sharpe(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
        rets = self.daily_returns.dropna()
        if rets.empty:
            return 0.0
        std = float(rets.std(ddof=1))
        if std == 0.0:
            return 0.0
        return float(rets.mean() / std * np.sqrt(periods_per_year))

    def cagr(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
        eq = self.equity.dropna()
        if len(eq) < 2:
            return 0.0
        n_periods = len(eq) - 1
        years = n_periods / periods_per_year
        if years <= 0:
            return 0.0
        total = float(eq.iloc[-1] / eq.iloc[0])
        if total <= 0:
            return -1.0
        return total ** (1.0 / years) - 1.0

    def max_drawdown(self) -> float:
        eq = self.equity.dropna()
        if eq.empty:
            return 0.0
        peak = eq.cummax()
        dd = eq / peak - 1.0
        return float(dd.min())


def _month_end_positions(dates: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Return last-trading-day of each calendar month in ``dates``.

    Uses the actual trading-day index (no exchange-calendar dependency).
    Equivalent to ``groupby(year, month).last()``.
    """
    s = pd.Series(dates, index=dates)
    monthly = s.groupby([s.index.year, s.index.month]).last()
    return pd.DatetimeIndex(monthly.values)


def compute_monthly_regime(
    price: pd.Series,
    sma_months: int = 10,
) -> pd.Series:
    """Literal Faber 2007 monthly regime — 0/1 series on the **daily** index.

    Protocol
    --------

    1. Identify each calendar month's **last trading day** in ``price.index``.
    2. At month-end ``T``, compute ``sma_N_T = SMA(monthly_close, N).at[T]``
       where ``monthly_close`` = ``price`` sampled at month-ends and
       ``N = sma_months``.
    3. Raw regime at ``T`` = ``1 if close_T > sma_N_T else 0``; NaN
       during warmup (first ``sma_months`` months).
    4. Shift execution: the raw regime at ``T`` applies from the
       **next trading day** through the **next month-end inclusive**.
       Equivalently, on any trading day ``t``, the active regime is
       the most recent raw regime at a month-end **strictly before ``t``**.

    Returns
    -------
    pd.Series
        0/1 regime indexed by ``price.index``, 0 during warmup /
        before any month-end fires.

    Citations
    ---------

    * Faber 2007 canon (10-month SMA monthly filter):
      ``[phase3_7_literature_sprint §T3]``.
    * Monthly MA as trend filter with hindsight caveat:
      ``[trading_evolved, p.211-212]``.
    """
    if sma_months <= 0:
        raise ValueError(f"sma_months must be > 0, got {sma_months}")
    px = price.astype(float)
    month_ends = _month_end_positions(px.index)

    # Monthly close series (values at month-end positions only).
    monthly_close = px.reindex(month_ends)
    # SMA over sma_months monthly bars (min_periods = sma_months → NaN
    # during warmup so the raw regime is NaN and executed regime is 0).
    monthly_sma = monthly_close.rolling(
        window=sma_months, min_periods=sma_months
    ).mean()
    raw_monthly = (monthly_close > monthly_sma).astype(float)
    raw_monthly = raw_monthly.where(monthly_sma.notna(), other=np.nan)

    # Build the daily regime: for each day ``t`` pick the most recent
    # month-end regime STRICTLY BEFORE ``t``. Because ``raw_monthly`` is
    # indexed at month-ends (inclusive of ``t`` when ``t`` is itself a
    # month-end), we ffill on the full daily index AFTER shifting one
    # month-end forward. That way, the day-of-month-end itself does
    # NOT immediately flip to its own regime — it keeps the prior
    # month's regime, and the flip happens on the next trading day.
    shifted_monthly = raw_monthly.shift(1)
    daily = shifted_monthly.reindex(px.index).ffill()
    # Before the first resolved month-end signal, regime is 0.
    return daily.fillna(0.0).astype(int)


def compute_daily_regime(
    price: pd.Series,
    sma_days: int = 210,
) -> pd.Series:
    """Daily SMA-N regime with ``t-1`` shift (F2-alignment).

    Returns a 0/1 integer series — 1 iff ``close_{t-1} > SMA(N)_{t-1}``.
    Mirrors B1's ``compute_regime_signal`` with the SMA length set to
    ``sma_days`` (default 210 for 10-month daily equivalent).

    Citations
    ---------

    * SMA-200 daily ≈ SMA-10-month monthly:
      ``[leverage_for_the_long_run, p.13-14]``.
    * F2-alignment: ``[advances_fin_ml, p.31-34]``.
    """
    if sma_days <= 1:
        raise ValueError(f"sma_days must be > 1, got {sma_days}")
    px = price.astype(float)
    sma = px.rolling(window=sma_days, min_periods=sma_days).mean()
    raw = (px > sma).astype(float)
    return raw.shift(1).fillna(0.0).astype(int)


def simulate_b5(
    spy_returns: pd.Series,
    spy_price: pd.Series,
    config: B5Config,
) -> B5Result:
    """Run one B5 Faber-GTAA-single-asset config end-to-end.

    Pipeline
    --------

    1. Compute the regime signal:
       * ``rebal="monthly"`` → :func:`compute_monthly_regime` using
         ``sma_months``.
       * ``rebal="daily"`` → :func:`compute_daily_regime` using
         ``sma_months * 21`` as the daily SMA window.
    2. Build the **unleveraged** gate (0 or 1) — exposure to SPY.
    3. Build gross daily return:
       ``gross_t = gate_t × (spy_t − daily_ER) + (1 − gate_t) × cash_daily − switch_cost``.
    4. Apply year-end DARF via :func:`apply_darf_year_end` (shared with B1).

    Parameters
    ----------
    spy_returns : pd.Series
        Daily decimal SPY total returns (stitched KF pre-2001-05 + SPY
        adj_close pct_change post).
    spy_price : pd.Series
        Daily SPY cumulative-TR price (``(1 + spy_returns).cumprod() *
        100``) — must share the index with ``spy_returns``.
    config : B5Config

    Returns
    -------
    B5Result

    Raises
    ------
    ValueError
        If index alignment is violated.
    """
    if not spy_returns.index.equals(spy_price.index):
        raise ValueError("spy_returns and spy_price must share index")

    if config.rebal == "monthly":
        regime = compute_monthly_regime(spy_price, sma_months=config.sma_months)
    else:
        regime = compute_daily_regime(spy_price, sma_days=config.daily_sma_window)

    # Unleveraged: exposure ∈ {0, 1}.
    gate = regime.astype(float)
    exposure = gate.copy()

    cash_daily = config.cash_rate_annual / TRADING_DAYS_PER_YEAR
    daily_er = config.spy_expense_ratio / TRADING_DAYS_PER_YEAR

    # Gross daily return before switch cost + tax.
    #   on-regime:  gate=1 → SPY return − daily_ER
    #   off-regime: gate=0 → cash_daily
    spy_net = spy_returns.astype(float) - daily_er
    gross_noswitch = gate * spy_net + (1.0 - gate) * cash_daily

    # Switch detection — a transition absorbs the round-trip cost.
    prev_exp = exposure.shift(1).fillna(0.0)
    switches = exposure != prev_exp
    switch_drag = switches.astype(float) * config.switch_cost_pct

    gross = gross_noswitch - switch_drag
    cum_cost = float(switch_drag.sum())

    equity, daily_net, cum_tax = apply_darf_year_end(gross, config.tax_rate)

    return B5Result(
        equity=equity,
        daily_returns=daily_net,
        regime=regime,
        exposure=exposure,
        switches=switches,
        cum_cost_pct=cum_cost,
        cum_tax_pct=cum_tax,
    )
