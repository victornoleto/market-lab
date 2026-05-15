"""Phase 3 iteration 024: QLD/TLT/GLD risk-migration sleeve.

The mechanism uses a permanent LETF growth sleeve plus bond/gold diversifiers and
adds controlled gross `QLD` exposure only while the strategy is underwater. This
tests Vince-style leverage-space migration rather than another long/flat timing
filter `[leverage_space, p.149-167]`, with LETF path risk and explicit financing
drag `[leverage_for_the_long_run, p.13]`, `[systematic_trading, p.137-148]`.
Validation keeps MCPT, PBO and DSR as hard anti-overfit controls
`[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.
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


ITERATION = "024-2026-05-14-qld-migration-sleeve"
ITER_DIR = Path(__file__).resolve().parent
PRICE_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
TRADING_DAYS = 252
CUMULATIVE_TRIALS_AFTER = 308
AUDIT_TICKERS = ["QLD", "TLT", "GLD", "QQQ", "SPY", "SHV"]
REQUIRED = set(AUDIT_TICKERS)
FINANCING_RATE = 0.05


@dataclass(frozen=True)
class Config:
    name: str
    base_qld: float
    base_tlt: float
    base_gld: float
    dd_trigger: float
    qld_boost: float


CONFIGS = [
    Config("qld60_tlt20_gld20_dd15_boost25", 0.60, 0.20, 0.20, -0.15, 0.25),
    Config("qld70_tlt15_gld15_dd15_boost25", 0.70, 0.15, 0.15, -0.15, 0.25),
    Config("qld60_tlt20_gld20_dd25_boost50", 0.60, 0.20, 0.20, -0.25, 0.50),
    Config("qld70_tlt15_gld15_dd25_boost50", 0.70, 0.15, 0.15, -0.25, 0.50),
]


def main() -> None:
    audit = audit_data()
    missing = [item["ticker"] for item in audit["daily_files"] if item["ticker"] in REQUIRED and not item["exists"]]
    if missing:
        write_blocked(audit, f"missing required daily parquet: {missing}")
        return
    missing_close = [item["ticker"] for item in audit["daily_files"] if item["ticker"] in REQUIRED and not item.get("has_close", False)]
    if missing_close:
        write_blocked(audit, f"missing close column: {missing_close}")
        return

    closes = {ticker: load_close(ticker) for ticker in REQUIRED}
    prices = pd.concat({ticker: closes[ticker] for ticker in AUDIT_TICKERS}, axis=1).dropna()
    if len(prices) < 756 + 252:
        write_blocked(audit, f"insufficient aligned observations: {len(prices)}")
        return

    returns_by_config: dict[str, pd.Series] = {}
    reference_returns_by_config: dict[str, pd.Series] = {}
    weights_by_config: dict[str, pd.DataFrame] = {}
    metrics_by_config: dict[str, dict[str, object]] = {}

    for cfg in CONFIGS:
        strat, reference, weights = strategy_returns(prices, cfg)
        returns_by_config[cfg.name] = strat
        reference_returns_by_config[cfg.name] = reference
        weights_by_config[cfg.name] = weights
        metrics_by_config[cfg.name] = compute_metrics(strat, weights, aligned_benchmarks(strat.index, prices))

    best_name = max(metrics_by_config, key=lambda name: (metrics_by_config[name]["terminal_wealth"], metrics_by_config[name]["sharpe"]))
    best_cfg = next(cfg for cfg in CONFIGS if cfg.name == best_name)
    best_returns = returns_by_config[best_name]
    best_weights = weights_by_config[best_name]
    returns_matrix = pd.concat(returns_by_config, axis=1).dropna()

    pbo_result = pbo(returns_matrix.to_numpy(dtype=float), n_blocks=10)
    dsr_result = dsr(best_returns.to_numpy(dtype=float), n_trials=CUMULATIVE_TRIALS_AFTER)
    is_mcpt = mcpt_joint(prices, best_cfg, n_permutations=200, seed=24001)
    wf_mcpt = walk_forward_mcpt_joint(prices, best_cfg, train_size=756, test_size=252, step_size=252, n_permutations=100, seed=24002)
    wf_returns_by_window = walk_forward_window_returns(best_returns, train_size=756, test_size=252, step_size=252)
    bootstrap_ci = bootstrap_mean_ci(best_returns.to_numpy(dtype=float), n_resamples=2000, seed=24003)
    vector_delta = abs(cagr(best_returns) - cagr(reference_returns_by_config[best_name]))
    best_metrics = metrics_by_config[best_name]

    econ_qqq_cagr = best_metrics["cagr"] > best_metrics["qqq_bh_cagr"]
    econ_qqq_terminal = best_metrics["terminal_wealth"] > best_metrics["qqq_bh_terminal_wealth"]
    econ_ew_cagr = best_metrics["cagr"] > best_metrics["qld_tlt_gld_ew_bh_cagr"]
    econ_ew_terminal = best_metrics["terminal_wealth"] > best_metrics["qld_tlt_gld_ew_bh_terminal_wealth"]
    econ_spy_cagr = best_metrics["cagr"] > best_metrics["spy_bh_cagr"]
    mdd_not_extreme = abs(best_metrics["max_drawdown"]) <= 1.5 * abs(best_metrics["qqq_bh_max_drawdown"])
    gates = {
        "economic_cagr_vs_qqq": econ_qqq_cagr,
        "economic_terminal_vs_qqq": econ_qqq_terminal,
        "economic_cagr_vs_qld_tlt_gld_ew": econ_ew_cagr,
        "economic_terminal_vs_qld_tlt_gld_ew": econ_ew_terminal,
        "economic_cagr_vs_spy_opportunity": econ_spy_cagr,
        "mdd_not_extreme_vs_primary": mdd_not_extreme,
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
    economic_pass = econ_qqq_cagr and econ_qqq_terminal and econ_ew_cagr and econ_ew_terminal and econ_spy_cagr
    validation_failed = not all(v for k, v in gates.items() if not k.startswith("economic_"))
    strict_winner = economic_pass and not validation_failed
    status = "strict_winner" if strict_winner else "economic_beater_not_validated" if economic_pass else "fail"

    kill_switches = []
    if not econ_qqq_cagr:
        kill_switches.append("CAGR <= QQQ buy-and-hold")
    if not econ_qqq_terminal:
        kill_switches.append("terminal wealth <= QQQ buy-and-hold")
    if not econ_ew_cagr:
        kill_switches.append("CAGR <= equal-weight QLD/TLT/GLD buy-and-hold")
    if not econ_ew_terminal:
        kill_switches.append("terminal wealth <= equal-weight QLD/TLT/GLD buy-and-hold")
    if not econ_spy_cagr:
        kill_switches.append("CAGR <= SPY opportunity buy-and-hold")
    if not mdd_not_extreme:
        kill_switches.append("MDD worse than 1.5x QQQ benchmark MDD")
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
            "best_gross_max": float(best_weights.abs().sum(axis=1).max()),
            "boost_days_fraction": float((best_weights["QLD"] > best_cfg.base_qld).mean()),
            "financing_rate_annual": FINANCING_RATE,
        },
        "benchmark": {
            "primary": ["QQQ_buy_hold", "equal_weight_QLD_TLT_GLD_buy_hold"],
            "opportunity": "SPY_buy_hold",
            "context": ["QLD_buy_hold", "TLT_buy_hold", "GLD_buy_hold", "SHV_buy_hold"],
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
        "notes": "Monthly QLD/TLT/GLD sleeve with drawdown-triggered QLD gross migration and 5% annual financing drag; research-only, no tax model.",
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
    asset_returns = prices[["QLD", "TLT", "GLD"]].pct_change().fillna(0.0)
    weights = migration_weights(asset_returns.index, asset_returns, cfg)
    gross = weights.abs().sum(axis=1)
    financing = (gross - 1.0).clip(lower=0.0) * FINANCING_RATE / TRADING_DAYS
    loop_returns = ((weights * asset_returns).sum(axis=1) - financing).rename(cfg.name)
    reference_returns = (reference_strategy_returns(asset_returns, weights) - financing).rename(cfg.name)
    return loop_returns.iloc[1:], reference_returns.iloc[1:], weights.iloc[1:]


def migration_weights(index: pd.Index, asset_returns: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    weights = pd.DataFrame(0.0, index=index, columns=["QLD", "TLT", "GLD"])
    equity = 1.0
    high_water = 1.0
    current = base_weights(cfg)
    month = None
    for i, date in enumerate(index):
        period = pd.Timestamp(date).to_period("M")
        if i == 0 or period != month:
            dd = equity / high_water - 1.0
            current = base_weights(cfg)
            if dd <= cfg.dd_trigger:
                current["QLD"] += cfg.qld_boost
            month = period
        weights.iloc[i] = [current["QLD"], current["TLT"], current["GLD"]]
        day_return = float((weights.iloc[i] * asset_returns.iloc[i]).sum())
        gross = float(weights.iloc[i].abs().sum())
        equity *= 1.0 + day_return - max(gross - 1.0, 0.0) * FINANCING_RATE / TRADING_DAYS
        high_water = max(high_water, equity)
    return weights


def base_weights(cfg: Config) -> dict[str, float]:
    return {"QLD": cfg.base_qld, "TLT": cfg.base_tlt, "GLD": cfg.base_gld}


def reference_strategy_returns(asset_returns: pd.DataFrame, weights: pd.DataFrame) -> pd.Series:
    arr = asset_returns.to_numpy(dtype=float)
    w = weights.to_numpy(dtype=float)
    out = np.empty(arr.shape[0], dtype=float)
    for i in range(arr.shape[0]):
        out[i] = float(np.dot(w[i], arr[i]))
    return pd.Series(out, index=asset_returns.index)


def aligned_benchmarks(index: pd.Index, prices: pd.DataFrame) -> dict[str, pd.Series]:
    returns = prices.pct_change().fillna(0.0).reindex(index).fillna(0.0)
    qld_tlt_gld_ew = (returns["QLD"] + returns["TLT"] + returns["GLD"]) / 3.0
    return {
        "qqq_bh": returns["QQQ"],
        "qld_tlt_gld_ew_bh": qld_tlt_gld_ew,
        "spy_bh": returns["SPY"],
        "qld_bh": returns["QLD"],
        "tlt_bh": returns["TLT"],
        "gld_bh": returns["GLD"],
        "shv_bh": returns["SHV"],
    }


def mcpt_joint(prices: pd.DataFrame, cfg: Config, *, n_permutations: int, seed: int) -> dict[str, object]:
    observed = annualized_sharpe(strategy_returns(prices, cfg)[0].to_numpy(dtype=float))
    rng = np.random.default_rng(seed)
    stats = np.empty(n_permutations, dtype=float)
    for i in range(n_permutations):
        stats[i] = annualized_sharpe(strategy_returns(permute_joint_return_rows(prices, rng), cfg)[0].to_numpy(dtype=float))
    return {"observed": observed, "p_value": float(np.sum(stats >= observed) / n_permutations), "n_permutations": n_permutations}


def walk_forward_mcpt_joint(prices: pd.DataFrame, cfg: Config, *, train_size: int, test_size: int, step_size: int, n_permutations: int, seed: int) -> dict[str, object]:
    observed_returns = walk_forward_strategy_returns(prices, cfg, train_size=train_size, test_size=test_size, step_size=step_size)
    observed = annualized_sharpe(observed_returns)
    rng = np.random.default_rng(seed)
    stats = np.empty(n_permutations, dtype=float)
    for i in range(n_permutations):
        stats[i] = annualized_sharpe(walk_forward_strategy_returns(permute_after_initial_train(prices, train_size, rng), cfg, train_size=train_size, test_size=test_size, step_size=step_size))
    return {"observed": observed, "p_value": float(np.sum(stats >= observed) / n_permutations), "n_permutations": n_permutations}


def walk_forward_strategy_returns(prices: pd.DataFrame, cfg: Config, *, train_size: int, test_size: int, step_size: int) -> np.ndarray:
    out: list[np.ndarray] = []
    start = 0
    while start + train_size + test_size <= len(prices):
        frame = prices.iloc[start : start + train_size + test_size]
        test_index = prices.index[start + train_size : start + train_size + test_size]
        out.append(strategy_returns(frame, cfg)[0].reindex(test_index).dropna().to_numpy(dtype=float))
        start += step_size
    return np.concatenate(out) if out else np.array([], dtype=float)


def permute_joint_return_rows(prices: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    returns = prices.pct_change().dropna().to_numpy(dtype=float)
    shuffled = returns[rng.permutation(np.arange(returns.shape[0]))]
    values = np.vstack([np.ones((1, prices.shape[1])), np.cumprod(1.0 + shuffled, axis=0)])
    return pd.DataFrame(values, index=prices.index, columns=prices.columns)


def permute_after_initial_train(prices: pd.DataFrame, initial_train_size: int, rng: np.random.Generator) -> pd.DataFrame:
    returns = prices.pct_change().dropna().to_numpy(dtype=float)
    prefix_prices = prices.iloc[:initial_train_size].to_numpy(dtype=float)
    tail_returns = returns[initial_train_size - 1 :]
    shuffled_tail = tail_returns[rng.permutation(np.arange(tail_returns.shape[0]))]
    tail_prices = prefix_prices[-1:] * np.cumprod(1.0 + shuffled_tail, axis=0)
    return pd.DataFrame(np.vstack([prefix_prices, tail_prices]), index=prices.index, columns=prices.columns)


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
        "exposure_time": float(np.mean(weights.abs().sum(axis=1).to_numpy(dtype=float) > 1e-12)),
        "annual_turnover": annual_turnover(weights),
        "gross_mean": float(weights.abs().sum(axis=1).mean()),
        "gross_max": float(weights.abs().sum(axis=1).max()),
    }
    for name, series in benchmarks.items():
        out[f"{name}_cagr"] = cagr(series)
        out[f"{name}_terminal_wealth"] = 1.0 + compound(series)
        out[f"{name}_sharpe"] = sharpe(series)
        out[f"{name}_max_drawdown"] = max_drawdown(series)
    return out


def annual_turnover(weights: pd.DataFrame) -> float:
    daily_turnover = weights.diff().abs().sum(axis=1).fillna(0.0) / 2.0
    years = len(weights) / TRADING_DAYS
    return float(daily_turnover.sum() / years) if years > 0 else 0.0


def walk_forward_window_returns(returns: pd.Series, train_size: int, test_size: int, step_size: int) -> list[float]:
    out = []
    start = 0
    while start + train_size + test_size <= len(returns):
        out.append(compound(returns.iloc[start + train_size : start + train_size + test_size]))
        start += step_size
    return out


def bootstrap_mean_ci(values: np.ndarray, n_resamples: int, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    values = np.asarray(values, dtype=float)
    means = np.empty(n_resamples, dtype=float)
    for i in range(n_resamples):
        means[i] = float(np.mean(rng.choice(values, size=values.size, replace=True)))
    return float(np.quantile(means, 0.0005)), float(np.quantile(means, 0.9995))


def cagr(returns: pd.Series) -> float:
    total = compound(returns)
    years = len(returns) / TRADING_DAYS
    return float((1.0 + total) ** (1.0 / years) - 1.0) if years > 0 and total > -1.0 else -1.0


def compound(returns: pd.Series | np.ndarray) -> float:
    return float(np.prod(1.0 + np.asarray(returns, dtype=float)) - 1.0)


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
    return float((equity / equity.cummax() - 1.0).min())


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
        "benchmark": {"primary": ["QQQ_buy_hold", "equal_weight_QLD_TLT_GLD_buy_hold"], "opportunity": "SPY_buy_hold", "context": ["QLD_buy_hold", "TLT_buy_hold", "GLD_buy_hold", "SHV_buy_hold"]},
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
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    return obj


if __name__ == "__main__":
    main()
