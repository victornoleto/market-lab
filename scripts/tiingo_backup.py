#!/usr/bin/env python3
"""Backup the local Tiingo dataset — survives subscription cancellation.

Bundles ``data/tiingo/prices/``, ``data/tiingo/meta/`` and the manifest
into a single ``.tar.gz`` under ``data/`` (or ``--out-dir``). After
running this once a month with the subscription active, the resulting
archive is your portable, restorable cache.

Restore::

    cd /path/to/market-lab
    tar -xzf data/tiingo_backup_<date>.tar.gz

Usage::

    .venv/bin/python scripts/tiingo_backup.py
    .venv/bin/python scripts/tiingo_backup.py --out-dir /mnt/external
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import tarfile
from datetime import datetime
from pathlib import Path

log = logging.getLogger("market_lab.tiingo_backup")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Backup data/tiingo/ to .tar.gz.")
    ap.add_argument(
        "--storage-root", type=Path, default=Path("data/tiingo"),
    )
    ap.add_argument(
        "--out-dir", type=Path, default=Path("data"),
        help="Where to write the archive (default: data/).",
    )
    ap.add_argument("--log-level", default="INFO")
    return ap.parse_args(argv)


def _human_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024.0  # type: ignore[assignment]
    return f"{n:.1f} TB"


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )

    if not args.storage_root.exists():
        log.error("storage root does not exist: %s", args.storage_root)
        return 1

    manifest_path = args.storage_root / "manifest.json"
    if not manifest_path.exists():
        log.error("manifest missing at %s", manifest_path)
        return 1

    manifest = json.loads(manifest_path.read_text())
    log.info("Manifest: %d tickers", len(manifest))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    archive = args.out_dir / f"tiingo_backup_{stamp}.tar.gz"

    log.info("Bundling → %s", archive)
    with tarfile.open(archive, "w:gz") as tf:
        # Add the storage root preserving relative paths under "tiingo/".
        # We store as `tiingo/...` so an extract from the project root
        # restores to `data/tiingo/...` when run with `cd data && tar -xzf`,
        # or to `tiingo/...` when run from elsewhere — the README example
        # shows `cd market-lab && tar -xzf data/tiingo_backup_*.tar.gz`,
        # which would extract to `data/tiingo/`. Match that:
        tf.add(args.storage_root, arcname="data/tiingo")

    size = archive.stat().st_size
    log.info("Backup written: %s (%s)", archive, _human_bytes(size))
    log.info(
        "Restore: tar -xzf %s   (from project root)", archive.name,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
