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
