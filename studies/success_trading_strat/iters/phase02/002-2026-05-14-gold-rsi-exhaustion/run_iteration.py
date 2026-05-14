"""Phase 2 iteration 002: daily GLD RSI exhaustion mean reversion.

Short-horizon RSI mean reversion is a classical countertrend setup, but any
small parameter grid still requires MCPT/PBO/DSR controls
`[quant_trading_chan, p.51]`, `[quant_trading_chan, p.142-143]`,
`[advances_fin_ml, p.208-211]`.
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
TRADING_DAYS = 252
CUMULATIVE_TRIALS_AFTER = 108


@dataclass(frozen=True)
class Config:
    name: str
    rsi_lookback: int
    entry_rsi: float
    exit_rsi: float
    trend_sma: int


CONFIGS = [
    Config("gld_rsi2_e5_x60_sma200", 2, 5.0, 60.0, 200),
    Config("gld_rsi2_e10_x70_sma200", 2, 10.0, 70.0, 200),
    Config("gld_rsi3_e10_x60_sma150", 3, 10.0, 60.0, 150),
    Config("gld_rsi3_e15_x70_sma150", 3, 15.0, 70.0, 150),
]


def main() -> None:
    audit = audit_data()
    if any(not item["exists"] for item in audit["daily_files"]):
        write_blocked(audit)
        return

    frames = {ticker: load_prices(ticker) for ticker in ["GLD", "SHV", "SPY"]}
    returns_by_config: dict[str, pd.Series] = {}
    vector_returns_by_config: dict[str, pd.Series] = {}
    metrics_by_config: dict[str, dict[str, float | int | str]] = {}

    for cfg in CONFIGS:
        strat, _pos, vector = strategy_returns(frames["GLD"]["price"], frames["SHV"]["price"], cfg)
        returns_by_config[cfg.name] = strat
        vector_returns_by_config[cfg.name] = vector
        aligned_gld = frames["GLD"]["price"].pct_change().reindex(strat.index).fillna(0.0)
        aligned_spy = frames["SPY"]["price"].pct_change().reindex(strat.index).fillna(0.0)
        metrics_by_config[cfg.name] = compute_metrics(strat, aligned_gld, aligned_spy)

    best_name = max(metrics_by_config, key=lambda name: metrics_by_config[name]["sharpe"])
    best_cfg = next(cfg for cfg in CONFIGS if cfg.name == best_name)
    best_returns = returns_by_config[best_name]
    best_prices = frames["GLD"]["price"].reindex(best_returns.index).dropna()
    mcpt_prices = np.log(best_prices.to_numpy()) + 100.0

    returns_matrix = pd.concat(returns_by_config, axis=1).dropna()
    pbo_result = pbo(returns_matrix.to_numpy(), n_blocks=10)
    dsr_result = dsr(best_returns.to_numpy(), n_trials=CUMULATIVE_TRIALS_AFTER)
    is_mcpt = mcpt_on_strategy_returns(
        mcpt_prices,
        lambda prices: fixed_strategy_from_mcpt_prices(prices, best_cfg),
        n_permutations=200,
        seed=1501,
        metric=annualized_sharpe,
    )
    wf_result = walk_forward_mcpt(
        mcpt_prices,
        lambda train, test: fixed_strategy_from_mcpt_prices(np.concatenate([train, test]), best_cfg)[-(test.size - 1) :],
        train_size=min(756, max(252, best_prices.size // 3)),
        test_size=252,
        step_size=252,
        n_permutations=100,
        seed=1502,
        metric=annualized_sharpe,
    )
    wf_returns_by_window = walk_forward_window_returns(best_returns, train_size=756, test_size=252, step_size=252)
    bootstrap_ci = bootstrap_mean_ci(best_returns.to_numpy(), n_resamples=2000, seed=1503)
    vector_delta = abs(cagr(best_returns) - cagr(vector_returns_by_config[best_name]))
    gld_bh = frames["GLD"]["price"].pct_change().reindex(best_returns.index).fillna(0.0)

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
    status = "strict_winner" if strict_winner else "fail"

    results = {
        "iteration": "002-2026-05-14-gold-rsi-exhaustion",
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
            "same_asset_buyhold_total_return": compound(gld_bh),
        },
        "benchmark": {
            "primary": "GLD_buy_hold",
            "context": "SPY_buy_hold",
        },
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
        "notes": "Daily GLD RSI exhaustion tested only; 1h physical cache remains absent, so intraday was not synthesized.",
    }

    pd.concat(returns_by_config, axis=1).to_csv(ITER_DIR / "returns.csv")
    (ITER_DIR / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    (ITER_DIR / "RESULTS.json").write_text(json.dumps(to_jsonable(results), indent=2), encoding="utf-8")


def audit_data() -> dict[str, object]:
    daily_files = []
    for ticker in ["GLD", "SHV", "SPY"]:
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
    intraday_files = []
    for ticker in ["GLD", "xauusd"]:
        path = HOUR_DIR / f"{ticker}.parquet"
        intraday_files.append({"ticker": ticker, "path": str(path), "exists": path.exists()})
    return {
        "daily_files": daily_files,
        "intraday_files": intraday_files,
        "intraday_directory_exists": HOUR_DIR.exists(),
        "intraday_directory_file_count": len(list(HOUR_DIR.glob("*.parquet"))) if HOUR_DIR.exists() else None,
    }


def load_prices(ticker: str) -> pd.DataFrame:
    df = pd.read_parquet(PRICE_DIR / f"{ticker}.parquet").copy()
    df.index = pd.to_datetime(df.index).tz_localize(None)
    col = "adj_close" if "adj_close" in df.columns else "close"
    out = df[[col]].rename(columns={col: "price"})
    return out[~out.index.duplicated()].sort_index().dropna()


def strategy_returns(close: pd.Series, cash: pd.Series, cfg: Config) -> tuple[pd.Series, pd.Series, pd.Series]:
    price = close.dropna().astype(float)
    asset_ret = price.pct_change().fillna(0.0)
    cash_ret = cash.pct_change().reindex(price.index).fillna(0.0)
    rsi_values = rsi(price, cfg.rsi_lookback)
    trend = price > price.rolling(cfg.trend_sma).mean()
    entry = (rsi_values <= cfg.entry_rsi) & trend
    exit_ = rsi_values >= cfg.exit_rsi
    pos = pd.Series(0.0, index=price.index)
    invested = False
    for i, dt in enumerate(price.index):
        if i == 0:
            continue
        if invested and bool(exit_.loc[dt]):
            invested = False
        elif (not invested) and bool(entry.loc[dt]):
            invested = True
        pos.iloc[i] = 1.0 if invested else 0.0
    effective_pos = pos.shift(1).fillna(0.0)
    loop_returns = effective_pos * asset_ret + (1.0 - effective_pos) * cash_ret
    vector_returns = pos.shift(1).fillna(0.0) * asset_ret + (1.0 - pos.shift(1).fillna(0.0)) * cash_ret
    valid_start = max(cfg.trend_sma, cfg.rsi_lookback + 1) + 1
    return loop_returns.iloc[valid_start:], pos.iloc[valid_start:], vector_returns.iloc[valid_start:]


def rsi(price: pd.Series, lookback: int) -> pd.Series:
    delta = price.diff()
    gains = delta.clip(lower=0.0).rolling(lookback).mean()
    losses = (-delta.clip(upper=0.0)).rolling(lookback).mean()
    rs = gains / losses.replace(0.0, np.nan)
    out = 100.0 - 100.0 / (1.0 + rs)
    return out.fillna(50.0)


def fixed_strategy_from_prices(prices: np.ndarray, cfg: Config) -> np.ndarray:
    idx = pd.RangeIndex(len(prices))
    close = pd.Series(prices, index=idx, dtype=float)
    cash = pd.Series(1.0, index=idx, dtype=float)
    returns, _, _ = strategy_returns(close, cash, cfg)
    return returns.to_numpy()


def fixed_strategy_from_mcpt_prices(prices: np.ndarray, cfg: Config) -> np.ndarray:
    raw_prices = np.exp(np.asarray(prices, dtype=float) - 100.0)
    return fixed_strategy_from_prices(raw_prices, cfg)


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
        "iteration": "002-2026-05-14-gold-rsi-exhaustion",
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
