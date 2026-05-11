"""Tests for sortino_reanalysis sub-study (spec §7)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from studies.letf_rotation_hunt.analyses.sortino_reanalysis.sortino_metric import (
    _annualised_sortino,
    _sortino_edge_vs_spy,
)


def test_annualised_sortino_basic():
    """Synthetic returns: deterministic mean + downside dev → exact Sortino 1991."""
    # 10 returns: 5 positive (0.01) and 5 negative (-0.005)
    rets = pd.Series([0.01, -0.005, 0.01, -0.005, 0.01, -0.005, 0.01, -0.005, 0.01, -0.005])
    # mean = (5*0.01 + 5*(-0.005)) / 10 = 0.0025
    # downside_dev = sqrt(mean over ALL N of min(r,0)^2) = sqrt((5 * 0.000025) / 10) = sqrt(0.0000125)
    # sortino = (0.0025 / sqrt(0.0000125)) * sqrt(252)
    expected_dn_dev = np.sqrt((5 * (0.005**2)) / 10)
    expected = (0.0025 / expected_dn_dev) * np.sqrt(252)
    actual = _annualised_sortino(rets, target=0.0, trading_days=252)
    assert abs(actual - expected) < 1e-9, f"expected {expected}, got {actual}"


def test_annualised_sortino_no_downside():
    """All returns >= target → downside_dev = 0 → +inf."""
    rets = pd.Series([0.01, 0.02, 0.005, 0.015])
    actual = _annualised_sortino(rets, target=0.0)
    assert np.isinf(actual) and actual > 0


def test_annualised_sortino_short_returns():
    """len < 2 returns NaN to match scoring.compute_metrics convention."""
    rets = pd.Series([0.01])
    actual = _annualised_sortino(rets, target=0.0)
    assert np.isnan(actual)


def test_sortino_edge_vs_spy():
    """Pure subtraction over a (sortino, dataset_dict) pair."""
    spy_per_ds = {"lh_56y": 0.50, "modern_1990": 0.65}
    edge = _sortino_edge_vs_spy(0.85, spy_per_ds, "lh_56y")
    assert abs(edge - 0.35) < 1e-12
    edge2 = _sortino_edge_vs_spy(0.40, spy_per_ds, "modern_1990")
    assert abs(edge2 - (-0.25)) < 1e-12


def test_threshold_rebuild():
    """Track A/B-M1/B-M2 thresholds = canonical_sortino + 0.05 (literal)."""
    from studies.letf_rotation_hunt.analyses.sortino_reanalysis.winner_detection import (
        rebuild_thresholds,
    )
    canonical = {"gross": 1.20, "m1": 0.95, "m2": 1.10}
    out = rebuild_thresholds(canonical)
    assert abs(out["track_a"] - 1.25) < 1e-12
    assert abs(out["track_b_m1"] - 1.00) < 1e-12
    assert abs(out["track_b_m2"] - 1.15) < 1e-12


def test_winner_changed_detection():
    """Strategy with higher sortino_edge_vs_canonical AND track_a_pass becomes new winner."""
    from studies.letf_rotation_hunt.analyses.sortino_reanalysis.winner_detection import (
        detect_new_winner,
    )
    df = pd.DataFrame([
        {"strategy": "qld_vote_k2_off_zroz", "dataset": "lh_56y", "track": "gross",
         "sortino": 1.20, "sortino_edge_vs_canonical": 0.0, "track_a_pass_sortino": True},
        {"strategy": "t3d_k2_smabuf_5pct", "dataset": "lh_56y", "track": "gross",
         "sortino": 1.30, "sortino_edge_vs_canonical": 0.10, "track_a_pass_sortino": True},
        {"strategy": "qld_voteK2_off_ief", "dataset": "lh_56y", "track": "gross",
         "sortino": 1.05, "sortino_edge_vs_canonical": -0.15, "track_a_pass_sortino": False},
    ])
    changed, new_winner = detect_new_winner(df)
    assert changed is True
    assert new_winner == "t3d_k2_smabuf_5pct"


def test_idempotency_no_change():
    """If no strategy passes Track A, winner_changed=False and cohort extension skipped."""
    from studies.letf_rotation_hunt.analyses.sortino_reanalysis.winner_detection import (
        detect_new_winner,
    )
    df = pd.DataFrame([
        {"strategy": "qld_vote_k2_off_zroz", "dataset": "lh_56y", "track": "gross",
         "sortino": 1.20, "sortino_edge_vs_canonical": 0.0, "track_a_pass_sortino": False},
        {"strategy": "t3d_k2_smabuf_5pct", "dataset": "lh_56y", "track": "gross",
         "sortino": 1.22, "sortino_edge_vs_canonical": 0.02, "track_a_pass_sortino": False},
    ])
    changed, new_winner = detect_new_winner(df)
    assert changed is False
    assert new_winner is None


@pytest.mark.slow
def test_recompute_canonical_lh56y():
    """Integration: re-dispatch canonical, assert sortino > 0 and sortino > sharpe.

    Spot-checks the LETF asymmetric-upside hypothesis on canonical lh_56y gross.
    Expected: Sortino ~1.20+ vs Sharpe ~0.85 (per parent study).
    """
    from studies.letf_rotation_hunt.analyses.sortino_reanalysis.recompute import (
        recompute_canonical,
    )
    rows = recompute_canonical()
    lh_gross = [r for r in rows if r["dataset"] == "lh_56y" and r["track"] == "gross"][0]
    assert lh_gross["sortino"] > 0
    assert lh_gross["sharpe"] > 0
    # Canonical asymmetric-upside spot check: Sortino should exceed Sharpe in absolute terms.
    assert lh_gross["sortino"] > lh_gross["sharpe"]
