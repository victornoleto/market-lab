"""Monthly DARF 6015 regime (Lei 11033/2004 — pre-Lei-14.754 for renda variável)."""
from __future__ import annotations

import calendar
from datetime import date
from decimal import ROUND_UP, Decimal
from typing import ClassVar

from ops.core.models import DarfEvent, Dividend, Stream, Trade
from ops.core.tax._date_utils import last_business_day_of_month, next_month
from ops.core.tax.base import TaxRegime


class MonthlyLei11033Regime(TaxRegime):
    name: ClassVar[str] = "monthly_6015"
    darf_code_default: ClassVar[str] = "6015"
    streams: ClassVar[tuple[Stream, ...]] = ("swing", "daytrade")

    def period_for(self, d: date) -> tuple[date, date]:
        _, last = calendar.monthrange(d.year, d.month)
        return (date(d.year, d.month, 1), date(d.year, d.month, last))

    def due_date(self, period_end: date) -> date:
        y, m = next_month(period_end)
        return last_business_day_of_month(y, m)

    def period_key(self, period_end: date) -> str:
        return f"{period_end.year:04d}-{period_end.month:02d}"

    def compute(
        self,
        trades: list[Trade],
        dividends: list[Dividend],
        carryforward_in: dict[Stream, Decimal],
        period_start: date,
        period_end: date,
    ) -> list[DarfEvent]:
        events: list[DarfEvent] = []
        due = self.due_date(period_end)
        period_key = self.period_key(period_end)

        for stream_name in ("swing", "daytrade"):
            sells = [
                t for t in trades
                if t.side == "sell"
                and t.trade_type == stream_name
                and period_start <= t.date <= period_end
            ]
            if not sells:
                continue

            gross_gain = sum(
                (t.realized_gain_brl for t in sells),
                start=Decimal("0"),
            )
            # Only positive gross_gain produces DARF; losses accrue to carryforward
            # (handled by caller, not this regime).
            if gross_gain <= Decimal("0"):
                continue

            carry_in = max(Decimal("0"), carryforward_in.get(stream_name, Decimal("0")))
            loss_offset = min(carry_in, gross_gain)
            net_taxable = gross_gain - loss_offset
            rate = Decimal("0.15") if stream_name == "swing" else Decimal("0.20")
            tax_due = (net_taxable * rate).quantize(Decimal("0.01"), rounding=ROUND_UP)

            # Zero-tax → no DARF emitted. Carryforward consumption is tracked by caller
            # via carryforward.csv; the underlying realization is still in trades.csv.
            if tax_due <= Decimal("0"):
                continue

            code = "6015" if stream_name == "swing" else "8523"
            darf_id = f"DARF-M-{period_key.replace('-', '')}-{stream_name[:2].upper()}"

            events.append(
                DarfEvent(
                    darf_id=darf_id,
                    regime="monthly_6015",
                    period_start=period_start,
                    period_end=period_end,
                    due_date=due,
                    code=code,
                    stream=stream_name,
                    gross_gain_brl=gross_gain,
                    dividends_brl=Decimal("0"),
                    loss_offset_brl=loss_offset,
                    net_taxable_brl=net_taxable,
                    tax_rate_applied=rate,
                    tax_due_brl=tax_due,
                )
            )
        return events
