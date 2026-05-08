"""Meta-labeler (primary + secondary classifier) — Pipeline v4 Redesign module.

Spec authority: studies/myfxbook_reverse_engineering/v4_redesign/SPEC.md
Task: 016-meta-labeler em studies/myfxbook_reverse_engineering/v4_redesign/TASKS.md

Citations:
- [advances_fin_ml, p.84-89] — Meta-labeling: primary classifier (Buy/Sell/None) identifica
  o lado da posicao; secondary classifier (take/skip) filtra apenas os sinais do primary.
  Reduz false positives sem alterar o lado da aposta.

Trilha B2 do SPEC.md: meta-labeling sobre janela bruta.

Interface esperada (task 016):
  MetaLabeler.fit_primary(features: pd.DataFrame, labels: pd.Series) -> None
  MetaLabeler.fit_secondary(features: pd.DataFrame, meta_labels: pd.Series) -> None
  MetaLabeler.predict(features: pd.DataFrame) -> pd.DataFrame
    -> columns: primary_signal (Buy/Sell/None), meta_label (take/skip), confidence

Output: meta_labeled_synthetic_trades.parquet
"""
from __future__ import annotations

# TODO(016-meta-labeler): implementar conforme tasks/016-meta-labeler.md (detalhar on-demand apos task 015)
