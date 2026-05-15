"""Genetic search over discrete static ETF portfolios.

The GA is discovery tooling, not validation. Every unique evaluated chromosome is
reported so downstream DSR/PBO validation can account for search breadth
`[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from studies.static_spy_beater_portfolio.scripts.score_portfolio import (
    score_named_benchmarks,
    score_portfolio,
    score_to_dict,
)
from studies.static_spy_beater_portfolio.scripts.universe import UNIVERSES, common_window, load_universe_returns

WEIGHT_UNITS = 20


def random_chromosome(n_assets: int, max_assets: int, rng: random.Random) -> tuple[int, ...]:
    k = rng.randint(1, min(max_assets, n_assets, WEIGHT_UNITS))
    idxs = rng.sample(range(n_assets), k)
    cuts = sorted(rng.sample(range(1, WEIGHT_UNITS), k - 1)) if k > 1 else []
    parts = [b - a for a, b in zip([0] + cuts, cuts + [WEIGHT_UNITS], strict=True)]
    units = [0] * n_assets
    rng.shuffle(parts)
    for idx, units_value in zip(idxs, parts, strict=True):
        units[idx] = units_value
    return tuple(units)


def repair_units(raw: list[int], max_assets: int, rng: random.Random) -> tuple[int, ...]:
    raw = [max(0, int(x)) for x in raw]
    active = [i for i, value in enumerate(raw) if value > 0]
    if not active:
        return random_chromosome(len(raw), max_assets, rng)
    if len(active) > max_assets:
        keep = set(sorted(active, key=lambda i: raw[i], reverse=True)[:max_assets])
        raw = [value if i in keep else 0 for i, value in enumerate(raw)]
    total = sum(raw)
    if total <= 0:
        return random_chromosome(len(raw), max_assets, rng)
    scaled = [int(round(value * WEIGHT_UNITS / total)) for value in raw]
    active = [i for i, value in enumerate(scaled) if value > 0]
    if not active:
        return random_chromosome(len(raw), max_assets, rng)
    while sum(scaled) > WEIGHT_UNITS:
        i = max((i for i in range(len(scaled)) if scaled[i] > 0), key=lambda j: scaled[j])
        scaled[i] -= 1
    while sum(scaled) < WEIGHT_UNITS:
        i = rng.choice(active)
        scaled[i] += 1
    return tuple(scaled)


def crossover(a: tuple[int, ...], b: tuple[int, ...], max_assets: int, rng: random.Random) -> tuple[int, ...]:
    raw = [rng.choice((x, y, int(round((x + y) / 2)))) for x, y in zip(a, b, strict=True)]
    return repair_units(raw, max_assets, rng)


def mutate(chrom: tuple[int, ...], max_assets: int, rng: random.Random, rate: float) -> tuple[int, ...]:
    raw = list(chrom)
    for i in range(len(raw)):
        if rng.random() < rate:
            raw[i] = max(0, raw[i] + rng.choice([-2, -1, 1, 2]))
    if rng.random() < rate:
        donors = [i for i, value in enumerate(raw) if value > 1]
        receivers = list(range(len(raw)))
        if donors and receivers:
            donor = rng.choice(donors)
            receiver = rng.choice(receivers)
            raw[donor] -= 1
            raw[receiver] += 1
    return repair_units(raw, max_assets, rng)


def chrom_to_weights(chrom: tuple[int, ...], tickers: list[str]) -> dict[str, float]:
    return {ticker: units / WEIGHT_UNITS for ticker, units in zip(tickers, chrom, strict=True) if units > 0}


def run_ga(
    universe: str,
    fitness: str,
    *,
    population_size: int,
    generations: int,
    elite_size: int,
    mutation_rate: float,
    max_assets: int,
    seed: int,
    rolling_step: int,
    finalist_exact: int,
) -> dict:
    rng = random.Random(seed)
    tickers = UNIVERSES[universe]
    frame = load_universe_returns(universe)
    start, end, rows = common_window(frame, tickers)
    required_columns = list(dict.fromkeys(tickers + ["SPYSIM", "QQQSIM"]))
    frame = frame.loc[start:end, required_columns].dropna()
    population = [random_chromosome(len(tickers), max_assets, rng) for _ in range(population_size)]
    cache: dict[tuple[int, ...], dict] = {}
    history = []

    def evaluate(chrom: tuple[int, ...]) -> dict:
        if chrom not in cache:
            weights = chrom_to_weights(chrom, tickers)
            score = score_portfolio(frame, weights, rolling_step=rolling_step)
            payload = score_to_dict(score)
            payload["chromosome"] = list(chrom)
            payload["fitness_name"] = fitness
            payload["fitness_value"] = float(payload["fitness"].get(fitness, np.nan))
            cache[chrom] = payload
        return cache[chrom]

    for generation in range(generations + 1):
        evaluated = [evaluate(chrom) for chrom in population]
        evaluated.sort(key=lambda x: x["fitness_value"], reverse=True)
        best = evaluated[0]
        history.append(
            {
                "generation": generation,
                "best_fitness": best["fitness_value"],
                "best_weights": best["weights"],
                "unique_evaluated": len(cache),
            }
        )
        if generation == generations:
            break
        elites = [tuple(row["chromosome"]) for row in evaluated[:elite_size]]
        next_population = list(elites)
        parent_pool = [tuple(row["chromosome"]) for row in evaluated[: max(elite_size * 3, 2)]]
        while len(next_population) < population_size:
            child = crossover(rng.choice(parent_pool), rng.choice(parent_pool), max_assets, rng)
            child = mutate(child, max_assets, rng, mutation_rate)
            next_population.append(child)
        population = next_population

    all_rows = list(cache.values())
    all_rows.sort(key=lambda x: x["fitness_value"], reverse=True)

    exact_rows = []
    if finalist_exact > 0:
        for sampled in all_rows[:finalist_exact]:
            weights = sampled["weights"]
            exact_score = score_portfolio(frame, weights, rolling_step=1)
            exact_payload = score_to_dict(exact_score)
            exact_payload["chromosome"] = sampled["chromosome"]
            exact_payload["fitness_name"] = fitness
            exact_payload["fitness_value"] = float(exact_payload["fitness"].get(fitness, np.nan))
            exact_payload["sampled_fitness_value"] = sampled["fitness_value"]
            exact_rows.append(exact_payload)
        exact_rows.sort(key=lambda x: x["fitness_value"], reverse=True)

    benchmark_step = 1 if finalist_exact > 0 else rolling_step
    benchmark_scores = {
        name: score_to_dict(score)
        for name, score in score_named_benchmarks(universe, frame, rolling_step=benchmark_step).items()
    }
    return {
        "universe": universe,
        "fitness": fitness,
        "seed": seed,
        "population_size": population_size,
        "generations": generations,
        "elite_size": elite_size,
        "mutation_rate": mutation_rate,
        "max_assets": max_assets,
        "rolling_step": rolling_step,
        "finalist_exact": finalist_exact,
        "benchmark_rolling_step": benchmark_step,
        "common_start": str(start.date()),
        "common_end": str(end.date()),
        "common_rows": rows,
        "unique_evaluated": len(cache),
        "history": history,
        "top": (exact_rows if exact_rows else all_rows)[:50],
        "top_sampled": all_rows[:50],
        "top_exact": exact_rows[:50],
        "benchmarks": benchmark_scores,
    }


def flatten_top(payload: dict) -> pd.DataFrame:
    rows = []
    for rank, row in enumerate(payload["top"], start=1):
        flat = {
            "rank": rank,
            "fitness_name": row["fitness_name"],
            "fitness_value": row["fitness_value"],
            "weights": json.dumps(row["weights"], sort_keys=True),
        }
        flat.update({f"full_{k}": v for k, v in row["full_metrics"].items()})
        flat.update({f"fit_{k}": v for k, v in row["fitness"].items()})
        flat.update({f"exposure_{k}": v for k, v in row["exposure"].items()})
        rows.append(flat)
    return pd.DataFrame(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", choices=sorted(UNIVERSES), required=True)
    parser.add_argument("--fitness", default="balanced_spy_beater")
    parser.add_argument("--population", type=int, default=40)
    parser.add_argument("--generations", type=int, default=10)
    parser.add_argument("--elite-size", type=int, default=6)
    parser.add_argument("--mutation-rate", type=float, default=0.12)
    parser.add_argument("--max-assets", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--rolling-step",
        type=int,
        default=21,
        help="Rolling-window stride used during GA discovery. Use 21 for monthly sampling; exact finalists use stride 1.",
    )
    parser.add_argument(
        "--finalist-exact",
        type=int,
        default=10,
        help="Re-score top N sampled portfolios with all possible rolling windows (rolling_step=1).",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("studies/static_spy_beater_portfolio/results/ga"))
    args = parser.parse_args()

    payload = run_ga(
        args.universe,
        args.fitness,
        population_size=args.population,
        generations=args.generations,
        elite_size=args.elite_size,
        mutation_rate=args.mutation_rate,
        max_assets=args.max_assets,
        seed=args.seed,
        rolling_step=args.rolling_step,
        finalist_exact=args.finalist_exact,
    )
    run_dir = args.output_dir / f"{args.universe}_{args.fitness}_seed{args.seed}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "results.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    flatten_top(payload).to_csv(run_dir / "top.csv", index=False)
    if payload.get("top_sampled"):
        sampled_payload = dict(payload)
        sampled_payload["top"] = payload["top_sampled"]
        flatten_top(sampled_payload).to_csv(run_dir / "top_sampled.csv", index=False)
    if payload.get("top_exact"):
        exact_payload = dict(payload)
        exact_payload["top"] = payload["top_exact"]
        flatten_top(exact_payload).to_csv(run_dir / "top_exact.csv", index=False)
    pd.DataFrame(payload["history"]).to_csv(run_dir / "history.csv", index=False)
    print(f"wrote {run_dir}")
    print(flatten_top(payload).head(10).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
