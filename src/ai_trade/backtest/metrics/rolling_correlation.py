"""Rolling correlation — diversification stability across regimes.

Purpose
-------
Phase 3.5b Task 7e: measure how pair-wise correlation between the three
Phase 3 winner legs (LETF rotation EMA100/2x, QQQ Donchian 20/10, GLD
Donchian 40/20) evolves through time, identify periods where the
diversification premise breaks (high-ρ regimes), and produce summary
statistics per pair plus a time-series export for plotting downstream.

The three pairs are:

* ``LETF × QQQ`` — both equity-momentum streams; expected to be highly
  correlated in calm on-regimes and in crises.
* ``LETF × GLD`` — equity-vs-gold; expected near-zero / mildly negative.
* ``QQQ × GLD`` — equity-vs-gold; similar expectation.

Two lookback windows are canonical:

* ``63`` trading days (≈ 1 quarter) — fast diversification monitor.
* ``252`` trading days (≈ 1 calendar year) — slow "regime" monitor.

A high-correlation regime is defined as a contiguous streak of bars
where **all three pairs** simultaneously exceed a high-ρ threshold
(default ``0.7``). This is a strict definition: the portfolio's
diversification benefit requires *at least one* cross-pair correlation
to stay low, so an "all-three-above" regime is the worst case.

Path tag: **[SWING BROKER]** — same post-tax daily-return streams used
upstream in the allocation-comparison module.

Citations
---------
* Spec: ``specs/phase_3_5b_winners_validation.md`` §Task 7e.
* Rolling-correlation risk monitoring: ``[advances_fin_ml, p.289-293]``
  (clusterization / structural break detection on correlation matrices).
* Diversification breakdown in crises: ``[ang_asset_pricing, ch.12]``
  (correlations rise towards 1 in tail events — motivation for the
  high-ρ regime test).

Design notes
------------
* The module is a pure-function layer: no data loading, no simulation.
  Callers pass already-aligned daily-return series.
* We intentionally skip Fisher-z averaging: the goal is a monitoring
  diagnostic, not a statistical estimator of a population ρ. Raw
  Pearson is simpler to audit in a Markdown report.
* Rolling windows use ``min_periods=window`` so the first ``window-1``
  bars emit ``NaN`` — reported stats ignore those rows.
* Streak detection uses a simple boolean-run-length scan. All three
  pairs must be ``>= threshold`` simultaneously on every bar of a
  streak.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np
import pandas as pd

from ai_trade.backtest.grid.portfolio_3leg import align_returns_3
from ai_trade.backtest.metrics._fmt import _fmt_num, _fmt_pct

__all__ = [
    "CANONICAL_WINDOWS",
    "CANONICAL_HIGH_RHO_THRESHOLD",
    "PairwiseRollingStats",
    "HighCorrelationRegime",
    "RollingCorrelationReport",
    "pairwise_rolling_correlations",
    "summarize_pair",
    "find_high_correlation_regimes",
    "compute_rolling_correlation_report",
    "render_rolling_correlation_markdown",
]


# ---------------------------------------------------------------------------
# Canonical knobs
# ---------------------------------------------------------------------------

#: Canonical rolling-window lengths (trading days) mandated by the spec.
CANONICAL_WINDOWS: tuple[int, ...] = (63, 252)

#: High-ρ threshold above which the pair is flagged as "diversification
#: broken". Conventional lattice in institutional risk reports
#: [advances_fin_ml, p.289-293].
CANONICAL_HIGH_RHO_THRESHOLD: float = 0.7


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PairwiseRollingStats:
    """Summary of one (pair, window) rolling-correlation series."""

    pair: str  # "A_vs_B"
    window: int
    bars: int  # non-NaN rolling bars
    mean: float
    median: float
    std: float
    min: float
    max: float
    p25: float
    p75: float
    last: float  # most recent rolling value
    frac_above_threshold: float
    threshold: float
    longest_streak_above: int  # consecutive bars with ρ >= threshold

    def to_dict(self) -> dict:
        return {
            "pair": self.pair,
            "window": int(self.window),
            "bars": int(self.bars),
            "mean": float(self.mean),
            "median": float(self.median),
            "std": float(self.std),
            "min": float(self.min),
            "max": float(self.max),
            "p25": float(self.p25),
            "p75": float(self.p75),
            "last": float(self.last),
            "frac_above_threshold": float(self.frac_above_threshold),
            "threshold": float(self.threshold),
            "longest_streak_above": int(self.longest_streak_above),
        }


@dataclass(frozen=True)
class HighCorrelationRegime:
    """A contiguous streak where all three pairs exceed the threshold."""

    window: int
    threshold: float
    start: pd.Timestamp
    end: pd.Timestamp
    bars: int
    mean_rho_letf_qqq: float
    mean_rho_letf_gld: float
    mean_rho_qqq_gld: float

    def to_dict(self) -> dict:
        return {
            "window": int(self.window),
            "threshold": float(self.threshold),
            "start": str(self.start.date()),
            "end": str(self.end.date()),
            "bars": int(self.bars),
            "mean_rho_letf_qqq": float(self.mean_rho_letf_qqq),
            "mean_rho_letf_gld": float(self.mean_rho_letf_gld),
            "mean_rho_qqq_gld": float(self.mean_rho_qqq_gld),
        }


@dataclass(frozen=True)
class RollingCorrelationReport:
    """Container for all per-pair stats + high-ρ regimes per window."""

    leg_names: tuple[str, str, str]
    common_start: pd.Timestamp
    common_end: pd.Timestamp
    bars: int
    threshold: float
    windows: tuple[int, ...]
    pair_stats: tuple[PairwiseRollingStats, ...]
    regimes: tuple[HighCorrelationRegime, ...]
    series: dict[int, pd.DataFrame] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "leg_names": list(self.leg_names),
            "common_start": str(self.common_start.date()),
            "common_end": str(self.common_end.date()),
            "bars": int(self.bars),
            "threshold": float(self.threshold),
            "windows": list(self.windows),
            "pair_stats": [s.to_dict() for s in self.pair_stats],
            "regimes": [r.to_dict() for r in self.regimes],
        }


# ---------------------------------------------------------------------------
# Core computations
# ---------------------------------------------------------------------------


def pairwise_rolling_correlations(
    a: pd.Series,
    b: pd.Series,
    c: pd.Series,
    window: int,
) -> pd.DataFrame:
    """Return a DataFrame with rolling Pearson ρ for the three pairs.

    Columns: ``{A}_vs_{B}``, ``{A}_vs_{C}``, ``{B}_vs_{C}``, where the
    leg name is taken from the ``name`` attribute of each input series
    (falls back to ``leg_0/1/2`` if unnamed).

    Parameters
    ----------
    a, b, c : pd.Series
        Aligned daily-return series (callers should run
        :func:`ai_trade.backtest.grid.portfolio_3leg.align_returns_3`
        first).
    window : int
        Rolling lookback in bars. Must be ``>= 2``.
    """
    if window < 2:
        raise ValueError(f"window must be >= 2, got {window}")
    if not (len(a) == len(b) == len(c)):
        raise ValueError(
            f"series must share the same length: got {len(a)}/{len(b)}/{len(c)}"
        )
    if not (a.index.equals(b.index) and a.index.equals(c.index)):
        raise ValueError("series must share identical indexes")

    name_a = a.name or "leg_0"
    name_b = b.name or "leg_1"
    name_c = c.name or "leg_2"

    rho_ab = a.rolling(window, min_periods=window).corr(b)
    rho_ac = a.rolling(window, min_periods=window).corr(c)
    rho_bc = b.rolling(window, min_periods=window).corr(c)

    frame = pd.concat(
        [rho_ab, rho_ac, rho_bc],
        axis=1,
        keys=[
            f"{name_a}_vs_{name_b}",
            f"{name_a}_vs_{name_c}",
            f"{name_b}_vs_{name_c}",
        ],
    )
    frame.index.name = "date"
    return frame


def _longest_streak(flags: np.ndarray) -> int:
    """Length of the longest run of ``True`` in a 1-D boolean array."""
    longest = 0
    current = 0
    for flag in flags:
        if flag:
            current += 1
            if current > longest:
                longest = current
        else:
            current = 0
    return int(longest)


def summarize_pair(
    series: pd.Series,
    window: int,
    threshold: float = CANONICAL_HIGH_RHO_THRESHOLD,
    pair_name: str | None = None,
) -> PairwiseRollingStats:
    """Reduce a single pair's rolling-ρ series to a :class:`PairwiseRollingStats`."""
    clean = series.dropna()
    name = pair_name or str(series.name) or "pair"
    if clean.empty:
        return PairwiseRollingStats(
            pair=name,
            window=int(window),
            bars=0,
            mean=float("nan"),
            median=float("nan"),
            std=float("nan"),
            min=float("nan"),
            max=float("nan"),
            p25=float("nan"),
            p75=float("nan"),
            last=float("nan"),
            frac_above_threshold=0.0,
            threshold=float(threshold),
            longest_streak_above=0,
        )
    arr = clean.to_numpy(dtype=float)
    above = arr >= threshold
    return PairwiseRollingStats(
        pair=name,
        window=int(window),
        bars=int(len(clean)),
        mean=float(arr.mean()),
        median=float(np.median(arr)),
        std=float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
        min=float(arr.min()),
        max=float(arr.max()),
        p25=float(np.quantile(arr, 0.25)),
        p75=float(np.quantile(arr, 0.75)),
        last=float(arr[-1]),
        frac_above_threshold=float(above.mean()),
        threshold=float(threshold),
        longest_streak_above=_longest_streak(above),
    )


def find_high_correlation_regimes(
    rolling: pd.DataFrame,
    window: int,
    threshold: float = CANONICAL_HIGH_RHO_THRESHOLD,
    min_bars: int = 5,
) -> list[HighCorrelationRegime]:
    """Scan a 3-pair rolling frame for streaks where ALL pairs exceed ``threshold``.

    Parameters
    ----------
    rolling : pd.DataFrame
        Output of :func:`pairwise_rolling_correlations` (3 columns).
    window : int
        The lookback used to compute ``rolling`` (stored in the result).
    threshold : float
        High-ρ cutoff applied elementwise.
    min_bars : int
        Minimum streak length to qualify as a regime. Streaks below
        ``min_bars`` are dropped (too ephemeral to signal a regime).
    """
    if rolling.shape[1] != 3:
        raise ValueError(
            f"expected a 3-column pairwise rolling frame, got {rolling.shape[1]}"
        )
    clean = rolling.dropna()
    if clean.empty:
        return []
    col_ab, col_ac, col_bc = clean.columns
    flags = (
        (clean[col_ab] >= threshold)
        & (clean[col_ac] >= threshold)
        & (clean[col_bc] >= threshold)
    ).to_numpy()

    regimes: list[HighCorrelationRegime] = []
    i = 0
    n = len(flags)
    arr_ab = clean[col_ab].to_numpy()
    arr_ac = clean[col_ac].to_numpy()
    arr_bc = clean[col_bc].to_numpy()
    idx = clean.index
    while i < n:
        if not flags[i]:
            i += 1
            continue
        j = i
        while j < n and flags[j]:
            j += 1
        streak_len = j - i
        if streak_len >= min_bars:
            regimes.append(
                HighCorrelationRegime(
                    window=int(window),
                    threshold=float(threshold),
                    start=pd.Timestamp(idx[i]),
                    end=pd.Timestamp(idx[j - 1]),
                    bars=int(streak_len),
                    mean_rho_letf_qqq=float(arr_ab[i:j].mean()),
                    mean_rho_letf_gld=float(arr_ac[i:j].mean()),
                    mean_rho_qqq_gld=float(arr_bc[i:j].mean()),
                )
            )
        i = j
    return regimes


def compute_rolling_correlation_report(
    letf: pd.Series,
    qqq: pd.Series,
    gld: pd.Series,
    *,
    windows: Sequence[int] = CANONICAL_WINDOWS,
    threshold: float = CANONICAL_HIGH_RHO_THRESHOLD,
    min_regime_bars: int = 5,
    leg_names: tuple[str, str, str] = ("LETF", "QQQ", "GLD"),
) -> RollingCorrelationReport:
    """End-to-end: align, roll, summarize, detect regimes.

    The three pair labels in the returned stats follow ``leg_names``
    ordering: ``{L0}_vs_{L1}``, ``{L0}_vs_{L2}``, ``{L1}_vs_{L2}``.
    """
    a, b, c = align_returns_3(letf, qqq, gld)
    a = a.rename(leg_names[0])
    b = b.rename(leg_names[1])
    c = c.rename(leg_names[2])

    pair_stats: list[PairwiseRollingStats] = []
    regimes: list[HighCorrelationRegime] = []
    series_by_window: dict[int, pd.DataFrame] = {}
    for w in windows:
        rolling = pairwise_rolling_correlations(a, b, c, w)
        series_by_window[int(w)] = rolling
        for col in rolling.columns:
            pair_stats.append(summarize_pair(rolling[col], w, threshold, pair_name=col))
        regimes.extend(
            find_high_correlation_regimes(rolling, w, threshold, min_bars=min_regime_bars)
        )

    return RollingCorrelationReport(
        leg_names=tuple(leg_names),
        common_start=pd.Timestamp(a.index.min()),
        common_end=pd.Timestamp(a.index.max()),
        bars=int(len(a)),
        threshold=float(threshold),
        windows=tuple(int(w) for w in windows),
        pair_stats=tuple(pair_stats),
        regimes=tuple(regimes),
        series=series_by_window,
    )


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


_STATS_COLUMNS = (
    "pair",
    "window",
    "bars",
    "mean",
    "median",
    "std",
    "min",
    "p25",
    "p75",
    "max",
    "last",
    "frac≥thr",
    "streak≥thr",
)


def _stats_row_to_md(s: PairwiseRollingStats) -> list[str]:
    return [
        s.pair,
        str(int(s.window)),
        str(int(s.bars)),
        _fmt_num(s.mean, 3),
        _fmt_num(s.median, 3),
        _fmt_num(s.std, 3),
        _fmt_num(s.min, 3),
        _fmt_num(s.p25, 3),
        _fmt_num(s.p75, 3),
        _fmt_num(s.max, 3),
        _fmt_num(s.last, 3),
        _fmt_pct(s.frac_above_threshold, 1),
        str(int(s.longest_streak_above)),
    ]


def _regimes_table(regimes: Sequence[HighCorrelationRegime]) -> list[str]:
    if not regimes:
        return [
            "_No regime detected where all three pairs simultaneously exceed "
            "the high-ρ threshold for ≥ the minimum streak length._",
            "",
        ]
    cols = (
        "window",
        "start",
        "end",
        "bars",
        "ρ(LETF,QQQ)",
        "ρ(LETF,GLD)",
        "ρ(QQQ,GLD)",
    )
    out = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join("---" for _ in cols) + " |",
    ]
    for r in regimes:
        out.append(
            "| "
            + " | ".join(
                [
                    str(int(r.window)),
                    str(r.start.date()),
                    str(r.end.date()),
                    str(int(r.bars)),
                    _fmt_num(r.mean_rho_letf_qqq, 3),
                    _fmt_num(r.mean_rho_letf_gld, 3),
                    _fmt_num(r.mean_rho_qqq_gld, 3),
                ]
            )
            + " |"
        )
    out.append("")
    return out


def render_rolling_correlation_markdown(
    report: RollingCorrelationReport,
    title: str = "Rolling correlation — 3-leg portfolio [SWING BROKER]",
) -> str:
    """Emit the full Markdown report (header + stats table + regime table)."""
    parts: list[str] = [f"# {title}", ""]
    parts.append(
        f"Common window **{report.common_start.date()} → {report.common_end.date()}** "
        f"({report.bars} bars). High-ρ threshold = "
        f"**{report.threshold:.2f}**. Windows (bars): "
        + ", ".join(str(w) for w in report.windows)
        + "."
    )
    parts.append("")
    parts.append(
        "Legs: "
        + ", ".join(report.leg_names)
        + " (post-tax daily returns — 15% BR capital-gains baked in by upstream "
        "strategy simulators)."
    )
    parts.append("")

    # Stats table
    parts.append("## Pair-wise rolling ρ — summary statistics")
    parts.append("")
    header = "| " + " | ".join(_STATS_COLUMNS) + " |"
    sep = "| " + " | ".join("---" for _ in _STATS_COLUMNS) + " |"
    parts.append(header)
    parts.append(sep)
    for s in report.pair_stats:
        parts.append("| " + " | ".join(_stats_row_to_md(s)) + " |")
    parts.append("")

    # Regime table
    parts.append(
        "## High-ρ regimes (all three pairs simultaneously ≥ threshold)"
    )
    parts.append("")
    parts.extend(_regimes_table(report.regimes))

    return "\n".join(parts)
