#!/usr/bin/env python3
"""Fixed RSC-like portfolios versus SPY across monthly rolling windows.

This is a research-only diagnostic: the portfolios are fixed ex ante and are not
optimized. Rolling-window evaluation is used to measure path dependence and
benchmark-relative persistence rather than to promote a live allocation
`[systematic_trading, p.185-188]`, `[testing_tuning, p.327-335]`.
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
from typing import Any

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

STUDY_DIR = Path(__file__).resolve().parent
RAW_DIR = STUDY_DIR / "raw"
RESULTS_DIR = STUDY_DIR / "results"
PLOTS_DIR = STUDY_DIR / "plots"
REPORT_MD = STUDY_DIR / "REPORT.md"

ENDPOINT = "https://testfol.io/api/backtest"
START_VALUE = 10_000.0
TRADING_DAYS = 252
HORIZONS_YEARS = (3, 5, 10, 15, 20)
HORIZON_WEIGHTS = {horizon: horizon / sum(HORIZONS_YEARS) for horizon in HORIZONS_YEARS}


@dataclass(frozen=True)
class AssetSpec:
    alias: str
    ticker: str
    role: str


@dataclass(frozen=True)
class PortfolioSpec:
    name: str
    weights: dict[str, float]
    note: str


@dataclass(frozen=True)
class WindowSpec:
    horizon_years: int
    start_date: pd.Timestamp
    end_exclusive_date: pd.Timestamp


ASSET_SPECS: tuple[AssetSpec, ...] = (
    AssetSpec("SPY", "SPYSIM", "S&P 500 benchmark"),
    AssetSpec("NTSX", "NTSXSIM", "90/60 US stock/Treasury reference sleeve"),
    AssetSpec("GDE", "GDESIM", "90/90 S&P 500/gold reference sleeve"),
    AssetSpec("ZROZ", "ZROZSIM", "25y+ zero-coupon Treasury sleeve"),
    AssetSpec("DBMF", "DBMFSIM", "managed-futures proxy"),
    AssetSpec("KMLM", "KMLMSIM", "managed-futures proxy"),
    AssetSpec("CASH_E_MINUS_2", "CASHX?E=-2", "cash + 2% financing leg"),
    AssetSpec("SSO_E091", "SPYSIM?L=2&E=0.91", "2x S&P 500 LETF proxy"),
    AssetSpec("UPRO_E091", "SPYSIM?L=3&E=0.91", "3x S&P 500 LETF proxy"),
)

ASSET_LABELS = {
    "SPY": "SPY",
    "NTSX": "NTSX",
    "GDE": "GDE",
    "ZROZ": "ZROZ",
    "DBMF": "DBMF",
    "KMLM": "KMLM",
    "CASH_E_MINUS_2": "CASH+2%",
    "SSO_E091": "SSO-like",
    "UPRO_E091": "UPRO-like",
    "RSST70_30": "RSST70/30",
}

PORTFOLIO_LABELS = {
    "p25_rsst_25_ntsx_25_gde_25_zroz": "25 RSST / 25 NTSX / 25 GDE / 25 ZROZ",
    "p50_rsst_25_gde_25_zroz": "50 RSST / 25 GDE / 25 ZROZ",
    "p25_rsst_50_gde_25_zroz": "25 RSST / 50 GDE / 25 ZROZ",
    "p375_rsst_375_gde_25_zroz": "37.5 RSST / 37.5 GDE / 25 ZROZ",
    "p16_upro_29_zroz_25_rsst_30_gde": "16 UPRO / 29 ZROZ / 25 RSST / 30 GDE",
    "sso_proportional_scaled_core": "SSO proportional core",
    "sso_keep_rsst_gde_reduce_zroz": "24 SSO / 21 ZROZ / 25 RSST / 30 GDE",
    "sso_keep_zroz_scale_rsst_gde": "SSO keep 29 ZROZ",
}

PORTFOLIO_ANALYSES = {
    "p16_upro_29_zroz_25_rsst_30_gde": {
        "strategy": "Small UPRO sleeve used to complete 100% effective equity while keeping high ZROZ and RSST/GDE diversification.",
        "expectation": "Best candidate if the goal is to maximize rolling dominance versus SPY while accepting LETF-level absolute drawdown. The forward expectation is positive, but it depends on the UPRO sleeve not being punished by long sideways/high-volatility regimes.",
        "why": "It worked because it combines full effective equity beta with diversifier convexity: ZROZ helps in disinflationary crashes, GDE carries equity/gold, RSST adds managed futures, and UPRO adds upside when SPY compounds without consuming much capital.",
    },
    "p25_rsst_50_gde_25_zroz": {
        "strategy": "No external LETF; concentrated in GDE, with RSST and ZROZ as counterweights.",
        "expectation": "Good candidate for investors who prefer to avoid UPRO/SSO and accept lower rolling consistency. Future performance should depend more on gold/GDE and the real-inflation regime.",
        "why": "It did very well full-period because GDE/gold captured a historically favorable decade and reduced the need for explicit leverage, but the rolling path was less uniform than the completion-sleeve versions.",
    },
    "sso_keep_rsst_gde_reduce_zroz": {
        "strategy": "SSO version that keeps RSST/GDE equal to the UPRO case and reduces ZROZ to close 100% effective equity.",
        "expectation": "Best SSO candidate for relative investor experience: slightly lower return than UPRO, but smoother relative drawdown. Forward expectation is more balanced if behavioral tolerance matters.",
        "why": "It got this result because SSO delivers equity beta with less path-dependence than UPRO, while preserving RSST/GDE kept crisis and trend diversification. The trade-off was cutting ZROZ from 29% to 21%.",
    },
    "sso_proportional_scaled_core": {
        "strategy": "Proportional SSO version: scales the original ZROZ/RSST/GDE block to make room for SSO and close 100% effective equity.",
        "expectation": "Robust and clean alternative if the preference is not to choose which sleeve to cut. Forward expectation is good, but slightly diluted because all diversifiers are reduced together.",
        "why": "It stayed close to the leaders because it preserved the economic architecture of the UPRO case with a less aggressive LETF. It lagged the keep-RSST/GDE SSO version because it also cut RSST/GDE, which were valuable sleeves in the sample.",
    },
    "sso_keep_zroz_scale_rsst_gde": {
        "strategy": "SSO version that preserves ZROZ at 29% and reduces RSST/GDE to close 100% effective equity.",
        "expectation": "More defensive against duration shocks, but less powerful if gold and managed futures keep adding value. Useful as a sensitivity, not as the best base case.",
        "why": "The result fell because preserving ZROZ required cutting RSST and GDE, reducing two sources that historically improved the return/risk profile in this data set.",
    },
    "p375_rsst_375_gde_25_zroz": {
        "strategy": "Simple no-LETF rule: balanced RSST and GDE, with ZROZ fixed at 25%.",
        "expectation": "Good conservative/simplex reference. Forward expectation is stable if RSST/GDE remain complementary, but without full effective equity it should lag completion rows in bull markets.",
        "why": "It was consistent over longer horizons, but ranked lower because it has less effective equity and less growth engine than UPRO/SSO, compensated by lower absolute drawdown.",
    },
    "p50_rsst_25_gde_25_zroz": {
        "strategy": "RSST-heavy rule, leaning more on managed futures stacked with equity.",
        "expectation": "May improve in strong macro-trend regimes, but it was not the best weighted-average result. Forward expectation depends heavily on persistent quality from the RSST70/30 proxy.",
        "why": "The high RSST weight increased trend diversification, but reduced exposure to GDE/gold, which explained a large part of the best full-period and rolling results.",
    },
    "p25_rsst_25_ntsx_25_gde_25_zroz": {
        "strategy": "Equal-weight 25/25/25/25 across NTSX, RSST, GDE and ZROZ.",
        "expectation": "Better as an educational benchmark than as the main choice. Forward expectation is defensive, but likely diluted if the objective is to beat SPY in rolling terminal wealth.",
        "why": "It ranked last because NTSX reduced the relative potency of the mix: it added intermediate-bond exposure and lower equity exposure, while the winning rows used UPRO/SSO or high GDE to capture more upside.",
    },
}


class TestfolioClient:
    """Anonymous Testfol.io `/api/backtest` client for one-series pulls."""

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
                "User-Agent": "market-lab/fixed-portfolio-rolling-spy-comparison",
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
    if {"SPY", "DBMF", "KMLM", "CASH_E_MINUS_2"}.issubset(returns.columns):
        returns["RSST70_30"] = (
            returns["SPY"]
            + 0.70 * returns["DBMF"]
            + 0.30 * returns["KMLM"]
            - returns["CASH_E_MINUS_2"]
        )
    return returns


def exposure_breakdown(weights: dict[str, float]) -> dict[str, float]:
    """Approximate economic sleeves for fixed explanatory portfolios.

    GDE is treated as 90% S&P + 90% gold, RSST70/30 as 100% S&P + 100% MF,
    and NTSX as 90% S&P + 60% intermediate Treasury exposure. These are
    explanatory decompositions, not validation gates `[leverage_for_the_long_run,
    p.13]`, `[risk_parity, ch.5]`.
    """

    return {
        "effective_equity": (
            weights.get("SPY", 0.0)
            + 2.0 * weights.get("SSO_E091", 0.0)
            + 3.0 * weights.get("UPRO_E091", 0.0)
            + 0.90 * weights.get("NTSX", 0.0)
            + weights.get("RSST70_30", 0.0)
            + 0.90 * weights.get("GDE", 0.0)
        ),
        "effective_mf": weights.get("RSST70_30", 0.0),
        "effective_gold": 0.90 * weights.get("GDE", 0.0),
        "effective_zroz": weights.get("ZROZ", 0.0),
        "effective_intermediate_treasury": 0.60 * weights.get("NTSX", 0.0),
    }


def _sso_proportional_variant() -> dict[str, float]:
    base = {"ZROZ": 0.29, "RSST70_30": 0.25, "GDE": 0.30}
    base_capital = sum(base.values())
    base_equity = exposure_breakdown(base)["effective_equity"]
    equity_per_capital = base_equity / base_capital
    sso = (1.0 - equity_per_capital) / (2.0 - equity_per_capital)
    scale = (1.0 - sso) / base_capital
    return {"SSO_E091": sso, **{asset: weight * scale for asset, weight in base.items()}}


def _sso_keep_zroz_variant() -> dict[str, float]:
    zroz = 0.29
    base = {"RSST70_30": 0.25, "GDE": 0.30}
    base_capital = sum(base.values())
    base_equity = exposure_breakdown(base)["effective_equity"]
    remaining_capital = 1.0 - zroz
    equity_per_capital = base_equity / base_capital
    sso = (1.0 - equity_per_capital * remaining_capital) / (2.0 - equity_per_capital)
    scale = (remaining_capital - sso) / base_capital
    return {"SSO_E091": sso, "ZROZ": zroz, **{a: w * scale for a, w in base.items()}}


def _sso_keep_rsst_gde_variant() -> dict[str, float]:
    fixed = {"RSST70_30": 0.25, "GDE": 0.30}
    fixed_equity = exposure_breakdown(fixed)["effective_equity"]
    sso = (1.0 - fixed_equity) / 2.0
    zroz = 1.0 - sum(fixed.values()) - sso
    return {"SSO_E091": sso, "ZROZ": zroz, **fixed}


def portfolio_specs() -> list[PortfolioSpec]:
    """Fixed rules requested by the user plus SSO analogues that close 100% equity."""

    return [
        PortfolioSpec(
            "p25_rsst_25_ntsx_25_gde_25_zroz",
            {"RSST70_30": 0.25, "NTSX": 0.25, "GDE": 0.25, "ZROZ": 0.25},
            "Equal 25/25/25/25 RSST/NTSX/GDE/ZROZ.",
        ),
        PortfolioSpec(
            "p50_rsst_25_gde_25_zroz",
            {"RSST70_30": 0.50, "GDE": 0.25, "ZROZ": 0.25},
            "RSST-heavy three-sleeve fixed rule.",
        ),
        PortfolioSpec(
            "p25_rsst_50_gde_25_zroz",
            {"RSST70_30": 0.25, "GDE": 0.50, "ZROZ": 0.25},
            "GDE-heavy three-sleeve fixed rule.",
        ),
        PortfolioSpec(
            "p375_rsst_375_gde_25_zroz",
            {"RSST70_30": 0.375, "GDE": 0.375, "ZROZ": 0.25},
            "Balanced RSST/GDE fixed rule with 25% ZROZ.",
        ),
        PortfolioSpec(
            "p16_upro_29_zroz_25_rsst_30_gde",
            {"UPRO_E091": 0.16, "ZROZ": 0.29, "RSST70_30": 0.25, "GDE": 0.30},
            "UPRO completion sleeve calibrated to 100% effective equity.",
        ),
        PortfolioSpec(
            "sso_proportional_scaled_core",
            _sso_proportional_variant(),
            "SSO analogue scaling the original RSST/GDE/ZROZ block proportionally.",
        ),
        PortfolioSpec(
            "sso_keep_rsst_gde_reduce_zroz",
            _sso_keep_rsst_gde_variant(),
            "SSO analogue keeping RSST and GDE fixed, reducing ZROZ.",
        ),
        PortfolioSpec(
            "sso_keep_zroz_scale_rsst_gde",
            _sso_keep_zroz_variant(),
            "SSO analogue keeping ZROZ fixed and scaling RSST/GDE.",
        ),
    ]


def portfolio_weight_rows(specs: list[PortfolioSpec]) -> pd.DataFrame:
    rows = []
    for spec in specs:
        if not math.isclose(sum(spec.weights.values()), 1.0, abs_tol=1e-10):
            raise ValueError(f"weights for {spec.name} do not sum to 1.0")
        row: dict[str, object] = {
            "portfolio": spec.name,
            "weights": format_weights(spec.weights),
            "note": spec.note,
            **exposure_breakdown(spec.weights),
        }
        for asset, weight in spec.weights.items():
            row[f"w_{asset}"] = weight
        rows.append(row)
    return pd.DataFrame(rows)


def format_weight_value(weight: float) -> str:
    pct = weight * 100.0
    if math.isclose(pct, round(pct), abs_tol=0.005):
        return f"{int(round(pct))}%"
    return f"{pct:.2f}%"


def format_weights(weights: dict[str, float]) -> str:
    parts = []
    for asset, weight in weights.items():
        if weight <= 1e-10:
            continue
        parts.append(f"{format_weight_value(weight)} {ASSET_LABELS.get(asset, asset)}")
    return " / ".join(parts)


def monthly_start_dates(index: pd.DatetimeIndex) -> pd.Series:
    if index.empty:
        return pd.Series(dtype="datetime64[ns]")
    dates = pd.DatetimeIndex(index).sort_values().unique()
    rows = pd.DataFrame({"date": dates})
    rows["month_id"] = rows["date"].dt.year * 12 + rows["date"].dt.month
    return rows.groupby("month_id", sort=True)["date"].first()


def build_rolling_windows(
    index: pd.DatetimeIndex,
    horizons: tuple[int, ...] = HORIZONS_YEARS,
) -> list[WindowSpec]:
    starts_by_month = monthly_start_dates(index)
    windows: list[WindowSpec] = []
    for horizon in horizons:
        month_delta = horizon * 12
        for start_month, start_date in starts_by_month.items():
            end_month = int(start_month) + month_delta
            if end_month not in starts_by_month.index:
                continue
            windows.append(
                WindowSpec(
                    horizon_years=horizon,
                    start_date=pd.Timestamp(start_date),
                    end_exclusive_date=pd.Timestamp(starts_by_month.loc[end_month]),
                )
            )
    return windows


def simulate_monthly_rebalanced_equity(
    asset_returns: pd.DataFrame,
    weights: dict[str, float],
) -> pd.Series:
    aligned = asset_returns[list(weights)].dropna(how="any")
    if aligned.empty:
        return pd.Series(dtype=float, name="portfolio")
    target = pd.Series(weights, dtype=float)
    if not math.isclose(float(target.sum()), 1.0, abs_tol=1e-8):
        raise ValueError(f"weights must sum to 1.0, got {target.sum():.8f}")
    target = target.reindex(aligned.columns).astype(float)
    returns = aligned.to_numpy(dtype=float)
    month_codes = np.asarray([date.year * 12 + date.month for date in aligned.index], dtype=int)
    target_values = target.to_numpy(dtype=float)
    out = np.empty(len(aligned), dtype=float)
    value = 1.0
    holdings = target_values * value
    current_month: int | None = None
    for i, month in enumerate(month_codes):
        if month != current_month:
            holdings = target_values * value
            current_month = int(month)
        holdings = holdings * (1.0 + returns[i])
        value = float(holdings.sum())
        out[i] = value
    return pd.Series(out, index=aligned.index, name="portfolio")


def max_drawdown_from_equity(equity: pd.Series) -> float:
    values = np.concatenate([[1.0], equity.to_numpy(dtype=float)])
    peaks = np.maximum.accumulate(values)
    drawdowns = values / peaks - 1.0
    return float(drawdowns.min())


def longest_streak(mask: pd.Series) -> int:
    longest = 0
    current = 0
    for value in mask.astype(bool):
        if value:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def evaluate_window(
    daily_returns: pd.DataFrame,
    portfolio: PortfolioSpec,
    window: WindowSpec,
) -> dict[str, object] | None:
    window_returns = daily_returns.loc[
        (daily_returns.index >= window.start_date)
        & (daily_returns.index < window.end_exclusive_date),
        ["SPY", *portfolio.weights.keys()],
    ].dropna(how="any")
    if len(window_returns) < 2:
        return None

    portfolio_equity = simulate_monthly_rebalanced_equity(window_returns, portfolio.weights)
    spy_equity = (1.0 + window_returns.loc[portfolio_equity.index, "SPY"]).cumprod()
    relative = portfolio_equity / spy_equity
    years = (portfolio_equity.index[-1] - window.start_date).days / 365.25
    terminal_portfolio = float(portfolio_equity.iloc[-1])
    terminal_spy = float(spy_equity.iloc[-1])
    terminal_ratio = terminal_portfolio / terminal_spy
    relative_mdd = max_drawdown_from_equity(relative)
    portfolio_mdd = max_drawdown_from_equity(portfolio_equity)
    spy_mdd = max_drawdown_from_equity(spy_equity)

    return {
        "portfolio": portfolio.name,
        "horizon_years": window.horizon_years,
        "start_date": window.start_date.date().isoformat(),
        "end_date": portfolio_equity.index[-1].date().isoformat(),
        "end_exclusive_date": window.end_exclusive_date.date().isoformat(),
        "n_trading_days": int(len(window_returns)),
        "years": float(years),
        "portfolio_terminal": terminal_portfolio,
        "spy_terminal": terminal_spy,
        "terminal_ratio_vs_spy": float(terminal_ratio),
        "log_terminal_ratio_vs_spy": float(math.log(terminal_ratio)),
        "final_hit_vs_spy": bool(terminal_ratio > 1.0),
        "time_above_spy_pct": float((relative > 1.0).mean()),
        "time_above_spy_days": int((relative > 1.0).sum()),
        "min_ratio_vs_spy": float(relative.min()),
        "max_ratio_vs_spy": float(relative.max()),
        "mean_ratio_vs_spy": float(relative.mean()),
        "relative_mdd_vs_spy": relative_mdd,
        "longest_under_spy_days": longest_streak(relative < 1.0),
        "portfolio_cagr": float(terminal_portfolio ** (1.0 / years) - 1.0),
        "spy_cagr": float(terminal_spy ** (1.0 / years) - 1.0),
        "excess_cagr": float(
            terminal_portfolio ** (1.0 / years) - terminal_spy ** (1.0 / years)
        ),
        "portfolio_mdd": portfolio_mdd,
        "spy_mdd": spy_mdd,
    }


def evaluate_rolling_windows(
    daily_returns: pd.DataFrame,
    specs: list[PortfolioSpec],
    horizons: tuple[int, ...] = HORIZONS_YEARS,
) -> pd.DataFrame:
    required = sorted({"SPY"}.union(*(set(spec.weights) for spec in specs)))
    common = daily_returns[required].dropna(how="any")
    windows = build_rolling_windows(common.index, horizons=horizons)
    rows = []
    for window in windows:
        for spec in specs:
            row = evaluate_window(common, spec, window)
            if row is not None:
                rows.append(row)
    return pd.DataFrame(rows)


def _quantile(series: pd.Series, q: float) -> float:
    clean = series.astype(float).replace([np.inf, -np.inf], np.nan).dropna()
    return float(clean.quantile(q)) if not clean.empty else math.nan


def summarize_by_horizon(rolling: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (portfolio, horizon), group in rolling.groupby(["portfolio", "horizon_years"], sort=True):
        terminal = group["terminal_ratio_vs_spy"].astype(float)
        log_terminal = group["log_terminal_ratio_vs_spy"].astype(float)
        time_above = group["time_above_spy_pct"].astype(float)
        relative_mdd = group["relative_mdd_vs_spy"].astype(float)
        rows.append(
            {
                "portfolio": portfolio,
                "horizon_years": int(horizon),
                "horizon_weight": HORIZON_WEIGHTS[int(horizon)],
                "n_windows": int(len(group)),
                "hit_rate": float(group["final_hit_vs_spy"].mean()),
                "mean_terminal_ratio": float(terminal.mean()),
                "mean_log_terminal_ratio": float(log_terminal.mean()),
                "geo_mean_terminal_ratio": float(math.exp(log_terminal.mean())),
                "min_terminal_ratio": float(terminal.min()),
                "p10_terminal_ratio": _quantile(terminal, 0.10),
                "p25_terminal_ratio": _quantile(terminal, 0.25),
                "median_terminal_ratio": _quantile(terminal, 0.50),
                "p75_terminal_ratio": _quantile(terminal, 0.75),
                "p90_terminal_ratio": _quantile(terminal, 0.90),
                "mean_time_above_spy_pct": float(time_above.mean()),
                "p25_time_above_spy_pct": _quantile(time_above, 0.25),
                "mean_relative_mdd_vs_spy": float(relative_mdd.mean()),
                "worst_relative_mdd_vs_spy": float(relative_mdd.min()),
                "mean_longest_under_spy_days": float(group["longest_under_spy_days"].mean()),
                "p75_longest_under_spy_days": _quantile(group["longest_under_spy_days"], 0.75),
                "mean_excess_cagr": float(group["excess_cagr"].mean()),
                "p25_excess_cagr": _quantile(group["excess_cagr"], 0.25),
                "mean_portfolio_mdd": float(group["portfolio_mdd"].mean()),
                "mean_spy_mdd": float(group["spy_mdd"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(["portfolio", "horizon_years"]).reset_index(drop=True)


def summarize_weighted_final(horizon_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for portfolio, group in horizon_summary.groupby("portfolio", sort=True):
        weights = group["horizon_weight"].astype(float)
        weights = weights / weights.sum()
        row = {
            "portfolio": portfolio,
            "available_horizon_weight": float(group["horizon_weight"].sum()),
            "weighted_mean_log_terminal_ratio": float(
                np.average(group["mean_log_terminal_ratio"], weights=weights)
            ),
            "weighted_hit_rate": float(np.average(group["hit_rate"], weights=weights)),
            "weighted_time_above_spy": float(
                np.average(group["mean_time_above_spy_pct"], weights=weights)
            ),
            "weighted_p10_terminal_ratio": float(
                np.average(group["p10_terminal_ratio"], weights=weights)
            ),
            "weighted_p25_terminal_ratio": float(
                np.average(group["p25_terminal_ratio"], weights=weights)
            ),
            "weighted_median_terminal_ratio": float(
                np.average(group["median_terminal_ratio"], weights=weights)
            ),
            "weighted_mean_relative_mdd_vs_spy": float(
                np.average(group["mean_relative_mdd_vs_spy"], weights=weights)
            ),
            "weighted_worst_relative_mdd_vs_spy": float(
                np.average(group["worst_relative_mdd_vs_spy"], weights=weights)
            ),
            "weighted_mean_longest_under_spy_days": float(
                np.average(group["mean_longest_under_spy_days"], weights=weights)
            ),
            "weighted_mean_excess_cagr": float(
                np.average(group["mean_excess_cagr"], weights=weights)
            ),
        }
        row["weighted_geo_terminal_ratio"] = float(
            math.exp(row["weighted_mean_log_terminal_ratio"])
        )
        rows.append(row)
    final = pd.DataFrame(rows).sort_values(
        ["weighted_geo_terminal_ratio", "weighted_hit_rate", "weighted_time_above_spy"],
        ascending=[False, False, False],
    )
    final.insert(0, "rank", range(1, len(final) + 1))
    return final.reset_index(drop=True)


def summarize_full_period(daily_returns: pd.DataFrame, specs: list[PortfolioSpec]) -> pd.DataFrame:
    required = sorted({"SPY"}.union(*(set(spec.weights) for spec in specs)))
    common = daily_returns[required].dropna(how="any")
    rows = []
    for spec in specs:
        equity = simulate_monthly_rebalanced_equity(common, spec.weights)
        spy_equity = (1.0 + common.loc[equity.index, "SPY"]).cumprod()
        relative = equity / spy_equity
        years = (equity.index[-1] - equity.index[0]).days / 365.25
        terminal = float(equity.iloc[-1])
        spy_terminal = float(spy_equity.iloc[-1])
        rows.append(
            {
                "portfolio": spec.name,
                "start_date": equity.index[0].date().isoformat(),
                "end_date": equity.index[-1].date().isoformat(),
                "years": years,
                "portfolio_cagr": terminal ** (1.0 / years) - 1.0,
                "spy_cagr": spy_terminal ** (1.0 / years) - 1.0,
                "terminal_ratio_vs_spy": terminal / spy_terminal,
                "time_above_spy_pct": float((relative > 1.0).mean()),
                "portfolio_mdd": max_drawdown_from_equity(equity),
                "spy_mdd": max_drawdown_from_equity(spy_equity),
                "relative_mdd_vs_spy": max_drawdown_from_equity(relative),
                "longest_under_spy_days": longest_streak(relative < 1.0),
            }
        )
    return pd.DataFrame(rows).sort_values("terminal_ratio_vs_spy", ascending=False)


def _fmt_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _fmt_x(value: float) -> str:
    return f"{value:.2f}x"


def _fmt_num(value: float) -> str:
    return f"{value:.2f}"


def markdown_table(
    frame: pd.DataFrame,
    columns: list[str],
    formats: dict[str, str] | None = None,
) -> str:
    formats = formats or {}
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    lines = [header, sep]
    for _, row in frame.iterrows():
        cells = []
        for col in columns:
            value = row[col]
            fmt = formats.get(col, "")
            if pd.isna(value):
                cells.append("")
            elif fmt == "pct":
                cells.append(_fmt_pct(float(value)))
            elif fmt == "x":
                cells.append(_fmt_x(float(value)))
            elif fmt == "num":
                cells.append(_fmt_num(float(value)))
            elif fmt == "int":
                cells.append(str(int(value)))
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def build_tldr_section(final_summary: pd.DataFrame, full_period: pd.DataFrame) -> str:
    full = full_period.set_index("portfolio")
    lines = [
        "## TL;DR",
        "",
        "Primary lens: duration-weighted geometric mean of terminal `equity/equity_benchmark` versus SPY across all monthly rolling `3/5/10/15/20y` windows. This describes historical path dependence and investor experience, not a guaranteed forecast.",
        "",
    ]
    for _, row in final_summary.sort_values("rank").iterrows():
        portfolio = str(row["portfolio"])
        analysis = PORTFOLIO_ANALYSES[portfolio]
        full_row = full.loc[portfolio]
        lines.append(
            f"{int(row['rank'])}. **{_portfolio_label(portfolio)}**. "
            f"Weighted average: `{_fmt_x(float(row['weighted_geo_terminal_ratio']))}` vs SPY; "
            f"hit rate `{_fmt_pct(float(row['weighted_hit_rate']))}`; "
            f"time above SPY `{_fmt_pct(float(row['weighted_time_above_spy']))}`; "
            f"p25 terminal `{_fmt_x(float(row['weighted_p25_terminal_ratio']))}`; "
            f"mean relative MDD `{_fmt_pct(float(row['weighted_mean_relative_mdd_vs_spy']))}`. "
            f"Full-period 2000-2026: CAGR `{_fmt_pct(float(full_row['portfolio_cagr']))}`, "
            f"MDD `{_fmt_pct(float(full_row['portfolio_mdd']))}`, terminal "
            f"`{_fmt_x(float(full_row['terminal_ratio_vs_spy']))}` vs SPY. "
            f"Strategy: {analysis['strategy']} "
            f"Forward expectation: {analysis['expectation']} "
            f"Why it got this result: {analysis['why']}"
        )
        lines.append("")
    return "\n".join(lines)


def _portfolio_label(name: str) -> str:
    return PORTFOLIO_LABELS.get(name, name)


def _load_matplotlib() -> Any:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _plot_style(ax: Any, title: str, xlabel: str = "", ylabel: str = "") -> None:
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis="x", alpha=0.22)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _save_figure(fig: Any, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    return path


def _add_value_labels(ax: Any, values: pd.Series, fmt: str) -> None:
    for patch, value in zip(ax.patches, values, strict=False):
        x = patch.get_width()
        y = patch.get_y() + patch.get_height() / 2.0
        ax.text(x, y, fmt.format(value), va="center", ha="left", fontsize=8)


def plot_final_weighted_ranking(final_summary: pd.DataFrame) -> Path:
    plt = _load_matplotlib()
    frame = final_summary.sort_values("weighted_geo_terminal_ratio", ascending=True).copy()
    labels = frame["portfolio"].map(_portfolio_label)
    colors = ["#2f6fbb" if rank == 1 else "#8fb7df" for rank in frame["rank"]]
    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    ax.barh(labels, frame["weighted_geo_terminal_ratio"], color=colors)
    ax.axvline(1.0, color="#3a3a3a", linewidth=1.1, linestyle="--")
    _add_value_labels(ax, frame["weighted_geo_terminal_ratio"], "{:.2f}x")
    _plot_style(
        ax,
        "Duration-weighted rolling terminal ratio vs SPY",
        "Geometric mean terminal ratio",
        "",
    )
    ax.set_xlim(0.0, max(1.9, float(frame["weighted_geo_terminal_ratio"].max()) * 1.12))
    return _save_figure(fig, PLOTS_DIR / "final_weighted_ranking.png")


def plot_horizon_terminal_ratios(horizon_summary: pd.DataFrame, final_summary: pd.DataFrame) -> Path:
    plt = _load_matplotlib()
    ordered = final_summary.sort_values("rank")["portfolio"].tolist()
    fig, ax = plt.subplots(figsize=(10.5, 6.4))
    for rank, portfolio in enumerate(ordered, start=1):
        rows = horizon_summary[horizon_summary["portfolio"] == portfolio].sort_values(
            "horizon_years"
        )
        linewidth = 2.6 if rank <= 3 else 1.35
        alpha = 0.95 if rank <= 3 else 0.45
        ax.plot(
            rows["horizon_years"],
            rows["geo_mean_terminal_ratio"],
            marker="o",
            linewidth=linewidth,
            alpha=alpha,
            label=f"#{rank} {_portfolio_label(portfolio)}",
        )
    ax.axhline(1.0, color="#3a3a3a", linewidth=1.1, linestyle="--")
    ax.set_xticks(list(HORIZONS_YEARS))
    _plot_style(ax, "Rolling terminal ratio by horizon", "Window length (years)", "Ratio vs SPY")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=8, frameon=False)
    return _save_figure(fig, PLOTS_DIR / "horizon_terminal_ratios.png")


def plot_horizon_hit_rates(horizon_summary: pd.DataFrame, final_summary: pd.DataFrame) -> Path:
    plt = _load_matplotlib()
    ordered = final_summary.sort_values("rank")["portfolio"].tolist()
    fig, ax = plt.subplots(figsize=(10.5, 6.4))
    for rank, portfolio in enumerate(ordered, start=1):
        rows = horizon_summary[horizon_summary["portfolio"] == portfolio].sort_values(
            "horizon_years"
        )
        linewidth = 2.6 if rank <= 3 else 1.35
        alpha = 0.95 if rank <= 3 else 0.45
        ax.plot(
            rows["horizon_years"],
            rows["hit_rate"] * 100.0,
            marker="o",
            linewidth=linewidth,
            alpha=alpha,
            label=f"#{rank} {_portfolio_label(portfolio)}",
        )
    ax.set_xticks(list(HORIZONS_YEARS))
    ax.set_ylim(45.0, 103.0)
    _plot_style(ax, "Rolling hit rate by horizon", "Window length (years)", "% ending above SPY")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=8, frameon=False)
    return _save_figure(fig, PLOTS_DIR / "horizon_hit_rates.png")


def plot_risk_reward_scatter(final_summary: pd.DataFrame) -> Path:
    plt = _load_matplotlib()
    frame = final_summary.sort_values("rank").copy()
    fig, ax = plt.subplots(figsize=(9.2, 6.4))
    scatter = ax.scatter(
        frame["weighted_mean_relative_mdd_vs_spy"] * 100.0,
        frame["weighted_geo_terminal_ratio"],
        s=80 + 260 * frame["weighted_hit_rate"],
        c=frame["rank"],
        cmap="viridis_r",
        alpha=0.86,
        edgecolor="#222222",
        linewidth=0.6,
    )
    for _, row in frame.iterrows():
        ax.annotate(
            f"#{int(row['rank'])}",
            (
                row["weighted_mean_relative_mdd_vs_spy"] * 100.0,
                row["weighted_geo_terminal_ratio"],
            ),
            xytext=(5, 4),
            textcoords="offset points",
            fontsize=8,
        )
    _plot_style(
        ax,
        "Return-relative reward versus relative pain",
        "Weighted mean relative MDD vs SPY (%)",
        "Weighted geometric terminal ratio",
    )
    cbar = fig.colorbar(scatter, ax=ax, shrink=0.82)
    cbar.set_label("Ranking (lower is better)")
    return _save_figure(fig, PLOTS_DIR / "risk_reward_scatter.png")


def plot_full_period_context(full_period: pd.DataFrame) -> Path:
    plt = _load_matplotlib()
    frame = full_period.copy()
    labels = frame["portfolio"].map(_portfolio_label)
    fig, ax = plt.subplots(figsize=(9.2, 6.4))
    scatter = ax.scatter(
        frame["portfolio_mdd"] * 100.0,
        frame["portfolio_cagr"] * 100.0,
        s=85 + 65 * frame["terminal_ratio_vs_spy"],
        c=frame["terminal_ratio_vs_spy"],
        cmap="plasma",
        alpha=0.84,
        edgecolor="#222222",
        linewidth=0.6,
    )
    for label, (_, row) in zip(labels, frame.iterrows(), strict=False):
        ax.annotate(
            label.split(" / ")[0],
            (row["portfolio_mdd"] * 100.0, row["portfolio_cagr"] * 100.0),
            xytext=(5, 4),
            textcoords="offset points",
            fontsize=8,
        )
    _plot_style(ax, "Full-period CAGR versus MDD", "Portfolio MDD (%)", "CAGR (%)")
    cbar = fig.colorbar(scatter, ax=ax, shrink=0.82)
    cbar.set_label("Terminal ratio vs SPY")
    return _save_figure(fig, PLOTS_DIR / "full_period_cagr_mdd.png")


def plot_terminal_ratio_boxplots(rolling: pd.DataFrame, final_summary: pd.DataFrame) -> Path:
    plt = _load_matplotlib()
    top = final_summary.sort_values("rank").head(5)["portfolio"].tolist()
    fig, axes = plt.subplots(2, 3, figsize=(15.5, 8.8))
    flat_axes = list(axes.ravel())
    for ax, horizon in zip(flat_axes, HORIZONS_YEARS, strict=False):
        data = [
            rolling[
                (rolling["portfolio"] == portfolio) & (rolling["horizon_years"] == horizon)
            ]["terminal_ratio_vs_spy"].to_numpy(dtype=float)
            for portfolio in top
        ]
        ax.boxplot(
            data,
            vert=False,
            showfliers=False,
            widths=0.62,
            patch_artist=True,
            boxprops={"facecolor": "#dbeafe", "edgecolor": "#2f6fbb", "linewidth": 1.0},
            medianprops={"color": "#111827", "linewidth": 1.4},
            whiskerprops={"color": "#2f6fbb", "linewidth": 1.0},
            capprops={"color": "#2f6fbb", "linewidth": 1.0},
        )
        ax.axvline(1.0, color="#3a3a3a", linewidth=1.0, linestyle="--")
        ax.set_yticks(range(1, len(top) + 1))
        ax.set_yticklabels([f"#{i + 1}" for i in range(len(top))], fontsize=8)
        ax.set_title(f"{horizon}y windows", loc="left", fontsize=10, fontweight="bold")
        ax.set_xlabel("Terminal equity / SPY equity")
        ax.set_ylabel("Strategy rank")
        ax.grid(True, axis="x", alpha=0.2)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    flat_axes[-1].axis("off")
    legend_lines = [f"#{i + 1}: {_portfolio_label(name)}" for i, name in enumerate(top)]
    flat_axes[-1].text(0.0, 1.0, "Legend\n" + "\n".join(legend_lines), va="top", fontsize=9)
    fig.suptitle("Terminal-ratio distribution for top 5 weighted rows", fontsize=14, fontweight="bold")
    return _save_figure(fig, PLOTS_DIR / "terminal_ratio_boxplots_top5.png")


def plot_terminal_ratio_by_start_grid(rolling: pd.DataFrame, final_summary: pd.DataFrame) -> Path:
    plt = _load_matplotlib()
    ordered = final_summary.sort_values("rank")["portfolio"].tolist()
    colors = plt.get_cmap("tab10").colors
    fig, axes = plt.subplots(3, 2, figsize=(16.0, 11.2))
    flat_axes = list(axes.ravel())
    legend_handles = []
    for ax, horizon in zip(flat_axes, HORIZONS_YEARS, strict=False):
        horizon_rows = rolling[rolling["horizon_years"] == horizon].copy()
        horizon_rows["start_date"] = pd.to_datetime(horizon_rows["start_date"])
        for i, portfolio in enumerate(ordered):
            rows = horizon_rows[horizon_rows["portfolio"] == portfolio].sort_values("start_date")
            (line,) = ax.plot(
                rows["start_date"],
                rows["terminal_ratio_vs_spy"],
                linewidth=1.85 if i < 3 else 1.05,
                alpha=0.92 if i < 3 else 0.48,
                color=colors[i % len(colors)],
                label=f"#{i + 1} {_portfolio_label(portfolio)}",
            )
            if horizon == HORIZONS_YEARS[0]:
                legend_handles.append(line)
        ax.axhline(1.0, color="#3a3a3a", linewidth=1.0, linestyle="--")
        ax.set_title(f"{horizon}y rolling windows", loc="left", fontsize=10, fontweight="bold")
        ax.set_xlabel("Backtest start month")
        ax.set_ylabel("Final equity / SPY equity")
        ax.grid(True, alpha=0.2)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="x", labelrotation=30)
    flat_axes[-1].axis("off")
    flat_axes[-1].legend(
        handles=legend_handles,
        loc="upper left",
        fontsize=8,
        frameon=False,
        title="Strategy lines",
    )
    fig.suptitle(
        "Final equity / SPY equity for every monthly start",
        fontsize=14,
        fontweight="bold",
    )
    return _save_figure(fig, PLOTS_DIR / "terminal_ratio_by_start_grid.png")


def generate_plots(
    rolling: pd.DataFrame,
    horizon_summary: pd.DataFrame,
    final_summary: pd.DataFrame,
    full_period: pd.DataFrame,
) -> list[tuple[str, Path]]:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    return [
        (
            "Final duration-weighted ranking by geometric terminal ratio vs SPY.",
            plot_final_weighted_ranking(final_summary),
        ),
        (
            "Geometric terminal ratio by rolling horizon; top three rows are emphasized.",
            plot_horizon_terminal_ratios(horizon_summary, final_summary),
        ),
        (
            "Hit rate by rolling horizon; values are the share of windows ending above SPY.",
            plot_horizon_hit_rates(horizon_summary, final_summary),
        ),
        (
            "Reward versus relative pain; bubble size is weighted hit rate.",
            plot_risk_reward_scatter(final_summary),
        ),
        (
            "Full common-period CAGR/MDD context, with color and size by terminal vs SPY.",
            plot_full_period_context(full_period),
        ),
        (
            "Every rolling backtest endpoint by start month: one line per strategy, faceted by horizon.",
            plot_terminal_ratio_by_start_grid(rolling, final_summary),
        ),
        (
            "Distribution of terminal ratios for the top five weighted rows, split into a horizon grid.",
            plot_terminal_ratio_boxplots(rolling, final_summary),
        ),
    ]


def write_report(
    asset_equity: pd.DataFrame,
    weights: pd.DataFrame,
    rolling: pd.DataFrame,
    horizon_summary: pd.DataFrame,
    final_summary: pd.DataFrame,
    full_period: pd.DataFrame,
) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    best = final_summary.iloc[0]
    best_relative_mdd = final_summary.sort_values(
        "weighted_mean_relative_mdd_vs_spy", ascending=False
    ).iloc[0]
    best_full_period = full_period.iloc[0]
    common_start = rolling["start_date"].min()
    common_end = rolling["end_date"].max()
    n_windows = int(len(rolling))
    plots = generate_plots(rolling, horizon_summary, final_summary, full_period)
    figures_md = "\n\n".join(
        f"![{caption}]({path.relative_to(STUDY_DIR)})\n\n{caption}" for caption, path in plots
    )
    tldr = build_tldr_section(final_summary, full_period)
    horizon_counts = (
        rolling.groupby("horizon_years")["start_date"].nunique().reset_index(name="n_starts")
    )

    final_cols = [
        "rank",
        "portfolio",
        "weighted_geo_terminal_ratio",
        "weighted_hit_rate",
        "weighted_time_above_spy",
        "weighted_p25_terminal_ratio",
        "weighted_mean_relative_mdd_vs_spy",
        "weighted_mean_excess_cagr",
    ]
    weight_cols = [
        "portfolio",
        "weights",
        "effective_equity",
        "effective_mf",
        "effective_gold",
        "effective_zroz",
        "effective_intermediate_treasury",
    ]
    horizon_cols = [
        "portfolio",
        "horizon_years",
        "n_windows",
        "hit_rate",
        "geo_mean_terminal_ratio",
        "p25_terminal_ratio",
        "median_terminal_ratio",
        "mean_time_above_spy_pct",
        "mean_relative_mdd_vs_spy",
    ]
    full_cols = [
        "portfolio",
        "portfolio_cagr",
        "spy_cagr",
        "terminal_ratio_vs_spy",
        "time_above_spy_pct",
        "portfolio_mdd",
        "relative_mdd_vs_spy",
    ]
    pct_formats = {
        "effective_equity": "pct",
        "effective_mf": "pct",
        "effective_gold": "pct",
        "effective_zroz": "pct",
        "effective_intermediate_treasury": "pct",
        "weighted_hit_rate": "pct",
        "weighted_time_above_spy": "pct",
        "weighted_mean_relative_mdd_vs_spy": "pct",
        "weighted_mean_excess_cagr": "pct",
        "hit_rate": "pct",
        "mean_time_above_spy_pct": "pct",
        "mean_relative_mdd_vs_spy": "pct",
        "portfolio_cagr": "pct",
        "spy_cagr": "pct",
        "time_above_spy_pct": "pct",
        "portfolio_mdd": "pct",
        "relative_mdd_vs_spy": "pct",
    }
    x_formats = {
        "weighted_geo_terminal_ratio": "x",
        "weighted_p25_terminal_ratio": "x",
        "geo_mean_terminal_ratio": "x",
        "p25_terminal_ratio": "x",
        "median_terminal_ratio": "x",
        "terminal_ratio_vs_spy": "x",
    }
    formats = {**pct_formats, **x_formats, "rank": "int", "n_windows": "int"}

    report = (
        "# Fixed Portfolio Rolling SPY Comparison\n\n"
        "Status: research-only diagnostic. No deployment, paper-trade label or mandate change.\n\n"
        f"{tldr}\n\n"
        "## Summary\n\n"
        f"- Asset cache span after outer join: `{asset_equity.index.min().date()}`.."
        f"`{asset_equity.index.max().date()}`.\n"
        f"- Common rolling-window span used by all portfolios: `{common_start}`..`{common_end}`.\n"
        f"- Portfolios: `{len(weights)}` fixed monthly-rebalanced rules.\n"
        f"- Rolling rows: `{n_windows}` across horizons `{list(HORIZONS_YEARS)}`.\n"
        f"- Final horizon weights: `3y={HORIZON_WEIGHTS[3]:.2%}`, "
        f"`5y={HORIZON_WEIGHTS[5]:.2%}`, `10y={HORIZON_WEIGHTS[10]:.2%}`, "
        f"`15y={HORIZON_WEIGHTS[15]:.2%}`, `20y={HORIZON_WEIGHTS[20]:.2%}`.\n"
        f"- Top weighted terminal-ratio row: `{best['portfolio']}` at "
        f"`{_fmt_x(float(best['weighted_geo_terminal_ratio']))}` weighted geometric "
        f"terminal ratio vs SPY, hit rate `{_fmt_pct(float(best['weighted_hit_rate']))}`, "
        f"time above SPY `{_fmt_pct(float(best['weighted_time_above_spy']))}`.\n\n"
        "## Method\n\n"
        "Each portfolio is rebalanced monthly inside each rolling window, starting from "
        "target weights at that window's first trading day. The benchmark is SPY buy "
        "and hold over the same dates. The primary path object is the daily relative "
        "curve `portfolio_equity / spy_equity`; terminal ratio, time above SPY, relative "
        "drawdown and longest under-SPY streak are computed from that curve. RSST70/30 "
        "uses the same tracking proxy as the current RSC studies: `SPYSIM + 70% DBMFSIM "
        "+ 30% KMLMSIM - CASHX?E=-2`. Rolling windows are calendar-month starts with "
        "horizons `3/5/10/15/20y`; horizon-level summaries are combined with linear "
        "duration weights. This is robustness description, not parameter selection "
        "`[systematic_trading, p.185-188]`, `[testing_tuning, p.327-335]`.\n\n"
        "## Figures\n\n"
        f"{figures_md}\n\n"
        "## Portfolio Definitions\n\n"
        f"{markdown_table(weights[weight_cols], weight_cols, formats)}\n\n"
        "## Final Weighted Ranking\n\n"
        f"{markdown_table(final_summary[final_cols], final_cols, formats)}\n\n"
        "## Horizon Window Counts\n\n"
        f"{markdown_table(horizon_counts, ['horizon_years', 'n_starts'], {'n_starts': 'int'})}\n\n"
        "## Horizon Summary\n\n"
        f"{markdown_table(horizon_summary[horizon_cols], horizon_cols, formats)}\n\n"
        "## Full Common Period Context\n\n"
        f"{markdown_table(full_period[full_cols], full_cols, formats)}\n\n"
        "## Interpretation\n\n"
        f"The weighted rolling-window lens favors `{best['portfolio']}`: it has the "
        f"highest duration-weighted geometric terminal ratio versus SPY "
        f"(`{_fmt_x(float(best['weighted_geo_terminal_ratio']))}`) and very high "
        f"weighted hit rate (`{_fmt_pct(float(best['weighted_hit_rate']))}`). The "
        f"full common-period leader is `{best_full_period['portfolio']}` at terminal "
        f"`{_fmt_x(float(best_full_period['terminal_ratio_vs_spy']))}` versus SPY, "
        "but its rolling hit rate and relative drawdown are weaker than the UPRO/SSO "
        f"completion rows. The least painful relative curve among the final weighted "
        f"rows is `{best_relative_mdd['portfolio']}` with weighted mean relative MDD "
        f"`{_fmt_pct(float(best_relative_mdd['weighted_mean_relative_mdd_vs_spy']))}`. "
        "Because these rolling windows overlap heavily, the statistics describe path "
        "dependence and investor experience; they are not independent validation trials "
        "`[testing_tuning, p.318-320]`.\n\n"
        "## Artifacts\n\n"
        f"- Asset curves: `{(RESULTS_DIR / 'asset_equity_curves.csv').relative_to(REPO_ROOT)}`.\n"
        f"- Portfolio definitions: `{(RESULTS_DIR / 'portfolio_definitions.csv').relative_to(REPO_ROOT)}`.\n"
        f"- Individual windows: `{(RESULTS_DIR / 'rolling_windows.csv').relative_to(REPO_ROOT)}`.\n"
        f"- Horizon summary: `{(RESULTS_DIR / 'horizon_summary.csv').relative_to(REPO_ROOT)}`.\n"
        f"- Final weighted summary: `{(RESULTS_DIR / 'final_weighted_summary.csv').relative_to(REPO_ROOT)}`.\n"
        f"- Full-period context: `{(RESULTS_DIR / 'full_period_summary.csv').relative_to(REPO_ROOT)}`.\n"
        f"- Plots: `{PLOTS_DIR.relative_to(REPO_ROOT)}`.\n"
    )
    REPORT_MD.write_text(report, encoding="utf-8")


def run(skip_download: bool = False, force_download: bool = False) -> None:
    asset_equity = load_asset_curves_from_raw() if skip_download else download_asset_curves(force_download)
    daily_returns = build_daily_returns(asset_equity)
    specs = portfolio_specs()
    weights = portfolio_weight_rows(specs)
    rolling = evaluate_rolling_windows(daily_returns, specs)
    horizon_summary = summarize_by_horizon(rolling)
    final_summary = summarize_weighted_final(horizon_summary)
    full_period = summarize_full_period(daily_returns, specs)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    weights.to_csv(RESULTS_DIR / "portfolio_definitions.csv", index=False)
    rolling.to_csv(RESULTS_DIR / "rolling_windows.csv", index=False)
    horizon_summary.to_csv(RESULTS_DIR / "horizon_summary.csv", index=False)
    final_summary.to_csv(RESULTS_DIR / "final_weighted_summary.csv", index=False)
    full_period.to_csv(RESULTS_DIR / "full_period_summary.csv", index=False)
    write_report(asset_equity, weights, rolling, horizon_summary, final_summary, full_period)
    print(f"wrote {REPORT_MD.relative_to(REPO_ROOT)}")
    print(final_summary[["rank", "portfolio", "weighted_geo_terminal_ratio", "weighted_hit_rate"]])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-download", action="store_true", help="use raw JSON cache only")
    parser.add_argument("--force-download", action="store_true", help="refresh raw Testfol.io cache")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run(skip_download=args.skip_download, force_download=args.force_download)


if __name__ == "__main__":
    main()
