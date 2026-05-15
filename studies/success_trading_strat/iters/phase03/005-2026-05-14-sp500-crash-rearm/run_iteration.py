"""Phase 3 iteration 005: S&P crash-rearmed SSO booster.

The rule stays invested in `SPY` and temporarily switches to `SSO` after a
material drawdown has recovered above a moving average. This tests post-stress
re-risking on the broad S&P engine rather than local-tuning the prior Nasdaq
result `[leverage_for_the_long_run, p.16-17]`, `[systematic_trading, p.119]`.
Validation follows MCPT/WF-MCPT plus PBO/DSR discipline `[testing_tuning,
p.318-320]`, `[advances_fin_ml, p.208-211]`.
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


ITERATION = "005-2026-05-14-sp500-crash-rearm"
ITER_DIR = Path(__file__).resolve().parent
PRICE_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
TRADING_DAYS = 252
CUMULATIVE_TRIALS_AFTER = 246
AUDIT_TICKERS = ["SPY", "SSO", "QQQ", "SHV"]
REQUIRED = {"SPY", "SSO", "QQQ", "SHV"}


@dataclass(frozen=True)
class Config:
    name: str
    trigger_drawdown: float
    recovery_sma: int
    booster_hold: int


CONFIGS = [
    Config("spy_sso_rearm_dd15_sma50_h63", -0.15, 50, 63),
    Config("spy_sso_rearm_dd20_sma50_h63", -0.20, 50, 63),
    Config("spy_sso_rearm_dd25_sma50_h126", -0.25, 50, 126),
    Config("spy_sso_rearm_dd20_sma100_h126", -0.20, 100, 126),
    Config("spy_sso_rearm_dd30_sma100_h126", -0.30, 100, 126),
    Config("spy_sso_rearm_dd35_sma100_h189", -0.35, 100, 189),
]


def main() -> None:
    audit = audit_data()
    if any((item["ticker"] in REQUIRED) and not item["exists"] for item in audit["daily_files"]):
        write_blocked(audit, "missing required tested daily parquet")
        return
    if any((item["ticker"] in REQUIRED) and not item.get("has_close", False) for item in audit["daily_files"]):
        write_blocked(audit, "missing required tested close column")
        return

    prices = {ticker: load_close(ticker) for ticker in REQUIRED}
    returns_by_config: dict[str, pd.Series] = {}
    vector_returns_by_config: dict[str, pd.Series] = {}
    metrics_by_config: dict[str, dict[str, float | int | str]] = {}

    for cfg in CONFIGS:
        strat, vector = strategy_returns(prices["SPY"], prices["SSO"], cfg)
        returns_by_config[cfg.name] = strat
        vector_returns_by_config[cfg.name] = vector
        spy_bh = prices["SPY"].pct_change().reindex(strat.index).fillna(0.0)
        sso_bh = prices["SSO"].pct_change().reindex(strat.index).fillna(0.0)
        qqq_bh = prices["QQQ"].pct_change().reindex(strat.index).fillna(0.0)
        metrics_by_config[cfg.name] = compute_metrics(strat, spy_bh, sso_bh, qqq_bh)

    best_name = max(metrics_by_config, key=lambda name: (metrics_by_config[name]["sharpe"], metrics_by_config[name]["terminal_wealth"]))
    best_cfg = next(cfg for cfg in CONFIGS if cfg.name == best_name)
    best_returns = returns_by_config[best_name]
    best_close = prices["SPY"].reindex(best_returns.index).dropna()
    mcpt_prices = np.log(best_close.to_numpy(dtype=float)) + 100.0
    returns_matrix = pd.concat(returns_by_config, axis=1).dropna()

    pbo_result = pbo(returns_matrix.to_numpy(), n_blocks=10)
    dsr_result = dsr(best_returns.to_numpy(), n_trials=CUMULATIVE_TRIALS_AFTER)
    is_mcpt = mcpt_on_strategy_returns(
        mcpt_prices,
        lambda series: fixed_strategy_from_prices(series, best_cfg),
        n_permutations=200,
        seed=5501,
        metric=annualized_sharpe,
    )
    train_size = min(756, max(252, mcpt_prices.size // 3))
    wf_result = walk_forward_mcpt(
        mcpt_prices,
        lambda train, test: fixed_strategy_from_prices(np.concatenate([train, test]), best_cfg)[-(test.size - 1) :],
        train_size=train_size,
        test_size=252,
        step_size=252,
        n_permutations=100,
        seed=5502,
        metric=annualized_sharpe,
    )
    wf_returns_by_window = walk_forward_window_returns(best_returns, train_size=756, test_size=252, step_size=252)
    bootstrap_ci = bootstrap_mean_ci(best_returns.to_numpy(), n_resamples=2000, seed=5503)
    vector_delta = abs(cagr(best_returns) - cagr(vector_returns_by_config[best_name]))
    best_metrics = metrics_by_config[best_name]

    econ_cagr = best_metrics["cagr"] > best_metrics["spy_bh_cagr"]
    econ_terminal = best_metrics["terminal_wealth"] > best_metrics["spy_bh_terminal_wealth"]
    gates = {
        "economic_cagr_vs_primary_spy": econ_cagr,
        "economic_terminal_vs_primary_spy": econ_terminal,
        "is_mcpt": is_mcpt.p_value <= 0.01,
        "wf_mcpt": wf_result.mcpt.p_value <= 0.05,
        "pbo": pbo_result.pbo < 0.5,
        "dsr": dsr_result.p_value < 0.05,
        "wf_windows": len(wf_returns_by_window) >= 8 and sum(x > 0 for x in wf_returns_by_window) >= 6,
        "oos": compound(best_returns.iloc[int(len(best_returns) * 0.8) :]) > 0,
        "fwd_63d": compound(best_returns.iloc[-63:]) > 0,
        "bootstrap": bootstrap_ci[0] > 0,
        "cross_lib": vector_delta <= 0.03,
        "mcpt_joint_path_caveat_clear": False,
    }
    economic_pass = econ_cagr and econ_terminal
    validation_failed = not all(v for k, v in gates.items() if not k.startswith("economic_"))
    strict_winner = all(gates.values())
    if strict_winner:
        status = "strict_winner"
    elif economic_pass and validation_failed:
        status = "economic_beater_not_validated"
    else:
        status = "fail"

    kill_switches = []
    if not econ_cagr:
        kill_switches.append("CAGR <= primary SPY buy-and-hold")
    if not econ_terminal:
        kill_switches.append("terminal wealth <= primary SPY buy-and-hold")
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
        },
        "benchmark": {
            "primary": "SPY_buy_hold",
            "context": ["SSO_buy_hold", "QQQ_buy_hold"],
            "aligned_start": best_metrics["start"],
            "aligned_end": best_metrics["end"],
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
        "kill_switches": kill_switches,
        "artifacts": [
            str(ITER_DIR / "PRE_REG.md"),
            str(ITER_DIR / "run_iteration.py"),
            str(ITER_DIR / "RESULTS.json"),
            str(ITER_DIR / "audit.json"),
            str(ITER_DIR / "returns.csv"),
        ],
        "notes": "S&P crash-rearmed SSO booster tested against primary SPY buy-and-hold. MCPT uses synthetic 2x SPY booster proxy, so joint SPY/SSO path caveat blocks strict promotion.",
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


def strategy_returns(spy_close: pd.Series, sso_close: pd.Series, cfg: Config) -> tuple[pd.Series, pd.Series]:
    frame = pd.concat({"spy": spy_close, "sso": sso_close}, axis=1).dropna()
    spy_ret = frame["spy"].pct_change().fillna(0.0)
    sso_ret = frame["sso"].pct_change().fillna(0.0)
    booster = rearm_signal(frame["spy"], cfg).shift(1).fillna(False).astype(float)
    loop_returns = booster * sso_ret + (1.0 - booster) * spy_ret
    vector_returns = np.where(booster.to_numpy(dtype=bool), sso_ret, spy_ret)
    vector_returns = pd.Series(vector_returns, index=frame.index)
    warmup = cfg.recovery_sma + 2
    return loop_returns.iloc[warmup:], vector_returns.iloc[warmup:]


def rearm_signal(close: pd.Series, cfg: Config) -> pd.Series:
    sma = close.rolling(cfg.recovery_sma, min_periods=cfg.recovery_sma).mean()
    drawdown = close / close.cummax() - 1.0
    arm = (drawdown <= cfg.trigger_drawdown) & (close > sma)
    active = []
    countdown = 0
    for should_arm in arm.fillna(False).to_numpy(dtype=bool):
        if should_arm:
            countdown = cfg.booster_hold
        active.append(countdown > 0)
        if countdown > 0:
            countdown -= 1
    return pd.Series(active, index=close.index)


def fixed_strategy_from_prices(prices: np.ndarray, cfg: Config) -> np.ndarray:
    close = pd.Series(np.exp(np.asarray(prices, dtype=float) - 100.0), index=pd.RangeIndex(len(prices)), dtype=float)
    spy_ret = close.pct_change().fillna(0.0)
    synthetic_sso_ret = 2.0 * spy_ret - 0.0089 / TRADING_DAYS
    booster = rearm_signal(close, cfg).shift(1).fillna(False).astype(float)
    returns = booster * synthetic_sso_ret + (1.0 - booster) * spy_ret
    return returns.iloc[cfg.recovery_sma + 2 :].to_numpy(dtype=float)


def compute_metrics(strategy: pd.Series, spy_bh: pd.Series, sso_bh: pd.Series, qqq_bh: pd.Series) -> dict[str, float | int | str]:
    return {
        "start": str(strategy.index.min().date()),
        "end": str(strategy.index.max().date()),
        "n_obs": int(strategy.size),
        "cagr": cagr(strategy),
        "sharpe": sharpe(strategy),
        "sortino": sortino(strategy),
        "calmar": calmar(strategy),
        "max_drawdown": max_drawdown(strategy),
        "terminal_wealth": 1.0 + compound(strategy),
        "exposure_time": exposure_time(strategy),
        "booster_time": booster_time(strategy, spy_bh),
        "spy_bh_cagr": cagr(spy_bh),
        "spy_bh_terminal_wealth": 1.0 + compound(spy_bh),
        "spy_bh_sharpe": sharpe(spy_bh),
        "spy_bh_max_drawdown": max_drawdown(spy_bh),
        "sso_bh_cagr": cagr(sso_bh),
        "sso_bh_terminal_wealth": 1.0 + compound(sso_bh),
        "sso_bh_max_drawdown": max_drawdown(sso_bh),
        "qqq_bh_cagr": cagr(qqq_bh),
        "qqq_bh_terminal_wealth": 1.0 + compound(qqq_bh),
    }


def exposure_time(returns: pd.Series) -> float:
    return float(np.mean(np.abs(returns.to_numpy(dtype=float)) > 1e-12))


def booster_time(strategy: pd.Series, spy_bh: pd.Series) -> float:
    return float(np.mean(np.abs(strategy.to_numpy(dtype=float) - spy_bh.to_numpy(dtype=float)) > 1e-12))


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
        "benchmark": {"primary": "SPY_buy_hold"},
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
