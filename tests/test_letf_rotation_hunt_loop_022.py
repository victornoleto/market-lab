"""Tests for iter 022 rearm_independent module (parity + PFV gate)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
ITER022 = REPO / "studies" / "letf_rotation_hunt" / "loop_iterations" / "022-2026-05-10-rearm-only-indep-pfv-confirm"
ITER017 = REPO / "studies" / "letf_rotation_hunt" / "loop_iterations" / "017-2026-05-10-postcrash-rearm-tqqq-streak"


def _load(file_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def rearm_independent():
    return _load(ITER022 / "rearm_independent.py", "iter022_rearm_independent_test")


@pytest.fixture(scope="module")
def reentry_overlay():
    return _load(ITER017 / "reentry_overlay.py", "iter022_iter017_reentry_test")


@pytest.fixture
def synthetic_signal() -> pd.Series:
    """A 200-day on_signal with multiple OFF→ON flips and varying off-stretches."""
    rng = pd.date_range("1990-01-01", periods=200, freq="B")
    sig = np.zeros(200, dtype=float)
    # NaN warmup days 0-4
    sig[:5] = np.nan
    # 5-29 OFF, 30-49 ON, 50-99 OFF (50 days), 100-119 ON, 120-129 OFF, 130-150 ON, 151-180 OFF, 181-199 ON
    sig[5:30] = 0.0
    sig[30:50] = 1.0
    sig[50:100] = 0.0
    sig[100:120] = 1.0
    sig[120:130] = 0.0
    sig[130:151] = 1.0
    sig[151:181] = 0.0
    sig[181:200] = 1.0
    return pd.Series(sig, index=rng)


def test_disabled_returns_zero(rearm_independent, synthetic_signal):
    gate = rearm_independent.build_postcrash_rearm_gate_independent(
        on_signal=synthetic_signal, t_crash=0, d_arm=60,
    )
    assert (gate == 0).all()
    gate = rearm_independent.build_postcrash_rearm_gate_independent(
        on_signal=synthetic_signal, t_crash=40, d_arm=0,
    )
    assert (gate == 0).all()


def test_parity_with_iter017(rearm_independent, reentry_overlay, synthetic_signal):
    """INDEPENDENT impl must produce bit-exact identical gate as iter 017 module."""
    for t_crash, d_arm in [(20, 30), (40, 60), (10, 5), (1, 1), (50, 100)]:
        g_indep = rearm_independent.build_postcrash_rearm_gate_independent(
            on_signal=synthetic_signal, t_crash=t_crash, d_arm=d_arm,
        )
        g_iter017 = reentry_overlay.build_postcrash_rearm_gate(
            on_signal=synthetic_signal, t_crash=t_crash, d_arm=d_arm,
        )
        max_diff = (g_indep.fillna(0.0) - g_iter017.fillna(0.0)).abs().max()
        assert max_diff < 1e-12, f"parity failed for T={t_crash} D={d_arm}: max_diff={max_diff}"


def test_qualifying_flips_count(rearm_independent, synthetic_signal):
    """At T_crash=40, only the 50-day OFF (50→100) qualifies; 25-day and 30-day OFFs do not."""
    diag = rearm_independent.diagnose_rearm_events_independent(
        on_signal=synthetic_signal, t_crash=40, d_arm=60,
    )
    assert diag["n_qualified_flips"] == 1
    # At T_crash=20, 25/50/10/30 OFFs → 25 and 50 qualify (10 and 30 don't... wait 30 does).
    diag2 = rearm_independent.diagnose_rearm_events_independent(
        on_signal=synthetic_signal, t_crash=20, d_arm=60,
    )
    # OFFs: 5-29 (25 days), 50-99 (50 days), 120-129 (10 days), 151-180 (30 days)
    # T_crash=20: 25 ✓, 50 ✓, 10 ✗, 30 ✓ → 3 qualifying flips.
    assert diag2["n_qualified_flips"] == 3


def test_pfv_disabled_d_arm_le_confirm_window(rearm_independent, synthetic_signal):
    """If d_arm <= confirm_window, gate is all zeros."""
    qld_returns = pd.Series(
        np.random.RandomState(0).randn(len(synthetic_signal)) * 0.01,
        index=synthetic_signal.index,
    )
    gate = rearm_independent.post_flip_vol_confirmation_gate(
        on_signal=synthetic_signal, asset_returns=qld_returns,
        t_crash=20, d_arm=5, confirm_window=5,
    )
    assert (gate == 0).all()


def test_pfv_subset_of_unconditional_rearm(rearm_independent, synthetic_signal):
    """PFV-AND-rearm gate must be a subset of unconditional rearm gate (where rearm fires)."""
    qld_returns = pd.Series(
        np.random.RandomState(42).randn(len(synthetic_signal)) * 0.01,
        index=synthetic_signal.index,
    )
    rearm = rearm_independent.build_postcrash_rearm_gate_independent(
        on_signal=synthetic_signal, t_crash=20, d_arm=60,
    )
    pfv = rearm_independent.post_flip_vol_confirmation_gate(
        on_signal=synthetic_signal, asset_returns=qld_returns,
        t_crash=20, d_arm=60, confirm_window=5, pct_window=60, pct_threshold=0.5,
    )
    # PFV-active days must imply rearm-active days (PFV ⊆ rearm).
    assert ((pfv == 1) & (rearm == 0)).sum() == 0


def test_pfv_diag_counts_consistent(rearm_independent, synthetic_signal):
    qld_returns = pd.Series(
        np.random.RandomState(7).randn(len(synthetic_signal)) * 0.01,
        index=synthetic_signal.index,
    )
    diag = rearm_independent.diagnose_pfv_events(
        on_signal=synthetic_signal, asset_returns=qld_returns,
        t_crash=20, d_arm=60, confirm_window=5, pct_window=60, pct_threshold=0.2,
    )
    # n_pfv_qualified_flips ≤ n_duration_qualified_flips
    assert diag["n_pfv_qualified_flips"] <= diag["n_duration_qualified_flips"]
    assert diag["n_active_rearm_days"] >= 0
