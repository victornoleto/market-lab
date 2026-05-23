"""Genetic search for Stage 1 close-only technical signal votes.

This runner searches the 33-signal combinatorial space without attempting an
impossible exhaustive all-subset grid. It is a search tool, not a validation
gate: every evaluated chromosome counts toward later multiple-testing penalties
`[advances_fin_ml, p.222-223]`, and final candidates still require PBO, DSR,
walk-forward, OOS, FWD and bootstrap validation `[advances_fin_ml, p.208-211]`.

Progress is printed every generation and CSV files are rewritten/appended during
the run so the process can be monitored from the terminal.
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

from market_lab.backtest.data.testfolio_loader import load_testfolio_series
from studies.technical_signal_vote_hunt.core import STAGE1_BRANCHES, daily_returns
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import (
    FIELDNAMES,
    _metrics_row_np,
    _prepare_branch,
    _simulate_on_off_np,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
BASE_OUT_DIR = REPO_ROOT / "studies/technical_signal_vote_hunt/results/stage1_ga"


@dataclass(frozen=True)
class Individual:
    mask: np.ndarray
    k: int


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Stage 1 GA search over close-only vote signals")
    p.add_argument("--branch", choices=["SPY", "QQQ"], required=True)
    p.add_argument("--risk-on", choices=["SSO_2x", "UPRO_3x", "QLD_2x", "TQQQ_3x"], required=True)
    p.add_argument("--off-leg", choices=["ZROZSIM", "CASHX"], default="ZROZSIM")
    p.add_argument("--population", type=int, default=256)
    p.add_argument("--generations", type=int, default=100)
    p.add_argument("--elite", type=int, default=20)
    p.add_argument("--mutation-rate", type=float, default=0.03)
    p.add_argument("--k-mutation-rate", type=float, default=0.10)
    p.add_argument("--min-n", type=int, default=2)
    p.add_argument("--max-n", type=int, default=12)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--signal-limit", type=int, default=None)
    p.add_argument("--cagr-weight", type=float, default=0.50)
    p.add_argument("--calmar-weight", type=float, default=0.20)
    p.add_argument("--mdd-penalty", type=float, default=0.15)
    p.add_argument("--complexity-penalty", type=float, default=0.01)
    p.add_argument("--complexity-free-n", type=int, default=6)
    p.add_argument("--top-final", type=int, default=200)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    _validate_args(args)
    rng = np.random.default_rng(args.seed)

    spec = _select_branch(args.branch, args.risk_on)
    off_returns = daily_returns(load_testfolio_series(args.off_leg))
    branch = _prepare_branch(spec, off_returns, args.signal_limit)
    n_signals = len(branch.signal_names)
    max_n = min(args.max_n, n_signals)
    if args.min_n > max_n:
        raise SystemExit(f"min_n={args.min_n} exceeds available max_n={max_n}")

    out_dir = BASE_OUT_DIR / f"{args.branch}_{args.risk_on}_seed{args.seed}"
    out_dir.mkdir(parents=True, exist_ok=True)
    best_path = out_dir / "best_by_generation.csv"
    pop_path = out_dir / "population_history.csv"
    final_path = out_dir / "final_candidates.csv"

    population = [_random_individual(rng, n_signals, args.min_n, max_n) for _ in range(args.population)]
    seen: dict[str, dict] = {}
    started = time.perf_counter()

    with best_path.open("w", newline="", encoding="utf-8") as best_fh, pop_path.open("w", newline="", encoding="utf-8") as pop_fh:
        best_writer = csv.DictWriter(best_fh, fieldnames=["generation", "fitness", *FIELDNAMES])
        pop_writer = csv.DictWriter(pop_fh, fieldnames=["generation", "rank", "fitness", *FIELDNAMES])
        best_writer.writeheader()
        pop_writer.writeheader()

        for generation in range(args.generations):
            evaluated = [_evaluate(ind, branch, args) for ind in population]
            evaluated.sort(key=lambda item: item[0], reverse=True)

            for rank, (fitness, row, ind) in enumerate(evaluated, start=1):
                key = f"{row['branch']}|{row['risk_on']}|{row['signals']}|k={row['k']}"
                prior = seen.get(key)
                if prior is None or fitness > prior["fitness"]:
                    seen[key] = {"fitness": fitness, **row}
                pop_writer.writerow({"generation": generation, "rank": rank, "fitness": fitness, **row})
            pop_fh.flush()

            best_fitness, best_row, _ = evaluated[0]
            best_writer.writerow({"generation": generation, "fitness": best_fitness, **best_row})
            best_fh.flush()

            elapsed = time.perf_counter() - started
            print(
                f"gen={generation:03d}/{args.generations - 1:03d} "
                f"best_fit={best_fitness:.4f} sortino={best_row['sortino']:.4f} "
                f"cagr={best_row['cagr']:.2%} mdd={best_row['mdd']:.2%} "
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

            _write_intermediate_final(seen, final_path, args.top_final)

    final_df = _write_intermediate_final(seen, final_path, args.top_final)
    _write_report(out_dir, final_df, args, n_signals=n_signals, max_n=max_n, elapsed=time.perf_counter() - started)
    _write_manifest(out_dir, args, n_signals=n_signals, max_n=max_n, unique_candidates=len(seen))
    print(f"done unique_candidates={len(seen):,} final={final_path}", flush=True)
    return 0


def _validate_args(args: argparse.Namespace) -> None:
    if args.population < 4:
        raise SystemExit("population must be >= 4")
    if args.elite < 1 or args.elite >= args.population:
        raise SystemExit("elite must be >=1 and < population")
    if not 0.0 <= args.mutation_rate <= 1.0:
        raise SystemExit("mutation-rate must be in [0,1]")
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


def _random_individual(rng: np.random.Generator, n_signals: int, min_n: int, max_n: int) -> Individual:
    n = int(rng.integers(min_n, max_n + 1))
    idx = rng.choice(n_signals, size=n, replace=False)
    mask = np.zeros(n_signals, dtype=bool)
    mask[idx] = True
    return Individual(mask=mask, k=int(rng.integers(1, n + 1)))


def _evaluate(ind: Individual, branch, args: argparse.Namespace) -> tuple[float, dict, Individual]:
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
        label="ga_vote_k",
        branch=branch.spec.branch,
        risk_on=branch.spec.risk_on_label,
        n=n,
        k=k,
        signals="|".join(branch.signal_names[i] for i in idx),
    )
    fitness = _fitness(row, args)
    if k != ind.k:
        ind = Individual(mask=ind.mask.copy(), k=k)
    return fitness, row, ind


def _fitness(row: dict, args: argparse.Namespace) -> float:
    complexity = max(0, int(row["n"]) - args.complexity_free_n)
    mdd_abs = abs(float(row["mdd"]))
    return (
        float(row["sortino"])
        + args.cagr_weight * float(row["cagr"])
        + args.calmar_weight * float(row["calmar"])
        - args.mdd_penalty * mdd_abs
        - args.complexity_penalty * complexity
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
        p1 = _tournament(rng, elites)
        p2 = _tournament(rng, elites)
        child_mask = np.where(rng.random(n_signals) < 0.5, p1.mask, p2.mask).astype(bool)
        mutation = rng.random(n_signals) < mutation_rate
        child_mask = np.logical_xor(child_mask, mutation)
        child_mask = _repair_mask(rng, child_mask, min_n, max_n)
        n = int(child_mask.sum())
        child_k = p1.k if rng.random() < 0.5 else p2.k
        if rng.random() < k_mutation_rate:
            child_k += int(rng.choice([-1, 1]))
        child_k = int(np.clip(child_k, 1, n))
        out.append(Individual(mask=child_mask, k=child_k))
    return out


def _tournament(rng: np.random.Generator, elites: list[Individual], size: int = 3) -> Individual:
    picks = rng.choice(len(elites), size=min(size, len(elites)), replace=False)
    return elites[int(picks[0])]


def _repair_mask(
    rng: np.random.Generator,
    mask: np.ndarray,
    min_n: int,
    max_n: int,
) -> np.ndarray:
    out = mask.copy()
    n = int(out.sum())
    if n < min_n:
        missing = min_n - n
        available = np.flatnonzero(~out)
        out[rng.choice(available, size=missing, replace=False)] = True
    elif n > max_n:
        remove = n - max_n
        active = np.flatnonzero(out)
        out[rng.choice(active, size=remove, replace=False)] = False
    return out


def _write_intermediate_final(seen: dict[str, dict], path: Path, top_n: int) -> pd.DataFrame:
    df = pd.DataFrame(seen.values()).sort_values("fitness", ascending=False).head(top_n)
    df.to_csv(path, index=False)
    return df


def _write_report(
    out_dir: Path,
    final_df: pd.DataFrame,
    args: argparse.Namespace,
    n_signals: int,
    max_n: int,
    elapsed: float,
) -> None:
    lines = [
        "# Stage 1 GA Results",
        "",
        "Status: genetic-search output. This is not a deploy verdict.",
        "",
        f"Branch: `{args.branch}`",
        f"Risk-on: `{args.risk_on}`",
        f"Off leg: `{args.off_leg}`",
        f"Signals available: {n_signals}",
        f"n range: {args.min_n}..{max_n}",
        f"Population/generations: {args.population}/{args.generations}",
        f"Evaluations: {args.population * args.generations:,}",
        f"Elapsed seconds: {elapsed:.1f}",
        "",
        "## Top Final Candidates",
        "",
        final_df.head(50)[["fitness", "branch", "risk_on", "n", "k", "sortino", "cagr", "sharpe", "mdd", "calmar", "signals"]].to_markdown(index=False, floatfmt=".4f") if not final_df.empty else "No candidates.",
        "",
        "## Method Notes",
        "",
        "- GA chromosome = signal inclusion mask + `k` vote threshold.",
        "- Fitness = Sortino + weighted CAGR/Calmar - MDD/complexity penalties.",
        "- Signals are lagged one day in the shared simulator to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.",
        "- Final candidates still require PBO/DSR/WF/OOS/FWD/bootstrap validation `[advances_fin_ml, p.208-211]`.",
    ]
    (out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(
    out_dir: Path,
    args: argparse.Namespace,
    n_signals: int,
    max_n: int,
    unique_candidates: int,
) -> None:
    manifest = {
        "stage": "stage1_ga",
        "branch": args.branch,
        "risk_on": args.risk_on,
        "off_leg": args.off_leg,
        "n_signals": n_signals,
        "min_n": args.min_n,
        "max_n": max_n,
        "population": args.population,
        "generations": args.generations,
        "elite": args.elite,
        "mutation_rate": args.mutation_rate,
        "k_mutation_rate": args.k_mutation_rate,
        "seed": args.seed,
        "evaluations": args.population * args.generations,
        "unique_candidates": unique_candidates,
        "fitness": {
            "cagr_weight": args.cagr_weight,
            "calmar_weight": args.calmar_weight,
            "mdd_penalty": args.mdd_penalty,
            "complexity_penalty": args.complexity_penalty,
            "complexity_free_n": args.complexity_free_n,
        },
        "primary_citation": "[advances_fin_ml, p.208-211]",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
