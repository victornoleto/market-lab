"""Pre-registered KILL rules + inheritance fallback per spec §3.4.

KILL rules are **informational tags** (loop continues regardless).
Inheritance fallback applied when KILL fires: next tier inherits from
last valid winner (skipping killed tier).

Thresholds frozen at study start; no mid-study adjustments.

Citations:
  - [advances_fin_ml, p.208-211] — combinatorial purged CV / PBO for robustness gates
  - [leverage_for_the_long_run, p.13] — Sharpe edge as primary discriminator across leverage regimes
"""
from __future__ import annotations

KILL_THRESHOLDS = {
    "T0": 0.05,        # T1 vs SPY
    "T1_T2": 0.05,     # T2 vs T1-best
    "T2_T3": 0.05,     # T3 vs T2-best (or T1-best if T2 killed)
    "T3_T4": 0.05,     # T4 vs T3-best (or fallback)
    "T4_T5": 0.10,     # T5 vs T4-best (higher threshold for Carver complexity)
}

KILL_TAG_BY_TRANSITION = {
    "T0": "CLOSE_NO_VALUE",
    "T1_T2": "BASKET_NO_VALUE",
    "T2_T3": "COMPOSITE_NO_VALUE",
    "T3_T4": "CROSS_SECTIONAL_NO_VALUE",
    "T4_T5": "CARVER_NO_VALUE",
}


def evaluate_kill(
    transition: str,
    candidate_sharpe: float,
    anchor_sharpe: float,
) -> dict:
    """Evaluate KILL rule for a transition.

    Parameters
    ----------
    transition : str
        One of T0, T1_T2, T2_T3, T3_T4, T4_T5.
    candidate_sharpe : float
        Best Sharpe of candidate (current) tier.
    anchor_sharpe : float
        Anchor Sharpe (SPY for T0; prev tier best otherwise).

    Returns
    -------
    dict
        {"fires": bool, "status": str, "delta": float, "threshold": float}

    Raises
    ------
    ValueError
        If transition is not one of the registered KILL transitions.
    """
    if transition not in KILL_THRESHOLDS:
        raise ValueError(
            f"Unknown transition: {transition!r}. "
            f"Valid transitions: {list(KILL_THRESHOLDS.keys())}"
        )
    threshold = KILL_THRESHOLDS[transition]
    delta = candidate_sharpe - anchor_sharpe
    fires = delta < threshold
    status = KILL_TAG_BY_TRANSITION[transition] if fires else "PASS"
    return {
        "fires": fires,
        "status": status,
        "delta": float(delta),
        "threshold": threshold,
    }


def resolve_inheritance(
    current_tier: str,
    tier_winners: dict[str, str | None],
    tier_kill_status: dict[str, str],
) -> dict:
    """Resolve inheritance for a new tier, walking back to last valid winner.

    When the immediately preceding tier was killed, walk back through all
    prior tiers to find the last one that both passed its KILL rule AND has
    a named winner config. If no such tier exists, fall back to any tier with
    a non-None winner (kill_fallback=True).

    Parameters
    ----------
    current_tier : str
        e.g. "T3" (about to start)
    tier_winners : dict
        {"T1": config_name, "T2": None | config_name, ...}
        None = tier was killed / no winner yet.
    tier_kill_status : dict
        {"T1": "PASS", "T2": "FIRES", ...}

    Returns
    -------
    dict
        {"from_tier": str, "inherited_config": str | None, "kill_fallback": bool}

    Raises
    ------
    ValueError
        If current_tier is not in the recognised tier order.
    """
    tier_order = ["T1", "T2", "T3", "T4", "T5"]
    if current_tier not in tier_order:
        raise ValueError(f"Unknown tier: {current_tier!r}. Valid tiers: {tier_order}")
    idx = tier_order.index(current_tier)
    prior_tiers = tier_order[:idx]

    # Determine if any prior tier was killed (= any KILL fired on the path)
    any_prior_killed = any(
        tier_kill_status.get(t, "N/A") == "FIRES" for t in prior_tiers
    )

    # Walk back: prefer last tier that both passed its KILL rule AND has a winner
    for prev_tier in reversed(prior_tiers):
        kill_status = tier_kill_status.get(prev_tier, "N/A")
        winner = tier_winners.get(prev_tier)
        if kill_status == "PASS" and winner is not None:
            return {
                "from_tier": prev_tier,
                "inherited_config": winner,
                # kill_fallback=True when we had to skip at least one killed tier
                "kill_fallback": any_prior_killed,
            }

    # Second pass: any tier with a non-None winner (regardless of kill status)
    for prev_tier in reversed(prior_tiers):
        winner = tier_winners.get(prev_tier)
        if winner is not None:
            return {
                "from_tier": prev_tier,
                "inherited_config": winner,
                "kill_fallback": True,
            }
    return {"from_tier": None, "inherited_config": None, "kill_fallback": False}


def deploy_escalation_eligible(
    sharpe_net: float,
    spy_net_sharpe: float,
    score: float,
    gates_all_pass: bool,
    dsr_cumulative_p: float,
) -> bool:
    """Per spec §3.4 DEPLOY ESCALATION criteria.

    Sharpe_net > SPY_net + 0.15 AND DSR cumulative pass AND score ≥ 90 AND all 7 gates pass.

    Threshold revised 2026-05-06 from +0.20 → +0.15 per user decision: a
    sustained +0.15 net Sharpe edge over multi-decade rolling windows is
    economically meaningful, especially after 37k-rolling-window robustness
    validation. See KILL_RULES.md for full rationale.

    Parameters
    ----------
    sharpe_net : float
        Net-of-tax Sharpe of the candidate strategy.
    spy_net_sharpe : float
        Net-of-tax SPY Sharpe on the same period.
    score : float
        Total rubric score (0-100).
    gates_all_pass : bool
        True if all 7 hard gates passed.
    dsr_cumulative_p : float
        Cumulative DSR p-value (must be < 0.05).

    Returns
    -------
    bool
        True if all deploy escalation criteria are met.
    """
    return (
        (sharpe_net - spy_net_sharpe) >= 0.15
        and dsr_cumulative_p < 0.05
        and score >= 90
        and gates_all_pass
    )
