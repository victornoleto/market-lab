"""Phase 3.6 Family B — Risk Parity inverse-vol multi-asset ETF rotation.

Clean return-series simulator for a 21-trading-day rebalanced,
inverse-volatility-weighted basket of liquid ETFs. Unleveraged. Built
explicitly with ``prev_weight * ret`` alignment (one-day shift) so no
lookahead slips in.

Design (Phase 3.6 plan §5, Family B spec)
-----------------------------------------

* **Universe:** 4 liquid ETFs spanning three economic risk premia —
  ``SPY`` (US equity), ``TLT`` (long-duration nominal bonds, interest
  rate risk), ``GLD`` (gold, inflation hedge), ``EEM`` (EM equity,
  additional equity/currency exposure). Defensible under Qian's three
  primary risk premia  (equity / interest rate / inflation-hedge)
  framework ``[risk_parity, p.17-18, ch.2]``. Commodity breadth (DBC,
  GSG) not available in the Tiingo snapshot — EEM substitutes as a
  second equity-risk diversifier. This is **naïve inverse-vol risk
  parity** (the 2-asset case is ERC-exact; the N-asset case
  approximates ERC) ``[risk_parity, p.10-11, ch.1]``.
* **Weighting:** ``w_i = (1/σ_i) / Σ(1/σ_j)`` — naïve inverse-vol risk
  parity ``[risk_parity, p.10-11, ch.1]``. Correlations deliberately
  ignored for robustness (full ERC needs Excel-Solver-style iteration
  and is brittle to covariance estimation noise; naïve inverse-vol is
  what retail implementations actually use and what Carver endorses as
  diversified multiplier scaling) ``[systematic_trading, p.185-188]``.
* **Vol lookback N (grid):** 20, 40, 60, 120 trading days.
  Carver's vol-target chapter uses 25-36 days exponentially weighted
  ``[systematic_trading, p.~175]``; Qian uses ≥ 3 years monthly
  ``[risk_parity, p.166-167]``. The grid spans retail/tactical (20-60)
  through strategic (120). Central choice: 60d ``[risk_parity,
  p.166-167]`` (short-enough to adapt to regime, long-enough for stable
  σ).
* **Target volatility (grid):** 10% (conservative retail) and 15%
  (Carver default) annualized. Scaling factor applied daily to the
  raw inverse-vol weights: ``k = target_vol / realized_portfolio_vol``
  ``[systematic_trading, p.~175]``. Portfolio leverage CAPPED at 1.0
  (no leverage, per spec — risk parity WITH leverage is a different
  family).
* **Grid total: 4 × 2 = 8 configs** (meets ≥ 5 for CPCV/PBO/DSR).
* **Rebalance:** every 21 trading days. Full-rebalance (no threshold).
  Monthly rebalance is the Qian/Carver standard
  ``[risk_parity, p.166-167]``, ``[systematic_trading, p.~195]``.
* **No regime filter** — risk parity is always-on by construction
  ``[risk_parity, p.10, ch.1]``. Any regime overlay would be a
  different family (Gayed LRS, GTAA, etc.).
* **Frictions:** Banco Inter model — zero ETF commission, FX spread
  1.25% one-way (the round-trip ≈ 2.5% gets paid only on the
  ``BRL → USD`` at first entry and the ``USD → BRL`` at final exit; per
  the plan §3.2 the round-trip FX is amortized over monthly rebal
  turnover). 15% BR capital-gains tax applied monthly on positive
  realized P&L at each rebalance ``[investment_mandate, §1, §3]``.

Engine cleanliness
------------------

The simulator uses an **explicit** ``w_{t-1} * r_t`` formulation:

1. At end of day ``t`` compute target weights ``w_t`` from σ estimated on
   returns through ``t`` (inclusive).
2. Hold ``w_t`` from day ``t+1`` through the next rebalance date.
3. Daily portfolio return ``r_p[t+1] = Σ_i w_t[i] * r_i[t+1] - daily_drag``.

Daily drag = none (unleveraged, no financing cost). FX spread is
applied to the net USD turnover at each rebalance (not every bar). Tax
is applied monthly on realized positive portfolio return (the per-day
net return already has the rebalance costs baked in; the 15% tax is
then deducted as a one-off at the rebalance).

No bar-level Portfolio/Order machinery — this is a pure return-series
strategy, same pattern as ``letf_rotation.py``.

Citations
---------

* Inverse-vol / naïve risk parity:  ``[risk_parity, p.10-11, ch.1]``
* Three risk premia universe:        ``[risk_parity, p.17-18, ch.2]``
* Vol lookback window choice:         ``[systematic_trading, p.~175]``
* Vol-targeting mechanic:             ``[systematic_trading, p.~175]``
* Retail cost model + monthly rebal:  ``[systematic_trading, p.185-188]``
* Lookahead-free t+1 execution:       ``[advances_fin_ml, p.31-34]``
* CDI soft-floor 13% CAGR:            ``[investment_mandate, §2]``
* Inter broker cost model:            ``[investment_mandate, §3]``
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

__all__ = [
    "RPInverseVolConfig",
    "RPInverseVolResult",
    "simulate_rp_inverse_vol",
]

TRADING_DAYS_PER_YEAR = 252


@dataclass(frozen=True)
class RPInverseVolConfig:
    """Immutable config for one RP inverse-vol run.

    Parameters
    ----------
    universe : tuple[str, ...]
        Ordered ETF ticker list. Default = (SPY, TLT, GLD, EEM) per
        three-risk-premia framework ``[risk_parity, p.17-18, ch.2]``.
    vol_lookback : int
        Trailing-window length (in trading days) for realized σ
        estimation. Grid: {20, 40, 60, 120}. Central = 60.
        ``[systematic_trading, p.~175]``.
    target_vol : float
        Target annualized portfolio volatility. Grid: {0.10, 0.15}.
        ``[systematic_trading, p.~175]``.
    rebalance_days : int
        Rebalance cadence in trading days. 21 ≈ calendar month.
        ``[risk_parity, p.166-167]``, ``[systematic_trading, p.~195]``.
    max_leverage : float
        Hard cap on ``Σ|w|``. Default 1.0 (unleveraged per spec).
    fx_spread_one_way : float
        One-way BRL↔USD FX spread fraction (Inter 0.99-1.50%; midpoint
        1.25%). Applied to net turnover at each rebalance.
        ``[investment_mandate, §3]``, plan §3.2.
    tax_rate_monthly : float
        Monthly realized-P&L tax (BR 15%). Applied on positive
        month-over-month portfolio return, deducted once per rebal.
        ``[investment_mandate, §1]``.
    vol_floor : float
        Minimum per-asset σ to avoid divide-by-zero. Default 1e-6.

    Notes
    -----
    ``max_leverage=1.0`` combined with vol-targeting means the vol-scale
    factor ``k`` is CLAMPED at 1.0 (never leverage up). This makes the
    strategy conservative in low-vol regimes — by design, per the
    Family B spec.
    """

    universe: tuple[str, ...] = ("SPY", "TLT", "GLD", "EEM")
    vol_lookback: int = 60
    target_vol: float = 0.10
    rebalance_days: int = 21
    max_leverage: float = 1.0
    fx_spread_one_way: float = 0.0125
    tax_rate_monthly: float = 0.15
    vol_floor: float = 1e-6

    def __post_init__(self) -> None:
        if len(self.universe) < 2:
            raise ValueError(f"universe must have ≥2 tickers, got {self.universe!r}")
        if self.vol_lookback < 5:
            raise ValueError(f"vol_lookback must be ≥5, got {self.vol_lookback}")
        if self.target_vol <= 0:
            raise ValueError(f"target_vol must be > 0, got {self.target_vol}")
        if self.rebalance_days < 1:
            raise ValueError(f"rebalance_days must be ≥1, got {self.rebalance_days}")
        if self.max_leverage <= 0:
            raise ValueError(f"max_leverage must be > 0, got {self.max_leverage}")
        if not 0.0 <= self.fx_spread_one_way < 0.1:
            raise ValueError(f"fx_spread_one_way must be in [0, 0.1), got {self.fx_spread_one_way}")
        if not 0.0 <= self.tax_rate_monthly < 0.5:
            raise ValueError(f"tax_rate_monthly in [0, 0.5), got {self.tax_rate_monthly}")

    @property
    def slug(self) -> str:
        return (
            f"N{self.vol_lookback}_tvol{int(self.target_vol * 100):02d}"
            f"_rbd{self.rebalance_days}"
        )


@dataclass
class RPInverseVolResult:
    """End-to-end simulation output."""

    equity: pd.Series
    daily_returns: pd.Series  # net of drag/tax/FX
    daily_returns_gross: pd.Series  # before tax & FX
    weights: pd.DataFrame  # one row per trading day, cols = universe
    rebalance_dates: pd.DatetimeIndex
    cum_fx_cost: float = 0.0
    cum_tax: float = 0.0
    config: RPInverseVolConfig | None = None

    def sharpe(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
        r = self.daily_returns.dropna()
        if r.empty:
            return 0.0
        sd = float(r.std(ddof=1))
        if sd == 0.0:
            return 0.0
        return float(r.mean() / sd * np.sqrt(periods_per_year))

    def cagr(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
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
        return float((eq / peak - 1.0).min())


def _compute_realized_vol(
    returns: pd.DataFrame, lookback: int
) -> pd.DataFrame:
    """Per-asset trailing realized σ (annualized) on a return-panel.

    σ_{i,t} = sqrt(252) * std(r_{i, t-lookback+1 .. t}, ddof=1).

    Uses **information available at t** — no lookahead. The first
    ``lookback-1`` rows are NaN.

    ``[systematic_trading, p.~175]``.
    """
    return returns.rolling(window=lookback, min_periods=lookback).std(ddof=1) * np.sqrt(
        TRADING_DAYS_PER_YEAR
    )


def _compute_rp_weights(
    sigma_row: pd.Series,
    target_vol: float,
    max_leverage: float,
    vol_floor: float,
    cov_window: pd.DataFrame | None = None,
) -> pd.Series:
    """Inverse-vol weights for one rebalance date, with vol-target cap.

    Steps:
      1. Raw ``w_raw[i] = (1/σ_i) / Σ(1/σ_j)`` — naïve RP.
         ``[risk_parity, p.10-11, ch.1]``.
      2. Estimate portfolio σ using either the diagonal approximation
         (``σ_p ≈ sqrt(Σ w² σ²)``) OR the full covariance if provided.
      3. Scale factor ``k = target_vol / σ_p``, clamped to [0, max_lev].
         ``[systematic_trading, p.~175]``.
      4. Final ``w = k * w_raw``.

    Returns NaN vector if any σ is NaN.
    """
    if sigma_row.isna().any():
        return pd.Series(np.nan, index=sigma_row.index)

    # Floor σ to avoid divide-by-zero on freak zero-vol days.
    sigma = sigma_row.clip(lower=vol_floor)
    inv = 1.0 / sigma
    w_raw = inv / inv.sum()

    # Portfolio σ under diagonal assumption (uncorrelated proxy). This
    # is the retail-standard approximation — full covariance pushes
    # towards ERC but the spec says "naïve inverse-vol".
    if cov_window is None:
        sigma_p = float(np.sqrt(((w_raw * sigma) ** 2).sum()))
    else:
        cov_ann = cov_window.values * TRADING_DAYS_PER_YEAR
        sigma_p = float(np.sqrt(w_raw.values @ cov_ann @ w_raw.values))

    if sigma_p <= 0:
        return pd.Series(0.0, index=sigma_row.index)

    k = target_vol / sigma_p
    # CLAMP TO max_leverage — no leverage-up by construction.
    k = min(k, max_leverage)
    k = max(k, 0.0)

    return w_raw * k


def simulate_rp_inverse_vol(
    returns: pd.DataFrame,
    config: RPInverseVolConfig,
) -> RPInverseVolResult:
    """Full simulation of one RP inverse-vol config.

    Parameters
    ----------
    returns : pd.DataFrame
        Daily simple returns per asset. Must contain all tickers listed
        in ``config.universe``. Index = trading-day ``DatetimeIndex``.
        **Already aligned** (inner-joined across tickers, no NaNs on
        rows after warmup).
    config : RPInverseVolConfig
        Grid cell config.

    Returns
    -------
    RPInverseVolResult
        Equity curve, daily returns (net of tax+FX), weights DataFrame,
        rebalance dates.

    Engine conventions
    ------------------

    * At end of day ``t_rebal`` (a rebalance day), compute σ on the
      trailing window **ending at t_rebal inclusive**. Then apply those
      new weights **starting t_rebal + 1** (one-day shift — lookahead
      free per ``[advances_fin_ml, p.31-34]``).
    * Between rebalance days, weights drift with price (buy-and-hold
      inside the month). This is the standard monthly-rebal convention
      — ``[risk_parity, p.166-167]``.
    * First rebalance happens at the first bar where the σ estimate is
      available (i.e. bar ``vol_lookback - 1``, zero-indexed). Before
      that, the portfolio sits in cash (all weights = 0).
    """
    missing = [t for t in config.universe if t not in returns.columns]
    if missing:
        raise ValueError(f"missing tickers in returns: {missing}")

    rets = returns[list(config.universe)].astype(float).copy()
    rets.index = pd.DatetimeIndex(rets.index)

    # Trailing σ panel (NaN until window is full).
    sigma_panel = _compute_realized_vol(rets, config.vol_lookback)

    n = len(rets)
    tickers = list(config.universe)
    n_assets = len(tickers)

    # Rebalance calendar: every rebalance_days bars, starting at the
    # first bar where σ at t-1 is available (i.e. t-1 ≥ lookback - 1,
    # so t ≥ lookback). This keeps the simulator strictly lookahead-
    # free: weights applied at day t are derived from σ computed on
    # returns through day t-1 inclusive. ``[advances_fin_ml, p.31-34]``.
    first_rebal_idx = config.vol_lookback
    rebal_idxs = list(range(first_rebal_idx, n, config.rebalance_days))

    rebal_dates_actual: list[pd.Timestamp] = []

    # Build the actual held-weights panel by forward-filling from each
    # rebalance point — but the drift between rebalances means weights
    # evolve with price moves. Model: at each rebalance we set exposure
    # to `new_w`, and inside the month weights drift proportionally to
    # realized returns.
    weights_held = pd.DataFrame(0.0, index=rets.index, columns=tickers)
    current_w = np.zeros(n_assets, dtype=float)
    rebal_i_ptr = 0

    gross_returns = np.zeros(n, dtype=float)
    fx_costs = np.zeros(n, dtype=float)
    taxes = np.zeros(n, dtype=float)
    equity_path = np.zeros(n, dtype=float)

    equity = 1.0
    period_entry_equity = 1.0  # equity at last rebal, for tax calc

    rebal_dates_set = set(rebal_idxs)

    for t in range(n):
        # === Rebalance at start of day t (use σ from day t-1) ===
        if t in rebal_dates_set:
            # The σ used to set weights is sigma_panel.iloc[t-1] so the
            # weights being applied at t are based on info up to t-1 —
            # no lookahead.
            if t == 0:
                new_w = np.zeros(n_assets, dtype=float)
            else:
                sigma_row = sigma_panel.iloc[t - 1]
                if sigma_row.isna().any():
                    new_w = current_w  # hold previous
                else:
                    w_series = _compute_rp_weights(
                        sigma_row,
                        config.target_vol,
                        config.max_leverage,
                        config.vol_floor,
                    )
                    new_w = w_series.values.astype(float)

            # Turnover = Σ|Δw| * equity, in USD terms.
            turnover_usd = float(np.abs(new_w - current_w).sum()) * equity
            # FX spread: applied to the change in USD-denominated notional.
            # First allocation ever: we convert BRL→USD, pay spread. On
            # rebal: only the *net* change pays FX spread.
            fx_cost = turnover_usd * config.fx_spread_one_way
            equity -= fx_cost
            fx_costs[t] += fx_cost

            # BR monthly tax — 15% on realized positive P&L since last
            # rebalance. A conservative proxy for "realized" during the
            # rebalance: we treat the delta equity since last rebalance
            # entry as realized because we've churned weights.
            # (Investment mandate §1: 15% on realized gains; rebalance
            # realizes the gain.)
            realized_pnl = equity - period_entry_equity
            if realized_pnl > 0 and config.tax_rate_monthly > 0:
                tax = realized_pnl * config.tax_rate_monthly
                equity -= tax
                taxes[t] += tax
            period_entry_equity = equity

            current_w = new_w.copy()
            rebal_dates_actual.append(rets.index[t])

        # === Apply day's return with CURRENT weights ===
        r_vec = rets.iloc[t].values.astype(float)
        r_port = float((current_w * r_vec).sum())
        gross_returns[t] = r_port

        equity_new = equity * (1.0 + r_port)
        equity_path[t] = equity_new

        # Drift: weights evolve with returns (no rebalance inside month)
        # w_i[t+1] = w_i[t] * (1 + r_i[t]) / (1 + r_port[t])   when w_i ≠ 0
        if equity_new > 0 and equity > 0:
            new_current = current_w * (1.0 + r_vec) / (1.0 + r_port) if (1.0 + r_port) != 0 else current_w
            current_w = new_current

        weights_held.iloc[t] = current_w
        equity = equity_new

    equity_series = pd.Series(equity_path, index=rets.index)
    # Net daily returns: derived from equity path (baked-in FX + tax).
    net_daily = equity_series.pct_change().fillna(equity_path[0] - 1.0)
    gross_daily = pd.Series(gross_returns, index=rets.index)

    return RPInverseVolResult(
        equity=equity_series,
        daily_returns=net_daily,
        daily_returns_gross=gross_daily,
        weights=weights_held,
        rebalance_dates=pd.DatetimeIndex(rebal_dates_actual),
        cum_fx_cost=float(fx_costs.sum()),
        cum_tax=float(taxes.sum()),
        config=config,
    )


def build_config_grid(
    universe: Sequence[str] = ("SPY", "TLT", "GLD", "EEM"),
    vol_lookbacks: Sequence[int] = (20, 40, 60, 120),
    target_vols: Sequence[float] = (0.10, 0.15),
    rebalance_days: int = 21,
    fx_spread_one_way: float = 0.0125,
    tax_rate_monthly: float = 0.15,
) -> list[RPInverseVolConfig]:
    """Enumerate the 4×2 = 8-config grid for CPCV/PBO."""
    out: list[RPInverseVolConfig] = []
    for lb in vol_lookbacks:
        for tv in target_vols:
            out.append(
                RPInverseVolConfig(
                    universe=tuple(universe),
                    vol_lookback=int(lb),
                    target_vol=float(tv),
                    rebalance_days=int(rebalance_days),
                    fx_spread_one_way=float(fx_spread_one_way),
                    tax_rate_monthly=float(tax_rate_monthly),
                )
            )
    return out
