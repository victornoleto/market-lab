"""GA over plausible T3d-K2 / iter030 parameters.

This searches the actual strategy family: vote-K entry parameters, rearm window,
rate-vol OFF override, TQQQ upgrade weight and LRS factor. It is economic-first
research and intentionally constrained to interpretable parameters from the
existing T3d/iter030 lineage `[leverage_for_the_long_run, p.5-7]`,
`[advances_fin_ml, p.31-34]`.
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

from market_lab.backtest.data.testfolio_loader import load_testfolio_series
from studies._shared.signals import ar1_coefficient, realized_vol_gate, sma_gate, vote_of_k
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import _metrics_row_np

REPO_ROOT = Path(__file__).resolve().parents[3]
ITER030_BACKTEST = REPO_ROOT / "studies/letf_rotation_hunt/runs/post_close/030-2026-05-10-tcrash-scan-lrs120-rearmonly/backtest.py"
OUT_DIR = REPO_ROOT / "studies/technical_signal_vote_hunt/reports/iter030_param_ga"


@dataclass(frozen=True)
class Gene:
    sma_long: int
    sma_short: int
    vol_window: int
    vol_threshold: float
    ar_window: int
    entry_k: int
    upgrade_mode: str
    t_crash: int
    d_arm: int
    tqqq_weight: float
    lrs_factor: float
    gamma: float
    ratevol_window: int
    ratevol_threshold: float


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run GA over iter030 parameter family")
    p.add_argument("--population", type=int, default=128)
    p.add_argument("--generations", type=int, default=60)
    p.add_argument("--elite", type=int, default=16)
    p.add_argument("--seed", type=int, default=43)
    p.add_argument("--out-dir", type=Path, default=OUT_DIR)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    tables_dir = args.out_dir / "tables"
    plots_dir = args.out_dir / "plots"
    tables_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    ctx = _prepare_context(_load_module(ITER030_BACKTEST, "iter030_param_ga"))
    baseline = _evaluate(ctx, _baseline_gene(), "iter030_baseline")
    population = [_random_gene(rng) for _ in range(args.population)]
    population[0] = _baseline_gene()
    seen: dict[Gene, dict] = {}
    history = []
    for gen in range(1, args.generations + 1):
        scored = []
        for gene in population:
            if gene not in seen:
                row = _evaluate(ctx, gene, _label(gene))
                row["fitness"] = _fitness(row, baseline)
                seen[gene] = row
            scored.append(seen[gene])
        df = pd.DataFrame(scored).sort_values("fitness", ascending=False)
        best = df.iloc[0].to_dict()
        best["generation"] = gen
        history.append(best)
        print(
            f"gen={gen:03d} fit={best['fitness']:.4f} cagr={best['cagr']:.4f} "
            f"sortino={best['sortino']:.4f} mdd={best['mdd']:.4f} {best['label']}",
            flush=True,
        )
        elites = [_row_to_gene(row) for row in df.head(args.elite).to_dict("records")]
        next_pop = elites[:]
        while len(next_pop) < args.population:
            a = elites[int(rng.integers(0, len(elites)))]
            b = elites[int(rng.integers(0, len(elites)))]
            next_pop.append(_mutate(_crossover(a, b, rng), rng))
        population = next_pop

    all_rows = pd.DataFrame(seen.values()).sort_values("fitness", ascending=False)
    hist = pd.DataFrame(history)
    all_rows.to_csv(tables_dir / "all_candidates.csv", index=False)
    hist.to_csv(tables_dir / "best_by_generation.csv", index=False)
    top = all_rows.head(30).copy()
    top.to_csv(tables_dir / "top_candidates.csv", index=False)
    returns = pd.concat({"iter030_baseline": ctx.baseline_returns, **{row.label: _returns_for_gene(ctx, _row_to_gene(row._asdict())) for row in top.head(8).itertuples(index=False)}}, axis=1).dropna()
    equity = (1.0 + returns).cumprod()
    equity.to_csv(tables_dir / "top_equity_curves.csv")
    _plot(equity, plots_dir / "top_equity_curves.png")
    _write_report(top, hist, baseline, args, len(seen))
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


def _prepare_context(iter030) -> Context:
    qld = load_testfolio_series("QLDSIM")
    tqqq = load_testfolio_series("TQQQSIM")
    zroz = load_testfolio_series("ZROZSIM")
    cash = load_testfolio_series("CASHX")
    spy = load_testfolio_series("SPYSIM")
    qld_ret = qld.pct_change().dropna()
    ctx = Context(
        iter030=iter030,
        qld=qld,
        qld_ret=qld_ret,
        tqqq_ret=tqqq.pct_change().dropna(),
        zroz_ret=zroz.pct_change().dropna(),
        cash_ret=cash.pct_change().dropna(),
        spy_ret=spy.pct_change().dropna(),
        baseline_returns=None,
    )
    ctx.baseline_returns = _returns_for_gene(ctx, _baseline_gene())
    return ctx


def _baseline_gene() -> Gene:
    return Gene(250, 100, 21, 0.40, 30, 2, "rearm", 35, 60, 1.0, 1.20, 0.25, 60, 0.70)


def _random_gene(rng: np.random.Generator) -> Gene:
    return Gene(
        sma_long=int(rng.choice([180, 200, 225, 250, 275, 300])),
        sma_short=int(rng.choice([50, 75, 100, 125, 150])),
        vol_window=int(rng.choice([10, 21, 42, 63])),
        vol_threshold=float(rng.choice([0.30, 0.35, 0.40, 0.45, 0.50, 0.60])),
        ar_window=int(rng.choice([20, 30, 40, 60])),
        entry_k=int(rng.choice([1, 2, 3, 4])),
        upgrade_mode=str(rng.choice(["none", "k4", "lowvol", "k4_and_lowvol", "k4_or_lowvol", "rearm", "rearm_or_k4", "rearm_or_lowvol"])),
        t_crash=int(rng.choice([20, 30, 35, 40, 45, 50, 60, 80])),
        d_arm=int(rng.choice([30, 45, 60, 90, 120, 150])),
        tqqq_weight=float(rng.choice([0.0, 0.25, 0.50, 0.75, 1.0])),
        lrs_factor=float(rng.choice([1.00, 1.05, 1.10, 1.15, 1.20, 1.25])),
        gamma=float(rng.choice([0.0, 0.10, 0.25, 0.40, 0.50])),
        ratevol_window=int(rng.choice([30, 60, 90, 120])),
        ratevol_threshold=float(rng.choice([0.60, 0.70, 0.80, 0.90])),
    )


def _crossover(a: Gene, b: Gene, rng: np.random.Generator) -> Gene:
    vals = [av if rng.random() < 0.5 else bv for av, bv in zip(a.__dict__.values(), b.__dict__.values(), strict=True)]
    return Gene(*vals)


def _mutate(g: Gene, rng: np.random.Generator) -> Gene:
    vals = list(g.__dict__.values())
    opts = [
        [180, 200, 225, 250, 275, 300], [50, 75, 100, 125, 150], [10, 21, 42, 63],
        [0.30, 0.35, 0.40, 0.45, 0.50, 0.60], [20, 30, 40, 60], [1, 2, 3, 4],
        ["none", "k4", "lowvol", "k4_and_lowvol", "k4_or_lowvol", "rearm", "rearm_or_k4", "rearm_or_lowvol"],
        [20, 30, 35, 40, 45, 50, 60, 80], [30, 45, 60, 90, 120, 150],
        [0.0, 0.25, 0.50, 0.75, 1.0], [1.00, 1.05, 1.10, 1.15, 1.20, 1.25],
        [0.0, 0.10, 0.25, 0.40, 0.50], [30, 60, 90, 120], [0.60, 0.70, 0.80, 0.90],
    ]
    for i, choices in enumerate(opts):
        if rng.random() < 0.10:
            vals[i] = choices[int(rng.integers(0, len(choices)))]
    if vals[1] >= vals[0]:
        vals[1] = 100
        vals[0] = 250
    return Gene(*vals)


def _entry_components(ctx: Context, gene: Gene) -> list[pd.Series]:
    s1 = sma_gate(ctx.qld, period=gene.sma_long)
    s2 = sma_gate(ctx.qld, period=gene.sma_short)
    s3 = realized_vol_gate(ctx.qld_ret, window=gene.vol_window, threshold=gene.vol_threshold)
    ar = ar1_coefficient(ctx.qld_ret, window=gene.ar_window)
    s4 = (ar > 0.0).astype(float)
    s4[ar.isna()] = np.nan
    return [s1, s2, s3, s4]


def _upgrade_gate(ctx: Context, gene: Gene, components: list[pd.Series], on_signal: pd.Series) -> pd.Series:
    k4 = vote_of_k(components, k=4)
    lowvol = _lowvol_gate(ctx.qld_ret)
    rearm = ctx.iter030.build_postcrash_rearm_gate_independent(on_signal=on_signal, t_crash=gene.t_crash, d_arm=gene.d_arm)
    if gene.upgrade_mode == "none":
        return pd.Series(0.0, index=on_signal.index)
    if gene.upgrade_mode == "k4":
        return k4
    if gene.upgrade_mode == "lowvol":
        return lowvol
    if gene.upgrade_mode == "k4_and_lowvol":
        return _and(k4, lowvol)
    if gene.upgrade_mode == "k4_or_lowvol":
        return _or(k4, lowvol)
    if gene.upgrade_mode == "rearm":
        return rearm
    if gene.upgrade_mode == "rearm_or_k4":
        return _or(rearm, k4)
    if gene.upgrade_mode == "rearm_or_lowvol":
        return _or(rearm, lowvol)
    raise ValueError(gene.upgrade_mode)


def _lowvol_gate(returns: pd.Series, vol_window: int = 21, pct_window: int = 1260, threshold: float = 0.25) -> pd.Series:
    sigma = returns.rolling(vol_window, min_periods=vol_window).std() * np.sqrt(252.0)
    pct = sigma.rolling(pct_window, min_periods=pct_window).rank(pct=True)
    out = (pct < threshold).astype(float)
    out[pct.isna()] = np.nan
    return out


def _and(a: pd.Series, b: pd.Series) -> pd.Series:
    df = pd.concat({"a": a, "b": b}, axis=1, sort=False)
    out = ((df["a"] == 1.0) & (df["b"] == 1.0)).astype(float)
    out[df.isna().any(axis=1)] = np.nan
    return out


def _or(a: pd.Series, b: pd.Series) -> pd.Series:
    df = pd.concat({"a": a, "b": b}, axis=1, sort=False)
    out = ((df["a"] == 1.0) | (df["b"] == 1.0)).astype(float)
    out[df.isna().any(axis=1)] = np.nan
    return out


def _returns_for_gene(ctx: Context, gene: Gene) -> pd.Series:
    components = _entry_components(ctx, gene)
    on_signal = vote_of_k(components, k=gene.entry_k)
    upgrade = _upgrade_gate(ctx, gene, components, on_signal)
    up_lag = upgrade.shift(1)
    aligned = pd.concat({"q": ctx.qld_ret, "t": ctx.tqqq_ret, "u": up_lag}, axis=1, sort=False).dropna(subset=["q", "t"])
    turbo = (1.0 - gene.tqqq_weight) * aligned["q"] + gene.tqqq_weight * aligned["t"]
    on_leg = pd.Series(np.where(aligned["u"].fillna(0.0) == 1.0, turbo, aligned["q"]), index=aligned.index)
    on_leg_lrs = ctx.iter030.apply_unconditional_lrs_overlay(on_leg_returns=on_leg, on_signal=on_signal, lrs_factor=gene.lrs_factor)
    ratevol = ctx.iter030.ratevol_regime_gate(ctx.zroz_ret, vol_window=gene.ratevol_window, pct_window=1260, threshold=gene.ratevol_threshold)
    return ctx.iter030.build_mechanism_mix_strategy_returns(
        on_signal=on_signal,
        on_leg_returns=on_leg_lrs,
        off_returns=ctx.zroz_ret,
        alt_off_returns=ctx.cash_ret,
        ratevol_gate=ratevol,
        gamma=gene.gamma,
        use_off_override=gene.gamma > 0.0,
        drop_on_signal_warmup=False,
    )


def _evaluate(ctx: Context, gene: Gene, label: str) -> dict:
    r = _returns_for_gene(ctx, gene)
    aligned = pd.concat({"r": r, "b": ctx.spy_ret}, axis=1, sort=False).dropna()
    row = _metrics_row_np(aligned["r"].to_numpy(float), aligned["b"].to_numpy(float), pd.DatetimeIndex(aligned.index), label, "QQQ", "iter030_param_ga", 0, 0, "ga")
    row.update(gene.__dict__)
    return row


def _fitness(row: dict, base: dict) -> float:
    cagr_gain = float(row["cagr"] - base["cagr"])
    sortino_gap = float(row["sortino"] - base["sortino"])
    mdd_gap = float(row["mdd"] - base["mdd"])
    return 5.0 * cagr_gain + sortino_gap + mdd_gap - 4.0 * max(0.0, -sortino_gap) - 3.0 * max(0.0, -mdd_gap)


def _label(g: Gene) -> str:
    return (
        f"ga_s{g.sma_short}_{g.sma_long}_vw{g.vol_window}_vt{g.vol_threshold:.2f}_ar{g.ar_window}_k{g.entry_k}_"
        f"{g.upgrade_mode}_T{g.t_crash}D{g.d_arm}_w{g.tqqq_weight:.2f}_lrs{g.lrs_factor:.2f}_"
        f"g{g.gamma:.2f}_rv{g.ratevol_window}_{g.ratevol_threshold:.2f}"
    )


def _row_to_gene(row: dict) -> Gene:
    return Gene(
        int(row["sma_long"]), int(row["sma_short"]), int(row["vol_window"]), float(row["vol_threshold"]),
        int(row["ar_window"]), int(row["entry_k"]), str(row["upgrade_mode"]), int(row["t_crash"]),
        int(row["d_arm"]), float(row["tqqq_weight"]), float(row["lrs_factor"]), float(row["gamma"]),
        int(row["ratevol_window"]), float(row["ratevol_threshold"]),
    )


def _plot(equity: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(13, 7))
    equity.plot(ax=ax, logy=True, linewidth=1.4)
    ax.set_title("Iter030 Parameter GA: Top Equity Curves")
    ax.set_ylabel("Growth of $1")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _write_report(top: pd.DataFrame, history: pd.DataFrame, base: dict, args: argparse.Namespace, evaluated: int) -> None:
    strict = top[(top["cagr"] > base["cagr"]) & (top["sortino"] >= base["sortino"]) & (top["mdd"] >= base["mdd"])]
    lines = [
        "# Iter030 Parameter GA",
        "",
        "Status: economic-first GA over plausible T3d-K2/iter030 parameters.",
        "",
        f"Population: {args.population}",
        f"Generations: {args.generations}",
        f"Unique evaluated: {evaluated:,}",
        f"Strict Pareto candidates in top 30: {len(strict)}",
        "",
        "## Baseline",
        "",
        pd.DataFrame([base])[["label", "sortino", "cagr", "sharpe", "mdd", "calmar", "end_mult"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Top Candidates",
        "",
        top[["label", "fitness", "sortino", "cagr", "sharpe", "mdd", "calmar", "end_mult", "sma_long", "sma_short", "vol_window", "vol_threshold", "ar_window", "entry_k", "upgrade_mode", "t_crash", "d_arm", "tqqq_weight", "lrs_factor", "gamma", "ratevol_window", "ratevol_threshold"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Best By Generation",
        "",
        history.tail(25)[["generation", "fitness", "sortino", "cagr", "mdd", "label"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Plot",
        "",
        "![Top equity curves](plots/top_equity_curves.png)",
        "",
        "## Method Notes",
        "",
        "- Entry vote parameters are constrained around the T3d-K2 lineage: SMA gates, realised-vol gate and AR(1) gate.",
        "- Rearm, rate-vol OFF override and LRS are constrained around iter030's documented mechanisms.",
        "- This is economic-first exploration, not a mandate pass.",
    ]
    (args.out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(args: argparse.Namespace, evaluated: int) -> None:
    manifest = {
        "stage": "iter030_param_ga",
        "population": args.population,
        "generations": args.generations,
        "evaluated_unique": evaluated,
        "primary_citation": "[leverage_for_the_long_run, p.5-7]",
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
