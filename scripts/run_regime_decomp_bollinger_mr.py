#!/usr/bin/env python3
"""Regime decomposition of Bollinger MR winners by year × VIX quintile.

For each ticker (SPY/XLK/XLE), bucket trades by:
  * Entry-date year (2021 .. 2026Q1 — last bucket combines 2025 + 2026Q1
    because Q1-2026 alone is too small for cell-level statistics).
  * Entry-date VIX-proxy quintile (Q1 calm → Q5 panic).

Reports per-cell win rate, mean return, and trade-level annualised Sharpe
(when n ≥ 5; otherwise marked low-n).

VIX is not in Tiingo — we use **VIXY** (1x VIX short-term futures ETF)
as proxy. Daily VIXY close ranks days by volatility level, which is
what regime bucketing needs (absolute level matters less than ordinal).

Citations:
- `[advances_fin_ml, p.215-219, ch.13]` — backtest stress under regime
  partitioning; the same edge can flip sign across regimes.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ai_trade.backtest.data.tiingo_source import TiingoSource
from ai_trade.backtest.data.tiingo_storage import TiingoStorage


YEAR_BUCKETS = [
    ("2021", date(2021, 1, 1), date(2021, 12, 31)),
    ("2022", date(2022, 1, 1), date(2022, 12, 31)),
    ("2023", date(2023, 1, 1), date(2023, 12, 31)),
    ("2024", date(2024, 1, 1), date(2024, 12, 31)),
    ("2025+26Q1", date(2025, 1, 1), date(2026, 4, 15)),
]


def load_vixy(start: date, end: date, storage_root: Path) -> pd.Series:
    src = TiingoSource(storage=TiingoStorage(root=storage_root))
    df = src.fetch("VIXY", start, end, asset_class="etf", frequency="daily")
    if df.empty:
        raise RuntimeError("Could not fetch VIXY proxy data")
    df.index = pd.to_datetime(df.index).normalize()
    return df["close"]


def attach_vix_quintiles(
    trades: pd.DataFrame, vixy: pd.Series, n_quintiles: int = 5,
) -> pd.DataFrame:
    """Add 'vixy_close' and 'vix_quintile' (1..5) per trade based on entry date."""
    trades = trades.copy()
    trades["entry_time"] = pd.to_datetime(trades["entry_time"])
    trades["entry_date"] = trades["entry_time"].dt.normalize()
    # Quintile thresholds computed once across the full VIXY series so all
    # tickers share the same regime calibration.
    quintile_edges = np.percentile(
        vixy.values, np.linspace(0, 100, n_quintiles + 1),
    )
    # Inclusive last edge to capture the max value.
    quintile_edges[-1] = quintile_edges[-1] + 1e-9
    quintile_edges[0] = quintile_edges[0] - 1e-9

    aligned = trades.merge(
        vixy.rename("vixy_close"),
        how="left", left_on="entry_date", right_index=True,
    )
    # If entry is on a holiday/weekend (rare), backfill from prev trading day.
    aligned["vixy_close"] = aligned["vixy_close"].ffill()
    quintiles = pd.cut(
        aligned["vixy_close"], bins=quintile_edges,
        labels=list(range(1, n_quintiles + 1)), include_lowest=True,
    )
    aligned["vix_quintile"] = quintiles.astype("Int64")
    return aligned, quintile_edges


def compute_trade_returns(df: pd.DataFrame) -> pd.Series:
    side = df["side"].astype(str).str.lower()
    pr = (df["exit_price"] - df["entry_price"]) / df["entry_price"]
    pr = pr.where(side == "long", -pr)
    return pr


def cell_metrics(rets: pd.Series, min_n_for_sharpe: int = 5) -> dict:
    n = len(rets)
    if n == 0:
        return {"n": 0, "wr": np.nan, "mean_ret": np.nan, "sharpe": np.nan}
    wins = (rets > 0).sum()
    wr = wins / n
    mean_ret = float(rets.mean())
    if n < min_n_for_sharpe or rets.std() == 0:
        sharpe = np.nan
    else:
        # Trade-level annualised Sharpe; annualise by avg trade rate per year
        # in this cell (use 50 tpy as a rough constant — cells too small to
        # estimate own rate reliably). Comparison is valid across cells/tickers.
        sharpe = float(rets.mean() / rets.std() * np.sqrt(50))
    return {
        "n": int(n),
        "wr": round(float(wr), 4),
        "mean_ret": round(mean_ret, 6),
        "sharpe": round(float(sharpe), 4) if not np.isnan(sharpe) else None,
    }


def build_grid(trades_with_q: pd.DataFrame, returns: pd.Series, n_quintiles: int = 5) -> dict:
    """Build year×quintile grid of cell metrics."""
    grid: dict[str, dict[str, dict]] = {}
    for year_label, ystart, yend in YEAR_BUCKETS:
        grid[year_label] = {}
        year_mask = (
            (trades_with_q["entry_date"] >= pd.Timestamp(ystart))
            & (trades_with_q["entry_date"] <= pd.Timestamp(yend))
        )
        for q in range(1, n_quintiles + 1):
            mask = year_mask & (trades_with_q["vix_quintile"] == q)
            grid[year_label][f"Q{q}"] = cell_metrics(returns[mask])
    return grid


def plot_heatmap(grid: dict, ticker: str, out_path: Path, n_quintiles: int = 5) -> None:
    years = list(grid.keys())
    cols = [f"Q{q}" for q in range(1, n_quintiles + 1)]
    sharpe_grid = np.full((len(years), n_quintiles), np.nan)
    n_grid = np.zeros((len(years), n_quintiles), dtype=int)
    for i, y in enumerate(years):
        for j, q in enumerate(cols):
            cell = grid[y][q]
            if cell["sharpe"] is not None:
                sharpe_grid[i, j] = cell["sharpe"]
            n_grid[i, j] = cell["n"]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    vmax = np.nanmax(np.abs(sharpe_grid)) if not np.isnan(sharpe_grid).all() else 1.0
    im = ax.imshow(sharpe_grid, vmin=-vmax, vmax=vmax, cmap="RdBu_r", aspect="auto")
    ax.set_xticks(range(n_quintiles))
    ax.set_yticks(range(len(years)))
    ax.set_xticklabels([f"Q{q}\n{['calm','low','mid','high','panic'][q-1]}" for q in range(1, n_quintiles + 1)])
    ax.set_yticklabels(years)
    for i in range(len(years)):
        for j in range(n_quintiles):
            n = n_grid[i, j]
            sh = sharpe_grid[i, j]
            if np.isnan(sh):
                txt = f"n={n}"
                color = "gray"
            else:
                txt = f"{sh:.2f}\nn={n}"
                color = "white" if abs(sh) > 0.5 * vmax else "black"
            ax.text(j, i, txt, ha="center", va="center", color=color, fontsize=8)
    ax.set_xlabel("VIXY Quintile (regime)")
    ax.set_ylabel("Year")
    ax.set_title(f"{ticker} Bollinger MR — per-cell Sharpe (n≥5)")
    fig.colorbar(im, ax=ax, label="Trade-level Sharpe (×√50 annualisation)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Regime decomposition for Bollinger MR winners")
    ap.add_argument("--trades-dir", type=Path, default=Path("reports/bollinger_mr_trades"))
    ap.add_argument("--symbols", nargs="+", default=["SPY", "XLK", "XLE"])
    ap.add_argument("--oos-start", default="2025-01-01")
    ap.add_argument("--oos-end", default="2026-04-15")
    ap.add_argument("--storage-root", type=Path, default=Path("data/tiingo"))
    ap.add_argument("--out-dir", type=Path, default=Path("reports/bollinger_mr_regime_decomp"))
    args = ap.parse_args(argv)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "assets").mkdir(parents=True, exist_ok=True)

    print("Fetching VIXY (VIX proxy) 2021-01-01 → 2026-04-15...")
    vixy = load_vixy(date(2021, 1, 1), date(2026, 4, 15), args.storage_root)
    print(f"VIXY: {len(vixy)} daily bars, range [{vixy.min():.2f}, {vixy.max():.2f}], median={vixy.median():.2f}")

    all_grids = {}
    quintile_edges_global = None
    for sym in args.symbols:
        csv = args.trades_dir / f"{sym}_{args.oos_start}_{args.oos_end}.csv"
        df = pd.read_csv(csv)
        with_q, edges = attach_vix_quintiles(df, vixy, n_quintiles=5)
        if quintile_edges_global is None:
            quintile_edges_global = edges
        rets = compute_trade_returns(with_q)
        grid = build_grid(with_q, rets, n_quintiles=5)
        all_grids[sym] = grid
        plot_heatmap(grid, sym, args.out_dir / f"assets/heatmap_year_x_vix_{sym.lower()}.png")

        # Quintile-only summary (collapse years).
        print(f"\n=== {sym} — by VIX quintile (all years) ===")
        for q in range(1, 6):
            mask = with_q["vix_quintile"] == q
            cell = cell_metrics(rets[mask])
            sh = "n/a (low n)" if cell["sharpe"] is None else f"Sharpe={cell['sharpe']:+.3f}"
            print(f"  Q{q} (VIXY {edges[q-1]:.1f}-{edges[q]:.1f}): "
                  f"n={cell['n']}, WR={cell['wr']*100:.1f}%, mean_ret={cell['mean_ret']*100:+.3f}%, {sh}")

    # ---- Persist JSON ----
    out_json = args.out_dir / "regime_decomp.json"
    out_json.write_text(json.dumps({
        "quintile_edges_vixy": [float(x) for x in quintile_edges_global],
        "year_buckets": [yb[0] for yb in YEAR_BUCKETS],
        "tickers": all_grids,
    }, indent=2))
    print(f"\n✓ Wrote {out_json}")

    # ---- Markdown summary ----
    lines = [
        "# Bollinger MR — Regime Decomposition (Year × VIX Quintile)",
        "",
        "Per-cell trade-level annualised Sharpe (×√50 trades/year average) for "
        "each ticker × year × VIXY quintile. Cells with n<5 trades show only "
        "the count (Sharpe undefined).",
        "",
        "VIX proxy: **VIXY** (1x VIX short-term futures ETF). VIX index itself "
        "isn't in Tiingo's coverage — VIXY's daily close ranks days by vol regime "
        "consistently with VIX (correlation ≈ 0.9).",
        "",
        "## Quintile thresholds (VIXY close)",
        "",
        "| Quintile | Range | Regime label |",
        "|---|---|---|",
        f"| Q1 | {quintile_edges_global[0]:.2f} – {quintile_edges_global[1]:.2f} | calm |",
        f"| Q2 | {quintile_edges_global[1]:.2f} – {quintile_edges_global[2]:.2f} | low |",
        f"| Q3 | {quintile_edges_global[2]:.2f} – {quintile_edges_global[3]:.2f} | mid |",
        f"| Q4 | {quintile_edges_global[3]:.2f} – {quintile_edges_global[4]:.2f} | high |",
        f"| Q5 | {quintile_edges_global[4]:.2f} – {quintile_edges_global[5]:.2f} | panic |",
        "",
        "## Per-ticker per-quintile (collapsed across years)",
        "",
    ]

    for sym in args.symbols:
        lines.append(f"### {sym}")
        lines.append("")
        lines.append("| Quintile | n | WR | mean ret | Sharpe |")
        lines.append("|---|---|---|---|---|")
        # Reload trades for the table (small cost, keeps script readable).
        df = pd.read_csv(args.trades_dir / f"{sym}_{args.oos_start}_{args.oos_end}.csv")
        with_q, _ = attach_vix_quintiles(df, vixy)
        rets = compute_trade_returns(with_q)
        for q in range(1, 6):
            mask = with_q["vix_quintile"] == q
            cell = cell_metrics(rets[mask])
            sh = "n/a" if cell["sharpe"] is None else f"{cell['sharpe']:+.3f}"
            wr_str = f"{cell['wr']*100:.1f}%" if cell["n"] > 0 else "—"
            mr_str = f"{cell['mean_ret']*100:+.3f}%" if cell["n"] > 0 else "—"
            lines.append(f"| Q{q} | {cell['n']} | {wr_str} | {mr_str} | {sh} |")
        lines.append("")
        lines.append(f"![{sym} heatmap](assets/heatmap_year_x_vix_{sym.lower()}.png)")
        lines.append("")

    lines += [
        "## Verdict cues",
        "",
        "- Any quintile with Sharpe < 0 (and n ≥ 5) ⇒ regime where strategy actively",
        "  loses; informs a live pause-trigger threshold.",
        "- 2022 was a deep bear (S&P -19% peak-to-trough). If 2022 row stays positive,",
        "  the edge is regime-robust on the realised distribution.",
        "- Q5 (panic) is where mean-reversion strategies typically thrive (overshoot)",
        "  but also where slippage is worst — paper Sharpe ≠ live Sharpe in Q5.",
        "",
        "## Citation",
        "",
        "- `[advances_fin_ml, p.215-219, ch.13]` — regime stress for backtests.",
    ]
    summary_path = args.out_dir / "summary.md"
    summary_path.write_text("\n".join(lines))
    print(f"✓ Wrote {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
