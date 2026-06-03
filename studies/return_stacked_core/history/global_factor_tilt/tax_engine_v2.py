"""Annual DARF engine — Lei 14.754/2023 (vigente jan/2024).

Replaces DarfCostBasisEngine (monthly model) with the legally-correct
annual model for Brazilian investors holding foreign ETFs via an
international broker (Inter Internacional, etc.).

Key differences vs the old monthly model:
- Tax is assessed ONCE per calendar year (not per trade/month)
- Losses within the same calendar year offset gains (full netting)
- Unused losses carry forward INDEFINITELY (not capped at 12 months)
- No monthly DARF obligation; payment via annual DIRPF declaration

Usage (in a backtest loop):
    engine = AnnualDarfEngine(initial_investment=10_000.0)

    for date, daily_ret in daily_returns.items():
        engine.apply_return(daily_ret)                      # update MtM
        if rebalance_today:
            engine.record_trade(date, gross_gain)           # record realized P&L
        if is_year_end(date):
            engine.year_end_settlement(date.year)           # deduct DARF

    # If simulation ends mid-year, call final settlement:
    engine.year_end_settlement(last_date.year, force=True)

References:
    Lei 14.754/2023 — https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/Lei/L14754.htm
    Banco Inter guide — https://blog.inter.co/ir-investimentos-no-exterior/
    Avenue guide     — https://connection.avenue.us/educacional/tributacao/novas-regras-do-imposto-de-renda-exterior/
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

DARF_RATE = 0.15  # flat 15% — no progressive table under Lei 14.754/2023


class AnnualDarfEngine:
    """DARF anual sobre ganho líquido realizado — Lei 14.754/2023.

    Lifecycle:
      1. Call apply_return(daily_ret) each trading day.
      2. Call record_trade(date, gross_gain) at each rebalance that
         realizes a gain or loss (gross_gain > 0 → gain, < 0 → loss).
      3. Call year_end_settlement(year) on Dec 31 of each year.
         Pass force=True at simulation end for mid-year settlement.

    Attributes:
        port_value        : current portfolio market value
        cost_basis        : total cost of currently held positions
        loss_carryforward : cumulative unrecovered losses (always ≤ 0)
        total_darf_paid   : cumulative DARF paid across all years
        events            : list of settlement event dicts
    """

    def __init__(self, initial_investment: float = 10_000.0) -> None:
        self.port_value: float = initial_investment
        self.cost_basis: float = initial_investment
        self.loss_carryforward: float = 0.0   # ≤ 0; grows more negative with losses
        self.total_darf_paid: float = 0.0
        self._year_trades: dict[int, list[float]] = defaultdict(list)
        self._settled_years: set[int] = set()
        self.events: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Per-day / per-rebalance calls
    # ------------------------------------------------------------------

    def apply_return(self, daily_return: float) -> None:
        """Update port_value for a single day's return. Cost basis unchanged."""
        self.port_value *= (1.0 + daily_return)

    def record_trade(
        self,
        date: Any,
        prev_weights: dict[str, float],
        new_weights: dict[str, float],
    ) -> float:
        """Compute and record realized gross gain/loss for a rebalance.

        Uses portfolio-level average-cost method:
          sold_value = sold_fraction × port_value
          cost_of_sold = sold_fraction × cost_basis
          gross_gain = sold_value − cost_of_sold

        Returns gross_gain (positive = gain, negative = loss).
        Updates cost_basis and records trade in the annual accumulator.
        """
        import pandas as _pd

        year = date.year if hasattr(date, "year") else int(str(date)[:4])

        all_keys = set(prev_weights) | set(new_weights)
        sold_fraction = sum(
            max(0.0, prev_weights.get(k, 0.0) - new_weights.get(k, 0.0))
            for k in all_keys
        )
        bought_fraction = sum(
            max(0.0, new_weights.get(k, 0.0) - prev_weights.get(k, 0.0))
            for k in all_keys
        )

        if sold_fraction < 1e-6:
            return 0.0

        sold_value = sold_fraction * self.port_value
        cost_for_sold = sold_fraction * self.cost_basis
        gross_gain = sold_value - cost_for_sold

        # Record in annual bucket (no tax taken now — deferred to year-end)
        self._year_trades[year].append(gross_gain)

        # Update cost basis
        remaining_cost = self.cost_basis * (1.0 - sold_fraction)
        purchased_value = bought_fraction * self.port_value
        self.cost_basis = remaining_cost + purchased_value

        return gross_gain

    # ------------------------------------------------------------------
    # Year-end settlement
    # ------------------------------------------------------------------

    def year_end_settlement(self, year: int, force: bool = False) -> float:
        """Compute and deduct DARF for the given calendar year.

        Args:
            year : the calendar year to settle (e.g. 2023)
            force: if True, settle even if already settled or no trades

        Returns:
            darf amount deducted from port_value (0.0 if no tax due)
        """
        if year in self._settled_years and not force:
            return 0.0

        annual_gross = sum(self._year_trades.get(year, []))
        taxable = annual_gross + self.loss_carryforward

        if taxable > 0:
            darf = taxable * DARF_RATE
            self.port_value -= darf
            self.total_darf_paid += darf
            self.loss_carryforward = 0.0
        else:
            darf = 0.0
            # Unused loss carries forward indefinitely
            self.loss_carryforward = taxable  # ≤ 0

        self._settled_years.add(year)
        self.events.append({
            "year": year,
            "annual_gross_gain": round(annual_gross, 2),
            "loss_carryforward_in": round(
                self.loss_carryforward - (0 if taxable > 0 else annual_gross), 2
            ),
            "taxable": round(taxable, 2),
            "darf": round(darf, 2),
            "loss_carryforward_out": round(self.loss_carryforward, 2),
            "port_value_after": round(self.port_value, 2),
        })

        return darf

    def settle_all_pending_years(self, up_to_year: int) -> float:
        """Settle all years from first trade year through up_to_year."""
        if not self._year_trades:
            return 0.0
        total = 0.0
        for yr in range(min(self._year_trades), up_to_year + 1):
            total += self.year_end_settlement(yr)
        return total

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @property
    def unrealized_gain(self) -> float:
        return self.port_value - self.cost_basis

    def summary(self) -> dict[str, Any]:
        return {
            "port_value": round(self.port_value, 2),
            "cost_basis": round(self.cost_basis, 2),
            "unrealized_gain": round(self.unrealized_gain, 2),
            "loss_carryforward": round(self.loss_carryforward, 2),
            "total_darf_paid": round(self.total_darf_paid, 2),
            "settled_years": sorted(self._settled_years),
        }
