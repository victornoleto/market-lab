"""JSON API for the interactive iter030 T/D report.

This server is intentionally simple and dependency-free. The React/Vite frontend
consumes only JSON from this process; all expensive series construction happens
once at startup, while date-window slicing is served from memory. The analytics
remain research-only because DSR/PBO failures block promotion
`[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
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
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import _metrics_row_np, _simulate_on_off_np


DEFAULT_PORT = 8765
TRADING_DAYS_PER_YEAR = 252
WINDOW_YEARS = (3, 5, 10, 15, 20)
ALIASES = {
    "iter030 T20D120 candidate": "Rearm T20D120",
    "T20D90 balanced sensitivity": "Rearm T20D90",
    "iter030 canonical": "Rearm T35D60",
    "T3d-K2 canonical": "Quad Risk K2",
    "Stage3 shared QLD": "Octa Price K6 QLD",
    "Stage3 shared TQQQ": "Octa Price K6 TQQQ",
    "Stage4-inside iter030 turbo": "Quint TrendMomVol Overlay",
    "Stage4 QLD base vote": "Quint TrendMomVol K3 QLD",
    "Stage4 TQQQ base vote": "Quint TrendMomVol K3 TQQQ",
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
    p = argparse.ArgumentParser(description="Serve iter030 T/D JSON API")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    state = _load_state()
    handler = _handler_factory(state)
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"api serving http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopping", flush=True)
    finally:
        server.server_close()
    return 0


def _load_state() -> AppState:
    ctx = _prepare_context(_load_module(ITER030_BACKTEST, "iter030_td_react_api"))
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
    return AppState(returns=returns, start=str(returns.index.min().date()), end=str(returns.index.max().date()))


def _lrs_200d_returns() -> pd.DataFrame:
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
        ma = sma(underlying, 200)
        signal = ((underlying > ma) & ma.notna()).reindex(underlying.index)
        risk = daily_returns(load_testfolio_series(risk_ticker)).reindex(underlying.index)
        off = cash.reindex(underlying.index)
        out[label] = pd.Series(
            _simulate_on_off_np(signal.fillna(False).to_numpy(dtype=bool), risk.to_numpy(float), off.to_numpy(float)),
            index=underlying.index,
        )
    return pd.DataFrame(out)


def _handler_factory(state: AppState):
    class Handler(BaseHTTPRequestHandler):
        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(HTTPStatus.NO_CONTENT)
            self._cors_headers()
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            try:
                if parsed.path == "/api/health":
                    self._send_json({"ok": True})
                elif parsed.path == "/api/strategies":
                    self._send_json(_strategies_payload(state))
                elif parsed.path == "/api/report":
                    self._send_json(_report_payload(state, parse_qs(parsed.query)))
                else:
                    self.send_error(HTTPStatus.NOT_FOUND, "not found")
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            except Exception as exc:  # pragma: no cover - local server guard
                self._send_json({"error": f"internal error: {exc}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

        def log_message(self, fmt: str, *args) -> None:
            print(f"{self.address_string()} - {fmt % args}", flush=True)

        def _cors_headers(self) -> None:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

        def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
            data = json.dumps(payload, allow_nan=False).encode("utf-8")
            self.send_response(status)
            self._cors_headers()
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
        "default_a": "T3d-K2 canonical",
        "default_b": "SPY buy_hold",
        "window_years": list(WINDOW_YEARS),
    }


def _report_payload(state: AppState, query: dict[str, list[str]]) -> dict:
    start = _one(query, "start", state.start)
    end = _one(query, "end", state.end)
    strategy_a = _one(query, "a", "iter030 T20D120 candidate")
    strategy_b = _one(query, "b", "iter030 canonical")
    sliced = _slice_returns(state, start, end)
    _require_columns(sliced, strategy_a, strategy_b)

    equity = (1.0 + sliced).cumprod()
    drawdowns = equity / equity.cummax() - 1.0
    relative = equity[strategy_a] / equity[strategy_b]
    return {
        "start": str(sliced.index.min().date()),
        "end": str(sliced.index.max().date()),
        "n_days": int(len(sliced)),
        "strategy_a": strategy_a,
        "strategy_b": strategy_b,
        "metrics": _metrics_payload(sliced),
        "summary": {
            "a_end_equity": float(equity[strategy_a].iloc[-1]),
            "b_end_equity": float(equity[strategy_b].iloc[-1]),
            "a_over_b_end": float(relative.iloc[-1]),
            "pct_days_a_above_b": float((relative > 1.0).mean()),
            "a_mdd": float(drawdowns[strategy_a].min()),
            "b_mdd": float(drawdowns[strategy_b].min()),
        },
        "series": {
            "dates": [str(d.date()) for d in equity.index],
            "equity": {col: _float_list(equity[col]) for col in equity.columns},
            "drawdown": {col: _float_list(drawdowns[col]) for col in drawdowns.columns},
        },
    }


def _slice_returns(state: AppState, start: str, end: str) -> pd.DataFrame:
    try:
        sliced = state.returns.loc[pd.Timestamp(start):pd.Timestamp(end)]
    except Exception as exc:
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
        row = _metrics_row_np(returns[label].to_numpy(float), benchmark, dates, label, "QQQ", "react_td_report", 0, 0, "comparison")
        rows.append({
            "label": label,
            "cagr": float(row["cagr"]),
            "sortino": float(row["sortino"]),
            "sharpe": float(row["sharpe"]),
            "mdd": float(row["mdd"]),
            "calmar": float(row["calmar"]),
            "end_mult": float(row["end_mult"]),
        })
    return sorted(rows, key=lambda x: (x["sortino"], x["cagr"]), reverse=True)


def _float_list(series: pd.Series) -> list[float]:
    return [float(x) for x in series.to_numpy(dtype=float)]


def _one(query: dict[str, list[str]], key: str, default: str) -> str:
    vals = query.get(key)
    return vals[0] if vals else default


if __name__ == "__main__":
    raise SystemExit(main())
