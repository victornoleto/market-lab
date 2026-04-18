#!/usr/bin/env python3
"""Extract testfol.io chart JSONs into unified compact parquet cache.

Walks ``data/testfolio/*.json`` (excluding files under ``cache/``),
keeps only timestamps + equity curves, translates testfol.io ticker
labels to clean canonical names, and merges all sources on a shared
DatetimeIndex.

Ticker label translation — testfol.io's ``?L=N`` suffix is awkward
as a column name; we map known synthetic tickers to the real LETF
ticker they proxy:

* ``SPYSIM?L=2`` → **SSOSIM** (ProShares Ultra S&P 500, 2×)
* ``QQQSIM?L=2`` → **QLDSIM** (ProShares Ultra QQQ, 2×)
* ``GLDSIM?L=2`` → **UGLSIM** (ProShares Ultra Gold, 2×)
* ``SPYSIM?L=3`` → **UPROSIM** (if ever needed)
* ``QQQSIM?L=3`` → **TQQQSIM** (if ever needed)

Any ``?L=N`` label not in the map passes through unchanged.

Emits:

* ``data/testfolio/cache/history.parquet`` — DatetimeIndex × all tickers.
* ``data/testfolio/cache/history.meta.json`` — per-source provenance.

Idempotent: re-run after dropping new JSONs to refresh cache.

Usage
-----
::

    .venv/bin/python scripts/extract_testfolio_json.py

Citations
---------
* testfol.io as simulation source: Phase 3.5b Task 7a
  (``reports/phase3_5b/robustness/testfolio_vs_synthetic_letf.md``).
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

log = logging.getLogger("extract_testfolio")

LABEL_RENAME = {
    "SPYSIM?L=2": "SSOSIM",
    "QQQSIM?L=2": "QLDSIM",
    "GLDSIM?L=2": "UGLSIM",
    "SPYSIM?L=3": "UPROSIM",
    "QQQSIM?L=3": "TQQQSIM",
}


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--input-dir", type=Path, default=Path("data/testfolio"),
        help="Directory containing *.json files (non-recursive).",
    )
    ap.add_argument(
        "--output-dir", type=Path, default=Path("data/testfolio/cache"),
    )
    ap.add_argument("--log-level", default="INFO")
    return ap.parse_args(argv)


def _extract_one(path: Path) -> tuple[pd.DataFrame, dict]:
    with path.open() as fh:
        raw = json.load(fh)
    hist = raw["charts"]["history"]
    if len(hist) < 2:
        raise ValueError(f"{path.name}: history has < 2 elements")
    ts = hist[0]
    series = hist[1:]
    labels_raw = raw.get("allocation_labels", [])
    if len(labels_raw) != len(series):
        raise ValueError(
            f"{path.name}: allocation_labels count ({len(labels_raw)}) "
            f"!= series count ({len(series)})"
        )
    labels = [
        lbl[0] if isinstance(lbl, list) and lbl else str(lbl)
        for lbl in labels_raw
    ]
    renamed = [LABEL_RENAME.get(lbl, lbl) for lbl in labels]
    for s in series:
        if len(s) != len(ts):
            raise ValueError(f"{path.name}: series/ts length mismatch")

    index = pd.DatetimeIndex(
        pd.to_datetime(ts, unit="s", utc=True).tz_convert(None)
    )
    df = pd.DataFrame(
        {col: pd.Series(s, index=index, dtype=float)
         for col, s in zip(renamed, series)}
    )
    df.index.name = "date"
    source_meta = {
        "source_file": str(path),
        "source_size_bytes": int(path.stat().st_size),
        "labels_raw": labels,
        "labels_renamed": renamed,
        "bars": int(len(df)),
        "first_date": df.index[0].strftime("%Y-%m-%d"),
        "last_date": df.index[-1].strftime("%Y-%m-%d"),
        "last_value_per_label": {c: float(df[c].iloc[-1]) for c in renamed},
    }
    return df, source_meta


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    json_files = sorted(args.input_dir.glob("*.json"))
    if not json_files:
        log.error("no *.json under %s", args.input_dir)
        return 1
    log.info("found %d JSON files", len(json_files))

    frames: list[pd.DataFrame] = []
    sources: list[dict] = []
    for path in json_files:
        log.info("  extracting %s (%.1f KB)", path.name,
                 path.stat().st_size / 1024)
        df, meta = _extract_one(path)
        frames.append(df)
        sources.append(meta)

    # Outer merge on date index; conflicting labels (same column in
    # two JSONs) → first occurrence wins, second is reported.
    merged = frames[0]
    conflicts: list[str] = []
    for i, df in enumerate(frames[1:], start=1):
        overlap = set(merged.columns) & set(df.columns)
        if overlap:
            conflicts.extend(sorted(overlap))
            df = df.drop(columns=list(overlap))
        merged = merged.join(df, how="outer")
    if conflicts:
        log.warning("column conflicts (first-wins): %s",
                    ", ".join(sorted(set(conflicts))))

    # Sort columns deterministically for reproducibility.
    merged = merged[sorted(merged.columns)]
    merged = merged.sort_index()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = args.output_dir / "history.parquet"
    merged.to_parquet(parquet_path, compression="snappy")

    meta = {
        "extracted_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "conflicts_resolved_first_wins": sorted(set(conflicts)),
        "label_rename_map": LABEL_RENAME,
        "merged_columns": sorted(merged.columns),
        "merged_bars": int(len(merged)),
        "merged_first_date": merged.index[0].strftime("%Y-%m-%d"),
        "merged_last_date": merged.index[-1].strftime("%Y-%m-%d"),
    }
    meta_path = args.output_dir / "history.meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    out_size = parquet_path.stat().st_size
    total_src = sum(s["source_size_bytes"] for s in sources)
    ratio = (out_size / total_src) * 100.0 if total_src else 0.0

    log.info("merged: %d bars × %d cols  %s → %s",
             meta["merged_bars"], len(meta["merged_columns"]),
             meta["merged_first_date"], meta["merged_last_date"])
    for col in meta["merged_columns"]:
        s = merged[col].dropna()
        v0, vT = float(s.iloc[0]), float(s.iloc[-1])
        years = (s.index[-1] - s.index[0]).days / 365.25
        cagr = (vT / v0) ** (1.0 / years) - 1.0 if years > 0 else 0.0
        log.info("  %-10s  %.2f → %.2f  CAGR %.2f%% / %.1fy  (%d bars)",
                 col, v0, vT, cagr * 100.0, years, len(s))
    log.info("parquet: %s  (%.1f KB, %.1f%% of %d sources)",
             parquet_path, out_size / 1024, ratio, len(json_files))
    log.info("meta:    %s", meta_path)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
