"""Phase 2 iteration 021: Wilder ASI daily swing breakout.

Wilder's Swing Index compresses OHLC action into a swing-pressure measure; the
Accumulated Swing Index can be traded on breakouts above prior swing points
`[trading_systems_methods, p.193-195]`. Signals are lagged one completed daily
bar before returns are earned `[advances_fin_ml, p.31-34]`.
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

from market_lab.backtest.validation.dsr import dsr
from market_lab.backtest.validation.pbo import pbo
from studies.success_trading_strat.scripts.validation_scaffold import (
    annualized_sharpe,
    mcpt_on_strategy_returns,
    walk_forward_mcpt,
)


ITERATION = "021-2026-05-14-wilder-asi-swing-breakout"
ITER_DIR = Path(__file__).resolve().parent
PRICE_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
HOUR_DIR = ROOT / "data" / "tiingo" / "1hour" / "prices"
MIN15_DIR = ROOT / "data" / "tiingo" / "15min" / "prices"
TRADING_DAYS = 252
CUMULATIVE_TRIALS_AFTER = 184


@dataclass(frozen=True)
class Config:
    name: str
    ticker: str
    entry_lookback: int
    exit_lookback: int
    max_hold: int


CONFIGS = [
    Config("spy_asi20_10_h20", "SPY", 20, 10, 20),
    Config("qqq_asi20_10_h20", "QQQ", 20, 10, 20),
    Config("gld_asi20_10_h20", "GLD", 20, 10, 20),
    Config("xau_asi20_10_h20", "xauusd", 20, 10, 20),
]


def main() -> None:
    audit = audit_data()
    required = {"SPY", "QQQ", "GLD", "xauusd", "SHV"}
    if any((item["ticker"] in required) and not item["exists"] for item in audit["daily_files"]):
        write_blocked(audit, "missing required daily file")
        return
    if any((item["ticker"] in required) and not item.get("has_ohlc", False) for item in audit["daily_files"]):
        write_blocked(audit, "missing required adjusted OHLC columns")
        return

    frames = {ticker: load_frame(ticker) for ticker in ["SPY", "QQQ", "GLD", "xauusd", "SHV"]}
    returns_by_config: dict[str, pd.Series] = {}
    vector_returns_by_config: dict[str, pd.Series] = {}
    metrics_by_config: dict[str, dict[str, float | int | str]] = {}

    for cfg in CONFIGS:
        strat, vector = strategy_returns(frames[cfg.ticker], frames["SHV"], cfg)
        returns_by_config[cfg.name] = strat
        vector_returns_by_config[cfg.name] = vector
        asset_bh = frames[cfg.ticker]["close"].pct_change().reindex(strat.index).fillna(0.0)
        spy_bh = frames["SPY"]["close"].pct_change().reindex(strat.index).fillna(0.0)
        gld_bh = frames["GLD"]["close"].pct_change().reindex(strat.index).fillna(0.0)
        xau_bh = frames["xauusd"]["close"].pct_change().reindex(strat.index).fillna(0.0)
        metrics_by_config[cfg.name] = compute_metrics(strat, asset_bh, spy_bh, gld_bh, xau_bh)

    best_name = max(metrics_by_config, key=lambda name: metrics_by_config[name]["sharpe"])
    best_cfg = next(cfg for cfg in CONFIGS if cfg.name == best_name)
    best_returns = returns_by_config[best_name]
    best_frame = frames[best_cfg.ticker].reindex(best_returns.index).dropna()
    mcpt_prices = np.log(best_frame["close"].to_numpy()) + 100.0
    ohl_ratios = ohlc_ratios(best_frame)

    returns_matrix = pd.concat(returns_by_config, axis=1).dropna()
    pbo_result = pbo(returns_matrix.to_numpy(), n_blocks=10)
    dsr_result = dsr(best_returns.to_numpy(), n_trials=CUMULATIVE_TRIALS_AFTER)
    is_mcpt = mcpt_on_strategy_returns(
        mcpt_prices,
        lambda series: fixed_strategy_from_mcpt_prices(series, ohl_ratios, best_cfg),
        n_permutations=200,
        seed=4211,
        metric=annualized_sharpe,
    )
    train_size = min(756, max(252, mcpt_prices.size // 3))
    wf_result = walk_forward_mcpt(
        mcpt_prices,
        lambda train, test: fixed_strategy_from_mcpt_prices(np.concatenate([train, test]), ohl_ratios, best_cfg)[-(test.size - 1) :],
        train_size=train_size,
        test_size=252,
        step_size=252,
        n_permutations=100,
        seed=4212,
        metric=annualized_sharpe,
    )
    wf_returns_by_window = walk_forward_window_returns(best_returns, train_size=756, test_size=252, step_size=252)
    bootstrap_ci = bootstrap_mean_ci(best_returns.to_numpy(), n_resamples=2000, seed=4213)
    vector_delta = abs(cagr(best_returns) - cagr(vector_returns_by_config[best_name]))
    asset_bh = frames[best_cfg.ticker]["close"].pct_change().reindex(best_returns.index).fillna(0.0)

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
        "benchmark": {"primary": f"{best_cfg.ticker}_buy_hold", "context": "SPY_buy_hold", "gold_context": "GLD_and_xauusd_buy_hold"},
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
        "notes": "Daily Wilder ASI breakout tested on SPY/QQQ/GLD/xauusd. Intraday 1h/15m files remained unavailable, so no Track B hybrid was synthesized.",
    }

    pd.concat(returns_by_config, axis=1).to_csv(ITER_DIR / "returns.csv")
    (ITER_DIR / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    (ITER_DIR / "RESULTS.json").write_text(json.dumps(to_jsonable(results), indent=2), encoding="utf-8")


def audit_data() -> dict[str, object]:
    daily_files = []
    for ticker in ["SPY", "QQQ", "GLD", "xauusd", "SHV"]:
        path = PRICE_DIR / f"{ticker}.parquet"
        item: dict[str, object] = {"ticker": ticker, "path": str(path), "exists": path.exists()}
        if path.exists():
            df = pd.read_parquet(path)
            idx = pd.to_datetime(df.index)
            columns = set(df.columns)
            item.update({
                "rows": int(len(df)),
                "first": str(idx.min()),
                "last": str(idx.max()),
                "timezone": str(getattr(idx, "tz", None)),
                "columns": list(df.columns),
                "has_ohlc": {"open", "high", "low", "close", "adj_close"}.issubset(columns),
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
        for ticker in ["SPY", "QQQ", "GLD", "xauusd"]
    ]


def load_frame(ticker: str) -> pd.DataFrame:
    raw = pd.read_parquet(PRICE_DIR / f"{ticker}.parquet").copy()
    raw.index = pd.to_datetime(raw.index).tz_localize(None)
    raw = raw[~raw.index.duplicated()].sort_index()
    factor = (raw["adj_close"] / raw["close"]).replace([np.inf, -np.inf], np.nan).fillna(1.0)
    return pd.DataFrame({
        "open": raw["open"].astype(float) * factor,
        "high": raw["high"].astype(float) * factor,
        "low": raw["low"].astype(float) * factor,
        "close": raw["adj_close"].astype(float),
    }).dropna()


def strategy_returns(frame: pd.DataFrame, cash_frame: pd.DataFrame, cfg: Config) -> tuple[pd.Series, pd.Series]:
    cash = cash_frame["close"].reindex(frame.index).ffill()
    asset_ret = frame["close"].pct_change().fillna(0.0)
    cash_ret = cash.pct_change().fillna(0.0)
    exposure = asi_exposure(frame, cfg).shift(1).fillna(0.0)
    loop_returns = exposure * asset_ret + (1.0 - exposure) * cash_ret
    vector_returns = exposure * asset_ret + (1.0 - exposure) * cash_ret
    warmup = max(cfg.entry_lookback, cfg.exit_lookback) + 5
    return loop_returns.iloc[warmup:], vector_returns.iloc[warmup:]


def asi_exposure(frame: pd.DataFrame, cfg: Config) -> pd.Series:
    asi = accumulated_swing_index(frame)
    entry_level = asi.shift(1).rolling(cfg.entry_lookback, min_periods=cfg.entry_lookback).max()
    exit_level = asi.shift(1).rolling(cfg.exit_lookback, min_periods=cfg.exit_lookback).min()
    exposure = np.zeros(len(frame), dtype=float)
    in_trade = False
    bars_held = 0
    for i in range(len(frame)):
        valid = np.isfinite(asi.iloc[i]) and np.isfinite(entry_level.iloc[i]) and np.isfinite(exit_level.iloc[i])
        if in_trade:
            bars_held += 1
            exit_now = (not valid) or asi.iloc[i] < exit_level.iloc[i] or bars_held >= cfg.max_hold
            if exit_now:
                in_trade = False
                bars_held = 0
        if not in_trade and valid and asi.iloc[i] > entry_level.iloc[i]:
            in_trade = True
            bars_held = 0
        exposure[i] = 1.0 if in_trade else 0.0
    return pd.Series(exposure, index=frame.index)


def accumulated_swing_index(frame: pd.DataFrame) -> pd.Series:
    high = frame["high"]
    low = frame["low"]
    close = frame["close"]
    open_ = frame["open"]
    prev_close = close.shift(1)
    prev_open = open_.shift(1)
    a = (high - prev_close).abs()
    b = (low - prev_close).abs()
    c = (high - low).abs()
    d = (prev_close - prev_open).abs()
    r = pd.Series(np.nan, index=frame.index, dtype=float)
    r = r.mask((a >= b) & (a >= c), a - 0.5 * b + 0.25 * d)
    r = r.mask((b > a) & (b >= c), b - 0.5 * a + 0.25 * d)
    r = r.mask((c > a) & (c > b), c + 0.25 * d)
    k = np.maximum(a, b)
    numerator = (close - prev_close) + 0.5 * (close - open_) + 0.25 * (prev_close - prev_open)
    si = 50.0 * numerator / r.replace(0.0, np.nan) * k / close.replace(0.0, np.nan)
    return si.replace([np.inf, -np.inf], np.nan).fillna(0.0).cumsum()


def ohlc_ratios(frame: pd.DataFrame) -> dict[str, np.ndarray]:
    close = frame["close"].to_numpy(dtype=float)
    return {
        "open": frame["open"].to_numpy(dtype=float) / close,
        "high": frame["high"].to_numpy(dtype=float) / close,
        "low": frame["low"].to_numpy(dtype=float) / close,
    }


def fixed_strategy_from_mcpt_prices(prices: np.ndarray, ratios: dict[str, np.ndarray], cfg: Config) -> np.ndarray:
    close = pd.Series(np.exp(np.asarray(prices, dtype=float) - 100.0), index=pd.RangeIndex(len(prices)), dtype=float)
    n = len(close)
    frame = pd.DataFrame({
        "open": close.to_numpy() * ratios["open"][:n],
        "high": close.to_numpy() * ratios["high"][:n],
        "low": close.to_numpy() * ratios["low"][:n],
        "close": close.to_numpy(),
    })
    ret = close.pct_change().fillna(0.0)
    exposure = asi_exposure(frame, cfg).shift(1).fillna(0.0)
    returns = exposure * ret
    warmup = max(cfg.entry_lookback, cfg.exit_lookback) + 5
    return returns.iloc[warmup:].to_numpy(dtype=float)


def compute_metrics(strategy: pd.Series, asset_bh: pd.Series, spy_bh: pd.Series, gld_bh: pd.Series, xau_bh: pd.Series) -> dict[str, float | int | str]:
    return {
        "start": str(strategy.index.min().date()),
        "end": str(strategy.index.max().date()),
        "n_obs": int(strategy.size),
        "cagr": cagr(strategy),
        "sharpe": sharpe(strategy),
        "max_drawdown": max_drawdown(strategy),
        "total_return": compound(strategy),
        "same_asset_bh_cagr": cagr(asset_bh),
        "same_asset_bh_sharpe": sharpe(asset_bh),
        "same_asset_bh_max_drawdown": max_drawdown(asset_bh),
        "spy_bh_cagr": cagr(spy_bh),
        "spy_bh_sharpe": sharpe(spy_bh),
        "gld_bh_cagr": cagr(gld_bh),
        "gld_bh_sharpe": sharpe(gld_bh),
        "xau_bh_cagr": cagr(xau_bh),
        "xau_bh_sharpe": sharpe(xau_bh),
    }


def walk_forward_window_returns(returns: pd.Series, train_size: int, test_size: int, step_size: int) -> list[float]:
    out = []
    start = 0
    while start + train_size + test_size <= len(returns):
        test = returns.iloc[start + train_size : start + train_size + test_size]
        out.append(compound(test))
        start += step_size
    return out


def bootstrap_mean_ci(values: np.ndarray, n_resamples: int, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    values = np.asarray(values, dtype=float)
    means = np.empty(n_resamples, dtype=float)
    for i in range(n_resamples):
        sample = rng.choice(values, size=values.size, replace=True)
        means[i] = float(np.mean(sample))
    return float(np.quantile(means, 0.0005)), float(np.quantile(means, 0.9995))


def cagr(returns: pd.Series) -> float:
    if len(returns) == 0:
        return 0.0
    total = compound(returns)
    years = len(returns) / TRADING_DAYS
    return float((1.0 + total) ** (1.0 / years) - 1.0) if years > 0 and total > -1.0 else -1.0


def compound(returns: pd.Series | np.ndarray) -> float:
    values = np.asarray(returns, dtype=float)
    return float(np.prod(1.0 + values) - 1.0)


def sharpe(returns: pd.Series) -> float:
    values = returns.to_numpy(dtype=float)
    std = float(np.std(values, ddof=1))
    return 0.0 if std == 0.0 else float(np.mean(values) / std * np.sqrt(TRADING_DAYS))


def max_drawdown(returns: pd.Series) -> float:
    equity = (1.0 + returns).cumprod()
    drawdown = equity / equity.cummax() - 1.0
    return float(drawdown.min())


def missing_bday_rate(index: pd.DatetimeIndex) -> float:
    idx = pd.to_datetime(index).tz_localize(None).normalize()
    if len(idx) < 2:
        return 0.0
    expected = pd.bdate_range(idx.min(), idx.max())
    return float(1.0 - len(idx.intersection(expected)) / len(expected))


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


def to_jsonable(obj: object) -> object:
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj


if __name__ == "__main__":
    main()
