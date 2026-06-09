#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC = REPO_ROOT / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from market_lab.backtest.metrics.performance import (  # noqa: E402
    cagr,
    calmar,
    max_drawdown,
    returns_from_equity,
    sharpe,
    sortino,
    volatility,
)

STUDY_DIR = Path(__file__).resolve().parent
RAW_DIR = STUDY_DIR / "raw"
RESULTS_DIR = STUDY_DIR / "results"
RAW_RESPONSE = RAW_DIR / "testfolio_four_asset_response.json"
RAW_PAYLOAD = RAW_DIR / "testfolio_four_asset_payload.json"
ASSET_EQUITY_CSV = RESULTS_DIR / "asset_equity_curves.csv"
GRID_CSV = RESULTS_DIR / "four_asset_monthly_grid.csv"
REPORT_MD = STUDY_DIR / "REPORT.md"

ENDPOINT = "https://testfol.io/api/backtest"
TOKEN_FILE = REPO_ROOT / ".testfolio_token"
START_VALUE = 10_000.0
GRID_STEP_PCT = 5
PERIODS_PER_YEAR = 252

ASSETS = ["NTSXSIM", "GDESIM", "RSST70_30", "ZROZSIM"]
PAYLOAD_LABELS = ["NTSXSIM", "GDESIM", "ZROZSIM", "RSST70_30", "EQUAL_25_DAILY_PAYLOAD"]

# Rank-based blend keeps units comparable while balancing return and drawdown
# diagnostics; see [testing_tuning, p.327-335] and [systematic_trading, p.185-188].
FITNESS_WEIGHTS = {
    "calmar": 0.25,
    "sharpe": 0.20,
    "sortino": 0.15,
    "cagr": 0.20,
    "mdd_safety": 0.10,
    "vol_safety": 0.10,
}


@dataclass(frozen=True)
class PortfolioMetrics:
    portfolio: str
    n_assets: int
    ntsx_pct: int
    gde_pct: int
    rsst70_30_pct: int
    zroz_pct: int
    start_date: str
    end_date: str
    years: float
    cagr: float
    mdd: float
    mdd_abs: float
    vol: float
    sharpe: float
    sortino: float
    calmar: float
    terminal: float


def build_payload() -> dict:
    return {
        "start_date": "1800-01-01",
        "end_date": "2100-01-01",
        "start_val": START_VALUE,
        "adj_inflation": False,
        "target_currency": "USD",
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
        "backtests": [
            _single_asset_backtest("NTSXSIM", "Yearly"),
            _single_asset_backtest("GDESIM", "Yearly"),
            _single_asset_backtest("ZROZSIM", "Yearly"),
            {
                "invest_dividends": True,
                "rebalance_freq": "Daily",
                "rebalance_offset": 0,
                "allocation": {
                    "SPYSIM": 100,
                    "DBMFSIM": 70,
                    "KMLMSIM": 30,
                    "CASHX?E=-2": -100,
                },
                "drag": 0,
                "absolute_dev": 0,
                "relative_dev": 0,
            },
            {
                "invest_dividends": True,
                "rebalance_freq": "Daily",
                "rebalance_offset": 0,
                "allocation": {
                    "SPYSIM": 25,
                    "DBMFSIM": 17.5,
                    "KMLMSIM": 7.5,
                    "CASHX?E=-2": -25,
                    "NTSXSIM": 25,
                    "GDESIM": 25,
                    "ZROZSIM": 25,
                },
                "drag": 0,
                "absolute_dev": 0,
                "relative_dev": 0,
            },
        ],
        "cashflow_legs": [],
    }


def _single_asset_backtest(ticker: str, rebalance_freq: str) -> dict:
    return {
        "invest_dividends": True,
        "rebalance_freq": rebalance_freq,
        "rebalance_offset": 0,
        "allocation": {ticker: 100},
        "drag": 0,
        "absolute_dev": 0,
        "relative_dev": 0,
    }


def _token_from_env_or_file() -> str:
    token = os.environ.get("TESTFOLIO_TOKEN", "").strip()
    if token:
        return token
    if TOKEN_FILE.exists():
        token = TOKEN_FILE.read_text(encoding="utf-8").strip()
        if token:
            return token
    return ""


def _post_payload(payload: dict, token: str = "") -> dict:
    headers = {
        "content-type": "application/json",
        "Referer": "https://testfol.io/",
        "User-Agent": "market-lab/four-asset-grid",
    }
    if token:
        headers["authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download_response(force: bool) -> dict:
    if RAW_RESPONSE.exists() and not force:
        return json.loads(RAW_RESPONSE.read_text(encoding="utf-8"))

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    RAW_PAYLOAD.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    try:
        response = _post_payload(payload)
    except urllib.error.HTTPError as no_auth_error:
        token = _token_from_env_or_file()
        if not token:
            body = no_auth_error.read().decode(errors="replace")[:500]
            raise RuntimeError(
                f"Testfol.io no-auth request failed with HTTP {no_auth_error.code}: {body}. "
                "Set TESTFOLIO_TOKEN or .testfolio_token for an authenticated retry."
            ) from no_auth_error
        response = _post_payload(payload, token=token)

    RAW_RESPONSE.write_text(json.dumps(response), encoding="utf-8")
    return response


def extract_equity_frame(response: dict) -> pd.DataFrame:
    errors = response.get("errors", [])
    if errors:
        raise RuntimeError(f"Testfol.io returned errors: {errors}")

    history = response.get("charts", {}).get("history")
    if not isinstance(history, list) or len(history) < len(PAYLOAD_LABELS) + 1:
        raise ValueError("charts.history does not contain the expected five equity curves")

    index = pd.DatetimeIndex(pd.to_datetime(history[0], unit="s", utc=True).tz_convert(None))
    frame = pd.DataFrame(index=index)
    for label, values in zip(PAYLOAD_LABELS, history[1:], strict=False):
        frame[label] = pd.to_numeric(pd.Series(values, index=index), errors="coerce")

    asset_frame = frame[ASSETS].dropna(how="any")
    if asset_frame.empty:
        raise ValueError("common asset equity frame is empty after dropna")
    return asset_frame


def generate_weight_vectors(step_pct: int = GRID_STEP_PCT) -> list[tuple[int, int, int, int]]:
    units = 100 // step_pct
    vectors: list[tuple[int, int, int, int]] = []
    for a in range(units + 1):
        for b in range(units + 1 - a):
            for c in range(units + 1 - a - b):
                d = units - a - b - c
                vectors.append((a * step_pct, b * step_pct, c * step_pct, d * step_pct))
    return vectors


def monthly_rebalanced_equity(asset_returns: pd.DataFrame, weights_pct: tuple[int, int, int, int], start_date: pd.Timestamp) -> pd.Series:
    weights = pd.Series([w / 100.0 for w in weights_pct], index=ASSETS, dtype=float)
    holdings = weights.copy()
    value = 1.0
    current_month: tuple[int, int] | None = None
    dates: list[pd.Timestamp] = [start_date]
    values: list[float] = [value]

    for date, row in asset_returns.iterrows():
        month = (date.year, date.month)
        if month != current_month:
            holdings = weights * value
            current_month = month
        holdings = holdings * (1.0 + row[ASSETS])
        value = float(holdings.sum())
        dates.append(date)
        values.append(value)

    return pd.Series(values, index=pd.DatetimeIndex(dates), name=format_portfolio(weights_pct))


def format_portfolio(weights_pct: tuple[int, int, int, int]) -> str:
    parts = [f"{weight}% {asset}" for asset, weight in zip(ASSETS, weights_pct, strict=True) if weight > 0]
    return " / ".join(parts)


def compute_metrics(equity: pd.Series, weights_pct: tuple[int, int, int, int]) -> PortfolioMetrics:
    returns = returns_from_equity(equity)
    mdd_abs = max_drawdown(equity)
    start = equity.index[0]
    end = equity.index[-1]
    years = (end - start).days / 365.25
    calmar_value = calmar(equity, PERIODS_PER_YEAR)
    sortino_value = sortino(returns, PERIODS_PER_YEAR)
    return PortfolioMetrics(
        portfolio=format_portfolio(weights_pct),
        n_assets=sum(1 for w in weights_pct if w > 0),
        ntsx_pct=weights_pct[0],
        gde_pct=weights_pct[1],
        rsst70_30_pct=weights_pct[2],
        zroz_pct=weights_pct[3],
        start_date=start.strftime("%Y-%m-%d"),
        end_date=end.strftime("%Y-%m-%d"),
        years=years,
        cagr=cagr(equity, PERIODS_PER_YEAR),
        mdd=-mdd_abs,
        mdd_abs=mdd_abs,
        vol=volatility(returns, PERIODS_PER_YEAR),
        sharpe=sharpe(returns, PERIODS_PER_YEAR),
        sortino=sortino_value,
        calmar=calmar_value,
        terminal=float(equity.iloc[-1]),
    )


def _finite_for_rank(series: pd.Series) -> pd.Series:
    cleaned = series.astype(float).replace([np.inf, -np.inf], np.nan)
    if cleaned.notna().any():
        return cleaned.fillna(cleaned.max())
    return pd.Series(0.0, index=series.index)


def add_fitness_score(frame: pd.DataFrame) -> pd.DataFrame:
    scored = frame.copy()
    scored["rank_calmar"] = _finite_for_rank(scored["calmar"]).rank(pct=True, ascending=True)
    scored["rank_sharpe"] = _finite_for_rank(scored["sharpe"]).rank(pct=True, ascending=True)
    scored["rank_sortino"] = _finite_for_rank(scored["sortino"]).rank(pct=True, ascending=True)
    scored["rank_cagr"] = _finite_for_rank(scored["cagr"]).rank(pct=True, ascending=True)
    scored["rank_mdd_safety"] = _finite_for_rank(scored["mdd_abs"]).rank(pct=True, ascending=False)
    scored["rank_vol_safety"] = _finite_for_rank(scored["vol"]).rank(pct=True, ascending=False)
    scored["fitness_score"] = 100.0 * (
        FITNESS_WEIGHTS["calmar"] * scored["rank_calmar"]
        + FITNESS_WEIGHTS["sharpe"] * scored["rank_sharpe"]
        + FITNESS_WEIGHTS["sortino"] * scored["rank_sortino"]
        + FITNESS_WEIGHTS["cagr"] * scored["rank_cagr"]
        + FITNESS_WEIGHTS["mdd_safety"] * scored["rank_mdd_safety"]
        + FITNESS_WEIGHTS["vol_safety"] * scored["rank_vol_safety"]
    )
    return scored.sort_values(
        ["fitness_score", "calmar", "sharpe", "cagr", "mdd"],
        ascending=[False, False, False, False, False],
    ).reset_index(drop=True)


def run_grid(asset_equity: pd.DataFrame) -> pd.DataFrame:
    asset_returns = asset_equity.pct_change().dropna()
    vectors = generate_weight_vectors()
    weights_pct = np.array(vectors, dtype=int)
    weights = weights_pct.astype(float) / 100.0
    equity = simulate_monthly_rebalanced_matrix(asset_returns, weights)
    frame = metrics_from_equity_matrix(asset_equity, equity, weights_pct, vectors)
    return add_fitness_score(frame)


def simulate_monthly_rebalanced_matrix(asset_returns: pd.DataFrame, weights: np.ndarray) -> np.ndarray:
    returns = asset_returns[ASSETS].to_numpy(dtype=float)
    month_codes = np.array([date.year * 12 + date.month for date in asset_returns.index], dtype=int)
    n_days = returns.shape[0]
    n_portfolios = weights.shape[0]
    equity = np.empty((n_days + 1, n_portfolios), dtype=float)
    values = np.ones(n_portfolios, dtype=float)
    holdings = values[:, None] * weights
    current_month: int | None = None
    equity[0] = values

    for i in range(n_days):
        if int(month_codes[i]) != current_month:
            holdings = values[:, None] * weights
            current_month = int(month_codes[i])
        holdings = holdings * (1.0 + returns[i])
        values = holdings.sum(axis=1)
        equity[i + 1] = values
    return equity


def metrics_from_equity_matrix(
    asset_equity: pd.DataFrame,
    equity: np.ndarray,
    weights_pct: np.ndarray,
    vectors: list[tuple[int, int, int, int]],
) -> pd.DataFrame:
    returns = equity[1:] / equity[:-1] - 1.0
    n_periods = equity.shape[0] - 1
    terminal = equity[-1]
    cagr_values = terminal ** (PERIODS_PER_YEAR / n_periods) - 1.0
    running_peak = np.maximum.accumulate(equity, axis=0)
    drawdowns = (running_peak - equity) / running_peak
    mdd_abs = drawdowns.max(axis=0)
    vol_values = returns.std(axis=0, ddof=0) * np.sqrt(PERIODS_PER_YEAR)
    mean_returns = returns.mean(axis=0)
    sharpe_values = np.divide(
        mean_returns,
        returns.std(axis=0, ddof=0),
        out=np.zeros_like(mean_returns),
        where=returns.std(axis=0, ddof=0) > 1e-12,
    ) * np.sqrt(PERIODS_PER_YEAR)
    downside = np.minimum(returns, 0.0)
    downside_dev = np.sqrt(np.mean(downside**2, axis=0))
    sortino_values = np.divide(
        mean_returns,
        downside_dev,
        out=np.full_like(mean_returns, np.inf),
        where=downside_dev > 1e-12,
    ) * np.sqrt(PERIODS_PER_YEAR)
    calmar_values = np.divide(
        cagr_values,
        mdd_abs,
        out=np.full_like(cagr_values, np.inf),
        where=mdd_abs > 1e-12,
    )
    years = (asset_equity.index[-1] - asset_equity.index[0]).days / 365.25
    return pd.DataFrame(
        {
            "portfolio": [format_portfolio(vector) for vector in vectors],
            "n_assets": (weights_pct > 0).sum(axis=1),
            "ntsx_pct": weights_pct[:, 0],
            "gde_pct": weights_pct[:, 1],
            "rsst70_30_pct": weights_pct[:, 2],
            "zroz_pct": weights_pct[:, 3],
            "start_date": asset_equity.index[0].strftime("%Y-%m-%d"),
            "end_date": asset_equity.index[-1].strftime("%Y-%m-%d"),
            "years": years,
            "cagr": cagr_values,
            "mdd": -mdd_abs,
            "mdd_abs": mdd_abs,
            "vol": vol_values,
            "sharpe": sharpe_values,
            "sortino": sortino_values,
            "calmar": calmar_values,
            "terminal": terminal,
        }
    )


def _fmt_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _fmt_num(value: float) -> str:
    if isinstance(value, float) and math.isinf(value):
        return "inf"
    return f"{value:.3f}"


def _markdown_table(frame: pd.DataFrame, columns: list[str], formats: dict[str, str] | None = None) -> str:
    formats = formats or {}
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    lines = [header, sep]
    for _, row in frame.iterrows():
        cells: list[str] = []
        for col in columns:
            value = row[col]
            fmt = formats.get(col, "")
            if fmt == "pct":
                cells.append(_fmt_pct(float(value)))
            elif fmt == "num":
                cells.append(_fmt_num(float(value)))
            elif fmt == "score":
                cells.append(f"{float(value):.2f}")
            elif fmt == "int":
                cells.append(str(int(value)))
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_report(scored: pd.DataFrame, asset_equity: pd.DataFrame) -> None:
    top20 = scored.head(20).copy()
    top20.insert(0, "rank", range(1, len(top20) + 1))
    baseline_keys = [
        (25, 25, 25, 25),
        (0, 35, 40, 25),
        (100, 0, 0, 0),
        (0, 100, 0, 0),
        (0, 0, 100, 0),
        (0, 0, 0, 100),
    ]
    baseline = scored.set_index(["ntsx_pct", "gde_pct", "rsst70_30_pct", "zroz_pct"]).loc[baseline_keys].reset_index()
    best = top20.iloc[0]
    weights_text = " + ".join(f"{int(best[col])}% {label}" for col, label in [
        ("ntsx_pct", "NTSXSIM"),
        ("gde_pct", "GDESIM"),
        ("rsst70_30_pct", "RSST70_30"),
        ("zroz_pct", "ZROZSIM"),
    ] if int(best[col]) > 0)

    formats = {
        "rank": "int",
        "fitness_score": "score",
        "cagr": "pct",
        "mdd": "pct",
        "vol": "pct",
        "sharpe": "num",
        "sortino": "num",
        "calmar": "num",
        "terminal": "num",
        "ntsx_pct": "int",
        "gde_pct": "int",
        "rsst70_30_pct": "int",
        "zroz_pct": "int",
    }
    table_cols = [
        "rank",
        "portfolio",
        "fitness_score",
        "cagr",
        "mdd",
        "vol",
        "sharpe",
        "sortino",
        "calmar",
        "terminal",
    ]
    baseline_cols = [
        "portfolio",
        "fitness_score",
        "cagr",
        "mdd",
        "vol",
        "sharpe",
        "sortino",
        "calmar",
        "terminal",
    ]

    report = (
        "# Four-Asset Monthly Grid\n\n"
        "Status: research-only diagnostic. No deployment, paper-trade label or mandate change.\n\n"
        "## Summary\n\n"
        f"- Window: `{asset_equity.index[0].date()}..{asset_equity.index[-1].date()}`.\n"
        f"- Assets: `{', '.join(ASSETS)}`.\n"
        f"- Grid: `{GRID_STEP_PCT}%` increments, `1,771` portfolios, monthly rebalance.\n"
        f"- Best by rank-based fitness: **{weights_text}**, score `{best['fitness_score']:.2f}`, "
        f"CAGR `{_fmt_pct(float(best['cagr']))}`, MDD `{_fmt_pct(float(best['mdd']))}`, "
        f"Sharpe `{_fmt_num(float(best['sharpe']))}`, Calmar `{_fmt_num(float(best['calmar']))}`.\n\n"
        "## Method\n\n"
        "The Testfol.io payload downloads `NTSXSIM`, `GDESIM`, `ZROZSIM`, and an "
        "`RSST70_30` tracking sleeve defined as `100% SPYSIM + 70% DBMFSIM + 30% "
        "KMLMSIM - 100% CASHX?E=-2`. The grid then simulates monthly rebalanced "
        "portfolio returns across all `[a,b,c,d]` weights where each component is "
        "a multiple of 5% and sums to 100%. Monthly rebalance is the requested "
        "cadence and matches the RSC research convention for turnover/friction "
        "discipline `[systematic_trading, p.185-188]`, `[risk_parity, p.80-81]`.\n\n"
        "Correction note: an earlier run used `CASHX?E=2`; that was a financing-sign "
        "error. The current canonical four-asset grid uses `CASHX?E=-2`, matching the "
        "correct RSST tracking payload `[systematic_trading, p.185-188]`.\n\n"
        "Fitness is a rank blend: 25% Calmar, 20% Sharpe, 15% Sortino, 20% CAGR, "
        "10% drawdown safety and 10% volatility safety. Rank scoring avoids mixing "
        "raw metric scales and keeps the result as a screening heuristic, not a "
        "validation gate `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.\n\n"
        "## Top 20\n\n"
        f"{_markdown_table(top20[table_cols], table_cols, formats)}\n\n"
        "## Reference Rows\n\n"
        f"{_markdown_table(baseline[baseline_cols], baseline_cols, formats)}\n\n"
        "## Artifacts\n\n"
        f"- Raw response: `{RAW_RESPONSE.relative_to(REPO_ROOT)}`.\n"
        f"- Payload: `{RAW_PAYLOAD.relative_to(REPO_ROOT)}`.\n"
        f"- Asset equity curves: `{ASSET_EQUITY_CSV.relative_to(REPO_ROOT)}`.\n"
        f"- Full grid: `{GRID_CSV.relative_to(REPO_ROOT)}`.\n\n"
        "- Walk-forward anti-overfit report: `studies/return_stacked_core/us_core/four_asset_grid/WF_REPORT.md`.\n\n"
        "- Robustness/PBO report: `studies/return_stacked_core/us_core/four_asset_grid/ROBUSTNESS_REPORT.md`.\n\n"
        "## Caveats\n\n"
        "This is a Testfol.io simulation screen. `RSST70_30` is a tracking proxy, not "
        "a live RSST ETF backfill. The grid does not include tax, implementation "
        "friction, DSR, bootstrap or cross-library gates. The separate walk-forward "
        "and PBO robustness reports test the full-sample weight-selection overfit risk and must be read "
        "before treating the top-20 as anything beyond research leads `[testing_tuning, "
        "p.318-320]`, `[advances_fin_ml, p.208-211]`.\n"
    )
    REPORT_MD.write_text(report, encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download Testfol.io data and run four-asset monthly grid.")
    parser.add_argument("--force-download", action="store_true", help="ignore existing raw response and request Testfol.io again")
    parser.add_argument("--skip-download", action="store_true", help="use existing raw response only")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.skip_download:
        if not RAW_RESPONSE.exists():
            raise FileNotFoundError(f"{RAW_RESPONSE} does not exist")
        response = json.loads(RAW_RESPONSE.read_text(encoding="utf-8"))
    else:
        response = download_response(force=args.force_download)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    asset_equity = extract_equity_frame(response)
    asset_equity.to_csv(ASSET_EQUITY_CSV, index_label="date")
    scored = run_grid(asset_equity)
    scored.to_csv(GRID_CSV, index=False)
    write_report(scored, asset_equity)
    print(f"wrote {GRID_CSV.relative_to(REPO_ROOT)} rows={len(scored)}")
    print(f"wrote {REPORT_MD.relative_to(REPO_ROOT)}")
    print(scored.head(20)[["portfolio", "fitness_score", "cagr", "mdd", "vol", "sharpe", "sortino", "calmar", "terminal"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
