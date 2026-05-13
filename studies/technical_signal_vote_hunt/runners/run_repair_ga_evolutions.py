"""Sequential repair GA evolutions after the QLD-vs-QQQ signal audit.

The goal is not another open-ended winner hunt. Each evolution changes the
question: QQQ-signal repair, rolling robustness, conservative turbo, QLD
simplification, execution robustness and equity-curve diversity. PBO/DSR remain
post-search gates; GA fitness is only an economic discovery tool
`[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.core.data_loader import load_testfolio_series
from studies.letf_rotation_hunt.core.signals import ar1_coefficient, realized_vol_gate, sma_gate, vote_of_k
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import _metrics_row_np


REPO_ROOT = Path(__file__).resolve().parents[3]
ITER030_BACKTEST = REPO_ROOT / "studies/letf_rotation_hunt/runs/post_close/030-2026-05-10-tcrash-scan-lrs120-rearmonly/backtest.py"
OUT_DIR = REPO_ROOT / "studies/technical_signal_vote_hunt/reports/repair_ga_evolutions"


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
    tqqq_weight: float
    lrs_factor: float
    gamma: float
    ratevol_window: int
    ratevol_threshold: float


@dataclass(frozen=True)
class EvolutionSpec:
    name: str
    objective: str
    signal_assets: tuple[str, ...]
    tqqq_weights: tuple[float, ...]
    lrs_factors: tuple[float, ...]
    t_values: tuple[int, ...]
    d_values: tuple[int, ...]
    entry_ks: tuple[int, ...]
    mdd_floor: float
    description: str


class Context:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run sequential repair GA evolutions")
    p.add_argument("--case", default="all", help="all or comma-separated evolution names")
    p.add_argument("--minutes-per-case", type=float, default=20.0, help="Legacy target note for reports; does not stop the GA when --generations-per-case is set")
    p.add_argument("--generations-per-case", type=int, default=120)
    p.add_argument("--population", type=int, default=384)
    p.add_argument("--elite", type=int, default=48)
    p.add_argument("--seed", type=int, default=71)
    p.add_argument("--out-dir", type=Path, default=OUT_DIR)
    p.add_argument("--progress-every", type=int, default=1)
    p.add_argument("--eval-progress-every", type=int, default=0)
    p.add_argument("--checkpoint-every", type=int, default=1)
    p.add_argument("--stagnation-generations", type=int, default=40)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    ctx = _prepare_context()
    specs = _selected_specs(args.case)
    summaries = _load_existing_summaries(args.out_dir, {s.name for s in specs})
    for idx, spec in enumerate(specs, start=1):
        case_seed = args.seed + idx * 1000
        summary = _run_evolution(ctx, spec, args, case_seed)
        summaries.append(summary)
        _write_master_report(args.out_dir, summaries)
    print(f"wrote {args.out_dir / 'REPORT.md'}", flush=True)
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
            "evo01_qqq_mdd_repair",
            "qqq_mdd_repair",
            ("QQQ",),
            (0.0, 0.25, 0.50, 0.75, 1.0),
            (1.00, 1.05, 1.10, 1.15, 1.20),
            (10, 15, 20, 25, 30, 35, 45, 60),
            (30, 45, 60, 90, 120),
            (1, 2, 3, 4),
            -0.65,
            "Repair the clean QQQ-signal version with a hard drawdown penalty.",
        ),
        EvolutionSpec(
            "evo02_qqq_rolling_repair",
            "qqq_rolling_repair",
            ("QQQ",),
            (0.0, 0.25, 0.50, 0.75, 1.0),
            (1.00, 1.05, 1.10, 1.15, 1.20),
            (10, 15, 20, 25, 30, 35, 45, 60),
            (30, 45, 60, 90, 120, 150),
            (1, 2, 3, 4),
            -0.70,
            "Search QQQ-signal variants that improve worst rolling 3y/5y behavior.",
        ),
        EvolutionSpec(
            "evo03_qqq_conservative_turbo",
            "qqq_conservative_turbo",
            ("QQQ",),
            (0.0, 0.25, 0.50),
            (1.00, 1.05, 1.10),
            (10, 15, 20, 25, 30, 35, 45, 60),
            (30, 45, 60, 90, 120),
            (2, 3, 4),
            -0.60,
            "Conservative QQQ-signal repair with capped TQQQ and LRS exposure.",
        ),
        EvolutionSpec(
            "evo04_qld_simplify",
            "qld_simplify",
            ("QLD",),
            (0.0, 0.25, 0.50, 0.75, 1.0),
            (1.00, 1.05, 1.10, 1.15, 1.20),
            (15, 20, 25, 30, 35, 45),
            (45, 60, 90, 120),
            (1, 2, 3),
            -0.58,
            "Compress the QLD self-regime family while preserving T20D90-like economics.",
        ),
        EvolutionSpec(
            "evo05_execution_robust",
            "execution_robust",
            ("QLD", "QQQ"),
            (0.0, 0.25, 0.50, 0.75, 1.0),
            (1.00, 1.05, 1.10, 1.15, 1.20),
            (15, 20, 25, 30, 35, 45),
            (45, 60, 90, 120),
            (1, 2, 3, 4),
            -0.65,
            "Score average behavior under added execution lags 0/1/2.",
        ),
        EvolutionSpec(
            "evo06_diversity_search",
            "diversity_search",
            ("QLD", "QQQ"),
            (0.0, 0.25, 0.50, 0.75, 1.0),
            (1.00, 1.05, 1.10, 1.15, 1.20),
            (10, 15, 20, 25, 30, 35, 45, 60),
            (30, 45, 60, 90, 120, 150),
            (1, 2, 3, 4),
            -0.70,
            "Look for economically decent variants with lower correlation to T20D90.",
        ),
    ]


def _prepare_context() -> Context:
    iter030 = _load_module(ITER030_BACKTEST, "repair_ga_iter030")
    prices = {
        "QQQ": load_testfolio_series("QQQSIM"),
        "QLD": load_testfolio_series("QLDSIM"),
        "TQQQ": load_testfolio_series("TQQQSIM"),
        "ZROZ": load_testfolio_series("ZROZSIM"),
        "CASH": load_testfolio_series("CASHX"),
        "SPY": load_testfolio_series("SPYSIM"),
    }
    returns = {k: v.pct_change().dropna() for k, v in prices.items()}
    baseline_t20d90 = Gene("QLD", 250, 100, 21, 0.40, 30, 2, 20, 90, 1.0, 1.20, 0.25, 60, 0.70)
    ctx = Context(
        iter030=iter030,
        prices=prices,
        returns=returns,
        baseline_t20d90_returns=None,
        primitive_cache={},
        ratevol_cache={},
    )
    ctx.baseline_t20d90_returns = _returns_for_gene(ctx, baseline_t20d90)
    return ctx


def _load_module(file_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {file_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_evolution(ctx: Context, spec: EvolutionSpec, args: argparse.Namespace, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    out_dir = args.out_dir / spec.name
    tables_dir = out_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    population = [_random_gene(rng, spec) for _ in range(args.population)]
    population[0] = _anchor_gene(spec)
    seen: dict[Gene, dict] = {}
    history = []
    generation = 0
    best_fitness_seen = -np.inf
    stagnant_generations = 0
    while generation < args.generations_per_case:
        generation += 1
        scored = []
        for i, gene in enumerate(population, start=1):
            if gene not in seen:
                row = _evaluate(ctx, gene, spec)
                seen[gene] = row
                if args.eval_progress_every > 0 and len(seen) % args.eval_progress_every == 0:
                    print(
                        f"{spec.name} gen={generation:04d} eval_in_gen={i:04d}/{len(population)} "
                        f"unique={len(seen):,}",
                        flush=True,
                    )
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
            _write_live_checkpoint(out_dir, spec, seen, history, seed, args.minutes_per_case, time.perf_counter() - started)
        if float(best["fitness"]) > best_fitness_seen + 1e-12:
            best_fitness_seen = float(best["fitness"])
            stagnant_generations = 0
        else:
            stagnant_generations += 1
        if args.stagnation_generations > 0 and stagnant_generations >= args.stagnation_generations:
            print(
                f"{spec.name} early_stop stagnant_generations={stagnant_generations} "
                f"best_fit={best_fitness_seen:.4f}",
                flush=True,
            )
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
    top_df = all_df.head(50).copy()
    all_df.to_csv(tables_dir / "all_candidates.csv", index=False)
    top_df.to_csv(tables_dir / "top_candidates.csv", index=False)
    hist_df.to_csv(tables_dir / "best_by_generation.csv", index=False)
    elapsed = time.perf_counter() - started
    _write_case_report(out_dir, spec, top_df, hist_df, seed, args.minutes_per_case, elapsed)
    summary = _case_summary(spec, top_df.iloc[0].to_dict(), len(seen), generation, seed, elapsed)
    (out_dir / "manifest.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def _write_live_checkpoint(
    out_dir: Path,
    spec: EvolutionSpec,
    seen: dict[Gene, dict],
    history: list[dict],
    seed: int,
    minutes: float,
    elapsed_seconds: float,
) -> None:
    tables_dir = out_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    top = pd.DataFrame(seen.values()).sort_values("fitness", ascending=False).head(50).copy()
    hist = pd.DataFrame(history)
    top.to_csv(tables_dir / "top_candidates_partial.csv", index=False)
    hist.to_csv(tables_dir / "best_by_generation_partial.csv", index=False)
    _write_case_report(out_dir, spec, top, hist, seed, minutes, elapsed_seconds)


def _anchor_gene(spec: EvolutionSpec) -> Gene:
    signal_asset = spec.signal_assets[0]
    if spec.name.startswith("evo01") or spec.name.startswith("evo02") or spec.name.startswith("evo03"):
        signal_asset = "QQQ"
    return Gene(signal_asset, 250, 100, 21, 0.40, 30, 2, 20, 90, min(1.0, max(spec.tqqq_weights)), max(spec.lrs_factors), 0.25, 60, 0.70)


def _random_gene(rng: np.random.Generator, spec: EvolutionSpec) -> Gene:
    sma_long = int(rng.choice([180, 200, 225, 250, 275, 300]))
    sma_short = int(rng.choice([50, 75, 100, 125, 150]))
    if sma_short >= sma_long:
        sma_short = 100
        sma_long = 250
    return Gene(
        signal_asset=str(rng.choice(spec.signal_assets)),
        sma_long=sma_long,
        sma_short=sma_short,
        vol_window=int(rng.choice([10, 21, 42, 63])),
        vol_threshold=float(rng.choice([0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60])),
        ar_window=int(rng.choice([20, 30, 40, 60])),
        entry_k=int(rng.choice(spec.entry_ks)),
        t_crash=int(rng.choice(spec.t_values)),
        d_arm=int(rng.choice(spec.d_values)),
        tqqq_weight=float(rng.choice(spec.tqqq_weights)),
        lrs_factor=float(rng.choice(spec.lrs_factors)),
        gamma=float(rng.choice([0.0, 0.10, 0.25, 0.40, 0.50])),
        ratevol_window=int(rng.choice([30, 60, 90, 120])),
        ratevol_threshold=float(rng.choice([0.60, 0.70, 0.80, 0.90])),
    )


def _crossover(a: Gene, b: Gene, rng: np.random.Generator) -> Gene:
    vals = [av if rng.random() < 0.5 else bv for av, bv in zip(a.__dict__.values(), b.__dict__.values(), strict=True)]
    return Gene(*vals)


def _mutate(g: Gene, rng: np.random.Generator, spec: EvolutionSpec) -> Gene:
    vals = list(g.__dict__.values())
    opts = [
        list(spec.signal_assets),
        [180, 200, 225, 250, 275, 300],
        [50, 75, 100, 125, 150],
        [10, 21, 42, 63],
        [0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60],
        [20, 30, 40, 60],
        list(spec.entry_ks),
        list(spec.t_values),
        list(spec.d_values),
        list(spec.tqqq_weights),
        list(spec.lrs_factors),
        [0.0, 0.10, 0.25, 0.40, 0.50],
        [30, 60, 90, 120],
        [0.60, 0.70, 0.80, 0.90],
    ]
    for i, choices in enumerate(opts):
        if rng.random() < 0.12:
            vals[i] = choices[int(rng.integers(0, len(choices)))]
    if int(vals[2]) >= int(vals[1]):
        vals[2] = 100
        vals[1] = 250
    return Gene(*vals)


def _evaluate(ctx: Context, gene: Gene, spec: EvolutionSpec) -> dict:
    if spec.objective == "execution_robust":
        return _evaluate_execution_robust(ctx, gene, spec)
    r = _returns_for_gene(ctx, gene)
    row = _metrics(ctx, r, _label(gene), spec.name)
    row.update(gene.__dict__)
    row.update(_rolling_features(r))
    row["corr_to_t20d90"] = _corr_to_baseline(ctx, r)
    row["fitness"] = _fitness(row, spec)
    return row


def _evaluate_execution_robust(ctx: Context, gene: Gene, spec: EvolutionSpec) -> dict:
    rows = []
    for extra_lag in (0, 1, 2):
        r = _returns_for_gene(ctx, gene, extra_lag=extra_lag)
        row = _metrics(ctx, r, f"{_label(gene)}_lag{extra_lag}", spec.name)
        row.update(_rolling_features(r))
        rows.append(row)
    base = rows[0].copy()
    base["label"] = _label(gene)
    for field in ("sortino", "cagr", "sharpe", "mdd", "calmar", "min_3y_cagr", "min_5y_cagr"):
        vals = [float(r[field]) for r in rows]
        base[field] = float(np.mean(vals)) if field != "mdd" else float(np.min(vals))
        base[f"worst_{field}"] = float(np.min(vals))
    base.update(gene.__dict__)
    base["corr_to_t20d90"] = _corr_to_baseline(ctx, _returns_for_gene(ctx, gene))
    base["fitness"] = _fitness(base, spec)
    return base


def _returns_for_gene(ctx: Context, gene: Gene, extra_lag: int = 0) -> pd.Series:
    on_signal = _on_signal(ctx, gene)
    rearm = _rearm_signal(ctx, gene, on_signal)
    up_lag = rearm.shift(1 + extra_lag)
    aligned = pd.concat({"q": ctx.returns["QLD"], "t": ctx.returns["TQQQ"], "u": up_lag}, axis=1, sort=False).dropna(subset=["q", "t"])
    turbo = (1.0 - gene.tqqq_weight) * aligned["q"] + gene.tqqq_weight * aligned["t"]
    on_leg = pd.Series(np.where(aligned["u"].fillna(0.0) == 1.0, turbo, aligned["q"]), index=aligned.index)
    on_for_mix = on_signal.shift(extra_lag) if extra_lag > 0 else on_signal
    on_leg_lrs = ctx.iter030.apply_unconditional_lrs_overlay(on_leg_returns=on_leg, on_signal=on_for_mix, lrs_factor=gene.lrs_factor)
    ratevol = _ratevol_signal(ctx, gene)
    ratevol = ratevol.shift(extra_lag) if extra_lag > 0 else ratevol
    return ctx.iter030.build_mechanism_mix_strategy_returns(
        on_signal=on_for_mix,
        on_leg_returns=on_leg_lrs,
        off_returns=ctx.returns["ZROZ"],
        alt_off_returns=ctx.returns["CASH"],
        ratevol_gate=ratevol,
        gamma=gene.gamma,
        use_off_override=gene.gamma > 0.0,
        drop_on_signal_warmup=False,
    )


def _entry_components(signal_px: pd.Series, signal_ret: pd.Series, gene: Gene) -> list[pd.Series]:
    s1 = sma_gate(signal_px, period=gene.sma_long)
    s2 = sma_gate(signal_px, period=gene.sma_short)
    s3 = realized_vol_gate(signal_ret, window=gene.vol_window, threshold=gene.vol_threshold)
    ar = ar1_coefficient(signal_ret, window=gene.ar_window)
    s4 = (ar > 0.0).astype(float)
    s4[ar.isna()] = np.nan
    return [s1, s2, s3, s4]


def _component_key(gene: Gene) -> tuple:
    return (gene.signal_asset, gene.sma_long, gene.sma_short, gene.vol_window, gene.vol_threshold, gene.ar_window)


def _on_key(gene: Gene) -> tuple:
    return (*_component_key(gene), gene.entry_k)


def _rearm_key(gene: Gene) -> tuple:
    return (*_on_key(gene), gene.t_crash, gene.d_arm)


def _ratevol_key(gene: Gene) -> tuple:
    return (gene.ratevol_window, gene.ratevol_threshold)


def _components(ctx: Context, gene: Gene) -> list[pd.Series]:
    return [
        _primitive(ctx, gene.signal_asset, "sma", gene.sma_long),
        _primitive(ctx, gene.signal_asset, "sma", gene.sma_short),
        _primitive(ctx, gene.signal_asset, "vol", gene.vol_window, gene.vol_threshold),
        _primitive(ctx, gene.signal_asset, "ar", gene.ar_window),
    ]


def _on_signal(ctx: Context, gene: Gene) -> pd.Series:
    return vote_of_k(_components(ctx, gene), k=gene.entry_k)


def _rearm_signal(ctx: Context, gene: Gene, on_signal: pd.Series) -> pd.Series:
    return ctx.iter030.build_postcrash_rearm_gate_independent(
        on_signal=on_signal,
        t_crash=gene.t_crash,
        d_arm=gene.d_arm,
    )


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


def _ratevol_signal(ctx: Context, gene: Gene) -> pd.Series:
    key = _ratevol_key(gene)
    if key not in ctx.ratevol_cache:
        ctx.ratevol_cache[key] = ctx.iter030.ratevol_regime_gate(
            ctx.returns["ZROZ"],
            vol_window=gene.ratevol_window,
            pct_window=1260,
            threshold=gene.ratevol_threshold,
        )
    return ctx.ratevol_cache[key]


def _metrics(ctx: Context, returns: pd.Series, label: str, case: str) -> dict:
    aligned = pd.concat({"r": returns, "b": ctx.returns["SPY"]}, axis=1, sort=False).dropna()
    return _metrics_row_np(aligned["r"].to_numpy(float), aligned["b"].to_numpy(float), pd.DatetimeIndex(aligned.index), label, "QQQ", case, 0, 0, "repair_ga")


def _rolling_features(returns: pd.Series) -> dict:
    out = {}
    r = returns.dropna()
    for years in (3, 5, 10):
        vals = (1.0 + r).rolling(years * 252).apply(np.prod, raw=True).dropna()
        cagr = vals ** (1.0 / years) - 1.0
        out[f"min_{years}y_cagr"] = float(cagr.min()) if len(cagr) else np.nan
        out[f"pct_pos_{years}y"] = float((cagr > 0.0).mean()) if len(cagr) else np.nan
    return out


def _corr_to_baseline(ctx: Context, returns: pd.Series) -> float:
    aligned = pd.concat({"a": returns, "b": ctx.baseline_t20d90_returns}, axis=1, sort=False).dropna()
    if len(aligned) < 100 or aligned["a"].std() == 0 or aligned["b"].std() == 0:
        return 1.0
    return float(aligned["a"].corr(aligned["b"]))


def _fitness(row: dict, spec: EvolutionSpec) -> float:
    cagr = float(row["cagr"])
    sortino = float(row["sortino"])
    mdd = float(row["mdd"])
    calmar = float(row["calmar"])
    min3 = float(row.get("min_3y_cagr", -1.0))
    min5 = float(row.get("min_5y_cagr", -1.0))
    corr = float(row.get("corr_to_t20d90", 1.0))
    dd_penalty = max(0.0, spec.mdd_floor - mdd)
    base = 2.0 * sortino + 4.0 * cagr + 1.5 * calmar + 1.0 * min5 + 0.5 * min3 - 8.0 * dd_penalty
    if spec.objective == "qqq_mdd_repair":
        return base - 20.0 * max(0.0, -0.75 - mdd)
    if spec.objective == "qqq_rolling_repair":
        return base + 3.0 * min3 + 4.0 * min5
    if spec.objective == "qqq_conservative_turbo":
        return base + 1.5 * mdd - 0.25 * float(row["tqqq_weight"]) - 0.5 * max(0.0, float(row["lrs_factor"]) - 1.0)
    if spec.objective == "qld_simplify":
        complexity_penalty = 0.15 * (float(row["tqqq_weight"]) > 0.5) + 0.15 * (float(row["lrs_factor"]) > 1.10)
        return base - complexity_penalty
    if spec.objective == "execution_robust":
        return base + 2.0 * float(row.get("worst_calmar", calmar)) + float(row.get("worst_min_5y_cagr", min5))
    if spec.objective == "diversity_search":
        return base + 1.5 * (1.0 - corr) - 6.0 * max(0.0, 0.55 - cagr)
    return base


def _label(g: Gene) -> str:
    return (
        f"{g.signal_asset}_s{g.sma_short}_{g.sma_long}_vw{g.vol_window}_vt{g.vol_threshold:.2f}_ar{g.ar_window}_"
        f"k{g.entry_k}_T{g.t_crash}D{g.d_arm}_w{g.tqqq_weight:.2f}_lrs{g.lrs_factor:.2f}_"
        f"g{g.gamma:.2f}_rv{g.ratevol_window}_{g.ratevol_threshold:.2f}"
    )


def _row_to_gene(row: dict) -> Gene:
    return Gene(
        str(row["signal_asset"]), int(row["sma_long"]), int(row["sma_short"]), int(row["vol_window"]),
        float(row["vol_threshold"]), int(row["ar_window"]), int(row["entry_k"]), int(row["t_crash"]),
        int(row["d_arm"]), float(row["tqqq_weight"]), float(row["lrs_factor"]), float(row["gamma"]),
        int(row["ratevol_window"]), float(row["ratevol_threshold"]),
    )


def _write_case_report(out_dir: Path, spec: EvolutionSpec, top: pd.DataFrame, history: pd.DataFrame, seed: int, minutes: float, elapsed_seconds: float) -> None:
    cols = [
        "label", "fitness", "sortino", "cagr", "sharpe", "mdd", "calmar", "end_mult",
        "min_3y_cagr", "min_5y_cagr", "corr_to_t20d90", "signal_asset", "sma_long", "sma_short",
        "vol_window", "vol_threshold", "ar_window", "entry_k", "t_crash", "d_arm", "tqqq_weight",
        "lrs_factor", "gamma", "ratevol_window", "ratevol_threshold",
    ]
    existing = [c for c in cols if c in top.columns]
    lines = [
        f"# {spec.name}",
        "",
        f"Description: {spec.description}",
        "",
        f"Seed: `{seed}`",
        f"Target runtime note minutes: `{minutes}`",
        f"Elapsed minutes: `{elapsed_seconds / 60.0:.2f}`",
        f"Generations completed: `{int(history['generation'].max())}`",
        f"Unique candidates evaluated: `{int(history['evaluated_unique'].max())}`",
        "",
        "## Best Candidate",
        "",
        top.head(1)[existing].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Top 20",
        "",
        top.head(20)[existing].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Best By Generation Tail",
        "",
        history.tail(20)[["generation", "evaluated_unique", "fitness", "sortino", "cagr", "mdd", "label"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Method Note",
        "",
        "This is GA discovery only. Any candidate requires fresh OOS/FWD/WF/bootstrap/PBO/DSR validation before claims `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.",
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
        "best_fitness": float(best["fitness"]),
        "best_sortino": float(best["sortino"]),
        "best_cagr": float(best["cagr"]),
        "best_mdd": float(best["mdd"]),
        "best_calmar": float(best["calmar"]),
    }


def _write_master_report(out_dir: Path, summaries: list[dict]) -> None:
    df = pd.DataFrame(summaries).drop_duplicates(subset=["name"], keep="last")
    if len(df) and "name" in df:
        df = df.sort_values("name")
    lines = [
        "# Repair GA Evolutions",
        "",
        "Status: sequential GA repair suite after the QLD-vs-QQQ signal audit.",
        "",
        "## Completed Evolutions",
        "",
        df.to_markdown(index=False, floatfmt=".4f") if len(df) else "No runs yet.",
        "",
        "## Interpretation Placeholder",
        "",
        "Read each subdirectory report before promoting any candidate. These are discovery runs only; PBO/DSR remain hard blockers `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.",
    ]
    (out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


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
