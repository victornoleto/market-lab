"""Fast Stage 1 close-only technical signal vote grid.

This runner is designed for large exact sweeps. It precomputes each branch into
NumPy arrays once, then evaluates `n`/`k` combinations without per-config pandas
alignment overhead. Progress is printed during the run so the loop can be
monitored directly from the Python process.

Important: an exhaustive sweep over all subset sizes is still exponential. With
33 close-only signals, `n=1..33` means `(2**33 - 1)` subsets before the `k`
dimension, which is not a practical exact grid. Use `--estimate`, capped
`--max-n`, or later a beam-search layer before attempting huge runs
`[advances_fin_ml, p.222-223]`.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.core.data_loader import load_testfolio_series
from studies.technical_signal_vote_hunt.core import (
    STAGE1_BRANCHES,
    BranchSpec,
    build_close_only_signals,
    build_rearm_gate,
    build_t3d_k2_signal,
    daily_returns,
    vote_signal,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = REPO_ROOT / "studies/technical_signal_vote_hunt/results/stage1_close_only_fast"
TABLES_DIR = OUT_DIR / "tables"
RESULTS_CSV = TABLES_DIR / "stage1_results_fast.csv"
BENCH_CSV = TABLES_DIR / "stage1_native_benchmarks_fast.csv"
IMPORTANCE_CSV = TABLES_DIR / "indicator_importance_top5pct_fast.csv"

TRADING_DAYS_PER_YEAR = 252.0
FIELDNAMES = [
    "label", "branch", "risk_on", "n", "k", "signals",
    "cagr", "sharpe", "sortino", "mdd", "calmar", "vol_annual",
    "end_mult", "end_rel_to_benchmark", "pct_above_benchmark",
    "start", "end", "n_days",
]


@dataclass(frozen=True)
class BranchArrays:
    spec: BranchSpec
    dates: pd.DatetimeIndex
    signal_names: list[str]
    signal_matrix: np.ndarray
    on_returns: np.ndarray
    off_returns: np.ndarray
    benchmark_returns: np.ndarray
    t3d_signal: np.ndarray
    lrs_signal: np.ndarray


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fast Stage 1 close-only vote-k grid")
    p.add_argument("--min-n", type=int, default=1)
    p.add_argument("--max-n", type=int, default=3, help="0 means all available signals")
    p.add_argument("--off-leg", choices=["ZROZSIM", "CASHX"], default="ZROZSIM")
    p.add_argument("--signal-limit", type=int, default=None)
    p.add_argument("--progress-every", type=int, default=10_000, help="print every N configs; use 1 for every config")
    p.add_argument("--top", type=int, default=50)
    p.add_argument("--estimate", action="store_true", help="only print estimated config count")
    p.add_argument("--allow-huge", action="store_true", help="allow estimated grids above --huge-threshold")
    p.add_argument("--huge-threshold", type=int, default=2_000_000)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    off_returns = daily_returns(load_testfolio_series(args.off_leg))
    branches = [_prepare_branch(spec, off_returns, args.signal_limit) for spec in STAGE1_BRANCHES]
    n_signals = len(branches[0].signal_names)
    max_n = n_signals if args.max_n == 0 else args.max_n
    if args.min_n < 1 or max_n < args.min_n or max_n > n_signals:
        raise SystemExit(f"Require 1 <= min_n <= max_n <= {n_signals}; got {args.min_n}..{max_n}")

    estimated = estimate_config_count(n_signals=n_signals, min_n=args.min_n, max_n=max_n) * len(branches)
    print(f"signals={n_signals} branches={len(branches)} n={args.min_n}..{max_n} estimated_configs={estimated:,}", flush=True)
    if args.estimate:
        return 0
    if estimated > args.huge_threshold and not args.allow_huge:
        raise SystemExit(
            f"Estimated {estimated:,} configs exceeds threshold {args.huge_threshold:,}. "
            "Re-run with --allow-huge or reduce --max-n."
        )

    started = time.perf_counter()
    bench_rows = []
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        processed = 0
        for branch in branches:
            for row in _benchmark_rows(branch):
                bench_rows.append(row)
            for row in _iter_vote_rows(branch, args.min_n, max_n):
                writer.writerow(row)
                processed += 1
                if args.progress_every > 0 and processed % args.progress_every == 0:
                    elapsed = max(time.perf_counter() - started, 1e-9)
                    rate = processed / elapsed
                    print(
                        f"processed={processed:,}/{estimated:,} rate={rate:,.0f}/s "
                        f"elapsed={elapsed:,.1f}s last={row['branch']}:{row['risk_on']} n={row['n']} k={row['k']}",
                        flush=True,
                    )

    benches = pd.DataFrame(bench_rows).sort_values(
        ["branch", "risk_on", "sortino", "cagr"], ascending=[True, True, False, False]
    )
    benches.to_csv(BENCH_CSV, index=False)

    results = pd.read_csv(RESULTS_CSV)
    results = results.sort_values(["sortino", "cagr", "calmar"], ascending=[False, False, False])
    results.to_csv(RESULTS_CSV, index=False)
    importance = _indicator_importance(results, top_frac=0.05)
    importance.to_csv(IMPORTANCE_CSV, index=False)
    _write_report(results, benches, importance, args, max_n=max_n, estimated=estimated)
    _write_manifest(args, max_n=max_n, estimated=estimated, results=len(results), benchmarks=len(benches))

    elapsed = time.perf_counter() - started
    print(f"done configs={len(results):,} elapsed={elapsed:,.1f}s output={RESULTS_CSV}", flush=True)
    return 0


def estimate_config_count(n_signals: int, min_n: int, max_n: int) -> int:
    return sum(math.comb(n_signals, n) * n for n in range(min_n, max_n + 1))


def _prepare_branch(
    spec: BranchSpec,
    off_returns: pd.Series,
    signal_limit: int | None,
) -> BranchArrays:
    signal_prices = load_testfolio_series(spec.signal_ticker)
    on_returns = daily_returns(load_testfolio_series(spec.risk_on_ticker))
    benchmark_returns = daily_returns(load_testfolio_series(spec.benchmark_ticker))

    signal_map = build_close_only_signals(signal_prices)
    if signal_limit is not None:
        signal_map = dict(list(signal_map.items())[:signal_limit])
    names = list(signal_map)

    t3d = build_t3d_k2_signal(signal_prices)
    lrs_ma = signal_prices.rolling(200, min_periods=200).mean()
    lrs = (signal_prices > lrs_ma).astype(float)
    lrs[lrs_ma.isna()] = np.nan

    aligned = pd.concat(
        {
            "on": on_returns,
            "off": off_returns,
            "bench": benchmark_returns,
            "t3d": t3d,
            "lrs": lrs,
            **{f"s_{name}": signal_map[name] for name in names},
        },
        axis=1,
        sort=False,
    ).dropna(subset=["on", "off", "bench"])

    sig_cols = [f"s_{name}" for name in names]
    return BranchArrays(
        spec=spec,
        dates=aligned.index,
        signal_names=names,
        signal_matrix=aligned[sig_cols].to_numpy(dtype=np.float32),
        on_returns=aligned["on"].to_numpy(dtype=np.float64),
        off_returns=aligned["off"].to_numpy(dtype=np.float64),
        benchmark_returns=aligned["bench"].to_numpy(dtype=np.float64),
        t3d_signal=aligned["t3d"].to_numpy(dtype=np.float32),
        lrs_signal=aligned["lrs"].to_numpy(dtype=np.float32),
    )


def _iter_vote_rows(branch: BranchArrays, min_n: int, max_n: int):
    idx_by_name = range(len(branch.signal_names))
    for n in range(min_n, max_n + 1):
        for combo in itertools.combinations(idx_by_name, n):
            sub = branch.signal_matrix[:, combo]
            valid = ~np.isnan(sub).any(axis=1)
            counts = np.nansum(sub, axis=1)
            signal_names = "|".join(branch.signal_names[i] for i in combo)
            for k in range(1, n + 1):
                raw_signal = np.where(valid, counts >= k, False)
                returns = _simulate_on_off_np(raw_signal, branch.on_returns, branch.off_returns)
                yield _metrics_row_np(
                    returns=returns,
                    benchmark_returns=branch.benchmark_returns,
                    dates=branch.dates,
                    label="vote_k",
                    branch=branch.spec.branch,
                    risk_on=branch.spec.risk_on_label,
                    n=n,
                    k=k,
                    signals=signal_names,
                )


def _benchmark_rows(branch: BranchArrays) -> list[dict]:
    t3d = np.where(np.isnan(branch.t3d_signal), False, branch.t3d_signal >= 1.0)
    lrs = np.where(np.isnan(branch.lrs_signal), False, branch.lrs_signal >= 1.0)
    rearm = build_rearm_gate(pd.Series(branch.t3d_signal, index=branch.dates)).to_numpy(dtype=np.float32)
    rearm_bool = np.where(np.isnan(rearm), False, rearm >= 1.0)
    return [
        _metrics_row_np(
            branch.benchmark_returns,
            branch.benchmark_returns,
            branch.dates,
            f"{branch.spec.branch}_buy_hold",
            branch.spec.branch,
            branch.spec.risk_on_label,
            0,
            0,
            "benchmark",
        ),
        _metrics_row_np(
            _simulate_on_off_np(lrs, branch.on_returns, branch.off_returns),
            branch.benchmark_returns,
            branch.dates,
            f"{branch.spec.branch}_{branch.spec.risk_on_label}_lrs_sma200",
            branch.spec.branch,
            branch.spec.risk_on_label,
            0,
            0,
            "benchmark",
        ),
        _metrics_row_np(
            _simulate_on_off_np(t3d, branch.on_returns, branch.off_returns),
            branch.benchmark_returns,
            branch.dates,
            f"{branch.spec.branch}_{branch.spec.risk_on_label}_t3d_k2",
            branch.spec.branch,
            branch.spec.risk_on_label,
            0,
            0,
            "benchmark",
        ),
        _metrics_row_np(
            _simulate_iter030_like_np(t3d, rearm_bool, branch.on_returns, branch.off_returns),
            branch.benchmark_returns,
            branch.dates,
            f"{branch.spec.branch}_{branch.spec.risk_on_label}_iter030_like",
            branch.spec.branch,
            branch.spec.risk_on_label,
            0,
            0,
            "benchmark",
        ),
    ]


def _simulate_on_off_np(signal: np.ndarray, on_returns: np.ndarray, off_returns: np.ndarray) -> np.ndarray:
    sig_lag = np.empty_like(signal, dtype=bool)
    sig_lag[0] = False
    sig_lag[1:] = signal[:-1]
    return np.where(sig_lag, on_returns, off_returns)


def _simulate_iter030_like_np(
    signal: np.ndarray,
    rearm: np.ndarray,
    on_returns: np.ndarray,
    off_returns: np.ndarray,
    lrs_factor: float = 1.20,
) -> np.ndarray:
    sig_lag = np.empty_like(signal, dtype=bool)
    rearm_lag = np.empty_like(rearm, dtype=bool)
    sig_lag[0] = False
    rearm_lag[0] = False
    sig_lag[1:] = signal[:-1]
    rearm_lag[1:] = rearm[:-1]
    on_leg = np.where(rearm_lag, on_returns * lrs_factor, on_returns)
    return np.where(sig_lag, on_leg, off_returns)


def _metrics_row_np(
    returns: np.ndarray,
    benchmark_returns: np.ndarray,
    dates: pd.DatetimeIndex,
    label: str,
    branch: str,
    risk_on: str,
    n: int,
    k: int,
    signals: str,
) -> dict:
    mask = np.isfinite(returns) & np.isfinite(benchmark_returns)
    r = returns[mask]
    b = benchmark_returns[mask]
    d = dates[mask]
    eq = np.cumprod(1.0 + r)
    bench_eq = np.cumprod(1.0 + b)
    rel = eq / bench_eq
    mdd = _max_drawdown(eq)
    years = len(r) / TRADING_DAYS_PER_YEAR
    total = float(eq[-1]) if len(eq) else np.nan
    cagr = total ** (1.0 / years) - 1.0 if years > 0 and total > 0 else np.nan
    vol = float(np.std(r, ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR)) if len(r) > 1 else np.nan
    mean = float(np.mean(r)) if len(r) else np.nan
    std = float(np.std(r, ddof=1)) if len(r) > 1 else np.nan
    sharpe = mean / std * np.sqrt(TRADING_DAYS_PER_YEAR) if std and std > 0 else 0.0
    downside = r[r < 0.0]
    down_std = float(np.std(downside, ddof=1)) if len(downside) > 1 else 0.0
    sortino = mean / down_std * np.sqrt(TRADING_DAYS_PER_YEAR) if down_std > 0 else 0.0
    return {
        "label": label,
        "branch": branch,
        "risk_on": risk_on,
        "n": int(n),
        "k": int(k),
        "signals": signals,
        "cagr": cagr,
        "sharpe": sharpe,
        "sortino": sortino,
        "mdd": -mdd,
        "calmar": cagr / mdd if mdd > 0 else np.inf,
        "vol_annual": vol,
        "end_mult": total,
        "end_rel_to_benchmark": float(rel[-1]) if len(rel) else np.nan,
        "pct_above_benchmark": float(np.mean(rel[252:] > 1.0)) if len(rel) > 252 else np.nan,
        "start": str(d[0].date()) if len(d) else "",
        "end": str(d[-1].date()) if len(d) else "",
        "n_days": int(len(r)),
    }


def _max_drawdown(equity: np.ndarray) -> float:
    peak = np.maximum.accumulate(equity)
    dd = (peak - equity) / peak
    return float(np.max(dd))


def _indicator_importance(results: pd.DataFrame, top_frac: float) -> pd.DataFrame:
    cutoff = max(1, int(len(results) * top_frac))
    top = results.head(cutoff).copy()
    signals = sorted({s for row in results["signals"] for s in str(row).split("|") if s})
    rows = []
    split_all = results["signals"].str.split("|")
    split_top = top["signals"].str.split("|")
    for sig in signals:
        present_all = split_all.apply(lambda xs: sig in xs)
        present_top = split_top.apply(lambda xs: sig in xs)
        with_sig = results[present_all]
        without_sig = results[~present_all]
        rows.append({
            "signal": sig,
            "top_count": int(present_top.sum()),
            "top_share": float(present_top.mean()) if len(top) else 0.0,
            "all_count": int(present_all.sum()),
            "mean_sortino_with": float(with_sig["sortino"].mean()) if len(with_sig) else np.nan,
            "mean_sortino_without": float(without_sig["sortino"].mean()) if len(without_sig) else np.nan,
            "mean_cagr_with": float(with_sig["cagr"].mean()) if len(with_sig) else np.nan,
            "mean_cagr_without": float(without_sig["cagr"].mean()) if len(without_sig) else np.nan,
        })
    return pd.DataFrame(rows).sort_values(["top_count", "mean_sortino_with"], ascending=[False, False])


def _write_report(
    results: pd.DataFrame,
    benches: pd.DataFrame,
    importance: pd.DataFrame,
    args: argparse.Namespace,
    max_n: int,
    estimated: int,
) -> None:
    lines = [
        "# Stage 1 Close-Only Fast Results",
        "",
        "Status: exploratory exact-grid output. This is not a deploy verdict.",
        "",
        f"Estimated/configs tested: {estimated:,}",
        f"Signal subset range: n={args.min_n}..{max_n}",
        f"Off leg: `{args.off_leg}`",
        "",
        "## Top Configs",
        "",
        results.head(args.top)[["branch", "risk_on", "n", "k", "sortino", "cagr", "sharpe", "mdd", "calmar", "end_rel_to_benchmark", "signals"]].to_markdown(index=False, floatfmt=".4f"),
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
        "- The runner is NumPy-based and prints progress during the loop.",
        "- Exhaustive all-subset grids remain exponential; final claims require PBO/DSR/WF/OOS/FWD/bootstrap gates `[advances_fin_ml, p.208-211]`.",
    ]
    (OUT_DIR / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(
    args: argparse.Namespace,
    max_n: int,
    estimated: int,
    results: int,
    benchmarks: int,
) -> None:
    manifest = {
        "stage": "stage1_close_only_fast",
        "min_n": args.min_n,
        "max_n": max_n,
        "off_leg": args.off_leg,
        "signal_limit": args.signal_limit,
        "estimated_configs": estimated,
        "configs_tested": results,
        "benchmarks_tested": benchmarks,
        "primary_citation": "[advances_fin_ml, p.208-211]",
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
