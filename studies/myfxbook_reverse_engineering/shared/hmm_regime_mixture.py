"""HMM regime mixture model — Pipeline v4 Redesign module.

Spec authority: studies/myfxbook_reverse_engineering/v4_redesign/SPEC.md
Task: 021-hmm-regime-mixture em studies/myfxbook_reverse_engineering/v4_redesign/TASKS.md

Citations:
- [machine_trading, ch.4] — HMM (Hidden Markov Model) para deteccao de regime de mercado;
  3 estados (trend / mean-reversion / quiet); gating de regras por regime.

Trilha B4 do SPEC.md: HMM 3-estados.

Interface esperada (task 021):
  HMMRegimeMixture(n_states=3)
  HMMRegimeMixture.fit(trade_history: pd.DataFrame) -> None
  HMMRegimeMixture.classify_trades(trades: pd.DataFrame) -> pd.Series
    -> state per trade: 0=trend, 1=mean_reversion, 2=quiet
  HMMRegimeMixture.train_per_regime(features: pd.DataFrame, labels: pd.Series) -> dict

Aplicar em EAs com taxonomy_gap detectado pelo decoder.
"""
from __future__ import annotations

# TODO(021-hmm-regime-mixture): implementar conforme tasks/021-hmm-regime-mixture.md (detalhar on-demand apos task 019)
