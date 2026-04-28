"""Plot strategy vs SPY/VT/NDX benchmarks for the long-term portfolio loop.

Reads ``iterations/{iter}-*/results.json`` and expects
``results["returns_series"][dataset][cfg_id] = {"index": [...], "net_returns": [...]}``
(``gross_returns`` also tolerated).

Produces TWO files per dataset:

  1. ``plot_{dataset}.png`` — equity curves (strategy + SPY + VT + NDX,
     log-scale), with three sub-panels below: rolling 1-year Sharpe delta
     of the strategy vs each of the three benchmarks.
  2. ``plot_rolling_windows_{dataset}.png`` — one row of subplots, one per
     window size in [3, 5, 10, 15, 20, 30] years (windows that don't fit
     the dataset length are skipped). Each subplot shows the strategy and
     three-benchmark Sharpe ratios at that window size.

CLI:

    uv run python studies/long_term_portfolio/plot_helper.py --iter 011
    uv run python studies/long_term_portfolio/plot_helper.py --iter 011 --datasets lh_56y
    uv run python studies/long_term_portfolio/plot_helper.py --iter 011 --cfg my_cfg

Benchmark sources (per dataset):
  - lh_56y / educational: SPYSIM (1986+), VTSIM (1970+), QQQSIM (1986+) — testfolio cache
  - vt_real, ndx_real:    SPY/QQQ Tiingo daily, VTSIM testfolio proxy
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from studies.long_term_portfolio.rolling_windows import (
    DEFAULT_WINDOWS_YEARS,
    fits_in_history,
    rolling_outperformance_pct,
    rolling_sharpe_at_windows,
)

ITER_ROOT = Path(__file__).parent / "iterations"
TESTFOLIO_CACHE = REPO / "data/testfolio/cache/history.parquet"
TIINGO_DIR = REPO / "data/tiingo/daily/prices"


# (source_kind, label) — source_kind = "testfolio:<col>" or "tiingo:<file.parquet>"
BENCHMARK_SOURCES: dict[str, dict[str, tuple[str, str]]] = {
    "lh_56y": {
        "SPY": ("testfolio:SPYSIM", "SPY (SPYSIM 1986+)"),
        "VT":  ("testfolio:VTSIM",  "VT (VTSIM 1970+)"),
        "NDX": ("testfolio:QQQSIM", "NDX (QQQSIM 1986+)"),
    },
    "educational": {  # legacy alias for lh_56y
        "SPY": ("testfolio:SPYSIM", "SPY (SPYSIM 1986+)"),
        "VT":  ("testfolio:VTSIM",  "VT (VTSIM 1970+)"),
        "NDX": ("testfolio:QQQSIM", "NDX (QQQSIM 1986+)"),
    },
    "vt_real": {
        "SPY": ("tiingo:SPY.parquet", "SPY (Tiingo)"),
        "VT":  ("testfolio:VTSIM", "VT (VTSIM proxy until live)"),
        "NDX": ("tiingo:QQQ.parquet", "NDX (QQQ Tiingo)"),
    },
    "ndx_real": {
        "SPY": ("tiingo:SPY.parquet", "SPY (Tiingo)"),
        "VT":  ("testfolio:VTSIM", "VT (VTSIM proxy until live)"),
        "NDX": ("tiingo:QQQ.parquet", "NDX (QQQ Tiingo)"),
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_iter_dir(iter_prefix: str) -> Path:
    matches = sorted(ITER_ROOT.glob(f"{iter_prefix}-*"))
    if not matches:
        raise FileNotFoundError(f"No iteration dir starting with {iter_prefix}")
    return matches[0]


def _strategy_returns(results: dict, ds: str, cfg_id: str) -> pd.Series | None:
    payload = results.get("returns_series", {}).get(ds, {}).get(cfg_id)
    if not payload:
        return None
    idx = pd.to_datetime(payload["index"])
    # Prefer net_returns (tax-aware) when available; fall back to gross_returns.
    if "net_returns" in payload:
        return pd.Series(payload["net_returns"], index=idx)
    if "gross_returns" in payload:
        return pd.Series(payload["gross_returns"], index=idx)
    return None


def _bench_returns(source: str, start: str, end: str) -> pd.Series:
    """Load benchmark returns for the given source token within [start, end]."""
    kind, ref = source.split(":", 1)
    if kind == "testfolio":
        df = pd.read_parquet(TESTFOLIO_CACHE)
        df.index = pd.to_datetime(df.index)
        if ref not in df.columns:
            return pd.Series([], dtype=float)
        s = df[ref].loc[start:end].astype(float).pct_change().dropna()
    elif kind == "tiingo":
        path = TIINGO_DIR / ref
        if not path.exists():
            return pd.Series([], dtype=float)
        df = pd.read_parquet(path)
        df.index = pd.to_datetime(df.index)
        col = "adj_close" if "adj_close" in df.columns else "close"
        s = df[col].loc[start:end].astype(float).pct_change().dropna()
    else:
        raise ValueError(f"unknown benchmark source kind: {kind}")
    return s


def _equity(r: pd.Series) -> pd.Series:
    return (1.0 + r).cumprod()


def _stats(r: pd.Series) -> tuple[float, float, float]:
    """(Sharpe, CAGR, MDD) — annualised, all decimal."""
    if len(r) < 2:
        return float("nan"), float("nan"), float("nan")
    sd = r.std(ddof=0)
    sharpe = float(r.mean() / sd * np.sqrt(252)) if sd > 0 else float("nan")
    eq = _equity(r)
    years = len(r) / 252.0
    cagr = float(eq.iloc[-1] ** (1 / years) - 1) if years > 0 else float("nan")
    mdd = float((1.0 - eq / eq.cummax()).max())
    return sharpe, cagr, mdd


def _rolling_1y_sharpe(r: pd.Series) -> pd.Series:
    mu = r.rolling(252).mean()
    sd = r.rolling(252).std(ddof=0)
    return (mu / sd * np.sqrt(252.0)).dropna()


def _pick_top_cfg(results: dict, ds: str) -> str | None:
    runs = results.get("runs", {}).get(ds, {})
    if not isinstance(runs, dict) or not runs:
        return None
    top_id, _ = max(runs.items(), key=lambda kv: kv[1].get("sharpe", float("-inf")))
    return top_id


# ---------------------------------------------------------------------------
# Equity + 3-sub-panel rolling delta plot
# ---------------------------------------------------------------------------


_BENCH_COLOURS = {"SPY": "#5b6e7f", "VT": "#9b59b6", "NDX": "#16a085"}
_STRAT_COLOUR = "#1f6feb"
_AHEAD_COLOUR = "#d35400"
_BEHIND_COLOUR = "#1f6feb"


def plot_dataset(iter_dir: Path, ds: str, cfg_id: str) -> Path | None:
    results = json.loads((iter_dir / "results.json").read_text())
    r_strat = _strategy_returns(results, ds, cfg_id)
    if r_strat is None or len(r_strat) < 60:
        print(f"[{ds}] no usable returns series for cfg={cfg_id}, skip")
        return None

    start, end = str(r_strat.index[0].date()), str(r_strat.index[-1].date())
    sources = BENCHMARK_SOURCES.get(ds, {})
    bench_returns: dict[str, pd.Series] = {}
    for name, (source, _label) in sources.items():
        b = _bench_returns(source, start, end)
        if len(b) > 60:
            common = r_strat.index.intersection(b.index)
            if len(common) >= 60:
                bench_returns[name] = b.loc[common]

    if not bench_returns:
        print(f"[{ds}] no usable benchmarks, skip")
        return None

    # Restrict strategy to overlap with at least one benchmark (use tightest window across all).
    overlap = r_strat.index
    for b in bench_returns.values():
        overlap = overlap.union(b.index)
    r_strat_aligned = r_strat.loc[overlap.intersection(r_strat.index)]

    # Layout: top panel (equity), 3 panels below (one per benchmark).
    fig = plt.figure(figsize=(14, 10), constrained_layout=True)
    gs = fig.add_gridspec(2, 3, height_ratios=[2.4, 1.0])
    ax_eq = fig.add_subplot(gs[0, :])

    eq_strat = _equity(r_strat_aligned)
    ax_eq.plot(eq_strat.index, eq_strat.values, color=_STRAT_COLOUR, lw=1.9,
               label=f"Strategy ({cfg_id})", zorder=10)
    bench_stats: dict[str, tuple[float, float, float]] = {}
    for name in ("SPY", "VT", "NDX"):
        if name not in bench_returns:
            continue
        b = bench_returns[name]
        eq_b = _equity(b)
        ax_eq.plot(eq_b.index, eq_b.values, color=_BENCH_COLOURS[name], lw=1.3,
                   ls="--", label=sources[name][1], alpha=0.85)
        bench_stats[name] = _stats(b)

    ax_eq.set_yscale("log")
    ax_eq.set_ylabel("Equity (growth of $1, log)")
    ax_eq.grid(True, which="both", alpha=0.25)
    ax_eq.legend(loc="upper left", fontsize=9, framealpha=0.85)
    s_sharpe, s_cagr, s_mdd = _stats(r_strat_aligned)
    bench_summary = "  |  ".join(
        f"{n}: S={st[0]:.2f} CAGR={st[1]*100:.1f}% MDD={st[2]*100:.1f}%"
        for n, st in bench_stats.items()
    )
    ax_eq.set_title(
        f"{iter_dir.name} — {ds}  "
        f"({r_strat_aligned.index[0].year}-{r_strat_aligned.index[-1].year}, "
        f"{len(r_strat_aligned)/252:.1f}y)\n"
        f"strat: S={s_sharpe:.2f} CAGR={s_cagr*100:.1f}% MDD={s_mdd*100:.1f}%   "
        f"|   {bench_summary}",
        fontsize=10,
    )

    # Three sub-panels: rolling 1y Sharpe Δ vs each benchmark
    rolling_strat = _rolling_1y_sharpe(r_strat_aligned)
    for col, name in enumerate(("SPY", "VT", "NDX")):
        ax = fig.add_subplot(gs[1, col])
        if name not in bench_returns:
            ax.text(0.5, 0.5, f"{name}: no data", ha="center", va="center",
                    transform=ax.transAxes, color="#888")
            ax.axis("off")
            continue
        rolling_b = _rolling_1y_sharpe(bench_returns[name])
        common = rolling_strat.index.intersection(rolling_b.index)
        diff = rolling_strat.loc[common] - rolling_b.loc[common]
        ax.axhline(0, color="#888", lw=0.8)
        ax.plot(diff.index, diff.values, color=_AHEAD_COLOUR, lw=1.0)
        ax.fill_between(diff.index, diff.values, 0, where=diff.values > 0,
                        color=_AHEAD_COLOUR, alpha=0.30, interpolate=True)
        ax.fill_between(diff.index, diff.values, 0, where=diff.values <= 0,
                        color=_BEHIND_COLOUR, alpha=0.30, interpolate=True)
        ax.grid(True, alpha=0.25)
        ax.set_xlabel("")
        ax.set_title(f"Strat – {name}: rolling 1y Sharpe Δ", fontsize=9)
        if col == 0:
            ax.set_ylabel("ΔSharpe (1y)")

    out = iter_dir / f"plot_{ds}.png"
    fig.savefig(out, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# Rolling-windows comparison plot
# ---------------------------------------------------------------------------


def plot_rolling_windows(iter_dir: Path, ds: str, cfg_id: str) -> Path | None:
    """Render strategy vs benchmark Sharpe at each window size [3,5,10,15,20,30]y.

    Skips windows that don't fit the dataset length.
    """
    results = json.loads((iter_dir / "results.json").read_text())
    r_strat = _strategy_returns(results, ds, cfg_id)
    if r_strat is None or len(r_strat) < 252 * 3:
        return None

    start, end = str(r_strat.index[0].date()), str(r_strat.index[-1].date())
    sources = BENCHMARK_SOURCES.get(ds, {})
    bench_returns: dict[str, pd.Series] = {}
    for name, (source, _label) in sources.items():
        b = _bench_returns(source, start, end)
        if len(b) > 252:
            common = r_strat.index.intersection(b.index)
            if len(common) > 252:
                bench_returns[name] = b.loc[common]

    if not bench_returns:
        return None

    fitting_windows = fits_in_history(r_strat, DEFAULT_WINDOWS_YEARS)
    if not fitting_windows:
        return None

    # Grid: 2 rows × 3 cols (handles up to 6 windows). Empty slots stay blank.
    n = len(fitting_windows)
    n_cols = min(3, n)
    n_rows = (n + n_cols - 1) // n_cols
    fig, axes = plt.subplots(
        n_rows, n_cols, figsize=(5.0 * n_cols, 3.5 * n_rows),
        sharey=False, constrained_layout=True,
    )
    axes_flat = axes.flatten() if hasattr(axes, "flatten") else [axes]

    strat_rolls = rolling_sharpe_at_windows(r_strat, fitting_windows)
    bench_rolls = {n: rolling_sharpe_at_windows(b, fitting_windows) for n, b in bench_returns.items()}
    outperf = {n: rolling_outperformance_pct(r_strat, b, fitting_windows) for n, b in bench_returns.items()}

    for i, w in enumerate(fitting_windows):
        ax = axes_flat[i]
        s_series = strat_rolls[w]
        ax.plot(s_series.index, s_series.values, color=_STRAT_COLOUR, lw=1.7,
                label="Strategy", zorder=10)
        for name in ("SPY", "VT", "NDX"):
            if name not in bench_rolls:
                continue
            b_series = bench_rolls[name][w]
            ax.plot(b_series.index, b_series.values, color=_BENCH_COLOURS[name],
                    lw=1.1, ls="--", label=name, alpha=0.85)
        ax.axhline(0, color="#888", lw=0.6)
        ax.grid(True, alpha=0.25)
        footer = " | ".join(
            f"{name}: {outperf[name][w]['pct_strat_wins']*100:.0f}% wins (n={outperf[name][w]['n_windows']})"
            for name in ("SPY", "VT", "NDX") if name in outperf
        )
        ax.set_title(f"{w}y rolling Sharpe — {footer}", fontsize=9)
        ax.set_ylabel("Sharpe (ann.)" if i % n_cols == 0 else "")
        if i == 0:
            ax.legend(loc="lower left", fontsize=8, framealpha=0.85)

    # Hide empty axes if any
    for j in range(n, len(axes_flat)):
        axes_flat[j].axis("off")

    fig.suptitle(
        f"{iter_dir.name} — {ds} — rolling Sharpe at multiple windows "
        f"(% wins = strategy beats benchmark in that fraction of overlapping windows)",
        fontsize=10,
    )
    out = iter_dir / f"plot_rolling_windows_{ds}.png"
    fig.savefig(out, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# CLI / batch
# ---------------------------------------------------------------------------


def plot_iter(iter_prefix: str, cfg_id: str | None = None,
              datasets: list[str] | None = None) -> list[Path]:
    iter_dir = _find_iter_dir(iter_prefix)
    results = json.loads((iter_dir / "results.json").read_text())
    available = list(results.get("returns_series", {}).keys())
    targets = datasets or available
    outs: list[Path] = []
    for ds in targets:
        if ds not in BENCHMARK_SOURCES:
            print(f"[{ds}] no benchmark sources registered, skip")
            continue
        if ds not in results.get("returns_series", {}):
            print(f"[{ds}] not in returns_series, skip")
            continue
        target_cfg = cfg_id or _pick_top_cfg(results, ds)
        if target_cfg is None or target_cfg not in results["returns_series"][ds]:
            cfgs = list(results["returns_series"][ds].keys())
            target_cfg = cfgs[0] if cfgs else None
        if target_cfg is None:
            print(f"[{ds}] no cfg available, skip")
            continue
        p1 = plot_dataset(iter_dir, ds, target_cfg)
        if p1 is not None:
            print(f"[{ds}] wrote {p1.name}")
            outs.append(p1)
        p2 = plot_rolling_windows(iter_dir, ds, target_cfg)
        if p2 is not None:
            print(f"[{ds}] wrote {p2.name}")
            outs.append(p2)
    return outs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iter", required=True, help="iteration prefix (e.g. '011')")
    ap.add_argument("--cfg", default=None, help="config id; if omitted, auto-detect top per dataset")
    ap.add_argument("--datasets", nargs="*", default=None,
                    help="subset of datasets; default: all in returns_series")
    args = ap.parse_args()
    plot_iter(args.iter, args.cfg, args.datasets)


if __name__ == "__main__":
    main()
