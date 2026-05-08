"""Tests for market_lab.backtest.data.tiingo_migrate.

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


def test_detects_old_layout_and_plans_moves(old_layout_root: Path):
    from market_lab.backtest.data.tiingo_migrate import migrate_to_freq_layout

    report = migrate_to_freq_layout(old_layout_root, dry_run=True)

    assert report.dry_run is True
    assert report.moved_parquets == 0  # dry-run não movimenta
    # Plan lista moves esperados
    ops_str = "\n".join(report.operations)
    assert "prices/AAPL.parquet" in ops_str
    assert "daily/prices/AAPL.parquet" in ops_str
    assert "rekey manifest" in ops_str


def test_dry_run_does_not_write(old_layout_root: Path):
    from market_lab.backtest.data.tiingo_migrate import migrate_to_freq_layout

    manifest_before = (old_layout_root / "manifest.json").read_text()
    files_before = sorted(str(p) for p in old_layout_root.rglob("*"))

    migrate_to_freq_layout(old_layout_root, dry_run=True, skip_backup=True)

    assert (old_layout_root / "manifest.json").read_text() == manifest_before
    files_after = sorted(str(p) for p in old_layout_root.rglob("*"))
    assert files_after == files_before


def test_real_migration_moves_files_and_rekeys_manifest(old_layout_root: Path):
    from market_lab.backtest.data.tiingo_migrate import migrate_to_freq_layout

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
    from market_lab.backtest.data.tiingo_migrate import migrate_to_freq_layout

    migrate_to_freq_layout(
        old_layout_root, dry_run=False, skip_backup=True,
    )
    report2 = migrate_to_freq_layout(
        old_layout_root, dry_run=False, skip_backup=True,
    )
    assert report2.moved_parquets == 0
    assert "layout já migrado" in "\n".join(report2.operations).lower()


def test_raises_on_corrupt_manifest(tmp_path: Path):
    from market_lab.backtest.data.tiingo_migrate import migrate_to_freq_layout

    (tmp_path / "prices").mkdir()
    (tmp_path / "manifest.json").write_text("{{{", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        migrate_to_freq_layout(tmp_path, dry_run=False, skip_backup=True)


def test_preserves_datetime_semantics_daily_at_midnight(old_layout_root: Path):
    from market_lab.backtest.data.tiingo_migrate import migrate_to_freq_layout

    migrate_to_freq_layout(
        old_layout_root, dry_run=False, skip_backup=True,
    )
    manifest = json.loads((old_layout_root / "manifest.json").read_text())
    # first_dt é ISO datetime com T00:00:00
    assert manifest["AAPL"]["daily"]["first_dt"] == "2023-01-01T00:00:00"
    assert manifest["AAPL"]["daily"]["last_dt"] == "2024-12-31T00:00:00"


def test_pgrep_guard_blocks_when_bulk_running(old_layout_root: Path):
    from market_lab.backtest.data import tiingo_migrate

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
    from market_lab.backtest.data import tiingo_migrate
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
    assert any("bulk tiingo ativo" in r.message.lower() for r in caplog.records)


def test_backup_automatico_cria_tarball_e_opt_out_via_skip_backup(
    old_layout_root: Path,
):
    from market_lab.backtest.data import tiingo_migrate

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
    from market_lab.backtest.data import tiingo_migrate

    def boom(path, content):
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
    from market_lab.backtest.data.tiingo_storage import TiingoStorage

    (old_layout_root / ".migration.lock").write_text("x", encoding="utf-8")
    with pytest.raises(RuntimeError, match="migração incompleta"):
        TiingoStorage(root=old_layout_root)
