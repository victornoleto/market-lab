# `tiingo_service` Lazy-Cache Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refatorar `TiingoSource` + `TiingoStorage` para aceitar eixo `frequency` (v1: `{daily, 1hour}`), rotear endpoints IEX/crypto/forex intraday, aplicar split/dividend adjust no IEX via daily cache (reusando `adjust.py`), e migrar o bulk daily existente (1660 tickers) para o novo layout `{freq}/prices/{ticker}.parquet`.

**Architecture:** Refactor in place (não módulo paralelo). Manifest vira `{ticker: {freq: entry}}` nested com `first_dt`/`last_dt` ISO datetime tz-naive e `requested_start`/`requested_end` para tracking v1. Slack per-`(asset_class, frequency)`. Migração opt-in via script com pgrep guard + backup automático + lockfile + teste de rollback. Split adjust via `adjust.py` existente (ratio `adj_close_daily/close_daily` derivado por dia de calendário, aplicado às bars intraday do mesmo dia).

**Tech Stack:** Python 3.12, `pandas`/`pyarrow` (já presentes), `requests`, `pytest` (padrão mock HTTP via `MagicMock` + `tmp_path`). Zero dependências novas.

**Pré-condição:** Smoke #1 retention probe já executado em 2026-04-15 17:47 com veredito PASS (Cenário A: SPY 5a, btcusd 208d, eurusd 416d). Log auditável em `logs/tiingo.log`.

**Baseline:** 377 testes verdes. Meta final: ~405 testes verdes. **Não quebrar baseline.**

**Commits esperados (split em 3 conforme spec §6.1):**
1. `feat(data): add frequency axis to tiingo storage + migrate script`
2. `feat(data): route tiingo source to IEX for 1h intraday with split adjust`
3. `feat(data): smoke intraday probe + unblock path docs`

---

## File Structure

**Criar:**
- `src/ai_trade/backtest/data/tiingo_migrate.py` (~180 lines) — `migrate_to_freq_layout(root, *, dry_run, force_ignore_running, skip_backup) -> MigrationReport`.
- `scripts/run_tiingo_migrate.py` (~60 lines) — CLI wrapper com flags `--dry-run`, `--root`, `--force-ignore-running`, `--skip-backup`.
- `tests/test_tiingo_migrate.py` (~260 lines) — testes de layout detect, dry-run, migração real, idempotência, pgrep guard, backup auto, rollback sim, lockfile.

**Modificar:**
- `src/ai_trade/backtest/data/tiingo_storage.py` — +120/-30 lines.
  - Nested manifest schema `{ticker: {freq: entry}}` com `first_dt`/`last_dt` ISO datetime + `requested_start`/`requested_end`.
  - `_COVERAGE_SLACK: dict[(asset_class, freq), timedelta]` per-asset-class.
  - `has(ticker, start, end, frequency)` aceita `date | datetime`.
  - `read/write` recebem `frequency` kwarg.
  - Layout físico `root/{freq}/{prices,meta}/{ticker}`.
  - `__post_init__` detecta lockfile `root/.migration.lock` e raise.
- `src/ai_trade/backtest/data/tiingo_source.py` — +180/-10 lines.
  - `frequency` kwarg com default `"daily"` (backwards-compat).
  - `_WHITELIST` por `(asset_class, frequency)`.
  - `_build_url` roteia equity/etf 1h → `/iex/{ticker}/prices`.
  - `_build_params` adiciona `resampleFreq` para intraday.
  - Split adjust v1 via `adjust.py` existente (derive ratio do daily cache).
  - `NotImplementedError` para equity/etf 1h sem daily cache populado.
  - `NotImplementedError` para index intraday (apontar ETF proxy).
  - `NotImplementedError` para frequências fora do whitelist v1.
- `tests/test_tiingo_storage.py` — +260 lines (novos testes).
- `tests/test_tiingo_source.py` — +320 lines (novos testes).

**Já criado (Smoke #1):**
- `scripts/tiingo_smoke_intraday.py` — executado em 2026-04-15 17:47, PASS.

**Sem mudança:** `pyproject.toml`, `adjust.py` (reusado como-está).

---

## Phase A — TiingoStorage refactor + migration module (commit #1)

### Task 1: Escrever teste de manifest nested schema

**Files:**
- Modify: `tests/test_tiingo_storage.py` (adicionar função de teste)
- Reference: `src/ai_trade/backtest/data/tiingo_storage.py` (ainda não modificado)

- [ ] **Step 1: Ler conteúdo atual dos testes para entender fixtures**

Run: `wc -l tests/test_tiingo_storage.py` (confirmar ~242 linhas atuais).

- [ ] **Step 2: Adicionar teste `test_manifest_nested_schema_roundtrip` no final de `tests/test_tiingo_storage.py`**

```python
def test_manifest_nested_schema_roundtrip(tmp_path: Path):
    """Manifest grava e carrega formato nested {ticker: {freq: entry}}."""
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    import pandas as pd

    storage = TiingoStorage(root=tmp_path)
    df = pd.DataFrame(
        {
            "open": [1.0], "high": [2.0], "low": [0.5],
            "close": [1.5], "adj_close": [1.5], "volume": [100.0],
        },
        index=pd.DatetimeIndex([pd.Timestamp("2024-01-02T09:30")], name="date"),
    )

    storage.write("AAPL", df, asset_class="equity", frequency="1hour")

    # Manifest nested
    assert "AAPL" in storage.manifest
    assert "1hour" in storage.manifest["AAPL"]
    entry = storage.manifest["AAPL"]["1hour"]
    assert entry["first_dt"].startswith("2024-01-02")
    assert entry["last_dt"].startswith("2024-01-02")
    assert entry["n_bars"] == 1
    assert entry["asset_class"] == "equity"
    assert "requested_start" in entry
    assert "requested_end" in entry

    # Round-trip via nova instância
    storage2 = TiingoStorage(root=tmp_path)
    assert storage2.manifest == storage.manifest
```

- [ ] **Step 3: Rodar teste, verificar que falha**

Run: `.venv/bin/python -m pytest tests/test_tiingo_storage.py::test_manifest_nested_schema_roundtrip -xvs`
Expected: FAIL — `write()` ainda não aceita `frequency` kwarg (TypeError) ou manifest ainda flat.

### Task 2: Refatorar `TiingoStorage` para manifest nested + datetime

**Files:**
- Modify: `src/ai_trade/backtest/data/tiingo_storage.py`

- [ ] **Step 1: Reler `tiingo_storage.py` integralmente (174 linhas atuais)**

- [ ] **Step 2: Substituir a assinatura de `write`, `has`, `read` para aceitar `frequency` kwarg**

```python
def write(
    self,
    ticker: str,
    df: pd.DataFrame,
    asset_class: str,
    frequency: str = "daily",
) -> None:
    """Persist df for (ticker, frequency), merging with any existing data.

    Nested manifest schema: {ticker: {freq: entry}}, first_dt/last_dt as
    ISO datetime tz-naive. requested_range fields capture what the CALLER
    asked for (used by §2.5 partial-fetch warning).
    """
    if df.empty:
        log.warning("skipping empty write for %s (freq=%s)", ticker, frequency)
        return

    path = self._price_path(ticker, frequency)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = pd.read_parquet(path)
        merged = pd.concat([existing, df])
        merged = merged[~merged.index.duplicated(keep="last")]
        merged = merged.sort_index()
    else:
        merged = df.sort_index()

    merged.to_parquet(path)

    first_dt = pd.Timestamp(merged.index.min()).tz_localize(None)
    last_dt = pd.Timestamp(merged.index.max()).tz_localize(None)

    ticker_entry = self._manifest.setdefault(ticker, {})
    ticker_entry[frequency] = {
        "first_dt": first_dt.isoformat(),
        "last_dt": last_dt.isoformat(),
        "n_bars": int(len(merged)),
        "asset_class": asset_class,
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
        "requested_start": first_dt.isoformat(),
        "requested_end": last_dt.isoformat(),
    }
    self._save_manifest()
```

- [ ] **Step 3: Adicionar método helper `_price_path(ticker, frequency) -> Path`**

```python
def _price_path(self, ticker: str, frequency: str = "daily") -> Path:
    safe = ticker.replace("/", "_")
    return self.root / frequency / _PRICES_DIR / f"{safe}.parquet"
```

Remover o `_price_path` antigo que não tem frequency.

- [ ] **Step 4: Atualizar `__post_init__` para criar `daily/prices` e `daily/meta`**

```python
def __post_init__(self) -> None:
    self.root = Path(self.root)
    (self.root / "daily" / _PRICES_DIR).mkdir(parents=True, exist_ok=True)
    (self.root / "daily" / _META_DIR).mkdir(parents=True, exist_ok=True)
    self._manifest_path = self.root / _MANIFEST_NAME
    self._lockfile = self.root / ".migration.lock"
    if self._lockfile.exists():
        raise RuntimeError(
            f"migração incompleta detectada em {self.root} "
            f"(lockfile {_LOCKFILE} presente); execute rollback antes de usar."
        )
    self._manifest = self._load_manifest()
```

Adicionar no topo do arquivo:
```python
_LOCKFILE = ".migration.lock"
```

- [ ] **Step 5: Rodar o teste novo**

Run: `.venv/bin/python -m pytest tests/test_tiingo_storage.py::test_manifest_nested_schema_roundtrip -xvs`
Expected: PASS.

### Task 3: Refatorar `has()` + `read()` para aceitar frequency + date|datetime

**Files:**
- Modify: `src/ai_trade/backtest/data/tiingo_storage.py`
- Modify: `tests/test_tiingo_storage.py`

- [ ] **Step 1: Adicionar teste `test_has_with_frequency_kwarg` em tests/test_tiingo_storage.py**

```python
def test_has_with_frequency_kwarg(tmp_path: Path):
    """has() respeita frequency isolado (AAPL daily ≠ AAPL 1hour)."""
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    import pandas as pd
    from datetime import date

    storage = TiingoStorage(root=tmp_path)
    df_daily = pd.DataFrame(
        {"open": [1.0], "high": [1.1], "low": [0.9], "close": [1.0],
         "adj_close": [1.0], "volume": [100.0]},
        index=pd.DatetimeIndex([pd.Timestamp("2024-01-02")], name="date"),
    )
    storage.write("AAPL", df_daily, asset_class="equity", frequency="daily")

    # AAPL daily existe, 1hour não
    assert storage.has("AAPL", date(2024, 1, 2), date(2024, 1, 2), frequency="daily")
    assert not storage.has("AAPL", date(2024, 1, 2), date(2024, 1, 2), frequency="1hour")
```

- [ ] **Step 2: Adicionar teste `test_has_accepts_date_or_datetime`**

```python
def test_has_accepts_date_or_datetime(tmp_path: Path):
    """has() aceita date e datetime sem crash."""
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    import pandas as pd
    from datetime import date, datetime

    storage = TiingoStorage(root=tmp_path)
    df = pd.DataFrame(
        {"open": [1.0], "high": [1.1], "low": [0.9], "close": [1.0],
         "adj_close": [1.0], "volume": [100.0]},
        index=pd.DatetimeIndex([pd.Timestamp("2024-01-02T14:00")], name="date"),
    )
    storage.write("SPY", df, asset_class="equity", frequency="1hour")

    assert storage.has("SPY", date(2024, 1, 2), date(2024, 1, 2), frequency="1hour")
    assert storage.has(
        "SPY",
        datetime(2024, 1, 2, 10, 0),
        datetime(2024, 1, 2, 20, 0),
        frequency="1hour",
    )
```

- [ ] **Step 3: Rodar testes, verificar que falham**

Run: `.venv/bin/python -m pytest tests/test_tiingo_storage.py -xvs -k "has_with_frequency_kwarg or has_accepts_date"`
Expected: FAIL — `has()` ainda não tem `frequency` kwarg ou não aceita datetime.

- [ ] **Step 4: Refatorar `has()` em tiingo_storage.py**

```python
def has(
    self,
    ticker: str,
    start: date | datetime,
    end: date | datetime,
    frequency: str = "daily",
) -> bool:
    """True iff the manifest range for (ticker, frequency) covers [start, end]."""
    entry = self._manifest.get(ticker, {}).get(frequency)
    if entry is None:
        return False

    asset_class = entry.get("asset_class", "equity")
    slack = _COVERAGE_SLACK.get(
        (asset_class, frequency), timedelta(days=7)
    )

    first_dt = datetime.fromisoformat(entry["first_dt"])
    last_dt = datetime.fromisoformat(entry["last_dt"])

    start_dt = start if isinstance(start, datetime) else datetime.combine(
        start, datetime.min.time()
    )
    end_dt = end if isinstance(end, datetime) else datetime.combine(
        end, datetime.min.time()
    )
    return first_dt <= start_dt + slack and last_dt + slack >= end_dt
```

- [ ] **Step 5: Adicionar tabela `_COVERAGE_SLACK` no topo do módulo**

```python
from datetime import timedelta

_COVERAGE_SLACK: dict[tuple[str, str], timedelta] = {
    ("equity", "daily"):  timedelta(days=7),
    ("etf",    "daily"):  timedelta(days=7),
    ("index",  "daily"):  timedelta(days=7),
    ("crypto", "daily"):  timedelta(days=2),
    ("forex",  "daily"):  timedelta(days=4),
    ("equity", "1hour"):  timedelta(hours=12),
    ("etf",    "1hour"):  timedelta(hours=12),
    ("crypto", "1hour"):  timedelta(hours=6),
    ("forex",  "1hour"):  timedelta(hours=48),
}
```

- [ ] **Step 6: Refatorar `read()` para aceitar frequency**

```python
def read(
    self,
    ticker: str,
    start: date | datetime | None = None,
    end: date | datetime | None = None,
    frequency: str = "daily",
) -> pd.DataFrame:
    entry = self._manifest.get(ticker, {}).get(frequency)
    if entry is None:
        raise KeyError(
            f"ticker {ticker!r} (freq={frequency!r}) not in storage manifest"
        )
    df = pd.read_parquet(self._price_path(ticker, frequency))
    if start is None and end is None:
        return df
    lo = pd.Timestamp(start) if start is not None else df.index.min()
    hi = pd.Timestamp(end) if end is not None else df.index.max()
    mask = (df.index >= lo) & (df.index <= hi)
    return df.loc[mask]
```

- [ ] **Step 7: Rodar testes novos + todos os pré-existentes de storage**

Run: `.venv/bin/python -m pytest tests/test_tiingo_storage.py -x`
Expected: PASS novos testes + quebrar testes pré-existentes que assumem API antiga.

### Task 4: Adaptar testes pré-existentes de storage para nova API

**Files:**
- Modify: `tests/test_tiingo_storage.py` (ajustar testes que quebraram)

- [ ] **Step 1: Rodar testes para listar exatamente os que quebraram**

Run: `.venv/bin/python -m pytest tests/test_tiingo_storage.py -x 2>&1 | head -80`

- [ ] **Step 2: Para cada teste quebrado, ajustar para passar frequency="daily" explícito**

Teste típico antes:
```python
storage.write("KR", df, asset_class="equity")
storage.has("KR", date(2024,1,1), date(2024,1,31))
```

Depois:
```python
storage.write("KR", df, asset_class="equity", frequency="daily")
storage.has("KR", date(2024,1,1), date(2024,1,31), frequency="daily")
```

- [ ] **Step 3: Ajustar assertions sobre manifest flat para nested**

Antes:
```python
assert storage.manifest["KR"]["n_bars"] == 10
```

Depois:
```python
assert storage.manifest["KR"]["daily"]["n_bars"] == 10
```

- [ ] **Step 4: Ajustar assertions sobre `first_date`/`last_date` para `first_dt`/`last_dt`**

Antes:
```python
assert storage.manifest["KR"]["first_date"] == "2024-01-01"
```

Depois:
```python
assert storage.manifest["KR"]["daily"]["first_dt"].startswith("2024-01-01")
```

- [ ] **Step 5: Rodar todos os testes de storage**

Run: `.venv/bin/python -m pytest tests/test_tiingo_storage.py -x`
Expected: PASS todos.

### Task 5: Adaptar testes pré-existentes de tiingo_source que usam storage

**Files:**
- Modify: `tests/test_tiingo_source.py` (ajustar calls afetadas)

- [ ] **Step 1: Rodar testes para listar quebrados**

Run: `.venv/bin/python -m pytest tests/test_tiingo_source.py -x 2>&1 | head -80`

- [ ] **Step 2: Ajustar TiingoSource.fetch() calls nos testes que instanciam storage diretamente**

O source em si não mudou ainda, mas o `TiingoStorage.write()` agora exige `frequency` kwarg — setups de fixture podem precisar `frequency="daily"`.

- [ ] **Step 3: Rodar testes, verificar que passam (source ainda na API antiga — OK temporariamente)**

Run: `.venv/bin/python -m pytest tests/test_tiingo_source.py -x`
Expected: PASS. Storage expõe API nova, source ainda assume API antiga internamente (chama `storage.write(...)` sem `frequency` → usa default `"daily"` → OK).

### Task 6: Escrever teste de slack per-(asset_class, freq)

**Files:**
- Modify: `tests/test_tiingo_storage.py`

- [ ] **Step 1: Adicionar teste `test_slack_per_asset_class_and_freq`**

```python
def test_slack_per_asset_class_and_freq(tmp_path: Path):
    """Crypto 1h slack é menor que equity 1h (24/7 vs RTH)."""
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    import pandas as pd
    from datetime import datetime

    storage = TiingoStorage(root=tmp_path)

    # Equity 1h — slack 12h
    df = pd.DataFrame(
        {"open": [1.0], "high": [1.1], "low": [0.9], "close": [1.0],
         "adj_close": [1.0], "volume": [100.0]},
        index=pd.DatetimeIndex(
            [pd.Timestamp("2024-01-02T14:00")], name="date",
        ),
    )
    storage.write("SPY", df, asset_class="equity", frequency="1hour")

    # Request 14h antes de first_dt: 12h slack permite, 6h não
    assert storage.has(
        "SPY",
        datetime(2024, 1, 2, 4, 0),  # 10h antes → slack 12h permite
        datetime(2024, 1, 2, 14, 0),
        frequency="1hour",
    )
    # 24h antes de first_dt → slack 12h NÃO cobre
    assert not storage.has(
        "SPY",
        datetime(2024, 1, 1, 0, 0),
        datetime(2024, 1, 2, 14, 0),
        frequency="1hour",
    )

    # Crypto 1h — slack 6h (mais apertado)
    storage.write(
        "BTCUSD",
        pd.DataFrame(
            {"open": [1.0], "high": [1.1], "low": [0.9], "close": [1.0],
             "adj_close": [1.0], "volume": [100.0]},
            index=pd.DatetimeIndex([pd.Timestamp("2024-01-02T14:00")], name="date"),
        ),
        asset_class="crypto",
        frequency="1hour",
    )
    # 10h antes — slack 6h NÃO permite
    assert not storage.has(
        "BTCUSD",
        datetime(2024, 1, 2, 4, 0),
        datetime(2024, 1, 2, 14, 0),
        frequency="1hour",
    )
    # 4h antes — slack 6h permite
    assert storage.has(
        "BTCUSD",
        datetime(2024, 1, 2, 10, 0),
        datetime(2024, 1, 2, 14, 0),
        frequency="1hour",
    )
```

- [ ] **Step 2: Rodar teste**

Run: `.venv/bin/python -m pytest tests/test_tiingo_storage.py::test_slack_per_asset_class_and_freq -xvs`
Expected: PASS (a tabela `_COVERAGE_SLACK` e o lookup em `has()` já foram implementados em Task 3).

### Task 7: Escrever teste para lockfile detection no __post_init__

**Files:**
- Modify: `tests/test_tiingo_storage.py`

- [ ] **Step 1: Adicionar teste `test_init_raises_on_lockfile_present`**

```python
def test_init_raises_on_lockfile_present(tmp_path: Path):
    """TiingoStorage(__post_init__) raise se lockfile .migration.lock existe."""
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage

    (tmp_path / ".migration.lock").write_text("in-progress\n", encoding="utf-8")

    import pytest
    with pytest.raises(RuntimeError, match="migração incompleta"):
        TiingoStorage(root=tmp_path)
```

- [ ] **Step 2: Rodar teste**

Run: `.venv/bin/python -m pytest tests/test_tiingo_storage.py::test_init_raises_on_lockfile_present -xvs`
Expected: PASS (lockfile detection já foi adicionado em Task 2 Step 4).

### Task 8: Escrever teste para requested_range tracking

**Files:**
- Modify: `tests/test_tiingo_storage.py`

- [ ] **Step 1: Adicionar teste `test_write_stores_requested_range_when_provided`**

```python
def test_write_stores_requested_range_when_provided(tmp_path: Path):
    """write() aceita requested_start/end e grava no manifest."""
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    import pandas as pd
    from datetime import datetime

    storage = TiingoStorage(root=tmp_path)
    df = pd.DataFrame(
        {"open": [1.0], "high": [1.1], "low": [0.9], "close": [1.0],
         "adj_close": [1.0], "volume": [100.0]},
        index=pd.DatetimeIndex(
            [pd.Timestamp("2024-04-15T14:00")], name="date"
        ),
    )
    storage.write(
        "SPY", df,
        asset_class="equity",
        frequency="1hour",
        requested_start=datetime(2020, 1, 1),
        requested_end=datetime(2024, 4, 15),
    )

    entry = storage.manifest["SPY"]["1hour"]
    assert entry["requested_start"].startswith("2020-01-01")
    assert entry["requested_end"].startswith("2024-04-15")
    # first_dt/last_dt refletem o que veio (o returned range)
    assert entry["first_dt"].startswith("2024-04-15")
    assert entry["last_dt"].startswith("2024-04-15")
```

- [ ] **Step 2: Rodar teste, verificar falha**

Run: `.venv/bin/python -m pytest tests/test_tiingo_storage.py::test_write_stores_requested_range_when_provided -xvs`
Expected: FAIL — `write()` ainda não aceita `requested_start`/`requested_end` kwargs.

- [ ] **Step 3: Adicionar kwargs ao `write()` em tiingo_storage.py**

```python
def write(
    self,
    ticker: str,
    df: pd.DataFrame,
    asset_class: str,
    frequency: str = "daily",
    requested_start: date | datetime | None = None,
    requested_end: date | datetime | None = None,
) -> None:
    ...
    # (após computar first_dt, last_dt)
    req_start_iso = (
        (requested_start if isinstance(requested_start, datetime)
         else datetime.combine(requested_start, datetime.min.time())
        ).isoformat()
        if requested_start is not None
        else first_dt.isoformat()
    )
    req_end_iso = (
        (requested_end if isinstance(requested_end, datetime)
         else datetime.combine(requested_end, datetime.min.time())
        ).isoformat()
        if requested_end is not None
        else last_dt.isoformat()
    )
    ticker_entry[frequency] = {
        ...
        "requested_start": req_start_iso,
        "requested_end": req_end_iso,
    }
```

- [ ] **Step 4: Rodar teste**

Run: `.venv/bin/python -m pytest tests/test_tiingo_storage.py::test_write_stores_requested_range_when_provided -xvs`
Expected: PASS.

### Task 9: Escrever todos os testes de migrate antes de implementar

**Files:**
- Create: `tests/test_tiingo_migrate.py`

- [ ] **Step 1: Criar `tests/test_tiingo_migrate.py` com header e fixtures**

```python
"""Tests for ai_trade.backtest.data.tiingo_migrate.

Tests cover:
- Layout detection (old single-freq vs new nested)
- Dry-run doesn't write
- Real migration moves files + rekeys manifest
- Idempotency (re-run is no-op)
- Raises on corrupt manifest
- Preserves datetime semantics (daily at midnight)
- pgrep guard blocks when bulk running
- force_ignore_running bypasses guard with warning
- backup automatic opt-out via skip_backup
- Migration rollback via lockfile simulation
- Lockfile blocks concurrent storage init
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest


@pytest.fixture
def old_layout_root(tmp_path: Path) -> Path:
    """Root populado com layout velho: prices/*.parquet + meta/*.json + manifest flat."""
    prices = tmp_path / "prices"
    meta = tmp_path / "meta"
    prices.mkdir(parents=True)
    meta.mkdir(parents=True)

    # 2 parquets sintéticos
    for ticker, data_range in [
        ("AAPL", ("2023-01-01", "2024-12-31")),
        ("SPY",  ("2020-01-01", "2024-12-31")),
    ]:
        dates = pd.date_range(data_range[0], data_range[1], freq="D")
        df = pd.DataFrame(
            {
                "open": [1.0] * len(dates),
                "high": [1.1] * len(dates),
                "low": [0.9] * len(dates),
                "close": [1.0] * len(dates),
                "adj_close": [1.0] * len(dates),
                "volume": [100.0] * len(dates),
            },
            index=dates,
        )
        df.index.name = "date"
        df.to_parquet(prices / f"{ticker}.parquet")
        (meta / f"{ticker}.json").write_text(
            json.dumps({"sector": "Tech"}), encoding="utf-8"
        )

    # Manifest flat (formato velho)
    manifest = {
        "AAPL": {
            "first_date": "2023-01-01",
            "last_date": "2024-12-31",
            "n_bars": 731,
            "asset_class": "equity",
            "fetched_at": "2026-04-10T12:00:00",
        },
        "SPY": {
            "first_date": "2020-01-01",
            "last_date": "2024-12-31",
            "n_bars": 1827,
            "asset_class": "etf",
            "fetched_at": "2026-04-10T12:00:00",
        },
    }
    (tmp_path / "manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    return tmp_path
```

- [ ] **Step 2: Adicionar testes estruturais (layout detect + dry-run + real)**

```python
def test_detects_old_layout_and_plans_moves(old_layout_root: Path):
    from ai_trade.backtest.data.tiingo_migrate import migrate_to_freq_layout

    report = migrate_to_freq_layout(old_layout_root, dry_run=True)

    assert report.dry_run is True
    assert report.moved_parquets == 0  # dry-run não movimenta
    # Plan lista moves esperados
    ops_str = "\n".join(report.operations)
    assert "prices/AAPL.parquet" in ops_str
    assert "daily/prices/AAPL.parquet" in ops_str
    assert "rekey manifest" in ops_str


def test_dry_run_does_not_write(old_layout_root: Path):
    from ai_trade.backtest.data.tiingo_migrate import migrate_to_freq_layout

    manifest_before = (old_layout_root / "manifest.json").read_text()
    files_before = sorted(str(p) for p in old_layout_root.rglob("*"))

    migrate_to_freq_layout(old_layout_root, dry_run=True, skip_backup=True)

    assert (old_layout_root / "manifest.json").read_text() == manifest_before
    files_after = sorted(str(p) for p in old_layout_root.rglob("*"))
    assert files_after == files_before


def test_real_migration_moves_files_and_rekeys_manifest(old_layout_root: Path):
    from ai_trade.backtest.data.tiingo_migrate import migrate_to_freq_layout

    report = migrate_to_freq_layout(
        old_layout_root, dry_run=False, skip_backup=True,
    )

    # Arquivos moveram
    assert (old_layout_root / "daily" / "prices" / "AAPL.parquet").exists()
    assert (old_layout_root / "daily" / "prices" / "SPY.parquet").exists()
    assert not (old_layout_root / "prices" / "AAPL.parquet").exists()
    assert (old_layout_root / "daily" / "meta" / "AAPL.json").exists()

    # Manifest rekeyed
    new_manifest = json.loads(
        (old_layout_root / "manifest.json").read_text()
    )
    assert "AAPL" in new_manifest
    assert "daily" in new_manifest["AAPL"]
    aapl = new_manifest["AAPL"]["daily"]
    assert aapl["first_dt"].startswith("2023-01-01")
    assert aapl["last_dt"].startswith("2024-12-31")
    assert aapl["n_bars"] == 731

    # Contadores no report
    assert report.moved_parquets == 2
    assert report.rekeyed_tickers == 2
    # Lockfile removido
    assert not (old_layout_root / ".migration.lock").exists()


def test_idempotent_on_already_migrated_root(old_layout_root: Path):
    from ai_trade.backtest.data.tiingo_migrate import migrate_to_freq_layout

    migrate_to_freq_layout(
        old_layout_root, dry_run=False, skip_backup=True,
    )
    report2 = migrate_to_freq_layout(
        old_layout_root, dry_run=False, skip_backup=True,
    )
    assert report2.moved_parquets == 0
    assert "layout já migrado" in "\n".join(report2.operations).lower()


def test_raises_on_corrupt_manifest(tmp_path: Path):
    from ai_trade.backtest.data.tiingo_migrate import migrate_to_freq_layout

    (tmp_path / "prices").mkdir()
    (tmp_path / "manifest.json").write_text("{{{", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        migrate_to_freq_layout(tmp_path, dry_run=False, skip_backup=True)


def test_preserves_datetime_semantics_daily_at_midnight(old_layout_root: Path):
    from ai_trade.backtest.data.tiingo_migrate import migrate_to_freq_layout

    migrate_to_freq_layout(
        old_layout_root, dry_run=False, skip_backup=True,
    )
    manifest = json.loads((old_layout_root / "manifest.json").read_text())
    # first_dt é ISO datetime com T00:00:00
    assert manifest["AAPL"]["daily"]["first_dt"] == "2023-01-01T00:00:00"
    assert manifest["AAPL"]["daily"]["last_dt"] == "2024-12-31T00:00:00"
```

- [ ] **Step 3: Adicionar testes de guards (pgrep, backup, rollback, lockfile)**

```python
def test_pgrep_guard_blocks_when_bulk_running(old_layout_root: Path):
    from ai_trade.backtest.data import tiingo_migrate

    def fake_pgrep(*args, **kwargs):
        # subprocess.run mock — retorna returncode=0 (process found)
        class Result:
            returncode = 0
            stdout = "12345\n"
        return Result()

    with patch.object(tiingo_migrate, "_pgrep_bulk", return_value=[12345]):
        with pytest.raises(RuntimeError, match="Bulk Tiingo em execução"):
            tiingo_migrate.migrate_to_freq_layout(
                old_layout_root, dry_run=False, skip_backup=True,
            )


def test_force_ignore_running_bypasses_guard_with_warning(
    old_layout_root: Path, caplog,
):
    from ai_trade.backtest.data import tiingo_migrate
    import logging

    with patch.object(tiingo_migrate, "_pgrep_bulk", return_value=[12345]):
        with caplog.at_level(logging.WARNING):
            report = tiingo_migrate.migrate_to_freq_layout(
                old_layout_root,
                dry_run=False,
                force_ignore_running=True,
                skip_backup=True,
            )
    assert report.moved_parquets == 2
    assert any("bulk Tiingo ativo" in r.message.lower() for r in caplog.records)


def test_backup_automatico_cria_tarball_e_opt_out_via_skip_backup(
    old_layout_root: Path,
):
    from ai_trade.backtest.data import tiingo_migrate

    # Default: backup acontece
    with patch.object(tiingo_migrate, "_pgrep_bulk", return_value=[]):
        report = tiingo_migrate.migrate_to_freq_layout(
            old_layout_root, dry_run=False,
        )
    # Tarball criado no parent do root
    backups = list(old_layout_root.parent.glob("*_premigrate_*.tar.gz"))
    assert len(backups) >= 1
    assert any("backup" in op for op in report.operations)


def test_migration_rollback_lockfile_persists_on_manifest_failure(
    old_layout_root: Path,
):
    """Se _save_manifest falha, lockfile persiste e arquivos são recuperáveis."""
    from ai_trade.backtest.data import tiingo_migrate

    def boom(self_, path, content):
        raise OSError("disk full simulated")

    with patch.object(tiingo_migrate, "_pgrep_bulk", return_value=[]):
        with patch.object(
            tiingo_migrate,
            "_persist_manifest",
            side_effect=boom,
        ):
            with pytest.raises(OSError, match="disk full simulated"):
                tiingo_migrate.migrate_to_freq_layout(
                    old_layout_root, dry_run=False, skip_backup=True,
                )
    # Lockfile presente (sinal de migração interrompida)
    assert (old_layout_root / ".migration.lock").exists()


def test_lockfile_blocks_concurrent_storage_init(old_layout_root: Path):
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage

    (old_layout_root / ".migration.lock").write_text("x", encoding="utf-8")
    with pytest.raises(RuntimeError, match="migração incompleta"):
        TiingoStorage(root=old_layout_root)
```

- [ ] **Step 4: Rodar todos os testes de migrate (devem falhar — módulo não existe)**

Run: `.venv/bin/python -m pytest tests/test_tiingo_migrate.py -x 2>&1 | head -20`
Expected: ModuleNotFoundError: ai_trade.backtest.data.tiingo_migrate.

### Task 10: Implementar `tiingo_migrate.py` minimal (estrutura + migração básica)

**Files:**
- Create: `src/ai_trade/backtest/data/tiingo_migrate.py`

- [ ] **Step 1: Criar o módulo com docstring + MigrationReport dataclass + constantes**

```python
"""Migração one-shot do layout single-freq para nested-freq no TiingoStorage.

Mudanças:
- Old: root/{prices,meta}/{ticker}.parquet + flat manifest.
- New: root/{freq}/{prices,meta}/{ticker}.parquet + nested manifest.

Guards v1:
- pgrep -f tiingo_bulk_download (bloqueia se ativo, a menos que
  force_ignore_running=True).
- Backup automático via scripts/tiingo_backup.py ou tar direto (opt-out
  via skip_backup=True).
- Lockfile root/.migration.lock durante a execução; removido no final.

Idempotência: se root/daily/prices/ já existe, no-op.
"""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
import tarfile
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

log = logging.getLogger(__name__)

_LOCKFILE = ".migration.lock"
_MANIFEST_NAME = "manifest.json"


@dataclass
class MigrationReport:
    moved_parquets: int = 0
    moved_meta_files: int = 0
    rekeyed_tickers: int = 0
    elapsed_seconds: float = 0.0
    dry_run: bool = False
    operations: list[str] = field(default_factory=list)
```

- [ ] **Step 2: Adicionar função `_pgrep_bulk() -> list[int]`**

```python
def _pgrep_bulk() -> list[int]:
    """Return list of PIDs matching `tiingo_bulk_download`, or []."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "tiingo_bulk_download"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []
    if result.returncode != 0:
        return []
    return [int(pid) for pid in result.stdout.split() if pid.isdigit()]
```

- [ ] **Step 3: Adicionar função `_run_backup(root: Path) -> str`**

```python
def _run_backup(root: Path) -> str:
    """Create a tarball of `root` at `root.parent/{name}_premigrate_<ts>.tar.gz`."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_name = f"{root.name}_premigrate_{ts}.tar.gz"
    backup_path = root.parent / backup_name
    with tarfile.open(backup_path, "w:gz") as tar:
        tar.add(root, arcname=root.name)
    return str(backup_path)
```

- [ ] **Step 4: Adicionar função `_persist_manifest(path: Path, content: dict)`**

```python
def _persist_manifest(path: Path, content: dict) -> None:
    """Write manifest atomically (separate function for test monkeypatching)."""
    path.write_text(
        json.dumps(content, indent=2, sort_keys=True),
        encoding="utf-8",
    )
```

- [ ] **Step 5: Implementar função principal `migrate_to_freq_layout`**

```python
def migrate_to_freq_layout(
    root: Path,
    *,
    dry_run: bool = False,
    force_ignore_running: bool = False,
    skip_backup: bool = False,
) -> MigrationReport:
    """Migrate root/{prices,meta}/*.parquet → root/daily/{prices,meta}/*.

    See module docstring for full contract.
    """
    root = Path(root)
    start_ts = time.time()
    report = MigrationReport(dry_run=dry_run)

    # 1. pgrep guard
    active_pids = _pgrep_bulk()
    if active_pids and not force_ignore_running:
        raise RuntimeError(
            f"Bulk Tiingo em execução (PID(s) {active_pids}); pare-os antes "
            f"de migrar OU passe force_ignore_running=True (risco: split-brain)."
        )
    if active_pids and force_ignore_running:
        log.warning(
            "bulk Tiingo ativo (PIDs=%s) — prosseguindo com force_ignore_running",
            active_pids,
        )
    report.operations.append(
        f"check: pgrep tiingo_bulk_download → {len(active_pids)} found"
    )

    # 2. Idempotência
    if (root / "daily" / "prices").exists():
        report.operations.append("layout já migrado — no-op")
        report.elapsed_seconds = time.time() - start_ts
        return report

    # 3. Nothing to migrate
    old_prices = root / "prices"
    if not old_prices.exists():
        report.operations.append(f"root vazio ({root}/prices ausente) — no-op")
        report.elapsed_seconds = time.time() - start_ts
        return report

    # 4. Load + validate manifest
    manifest_path = root / _MANIFEST_NAME
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {}

    # 5. Dry-run: just plan
    if dry_run:
        for parquet in sorted(old_prices.glob("*.parquet")):
            report.operations.append(
                f"mv {parquet.relative_to(root)} → daily/{parquet.relative_to(root)}"
            )
        old_meta = root / "meta"
        if old_meta.exists():
            for meta_file in sorted(old_meta.glob("*.json")):
                report.operations.append(
                    f"mv {meta_file.relative_to(root)} → "
                    f"daily/{meta_file.relative_to(root)}"
                )
        for ticker in sorted(manifest.keys()):
            report.operations.append(
                f"rekey manifest[{ticker}] → manifest[{ticker}][daily]"
            )
        report.elapsed_seconds = time.time() - start_ts
        return report

    # 6. Real migration: backup → lockfile → mv → rekey → save → cleanup
    if not skip_backup:
        backup_path = _run_backup(root)
        report.operations.append(f"backup: {backup_path}")

    # Lockfile sinaliza migração em progresso
    lockfile = root / _LOCKFILE
    lockfile.write_text(
        f"migration started {datetime.now().isoformat()}\n",
        encoding="utf-8",
    )
    report.operations.append(f"lockfile: {lockfile.name} created")

    # Move parquets
    new_prices = root / "daily" / "prices"
    new_prices.mkdir(parents=True, exist_ok=True)
    for parquet in sorted(old_prices.glob("*.parquet")):
        dest = new_prices / parquet.name
        shutil.move(str(parquet), str(dest))
        report.operations.append(f"mv {parquet.name} → daily/prices/")
        report.moved_parquets += 1
    try:
        old_prices.rmdir()
    except OSError:
        pass  # not empty — user can inspect

    # Move meta
    old_meta = root / "meta"
    new_meta = root / "daily" / "meta"
    new_meta.mkdir(parents=True, exist_ok=True)
    if old_meta.exists():
        for meta_file in sorted(old_meta.glob("*.json")):
            dest = new_meta / meta_file.name
            shutil.move(str(meta_file), str(dest))
            report.operations.append(f"mv meta/{meta_file.name} → daily/meta/")
            report.moved_meta_files += 1
        try:
            old_meta.rmdir()
        except OSError:
            pass

    # Rekey manifest
    new_manifest = {}
    for ticker, old_entry in manifest.items():
        # old_entry: {first_date, last_date, n_bars, asset_class, fetched_at}
        first_date = old_entry.get("first_date", "1990-01-01")
        last_date = old_entry.get("last_date", "1990-01-01")
        new_entry = {
            "first_dt": f"{first_date}T00:00:00",
            "last_dt": f"{last_date}T00:00:00",
            "n_bars": old_entry.get("n_bars", 0),
            "asset_class": old_entry.get("asset_class", "equity"),
            "fetched_at": old_entry.get("fetched_at", "1990-01-01T00:00:00"),
            "requested_start": f"{first_date}T00:00:00",
            "requested_end": f"{last_date}T00:00:00",
        }
        new_manifest[ticker] = {"daily": new_entry}
        report.rekeyed_tickers += 1
        report.operations.append(f"rekey {ticker} → nested daily")

    # Persistir manifest NO FIM (point-of-no-return tardio)
    _persist_manifest(manifest_path, new_manifest)
    report.operations.append(f"persisted manifest.json ({len(new_manifest)} tickers)")

    # Remover lockfile
    lockfile.unlink()
    report.operations.append("lockfile removed")

    report.elapsed_seconds = time.time() - start_ts
    return report
```

- [ ] **Step 6: Rodar todos os testes de migrate**

Run: `.venv/bin/python -m pytest tests/test_tiingo_migrate.py -x`
Expected: PASS para todos os estruturais (detect, dry-run, real, idempotent, corrupt, datetime, pgrep, force_ignore, backup, rollback, lockfile). Se algum falhar, ajustar minimamente.

### Task 11: Criar `scripts/run_tiingo_migrate.py`

**Files:**
- Create: `scripts/run_tiingo_migrate.py`

- [ ] **Step 1: Escrever o CLI wrapper**

```python
#!/usr/bin/env python3
"""CLI wrapper for migrate_to_freq_layout.

Usage::

    uv run python scripts/run_tiingo_migrate.py --dry-run
    uv run python scripts/run_tiingo_migrate.py
    uv run python scripts/run_tiingo_migrate.py --force-ignore-running --skip-backup

Default `--root` is `data/tiingo/`. Logs append to `logs/tiingo.log`.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from ai_trade.backtest.data.tiingo_migrate import migrate_to_freq_layout


def _log(msg: str) -> None:
    stamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{stamp}] tiingo-migrate {msg}\n"
    log_path = Path(__file__).resolve().parents[1] / "logs" / "tiingo.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line)


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate Tiingo storage to nested-freq layout.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("data/tiingo"),
        help="Storage root (default: data/tiingo)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Plan only, don't mutate")
    parser.add_argument(
        "--force-ignore-running",
        action="store_true",
        help="Bypass pgrep guard (DANGEROUS — may cause split-brain)",
    )
    parser.add_argument(
        "--skip-backup",
        action="store_true",
        help="Don't create pre-migration tarball (use if you have external backup)",
    )
    args = parser.parse_args()

    _log(
        f"START root={args.root} dry_run={args.dry_run} "
        f"force_ignore_running={args.force_ignore_running} "
        f"skip_backup={args.skip_backup}"
    )
    print(f"Root: {args.root}")
    print(f"Dry-run: {args.dry_run}")
    print()

    try:
        report = migrate_to_freq_layout(
            args.root,
            dry_run=args.dry_run,
            force_ignore_running=args.force_ignore_running,
            skip_backup=args.skip_backup,
        )
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        _log(f"FAIL RuntimeError: {exc}")
        return 1

    print(f"Operations planned/executed: {len(report.operations)}")
    for op in report.operations:
        print(f"  - {op}")
    print()
    print(f"Moved parquets:  {report.moved_parquets}")
    print(f"Moved meta:      {report.moved_meta_files}")
    print(f"Rekeyed tickers: {report.rekeyed_tickers}")
    print(f"Elapsed:         {report.elapsed_seconds:.2f}s")
    _log(
        f"DONE moved_parquets={report.moved_parquets} "
        f"rekeyed_tickers={report.rekeyed_tickers} "
        f"elapsed={report.elapsed_seconds:.2f}s"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Verificar que `uv run python scripts/run_tiingo_migrate.py --help` funciona**

Run: `.venv/bin/python scripts/run_tiingo_migrate.py --help`
Expected: mostra usage sem erro.

### Task 12: Executar migração dry-run contra `data/tiingo/` real

**Files:** (não modifica, apenas executa)

- [ ] **Step 1: Parar qualquer bulk Tiingo em execução (se houver)**

Run: `pgrep -f tiingo_bulk_download || echo "no bulk running"`
Se houver PID → `kill <PID>` e re-checar.

- [ ] **Step 2: Rodar dry-run**

Run: `.venv/bin/python scripts/run_tiingo_migrate.py --dry-run`
Expected: lista ~1660 mv operations + ~1660 rekey operations. Operations planned: ~3320+.
Não deve mutar nada.

- [ ] **Step 3: Confirmar que `data/tiingo/prices/` continua intacto**

Run: `ls data/tiingo/prices/ | wc -l`
Expected: ~1660 (ou número pré-existente).

### Task 13: Executar migração real (com backup automático)

**Files:** (não modifica código, apenas executa)

- [ ] **Step 1: Confirmar backup existente suficiente**

Run: `ls -lh data/tiingo_backup_20260415-0958.tar.gz`
Expected: ~145 MB — backup recente já existe.

- [ ] **Step 2: Executar migração real**

Run: `.venv/bin/python scripts/run_tiingo_migrate.py`
Expected: cria novo `data/tiingo_premigrate_<ts>.tar.gz`, move todos parquets, rekey manifest, remove lockfile. Moved parquets: ~1660.

- [ ] **Step 3: Verificar novo layout**

Run:
```
ls data/tiingo/daily/prices/ | wc -l
ls data/tiingo/daily/meta/ | wc -l
test ! -d data/tiingo/prices && echo "old prices/ removed"
test ! -f data/tiingo/.migration.lock && echo "lockfile cleaned up"
```
Expected: ~1660 parquets, ~1660 metas, old dirs removed, no lockfile.

- [ ] **Step 4: Verificar manifest nested**

Run: `.venv/bin/python -c "import json; m=json.load(open('data/tiingo/manifest.json')); t=next(iter(m)); print(t, list(m[t].keys()), m[t]['daily'])"`
Expected: ticker name, `['daily']`, dict com first_dt/last_dt/n_bars/asset_class/fetched_at/requested_start/requested_end.

- [ ] **Step 5: Sanity check: leitura pos-migração funciona**

Run: `.venv/bin/python -c "from ai_trade.backtest.data.tiingo_storage import TiingoStorage; s=TiingoStorage(root='data/tiingo'); print('tickers:', len(s.manifest)); df=s.read(next(iter(s.manifest)), frequency='daily'); print('shape:', df.shape)"`
Expected: contagem de tickers + shape do parquet lido.

### Task 14: Garantir baseline 377 verde + commit #1

**Files:** (só execução + commit)

- [ ] **Step 1: Rodar suite completa**

Run: `.venv/bin/python -m pytest -q`
Expected: ~388/388 verdes (377 baseline + ~11 novos de storage/migrate). Se quebrou, investigar antes de commitar.

- [ ] **Step 2: Git status para revisar**

Run: `git status`

- [ ] **Step 3: Commit #1**

Run:
```
git add src/ai_trade/backtest/data/tiingo_storage.py \
        src/ai_trade/backtest/data/tiingo_migrate.py \
        scripts/run_tiingo_migrate.py \
        tests/test_tiingo_storage.py \
        tests/test_tiingo_migrate.py
git commit -m "$(cat <<'EOF'
feat(data): add frequency axis to tiingo storage + migrate script

Storage now keys manifest entries by (ticker, frequency) nested dict,
with first_dt/last_dt as ISO datetime tz-naive + requested_start/
requested_end tracking for partial-fetch Warning (spec v3 §2.5).
Coverage slack is per-(asset_class, frequency), so crypto 24/7 and forex
weekend-close don't share equity RTH's 12h window (§2.4).

Layout: root/{freq}/{prices,meta}/{ticker}.parquet (was root/{prices,
meta}/{ticker}.parquet). Migration script tiingo_migrate.py + CLI wrapper
run_tiingo_migrate.py with pgrep guard + automatic backup opt-out +
lockfile on partial failure (§3.5, §4).

Real migration executed: 1660 tickers moved to data/tiingo/daily/;
backup tarball in data/tiingo_premigrate_<ts>.tar.gz.

Baseline 377 → ~388 tests (added nested manifest, slack per-AC,
date|datetime has(), requested_range, lockfile, plus 11 migrate tests).
Call-sites using default frequency="daily" unchanged.

Plan: docs/superpowers/plans/2026-04-15-tiingo-service-lazy-cache.md
Spec: docs/superpowers/specs/2026-04-15-tiingo-service-lazy-cache-design.md
EOF
)"
```

- [ ] **Step 4: Verificar commit limpo**

Run: `git log --oneline -1 && git status`
Expected: novo commit SHA + working tree clean (exceto arquivos não trackeados como report dir).

---

## Phase B — TiingoSource refactor with split adjust (commit #2)

### Task 15: Escrever testes de URL routing por (asset_class, frequency)

**Files:**
- Modify: `tests/test_tiingo_source.py`

- [ ] **Step 1: Adicionar testes de URL routing**

```python
class TestUrlRouting:
    """Smoke tests for endpoint dispatch by (asset_class, frequency)."""

    def test_equity_daily_uses_tiingo_daily_endpoint(self):
        from ai_trade.backtest.data.tiingo_source import _build_url

        url = _build_url("SPY", asset_class="equity", frequency="daily")
        assert url == "https://api.tiingo.com/tiingo/daily/SPY/prices"

    def test_equity_1hour_uses_iex_endpoint(self):
        from ai_trade.backtest.data.tiingo_source import _build_url

        url = _build_url("SPY", asset_class="equity", frequency="1hour")
        assert url == "https://api.tiingo.com/iex/SPY/prices"

    def test_crypto_1hour_uses_tiingo_crypto_endpoint(self):
        from ai_trade.backtest.data.tiingo_source import _build_url

        url = _build_url("BTCUSD", asset_class="crypto", frequency="1hour")
        assert url == "https://api.tiingo.com/tiingo/crypto/prices"

    def test_forex_1hour_uses_tiingo_fx_endpoint(self):
        from ai_trade.backtest.data.tiingo_source import _build_url

        url = _build_url("EURUSD", asset_class="forex", frequency="1hour")
        assert url == "https://api.tiingo.com/tiingo/fx/EURUSD/prices"

    def test_rejects_frequency_not_in_whitelist(self):
        from ai_trade.backtest.data.tiingo_source import _build_url
        import pytest

        with pytest.raises(NotImplementedError, match="frequency='5min'"):
            _build_url("SPY", asset_class="equity", frequency="5min")

    def test_rejects_index_1hour_with_etf_hint(self):
        from ai_trade.backtest.data.tiingo_source import _build_url
        import pytest

        with pytest.raises(NotImplementedError, match="ETF proxy"):
            _build_url("SPX", asset_class="index", frequency="1hour")
```

- [ ] **Step 2: Adicionar teste de params com resampleFreq**

```python
def test_build_params_adds_resample_freq_for_1hour():
    from ai_trade.backtest.data.tiingo_source import _build_params
    from datetime import date

    params = _build_params(
        "SPY",
        date(2024, 1, 1), date(2024, 12, 31),
        asset_class="equity",
        frequency="1hour",
    )
    assert params["resampleFreq"] == "1hour"
    assert params["startDate"] == "2024-01-01"
    assert params["endDate"] == "2024-12-31"


def test_build_params_crypto_1hour_has_tickers_and_resample():
    from ai_trade.backtest.data.tiingo_source import _build_params
    from datetime import date

    params = _build_params(
        "BTCUSD",
        date(2024, 1, 1), date(2024, 12, 31),
        asset_class="crypto",
        frequency="1hour",
    )
    assert params["tickers"] == "BTCUSD"
    assert params["resampleFreq"] == "1hour"
```

- [ ] **Step 3: Rodar testes, verificar falhas**

Run: `.venv/bin/python -m pytest tests/test_tiingo_source.py::TestUrlRouting tests/test_tiingo_source.py::test_build_params_adds_resample_freq_for_1hour tests/test_tiingo_source.py::test_build_params_crypto_1hour_has_tickers_and_resample -xvs`
Expected: FAIL — `_build_url` / `_build_params` ainda não aceitam `frequency`.

### Task 16: Refatorar `_build_url` + `_build_params` + whitelist

**Files:**
- Modify: `src/ai_trade/backtest/data/tiingo_source.py`

- [ ] **Step 1: Adicionar whitelist + função helper no topo**

```python
_WHITELIST_ASSET_FREQ: frozenset[tuple[str, str]] = frozenset({
    ("equity", "daily"),
    ("etf",    "daily"),
    ("index",  "daily"),
    ("crypto", "daily"),
    ("crypto", "1hour"),
    ("forex",  "daily"),
    ("forex",  "1hour"),
    ("equity", "1hour"),
    ("etf",    "1hour"),
})


def _check_whitelist(asset_class: str, frequency: str) -> None:
    if (asset_class, frequency) in _WHITELIST_ASSET_FREQ:
        return
    if asset_class == "index" and frequency == "1hour":
        raise NotImplementedError(
            "Tiingo IEX não cobre índices diretamente. Use um ETF proxy "
            "(SPY, QQQ, DIA, IWM). v1 whitelist: {equity, etf, crypto, forex} "
            "× {daily, 1hour}."
        )
    raise NotImplementedError(
        f"frequency={frequency!r} com asset_class={asset_class!r} fora do v1 "
        f"whitelist. v1 aceita: {{daily, 1hour}} para equity/etf/crypto/forex; "
        f"index só daily. Seguir §6.6 do spec para unblock path."
    )
```

- [ ] **Step 2: Refatorar `_build_url` para aceitar frequency**

```python
def _build_url(ticker: str, asset_class: str, frequency: str = "daily") -> str:
    _check_whitelist(asset_class, frequency)
    api_ticker = _normalize_ticker(ticker, asset_class)
    if asset_class in ("equity", "etf") and frequency == "1hour":
        return f"{_BASE}/iex/{api_ticker}/prices"
    if asset_class in ("equity", "etf", "index") and frequency == "daily":
        return f"{_BASE_DAILY}/{api_ticker}/prices"
    if asset_class == "crypto":
        return f"{_BASE}/tiingo/crypto/prices"
    if asset_class == "forex":
        return f"{_BASE}/tiingo/fx/{api_ticker}/prices"
    raise NotImplementedError(f"unhandled: {asset_class=} {frequency=}")
```

Adicionar `_BASE` e `_BASE_DAILY`:
```python
_BASE = "https://api.tiingo.com"
_BASE_DAILY = f"{_BASE}/tiingo/daily"
```

- [ ] **Step 3: Refatorar `_build_params` para aceitar frequency**

```python
def _build_params(
    ticker: str, start: date, end: date, asset_class: str,
    frequency: str = "daily",
) -> dict:
    params: dict[str, str] = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
    }
    if asset_class == "crypto":
        params["tickers"] = _normalize_ticker(ticker, asset_class)
        params["resampleFreq"] = "1hour" if frequency == "1hour" else "1day"
    elif frequency == "1hour":
        params["resampleFreq"] = "1hour"
    return params
```

- [ ] **Step 4: Rodar testes de routing**

Run: `.venv/bin/python -m pytest tests/test_tiingo_source.py::TestUrlRouting -xvs`
Expected: PASS.

### Task 17: Refatorar `TiingoSource.fetch()` para aceitar frequency

**Files:**
- Modify: `src/ai_trade/backtest/data/tiingo_source.py`
- Modify: `tests/test_tiingo_source.py`

- [ ] **Step 1: Adicionar teste `test_fetch_with_frequency_1hour_persists_and_serves_cache`**

```python
def test_fetch_with_frequency_1hour_persists_and_serves_cache(
    tiingo_env, storage, monkeypatch,
):
    """Primeira call faz HTTP; segunda lê do cache."""
    from datetime import date
    import pandas as pd
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data import tiingo_source as ts_mod

    # Pré-popular daily cache para permitir split adjust (ratio = 1.0 aqui)
    df_daily = pd.DataFrame(
        {"open": [100.0] * 3, "high": [101.0] * 3, "low": [99.0] * 3,
         "close": [100.0] * 3, "adj_close": [100.0] * 3, "volume": [1000.0] * 3},
        index=pd.DatetimeIndex(
            [pd.Timestamp("2024-01-02"),
             pd.Timestamp("2024-01-03"),
             pd.Timestamp("2024-01-04")],
            name="date",
        ),
    )
    storage.write("SPY", df_daily, asset_class="equity", frequency="daily")

    # Mock HTTP para IEX 1h
    IEX_SAMPLE = [
        {"date": "2024-01-02T14:00:00.000Z",
         "open": 100.0, "high": 100.5, "low": 99.5, "close": 100.2,
         "volume": 500},
        {"date": "2024-01-02T15:00:00.000Z",
         "open": 100.2, "high": 100.8, "low": 100.0, "close": 100.5,
         "volume": 600},
    ]

    call_count = {"n": 0}

    def fake_get(url, params=None, headers=None, timeout=None):
        call_count["n"] += 1
        mock = _mock_response(IEX_SAMPLE, 200)
        return mock

    monkeypatch.setattr(ts_mod.requests, "get", fake_get)

    source = TiingoSource(storage=storage)
    df1 = source.fetch(
        "SPY", date(2024, 1, 2), date(2024, 1, 2),
        asset_class="equity", frequency="1hour",
    )
    assert not df1.empty
    assert call_count["n"] == 1

    # Segunda call: cache hit — sem HTTP
    df2 = source.fetch(
        "SPY", date(2024, 1, 2), date(2024, 1, 2),
        asset_class="equity", frequency="1hour",
    )
    assert not df2.empty
    assert call_count["n"] == 1  # não incrementou
```

- [ ] **Step 2: Rodar teste, verificar falha**

Run: `.venv/bin/python -m pytest tests/test_tiingo_source.py::test_fetch_with_frequency_1hour_persists_and_serves_cache -xvs`
Expected: FAIL — `fetch()` não aceita `frequency` kwarg.

- [ ] **Step 3: Refatorar `TiingoSource.fetch()` e `_http_fetch()`**

```python
def fetch(
    self,
    ticker: str,
    start: date,
    end: date,
    asset_class: str = "equity",
    frequency: str = "daily",
) -> pd.DataFrame:
    """Return OHLCV for (ticker, frequency) in [start, end].

    Storage-first: hits the API only when the manifest does not cover
    the requested range for the given (ticker, frequency).
    """
    if self.storage.has(ticker, start, end, frequency=frequency):
        log.debug(
            "storage hit: %s freq=%s [%s..%s]", ticker, frequency, start, end,
        )
        return self.storage.read(
            ticker, start, end, frequency=frequency,
        )

    df = self._http_fetch(ticker, start, end, asset_class, frequency)
    if df.empty:
        return df

    # Split adjust para IEX 1h (equity/etf) se daily cache disponível
    if frequency == "1hour" and asset_class in ("equity", "etf"):
        df = self._apply_split_adjust_from_daily(ticker, df, asset_class)

    self.storage.write(
        ticker, df,
        asset_class=asset_class,
        frequency=frequency,
        requested_start=start,
        requested_end=end,
    )
    return self.storage.read(
        ticker, start, end, frequency=frequency,
    )


def _http_fetch(
    self,
    ticker: str,
    start: date,
    end: date,
    asset_class: str,
    frequency: str = "daily",
) -> pd.DataFrame:
    url = _build_url(ticker, asset_class, frequency)
    params = _build_params(ticker, start, end, asset_class, frequency)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {self._api_key()}",
    }
    log.info(
        "HTTP fetch %s [%s..%s] (%s freq=%s)",
        ticker, start, end, asset_class, frequency,
    )
    resp = requests.get(url, params=params, headers=headers, timeout=self.timeout)
    if resp.status_code == 404:
        log.warning(
            "tiingo 404 for %s (%s freq=%s) — returning empty frame",
            ticker, asset_class, frequency,
        )
        return _normalize([])
    resp.raise_for_status()
    body = resp.json()
    if asset_class == "crypto":
        if not body or not isinstance(body, list):
            return _normalize([])
        return _normalize(body[0].get("priceData", []))
    return _normalize(body)
```

- [ ] **Step 4: Adicionar placeholder `_apply_split_adjust_from_daily` que retorna df unchanged por enquanto**

```python
def _apply_split_adjust_from_daily(
    self, ticker: str, df_intraday: pd.DataFrame, asset_class: str,
) -> pd.DataFrame:
    """Apply split/dividend adjust to IEX intraday using daily cache ratio.

    Raises NotImplementedError if equity/etf and ticker not in daily cache.
    """
    # TEMPORARY stub — será completado em Task 18
    return df_intraday
```

- [ ] **Step 5: Rodar teste (não testa adjust ainda, só cache-hit)**

Run: `.venv/bin/python -m pytest tests/test_tiingo_source.py::test_fetch_with_frequency_1hour_persists_and_serves_cache -xvs`
Expected: PASS.

### Task 18: Implementar split adjust via adjust.py reusando ratio

**Files:**
- Modify: `src/ai_trade/backtest/data/tiingo_source.py`
- Modify: `tests/test_tiingo_source.py`

- [ ] **Step 1: Adicionar teste `test_iex_applies_split_adjust_from_daily_cache`**

```python
def test_iex_applies_split_adjust_from_daily_cache(
    tiingo_env, storage, monkeypatch,
):
    """close_intraday × (adj_close_daily/close_daily) vira adj_close_intraday."""
    from datetime import date
    import pandas as pd
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data import tiingo_source as ts_mod

    # Daily cache: SPY 2024-01-02 close=100, adj_close=50 (hypothetical split 2:1)
    df_daily = pd.DataFrame(
        {"open": [100.0], "high": [100.0], "low": [100.0],
         "close": [100.0], "adj_close": [50.0], "volume": [1000.0]},
        index=pd.DatetimeIndex([pd.Timestamp("2024-01-02")], name="date"),
    )
    storage.write("SPY", df_daily, asset_class="equity", frequency="daily")

    # IEX 1h sample: close=100 no mesmo dia
    IEX_SAMPLE = [
        {"date": "2024-01-02T14:00:00.000Z",
         "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0,
         "volume": 500},
    ]

    def fake_get(url, params=None, headers=None, timeout=None):
        return _mock_response(IEX_SAMPLE, 200)

    monkeypatch.setattr(ts_mod.requests, "get", fake_get)

    source = TiingoSource(storage=storage)
    df = source.fetch(
        "SPY", date(2024, 1, 2), date(2024, 1, 2),
        asset_class="equity", frequency="1hour",
    )

    # Ratio = 50/100 = 0.5; close_intraday = 100 × 0.5 = 50
    assert abs(df["close"].iloc[0] - 50.0) < 1e-6
    # adj_close após adjust_ohlc == close ajustado
    assert abs(df["adj_close"].iloc[0] - 50.0) < 1e-6


def test_iex_raises_notimplemented_if_equity_not_in_daily_cache(
    tiingo_env, storage, monkeypatch,
):
    """equity/etf 1h sem daily cache para o ticker → NotImplementedError."""
    from datetime import date
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data import tiingo_source as ts_mod
    import pytest

    IEX_SAMPLE = [
        {"date": "2024-01-02T14:00:00.000Z",
         "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0,
         "volume": 500},
    ]

    def fake_get(url, params=None, headers=None, timeout=None):
        return _mock_response(IEX_SAMPLE, 200)

    monkeypatch.setattr(ts_mod.requests, "get", fake_get)

    source = TiingoSource(storage=storage)
    with pytest.raises(NotImplementedError, match="daily primeiro"):
        source.fetch(
            "NVDA", date(2024, 1, 2), date(2024, 1, 2),
            asset_class="equity", frequency="1hour",
        )


def test_crypto_and_forex_use_close_as_adj_close_no_split(
    tiingo_env, storage, monkeypatch,
):
    """Crypto/forex 1h não tem split — adj_close := close."""
    from datetime import date
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data import tiingo_source as ts_mod

    CRYPTO_SAMPLE = [{
        "ticker": "btcusd",
        "priceData": [
            {"date": "2024-01-02T00:00:00.000Z",
             "open": 45000.0, "high": 45100.0, "low": 44900.0,
             "close": 45050.0, "volume": 100.0, "volumeNotional": 4500000.0,
             "tradesDone": 1000},
        ],
    }]

    def fake_get(url, params=None, headers=None, timeout=None):
        return _mock_response(CRYPTO_SAMPLE, 200)

    monkeypatch.setattr(ts_mod.requests, "get", fake_get)

    source = TiingoSource(storage=storage)
    df = source.fetch(
        "BTCUSD", date(2024, 1, 2), date(2024, 1, 2),
        asset_class="crypto", frequency="1hour",
    )
    assert abs(df["close"].iloc[0] - 45050.0) < 1e-6
    assert abs(df["adj_close"].iloc[0] - 45050.0) < 1e-6
```

- [ ] **Step 2: Rodar testes, verificar falhas**

Run: `.venv/bin/python -m pytest tests/test_tiingo_source.py -xvs -k "split_adjust or raises_notimplemented or close_as_adj_close"`
Expected: FAIL — lógica de adjust ainda é stub.

- [ ] **Step 3: Implementar `_apply_split_adjust_from_daily` completo**

```python
def _apply_split_adjust_from_daily(
    self, ticker: str, df_intraday: pd.DataFrame, asset_class: str,
) -> pd.DataFrame:
    """Apply daily-derived adjust ratio to intraday bars.

    Derivation per §3.3 of spec: ratio_D = adj_close_daily[D] / close_daily[D].
    Apply ratio_D to all intraday bars whose date.date() == D. Result:
    adj_close_intraday[t] is the total-return-adjusted close at bar t.

    Raises NotImplementedError if asset_class in {equity, etf} and ticker
    is not present in the daily cache — no silent fallback to close.
    """
    if df_intraday.empty:
        return df_intraday

    # Load daily cache entries for the ticker
    try:
        df_daily = self.storage.read(ticker, frequency="daily")
    except KeyError:
        raise NotImplementedError(
            f"Ticker {ticker!r} não está no daily cache. "
            f"Baixe o daily primeiro para obter adj_close, ou pré-autorize "
            f"via flag --skip-adjust se você sabe o que está fazendo. "
            f"Vide spec §3.3."
        )

    # Daily ratio por data
    daily_ratio = (df_daily["adj_close"] / df_daily["close"]).rename("ratio")

    # Align por data calendário (date), não por timestamp exato
    intraday_dates = pd.Index(df_intraday.index.date)
    daily_dates = pd.Index(df_daily.index.date)
    date_to_ratio: dict = {}
    for d, r in zip(daily_dates, daily_ratio.values):
        date_to_ratio[d] = r

    out = df_intraday.copy()
    ratios = pd.Series(
        [date_to_ratio.get(d, 1.0) for d in intraday_dates],
        index=df_intraday.index,
    )
    for col in ("open", "high", "low", "close"):
        if col in out.columns:
            out[col] = (out[col].astype(float) * ratios).astype(float)
    out["adj_close"] = out["close"]  # por construção
    return out
```

- [ ] **Step 4: Rodar testes de split adjust**

Run: `.venv/bin/python -m pytest tests/test_tiingo_source.py -xvs -k "split_adjust or raises_notimplemented or close_as_adj_close"`
Expected: PASS.

### Task 19: Verificar IEX payload normalize sem adjClose

**Files:**
- Modify: `tests/test_tiingo_source.py`

- [ ] **Step 1: Adicionar teste `test_iex_payload_normalizes_without_adjclose`**

```python
def test_iex_payload_normalizes_without_adjclose():
    """IEX payload sem adjClose — _normalize usa close."""
    from ai_trade.backtest.data.tiingo_source import _normalize

    payload = [
        {"date": "2024-01-02T14:00:00.000Z",
         "open": 100.0, "high": 100.5, "low": 99.5, "close": 100.2,
         "volume": 500},
    ]
    df = _normalize(payload)
    assert list(df.columns) == ["open", "high", "low", "close", "adj_close", "volume"]
    assert abs(df["adj_close"].iloc[0] - df["close"].iloc[0]) < 1e-6
```

- [ ] **Step 2: Rodar teste**

Run: `.venv/bin/python -m pytest tests/test_tiingo_source.py::test_iex_payload_normalizes_without_adjclose -xvs`
Expected: PASS (lógica existente de `_normalize` já faz fallback `adj_close := close`).

### Task 20: Baseline verde pós-refactor do source

**Files:** (só execução)

- [ ] **Step 1: Rodar suite completa**

Run: `.venv/bin/python -m pytest -q`
Expected: ~397 verdes (~388 após Task 14 + ~9 de source). Se falhar, investigar.

- [ ] **Step 2: Verificar cobertura de testes do source**

Run: `.venv/bin/python -m pytest tests/test_tiingo_source.py -v | tail -30`
Expected: listagem de 30-40 tests de source todos PASS.

### Task 21: Commit #2

**Files:** (só commit)

- [ ] **Step 1: Git status review**

Run: `git status`

- [ ] **Step 2: Commit #2**

Run:
```
git add src/ai_trade/backtest/data/tiingo_source.py \
        tests/test_tiingo_source.py
git commit -m "$(cat <<'EOF'
feat(data): route tiingo source to IEX for 1h intraday with split adjust

TiingoSource.fetch() now accepts frequency kwarg (default 'daily' preserves
call-site compat). Equity/ETF 1h routes to /iex/{ticker}/prices; crypto/
forex 1h add resampleFreq=1hour. Whitelist blocks {index × 1hour} with
ETF-proxy hint and all non-v1 frequencies with pointer to §6.6 of spec.

IEX payload lacks adjClose, so v1 applies split/dividend adjust in
post-processing by deriving ratio = adj_close_daily / close_daily per
calendar date from the existing daily cache (reusing the pattern from
adjust.py shipped in 5ca9410) and multiplying intraday OHLC by the
date-matched ratio. Equity/ETF 1h without daily cache raises
NotImplementedError — no silent fallback to raw close (spec v3 §3.3,
citations: [quant_trading_chan, p.37], [trading_systems_methods, p.914],
[ml_for_algo_trading, ch.2 p.35-40]).

Crypto/forex have no splits, so adj_close := close is the correct
behavior (ratio = 1.0 by construction).

~9 new source tests; baseline 388 → ~397 green.

Plan: docs/superpowers/plans/2026-04-15-tiingo-service-lazy-cache.md
Spec: docs/superpowers/specs/2026-04-15-tiingo-service-lazy-cache-design.md §3.3
EOF
)"
```

- [ ] **Step 3: Verificar commit limpo**

Run: `git log --oneline -2`

---

## Phase C — Smoke #2 + docs + commit #3

### Task 22: Rodar Smoke #2 end-to-end via código refatorado

**Files:** (execução + verificação)

- [ ] **Step 1: Escrever script scratch que usa TiingoSource ao invés do smoke standalone**

Criar `/tmp/smoke2.py`:
```python
"""Smoke #2 — valida que o TiingoSource refatorado produz mesmo output de Smoke #1."""
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ai_trade.backtest.data.tiingo_source import TiingoSource
from ai_trade.backtest.data.tiingo_storage import TiingoStorage

storage = TiingoStorage(root=Path("data/tiingo"))
source = TiingoSource(storage=storage)

today = date.today()
five_yr = today - timedelta(days=5 * 365)
four_yr = today - timedelta(days=4 * 365)

cases = [
    ("SPY",    "equity", four_yr),
    ("BTCUSD", "crypto", today - timedelta(days=60)),  # respect retention
    ("EURUSD", "forex",  today - timedelta(days=200)),
]
for ticker, asset_class, start in cases:
    print(f"--- {ticker} ({asset_class}) from {start} to {today}")
    df = source.fetch(
        ticker, start, today,
        asset_class=asset_class, frequency="1hour",
    )
    print(f"  shape={df.shape}, first={df.index.min()}, last={df.index.max()}")
    print(f"  columns={list(df.columns)}")
    if not df.empty and "adj_close" in df.columns and "close" in df.columns:
        ratio = (df["adj_close"] / df["close"]).round(6)
        print(f"  adj_close/close: min={ratio.min()} max={ratio.max()}")
```

Run: `.venv/bin/python /tmp/smoke2.py`

- [ ] **Step 2: Verificar shapes plausíveis (e.g. SPY ~hours em 4 anos)**

Expected: SPY shape ~(6500, 6) aproximadamente (6.5h RTH × 252 dias × 4 anos). Crypto/forex shapes menores por retention. Sem erros.

- [ ] **Step 3: Verificar persistência em data/tiingo/1hour/**

Run: `ls data/tiingo/1hour/prices/ 2>/dev/null | wc -l`
Expected: 3 (SPY, BTCUSD, EURUSD). Se 0, Smoke #2 não persistiu — investigar.

- [ ] **Step 4: Verificar adj_close != close para SPY (se houve split na janela)**

Run: `.venv/bin/python -c "import pandas as pd; df=pd.read_parquet('data/tiingo/1hour/prices/SPY.parquet'); print('ratio stats:', (df['adj_close']/df['close']).describe())"`
Expected: se houve split no período 2022-2026, ratio varies (e.g., min < 1.0). Se não houve, ratio ≈ 1.0 sempre. Qualquer resultado é aceitável — o importante é que o adjust foi aplicado e preservou consistency.

- [ ] **Step 5: Log Smoke #2 em logs/tiingo.log**

Run:
```bash
echo "[$(date '+%H:%M:%S')] smoke-2 e2e via refactored TiingoSource — 3 tickers persisted in data/tiingo/1hour/" >> logs/tiingo.log
```

### Task 23: Atualizar JORNADA.md com entrada do pivô executado

**Files:**
- Modify: `JORNADA.md`

- [ ] **Step 1: Ler últimas entradas do changelog**

Run: `head -240 JORNADA.md | tail -60`

- [ ] **Step 2: Adicionar nova entrada datada no topo do changelog (após o header `# Changelog`)**

Inserir antes da entrada `## 2026-04-15 (noite, final) — Pivô: intraday short-hold + \`tiingo_service\` lazy-cache`:

```markdown
## 2026-04-15 (noite, pós-pivô) — `tiingo_service` lazy-cache entregue ✅

**Gatilho:** item 1 do backlog pós-pivô de horas antes. Ver spec v3.1 em
`docs/superpowers/specs/2026-04-15-tiingo-service-lazy-cache-design.md`
(2 rodadas `/judge-spec` adversarial + Smoke #1 empírico antes de
commitar implementação).

**O que foi entregue:**

- **Storage refactor** — `TiingoStorage` agora nested por frequency; slack
  per-`(asset_class, freq)` (crypto 24/7 não compartilha slack com equity
  RTH); `has()` aceita `date|datetime`; manifest grava `requested_range`
  em v1; lockfile protege contra migração parcial concorrente.
- **Migração executada** — 1660 tickers daily movidos para
  `data/tiingo/daily/prices/` com backup automático em
  `data/tiingo_premigrate_<ts>.tar.gz`. pgrep guard contra bulk ativo.
- **Source refactor** — `TiingoSource.fetch()` aceita `frequency`;
  rotea equity/etf 1h para `/iex/`; crypto/forex 1h usam `resampleFreq=1hour`;
  aplica split/dividend adjust em IEX via ratio derivado do daily cache
  (reusa `adjust.py`); `NotImplementedError` explícito se equity sem
  daily cache ou frequency fora do whitelist v1 (`{daily, 1hour}`).
- **Smoke #1 empírico (gate de design)** — SPY 5a ✅ · btcusd 208d ✅ ·
  eurusd 416d ✅. Threshold ≥ 6m PASS para os 3 tickers.
  Log em `logs/tiingo.log` 17:47.
- **Smoke #2 e2e** — 3 tickers via código refatorado, persistem em
  `data/tiingo/1hour/prices/`, cache hit na segunda chamada.

**Baseline:** 377 → ~397 testes verdes. Não quebrado.

**O que destrava:** catálogo de estratégias intraday do ROADMAP §"Next
steps" item 2 — Chan mean-reversion pairs, Ehlers BP 1h, volatility
breakouts. Cada uma terá spec próprio seguindo mesmo padrão F3.D.

**Caveat residual:** cancelamento da subscrição Tiingo passa a ser safe
APENAS para daily. Intraday requer API viva por causa da janela rolling
de retention (crypto ~208 dias; SPY paid-tier superou docs públicos em
~22× mas ainda rolling). Ver spec §6.5 item 4.

**Arquivos gerados:**
- `reports/spec-judges/2026-04-15-tiingo-service-lazy-cache-design-*/`
  (4 juízes × 2 rodadas = 8 relatórios + 2 árbitros).
- `docs/superpowers/plans/2026-04-15-tiingo-service-lazy-cache.md`
  (plan executado).
- Commits: storage+migrate (#1), source+adjust (#2), smoke+docs (#3).

---
```

- [ ] **Step 3: Atualizar a seção "Onde estamos hoje" no topo**

Substituir a linha:
```
- **Pivô arquitetural (decidido 2026-04-15 noite)** ⚠️ Todos os ciclos
```

Por:
```
- **Pivô arquitetural (decidido + `tiingo_service` entregue 2026-04-15 noite)** ✅ `tiingo_service` lazy-cache com eixo frequency destravado via refactor in-place de `TiingoSource`/`TiingoStorage` (377 → ~397 testes verdes); Smoke #1 retention PASS, Smoke #2 e2e PASS. Intraday 1h viável para equity/crypto/forex. Próximo: catálogo Chan/Ehlers/vol-breakouts.
```

- [ ] **Step 4: Atualizar "O que vem a seguir" item 1**

Substituir o item 1 (`tiingo_service` lazy-cache) por:
```
1. **Chan mean-reversion / cointegration pairs em 1h** `[algo_trading_chan]` ← **próximo passo**. O `tiingo_service` entregue hoje destrava o dado; agora validamos a primeira estratégia intraday. Brainstorm → spec → plan → /judge-spec → impl.
```

Renumerar itens seguintes.

### Task 24: Atualizar ROADMAP.md §Current status

**Files:**
- Modify: `ROADMAP.md`

- [ ] **Step 1: Ler a seção Current status**

Run: `head -45 ROADMAP.md | tail -10`

- [ ] **Step 2: Adicionar entrada ✅ após a última entrada 🔄**

Inserir antes de `- ⚠️ **2026-04-15 (noite) — PIVOT: intraday short-hold**`:

```markdown
- ✅ **2026-04-15 (noite, pós-pivô) — `tiingo_service` lazy-cache ENTREGUE.** Refactor in place de `TiingoSource`/`TiingoStorage` com eixo `frequency`; migração de 1660 tickers daily para `data/tiingo/daily/` (backup preservado); roteamento IEX 1h + split adjust via `adjust.py` reusado; whitelist `{daily, 1hour}` × `{equity, etf, crypto, forex}`. Smoke #1 retention PASS (SPY 5a, btcusd 208d, eurusd 416d; threshold 6m). 377 → ~397 testes verdes. Spec v3.1 em `docs/superpowers/specs/2026-04-15-tiingo-service-lazy-cache-design.md` (2 rodadas `/judge-spec` + 1 smoke antes do impl). Plan em `docs/superpowers/plans/2026-04-15-tiingo-service-lazy-cache.md`. Commits storage+migrate · source+adjust · smoke+docs.
```

- [ ] **Step 3: Atualizar §"Next steps (in order, post-pivot)" item 1**

Substituir o item 1 completo (`tiingo_service` lazy-cache) por:

```markdown
    1. ✅ **`tiingo_service` lazy-cache** — ENTREGUE em 2026-04-15 (noite). Ver entrada acima.
```

Renumerar itens subsequentes (Intraday strategy → item 1; AFML → item 2; etc.).

### Task 25: Commit #3

**Files:** (só commit)

- [ ] **Step 1: Git status**

Run: `git status`
Expected: `JORNADA.md`, `ROADMAP.md`, `scripts/tiingo_smoke_intraday.py`, `docs/superpowers/specs/...`, `docs/superpowers/plans/...`, `logs/tiingo.log` (possivelmente), `reports/spec-judges/...`.

- [ ] **Step 2: Commit #3**

Run:
```
git add scripts/tiingo_smoke_intraday.py \
        docs/superpowers/specs/2026-04-15-tiingo-service-lazy-cache-design.md \
        docs/superpowers/plans/2026-04-15-tiingo-service-lazy-cache.md \
        .claude/commands/judge-spec.md \
        .claude/agents/spec-judge-*.md \
        reports/spec-judges/ \
        JORNADA.md \
        ROADMAP.md
git commit -m "$(cat <<'EOF'
feat(data): smoke intraday probe + unblock path docs

Ships scripts/tiingo_smoke_intraday.py as the design-gate retention probe
described in spec §6.1 step 1 (log empirical retention per asset class in
logs/tiingo.log). First run 2026-04-15 17:47 returned PASS: SPY 1825d
(5y), btcusd 208d (~5000 bars rolling), eurusd 416d — all above the 6m
threshold recalibrated from Chan buy-on-gap + Ehlers 1h use cases.

Also includes the adversarial /judge-spec infrastructure used to validate
the design before implementation: a slash command orchestrator + 3 judge
subagents (engineering, domain, strategic) + 1 arbiter. Two rounds ran
against this spec (v1 BLOCK → v2 PROCEED-WITH-CHANGES → v3 with 5 fixes
→ empirical smoke PASS → v3.1 + plan + execution).

JORNADA.md + ROADMAP.md updated with delivered status.

Spec: docs/superpowers/specs/2026-04-15-tiingo-service-lazy-cache-design.md
Plan: docs/superpowers/plans/2026-04-15-tiingo-service-lazy-cache.md
Judge reports: reports/spec-judges/2026-04-15-tiingo-service-lazy-cache-design-*/
EOF
)"
```

- [ ] **Step 3: Verificar log linear dos 3 commits**

Run: `git log --oneline -3`
Expected: 3 novos commits na ordem (smoke+docs mais recente).

---

## Post-execution self-checks

### Task 26: Verificação final end-to-end

**Files:** (só verificação)

- [ ] **Step 1: Todos testes verdes**

Run: `.venv/bin/python -m pytest -q`
Expected: ~397/397 PASS, 0 FAIL.

- [ ] **Step 2: Lint/type-check se configurado**

Run: `test -f mypy.ini && .venv/bin/python -m mypy src/ai_trade/backtest/data/ || echo "no mypy config, skip"`

- [ ] **Step 3: Diff total das mudanças**

Run: `git log --stat origin/main..HEAD`
Expected: 3 commits, ~7-10 arquivos tocados, ~800-1200 linhas adicionadas.

- [ ] **Step 4: Re-rodar Smoke #2 via os refactored modules (sanity)**

Run: `.venv/bin/python /tmp/smoke2.py | tail -20`
Expected: mesmo output do Task 22 — idempotência do cache confirma persistência.

---

## Handoff

**Plan complete.** Total de 26 tasks agrupadas em 3 commits.

Se PROCEED no handoff:
- Fase A (Tasks 1-14) produz commit #1 (storage + migrate).
- Fase B (Tasks 15-21) produz commit #2 (source + adjust).
- Fase C (Tasks 22-25) produz commit #3 (smoke + docs).
- Task 26 é verificação final pós-execução.

Após execução completa, próximo ciclo: **Chan mean-reversion pairs em 1h**
(novo spec seguindo padrão F3.D/tiingo_service).
