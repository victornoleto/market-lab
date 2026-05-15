"""Phase 3 iteration 028: stress prior QLD volatility-throttle sleeve.

No new strategy configuration is selected here. This script recomputes the
iteration 027 best rule and applies rolling-window plus friction stress because
post-selection stress is required before treating a result as robust
`[testing_tuning, p.327-335]`. The previous MCPT/DSR failures remain binding
`[testing_tuning, p.318-320]`, `[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))


ITERATION = "028-2026-05-14-qld-vol-throttle-stress"
ITER_DIR = Path(__file__).resolve().parent
PRICE_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
TRADING_DAYS = 252
CUMULATIVE_TRIALS_BEFORE = 312
CUMULATIVE_TRIALS_AFTER = 312
AUDIT_TICKERS = ["QLD", "TLT", "GLD", "QQQ", "SPY", "SHV"]
REQUIRED = set(AUDIT_TICKERS)
FINANCING_RATE = 0.05
EXTRA_DRAGS_BPS = [25, 50, 100]


@dataclass(frozen=True)
class Config:
    name: str
    base_qld: float
    base_tlt: float
    base_gld: float
    qld_boost: float
    qld_cut: float
    rv_lookback: int
    low_quantile: float = 0.30
    high_quantile: float = 0.70


CONFIG = Config("qld70_tlt15_gld15_rv126_q30_70_b50_c20", 0.70, 0.15, 0.15, 0.50, 0.20, 126)


def main() -> None:
    audit = audit_data()
    missing = [item["ticker"] for item in audit["daily_files"] if item["ticker"] in REQUIRED and not item["exists"]]
    if missing:
        write_blocked(audit, f"missing required daily parquet: {missing}")
        return

    closes = {ticker: load_close(ticker) for ticker in REQUIRED}
    prices = pd.concat({ticker: closes[ticker] for ticker in AUDIT_TICKERS}, axis=1).dropna()
    if len(prices) < 1260 + 252:
        write_blocked(audit, f"insufficient aligned observations for 5y rolling stress: {len(prices)}")
        return

    strategy, weights = strategy_returns(prices, CONFIG)
    bmarks = aligned_benchmarks(strategy.index, prices)
    base_metrics = compute_metrics(strategy, weights, bmarks)
    stress_metrics = {str(bps): compute_metrics(strategy - bps / 10000 / TRADING_DAYS, weights, bmarks) for bps in EXTRA_DRAGS_BPS}
    rolling = {
        "3y": rolling_stress(strategy, bmarks, window=756, step=21),
        "5y": rolling_stress(strategy, bmarks, window=1260, step=21),
    }

    full_pass = full_window_pass(base_metrics)
    drag_pass = {bps: full_window_pass(metrics) for bps, metrics in stress_metrics.items()}
    rolling_pass = {name: value["pass_rate_both_primary"] >= 0.90 for name, value in rolling.items()}
    stress_pass = full_pass and all(drag_pass.values()) and all(rolling_pass.values())

    gates = {
        "full_window_economic": full_pass,
        "extra_drag_25bps": drag_pass["25"],
        "extra_drag_50bps": drag_pass["50"],
        "extra_drag_100bps": drag_pass["100"],
        "rolling_3y_pass_rate_ge_90pct": rolling_pass["3y"],
        "rolling_5y_pass_rate_ge_90pct": rolling_pass["5y"],
        "prior_is_mcpt": False,
        "prior_wf_mcpt": False,
        "prior_dsr": False,
    }

    kill_switches = []
    if not full_pass:
        kill_switches.append("full-window CAGR or terminal wealth <= primary benchmark")
    for bps, passed in drag_pass.items():
        if not passed:
            kill_switches.append(f"{bps}bps extra-drag CAGR or terminal wealth <= primary benchmark")
    for name, passed in rolling_pass.items():
        if not passed:
            kill_switches.append(f"{name} rolling pass rate below 90%")
    kill_switches.append("prior iteration 027 MCPT/DSR failures remain binding")

    results = {
        "iteration": ITERATION,
        "status": "fail" if not stress_pass else "economic_beater_not_validated",
        "pre_registered": True,
        "n_trials": 0,
        "mcpt_reps": {},
        "best_config": asdict(CONFIG),
        "winner": False,
        "metrics": {
            "base": base_metrics,
            "extra_drag_bps": stress_metrics,
            "rolling": rolling,
            "cumulative_n_trials_before": CUMULATIVE_TRIALS_BEFORE,
            "cumulative_n_trials_after": CUMULATIVE_TRIALS_AFTER,
            "gross_mean": float(weights.abs().sum(axis=1).mean()),
            "gross_max": float(weights.abs().sum(axis=1).max()),
        },
        "benchmark": {
            "primary": ["QQQ_buy_hold", "equal_weight_QLD_TLT_GLD_buy_hold"],
            "opportunity": "SPY_buy_hold",
            "aligned_start": base_metrics["start"],
            "aligned_end": base_metrics["end"],
        },
        "gates": gates,
        "kill_switches": kill_switches,
        "artifacts": [
            str(ITER_DIR / "PRE_REG.md"),
            str(ITER_DIR / "run_iteration.py"),
            str(ITER_DIR / "RESULTS.json"),
            str(ITER_DIR / "audit.json"),
            str(ITER_DIR / "stress_returns.csv"),
        ],
        "notes": "Stress-only retest of iteration 027 best config; no new strategy trials or promotion labels.",
    }

    pd.DataFrame({"strategy": strategy, **bmarks}).to_csv(ITER_DIR / "stress_returns.csv")
    (ITER_DIR / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    (ITER_DIR / "RESULTS.json").write_text(json.dumps(to_jsonable(results), indent=2), encoding="utf-8")


def audit_data() -> dict[str, object]:
    daily_files = []
    for ticker in AUDIT_TICKERS:
        path = PRICE_DIR / f"{ticker}.parquet"
        item: dict[str, object] = {"ticker": ticker, "path": str(path), "exists": path.exists()}
        if path.exists():
            df = pd.read_parquet(path)
            idx = pd.to_datetime(df.index)
            item.update({
                "rows": int(len(df)),
                "first": str(idx.min()),
                "last": str(idx.max()),
                "timezone": str(getattr(idx, "tz", None)),
                "columns": list(df.columns),
                "missing_bday_rate": missing_bday_rate(idx),
                "has_close": "close" in df.columns or "adj_close" in df.columns,
            })
        daily_files.append(item)
    return {"daily_files": daily_files}


def load_close(ticker: str) -> pd.Series:
    df = pd.read_parquet(PRICE_DIR / f"{ticker}.parquet").copy()
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df = df[~df.index.duplicated()].sort_index()
    close_col = "adj_close" if "adj_close" in df.columns else "close"
    return df[close_col].astype(float).dropna()


def strategy_returns(prices: pd.DataFrame, cfg: Config) -> tuple[pd.Series, pd.DataFrame]:
    asset_returns = prices[["QLD", "TLT", "GLD"]].pct_change().fillna(0.0)
    weights = vol_throttle_weights(asset_returns.index, prices["QQQ"], cfg)
    gross = weights.abs().sum(axis=1)
    financing = (gross - 1.0).clip(lower=0.0) * FINANCING_RATE / TRADING_DAYS
    returns = ((weights * asset_returns).sum(axis=1) - financing).rename(cfg.name)
    return returns.iloc[1:], weights.iloc[1:]


def vol_throttle_weights(index: pd.Index, qqq_prices: pd.Series, cfg: Config) -> pd.DataFrame:
    weights = pd.DataFrame(0.0, index=index, columns=["QLD", "TLT", "GLD"])
    qqq_returns = qqq_prices.pct_change()
    rv = qqq_returns.rolling(cfg.rv_lookback).std() * np.sqrt(TRADING_DAYS)
    low = rv.rolling(756, min_periods=252).quantile(cfg.low_quantile).shift(1)
    high = rv.rolling(756, min_periods=252).quantile(cfg.high_quantile).shift(1)
    rv_lag = rv.shift(1)
    month = None
    current = base_weights(cfg)
    for i, date in enumerate(index):
        period = pd.Timestamp(date).to_period("M")
        if i == 0 or period != month:
            current = base_weights(cfg)
            if pd.notna(rv_lag.iloc[i]) and pd.notna(low.iloc[i]) and pd.notna(high.iloc[i]):
                if rv_lag.iloc[i] <= low.iloc[i]:
                    current["QLD"] += cfg.qld_boost
                elif rv_lag.iloc[i] >= high.iloc[i]:
                    current["QLD"] = max(0.0, current["QLD"] - cfg.qld_cut)
            month = period
        weights.loc[date, list(current)] = list(current.values())
    return weights


def base_weights(cfg: Config) -> dict[str, float]:
    return {"QLD": cfg.base_qld, "TLT": cfg.base_tlt, "GLD": cfg.base_gld}


def aligned_benchmarks(index: pd.Index, prices: pd.DataFrame) -> dict[str, pd.Series]:
    pct = prices.pct_change().fillna(0.0).reindex(index).fillna(0.0)
    return {
        "qqq_bh": pct["QQQ"],
        "spy_bh": pct["SPY"],
        "qld_bh": pct["QLD"],
        "tlt_bh": pct["TLT"],
        "gld_bh": pct["GLD"],
        "shv_bh": pct["SHV"],
        "qld_tlt_gld_ew_bh": pct[["QLD", "TLT", "GLD"]].mean(axis=1),
    }


def compute_metrics(returns: pd.Series, weights: pd.DataFrame, bmarks: dict[str, pd.Series]) -> dict[str, object]:
    out: dict[str, object] = {
        "start": str(returns.index.min().date()),
        "end": str(returns.index.max().date()),
        "n_obs": int(len(returns)),
        "cagr": cagr(returns),
        "sharpe": sharpe(returns),
        "max_drawdown": max_drawdown(returns),
        "terminal_wealth": compound(returns) + 1.0,
        "annual_turnover": annual_turnover(weights),
    }
    for name, series in bmarks.items():
        aligned = series.reindex(returns.index).fillna(0.0)
        out[f"{name}_cagr"] = cagr(aligned)
        out[f"{name}_terminal_wealth"] = compound(aligned) + 1.0
        out[f"{name}_max_drawdown"] = max_drawdown(aligned)
    return out


def rolling_stress(strategy: pd.Series, bmarks: dict[str, pd.Series], *, window: int, step: int) -> dict[str, object]:
    rows = []
    for start in range(0, len(strategy) - window + 1, step):
        end = start + window
        s = strategy.iloc[start:end]
        qqq = bmarks["qqq_bh"].reindex(s.index).fillna(0.0)
        ew = bmarks["qld_tlt_gld_ew_bh"].reindex(s.index).fillna(0.0)
        row = {
            "start": str(s.index.min().date()),
            "end": str(s.index.max().date()),
            "strategy_cagr": cagr(s),
            "strategy_terminal": compound(s) + 1.0,
            "qqq_cagr": cagr(qqq),
            "qqq_terminal": compound(qqq) + 1.0,
            "ew_cagr": cagr(ew),
            "ew_terminal": compound(ew) + 1.0,
        }
        row["pass_both_primary"] = row["strategy_cagr"] > row["qqq_cagr"] and row["strategy_terminal"] > row["qqq_terminal"] and row["strategy_cagr"] > row["ew_cagr"] and row["strategy_terminal"] > row["ew_terminal"]
        rows.append(row)
    pass_count = sum(bool(row["pass_both_primary"]) for row in rows)
    worst_excess_cagr_vs_qqq = min((row["strategy_cagr"] - row["qqq_cagr"] for row in rows), default=float("nan"))
    worst_excess_cagr_vs_ew = min((row["strategy_cagr"] - row["ew_cagr"] for row in rows), default=float("nan"))
    return {
        "window_days": window,
        "step_days": step,
        "n_windows": len(rows),
        "pass_count_both_primary": pass_count,
        "pass_rate_both_primary": pass_count / len(rows) if rows else 0.0,
        "worst_excess_cagr_vs_qqq": worst_excess_cagr_vs_qqq,
        "worst_excess_cagr_vs_equal_weight": worst_excess_cagr_vs_ew,
        "first_failures": [row for row in rows if not row["pass_both_primary"]][:10],
    }


def full_window_pass(metrics: dict[str, object]) -> bool:
    return bool(
        metrics["cagr"] > metrics["qqq_bh_cagr"]
        and metrics["terminal_wealth"] > metrics["qqq_bh_terminal_wealth"]
        and metrics["cagr"] > metrics["qld_tlt_gld_ew_bh_cagr"]
        and metrics["terminal_wealth"] > metrics["qld_tlt_gld_ew_bh_terminal_wealth"]
        and metrics["cagr"] > metrics["spy_bh_cagr"]
    )


def compound(returns: pd.Series) -> float:
    return float((1.0 + returns.astype(float)).prod() - 1.0)


def cagr(returns: pd.Series) -> float:
    if len(returns) == 0:
        return 0.0
    years = len(returns) / TRADING_DAYS
    terminal = compound(returns) + 1.0
    if terminal <= 0.0:
        return -1.0
    return float(terminal ** (1.0 / years) - 1.0)


def sharpe(returns: pd.Series) -> float:
    std = float(returns.std(ddof=1))
    return 0.0 if std == 0.0 else float(returns.mean() / std * np.sqrt(TRADING_DAYS))


def max_drawdown(returns: pd.Series) -> float:
    equity = (1.0 + returns.astype(float)).cumprod()
    return float((equity / equity.cummax() - 1.0).min())


def annual_turnover(weights: pd.DataFrame) -> float:
    monthly = weights[weights.index.to_series().dt.to_period("M") != weights.index.to_series().shift(1).dt.to_period("M")]
    if len(monthly) < 2:
        return 0.0
    return float(monthly.diff().abs().sum(axis=1).mean() * 12.0)


def missing_bday_rate(index: pd.DatetimeIndex) -> float:
    if len(index) < 2:
        return 0.0
    expected = pd.bdate_range(index.min(), index.max())
    return float(1.0 - len(index.normalize().unique()) / len(expected)) if len(expected) else 0.0


def write_blocked(audit: dict[str, object], reason: str) -> None:
    results = {
        "iteration": ITERATION,
        "status": "data_blocked",
        "pre_registered": True,
        "n_trials": 0,
        "mcpt_reps": {},
        "best_config": None,
        "winner": False,
        "metrics": {},
        "benchmark": {},
        "gates": {},
        "kill_switches": [reason],
        "artifacts": [str(ITER_DIR / "PRE_REG.md"), str(ITER_DIR / "run_iteration.py"), str(ITER_DIR / "RESULTS.json"), str(ITER_DIR / "audit.json")],
        "notes": reason,
    }
    (ITER_DIR / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    (ITER_DIR / "RESULTS.json").write_text(json.dumps(to_jsonable(results), indent=2), encoding="utf-8")


def to_jsonable(value):
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_jsonable(v) for v in value]
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value)
    return value


if __name__ == "__main__":
    main()
