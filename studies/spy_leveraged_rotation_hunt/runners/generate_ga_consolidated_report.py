"""Generate the consolidated SPY leveraged-rotation GA report.

This script reconstructs the best gene from each completed evolution and compares
them against SPY/SSO/UPRO buy-hold plus canonical LRS baselines. It is reporting
only; the GA remains discovery evidence pending PBO/DSR and other hard gates
`[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.core.data_loader import load_testfolio_series
from studies.technical_signal_vote_hunt.core import daily_returns, sma
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import _metrics_row_np, _simulate_on_off_np
from studies.spy_leveraged_rotation_hunt.runners.run_spy_repair_ga_evolutions import (
    Gene,
    Context,
    RESULTS_DIR,
    REPORT_DIR,
    _returns_for_gene,
)


TRADING_DAYS_PER_YEAR = 252


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate consolidated GA report")
    p.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    p.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = args.report_dir / "ga_consolidated"
    tables_dir = out_dir / "tables"
    plots_dir = out_dir / "plots"
    tables_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    ctx = Context()
    candidates = _load_best_candidates(args.results_dir)
    returns = _baseline_returns(ctx)
    for label, gene in candidates.items():
        returns[label] = _returns_for_gene(ctx, gene)
    panel = pd.concat(returns, axis=1, sort=False).dropna()
    metrics = _metrics_table(panel)
    rolling = _rolling_table(panel)
    relative_scores = _rolling_relative_scores(panel)
    relative = (1.0 + panel).cumprod().div((1.0 + panel["SPY buy_hold"]).cumprod(), axis=0)

    panel.to_csv(tables_dir / "comparison_returns.csv")
    metrics.to_csv(tables_dir / "comparison_metrics.csv")
    rolling.to_csv(tables_dir / "comparison_rolling_windows.csv", index=False)
    relative_scores.to_csv(tables_dir / "rolling_relative_scores.csv", index=False)
    relative.to_csv(tables_dir / "comparison_relative_to_spy.csv")
    _plot_equity(panel, plots_dir / "comparison_equity.png")
    _plot_drawdown(panel, plots_dir / "comparison_drawdown.png")
    _plot_relative(relative, plots_dir / "comparison_relative_to_spy.png")
    _write_report(args.report_dir / "GA_EVOLUTION_REPORT.md", args.results_dir, candidates, metrics, rolling, relative_scores, panel.index)
    print(f"wrote {args.report_dir / 'GA_EVOLUTION_REPORT.md'}", flush=True)
    return 0


def _load_best_candidates(results_dir: Path) -> dict[str, Gene]:
    out: dict[str, Gene] = {}
    for path in sorted(results_dir.glob("evo*/tables/top_candidates.csv")):
        df = pd.read_csv(path)
        if df.empty:
            continue
        row = df.iloc[0]
        evo = path.parents[1].name
        label = f"{evo} best"
        out[label] = Gene(
            str(row["signal_asset"]),
            int(row["sma_long"]),
            int(row["sma_short"]),
            int(row["vol_window"]),
            float(row["vol_threshold"]),
            int(row["ar_window"]),
            int(row["entry_k"]),
            int(row["t_crash"]),
            int(row["d_arm"]),
            float(row["normal_upro_weight"]),
            float(row["rearm_upro_weight"]),
            float(row["zroz_off_weight"]),
        )
    return out


def _baseline_returns(ctx: Context) -> dict[str, pd.Series]:
    spy_lrs = _sma200_signal(ctx.prices["SPY"])
    return {
        "SPY buy_hold": ctx.returns["SPY"],
        "SSO buy_hold": ctx.returns["SSO"],
        "UPRO buy_hold": ctx.returns["UPRO"],
        "LRS SPY->SSO": _on_off(spy_lrs, ctx.returns["SSO"], ctx.returns["CASH"]),
        "LRS SPY->UPRO": _on_off(spy_lrs, ctx.returns["UPRO"], ctx.returns["CASH"]),
    }


def _sma200_signal(prices: pd.Series) -> pd.Series:
    ma = sma(prices.astype(float), 200)
    out = (prices > ma).astype(float)
    out[ma.isna()] = np.nan
    return out


def _on_off(signal: pd.Series, on_returns: pd.Series, off_returns: pd.Series) -> pd.Series:
    aligned = pd.concat({"sig": signal, "on": on_returns, "off": off_returns}, axis=1, sort=False).dropna(subset=["on", "off"])
    sig = aligned["sig"].fillna(0.0).to_numpy(float) >= 1.0
    daily = _simulate_on_off_np(sig, aligned["on"].to_numpy(float), aligned["off"].to_numpy(float))
    return pd.Series(daily, index=aligned.index)


def _metrics_table(returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    bench = returns["SPY buy_hold"].to_numpy(float)
    dates = pd.DatetimeIndex(returns.index)
    for label in returns.columns:
        rows.append(_metrics_row_np(returns[label].to_numpy(float), bench, dates, label, "SPY", "consolidated", 0, 0, "comparison"))
    return pd.DataFrame(rows).set_index("label").sort_values(["sortino", "cagr", "calmar"], ascending=[False, False, False])


def _rolling_table(returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label in returns.columns:
        r = returns[label].dropna()
        for years in (3, 5, 10, 15):
            vals = (1.0 + r).rolling(years * TRADING_DAYS_PER_YEAR).apply(np.prod, raw=True).dropna()
            cagr = vals ** (1.0 / years) - 1.0
            rows.append(
                {
                    "label": label,
                    "years": years,
                    "min_cagr": float(cagr.min()) if len(cagr) else np.nan,
                    "median_cagr": float(cagr.median()) if len(cagr) else np.nan,
                    "pct_positive": float((cagr > 0.0).mean()) if len(cagr) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def _rolling_relative_scores(returns: pd.DataFrame) -> pd.DataFrame:
    """Monthly-end rolling relative-equity scores versus SPY buy-hold.

    For each month-end and horizon, both strategy and benchmark are rebased to 1
    at the start of that rolling window. `pct_above` is the fraction of days where
    strategy equity is above benchmark equity; `mean_rel` is the average
    strategy/benchmark equity ratio inside the window. Long windows receive more
    weight because persistent outperformance is more relevant than short bursts.
    """
    horizons = (1, 3, 5, 10, 15, 20)
    weights = {1: 0.05, 3: 0.10, 5: 0.15, 10: 0.20, 15: 0.25, 20: 0.25}
    benchmark = returns["SPY buy_hold"].dropna()
    month_ends = returns.resample("ME").last().index
    rows = []
    summary_rows = []
    for label in returns.columns:
        if label == "SPY buy_hold":
            continue
        strategy = returns[label].dropna()
        aligned = pd.concat({"s": strategy, "b": benchmark}, axis=1, sort=False).dropna()
        horizon_scores = {}
        horizon_mags = {}
        horizon_counts = {}
        for years in horizons:
            window_days = years * TRADING_DAYS_PER_YEAR
            pct_vals = []
            mag_vals = []
            for end in month_ends:
                sub = aligned.loc[:end].tail(window_days)
                if len(sub) < int(window_days * 0.95):
                    continue
                s_eq = (1.0 + sub["s"]).cumprod()
                b_eq = (1.0 + sub["b"]).cumprod()
                rel = s_eq / b_eq
                pct_vals.append(float((rel > 1.0).mean()))
                mag_vals.append(float(rel.mean()))
            pct_score = float(np.mean(pct_vals)) if pct_vals else np.nan
            mag_score = float(np.mean(mag_vals)) if mag_vals else np.nan
            horizon_scores[years] = pct_score
            horizon_mags[years] = mag_score
            horizon_counts[years] = len(pct_vals)
            rows.append(
                {
                    "label": label,
                    "years": years,
                    "weight": weights[years],
                    "n_monthly_windows": len(pct_vals),
                    "pct_above_score": pct_score,
                    "mean_relative_equity_score": mag_score,
                }
            )
        valid_pct_weight = sum(weights[y] for y in horizons if np.isfinite(horizon_scores[y]))
        valid_mag_weight = sum(weights[y] for y in horizons if np.isfinite(horizon_mags[y]))
        pct_overall = sum(weights[y] * horizon_scores[y] for y in horizons if np.isfinite(horizon_scores[y])) / valid_pct_weight if valid_pct_weight else np.nan
        mag_overall = sum(weights[y] * horizon_mags[y] for y in horizons if np.isfinite(horizon_mags[y])) / valid_mag_weight if valid_mag_weight else np.nan
        summary_rows.append(
            {
                "label": label,
                "years": "overall",
                "weight": 1.0,
                "n_monthly_windows": int(sum(horizon_counts.values())),
                "pct_above_score": pct_overall,
                "mean_relative_equity_score": mag_overall,
            }
        )
    return pd.DataFrame([*rows, *summary_rows])


def _plot_equity(returns: pd.DataFrame, path: Path) -> None:
    equity = (1.0 + returns).cumprod()
    ax = equity.plot(figsize=(13, 8), logy=True, linewidth=1.1)
    ax.set_title("SPY Rotation GA Candidates vs Benchmarks")
    ax.set_ylabel("Growth of $1, log scale")
    ax.grid(True, alpha=0.3)
    ax.figure.tight_layout()
    ax.figure.savefig(path, dpi=140)
    plt.close(ax.figure)


def _plot_drawdown(returns: pd.DataFrame, path: Path) -> None:
    equity = (1.0 + returns).cumprod()
    dd = equity / equity.cummax() - 1.0
    ax = dd.plot(figsize=(13, 8), linewidth=1.0)
    ax.set_title("Drawdowns")
    ax.set_ylabel("Drawdown")
    ax.grid(True, alpha=0.3)
    ax.figure.tight_layout()
    ax.figure.savefig(path, dpi=140)
    plt.close(ax.figure)


def _plot_relative(relative: pd.DataFrame, path: Path) -> None:
    ax = relative.plot(figsize=(13, 8), logy=True, linewidth=1.0)
    ax.set_title("Relative Equity vs SPY Buy-Hold")
    ax.set_ylabel("Strategy / SPY, log scale")
    ax.grid(True, alpha=0.3)
    ax.figure.tight_layout()
    ax.figure.savefig(path, dpi=140)
    plt.close(ax.figure)


def _write_report(
    path: Path,
    results_dir: Path,
    candidates: dict[str, Gene],
    metrics: pd.DataFrame,
    rolling: pd.DataFrame,
    relative_scores: pd.DataFrame,
    index: pd.DatetimeIndex,
) -> None:
    manifests = _load_manifests(results_dir)
    manifest_df = pd.DataFrame(manifests).sort_values(["beats_spy_economic", "best_sortino", "best_cagr"], ascending=[False, False, False]) if manifests else pd.DataFrame()
    total_trials = int(manifest_df["evaluated_unique"].sum()) if len(manifest_df) else 0
    spy = metrics.loc["SPY buy_hold"]
    economic_beaters = metrics[(metrics["cagr"] > spy["cagr"]) & (metrics["sharpe"] > spy["sharpe"]) & (metrics["sortino"] > spy["sortino"]) & (metrics["mdd"] > spy["mdd"])]
    candidate_labels = [label for label in candidates]
    candidate_metrics = metrics.loc[[label for label in candidate_labels if label in metrics.index]]
    top_candidate_metrics = candidate_metrics[["cagr", "sharpe", "sortino", "mdd", "calmar", "end_rel_to_benchmark"]].sort_values(
        ["sortino", "cagr", "calmar"], ascending=[False, False, False]
    )
    roll_min = rolling.pivot(index="label", columns="years", values="min_cagr").rename(columns={3: "3y_min", 5: "5y_min", 10: "10y_min", 15: "15y_min"})
    rolling_candidates = roll_min.loc[[label for label in candidate_labels if label in roll_min.index]]
    rel_overall = relative_scores[relative_scores["years"].astype(str) == "overall"].copy()
    rel_overall = rel_overall.set_index("label").sort_values(
        ["pct_above_score", "mean_relative_equity_score"], ascending=[False, False]
    )
    pct_by_horizon = _relative_score_pivot(relative_scores, "pct_above_score")
    mag_by_horizon = _relative_score_pivot(relative_scores, "mean_relative_equity_score")
    best_spy_signal = _best_by_signal(candidates, candidate_metrics, "SPY")
    best_sso_signal = _best_by_signal(candidates, candidate_metrics, "SSO")
    best_time = rel_overall.sort_values("pct_above_score", ascending=False).head(1)
    best_magnitude = rel_overall.sort_values("mean_relative_equity_score", ascending=False).head(1)
    best_time_text = _best_relative_line(best_time, "tempo acima")
    best_magnitude_text = _best_relative_line(best_magnitude, "magnitude relativa")
    lines = [
        "# SPY Leveraged Rotation GA Evolution Report",
        "",
        f"Window: `{index.min().date()}..{index.max().date()}`",
        f"Completed evolutions: `{len(manifest_df)}`",
        f"Unique candidates in final manifests: `{total_trials}`",
        "",
        "## Executive Read",
        "",
        f"Initial economic screen beaters vs `SPY buy_hold`: `{len(economic_beaters.loc[[x for x in candidate_labels if x in economic_beaters.index]])}` among GA best candidates.",
        best_time_text,
        best_magnitude_text,
        best_spy_signal,
        best_sso_signal,
        "",
        "Interpretation: `evo02` is the performance-first/most-often-ahead candidate, while `evo05` is the strongest average relative-equity candidate. The best clean `SPY` underlying-signal candidate remains `evo01`; the strongest overall economic candidate uses `SSO` self-regime, so it carries the same conceptual caveat identified in the prior QLD audit `[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.5-7]`.",
        "",
        "No candidate is deploy-authorized. These are discovery results only until OOS/FWD/WF/bootstrap/PBO/DSR validation is run with cumulative trial accounting `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.",
        "",
        "## Plots",
        "",
        "### Equity",
        "",
        "![Equity](ga_consolidated/plots/comparison_equity.png)",
        "",
        "### Relative Equity vs SPY",
        "",
        "![Relative equity vs SPY](ga_consolidated/plots/comparison_relative_to_spy.png)",
        "",
        "### Drawdown",
        "",
        "![Drawdown](ga_consolidated/plots/comparison_drawdown.png)",
        "",
        "## Quick Rankings",
        "",
        "### Candidate Metrics",
        "",
        top_candidate_metrics.to_markdown(floatfmt=".4f") if len(top_candidate_metrics) else "No candidate metrics found.",
        "",
        "### Relative Equity Overall Scores",
        "",
        rel_overall[["pct_above_score", "mean_relative_equity_score", "n_monthly_windows"]].to_markdown(floatfmt=".4f") if len(rel_overall) else "No relative scores found.",
        "",
        "## Evolution Manifests",
        "",
        manifest_df.to_markdown(index=False, floatfmt=".4f") if len(manifest_df) else "No completed manifests found.",
        "",
        "## Candidate vs Benchmarks",
        "",
        metrics[["cagr", "sharpe", "sortino", "mdd", "calmar", "end_mult", "end_rel_to_benchmark", "pct_above_benchmark"]].to_markdown(floatfmt=".4f"),
        "",
        "## GA Candidate Rolling Windows",
        "",
        rolling_candidates.to_markdown(floatfmt=".4f") if len(rolling_candidates) else "No candidate rolling rows found.",
        "",
        "## Relative Equity Method",
        "",
        "Definition: for every possible monthly-ended rolling window, strategy and `SPY buy_hold` are rebased to 1 at the window start. `pct_above_score` is the average fraction of days where strategy equity is above SPY. `mean_relative_equity_score` is the average within-window strategy/SPY equity ratio. Overall score weights horizons as `1y=5%`, `3y=10%`, `5y=15%`, `10y=20%`, `15y=25%`, `20y=25%`.",
        "",
        "### Pct Above By Horizon",
        "",
        pct_by_horizon.to_markdown(floatfmt=".4f") if len(pct_by_horizon) else "No pct-above scores found.",
        "",
        "### Mean Relative Equity By Horizon",
        "",
        mag_by_horizon.to_markdown(floatfmt=".4f") if len(mag_by_horizon) else "No magnitude scores found.",
        "",
        "## SPY-Signal vs SSO-Self-Signal",
        "",
        "| Signal family | Best candidate | Read |",
        "|---|---|---|",
        _signal_table_row(candidates, candidate_metrics, "SPY", "Cleaner underlying-regime interpretation."),
        _signal_table_row(candidates, candidate_metrics, "SSO", "Stronger economics here, but LETF self-regime caveat."),
        "",
        "The SPY-underlying candidate is conceptually cleaner because the regime is measured on the unlevered S&P 500 proxy `[leverage_for_the_long_run, p.13]`. The SSO candidate must be labeled as LETF self-regime because SSO's own trend/volatility state drives exposure `[leverage_for_the_long_run, p.5-7]`.",
        "",
        "## Files",
        "",
        "- `reports/baseline/REPORT.md` for simple baselines.",
        "- `reports/ga_consolidated/tables/comparison_metrics.csv` for metrics.",
        "- `reports/ga_consolidated/tables/comparison_rolling_windows.csv` for rolling windows.",
        "- `reports/ga_consolidated/tables/rolling_relative_scores.csv` for monthly-ended relative-equity scores.",
        "- `reports/ga_consolidated/plots/` for equity, drawdown and relative-equity plots.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _relative_score_pivot(relative_scores: pd.DataFrame, value_col: str) -> pd.DataFrame:
    df = relative_scores[relative_scores["years"].astype(str) != "overall"].copy()
    if df.empty:
        return pd.DataFrame()
    df["years"] = df["years"].astype(int)
    pivot = df.pivot(index="label", columns="years", values=value_col)
    pivot = pivot.rename(columns={1: "1y", 3: "3y", 5: "5y", 10: "10y", 15: "15y", 20: "20y"})
    overall = relative_scores[relative_scores["years"].astype(str) == "overall"].set_index("label")[[value_col]]
    pivot["overall"] = overall[value_col]
    return pivot.sort_values("overall", ascending=False)


def _best_by_signal(candidates: dict[str, Gene], metrics: pd.DataFrame, signal_asset: str) -> str:
    labels = [label for label, gene in candidates.items() if gene.signal_asset == signal_asset and label in metrics.index]
    if not labels:
        return f"{signal_asset}: no candidate."
    row = metrics.loc[labels].sort_values(["sortino", "cagr", "calmar"], ascending=[False, False, False]).iloc[0]
    return f"{signal_asset}: best `{row.name}` with Sortino `{row['sortino']:.4f}`, CAGR `{row['cagr']:.2%}`, Sharpe `{row['sharpe']:.4f}`, MDD `{row['mdd']:.2%}`, Calmar `{row['calmar']:.4f}`."


def _best_relative_line(df: pd.DataFrame, label: str) -> str:
    if df.empty:
        return f"Best {label}: unavailable."
    row = df.iloc[0]
    return f"Best {label}: `{row.name}` with pct-above `{row['pct_above_score']:.2%}` and mean relative equity `{row['mean_relative_equity_score']:.4f}x`."


def _signal_table_row(candidates: dict[str, Gene], metrics: pd.DataFrame, signal_asset: str, read: str) -> str:
    labels = [label for label, gene in candidates.items() if gene.signal_asset == signal_asset and label in metrics.index]
    if not labels:
        return f"| `{signal_asset}` | n/a | No completed candidate. |"
    row = metrics.loc[labels].sort_values(["sortino", "cagr", "calmar"], ascending=[False, False, False]).iloc[0]
    text = f"`{row.name}`: CAGR {row['cagr']:.2%}, Sortino {row['sortino']:.4f}, MDD {row['mdd']:.2%}"
    return f"| `{signal_asset}` | {text} | {read} |"


def _load_manifests(results_dir: Path) -> list[dict]:
    out = []
    for path in sorted(results_dir.glob("evo*/manifest.json")):
        try:
            out.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return out


if __name__ == "__main__":
    raise SystemExit(main())
