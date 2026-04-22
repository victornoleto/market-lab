"""Ingest Tiingo IEX 1-minute intraday bars for H1 intraday SPY momentum.

Output: data/phase3_7/intraday/{TICKER}_1min.parquet with canonical
[open, high, low, close, volume] columns and UTC DatetimeIndex (the
Tiingo IEX API returns ISO-8601 timestamps with Z suffix).

Tiingo IEX minute-data coverage (probed 2026-04-23):
  * IEX exchange founded 2013; Tiingo IEX minute-level data effectively
    starts 2017-01-03 for QQQ/DIA, 2017-06-01 for SPY.
  * Full 9:30-16:00 ET session = 390 regular-hours minutes/day; extended
    hours add pre-market (4:00-9:30) + after-hours (16:00-20:00) = 585 bars.
    This script requests resampleFreq=1min which returns ALL trades;
    callers can later filter by hour-of-day for regular-hours-only.

Zarattini-Aziz-Barbon 2024 (SSRN 4824172 — H1 base paper) uses SPY
minute bars 2007-early 2024 for noise-boundary computation. We have
access to 2017-01 onwards — 9 years, ~2,250 trading days, each with
~585 bars. Total n per ticker ≈ 1.3M rows. Sufficient for the
bootstrap-99.9%-CI gate (mandate §2.4) which requires n>>1500.

CLI chunks the download by year to stay under Tiingo's per-request size
limit and to allow resume on interrupt.
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).parent))
from _utils import DATA_DIR, load_env, retry, setup_logger  # noqa: E402
import os

IEX_BASE = "https://api.tiingo.com/iex"

CANONICAL_COLS = ["open", "high", "low", "close", "volume"]


def fetch_chunk(ticker: str, start: str, end: str, key: str, log) -> pd.DataFrame:
    def _call() -> list[dict]:
        r = requests.get(
            f"{IEX_BASE}/{ticker}/prices",
            params={
                "startDate": start,
                "endDate": end,
                "resampleFreq": "1min",
                "format": "json",
            },
            headers={"Authorization": f"Token {key}"},
            timeout=120,
        )
        r.raise_for_status()
        return r.json()

    data = retry(_call, log=log)
    if not data:
        return pd.DataFrame(columns=CANONICAL_COLS)
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"], utc=True)
    df = df.set_index("date").sort_index()
    cols_present = [c for c in CANONICAL_COLS if c in df.columns]
    df = df[cols_present]
    df = df[~df.index.duplicated(keep="last")]
    return df


def week_chunks(start_year: int, end_date: date, step_days: int = 7) -> list[tuple[str, str]]:
    """Tiingo IEX /prices returns a hard max 10,000 bars per request.

    At ~585 extended-hours bars/trading-day, ≥17 trading days = ≥10K bars and
    truncation silently caps the response. Weekly chunks (5 trading days,
    ~2,925 bars) leave a 3× headroom.
    """
    chunks: list[tuple[str, str]] = []
    d = date(start_year, 1, 1)
    while d <= end_date:
        nxt = d + timedelta(days=step_days - 1)
        if nxt > end_date:
            nxt = end_date
        chunks.append((d.isoformat(), nxt.isoformat()))
        d = nxt + timedelta(days=1)
    return chunks


def ingest_ticker(
    ticker: str,
    start_year: int,
    end_d: date,
    key: str,
    out_dir: Path,
    log,
) -> Path | None:
    out = out_dir / f"{ticker}_1min.parquet"
    if out.exists():
        existing = pd.read_parquet(out)
        log.info("existing %s: %d rows (first=%s last=%s)", ticker,
                 len(existing), existing.index.min(), existing.index.max())
    else:
        existing = None

    frames: list[pd.DataFrame] = []
    chunks = week_chunks(start_year, end_d)
    log.info("%s: %d weekly chunks to fetch", ticker, len(chunks))
    for i, (s, e) in enumerate(chunks):
        df = fetch_chunk(ticker, s, e, key, log)
        if df.empty:
            continue
        if len(df) >= 9000:
            log.warning("%s %s→%s: %d bars near 10K cap — consider smaller chunks",
                        ticker, s, e, len(df))
        frames.append(df)
        if (i + 1) % 50 == 0:
            log.info("%s progress: %d/%d chunks, %d bars so far",
                     ticker, i + 1, len(chunks), sum(len(f) for f in frames))
        time.sleep(0.15)

    if not frames:
        log.warning("%s: all chunks empty", ticker)
        return None

    new = pd.concat(frames)
    new = new[~new.index.duplicated(keep="last")].sort_index()
    if existing is not None:
        merged = pd.concat([existing, new])
        merged = merged[~merged.index.duplicated(keep="last")].sort_index()
    else:
        merged = new
    merged.to_parquet(out)
    log.info("wrote %s rows=%d first=%s last=%s", out, len(merged),
             merged.index.min(), merged.index.max())
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument(
        "--tickers",
        default="SPY,QQQ",
        help="Comma-separated ETF tickers (default: SPY,QQQ — H1 primary+confirmation)",
    )
    ap.add_argument("--start-year", type=int, default=2017)
    ap.add_argument("--end", default="2026-04-14")
    ap.add_argument("--output-dir", default=str(DATA_DIR / "intraday"))
    args = ap.parse_args()

    load_env()
    key = os.environ.get("TIINGO_API_KEY", "")
    if not key:
        raise SystemExit("TIINGO_API_KEY not set in env or .env")

    log = setup_logger("ingest_intraday_etf")
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    end_d = date.fromisoformat(args.end)

    tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    log.info("IEX 1-min ingest tickers=%s start_year=%d end=%s", tickers, args.start_year, args.end)
    for t in tickers:
        ingest_ticker(t, args.start_year, end_d, key, out_dir, log)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
