"""Tests for the strategy hunt loop scoring rubric."""

from __future__ import annotations

import sys
from pathlib import Path

# Make studies/strategy_hunt_loop importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "studies" / "strategy_hunt_loop"))

import pytest  # noqa: E402

from scoring import (  # noqa: E402
    BENCHMARKS,
    Benchmark,
    DatasetMetrics,
    Gates,
    Tier,
    score_strategy,
    tier_from_score,
)


def _perfect_metrics() -> dict[str, DatasetMetrics]:
    """Build metrics that should score 100 against default benchmarks."""
    return {
        "educational": DatasetMetrics(
            sharpe=1.00,      # > 0.68 + 0.10 = 0.78 ✓
            cagr=0.20,        # > 0.1147 × 0.8 ✓
            mdd=0.40,         # < 0.5514 + 0.05 ✓
            dsr_p_value=0.01,
        ),
        "spy_real": DatasetMetrics(
            sharpe=1.10,      # > 0.90 + 0.10 ✓
            cagr=0.18,        # > 0.1497 × 0.8 ✓
            mdd=0.30,         # < 0.3370 + 0.05 ✓
            dsr_p_value=0.01,
        ),
        "ndx_real": DatasetMetrics(
            sharpe=1.20,      # > 0.955 + 0.10 ✓
            cagr=0.20,        # > 0.1918 × 0.8 ✓
            mdd=0.32,         # < 0.3512 + 0.05 ✓
            dsr_p_value=0.01,
        ),
    }


def _perfect_gates() -> dict[str, Gates]:
    return {
        "educational": Gates(g1_pbo=True, g2_dsr=True, g3_wf=True,
                             g4_oos=True, g5_fwd=True, g6_bootstrap=True,
                             g7_crosslib=True),
        "spy_real": Gates(g1_pbo=True, g2_dsr=True, g3_wf=True,
                          g4_oos=True, g5_fwd=True, g6_bootstrap=True,
                          g7_crosslib=True),
        "ndx_real": Gates(g1_pbo=True, g2_dsr=True, g3_wf=True,
                          g4_oos=True, g5_fwd=True, g6_bootstrap=True,
                          g7_crosslib=True),
    }


class TestTierMapping:
    @pytest.mark.parametrize(
        "score,expected_tier",
        [
            # Without winner_conditions_met=True, 100 caps at STRONG.
            (100, Tier.STRONG),
            (95, Tier.STRONG),
            (80, Tier.STRONG),
            (75, Tier.STRONG),
            (74, Tier.PROMISING),
            (60, Tier.PROMISING),
            (59, Tier.MARGINAL),
            (40, Tier.MARGINAL),
            (39, Tier.NEAR_FAIL),
            (20, Tier.NEAR_FAIL),
            (19, Tier.FAIL),
            (0, Tier.FAIL),
        ],
    )
    def test_tier_boundaries(self, score, expected_tier):
        assert tier_from_score(score, winner_conditions_met=False) == expected_tier

    def test_winner_tier_requires_all_5_conditions(self):
        # Score 100 but winner_conditions_met=False → STRONG, not WINNER
        # Prevents scoring function alone from claiming WINNER.
        assert tier_from_score(100, winner_conditions_met=False) == Tier.STRONG
        assert tier_from_score(100, winner_conditions_met=True) == Tier.WINNER


class TestPerfectStrategy:
    def test_all_5_met_scores_95_without_robustness_bonus_but_winner(self):
        """Max core score is 95 (without +5 robustness bonus). Winner still
        requires tier=WINNER which is granted via winner_conditions_met check."""
        result = score_strategy(
            _perfect_metrics(), _perfect_gates(),
            cumulative_n_trials=5000,
        )
        # Core criteria 1-5 sum to 95; robustness bonus not auto-computed.
        assert result.total_score == 95
        # With winner_conditions_met=True and score ≥ 90, tier is WINNER.
        assert result.tier == Tier.WINNER
        assert result.winner_conditions_met is True


class TestFailingStrategy:
    def test_all_zero_metrics_scores_low_fail(self):
        bad_metrics = {
            ds: DatasetMetrics(sharpe=0.0, cagr=0.0, mdd=0.90, dsr_p_value=0.99)
            for ds in ["educational", "spy_real", "ndx_real"]
        }
        bad_gates = {
            ds: Gates(g1_pbo=False, g2_dsr=False, g3_wf=False,
                      g4_oos=False, g5_fwd=False, g6_bootstrap=False,
                      g7_crosslib=False)
            for ds in ["educational", "spy_real", "ndx_real"]
        }
        result = score_strategy(bad_metrics, bad_gates, cumulative_n_trials=5000)
        assert result.total_score == 0
        assert result.tier == Tier.FAIL
        assert result.winner_conditions_met is False


class TestPartialCredit:
    def test_sharpe_edge_one_dataset(self):
        """Sharpe edge on only 1 dataset → 10 points for that criterion."""
        m = _perfect_metrics()
        m["educational"].sharpe = 0.50  # below benchmark 0.68
        m["ndx_real"].sharpe = 0.50  # below benchmark 0.955
        # Only spy_real beats → 10 pts for criterion 1
        g = _perfect_gates()
        result = score_strategy(m, g, cumulative_n_trials=5000)
        assert result.criteria["1_sharpe_edge"]["points"] == 10
        assert result.criteria["1_sharpe_edge"]["datasets_beat"] == 1

    def test_gates_partial_credit(self):
        """Partial gate passes still score points."""
        m = _perfect_metrics()
        g = _perfect_gates()
        # Degrade spy_real to 4/7 (exactly min threshold)
        g["spy_real"] = Gates(g1_pbo=True, g2_dsr=True, g3_wf=True,
                              g4_oos=True, g5_fwd=False, g6_bootstrap=False,
                              g7_crosslib=False)
        result = score_strategy(m, g, cumulative_n_trials=5000)
        # Should still get the cross-dataset bonus since 5/7+4/7+7/7 all meet thresholds
        assert result.criteria["2_gates"]["cross_dataset_thresholds_met"] is True

    def test_dsr_p_value_tiers(self):
        m = _perfect_metrics()
        g = _perfect_gates()
        # p=0.06 → partial credit
        for ds in m:
            m[ds].dsr_p_value = 0.06
        result = score_strategy(m, g, cumulative_n_trials=5000)
        assert result.criteria["3_dsr"]["points"] == 10  # <0.10 bucket
        # p=0.15 → smaller credit
        for ds in m:
            m[ds].dsr_p_value = 0.15
        result = score_strategy(m, g, cumulative_n_trials=5000)
        assert result.criteria["3_dsr"]["points"] == 5   # <0.20 bucket
        # p=0.5 → no credit
        for ds in m:
            m[ds].dsr_p_value = 0.5
        result = score_strategy(m, g, cumulative_n_trials=5000)
        assert result.criteria["3_dsr"]["points"] == 0


class TestNearMiss:
    def test_crash_protected_top_candidate_approx(self):
        """Back-fill of iter 001 top candidate (3x UPRO + stop + CAPE).

        Approximate values from studies/ema_sma_threshold_crash_protected/
        phase3/cross_dataset_gates.md for EMA_N150_th5_bL3_sL0 + sl30_rec10_cape05.
        Expected: MARGINAL tier.
        """
        m = {
            "educational": DatasetMetrics(
                sharpe=0.87, cagr=0.2401, mdd=0.4455, dsr_p_value=0.04,
            ),
            "spy_real": DatasetMetrics(
                sharpe=0.68, cagr=0.1809, mdd=0.4377, dsr_p_value=0.3,
            ),
            "ndx_real": DatasetMetrics(
                sharpe=0.70, cagr=0.19, mdd=0.50, dsr_p_value=0.25,
            ),
        }
        g = {
            "educational": Gates(g1_pbo=True, g2_dsr=True, g3_wf=False,
                                 g4_oos=True, g5_fwd=True, g6_bootstrap=True,
                                 g7_crosslib=True),  # 6/7
            "spy_real": Gates(g1_pbo=False, g2_dsr=False, g3_wf=False,
                              g4_oos=True, g5_fwd=True, g6_bootstrap=False,
                              g7_crosslib=True),  # 3/7
            "ndx_real": Gates(g1_pbo=False, g2_dsr=False, g3_wf=False,
                              g4_oos=True, g5_fwd=True, g6_bootstrap=False,
                              g7_crosslib=True),  # 3/7
        }
        result = score_strategy(m, g, cumulative_n_trials=4020)
        # Not a winner (3/7 spy_real fails), but has educational edge
        assert result.winner_conditions_met is False
        assert result.tier in (Tier.MARGINAL, Tier.NEAR_FAIL, Tier.PROMISING)
        assert 20 <= result.total_score <= 70


class TestBenchmarks:
    def test_defaults_match_spec(self):
        assert BENCHMARKS["educational"].sharpe == pytest.approx(0.68)
        assert BENCHMARKS["spy_real"].sharpe == pytest.approx(0.90)
        assert BENCHMARKS["ndx_real"].sharpe == pytest.approx(0.955)


class TestSerialization:
    def test_result_to_dict_has_expected_keys(self):
        result = score_strategy(
            _perfect_metrics(), _perfect_gates(), cumulative_n_trials=5000,
        )
        d = result.to_dict()
        assert "total_score" in d
        assert "tier" in d
        assert "winner_conditions_met" in d
        assert "criteria" in d
        assert set(d["criteria"].keys()) == {
            "1_sharpe_edge", "2_gates", "3_dsr",
            "4_cagr_floor", "5_mdd_ceiling", "6_robustness_bonus",
        }
