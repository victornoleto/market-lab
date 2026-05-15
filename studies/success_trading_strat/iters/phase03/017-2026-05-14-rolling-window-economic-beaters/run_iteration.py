"""Phase 3 iteration 017: rolling-window audit of economic beaters.

This is a stricter robustness audit, not a new strategy search. Rolling 3y/5y
economic windows test whether previously discovered leveraged and crash-rearmed
economic beaters keep beating their pre-registered buy-and-hold benchmarks across
investor holding periods `[testing_tuning, p.327-335]`. Leveraged ETF paths are
regime-dependent `[leverage_for_the_long_run, p.4-7]`, and prior MCPT/PBO/DSR
failures remain binding `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[5]
ITERATION = "017-2026-05-14-rolling-window-economic-beaters"
ITER_DIR = Path(__file__).resolve().parent
PHASE_DIR = ITER_DIR.parent
PRICE_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
TRADING_DAYS = 252
WINDOWS = {"rolling_3y": 756, "rolling_5y": 1260}
STEP = 63
REQUIRED_TICKERS = ["SPY", "QQQ", "UPRO", "SSO", "QLD", "TQQQ", "TLT", "TMF", "GLD", "SHV"]


@dataclass(frozen=True)
class Candidate:
    label: str
    source_dir: str
    config_name: str
    primary_single: str
    primary_equal_weight: tuple[str, ...]


CANDIDATES = [
    Candidate("010_upro_tlt_gld", "010-2026-05-14-levered-balanced-sleeve", "upro50_tlt25_gld25_quarterly", "SPY", ("UPRO", "TLT", "GLD")),
    Candidate("011_sso_tlt_gld", "011-2026-05-14-sso-balanced-sleeve-stress", "sso75_tlt15_gld10_quarterly", "SPY", ("SSO", "TLT", "GLD")),
    Candidate("012_upro_tmf_gld", "012-2026-05-14-hfea-levered-sleeve", "upro50_tmf30_gld20_quarterly", "SPY", ("UPRO", "TMF", "GLD")),
    Candidate("013_nasdaq_rearm", "013-2026-05-14-nasdaq-drawdown-rearm-booster", "qld_tqqq_dd25_recover_sma50_rv40", "QQQ", ("QQQ", "QLD", "TQQQ")),
    Candidate("014_upro_tlt_spread", "014-2026-05-14-upro-tlt-gross-spread", "upro125_tlt25_sma200", "SPY", ("UPRO", "TLT", "SHV")),
]


def main() -> None:
    audit = audit_data()
    missing = [item["ticker"] for item in audit["daily_files"] if not item["exists"]]
    if missing:
        write_blocked(audit, f"missing required daily parquet: {', '.join(missing)}")
        return

    prices = pd.concat({ticker: load_close(ticker) for ticker in REQUIRED_TICKERS}, axis=1).dropna(how="all")
    rows: list[dict[str, object]] = []
    summary: dict[str, dict[str, object]] = {}

    for candidate in CANDIDATES:
        returns = load_candidate_returns(candidate)
        benchmark_returns = build_benchmarks(prices, candidate).reindex(returns.index).dropna()
        aligned = pd.concat([returns.rename("strategy"), benchmark_returns], axis=1).dropna()
        candidate_rows = rolling_rows(candidate, aligned)
        rows.extend(candidate_rows)
        failures = [row for row in candidate_rows if not row["pass"]]
        summary[candidate.label] = {
            "config_name": candidate.config_name,
            "aligned_start": str(aligned.index.min().date()),
            "aligned_end": str(aligned.index.max().date()),
            "n_obs": int(len(aligned)),
            "total_windows": len(candidate_rows),
            "failed_windows": len(failures),
            "worst_excess_cagr": min(float(row["min_excess_cagr"]) for row in candidate_rows),
            "worst_excess_terminal_wealth": min(float(row["min_excess_terminal_wealth"]) for row in candidate_rows),
        }

    rolling = pd.DataFrame(rows)
    rolling.to_csv(ITER_DIR / "rolling_windows.csv", index=False)
    (ITER_DIR / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")

    failed_rows = rolling[~rolling["pass"]]
    status = "fail"
    kill_switches = []
    if not failed_rows.empty:
        kill_switches.append(f"rolling economic gate failed in {len(failed_rows)} candidate-window rows")
    kill_switches.append("prior strict validation failures remain binding")

    results = {
        "iteration": ITERATION,
        "status": status,
        "pre_registered": True,
        "n_trials": 0,
        "mcpt_reps": {},
        "best_config": None,
        "winner": False,
        "metrics": {
            "audit_type": "rolling_3y_5y_economic_stress",
            "window_lengths": WINDOWS,
            "step_observations": STEP,
            "candidate_summary": summary,
            "total_rows": int(len(rolling)),
            "failed_rows": int(len(failed_rows)),
            "pass_rows": int(rolling["pass"].sum()),
        },
        "benchmark": {
            "primary": "candidate_specific_dual_primary_buy_hold",
            "opportunity": "SPY_buy_hold_context",
            "details": {candidate.label: {"single": candidate.primary_single, "equal_weight": list(candidate.primary_equal_weight)} for candidate in CANDIDATES},
        },
        "gates": {
            "rolling_economic_cagr": bool((rolling["min_excess_cagr"] > 0).all()),
            "rolling_economic_terminal_wealth": bool((rolling["min_excess_terminal_wealth"] > 0).all()),
            "physical_daily_files": True,
            "prior_validation_failures_binding": True,
            "mcpt_recomputed": False,
            "pbo_recomputed": False,
            "dsr_recomputed": False,
        },
        "kill_switches": kill_switches,
        "artifacts": [
            str(ITER_DIR / "PRE_REG.md"),
            str(ITER_DIR / "run_iteration.py"),
            str(ITER_DIR / "RESULTS.json"),
            str(ITER_DIR / "audit.json"),
            str(ITER_DIR / "rolling_windows.csv"),
        ],
        "notes": "Rolling-window economic audit only; no new strategy trials and no deploy implication.",
    }
    (ITER_DIR / "RESULTS.json").write_text(json.dumps(to_jsonable(results), indent=2), encoding="utf-8")


def audit_data() -> dict[str, object]:
    daily_files = []
    for ticker in REQUIRED_TICKERS:
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
    df = pd.read_parquet(PRICE_DIR / f"{ticker}.parquet")
    column = "adj_close" if "adj_close" in df.columns else "close"
    return pd.to_numeric(df[column], errors="coerce").dropna().rename(ticker)


def load_candidate_returns(candidate: Candidate) -> pd.Series:
    path = PHASE_DIR / candidate.source_dir / "returns.csv"
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    if candidate.config_name not in df.columns:
        raise KeyError(f"{candidate.config_name} not found in {path}")
    return pd.to_numeric(df[candidate.config_name], errors="coerce").dropna()


def build_benchmarks(prices: pd.DataFrame, candidate: Candidate) -> pd.DataFrame:
    pct = prices.pct_change().fillna(0.0)
    return pd.DataFrame({
        f"{candidate.primary_single}_bh": pct[candidate.primary_single],
        "ew_bh": pct[list(candidate.primary_equal_weight)].mean(axis=1),
        "SPY_bh_context": pct["SPY"],
    })


def rolling_rows(candidate: Candidate, aligned: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for window_name, window_size in WINDOWS.items():
        if len(aligned) < window_size:
            continue
        for start in range(0, len(aligned) - window_size + 1, STEP):
            frame = aligned.iloc[start : start + window_size]
            strat_cagr = cagr(frame["strategy"])
            strat_tw = compound(frame["strategy"])
            benchmarks = [f"{candidate.primary_single}_bh", "ew_bh"]
            bench_cagrs = {name: cagr(frame[name]) for name in benchmarks}
            bench_tws = {name: compound(frame[name]) for name in benchmarks}
            min_excess_cagr = min(strat_cagr - value for value in bench_cagrs.values())
            min_excess_tw = min(strat_tw - value for value in bench_tws.values())
            rows.append({
                "candidate": candidate.label,
                "config_name": candidate.config_name,
                "window": window_name,
                "start": str(frame.index.min().date()),
                "end": str(frame.index.max().date()),
                "strategy_cagr": strat_cagr,
                "strategy_terminal_wealth": strat_tw,
                "primary_single_cagr": bench_cagrs[f"{candidate.primary_single}_bh"],
                "primary_single_terminal_wealth": bench_tws[f"{candidate.primary_single}_bh"],
                "equal_weight_cagr": bench_cagrs["ew_bh"],
                "equal_weight_terminal_wealth": bench_tws["ew_bh"],
                "min_excess_cagr": min_excess_cagr,
                "min_excess_terminal_wealth": min_excess_tw,
                "pass": min_excess_cagr > 0 and min_excess_tw > 0,
            })
    return rows


def cagr(returns: pd.Series) -> float:
    if returns.empty:
        return 0.0
    years = len(returns) / TRADING_DAYS
    if years <= 0:
        return 0.0
    return float((1.0 + returns).prod() ** (1.0 / years) - 1.0)


def compound(returns: pd.Series) -> float:
    return float((1.0 + returns).prod())


def missing_bday_rate(index: pd.DatetimeIndex) -> float:
    if len(index) < 2:
        return 0.0
    bdays = pd.bdate_range(index.min(), index.max())
    if len(bdays) == 0:
        return 0.0
    return float(1.0 - len(pd.DatetimeIndex(index).normalize().intersection(bdays)) / len(bdays))


def to_jsonable(value):
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_jsonable(v) for v in value]
    if isinstance(value, tuple):
        return [to_jsonable(v) for v in value]
    if hasattr(value, "item"):
        return value.item()
    return value


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
        "benchmark": {"primary": "candidate_specific_dual_primary_buy_hold", "opportunity": "SPY_buy_hold_context"},
        "gates": {"physical_daily_files": False},
        "kill_switches": [reason],
        "artifacts": [str(ITER_DIR / "PRE_REG.md"), str(ITER_DIR / "run_iteration.py"), str(ITER_DIR / "RESULTS.json"), str(ITER_DIR / "audit.json")],
        "notes": reason,
    }
    (ITER_DIR / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    (ITER_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
