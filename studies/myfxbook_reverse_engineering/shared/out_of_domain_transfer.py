"""Out-of-domain transfer validator — Pipeline v4 Redesign module.

Spec authority: studies/myfxbook_reverse_engineering/v4_redesign/SPEC.md
Task: 022-out-of-domain-transfer em studies/myfxbook_reverse_engineering/v4_redesign/TASKS.md

Citations:
- [testing_tuning, p.148-162] — walk-forward com purge+embargo; generalizacao fora do dominio
  de treino; validacao de transferencia entre universos distintos (in-domain vs out-of-domain).

Trilha C5 do SPEC.md: out-of-domain validation (EUR train → JPY test).

Interface esperada (task 022):
  OutOfDomainTransfer.fit(in_domain_features: pd.DataFrame, labels: pd.Series,
                          pairs: list[str]) -> None
  OutOfDomainTransfer.transfer_score(out_domain_features: pd.DataFrame,
                                     labels: pd.Series) -> dict[str, float]
    -> {"sharpe_in_domain": float, "sharpe_out_domain": float, "transfer_ratio": float}

Gate: transfer_ratio >= 0.50 (Sharpe OOS >= 50% Sharpe in-domain).
Output: transfer_score registrado em pipeline_summary.json.
"""
from __future__ import annotations

# TODO(022-out-of-domain-transfer): implementar conforme tasks/022-out-of-domain-transfer.md (detalhar on-demand apos task 020)
