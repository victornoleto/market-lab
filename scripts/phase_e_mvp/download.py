"""Download OHLCV for Strategy E multi-market universe.

Combines SP500 top-200 (yfinance, no suffix) + IBrX-100 (yfinance, ``.SA``
suffix) = ~300 tickers. Same pattern as ``phase_d_mvp.download_ibrx100``
but wider coverage.

Sequential (yfinance rate-limits aggressively). Expected real-time: ~5
minutes for the US batch + ~2 minutes for BR (BR already cached from
Phase D-MVP, so the ``--skip-cached`` default makes the BR leg a no-op).

Usage::

    .venv/bin/python -m scripts.phase_e_mvp.download \
        --start 2010-01-01 --end 2026-04-15 \
        [--log-path logs/download_e.log]
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, datetime
from pathlib import Path

from ai_trade.backtest.data.yfinance_source import YFinanceSource

from scripts.phase_e_mvp.universe import MULTIMARKET_TICKERS

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _parse_date(text: str) -> date:
    return datetime.strptime(text, "%Y-%m-%d").date()


def _configure_logging(log_path: Path) -> logging.Logger:
    log = logging.getLogger("phase_e_mvp.download")
    log.setLevel(logging.INFO)
    log.handlers.clear()
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    stdout_h = logging.StreamHandler(sys.stdout)
    stdout_h.setFormatter(fmt)
    log.addHandler(stdout_h)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_h = logging.FileHandler(log_path, mode="a")
    file_h.setFormatter(fmt)
    log.addHandler(file_h)
    return log


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=_parse_date, default=date(2010, 1, 1))
    parser.add_argument("--end", type=_parse_date, default=date(2026, 4, 15))
    parser.add_argument(
        "--log-path", type=Path,
        default=_PROJECT_ROOT / "logs" / "download_phase_e.log",
    )
    parser.add_argument(
        "--tickers", nargs="*", default=None,
        help="Override — subset of tickers (debug).",
    )
    args = parser.parse_args(argv)

    log = _configure_logging(args.log_path)
    source = YFinanceSource()
    tickers = args.tickers or MULTIMARKET_TICKERS

    log.info("Phase E download: %d tickers, range %s..%s",
             len(tickers), args.start, args.end)

    n_ok = n_empty = n_error = 0
    for i, ticker in enumerate(tickers, start=1):
        try:
            df = source.fetch(ticker, args.start, args.end)
        except Exception as exc:
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
            log.info("[%d/%d] %s OK n_bars=%d first=%s last=%s",
                     i, len(tickers), ticker, len(df), first, last)

    log.info("done ok=%d empty=%d error=%d total=%d",
             n_ok, n_empty, n_error, len(tickers))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
