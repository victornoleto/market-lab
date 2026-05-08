"""Migração one-shot do layout single-freq para nested-freq no TiingoStorage.

Mudanças:
- Old: root/{prices,meta}/{ticker}.parquet + flat manifest.
- New: root/{freq}/{prices,meta}/{ticker}.parquet + nested manifest.

Guards v1:
- pgrep -f tiingo_bulk_download (bloqueia se ativo, a menos que
  force_ignore_running=True).
- Backup automático via tar direto (opt-out via skip_backup=True).
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


def _run_backup(root: Path) -> str:
    """Create a tarball of `root` at `root.parent/{name}_premigrate_<ts>.tar.gz`."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_name = f"{root.name}_premigrate_{ts}.tar.gz"
    backup_path = root.parent / backup_name
    with tarfile.open(backup_path, "w:gz") as tar:
        tar.add(root, arcname=root.name)
    return str(backup_path)


def _persist_manifest(path: Path, content: dict) -> None:
    """Write manifest atomically (separate function for test monkeypatching)."""
    path.write_text(
        json.dumps(content, indent=2, sort_keys=True),
        encoding="utf-8",
    )


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
    new_manifest: dict[str, dict] = {}
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
