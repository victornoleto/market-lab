"""LightGBM rule miner (purged-CV) — Pipeline v4 Redesign module.

Spec authority: studies/myfxbook_reverse_engineering/v4_redesign/SPEC.md
Task: 015-lightgbm-miner em studies/myfxbook_reverse_engineering/v4_redesign/TASKS.md

Citations:
- [advances_fin_ml, ch.5] — LightGBM com purged k-fold CV + embargo; permutation importance;
  monotonic constraints para regras interpretaveis. Substitui univariate+tree+RIPPER como
  minerador de regras candidatas.

Trilha B1 do SPEC.md: LightGBM purged-CV.

Interface esperada (task 015):
  LightGBMMiner.fit(features: pd.DataFrame, labels: pd.Series,
                    embargo_pct: float = 0.01) -> None
  LightGBMMiner.top_rules(n: int = 20) -> list[dict]
    -> cada regra: {"feature": str, "threshold": float, "direction": str, "importance": float}
  LightGBMMiner.predict_proba(features: pd.DataFrame) -> np.ndarray

Mantém miners antigos (univariate, tree, ripper) em decoder_candidates.py como baseline.
"""
from __future__ import annotations

# TODO(015-lightgbm-miner): implementar conforme tasks/015-lightgbm-miner.md (detalhar on-demand apos task 014)
