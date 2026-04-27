"""Scoring rubric for the global factor-tilt hunt loop.

Produces a 0-100 score + tier classification for every tested strategy.
Same (metrics, gates, cumulative_n_trials) → same score always, so
iterations can be ranked across sessions.

Tier ``WINNER`` is reserved for strategies that satisfy ALL 5 strict
conditions in `WINNER_AND_RANKING.md` — the score alone cannot claim
it. This keeps the strict pass test honest while letting the score
rank everything else.

Datasets (3): vt_real (VTSIM proxy 17y), educational (VTSIM 56y),
ndx_real (QQQ 16y, carryover from strategy_hunt_loop as stretch test).

Usage
-----

::

    from scoring import score_strategy, Gates, DatasetMetrics

    metrics = {
        "educational": DatasetMetrics(sharpe=0.8, cagr=0.13, mdd=0.5, dsr_p_value=0.03),
        "vt_real":     DatasetMetrics(sharpe=0.7, cagr=0.11, mdd=0.45, dsr_p_value=0.02),
        "ndx_real":    DatasetMetrics(sharpe=1.1, cagr=0.22, mdd=0.34, dsr_p_value=0.01),
    }
    gates = {
        "educational": Gates(...),
        "vt_real":     Gates(...),
        "ndx_real":    Gates(...),
    }
    result = score_strategy(metrics, gates, cumulative_n_trials=5000)
    print(result.tier, result.total_score)

Citations
---------
* Winner criteria (strict) — `studies/global_factor_tilt_loop/WINNER_AND_RANKING.md`
* DSR penalty with cumulative n_trials — `[advances_fin_ml, p.222-223]`
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Benchmarks (computed 2026-04-26)
#
# educational: VTSIM 1970-01 → 2026-04 (56y), testfolio synth.
# vt_real:     VTSIM truncated 2008-06 → 2026-04 (~17y) as proxy for VT
#              live (Tiingo VT.parquet not yet pulled — TODO refresh once
#              VT pulled and re-measure).
# ndx_real:    QQQ Tiingo 2010-02 → 2026-04 (16y), carryover from
#              strategy_hunt_loop as global-vs-US-tech stretch test.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Benchmark:
    """Risk-adjusted baseline for one dataset."""

    sharpe: float
    cagr: float
    mdd: float  # positive magnitude
    label: str


BENCHMARKS: dict[str, Benchmark] = {
    "educational": Benchmark(sharpe=0.6626, cagr=0.0999, mdd=0.5835,
                              label="VTSIM b&h (56y synth)"),
    "vt_real":     Benchmark(sharpe=0.5132, cagr=0.0880, mdd=0.5021,
                              label="VTSIM proxy 2008-06+ (~17y; VT live pending)"),
    "ndx_real":    Benchmark(sharpe=0.9472, cagr=0.1899, mdd=0.3512,
                              label="QQQ b&h Tiingo (16y)"),
}


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------


@dataclass
class DatasetMetrics:
    """Per-dataset summary metrics for a candidate strategy."""

    sharpe: float
    cagr: float
    mdd: float                      # positive magnitude
    dsr_p_value: Optional[float] = None  # None = not computed


@dataclass
class Gates:
    """7-gate battery outcome for one dataset."""

    g1_pbo: bool
    g2_dsr: bool
    g3_wf: bool
    g4_oos: bool
    g5_fwd: bool
    g6_bootstrap: bool
    g7_crosslib: bool

    @property
    def n_passed(self) -> int:
        return sum([
            self.g1_pbo, self.g2_dsr, self.g3_wf, self.g4_oos,
            self.g5_fwd, self.g6_bootstrap, self.g7_crosslib,
        ])


# ---------------------------------------------------------------------------
# Tiers
# ---------------------------------------------------------------------------


class Tier(str, Enum):
    WINNER = "WINNER"
    STRONG = "STRONG"
    PROMISING = "PROMISING"
    MARGINAL = "MARGINAL"
    NEAR_FAIL = "NEAR_FAIL"
    FAIL = "FAIL"


def tier_from_score(score: int, *, winner_conditions_met: bool) -> Tier:
    """Map integer score → tier.

    WINNER is reserved for strategies that simultaneously (a) score ≥ 90
    AND (b) satisfy all 5 strict winner conditions. Without (b), even a
    perfect score caps at STRONG.
    """
    if winner_conditions_met and score >= 90:
        return Tier.WINNER
    if score >= 75:
        return Tier.STRONG
    if score >= 60:
        return Tier.PROMISING
    if score >= 40:
        return Tier.MARGINAL
    if score >= 20:
        return Tier.NEAR_FAIL
    return Tier.FAIL


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


# Minimum-gate thresholds per spec §0 for winner status.
GATE_THRESHOLDS = {
    "educational": 5,
    "vt_real": 4,
    "ndx_real": 4,
}


@dataclass
class ScoreResult:
    total_score: int
    tier: Tier
    winner_conditions_met: bool
    criteria: dict = field(default_factory=dict)
    metrics_used: dict = field(default_factory=dict)
    benchmarks_used: dict = field(default_factory=dict)
    cumulative_n_trials: int = 0

    def to_dict(self) -> dict:
        d = {
            "total_score": self.total_score,
            "tier": self.tier.value,
            "winner_conditions_met": self.winner_conditions_met,
            "criteria": self.criteria,
            "metrics_used": self.metrics_used,
            "benchmarks_used": self.benchmarks_used,
            "cumulative_n_trials": self.cumulative_n_trials,
        }
        return d


def score_strategy(
    metrics: dict[str, DatasetMetrics],
    gates: dict[str, Gates],
    cumulative_n_trials: int,
    benchmarks: Optional[dict[str, Benchmark]] = None,
) -> ScoreResult:
    """Score a strategy across 3 datasets.

    Rubric (total 100 + 5 bonus):

    1. **Sharpe edge** (25 pts) — beats ``benchmark + 0.10`` per dataset.
    2. **Gate pass** (25 pts) — 7-gate battery per dataset + cross-dataset bonus.
    3. **DSR significance** (15 pts) — p-value with cumulative n_trials.
    4. **CAGR floor** (15 pts) — ≥ 0.8 × benchmark CAGR per dataset.
    5. **MDD ceiling** (15 pts) — ≤ benchmark MDD + 5 pp per dataset.
    6. **Robustness bonus** (5 pts) — when available (caller-provided).

    Score is clamped to [0, 100]. Tier is derived including the strict
    winner-conditions check: ALL 5 criteria (same as
    `WINNER_AND_RANKING.md`) must be met for tier = WINNER.
    """
    bm = benchmarks or BENCHMARKS
    datasets = ["educational", "vt_real", "ndx_real"]

    # --- 1. Sharpe edge (25 pts) ---------------------------------------
    datasets_beat_sharpe = sum(
        1 for ds in datasets
        if metrics[ds].sharpe >= bm[ds].sharpe + 0.10
    )
    c1_pts = 0
    if datasets_beat_sharpe >= 1:
        c1_pts += 10
    if datasets_beat_sharpe >= 2:
        c1_pts += 10
    if datasets_beat_sharpe >= 3:
        c1_pts += 5

    # --- 2. Gate passes (25 pts) ---------------------------------------
    c2_pts = 0
    per_dataset_gates: dict[str, int] = {}
    for ds in datasets:
        n = gates[ds].n_passed
        per_dataset_gates[ds] = n
        threshold = GATE_THRESHOLDS[ds]
        if n >= 7:
            c2_pts += 7
        elif n >= threshold + 1:
            c2_pts += 5
        elif n >= threshold:
            c2_pts += 3
        elif n >= threshold - 1:
            c2_pts += 1
    cross_ds_met = all(
        per_dataset_gates[ds] >= GATE_THRESHOLDS[ds]
        for ds in datasets
    )
    if cross_ds_met:
        c2_pts += 4
    c2_pts = min(25, c2_pts)

    # --- 3. DSR with cumulative n_trials (15 pts) ----------------------
    p_values = [metrics[ds].dsr_p_value for ds in datasets
                if metrics[ds].dsr_p_value is not None]
    if p_values:
        worst_p = max(p_values)
    else:
        worst_p = 1.0
    if worst_p < 0.05:
        c3_pts = 15
    elif worst_p < 0.10:
        c3_pts = 10
    elif worst_p < 0.20:
        c3_pts = 5
    else:
        c3_pts = 0

    # --- 4. CAGR floor (15 pts) ----------------------------------------
    c4_pts = 0
    cagr_per_dataset: dict[str, bool] = {}
    for ds in datasets:
        floor = bm[ds].cagr * 0.8
        passed = metrics[ds].cagr >= floor
        cagr_per_dataset[ds] = passed
        if passed:
            c4_pts += 5

    # --- 5. MDD ceiling (15 pts) ---------------------------------------
    c5_pts = 0
    mdd_per_dataset: dict[str, bool] = {}
    for ds in datasets:
        ceiling = bm[ds].mdd + 0.05
        passed = metrics[ds].mdd <= ceiling
        mdd_per_dataset[ds] = passed
        if passed:
            c5_pts += 5

    # --- 6. Robustness bonus (5 pts, currently 0 without caller data) --
    c6_pts = 0

    total = c1_pts + c2_pts + c3_pts + c4_pts + c5_pts + c6_pts
    total = max(0, min(100, total))

    winner_conds = _check_winner_conditions(
        metrics, gates, bm, worst_p, datasets_beat_sharpe, cagr_per_dataset, mdd_per_dataset,
    )
    tier = tier_from_score(total, winner_conditions_met=winner_conds)

    criteria_detail = {
        "1_sharpe_edge": {
            "points": c1_pts,
            "max": 25,
            "datasets_beat": datasets_beat_sharpe,
            "required_minimum_dataset_count": 2,
        },
        "2_gates": {
            "points": c2_pts,
            "max": 25,
            "per_dataset": per_dataset_gates,
            "thresholds": GATE_THRESHOLDS,
            "cross_dataset_thresholds_met": cross_ds_met,
        },
        "3_dsr": {
            "points": c3_pts,
            "max": 15,
            "worst_p_value": worst_p,
            "cumulative_n_trials": cumulative_n_trials,
        },
        "4_cagr_floor": {
            "points": c4_pts,
            "max": 15,
            "per_dataset": cagr_per_dataset,
        },
        "5_mdd_ceiling": {
            "points": c5_pts,
            "max": 15,
            "per_dataset": mdd_per_dataset,
        },
        "6_robustness_bonus": {
            "points": c6_pts,
            "max": 5,
            "note": "Populated by caller if rolling-window data provided",
        },
    }

    return ScoreResult(
        total_score=total,
        tier=tier,
        winner_conditions_met=winner_conds,
        criteria=criteria_detail,
        metrics_used={ds: asdict(metrics[ds]) for ds in datasets},
        benchmarks_used={ds: asdict(bm[ds]) for ds in datasets},
        cumulative_n_trials=cumulative_n_trials,
    )


def _check_winner_conditions(
    metrics: dict[str, DatasetMetrics],
    gates: dict[str, Gates],
    bm: dict[str, Benchmark],
    worst_p: float,
    datasets_beat_sharpe: int,
    cagr_per_dataset: dict[str, bool],
    mdd_per_dataset: dict[str, bool],
) -> bool:
    """Strict check — all 5 conditions of WINNER_AND_RANKING.md hold."""
    if datasets_beat_sharpe < 2:
        return False
    for ds, th in GATE_THRESHOLDS.items():
        if gates[ds].n_passed < th:
            return False
    if worst_p >= 0.05:
        return False
    if sum(cagr_per_dataset.values()) < 2:
        return False
    if sum(mdd_per_dataset.values()) < 2:
        return False
    return True
