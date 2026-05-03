#!/usr/bin/env python3
"""Iter 045 — re-run iter 044 with RSST trend proxy = 70% DBMF + 30% KMLM.

Rationale: live RSST tracking test (2023-09-06 -> 2026-05-01) showed
`SPY + 70% DBMF + 30% KMLM - cash` tracks real RSST materially better than
the previous `SPY + KMLM - cash` proxy. This is a proxy correction, not a new
weight optimization. Return stacking follows Carlson's capital-efficient
stacking framing `[risk_parity, ch.5, p.10]`; diversifying managed-futures
engines follows Ilmanen's crisis-alpha/alternative-risk-premia rationale
`[ilmanen_expected_returns, ch.19]`.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "testfolio_data"
API_BACKTEST = "https://testfol.io/api/backtest"
INITIAL = 10000.0

EXPENSE_RATIOS = {
    "SPY": 0.0945,
    "NTSX": 0.20,
    "GDE": 0.20,
    "RSST": 0.99,
    "RSSB": 0.69,
    "KMLM": 0.92,
    "DBMF": 0.85,
    "GLD": 0.40,
    "TLT": 0.15,
    "ZROZ": 0.15,
}

ER_BAKED_IN_SIM = {"TMF"}

MAPPINGS = {
    "NTSX": [("SPYSIM", 0.90), ("IEFSIM", 0.60), ("CASHX", -0.50)],
    "RSST": [("SPYSIM", 1.00), ("DBMFSIM", 0.70), ("KMLMSIM", 0.30), ("CASHX?E=-2", -1.00)],
    "TMF": [("TLTSIM?L=3&E=1.05", 1.0)],
}

PORTFOLIOS_38Y = [
    {"slug": "M1_kmlm_no_rsst", "label": "M1 KMLM no RSST",
     "allocation_real": [(25, "NTSX"), (25, "GDE"), (25, "KMLM"), (25, "TMF")]},
    {"slug": "L1_cegb_proxy", "label": "L1 CEGB proxy",
     "allocation_real": [(40, "NTSX"), (25, "GDE"), (17.5, "KMLM"), (17.5, "TLT")]},
    {"slug": "L2_bogleheads_67ntsx", "label": "L2 Bogleheads (67/11/11/11 NTSX/GLD/KMLM/ZROZ)",
     "allocation_real": [(67, "NTSX"), (11, "GLD"), (11, "KMLM"), (11, "ZROZ")]},
    {"slug": "spy_1x", "label": "SPY 1x buy-hold",
     "allocation_real": [(100, "SPY")]},
]

PORTFOLIOS_26Y_RSST_DBMF = [
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
    {"slug": "M2_dbmf_no_rsst", "label": "M2 DBMF no RSST",
     "allocation_real": [(25, "NTSX"), (25, "GDE"), (25, "DBMF"), (25, "TMF")]},
    {"slug": "M3_kmlm_dbmf_blend", "label": "M3 KMLM+DBMF blend",
     "allocation_real": [(25, "NTSX"), (25, "GDE"), (12.5, "KMLM"), (12.5, "DBMF"), (25, "TMF")]},
    {"slug": "M4_rsst_kmlm_blend", "label": "M4 RSST+KMLM blend",
     "allocation_real": [(25, "NTSX"), (25, "GDE"), (12.5, "RSST"), (12.5, "KMLM"), (25, "TMF")]},
    {"slug": "T1_gold_heavy", "label": "T1 gold-heavy (20/35/25/20 NTSX/GDE/RSST/TMF)",
     "allocation_real": [(20, "NTSX"), (35, "GDE"), (25, "RSST"), (20, "TMF")]},
    {"slug": "T2_equity_heavy", "label": "T2 equity-heavy (35/25/25/15 NTSX/GDE/RSST/TMF)",
     "allocation_real": [(35, "NTSX"), (25, "GDE"), (25, "RSST"), (15, "TMF")]},
    {"slug": "T3_rssb_global", "label": "T3 RSSB global (25/25/25/25 RSSB/GDE/RSST/TMF)",
     "allocation_real": [(25, "RSSB"), (25, "GDE"), (25, "RSST"), (25, "TMF")]},
]


def expand(weight_pct: float, ticker: str) -> list[tuple[str, float]]:
    ticker = ticker.upper()
    if ticker in MAPPINGS:
        return [(token, weight_pct * mult) for token, mult in MAPPINGS[ticker]]
    if ticker == "SPY":
        return [("SPY", weight_pct)]
    return [(f"{ticker}SIM", weight_pct)]


def decompose(allocation: list[tuple[float, str]]) -> dict[str, float]:
    agg: defaultdict[str, float] = defaultdict(float)
    for pct, ticker in allocation:
        for token, weight_pct in expand(pct, ticker):
            agg[token] += weight_pct
    return {k: round(v, 4) for k, v in agg.items() if abs(v) > 1e-6}


def compute_drag(allocation: list[tuple[float, str]]) -> float:
    drag = 0.0
    for pct, ticker in allocation:
        ticker = ticker.upper()
        if ticker in ER_BAKED_IN_SIM:
            continue
        drag += (pct / 100.0) * EXPENSE_RATIOS.get(ticker, 0.0)
    return round(drag, 4)


def build_payload(portfolios: list[dict]) -> dict:
    return {
        "start_date": "2000-01-01",
        "end_date": "2100-01-01",
        "start_val": INITIAL,
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
        "cashflow_legs": [],
        "cashflow_type": None,
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
    }


def post(payload: dict, attempts: int = 3) -> dict:
    body = json.dumps(payload).encode("utf-8")
    last_err: Exception | None = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(
                API_BACKTEST,
                data=body,
                method="POST",
                headers={"content-type": "application/json", "user-agent": "Mozilla/5.0"},
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.loads(resp.read())
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            last_err = exc
            time.sleep(2 ** (i + 1))
    raise RuntimeError(f"failed after retries: {last_err}")


def fetch_and_save(batch: list[dict], letter: str) -> None:
    for p in batch:
        p["allocation_sim"] = decompose(p["allocation_real"])
        p["drag_pct"] = compute_drag(p["allocation_real"])
    print(f"POST batch {letter} ({len(batch)} portfolios)")
    response = post(build_payload(batch))
    if response.get("errors"):
        raise RuntimeError(response["errors"])
    out = DATA_DIR / f"backtest_{letter}.json"
    out.write_text(json.dumps({"portfolios": batch, "response": response}, indent=2))
    for p, s in zip(batch, response["stats"]):
        print(f"  {p['slug']:<28} CAGR={s['cagr']:.2f}% MDD={s['max_drawdown']:.2f}% Sharpe={s['sharpe']:.4f}")


def years_from_response(response: dict) -> tuple[float, str]:
    history = response["charts"]["history"][0]
    start = dt.datetime.fromtimestamp(history[0], tz=dt.UTC).date()
    end = dt.datetime.fromtimestamp(history[-1], tz=dt.UTC).date()
    years = (end - start).days / 365.25
    return years, f"{start} -> {end} ({years:.2f}y)"


def no_tax_buy_hold(end_val: float, years: float) -> tuple[float, float]:
    """Do not apply DARF to static buy-and-hold/lazy-rebal comparisons.

    User decision 2026-05-02: taxes are considered for swing/tactical
    strategies that realize gains through position changes, not for these
    buy-and-hold portfolio comparisons.
    """
    cagr = ((end_val / INITIAL) ** (1.0 / years) - 1.0) * 100.0
    return end_val, cagr


def analyze() -> list[dict]:
    rows: list[dict] = []
    for path in sorted(DATA_DIR.glob("backtest_*.json")):
        d = json.loads(path.read_text())
        years, window = years_from_response(d["response"])
        for p, s in zip(d["portfolios"], d["response"]["stats"]):
            net_end, net_cagr = no_tax_buy_hold(s["end_val"], years)
            rows.append({
                "slug": p["slug"],
                "label": p["label"],
                "gross_cagr_pct": s["cagr"],
                "mdd_pct": s["max_drawdown"],
                "sharpe": s["sharpe"],
                "sortino": s.get("sortino", 0.0),
                "calmar": s.get("calmar", 0.0),
                "gross_end_val": s["end_val"],
                "net_end_val": net_end,
                "net_cagr_pct": net_cagr,
                "years": years,
                "window_label": window,
                "drag_pct": p["drag_pct"],
                "allocation_sim": p["allocation_sim"],
            })
    rows.sort(key=lambda r: (-r["sharpe"], -r["net_cagr_pct"]))
    (SCRIPT_DIR / "unified_metrics.json").write_text(json.dumps(rows, indent=2))
    return rows


def write_summary(rows: list[dict]) -> None:
    spy = next(r for r in rows if r["slug"] == "spy_1x")
    lines = [
        "# Iter 045 — RSST proxy 70/30 DBMF/KMLM rebaseline",
        "",
        "**Date:** 2026-05-02",
        "**Source:** testfol.io API",
        "**Change vs iter 044:** `RSST = SPY + 70% DBMF + 30% KMLM - CASHX?E=-2` instead of `SPY + KMLM - CASHX`.",
        "",
        "Because DBMFSIM starts in 2000, this run forces all portfolios onto the same common 2000-01-03 -> 2026-05-01 window. This is the apples-to-apples comparison for the corrected RSST proxy.",
        "",
        "## Ranking By Sharpe",
        "",
        "**Tax model:** no DARF applied. These are static buy-and-hold/lazy-rebal scenarios; tax is reserved for swing/tactical strategies that realize gains through position changes.",
        "",
        "| # | strategy | window | CAGR (no tax) | MDD | Sharpe | Calmar |",
        "|---:|---|---|---:|---:|---:|---:|",
    ]
    for i, r in enumerate(rows, 1):
        lines.append(
            f"| {i} | {r['slug']} | {r['window_label']} | {r['gross_cagr_pct']:.2f}% | "
            f"{r['mdd_pct']:.2f}% | {r['sharpe']:.3f} | {r['calmar']:.3f} |"
        )
    lines += [
        "",
        "## Beats SPY On CAGR And MDD",
        "",
        f"SPY benchmark: CAGR {spy['gross_cagr_pct']:.2f}% / MDD {spy['mdd_pct']:.2f}%.",
        "",
    ]
    winners = [r for r in rows if r["slug"] != "spy_1x" and r["net_cagr_pct"] > spy["net_cagr_pct"] and abs(r["mdd_pct"]) < abs(spy["mdd_pct"])]
    for r in winners:
        lines.append(f"- {r['slug']}: CAGR {r['gross_cagr_pct']:.2f}%, MDD {r['mdd_pct']:.2f}%, Sharpe {r['sharpe']:.3f}")
    lines += [
        "",
        "## Methodology Note",
        "",
        "This run corrects the RSST proxy based on a live ETF tracking check, not on a new parameter search. The proxy follows return-stacking logic `[risk_parity, ch.5, p.10]` and uses diversified managed-futures engines `[ilmanen_expected_returns, ch.19]`.",
    ]
    (SCRIPT_DIR / "SUMMARY.md").write_text("\n".join(lines) + "\n")


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for old in DATA_DIR.glob("backtest_*.json"):
        old.unlink()
    all_portfolios = PORTFOLIOS_26Y_RSST_DBMF + PORTFOLIOS_38Y
    batches = []
    for idx in range(0, len(all_portfolios), 5):
        batches.append((chr(ord("a") + len(batches)), all_portfolios[idx:idx + 5]))
    for letter, batch in batches:
        fetch_and_save(batch, letter)
    rows = analyze()
    write_summary(rows)
    print("\nRanking by Sharpe")
    for r in rows:
        print(f"{r['slug']:<28} window={r['window_label']:<28} net={r['net_cagr_pct']:.2f}% mdd={r['mdd_pct']:.2f}% sharpe={r['sharpe']:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
