"""Generate a rich report for Stage 1 close-only top vote strategies.

Input is the fast exact-grid output from
`run_stage1_close_only_fast.py`. The report reconstructs top candidates,
compares them against branch-native benchmarks, and renders equity,
benchmark-relative equity, drawdown and rolling-window diagnostics.

This is still exploratory reporting. Final strategy claims require validation
gates such as PBO, DSR, walk-forward, OOS, FWD and bootstrap
`[advances_fin_ml, p.208-211]`.
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
from studies.technical_signal_vote_hunt.core import STAGE1_BRANCHES, daily_returns
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import (
    _benchmark_rows,
    _prepare_branch,
    _simulate_on_off_np,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FAST_DIR = REPO_ROOT / "studies/technical_signal_vote_hunt/results/stage1_close_only_fast"
TABLES_DIR = FAST_DIR / "tables"
OUT_DIR = REPO_ROOT / "studies/technical_signal_vote_hunt/reports/stage1_top_strategies"
PLOTS_DIR = OUT_DIR / "plots"
OUT_TABLES_DIR = OUT_DIR / "tables"

TRADING_DAYS_PER_YEAR = 252


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate Stage 1 top strategy report")
    p.add_argument("--top-per-branch", type=int, default=3)
    p.add_argument("--off-leg", choices=["ZROZSIM", "CASHX"], default="ZROZSIM")
    p.add_argument("--input", type=Path, default=TABLES_DIR / "stage1_results_fast.csv")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    OUT_TABLES_DIR.mkdir(parents=True, exist_ok=True)

    results = pd.read_csv(args.input)
    top = _select_top(results, args.top_per_branch)
    top.to_csv(OUT_TABLES_DIR / "selected_top_candidates.csv", index=False)

    off_returns = daily_returns(load_testfolio_series(args.off_leg))
    branch_arrays = {
        (spec.branch, spec.risk_on_label): _prepare_branch(spec, off_returns, signal_limit=None)
        for spec in STAGE1_BRANCHES
    }

    series: dict[str, pd.Series] = {}
    metrics_rows: list[dict] = []
    rolling_rows: list[dict] = []

    for (branch, risk_on), sub in top.groupby(["branch", "risk_on"], sort=True):
        arr = branch_arrays[(branch, risk_on)]
        bench_series = _benchmark_series(arr)
        for label, returns in bench_series.items():
            key = f"{branch}_{risk_on}_{label}"
            series[key] = pd.Series(returns, index=arr.dates, name=key)
            metrics_rows.append(_metrics_row(key, branch, risk_on, "benchmark", series[key], series[f"{branch}_{risk_on}_buy_hold"] if f"{branch}_{risk_on}_buy_hold" in series else pd.Series(arr.benchmark_returns, index=arr.dates)))

        for rank, row in enumerate(sub.itertuples(index=False), start=1):
            returns = _candidate_returns(arr, row.signals, int(row.k))
            label = f"top{rank:02d}_n{int(row.n)}k{int(row.k)}"
            key = f"{branch}_{risk_on}_{label}"
            series[key] = pd.Series(returns, index=arr.dates, name=key)
            metrics_rows.append(_metrics_row(key, branch, risk_on, row.signals, series[key], series[f"{branch}_{risk_on}_buy_hold"]))

        group_keys = [k for k in series if k.startswith(f"{branch}_{risk_on}_")]
        _plot_group(branch, risk_on, {k: series[k] for k in group_keys})
        rolling_rows.extend(_rolling_summary(branch, risk_on, {k: series[k] for k in group_keys}))

    metrics = pd.DataFrame(metrics_rows).sort_values(["branch", "risk_on", "sortino"], ascending=[True, True, False])
    rolling = pd.DataFrame(rolling_rows)
    metrics.to_csv(OUT_TABLES_DIR / "headline_metrics.csv", index=False)
    rolling.to_csv(OUT_TABLES_DIR / "rolling_summary.csv", index=False)

    _write_report(top, metrics, rolling, args)
    _write_manifest(args, top, metrics)
    print(f"Wrote report to {OUT_DIR / 'REPORT.md'}")
    return 0


def _select_top(results: pd.DataFrame, top_per_branch: int) -> pd.DataFrame:
    selected = []
    for _, sub in results.sort_values(["sortino", "cagr", "calmar"], ascending=[False, False, False]).groupby(["branch", "risk_on"], sort=True):
        # Deduplicate exact signal sets that differ only by duplicate MACD aliases.
        seen = set()
        rows = []
        for row in sub.itertuples(index=False):
            normalized = _normalize_signal_set(str(row.signals), int(row.k))
            if normalized in seen:
                continue
            seen.add(normalized)
            rows.append(row._asdict())
            if len(rows) >= top_per_branch:
                break
        selected.extend(rows)
    return pd.DataFrame(selected).sort_values(["branch", "risk_on", "sortino"], ascending=[True, True, False])


def _normalize_signal_set(signals: str, k: int) -> tuple[tuple[str, ...], int]:
    names = ["macd" if s in {"macd_gt_signal", "macd_hist_gt_0"} else s for s in signals.split("|")]
    return tuple(sorted(names)), k


def _candidate_returns(arr, signals: str, k: int) -> np.ndarray:
    idx = [arr.signal_names.index(name) for name in signals.split("|")]
    sub = arr.signal_matrix[:, idx]
    valid = ~np.isnan(sub).any(axis=1)
    counts = np.nansum(sub, axis=1)
    signal = np.where(valid, counts >= k, False)
    return _simulate_on_off_np(signal, arr.on_returns, arr.off_returns)


def _benchmark_series(arr) -> dict[str, np.ndarray]:
    out = {}
    for row in _benchmark_rows(arr):
        raw = str(row["label"])
        if raw.endswith("_buy_hold"):
            label = "buy_hold"
            returns = arr.benchmark_returns
        elif raw.endswith("_lrs_sma200"):
            label = "lrs_sma200"
            returns = _returns_from_metrics_row_not_available(arr, raw)
        elif raw.endswith("_t3d_k2"):
            label = "t3d_k2"
            returns = _returns_from_metrics_row_not_available(arr, raw)
        elif raw.endswith("_iter030_like"):
            label = "iter030_like"
            returns = _returns_from_metrics_row_not_available(arr, raw)
        else:
            continue
        out[label] = returns
    return out


def _returns_from_metrics_row_not_available(arr, label: str) -> np.ndarray:
    # Reconstruct benchmark controls directly; _benchmark_rows returns metrics only.
    from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import (
        _simulate_iter030_like_np,
    )
    from studies.technical_signal_vote_hunt.core import build_rearm_gate

    if label.endswith("_lrs_sma200"):
        signal = np.where(np.isnan(arr.lrs_signal), False, arr.lrs_signal >= 1.0)
        return _simulate_on_off_np(signal, arr.on_returns, arr.off_returns)
    if label.endswith("_t3d_k2"):
        signal = np.where(np.isnan(arr.t3d_signal), False, arr.t3d_signal >= 1.0)
        return _simulate_on_off_np(signal, arr.on_returns, arr.off_returns)
    if label.endswith("_iter030_like"):
        signal = np.where(np.isnan(arr.t3d_signal), False, arr.t3d_signal >= 1.0)
        rearm = build_rearm_gate(pd.Series(arr.t3d_signal, index=arr.dates)).to_numpy(dtype=np.float32)
        rearm_bool = np.where(np.isnan(rearm), False, rearm >= 1.0)
        return _simulate_iter030_like_np(signal, rearm_bool, arr.on_returns, arr.off_returns)
    raise ValueError(label)


def _metrics_row(label: str, branch: str, risk_on: str, signals: str, returns: pd.Series, benchmark: pd.Series) -> dict:
    aligned = pd.concat({"r": returns, "b": benchmark}, axis=1, sort=False).dropna()
    r = aligned["r"].to_numpy(dtype=float)
    b = aligned["b"].to_numpy(dtype=float)
    eq = np.cumprod(1.0 + r)
    beq = np.cumprod(1.0 + b)
    years = len(r) / TRADING_DAYS_PER_YEAR
    cagr = (eq[-1] / eq[0]) ** (1.0 / years) - 1.0
    mdd = _max_drawdown(eq)
    mean = float(np.mean(r))
    std = float(np.std(r, ddof=1))
    sharpe = mean / std * np.sqrt(TRADING_DAYS_PER_YEAR) if std > 0 else 0.0
    downside = r[r < 0]
    down_std = float(np.std(downside, ddof=1)) if len(downside) > 1 else 0.0
    sortino = mean / down_std * np.sqrt(TRADING_DAYS_PER_YEAR) if down_std > 0 else 0.0
    rel = eq / beq
    return {
        "label": label,
        "branch": branch,
        "risk_on": risk_on,
        "signals": signals,
        "cagr": cagr,
        "sharpe": sharpe,
        "sortino": sortino,
        "mdd": -mdd,
        "calmar": cagr / mdd if mdd > 0 else np.inf,
        "end_mult": float(eq[-1] / eq[0]),
        "end_rel_to_benchmark": float(rel[-1]),
        "pct_above_benchmark": float(np.mean(rel[252:] > 1.0)) if len(rel) > 252 else np.nan,
    }


def _plot_group(branch: str, risk_on: str, data: dict[str, pd.Series]) -> None:
    bench_key = f"{branch}_{risk_on}_buy_hold"
    benchmark = data[bench_key]
    equities = {k: _equity(v) for k, v in data.items()}
    bench_eq = equities[bench_key]
    colors = _color_map(list(data))

    _line_plot(
        {k: eq for k, eq in equities.items()},
        title=f"{branch}->{risk_on}: equity curves (log)",
        ylabel="Equity ($10k base)",
        path=PLOTS_DIR / f"{branch}_{risk_on}_01_equity.png",
        colors=colors,
        logy=True,
    )
    _line_plot(
        {k: eq / bench_eq.reindex(eq.index).ffill() for k, eq in equities.items() if k != bench_key},
        title=f"{branch}->{risk_on}: relative equity vs buy-hold",
        ylabel="Strategy equity / benchmark equity",
        path=PLOTS_DIR / f"{branch}_{risk_on}_02_relative_equity.png",
        colors=colors,
        hline=1.0,
    )
    _line_plot(
        {k: _drawdown(eq) for k, eq in equities.items()},
        title=f"{branch}->{risk_on}: drawdowns",
        ylabel="Drawdown",
        path=PLOTS_DIR / f"{branch}_{risk_on}_03_drawdown.png",
        colors=colors,
        percent=True,
    )
    _rolling_plot(data, branch, risk_on, metric="cagr")
    _rolling_plot(data, branch, risk_on, metric="sortino")


def _line_plot(
    data: dict[str, pd.Series],
    title: str,
    ylabel: str,
    path: Path,
    colors: dict[str, str],
    logy: bool = False,
    hline: float | None = None,
    percent: bool = False,
) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    for name, s in data.items():
        lw = 2.3 if "top01" in name else 1.5
        alpha = 0.95 if "top" in name else 0.70
        ax.plot(s.index, s.values, label=_short_label(name), color=colors.get(name), linewidth=lw, alpha=alpha)
    if hline is not None:
        ax.axhline(hline, color="black", linewidth=1.0, linestyle="--", alpha=0.6)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    if logy:
        ax.set_yscale("log")
    if percent:
        ax.yaxis.set_major_formatter(lambda x, _: f"{x:.0%}")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8, loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _rolling_plot(data: dict[str, pd.Series], branch: str, risk_on: str, metric: str) -> None:
    windows = [3, 5, 10, 15]
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharex=True)
    colors = _color_map(list(data))
    for ax, years in zip(axes.ravel(), windows):
        window = years * TRADING_DAYS_PER_YEAR
        for name, returns in data.items():
            if len(returns) < window + 5:
                continue
            vals = _rolling_metric(returns, window, metric)
            ax.plot(vals.index, vals.values, label=_short_label(name), color=colors.get(name), linewidth=1.3, alpha=0.85)
        ax.set_title(f"{years}y rolling {metric}")
        ax.grid(True, alpha=0.25)
        ax.yaxis.set_major_formatter(lambda x, _: f"{x:.0%}" if metric == "cagr" else f"{x:.2f}")
    axes[0, 0].legend(fontsize=7, loc="best")
    fig.suptitle(f"{branch}->{risk_on}: rolling {metric}")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / f"{branch}_{risk_on}_04_rolling_{metric}.png", dpi=160)
    plt.close(fig)


def _rolling_summary(branch: str, risk_on: str, data: dict[str, pd.Series]) -> list[dict]:
    rows = []
    for name, returns in data.items():
        for years in (3, 5, 10, 15):
            window = years * TRADING_DAYS_PER_YEAR
            if len(returns) < window + 5:
                continue
            c = _rolling_metric(returns, window, "cagr")
            s = _rolling_metric(returns, window, "sortino")
            rows.append({
                "branch": branch,
                "risk_on": risk_on,
                "label": name,
                "window_years": years,
                "cagr_mean": float(c.mean()),
                "cagr_min": float(c.min()),
                "sortino_mean": float(s.mean()),
                "sortino_min": float(s.min()),
            })
    return rows


def _rolling_metric(returns: pd.Series, window: int, metric: str) -> pd.Series:
    vals = []
    idx = []
    arr = returns.to_numpy(dtype=float)
    for end in range(window, len(arr) + 1, TRADING_DAYS_PER_YEAR):
        r = arr[end - window:end]
        idx.append(returns.index[end - 1])
        if metric == "cagr":
            eq = np.cumprod(1.0 + r)
            vals.append(float((eq[-1] / eq[0]) ** (TRADING_DAYS_PER_YEAR / len(r)) - 1.0))
        elif metric == "sortino":
            mean = float(np.mean(r))
            downside = r[r < 0]
            down_std = float(np.std(downside, ddof=1)) if len(downside) > 1 else 0.0
            vals.append(mean / down_std * np.sqrt(TRADING_DAYS_PER_YEAR) if down_std > 0 else 0.0)
        else:
            raise ValueError(metric)
    return pd.Series(vals, index=idx)


def _write_report(top: pd.DataFrame, metrics: pd.DataFrame, rolling: pd.DataFrame, args: argparse.Namespace) -> None:
    lines = [
        "# Stage 1 Top Strategies Deep Dive",
        "",
        "Status: exploratory report from the Stage 1 close-only exact grid. This is not a deploy verdict.",
        "",
        f"Selection: top {args.top_per_branch} by Sortino per `(branch, risk_on)` from `{args.input}`.",
        f"Off leg: `{args.off_leg}`.",
        "",
        "## Selected Candidates",
        "",
        top[["branch", "risk_on", "n", "k", "sortino", "cagr", "sharpe", "mdd", "calmar", "signals"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Headline Metrics",
        "",
        metrics[["branch", "risk_on", "label", "sortino", "cagr", "sharpe", "mdd", "calmar", "end_rel_to_benchmark", "pct_above_benchmark"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Rolling Summary",
        "",
        rolling.to_markdown(index=False, floatfmt=".4f") if not rolling.empty else "No rolling rows.",
        "",
        "## Plot Index",
        "",
    ]
    for branch in ("QQQ", "SPY"):
        risks = ["QLD_2x", "TQQQ_3x"] if branch == "QQQ" else ["SSO_2x", "UPRO_3x"]
        for risk_on in risks:
            lines.extend([
                f"### {branch}->{risk_on}",
                "",
                f"![Equity](plots/{branch}_{risk_on}_01_equity.png)",
                f"![Relative equity](plots/{branch}_{risk_on}_02_relative_equity.png)",
                f"![Drawdown](plots/{branch}_{risk_on}_03_drawdown.png)",
                f"![Rolling CAGR](plots/{branch}_{risk_on}_04_rolling_cagr.png)",
                f"![Rolling Sortino](plots/{branch}_{risk_on}_04_rolling_sortino.png)",
                "",
            ])
    lines.extend([
        "## Caveats",
        "",
        "- These candidates were selected in-sample from 5,471,268 exact-grid configs.",
        "- DSR trial accounting must include the full grid and any GA evaluations `[advances_fin_ml, p.222-223]`.",
        "- Next validation step: deduplicate candidates and run walk-forward, OOS, FWD, bootstrap, PBO and DSR `[advances_fin_ml, p.208-211]`.",
    ])
    (OUT_DIR / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(args: argparse.Namespace, top: pd.DataFrame, metrics: pd.DataFrame) -> None:
    manifest = {
        "report": "stage1_top_strategies",
        "input": str(args.input),
        "top_per_branch": args.top_per_branch,
        "off_leg": args.off_leg,
        "selected_candidates": int(len(top)),
        "metric_rows": int(len(metrics)),
        "primary_citation": "[advances_fin_ml, p.208-211]",
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _equity(returns: pd.Series) -> pd.Series:
    return (1.0 + returns.fillna(0.0)).cumprod() * 10_000.0


def _drawdown(equity: pd.Series) -> pd.Series:
    return equity / equity.cummax() - 1.0


def _max_drawdown(equity: np.ndarray) -> float:
    peak = np.maximum.accumulate(equity)
    return float(np.max((peak - equity) / peak))


def _short_label(name: str) -> str:
    for prefix in ("QQQ_QLD_2x_", "QQQ_TQQQ_3x_", "SPY_SSO_2x_", "SPY_UPRO_3x_"):
        if name.startswith(prefix):
            return name.removeprefix(prefix)
    return name


def _color_map(names: list[str]) -> dict[str, str]:
    palette = [
        "#111111", "#777777", "#1f77b4", "#9467bd", "#d62728", "#2ca02c",
        "#ff7f0e", "#8c564b", "#e377c2", "#17becf",
    ]
    return {name: palette[i % len(palette)] for i, name in enumerate(names)}


if __name__ == "__main__":
    raise SystemExit(main())
