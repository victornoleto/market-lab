"""Transformer encoder (small) — Pipeline v4 Redesign module.

Spec authority: studies/myfxbook_reverse_engineering/v4_redesign/SPEC.md
Task: 020-transformer-encoder em studies/myfxbook_reverse_engineering/v4_redesign/TASKS.md

Citations:
- [advances_fin_ml, ch.5] — purged k-fold CV + embargo para treino de modelos de ML em series
  temporais financeiras; evitar leakage de informacao.
- [advances_fin_ml, ch.7] — feature engineering para ML em financas; representacao de janela
  temporal de bars.

Trilha B3 do SPEC.md: Transformer encoder pequeno (4 layers, 64 dim).

Interface esperada (task 020):
  TransformerEncoder(n_layers=4, d_model=64, n_heads=4, dropout=0.1)
  TransformerEncoder.fit(bar_windows: np.ndarray, labels: np.ndarray,
                         embargo_pct: float = 0.01) -> None
  TransformerEncoder.predict_proba(bar_windows: np.ndarray) -> np.ndarray
    -> P(real entry no bar atual) para janela [-200, 0] bars

Descartado (YAGNI) se nao superar LightGBM por +0.1 AUC.
"""
from __future__ import annotations

# TODO(020-transformer-encoder): implementar conforme tasks/020-transformer-encoder.md (detalhar on-demand apos task 019)
