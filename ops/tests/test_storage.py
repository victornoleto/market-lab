"""Tests for ops/core/storage.py — atomic CSV r/w with schema_version."""
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from ops.core import storage
from ops.core.models import FxRate, Trade


def test_schema_version_written_on_first_write(tmp_data_dir):
    rate = FxRate(
        date=date(2026, 4, 20),
        ptax_venda=Decimal("5.1234"),
        source="bcb_sgs_1",
        fetched_at=datetime(2026, 4, 20, 14, 23, 10, tzinfo=timezone.utc),
    )
    storage.append_fx_rate(rate)

    path = tmp_data_dir / "fx_cache.csv"
    assert path.exists()
    first_line = path.read_text().splitlines()[0]
    assert first_line == "# schema_version: 1"


def test_read_trades_empty_file_returns_empty_list(tmp_data_dir):
    assert storage.read_trades() == []


def test_append_and_read_trade_round_trip(tmp_data_dir):
    trade = Trade(
        trade_id="T-20260420-001",
        date=date(2026, 4, 20),
        broker="inter_global",
        account_id="inter_global_123456",
        strategy="plano_b",
        ticker="SSO",
        instrument_type="etf",
        instrument_domicile="us",
        side="buy",
        qty=Decimal("10"),
        price_native=Decimal("52.30"),
        currency="USD",
        fees_native=Decimal("0"),
        ptax_venda=Decimal("5.1234"),
        cost_basis_brl=Decimal("2678.20"),
        gross_brl=Decimal("2678.20"),
        realized_gain_brl=Decimal("0"),
        trade_type="swing",
        notes="",
    )
    storage.append_trade(trade)
    result = storage.read_trades()
    assert len(result) == 1
    assert result[0].trade_id == "T-20260420-001"
    assert result[0].qty == Decimal("10")
    assert result[0].ptax_venda == Decimal("5.1234")


def test_schema_version_mismatch_raises(tmp_data_dir):
    path = tmp_data_dir / "trades.csv"
    path.write_text(
        "# schema_version: 99\n"
        "trade_id,date,broker,account_id,strategy,ticker,instrument_type,"
        "instrument_domicile,side,qty,price_native,currency,fees_native,"
        "ptax_venda,cost_basis_brl,gross_brl,realized_gain_brl,"
        "trade_type,notes\n"
    )
    with pytest.raises(storage.SchemaVersionMismatch):
        storage.read_trades()


def test_atomic_write_no_partial_on_crash(tmp_data_dir, monkeypatch):
    rate = FxRate(
        date=date(2026, 4, 20),
        ptax_venda=Decimal("5.1234"),
        source="bcb_sgs_1",
        fetched_at=datetime.now(timezone.utc),
    )
    storage.append_fx_rate(rate)
    original_content = (tmp_data_dir / "fx_cache.csv").read_text()

    def fail_rename(*args, **kwargs):
        raise OSError("simulated crash")

    monkeypatch.setattr("os.rename", fail_rename)
    new_rate = FxRate(
        date=date(2026, 4, 21),
        ptax_venda=Decimal("5.2000"),
        source="bcb_sgs_1",
        fetched_at=datetime.now(timezone.utc),
    )
    with pytest.raises(OSError):
        storage.append_fx_rate(new_rate)

    assert (tmp_data_dir / "fx_cache.csv").read_text() == original_content


def test_lock_prevents_concurrent_write(tmp_data_dir):
    with storage.lock():
        with pytest.raises(storage.LockHeldError):
            with storage.lock(timeout_sec=0.1):
                pass


def test_empty_file_returns_empty_list(tmp_data_dir):
    """Zero-byte CSV is valid: no data, no schema — returns []."""
    path = tmp_data_dir / "trades.csv"
    path.touch()
    assert storage.read_trades() == []


def test_tmp_file_cleaned_up_on_write_failure(tmp_data_dir, monkeypatch):
    """If write fails before rename, .tmp file is removed (no orphan)."""
    # Force rename to fail after .tmp is written
    def fail_rename(*args, **kwargs):
        raise OSError("simulated rename failure")

    monkeypatch.setattr("os.rename", fail_rename)
    rate = FxRate(
        date=date(2026, 4, 20),
        ptax_venda=Decimal("5.1234"),
        source="bcb_sgs_1",
        fetched_at=datetime.now(timezone.utc),
    )
    with pytest.raises(OSError):
        storage.append_fx_rate(rate)

    # Tmp file must not be left behind
    assert not (tmp_data_dir / "fx_cache.csv.tmp").exists()
