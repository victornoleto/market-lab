"""Iteration 003: pre-registered SMA + momentum regime family.

All strategy/indicator/gate choices are fixed in PRE_REG.md before execution.
The rule is deliberately small: price above SMA and positive 63-day momentum
selects equity exposure; otherwise defensive SHV/cash. SMA follows the LRS
regime-filter literature `[leverage_for_the_long_run, p.13, p.16]`; momentum
uses a quarterly lookback as a parsimonious trend signal
`[stocks_on_the_move, p.76-77]`. MCPT/WF-MCPT are additional overfit guards
`[testing_tuning, p.318-320]` and do not replace PBO/DSR
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from market_lab.backtest.data.tiingo_storage import TiingoStorage
from market_lab.backtest.validation.dsr import dsr
from market_lab.backtest.validation.pbo import pbo
from studies.success_trading_strat.scripts.validation_scaffold import (
    annualized_sharpe,
    mcpt_on_strategy_returns,
    price_returns,
    walk_forward_mcpt,
)


OUT_DIR = Path(__file__).resolve().parent
START_DATE = "2008-01-01"
PERIODS_PER_YEAR = 252
N_TRIALS = 4
MCPT_REPS = 200
BOOTSTRAP_REPS = 5000


@dataclass(frozen=True)
class Config:
    name: str
    risk_asset: str
    sma_days: int
    momentum_days: int = 63


CONFIGS = [
    Config("spy_sma100_mom63", "SPY", 100),
    Config("spy_sma200_mom63", "SPY", 200),
    Config("qqq_sma100_mom63", "QQQ", 100),
    Config("qqq_sma200_mom63", "QQQ", 200),
]


def load_prices() -> pd.DataFrame:
    storage = TiingoStorage(ROOT / "data/tiingo")
    series = {}
    for ticker in ["SPY", "QQQ", "SHV"]:
        df = storage.read(ticker, frequency="daily")
        col = "adj_close" if "adj_close" in df.columns else "close"
        series[ticker] = df[col].rename(ticker)
    prices = pd.concat(series.values(), axis=1).sort_index()
    prices = prices.loc[prices.index >= pd.Timestamp(START_DATE)]
    return prices.dropna(subset=["SPY", "QQQ"])


def strategy_returns_for_config(prices: pd.DataFrame, cfg: Config) -> pd.Series:
    risk = prices[cfg.risk_asset].dropna()
    defensive = prices["SHV"].reindex(risk.index).ffill()
    risk_ret = risk.pct_change()
    defensive_ret = defensive.pct_change().fillna(0.0)
    sma = risk.rolling(cfg.sma_days).mean()
    momentum = risk / risk.shift(cfg.momentum_days) - 1.0
    signal = ((risk > sma) & (momentum > 0.0)).shift(1).fillna(False)
    returns = risk_ret.where(signal, defensive_ret).dropna()
    returns.name = cfg.name
    return returns


def fixed_rule_returns_from_prices(path: np.ndarray, sma_days: int, momentum_days: int) -> np.ndarray:
    # MCPT receives log-price paths so Masters-style additive permutations cannot
    # create negative nominal prices. Convert back before applying the rule.
    prices = pd.Series(np.exp(path))
    risk_ret = prices.pct_change()
    sma = prices.rolling(sma_days).mean()
    momentum = prices / prices.shift(momentum_days) - 1.0
    signal = ((prices > sma) & (momentum > 0.0)).shift(1).fillna(False)
    # MCPT uses cash at 0% while permuting the risk asset. This is conservative
    # versus SHV carry and keeps the null test single-series and reproducible.
    return risk_ret.where(signal, 0.0).dropna().to_numpy(dtype=float)


def metrics(returns: pd.Series) -> dict[str, float]:
    r = returns.dropna()
    equity = (1.0 + r).cumprod()
    years = len(r) / PERIODS_PER_YEAR
    cagr = float(equity.iloc[-1] ** (1.0 / years) - 1.0) if years > 0 else 0.0
    dd = equity / equity.cummax() - 1.0
    return {
        "cagr": cagr,
        "sharpe": float(annualized_sharpe(r.to_numpy(dtype=float))),
        "mdd": float(dd.min()),
        "terminal": float(equity.iloc[-1]),
        "mean_daily": float(r.mean()),
        "n_days": int(len(r)),
    }


def bootstrap_ci_low(returns: pd.Series, seed: int = 45) -> float:
    r = returns.dropna().to_numpy(dtype=float)
    rng = np.random.default_rng(seed)
    means = np.empty(BOOTSTRAP_REPS, dtype=float)
    for i in range(BOOTSTRAP_REPS):
        means[i] = float(rng.choice(r, size=r.size, replace=True).mean())
    return float(np.quantile(means, 0.001))


def positive_wf_windows(returns: pd.Series, window: int = 252) -> tuple[int, int]:
    chunks = [returns.iloc[i : i + window] for i in range(0, len(returns), window)]
    full_chunks = [c for c in chunks if len(c) >= window]
    positives = sum(float((1.0 + c).prod() - 1.0) > 0.0 for c in full_chunks)
    return positives, len(full_chunks)


def main() -> None:
    prices = load_prices()
    returns_by_config = {cfg.name: strategy_returns_for_config(prices, cfg) for cfg in CONFIGS}
    common_index = returns_by_config[CONFIGS[0].name].index
    for series in returns_by_config.values():
        common_index = common_index.intersection(series.index)
    aligned = pd.DataFrame({name: s.reindex(common_index) for name, s in returns_by_config.items()}).dropna()

    rows = []
    benchmark = {}
    for cfg in CONFIGS:
        r = aligned[cfg.name]
        risk_ret = prices[cfg.risk_asset].pct_change().reindex(aligned.index).dropna()
        rows.append({"config": cfg.name, **asdict(cfg), **metrics(r)})
        benchmark[cfg.name] = {"risk_asset": cfg.risk_asset, **metrics(risk_ret)}

    table = pd.DataFrame(rows).sort_values("sharpe", ascending=False)
    best_name = str(table.iloc[0]["config"])
    best_cfg = next(cfg for cfg in CONFIGS if cfg.name == best_name)
    best_returns = aligned[best_name]
    best_prices = prices[best_cfg.risk_asset].reindex(aligned.index).dropna()
    best_log_prices = np.log(best_prices.to_numpy(dtype=float))

    pbo_result = pbo(aligned.to_numpy(dtype=float), n_blocks=8)
    dsr_result = dsr(best_returns.to_numpy(dtype=float), n_trials=N_TRIALS)
    is_mcpt = mcpt_on_strategy_returns(
        best_log_prices,
        lambda path: fixed_rule_returns_from_prices(path, best_cfg.sma_days, best_cfg.momentum_days),
        n_permutations=MCPT_REPS,
        seed=3003,
    )
    wf_mcpt = walk_forward_mcpt(
        best_log_prices,
        lambda _train, test: fixed_rule_returns_from_prices(test, best_cfg.sma_days, best_cfg.momentum_days),
        train_size=252 * 4,
        test_size=252,
        step_size=252,
        n_permutations=MCPT_REPS,
        seed=3004,
    )

    wf_positive, wf_total = positive_wf_windows(best_returns)
    oos = best_returns.iloc[int(len(best_returns) * 0.8) :]
    fwd = best_returns.iloc[-63:]
    boot_low = bootstrap_ci_low(best_returns)
    best_benchmark = benchmark[best_name]

    gates = {
        "economic_beats_same_asset_bh_sharpe": bool(table.iloc[0]["sharpe"] > best_benchmark["sharpe"]),
        "is_mcpt_p_le_0_01": bool(is_mcpt.p_value <= 0.01),
        "wf_mcpt_p_le_0_05": bool(wf_mcpt.mcpt.p_value <= 0.05),
        "pbo_lt_0_5": bool(pbo_result.pbo < 0.5),
        "dsr_p_lt_0_05": bool(dsr_result.p_value < 0.05),
        "wf_6_of_8_positive": bool(wf_positive >= 6 and wf_total >= 8),
        "oos_positive": bool((1.0 + oos).prod() - 1.0 > 0.0),
        "fwd_positive": bool((1.0 + fwd).prod() - 1.0 > 0.0),
        "bootstrap_999_low_gt_0": bool(boot_low > 0.0),
        "cross_lib_computed": False,
    }
    hard_gate_pass = all(v for k, v in gates.items() if k != "cross_lib_computed") and gates["cross_lib_computed"]
    status = "winner" if hard_gate_pass else "fail"

    table.to_csv(OUT_DIR / "config_metrics.csv", index=False)
    aligned.to_csv(OUT_DIR / "returns_matrix.csv")

    results = {
        "iteration": "003-2026-05-14-sma-momentum-regime",
        "status": status,
        "pre_registered": True,
        "n_trials": N_TRIALS,
        "mcpt_reps": {"is": MCPT_REPS, "wf": MCPT_REPS},
        "best_config": best_name,
        "winner": False,
        "metrics": {
            "configs": rows,
            "best": metrics(best_returns),
            "pbo": float(pbo_result.pbo),
            "pbo_combinations": int(pbo_result.n_combinations),
            "dsr_p_value": float(dsr_result.p_value),
            "dsr_observed_sharpe_periodic": float(dsr_result.observed_sharpe),
            "dsr_benchmark_sharpe_periodic": float(dsr_result.benchmark_sharpe),
            "is_mcpt_p_value": float(is_mcpt.p_value),
            "wf_mcpt_p_value": float(wf_mcpt.mcpt.p_value),
            "wf_positive_windows": int(wf_positive),
            "wf_total_windows": int(wf_total),
            "oos_return": float((1.0 + oos).prod() - 1.0),
            "fwd_63d_return": float((1.0 + fwd).prod() - 1.0),
            "bootstrap_999_mean_daily_low": boot_low,
        },
        "benchmark": benchmark,
        "gates": gates,
        "kill_switches": [k for k, v in gates.items() if not v],
        "artifacts": ["PRE_REG.md", "run_iter.py", "config_metrics.csv", "returns_matrix.csv", "RESULTS.json"],
        "notes": "Cross-lib not computed; MCPT uses cash at 0% on permuted risk path, so no promotion is possible.",
    }
    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
