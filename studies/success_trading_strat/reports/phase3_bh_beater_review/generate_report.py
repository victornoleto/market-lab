"""Generate consolidated Phase 3 B&H-beater report artifacts.

The report keeps Phase 3 economic gates separate from strict validation gates:
beating buy-and-hold is necessary but not sufficient, while PBO/DSR/MCPT/WF/OOS/
FWD/bootstrap/cross-lib remain hard controls `[testing_tuning, p.318-320]`,
`[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[4]
PHASE_DIR = ROOT / "studies" / "success_trading_strat" / "iters" / "phase03"
OUT_DIR = ROOT / "studies" / "success_trading_strat" / "reports" / "phase3_bh_beater_review"
PLOTS_DIR = OUT_DIR / "plots"
PRICE_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
TRADING_DAYS = 252
CORE_GATES = ["is_mcpt", "wf_mcpt", "pbo", "dsr", "wf_windows", "oos", "fwd_63d", "bootstrap", "cross_lib"]


@dataclass(frozen=True)
class IterationRow:
    iteration: str
    family: str
    status: str
    n_trials: int
    best_config: str
    cagr: float | None
    benchmark_label: str
    benchmark_cagr: float | None
    excess_cagr: float | None
    terminal_wealth: float | None
    benchmark_terminal_wealth: float | None
    max_drawdown: float | None
    sharpe: float | None
    pbo: float | None
    dsr_p: float | None
    is_mcpt_p: float | None
    wf_mcpt_p: float | None
    core_pass_count: int
    core_gate_count: int
    failed_core_gates: str
    all_failed_gates: str
    winner: bool


def main() -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    rows, raw_results = parse_results()
    table = pd.DataFrame([row.__dict__ for row in rows])
    table.to_csv(OUT_DIR / "phase3_summary_table.csv", index=False)

    returns = load_best_returns(raw_results)
    curve_metrics = compute_curve_metrics(returns)
    curve_metrics.to_csv(OUT_DIR / "curve_metrics.csv", index=False)
    rolling = compute_rolling_windows(returns)
    rolling.to_csv(OUT_DIR / "rolling_windows.csv", index=False)
    if returns:
        pd.concat(returns, axis=1, sort=False).to_csv(OUT_DIR / "selected_candidate_returns.csv")

    plot_status_counts(table)
    plot_gate_fail_counts(table)
    plot_excess_cagr(table)
    plot_robustness_scatter(table)
    plot_curves(returns)
    plot_drawdowns(returns)
    plot_relative_vs_spy(returns)
    plot_rolling(rolling)

    write_report(table, curve_metrics, rolling)


def parse_results() -> tuple[list[IterationRow], dict[str, dict[str, Any]]]:
    rows: list[IterationRow] = []
    raw: dict[str, dict[str, Any]] = {}
    for path in sorted(PHASE_DIR.glob("*/RESULTS.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        iteration = data.get("iteration") or path.parent.name
        raw[iteration] = {"path": path, "data": data}
        metrics = (data.get("metrics") or {}).get("best") or {}
        gates = data.get("gates") or {}
        benchmark_label, benchmark_cagr, benchmark_tw = choose_primary_benchmark(metrics, gates, data.get("benchmark") or {})
        cagr = as_float(metrics.get("cagr"))
        excess = cagr - benchmark_cagr if cagr is not None and benchmark_cagr is not None else None
        core_bools = {gate: gates.get(gate) for gate in CORE_GATES if isinstance(gates.get(gate), bool)}
        failed_core = [gate for gate, passed in core_bools.items() if not passed]
        failed_all = [gate for gate, passed in gates.items() if isinstance(passed, bool) and not passed]
        best_config = data.get("best_config")
        rows.append(
            IterationRow(
                iteration=iteration,
                family=family_from_iteration(iteration),
                status=str(data.get("status") or ""),
                n_trials=int(data.get("n_trials") or 0),
                best_config=str(best_config.get("name") if isinstance(best_config, dict) else ""),
                cagr=cagr,
                benchmark_label=benchmark_label,
                benchmark_cagr=benchmark_cagr,
                excess_cagr=excess,
                terminal_wealth=as_float(metrics.get("terminal_wealth")),
                benchmark_terminal_wealth=benchmark_tw,
                max_drawdown=as_float(metrics.get("max_drawdown")),
                sharpe=as_float(metrics.get("sharpe")),
                pbo=as_float(gates.get("pbo_value")),
                dsr_p=as_float(gates.get("dsr_p_value")),
                is_mcpt_p=as_float(gates.get("is_mcpt_p_value")),
                wf_mcpt_p=as_float(gates.get("wf_mcpt_p_value")),
                core_pass_count=sum(1 for passed in core_bools.values() if passed),
                core_gate_count=len(core_bools),
                failed_core_gates=";".join(failed_core),
                all_failed_gates=";".join(failed_all),
                winner=bool(data.get("winner")),
            )
        )
    return rows, raw


def choose_primary_benchmark(metrics: dict[str, Any], gates: dict[str, Any], benchmark: dict[str, Any]) -> tuple[str, float | None, float | None]:
    available = benchmark_candidates(metrics)
    if not available:
        return "", None, None

    labels: set[str] = set()
    primary = str(benchmark.get("primary") or "").lower()
    gate_text = " ".join(key for key in gates if key.startswith("economic_cagr"))
    text = f"{primary} {gate_text}".lower()

    if "spy" in text:
        labels.add("spy_bh")
    if "qqq" in text:
        labels.add("qqq_bh")
    if "semis" in text:
        labels.update(label for label in available if "semis" in label or "smh" in label and "ew" in label)
    if "qld_tlt_gld" in text:
        labels.update(label for label in available if "qld_tlt_gld" in label)
    if "universe" in text:
        labels.update(label for label in available if "universe" in label)
    if "equal_weight" in text or "equal-weight" in text or "_ew" in text:
        labels.update(label for label in available if label.startswith("ew_bh") or "_ew_bh" in label or "universe" in label)

    selected = [item for item in available.items() if item[0] in labels]
    if not selected:
        selected = [(label, values) for label, values in available.items() if not label.startswith("shv_bh")]
    label, values = max(selected, key=lambda item: item[1][0] if item[1][0] is not None else -999.0)
    return label, values[0], values[1]


def benchmark_candidates(metrics: dict[str, Any]) -> dict[str, tuple[float | None, float | None]]:
    out: dict[str, tuple[float | None, float | None]] = {}
    for key, value in metrics.items():
        if not key.endswith("_cagr") or "_bh_" not in key:
            continue
        label = key[: -len("_cagr")]
        out[label] = (as_float(value), as_float(metrics.get(f"{label}_terminal_wealth")))
    return out


def load_best_returns(raw_results: dict[str, dict[str, Any]]) -> dict[str, pd.Series]:
    summary = pd.read_csv(OUT_DIR / "phase3_summary_table.csv")
    eligible = summary[summary["best_config"].fillna("") != ""].copy()
    eligible = eligible.sort_values(["excess_cagr", "core_pass_count"], ascending=[False, False], na_position="last")
    keep = set(eligible.head(12)["iteration"])
    keep.update(summary[summary["status"] == "economic_beater_not_validated"].head(20)["iteration"])

    returns: dict[str, pd.Series] = {}
    for iteration, payload in raw_results.items():
        if iteration not in keep:
            continue
        data = payload["data"]
        best_config = data.get("best_config")
        best_name = best_config.get("name") if isinstance(best_config, dict) else None
        if not best_name:
            continue
        csv_path = payload["path"].parent / "returns.csv"
        if not csv_path.exists():
            continue
        frame = pd.read_csv(csv_path, index_col=0, parse_dates=True)
        if best_name not in frame.columns:
            continue
        label = f"{iteration[:3]} {best_name}"
        returns[label] = frame[best_name].astype(float).dropna()
    return returns


def compute_curve_metrics(returns: dict[str, pd.Series]) -> pd.DataFrame:
    rows = []
    for label, series in returns.items():
        spy = load_ticker_returns("SPY", series.index)
        rows.append(
            {
                "label": label,
                "start": str(series.index.min().date()),
                "end": str(series.index.max().date()),
                "strategy_cagr": cagr(series),
                "strategy_sharpe": sharpe(series),
                "strategy_mdd": max_drawdown(series),
                "strategy_terminal_multiple": terminal(series),
                "spy_cagr": cagr(spy),
                "spy_sharpe": sharpe(spy),
                "spy_mdd": max_drawdown(spy),
                "spy_terminal_multiple": terminal(spy),
            }
        )
    return pd.DataFrame(rows).sort_values("strategy_cagr", ascending=False)


def compute_rolling_windows(returns: dict[str, pd.Series]) -> pd.DataFrame:
    rows = []
    for label, series in returns.items():
        spy = load_ticker_returns("SPY", series.index)
        for years in [1, 3, 5, 10, 15]:
            window = years * TRADING_DAYS
            if len(series) < window:
                continue
            strat_roll = rolling_cagr(series, window)
            spy_roll = rolling_cagr(spy, window).reindex(strat_roll.index).dropna()
            strat_roll = strat_roll.reindex(spy_roll.index).dropna()
            rows.append(
                {
                    "label": label,
                    "window_years": years,
                    "strategy_median_cagr": float(strat_roll.median()),
                    "strategy_min_cagr": float(strat_roll.min()),
                    "spy_median_cagr": float(spy_roll.median()),
                    "spy_min_cagr": float(spy_roll.min()),
                    "share_beating_spy": float((strat_roll > spy_roll).mean()),
                }
            )
    return pd.DataFrame(rows)


def plot_status_counts(table: pd.DataFrame) -> None:
    counts = table["status"].value_counts().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    counts.plot(kind="barh", ax=ax, color="#4C78A8")
    ax.set_title("Phase 3 Status Counts")
    ax.set_xlabel("iterations")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "status_counts.png", dpi=160)
    plt.close(fig)


def plot_gate_fail_counts(table: pd.DataFrame) -> None:
    counter: Counter[str] = Counter()
    for value in table["failed_core_gates"].dropna():
        for gate in str(value).split(";"):
            if gate:
                counter[gate] += 1
    counts = pd.Series(counter).sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    counts.plot(kind="barh", ax=ax, color="#F58518")
    ax.set_title("Strict Core Gate Fail Counts")
    ax.set_xlabel("fail count")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "gate_fail_counts.png", dpi=160)
    plt.close(fig)


def plot_excess_cagr(table: pd.DataFrame) -> None:
    data = table.dropna(subset=["excess_cagr"]).sort_values("excess_cagr", ascending=False).head(20)
    labels = data["iteration"].str[:3] + " " + data["best_config"].fillna("")
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(labels[::-1], data["excess_cagr"].iloc[::-1] * 100, color="#54A24B")
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_title("Top Phase 3 Excess CAGR vs Conservative Primary B&H")
    ax.set_xlabel("excess CAGR (percentage points)")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "excess_cagr_ranking.png", dpi=160)
    plt.close(fig)


def plot_robustness_scatter(table: pd.DataFrame) -> None:
    data = table.dropna(subset=["excess_cagr"])
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = data["status"].map({"economic_beater_not_validated": "#54A24B", "fail": "#E45756", "data_blocked": "#BAB0AC"}).fillna("#4C78A8")
    ax.scatter(data["excess_cagr"] * 100, data["core_pass_count"], c=colors, s=70, alpha=0.85)
    for _, row in data.iterrows():
        if row["status"] == "economic_beater_not_validated" or row["core_pass_count"] >= 7:
            ax.annotate(str(row["iteration"])[:3], (row["excess_cagr"] * 100, row["core_pass_count"]), fontsize=8)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_title("Economics vs Robustness")
    ax.set_xlabel("excess CAGR vs primary B&H (pp)")
    ax.set_ylabel("core gates passed")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "economics_vs_robustness.png", dpi=160)
    plt.close(fig)


def plot_curves(returns: dict[str, pd.Series]) -> None:
    if not returns:
        return
    ordered = sorted(returns.items(), key=lambda item: cagr(item[1]), reverse=True)[:12]
    fig, ax = plt.subplots(figsize=(11, 6))
    for label, series in ordered:
        equity = (1.0 + series).cumprod()
        ax.plot(equity.index, equity, label=label, linewidth=1.5)
    ax.set_yscale("log")
    ax.set_title("Selected Phase 3 Best Config Equity Curves")
    ax.set_ylabel("growth of $1, log scale")
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "selected_equity_log.png", dpi=160)
    plt.close(fig)


def plot_drawdowns(returns: dict[str, pd.Series]) -> None:
    if not returns:
        return
    ordered = sorted(returns.items(), key=lambda item: cagr(item[1]), reverse=True)[:12]
    fig, ax = plt.subplots(figsize=(11, 6))
    for label, series in ordered:
        equity = (1.0 + series).cumprod()
        dd = equity / equity.cummax() - 1.0
        ax.plot(dd.index, dd * 100, label=label, linewidth=1.2)
    ax.set_title("Selected Phase 3 Drawdowns")
    ax.set_ylabel("drawdown (%)")
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "selected_drawdowns.png", dpi=160)
    plt.close(fig)


def plot_relative_vs_spy(returns: dict[str, pd.Series]) -> None:
    if not returns:
        return
    ordered = sorted(returns.items(), key=lambda item: cagr(item[1]), reverse=True)[:12]
    fig, ax = plt.subplots(figsize=(11, 6))
    for label, series in ordered:
        spy = load_ticker_returns("SPY", series.index)
        rel = (1.0 + series).cumprod() / (1.0 + spy).cumprod()
        ax.plot(rel.index, rel, label=label, linewidth=1.3)
    ax.set_yscale("log")
    ax.axhline(1.0, color="black", linewidth=0.8)
    ax.set_title("Selected Phase 3 Relative Wealth vs SPY")
    ax.set_ylabel("strategy equity / SPY equity, log scale")
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "selected_relative_vs_spy.png", dpi=160)
    plt.close(fig)


def plot_rolling(rolling: pd.DataFrame) -> None:
    if rolling.empty:
        return
    for years in sorted(rolling["window_years"].unique()):
        data = rolling[rolling["window_years"] == years].sort_values("share_beating_spy", ascending=True)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(data["label"], data["share_beating_spy"] * 100, color="#72B7B2")
        ax.set_title(f"Rolling {years}Y Share Beating SPY")
        ax.set_xlabel("share of rolling windows (%)")
        fig.tight_layout()
        fig.savefig(PLOTS_DIR / f"rolling_{years}y_share_beating_spy.png", dpi=160)
        plt.close(fig)


def write_report(table: pd.DataFrame, curve_metrics: pd.DataFrame, rolling: pd.DataFrame) -> None:
    status_counts = table["status"].value_counts().to_dict()
    total_trials = int(table["n_trials"].sum())
    strict = int(table["winner"].sum())
    economic = table[table["status"] == "economic_beater_not_validated"].copy()
    fail = table[table["status"] == "fail"].copy()
    data_blocked = table[table["status"] == "data_blocked"].copy()
    top_excess = table.dropna(subset=["excess_cagr"]).sort_values("excess_cagr", ascending=False).head(10)
    robust = table[table["core_gate_count"] > 0].sort_values(["core_pass_count", "excess_cagr"], ascending=[False, False]).head(10)

    lines = [
        "# Phase 3 Buy-And-Hold Beater Review",
        "",
        "## Verdict",
        "",
        "Phase 3 closed with no validated strategy: zero `strict_winner`, zero `candidate_watchlist`, zero `paper_trade_candidate` and zero `winner=true`. Seventeen iterations found economic beaters, but every one failed at least one hard validation gate, mainly MCPT and DSR. This is research-only and does not authorize paper/live deployment; mandate capital remains 100% Plano C `[testing_tuning, p.318-320]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.",
        "",
        "## Files",
        "",
        "- `phase3_summary_table.csv`: one row per Phase 3 iteration.",
        "- `curve_metrics.csv`: recomputed metrics for selected plotted candidates versus aligned SPY.",
        "- `rolling_windows.csv`: rolling 1/3/5/10/15y diagnostics for selected candidates versus SPY.",
        "- `selected_candidate_returns.csv`: selected best-config return series used in plots.",
        "- Plot metrics are recomputed from each iteration's saved `returns.csv`; the canonical economic verdicts remain the per-iteration `RESULTS.json` rows above.",
        "- `plots/selected_equity_log.png`: selected equity curves.",
        "- `plots/selected_drawdowns.png`: selected drawdown curves.",
        "- `plots/selected_relative_vs_spy.png`: selected relative wealth versus SPY.",
        "- `plots/excess_cagr_ranking.png`: excess CAGR ranking.",
        "- `plots/economics_vs_robustness.png`: economics versus gate pass count.",
        "- `plots/gate_fail_counts.png`: strict gate failure counts.",
        "- `plots/status_counts.png`: final status counts.",
        "",
        "## Totals",
        "",
        f"- Iterations: `{len(table)}`.",
        f"- Phase-local strategy trials: `{total_trials}`.",
        "- Global cumulative trial accounting after Phase 3: `312`.",
        f"- Status counts: `{status_counts}`.",
        f"- Strict winners: `{strict}`.",
        "",
        "## Plots",
        "",
        "![Selected equity curves](plots/selected_equity_log.png)",
        "",
        "![Selected drawdowns](plots/selected_drawdowns.png)",
        "",
        "![Relative wealth vs SPY](plots/selected_relative_vs_spy.png)",
        "",
        "![Excess CAGR ranking](plots/excess_cagr_ranking.png)",
        "",
        "![Economics vs robustness](plots/economics_vs_robustness.png)",
        "",
        "![Gate fail counts](plots/gate_fail_counts.png)",
        "",
        "## Iteration Table",
        "",
        markdown_table(table_for_report(table)),
        "",
        "## Ranking By Excess CAGR",
        "",
        markdown_table(rank_table(top_excess)),
        "",
        "## Ranking By Robustness",
        "",
        markdown_table(robust_table(robust)),
        "",
        "## Status Buckets",
        "",
        f"- `strict_winner`: {list_items(table[table['winner']])}",
        f"- `economic_beater_not_validated`: {list_items(economic)}",
        "- `candidate_watchlist`: none.",
        "- `paper_trade_candidate`: none.",
        f"- `fail`: {list_items(fail)}",
        f"- `data_blocked`: {list_items(data_blocked)}",
        "",
        "## Beaters That Failed Validation",
        "",
        "The economically strongest families were LETF/controlled-leverage sleeves, semiconductor/technology LETF exposure, crash-rearm overlays and high-beta rotation. They beat the aligned B&H benchmark in CAGR and terminal wealth, but none survived the full validation stack. This is exactly the failure mode the Phase 3 spec was designed to expose: leverage can create attractive CAGR, but without MCPT/DSR/PBO robustness it remains a backtest artifact candidate rather than a strategy `[leverage_for_the_long_run, p.13]`, `[leverage_space, p.149-167]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.",
        "",
        "Common blockers:",
        "",
        "- MCPT failures: the observed result was not sufficiently extreme versus permuted-path nulls `[testing_tuning, p.318-320]`.",
        "- DSR failures: after cumulative trial accounting, Sharpe was not statistically defensible `[advances_fin_ml, p.222-223]`.",
        "- PBO failures in several stress/overlay variants: parameter selection risk remained too high `[advances_fin_ml, p.208-211]`.",
        "- Rolling/inception stress failures: some economic beaters depended on favorable asset-inception windows or specific 3y/5y regimes `[testing_tuning, p.327-335]`.",
        "",
        "## No Validated Strategy Passed",
        "",
        "No candidate passed the strict combination of economic gates plus IS MCPT, WF MCPT, PBO, DSR, WF windows, OOS, FWD, bootstrap and cross-lib. Therefore Phase 3 cannot justify Phase 4, paper trading or deployment. Under the mandate, any hard-gate failure blocks promotion; there is no `almost passed` override `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.",
        "",
        "## Lessons",
        "",
        "- Beating B&H requires an upside engine: the best economic results came from embedded leverage and high-beta participation, not defensive long/flat filters `[systematic_trading, p.40]`, `[leverage_for_the_long_run, p.13]`.",
        "- Simple balanced leverage sleeves can be economically strong, especially `UPRO/TLT/GLD`, but their validation failures suggest historical sequencing risk rather than robust edge.",
        "- More local tuning is not justified: the dominant blockers are MCPT/DSR/PBO and rolling stress, not a missing nearby lookback threshold `[testing_tuning, p.327-335]`.",
        "- If future work resumes, it should start from a new pre-registered mechanism or independent data regime, not another Phase 3 local sweep.",
        "",
        "## Recommendation",
        "",
        "Stop the Phase 3 hunt. Do not open Phase 4 from these results. Do not paper trade any Phase 3 candidate. Keep the project mandate unchanged: no deploy implication and 100% Plano C remains the only active allocation.",
        "",
    ]
    (OUT_DIR / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def table_for_report(table: pd.DataFrame) -> pd.DataFrame:
    cols = ["iteration", "family", "status", "n_trials", "best_config", "cagr", "benchmark_cagr", "excess_cagr", "terminal_wealth", "benchmark_terminal_wealth", "max_drawdown", "sharpe", "pbo", "dsr_p", "failed_core_gates"]
    return format_df(table[cols])


def rank_table(table: pd.DataFrame) -> pd.DataFrame:
    cols = ["iteration", "best_config", "status", "cagr", "benchmark_label", "benchmark_cagr", "excess_cagr", "terminal_wealth", "benchmark_terminal_wealth", "failed_core_gates"]
    return format_df(table[cols])


def robust_table(table: pd.DataFrame) -> pd.DataFrame:
    cols = ["iteration", "best_config", "status", "core_pass_count", "core_gate_count", "excess_cagr", "pbo", "dsr_p", "failed_core_gates"]
    return format_df(table[cols])


def format_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    pct_cols = ["cagr", "benchmark_cagr", "excess_cagr", "max_drawdown"]
    for col in pct_cols:
        if col in out:
            out[col] = out[col].map(lambda x: "" if pd.isna(x) else f"{x:.2%}")
    for col in ["terminal_wealth", "benchmark_terminal_wealth", "sharpe", "pbo", "dsr_p"]:
        if col in out:
            out[col] = out[col].map(lambda x: "" if pd.isna(x) else f"{x:.4g}")
    return out.fillna("")


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "None."
    headers = list(df.columns)
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for _, row in df.iterrows():
        values = [str(row[col]).replace("|", "\\|") for col in headers]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def list_items(df: pd.DataFrame) -> str:
    if df.empty:
        return "none"
    return ", ".join(f"`{row.iteration[:3]} {row.best_config or row.family}`" for row in df.itertuples())


def load_ticker_returns(ticker: str, index: pd.Index) -> pd.Series:
    path = PRICE_DIR / f"{ticker}.parquet"
    df = pd.read_parquet(path)
    df.index = pd.to_datetime(df.index).tz_localize(None)
    close_col = "adj_close" if "adj_close" in df.columns else "close"
    close = df[close_col].astype(float).sort_index()
    returns = close.pct_change().fillna(0.0).reindex(index).fillna(0.0)
    return returns


def rolling_cagr(returns: pd.Series, window: int) -> pd.Series:
    compounded = (1.0 + returns).rolling(window).apply(np.prod, raw=True) - 1.0
    years = window / TRADING_DAYS
    return (1.0 + compounded) ** (1.0 / years) - 1.0


def family_from_iteration(iteration: str) -> str:
    parts = iteration.split("-", 4)
    return parts[4] if len(parts) == 5 else iteration


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    return float(value)


def cagr(returns: pd.Series) -> float:
    if returns.empty:
        return 0.0
    total = terminal(returns) - 1.0
    years = len(returns) / TRADING_DAYS
    return float((1.0 + total) ** (1.0 / years) - 1.0) if years > 0 and total > -1.0 else -1.0


def terminal(returns: pd.Series) -> float:
    return float((1.0 + returns).prod())


def sharpe(returns: pd.Series) -> float:
    std = float(returns.std(ddof=1))
    return 0.0 if std == 0.0 else float(returns.mean() / std * np.sqrt(TRADING_DAYS))


def max_drawdown(returns: pd.Series) -> float:
    equity = (1.0 + returns).cumprod()
    return float((equity / equity.cummax() - 1.0).min())


if __name__ == "__main__":
    main()
