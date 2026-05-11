#!/usr/bin/env python3
"""Generate the consolidated post-close loop report.

The report compares the best config from loop iterations 001-010 against the
closed-study T3d-K2 benchmark. Relative-equity and rolling-window diagnostics
are used as robustness views, consistent with benchmark-relative evaluation and
multiple-testing caution [advances_fin_ml, p.208-211], [advances_fin_ml,
p.222-223].
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
LOOP_DIR = STUDY / "runs/post_close"
OUT_DIR = LOOP_DIR / "summary_plots"
REPORT_PATH = LOOP_DIR / "LOOP_10_ITER_REPORT.md"
BENCHMARK_RETURNS = (
    STUDY
    / "runs/original"
    / "022-2026-05-06-T3d-extended-grid"
    / "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz_strategy_returns.csv"
)
BENCHMARK_SORTINO = 1.3246
BEATS_THRESHOLD = 1.3746


@dataclass
class IterSummary:
    iter_id: str
    n: int
    slug: str
    hypothesis: str
    citation: str
    best_config: str
    best_score: float
    best_tier: str
    sortino: float
    edge: float
    beats_winner: bool
    winner_conditions_met: bool
    pct_above: float
    pbo: float | None
    dsr_cumulative: float | None
    g5_fwd_sharpe: float | None
    cagr: float | None
    mdd: float | None
    sharpe: float | None
    crisis_count: int | None
    returns_path: Path


def _read_returns(path: Path) -> pd.Series:
    df = pd.read_csv(path, parse_dates=["date"])
    ret_col = "return" if "return" in df.columns else "ret"
    s = df.set_index("date")[ret_col].astype(float).sort_index()
    return s.loc[~s.index.duplicated(keep="last")]


def _equity(returns: pd.Series) -> pd.Series:
    return (1.0 + returns.fillna(0.0)).cumprod()


def _result_for_best(verdict: dict) -> dict:
    best = verdict["best_config"]
    for result in verdict.get("results", []):
        if result.get("config_name") == best or result.get("name") == best:
            return result
    return {}


def _load_summaries() -> list[IterSummary]:
    rows: list[IterSummary] = []
    for verdict_path in sorted(LOOP_DIR.glob("[0-9][0-9][0-9]-*/verdict.json")):
        iter_dir = verdict_path.parent
        verdict = json.loads(verdict_path.read_text())
        best_config = verdict["best_config"]
        result = _result_for_best(verdict)
        metrics = (result.get("metrics_gross") or {}).get("lh_56y", {})
        gates = result.get("gates") or {}
        crisis = result.get("crisis_beats_benchmark") or {}
        score = result.get("score_breakdown") or {}
        returns_path = iter_dir / f"{best_config}_strategy_returns.csv"
        if not returns_path.exists():
            raise FileNotFoundError(f"Missing returns for {verdict['iter']}: {returns_path}")
        parts = verdict["iter"].split("-", 4)
        rows.append(
            IterSummary(
                iter_id=verdict["iter"],
                n=int(parts[0]),
                slug=parts[4] if len(parts) >= 5 else verdict["iter"],
                hypothesis=str(verdict.get("hypothesis", "")),
                citation=str(verdict.get("primary_citation", "")),
                best_config=best_config,
                best_score=float(verdict.get("best_score", np.nan)),
                best_tier=str(verdict.get("best_tier", "")),
                sortino=float(verdict.get("sortino_lh56y", metrics.get("sortino", np.nan))),
                edge=float(verdict.get("sortino_edge_vs_winner", np.nan)),
                beats_winner=bool(verdict.get("beats_winner", False)),
                winner_conditions_met=bool(verdict.get("winner_conditions_met", score.get("winner_conditions_met", False))),
                pct_above=float(verdict.get("pct_time_above_benchmark_lh56y", metrics.get("pct_time_above_benchmark", np.nan))),
                pbo=float(gates["g1_pbo"]) if "g1_pbo" in gates else None,
                dsr_cumulative=float(gates["g2_dsr_p_cumulative"]) if "g2_dsr_p_cumulative" in gates else None,
                g5_fwd_sharpe=float(gates["g5_fwd_post2020_sharpe"]) if "g5_fwd_post2020_sharpe" in gates else None,
                cagr=float(metrics["cagr"]) if "cagr" in metrics else None,
                mdd=float(metrics["mdd"]) if "mdd" in metrics else None,
                sharpe=float(metrics["sharpe"]) if "sharpe" in metrics else None,
                crisis_count=sum(1 for v in crisis.values() if v) if crisis else None,
                returns_path=returns_path,
            )
        )
    return rows


def _rolling_window_stats(candidate: pd.Series, benchmark: pd.Series, years: int) -> tuple[float, float, float]:
    joined = pd.concat([candidate, benchmark], axis=1, join="inner").dropna()
    joined.columns = ["candidate", "benchmark"]
    if joined.empty:
        return float("nan"), float("nan"), float("nan")
    window = int(252 * years)
    if len(joined) < window:
        return float("nan"), float("nan"), float("nan")
    cand_eq = _equity(joined["candidate"])
    bench_eq = _equity(joined["benchmark"])
    cand_ratio = cand_eq / cand_eq.shift(window)
    bench_ratio = bench_eq / bench_eq.shift(window)
    end_ratio = (cand_ratio / bench_ratio).dropna()
    if end_ratio.empty:
        return float("nan"), float("nan"), float("nan")
    return float(end_ratio.mean()), float((end_ratio > 1.0).mean()), float(end_ratio.min())


def _plot_performance(rows: list[IterSummary]) -> None:
    df = pd.DataFrame([r.__dict__ for r in rows]).sort_values("n")
    fig, ax1 = plt.subplots(figsize=(12, 6))
    colors = ["#2ca02c" if b else "#7f7f7f" for b in df["beats_winner"]]
    ax1.bar(df["n"], df["sortino"], color=colors, alpha=0.78, label="Best Sortino per iter")
    ax1.axhline(BENCHMARK_SORTINO, color="#d62728", linestyle="--", linewidth=1.4, label="T3d-K2 Sortino 1.3246")
    ax1.axhline(BEATS_THRESHOLD, color="#9467bd", linestyle=":", linewidth=1.6, label="beats threshold 1.3746")
    ax1.set_xlabel("Loop iteration")
    ax1.set_ylabel("Sortino lh_56y")
    ax1.set_xticks(df["n"])
    ax1.grid(axis="y", alpha=0.25)
    ax2 = ax1.twinx()
    ax2.plot(df["n"], df["best_score"], color="#1f77b4", marker="o", linewidth=2, label="Score")
    ax2.axhline(90, color="#1f77b4", linestyle="--", alpha=0.4, label="score 90 deploy bar")
    ax2.set_ylabel("Score")
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="upper left")
    ax1.set_title("Loop best config by iteration: Sortino and score")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "01_iter_performance_sortino_score.png", dpi=160)
    plt.close(fig)


def _plot_equity(rows: list[IterSummary], benchmark: pd.Series) -> dict[int, pd.Series]:
    selected = {r.n: _read_returns(r.returns_path) for r in rows}
    fig, ax = plt.subplots(figsize=(13, 7))
    bench_eq = _equity(benchmark)
    ax.plot(bench_eq.index, bench_eq, color="black", linewidth=2.2, label="T3d-K2 benchmark")
    for r in rows:
        eq = _equity(selected[r.n])
        lw = 2.2 if r.n in {9, 10} else 1.0
        alpha = 0.95 if r.n in {9, 10} else 0.45
        ax.plot(eq.index, eq, linewidth=lw, alpha=alpha, label=f"iter {r.n:03d}")
    ax.set_yscale("log")
    ax.set_title("Equity curves: best config from each loop iter vs T3d-K2")
    ax.set_ylabel("Growth of $1, log scale")
    ax.grid(alpha=0.25)
    ax.legend(ncol=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "02_equity_vs_t3d.png", dpi=160)
    plt.close(fig)
    return selected


def _plot_relative_equity(rows: list[IterSummary], returns_by_iter: dict[int, pd.Series], benchmark: pd.Series) -> None:
    fig, ax = plt.subplots(figsize=(13, 7))
    bench_eq = _equity(benchmark)
    for r in rows:
        joined = pd.concat([_equity(returns_by_iter[r.n]), bench_eq], axis=1, join="inner").dropna()
        joined.columns = ["candidate", "benchmark"]
        rel = joined["candidate"] / joined["benchmark"]
        lw = 2.5 if r.n in {9, 10} else 1.0
        alpha = 0.95 if r.n in {9, 10} else 0.4
        ax.plot(rel.index, rel, linewidth=lw, alpha=alpha, label=f"iter {r.n:03d}")
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1)
    ax.set_yscale("log")
    ax.set_title("Relative equity vs T3d-K2 benchmark")
    ax.set_ylabel("Candidate equity / T3d-K2 equity, log scale")
    ax.grid(alpha=0.25)
    ax.legend(ncol=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "03_relative_equity_vs_t3d.png", dpi=160)
    plt.close(fig)


def _plot_rolling_heatmap(rows: list[IterSummary], returns_by_iter: dict[int, pd.Series], benchmark: pd.Series) -> pd.DataFrame:
    records: list[dict] = []
    for r in rows:
        for years in (1, 3, 5, 10):
            mean_ratio, win_rate, min_ratio = _rolling_window_stats(returns_by_iter[r.n], benchmark, years)
            records.append(
                {
                    "iter": r.n,
                    "years": years,
                    "mean_end_ratio": mean_ratio,
                    "win_rate": win_rate,
                    "min_end_ratio": min_ratio,
                }
            )
    df = pd.DataFrame(records)
    pivot = df.pivot(index="iter", columns="years", values="win_rate").sort_index()
    fig, ax = plt.subplots(figsize=(9, 6))
    im = ax.imshow(pivot.values, aspect="auto", cmap="viridis", vmin=0, vmax=1)
    ax.set_xticks(range(len(pivot.columns)), [f"{c}y" for c in pivot.columns])
    ax.set_yticks(range(len(pivot.index)), [f"{i:03d}" for i in pivot.index])
    ax.set_xlabel("Rolling window length")
    ax.set_ylabel("Loop iteration")
    ax.set_title("Rolling-window win rate vs T3d-K2 (end equity ratio > 1)")
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.values[i, j]
            ax.text(j, i, "" if np.isnan(val) else f"{val:.0%}", ha="center", va="center", color="white" if val < 0.65 else "black", fontsize=8)
    fig.colorbar(im, ax=ax, label="Win rate")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "04_rolling_window_winrate_heatmap.png", dpi=160)
    plt.close(fig)
    return df


def _plot_top_rolling_relative(rows: list[IterSummary], returns_by_iter: dict[int, pd.Series], benchmark: pd.Series) -> None:
    top = [r for r in rows if r.n in {7, 8, 9, 10}]
    bench_eq = _equity(benchmark)
    fig, ax = plt.subplots(figsize=(13, 6))
    window = 252 * 3
    for r in top:
        cand_eq = _equity(returns_by_iter[r.n])
        joined = pd.concat([cand_eq, bench_eq], axis=1, join="inner").dropna()
        joined.columns = ["candidate", "benchmark"]
        cand_ratio = joined["candidate"] / joined["candidate"].shift(window)
        bench_ratio = joined["benchmark"] / joined["benchmark"].shift(window)
        rolling_rel = (cand_ratio / bench_ratio).dropna()
        ax.plot(rolling_rel.index, rolling_rel, linewidth=2, label=f"iter {r.n:03d}")
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1)
    ax.set_title("3-year rolling end-equity ratio vs T3d-K2 (top compound iters)")
    ax.set_ylabel("3y candidate return / 3y T3d-K2 return")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "05_top_iters_rolling_3y_relative.png", dpi=160)
    plt.close(fig)


def _fmt_pct(x: float | None) -> str:
    if x is None or not np.isfinite(x):
        return "n/a"
    return f"{x * 100:.2f}%"


def _fmt_num(x: float | None, digits: int = 3) -> str:
    if x is None or not np.isfinite(x):
        return "n/a"
    return f"{x:.{digits}f}"


def _write_report(rows: list[IterSummary], rolling: pd.DataFrame) -> None:
    best = max(rows, key=lambda r: r.sortino)
    beaters = [r for r in rows if r.beats_winner]
    lines: list[str] = []
    lines.extend(
        [
            "# letf_rotation_hunt — Post-Close Loop 001-010 Report",
            "",
            "## TL;DR",
            "",
            f"- **Yes, the loop found strategies better than the closed-study T3d-K2 winner under the frozen `beats_winner` test.** Iters 009 and 010 cleared `sortino_lh56y > 1.3746`, `winner_conditions_met=True`, and `pct_time_above_benchmark_lh56y >= 0.95`.",
            f"- **Best result:** iter {best.n:03d} `{best.slug}` with Sortino_lh56y **{best.sortino:.4f}**, edge **{best.edge:+.4f}** vs T3d-K2 Sortino 1.3246, score **{best.best_score:.1f}**, PBO **{_fmt_num(best.pbo, 3)}**, and `beats_winner={str(best.beats_winner).lower()}`.",
            "- **Not deploy-authorized:** score is still below the loop's 90-point public active-hunt/deploy escalation bar; mandate §1 remains 100% Plano C. This is a research beater, not an automatic capital allocation change.",
            "- The decisive mechanism was not a single tweak: it was **compound structural diversity** — basket3 inverse-vol ON leg + bond-rate-vol OFF override + master/graded scope. This is exactly why the PBO finally dropped below 0.5 after iter 009 [advances_fin_ml, p.208-211].",
            "- DSR accounting uses global trials starting from N=426 and ending at N=486, per loop protocol [advances_fin_ml, p.222-223].",
            "",
            "## Plots",
            "",
            "![Iter performance](summary_plots/01_iter_performance_sortino_score.png)",
            "",
            "![Equity vs T3d](summary_plots/02_equity_vs_t3d.png)",
            "",
            "![Relative equity vs T3d](summary_plots/03_relative_equity_vs_t3d.png)",
            "",
            "![Rolling window heatmap](summary_plots/04_rolling_window_winrate_heatmap.png)",
            "",
            "![Top rolling relative](summary_plots/05_top_iters_rolling_3y_relative.png)",
            "",
            "## Iteration Summary",
            "",
            "| Iter | Hypothesis slug | Best Sortino | Edge vs T3d | Score | PBO | DSR p_cum | G5 FWD Sharpe | Crisis | beats_winner | Lesson |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|:---:|---|",
        ]
    )
    lessons = {
        1: "OFF yield curve helped little; 2022 was mostly ON-leg damage.",
        2: "Drawdown kill-switch was too late and suppressed rallies.",
        3: "Calendar veto marginally helped but could not solve 2022.",
        4: "Stock-bond correlation gate was redundant with trend signal.",
        5: "Basket3 inverse-vol ON leg gave the first positive edge.",
        6: "Bond rate-vol OFF override improved post-2020 universally.",
        7: "Combining iter 005+006 was super-additive, but PBO barely failed.",
        8: "Parametric expansion did not improve PBO; structure matters.",
        9: "Master-scope structural diversity cracked PBO and produced first beater.",
        10: "Graded master bridge improved Sortino and 2022 rescue while preserving PBO.",
    }
    for r in rows:
        lines.append(
            f"| {r.n:03d} | `{r.slug}` | {r.sortino:.4f} | {r.edge:+.4f} | {r.best_score:.1f} | {_fmt_num(r.pbo, 3)} | {_fmt_num(r.dsr_cumulative, 4)} | {_fmt_num(r.g5_fwd_sharpe, 3)} | {r.crisis_count if r.crisis_count is not None else 'n/a'}/4 | {'Y' if r.beats_winner else 'N'} | {lessons.get(r.n, '')} |"
        )
    lines.extend(
        [
            "",
            "## Beater Verdict",
            "",
            f"The loop found **{len(beaters)} best-config beaters by iteration-level winner**: " + ", ".join(f"iter {r.n:03d}" for r in beaters) + ".",
            "",
            "Strictly, iter 009 produced the first `beats_winner=true` configs, and iter 010 produced the best overall config. The best config is:",
            "",
            f"- Iter: `{best.iter_id}`",
            f"- Config: `{best.best_config}`",
            f"- Sortino_lh56y: `{best.sortino:.4f}` vs T3d-K2 `{BENCHMARK_SORTINO:.4f}`",
            f"- Edge: `{best.edge:+.4f}`",
            f"- Score/tier: `{best.best_score:.1f}` / `{best.best_tier}`",
            f"- PBO: `{_fmt_num(best.pbo, 4)}`",
            f"- DSR p_cumulative: `{_fmt_num(best.dsr_cumulative, 6)}`",
            f"- pct_time_above_benchmark_lh56y: `{best.pct_above:.4f}`",
            "",
            "This is better than T3d-K2 as a **research candidate**, but not a mandate override. The score remains below 90, so the conservative next step is iter 011+ validation/consolidation, not deployment.",
            "",
            "## Rolling Window Diagnostics Vs T3d-K2",
            "",
            "Values below are based on best-config daily returns per iter against the closed-study T3d-K2 return stream. `win_rate` means rolling end-equity ratio > 1.",
            "",
            "| Iter | 1y win | 3y win | 5y win | 10y win | 3y mean ratio | 3y min ratio |",
            "|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for r in rows:
        sub = rolling[rolling["iter"] == r.n].set_index("years")
        def val(years: int, col: str) -> float:
            return float(sub.loc[years, col]) if years in sub.index else float("nan")
        lines.append(
            f"| {r.n:03d} | {_fmt_pct(val(1, 'win_rate'))} | {_fmt_pct(val(3, 'win_rate'))} | {_fmt_pct(val(5, 'win_rate'))} | {_fmt_pct(val(10, 'win_rate'))} | {_fmt_num(val(3, 'mean_end_ratio'), 3)}x | {_fmt_num(val(3, 'min_end_ratio'), 3)}x |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The loop path was informative: the first four attempts showed that simple gates around the original T3d signal did not solve the remaining weakness. Iter 005 found useful ON-leg diversification; iter 006 found useful bond-rate-vol OFF protection; iter 007 showed the combination was super-additive but still had PBO as a blocker; iter 009 changed the scope structure enough to pass PBO; iter 010 refined that scope into a graded bridge and became the best result.",
            "",
            "The practical answer is therefore: **yes, we found something better than T3d-K2 inside this research loop**, but the result should be treated as a new incumbent research candidate requiring follow-up validation rather than as a live allocation decision.",
            "",
            "## Next Work",
            "",
            "1. Run iter 011+ around the graded bridge family with strict config budget and global DSR accounting.",
            "2. Recompute cross-library agreement and independent implementation parity for iter 010 before any public promotion.",
            "3. Add a dedicated report comparing iter 010 vs T3d-K2 by crisis windows, turnover, tax drag and execution assumptions.",
            "4. Keep mandate §1 unchanged unless the user explicitly requests a mandate §7 override review.",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = _load_summaries()
    if len(rows) != 10:
        raise RuntimeError(f"Expected 10 loop iterations, found {len(rows)}")
    benchmark = _read_returns(BENCHMARK_RETURNS)
    _plot_performance(rows)
    returns_by_iter = _plot_equity(rows, benchmark)
    _plot_relative_equity(rows, returns_by_iter, benchmark)
    rolling = _plot_rolling_heatmap(rows, returns_by_iter, benchmark)
    _plot_top_rolling_relative(rows, returns_by_iter, benchmark)
    rolling.to_csv(LOOP_DIR / "loop_001_010_rolling_window_stats.csv", index=False)
    pd.DataFrame([r.__dict__ | {"returns_path": str(r.returns_path)} for r in rows]).to_csv(
        LOOP_DIR / "loop_001_010_summary_table.csv", index=False
    )
    _write_report(rows, rolling)
    print(f"Wrote {REPORT_PATH}")
    print(f"Wrote plots to {OUT_DIR}")


if __name__ == "__main__":
    main()
