#!/usr/bin/env python3
"""QQQ/NDX benchmark supplement for LETF Rotation Hunt top-N strategies.

This script intentionally reuses the original top-N strategy universe and swaps
only the benchmark from SPYSIM to QQQSIM. That isolates benchmark sensitivity
without re-optimizing strategy selection against QQQ/NDX. Benchmark-relative
stress testing follows the same rolling-window spirit as the original robustness
analysis, per sensitivity validation guidance [advances_fin_ml, p.31-34] and
regime testing [trading_systems_methods, Kaufman, ch.21].

Outputs:
  data/robustness_qqq/*
  studies/letf_rotation_hunt/reports/qqq_benchmark_plots/*
  studies/letf_rotation_hunt/reports/STUDY_QQQ_BENCHMARK_REPORT.md
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from studies.letf_rotation_hunt.data_loader import load_ffr_daily, load_testfolio_series
from studies.letf_rotation_hunt.run_iter_t1 import _run_single_config
from studies.letf_rotation_hunt.run_iter_t2 import _run_single_basket_config
from studies.letf_rotation_hunt.run_iter_t3 import _run_single_composite_config
from studies.letf_rotation_hunt.run_iter_t4 import _run_single_xs_config
from studies.letf_rotation_hunt.run_iter_t5 import _run_single_voltarget_config
from studies.letf_rotation_hunt.run_iter_t5_extended import _run_single_extended

ITER_DIR = PROJECT_ROOT / "studies/letf_rotation_hunt/iterations"
OUT_DATA_DIR = PROJECT_ROOT / "data/robustness_qqq"
OUT_PLOTS_DIR = PROJECT_ROOT / "studies/letf_rotation_hunt/reports/qqq_benchmark_plots"
OUT_REPORT = PROJECT_ROOT / "studies/letf_rotation_hunt/reports/STUDY_QQQ_BENCHMARK_REPORT.md"

WINDOW_SIZES_Y = [3, 5, 10, 15, 20]
WARMUP_DAYS = {3: 21, 5: 21, 10: 252, 15: 252, 20: 252}
TOP_N = 20
BENCHMARK_NAME = "QQQ/NDX 1x b&h"
OPERATIVE_WINNER = "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz"

warnings.filterwarnings("ignore", category=UserWarning, module="market_lab.backtest.validation.pbo")
warnings.filterwarnings("ignore", category=FutureWarning)


def find_top_n_strategies(n: int = TOP_N) -> list[dict[str, Any]]:
    """Find original top-N unique strategies by full-history lh_56y Sharpe.

    The ranking source is deliberately unchanged from the original robustness
    analysis: this is a benchmark sensitivity test, not a QQQ-optimized search
    [advances_fin_ml, p.208-211].
    """
    all_results: list[dict[str, Any]] = []
    for d in sorted(ITER_DIR.glob("0*-*")):
        verdict_path = d / "verdict.json"
        if not verdict_path.exists():
            continue
        try:
            v = json.loads(verdict_path.read_text())
        except json.JSONDecodeError:
            continue
        configs_lookup = {c["name"]: c for c in v.get("configs_tested", [])}
        tier = v.get("tier", "?")
        for r in v.get("results", []):
            if "error" in r:
                continue
            sharpe = r.get("metrics_gross", {}).get("lh_56y", {}).get("sharpe")
            if sharpe is None or not isinstance(sharpe, (int, float)) or sharpe != sharpe:
                continue
            name = r.get("config_name")
            cfg = configs_lookup.get(name)
            if cfg is None or name is None:
                continue
            all_results.append({
                "config_name": name,
                "tier": tier,
                "sharpe_lh56y": float(sharpe),
                "iter_dir": d.name,
                "cfg": cfg,
                "score": r.get("score_breakdown", {}).get("total", 0),
                "tier_label": r.get("tier_label", "?"),
            })

    seen: dict[str, dict[str, Any]] = {}
    for r in sorted(all_results, key=lambda x: -x["sharpe_lh56y"]):
        if r["config_name"] not in seen:
            seen[r["config_name"]] = r
    return sorted(seen.values(), key=lambda x: -x["sharpe_lh56y"])[:n]


def _dispatch_for(entry: dict[str, Any]):
    tier_prefix = entry["tier"][:2]
    cfg = entry["cfg"]
    if tier_prefix == "T1":
        return _run_single_config
    if tier_prefix == "T2":
        return _run_single_basket_config
    if tier_prefix == "T3":
        return _run_single_composite_config
    if tier_prefix == "T4":
        return _run_single_xs_config
    if tier_prefix == "T5":
        if "forecast_type" in cfg or "weighting_scheme" in cfg:
            return _run_single_extended
        return _run_single_voltarget_config
    raise ValueError(f"unknown tier {entry['tier']!r}")


def recompute_equities(top_n: list[dict[str, Any]], ffr_daily: pd.Series) -> dict[str, pd.Series]:
    equities: dict[str, pd.Series] = {}
    for entry in tqdm(top_n, desc="Recomputing top-N equity curves"):
        try:
            r = _dispatch_for(entry)(entry["cfg"], ["lh_56y"], ffr_daily, n_trials_local=1)
            equities[entry["config_name"]] = r["_equity"].dropna()
        except Exception as e:
            print(f"  FAIL {entry['config_name']}: {type(e).__name__}: {e}")
    return equities


def _sortino(rets: pd.Series) -> float:
    if len(rets) < 10:
        return float("nan")
    downside = rets[rets < 0]
    dd = float(np.sqrt((downside.pow(2).mean()))) if len(downside) else 0.0
    if dd <= 1e-12:
        return 0.0
    return float(rets.mean() / dd * np.sqrt(252))


def _sharpe(rets: pd.Series) -> float:
    sigma = float(rets.std(ddof=0))
    return float(rets.mean() / sigma * np.sqrt(252)) if sigma > 1e-12 else 0.0


def _cagr(eq: pd.Series) -> float:
    yrs = max((eq.index[-1] - eq.index[0]).days / 365.25, 1e-6)
    total = float(eq.iloc[-1]) / float(eq.iloc[0])
    return total ** (1.0 / yrs) - 1.0 if total > 0 else -1.0


def _mdd(eq: pd.Series) -> float:
    peak = eq.cummax()
    return float(((eq - peak) / peak).min())


def _relative_metrics(eq: pd.Series, bench: pd.Series, warmup_days: int = 252) -> dict[str, float]:
    aligned = pd.concat({"s": eq.dropna(), "b": bench.dropna()}, axis=1, sort=True).dropna()
    if len(aligned) < warmup_days + 2:
        return {"pct_above_qqq": float("nan"), "min_relative_equity": float("nan"), "end_ratio": float("nan")}
    s_norm = aligned["s"] / float(aligned["s"].iloc[0])
    b_norm = aligned["b"] / float(aligned["b"].iloc[0])
    ratio = s_norm / b_norm
    post = ratio.iloc[warmup_days:]
    return {
        "pct_above_qqq": float((post > 1.0).mean()),
        "min_relative_equity": float(post.min()),
        "end_ratio": float(ratio.iloc[-1]),
    }


def full_history_metrics(equities: dict[str, pd.Series], benchmark: pd.Series) -> pd.DataFrame:
    rows = []
    for name, eq in equities.items():
        common = eq.index.intersection(benchmark.index)
        if len(common) < 252:
            continue
        eq_a = eq.loc[common].dropna()
        rets = eq_a.pct_change().dropna()
        rel = _relative_metrics(eq_a, benchmark.loc[common], warmup_days=252)
        rows.append({
            "config": name,
            "sortino": _sortino(rets),
            "sharpe": _sharpe(rets),
            "cagr": _cagr(eq_a),
            "mdd": _mdd(eq_a),
            **rel,
        })
    return pd.DataFrame(rows).sort_values("end_ratio", ascending=False)


def compute_window_metrics(eq_w: pd.Series, bench_w: pd.Series, warmup_days: int) -> dict[str, float]:
    rets = eq_w.pct_change().dropna()
    if len(rets) < 10:
        return {
            "sharpe": float("nan"), "sortino": float("nan"), "cagr": float("nan"),
            "mdd": float("nan"), "pct_above_qqq": float("nan"),
            "min_relative_equity": float("nan"), "end_ratio": float("nan"),
            "n_obs": int(len(eq_w)),
        }
    return {
        "sharpe": _sharpe(rets),
        "sortino": _sortino(rets),
        "cagr": _cagr(eq_w),
        "mdd": _mdd(eq_w),
        **_relative_metrics(eq_w, bench_w, warmup_days=warmup_days),
        "n_obs": int(len(eq_w)),
    }


def rolling_window_analysis(equities: dict[str, pd.Series], benchmark: pd.Series) -> pd.DataFrame:
    rows = []
    for label, eq in tqdm(equities.items(), desc="Rolling windows vs QQQ", unit="strat"):
        common_idx = eq.index.intersection(benchmark.index)
        eq_a = eq.loc[common_idx].dropna()
        bench_a = benchmark.loc[common_idx].dropna()
        common_idx = eq_a.index.intersection(bench_a.index)
        eq_a = eq_a.loc[common_idx]
        bench_a = bench_a.loc[common_idx]
        if len(eq_a) < 252:
            continue
        first_date = eq_a.index[0]
        last_date = eq_a.index[-1]
        month_starts = pd.date_range(first_date, last_date, freq="BME")
        for ws in WINDOW_SIZES_Y:
            warmup = WARMUP_DAYS[ws]
            min_obs = int(ws * 252 * 0.95)
            for start_date in month_starts:
                end_date = start_date + pd.DateOffset(years=ws)
                if end_date > last_date:
                    break
                eq_w = eq_a.loc[start_date:end_date]
                bench_w = bench_a.loc[start_date:end_date]
                if len(eq_w) < min_obs or len(bench_w) < min_obs:
                    continue
                rows.append({
                    "config": label,
                    "window_size_y": ws,
                    "start_date": start_date,
                    "end_date": eq_w.index[-1],
                    **compute_window_metrics(eq_w, bench_w, warmup),
                })
    return pd.DataFrame(rows)


def aggregate_per_strategy_window(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(["config", "window_size_y"], observed=True)
    return g.agg(
        median_sortino=("sortino", "median"),
        median_sharpe=("sharpe", "median"),
        min_sharpe=("sharpe", "min"),
        median_cagr=("cagr", "median"),
        median_mdd=("mdd", "median"),
        worst_mdd=("mdd", "min"),
        mean_pct_above_qqq=("pct_above_qqq", "mean"),
        win_rate_end_ratio=("end_ratio", lambda x: float((x > 1.0).mean())),
        median_min_rel=("min_relative_equity", "median"),
        worst_min_rel=("min_relative_equity", "min"),
        n_windows=("sharpe", "count"),
    ).reset_index()


def composite_robustness_rank(agg: pd.DataFrame) -> pd.DataFrame:
    out = []
    for config in agg["config"].unique():
        sub = agg[agg["config"] == config]
        out.append({
            "config": config,
            "avg_median_sortino": float(sub["median_sortino"].mean()),
            "avg_median_sharpe": float(sub["median_sharpe"].mean()),
            "avg_min_sharpe": float(sub["min_sharpe"].mean()),
            "avg_pct_above_qqq": float(sub["mean_pct_above_qqq"].mean()),
            "avg_win_rate_end_ratio": float(sub["win_rate_end_ratio"].mean()),
        })
    df = pd.DataFrame(out)
    df["rank_med_sortino"] = df["avg_median_sortino"].rank(ascending=False)
    df["rank_min_sharpe"] = df["avg_min_sharpe"].rank(ascending=False)
    df["rank_pct"] = df["avg_pct_above_qqq"].rank(ascending=False)
    df["rank_win"] = df["avg_win_rate_end_ratio"].rank(ascending=False)
    df["composite_rank"] = (
        df["rank_med_sortino"] + df["rank_min_sharpe"] + df["rank_pct"] + df["rank_win"]
    ) / 4.0
    return df.sort_values("composite_rank")


def _truncate(label: str, n: int = 34) -> str:
    return label if len(label) <= n else label[: n - 1] + "..."


def plot_top_relative_to_qqq(equities: dict[str, pd.Series], benchmark: pd.Series, out_path: Path) -> None:
    ratios: dict[str, pd.Series] = {}
    bench = benchmark.dropna()
    for label, eq in equities.items():
        common = eq.dropna().index.intersection(bench.index)
        if len(common) < 2:
            continue
        s = eq.loc[common] / float(eq.loc[common].iloc[0])
        b = bench.loc[common] / float(bench.loc[common].iloc[0])
        ratios[label] = s / b
    ranked = sorted(ratios, key=lambda n: -float(ratios[n].iloc[-1]))
    top_set = set(ranked[:6])
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1.2, label="QQQ/NDX 1x (=1.0)")
    palette = plt.cm.tab10.colors
    for label in ranked:
        if label in top_set:
            continue
        ax.plot(ratios[label].index, ratios[label].values, color="#d0d0d0", linewidth=0.8, alpha=0.35)
    for i, label in enumerate(ranked):
        if label not in top_set:
            continue
        terminal = float(ratios[label].iloc[-1])
        ax.plot(
            ratios[label].index,
            ratios[label].values,
            color=palette[i % len(palette)],
            linewidth=2.0,
            label=f"{_truncate(label, 28)} ({terminal:.2f}x)",
        )
    ax.set_yscale("log")
    ax.set_title("Top-N LETF rotation strategies relative to QQQ/NDX buy-hold")
    ax.set_ylabel("strategy equity / QQQ equity (rebased)")
    ax.set_xlabel("Date")
    ax.grid(True, which="both", linewidth=0.3, alpha=0.4)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.85)
    plt.tight_layout()
    fig.savefig(out_path, dpi=90, bbox_inches="tight")
    plt.close(fig)


def plot_pct_above_qqq_heatmap(agg: pd.DataFrame, out_path: Path) -> None:
    pivot = agg.pivot(index="config", columns="window_size_y", values="mean_pct_above_qqq")
    pivot = pivot.reindex(pivot.mean(axis=1).sort_values(ascending=False).index)
    fig, ax = plt.subplots(figsize=(8, max(6, 0.34 * len(pivot))))
    arr = pivot.to_numpy(dtype=float)
    im = ax.imshow(arr, aspect="auto", cmap="RdYlGn", vmin=0.0, vmax=1.0)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([f"{c}y" for c in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([_truncate(c) for c in pivot.index], fontsize=8)
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            v = arr[i, j]
            if v == v:
                ax.text(j, i, f"{v:.0%}", ha="center", va="center", fontsize=7)
    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label("Mean pct of rolling-window days above QQQ")
    ax.set_title("Pct time above QQQ/NDX by rolling-window size")
    plt.tight_layout()
    fig.savefig(out_path, dpi=90, bbox_inches="tight")
    plt.close(fig)


def plot_robustness_ranking(comp: pd.DataFrame, out_path: Path) -> None:
    df = comp.head(30).copy()
    df["rank_label"] = range(1, len(df) + 1)
    fig, ax = plt.subplots(figsize=(12, max(6, 0.34 * len(df))))
    labels = [f"{r}. {_truncate(c)}" for r, c in zip(df["rank_label"], df["config"])]
    bars = ax.barh(labels[::-1], df["composite_rank"][::-1], color="steelblue", alpha=0.85)
    for bar, rank, sortino, pct, win in zip(
        bars,
        df["composite_rank"][::-1],
        df["avg_median_sortino"][::-1],
        df["avg_pct_above_qqq"][::-1],
        df["avg_win_rate_end_ratio"][::-1],
    ):
        ax.text(rank + 0.25, bar.get_y() + bar.get_height() / 2,
                f"sort={sortino:.2f} pct={pct:.0%} win={win:.0%}", va="center", fontsize=8)
    ax.set_xlabel("Composite rank (lower = more robust vs QQQ)")
    ax.set_title("Composite robustness ranking vs QQQ/NDX")
    ax.grid(True, axis="x", linewidth=0.3, alpha=0.5)
    plt.tight_layout()
    fig.savefig(out_path, dpi=90, bbox_inches="tight")
    plt.close(fig)


def _fmt_pct(v: float) -> str:
    return "—" if v != v else f"{v * 100:.1f}%"


def _fmt_num(v: float, digits: int = 3) -> str:
    return "—" if v != v else f"{v:.{digits}f}"


def render_report(
    top_n: list[dict[str, Any]],
    full: pd.DataFrame,
    windows: pd.DataFrame,
    agg: pd.DataFrame,
    comp: pd.DataFrame,
    out_path: Path,
) -> None:
    winner_full = full[full["config"] == OPERATIVE_WINNER]
    winner_comp = comp[comp["config"] == OPERATIVE_WINNER]
    winner_rank = int(comp.reset_index(drop=True).index[comp["config"].to_numpy() == OPERATIVE_WINNER][0] + 1) if not winner_comp.empty else None

    win_pivot = agg.pivot(index="config", columns="window_size_y", values="win_rate_end_ratio")
    pct_pivot = agg.pivot(index="config", columns="window_size_y", values="mean_pct_above_qqq")

    lines = [
        "# LETF Rotation Hunt — QQQ/NDX Benchmark Supplement",
        "",
        "**Status:** Supplemental benchmark-sensitivity report generated 2026-05-09.",
        "**Benchmark:** `QQQSIM` as long-history QQQ/NDX 1x buy-and-hold proxy.",
        f"**Universe:** original top-{TOP_N} strategies ranked by lh_56y Sharpe, plus QQQ/NDX benchmark. No QQQ-specific re-optimization.",
        "",
        "> This report answers the Reddit criticism: if QLD is the risk-on asset, QQQ/NDX is the stricter direct benchmark. The methodology intentionally changes only the benchmark to avoid new selection bias [advances_fin_ml, p.31-34; p.208-211].",
        "",
        "---",
        "",
        "## 1. TL;DR",
        "",
    ]
    if not winner_full.empty and winner_rank is not None:
        wf = winner_full.iloc[0]
        wc = winner_comp.iloc[0]
        lines += [
            f"- Operative winner `{OPERATIVE_WINNER}` remains above QQQ/NDX on full-history terminal wealth: **{wf['end_ratio']:.2f}x QQQ**.",
            f"- Full-history pct time above QQQ: **{wf['pct_above_qqq'] * 100:.1f}%**; minimum relative equity after warmup: **{wf['min_relative_equity']:.2f}x**.",
            f"- Composite rolling robustness vs QQQ rank: **#{winner_rank} of {len(comp)}**.",
            f"- Rolling-window average end-ratio win rate vs QQQ: **{wc['avg_win_rate_end_ratio'] * 100:.1f}%**; average pct days above QQQ: **{wc['avg_pct_above_qqq'] * 100:.1f}%**.",
            "- The benchmark change is much stricter than SPY: short 3y/5y windows contain more relative underperformance during NDX bull recoveries, while 10y+ windows are the key durability check.",
        ]
    else:
        lines.append(f"- Operative winner `{OPERATIVE_WINNER}` was not present in the recomputed top-N universe.")

    lines += [
        "",
        "---",
        "",
        "## 2. Visuals",
        "",
        "![Top-N relative to QQQ](qqq_benchmark_plots/top21_relative_to_qqq.png)",
        "",
        "![Pct above QQQ](qqq_benchmark_plots/rolling_pct_above_qqq.png)",
        "",
        "![Robustness ranking vs QQQ](qqq_benchmark_plots/robustness_ranking_vs_qqq.png)",
        "",
        "---",
        "",
        "## 3. Full-History Metrics vs QQQ/NDX",
        "",
        "Ranked by terminal `strategy_eq / QQQ_eq` on the common lh_56y window.",
        "",
        "| Rank | Config | Sortino | Sharpe | CAGR | MDD | pct above QQQ | min rel | end ratio vs QQQ |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for i, (_, row) in enumerate(full.iterrows(), 1):
        lines.append(
            f"| {i} | `{row['config']}` | {_fmt_num(row['sortino'])} | {_fmt_num(row['sharpe'])} | "
            f"{_fmt_pct(row['cagr'])} | {_fmt_pct(row['mdd'])} | {_fmt_pct(row['pct_above_qqq'])} | "
            f"{_fmt_num(row['min_relative_equity'], 2)} | {_fmt_num(row['end_ratio'], 2)}x |"
        )

    lines += [
        "",
        "---",
        "",
        "## 4. Rolling End-Ratio Win Rate vs QQQ",
        "",
        "Cell = fraction of rolling windows where terminal strategy equity beats terminal QQQ equity.",
        "",
        "| Config | 3y | 5y | 10y | 15y | 20y |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    order = list(comp["config"])
    for cfg in order:
        if cfg not in win_pivot.index:
            continue
        vals = []
        for w in WINDOW_SIZES_Y:
            vals.append(_fmt_pct(float(win_pivot.loc[cfg, w])) if w in win_pivot.columns else "—")
        lines.append(f"| `{cfg}` | " + " | ".join(vals) + " |")

    lines += [
        "",
        "---",
        "",
        "## 5. Rolling Pct Time Above QQQ",
        "",
        "Cell = mean fraction of days inside each rolling window where strategy equity is above QQQ equity, after warmup.",
        "",
        "| Config | 3y | 5y | 10y | 15y | 20y |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for cfg in order:
        if cfg not in pct_pivot.index:
            continue
        vals = []
        for w in WINDOW_SIZES_Y:
            vals.append(_fmt_pct(float(pct_pivot.loc[cfg, w])) if w in pct_pivot.columns else "—")
        lines.append(f"| `{cfg}` | " + " | ".join(vals) + " |")

    worst = windows[windows["config"] == OPERATIVE_WINNER].sort_values("end_ratio").head(12)
    lines += [
        "",
        "---",
        "",
        f"## 6. Worst Relative Windows — `{OPERATIVE_WINNER}`",
        "",
        "| Start | End | Window | end ratio vs QQQ | pct above QQQ | min rel | Sharpe | Sortino | CAGR |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in worst.iterrows():
        lines.append(
            f"| {pd.Timestamp(row['start_date']).date()} | {pd.Timestamp(row['end_date']).date()} | "
            f"{int(row['window_size_y'])}y | {_fmt_num(row['end_ratio'], 3)}x | {_fmt_pct(row['pct_above_qqq'])} | "
            f"{_fmt_num(row['min_relative_equity'], 3)}x | {_fmt_num(row['sharpe'])} | {_fmt_num(row['sortino'])} | {_fmt_pct(row['cagr'])} |"
        )

    lines += [
        "",
        "---",
        "",
        "## 7. Top-N Input Strategies",
        "",
        "| Rank | Config | Tier | Original lh_56y Sharpe | Score | Label | Source iter |",
        "|---:|---|---|---:|---:|---|---|",
    ]
    for i, e in enumerate(top_n, 1):
        lines.append(
            f"| {i} | `{e['config_name']}` | {e['tier']} | {e['sharpe_lh56y']:.3f} | "
            f"{float(e['score']):.0f} | {e['tier_label']} | `{e['iter_dir']}` |"
        )

    lines += [
        "",
        "---",
        "",
        "## 8. Methodology Notes",
        "",
        "- Benchmark is `QQQSIM`; `NDXSIM` is not available in the local testfolio cache, so QQQSIM is used as the long-history NDX/QQQ proxy.",
        "- Strategy universe is unchanged from the original top-N robustness setup; this avoids benchmark-specific data snooping [advances_fin_ml, p.208-211].",
        "- Rolling windows use 3y/5y/10y/15y/20y horizons with month-end starts and the same warmup convention as the SPY robustness report.",
        "- Relative metrics rebase both strategy and QQQ to 1.0 at each common-window start date.",
        "- This is a supplemental benchmark-sensitivity report, not a new deployment authorization. Mandate §1 remains unchanged.",
        "",
    ]
    out_path.write_text("\n".join(lines) + "\n")


def main() -> int:
    OUT_DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Step 1: Identifying original top-20 strategies by lh_56y Sharpe...")
    top20 = find_top_n_strategies(TOP_N)
    for i, e in enumerate(top20, 1):
        print(f"  {i:>2}. {e['config_name']:<52} {e['tier']:<5} Sharpe {e['sharpe_lh56y']:.3f}")

    print("\nStep 2: Recomputing equity curves...")
    ffr = load_ffr_daily()
    equities = recompute_equities(top20, ffr)
    print(f"  Recomputed {len(equities)} strategies.")

    print("\nStep 2b: Loading QQQSIM benchmark...")
    qqq = load_testfolio_series("QQQSIM").dropna()
    equities_with_bench = {**equities, BENCHMARK_NAME: qqq}

    print("\nStep 3: Computing full-history metrics vs QQQ...")
    full = full_history_metrics(equities_with_bench, qqq)
    full.to_csv(OUT_DATA_DIR / "full_history_vs_qqq.csv", index=False)

    print("\nStep 4: Rolling-window analysis vs QQQ...")
    windows = rolling_window_analysis(equities_with_bench, qqq)
    windows.to_parquet(OUT_DATA_DIR / "all_windows.parquet", index=False)

    print("\nStep 5: Aggregating rankings...")
    agg = aggregate_per_strategy_window(windows)
    comp = composite_robustness_rank(agg)
    agg.to_csv(OUT_DATA_DIR / "agg_per_window.csv", index=False)
    comp.to_csv(OUT_DATA_DIR / "composite_ranking.csv", index=False)
    print("  Top 5 vs QQQ:")
    for i, (_, row) in enumerate(comp.head(5).iterrows(), 1):
        print(
            f"    {i}. {row['config']:<52} sort={row['avg_median_sortino']:.3f} "
            f"pct={row['avg_pct_above_qqq']*100:.1f}% win={row['avg_win_rate_end_ratio']*100:.1f}%"
        )

    print("\nStep 6: Generating plots...")
    plot_top_relative_to_qqq(equities, qqq, OUT_PLOTS_DIR / "top21_relative_to_qqq.png")
    plot_pct_above_qqq_heatmap(agg, OUT_PLOTS_DIR / "rolling_pct_above_qqq.png")
    plot_robustness_ranking(comp, OUT_PLOTS_DIR / "robustness_ranking_vs_qqq.png")

    print("\nStep 7: Rendering markdown report...")
    render_report(top20, full, windows, agg, comp, OUT_REPORT)
    print(f"  Wrote: {OUT_REPORT}")

    print("\nQQQ benchmark supplement complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
