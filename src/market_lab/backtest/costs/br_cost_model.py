"""Brazilian spot-market cost and tax model for Strategy D.

Two orthogonal concerns live here:

1. **Transaction cost** per fill: brokerage fee + B3 emolumentos + half-spread.
   Broker fee defaults to R$0 (zero-brokerage retailers like Clear, Nubank
   Invest, Rico/XP Easynvest, Inter DTVM). Emolumentos is the B3 public
   0.025% on notional. Spread is asymmetric between IBrX-100 top 30 (~15 bps)
   and smaller constituents (~50 bps).

2. **Monthly tax** on realized gains under art. 3º II Lei 11.033/2004:
   gross monthly sales ≤ R$20,000 → **isento**; > R$20,000 → 15% over the
   month's realized *positive* P&L. This is the core economic reason
   Strategy D exists as a slot separate from Strategy B (Inter, which
   pays 15% DARF unconditionally on foreign ETF gains).

This module is **pure** — no I/O, no Portfolio references, no Strategy
subclasses. The backtest engine consumes ``transaction_cost`` per fill and
``monthly_tax`` at each month-end close-of-book. Tests exercise the edge
cases in ``tests/test_br_cost_model.py``.

Citations
---------
- R$20k exemption: art. 3º II Lei 11.033/2004 (Receita Federal IN 1585/2015
  art. 59) — swing-trade spot equity only; excludes day-trade, futures,
  options, FIIs.
- Carry-forward of losses: IN RFB 1585/2015 art. 64 (losses compensable on
  future gains of the same category, no expiry).
- Mandate anchor: ``docs/investment-mandate.md §4b.4``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Literal

_DEFAULT_TOP30: frozenset[str] = frozenset(
    [
        # Top 30 IBrX-100 by market cap 2026-04 (tighter spreads, ~15 bps).
        "PETR4.SA", "PETR3.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA",
        "BBAS3.SA", "B3SA3.SA", "WEGE3.SA", "ABEV3.SA", "ITSA4.SA",
        "SUZB3.SA", "RENT3.SA", "RAIL3.SA", "EQTL3.SA", "PRIO3.SA",
        "UGPA3.SA", "BBSE3.SA", "RDOR3.SA", "HAPV3.SA", "ELET3.SA",
        "ELET6.SA", "KLBN11.SA", "RADL3.SA", "VIVT3.SA", "SBSP3.SA",
        "EMBR3.SA", "CMIG4.SA", "GGBR4.SA", "LREN3.SA", "ASAI3.SA",
    ]
)


@dataclass(frozen=True)
class BRCostConfig:
    """Parameters for per-fill transaction cost.

    Attributes
    ----------
    corretagem_per_side
        R$ flat fee per buy/sell. Default R$0 (zero-brokerage retailers).
        Pass R$5 as conservative sensitivity (XP/Rico non-promo).
    emolumentos_pct
        B3 fee on notional. Public 0.025%.
    spread_bps_top30
        Half-spread in basis points for IBrX-100 top-30 market cap.
    spread_bps_smalls
        Half-spread for other IBrX-100 constituents (smaller float).
    top30_tickers
        Set of tickers that pay the tighter spread. Defaults to the
        hand-curated list above; override for quadrimestral B3 rebalance.
    """

    corretagem_per_side: float = 0.0
    emolumentos_pct: float = 0.00025
    spread_bps_top30: float = 15.0
    spread_bps_smalls: float = 50.0
    top30_tickers: frozenset[str] = field(default_factory=lambda: _DEFAULT_TOP30)


def transaction_cost(
    ticker: str,
    volume_brl: float,
    side: Literal["buy", "sell"],
    config: BRCostConfig | None = None,
) -> float:
    """Return the total R$ cost of executing ``side`` at ``volume_brl``.

    Formula
    -------
        corretagem + emolumentos + half_spread

    where ``half_spread = (spread_bps / 10_000 / 2) × volume_brl`` — we pay
    the bid-ask from the mid, so the one-side cost is half the quoted spread.

    Notes
    -----
    * ``side`` currently doesn't change the cost (buys and sells pay the
      same), but it's threaded through so future asymmetries (e.g.
      settlement-funding drag on long positions) can be added without
      breaking callers.
    * Negative or zero ``volume_brl`` returns 0 cost — strategies should
      filter out zero-size orders before calling this.
    """
    del side  # currently symmetric; kept for API stability
    if volume_brl <= 0:
        return 0.0

    cfg = config or BRCostConfig()
    bps = cfg.spread_bps_top30 if ticker in cfg.top30_tickers else cfg.spread_bps_smalls
    half_spread = volume_brl * bps / 10_000.0 / 2.0
    emol = volume_brl * cfg.emolumentos_pct
    return cfg.corretagem_per_side + emol + half_spread


@dataclass(frozen=True)
class TaxConfig:
    """Parameters for monthly tax computation.

    Attributes
    ----------
    monthly_exemption_brl
        Ceiling on gross monthly sales that keeps the month exempt.
        Default R$20,000 per art. 3º II Lei 11.033/2004.
    swing_rate
        Tax rate applied when exemption is exceeded. Default 15%.
    """

    monthly_exemption_brl: float = 20_000.0
    swing_rate: float = 0.15


@dataclass(frozen=True)
class Sell:
    """One realized sale within a month — the unit of the R$20k count."""

    when: date
    ticker: str
    gross_amount: float  # R$ gross (price × qty), before costs


def monthly_tax(
    sells: list[Sell],
    realized_pnl_brl: float,
    config: TaxConfig | None = None,
) -> float:
    """Return the DARF tax due for a month.

    Parameters
    ----------
    sells
        All sales (swing, spot equity) within the calendar month. Only the
        ``gross_amount`` matters for the exemption check.
    realized_pnl_brl
        Net realized P&L of the month (sum over all sales of
        ``proceeds - cost_basis - transaction_costs``). Negative values
        carry forward per RFB 1585/2015 art. 64 — the caller owns that
        state; this function just returns 0 on losses.

    Returns
    -------
    Tax due in R$ (0 when exempt or when the month is a net loss).

    Rule (Receita Federal / CVM)
    ----------------------------
    * ``sum(gross_amount) ≤ R$20,000`` → exempt, regardless of gain.
    * ``sum(gross_amount) > R$20,000`` → 15% on the FULL positive
      ``realized_pnl_brl`` of the month (not pro-rata beyond the
      threshold — that's a common misconception; the entire month's
      gain is taxed once the ceiling is crossed).
    * Losses (``realized_pnl_brl < 0``) yield 0 tax and should be
      tracked by the caller as a credit against future positive months.
    """
    cfg = config or TaxConfig()
    gross_sales = sum(s.gross_amount for s in sells)
    if gross_sales <= cfg.monthly_exemption_brl:
        return 0.0
    return max(0.0, realized_pnl_brl) * cfg.swing_rate
