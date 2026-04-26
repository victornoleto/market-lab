"""Ingest 10y TIPS yield (DFII10) daily from FRED.

Output: data/external/macro/dfii10_daily.parquet with columns [close]
indexed by UTC midnight DatetimeIndex (one bar per business day, holidays
absent — FRED publishes the constant-maturity real rate at NY close).

Feed rationale (Gold Swing Loop iter 014):
  * FRED is free, no auth, no rate limit on CSV downloads.
  * DFII10 = 10-year TIPS yield, the canonical real-rate gauge that
    drives gold's macro regime per Erb & Harvey (2013) FAJ + Bauer &
    Mertens (2018) FRBSF.
  * Coverage 2003-01-02 → present; spans gld_long (2004-11-18+) fully.

Citation: `[trading_systems_methods, p.13]` — metals are low-noise → trend-following;
real-rate moves are the underlying low-noise driver. CLAUDE.md "prefere log
unificado em scripts longos" — appends to logs/phase3_7_data_sprint.log.

CLI: uv run python scripts/data_sprint/ingest_dfii10_fred.py --start 2003-01-02 --end 2026-04-25
Idempotent: overwrites parquet with full re-fetch.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO_ROOT / "data" / "external" / "macro" / "dfii10_daily.parquet"

FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
SERIES_ID = "DFII10"


def fetch(start: str, end: str) -> pd.DataFrame:
    r = requests.get(
        FRED_URL,
        params={"id": SERIES_ID, "cosd": start, "coed": end},
        timeout=60,
    )
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))

    cols_lower = {c.lower(): c for c in df.columns}
    date_col = cols_lower.get("observation_date") or cols_lower.get("date") or df.columns[0]
    value_col = cols_lower.get(SERIES_ID.lower(), SERIES_ID)

    df["date"] = pd.to_datetime(df[date_col])
    df = df.set_index("date")
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    df = df.dropna(subset=[value_col])
    df = df[[value_col]].rename(columns={value_col: "close"})
    df = df.sort_index()
    df = df[~df.index.duplicated(keep="last")]
    return df


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--start", default="2003-01-02")
    ap.add_argument("--end", default="2026-04-25")
    ap.add_argument("--output", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    print(f"FRED DFII10 fetch start={args.start} end={args.end}", file=sys.stderr)
    df = fetch(args.start, args.end)
    print(f"fetched n_bars={len(df)} first={df.index.min()} last={df.index.max()}", file=sys.stderr)
    if len(df) < 1000:
        print(f"ERROR: suspiciously few bars ({len(df)})", file=sys.stderr)
        return 1

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out)
    print(f"wrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
