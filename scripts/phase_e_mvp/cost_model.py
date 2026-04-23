"""Multi-market cost + tax model for Strategy E.

Dispatch per ticker market:

* **BR** tickers reuse :func:`~ai_trade.backtest.costs.br_cost_model.monthly_tax`
  (R$20k/mo exempt conditional + 15% DARF).
* **US** tickers pay BR capital-gains tax via **Banco Inter Internacional
  rota B** — 15% DARF on realized monthly net gain (no exemption ceiling).
  This matches mandate §4 Strategy B convention for US-listed equity.

Transaction costs:

* BR: ``br_cost_model.transaction_cost`` — spread 15-50 bps + emolumentos
  0.025% + R$0 corretagem (Clear/Nubank default).
* US: uniform 1-5 bps half-spread for SP500 top-200 + $0 commission
  (Robinhood/IBKR Pro zero-commission equity). Conservative 3 bps used here.

Monthly tax is applied post-hoc to the equity curve in the same way as
``phase_d_mvp.run_single.apply_monthly_tax``, but the exemption check is
per-market:

* R$20k exemption only applies to BR sells (Brazilian legal regime).
* US sells always contribute 15% on their monthly pnl (rota Inter).

Implementation: compute tax separately for each market inside the month
then sum.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Literal

from ai_trade.backtest.costs.br_cost_model import (
    BRCostConfig,
    Sell,
    TaxConfig,
    monthly_tax as _br_monthly_tax,
    transaction_cost as _br_transaction_cost,
)
from scripts.phase_e_mvp.universe import market_of


@dataclass(frozen=True)
class USCostConfig:
    """US equity costs — Banco Inter Internacional (rota B) convention.

    Attributes
    ----------
    commission_per_side
        USD commission per fill. Default 0 (Robinhood / IBKR Pro Tier-1).
    spread_bps
        Uniform half-spread for SP500 top-200 (tighter than IBrX). 3 bps
        is conservative; real SPY/AAPL is 1-2 bps.
    fx_spread_bps
        One-way FX conversion for USD→BRL repatriation. Default 100 bps
        (Inter Internacional 2026 retail tier). NOT charged per-trade;
        applied post-hoc to realized gains at month-end.
    """

    commission_per_side: float = 0.0
    spread_bps: float = 3.0
    fx_spread_bps: float = 100.0


@dataclass(frozen=True)
class USTaxConfig:
    """BR tax on US equity realized gains — rota Inter Internacional."""

    rate: float = 0.15  # 15% DARF per mandate §4.6


# ---------------------------------------------------------------------------
# Transaction cost dispatch
# ---------------------------------------------------------------------------
def transaction_cost(
    ticker: str,
    volume_local_ccy: float,
    side: Literal["buy", "sell"],
    br_config: BRCostConfig | None = None,
    us_config: USCostConfig | None = None,
) -> float:
    """Return per-fill cost in the ticker's local currency.

    BR: R$. US: USD. Caller must convert for equity-curve accounting — the
    Strategy E engine treats a ticker's currency as transparent because
    the equity curve aggregates all positions by BRL-equivalent only at
    tax time (see :func:`monthly_tax_multimarket`).
    """
    market = market_of(ticker)
    if market == "BR":
        return _br_transaction_cost(ticker, volume_local_ccy, side, br_config)
    if market == "US":
        cfg = us_config or USCostConfig()
        if volume_local_ccy <= 0:
            return 0.0
        half_spread = volume_local_ccy * cfg.spread_bps / 10_000.0 / 2.0
        return cfg.commission_per_side + half_spread
    # Unknown — behave as BR conservative fallback
    return _br_transaction_cost(ticker, volume_local_ccy, side, br_config)


# ---------------------------------------------------------------------------
# Monthly tax multi-market
# ---------------------------------------------------------------------------
def monthly_tax_multimarket(
    br_sells: list[Sell],
    br_pnl: float,
    us_pnl: float,
    br_tax_config: TaxConfig | None = None,
    us_tax_config: USTaxConfig | None = None,
) -> float:
    """Total monthly tax (R$) across both markets.

    BR gets the R$20k exemption check. US gets unconditional 15% on
    positive pnl. Losses carry forward implicitly (negative pnl returns 0
    and the caller tracks the credit).

    Note on FX: ``us_pnl`` is assumed already in BRL-equivalent at the
    realization date. The Strategy E engine handles the USD↔BRL
    conversion at fill-time (we ignore timing risk for the MVP; in
    production the FX lag adds a few basis points).
    """
    br_tax = _br_monthly_tax(br_sells, br_pnl, br_tax_config)
    us_cfg = us_tax_config or USTaxConfig()
    us_tax = max(0.0, us_pnl) * us_cfg.rate
    return br_tax + us_tax


__all__ = [
    "USCostConfig",
    "USTaxConfig",
    "monthly_tax_multimarket",
    "transaction_cost",
]
