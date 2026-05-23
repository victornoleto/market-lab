"""Honest validation runner for Stage 1 selected candidates.

Validates selected top candidates from the Stage 1 exact grid with OOS, FWD,
walk-forward, bootstrap, DSR and candidate-panel PBO. This runner is deliberately
separate from search runners so discovery and validation remain auditable
`[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from market_lab.backtest.validation.dsr import dsr
from market_lab.backtest.validation.pbo import pbo
from market_lab.backtest.data.testfolio_loader import load_testfolio_series
from studies.technical_signal_vote_hunt.core import STAGE1_BRANCHES, daily_returns
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import (
    _metrics_row_np,
    _prepare_branch,
    _simulate_on_off_np,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CANDIDATES = (
    REPO_ROOT
    / "studies/technical_signal_vote_hunt/reports/stage1_top_strategies/tables/selected_top_candidates.csv"
)
OUT_DIR = REPO_ROOT / "studies/technical_signal_vote_hunt/reports/stage1_validation"
TRADING_DAYS_PER_YEAR = 252


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate Stage 1 selected candidates")
    p.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    p.add_argument("--out-dir", type=Path, default=OUT_DIR)
    p.add_argument("--off-leg", choices=["ZROZSIM", "CASHX"], default="ZROZSIM")
    p.add_argument("--n-trials", type=int, default=5_471_268)
    p.add_argument("--bootstrap-n", type=int, default=2_000)
    p.add_argument("--bootstrap-block", type=int, default=21)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--wf-windows", type=int, default=8)
    p.add_argument("--pbo-blocks", type=int, default=10)
    p.add_argument(
        "--pbo-group",
        choices=["branch-risk-on", "branch", "all"],
        default="branch-risk-on",
        help="Candidate-panel PBO grouping. Small panels are diagnostic only.",
    )
    p.add_argument("--progress", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir
    tables_dir = out_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    rng = np.random.default_rng(args.seed)

    candidates = pd.read_csv(args.candidates)
    off_returns = daily_returns(load_testfolio_series(args.off_leg))
    branch_arrays = {
        (spec.branch, spec.risk_on_label): _prepare_branch(spec, off_returns, signal_limit=None)
        for spec in STAGE1_BRANCHES
    }

    metric_rows: list[dict] = []
    gate_rows: list[dict] = []
    wf_rows: list[dict] = []
    bootstrap_rows: list[dict] = []
    returns_by_label: dict[str, pd.Series] = {}

    for i, row in enumerate(candidates.itertuples(index=False), start=1):
        arr = branch_arrays[(row.branch, row.risk_on)]
        label = f"{row.branch}_{row.risk_on}_n{int(row.n)}k{int(row.k)}_rank{i:02d}"
        returns = _candidate_returns(arr, str(row.signals), int(row.k))
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
            "dsr_observed_sharpe_per_bar": dsr_row["observed_sharpe"],
            "dsr_benchmark_sharpe_per_bar": dsr_row["benchmark_sharpe"],
            "dsr_value": dsr_row["dsr"],
            "dsr_p_value": dsr_row["p_value"],
            "dsr_pass": dsr_row["pass"],
        })

    pbo_rows = _pbo_by_panel(returns_by_label, candidates, args.pbo_blocks, args.pbo_group)
    gates = pd.DataFrame(gate_rows)
    pbo_df = pd.DataFrame(pbo_rows)
    gates = gates.merge(pbo_df[["label", "pbo", "pbo_pass"]], on="label", how="left")
    gates["all_hard_gates_pass"] = gates[[
        "oos_pass", "fwd_pass", "wf_pass", "bootstrap_pass", "dsr_pass", "pbo_pass"
    ]].all(axis=1)

    metrics = pd.DataFrame(metric_rows)
    wf_df = pd.DataFrame(wf_rows)
    boot_df = pd.DataFrame(bootstrap_rows)
    metrics.to_csv(tables_dir / "candidate_metrics.csv", index=False)
    gates.to_csv(tables_dir / "gates.csv", index=False)
    wf_df.to_csv(tables_dir / "walk_forward.csv", index=False)
    boot_df.to_csv(tables_dir / "bootstrap.csv", index=False)
    pbo_df.to_csv(tables_dir / "pbo_panel.csv", index=False)
    _write_report(metrics, gates, wf_df, boot_df, pbo_df, args, time.perf_counter() - started, out_dir)
    _write_manifest(args, len(candidates), time.perf_counter() - started, out_dir)
    print(f"Wrote validation report to {out_dir / 'REPORT.md'}", flush=True)
    return 0


def _candidate_returns(arr, signals: str, k: int) -> np.ndarray:
    idx = [arr.signal_names.index(name) for name in signals.split("|")]
    sub = arr.signal_matrix[:, idx]
    valid = ~np.isnan(sub).any(axis=1)
    counts = np.nansum(sub, axis=1)
    signal = np.where(valid, counts >= k, False)
    return _simulate_on_off_np(signal, arr.on_returns, arr.off_returns)


def _sharpe(r: np.ndarray) -> float:
    if len(r) < 2:
        return 0.0
    std = float(np.std(r, ddof=1))
    return float(np.mean(r) / std * np.sqrt(TRADING_DAYS_PER_YEAR)) if std > 0 else 0.0


def _oos_70_30(returns: pd.Series) -> dict:
    r = returns.dropna().to_numpy(dtype=float)
    split = int(len(r) * 0.70)
    s = _sharpe(r[split:])
    return {"sharpe": s, "pass": bool(s > 0.0)}


def _fwd_post_2020(returns: pd.Series) -> dict:
    r = returns[returns.index >= "2020-01-01"].dropna().to_numpy(dtype=float)
    s = _sharpe(r)
    return {"sharpe": s, "pass": bool(len(r) >= 252 and s > 0.0)}


def _dsr(returns: pd.Series, n_trials: int) -> dict:
    result = dsr(returns.dropna().to_numpy(dtype=float), n_trials=n_trials)
    return {
        "observed_sharpe": float(result.observed_sharpe),
        "benchmark_sharpe": float(result.benchmark_sharpe),
        "dsr": float(result.dsr),
        "p_value": float(result.p_value),
        "pass": bool(result.p_value < 0.05),
    }


def _bootstrap(returns: pd.Series, n_boot: int, block: int, rng: np.random.Generator) -> dict:
    r = returns.dropna().to_numpy(dtype=float)
    vals = np.empty(n_boot, dtype=float)
    n = len(r)
    n_blocks = int(np.ceil(n / block))
    for i in range(n_boot):
        starts = rng.integers(0, max(1, n - block + 1), size=n_blocks)
        sample = np.concatenate([r[s:s + block] for s in starts])[:n]
        vals[i] = _sharpe(sample)
    low = float(np.percentile(vals, 1.0))
    return {
        "n_boot": int(n_boot),
        "block": int(block),
        "ci_low_sharpe": low,
        "ci_median_sharpe": float(np.percentile(vals, 50.0)),
        "ci_high_sharpe": float(np.percentile(vals, 99.0)),
        "pass": bool(low > 0.0),
    }


def _walk_forward(returns: pd.Series, benchmark: pd.Series, n_windows: int) -> dict:
    aligned = pd.concat({"r": returns, "b": benchmark}, axis=1, sort=False).dropna()
    n = len(aligned)
    size = n // n_windows
    rows = []
    pass_windows = 0
    for i in range(n_windows):
        start = i * size
        end = n if i == n_windows - 1 else (i + 1) * size
        sub = aligned.iloc[start:end]
        r = sub["r"].to_numpy(dtype=float)
        b = sub["b"].to_numpy(dtype=float)
        eq = np.cumprod(1.0 + r)
        beq = np.cumprod(1.0 + b)
        rel = eq / beq
        warmup = min(252, max(0, len(rel) // 5))
        pct_above = float(np.mean(rel[warmup:] > 1.0)) if len(rel) > warmup else 0.0
        s = _sharpe(r)
        passed = pct_above >= 0.50 and s > 0.0
        pass_windows += int(passed)
        rows.append({
            "window": i + 1,
            "start": str(sub.index.min().date()),
            "end": str(sub.index.max().date()),
            "sharpe": s,
            "pct_above_benchmark": pct_above,
            "pass": bool(passed),
        })
    return {
        "windows": rows,
        "pass_windows": int(pass_windows),
        "n_windows": int(n_windows),
        "pass": bool(pass_windows >= 6),
    }


def _pbo_by_panel(
    returns_by_label: dict[str, pd.Series],
    candidates: pd.DataFrame,
    n_blocks: int,
    group_mode: str,
) -> list[dict]:
    rows = []
    group_cols = {
        "branch-risk-on": ["branch", "risk_on"],
        "branch": ["branch"],
        "all": [],
    }[group_mode]
    groups = [((), candidates)] if not group_cols else candidates.groupby(group_cols, sort=True)
    for key, sub in groups:
        if group_mode == "branch-risk-on":
            branch, risk_on = key
            labels = [label for label in returns_by_label if label.startswith(f"{branch}_{risk_on}_")]
        elif group_mode == "branch":
            branch = key[0] if isinstance(key, tuple) else key
            risk_on = "*"
            labels = [label for label in returns_by_label if label.startswith(f"{branch}_")]
        else:
            branch = "*"
            risk_on = "*"
            labels = list(returns_by_label)
        panel = pd.concat({label: returns_by_label[label] for label in labels}, axis=1, sort=False).dropna()
        if panel.shape[1] < 2 or len(panel) < 252:
            pbo_value = np.nan
            pbo_pass = True
        else:
            res = pbo(panel.to_numpy(dtype=float), n_blocks=n_blocks)
            pbo_value = float(res.pbo)
            pbo_pass = bool(res.pbo < 0.5)
        for label in labels:
            rows.append({
                "label": label,
                "branch": branch,
                "risk_on": risk_on,
                "pbo_group": group_mode,
                "panel_size": len(labels),
                "pbo": pbo_value,
                "pbo_pass": pbo_pass,
            })
    return rows


def _write_report(
    metrics: pd.DataFrame,
    gates: pd.DataFrame,
    wf: pd.DataFrame,
    boot: pd.DataFrame,
    pbo_df: pd.DataFrame,
    args: argparse.Namespace,
    elapsed: float,
    out_dir: Path,
) -> None:
    lines = [
        "# Stage 1 Candidate Validation",
        "",
        "Status: validation report for selected Stage 1 close-only candidates. This is still research-only.",
        "",
        f"Candidates: {len(gates)}",
        f"DSR n_trials: {args.n_trials:,}",
        f"Bootstrap paths: {args.bootstrap_n:,}",
        f"PBO group: {args.pbo_group}",
        f"Elapsed seconds: {elapsed:.1f}",
        "",
        "## Gate Summary",
        "",
        gates[["label", "oos_pass", "fwd_pass", "wf_pass", "bootstrap_pass", "dsr_pass", "pbo_pass", "all_hard_gates_pass", "dsr_p_value", "pbo"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Headline Metrics",
        "",
        metrics[["label", "branch", "risk_on", "n", "k", "sortino", "cagr", "sharpe", "mdd", "calmar", "signals"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Interpretation",
        "",
        "A candidate passes this validation only if all hard gates pass. DSR uses conservative global trial accounting from the Stage 1 exact grid `[advances_fin_ml, p.222-223]`.",
        "Candidate-panel PBO is diagnostic over the selected top-k set; it is not a literal PBO over all evaluated configs.",
        "",
        "## Output Tables",
        "",
        "- `tables/candidate_metrics.csv`",
        "- `tables/gates.csv`",
        "- `tables/walk_forward.csv`",
        "- `tables/bootstrap.csv`",
        "- `tables/pbo_panel.csv`",
    ]
    (out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(args: argparse.Namespace, n_candidates: int, elapsed: float, out_dir: Path) -> None:
    manifest = {
        "report": "stage1_validation",
        "candidates": str(args.candidates),
        "out_dir": str(args.out_dir),
        "n_candidates": n_candidates,
        "off_leg": args.off_leg,
        "n_trials": args.n_trials,
        "bootstrap_n": args.bootstrap_n,
        "bootstrap_block": args.bootstrap_block,
        "wf_windows": args.wf_windows,
        "pbo_blocks": args.pbo_blocks,
        "pbo_group": args.pbo_group,
        "seed": args.seed,
        "elapsed_seconds": elapsed,
        "primary_citation": "[advances_fin_ml, p.208-211]",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
