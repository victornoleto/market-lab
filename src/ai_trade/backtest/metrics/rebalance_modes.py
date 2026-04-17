"""Rebalance-mode simulators — Phase 3.5b Addendum Task C1 [SWING BROKER].

Three pure functions applied to a DataFrame of per-leg daily returns and
a set of target weights:

* :func:`apply_daily_rebalance` — weights reset to target at close of
  every bar. Canonical "baseline" used by ``portfolio_combiner`` +
  ``portfolio_3leg``. Zero drift by construction; zero realized tax.
* :func:`apply_monthly_sell_rebalance` — weights drift within each
  month; on the last bar of each month, overweight legs are sold and
  proceeds buy the underweights. Realized gains on sells pay
  ``tax_rate`` (default 15 % BR per Investment Mandate §4). Net tax
  reduces portfolio value.
* :func:`apply_monthly_cashflow_rebalance` — weights drift; on the last
  bar of each month, ``monthly_deposit`` is added **entirely to the
  most-underweight leg**. No sells → no realized tax. Designed to model
  a disciplined monthly contribution via a broker with cash deposit
  flow (Plano B, BR swing broker).

Design choices
--------------
* Rebalance date detection via ``index.to_period(freq)`` groupby —
  returns the last *actual* bar of each period, robust to holidays /
  missing months. This matches the practitioner convention of "last
  trading day of the month".
* Cost-basis tracking per-leg is proportional: when a leg is sold, the
  realized cost basis is ``sold_amount * (leg_basis / leg_equity)``.
  Buys raise the basis dollar-for-dollar. Simplification vs lot-level
  FIFO, but symmetric with the monthly compounding mindset ``[carver_systematic,
  p.107-111]`` — swing strategies turn over infrequently, so averaged
  basis is a reasonable approximation.
* Tax is computed only on **realized gains** (``max(0, gain) *
  tax_rate``). Losses are not credited against gains across legs
  (conservative; a real BR broker statement could offset within the
  same month, but we do not net).
* Daily rebalance reports drift = 0 for every bar — any intraday drift
  is reset at close. Realistic for backtests where the cost of
  rebalance is not modelled at the sizing level. Tax for daily-rebal
  mode is **zero by construction** (the spec explicitly reuses the
  current ``portfolio_combiner`` convention — every bar is treated as
  a forced rebalance with no realized-gain accounting).

Output format
-------------
All three functions return :class:`RebalanceResult`:

* ``equity``          — total portfolio value per bar (``pd.Series``).
* ``leg_equity``      — per-leg dollar position per bar.
* ``weights``         — actual post-rebalance weights per bar.
* ``drift``           — ``|actual_w - target_w|`` per leg per bar.
* ``taxable_events``  — list[:class:`TaxableEvent`] for sell-based
  modes (daily + cashflow modes return an empty list).
* ``total_tax_paid``  — aggregate 15 % IR paid across all events.
* ``total_deposits``  — aggregate external deposits (cashflow mode).

Citations
---------
* Baseline "rebalance every bar" = ``[advances_fin_ml, p.298-299]``
  (naive 1/n or fixed weights as Bayesian prior absent strong evidence).
* Cost-basis / tax accounting: Investment Mandate §4 (BR 15 % capital
  gains on swing realized trades), cross-ref spec
  ``specs/phase_3_5b_addendum_operational.md`` §Task C.
* Drift-vs-tax tradeoff framing: ``[leverage_for_the_long_run, p.17,
  Table 8]`` — infrequent rebalance preserves compounding but drifts
  risk budget; monthly chosen as the operational cadence for retail
  swing trading.

Path tag: **[SWING BROKER]** — Plano B context (15 % IR, no swap).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

__all__ = [
    "TaxableEvent",
    "RebalanceResult",
    "apply_daily_rebalance",
    "apply_monthly_sell_rebalance",
    "apply_monthly_cashflow_rebalance",
]


@dataclass(frozen=True)
class TaxableEvent:
    """Single sell that crystallised a realized gain / loss."""

    date: pd.Timestamp
    leg: str
    proceeds: float
    cost_basis_sold: float
    realized_gain: float
    tax_paid: float


@dataclass
class RebalanceResult:
    """Output of a rebalance-mode simulation."""

    equity: pd.Series
    leg_equity: pd.DataFrame
    weights: pd.DataFrame
    drift: pd.DataFrame
    taxable_events: list[TaxableEvent] = field(default_factory=list)
    total_tax_paid: float = 0.0
    total_deposits: float = 0.0

    @property
    def returns(self) -> pd.Series:
        """Daily portfolio returns derived from equity (``pct_change``)."""
        return self.equity.pct_change().dropna()

    @property
    def max_drift(self) -> pd.Series:
        """Per-bar max absolute drift across legs."""
        return self.drift.max(axis=1)

    @property
    def n_taxable_events(self) -> int:
        return len(self.taxable_events)


def _validate_inputs(
    returns_df: pd.DataFrame,
    target_weights: dict[str, float] | pd.Series,
) -> tuple[pd.DataFrame, pd.Series]:
    if not isinstance(returns_df, pd.DataFrame):
        raise TypeError("returns_df must be a pandas DataFrame")
    if not isinstance(returns_df.index, pd.DatetimeIndex):
        raise TypeError("returns_df.index must be a DatetimeIndex")
    if returns_df.empty:
        raise ValueError("returns_df is empty")
    if returns_df.isna().any().any():
        raise ValueError(
            "returns_df contains NaN — fill or drop before calling"
        )
    w = pd.Series(target_weights, dtype=float)
    if set(w.index) != set(returns_df.columns):
        raise ValueError(
            "target_weights index must match returns_df columns exactly; "
            f"got weights={sorted(w.index)} vs cols={sorted(returns_df.columns)}"
        )
    if (w < 0).any():
        raise ValueError("target_weights must be non-negative (long-only)")
    total = float(w.sum())
    if abs(total - 1.0) > 1e-9:
        raise ValueError(
            f"target_weights must sum to 1.0, got {total:.9f}"
        )
    return returns_df.astype(float).copy(), w.reindex(returns_df.columns)


def _rebalance_dates(
    index: pd.DatetimeIndex, freq: str = "M"
) -> pd.DatetimeIndex:
    """Last bar of each ``freq`` period actually present in ``index``.

    Uses ``to_period(freq)`` groupby + ``tail(1)`` so holidays and
    missing months don't yield phantom rebalance dates.
    """
    if len(index) == 0:
        return index
    s = pd.Series(range(len(index)), index=index)
    last_per_period = s.groupby(s.index.to_period(freq)).tail(1)
    return last_per_period.index


def apply_daily_rebalance(
    returns_df: pd.DataFrame,
    target_weights: dict[str, float] | pd.Series,
    initial_capital: float = 1.0,
) -> RebalanceResult:
    """Reset weights to target at close of every bar.

    Portfolio return on bar ``t`` equals ``Σ w_j · r_{j,t}`` — the
    canonical weighted-sum convention used by the current
    ``portfolio_combiner``. No realized tax, zero drift.

    References: ``[advances_fin_ml, p.298-299]``.
    """
    rdf, w = _validate_inputs(returns_df, target_weights)
    target = w.values

    port_r = rdf.mul(w.values, axis=1).sum(axis=1)
    equity = initial_capital * (1.0 + port_r).cumprod()
    equity.name = "equity"

    leg_equity = pd.DataFrame(
        np.outer(equity.values, target),
        index=rdf.index,
        columns=rdf.columns,
    )
    weights_df = pd.DataFrame(
        np.tile(target, (len(rdf), 1)),
        index=rdf.index,
        columns=rdf.columns,
    )
    drift_df = pd.DataFrame(
        0.0,
        index=rdf.index,
        columns=rdf.columns,
    )
    return RebalanceResult(
        equity=equity,
        leg_equity=leg_equity,
        weights=weights_df,
        drift=drift_df,
        taxable_events=[],
        total_tax_paid=0.0,
        total_deposits=0.0,
    )


def _simulate_no_rebalance(
    rdf: pd.DataFrame, target: np.ndarray, initial_capital: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Internal helper: buy-and-hold compounding, no rebalancing.

    Returns ``(leg_equity_path, total_path, weights_path, drift_path)``
    as NumPy arrays shaped ``(T, N)`` (weights/drift/leg) or ``(T,)``
    (total).
    """
    n_bars = len(rdf)
    n_legs = len(target)
    leg_e = np.zeros((n_bars, n_legs), dtype=float)
    total = np.zeros(n_bars, dtype=float)
    weights = np.zeros((n_bars, n_legs), dtype=float)
    drift = np.zeros((n_bars, n_legs), dtype=float)
    current = target * initial_capital
    for i in range(n_bars):
        current = current * (1.0 + rdf.iloc[i].values)
        tot = current.sum()
        leg_e[i] = current
        total[i] = tot
        actual_w = current / tot if tot > 0 else target.copy()
        weights[i] = actual_w
        drift[i] = np.abs(actual_w - target)
    return leg_e, total, weights, drift


def apply_monthly_sell_rebalance(
    returns_df: pd.DataFrame,
    target_weights: dict[str, float] | pd.Series,
    initial_capital: float = 1.0,
    tax_rate: float = 0.15,
    rebalance_freq: str = "M",
) -> RebalanceResult:
    """Rebalance at end-of-period by selling overweight → buying underweight.

    On each rebalance date:

    1. Apply the bar's return to each leg.
    2. Compute ``Δ = w_target · T - E_j`` per leg (``T = Σ E_j``).
    3. For each leg with ``Δ < 0`` (overweight): sell ``|Δ|`` dollars.
       Realized gain = ``sold - sold · (basis / E_j)``; tax =
       ``max(0, gain) · tax_rate`` reduces the available proceeds pool.
    4. Distribute the tax-adjusted proceeds pool to underweight legs
       in proportion to their positive ``Δ``.

    Because tax eats part of the rebalance pool, post-rebalance weights
    may not reach target exactly — residual drift equals the relative
    size of total_tax_this_bar vs total portfolio.

    References: Investment Mandate §4 (BR 15 % IR); cost-basis
    averaging choice documented in module docstring.
    """
    if tax_rate < 0 or tax_rate >= 1:
        raise ValueError(f"tax_rate must be in [0, 1), got {tax_rate}")
    rdf, w = _validate_inputs(returns_df, target_weights)
    target = w.values
    legs = list(rdf.columns)
    n_legs = len(legs)
    n_bars = len(rdf)

    rebal_set = set(_rebalance_dates(rdf.index, freq=rebalance_freq))

    current_equity = target * initial_capital
    leg_basis = target * initial_capital
    leg_e = np.zeros((n_bars, n_legs), dtype=float)
    total_path = np.zeros(n_bars, dtype=float)
    weights_path = np.zeros((n_bars, n_legs), dtype=float)
    drift_path = np.zeros((n_bars, n_legs), dtype=float)
    events: list[TaxableEvent] = []
    total_tax = 0.0

    for i in range(n_bars):
        ts = rdf.index[i]
        current_equity = current_equity * (1.0 + rdf.iloc[i].values)

        if ts in rebal_set:
            total_pre = current_equity.sum()
            if total_pre > 1e-12:
                target_dollars = target * total_pre
                deltas = target_dollars - current_equity
                proceeds_pool = 0.0
                for j in range(n_legs):
                    if deltas[j] < -1e-12:
                        sell_amount = float(-deltas[j])
                        if current_equity[j] > 1e-12:
                            basis_per_dollar = (
                                leg_basis[j] / current_equity[j]
                            )
                            cost_basis_sold = (
                                sell_amount * basis_per_dollar
                            )
                            realized_gain = sell_amount - cost_basis_sold
                            tax = max(0.0, realized_gain) * tax_rate
                        else:
                            cost_basis_sold = 0.0
                            realized_gain = 0.0
                            tax = 0.0
                        events.append(
                            TaxableEvent(
                                date=ts,
                                leg=legs[j],
                                proceeds=sell_amount,
                                cost_basis_sold=float(cost_basis_sold),
                                realized_gain=float(realized_gain),
                                tax_paid=float(tax),
                            )
                        )
                        current_equity[j] -= sell_amount
                        leg_basis[j] = max(
                            0.0, leg_basis[j] - cost_basis_sold
                        )
                        proceeds_pool += sell_amount - tax
                        total_tax += tax

                buy_needed = np.maximum(deltas, 0.0)
                buy_total = float(buy_needed.sum())
                if buy_total > 1e-12 and proceeds_pool > 1e-12:
                    alloc = buy_needed / buy_total * proceeds_pool
                    current_equity = current_equity + alloc
                    leg_basis = leg_basis + alloc

        tot = current_equity.sum()
        leg_e[i] = current_equity
        total_path[i] = tot
        actual_w = current_equity / tot if tot > 1e-12 else target.copy()
        weights_path[i] = actual_w
        drift_path[i] = np.abs(actual_w - target)

    equity_series = pd.Series(total_path, index=rdf.index, name="equity")
    return RebalanceResult(
        equity=equity_series,
        leg_equity=pd.DataFrame(leg_e, index=rdf.index, columns=legs),
        weights=pd.DataFrame(weights_path, index=rdf.index, columns=legs),
        drift=pd.DataFrame(drift_path, index=rdf.index, columns=legs),
        taxable_events=events,
        total_tax_paid=float(total_tax),
        total_deposits=0.0,
    )


def apply_monthly_cashflow_rebalance(
    returns_df: pd.DataFrame,
    target_weights: dict[str, float] | pd.Series,
    monthly_deposit: float,
    initial_capital: float = 1.0,
    rebalance_freq: str = "M",
) -> RebalanceResult:
    """Deposit ``monthly_deposit`` into the most-underweight leg each period.

    No sells, so no realized tax. Weights still drift through the month;
    the deposit partially corrects on rebalance dates. Convergence to
    target depends on ``monthly_deposit / total_equity`` ratio — small
    deposits drift further from target over time.

    When ``monthly_deposit == 0`` the function degenerates to pure
    buy-and-hold (weights drift freely, no rebalance effect).
    """
    if monthly_deposit < 0:
        raise ValueError("monthly_deposit must be non-negative")
    rdf, w = _validate_inputs(returns_df, target_weights)
    target = w.values
    legs = list(rdf.columns)
    n_legs = len(legs)
    n_bars = len(rdf)

    rebal_set = set(_rebalance_dates(rdf.index, freq=rebalance_freq))

    current_equity = target * initial_capital
    leg_basis = target * initial_capital
    leg_e = np.zeros((n_bars, n_legs), dtype=float)
    total_path = np.zeros(n_bars, dtype=float)
    weights_path = np.zeros((n_bars, n_legs), dtype=float)
    drift_path = np.zeros((n_bars, n_legs), dtype=float)
    total_deposits = 0.0

    for i in range(n_bars):
        ts = rdf.index[i]
        current_equity = current_equity * (1.0 + rdf.iloc[i].values)

        if ts in rebal_set and monthly_deposit > 0:
            tot_pre = current_equity.sum()
            actual_w_now = (
                current_equity / tot_pre
                if tot_pre > 1e-12
                else target.copy()
            )
            underweight = target - actual_w_now
            j_star = int(np.argmax(underweight))
            current_equity[j_star] += monthly_deposit
            leg_basis[j_star] += monthly_deposit
            total_deposits += monthly_deposit

        tot = current_equity.sum()
        leg_e[i] = current_equity
        total_path[i] = tot
        actual_w = current_equity / tot if tot > 1e-12 else target.copy()
        weights_path[i] = actual_w
        drift_path[i] = np.abs(actual_w - target)

    equity_series = pd.Series(total_path, index=rdf.index, name="equity")
    return RebalanceResult(
        equity=equity_series,
        leg_equity=pd.DataFrame(leg_e, index=rdf.index, columns=legs),
        weights=pd.DataFrame(weights_path, index=rdf.index, columns=legs),
        drift=pd.DataFrame(drift_path, index=rdf.index, columns=legs),
        taxable_events=[],
        total_tax_paid=0.0,
        total_deposits=float(total_deposits),
    )
