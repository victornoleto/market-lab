#!/usr/bin/env python3
"""Build the consolidated weekly momentum tested-strategy summary.

This script intentionally consumes already-generated CSV artifacts instead of
rerunning backtests. The summary is a research inventory and comparison layer;
promotion gates still follow PBO/DSR/rolling-window evidence from the underlying
reports `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path("studies/weekly_momentum")
SUMMARY_PATH = ROOT / "STRATEGY_TESTED_SUMMARY.md"
PLOTS_DIR = ROOT / "summary_plots"


@dataclass(frozen=True)
class ComparedStrategy:
    label: str
    source: str
    path: Path
    verdict: str
    role: str


TOP_K_STRATEGIES = [
    ComparedStrategy(
        label="PIT lb80/k5/SMA250",
        source="Phase 3 PIT fixed",
        path=ROOT / "phase3/sp500_pit_fixed_promoted/phase2_fixed_lb80_k5_sma250",
        verdict="best research lead; not deployable",
        role="Current best PIT approximation lead; fails DSR at 200 trials.",
    ),
    ComparedStrategy(
        label="PIT lb80/k5/SMA200",
        source="Phase 3 PIT fixed",
        path=ROOT / "phase3/sp500_pit_fixed_promoted/phase2_fixed_lb80_k5_sma200",
        verdict="defensive alternate; not deployable",
        role="Similar edge with lower MDD than SMA250; also fails DSR at 200 trials.",
    ),
    ComparedStrategy(
        label="PIT original lb60/k3/SMA200",
        source="Phase 3 PIT fixed",
        path=ROOT / "phase3/sp500_pit_fixed_promoted/fixed_aggressive_sp500",
        verdict="rejected lead",
        role="Original aggressive lead weakened materially after PIT membership.",
    ),
    ComparedStrategy(
        label="PIT dynamic WF S&P",
        source="Phase 3 PIT dynamic",
        path=ROOT / "phase3/sp500_pit_dynamic_context/dynamic_wf_sp500",
        verdict="rejected",
        role="Dynamic selection process collapsed when current-membership bias was removed.",
    ),
    ComparedStrategy(
        label="Current lb60/k10/SMA100",
        source="Current-membership control",
        path=ROOT / "deploy_candidates/fixed_balanced_sp500",
        verdict="survivorship-biased control",
        role="Useful balanced baseline, but not honest enough for promotion.",
    ),
    ComparedStrategy(
        label="All-stocks dynamic WF",
        source="All-stock control",
        path=ROOT / "deploy_candidates/dynamic_wf_all_stocks",
        verdict="statistically rejected control",
        role="High gross CAGR but fails PBO and lacks PIT/delisted coverage.",
    ),
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build weekly momentum tested-strategy summary")
    parser.add_argument("--top-k", type=int, default=6)
    parser.add_argument("--output", default=str(SUMMARY_PATH))
    parser.add_argument("--plots-dir", default=str(PLOTS_DIR))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    selected = TOP_K_STRATEGIES[: args.top_k]
    plots_dir = Path(args.plots_dir)
    plots_dir.mkdir(parents=True, exist_ok=True)

    metrics = _load_top_metrics(selected)
    aligned = {item.label: _load_aligned(item.path) for item in selected}
    spy = _first_spy(aligned)

    _plot_equity(aligned, spy, plots_dir / "topk_equity_vs_spy.png")
    _plot_relative(aligned, spy, plots_dir / "topk_equity_over_spy.png")
    _plot_drawdown(aligned, spy, plots_dir / "topk_drawdown_vs_spy.png")
    _plot_rolling_cagr(aligned, spy, plots_dir / "topk_rolling_cagr_1_3_5_10y.png")
    _plot_metric_bars(metrics, plots_dir / "topk_metric_bars.png")
    _plot_gate_matrix(metrics, plots_dir / "topk_gate_matrix.png")

    report = _build_report(selected, metrics, plots_dir)
    Path(args.output).write_text(report, encoding="utf-8")
    print(f"summary={args.output}")
    print(f"plots={plots_dir}")
    print(metrics[["label", "cagr", "mdd", "sharpe", "dsr_pass", "oos_pass", "bootstrap_pass"]].to_string(index=False))
    return 0


def _load_top_metrics(items: list[ComparedStrategy]) -> pd.DataFrame:
    rows = []
    for item in items:
        comparison = _comparison_csv_for(item.path)
        df = pd.read_csv(comparison)
        name = item.path.name
        if "candidate" in df.columns:
            row = df[df["candidate"] == name]
            if row.empty:
                row = df.head(1)
        else:
            row = df.head(1)
        record = row.iloc[0].to_dict()
        record.update({"label": item.label, "source": item.source, "verdict": item.verdict, "role": item.role})
        rows.append(record)
    return pd.DataFrame(rows)


def _comparison_csv_for(path: Path) -> Path:
    candidates = [path.parent / "candidate_comparison.csv", path.parent / "metrics.csv"]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"No metrics CSV found for {path}")


def _load_aligned(path: Path) -> pd.DataFrame:
    aligned_path = path / "aligned_strategy_spy.csv"
    if not aligned_path.exists():
        raise FileNotFoundError(aligned_path)
    df = pd.read_csv(aligned_path, parse_dates=["date"]).set_index("date").sort_index()
    return df[["strategy_equity", "strategy_return", "spy_equity", "spy_return"]].dropna()


def _first_spy(aligned: dict[str, pd.DataFrame]) -> pd.Series:
    frame = next(iter(aligned.values()))
    return frame["spy_equity"] / frame["spy_equity"].iloc[0]


def _plot_equity(aligned: dict[str, pd.DataFrame], spy: pd.Series, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    for label, df in aligned.items():
        equity = df["strategy_equity"] / df["strategy_equity"].iloc[0]
        ax.plot(equity.index, equity.values, label=label, linewidth=1.3)
    ax.plot(spy.index, spy.values, label="SPY buy & hold", color="black", linestyle="--", linewidth=1.8)
    ax.set_yscale("log")
    ax.set_title("Weekly Momentum Top-K Equity vs SPY")
    ax.set_ylabel("Growth of $1, log scale")
    ax.grid(True, which="both", alpha=0.30)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_relative(aligned: dict[str, pd.DataFrame], spy: pd.Series, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    for label, df in aligned.items():
        equity = df["strategy_equity"] / df["strategy_equity"].iloc[0]
        bench = df["spy_equity"] / df["spy_equity"].iloc[0]
        ratio = equity / bench
        ax.plot(ratio.index, ratio.values, label=label, linewidth=1.3)
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1.0)
    ax.set_yscale("log")
    ax.set_title("Weekly Momentum Top-K Relative Equity to SPY")
    ax.set_ylabel("Strategy / SPY")
    ax.grid(True, which="both", alpha=0.30)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_drawdown(aligned: dict[str, pd.DataFrame], spy: pd.Series, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    for label, df in aligned.items():
        equity = df["strategy_equity"] / df["strategy_equity"].iloc[0]
        drawdown = equity / equity.cummax() - 1.0
        ax.plot(drawdown.index, drawdown.values * 100.0, label=label, linewidth=1.2)
    spy_dd = spy / spy.cummax() - 1.0
    ax.plot(spy_dd.index, spy_dd.values * 100.0, label="SPY buy & hold", color="black", linestyle="--", linewidth=1.8)
    ax.set_title("Weekly Momentum Top-K Drawdown vs SPY")
    ax.set_ylabel("Drawdown (%)")
    ax.grid(True, alpha=0.30)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_rolling_cagr(aligned: dict[str, pd.DataFrame], spy: pd.Series, out_path: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharex=True)
    for ax, years in zip(axes.flatten(), [1, 3, 5, 10], strict=True):
        window = years * 252
        for label, df in aligned.items():
            equity = df["strategy_equity"] / df["strategy_equity"].iloc[0]
            rolling = (equity / equity.shift(window)) ** (1.0 / years) - 1.0
            ax.plot(rolling.index, rolling.values * 100.0, label=label, linewidth=1.0)
        spy_roll = (spy / spy.shift(window)) ** (1.0 / years) - 1.0
        ax.plot(spy_roll.index, spy_roll.values * 100.0, label="SPY", color="black", linestyle="--", linewidth=1.4)
        ax.axhline(0.0, color="black", linewidth=0.7, alpha=0.4)
        ax.set_title(f"{years}y rolling CAGR")
        ax.set_ylabel("CAGR (%)")
        ax.grid(True, alpha=0.25)
    axes[0, 0].legend(fontsize=7)
    fig.suptitle("Weekly Momentum Top-K Rolling CAGR vs SPY")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_metric_bars(metrics: pd.DataFrame, out_path: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    labels = metrics["label"].tolist()
    for ax, column, title in zip(axes, ["cagr", "mdd", "sharpe"], ["CAGR", "MDD", "Sharpe"], strict=True):
        values = metrics[column].astype(float).to_numpy()
        scale = 100.0 if column in {"cagr", "mdd"} else 1.0
        ax.barh(labels, values * scale)
        ax.set_title(title)
        ax.grid(True, axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_gate_matrix(metrics: pd.DataFrame, out_path: Path) -> None:
    gate_cols = ["dsr_pass", "bootstrap_pass", "oos_pass", "pbo_family_pass"]
    matrix = []
    for _, row in metrics.iterrows():
        matrix.append([_gate_value(row.get(col)) for col in gate_cols])
    data = np.array(matrix, dtype=float)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.imshow(data, cmap="RdYlGn", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(gate_cols)), ["DSR", "Bootstrap", "OOS", "PBO family"])
    ax.set_yticks(range(len(metrics)), metrics["label"].tolist())
    ax.set_title("Gate Matrix (green=pass, red=fail, gray=n/a)")
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            text = "n/a" if data[i, j] == 0 else ("pass" if data[i, j] > 0 else "fail")
            ax.text(j, i, text, ha="center", va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _gate_value(value: object) -> int:
    if isinstance(value, bool):
        return 1 if value else -1
    if pd.isna(value):
        return 0
    text = str(value).lower()
    if text in {"true", "pass", "passed"}:
        return 1
    if text in {"false", "fail", "failed"}:
        return -1
    return 0


def _build_report(items: list[ComparedStrategy], metrics: pd.DataFrame, plots_dir: Path) -> str:
    top_table = metrics[
        [
            "label",
            "source",
            "verdict",
            "cagr",
            "mdd",
            "sharpe",
            "spy_cagr",
            "dsr_p_value",
            "oos_positive_windows",
            "oos_windows",
            "bootstrap_cagr_ci_low_0p1pct",
            "cost10bps_tax_cagr",
        ]
    ].copy()
    for column in ["cagr", "mdd", "spy_cagr", "bootstrap_cagr_ci_low_0p1pct", "cost10bps_tax_cagr"]:
        top_table[column] = top_table[column].map(_fmt_pct)
    top_table["sharpe"] = top_table["sharpe"].map(_fmt_float)
    top_table["dsr_p_value"] = top_table["dsr_p_value"].map(_fmt_float)
    top_table["OOS positive"] = top_table["oos_positive_windows"].astype(str) + "/" + top_table["oos_windows"].astype(str)
    top_table = top_table.drop(columns=["oos_positive_windows", "oos_windows"])

    inventory = pd.DataFrame(_inventory_rows())
    lines = [
        "# Weekly Momentum Tested Strategy Summary",
        "",
        "## Verdict",
        "",
        "No weekly-momentum variant is deployable. The best current research lead is `lb80/k5/SMA250` over approximate PIT S&P 500 membership, but it fails DSR under the conservative 200-trial penalty and still depends on imperfect PIT/delisted coverage `[advances_fin_ml, p.273-275]`.",
        "",
        "The study should pause broad sweeping. The next useful action is paid survivorship-free/PIT data or a delisting-aware reconstruction, then rerunning only the frozen `lb80/k5/SMA200-250` candidates `[advances_fin_ml, p.208-211]`.",
        "",
        "## What Was Tested",
        "",
        inventory.to_markdown(index=False),
        "",
        f"## Top-{len(items)} Decision-Relevant Comparison",
        "",
        "These are not simply the highest-CAGR rows. They include the current leads, the prior promoted lead, dynamic-selection controls and rejected high-CAGR controls so the final conclusion is auditable.",
        "",
        top_table.to_markdown(index=False),
        "",
        "## Plots",
        "",
        f"![Top-K equity vs SPY]({_rel(plots_dir / 'topk_equity_vs_spy.png')})",
        "",
        f"![Top-K relative equity to SPY]({_rel(plots_dir / 'topk_equity_over_spy.png')})",
        "",
        f"![Top-K drawdown vs SPY]({_rel(plots_dir / 'topk_drawdown_vs_spy.png')})",
        "",
        f"![Top-K rolling CAGR]({_rel(plots_dir / 'topk_rolling_cagr_1_3_5_10y.png')})",
        "",
        f"![Top-K metric bars]({_rel(plots_dir / 'topk_metric_bars.png')})",
        "",
        f"![Top-K gate matrix]({_rel(plots_dir / 'topk_gate_matrix.png')})",
        "",
        "## Strategy Notes",
        "",
    ]
    for item in items:
        lines.append(f"- `{item.label}`: {item.role} Source: `{item.path}`.")
    lines.extend(
        [
            "",
            "## Caveats",
            "",
            "- Approximate PIT S&P membership is a robustness improvement, not a survivorship-free price feed.",
            "- Current-membership and all-stocks controls remain biased by missing delisted/renamed securities.",
            "- Rolling-window wins are overlapping samples, not independent evidence.",
            "- Tax stress is a proxy based on annual DARF and fixed transaction costs; live brokerage mechanics are not modeled in full.",
            "- ETF replication did not inherit the stock signal edge and needs a separate ETF-specific design.",
            "",
            "## Source Reports",
            "",
            "- `studies/weekly_momentum/STUDY_REPORT.md`",
            "- `studies/weekly_momentum/DEPLOY_CANDIDATES.md`",
            "- `studies/weekly_momentum/deploy_candidates/CANDIDATE_VALIDATION_REPORT.md`",
            "- `studies/weekly_momentum/PHASE2_REPORT.md`",
            "- `studies/weekly_momentum/PHASE3_REPORT.md`",
            "- `studies/weekly_momentum/phase3/pit_coverage_audit/PIT_COVERAGE_AUDIT.md`",
            "- `studies/weekly_momentum/phase3/lb80_k5_sma250_deep_dive/DEEP_DIVE_REPORT.md`",
            "- `studies/weekly_momentum/ETF_STUDY_REPORT.md`",
            "",
        ]
    )
    return "\n".join(lines)


def _inventory_rows() -> list[dict[str, str]]:
    return [
        {
            "stage": "Initial stocks/ETFs",
            "scope": "4-day weekly momentum, top-1/top-5, cash/defensive, SMA filter",
            "result": "Stocks looked promising; ETFs weak versus SPY.",
            "artifact": "`STUDY_REPORT.md`, `ETF_STUDY_REPORT.md`",
        },
        {
            "stage": "Controlled sweeps",
            "scope": "200 configs each for current S&P 500 and full stock cache",
            "result": "High current-membership CAGR, but not honest enough for promotion.",
            "artifact": "`sweeps/stocks/*_controlled/`",
        },
        {
            "stage": "Controlled walk-forward",
            "scope": "3y train / 1y test dynamic selection",
            "result": "Attractive before PIT; later rejected under PIT.",
            "artifact": "`walk_forward/stocks_*_controlled/`",
        },
        {
            "stage": "Candidate validation",
            "scope": "Fixed aggressive/balanced plus dynamic WF controls",
            "result": "Costs, tax, PBO, DSR and bootstrap added; all remain research-only.",
            "artifact": "`deploy_candidates/`",
        },
        {
            "stage": "Phase 2 neighborhood",
            "scope": "Fixed-aggressive local sweep and all-stock liquidity filters",
            "result": "Moved robust island toward `lb80/k5/SMA200-250`; all-stocks failed PBO/DSR.",
            "artifact": "`PHASE2_REPORT.md`",
        },
        {
            "stage": "Phase 3 PIT approximation",
            "scope": "Wikipedia selected-change S&P 500 membership at signal time",
            "result": "Original lead weakened; `lb80/k5/SMA200-250` survived best but failed DSR.",
            "artifact": "`PHASE3_REPORT.md`",
        },
        {
            "stage": "Deep dive",
            "scope": "DSR decomposition and all possible 1/3/5/10/15/20y entry windows",
            "result": "Standalone PSR is strong; DSR fails once 50+ trials are charged.",
            "artifact": "`phase3/lb80_k5_sma250_deep_dive/`",
        },
    ]


def _fmt_pct(value: object) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if not np.isfinite(number):
        return "n/a"
    return f"{number:.2%}"


def _fmt_float(value: object) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if not np.isfinite(number):
        return "n/a"
    return f"{number:.3f}"


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
