#!/usr/bin/env python3
"""Generate post-close loop continuation tables and plots.

This report extends `reports/STUDY_FINAL_REPORT.md` with the autonomous
post-close loop results. It keeps the same benchmark-relative visual convention:
compare the candidate against buy-and-hold SPY/NDX and the prior T3d-K2 winner,
while retaining PBO/DSR controls `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from studies.letf_rotation_hunt.core.data_loader import load_testfolio_series


STUDY = ROOT / "studies" / "letf_rotation_hunt"
LOOP_DIR = STUDY / "runs/post_close"
REPORT_DIR = STUDY / "reports" / "post_close_loop"
PLOTS_DIR = REPORT_DIR / "plots"
TABLES_DIR = REPORT_DIR / "tables"

T3D_RETURNS = (
    STUDY
    / "runs/original"
    / "022-2026-05-06-T3d-extended-grid"
    / "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz_strategy_returns.csv"
)
NEW_WINNER_ITER = "030-2026-05-10-tcrash-scan-lrs120-rearmonly"
NEW_WINNER_CONFIG = "qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T35D60_unclrs120"
ITER027_CONFIG = "qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T40D60_unclrs120"
T3D_SORTINO = 1.3246
T3D_CAGR = 0.3108
BEATS_THRESHOLD = 1.3746


@dataclass
class IterRow:
    n: int
    iter_id: str
    slug: str
    best_config: str
    sortino: float
    cagr: float
    sharpe: float
    mdd: float
    pbo: float
    dsr_global: float
    score: float
    tier: str
    beats_winner: bool
    phase3: bool
    phase4: bool
    strict_superset: bool
    terminal_ratio_vs_t3d: float
    returns_path: Path | None


def read_returns(path: Path) -> pd.Series:
    df = pd.read_csv(path, parse_dates=["date"])
    col = "return" if "return" in df.columns else "ret"
    return df.set_index("date")[col].astype(float).sort_index()


def equity(returns: pd.Series) -> pd.Series:
    return (1.0 + returns.fillna(0.0)).cumprod()


def max_drawdown(eq: pd.Series) -> pd.Series:
    return eq / eq.cummax() - 1.0


def best_result(verdict: dict) -> dict:
    best = verdict.get("best_config")
    for result in verdict.get("results", []):
        if result.get("config_name") == best:
            return result
    return {}


def metric_from(result: dict, verdict: dict, key: str, default: float = np.nan) -> float:
    metrics = (result.get("metrics_gross") or {}).get("lh_56y", {})
    if key == "cagr":
        return float(verdict.get("cagr_lh56y", metrics.get("cagr", default)))
    if key == "sortino":
        return float(verdict.get("sortino_lh56y", metrics.get("sortino", default)))
    return float(metrics.get(key, default))


def load_iter_rows() -> list[IterRow]:
    t3d = read_returns(T3D_RETURNS)
    rows: list[IterRow] = []
    for n in range(1, 31):
        verdict_path = next(LOOP_DIR.glob(f"{n:03d}-*/verdict.json"))
        iter_dir = verdict_path.parent
        verdict = json.loads(verdict_path.read_text())
        result = best_result(verdict)
        gates = result.get("gates") or {}
        returns_path = iter_dir / f"{verdict['best_config']}_strategy_returns.csv"
        baseline_path = next(iter_dir.glob("*baseline*qld_zroz_strategy_returns.csv"), T3D_RETURNS)
        baseline_eq = equity(read_returns(baseline_path))
        terminal_ratio = np.nan
        if returns_path.exists():
            joined = pd.concat([equity(read_returns(returns_path)), baseline_eq], axis=1, join="inner").dropna()
            joined.columns = ["candidate", "t3d"]
            terminal_ratio = float(joined["candidate"].iloc[-1] / joined["t3d"].iloc[-1])
        parts = verdict["iter"].split("-", 4)
        rows.append(
            IterRow(
                n=n,
                iter_id=verdict["iter"],
                slug=parts[4] if len(parts) > 4 else verdict["iter"],
                best_config=verdict.get("best_config", ""),
                sortino=metric_from(result, verdict, "sortino"),
                cagr=metric_from(result, verdict, "cagr"),
                sharpe=metric_from(result, verdict, "sharpe"),
                mdd=metric_from(result, verdict, "mdd"),
                pbo=float(gates.get("g1_pbo", np.nan)),
                dsr_global=float(gates.get("g2_dsr_p_cumulative", gates.get("g2_dsr_global", np.nan))),
                score=float(verdict.get("best_score", np.nan)),
                tier=str(verdict.get("best_tier", "")),
                beats_winner=bool(verdict.get("beats_winner", False)),
                phase3=bool(verdict.get("phase3_performance_candidate", False)),
                phase4=bool(verdict.get("phase4_anchor_improved", False)),
                strict_superset=bool(verdict.get("strict_superset", False)),
                terminal_ratio_vs_t3d=terminal_ratio,
                returns_path=returns_path if returns_path.exists() else None,
            )
        )
    return rows


def rolling_win_rate(candidate: pd.Series, benchmark: pd.Series, years: int) -> tuple[float, float, float]:
    joined = pd.concat([candidate, benchmark], axis=1, join="inner").dropna()
    joined.columns = ["candidate", "benchmark"]
    window = years * 252
    if len(joined) <= window:
        return np.nan, np.nan, np.nan
    ceq = equity(joined["candidate"])
    beq = equity(joined["benchmark"])
    ratio = ((ceq / ceq.shift(window)) / (beq / beq.shift(window))).dropna()
    if ratio.empty:
        return np.nan, np.nan, np.nan
    return float((ratio > 1.0).mean()), float(ratio.mean()), float(ratio.min())


def load_benchmarks() -> dict[str, pd.Series]:
    t3d = read_returns(T3D_RETURNS)
    spy = load_testfolio_series("SPYSIM").pct_change().dropna()
    ndx = load_testfolio_series("QQQSIM").pct_change().dropna()
    return {"T3d-K2": t3d, "SPY buy&hold": spy, "NDX/QQQ buy&hold": ndx}


def save_summary_tables(rows: list[IterRow], benchmarks: dict[str, pd.Series]) -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame([r.__dict__ for r in rows])
    df = df.drop(columns=["returns_path"])
    df.to_csv(TABLES_DIR / "post_close_loop_001_030_summary.csv", index=False)

    candidate = read_returns(LOOP_DIR / NEW_WINNER_ITER / f"{NEW_WINNER_CONFIG}_strategy_returns.csv")
    records = []
    for name, bench in benchmarks.items():
        for years in (1, 3, 5, 10):
            win, mean_ratio, min_ratio = rolling_win_rate(candidate, bench, years)
            records.append(
                {
                    "candidate": "iter030_T35D60_LRS120",
                    "benchmark": name,
                    "window_years": years,
                    "win_rate": win,
                    "mean_end_ratio": mean_ratio,
                    "min_end_ratio": min_ratio,
                }
            )
    pd.DataFrame(records).to_csv(TABLES_DIR / "iter030_rolling_win_rates.csv", index=False)


def plot_loop_evolution(rows: list[IterRow]) -> None:
    df = pd.DataFrame([r.__dict__ for r in rows])
    fig, ax1 = plt.subplots(figsize=(14, 7))
    colors = ["#2ca02c" if v else "#9e9e9e" for v in df["strict_superset"]]
    ax1.bar(df["n"], df["cagr"] * 100, color=colors, alpha=0.75, label="Best-config CAGR")
    ax1.axhline(T3D_CAGR * 100, color="#d62728", linestyle="--", label="T3d-K2 CAGR 31.08%")
    ax1.set_xlabel("Post-close loop iteration")
    ax1.set_ylabel("CAGR lh_56y (%)")
    ax1.set_xticks(df["n"])
    ax1.grid(axis="y", alpha=0.25)
    ax2 = ax1.twinx()
    ax2.plot(df["n"], df["sortino"], color="#1f77b4", marker="o", linewidth=1.8, label="Best-config Sortino")
    ax2.axhline(T3D_SORTINO, color="#1f77b4", linestyle="--", alpha=0.5, label="T3d-K2 Sortino")
    ax2.axhline(BEATS_THRESHOLD, color="#9467bd", linestyle=":", alpha=0.8, label="Beater threshold")
    ax2.set_ylabel("Sortino lh_56y")
    ax1.set_title("Post-close loop 001-030: CAGR expansion with Sortino guardrail")
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="upper left")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "01_loop_001_030_cagr_sortino.png", dpi=160)
    plt.close(fig)


def plot_equity_benchmarks(benchmarks: dict[str, pd.Series]) -> None:
    new_winner = read_returns(LOOP_DIR / NEW_WINNER_ITER / f"{NEW_WINNER_CONFIG}_strategy_returns.csv")
    iter027 = read_returns(LOOP_DIR / NEW_WINNER_ITER / f"{ITER027_CONFIG}_strategy_returns.csv")
    series = {
        "iter030 T35D60 + LRS1.20": new_winner,
        "iter027 T40D60 + LRS1.20": iter027,
        **benchmarks,
    }
    colors = {
        "iter030 T35D60 + LRS1.20": "#2ca02c",
        "iter027 T40D60 + LRS1.20": "#ff7f0e",
        "T3d-K2": "#000000",
        "SPY buy&hold": "#7f7f7f",
        "NDX/QQQ buy&hold": "#1f77b4",
    }
    fig, ax = plt.subplots(figsize=(14, 8))
    for name, returns in series.items():
        eq = equity(returns)
        lw = 2.8 if name.startswith("iter030") else (2.1 if name.startswith("iter027") else 1.7)
        ax.plot(eq.index, eq, label=name, color=colors[name], linewidth=lw)
    ax.set_yscale("log")
    ax.set_title("Post-close winner vs T3d-K2 and buy-hold benchmarks")
    ax.set_ylabel("Growth of $1, log scale")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "02_equity_vs_t3d_spy_ndx.png", dpi=160)
    plt.close(fig)


def plot_relative_benchmarks(benchmarks: dict[str, pd.Series]) -> None:
    candidate = read_returns(LOOP_DIR / NEW_WINNER_ITER / f"{NEW_WINNER_CONFIG}_strategy_returns.csv")
    ceq = equity(candidate)
    fig, ax = plt.subplots(figsize=(14, 7))
    for name, bench in benchmarks.items():
        joined = pd.concat([ceq, equity(bench)], axis=1, join="inner").dropna()
        joined.columns = ["candidate", "benchmark"]
        ax.plot(joined.index, joined["candidate"] / joined["benchmark"], linewidth=2.2, label=f"iter030 / {name}")
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1)
    ax.set_yscale("log")
    ax.set_title("Post-close winner relative equity vs benchmarks")
    ax.set_ylabel("Relative equity, log scale")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "03_relative_equity_vs_benchmarks.png", dpi=160)
    plt.close(fig)


def plot_drawdowns(benchmarks: dict[str, pd.Series]) -> None:
    candidate = read_returns(LOOP_DIR / NEW_WINNER_ITER / f"{NEW_WINNER_CONFIG}_strategy_returns.csv")
    iter027 = read_returns(LOOP_DIR / NEW_WINNER_ITER / f"{ITER027_CONFIG}_strategy_returns.csv")
    series = {
        "iter030 T35D60 + LRS1.20": candidate,
        "iter027 T40D60 + LRS1.20": iter027,
        "T3d-K2": benchmarks["T3d-K2"],
        "SPY buy&hold": benchmarks["SPY buy&hold"],
        "NDX/QQQ buy&hold": benchmarks["NDX/QQQ buy&hold"],
    }
    fig, ax = plt.subplots(figsize=(14, 7))
    for name, returns in series.items():
        ax.plot(max_drawdown(equity(returns)).index, max_drawdown(equity(returns)) * 100, label=name, linewidth=2 if name.startswith("iter") else 1.4)
    ax.set_title("Drawdown comparison: winner vs T3d-K2 and buy-hold")
    ax.set_ylabel("Drawdown (%)")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "04_drawdowns_vs_benchmarks.png", dpi=160)
    plt.close(fig)


def plot_phase4_frontiers() -> None:
    lrs = pd.DataFrame(
        [
            {"label": "1.00", "sortino": 1.4176, "cagr": 0.3244, "terminal": 1.516},
            {"label": "1.05", "sortino": 1.4068, "cagr": 0.3343, "terminal": 2.049},
            {"label": "1.10", "sortino": 1.3968, "cagr": 0.3439, "terminal": 2.730},
            {"label": "1.15", "sortino": 1.3874, "cagr": 0.3532, "terminal": 3.610},
            {"label": "1.20", "sortino": 1.3786, "cagr": 0.3622, "terminal": 4.710},
        ]
    )
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(lrs["cagr"] * 100, lrs["sortino"], marker="o", linewidth=2.5, color="#ff7f0e")
    for _, row in lrs.iterrows():
        ax.text(row["cagr"] * 100 + 0.05, row["sortino"], f"LRS{row['label']}")
    ax.axhline(BEATS_THRESHOLD, color="#9467bd", linestyle=":", label="Beater threshold")
    ax.axhline(1.35, color="#7f7f7f", linestyle="--", alpha=0.7, label="Phase 4 floor")
    ax.set_title("Phase 4 LRS magnitude frontier on T40D60 rearm base")
    ax.set_xlabel("CAGR lh_56y (%)")
    ax.set_ylabel("Sortino lh_56y")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "05_lrs_magnitude_frontier.png", dpi=160)
    plt.close(fig)

    tscan = pd.DataFrame(
        [
            {"T": 35, "sortino": 1.3839, "cagr": 0.3668, "terminal": 5.398, "flips": 20},
            {"T": 40, "sortino": 1.3786, "cagr": 0.3622, "terminal": 4.710, "flips": 16},
            {"T": 45, "sortino": 1.3689, "cagr": 0.3577, "terminal": 4.133, "flips": 14},
            {"T": 50, "sortino": 1.3379, "cagr": 0.3427, "terminal": 2.635, "flips": 9},
        ]
    )
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(tscan["T"], tscan["cagr"] * 100, marker="o", linewidth=2.5, color="#2ca02c", label="CAGR")
    ax1.set_xlabel("T_crash minimum prior OFF days")
    ax1.set_ylabel("CAGR lh_56y (%)")
    ax1.grid(alpha=0.25)
    ax2 = ax1.twinx()
    ax2.plot(tscan["T"], tscan["sortino"], marker="s", linewidth=2.0, color="#1f77b4", label="Sortino")
    ax2.axhline(BEATS_THRESHOLD, color="#9467bd", linestyle=":", alpha=0.8, label="Beater threshold")
    ax2.set_ylabel("Sortino lh_56y")
    for _, row in tscan.iterrows():
        ax1.text(row["T"], row["cagr"] * 100 + 0.08, f"{int(row['flips'])} flips", ha="center", fontsize=8)
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="upper right")
    ax1.set_title("Iter 030 T_crash scan: T35 dominates T40/T45/T50")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "06_tcrash_scan_t35_t50.png", dpi=160)
    plt.close(fig)


def plot_rolling_heatmap(benchmarks: dict[str, pd.Series]) -> None:
    candidate = read_returns(LOOP_DIR / NEW_WINNER_ITER / f"{NEW_WINNER_CONFIG}_strategy_returns.csv")
    records = []
    for name, bench in benchmarks.items():
        for years in (1, 3, 5, 10):
            win, _, _ = rolling_win_rate(candidate, bench, years)
            records.append({"benchmark": name, "years": years, "win_rate": win})
    df = pd.DataFrame(records).pivot(index="benchmark", columns="years", values="win_rate")
    fig, ax = plt.subplots(figsize=(8, 4.8))
    im = ax.imshow(df.values, cmap="viridis", aspect="auto", vmin=0, vmax=1)
    ax.set_xticks(range(len(df.columns)), [f"{c}y" for c in df.columns])
    ax.set_yticks(range(len(df.index)), df.index)
    ax.set_title("Iter 030 rolling-window win rate vs benchmarks")
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            val = df.values[i, j]
            ax.text(j, i, "" if np.isnan(val) else f"{val:.0%}", ha="center", va="center", color="white" if val < 0.65 else "black")
    fig.colorbar(im, ax=ax, label="Win rate")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "07_iter030_rolling_winrate_heatmap.png", dpi=160)
    plt.close(fig)


def main() -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_iter_rows()
    benchmarks = load_benchmarks()
    save_summary_tables(rows, benchmarks)
    plot_loop_evolution(rows)
    plot_equity_benchmarks(benchmarks)
    plot_relative_benchmarks(benchmarks)
    plot_drawdowns(benchmarks)
    plot_phase4_frontiers()
    plot_rolling_heatmap(benchmarks)
    print(f"wrote {REPORT_DIR}")


if __name__ == "__main__":
    main()
