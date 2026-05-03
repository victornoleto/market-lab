#!/usr/bin/env python3
"""Iter 048 - restricted regime overlay for B4 + 5% BTC.

Tests the user's walk-forward idea without free weight optimization. Previous
iter 043 showed rolling max-Sharpe weight fitting creates 0/100 corner solutions
and worse OOS Sharpe. Here the only allowed changes are pre-defined +/-5pp or
/-10pp tilts based on SPY trend/drawdown state.

Parameter choices are deliberately few and cited:
- 200-day / 10-month trend is the canonical long-term trend filter family used
  by Gayed-style leverage timing `[leverage_for_the_long_run, ch.3-4, p.40-60]`.
- Avoiding optimizer-selected weights follows overfit warnings from Lopez de
  Prado and Chan `[advances_fin_ml, p.208-211]`, `[machine_trading, p.83-84]`.
- A walk-forward test is required before trusting any optimized/adaptive rule
  `[eval_opt_strategies, p.1, p.237]`.
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

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "testfolio_data"
PLOT_DIR = SCRIPT_DIR / "plots"
API_BACKTEST = "https://testfol.io/api/backtest"
INITIAL = 10_000.0

EXPENSE_RATIOS = {
    "SPY": 0.0945,
    "NTSX": 0.20,
    "GDE": 0.20,
    "RSST": 0.99,
    "ZROZ": 0.15,
    "BTC": 0.25,
}

MAPPINGS = {
    "NTSX": [("SPYSIM", 0.90), ("IEFSIM", 0.60), ("CASHX", -0.50)],
    "RSST": [("SPYSIM", 1.00), ("DBMFSIM", 0.70), ("KMLMSIM", 0.30), ("CASHX?E=-2", -1.00)],
    "BTC": [("BTCSIM", 1.0)],
    "SPY": [("SPYSIM", 1.0)],
}

SLEEVES = ["NTSX", "GDE", "RSST", "ZROZ", "BTC", "SPY"]
BASE = {"NTSX": 0.25, "GDE": 0.25, "RSST": 0.25, "ZROZ": 0.20, "BTC": 0.05}


@dataclass(frozen=True)
class OverlaySpec:
    slug: str
    trend_days: int
    drawdown_days: int
    dd_trigger: float
    tilt: float


SPECS = [
    OverlaySpec("overlay_200d_12mdd_5pp", 200, 252, -0.10, 0.05),
    OverlaySpec("overlay_200d_24mdd_5pp", 200, 504, -0.15, 0.05),
    OverlaySpec("overlay_10m_12mdd_5pp", 210, 252, -0.10, 0.05),
    OverlaySpec("overlay_200d_12mdd_10pp", 200, 252, -0.10, 0.10),
]


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


def drag(allocation: dict[str, float]) -> float:
    return sum(allocation[ticker] * EXPENSE_RATIOS.get(ticker, 0.0) for ticker in allocation)


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


def fetch_sleeves() -> pd.DataFrame:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cache = DATA_DIR / "single_sleeves.json"
    if cache.exists():
        payload = json.loads(cache.read_text())
    else:
        all_portfolios = []
        all_frames = []
        for ticker in SLEEVES:
            all_portfolios.append(
                {
                    "slug": ticker,
                    "allocation": decompose([(100, ticker)]),
                    "drag": EXPENSE_RATIOS.get(ticker, 0.0),
                }
            )
        for batch_i in range(0, len(all_portfolios), 5):
            portfolios = all_portfolios[batch_i : batch_i + 5]
            response = post(
                {
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
                            "allocation": p["allocation"],
                            "drag": p["drag"],
                            "absolute_dev": 0,
                            "relative_dev": 0,
                        }
                        for p in portfolios
                    ],
                }
            )
            history = response["charts"]["history"]
            dates = [dt.datetime.fromtimestamp(ts, tz=dt.UTC).date() for ts in history[0]]
            data = {p["slug"]: history[i + 1] for i, p in enumerate(portfolios)}
            all_frames.append(pd.DataFrame(data, index=pd.to_datetime(dates)))
        frame = pd.concat(all_frames, axis=1).dropna()
        payload = {
            "portfolios": all_portfolios,
            "frame": {
                "index": [str(x.date()) for x in frame.index],
                "data": {col: frame[col].tolist() for col in frame.columns},
            },
        }
        cache.write_text(json.dumps(payload, indent=2))
    if "frame" in payload:
        frame_payload = payload["frame"]
        frame = pd.DataFrame(
            frame_payload["data"], index=pd.to_datetime(frame_payload["index"])
        ).dropna()
    else:
        history = payload["response"]["charts"]["history"]
        dates = [dt.datetime.fromtimestamp(ts, tz=dt.UTC).date() for ts in history[0]]
        data = {}
        for i, p in enumerate(payload["portfolios"]):
            data[p["slug"]] = history[i + 1]
        frame = pd.DataFrame(data, index=pd.to_datetime(dates)).dropna()
    return frame


def rebalance_dates(index: pd.DatetimeIndex) -> set[pd.Timestamp]:
    months = pd.Series(index=index, data=index.to_period("M"))
    return set(months.groupby(months).head(1).index)


def weights_for_state(spec: OverlaySpec, state: str) -> dict[str, float]:
    weights = dict(BASE)
    if state == "risk_on":
        weights["NTSX"] += spec.tilt
        weights["ZROZ"] -= spec.tilt
    elif state == "defensive":
        half = spec.tilt / 2
        weights["NTSX"] -= half
        weights["BTC"] = max(0.025, weights["BTC"] - half)
        weights["RSST"] += half
        weights["ZROZ"] += half
    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}


def state_for_date(spy: pd.Series, date: pd.Timestamp, spec: OverlaySpec) -> str:
    loc = spy.index.get_loc(date)
    if loc < max(spec.trend_days, spec.drawdown_days):
        return "neutral"
    trailing = spy.iloc[loc - spec.trend_days : loc]
    dd_window = spy.iloc[loc - spec.drawdown_days : loc]
    price_yesterday = spy.iloc[loc - 1]
    sma = trailing.mean()
    trailing_dd = price_yesterday / dd_window.max() - 1
    if price_yesterday > sma and trailing_dd > -0.05:
        return "risk_on"
    if price_yesterday < sma or trailing_dd <= spec.dd_trigger:
        return "defensive"
    return "neutral"


def simulate(frame: pd.DataFrame, spec: OverlaySpec | None = None) -> tuple[pd.Series, pd.DataFrame]:
    returns = frame[SLEEVES].pct_change().fillna(0.0)
    rebal_dates = rebalance_dates(frame.index)
    holdings = {ticker: INITIAL * BASE[ticker] for ticker in BASE}
    equity = []
    weight_rows = []
    current_weights = dict(BASE)
    for date in frame.index:
        if date in rebal_dates:
            state = "neutral" if spec is None else state_for_date(frame["SPY"], date, spec)
            current_weights = dict(BASE) if spec is None else weights_for_state(spec, state)
            total = sum(holdings.values())
            holdings = {ticker: total * current_weights[ticker] for ticker in BASE}
            weight_rows.append({"date": date, "state": state, **current_weights})
        for ticker in BASE:
            holdings[ticker] *= 1 + returns.at[date, ticker]
        daily_drag = drag(current_weights) / 100.0 / 252.0
        total_after_returns = sum(holdings.values())
        total_after_drag = total_after_returns * (1 - daily_drag)
        scale = total_after_drag / total_after_returns if total_after_returns else 1.0
        holdings = {ticker: value * scale for ticker, value in holdings.items()}
        equity.append(total_after_drag)
    return pd.Series(equity, index=frame.index), pd.DataFrame(weight_rows).set_index("date")


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


def plot(equities: dict[str, pd.Series]) -> None:
    PLOT_DIR.mkdir(exist_ok=True)
    frame = pd.DataFrame(equities)
    normalized = frame / frame.iloc[0] * INITIAL
    fig, ax = plt.subplots(figsize=(11, 6))
    for col in normalized.columns:
        normalized[col].plot(ax=ax, linewidth=2 if col == "static_b4_btc5" else 1.5, label=col)
    ax.set_yscale("log")
    ax.set_title("Iter 048: Static B4+5% BTC vs restricted overlays")
    ax.set_ylabel("Portfolio value, log scale")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "equity_overlay.png", dpi=160)
    plt.close(fig)

    dd = frame / frame.cummax() - 1
    fig, ax = plt.subplots(figsize=(11, 5))
    for col in dd.columns:
        (dd[col] * 100).plot(ax=ax, linewidth=2 if col == "static_b4_btc5" else 1.5, label=col)
    ax.set_title("Iter 048: Drawdown")
    ax.set_ylabel("Drawdown (%)")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "drawdown_overlay.png", dpi=160)
    plt.close(fig)


def write_summary(rows: list[dict], state_counts: dict[str, dict[str, int]]) -> None:
    rows_sorted = sorted(rows, key=lambda r: (-r["sharpe"], -r["cagr_pct"]))
    static = next(r for r in rows if r["slug"] == "static_b4_btc5")
    lines = [
        "# Iter 048 - Restricted regime overlay on B4 + 5% BTC",
        "",
        "**Date:** 2026-05-03",
        "**Purpose:** test whether a simple walk-forward/regime overlay improves the selected live candidate without free weight optimization.",
        "**Method:** monthly rebalance, saved/fetched testfol.io single-sleeve curves, SPY trend/drawdown state, pre-defined +/-5pp or +/-10pp tilts.",
        "",
        "## Ranking By Sharpe",
        "",
        "| # | strategy | window | CAGR | MDD | Sharpe | end value |",
        "|---:|---|---|---:|---:|---:|---:|",
    ]
    for i, row in enumerate(rows_sorted, 1):
        lines.append(
            f"| {i} | {row['slug']} | {row['window']} | {row['cagr_pct']:.2f}% | "
            f"{row['mdd_pct']:.2f}% | {row['sharpe']:.3f} | ${row['end_val']:,.0f} |"
        )
    lines += [
        "",
        "## Verdict",
        "",
        f"Static B4+5% BTC baseline: {static['cagr_pct']:.2f}% CAGR / {static['mdd_pct']:.2f}% MDD / {static['sharpe']:.3f} Sharpe.",
    ]
    winners = [
        r
        for r in rows
        if r["slug"] != "static_b4_btc5"
        and r["cagr_pct"] > static["cagr_pct"]
        and abs(r["mdd_pct"]) <= abs(static["mdd_pct"])
        and r["sharpe"] >= static["sharpe"]
    ]
    if winners:
        lines.append("At least one overlay strictly improves CAGR without worse MDD and without lower Sharpe.")
    else:
        lines.append("No overlay strictly improves CAGR while keeping MDD and Sharpe at least as good as static.")
    lines += [
        "",
        "## Regime Counts",
        "",
        "| strategy | neutral | risk_on | defensive |",
        "|---|---:|---:|---:|",
    ]
    for slug, counts in state_counts.items():
        lines.append(
            f"| {slug} | {counts.get('neutral', 0)} | {counts.get('risk_on', 0)} | {counts.get('defensive', 0)} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "This is an overlay test, not a new live recommendation unless it beats the static allocation on the full trade-off. Prior iter 043 already showed unrestricted walk-forward optimization overfits weights; this iter only tests small, pre-defined regime tilts.",
    ]
    (SCRIPT_DIR / "SUMMARY.md").write_text("\n".join(lines) + "\n")


def main() -> int:
    frame = fetch_sleeves()
    equities: dict[str, pd.Series] = {}
    rows: list[dict] = []
    state_counts: dict[str, dict[str, int]] = {}

    static_equity, static_weights = simulate(frame)
    equities["static_b4_btc5"] = static_equity
    rows.append({"slug": "static_b4_btc5", **metrics(static_equity)})
    state_counts["static_b4_btc5"] = static_weights["state"].value_counts().to_dict()

    for spec in SPECS:
        equity, weights = simulate(frame, spec)
        equities[spec.slug] = equity
        rows.append({"slug": spec.slug, **metrics(equity)})
        state_counts[spec.slug] = weights["state"].value_counts().to_dict()

    plot(equities)
    (SCRIPT_DIR / "unified_metrics.json").write_text(json.dumps(rows, indent=2))
    (SCRIPT_DIR / "state_counts.json").write_text(json.dumps(state_counts, indent=2))
    write_summary(rows, state_counts)
    for row in sorted(rows, key=lambda r: (-r["sharpe"], -r["cagr_pct"])):
        print(f"{row['slug']:<28} {row['cagr_pct']:>6.2f}% {row['mdd_pct']:>8.2f}% {row['sharpe']:>6.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
