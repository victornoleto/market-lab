"""Download OHLCV for the IBrX-100 proxy (yfinance ``.SA`` suffix).

One-shot script. Run once at the start of Phase D-MVP; the yfinance parquet
cache under ``.cache/yfinance/`` makes subsequent runs free.

Usage
-----
::

    .venv/bin/python -m scripts.phase_d_mvp.download_ibrx100 \
        --start 2010-01-01 --end 2026-04-15 [--log-path logs/download_ibrx100.log]

Behaviour
---------
* Iterates :data:`IBRX100_TICKERS` sequentially (yfinance rate-limits
  aggressively; concurrency makes failures worse, not better).
* Each ticker is fetched separately and cached to
  ``.cache/yfinance/<TICKER>.parquet`` by :class:`YFinanceSource`.
* Appends a unified log line per ticker: ``OK n_bars=<N>`` or
  ``EMPTY`` (delisted / no data) or ``ERROR <reason>``.
* Does NOT fail on individual ticker errors — logs and continues.
  Strategy D tolerates missing tickers; the dynamic universe filter will
  just skip them.

Survivorship bias note
----------------------
yfinance does not return delisted tickers. IBrX-100 turnover is ~15%/year.
Backtests rooted in this snapshot have current-member survivorship bias;
the disclaimer is mandatory in every report (CLAUDE.md Regra 2).
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, datetime
from pathlib import Path

from ai_trade.backtest.data.br_tickers import IBRX100_TICKERS
from ai_trade.backtest.data.yfinance_source import YFinanceSource

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _parse_date(text: str) -> date:
    return datetime.strptime(text, "%Y-%m-%d").date()


def _configure_logging(log_path: Path | None) -> logging.Logger:
    root = logging.getLogger("phase_d_mvp.download")
    root.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    stdout_h = logging.StreamHandler(sys.stdout)
    stdout_h.setFormatter(fmt)
    root.addHandler(stdout_h)
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_h = logging.FileHandler(log_path, mode="a")
        file_h.setFormatter(fmt)
        root.addHandler(file_h)
    return root


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=_parse_date, default=date(2010, 1, 1))
    parser.add_argument("--end", type=_parse_date, default=date(2026, 4, 15))
    parser.add_argument(
        "--log-path",
        type=Path,
        default=_PROJECT_ROOT / "logs" / "download_ibrx100.log",
        help="Append-only unified log in addition to stdout.",
    )
    parser.add_argument(
        "--tickers",
        nargs="*",
        default=None,
        help="Optional override — restrict to a subset of tickers (for debug).",
    )
    args = parser.parse_args(argv)

    log = _configure_logging(args.log_path)
    source = YFinanceSource()
    tickers = args.tickers or IBRX100_TICKERS

    log.info(
        "start tickers=%d start=%s end=%s cache=%s",
        len(tickers), args.start, args.end, source.cache_dir,
    )

    n_ok = n_empty = n_error = 0
    for i, ticker in enumerate(tickers, start=1):
        try:
            df = source.fetch(ticker, args.start, args.end)
        except Exception as exc:  # yfinance wraps many network errors
            n_error += 1
            log.error("[%d/%d] %s ERROR %s", i, len(tickers), ticker, exc)
            continue
        if df.empty:
            n_empty += 1
            log.warning("[%d/%d] %s EMPTY", i, len(tickers), ticker)
        else:
            n_ok += 1
            first = df.index.min().date()
            last = df.index.max().date()
            log.info(
                "[%d/%d] %s OK n_bars=%d first=%s last=%s",
                i, len(tickers), ticker, len(df), first, last,
            )

    log.info(
        "done ok=%d empty=%d error=%d total=%d",
        n_ok, n_empty, n_error, len(tickers),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
