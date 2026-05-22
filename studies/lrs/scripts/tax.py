"""BR annual realized-gain tax model with loss carry-forward (Lei 14.754/2023).

Models the Brazilian individual investor's IR on US-listed ETF capital
gains under the regime introduced by **Lei 14.754/2023**:

* **Article 5°** — fixed 15% rate on annual net gain from
  ``aplicações financeiras no exterior`` (replaces the older progressive
  table and the R$ 35k/month exemption that didn't apply to foreign assets).
* **Article 6°** — losses incurred in one period offset gains in subsequent
  periods **indefinitely** (no 12-month cap, no quarterly netting).

Each ``OFF→ON → ON→OFF`` round-trip realizes a signed gain (positive or
negative). Within a calendar year the signed gains and the running
``loss_carry_forward`` from prior years are summed; if the result is
positive, 15% × net is debited at the first bar of the following year.
If negative, no tax is paid and the unused loss carries into ``loss_carry``
for future years. Open positions at year-end are *not* marked to market
— only closed lots count, matching how DARF anual on aplicações no
exterior actually works.

This is intentionally simpler than
``letf_rotation.simulate_letf_rotation`` (per-switch immediate tax) — for
the lrs scoring framework we want a single annual drag with proper Lei
14.754 carry-forward, not trade-by-trade attribution.

Citations
---------
* Lei 14.754/2023 art. 5° (alíquota 15%): https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14754.htm
* Lei 14.754/2023 art. 6° (compensação de prejuízos, indefinido): same URL.
* Carry-forward implementation precedent:
  ``studies/_shared/tax_engine.py::AnnualDarfEngine`` — rebalance-based
  multi-asset engine that this module mirrors for the binary-rotation
  pattern.
* BR 15% IR overview: ``docs/investment-mandate.md`` §1.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class TaxEvent:
    """One year-end tax settlement record under Lei 14.754 art. 5°/6°."""

    year: int
    realized_gain: float          # signed sum of closed-lot deltas during the year
    loss_carry_in: float          # negative or zero — losses brought forward from prior years
    net_taxable: float            # max(0, realized_gain + loss_carry_in) — the actual tax base
    loss_carry_out: float         # negative or zero — losses left over for future years
    tax_paid: float               # 15% × net_taxable, debited at payment_date
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
    lot_entry_eq_post: float | None = None
    realized_by_year_post: dict[int, float] = {}
    tax_events: list[TaxEvent] = []
    n_switches = 0
    total_tax = 0.0
    loss_carry = 0.0          # ≤ 0; Lei 14.754 art. 6° indefinite carry-forward
    prev_year: int | None = None

    def _settle_year(year_to_settle: int, payment_ts: pd.Timestamp) -> None:
        """Apply art. 6° netting to ``year_to_settle`` and debit tax if any."""
        nonlocal eq_post, total_tax, loss_carry
        gain_post = realized_by_year_post.pop(year_to_settle, 0.0)
        net = gain_post + loss_carry
        if net > 0:
            taxable = net
            loss_carry_out = 0.0
        else:
            taxable = 0.0
            loss_carry_out = net  # ≤ 0, rolls into the next year
        tax = tax_rate * taxable
        eq_before = eq_post
        if tax > 0:
            eq_post -= tax
            total_tax += tax
        if tax > 0 or gain_post != 0.0 or loss_carry != 0.0:
            tax_events.append(TaxEvent(
                year=year_to_settle,
                realized_gain=gain_post,
                loss_carry_in=loss_carry,
                net_taxable=taxable,
                loss_carry_out=loss_carry_out,
                tax_paid=tax,
                payment_date=payment_ts,
                equity_before=eq_before,
                equity_after=eq_post,
            ))
        loss_carry = loss_carry_out

    for i, ts in enumerate(common):
        year = ts.year

        # 1. Year roll-over BEFORE today's transitions/return:
        #    settle tax on whatever was realized strictly in prior years.
        if prev_year is not None and year != prev_year:
            _settle_year(prev_year, ts)

        # 2. Detect exposure transition between i-1 and i.
        was_exposed = exposed[i - 1] if i > 0 else False
        is_exposed = exposed[i]
        if is_exposed and not was_exposed:
            # Opening — entry equity is yesterday's close.
            lot_entry_eq_post = eq_post
            n_switches += 1
        elif not is_exposed and was_exposed:
            # Closing — exit equity is yesterday's close. Attribute to today's year.
            if lot_entry_eq_post is not None:
                realized_by_year_post[year] = (
                    realized_by_year_post.get(year, 0.0) + (eq_post - lot_entry_eq_post)
                )
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

    # End-of-data: settle the trailing year if anything was realized
    # or any loss carry-forward remains pending.
    if prev_year is not None and (prev_year in realized_by_year_post or loss_carry != 0.0):
        _settle_year(prev_year, common[-1])
        post.iloc[-1] = eq_post

    return RotationSimResult(
        equity=post,
        pretax_equity=pretax,
        tax_events=tax_events,
        n_switches=n_switches,
        total_tax_paid=total_tax,
    )
