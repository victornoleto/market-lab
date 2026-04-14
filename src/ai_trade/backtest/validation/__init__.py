"""ai_trade.backtest.validation — anti-overfit framework.

Seven-layer gate from the ai-trade roadmap §"Fase 3 — Backtest rigoroso":

* :mod:`cpcv` — Purged K-Fold + Combinatorial Purged Cross-Validation
  (AFML ch.7 p.149-154, ch.12 p.219-222)
* :mod:`pbo` — Probability of Backtest Overfitting via CSCV
  (AFML ch.11 p.208-211; Masters ``CSCV_MKT/CSCV_CORE.CPP``)
* :mod:`dsr` — Deflated Sharpe Ratio (AFML ch.14 p.273-275)
* :mod:`walk_forward` — sliding IS/OOS window splits (Pardo, Kaufman, Masters)
* :mod:`permutation` — Monte Carlo Permutation Tests
  (Masters ``MCPT_TRN/MCPT_TRN.CPP``)
"""

from ai_trade.backtest.validation.cpcv import (
    cpcv_path_count,
    cpcv_splits,
    purged_kfold_splits,
)
from ai_trade.backtest.validation.dsr import (
    DSRResult,
    dsr,
    expected_max_sharpe,
    psr,
    sharpe_annualized,
    sharpe_periodic,
)
from ai_trade.backtest.validation.pbo import PBOResult, pbo, pbo_gate
from ai_trade.backtest.validation.permutation import (
    MCPTResult,
    monte_carlo_permutation_test,
    permute_prices,
)
from ai_trade.backtest.validation.walk_forward import (
    walk_forward_gate,
    walk_forward_splits,
)

__all__ = [
    "cpcv_path_count",
    "cpcv_splits",
    "purged_kfold_splits",
    "pbo",
    "pbo_gate",
    "PBOResult",
    "dsr",
    "DSRResult",
    "expected_max_sharpe",
    "psr",
    "sharpe_annualized",
    "sharpe_periodic",
    "walk_forward_gate",
    "walk_forward_splits",
    "monte_carlo_permutation_test",
    "permute_prices",
    "MCPTResult",
]
