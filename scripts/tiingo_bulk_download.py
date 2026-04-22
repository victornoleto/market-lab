#!/usr/bin/env python3
"""Bulk-download Tiingo OHLCV into ``data/tiingo/`` for offline use.

Goal: maximise the value of one Tiingo Power month — fetch a broad
universe to local parquet now so the subsequent backtests can run
without an active subscription.

Buckets (``--bucket``)
----------------------

* ``spx500``  — current SPX 500 ∪ historical SPX 500 at ``--start``
                (Wikipedia point-in-time, includes delistings up to today).
* ``spx400``  — current SP MidCap 400 (Wikipedia snapshot).
* ``spx600``  — current SP SmallCap 600 (Wikipedia snapshot).
* ``etf``     — broad/sector/bond/commodity ETFs (32 hand-picked).
* ``index``   — major US indices (5).
* ``crypto``  — top-10 by liquidity (Tiingo crypto endpoint).
* ``forex``   — majors + popular crosses (10).
* ``all``     — union of all above.

Idempotent: skips tickers whose manifest entry already covers
``[--start, --end]``. Re-runs are safe. When re-running with a wider
``--start``, the manifest check fails for each ticker and the full
widened range is refetched — TiingoStorage.write() merges the new
rows with the existing parquet (dedup by date), so no data is lost.

Failures are logged, not fatal — the run continues. Per-ticker outcome
goes to ``logs/tiingo_bulk.log``.

Default window
--------------

``--start`` defaults to **1990-01-01** to capture the widest history
each ticker has available (SPY from 1993-01, QQQ from 1999-03, TLT
from 2002-07, etc.). Tiingo gracefully returns whatever exists per
ticker — no 400s for pre-inception dates. Use a later ``--start`` for
smoke tests or to stay within a narrower research window.

Usage
-----

    .venv/bin/python scripts/tiingo_bulk_download.py \\
        --bucket all                    # widest history, today's --end

    .venv/bin/python scripts/tiingo_bulk_download.py \\
        --bucket etf --start 2014-01-01 --end 2026-04-15   # narrow smoke
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Callable

from tqdm import tqdm

# ---------------------------------------------------------------------------
# Static ticker lists — owned by this script, easy to amend
# ---------------------------------------------------------------------------

ETF_TICKERS = [
    # Broad
    "SPY", "IVV", "VOO", "QQQ", "IWM", "DIA", "VTI",
    "EFA", "EEM", "VEA", "VWO",
    # Sector SPDR
    "XLK", "XLF", "XLE", "XLV", "XLY", "XLP", "XLI", "XLU", "XLB", "XLRE", "XLC",
    # Bonds
    "AGG", "TLT", "IEF", "LQD", "HYG", "SHV",
    # Commodities / volatility
    "GLD", "SLV", "USO", "UNG", "VXX",
    # Leveraged ETFs — Plano B Path B LETF rotation universe
    # [leverage_for_the_long_run, ch.2]. Inceptions: SSO/QLD 2006-06-21,
    # UPRO 2009-06-23, TQQQ 2010-02-09. Tiingo serves these as standard
    # daily OHLCV — previously missing from bulk cache so reference_prices.py
    # fell back to yfinance (unstable adjusted-close causes Stage-2 drift).
    "SSO", "QLD", "UPRO", "TQQQ",
]

# Tiingo does NOT serve index prices directly (^GSPC, ^IXIC, ^DJI, ^RUT,
# ^VIX all 404) due to licensing. Standard substitute: use the tracking
# ETFs (SPY, QQQ, DIA, IWM, VXX) which are already in ETF_TICKERS.
# Strategies that ask for ``^GSPC`` (e.g. Clenow regime filter) should be
# rewired to use ``SPY`` when --data-source=tiingo is in effect.
INDEX_TICKERS: list[str] = []

CRYPTO_TICKERS = [
    "btcusd", "ethusd", "bnbusd", "xrpusd", "adausd",
    "solusd", "dogeusd", "avaxusd", "maticusd", "dotusd",
]

FOREX_TICKERS = [
    "eurusd", "gbpusd", "usdjpy", "usdchf", "audusd",
    "usdcad", "nzdusd", "eurjpy", "eurgbp", "gbpjpy",
    # Metals as FX (Pepperstone routes XAU/XAG via FX infra).
    "xauusd", "xagusd",
]

# Buckets that need network/cache (Wikipedia) are resolved lazily.

log = logging.getLogger("ai_trade.tiingo_bulk")


# ---------------------------------------------------------------------------
# Argparse
# ---------------------------------------------------------------------------


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Bulk download Tiingo OHLCV into data/tiingo/.",
    )
    ap.add_argument(
        "--bucket",
        required=True,
        choices=[
            "spx500", "spx400", "spx600", "etf", "index",
            "crypto", "forex", "all",
        ],
    )
    ap.add_argument(
        "--start", type=date.fromisoformat, default=date(1990, 1, 1),
        help="First date to fetch (default 1990-01-01 — widest window "
        "Tiingo typically serves for US equities/ETFs). Older tickers "
        "silently return their actual inception range; younger ones "
        "return what exists. Use a later date to speed up smoke tests.",
    )
    ap.add_argument(
        "--end", type=date.fromisoformat, default=date.today(),
        help="Last date (default: today).",
    )
    ap.add_argument(
        "--frequency", default="daily", choices=["daily", "1hour"],
        help="Bar frequency. v1 whitelist accepts {daily, 1hour} for "
        "equity/etf/crypto/forex; index is daily-only (Tiingo IEX "
        "doesn't cover indices).",
    )
    ap.add_argument(
        "--storage-root", type=Path, default=Path("data/tiingo"),
    )
    ap.add_argument(
        "--throttle-ms", type=int, default=50,
        help="Delay between API calls in milliseconds (default 50). "
        "Tiingo Power has generous limits but this avoids bursty 429s.",
    )
    ap.add_argument(
        "--limit", type=int, default=None,
        help="Stop after N tickers (smoke test). Default: no limit.",
    )
    ap.add_argument(
        "--log-level", default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return ap.parse_args(argv)


# ---------------------------------------------------------------------------
# Bucket → ticker resolution
# ---------------------------------------------------------------------------


def _resolve_spx500(start: date) -> list[str]:
    """Wikipedia: current ∪ point-in-time at start date."""
    from ai_trade.backtest.data.wikipedia_spx import WikipediaSPX
    wiki = WikipediaSPX()
    current = wiki.current_tickers()
    historical = wiki.constituents_on(start)
    return sorted(current | historical)


def _resolve_spx400_or_600(which: str) -> list[str]:
    """Wikipedia snapshot — current constituents only (no historical rotation)."""
    if which not in {"spx400", "spx600"}:
        raise ValueError(which)
    import pandas as pd
    import urllib.request

    page = (
        "https://en.wikipedia.org/wiki/List_of_S%26P_400_companies"
        if which == "spx400"
        else "https://en.wikipedia.org/wiki/List_of_S%26P_600_companies"
    )
    req = urllib.request.Request(
        page, headers={"User-Agent": "ai-trade/0.1 (research; +github.com)"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8")
    import io
    tables = pd.read_html(io.StringIO(html))
    # First table usually has the constituents.
    df = tables[0]
    symbol_col = next(
        (c for c in df.columns if str(c).lower() in {"symbol", "ticker"}),
        None,
    )
    if symbol_col is None:
        raise ValueError(f"no Symbol column in {which} page; got {list(df.columns)}")
    return sorted(df[symbol_col].dropna().astype(str).unique())


# (bucket → (resolver, asset_class))
_RESOLVERS: dict[str, tuple[Callable[[date], list[str]], str]] = {
    "spx500":  (lambda s: _resolve_spx500(s), "equity"),
    "spx400":  (lambda s: _resolve_spx400_or_600("spx400"), "equity"),
    "spx600":  (lambda s: _resolve_spx400_or_600("spx600"), "equity"),
    "etf":     (lambda s: ETF_TICKERS, "etf"),
    "index":   (lambda s: INDEX_TICKERS, "index"),
    "crypto":  (lambda s: CRYPTO_TICKERS, "crypto"),
    "forex":   (lambda s: FOREX_TICKERS, "forex"),
}


def _resolve_bucket(bucket: str, start: date) -> list[tuple[str, str]]:
    """Return list of (ticker, asset_class) for the bucket."""
    if bucket == "all":
        out: list[tuple[str, str]] = []
        seen: set[str] = set()
        for sub in ("spx500", "spx400", "spx600", "etf", "index", "crypto", "forex"):
            for t, ac in _resolve_bucket(sub, start):
                if t not in seen:
                    out.append((t, ac))
                    seen.add(t)
        return out
    resolver, asset_class = _RESOLVERS[bucket]
    return [(t, asset_class) for t in resolver(start)]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _setup_logging(level: int) -> None:
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
        handlers=[
            logging.FileHandler("logs/tiingo_bulk.log", mode="a"),
            logging.StreamHandler(),
        ],
    )


def _summary_path(storage_root: Path, run_id: str) -> Path:
    return storage_root / f"bulk_summary_{run_id}.json"


def main(argv: list[str] | None = None) -> int:
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage

    args = _parse_args(argv)
    _setup_logging(getattr(logging, args.log_level))

    run_id = (
        f"bulk_{args.bucket}_{args.frequency}_"
        f"{datetime.now().strftime('%Y%m%d-%H%M')}"
    )
    log.info("=== %s ===", run_id)
    log.info(
        "bucket=%s freq=%s start=%s end=%s storage=%s throttle=%dms limit=%s",
        args.bucket, args.frequency, args.start, args.end, args.storage_root,
        args.throttle_ms, args.limit,
    )

    storage = TiingoStorage(root=args.storage_root)
    source = TiingoSource(storage=storage)

    log.info("Resolving ticker list for bucket=%s", args.bucket)
    pairs = _resolve_bucket(args.bucket, args.start)
    if args.limit:
        pairs = pairs[: args.limit]
    log.info("Universe: %d tickers", len(pairs))

    summary = {
        "run_id": run_id,
        "bucket": args.bucket,
        "frequency": args.frequency,
        "start": args.start.isoformat(),
        "end": args.end.isoformat(),
        "n_total": len(pairs),
        "n_skipped_cached": 0,
        "n_fetched": 0,
        "n_empty": 0,
        "n_errors": 0,
        "errors": [],
    }

    # Intraday (1hour) is not routed for index tickers — Tiingo IEX doesn't
    # cover indices. Skip them gracefully with a warning instead of crashing
    # the run on the whitelist check.
    if args.frequency == "1hour":
        pairs = [(t, ac) for (t, ac) in pairs if ac != "index"]

    pbar = tqdm(pairs, desc=run_id, unit="tk")
    for ticker, asset_class in pbar:
        if storage.has(ticker, args.start, args.end, frequency=args.frequency):
            summary["n_skipped_cached"] += 1
            pbar.set_postfix({"last": f"{ticker} (cached)"})
            continue
        try:
            df = source.fetch(
                ticker, args.start, args.end,
                asset_class=asset_class, frequency=args.frequency,
            )
        except Exception as exc:  # noqa: BLE001
            summary["n_errors"] += 1
            summary["errors"].append({"ticker": ticker, "error": str(exc)[:200]})
            log.warning("FAIL %s: %s", ticker, exc)
            pbar.set_postfix({"last": f"{ticker} ERR"})
            continue

        if df.empty:
            summary["n_empty"] += 1
            pbar.set_postfix({"last": f"{ticker} (empty)"})
        else:
            summary["n_fetched"] += 1
            pbar.set_postfix({"last": f"{ticker} ({len(df)})"})

        if args.throttle_ms > 0:
            time.sleep(args.throttle_ms / 1000.0)

    pbar.close()

    summary_path = _summary_path(args.storage_root, run_id)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    log.info(
        "Done: %d total | %d cached | %d fetched | %d empty | %d errors → %s",
        summary["n_total"], summary["n_skipped_cached"],
        summary["n_fetched"], summary["n_empty"], summary["n_errors"],
        summary_path,
    )
    return 0 if summary["n_errors"] == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
