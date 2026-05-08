#!/usr/bin/env python3
"""Targeted Tiingo downloader for letf_rotation_hunt.

Downloads real ETF daily OHLCV for the 6 in-scope LETFs plus 4 risk-off
candidates not already in the bulk cache (TLT/IEF/SPY/QQQ/GLD already
present from prior bulk runs). Storage-first via TiingoStorage manifest,
so re-runs skip already-covered tickers.

In-scope universe per studies/letf_rotation_hunt/SPEC.md §4.1:
    LETFs: UPRO, SSO, TQQQ, QLD, TMF, UGL, SOXL
    Risk-off: EDV, ZROZ, BIL  (TLT, IEF, BIL alternatives also fine)

Real ETF data is the post-inception ground truth for synth parity validation
(iter 000) and for window-matched backtests where Tiingo coverage exists.
Pre-inception gaps fall back to testfolio synths (UPROSIM, etc.).

Citations
---------
* LETF inceptions: [leverage_for_the_long_run, ch.2]
  - SSO/QLD: 2006-06-21 (ProShares prospectus)
  - UPRO: 2009-06-25
  - TQQQ: 2010-02-09
  - UGL: 2008-12-01
  - TMF: 2009-04-16
  - SOXL: 2010-03-11
* Storage-first idempotency: [scripts/tiingo_bulk_download.py docstring]

Usage
-----
    .venv/bin/python studies/letf_rotation_hunt/scripts/fetch_tiingo_letfs.py
    .venv/bin/python studies/letf_rotation_hunt/scripts/fetch_tiingo_letfs.py \\
        --start 1990-01-01 --end 2026-04-30

Logs to logs/tiingo.log (append) per the project's unified-log convention.
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import date
from pathlib import Path

from market_lab.backtest.data.tiingo_source import TiingoSource
from market_lab.backtest.data.tiingo_storage import TiingoStorage

# 10 in-scope tickers. SSO/QLD/UPRO/TQQQ are listed in scripts/tiingo_bulk_download.py
# ETF_TICKERS but the bulk run never picked them up (cache empty as of 2026-05-05).
# TMF/UGL/SOXL/EDV/ZROZ/BIL are missing from the bulk list entirely.
TICKERS: list[str] = [
    "UPRO",  # 3x SPY  — inception 2009-06-25
    "SSO",   # 2x SPY  — inception 2006-06-21
    "TQQQ",  # 3x NDX  — inception 2010-02-09
    "QLD",   # 2x NDX  — inception 2006-06-21
    "TMF",   # 3x 20yr — inception 2009-04-16
    "UGL",   # 2x Gold — inception 2008-12-01
    "SOXL",  # 3x SOX  — inception 2010-03-11 (T4d only)
    "EDV",   # 25yr Vanguard ext duration — inception 2007-12-06
    "ZROZ",  # 25yr Strips — inception 2009-10-30
    "BIL",   # 1-3m T-bill — inception 2007-05-30
]

DEFAULT_START = date(1990, 1, 1)
DEFAULT_END = date(2026, 4, 30)


def _setup_logging(log_path: Path) -> logging.Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    fmt = "%(asctime)s %(levelname)s %(name)s — %(message)s"
    handlers: list[logging.Handler] = [
        logging.FileHandler(log_path, mode="a"),
        logging.StreamHandler(sys.stdout),
    ]
    logging.basicConfig(level=logging.INFO, format=fmt, handlers=handlers, force=True)
    return logging.getLogger("fetch_tiingo_letfs")


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fetch LETF rotation hunt tickers from Tiingo")
    p.add_argument("--start", default=DEFAULT_START.isoformat(),
                   help=f"ISO start date (default {DEFAULT_START})")
    p.add_argument("--end", default=DEFAULT_END.isoformat(),
                   help=f"ISO end date (default {DEFAULT_END})")
    p.add_argument("--storage-root", default="data/tiingo",
                   help="TiingoStorage root (default data/tiingo)")
    p.add_argument("--log-path", default="logs/tiingo.log",
                   help="Append-only log path (default logs/tiingo.log)")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    log = _setup_logging(Path(args.log_path))

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)

    log.info(
        "fetch_tiingo_letfs: %d tickers, range %s..%s, storage=%s",
        len(TICKERS), start, end, args.storage_root,
    )

    storage = TiingoStorage(root=Path(args.storage_root))
    source = TiingoSource(storage=storage)

    n_cached = 0
    n_fetched = 0
    n_empty = 0
    n_errors = 0

    for ticker in TICKERS:
        try:
            already = storage.has(ticker, start, end, frequency="daily")
            df = source.fetch(ticker, start, end, asset_class="etf", frequency="daily")
        except Exception as exc:  # noqa: BLE001 — log and continue per bulk script convention
            n_errors += 1
            log.error("FAIL %s: %s", ticker, exc)
            continue

        if df.empty:
            n_empty += 1
            log.warning("EMPTY %s (Tiingo 404 or no data in range)", ticker)
            continue

        n_rows = len(df)
        first = df.index.min().date()
        last = df.index.max().date()
        if already:
            n_cached += 1
            log.info("CACHED %s — %d rows %s..%s", ticker, n_rows, first, last)
        else:
            n_fetched += 1
            log.info("FETCHED %s — %d rows %s..%s", ticker, n_rows, first, last)

    log.info(
        "done: fetched=%d cached=%d empty=%d errors=%d",
        n_fetched, n_cached, n_empty, n_errors,
    )
    return 1 if n_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
