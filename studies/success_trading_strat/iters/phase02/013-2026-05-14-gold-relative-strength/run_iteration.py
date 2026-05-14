"""Phase 2 iteration 013: daily gold relative-strength filter.

The family holds gold only when gold outperforms SPY on a lagged rolling
relative-strength filter and own momentum is positive. Relative-strength and
intermarket filters are used as regime tools `[trading_systems_methods,
p.542-544]`, `[trading_systems_methods, p.939]`; one completed-bar lag avoids
same-close lookahead `[advances_fin_ml, p.31-34]`.
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

from market_lab.backtest.validation.dsr import dsr, sharpe_annualized
from market_lab.backtest.validation.pbo import pbo
from studies.success_trading_strat.scripts.validation_scaffold import (
    annualized_sharpe,
    mcpt_on_strategy_returns,
    walk_forward_mcpt,
)


ITERATION = "013-2026-05-14-gold-relative-strength"
ITER_DIR = Path(__file__).resolve().parent
PRICE_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
HOUR_DIR = ROOT / "data" / "tiingo" / "1hour" / "prices"
MIN15_DIR = ROOT / "data" / "tiingo" / "15min" / "prices"
TRADING_DAYS = 252
CUMULATIVE_TRIALS_AFTER = 152


@dataclass(frozen=True)
class Config:
    name: str
    ticker: str
    rs_sma: int
    momentum: int


CONFIGS = [
    Config("gld_rs100_m63", "GLD", 100, 63),
    Config("gld_rs200_m126", "GLD", 200, 126),
    Config("xau_rs100_m63", "xauusd", 100, 63),
    Config("xau_rs200_m126", "xauusd", 200, 126),
]


def main() -> None:
    audit = audit_data()
    if any(not item["exists"] for item in audit["daily_files"]):
        write_blocked(audit)
        return

    prices = {ticker: load_close(ticker) for ticker in ["GLD", "xauusd", "SPY", "SHV"]}
    returns_by_config: dict[str, pd.Series] = {}
    vector_returns_by_config: dict[str, pd.Series] = {}
    metrics_by_config: dict[str, dict[str, float | int | str]] = {}

    for cfg in CONFIGS:
        strat, vector = strategy_returns(prices[cfg.ticker], prices["SPY"], prices["SHV"], cfg)
        returns_by_config[cfg.name] = strat
        vector_returns_by_config[cfg.name] = vector
        asset_bh = prices[cfg.ticker].pct_change().reindex(strat.index).fillna(0.0)
        spy_bh = prices["SPY"].pct_change().reindex(strat.index).fillna(0.0)
        metrics_by_config[cfg.name] = compute_metrics(strat, asset_bh, spy_bh)

    best_name = max(metrics_by_config, key=lambda name: metrics_by_config[name]["sharpe"])
    best_cfg = next(cfg for cfg in CONFIGS if cfg.name == best_name)
    best_returns = returns_by_config[best_name]
    best_close = prices[best_cfg.ticker].reindex(best_returns.index).dropna()
    spy_close = prices["SPY"].reindex(best_close.index).ffill().dropna()
    aligned_close = best_close.reindex(spy_close.index).dropna()
    aligned_spy = spy_close.reindex(aligned_close.index).dropna()
    mcpt_prices = np.log(aligned_close.to_numpy()) + 100.0
    mcpt_spy = np.log(aligned_spy.to_numpy()) + 100.0

    returns_matrix = pd.concat(returns_by_config, axis=1).dropna()
    pbo_result = pbo(returns_matrix.to_numpy(), n_blocks=10)
    dsr_result = dsr(best_returns.to_numpy(), n_trials=CUMULATIVE_TRIALS_AFTER)
    is_mcpt = mcpt_on_strategy_returns(
        mcpt_prices,
        lambda series: fixed_strategy_from_mcpt_prices(series, mcpt_spy, best_cfg),
        n_permutations=200,
        seed=2601,
        metric=annualized_sharpe,
    )
    train_size = min(756, max(252, mcpt_prices.size // 3))
    wf_result = walk_forward_mcpt(
        mcpt_prices,
        lambda train, test: fixed_strategy_from_mcpt_prices(
            np.concatenate([train, test]), mcpt_spy[: train.size + test.size], best_cfg
        )[-(test.size - 1) :],
        train_size=train_size,
        test_size=252,
        step_size=252,
        n_permutations=100,
        seed=2602,
        metric=annualized_sharpe,
    )
    wf_returns_by_window = walk_forward_window_returns(best_returns, train_size=756, test_size=252, step_size=252)
    bootstrap_ci = bootstrap_mean_ci(best_returns.to_numpy(), n_resamples=2000, seed=2603)
    vector_delta = abs(cagr(best_returns) - cagr(vector_returns_by_config[best_name]))
    asset_bh = prices[best_cfg.ticker].pct_change().reindex(best_returns.index).fillna(0.0)

    best_metrics = metrics_by_config[best_name]
    economic_cagr = best_metrics["cagr"] > best_metrics["same_asset_bh_cagr"]
    gates = {
        "economic_cagr_vs_same_asset": economic_cagr,
        "economic_sharpe_vs_same_asset": best_metrics["sharpe"] > best_metrics["same_asset_bh_sharpe"],
        "is_mcpt": is_mcpt.p_value <= 0.01,
        "wf_mcpt": wf_result.mcpt.p_value <= 0.05,
        "pbo": pbo_result.pbo < 0.5,
        "dsr": dsr_result.p_value < 0.05,
        "wf_windows": len(wf_returns_by_window) >= 8 and sum(x > 0 for x in wf_returns_by_window) >= 6,
        "oos": compound(best_returns.iloc[int(len(best_returns) * 0.8) :]) > 0,
        "fwd_63d": compound(best_returns.iloc[-63:]) > 0,
        "bootstrap": bootstrap_ci[0] > 0,
        "cross_lib": vector_delta <= 0.03,
    }
    strict_winner = all(gates.values())
    watchlist_ok = bool(economic_cagr and gates["economic_sharpe_vs_same_asset"] and sum(bool(v) for v in gates.values()) >= 8)
    status = "strict_winner" if strict_winner else "candidate_watchlist" if watchlist_ok else "fail"
    kill_switches = []
    if not economic_cagr:
        kill_switches.append("CAGR <= same-asset buy-and-hold")
    if not strict_winner:
        kill_switches.append("failed strict validation gates")

    results = {
        "iteration": ITERATION,
        "status": status,
        "pre_registered": True,
        "n_trials": len(CONFIGS),
        "mcpt_reps": {"is": 200, "wf": 100},
        "best_config": asdict(best_cfg),
        "winner": strict_winner,
        "metrics": {
            "by_config": metrics_by_config,
            "best": best_metrics,
            "wf_window_returns": wf_returns_by_window,
            "bootstrap_mean_daily_ci_99_9": bootstrap_ci,
            "cross_lib_cagr_delta": vector_delta,
            "same_asset_buyhold_total_return": compound(asset_bh),
        },
        "benchmark": {"primary": f"{best_cfg.ticker}_buy_hold", "context": "SPY_buy_hold"},
        "gates": {
            **gates,
            "pbo_value": pbo_result.pbo,
            "dsr_p_value": dsr_result.p_value,
            "is_mcpt_p_value": is_mcpt.p_value,
            "wf_mcpt_p_value": wf_result.mcpt.p_value,
            "wf_positive_windows": int(sum(x > 0 for x in wf_returns_by_window)),
            "wf_total_windows": len(wf_returns_by_window),
            "oos_total_return": compound(best_returns.iloc[int(len(best_returns) * 0.8) :]),
            "fwd_63d_total_return": compound(best_returns.iloc[-63:]),
        },
        "kill_switches": kill_switches,
        "artifacts": [
            str(ITER_DIR / "PRE_REG.md"),
            str(ITER_DIR / "run_iteration.py"),
            str(ITER_DIR / "RESULTS.json"),
            str(ITER_DIR / "audit.json"),
            str(ITER_DIR / "returns.csv"),
        ],
        "notes": "Daily gold relative-strength filter tested. Intraday files remained physically unavailable, so no 1h/15m test was attempted.",
    }

    pd.concat(returns_by_config, axis=1).to_csv(ITER_DIR / "returns.csv")
    (ITER_DIR / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    (ITER_DIR / "RESULTS.json").write_text(json.dumps(to_jsonable(results), indent=2), encoding="utf-8")


def audit_data() -> dict[str, object]:
    daily_files = []
    for ticker in ["GLD", "xauusd", "SPY", "SHV"]:
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
            })
        daily_files.append(item)
    return {
        "daily_files": daily_files,
        "intraday_files": intraday_file_items(HOUR_DIR) + intraday_file_items(MIN15_DIR),
        "hour_directory_exists": HOUR_DIR.exists(),
        "hour_directory_file_count": len(list(HOUR_DIR.glob("*.parquet"))) if HOUR_DIR.exists() else None,
        "min15_directory_exists": MIN15_DIR.exists(),
        "min15_directory_file_count": len(list(MIN15_DIR.glob("*.parquet"))) if MIN15_DIR.exists() else None,
    }


def intraday_file_items(directory: Path) -> list[dict[str, object]]:
    return [
        {"frequency": directory.parent.name, "ticker": ticker, "path": str(directory / f"{ticker}.parquet"), "exists": (directory / f"{ticker}.parquet").exists()}
        for ticker in ["GLD", "xauusd"]
    ]


def load_close(ticker: str) -> pd.Series:
    df = pd.read_parquet(PRICE_DIR / f"{ticker}.parquet").copy()
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df = df[~df.index.duplicated()].sort_index()
    col = "adj_close" if "adj_close" in df.columns else "close"
    return df[col].astype(float).dropna()


def strategy_returns(close: pd.Series, spy_close: pd.Series, cash: pd.Series, cfg: Config) -> tuple[pd.Series, pd.Series]:
    close, spy_close = close.align(spy_close, join="inner")
    cash = cash.reindex(close.index).ffill()
    asset_ret = close.pct_change().fillna(0.0)
    cash_ret = cash.pct_change().fillna(0.0)
    exposure = rs_exposure(close, spy_close, cfg).shift(1).fillna(0.0)
    loop_returns = exposure * asset_ret + (1.0 - exposure) * cash_ret
    vector_returns = exposure * asset_ret + (1.0 - exposure) * cash_ret
    warmup = max(cfg.rs_sma, cfg.momentum) + 1
    return loop_returns.iloc[warmup:], vector_returns.iloc[warmup:]


def rs_exposure(close: pd.Series, spy_close: pd.Series, cfg: Config) -> pd.Series:
    ratio = close / spy_close.reindex(close.index).ffill()
    rs_on = ratio > ratio.rolling(cfg.rs_sma, min_periods=cfg.rs_sma).mean()
    own_momentum_on = close.pct_change(cfg.momentum) > 0.0
    return (rs_on & own_momentum_on).astype(float)


def fixed_strategy_from_mcpt_prices(prices: np.ndarray, spy_prices: np.ndarray, cfg: Config) -> np.ndarray:
    close = pd.Series(np.exp(np.asarray(prices, dtype=float) - 100.0), index=pd.RangeIndex(len(prices)), dtype=float)
    spy = pd.Series(np.exp(np.asarray(spy_prices[: len(close)], dtype=float) - 100.0), index=close.index, dtype=float)
    ret = close.pct_change().fillna(0.0)
    exposure = rs_exposure(close, spy, cfg).shift(1).fillna(0.0)
    warmup = max(cfg.rs_sma, cfg.momentum) + 1
    return (exposure * ret).iloc[warmup:].to_numpy()


def compute_metrics(strategy: pd.Series, asset_bh: pd.Series, spy_bh: pd.Series) -> dict[str, float | int | str]:
    return {
        "start": str(strategy.index.min().date()),
        "end": str(strategy.index.max().date()),
        "n_obs": int(strategy.size),
        "cagr": cagr(strategy),
        "sharpe": sharpe_annualized(strategy.to_numpy()),
        "max_drawdown": max_drawdown(strategy),
        "total_return": compound(strategy),
        "same_asset_bh_cagr": cagr(asset_bh),
        "same_asset_bh_sharpe": sharpe_annualized(asset_bh.to_numpy()),
        "same_asset_bh_max_drawdown": max_drawdown(asset_bh),
        "spy_bh_cagr": cagr(spy_bh),
        "spy_bh_sharpe": sharpe_annualized(spy_bh.to_numpy()),
    }


def walk_forward_window_returns(returns: pd.Series, *, train_size: int, test_size: int, step_size: int) -> list[float]:
    values = []
    start = 0
    arr = returns.reset_index(drop=True)
    while start + train_size + test_size <= len(arr):
        test = arr.iloc[start + train_size : start + train_size + test_size]
        values.append(compound(test))
        start += step_size
    return values


def bootstrap_mean_ci(returns: np.ndarray, *, n_resamples: int, seed: int) -> list[float]:
    rng = np.random.default_rng(seed)
    arr = np.asarray(returns, dtype=float)
    means = np.empty(n_resamples)
    for i in range(n_resamples):
        means[i] = float(np.mean(rng.choice(arr, size=arr.size, replace=True)))
    return [float(np.quantile(means, 0.0005)), float(np.quantile(means, 0.9995))]


def cagr(returns: pd.Series | np.ndarray) -> float:
    arr = np.asarray(returns, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return 0.0
    return float(np.prod(1.0 + arr) ** (TRADING_DAYS / arr.size) - 1.0)


def compound(returns: pd.Series | np.ndarray) -> float:
    arr = np.asarray(returns, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return 0.0
    return float(np.prod(1.0 + arr) - 1.0)


def max_drawdown(returns: pd.Series | np.ndarray) -> float:
    arr = np.asarray(returns, dtype=float)
    equity = np.cumprod(1.0 + arr)
    peak = np.maximum.accumulate(equity)
    dd = equity / peak - 1.0
    return float(np.min(dd)) if dd.size else 0.0


def missing_bday_rate(idx: pd.DatetimeIndex) -> float:
    if len(idx) < 2:
        return 0.0
    expected = pd.bdate_range(idx.min().normalize(), idx.max().normalize())
    if len(expected) == 0:
        return 0.0
    return float(1.0 - len(pd.DatetimeIndex(idx.normalize()).intersection(expected)) / len(expected))


def write_blocked(audit: dict[str, object]) -> None:
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
        "kill_switches": ["required daily physical file missing"],
        "artifacts": [str(ITER_DIR / "PRE_REG.md"), str(ITER_DIR / "run_iteration.py"), str(ITER_DIR / "RESULTS.json")],
        "notes": "Daily physical data audit failed before strategy testing.",
    }
    (ITER_DIR / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    (ITER_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")


def to_jsonable(value):
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [to_jsonable(v) for v in value]
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    return value


if __name__ == "__main__":
    main()
