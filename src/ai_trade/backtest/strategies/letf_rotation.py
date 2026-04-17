"""LETF Rotation Strategy — Gayed's Leverage Rotation Strategy (LRS).

Return-series simulator for the Leverage Rotation Strategy described in
``books/summaries/leverage_for_the_long_run.md`` (Gayed 2016/2020):

* **RISK_ON** (index above MA ± band): hold daily-leveraged S&P 500
  synthesized via :func:`ai_trade.backtest.helpers.synthetic_letf.synthesize_letf_returns`.
* **RISK_OFF** (index below MA ∓ band): rotate to cash or a
  blended cash/gold allocation.

Path B [SWING BROKER] — no swap, no intraday rebalancing. Daily
close-to-close decisions. BR capital-gains tax (15%) applied to
realized gains at each RISK_ON → RISK_OFF transition.

Design choices
--------------

Unlike :class:`ai_trade.backtest.strategies.etf_rotation.ETFRotationStrategy`
this module does **not** use the bar-level engine. Gayed's LRS is a
pure return-series strategy: each day the rule produces a single
leveraged or cash return, and the compounded equity curve follows
directly from those returns. Bypassing the Portfolio/Bar machinery
gives us:

* Exact replication of the paper's methodology (no execution slippage
  noise).
* ~100x speed for the 360-config grid (B1b) on 56 years of daily data.
* Simpler hook for CPCV / PBO / block bootstrap (operate directly on
  the daily return vector).

Citations
---------

* LRS signal (SMA 200, above→RISK_ON, below→RISK_OFF):
  ``[leverage_for_the_long_run, p.13]``.
* Leverage rotation via SMA as volatility-regime proxy:
  ``[leverage_for_the_long_run, p.7, p.11]``.
* ETF implementation uses **cash**, not BIL, for RISK_OFF:
  ``[leverage_for_the_long_run, p.21]``.
* Synthetic leveraged return formula (``r = L·r_SPX - fee/252``):
  ``[leverage_for_the_long_run, p.16]``.
* MA periods {10, 20, 50, 100, 200} all produce positive alpha
  (Sharpe 0.58-0.68): ``[leverage_for_the_long_run, p.14, Table 6]``.
* All leverage levels {1.25, 2, 3} tested in paper:
  ``[leverage_for_the_long_run, p.17, Table 8]``.

Grid deviations (documented for Lead B1)
----------------------------------------

* **EMA** added to filter grid (Gayed uses SMA only, p.8). Rationale:
  the Reddit study uses EMA 125; including both lets the gates decide.
* **Band** parameter (0, 3, 5%) added. Rationale: the Reddit study
  uses 5% band to dampen whipsaws. Gayed uses 0% implicitly (strict
  cross). Winner by gates, not affinity.
* **Lookback** restricted to {100, 125, 150, 200} for the 360-config
  grid (shorter MAs {10, 20, 50} excluded per mandate pre-specification).
* **Off-asset** widened to include partial gold allocations (25/50/75/
  100% gold, balance cash). Rationale: Gayed uses cash only; mandate
  asks us to test gold as a hedge. Winner by gates.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import pandas as pd

from ai_trade.backtest.helpers.synthetic_letf import (
    DEFAULT_ANNUAL_FEE,
    TRADING_DAYS_PER_YEAR,
    synthesize_letf_returns,
)

log = logging.getLogger(__name__)

__all__ = [
    "LETFRotationConfig",
    "RotationResult",
    "compute_regime_signal",
    "simulate_letf_rotation",
]


FilterKind = Literal["SMA", "EMA"]
RegimeState = Literal["ON", "OFF"]


@dataclass(frozen=True)
class LETFRotationConfig:
    """Immutable configuration for a single LETF rotation run.

    Each (filter, lookback, band_pct, leverage, gold_weight) combination
    defines one grid cell. Costs and tax are kept in the config so cost
    ablation is trivial (flip a flag, rerun the grid).

    Parameters
    ----------
    filter : {"SMA", "EMA"}
        Moving-average flavour on the underlying index. Gayed uses SMA
        [p.8]. EMA added per grid widening (see module docstring).
    lookback : int
        MA window in trading days. Canonical 200 per Gayed [p.16].
    band_pct : float
        Hysteresis band as fraction (e.g. 0.05 = 5%). RISK_ON requires
        ``price > MA * (1 + band_pct)``; RISK_OFF requires
        ``price < MA * (1 - band_pct)``. Inside the band: keep prior
        state. Band 0.0 = strict cross. Reddit-style 5% band.
    leverage : float
        Daily leverage factor applied on RISK_ON days. 1.0 = unlevered
        SPX. Values {1.25, 2.0, 3.0} tested in Gayed [p.17].
    gold_weight : float
        Fraction of RISK_OFF allocation going to gold; the remainder is
        cash (0 return). Values {0.0, 0.25, 0.50, 0.75, 1.0}. 0.0 = pure
        cash (Gayed canonical, p.21).
    annual_fee : float
        Leverage expense ratio applied as daily drag on RISK_ON days.
        1% pre-2021, 0.95% post-2021 [p.16].
    commission_bps : float
        Round-trip commission per regime switch in basis points of the
        switched notional. 10 bps = 0.10% per switch. Applied on ON↔OFF
        transitions (not on "hold" days).
    spread_bps : float
        Bid-ask spread cost per switch in basis points. 5 bps = 0.05%.
        Applied on transitions only.
    tax_rate : float
        Capital-gains tax on realized gain at each RISK_ON exit.
        BR swing rate = 15% per Investment Mandate §4.
    cash_rate_annual : float
        Annual risk-free rate used for cash sleeve of RISK_OFF. Default
        0.0 — matches Gayed's ETF implementation which holds literal
        cash, not a T-bill ETF [p.21]. Set to a positive value for
        high-rate regimes.
    """

    filter: FilterKind = "SMA"
    lookback: int = 200
    band_pct: float = 0.0
    leverage: float = 3.0
    gold_weight: float = 0.0
    annual_fee: float = DEFAULT_ANNUAL_FEE
    commission_bps: float = 10.0
    spread_bps: float = 5.0
    tax_rate: float = 0.15
    cash_rate_annual: float = 0.0

    def __post_init__(self) -> None:
        if self.filter not in ("SMA", "EMA"):
            raise ValueError(f"filter must be SMA or EMA, got {self.filter!r}")
        if self.lookback <= 1:
            raise ValueError(f"lookback must be > 1, got {self.lookback}")
        if self.band_pct < 0:
            raise ValueError(f"band_pct must be >= 0, got {self.band_pct}")
        if self.leverage <= 0:
            raise ValueError(f"leverage must be > 0, got {self.leverage}")
        if not 0.0 <= self.gold_weight <= 1.0:
            raise ValueError(
                f"gold_weight must be in [0, 1], got {self.gold_weight}"
            )

    @property
    def switch_cost_pct(self) -> float:
        """Combined commission + spread on each regime switch, as fraction."""
        return (self.commission_bps + self.spread_bps) / 10_000.0


@dataclass
class RotationResult:
    """Output of a rotation simulation.

    Attributes
    ----------
    equity : pd.Series
        Daily equity curve starting at 1.0.
    daily_returns : pd.Series
        Net daily return after fees/costs/tax. Same index as equity.
    regime : pd.Series
        String series "ON" or "OFF" per day.
    switches : pd.Series
        Boolean series — True when day ``t`` had a regime change vs ``t-1``.
    cum_cost_pct : float
        Cumulative switch-cost drag (commission + spread) across the run,
        expressed as fraction of starting equity lost to costs.
    cum_tax_pct : float
        Cumulative tax paid across the run, as fraction of starting equity.
    """

    equity: pd.Series
    daily_returns: pd.Series
    regime: pd.Series
    switches: pd.Series
    cum_cost_pct: float = 0.0
    cum_tax_pct: float = 0.0

    def sharpe(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
        """Annualized Sharpe from daily net returns. Zero std → 0.0."""
        rets = self.daily_returns.dropna()
        if rets.empty:
            return 0.0
        std = float(rets.std(ddof=1))
        if std == 0.0:
            return 0.0
        return float(rets.mean() / std * np.sqrt(periods_per_year))

    def cagr(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
        """Annualized compound growth rate from the equity path."""
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
        """Maximum drawdown as a negative fraction (e.g. -0.35 = -35%)."""
        eq = self.equity.dropna()
        if eq.empty:
            return 0.0
        peak = eq.cummax()
        dd = eq / peak - 1.0
        return float(dd.min())


def compute_regime_signal(
    prices: pd.Series,
    filter: FilterKind = "SMA",
    lookback: int = 200,
    band_pct: float = 0.0,
) -> pd.Series:
    """Daily RISK_ON/RISK_OFF signal via MA filter with optional band.

    The first ``lookback-1`` bars yield NaN (insufficient history).
    Inside the band (``MA·(1-band) ≤ price ≤ MA·(1+band)``) the signal
    **holds** the previous state — this is the hysteresis behaviour
    described by the Reddit study's 5% band; Gayed's 0% band collapses
    this to a strict cross.

    Parameters
    ----------
    prices : pd.Series
        Daily close prices of the index (SPY or SPX TR).
    filter : {"SMA", "EMA"}
        Moving-average flavour. SMA = simple mean of last ``lookback``
        closes. EMA = exponentially-weighted with span ``lookback``
        (alpha = 2/(lookback+1)).
    lookback : int
        MA period in days. Must be > 1.
    band_pct : float
        Band width as fraction of MA. 0.0 = strict cross.

    Returns
    -------
    pd.Series
        String series with values in {"ON", "OFF"} or NaN for warmup.

    Citations
    ---------

    * SMA definition: ``[leverage_for_the_long_run, p.8]`` (footnote 15).
    * Band hysteresis: used by the Reddit reference study (off-paper).
      Reported here as a widening of Gayed's strict rule.
    """
    if filter not in ("SMA", "EMA"):
        raise ValueError(f"filter must be SMA or EMA, got {filter!r}")
    if lookback <= 1:
        raise ValueError(f"lookback must be > 1, got {lookback}")
    if band_pct < 0:
        raise ValueError(f"band_pct must be >= 0, got {band_pct}")

    px = prices.astype(float)
    if filter == "SMA":
        ma = px.rolling(window=lookback, min_periods=lookback).mean()
    else:
        ma = px.ewm(span=lookback, min_periods=lookback, adjust=False).mean()

    upper = ma * (1.0 + band_pct)
    lower = ma * (1.0 - band_pct)

    signal: list[str | float] = []
    prev: str | None = None
    for p, up, lo in zip(px.values, upper.values, lower.values):
        if np.isnan(up) or np.isnan(lo):
            signal.append(np.nan)
            continue
        if p > up:
            prev = "ON"
        elif p < lo:
            prev = "OFF"
        # inside band → hold prev. If prev is still None, default OFF
        # (safer: wait for a definitive cross before going risk-on).
        signal.append(prev if prev is not None else "OFF")

    return pd.Series(signal, index=prices.index, dtype=object)


def simulate_letf_rotation(
    spx_returns: pd.Series,
    spx_prices: pd.Series,
    config: LETFRotationConfig,
    gold_returns: pd.Series | None = None,
) -> RotationResult:
    """Run a single LETF rotation configuration end-to-end.

    Produces a compounded equity curve matching Gayed's LRS
    methodology. Transaction costs, leverage drag, and tax are
    applied explicitly.

    Parameters
    ----------
    spx_returns : pd.Series
        Daily total-return of the S&P 500. Must share index with
        ``spx_prices``.
    spx_prices : pd.Series
        Daily close price series used for the MA signal. Typically the
        same index's total-return price series (``cumprod(1+r) * 100``)
        so the MA is "TR-aware" — Gayed uses TR closes [p.8].
    config : LETFRotationConfig
        Grid cell configuration. Must be immutable (frozen dataclass).
    gold_returns : pd.Series | None
        Daily gold returns (aligned to ``spx_returns.index``). Required
        if ``config.gold_weight > 0``.

    Returns
    -------
    RotationResult
        Equity, daily returns, regime, switches, and aggregate cost/tax.

    Raises
    ------
    ValueError
        If ``gold_returns`` is required but not provided, or if inputs
        are misaligned.
    """
    if not spx_returns.index.equals(spx_prices.index):
        raise ValueError("spx_returns and spx_prices must share the same index")
    if config.gold_weight > 0 and gold_returns is None:
        raise ValueError(
            "gold_returns required when config.gold_weight > 0"
        )
    if gold_returns is not None and not gold_returns.index.equals(spx_returns.index):
        raise ValueError("gold_returns must share index with spx_returns")

    regime = compute_regime_signal(
        spx_prices, config.filter, config.lookback, config.band_pct
    )

    on_returns = synthesize_letf_returns(
        spx_returns, config.leverage, config.annual_fee
    )

    cash_daily = config.cash_rate_annual / TRADING_DAYS_PER_YEAR
    if gold_returns is None:
        off_returns = pd.Series(cash_daily, index=spx_returns.index)
    else:
        off_returns = (
            config.gold_weight * gold_returns
            + (1.0 - config.gold_weight) * cash_daily
        )

    daily_net = pd.Series(0.0, index=spx_returns.index)
    switches = pd.Series(False, index=spx_returns.index)
    prev_regime: str | None = None
    equity = 1.0
    equity_curve = []
    entry_equity = 1.0  # equity at last ON entry, for BR tax on exit
    cum_cost = 0.0
    cum_tax = 0.0

    for ts in spx_returns.index:
        cur_regime = regime.loc[ts]
        if not isinstance(cur_regime, str):
            # Warmup — hold cash, no signal.
            equity_curve.append(equity)
            continue

        # Apply the day's pre-cost return based on current regime.
        if cur_regime == "ON":
            r = on_returns.loc[ts]
        else:
            r = off_returns.loc[ts]

        r = 0.0 if np.isnan(r) else float(r)

        # Detect transition — costs & tax are taken at the open of the
        # new regime (i.e. deducted from the equity BEFORE applying the
        # new regime's return). This models rebalance-at-close with
        # settlement next day, which is the common Gayed interpretation
        # [p.13, p.21].
        if prev_regime is not None and cur_regime != prev_regime:
            switches.loc[ts] = True
            # Switch cost: commission + spread on the switched notional.
            cost = config.switch_cost_pct * equity
            equity -= cost
            cum_cost += cost
            # BR tax realized on RISK_ON exit if equity > entry_equity.
            # Gayed uses theoretical US-style; we model BR 15% per mandate.
            if prev_regime == "ON" and config.tax_rate > 0:
                gain = max(0.0, equity - entry_equity)
                tax = gain * config.tax_rate
                equity -= tax
                cum_tax += tax
            # Track new ON entry for next tax event.
            if cur_regime == "ON":
                entry_equity = equity

        # Apply regime return.
        new_equity = equity * (1.0 + r)
        # Compute net return attributed to the day (including any
        # switch-costs taken above).
        daily_net.loc[ts] = (new_equity / equity_curve[-1] - 1.0) if equity_curve else 0.0
        equity = new_equity
        equity_curve.append(equity)
        prev_regime = cur_regime

    equity_series = pd.Series(equity_curve, index=spx_returns.index[: len(equity_curve)])
    return RotationResult(
        equity=equity_series,
        daily_returns=daily_net,
        regime=regime,
        switches=switches,
        cum_cost_pct=cum_cost,
        cum_tax_pct=cum_tax,
    )
