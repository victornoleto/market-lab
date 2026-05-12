"""Run Stage 1 close-only technical signal vote grid.

The runner evaluates all combinations up to `--max-n`; for each subset it tests
all `k=1..n` vote thresholds. Use larger `--max-n` deliberately because the
search grows combinatorially and every trial must be accounted for in DSR/PBO
later `[advances_fin_ml, p.222-223]`.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

from market_lab.backtest.metrics.performance import cagr, calmar, max_drawdown, sharpe, sortino
from studies.letf_rotation_hunt.core.data_loader import load_testfolio_series
from studies.technical_signal_vote_hunt.core import (
    STAGE1_BRANCHES,
    build_close_only_signals,
    build_t3d_k2_signal,
    daily_returns,
    equity_from_returns,
    simulate_iter030_like,
    simulate_on_off,
    vote_signal,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = REPO_ROOT / "studies/technical_signal_vote_hunt/results/stage1_close_only"
TABLES_DIR = OUT_DIR / "tables"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Stage 1 close-only vote-k grid")
    p.add_argument("--max-n", type=int, default=3, help="maximum signal subset size")
    p.add_argument("--min-n", type=int, default=1, help="minimum signal subset size")
    p.add_argument("--off-leg", choices=["ZROZSIM", "CASHX"], default="ZROZSIM")
    p.add_argument("--top", type=int, default=50, help="top rows to include in report")
    p.add_argument(
        "--signal-limit",
        type=int,
        default=None,
        help="optional first-N signal limiter for smoke tests",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.min_n < 1 or args.max_n < args.min_n:
        raise SystemExit("Require 1 <= --min-n <= --max-n")

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict] = []
    bench_rows: list[dict] = []

    off_prices = load_testfolio_series(args.off_leg)
    off_returns = daily_returns(off_prices)

    for branch in STAGE1_BRANCHES:
        signal_prices = load_testfolio_series(branch.signal_ticker)
        on_prices = load_testfolio_series(branch.risk_on_ticker)
        bench_prices = load_testfolio_series(branch.benchmark_ticker)

        signal_map = build_close_only_signals(signal_prices)
        if args.signal_limit is not None:
            signal_map = dict(list(signal_map.items())[: args.signal_limit])
        signal_names = list(signal_map.keys())

        on_returns = daily_returns(on_prices)
        bench_returns = daily_returns(bench_prices)

        native_benchmarks = _build_native_benchmarks(
            signal_prices=signal_prices,
            on_returns=on_returns,
            off_returns=off_returns,
            bench_returns=bench_returns,
            branch=branch.branch,
            risk_on_label=branch.risk_on_label,
        )
        for label, returns in native_benchmarks.items():
            bench_rows.append(_metrics_row(
                returns,
                label=label,
                branch=branch.branch,
                risk_on=branch.risk_on_label,
                n=0,
                k=0,
                signals="benchmark",
                benchmark_returns=bench_returns,
            ))

        for n in range(args.min_n, min(args.max_n, len(signal_names)) + 1):
            for combo in itertools.combinations(signal_names, n):
                sig_list = [signal_map[name] for name in combo]
                for k in range(1, n + 1):
                    sig = vote_signal(sig_list, k)
                    returns = simulate_on_off(sig, on_returns, off_returns)
                    all_rows.append(_metrics_row(
                        returns,
                        label="vote_k",
                        branch=branch.branch,
                        risk_on=branch.risk_on_label,
                        n=n,
                        k=k,
                        signals="|".join(combo),
                        benchmark_returns=bench_returns,
                    ))

    results = pd.DataFrame(all_rows)
    benches = pd.DataFrame(bench_rows)
    if results.empty:
        raise SystemExit("No results generated")

    results = results.sort_values(
        ["sortino", "cagr", "calmar"], ascending=[False, False, False]
    ).reset_index(drop=True)
    benches = benches.sort_values(
        ["branch", "risk_on", "sortino", "cagr"], ascending=[True, True, False, False]
    ).reset_index(drop=True)

    results.to_csv(TABLES_DIR / "stage1_results.csv", index=False)
    benches.to_csv(TABLES_DIR / "stage1_native_benchmarks.csv", index=False)

    importance = _indicator_importance(results, top_frac=0.05)
    importance.to_csv(TABLES_DIR / "indicator_importance_top5pct.csv", index=False)

    _write_report(results, benches, importance, args)
    _write_manifest(results, benches, args)
    print(f"Wrote {len(results):,} configs to {TABLES_DIR / 'stage1_results.csv'}")
    return 0


def _build_native_benchmarks(
    signal_prices: pd.Series,
    on_returns: pd.Series,
    off_returns: pd.Series,
    bench_returns: pd.Series,
    branch: str,
    risk_on_label: str,
) -> dict[str, pd.Series]:
    lrs_signal = (signal_prices > signal_prices.rolling(200, min_periods=200).mean()).astype(float)
    lrs_signal[signal_prices.rolling(200, min_periods=200).mean().isna()] = np.nan

    t3d = build_t3d_k2_signal(signal_prices)
    return {
        f"{branch}_buy_hold": bench_returns.dropna(),
        f"{branch}_{risk_on_label}_lrs_sma200": simulate_on_off(lrs_signal, on_returns, off_returns),
        f"{branch}_{risk_on_label}_t3d_k2": simulate_on_off(t3d, on_returns, off_returns),
        f"{branch}_{risk_on_label}_iter030_like": simulate_iter030_like(t3d, on_returns, off_returns),
    }


def _metrics_row(
    returns: pd.Series,
    label: str,
    branch: str,
    risk_on: str,
    n: int,
    k: int,
    signals: str,
    benchmark_returns: pd.Series,
) -> dict:
    aligned = pd.concat({"r": returns, "b": benchmark_returns}, axis=1, sort=False).dropna()
    r = aligned["r"]
    b = aligned["b"]
    eq = equity_from_returns(r)
    bench_eq = equity_from_returns(b)
    rel = (eq / eq.iloc[0]) / (bench_eq / bench_eq.iloc[0])
    return {
        "label": label,
        "branch": branch,
        "risk_on": risk_on,
        "n": int(n),
        "k": int(k),
        "signals": signals,
        "cagr": float(cagr(eq)),
        "sharpe": float(sharpe(r)),
        "sortino": float(sortino(r)),
        "mdd": float(-max_drawdown(eq)),
        "calmar": float(calmar(eq)),
        "vol_annual": float(r.std(ddof=1) * np.sqrt(252)),
        "end_mult": float(eq.iloc[-1] / eq.iloc[0]),
        "end_rel_to_benchmark": float(rel.iloc[-1]),
        "pct_above_benchmark": float((rel.iloc[252:] > 1.0).mean()) if len(rel) > 252 else np.nan,
        "start": str(r.index.min().date()),
        "end": str(r.index.max().date()),
        "n_days": int(len(r)),
    }


def _indicator_importance(results: pd.DataFrame, top_frac: float) -> pd.DataFrame:
    cutoff = max(1, int(len(results) * top_frac))
    top = results.head(cutoff).copy()
    records: list[dict] = []
    all_signals = sorted({s for row in results["signals"] for s in str(row).split("|") if s})
    for sig in all_signals:
        present_all = results["signals"].str.split("|").apply(lambda xs: sig in xs)
        present_top = top["signals"].str.split("|").apply(lambda xs: sig in xs)
        all_with = results[present_all]
        all_without = results[~present_all]
        records.append({
            "signal": sig,
            "top_count": int(present_top.sum()),
            "top_share": float(present_top.mean()) if len(top) else 0.0,
            "all_count": int(present_all.sum()),
            "mean_sortino_with": float(all_with["sortino"].mean()) if len(all_with) else np.nan,
            "mean_sortino_without": float(all_without["sortino"].mean()) if len(all_without) else np.nan,
            "mean_cagr_with": float(all_with["cagr"].mean()) if len(all_with) else np.nan,
            "mean_cagr_without": float(all_without["cagr"].mean()) if len(all_without) else np.nan,
        })
    return pd.DataFrame(records).sort_values(
        ["top_count", "mean_sortino_with"], ascending=[False, False]
    )


def _write_report(
    results: pd.DataFrame,
    benches: pd.DataFrame,
    importance: pd.DataFrame,
    args: argparse.Namespace,
) -> None:
    top = results.head(args.top)
    lines = [
        "# Stage 1 Close-Only Results",
        "",
        "Status: exploratory grid output. This is not a deploy verdict.",
        "",
        f"Configs tested: {len(results):,}",
        f"Signal subset range: n={args.min_n}..{args.max_n}",
        f"Off leg: `{args.off_leg}`",
        "",
        "## Top Configs",
        "",
        top[["branch", "risk_on", "n", "k", "sortino", "cagr", "sharpe", "mdd", "calmar", "end_rel_to_benchmark", "signals"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Native Benchmarks",
        "",
        benches[["branch", "risk_on", "label", "sortino", "cagr", "sharpe", "mdd", "calmar", "end_rel_to_benchmark"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Indicator Importance: Top 5% Frequency",
        "",
        importance.head(30).to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Method Notes",
        "",
        "- Signals are lagged one trading day before earning returns to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.",
        "- Moving-average/LRS controls follow Gayed `[leverage_for_the_long_run, p.13]`.",
        "- This runner is exploratory; final claims require PBO, DSR, WF, OOS, FWD and bootstrap gates `[advances_fin_ml, p.208-211]`.",
    ]
    (OUT_DIR / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(results: pd.DataFrame, benches: pd.DataFrame, args: argparse.Namespace) -> None:
    manifest = {
        "stage": "stage1_close_only",
        "max_n": args.max_n,
        "min_n": args.min_n,
        "off_leg": args.off_leg,
        "signal_limit": args.signal_limit,
        "configs_tested": int(len(results)),
        "benchmarks_tested": int(len(benches)),
        "primary_citation": "[advances_fin_ml, p.208-211]",
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
