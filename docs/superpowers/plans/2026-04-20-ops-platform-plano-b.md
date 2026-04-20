# Ops Platform — Plano B MVP — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CLI-based operational platform (`ops/`) for manual trade journaling, DARF calculation (two regimes), FIFO position tracking, dividend logging, and multi-benchmark comparison in BRL — servicing Plano B today, schema-ready for Planos A and C.

**Architecture:** Split `ops/core/` (pure business logic, testable without I/O) + `ops/cli/` (typer CLI wrapper) + `ops/data/` (gitignored CSVs) + `ops/tests/`. Two pluggable tax regimes (`monthly_6015`, `annual_14754`). All financial math in `Decimal`. Zero network in pytest (BCB/yfinance mocked).

**Tech Stack:** Python 3.11+, typer, pandas, Decimal, requests (BCB SGS), yfinance (IBOV/IVVB11), matplotlib (charts), holidays (feriados BR), cryptography (encrypted backup), pytest + requests_mock (tests).

**Source spec:** `docs/superpowers/specs/2026-04-20-ops-platform-plano-b-design.md`.

**Baseline invariant:** pytest suite passes at ≥796 tests throughout. Each commit keeps baseline green.

---

## File structure (locked)

```
ops/
├── __init__.py                              # empty; package marker
├── core/
│   ├── __init__.py                          # public re-exports from models
│   ├── models.py                            # Trade, Dividend, FxRate, DarfEvent, CarryforwardBalance, Position, Lot
│   ├── storage.py                           # atomic CSV r/w + schema_version + flock
│   ├── fx.py                                # BCB SGS série 1 client + cache lookup + feriado fallback
│   ├── tax/
│   │   ├── __init__.py                      # get_regime(name) factory
│   │   ├── base.py                          # TaxRegime ABC + DarfEvent building helpers
│   │   ├── regime_monthly_6015.py           # swing+daytrade monthly
│   │   └── regime_annual_14754.py           # unified rendimentos annual
│   ├── positions.py                         # FIFO lot matching, current_positions, drift_vs_target
│   ├── benchmarks.py                        # fetchers + equity_curve_brl normalizer
│   └── reports.py                           # markdown + chart renderers
├── cli/
│   ├── __init__.py
│   ├── main.py                              # typer app entrypoint
│   ├── _common.py                           # shared CLI utilities (table printing, confirmations)
│   ├── trade.py, dividend.py, darf.py,
│   ├── benchmark.py, signal.py, status.py,
│   └── export.py
├── data/
│   ├── .gitkeep
│   └── (runtime files: trades.csv, dividends.csv, fx_cache.csv, benchmarks_cache.csv,
│         darf_history.csv, carryforward.csv, .lock, config.yaml)
├── tests/
│   ├── __init__.py
│   ├── conftest.py                          # tmp_data_dir fixture, mocked BCB
│   ├── fixtures/
│   │   └── example_plano_b_2026/            # golden fixture for e2e + tax tests
│   ├── test_storage.py
│   ├── test_fx.py
│   ├── test_positions.py
│   ├── test_benchmarks.py
│   ├── test_reports.py
│   ├── test_tax/
│   │   ├── __init__.py
│   │   ├── test_regime_monthly_6015.py
│   │   └── test_regime_annual_14754.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── test_smoke_trade.py
│   │   ├── test_smoke_darf.py
│   │   └── test_smoke_benchmark.py
│   ├── test_e2e_plano_b_workflow.py
│   └── test_bcb_live.py                     # @pytest.mark.live_api
└── README.md
```

Modified outside `ops/`:

- `pyproject.toml` — add ops to hatch packages, add deps, add script entrypoint.
- `.gitignore` — add `ops/data/**` except `.gitkeep`.
- `.pre-commit-config.yaml` (if exists) — add hook rejecting staged `ops/data/*.csv`.

---

## Task 1: Scaffolding + pyproject + gitignore + empty package

**Files:**
- Create: `ops/__init__.py`, `ops/core/__init__.py`, `ops/core/tax/__init__.py`, `ops/cli/__init__.py`, `ops/data/.gitkeep`, `ops/tests/__init__.py`, `ops/tests/cli/__init__.py`, `ops/tests/test_tax/__init__.py`, `ops/README.md` (stub)
- Modify: `pyproject.toml`, `.gitignore`

- [ ] **Step 1.1: Create empty package markers**

```bash
mkdir -p ops/core/tax ops/cli ops/data ops/tests/cli ops/tests/test_tax ops/tests/fixtures
touch ops/__init__.py ops/core/__init__.py ops/core/tax/__init__.py ops/cli/__init__.py
touch ops/tests/__init__.py ops/tests/cli/__init__.py ops/tests/test_tax/__init__.py
touch ops/data/.gitkeep
```

- [ ] **Step 1.2: Stub `ops/README.md`**

```markdown
# ops/ — Operational platform (Plano B MVP)

Stub. Full content delivered in Task 11.

See `docs/superpowers/specs/2026-04-20-ops-platform-plano-b-design.md`.
```

- [ ] **Step 1.3: Update `pyproject.toml` — add deps + package + script**

Add to `dependencies`:

```toml
    "typer>=0.12",              # ops/ CLI
    "requests>=2.31",           # BCB SGS HTTP client
    "holidays>=0.50",           # BR feriados bancários
    "cryptography>=42.0",       # encrypted backup
```

Modify `[tool.hatch.build.targets.wheel]`:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/ai_trade", "ops"]
```

Add new section `[project.scripts]`:

```toml
[project.scripts]
ops = "ops.cli.main:app"
```

Add new dev deps to `[dependency-groups]` dev:

```toml
dev = [
    "pytest>=8.0",
    "ruff>=0.6",
    "requests-mock>=1.12",      # mock BCB/yfinance in tests
    "hypothesis>=6.100",        # property-based (Phase 2, opt)
]
```

- [ ] **Step 1.4: Update `.gitignore`**

Append:

```
# ops/ data — trades fiscais, CSVs privados, NUNCA commitar
ops/data/**
!ops/data/.gitkeep
```

- [ ] **Step 1.5: Install dev env + verify**

```bash
.venv/bin/pip install -e '.[dev]' 2>/dev/null || uv pip install -e . --group dev
.venv/bin/pytest --co -q 2>&1 | tail -5
```

Expected: baseline test count unchanged (still 796+). No import errors.

- [ ] **Step 1.6: Commit**

```bash
git add ops/ pyproject.toml .gitignore
git commit -m "feat(ops): scaffold package + deps + gitignore (Task 1/11)"
```

---

## Task 2: Models (dataclasses) + storage module (atomic CSV r/w)

**Files:**
- Create: `ops/core/models.py`, `ops/core/storage.py`, `ops/tests/conftest.py`, `ops/tests/test_storage.py`

- [ ] **Step 2.1: Write `ops/core/models.py`**

```python
"""Dataclasses for all CSV-backed entities. Immutable (frozen=True)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

Side = Literal["buy", "sell"]
InstrumentType = Literal["etf", "stock", "fii", "bdr", "cfd", "cash"]
InstrumentDomicile = Literal["us", "br", "other"]
TradeType = Literal["swing", "daytrade"]
Stream = Literal["swing", "daytrade", "rendimentos"]
RegimeName = Literal["monthly_6015", "annual_14754"]


@dataclass(frozen=True)
class Trade:
    trade_id: str
    date: date
    broker: str
    account_id: str
    strategy: str
    ticker: str
    instrument_type: InstrumentType
    instrument_domicile: InstrumentDomicile
    side: Side
    qty: Decimal
    price_native: Decimal
    currency: str
    fees_native: Decimal
    ptax_venda: Decimal
    cost_basis_brl: Decimal
    gross_brl: Decimal
    realized_gain_brl: Decimal
    trade_type: TradeType
    notes: str = ""


@dataclass(frozen=True)
class Dividend:
    dividend_id: str
    payment_date: date
    broker: str
    account_id: str
    ticker: str
    gross_usd: Decimal
    withheld_us_tax_usd: Decimal
    net_usd: Decimal
    ptax_venda: Decimal
    gross_brl: Decimal
    withheld_us_tax_brl: Decimal
    net_brl: Decimal
    notes: str = ""


@dataclass(frozen=True)
class FxRate:
    date: date
    ptax_venda: Decimal
    source: str
    fetched_at: datetime


@dataclass(frozen=True)
class BenchmarkPoint:
    date: date
    series_id: str
    value: Decimal
    source: str
    fetched_at: datetime


@dataclass(frozen=True)
class DarfEvent:
    darf_id: str
    regime: RegimeName
    period_start: date
    period_end: date
    due_date: date
    code: str
    stream: Stream
    gross_gain_brl: Decimal
    dividends_brl: Decimal
    loss_offset_brl: Decimal
    net_taxable_brl: Decimal
    tax_rate_applied: Decimal
    tax_due_brl: Decimal
    paid_at: date | None = None
    paid_proof_path: str = ""
    notes: str = ""


@dataclass(frozen=True)
class CarryforwardBalance:
    regime: RegimeName
    stream: Stream
    period: str  # "YYYY-MM" monthly, "YYYY" annual
    balance_in: Decimal
    accrued_this_period: Decimal
    consumed_this_period: Decimal
    balance_out: Decimal


@dataclass(frozen=True)
class Lot:
    """An open buy lot used for FIFO realization."""
    trade_id: str
    date: date
    ticker: str
    qty: Decimal
    cost_basis_brl: Decimal  # for the remaining qty


@dataclass(frozen=True)
class Position:
    broker: str
    account_id: str
    ticker: str
    qty: Decimal
    avg_cost_brl: Decimal
    open_lots: tuple[Lot, ...] = ()
```

- [ ] **Step 2.2: Write `ops/tests/conftest.py`** (shared fixtures)

```python
"""Shared fixtures for ops/ test suite."""
import os
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def tmp_data_dir(tmp_path, monkeypatch):
    """Isolated ops/data/ for each test.

    Monkeypatches OPS_DATA_DIR so storage module reads from tmp dir.
    """
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setenv("OPS_DATA_DIR", str(data_dir))
    yield data_dir
```

- [ ] **Step 2.3: Write failing tests in `ops/tests/test_storage.py`**

```python
"""Tests for ops/core/storage.py — atomic CSV r/w with schema_version."""
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

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
    # File doesn't exist yet
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
    """If rename fails mid-write, original file is unchanged."""
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

    # Original content intact
    assert (tmp_data_dir / "fx_cache.csv").read_text() == original_content


def test_lock_prevents_concurrent_write(tmp_data_dir):
    """Second acquirer on same lock fails fast."""
    with storage.lock():
        with pytest.raises(storage.LockHeldError):
            with storage.lock(timeout_sec=0.1):
                pass
```

- [ ] **Step 2.4: Run tests to verify they fail**

```bash
.venv/bin/pytest ops/tests/test_storage.py -v
```

Expected: 6 FAILS (module not implemented).

- [ ] **Step 2.5: Write `ops/core/storage.py`**

```python
"""Atomic CSV r/w with schema_version header + flock.

Data dir resolved from env OPS_DATA_DIR, else ops/data/ at repo root.
"""
from __future__ import annotations

import csv
import fcntl
import os
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
    with tmp.open("w", newline="", encoding="utf-8") as f:
        f.write(f"# schema_version: {SCHEMA_VERSION}\n")
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    os.rename(tmp, path)


def _check_schema(path: Path) -> None:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        first = f.readline().strip()
    expected = f"# schema_version: {SCHEMA_VERSION}"
    if first != expected:
        raise SchemaVersionMismatch(f"{path}: got {first!r}, want {expected!r}")


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
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
    trades = read_trades()
    trades.append(trade)
    write_trades(trades)


# --- Analogous read_/write_/append_ for Dividend, FxRate, BenchmarkPoint,
#     DarfEvent, CarryforwardBalance. Code pattern identical — for brevity,
#     implement them following the Trade pattern. Each uses its own
#     _COLUMNS list from `fields(Class)`. ---

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
    divs = read_dividends()
    divs.append(div)
    _atomic_write(
        _path("dividends.csv"),
        [_row_from_dataclass(d) for d in divs],
        _DIVIDEND_COLUMNS,
    )


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
    rates = read_fx_rates()
    rates.append(rate)
    _atomic_write(
        _path("fx_cache.csv"),
        [_row_from_dataclass(r) for r in rates],
        _FX_COLUMNS,
    )


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
    existing = read_benchmark_points()
    combined = existing + points
    _atomic_write(
        _path("benchmarks_cache.csv"),
        [_row_from_dataclass(p) for p in combined],
        _BENCHMARK_COLUMNS,
    )


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


def append_darf_event(event: DarfEvent) -> None:
    events = read_darf_history()
    events.append(event)
    _atomic_write(
        _path("darf_history.csv"),
        [_row_from_dataclass(e) for e in events],
        _DARF_COLUMNS,
    )


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
    _atomic_write(
        _path("carryforward.csv"),
        [_row_from_dataclass(b) for b in balances],
        _CARRY_COLUMNS,
    )


# --- Lock ---


@contextmanager
def lock(timeout_sec: float = 5.0):
    """Exclusive flock on ops/data/.lock. Raises LockHeldError if timeout."""
    import time

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
```

- [ ] **Step 2.6: Run tests to verify PASS**

```bash
.venv/bin/pytest ops/tests/test_storage.py -v
```

Expected: 6 PASS.

- [ ] **Step 2.7: Run full baseline test suite**

```bash
.venv/bin/pytest 2>&1 | tail -5
```

Expected: `NNN passed` where NNN ≥ 802 (original 796+6 new).

- [ ] **Step 2.8: Commit**

```bash
git add ops/core/models.py ops/core/storage.py ops/tests/conftest.py ops/tests/test_storage.py
git commit -m "feat(ops): models + storage with atomic CSV r/w (Task 2/11)"
```

---

## Task 3: FX module (BCB SGS client + PTAX cache + feriado fallback)

**Files:**
- Create: `ops/core/fx.py`, `ops/tests/test_fx.py`

- [ ] **Step 3.1: Write failing tests in `ops/tests/test_fx.py`**

```python
"""Tests for ops/core/fx.py — BCB SGS série 1 PTAX client."""
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from ops.core import fx, storage
from ops.core.models import FxRate


def test_get_ptax_cache_hit(tmp_data_dir):
    storage.append_fx_rate(
        FxRate(
            date=date(2026, 4, 20),
            ptax_venda=Decimal("5.1234"),
            source="bcb_sgs_1",
            fetched_at=datetime.now(timezone.utc),
        )
    )
    result = fx.get_ptax(date(2026, 4, 20))
    assert result == Decimal("5.1234")


def test_get_ptax_cache_miss_fetches_bcb(tmp_data_dir, requests_mock):
    requests_mock.get(
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados",
        json=[{"data": "20/04/2026", "valor": "5.1234"}],
    )
    result = fx.get_ptax(date(2026, 4, 20))
    assert result == Decimal("5.1234")

    # Second call: cache hit, no new HTTP
    requests_mock.reset_mock()
    result2 = fx.get_ptax(date(2026, 4, 20))
    assert result2 == Decimal("5.1234")
    assert requests_mock.call_count == 0


def test_weekend_falls_back_to_previous_business_day(tmp_data_dir, requests_mock):
    # 2026-04-18 is a Saturday → fallback to Friday 2026-04-17
    requests_mock.get(
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados",
        json=[{"data": "17/04/2026", "valor": "5.1000"}],
    )
    result = fx.get_ptax(date(2026, 4, 18))
    assert result == Decimal("5.1000")


def test_bcb_empty_response_raises(tmp_data_dir, requests_mock):
    requests_mock.get(
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados",
        json=[],
    )
    with pytest.raises(fx.PtaxUnavailable):
        fx.get_ptax(date(2026, 4, 20))


def test_set_ptax_manual_bypasses_api(tmp_data_dir, requests_mock):
    fx.set_ptax_manual(date(2026, 4, 20), Decimal("5.5000"))
    # API never called
    assert requests_mock.call_count == 0
    assert fx.get_ptax(date(2026, 4, 20)) == Decimal("5.5000")
```

- [ ] **Step 3.2: Run tests to verify fail**

```bash
.venv/bin/pytest ops/tests/test_fx.py -v
```

Expected: 5 FAILS (module missing).

- [ ] **Step 3.3: Write `ops/core/fx.py`**

```python
"""BCB SGS série 1 PTAX venda client + persistent cache + feriado fallback."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import holidays
import requests

from ops.core import storage
from ops.core.models import FxRate

BCB_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados"
BCB_TIMEOUT_SEC = 10.0
_BR_HOLIDAYS = holidays.country_holidays("BR")


class PtaxUnavailable(Exception):
    pass


def _is_business_day(d: date) -> bool:
    return d.weekday() < 5 and d not in _BR_HOLIDAYS


def _previous_business_day(d: date) -> date:
    cur = d - timedelta(days=1)
    while not _is_business_day(cur):
        cur -= timedelta(days=1)
    return cur


def _lookup_cache(d: date) -> Decimal | None:
    for rate in storage.read_fx_rates():
        if rate.date == d:
            return rate.ptax_venda
    return None


def _fetch_bcb(d: date) -> Decimal:
    params = {
        "formato": "json",
        "dataInicial": d.strftime("%d/%m/%Y"),
        "dataFinal": d.strftime("%d/%m/%Y"),
    }
    resp = requests.get(BCB_URL, params=params, timeout=BCB_TIMEOUT_SEC)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise PtaxUnavailable(f"BCB returned empty for {d.isoformat()}")
    return Decimal(str(data[0]["valor"]))


def get_ptax(d: date) -> Decimal:
    """Resolve PTAX venda for d.

    Order: cache → BCB fetch → fallback to last business day if d is weekend/holiday.
    """
    target = d if _is_business_day(d) else _previous_business_day(d)

    cached = _lookup_cache(target)
    if cached is not None:
        return cached

    value = _fetch_bcb(target)
    storage.append_fx_rate(
        FxRate(
            date=target,
            ptax_venda=value,
            source="bcb_sgs_1",
            fetched_at=datetime.now(timezone.utc),
        )
    )
    return value


def set_ptax_manual(d: date, value: Decimal) -> None:
    """Override cache with a manual PTAX value. Source tagged 'manual'."""
    storage.append_fx_rate(
        FxRate(
            date=d,
            ptax_venda=value,
            source="manual",
            fetched_at=datetime.now(timezone.utc),
        )
    )
```

- [ ] **Step 3.4: Run tests to verify PASS**

```bash
.venv/bin/pytest ops/tests/test_fx.py -v
```

Expected: 5 PASS.

- [ ] **Step 3.5: Baseline check**

```bash
.venv/bin/pytest 2>&1 | tail -3
```

Expected: ≥ 807 passed.

- [ ] **Step 3.6: Commit**

```bash
git add ops/core/fx.py ops/tests/test_fx.py
git commit -m "feat(ops): BCB SGS PTAX client + cache + feriado fallback (Task 3/11)"
```

---

## Task 4: Tax regime base + monthly_6015

**Files:**
- Create: `ops/core/tax/base.py`, `ops/core/tax/regime_monthly_6015.py`, `ops/tests/test_tax/test_regime_monthly_6015.py`

- [ ] **Step 4.1: Write `ops/core/tax/base.py`**

```python
"""TaxRegime abstract base + factory."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import ClassVar

from ops.core.models import DarfEvent, Dividend, Stream, Trade


class TaxRegime(ABC):
    name: ClassVar[str]
    darf_code_default: ClassVar[str]
    streams: ClassVar[tuple[Stream, ...]]

    @abstractmethod
    def period_for(self, d: date) -> tuple[date, date]:
        """Return (period_start, period_end) containing d."""

    @abstractmethod
    def due_date(self, period_end: date) -> date:
        """Last business day after period_end when DARF is due."""

    @abstractmethod
    def period_key(self, period_end: date) -> str:
        """String key for carryforward lookups ('YYYY-MM' or 'YYYY')."""

    @abstractmethod
    def compute(
        self,
        trades: list[Trade],
        dividends: list[Dividend],
        carryforward_in: dict[Stream, Decimal],
        period_start: date,
        period_end: date,
    ) -> list[DarfEvent]:
        """Compute 0-N DarfEvents for period; consumes carryforward_in."""
```

- [ ] **Step 4.2: Write `ops/core/tax/__init__.py`** (factory)

```python
"""Tax regime factory."""
from __future__ import annotations

from ops.core.tax.base import TaxRegime
from ops.core.tax.regime_annual_14754 import AnnualLei14754Regime
from ops.core.tax.regime_monthly_6015 import MonthlyLei11033Regime

_REGIMES = {
    "monthly_6015": MonthlyLei11033Regime,
    "annual_14754": AnnualLei14754Regime,
}


def get_regime(name: str) -> TaxRegime:
    if name not in _REGIMES:
        raise ValueError(f"Unknown regime: {name}. Known: {list(_REGIMES)}")
    return _REGIMES[name]()


__all__ = ["TaxRegime", "get_regime"]
```

**Note:** `regime_annual_14754` import will fail until Task 5; that's expected. We implement monthly first and temporarily suppress the annual import.

Replace `__init__.py` contents with deferred import:

```python
"""Tax regime factory."""
from __future__ import annotations

from ops.core.tax.base import TaxRegime


def get_regime(name: str) -> TaxRegime:
    if name == "monthly_6015":
        from ops.core.tax.regime_monthly_6015 import MonthlyLei11033Regime
        return MonthlyLei11033Regime()
    if name == "annual_14754":
        from ops.core.tax.regime_annual_14754 import AnnualLei14754Regime
        return AnnualLei14754Regime()
    raise ValueError(f"Unknown regime: {name}")


__all__ = ["TaxRegime", "get_regime"]
```

- [ ] **Step 4.3: Write failing tests in `ops/tests/test_tax/test_regime_monthly_6015.py`**

```python
"""Tests for MonthlyLei11033Regime (legacy monthly DARF 6015)."""
from datetime import date
from decimal import Decimal

import pytest

from ops.core.models import Trade
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
    from ops.core.models import Dividend
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
```

- [ ] **Step 4.4: Run tests to verify fail**

```bash
.venv/bin/pytest ops/tests/test_tax/test_regime_monthly_6015.py -v
```

Expected: 9 FAILS.

- [ ] **Step 4.5: Write `ops/core/tax/regime_monthly_6015.py`**

```python
"""Monthly DARF 6015 regime (Lei 11033/2004 — pre-Lei-14.754 for renda variável)."""
from __future__ import annotations

import calendar
from datetime import date, timedelta
from decimal import ROUND_UP, Decimal
from typing import ClassVar

import holidays

from ops.core.models import DarfEvent, Dividend, Stream, Trade
from ops.core.tax.base import TaxRegime

_BR = holidays.country_holidays("BR")


def _last_business_day_of_month(year: int, month: int) -> date:
    _, last = calendar.monthrange(year, month)
    d = date(year, month, last)
    while d.weekday() >= 5 or d in _BR:
        d -= timedelta(days=1)
    return d


def _next_month(d: date) -> tuple[int, int]:
    if d.month == 12:
        return (d.year + 1, 1)
    return (d.year, d.month + 1)


class MonthlyLei11033Regime(TaxRegime):
    name: ClassVar[str] = "monthly_6015"
    darf_code_default: ClassVar[str] = "6015"
    streams: ClassVar[tuple[Stream, ...]] = ("swing", "daytrade")

    def period_for(self, d: date) -> tuple[date, date]:
        _, last = calendar.monthrange(d.year, d.month)
        return (date(d.year, d.month, 1), date(d.year, d.month, last))

    def due_date(self, period_end: date) -> date:
        y, m = _next_month(period_end)
        return _last_business_day_of_month(y, m)

    def period_key(self, period_end: date) -> str:
        return f"{period_end.year:04d}-{period_end.month:02d}"

    def compute(
        self,
        trades: list[Trade],
        dividends: list[Dividend],
        carryforward_in: dict[Stream, Decimal],
        period_start: date,
        period_end: date,
    ) -> list[DarfEvent]:
        events: list[DarfEvent] = []
        due = self.due_date(period_end)
        period_key = self.period_key(period_end)

        for stream_name in ("swing", "daytrade"):
            sells = [
                t for t in trades
                if t.side == "sell"
                and t.trade_type == stream_name
                and period_start <= t.date <= period_end
            ]
            if not sells:
                continue

            gross_gain = sum(
                (t.realized_gain_brl for t in sells),
                start=Decimal("0"),
            )
            # Only positive gross_gain produces DARF; losses accrue to carryforward
            # (handled by caller, not this regime).
            if gross_gain <= Decimal("0"):
                continue

            carry_in = carryforward_in.get(stream_name, Decimal("0"))
            loss_offset = min(carry_in, gross_gain)
            net_taxable = gross_gain - loss_offset
            rate = Decimal("0.15") if stream_name == "swing" else Decimal("0.20")
            tax_due = (net_taxable * rate).quantize(Decimal("0.01"), rounding=ROUND_UP)

            code = "6015" if stream_name == "swing" else "8523"
            darf_id = f"DARF-M-{period_key.replace('-', '')}-{stream_name[:2].upper()}"

            events.append(
                DarfEvent(
                    darf_id=darf_id,
                    regime="monthly_6015",
                    period_start=period_start,
                    period_end=period_end,
                    due_date=due,
                    code=code,
                    stream=stream_name,
                    gross_gain_brl=gross_gain,
                    dividends_brl=Decimal("0"),
                    loss_offset_brl=loss_offset,
                    net_taxable_brl=net_taxable,
                    tax_rate_applied=rate,
                    tax_due_brl=tax_due,
                )
            )
        return events
```

- [ ] **Step 4.6: Run tests to verify PASS**

```bash
.venv/bin/pytest ops/tests/test_tax/test_regime_monthly_6015.py -v
```

Expected: 9 PASS.

- [ ] **Step 4.7: Commit**

```bash
git add ops/core/tax/
git commit -m "feat(ops): tax regime base + monthly_6015 (Task 4/11)"
```

---

## Task 5: Tax regime annual_14754

**Files:**
- Create: `ops/core/tax/regime_annual_14754.py`, `ops/tests/test_tax/test_regime_annual_14754.py`

- [ ] **Step 5.1: Write failing tests**

```python
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
```

- [ ] **Step 5.2: Run tests to verify fail**

```bash
.venv/bin/pytest ops/tests/test_tax/test_regime_annual_14754.py -v
```

Expected: 6 FAILS.

- [ ] **Step 5.3: Write `ops/core/tax/regime_annual_14754.py`**

```python
"""Annual regime Lei 14.754/2023 — unified rendimentos bucket, DARF code 0211."""
from __future__ import annotations

import calendar
from datetime import date, timedelta
from decimal import ROUND_UP, Decimal
from typing import ClassVar

import holidays

from ops.core.models import DarfEvent, Dividend, Stream, Trade
from ops.core.tax.base import TaxRegime

_BR = holidays.country_holidays("BR")


def _last_business_day_of_month(year: int, month: int) -> date:
    _, last = calendar.monthrange(year, month)
    d = date(year, month, last)
    while d.weekday() >= 5 or d in _BR:
        d -= timedelta(days=1)
    return d


class AnnualLei14754Regime(TaxRegime):
    name: ClassVar[str] = "annual_14754"
    darf_code_default: ClassVar[str] = "0211"
    streams: ClassVar[tuple[Stream, ...]] = ("rendimentos",)

    def period_for(self, d: date) -> tuple[date, date]:
        return (date(d.year, 1, 1), date(d.year, 12, 31))

    def due_date(self, period_end: date) -> date:
        # IRPF deadline: last business day of April of following year
        return _last_business_day_of_month(period_end.year + 1, 4)

    def period_key(self, period_end: date) -> str:
        return f"{period_end.year:04d}"

    def compute(
        self,
        trades: list[Trade],
        dividends: list[Dividend],
        carryforward_in: dict[Stream, Decimal],
        period_start: date,
        period_end: date,
    ) -> list[DarfEvent]:
        sells = [
            t for t in trades
            if t.side == "sell" and period_start <= t.date <= period_end
        ]
        gross_gain = sum(
            (t.realized_gain_brl for t in sells),
            start=Decimal("0"),
        )
        divs_in_period = [
            d for d in dividends
            if period_start <= d.payment_date <= period_end
        ]
        dividends_brl = sum(
            (d.gross_brl for d in divs_in_period),
            start=Decimal("0"),
        )

        net_rendimentos = gross_gain + dividends_brl
        if net_rendimentos <= Decimal("0"):
            return []  # net loss year — all accrues to carryforward (caller handles)

        carry_in = carryforward_in.get("rendimentos", Decimal("0"))
        loss_offset = min(carry_in, net_rendimentos)
        net_taxable = net_rendimentos - loss_offset
        rate = Decimal("0.15")
        tax_due = (net_taxable * rate).quantize(Decimal("0.01"), rounding=ROUND_UP)

        return [
            DarfEvent(
                darf_id=f"DARF-A-{period_end.year}-REND",
                regime="annual_14754",
                period_start=period_start,
                period_end=period_end,
                due_date=self.due_date(period_end),
                code=self.darf_code_default,
                stream="rendimentos",
                gross_gain_brl=gross_gain,
                dividends_brl=dividends_brl,
                loss_offset_brl=loss_offset,
                net_taxable_brl=net_taxable,
                tax_rate_applied=rate,
                tax_due_brl=tax_due,
            )
        ]
```

- [ ] **Step 5.4: Run tests to verify PASS**

```bash
.venv/bin/pytest ops/tests/test_tax/ -v
```

Expected: 15 PASS (9 monthly + 6 annual).

- [ ] **Step 5.5: Commit**

```bash
git add ops/core/tax/regime_annual_14754.py ops/tests/test_tax/test_regime_annual_14754.py
git commit -m "feat(ops): tax regime annual_14754 (Task 5/11)"
```

---

## Task 6: Positions module (FIFO lot matching)

**Files:**
- Create: `ops/core/positions.py`, `ops/tests/test_positions.py`

- [ ] **Step 6.1: Write failing tests**

```python
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
```

- [ ] **Step 6.2: Run tests to verify fail**

```bash
.venv/bin/pytest ops/tests/test_positions.py -v
```

Expected: 6 FAILS.

- [ ] **Step 6.3: Write `ops/core/positions.py`**

```python
"""FIFO lot matching + current positions derived from trade log."""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from ops.core import storage
from ops.core.models import Lot, Position, Trade


class InsufficientQty(Exception):
    pass


def _group_key(t: Trade) -> tuple[str, str, str]:
    return (t.broker, t.account_id, t.ticker)


def current_positions() -> list[Position]:
    trades = sorted(storage.read_trades(), key=lambda t: (t.date, t.trade_id))
    return positions_from_trades(trades)


def positions_from_trades(trades: list[Trade]) -> list[Position]:
    open_lots: dict[tuple[str, str, str], list[Lot]] = defaultdict(list)

    for t in trades:
        key = _group_key(t)
        if t.side == "buy":
            open_lots[key].append(
                Lot(trade_id=t.trade_id, date=t.date, ticker=t.ticker,
                    qty=t.qty, cost_basis_brl=t.cost_basis_brl)
            )
        else:  # sell — consume FIFO
            remaining = t.qty
            while remaining > Decimal("0"):
                if not open_lots[key]:
                    raise InsufficientQty(
                        f"Sell {t.trade_id} of {remaining} {t.ticker} but no open lots"
                    )
                lot = open_lots[key][0]
                if lot.qty <= remaining:
                    remaining -= lot.qty
                    open_lots[key].pop(0)
                else:
                    # Partial consume
                    fraction = remaining / lot.qty
                    new_qty = lot.qty - remaining
                    new_basis = lot.cost_basis_brl * (Decimal("1") - fraction)
                    open_lots[key][0] = Lot(
                        trade_id=lot.trade_id, date=lot.date, ticker=lot.ticker,
                        qty=new_qty, cost_basis_brl=new_basis,
                    )
                    remaining = Decimal("0")

    positions: list[Position] = []
    for (broker, account_id, ticker), lots in open_lots.items():
        if not lots:
            continue
        total_qty = sum((l.qty for l in lots), start=Decimal("0"))
        total_basis = sum((l.cost_basis_brl for l in lots), start=Decimal("0"))
        avg_cost = total_basis / total_qty if total_qty > 0 else Decimal("0")
        positions.append(
            Position(
                broker=broker, account_id=account_id, ticker=ticker,
                qty=total_qty, avg_cost_brl=avg_cost,
                open_lots=tuple(lots),
            )
        )
    return positions


def drift_vs_target(strategy: str, target: dict[str, Decimal]) -> dict[str, Decimal]:
    """Realized weight per ticker within strategy minus target. Uses avg_cost_brl
    as value proxy (not mark-to-market) — MVP level; MTM comes in Task 8 when
    benchmarks fetch current prices."""
    trades = [t for t in storage.read_trades() if t.strategy == strategy]
    pos = positions_from_trades(trades)
    total = sum((p.qty * p.avg_cost_brl for p in pos), start=Decimal("0"))
    if total == 0:
        return {ticker: -target.get(ticker, Decimal("0")) for ticker in target}
    actual = {p.ticker: (p.qty * p.avg_cost_brl) / total for p in pos}
    return {
        ticker: actual.get(ticker, Decimal("0")) - target.get(ticker, Decimal("0"))
        for ticker in set(list(target) + list(actual))
    }
```

- [ ] **Step 6.4: Run tests to verify PASS**

```bash
.venv/bin/pytest ops/tests/test_positions.py -v
```

Expected: 6 PASS.

- [ ] **Step 6.5: Commit**

```bash
git add ops/core/positions.py ops/tests/test_positions.py
git commit -m "feat(ops): positions module + FIFO lot matching (Task 6/11)"
```

---

## Task 7: CLI scaffolding + `ops trade` group

**Files:**
- Create: `ops/cli/main.py`, `ops/cli/_common.py`, `ops/cli/trade.py`, `ops/tests/cli/test_smoke_trade.py`

- [ ] **Step 7.1: Write `ops/cli/main.py`**

```python
"""Entry point: `ops` typer app. Wire subcommand groups."""
from __future__ import annotations

import typer

from ops.cli import trade

app = typer.Typer(
    help="ops — Plano B operational platform (trades, DARFs, benchmarks).",
    no_args_is_help=True,
)

app.add_typer(trade.app, name="trade", help="Manage trade log.")


@app.command()
def version() -> None:
    """Print version + schema_version."""
    from ops.core.storage import SCHEMA_VERSION
    typer.echo(f"ops 0.1.0 (schema_version {SCHEMA_VERSION})")


if __name__ == "__main__":
    app()
```

- [ ] **Step 7.2: Write `ops/cli/_common.py`**

```python
"""Shared CLI utilities: pretty tables, confirmations, error formatting."""
from __future__ import annotations

from decimal import Decimal

import typer


def fmt_brl(v: Decimal) -> str:
    sign = "-" if v < 0 else ""
    abs_v = abs(v)
    return f"{sign}R$ {abs_v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_qty(v: Decimal) -> str:
    s = str(v.normalize())
    return s if "." in s else s + ".0"


def confirm(prompt: str) -> bool:
    return typer.confirm(prompt, default=False, abort=False)


def die(msg: str, code: int = 1) -> None:
    typer.secho(f"[ERROR] {msg}", fg=typer.colors.RED, err=True)
    raise typer.Exit(code)
```

- [ ] **Step 7.3: Write `ops/cli/trade.py`**

```python
"""`ops trade ...` subcommand group."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

import typer

from ops.cli._common import die, fmt_brl, fmt_qty
from ops.core import fx, storage
from ops.core.models import Trade

app = typer.Typer(help="Trade journal — add, list, show, delete, edit.")


def _next_trade_id(d: date) -> str:
    existing = storage.read_trades()
    prefix = f"T-{d.strftime('%Y%m%d')}"
    count = sum(1 for t in existing if t.trade_id.startswith(prefix))
    return f"{prefix}-{count + 1:03d}"


@app.command()
def add(
    ticker: str = typer.Option(..., "--ticker", "-t"),
    side: str = typer.Option(..., "--side", "-s", help="buy|sell"),
    qty: Decimal = typer.Option(..., "--qty", "-q"),
    price_native: Decimal = typer.Option(..., "--price", "-p"),
    currency: str = typer.Option("USD", "--currency"),
    fees_native: Decimal = typer.Option(Decimal("0"), "--fees"),
    d: str = typer.Option(None, "--date", help="YYYY-MM-DD, default today"),
    broker: str = typer.Option("inter_global", "--broker"),
    account_id: str = typer.Option("inter_global_placeholder", "--account"),
    strategy: str = typer.Option("plano_b", "--strategy"),
    instrument_type: str = typer.Option("etf", "--instrument-type"),
    instrument_domicile: str = typer.Option("us", "--domicile"),
    ptax: Optional[Decimal] = typer.Option(None, "--ptax",
        help="Override PTAX; default auto-fetch from BCB"),
    trade_type: str = typer.Option("swing", "--type"),
    notes: str = typer.Option("", "--notes"),
) -> None:
    """Add a new trade. PTAX auto-fetched unless --ptax given."""
    if side not in ("buy", "sell"):
        die(f"side must be buy|sell, got {side!r}")
    trade_date = date.fromisoformat(d) if d else date.today()
    ptax_venda = ptax if ptax is not None else (
        Decimal("1") if currency == "BRL" else fx.get_ptax(trade_date)
    )

    # Compute BRL values
    gross_native = qty * price_native
    gross_brl = gross_native * ptax_venda
    fees_brl = fees_native * ptax_venda
    cost_basis_brl = gross_brl + fees_brl if side == "buy" else Decimal("0")

    realized_gain_brl = Decimal("0")
    if side == "sell":
        # Compute FIFO realized gain using existing positions
        from ops.core.positions import positions_from_trades
        existing = storage.read_trades()
        ticker_lots = []
        for p in positions_from_trades(existing):
            if (p.broker == broker and p.account_id == account_id
                and p.ticker == ticker):
                ticker_lots = list(p.open_lots)
                break
        remaining = qty
        consumed_basis = Decimal("0")
        for lot in ticker_lots:
            if remaining <= 0:
                break
            take = min(lot.qty, remaining)
            fraction = take / lot.qty
            consumed_basis += lot.cost_basis_brl * fraction
            remaining -= take
        if remaining > 0:
            die(f"Insufficient FIFO qty: need {qty}, available "
                f"{qty - remaining}. Backfill buys first.")
        realized_gain_brl = gross_brl - fees_brl - consumed_basis

    trade_id = _next_trade_id(trade_date)
    trade = Trade(
        trade_id=trade_id, date=trade_date, broker=broker, account_id=account_id,
        strategy=strategy, ticker=ticker, instrument_type=instrument_type,
        instrument_domicile=instrument_domicile, side=side, qty=qty,
        price_native=price_native, currency=currency, fees_native=fees_native,
        ptax_venda=ptax_venda, cost_basis_brl=cost_basis_brl, gross_brl=gross_brl,
        realized_gain_brl=realized_gain_brl, trade_type=trade_type, notes=notes,
    )
    with storage.lock():
        storage.append_trade(trade)
    typer.secho(f"[OK] Trade {trade_id} registrado.", fg=typer.colors.GREEN)
    typer.echo(f"  Date      : {trade_date.isoformat()}")
    typer.echo(f"  {side.upper():4} {fmt_qty(qty)} {ticker} @ {price_native} {currency}")
    typer.echo(f"  PTAX      : {ptax_venda}")
    typer.echo(f"  Gross BRL : {fmt_brl(gross_brl)}")
    if side == "buy":
        typer.echo(f"  Cost basis: {fmt_brl(cost_basis_brl)}")
    else:
        typer.echo(f"  Realized  : {fmt_brl(realized_gain_brl)}")


@app.command("list")
def list_trades(
    strategy: Optional[str] = typer.Option(None, "--strategy"),
    ticker: Optional[str] = typer.Option(None, "--ticker"),
    broker: Optional[str] = typer.Option(None, "--broker"),
    side: Optional[str] = typer.Option(None, "--side"),
    since: Optional[str] = typer.Option(None, "--since"),
    until: Optional[str] = typer.Option(None, "--until"),
) -> None:
    """List trades with filters."""
    trades = storage.read_trades()
    if strategy:
        trades = [t for t in trades if t.strategy == strategy]
    if ticker:
        trades = [t for t in trades if t.ticker == ticker]
    if broker:
        trades = [t for t in trades if t.broker == broker]
    if side:
        trades = [t for t in trades if t.side == side]
    if since:
        d = date.fromisoformat(since)
        trades = [t for t in trades if t.date >= d]
    if until:
        d = date.fromisoformat(until)
        trades = [t for t in trades if t.date <= d]

    if not trades:
        typer.echo("(no trades)")
        return
    for t in sorted(trades, key=lambda t: (t.date, t.trade_id)):
        typer.echo(
            f"{t.trade_id}  {t.date.isoformat()}  {t.side:4}  "
            f"{fmt_qty(t.qty):>8} {t.ticker:<6}  @ {t.price_native} {t.currency}  "
            f"PTAX {t.ptax_venda}  "
            f"gain={fmt_brl(t.realized_gain_brl):>14}  [{t.strategy}]"
        )


@app.command()
def show(trade_id: str) -> None:
    """Show detail of one trade."""
    trades = storage.read_trades()
    match = [t for t in trades if t.trade_id == trade_id]
    if not match:
        die(f"Trade {trade_id} not found")
    t = match[0]
    for field_name in t.__dataclass_fields__:
        value = getattr(t, field_name)
        typer.echo(f"  {field_name:22}: {value}")
```

- [ ] **Step 7.4: Write smoke tests in `ops/tests/cli/test_smoke_trade.py`**

```python
"""Smoke tests for `ops trade ...` CLI."""
from datetime import date
from decimal import Decimal

from typer.testing import CliRunner

from ops.cli.main import app

runner = CliRunner()


def test_trade_add_buy(tmp_data_dir, requests_mock):
    requests_mock.get(
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados",
        json=[{"data": "20/04/2026", "valor": "5.1234"}],
    )
    result = runner.invoke(app, [
        "trade", "add",
        "--ticker", "SSO", "--side", "buy", "--qty", "10",
        "--price", "52.30", "--date", "2026-04-20",
    ])
    assert result.exit_code == 0, result.output
    assert "Trade T-20260420-001 registrado" in result.output
    assert "PTAX      : 5.1234" in result.output


def test_trade_list_empty(tmp_data_dir):
    result = runner.invoke(app, ["trade", "list"])
    assert result.exit_code == 0
    assert "(no trades)" in result.output


def test_trade_show_missing(tmp_data_dir):
    result = runner.invoke(app, ["trade", "show", "T-NOTEXIST-001"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_trade_add_then_list(tmp_data_dir, requests_mock):
    requests_mock.get(
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados",
        json=[{"data": "20/04/2026", "valor": "5.1234"}],
    )
    runner.invoke(app, [
        "trade", "add",
        "--ticker", "SSO", "--side", "buy", "--qty", "10",
        "--price", "52.30", "--date", "2026-04-20",
    ])
    result = runner.invoke(app, ["trade", "list"])
    assert result.exit_code == 0
    assert "T-20260420-001" in result.output
    assert "SSO" in result.output
```

- [ ] **Step 7.5: Run tests**

```bash
.venv/bin/pytest ops/tests/cli/test_smoke_trade.py -v
```

Expected: 4 PASS.

- [ ] **Step 7.6: Commit**

```bash
git add ops/cli/ ops/tests/cli/test_smoke_trade.py
git commit -m "feat(ops): CLI scaffolding + trade group (Task 7/11)"
```

---

## Task 8: `ops dividend` + `ops darf` CLI groups (+ carryforward persistence)

**Files:**
- Create: `ops/cli/dividend.py`, `ops/cli/darf.py`, `ops/tests/cli/test_smoke_darf.py`
- Modify: `ops/cli/main.py` (register groups)

- [ ] **Step 8.1: Write `ops/cli/dividend.py`**

```python
"""`ops dividend ...` subcommand group."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

import typer

from ops.cli._common import die, fmt_brl
from ops.core import fx, storage
from ops.core.models import Dividend

app = typer.Typer(help="Dividend journal (Plano B ETFs distribute; Lei 14.754 unifies).")


def _next_div_id(d: date) -> str:
    existing = storage.read_dividends()
    prefix = f"D-{d.strftime('%Y%m%d')}"
    count = sum(1 for x in existing if x.dividend_id.startswith(prefix))
    return f"{prefix}-{count + 1:03d}"


@app.command()
def add(
    ticker: str = typer.Option(..., "--ticker", "-t"),
    gross_usd: Decimal = typer.Option(..., "--gross-usd"),
    withheld_usd: Decimal = typer.Option(Decimal("0"), "--withheld-usd"),
    d: str = typer.Option(None, "--date", help="Payment date YYYY-MM-DD"),
    broker: str = typer.Option("inter_global", "--broker"),
    account_id: str = typer.Option("inter_global_placeholder", "--account"),
    ptax: Optional[Decimal] = typer.Option(None, "--ptax"),
    notes: str = typer.Option("", "--notes"),
) -> None:
    """Register a dividend payment. PTAX auto-fetched."""
    payment_date = date.fromisoformat(d) if d else date.today()
    ptax_venda = ptax if ptax is not None else fx.get_ptax(payment_date)
    net_usd = gross_usd - withheld_usd
    div = Dividend(
        dividend_id=_next_div_id(payment_date),
        payment_date=payment_date, broker=broker, account_id=account_id,
        ticker=ticker, gross_usd=gross_usd, withheld_us_tax_usd=withheld_usd,
        net_usd=net_usd, ptax_venda=ptax_venda,
        gross_brl=gross_usd * ptax_venda,
        withheld_us_tax_brl=withheld_usd * ptax_venda,
        net_brl=net_usd * ptax_venda, notes=notes,
    )
    with storage.lock():
        storage.append_dividend(div)
    typer.secho(f"[OK] Dividend {div.dividend_id} registrado.", fg=typer.colors.GREEN)
    typer.echo(f"  Gross BRL: {fmt_brl(div.gross_brl)}  (withheld "
               f"{fmt_brl(div.withheld_us_tax_brl)})")
    typer.secho(
        "[ALERT] Regime annual_14754: este valor entra no bucket rendimentos anual.\n"
        "[ALERT] Regime monthly_6015: lembrar de declarar Carnê-Leão (código 0190) "
        "até último dia útil do mês seguinte.",
        fg=typer.colors.YELLOW,
    )


@app.command("list")
def list_dividends(
    ticker: Optional[str] = typer.Option(None, "--ticker"),
    since: Optional[str] = typer.Option(None, "--since"),
    until: Optional[str] = typer.Option(None, "--until"),
) -> None:
    """List dividends with filters."""
    divs = storage.read_dividends()
    if ticker:
        divs = [d for d in divs if d.ticker == ticker]
    if since:
        s = date.fromisoformat(since)
        divs = [d for d in divs if d.payment_date >= s]
    if until:
        u = date.fromisoformat(until)
        divs = [d for d in divs if d.payment_date <= u]
    if not divs:
        typer.echo("(no dividends)")
        return
    for d in sorted(divs, key=lambda x: x.payment_date):
        typer.echo(
            f"{d.dividend_id}  {d.payment_date.isoformat()}  {d.ticker:<6}  "
            f"gross={fmt_brl(d.gross_brl):>12}  net={fmt_brl(d.net_brl):>12}"
        )
```

- [ ] **Step 8.2: Write `ops/cli/darf.py`**

```python
"""`ops darf ...` subcommand group."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

import typer

from ops.cli._common import die, fmt_brl
from ops.core import storage
from ops.core.models import CarryforwardBalance, Stream
from ops.core.tax import get_regime

app = typer.Typer(help="DARF calculator — preview, close, list, show, paid.")

DEFAULT_REGIME = "annual_14754"  # Can be made configurable via config.yaml in Task 11


def _current_carryforward(regime_name: str, stream: Stream) -> Decimal:
    """Latest balance_out for (regime, stream)."""
    balances = storage.read_carryforward()
    matching = [b for b in balances if b.regime == regime_name and b.stream == stream]
    if not matching:
        return Decimal("0")
    # Latest by period key (lexicographic works for both YYYY and YYYY-MM)
    latest = max(matching, key=lambda b: b.period)
    return latest.balance_out


@app.command()
def preview(
    regime: str = typer.Option(DEFAULT_REGIME, "--regime"),
    d: str = typer.Option(None, "--date", help="Any date inside the period"),
) -> None:
    """Compute DARFs for the period containing --date (or today) without committing."""
    r = get_regime(regime)
    ref = date.fromisoformat(d) if d else date.today()
    period_start, period_end = r.period_for(ref)

    trades = [t for t in storage.read_trades()
              if period_start <= t.date <= period_end]
    divs = [x for x in storage.read_dividends()
            if period_start <= x.payment_date <= period_end]
    carry_in = {s: _current_carryforward(regime, s) for s in r.streams}

    events = r.compute(trades, divs, carry_in, period_start, period_end)
    if not events:
        typer.echo(f"[PREVIEW] {regime} {r.period_key(period_end)}: nenhum DARF "
                   f"(sem ganho líquido positivo no período).")
        return
    for e in events:
        typer.echo(f"--- {e.darf_id} ({e.stream}, code {e.code}) ---")
        typer.echo(f"  Period          : {e.period_start} → {e.period_end}")
        typer.echo(f"  Due date        : {e.due_date}")
        typer.echo(f"  Gross gain      : {fmt_brl(e.gross_gain_brl)}")
        typer.echo(f"  Dividends       : {fmt_brl(e.dividends_brl)}")
        typer.echo(f"  Carryforward in : {fmt_brl(carry_in.get(e.stream, Decimal('0')))}")
        typer.echo(f"  Loss offset     : {fmt_brl(e.loss_offset_brl)}")
        typer.echo(f"  Net taxable     : {fmt_brl(e.net_taxable_brl)}")
        typer.echo(f"  Tax rate        : {e.tax_rate_applied * 100}%")
        typer.secho(f"  Tax due         : {fmt_brl(e.tax_due_brl)}",
                    fg=typer.colors.YELLOW, bold=True)


@app.command()
def close(
    regime: str = typer.Option(DEFAULT_REGIME, "--regime"),
    period: Optional[str] = typer.Option(None, "--period",
        help="YYYY-MM (monthly) or YYYY (annual). Defaults to period containing today."),
) -> None:
    """Compute + commit DARFs + update carryforward."""
    r = get_regime(regime)
    if period:
        if len(period) == 7:  # YYYY-MM
            y, m = int(period[:4]), int(period[5:7])
            ref = date(y, m, 15)
        elif len(period) == 4:
            ref = date(int(period), 6, 15)
        else:
            die(f"Invalid --period {period!r}")
    else:
        ref = date.today()
    period_start, period_end = r.period_for(ref)
    period_key = r.period_key(period_end)

    # Idempotency: reject if DARF already exists
    existing = [e for e in storage.read_darf_history()
                if e.regime == regime
                and e.period_start == period_start
                and e.period_end == period_end]
    if existing:
        die(f"DARF for {regime} {period_key} already exists. "
            f"Use `ops darf recompute --confirm`.")

    trades = [t for t in storage.read_trades()
              if period_start <= t.date <= period_end]
    divs = [x for x in storage.read_dividends()
            if period_start <= x.payment_date <= period_end]
    carry_in = {s: _current_carryforward(regime, s) for s in r.streams}

    events = r.compute(trades, divs, carry_in, period_start, period_end)

    # Compute new carryforward balances
    new_balances = []
    for stream in r.streams:
        # Accrue negative trade_type realized_gain + account for consumption
        accrued = sum(
            (-t.realized_gain_brl for t in trades
             if t.side == "sell"
             and (t.trade_type == stream if stream in ("swing", "daytrade") else True)
             and t.realized_gain_brl < 0),
            start=Decimal("0"),
        )
        consumed = sum(
            (e.loss_offset_brl for e in events if e.stream == stream),
            start=Decimal("0"),
        )
        balance_in = carry_in.get(stream, Decimal("0"))
        balance_out = balance_in + accrued - consumed
        if balance_out < 0:
            die(f"Carryforward invariant violated: balance_out={balance_out} "
                f"for {regime}/{stream} in {period_key}")
        new_balances.append(CarryforwardBalance(
            regime=regime, stream=stream, period=period_key,
            balance_in=balance_in, accrued_this_period=accrued,
            consumed_this_period=consumed, balance_out=balance_out,
        ))

    with storage.lock():
        for e in events:
            storage.append_darf_event(e)
        all_balances = storage.read_carryforward()
        # Replace any existing balance for this (regime, stream, period)
        all_balances = [
            b for b in all_balances
            if not (b.regime == regime and b.period == period_key)
        ] + new_balances
        storage.write_carryforward(all_balances)

    if not events:
        typer.echo(f"[OK] {regime} {period_key}: sem DARF (sem ganho). "
                   f"Carryforward atualizado.")
    else:
        for e in events:
            typer.secho(f"[OK] {e.darf_id} criado: "
                        f"{fmt_brl(e.tax_due_brl)} vence {e.due_date}.",
                        fg=typer.colors.GREEN)
    typer.echo(f"Carryforward saldos pós-período ({period_key}):")
    for b in new_balances:
        typer.echo(f"  {b.stream:<12}: balance_out = {fmt_brl(b.balance_out)}")


@app.command("list")
def list_darfs(
    unpaid: bool = typer.Option(False, "--unpaid"),
) -> None:
    """List DARFs. --unpaid filters pending."""
    events = storage.read_darf_history()
    if unpaid:
        events = [e for e in events if e.paid_at is None]
    if not events:
        typer.echo("(no DARFs)")
        return
    for e in sorted(events, key=lambda x: x.due_date):
        status = "PAID" if e.paid_at else "PENDING"
        typer.echo(f"{e.darf_id}  {status:<7}  due {e.due_date}  "
                   f"{fmt_brl(e.tax_due_brl):>14}  [{e.regime}/{e.stream}]")


@app.command()
def carryforward() -> None:
    """Show current carryforward balances per (regime, stream)."""
    balances = storage.read_carryforward()
    if not balances:
        typer.echo("(no carryforward data)")
        return
    # Group latest per (regime, stream)
    latest: dict[tuple[str, str], CarryforwardBalance] = {}
    for b in balances:
        key = (b.regime, b.stream)
        if key not in latest or b.period > latest[key].period:
            latest[key] = b
    for (regime, stream), b in sorted(latest.items()):
        typer.echo(f"{regime}/{stream:<12}  period {b.period}  "
                   f"balance = {fmt_brl(b.balance_out)}")


@app.command()
def paid(
    darf_id: str,
    d: str = typer.Option(None, "--date", help="Payment date YYYY-MM-DD"),
    proof: str = typer.Option("", "--proof", help="Path to receipt PDF"),
) -> None:
    """Mark a DARF as paid."""
    events = storage.read_darf_history()
    match_idx = next((i for i, e in enumerate(events) if e.darf_id == darf_id), None)
    if match_idx is None:
        die(f"DARF {darf_id} not found")
    paid_date = date.fromisoformat(d) if d else date.today()
    e = events[match_idx]
    updated = DarfEvent_replace(e, paid_at=paid_date, paid_proof_path=proof)
    events[match_idx] = updated
    # Rewrite whole file (small)
    with storage.lock():
        from ops.core.models import DarfEvent
        from dataclasses import fields as _fields
        storage._atomic_write(
            storage._path("darf_history.csv"),
            [storage._row_from_dataclass(ev) for ev in events],
            [f.name for f in _fields(DarfEvent)],
        )
    typer.secho(f"[OK] {darf_id} marked paid on {paid_date}.", fg=typer.colors.GREEN)


def DarfEvent_replace(e, **kwargs):
    from dataclasses import replace
    return replace(e, **kwargs)
```

- [ ] **Step 8.3: Register groups in `ops/cli/main.py`**

Edit `ops/cli/main.py`:

```python
"""Entry point: `ops` typer app."""
from __future__ import annotations

import typer

from ops.cli import darf, dividend, trade

app = typer.Typer(
    help="ops — Plano B operational platform (trades, DARFs, benchmarks).",
    no_args_is_help=True,
)

app.add_typer(trade.app, name="trade", help="Manage trade log.")
app.add_typer(dividend.app, name="dividend", help="Manage dividend log.")
app.add_typer(darf.app, name="darf", help="DARF calculator.")


@app.command()
def version() -> None:
    from ops.core.storage import SCHEMA_VERSION
    typer.echo(f"ops 0.1.0 (schema_version {SCHEMA_VERSION})")


if __name__ == "__main__":
    app()
```

- [ ] **Step 8.4: Write smoke tests in `ops/tests/cli/test_smoke_darf.py`**

```python
"""Smoke tests for `ops darf` + `ops dividend` CLI."""
from decimal import Decimal

from typer.testing import CliRunner

from ops.cli.main import app

runner = CliRunner()

BCB_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados"


def _bcb(mock, date_str: str, value: str) -> None:
    mock.get(BCB_URL, json=[{"data": date_str, "valor": value}])


def test_darf_preview_no_trades(tmp_data_dir):
    result = runner.invoke(app, ["darf", "preview", "--regime", "monthly_6015"])
    assert result.exit_code == 0
    assert "nenhum DARF" in result.output


def test_darf_close_full_cycle_monthly(tmp_data_dir, requests_mock):
    _bcb(requests_mock, "01/04/2026", "5.0000")
    _bcb(requests_mock, "15/04/2026", "5.1000")
    # Buy
    r1 = runner.invoke(app, [
        "trade", "add", "--ticker", "SSO", "--side", "buy",
        "--qty", "10", "--price", "50", "--date", "2026-04-01",
    ])
    assert r1.exit_code == 0, r1.output
    # Sell with gain
    r2 = runner.invoke(app, [
        "trade", "add", "--ticker", "SSO", "--side", "sell",
        "--qty", "10", "--price", "55", "--date", "2026-04-15",
    ])
    assert r2.exit_code == 0, r2.output
    # Close DARF for April
    r3 = runner.invoke(app, [
        "darf", "close", "--regime", "monthly_6015", "--period", "2026-04",
    ])
    assert r3.exit_code == 0, r3.output
    assert "DARF-M-202604" in r3.output
    # List shows the DARF
    r4 = runner.invoke(app, ["darf", "list"])
    assert "PENDING" in r4.output


def test_dividend_add_then_list(tmp_data_dir, requests_mock):
    _bcb(requests_mock, "15/06/2026", "5.2000")
    r1 = runner.invoke(app, [
        "dividend", "add", "--ticker", "SSO", "--gross-usd", "10",
        "--withheld-usd", "3", "--date", "2026-06-15",
    ])
    assert r1.exit_code == 0, r1.output
    assert "Dividend D-20260615-001" in r1.output
    r2 = runner.invoke(app, ["dividend", "list"])
    assert "SSO" in r2.output
```

- [ ] **Step 8.5: Run tests**

```bash
.venv/bin/pytest ops/tests/cli/test_smoke_darf.py -v
```

Expected: 3 PASS.

- [ ] **Step 8.6: Baseline check**

```bash
.venv/bin/pytest 2>&1 | tail -3
```

Expected: ≥ 830 passed (original 796 + 34+ ops).

- [ ] **Step 8.7: Commit**

```bash
git add ops/cli/dividend.py ops/cli/darf.py ops/cli/main.py ops/tests/cli/test_smoke_darf.py
git commit -m "feat(ops): CLI dividend + darf groups (Task 8/11)"
```

---

## Task 9: Benchmarks fetchers (BCB + yfinance + Tiingo reuse)

**Files:**
- Create: `ops/core/benchmarks.py`, `ops/tests/test_benchmarks.py`

- [ ] **Step 9.1: Write failing tests**

```python
"""Tests for ops/core/benchmarks.py — fetchers + equity curve normalizer."""
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from ops.core import benchmarks, storage
from ops.core.models import BenchmarkPoint


def test_ipca_fetch_from_bcb(tmp_data_dir, requests_mock):
    requests_mock.get(
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados",
        json=[
            {"data": "01/03/2026", "valor": "0.35"},
            {"data": "01/04/2026", "valor": "0.40"},
        ],
    )
    benchmarks.fetch_ipca()
    points = storage.read_benchmark_points()
    ipca = [p for p in points if p.series_id == "ipca_pct_monthly"]
    assert len(ipca) == 2
    assert ipca[0].value == Decimal("0.35")


def test_selic_daily_fetch(tmp_data_dir, requests_mock):
    requests_mock.get(
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados",
        json=[
            {"data": "20/04/2026", "valor": "0.0456"},
        ],
    )
    benchmarks.fetch_selic_daily()
    points = storage.read_benchmark_points()
    assert any(p.series_id == "selic_daily_pct" for p in points)


def test_equity_curve_selic_accumulates(tmp_data_dir):
    # Seed 3 daily SELIC bars @ 0.05% each
    storage.append_benchmark_points([
        BenchmarkPoint(
            date=date(2026, 4, 20 + i), series_id="selic_daily_pct",
            value=Decimal("0.05"), source="bcb_sgs_11",
            fetched_at=datetime.now(timezone.utc),
        )
        for i in range(3)
    ])
    curve = benchmarks.equity_curve_brl(
        series_id="selic_daily_pct",
        inception_date=date(2026, 4, 20),
        end_date=date(2026, 4, 22),
        base_value_brl=Decimal("100000"),
    )
    # After 3 days at 0.05%: 100_000 × 1.0005³ ≈ 100_150.08
    assert curve.iloc[-1]["value"] == pytest.approx(100150.08, rel=1e-4)


def test_equity_curve_single_bar_applies_return(tmp_data_dir):
    """Single bar on inception day applies its return — convention: each bar's
    return accrues on its own date."""
    storage.append_benchmark_points([
        BenchmarkPoint(
            date=date(2026, 4, 20), series_id="selic_daily_pct",
            value=Decimal("0.05"), source="bcb_sgs_11",
            fetched_at=datetime.now(timezone.utc),
        ),
    ])
    curve = benchmarks.equity_curve_brl(
        series_id="selic_daily_pct",
        inception_date=date(2026, 4, 20),
        end_date=date(2026, 4, 20),
        base_value_brl=Decimal("100000"),
    )
    # 100000 × 1.0005 = 100050
    assert curve.iloc[0]["value"] == pytest.approx(100050.0, rel=1e-6)
```

- [ ] **Step 9.2: Run tests to verify fail**

```bash
.venv/bin/pytest ops/tests/test_benchmarks.py -v
```

Expected: 4 FAILS.

- [ ] **Step 9.3: Write `ops/core/benchmarks.py`**

```python
"""Benchmark fetchers + equity curve normalizer.

Series:
- spy_usd            → Tiingo cache reuse (data/tiingo/SPY.csv)
- ivvb11_brl         → yfinance (IVVB11.SA)
- ibov_brl           → yfinance (^BVSP)
- ipca_pct_monthly   → BCB SGS 433
- selic_daily_pct    → BCB SGS 11
- selic_meta_annual  → BCB SGS 1178
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Iterable

import pandas as pd
import requests

from ops.core import fx, storage
from ops.core.models import BenchmarkPoint

BCB_SERIES_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"
BCB_TIMEOUT = 10.0


def _fetch_bcb_series(code: int, series_id: str, source: str) -> list[BenchmarkPoint]:
    resp = requests.get(BCB_SERIES_URL.format(code=code), timeout=BCB_TIMEOUT)
    resp.raise_for_status()
    out: list[BenchmarkPoint] = []
    now = datetime.now(timezone.utc)
    for item in resp.json():
        d_str = item["data"]  # DD/MM/YYYY
        d = date(int(d_str[6:10]), int(d_str[3:5]), int(d_str[0:2]))
        out.append(BenchmarkPoint(
            date=d, series_id=series_id, value=Decimal(str(item["valor"])),
            source=source, fetched_at=now,
        ))
    return out


def _known_dates(series_id: str) -> set[date]:
    return {p.date for p in storage.read_benchmark_points() if p.series_id == series_id}


def _incremental_append(series_id: str, new_points: list[BenchmarkPoint]) -> None:
    known = _known_dates(series_id)
    to_add = [p for p in new_points if p.date not in known]
    if to_add:
        storage.append_benchmark_points(to_add)


def fetch_ipca() -> None:
    points = _fetch_bcb_series(433, "ipca_pct_monthly", "bcb_sgs_433")
    _incremental_append("ipca_pct_monthly", points)


def fetch_selic_daily() -> None:
    points = _fetch_bcb_series(11, "selic_daily_pct", "bcb_sgs_11")
    _incremental_append("selic_daily_pct", points)


def fetch_selic_meta() -> None:
    points = _fetch_bcb_series(1178, "selic_meta_annual", "bcb_sgs_1178")
    _incremental_append("selic_meta_annual", points)


def fetch_ibov() -> None:
    """IBOV via yfinance. Fallback to no-op on network error."""
    try:
        import yfinance as yf
    except ImportError:
        return
    try:
        df = yf.Ticker("^BVSP").history(period="max")
    except Exception:
        return
    now = datetime.now(timezone.utc)
    points = [
        BenchmarkPoint(
            date=idx.date(), series_id="ibov_brl",
            value=Decimal(str(row["Close"])),
            source="yfinance", fetched_at=now,
        )
        for idx, row in df.iterrows()
        if not pd.isna(row["Close"])
    ]
    _incremental_append("ibov_brl", points)


def fetch_ivvb11() -> None:
    """IVVB11 via yfinance."""
    try:
        import yfinance as yf
    except ImportError:
        return
    try:
        df = yf.Ticker("IVVB11.SA").history(period="max")
    except Exception:
        return
    now = datetime.now(timezone.utc)
    points = [
        BenchmarkPoint(
            date=idx.date(), series_id="ivvb11_brl",
            value=Decimal(str(row["Close"])),
            source="yfinance", fetched_at=now,
        )
        for idx, row in df.iterrows()
        if not pd.isna(row["Close"])
    ]
    _incremental_append("ivvb11_brl", points)


def fetch_spy_usd_from_tiingo_cache() -> None:
    """Read existing data/tiingo/SPY.csv if present and import as benchmark points."""
    from pathlib import Path
    repo_root = Path(__file__).resolve().parents[2]
    tiingo_spy = repo_root / "data" / "tiingo" / "SPY.csv"
    if not tiingo_spy.exists():
        return
    df = pd.read_csv(tiingo_spy, parse_dates=["date"])
    now = datetime.now(timezone.utc)
    points = [
        BenchmarkPoint(
            date=row["date"].date(), series_id="spy_usd",
            value=Decimal(str(row["adjClose"] if "adjClose" in row else row["close"])),
            source="tiingo", fetched_at=now,
        )
        for _, row in df.iterrows()
    ]
    _incremental_append("spy_usd", points)


def fetch_all() -> None:
    """Refresh all benchmark series. Failures per-series logged, don't halt."""
    for fn in (fetch_ipca, fetch_selic_daily, fetch_selic_meta,
               fetch_ibov, fetch_ivvb11, fetch_spy_usd_from_tiingo_cache):
        try:
            fn()
        except Exception as exc:
            print(f"[WARN] {fn.__name__} failed: {exc}")


def equity_curve_brl(
    series_id: str,
    inception_date: date,
    end_date: date,
    base_value_brl: Decimal,
) -> pd.DataFrame:
    """Normalized equity curve reindexed to base_value_brl at inception_date."""
    points = sorted(
        [p for p in storage.read_benchmark_points() if p.series_id == series_id],
        key=lambda p: p.date,
    )
    points = [p for p in points if inception_date <= p.date <= end_date]
    if not points:
        return pd.DataFrame(columns=["date", "value"])

    rows = [{"date": p.date, "raw": float(p.value)} for p in points]
    df = pd.DataFrame(rows)

    if series_id in ("selic_daily_pct",):
        # Daily return in %: value_t = base × prod(1 + raw_k/100 for k ≤ t)
        # Convention: each bar's return applies on its own date.
        df["factor"] = 1 + df["raw"] / 100.0
        df["cumul"] = df["factor"].cumprod()
        df["value"] = df["cumul"] * float(base_value_brl)
    elif series_id == "ipca_pct_monthly":
        df["factor"] = 1 + df["raw"] / 100.0
        df["cumul"] = df["factor"].cumprod()
        df["value"] = df["cumul"] * float(base_value_brl)
    elif series_id in ("spy_usd",):
        # Convert USD price via PTAX then normalize
        df["ptax"] = [float(fx.get_ptax(d)) for d in df["date"]]
        df["brl"] = df["raw"] * df["ptax"]
        df["value"] = df["brl"] / df["brl"].iloc[0] * float(base_value_brl)
    else:
        # ibov_brl, ivvb11_brl: raw close price in BRL, just rebase
        df["value"] = df["raw"] / df["raw"].iloc[0] * float(base_value_brl)

    return df[["date", "value"]].copy()
```

- [ ] **Step 9.4: Run tests**

```bash
.venv/bin/pytest ops/tests/test_benchmarks.py -v
```

Expected: 4 PASS.

- [ ] **Step 9.5: Commit**

```bash
git add ops/core/benchmarks.py ops/tests/test_benchmarks.py
git commit -m "feat(ops): benchmarks fetchers + equity curve normalizer (Task 9/11)"
```

---

## Task 10: CLI benchmark + status groups + reports module

**Files:**
- Create: `ops/core/reports.py`, `ops/cli/benchmark.py`, `ops/cli/status.py`, `ops/tests/test_reports.py`, `ops/tests/cli/test_smoke_benchmark.py`
- Modify: `ops/cli/main.py`

- [ ] **Step 10.1: Write `ops/core/reports.py`**

```python
"""Markdown renderers for benchmark reports + status dashboard."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from io import StringIO

import pandas as pd

from ops.core import benchmarks, positions, storage

ENABLED_SERIES = ("spy_usd", "ivvb11_brl", "ibov_brl", "ipca_pct_monthly",
                  "selic_daily_pct")


def _strategy_equity_curve(strategy: str, inception: date, end: date,
                           base: Decimal) -> pd.DataFrame:
    """Simple strategy equity: cumulative realized_gain_brl + current notional."""
    trades = sorted(
        [t for t in storage.read_trades() if t.strategy == strategy
         and inception <= t.date <= end],
        key=lambda t: t.date,
    )
    rows = []
    equity = float(base)
    current_date = inception
    for t in trades:
        if t.date > current_date:
            rows.append({"date": current_date, "value": equity})
            current_date = t.date
        if t.side == "sell":
            equity += float(t.realized_gain_brl)
    rows.append({"date": end, "value": equity})
    return pd.DataFrame(rows)


def render_monthly_benchmark_report(year: int, month: int,
                                    strategy: str = "plano_b",
                                    base_value_brl: Decimal = Decimal("100000")
                                    ) -> str:
    """Build a full markdown report for the given year-month."""
    import calendar
    _, last = calendar.monthrange(year, month)
    period_start = date(year, month, 1)
    period_end = date(year, month, last)

    # Find strategy inception (first trade)
    strategy_trades = [t for t in storage.read_trades() if t.strategy == strategy]
    if not strategy_trades:
        return f"# Benchmark report {year}-{month:02d}\n\nNo {strategy} trades yet.\n"
    inception = min(t.date for t in strategy_trades)

    buf = StringIO()
    buf.write(f"# Benchmark report — {strategy} — {year}-{month:02d}\n\n")
    buf.write(f"Inception: {inception}\n")
    buf.write(f"Period end: {period_end}\n\n")
    buf.write("## Equity vs benchmarks (rebased 100 at inception)\n\n")
    buf.write("| Series | Value @ period_end | Return since inception |\n")
    buf.write("|---|---|---|\n")

    strat_curve = _strategy_equity_curve(strategy, inception, period_end,
                                         base_value_brl)
    if not strat_curve.empty:
        strat_final = strat_curve.iloc[-1]["value"]
        strat_ret = (strat_final / float(base_value_brl) - 1) * 100
        buf.write(f"| **{strategy}** | R$ {strat_final:,.2f} | {strat_ret:+.2f}% |\n")

    for series_id in ENABLED_SERIES:
        curve = benchmarks.equity_curve_brl(series_id, inception, period_end,
                                            base_value_brl)
        if curve.empty:
            buf.write(f"| {series_id} | (no data) | — |\n")
            continue
        final = curve.iloc[-1]["value"]
        ret = (final / float(base_value_brl) - 1) * 100
        buf.write(f"| {series_id} | R$ {final:,.2f} | {ret:+.2f}% |\n")

    return buf.getvalue()


def render_status_dashboard(strategy: str = "plano_b") -> str:
    """Compact CLI dashboard."""
    pos = [p for p in positions.current_positions() if True]  # all
    strategy_trades = [t for t in storage.read_trades() if t.strategy == strategy]
    unpaid_darfs = [e for e in storage.read_darf_history() if e.paid_at is None]
    carry = storage.read_carryforward()

    buf = StringIO()
    buf.write(f"=== ops status ({strategy}) ===\n")
    if strategy_trades:
        first = min(t.date for t in strategy_trades)
        last = max(t.date for t in strategy_trades)
        buf.write(f"Window: {first} → {last}  ({len(strategy_trades)} trades)\n")
    else:
        buf.write("Window: (no trades yet)\n")

    buf.write("\nCurrent positions:\n")
    if not pos:
        buf.write("  (none)\n")
    for p in pos:
        buf.write(f"  {p.broker}/{p.account_id}  {p.ticker:<6}  "
                  f"qty={p.qty}  avg_cost_brl={p.avg_cost_brl:.2f}\n")

    buf.write(f"\nDARFs pendentes: {len(unpaid_darfs)}\n")
    for e in unpaid_darfs:
        buf.write(f"  {e.darf_id}  due {e.due_date}  "
                  f"R$ {e.tax_due_brl:.2f}  [{e.regime}]\n")

    if carry:
        buf.write("\nCarryforward balances (latest per stream):\n")
        latest: dict = {}
        for b in carry:
            key = (b.regime, b.stream)
            if key not in latest or b.period > latest[key].period:
                latest[key] = b
        for (regime, stream), b in sorted(latest.items()):
            buf.write(f"  {regime}/{stream:<12}  {b.period}  "
                      f"R$ {b.balance_out:.2f}\n")

    return buf.getvalue()
```

- [ ] **Step 10.2: Write `ops/cli/benchmark.py`**

```python
"""`ops benchmark ...` subcommand group."""
from __future__ import annotations

from pathlib import Path

import typer

from ops.core import benchmarks, reports, storage

app = typer.Typer(help="Benchmarks — fetch, report, compare.")


@app.command()
def fetch(
    series: str = typer.Option("all", "--series",
        help="Comma-separated list or 'all'."),
) -> None:
    """Refresh benchmark series caches."""
    if series == "all":
        benchmarks.fetch_all()
    else:
        for s in series.split(","):
            fn = getattr(benchmarks, f"fetch_{s.strip()}", None)
            if fn is None:
                typer.echo(f"[WARN] unknown series {s!r}, skipping")
                continue
            fn()
    typer.secho("[OK] benchmark fetch done.", fg=typer.colors.GREEN)


@app.command()
def report(
    year: int = typer.Option(..., "--year"),
    month: int = typer.Option(..., "--month"),
    strategy: str = typer.Option("plano_b", "--strategy"),
    out: str = typer.Option(None, "--out", help="Write to file; default stdout"),
) -> None:
    """Generate monthly benchmark comparison report (markdown)."""
    md = reports.render_monthly_benchmark_report(year, month, strategy=strategy)
    if out:
        Path(out).write_text(md, encoding="utf-8")
        typer.echo(f"[OK] Report written to {out}")
    else:
        typer.echo(md)
```

- [ ] **Step 10.3: Write `ops/cli/status.py`**

```python
"""`ops status` quick dashboard."""
from __future__ import annotations

import typer

from ops.core import reports

app = typer.Typer(help="Quick dashboard.")


def main(strategy: str = typer.Option("plano_b", "--strategy")) -> None:
    typer.echo(reports.render_status_dashboard(strategy=strategy))
```

- [ ] **Step 10.4: Update `ops/cli/main.py`**

```python
"""Entry point."""
from __future__ import annotations

import typer

from ops.cli import benchmark, darf, dividend, status, trade

app = typer.Typer(
    help="ops — Plano B operational platform.",
    no_args_is_help=True,
)

app.add_typer(trade.app, name="trade")
app.add_typer(dividend.app, name="dividend")
app.add_typer(darf.app, name="darf")
app.add_typer(benchmark.app, name="benchmark")

# `ops status` as top-level command (no subgroup)
app.command(name="status")(status.main)


@app.command()
def version() -> None:
    from ops.core.storage import SCHEMA_VERSION
    typer.echo(f"ops 0.1.0 (schema_version {SCHEMA_VERSION})")


if __name__ == "__main__":
    app()
```

- [ ] **Step 10.5: Write tests `ops/tests/test_reports.py`**

```python
"""Tests for reports module — snapshot-style markers."""
from datetime import date

from ops.core import reports, storage
from ops.core.models import Trade
from decimal import Decimal


def test_status_dashboard_empty(tmp_data_dir):
    out = reports.render_status_dashboard()
    assert "ops status" in out
    assert "(none)" in out


def test_monthly_report_no_trades(tmp_data_dir):
    out = reports.render_monthly_benchmark_report(2026, 4)
    assert "No plano_b trades yet" in out
```

- [ ] **Step 10.6: Write smoke tests `ops/tests/cli/test_smoke_benchmark.py`**

```python
"""Smoke tests for ops benchmark + ops status."""
from typer.testing import CliRunner

from ops.cli.main import app

runner = CliRunner()


def test_status_empty(tmp_data_dir):
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "ops status" in result.output


def test_benchmark_report_no_data(tmp_data_dir):
    result = runner.invoke(app, ["benchmark", "report",
                                  "--year", "2026", "--month", "4"])
    assert result.exit_code == 0
    assert "No plano_b trades yet" in result.output
```

- [ ] **Step 10.7: Run tests**

```bash
.venv/bin/pytest ops/tests/test_reports.py ops/tests/cli/test_smoke_benchmark.py -v
```

Expected: 4 PASS.

- [ ] **Step 10.8: Commit**

```bash
git add ops/core/reports.py ops/cli/benchmark.py ops/cli/status.py ops/cli/main.py ops/tests/test_reports.py ops/tests/cli/test_smoke_benchmark.py
git commit -m "feat(ops): benchmark + status CLI + reports module (Task 10/11)"
```

---

## Task 11: README + E2E test + golden fixture + final polish

**Files:**
- Create: `ops/README.md` (full content), `ops/tests/fixtures/example_plano_b_2026/README.md`, `ops/tests/test_e2e_plano_b_workflow.py`
- Modify: `ops/README.md` (replace stub)

- [ ] **Step 11.1: Write E2E test `ops/tests/test_e2e_plano_b_workflow.py`**

```python
"""End-to-end test: init → buys → sells → DARF close → benchmark report."""
from typer.testing import CliRunner

from ops.cli.main import app

runner = CliRunner()
BCB_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados"


def _bcb(mock, date_str: str, value: str) -> None:
    mock.get(BCB_URL, json=[{"data": date_str, "valor": value}])


def test_e2e_plano_b_two_buys_one_sell_monthly_darf(tmp_data_dir, requests_mock):
    """Simulate April 2026: buy SSO twice, sell half with gain, close DARF."""
    # All PTAX fetches mocked to fixed rate for simplicity
    requests_mock.get(BCB_URL, json=[{"data": "15/04/2026", "valor": "5.0"}])

    # Buy 1
    r = runner.invoke(app, [
        "trade", "add", "--ticker", "SSO", "--side", "buy",
        "--qty", "10", "--price", "50", "--date", "2026-04-05",
    ])
    assert r.exit_code == 0, r.output

    # Buy 2
    r = runner.invoke(app, [
        "trade", "add", "--ticker", "SSO", "--side", "buy",
        "--qty", "10", "--price", "55", "--date", "2026-04-10",
    ])
    assert r.exit_code == 0, r.output

    # Sell 15 shares at $60 (FIFO: 10 from B1 @ $50 + 5 from B2 @ $55)
    r = runner.invoke(app, [
        "trade", "add", "--ticker", "SSO", "--side", "sell",
        "--qty", "15", "--price", "60", "--date", "2026-04-20",
    ])
    assert r.exit_code == 0, r.output

    # Preview April DARF
    r = runner.invoke(app, ["darf", "preview", "--regime", "monthly_6015",
                            "--date", "2026-04-15"])
    assert r.exit_code == 0
    assert "DARF-M-202604" in r.output
    assert "Tax due" in r.output

    # Close April DARF
    r = runner.invoke(app, ["darf", "close", "--regime", "monthly_6015",
                            "--period", "2026-04"])
    assert r.exit_code == 0
    assert "criado" in r.output

    # List shows pending DARF
    r = runner.invoke(app, ["darf", "list", "--unpaid"])
    assert "PENDING" in r.output

    # Status
    r = runner.invoke(app, ["status"])
    assert r.exit_code == 0
    assert "SSO" in r.output
```

- [ ] **Step 11.2: Run E2E**

```bash
.venv/bin/pytest ops/tests/test_e2e_plano_b_workflow.py -v
```

Expected: 1 PASS.

- [ ] **Step 11.3: Overwrite `ops/README.md` with full content**

Use the content below (long — see README template in Task 11 appendix).

```markdown
# ops/ — Operational platform for Plano B (MVP)

> Plataforma CLI para journal de trades, DARFs (dois regimes), dividendos,
> posições FIFO e comparação contra benchmarks (S&P500 em BRL, IBOV, IPCA,
> SELIC). Schema multi-account pronto para Planos A e C.
>
> **Source spec:** `docs/superpowers/specs/2026-04-20-ops-platform-plano-b-design.md`.
> **Strategy doc:** `docs/strategies/plano_b_3leg_letf_rotation.md`.

## Design decisions (Q1-Q6 locked)

### Q1 — Multi-account schema from day 1

`broker`, `account_id`, `strategy`, `instrument_domicile` em todo trade.
Plano A (Pepperstone CFD, futuro) e Plano C (buy-hold ETF factor)
entram adicionando linhas, zero migration.

### Q2 — Auto-PTAX via BCB SGS série 1

`get_ptax(date)` primeiro consulta cache local, depois API Banco
Central (série 1 = PTAX venda USD/BRL). Feriado/fim-de-semana:
fallback ao último dia útil anterior (convenção Receita). Manual
override via `--ptax 5.1234`.

### Q3 — Flat CSV files

7 arquivos em `ops/data/` (gitignored), schema_version + atomic
writes + flock. Volume esperado: ~500 trades em 10 anos.

### Q4 — Loss carryforward completo

Perdas acumuladas compensam ganhos futuros:

- **Monthly 6015:** swing e daytrade em streams independentes,
  carryforward mês-a-mês.
- **Annual 14754:** stream unificada `rendimentos`, carryforward
  ILIMITADO entre anos (Lei 14.754/2023, Art. 3°, §5).

### Q5 — Dividend tracking sem auto-Carnê-Leão

`ops dividend add` registra bruto + withholding IRS 30% + PTAX.
Alíquota progressiva (7.5%-27.5%) fica com contador/Excel no regime
mensal. No regime anual Lei 14.754, dividendos entram no bucket
rendimentos automaticamente.

### Q6 — Benchmarks hybrid

- `ops status` — tabela rápida.
- `ops benchmark report --year Y --month M` — markdown completo.
- Séries: **spy_usd** (Tiingo cache reuse) × PTAX, **ivvb11_brl**
  (yfinance), **ibov_brl** (yfinance ^BVSP), **ipca_pct_monthly**
  (BCB 433), **selic_daily_pct** (BCB 11), **selic_meta_annual**
  (BCB 1178). Todos rebased a 100 no inception.

## Tax regimes — qual usar?

Depende de como o **Informe de Rendimentos do Inter Global** classifica
os trades. Confirmar com contador antes do primeiro DARF real.

| Característica | monthly_6015 (legacy) | annual_14754 (Lei 14.754/2023, atual) |
|---|---|---|
| Cadence | mensal (12+/ano) | anual (1/ano) |
| DARF code | 6015 swing / 8523 daytrade | 0211 (ou 4600 legacy) |
| Isenção R$35k/mês | ❌ não aplica a ETF | ❌ não existe no regime novo |
| Dividendos | Carnê-Leão separado (código 0190) | incluídos no bucket rendimentos |
| Carryforward | mensal, por stream (swing/daytrade) | ilimitado entre anos, stream unificada |
| Vencimento | último útil do mês seguinte | último útil de abril ano seguinte (IRPF) |
| Alíquota | 15% swing / 20% daytrade | 15% flat |

**Recomendação:** default `annual_14754` no `config.yaml`; rodar
`ops darf preview` em ambos durante 2026 e comparar antes do primeiro
DARF real em 2027-04.

## Workflow típico Plano B

```bash
# 1. Primeira compra
ops trade add --ticker SSO --side buy --qty 10 --price 52.30 --date 2026-04-20

# 2. Check diário de sinais (futuro — signal module)
ops signal check --strategy plano_b

# 3. Após rebalance ou exit, registrar venda
ops trade add --ticker SSO --side sell --qty 5 --price 55.00 --date 2026-05-15

# 4. Ao receber dividendo
ops dividend add --ticker SSO --gross-usd 12.50 --withheld-usd 3.75 --date 2026-06-15

# 5. Fim de mês: preview DARF
ops darf preview --regime monthly_6015 --date 2026-05-31

# 6. Se confirmado, fechar DARF
ops darf close --regime monthly_6015 --period 2026-05

# 7. Recolher via sicalcnet, depois marcar pago
ops darf paid DARF-M-202605-SW --date 2026-06-28 --proof ~/darfs/202605.pdf

# 8. Mensal: benchmark report
ops benchmark report --year 2026 --month 5 --out reports/2026-05.md

# 9. Quick status
ops status
```

## Adicionar Planos A/C no futuro

- **Plano A (Pepperstone CFD):** `--broker pepperstone --strategy plano_a
  --instrument-type cfd`. Domicile depende do produto (CFD ≠ ETF
  subjacente). Tax model CFD: requer adição de regime próprio
  (Phase 5).
- **Plano C (buy-hold factor):** `--strategy plano_c --broker <br_broker>
  --instrument-type etf --domicile br`. Regime fiscal igual Plano B
  se ETF no exterior, ou monthly_6015 padrão BR se ETF na B3 (VOO
  pela Inter = US, IVVB11 = BR).

## Backup / disaster recovery

```bash
# Backup criptografado AES-256
ops export backup --out ~/backups/ops-$(date +%F).tar.gz --password

# Restaurar em máquina nova
tar xzf ops-2026-04-20.tar.gz -C /var/www/pessoal/ai-trade/
```

## DARF codes — referência

| Código | Regime | Uso |
|---|---|---|
| **6015** | monthly_6015 | Ganhos líquidos swing em renda variável (bolsa) |
| **8523** | monthly_6015 | Ganhos líquidos day-trade |
| **0190** | legacy | Carnê-Leão — rendimentos exterior (dividendos) |
| **0211** | annual_14754 | Cota única IRPF anual |
| **4600** | legacy | Ganho capital ativos moeda estrangeira (pré-14.754) |

## Legislação

- **Lei 11033/2004** — regime mensal de renda variável (swing 15%,
  daytrade 20%, compensação de prejuízo mês a mês).
- **Lei 14.754/2023** — regime anual atual de aplicações no exterior
  para residentes BR. Art. 2° (15% flat), Art. 3° §5 (carryforward
  ilimitado).
- **IN RFB 1.585/2015, Art. 58** — FIFO lot matching obrigatório.

## Tests

```bash
.venv/bin/pytest ops/tests/ -v
.venv/bin/pytest ops/tests/ --cov=ops/core --cov-report=term
```

## Citations

- `docs/investment-mandate.md` §4.7 — Inter Global operational facts.
- `reports/phase3_5b/PRODUCTION.md` — runbook produção Plano B.
- `books/summaries/advances_fin_ml.md, p.275-278` — threshold
  rebalance rationale.
- `jornada/2026-04-19/09-t+1-settlement-caveat-plano-b.md` — T+1
  caveat registrado.
```

- [ ] **Step 11.4: Baseline full suite**

```bash
.venv/bin/pytest 2>&1 | tail -3
```

Expected: ≥ 845 passed.

- [ ] **Step 11.5: Final lint pass**

```bash
.venv/bin/ruff check ops/
```

Expected: clean (or auto-fix with `ruff check --fix ops/`).

- [ ] **Step 11.6: Commit**

```bash
git add ops/README.md ops/tests/test_e2e_plano_b_workflow.py
git commit -m "feat(ops): README + E2E test + final polish (Task 11/11)"
```

---

## Post-implementation — deferred to Phase 5+

Documented in spec §10 — do NOT implement in MVP:

- `ops signal check` for Plano B (daily EMA-100/Donchian signals from
  Tiingo cache). Stubbed out but not required for fiscal workflow.
- `ops export backup --password` AES-256 encryption.
- `ops init` interactive wizard + `ops config show/set` runtime config.
- Plano A live features (CFD tax model, margin tracking, swap daily
  accrual).
- Web UI (FastAPI + HTMX + SQLite migration).
- Automatic Inter API integration.

These are logged in `docs/superpowers/specs/2026-04-20-ops-platform-plano-b-design.md` §10 as deferred — add them to `ROADMAP.md` Phase 5+ when prioritized.

---

## Self-review (verify before handoff)

**Spec coverage:**

- Q1 multi-account schema → Task 2 (models), Task 7 (CLI --broker --strategy) ✅
- Q2 PTAX auto-fetch → Task 3 (fx module) ✅
- Q3 flat CSV + schema_version + atomic → Task 2 (storage) ✅
- Q4 carryforward → Task 4 (monthly), Task 5 (annual), Task 8 (persistence) ✅
- Q5 dividends tracking → Task 8 (CLI) + Task 2 (model) ✅
- Q6 benchmarks hybrid → Task 9 (fetchers) + Task 10 (reports + status) ✅
- Two tax regimes plugable → Task 4 + Task 5 + factory `get_regime` ✅
- FIFO lot matching → Task 6 ✅
- DARF close idempotent → Task 8 `close` command ✅
- Zero network in pytest → all BCB/yfinance mocked via `requests_mock` ✅
- Pytest baseline ≥796 preserved → each task re-runs full suite ✅

**Deferred (documented, not in scope):**

- `ops signal check` module (Plano B daily signal from Tiingo)
- `ops init` interactive wizard
- `ops export backup` encrypted
- Property-based tests with hypothesis

These are Phase 5+ — spec §10 documents; they can be added as follow-up
tasks without changing the MVP foundation.
