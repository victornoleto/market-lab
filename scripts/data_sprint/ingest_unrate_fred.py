"""Ingest UNRATE (civilian unemployment rate, monthly, SA) from FRED.

Output: data/external/macro/unrate_monthly.parquet with column [unrate]
indexed by first-of-month DatetimeIndex (FRED reference-month stamp).

Feed rationale (LRS Phase 7C pre-registration):
  * FRED is free, no auth, no rate limit on CSV downloads (same channel as
    the VIXCLS ingest in this directory).
  * UNRATE is the macro input of the Growth-Trend Timing regime gate
    (UNRATE > its 12-month SMA = recession-risk regime). The rule source is
    the Philosophical Economics "Growth-Trend Timing" essay — a documented
    EXCEPTION to the book-citation rule approved by the user (2026-06-09);
    the family anchors on `[leverage_for_the_long_run, p.9]` (S&P 500 below
    its 200dma 68.2% of the time in recessions vs 19.4% in expansions).
  * LIMITATION (recorded, not blocking): FRED serves the LATEST revised
    vintage, not point-in-time ALFRED data. Revisions to UNRATE are small
    (seasonal-adjustment updates), but backtests on revised data remain
    slightly optimistic.

CLI: uv run python scripts/data_sprint/ingest_unrate_fred.py --start 1948-01-01
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
from _utils import retry, setup_logger  # noqa: E402

FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
SERIES_ID = "UNRATE"
DEFAULT_OUTPUT = Path("data/external/macro/unrate_monthly.parquet")


def fetch(start: str, end: str, log) -> pd.DataFrame:
    def _call() -> pd.DataFrame:
        r = requests.get(
            FRED_URL,
            params={"id": SERIES_ID, "cosd": start, "coed": end},
            timeout=60,
        )
        r.raise_for_status()
        return pd.read_csv(io.StringIO(r.text))

    df = retry(_call, log=log)
    cols_lower = {c.lower(): c for c in df.columns}
    date_col = cols_lower.get("observation_date") or cols_lower.get("date") or df.columns[0]
    value_col = cols_lower.get(SERIES_ID.lower(), SERIES_ID)
    df["date"] = pd.to_datetime(df[date_col])
    df = df.set_index("date")
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    df = df.dropna(subset=[value_col])
    df = df[[value_col]].rename(columns={value_col: "unrate"})
    df = df.sort_index()
    df = df[~df.index.duplicated(keep="last")]
    return df


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--start", default="1948-01-01")
    ap.add_argument("--end", default="2026-06-09")
    ap.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = ap.parse_args()
    log = setup_logger("ingest_unrate_fred")
    log.info("FRED UNRATE fetch start=%s end=%s", args.start, args.end)

    df = fetch(args.start, args.end, log)
    log.info("fetched n_obs=%d first=%s last=%s", len(df), df.index.min(), df.index.max())

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
