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
from joblib import Parallel, delayed

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from studies.static_spy_beater_portfolio.scripts.score_portfolio import (  # noqa: E402
    build_benchmark_cache,
    monthly_rebalanced_returns,
    precompute_growth_matrix,
    score_named_benchmarks,
    score_portfolio,
    score_to_dict,
)
from studies.static_spy_beater_portfolio.scripts.universe import (  # noqa: E402
    CORE_35_40_25_WEIGHTS,
    UNIVERSES,
    common_window,
    load_universe_returns,
)

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


def format_weights(weights: dict[str, float]) -> str:
    """Compact human log format: `10 SPYSIM 20 ZROZSIM`."""
    parts = []
    for ticker, weight in sorted(weights.items(), key=lambda item: (-item[1], item[0])):
        parts.append(f"{int(round(weight * 100))} {ticker}")
    return " ".join(parts)


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
    patience: int,
    min_delta: float,
    log_every: int,
    eval_log_every: int,
    fast_discovery: bool,
    jobs: int,
) -> dict:
    rng = random.Random(seed)
    tickers = UNIVERSES[universe]
    print(
        " ".join(
            [
                "loading_universe",
                f"universe={universe}",
                f"assets={len(tickers)}",
                f"fitness={fitness}",
                f"population={population_size}",
                f"generations={generations}",
                f"rolling_step={rolling_step}",
                f"finalist_exact={finalist_exact}",
                f"fast_discovery={fast_discovery}",
                f"jobs={jobs}",
            ]
        ),
        flush=True,
    )
    frame = load_universe_returns(universe)
    start, end, rows = common_window(frame, tickers)
    required_columns = list(dict.fromkeys(tickers + ["SPYSIM", "QQQSIM"]))
    frame = frame.loc[start:end, required_columns].dropna()
    print(
        f"loaded_universe common_start={start.date()} common_end={end.date()} rows={rows} columns={len(required_columns)}",
        flush=True,
    )
    drawdown_required = fitness in {
        "calmar_robust",
        "balanced_spy_beater",
        "balanced_dual_beater",
        "spy_beater_mdd_guard",
        "spy_beater_calmar_guard",
        "spy_beater_consistency_guard",
        "spy_beater_p10_mdd_guard",
        "core_relative_wealth_dominance",
    }
    discovery_drawdown = (not fast_discovery) or drawdown_required
    print(
        f"precomputing_growth_matrix rows={len(frame)} assets={len(tickers)}",
        flush=True,
    )
    growth_cache = precompute_growth_matrix(frame[tickers])
    core_returns = None
    if set(CORE_35_40_25_WEIGHTS).issubset(set(frame.columns)):
        core_returns = monthly_rebalanced_returns(frame, CORE_35_40_25_WEIGHTS, growth_cache=growth_cache)
    print(
        f"precomputing_benchmarks rolling_step={rolling_step} compute_drawdown={discovery_drawdown}",
        flush=True,
    )
    sampled_benchmark_cache = build_benchmark_cache(
        frame["SPYSIM"],
        frame["QQQSIM"],
        core_returns,
        rolling_step=rolling_step,
        compute_drawdown=discovery_drawdown,
    )
    exact_benchmark_cache = None
    population = [random_chromosome(len(tickers), max_assets, rng) for _ in range(population_size)]
    cache: dict[tuple[int, ...], dict] = {}
    history = []
    best_seen = -np.inf
    last_improvement_generation = 0
    stopped_early = False
    stop_reason = "completed_generations"

    def score_chromosome(chrom: tuple[int, ...]) -> tuple[tuple[int, ...], dict]:
        weights = chrom_to_weights(chrom, tickers)
        score = score_portfolio(
            frame,
            weights,
            rolling_step=rolling_step,
            benchmark_cache=sampled_benchmark_cache,
            compute_drawdown=discovery_drawdown,
            growth_cache=growth_cache,
        )
        payload = score_to_dict(score)
        payload["chromosome"] = list(chrom)
        payload["fitness_name"] = fitness
        payload["fitness_value"] = float(payload["fitness"].get(fitness, np.nan))
        return chrom, payload

    def evaluate_population(chromosomes: list[tuple[int, ...]]) -> list[dict]:
        missing = list(dict.fromkeys(chrom for chrom in chromosomes if chrom not in cache))
        if missing:
            if jobs == 1:
                scored = [score_chromosome(chrom) for chrom in missing]
            else:
                scored = Parallel(n_jobs=jobs, prefer="threads")(
                    delayed(score_chromosome)(chrom) for chrom in missing
                )
            for chrom, payload in scored:
                cache[chrom] = payload
                if eval_log_every > 0 and len(cache) % eval_log_every == 0:
                    print(
                        f"evaluated_unique={len(cache)} latest_fitness={payload['fitness_value']:.8f}",
                        flush=True,
                    )
        return [cache[chrom] for chrom in chromosomes]

    for generation in range(generations + 1):
        evaluated = evaluate_population(population)
        evaluated.sort(key=lambda x: x["fitness_value"], reverse=True)
        best = evaluated[0]
        best_fitness = best["fitness_value"]
        if np.isfinite(best_fitness) and best_fitness > best_seen + min_delta:
            best_seen = best_fitness
            last_improvement_generation = generation
        fitness_values = np.array(
            [row["fitness_value"] for row in evaluated if np.isfinite(row["fitness_value"])],
            dtype=float,
        )
        distinct_chromosomes = len({tuple(row["chromosome"]) for row in evaluated})
        history.append(
            {
                "generation": generation,
                "best_fitness": best_fitness,
                "best_weights": best["weights"],
                "unique_evaluated": len(cache),
                "best_seen": best_seen,
                "generations_since_improvement": generation - last_improvement_generation,
                "mean_fitness": float(fitness_values.mean()) if fitness_values.size else float("nan"),
                "median_fitness": float(np.median(fitness_values)) if fitness_values.size else float("nan"),
                "std_fitness": float(fitness_values.std(ddof=0)) if fitness_values.size else float("nan"),
                "distinct_chromosomes": distinct_chromosomes,
                "population_unique_share": distinct_chromosomes / len(evaluated) if evaluated else float("nan"),
            }
        )
        if log_every > 0 and (generation == 0 or generation % log_every == 0):
            print(
                " ".join(
                    [
                        f"gen={generation}/{generations}",
                        f"best={best_fitness:.8f}",
                        f"best_seen={best_seen:.8f}",
                        f"since_improve={generation - last_improvement_generation}",
                        f"unique={len(cache)}",
                        f"portfolio=\"{format_weights(best['weights'])}\"",
                    ]
                ),
                flush=True,
            )
        if generation == generations:
            break
        if patience > 0 and generation - last_improvement_generation >= patience:
            stopped_early = True
            stop_reason = f"no_improvement_for_{patience}_generations"
            print(
                f"early_stop generation={generation} reason={stop_reason} best_seen={best_seen:.8f}",
                flush=True,
            )
            break
        elites = [tuple(row["chromosome"]) for row in evaluated[:elite_size]]
        next_population = list(elites)
        # Parent pool scales with population to avoid premature convergence when
        # the GA runs with larger pops `[advances_fin_ml, p.222-223]`.
        parent_pool_size = max(elite_size * 3, population_size // 2, 2)
        parent_pool = [tuple(row["chromosome"]) for row in evaluated[:parent_pool_size]]
        while len(next_population) < population_size:
            child = crossover(rng.choice(parent_pool), rng.choice(parent_pool), max_assets, rng)
            child = mutate(child, max_assets, rng, mutation_rate)
            next_population.append(child)
        population = next_population

    all_rows = list(cache.values())
    all_rows.sort(key=lambda x: x["fitness_value"], reverse=True)

    exact_rows = []
    if finalist_exact > 0:
        print(f"exact_rerank finalists={min(finalist_exact, len(all_rows))} rolling_step=1", flush=True)
        print("precomputing_benchmarks rolling_step=1 compute_drawdown=True", flush=True)
        exact_benchmark_cache = build_benchmark_cache(
            frame["SPYSIM"], frame["QQQSIM"], core_returns, rolling_step=1, compute_drawdown=True
        )
        for sampled in all_rows[:finalist_exact]:
            weights = sampled["weights"]
            exact_score = score_portfolio(
                frame,
                weights,
                rolling_step=1,
                benchmark_cache=exact_benchmark_cache,
                compute_drawdown=True,
                growth_cache=growth_cache,
            )
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
        for name, score in score_named_benchmarks(
            universe,
            frame,
            rolling_step=benchmark_step,
            benchmark_cache=exact_benchmark_cache if benchmark_step == 1 else sampled_benchmark_cache,
            compute_drawdown=benchmark_step == 1 or discovery_drawdown,
            growth_cache=growth_cache,
        ).items()
    }
    return {
        "discovery_only": True,
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
        "patience": patience,
        "min_delta": min_delta,
        "log_every": log_every,
        "eval_log_every": eval_log_every,
        "fast_discovery": fast_discovery,
        "jobs": jobs,
        "stopped_early": stopped_early,
        "stop_reason": stop_reason,
        "generations_completed": history[-1]["generation"] if history else 0,
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
    parser.add_argument(
        "--patience",
        type=int,
        default=0,
        help=(
            "Stop early after this many generations without best-fitness improvement. "
            "0 (default) auto-selects min(25, max(5, generations // 2)); use -1 to disable."
        ),
    )
    parser.add_argument(
        "--min-delta",
        type=float,
        default=1e-9,
        help="Minimum best-fitness improvement required to reset patience.",
    )
    parser.add_argument(
        "--log-every",
        type=int,
        default=5,
        help="Print GA progress every N generations. Use 0 to disable progress logs.",
    )
    parser.add_argument(
        "--eval-log-every",
        type=int,
        default=50,
        help="Print progress after every N newly evaluated unique portfolios. Use 0 to disable.",
    )
    parser.add_argument(
        "--fast-discovery",
        action="store_true",
        help="Skip rolling MDD/Calmar during GA discovery unless the selected fitness needs drawdown.",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="Threaded parallel candidate scoring jobs. Use 1 for deterministic single-thread execution.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("studies/static_spy_beater_portfolio/results/ga"))
    args = parser.parse_args()

    if args.patience == 0:
        patience = min(25, max(5, args.generations // 2))
    elif args.patience < 0:
        patience = 0
    else:
        patience = args.patience

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
        patience=patience,
        min_delta=args.min_delta,
        log_every=args.log_every,
        eval_log_every=args.eval_log_every,
        fast_discovery=args.fast_discovery,
        jobs=args.jobs,
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
