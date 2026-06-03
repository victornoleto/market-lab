"""CAGR-anchored scoring for spy_beater_hunt.

Distinct from studies.return_stacked_core.scoring (which is Sharpe-edge
anchored). This rubric prioritises CAGR (30 pts) over Sharpe (10 pts) per
WINNER_AND_RANKING.md — opposite of long_term_portfolio.

WINNER conditions (3 strict bars, ALL must hold):
  - Bar 1: mean(CAGR) ≥ SPY mean (13.80%)
  - Bar 2: mean(MDD)  ≤ SPY mean (40.85%)
  - Bar 3: 7-gate battery passes ≥ threshold per dataset on ≥ 2/3 datasets

Total score = CAGR(30) + MDD(20) + Gates(20) + DSR(10) + Sharpe(10)
            + Robustness(10) + ExtraBonus(5) → clamped to [0, 100].

Tier WINNER requires score ≥ 90 AND all 3 bars met.

Citations:
  - [leverage_for_the_long_run, ch.3-4]: regime-gated leveraged equity
    rationale (the strategies this rubric evaluates).
  - [advances_fin_ml, p.208-211]: PBO; [p.222-223]: DSR; [p.196-202]:
    bootstrap CI; [p.31-34]: cross-lib. Same 7-gate battery as
    studies.return_stacked_core.
"""
from __future__ import annotations

from typing import Optional

from studies.return_stacked_core.scoring import (
    DatasetMetrics,
    GATE_THRESHOLDS,
    Gates,
    Tier,
)


# ---------------------------------------------------------------------------
# SPY 2-dataset benchmarks (lh_56y synth + spy_real Tiingo, 2026-04-29 refactor)
# ---------------------------------------------------------------------------
#
# Reframing rationale: vt_real (2008+) and ndx_real (2010+) had SPY MDD only
# 33.70% because the windows missed the 2007-09 GFC peak-to-trough -56%.
# That bull-biased MDD ceiling (40.85%) was artificially tight for a hunt
# whose mission is to beat SPY. The new 2-dataset setup uses:
#
#   - lh_56y    (1986+, ~40y synth via SPYSIM): SPY CAGR 11.47%, MDD 55.14%.
#   - spy_real  (2003+, ~22.7y Tiingo daily real): SPY CAGR 10.95%, MDD 55.20%.
#
# Both windows include the 2008 GFC peak-to-trough. The new bars are
# honest reflections of "beat SPY" — strategies must beat the actual SPY
# investor experience over multiple regimes.

SPY_CAGR_MEAN = 0.1121   # (0.1147 + 0.1095) / 2
SPY_MDD_MEAN = 0.5517    # (0.5514 + 0.5520) / 2
SPY_SHARPE_MEAN = 0.6661  # (0.6800 + 0.6522) / 2

CAGR_BAR = SPY_CAGR_MEAN
MDD_BAR = SPY_MDD_MEAN

# Scoring anchor ranges
# Adjusted 2026-04-29: MDD ceiling/floor recalibrated to 70%/15% to span the
# new realistic range (SPY MDD now 55%; "great" strategies cluster ~30-40%;
# only de-risked / 2× leverage / SPY-itself score in 50-70% band).
CAGR_FLOOR = 0.05    # CAGR ≤ 5% → 0 pts
CAGR_CEILING = 0.20  # CAGR ≥ 20% → 30 pts
MDD_FLOOR = 0.15     # MDD ≤ 15% → 20 pts (was 10%)
MDD_CEILING = 0.70   # MDD ≥ 70% → 0 pts (was 50%)
SHARPE_FLOOR = 0.50  # Sharpe ≤ 0.5 → 0 pts
SHARPE_CEILING = 2.0  # Sharpe ≥ 2.0 → 10 pts


def _clamp(value: float, lo: float, hi: float) -> float:
    """Clamp value to [lo, hi]."""
    return max(lo, min(hi, value))


def compute_cagr_points(mean_cagr: float) -> int:
    """30 pts × clamp((mean_cagr - 0.05) / (0.20 - 0.05), 0, 1).

    SPY mean (0.1380) yields ~17.6 → int 17.
    """
    raw = 30.0 * _clamp((mean_cagr - CAGR_FLOOR) / (CAGR_CEILING - CAGR_FLOOR), 0.0, 1.0)
    return int(round(raw))


def compute_mdd_points(mean_mdd: float) -> int:
    """20 pts × clamp((0.50 - mean_mdd) / (0.50 - 0.10), 0, 1).

    SPY mean (0.4085) yields ~4.6 → int 4 (truncated from rounding).
    """
    raw = 20.0 * _clamp((MDD_CEILING - mean_mdd) / (MDD_CEILING - MDD_FLOOR), 0.0, 1.0)
    return int(raw)  # truncate (per spec example: 4.575 → 4)


def compute_gates_points(
    gates: dict[str, Gates],
    datasets: list[str],
) -> tuple[int, dict[str, int], bool]:
    """20 pts: 3 pts at min threshold per dataset, +5 bonus if all datasets meet.

    Returns:
        (points, per_dataset_n_passed, cross_dataset_met).
    """
    pts = 0
    per_ds: dict[str, int] = {}
    for ds in datasets:
        n = gates[ds].n_passed
        per_ds[ds] = n
        threshold = GATE_THRESHOLDS.get(ds, 4)
        if n >= 7:
            pts += 5
        elif n >= threshold + 1:
            pts += 4
        elif n >= threshold:
            pts += 3
        elif n >= threshold - 1:
            pts += 1
    cross_met = all(per_ds[ds] >= GATE_THRESHOLDS.get(ds, 4) for ds in datasets)
    if cross_met:
        pts += 5
    return min(20, pts), per_ds, cross_met


def compute_dsr_points(worst_p_value: float) -> int:
    """10 @ p<0.05 / 7 @ p<0.10 / 3 @ p<0.20 / 0 otherwise."""
    if worst_p_value < 0.05:
        return 10
    if worst_p_value < 0.10:
        return 7
    if worst_p_value < 0.20:
        return 3
    return 0


def compute_sharpe_points(mean_sharpe: float) -> int:
    """10 pts × clamp((mean_sharpe - 0.5) / (2.0 - 0.5), 0, 1)."""
    raw = 10.0 * _clamp((mean_sharpe - SHARPE_FLOOR) / (SHARPE_CEILING - SHARPE_FLOOR), 0.0, 1.0)
    return int(round(raw))


def compute_robustness_points(robustness_bonus: int) -> int:
    """Pass-through bonus, clamped to [0, 10]."""
    return max(0, min(10, robustness_bonus))


def compute_multi_horizon_robustness(
    rolling_pass_rates: dict[int, float],
) -> int:
    """Multi-horizon robustness criterion (10pts max).

    Args:
        rolling_pass_rates: {window_years: pass_rate} where pass_rate is the
            fraction of W-year rolling windows in which the strategy beat
            the SPY benchmark CAGR. NaN rates (window doesn't fit dataset)
            are excluded from scoring.

    Scoring:
      - 5y window:  3 pts × pass_rate
      - 10y window: 3 pts × pass_rate
      - 15y window: 2 pts × pass_rate
      - 20y window: 2 pts × pass_rate
    """
    weights = {5: 3, 10: 3, 15: 2, 20: 2}
    total = 0.0
    for w, max_pts in weights.items():
        rate = rolling_pass_rates.get(w, float("nan"))
        if rate != rate:  # NaN check
            continue
        total += max_pts * float(rate)
    return int(round(total))


def compute_gates_bar_met(
    gates: dict[str, Gates],
    datasets: list[str],
    min_datasets: int = 2,
) -> bool:
    """Bar 3: ≥ min_datasets/total reach the per-dataset threshold."""
    n_meet = sum(
        1 for ds in datasets
        if gates[ds].n_passed >= GATE_THRESHOLDS.get(ds, 4)
    )
    return n_meet >= min_datasets


def tier_from_score_spy_beater(
    score: int,
    *,
    bars_met_count: int,
    winner_conditions_met: bool,
) -> Tier:
    """Tier mapping per WINNER_AND_RANKING.md.

    Note: this is more forgiving than long_term_portfolio.tier_from_score
    in the (1-2 bars met) case to track near-miss strategies.
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


def score_strategy_spy_beater(
    metrics: dict[str, DatasetMetrics],
    gates: dict[str, Gates],
    cumulative_n_trials: int,
    robustness_bonus: int = 0,
    extra_bonus: int = 0,
    rolling_pass_rates: dict[int, float] | None = None,
    rolling_worst_mdd: dict[int, float] | None = None,
) -> dict:
    """Score a strategy under spy_beater rubric (CAGR-anchored).

    Args:
        metrics: per-dataset DatasetMetrics (sharpe, cagr, mdd, dsr_p_value).
        gates: per-dataset Gates (7-gate battery).
        cumulative_n_trials: prior + this iter's configs (for DSR penalty).
        robustness_bonus: 0-10 pts (caller computes 5y rolling Sharpe %positive).
        extra_bonus: 0-5 pts caller-supplied (regime-spread, breadth, etc.).

    Returns:
        verdict-shaped dict with status, tier, total_score, bars, criteria,
        metrics_used, cumulative_n_trials.
    """
    datasets = list(metrics.keys())
    n_ds = len(datasets)

    # Means across datasets (skipping NaN if any)
    cagrs = [metrics[ds].cagr for ds in datasets]
    mdds = [metrics[ds].mdd for ds in datasets]
    sharpes = [metrics[ds].sharpe for ds in datasets]
    p_values = [
        metrics[ds].dsr_p_value for ds in datasets
        if metrics[ds].dsr_p_value is not None
    ]

    mean_cagr = sum(cagrs) / n_ds if n_ds else 0.0
    mean_mdd = sum(mdds) / n_ds if n_ds else 1.0
    mean_sharpe = sum(sharpes) / n_ds if n_ds else 0.0
    worst_p = max(p_values) if p_values else 1.0

    # Strict bars
    cagr_bar_met = mean_cagr >= CAGR_BAR
    mdd_bar_met = mean_mdd <= MDD_BAR
    gates_bar_met = compute_gates_bar_met(gates, datasets)
    bars = {
        "cagr_bar": cagr_bar_met,
        "mdd_bar": mdd_bar_met,
        "gates_bar": gates_bar_met,
    }
    bars_met = sum(bars.values())
    winner_conditions_met = all(bars.values())

    # Scoring
    c1_pts = compute_cagr_points(mean_cagr)
    c2_pts = compute_mdd_points(mean_mdd)
    c3_pts, per_ds_gates, cross_ds_met = compute_gates_points(gates, datasets)
    c4_pts = compute_dsr_points(worst_p)
    c5_pts = compute_sharpe_points(mean_sharpe)
    # Multi-horizon robustness (replaces 5y rolling Sharpe pass-through):
    # if rolling_pass_rates supplied, use multi-window CAGR pass-rate;
    # else fall back to caller's `robustness_bonus` (legacy path).
    if rolling_pass_rates is not None:
        c6_pts = compute_multi_horizon_robustness(rolling_pass_rates)
    else:
        c6_pts = compute_robustness_points(robustness_bonus)
    c7_pts = max(0, min(5, extra_bonus))

    total = c1_pts + c2_pts + c3_pts + c4_pts + c5_pts + c6_pts + c7_pts
    total = max(0, min(100, total))

    tier = tier_from_score_spy_beater(
        total,
        bars_met_count=bars_met,
        winner_conditions_met=winner_conditions_met,
    )

    return {
        "status": tier.value.lower(),
        "tier": tier.value,
        "total_score": total,
        "winner_conditions_met": winner_conditions_met,
        "bars": bars,
        "bars_met_count": bars_met,
        "criteria": {
            "1_cagr": {
                "points": c1_pts, "max": 30,
                "mean_cagr": mean_cagr, "spy_bar": CAGR_BAR,
                "anchor_range": [CAGR_FLOOR, CAGR_CEILING],
            },
            "2_mdd": {
                "points": c2_pts, "max": 20,
                "mean_mdd": mean_mdd, "spy_bar": MDD_BAR,
                "anchor_range": [MDD_CEILING, MDD_FLOOR],
            },
            "3_gates": {
                "points": c3_pts, "max": 20,
                "per_dataset": per_ds_gates,
                "thresholds": {ds: GATE_THRESHOLDS.get(ds, 4) for ds in datasets},
                "cross_dataset_met": cross_ds_met,
            },
            "4_dsr": {
                "points": c4_pts, "max": 10,
                "worst_p_value": worst_p,
                "cumulative_n_trials": cumulative_n_trials,
            },
            "5_sharpe": {
                "points": c5_pts, "max": 10,
                "mean_sharpe": mean_sharpe,
                "anchor_range": [SHARPE_FLOOR, SHARPE_CEILING],
            },
            "6_robustness": {
                "points": c6_pts, "max": 10,
                "input_bonus": robustness_bonus,
                "rolling_pass_rates": rolling_pass_rates or {},
                "rolling_worst_mdd": rolling_worst_mdd or {},
                "note": (
                    "Multi-horizon CAGR pass-rate vs SPY benchmark across "
                    "5y/10y/15y/20y rolling windows (3+3+2+2 pts max)."
                ),
            },
            "7_extra_bonus": {"points": c7_pts, "max": 5},
        },
        "metrics_used": {
            ds: {
                "sharpe": metrics[ds].sharpe,
                "cagr": metrics[ds].cagr,
                "mdd": metrics[ds].mdd,
                "dsr_p_value": metrics[ds].dsr_p_value,
            }
            for ds in datasets
        },
        "spy_benchmark": {"cagr_mean": SPY_CAGR_MEAN, "mdd_mean": SPY_MDD_MEAN},
        "cumulative_n_trials": cumulative_n_trials,
    }
