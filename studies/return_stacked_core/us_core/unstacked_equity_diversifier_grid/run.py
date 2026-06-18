#!/usr/bin/env python3
"""Unstacked SSO/UPRO + diversifier grid.

The study keeps effective S&P 500 exposure at ~100% by holding a fractional
capital sleeve in 2x/3x daily-reset LETF proxies, then allocates the remaining
capital to unstacked diversifiers. LETF leverage is embedded inside Testfol.io's
daily-reset model, not external margin `[leverage_for_the_long_run, p.13]`.

Grid selection is a screen only: PBO and walk-forward are diagnostics against
weight-mining and regime dependence `[advances_fin_ml, p.208-211]`,
`[testing_tuning, p.327-335]`.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC = REPO_ROOT / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from market_lab.backtest.validation.pbo import pbo, pbo_gate  # noqa: E402

STUDY_DIR = Path(__file__).resolve().parent
RAW_DIR = STUDY_DIR / "raw"
RESULTS_DIR = STUDY_DIR / "results"
REPORT_MD = STUDY_DIR / "REPORT.md"

ENDPOINT = "https://testfol.io/api/backtest"
START_VALUE = 10_000.0
TRADING_DAYS = 252
DEFAULT_LEVERAGE_STEP = 0.05
# Coarse enough to run WF/PBO on the full grid, fine enough to distinguish
# cash/gold/ZROZ/MF mix regions `[testing_tuning, p.327-335]`.
DEFAULT_DIVERSIFIER_STEP_PCT = 10
DEFAULT_BATCH_SIZE = 1_500
PBO_BLOCKS = 10
WF_TRAIN_YEARS = 8
WF_TEST_YEARS = 2
WF_STEP_YEARS = 2
WF_PASS_RATIO = 6.0 / 8.0
HORIZONS_YEARS = [3, 5, 10, 15, 20, 30]
FITNESS_WEIGHTS = {
    "calmar": 0.25,
    "sharpe": 0.20,
    "sortino": 0.15,
    "cagr": 0.20,
    "mdd_safety": 0.10,
    "vol_safety": 0.10,
}


@dataclass(frozen=True)
class AssetSpec:
    alias: str
    ticker: str
    role: str


@dataclass(frozen=True)
class Scenario:
    slug: str
    diversifiers: tuple[str, ...]
    description: str
    min_start: str | None = None


@dataclass(frozen=True)
class Window:
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp


ASSET_SPECS: tuple[AssetSpec, ...] = (
    AssetSpec("SPY", "SPYSIM", "S&P 500 benchmark"),
    # User-provided ER convention. Testfol.io applies LETF daily reset and costs.
    AssetSpec("SSO_E091", "SPYSIM?L=2&E=0.91", "2x S&P 500 LETF proxy"),
    AssetSpec("UPRO_E091", "SPYSIM?L=3&E=0.91", "3x S&P 500 LETF proxy"),
    AssetSpec("CASH", "CASHX", "3-month T-bill cash sleeve"),
    AssetSpec("CASH_E_MINUS_2", "CASHX?E=-2", "cash + 2% financing leg"),
    AssetSpec("GOLD", "GLDSIM", "gold diversifier"),
    AssetSpec("ZROZ", "ZROZSIM", "25y+ zero-coupon Treasury diversifier"),
    AssetSpec("KMLM", "KMLMSIM", "managed futures proxy"),
    AssetSpec("DBMF", "DBMFSIM", "managed futures proxy"),
    AssetSpec("GDE", "GDESIM", "RSC gold/equity reference sleeve"),
)

SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        "kmlm_long",
        ("CASH", "GOLD", "ZROZ", "KMLM"),
        "long-window grid with KMLM as the managed-futures sleeve",
    ),
    Scenario(
        "dbmf_2000",
        ("CASH", "GOLD", "ZROZ", "DBMF"),
        "DBMF-only managed-futures sleeve, common 2000+ window",
    ),
    Scenario(
        "mf_blend_2000",
        ("CASH", "GOLD", "ZROZ", "MF70DBMF30KMLM"),
        "managed-futures sleeve fixed at 70% DBMF / 30% KMLM",
    ),
    Scenario(
        "kmlm_dbmf_split_2000",
        ("CASH", "GOLD", "ZROZ", "KMLM", "DBMF"),
        "KMLM and DBMF both available as separate optimizer sleeves",
    ),
)

ASSET_LABELS = {
    "SPY": "SPY",
    "SSO_E091": "SSO-like",
    "UPRO_E091": "UPRO-like",
    "CASH": "CASH",
    "CASH_E_MINUS_2": "CASH+2%",
    "GOLD": "GOLD",
    "ZROZ": "ZROZ",
    "KMLM": "KMLM",
    "DBMF": "DBMF",
    "MF70DBMF30KMLM": "MF70/30",
    "GDE": "GDE",
    "RSST70_30": "RSST70/30",
}


class TestfolioClient:
    """Small anonymous Testfol.io `/api/backtest` client for one-series pulls."""

    __test__ = False

    def __init__(self, raw_dir: Path = RAW_DIR, endpoint: str = ENDPOINT) -> None:
        self.raw_dir = raw_dir
        self.endpoint = endpoint

    @staticmethod
    def build_single_ticker_payload(ticker: str) -> dict[str, Any]:
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
                {
                    "invest_dividends": True,
                    "rebalance_freq": "Yearly",
                    "rebalance_offset": 0,
                    "allocation": {ticker: 100},
                    "drag": 0,
                    "absolute_dev": 0,
                    "relative_dev": 0,
                }
            ],
            "cashflow_legs": [],
        }

    def post_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "content-type": "application/json",
                "Referer": "https://testfol.io/",
                "User-Agent": "market-lab/unstacked-equity-diversifier-grid",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def fetch_json(self, spec: AssetSpec, force: bool = False) -> dict[str, Any]:
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        payload_path = self.raw_dir / f"{spec.alias.lower()}.payload.json"
        response_path = self.raw_dir / f"{spec.alias.lower()}.json"
        payload = self.build_single_ticker_payload(spec.ticker)
        payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        if response_path.exists() and not force:
            return json.loads(response_path.read_text(encoding="utf-8"))
        try:
            response = self.post_payload(payload)
        except urllib.error.HTTPError as error:
            body = error.read().decode(errors="replace")[:500]
            raise RuntimeError(
                f"Testfol.io public request failed for {spec.alias}/{spec.ticker}: "
                f"HTTP {error.code}: {body}"
            ) from error
        response_path.write_text(json.dumps(response), encoding="utf-8")
        return response


def alias_from_ticker(ticker: str) -> str:
    """Stable filesystem-safe alias for arbitrary Testfol.io ticker expressions."""
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", ticker).strip("_").lower()
    return cleaned or "ticker"


def extract_single_equity(response: dict[str, Any], alias: str) -> pd.Series:
    errors = response.get("errors", [])
    if errors:
        raise RuntimeError(f"Testfol.io returned errors for {alias}: {errors}")
    history = response.get("charts", {}).get("history")
    if not isinstance(history, list) or len(history) < 2:
        raise ValueError(f"Testfol.io response for {alias} does not contain history")
    timestamps = history[0]
    values = history[1]
    if len(timestamps) != len(values):
        raise ValueError(f"timestamp/value length mismatch for {alias}")
    index = pd.DatetimeIndex(pd.to_datetime(timestamps, unit="s", utc=True).tz_convert(None))
    return pd.Series(pd.to_numeric(values, errors="coerce"), index=index, name=alias)


def download_asset_curves(force: bool = False) -> pd.DataFrame:
    client = TestfolioClient()
    series = []
    for spec in ASSET_SPECS:
        response = client.fetch_json(spec, force=force)
        series.append(extract_single_equity(response, spec.alias))
    frame = pd.concat(series, axis=1, sort=True).sort_index()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    frame.to_csv(RESULTS_DIR / "asset_equity_curves.csv", index_label="date")
    return frame


def load_asset_curves_from_raw() -> pd.DataFrame:
    series = []
    for spec in ASSET_SPECS:
        path = RAW_DIR / f"{spec.alias.lower()}.json"
        if not path.exists():
            raise FileNotFoundError(f"{path} missing; run without --skip-download first")
        series.append(extract_single_equity(json.loads(path.read_text(encoding="utf-8")), spec.alias))
    frame = pd.concat(series, axis=1, sort=True).sort_index()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    frame.to_csv(RESULTS_DIR / "asset_equity_curves.csv", index_label="date")
    return frame


def build_daily_returns(asset_equity: pd.DataFrame) -> pd.DataFrame:
    returns = asset_equity.sort_index().pct_change()
    if {"DBMF", "KMLM"}.issubset(returns.columns):
        returns["MF70DBMF30KMLM"] = 0.70 * returns["DBMF"] + 0.30 * returns["KMLM"]
    if {"SPY", "DBMF", "KMLM", "CASH_E_MINUS_2"}.issubset(returns.columns):
        returns["RSST70_30"] = (
            returns["SPY"]
            + 0.70 * returns["DBMF"]
            + 0.30 * returns["KMLM"]
            - returns["CASH_E_MINUS_2"]
        )
    return returns


def simplex(n_assets: int, step_pct: int) -> list[tuple[float, ...]]:
    if 100 % step_pct != 0:
        raise ValueError(f"step_pct must divide 100 exactly, got {step_pct}")
    units = 100 // step_pct

    def rec(remaining: int, slots: int) -> Iterable[tuple[int, ...]]:
        if slots == 1:
            yield (remaining,)
            return
        for value in range(remaining + 1):
            for tail in rec(remaining - value, slots - 1):
                yield (value, *tail)

    return [tuple(value / units for value in row) for row in rec(units, n_assets)]


def leverage_ladder(step: float) -> list[float]:
    if step <= 0:
        raise ValueError("leverage step must be positive")
    n = int(round(1.0 / step))
    values = [round(2.0 + i * step, 10) for i in range(n + 1)]
    if not math.isclose(values[-1], 3.0, abs_tol=1e-9):
        raise ValueError("leverage step must land exactly on 3.0")
    return values


def carrier_weights(target_leverage: float) -> dict[str, float]:
    """Capital weights in SSO/UPRO that sum to exactly 100% equity beta."""
    if target_leverage < 2.0 or target_leverage > 3.0:
        raise ValueError(f"target leverage out of range: {target_leverage}")
    sso = (3.0 - target_leverage) / target_leverage
    upro = (target_leverage - 2.0) / target_leverage
    return {
        "SSO_E091": 0.0 if abs(sso) < 1e-12 else sso,
        "UPRO_E091": 0.0 if abs(upro) < 1e-12 else upro,
    }


def generate_candidate_table(
    scenario: Scenario,
    leverage_step: float = DEFAULT_LEVERAGE_STEP,
    diversifier_step_pct: int = DEFAULT_DIVERSIFIER_STEP_PCT,
) -> tuple[pd.DataFrame, np.ndarray, list[str]]:
    asset_cols = ["SSO_E091", "UPRO_E091", *scenario.diversifiers]
    div_props = simplex(len(scenario.diversifiers), diversifier_step_pct)
    rows: list[dict[str, object]] = []
    weights: list[list[float]] = []
    candidate_id = 0
    for target_leverage in leverage_ladder(leverage_step):
        carrier = carrier_weights(target_leverage)
        equity_capital = carrier["SSO_E091"] + carrier["UPRO_E091"]
        diversifier_capital = 1.0 - equity_capital
        for props in div_props:
            row_weights = [carrier.get("SSO_E091", 0.0), carrier.get("UPRO_E091", 0.0)]
            row_weights.extend(diversifier_capital * prop for prop in props)
            weights.append(row_weights)
            row: dict[str, object] = {
                "candidate_id": candidate_id,
                "scenario": scenario.slug,
                "target_leverage": target_leverage,
                "equity_capital": equity_capital,
                "diversifier_capital": diversifier_capital,
                "effective_equity": 2.0 * row_weights[0] + 3.0 * row_weights[1],
            }
            for asset, weight in zip(asset_cols, row_weights, strict=True):
                row[f"w_{asset}"] = weight
            rows.append(row)
            candidate_id += 1
    return pd.DataFrame(rows), np.asarray(weights, dtype=float), asset_cols


def period_codes(index: pd.DatetimeIndex, freq: str) -> np.ndarray:
    if freq == "M":
        return np.asarray([date.year * 12 + date.month for date in index], dtype=int)
    if freq == "Q":
        return np.asarray([date.year * 4 + (date.month - 1) // 3 for date in index], dtype=int)
    if freq == "Y":
        return np.asarray([date.year for date in index], dtype=int)
    raise ValueError(f"unknown frequency {freq!r}")


def simulate_rebalanced_matrix(
    asset_returns: pd.DataFrame,
    weights: np.ndarray,
    freq: str = "M",
) -> np.ndarray:
    returns = asset_returns.to_numpy(dtype=float)
    codes = period_codes(asset_returns.index, freq)
    n_days = returns.shape[0]
    n_portfolios = weights.shape[0]
    equity = np.empty((n_days + 1, n_portfolios), dtype=float)
    values = np.ones(n_portfolios, dtype=float)
    holdings = values[:, None] * weights
    current_period: int | None = None
    equity[0] = values
    for i in range(n_days):
        if int(codes[i]) != current_period:
            holdings = values[:, None] * weights
            current_period = int(codes[i])
        holdings = holdings * (1.0 + returns[i])
        values = holdings.sum(axis=1)
        equity[i + 1] = values
    return equity


def metrics_from_equity_matrix(equity: np.ndarray, dates: pd.DatetimeIndex) -> pd.DataFrame:
    returns = equity[1:] / equity[:-1] - 1.0
    years = (dates[-1] - dates[0]).days / 365.25
    terminal = equity[-1]
    cagr = np.power(terminal, 1.0 / years) - 1.0
    drawdown = equity / np.maximum.accumulate(equity, axis=0) - 1.0
    mdd = drawdown.min(axis=0)
    std = returns.std(axis=0, ddof=0)
    mean = returns.mean(axis=0)
    sharpe = np.divide(mean, std, out=np.zeros_like(mean), where=std > 1e-12)
    sharpe *= math.sqrt(TRADING_DAYS)
    downside = np.where(returns < 0.0, returns, np.nan)
    with np.errstate(invalid="ignore"):
        downside_std = np.nanstd(downside, axis=0, ddof=0)
    sortino = np.divide(mean, downside_std, out=np.zeros_like(mean), where=downside_std > 1e-12)
    sortino *= math.sqrt(TRADING_DAYS)
    vol = std * math.sqrt(TRADING_DAYS)
    calmar = np.divide(cagr, np.abs(mdd), out=np.zeros_like(cagr), where=np.abs(mdd) > 1e-12)
    return pd.DataFrame(
        {
            "start_date": dates[0].date().isoformat(),
            "end_date": dates[-1].date().isoformat(),
            "years": years,
            "cagr": cagr,
            "mdd": mdd,
            "mdd_abs": np.abs(mdd),
            "vol": vol,
            "sharpe": sharpe,
            "sortino": sortino,
            "calmar": calmar,
            "terminal": terminal,
        }
    )


def score_metric_frame(frame: pd.DataFrame) -> pd.DataFrame:
    scored = frame.copy()

    def finite(series: pd.Series) -> pd.Series:
        clean = series.astype(float).replace([np.inf, -np.inf], np.nan)
        return clean.fillna(clean.max() if clean.notna().any() else 0.0)

    scored["rank_calmar"] = finite(scored["calmar"]).rank(pct=True, ascending=True)
    scored["rank_sharpe"] = finite(scored["sharpe"]).rank(pct=True, ascending=True)
    scored["rank_sortino"] = finite(scored["sortino"]).rank(pct=True, ascending=True)
    scored["rank_cagr"] = finite(scored["cagr"]).rank(pct=True, ascending=True)
    scored["rank_mdd_safety"] = finite(scored["mdd_abs"]).rank(pct=True, ascending=False)
    scored["rank_vol_safety"] = finite(scored["vol"]).rank(pct=True, ascending=False)
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


def score_candidates_for_period(
    daily_returns: pd.DataFrame,
    meta: pd.DataFrame,
    weights: np.ndarray,
    asset_cols: list[str],
    batch_size: int,
) -> pd.DataFrame:
    aligned = daily_returns[asset_cols].dropna(how="any")
    if aligned.empty:
        raise ValueError(f"empty return matrix for {asset_cols}")
    rows = []
    for start in range(0, len(weights), batch_size):
        stop = min(start + batch_size, len(weights))
        equity = simulate_rebalanced_matrix(aligned, weights[start:stop], freq="M")
        metrics = metrics_from_equity_matrix(equity, aligned.index)
        rows.append(pd.concat([meta.iloc[start:stop].reset_index(drop=True), metrics], axis=1))
    frame = pd.concat(rows, ignore_index=True)
    frame["portfolio"] = [format_weights(row) for _, row in frame.iterrows()]
    return score_metric_frame(frame)


def format_weight_value(weight: float) -> str:
    pct = weight * 100.0
    if math.isclose(pct, round(pct), abs_tol=0.005):
        return f"{int(round(pct))}%"
    return f"{pct:.2f}%"


def format_weights(row: pd.Series | dict[str, object]) -> str:
    parts = []
    for key, value in row.items():
        if not str(key).startswith("w_"):
            continue
        weight = float(value)
        if weight <= 1e-10:
            continue
        asset = str(key)[2:]
        parts.append(f"{format_weight_value(weight)} {ASSET_LABELS.get(asset, asset)}")
    return " / ".join(parts)


def rebalanced_returns(
    asset_returns: pd.DataFrame,
    weights: dict[str, float],
    freq: str = "M",
) -> pd.Series:
    aligned = asset_returns[list(weights)].dropna(how="any")
    if aligned.empty:
        return pd.Series(dtype=float, name="portfolio")
    target = np.asarray([weights[col] for col in aligned.columns], dtype=float)
    if not math.isclose(float(target.sum()), 1.0, abs_tol=1e-6):
        raise ValueError(f"weights must sum to 1.0, got {target.sum():.8f}")
    equity = simulate_rebalanced_matrix(aligned, target.reshape(1, -1), freq=freq)[:, 0]
    returns = pd.Series(equity[1:] / equity[:-1] - 1.0, index=aligned.index, name="portfolio")
    return returns


def metrics_from_returns(returns: pd.Series) -> dict[str, float | str]:
    clean = returns.dropna().astype(float)
    if clean.empty:
        return {
            "start_date": "n/a",
            "end_date": "n/a",
            "years": math.nan,
            "cagr": math.nan,
            "mdd": math.nan,
            "mdd_abs": math.nan,
            "vol": math.nan,
            "sharpe": math.nan,
            "sortino": math.nan,
            "calmar": math.nan,
            "terminal": math.nan,
        }
    equity = (1.0 + clean).cumprod()
    years = (clean.index[-1] - clean.index[0]).days / 365.25
    drawdown = equity / equity.cummax() - 1.0
    std = clean.std(ddof=0)
    downside = clean[clean < 0.0].std(ddof=0)
    cagr = equity.iloc[-1] ** (1.0 / years) - 1.0
    mdd = float(drawdown.min())
    return {
        "start_date": clean.index[0].date().isoformat(),
        "end_date": clean.index[-1].date().isoformat(),
        "years": float(years),
        "cagr": float(cagr),
        "mdd": mdd,
        "mdd_abs": abs(mdd),
        "vol": float(std * math.sqrt(TRADING_DAYS)),
        "sharpe": float(clean.mean() / std * math.sqrt(TRADING_DAYS)) if std > 0 else math.nan,
        "sortino": (
            float(clean.mean() / downside * math.sqrt(TRADING_DAYS))
            if downside > 0
            else math.nan
        ),
        "calmar": float(cagr / abs(mdd)) if mdd < 0 else math.nan,
        "terminal": float(equity.iloc[-1]),
    }


def rolling_relative_stats(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    prefix: str,
) -> dict[str, float]:
    aligned = pd.concat(
        {"portfolio": portfolio_returns, "benchmark": benchmark_returns}, axis=1, sort=True
    ).dropna()
    if aligned.empty:
        return {}
    portfolio_equity = (1.0 + aligned["portfolio"]).cumprod().to_numpy(dtype=float)
    benchmark_equity = (1.0 + aligned["benchmark"]).cumprod().to_numpy(dtype=float)
    out: dict[str, float] = {}
    n = len(aligned)
    for horizon in HORIZONS_YEARS:
        days = horizon * TRADING_DAYS
        if n <= days:
            continue
        pprev = np.concatenate([[1.0], portfolio_equity[: n - days]])
        bprev = np.concatenate([[1.0], benchmark_equity[: n - days]])
        pend = portfolio_equity[days - 1 :]
        bend = benchmark_equity[days - 1 :]
        relative = (pend / pprev) / (bend / bprev)
        out[f"{prefix}_hit_{horizon}y"] = float((relative > 1.0).mean())
        out[f"{prefix}_p10_{horizon}y"] = float(np.quantile(relative, 0.10))
        out[f"{prefix}_min_{horizon}y"] = float(relative.min())
        out[f"{prefix}_latest_{horizon}y"] = float(relative[-1])
    return out


def named_reference_specs() -> dict[str, tuple[str, dict[str, float]]]:
    return {
        "SPY_yearly": ("Y", {"SPY": 1.00}),
        "user_P2_50_SSO_50_ZROZ": ("M", {"SSO_E091": 0.50, "ZROZ": 0.50}),
        "user_P3_34_UPRO_66_ZROZ": ("M", {"UPRO_E091": 0.34, "ZROZ": 0.66}),
        "user_P3_exact_1x_UPRO_ZROZ": ("M", {"UPRO_E091": 1.0 / 3.0, "ZROZ": 2.0 / 3.0}),
        "user_P4_UPRO_ZROZ_KMLM_GOLD": (
            "M",
            {"UPRO_E091": 0.3334, "ZROZ": 0.2222, "KMLM": 0.2222, "GOLD": 0.2222},
        ),
        "user_P5_SSO_ZROZ_KMLM_GOLD": (
            "M",
            {"SSO_E091": 0.50, "ZROZ": 0.1666, "KMLM": 0.1667, "GOLD": 0.1667},
        ),
        "proposal_base_25Z_25R_30G_20CASH": (
            "M",
            {"ZROZ": 0.25, "RSST70_30": 0.25, "GDE": 0.30, "CASH": 0.20},
        ),
        "proposal_16UPRO_4CASH": (
            "M",
            {"ZROZ": 0.25, "RSST70_30": 0.25, "GDE": 0.30, "UPRO_E091": 0.16, "CASH": 0.04},
        ),
        "proposal_16UPRO_plus_ZROZ": (
            "M",
            {"ZROZ": 0.29, "RSST70_30": 0.25, "GDE": 0.30, "UPRO_E091": 0.16},
        ),
        "proposal_16UPRO_plus_RSST": (
            "M",
            {"ZROZ": 0.25, "RSST70_30": 0.29, "GDE": 0.30, "UPRO_E091": 0.16},
        ),
        "proposal_16UPRO_plus_GDE": (
            "M",
            {"ZROZ": 0.25, "RSST70_30": 0.25, "GDE": 0.34, "UPRO_E091": 0.16},
        ),
        "proposal_16UPRO_split_4pct": (
            "M",
            {"ZROZ": 0.2633, "RSST70_30": 0.2633, "GDE": 0.3134, "UPRO_E091": 0.16},
        ),
        "proposal_20SSO": (
            "M",
            {"ZROZ": 0.25, "RSST70_30": 0.25, "GDE": 0.30, "SSO_E091": 0.20},
        ),
        "proposal_20UPRO": (
            "M",
            {"ZROZ": 0.25, "RSST70_30": 0.25, "GDE": 0.30, "UPRO_E091": 0.20},
        ),
        "RSC_like_35_40_25": ("M", {"GDE": 0.35, "RSST70_30": 0.40, "ZROZ": 0.25}),
    }


def exposure_breakdown(weights: dict[str, float]) -> dict[str, float]:
    """Approximate economic sleeves for named fixed portfolios.

    GDE is treated as 90% S&P + 90% gold; RSST70_30 as 100% S&P + 100% MF.
    This is an explanatory decomposition, not an accounting gate
    `[leverage_for_the_long_run, p.13]`, `[risk_parity, ch.5]`.
    """

    return {
        "effective_equity": (
            weights.get("SPY", 0.0)
            + 2.0 * weights.get("SSO_E091", 0.0)
            + 3.0 * weights.get("UPRO_E091", 0.0)
            + weights.get("RSST70_30", 0.0)
            + 0.90 * weights.get("GDE", 0.0)
        ),
        "effective_mf": (
            weights.get("KMLM", 0.0)
            + weights.get("DBMF", 0.0)
            + weights.get("MF70DBMF30KMLM", 0.0)
            + weights.get("RSST70_30", 0.0)
        ),
        "effective_gold": weights.get("GOLD", 0.0) + 0.90 * weights.get("GDE", 0.0),
        "effective_zroz": weights.get("ZROZ", 0.0),
    }


def evaluate_named_references(daily_returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    spy_returns = daily_returns["SPY"].dropna()
    rsc_returns = rebalanced_returns(
        daily_returns, {"GDE": 0.35, "RSST70_30": 0.40, "ZROZ": 0.25}, freq="M"
    )
    for name, (freq, weights) in named_reference_specs().items():
        returns = rebalanced_returns(daily_returns, weights, freq=freq)
        exposures = exposure_breakdown(weights)
        row: dict[str, object] = {
            "name": name,
            "freq": freq,
            "weights": format_weights({f"w_{asset}": weight for asset, weight in weights.items()}),
            **exposures,
            **metrics_from_returns(returns),
        }
        spy_aligned = pd.concat({"p": returns, "b": spy_returns}, axis=1, sort=True).dropna()
        rsc_aligned = pd.concat({"p": returns, "b": rsc_returns}, axis=1, sort=True).dropna()
        row["terminal_vs_spy"] = float(
            (1.0 + spy_aligned["p"]).prod() / (1.0 + spy_aligned["b"]).prod()
        ) if not spy_aligned.empty else math.nan
        row["terminal_vs_rsc"] = float(
            (1.0 + rsc_aligned["p"]).prod() / (1.0 + rsc_aligned["b"]).prod()
        ) if not rsc_aligned.empty else math.nan
        row.update(rolling_relative_stats(returns, spy_returns, "spy"))
        row.update(rolling_relative_stats(returns, rsc_returns, "rsc"))
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["terminal", "cagr"], ascending=False)


def build_windows(index: pd.DatetimeIndex) -> list[Window]:
    first = pd.Timestamp(index.min()).normalize()
    last = pd.Timestamp(index.max()).normalize()
    windows = []
    train_start = first
    while True:
        train_end = train_start + pd.DateOffset(years=WF_TRAIN_YEARS) - pd.Timedelta(days=1)
        test_start = train_end + pd.Timedelta(days=1)
        test_end = test_start + pd.DateOffset(years=WF_TEST_YEARS) - pd.Timedelta(days=1)
        if test_end > last:
            break
        windows.append(Window(train_start, train_end, test_start, test_end))
        train_start = train_start + pd.DateOffset(years=WF_STEP_YEARS)
    return windows


def weights_dict_from_row(row: pd.Series, asset_cols: list[str]) -> dict[str, float]:
    return {asset: float(row[f"w_{asset}"]) for asset in asset_cols if float(row[f"w_{asset}"]) > 1e-10}


def run_walk_forward(
    scenario: Scenario,
    daily_returns: pd.DataFrame,
    meta: pd.DataFrame,
    weights: np.ndarray,
    asset_cols: list[str],
    full_top_id: int,
    batch_size: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    aligned = daily_returns[asset_cols].dropna(how="any")
    windows = build_windows(aligned.index)
    rows = []
    wf_parts = []
    top_parts = []
    for i, window in enumerate(windows, start=1):
        train = daily_returns.loc[window.train_start : window.train_end]
        test = daily_returns.loc[window.test_start : window.test_end]
        train_grid = score_candidates_for_period(train, meta, weights, asset_cols, batch_size)
        test_grid = score_candidates_for_period(test, meta, weights, asset_cols, batch_size)
        test_ranked = test_grid.reset_index(drop=True).copy()
        test_ranked["oos_rank"] = np.arange(1, len(test_ranked) + 1)
        selected = train_grid.iloc[0]
        selected_id = int(selected["candidate_id"])
        selected_test = test_ranked[test_ranked["candidate_id"] == selected_id].iloc[0]
        full_top_test = test_ranked[test_ranked["candidate_id"] == full_top_id].iloc[0]
        selected_returns = rebalanced_returns(
            test, weights_dict_from_row(selected, asset_cols), freq="M"
        )
        full_top_returns = rebalanced_returns(
            test, weights_dict_from_row(full_top_test, asset_cols), freq="M"
        )
        wf_parts.append(selected_returns)
        top_parts.append(full_top_returns)
        rows.append(
            {
                "scenario": scenario.slug,
                "window": i,
                "train_start": window.train_start.date().isoformat(),
                "train_end": window.train_end.date().isoformat(),
                "test_start": window.test_start.date().isoformat(),
                "test_end": window.test_end.date().isoformat(),
                "selected_candidate_id": selected_id,
                "selected_portfolio": selected["portfolio"],
                "test_cagr": float(selected_test["cagr"]),
                "test_mdd": float(selected_test["mdd"]),
                "test_sharpe": float(selected_test["sharpe"]),
                "test_terminal": float(selected_test["terminal"]),
                "test_rank_pct": float((int(selected_test["oos_rank"]) / len(test_ranked))),
                "full_top_cagr": float(full_top_test["cagr"]),
                "full_top_mdd": float(full_top_test["mdd"]),
                "full_top_terminal": float(full_top_test["terminal"]),
                "positive_oos": bool(float(selected_test["terminal"]) > 1.0),
                "beat_full_top": bool(float(selected_test["terminal"]) > float(full_top_test["terminal"])),
            }
        )
    windows_df = pd.DataFrame(rows)
    summary_rows = []
    for name, parts in [("wf_selected", wf_parts), ("full_top_fixed", top_parts)]:
        returns = pd.concat(parts).sort_index() if parts else pd.Series(dtype=float)
        metrics = metrics_from_returns(returns)
        summary_rows.append({"scenario": scenario.slug, "strategy": name, **metrics})
    summary = pd.DataFrame(summary_rows)
    if not windows_df.empty:
        required = int(math.ceil(WF_PASS_RATIO * len(windows_df)))
        summary.loc[summary["strategy"] == "wf_selected", "wf_positive_windows"] = int(
            windows_df["positive_oos"].sum()
        )
        summary.loc[summary["strategy"] == "wf_selected", "wf_required_windows"] = required
        summary.loc[summary["strategy"] == "wf_selected", "wf_positive_pass"] = bool(
            int(windows_df["positive_oos"].sum()) >= required
        )
        summary.loc[summary["strategy"] == "wf_selected", "windows_beat_full_top"] = int(
            windows_df["beat_full_top"].sum()
        )
        summary.loc[summary["strategy"] == "wf_selected", "median_oos_rank_pct"] = float(
            windows_df["test_rank_pct"].median()
        )
    return windows_df, summary


def run_pbo_monthly(
    scenario: Scenario,
    daily_returns: pd.DataFrame,
    weights: np.ndarray,
    asset_cols: list[str],
) -> dict[str, object]:
    aligned = daily_returns[asset_cols].dropna(how="any")
    monthly = (1.0 + aligned).resample("ME").prod() - 1.0
    monthly = monthly.dropna(how="any")
    equity = simulate_rebalanced_matrix(monthly, weights, freq="M")
    returns = equity[1:] / equity[:-1] - 1.0
    result = pbo(returns, n_blocks=PBO_BLOCKS)
    return {
        "scenario": scenario.slug,
        "pbo": float(result.pbo),
        "pbo_gate": pbo_gate(float(result.pbo)),
        "n_blocks": int(result.n_blocks),
        "n_combinations": int(result.n_combinations),
        "pbo_n_configs": int(weights.shape[0]),
        "n_months": int(returns.shape[0]),
        "logit_median": float(np.median(result.logits)),
    }


def run_all_scenarios(
    daily_returns: pd.DataFrame,
    leverage_step: float,
    diversifier_step_pct: int,
    batch_size: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    grid_summaries = []
    pbo_rows = []
    wf_windows_all = []
    wf_summary_all = []
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    for scenario in SCENARIOS:
        meta, weights, asset_cols = generate_candidate_table(
            scenario,
            leverage_step=leverage_step,
            diversifier_step_pct=diversifier_step_pct,
        )
        scored = score_candidates_for_period(daily_returns, meta, weights, asset_cols, batch_size)
        scored.to_csv(RESULTS_DIR / f"grid_{scenario.slug}.csv", index=False)
        top = scored.iloc[0]
        full_top_id = int(top["candidate_id"])
        grid_summaries.append(
            {
                "scenario": scenario.slug,
                "description": scenario.description,
                "n_configs": len(scored),
                "top_candidate_id": full_top_id,
                "top_portfolio": top["portfolio"],
                "top_fitness_score": float(top["fitness_score"]),
                "top_cagr": float(top["cagr"]),
                "top_mdd": float(top["mdd"]),
                "top_vol": float(top["vol"]),
                "top_sharpe": float(top["sharpe"]),
                "top_calmar": float(top["calmar"]),
                "top_terminal": float(top["terminal"]),
                "start_date": top["start_date"],
                "end_date": top["end_date"],
            }
        )
        pbo_rows.append(run_pbo_monthly(scenario, daily_returns, weights, asset_cols))
        wf_windows, wf_summary = run_walk_forward(
            scenario, daily_returns, meta, weights, asset_cols, full_top_id, batch_size
        )
        wf_windows_all.append(wf_windows)
        wf_summary_all.append(wf_summary)
    grid_summary = pd.DataFrame(grid_summaries)
    pbo_summary = pd.DataFrame(pbo_rows)
    wf_windows_frame = pd.concat(wf_windows_all, ignore_index=True)
    wf_summary_frame = pd.concat(wf_summary_all, ignore_index=True)
    grid_summary.to_csv(RESULTS_DIR / "grid_summary.csv", index=False)
    pbo_summary.to_csv(RESULTS_DIR / "pbo_monthly_summary.csv", index=False)
    wf_windows_frame.to_csv(RESULTS_DIR / "walk_forward_windows.csv", index=False)
    wf_summary_frame.to_csv(RESULTS_DIR / "walk_forward_summary.csv", index=False)
    return grid_summary, pbo_summary, wf_windows_frame, wf_summary_frame


def _fmt_pct(value: float, digits: int = 2) -> str:
    if not math.isfinite(value):
        return "n/a"
    return f"{value * 100:.{digits}f}%"


def _fmt_num(value: float, digits: int = 3) -> str:
    if not math.isfinite(value):
        return "n/a"
    return f"{value:.{digits}f}"


def _fmt_x(value: float, digits: int = 2) -> str:
    if not math.isfinite(value):
        return "n/a"
    return f"{value:.{digits}f}x"


def markdown_table(
    frame: pd.DataFrame,
    columns: list[str],
    formats: dict[str, str] | None = None,
    limit: int | None = None,
) -> str:
    formats = formats or {}
    data = frame.head(limit) if limit is not None else frame
    if data.empty:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in data.iterrows():
        cells = []
        for col in columns:
            value = row.get(col, "")
            fmt = formats.get(col, "")
            if fmt == "pct":
                cells.append(_fmt_pct(float(value)))
            elif fmt == "num":
                cells.append(_fmt_num(float(value)))
            elif fmt == "x":
                cells.append(_fmt_x(float(value)))
            elif fmt == "score":
                cells.append(f"{float(value):.2f}")
            elif fmt == "bool":
                cells.append("PASS" if bool(value) else "FAIL")
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def best_constrained_rows() -> pd.DataFrame:
    rows = []
    for path in sorted(RESULTS_DIR.glob("grid_*.csv")):
        if path.name == "grid_summary.csv":
            continue
        scenario = path.stem.removeprefix("grid_")
        grid = pd.read_csv(path)
        for threshold in (0.30, 0.40, 0.50, 0.60):
            eligible = grid[grid["mdd"] >= -threshold].sort_values("cagr", ascending=False)
            if eligible.empty:
                continue
            row = eligible.iloc[0].to_dict()
            rows.append({"scenario": scenario, "mdd_floor": -threshold, **row})
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame.to_csv(RESULTS_DIR / "best_cagr_by_mdd_floor.csv", index=False)
    return frame


def write_report(
    asset_equity: pd.DataFrame,
    reference_metrics: pd.DataFrame,
    grid_summary: pd.DataFrame,
    pbo_summary: pd.DataFrame,
    wf_summary: pd.DataFrame,
    constrained: pd.DataFrame,
    leverage_step: float,
    diversifier_step_pct: int,
) -> None:
    merged_summary = grid_summary.merge(pbo_summary, on="scenario", how="left")
    wf_selected = wf_summary[wf_summary["strategy"] == "wf_selected"]
    wf_cols = [
        "scenario",
        "wf_positive_windows",
        "wf_required_windows",
        "wf_positive_pass",
        "windows_beat_full_top",
        "median_oos_rank_pct",
    ]
    merged_summary = merged_summary.merge(wf_selected[wf_cols], on="scenario", how="left")
    best = merged_summary.sort_values("top_fitness_score", ascending=False).iloc[0]
    constrained_sorted = constrained.sort_values(["mdd_floor", "cagr"], ascending=[False, False])
    rsc_ref = reference_metrics[reference_metrics["name"] == "RSC_like_35_40_25"].iloc[0]
    user_p4 = reference_metrics[
        reference_metrics["name"] == "user_P4_UPRO_ZROZ_KMLM_GOLD"
    ].iloc[0]
    proposal_upro_zroz = reference_metrics[
        reference_metrics["name"] == "proposal_16UPRO_plus_ZROZ"
    ].iloc[0]
    proposal_upro_cash = reference_metrics[
        reference_metrics["name"] == "proposal_16UPRO_4CASH"
    ].iloc[0]
    proposal_upro_best = reference_metrics[
        reference_metrics["name"] == "proposal_16UPRO_plus_GDE"
    ].iloc[0]
    proposal_sso = reference_metrics[reference_metrics["name"] == "proposal_20SSO"].iloc[0]
    proposal_upro20 = reference_metrics[reference_metrics["name"] == "proposal_20UPRO"].iloc[0]
    proposal_base = reference_metrics[
        reference_metrics["name"] == "proposal_base_25Z_25R_30G_20CASH"
    ].iloc[0]
    comparable_2000 = merged_summary[merged_summary["scenario"] != "kmlm_long"].sort_values(
        "top_fitness_score", ascending=False
    ).iloc[0]

    summary_cols = [
        "scenario",
        "n_configs",
        "top_portfolio",
        "top_cagr",
        "top_mdd",
        "top_sharpe",
        "top_calmar",
        "pbo",
        "pbo_gate",
        "wf_positive_windows",
        "wf_required_windows",
        "wf_positive_pass",
    ]
    ref_cols = [
        "name",
        "weights",
        "effective_equity",
        "effective_mf",
        "effective_gold",
        "effective_zroz",
        "cagr",
        "mdd",
        "sharpe",
        "calmar",
        "terminal_vs_spy",
        "terminal_vs_rsc",
    ]
    constrained_cols = ["scenario", "mdd_floor", "portfolio", "cagr", "mdd", "sharpe", "calmar"]
    formats = {
        "top_cagr": "pct",
        "top_mdd": "pct",
        "top_sharpe": "num",
        "top_calmar": "num",
        "pbo": "num",
        "wf_positive_pass": "bool",
        "effective_equity": "pct",
        "effective_mf": "pct",
        "effective_gold": "pct",
        "effective_zroz": "pct",
        "cagr": "pct",
        "mdd": "pct",
        "sharpe": "num",
        "calmar": "num",
        "terminal_vs_spy": "x",
        "terminal_vs_rsc": "x",
        "mdd_floor": "pct",
    }
    report = (
        "# Unstacked Equity + Diversifier Grid\n\n"
        "Status: research-only diagnostic. No deployment, paper-trade label or mandate change.\n\n"
        "## Summary\n\n"
        f"- Testfol.io assets/custom tickers were downloaded one by one; raw payloads/responses live in `{RAW_DIR.relative_to(REPO_ROOT)}`.\n"
        f"- Asset cache span after outer join: `{asset_equity.index.min().date()}..{asset_equity.index.max().date()}`.\n"
        f"- Grid: target LETF leverage `2.00..3.00` step `{leverage_step:.2f}`; "
        f"diversifier simplex step `{diversifier_step_pct}%`; monthly rebalance.\n"
        f"- Best rank-fitness screen row: `{best['scenario']}` -> **{best['top_portfolio']}**, "
        f"CAGR `{_fmt_pct(float(best['top_cagr']))}`, MDD `{_fmt_pct(float(best['top_mdd']))}`, "
        f"Sharpe `{_fmt_num(float(best['top_sharpe']))}`, Calmar `{_fmt_num(float(best['top_calmar']))}`.\n"
        f"- The best row's scenario PBO is `{float(best['pbo']):.3f}` (`{best['pbo_gate']}`), "
        "so it is a screen result, not a promoted allocation.\n\n"
        "## Verdict\n\n"
        "The unstacked SSO/UPRO structure is a useful SPY-relative diagnostic, but "
        "it does **not** improve the current RSC-style risk/return profile. The "
        f"closest user-style 1988+ row (`user_P4`) has CAGR `{_fmt_pct(float(user_p4['cagr']))}` "
        f"and MDD `{_fmt_pct(float(user_p4['mdd']))}`, but only "
        f"`{_fmt_x(float(user_p4['terminal_vs_rsc']))}` terminal wealth versus the "
        "RSC-like reference on the common window. The RSC-like reference is "
        f"CAGR `{_fmt_pct(float(rsc_ref['cagr']))}`, MDD `{_fmt_pct(float(rsc_ref['mdd']))}`, "
        f"Sharpe `{_fmt_num(float(rsc_ref['sharpe']))}`. Among comparable 2000+ grids, "
        f"the best screen row is `{comparable_2000['scenario']}` at CAGR "
        f"`{_fmt_pct(float(comparable_2000['top_cagr']))}` and MDD "
        f"`{_fmt_pct(float(comparable_2000['top_mdd']))}`, with PBO "
        f"`{float(comparable_2000['pbo']):.3f}` (`{comparable_2000['pbo_gate']}`). "
        "The only scenario with PBO below 0.5 is `kmlm_long`, but it uses the "
        "KMLM-only 1988+ window and fails the WF positive-window threshold. "
        "Therefore the robust action remains: keep this as a diagnostic, not as "
        "an RSC replacement or mandate change `[advances_fin_ml, p.208-211]`, "
        "`[testing_tuning, p.327-335]`. CTA is not ranked in the primary grid "
        "because there is no comparable long-history Testfol.io simulated CTA sleeve; "
        "KMLM/DBMF are the long-history MF proxies used here.\n\n"
        "The later fixed `25% ZROZ / 25% RSST70_30 / 30% GDE` proposal is more "
        "interesting than the plain unstacked grid because GDE/RSST supply embedded "
        "gold and MF while leaving room for a small LETF completion sleeve. The exact "
        f"100%-equity version with `16% UPRO + 4% ZROZ` reaches CAGR "
        f"`{_fmt_pct(float(proposal_upro_zroz['cagr']))}`, MDD "
        f"`{_fmt_pct(float(proposal_upro_zroz['mdd']))}`, terminal "
        f"`{_fmt_x(float(proposal_upro_zroz['terminal_vs_rsc']))}` vs RSC. The "
        f"clean `16% UPRO + 4% CASH` version is CAGR "
        f"`{_fmt_pct(float(proposal_upro_cash['cagr']))}`, MDD "
        f"`{_fmt_pct(float(proposal_upro_cash['mdd']))}`, terminal "
        f"`{_fmt_x(float(proposal_upro_cash['terminal_vs_rsc']))}` vs RSC. The highest "
        f"CAGR variant among the 4%-top-up choices is `+GDE`, CAGR "
        f"`{_fmt_pct(float(proposal_upro_best['cagr']))}`, MDD "
        f"`{_fmt_pct(float(proposal_upro_best['mdd']))}`, terminal "
        f"`{_fmt_x(float(proposal_upro_best['terminal_vs_rsc']))}` vs RSC, but it lifts "
        "effective equity above 100%. The lower-vol `20% SSO` version gives "
        f"CAGR `{_fmt_pct(float(proposal_sso['cagr']))}`, MDD "
        f"`{_fmt_pct(float(proposal_sso['mdd']))}`, terminal "
        f"`{_fmt_x(float(proposal_sso['terminal_vs_rsc']))}` vs RSC. The fully "
        f"allocated `20% UPRO` version is a different risk budget: effective equity "
        f"`{_fmt_pct(float(proposal_upro20['effective_equity']))}`, CAGR "
        f"`{_fmt_pct(float(proposal_upro20['cagr']))}`, MDD "
        f"`{_fmt_pct(float(proposal_upro20['mdd']))}`, terminal "
        f"`{_fmt_x(float(proposal_upro20['terminal_vs_rsc']))}` vs RSC, with worse "
        "Sharpe/Calmar than the 16% UPRO variants. The 20%-cash "
        f"base is defensive (CAGR `{_fmt_pct(float(proposal_base['cagr']))}`, MDD "
        f"`{_fmt_pct(float(proposal_base['mdd']))}`) but gives up too much terminal "
        "wealth. Net: the construction is a viable fixed reference row, but the "
        "RSC-like reference still has the superior drawdown/Sharpe/Calmar trade-off "
        "for this repo's current objective `[systematic_trading, p.185-188]`.\n\n"
        "## Method\n\n"
        "Each equity carrier is built from the user's Testfol.io custom tickers "
        "`SPYSIM?L=2&E=0.91` and `SPYSIM?L=3&E=0.91`. For a target internal "
        "LETF leverage `L` in `[2,3]`, capital weights are `(3-L)/L` in SSO-like "
        "and `(L-2)/L` in UPRO-like, giving effective equity beta "
        "`2*w_SSO + 3*w_UPRO = 1.0`. The leftover capital `1 - 1/L` is allocated "
        "across cash, gold, ZROZ and MF sleeves. LETF daily reset and cost caveats "
        "follow `[leverage_for_the_long_run, p.13]`; monthly rebalancing and "
        "robustness diagnostics follow `[systematic_trading, p.185-188]`, "
        "`[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.\n\n"
        "## Scenario Summary\n\n"
        f"{markdown_table(merged_summary[summary_cols], summary_cols, formats)}\n\n"
        "## Named References\n\n"
        f"{markdown_table(reference_metrics[ref_cols], ref_cols, formats)}\n\n"
        "## Best CAGR By MDD Floor\n\n"
        f"{markdown_table(constrained_sorted[constrained_cols], constrained_cols, formats, limit=20)}\n\n"
        "## Interpretation\n\n"
        "This study answers a narrower question than RSC: can embedded SSO/UPRO "
        "capital efficiency carry 100% equity beta while diversifiers use the "
        "unencumbered capital? The screen can produce attractive SPY-relative rows, "
        "but any argmax must be discounted when PBO rejects or WF selection is unstable. "
        "Compare fixed/simple rows against the named references and the RSC-like row "
        "rather than treating the top grid row as a winner.\n\n"
        "## Artifacts\n\n"
        f"- Asset curves: `{(RESULTS_DIR / 'asset_equity_curves.csv').relative_to(REPO_ROOT)}`.\n"
        f"- Reference metrics: `{(RESULTS_DIR / 'named_references.csv').relative_to(REPO_ROOT)}`.\n"
        f"- Grid summary: `{(RESULTS_DIR / 'grid_summary.csv').relative_to(REPO_ROOT)}`.\n"
        f"- Scenario grids: `{RESULTS_DIR.relative_to(REPO_ROOT)}/grid_<scenario>.csv`.\n"
        f"- PBO summary: `{(RESULTS_DIR / 'pbo_monthly_summary.csv').relative_to(REPO_ROOT)}`.\n"
        f"- Walk-forward windows: `{(RESULTS_DIR / 'walk_forward_windows.csv').relative_to(REPO_ROOT)}`.\n"
    )
    REPORT_MD.write_text(report, encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force-download", action="store_true", help="refresh all Testfol.io raw files")
    parser.add_argument("--skip-download", action="store_true", help="use existing raw files only")
    parser.add_argument("--leverage-step", type=float, default=DEFAULT_LEVERAGE_STEP)
    parser.add_argument("--div-step", type=int, default=DEFAULT_DIVERSIFIER_STEP_PCT)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.skip_download:
        asset_equity = load_asset_curves_from_raw()
    else:
        asset_equity = download_asset_curves(force=args.force_download)
    daily_returns = build_daily_returns(asset_equity)
    reference_metrics = evaluate_named_references(daily_returns)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    reference_metrics.to_csv(RESULTS_DIR / "named_references.csv", index=False)
    grid_summary, _pbo_summary, _wf_windows, wf_summary = run_all_scenarios(
        daily_returns,
        leverage_step=args.leverage_step,
        diversifier_step_pct=args.div_step,
        batch_size=args.batch_size,
    )
    pbo_summary = pd.read_csv(RESULTS_DIR / "pbo_monthly_summary.csv")
    constrained = best_constrained_rows()
    write_report(
        asset_equity,
        reference_metrics,
        grid_summary,
        pbo_summary,
        wf_summary,
        constrained,
        leverage_step=args.leverage_step,
        diversifier_step_pct=args.div_step,
    )
    print(f"wrote {REPORT_MD.relative_to(REPO_ROOT)}")
    print(grid_summary[["scenario", "top_portfolio", "top_cagr", "top_mdd", "top_sharpe"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
