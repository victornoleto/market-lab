#!/usr/bin/env python3
"""Extract testfol.io comparison JSON into compact parquet cache.

The raw JSON dumped by testfol.io (chart export) contains ~40 sections
with seasonality / rolling / sliding-window stats — bloat irrelevant to
our backtest. This script keeps only:

* Unix timestamps from ``charts.history[0]``.
* Equity curves (starting at $10,000) from ``charts.history[1..N]``.
* Ticker names from ``allocation_labels``.

Emits:

* ``data/testfolio/cache/history.parquet`` — DatetimeIndex × N tickers.
* ``data/testfolio/cache/history.meta.json`` — source file, extraction
  date, asset labels, date range, bar count.

Usage
-----
::

    .venv/bin/python scripts/extract_testfolio_json.py \\
        --input data/testfolio/spysim-qqqsim-gldsim-zrozsim.json

Idempotent — re-running overwrites the cache. Source JSON preserved.

Citations
---------
* testfol.io as simulation source for long-history ETF proxies: Phase
  3.5b Task 7a ``reports/phase3_5b/robustness/testfolio_vs_synthetic_letf.md``.
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

log = logging.getLogger("extract_testfolio")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--input", type=Path,
        default=Path("data/testfolio/spysim-qqqsim-gldsim-zrozsim.json"),
    )
    ap.add_argument(
        "--output-dir", type=Path,
        default=Path("data/testfolio/cache"),
    )
    ap.add_argument("--log-level", default="INFO")
    return ap.parse_args(argv)


def extract(input_path: Path, output_dir: Path) -> tuple[pd.DataFrame, dict]:
    with input_path.open() as fh:
        raw = json.load(fh)

    hist = raw["charts"]["history"]
    if len(hist) < 2:
        raise ValueError(
            f"history has {len(hist)} elements; need [0]=timestamps "
            "plus at least one series"
        )
    ts = hist[0]
    series = hist[1:]
    labels_raw = raw.get("allocation_labels", [])
    if len(labels_raw) != len(series):
        raise ValueError(
            f"allocation_labels count ({len(labels_raw)}) != series count "
            f"({len(series)}) — manual mapping needed"
        )
    # testfol.io wraps each label as a single-item list: [['QQQSIM'], ...]
    labels = [
        lbl[0] if isinstance(lbl, list) and lbl else str(lbl)
        for lbl in labels_raw
    ]
    for s in series:
        if len(s) != len(ts):
            raise ValueError(
                f"series length {len(s)} != timestamps length {len(ts)}"
            )

    index = pd.DatetimeIndex(
        pd.to_datetime(ts, unit="s", utc=True).tz_convert(None)
    )
    df = pd.DataFrame(
        {label: pd.Series(s, index=index, dtype=float)
         for label, s in zip(labels, series)}
    )
    df.index.name = "date"

    output_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = output_dir / "history.parquet"
    df.to_parquet(parquet_path, compression="snappy")

    meta = {
        "source_file": str(input_path),
        "extracted_at_utc": datetime.now(timezone.utc).isoformat(),
        "labels": labels,
        "bars": int(len(df)),
        "first_date": df.index[0].strftime("%Y-%m-%d"),
        "last_date": df.index[-1].strftime("%Y-%m-%d"),
        "first_value_per_label": {
            lbl: float(df[lbl].iloc[0]) for lbl in labels
        },
        "last_value_per_label": {
            lbl: float(df[lbl].iloc[-1]) for lbl in labels
        },
    }
    meta_path = output_dir / "history.meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return df, meta


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    src_size = args.input.stat().st_size if args.input.exists() else 0
    log.info("input: %s  (%s)", args.input,
             f"{src_size / 1024:,.1f} KB" if src_size else "missing")
    df, meta = extract(args.input, args.output_dir)
    out_size = (args.output_dir / "history.parquet").stat().st_size
    log.info("labels: %s", meta["labels"])
    log.info("bars: %d  %s → %s",
             meta["bars"], meta["first_date"], meta["last_date"])
    for lbl in meta["labels"]:
        v0 = meta["first_value_per_label"][lbl]
        vT = meta["last_value_per_label"][lbl]
        years = (pd.Timestamp(meta["last_date"])
                 - pd.Timestamp(meta["first_date"])).days / 365.25
        cagr = (vT / v0) ** (1.0 / years) - 1.0 if years > 0 else 0.0
        log.info("  %-10s  %.2f → %.2f  (CAGR %.2f%%)",
                 lbl, v0, vT, cagr * 100.0)
    ratio = (out_size / src_size) * 100.0 if src_size else 0.0
    log.info("parquet: %s  (%.1f KB, %.1f%% of source)",
             args.output_dir / "history.parquet", out_size / 1024, ratio)
    log.info("meta:    %s", args.output_dir / "history.meta.json")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
