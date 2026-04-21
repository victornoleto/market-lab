"""Adapter interface contract. Every lib-specific adapter implements this."""
from __future__ import annotations

from typing import Protocol

from reports.phase_3_5c.cross_lib.types import RunResult, VariantConfig


class Adapter(Protocol):
    """Common interface for all library adapters."""

    name: str  # "bt", "vectorbt", "backtrader", "quantstats"

    def run(
        self,
        variant: VariantConfig,
        window: tuple[str, str],
        stage: int,
    ) -> RunResult:
        """Run the variant in this library within the given window.

        Returns RunResult with outcome in {OK, SKIPPED, DATA_UNAVAILABLE, ERROR}.
        MUST NOT raise — any exception must be caught and packaged as ERROR.
        """
        ...
