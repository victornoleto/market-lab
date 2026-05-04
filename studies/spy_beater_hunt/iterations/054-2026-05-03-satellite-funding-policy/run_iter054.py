#!/usr/bin/env python3
"""Iter 054 — funding policy for 25% factor/crypto satellite.

Tests the user's proposed satellite basket (10% AVUV, 5% SPMO, 5% FMTM,
5% BTC) against different funding policies. Factor sleeves are justified by
SCV/momentum premia `[ilmanen_expected_returns, ch.10-12]` and momentum
specific evidence `[stocks_on_the_move, ch.4]`, but the live comparison is
inception-limited and cannot override the anti-overfit gates
`[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import datetime as dt
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import pandas as pd


SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "testfolio_data"
API_BACKTEST = "https://testfol.io/api/backtest"
INITIAL = 10_000.0


EXPENSE_RATIOS = {
    "NTSX": 0.20,
    "GDE": 0.20,
    "RSST": 0.99,
    "ZROZ": 0.15,
    "BTC": 0.25,
    "AVUV": 0.25,
    "SPMO": 0.13,
    "FMTM": 0.15,
    "SPY": 0.0945,
    "SSO": 0.89,
}


def drag(allocation: list[tuple[float, str]]) -> float:
    return round(sum((pct / 100.0) * EXPENSE_RATIOS.get(ticker.upper(), 0.0) for pct, ticker in allocation), 4)


def portfolio(slug: str, allocation: list[tuple[float, str]]) -> dict[str, Any]:
    return {"slug": slug, "allocation_real": allocation, "drag_pct": drag(allocation)}


PORTFOLIOS = [
    portfolio("B4_base", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (25, "ZROZ")]),
    portfolio("B4_btc5", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (20, "ZROZ"), (5, "BTC")]),
    portfolio("sat_25_prorata_b4", [(18.75, "NTSX"), (18.75, "GDE"), (18.75, "RSST"), (18.75, "ZROZ"), (10, "AVUV"), (5, "SPMO"), (5, "FMTM"), (5, "BTC")]),
    portfolio("sat_25_from_zroz_only", [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (0, "ZROZ"), (10, "AVUV"), (5, "SPMO"), (5, "FMTM"), (5, "BTC")]),
    portfolio("sat_25_from_zroz_gde", [(25, "NTSX"), (15, "GDE"), (25, "RSST"), (10, "ZROZ"), (10, "AVUV"), (5, "SPMO"), (5, "FMTM"), (5, "BTC")]),
    portfolio("sat_25_from_zroz_ntsx", [(15, "NTSX"), (25, "GDE"), (25, "RSST"), (10, "ZROZ"), (10, "AVUV"), (5, "SPMO"), (5, "FMTM"), (5, "BTC")]),
    portfolio("sat_25_keep_rsst_20zroz", [(20, "NTSX"), (20, "GDE"), (25, "RSST"), (10, "ZROZ"), (10, "AVUV"), (5, "SPMO"), (5, "FMTM"), (5, "BTC")]),
    portfolio("sat_20_no_fmtm", [(20, "NTSX"), (20, "GDE"), (25, "RSST"), (15, "ZROZ"), (10, "AVUV"), (5, "SPMO"), (5, "BTC")]),
    portfolio("SPY", [(100, "SPY")]),
    portfolio("SSO", [(100, "SSO")]),
]


def payload(portfolios: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "start_date": "1800-01-01",
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
        "backtests": [{"invest_dividends": True, "rebalance_freq": "None", "rebalance_offset": 0, "allocation": {p["ticker"]: 100}, "drag": 0, "absolute_dev": 0, "relative_dev": 0} for p in portfolios],
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
            last_err = RuntimeError(f"HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')[:500]}")
            if exc.code == 429:
                time.sleep(30)
                continue
        except (urllib.error.URLError, TimeoutError) as exc:
            last_err = exc
        time.sleep(2 ** (i + 1))
    raise RuntimeError(last_err)


def window(response: dict[str, Any]) -> str:
    hist = response["charts"]["history"][0]
    start = dt.datetime.fromtimestamp(hist[0], tz=dt.UTC).date()
    end = dt.datetime.fromtimestamp(hist[-1], tz=dt.UTC).date()
    return f"{start} -> {end} ({(end - start).days / 365.25:.2f}y)"


def fetch_sleeves() -> pd.DataFrame:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tickers = ["NTSX", "GDE", "RSST", "ZROZ", "AVUV", "SPMO", "FMTM", "BTC", "SPY", "SSO"]
    frames = []
    for batch_id, start in enumerate(range(0, len(tickers), 5)):
        batch_tickers = tickers[start : start + 5]
        batch = [{"ticker": t} for t in batch_tickers]
        cache = DATA_DIR / f"sleeves_{batch_id}.json"
        if cache.exists():
            response = json.loads(cache.read_text())["response"]
        else:
            response = post(payload(batch))
            cache.write_text(json.dumps({"tickers": batch_tickers, "response": response}, indent=2))
        if response.get("errors"):
            raise RuntimeError(response["errors"])
        idx = pd.to_datetime(response["charts"]["history"][0], unit="s", utc=True).tz_convert(None)
        for i, ticker in enumerate(batch_tickers, start=1):
            frames.append(pd.Series(response["charts"]["history"][i], index=idx, name=ticker).astype(float))
    return pd.concat(frames, axis=1, join="inner").dropna()


def simulate(prices: pd.DataFrame, allocation: list[tuple[float, str]], er_drag: float) -> pd.Series:
    weights = {ticker: pct / 100.0 for pct, ticker in allocation if pct > 0}
    frame = prices[list(weights)].dropna()
    dollars = {ticker: INITIAL * weight for ticker, weight in weights.items()}
    current_month = None
    out = []
    daily_drag = er_drag / 100.0 / 252.0
    returns = frame.pct_change().fillna(0.0)
    for date, row in returns.iterrows():
        total = sum(dollars.values())
        if current_month != date.to_period("M"):
            current_month = date.to_period("M")
            dollars = {ticker: total * weight for ticker, weight in weights.items()}
        for ticker in dollars:
            dollars[ticker] *= 1 + float(row[ticker]) - daily_drag
        out.append(sum(dollars.values()))
    return pd.Series(out, index=frame.index)


def metrics(values: pd.Series) -> dict[str, float | str]:
    years = (values.index[-1] - values.index[0]).days / 365.25
    rets = values.pct_change().dropna()
    cagr = (values.iloc[-1] / values.iloc[0]) ** (1 / years) - 1
    mdd = (values / values.cummax() - 1).min()
    sharpe = (252 ** 0.5) * rets.mean() / rets.std(ddof=0)
    return {"window": f"{values.index[0].date()} -> {values.index[-1].date()} ({years:.2f}y)", "cagr_pct": cagr * 100, "mdd_pct": mdd * 100, "sharpe": sharpe, "end_val": values.iloc[-1]}


def main() -> int:
    prices = fetch_sleeves()
    rows = []
    for p in PORTFOLIOS:
        curve = simulate(prices, p["allocation_real"], p["drag_pct"])
        rows.append({"slug": p["slug"], **metrics(curve), "drag_pct": p["drag_pct"], "allocation_real": p["allocation_real"]})
    rows.sort(key=lambda r: (-r["sharpe"], -r["cagr_pct"]))
    (SCRIPT_DIR / "unified_metrics.json").write_text(json.dumps(rows, indent=2))
    write_summary(rows)
    for r in rows:
        print(f"{r['slug']:<28} {r['cagr_pct']:>6.2f}% {r['mdd_pct']:>8.2f}% {r['sharpe']:>6.3f} {r['window']}")
    return 0


def write_summary(rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Iter 054 — Satellite Funding Policy",
        "",
        "**Date:** 2026-05-03",
        "**Satellite basket:** 10% AVUV / 5% SPMO / 5% FMTM / 5% BTC.",
        "**Status:** live-window screen only; FMTM constrains common history to ~1.1y.",
        "",
        "## Ranking",
        "",
        "| strategy | window | CAGR | MDD | Sharpe |",
        "|---|---|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(f"| {r['slug']} | {r['window']} | {r['cagr_pct']:.2f}% | {r['mdd_pct']:.2f}% | {r['sharpe']:.3f} |")
    lines += [
        "",
        "## Interpretation",
        "",
        "Because FMTM forces the common window to 2025-03-20 -> 2026-05-01, this test cannot approve a permanent allocation. It can only compare funding mechanics in the current regime.",
        "",
        "Funding all 25% from ZROZ is too aggressive structurally: it removes most of the long-duration crash convexity. A pro-rata 75% B4 core is cleaner, but it cuts RSST and GDE, the two sleeves that make B4 different from a simple equity/factor bet.",
        "",
        "Preferred compromise if the user explicitly wants the 25% satellite: keep RSST at 25%, keep at least 10-12.5% ZROZ, and fund from NTSX/GDE/ZROZ rather than only from ZROZ.",
    ]
    (SCRIPT_DIR / "SUMMARY.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
