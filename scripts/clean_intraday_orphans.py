#!/usr/bin/env python3
"""Clean orphan intraday bars from existing Tiingo cache.

Tiingo IEX returns 6 placeholder bars on US market-closed days (US
holidays) with volume=0 and OHLC all identical at the RAW (unadjusted)
price. For tickers with historical splits these bars sit at 2x+ the
surrounding adjusted bars and inflate backtest PnL by 50-90% on
strategies that hold over holidays.

This script removes those bars from the existing intraday parquets and
updates `manifest.json` accordingly. Detected via Task 1D regime decomp;
fix landed via the new `_filter_orphan_intraday_bars` guard in
`tiingo_source.py` (so future fetches won't re-introduce the bug).

Usage:
    .venv/bin/python scripts/clean_intraday_orphans.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd


def find_orphan_dates(intra: pd.DataFrame, daily: pd.DataFrame) -> set:
    intra_dates = {ts.date() for ts in intra.index}
    daily_dates = {ts.date() for ts in daily.index}
    return intra_dates - daily_dates


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Drop orphan intraday bars from cache")
    ap.add_argument("--root", type=Path, default=Path("data/tiingo"))
    ap.add_argument(
        "--dry-run", action="store_true",
        help="Report orphans without modifying files",
    )
    ap.add_argument(
        "--no-backup", action="store_true",
        help="Skip per-file .bak copies (caller already has external backup)",
    )
    args = ap.parse_args(argv)

    intra_dir = args.root / "1hour" / "prices"
    daily_dir = args.root / "daily" / "prices"
    manifest_path = args.root / "manifest.json"

    if not intra_dir.exists():
        print(f"No intraday dir at {intra_dir}", file=sys.stderr)
        return 1
    if not manifest_path.exists():
        print(f"No manifest at {manifest_path}", file=sys.stderr)
        return 1

    manifest = json.loads(manifest_path.read_text())
    parquets = sorted(intra_dir.glob("*.parquet"))
    print(f"Found {len(parquets)} intraday parquets under {intra_dir}")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    summary: list[dict] = []

    for path in parquets:
        ticker = path.stem
        intra = pd.read_parquet(path)
        daily_path = daily_dir / f"{ticker}.parquet"
        if not daily_path.exists():
            print(f"  {ticker}: SKIP (no daily counterpart at {daily_path})")
            summary.append({"ticker": ticker, "skipped": "no_daily"})
            continue
        daily = pd.read_parquet(daily_path)

        orphan_dates = find_orphan_dates(intra, daily)
        n_orphan_dates = len(orphan_dates)
        if n_orphan_dates == 0:
            print(f"  {ticker}: clean (no orphans)")
            summary.append({"ticker": ticker, "n_orphan_dates": 0, "n_orphan_bars": 0})
            continue

        bar_dates = pd.Series(
            [ts.date() for ts in intra.index], index=intra.index,
        )
        orphan_mask = bar_dates.isin(orphan_dates)
        n_orphan_bars = int(orphan_mask.sum())
        n_kept = int((~orphan_mask).sum())

        sample = sorted(d.isoformat() for d in orphan_dates)[:3]
        print(
            f"  {ticker}: {n_orphan_bars} bars on {n_orphan_dates} orphan day(s) "
            f"(sample: {sample}); keep {n_kept} of {len(intra)}"
        )

        if args.dry_run:
            summary.append({
                "ticker": ticker,
                "n_orphan_dates": n_orphan_dates,
                "n_orphan_bars": n_orphan_bars,
                "n_kept": n_kept,
                "would_save": False,
            })
            continue

        if not args.no_backup:
            bak_path = path.with_suffix(f".parquet.bak_orphan_clean_{timestamp}")
            shutil.copy2(path, bak_path)

        cleaned = intra.loc[~orphan_mask].copy()
        cleaned.to_parquet(path)

        # Manifest update.
        if ticker in manifest and "1hour" in manifest[ticker]:
            entry = manifest[ticker]["1hour"]
            entry["n_bars"] = int(len(cleaned))
            entry["first_dt"] = pd.Timestamp(cleaned.index.min()).isoformat()
            entry["last_dt"] = pd.Timestamp(cleaned.index.max()).isoformat()
            entry["fetched_at"] = datetime.now().isoformat(timespec="seconds")

        summary.append({
            "ticker": ticker,
            "n_orphan_dates": n_orphan_dates,
            "n_orphan_bars": n_orphan_bars,
            "n_kept": n_kept,
            "saved": True,
            "backup": (str(bak_path) if not args.no_backup else None),
        })

    if not args.dry_run:
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True))
        print(f"\n✓ Updated manifest at {manifest_path}")

    total_dropped = sum(s.get("n_orphan_bars", 0) for s in summary)
    affected = sum(1 for s in summary if s.get("n_orphan_bars", 0) > 0)
    print(f"\nTotal: {affected} ticker(s) affected, {total_dropped} bar(s) {'would be' if args.dry_run else ''} dropped.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
