"""Tests for MonthlyLei11033Regime (legacy monthly DARF 6015)."""
from datetime import date
from decimal import Decimal

import pytest

from ops.core.models import Dividend, Trade
from ops.core.tax import get_regime


def _make_sell(
    trade_id: str,
    d: date,
    realized_gain_brl: Decimal,
    trade_type: str = "swing",
) -> Trade:
    """Helper: minimal Trade with only the fields the regime reads."""
    return Trade(
        trade_id=trade_id,
        date=d,
        broker="inter_global",
        account_id="acc1",
        strategy="plano_b",
        ticker="SSO",
        instrument_type="etf",
        instrument_domicile="us",
        side="sell",
        qty=Decimal("10"),
        price_native=Decimal("52"),
        currency="USD",
        fees_native=Decimal("0"),
        ptax_venda=Decimal("5"),
        cost_basis_brl=Decimal("2500"),
        gross_brl=Decimal("2600"),
        realized_gain_brl=realized_gain_brl,
        trade_type=trade_type,
    )


def test_period_is_calendar_month():
    r = get_regime("monthly_6015")
    assert r.period_for(date(2026, 4, 15)) == (date(2026, 4, 1), date(2026, 4, 30))
    assert r.period_for(date(2026, 2, 1)) == (date(2026, 2, 1), date(2026, 2, 28))


def test_due_date_last_business_day_of_next_month():
    r = get_regime("monthly_6015")
    # April 2026 ends 2026-04-30 → due last business day of May
    # 2026-05-31 = Sunday → 2026-05-29 (Friday)
    assert r.due_date(date(2026, 4, 30)) == date(2026, 5, 29)


def test_no_trades_no_darfs():
    r = get_regime("monthly_6015")
    events = r.compute([], [], {"swing": Decimal("0"), "daytrade": Decimal("0")},
                       date(2026, 4, 1), date(2026, 4, 30))
    assert events == []


def test_swing_gain_generates_single_darf():
    r = get_regime("monthly_6015")
    trades = [_make_sell("T1", date(2026, 4, 15), Decimal("3200.00"))]
    events = r.compute(
        trades, [],
        {"swing": Decimal("0"), "daytrade": Decimal("0")},
        date(2026, 4, 1), date(2026, 4, 30),
    )
    assert len(events) == 1
    e = events[0]
    assert e.stream == "swing"
    assert e.gross_gain_brl == Decimal("3200.00")
    assert e.loss_offset_brl == Decimal("0")
    assert e.net_taxable_brl == Decimal("3200.00")
    assert e.tax_due_brl == Decimal("480.00")
    assert e.code == "6015"


def test_swing_loss_produces_no_darf_but_accrues_carryforward_signal():
    """Losses do not generate DARFs but caller will track via accrued_carryforward."""
    r = get_regime("monthly_6015")
    trades = [_make_sell("T1", date(2026, 4, 15), Decimal("-500.00"))]
    events = r.compute(
        trades, [],
        {"swing": Decimal("0"), "daytrade": Decimal("0")},
        date(2026, 4, 1), date(2026, 4, 30),
    )
    assert events == []


def test_carryforward_offsets_gain():
    r = get_regime("monthly_6015")
    trades = [_make_sell("T1", date(2026, 5, 10), Decimal("5000.00"))]
    events = r.compute(
        trades, [],
        {"swing": Decimal("2000.00"), "daytrade": Decimal("0")},
        date(2026, 5, 1), date(2026, 5, 31),
    )
    assert len(events) == 1
    e = events[0]
    assert e.gross_gain_brl == Decimal("5000.00")
    assert e.loss_offset_brl == Decimal("2000.00")
    assert e.net_taxable_brl == Decimal("3000.00")
    assert e.tax_due_brl == Decimal("450.00")


def test_carryforward_larger_than_gain_zero_tax():
    r = get_regime("monthly_6015")
    trades = [_make_sell("T1", date(2026, 5, 10), Decimal("1000.00"))]
    events = r.compute(
        trades, [],
        {"swing": Decimal("2500.00"), "daytrade": Decimal("0")},
        date(2026, 5, 1), date(2026, 5, 31),
    )
    assert len(events) == 1
    e = events[0]
    assert e.loss_offset_brl == Decimal("1000.00")  # only consume up to gain
    assert e.net_taxable_brl == Decimal("0")
    assert e.tax_due_brl == Decimal("0")


def test_swing_and_daytrade_produce_separate_darfs():
    r = get_regime("monthly_6015")
    trades = [
        _make_sell("T1", date(2026, 4, 15), Decimal("1000"), trade_type="swing"),
        _make_sell("T2", date(2026, 4, 20), Decimal("500"), trade_type="daytrade"),
    ]
    events = r.compute(
        trades, [],
        {"swing": Decimal("0"), "daytrade": Decimal("0")},
        date(2026, 4, 1), date(2026, 4, 30),
    )
    assert len(events) == 2
    streams = sorted(e.stream for e in events)
    assert streams == ["daytrade", "swing"]


def test_dividends_not_in_monthly_stream():
    """Monthly regime: dividends are separate Carnê-Leão, not in DARF."""
    r = get_regime("monthly_6015")
    div = Dividend(
        dividend_id="D1",
        payment_date=date(2026, 4, 15),
        broker="inter_global",
        account_id="acc1",
        ticker="SSO",
        gross_usd=Decimal("10"),
        withheld_us_tax_usd=Decimal("3"),
        net_usd=Decimal("7"),
        ptax_venda=Decimal("5"),
        gross_brl=Decimal("50"),
        withheld_us_tax_brl=Decimal("15"),
        net_brl=Decimal("35"),
    )
    events = r.compute(
        [], [div],
        {"swing": Decimal("0"), "daytrade": Decimal("0")},
        date(2026, 4, 1), date(2026, 4, 30),
    )
    assert events == []  # dividends ignored by monthly
