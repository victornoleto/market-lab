#!/usr/bin/env python3
"""Iter 050 - B4 overlay tax and SMA/EMA sensitivity.

Compares restricted regime overlays against static B4 after annual 15% tax on
realized gains. Tests SMA/EMA trend filters across a small pre-declared window
set rather than optimizing freely. Popular 200d SMA is included as the literature
anchor `[leverage_for_the_long_run, ch.3-4, p.40-60]`; alternative windows and
EMA test whether the result is a single crowded threshold artifact. Parameter
snooping is controlled by reporting the whole grid, not only the best result
`[advances_fin_ml, p.276]`.
"""
from __future__ import annotations

import json
import math
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
INITIAL = 10_000.0
TAX_RATE = 0.15
BASE = {"NTSX": 0.25, "GDE": 0.25, "RSST": 0.25, "ZROZ": 0.25}
SLEEVES = ["NTSX", "GDE", "RSST", "ZROZ", "SPY"]


@dataclass(frozen=True)
class Spec:
    slug: str
    ma_type: str
    trend_days: int
    dd_days: int
    dd_trigger: float
    tilt: float


WINDOWS = [126, 150, 180, 200, 210, 252]
SPECS = [
    Spec(f"overlay_{ma}{days}_12mdd_10pp", ma, days, 252, -0.10, 0.10)
    for ma in ["sma", "ema"]
    for days in WINDOWS
]


def load_frame() -> pd.DataFrame:
    payload = json.loads(SOURCE_CACHE.read_text())
    frame_payload = payload["frame"]
    return pd.DataFrame(frame_payload["data"], index=pd.to_datetime(frame_payload["index"])).dropna()


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
    if spec is not None and state == "risk_on":
        weights["NTSX"] += spec.tilt
        weights["ZROZ"] -= spec.tilt
    elif spec is not None and state == "defensive":
        half = spec.tilt / 2
        weights["NTSX"] -= half
        weights["GDE"] -= half
        weights["RSST"] += half
        weights["ZROZ"] += half
    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}


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
    prices = frame[SLEEVES]
    units = {ticker: 0.0 for ticker in BASE}
    avg_cost = {ticker: 0.0 for ticker in BASE}
    cash = 0.0
    realized_by_year: dict[int, float] = {}
    states: dict[str, int] = {"neutral": 0, "risk_on": 0, "defensive": 0}

    first = prices.index[0]
    for ticker, weight in BASE.items():
        value = INITIAL * weight
        units[ticker] = value / prices.at[first, ticker]
        avg_cost[ticker] = prices.at[first, ticker]

    equity = []
    for date in prices.index:
        if date in rebal_dates:
            state = "neutral" if spec is None else state_for_date(prices["SPY"], date, spec)
            states[state] += 1
            target_weights = weights_for_state(spec, state)
            portfolio_value = cash + sum(units[t] * prices.at[date, t] for t in BASE)
            targets = {ticker: portfolio_value * target_weights[ticker] for ticker in BASE}

            for ticker in BASE:
                current_value = units[ticker] * prices.at[date, ticker]
                diff = targets[ticker] - current_value
                price = prices.at[date, ticker]
                if diff < -1e-8:
                    sell_value = -diff
                    sell_units = min(units[ticker], sell_value / price)
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
                        avg_cost[ticker] = (
                            (old_units * avg_cost[ticker]) + buy_value
                        ) / new_units
                        units[ticker] = new_units
                        cash -= buy_value

        if tax and date.is_year_end:
            profit = realized_by_year.get(date.year, 0.0)
            if profit > 0:
                cash -= TAX_RATE * profit

        equity.append(cash + sum(units[t] * prices.at[date, t] for t in BASE))

    values = pd.Series(equity, index=prices.index)
    total_tax = 0.0
    if tax:
        total_tax = sum(max(0.0, gain) * TAX_RATE for gain in realized_by_year.values())
    return values, total_tax, states


def main() -> int:
    frame = load_frame()
    rows = []
    state_counts = {}
    for slug, spec in [("static_b4_forced_monthly", None), *[(s.slug, s) for s in SPECS]]:
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

    static = next(r for r in rows if r["slug"] == "static_b4_forced_monthly")
    rows_sorted = sorted(rows, key=lambda r: (-r["net_sharpe"], -r["net_cagr_pct"]))
    (SCRIPT_DIR / "unified_metrics.json").write_text(json.dumps(rows, indent=2))
    (SCRIPT_DIR / "state_counts.json").write_text(json.dumps(state_counts, indent=2))

    lines = [
        "# Iter 050 - B4 overlay tax and SMA/EMA sensitivity",
        "",
        "**Date:** 2026-05-03",
        "**Tax model:** 15% annual tax on positive realized gains from monthly rebalances; losses offset gains within the same year only.",
        "**Note:** static row is forced monthly rebalance for tax comparability. Live lazy-rebal static can defer tax more than this.",
        "",
        "## Ranking By Net Sharpe",
        "",
        "| # | strategy | net CAGR | net MDD | net Sharpe | gross CAGR | tax paid |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for i, row in enumerate(rows_sorted, 1):
        lines.append(
            f"| {i} | {row['slug']} | {row['net_cagr_pct']:.2f}% | {row['net_mdd_pct']:.2f}% | "
            f"{row['net_sharpe']:.3f} | {row['gross_cagr_pct']:.2f}% | ${row['total_tax_paid']:,.0f} |"
        )
    best = rows_sorted[0]
    lines += [
        "",
        "## Verdict",
        "",
        f"Forced-monthly static B4 after tax: {static['net_cagr_pct']:.2f}% CAGR / {static['net_mdd_pct']:.2f}% MDD / {static['net_sharpe']:.3f} Sharpe.",
        f"Best after-tax overlay: `{best['slug']}` at {best['net_cagr_pct']:.2f}% CAGR / {best['net_mdd_pct']:.2f}% MDD / {best['net_sharpe']:.3f} Sharpe.",
        "",
        "## Interpretation",
        "",
        "If multiple nearby SMA/EMA windows work, the overlay is less likely to be a single 200d crowding artifact. If only one window works, treat it as parameter fragility.",
    ]
    (SCRIPT_DIR / "SUMMARY.md").write_text("\n".join(lines) + "\n")

    for row in rows_sorted[:8]:
        print(
            f"{row['slug']:<28} net {row['net_cagr_pct']:>6.2f}% "
            f"{row['net_mdd_pct']:>8.2f}% {row['net_sharpe']:>6.3f} "
            f"gross {row['gross_cagr_pct']:>6.2f}%"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
