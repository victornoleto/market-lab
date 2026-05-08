#!/usr/bin/env python3
"""Iter 052 — momentum/SCV sleeves on corrected B4 and B4+BTC5.

Purpose: evaluate user-proposed momentum and small-cap-value additions to the
current B4 family without treating recent ETF popularity as sufficient evidence.
Momentum/SCV rationale follows documented factor premia rather than narrative
timing: momentum `[stocks_on_the_move, ch.4]` and factor expected returns
`[ilmanen_expected_returns, ch.10-12]`. Overfit discipline follows the project's
PBO/DSR habit: this is a screening run, not a full gate-equivalent promotion
`[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import datetime as dt
import json
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any


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
    "BTC": 0.25,
    "SPMO": 0.13,
    "FMTM": 0.15,
    "MTUM": 0.15,
    "VBR": 0.07,
    "AVUV": 0.25,
    "SCHG": 0.04,
    "VUG": 0.04,
}


MAPPINGS = {
    "NTSX": [("SPYSIM", 0.90), ("IEFSIM", 0.60), ("CASHX", -0.50)],
    "RSST": [("SPYSIM", 1.00), ("DBMFSIM", 0.70), ("KMLMSIM", 0.30), ("CASHX?E=-2", -1.00)],
    "BTC": [("BTCSIM", 1.0)],
    "SPY": [("SPYSIM", 1.0)],
    "MTUM": [("MTUMSIM", 1.0)],
    "VBR": [("VBRSIM", 1.0)],
}


def expand(weight_pct: float, ticker: str) -> list[tuple[str, float]]:
    ticker = ticker.upper()
    if ticker in MAPPINGS:
        return [(token, weight_pct * mult) for token, mult in MAPPINGS[ticker]]
    return [(ticker, weight_pct)]


def decompose(allocation: list[tuple[float, str]]) -> dict[str, float]:
    agg: defaultdict[str, float] = defaultdict(float)
    for pct, ticker in allocation:
        for token, weight_pct in expand(pct, ticker):
            agg[token] += weight_pct
    return {k: round(v, 4) for k, v in agg.items() if abs(v) > 1e-6}


def compute_drag(allocation: list[tuple[float, str]]) -> float:
    return round(sum((pct / 100.0) * EXPENSE_RATIOS.get(ticker.upper(), 0.0) for pct, ticker in allocation), 4)


def make_portfolio(slug: str, label: str, allocation_real: list[tuple[float, str]]) -> dict[str, Any]:
    return {
        "slug": slug,
        "label": label,
        "allocation_real": allocation_real,
        "allocation_sim": decompose(allocation_real),
        "drag_pct": compute_drag(allocation_real),
    }


def payload(portfolios: list[dict[str, Any]], *, start_date: str = "1800-01-01") -> dict[str, Any]:
    return {
        "start_date": start_date,
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


def post(data: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(data).encode("utf-8")
    last_err: Exception | None = None
    for i in range(3):
        try:
            req = urllib.request.Request(
                API_BACKTEST,
                data=body,
                method="POST",
                headers={"content-type": "application/json", "user-agent": "Mozilla/5.0"},
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:1000]
            last_err = RuntimeError(f"HTTP {exc.code}: {detail}")
        except (urllib.error.URLError, TimeoutError) as exc:
            last_err = exc
        time.sleep(2 ** (i + 1))
    raise RuntimeError(last_err)


def window_from_response(response: dict[str, Any]) -> str:
    history = response["charts"]["history"][0]
    start = dt.datetime.fromtimestamp(history[0], tz=dt.UTC).date()
    end = dt.datetime.fromtimestamp(history[-1], tz=dt.UTC).date()
    years = (end - start).days / 365.25
    return f"{start} -> {end} ({years:.2f}y)"


def collect(group: str, portfolios: list[dict[str, Any]], *, start_date: str = "1800-01-01") -> list[dict[str, Any]]:
    cache_path = DATA_DIR / f"{group}.json"
    try:
        response = post(payload(portfolios, start_date=start_date))
    except RuntimeError:
        if not cache_path.exists():
            raise
        cached = json.loads(cache_path.read_text())
        response = cached["response"]
        portfolios = cached["portfolios"]
    if response.get("errors"):
        raise RuntimeError(response["errors"])
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps({"portfolios": portfolios, "response": response}, indent=2))
    window = window_from_response(response)
    rows = []
    for p, s in zip(portfolios, response["stats"]):
        rows.append(
            {
                "group": group,
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
            }
        )
    return rows


def portfolio_sets() -> dict[str, list[dict[str, Any]]]:
    b4 = [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (25, "ZROZ")]
    b4_btc5 = [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (20, "ZROZ"), (5, "BTC")]

    standalone_spmo_live = [
        make_portfolio("SPY", "SPY live", [(100, "SPY")]),
        make_portfolio("SPMO", "SPMO live", [(100, "SPMO")]),
        make_portfolio("SSO", "SSO live", [(100, "SSO")]),
        make_portfolio("SCHG", "SCHG live", [(100, "SCHG")]),
    ]
    standalone_fmtm_live = [
        make_portfolio("SPY", "SPY live", [(100, "SPY")]),
        make_portfolio("SPMO", "SPMO live", [(100, "SPMO")]),
        make_portfolio("FMTM", "FMTM live", [(100, "FMTM")]),
        make_portfolio("SSO", "SSO live", [(100, "SSO")]),
        make_portfolio("SCHG", "SCHG live", [(100, "SCHG")]),
    ]
    standalone_sim = [
        make_portfolio("SPYSIM", "SPYSIM long", [(100, "SPY")]),
        make_portfolio("MTUMSIM", "MTUMSIM long", [(100, "MTUM")]),
        make_portfolio("VBRSIM", "VBRSIM long", [(100, "VBR")]),
    ]
    b4_screen = [
        make_portfolio("B4_base", "B4 corrected", b4),
        make_portfolio("B4_spmo2p5_from_zroz", "B4 + 2.5 SPMO from ZROZ", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (22.5, "ZROZ"), (2.5, "SPMO")]),
        make_portfolio("B4_spmo5_from_zroz", "B4 + 5 SPMO from ZROZ", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (20, "ZROZ"), (5, "SPMO")]),
        make_portfolio("B4_spmo10_from_zroz", "B4 + 10 SPMO from ZROZ", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (15, "ZROZ"), (10, "SPMO")]),
        make_portfolio("B4_mtum10_from_zroz", "B4 + 10 MTUMSIM from ZROZ", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (15, "ZROZ"), (10, "MTUM")]),
    ]
    b4_screen_2 = [
        make_portfolio("B4_base", "B4 corrected", b4),
        make_portfolio("B4_fmtm2p5_from_zroz", "B4 + 2.5 FMTM from ZROZ", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (22.5, "ZROZ"), (2.5, "FMTM")]),
        make_portfolio("B4_fmtm5_from_zroz", "B4 + 5 FMTM from ZROZ", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (20, "ZROZ"), (5, "FMTM")]),
        make_portfolio("B4_vbr10_from_zroz", "B4 + 10 VBRSIM from ZROZ", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (15, "ZROZ"), (10, "VBR")]),
        make_portfolio("B4_avuv5_from_zroz", "B4 + 5 AVUV from ZROZ", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (20, "ZROZ"), (5, "AVUV")]),
    ]
    b4_btc_screen = [
        make_portfolio("B4_btc5", "B4 + 5 BTC", b4_btc5),
        make_portfolio("B4_btc5_spmo2p5_from_zroz", "B4+BTC5 + 2.5 SPMO from ZROZ", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (17.5, "ZROZ"), (5, "BTC"), (2.5, "SPMO")]),
        make_portfolio("B4_btc5_spmo5_from_zroz", "B4+BTC5 + 5 SPMO from ZROZ", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (15, "ZROZ"), (5, "BTC"), (5, "SPMO")]),
        make_portfolio("B4_btc5_mtum5_from_zroz", "B4+BTC5 + 5 MTUMSIM from ZROZ", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (15, "ZROZ"), (5, "BTC"), (5, "MTUM")]),
        make_portfolio("B4_btc5_vbr5_from_zroz", "B4+BTC5 + 5 VBRSIM from ZROZ", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (15, "ZROZ"), (5, "BTC"), (5, "VBR")]),
    ]
    b4_btc_screen_2 = [
        make_portfolio("B4_btc5", "B4 + 5 BTC", b4_btc5),
        make_portfolio("B4_btc5_fmtm2p5_from_zroz", "B4+BTC5 + 2.5 FMTM from ZROZ", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (17.5, "ZROZ"), (5, "BTC"), (2.5, "FMTM")]),
        make_portfolio("B4_btc5_fmtm5_from_zroz", "B4+BTC5 + 5 FMTM from ZROZ", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (15, "ZROZ"), (5, "BTC"), (5, "FMTM")]),
        make_portfolio("B4_btc5_avuv5_from_zroz", "B4+BTC5 + 5 AVUV from ZROZ", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (15, "ZROZ"), (5, "BTC"), (5, "AVUV")]),
        make_portfolio("B4_btc5_schg5_from_zroz", "B4+BTC5 + 5 SCHG from ZROZ", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (15, "ZROZ"), (5, "BTC"), (5, "SCHG")]),
    ]
    return {
        "standalone_spmo_live": standalone_spmo_live,
        "standalone_fmtm_live": standalone_fmtm_live,
        "standalone_sim": standalone_sim,
        "b4_screen_a": b4_screen,
        "b4_screen_b": b4_screen_2,
        "b4_btc_screen_a": b4_btc_screen,
        "b4_btc_screen_b": b4_btc_screen_2,
    }


def write_summary(rows: list[dict[str, Any]]) -> None:
    by_group: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_group[row["group"]].append(row)
    lines = [
        "# Iter 052 — Momentum/SCV sleeves on B4",
        "",
        "**Date:** 2026-05-03",
        "**Source:** testfol.io API; monthly rebalance; explicit estimated ER drag.",
        "**Status:** screening only, not full PBO/DSR/WF/bootstrap gate-equivalent.",
        "",
    ]
    for group, group_rows in by_group.items():
        lines += [
            f"## {group}",
            "",
            f"Window: {group_rows[0]['window']}",
            "",
            "| strategy | CAGR | MDD | Sharpe | Calmar |",
            "|---|---:|---:|---:|---:|",
        ]
        for r in sorted(group_rows, key=lambda x: (-x["sharpe"], -x["cagr_pct"])):
            lines.append(f"| {r['slug']} | {r['cagr_pct']:.2f}% | {r['mdd_pct']:.2f}% | {r['sharpe']:.3f} | {r['calmar']:.3f} |")
        lines.append("")
    lines += [
        "## Caveats",
        "",
        "- Live `SPMO`, `FMTM`, `AVUV`, and `SCHG` rows are inception-limited; do not compare them to 1987+/2000+ stress windows as if they were equivalent.",
        "- `MTUMSIM` and `VBRSIM` are long synthetic factor proxies and are useful for stress shape, but they are not identical to live SPMO/FMTM/AVUV products.",
        "- Replacing ZROZ with equity-like factor exposure mechanically raises equity beta and usually weakens crisis convexity.",
    ]
    (SCRIPT_DIR / "SUMMARY.md").write_text("\n".join(lines) + "\n")


def main() -> int:
    all_rows: list[dict[str, Any]] = []
    for group, portfolios in portfolio_sets().items():
        rows = collect(group, portfolios)
        all_rows.extend(rows)
        print(f"\n{group}")
        for r in sorted(rows, key=lambda x: (-x["sharpe"], -x["cagr_pct"])):
            print(f"{r['slug']:<34} {r['cagr_pct']:>6.2f}% {r['mdd_pct']:>8.2f}% {r['sharpe']:>6.3f}  {r['window']}")
    (SCRIPT_DIR / "unified_metrics.json").write_text(json.dumps(all_rows, indent=2))
    write_summary(all_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
