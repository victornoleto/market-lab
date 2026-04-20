"""Tests for AnnualLei14754Regime (Lei 14.754/2023 — unified annual rendimentos)."""
from datetime import date
from decimal import Decimal

from ops.core.models import Dividend, Trade
from ops.core.tax import get_regime


def _sell(d: date, gain: Decimal) -> Trade:
    return Trade(
        trade_id=f"T-{d.isoformat()}", date=d, broker="inter_global",
        account_id="acc1", strategy="plano_b", ticker="SSO",
        instrument_type="etf", instrument_domicile="us", side="sell",
        qty=Decimal("10"), price_native=Decimal("52"), currency="USD",
        fees_native=Decimal("0"), ptax_venda=Decimal("5"),
        cost_basis_brl=Decimal("2500"), gross_brl=Decimal("2600"),
        realized_gain_brl=gain, trade_type="swing",
    )


def _div(d: date, gross_brl: Decimal) -> Dividend:
    return Dividend(
        dividend_id=f"D-{d.isoformat()}", payment_date=d, broker="inter_global",
        account_id="acc1", ticker="SSO", gross_usd=gross_brl / Decimal("5"),
        withheld_us_tax_usd=(gross_brl / Decimal("5")) * Decimal("0.30"),
        net_usd=(gross_brl / Decimal("5")) * Decimal("0.70"),
        ptax_venda=Decimal("5"), gross_brl=gross_brl,
        withheld_us_tax_brl=gross_brl * Decimal("0.30"),
        net_brl=gross_brl * Decimal("0.70"),
    )


def test_period_is_calendar_year():
    r = get_regime("annual_14754")
    assert r.period_for(date(2026, 4, 15)) == (date(2026, 1, 1), date(2026, 12, 31))


def test_due_date_last_business_day_april_following_year():
    r = get_regime("annual_14754")
    # 2026 year → due 2027-04-30
    # 2027-04-30 = Friday → that's the due
    assert r.due_date(date(2026, 12, 31)) == date(2027, 4, 30)


def test_gains_and_dividends_unified_into_single_darf():
    r = get_regime("annual_14754")
    trades = [_sell(date(2026, 4, 15), Decimal("3000"))]
    divs = [_div(date(2026, 6, 15), Decimal("500"))]
    events = r.compute(
        trades, divs,
        {"rendimentos": Decimal("0")},
        date(2026, 1, 1), date(2026, 12, 31),
    )
    assert len(events) == 1
    e = events[0]
    assert e.stream == "rendimentos"
    assert e.gross_gain_brl == Decimal("3000")
    assert e.dividends_brl == Decimal("500")
    assert e.net_taxable_brl == Decimal("3500")
    assert e.tax_due_brl == Decimal("525.00")


def test_carryforward_unlimited_between_years():
    r = get_regime("annual_14754")
    trades = [_sell(date(2026, 5, 10), Decimal("5000"))]
    events = r.compute(
        trades, [],
        {"rendimentos": Decimal("2000")},
        date(2026, 1, 1), date(2026, 12, 31),
    )
    assert len(events) == 1
    assert events[0].loss_offset_brl == Decimal("2000")
    assert events[0].net_taxable_brl == Decimal("3000")


def test_only_dividends_no_gains_still_darf():
    r = get_regime("annual_14754")
    divs = [_div(date(2026, 6, 15), Decimal("1000"))]
    events = r.compute(
        [], divs,
        {"rendimentos": Decimal("0")},
        date(2026, 1, 1), date(2026, 12, 31),
    )
    assert len(events) == 1
    assert events[0].gross_gain_brl == Decimal("0")
    assert events[0].dividends_brl == Decimal("1000")
    assert events[0].net_taxable_brl == Decimal("1000")


def test_net_loss_no_darf():
    r = get_regime("annual_14754")
    trades = [_sell(date(2026, 5, 10), Decimal("-500"))]
    events = r.compute(
        trades, [],
        {"rendimentos": Decimal("0")},
        date(2026, 1, 1), date(2026, 12, 31),
    )
    assert events == []


def test_negative_gain_offset_by_dividends_still_net_positive_emits_darf():
    """gain=-500 + dividends=+700 → net_rendimentos=+200 → DARF R$ 30."""
    r = get_regime("annual_14754")
    trades = [_sell(date(2026, 5, 10), Decimal("-500"))]
    divs = [_div(date(2026, 6, 15), Decimal("700"))]
    events = r.compute(
        trades, divs,
        {"rendimentos": Decimal("0")},
        date(2026, 1, 1), date(2026, 12, 31),
    )
    assert len(events) == 1
    e = events[0]
    assert e.gross_gain_brl == Decimal("-500")
    assert e.dividends_brl == Decimal("700")
    assert e.net_taxable_brl == Decimal("200")
    assert e.tax_due_brl == Decimal("30.00")


def test_negative_carry_clamped_to_zero_never_overcharges():
    """Malformed carry_in (negative) must NOT become an overcharge."""
    r = get_regime("annual_14754")
    trades = [_sell(date(2026, 5, 10), Decimal("1000"))]
    events = r.compute(
        trades, [],
        {"rendimentos": Decimal("-200")},  # BUG scenario upstream
        date(2026, 1, 1), date(2026, 12, 31),
    )
    assert len(events) == 1
    e = events[0]
    assert e.loss_offset_brl == Decimal("0")   # clamped, not -200
    assert e.net_taxable_brl == Decimal("1000")  # not 1200
    assert e.tax_due_brl == Decimal("150.00")    # not 180
