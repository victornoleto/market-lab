"""Controlled GA evolutions for SPY/SSO/UPRO rotation discovery.

This runner is a minimal S&P 500 focused adaptation of the repair-GA idea from
`technical_signal_vote_hunt`. It tests both clean underlying signals (`SPY`) and
LETF self-signals (`SSO`). The GA is discovery only; PBO/DSR remain mandatory
post-search gates `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`,
and every unique gene counted here must be included in cumulative trial accounting
`[advances_fin_ml, p.222-223]`.
"""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.core.data_loader import load_testfolio_series
from studies.letf_rotation_hunt.core.signals import ar1_coefficient, realized_vol_gate, sma_gate, vote_of_k
from studies.technical_signal_vote_hunt.core import build_rearm_gate, daily_returns
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import _metrics_row_np


REPO_ROOT = Path(__file__).resolve().parents[3]
RESULTS_DIR = REPO_ROOT / "studies/spy_leveraged_rotation_hunt/results/ga_evolutions"
REPORT_DIR = REPO_ROOT / "studies/spy_leveraged_rotation_hunt/reports"
TRADING_DAYS_PER_YEAR = 252


@dataclass(frozen=True)
class Gene:
    signal_asset: str
    sma_long: int
    sma_short: int
    vol_window: int
    vol_threshold: float
    ar_window: int
    entry_k: int
    t_crash: int
    d_arm: int
    normal_upro_weight: float
    rearm_upro_weight: float
    zroz_off_weight: float


@dataclass(frozen=True)
class EvolutionSpec:
    name: str
    objective: str
    signal_assets: tuple[str, ...]
    normal_upro_weights: tuple[float, ...]
    rearm_upro_weights: tuple[float, ...]
    zroz_off_weights: tuple[float, ...]
    t_values: tuple[int, ...]
    d_values: tuple[int, ...]
    entry_ks: tuple[int, ...]
    mdd_floor: float
    description: str


class Context:
    def __init__(self) -> None:
        self.prices = {
            "SPY": load_testfolio_series("SPYSIM"),
            "SSO": load_testfolio_series("SSOSIM"),
            "UPRO": load_testfolio_series("UPROSIM"),
            "CASH": load_testfolio_series("CASHX"),
            "ZROZ": load_testfolio_series("ZROZSIM"),
        }
        self.returns = {k: daily_returns(v) for k, v in self.prices.items()}
        self.primitive_cache: dict[tuple, pd.Series] = {}
        self.on_cache: dict[tuple, pd.Series] = {}
        self.rearm_cache: dict[tuple, pd.Series] = {}
        self.spy_buyhold = self.returns["SPY"]
        spy = self.spy_buyhold.dropna()
        self.spy_metrics = _metrics_row_np(
            spy.to_numpy(float),
            spy.to_numpy(float),
            pd.DatetimeIndex(spy.index),
            "SPY",
            "SPY",
            "spy",
            0,
            0,
            "bench",
        )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run SPY leveraged rotation GA evolutions")
    p.add_argument("--case", default="all", help="all or comma-separated evolution names")
    p.add_argument("--population", type=int, default=96)
    p.add_argument("--generations-per-case", type=int, default=35)
    p.add_argument("--elite", type=int, default=16)
    p.add_argument("--seed", type=int, default=91)
    p.add_argument("--progress-every", type=int, default=1)
    p.add_argument("--eval-progress-every", type=int, default=0)
    p.add_argument("--checkpoint-every", type=int, default=1)
    p.add_argument("--stagnation-generations", type=int, default=15)
    p.add_argument("--out-dir", type=Path, default=RESULTS_DIR)
    p.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.elite < 1 or args.elite >= args.population:
        raise SystemExit("Require 1 <= elite < population")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    ctx = Context()
    specs = _selected_specs(args.case)
    summaries = _load_existing_summaries(args.out_dir, {s.name for s in specs})
    for i, spec in enumerate(specs, start=1):
        summary = _run_evolution(ctx, spec, args, args.seed + i * 1000)
        summaries.append(summary)
        _write_master_report(args.report_dir / "GA_EVOLUTION_REPORT.md", summaries)
    print(f"wrote {args.report_dir / 'GA_EVOLUTION_REPORT.md'}", flush=True)
    return 0


def _selected_specs(case_arg: str) -> list[EvolutionSpec]:
    specs = _evolution_specs()
    if case_arg == "all":
        return specs
    wanted = {x.strip() for x in case_arg.split(",") if x.strip()}
    by_name = {s.name: s for s in specs}
    missing = sorted(wanted - set(by_name))
    if missing:
        raise ValueError(f"unknown evolution(s): {missing}; available={sorted(by_name)}")
    return [s for s in specs if s.name in wanted]


def _evolution_specs() -> list[EvolutionSpec]:
    return [
        EvolutionSpec(
            "evo01_spy_sso_repair",
            "spy_sso_repair",
            ("SPY",),
            (0.0, 0.10, 0.25),
            (0.0, 0.25, 0.50),
            (0.0, 0.25, 0.50),
            (15, 20, 25, 30, 35, 45, 60),
            (30, 45, 60, 90, 120),
            (1, 2, 3, 4),
            -0.50,
            "SPY underlying-signal repair with SSO-dominant execution.",
        ),
        EvolutionSpec(
            "evo02_spy_upro_performance",
            "spy_upro_performance",
            ("SPY",),
            (0.50, 0.75, 1.0),
            (0.75, 1.0),
            (0.0, 0.25),
            (10, 15, 20, 25, 30, 35, 45, 60),
            (30, 45, 60, 90, 120),
            (1, 2, 3, 4),
            -0.70,
            "SPY underlying-signal performance branch with UPRO-heavy execution.",
        ),
        EvolutionSpec(
            "evo03_sso_self_balanced",
            "sso_self_balanced",
            ("SSO",),
            (0.0, 0.25, 0.50, 0.75),
            (0.25, 0.50, 0.75, 1.0),
            (0.0, 0.25, 0.50),
            (10, 15, 20, 25, 30, 35, 45, 60),
            (30, 45, 60, 90, 120),
            (1, 2, 3, 4),
            -0.65,
            "SSO LETF-self-signal balanced branch.",
        ),
        EvolutionSpec(
            "evo04_execution_lag_robust",
            "execution_lag_robust",
            ("SPY", "SSO"),
            (0.0, 0.25, 0.50, 0.75, 1.0),
            (0.0, 0.25, 0.50, 0.75, 1.0),
            (0.0, 0.25, 0.50),
            (15, 20, 25, 30, 35, 45, 60),
            (30, 45, 60, 90, 120),
            (1, 2, 3, 4),
            -0.70,
            "Average score under extra execution lags 0/1/2.",
        ),
        EvolutionSpec(
            "evo05_diversity_low_corr",
            "diversity_low_corr",
            ("SPY", "SSO"),
            (0.0, 0.25, 0.50, 0.75, 1.0),
            (0.0, 0.25, 0.50, 0.75, 1.0),
            (0.0, 0.25, 0.50, 0.75),
            (10, 15, 20, 25, 30, 35, 45, 60),
            (30, 45, 60, 90, 120, 150),
            (1, 2, 3, 4),
            -0.75,
            "Search for lower correlation to SPY while preserving economics.",
        ),
        EvolutionSpec(
            "evo06_conservative_drawdown",
            "conservative_drawdown",
            ("SPY", "SSO"),
            (0.0, 0.10, 0.25, 0.50),
            (0.0, 0.25, 0.50),
            (0.0, 0.25, 0.50, 0.75),
            (20, 25, 30, 35, 45, 60),
            (30, 45, 60, 90),
            (2, 3, 4),
            -0.45,
            "Conservative drawdown-focused S&P 500 branch.",
        ),
    ]


def _run_evolution(ctx: Context, spec: EvolutionSpec, args: argparse.Namespace, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    out_dir = args.out_dir / spec.name
    tables_dir = out_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    population = [_random_gene(rng, spec) for _ in range(args.population)]
    population[0] = _anchor_gene(spec)
    seen: dict[Gene, dict] = {}
    history: list[dict] = []
    best_fitness_seen = -np.inf
    stagnant = 0
    generation = 0
    while generation < args.generations_per_case:
        generation += 1
        scored = []
        for i, gene in enumerate(population, start=1):
            if gene not in seen:
                seen[gene] = _evaluate(ctx, gene, spec)
                if args.eval_progress_every > 0 and len(seen) % args.eval_progress_every == 0:
                    print(f"{spec.name} gen={generation:04d} eval_in_gen={i:04d}/{len(population)} unique={len(seen):,}", flush=True)
            scored.append(seen[gene])
        df = pd.DataFrame(scored).sort_values("fitness", ascending=False)
        best = df.iloc[0].to_dict()
        best["generation"] = generation
        best["evaluated_unique"] = len(seen)
        history.append(best)
        if args.progress_every > 0 and generation % args.progress_every == 0:
            print(
                f"{spec.name} gen={generation:04d} eval={len(seen):,} fit={best['fitness']:.4f} "
                f"sortino={best['sortino']:.4f} cagr={best['cagr']:.4f} mdd={best['mdd']:.4f} {best['label']}",
                flush=True,
            )
        if args.checkpoint_every > 0 and generation % args.checkpoint_every == 0:
            _write_checkpoint(out_dir, spec, seen, history, seed, time.perf_counter() - started)
        if float(best["fitness"]) > best_fitness_seen + 1e-12:
            best_fitness_seen = float(best["fitness"])
            stagnant = 0
        else:
            stagnant += 1
        if args.stagnation_generations > 0 and stagnant >= args.stagnation_generations:
            print(f"{spec.name} early_stop stagnant_generations={stagnant} best_fit={best_fitness_seen:.4f}", flush=True)
            break
        elites = [_row_to_gene(row) for row in df.head(args.elite).to_dict("records")]
        next_pop = elites[:]
        while len(next_pop) < args.population:
            a = elites[int(rng.integers(0, len(elites)))]
            b = elites[int(rng.integers(0, len(elites)))]
            next_pop.append(_mutate(_crossover(a, b, rng), rng, spec))
        population = next_pop

    all_df = pd.DataFrame(seen.values()).sort_values("fitness", ascending=False)
    hist_df = pd.DataFrame(history)
    top_df = all_df.head(100).copy()
    all_df.to_csv(tables_dir / "all_candidates.csv", index=False)
    top_df.to_csv(tables_dir / "top_candidates.csv", index=False)
    hist_df.to_csv(tables_dir / "best_by_generation.csv", index=False)
    elapsed = time.perf_counter() - started
    _write_case_report(out_dir, spec, top_df, hist_df, seed, elapsed)
    summary = _case_summary(spec, top_df.iloc[0].to_dict(), len(seen), generation, seed, elapsed)
    (out_dir / "manifest.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def _anchor_gene(spec: EvolutionSpec) -> Gene:
    signal_asset = spec.signal_assets[0]
    return Gene(signal_asset, 200, 100, 21, 0.40, 30, min(2, max(spec.entry_ks)), 35, 60, spec.normal_upro_weights[0], spec.rearm_upro_weights[-1], spec.zroz_off_weights[0])


def _random_gene(rng: np.random.Generator, spec: EvolutionSpec) -> Gene:
    sma_long = int(rng.choice([150, 180, 200, 225, 250, 275, 300]))
    sma_short = int(rng.choice([20, 50, 75, 100, 125, 150]))
    if sma_short >= sma_long:
        sma_short = 100
        sma_long = 200
    return Gene(
        signal_asset=str(rng.choice(spec.signal_assets)),
        sma_long=sma_long,
        sma_short=sma_short,
        vol_window=int(rng.choice([10, 21, 42, 63])),
        vol_threshold=float(rng.choice([0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60])),
        ar_window=int(rng.choice([20, 30, 40, 60])),
        entry_k=int(rng.choice(spec.entry_ks)),
        t_crash=int(rng.choice(spec.t_values)),
        d_arm=int(rng.choice(spec.d_values)),
        normal_upro_weight=float(rng.choice(spec.normal_upro_weights)),
        rearm_upro_weight=float(rng.choice(spec.rearm_upro_weights)),
        zroz_off_weight=float(rng.choice(spec.zroz_off_weights)),
    )


def _crossover(a: Gene, b: Gene, rng: np.random.Generator) -> Gene:
    vals = [av if rng.random() < 0.5 else bv for av, bv in zip(a.__dict__.values(), b.__dict__.values(), strict=True)]
    return Gene(*vals)


def _mutate(g: Gene, rng: np.random.Generator, spec: EvolutionSpec) -> Gene:
    vals = list(g.__dict__.values())
    opts = [
        list(spec.signal_assets),
        [150, 180, 200, 225, 250, 275, 300],
        [20, 50, 75, 100, 125, 150],
        [10, 21, 42, 63],
        [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60],
        [20, 30, 40, 60],
        list(spec.entry_ks),
        list(spec.t_values),
        list(spec.d_values),
        list(spec.normal_upro_weights),
        list(spec.rearm_upro_weights),
        list(spec.zroz_off_weights),
    ]
    for i, choices in enumerate(opts):
        if rng.random() < 0.12:
            vals[i] = choices[int(rng.integers(0, len(choices)))]
    if int(vals[2]) >= int(vals[1]):
        vals[2] = 100
        vals[1] = 200
    return Gene(*vals)


def _evaluate(ctx: Context, gene: Gene, spec: EvolutionSpec) -> dict:
    if spec.objective == "execution_lag_robust":
        return _evaluate_lag_robust(ctx, gene, spec)
    r = _returns_for_gene(ctx, gene)
    row = _metrics(ctx, r, _label(gene), spec.name)
    row.update(gene.__dict__)
    row.update(_rolling_features(r))
    row["corr_to_spy"] = _corr(ctx.spy_buyhold, r)
    row["beats_spy_economic"] = _beats_spy(ctx, row)
    row["fitness"] = _fitness(row, spec)
    return row


def _evaluate_lag_robust(ctx: Context, gene: Gene, spec: EvolutionSpec) -> dict:
    rows = []
    for extra_lag in (0, 1, 2):
        r = _returns_for_gene(ctx, gene, extra_lag=extra_lag)
        row = _metrics(ctx, r, f"{_label(gene)}_lag{extra_lag}", spec.name)
        row.update(_rolling_features(r))
        rows.append(row)
    base = rows[0].copy()
    base["label"] = _label(gene)
    for field in ("sortino", "cagr", "sharpe", "mdd", "calmar", "min_3y_cagr", "min_5y_cagr", "min_10y_cagr"):
        vals = [float(x[field]) for x in rows]
        base[field] = float(np.min(vals)) if field in {"mdd", "min_3y_cagr", "min_5y_cagr", "min_10y_cagr"} else float(np.mean(vals))
        base[f"worst_{field}"] = float(np.min(vals))
    r0 = _returns_for_gene(ctx, gene)
    base.update(gene.__dict__)
    base["corr_to_spy"] = _corr(ctx.spy_buyhold, r0)
    base["beats_spy_economic"] = _beats_spy(ctx, base)
    base["fitness"] = _fitness(base, spec)
    return base


def _returns_for_gene(ctx: Context, gene: Gene, extra_lag: int = 0) -> pd.Series:
    on_signal = _on_signal(ctx, gene)
    rearm = _rearm_signal(ctx, gene, on_signal)
    aligned = pd.concat(
        {
            "sig": on_signal.shift(1 + extra_lag),
            "rearm": rearm.shift(1 + extra_lag),
            "sso": ctx.returns["SSO"],
            "upro": ctx.returns["UPRO"],
            "cash": ctx.returns["CASH"],
            "zroz": ctx.returns["ZROZ"],
        },
        axis=1,
        sort=False,
    ).dropna(subset=["sso", "upro", "cash", "zroz"])
    normal_on = (1.0 - gene.normal_upro_weight) * aligned["sso"] + gene.normal_upro_weight * aligned["upro"]
    rearm_on = (1.0 - gene.rearm_upro_weight) * aligned["sso"] + gene.rearm_upro_weight * aligned["upro"]
    on_leg = np.where(aligned["rearm"].fillna(0.0).to_numpy(float) >= 1.0, rearm_on, normal_on)
    off_leg = (1.0 - gene.zroz_off_weight) * aligned["cash"] + gene.zroz_off_weight * aligned["zroz"]
    is_on = aligned["sig"].fillna(0.0).to_numpy(float) >= 1.0
    return pd.Series(np.where(is_on, on_leg, off_leg), index=aligned.index)


def _on_signal(ctx: Context, gene: Gene) -> pd.Series:
    key = (gene.signal_asset, gene.sma_long, gene.sma_short, gene.vol_window, gene.vol_threshold, gene.ar_window, gene.entry_k)
    if key not in ctx.on_cache:
        ctx.on_cache[key] = vote_of_k(_components(ctx, gene), k=gene.entry_k)
    return ctx.on_cache[key]


def _rearm_signal(ctx: Context, gene: Gene, on_signal: pd.Series) -> pd.Series:
    key = (gene.signal_asset, gene.sma_long, gene.sma_short, gene.vol_window, gene.vol_threshold, gene.ar_window, gene.entry_k, gene.t_crash, gene.d_arm)
    if key not in ctx.rearm_cache:
        ctx.rearm_cache[key] = build_rearm_gate(on_signal, t_crash=gene.t_crash, d_arm=gene.d_arm)
    return ctx.rearm_cache[key]


def _components(ctx: Context, gene: Gene) -> list[pd.Series]:
    return [
        _primitive(ctx, gene.signal_asset, "sma", gene.sma_long),
        _primitive(ctx, gene.signal_asset, "sma", gene.sma_short),
        _primitive(ctx, gene.signal_asset, "vol", gene.vol_window, gene.vol_threshold),
        _primitive(ctx, gene.signal_asset, "ar", gene.ar_window),
    ]


def _primitive(ctx: Context, asset: str, kind: str, *params: float | int) -> pd.Series:
    key = (asset, kind, *params)
    if key in ctx.primitive_cache:
        return ctx.primitive_cache[key]
    px = ctx.prices[asset]
    ret = ctx.returns[asset]
    if kind == "sma":
        value = sma_gate(px, period=int(params[0]))
    elif kind == "vol":
        value = realized_vol_gate(ret, window=int(params[0]), threshold=float(params[1]))
    elif kind == "ar":
        ar = ar1_coefficient(ret, window=int(params[0]))
        value = (ar > 0.0).astype(float)
        value[ar.isna()] = np.nan
    else:
        raise ValueError(f"unknown primitive kind: {kind}")
    ctx.primitive_cache[key] = value
    return value


def _metrics(ctx: Context, returns: pd.Series, label: str, case: str) -> dict:
    aligned = pd.concat({"r": returns, "b": ctx.spy_buyhold}, axis=1, sort=False).dropna()
    return _metrics_row_np(aligned["r"].to_numpy(float), aligned["b"].to_numpy(float), pd.DatetimeIndex(aligned.index), label, "SPY", case, 0, 0, "ga")


def _rolling_features(returns: pd.Series) -> dict:
    out: dict[str, float] = {}
    r = returns.dropna()
    for years in (3, 5, 10, 15):
        vals = (1.0 + r).rolling(years * TRADING_DAYS_PER_YEAR).apply(np.prod, raw=True).dropna()
        cagr = vals ** (1.0 / years) - 1.0
        out[f"min_{years}y_cagr"] = float(cagr.min()) if len(cagr) else np.nan
        out[f"pct_pos_{years}y"] = float((cagr > 0.0).mean()) if len(cagr) else np.nan
    return out


def _corr(a: pd.Series, b: pd.Series) -> float:
    aligned = pd.concat({"a": a, "b": b}, axis=1, sort=False).dropna()
    if len(aligned) < 100 or aligned["a"].std() == 0 or aligned["b"].std() == 0:
        return 1.0
    return float(aligned["a"].corr(aligned["b"]))


def _beats_spy(ctx: Context, row: dict) -> bool:
    spy_metrics = ctx.spy_metrics
    return bool(row["cagr"] > spy_metrics["cagr"] and row["sharpe"] > spy_metrics["sharpe"] and row["sortino"] > spy_metrics["sortino"] and row["mdd"] > spy_metrics["mdd"])


def _fitness(row: dict, spec: EvolutionSpec) -> float:
    cagr = float(row["cagr"])
    sharpe = float(row["sharpe"])
    sortino = float(row["sortino"])
    mdd = float(row["mdd"])
    calmar = float(row["calmar"])
    min3 = float(row.get("min_3y_cagr", -1.0))
    min5 = float(row.get("min_5y_cagr", -1.0))
    min10 = float(row.get("min_10y_cagr", -1.0))
    corr = float(row.get("corr_to_spy", 1.0))
    dd_penalty = max(0.0, spec.mdd_floor - mdd)
    base = 2.0 * sortino + 1.0 * sharpe + 4.0 * cagr + 1.5 * calmar + 0.75 * min5 + 0.50 * min10 + 0.25 * min3 - 8.0 * dd_penalty
    if spec.objective == "spy_sso_repair":
        return base + 1.5 * mdd - 0.5 * float(row["normal_upro_weight"])
    if spec.objective == "spy_upro_performance":
        return base + 3.0 * cagr - 8.0 * max(0.0, -0.80 - mdd)
    if spec.objective == "sso_self_balanced":
        return base + 0.5 * calmar
    if spec.objective == "execution_lag_robust":
        return base + 1.5 * float(row.get("worst_calmar", calmar)) + float(row.get("worst_min_5y_cagr", min5))
    if spec.objective == "diversity_low_corr":
        return base + 2.0 * (1.0 - corr) - 2.0 * max(0.0, 0.15 - cagr)
    if spec.objective == "conservative_drawdown":
        return base + 2.5 * mdd - 0.75 * float(row["normal_upro_weight"])
    return base


def _label(g: Gene) -> str:
    return (
        f"{g.signal_asset}_s{g.sma_short}_{g.sma_long}_vw{g.vol_window}_vt{g.vol_threshold:.2f}_ar{g.ar_window}_"
        f"k{g.entry_k}_T{g.t_crash}D{g.d_arm}_nw{g.normal_upro_weight:.2f}_rw{g.rearm_upro_weight:.2f}_z{g.zroz_off_weight:.2f}"
    )


def _row_to_gene(row: dict) -> Gene:
    return Gene(
        str(row["signal_asset"]),
        int(row["sma_long"]),
        int(row["sma_short"]),
        int(row["vol_window"]),
        float(row["vol_threshold"]),
        int(row["ar_window"]),
        int(row["entry_k"]),
        int(row["t_crash"]),
        int(row["d_arm"]),
        float(row["normal_upro_weight"]),
        float(row["rearm_upro_weight"]),
        float(row["zroz_off_weight"]),
    )


def _write_checkpoint(out_dir: Path, spec: EvolutionSpec, seen: dict[Gene, dict], history: list[dict], seed: int, elapsed: float) -> None:
    tables_dir = out_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    top = pd.DataFrame(seen.values()).sort_values("fitness", ascending=False).head(100)
    hist = pd.DataFrame(history)
    top.to_csv(tables_dir / "top_candidates_partial.csv", index=False)
    hist.to_csv(tables_dir / "best_by_generation_partial.csv", index=False)
    _write_case_report(out_dir, spec, top, hist, seed, elapsed)


def _write_case_report(out_dir: Path, spec: EvolutionSpec, top: pd.DataFrame, history: pd.DataFrame, seed: int, elapsed_seconds: float) -> None:
    cols = [
        "label", "fitness", "sortino", "cagr", "sharpe", "mdd", "calmar", "end_mult", "end_rel_to_benchmark",
        "min_3y_cagr", "min_5y_cagr", "min_10y_cagr", "min_15y_cagr", "corr_to_spy", "beats_spy_economic",
        "signal_asset", "sma_long", "sma_short", "vol_window", "vol_threshold", "ar_window", "entry_k", "t_crash", "d_arm",
        "normal_upro_weight", "rearm_upro_weight", "zroz_off_weight",
    ]
    existing = [c for c in cols if c in top.columns]
    lines = [
        f"# {spec.name}",
        "",
        f"Description: {spec.description}",
        f"Seed: `{seed}`",
        f"Elapsed minutes: `{elapsed_seconds / 60.0:.2f}`",
        f"Generations completed: `{int(history['generation'].max())}`",
        f"Unique candidates evaluated: `{int(history['evaluated_unique'].max())}`",
        "",
        "## Best Candidate",
        "",
        top.head(1)[existing].to_markdown(index=False, floatfmt=".4f") if len(top) else "No candidates yet.",
        "",
        "## Top 20",
        "",
        top.head(20)[existing].to_markdown(index=False, floatfmt=".4f") if len(top) else "No candidates yet.",
        "",
        "## Best By Generation Tail",
        "",
        history.tail(20)[["generation", "evaluated_unique", "fitness", "sortino", "cagr", "mdd", "label"]].to_markdown(index=False, floatfmt=".4f") if len(history) else "No history yet.",
        "",
        "## Method Note",
        "",
        "This is GA discovery only. Signals use one-day execution lag; any candidate requires OOS/FWD/WF/bootstrap/PBO/DSR validation before claims `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.",
    ]
    (out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _case_summary(spec: EvolutionSpec, best: dict, evaluated: int, generations: int, seed: int, elapsed_seconds: float) -> dict:
    return {
        "name": spec.name,
        "objective": spec.objective,
        "seed": seed,
        "evaluated_unique": int(evaluated),
        "generations": int(generations),
        "elapsed_minutes": float(elapsed_seconds / 60.0),
        "best_label": str(best["label"]),
        "best_signal_asset": str(best["signal_asset"]),
        "best_fitness": float(best["fitness"]),
        "best_sortino": float(best["sortino"]),
        "best_cagr": float(best["cagr"]),
        "best_sharpe": float(best["sharpe"]),
        "best_mdd": float(best["mdd"]),
        "best_calmar": float(best["calmar"]),
        "best_corr_to_spy": float(best["corr_to_spy"]),
        "beats_spy_economic": bool(best["beats_spy_economic"]),
    }


def _write_master_report(path: Path, summaries: list[dict]) -> None:
    df = pd.DataFrame(summaries).drop_duplicates(subset=["name"], keep="last")
    if len(df):
        df = df.sort_values(["beats_spy_economic", "best_sortino", "best_cagr"], ascending=[False, False, False])
    total = int(df["evaluated_unique"].sum()) if len(df) else 0
    spy_signal = df[df["best_signal_asset"] == "SPY"] if len(df) else pd.DataFrame()
    sso_signal = df[df["best_signal_asset"] == "SSO"] if len(df) else pd.DataFrame()
    lines = [
        "# SPY Leveraged Rotation GA Evolution Report",
        "",
        f"Completed evolutions: `{len(df)}`",
        f"Unique candidates in final manifests: `{total}`",
        "",
        "## Ranking",
        "",
        df.to_markdown(index=False, floatfmt=".4f") if len(df) else "No runs yet.",
        "",
        "## SPY-Signal vs SSO-Self-Signal",
        "",
        _signal_summary("SPY underlying-signal", spy_signal),
        "",
        _signal_summary("SSO LETF-self-signal", sso_signal),
        "",
        "## Interpretation",
        "",
        "Rows with `beats_spy_economic=True` beat `SPY buy_hold` on CAGR, Sharpe, Sortino and MaxDD in the long-history panel. This is an initial economic screen only, not validation. No candidate is deployable without OOS/FWD/WF/bootstrap/PBO/DSR and cumulative trial accounting `[advances_fin_ml, p.222-223]`.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _signal_summary(label: str, df: pd.DataFrame) -> str:
    if not len(df):
        return f"{label}: no best candidate in completed manifests."
    best = df.sort_values(["beats_spy_economic", "best_sortino", "best_cagr"], ascending=[False, False, False]).iloc[0]
    return (
        f"{label}: best `{best['name']}` / `{best['best_label']}` with "
        f"Sortino `{best['best_sortino']:.4f}`, CAGR `{best['best_cagr']:.2%}`, "
        f"MDD `{best['best_mdd']:.2%}`, beats_spy_economic=`{bool(best['beats_spy_economic'])}`."
    )


def _load_existing_summaries(out_dir: Path, skip_names: set[str]) -> list[dict]:
    summaries = []
    if not out_dir.exists():
        return summaries
    for path in sorted(out_dir.glob("evo*/manifest.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if data.get("name") not in skip_names:
            summaries.append(data)
    return summaries


if __name__ == "__main__":
    raise SystemExit(main())
