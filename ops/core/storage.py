"""Atomic CSV r/w with schema_version header + flock.

Data dir resolved from env OPS_DATA_DIR, else ops/data/ at repo root.
"""
from __future__ import annotations

import csv
import fcntl
import os
import time
from contextlib import contextmanager
from dataclasses import asdict, fields
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable

from ops.core.models import (
    BenchmarkPoint,
    CarryforwardBalance,
    DarfEvent,
    Dividend,
    FxRate,
    Trade,
)

SCHEMA_VERSION = 1


class SchemaVersionMismatch(Exception):
    pass


class LockHeldError(Exception):
    pass


def data_dir() -> Path:
    env = os.environ.get("OPS_DATA_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2] / "ops" / "data"


def _path(name: str) -> Path:
    return data_dir() / name


def _atomic_write(path: Path, rows: Iterable[dict[str, Any]], columns: list[str]) -> None:
    """Write to .tmp, then os.rename (atomic on POSIX)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        with tmp.open("w", newline="", encoding="utf-8") as f:
            f.write(f"# schema_version: {SCHEMA_VERSION}\n")
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        os.rename(tmp, path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def _check_schema(path: Path) -> None:
    if not path.exists():
        return
    if path.stat().st_size == 0:
        return  # empty file = no data yet, no schema to check
    with path.open("r", encoding="utf-8") as f:
        first = f.readline().strip()
    expected = f"# schema_version: {SCHEMA_VERSION}"
    if first != expected:
        raise SchemaVersionMismatch(f"{path}: got {first!r}, want {expected!r}")


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    if path.stat().st_size == 0:
        return []
    _check_schema(path)
    with path.open("r", encoding="utf-8") as f:
        f.readline()  # skip schema_version line
        return list(csv.DictReader(f))


def _serialize(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)


def _row_from_dataclass(obj: Any) -> dict[str, str]:
    return {k: _serialize(v) for k, v in asdict(obj).items()}


def _parse_decimal(s: str) -> Decimal:
    return Decimal(s) if s else Decimal("0")


def _parse_date(s: str) -> date:
    return date.fromisoformat(s)


def _parse_datetime(s: str) -> datetime:
    return datetime.fromisoformat(s)


def _parse_optional_date(s: str) -> date | None:
    return _parse_date(s) if s else None


# --- Trade ---

_TRADE_COLUMNS = [f.name for f in fields(Trade)]


def read_trades() -> list[Trade]:
    rows = _read_rows(_path("trades.csv"))
    return [
        Trade(
            trade_id=r["trade_id"],
            date=_parse_date(r["date"]),
            broker=r["broker"],
            account_id=r["account_id"],
            strategy=r["strategy"],
            ticker=r["ticker"],
            instrument_type=r["instrument_type"],
            instrument_domicile=r["instrument_domicile"],
            side=r["side"],
            qty=_parse_decimal(r["qty"]),
            price_native=_parse_decimal(r["price_native"]),
            currency=r["currency"],
            fees_native=_parse_decimal(r["fees_native"]),
            ptax_venda=_parse_decimal(r["ptax_venda"]),
            cost_basis_brl=_parse_decimal(r["cost_basis_brl"]),
            gross_brl=_parse_decimal(r["gross_brl"]),
            realized_gain_brl=_parse_decimal(r["realized_gain_brl"]),
            trade_type=r["trade_type"],
            notes=r["notes"],
        )
        for r in rows
    ]


def write_trades(trades: list[Trade]) -> None:
    rows = [_row_from_dataclass(t) for t in trades]
    _atomic_write(_path("trades.csv"), rows, _TRADE_COLUMNS)


def append_trade(trade: Trade) -> None:
    """Append a trade. Read-then-write; not process-safe alone — wrap in lock() if concurrent writers."""
    trades = read_trades()
    trades.append(trade)
    write_trades(trades)


# --- Dividend ---

_DIVIDEND_COLUMNS = [f.name for f in fields(Dividend)]


def read_dividends() -> list[Dividend]:
    rows = _read_rows(_path("dividends.csv"))
    return [
        Dividend(
            dividend_id=r["dividend_id"],
            payment_date=_parse_date(r["payment_date"]),
            broker=r["broker"],
            account_id=r["account_id"],
            ticker=r["ticker"],
            gross_usd=_parse_decimal(r["gross_usd"]),
            withheld_us_tax_usd=_parse_decimal(r["withheld_us_tax_usd"]),
            net_usd=_parse_decimal(r["net_usd"]),
            ptax_venda=_parse_decimal(r["ptax_venda"]),
            gross_brl=_parse_decimal(r["gross_brl"]),
            withheld_us_tax_brl=_parse_decimal(r["withheld_us_tax_brl"]),
            net_brl=_parse_decimal(r["net_brl"]),
            notes=r["notes"],
        )
        for r in rows
    ]


def append_dividend(div: Dividend) -> None:
    """Append a dividend. Read-then-write; not process-safe alone — wrap in lock() if concurrent writers."""
    divs = read_dividends()
    divs.append(div)
    _atomic_write(
        _path("dividends.csv"),
        [_row_from_dataclass(d) for d in divs],
        _DIVIDEND_COLUMNS,
    )


# --- FxRate ---

_FX_COLUMNS = [f.name for f in fields(FxRate)]


def read_fx_rates() -> list[FxRate]:
    rows = _read_rows(_path("fx_cache.csv"))
    return [
        FxRate(
            date=_parse_date(r["date"]),
            ptax_venda=_parse_decimal(r["ptax_venda"]),
            source=r["source"],
            fetched_at=_parse_datetime(r["fetched_at"]),
        )
        for r in rows
    ]


def append_fx_rate(rate: FxRate) -> None:
    """Append an FX rate. Read-then-write; not process-safe alone — wrap in lock() if concurrent writers."""
    rates = read_fx_rates()
    rates.append(rate)
    _atomic_write(
        _path("fx_cache.csv"),
        [_row_from_dataclass(r) for r in rates],
        _FX_COLUMNS,
    )


# --- BenchmarkPoint ---

_BENCHMARK_COLUMNS = [f.name for f in fields(BenchmarkPoint)]


def read_benchmark_points() -> list[BenchmarkPoint]:
    rows = _read_rows(_path("benchmarks_cache.csv"))
    return [
        BenchmarkPoint(
            date=_parse_date(r["date"]),
            series_id=r["series_id"],
            value=_parse_decimal(r["value"]),
            source=r["source"],
            fetched_at=_parse_datetime(r["fetched_at"]),
        )
        for r in rows
    ]


def append_benchmark_points(points: list[BenchmarkPoint]) -> None:
    """Append benchmark points. Read-then-write; not process-safe alone — wrap in lock() if concurrent writers."""
    existing = read_benchmark_points()
    combined = existing + points
    _atomic_write(
        _path("benchmarks_cache.csv"),
        [_row_from_dataclass(p) for p in combined],
        _BENCHMARK_COLUMNS,
    )


# --- DarfEvent ---

_DARF_COLUMNS = [f.name for f in fields(DarfEvent)]


def read_darf_history() -> list[DarfEvent]:
    rows = _read_rows(_path("darf_history.csv"))
    return [
        DarfEvent(
            darf_id=r["darf_id"],
            regime=r["regime"],
            period_start=_parse_date(r["period_start"]),
            period_end=_parse_date(r["period_end"]),
            due_date=_parse_date(r["due_date"]),
            code=r["code"],
            stream=r["stream"],
            gross_gain_brl=_parse_decimal(r["gross_gain_brl"]),
            dividends_brl=_parse_decimal(r["dividends_brl"]),
            loss_offset_brl=_parse_decimal(r["loss_offset_brl"]),
            net_taxable_brl=_parse_decimal(r["net_taxable_brl"]),
            tax_rate_applied=_parse_decimal(r["tax_rate_applied"]),
            tax_due_brl=_parse_decimal(r["tax_due_brl"]),
            paid_at=_parse_optional_date(r["paid_at"]),
            paid_proof_path=r["paid_proof_path"],
            notes=r["notes"],
        )
        for r in rows
    ]


def write_darf_history(events: list[DarfEvent]) -> None:
    """Rewrite the entire darf_history.csv. Not process-safe alone — wrap in lock() for concurrent writers."""
    _atomic_write(
        _path("darf_history.csv"),
        [_row_from_dataclass(e) for e in events],
        _DARF_COLUMNS,
    )


def append_darf_event(event: DarfEvent) -> None:
    """Append a DARF event. Read-then-write; not process-safe alone — wrap in lock() if concurrent writers."""
    events = read_darf_history()
    events.append(event)
    write_darf_history(events)


# --- CarryforwardBalance ---

_CARRY_COLUMNS = [f.name for f in fields(CarryforwardBalance)]


def read_carryforward() -> list[CarryforwardBalance]:
    rows = _read_rows(_path("carryforward.csv"))
    return [
        CarryforwardBalance(
            regime=r["regime"],
            stream=r["stream"],
            period=r["period"],
            balance_in=_parse_decimal(r["balance_in"]),
            accrued_this_period=_parse_decimal(r["accrued_this_period"]),
            consumed_this_period=_parse_decimal(r["consumed_this_period"]),
            balance_out=_parse_decimal(r["balance_out"]),
        )
        for r in rows
    ]


def write_carryforward(balances: list[CarryforwardBalance]) -> None:
    """Write full carryforward state. Read-then-write; not process-safe alone — wrap in lock() if concurrent writers."""
    _atomic_write(
        _path("carryforward.csv"),
        [_row_from_dataclass(b) for b in balances],
        _CARRY_COLUMNS,
    )


# --- Lock ---


@contextmanager
def lock(timeout_sec: float = 5.0):
    """Exclusive flock on ops/data/.lock. Raises LockHeldError if timeout."""
    lock_path = data_dir() / ".lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o644)
    deadline = time.monotonic() + timeout_sec
    while True:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except BlockingIOError:
            if time.monotonic() >= deadline:
                os.close(fd)
                raise LockHeldError(f"ops/data/.lock held (waited {timeout_sec}s)")
            time.sleep(0.05)
    try:
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
