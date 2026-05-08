#!/usr/bin/env python3
"""Iter 055 — VBRSIM/MTUMSIM satellite with BTC-limited and no-BTC windows.

Tests the user's satellite idea with long synthetic proxies rather than live
AVUV/SPMO/FMTM inception-limited ETFs: 10% VBRSIM (SCV proxy), 10% MTUMSIM
(momentum proxy for SPMO+FMTM), and optionally 5% BTCSIM. Factor rationale follows value/size
and momentum evidence `[ilmanen_expected_returns, ch.10-12]` and
`[stocks_on_the_move, ch.4]`; the comparison is still a pre-registered screen,
not a full PBO/DSR promotion `[advances_fin_ml, p.208-211]`.
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

import pandas as pd

from ai_trade.backtest.data.testfolio_loader import load_testfolio_frame


SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "testfolio_data"
API_BACKTEST = "https://testfol.io/api/backtest"
INITIAL = 10_000.0


EXPENSE_RATIOS = {
    "SPY": 0.0945,
    "NTSX": 0.20,
    "GDE": 0.20,
    "RSST": 0.99,
    "ZROZ": 0.15,
    "BTC": 0.25,
    "VBR": 0.07,
    "MTUM": 0.15,
}


MAPPINGS = {
    "NTSX": [("SPYSIM", 0.90), ("IEFSIM", 0.60), ("CASHX", -0.50)],
    "GDE": [("GDESIM", 1.0)],
    "RSST": [("SPYSIM", 1.00), ("DBMFSIM", 0.70), ("KMLMSIM", 0.30), ("CASHX?E=-2", -1.00)],
    "ZROZ": [("ZROZSIM", 1.0)],
    "BTC": [("BTCSIM", 1.0)],
    "VBR": [("VBRSIM", 1.0)],
    "MTUM": [("MTUMSIM", 1.0)],
    "SPY": [("SPYSIM", 1.0)],
}


def expand(pct: float, ticker: str) -> list[tuple[str, float]]:
    return [(token, pct * mult) for token, mult in MAPPINGS[ticker]]


def decompose(allocation: list[tuple[float, str]]) -> dict[str, float]:
    out: defaultdict[str, float] = defaultdict(float)
    for pct, ticker in allocation:
        if pct == 0:
            continue
        for token, weight in expand(pct, ticker):
            out[token] += weight
    return {k: round(v, 6) for k, v in out.items() if abs(v) > 1e-8}


def drag(allocation: list[tuple[float, str]]) -> float:
    return round(sum((pct / 100.0) * EXPENSE_RATIOS[ticker] for pct, ticker in allocation), 4)


def portfolio(slug: str, allocation: list[tuple[float, str]]) -> dict[str, Any]:
    return {"slug": slug, "allocation_real": allocation, "allocation_sim": decompose(allocation), "drag_pct": drag(allocation)}


WITH_BTC = [
    portfolio("B4_base", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (25, "ZROZ")]),
    portfolio("B4_btc5", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (20, "ZROZ"), (5, "BTC")]),
    portfolio("proxy_sat_prorata_b4", [(18.75, "NTSX"), (18.75, "GDE"), (18.75, "RSST"), (18.75, "ZROZ"), (10, "VBR"), (10, "MTUM"), (5, "BTC")]),
    portfolio("proxy_sat_from_zroz_only", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (0, "ZROZ"), (10, "VBR"), (10, "MTUM"), (5, "BTC")]),
    portfolio("proxy_sat_from_zroz_ntsx", [(15, "NTSX"), (25, "GDE"), (25, "RSST"), (10, "ZROZ"), (10, "VBR"), (10, "MTUM"), (5, "BTC")]),
    portfolio("proxy_sat_keep_rsst_bal", [(20, "NTSX"), (20, "GDE"), (25, "RSST"), (10, "ZROZ"), (10, "VBR"), (10, "MTUM"), (5, "BTC")]),
    portfolio("SPY", [(100, "SPY")]),
]


NO_BTC = [
    portfolio("B4_base", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (25, "ZROZ")]),
    portfolio("proxy_sat20_prorata_no_btc", [(20, "NTSX"), (20, "GDE"), (20, "RSST"), (20, "ZROZ"), (10, "VBR"), (10, "MTUM")]),
    portfolio("proxy_sat20_from_zroz", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (5, "ZROZ"), (10, "VBR"), (10, "MTUM")]),
    portfolio("proxy_sat20_from_zroz_ntsx", [(15, "NTSX"), (25, "GDE"), (25, "RSST"), (15, "ZROZ"), (10, "VBR"), (10, "MTUM")]),
    portfolio("proxy_sat20_keep_rsst_bal", [(20, "NTSX"), (20, "GDE"), (25, "RSST"), (15, "ZROZ"), (10, "VBR"), (10, "MTUM")]),
    portfolio("SPY", [(100, "SPY")]),
]


def payload(portfolios: list[dict[str, Any]], start_date: str) -> dict[str, Any]:
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
        "backtests": [
            {"invest_dividends": True, "rebalance_freq": "Monthly", "rebalance_offset": 0, "allocation": p["allocation_sim"], "drag": p["drag_pct"], "absolute_dev": 0, "relative_dev": 0}
            for p in portfolios
        ],
    }


def post(data: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(data).encode("utf-8")
    last_err: Exception | None = None
    for i in range(4):
        try:
            req = urllib.request.Request(API_BACKTEST, data=body, method="POST", headers={"content-type": "application/json", "user-agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            last_err = RuntimeError(f"HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')[:800]}")
            if exc.code == 429:
                time.sleep(30)
                continue
        except (urllib.error.URLError, TimeoutError) as exc:
            last_err = exc
        time.sleep(2 ** (i + 1))
    raise RuntimeError(last_err)


def fetch_single_curve(ticker: str) -> pd.Series:
    cache = DATA_DIR / f"single_{ticker}.json"
    if cache.exists():
        response = json.loads(cache.read_text())["response"]
    else:
        response = post(payload([{"allocation_sim": {ticker: 100}, "drag_pct": 0}], "1800-01-01"))
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps({"ticker": ticker, "response": response}, indent=2))
    if response.get("errors"):
        raise RuntimeError(response["errors"])
    idx = pd.to_datetime(response["charts"]["history"][0], unit="s", utc=True).tz_convert(None)
    return pd.Series(response["charts"]["history"][1], index=idx, name=ticker).astype(float)


def sleeve_returns(include_btc: bool) -> pd.DataFrame:
    cache = load_testfolio_frame()
    prices = cache[["SPYSIM", "IEFSIM", "CASHX", "GDESIM", "DBMFSIM", "KMLMSIM", "ZROZSIM", "VBRSIM"]].copy()
    extra_series = [fetch_single_curve("MTUMSIM")]
    if include_btc:
        extra_series.append(fetch_single_curve("BTCSIM"))
    extras = pd.concat(extra_series, axis=1)
    prices = pd.concat([prices, extras], axis=1, join="inner").dropna()
    rets = prices.pct_change().dropna()
    sleeves = pd.DataFrame(index=rets.index)
    sleeves["NTSX"] = 0.90 * rets["SPYSIM"] + 0.60 * rets["IEFSIM"] - 0.50 * rets["CASHX"] - EXPENSE_RATIOS["NTSX"] / 100 / 252
    sleeves["GDE"] = rets["GDESIM"] - EXPENSE_RATIOS["GDE"] / 100 / 252
    sleeves["RSST"] = rets["SPYSIM"] + 0.70 * rets["DBMFSIM"] + 0.30 * rets["KMLMSIM"] - (rets["CASHX"] - 0.02 / 252) - EXPENSE_RATIOS["RSST"] / 100 / 252
    sleeves["ZROZ"] = rets["ZROZSIM"] - EXPENSE_RATIOS["ZROZ"] / 100 / 252
    sleeves["VBR"] = rets["VBRSIM"] - EXPENSE_RATIOS["VBR"] / 100 / 252
    sleeves["MTUM"] = rets["MTUMSIM"] - EXPENSE_RATIOS["MTUM"] / 100 / 252
    if include_btc:
        sleeves["BTC"] = rets["BTCSIM"] - EXPENSE_RATIOS["BTC"] / 100 / 252
    sleeves["SPY"] = rets["SPYSIM"] - EXPENSE_RATIOS["SPY"] / 100 / 252
    return sleeves.dropna()


def window(response: dict[str, Any]) -> str:
    hist = response["charts"]["history"][0]
    start = dt.datetime.fromtimestamp(hist[0], tz=dt.UTC).date()
    end = dt.datetime.fromtimestamp(hist[-1], tz=dt.UTC).date()
    years = (end - start).days / 365.25
    return f"{start} -> {end} ({years:.2f}y)"


def monthly_curve(rets: pd.DataFrame, allocation: list[tuple[float, str]]) -> pd.Series:
    weights = {ticker: pct / 100 for pct, ticker in allocation if pct > 0}
    frame = rets[list(weights)].dropna()
    dollars = {ticker: INITIAL * weight for ticker, weight in weights.items()}
    current_month = None
    values = []
    for date, row in frame.iterrows():
        total = sum(dollars.values())
        if current_month != date.to_period("M"):
            current_month = date.to_period("M")
            dollars = {ticker: total * weight for ticker, weight in weights.items()}
        for ticker in dollars:
            dollars[ticker] *= 1 + float(row[ticker])
        values.append(sum(dollars.values()))
    return pd.Series(values, index=frame.index)


def metrics(values: pd.Series) -> dict[str, Any]:
    years = (values.index[-1] - values.index[0]).days / 365.25
    rets = values.pct_change().dropna()
    cagr = (values.iloc[-1] / values.iloc[0]) ** (1 / years) - 1
    mdd = (values / values.cummax() - 1).min()
    sharpe = (252 ** 0.5) * rets.mean() / rets.std(ddof=0)
    return {"window": f"{values.index[0].date()} -> {values.index[-1].date()} ({years:.2f}y)", "cagr_pct": cagr * 100, "mdd_pct": mdd * 100, "sharpe": sharpe, "end_val": values.iloc[-1]}


def run_group(name: str, portfolios: list[dict[str, Any]], start_date: str, all_rets: pd.DataFrame) -> list[dict[str, Any]]:
    rets = all_rets.loc[start_date:].copy()
    rows = []
    for p in portfolios:
        curve = monthly_curve(rets, p["allocation_real"])
        rows.append({"group": name, "slug": p["slug"], **metrics(curve), "allocation_real": p["allocation_real"]})
    return rows


def write_summary(rows: list[dict[str, Any]]) -> None:
    groups = ["with_btc_2010", "no_btc_long"]
    lines = [
        "# Iter 055 — VBR/MTUM Proxy Satellite",
        "",
        "**Date:** 2026-05-03",
        "**Purpose:** test the satellite idea using long proxies: `VBRSIM` for SCV and `MTUMSIM` for the combined SPMO/FMTM momentum sleeve.",
        "",
    ]
    for group in groups:
        part = sorted([r for r in rows if r["group"] == group], key=lambda r: (-r["sharpe"], -r["cagr_pct"]))
        lines += [f"## {group}", "", f"Window: {part[0]['window']}", "", "| strategy | CAGR | MDD | Sharpe |", "|---|---:|---:|---:|"]
        for r in part:
            lines.append(f"| {r['slug']} | {r['cagr_pct']:.2f}% | {r['mdd_pct']:.2f}% | {r['sharpe']:.3f} |")
        lines.append("")
    lines += [
        "## Interpretation",
        "",
        "The 2010+ BTC-limited test answers whether the proposed 10% SCV / 10% momentum / 5% BTC satellite works when BTC history is included. The no-BTC long test answers whether VBRSIM/MTUMSIM improve B4 without relying on Bitcoin's adoption path.",
    ]
    (SCRIPT_DIR / "SUMMARY.md").write_text("\n".join(lines) + "\n")


def main() -> int:
    rets_with_btc = sleeve_returns(include_btc=True)
    rets_no_btc = sleeve_returns(include_btc=False)
    rows = []
    rows.extend(run_group("with_btc_2010", WITH_BTC, "2010-01-01", rets_with_btc))
    rows.extend(run_group("no_btc_long", NO_BTC, "2000-01-03", rets_no_btc))
    (SCRIPT_DIR / "unified_metrics.json").write_text(json.dumps(rows, indent=2))
    write_summary(rows)
    for r in sorted(rows, key=lambda r: (r["group"], -r["sharpe"], -r["cagr_pct"])):
        print(f"{r['group']:<15} {r['slug']:<32} {r['cagr_pct']:>6.2f}% {r['mdd_pct']:>8.2f}% {r['sharpe']:>6.3f} {r['window']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
