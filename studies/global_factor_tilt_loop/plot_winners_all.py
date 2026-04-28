"""Unified comparison chart: all Pareto-frontier winners vs VT and SPY.

Plots equity curves (log scale) for iters 005, 009, 013 alongside
VT buy-and-hold (VTSIM proxy) and SPY buy-and-hold on the same axes.

Note: iter 012 (Hybrid 50/50 net-of-tax) has no equity-curve data in
results.json (only aggregate metrics). Its numbers are annotated as a
text reference on the chart.

Outputs:
  studies/global_factor_tilt_loop/plots/winners_comparison_vt_real.png
  studies/global_factor_tilt_loop/plots/winners_comparison_ndx_real.png

Usage:
  uv run python studies/global_factor_tilt_loop/plot_winners_all.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
LOOP_DIR = Path(__file__).parent
ITER_ROOT = LOOP_DIR / "iterations"
OUT_DIR = LOOP_DIR / "plots"
TESTFOLIO_CACHE = REPO / "data/testfolio/cache/history.parquet"
SPY_PARQUET = REPO / "data/tiingo/daily/prices/SPY.parquet"

# Iterations to include (prefix → display label + color)
ITERS: list[tuple[str, str, str, str]] = [
    ("009", "HAA+Gold (iter009) — SHARPE FRONTIER", "#1f6feb", "solid"),
    ("013", "HAA+ZROZ (iter013) — CAGR FRONTIER",   "#d35400", "solid"),
    ("005", "HAA SmartStack (iter005)",               "#2ecc71", "dashed"),
]

# Hybrid 012 has no equity series — annotate as text
HYBRID_NOTE = (
    "iter012 Hybrid 50/50 net-tax: S=1.021 / CAGR=13.4% / MDD=26.9%\n"
    "(no equity curve — annual-DARF model; see iter014 for corrected numbers)"
)

DATASETS: dict[str, dict] = {
    "vt_real": {
        "vt_source": ("testfolio", "VTSIM"),
        "spy_source": ("tiingo", SPY_PARQUET),
    },
    "ndx_real": {
        "vt_source": ("testfolio", "VTSIM"),
        "spy_source": ("tiingo", SPY_PARQUET),
    },
}


# ---------------------------------------------------------------------------
# helpers (mirrors plot_helper.py — kept local so this script is standalone)
# ---------------------------------------------------------------------------

def _equity(r: pd.Series) -> pd.Series:
    return (1.0 + r).cumprod()


def _sharpe(r: pd.Series) -> float:
    sd = r.std()
    return float(np.sqrt(252) * r.mean() / sd) if sd > 0 else float("nan")


def _cagr(r: pd.Series) -> float:
    eq = _equity(r)
    years = len(r) / 252.0
    return float(eq.iloc[-1] ** (1.0 / years) - 1.0) if years > 0 else float("nan")


def _mdd(r: pd.Series) -> float:
    eq = _equity(r)
    return float((1.0 - eq / eq.cummax()).max())


def _rolling_sharpe(r: pd.Series, window: int = 252) -> pd.Series:
    mu = r.rolling(window).mean()
    sd = r.rolling(window).std()
    return np.sqrt(252.0) * mu / sd


# ---------------------------------------------------------------------------
# data loaders
# ---------------------------------------------------------------------------

def _load_testfolio_col(col: str) -> pd.Series:
    df = pd.read_parquet(TESTFOLIO_CACHE)
    df.index = pd.to_datetime(df.index)
    return df[col].astype(float).pct_change().dropna()


def _load_tiingo_returns(parquet: Path) -> pd.Series:
    df = pd.read_parquet(parquet)
    df.index = pd.to_datetime(df.index)
    col = "adj_close" if "adj_close" in df.columns else "close"
    return df[col].astype(float).pct_change().dropna()


def _find_iter_dir(prefix: str) -> Path:
    matches = sorted(ITER_ROOT.glob(f"{prefix}-*"))
    if not matches:
        raise FileNotFoundError(f"No iteration dir starting with {prefix}")
    return matches[0]


def _top_cfg(results: dict, ds: str) -> str:
    runs = results.get("runs", {}).get(ds, {})
    if not runs:
        cfgs = list(results.get("returns_series", {}).get(ds, {}).keys())
        return cfgs[0] if cfgs else ""
    top_id, _ = max(runs.items(), key=lambda kv: kv[1].get("sharpe", float("-inf")))
    return top_id


def _iter_returns(iter_prefix: str, ds: str) -> tuple[pd.Series, str] | None:
    """Return (daily_returns, cfg_id) or None if not available."""
    iter_dir = _find_iter_dir(iter_prefix)
    results = json.loads((iter_dir / "results.json").read_text())
    cfg_id = _top_cfg(results, ds)
    payload = results.get("returns_series", {}).get(ds, {}).get(cfg_id)
    if not payload:
        return None
    idx = pd.to_datetime(payload["index"])
    r = pd.Series(payload["net_returns"], index=idx)
    return r, cfg_id


# ---------------------------------------------------------------------------
# main plot function
# ---------------------------------------------------------------------------

def plot_dataset(ds: str, out_path: Path) -> None:
    cfg = DATASETS[ds]

    # --- load VT (VTSIM proxy) ---
    r_vt = _load_testfolio_col("VTSIM")

    # --- load SPY ---
    r_spy = _load_tiingo_returns(SPY_PARQUET)

    # --- load strategy series ---
    strategies: list[tuple[pd.Series, str, str, str]] = []
    for prefix, label, color, ls in ITERS:
        result = _iter_returns(prefix, ds)
        if result is None:
            print(f"  [{ds}] iter {prefix}: no returns_series, skipping")
            continue
        r_strat, cfg_id = result
        strategies.append((r_strat, label, color, ls))

    if not strategies:
        print(f"[{ds}] no strategies to plot, skipping")
        return

    # --- common date range: intersection of all series ---
    all_idx = strategies[0][0].index
    for r, *_ in strategies[1:]:
        all_idx = all_idx.intersection(r.index)
    start, end = str(all_idx[0].date()), str(all_idx[-1].date())
    r_vt  = r_vt.loc[start:end]
    r_spy = r_spy.loc[start:end]
    all_idx = all_idx.intersection(r_vt.index).intersection(r_spy.index)
    strategies = [(r.loc[all_idx], lbl, clr, ls) for r, lbl, clr, ls in strategies]
    r_vt  = r_vt.loc[all_idx]
    r_spy = r_spy.loc[all_idx]

    # --- build figure: 2 panels ---
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(14, 9),
        gridspec_kw={"height_ratios": [2.5, 1.0]},
        sharex=True,
    )

    # panel 1 — equity curves
    for r_s, lbl, clr, ls in strategies:
        eq = _equity(r_s)
        s, c, m = _sharpe(r_s), _cagr(r_s) * 100, _mdd(r_s) * 100
        full_label = f"{lbl}\nS={s:.3f} | CAGR={c:.1f}% | MDD={m:.1f}%"
        ax1.plot(eq.index, eq.values, color=clr, lw=2.0, ls=ls, label=full_label)

    # benchmarks
    for r_b, lbl_b, clr_b in [(r_vt, "VT b&h (VTSIM proxy)", "#888"),
                               (r_spy, "SPY b&h", "#333")]:
        eq_b = _equity(r_b)
        s_b, c_b, m_b = _sharpe(r_b), _cagr(r_b)*100, _mdd(r_b)*100
        full_lbl_b = f"{lbl_b}\nS={s_b:.3f} | CAGR={c_b:.1f}% | MDD={m_b:.1f}%"
        ax1.plot(eq_b.index, eq_b.values, color=clr_b, lw=1.4, ls="dotted",
                 label=full_lbl_b)

    ax1.set_yscale("log")
    ax1.set_ylabel("Equity (growth of $1, log scale)")
    ax1.grid(True, which="both", alpha=0.2)
    ax1.legend(loc="upper left", fontsize=8.5, framealpha=0.85)
    ax1.set_title(
        f"Global Factor-Tilt Loop — Winners vs Benchmarks — {ds}\n"
        f"window: {start} → {end}  |  {HYBRID_NOTE}",
        fontsize=9,
    )

    # panel 2 — rolling Sharpe differential vs SPY
    ax2.axhline(0, color="#888", lw=0.8)
    for r_s, lbl, clr, ls in strategies:
        diff = _rolling_sharpe(r_s) - _rolling_sharpe(r_spy)
        ax2.plot(diff.index, diff.values, color=clr, lw=1.2, ls=ls,
                 label=lbl.split(" (")[0].split(" —")[0])
        ax2.fill_between(diff.index, diff.values, 0,
                         where=(diff.values > 0), color=clr, alpha=0.12, interpolate=True)

    ax2.set_ylabel("Rolling 1y Sharpe Δ vs SPY")
    ax2.grid(True, alpha=0.2)
    ax2.legend(loc="upper left", fontsize=8)
    ax2.set_xlabel("Date")

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"  [{ds}] saved → {out_path}")


def main() -> None:
    print("=== plot_winners_all.py ===")
    for ds in DATASETS:
        out = OUT_DIR / f"winners_comparison_{ds}.png"
        print(f"[{ds}] plotting…")
        try:
            plot_dataset(ds, out)
        except Exception as exc:
            print(f"  [{ds}] ERROR: {exc}")
    print("Done.")


if __name__ == "__main__":
    main()
