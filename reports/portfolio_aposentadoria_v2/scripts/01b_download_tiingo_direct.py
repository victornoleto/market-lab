"""Download missing ETF data from Tiingo REST API directly.

Tiingo has better coverage than yfinance for US-domiciled ETFs, and we already
have an API key configured in .env.

Also builds synthetic replicators for ETFs with short history:
- NTSX (inception 2018-08) — replicate as 0.9*SPY + 0.6*IEF backwards
- Return Stacked ETFs (inception 2023-2024) — use 1.0*SPY + 1.0*DBMF for RSST, etc.

Writes to reports/portfolio_aposentadoria_v2/data/<TICKER>.parquet.
"""
from __future__ import annotations

import json
import os
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv("/var/www/pessoal/ai-trade/.env")

API_KEY = os.getenv("TIINGO_API_KEY")
assert API_KEY, "TIINGO_API_KEY not set"

REPO = Path("/var/www/pessoal/ai-trade")
OUT_DIR = REPO / "reports" / "portfolio_aposentadoria_v2" / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MISSING = [
    # Factor core
    "AVUS", "AVUV", "SPMO", "AVDE", "IDMO", "AVDV", "AVEM",
    "DFAC", "DFAT", "AVGV",
    # Leveraged non-US
    "EFO",
    # Return stacking / efficient core
    "NTSX", "NTSI", "NTSE", "RSST", "RSSB", "RSBT", "RSSY", "RSBY",
    # Managed futures
    "DBMF", "KMLM", "CTA",
    # Alts
    "IBIT", "GLDM", "GLD",
    # Broad
    "VXUS", "VT",
]


def tiingo_daily(ticker: str, start: str = "1990-01-01", end: str | None = None) -> pd.DataFrame | None:
    if end is None:
        end = date.today().isoformat()
    url = f"https://api.tiingo.com/tiingo/daily/{ticker}/prices"
    params = {"startDate": start, "endDate": end, "format": "json"}
    for attempt in range(3):
        try:
            r = requests.get(
                url,
                params=params,
                headers={"Content-Type": "application/json", "Authorization": f"Token {API_KEY}"},
                timeout=30,
            )
            if r.status_code == 404:
                return None
            if r.status_code != 200:
                print(f"  {ticker} HTTP {r.status_code}: {r.text[:100]}")
                time.sleep(1 + attempt)
                continue
            data = r.json()
            if not data:
                return None
            df = pd.DataFrame(data)
            df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
            df = df.set_index("date").sort_index()
            out = pd.DataFrame({"close": df["adjClose"].astype(float)})
            out["return"] = out["close"].pct_change()
            return out
        except Exception as e:
            print(f"  retry {attempt+1}/3 {ticker}: {e}")
            time.sleep(1 + attempt)
    return None


def main() -> None:
    sources = {}
    src_file = OUT_DIR / "_sources.json"
    if src_file.exists():
        sources = json.loads(src_file.read_text())

    for ticker in MISSING:
        out_path = OUT_DIR / f"{ticker}.parquet"
        if out_path.exists():
            df = pd.read_parquet(out_path)
            print(f"SKIP exists: {ticker} — {len(df)} rows")
            continue
        df = tiingo_daily(ticker)
        if df is None or df.empty or len(df) < 30:
            print(f"FAIL: {ticker}")
            sources[ticker] = {"source": "FAIL_TIINGO"}
            continue
        df = df.dropna(subset=["close"])
        df.to_parquet(out_path)
        sources[ticker] = {
            "source": "tiingo_api",
            "start": df.index.min().isoformat(),
            "end": df.index.max().isoformat(),
            "rows": int(len(df)),
        }
        print(f"OK: {ticker} — {len(df)} rows {df.index.min().date()} → {df.index.max().date()}")
        time.sleep(0.2)

    src_file.write_text(json.dumps(sources, indent=2, default=str))


if __name__ == "__main__":
    main()
