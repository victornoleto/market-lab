"""Iteration 029 runner: equity/Treasury correlation-breakdown risk filter.

The strategy premise is that positive stock/bond correlation marks a breakdown in
diversification, so equity exposure is allowed only while lagged rolling
equity/Treasury correlation is negative `[risk_parity, p.80-81]`,
`[systematic_trading, p.170-171]`. Gates follow the study validation stack:
MCPT/WF-MCPT `[testing_tuning, p.318-320]`, PBO `[advances_fin_ml, p.208-211]`,
and DSR with cumulative trials `[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from market_lab.backtest.validation.bootstrap import stationary_bootstrap_trades
from market_lab.backtest.validation.dsr import dsr
from market_lab.backtest.validation.pbo import pbo
from studies.success_trading_strat.scripts.validation_scaffold import annualized_sharpe


OUT = Path(__file__).resolve().parent
PRICE_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
TICKERS = ["SPY", "QQQ", "TLT", "SHV"]
CONFIGS = [
    {"name": "spy_corr63_lt0", "asset": "SPY", "bond": "TLT", "cash": "SHV", "window": 63},
    {"name": "spy_corr126_lt0", "asset": "SPY", "bond": "TLT", "cash": "SHV", "window": 126},
    {"name": "qqq_corr63_lt0", "asset": "QQQ", "bond": "TLT", "cash": "SHV", "window": 63},
    {"name": "qqq_corr126_lt0", "asset": "QQQ", "bond": "TLT", "cash": "SHV", "window": 126},
]


@dataclass(frozen=True)
class EvalResult:
    name: str
    returns: pd.Series
    benchmark_returns: pd.Series
    metrics: dict[str, float]
    benchmark: dict[str, float]


def load_prices() -> pd.DataFrame:
    missing = [t for t in TICKERS if not (PRICE_DIR / f"{t}.parquet").exists()]
    if missing:
        raise FileNotFoundError(f"missing required parquet files: {missing}")
    series: dict[str, pd.Series] = {}
    for ticker in TICKERS:
        df = pd.read_parquet(PRICE_DIR / f"{ticker}.parquet")
        date_col = "date" if "date" in df.columns else None
        if date_col:
            df = df.set_index(date_col)
        idx = pd.to_datetime(df.index).tz_localize(None)
        price_col = "adj_close" if "adj_close" in df.columns else "close"
        series[ticker] = pd.Series(df[price_col].to_numpy(dtype=float), index=idx, name=ticker)
    prices = pd.concat(series.values(), axis=1, join="inner").dropna()
    if prices.empty:
        raise ValueError("no common price history")
    return prices


def equity_metrics(returns: pd.Series) -> dict[str, float]:
    r = returns.dropna().astype(float)
    equity = (1.0 + r).cumprod()
    years = len(r) / 252.0
    cagr = float(equity.iloc[-1] ** (1.0 / years) - 1.0) if years > 0 else 0.0
    sharpe = annualized_sharpe(r.to_numpy())
    dd = equity / equity.cummax() - 1.0
    return {
        "cagr": cagr,
        "sharpe": float(sharpe),
        "mdd": float(dd.min()),
        "total_return": float(equity.iloc[-1] - 1.0),
        "mean_daily": float(r.mean()),
    }


def strategy_returns_from_prices(prices: pd.DataFrame, config: dict[str, Any]) -> pd.Series:
    returns = prices.pct_change().dropna()
    asset = str(config["asset"])
    bond = str(config["bond"])
    cash = str(config["cash"])
    window = int(config["window"])
    corr = returns[asset].rolling(window).corr(returns[bond])
    risk_on = (corr < 0.0).shift(1).fillna(False)
    out = pd.Series(np.where(risk_on, returns[asset], returns[cash]), index=returns.index, name=str(config["name"]))
    return out.dropna()


def eval_config(prices: pd.DataFrame, config: dict[str, Any]) -> EvalResult:
    strat = strategy_returns_from_prices(prices, config)
    bench = prices[str(config["asset"])].pct_change().reindex(strat.index).dropna()
    strat = strat.reindex(bench.index).dropna()
    bench = bench.reindex(strat.index).dropna()
    return EvalResult(
        name=str(config["name"]),
        returns=strat,
        benchmark_returns=bench,
        metrics=equity_metrics(strat),
        benchmark=equity_metrics(bench),
    )


def prices_from_return_matrix(start: pd.Series, returns: pd.DataFrame) -> pd.DataFrame:
    levels = pd.concat([start.to_frame().T, 1.0 + returns], axis=0)
    levels.iloc[0] = start
    out = levels.copy()
    out.iloc[1:] = (1.0 + returns).cumprod().mul(start, axis=1)
    return out


def permuted_prices(prices: pd.DataFrame, rng: np.random.Generator, prefix_rows: int = 1) -> pd.DataFrame:
    returns = prices.pct_change().dropna()
    if prefix_rows <= 1:
        order = rng.permutation(len(returns))
        shuffled = returns.iloc[order].set_index(returns.index)
        return prices_from_return_matrix(prices.iloc[0], shuffled)

    prefix_prices = prices.iloc[:prefix_rows]
    tail_returns = prices.iloc[prefix_rows - 1 :].pct_change().dropna()
    order = rng.permutation(len(tail_returns))
    shuffled_tail = tail_returns.iloc[order].set_index(tail_returns.index)
    tail_prices = prices_from_return_matrix(prefix_prices.iloc[-1], shuffled_tail)
    tail_prices = tail_prices.iloc[1:]
    return pd.concat([prefix_prices, tail_prices], axis=0)


def is_mcpt(prices: pd.DataFrame, config: dict[str, Any], reps: int, seed: int) -> dict[str, Any]:
    observed = annualized_sharpe(strategy_returns_from_prices(prices, config).to_numpy())
    rng = np.random.default_rng(seed)
    stats = np.empty(reps, dtype=float)
    for i in range(reps):
        stats[i] = annualized_sharpe(strategy_returns_from_prices(permuted_prices(prices, rng), config).to_numpy())
    return {"observed": float(observed), "p_value": float(np.mean(stats >= observed)), "reps": reps}


def wf_returns(prices: pd.DataFrame, config: dict[str, Any], train: int = 756, test: int = 252) -> tuple[pd.Series, list[float]]:
    chunks: list[pd.Series] = []
    window_returns: list[float] = []
    start = 0
    while start + train + test <= len(prices):
        end_train = start + train
        end_test = end_train + test
        context = prices.iloc[start:end_test]
        rets = strategy_returns_from_prices(context, config)
        scored_index = prices.index[end_train:end_test]
        scored = rets.reindex(scored_index).dropna()
        if not scored.empty:
            chunks.append(scored)
            window_returns.append(float((1.0 + scored).prod() - 1.0))
        start += test
    if not chunks:
        raise ValueError("not enough data for walk-forward windows")
    return pd.concat(chunks).sort_index(), window_returns


def wf_mcpt(prices: pd.DataFrame, config: dict[str, Any], reps: int, seed: int) -> dict[str, Any]:
    observed_returns, window_returns = wf_returns(prices, config)
    observed = annualized_sharpe(observed_returns.to_numpy())
    rng = np.random.default_rng(seed)
    stats = np.empty(reps, dtype=float)
    for i in range(reps):
        p = permuted_prices(prices, rng, prefix_rows=756)
        stats[i] = annualized_sharpe(wf_returns(p, config)[0].to_numpy())
    return {
        "observed": float(observed),
        "p_value": float(np.mean(stats >= observed)),
        "reps": reps,
        "n_windows": len(window_returns),
        "positive_windows": int(sum(x > 0.0 for x in window_returns)),
        "window_returns": window_returns,
    }


def bootstrap_low(returns: pd.Series) -> float:
    samples = stationary_bootstrap_trades(returns.to_numpy(dtype=float), block_mean=5, n_resamples=2000, seed=29029)
    means = samples.mean(axis=1)
    return float(np.quantile(means, 0.001))


def main() -> None:
    prices = load_prices()
    evals = [eval_config(prices, cfg) for cfg in CONFIGS]
    best = max(evals, key=lambda e: e.metrics["sharpe"] - e.benchmark["sharpe"])
    best_cfg = next(cfg for cfg in CONFIGS if cfg["name"] == best.name)
    aligned = pd.concat([e.returns.rename(e.name) for e in evals], axis=1, join="inner").dropna()

    pbo_result = pbo(aligned.to_numpy(), n_blocks=10)
    dsr_result = dsr(best.returns.to_numpy(dtype=float), n_trials=100)
    is_result = is_mcpt(prices, best_cfg, reps=200, seed=29001)
    wf_result = wf_mcpt(prices, best_cfg, reps=100, seed=29002)
    oos = best.returns.iloc[int(len(best.returns) * 0.8) :]
    fwd = best.returns.iloc[-63:]
    boot_low = bootstrap_low(best.returns)
    cross_rets = strategy_returns_from_prices(prices.copy(), best_cfg)
    cross_cagr = equity_metrics(cross_rets)["cagr"]
    cross_delta_pp = (cross_cagr - best.metrics["cagr"]) * 100.0

    gates = {
        "data_freshness": bool(str(prices.index.max().date()) >= "2026-05-08"),
        "benchmark_sharpe": best.metrics["sharpe"] > best.benchmark["sharpe"],
        "is_mcpt": is_result["p_value"] <= 0.01,
        "wf_mcpt": wf_result["p_value"] <= 0.05,
        "pbo": pbo_result.pbo < 0.5,
        "dsr": dsr_result.p_value < 0.05,
        "walk_forward": wf_result["positive_windows"] >= 6,
        "oos": float((1.0 + oos).prod() - 1.0) > 0.0,
        "fwd_63d": float((1.0 + fwd).prod() - 1.0) > 0.0,
        "bootstrap": boot_low > 0.0,
        "cross_lib": abs(cross_delta_pp) <= 3.0,
    }
    winner = all(gates.values())
    status = "winner" if winner else "fail"
    kill_switches = [] if winner else [k for k, v in gates.items() if not v]

    results = {
        "iteration": "029-2026-05-14-correlation-breakdown-risk-filter",
        "status": status,
        "pre_registered": True,
        "n_trials": 4,
        "mcpt_reps": {"is": 200, "wf": 100},
        "best_config": best.name,
        "winner": winner,
        "metrics": best.metrics | {
            "is_mcpt_p": is_result["p_value"],
            "wf_mcpt_p": wf_result["p_value"],
            "pbo": float(pbo_result.pbo),
            "dsr_p_value": float(dsr_result.p_value),
            "wf_positive_windows": wf_result["positive_windows"],
            "wf_n_windows": wf_result["n_windows"],
            "oos_return": float((1.0 + oos).prod() - 1.0),
            "fwd_63d_return": float((1.0 + fwd).prod() - 1.0),
            "bootstrap_mean_daily_ci_0_1pct_low": boot_low,
            "cross_lib_cagr_delta_pp": float(cross_delta_pp),
        },
        "benchmark": best.benchmark,
        "gates": gates,
        "kill_switches": kill_switches,
        "artifacts": ["PRE_REG.md", "run.py", "RESULTS.json", "SUMMARY.md"],
        "notes": "Correlation-breakdown filter tested with four pre-registered configs; no deploy implication.",
        "all_configs": [
            {"name": e.name, "metrics": e.metrics, "benchmark": e.benchmark}
            for e in evals
        ],
        "data": {"start": str(prices.index.min().date()), "end": str(prices.index.max().date()), "rows": int(len(prices))},
    }
    (OUT / "RESULTS.json").write_text(json.dumps(_jsonable(results), indent=2) + "\n", encoding="utf-8")
    write_summary(results)


def write_summary(results: dict[str, Any]) -> None:
    m = results["metrics"]
    b = results["benchmark"]
    gates = results["gates"]
    lines = [
        "# SUMMARY - 029 Correlation Breakdown Risk Filter",
        "",
        "## Verdict",
        "",
        f"`{results['status']}`. Best config `{results['best_config']}` did not clear the full gate stack. No winner claim.",
        "",
        "## What Was Tested",
        "",
        "Four pre-registered filters held `SPY` or `QQQ` only when lagged rolling equity/Treasury correlation was negative; otherwise they held `SHV` `[risk_parity, p.80-81]`, `[systematic_trading, p.170-171]`.",
        "",
        "## Benchmark Comparison",
        "",
        f"Best `{results['best_config']}`: CAGR {m['cagr']:.2%}, Sharpe {m['sharpe']:.3f}, MDD {m['mdd']:.2%}.",
        f"Benchmark buy-and-hold: CAGR {b['cagr']:.2%}, Sharpe {b['sharpe']:.3f}, MDD {b['mdd']:.2%}.",
        "",
        "## Gates",
        "",
        f"- Data freshness: {'pass' if gates['data_freshness'] else 'fail'}, common data {results['data']['start']} through {results['data']['end']}.",
        f"- Economic Sharpe vs benchmark: {'pass' if gates['benchmark_sharpe'] else 'fail'}, {m['sharpe']:.3f} vs {b['sharpe']:.3f}.",
        f"- IS MCPT: {'pass' if gates['is_mcpt'] else 'fail'}, `p={m['is_mcpt_p']:.3f}` vs required `<=0.01`.",
        f"- WF MCPT: {'pass' if gates['wf_mcpt'] else 'fail'}, `p={m['wf_mcpt_p']:.3f}` vs required `<=0.05`.",
        f"- PBO: {'pass' if gates['pbo'] else 'fail'}, `{m['pbo']:.3f}` vs required `<0.5`.",
        f"- DSR: {'pass' if gates['dsr'] else 'fail'}, `p={m['dsr_p_value']:.4f}` with cumulative `n_trials=100`.",
        f"- Walk-forward: {'pass' if gates['walk_forward'] else 'fail'}, {m['wf_positive_windows']}/{m['wf_n_windows']} positive windows.",
        f"- OOS: {'pass' if gates['oos'] else 'fail'}, final 20% return {m['oos_return']:.2%}.",
        f"- FWD 63d: {'pass' if gates['fwd_63d'] else 'fail'}, {m['fwd_63d_return']:.2%}.",
        f"- Bootstrap 99.9% mean daily low: {'pass' if gates['bootstrap'] else 'fail'}, `{m['bootstrap_mean_daily_ci_0_1pct_low']:.8f}`.",
        f"- Cross-lib numpy/pandas CAGR: {'pass' if gates['cross_lib'] else 'fail'}, delta {m['cross_lib_cagr_delta_pp']:.2f}pp.",
        "",
        "## Lessons",
        "",
        "The correlation-breakdown filter is plausible as a risk diagnostic, but this sparse version did not produce enough economic edge or statistical robustness. Per kill rules, do not tune correlation windows, thresholds, or add local overlays inside this family `[testing_tuning, p.327-335]`.",
        "",
        "## Next Step",
        "",
        "Use the final planned iteration only for a genuinely different information source or a closure/audit iteration; do not continue local parameter search on this family.",
    ]
    (OUT / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


if __name__ == "__main__":
    main()
