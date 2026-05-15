"""Phase 3 iteration 027: QLD/TLT/GLD realized-volatility throttle sleeve.

The mechanism keeps a permanent LETF/diversifier sleeve and varies gross `QLD`
exposure from lagged `QQQ` realized volatility. This tests controlled leverage as
the return engine `[leverage_for_the_long_run, p.13]` with explicit financing and
volatility sizing `[systematic_trading, p.137-148]`. MCPT, PBO and DSR remain hard
anti-overfit controls `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`,
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


ITERATION = "027-2026-05-14-qld-vol-throttle-sleeve"
ITER_DIR = Path(__file__).resolve().parent
PRICE_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
TRADING_DAYS = 252
CUMULATIVE_TRIALS_AFTER = 312
AUDIT_TICKERS = ["QLD", "TLT", "GLD", "QQQ", "SPY", "SHV"]
REQUIRED = set(AUDIT_TICKERS)
FINANCING_RATE = 0.05


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


CONFIGS = [
    Config("qld60_tlt20_gld20_rv63_q30_70_b25_c10", 0.60, 0.20, 0.20, 0.25, 0.10, 63),
    Config("qld70_tlt15_gld15_rv63_q30_70_b25_c10", 0.70, 0.15, 0.15, 0.25, 0.10, 63),
    Config("qld60_tlt20_gld20_rv126_q30_70_b50_c20", 0.60, 0.20, 0.20, 0.50, 0.20, 126),
    Config("qld70_tlt15_gld15_rv126_q30_70_b50_c20", 0.70, 0.15, 0.15, 0.50, 0.20, 126),
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
    benchmarks_by_config: dict[str, dict[str, pd.Series]] = {}

    for cfg in CONFIGS:
        strat, reference, weights = strategy_returns(prices, cfg)
        returns_by_config[cfg.name] = strat
        reference_returns_by_config[cfg.name] = reference
        weights_by_config[cfg.name] = weights
        bmarks = aligned_benchmarks(strat.index, prices)
        benchmarks_by_config[cfg.name] = bmarks
        metrics_by_config[cfg.name] = compute_metrics(strat, weights, bmarks)

    best_name = max(metrics_by_config, key=lambda name: (metrics_by_config[name]["terminal_wealth"], metrics_by_config[name]["sharpe"]))
    best_cfg = next(cfg for cfg in CONFIGS if cfg.name == best_name)
    best_returns = returns_by_config[best_name]
    best_weights = weights_by_config[best_name]
    returns_matrix = pd.concat(returns_by_config, axis=1).dropna()

    pbo_result = pbo(returns_matrix.to_numpy(dtype=float), n_blocks=10)
    dsr_result = dsr(best_returns.to_numpy(dtype=float), n_trials=CUMULATIVE_TRIALS_AFTER)
    is_mcpt = mcpt_joint(prices, best_cfg, n_permutations=200, seed=27001)
    wf_mcpt = walk_forward_mcpt_joint(prices, best_cfg, train_size=756, test_size=252, step_size=252, n_permutations=100, seed=27002)
    wf_returns_by_window = walk_forward_window_returns(best_returns, train_size=756, test_size=252, step_size=252)
    bootstrap_ci = bootstrap_mean_ci(best_returns.to_numpy(dtype=float), n_resamples=2000, seed=27003)
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
            "low_vol_boost_days_fraction": float((best_weights["QLD"] > best_cfg.base_qld).mean()),
            "high_vol_cut_days_fraction": float((best_weights["QLD"] < best_cfg.base_qld).mean()),
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
        "notes": "Monthly QLD/TLT/GLD sleeve with QQQ realized-volatility gross throttle and 5% annual financing drag; research-only, no tax model.",
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
    weights = vol_throttle_weights(asset_returns.index, prices["QQQ"], cfg)
    gross = weights.abs().sum(axis=1)
    financing = (gross - 1.0).clip(lower=0.0) * FINANCING_RATE / TRADING_DAYS
    loop_returns = ((weights * asset_returns).sum(axis=1) - financing).rename(cfg.name)
    reference_returns = (reference_strategy_returns(asset_returns, weights) - financing).rename(cfg.name)
    return loop_returns.iloc[1:], reference_returns.iloc[1:], weights.iloc[1:]


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
        weights.iloc[i] = [current["QLD"], current["TLT"], current["GLD"]]
    return weights


def base_weights(cfg: Config) -> dict[str, float]:
    return {"QLD": cfg.base_qld, "TLT": cfg.base_tlt, "GLD": cfg.base_gld}


def reference_strategy_returns(asset_returns: pd.DataFrame, weights: pd.DataFrame) -> pd.Series:
    out = []
    for i in range(len(asset_returns)):
        row_return = 0.0
        for col in asset_returns.columns:
            row_return += float(weights.iloc[i][col]) * float(asset_returns.iloc[i][col])
        out.append(row_return)
    return pd.Series(out, index=asset_returns.index, name="reference")


def aligned_benchmarks(index: pd.Index, prices: pd.DataFrame) -> dict[str, pd.Series]:
    out = {}
    for ticker in ["QQQ", "SPY", "QLD", "TLT", "GLD", "SHV"]:
        out[ticker] = prices[ticker].reindex(index).pct_change().fillna(0.0).iloc[1:]
    ew_prices = prices[["QLD", "TLT", "GLD"]].reindex(index)
    ew_returns = ew_prices.pct_change().fillna(0.0).mean(axis=1).iloc[1:]
    out["QLD_TLT_GLD_EW"] = ew_returns
    return out


def compute_metrics(returns: pd.Series, weights: pd.DataFrame, benchmarks: dict[str, pd.Series]) -> dict[str, object]:
    aligned_returns = returns.dropna()
    out = {
        "start": str(aligned_returns.index.min().date()),
        "end": str(aligned_returns.index.max().date()),
        "n_obs": int(len(aligned_returns)),
        "cagr": cagr(aligned_returns),
        "sharpe": annualized_sharpe(aligned_returns),
        "sortino": sortino(aligned_returns),
        "calmar": cagr(aligned_returns) / abs(max_drawdown(aligned_returns)) if max_drawdown(aligned_returns) < 0 else float("inf"),
        "max_drawdown": max_drawdown(aligned_returns),
        "terminal_wealth": compound_wealth(aligned_returns),
        "exposure_time": float((weights.abs().sum(axis=1) > 0).mean()),
        "annual_turnover": annual_turnover(weights),
        "gross_mean": float(weights.abs().sum(axis=1).mean()),
        "gross_max": float(weights.abs().sum(axis=1).max()),
    }
    for name, bench in benchmarks.items():
        bench = bench.reindex(aligned_returns.index).fillna(0.0)
        key = name.lower()
        out[f"{key}_bh_cagr"] = cagr(bench)
        out[f"{key}_bh_terminal_wealth"] = compound_wealth(bench)
        out[f"{key}_bh_sharpe"] = annualized_sharpe(bench)
        out[f"{key}_bh_max_drawdown"] = max_drawdown(bench)
    return out


def mcpt_joint(prices: pd.DataFrame, cfg: Config, n_permutations: int, seed: int) -> dict[str, object]:
    observed = annualized_sharpe(strategy_returns(prices, cfg)[0])
    rng = np.random.default_rng(seed)
    null = []
    for _ in range(n_permutations):
        permuted = permute_prices_joint(prices, rng)
        null.append(annualized_sharpe(strategy_returns(permuted, cfg)[0]))
    p_value = (1 + sum(x >= observed for x in null)) / (n_permutations + 1)
    return {"observed_sharpe": observed, "p_value": p_value, "null_mean": float(np.mean(null))}


def walk_forward_mcpt_joint(prices: pd.DataFrame, cfg: Config, train_size: int, test_size: int, step_size: int, n_permutations: int, seed: int) -> dict[str, object]:
    observed = sum(walk_forward_window_returns(strategy_returns(prices, cfg)[0], train_size, test_size, step_size))
    rng = np.random.default_rng(seed)
    null = []
    for _ in range(n_permutations):
        permuted = permute_prices_joint(prices, rng)
        permuted_returns = strategy_returns(permuted, cfg)[0]
        null.append(sum(walk_forward_window_returns(permuted_returns, train_size, test_size, step_size)))
    p_value = (1 + sum(x >= observed for x in null)) / (n_permutations + 1)
    return {"observed_wf_total": observed, "p_value": p_value, "null_mean": float(np.mean(null))}


def permute_prices_joint(prices: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    out = pd.DataFrame(index=prices.index)
    for col in prices.columns:
        returns = prices[col].pct_change().dropna().to_numpy(dtype=float)
        permuted = rng.permutation(returns)
        path = prices[col].iloc[0] * np.cumprod(np.r_[1.0, 1.0 + permuted])
        out[col] = path
    return out


def walk_forward_window_returns(returns: pd.Series, train_size: int, test_size: int, step_size: int) -> list[float]:
    values = []
    start = 0
    while start + train_size + test_size <= len(returns):
        test = returns.iloc[start + train_size : start + train_size + test_size]
        values.append(compound(test))
        start += step_size
    return values


def bootstrap_mean_ci(values: np.ndarray, n_resamples: int, seed: int) -> list[float]:
    rng = np.random.default_rng(seed)
    means = []
    clean = values[np.isfinite(values)]
    for _ in range(n_resamples):
        sample = rng.choice(clean, size=len(clean), replace=True)
        means.append(float(np.mean(sample)))
    return [float(np.quantile(means, 0.0005)), float(np.quantile(means, 0.9995))]


def cagr(returns: pd.Series) -> float:
    wealth = compound_wealth(returns)
    years = len(returns) / TRADING_DAYS
    return float(wealth ** (1 / years) - 1) if years > 0 and wealth > 0 else float("nan")


def compound(returns: pd.Series) -> float:
    return float((1.0 + returns.dropna()).prod() - 1.0)


def compound_wealth(returns: pd.Series) -> float:
    return float((1.0 + returns.dropna()).prod())


def annualized_sharpe(returns: pd.Series) -> float:
    clean = returns.dropna()
    std = clean.std(ddof=1)
    if std == 0 or not np.isfinite(std):
        return 0.0
    return float(clean.mean() / std * np.sqrt(TRADING_DAYS))


def sortino(returns: pd.Series) -> float:
    clean = returns.dropna()
    downside = clean[clean < 0].std(ddof=1)
    if downside == 0 or not np.isfinite(downside):
        return 0.0
    return float(clean.mean() / downside * np.sqrt(TRADING_DAYS))


def max_drawdown(returns: pd.Series) -> float:
    equity = (1.0 + returns.dropna()).cumprod()
    drawdown = equity / equity.cummax() - 1.0
    return float(drawdown.min())


def annual_turnover(weights: pd.DataFrame) -> float:
    daily_turnover = weights.diff().abs().sum(axis=1).fillna(0.0)
    return float(daily_turnover.sum() / (len(weights) / TRADING_DAYS))


def missing_bday_rate(index: pd.DatetimeIndex) -> float:
    clean = pd.to_datetime(index).tz_localize(None).normalize()
    if len(clean) < 2:
        return 0.0
    expected = pd.bdate_range(clean.min(), clean.max())
    return float(1.0 - len(pd.Index(clean.unique()).intersection(expected)) / len(expected))


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
        "benchmark": {"primary": ["QQQ_buy_hold", "equal_weight_QLD_TLT_GLD_buy_hold"], "opportunity": "SPY_buy_hold"},
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
    if isinstance(obj, list | tuple):
        return [to_jsonable(v) for v in obj]
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, float) and not np.isfinite(obj):
        return None
    return obj


if __name__ == "__main__":
    main()
