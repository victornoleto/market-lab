"""Phase 3.6 Family C — Faber GTAA 10-month SMA multi-asset rotation.

A clean return-series simulator of Meb Faber's 2007 GTAA (Global Tactical
Asset Allocation): for each asset in a pre-specified universe, hold it
equal-weight on months where its end-of-month close is above an N-month
SMA; otherwise that slot goes to cash (0% return). The "on"-assets are
equal-weighted (or inverse-vol-weighted) within the risk budget.

Monthly rebalance on last trading day; the new weights take effect on
the first trading day of the next month. No mid-month re-entry. This is
a pure return-series strategy — no bar-level engine, no execution slippage
noise, ~100× faster than the bar engine, and aligned with the clean
`letf_rotation.py` pattern (reference for Phase 3.6).

Design anchors
--------------
* **Faber GTAA thesis (monthly MA filter per asset, equal weight of on
  assets, cash otherwise):** Clenow's exposition of tactical asset
  allocation with fixed-weight ETF rebalance is at
  `[trading_evolved, p.183-185]`. The Faber 10-month rule is the
  precursor in the "trend filter at index level" discussion at
  `[trading_evolved, p.211-212]` — Clenow explicitly flags it as
  potentially curve-fit to 2008 hindsight, so honest OOS gating is
  exactly what this family needs to survive.
* **Moving-average as volatility-regime proxy:**
  `[leverage_for_the_long_run, p.8]` (Gayed footnote 15) — same
  mechanism, different asset set.
* **Inverse-vol sizing (alternative grid arm):**
  `[trading_evolved, p.206-207, p.293]` + Carver
  `[systematic_trading, p.175-177, ch.10]`.
* **Retail cost / hold discipline:** `[systematic_trading, p.185-188]`
  (Carver) — monthly rebalance consistent with Inter T+1 ETF model.

4-asset universe variant (documented deviation from 5-asset canonical)
----------------------------------------------------------------------
Faber's canonical 2007 paper uses SPY / EFA / VNQ (REIT) / DBC (commodity)
/ IEF. Our Tiingo cache has SPY, EFA, IEF, GLD, AGG, TLT but NO REIT
with sufficient history (VNQ/ICF/IYR absent; XLRE starts 2015 — too
late for IS). We therefore run a **4-asset variant** SPY / EFA / GLD
(commodity proxy via gold) / IEF. This deviation is disclosed in the
aggregate report. Clenow's Ivy-style allocation at
`[trading_evolved, p.200]` also uses GLD as the commodity slot
(7.5% GLD + 7.5% DBC), supporting gold as a defensible single-commodity
proxy.

Grid (≥5 configs → enables CSCV/PBO + DSR)
------------------------------------------
* SMA window months ∈ {6, 8, 10, 12}        # Faber 2007 uses 10 [paper]
* Signal lag (trading days) ∈ {0, 1}        # t+0 apply next-bar / t+1 next-bar
* Weighting ∈ {"equal", "inv_vol"}          # equal is Faber canon
  → 4 × 2 × 2 = 16 configs, winner = grid cell with best OOS Sharpe
  among those with OOS CAGR ≥ CDI floor. PBO computed over all 16.

Costs (Inter broker — plan §3.2)
--------------------------------
* Commission: 0 bps on US ETFs.
* Monthly BR 15% capital-gains tax on realized gains (applied per
  month on any positive net monthly return).
* Bid-ask + slippage: 3 bps per rebalance event, applied on the
  **traded** notional fraction (assets switched in or out) — mandate
  §1 default retail friction.
* FX spread: NOT per-rebalance (ETFs stay USD-denominated at Inter).
  FX is only at capital deployment/withdrawal, outside backtest scope.
  Cost×2 sensitivity doubles the 3bps frictions for gate 13.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

__all__ = [
    "GTAAConfig",
    "GTAAResult",
    "compute_monthly_signals",
    "simulate_gtaa",
]


WeightingKind = Literal["equal", "inv_vol"]


@dataclass(frozen=True)
class GTAAConfig:
    """Immutable configuration for a single Faber GTAA run.

    Parameters
    ----------
    sma_months
        SMA window in calendar months. Faber canonical = 10.
        `[trading_evolved, p.211-212]` treats ``200d ≈ 10-month SMA``
        as the "trend filter" — same mechanism. Grid {6, 8, 10, 12}.
    signal_lag_days
        Trading-day lag between signal evaluation (last bar of month)
        and execution (first bar of next month). 0 = trade next bar
        immediately; 1 = trade the bar after that. Defeats look-ahead
        bias audit at `[advances_fin_ml, p.31-34]`.
    weighting
        "equal" = equal split among on-assets (Faber canon);
        "inv_vol" = weight inversely to 20-day return std per leg
        `[trading_evolved, p.206-207]`.
    commission_bps
        Round-trip commission per rebalance switch, in bps of the
        traded notional. Inter = 0 on US ETFs (plan §3.2).
    spread_bps
        Bid-ask spread per switch in bps of traded notional.
    slippage_bps
        Slippage per switch in bps of traded notional.
    tax_rate
        BR capital-gains tax on monthly realized gains (15% per
        investment mandate §1 + plan §3.2).
    vol_lookback_days
        Lookback (trading days) for inv-vol weighting. 20 business
        days ≈ 1 month, Clenow default `[trading_evolved, p.208]`.
    """

    sma_months: int = 10
    signal_lag_days: int = 0
    weighting: WeightingKind = "equal"
    commission_bps: float = 0.0
    spread_bps: float = 2.0
    slippage_bps: float = 1.0
    tax_rate: float = 0.15
    vol_lookback_days: int = 20

    def __post_init__(self) -> None:
        if self.sma_months <= 0:
            raise ValueError(f"sma_months must be > 0, got {self.sma_months}")
        if self.signal_lag_days < 0:
            raise ValueError(
                f"signal_lag_days must be >= 0, got {self.signal_lag_days}"
            )
        if self.weighting not in ("equal", "inv_vol"):
            raise ValueError(
                f"weighting must be 'equal' or 'inv_vol', got {self.weighting!r}"
            )
        if self.tax_rate < 0:
            raise ValueError(f"tax_rate must be >= 0, got {self.tax_rate}")

    @property
    def switch_cost_pct(self) -> float:
        """Combined commission + spread + slippage as fraction."""
        return (self.commission_bps + self.spread_bps + self.slippage_bps) / 10_000.0


@dataclass
class GTAAResult:
    """Output of a GTAA simulation.

    Attributes
    ----------
    equity
        Daily equity curve starting at 1.0.
    daily_returns
        Daily net return after frictions and monthly tax. Same index
        as equity.
    monthly_weights
        Per-asset target weight at each month-end rebalance
        (rows = rebal dates, cols = asset tickers). Cash weight =
        1 - sum(asset weights).
    switch_dates
        DatetimeIndex of rebalance dates (last-trading-day of each
        calendar month within the run window).
    cum_cost_pct
        Cumulative friction drag as fraction of starting equity.
    cum_tax_pct
        Cumulative BR tax paid as fraction of starting equity.
    """

    equity: pd.Series
    daily_returns: pd.Series
    monthly_weights: pd.DataFrame
    switch_dates: pd.DatetimeIndex
    cum_cost_pct: float = 0.0
    cum_tax_pct: float = 0.0

    def sharpe(self, periods_per_year: int = 252) -> float:
        rets = self.daily_returns.dropna()
        if rets.empty:
            return 0.0
        std = float(rets.std(ddof=1))
        if std == 0.0:
            return 0.0
        return float(rets.mean() / std * np.sqrt(periods_per_year))

    def cagr(self, periods_per_year: int = 252) -> float:
        eq = self.equity.dropna()
        if len(eq) < 2:
            return 0.0
        years = (len(eq) - 1) / periods_per_year
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


def _month_end_index(dates: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Return last-trading-day of each calendar month in ``dates``.

    Uses the actual trading-day index (no exchange-calendar dependency).
    Equivalent to a groupby(year, month).last().
    """
    s = pd.Series(dates, index=dates)
    monthly = s.groupby([s.index.year, s.index.month]).last()
    return pd.DatetimeIndex(monthly.values)


def compute_monthly_signals(
    prices: pd.DataFrame,
    sma_months: int = 10,
    trading_days_per_month: int = 21,
) -> pd.DataFrame:
    """Monthly GTAA on/off signal per asset.

    For each asset column, signal at month-end t =
        1.0 if close_t > SMA(close, sma_months * 21)_t
        0.0 otherwise
        NaN during warmup.

    Parameters
    ----------
    prices
        Daily close prices with DatetimeIndex, columns = assets.
    sma_months
        Window size in calendar months.
    trading_days_per_month
        Conversion factor for the SMA lookback window in trading days.

    Returns
    -------
    pd.DataFrame
        Monthly signals (1.0/0.0/NaN), indexed by last-trading-day of
        each calendar month, columns = asset tickers.

    Citations
    ---------
    * Monthly MA signal per asset (Faber 2007 canon — reproduced in
      Clenow): `[trading_evolved, p.211-212]` discusses the 200d
      (≈10-month) trend filter and its 2008-2020 hindsight caveat.
    * Same MA-filter mechanism across assets: Gayed footnote 15
      `[leverage_for_the_long_run, p.8]`.
    """
    if sma_months <= 0:
        raise ValueError(f"sma_months must be > 0, got {sma_months}")
    window = sma_months * trading_days_per_month

    px = prices.astype(float)
    sma = px.rolling(window=window, min_periods=window).mean()
    # Signal is evaluated at every bar; we will subset to month-ends later.
    daily_signal = (px > sma).astype(float).where(sma.notna(), other=np.nan)

    month_ends = _month_end_index(px.index)
    # Month-end snapshot of daily signal.
    monthly = daily_signal.reindex(month_ends, method=None)
    return monthly


def _inv_vol_weights(
    returns: pd.DataFrame,
    as_of: pd.Timestamp,
    lookback_days: int,
    on_assets: list[str],
) -> pd.Series:
    """Inverse-volatility weights among the on-assets.

    Uses the ``lookback_days`` of daily returns ending at ``as_of``
    (inclusive). If an asset has zero or missing vol, it receives an
    equal-weight share (protects against degenerate lookback).

    Citation: `[trading_evolved, p.206-207]` inverse-vol sizing +
    `[systematic_trading, p.175-177]` vol-target framework.
    """
    if not on_assets:
        return pd.Series(dtype=float)
    window = returns.loc[:as_of].iloc[-lookback_days:]
    vol = window[on_assets].std(ddof=1)
    if vol.isna().any() or (vol == 0).any():
        # Fall back to equal weight when volatilities are degenerate.
        return pd.Series(1.0 / len(on_assets), index=on_assets)
    inv = 1.0 / vol
    return inv / inv.sum()


def simulate_gtaa(
    prices: pd.DataFrame,
    returns: pd.DataFrame,
    config: GTAAConfig,
) -> GTAAResult:
    """Run a single Faber-style GTAA configuration end-to-end.

    Parameters
    ----------
    prices
        Daily close prices (adjusted) with DatetimeIndex, columns = assets.
        Signal is computed from this (SMA on close).
    returns
        Daily total-returns aligned on the same index, same columns.
        P&L is computed from this (using `prev_weight × ret` alignment
        — one-day shift — per `[advances_fin_ml, p.31-34]`).
    config
        Grid cell configuration (sma_months, lag, weighting, costs, tax).

    Returns
    -------
    GTAAResult

    Raises
    ------
    ValueError
        If prices and returns are misaligned or columns disagree.
    """
    if not prices.index.equals(returns.index):
        raise ValueError("prices and returns must share the same DatetimeIndex")
    if list(prices.columns) != list(returns.columns):
        raise ValueError("prices and returns must have identical columns")

    assets = list(prices.columns)

    # Monthly signals (last-trading-day of each calendar month).
    monthly_sig = compute_monthly_signals(prices, config.sma_months)
    # Drop rows where ALL signals are NaN (warmup period).
    monthly_sig = monthly_sig.dropna(how="all")

    # Build a daily weights schedule. The weight on day d is determined by
    # the LAST month-end-signal BEFORE (or equal to) d - signal_lag_days.
    # This enforces "signal decided at month-end close, executed after
    # signal_lag_days trading days" — no mid-month re-entry, no lookahead.
    daily_weights = pd.DataFrame(0.0, index=prices.index, columns=assets)
    switch_dates: list[pd.Timestamp] = []

    rebal_month_ends = list(monthly_sig.index)

    # For each rebalance month-end, compute the target weights.
    # Then those weights apply from (month_end + 1 + signal_lag_days) until
    # next rebalance.
    for me in rebal_month_ends:
        sig_row = monthly_sig.loc[me].fillna(0.0)
        on_assets = [a for a in assets if sig_row[a] > 0.5]

        if not on_assets:
            target = pd.Series(0.0, index=assets)
        elif config.weighting == "equal":
            w = 1.0 / len(on_assets)
            target = pd.Series(
                {a: (w if a in on_assets else 0.0) for a in assets}
            )
        else:  # inv_vol
            ivw = _inv_vol_weights(
                returns, me, config.vol_lookback_days, on_assets
            )
            target = pd.Series(
                {a: float(ivw.get(a, 0.0)) for a in assets}
            )

        # Find execution date: me + 1 + lag (by trading-day position).
        try:
            me_pos = prices.index.get_loc(me)
        except KeyError:
            continue
        exec_pos = me_pos + 1 + config.signal_lag_days
        if exec_pos >= len(prices.index):
            # Not enough trading days left — skip (edge of series).
            continue
        exec_date = prices.index[exec_pos]
        switch_dates.append(exec_date)
        # Apply these weights from exec_date onward (will be overwritten
        # on next rebalance exec_date).
        daily_weights.loc[exec_date:, assets] = target.values

    # Apply P&L using prev_weight × ret — per `[advances_fin_ml, p.31-34]`.
    # daily_weights.shift(1) ensures we use yesterday's weight to compute
    # today's P&L.
    prev_weights = daily_weights.shift(1).fillna(0.0)
    daily_ret_gross = (prev_weights * returns.fillna(0.0)).sum(axis=1)

    # Rebalance frictions: on each switch_date, apply switch_cost_pct
    # scaled by traded notional = sum(|Δw|) / 2 across assets.
    cost_series = pd.Series(0.0, index=prices.index)
    weight_diff = daily_weights.diff().abs().sum(axis=1)  # gross turnover
    traded_notional = weight_diff / 2.0  # one-way notional fraction
    cost_series = traded_notional * config.switch_cost_pct

    # BR tax 15% on POSITIVE monthly net return (realized at month-end,
    # per investment mandate §1 + plan §3.2). Losses carry forward within
    # the same month only (simple per-month offset).
    daily_net_before_tax = daily_ret_gross - cost_series

    # Compound into monthly totals, apply tax on positive monthly totals,
    # then convert back to a per-day net return that matches the monthly
    # product. Implementation detail: we apply tax as a one-day hit on
    # the last-trading-day of each month (realized gain).
    equity = 1.0
    equity_curve: list[float] = []
    cum_cost = 0.0
    cum_tax = 0.0

    dates = prices.index
    # Precompute month-end positions for tax application.
    month_end_dates = set(_month_end_index(dates))

    # Rolling month gross for tax base.
    month_start_equity = equity

    for ts, r_net in daily_net_before_tax.items():
        r_net = 0.0 if np.isnan(r_net) else float(r_net)
        # Apply day's net (already includes cost for rebalance days).
        new_equity = equity * (1.0 + r_net)
        cum_cost += float(cost_series.loc[ts]) * equity
        equity = new_equity

        if ts in month_end_dates and config.tax_rate > 0:
            # Monthly realized gain since month_start_equity.
            gain = max(0.0, equity - month_start_equity)
            tax = gain * config.tax_rate
            equity -= tax
            cum_tax += tax
            month_start_equity = equity

        equity_curve.append(equity)

    equity_series = pd.Series(equity_curve, index=dates, name="equity")
    # Reconstruct net daily returns from equity path (includes tax).
    daily_net = equity_series.pct_change().fillna(0.0)

    # Monthly weights frame for diagnostics.
    monthly_weights = daily_weights.reindex(rebal_month_ends).fillna(0.0)

    return GTAAResult(
        equity=equity_series,
        daily_returns=daily_net,
        monthly_weights=monthly_weights,
        switch_dates=pd.DatetimeIndex(switch_dates),
        cum_cost_pct=cum_cost,
        cum_tax_pct=cum_tax,
    )
