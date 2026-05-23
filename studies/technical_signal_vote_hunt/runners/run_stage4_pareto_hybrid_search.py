"""Search for Pareto hybrids between Stage4, T3d-K2 and iter030.

This is an economic-first search for a practical "best of both worlds" hybrid:
keep iter030's defensive shell, then apply partial or full TQQQ turbo only when a
Stage4-derived condition is true. The target is strict Pareto improvement versus
iter030 on CAGR, Sortino and MDD `[advances_fin_ml, p.31-34]`.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from market_lab.backtest.data.testfolio_loader import load_testfolio_series
from studies.technical_signal_vote_hunt.core import build_close_only_signals, daily_returns, realized_vol, sma
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import _metrics_row_np
from studies.technical_signal_vote_hunt.runners.run_stage4_regime_bridge import DEFAULT_BASE_SIGNALS

REPO_ROOT = Path(__file__).resolve().parents[3]
ITER030_BACKTEST = REPO_ROOT / "studies/letf_rotation_hunt/runs/post_close/030-2026-05-10-tcrash-scan-lrs120-rearmonly/backtest.py"
OUT_DIR = REPO_ROOT / "studies/technical_signal_vote_hunt/reports/stage4_pareto_hybrid_search"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Search Stage4/T3d/iter030 Pareto hybrids")
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
    iter030 = _load_module(ITER030_BACKTEST, "iter030_pareto_hybrid")
    context = _prepare_context(iter030, args)
    metrics, stats, returns = _search(context)
    metrics.to_csv(tables_dir / "metrics.csv", index=False)
    stats.to_csv(tables_dir / "variant_stats.csv", index=False)
    pareto = _pareto(metrics)
    pareto.to_csv(tables_dir / "pareto_candidates.csv", index=False)
    rolling = _rolling_table(returns, list(pareto.head(10)["label"]) + ["iter030 canonical"])
    rolling.to_csv(tables_dir / "rolling_windows.csv", index=False)
    _plot(returns, list(pareto.head(6)["label"]) + ["iter030 canonical"], plots_dir / "pareto_equity.png")
    _write_report(metrics, pareto, stats, rolling, args, context.dates)
    _write_manifest(args, context.dates, len(metrics), int(pareto["strict_pareto_vs_iter030"].sum()))
    strict_count = int(pareto["strict_pareto_vs_iter030"].sum())
    print(f"wrote {args.out_dir / 'REPORT.md'} candidates={len(metrics):,} strict_pareto={strict_count:,}", flush=True)
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
    gates = _turbo_gates(qqq, rearm, on_signal, args)
    dates = pd.DatetimeIndex(spy_ret.index)
    return Context(
        iter030=iter030,
        qld_ret=qld_ret,
        tqqq_ret=tqqq_ret,
        zroz_ret=zroz_ret,
        cash_ret=cash_ret,
        spy_ret=spy_ret,
        on_signal=on_signal,
        rearm=rearm,
        ratevol=ratevol,
        gates=gates,
        dates=dates,
    )


def _turbo_gates(qqq: pd.Series, rearm: pd.Series, on_signal: pd.Series, args: argparse.Namespace) -> dict[str, pd.Series]:
    sigs = build_close_only_signals(qqq)
    names = [name for name in args.base_signals.split("|") if name]
    df = pd.concat({name: sigs[name] for name in names}, axis=1)
    stage4 = ((df.sum(axis=1) >= args.base_k) & (~df.isna().any(axis=1))).astype(float)
    px = qqq.astype(float)
    ret = daily_returns(px)
    rv21 = realized_vol(ret, 21)
    rv_pct = rv21.rolling(1260, min_periods=252).rank(pct=True)
    dd252 = px / px.rolling(252, min_periods=126).max() - 1.0
    trend = (px > sma(px, 200)).astype(float).where(sma(px, 200).notna())
    high_strength = ((sigs["roc120_gt_0"] == 1.0) & (sigs["rv21_pct_lt_70"] == 1.0) & (sigs["sma100_gt_sma250"] == 1.0)).astype(float)
    gates = {
        "rearm": rearm,
        "stage4": stage4,
        "rearm_or_stage4": _or(rearm, stage4),
        "rearm_and_stage4": _and(rearm, stage4),
        "stage4_trend200": _and(stage4, trend),
        "stage4_dd252_gt_m20": _and(stage4, (dd252 > -0.20).astype(float).where(dd252.notna())),
        "stage4_dd252_gt_m30": _and(stage4, (dd252 > -0.30).astype(float).where(dd252.notna())),
        "stage4_rv_lt_70": _and(stage4, (rv_pct < 0.70).astype(float).where(rv_pct.notna())),
        "stage4_rv_lt_50": _and(stage4, (rv_pct < 0.50).astype(float).where(rv_pct.notna())),
        "stage4_high_strength": _and(stage4, high_strength),
        "rearm_or_stage4_trend200": _or(rearm, _and(stage4, trend)),
        "rearm_or_stage4_dd252_gt_m20": _or(rearm, _and(stage4, (dd252 > -0.20).astype(float).where(dd252.notna()))),
        "rearm_or_stage4_rv_lt_70": _or(rearm, _and(stage4, (rv_pct < 0.70).astype(float).where(rv_pct.notna()))),
        "rearm_or_stage4_high_strength": _or(rearm, _and(stage4, high_strength)),
        "on_and_stage4": _and(on_signal, stage4),
    }
    return gates


def _and(a: pd.Series, b: pd.Series) -> pd.Series:
    aligned = pd.concat({"a": a, "b": b}, axis=1)
    return ((aligned["a"].fillna(0.0) == 1.0) & (aligned["b"].fillna(0.0) == 1.0)).astype(float)


def _or(a: pd.Series, b: pd.Series) -> pd.Series:
    aligned = pd.concat({"a": a, "b": b}, axis=1)
    return ((aligned["a"].fillna(0.0) == 1.0) | (aligned["b"].fillna(0.0) == 1.0)).astype(float)


def _search(ctx: Context) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    stats = []
    returns: dict[str, pd.Series] = {"SPYSIM buy_hold": ctx.spy_ret}
    weights = [0.0, 0.25, 0.50, 0.75, 1.0]
    lrs_factors = [1.00, 1.10, 1.20]
    for gate_name, gate in ctx.gates.items():
        up_lag = gate.shift(1)
        for weight, lrs in itertools.product(weights, lrs_factors):
            label = f"gate_{gate_name}_w{weight:.2f}_lrs{lrs:.2f}"
            on_leg = _blend_on_leg(ctx.qld_ret, ctx.tqqq_ret, up_lag, weight)
            on_leg_lrs = ctx.iter030.apply_unconditional_lrs_overlay(on_leg_returns=on_leg, on_signal=ctx.on_signal, lrs_factor=lrs)
            strat = ctx.iter030.build_mechanism_mix_strategy_returns(
                on_signal=ctx.on_signal,
                on_leg_returns=on_leg_lrs,
                off_returns=ctx.zroz_ret,
                alt_off_returns=ctx.cash_ret,
                ratevol_gate=ctx.ratevol,
                gamma=0.25,
                use_off_override=True,
                drop_on_signal_warmup=False,
            )
            returns[label] = strat
            metric = _metric(label, strat, ctx.spy_ret)
            metric.update({"gate": gate_name, "weight": weight, "lrs_factor": lrs})
            rows.append(metric)
            on_lag = ctx.on_signal.shift(1).reindex(strat.index).fillna(0.0)
            up = gate.shift(1).reindex(strat.index).fillna(0.0)
            stats.append({
                "label": label,
                "gate": gate_name,
                "weight": weight,
                "lrs_factor": lrs,
                "upgrade_active_pct": float(((up == 1.0) & (on_lag == 1.0)).mean()),
                "switches": int(up.astype(int).diff().abs().fillna(0).sum()),
            })
    ret_df = pd.DataFrame(returns).dropna()
    metrics = pd.DataFrame(rows).sort_values(["sortino", "cagr"], ascending=[False, False])
    return metrics, pd.DataFrame(stats), ret_df


def _blend_on_leg(qld: pd.Series, tqqq: pd.Series, up_lag: pd.Series, weight: float) -> pd.Series:
    aligned = pd.concat({"q": qld, "t": tqqq, "u": up_lag}, axis=1, sort=False).dropna(subset=["q", "t"])
    up = aligned["u"].fillna(0.0) == 1.0
    turbo = (1.0 - weight) * aligned["q"] + weight * aligned["t"]
    return pd.Series(np.where(up, turbo, aligned["q"]), index=aligned.index)


def _metric(label: str, returns: pd.Series, spy: pd.Series) -> dict:
    aligned = pd.concat({"r": returns, "b": spy}, axis=1).dropna()
    row = _metrics_row_np(aligned["r"].to_numpy(float), aligned["b"].to_numpy(float), pd.DatetimeIndex(aligned.index), label, "QQQ", "hybrid", 0, 0, "pareto")
    return row


def _pareto(metrics: pd.DataFrame) -> pd.DataFrame:
    base = metrics.loc[metrics["label"] == "gate_rearm_w1.00_lrs1.20"].iloc[0]
    out = metrics.copy()
    out["beats_iter030_cagr"] = out["cagr"] > base["cagr"]
    out["beats_iter030_sortino"] = out["sortino"] >= base["sortino"]
    out["beats_iter030_mdd"] = out["mdd"] >= base["mdd"]
    out["strict_pareto_vs_iter030"] = out[["beats_iter030_cagr", "beats_iter030_sortino", "beats_iter030_mdd"]].all(axis=1)
    out["score"] = (out["cagr"] - base["cagr"]) * 3.0 + (out["sortino"] - base["sortino"]) + (out["mdd"] - base["mdd"])
    return out.sort_values(["strict_pareto_vs_iter030", "score", "sortino", "cagr"], ascending=[False, False, False, False])


def _rolling_table(returns: pd.DataFrame, labels: list[str]) -> pd.DataFrame:
    rows = []
    for label in dict.fromkeys(labels):
        if label not in returns:
            continue
        r = returns[label].dropna()
        for years in (3, 5, 10, 15):
            window = years * 252
            vals = []
            if len(r) >= window:
                for end in range(window, len(r) + 1, 21):
                    sub = r.iloc[end - window:end].to_numpy(float)
                    vals.append(np.cumprod(1.0 + sub)[-1] ** (1.0 / years) - 1.0)
            arr = np.asarray(vals, dtype=float)
            rows.append({
                "label": label,
                "window_years": years,
                "n_windows": int(len(arr)),
                "min_cagr": float(np.nanmin(arr)) if len(arr) else np.nan,
                "median_cagr": float(np.nanmedian(arr)) if len(arr) else np.nan,
                "pct_positive_cagr": float(np.nanmean(arr > 0.0)) if len(arr) else np.nan,
            })
    return pd.DataFrame(rows)


def _plot(returns: pd.DataFrame, labels: list[str], path: Path) -> None:
    labels = [label for label in dict.fromkeys(labels) if label in returns]
    equity = (1.0 + returns[labels]).cumprod()
    fig, ax = plt.subplots(figsize=(13, 7))
    equity.plot(ax=ax, logy=True, linewidth=1.5)
    ax.set_title("Pareto Hybrid Search: Top Candidates")
    ax.set_ylabel("Growth of $1")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _write_report(metrics: pd.DataFrame, pareto: pd.DataFrame, stats: pd.DataFrame, rolling: pd.DataFrame, args: argparse.Namespace, dates: pd.DatetimeIndex) -> None:
    top = pareto.head(25)
    top_stats = stats[stats["label"].isin(top["label"])]
    lines = [
        "# Stage4 Pareto Hybrid Search",
        "",
        "Status: economic-first search for a hybrid that beats iter030 on CAGR, Sortino and MDD.",
        "",
        f"Window: `{dates.min().date()}` to `{dates.max().date()}` ({len(dates):,} bars)",
        f"Candidates tested: {len(metrics):,}",
        f"Strict Pareto candidates vs iter030: {int(pareto['strict_pareto_vs_iter030'].sum())}",
        "",
        "## Top Candidates",
        "",
        top[["label", "gate", "weight", "lrs_factor", "strict_pareto_vs_iter030", "sortino", "cagr", "sharpe", "mdd", "calmar", "end_mult", "score"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Top Candidate Switch Stats",
        "",
        top_stats.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Rolling Windows",
        "",
        rolling.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Plot",
        "",
        "![Pareto equity](plots/pareto_equity.png)",
        "",
        "## Method Notes",
        "",
        "- The iter030 shell is preserved: ON/OFF signal, ZROZ/CASHX off-leg logic and optional LRS overlay.",
        "- Search only changes the TQQQ turbo gate, turbo blend weight and LRS factor.",
        "- This is economic-first exploration; it is not a mandate pass.",
    ]
    (args.out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(args: argparse.Namespace, dates: pd.DatetimeIndex, n_candidates: int, n_pareto: int) -> None:
    manifest = {
        "stage": "stage4_pareto_hybrid_search",
        "start": str(dates.min().date()),
        "end": str(dates.max().date()),
        "candidates": n_candidates,
        "strict_pareto_candidates": n_pareto,
        "base_signals": args.base_signals,
        "base_k": args.base_k,
        "primary_citation": "[advances_fin_ml, p.31-34]",
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
