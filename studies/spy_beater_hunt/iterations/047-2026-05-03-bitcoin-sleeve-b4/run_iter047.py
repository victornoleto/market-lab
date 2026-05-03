#!/usr/bin/env python3
"""Iter 047 — small Bitcoin sleeve on corrected B4.

Tests whether a 2.5-10% crypto sleeve improves corrected B4's CAGR/MDD trade-off.
Uses BTCSIM for long-ish history; live ETF wrappers (IBIT/BTGD) are too new for
the retirement-horizon stress window. Bitcoin allocation is speculative and must
be capped because standalone BTC has extreme volatility and operational/venue
risks `[machine_trading, p.202, ch.7]`; BlackRock also frames bitcoin as unique
and volatile, not a complete investment program.
"""
from __future__ import annotations

import datetime as dt
import json
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "testfolio_data"
API_BACKTEST = "https://testfol.io/api/backtest"
INITIAL = 10_000.0

EXPENSE_RATIOS = {
    "SPY": 0.0945,
    "NTSX": 0.20,
    "GDE": 0.20,
    "RSST": 0.99,
    "KMLM": 0.92,
    "DBMF": 0.85,
    "ZROZ": 0.15,
    "BTC": 0.25,  # IBIT-like placeholder; BTCSIM itself has no ETF wrapper fee.
}

MAPPINGS = {
    "NTSX": [("SPYSIM", 0.90), ("IEFSIM", 0.60), ("CASHX", -0.50)],
    "RSST": [("SPYSIM", 1.00), ("DBMFSIM", 0.70), ("KMLMSIM", 0.30), ("CASHX?E=-2", -1.00)],
    "BTC": [("BTCSIM", 1.0)],
    "SPY": [("SPYSIM", 1.0)],
}

PORTFOLIOS = [
    {"slug": "B4_base", "label": "B4 corrected baseline", "allocation_real": [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (25, "ZROZ")]},
    {"slug": "B4_btc2p5_from_zroz", "label": "B4 + 2.5 BTC from ZROZ", "allocation_real": [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (22.5, "ZROZ"), (2.5, "BTC")]},
    {"slug": "B4_btc5_from_zroz", "label": "B4 + 5 BTC from ZROZ", "allocation_real": [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (20, "ZROZ"), (5, "BTC")]},
    {"slug": "B4_btc10_from_zroz", "label": "B4 + 10 BTC from ZROZ", "allocation_real": [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (15, "ZROZ"), (10, "BTC")]},
    {"slug": "B4_btc5_from_ntsx", "label": "B4 + 5 BTC from NTSX", "allocation_real": [(20, "NTSX"), (5, "BTC"), (25, "GDE"), (25, "RSST"), (25, "ZROZ")]},
    {"slug": "B4_btc5_from_rsst", "label": "B4 + 5 BTC from RSST", "allocation_real": [(25, "NTSX"), (25, "GDE"), (20, "RSST"), (25, "ZROZ"), (5, "BTC")]},
    {"slug": "SPY_1x", "label": "SPY 1x benchmark", "allocation_real": [(100, "SPY")]},
]


def expand(weight_pct: float, ticker: str) -> list[tuple[str, float]]:
    if ticker in MAPPINGS:
        return [(token, weight_pct * mult) for token, mult in MAPPINGS[ticker]]
    return [(f"{ticker}SIM", weight_pct)]


def decompose(allocation: list[tuple[float, str]]) -> dict[str, float]:
    agg: defaultdict[str, float] = defaultdict(float)
    for pct, ticker in allocation:
        for token, w in expand(pct, ticker.upper()):
            agg[token] += w
    return {k: round(v, 4) for k, v in agg.items() if abs(v) > 1e-6}


def compute_drag(allocation: list[tuple[float, str]]) -> float:
    return round(sum((pct / 100.0) * EXPENSE_RATIOS.get(ticker.upper(), 0.0) for pct, ticker in allocation), 4)


def payload(portfolios: list[dict]) -> dict:
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


def post(data: dict) -> dict:
    body = json.dumps(data).encode("utf-8")
    last_err: Exception | None = None
    for i in range(3):
        try:
            req = urllib.request.Request(API_BACKTEST, data=body, method="POST", headers={"content-type": "application/json", "user-agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            last_err = RuntimeError(f"HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')[:1000]}")
        except (urllib.error.URLError, TimeoutError) as exc:
            last_err = exc
        time.sleep(2 ** (i + 1))
    raise RuntimeError(last_err)


def years_from_response(response: dict) -> tuple[float, str]:
    history = response["charts"]["history"][0]
    start = dt.datetime.fromtimestamp(history[0], tz=dt.UTC).date()
    end = dt.datetime.fromtimestamp(history[-1], tz=dt.UTC).date()
    years = (end - start).days / 365.25
    return years, f"{start} -> {end} ({years:.2f}y)"


def run() -> list[dict]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    portfolios = [dict(p) for p in PORTFOLIOS]
    for p in portfolios:
        p["allocation_sim"] = decompose(p["allocation_real"])
        p["drag_pct"] = compute_drag(p["allocation_real"])
    rows = []
    for i in range(0, len(portfolios), 5):
        batch = portfolios[i:i + 5]
        response = post(payload(batch))
        if response.get("errors"):
            raise RuntimeError(response["errors"])
        letter = chr(ord("a") + i // 5)
        (DATA_DIR / f"backtest_{letter}.json").write_text(json.dumps({"portfolios": batch, "response": response}, indent=2))
        years, window = years_from_response(response)
        for p, s in zip(batch, response["stats"]):
            rows.append({
                "slug": p["slug"],
                "label": p["label"],
                "window": window,
                "cagr_pct": s["cagr"],
                "mdd_pct": s["max_drawdown"],
                "sharpe": s["sharpe"],
                "sortino": s.get("sortino", 0.0),
                "calmar": s.get("calmar", 0.0),
                "end_val": s["end_val"],
                "drag_pct": p["drag_pct"],
                "allocation_sim": p["allocation_sim"],
            })
    rows.sort(key=lambda r: (-r["sharpe"], -r["cagr_pct"]))
    (SCRIPT_DIR / "unified_metrics.json").write_text(json.dumps(rows, indent=2))
    return rows


def write_summary(rows: list[dict]) -> None:
    b4 = next(r for r in rows if r["slug"] == "B4_base")
    lines = [
        "# Iter 047 — Bitcoin sleeve on corrected B4",
        "",
        "**Date:** 2026-05-03",
        "**Source:** testfol.io API (`BTCSIM` for Bitcoin).",
        "**Window:** common window determined by BTCSIM + corrected RSST proxy.",
        "**Tax model:** no DARF applied; crypto ETF/ETP tax treatment and availability must be checked separately.",
        "",
        "## Ranking By Sharpe",
        "",
        "| # | strategy | window | CAGR | MDD | Sharpe | Calmar |",
        "|---:|---|---|---:|---:|---:|---:|",
    ]
    for i, r in enumerate(rows, 1):
        lines.append(f"| {i} | {r['slug']} | {r['window']} | {r['cagr_pct']:.2f}% | {r['mdd_pct']:.2f}% | {r['sharpe']:.3f} | {r['calmar']:.3f} |")
    lines += [
        "",
        "## Findings",
        "",
        f"Corrected B4 baseline in this Bitcoin-constrained window: {b4['cagr_pct']:.2f}% CAGR / {b4['mdd_pct']:.2f}% MDD / {b4['sharpe']:.3f} Sharpe.",
    ]
    beat = [r for r in rows if r["slug"] != "B4_base" and r["cagr_pct"] > b4["cagr_pct"] and abs(r["mdd_pct"]) <= abs(b4["mdd_pct"])]
    if beat:
        lines.append("Variants that beat B4 on CAGR without worse MDD:")
        for r in beat:
            lines.append(f"- {r['slug']}: {r['cagr_pct']:.2f}% / {r['mdd_pct']:.2f}% / {r['sharpe']:.3f}")
    else:
        lines.append("No Bitcoin variant beats B4 on CAGR without worse MDD.")
    lines += [
        "",
        "## Caveats",
        "",
        "- BTCSIM is spot Bitcoin simulation, not IBIT/BTGD live history.",
        "- Bitcoin has short history versus equities/bonds and extreme regime dependence.",
        "- A 5-10% sleeve is a speculation sleeve; size must be capped ex ante.",
    ]
    (SCRIPT_DIR / "SUMMARY.md").write_text("\n".join(lines) + "\n")


def main() -> int:
    rows = run()
    write_summary(rows)
    for r in rows:
        print(f"{r['slug']:<24} {r['cagr_pct']:>6.2f}% {r['mdd_pct']:>8.2f}% {r['sharpe']:>6.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
