#!/usr/bin/env python3
"""Fetch testfol.io for each sleeve as a 100% standalone portfolio.

Sleeves: NTSX, GDE, RSST, ZROZ, TMF, KMLM, TLT.
Used as inputs to the walk-forward weight-drift optimizer (G8 gate).

Per laurenthu critique: re-optimize B4/B2/T1 weights on rolling 5y windows;
if optimal weights drift > ±5pp from static, edge is window-specific (curve-fit).

ERs applied via `drag` per sleeve.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "testfolio_data"

API_BACKTEST = "https://testfol.io/api/backtest"
SEARCH_URL = "https://testfol.io/api/search/SIM"

ER = {
    "NTSX": 0.20, "GDE": 0.20, "RSST": 0.99, "ZROZ": 0.15,
    "TMF": 1.05, "KMLM": 0.92, "TLT": 0.15,
}

MAPPINGS = {
    "NTSX": [("SPYSIM", 0.90), ("IEFSIM", 0.60), ("CASHX", -0.50)],
    "RSST": [("SPYSIM", 1.00), ("KMLMSIM", 1.00), ("CASHX", -1.00)],
    "TMF":  [("TLTSIM?L=3&E=1.05", 1.0)],
}

SLEEVES = ["NTSX", "GDE", "RSST", "ZROZ", "TMF", "KMLM", "TLT"]


def fetch_sim_list() -> set[str]:
    req = urllib.request.Request(SEARCH_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return {d["ticker"] for d in json.loads(resp.read()) if d["ticker"].endswith("SIM")}


def expand(weight: float, ticker: str, sim_list: set[str]) -> list[tuple[str, float]]:
    sim = f"{ticker}SIM"
    if sim in sim_list:
        return [(sim, weight)]
    if ticker in MAPPINGS:
        return [(t, weight * w) for t, w in MAPPINGS[ticker]]
    sys.exit(f"error: no expansion for {ticker!r}")


def decompose(allocation_real: list[tuple[float, str]], sim_list: set[str]) -> dict[str, float]:
    agg: dict[str, float] = defaultdict(float)
    for pct, ticker in allocation_real:
        for token, w in expand(pct / 100.0, ticker.upper(), sim_list):
            agg[token] += w * 100.0
    return {k: round(v, 4) for k, v in agg.items() if abs(v) > 1e-6}


def build_payload(portfolios: list[dict]) -> dict:
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
        "backtests": [
            {
                "invest_dividends": True,
                "rebalance_freq": "None",  # single-sleeve = no rebal
                "rebalance_offset": 0,
                "allocation": p["allocation_sim"],
                "drag": p["drag_pct"],
                "absolute_dev": 0,
                "relative_dev": 0,
            }
            for p in portfolios
        ],
        "cashflow_legs": [],
    }


def post_with_retries(url: str, payload: dict, token: str, attempts: int = 3) -> dict:
    body = json.dumps(payload).encode("utf-8")
    last_err = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, data=body, method="POST",
                headers={"accept": "*/*", "authorization": f"Bearer {token}",
                         "content-type": "application/json", "origin": "https://testfol.io",
                         "referer": "https://testfol.io/", "user-agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 401:
                sys.exit("fatal: TESTFOLIO_TOKEN expired (401)")
            if e.code == 429:
                print(f"warn: 429, sleeping 30s ({i+1}/{attempts})", file=sys.stderr)
                time.sleep(30)
                last_err = e
                continue
            if 500 <= e.code < 600:
                wait = 2 ** (i + 1)
                time.sleep(wait)
                last_err = e
                continue
            sys.exit(f"fatal: HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:500]}")
        except (urllib.error.URLError, TimeoutError) as e:
            wait = 2 ** (i + 1)
            time.sleep(wait)
            last_err = e
    sys.exit(f"fatal: exhausted retries: {last_err}")


def main() -> int:
    token = os.environ.get("TESTFOLIO_TOKEN", "").strip()
    if not token:
        sys.exit("fatal: TESTFOLIO_TOKEN env var not set")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    sim_list = fetch_sim_list()

    portfolios = []
    for sleeve in SLEEVES:
        alloc_sim = decompose([(100, sleeve)], sim_list)
        portfolios.append({
            "slug": sleeve.lower(),
            "label": f"{sleeve} 100%",
            "allocation_sim": alloc_sim,
            "drag_pct": ER.get(sleeve, 0.0),
        })

    print("Sleeves:")
    for p in portfolios:
        legs = ", ".join(f"{w:+.2f} {t}" for t, w in p["allocation_sim"].items())
        print(f"  [{p['slug']:<6s}] drag={p['drag_pct']:.2f}% [{legs}]")

    # 5 per batch
    MAX = 5
    batches = [portfolios[i:i + MAX] for i in range(0, len(portfolios), MAX)]
    for letter, batch in zip("abcdef", batches):
        print(f"\nPOST batch {letter}: {len(batch)} sleeves")
        resp = post_with_retries(API_BACKTEST, build_payload(batch), token)
        out = DATA_DIR / f"sleeves_{letter}.json"
        out.write_text(json.dumps({
            "portfolios": [{"slug": p["slug"], "drag_pct": p["drag_pct"]} for p in batch],
            "response": resp,
        }, indent=2))
        print(f"  saved {out} ({out.stat().st_size//1024} KB)")
        for p, s in zip(batch, resp["stats"]):
            print(f"    {p['slug']:<6s} CAGR={s['cagr']:.2f}% MDD={s['max_drawdown']:.2f}% "
                  f"Sharpe={s['sharpe']:.4f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
