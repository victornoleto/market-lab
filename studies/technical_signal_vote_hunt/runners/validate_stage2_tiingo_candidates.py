"""Validate selected Stage 2 Tiingo candidates.

This runner applies the same hard-gate style used by Stage 1/3 validation to
real-inception Tiingo candidates, including explicit execution lag. It is meant
for fixed candidates sourced from Stage 2 local/grid outputs; every source grid
or local search still contributes to DSR trial accounting `[advances_fin_ml,
p.222-223]`.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from market_lab.backtest.data.tiingo_storage import TiingoStorage
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import _metrics_row_np
from studies.technical_signal_vote_hunt.runners.run_stage2_tiingo_ohlc import (
    BRANCHES,
    Prepared,
    _prepare,
    _simulate_on_off_lag_np,
    _window_prepared,
)
from studies.technical_signal_vote_hunt.runners.validate_stage1_candidates import (
    _bootstrap,
    _dsr,
    _fwd_post_2020,
    _oos_70_30,
    _pbo_by_panel,
    _walk_forward,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = REPO_ROOT / "studies/technical_signal_vote_hunt/reports/stage2_tiingo_validation"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate selected Stage 2 Tiingo candidates")
    p.add_argument("--candidates", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, default=OUT_DIR)
    p.add_argument("--off-leg", choices=["ZROZ", "BIL", "CASH_USD"], default="CASH_USD")
    p.add_argument("--extra-lag-days", type=int, default=1)
    p.add_argument("--start-date", default=None)
    p.add_argument("--end-date", default=None)
    p.add_argument("--storage-root", type=Path, default=REPO_ROOT / "data/tiingo")
    p.add_argument("--n-trials", type=int, default=122_644_986)
    p.add_argument("--bootstrap-n", type=int, default=2_000)
    p.add_argument("--bootstrap-block", type=int, default=21)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--wf-windows", type=int, default=8)
    p.add_argument("--pbo-blocks", type=int, default=10)
    p.add_argument("--pbo-group", choices=["branch-risk-on", "branch", "all"], default="branch-risk-on")
    p.add_argument("--top", type=int, default=40)
    p.add_argument("--progress", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.extra_lag_days < 0:
        raise SystemExit("--extra-lag-days must be >= 0")
    out_dir = args.out_dir
    tables_dir = out_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    rng = np.random.default_rng(args.seed)

    candidates = pd.read_csv(args.candidates).head(args.top).copy()
    storage = TiingoStorage(args.storage_root)
    prepared: dict[tuple[str, str], Prepared] = {}
    for row in candidates.itertuples(index=False):
        key = (row.branch, row.risk_on)
        if key not in prepared:
            spec = BRANCHES[key]
            prepared[key] = _window_prepared(_prepare(spec, args.off_leg, storage), args.start_date, args.end_date)

    metric_rows: list[dict] = []
    gate_rows: list[dict] = []
    wf_rows: list[dict] = []
    bootstrap_rows: list[dict] = []
    returns_by_label: dict[str, pd.Series] = {}

    for i, row in enumerate(candidates.itertuples(index=False), start=1):
        arr = prepared[(row.branch, row.risk_on)]
        label = f"{row.branch}_{row.risk_on}_n{int(row.n)}k{int(row.k)}_rank{i:02d}"
        returns = _candidate_returns(arr, str(row.signals), int(row.k), args.extra_lag_days)
        series = pd.Series(returns, index=arr.dates, name=label)
        bench = pd.Series(arr.benchmark_returns, index=arr.dates, name="benchmark")
        returns_by_label[label] = series
        if args.progress:
            print(f"validating {i}/{len(candidates)} {label}", flush=True)

        metric_rows.append(_metrics_row_np(
            returns=returns,
            benchmark_returns=arr.benchmark_returns,
            dates=arr.dates,
            label=label,
            branch=row.branch,
            risk_on=row.risk_on,
            n=int(row.n),
            k=int(row.k),
            signals=str(row.signals),
        ))
        oos = _oos_70_30(series)
        fwd = _fwd_post_2020(series)
        dsr_row = _dsr(series, args.n_trials)
        boot = _bootstrap(series, args.bootstrap_n, args.bootstrap_block, rng)
        wf = _walk_forward(series, bench, args.wf_windows)
        wf_rows.extend({"label": label, **r} for r in wf["windows"])
        bootstrap_rows.append({"label": label, **boot})
        gate_rows.append({
            "label": label,
            "branch": row.branch,
            "risk_on": row.risk_on,
            "n": int(row.n),
            "k": int(row.k),
            "signals": str(row.signals),
            "oos_sharpe": oos["sharpe"],
            "oos_pass": oos["pass"],
            "fwd_sharpe": fwd["sharpe"],
            "fwd_pass": fwd["pass"],
            "wf_pass_windows": wf["pass_windows"],
            "wf_n_windows": wf["n_windows"],
            "wf_pass": wf["pass"],
            "bootstrap_ci_low_sharpe": boot["ci_low_sharpe"],
            "bootstrap_pass": boot["pass"],
            "dsr_value": dsr_row["dsr"],
            "dsr_p_value": dsr_row["p_value"],
            "dsr_pass": dsr_row["pass"],
        })

    pbo_rows = _pbo_by_panel(returns_by_label, candidates, args.pbo_blocks, args.pbo_group)
    gates = pd.DataFrame(gate_rows)
    pbo_df = pd.DataFrame(pbo_rows)
    gates = gates.merge(pbo_df[["label", "pbo", "pbo_pass"]], on="label", how="left")
    gates["all_hard_gates_pass"] = gates[["oos_pass", "fwd_pass", "wf_pass", "bootstrap_pass", "dsr_pass", "pbo_pass"]].all(axis=1)

    metrics = pd.DataFrame(metric_rows)
    wf_df = pd.DataFrame(wf_rows)
    boot_df = pd.DataFrame(bootstrap_rows)
    metrics.to_csv(tables_dir / "candidate_metrics.csv", index=False)
    gates.to_csv(tables_dir / "gates.csv", index=False)
    wf_df.to_csv(tables_dir / "walk_forward.csv", index=False)
    boot_df.to_csv(tables_dir / "bootstrap.csv", index=False)
    pbo_df.to_csv(tables_dir / "pbo_panel.csv", index=False)
    _write_report(metrics, gates, args, time.perf_counter() - started, out_dir)
    _write_manifest(args, len(candidates), time.perf_counter() - started, out_dir)
    print(f"Wrote validation report to {out_dir / 'REPORT.md'}", flush=True)
    return 0


def _candidate_returns(arr: Prepared, signals: str, k: int, extra_lag_days: int) -> np.ndarray:
    idx = [arr.signal_names.index(name) for name in signals.split("|")]
    sub = arr.signal_matrix[:, idx]
    valid = ~np.isnan(sub).any(axis=1)
    counts = np.nansum(sub, axis=1)
    signal = np.where(valid, counts >= k, False)
    return _simulate_on_off_lag_np(signal, arr.on_returns, arr.off_returns, extra_lag_days)


def _write_report(metrics: pd.DataFrame, gates: pd.DataFrame, args: argparse.Namespace, elapsed: float, out_dir: Path) -> None:
    lines = [
        "# Stage 2 Tiingo Candidate Validation",
        "",
        "Status: real-ETF validation report for selected Tiingo candidates. This is research-only.",
        "",
        f"Candidates: {len(gates)}",
        f"Off leg: `{args.off_leg}`",
        f"Extra lag days: `{args.extra_lag_days}`",
        f"DSR n_trials: {args.n_trials:,}",
        f"Bootstrap paths: {args.bootstrap_n:,}",
        f"PBO group: {args.pbo_group}",
        f"Elapsed seconds: {elapsed:.1f}",
        "",
        "## Gate Summary",
        "",
        gates[["label", "oos_pass", "fwd_pass", "wf_pass", "bootstrap_pass", "dsr_pass", "pbo_pass", "all_hard_gates_pass", "dsr_p_value", "pbo"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Top Metrics",
        "",
        metrics.head(20)[["label", "branch", "risk_on", "n", "k", "sortino", "cagr", "sharpe", "mdd", "calmar", "signals"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Method Notes",
        "",
        "- Tiingo OHLC is adjusted before signals; candidates are lagged by `1 + extra_lag_days` bars before earning returns `[quant_trading_chan, p.37]`, `[advances_fin_ml, p.31-34]`.",
        "- DSR/PBO remain hard gates; CAGR/MDD are tier diagnostics only `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.",
    ]
    (out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(args: argparse.Namespace, candidates: int, elapsed: float, out_dir: Path) -> None:
    manifest = {
        "stage": "stage2_tiingo_candidate_validation",
        "candidates": candidates,
        "source_candidates": str(args.candidates),
        "off_leg": args.off_leg,
        "extra_lag_days": args.extra_lag_days,
        "start_date": args.start_date,
        "end_date": args.end_date,
        "n_trials": args.n_trials,
        "bootstrap_n": args.bootstrap_n,
        "pbo_group": args.pbo_group,
        "elapsed_seconds": elapsed,
        "primary_citation": "[advances_fin_ml, p.208-211]",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
