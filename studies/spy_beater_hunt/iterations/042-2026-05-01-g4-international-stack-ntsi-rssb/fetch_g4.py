#!/usr/bin/env python3
"""Fetch testfol.io results for iter 042 — G4 international stack.

Per Reddit Post 1 feedback (u/Grouchy_Release_2321 + u/perky_python):
  Replace SPY-only base with global / international ETFs to test if Sharpe
  survives without US-equity bias.

5 variants:
  G4a (NTSD swap)    — 25 NTSD / 25 GDE / 25 RSST / 25 ZROZ (B4 with US→Intl)
  G4b (RSSB-heavy)   — 50 RSSB / 25 GDE / 25 KMLM (no duration sleeve)
  G4c (mixed US/Intl)— 12.5 NTSX / 12.5 NTSD / 25 GDE / 25 RSST / 25 ZROZ
  G4d (4-sleeve)     — 25 RSSB / 25 GDE / 25 ZROZ / 25 KMLM
  G4e (full intl)    — 50 NTSD / 25 GDE / 25 KMLM (no US large-cap, no duration)

NTSDSIM = WisdomTree Efficient Core International Developed (90/60).
RSSBSIM = Return Stacked Global Stocks & Bonds (100/100).
Both directly available as testfol.io SIMs.

Top-level rebal Monthly. ERs applied per portfolio via `drag`.
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

EXPENSE_RATIOS: dict[str, float] = {
    "SPY":  0.0945,
    "NTSX": 0.20,
    "NTSD": 0.20,    # WisdomTree Efficient Core International Developed
    "GDE":  0.20,
    "RSST": 0.99,
    "RSSB": 0.69,    # Return Stacked Global Stocks & Bonds (net ER per issuer page)
    "KMLM": 0.92,
    "GLD":  0.40,
    "TLT":  0.15,
    "ZROZ": 0.15,
    "IEF":  0.15,
}

# RSST decomposition still needed (KMLMSIM/SPYSIM legs).
# NTSD/RSSB available directly as SIMs — no decomposition.
MAPPINGS: dict[str, list[tuple[str, float]]] = {
    "NTSX": [("SPYSIM", 0.90), ("IEFSIM", 0.60), ("CASHX", -0.50)],
    "RSST": [("SPYSIM", 1.00), ("KMLMSIM", 1.00), ("CASHX", -1.00)],
}


def compute_drag(allocation: list[tuple[float, str]]) -> float:
    drag = 0.0
    for pct, ticker in allocation:
        er = EXPENSE_RATIOS.get(ticker.upper(), 0.0)
        drag += (pct / 100.0) * er
    return round(drag, 4)


PORTFOLIOS = [
    {
        "slug": "g4a_ntsd_swap",
        "label": "G4a — 25 NTSD / 25 GDE / 25 RSST / 25 ZROZ (B4 US→Intl)",
        "allocation_real": [(25, "NTSD"), (25, "GDE"), (25, "RSST"), (25, "ZROZ")],
    },
    {
        "slug": "g4b_rssb_heavy",
        "label": "G4b — 50 RSSB / 25 GDE / 25 KMLM (no duration)",
        "allocation_real": [(50, "RSSB"), (25, "GDE"), (25, "KMLM")],
    },
    {
        "slug": "g4c_mixed_us_intl",
        "label": "G4c — 12.5 NTSX / 12.5 NTSD / 25 GDE / 25 RSST / 25 ZROZ",
        "allocation_real": [(12.5, "NTSX"), (12.5, "NTSD"), (25, "GDE"), (25, "RSST"), (25, "ZROZ")],
    },
    {
        "slug": "g4d_global_4sleeve",
        "label": "G4d — 25 RSSB / 25 GDE / 25 ZROZ / 25 KMLM",
        "allocation_real": [(25, "RSSB"), (25, "GDE"), (25, "ZROZ"), (25, "KMLM")],
    },
    {
        "slug": "g4e_full_intl",
        "label": "G4e — 50 NTSD / 25 GDE / 25 KMLM (no US, no duration)",
        "allocation_real": [(50, "NTSD"), (25, "GDE"), (25, "KMLM")],
    },
]


def fetch_sim_list() -> set[str]:
    req = urllib.request.Request(SEARCH_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    return {d["ticker"] for d in data if d["ticker"].endswith("SIM")}


def expand(weight: float, ticker: str, sim_list: set[str]) -> list[tuple[str, float]]:
    sim = f"{ticker}SIM"
    if sim in sim_list:
        return [(sim, weight)]
    if ticker in MAPPINGS:
        return [(t, weight * w) for t, w in MAPPINGS[ticker]]
    if ticker in sim_list:
        return [(ticker, weight)]
    sys.exit(f"error: no SIM nor MAPPINGS for {ticker!r}")


def decompose(allocation: list[tuple[float, str]], sim_list: set[str]) -> dict[str, float]:
    agg: dict[str, float] = defaultdict(float)
    for pct, ticker in allocation:
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
                "rebalance_freq": "Monthly",
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
            req = urllib.request.Request(
                url, data=body, method="POST",
                headers={
                    "accept": "*/*",
                    "authorization": f"Bearer {token}",
                    "content-type": "application/json",
                    "origin": "https://testfol.io",
                    "referer": "https://testfol.io/",
                    "user-agent": "Mozilla/5.0",
                },
            )
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
                print(f"warn: {e.code}, sleeping {wait}s", file=sys.stderr)
                time.sleep(wait)
                last_err = e
                continue
            sys.exit(f"fatal: HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:500]}")
        except (urllib.error.URLError, TimeoutError) as e:
            wait = 2 ** (i + 1)
            print(f"warn: net error ({e}), sleeping {wait}s", file=sys.stderr)
            time.sleep(wait)
            last_err = e
    sys.exit(f"fatal: exhausted retries: {last_err}")


def main() -> int:
    token = os.environ.get("TESTFOLIO_TOKEN", "").strip()
    if not token:
        sys.exit("fatal: TESTFOLIO_TOKEN env var not set")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    sim_list = fetch_sim_list()
    print(f"{len(sim_list)} SIMs available")

    print("\nDecomposing G4 variants:")
    for p in PORTFOLIOS:
        p["allocation_sim"] = decompose(p["allocation_real"], sim_list)
        p["drag_pct"] = compute_drag(p["allocation_real"])
        legs = ", ".join(f"{w:+.2f} {t}"
                         for t, w in sorted(p["allocation_sim"].items(), key=lambda kv: -kv[1]))
        print(f"  [{p['slug']}] drag={p['drag_pct']:.4f}% [{legs}]")

    print("\nPOST batch (5 portfolios, Monthly rebal + ERs)...")
    resp = post_with_retries(API_BACKTEST, build_payload(PORTFOLIOS), token)
    out = DATA_DIR / "backtest_g4.json"
    out.write_text(json.dumps(
        {
            "portfolios": [
                {"slug": p["slug"], "label": p["label"],
                 "allocation_real": p["allocation_real"],
                 "allocation_sim": p["allocation_sim"],
                 "drag_pct": p["drag_pct"]}
                for p in PORTFOLIOS
            ],
            "response": resp,
        },
        indent=2,
    ))
    print(f"saved {out} ({out.stat().st_size//1024} KB)")

    print("\nQuick stats:")
    for p, s in zip(PORTFOLIOS, resp["stats"]):
        print(f"  [{p['slug']:<25s}] CAGR={s['cagr']:.2f}% MDD={s['max_drawdown']:.2f}% "
              f"Sharpe={s['sharpe']:.4f}")

    print(f"\nstart_date={resp.get('start_date')} end_date={resp.get('end_date')}")
    print("Run analyze_g4.py to compare with iter 040 baselines.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
