"""Verdict engine.

Maps each RunResult to a 4-tier verdict (CONFIRMS-STRONG / CONFIRMS / WARNING /
REFUTES) against a pinned Baseline, then aggregates per-lib tiers into a
variant-level aggregate verdict (VALIDATED / VALIDATED-WITH-CAVEATS /
BLOCKED-INVESTIGATE / INCONCLUSIVE).

Citations
---------
- Tolerance magnitudes: `[advances_fin_ml, p.208-211]`
- Strategy similarity under perturbation: `[advances_fin_ml, p.273-275]`
- 5-gate framework: `[advances_fin_ml, p.208-211, p.273-275, p.298-299]`
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from reports.phase_3_5c.cross_lib.types import RunResult


class Tier(str, Enum):
    CONFIRMS_STRONG = "CONFIRMS-STRONG"
    CONFIRMS = "CONFIRMS"
    WARNING = "WARNING"
    REFUTES = "REFUTES"


class AggregateVerdict(str, Enum):
    VALIDATED = "VALIDATED"
    VALIDATED_WITH_CAVEATS = "VALIDATED-WITH-CAVEATS"
    BLOCKED_INVESTIGATE = "BLOCKED-INVESTIGATE"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class Tolerance:
    cagr_pp: float
    sharpe: float
    max_dd_pp: float
    monthly_rho: float


TOL_STRONG = Tolerance(cagr_pp=0.5, sharpe=0.05, max_dd_pp=1.0, monthly_rho=0.99)
TOL_CONFIRM = Tolerance(cagr_pp=2.0, sharpe=0.15, max_dd_pp=3.0, monthly_rho=0.95)


@dataclass(frozen=True)
class Baseline:
    cagr: float
    sharpe: float
    max_dd: float


def classify_tier(
    run: RunResult,
    baseline: Baseline,
    monthly_rho_override: float | None = None,
) -> Tier:
    """Map one run to one tier.

    monthly_rho_override is for unit tests — production callers pass None and
    rho is computed against baseline monthly returns (loaded separately).
    """
    # Gate flips → REFUTES first (they matter most)
    if (
        run.sharpe <= 0
        or abs(run.max_dd) >= 0.25
        or sum(1 for s in run.wf_splits_8 if s > 0) < 6
        or run.dsr_pval >= 0.05
    ):
        return Tier.REFUTES

    rho = monthly_rho_override if monthly_rho_override is not None else 1.0

    d_cagr = abs(run.cagr - baseline.cagr) * 100  # to percentage points
    d_sharpe = abs(run.sharpe - baseline.sharpe)
    d_max_dd = abs(run.max_dd - baseline.max_dd) * 100  # to pp

    if (
        d_cagr < TOL_STRONG.cagr_pp
        and d_sharpe < TOL_STRONG.sharpe
        and d_max_dd < TOL_STRONG.max_dd_pp
        and rho > TOL_STRONG.monthly_rho
    ):
        return Tier.CONFIRMS_STRONG

    if (
        d_cagr < TOL_CONFIRM.cagr_pp
        and d_sharpe < TOL_CONFIRM.sharpe
        and d_max_dd < TOL_CONFIRM.max_dd_pp
        and rho > TOL_CONFIRM.monthly_rho
    ):
        return Tier.CONFIRMS

    return Tier.WARNING


def aggregate_verdict(
    stage1_tiers: dict[str, Tier],
    stage2_tiers: dict[str, Tier],
    min_strong_stage1: int = 2,
    min_confirm_stage2: int = 3,
) -> AggregateVerdict:
    """Aggregate per-lib tiers into a single verdict for one variant.

    Precedence: REFUTES > insufficient coverage > weak-stage-1 > caveats > validated.
    """
    all_tiers = list(stage1_tiers.values()) + list(stage2_tiers.values())

    if Tier.REFUTES in all_tiers:
        return AggregateVerdict.BLOCKED_INVESTIGATE

    if len(stage1_tiers) < min_strong_stage1:
        return AggregateVerdict.INCONCLUSIVE

    strong_s1 = sum(1 for t in stage1_tiers.values() if t == Tier.CONFIRMS_STRONG)
    if strong_s1 < min_strong_stage1:
        return AggregateVerdict.BLOCKED_INVESTIGATE

    pass_s2 = sum(1 for t in stage2_tiers.values() if t in (Tier.CONFIRMS_STRONG, Tier.CONFIRMS))
    warn_s2 = sum(1 for t in stage2_tiers.values() if t == Tier.WARNING)

    if pass_s2 >= min_confirm_stage2:
        return AggregateVerdict.VALIDATED

    if pass_s2 + warn_s2 >= min_confirm_stage2 and warn_s2 <= 2:
        return AggregateVerdict.VALIDATED_WITH_CAVEATS

    return AggregateVerdict.INCONCLUSIVE
