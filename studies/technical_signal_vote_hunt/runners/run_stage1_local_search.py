"""Exact local search around a Stage 1 GA incumbent.

This runner is deliberately small and exhaustive over a one-edit neighborhood:
base set, one-signal drops, one-signal additions, and one-for-one swaps. It is a
candidate-discovery diagnostic only; every evaluated neighbor counts toward later
DSR trial accounting `[advances_fin_ml, p.222-223]`, and any selected candidate
still requires the hard validation stack `[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.core.data_loader import load_testfolio_series
from studies.technical_signal_vote_hunt.core import STAGE1_BRANCHES, daily_returns
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import (
    FIELDNAMES,
    _metrics_row_np,
    _prepare_branch,
    _simulate_on_off_np,
)
from studies.technical_signal_vote_hunt.runners.run_stage1_ga import _fitness

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_ROOT = REPO_ROOT / "studies/technical_signal_vote_hunt/results/stage1_local_search"

DEFAULT_BASE_SIGNALS = "|".join(
    [
        "px_gt_sma10",
        "px_gt_sma20",
        "px_gt_ema100",
        "px_gt_ema200",
        "px_gt_ema250",
        "roc20_gt_0",
        "roc60_gt_0",
    ]
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Exact one-edit local search around a Stage 1 vote-k incumbent")
    p.add_argument("--branch", choices=["SPY", "QQQ"], default="QQQ")
    p.add_argument("--risk-on", choices=["SSO_2x", "UPRO_3x", "QLD_2x", "TQQQ_3x"], default="QLD_2x")
    p.add_argument("--off-leg", choices=["ZROZSIM", "CASHX"], default="ZROZSIM")
    p.add_argument("--base-signals", default=DEFAULT_BASE_SIGNALS, help="Pipe-separated incumbent signals")
    p.add_argument("--base-k", type=int, default=5)
    p.add_argument("--top", type=int, default=100)
    p.add_argument("--cagr-weight", type=float, default=0.50)
    p.add_argument("--calmar-weight", type=float, default=0.20)
    p.add_argument("--mdd-penalty", type=float, default=0.15)
    p.add_argument("--complexity-penalty", type=float, default=0.01)
    p.add_argument("--complexity-free-n", type=int, default=6)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    _validate_args(args)
    started = time.perf_counter()

    spec = _select_branch(args.branch, args.risk_on)
    off_returns = daily_returns(load_testfolio_series(args.off_leg))
    branch = _prepare_branch(spec, off_returns, signal_limit=None)
    name_to_idx = {name: i for i, name in enumerate(branch.signal_names)}
    base_names = _parse_base_signals(args.base_signals, name_to_idx)

    out_dir = OUT_ROOT / f"{args.branch}_{args.risk_on}_{args.off_leg}_local"
    tables_dir = out_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    results_path = tables_dir / "local_search_results.csv"

    subsets = _build_neighborhood(base_names, branch.signal_names)
    rows = []
    for neighborhood, change, names in subsets:
        rows.extend(_evaluate_subset(branch, names, neighborhood, change, args))

    results = pd.DataFrame(rows).sort_values(["fitness", "sortino", "cagr"], ascending=[False, False, False])
    results.to_csv(results_path, index=False)
    _write_report(out_dir, results, args, base_names, len(subsets), elapsed=time.perf_counter() - started)
    _write_manifest(out_dir, args, base_names, len(subsets), len(results), elapsed=time.perf_counter() - started)

    best = results.iloc[0]
    print(
        f"done subsets={len(subsets):,} configs={len(results):,} "
        f"best_fit={best['fitness']:.4f} sortino={best['sortino']:.4f} "
        f"cagr={best['cagr']:.2%} mdd={best['mdd']:.2%} "
        f"n={int(best['n'])} k={int(best['k'])} output={results_path}",
        flush=True,
    )
    return 0


def _validate_args(args: argparse.Namespace) -> None:
    if args.branch == "SPY" and args.risk_on not in {"SSO_2x", "UPRO_3x"}:
        raise SystemExit("SPY branch supports SSO_2x or UPRO_3x")
    if args.branch == "QQQ" and args.risk_on not in {"QLD_2x", "TQQQ_3x"}:
        raise SystemExit("QQQ branch supports QLD_2x or TQQQ_3x")
    if args.base_k < 1:
        raise SystemExit("base-k must be >= 1")


def _select_branch(branch: str, risk_on: str):
    for spec in STAGE1_BRANCHES:
        if spec.branch == branch and spec.risk_on_label == risk_on:
            return spec
    raise SystemExit(f"No Stage 1 branch for {branch=} {risk_on=}")


def _parse_base_signals(raw: str, name_to_idx: dict[str, int]) -> tuple[str, ...]:
    names = tuple(name.strip() for name in raw.split("|") if name.strip())
    if not names:
        raise SystemExit("base-signals cannot be empty")
    missing = [name for name in names if name not in name_to_idx]
    if missing:
        raise SystemExit(f"Unknown base signals: {missing}")
    if len(set(names)) != len(names):
        raise SystemExit("base-signals contains duplicates")
    return names


def _build_neighborhood(base_names: tuple[str, ...], all_names: list[str]) -> list[tuple[str, str, tuple[str, ...]]]:
    base = frozenset(base_names)
    outside = [name for name in all_names if name not in base]
    seen: set[frozenset[str]] = set()
    out: list[tuple[str, str, tuple[str, ...]]] = []

    def add(neighborhood: str, change: str, names: frozenset[str]) -> None:
        if names in seen:
            return
        seen.add(names)
        ordered = tuple(name for name in all_names if name in names)
        out.append((neighborhood, change, ordered))

    add("base", "none", base)
    for drop in base_names:
        add("drop1", f"-{drop}", base - {drop})
    for add_name in outside:
        add("add1", f"+{add_name}", base | {add_name})
    for drop in base_names:
        for add_name in outside:
            add("swap1", f"-{drop}+{add_name}", (base - {drop}) | {add_name})
    return out


def _evaluate_subset(branch, names: tuple[str, ...], neighborhood: str, change: str, args: argparse.Namespace) -> list[dict]:
    idx = [branch.signal_names.index(name) for name in names]
    sub = branch.signal_matrix[:, idx]
    valid = ~np.isnan(sub).any(axis=1)
    counts = np.nansum(sub, axis=1)
    rows = []
    signal_text = "|".join(names)
    for k in range(1, len(names) + 1):
        raw_signal = np.where(valid, counts >= k, False)
        returns = _simulate_on_off_np(raw_signal, branch.on_returns, branch.off_returns)
        row = _metrics_row_np(
            returns=returns,
            benchmark_returns=branch.benchmark_returns,
            dates=branch.dates,
            label="local_vote_k",
            branch=branch.spec.branch,
            risk_on=branch.spec.risk_on_label,
            n=len(names),
            k=k,
            signals=signal_text,
        )
        rows.append({"neighborhood": neighborhood, "change": change, "fitness": _fitness(row, args), **row})
    return rows


def _write_report(
    out_dir: Path,
    results: pd.DataFrame,
    args: argparse.Namespace,
    base_names: tuple[str, ...],
    n_subsets: int,
    elapsed: float,
) -> None:
    base_mask = (results["neighborhood"] == "base") & (results["k"] == args.base_k)
    base_row = results[base_mask].head(1)
    lines = [
        "# Stage 1 Local Search Results",
        "",
        "Status: exact one-edit neighborhood diagnostic. This is not a deploy verdict.",
        "",
        f"Branch: `{args.branch}`",
        f"Risk-on: `{args.risk_on}`",
        f"Off leg: `{args.off_leg}`",
        f"Base k: `{args.base_k}`",
        f"Base signals: `{ '|'.join(base_names) }`",
        f"Neighbor subsets: {n_subsets:,}",
        f"Configs tested: {len(results):,}",
        f"Elapsed seconds: {elapsed:.1f}",
        "",
        "## Base Incumbent",
        "",
        base_row[["fitness", "n", "k", "sortino", "cagr", "sharpe", "mdd", "calmar", "signals"]].to_markdown(index=False, floatfmt=".4f") if len(base_row) else "Base row not found.",
        "",
        "## Top Local Candidates",
        "",
        results.head(args.top)[["neighborhood", "change", "fitness", "n", "k", "sortino", "cagr", "sharpe", "mdd", "calmar", "signals"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Best By Neighborhood",
        "",
        results.sort_values(["fitness", "sortino", "cagr"], ascending=[False, False, False])
        .groupby("neighborhood", as_index=False)
        .head(1)[["neighborhood", "change", "fitness", "n", "k", "sortino", "cagr", "mdd", "signals"]]
        .to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Method Notes",
        "",
        "- Neighborhood = base, one-signal drops, one-signal additions, and one-for-one swaps.",
        "- All valid `k=1..n` thresholds are evaluated for every neighbor.",
        "- Signals are lagged one trading day before earning returns to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.",
        "- This is candidate discovery only; final claims require PBO/DSR/WF/OOS/FWD/bootstrap gates `[advances_fin_ml, p.208-211]`.",
    ]
    (out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(
    out_dir: Path,
    args: argparse.Namespace,
    base_names: tuple[str, ...],
    n_subsets: int,
    n_configs: int,
    elapsed: float,
) -> None:
    manifest = {
        "stage": "stage1_local_search",
        "branch": args.branch,
        "risk_on": args.risk_on,
        "off_leg": args.off_leg,
        "base_k": args.base_k,
        "base_signals": list(base_names),
        "neighbor_subsets": n_subsets,
        "configs_tested": n_configs,
        "elapsed_seconds": elapsed,
        "primary_citation": "[advances_fin_ml, p.208-211]",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
