"""Tax regime factory."""
from __future__ import annotations

from ops.core.tax.base import TaxRegime


def get_regime(name: str) -> TaxRegime:
    if name == "monthly_6015":
        from ops.core.tax.regime_monthly_6015 import MonthlyLei11033Regime
        return MonthlyLei11033Regime()
    if name == "annual_14754":
        from ops.core.tax.regime_annual_14754 import AnnualLei14754Regime
        return AnnualLei14754Regime()
    raise ValueError(f"Unknown regime: {name}")


__all__ = ["TaxRegime", "get_regime"]
