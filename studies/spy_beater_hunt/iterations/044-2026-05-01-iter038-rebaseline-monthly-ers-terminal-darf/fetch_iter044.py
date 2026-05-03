#!/usr/bin/env python3
"""Iter 044 — re-baseline iter 038 sweep with consistent methodology.

User feedback (2026-05-01): "use Monthly rebal in all contexts. Tax = 1 DARF/year
on net profit (gains offset by losses). For lazy-rebal-via-aportes-only investors
(no selling during year), realized gains = 0 → DARF deferred to terminal."

This iter re-runs all 14 configs from iter 038's sweep through testfol.io with:
  - Top-level rebal: Monthly (consistent with iter 040/041/042)
  - ERs: explicit via `drag` (NTSX 0.20%, GDE 0.20%, RSST 0.99%, KMLM 0.92%, etc.)
  - Tax model applied post-fetch in analyze.py: lazy-rebal terminal DARF
    (defer to end of period, 15% on cumulative profit)

Output is the canonical unified ranking that supersedes both iter 038 (Yearly +
no ER + post-tax) and iter 040 (Monthly + ERs + pre-tax) tables.
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

EXPENSE_RATIOS = {
    "SPY":  0.0945,
    "NTSX": 0.20,
    "GDE":  0.20,
    "RSST": 0.99,
    "RSSB": 0.69,
    "KMLM": 0.92,
    "DBMF": 0.85,
    "GLD":  0.40,
    "TLT":  0.15,
    "ZROZ": 0.15,
    "IEF":  0.15,
}

ER_BAKED_IN_SIM = {"SSO", "UPRO", "TMF"}

MAPPINGS = {
    "NTSX": [("SPYSIM", 0.90), ("IEFSIM", 0.60), ("CASHX", -0.50)],
    "RSST": [("SPYSIM", 1.00), ("KMLMSIM", 1.00), ("CASHX", -1.00)],
    "TMF":  [("TLTSIM?L=3&E=1.05", 1.0)],
}


# All 14 configs from iter 038 verbatim
PORTFOLIOS = [
    {"slug": "B1_user_baseline_25tmf", "label": "B1 user baseline (25/25/25/25 NTSX/GDE/RSST/TMF)",
     "allocation_real": [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (25, "TMF")]},
    {"slug": "B2_tmf10_balanced", "label": "B2 TMF10 balanced (30/30/30/10 NTSX/GDE/RSST/TMF)",
     "allocation_real": [(30, "NTSX"), (30, "GDE"), (30, "RSST"), (10, "TMF")]},
    {"slug": "B3_tlt_instead_of_tmf", "label": "B3 TLT instead of TMF (25/25/25/25 NTSX/GDE/RSST/TLT)",
     "allocation_real": [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (25, "TLT")]},
    {"slug": "B4_zroz_instead_of_tmf", "label": "B4 ZROZ instead of TMF (25/25/25/25 NTSX/GDE/RSST/ZROZ)",
     "allocation_real": [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (25, "ZROZ")]},
    {"slug": "B5_no_duration", "label": "B5 no duration (35/35/30 NTSX/GDE/RSST)",
     "allocation_real": [(35, "NTSX"), (35, "GDE"), (30, "RSST")]},
    {"slug": "M1_kmlm_no_rsst", "label": "M1 KMLM no RSST (25/25/25/25 NTSX/GDE/KMLM/TMF)",
     "allocation_real": [(25, "NTSX"), (25, "GDE"), (25, "KMLM"), (25, "TMF")]},
    {"slug": "M2_dbmf_no_rsst", "label": "M2 DBMF no RSST (25/25/25/25 NTSX/GDE/DBMF/TMF)",
     "allocation_real": [(25, "NTSX"), (25, "GDE"), (25, "DBMF"), (25, "TMF")]},
    {"slug": "M3_kmlm_dbmf_blend", "label": "M3 KMLM+DBMF blend (25/25/12.5/12.5/25 NTSX/GDE/KMLM/DBMF/TMF)",
     "allocation_real": [(25, "NTSX"), (25, "GDE"), (12.5, "KMLM"), (12.5, "DBMF"), (25, "TMF")]},
    {"slug": "M4_rsst_kmlm_blend", "label": "M4 RSST+KMLM blend (25/25/12.5/12.5/25 NTSX/GDE/RSST/KMLM/TMF)",
     "allocation_real": [(25, "NTSX"), (25, "GDE"), (12.5, "RSST"), (12.5, "KMLM"), (25, "TMF")]},
    {"slug": "L1_cegb_proxy", "label": "L1 CEGB proxy (40/25/17.5/17.5 NTSX/GDE/KMLM/TLT)",
     "allocation_real": [(40, "NTSX"), (25, "GDE"), (17.5, "KMLM"), (17.5, "TLT")]},
    {"slug": "L2_bogleheads_67ntsx", "label": "L2 Bogleheads (67/11/11/11 NTSX/GLD/KMLM/ZROZ)",
     "allocation_real": [(67, "NTSX"), (11, "GLD"), (11, "KMLM"), (11, "ZROZ")]},
    {"slug": "T1_gold_heavy", "label": "T1 gold-heavy (20/35/25/20 NTSX/GDE/RSST/TMF)",
     "allocation_real": [(20, "NTSX"), (35, "GDE"), (25, "RSST"), (20, "TMF")]},
    {"slug": "T2_equity_heavy", "label": "T2 equity-heavy (35/25/25/15 NTSX/GDE/RSST/TMF)",
     "allocation_real": [(35, "NTSX"), (25, "GDE"), (25, "RSST"), (15, "TMF")]},
    {"slug": "T3_rssb_global", "label": "T3 RSSB global (25/25/25/25 RSSB/GDE/RSST/TMF)",
     "allocation_real": [(25, "RSSB"), (25, "GDE"), (25, "RSST"), (25, "TMF")]},
]


def compute_drag(allocation):
    drag = 0.0
    for pct, ticker in allocation:
        t = ticker.upper()
        if t in ER_BAKED_IN_SIM:
            continue
        er = EXPENSE_RATIOS.get(t, 0.0)
        drag += (pct / 100.0) * er
    return round(drag, 4)


def fetch_sim_list():
    req = urllib.request.Request(SEARCH_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return {d["ticker"] for d in json.loads(resp.read()) if d["ticker"].endswith("SIM")}


def expand(weight, ticker, sim_list):
    sim = f"{ticker}SIM"
    if sim in sim_list:
        return [(sim, weight)]
    if ticker in MAPPINGS:
        return [(t, weight * w) for t, w in MAPPINGS[ticker]]
    if ticker in sim_list:
        return [(ticker, weight)]
    sys.exit(f"error: no expansion for {ticker!r}")


def decompose(allocation, sim_list):
    agg = defaultdict(float)
    for pct, ticker in allocation:
        for token, w in expand(pct / 100.0, ticker.upper(), sim_list):
            agg[token] += w * 100.0
    return {k: round(v, 4) for k, v in agg.items() if abs(v) > 1e-6}


def build_payload(portfolios):
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


def post_with_retries(url, payload, token, attempts=3):
    body = json.dumps(payload).encode("utf-8")
    last_err = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, data=body, method="POST", headers={
                "accept": "*/*",
                "authorization": f"Bearer {token}",
                "content-type": "application/json",
                "origin": "https://testfol.io",
                "referer": "https://testfol.io/",
                "user-agent": "Mozilla/5.0",
            })
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


def main():
    token = os.environ.get("TESTFOLIO_TOKEN", "").strip()
    if not token:
        sys.exit("fatal: TESTFOLIO_TOKEN env var not set")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    sim_list = fetch_sim_list()
    print(f"{len(sim_list)} SIMs available")

    print("\nDecomposing 14 configs:")
    for p in PORTFOLIOS:
        p["allocation_sim"] = decompose(p["allocation_real"], sim_list)
        p["drag_pct"] = compute_drag(p["allocation_real"])
        legs = ", ".join(f"{w:+.2f} {t}" for t, w in sorted(p["allocation_sim"].items(), key=lambda kv: -kv[1]))
        print(f"  [{p['slug']:<25s}] drag={p['drag_pct']:.4f}% [{legs}]")

    # 5 per batch (testfolio cap), 14 configs → 3 batches of 5+5+4
    MAX = 5
    batches = [PORTFOLIOS[i:i+MAX] for i in range(0, len(PORTFOLIOS), MAX)]
    for letter, batch in zip("abc", batches):
        print(f"\nPOST batch '{letter}' ({len(batch)} configs)...")
        resp = post_with_retries(API_BACKTEST, build_payload(batch), token)
        out = DATA_DIR / f"backtest_{letter}.json"
        out.write_text(json.dumps({
            "portfolios": [{"slug": p["slug"], "label": p["label"],
                          "allocation_real": p["allocation_real"],
                          "allocation_sim": p["allocation_sim"],
                          "drag_pct": p["drag_pct"]} for p in batch],
            "response": resp,
        }, indent=2))
        print(f"  saved {out} ({out.stat().st_size//1024} KB)")
        for p, s in zip(batch, resp["stats"]):
            print(f"    {p['slug']:<25s} CAGR={s['cagr']:.2f}% MDD={s['max_drawdown']:.2f}% Sharpe={s['sharpe']:.4f}")

    print("\nFetch complete. Run analyze_iter044.py to apply tax model + build unified ranking.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
