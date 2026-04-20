"""Dataclasses for all CSV-backed entities. Immutable (frozen=True)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

Side = Literal["buy", "sell"]
InstrumentType = Literal["etf", "stock", "fii", "bdr", "cfd", "cash"]
InstrumentDomicile = Literal["us", "br", "other"]
TradeType = Literal["swing", "daytrade"]
Stream = Literal["swing", "daytrade", "rendimentos"]
RegimeName = Literal["monthly_6015", "annual_14754"]


@dataclass(frozen=True)
class Trade:
    trade_id: str
    date: date
    broker: str
    account_id: str
    strategy: str
    ticker: str
    instrument_type: InstrumentType
    instrument_domicile: InstrumentDomicile
    side: Side
    qty: Decimal
    price_native: Decimal
    currency: str
    fees_native: Decimal
    ptax_venda: Decimal
    cost_basis_brl: Decimal
    gross_brl: Decimal
    realized_gain_brl: Decimal
    trade_type: TradeType
    notes: str = ""


@dataclass(frozen=True)
class Dividend:
    dividend_id: str
    payment_date: date
    broker: str
    account_id: str
    ticker: str
    gross_usd: Decimal
    withheld_us_tax_usd: Decimal
    net_usd: Decimal
    ptax_venda: Decimal
    gross_brl: Decimal
    withheld_us_tax_brl: Decimal
    net_brl: Decimal
    notes: str = ""


@dataclass(frozen=True)
class FxRate:
    date: date
    ptax_venda: Decimal
    source: str
    fetched_at: datetime


@dataclass(frozen=True)
class BenchmarkPoint:
    date: date
    series_id: str
    value: Decimal
    source: str
    fetched_at: datetime


@dataclass(frozen=True)
class DarfEvent:
    darf_id: str
    regime: RegimeName
    period_start: date
    period_end: date
    due_date: date
    code: str
    stream: Stream
    gross_gain_brl: Decimal
    dividends_brl: Decimal
    loss_offset_brl: Decimal
    net_taxable_brl: Decimal
    tax_rate_applied: Decimal
    tax_due_brl: Decimal
    paid_at: date | None = None
    paid_proof_path: str = ""
    notes: str = ""


@dataclass(frozen=True)
class CarryforwardBalance:
    regime: RegimeName
    stream: Stream
    period: str  # "YYYY-MM" monthly, "YYYY" annual
    balance_in: Decimal
    accrued_this_period: Decimal
    consumed_this_period: Decimal
    balance_out: Decimal


@dataclass(frozen=True)
class Lot:
    """An open buy lot used for FIFO realization."""
    trade_id: str
    date: date
    ticker: str
    qty: Decimal
    cost_basis_brl: Decimal  # for the remaining qty


@dataclass(frozen=True)
class Position:
    broker: str
    account_id: str
    ticker: str
    qty: Decimal
    avg_cost_brl: Decimal
    open_lots: tuple[Lot, ...] = ()
