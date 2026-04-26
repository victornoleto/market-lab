"""Fetch CFTC Legacy Futures-Only weekly reports for Gold (COMEX, code 088691).

Source: Socrata API at https://publicreporting.cftc.gov/resource/6dca-aqww.json
Range: 1986-01-15 → latest available (auto-detected).
Output: data/external/macro/cftc_cot_gold_weekly.parquet (minimal columns).

Citation: `[trading_systems_methods, p.639-640]` — Briese COT Index uses
commercials and small-trader (nonreportable) net-long positions.

Run once before backtest; idempotent (overwrites cache).
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

CFTC_GOLD_CODE = "088691"
SOCRATA_ENDPOINT = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"
KEEP_COLS = [
    "report_date_as_yyyy_mm_dd",
    "comm_positions_long_all",
    "comm_positions_short_all",
    "nonrept_positions_long_all",
    "nonrept_positions_short_all",
    "noncomm_positions_long_all",
    "noncomm_positions_short_all",
    "open_interest_all",
]
PAGE_SIZE = 1000


def fetch_paginated() -> list[dict]:
    rows: list[dict] = []
    offset = 0
    while True:
        params = {
            "cftc_contract_market_code": CFTC_GOLD_CODE,
            "$select": ",".join(KEEP_COLS),
            "$order": "report_date_as_yyyy_mm_dd ASC",
            "$limit": PAGE_SIZE,
            "$offset": offset,
        }
        url = SOCRATA_ENDPOINT + "?" + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url, timeout=60) as resp:
            page = json.loads(resp.read().decode("utf-8"))
        if not page:
            break
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
        time.sleep(0.2)
    return rows


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    out_path = repo_root / "data" / "external" / "macro" / "cftc_cot_gold_weekly.parquet"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Fetching CFTC Legacy weekly Gold (code {CFTC_GOLD_CODE})...", file=sys.stderr)
    rows = fetch_paginated()
    print(f"  pulled {len(rows)} weekly records", file=sys.stderr)

    df = pd.DataFrame(rows)
    df["report_date"] = pd.to_datetime(df["report_date_as_yyyy_mm_dd"]).dt.tz_localize(None)
    for col in KEEP_COLS[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = (
        df.set_index("report_date")
          .drop(columns=["report_date_as_yyyy_mm_dd"])
          .sort_index()
    )
    if df.index.has_duplicates:
        df = df[~df.index.duplicated(keep="last")]

    df.to_parquet(out_path)
    print(
        f"  wrote {len(df)} rows to {out_path}\n"
        f"  range: {df.index.min().date()} → {df.index.max().date()}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
