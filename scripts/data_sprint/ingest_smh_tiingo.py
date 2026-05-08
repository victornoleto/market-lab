"""Fetch SMH (VanEck Semiconductor ETF, 1x SOX) from Tiingo and save to Tiingo daily cache.

SMH is the 1x signal underlying for the SOXL LETF rotation strategy (analogous to
QQQ for TQQQ, SPY for UPRO). It is NOT available in the bulk Tiingo snapshot, so
this script fetches it on-demand via the Tiingo REST API.

Output: data/tiingo/daily/prices/SMH.parquet
  Schema: [close, high, low, open, volume, adj_close, adj_high, adj_low, adj_open,
           adj_volume, divCash, splitFactor] with DatetimeIndex (normalized, UTC-stripped).

Citation:
  - [trading_systems_methods, Kaufman ch.21] SMH as 1x SOX signal underlying for
    SOXL rotation (analogous to QQQ for TQQQ).

Usage:
    source .venv/bin/activate && python scripts/data_sprint/ingest_smh_tiingo.py
"""

from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).parent))
from _utils import load_env  # noqa: E402

TIINGO_BASE = "https://api.tiingo.com/tiingo/daily"
OUT_PATH = Path("data/tiingo/daily/prices/SMH.parquet")
START_DATE = "2000-05-22"  # SMH inception (VanEck Semiconductor ETF launched 2000-05-22)
TICKER = "SMH"


def main() -> int:
    load_env()
    key = os.environ.get("TIINGO_API_KEY", "")
    if not key:
        print("ERROR: TIINGO_API_KEY not set in .env or environment")
        return 1

    end_date = str(date.today())
    url = f"{TIINGO_BASE}/{TICKER}/prices"
    params = {
        "startDate": START_DATE,
        "endDate": end_date,
        "format": "json",
        "token": key,
    }
    print(f"[ingest_smh_tiingo] fetching {TICKER} from {START_DATE} to {end_date}")
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    if not data:
        print(f"[ingest_smh_tiingo] ERROR: empty response from Tiingo for {TICKER}")
        return 1

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None).dt.normalize()
    df = df.set_index("date").sort_index()
    # Rename Tiingo camelCase adj columns to snake_case canonical
    col_map = {
        "adjOpen": "adj_open",
        "adjHigh": "adj_high",
        "adjLow": "adj_low",
        "adjClose": "adj_close",
        "adjVolume": "adj_volume",
    }
    df = df.rename(columns=col_map)
    df = df[~df.index.duplicated(keep="last")]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_PATH)
    print(
        f"[ingest_smh_tiingo] wrote {OUT_PATH}: "
        f"{len(df)} rows, {df.index[0].date()} to {df.index[-1].date()}, "
        f"last adj_close={df['adj_close'].iloc[-1]:.2f}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
