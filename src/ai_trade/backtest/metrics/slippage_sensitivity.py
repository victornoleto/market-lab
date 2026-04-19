"""Slippage sensitivity — per-strategy robustness at varying transaction cost.

Purpose
-------
Phase 3.5b Task 7c: sweep a set of total round-trip transaction-cost
levels (e.g. ``{0, 1, 5, 10}`` basis points) and report Sharpe / CAGR /
max-drawdown / cost drag for each Phase 3 winner + the 3-leg portfolio.
The goal is to confirm the PASS verdicts survive under a range of
execution-cost assumptions, not only the 15-bp baseline used in Tasks
3-6.

Interpretation of "round-trip slippage" here:

* Each regime switch in the Phase 3 strategies (LETF rotation, TSMOM
  Donchian) closes one position and opens another on the same bar — it
  is the full "round-trip" event. The cost model in
  :class:`ai_trade.backtest.strategies.letf_rotation.LETFRotationConfig`
  and :class:`ai_trade.backtest.strategies.tsmom.TSMOMConfig` already
  debits ``(commission_bps + spread_bps) * equity / 10_000`` at each
  such switch. To model a slippage level of ``X`` bps per switch we
  simply set ``commission_bps=0, spread_bps=X`` (tax, annual fee, and
  FFR drag — if active — stay untouched).

* ``{0, 1, 5, 10}`` bps covers the realistic small-retail range for
  SPY/QQQ/GLD ETFs on a BR swing broker (Path B) — the baseline
  15-bp winner config already sits at the pessimistic edge of this
  range. Levels above baseline are not in the spec but would be a
  natural extension for institutional use-cases.

The module is a dumb pure-function layer: no simulation, no data
loading. Callers pass already-computed ``equity`` / ``daily_returns`` /
``n_switches`` and receive :class:`SlippageRow` rows, one per level.

Citations
---------
* Spec: ``specs/phase_3_5b_winners_validation.md`` §Task 7c.
* Cost-model documentation: ``[advances_fin_ml, p.261-266]`` — realistic
  cost assumptions as a necessary robustness gate for any live strategy.
* Winner configs frozen (Phase 3 jornadas iter 32/36/37/40) — this
  module only perturbs the ``commission_bps``/``spread_bps`` fields.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd

from ai_trade.backtest.metrics._fmt import _fmt_num, _fmt_pct
from ai_trade.backtest.metrics.performance import (
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    returns_from_equity,
    sharpe as _sharpe,
    volatility as _volatility,
)

# ---------------------------------------------------------------------------
# Canonical levels
# ---------------------------------------------------------------------------

#: Round-trip cost levels (basis points per regime switch) mandated by
#: Phase 3.5b spec §Task 7c.
CANONICAL_SLIPPAGE_LEVELS_BPS: tuple[float, ...] = (0.0, 1.0, 5.0, 10.0)


# ---------------------------------------------------------------------------
# Row dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SlippageRow:
    """Metrics for one (strategy, slippage level) combination."""

    level_bps: float
    bars: int
    n_switches: int
    cum_cost_pct: float  # fraction of starting equity lost to switch costs
    total_return_pct: float
    cagr_pct: float
    volatility_ann_pct: float
    sharpe: float
    # Positive-magnitude DD convention (matches performance.max_drawdown
    # and stress_periods.StressReport.max_drawdown_pct).
    max_drawdown_pct: float


def summarize_equity(
    equity: pd.Series,
    level_bps: float,
    n_switches: int,
    cum_cost_pct: float,
    periods_per_year: int = 252,
) -> SlippageRow:
    """Compute a :class:`SlippageRow` for a simulated equity curve.

    Parameters
    ----------
    equity : pd.Series
        Daily equity curve (rebased or absolute — only ratios are used).
    level_bps : float
        The slippage level assumed for this run (bps per switch).
    n_switches : int
        Number of regime switches the simulator executed.
    cum_cost_pct : float
        Fraction of the starting equity lost to switch costs over the
        run (the ``cum_cost_pct`` field of ``RotationResult`` /
        ``TSMOMResult``).
    periods_per_year : int
        Annualization factor. Default 252 trading days.
    """
    eq = equity.dropna()
    if len(eq) < 2:
        return SlippageRow(
            level_bps=level_bps,
            bars=0,
            n_switches=n_switches,
            cum_cost_pct=cum_cost_pct,
            total_return_pct=0.0,
            cagr_pct=0.0,
            volatility_ann_pct=0.0,
            sharpe=0.0,
            max_drawdown_pct=0.0,
        )
    rets = returns_from_equity(eq)
    total_return = float(eq.iloc[-1] / eq.iloc[0] - 1.0)
    return SlippageRow(
        level_bps=level_bps,
        bars=len(eq),
        n_switches=n_switches,
        cum_cost_pct=cum_cost_pct,
        total_return_pct=total_return,
        cagr_pct=_cagr(eq, periods_per_year=periods_per_year),
        volatility_ann_pct=_volatility(rets, periods_per_year=periods_per_year),
        sharpe=_sharpe(rets, periods_per_year=periods_per_year),
        max_drawdown_pct=_max_drawdown(eq),
    )


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _row_to_md(row: SlippageRow) -> list[str]:
    return [
        f"{row.level_bps:.0f}",
        f"{row.bars}",
        f"{row.n_switches}",
        _fmt_pct(row.cum_cost_pct),
        _fmt_pct(row.total_return_pct),
        _fmt_pct(row.cagr_pct),
        _fmt_pct(row.volatility_ann_pct),
        _fmt_num(row.sharpe),
        _fmt_pct(row.max_drawdown_pct),
    ]


_COLUMNS = (
    "slippage_bps",
    "bars",
    "n_switches",
    "cum_cost",
    "total_return",
    "CAGR",
    "vol_ann",
    "Sharpe",
    "max_DD",
)


def render_strategy_slippage_markdown(
    name: str, rows: Sequence[SlippageRow]
) -> str:
    """Render a per-strategy slippage table to Markdown."""
    header = "| " + " | ".join(_COLUMNS) + " |"
    sep = "| " + " | ".join("---" for _ in _COLUMNS) + " |"
    body = [
        "| " + " | ".join(_row_to_md(r)) + " |"
        for r in rows
    ]
    return "\n".join([f"### {name}", "", header, sep, *body, ""])


def render_multi_strategy_slippage_markdown(
    sections: Sequence[tuple[str, Sequence[SlippageRow]]],
    title: str = "Slippage sensitivity",
    levels_bps: Sequence[float] = CANONICAL_SLIPPAGE_LEVELS_BPS,
) -> str:
    """Render the top-level Markdown report for all strategies."""
    parts: list[str] = [f"# {title}", ""]
    parts.append(
        "Total per-switch transaction cost is set to the `slippage_bps` value "
        "for each row (`commission_bps=0, spread_bps=slippage_bps`). Tax rate, "
        "annual fee, and any FFR-aware funding drag are held constant at the "
        "Phase 3 winner defaults. Winner configs are frozen per Phase 3 iter "
        "32/36/37/40 jornadas."
    )
    parts.append("")
    parts.append(
        "Swept levels (bps): " + ", ".join(f"{int(l)}" for l in levels_bps)
    )
    parts.append("")
    for name, rows in sections:
        parts.append(render_strategy_slippage_markdown(name, list(rows)))
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Helper: build cost-varied config clones
# ---------------------------------------------------------------------------


def make_cost_varied_config(config, level_bps: float):
    """Return a clone of ``config`` with total switch cost set to ``level_bps``.

    The clone has ``commission_bps=0`` and ``spread_bps=level_bps`` — other
    fields (tax, leverage, lookbacks, …) are preserved via
    :func:`dataclasses.replace`. Works for any frozen dataclass that
    exposes those two fields (``LETFRotationConfig``, ``TSMOMConfig``).
    """
    from dataclasses import replace

    if level_bps < 0:
        raise ValueError(f"level_bps must be >= 0, got {level_bps}")
    return replace(config, commission_bps=0.0, spread_bps=float(level_bps))


__all__ = [
    "CANONICAL_SLIPPAGE_LEVELS_BPS",
    "SlippageRow",
    "make_cost_varied_config",
    "render_multi_strategy_slippage_markdown",
    "render_strategy_slippage_markdown",
    "summarize_equity",
]
