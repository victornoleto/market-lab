"""Test Stage 4 as an ON-leg turbo inside the iter030 architecture.

This keeps iter030's defensive shell (T3d-K2 ON/OFF, rate-vol OFF override,
rearm/LRS plumbing) and only changes the QLD->TQQQ upgrade gate inside ON days.
The aim is to see whether Stage 4 can improve the risk-on engine without giving
up iter030's long-history defense `[advances_fin_ml, p.31-34]`,
`[leverage_for_the_long_run, p.5-7]`.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.core.data_loader import load_testfolio_series
from studies.technical_signal_vote_hunt.core import build_close_only_signals
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import _metrics_row_np
from studies.technical_signal_vote_hunt.runners.run_stage4_regime_bridge import DEFAULT_BASE_SIGNALS

REPO_ROOT = Path(__file__).resolve().parents[3]
ITER030_DIR = REPO_ROOT / "studies/letf_rotation_hunt/runs/post_close/030-2026-05-10-tcrash-scan-lrs120-rearmonly"
ITER030_BACKTEST = ITER030_DIR / "backtest.py"
OUT_DIR = REPO_ROOT / "studies/technical_signal_vote_hunt/reports/stage4_inside_iter030"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Test Stage4 turbo gates inside iter030")
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
    iter030 = _load_module(ITER030_BACKTEST, "iter030_stage4_inside")
    returns, stats = _build_returns(iter030, args)
    returns = returns.dropna()
    metrics = _metrics_table(returns)
    rolling = _rolling_table(returns)
    metrics.to_csv(tables_dir / "metrics.csv")
    rolling.to_csv(tables_dir / "rolling_windows.csv", index=False)
    stats.to_csv(tables_dir / "variant_stats.csv", index=False)
    equity = (1.0 + returns).cumprod()
    equity.to_csv(tables_dir / "equity_curves.csv")
    _plot(equity, plots_dir / "equity_curves.png")
    _write_report(metrics, rolling, stats, args, returns.index)
    _write_manifest(args, returns.index)
    print(f"wrote {args.out_dir / 'REPORT.md'}", flush=True)
    return 0


def _load_module(file_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module from {file_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _build_returns(iter030, args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
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
    stage4 = _stage4_vote(qqq, args).reindex(on_signal.index).fillna(0.0)

    variants = {
        "iter030 canonical replica": rearm,
        "inside_stage4_only": stage4,
        "inside_rearm_or_stage4": ((rearm.reindex(stage4.index).fillna(0.0) == 1.0) | (stage4 == 1.0)).astype(float),
        "inside_rearm_and_stage4": ((rearm.reindex(stage4.index).fillna(0.0) == 1.0) & (stage4 == 1.0)).astype(float),
        "inside_rearm_then_stage4_confirm": ((rearm.reindex(stage4.index).fillna(0.0) == 1.0) | ((stage4 == 1.0) & (on_signal.reindex(stage4.index).fillna(0.0) == 1.0))).astype(float),
    }
    rows = []
    out: dict[str, pd.Series] = {
        "SPYSIM buy_hold": spy_ret,
        "QQQSIM buy_hold": qqq.pct_change().dropna(),
    }
    for label, upgrade in variants.items():
        on_leg = iter030.build_single_asset_on_leg(qld_returns=qld_ret, tqqq_returns=tqqq_ret, upgrade_gate=upgrade)
        on_leg_lrs = iter030.apply_unconditional_lrs_overlay(on_leg_returns=on_leg, on_signal=on_signal, lrs_factor=1.20)
        strat = iter030.build_mechanism_mix_strategy_returns(
            on_signal=on_signal,
            on_leg_returns=on_leg_lrs,
            off_returns=zroz_ret,
            alt_off_returns=cash_ret,
            ratevol_gate=ratevol,
            gamma=0.25,
            use_off_override=True,
            drop_on_signal_warmup=False,
        )
        out[label] = strat
        up_lag = upgrade.shift(1).reindex(strat.index).fillna(0.0)
        on_lag = on_signal.shift(1).reindex(strat.index).fillna(0.0)
        rows.append({
            "label": label,
            "upgrade_active_pct": float(((up_lag == 1.0) & (on_lag == 1.0)).mean()),
            "on_active_pct": float((on_lag == 1.0).mean()),
            "switches": int(up_lag.astype(int).diff().abs().fillna(0).sum()),
        })
    return pd.DataFrame(out), pd.DataFrame(rows)


def _stage4_vote(qqq: pd.Series, args: argparse.Namespace) -> pd.Series:
    sigs = build_close_only_signals(qqq)
    names = [name for name in args.base_signals.split("|") if name]
    df = pd.concat([sigs[name] for name in names], axis=1)
    vote = ((df.sum(axis=1) >= args.base_k) & (~df.isna().any(axis=1))).astype(float)
    return vote


def _metrics_table(returns: pd.DataFrame) -> pd.DataFrame:
    dates = pd.DatetimeIndex(returns.index)
    bench = returns["SPYSIM buy_hold"].to_numpy(float)
    rows = []
    for label in returns.columns:
        rows.append(_metrics_row_np(returns[label].to_numpy(float), bench, dates, label, "QQQ", "mixed", 0, 0, "inside_iter030"))
    return pd.DataFrame(rows).set_index("label").sort_values(["sortino", "cagr"], ascending=[False, False])


def _rolling_table(returns: pd.DataFrame) -> pd.DataFrame:
    labels = list(_metrics_table(returns).head(10).index)
    rows = []
    for label in labels:
        r = returns[label].dropna()
        for years in (3, 5, 10, 15):
            window = years * 252
            vals = []
            if len(r) >= window:
                for end in range(window, len(r) + 1, 21):
                    sub = r.iloc[end - window:end].to_numpy(float)
                    eq = np.cumprod(1.0 + sub)
                    vals.append(eq[-1] ** (1.0 / years) - 1.0)
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


def _plot(equity: pd.DataFrame, path: Path) -> None:
    keep = [c for c in equity.columns if c not in {"SPYSIM buy_hold", "QQQSIM buy_hold"}]
    fig, ax = plt.subplots(figsize=(13, 7))
    equity[keep].plot(ax=ax, logy=True, linewidth=1.6)
    ax.set_title("Stage4 Turbo Inside Iter030")
    ax.set_ylabel("Growth of $1")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _write_report(metrics: pd.DataFrame, rolling: pd.DataFrame, stats: pd.DataFrame, args: argparse.Namespace, index: pd.DatetimeIndex) -> None:
    lines = [
        "# Stage4 Turbo Inside Iter030",
        "",
        "Status: test of Stage4 as the QLD->TQQQ upgrade gate inside iter030's defensive shell.",
        "",
        f"Window: `{index.min().date()}` to `{index.max().date()}` ({len(index):,} bars)",
        f"Stage4 rule: `{args.base_signals}`, `k={args.base_k}`",
        "",
        "## Metrics",
        "",
        metrics[["sortino", "cagr", "sharpe", "mdd", "calmar", "end_mult", "pct_above_benchmark"]].to_markdown(floatfmt=".4f"),
        "",
        "## Upgrade Stats",
        "",
        stats.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Rolling Windows",
        "",
        rolling.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Plot",
        "",
        "![Equity curves](plots/equity_curves.png)",
        "",
        "## Method Notes",
        "",
        "- Iter030's ON/OFF, LRS1.20, rearm plumbing and rate-vol CASHX off override are preserved.",
        "- Variants only change the ON-leg upgrade gate that selects QLD versus TQQQ.",
        "- This is economic-first exploration, not a mandate pass.",
    ]
    (args.out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(args: argparse.Namespace, index: pd.DatetimeIndex) -> None:
    manifest = {
        "stage": "stage4_inside_iter030",
        "start": str(index.min().date()),
        "end": str(index.max().date()),
        "base_signals": args.base_signals,
        "base_k": args.base_k,
        "primary_citation": "[advances_fin_ml, p.31-34]",
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
