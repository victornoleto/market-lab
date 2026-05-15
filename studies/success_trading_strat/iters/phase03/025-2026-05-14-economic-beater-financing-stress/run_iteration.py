"""Phase 3 iteration 025: financing/friction stress for economic beaters.

This audit applies conservative strategy-only annual drag to prior Phase 3
economic beaters. It is not a new strategy search and consumes zero new trials.
Leveraged ETF implementation can lag theoretical returns
`[leverage_for_the_long_run, p.21]`, retail costs can dominate active systems
`[systematic_trading, p.185-188]`, and failed candidates should be stress-tested
or abandoned rather than locally tuned `[testing_tuning, p.327-335]`.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[5]
ITERATION = "025-2026-05-14-economic-beater-financing-stress"
ITER_DIR = Path(__file__).resolve().parent
PHASE_DIR = ITER_DIR.parent
PRICE_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
TRADING_DAYS = 252
STRESS_DRAGS = (0.0025, 0.0050, 0.0100)
REQUIRED_TICKERS = [
    "SPY",
    "QQQ",
    "QLD",
    "TQQQ",
    "SSO",
    "UPRO",
    "SMH",
    "SOXX",
    "XLK",
    "TECL",
    "TLT",
    "TMF",
    "GLD",
    "SHV",
    "VXX",
]


@dataclass(frozen=True)
class Candidate:
    label: str
    source_dir: str
    config_name: str
    primary_single: str | None = None
    primary_equal_weight: tuple[str, ...] = ()


CANDIDATES = [
    Candidate("001_qld_vt", "001-2026-05-14-nasdaq-letf-vol-target", "qld_vt35_rv21_dd25_half", "QQQ"),
    Candidate("002_upro_vt", "002-2026-05-14-sp500-letf-vol-target", "upro_vt40_rv63_dd30_half", "SPY"),
    Candidate("003_tecl_vt", "003-2026-05-14-semis-letf-vol-target", "tecl_vt40_rv63", "QQQ", ("SMH", "SOXX")),
    Candidate("004_nasdaq_rearm", "004-2026-05-14-nasdaq-crash-rearm", "qqq_qld_rearm_dd35_sma100_h189", "QQQ"),
    Candidate("005_sp500_rearm", "005-2026-05-14-sp500-crash-rearm", "spy_sso_rearm_dd35_sma100_h189", "SPY"),
    Candidate("006_high_beta_rotation", "006-2026-05-14-high-beta-relative-rotation", "top2_m63", None, ("QQQ", "SMH", "SOXX", "XLK")),
    Candidate("008_drawdown_adaptive", "008-2026-05-14-drawdown-adaptive-high-beta", "top2_m63_dd15_boost125_cap150", None, ("QQQ", "SMH", "SOXX", "XLK")),
    Candidate("010_upro_tlt_gld", "010-2026-05-14-levered-balanced-sleeve", "upro50_tlt25_gld25_quarterly", "SPY", ("UPRO", "TLT", "GLD")),
    Candidate("011_sso_tlt_gld", "011-2026-05-14-sso-balanced-sleeve-stress", "sso75_tlt15_gld10_quarterly", "SPY", ("SSO", "TLT", "GLD")),
    Candidate("012_upro_tmf_gld", "012-2026-05-14-hfea-levered-sleeve", "upro50_tmf30_gld20_quarterly", "SPY", ("UPRO", "TMF", "GLD")),
    Candidate("013_nasdaq_booster", "013-2026-05-14-nasdaq-drawdown-rearm-booster", "qld_tqqq_dd25_recover_sma50_rv40", "QQQ", ("QQQ", "QLD", "TQQQ")),
    Candidate("014_upro_tlt_spread", "014-2026-05-14-upro-tlt-gross-spread", "upro125_tlt25_sma200", "SPY", ("UPRO", "TLT", "SHV")),
    Candidate("018_vxx_rearm", "018-2026-05-14-vxx-crash-rearm", "qqq_tqqq_vxx95_norm70_h126", "QQQ"),
    Candidate("019_letf_gross_rotation", "019-2026-05-14-letf-light-gross-rotation", "top2_m126_g125", None, ("QLD", "SSO", "SMH", "SOXX")),
    Candidate("022_qqq_qld_overlay", "022-2026-05-14-qqq-core-qld-overlay", "mom126_vol63_cap25", "QQQ"),
    Candidate("024_qld_migration", "024-2026-05-14-qld-migration-sleeve", "qld70_tlt15_gld15_dd25_boost50", "QQQ", ("QLD", "TLT", "GLD")),
]


def main() -> None:
    audit = audit_data()
    missing = [item["ticker"] for item in audit["daily_files"] if not item["exists"]]
    if missing:
        write_blocked(audit, f"missing required daily parquet: {missing}")
        return

    prices = pd.concat({ticker: load_close(ticker) for ticker in REQUIRED_TICKERS}, axis=1).dropna(how="all")
    rows: list[dict[str, object]] = []
    candidate_summary: dict[str, dict[str, object]] = {}

    for candidate in CANDIDATES:
        source_returns = load_candidate_returns(candidate)
        benchmarks = build_benchmarks(prices, candidate).reindex(source_returns.index)
        aligned = pd.concat([source_returns.rename("strategy"), benchmarks], axis=1).dropna()
        if aligned.empty:
            raise ValueError(f"no aligned rows for {candidate.label}")
        candidate_rows = stress_rows(candidate, aligned)
        rows.extend(candidate_rows)
        failed = [row for row in candidate_rows if not row["pass"]]
        candidate_summary[candidate.label] = {
            "config_name": candidate.config_name,
            "aligned_start": str(aligned.index.min().date()),
            "aligned_end": str(aligned.index.max().date()),
            "n_obs": int(len(aligned)),
            "stress_rows": len(candidate_rows),
            "failed_rows": len(failed),
            "worst_min_excess_cagr": min(float(row["min_excess_cagr"]) for row in candidate_rows),
            "worst_min_excess_terminal_wealth": min(float(row["min_excess_terminal_wealth"]) for row in candidate_rows),
        }

    stress = pd.DataFrame(rows)
    failed_rows = stress[~stress["pass"]]
    stress.to_csv(ITER_DIR / "stress_results.csv", index=False)
    (ITER_DIR / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")

    kill_switches = ["prior strict validation failures remain binding"]
    status = "economic_beater_not_validated"
    if not failed_rows.empty:
        status = "fail"
        kill_switches.insert(0, f"stressed economic gate failed in {len(failed_rows)} candidate-stress rows")

    results = {
        "iteration": ITERATION,
        "status": status,
        "pre_registered": True,
        "n_trials": 0,
        "mcpt_reps": {},
        "best_config": None,
        "winner": False,
        "metrics": {
            "audit_type": "prior_economic_beater_financing_friction_stress",
            "annual_strategy_only_drags": list(STRESS_DRAGS),
            "candidate_summary": candidate_summary,
            "total_rows": int(len(stress)),
            "failed_rows": int(len(failed_rows)),
            "pass_rows": int(stress["pass"].sum()),
            "worst_rows": stress.sort_values(["min_excess_cagr", "min_excess_terminal_wealth"]).head(10).to_dict(orient="records"),
        },
        "benchmark": {
            "primary": "candidate_specific_phase3_primary_buy_hold",
            "opportunity": "SPY_buy_hold_context",
            "details": {
                candidate.label: {
                    "single": candidate.primary_single,
                    "equal_weight": list(candidate.primary_equal_weight),
                }
                for candidate in CANDIDATES
            },
        },
        "gates": {
            "physical_daily_files": True,
            "stressed_economic_cagr_all_rows": bool((stress["min_excess_cagr"] > 0).all()),
            "stressed_economic_terminal_wealth_all_rows": bool((stress["min_excess_terminal_wealth"] > 0).all()),
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
            str(ITER_DIR / "stress_results.csv"),
        ],
        "notes": "Conservative stress audit only; no new strategy trials and no deploy implication.",
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
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df = df[~df.index.duplicated()].sort_index()
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
    data: dict[str, pd.Series] = {"SPY_bh_context": pct["SPY"]}
    if candidate.primary_single is not None:
        data[f"{candidate.primary_single}_bh"] = pct[candidate.primary_single]
    if candidate.primary_equal_weight:
        data["ew_bh"] = pct[list(candidate.primary_equal_weight)].mean(axis=1)
    return pd.DataFrame(data)


def stress_rows(candidate: Candidate, aligned: pd.DataFrame) -> list[dict[str, object]]:
    benchmark_cols = []
    if candidate.primary_single is not None:
        benchmark_cols.append(f"{candidate.primary_single}_bh")
    if candidate.primary_equal_weight:
        benchmark_cols.append("ew_bh")
    rows = []
    for annual_drag in STRESS_DRAGS:
        stressed = aligned["strategy"] - annual_drag / TRADING_DAYS
        strat_cagr = cagr(stressed)
        strat_tw = compound(stressed)
        bench_cagrs = {name: cagr(aligned[name]) for name in benchmark_cols}
        bench_tws = {name: compound(aligned[name]) for name in benchmark_cols}
        min_excess_cagr = min(strat_cagr - value for value in bench_cagrs.values())
        min_excess_tw = min(strat_tw - value for value in bench_tws.values())
        rows.append({
            "candidate": candidate.label,
            "config_name": candidate.config_name,
            "annual_drag": annual_drag,
            "start": str(aligned.index.min().date()),
            "end": str(aligned.index.max().date()),
            "strategy_cagr_stressed": strat_cagr,
            "strategy_terminal_wealth_stressed": strat_tw,
            "benchmark_cagrs": bench_cagrs,
            "benchmark_terminal_wealth": bench_tws,
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
        "benchmark": {"primary": "candidate_specific_phase3_primary_buy_hold", "opportunity": "SPY_buy_hold_context"},
        "gates": {"physical_daily_files": False},
        "kill_switches": [reason],
        "artifacts": [str(ITER_DIR / "PRE_REG.md"), str(ITER_DIR / "run_iteration.py"), str(ITER_DIR / "RESULTS.json"), str(ITER_DIR / "audit.json")],
        "notes": reason,
    }
    (ITER_DIR / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    (ITER_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
