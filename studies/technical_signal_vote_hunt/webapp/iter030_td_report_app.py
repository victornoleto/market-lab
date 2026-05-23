"""Interactive web report for iter030 T/D sensitivity.

This is a dependency-free local webapp for inspecting the final T/D sensitivity
report interactively. It serves a small HTML/JS frontend and JSON endpoints from
the Python standard library, so it does not change the project runtime deps. The
analytics remain research-only: PBO/DSR failures still block promotion
`[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import numpy as np
import pandas as pd

from market_lab.backtest.data.testfolio_loader import load_testfolio_series
from studies.technical_signal_vote_hunt.core import daily_returns, sma
from studies.technical_signal_vote_hunt.runners.run_iter030_td_sensitivity import (
    _comparison_returns,
    _gene_with_td,
    _load_module,
    _prepare_context,
    _returns_for_gene,
    ITER030_BACKTEST,
)
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import _metrics_row_np


TRADING_DAYS_PER_YEAR = 252
DEFAULT_PORT = 8765
WINDOW_YEARS = (3, 5, 10, 15, 20)
ALIASES = {
    "iter030 T20D120 candidate": "T20D120",
    "T20D90 balanced sensitivity": "T20D90",
    "iter030 canonical": "iter030",
    "T3d-K2 canonical": "T3d-K2",
    "Stage3 shared QLD": "S3 QLD",
    "Stage3 shared TQQQ": "S3 TQQQ",
    "Stage4-inside iter030 turbo": "S4 inside",
    "Stage4 QLD base vote": "S4 QLD",
    "Stage4 TQQQ base vote": "S4 TQQQ",
    "LRS 200d SSO": "LRS SSO",
    "LRS 200d UPRO": "LRS UPRO",
    "LRS 200d QLD": "LRS QLD",
    "LRS 200d TQQQ": "LRS TQQQ",
    "QQQ buy_hold": "QQQ B&H",
    "SPY buy_hold": "SPY B&H",
}


@dataclass(frozen=True)
class AppState:
    returns: pd.DataFrame
    start: str
    end: str


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Serve interactive iter030 T/D report")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    state = _load_state()
    handler = _handler_factory(state)
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"serving http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopping", flush=True)
    finally:
        server.server_close()
    return 0


def _load_state() -> AppState:
    ctx = _prepare_context(_load_module(ITER030_BACKTEST, "iter030_td_webapp"))
    returns = _comparison_returns(ctx)
    returns["T20D90 balanced sensitivity"] = _returns_for_gene(ctx, _gene_with_td(20, 90))
    returns = pd.concat([returns, _lrs_200d_returns()], axis=1, sort=False)
    ordered = [
        "iter030 T20D120 candidate",
        "T20D90 balanced sensitivity",
        "iter030 canonical",
        "T3d-K2 canonical",
        "Stage3 shared QLD",
        "Stage3 shared TQQQ",
        "Stage4-inside iter030 turbo",
        "Stage4 QLD base vote",
        "Stage4 TQQQ base vote",
        "LRS 200d SSO",
        "LRS 200d UPRO",
        "LRS 200d QLD",
        "LRS 200d TQQQ",
        "QQQ buy_hold",
        "SPY buy_hold",
    ]
    returns = returns[[c for c in ordered if c in returns.columns]].loc[lambda x: x.notna().all(axis=1)]
    return AppState(
        returns=returns,
        start=str(returns.index.min().date()),
        end=str(returns.index.max().date()),
    )


def _handler_factory(state: AppState):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - stdlib API name
            parsed = urlparse(self.path)
            try:
                if parsed.path == "/":
                    self._send_html(INDEX_HTML)
                elif parsed.path == "/api/strategies":
                    self._send_json(_strategies_payload(state))
                elif parsed.path == "/api/report":
                    self._send_json(_report_payload(state, parse_qs(parsed.query)))
                elif parsed.path == "/api/heatmap":
                    self._send_json(_heatmap_payload(state, parse_qs(parsed.query)))
                else:
                    self.send_error(HTTPStatus.NOT_FOUND, "not found")
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            except Exception as exc:  # pragma: no cover - defensive local server guard
                self._send_json({"error": f"internal error: {exc}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

        def log_message(self, fmt: str, *args) -> None:
            print(f"{self.address_string()} - {fmt % args}", flush=True)

        def _send_html(self, body: str) -> None:
            data = body.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
            data = json.dumps(payload, allow_nan=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return Handler


def _strategies_payload(state: AppState) -> dict:
    return {
        "start": state.start,
        "end": state.end,
        "strategies": list(state.returns.columns),
        "aliases": {name: ALIASES.get(name, name) for name in state.returns.columns},
        "default_a": "iter030 T20D120 candidate",
        "default_b": "iter030 canonical",
        "window_years": list(WINDOW_YEARS),
    }


def _lrs_200d_returns() -> pd.DataFrame:
    """Canonical price>SMA200 LRS variants with CASHX off-leg.

    The signal uses the unlevered underlying close and trades the next bar via
    `_simulate_on_off_np`, matching the Gayed LRS timing convention
    `[leverage_for_the_long_run, p.13]`.
    """
    from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import _simulate_on_off_np

    cash = daily_returns(load_testfolio_series("CASHX"))
    specs = {
        "LRS 200d SSO": ("SPYSIM", "SSOSIM"),
        "LRS 200d UPRO": ("SPYSIM", "UPROSIM"),
        "LRS 200d QLD": ("QQQSIM", "QLDSIM"),
        "LRS 200d TQQQ": ("QQQSIM", "TQQQSIM"),
    }
    out = {}
    for label, (underlying_ticker, risk_ticker) in specs.items():
        underlying = load_testfolio_series(underlying_ticker)
        signal = ((underlying > sma(underlying, 200)) & sma(underlying, 200).notna()).reindex(underlying.index)
        risk = daily_returns(load_testfolio_series(risk_ticker)).reindex(underlying.index)
        off = cash.reindex(underlying.index)
        out[label] = pd.Series(
            _simulate_on_off_np(signal.fillna(False).to_numpy(dtype=bool), risk.to_numpy(float), off.to_numpy(float)),
            index=underlying.index,
        )
    return pd.DataFrame(out)


def _report_payload(state: AppState, query: dict[str, list[str]]) -> dict:
    start = _one(query, "start", state.start)
    end = _one(query, "end", state.end)
    strategy_a = _one(query, "a", "iter030 T20D120 candidate")
    strategy_b = _one(query, "b", "iter030 canonical")
    sampled = max(1, int(_one(query, "sample", "12")))
    sliced = _slice_returns(state, start, end)
    _require_columns(sliced, strategy_a, strategy_b)

    metrics = _metrics_payload(sliced)
    equity = (1.0 + sliced).cumprod()
    drawdowns = equity / equity.cummax() - 1.0
    relative = equity[strategy_a] / equity[strategy_b]
    return {
        "start": str(sliced.index.min().date()),
        "end": str(sliced.index.max().date()),
        "n_days": int(len(sliced)),
        "strategy_a": strategy_a,
        "strategy_b": strategy_b,
        "metrics": metrics,
        "summary": {
            "a_end_equity": float(equity[strategy_a].iloc[-1]),
            "b_end_equity": float(equity[strategy_b].iloc[-1]),
            "a_over_b_end": float(relative.iloc[-1]),
            "pct_days_a_above_b": float((relative > 1.0).mean()),
            "a_mdd": float(drawdowns[strategy_a].min()),
            "b_mdd": float(drawdowns[strategy_b].min()),
        },
        "series": _series_payload(equity, drawdowns, relative, sampled),
    }


def _heatmap_payload(state: AppState, query: dict[str, list[str]]) -> dict:
    start = _one(query, "start", state.start)
    end = _one(query, "end", state.end)
    strategy_a = _one(query, "a", "iter030 T20D120 candidate")
    strategy_b = _one(query, "b", "iter030 canonical")
    sliced = _slice_returns(state, start, end)
    _require_columns(sliced, strategy_a, strategy_b)
    equity = (1.0 + sliced[[strategy_a, strategy_b]]).cumprod()
    relative = equity[strategy_a] / equity[strategy_b]
    rows = []
    for years in WINDOW_YEARS:
        window_days = years * TRADING_DAYS_PER_YEAR
        cells = []
        month_ends = pd.date_range(relative.index.min(), relative.index.max(), freq="ME")
        for end_date in month_ends:
            window = relative.loc[:end_date].tail(window_days)
            if len(window) < window_days:
                continue
            cells.append(
                {
                    "window_years": years,
                    "start": str(window.index.min().date()),
                    "end": str(window.index.max().date()),
                    "pct_a_above_b": float((window > 1.0).mean()),
                    "end_ratio": float(window.iloc[-1]),
                }
            )
        rows.append({"window_years": years, "cells": cells})
    return {
        "strategy_a": strategy_a,
        "strategy_b": strategy_b,
        "start": str(sliced.index.min().date()),
        "end": str(sliced.index.max().date()),
        "rows": rows,
        "scale": {"red": 0.0, "white": 0.5, "blue": 1.0},
    }


def _slice_returns(state: AppState, start: str, end: str) -> pd.DataFrame:
    try:
        sliced = state.returns.loc[pd.Timestamp(start):pd.Timestamp(end)]
    except Exception as exc:  # noqa: BLE001 - convert parsing errors to API 400
        raise ValueError(f"invalid date range: {exc}") from exc
    if len(sliced) < TRADING_DAYS_PER_YEAR:
        raise ValueError("date range must contain at least one trading year")
    return sliced


def _require_columns(df: pd.DataFrame, *names: str) -> None:
    missing = [name for name in names if name not in df.columns]
    if missing:
        raise ValueError(f"unknown strategy: {', '.join(missing)}")


def _metrics_payload(returns: pd.DataFrame) -> list[dict]:
    rows = []
    dates = pd.DatetimeIndex(returns.index)
    benchmark = returns["SPY buy_hold"].to_numpy(float)
    for label in returns.columns:
        row = _metrics_row_np(
            returns[label].to_numpy(float),
            benchmark,
            dates,
            label,
            "QQQ",
            "interactive_td_report",
            0,
            0,
            "comparison",
        )
        rows.append(
            {
                "label": label,
                "cagr": float(row["cagr"]),
                "sortino": float(row["sortino"]),
                "sharpe": float(row["sharpe"]),
                "mdd": float(row["mdd"]),
                "calmar": float(row["calmar"]),
                "end_mult": float(row["end_mult"]),
            }
        )
    return sorted(rows, key=lambda x: (x["sortino"], x["cagr"]), reverse=True)


def _series_payload(
    equity: pd.DataFrame,
    drawdowns: pd.DataFrame,
    relative: pd.Series,
    sampled: int,
) -> dict:
    # Keep full daily series in the browser. The frontend caches this payload and
    # recomputes the rolling A/B heatmap locally, so changing A/B does not require
    # another API call.
    step = 1
    eq = equity.iloc[::step]
    dd = drawdowns.iloc[::step]
    rel = relative.iloc[::step]
    return {
        "dates": [str(d.date()) for d in eq.index],
        "equity": {col: _float_list(eq[col]) for col in eq.columns},
        "drawdown": {col: _float_list(dd[col]) for col in dd.columns},
        "relative": _float_list(rel),
    }


def _float_list(series: pd.Series) -> list[float]:
    return [float(x) for x in series.to_numpy(dtype=float)]


def _one(query: dict[str, list[str]], key: str, default: str) -> str:
    vals = query.get(key)
    return vals[0] if vals else default


INDEX_HTML = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Iter030 T/D Interactive Report</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/uplot@1.6.30/dist/uPlot.min.css">
  <script src="https://cdn.jsdelivr.net/npm/uplot@1.6.30/dist/uPlot.iife.min.js"></script>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root { color-scheme: light; --bg: #f5f6fa; --panel: #ffffff; --muted: #6b7280; --text: #1c273c; --line: #d9dee8; --line-soft: #edf0f5; --accent: #0168fa; --accent-dark: #0156d0; }
    * { box-sizing: border-box; border-radius: 0 !important; }
    body { margin: 0; font-family: 'IBM Plex Sans', Arial, sans-serif; background: var(--bg); color: var(--text); }
    main { max-width: 1420px; margin: 0 auto; padding: 24px; }
    h1 { margin: 0 0 6px; font-size: 28px; font-weight: 600; letter-spacing: -0.02em; }
    h2 { margin: 0 0 12px; font-size: 18px; font-weight: 600; }
    h3 { margin: 0 0 8px; font-size: 15px; font-weight: 600; }
    p { color: var(--muted); margin: 0 0 18px; }
    .tabs { display: flex; gap: 0; margin: 18px 0 0; border-bottom: 1px solid var(--line); }
    .tab { background: #ffffff; color: var(--muted); border: 1px solid var(--line); border-bottom: 0; padding: 10px 16px; font-weight: 600; cursor: pointer; }
    .tab:hover { background: #eef5ff; color: var(--accent); border-color: #b8d4ff; }
    .tab.active { color: #ffffff; background: var(--accent); border-color: var(--accent); }
    .tab.active:hover { color: #ffffff; background: var(--accent-dark); border-color: var(--accent-dark); }
    .tab-content { display: none; }
    .tab-content.active { display: block; }
    .controls, .panel { background: var(--panel); border: 1px solid var(--line); padding: 16px; margin: 16px 0; box-shadow: 0 1px 2px rgba(28, 39, 60, 0.04); }
    .controls { display: grid; grid-template-columns: repeat(4, minmax(130px, 1fr)); gap: 12px; align-items: end; }
    .heat-controls { display: grid; grid-template-columns: 1fr 1fr auto; gap: 12px; align-items: end; margin-bottom: 12px; }
    label { display: grid; gap: 6px; color: var(--muted); font-size: 12px; font-weight: 500; }
    select, input, button { appearance: none; -webkit-appearance: none; background: #ffffff; color: var(--text); border: 1px solid var(--line); padding: 9px 10px; font: inherit; line-height: 1.35; outline: none; min-height: 40px; }
    select { background-image: linear-gradient(45deg, transparent 50%, #6b7280 50%), linear-gradient(135deg, #6b7280 50%, transparent 50%); background-position: calc(100% - 16px) 17px, calc(100% - 11px) 17px; background-size: 5px 5px, 5px 5px; background-repeat: no-repeat; padding-right: 30px; }
    select:focus, input:focus { border-color: var(--accent); box-shadow: 0 0 0 2px rgba(1, 104, 250, 0.12); }
    button { background: var(--accent); color: #ffffff; border: 1px solid var(--accent); font-weight: 700; cursor: pointer; }
    button:hover { background: var(--accent-dark); border-color: var(--accent-dark); }
    .summary { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; }
    .card { background: #ffffff; border: 1px solid var(--line); padding: 12px; }
    .card small { display: block; color: var(--muted); }
    .card strong { font-size: 18px; font-weight: 600; }
    .plot-layout { display: grid; grid-template-columns: 8fr 4fr; gap: 14px; align-items: start; }
    .plot-stack { display: grid; gap: 16px; }
    .plot { width: 100%; height: 360px; min-height: 360px; border: 1px solid var(--line); overflow: hidden; }
    .uplot { font-family: 'IBM Plex Sans', Arial, sans-serif; }
    .uplot .u-legend { display: none !important; }
    .uplot .u-title { display: none !important; }
    .legend-panel { border: 1px solid var(--line); background: #ffffff; max-height: 736px; overflow: auto; }
    .legend-panel table { font-size: 12px; }
    .legend-panel tr { cursor: pointer; }
    .legend-panel tr.off { opacity: 0.42; text-decoration: line-through; }
    .color-chip { display: inline-block; width: 12px; height: 12px; border: 1px solid rgba(28, 39, 60, 0.15); vertical-align: middle; }
    .heat-plot { width: 100%; height: 480px; border: 1px solid var(--line); }
    .heat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th, td { padding: 8px 9px; border-bottom: 1px solid var(--line-soft); text-align: right; }
    th { color: var(--muted); font-weight: 600; background: #fafbfc; border-bottom-color: var(--line); cursor: pointer; user-select: none; }
    th:first-child, td:first-child { text-align: left; }
    .note { color: var(--muted); font-size: 12px; margin-top: 8px; }
    details { border: 1px solid var(--line); background: #ffffff; margin-bottom: 10px; }
    summary { cursor: pointer; padding: 13px 14px; font-weight: 600; color: var(--text); background: #fafbfc; border-bottom: 1px solid var(--line-soft); }
    details[open] summary { border-bottom-color: var(--line); }
    .strategy-body { padding: 14px; display: grid; gap: 10px; color: #3b4863; }
    .strategy-body p { margin: 0; color: #3b4863; }
    .strategy-body ul { margin: 0; padding-left: 18px; color: #3b4863; }
    @media (max-width: 1100px) { .heat-grid, .plot-layout { grid-template-columns: 1fr; } .legend-panel { max-height: none; } }
    @media (max-width: 900px) { .controls, .summary, .heat-controls { grid-template-columns: 1fr; } main { padding: 14px; } }
  </style>
</head>
<body>
<main>
  <h1>Iter030 T/D Interactive Report</h1>
  <p>Research-only view. DSR/PBO failures still block promotion; this app is for interactive diagnostics.</p>

  <nav class="tabs">
    <button class="tab active" data-tab="overview">Overview</button>
    <button class="tab" data-tab="strategies">Strategies</button>
  </nav>

  <section id="overview" class="tab-content active">
    <section class="controls">
      <label>Start date<input id="start" type="date"></label>
      <label>End date<input id="end" type="date"></label>
      <label>Sample density<input id="sample" type="number" min="1" max="50" value="12"></label>
      <button id="run">Update all</button>
    </section>

    <section class="panel">
      <h2>Window Summary</h2>
      <div class="summary" id="summary"></div>
    </section>

    <section class="panel">
      <h2>Equity Curves</h2>
      <div class="plot-layout">
        <div class="plot-stack">
          <div id="equityChart" class="plot"></div>
          <div>
            <h2>Drawdown</h2>
            <div id="drawdownChart" class="plot"></div>
          </div>
        </div>
        <aside class="legend-panel">
          <table>
            <thead><tr><th>Color</th><th>Name</th><th>Date</th><th>Equity</th><th>Drawdown</th></tr></thead>
            <tbody id="seriesTable"></tbody>
          </table>
        </aside>
      </div>
      <div class="note">Equity/drawdown use uPlot for faster rendering with many curves. Click table rows to hide/show curves; cursor movement updates the table.</div>
    </section>

    <section class="panel">
      <h2>Rolling A/B Heatmap</h2>
      <p>Computed from cached daily equity in the browser. Changing A/B or clicking “Update heatmap” does not call the API again.</p>
      <div class="heat-controls">
        <label>Strategy A<select id="strategyA"></select></label>
        <label>Strategy B<select id="strategyB"></select></label>
        <button id="runHeatmap">Update heatmap</button>
      </div>
      <div id="abSummary" class="summary"></div>
      <div class="heat-grid">
        <div>
          <h3>% Days A Above B</h3>
          <div id="heatmapPct" class="heat-plot"></div>
        </div>
        <div>
          <h3>Window End A/B Ratio</h3>
          <div id="heatmapRatio" class="heat-plot"></div>
        </div>
      </div>
      <div class="note" id="heatNote"></div>
    </section>

    <section class="panel">
      <h2>Metrics</h2>
      <div id="metrics"></div>
      <div class="note">Click a column header to sort ascending/descending.</div>
    </section>
  </section>

  <section id="strategies" class="tab-content">
    <section class="panel">
      <h2>Strategy Concepts</h2>
      <div id="strategyDocs"></div>
    </section>
  </section>
</main>
<script>
const fmtPct = x => (x * 100).toFixed(2) + '%';
const fmtNum = x => Number(x).toLocaleString(undefined, {maximumFractionDigits: 2});
const fmtMult = x => fmtNum(x) + 'x';
const PLOT_CONFIG = {responsive: true, displaylogo: false, scrollZoom: true};
const PLOT_LAYOUT = {
  paper_bgcolor: '#ffffff', plot_bgcolor: '#ffffff', hovermode: 'x unified',
  margin: {l: 58, r: 24, t: 20, b: 38}, font: {family: 'IBM Plex Sans', color: '#1c273c'},
  xaxis: {showgrid: true, gridcolor: '#edf0f5', rangeslider: {visible: false}},
  yaxis: {showgrid: true, gridcolor: '#edf0f5'},
  legend: {orientation: 'h', y: -0.18}
};
const STRATEGY_DOCS = {
  'iter030 T20D120 candidate': {
    concept: 'Performance-first sensitivity from the iter030 family. It keeps the same T3d-K2 defensive shell and changes only the post-crash rearm geometry.',
    algorithm: ['Build the T3d-K2 ON/OFF vote from QLD: SMA250 gate, SMA100 gate, 21d realised-vol gate and 30d AR(1) gate with K=2.', 'When ON, hold QLD by default. If the post-crash rearm gate is active, upgrade the ON leg to TQQQ and apply the unconditional LRS1.20 overlay.', 'The rearm gate uses T20D120: a faster 20-day crash trigger and a longer 120-day rearm persistence window.', 'When OFF, hold ZROZ unless the rate-vol override is active, in which case use CASHX with gamma 0.25 plumbing from iter030.'],
    status: 'Best CAGR/terminal-equity sensitivity found here, but not a validated winner because the strict-Pareto validation failed DSR and PBO.'
  },
  'T20D90 balanced sensitivity': {
    concept: 'Balanced local T/D sensitivity. It tests whether the same faster crash trigger works with a less persistent D90 rearm window.',
    algorithm: ['Same T3d-K2 vote, risk-on QLD/TQQQ mechanics, LRS1.20 and off-leg logic as iter030.', 'Only the post-crash geometry changes to T20D90.', 'Compared with T20D120 it keeps almost the same CAGR but improves Sortino in the constrained T/D grid.'],
    status: 'Best balanced Sortino variant in the final local grid; still research-only.'
  },
  'iter030 canonical': {
    concept: 'The post-close iter030 anchor from the LETF rotation study. It is the main core benchmark for this branch.',
    algorithm: ['Use the T3d-K2 QLD/ZROZ ON/OFF vote.', 'Inside ON regimes, apply the T35D60 rearm-only QLD-to-TQQQ upgrade.', 'Apply LRS1.20 to the ON leg.', 'Use rate-vol CASHX override on the defensive leg when ZROZ/rate volatility is unfavorable.'],
    status: 'Preserved as the core anchor because it remains strong and the local improvements failed formal DSR/PBO validation.'
  },
  'T3d-K2 canonical': {
    concept: 'Closed-study canonical winner before the post-close iter030 extensions.',
    algorithm: ['Compute four QLD-based gates: long trend, medium trend, realised-volatility regime and AR(1) persistence.', 'Enter risk-on QLD when at least 2 of 4 gates pass.', 'Use ZROZ as the risk-off asset.', 'No TQQQ rearm turbo and no iter030 rate-vol CASHX override.'],
    status: 'Lower CAGR than iter030 but historically important as the frozen closed-study anchor.'
  },
  'Stage3 shared QLD': {
    concept: 'A price-only GA rule discovered in Stage 3 on the long-history testfolio panel.',
    algorithm: ['Build an 8-signal vote from SMA/EMA trend, ROC momentum and RSI.', 'Use K=6 as the vote threshold.', 'Hold QLD when the vote passes and ZROZ otherwise.', 'No OHLC signals are used, so it can be reproduced on testfolio long-history data.'],
    status: 'Strong in-sample Sortino, but failed honest PBO/DSR validation.'
  },
  'Stage3 shared TQQQ': {
    concept: 'The same Stage 3 shared vote, but with TQQQ as the risk-on leg.',
    algorithm: ['Use the identical 8-signal price-only vote and K=6 threshold.', 'Hold TQQQ when ON and ZROZ otherwise.', 'This increases convexity and terminal equity at the cost of deeper drawdowns.'],
    status: 'High CAGR but failed honest validation and has materially worse drawdown than iter030.'
  },
  'Stage4-inside iter030 turbo': {
    concept: 'A hybrid that inserts the Stage4 technical vote as an extra TQQQ turbo gate inside iter030.',
    algorithm: ['Keep iter030 ON/OFF, defensive shell, LRS1.20 and rate-vol override.', 'Compute the Stage4 close-only vote on QQQ.', 'Upgrade QLD to TQQQ when either iter030 rearm or Stage4 says turbo is active.', 'Leave all other iter030 machinery unchanged.'],
    status: 'Raises CAGR/terminal equity but worsens MDD and Sortino, so it does not dominate iter030.'
  },
  'Stage4 QLD base vote': {
    concept: 'Modern Tiingo-derived technical vote reproduced on testfolio with QLD risk-on.',
    algorithm: ['Use the Stage4 base vote: SMA100>SMA250, ROC10>0, ROC120>0, StochRSI14>50 and RV21 percentile <70.', 'Risk-on if at least 3 signals pass.', 'Hold QLD when ON and ZROZ otherwise in this long-history reproduction.'],
    status: 'Very strong on modern Tiingo 2010+, but weakens materially over the full 1986+ testfolio history.'
  },
  'Stage4 TQQQ base vote': {
    concept: 'The same Stage4 base vote with TQQQ risk-on.',
    algorithm: ['Use the same 5-signal K=3 Stage4 vote.', 'Hold TQQQ when ON and ZROZ otherwise.', 'No iter030 defensive shell or rearm logic is applied.'],
    status: 'Aggressive modern-regime challenger, but old crash regimes make full-history risk unacceptable.'
  },
  'LRS 200d SSO': {
    concept: 'Canonical Leverage Rotation Strategy using SPY price above SMA200 to hold SSO.',
    algorithm: ['Compute SPYSIM close versus its 200-day simple moving average.', 'If SPY closes above SMA200, hold SSOSIM on the next bar.', 'Otherwise hold CASHX.', 'This is the 2x S&P 500 version of the Gayed-style LRS baseline.'],
    status: 'Simple benchmark for whether the complex rules beat a transparent 200d trend filter.'
  },
  'LRS 200d UPRO': {
    concept: 'Canonical LRS using SPY>SMA200 with UPRO as the 3x S&P 500 risk-on leg.',
    algorithm: ['Compute SPYSIM close versus SMA200.', 'If above SMA200, hold UPROSIM on the next bar.', 'Otherwise hold CASHX.', 'Same timing as LRS SSO but with 3x leverage.'],
    status: 'Useful stress benchmark for leverage decay and drawdown sensitivity.'
  },
  'LRS 200d QLD': {
    concept: 'Nasdaq version of LRS using QQQ>SMA200 with QLD risk-on.',
    algorithm: ['Compute QQQSIM close versus SMA200.', 'If above SMA200, hold QLDSIM on the next bar.', 'Otherwise hold CASHX.', 'This is the 2x Nasdaq trend-following baseline.'],
    status: 'Simple QQQ-family comparator for T3d/iter030 complexity.'
  },
  'LRS 200d TQQQ': {
    concept: 'Nasdaq LRS using QQQ>SMA200 with TQQQ risk-on.',
    algorithm: ['Compute QQQSIM close versus SMA200.', 'If above SMA200, hold TQQQSIM on the next bar.', 'Otherwise hold CASHX.', 'This is the 3x Nasdaq trend-following baseline.'],
    status: 'High-octane benchmark; useful for seeing whether iter030 adds more than simple trend timing.'
  },
  'QQQ buy_hold': {concept: 'Long-history Nasdaq/QQQ proxy buy-and-hold benchmark.', algorithm: ['Buy QQQSIM and hold continuously over the selected window.'], status: 'Passive Nasdaq comparator.'},
  'SPY buy_hold': {concept: 'Long-history SPY/S&P 500 proxy buy-and-hold benchmark.', algorithm: ['Buy SPYSIM and hold continuously over the selected window.'], status: 'Passive broad-market comparator.'}
};
let appMeta = null;
let cachedReport = null;
let sortState = {key: 'sortino', dir: -1};
let equityPlot = null;
let drawdownPlot = null;
let visibleSeries = new Set();
const PALETTE = ['#0168fa', '#dc3545', '#00cccc', '#6f42c1', '#10b759', '#f59f00', '#f10075', '#5b47fb', '#7987a1', '#3b4863', '#00a3ff', '#b91c1c', '#0f766e', '#7c3aed', '#65a30d'];

function alias(name) {
  return (appMeta && appMeta.aliases && appMeta.aliases[name]) || name;
}

async function getJSON(url) {
  const res = await fetch(url);
  const data = await res.json();
  if (!res.ok || data.error) throw new Error(data.error || res.statusText);
  return data;
}

function baseParams() {
  return new URLSearchParams({
    start: document.getElementById('start').value,
    end: document.getElementById('end').value,
    a: document.getElementById('strategyA').value,
    b: document.getElementById('strategyB').value,
    sample: document.getElementById('sample').value || '12',
  });
}

function renderWindowSummary(data) {
  const rows = data.metrics;
  const bestCagr = [...rows].sort((a, b) => b.cagr - a.cagr)[0];
  const bestSortino = [...rows].sort((a, b) => b.sortino - a.sortino)[0];
  const lowMdd = [...rows].sort((a, b) => b.mdd - a.mdd)[0];
  const cards = [
    ['Start', data.start], ['End', data.end], ['Bars', fmtNum(data.n_days)],
    ['Best CAGR', `${alias(bestCagr.label)}: ${fmtPct(bestCagr.cagr)}`],
    ['Best Sortino', `${alias(bestSortino.label)}: ${bestSortino.sortino.toFixed(3)}`],
    ['Lowest MDD', `${alias(lowMdd.label)}: ${fmtPct(lowMdd.mdd)}`],
  ];
  document.getElementById('summary').innerHTML = cards.map(([k, v]) => `<div class="card"><small>${k}</small><strong>${v}</strong></div>`).join('');
}

function renderABSummary() {
  const a = document.getElementById('strategyA').value;
  const b = document.getElementById('strategyB').value;
  const eq = cachedReport.series.equity;
  const rel = eq[a].map((v, i) => v / eq[b][i]);
  const cards = [
    ['A end equity', fmtMult(eq[a].at(-1))],
    ['B end equity', fmtMult(eq[b].at(-1))],
    ['A/B end ratio', fmtNum(rel.at(-1))],
    ['Days A > B', fmtPct(rel.filter(x => x > 1).length / rel.length)],
    ['A max DD', fmtPct(Math.min(...cachedReport.series.drawdown[a]))],
    ['B max DD', fmtPct(Math.min(...cachedReport.series.drawdown[b]))],
  ];
  document.getElementById('abSummary').innerHTML = cards.map(([k, v]) => `<div class="card"><small>${k}</small><strong>${v}</strong></div>`).join('');
}

function renderMetrics(rows) {
  const sorted = [...rows].sort((a, b) => {
    const av = a[sortState.key], bv = b[sortState.key];
    return (typeof av === 'string' ? av.localeCompare(bv) : av - bv) * sortState.dir;
  });
  const cols = [['label','Strategy'], ['cagr','CAGR'], ['sortino','Sortino'], ['sharpe','Sharpe'], ['mdd','MDD'], ['calmar','Calmar'], ['end_mult','End']];
  const head = cols.map(([key, label]) => `<th data-key="${key}">${label}${sortState.key === key ? (sortState.dir > 0 ? ' ▲' : ' ▼') : ''}</th>`).join('');
  const body = sorted.map(r => `<tr><td title="${r.label}">${alias(r.label)}</td><td>${fmtPct(r.cagr)}</td><td>${r.sortino.toFixed(3)}</td><td>${r.sharpe.toFixed(3)}</td><td>${fmtPct(r.mdd)}</td><td>${r.calmar.toFixed(3)}</td><td>${fmtMult(r.end_mult)}</td></tr>`).join('');
  document.getElementById('metrics').innerHTML = `<table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
  document.querySelectorAll('#metrics th').forEach(th => th.addEventListener('click', () => {
    const key = th.dataset.key;
    sortState = sortState.key === key ? {key, dir: -sortState.dir} : {key, dir: key === 'label' ? 1 : -1};
    renderMetrics(cachedReport.metrics);
  }));
}

function renderCharts(data) {
  const dates = data.series.dates;
  const names = Object.keys(data.series.equity);
  if (!visibleSeries.size) names.forEach(name => visibleSeries.add(name));
  const timestamps = dates.map(d => new Date(d + 'T00:00:00Z').getTime() / 1000);
  const equityData = [timestamps, ...names.map(name => data.series.equity[name])];
  const drawdownData = [timestamps, ...names.map(name => data.series.drawdown[name].map(v => v * 100))];
  const equityOpts = uplotOptions('Growth of $1', names, true);
  const drawdownOpts = uplotOptions('Drawdown %', names, false);
  if (equityPlot) equityPlot.destroy();
  if (drawdownPlot) drawdownPlot.destroy();
  equityPlot = new uPlot(equityOpts, equityData, document.getElementById('equityChart'));
  drawdownPlot = new uPlot(drawdownOpts, drawdownData, document.getElementById('drawdownChart'));
  applySeriesVisibility(names);
  renderSeriesTable(names, dates.length - 1);
}

function uplotOptions(title, names, logScale) {
  return {
    width: document.getElementById('equityChart').clientWidth || 900,
    height: 358,
    title: null,
    legend: {show: false},
    cursor: {sync: {key: 'td-report'}},
    scales: {x: {time: true}, y: logScale ? {distr: 3, log: 10} : {}},
    axes: [{stroke: '#6b7280', grid: {stroke: '#edf0f5'}}, {stroke: '#6b7280', grid: {stroke: '#edf0f5'}}],
    series: [
      {},
      ...names.map((name, i) => ({label: alias(name), stroke: PALETTE[i % PALETTE.length], width: 1.6, points: {show: false}})),
    ],
    hooks: {setCursor: [u => renderSeriesTable(names, u.cursor.idx ?? cachedReport.series.dates.length - 1)]},
  };
}

function applySeriesVisibility(names) {
  names.forEach((name, i) => {
    const show = visibleSeries.has(name);
    equityPlot && equityPlot.setSeries(i + 1, {show});
    drawdownPlot && drawdownPlot.setSeries(i + 1, {show});
  });
}

function renderSeriesTable(names, idx) {
  if (!cachedReport) return;
  const dates = cachedReport.series.dates;
  const safeIdx = Math.max(0, Math.min(dates.length - 1, idx == null ? dates.length - 1 : idx));
  const rows = names.map((name, i) => {
    const shown = visibleSeries.has(name);
    const color = PALETTE[i % PALETTE.length];
    const equity = cachedReport.series.equity[name][safeIdx];
    const dd = cachedReport.series.drawdown[name][safeIdx];
    return `<tr class="${shown ? '' : 'off'}" data-name="${name}"><td><span class="color-chip" style="background:${color}"></span></td><td title="${name}">${alias(name)}</td><td>${dates[safeIdx]}</td><td>${fmtMult(equity)}</td><td>${fmtPct(dd)}</td></tr>`;
  }).join('');
  document.getElementById('seriesTable').innerHTML = rows;
  document.querySelectorAll('#seriesTable tr').forEach(row => row.addEventListener('click', () => {
    const name = row.dataset.name;
    visibleSeries.has(name) ? visibleSeries.delete(name) : visibleSeries.add(name);
    applySeriesVisibility(names);
    renderSeriesTable(names, safeIdx);
  }));
}

function monthEndIndices(dates) {
  const out = [];
  for (let i = 0; i < dates.length; i++) {
    const cur = dates[i].slice(0, 7);
    const next = i + 1 < dates.length ? dates[i + 1].slice(0, 7) : null;
    if (cur !== next) out.push(i);
  }
  return out;
}

function computeHeatmap() {
  const dates = cachedReport.series.dates;
  const eq = cachedReport.series.equity;
  const a = document.getElementById('strategyA').value;
  const b = document.getElementById('strategyB').value;
  const rel = eq[a].map((v, i) => v / eq[b][i]);
  const monthEnds = monthEndIndices(dates);
  const windows = [3, 5, 10, 15, 20];
  const zPct = [], zRatio = [], textPct = [], textRatio = [], x = [];
  const validEnds = monthEnds.filter(idx => idx >= 3 * 252);
  for (const idx of validEnds) x.push(dates[idx]);
  for (const years of windows) {
    const pctRow = [], ratioRow = [], pctTxt = [], ratioTxt = [];
    const n = years * 252;
    for (const idx of validEnds) {
      if (idx < n) {
        pctRow.push(null); ratioRow.push(null); pctTxt.push('Not enough history'); ratioTxt.push('Not enough history');
        continue;
      }
      const start = idx - n + 1;
      const slice = rel.slice(start, idx + 1);
      const pct = slice.filter(v => v > 1).length / slice.length;
      const base = rel[start];
      const windowRatio = rel[idx] / base;
      pctRow.push(pct * 100);
      ratioRow.push(windowRatio);
      pctTxt.push(`${years}y: ${dates[start]} to ${dates[idx]}<br>A > B: ${(pct * 100).toFixed(2)}%<br>Window A/B ratio: ${windowRatio.toFixed(3)}`);
      ratioTxt.push(`${years}y: ${dates[start]} to ${dates[idx]}<br>Window A/B ratio: ${windowRatio.toFixed(3)}<br>A > B: ${(pct * 100).toFixed(2)}%`);
    }
    zPct.push(pctRow); zRatio.push(ratioRow); textPct.push(pctTxt); textRatio.push(ratioTxt);
  }
  return {x, y: windows.map(w => `${w}y`), zPct, zRatio, textPct, textRatio, a, b};
}

function renderHeatmap() {
  const h = computeHeatmap();
  const tracePct = {x: h.x, y: h.y, z: h.zPct, text: h.textPct, type: 'heatmap', zmin: 0, zmax: 100, colorscale: [[0, '#d73027'], [0.5, '#f7f7f7'], [1, '#2166ac']], hovertemplate: '%{text}<extra></extra>', colorbar: {title: '% days A>B'}};
  const traceRatio = {x: h.x, y: h.y, z: h.zRatio, text: h.textRatio, type: 'heatmap', zmid: 1, colorscale: [[0, '#d73027'], [0.5, '#f7f7f7'], [1, '#2166ac']], hovertemplate: '%{text}<extra></extra>', colorbar: {title: 'A/B'}};
  const layout = {...PLOT_LAYOUT, height: 480, margin: {l: 58, r: 24, t: 20, b: 56}, yaxis: {autorange: 'reversed'}, xaxis: {showgrid: false, rangeslider: {visible: false}}};
  Plotly.react('heatmapPct', [tracePct], layout, PLOT_CONFIG);
  Plotly.react('heatmapRatio', [traceRatio], layout, PLOT_CONFIG);
  renderABSummary();
  document.getElementById('heatNote').textContent = `${alias(h.a)} / ${alias(h.b)}. Heatmaps recalculated from cached daily equity; no API call used.`;
}

function renderStrategyDocs(strategies) {
  document.getElementById('strategyDocs').innerHTML = strategies.map(name => {
    const doc = STRATEGY_DOCS[name] || {concept: 'No description available.', algorithm: [], status: ''};
    const bullets = (doc.algorithm || []).map(x => `<li>${x}</li>`).join('');
    return `<details><summary>${alias(name)} <span class="text-slate-500 font-normal">${name}</span></summary><div class="strategy-body"><p><strong>Concept:</strong> ${doc.concept}</p><div><strong>Algorithm:</strong><ul>${bullets}</ul></div><p><strong>Status:</strong> ${doc.status}</p></div></details>`;
  }).join('');
}

async function updateAll() {
  try {
    cachedReport = await getJSON('/api/report?' + baseParams().toString());
    renderWindowSummary(cachedReport);
    renderMetrics(cachedReport.metrics);
    renderCharts(cachedReport);
    renderHeatmap();
  } catch (err) {
    alert(err.message);
  }
}

function setupTabs() {
  document.querySelectorAll('.tab').forEach(btn => btn.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(x => x.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(btn.dataset.tab).classList.add('active');
  }));
}

async function init() {
  appMeta = await getJSON('/api/strategies');
  document.getElementById('start').value = appMeta.start;
  document.getElementById('end').value = appMeta.end;
  for (const id of ['strategyA', 'strategyB']) {
    const el = document.getElementById(id);
    el.innerHTML = appMeta.strategies.map(s => `<option>${s}</option>`).join('');
  }
  document.getElementById('strategyA').value = appMeta.default_a;
  document.getElementById('strategyB').value = appMeta.default_b;
  renderStrategyDocs(appMeta.strategies);
  setupTabs();
  document.getElementById('run').addEventListener('click', updateAll);
  document.getElementById('runHeatmap').addEventListener('click', renderHeatmap);
  await updateAll();
}

init();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
