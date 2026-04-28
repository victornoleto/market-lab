"""Scoring rubric for the long-term portfolio loop.

Mission shift (2026-04-28): rather than trying to advance iter 009
HAA+Gold by +0.10 Sharpe (apples-to-oranges due to gross/net mismatch),
this loop scores against the **average of SPY and VT 1× buy-and-hold**
per dataset — the user's literal "above-the-average" mandate.

All benchmarks below are **gross-of-tax** (no DARF applied), and the
gating below evaluates **gross** candidate metrics so the comparison
is apples-to-apples. Net-of-tax (Lei 14.754/2023, `_shared/tax_engine.py`)
is reported separately in `final_report.md` as a deploy-readiness
diagnostic — it does NOT change tier / winner status.

Datasets:
- ``lh_56y``     — VTSIM 56y synth (1970+); replaces the legacy ``educational``
                   key. Benchmark Sharpe values were always computed on this
                   56y window — the legacy iter 011 backtest sliced strategy
                   returns to 1995-2026 (31y) due to KMLMSIM inception, which
                   created an apples-to-oranges window mismatch. The new
                   ``datasets.py`` splice (FF MoM proxy pre-1988) lets
                   strategies actually run on the full 56y window.
- ``educational`` — DEPRECATED alias for ``lh_56y`` (same Benchmark values).
                   Kept so prior-iter results.json stay readable; new iters
                   should use ``lh_56y``.
- ``vt_real``    — VTSIM proxy 17y (2008-06+, real VT pending).
- ``ndx_real``   — QQQ Tiingo 16y (NDX-specific stretch test).

Citations
---------
* Winner criteria (strict) — `WINNER_AND_RANKING.md`
* DSR penalty with cumulative n_trials — `[advances_fin_ml, p.222-223]`
* PBO grid-level — `[advances_fin_ml, p.208-211]`
* Bootstrap CI — `[advances_fin_ml, p.196-202]`
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Benchmark — single named buy-and-hold reference (gross-of-tax)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Benchmark:
    sharpe: float
    cagr: float
    mdd: float
    label: str


# ---------------------------------------------------------------------------
# Per-dataset benchmarks: SPY (US-only) AND VT (global) where applicable.
#
# Numbers sourced from:
#   - educational: global_factor_tilt_loop scoring.py (VTSIM 56y synth) +
#                  strategy_hunt_loop scoring.py (SPYSIM 40y synth, conservative
#                  proxy for the longer 56y window)
#   - vt_real:     global_factor_tilt_loop scoring.py (VTSIM proxy 17y) +
#                  strategy_hunt_loop scoring.py (SPY Tiingo 17y)
#   - ndx_real:    global_factor_tilt_loop scoring.py (QQQ 16y) +
#                  strategy_hunt_loop scoring.py (SPY Tiingo 16y)
#
# All values are GROSS-of-tax. Net-of-tax (Lei 14.754) drag is roughly
# −0.10 Sharpe / −2pp CAGR for the equity series; documented per
# strategy_hunt_loop FINAL_REPORT.md "Post-tax results" §.
# ---------------------------------------------------------------------------


_LH_56Y_BENCHMARKS = {
    "vt":  Benchmark(sharpe=0.6626, cagr=0.0999, mdd=0.5835,
                    label="VTSIM b&h 56y synth (gross)"),
    "spy": Benchmark(sharpe=0.6800, cagr=0.1147, mdd=0.5514,
                    label="SPYSIM b&h 40y synth (gross)"),
}


BENCHMARKS: dict[str, dict[str, Benchmark]] = {
    "lh_56y": _LH_56Y_BENCHMARKS,
    "educational": _LH_56Y_BENCHMARKS,  # deprecated alias for lh_56y
    "vt_real": {
        "vt":  Benchmark(sharpe=0.5132, cagr=0.0880, mdd=0.5021,
                        label="VTSIM proxy 17y (gross; VT live pending)"),
        "spy": Benchmark(sharpe=0.9000, cagr=0.1497, mdd=0.3370,
                        label="SPY b&h Tiingo 17y (gross)"),
    },
    "ndx_real": {
        "qqq": Benchmark(sharpe=0.9472, cagr=0.1899, mdd=0.3512,
                        label="QQQ b&h Tiingo 16y (gross)"),
        "spy": Benchmark(sharpe=0.9000, cagr=0.1497, mdd=0.3370,
                        label="SPY b&h Tiingo 16y (gross, ndx_real-aligned)"),
    },
}


def avg_benchmark(dataset_benchmarks: dict[str, Benchmark]) -> Benchmark:
    """Synthetic 'avg of SPY and VT (and QQQ)' per dataset.

    Sharpe and CAGR averaged; MDD takes the worst (most permissive ceiling).
    This is the threshold the candidate must beat by ≥0.10 Sharpe.
    """
    bms = list(dataset_benchmarks.values())
    n = len(bms)
    return Benchmark(
        sharpe=sum(b.sharpe for b in bms) / n,
        cagr=sum(b.cagr for b in bms) / n,
        mdd=max(b.mdd for b in bms),
        label=f"AVG of {n}: " + " + ".join(b.label for b in bms),
    )


def primary_benchmarks() -> dict[str, Benchmark]:
    """Per-dataset primary benchmark = avg of SPY/VT/QQQ.

    Used internally by score_strategy. Override via the ``benchmarks`` arg
    to score_strategy when testing alternative thresholds.
    """
    return {ds: avg_benchmark(BENCHMARKS[ds]) for ds in BENCHMARKS}


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------


@dataclass
class DatasetMetrics:
    """Candidate's per-dataset metrics (GROSS-of-tax for gating).

    ``net_*`` fields are optional and reported in final_report.md only.
    They do NOT influence score / tier — kept here so the loop can persist
    them in verdict.json for deploy-readiness analysis.
    """
    sharpe: float
    cagr: float
    mdd: float
    dsr_p_value: Optional[float] = None
    # Optional net-of-tax metrics (Lei 14.754, AnnualDarfEngine).
    net_sharpe: Optional[float] = None
    net_cagr: Optional[float] = None
    net_mdd: Optional[float] = None


@dataclass
class Gates:
    """7-gate battery per dataset."""
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


GATE_THRESHOLDS = {
    "lh_56y": 5,
    "educational": 5,  # deprecated alias for lh_56y
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
    raw_benchmarks: dict = field(default_factory=dict)
    cumulative_n_trials: int = 0

    def to_dict(self) -> dict:
        return {
            "total_score": self.total_score,
            "tier": self.tier.value,
            "winner_conditions_met": self.winner_conditions_met,
            "criteria": self.criteria,
            "metrics_used": self.metrics_used,
            "benchmarks_used": self.benchmarks_used,
            "raw_benchmarks": self.raw_benchmarks,
            "cumulative_n_trials": self.cumulative_n_trials,
        }


def score_strategy(
    metrics: dict[str, DatasetMetrics],
    gates: dict[str, Gates],
    cumulative_n_trials: int,
    benchmarks: Optional[dict[str, Benchmark]] = None,
    robustness_bonus: int = 0,
) -> ScoreResult:
    """Score a strategy across 3 datasets (gross-of-tax).

    Rubric (total 100 + 5 bonus):

    1. **Sharpe edge** (25 pts) — beats ``avg(SPY, VT) + 0.10`` per dataset.
       avg = mean of named benchmarks per dataset (e.g. educational: avg of
       VTSIM and SPYSIM b&h).
    2. **Gate pass** (25 pts) — 7-gate battery per dataset + cross-dataset bonus.
    3. **DSR significance** (15 pts) — p-value with cumulative n_trials.
    4. **CAGR floor** (15 pts) — ≥ 0.8 × avg-benchmark CAGR per dataset.
    5. **MDD ceiling** (15 pts) — ≤ avg-benchmark MDD + 5pp per dataset.
    6. **Robustness bonus** (5 pts) — when caller provides rolling-window stat.

    Score is clamped to [0, 100]. Tier WINNER requires ALL 5 strict
    conditions (see ``_check_winner_conditions``).
    """
    bm = benchmarks or primary_benchmarks()
    datasets = list(metrics.keys())  # infer from caller; supports both lh_56y and legacy educational

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
    worst_p = max(p_values) if p_values else 1.0
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

    # --- 6. Robustness bonus (5 pts) -----------------------------------
    c6_pts = max(0, min(5, robustness_bonus))

    total = c1_pts + c2_pts + c3_pts + c4_pts + c5_pts + c6_pts
    total = max(0, min(100, total))

    winner_conds = _check_winner_conditions(
        metrics, gates, bm, worst_p, datasets_beat_sharpe,
        cagr_per_dataset, mdd_per_dataset,
    )
    tier = tier_from_score(total, winner_conditions_met=winner_conds)

    criteria_detail = {
        "1_sharpe_edge": {
            "points": c1_pts,
            "max": 25,
            "datasets_beat": datasets_beat_sharpe,
            "required_minimum_dataset_count": 2,
            "note": "Sharpe edge measured vs avg(SPY, VT) per dataset (gross).",
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
        raw_benchmarks={
            ds: {name: asdict(b) for name, b in BENCHMARKS[ds].items()}
            for ds in datasets
        },
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
    """Strict 5/5 winner conditions per WINNER_AND_RANKING.md."""
    if datasets_beat_sharpe < 2:
        return False
    # Iterate gates per dataset present in the caller's metrics, looking up
    # threshold from GATE_THRESHOLDS (which has both lh_56y and educational).
    for ds in metrics.keys():
        threshold = GATE_THRESHOLDS.get(ds)
        if threshold is None:
            continue
        if gates[ds].n_passed < threshold:
            return False
    if worst_p >= 0.05:
        return False
    if sum(cagr_per_dataset.values()) < 2:
        return False
    if sum(mdd_per_dataset.values()) < 2:
        return False
    return True
