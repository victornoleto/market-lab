"""Fetch CFTC Disaggregated (DCOT) Futures-Only weekly Gold report (code 088691).

Source: Socrata API at https://publicreporting.cftc.gov/resource/72hh-3qpy.json
Range: 2006-06-13 → latest available (auto-detected, ~1030 weekly rows).
Output: data/external/macro/cftc_dcot_gold_weekly.parquet (minimal columns).

Citation: `[trading_systems_methods, p.640]` — Kaufman: COT positioning
extremes contrarian; DCOT money-manager bucket isolates speculator flow.

Adapted from iter 017's `fetch_cftc.py` with DCOT endpoint + MM columns.
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
SOCRATA_DCOT = "https://publicreporting.cftc.gov/resource/72hh-3qpy.json"
KEEP_COLS = [
    "report_date_as_yyyy_mm_dd",
    "m_money_positions_long_all",
    "m_money_positions_short_all",
    "prod_merc_positions_long",
    "prod_merc_positions_short",
    "swap_positions_long_all",
    "swap__positions_short_all",  # NOTE: CFTC API has double underscore here
    "other_rept_positions_long",
    "other_rept_positions_short",
    "nonrept_positions_long_all",
    "nonrept_positions_short_all",
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
        url = SOCRATA_DCOT + "?" + urllib.parse.urlencode(params)
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
    out_path = repo_root / "data" / "external" / "macro" / "cftc_dcot_gold_weekly.parquet"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Fetching CFTC DCOT weekly Gold (code {CFTC_GOLD_CODE})...", file=sys.stderr)
    rows = fetch_paginated()
    print(f"  pulled {len(rows)} weekly DCOT records", file=sys.stderr)

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
        f"  range: {df.index.min().date()} → {df.index.max().date()}\n"
        f"  m_money sample (latest row): long={int(df['m_money_positions_long_all'].iloc[-1])}, "
        f"short={int(df['m_money_positions_short_all'].iloc[-1])}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
