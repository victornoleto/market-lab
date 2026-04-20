"""Tests for ops/core/positions.py — FIFO lot matching."""
from datetime import date
from decimal import Decimal

from ops.core.models import Trade
from ops.core import positions, storage


def _buy(tid: str, d: date, qty: Decimal, cost_brl: Decimal) -> Trade:
    return Trade(
        trade_id=tid, date=d, broker="inter_global", account_id="acc1",
        strategy="plano_b", ticker="SSO", instrument_type="etf",
        instrument_domicile="us", side="buy", qty=qty,
        price_native=cost_brl / qty / Decimal("5"),
        currency="USD", fees_native=Decimal("0"), ptax_venda=Decimal("5"),
        cost_basis_brl=cost_brl, gross_brl=cost_brl,
        realized_gain_brl=Decimal("0"), trade_type="swing",
    )


def _sell(tid: str, d: date, qty: Decimal, gross_brl: Decimal, gain_brl: Decimal) -> Trade:
    return Trade(
        trade_id=tid, date=d, broker="inter_global", account_id="acc1",
        strategy="plano_b", ticker="SSO", instrument_type="etf",
        instrument_domicile="us", side="sell", qty=qty,
        price_native=gross_brl / qty / Decimal("5"),
        currency="USD", fees_native=Decimal("0"), ptax_venda=Decimal("5"),
        cost_basis_brl=Decimal("0"), gross_brl=gross_brl,
        realized_gain_brl=gain_brl, trade_type="swing",
    )


def test_no_trades_no_positions(tmp_data_dir):
    assert positions.current_positions() == []


def test_single_buy_yields_one_lot(tmp_data_dir):
    storage.append_trade(_buy("T1", date(2026, 4, 1), Decimal("10"), Decimal("2500")))
    pos = positions.current_positions()
    assert len(pos) == 1
    assert pos[0].ticker == "SSO"
    assert pos[0].qty == Decimal("10")
    assert pos[0].avg_cost_brl == Decimal("250")
    assert len(pos[0].open_lots) == 1


def test_partial_sell_fifo_consumes_oldest_lot(tmp_data_dir):
    storage.append_trade(_buy("B1", date(2026, 4, 1), Decimal("10"), Decimal("2500")))
    storage.append_trade(_buy("B2", date(2026, 4, 10), Decimal("10"), Decimal("3000")))
    storage.append_trade(_sell("S1", date(2026, 4, 20), Decimal("5"),
                               Decimal("1400"), Decimal("150")))
    pos = positions.current_positions()
    assert len(pos) == 1
    assert pos[0].qty == Decimal("15")
    # FIFO: B1 had 10, sold 5 → 5 remain from B1, 10 from B2
    assert len(pos[0].open_lots) == 2
    assert pos[0].open_lots[0].trade_id == "B1"
    assert pos[0].open_lots[0].qty == Decimal("5")
    assert pos[0].open_lots[1].trade_id == "B2"
    assert pos[0].open_lots[1].qty == Decimal("10")


def test_full_sell_removes_position(tmp_data_dir):
    storage.append_trade(_buy("B1", date(2026, 4, 1), Decimal("10"), Decimal("2500")))
    storage.append_trade(_sell("S1", date(2026, 4, 20), Decimal("10"),
                               Decimal("2600"), Decimal("100")))
    pos = positions.current_positions()
    assert pos == []


def test_oversell_raises(tmp_data_dir):
    import pytest
    storage.append_trade(_buy("B1", date(2026, 4, 1), Decimal("10"), Decimal("2500")))
    storage.append_trade(_sell("S1", date(2026, 4, 20), Decimal("15"),
                               Decimal("3900"), Decimal("150")))
    with pytest.raises(positions.InsufficientQty):
        positions.current_positions()


def test_multiple_tickers_tracked_independently(tmp_data_dir):
    storage.append_trade(_buy("B1", date(2026, 4, 1), Decimal("10"), Decimal("2500")))
    qld_trade = Trade(
        trade_id="B2", date=date(2026, 4, 2), broker="inter_global",
        account_id="acc1", strategy="plano_b", ticker="QLD",
        instrument_type="etf", instrument_domicile="us", side="buy",
        qty=Decimal("5"), price_native=Decimal("80"), currency="USD",
        fees_native=Decimal("0"), ptax_venda=Decimal("5"),
        cost_basis_brl=Decimal("2000"), gross_brl=Decimal("2000"),
        realized_gain_brl=Decimal("0"), trade_type="swing",
    )
    storage.append_trade(qld_trade)
    pos = positions.current_positions()
    tickers = sorted(p.ticker for p in pos)
    assert tickers == ["QLD", "SSO"]
