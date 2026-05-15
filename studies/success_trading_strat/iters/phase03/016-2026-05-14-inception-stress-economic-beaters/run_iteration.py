"""Phase 3 iteration 016: inception stress for prior economic beaters.

This is a consolidation stress, not a new strategy search. It checks whether
previous Phase 3 economic beaters remain buy-and-hold beaters under later
inception dates without changing their rules `[testing_tuning, p.327-335]`.
Leveraged sleeves are path dependent, so start-date sensitivity is a necessary
stress before treating a prior beater as robust `[leverage_for_the_long_run,
p.13]`, `[leverage_space, p.149-167]`. Prior MCPT/PBO/DSR failures remain binding
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

ITERATION = "016-2026-05-14-inception-stress-economic-beaters"
ITER_DIR = Path(__file__).resolve().parent
PRICE_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
TRADING_DAYS = 252


@dataclass(frozen=True)
class StressConfig:
    label: str
    source_dir: str
    column: str
    same_market: str
    equal_weight: tuple[str, ...]


CONFIGS = [
    StressConfig(
        "010_upro50_tlt25_gld25_quarterly",
        "010-2026-05-14-levered-balanced-sleeve",
        "upro50_tlt25_gld25_quarterly",
        "SPY",
        ("UPRO", "TLT", "GLD"),
    ),
    StressConfig(
        "011_sso75_tlt15_gld10_quarterly",
        "011-2026-05-14-sso-balanced-sleeve-stress",
        "sso75_tlt15_gld10_quarterly",
        "SPY",
        ("SSO", "TLT", "GLD"),
    ),
    StressConfig(
        "012_upro50_tmf30_gld20_quarterly",
        "012-2026-05-14-hfea-levered-sleeve",
        "upro50_tmf30_gld20_quarterly",
        "SPY",
        ("UPRO", "TMF", "GLD"),
    ),
    StressConfig(
        "013_qld_tqqq_dd25_recover_sma50_rv40",
        "013-2026-05-14-nasdaq-drawdown-rearm-booster",
        "qld_tqqq_dd25_recover_sma50_rv40",
        "QQQ",
        ("QQQ", "QLD", "TQQQ"),
    ),
    StressConfig(
        "014_upro125_tlt25_sma200",
        "014-2026-05-14-upro-tlt-gross-spread",
        "upro125_tlt25_sma200",
        "SPY",
        ("UPRO", "TLT", "SHV"),
    ),
]

INCEPTION_STARTS = [None, "2010-01-01", "2015-01-01", "2020-01-01"]
REQUIRED_TICKERS = sorted({"SPY", "QQQ", "UPRO", "SSO", "QLD", "TQQQ", "TLT", "TMF", "GLD", "SHV"})


def main() -> None:
    audit = audit_data()
    missing = [item["ticker"] for item in audit["daily_files"] if not item["exists"]]
    if missing:
        write_results(status="data_blocked", audit=audit, rows=[], notes=f"missing required daily files: {missing}")
        return

    closes = {ticker: load_close(ticker) for ticker in REQUIRED_TICKERS}
    rows: list[dict[str, object]] = []
    all_window_passes = True

    for cfg in CONFIGS:
        strategy = load_strategy_returns(cfg)
        same_market = closes[cfg.same_market].pct_change().fillna(0.0).rename(f"{cfg.same_market}_bh")
        ew_returns = pd.concat([closes[ticker].pct_change().fillna(0.0) for ticker in cfg.equal_weight], axis=1, sort=False).mean(axis=1).rename("equal_weight_bh")
        spy = closes["SPY"].pct_change().fillna(0.0).rename("spy_opportunity_bh")
        aligned = pd.concat([strategy, same_market, ew_returns, spy], axis=1, sort=False).dropna()

        for start in INCEPTION_STARTS:
            window = aligned if start is None else aligned.loc[pd.Timestamp(start) :]
            window = window.dropna()
            if len(window) < TRADING_DAYS:
                row = stress_row(cfg, start, window, skipped=True)
            else:
                row = stress_row(cfg, start, window, skipped=False)
                all_window_passes = all_window_passes and bool(row["economic_pass"])
            rows.append(row)

    status = "economic_beater_not_validated" if all_window_passes else "fail"
    notes = (
        "All audited inception windows retained economic beater status, but prior MCPT/DSR failures remain binding."
        if all_window_passes
        else "At least one audited inception window failed the pre-registered CAGR/terminal-wealth economic gate."
    )
    write_results(status=status, audit=audit, rows=rows, notes=notes)


def audit_data() -> dict[str, object]:
    daily_files = []
    for ticker in REQUIRED_TICKERS:
        path = PRICE_DIR / f"{ticker}.parquet"
        item: dict[str, object] = {"ticker": ticker, "path": str(path), "exists": path.exists()}
        if path.exists():
            df = pd.read_parquet(path)
            idx = pd.to_datetime(df.index)
            item.update(
                {
                    "rows": int(len(df)),
                    "first": str(idx.min()),
                    "last": str(idx.max()),
                    "timezone": str(getattr(idx, "tz", None)),
                    "columns": list(df.columns),
                    "missing_bday_rate": missing_bday_rate(idx),
                    "has_close": "close" in df.columns or "adj_close" in df.columns,
                }
            )
        daily_files.append(item)
    return {"daily_files": daily_files}


def load_close(ticker: str) -> pd.Series:
    df = pd.read_parquet(PRICE_DIR / f"{ticker}.parquet")
    col = "adj_close" if "adj_close" in df.columns else "close"
    out = df[col].astype(float).copy()
    out.index = pd.to_datetime(out.index).tz_localize(None)
    return out.sort_index().rename(ticker)


def load_strategy_returns(cfg: StressConfig) -> pd.Series:
    path = ITER_DIR.parent / cfg.source_dir / "returns.csv"
    data = pd.read_csv(path, index_col=0, parse_dates=True)
    if cfg.column not in data.columns:
        raise KeyError(f"{cfg.column} not found in {path}")
    out = data[cfg.column].astype(float).copy()
    out.index = pd.to_datetime(out.index).tz_localize(None)
    return out.sort_index().rename("strategy")


def stress_row(cfg: StressConfig, start: str | None, window: pd.DataFrame, *, skipped: bool) -> dict[str, object]:
    row: dict[str, object] = {
        "label": cfg.label,
        "source_dir": cfg.source_dir,
        "config": cfg.column,
        "start_rule": "full" if start is None else start,
        "same_market_benchmark": cfg.same_market,
        "equal_weight_benchmark": "/".join(cfg.equal_weight),
        "observations": int(len(window)),
        "skipped": skipped,
    }
    if skipped:
        row.update({"economic_pass": False, "skip_reason": "fewer than 252 aligned observations"})
        return row

    strategy = window["strategy"]
    same_market = window[f"{cfg.same_market}_bh"]
    equal_weight = window["equal_weight_bh"]
    spy = window["spy_opportunity_bh"]
    metrics = {
        "strategy": metrics_for(strategy),
        "same_market_bh": metrics_for(same_market),
        "equal_weight_bh": metrics_for(equal_weight),
        "spy_bh": metrics_for(spy),
    }
    economic_pass = (
        metrics["strategy"]["cagr"] > metrics["same_market_bh"]["cagr"]
        and metrics["strategy"]["terminal_wealth"] > metrics["same_market_bh"]["terminal_wealth"]
        and metrics["strategy"]["cagr"] > metrics["equal_weight_bh"]["cagr"]
        and metrics["strategy"]["terminal_wealth"] > metrics["equal_weight_bh"]["terminal_wealth"]
    )
    row.update(
        {
            "start": str(window.index.min().date()),
            "end": str(window.index.max().date()),
            "metrics": metrics,
            "economic_pass": bool(economic_pass),
            "fails": economic_fail_reasons(metrics, cfg),
        }
    )
    return row


def metrics_for(returns: pd.Series) -> dict[str, float]:
    returns = returns.astype(float).dropna()
    terminal = float((1.0 + returns).prod())
    years = len(returns) / TRADING_DAYS
    cagr = terminal ** (1.0 / years) - 1.0 if years > 0 else float("nan")
    equity = (1.0 + returns).cumprod()
    drawdown = equity / equity.cummax() - 1.0
    vol = float(returns.std(ddof=1) * np.sqrt(TRADING_DAYS)) if len(returns) > 1 else float("nan")
    sharpe = float((returns.mean() / returns.std(ddof=1)) * np.sqrt(TRADING_DAYS)) if len(returns) > 1 and returns.std(ddof=1) > 0 else 0.0
    return {
        "cagr": float(cagr),
        "terminal_wealth": terminal,
        "max_drawdown": float(drawdown.min()),
        "annual_vol": vol,
        "sharpe": sharpe,
    }


def economic_fail_reasons(metrics: dict[str, dict[str, float]], cfg: StressConfig) -> list[str]:
    fails = []
    if metrics["strategy"]["cagr"] <= metrics["same_market_bh"]["cagr"]:
        fails.append(f"CAGR <= {cfg.same_market} buy-and-hold")
    if metrics["strategy"]["terminal_wealth"] <= metrics["same_market_bh"]["terminal_wealth"]:
        fails.append(f"terminal wealth <= {cfg.same_market} buy-and-hold")
    if metrics["strategy"]["cagr"] <= metrics["equal_weight_bh"]["cagr"]:
        fails.append("CAGR <= equal-weight opportunity buy-and-hold")
    if metrics["strategy"]["terminal_wealth"] <= metrics["equal_weight_bh"]["terminal_wealth"]:
        fails.append("terminal wealth <= equal-weight opportunity buy-and-hold")
    return fails


def missing_bday_rate(index: pd.DatetimeIndex) -> float:
    index = pd.DatetimeIndex(index).tz_localize(None).normalize()
    if len(index) < 2:
        return 0.0
    expected = pd.bdate_range(index.min(), index.max())
    return float(1.0 - len(index.intersection(expected)) / len(expected))


def write_results(*, status: str, audit: dict[str, object], rows: list[dict[str, object]], notes: str) -> None:
    table = pd.DataFrame(rows)
    if rows:
        table.to_csv(ITER_DIR / "inception_stress.csv", index=False)
    (ITER_DIR / "audit.json").write_text(json.dumps(to_jsonable(audit), indent=2), encoding="utf-8")
    failed_rows = [row for row in rows if not row.get("skipped") and not row.get("economic_pass")]
    results = {
        "iteration": ITERATION,
        "status": status,
        "pre_registered": True,
        "n_trials": 0,
        "mcpt_reps": {},
        "best_config": None,
        "winner": False,
        "metrics": {
            "stress_rows": rows,
            "tested_configs": [asdict(cfg) for cfg in CONFIGS],
            "inception_starts": ["full" if x is None else x for x in INCEPTION_STARTS],
            "failed_window_count": len(failed_rows),
        },
        "benchmark": {
            "primary": "per_config_same_market_and_equal_weight_opportunity_buy_hold",
            "opportunity": "SPY_buy_hold",
        },
        "gates": {
            "economic_inception_stress": status != "fail" and status != "data_blocked",
            "mcpt_recomputed": False,
            "pbo_recomputed": False,
            "dsr_recomputed": False,
            "prior_validation_failures_binding": True,
        },
        "kill_switches": ["one or more inception windows failed economic B&H gates"] if status == "fail" else [],
        "artifacts": [
            str(ITER_DIR / "PRE_REG.md"),
            str(ITER_DIR / "run_iteration.py"),
            str(ITER_DIR / "RESULTS.json"),
            str(ITER_DIR / "audit.json"),
            str(ITER_DIR / "inception_stress.csv"),
        ],
        "notes": notes,
    }
    (ITER_DIR / "RESULTS.json").write_text(json.dumps(to_jsonable(results), indent=2), encoding="utf-8")


def to_jsonable(value):
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_jsonable(v) for v in value]
    if isinstance(value, tuple):
        return [to_jsonable(v) for v in value]
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    return value


if __name__ == "__main__":
    main()
