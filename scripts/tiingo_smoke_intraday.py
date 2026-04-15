#!/usr/bin/env python3
"""Tiingo intraday (1-hour) retention probe — SMOKE #1 DESIGN GATE.

This is the empirical gate described in `docs/superpowers/specs/
2026-04-15-tiingo-service-lazy-cache-design.md §6.1 passo 1 + §6.2`.
Rodar ANTES de qualquer refactor para determinar se o paradigma
lazy-cache reativo é viável para a subscrição Tiingo atual.

Probes:
  - SPY     via /iex/SPY/prices          (equity IEX feed)
  - btcusd  via /tiingo/crypto/prices    (crypto)
  - eurusd  via /tiingo/fx/eurusd/prices (forex)

Para cada ticker, pede `startDate = today - 5 anos`, `resampleFreq=1hour`
e mede retention real retornada pela API (bars, first_dt, last_dt, days).

Veredito por threshold do spec §6.2 (recalibrado v3):
  - ≥ 180 dias (6 meses) em todos 3  → PROCEED (Cenário A)
  - 90-180 dias                      → ESCALATE (cointegration pairs deferred)
  - < 90 dias                        → BLOCK (Cenário B, re-brainstorm)

Reads TIINGO_API_KEY from environment or .env. Does not write to disk
exceto log em logs/tiingo.log (append-only, padrão do projeto).

Usage::

    .venv/bin/python scripts/tiingo_smoke_intraday.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import requests


_BASE = "https://api.tiingo.com"


def _load_env_key() -> str:
    key = os.environ.get("TIINGO_API_KEY")
    if key:
        return key
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, _, value = line.partition("=")
            if name.strip() == "TIINGO_API_KEY":
                return value.strip().strip('"').strip("'")
    return ""


def _log(msg: str) -> None:
    stamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{stamp}] tiingo-smoke-intraday {msg}\n"
    log_path = Path(__file__).resolve().parents[1] / "logs" / "tiingo.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line)


def _probe_equity_iex(
    ticker: str, start: str, end: str, token: str
) -> tuple[int, list[dict] | str]:
    url = f"{_BASE}/iex/{ticker}/prices"
    params = {
        "startDate": start,
        "endDate": end,
        "resampleFreq": "1hour",
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}",
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=30)
    except requests.RequestException as exc:
        return -1, f"request error: {exc}"
    try:
        body = resp.json()
    except json.JSONDecodeError:
        body = resp.text
    return resp.status_code, body


def _probe_crypto(
    ticker: str, start: str, end: str, token: str
) -> tuple[int, list[dict] | str]:
    url = f"{_BASE}/tiingo/crypto/prices"
    params = {
        "tickers": ticker,
        "startDate": start,
        "endDate": end,
        "resampleFreq": "1hour",
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}",
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=30)
    except requests.RequestException as exc:
        return -1, f"request error: {exc}"
    try:
        body = resp.json()
    except json.JSONDecodeError:
        body = resp.text
    # Crypto wraps: [{ticker, baseCurrency, ..., priceData: [...]}]
    if isinstance(body, list) and body and isinstance(body[0], dict) and "priceData" in body[0]:
        return resp.status_code, body[0]["priceData"]
    return resp.status_code, body


def _probe_forex(
    ticker: str, start: str, end: str, token: str
) -> tuple[int, list[dict] | str]:
    url = f"{_BASE}/tiingo/fx/{ticker}/prices"
    params = {
        "startDate": start,
        "endDate": end,
        "resampleFreq": "1hour",
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}",
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=30)
    except requests.RequestException as exc:
        return -1, f"request error: {exc}"
    try:
        body = resp.json()
    except json.JSONDecodeError:
        body = resp.text
    return resp.status_code, body


def _measure_retention(body: Any) -> dict[str, Any] | None:
    """Extract retention stats from a Tiingo response body."""
    if not isinstance(body, list) or not body:
        return None
    first = body[0]
    last = body[-1]
    if not isinstance(first, dict) or not isinstance(last, dict):
        return None
    first_dt_raw = first.get("date") or first.get("timestamp")
    last_dt_raw = last.get("date") or last.get("timestamp")
    if not first_dt_raw or not last_dt_raw:
        return None
    # Tiingo returns ISO 8601 with Z suffix or +00:00
    first_dt = datetime.fromisoformat(first_dt_raw.replace("Z", "+00:00"))
    last_dt = datetime.fromisoformat(last_dt_raw.replace("Z", "+00:00"))
    span = last_dt - first_dt
    return {
        "bars": len(body),
        "first_dt": first_dt.isoformat(),
        "last_dt": last_dt.isoformat(),
        "days": span.days,
        "first_keys": sorted(first.keys()),
    }


def _classify(days: int) -> str:
    if days >= 180:
        return "PROCEED (Cenário A)"
    if days >= 90:
        return "ESCALATE (cointegration pairs deferred para v2/v3)"
    return "BLOCK (Cenário B — re-brainstorm scheduled daily-append)"


def main() -> int:
    token = _load_env_key()
    if not token:
        print("ERROR: TIINGO_API_KEY not set (env or .env file).", file=sys.stderr)
        return 1
    print(f"Token loaded: {token[:6]}…{token[-4:]} (len {len(token)})")
    _log(f"START token_len={len(token)}")

    today = date.today()
    five_years_ago = today - timedelta(days=5 * 365)
    start_iso = five_years_ago.isoformat()
    end_iso = today.isoformat()
    print(f"Window: {start_iso} → {end_iso} (5 anos de pedido)")
    print(f"resampleFreq: 1hour")
    print()

    cases = [
        ("SPY",     "equity", _probe_equity_iex),
        ("btcusd",  "crypto", _probe_crypto),
        ("eurusd",  "forex",  _probe_forex),
    ]

    results: dict[str, dict[str, Any] | None] = {}
    for ticker, asset_class, probe in cases:
        print(f"--- {ticker} ({asset_class}) via {probe.__name__}")
        status, body = probe(ticker, start_iso, end_iso, token)
        print(f"  HTTP {status}")
        if status != 200:
            preview = body if isinstance(body, str) else json.dumps(body)[:300]
            print(f"  body: {preview}")
            _log(f"{ticker} HTTP={status} FAILED body={preview[:200]}")
            results[ticker] = None
            print()
            continue
        stats = _measure_retention(body)
        if stats is None:
            print(f"  WARNING: empty or malformed body")
            _log(f"{ticker} HTTP=200 but empty/malformed response")
            results[ticker] = None
            print()
            continue
        print(f"  bars={stats['bars']} | first={stats['first_dt']} | last={stats['last_dt']}")
        print(f"  retention={stats['days']} days")
        print(f"  keys={stats['first_keys']}")
        _log(
            f"{ticker} bars={stats['bars']} "
            f"first={stats['first_dt']} last={stats['last_dt']} "
            f"days={stats['days']}"
        )
        results[ticker] = stats
        print()

    # -- Verdict consolidado --
    print("=" * 60)
    print("VEREDITO AGREGADO (spec §6.2 v3 threshold)")
    print("=" * 60)
    all_days: list[int] = []
    for ticker, stats in results.items():
        if stats is None:
            print(f"  {ticker:8} retention=??? (probe falhou — trate como BLOCK)")
            all_days.append(0)
            continue
        days = stats["days"]
        print(f"  {ticker:8} retention={days:4}d → {_classify(days)}")
        all_days.append(days)

    min_days = min(all_days) if all_days else 0
    print()
    print(f"Pior caso entre os 3 tickers: {min_days} dias")
    verdict = _classify(min_days)
    print(f"VEREDITO FINAL: {verdict}")
    _log(f"VERDICT min_days={min_days} {verdict}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
