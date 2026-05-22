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

import numpy as np
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
    *,
    off_leg_returns: pd.Series | None = None,
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
        Fraction applied to year's net positive realized gain. Default
        0.15 (BR long-term IR on aplicações financeiras no exterior).
    off_leg_returns : pd.Series, optional
        Daily returns of the off-leg asset (e.g. GLDSIM, IEFSIM,
        ZROZSIM). ``None`` (default) means cash with 0% yield, which
        is the phase-0 behavior. When non-None, off-leg appreciation
        also accumulates in equity and its lots are realized at every
        leg transition.

    Returns
    -------
    RotationSimResult
        Post-tax equity curve plus pretax curve, tax-event ledger,
        switch count, and total tax paid.

    Notes
    -----
    Exposure convention: signal at close of ``T`` controls position on
    ``T+1`` (``signal.shift(1) == "ON"``) — no lookahead.

    Lot model (generalised in phase-1): at any moment we hold either the
    on-leg or the off-leg. We start in the off-leg (the first ON-bar
    closes the degenerate off-leg lot and opens the on-leg lot). Each
    leg transition closes the current leg's lot (realising signed gain
    against its entry equity) and opens the new leg's lot at the same
    equity level. Realised gains are attributed to the **calendar year
    of the transition** and settled at the first bar of the following
    year per Lei 14.754 art. 5°/6°.

    The currently-open lot at end-of-data is **not** realised — held
    positions defer tax (matches BR "ganho realizado" doctrine).
    """
    common = signal.index.intersection(asset_returns.index)
    if off_leg_returns is not None:
        common = common.intersection(off_leg_returns.index)
    if len(common) == 0:
        raise ValueError("no overlapping bars between signal, asset_returns, off_leg_returns")

    cash_off_leg = off_leg_returns is None
    sig = signal.reindex(common)
    on_ret = asset_returns.reindex(common).astype(float).fillna(0.0).to_numpy()
    if cash_off_leg:
        off_ret = np.zeros(len(common), dtype=float)
    else:
        off_ret = off_leg_returns.reindex(common).astype(float).fillna(0.0).to_numpy()
    exposed = sig.shift(1).eq("ON").to_numpy(dtype=bool)

    pretax_arr = np.empty(len(common), dtype=float)
    post_arr = np.empty(len(common), dtype=float)

    eq_pre = 1.0
    eq_post = 1.0
    # We start in the off-leg at unit equity. The first ON transition (if any)
    # closes this lot (with whatever off-leg gain has accumulated) and opens
    # the on-leg lot at the same equity level.
    lot_entry_eq_post = 1.0
    is_in_on = False
    realized_by_year_post: dict[int, float] = {}
    tax_events: list[TaxEvent] = []
    n_switches = 0
    total_tax = 0.0
    loss_carry = 0.0          # ≤ 0; Lei 14.754 art. 6° indefinite carry-forward
    prev_year: int | None = None

    def _settle_year(year_to_settle: int, payment_ts: pd.Timestamp) -> None:
        """Apply art. 6° netting to ``year_to_settle`` and debit tax if any.

        Tax-payment model (BR external-cash interpretation): tax is conceptually
        paid from a separate BRL cash account that isn't part of the modelled
        ETF equity. So the debit reduces ``eq_post`` but never reduces the
        on-leg lot's basis — on-leg realised gains at close still reflect
        the pure market move from purchase price to sale price. For non-cash
        off-legs (gold / IEF / ZROZ) we DO reduce the off-leg lot's basis on
        tax debits, because the off-leg position itself is conceptually being
        partially liquidated to pay the tax — otherwise the next off→on
        transition would record a phantom loss equal to the tax debit.
        """
        nonlocal eq_post, total_tax, loss_carry, lot_entry_eq_post
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
            # For non-cash off-leg holds (rare: only when in OFF state at year-end
            # with off_leg_returns provided), adjust the off-leg lot basis so the
            # next off→on transition doesn't register the tax debit as a loss.
            if (not is_in_on) and (not cash_off_leg):
                lot_entry_eq_post -= tax
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

        # 1. Year roll-over BEFORE today's transitions/return.
        if prev_year is not None and year != prev_year:
            _settle_year(prev_year, ts)

        # 2. Detect leg transition between i-1 and i. Close current leg's
        #    lot (realise signed gain), open new leg's lot at same equity.
        #    For cash off-leg (`cash_off_leg=True`) we skip realising the
        #    off-leg "lot" entirely — its basis would be 1:1 with cash so
        #    realised would always equal exactly the year's tax debits
        #    (creating phantom losses that incorrectly offset future gains).
        is_exp = bool(exposed[i])
        if is_exp != is_in_on:
            closing_off_leg_to_on = (is_exp and not is_in_on)
            skip_realize = closing_off_leg_to_on and cash_off_leg
            if not skip_realize:
                realized = eq_post - lot_entry_eq_post
                realized_by_year_post[year] = (
                    realized_by_year_post.get(year, 0.0) + realized
                )
            lot_entry_eq_post = eq_post
            is_in_on = is_exp
            n_switches += 1

        # 3. Apply today's return based on the leg we're currently in.
        r = on_ret[i] if is_in_on else off_ret[i]
        eq_pre *= 1.0 + r
        eq_post *= 1.0 + r

        pretax_arr[i] = eq_pre
        post_arr[i] = eq_post
        prev_year = year

    # End-of-data: settle the trailing year if anything was realised
    # or any loss carry-forward remains pending. (Open lot is NOT realised.)
    if prev_year is not None and (prev_year in realized_by_year_post or loss_carry != 0.0):
        _settle_year(prev_year, common[-1])
        post_arr[-1] = eq_post

    pretax = pd.Series(pretax_arr, index=common)
    post = pd.Series(post_arr, index=common)

    return RotationSimResult(
        equity=post,
        pretax_equity=pretax,
        tax_events=tax_events,
        n_switches=n_switches,
        total_tax_paid=total_tax,
    )
