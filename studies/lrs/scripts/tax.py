"""BR annual realized-gain tax model for binary rotation strategies.

Models the Brazilian individual investor's IR on US-listed ETF capital
gains: each ``OFF→ON → ON→OFF`` round-trip realizes a gain (or loss);
positive gains summed across the calendar year are taxed at 15% and the
tax is debited from equity at the first bar of the next year (or at the
last bar of the data for the trailing open year). Open positions at
year-end are *not* marked to market — only closed lots count, matching
how DARF anual on `ganhos com renda variável` actually works.

This is intentionally simpler than ``letf_rotation.simulate_letf_rotation``
(per-switch immediate tax) — for phase-0 we want a single annual drag, not
trade-by-trade attribution.

Citations
---------
* BR 15% IR on US-listed ETF realized gain: ``docs/investment-mandate.md`` §1.
* Annual tax cadence (DARF anual em março): standard BR Receita Federal
  treatment for `renda variável` on foreign exchanges via Inter
  Internacional / IBKR. Phase-0 simplification: tax paid at the first
  bar of the new calendar year, no carry-forward of losses across years.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class TaxEvent:
    """One year-end tax payment record."""

    year: int
    realized_gain: float          # signed sum of closed-lot deltas in the year (equity units)
    tax_paid: float               # 15% × max(0, realized_gain), debited at payment_date
    payment_date: pd.Timestamp    # first bar of the following calendar year (or last bar of data)
    equity_before: float
    equity_after: float


@dataclass(frozen=True)
class RotationSimResult:
    """Output of :func:`simulate_rotation_with_annual_tax`."""

    equity: pd.Series              # post-tax equity, starts at 1.0
    pretax_equity: pd.Series       # pre-tax equity for comparison, starts at 1.0
    tax_events: list[TaxEvent]
    n_switches: int                # number of regime changes on the exposure timeline (open+close pairs counted as 2)
    total_tax_paid: float          # cumulative equity-units debited as tax


def simulate_rotation_with_annual_tax(
    asset_returns: pd.Series,
    signal: pd.Series,
    tax_rate: float = 0.15,
) -> RotationSimResult:
    """Compound a 2-state rotation with BR-style annual realized-gain tax.

    Parameters
    ----------
    asset_returns : pd.Series
        Daily returns of the on-leg asset (e.g. SSO).
    signal : pd.Series
        Object-dtype series of ``"ON"``/``"OFF"``/NaN. Aligned with
        ``asset_returns`` by intersection.
    tax_rate : float
        Fraction applied to year's positive realized gain. Default 0.15
        (BR long-term IR on US-listed ETF capital gain).

    Returns
    -------
    RotationSimResult
        Post-tax equity curve plus pretax curve, tax-event ledger,
        switch count, and total tax paid.

    Notes
    -----
    Exposure convention: signal at close of ``T`` controls position on
    ``T+1`` (``signal.shift(1) == "ON"``) — no lookahead. A lot opens on
    the first bar where exposure flips ``False → True`` (entry equity =
    equity at close of the previous bar, since today's return has not
    yet been applied). The lot closes on the first bar where exposure
    flips ``True → False`` (exit equity = same — yesterday's close,
    since today's return is zero on cash). Realized gain is attributed
    to the year of the bar where the close transition is detected.
    """
    common = signal.index.intersection(asset_returns.index)
    sig = signal.reindex(common)
    rets = asset_returns.reindex(common).astype(float).fillna(0.0)
    exposed = sig.shift(1).eq("ON").to_numpy(dtype=bool)

    pretax = pd.Series(index=common, dtype=float)
    post = pd.Series(index=common, dtype=float)

    eq_pre = 1.0
    eq_post = 1.0
    lot_entry_eq_pre: float | None = None
    lot_entry_eq_post: float | None = None
    realized_by_year_post: dict[int, float] = {}
    realized_by_year_pre: dict[int, float] = {}
    tax_events: list[TaxEvent] = []
    n_switches = 0
    total_tax = 0.0
    prev_year: int | None = None

    for i, ts in enumerate(common):
        year = ts.year

        # 1. Year roll-over BEFORE today's transitions/return:
        #    settle tax on whatever was realized strictly in prior years.
        if prev_year is not None and year != prev_year:
            gain_post = realized_by_year_post.pop(prev_year, 0.0)
            realized_by_year_pre.pop(prev_year, 0.0)
            tax = tax_rate * max(0.0, gain_post)
            if tax > 0:
                eq_before = eq_post
                eq_post -= tax
                total_tax += tax
                tax_events.append(TaxEvent(
                    year=prev_year,
                    realized_gain=gain_post,
                    tax_paid=tax,
                    payment_date=ts,
                    equity_before=eq_before,
                    equity_after=eq_post,
                ))

        # 2. Detect exposure transition between i-1 and i.
        was_exposed = exposed[i - 1] if i > 0 else False
        is_exposed = exposed[i]
        if is_exposed and not was_exposed:
            # Opening — entry equity is yesterday's close.
            lot_entry_eq_pre = eq_pre
            lot_entry_eq_post = eq_post
            n_switches += 1
        elif not is_exposed and was_exposed:
            # Closing — exit equity is yesterday's close. Attribute to today's year.
            if lot_entry_eq_pre is not None and lot_entry_eq_post is not None:
                realized_by_year_pre[year] = (
                    realized_by_year_pre.get(year, 0.0) + (eq_pre - lot_entry_eq_pre)
                )
                realized_by_year_post[year] = (
                    realized_by_year_post.get(year, 0.0) + (eq_post - lot_entry_eq_post)
                )
                lot_entry_eq_pre = None
                lot_entry_eq_post = None
            n_switches += 1

        # 3. Apply today's return if exposed.
        if is_exposed:
            r = rets.iloc[i]
            eq_pre *= 1.0 + r
            eq_post *= 1.0 + r

        pretax.iloc[i] = eq_pre
        post.iloc[i] = eq_post
        prev_year = year

    # End-of-data: settle the trailing year if anything was realized.
    if prev_year is not None and prev_year in realized_by_year_post:
        gain_post = realized_by_year_post.pop(prev_year, 0.0)
        realized_by_year_pre.pop(prev_year, 0.0)
        tax = tax_rate * max(0.0, gain_post)
        if tax > 0:
            eq_before = eq_post
            eq_post -= tax
            total_tax += tax
            post.iloc[-1] = eq_post
            tax_events.append(TaxEvent(
                year=prev_year,
                realized_gain=gain_post,
                tax_paid=tax,
                payment_date=common[-1],
                equity_before=eq_before,
                equity_after=eq_post,
            ))

    return RotationSimResult(
        equity=post,
        pretax_equity=pretax,
        tax_events=tax_events,
        n_switches=n_switches,
        total_tax_paid=total_tax,
    )
