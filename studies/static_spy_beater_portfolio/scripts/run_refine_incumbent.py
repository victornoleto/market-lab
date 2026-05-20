"""Refine GA incumbents with exact small grids and local one/two-edit search.

This script is deliberately narrower than `run_ga.py`: after the broad GA finds a
stable family, refinement tests whether nearby 5% allocations improve the exact
rolling fitness. The refinement is still discovery-only and must not be treated as
validation `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from studies.static_spy_beater_portfolio.scripts.run_ga import format_weights
from studies.static_spy_beater_portfolio.scripts.score_portfolio import (
    build_benchmark_cache,
    score_named_benchmarks,
    score_portfolio,
    score_to_dict,
)
from studies.static_spy_beater_portfolio.scripts.universe import UNIVERSES, common_window, load_universe_returns

WEIGHT_UNITS = 20

DEFAULT_INCUMBENTS = {
    "core_1986": {"TQQQSIM": 0.40, "TMFSIM": 0.60},
    "mf_1988": {"TQQQSIM": 0.35, "TMFSIM": 0.50, "RSSTSIM": 0.15},
}

FOCUSED_POOLS = {
    "core_1986": ["TQQQSIM", "QLDSIM", "QQQSIM", "TMFSIM", "TLTSIM", "ZROZSIM", "GDESIM", "GLDSIM"],
    "mf_1988": ["TQQQSIM", "QLDSIM", "QQQSIM", "TMFSIM", "TLTSIM", "ZROZSIM", "RSSTSIM", "KMLMSIM", "GDESIM", "GLDSIM"],
    "lead_family_focused": ["GDESIM", "RSSTSIM", "ZROZSIM", "SPYSIM", "QQQSIM", "QLDSIM", "TQQQSIM", "GLDSIM", "UGLSIM", "TLTSIM", "CASHX"],
    "lead_family_no_3x_booster": ["GDESIM", "RSSTSIM", "ZROZSIM", "SPYSIM", "QQQSIM", "QLDSIM", "GLDSIM", "UGLSIM", "TLTSIM", "CASHX"],
}

FITNESSES_REQUIRING_DRAWDOWN = {
    "calmar_robust",
    "balanced_spy_beater",
    "balanced_dual_beater",
    "spy_beater_mdd_guard",
    "spy_beater_calmar_guard",
    "spy_beater_consistency_guard",
    "spy_beater_p10_mdd_guard",
}


def parse_weights(text: str | None, universe: str) -> dict[str, float]:
    if not text:
        if universe not in DEFAULT_INCUMBENTS:
            raise ValueError(f"no default incumbent for {universe}; pass --incumbent JSON")
        return dict(DEFAULT_INCUMBENTS[universe])
    weights = json.loads(text)
    total = sum(float(v) for v in weights.values())
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"incumbent weights sum to {total}, expected 1.0")
    return {str(k): float(v) for k, v in weights.items() if float(v) > 0.0}


def units_from_weights(weights: dict[str, float], tickers: list[str]) -> tuple[int, ...]:
    units = [0] * len(tickers)
    for ticker, weight in weights.items():
        if ticker not in tickers:
            raise ValueError(f"ticker {ticker} not in candidate tickers")
        unit = int(round(weight * WEIGHT_UNITS))
        if abs(unit / WEIGHT_UNITS - weight) > 1e-9:
            raise ValueError(f"weight {ticker}={weight} is not a 5% increment")
        units[tickers.index(ticker)] = unit
    if sum(units) != WEIGHT_UNITS:
        raise ValueError(f"incumbent units sum to {sum(units)}, expected {WEIGHT_UNITS}")
    return tuple(units)


def weights_from_units(units: tuple[int, ...], tickers: list[str]) -> dict[str, float]:
    return {ticker: unit / WEIGHT_UNITS for ticker, unit in zip(tickers, units, strict=True) if unit > 0}


def simplex_candidates(tickers: list[str], max_active: int) -> set[tuple[int, ...]]:
    """All 5%-grid portfolios using up to `max_active` names from `tickers`."""
    candidates: set[tuple[int, ...]] = set()
    n = len(tickers)
    for k in range(1, min(max_active, n, WEIGHT_UNITS) + 1):
        for active in itertools.combinations(range(n), k):
            for parts in positive_integer_compositions(WEIGHT_UNITS, k):
                units = [0] * n
                for idx, unit in zip(active, parts, strict=True):
                    units[idx] = unit
                candidates.add(tuple(units))
    return candidates


def positive_integer_compositions(total: int, parts: int):
    """Yield ordered positive integer compositions of total into parts."""
    if parts == 1:
        yield (total,)
        return
    for first in range(1, total - parts + 2):
        for rest in positive_integer_compositions(total - first, parts - 1):
            yield (first, *rest)


def local_edit_candidates(
    incumbent: tuple[int, ...],
    *,
    depth: int,
    max_active: int,
) -> set[tuple[int, ...]]:
    """Generate portfolios reachable by moving 5% units up to `depth` times."""
    seen = {incumbent}
    frontier = {incumbent}
    n = len(incumbent)
    for _ in range(depth):
        next_frontier = set()
        for units in frontier:
            donors = [i for i, unit in enumerate(units) if unit > 0]
            receivers = list(range(n))
            for donor in donors:
                for receiver in receivers:
                    if donor == receiver:
                        continue
                    new_units = list(units)
                    new_units[donor] -= 1
                    new_units[receiver] += 1
                    if sum(1 for unit in new_units if unit > 0) > max_active:
                        continue
                    candidate = tuple(new_units)
                    if candidate not in seen:
                        seen.add(candidate)
                        next_frontier.add(candidate)
        frontier = next_frontier
    return seen


def score_candidates(
    frame: pd.DataFrame,
    tickers: list[str],
    candidates: set[tuple[int, ...]],
    *,
    universe: str,
    fitness: str,
    discovery_rolling_step: int,
    exact_top: int,
) -> dict:
    compute_drawdown = fitness in FITNESSES_REQUIRING_DRAWDOWN
    discovery_cache = build_benchmark_cache(
        frame["SPYSIM"], frame["QQQSIM"], rolling_step=discovery_rolling_step, compute_drawdown=compute_drawdown
    )
    rows = []
    for i, units in enumerate(sorted(candidates), start=1):
        weights = weights_from_units(units, tickers)
        score = score_portfolio(
            frame,
            weights,
            rolling_step=discovery_rolling_step,
            benchmark_cache=discovery_cache,
            compute_drawdown=compute_drawdown,
        )
        payload = score_to_dict(score)
        payload["chromosome"] = list(units)
        payload["fitness_name"] = fitness
        payload["fitness_value"] = float(payload["fitness"].get(fitness, math.nan))
        rows.append(payload)
        if i % 1000 == 0:
            print(f"scored_discovery={i}/{len(candidates)}", flush=True)
    rows.sort(key=lambda row: row["fitness_value"], reverse=True)

    print(f"exact_rerank={min(exact_top, len(rows))} rolling_step=1", flush=True)
    exact_cache = build_benchmark_cache(frame["SPYSIM"], frame["QQQSIM"], rolling_step=1, compute_drawdown=True)
    exact_rows = []
    for row in rows[:exact_top]:
        weights = row["weights"]
        exact = score_portfolio(
            frame,
            weights,
            rolling_step=1,
            benchmark_cache=exact_cache,
            compute_drawdown=True,
        )
        payload = score_to_dict(exact)
        payload["chromosome"] = row["chromosome"]
        payload["fitness_name"] = fitness
        payload["fitness_value"] = float(payload["fitness"].get(fitness, math.nan))
        payload["sampled_fitness_value"] = row["fitness_value"]
        exact_rows.append(payload)
    exact_rows.sort(key=lambda row: row["fitness_value"], reverse=True)
    benchmarks = {
        name: score_to_dict(score)
        for name, score in score_named_benchmarks(
            universe, frame, rolling_step=1, benchmark_cache=exact_cache, compute_drawdown=True
        ).items()
    }
    return {"top_sampled": rows[: min(200, len(rows))], "top_exact": exact_rows, "benchmarks": benchmarks}


def flatten(rows: list[dict]) -> pd.DataFrame:
    out = []
    for rank, row in enumerate(rows, start=1):
        flat = {
            "rank": rank,
            "fitness_value": row["fitness_value"],
            "sampled_fitness_value": row.get("sampled_fitness_value"),
            "weights": json.dumps(row["weights"], sort_keys=True),
        }
        flat.update({f"full_{k}": v for k, v in row["full_metrics"].items()})
        flat.update({f"fit_{k}": v for k, v in row["fitness"].items()})
        flat.update({f"exposure_{k}": v for k, v in row["exposure"].items()})
        out.append(flat)
    return pd.DataFrame(out)


def write_report(payload: dict, run_dir: Path) -> None:
    best = payload["top_exact"][0]
    top_md = flatten(payload["top_exact"]).head(20).to_markdown(index=False)
    bench_rows = []
    for name, score in payload["benchmarks"].items():
        metrics = score["full_metrics"]
        bench_rows.append(
            {
                "benchmark": name,
                "cagr": metrics["cagr"],
                "mdd": metrics["mdd"],
                "sharpe": metrics["sharpe"],
                "calmar": metrics["calmar"],
                "terminal_wealth": metrics["terminal_wealth"],
            }
        )
    bench_md = pd.DataFrame(bench_rows).to_markdown(index=False)
    report = f"""# Incumbent Refinement Report

## Run

- Universe: `{payload['universe']}`
- Fitness: `{payload['fitness']}`
- Candidate pool: `{payload['candidate_tickers']}`
- Candidate count: `{payload['candidate_count']}`
- Discovery rolling step: `{payload['discovery_rolling_step']}`
- Exact top rerank: `{payload['exact_top']}`

This is discovery-only refinement around a GA incumbent, not validation.

## Best Exact Candidate

- Fitness: `{best['fitness_value']:.6f}`
- Weights: `{format_weights(best['weights'])}`
- Effective exposure: `{json.dumps(best['exposure'], sort_keys=True)}`

## Top Exact Candidates

{top_md}

## Benchmarks

{bench_md}
"""
    (run_dir / "REPORT.md").write_text(report, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", choices=sorted(UNIVERSES), required=True)
    parser.add_argument("--fitness", default="balanced_spy_beater")
    parser.add_argument("--incumbent", help='JSON weights. Defaults to known GA incumbent for core_1986/mf_1988.')
    parser.add_argument("--pool", help="Comma-separated candidate pool. Defaults to focused pool for universe.")
    parser.add_argument("--max-active-grid", type=int, default=3)
    parser.add_argument("--local-depth", type=int, default=2)
    parser.add_argument("--max-assets", type=int, default=6)
    parser.add_argument("--discovery-rolling-step", type=int, default=21)
    parser.add_argument("--exact-top", type=int, default=200)
    parser.add_argument("--output-dir", type=Path, default=Path("studies/static_spy_beater_portfolio/results/refine"))
    args = parser.parse_args()

    universe_tickers = UNIVERSES[args.universe]
    incumbent = parse_weights(args.incumbent, args.universe)
    pool = args.pool.split(",") if args.pool else list(FOCUSED_POOLS.get(args.universe, universe_tickers))
    candidate_tickers = list(dict.fromkeys(list(incumbent) + [ticker for ticker in pool if ticker in universe_tickers]))
    if any(ticker not in universe_tickers for ticker in candidate_tickers):
        missing = [ticker for ticker in candidate_tickers if ticker not in universe_tickers]
        raise ValueError(f"candidate tickers not in universe {args.universe}: {missing}")

    frame = load_universe_returns(args.universe)
    start, end, _rows = common_window(frame, universe_tickers)
    required_columns = list(dict.fromkeys(candidate_tickers + ["SPYSIM", "QQQSIM"] + universe_tickers))
    frame = frame.loc[start:end, required_columns].dropna()

    incumbent_units = units_from_weights(incumbent, candidate_tickers)
    candidates = simplex_candidates(candidate_tickers, args.max_active_grid)
    candidates |= local_edit_candidates(incumbent_units, depth=args.local_depth, max_active=args.max_assets)

    print(
        f"refine universe={args.universe} assets={len(candidate_tickers)} candidates={len(candidates)} "
        f"grid_max_active={args.max_active_grid} local_depth={args.local_depth}",
        flush=True,
    )
    result = score_candidates(
        frame,
        candidate_tickers,
        candidates,
        universe=args.universe,
        fitness=args.fitness,
        discovery_rolling_step=args.discovery_rolling_step,
        exact_top=args.exact_top,
    )
    payload = {
        "universe": args.universe,
        "fitness": args.fitness,
        "incumbent": incumbent,
        "candidate_tickers": candidate_tickers,
        "candidate_count": len(candidates),
        "max_active_grid": args.max_active_grid,
        "local_depth": args.local_depth,
        "max_assets": args.max_assets,
        "discovery_rolling_step": args.discovery_rolling_step,
        "exact_top": args.exact_top,
        "discovery_only": True,
        **result,
    }
    slug = f"{args.universe}_{args.fitness}_refine"
    run_dir = args.output_dir / slug
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "results.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    flatten(payload["top_exact"]).to_csv(run_dir / "top_exact.csv", index=False)
    flatten(payload["top_sampled"]).to_csv(run_dir / "top_sampled.csv", index=False)
    write_report(payload, run_dir)
    best = payload["top_exact"][0]
    print(f"wrote {run_dir}")
    print(f"best_exact fitness={best['fitness_value']:.6f} weights={format_weights(best['weights'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
