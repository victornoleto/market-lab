"""Validate iter030 parameter-GA candidates against hard gates.

This validates the strict Pareto candidates from the small parameter GA with
OOS, FWD, walk-forward, bootstrap, DSR and a diagnostic PBO panel over all
evaluated GA genes. The panel is still small and post-search, so the result is a
research diagnostic rather than a mandate promotion `[advances_fin_ml, p.196-202]`,
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
from studies.technical_signal_vote_hunt.runners.run_iter030_param_ga import (
    _baseline_gene,
    _evaluate,
    _label,
    _load_module,
    _prepare_context,
    _returns_for_gene,
    _row_to_gene,
    ITER030_BACKTEST,
)
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import _metrics_row_np
from studies.technical_signal_vote_hunt.runners.validate_stage1_candidates import (
    _bootstrap,
    _dsr,
    _fwd_post_2020,
    _oos_70_30,
    _walk_forward,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
GA_REPORT_DIR = REPO_ROOT / "studies/technical_signal_vote_hunt/reports/iter030_param_ga"
OUT_DIR = GA_REPORT_DIR / "validation"
ALL_CANDIDATES = GA_REPORT_DIR / "tables/all_candidates.csv"
TOP_CANDIDATES = GA_REPORT_DIR / "tables/top_candidates.csv"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate strict Pareto iter030 parameter-GA candidates")
    p.add_argument("--all-candidates", type=Path, default=ALL_CANDIDATES)
    p.add_argument("--top-candidates", type=Path, default=TOP_CANDIDATES)
    p.add_argument("--out-dir", type=Path, default=OUT_DIR)
    p.add_argument("--n-trials", type=int, default=136_784_569)
    p.add_argument("--bootstrap-n", type=int, default=2_000)
    p.add_argument("--bootstrap-block", type=int, default=21)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--wf-windows", type=int, default=8)
    p.add_argument("--pbo-blocks", type=int, default=10)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    started = time.perf_counter()
    rng = np.random.default_rng(args.seed)
    tables_dir = args.out_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    top = pd.read_csv(args.top_candidates)
    all_candidates = pd.read_csv(args.all_candidates)
    baseline_ga_label = _label(_baseline_gene())
    base = top[top["label"].eq(baseline_ga_label)].iloc[0]
    strict = top[
        (top["cagr"] > float(base["cagr"]))
        & (top["sortino"] >= float(base["sortino"]))
        & (top["mdd"] >= float(base["mdd"]))
    ].copy()

    ctx = _prepare_context(_load_module(ITER030_BACKTEST, "iter030_param_validation"))
    selected = [("iter030_baseline", _baseline_gene())]
    selected.extend((row.label, _row_to_gene(row._asdict())) for row in strict.itertuples(index=False))

    returns_by_label = {label: _returns_for_gene(ctx, gene) for label, gene in selected}
    pbo_returns = {
        row.label: _returns_for_gene(ctx, _row_to_gene(row._asdict()))
        for row in all_candidates.itertuples(index=False)
    }
    pbo_value, pbo_pass = _pbo_panel(pbo_returns, args.pbo_blocks)

    metric_rows = []
    gate_rows = []
    wf_rows = []
    boot_rows = []
    bench = ctx.spy_ret.rename("benchmark")
    for label, series in returns_by_label.items():
        aligned = pd.concat({"r": series, "b": bench}, axis=1, sort=False).dropna()
        metric_rows.append(_metrics_row_np(aligned["r"].to_numpy(float), aligned["b"].to_numpy(float), pd.DatetimeIndex(aligned.index), label, "QQQ", "iter030_param_validation", 0, 0, "ga"))
        oos = _oos_70_30(series)
        fwd = _fwd_post_2020(series)
        wf = _walk_forward(series, bench, args.wf_windows)
        boot = _bootstrap(series, args.bootstrap_n, args.bootstrap_block, rng)
        dsr_row = _dsr(series, args.n_trials)
        wf_rows.extend({"label": label, **row} for row in wf["windows"])
        boot_rows.append({"label": label, **boot})
        gate_rows.append(
            {
                "label": label,
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
                "pbo": pbo_value,
                "pbo_pass": pbo_pass,
            }
        )

    metrics = pd.DataFrame(metric_rows)
    gates = pd.DataFrame(gate_rows)
    gates["all_hard_gates_pass"] = gates[["oos_pass", "fwd_pass", "wf_pass", "bootstrap_pass", "dsr_pass", "pbo_pass"]].all(axis=1)
    wf_df = pd.DataFrame(wf_rows)
    boot_df = pd.DataFrame(boot_rows)
    pbo_df = pd.DataFrame([{"panel_size": len(pbo_returns), "pbo_blocks": args.pbo_blocks, "pbo": pbo_value, "pbo_pass": pbo_pass}])

    metrics.to_csv(tables_dir / "candidate_metrics.csv", index=False)
    gates.to_csv(tables_dir / "gates.csv", index=False)
    wf_df.to_csv(tables_dir / "walk_forward.csv", index=False)
    boot_df.to_csv(tables_dir / "bootstrap.csv", index=False)
    pbo_df.to_csv(tables_dir / "pbo_panel.csv", index=False)
    _write_report(metrics, gates, pbo_df, args, time.perf_counter() - started)
    _write_manifest(args, len(selected), len(pbo_returns), time.perf_counter() - started)
    print(f"wrote {args.out_dir / 'REPORT.md'}")
    return 0


def _pbo_panel(returns_by_label: dict[str, pd.Series], n_blocks: int) -> tuple[float, bool]:
    panel = pd.concat(returns_by_label, axis=1, sort=False).dropna()
    result = pbo(panel.to_numpy(dtype=float), n_blocks=n_blocks)
    return float(result.pbo), bool(result.pbo < 0.5)


def _write_report(metrics: pd.DataFrame, gates: pd.DataFrame, pbo_df: pd.DataFrame, args: argparse.Namespace, elapsed: float) -> None:
    lines = [
        "# Iter030 Parameter GA Validation",
        "",
        "Status: honest validation diagnostic for the strict Pareto candidates from the small parameter GA.",
        "",
        f"Candidates: {len(gates)} including baseline",
        f"DSR n_trials: {args.n_trials:,}",
        f"Bootstrap paths: {args.bootstrap_n:,}",
        f"PBO panel size: {int(pbo_df.iloc[0]['panel_size'])}",
        f"Elapsed seconds: {elapsed:.1f}",
        "",
        "## Gate Summary",
        "",
        gates[["label", "oos_pass", "fwd_pass", "wf_pass", "bootstrap_pass", "dsr_pass", "pbo_pass", "all_hard_gates_pass", "dsr_p_value", "pbo"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Headline Metrics",
        "",
        metrics[["label", "sortino", "cagr", "sharpe", "mdd", "calmar", "end_mult"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Interpretation",
        "",
        "This validation is intentionally stricter than the economic-first diagnostic: PBO and DSR are hard gates again. A candidate only passes if every hard gate is true `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.",
        "The PBO panel covers the 195 genes evaluated by the small GA, not the full theoretical parameter space, so a pass would still require a larger pre-registered validation panel.",
    ]
    (args.out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(args: argparse.Namespace, n_candidates: int, pbo_panel_size: int, elapsed: float) -> None:
    manifest = {
        "report": "iter030_param_ga_validation",
        "n_candidates": n_candidates,
        "pbo_panel_size": pbo_panel_size,
        "n_trials": args.n_trials,
        "bootstrap_n": args.bootstrap_n,
        "bootstrap_block": args.bootstrap_block,
        "wf_windows": args.wf_windows,
        "pbo_blocks": args.pbo_blocks,
        "seed": args.seed,
        "elapsed_seconds": elapsed,
        "primary_citation": "[advances_fin_ml, p.208-211]",
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
