"""Signal quality score (consolidated) — Pipeline v4 Redesign module.

Spec authority: studies/myfxbook_reverse_engineering/v4_redesign/SPEC.md
Task: 025-signal-score-consolidated em studies/myfxbook_reverse_engineering/v4_redesign/TASKS.md

Citations:
- [advances_fin_ml, p.196-211] — bet sizing e scoring de sinais; combinacao ponderada de
  metricas de qualidade para ranking de candidatos; Kelly fraction como peso base.

Trilha C3 / Fase 3b: signal quality score para filter-and-copy.

Interface esperada (task 025):
  compute_signal_quality_score(
      pbo: float,
      dsr_p: float,
      mcpt_p: float,
      adversarial_auc: float,
      concentration_ratio: float,
  ) -> float
    -> signal_quality_score normalizado [0, 1]; maior = melhor candidate para copy-trading

Output: ranking top-3 EAs por signal_quality_score.
"""
from __future__ import annotations

# TODO(025-signal-score-consolidated): implementar conforme tasks/025-signal-score-consolidated.md (detalhar on-demand apos task 019)
