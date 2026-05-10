#!/usr/bin/env python3
"""Generate Phase 3 (iters 011-020) performance-first loop report.

Phase 3 prioritizes CAGR, terminal equity and rolling-window performance versus
the frozen T3d-K2 benchmark while keeping PBO/DSR controls in force
[advances_fin_ml, p.208-211], [advances_fin_ml, p.222-223].
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
STUDY = ROOT / "studies" / "letf_rotation_hunt"
LOOP_DIR = STUDY / "loop_iterations"
OUT_DIR = LOOP_DIR / "phase3_plots"
REPORT_PATH = LOOP_DIR / "LOOP_PHASE3_011_020_REPORT.md"
SUMMARY_CSV = LOOP_DIR / "loop_phase3_011_020_summary_table.csv"
ROLLING_CSV = LOOP_DIR / "loop_phase3_011_020_rolling_window_stats.csv"
BENCHMARK_RETURNS = (
    STUDY
    / "iterations"
    / "022-2026-05-06-T3d-extended-grid"
    / "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz_strategy_returns.csv"
)
BENCHMARK_CAGR = 0.3108
BENCHMARK_SORTINO = 1.3246
BEATS_THRESHOLD = 1.3746


@dataclass
class Row:
    iter_id: str
    n: int
    slug: str
    best_config: str
    cagr: float
    cagr_edge: float
    sortino: float
    sortino_edge: float
    sharpe: float | None
    mdd: float | None
    pbo: float | None
    dsr_cumulative: float | None
    score: float
    tier: str
    beats_winner: bool
    phase3: bool
    strict_superset: bool
    novel_strict: bool
    crisis_count: int | None
    terminal_ratio: float
    returns_path: Path


def read_returns(path: Path) -> pd.Series:
    df = pd.read_csv(path, parse_dates=["date"])
    col = "return" if "return" in df.columns else "ret"
    return df.set_index("date")[col].astype(float).sort_index()


def equity(returns: pd.Series) -> pd.Series:
    return (1 + returns.fillna(0)).cumprod()


def best_result(verdict: dict) -> dict:
    best = verdict["best_config"]
    for result in verdict.get("results", []):
        if result.get("config_name") == best:
            return result
    return {}


def rolling_stats(candidate: pd.Series, benchmark: pd.Series, years: int) -> tuple[float, float, float]:
    joined = pd.concat([candidate, benchmark], axis=1, join="inner").dropna()
    joined.columns = ["candidate", "benchmark"]
    window = years * 252
    if len(joined) < window:
        return float("nan"), float("nan"), float("nan")
    ceq = equity(joined["candidate"])
    beq = equity(joined["benchmark"])
    ratio = ((ceq / ceq.shift(window)) / (beq / beq.shift(window))).dropna()
    if ratio.empty:
        return float("nan"), float("nan"), float("nan")
    return float(ratio.mean()), float((ratio > 1).mean()), float(ratio.min())


def load_rows() -> list[Row]:
    benchmark = read_returns(BENCHMARK_RETURNS)
    beq = equity(benchmark)
    rows: list[Row] = []
    for n in range(11, 21):
        verdict_path = next(LOOP_DIR.glob(f"{n:03d}-*/verdict.json"))
        iter_dir = verdict_path.parent
        verdict = json.loads(verdict_path.read_text())
        result = best_result(verdict)
        metrics = (result.get("metrics_gross") or {}).get("lh_56y", {})
        gates = result.get("gates") or {}
        crisis = result.get("crisis_beats_benchmark") or {}
        returns_path = iter_dir / f"{verdict['best_config']}_strategy_returns.csv"
        candidate = read_returns(returns_path)
        joined = pd.concat([equity(candidate), beq], axis=1, join="inner").dropna()
        joined.columns = ["candidate", "benchmark"]
        terminal_ratio = float(joined["candidate"].iloc[-1] / joined["benchmark"].iloc[-1])
        parts = verdict["iter"].split("-", 4)
        rows.append(
            Row(
                iter_id=verdict["iter"],
                n=n,
                slug=parts[4],
                best_config=verdict["best_config"],
                cagr=float(verdict.get("cagr_lh56y", metrics.get("cagr", np.nan))),
                cagr_edge=float(verdict.get("cagr_edge_vs_winner", metrics.get("cagr", np.nan) - BENCHMARK_CAGR)),
                sortino=float(verdict.get("sortino_lh56y", metrics.get("sortino", np.nan))),
                sortino_edge=float(verdict.get("sortino_edge_vs_winner", np.nan)),
                sharpe=float(metrics["sharpe"]) if "sharpe" in metrics else None,
                mdd=float(metrics["mdd"]) if "mdd" in metrics else None,
                pbo=float(gates["g1_pbo"]) if "g1_pbo" in gates else None,
                dsr_cumulative=float(gates["g2_dsr_p_cumulative"]) if "g2_dsr_p_cumulative" in gates else None,
                score=float(verdict.get("best_score", np.nan)),
                tier=str(verdict.get("best_tier", "")),
                beats_winner=bool(verdict.get("beats_winner", False)),
                phase3=bool(verdict.get("phase3_performance_candidate", False)),
                strict_superset=bool(verdict.get("strict_superset", False)),
                novel_strict=bool(verdict.get("latest_strict_superset_is_novel", verdict.get("strict_superset_is_novel", False))),
                crisis_count=sum(1 for v in crisis.values() if v) if crisis else None,
                terminal_ratio=terminal_ratio,
                returns_path=returns_path,
            )
        )
    return rows


def pct(x: float | None) -> str:
    if x is None or not np.isfinite(x):
        return "n/a"
    return f"{x * 100:.2f}%"


def num(x: float | None, digits: int = 3) -> str:
    if x is None or not np.isfinite(x):
        return "n/a"
    return f"{x:.{digits}f}"


def plot_cagr_sortino(rows: list[Row]) -> None:
    df = pd.DataFrame([r.__dict__ for r in rows])
    fig, ax1 = plt.subplots(figsize=(12, 6))
    colors = ["#2ca02c" if p else "#7f7f7f" for p in df["phase3"]]
    ax1.bar(df["n"], df["cagr"] * 100, color=colors, alpha=0.8, label="CAGR")
    ax1.axhline(BENCHMARK_CAGR * 100, color="#d62728", linestyle="--", label="T3d CAGR 31.08%")
    ax1.set_ylabel("CAGR lh_56y (%)")
    ax1.set_xlabel("Loop iteration")
    ax1.set_xticks(df["n"])
    ax1.grid(axis="y", alpha=0.25)
    ax2 = ax1.twinx()
    ax2.plot(df["n"], df["sortino"], color="#1f77b4", marker="o", linewidth=2, label="Sortino")
    ax2.axhline(BENCHMARK_SORTINO, color="#1f77b4", linestyle="--", alpha=0.45, label="T3d Sortino")
    ax2.axhline(BEATS_THRESHOLD, color="#9467bd", linestyle=":", alpha=0.7, label="Sortino beater threshold")
    ax2.set_ylabel("Sortino lh_56y")
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="upper right")
    ax1.set_title("Phase 3: performance-first CAGR and Sortino")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "01_phase3_cagr_sortino.png", dpi=160)
    plt.close(fig)


def plot_equity(rows: list[Row], benchmark: pd.Series) -> dict[int, pd.Series]:
    returns = {r.n: read_returns(r.returns_path) for r in rows}
    beq = equity(benchmark)
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.plot(beq.index, beq, color="black", linewidth=2.4, label="T3d-K2")
    for r in rows:
        eq = equity(returns[r.n])
        lw = 2.5 if r.n in {12, 17, 20} else 1.1
        alpha = 0.95 if r.n in {12, 17, 20} else 0.45
        ax.plot(eq.index, eq, linewidth=lw, alpha=alpha, label=f"iter {r.n:03d}")
    ax.set_yscale("log")
    ax.set_title("Phase 3 equity curves vs T3d-K2")
    ax.set_ylabel("Growth of $1, log scale")
    ax.grid(alpha=0.25)
    ax.legend(ncol=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "02_phase3_equity_vs_t3d.png", dpi=160)
    plt.close(fig)
    return returns


def plot_relative(rows: list[Row], returns: dict[int, pd.Series], benchmark: pd.Series) -> None:
    beq = equity(benchmark)
    fig, ax = plt.subplots(figsize=(13, 7))
    for r in rows:
        joined = pd.concat([equity(returns[r.n]), beq], axis=1, join="inner").dropna()
        joined.columns = ["candidate", "benchmark"]
        rel = joined["candidate"] / joined["benchmark"]
        lw = 2.5 if r.n in {12, 17, 20} else 1.1
        alpha = 0.95 if r.n in {12, 17, 20} else 0.45
        ax.plot(rel.index, rel, linewidth=lw, alpha=alpha, label=f"iter {r.n:03d}")
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1)
    ax.set_yscale("log")
    ax.set_title("Phase 3 relative equity vs T3d-K2")
    ax.set_ylabel("Candidate / T3d-K2 equity, log scale")
    ax.grid(alpha=0.25)
    ax.legend(ncol=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "03_phase3_relative_equity.png", dpi=160)
    plt.close(fig)


def rolling_table(rows: list[Row], returns: dict[int, pd.Series], benchmark: pd.Series) -> pd.DataFrame:
    records = []
    for r in rows:
        for years in (1, 3, 5, 10):
            mean_ratio, win_rate, min_ratio = rolling_stats(returns[r.n], benchmark, years)
            records.append({"iter": r.n, "years": years, "mean_end_ratio": mean_ratio, "win_rate": win_rate, "min_end_ratio": min_ratio})
    df = pd.DataFrame(records)
    pivot = df.pivot(index="iter", columns="years", values="win_rate")
    fig, ax = plt.subplots(figsize=(9, 6))
    im = ax.imshow(pivot.values, cmap="viridis", aspect="auto", vmin=0, vmax=1)
    ax.set_xticks(range(len(pivot.columns)), [f"{c}y" for c in pivot.columns])
    ax.set_yticks(range(len(pivot.index)), [f"{i:03d}" for i in pivot.index])
    ax.set_title("Phase 3 rolling-window win rate vs T3d-K2")
    ax.set_xlabel("Window")
    ax.set_ylabel("Iteration")
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.values[i, j]
            ax.text(j, i, "" if np.isnan(val) else f"{val:.0%}", ha="center", va="center", color="white" if val < 0.65 else "black", fontsize=8)
    fig.colorbar(im, ax=ax, label="Win rate")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "04_phase3_rolling_winrate_heatmap.png", dpi=160)
    plt.close(fig)
    return df


def plot_scatter(rows: list[Row]) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))
    for r in rows:
        color = "#2ca02c" if r.strict_superset else ("#1f77b4" if r.phase3 else "#7f7f7f")
        marker = "*" if r.n in {17, 20} else "o"
        ax.scatter(r.cagr * 100, r.sortino, s=120 if marker == "*" else 70, color=color, marker=marker)
        ax.text(r.cagr * 100 + 0.08, r.sortino, f"{r.n:03d}", fontsize=8)
    ax.axvline(BENCHMARK_CAGR * 100, color="#d62728", linestyle="--", label="T3d CAGR")
    ax.axhline(BENCHMARK_SORTINO, color="#1f77b4", linestyle="--", label="T3d Sortino")
    ax.axhline(BEATS_THRESHOLD, color="#9467bd", linestyle=":", label="Sortino threshold")
    ax.set_xlabel("CAGR lh_56y (%)")
    ax.set_ylabel("Sortino lh_56y")
    ax.set_title("Phase 3 risk/profit vs performance trade-off")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "05_phase3_cagr_sortino_scatter.png", dpi=160)
    plt.close(fig)


def write_report(rows: list[Row], rolling: pd.DataFrame) -> None:
    highest_cagr = max(rows, key=lambda r: r.cagr)
    strict = [r for r in rows if r.strict_superset]
    novel = [r for r in rows if r.n in {17, 20}]
    best_balanced = max(strict, key=lambda r: (r.cagr, r.sortino)) if strict else highest_cagr
    lines = [
        "# letf_rotation_hunt — Phase 3 Performance Report (iters 011-020)",
        "",
        "## TL;DR",
        "",
        "- Phase 3 addressed the exact issue from iters 009-010: those were safer/Sortino beaters but not better compounders. The new phase explicitly targeted CAGR and terminal equity versus T3d-K2 while preserving PBO/global DSR controls.",
        f"- **Highest CAGR:** iter {highest_cagr.n:03d} `{highest_cagr.slug}` at **{pct(highest_cagr.cagr)}** CAGR, edge **{pct(highest_cagr.cagr_edge)}**, terminal equity **{highest_cagr.terminal_ratio:.2f}x** T3d-K2, Sortino **{highest_cagr.sortino:.4f}**. It is a performance hit but not a Sortino beater.",
        f"- **Best balanced strict-superset:** iter {best_balanced.n:03d} `{best_balanced.slug}` at **{pct(best_balanced.cagr)}** CAGR, Sortino **{best_balanced.sortino:.4f}**, terminal equity **{best_balanced.terminal_ratio:.2f}x**, PBO **{num(best_balanced.pbo)}**.",
        "- **First strict-superset:** iter 012. **First novel non-replica strict-superset:** iter 017. Iter 020 added more novel strict-supersets but did not improve over iter 017's best T40D60 anchor.",
        "- Mandate §1 remains unchanged: 100% Plano C. These are research candidates, not automatic deployment instructions.",
        "",
        "## Plots",
        "",
        "![CAGR and Sortino](phase3_plots/01_phase3_cagr_sortino.png)",
        "",
        "![Equity](phase3_plots/02_phase3_equity_vs_t3d.png)",
        "",
        "![Relative Equity](phase3_plots/03_phase3_relative_equity.png)",
        "",
        "![Rolling Winrate](phase3_plots/04_phase3_rolling_winrate_heatmap.png)",
        "",
        "![CAGR Sortino Scatter](phase3_plots/05_phase3_cagr_sortino_scatter.png)",
        "",
        "## Iteration Table",
        "",
        "| Iter | Slug | CAGR | CAGR edge | Terminal ratio | Sortino | PBO | Score | Phase3 | Strict | Novel strict | Lesson |",
        "|---:|---|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|---|",
    ]
    lessons = {
        11: "TQQQ upgrade restored performance but did not beat Sortino threshold.",
        12: "TQQQ K4 + ratevol OFF created first CAGR+Sortino strict-superset.",
        13: "Triple stack improved risk metrics but PBO failed due parametric clustering.",
        14: "Mechanism diversity restored PBO and unlocked higher Sortino strict-superset.",
        15: "Static equity-tilted baskets could not clear CAGR floor without losing crisis rescue.",
        16: "Dynamic basket switching preserved crisis cushion but failed Phase 3 CAGR.",
        17: "Post-crash rearm produced first new non-replica strict-superset and better rolling performance.",
        18: "Graded rearm was parametric overfit; PBO blew up.",
        19: "SPY realised-vol gate improved PBO diversity but not the best config.",
        20: "MDD-depth gate produced new strict-supersets but did not beat iter 017 anchor.",
    }
    for r in rows:
        lines.append(
            f"| {r.n:03d} | `{r.slug}` | {pct(r.cagr)} | {pct(r.cagr_edge)} | {r.terminal_ratio:.2f}x | {r.sortino:.4f} | {num(r.pbo)} | {r.score:.1f} | {'Y' if r.phase3 else 'N'} | {'Y' if r.strict_superset else 'N'} | {'Y' if r.n in {17, 20} else 'N'} | {lessons[r.n]} |"
        )
    lines += [
        "",
        "## Answer To The Performance Question",
        "",
        "Yes: Phase 3 found strategies that improve performance versus T3d-K2, not just Sortino. Iter 011 is the clearest pure-performance result (36.69% CAGR, 5.42x terminal equity vs T3d-K2), but its Sortino is lower than the T3d threshold. Iter 012 is the first strict-superset: it beats T3d-K2 on CAGR, terminal equity and Sortino threshold simultaneously. Iter 017 is the strongest new non-replica strict-superset, improving CAGR to 32.66%, Sortino to 1.4030, and terminal equity to 1.62x while preserving PBO < 0.5.",
        "",
        "The practical research incumbent after Phase 3 is therefore iter 017's `T40D60` post-crash rearm family, not the safer-but-slower iter 010 g25 bridge. Iter 020 confirms nearby depth-gated variants exist, but the MDD-depth filter does not improve over the iter 017 anchor.",
        "",
        "## Rolling Window Diagnostics",
        "",
        "| Iter | 1y win | 3y win | 5y win | 10y win | 3y mean ratio | 3y min ratio |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        sub = rolling[rolling["iter"] == r.n].set_index("years")
        def val(years: int, col: str) -> float:
            return float(sub.loc[years, col]) if years in sub.index else float("nan")
        lines.append(
            f"| {r.n:03d} | {pct(val(1, 'win_rate'))} | {pct(val(3, 'win_rate'))} | {pct(val(5, 'win_rate'))} | {pct(val(10, 'win_rate'))} | {num(val(3, 'mean_end_ratio'))}x | {num(val(3, 'min_end_ratio'))}x |"
        )
    lines += [
        "",
        "## Next Work",
        "",
        "1. Continue with iter 021 around the T40D60 strict-superset, but avoid narrow parametric clusters that caused iter 018 PBO blow-up.",
        "2. Test T_crash/D_arm with a mechanism-diverse grid, not a pure sweep, to preserve CSCV rank diversity [advances_fin_ml, p.208-211].",
        "3. Run independent implementation/cross-library parity before any mandate §7 discussion.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    benchmark = read_returns(BENCHMARK_RETURNS)
    plot_cagr_sortino(rows)
    returns = plot_equity(rows, benchmark)
    plot_relative(rows, returns, benchmark)
    rolling = rolling_table(rows, returns, benchmark)
    plot_scatter(rows)
    rolling.to_csv(ROLLING_CSV, index=False)
    pd.DataFrame([r.__dict__ | {"returns_path": str(r.returns_path)} for r in rows]).to_csv(SUMMARY_CSV, index=False)
    write_report(rows, rolling)
    print(f"Wrote {REPORT_PATH}")
    print(f"Wrote plots to {OUT_DIR}")


if __name__ == "__main__":
    main()
