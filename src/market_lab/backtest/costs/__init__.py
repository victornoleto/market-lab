"""Cost models for backtesting.

Per-strategy cost/tax logic is currently inlined in each
``src/ai_trade/backtest/strategies/<strategy>.py`` module. This package
collects the shared cost-model primitives when a strategy has non-trivial
tax rules that deserve unit testing in isolation.

Strategy D (swing BR ranking mensal) is the first consumer — the Brazilian
R$20k/month exemption + 15% DARF rule is both stateful and non-obvious, so
it lives as a standalone module with its own tests.
"""

from ai_trade.backtest.costs.br_cost_model import (
    BRCostConfig,
    Sell,
    TaxConfig,
    monthly_tax,
    transaction_cost,
)

__all__ = [
    "BRCostConfig",
    "Sell",
    "TaxConfig",
    "monthly_tax",
    "transaction_cost",
]
