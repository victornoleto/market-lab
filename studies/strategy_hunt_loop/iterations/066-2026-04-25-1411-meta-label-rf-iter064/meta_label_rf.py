"""Iter 066 — Random Forest meta-label with purged k-fold CV.

Implements 5-fold purged k-fold cross-validation [advances_fin_ml, ch.7]
with explicit ``embargo`` to prevent train/test contamination via
overlapping forward labels. For each fold k:

1. Test = bars in contiguous block k.
2. Train = all bars NOT within ``embargo`` of fold k's boundaries.
3. Fit ``RandomForestClassifier(n_estimators=200, max_depth=4,
   random_state=42, class_weight='balanced')`` on train.
4. Predict P(class=1) on test → store as out-of-fold probability.

The concatenation of OOF probabilities forms a single full-length
prediction series. Binary signal = ``oof_proba > 0.5``.

Citations
---------
* `[advances_fin_ml, ch.7]` — purged k-fold; embargo prevents look-ahead.
* `[advances_fin_ml, ch.3]` — meta-labeling pattern.
* Breiman (2001) DOI 10.1023/A:1010933404324 — Random Forest.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score


RF_PARAMS: dict = {
    "n_estimators": 200,
    "max_depth": 4,
    "random_state": 42,
    "n_jobs": 1,
    "class_weight": "balanced",
}


@dataclass
class MetaLabelResult:
    oof_proba: pd.Series         # P(class=1) per bar, OOF
    oof_pred: pd.Series          # binary 0/1 signal (proba > threshold)
    fold_aucs: list[float]       # per-fold OOF AUC
    avg_auc: float               # mean of fold_aucs
    n_folds: int
    embargo: int
    threshold: float
    fold_assignments: pd.Series  # int fold id per bar
    feature_names: list[str]
    feature_importance_avg: dict[str, float]  # mean across folds


def make_fold_assignments(n_bars: int, n_folds: int) -> np.ndarray:
    """Contiguous fold assignment 0..n_folds-1.

    Last fold absorbs remainder so all folds have ≥ floor(n/k) bars.
    """
    fold_size = n_bars // n_folds
    assignments = np.empty(n_bars, dtype=np.int64)
    for k in range(n_folds):
        start = k * fold_size
        end = start + fold_size if k < n_folds - 1 else n_bars
        assignments[start:end] = k
    return assignments


def purged_train_mask(
    fold_assignments: np.ndarray, fold_id: int, embargo: int,
) -> np.ndarray:
    """Boolean mask of train bars: NOT in fold ``fold_id`` AND NOT within
    ``embargo`` bars of the fold's boundaries on either side.
    """
    n = len(fold_assignments)
    test_idx = np.where(fold_assignments == fold_id)[0]
    if len(test_idx) == 0:
        return np.ones(n, dtype=bool)
    lo = max(0, test_idx[0] - embargo)
    hi = min(n, test_idx[-1] + 1 + embargo)
    train = np.ones(n, dtype=bool)
    train[lo:hi] = False
    return train


def fit_predict_purged_kfold(
    X: pd.DataFrame, y: pd.Series, *,
    n_folds: int = 5, embargo: int = 21, threshold: float = 0.5,
    rf_params: dict | None = None,
) -> MetaLabelResult:
    """Run 5-fold purged k-fold and concatenate OOF predictions.

    Each fold trains a fresh classifier with deterministic seed; OOF
    probabilities and AUC stored. Final ``oof_proba`` series spans the
    full input index (one prediction per bar from its hold-out fold).
    """
    rf_params = rf_params or RF_PARAMS
    if not (X.index.equals(y.index)):
        raise ValueError("X.index must equal y.index")
    n = len(X)
    assignments = make_fold_assignments(n, n_folds)

    oof_proba = np.full(n, np.nan, dtype=np.float64)
    fold_aucs: list[float] = []
    fold_importances: list[np.ndarray] = []

    X_arr = X.to_numpy()
    y_arr = y.to_numpy()

    for k in range(n_folds):
        test_mask = (assignments == k)
        train_mask = purged_train_mask(assignments, k, embargo)
        # Sanity: train ∩ test = ∅
        if (train_mask & test_mask).any():
            raise RuntimeError("purged k-fold contamination: train ∩ test ≠ ∅")
        if y_arr[train_mask].sum() == 0 or (y_arr[train_mask] == 0).sum() == 0:
            # Single-class train fold — predict majority class proba.
            majority = float(y_arr[train_mask].mean())
            oof_proba[test_mask] = majority
            fold_aucs.append(0.5)
            fold_importances.append(np.zeros(X_arr.shape[1]))
            continue
        model = RandomForestClassifier(**rf_params)
        model.fit(X_arr[train_mask], y_arr[train_mask])
        proba_test = model.predict_proba(X_arr[test_mask])[:, 1]
        oof_proba[test_mask] = proba_test
        try:
            auc = float(roc_auc_score(y_arr[test_mask], proba_test))
        except ValueError:
            auc = 0.5
        fold_aucs.append(auc)
        fold_importances.append(np.asarray(model.feature_importances_))

    proba_series = pd.Series(oof_proba, index=X.index, name="oof_proba")
    pred_series = (proba_series > threshold).astype(int)
    pred_series.name = "oof_pred"

    if fold_importances:
        imp_avg = np.mean(np.vstack(fold_importances), axis=0)
        feat_imp = {col: float(imp_avg[i]) for i, col in enumerate(X.columns)}
    else:
        feat_imp = {}

    return MetaLabelResult(
        oof_proba=proba_series,
        oof_pred=pred_series,
        fold_aucs=fold_aucs,
        avg_auc=float(np.mean(fold_aucs)) if fold_aucs else 0.5,
        n_folds=n_folds,
        embargo=embargo,
        threshold=threshold,
        fold_assignments=pd.Series(assignments, index=X.index, name="fold"),
        feature_names=list(X.columns),
        feature_importance_avg=feat_imp,
    )
