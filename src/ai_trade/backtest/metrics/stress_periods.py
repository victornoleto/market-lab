"""Stress-period isolation — per-strategy metrics in named crisis windows.

Purpose
-------
Phase 3.5b Task 7b: given an equity curve + trade list, slice it by the
canonical stress sub-periods and report the strategy's Sharpe / drawdown
inside each window, alongside SPY buy-and-hold over the same dates. The
goal is to expose whether a "full-window" PASS is carried by one regime
or whether the strategy survives the worst sub-periods independently.

The four canonical windows (user-spec §Task 7b):

- **2008-09-01 → 2009-03-31** — Lehman to the March 2009 trough.
- **2020-02-19 → 2020-04-30** — COVID peak-to-rebound crash.
- **2022-01-03 → 2022-12-30** — full-year bear + Fed rate-hike cycle.
- **2025-01-01 → 2025-03-31** — 2025 Q1 tariff/stress shock.

The module is a dumb pure-function layer on top of
``metrics.performance`` and ``metrics.standard_report``: no data loading,
no simulation — callers pass already-computed equity/trade/SPY series.

References
----------
* Sharpe / Sortino / max-drawdown conventions match
  ``backtest.metrics.performance`` (population std, ddof=0).
* Window definitions: ``specs/phase_3_5b_winners_validation.md`` §Task 7b.
* 15% BR tax per winning trade (same as standard_report): Investment
  Mandate §4 (Path B swing broker).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

import numpy as np
import pandas as pd

from ai_trade.backtest.metrics._fmt import _fmt_num, _fmt_pct
from ai_trade.backtest.metrics.performance import (
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    returns_from_equity,
    sharpe as _sharpe,
    sortino as _sortino,
    volatility as _volatility,
)
from ai_trade.backtest.metrics.standard_report import Trade

# ---------------------------------------------------------------------------
# Canonical stress windows
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StressWindow:
    name: str
    start: pd.Timestamp
    end: pd.Timestamp
    description: str = ""


def _ts(date: str) -> pd.Timestamp:
    return pd.Timestamp(date)


STANDARD_STRESS_WINDOWS: tuple[StressWindow, ...] = (
    StressWindow(
        name="2008_crisis",
        start=_ts("2008-09-01"),
        end=_ts("2009-03-31"),
        description="Lehman collapse → March 2009 bottom (global financial crisis).",
    ),
    StressWindow(
        name="2020_covid",
        start=_ts("2020-02-19"),
        end=_ts("2020-04-30"),
        description="Pre-COVID S&P peak → April 2020 recovery shelf.",
    ),
    StressWindow(
        name="2022_bear",
        start=_ts("2022-01-03"),
        end=_ts("2022-12-30"),
        description="Full-year bear + Fed hike cycle (75bp hikes).",
    ),
    StressWindow(
        name="2025_q1",
        start=_ts("2025-01-01"),
        end=_ts("2025-03-31"),
        description="2025 Q1 tariff/rate stress shock.",
    ),
)


# ---------------------------------------------------------------------------
# Report dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StressReport:
    """Single-window per-strategy snapshot + SPY benchmark row."""

    window_name: str
    window_start: pd.Timestamp
    window_end: pd.Timestamp
    description: str

    bars: int  # bars inside window (strategy)
    n_trades: int  # trades fully contained in window
    total_return_pct: float
    cagr_pct: float
    volatility_ann_pct: float
    sharpe: float
    sortino: float
    max_drawdown_pct: float
    calmar: float

    spy_bars: int
    spy_total_return_pct: float
    spy_cagr_pct: float
    spy_sharpe: float
    spy_max_drawdown_pct: float

    excess_return_pct: float
    delta_max_dd_pct: float

    equity_curve: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))
    spy_equity_curve: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _slice_equity(equity: pd.Series, start: pd.Timestamp, end: pd.Timestamp) -> pd.Series:
    """Inclusive slice on both ends. Returns a rebased series starting at equity[0]=1.0.

    We rebase to 1.0 so CAGR/return numbers are self-contained to the
    window and don't depend on the absolute scale of the full curve.
    """
    s = equity.sort_index()
    clipped = s.loc[(s.index >= start) & (s.index <= end)]
    if len(clipped) < 2:
        return pd.Series(dtype=float)
    e0 = float(clipped.iloc[0])
    if e0 <= 0:
        return pd.Series(dtype=float)
    rebased = clipped / e0
    rebased.name = s.name
    return rebased


def _count_trades_in_window(
    trades: Sequence[Trade], start: pd.Timestamp, end: pd.Timestamp
) -> int:
    return sum(
        1
        for t in trades
        if pd.Timestamp(t.entry_date) >= start
        and pd.Timestamp(t.exit_date) <= end
    )


def _empty_report(window: StressWindow) -> StressReport:
    empty = pd.Series(dtype=float)
    return StressReport(
        window_name=window.name,
        window_start=window.start,
        window_end=window.end,
        description=window.description,
        bars=0,
        n_trades=0,
        total_return_pct=0.0,
        cagr_pct=0.0,
        volatility_ann_pct=0.0,
        sharpe=0.0,
        sortino=0.0,
        max_drawdown_pct=0.0,
        calmar=0.0,
        spy_bars=0,
        spy_total_return_pct=0.0,
        spy_cagr_pct=0.0,
        spy_sharpe=0.0,
        spy_max_drawdown_pct=0.0,
        excess_return_pct=0.0,
        delta_max_dd_pct=0.0,
        equity_curve=empty,
        spy_equity_curve=empty,
    )


def _metrics_from_equity(
    equity: pd.Series, periods_per_year: int
) -> tuple[float, float, float, float, float, float, float]:
    """Return (total_return, cagr, vol, sharpe, sortino, max_dd, calmar)."""
    if len(equity) < 2:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    rets = returns_from_equity(equity)
    v0 = float(equity.iloc[0])
    vT = float(equity.iloc[-1])
    tot = (vT - v0) / v0 if v0 > 0 else 0.0
    # For short windows, annualized CAGR is volatile but still useful as a
    # "what pace did this run at" figure; callers should cross-read with
    # total_return when duration < 1y.
    return (
        tot,
        _cagr(equity, periods_per_year),
        _volatility(rets, periods_per_year),
        _sharpe(rets, periods_per_year),
        _sortino(rets, periods_per_year),
        _max_drawdown(equity),
        _calmar_safe(equity, periods_per_year),
    )


def _calmar_safe(equity: pd.Series, periods_per_year: int) -> float:
    """Calmar with an explicit zero-guard for tiny windows."""
    mdd = _max_drawdown(equity)
    if mdd <= 1e-9:
        return 0.0
    c = _cagr(equity, periods_per_year)
    return c / mdd


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


def compute_stress_report(
    equity: pd.Series,
    trades: Sequence[Trade],
    spy_equity: pd.Series,
    window: StressWindow,
    periods_per_year: int = 252,
) -> StressReport:
    """One strategy × one window → a StressReport. Missing data → empty row."""
    strat_slice = _slice_equity(equity, window.start, window.end)
    spy_slice = _slice_equity(spy_equity, window.start, window.end)

    if len(strat_slice) < 2 and len(spy_slice) < 2:
        return _empty_report(window)

    tot, cgr, vol, shp, sor, mdd, cal = _metrics_from_equity(strat_slice, periods_per_year)
    spy_tot, spy_cgr, _spy_vol, spy_shp, _spy_sor, spy_mdd, _spy_cal = _metrics_from_equity(
        spy_slice, periods_per_year
    )

    return StressReport(
        window_name=window.name,
        window_start=window.start,
        window_end=window.end,
        description=window.description,
        bars=len(strat_slice),
        n_trades=_count_trades_in_window(trades, window.start, window.end),
        total_return_pct=tot,
        cagr_pct=cgr,
        volatility_ann_pct=vol,
        sharpe=shp,
        sortino=sor,
        max_drawdown_pct=mdd,
        calmar=cal,
        spy_bars=len(spy_slice),
        spy_total_return_pct=spy_tot,
        spy_cagr_pct=spy_cgr,
        spy_sharpe=spy_shp,
        spy_max_drawdown_pct=spy_mdd,
        excess_return_pct=tot - spy_tot,
        delta_max_dd_pct=mdd - spy_mdd,
        equity_curve=strat_slice,
        spy_equity_curve=spy_slice,
    )


def compute_all_stress_reports(
    equity: pd.Series,
    trades: Sequence[Trade],
    spy_equity: pd.Series,
    windows: Iterable[StressWindow] = STANDARD_STRESS_WINDOWS,
    periods_per_year: int = 252,
) -> list[StressReport]:
    return [
        compute_stress_report(equity, trades, spy_equity, w, periods_per_year)
        for w in windows
    ]


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _row_markdown(cells: Sequence[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def render_stress_markdown(
    strategy_name: str,
    reports: Sequence[StressReport],
) -> str:
    """Render a per-strategy Markdown section with a stress-window table.

    Columns: window / bars / #trades / total return / CAGR / vol / Sharpe
    / Sortino / max DD / SPY total / SPY max DD / ΔDD / excess return.
    """
    header = [
        "window",
        "bars",
        "#trades",
        "total %",
        "CAGR",
        "vol",
        "Sharpe",
        "Sortino",
        "max DD",
        "SPY tot %",
        "SPY max DD",
        "ΔDD (strat−SPY)",
        "excess tot %",
    ]
    separator = ["---"] * len(header)
    rows = [_row_markdown(header), _row_markdown(separator)]
    for r in reports:
        cells = [
            r.window_name,
            str(r.bars),
            str(r.n_trades),
            _fmt_pct(r.total_return_pct),
            _fmt_pct(r.cagr_pct),
            _fmt_pct(r.volatility_ann_pct),
            _fmt_num(r.sharpe, 3),
            _fmt_num(r.sortino, 3) if np.isfinite(r.sortino) else "inf",
            _fmt_pct(r.max_drawdown_pct),
            _fmt_pct(r.spy_total_return_pct),
            _fmt_pct(r.spy_max_drawdown_pct),
            _fmt_pct(r.delta_max_dd_pct),
            _fmt_pct(r.excess_return_pct),
        ]
        rows.append(_row_markdown(cells))

    lines = [
        f"## {strategy_name}",
        "",
        *rows,
        "",
    ]
    # Window descriptions follow the table so readers can recall what each
    # window covers without scrolling back to a shared header.
    lines.append("**Windows**")
    lines.append("")
    for r in reports:
        lines.append(
            f"- `{r.window_name}` ({r.window_start.date()} → {r.window_end.date()}): "
            f"{r.description}"
        )
    lines.append("")
    return "\n".join(lines)


def render_multi_strategy_stress_markdown(
    sections: Sequence[tuple[str, Sequence[StressReport]]],
    title: str = "Stress-period isolation",
) -> str:
    """Top-level doc: title + one section per strategy."""
    parts = [
        f"# {title}",
        "",
        "Per-strategy metrics inside canonical stress sub-periods; SPY"
        " buy-and-hold is aligned to the same dates for reference.",
        "",
    ]
    for name, reports in sections:
        parts.append(render_stress_markdown(name, reports))
    return "\n".join(parts).rstrip() + "\n"


__all__ = [
    "STANDARD_STRESS_WINDOWS",
    "StressReport",
    "StressWindow",
    "compute_all_stress_reports",
    "compute_stress_report",
    "render_multi_strategy_stress_markdown",
    "render_stress_markdown",
]
