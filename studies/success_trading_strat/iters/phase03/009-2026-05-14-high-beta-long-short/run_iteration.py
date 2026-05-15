"""Phase 3 iteration 009: high-beta long/short relative momentum.

The mechanism tests cross-sectional relative strength with explicit gross
exposure and financing/borrow costs, rather than another defensive long/flat
filter `[stocks_on_the_move, p.66-67]`, `[systematic_trading, p.137-148]`.
Validation keeps MCPT, PBO and DSR hard controls `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
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
from studies.success_trading_strat.scripts.validation_scaffold import annualized_sharpe


ITERATION = "009-2026-05-14-high-beta-long-short"
ITER_DIR = Path(__file__).resolve().parent
PRICE_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
TRADING_DAYS = 252
CUMULATIVE_TRIALS_AFTER = 260
UNIVERSE = ["QQQ", "SMH", "SOXX", "XLK"]
AUDIT_TICKERS = ["QQQ", "SMH", "SOXX", "XLK", "SPY", "SHV"]
REQUIRED = {"QQQ", "SMH", "SOXX", "XLK", "SPY", "SHV"}
FINANCING_ANNUAL = 0.05


@dataclass(frozen=True)
class Config:
    name: str
    lookback: int
    long_count: int
    short_count: int
    gross: float


CONFIGS = [
    Config("ls_m63_top1_bottom1_g100", 63, 1, 1, 1.00),
    Config("ls_m63_top1_bottom1_g150", 63, 1, 1, 1.50),
    Config("ls_m126_top1_bottom1_g150", 126, 1, 1, 1.50),
    Config("ls_m126_top2_bottom1_g150", 126, 2, 1, 1.50),
]


def main() -> None:
    audit = audit_data()
    if any((item["ticker"] in REQUIRED) and not item["exists"] for item in audit["daily_files"]):
        write_blocked(audit, "missing required daily parquet")
        return
    if any((item["ticker"] in REQUIRED) and not item.get("has_close", False) for item in audit["daily_files"]):
        write_blocked(audit, "missing required close column")
        return

    closes = {ticker: load_close(ticker) for ticker in REQUIRED}
    prices = pd.concat({ticker: closes[ticker] for ticker in UNIVERSE}, axis=1).dropna()
    spy_close = closes["SPY"].reindex(prices.index).dropna()
    shv_close = closes["SHV"].reindex(prices.index).dropna()
    common_index = prices.index.intersection(spy_close.index).intersection(shv_close.index)
    prices = prices.reindex(common_index).dropna()
    spy_close = spy_close.reindex(prices.index).dropna()
    shv_close = shv_close.reindex(prices.index).dropna()

    returns_by_config: dict[str, pd.Series] = {}
    reference_returns_by_config: dict[str, pd.Series] = {}
    weights_by_config: dict[str, pd.DataFrame] = {}
    metrics_by_config: dict[str, dict[str, object]] = {}

    for cfg in CONFIGS:
        strat, reference, weights = strategy_returns(prices, cfg)
        returns_by_config[cfg.name] = strat
        reference_returns_by_config[cfg.name] = reference
        weights_by_config[cfg.name] = weights
        metrics_by_config[cfg.name] = compute_metrics(strat, weights, aligned_benchmarks(strat.index, prices, spy_close, shv_close))

    best_name = max(metrics_by_config, key=lambda name: (metrics_by_config[name]["terminal_wealth"], metrics_by_config[name]["sharpe"]))
    best_cfg = next(cfg for cfg in CONFIGS if cfg.name == best_name)
    best_returns = returns_by_config[best_name]
    best_weights = weights_by_config[best_name]
    returns_matrix = pd.concat(returns_by_config, axis=1).dropna()

    pbo_result = pbo(returns_matrix.to_numpy(dtype=float), n_blocks=10)
    dsr_result = dsr(best_returns.to_numpy(dtype=float), n_trials=CUMULATIVE_TRIALS_AFTER)
    is_mcpt = mcpt_joint(prices, best_cfg, n_permutations=200, seed=5901)
    wf_mcpt = walk_forward_mcpt_joint(prices, best_cfg, train_size=756, test_size=252, step_size=252, n_permutations=100, seed=5902)
    wf_returns_by_window = walk_forward_window_returns(best_returns, train_size=756, test_size=252, step_size=252)
    bootstrap_ci = bootstrap_mean_ci(best_returns.to_numpy(dtype=float), n_resamples=2000, seed=5903)
    vector_delta = abs(cagr(best_returns) - cagr(reference_returns_by_config[best_name]))
    best_metrics = metrics_by_config[best_name]

    econ_cagr = best_metrics["cagr"] > best_metrics["ew_bh_cagr"]
    econ_terminal = best_metrics["terminal_wealth"] > best_metrics["ew_bh_terminal_wealth"]
    gates = {
        "economic_cagr_vs_primary_equal_weight": econ_cagr,
        "economic_terminal_vs_primary_equal_weight": econ_terminal,
        "economic_cagr_vs_spy_opportunity": best_metrics["cagr"] > best_metrics["spy_bh_cagr"],
        "is_mcpt": is_mcpt["p_value"] <= 0.01,
        "wf_mcpt": wf_mcpt["p_value"] <= 0.05,
        "pbo": pbo_result.pbo < 0.5,
        "dsr": dsr_result.p_value < 0.05,
        "wf_windows": len(wf_returns_by_window) >= 8 and sum(x > 0 for x in wf_returns_by_window) >= 6,
        "oos": compound(best_returns.iloc[int(len(best_returns) * 0.8) :]) > 0,
        "fwd_63d": compound(best_returns.iloc[-63:]) > 0,
        "bootstrap": bootstrap_ci[0] > 0,
        "cross_lib": vector_delta <= 0.03,
    }
    economic_pass = econ_cagr and econ_terminal
    strict_winner = all(gates.values())
    validation_failed = not all(v for k, v in gates.items() if not k.startswith("economic_"))
    if strict_winner:
        status = "strict_winner"
    elif economic_pass and validation_failed:
        status = "economic_beater_not_validated"
    else:
        status = "fail"

    kill_switches = []
    if not econ_cagr:
        kill_switches.append("CAGR <= primary equal-weight opportunity buy-and-hold")
    if not econ_terminal:
        kill_switches.append("terminal wealth <= primary equal-weight opportunity buy-and-hold")
    if validation_failed:
        kill_switches.append("failed one or more strict validation gates")

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
            "best_asset_weights_mean": {k: float(v) for k, v in best_weights.mean().items()},
            "best_gross_mean": float(best_weights.abs().sum(axis=1).mean()),
            "best_net_exposure_mean": float(best_weights.sum(axis=1).mean()),
            "financing_annual_assumption": FINANCING_ANNUAL,
        },
        "benchmark": {
            "primary": "equal_weight_QQQ_SMH_SOXX_XLK_buy_hold",
            "opportunity": "SPY_buy_hold",
            "context": ["QQQ_buy_hold", "SMH_buy_hold", "SOXX_buy_hold", "XLK_buy_hold", "SHV_buy_hold"],
            "aligned_start": best_metrics["start"],
            "aligned_end": best_metrics["end"],
        },
        "gates": {
            **gates,
            "pbo_value": pbo_result.pbo,
            "dsr_p_value": dsr_result.p_value,
            "is_mcpt_p_value": is_mcpt["p_value"],
            "wf_mcpt_p_value": wf_mcpt["p_value"],
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
        "notes": "High-beta long/short relative momentum with explicit 5% annual financing/borrow proxy. No tax model; research-only.",
    }

    returns_matrix.to_csv(ITER_DIR / "returns.csv")
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


def strategy_returns(prices: pd.DataFrame, cfg: Config) -> tuple[pd.Series, pd.Series, pd.DataFrame]:
    asset_returns = prices.pct_change().fillna(0.0)
    weights = long_short_weights(prices, cfg).shift(1).fillna(0.0)
    gross = weights.abs().sum(axis=1)
    short_notional = weights.clip(upper=0.0).abs().sum(axis=1)
    leverage_notional = (gross - 1.0).clip(lower=0.0)
    financing_cost = (short_notional + leverage_notional) * FINANCING_ANNUAL / TRADING_DAYS
    loop_returns = ((weights * asset_returns).sum(axis=1) - financing_cost).rename(cfg.name)
    reference_returns = reference_strategy_returns(asset_returns, weights, financing_cost).rename(cfg.name)
    warmup = cfg.lookback + 2
    return loop_returns.iloc[warmup:], reference_returns.iloc[warmup:], weights.iloc[warmup:]


def long_short_weights(prices: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    momentum = prices / prices.shift(cfg.lookback) - 1.0
    arr = momentum.to_numpy(dtype=float)
    finite = np.isfinite(arr)
    weights = np.zeros_like(arr, dtype=float)
    long_book = cfg.gross / 2.0
    short_book = cfg.gross / 2.0
    for row_idx in range(arr.shape[0]):
        n_valid = int(finite[row_idx].sum())
        if n_valid < cfg.long_count + cfg.short_count:
            continue
        scores = np.where(finite[row_idx], arr[row_idx], np.nan)
        ranked_desc = np.argsort(-np.nan_to_num(scores, nan=-np.inf))
        ranked_asc = np.argsort(np.nan_to_num(scores, nan=np.inf))
        longs = ranked_desc[: cfg.long_count]
        shorts = ranked_asc[: cfg.short_count]
        weights[row_idx, longs] = long_book / cfg.long_count
        weights[row_idx, shorts] -= short_book / cfg.short_count
    return pd.DataFrame(weights, index=prices.index, columns=prices.columns)


def reference_strategy_returns(asset_returns: pd.DataFrame, weights: pd.DataFrame, financing_cost: pd.Series) -> pd.Series:
    arr = asset_returns.to_numpy(dtype=float)
    w = weights.to_numpy(dtype=float)
    cost = financing_cost.to_numpy(dtype=float)
    out = np.empty(arr.shape[0], dtype=float)
    for i in range(arr.shape[0]):
        out[i] = float(np.dot(w[i], arr[i]) - cost[i])
    return pd.Series(out, index=asset_returns.index)


def aligned_benchmarks(index: pd.Index, prices: pd.DataFrame, spy_close: pd.Series, shv_close: pd.Series) -> dict[str, pd.Series]:
    asset_returns = prices.pct_change().fillna(0.0).reindex(index).fillna(0.0)
    spy = spy_close.pct_change().fillna(0.0).reindex(index).fillna(0.0)
    shv = shv_close.pct_change().fillna(0.0).reindex(index).fillna(0.0)
    out = {f"{ticker}_bh": asset_returns[ticker] for ticker in prices.columns}
    out["ew_bh"] = asset_returns.mean(axis=1)
    out["spy_bh"] = spy
    out["shv_bh"] = shv
    return out


def mcpt_joint(prices: pd.DataFrame, cfg: Config, *, n_permutations: int, seed: int) -> dict[str, object]:
    observed = annualized_sharpe(strategy_returns(prices, cfg)[0].to_numpy(dtype=float))
    rng = np.random.default_rng(seed)
    stats = np.empty(n_permutations, dtype=float)
    for i in range(n_permutations):
        permuted = permute_joint_return_rows(prices, rng)
        stats[i] = annualized_sharpe(strategy_returns(permuted, cfg)[0].to_numpy(dtype=float))
    return {"observed": observed, "p_value": float(np.sum(stats >= observed) / n_permutations), "n_permutations": n_permutations}


def walk_forward_mcpt_joint(
    prices: pd.DataFrame,
    cfg: Config,
    *,
    train_size: int,
    test_size: int,
    step_size: int,
    n_permutations: int,
    seed: int,
) -> dict[str, object]:
    observed_returns = walk_forward_strategy_returns(prices, cfg, train_size=train_size, test_size=test_size, step_size=step_size)
    observed = annualized_sharpe(observed_returns)
    rng = np.random.default_rng(seed)
    stats = np.empty(n_permutations, dtype=float)
    for i in range(n_permutations):
        permuted = permute_after_initial_train(prices, train_size, rng)
        stats[i] = annualized_sharpe(walk_forward_strategy_returns(permuted, cfg, train_size=train_size, test_size=test_size, step_size=step_size))
    return {"observed": observed, "p_value": float(np.sum(stats >= observed) / n_permutations), "n_permutations": n_permutations}


def walk_forward_strategy_returns(prices: pd.DataFrame, cfg: Config, *, train_size: int, test_size: int, step_size: int) -> np.ndarray:
    out: list[np.ndarray] = []
    start = 0
    while start + train_size + test_size <= len(prices):
        frame = prices.iloc[start : start + train_size + test_size]
        test_index = prices.index[start + train_size : start + train_size + test_size]
        strat = strategy_returns(frame, cfg)[0].reindex(test_index).dropna()
        out.append(strat.to_numpy(dtype=float))
        start += step_size
    return np.concatenate(out) if out else np.array([], dtype=float)


def permute_joint_return_rows(prices: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    returns = prices.pct_change().dropna().to_numpy(dtype=float)
    shuffled = returns[rng.permutation(np.arange(returns.shape[0]))]
    values = np.vstack([np.ones((1, prices.shape[1])), np.cumprod(1.0 + shuffled, axis=0)])
    return pd.DataFrame(values, index=prices.index, columns=prices.columns)


def permute_after_initial_train(prices: pd.DataFrame, initial_train_size: int, rng: np.random.Generator) -> pd.DataFrame:
    if initial_train_size < 2 or initial_train_size >= len(prices) - 1:
        raise ValueError("initial_train_size must leave a non-empty permuted tail")
    returns = prices.pct_change().dropna().to_numpy(dtype=float)
    prefix_prices = prices.iloc[:initial_train_size].to_numpy(dtype=float)
    tail_returns = returns[initial_train_size - 1 :]
    shuffled_tail = tail_returns[rng.permutation(np.arange(tail_returns.shape[0]))]
    tail_prices = prefix_prices[-1:] * np.cumprod(1.0 + shuffled_tail, axis=0)
    values = np.vstack([prefix_prices, tail_prices])
    return pd.DataFrame(values, index=prices.index, columns=prices.columns)


def compute_metrics(strategy: pd.Series, weights: pd.DataFrame, benchmarks: dict[str, pd.Series]) -> dict[str, object]:
    out: dict[str, object] = {
        "start": str(strategy.index.min().date()),
        "end": str(strategy.index.max().date()),
        "n_obs": int(strategy.size),
        "cagr": cagr(strategy),
        "sharpe": sharpe(strategy),
        "sortino": sortino(strategy),
        "calmar": calmar(strategy),
        "max_drawdown": max_drawdown(strategy),
        "terminal_wealth": 1.0 + compound(strategy),
        "exposure_time": exposure_time(weights),
        "annual_turnover": annual_turnover(weights),
        "gross_mean": float(weights.abs().sum(axis=1).mean()),
        "gross_max": float(weights.abs().sum(axis=1).max()),
        "net_exposure_mean": float(weights.sum(axis=1).mean()),
        "short_notional_mean": float(weights.clip(upper=0.0).abs().sum(axis=1).mean()),
    }
    for name, series in benchmarks.items():
        out[f"{name}_cagr"] = cagr(series)
        out[f"{name}_terminal_wealth"] = 1.0 + compound(series)
        out[f"{name}_sharpe"] = sharpe(series)
        out[f"{name}_max_drawdown"] = max_drawdown(series)
    return out


def exposure_time(weights: pd.DataFrame) -> float:
    return float(np.mean(weights.abs().sum(axis=1).to_numpy(dtype=float) > 1e-12))


def annual_turnover(weights: pd.DataFrame) -> float:
    daily_turnover = weights.diff().abs().sum(axis=1).fillna(0.0) / 2.0
    years = len(weights) / TRADING_DAYS
    return float(daily_turnover.sum() / years) if years > 0 else 0.0


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


def sortino(returns: pd.Series) -> float:
    values = returns.to_numpy(dtype=float)
    downside = values[values < 0.0]
    if downside.size < 2:
        return 0.0
    std = float(np.std(downside, ddof=1))
    return 0.0 if std == 0.0 else float(np.mean(values) / std * np.sqrt(TRADING_DAYS))


def calmar(returns: pd.Series) -> float:
    mdd = abs(max_drawdown(returns))
    return 0.0 if mdd == 0.0 else cagr(returns) / mdd


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
        "benchmark": {"primary": "equal_weight_QQQ_SMH_SOXX_XLK_buy_hold", "opportunity": "SPY_buy_hold"},
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
