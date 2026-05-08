#!/usr/bin/env python3
"""Pull historical equity curves from testfol.io /api/backtest.

For each ticker, sends a single-asset 100% allocation backtest with
maximally-wide date range (1800 → 2100). The endpoint returns the
full historical equity curve from the synth's actual inception date.

Auth: Bearer JWT in `.testfolio_token` file (gitignored) or
`TESTFOLIO_TOKEN` env var. Token is a Supabase JWT; expires every few
hours — if the request returns 401, refresh by re-extracting from
DevTools and overwriting `.testfolio_token`.

Output: `data/testfolio/<ticker>.json` (one file per ticker). After
pulling, run `scripts/extract_testfolio_json.py` to merge into the
parquet cache that the loader reads.

Usage::

    python scripts/testfolio_pull.py BNDSIM IEFSIM VTSIM
    python scripts/testfolio_pull.py --refresh-cache BNDSIM      # also runs extract
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "https://testfol.io/api/backtest"
TOKEN_FILE = REPO_ROOT / ".testfolio_token"
OUT_DIR = REPO_ROOT / "data/testfolio"
EXTRACT_SCRIPT = REPO_ROOT / "scripts/extract_testfolio_json.py"


def get_token() -> str:
    token = os.environ.get("TESTFOLIO_TOKEN", "").strip()
    if token:
        return token
    if TOKEN_FILE.exists():
        token = TOKEN_FILE.read_text().strip()
        if token:
            return token
    sys.exit(
        "ERROR: no token. Set TESTFOLIO_TOKEN env var OR create "
        f"{TOKEN_FILE.relative_to(REPO_ROOT)} (gitignored).\n"
        "To get a fresh token: open testfol.io in browser, F12 → Network, "
        "trigger a backtest, copy the 'authorization: Bearer ...' header value."
    )


def build_payload(ticker: str) -> dict:
    return {
        "start_date": "1800-01-01",
        "end_date": "2100-01-01",
        "start_val": 10000,
        "adj_inflation": False,
        "cashflow": 0,
        "cashflow_freq": "Yearly",
        "cashflow_offset": 0,
        "match_first_portfolio_income_cashflows": False,
        "one_time_cashflows": [],
        "rolling_window": 60,
        "withdrawal_surface_include": False,
        "withdrawal_surface_projection": "NONE",
        "withdrawal_surface_projection_min_years": 10,
        "withdrawal_surface_start_years": 5,
        "withdrawal_surface_end_years": 50,
        "withdrawal_surface_step_years": 1,
        "backtests": [{
            "invest_dividends": True,
            "rebalance_freq": "Yearly",
            "rebalance_offset": 0,
            "allocation": {ticker: 100},
            "drag": 0,
            "absolute_dev": 0,
            "relative_dev": 0,
        }],
        "cashflow_legs": [],
    }


def pull(token: str, ticker: str) -> dict:
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(build_payload(ticker)).encode(),
        headers={
            "authorization": f"Bearer {token}",
            "content-type": "application/json",
            "User-Agent": "market-lab/testfolio_pull (https://github.com/...)",
            "Referer": "https://testfol.io/",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:500]
        raise RuntimeError(
            f"HTTP {e.code} {e.reason} for {ticker}: {body}"
        ) from e


def save(ticker: str, payload: dict) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{ticker.lower()}.json"
    out_path.write_text(json.dumps(payload))
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("tickers", nargs="+", help="testfol.io sim tickers (e.g. BNDSIM IEFSIM)")
    ap.add_argument("--sleep", type=float, default=0.5,
                    help="seconds between requests (default 0.5)")
    ap.add_argument("--refresh-cache", action="store_true",
                    help="run extract_testfolio_json.py after pulling")
    args = ap.parse_args()

    token = get_token()
    print(f"loaded token (length={len(token)} chars), pulling {len(args.tickers)} ticker(s)...")
    failed: list[str] = []
    for i, t in enumerate(args.tickers):
        if i > 0:
            time.sleep(args.sleep)
        ticker = t.upper()
        print(f"[{i+1}/{len(args.tickers)}] {ticker}...", end=" ", flush=True)
        try:
            data = pull(token, ticker)
            out = save(ticker, data)
            size_kb = out.stat().st_size // 1024
            n_bars = 0
            try:
                hist = data.get("charts", {}).get("history")
                if hist and isinstance(hist, list) and len(hist):
                    n_bars = len(hist[0]) if isinstance(hist[0], list) else 0
            except Exception:
                pass
            print(f"OK ({size_kb} KB, ~{n_bars} bars) → {out.relative_to(REPO_ROOT)}")
        except Exception as e:
            print(f"FAILED: {e}")
            failed.append(ticker)

    if failed:
        print(f"\nFailed tickers: {failed}")
        sys.exit(1)

    if args.refresh_cache:
        print("\nrefreshing parquet cache...")
        result = subprocess.run(
            ["uv", "run", "python", str(EXTRACT_SCRIPT)],
            cwd=REPO_ROOT, capture_output=True, text=True,
        )
        print(result.stdout[-2000:] if result.stdout else "")
        if result.returncode != 0:
            print(f"extract failed: {result.stderr[-1000:]}")
            sys.exit(result.returncode)


if __name__ == "__main__":
    main()
