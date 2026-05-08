#!/usr/bin/env python3
"""Fetch testfol.io results for iter 041 — G3 NDX regime-gate.

Per Reddit Post 1 feedback (u/Fun-Sundae4060, u/no_simpsons):
  TQQQ + multi-asset above 200d SMA(QQQ) → QQQ + multi-asset below.

5 variants tested:
  G3a (funsundae)   — TQQQ/KMLM/GLD 33/33/33 bull → QQQ/KMLM/GLD bear
  G3b (heavy_ndx)   — TQQQ/KMLM/GLD 50/25/25 bull → QQQ/KMLM/GLD bear
  G3c (with_bonds)  — TQQQ/KMLM/GLD/IEF 25/25/25/25 bull → QQQ/KMLM/GLD/IEF bear
  G3d (minimal)     — TQQQ/KMLM 50/50 bull → QQQ/KMLM bear
  G3e (gayed_ndx)   — 100% TQQQ bull → 100% IEF bear (NDX-Gayed analog)

TQQQSIM not available on testfol.io → emulated via QQQSIM?L=3&E=0.84 (TQQQ ER 0.84%).
CTASIM not available → KMLM used as MF sleeve (rules-based, lower bias per Bhardwaj 2014).

All G3 variants use Daily rebal at the leg level (signal-driven nature). The
signal switches are continuous. Bull-state allocation rebalances internally
daily (per testfol.io tactical engine), but the regime switch itself fires only
when SMA condition flips (with 2% tolerance to dampen whipsaw).

Auth: TESTFOLIO_TOKEN env var.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "testfolio_data"

API_TACTICAL = "https://testfol.io/api/tactical"

# Real ETF expense ratios used as `drag` in alloc_legs.
ER = {
    "QQQ":  0.20,
    "TQQQ": 0.84,    # baked into QQQSIM?L=3&E=0.84
    "KMLM": 0.92,
    "GLD":  0.40,
    "IEF":  0.15,
    "TLT":  0.15,
    "SPY":  0.0945,
}

# Signal: SMA(QQQSIM, 200) < Price(QQQSIM)  =>  QQQ above SMA = bull regime
SIGNAL_QQQ_ABOVE_200D = {
    "name": "1",
    "indicator_1": {"type": "SMA", "ticker": "QQQSIM", "ticker_2": None,
                    "value": None, "lookback": 200, "delay": None},
    "comparison": "<",
    "indicator_2": {"type": "Price", "ticker": "QQQSIM", "ticker_2": None,
                    "value": None, "lookback": None, "delay": None},
    "tolerance": 2,    # 2% buffer to dampen whipsaw
}


def alloc_leg(name: str, signal_active: bool | None, tickers: list[tuple[str, float]],
              drag_pct: float = 0.0) -> dict:
    """Build a tactical alloc_leg.

    signal_active: True  = active when signal fires (bull)
                   False = active when signal does NOT fire (bear)
                   None  = always active (no signal)
    tickers: list of (ticker, percent) — percents must sum to 100.
    """
    if signal_active is None:
        signals = []
        nots = []
    else:
        signals = ["1"]
        nots = [not signal_active]
    return {
        "name": name,
        "signals": signals,
        "ops": [],
        "nots": nots,
        "kind": "FIXED",
        "tickers": [{"ticker": t, "percent": p} for t, p in tickers],
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
        "drag": drag_pct,
        "candidate_tickers": [],
        "optimize_objective": None,
        "rebalance_freq": "Daily",
        "rebalance_offset": 0,
        "absolute_dev": 0,
        "relative_dev": 0,
    }


def variant_g3a_funsundae() -> tuple[str, list[dict], float, float]:
    """TQQQ/KMLM/GLD 33/33/33 bull → QQQ/KMLM/GLD bear."""
    bull_drag = 0.34 * ER["TQQQ"] + 0.33 * ER["KMLM"] + 0.33 * ER["GLD"]
    bear_drag = 0.34 * ER["QQQ"]  + 0.33 * ER["KMLM"] + 0.33 * ER["GLD"]
    return (
        "G3a — TQQQ/KMLM/GLD 33-33-34 (Fun-Sundae spec)",
        [
            alloc_leg("Bull TQQQ", True, [
                ("QQQSIM?L=3&E=0.84", 34),
                ("KMLMSIM", 33),
                ("GLDSIM", 33),
            ], drag_pct=bull_drag),
            alloc_leg("Bear QQQ", False, [
                ("QQQSIM", 34),
                ("KMLMSIM", 33),
                ("GLDSIM", 33),
            ], drag_pct=bear_drag),
        ],
        bull_drag, bear_drag,
    )


def variant_g3b_heavy_ndx() -> tuple[str, list[dict], float, float]:
    """TQQQ/KMLM/GLD 50/25/25 bull → QQQ/KMLM/GLD bear (NDX-heavy)."""
    bull_drag = 0.50 * ER["TQQQ"] + 0.25 * ER["KMLM"] + 0.25 * ER["GLD"]
    bear_drag = 0.50 * ER["QQQ"]  + 0.25 * ER["KMLM"] + 0.25 * ER["GLD"]
    return (
        "G3b — TQQQ/KMLM/GLD 50-25-25 (NDX-heavy)",
        [
            alloc_leg("Bull TQQQ-heavy", True, [
                ("QQQSIM?L=3&E=0.84", 50),
                ("KMLMSIM", 25),
                ("GLDSIM", 25),
            ], drag_pct=bull_drag),
            alloc_leg("Bear QQQ-heavy", False, [
                ("QQQSIM", 50),
                ("KMLMSIM", 25),
                ("GLDSIM", 25),
            ], drag_pct=bear_drag),
        ],
        bull_drag, bear_drag,
    )


def variant_g3c_with_bonds() -> tuple[str, list[dict], float, float]:
    """TQQQ/KMLM/GLD/IEF 25/25/25/25 bull → QQQ/KMLM/GLD/IEF bear."""
    bull_drag = 0.25*ER["TQQQ"] + 0.25*ER["KMLM"] + 0.25*ER["GLD"] + 0.25*ER["IEF"]
    bear_drag = 0.25*ER["QQQ"]  + 0.25*ER["KMLM"] + 0.25*ER["GLD"] + 0.25*ER["IEF"]
    return (
        "G3c — TQQQ/KMLM/GLD/IEF 25-25-25-25 (with bonds)",
        [
            alloc_leg("Bull TQQQ+bonds", True, [
                ("QQQSIM?L=3&E=0.84", 25),
                ("KMLMSIM", 25),
                ("GLDSIM", 25),
                ("IEFSIM", 25),
            ], drag_pct=bull_drag),
            alloc_leg("Bear QQQ+bonds", False, [
                ("QQQSIM", 25),
                ("KMLMSIM", 25),
                ("GLDSIM", 25),
                ("IEFSIM", 25),
            ], drag_pct=bear_drag),
        ],
        bull_drag, bear_drag,
    )


def variant_g3d_minimal() -> tuple[str, list[dict], float, float]:
    """TQQQ/KMLM 50/50 bull → QQQ/KMLM 50/50 bear (minimal sleeves)."""
    bull_drag = 0.50*ER["TQQQ"] + 0.50*ER["KMLM"]
    bear_drag = 0.50*ER["QQQ"]  + 0.50*ER["KMLM"]
    return (
        "G3d — TQQQ/KMLM 50-50 (minimal, 2 sleeves)",
        [
            alloc_leg("Bull TQQQ+KMLM", True, [
                ("QQQSIM?L=3&E=0.84", 50),
                ("KMLMSIM", 50),
            ], drag_pct=bull_drag),
            alloc_leg("Bear QQQ+KMLM", False, [
                ("QQQSIM", 50),
                ("KMLMSIM", 50),
            ], drag_pct=bear_drag),
        ],
        bull_drag, bear_drag,
    )


def variant_g3e_gayed_ndx() -> tuple[str, list[dict], float, float]:
    """100% TQQQ bull → 100% IEF bear (NDX analog of canonical Gayed LRS)."""
    bull_drag = ER["TQQQ"]
    bear_drag = ER["IEF"]
    return (
        "G3e — TQQQ 100 / IEF 100 (Gayed-NDX)",
        [
            alloc_leg("Bull TQQQ", True, [
                ("QQQSIM?L=3&E=0.84", 100),
            ], drag_pct=bull_drag),
            alloc_leg("Bear IEF", False, [
                ("IEFSIM", 100),
            ], drag_pct=bear_drag),
        ],
        bull_drag, bear_drag,
    )


VARIANTS = [
    ("g3a_funsundae",   variant_g3a_funsundae),
    ("g3b_heavy_ndx",   variant_g3b_heavy_ndx),
    ("g3c_with_bonds",  variant_g3c_with_bonds),
    ("g3d_minimal",     variant_g3d_minimal),
    ("g3e_gayed_ndx",   variant_g3e_gayed_ndx),
]


def build_tactical_payload(name: str, allocations: list[dict]) -> dict:
    # Add benchmark leg (SPY always-on) for visual reference in stats[]
    benchmark_leg = alloc_leg("SPY (benchmark)", None, [("SPYSIM", 100)], drag_pct=ER["SPY"])
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
        "signals": [SIGNAL_QQQ_ABOVE_200D],
        "derived_signals": [],
        "aggregate_derived_signals": [],
        "mode": "BACKTEST",
        "global_candidate_tickers": [],
        "include_efficient_frontier": False,
        "allocations": allocations + [benchmark_leg],
        "trading_freq": "Daily",
        "trading_offset": 0,
        "cashflow_legs": [],
        "one_time_cashflows": [],
    }


def post_with_retries(url: str, payload: dict, token: str, attempts: int = 3) -> dict:
    body = json.dumps(payload).encode("utf-8")
    last_err: Exception | None = None
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
                    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) reddit-letf-post/1.0",
                },
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 401:
                sys.exit("fatal: TESTFOLIO_TOKEN invalid or expired (401).")
            if e.code == 429:
                print(f"warn: 429 rate-limited, sleeping 30s before retry {i+1}/{attempts}", file=sys.stderr)
                time.sleep(30)
                last_err = e
                continue
            if 500 <= e.code < 600:
                wait = 2 ** (i + 1)
                print(f"warn: {e.code} server error, sleeping {wait}s", file=sys.stderr)
                time.sleep(wait)
                last_err = e
                continue
            sys.exit(f"fatal: HTTP {e.code} from {url}: {e.read().decode('utf-8', errors='replace')[:500]}")
        except (urllib.error.URLError, TimeoutError) as e:
            wait = 2 ** (i + 1)
            print(f"warn: network error ({e}), sleeping {wait}s", file=sys.stderr)
            time.sleep(wait)
            last_err = e
    sys.exit(f"fatal: exhausted {attempts} retries: {last_err}")


def main() -> int:
    token = os.environ.get("TESTFOLIO_TOKEN", "").strip()
    if not token:
        sys.exit("fatal: TESTFOLIO_TOKEN env var not set.")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    summary: list[dict] = []
    for slug, builder in VARIANTS:
        name, allocs, bull_drag, bear_drag = builder()
        print(f"\nVariant {slug}: {name}")
        print(f"  bull drag = {bull_drag:.4f}%, bear drag = {bear_drag:.4f}%")
        payload = build_tactical_payload(name, allocs)
        resp = post_with_retries(API_TACTICAL, payload, token)
        out = DATA_DIR / f"{slug}.json"
        out.write_text(json.dumps(resp, indent=2))
        print(f"  saved {out} ({out.stat().st_size//1024} KB)")

        # Show quick stats
        if "stats" in resp and resp["stats"]:
            for s in resp["stats"]:
                lab = s.get("name", "?")
                cagr = s.get("cagr", 0)
                mdd = s.get("max_drawdown", 0)
                sharpe = s.get("sharpe", 0)
                print(f"    [{lab}] CAGR={cagr:.2f}% MDD={mdd:.2f}% Sharpe={sharpe:.4f}")
        summary.append({"slug": slug, "name": name, "bull_drag": bull_drag, "bear_drag": bear_drag})
        time.sleep(5)  # pacing between calls

    print(f"\nDone. {len(VARIANTS)} variants saved in {DATA_DIR}/")
    print("Run analyze_g3.py to extract metrics + compare with iter 040 baselines.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
