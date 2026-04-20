"""TaxRegime abstract base + factory."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import ClassVar

from ops.core.models import DarfEvent, Dividend, Stream, Trade


class TaxRegime(ABC):
    name: ClassVar[str]
    darf_code_default: ClassVar[str]
    streams: ClassVar[tuple[Stream, ...]]

    @abstractmethod
    def period_for(self, d: date) -> tuple[date, date]:
        """Return (period_start, period_end) containing d."""

    @abstractmethod
    def due_date(self, period_end: date) -> date:
        """Last business day after period_end when DARF is due."""

    @abstractmethod
    def period_key(self, period_end: date) -> str:
        """String key for carryforward lookups ('YYYY-MM' or 'YYYY')."""

    @abstractmethod
    def compute(
        self,
        trades: list[Trade],
        dividends: list[Dividend],
        carryforward_in: dict[Stream, Decimal],
        period_start: date,
        period_end: date,
    ) -> list[DarfEvent]:
        """Compute 0-N DarfEvents for period; consumes carryforward_in."""
