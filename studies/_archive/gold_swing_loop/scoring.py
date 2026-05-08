"""Scoring rubric for the GOLD SWING loop (XAUUSD day/swing).

Produces a 0-100 score + tier classification for every tested strategy.
Same (metrics, gates, cumulative_n_trials) → same score always, so
iterations can be ranked across sessions.

Tier ``WINNER`` is reserved for strategies that satisfy ALL 5 strict
conditions in `WINNER_AND_RANKING.md` — the score alone cannot claim
it. The 6th condition (mean hold ≤ 5 days) is checked SEPARATELY by
the caller (not in this module).

This is a sibling of `studies/strategy_hunt_loop/scoring.py` with
gold-specific BENCHMARKS and dataset names. The scoring math is
identical.

Usage
-----

::

    from scoring import score_strategy, Gates, DatasetMetrics

    metrics = {
        "gld_long":        DatasetMetrics(sharpe=0.65, cagr=0.10, mdd=0.40, dsr_p_value=0.04),
        "xauusd_real":     DatasetMetrics(sharpe=1.05, cagr=0.16, mdd=0.20, dsr_p_value=0.03),
        "xauusd_intraday": DatasetMetrics(sharpe=1.10, cagr=0.16, mdd=0.20, dsr_p_value=0.03),
    }
    gates = {
        "gld_long":        Gates(...),
        "xauusd_real":     Gates(...),
        "xauusd_intraday": Gates(...),
    }
    result = score_strategy(metrics, gates, cumulative_n_trials=500)
    print(result.tier, result.total_score)

    # Hold-time gate (NEW vs sister loop) — checked separately by caller:
    hold_gate_pass = mean_hold_days <= 5.0
    is_winner = result.winner_conditions_met and hold_gate_pass

Citations
---------
* Winner criteria (strict) — `studies/gold_swing_loop/WINNER_AND_RANKING.md`
* DSR penalty with cumulative n_trials — `[advances_fin_ml, p.222-223]`
* Sister loop scoring API mirror — `../strategy_hunt_loop/scoring.py`
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Benchmarks (real data, measured 2026-04-24)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Benchmark:
    """Risk-adjusted baseline for one dataset."""

    sharpe: float
    cagr: float
    mdd: float  # positive magnitude
    label: str


# Empirically measured 2026-04-26 (iter 001) on Tiingo cache:
#   - GLD ETF daily 2004-11-18 → 2026-04-15 (5 384 bars, 21.40 y)
#   - XAUUSD spot daily 2020-01-02 → 2026-04-17 (1 700 bars, 6.29 y)
#   - XAUUSD spot 1h 2020-01-02 → 2026-04-17 (32 195 bars, 6.29 y, 5 119 bars/yr)
# Annualization: daily=252, 1h=5119 (empirical). Sharpe = mean/std × sqrt(N_bars/yr).
# CAGR = (P_T/P_0)^(1/years) − 1. MDD = max drawdown from peak (positive magnitude).
# See `iterations/001-2026-04-26-0151-connors-rsi2/run_benchmarks.py` for code.
BENCHMARKS: dict[str, Benchmark] = {
    "gld_long":        Benchmark(sharpe=0.6844, cagr=0.11318, mdd=0.4556,
                                  label="GLD ETF b&h 2004-11-18→2026-04-15 (21.40y, daily)"),
    "xauusd_real":     Benchmark(sharpe=1.0382, cagr=0.19928, mdd=0.2036,
                                  label="XAUUSD spot b&h 2020-01-02→2026-04-17 (6.29y, daily)"),
    "xauusd_intraday": Benchmark(sharpe=1.1028, cagr=0.20195, mdd=0.2442,
                                  label="XAUUSD spot b&h 2020-01-02→2026-04-17 (6.29y, 1h, 5119 bars/yr)"),
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
# gld_long is longest dataset → strictest threshold (mirrors sister loop's educational tier).
GATE_THRESHOLDS = {
    "gld_long": 5,
    "xauusd_real": 4,
    "xauusd_intraday": 4,
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
    datasets = ["gld_long", "xauusd_real", "xauusd_intraday"]

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
        # else 0
    # Cross-dataset bonus — all 3 meet or exceed spec §0 minimums.
    cross_ds_met = all(
        per_dataset_gates[ds] >= GATE_THRESHOLDS[ds]
        for ds in datasets
    )
    if cross_ds_met:
        c2_pts += 4
    c2_pts = min(25, c2_pts)

    # --- 3. DSR with cumulative n_trials (15 pts) ----------------------
    # Use the WORST (highest) p-value across datasets — conservative.
    # If any dataset's p is None, fall back to the best available.
    p_values = [metrics[ds].dsr_p_value for ds in datasets
                if metrics[ds].dsr_p_value is not None]
    if p_values:
        worst_p = max(p_values)
    else:
        worst_p = 1.0  # no DSR → treated as failing
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
    c6_pts = 0  # caller may compute + set later; placeholder 0

    # --- Total + tier --------------------------------------------------
    total = c1_pts + c2_pts + c3_pts + c4_pts + c5_pts + c6_pts
    total = max(0, min(100, total))

    # Strict winner check (same 5 conditions as WINNER_AND_RANKING.md).
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
    """Strict check — all 5 conditions of WINNER_AND_RANKING.md hold (v1, legacy)."""
    # 1. Sharpe edge on ≥ 2 datasets
    if datasets_beat_sharpe < 2:
        return False
    # 2. Gate cross-dataset: educational ≥5, spy ≥4, ndx ≥4
    for ds, th in GATE_THRESHOLDS.items():
        if gates[ds].n_passed < th:
            return False
    # 3. DSR p < 0.05 (using worst p)
    if worst_p >= 0.05:
        return False
    # 4. CAGR floor on ≥ 2 datasets
    if sum(cagr_per_dataset.values()) < 2:
        return False
    # 5. MDD ceiling on ≥ 2 datasets
    if sum(mdd_per_dataset.values()) < 2:
        return False
    return True


# ---------------------------------------------------------------------------
# v2 scoring (rules_version: 2026-04-26-relaxed-r1)
# ---------------------------------------------------------------------------
#
# Adds primary + corroborating dataset semantics. Use this from iter 016+.
# Iters 001-015 stay on v1 (their verdict.json files reference v1 schema).


GATE_THRESHOLDS_V2 = {
    "gld_long": 5,
    "xauusd_real": 4,
    "xauusd_intraday": 4,
    "gold_synth_40y": 5,  # placeholder until built
}


def score_strategy_v2(
    metrics: dict[str, DatasetMetrics],
    gates: dict[str, Gates],
    cumulative_n_trials: int,
    declared_primary: str,
    declared_corroborating: list[str],
    benchmarks: Optional[dict[str, Benchmark]] = None,
) -> ScoreResult:
    """Score under relaxed rules (2026-04-26 r1).

    primary: full Sharpe edge + full gate count + DSR<0.05 + CAGR floor + MDD ceiling
    corroborating (≥1 required): Sharpe>0 + G6_bootstrap + G2_DSR(p<0.20)

    Rubric (total 100 + 5 bonus):
    1. Sharpe edge (25 pts) — primary +0.10 = 20pts; each corroborating Sharpe>0 = 5pts (cap at 25)
    2. Gates (25 pts) — primary full count = 15pts; +5 if all corroborating pass relaxed; +5 cross-bonus if also legacy 3/3 met
    3. DSR significance (15 pts) — primary p
    4. CAGR floor (15 pts) — primary alone (full 15 pts if pass)
    5. MDD ceiling (15 pts) — primary alone (full 15 pts if pass)
    6. Robustness bonus (5 pts) — non-overlap subwindow, caller-set
    """
    bm = benchmarks or BENCHMARKS
    if declared_primary not in metrics:
        raise ValueError(f"declared_primary={declared_primary!r} not in metrics keys {list(metrics)}")
    if not declared_corroborating:
        raise ValueError("v2 requires ≥1 corroborating dataset")
    for ds in declared_corroborating:
        if ds not in metrics:
            raise ValueError(f"corroborating ds={ds!r} not in metrics")

    # --- 1. Sharpe edge (25 pts) ---------------------------------------
    primary_beat = (
        declared_primary in bm
        and metrics[declared_primary].sharpe >= bm[declared_primary].sharpe + 0.10
    )
    c1_pts = 20 if primary_beat else 0
    corr_pos = sum(1 for ds in declared_corroborating if metrics[ds].sharpe > 0)
    c1_pts += min(5, corr_pos * 5)
    c1_pts = min(25, c1_pts)

    # --- 2. Gates (25 pts) ---------------------------------------------
    primary_gate_th = GATE_THRESHOLDS_V2.get(declared_primary, 4)
    primary_gates_n = gates[declared_primary].n_passed
    c2_pts = 0
    if primary_gates_n >= primary_gate_th:
        c2_pts += 15
    elif primary_gates_n >= primary_gate_th - 1:
        c2_pts += 8
    # Corroborating: each ds passing G6 + G2 → +5 pts (max 5)
    corr_relaxed_pass = sum(
        1 for ds in declared_corroborating
        if gates[ds].g6_bootstrap and gates[ds].g2_dsr
    )
    if corr_relaxed_pass >= 1:
        c2_pts += 5
    # Legacy cross-bonus: if all 3 legacy datasets present and pass legacy thresholds
    legacy_ds = ["gld_long", "xauusd_real", "xauusd_intraday"]
    if all(ds in metrics for ds in legacy_ds):
        legacy_cross = all(gates[ds].n_passed >= GATE_THRESHOLDS[ds] for ds in legacy_ds)
        if legacy_cross:
            c2_pts += 5
    c2_pts = min(25, c2_pts)

    # --- 3. DSR (15 pts) — primary only --------------------------------
    primary_p = metrics[declared_primary].dsr_p_value
    if primary_p is None:
        c3_pts = 0
    elif primary_p < 0.05:
        c3_pts = 15
    elif primary_p < 0.10:
        c3_pts = 10
    elif primary_p < 0.20:
        c3_pts = 5
    else:
        c3_pts = 0

    # --- 4. CAGR floor (15 pts) — primary --------------------------------
    primary_cagr_pass = (
        declared_primary in bm
        and metrics[declared_primary].cagr >= bm[declared_primary].cagr * 0.8
    )
    c4_pts = 15 if primary_cagr_pass else 0

    # --- 5. MDD ceiling (15 pts) — primary --------------------------------
    primary_mdd_pass = (
        declared_primary in bm
        and metrics[declared_primary].mdd <= bm[declared_primary].mdd + 0.05
    )
    c5_pts = 15 if primary_mdd_pass else 0

    # --- 6. Robustness (5 pts, caller-set) -------------------------------
    c6_pts = 0

    total = c1_pts + c2_pts + c3_pts + c4_pts + c5_pts + c6_pts
    total = max(0, min(100, total))

    # Winner v2: primary passes 1+2+3+4+5; ≥1 corroborating passes relaxed gate.
    winner_conds = (
        primary_beat
        and primary_gates_n >= primary_gate_th
        and (primary_p is not None and primary_p < 0.05)
        and primary_cagr_pass
        and primary_mdd_pass
        and corr_relaxed_pass >= 1
    )
    tier = tier_from_score(total, winner_conditions_met=winner_conds)

    criteria_detail = {
        "rules_version": "2026-04-26-relaxed-r1",
        "declared_primary": declared_primary,
        "declared_corroborating": list(declared_corroborating),
        "1_sharpe_edge": {"points": c1_pts, "max": 25, "primary_beat": primary_beat, "corr_positive": corr_pos},
        "2_gates": {"points": c2_pts, "max": 25, "primary_gates": primary_gates_n, "primary_threshold": primary_gate_th, "corr_relaxed_pass": corr_relaxed_pass},
        "3_dsr": {"points": c3_pts, "max": 15, "primary_p": primary_p},
        "4_cagr_floor": {"points": c4_pts, "max": 15, "primary_pass": primary_cagr_pass},
        "5_mdd_ceiling": {"points": c5_pts, "max": 15, "primary_pass": primary_mdd_pass},
        "6_robustness": {"points": c6_pts, "max": 5},
    }

    return ScoreResult(
        total_score=total,
        tier=tier,
        winner_conditions_met=winner_conds,
        criteria=criteria_detail,
        metrics_used={ds: asdict(metrics[ds]) for ds in metrics},
        benchmarks_used={ds: asdict(bm[ds]) for ds in metrics if ds in bm},
        cumulative_n_trials=cumulative_n_trials,
    )
