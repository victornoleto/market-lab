"""Unit tests for kill_rules.py per spec §3.4."""
from __future__ import annotations

import pytest


def test_kill_t0_fires_below_spy():
    """KILL T0: T1-best Sharpe < SPY+0.05 → CLOSE_NO_VALUE."""
    from studies.letf_rotation_hunt.core.kill_rules import evaluate_kill

    result = evaluate_kill(
        transition="T0",
        candidate_sharpe=0.70,  # only +0.018 above SPY 0.682
        anchor_sharpe=0.682,
    )
    assert result["fires"] is True
    assert result["status"] == "CLOSE_NO_VALUE"


def test_kill_t1_t2_passes():
    """KILL T1→T2 passes when T2 advances ≥ 0.05."""
    from studies.letf_rotation_hunt.core.kill_rules import evaluate_kill

    result = evaluate_kill(
        transition="T1_T2",
        candidate_sharpe=0.85,  # T2-best
        anchor_sharpe=0.78,  # T1-best
    )
    assert result["fires"] is False
    assert result["status"] == "PASS"


def test_kill_t4_t5_requires_higher_threshold():
    """KILL T4→T5 requires +0.10 (not +0.05)."""
    from studies.letf_rotation_hunt.core.kill_rules import evaluate_kill

    # +0.05 not enough for T4→T5
    result = evaluate_kill(
        transition="T4_T5",
        candidate_sharpe=1.05,
        anchor_sharpe=1.00,
    )
    assert result["fires"] is True

    # +0.10 enough
    result2 = evaluate_kill(
        transition="T4_T5",
        candidate_sharpe=1.11,
        anchor_sharpe=1.00,
    )
    assert result2["fires"] is False


def test_inheritance_fallback_after_kill():
    """When tier KILL fires, next tier inherits from last valid winner."""
    from studies.letf_rotation_hunt.core.kill_rules import resolve_inheritance

    # T2 kill fired → T3 should inherit from T1 (skip T2)
    inheritance = resolve_inheritance(
        current_tier="T3",
        tier_winners={"T1": "upro_sma200_off_bil", "T2": None},  # T2 None = killed
        tier_kill_status={"T1": "PASS", "T2": "FIRES"},
    )
    assert inheritance["from_tier"] == "T1"
    assert inheritance["inherited_config"] == "upro_sma200_off_bil"
    assert inheritance["kill_fallback"] is True


def test_deploy_escalation_threshold_relaxed_to_015():
    """Deploy threshold relaxed 2026-05-06 from +0.20 → +0.15 net edge.

    A strategy with Sharpe edge +0.15 over SPY (and other criteria met)
    must now be deploy-eligible. +0.10 still fails."""
    from studies.letf_rotation_hunt.core.kill_rules import deploy_escalation_eligible

    common = dict(
        spy_net_sharpe=0.65, score=92.0, gates_all_pass=True,
        dsr_cumulative_p=0.01,
    )
    # Edge +0.15 → eligible (boundary case)
    assert deploy_escalation_eligible(sharpe_net=0.80, **common) is True
    # Edge +0.10 → NOT eligible
    assert deploy_escalation_eligible(sharpe_net=0.75, **common) is False
    # Edge +0.20 → still eligible (was old threshold)
    assert deploy_escalation_eligible(sharpe_net=0.85, **common) is True


def test_deploy_escalation_score_below_90_blocks():
    """Even if Sharpe edge +0.20, score < 90 blocks deploy."""
    from studies.letf_rotation_hunt.core.kill_rules import deploy_escalation_eligible

    assert deploy_escalation_eligible(
        sharpe_net=0.85, spy_net_sharpe=0.65,
        score=82.0,  # < 90
        gates_all_pass=True, dsr_cumulative_p=0.01,
    ) is False
