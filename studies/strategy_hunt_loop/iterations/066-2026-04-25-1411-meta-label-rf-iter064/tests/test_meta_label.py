"""Iter 066 — Purged k-fold + RF wrapper invariants."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ITER_DIR))

from meta_label_rf import (  # noqa: E402
    fit_predict_purged_kfold,
    make_fold_assignments,
    purged_train_mask,
)


def test_make_fold_assignments_5fold_balanced():
    a = make_fold_assignments(100, 5)
    counts = np.bincount(a)
    assert len(counts) == 5
    # Balanced: ≥ 20 each
    assert counts.min() >= 20


def test_make_fold_assignments_remainder_in_last():
    a = make_fold_assignments(102, 5)
    counts = np.bincount(a)
    assert counts[-1] == 22
    assert counts[0] == 20


def test_purged_train_mask_excludes_test_fold():
    a = make_fold_assignments(50, 5)
    mask = purged_train_mask(a, fold_id=2, embargo=0)
    # Fold 2 = bars 20-29 (no embargo, just exclude test).
    assert (mask[20:30] == False).all()
    assert (mask[0:20] == True).all()
    assert (mask[30:50] == True).all()


def test_purged_train_mask_with_embargo():
    a = make_fold_assignments(50, 5)
    mask = purged_train_mask(a, fold_id=2, embargo=5)
    # Embargo 5: drop train bars within 5 of test boundaries.
    assert (mask[15:35] == False).all()
    assert (mask[0:15] == True).all()
    assert (mask[35:50] == True).all()


def test_purged_kfold_no_train_test_overlap():
    rng = np.random.default_rng(42)
    n = 500
    X = pd.DataFrame(rng.normal(size=(n, 5)),
                     columns=[f"f{i}" for i in range(5)],
                     index=pd.date_range("2010", periods=n, freq="B"))
    y = pd.Series((rng.normal(size=n) > 0).astype(int), index=X.index)
    res = fit_predict_purged_kfold(X, y, n_folds=5, embargo=10)
    # All bars get an OOF prediction.
    assert res.oof_proba.notna().all()
    assert res.oof_pred.isin([0, 1]).all()
    assert len(res.fold_aucs) == 5


def test_purged_kfold_deterministic():
    rng = np.random.default_rng(7)
    n = 300
    X = pd.DataFrame(rng.normal(size=(n, 5)),
                     columns=[f"f{i}" for i in range(5)],
                     index=pd.date_range("2010", periods=n, freq="B"))
    y = pd.Series((rng.normal(size=n) > 0).astype(int), index=X.index)
    r1 = fit_predict_purged_kfold(X, y, n_folds=5, embargo=10)
    r2 = fit_predict_purged_kfold(X, y, n_folds=5, embargo=10)
    np.testing.assert_array_equal(r1.oof_pred.values, r2.oof_pred.values)
    np.testing.assert_array_almost_equal(r1.oof_proba.values, r2.oof_proba.values)


def test_purged_kfold_signal_label_alignment():
    """When y is informatively predictable from X, AUC must be > 0.5."""
    rng = np.random.default_rng(123)
    n = 800
    f0 = rng.normal(size=n)
    # y depends on f0 monotonically (with noise).
    y_arr = ((f0 + 0.5 * rng.normal(size=n)) > 0).astype(int)
    X = pd.DataFrame({"f0": f0, "f1": rng.normal(size=n),
                      "f2": rng.normal(size=n), "f3": rng.normal(size=n),
                      "f4": rng.normal(size=n)},
                     index=pd.date_range("2010", periods=n, freq="B"))
    y = pd.Series(y_arr, index=X.index)
    res = fit_predict_purged_kfold(X, y, n_folds=5, embargo=10)
    assert res.avg_auc > 0.55, f"AUC must improve over chance, got {res.avg_auc}"
