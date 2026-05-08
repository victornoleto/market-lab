"""Cross-asset state features — Pipeline v4 Redesign module.

Spec authority: studies/myfxbook_reverse_engineering/v4_redesign/SPEC.md
Task: 010-cross-asset-features em studies/myfxbook_reverse_engineering/v4_redesign/TASKS.md

Citations:
- [volatility_trading, p.173-177] — HAR-RV (Heterogeneous AutoRegressive Realized Volatility)
  para bucketing de regime de volatilidade; cross-asset state como contexto de entrada.

Trilha A3 do SPEC.md: cross-asset state via cache Tiingo.

Interface esperada (task 010):
  compute_cross_asset_features(candidate_window: pd.DatetimeIndex) -> pd.DataFrame
    -> features: dxy_proxy (UUP), vix, gold_silver_ratio, btc_dominance, us10y,
                 breakeven_inflation
  Source: data/tiingo/ (cache existente, read-only)
"""
from __future__ import annotations

# TODO(010-cross-asset-features): implementar conforme tasks/010-cross-asset-features.md (detalhar on-demand apos task 008)
