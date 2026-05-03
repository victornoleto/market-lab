#!/usr/bin/env python3
"""Iter 051 - LETF risk-on sleeves on B4 overlay.

Tests whether a SSO/QLD/UPRO/TQQQ sleeve during risk-on regimes improves
after-tax performance versus B4 static and the no-LETF overlay. The grid is kept
pre-declared to avoid free optimization/data snooping
`[advances_fin_ml, p.208-211]`. Trend gating follows the Gayed/LRS rationale
for using long moving averages with leveraged equity `[leverage_for_the_long_run,
ch.3-4, p.40-60]`.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import time
import urllib.error
import urllib.request
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).parent
SOURCE_CACHE = (
    SCRIPT_DIR.parent
    / "049-2026-05-03-b4-no-btc-regime-overlay-fallback"
    / "testfolio_data"
    / "single_sleeves.json"
)
DATA_DIR = SCRIPT_DIR / "testfolio_data"
API_BACKTEST = "https://testfol.io/api/backtest"
INITIAL = 10_000.0
TAX_RATE = 0.15

BASE = {"NTSX": 0.25, "GDE": 0.25, "RSST": 0.25, "ZROZ": 0.25}
CORE_SLEEVES = ["NTSX", "GDE", "RSST", "ZROZ", "SPY"]
LETF_SLEEVES = ["SSO", "QLD", "UPRO", "TQQQ"]
ALL_SLEEVES = CORE_SLEEVES + LETF_SLEEVES

EXPENSE_RATIOS = {
    "SPY": 0.0945,
    "NTSX": 0.20,
    "GDE": 0.20,
    "RSST": 0.99,
    "ZROZ": 0.15,
    "SSO": 0.89,
    "QLD": 0.95,
    "UPRO": 0.91,
    "TQQQ": 0.86,
}

MAPPINGS = {
    "NTSX": [("SPYSIM", 0.90), ("IEFSIM", 0.60), ("CASHX", -0.50)],
    "RSST": [
        ("SPYSIM", 1.00),
        ("DBMFSIM?FB=KMLMSIM", 0.70),
        ("KMLMSIM", 0.30),
        ("CASHX?E=-2", -1.00),
    ],
    "SPY": [("SPYSIM", 1.0)],
    "SSO": [("SPYSIM?L=2&E=0.89", 1.0)],
    "UPRO": [("SPYSIM?L=3&E=0.91", 1.0)],
    "QLD": [("QQQSIM?L=2&E=0.95", 1.0)],
    "TQQQ": [("QQQSIM?L=3&E=0.84", 1.0)],
}


@dataclass(frozen=True)
class Spec:
    slug: str
    ma_type: str
    trend_days: int
    dd_days: int
    dd_trigger: float
    tilt: float
    letf: str | None
    letf_weight: float
    funding: str


BASE_OVERLAYS = [
    Spec("overlay_sma150_12mdd_10pp", "sma", 150, 252, -0.10, 0.10, None, 0.0, "none"),
    Spec("overlay_sma200_12mdd_10pp", "sma", 200, 252, -0.10, 0.10, None, 0.0, "none"),
]

LETF_SPECS = [
    Spec(
        f"{letf.lower()}_{int(weight * 100)}_{ma}{days}_from_{funding}",
        ma,
        days,
        252,
        -0.10,
        0.10,
        letf,
        weight,
        funding,
    )
    for letf in LETF_SLEEVES
    for weight in [x / 100 for x in range(5, 55, 5)]
    for ma in ["sma", "ema"]
    for days in [150, 200]
    for funding in ["ZROZ", "NTSX"]
]

SPECS = BASE_OVERLAYS + LETF_SPECS


def expand(weight_pct: float, ticker: str) -> list[tuple[str, float]]:
    if ticker in MAPPINGS:
        return [(token, weight_pct * mult) for token, mult in MAPPINGS[ticker]]
    return [(f"{ticker}SIM", weight_pct)]


def decompose(allocation: list[tuple[float, str]]) -> dict[str, float]:
    agg: defaultdict[str, float] = defaultdict(float)
    for pct, ticker in allocation:
        for token, weight in expand(pct, ticker.upper()):
            agg[token] += weight
    return {k: round(v, 4) for k, v in agg.items() if abs(v) > 1e-6}


def post(data: dict) -> dict:
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
            last_err = RuntimeError(
                f"HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')[:1000]}"
            )
        except (urllib.error.URLError, TimeoutError) as exc:
            last_err = exc
        time.sleep(2 ** (i + 1))
    raise RuntimeError(last_err)


def api_payload(portfolios: list[dict]) -> dict:
    return {
        "start_date": "1987-01-01",
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
                "allocation": p["allocation"],
                "drag": p["drag"],
                "absolute_dev": 0,
                "relative_dev": 0,
            }
            for p in portfolios
        ],
    }


def load_core_frame() -> pd.DataFrame:
    payload = json.loads(SOURCE_CACHE.read_text())
    frame_payload = payload["frame"]
    return pd.DataFrame(frame_payload["data"], index=pd.to_datetime(frame_payload["index"])).dropna()


def fetch_letfs() -> pd.DataFrame:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cache = DATA_DIR / "letf_sleeves.json"
    if cache.exists():
        payload = json.loads(cache.read_text())
        frame_payload = payload["frame"]
        return pd.DataFrame(frame_payload["data"], index=pd.to_datetime(frame_payload["index"])).dropna()
    portfolios = [
        {
            "slug": ticker,
            "allocation": decompose([(100, ticker)]),
            "drag": 0.0,
        }
        for ticker in LETF_SLEEVES
    ]
    response = post(api_payload(portfolios))
    if response.get("errors"):
        raise RuntimeError(response["errors"])
    history = response["charts"]["history"]
    dates = [dt.datetime.fromtimestamp(ts, tz=dt.UTC).date() for ts in history[0]]
    frame = pd.DataFrame(
        {p["slug"]: history[i + 1] for i, p in enumerate(portfolios)},
        index=pd.to_datetime(dates),
    ).dropna()
    cache.write_text(
        json.dumps(
            {
                "portfolios": portfolios,
                "frame": {
                    "index": [str(x.date()) for x in frame.index],
                    "data": {col: frame[col].tolist() for col in frame.columns},
                },
            },
            indent=2,
        )
    )
    return frame


def load_frame() -> pd.DataFrame:
    return pd.concat([load_core_frame(), fetch_letfs()], axis=1, sort=False).dropna()


def rebalance_dates(index: pd.DatetimeIndex) -> set[pd.Timestamp]:
    months = pd.Series(index=index, data=index.to_period("M"))
    return set(months.groupby(months).head(1).index)


def moving_average(spy: pd.Series, loc: int, spec: Spec) -> float:
    trailing = spy.iloc[loc - spec.trend_days : loc]
    if spec.ma_type == "ema":
        return float(trailing.ewm(span=spec.trend_days, adjust=False).mean().iloc[-1])
    return float(trailing.mean())


def state_for_date(spy: pd.Series, date: pd.Timestamp, spec: Spec) -> str:
    loc = spy.index.get_loc(date)
    if loc < max(spec.trend_days, spec.dd_days):
        return "neutral"
    price_yesterday = spy.iloc[loc - 1]
    ma = moving_average(spy, loc, spec)
    dd_window = spy.iloc[loc - spec.dd_days : loc]
    trailing_dd = price_yesterday / dd_window.max() - 1
    if price_yesterday > ma and trailing_dd > -0.05:
        return "risk_on"
    if price_yesterday < ma or trailing_dd <= spec.dd_trigger:
        return "defensive"
    return "neutral"


def weights_for_state(spec: Spec | None, state: str) -> dict[str, float]:
    weights = dict(BASE)
    if spec is None:
        return weights
    if state == "risk_on":
        weights["NTSX"] += spec.tilt
        weights["ZROZ"] -= spec.tilt
        if spec.letf:
            weights[spec.letf] = spec.letf_weight
            weights[spec.funding] -= spec.letf_weight
    elif state == "defensive":
        half = spec.tilt / 2
        weights["NTSX"] -= half
        weights["GDE"] -= half
        weights["RSST"] += half
        weights["ZROZ"] += half
    total = sum(weights.values())
    return {k: v / total for k, v in weights.items() if abs(v) > 1e-12}


def metrics(values: pd.Series) -> dict[str, float | str]:
    years = (values.index[-1] - values.index[0]).days / 365.25
    rets = values.pct_change().dropna()
    cagr = (values.iloc[-1] / values.iloc[0]) ** (1 / years) - 1
    mdd = (values / values.cummax() - 1).min()
    sharpe = math.sqrt(252) * rets.mean() / rets.std(ddof=0)
    return {
        "window": f"{values.index[0].date()} -> {values.index[-1].date()} ({years:.2f}y)",
        "cagr_pct": cagr * 100,
        "mdd_pct": mdd * 100,
        "sharpe": sharpe,
        "end_val": values.iloc[-1],
    }


def simulate(frame: pd.DataFrame, spec: Spec | None, tax: bool) -> tuple[pd.Series, float, dict[str, int]]:
    rebal_dates = rebalance_dates(frame.index)
    units = {ticker: 0.0 for ticker in ALL_SLEEVES}
    avg_cost = {ticker: 0.0 for ticker in ALL_SLEEVES}
    cash = 0.0
    realized_by_year: dict[int, float] = {}
    states = {"neutral": 0, "risk_on": 0, "defensive": 0}
    first = frame.index[0]
    for ticker, weight in BASE.items():
        value = INITIAL * weight
        units[ticker] = value / frame.at[first, ticker]
        avg_cost[ticker] = frame.at[first, ticker]
    equity = []
    for date in frame.index:
        if date in rebal_dates:
            state = "neutral" if spec is None else state_for_date(frame["SPY"], date, spec)
            states[state] += 1
            target_weights = weights_for_state(spec, state)
            portfolio_value = cash + sum(units[t] * frame.at[date, t] for t in ALL_SLEEVES)
            targets = {ticker: portfolio_value * target_weights.get(ticker, 0.0) for ticker in ALL_SLEEVES}
            for ticker in ALL_SLEEVES:
                current_value = units[ticker] * frame.at[date, ticker]
                diff = targets[ticker] - current_value
                price = frame.at[date, ticker]
                if diff < -1e-8:
                    sell_units = min(units[ticker], -diff / price)
                    proceeds = sell_units * price
                    gain = (price - avg_cost[ticker]) * sell_units
                    units[ticker] -= sell_units
                    cash += proceeds
                    if tax:
                        realized_by_year[date.year] = realized_by_year.get(date.year, 0.0) + gain
                elif diff > 1e-8:
                    buy_value = min(diff, cash)
                    if buy_value > 0:
                        buy_units = buy_value / price
                        old_units = units[ticker]
                        new_units = old_units + buy_units
                        avg_cost[ticker] = ((old_units * avg_cost[ticker]) + buy_value) / new_units
                        units[ticker] = new_units
                        cash -= buy_value
        if tax and date.is_year_end:
            profit = realized_by_year.get(date.year, 0.0)
            if profit > 0:
                cash -= TAX_RATE * profit
        equity.append(cash + sum(units[t] * frame.at[date, t] for t in ALL_SLEEVES))
    values = pd.Series(equity, index=frame.index)
    total_tax = sum(max(0.0, gain) * TAX_RATE for gain in realized_by_year.values()) if tax else 0.0
    return values, total_tax, states


def main() -> int:
    frame = load_frame()
    rows = []
    state_counts = {}
    run_specs: list[tuple[str, Spec | None]] = [("static_b4_forced_monthly", None)] + [
        (s.slug, s) for s in SPECS
    ]
    for slug, spec in run_specs:
        gross, _, states = simulate(frame, spec, tax=False)
        net, total_tax, states_tax = simulate(frame, spec, tax=True)
        gross_m = metrics(gross)
        net_m = metrics(net)
        rows.append(
            {
                "slug": slug,
                "window": net_m["window"],
                "gross_cagr_pct": gross_m["cagr_pct"],
                "gross_mdd_pct": gross_m["mdd_pct"],
                "gross_sharpe": gross_m["sharpe"],
                "net_cagr_pct": net_m["cagr_pct"],
                "net_mdd_pct": net_m["mdd_pct"],
                "net_sharpe": net_m["sharpe"],
                "net_end_val": net_m["end_val"],
                "total_tax_paid": total_tax,
            }
        )
        state_counts[slug] = states_tax or states
    rows_sorted = sorted(rows, key=lambda r: (-r["net_sharpe"], -r["net_cagr_pct"]))
    letf_rows = [
        r
        for r in rows
        if any(r["slug"].startswith(prefix) for prefix in ("sso_", "qld_", "upro_", "tqqq_"))
    ]
    letf_by_cagr = sorted(letf_rows, key=lambda r: (-r["net_cagr_pct"], r["net_mdd_pct"]))
    (SCRIPT_DIR / "unified_metrics.json").write_text(json.dumps(rows, indent=2))
    (SCRIPT_DIR / "state_counts.json").write_text(json.dumps(state_counts, indent=2))

    lines = [
        "# Iter 051 - LETF risk-on overlay",
        "",
        "**Date:** 2026-05-03",
        "**Tax model:** 15% annual tax on positive realized gains from monthly rebalances.",
        "**Grid:** SSO/QLD/UPRO/TQQQ, 5-50% in 5pp steps, SMA/EMA 150/200, funded from ZROZ or NTSX only in risk-on state.",
        "",
        "## Top 20 By Net Sharpe",
        "",
        "| # | strategy | net CAGR | net MDD | net Sharpe | gross CAGR | tax paid |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for i, row in enumerate(rows_sorted[:20], 1):
        lines.append(
            f"| {i} | {row['slug']} | {row['net_cagr_pct']:.2f}% | {row['net_mdd_pct']:.2f}% | "
            f"{row['net_sharpe']:.3f} | {row['gross_cagr_pct']:.2f}% | ${row['total_tax_paid']:,.0f} |"
        )
    lines += [
        "",
        "## Top 10 LETF Rows By Net CAGR",
        "",
        "| # | strategy | net CAGR | net MDD | net Sharpe | gross CAGR | tax paid |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for i, row in enumerate(letf_by_cagr[:10], 1):
        lines.append(
            f"| {i} | {row['slug']} | {row['net_cagr_pct']:.2f}% | {row['net_mdd_pct']:.2f}% | "
            f"{row['net_sharpe']:.3f} | {row['gross_cagr_pct']:.2f}% | ${row['total_tax_paid']:,.0f} |"
        )
    lines += [
        "",
        "## Best Row Per LETF",
        "",
        "| LETF | best by Sharpe | net CAGR | net MDD | net Sharpe | best by CAGR | net CAGR | net MDD | net Sharpe |",
        "|---|---|---:|---:|---:|---|---:|---:|---:|",
    ]
    for letf in LETF_SLEEVES:
        subset = [r for r in letf_rows if r["slug"].startswith(f"{letf.lower()}_")]
        by_sharpe = max(subset, key=lambda r: (r["net_sharpe"], r["net_cagr_pct"]))
        by_cagr = max(subset, key=lambda r: r["net_cagr_pct"])
        lines.append(
            f"| {letf} | `{by_sharpe['slug']}` | {by_sharpe['net_cagr_pct']:.2f}% | "
            f"{by_sharpe['net_mdd_pct']:.2f}% | {by_sharpe['net_sharpe']:.3f} | "
            f"`{by_cagr['slug']}` | {by_cagr['net_cagr_pct']:.2f}% | "
            f"{by_cagr['net_mdd_pct']:.2f}% | {by_cagr['net_sharpe']:.3f} |"
        )
    static = next(r for r in rows if r["slug"] == "static_b4_forced_monthly")
    no_letf_best = next(r for r in rows if r["slug"] == "overlay_sma150_12mdd_10pp")
    best_letf_sharpe = max(letf_rows, key=lambda r: (r["net_sharpe"], r["net_cagr_pct"]))
    best_letf_cagr = letf_by_cagr[0]
    letf_passes = [
        r
        for r in letf_rows
        if r["net_sharpe"] > no_letf_best["net_sharpe"] and r["net_mdd_pct"] >= no_letf_best["net_mdd_pct"]
    ]
    best = rows_sorted[0]
    lines += [
        "",
        "## Verdict",
        "",
        f"Static forced-monthly B4: {static['net_cagr_pct']:.2f}% / {static['net_mdd_pct']:.2f}% / {static['net_sharpe']:.3f}.",
        f"Best no-LETF overlay: `{no_letf_best['slug']}` at {no_letf_best['net_cagr_pct']:.2f}% / {no_letf_best['net_mdd_pct']:.2f}% / {no_letf_best['net_sharpe']:.3f}.",
        f"Best grid row by net Sharpe: `{best['slug']}` at {best['net_cagr_pct']:.2f}% / {best['net_mdd_pct']:.2f}% / {best['net_sharpe']:.3f}.",
        f"Best LETF by net Sharpe: `{best_letf_sharpe['slug']}` at {best_letf_sharpe['net_cagr_pct']:.2f}% / {best_letf_sharpe['net_mdd_pct']:.2f}% / {best_letf_sharpe['net_sharpe']:.3f}.",
        f"Best LETF by net CAGR: `{best_letf_cagr['slug']}` at {best_letf_cagr['net_cagr_pct']:.2f}% / {best_letf_cagr['net_mdd_pct']:.2f}% / {best_letf_cagr['net_sharpe']:.3f}.",
        "",
        f"LETF rows beating the no-LETF overlay on both after-tax Sharpe and MDD: {len(letf_passes)}.",
        "Conclusion: reject LETF sleeves for the balanced live candidate. The expanded 5-50% grid buys higher CAGR by accepting materially worse drawdown and lower risk-adjusted return versus the cleaner no-LETF overlay; this is a return-seeking variant only, not a core improvement.",
    ]
    (SCRIPT_DIR / "SUMMARY.md").write_text("\n".join(lines) + "\n")

    for row in rows_sorted[:12]:
        print(
            f"{row['slug']:<36} net {row['net_cagr_pct']:>6.2f}% "
            f"{row['net_mdd_pct']:>8.2f}% {row['net_sharpe']:>6.3f} gross {row['gross_cagr_pct']:>6.2f}%"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
