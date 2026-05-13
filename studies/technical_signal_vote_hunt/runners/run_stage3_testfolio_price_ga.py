"""Stage 3 GA for long-history testfolio price-only vote strategies.

This runner searches for candidates that beat the T3d-K2 and iter030-like
long-history anchors before any Tiingo confirmation. It intentionally uses only
close-derived signals from testfolio so the first optimization target includes
older regimes such as 1987, 2000-2002 and 2008. The GA is discovery only: every
evaluated individual must be included in later DSR trial accounting
`[advances_fin_ml, p.222-223]`, and promotion still requires OOS/WF/FWD,
bootstrap, PBO and DSR gates `[advances_fin_ml, p.196-202]`,
`[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import argparse
import csv
import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.core.data_loader import load_testfolio_series
from studies.technical_signal_vote_hunt.core import STAGE1_BRANCHES, daily_returns
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import (
    FIELDNAMES,
    _benchmark_rows,
    _metrics_row_np,
    _prepare_branch,
    _simulate_on_off_np,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
BASE_OUT_DIR = REPO_ROOT / "studies/technical_signal_vote_hunt/results/stage3_testfolio_price_ga"

EXTRA_FIELDS = [
    "fitness",
    "edge_sortino_vs_best_anchor",
    "edge_cagr_vs_best_anchor",
    "edge_calmar_vs_best_anchor",
    "pbo_proxy_score",
    "wf_positive_windows",
    "min_window_sharpe",
    "window_sharpe_std",
    "beats_t3d_k2",
    "beats_iter030_like",
]


@dataclass(frozen=True)
class Individual:
    mask: np.ndarray
    k: int


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Stage 3 testfolio price-only GA against T3d/iter030 anchors")
    p.add_argument("--branch", choices=["SPY", "QQQ"], default="QQQ")
    p.add_argument("--risk-on", choices=["SSO_2x", "UPRO_3x", "QLD_2x", "TQQQ_3x"], default="QLD_2x")
    p.add_argument("--off-leg", choices=["ZROZSIM", "CASHX"], default="ZROZSIM")
    p.add_argument("--population", type=int, default=256)
    p.add_argument("--generations", type=int, default=120)
    p.add_argument("--elite", type=int, default=24)
    p.add_argument("--mutation-rate", type=float, default=0.025)
    p.add_argument("--k-mutation-rate", type=float, default=0.12)
    p.add_argument("--min-n", type=int, default=8)
    p.add_argument("--max-n", type=int, default=14)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--signal-limit", type=int, default=None)
    p.add_argument("--top-final", type=int, default=200)
    p.add_argument("--cagr-weight", type=float, default=0.80)
    p.add_argument("--calmar-weight", type=float, default=0.35)
    p.add_argument("--mdd-penalty", type=float, default=0.25)
    p.add_argument("--complexity-penalty", type=float, default=0.015)
    p.add_argument("--complexity-free-n", type=int, default=8)
    p.add_argument("--pbo-proxy-weight", type=float, default=0.0)
    p.add_argument("--pbo-proxy-windows", type=int, default=8)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    _validate_args(args)
    rng = np.random.default_rng(args.seed)

    spec = _select_branch(args.branch, args.risk_on)
    off_returns = daily_returns(load_testfolio_series(args.off_leg))
    branch = _prepare_branch(spec, off_returns, args.signal_limit)
    anchors = _anchor_rows(branch)
    n_signals = len(branch.signal_names)
    max_n = min(args.max_n, n_signals)
    if args.min_n > max_n:
        raise SystemExit(f"min_n={args.min_n} exceeds available max_n={max_n}")

    out_dir = BASE_OUT_DIR / f"{args.branch}_{args.risk_on}_{args.off_leg}_seed{args.seed}"
    out_dir.mkdir(parents=True, exist_ok=True)
    best_path = out_dir / "best_by_generation.csv"
    pop_path = out_dir / "population_history.csv"
    final_path = out_dir / "final_candidates.csv"
    anchors_path = out_dir / "anchors.csv"

    pd.DataFrame(anchors).to_csv(anchors_path, index=False)
    population = [_random_individual(rng, n_signals, args.min_n, max_n) for _ in range(args.population)]
    seen: dict[str, dict] = {}
    started = time.perf_counter()

    fieldnames = [*EXTRA_FIELDS, *FIELDNAMES]
    with best_path.open("w", newline="", encoding="utf-8") as best_fh, pop_path.open("w", newline="", encoding="utf-8") as pop_fh:
        best_writer = csv.DictWriter(best_fh, fieldnames=["generation", *fieldnames])
        pop_writer = csv.DictWriter(pop_fh, fieldnames=["generation", "rank", *fieldnames])
        best_writer.writeheader()
        pop_writer.writeheader()

        for generation in range(args.generations):
            evaluated = [_evaluate(ind, branch, anchors, args) for ind in population]
            evaluated.sort(key=lambda item: item[0], reverse=True)

            for rank, (fitness, row, ind) in enumerate(evaluated, start=1):
                record = {"fitness": fitness, **row}
                key = f"{row['branch']}|{row['risk_on']}|{row['signals']}|k={row['k']}"
                prior = seen.get(key)
                if prior is None or fitness > float(prior["fitness"]):
                    seen[key] = record
                pop_writer.writerow({"generation": generation, "rank": rank, **record})
            pop_fh.flush()

            best_fitness, best_row, _ = evaluated[0]
            best_writer.writerow({"generation": generation, "fitness": best_fitness, **best_row})
            best_fh.flush()

            elapsed = time.perf_counter() - started
            print(
                f"gen={generation:03d}/{args.generations - 1:03d} "
                f"fit={best_fitness:.4f} sortino={best_row['sortino']:.4f} "
                f"cagr={best_row['cagr']:.2%} mdd={best_row['mdd']:.2%} "
                f"edgeS={best_row['edge_sortino_vs_best_anchor']:.4f} "
                f"n={best_row['n']} k={best_row['k']} elapsed={elapsed:.1f}s "
                f"signals={best_row['signals']}",
                flush=True,
            )

            elites = [item[2] for item in evaluated[: args.elite]]
            population = _next_generation(
                rng=rng,
                elites=elites,
                pop_size=args.population,
                n_signals=n_signals,
                min_n=args.min_n,
                max_n=max_n,
                mutation_rate=args.mutation_rate,
                k_mutation_rate=args.k_mutation_rate,
            )
            _write_final(seen, final_path, args.top_final)

    final_df = _write_final(seen, final_path, args.top_final)
    elapsed = time.perf_counter() - started
    _write_report(out_dir, final_df, pd.DataFrame(anchors), args, n_signals, max_n, len(seen), elapsed)
    _write_manifest(out_dir, args, n_signals, max_n, len(seen), elapsed)
    print(f"done unique_candidates={len(seen):,} final={final_path}", flush=True)
    return 0


def _validate_args(args: argparse.Namespace) -> None:
    if args.population < 4:
        raise SystemExit("population must be >= 4")
    if args.elite < 1 or args.elite >= args.population:
        raise SystemExit("elite must be >=1 and < population")
    if args.min_n < 1 or args.max_n < args.min_n:
        raise SystemExit("Require 1 <= min_n <= max_n")
    if args.branch == "SPY" and args.risk_on not in {"SSO_2x", "UPRO_3x"}:
        raise SystemExit("SPY branch supports SSO_2x or UPRO_3x")
    if args.branch == "QQQ" and args.risk_on not in {"QLD_2x", "TQQQ_3x"}:
        raise SystemExit("QQQ branch supports QLD_2x or TQQQ_3x")


def _select_branch(branch: str, risk_on: str):
    for spec in STAGE1_BRANCHES:
        if spec.branch == branch and spec.risk_on_label == risk_on:
            return spec
    raise SystemExit(f"No Stage 1 branch for {branch=} {risk_on=}")


def _anchor_rows(branch) -> list[dict]:
    rows = _benchmark_rows(branch)
    keep = []
    for row in rows:
        if str(row["label"]).endswith(("_t3d_k2", "_iter030_like")):
            keep.append(row)
    if len(keep) != 2:
        raise RuntimeError(f"expected 2 anchors, got {len(keep)}")
    return keep


def _random_individual(rng: np.random.Generator, n_signals: int, min_n: int, max_n: int) -> Individual:
    n = int(rng.integers(min_n, max_n + 1))
    idx = rng.choice(n_signals, size=n, replace=False)
    mask = np.zeros(n_signals, dtype=bool)
    mask[idx] = True
    return Individual(mask=mask, k=int(rng.integers(1, n + 1)))


def _evaluate(ind: Individual, branch, anchors: list[dict], args: argparse.Namespace) -> tuple[float, dict, Individual]:
    idx = np.flatnonzero(ind.mask)
    n = int(len(idx))
    k = int(np.clip(ind.k, 1, n))
    sub = branch.signal_matrix[:, idx]
    valid = ~np.isnan(sub).any(axis=1)
    counts = np.nansum(sub, axis=1)
    signal = np.where(valid, counts >= k, False)
    returns = _simulate_on_off_np(signal, branch.on_returns, branch.off_returns)
    row = _metrics_row_np(
        returns=returns,
        benchmark_returns=branch.benchmark_returns,
        dates=branch.dates,
        label="stage3_price_vote_ga",
        branch=branch.spec.branch,
        risk_on=branch.spec.risk_on_label,
        n=n,
        k=k,
        signals="|".join(branch.signal_names[i] for i in idx),
    )
    row.update(_anchor_edges(row, anchors))
    row.update(_pbo_proxy_edges(returns, args.pbo_proxy_windows))
    fitness = _fitness(row, args)
    if k != ind.k:
        ind = Individual(mask=ind.mask.copy(), k=k)
    return fitness, row, ind


def _anchor_edges(row: dict, anchors: list[dict]) -> dict:
    best_sortino = max(float(a["sortino"]) for a in anchors)
    best_cagr = max(float(a["cagr"]) for a in anchors)
    best_calmar = max(float(a["calmar"]) for a in anchors)
    t3d = next(a for a in anchors if str(a["label"]).endswith("_t3d_k2"))
    iter030 = next(a for a in anchors if str(a["label"]).endswith("_iter030_like"))
    return {
        "edge_sortino_vs_best_anchor": float(row["sortino"]) - best_sortino,
        "edge_cagr_vs_best_anchor": float(row["cagr"]) - best_cagr,
        "edge_calmar_vs_best_anchor": float(row["calmar"]) - best_calmar,
        "beats_t3d_k2": _beats_anchor(row, t3d),
        "beats_iter030_like": _beats_anchor(row, iter030),
    }


def _beats_anchor(row: dict, anchor: dict) -> bool:
    return (
        float(row["sortino"]) > float(anchor["sortino"])
        and float(row["cagr"]) > float(anchor["cagr"])
        and float(row["mdd"]) >= float(anchor["mdd"])
    )


def _pbo_proxy_edges(returns: np.ndarray, n_windows: int) -> dict:
    """Compute an individual stability proxy for PBO-aware discovery.

    True PBO is a panel/ranking statistic, not an individual strategy metric.
    This proxy rewards broad walk-forward Sharpe consistency and penalizes
    high window dispersion so the GA is less attracted to single-regime winners
    `[advances_fin_ml, p.208-211]`.
    """
    r = returns[np.isfinite(returns)]
    if len(r) < n_windows * 20:
        return {
            "pbo_proxy_score": 0.0,
            "wf_positive_windows": 0,
            "min_window_sharpe": 0.0,
            "window_sharpe_std": 0.0,
        }
    splits = np.array_split(r, n_windows)
    sharpes = np.array([_sharpe_np(s) for s in splits], dtype=float)
    positive = int(np.sum(sharpes > 0.0))
    min_sharpe = float(np.min(sharpes))
    std = float(np.std(sharpes, ddof=1)) if len(sharpes) > 1 else 0.0
    median = float(np.median(sharpes))
    score = median + 0.15 * min_sharpe + 0.10 * positive - 0.35 * std
    return {
        "pbo_proxy_score": score,
        "wf_positive_windows": positive,
        "min_window_sharpe": min_sharpe,
        "window_sharpe_std": std,
    }


def _sharpe_np(r: np.ndarray) -> float:
    if len(r) < 2:
        return 0.0
    std = float(np.std(r, ddof=1))
    return float(np.mean(r) / std * np.sqrt(252.0)) if std > 0 else 0.0


def _fitness(row: dict, args: argparse.Namespace) -> float:
    complexity = max(0, int(row["n"]) - args.complexity_free_n)
    mdd_abs = abs(float(row["mdd"]))
    anchor_bonus = 0.50 if row["beats_t3d_k2"] else 0.0
    anchor_bonus += 0.75 if row["beats_iter030_like"] else 0.0
    return (
        float(row["sortino"])
        + args.cagr_weight * float(row["cagr"])
        + args.calmar_weight * float(row["calmar"])
        + 0.75 * float(row["edge_sortino_vs_best_anchor"])
        + 0.25 * float(row["edge_cagr_vs_best_anchor"])
        + args.pbo_proxy_weight * float(row["pbo_proxy_score"])
        - args.mdd_penalty * mdd_abs
        - args.complexity_penalty * complexity
        + anchor_bonus
    )


def _next_generation(
    rng: np.random.Generator,
    elites: list[Individual],
    pop_size: int,
    n_signals: int,
    min_n: int,
    max_n: int,
    mutation_rate: float,
    k_mutation_rate: float,
) -> list[Individual]:
    out = [Individual(mask=e.mask.copy(), k=e.k) for e in elites]
    while len(out) < pop_size:
        p1 = elites[int(rng.integers(0, len(elites)))]
        p2 = elites[int(rng.integers(0, len(elites)))]
        child_mask = np.where(rng.random(n_signals) < 0.5, p1.mask, p2.mask).astype(bool)
        child_mask = np.logical_xor(child_mask, rng.random(n_signals) < mutation_rate)
        child_mask = _repair_mask(rng, child_mask, min_n, max_n)
        n = int(child_mask.sum())
        child_k = p1.k if rng.random() < 0.5 else p2.k
        if rng.random() < k_mutation_rate:
            child_k += int(rng.choice([-1, 1]))
        out.append(Individual(mask=child_mask, k=int(np.clip(child_k, 1, n))))
    return out


def _repair_mask(rng: np.random.Generator, mask: np.ndarray, min_n: int, max_n: int) -> np.ndarray:
    out = mask.copy()
    n = int(out.sum())
    if n < min_n:
        available = np.flatnonzero(~out)
        out[rng.choice(available, size=min_n - n, replace=False)] = True
    elif n > max_n:
        active = np.flatnonzero(out)
        out[rng.choice(active, size=n - max_n, replace=False)] = False
    return out


def _write_final(seen: dict[str, dict], path: Path, top_final: int) -> pd.DataFrame:
    rows = sorted(seen.values(), key=lambda row: float(row["fitness"]), reverse=True)[:top_final]
    df = pd.DataFrame(rows)
    if not df.empty:
        df.to_csv(path, index=False)
    return df


def _write_report(
    out_dir: Path,
    final_df: pd.DataFrame,
    anchors: pd.DataFrame,
    args: argparse.Namespace,
    n_signals: int,
    max_n: int,
    unique_candidates: int,
    elapsed: float,
) -> None:
    top_cols = [
        "fitness", "branch", "risk_on", "n", "k", "sortino", "cagr", "mdd", "calmar",
        "edge_sortino_vs_best_anchor", "edge_cagr_vs_best_anchor", "pbo_proxy_score",
        "wf_positive_windows", "min_window_sharpe", "window_sharpe_std",
        "beats_t3d_k2", "beats_iter030_like", "signals",
    ]
    lines = [
        "# Stage 3 Testfolio Price-Only GA",
        "",
        "Status: discovery search, not a validation verdict.",
        "",
        "## Purpose",
        "",
        "Search the long-history testfolio panel first, using only close-derived price signals, before treating Tiingo 2006/2010+ as modern confirmation.",
        "",
        "## Run",
        "",
        f"- Branch/risk-on: `{args.branch}` / `{args.risk_on}`",
        f"- Off leg: `{args.off_leg}`",
        f"- Signal subset range: `n={args.min_n}..{max_n}` from {n_signals} available signals",
        f"- Population/generations/elite: `{args.population}` / `{args.generations}` / `{args.elite}`",
        f"- PBO proxy weight/windows: `{args.pbo_proxy_weight}` / `{args.pbo_proxy_windows}`",
        f"- Unique candidates observed: {unique_candidates:,}",
        f"- Elapsed seconds: {elapsed:.1f}",
        "",
        "## Anchors",
        "",
        anchors[["label", "sortino", "cagr", "mdd", "calmar", "end_mult"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Top Candidates",
        "",
        _top_markdown(final_df, top_cols) if not final_df.empty else "No candidates written.",
        "",
        "## Method Notes",
        "",
        "- Uses the same close-only signal library as Stage 1: moving averages, MACD, ROC, RSI/StochRSI, realized-vol percentiles and AR(1).",
        "- Signals are lagged one trading day before returns are earned to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.",
        "- Fitness rewards Sortino/CAGR/Calmar and explicit edge versus the best T3d-K2/iter030-like anchor, while penalizing drawdown and excess complexity.",
        "- If `--pbo-proxy-weight > 0`, fitness also rewards an individual walk-forward stability proxy. This is not true PBO, because true PBO is a panel/ranking statistic, but it is a practical anti-single-regime discovery pressure `[advances_fin_ml, p.208-211]`.",
        "- This is candidate discovery only; any survivor must still clear WF/OOS/FWD/bootstrap/PBO/DSR with cumulative GA trial accounting `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.",
    ]
    (out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _top_markdown(final_df: pd.DataFrame, top_cols: list[str]) -> str:
    display = final_df.head(25)[top_cols].copy()
    display["signals"] = display["signals"].astype(str).str.replace("|", "<br>", regex=False)
    return display.to_markdown(index=False, floatfmt=".4f")


def _write_manifest(out_dir: Path, args: argparse.Namespace, n_signals: int, max_n: int, unique_candidates: int, elapsed: float) -> None:
    manifest = {
        "stage": "stage3_testfolio_price_ga",
        "branch": args.branch,
        "risk_on": args.risk_on,
        "off_leg": args.off_leg,
        "min_n": args.min_n,
        "max_n": max_n,
        "signal_limit": args.signal_limit,
        "n_signals": n_signals,
        "population": args.population,
        "generations": args.generations,
        "elite": args.elite,
        "seed": args.seed,
        "unique_candidates": unique_candidates,
        "minimum_trials_for_dsr": args.population * args.generations,
        "pbo_proxy_weight": args.pbo_proxy_weight,
        "pbo_proxy_windows": args.pbo_proxy_windows,
        "elapsed_seconds": elapsed,
        "primary_citation": "[advances_fin_ml, p.222-223]",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
