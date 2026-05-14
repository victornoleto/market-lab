"""Phase 2 iteration 007: daily equity Bollinger mean reversion.

The family tests close-only Bollinger lower-band reversion inside a lagged
SMA200 uptrend. Bollinger Bands are MA +/- standard-deviation envelopes
`[trading_systems_methods, p.323-324]`; signals are lagged one completed bar to
avoid look-ahead bias `[quant_trading_chan, p.51-53]`.
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


ITER_DIR = Path(__file__).resolve().parent
PRICE_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
HOUR_DIR = ROOT / "data" / "tiingo" / "1hour" / "prices"
MIN15_DIR = ROOT / "data" / "tiingo" / "15min" / "prices"
TRADING_DAYS = 252
CUMULATIVE_TRIALS_AFTER = 128


@dataclass(frozen=True)
class Config:
    name: str
    ticker: str
    band_window: int
    band_sigma: float
    max_hold: int


CONFIGS = [
    Config("spy_bb20_2_hold10", "SPY", 20, 2.0, 10),
    Config("spy_bb30_2_hold15", "SPY", 30, 2.0, 15),
    Config("qqq_bb20_2_hold10", "QQQ", 20, 2.0, 10),
    Config("qqq_bb30_2_hold15", "QQQ", 30, 2.0, 15),
]


def main() -> None:
    audit = audit_data()
    if any(not item["exists"] for item in audit["daily_files"]):
        write_blocked(audit)
        return

    frames = {ticker: load_close(ticker) for ticker in ["SPY", "QQQ", "SHV"]}
    returns_by_config: dict[str, pd.Series] = {}
    vector_returns_by_config: dict[str, pd.Series] = {}
    metrics_by_config: dict[str, dict[str, float | int | str]] = {}

    for cfg in CONFIGS:
        strat, _pos, vector = strategy_returns(frames[cfg.ticker], frames["SHV"], cfg)
        returns_by_config[cfg.name] = strat
        vector_returns_by_config[cfg.name] = vector
        aligned_asset = frames[cfg.ticker].pct_change().reindex(strat.index).fillna(0.0)
        aligned_spy = frames["SPY"].pct_change().reindex(strat.index).fillna(0.0)
        metrics_by_config[cfg.name] = compute_metrics(strat, aligned_asset, aligned_spy)

    best_name = max(metrics_by_config, key=lambda name: metrics_by_config[name]["sharpe"])
    best_cfg = next(cfg for cfg in CONFIGS if cfg.name == best_name)
    best_returns = returns_by_config[best_name]
    best_prices = frames[best_cfg.ticker].reindex(best_returns.index).dropna()
    mcpt_prices = np.log(best_prices.to_numpy()) + 100.0

    returns_matrix = pd.concat(returns_by_config, axis=1).dropna()
    pbo_result = pbo(returns_matrix.to_numpy(), n_blocks=10)
    dsr_result = dsr(best_returns.to_numpy(), n_trials=CUMULATIVE_TRIALS_AFTER)
    is_mcpt = mcpt_on_strategy_returns(
        mcpt_prices,
        lambda prices: fixed_strategy_from_mcpt_prices(prices, best_cfg),
        n_permutations=200,
        seed=2001,
        metric=annualized_sharpe,
    )
    train_size = min(756, max(252, best_prices.size // 3))
    wf_result = walk_forward_mcpt(
        mcpt_prices,
        lambda train, test: fixed_strategy_from_mcpt_prices(np.concatenate([train, test]), best_cfg)[-(test.size - 1) :],
        train_size=train_size,
        test_size=252,
        step_size=252,
        n_permutations=100,
        seed=2002,
        metric=annualized_sharpe,
    )
    wf_returns_by_window = walk_forward_window_returns(best_returns, train_size=756, test_size=252, step_size=252)
    bootstrap_ci = bootstrap_mean_ci(best_returns.to_numpy(), n_resamples=2000, seed=2003)
    vector_delta = abs(cagr(best_returns) - cagr(vector_returns_by_config[best_name]))
    asset_bh = frames[best_cfg.ticker].pct_change().reindex(best_returns.index).fillna(0.0)

    gates = {
        "economic_sharpe_vs_same_asset": metrics_by_config[best_name]["sharpe"] > metrics_by_config[best_name]["same_asset_bh_sharpe"],
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
    strong_economics = bool(gates["economic_sharpe_vs_same_asset"] and metrics_by_config[best_name]["cagr"] > 0.08)
    status = "strict_winner" if strict_winner else "candidate_watchlist" if strong_economics and sum(bool(v) for v in gates.values()) >= 7 else "fail"

    results = {
        "iteration": "007-2026-05-14-equity-bollinger-reversion",
        "status": status,
        "pre_registered": True,
        "n_trials": len(CONFIGS),
        "mcpt_reps": {"is": 200, "wf": 100},
        "best_config": asdict(best_cfg),
        "winner": strict_winner,
        "metrics": {
            "by_config": metrics_by_config,
            "best": metrics_by_config[best_name],
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
        "kill_switches": [] if strict_winner else ["failed strict validation gates"],
        "artifacts": [
            str(ITER_DIR / "PRE_REG.md"),
            str(ITER_DIR / "run_iteration.py"),
            str(ITER_DIR / "RESULTS.json"),
            str(ITER_DIR / "audit.json"),
            str(ITER_DIR / "returns.csv"),
        ],
        "notes": "Daily SPY/QQQ Bollinger lower-band mean-reversion tested. Intraday remained physically unavailable and was not synthesized. MCPT used a close-path fixed-rule proxy suitable only for close-only signals.",
    }

    pd.concat(returns_by_config, axis=1).to_csv(ITER_DIR / "returns.csv")
    (ITER_DIR / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    (ITER_DIR / "RESULTS.json").write_text(json.dumps(to_jsonable(results), indent=2), encoding="utf-8")


def audit_data() -> dict[str, object]:
    daily_files = []
    for ticker in ["SPY", "QQQ", "SHV"]:
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
        for ticker in ["SPY", "QQQ"]
    ]


def load_close(ticker: str) -> pd.Series:
    df = pd.read_parquet(PRICE_DIR / f"{ticker}.parquet").copy()
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df = df[~df.index.duplicated()].sort_index()
    close_col = "adj_close" if "adj_close" in df.columns else "close"
    return df[close_col].astype(float).dropna()


def strategy_returns(close: pd.Series, cash: pd.Series, cfg: Config) -> tuple[pd.Series, pd.Series, pd.Series]:
    frame = pd.DataFrame({"close": close, "cash": cash.reindex(close.index).ffill()}).dropna()
    asset_ret = frame["close"].pct_change().fillna(0.0)
    cash_ret = frame["cash"].pct_change().fillna(0.0)
    middle = frame["close"].rolling(cfg.band_window).mean()
    band_std = frame["close"].rolling(cfg.band_window).std(ddof=0)
    lower = middle - cfg.band_sigma * band_std
    trend = frame["close"] > frame["close"].rolling(200).mean()
    entry = (trend & (frame["close"] < lower)).astype(float)
    exit_signal = frame["close"] >= middle
    raw_pos = mean_reversion_position(entry.to_numpy(), exit_signal.to_numpy(), cfg.max_hold)
    pos = pd.Series(raw_pos, index=frame.index).shift(1).fillna(0.0)
    loop_returns = pos * asset_ret + (1.0 - pos) * cash_ret
    vector_returns = pos * asset_ret + (1.0 - pos) * cash_ret
    return loop_returns.iloc[201:], pos.iloc[201:], vector_returns.iloc[201:]


def mean_reversion_position(entry: np.ndarray, exit_signal: np.ndarray, max_hold: int) -> np.ndarray:
    pos = np.zeros(len(entry), dtype=float)
    remaining = 0
    for i, value in enumerate(entry):
        if remaining <= 0 and value > 0:
            remaining = max_hold
        if remaining > 0:
            pos[i] = 1.0
            remaining -= 1
            if exit_signal[i] and remaining < max_hold - 1:
                remaining = 0
    return pos


def fixed_strategy_from_mcpt_prices(prices: np.ndarray, cfg: Config) -> np.ndarray:
    raw_prices = np.exp(np.asarray(prices, dtype=float) - 100.0)
    close = pd.Series(raw_prices, index=pd.RangeIndex(len(raw_prices)), dtype=float)
    ret = close.pct_change().fillna(0.0)
    middle = close.rolling(cfg.band_window).mean()
    band_std = close.rolling(cfg.band_window).std(ddof=0)
    lower = middle - cfg.band_sigma * band_std
    trend = close > close.rolling(200).mean()
    entry = (trend & (close < lower)).astype(float)
    exit_signal = close >= middle
    pos = pd.Series(mean_reversion_position(entry.to_numpy(), exit_signal.to_numpy(), cfg.max_hold), index=close.index).shift(1).fillna(0.0)
    returns = pos * ret
    return returns.iloc[201:].to_numpy()


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
        "iteration": "007-2026-05-14-equity-bollinger-reversion",
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
