"""Ingest VIX-ETF term-structure proxies (VIXY, VIXM, VXX) — Tiingo daily.

Re-fetches full history from inception because the existing
data/tiingo/daily/prices/VIXY.parquet only starts 2021-01-04 (bulk-download
window was too narrow) and VIXM is essentially empty (4 bars). Inception
dates (per Tiingo probe 2026-04-23):
  * VIXY: 2011-01-04 (ProShares VIX Short-Term Futures ETF)
  * VIXM: 2011-01-04 (ProShares VIX Mid-Term Futures ETF)
  * VXX:  2009-01-30 (iPath Series B S&P 500 VIX Short-Term Futures ETN)

Output: data/phase3_7/vix/{TICKER}.parquet with canonical
[open, high, low, close, adj_close, volume] columns.

Rationale: H2 VIX-gated LETF rotation (per Phase 3.7-1) benefits from
multi-decade backtest; Gayed-style IS 1970-2000 / OOS 2001-2015 splits are
impossible for VIX futures ETFs which only exist 2009+, but ~15 years of
daily data is still adequate for bootstrap-99.9%-CI with n>1500.

Citation: Božović 2024 IRFA §3; mandate §4.1-4.2 splits.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).parent))
from _utils import DATA_DIR, load_env, retry, setup_logger  # noqa: E402
import os

TIINGO_BASE = "https://api.tiingo.com/tiingo/daily"

TICKERS = [
    ("VIXY", "2011-01-04"),
    ("VIXM", "2011-01-04"),
    ("VXX", "2009-01-30"),
]

CANONICAL_COLS = ["open", "high", "low", "close", "adj_close", "volume"]


def fetch_tiingo_daily(ticker: str, start: str, end: str, key: str, log) -> pd.DataFrame:
    def _call() -> list[dict]:
        r = requests.get(
            f"{TIINGO_BASE}/{ticker}/prices",
            params={"startDate": start, "endDate": end, "format": "json"},
            headers={"Authorization": f"Token {key}"},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()

    data = retry(_call, log=log)
    if not data:
        return pd.DataFrame(columns=CANONICAL_COLS)
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None).dt.normalize()
    df = df.set_index("date").sort_index()
    col_map = {"adjOpen": "adj_open", "adjHigh": "adj_high", "adjLow": "adj_low",
               "adjClose": "adj_close", "adjVolume": "adj_volume"}
    df = df.rename(columns=col_map)
    cols_present = [c for c in CANONICAL_COLS if c in df.columns]
    df = df[cols_present]
    df = df[~df.index.duplicated(keep="last")]
    return df


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--end", default="2026-04-14")
    ap.add_argument("--output-dir", default=str(DATA_DIR / "vix"))
    args = ap.parse_args()

    load_env()
    key = os.environ.get("TIINGO_API_KEY", "")
    if not key:
        raise SystemExit("TIINGO_API_KEY not set in env or .env")

    log = setup_logger("ingest_vix_proxies")
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for ticker, inception in TICKERS:
        log.info("Tiingo daily fetch ticker=%s start=%s end=%s", ticker, inception, args.end)
        df = fetch_tiingo_daily(ticker, inception, args.end, key, log)
        if df.empty:
            log.warning("ticker=%s returned empty; skipping", ticker)
            continue
        out = out_dir / f"{ticker}.parquet"
        if out.exists():
            existing = pd.read_parquet(out)
            merged = pd.concat([existing, df])
            merged = merged[~merged.index.duplicated(keep="last")].sort_index()
            log.info("merged %s: %d + %d = %d rows", ticker, len(existing), len(df), len(merged))
            merged.to_parquet(out)
        else:
            df.to_parquet(out)
            log.info("wrote %s rows=%d first=%s last=%s", out, len(df), df.index.min(), df.index.max())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
