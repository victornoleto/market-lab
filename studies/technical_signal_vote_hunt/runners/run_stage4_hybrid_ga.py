"""Constrained GA for Stage4 turbo filters inside iter030.

The GA is deliberately narrow: it does not invent new base indicators. It only
searches a small meta-gate that decides when Stage4 may upgrade iter030's QLD
ON-leg toward TQQQ, plus the TQQQ blend weight and LRS factor. Fitness penalizes
any deterioration versus iter030 in Sortino or MDD `[advances_fin_ml, p.31-34]`.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.core.data_loader import load_testfolio_series
from studies.technical_signal_vote_hunt.core import build_close_only_signals, daily_returns, realized_vol, sma
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import _metrics_row_np
from studies.technical_signal_vote_hunt.runners.run_stage4_regime_bridge import DEFAULT_BASE_SIGNALS

REPO_ROOT = Path(__file__).resolve().parents[3]
ITER030_BACKTEST = REPO_ROOT / "studies/letf_rotation_hunt/runs/post_close/030-2026-05-10-tcrash-scan-lrs120-rearmonly/backtest.py"
OUT_DIR = REPO_ROOT / "studies/technical_signal_vote_hunt/reports/stage4_hybrid_ga"


@dataclass(frozen=True)
class Gene:
    include_rearm: bool
    require_stage4: bool
    use_trend: bool
    use_slope: bool
    use_dd: bool
    dd_threshold: float
    use_rv: bool
    rv_threshold: float
    use_high_strength: bool
    weight: float
    lrs_factor: float


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run constrained Stage4 hybrid GA")
    p.add_argument("--population", type=int, default=96)
    p.add_argument("--generations", type=int, default=60)
    p.add_argument("--elite", type=int, default=12)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--base-signals", default=DEFAULT_BASE_SIGNALS)
    p.add_argument("--base-k", type=int, default=3)
    p.add_argument("--out-dir", type=Path, default=OUT_DIR)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    tables_dir = args.out_dir / "tables"
    plots_dir = args.out_dir / "plots"
    tables_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    ctx = _prepare_context(_load_module(ITER030_BACKTEST, "iter030_hybrid_ga"), args)
    base_metrics = _evaluate(ctx, Gene(True, False, False, False, False, -0.2, False, 0.7, False, 1.0, 1.2), "iter030_baseline")
    population = [_random_gene(rng) for _ in range(args.population)]
    history = []
    seen: dict[Gene, dict] = {}
    for generation in range(1, args.generations + 1):
        scored = []
        for gene in population:
            if gene not in seen:
                row = _evaluate(ctx, gene, _gene_label(gene))
                row["fitness"] = _fitness(row, base_metrics)
                seen[gene] = row
            scored.append(seen[gene])
        scored_df = pd.DataFrame(scored).sort_values("fitness", ascending=False)
        best = scored_df.iloc[0].to_dict()
        best["generation"] = generation
        history.append(best)
        print(
            f"gen={generation:03d} fitness={best['fitness']:.4f} cagr={best['cagr']:.4f} "
            f"sortino={best['sortino']:.4f} mdd={best['mdd']:.4f} label={best['label']}",
            flush=True,
        )
        elites = [_row_to_gene(row) for row in scored_df.head(args.elite).to_dict("records")]
        next_population = elites[:]
        while len(next_population) < args.population:
            p1 = elites[int(rng.integers(0, len(elites)))]
            p2 = elites[int(rng.integers(0, len(elites)))]
            child = _mutate(_crossover(p1, p2, rng), rng)
            next_population.append(child)
        population = next_population

    all_rows = pd.DataFrame(seen.values()).sort_values("fitness", ascending=False)
    hist_df = pd.DataFrame(history)
    all_rows.to_csv(tables_dir / "all_candidates.csv", index=False)
    hist_df.to_csv(tables_dir / "best_by_generation.csv", index=False)
    top = all_rows.head(20).copy()
    top.to_csv(tables_dir / "top_candidates.csv", index=False)
    returns = pd.concat({"iter030_baseline": ctx.baseline_returns, **{row.label: _returns_for_gene(ctx, _row_to_gene(row._asdict())) for row in top.itertuples(index=False)}}, axis=1).dropna()
    (1.0 + returns).cumprod().to_csv(tables_dir / "top_equity_curves.csv")
    _plot((1.0 + returns).cumprod(), plots_dir / "top_equity_curves.png")
    _write_report(top, hist_df, base_metrics, args)
    _write_manifest(args, len(seen))
    print(f"wrote {args.out_dir / 'REPORT.md'} evaluated={len(seen):,}", flush=True)
    return 0


class Context:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def _load_module(file_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {file_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _prepare_context(iter030, args: argparse.Namespace) -> Context:
    qld = load_testfolio_series("QLDSIM")
    tqqq = load_testfolio_series("TQQQSIM")
    zroz = load_testfolio_series("ZROZSIM")
    cash = load_testfolio_series("CASHX")
    spy = load_testfolio_series("SPYSIM")
    qqq = load_testfolio_series("QQQSIM")
    qld_ret = qld.pct_change().dropna()
    tqqq_ret = tqqq.pct_change().dropna()
    zroz_ret = zroz.pct_change().dropna()
    cash_ret = cash.pct_change().dropna()
    spy_ret = spy.pct_change().dropna()
    on_signal = iter030.entry_signal_K2(qld, qld_ret)
    rearm = iter030.build_postcrash_rearm_gate_independent(on_signal=on_signal, t_crash=35, d_arm=60)
    ratevol = iter030.ratevol_regime_gate(zroz_ret, vol_window=60, pct_window=1260, threshold=0.70)
    primitives = _primitives(qqq, args)
    ctx = Context(
        iter030=iter030,
        qld_ret=qld_ret,
        tqqq_ret=tqqq_ret,
        zroz_ret=zroz_ret,
        cash_ret=cash_ret,
        spy_ret=spy_ret,
        on_signal=on_signal,
        rearm=rearm,
        ratevol=ratevol,
        primitives=primitives,
        baseline_returns=None,
    )
    baseline = Gene(True, False, False, False, False, -0.2, False, 0.7, False, 1.0, 1.2)
    ctx.baseline_returns = _returns_for_gene(ctx, baseline)
    return ctx


def _primitives(qqq: pd.Series, args: argparse.Namespace) -> dict[str, pd.Series]:
    sigs = build_close_only_signals(qqq)
    names = [name for name in args.base_signals.split("|") if name]
    df = pd.concat([sigs[name] for name in names], axis=1)
    stage4 = ((df.sum(axis=1) >= args.base_k) & (~df.isna().any(axis=1))).astype(float)
    px = qqq.astype(float)
    ret = daily_returns(px)
    rv_pct = realized_vol(ret, 21).rolling(1260, min_periods=252).rank(pct=True)
    sma200 = sma(px, 200)
    return {
        "stage4": stage4,
        "trend": (px > sma200).astype(float).where(sma200.notna()),
        "slope": (sma200.diff(21) > 0.0).astype(float).where(sma200.notna()),
        "dd252": px / px.rolling(252, min_periods=126).max() - 1.0,
        "rv_pct": rv_pct,
        "high_strength": ((sigs["roc120_gt_0"] == 1.0) & (sigs["rv21_pct_lt_70"] == 1.0) & (sigs["sma100_gt_sma250"] == 1.0)).astype(float),
    }


def _random_gene(rng: np.random.Generator) -> Gene:
    return Gene(
        include_rearm=bool(rng.integers(0, 2)),
        require_stage4=bool(rng.integers(0, 2)),
        use_trend=bool(rng.integers(0, 2)),
        use_slope=bool(rng.integers(0, 2)),
        use_dd=bool(rng.integers(0, 2)),
        dd_threshold=float(rng.choice([-0.10, -0.15, -0.20, -0.25, -0.30, -0.40])),
        use_rv=bool(rng.integers(0, 2)),
        rv_threshold=float(rng.choice([0.40, 0.50, 0.60, 0.70, 0.80, 0.90])),
        use_high_strength=bool(rng.integers(0, 2)),
        weight=float(rng.choice([0.0, 0.25, 0.50, 0.75, 1.0])),
        lrs_factor=float(rng.choice([1.00, 1.05, 1.10, 1.15, 1.20])),
    )


def _crossover(a: Gene, b: Gene, rng: np.random.Generator) -> Gene:
    vals = []
    for av, bv in zip(a.__dict__.values(), b.__dict__.values(), strict=True):
        vals.append(av if rng.random() < 0.5 else bv)
    return Gene(*vals)


def _mutate(g: Gene, rng: np.random.Generator) -> Gene:
    vals = list(g.__dict__.values())
    choices = [
        [False, True], [False, True], [False, True], [False, True], [False, True],
        [-0.10, -0.15, -0.20, -0.25, -0.30, -0.40], [False, True],
        [0.40, 0.50, 0.60, 0.70, 0.80, 0.90], [False, True],
        [0.0, 0.25, 0.50, 0.75, 1.0], [1.00, 1.05, 1.10, 1.15, 1.20],
    ]
    for i, opts in enumerate(choices):
        if rng.random() < 0.12:
            vals[i] = opts[int(rng.integers(0, len(opts)))]
    if not vals[0] and not vals[1]:
        vals[0] = True
    return Gene(*vals)


def _gate(ctx: Context, gene: Gene) -> pd.Series:
    parts = []
    if gene.require_stage4:
        parts.append(ctx.primitives["stage4"])
    if gene.use_trend:
        parts.append(ctx.primitives["trend"])
    if gene.use_slope:
        parts.append(ctx.primitives["slope"])
    if gene.use_dd:
        parts.append((ctx.primitives["dd252"] > gene.dd_threshold).astype(float).where(ctx.primitives["dd252"].notna()))
    if gene.use_rv:
        parts.append((ctx.primitives["rv_pct"] < gene.rv_threshold).astype(float).where(ctx.primitives["rv_pct"].notna()))
    if gene.use_high_strength:
        parts.append(ctx.primitives["high_strength"])
    if parts:
        combo = pd.concat(parts, axis=1, sort=False).fillna(0.0).all(axis=1).astype(float)
    else:
        combo = pd.Series(0.0, index=ctx.rearm.index)
    if gene.include_rearm:
        aligned = pd.concat({"r": ctx.rearm, "c": combo}, axis=1, sort=False).fillna(0.0)
        return ((aligned["r"] == 1.0) | (aligned["c"] == 1.0)).astype(float)
    return combo


def _returns_for_gene(ctx: Context, gene: Gene) -> pd.Series:
    gate = _gate(ctx, gene)
    up_lag = gate.shift(1)
    aligned = pd.concat({"q": ctx.qld_ret, "t": ctx.tqqq_ret, "u": up_lag}, axis=1, sort=False).dropna(subset=["q", "t"])
    turbo = (1.0 - gene.weight) * aligned["q"] + gene.weight * aligned["t"]
    on_leg = pd.Series(np.where(aligned["u"].fillna(0.0) == 1.0, turbo, aligned["q"]), index=aligned.index)
    on_leg_lrs = ctx.iter030.apply_unconditional_lrs_overlay(on_leg_returns=on_leg, on_signal=ctx.on_signal, lrs_factor=gene.lrs_factor)
    return ctx.iter030.build_mechanism_mix_strategy_returns(
        on_signal=ctx.on_signal,
        on_leg_returns=on_leg_lrs,
        off_returns=ctx.zroz_ret,
        alt_off_returns=ctx.cash_ret,
        ratevol_gate=ctx.ratevol,
        gamma=0.25,
        use_off_override=True,
        drop_on_signal_warmup=False,
    )


def _evaluate(ctx: Context, gene: Gene, label: str) -> dict:
    r = _returns_for_gene(ctx, gene)
    aligned = pd.concat({"r": r, "b": ctx.spy_ret}, axis=1, sort=False).dropna()
    row = _metrics_row_np(aligned["r"].to_numpy(float), aligned["b"].to_numpy(float), pd.DatetimeIndex(aligned.index), label, "QQQ", "hybrid_ga", 0, 0, "ga")
    row.update(gene.__dict__)
    return row


def _fitness(row: dict, base: dict) -> float:
    cagr_gain = float(row["cagr"] - base["cagr"])
    sortino_gap = float(row["sortino"] - base["sortino"])
    mdd_gap = float(row["mdd"] - base["mdd"])
    penalty = 0.0
    penalty += max(0.0, -sortino_gap) * 3.0
    penalty += max(0.0, -mdd_gap) * 2.0
    return cagr_gain * 4.0 + sortino_gap + mdd_gap - penalty


def _gene_label(g: Gene) -> str:
    flags = []
    if g.include_rearm: flags.append("rearm")
    if g.require_stage4: flags.append("s4")
    if g.use_trend: flags.append("trend")
    if g.use_slope: flags.append("slope")
    if g.use_dd: flags.append(f"dd{g.dd_threshold:.2f}")
    if g.use_rv: flags.append(f"rv{g.rv_threshold:.2f}")
    if g.use_high_strength: flags.append("hi")
    if not flags: flags.append("empty")
    return "ga_" + "_".join(flags) + f"_w{g.weight:.2f}_lrs{g.lrs_factor:.2f}"


def _row_to_gene(row: dict) -> Gene:
    return Gene(
        bool(row["include_rearm"]), bool(row["require_stage4"]), bool(row["use_trend"]), bool(row["use_slope"]),
        bool(row["use_dd"]), float(row["dd_threshold"]), bool(row["use_rv"]), float(row["rv_threshold"]),
        bool(row["use_high_strength"]), float(row["weight"]), float(row["lrs_factor"]),
    )


def _plot(equity: pd.DataFrame, path: Path) -> None:
    keep = list(equity.columns[:8])
    fig, ax = plt.subplots(figsize=(13, 7))
    equity[keep].plot(ax=ax, logy=True, linewidth=1.5)
    ax.set_title("Constrained Hybrid GA: Top Equity Curves")
    ax.set_ylabel("Growth of $1")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _write_report(top: pd.DataFrame, history: pd.DataFrame, base: dict, args: argparse.Namespace) -> None:
    strict = top[(top["cagr"] > base["cagr"]) & (top["sortino"] >= base["sortino"]) & (top["mdd"] >= base["mdd"])]
    lines = [
        "# Stage4 Constrained Hybrid GA",
        "",
        "Status: economic-first GA search for a turbo filter that improves iter030 without worsening Sortino/MDD.",
        "",
        f"Population: {args.population}",
        f"Generations: {args.generations}",
        f"Strict Pareto candidates in top 20: {len(strict)}",
        "",
        "## Iter030 Baseline",
        "",
        pd.DataFrame([base])[['label', 'sortino', 'cagr', 'sharpe', 'mdd', 'calmar', 'end_mult']].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Top Candidates",
        "",
        top[["label", "fitness", "sortino", "cagr", "sharpe", "mdd", "calmar", "end_mult", "include_rearm", "require_stage4", "use_trend", "use_slope", "use_dd", "dd_threshold", "use_rv", "rv_threshold", "use_high_strength", "weight", "lrs_factor"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Best By Generation",
        "",
        history.tail(20)[["generation", "fitness", "sortino", "cagr", "mdd", "label"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Plot",
        "",
        "![Top equity curves](plots/top_equity_curves.png)",
    ]
    (args.out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(args: argparse.Namespace, evaluated: int) -> None:
    manifest = {
        "stage": "stage4_hybrid_ga",
        "population": args.population,
        "generations": args.generations,
        "evaluated_unique": evaluated,
        "primary_citation": "[advances_fin_ml, p.31-34]",
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
