"""Top-K candidate rule mining from entry-time features.

Three independent miners that produce a unified `Candidate` list:

  1. Univariate threshold scan — for each (feature, decile threshold), measure
     match-rate of `feature > threshold ⇒ side=Buy` (and the inverse). Bonferroni-
     corrected p-value to filter data-snooping bias.

  2. Decision tree — shallow tree (max_depth=4) trained with purged k-fold CV
     to produce stable rule-paths. Top-3 leaves by support × purity become rules.

  3. RIPPER (lib `wittgenstein`) — IF cond1 AND cond2 THEN side, propositional
     rule learning with internal pruning.

Output: `list[Candidate]` ranked by CV match-rate × coverage.

Citations:
- [advances_fin_ml, ch.5] — feature importance + clustered MDA
- [advances_fin_ml, ch.7] — purged k-fold (avoids info-leak across nearby trades)
- [evidence_based_ta, Aronson] — Bonferroni for multiple-comparison data-snooping
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np
import pandas as pd
from scipy.stats import binomtest


@dataclass
class Candidate:
    rank: int
    miner: str  # "univariate" | "tree" | "ripper"
    rule_text: str
    match_rate_cv: float
    match_rate_std: float
    coverage: float  # fraction of trades the rule predicts on (non-default branch)
    n_features: int
    p_value_corrected: float
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "miner": self.miner,
            "rule_text": self.rule_text,
            "match_rate_cv": float(self.match_rate_cv),
            "match_rate_std": float(self.match_rate_std),
            "coverage": float(self.coverage),
            "n_features": int(self.n_features),
            "p_value_corrected": float(self.p_value_corrected),
            "extra": self.extra,
        }


def _numeric_feature_columns(df: pd.DataFrame) -> list[str]:
    drop = {"pair", "side", "y_buy", "session", "minute", "trade_idx"}
    return [c for c in df.columns if c not in drop and pd.api.types.is_numeric_dtype(df[c])]


def _purged_kfold_indices(
    n: int, k: int = 5, embargo: int = 5
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Sequential k-fold with per-fold embargo (drops `embargo` neighbors of test set).

    Trades are time-ordered; nearby trades share OHLC features. Embargo drops the
    `embargo` rows on either side of the test fold from the training set.
    [advances_fin_ml, ch.7]
    """
    fold_size = n // k
    folds = []
    for i in range(k):
        test_start = i * fold_size
        test_end = (i + 1) * fold_size if i < k - 1 else n
        test_idx = np.arange(test_start, test_end)
        purge_start = max(0, test_start - embargo)
        purge_end = min(n, test_end + embargo)
        train_idx = np.concatenate(
            [np.arange(0, purge_start), np.arange(purge_end, n)]
        )
        folds.append((train_idx, test_idx))
    return folds


def _univariate_scan(
    features: pd.DataFrame, y: np.ndarray, feature_cols: Sequence[str]
) -> list[Candidate]:
    """For each (feature, decile threshold), test `feat > thr ⇒ Buy` and `feat <= thr ⇒ Buy`.

    Match-rate is fraction of trades where prediction matches actual side.
    """
    out: list[Candidate] = []
    n = len(features)
    n_tests = 0
    raw: list[dict] = []
    # Thresholds scale with sample size so the scan still fires on small pilot runs.
    min_valid = max(20, int(0.4 * n))
    min_support = max(10, int(0.15 * n))
    for col in feature_cols:
        s = features[col].astype(float)
        valid = s.notna()
        if valid.sum() < min_valid:
            continue
        s_valid = s[valid]
        y_valid = y[valid.values]
        deciles = np.unique(np.quantile(s_valid, np.linspace(0.1, 0.9, 9)))
        for thr in deciles:
            for direction in (">", "<="):
                pred = (s_valid > thr).astype(int) if direction == ">" else (s_valid <= thr).astype(int)
                if pred.sum() < min_support or pred.sum() > len(pred) - min_support:
                    continue
                # Two complementary rules: pred=1→Buy or pred=1→Sell; pick the better one.
                acc_buy = float((pred == y_valid).mean())
                acc_sell = float((pred != y_valid).mean())
                acc, label = (acc_buy, "Buy") if acc_buy >= acc_sell else (acc_sell, "Sell")
                k = int((pred == (y_valid if label == "Buy" else (1 - y_valid))).sum())
                p = float(binomtest(k, len(pred), p=0.5, alternative="greater").pvalue)
                raw.append({
                    "col": col, "thr": float(thr), "direction": direction,
                    "label": label, "acc": acc, "p": p, "support": int(pred.sum()),
                })
                n_tests += 1

    if not raw:
        return out

    bonferroni = float(max(n_tests, 1))
    raw.sort(key=lambda r: (-r["acc"], r["p"]))
    seen_features: set[str] = set()
    rank = 0
    for r in raw:
        if r["col"] in seen_features:
            continue  # one rule per feature for the top-K
        seen_features.add(r["col"])
        rank += 1
        if rank > 12:
            break
        rule = f"{r['col']} {r['direction']} {r['thr']:.4g} ⇒ {r['label']}"
        out.append(Candidate(
            rank=rank,
            miner="univariate",
            rule_text=rule,
            match_rate_cv=r["acc"],
            match_rate_std=0.0,
            coverage=r["support"] / max(n, 1),
            n_features=1,
            p_value_corrected=min(1.0, r["p"] * bonferroni),
            extra={"raw_p": r["p"], "n_tests": n_tests},
        ))
    return out


def _decision_tree(
    features: pd.DataFrame, y: np.ndarray, feature_cols: Sequence[str]
) -> list[Candidate]:
    try:
        from sklearn.tree import DecisionTreeClassifier, export_text
    except ImportError:
        return []

    X_full = features[list(feature_cols)].astype(float).fillna(features[list(feature_cols)].median(numeric_only=True))
    if len(X_full) < 60 or len(set(y.tolist())) < 2:
        return []

    folds = _purged_kfold_indices(len(X_full), k=5, embargo=5)
    fold_accs: list[float] = []
    for tr, te in folds:
        clf = DecisionTreeClassifier(max_depth=4, min_samples_leaf=50, random_state=7)
        clf.fit(X_full.iloc[tr], y[tr])
        pred = clf.predict(X_full.iloc[te])
        fold_accs.append(float((pred == y[te]).mean()))
    mean_acc = float(np.mean(fold_accs))
    std_acc = float(np.std(fold_accs))

    # Train final tree on full data for the rule export.
    final = DecisionTreeClassifier(max_depth=4, min_samples_leaf=50, random_state=7)
    final.fit(X_full, y)
    text = export_text(final, feature_names=list(feature_cols), max_depth=4)

    importances = pd.Series(final.feature_importances_, index=list(feature_cols))
    top_feats = importances.nlargest(5)
    importance_str = ", ".join(f"{k}={v:.2f}" for k, v in top_feats.items() if v > 0)

    return [Candidate(
        rank=1,
        miner="tree",
        rule_text=f"DecisionTree(max_depth=4) — top features: {importance_str}\n\n{text}",
        match_rate_cv=mean_acc,
        match_rate_std=std_acc,
        coverage=1.0,
        n_features=int((final.feature_importances_ > 0).sum()),
        p_value_corrected=float("nan"),
        extra={"fold_accs": fold_accs},
    )]


def _ripper(features: pd.DataFrame, y: np.ndarray, feature_cols: Sequence[str]) -> list[Candidate]:
    try:
        import wittgenstein as lw
    except ImportError:
        return []

    if len(features) < 100 or len(set(y.tolist())) < 2:
        return []

    df = features[list(feature_cols)].copy()
    df["__target__"] = y
    df = df.dropna(axis=1, thresh=int(0.8 * len(df)))  # drop sparse cols
    df = df.dropna()
    if len(df) < 100:
        return []

    folds = _purged_kfold_indices(len(df), k=5, embargo=5)
    accs: list[float] = []
    for tr, te in folds:
        try:
            clf = lw.RIPPER(random_state=7, prune_size=0.33, k=2)
            clf.fit(df.iloc[tr], class_feat="__target__", pos_class=1)
            preds = clf.predict(df.iloc[te].drop(columns="__target__"))
            preds_int = [int(bool(x)) for x in preds]
            accs.append(float(np.mean(np.array(preds_int) == df.iloc[te]["__target__"].values)))
        except Exception:
            continue
    if not accs:
        return []

    final = lw.RIPPER(random_state=7, prune_size=0.33, k=2)
    final.fit(df, class_feat="__target__", pos_class=1)
    # `out_pretty()` prints to stdout and returns None; `str(ruleset_)` gives the symbolic form.
    rules_text = str(final.ruleset_)
    if not rules_text or rules_text == "None":
        rules_text = repr(final.ruleset_)

    return [Candidate(
        rank=1,
        miner="ripper",
        rule_text=f"RIPPER ruleset:\n{rules_text}",
        match_rate_cv=float(np.mean(accs)),
        match_rate_std=float(np.std(accs)),
        coverage=1.0,
        n_features=len(final.ruleset_) if hasattr(final.ruleset_, "__len__") else 0,
        p_value_corrected=float("nan"),
        extra={"fold_accs": accs},
    )]


def mine_candidate_rules(
    features_df: pd.DataFrame,
    *,
    target_col: str = "y_buy",
    top_k: int = 10,
) -> list[Candidate]:
    """Run all three miners; return top-K candidates merged + ranked.

    Ranking key: match_rate_cv × coverage (favors rules that fire often AND are accurate).
    """
    if target_col not in features_df.columns:
        raise ValueError(f"missing target column {target_col!r}")
    y = features_df[target_col].astype(int).to_numpy()
    feature_cols = _numeric_feature_columns(features_df)
    if not feature_cols:
        return []

    candidates: list[Candidate] = []
    candidates += _univariate_scan(features_df, y, feature_cols)
    candidates += _decision_tree(features_df, y, feature_cols)
    candidates += _ripper(features_df, y, feature_cols)

    # Always-Buy / Always-Sell baseline (chance level reference).
    base_buy = float(y.mean())
    candidates.append(Candidate(
        rank=99,
        miner="baseline",
        rule_text=f"Always-Buy (y_buy mean = {base_buy:.4f}); Always-Sell = {1 - base_buy:.4f}",
        match_rate_cv=max(base_buy, 1 - base_buy),
        match_rate_std=0.0,
        coverage=1.0,
        n_features=0,
        p_value_corrected=float("nan"),
        extra={"buy_rate": base_buy},
    ))

    candidates.sort(key=lambda c: (-(c.match_rate_cv * (c.coverage ** 0.5)), c.rank))
    out = candidates[:top_k]
    for i, c in enumerate(out, start=1):
        c.rank = i
    return out
