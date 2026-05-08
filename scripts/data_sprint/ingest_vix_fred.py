"""Ingest ^VIX spot daily close from FRED (series VIXCLS).

Output: data/phase3_7/vix/VIXCLS.parquet with columns [close] indexed by
UTC midnight DatetimeIndex. Single canonical column only — FRED does not
publish OHLV for this series, only the daily close at US market close.

Feed rationale (Phase 3.7-2 audit doc §3):
  * FRED is free, no auth, no rate limit on CSV downloads.
  * Tiingo does NOT serve ^VIX (404 — 2026-04-23 probe); Yahoo works but
    less stable across long windows.
  * Božović 2024 IRFA (H2 VIX-gated LETF) needs VIX prior-month cumulative;
    the close series is sufficient.

Citation: Božović 2024, IRFA v95 — VIX-managed portfolios use daily VIX
close as the regime signal input.

CLI: python scripts/data_sprint/ingest_vix_fred.py --start 1990-01-02 --end 2026-04-14
Idempotent: merges with any existing parquet, dedupes by timestamp.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).parent))
from _utils import DATA_DIR, retry, setup_logger  # noqa: E402

FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
SERIES_ID = "VIXCLS"


def fetch(start: str, end: str, log) -> pd.DataFrame:
    def _call() -> pd.DataFrame:
        r = requests.get(
            FRED_URL,
            params={"id": SERIES_ID, "cosd": start, "coed": end},
            timeout=60,
        )
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        return df

    df = retry(_call, log=log)
    # FRED CSV headers vary by date — normalize lookups case-insensitively
    cols_lower = {c.lower(): c for c in df.columns}
    date_col = cols_lower.get("observation_date") or cols_lower.get("date") or df.columns[0]
    value_col = cols_lower.get(SERIES_ID.lower(), SERIES_ID)
    df["date"] = pd.to_datetime(df[date_col])
    df = df.set_index("date")
    # FRED marks missing days (holidays) as "." — coerce to NaN then drop
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    df = df.dropna(subset=[value_col])
    df = df[[value_col]].rename(columns={value_col: "close"})
    df = df.sort_index()
    df = df[~df.index.duplicated(keep="last")]
    return df


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--start", default="1990-01-02")
    ap.add_argument("--end", default="2026-04-14")
    ap.add_argument(
        "--output",
        default=str(DATA_DIR / "vix" / "VIXCLS.parquet"),
    )
    args = ap.parse_args()
    log = setup_logger("ingest_vix_fred")
    log.info("FRED VIXCLS fetch start=%s end=%s", args.start, args.end)

    df = fetch(args.start, args.end, log)
    log.info("fetched n_bars=%d first=%s last=%s", len(df), df.index.min(), df.index.max())

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        existing = pd.read_parquet(out)
        merged = pd.concat([existing, df])
        merged = merged[~merged.index.duplicated(keep="last")].sort_index()
        log.info("merged existing %d + new %d = %d rows", len(existing), len(df), len(merged))
        merged.to_parquet(out)
    else:
        df.to_parquet(out)
    log.info("wrote %s", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
