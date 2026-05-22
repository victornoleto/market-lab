"""Rolling-window scoring framework for studies.lrs.

The canonical evaluator for every strategy in the lrs study. Public entry
point: :func:`score_strategy`, which takes a strategy equity curve and a
benchmark equity curve and returns a :class:`ScoreReport` with:

* the **final score** (single number in roughly ``(-1, +1)``),
* per-window-length aggregates (mean / p25 / median / min / outperformance rate),
* the raw per-window scores for plotting.

Methodology
-----------

For each rolling window length L ∈ {1, 3, 5, 10, 15, 20} years, sample
overlapping windows with a monthly step (~21 trading days). Inside each
window, renormalise both strategy and benchmark to 1.0 at the window
start and compute four signed excess components:

* ``terminal_excess``    = strategy_end / benchmark_end − 1   (signed wealth excess)
* ``time_above_excess``  = 2·(fraction of bars where strategy > benchmark) − 1
* ``sortino_excess``     = Sortino(strategy) − Sortino(benchmark)
* ``calmar_excess``      = Calmar(strategy)  − Calmar(benchmark)

The window score is a weighted tanh-squashed composite (``time_above`` is
already bounded so no squash):

```
window_score = 0.40·tanh(terminal_excess)
             + 0.25·time_above_excess
             + 0.20·tanh(sortino_excess)
             + 0.15·tanh(calmar_excess)
```

Per-length aggregate: ``length_score = 0.60·mean + 0.40·p25`` — rewards
typical performance while penalising the worst quartile of regimes.

Final score: weighted across lengths with ``HORIZON_WEIGHTS``. Long
windows dominate (~70% combined) but short windows still inform the
picture.

Implementation notes
--------------------
Per-window metrics are computed by the cumulative-log-sum trick from
``studies/static_spy_beater_portfolio/scripts/score_portfolio.py``:
pre-compute log/linear cumulative sums once, then evaluate every window
in O(n_starts) instead of O(n_starts · window_length).

Citations
---------
* Vectorized rolling-metric approach:
  ``studies/static_spy_beater_portfolio/scripts/score_portfolio.py::_rolling_metrics_from_cumulatives``
  (precedent in this codebase).
* ``time_above_benchmark`` formula: lifted from
  ``studies/letf_rotation_hunt/core/plot_helper.py::plot_winner_vs_benchmark``
  (``(ratio > 1.0).mean()``).
* Sortino over Sharpe — only downside volatility penalised
  ``[advances_fin_ml, p.41-43]``; standard tradition since Sortino &
  Price (1994).
* Calmar (CAGR / |MDD|) — Young (1991), used widely in trend-following
  evaluation ``[trend_following, ch.7]``.
* tanh squash on unbounded components: standard normalisation to keep
  a single outlier window from dominating the composite.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252

#: Trading-day counts for each window length we evaluate.
HORIZON_DAYS: dict[int, int] = {
    1: 1 * TRADING_DAYS_PER_YEAR,
    3: 3 * TRADING_DAYS_PER_YEAR,
    5: 5 * TRADING_DAYS_PER_YEAR,
    10: 10 * TRADING_DAYS_PER_YEAR,
    15: 15 * TRADING_DAYS_PER_YEAR,
    20: 20 * TRADING_DAYS_PER_YEAR,
}

#: Final-score weights across window lengths. Sums to 1.0. Longer windows
#: dominate (~70% combined) — they're the most informative for a
#: long-horizon allocator — but short windows still inform the score.
HORIZON_WEIGHTS: dict[int, float] = {
    1: 0.05,
    3: 0.10,
    5: 0.15,
    10: 0.20,
    15: 0.25,
    20: 0.25,
}

#: Within-window composite weights. Sum to 1.0. Order: terminal_ratio
#: (primary), time_above (consistency), sortino (risk-adjusted),
#: calmar (drawdown context, discounted because LETFs always look bad).
COMPONENT_WEIGHTS: dict[str, float] = {
    "terminal": 0.40,
    "time_above": 0.25,
    "sortino": 0.20,
    "calmar": 0.15,
}

#: Monthly step (~21 trading days) for rolling-window starts. Yields ~500
#: 5y windows over a 45-year span — dense enough to catch regime variation
#: without daily-step overkill.
DEFAULT_WINDOW_STEP_DAYS = 21


# ---------------------------------------------------------------------------
# Public dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WindowScore:
    """Score for a single rolling-window instance."""

    length_years: int
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    terminal_ratio: float          # strategy_end / benchmark_end (both renormalised to 1.0 at start)
    time_above_benchmark: float    # fraction of bars where ratio > 1.0
    sortino_strategy: float
    sortino_benchmark: float
    calmar_strategy: float
    calmar_benchmark: float
    score: float                   # composite, signed, roughly in (-1, +1)

    def to_dict(self) -> dict[str, object]:
        return {
            "length_years": self.length_years,
            "start_date": self.start_date.strftime("%Y-%m-%d"),
            "end_date": self.end_date.strftime("%Y-%m-%d"),
            "terminal_ratio": float(self.terminal_ratio),
            "time_above_benchmark": float(self.time_above_benchmark),
            "sortino_strategy": float(self.sortino_strategy),
            "sortino_benchmark": float(self.sortino_benchmark),
            "calmar_strategy": float(self.calmar_strategy),
            "calmar_benchmark": float(self.calmar_benchmark),
            "score": float(self.score),
        }


@dataclass(frozen=True)
class LengthAggregate:
    """Aggregate of every window of one length."""

    length_years: int
    n_windows: int
    pct_outperforming: float       # fraction of windows where score > 0
    mean_score: float
    p25_score: float
    median_score: float
    min_score: float
    length_score: float            # 0.60·mean + 0.40·p25

    def to_dict(self) -> dict[str, float | int]:
        return {
            "length_years": self.length_years,
            "n_windows": int(self.n_windows),
            "pct_outperforming": float(self.pct_outperforming),
            "mean_score": float(self.mean_score),
            "p25_score": float(self.p25_score),
            "median_score": float(self.median_score),
            "min_score": float(self.min_score),
            "length_score": float(self.length_score),
        }


@dataclass(frozen=True)
class ScoreReport:
    """Complete scoring of one (strategy, tax_scenario) pair."""

    strategy_name: str
    tax_scenario: str              # "tax_free" or "br_lei_14754"
    final_score: float
    per_length: dict[int, LengthAggregate]
    windows: list[WindowScore] = field(default_factory=list)

    def summary_dict(self) -> dict[str, object]:
        """Compact dict for JSON serialisation (excludes raw windows)."""
        return {
            "strategy_name": self.strategy_name,
            "tax_scenario": self.tax_scenario,
            "final_score": float(self.final_score),
            "per_length": {str(k): v.to_dict() for k, v in self.per_length.items()},
        }


# ---------------------------------------------------------------------------
# Internal helpers (vectorized rolling-window math)
# ---------------------------------------------------------------------------


def _rolling_starts(n_rows: int, days: int, step: int) -> np.ndarray:
    """Indices at which a window of ``days`` bars can start with a ``step`` cadence.

    Always includes the latest possible start so we don't drop the most
    recent window.
    """
    last_start = n_rows - days - 1   # need one bar of returns after the last index
    if last_start < 0:
        return np.empty(0, dtype=int)
    starts = np.arange(0, last_start + 1, step, dtype=int)
    if starts.size == 0 or starts[-1] != last_start:
        starts = np.append(starts, np.array([last_start], dtype=int))
    return starts


def _series_cumulatives(returns: np.ndarray) -> dict[str, np.ndarray]:
    """Pre-cumulate per-series arrays once so per-window scoring is O(n_starts).

    All cumulatives are length ``n+1`` so window sums become
    ``cum[end] - cum[start]`` with ``end = start + days``.
    """
    logs = np.log1p(returns)
    neg = np.where(returns < 0.0, returns, 0.0)
    neg_sq = np.where(returns < 0.0, returns * returns, 0.0)
    return {
        "log_cum": np.concatenate([[0.0], np.cumsum(logs)]),
        "neg_sumsq_cum": np.concatenate([[0.0], np.cumsum(neg_sq)]),
        "neg_count_cum": np.concatenate([[0.0], np.cumsum((returns < 0.0).astype(float))]),
        "ret_sum_cum": np.concatenate([[0.0], np.cumsum(returns)]),
        "ret_sumsq_cum": np.concatenate([[0.0], np.cumsum(returns * returns)]),
    }


def _max_drawdowns(log_cum: np.ndarray, starts: np.ndarray, days: int) -> np.ndarray:
    """Per-window max drawdown as a negative fraction (e.g. -0.35 = -35%).

    Cache-aware chunking keeps the temp 2D arrays close to L2.
    """
    n_starts = starts.shape[0]
    if n_starts == 0:
        return np.empty(0, dtype=float)
    # ~128KB working set per chunk
    chunk = max(8, min(4096, (128 * 1024) // max(1, 8 * (days + 1))))
    out = np.empty(n_starts, dtype=float)
    offsets = np.arange(days + 1, dtype=np.int64)
    for c0 in range(0, n_starts, chunk):
        sub = starts[c0 : c0 + chunk]
        window = log_cum[sub[:, None] + offsets[None, :]]
        window -= window[:, :1]
        body = window[:, 1:]
        running_max = np.maximum.accumulate(body, axis=1)
        body -= running_max
        out[c0 : c0 + sub.shape[0]] = np.expm1(body.min(axis=1))
    return out


def _sortino_calmar_cagr_terminal(
    cumulatives: dict[str, np.ndarray],
    starts: np.ndarray,
    days: int,
) -> dict[str, np.ndarray]:
    """Per-window Sortino, Calmar, CAGR and terminal-wealth multiple."""
    ends = starts + days
    log_total = cumulatives["log_cum"][ends] - cumulatives["log_cum"][starts]
    terminal = np.exp(log_total)
    years = days / TRADING_DAYS_PER_YEAR
    cagr = np.power(terminal, 1.0 / years) - 1.0

    sums = cumulatives["ret_sum_cum"][ends] - cumulatives["ret_sum_cum"][starts]
    mean = sums / days

    # Downside-only deviation: ``√(mean(min(r, 0)²))``. Counts every
    # non-negative bar as zero contribution to the denominator, matching
    # the Estrada-style convention used in
    # ``src/market_lab/backtest/metrics/performance.py::sortino``.
    neg_sumsq = cumulatives["neg_sumsq_cum"][ends] - cumulatives["neg_sumsq_cum"][starts]
    downside_dev = np.sqrt(neg_sumsq / days)
    sortino = np.divide(
        mean * math.sqrt(TRADING_DAYS_PER_YEAR),
        downside_dev,
        out=np.full_like(mean, np.nan),
        where=downside_dev > 0,
    )

    mdd = _max_drawdowns(cumulatives["log_cum"], starts, days)
    calmar = np.divide(cagr, np.abs(mdd), out=np.full_like(cagr, np.nan), where=mdd < 0)

    return {"terminal": terminal, "cagr": cagr, "sortino": sortino, "calmar": calmar, "mdd": mdd}


def _time_above_benchmark(
    diff_log_cum: np.ndarray,
    starts: np.ndarray,
    days: int,
) -> np.ndarray:
    """Per-window winning fraction (strategy renormalised > benchmark renormalised).

    Equivalences used:
        ratio(t) > 1   ⇔ diff_log_cum(t) > diff_log_cum(start)
        ratio(t) == 1  ⇔ diff_log_cum(t) == diff_log_cum(start)

    Ties contribute **half** to the winning fraction so that a strategy
    that perfectly tracks the benchmark gets ``time_above = 0.5`` rather
    than ``0.0``. This is the standard convention for head-to-head
    comparisons and makes the self-score of any series against itself
    contribute exactly 0 to the composite.
    """
    n_starts = starts.shape[0]
    if n_starts == 0:
        return np.empty(0, dtype=float)
    chunk = max(8, min(4096, (128 * 1024) // max(1, 8 * (days + 1))))
    out = np.empty(n_starts, dtype=float)
    body_offsets = np.arange(1, days + 1, dtype=np.int64)
    for c0 in range(0, n_starts, chunk):
        sub = starts[c0 : c0 + chunk]
        body = diff_log_cum[sub[:, None] + body_offsets[None, :]]
        thresh = diff_log_cum[sub][:, None]
        above = (body > thresh).mean(axis=1)
        ties = (body == thresh).mean(axis=1)
        out[c0 : c0 + sub.shape[0]] = above + 0.5 * ties
    return out


def _tanh_or_zero(x: float) -> float:
    """tanh(x), but NaN-safe (returns 0.0 for NaN — neither rewards nor penalises)."""
    return 0.0 if not np.isfinite(x) else float(np.tanh(x))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def score_strategy(
    strategy_equity: pd.Series,
    benchmark_equity: pd.Series,
    *,
    strategy_name: str,
    tax_scenario: str,
    window_years: Iterable[int] = (1, 3, 5, 10, 15, 20),
    window_step_days: int = DEFAULT_WINDOW_STEP_DAYS,
    length_weights: dict[int, float] | None = None,
    component_weights: dict[str, float] | None = None,
) -> ScoreReport:
    """Score one strategy curve against a benchmark curve.

    Parameters
    ----------
    strategy_equity, benchmark_equity : pd.Series
        Equity curves indexed by date. Both must cover the same (or
        overlapping) span; the intersection of indices defines the
        scorable region. The caller is responsible for any pre-tax /
        post-tax choice — this function is policy-agnostic.
    strategy_name, tax_scenario : str
        Labels carried in the returned report (e.g. ``"LRS-SSO"``,
        ``"br_lei_14754"``).
    window_years : iterable of int
        Lengths to score, in years. Defaults to the lrs canonical
        ``(1, 3, 5, 10, 15, 20)``.
    window_step_days : int
        Step (in trading days) between consecutive rolling-window starts.
        Default ~21 (monthly).
    length_weights, component_weights : dict, optional
        Overrides for the across-length and within-window weights.
        Defaults: :data:`HORIZON_WEIGHTS` and :data:`COMPONENT_WEIGHTS`.

    Returns
    -------
    ScoreReport
        Final weighted score plus per-length aggregates plus the raw
        per-window scores (for plotting / diagnostics).
    """
    if length_weights is None:
        length_weights = HORIZON_WEIGHTS
    if component_weights is None:
        component_weights = COMPONENT_WEIGHTS

    common = strategy_equity.index.intersection(benchmark_equity.index)
    if len(common) < 2:
        raise ValueError("strategy and benchmark curves have <2 overlapping bars")
    strat = strategy_equity.reindex(common).astype(float)
    bench = benchmark_equity.reindex(common).astype(float)

    strat_ret = strat.pct_change().fillna(0.0).to_numpy()
    bench_ret = bench.pct_change().fillna(0.0).to_numpy()

    strat_cum = _series_cumulatives(strat_ret)
    bench_cum = _series_cumulatives(bench_ret)
    diff_log_cum = strat_cum["log_cum"] - bench_cum["log_cum"]

    per_length: dict[int, LengthAggregate] = {}
    all_windows: list[WindowScore] = []

    for years in window_years:
        days = HORIZON_DAYS.get(years, years * TRADING_DAYS_PER_YEAR)
        starts = _rolling_starts(len(common), days, window_step_days)
        if starts.size == 0:
            continue

        strat_m = _sortino_calmar_cagr_terminal(strat_cum, starts, days)
        bench_m = _sortino_calmar_cagr_terminal(bench_cum, starts, days)
        time_above = _time_above_benchmark(diff_log_cum, starts, days)

        terminal_ratio = strat_m["terminal"] / bench_m["terminal"]
        terminal_excess = terminal_ratio - 1.0
        time_above_excess = 2.0 * (time_above - 0.5)         # already in [-1, 1]
        sortino_excess = strat_m["sortino"] - bench_m["sortino"]
        calmar_excess = strat_m["calmar"] - bench_m["calmar"]

        scores = np.empty(starts.size, dtype=float)
        window_records: list[WindowScore] = []
        ends = starts + days
        for j in range(starts.size):
            s = (
                component_weights["terminal"] * _tanh_or_zero(terminal_excess[j])
                + component_weights["time_above"] * float(time_above_excess[j])
                + component_weights["sortino"] * _tanh_or_zero(sortino_excess[j])
                + component_weights["calmar"] * _tanh_or_zero(calmar_excess[j])
            )
            scores[j] = s
            window_records.append(WindowScore(
                length_years=int(years),
                start_date=common[int(starts[j])],
                end_date=common[int(ends[j])],
                terminal_ratio=float(terminal_ratio[j]),
                time_above_benchmark=float(time_above[j]),
                sortino_strategy=float(strat_m["sortino"][j]),
                sortino_benchmark=float(bench_m["sortino"][j]),
                calmar_strategy=float(strat_m["calmar"][j]),
                calmar_benchmark=float(bench_m["calmar"][j]),
                score=float(s),
            ))

        mean = float(np.nanmean(scores))
        p25 = float(np.nanpercentile(scores, 25))
        median = float(np.nanmedian(scores))
        mn = float(np.nanmin(scores))
        length_score = 0.60 * mean + 0.40 * p25
        per_length[int(years)] = LengthAggregate(
            length_years=int(years),
            n_windows=int(starts.size),
            pct_outperforming=float((scores > 0).mean()),
            mean_score=mean,
            p25_score=p25,
            median_score=median,
            min_score=mn,
            length_score=length_score,
        )
        all_windows.extend(window_records)

    # Weighted final score across lengths. Skip horizons we couldn't score
    # (too short for the window) and renormalise the remaining weights so
    # the score stays interpretable on shorter datasets.
    weighted = 0.0
    weight_sum = 0.0
    for years, agg in per_length.items():
        w = length_weights.get(years, 0.0)
        if w <= 0.0 or not np.isfinite(agg.length_score):
            continue
        weighted += w * agg.length_score
        weight_sum += w
    final = weighted / weight_sum if weight_sum > 0 else float("nan")

    return ScoreReport(
        strategy_name=strategy_name,
        tax_scenario=tax_scenario,
        final_score=float(final),
        per_length=per_length,
        windows=all_windows,
    )
