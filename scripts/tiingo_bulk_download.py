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
``[--start, --end]``. Re-runs are safe.

Failures are logged, not fatal — the run continues. Per-ticker outcome
goes to ``logs/tiingo_bulk.log``.

Usage
-----

    .venv/bin/python scripts/tiingo_bulk_download.py \\
        --bucket spx500 \\
        --start 2014-01-01 --end 2026-04-14

    .venv/bin/python scripts/tiingo_bulk_download.py \\
        --bucket all --resume
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
    "AGG", "TLT", "IEF", "LQD", "HYG",
    # Commodities / volatility
    "GLD", "SLV", "USO", "UNG", "VXX",
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
        "--start", type=date.fromisoformat, default=date(2014, 1, 1),
        help="First date to fetch (default 2014-01-01).",
    )
    ap.add_argument(
        "--end", type=date.fromisoformat, default=date.today(),
        help="Last date (default: today).",
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

    run_id = f"bulk_{args.bucket}_{datetime.now().strftime('%Y%m%d-%H%M')}"
    log.info("=== %s ===", run_id)
    log.info(
        "bucket=%s start=%s end=%s storage=%s throttle=%dms limit=%s",
        args.bucket, args.start, args.end, args.storage_root,
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
        "start": args.start.isoformat(),
        "end": args.end.isoformat(),
        "n_total": len(pairs),
        "n_skipped_cached": 0,
        "n_fetched": 0,
        "n_empty": 0,
        "n_errors": 0,
        "errors": [],
    }

    pbar = tqdm(pairs, desc=run_id, unit="tk")
    for ticker, asset_class in pbar:
        if storage.has(ticker, args.start, args.end):
            summary["n_skipped_cached"] += 1
            pbar.set_postfix({"last": f"{ticker} (cached)"})
            continue
        try:
            df = source.fetch(ticker, args.start, args.end, asset_class=asset_class)
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
