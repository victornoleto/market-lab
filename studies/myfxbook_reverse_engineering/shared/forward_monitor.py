"""Forward monitor (weekly EA tracking) — Pipeline v4 Redesign module.

Spec authority: studies/myfxbook_reverse_engineering/v4_redesign/SPEC.md
Task: 026-forward-monitor-setup em studies/myfxbook_reverse_engineering/v4_redesign/TASKS.md

Citations:
- [advances_fin_ml, ch.14] — forward testing framework; monitoramento continuo de estrategias
  apos selecao; deteccao precoce de regime shift ou deterioracao de performance.

Trilha C3 / Fase 3b: forward monitor 60d para top-3 EAs.

Interface esperada (task 026):
  ForwardMonitor(system_ids: list[int], data_dir: str)
  ForwardMonitor.run_weekly() -> dict[int, dict]
    -> diff de novos trades vs ultima snapshot por system
  ForwardMonitor.check_regime_drift(system_id: int) -> bool
    -> True se performance estatisticamente diferente do historico

Agendamento via cron/myfxbook_weekly.cron ou loop.sh separado.
Monitor 60d roda em background e nao bloqueia tasks subsequentes.
"""
from __future__ import annotations

# TODO(026-forward-monitor-setup): implementar conforme tasks/026-forward-monitor-setup.md (detalhar on-demand apos task 025)
