"""Adversarial validator (real-vs-synthetic) — Pipeline v4 Redesign module.

Spec authority: studies/myfxbook_reverse_engineering/v4_redesign/SPEC.md
Task: 005-adversarial-validator em studies/myfxbook_reverse_engineering/v4_redesign/TASKS.md

Citations:
- [advances_fin_ml, ch.5] — LightGBM purged-CV + feature importance; classificador binario
  real-vs-synthetic como metrica de identificabilidade do EA.

Interface esperada (task 005):
  AdversarialValidator.fit(real_trades: pd.DataFrame, synthetic_trades: pd.DataFrame)
  AdversarialValidator.auc() -> float
    -> AUC proxima de 0.5 = sintetico indistinguivel de real (bom)
    -> AUC > 0.9 = sintetico e diferente do real (ruim — EA nao decodificado)

Sanity tests (task 005):
  - Copia exata do real → AUC ≈ 0.5
  - Ruido puro → AUC > 0.9
"""
from __future__ import annotations

# TODO(005-adversarial-validator): implementar conforme tasks/005-adversarial-validator.md
