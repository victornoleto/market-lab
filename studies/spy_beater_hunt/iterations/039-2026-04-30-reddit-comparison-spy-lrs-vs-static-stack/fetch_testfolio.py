#!/usr/bin/env python3
"""Fetch testfol.io results for the r/LETFs Reddit post (iter 039).

Aligned with REDDIT_POST.md: 7 buy-hold profiles (annual rebal) + 2 LRS
(daily, with IEF off-state) over 1986-2026.

Saves JSONs in testfolio_data/ (testfolio caps at 5 portfolios per /api/backtest call,
so the 7 buy-hold portfolios are split across 2 batches):
  - backtest_buyhold_a.json — first 5 buy-hold portfolios (Yearly rebal)
  - backtest_buyhold_b.json — remaining buy-hold portfolios (Yearly rebal)
  - tactical_lrs_sso.json   — SSO 200d-SMA LRS, off-state IEF
  - tactical_lrs_upro.json  — UPRO 200d-SMA LRS, off-state IEF

Auth: TESTFOLIO_TOKEN env var. Token expires ~1h after browser login.
Get fresh from: testfol.io DevTools -> Network -> /api/backtest -> Headers -> authorization
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
API_TACTICAL = "https://testfol.io/api/tactical"
SEARCH_URL = "https://testfol.io/api/search/SIM"

# Mirrors scripts/testfolio-portfolio MAPPINGS table verbatim.
# CASHX legs fund borrowed sleeves at the 3M T-Bill rate.
MAPPINGS: dict[str, list[tuple[str, float]]] = {
    "NTSX": [("SPYSIM", 0.90), ("IEFSIM", 0.60), ("CASHX", -0.50)],
    "RSST": [("SPYSIM", 1.00), ("KMLMSIM", 1.00), ("CASHX", -1.00)],
    "TMF":  [("TLTSIM?L=3&E=1.05", 1.0)],
    "UPRO": [("SPYSIM?L=3&E=0.91", 1.0)],
    "SSO":  [("SPYSIM?L=2&E=0.89", 1.0)],
}

# Aligned with REDDIT_POST.md (line 13-23 contenders table). 7 buy-hold + 2 LRS.
BUYHOLD_PORTFOLIOS = [
    {
        "slug": "spy_1x",
        "label": "SPY 1x buy-hold",
        "allocation_real": [(100, "SPY")],
        "rebalance_freq": "None",
    },
    {
        "slug": "popular_50_25_25",
        "label": "Popular: 50/25/25 SSO/GLD/ZROZ",
        "allocation_real": [(50, "SSO"), (25, "GLD"), (25, "ZROZ")],
        "rebalance_freq": "Yearly",
    },
    {
        "slug": "l1_sleeping_pills",
        "label": "Sleeping pills (L1 CEGB): 40/25/17.5/17.5 NTSX/GDE/KMLM/TLT",
        "allocation_real": [(40, "NTSX"), (25, "GDE"), (17.5, "KMLM"), (17.5, "TLT")],
        "rebalance_freq": "Yearly",
    },
    {
        "slug": "l2_bogleheads",
        "label": "Bogleheads: 67/11/11/11 NTSX/GLD/KMLM/ZROZ",
        "allocation_real": [(67, "NTSX"), (11, "GLD"), (11, "KMLM"), (11, "ZROZ")],
        "rebalance_freq": "Yearly",
    },
    {
        "slug": "b4_conservative",
        "label": "Conservative (B4 ZROZ): 25/25/25/25 NTSX/GDE/RSST/ZROZ",
        "allocation_real": [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (25, "ZROZ")],
        "rebalance_freq": "Yearly",
    },
    {
        "slug": "b2_balanced",
        "label": "Balanced (B2): 30/30/30/10 NTSX/GDE/RSST/TMF",
        "allocation_real": [(30, "NTSX"), (30, "GDE"), (30, "RSST"), (10, "TMF")],
        "rebalance_freq": "Yearly",
    },
    {
        "slug": "t1_aggressive",
        "label": "Aggressive (T1 gold-heavy): 20/35/25/20 NTSX/GDE/RSST/TMF",
        "allocation_real": [(20, "NTSX"), (35, "GDE"), (25, "RSST"), (20, "TMF")],
        "rebalance_freq": "Yearly",
    },
]


def fetch_sim_list() -> set[str]:
    req = urllib.request.Request(
        SEARCH_URL,
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) reddit-letf-post/1.0"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    return {d["ticker"] for d in data if d["ticker"].endswith("SIM")}


def expand(weight: float, ticker: str, sim_list: set[str]) -> list[tuple[str, float]]:
    """Resolve a real ETF ticker to (sim_token, weight) legs.

    Order: (1) direct *SIM (e.g. GDE -> GDESIM), (2) MAPPINGS decomposition,
    (3) raw SIM token.
    """
    sim = f"{ticker}SIM"
    if sim in sim_list:
        return [(sim, weight)]
    if ticker in MAPPINGS:
        return [(token, weight * w) for token, w in MAPPINGS[ticker]]
    if ticker in sim_list:
        return [(ticker, weight)]
    sys.exit(f"error: no SIM and no MAPPINGS entry for {ticker!r}")


def decompose(allocation_real: list[tuple[float, str]], sim_list: set[str]) -> dict[str, float]:
    agg: dict[str, float] = defaultdict(float)
    for pct, ticker in allocation_real:
        for token, w in expand(pct / 100.0, ticker.upper(), sim_list):
            agg[token] += w * 100.0
    return {k: round(v, 4) for k, v in agg.items() if abs(v) > 1e-6}


def build_backtest_payload(portfolios: list[dict]) -> dict:
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
                "rebalance_freq": p["rebalance_freq"],
                "rebalance_offset": 0,
                "allocation": p["allocation_sim"],
                "drag": 0,
                "absolute_dev": 0,
                "relative_dev": 0,
            }
            for p in portfolios
        ],
        "cashflow_legs": [],
    }


def build_tactical_payload(name: str, leveraged_ticker: str, drag_pct: float) -> dict:
    """SPY > 200d-SMA -> leveraged_ticker, else IEF (Gayed canonical defensive sleeve)."""
    return {
        "name": name,
        "start_date": "1987-12-31",
        "end_date": "",
        "start_val": 10000,
        "adj_inflation": False,
        "trading_cost": 0,
        "rolling_window": 60,
        "withdrawal_surface_include": False,
        "withdrawal_surface_projection": "NONE",
        "withdrawal_surface_projection_min_years": 10,
        "withdrawal_surface_start_years": 5,
        "withdrawal_surface_end_years": 50,
        "withdrawal_surface_step_years": 1,
        "signals": [
            {
                "name": "1",
                "indicator_1": {"type": "SMA", "ticker": "SPYSIM", "ticker_2": None,
                                "value": None, "lookback": 200, "delay": None},
                "comparison": "<",
                "indicator_2": {"type": "Price", "ticker": "SPYSIM", "ticker_2": None,
                                "value": None, "lookback": None, "delay": None},
                "tolerance": 2,
            }
        ],
        "derived_signals": [],
        "aggregate_derived_signals": [],
        "mode": "BACKTEST",
        "global_candidate_tickers": [],
        "include_efficient_frontier": False,
        "allocations": [
            _alloc_leg(f"Leveraged ({leveraged_ticker})", ["1"], leveraged_ticker, drag_pct),
            _alloc_leg("Defensive (IEF)", [], "IEFSIM", 0),
            _alloc_leg("SPY (benchmark)", [], "SPYSIM", 0.02),
        ],
        "trading_freq": "Daily",
        "trading_offset": 0,
        "cashflow_legs": [],
        "one_time_cashflows": [],
    }


def _alloc_leg(name: str, signals: list[str], ticker: str, drag: float) -> dict:
    return {
        "name": name,
        "signals": signals,
        "ops": [],
        "nots": [False] if signals else [],
        "kind": "FIXED",
        "tickers": [{"ticker": ticker, "percent": 100}],
        "rank_universe_tickers": [],
        "rank_pairs": [],
        "rank_metric": None,
        "rank_selection": "TOP",
        "rank_lookbacks": [],
        "rank_top_n": None,
        "rank_threshold_comparison": None,
        "rank_threshold_value": None,
        "rank_fallback_ticker": None,
        "rank_weighting": None,
        "rank_score_tilt": None,
        "rank_vol_lookback": None,
        "rank_rp_vol_lookback": None,
        "rank_rp_corr_lookback": None,
        "rank_freq": None,
        "rank_offset": None,
        "drag": drag,
        "candidate_tickers": [],
        "optimize_objective": None,
        "rebalance_freq": "Daily",
        "rebalance_offset": 0,
        "absolute_dev": 0,
        "relative_dev": 0,
    }


def post_with_retries(url: str, payload: dict, token: str, attempts: int = 3) -> dict:
    body = json.dumps(payload).encode("utf-8")
    last_err: Exception | None = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(
                url,
                data=body,
                method="POST",
                headers={
                    "accept": "*/*",
                    "authorization": f"Bearer {token}",
                    "content-type": "application/json",
                    "origin": "https://testfol.io",
                    "referer": "https://testfol.io/",
                    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) reddit-letf-post/1.0",
                },
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 401:
                sys.exit(
                    "fatal: TESTFOLIO_TOKEN is invalid or expired (401).\n"
                    "Get a fresh token from testfol.io:\n"
                    "  1. Open testfol.io in browser, log in.\n"
                    "  2. Open DevTools (F12) -> Network tab.\n"
                    "  3. Run any backtest on the site.\n"
                    "  4. Click /api/backtest request -> Headers -> Request Headers.\n"
                    "  5. Copy the value after 'authorization: Bearer ' (the JWT).\n"
                    "  6. Re-run: TESTFOLIO_TOKEN='<paste>' python fetch_testfolio.py"
                )
            if e.code == 429:
                print(f"warn: 429 rate-limited, sleeping 30s before retry {i+1}/{attempts}", file=sys.stderr)
                time.sleep(30)
                last_err = e
                continue
            if 500 <= e.code < 600:
                wait = 2 ** (i + 1)
                print(f"warn: {e.code} server error, sleeping {wait}s before retry {i+1}/{attempts}", file=sys.stderr)
                time.sleep(wait)
                last_err = e
                continue
            sys.exit(f"fatal: HTTP {e.code} from {url}: {e.read().decode('utf-8', errors='replace')}")
        except (urllib.error.URLError, TimeoutError) as e:
            wait = 2 ** (i + 1)
            print(f"warn: network error ({e}), sleeping {wait}s before retry {i+1}/{attempts}", file=sys.stderr)
            time.sleep(wait)
            last_err = e
    sys.exit(f"fatal: exhausted {attempts} retries for {url}: {last_err}")


def main() -> int:
    token = os.environ.get("TESTFOLIO_TOKEN", "").strip()
    if not token:
        sys.exit(
            "fatal: TESTFOLIO_TOKEN env var not set.\n"
            "Get token from testfol.io DevTools (Network -> /api/backtest -> "
            "Headers -> authorization: Bearer <JWT>) and re-run with:\n"
            "  TESTFOLIO_TOKEN='<JWT>' python fetch_testfolio.py"
        )

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Fetching SIM ticker list from testfol.io...", file=sys.stderr)
    sim_list = fetch_sim_list()
    print(f"  {len(sim_list)} SIM tickers available", file=sys.stderr)

    print("\nDecomposing buy-hold portfolios into SIM legs:", file=sys.stderr)
    for p in BUYHOLD_PORTFOLIOS:
        p["allocation_sim"] = decompose(p["allocation_real"], sim_list)
        legs = ", ".join(f"{w:+.2f} {t}"
                         for t, w in sorted(p["allocation_sim"].items(), key=lambda kv: -kv[1]))
        print(f"  [{p['slug']}] {legs}", file=sys.stderr)

    # testfolio caps at 5 portfolios per /api/backtest call; split into batches.
    MAX_PER_CALL = 5
    batches = [BUYHOLD_PORTFOLIOS[i:i + MAX_PER_CALL]
               for i in range(0, len(BUYHOLD_PORTFOLIOS), MAX_PER_CALL)]
    for letter, batch in zip("abcdef", batches):
        print(f"\nPOST {API_BACKTEST} batch '{letter}' with {len(batch)} backtests (Yearly rebal)...", file=sys.stderr)
        bh_response = post_with_retries(API_BACKTEST, build_backtest_payload(batch), token)
        out = DATA_DIR / f"backtest_buyhold_{letter}.json"
        out.write_text(json.dumps(
            {
                "portfolios": [
                    {"slug": p["slug"], "label": p["label"],
                     "allocation_real": p["allocation_real"],
                     "allocation_sim": p["allocation_sim"]}
                    for p in batch
                ],
                "response": bh_response,
            },
            indent=2,
        ))
        print(f"  saved {out} ({out.stat().st_size//1024} KB)", file=sys.stderr)

    print(f"\nPOST {API_TACTICAL} for SSO 200SMA LRS (off-state IEF)...", file=sys.stderr)
    sso_response = post_with_retries(
        API_TACTICAL,
        build_tactical_payload("SPY 200d-SMA | Lev 2x | IEF off-state", "SPYSIM?L=2", drag_pct=0.87),
        token,
    )
    out_sso = DATA_DIR / "tactical_lrs_sso.json"
    out_sso.write_text(json.dumps(sso_response, indent=2))
    print(f"  saved {out_sso} ({out_sso.stat().st_size//1024} KB)", file=sys.stderr)

    print(f"\nPOST {API_TACTICAL} for UPRO 200SMA LRS (off-state IEF)...", file=sys.stderr)
    upro_response = post_with_retries(
        API_TACTICAL,
        build_tactical_payload("SPY 200d-SMA | Lev 3x | IEF off-state", "SPYSIM?L=3", drag_pct=0.87),
        token,
    )
    out_upro = DATA_DIR / "tactical_lrs_upro.json"
    out_upro.write_text(json.dumps(upro_response, indent=2))
    print(f"  saved {out_upro} ({out_upro.stat().st_size//1024} KB)", file=sys.stderr)

    print("\nAll 3 JSONs saved. Run plot_post.py to generate PNGs.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
