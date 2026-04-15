#!/usr/bin/env python3
"""Tiingo connectivity + survivorship-coverage smoke test.

Confirms three things before we build a full ``TiingoSource``:

1. **Auth works** — ``Authorization: Token <key>`` header against the
   EOD endpoint returns 200 OK with a non-empty body.
2. **Active ticker fetch is sane** — ``KR`` (Kroger, active) returns a
   reasonable OHLCV frame for a known window.
3. **Survivorship-free is real** — ``ANDV`` (Andeavor, merged into MPC
   on 2018-10-03 and removed from SPX) returns historical OHLCV up to
   the delisting date. yfinance returns empty for ANDV; if Tiingo
   serves it, the paid-data ablation is technically feasible.

Reads ``TIINGO_API_KEY`` from environment (loaded from .env via
pydantic-settings or a manual ``os.environ`` setup). Does not write
anything to disk; run is read-only.

Usage::

    .venv/bin/python scripts/tiingo_smoke.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests


_BASE = "https://api.tiingo.com/tiingo/daily"


def _load_env_key() -> str:
    """Read TIINGO_API_KEY from environment, falling back to .env parsing."""
    key = os.environ.get("TIINGO_API_KEY")
    if key:
        return key
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            name, _, value = line.partition("=")
            if name.strip() == "TIINGO_API_KEY":
                return value.strip().strip('"').strip("'")
    return ""


def _fetch_prices(
    ticker: str,
    start: str,
    end: str,
    token: str,
) -> tuple[int, list[dict] | str]:
    """Hit /tiingo/daily/{ticker}/prices and return (status_code, body)."""
    url = f"{_BASE}/{ticker}/prices"
    params = {"startDate": start, "endDate": end}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}",
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
    except requests.RequestException as exc:
        return -1, f"request error: {exc}"
    body: list[dict] | str
    try:
        body = resp.json()
    except json.JSONDecodeError:
        body = resp.text
    return resp.status_code, body


def _summarize(body: list[dict] | str) -> str:
    if isinstance(body, str):
        return f"non-JSON body ({len(body)} chars): {body[:120]}"
    if not body:
        return "EMPTY list"
    first, last = body[0], body[-1]
    keys = sorted(first.keys()) if isinstance(first, dict) else []
    return (
        f"{len(body)} rows | "
        f"first {first.get('date', '?')[:10]} close={first.get('close', '?')} | "
        f"last {last.get('date', '?')[:10]} close={last.get('close', '?')} | "
        f"keys={keys}"
    )


def main() -> int:
    token = _load_env_key()
    if not token:
        print("ERROR: TIINGO_API_KEY not set (env or .env file).", file=sys.stderr)
        return 1
    print(f"Token loaded: {token[:6]}…{token[-4:]} (len {len(token)})")
    print()

    # 3 sanity probes — index, active, delisted.
    cases = [
        ("SPY", "2023-12-01", "2023-12-29", "active US ETF on SPX (auth/format)"),
        ("KR",  "2023-12-01", "2023-12-29", "active US stock (Kroger)"),
        ("ANDV", "2018-08-01", "2018-10-31",
         "delisted 2018-10-03 (Andeavor → MPC merger)"),
    ]
    for ticker, start, end, note in cases:
        print(f"--- {ticker} [{start} → {end}]  ({note})")
        status, body = _fetch_prices(ticker, start, end, token)
        print(f"  HTTP {status}")
        if status == 200:
            print(f"  {_summarize(body)}")
        else:
            preview = body if isinstance(body, str) else json.dumps(body)[:200]
            print(f"  body: {preview}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
