"""Phase 3 iteration 020: dynamic risk-parity LETF sleeve.

The strategy allocates monthly across a levered equity ETF, Treasuries and gold
using lagged inverse realized volatility. The mechanism is controlled leverage
plus risk budgeting, not a defensive long/flat timing filter
`[leverage_for_the_long_run, p.13]`, `[risk_parity, p.80-81]`,
`[systematic_trading, p.137-148]`. Validation keeps MCPT, PBO and DSR as hard
anti-overfit controls `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import importlib.util
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


ITERATION = "020-2026-05-14-dynamic-risk-parity-letf"
ITER_DIR = Path(__file__).resolve().parent
PRICE_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
TRADING_DAYS = 252
CUMULATIVE_TRIALS_AFTER = 296
AUDIT_TICKERS = ["SPY", "UPRO", "SSO", "TLT", "GLD", "SHV"]
REQUIRED = set(AUDIT_TICKERS)
FINANCING_ANNUAL = 0.05


@dataclass(frozen=True)
class Config:
    name: str
    universe: tuple[str, str, str]
    lookback: int
    gross: float


CONFIGS = [
    Config("upro_rp63_g100", ("UPRO", "TLT", "GLD"), 63, 1.00),
    Config("upro_rp126_g125", ("UPRO", "TLT", "GLD"), 126, 1.25),
    Config("sso_rp63_g100", ("SSO", "TLT", "GLD"), 63, 1.00),
    Config("sso_rp126_g125", ("SSO", "TLT", "GLD"), 126, 1.25),
]


def main() -> None:
    helper = load_helper_module()
    helper.TRADING_DAYS = TRADING_DAYS

    audit = audit_data(helper)
    missing = [item["ticker"] for item in audit["daily_files"] if item["ticker"] in REQUIRED and not item["exists"]]
    if missing:
        write_blocked(helper, audit, f"missing required daily parquet: {missing}")
        return
    missing_close = [item["ticker"] for item in audit["daily_files"] if item["ticker"] in REQUIRED and not item.get("has_close", False)]
    if missing_close:
        write_blocked(helper, audit, f"missing close column: {missing_close}")
        return

    closes = {ticker: helper.load_close(ticker) for ticker in REQUIRED}
    all_prices = pd.concat({ticker: closes[ticker] for ticker in AUDIT_TICKERS}, axis=1).dropna()
    if len(all_prices) < 756 + 252:
        write_blocked(helper, audit, f"insufficient aligned observations: {len(all_prices)}")
        return

    returns_by_config: dict[str, pd.Series] = {}
    reference_returns_by_config: dict[str, pd.Series] = {}
    weights_by_config: dict[str, pd.DataFrame] = {}
    metrics_by_config: dict[str, dict[str, object]] = {}

    for cfg in CONFIGS:
        strat, reference, weights = strategy_returns(all_prices, cfg)
        returns_by_config[cfg.name] = strat
        reference_returns_by_config[cfg.name] = reference
        weights_by_config[cfg.name] = weights
        metrics_by_config[cfg.name] = helper.compute_metrics(
            strat,
            weights,
            benchmarks_for_config(all_prices, strat.index, cfg),
        )

    best_name = max(metrics_by_config, key=lambda name: (metrics_by_config[name]["terminal_wealth"], -abs(metrics_by_config[name]["max_drawdown"])))
    best_cfg = next(cfg for cfg in CONFIGS if cfg.name == best_name)
    best_returns = returns_by_config[best_name]
    best_weights = weights_by_config[best_name]
    returns_matrix = pd.concat(returns_by_config, axis=1).dropna()

    pbo_result = pbo(returns_matrix.to_numpy(dtype=float), n_blocks=10)
    dsr_result = dsr(best_returns.to_numpy(dtype=float), n_trials=CUMULATIVE_TRIALS_AFTER)
    is_mcpt = mcpt_joint(all_prices, best_cfg, n_permutations=200, seed=20001)
    wf_mcpt = walk_forward_mcpt_joint(all_prices, best_cfg, train_size=756, test_size=252, step_size=252, n_permutations=100, seed=20002)
    wf_returns_by_window = helper.walk_forward_window_returns(best_returns, train_size=756, test_size=252, step_size=252)
    bootstrap_ci = helper.bootstrap_mean_ci(best_returns.to_numpy(dtype=float), n_resamples=2000, seed=20003)
    vector_delta = abs(helper.cagr(best_returns) - helper.cagr(reference_returns_by_config[best_name]))
    best_metrics = metrics_by_config[best_name]

    econ_spy_cagr = best_metrics["cagr"] > best_metrics["spy_bh_cagr"]
    econ_spy_terminal = best_metrics["terminal_wealth"] > best_metrics["spy_bh_terminal_wealth"]
    econ_primary_cagr = best_metrics["cagr"] > best_metrics["ew_primary_bh_cagr"]
    econ_primary_terminal = best_metrics["terminal_wealth"] > best_metrics["ew_primary_bh_terminal_wealth"]
    mdd_limit = 1.5 * max(abs(best_metrics["spy_bh_max_drawdown"]), abs(best_metrics["ew_primary_bh_max_drawdown"]))
    mdd_not_extreme = abs(best_metrics["max_drawdown"]) <= mdd_limit
    gates = {
        "economic_cagr_vs_spy": econ_spy_cagr,
        "economic_terminal_vs_spy": econ_spy_terminal,
        "economic_cagr_vs_equal_weight_primary": econ_primary_cagr,
        "economic_terminal_vs_equal_weight_primary": econ_primary_terminal,
        "mdd_not_extreme_vs_primary": mdd_not_extreme,
        "is_mcpt": is_mcpt["p_value"] <= 0.01,
        "wf_mcpt": wf_mcpt["p_value"] <= 0.05,
        "pbo": pbo_result.pbo < 0.5,
        "dsr": dsr_result.p_value < 0.05,
        "wf_windows": len(wf_returns_by_window) >= 8 and sum(x > 0 for x in wf_returns_by_window) >= 6,
        "oos": helper.compound(best_returns.iloc[int(len(best_returns) * 0.8) :]) > 0,
        "fwd_63d": helper.compound(best_returns.iloc[-63:]) > 0,
        "bootstrap": bootstrap_ci[0] > 0,
        "cross_lib": vector_delta <= 0.03,
    }
    economic_pass = econ_spy_cagr and econ_spy_terminal and econ_primary_cagr and econ_primary_terminal
    validation_failed = not all(v for k, v in gates.items() if not k.startswith("economic_"))
    strict_winner = economic_pass and not validation_failed
    status = "strict_winner" if strict_winner else "economic_beater_not_validated" if economic_pass else "fail"

    kill_switches = []
    if not econ_spy_cagr:
        kill_switches.append("CAGR <= SPY buy-and-hold")
    if not econ_spy_terminal:
        kill_switches.append("terminal wealth <= SPY buy-and-hold")
    if not econ_primary_cagr:
        kill_switches.append("CAGR <= equal-weight primary universe buy-and-hold")
    if not econ_primary_terminal:
        kill_switches.append("terminal wealth <= equal-weight primary universe buy-and-hold")
    if not mdd_not_extreme:
        kill_switches.append("MDD worse than 1.5x primary benchmark MDD")
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
            "financing_annual": FINANCING_ANNUAL,
        },
        "benchmark": {
            "primary": f"dual_SPY_and_equal_weight_{'_'.join(best_cfg.universe)}_buy_hold",
            "opportunity": "SPY_buy_hold",
            "context": [f"{ticker}_buy_hold" for ticker in [*best_cfg.universe, "SHV"]],
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
            "oos_total_return": helper.compound(best_returns.iloc[int(len(best_returns) * 0.8) :]),
            "fwd_63d_total_return": helper.compound(best_returns.iloc[-63:]),
        },
        "kill_switches": kill_switches,
        "artifacts": [
            str(ITER_DIR / "PRE_REG.md"),
            str(ITER_DIR / "run_iteration.py"),
            str(ITER_DIR / "RESULTS.json"),
            str(ITER_DIR / "audit.json"),
            str(ITER_DIR / "returns.csv"),
        ],
        "notes": "Dynamic inverse-vol risk-parity LETF sleeve with monthly rebalance and 5% annual financing drag above gross 1.0; research-only, no tax model.",
    }

    returns_matrix.to_csv(ITER_DIR / "returns.csv")
    (ITER_DIR / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    (ITER_DIR / "RESULTS.json").write_text(json.dumps(helper.to_jsonable(results), indent=2), encoding="utf-8")


def load_helper_module():
    path = ITER_DIR.parent / "011-2026-05-14-sso-balanced-sleeve-stress" / "run_iteration.py"
    spec = importlib.util.spec_from_file_location("phase03_iter011_helpers", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load helper module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def audit_data(helper) -> dict[str, object]:
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
                "missing_bday_rate": helper.missing_bday_rate(idx),
                "has_close": "close" in df.columns or "adj_close" in df.columns,
            })
        daily_files.append(item)
    return {"daily_files": daily_files}


def strategy_returns(prices: pd.DataFrame, cfg: Config) -> tuple[pd.Series, pd.Series, pd.DataFrame]:
    asset_returns = prices[list(cfg.universe)].pct_change().fillna(0.0)
    weights = signal_weights(prices, cfg)
    applied = weights.shift(1).fillna(0.0)
    gross = applied.abs().sum(axis=1)
    financing_drag = (gross - 1.0).clip(lower=0.0) * (FINANCING_ANNUAL / TRADING_DAYS)
    loop_returns = ((applied * asset_returns).sum(axis=1) - financing_drag).rename(cfg.name)
    reference_returns = reference_strategy_returns(asset_returns, applied, financing_drag).rename(cfg.name)
    valid = gross > 0.0
    return loop_returns.loc[valid].iloc[1:], reference_returns.loc[valid].iloc[1:], applied.loc[valid].iloc[1:]


def signal_weights(prices: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    universe = list(cfg.universe)
    asset_returns = prices[universe].pct_change()
    realized_vol = asset_returns.rolling(cfg.lookback, min_periods=cfg.lookback).std().shift(1) * np.sqrt(TRADING_DAYS)
    inverse_vol = 1.0 / realized_vol.replace(0.0, np.nan)
    raw_weights = inverse_vol.div(inverse_vol.sum(axis=1), axis=0).fillna(0.0) * cfg.gross
    month_key = pd.Series(prices.index.to_period("M"), index=prices.index)
    is_rebalance = month_key.ne(month_key.shift(1))
    weights = pd.DataFrame(0.0, index=prices.index, columns=universe)
    current = pd.Series(0.0, index=universe)
    for date in prices.index:
        if bool(is_rebalance.loc[date]) and raw_weights.loc[date].sum() > 0.0:
            current = raw_weights.loc[date].copy()
        weights.loc[date] = current
    return weights.fillna(0.0)


def reference_strategy_returns(asset_returns: pd.DataFrame, weights: pd.DataFrame, financing_drag: pd.Series) -> pd.Series:
    arr = asset_returns.to_numpy(dtype=float)
    w = weights.to_numpy(dtype=float)
    drag = financing_drag.to_numpy(dtype=float)
    out = np.empty(arr.shape[0], dtype=float)
    for i in range(arr.shape[0]):
        out[i] = float(np.dot(w[i], arr[i]) - drag[i])
    return pd.Series(out, index=asset_returns.index)


def benchmarks_for_config(prices: pd.DataFrame, index: pd.Index, cfg: Config) -> dict[str, pd.Series]:
    asset_returns = prices[list(cfg.universe)].pct_change().fillna(0.0).reindex(index).fillna(0.0)
    spy = prices["SPY"].pct_change().fillna(0.0).reindex(index).fillna(0.0)
    shv = prices["SHV"].pct_change().fillna(0.0).reindex(index).fillna(0.0)
    out = {f"{ticker}_bh": asset_returns[ticker] for ticker in cfg.universe}
    out["ew_primary_bh"] = asset_returns.mean(axis=1)
    out["spy_bh"] = spy
    out["shv_bh"] = shv
    return out


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
    if initial_train_size < 2 or initial_train_size >= len(prices) - 1:
        raise ValueError("initial_train_size must leave a non-empty permuted tail")
    returns = prices.pct_change().dropna().to_numpy(dtype=float)
    prefix_prices = prices.iloc[:initial_train_size].to_numpy(dtype=float)
    tail_returns = returns[initial_train_size - 1 :]
    shuffled_tail = tail_returns[rng.permutation(np.arange(tail_returns.shape[0]))]
    tail_prices = prefix_prices[-1:] * np.cumprod(1.0 + shuffled_tail, axis=0)
    return pd.DataFrame(np.vstack([prefix_prices, tail_prices]), index=prices.index, columns=prices.columns)


def write_blocked(helper, audit: dict[str, object], reason: str) -> None:
    results = {
        "iteration": ITERATION,
        "status": "data_blocked",
        "pre_registered": True,
        "n_trials": 0,
        "mcpt_reps": {},
        "best_config": None,
        "winner": False,
        "metrics": {},
        "benchmark": {"primary": "dual_SPY_and_equal_weight_LETF_TLT_GLD_buy_hold", "opportunity": "SPY_buy_hold"},
        "gates": {},
        "kill_switches": [reason],
        "artifacts": [str(ITER_DIR / "PRE_REG.md"), str(ITER_DIR / "run_iteration.py"), str(ITER_DIR / "RESULTS.json"), str(ITER_DIR / "audit.json")],
        "notes": reason,
    }
    (ITER_DIR / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    (ITER_DIR / "RESULTS.json").write_text(json.dumps(helper.to_jsonable(results), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
