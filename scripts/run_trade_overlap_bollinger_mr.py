#!/usr/bin/env python3
"""Cross-asset trade overlap for Bollinger MR winners (SPY/XLK/XLE).

Are the 3 winners independent edges, or correlated facets of the same
underlying signal? If their entries cluster on the same bars and their
daily PnL correlates >0.7, "3 winners" is really 1 edge × 3 assets and
portfolio diversification is illusory.

Reads `reports/bollinger_mr_trades/<SYM>_<oos_start>_<oos_end>.csv`
emitted by `scripts/run_oos_bollinger_mr.py --emit-trades` and computes:

- Jaccard similarity of entry bars (1h granularity).
- Pearson correlation of daily PnL.
- Equal-weight portfolio Sharpe vs mean-of-3 (the diversification lift).
- Effective N via participation ratio of correlation-matrix eigenvalues
  (Shannon-style metric; lower than 3 means correlated assets).

Citation: `[advances_fin_ml, p.40-44, ch.3]` for purged correlation /
information-coefficient discipline (relevant when interpreting low N_eff
on overlapping signals).
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def trade_returns(df: pd.DataFrame) -> pd.Series:
    """Per-trade price return: (exit-entry)/entry, signed by side."""
    side = df["side"].astype(str).str.lower()
    pr = (df["exit_price"] - df["entry_price"]) / df["entry_price"]
    pr = pr.where(side == "long", -pr)
    pr.index = pd.to_datetime(df["exit_time"])
    return pr


def daily_pnl(df: pd.DataFrame) -> pd.Series:
    """Aggregate per-trade PnL by exit date (bar-day)."""
    sub = df.copy()
    sub["exit_time"] = pd.to_datetime(sub["exit_time"])
    sub["exit_date"] = sub["exit_time"].dt.normalize()
    return sub.groupby("exit_date")["pnl"].sum()


def jaccard_pair(a: set, b: set) -> float:
    union = len(a | b)
    return len(a & b) / union if union else 0.0


def effective_n_participation_ratio(corr: np.ndarray) -> float:
    """Participation ratio of eigenvalues — a Shannon-style measure of
    independence. PR = (sum λ)^2 / sum(λ^2) ∈ [1, N]. PR=N means perfectly
    diagonal (independent); PR=1 means rank-1 (single common factor).
    """
    eig = np.linalg.eigvalsh(corr)
    eig = np.clip(eig, 0, None)
    s1 = eig.sum()
    s2 = (eig ** 2).sum()
    return float((s1 ** 2) / s2) if s2 > 0 else 0.0


def annualised_sharpe(daily_pnl_series: pd.Series, periods_per_year: int = 252) -> float:
    if len(daily_pnl_series) < 2 or daily_pnl_series.std() == 0:
        return 0.0
    return float(daily_pnl_series.mean() / daily_pnl_series.std() * np.sqrt(periods_per_year))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Cross-asset overlap of Bollinger MR winner trades")
    ap.add_argument("--trades-dir", type=Path, default=Path("reports/bollinger_mr_trades"))
    ap.add_argument("--symbols", nargs="+", default=["SPY", "XLK", "XLE"])
    ap.add_argument("--oos-start", default="2025-01-01")
    ap.add_argument("--oos-end", default="2026-04-15")
    ap.add_argument("--out-dir", type=Path, default=Path("reports/bollinger_mr_overlap"))
    args = ap.parse_args(argv)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "assets").mkdir(parents=True, exist_ok=True)

    by_sym = {}
    for sym in args.symbols:
        csv = args.trades_dir / f"{sym}_{args.oos_start}_{args.oos_end}.csv"
        if not csv.exists():
            print(f"ERROR: missing {csv}", file=sys.stderr)
            return 1
        df = pd.read_csv(csv)
        oos = df[df["period"] == "oos"].copy()
        if oos.empty:
            print(f"ERROR: no OOS trades for {sym}", file=sys.stderr)
            return 1
        oos["entry_time"] = pd.to_datetime(oos["entry_time"])
        oos["exit_time"] = pd.to_datetime(oos["exit_time"])
        by_sym[sym] = oos

    # ---- Jaccard of entry bars (1h granularity) ----
    entry_sets = {
        sym: set(df["entry_time"].dt.floor("1h").tolist())
        for sym, df in by_sym.items()
    }
    jaccard = {
        f"{a}-{b}": jaccard_pair(entry_sets[a], entry_sets[b])
        for a, b in combinations(args.symbols, 2)
    }

    # ---- Daily PnL correlation matrix ----
    daily = pd.DataFrame({sym: daily_pnl(df) for sym, df in by_sym.items()})
    daily = daily.fillna(0.0).sort_index()
    corr = daily.corr().to_numpy()
    corr_df = pd.DataFrame(corr, index=args.symbols, columns=args.symbols)

    # ---- Effective N via participation ratio ----
    n_eff = effective_n_participation_ratio(corr)

    # ---- Per-asset and equal-weight portfolio Sharpe ----
    sharpes = {sym: annualised_sharpe(daily[sym]) for sym in args.symbols}
    mean_sharpe = float(np.mean(list(sharpes.values())))
    portfolio_daily = daily.mean(axis=1)
    portfolio_sharpe = annualised_sharpe(portfolio_daily)
    sqrt_n = np.sqrt(len(args.symbols))
    diversification_lift = portfolio_sharpe / mean_sharpe if mean_sharpe > 0 else 0.0

    summary = {
        "symbols": args.symbols,
        "oos_window": [args.oos_start, args.oos_end],
        "n_trades_oos": {sym: len(df) for sym, df in by_sym.items()},
        "n_trading_days_with_pnl": int((daily.abs() > 0).any(axis=1).sum()),
        "jaccard_entry_1h": jaccard,
        "daily_pnl_correlation": corr_df.round(4).to_dict(),
        "n_effective_participation_ratio": round(n_eff, 4),
        "sharpe_per_asset_daily": {k: round(v, 4) for k, v in sharpes.items()},
        "mean_sharpe": round(mean_sharpe, 4),
        "equal_weight_portfolio_sharpe": round(portfolio_sharpe, 4),
        "diversification_lift_vs_mean": round(diversification_lift, 4),
        "sqrt_n_max_lift": round(float(sqrt_n), 4),
    }

    print(json.dumps(summary, indent=2))

    (args.out_dir / "overlap.json").write_text(json.dumps(summary, indent=2))

    # ---- Heatmap ----
    fig, ax = plt.subplots(figsize=(5, 4.5))
    im = ax.imshow(corr, vmin=-1, vmax=1, cmap="RdBu_r", aspect="equal")
    ax.set_xticks(range(len(args.symbols)))
    ax.set_yticks(range(len(args.symbols)))
    ax.set_xticklabels(args.symbols)
    ax.set_yticklabels(args.symbols)
    for i in range(len(args.symbols)):
        for j in range(len(args.symbols)):
            ax.text(j, i, f"{corr[i, j]:.2f}", ha="center", va="center",
                    color="white" if abs(corr[i, j]) > 0.5 else "black",
                    fontsize=11)
    ax.set_title(f"Daily PnL correlation — Bollinger MR OOS\n{args.oos_start} → {args.oos_end}")
    fig.colorbar(im, ax=ax, label="Pearson")
    fig.tight_layout()
    fig.savefig(args.out_dir / "assets/daily_pnl_corr.png", dpi=120)
    plt.close(fig)

    # ---- Markdown summary ----
    lines = [
        "# Bollinger MR — Cross-Asset Trade Overlap (SPY / XLK / XLE)",
        "",
        f"OOS window: `{args.oos_start} → {args.oos_end}`. Trade counts: " +
        ", ".join(f"{s}={len(df)}" for s, df in by_sym.items()) + ".",
        f"Trading days with at least one PnL event: **{summary['n_trading_days_with_pnl']}**.",
        "",
        "## Jaccard similarity of entry bars (1h granularity)",
        "",
        "| Pair | Jaccard |",
        "|---|---|",
    ]
    for k, v in jaccard.items():
        lines.append(f"| {k} | {v:.4f} |")

    lines += [
        "",
        "Interpretation: Jaccard ∈ [0, 1]. 0 = no shared entry bars; 1 = identical entry timing.",
        "0.7+ would mean the strategy fires nearly simultaneously across assets — strong common driver.",
        "",
        "## Daily PnL correlation",
        "",
        "|  | " + " | ".join(args.symbols) + " |",
        "|---|" + "---|" * len(args.symbols),
    ]
    for i, sym in enumerate(args.symbols):
        lines.append("| " + sym + " | " + " | ".join(f"{corr[i, j]:.3f}" for j in range(len(args.symbols))) + " |")

    lines += [
        "",
        f"Effective N (participation ratio of eigenvalues) = **{n_eff:.3f}** "
        f"(max = {len(args.symbols)} for fully independent assets, "
        f"= 1 for rank-1 single-factor returns).",
        "",
        "## Per-asset Sharpe vs equal-weight portfolio Sharpe",
        "",
        "| | Sharpe (daily, ann.) |",
        "|---|---|",
    ]
    for sym in args.symbols:
        lines.append(f"| {sym} | {sharpes[sym]:.3f} |")
    lines += [
        f"| **Mean of 3** | **{mean_sharpe:.3f}** |",
        f"| **Equal-weight portfolio** | **{portfolio_sharpe:.3f}** |",
        "",
        f"Diversification lift = portfolio_sharpe / mean_sharpe = **{diversification_lift:.3f}**.",
        f"(Theoretical max = √N = {sqrt_n:.3f} for perfectly uncorrelated assets; min = 1 for perfectly correlated.)",
        "",
        "## Verdict",
        "",
        "Decision rule from the plan:",
        "- correlation > 0.7 ⇒ '3 winners' is really 1 edge × 3 assets; portfolio diversification illusory.",
        "- correlation < 0.4 ⇒ genuine diversification.",
        "- between 0.4 and 0.7 ⇒ partial — discount the portfolio Sharpe by the lift.",
        "",
        "![Daily PnL correlation](assets/daily_pnl_corr.png)",
        "",
        "## Citation",
        "",
        "- `[advances_fin_ml, p.40-44, ch.3]` — purged correlation discipline.",
    ]

    summary_path = args.out_dir / "summary.md"
    summary_path.write_text("\n".join(lines))
    print(f"\n✓ Wrote {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
