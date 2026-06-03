"""Net-of-tax layer for spy_beater_hunt — Lei 14.754/2023 (DARF anual).

Wraps :mod:`studies._shared.tax_engine.AnnualDarfEngine` to convert a
gross daily-returns ``pd.Series`` (output of any spy_beater StrategySpec)
into the corresponding net-of-tax series under Brazilian Lei 14.754/2023:

    - Alíquota 15% flat sobre ganho líquido realizado anual (DARF 6015).
    - Apuração anual única (DAA mar/mai); rebalances intra-ano NÃO disparam
      DARF mensal — compostagem preservada dentro do ano calendário.
    - Perdas compensam ganhos dentro do ano; saldo negativo carrega
      indefinidamente.
    - FX (variação cambial) entra no rendimento — modelado como flat PTAX
      neste backtest (pragmático; ver caveat em README).

Tax classification per spec.type
--------------------------------

``static``: buy-and-hold-forever. No mid-period realization; only final
liquidation triggers DARF. Maximum tax-deferral compounding benefit.
Drag is small relative to gross CAGR (one-shot 15% on cumulative gain).

``lrs``, ``vol_target``: annual-realize. We model "sell-rebuy" at each
calendar year-end (Dec 31). Within-year flips/rebalances aggregate to
the year's net realized P&L per Lei 14.754 — so daily/weekly rebal
within a year is fiscally equivalent to a single annual rebalance for
DARF computation. DARF paid each year on year's net gain.

``blend``: annual-realize if any constituent is non-static; else
buy-and-hold. Approximation — a real blend with shared cost basis is
slightly more efficient than independent constituents, but the
difference is below the FX modeling error so we ignore it.

Citations
---------

- Lei 14.754/2023 — https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/Lei/L14754.htm
- ``[advances_fin_ml, p.31-34]`` — separate gross (alpha test) from net
  (deploy readiness); gates evaluate gross, score reports both.
- ``project_plano_b_broker_inter`` (memory) — Inter Internacional via
  Inter&Co Securities FINRA, custody at Apex Clearing; tributação BR via
  Lei 14.754/2023.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from studies._shared.tax_engine import AnnualDarfEngine, DARF_RATE


__all__ = [
    "TaxClassification",
    "classify_for_tax",
    "net_returns_from_spec",
]


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


class TaxClassification:
    """String constants for tax-treatment classification."""

    BUY_HOLD = "buy_hold"           # static: realize only at terminal liquidation
    ANNUAL_REALIZE = "annual_realize"  # lrs/vol_target/blend(non-static): year-end realize


def classify_for_tax(spec: dict) -> str:
    """Return ``TaxClassification.BUY_HOLD`` or ``ANNUAL_REALIZE``.

    Buy-and-hold-forever (BUY_HOLD) — no realization until terminal
    liquidation. Applies to ``type=static``. Maximum tax deferral.

    Annual-realize (ANNUAL_REALIZE) — realize 100% at year-end calendar
    boundary. Applies to ``type=lrs`` (regime flips), ``type=vol_target``
    (continuous rebalance), and ``type=blend`` if any constituent is
    non-static.

    Per Lei 14.754/2023, intra-year flips/rebalances aggregate to the
    year's net realized P&L — so flip-frequency does NOT increase tax
    drag within a year. The drag is entirely a function of "did we
    realize the year's gain or defer it?".
    """
    stype = spec.get("type", "static")
    if stype == "static":
        return TaxClassification.BUY_HOLD
    if stype == "blend":
        for c in spec.get("constituents", []):
            sub = c.get("spec", {})
            if classify_for_tax(sub) == TaxClassification.ANNUAL_REALIZE:
                return TaxClassification.ANNUAL_REALIZE
        return TaxClassification.BUY_HOLD
    # lrs, vol_target, and any future swing-type spec
    return TaxClassification.ANNUAL_REALIZE


# ---------------------------------------------------------------------------
# Year-end detection
# ---------------------------------------------------------------------------


def _is_last_trading_day_of_year(idx: pd.DatetimeIndex) -> list[bool]:
    """Mark the last trading day of each calendar year in a DatetimeIndex."""
    flags = [False] * len(idx)
    for i in range(len(idx)):
        if i + 1 == len(idx) or idx[i + 1].year != idx[i].year:
            flags[i] = True
    return flags


# ---------------------------------------------------------------------------
# Core simulation
# ---------------------------------------------------------------------------


@dataclass
class TaxSummary:
    """Per-dataset tax simulation summary."""

    classification: str
    initial_capital: float
    final_port_gross: float
    final_port_net: float
    total_darf_paid: float
    n_year_end_settlements: int
    terminal_darf: float
    drag_pct_pts: float            # gross_cagr - net_cagr (pp)

    def to_dict(self) -> dict[str, Any]:
        return {
            "classification": self.classification,
            "initial_capital": round(self.initial_capital, 2),
            "final_port_gross": round(self.final_port_gross, 2),
            "final_port_net": round(self.final_port_net, 2),
            "total_darf_paid": round(self.total_darf_paid, 2),
            "n_year_end_settlements": self.n_year_end_settlements,
            "terminal_darf": round(self.terminal_darf, 2),
            "drag_pct_pts": round(self.drag_pct_pts, 4),
            "darf_rate": DARF_RATE,
        }


def net_returns_from_spec(
    spec: dict,
    gross_returns: pd.Series,
    initial_capital: float = 10_000.0,
) -> tuple[pd.Series, TaxSummary]:
    """Convert gross daily returns to net daily returns via Lei 14.754/2023.

    Args:
        spec: StrategySpec used to classify tax behavior (static/lrs/vol_target/blend).
        gross_returns: daily returns Series (DatetimeIndex).
        initial_capital: starting port_value for the simulation (default 10k).

    Returns:
        (net_daily_returns, TaxSummary)

        ``net_daily_returns`` has same DatetimeIndex as ``gross_returns``.
        The DARF deductions are reflected as discrete drops on the
        relevant days (year-ends + terminal liquidation day).
    """
    if gross_returns.empty:
        empty = pd.Series([], dtype=float)
        return empty, TaxSummary(
            classification=classify_for_tax(spec),
            initial_capital=initial_capital,
            final_port_gross=initial_capital,
            final_port_net=initial_capital,
            total_darf_paid=0.0,
            n_year_end_settlements=0,
            terminal_darf=0.0,
            drag_pct_pts=0.0,
        )

    classification = classify_for_tax(spec)
    idx = gross_returns.index
    last_day_of_year = _is_last_trading_day_of_year(idx)
    last_index = len(idx) - 1

    engine = AnnualDarfEngine(initial_investment=initial_capital)

    pv_curve: list[float] = [initial_capital]
    n_year_end = 0
    terminal_darf = 0.0

    # Synthetic weights to drive AnnualDarfEngine.record_trade into a
    # 100%-sold-100%-bought event (sold_fraction == bought_fraction == 1.0).
    SLEEVE_A = {"PORT_A": 1.0}
    SLEEVE_B = {"PORT_B": 1.0}
    CASH = {"CASH": 1.0}
    rebal_toggle = 0  # alternate between A/B so consecutive rebals work

    for i, (date, r) in enumerate(zip(idx, gross_returns.values)):
        engine.apply_return(float(r))

        is_last = i == last_index

        # Annual rebalance event (only for ANNUAL_REALIZE)
        if (
            classification == TaxClassification.ANNUAL_REALIZE
            and last_day_of_year[i]
            and not is_last  # terminal day handled below
        ):
            prev_w = SLEEVE_A if rebal_toggle == 0 else SLEEVE_B
            new_w = SLEEVE_B if rebal_toggle == 0 else SLEEVE_A
            engine.record_trade(date, prev_weights=prev_w, new_weights=new_w)
            rebal_toggle = 1 - rebal_toggle
            engine.year_end_settlement(date.year)
            n_year_end += 1

        # Terminal liquidation (always)
        if is_last:
            prev_w = SLEEVE_A if rebal_toggle == 0 else SLEEVE_B
            engine.record_trade(date, prev_weights=prev_w, new_weights=CASH)
            settled = engine.year_end_settlement(date.year, force=True)
            terminal_darf = settled
            if settled > 0:
                # Count terminal as a settlement only if it actually paid DARF
                # (not a no-op when prior years already settled with no gain)
                pass  # already counted via events list if needed

        pv_curve.append(engine.port_value)

    pv_array = pd.Series(pv_curve, dtype=float)

    # Build net daily returns from net pv curve
    # net_r[t] = pv[t] / pv[t-1] - 1, aligned to same index as gross
    net_pv_at_dates = pv_array.iloc[1:].reset_index(drop=True)
    prev_pv_at_dates = pv_array.iloc[:-1].reset_index(drop=True)
    net_returns_values = (net_pv_at_dates / prev_pv_at_dates - 1.0).values
    net_returns = pd.Series(net_returns_values, index=idx, name=gross_returns.name)

    # Compute drag
    n_years = len(idx) / 252.0
    final_pv_gross = float(initial_capital * (1.0 + gross_returns).prod())
    final_pv_net = float(engine.port_value)
    if n_years > 0 and final_pv_gross > 0 and final_pv_net > 0:
        gross_cagr = (final_pv_gross / initial_capital) ** (1.0 / n_years) - 1.0
        net_cagr = (final_pv_net / initial_capital) ** (1.0 / n_years) - 1.0
        drag = (gross_cagr - net_cagr) * 100.0  # in percentage points
    else:
        drag = 0.0

    summary = TaxSummary(
        classification=classification,
        initial_capital=initial_capital,
        final_port_gross=final_pv_gross,
        final_port_net=final_pv_net,
        total_darf_paid=engine.total_darf_paid,
        n_year_end_settlements=n_year_end,
        terminal_darf=terminal_darf,
        drag_pct_pts=drag,
    )

    return net_returns, summary
