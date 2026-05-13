"""Hybrid Stage 4 + canonical anchor combinations.

The goal is to test whether Stage 4 can act as a modern-regime turbo while
iter030/T3d-K2 remain the long-history defensive anchor. Meta-gates use only
lagged trailing relative performance, so the switch does not know future regimes
`[advances_fin_ml, p.31-34]`, `[leverage_for_the_long_run, p.5-7]`.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.core.data_loader import load_testfolio_series
from studies.technical_signal_vote_hunt.core import build_close_only_signals, daily_returns
from studies.technical_signal_vote_hunt.runners.compare_stage4_testfolio import (
    ITER030_CANONICAL,
    T3D_CANONICAL,
    _read_returns,
)
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import _metrics_row_np, _simulate_on_off_np
from studies.technical_signal_vote_hunt.runners.run_stage4_regime_bridge import DEFAULT_BASE_SIGNALS

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = REPO_ROOT / "studies/technical_signal_vote_hunt/reports/stage4_hybrid_combo"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Stage 4 hybrid combo tests")
    p.add_argument("--off-leg", choices=["ZROZSIM", "CASHX"], default="ZROZSIM")
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

    base_returns = _build_base_returns(args)
    hybrid_returns, switches = _build_hybrids(base_returns)
    returns = pd.concat([base_returns, hybrid_returns], axis=1).dropna()
    metrics = _metrics_table(returns)
    rolling = _rolling_table(returns)
    switches.to_csv(tables_dir / "hybrid_switch_stats.csv", index=False)
    metrics.to_csv(tables_dir / "metrics.csv")
    rolling.to_csv(tables_dir / "rolling_windows.csv", index=False)
    (1.0 + returns).cumprod().to_csv(tables_dir / "equity_curves.csv")
    _plot((1.0 + returns).cumprod(), plots_dir / "equity_curves.png")
    _write_report(metrics, rolling, switches, args, returns.index)
    _write_manifest(args, returns.index)
    print(f"wrote {args.out_dir / 'REPORT.md'}", flush=True)
    return 0


def _build_base_returns(args: argparse.Namespace) -> pd.DataFrame:
    qqq = load_testfolio_series("QQQSIM")
    signals = build_close_only_signals(qqq)
    names = [name for name in args.base_signals.split("|") if name]
    sig_df = pd.concat([signals[name] for name in names], axis=1)
    vote = ((sig_df.sum(axis=1) >= args.base_k) & (~sig_df.isna().any(axis=1))).to_numpy(dtype=bool)
    dates = sig_df.index
    off = daily_returns(load_testfolio_series(args.off_leg)).reindex(dates)
    qld = daily_returns(load_testfolio_series("QLDSIM")).reindex(dates)
    tqqq = daily_returns(load_testfolio_series("TQQQSIM")).reindex(dates)
    spy = daily_returns(load_testfolio_series("SPYSIM")).reindex(dates)
    qqq_ret = daily_returns(qqq).reindex(dates)
    return pd.concat(
        {
            "Stage4 QLD": pd.Series(_simulate_on_off_np(vote, qld.to_numpy(float), off.to_numpy(float)), index=dates),
            "Stage4 TQQQ": pd.Series(_simulate_on_off_np(vote, tqqq.to_numpy(float), off.to_numpy(float)), index=dates),
            "T3d-K2 canonical": _read_returns(T3D_CANONICAL).reindex(dates),
            "iter030 canonical": _read_returns(ITER030_CANONICAL).reindex(dates),
            "SPYSIM buy_hold": spy,
            "QQQSIM buy_hold": qqq_ret,
        },
        axis=1,
        sort=False,
    )


def _build_hybrids(base: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    hybrids: dict[str, pd.Series] = {}
    anchors = ["iter030 canonical", "T3d-K2 canonical"]
    turbos = ["Stage4 QLD", "Stage4 TQQQ"]
    windows = [252, 504, 756, 1260]
    thresholds = [0.00, 0.05, 0.10, 0.20]
    for anchor, turbo, window, threshold in itertools.product(anchors, turbos, windows, thresholds):
        rel = _trailing_cagr(base[turbo], window) - _trailing_cagr(base[anchor], window)
        use_turbo = (rel > threshold).shift(1).fillna(False)
        label = f"hybrid_{anchor.split()[0]}_{turbo.replace(' ', '')}_w{window}_thr{threshold:.2f}"
        hybrids[label] = pd.Series(np.where(use_turbo, base[turbo], base[anchor]), index=base.index)
        rows.append({
            "label": label,
            "anchor": anchor,
            "turbo": turbo,
            "window_days": window,
            "threshold": threshold,
            "turbo_exposure": float(use_turbo.mean()),
            "switches": int(use_turbo.astype(int).diff().abs().fillna(0).sum()),
        })
    return pd.DataFrame(hybrids), pd.DataFrame(rows)


def _trailing_cagr(returns: pd.Series, window: int) -> pd.Series:
    gross = (1.0 + returns.fillna(0.0)).rolling(window, min_periods=window).apply(np.prod, raw=True)
    years = window / 252.0
    return gross ** (1.0 / years) - 1.0


def _metrics_table(returns: pd.DataFrame) -> pd.DataFrame:
    dates = pd.DatetimeIndex(returns.index)
    bench = returns["SPYSIM buy_hold"].to_numpy(float)
    rows = []
    for name in returns.columns:
        rows.append(_metrics_row_np(returns[name].to_numpy(float), bench, dates, name, "QQQ", "mixed", 0, 0, "hybrid"))
    return pd.DataFrame(rows).set_index("label").sort_values(["sortino", "cagr"], ascending=[False, False])


def _rolling_table(returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    top_labels = list(_metrics_table(returns).head(20).index)
    for label in top_labels:
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
    keep = list(_metrics_table(equity.pct_change().fillna(0.0)).head(8).index)
    fig, ax = plt.subplots(figsize=(13, 7))
    equity[keep].plot(ax=ax, logy=True, linewidth=1.5)
    ax.set_title("Top Hybrid Equity Curves")
    ax.set_ylabel("Growth of $1")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _write_report(metrics: pd.DataFrame, rolling: pd.DataFrame, switches: pd.DataFrame, args: argparse.Namespace, index: pd.DatetimeIndex) -> None:
    top = metrics.head(20)
    switch_top = switches[switches["label"].isin(top.index)]
    lines = [
        "# Stage 4 Hybrid Combo",
        "",
        "Status: first strategy-of-strategies test combining canonical anchors with Stage 4 turbo legs.",
        "",
        f"Window: `{index.min().date()}` to `{index.max().date()}` ({len(index):,} bars)",
        f"Stage4 off-leg: `{args.off_leg}`",
        "Meta-gate: use Stage4 turbo when its lagged trailing CAGR exceeds the anchor by a threshold.",
        "",
        "## Top Metrics",
        "",
        top[["sortino", "cagr", "sharpe", "mdd", "calmar", "end_mult", "pct_above_benchmark"]].to_markdown(floatfmt=".4f"),
        "",
        "## Top Hybrid Switch Stats",
        "",
        switch_top.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Rolling Windows: Top 20",
        "",
        rolling.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Plot",
        "",
        "![Top hybrid equity curves](plots/equity_curves.png)",
        "",
        "## Method Notes",
        "",
        "- The meta-gate is lagged one day after trailing-CAGR computation; it does not know future regimes `[advances_fin_ml, p.31-34]`.",
        "- This is economic-first exploration, not a mandate pass.",
    ]
    (args.out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(args: argparse.Namespace, index: pd.DatetimeIndex) -> None:
    manifest = {
        "stage": "stage4_hybrid_combo",
        "start": str(index.min().date()),
        "end": str(index.max().date()),
        "off_leg": args.off_leg,
        "primary_citation": "[advances_fin_ml, p.31-34]",
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
