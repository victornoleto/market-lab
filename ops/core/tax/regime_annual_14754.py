"""Annual regime Lei 14.754/2023 — unified rendimentos bucket, DARF code 0211."""
from __future__ import annotations

from datetime import date
from decimal import ROUND_UP, Decimal
from typing import ClassVar

from ops.core.models import DarfEvent, Dividend, Stream, Trade
from ops.core.tax._date_utils import last_business_day_of_month
from ops.core.tax.base import TaxRegime


class AnnualLei14754Regime(TaxRegime):
    name: ClassVar[str] = "annual_14754"
    darf_code_default: ClassVar[str] = "0211"
    streams: ClassVar[tuple[Stream, ...]] = ("rendimentos",)

    def period_for(self, d: date) -> tuple[date, date]:
        return (date(d.year, 1, 1), date(d.year, 12, 31))

    def due_date(self, period_end: date) -> date:
        # IRPF deadline: last business day of April of following year
        return last_business_day_of_month(period_end.year + 1, 4)

    def period_key(self, period_end: date) -> str:
        return f"{period_end.year:04d}"

    def compute(
        self,
        trades: list[Trade],
        dividends: list[Dividend],
        carryforward_in: dict[Stream, Decimal],
        period_start: date,
        period_end: date,
    ) -> list[DarfEvent]:
        sells = [
            t for t in trades
            if t.side == "sell" and period_start <= t.date <= period_end
        ]
        gross_gain = sum(
            (t.realized_gain_brl for t in sells),
            start=Decimal("0"),
        )
        divs_in_period = [
            d for d in dividends
            if period_start <= d.payment_date <= period_end
        ]
        dividends_brl = sum(
            (d.gross_brl for d in divs_in_period),
            start=Decimal("0"),
        )

        net_rendimentos = gross_gain + dividends_brl
        if net_rendimentos <= Decimal("0"):
            return []  # net loss year — all accrues to carryforward (caller handles)

        carry_in = max(Decimal("0"), carryforward_in.get("rendimentos", Decimal("0")))
        loss_offset = min(carry_in, net_rendimentos)
        net_taxable = net_rendimentos - loss_offset
        rate = Decimal("0.15")
        tax_due = (net_taxable * rate).quantize(Decimal("0.01"), rounding=ROUND_UP)

        # Zero-tax → no DARF emitted (consistent with monthly regime convention).
        if tax_due <= Decimal("0"):
            return []

        # darf_id unique per year; assumes caller uses period_for() (full calendar year).
        return [
            DarfEvent(
                darf_id=f"DARF-A-{period_end.year}-REND",
                regime="annual_14754",
                period_start=period_start,
                period_end=period_end,
                due_date=self.due_date(period_end),
                code=self.darf_code_default,
                stream="rendimentos",
                gross_gain_brl=gross_gain,
                dividends_brl=dividends_brl,
                loss_offset_brl=loss_offset,
                net_taxable_brl=net_taxable,
                tax_rate_applied=rate,
                tax_due_brl=tax_due,
            )
        ]
