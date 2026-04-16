#!/usr/bin/env python3
"""Monte Carlo bootstrap of Bollinger MR winner trade sequences.

Reads `reports/bollinger_mr_trades/<sym>_<oos_start>_<oos_end>.csv`
emitted by `scripts/run_oos_bollinger_mr.py --emit-trades`, runs a
Politis-Romano stationary bootstrap (block_mean=5) on the OOS PnL,
and outputs 95% CIs for Sharpe / CAGR / MaxDD.

Citations:
- `[advances_fin_ml, p.196-202, ch.11]` — bootstrap CI for Sharpe.
- Politis & Romano (1994) — stationary bootstrap algorithm.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ai_trade.backtest.validation.bootstrap import stationary_bootstrap_trades


def trade_returns_from_prices(df: pd.DataFrame) -> np.ndarray:
    """Per-trade return on capital (price-based, equity-history-independent).

    For long: (exit-entry)/entry. For short: (entry-exit)/entry. The
    bar-level equity Sharpe reported by the script (e.g., 1.481 SPY OOS)
    is not identical to trade-return Sharpe but the two are within ~5%
    for short-hold strategies (max_hold≈1 day) — the bootstrap CI lives
    around the trade-return point estimate.
    """
    side = df["side"].astype(str).str.lower()
    pr = (df["exit_price"] - df["entry_price"]) / df["entry_price"]
    pr = pr.where(side == "long", -pr)
    return pr.to_numpy(dtype=float)


def compute_metrics(
    returns: np.ndarray,
    cash: float,
    years: float,
    trades_per_year: float,
    risk_pct: float,
) -> tuple[float, float, float]:
    """Annualised Sharpe, CAGR, MaxDD from a price-return sequence.

    Compounding: equity_t = cash × prod(1 + risk_pct × r_i). This matches
    BollingerMRStrategy's volume sizing (risk_pct of running equity).
    Sharpe uses raw returns (risk_pct cancels out: const × mean / const ×
    std = same).
    """
    mean_r = float(returns.mean())
    std_r = float(returns.std())
    sharpe = (mean_r / std_r) * np.sqrt(trades_per_year) if std_r > 0 else 0.0

    levered = 1.0 + risk_pct * returns
    levered = np.clip(levered, 1e-12, None)  # protect ruin from finite resamples
    equity = cash * np.cumprod(levered)
    cagr = (equity[-1] / cash) ** (1 / years) - 1 if years > 0 else 0.0
    peak = np.maximum.accumulate(equity)
    dd = (equity - peak) / peak
    max_dd = float(dd.min())

    return sharpe, cagr, max_dd


def bootstrap_metrics(
    returns: np.ndarray,
    cash: float,
    years: float,
    trades_per_year: float,
    risk_pct: float,
    block_mean: int,
    n_resamples: int,
    seed: int,
) -> dict[str, np.ndarray]:
    """Vectorised metric computation across all bootstrap resamples."""
    resamples = stationary_bootstrap_trades(
        returns, block_mean=block_mean, n_resamples=n_resamples, seed=seed,
    )
    means = resamples.mean(axis=1)
    stds = resamples.std(axis=1)
    sharpe = np.where(stds > 0, (means / stds) * np.sqrt(trades_per_year), 0.0)

    levered = np.clip(1.0 + risk_pct * resamples, 1e-12, None)
    equity = cash * np.cumprod(levered, axis=1)
    cagr = np.power(equity[:, -1] / cash, 1 / years) - 1 if years > 0 else np.zeros(len(resamples))

    peaks = np.maximum.accumulate(equity, axis=1)
    dd = (equity - peaks) / peaks
    max_dd = dd.min(axis=1)

    return {"sharpe": sharpe, "cagr": cagr, "max_dd": max_dd}


def ci_pct(arr: np.ndarray, low_q: float = 2.5, high_q: float = 97.5) -> tuple[float, float]:
    return float(np.percentile(arr, low_q)), float(np.percentile(arr, high_q))


def process_ticker(
    trades_csv: Path,
    cash: float,
    risk_pct: float,
    block_mean: int,
    n_resamples: int,
    seed: int,
    out_dir: Path,
) -> dict:
    df = pd.read_csv(trades_csv)
    if df.empty:
        raise RuntimeError(f"empty trades CSV: {trades_csv}")
    if "period" not in df.columns:
        raise RuntimeError(f"trades CSV missing 'period' column: {trades_csv}")

    symbol = df["symbol"].iloc[0]
    print(f"\n=== {symbol} ===  (from {trades_csv.name})")

    summary: dict = {"symbol": symbol, "trades_csv": str(trades_csv)}

    for period in ("train", "oos"):
        sub = df[df["period"] == period].copy()
        if sub.empty:
            print(f"  {period}: no trades, skipping")
            continue

        sub["entry_time"] = pd.to_datetime(sub["entry_time"])
        sub["exit_time"] = pd.to_datetime(sub["exit_time"])
        sub = sub.sort_values("entry_time").reset_index(drop=True)

        returns = trade_returns_from_prices(sub)
        n_trades = len(returns)
        first_entry = sub["entry_time"].iloc[0]
        last_exit = sub["exit_time"].iloc[-1]
        years = max((last_exit - first_entry).total_seconds() / (365.25 * 86400), 1e-9)
        trades_per_year = n_trades / years

        sharpe_pt, cagr_pt, dd_pt = compute_metrics(
            returns, cash, years, trades_per_year, risk_pct,
        )

        boot = bootstrap_metrics(
            returns, cash, years, trades_per_year, risk_pct,
            block_mean=block_mean, n_resamples=n_resamples, seed=seed,
        )
        sh_lo, sh_hi = ci_pct(boot["sharpe"])
        cg_lo, cg_hi = ci_pct(boot["cagr"])
        dd_lo, dd_hi = ci_pct(boot["max_dd"])

        period_summary = {
            "n_trades": n_trades,
            "years": round(years, 4),
            "trades_per_year": round(trades_per_year, 2),
            "first_entry": first_entry.isoformat(),
            "last_exit": last_exit.isoformat(),
            "point": {
                "sharpe": round(sharpe_pt, 4),
                "cagr": round(cagr_pt, 6),
                "max_dd": round(dd_pt, 6),
            },
            "ci_95": {
                "sharpe": [round(sh_lo, 4), round(sh_hi, 4)],
                "cagr": [round(cg_lo, 6), round(cg_hi, 6)],
                "max_dd": [round(dd_lo, 6), round(dd_hi, 6)],
            },
            "bootstrap": {
                "block_mean": block_mean,
                "n_resamples": n_resamples,
                "seed": seed,
            },
        }
        summary[period] = period_summary

        print(
            f"  {period}: n={n_trades}, years={years:.2f}, t/y={trades_per_year:.1f}\n"
            f"    Sharpe = {sharpe_pt:.3f}  CI95=[{sh_lo:.3f}, {sh_hi:.3f}]\n"
            f"    CAGR   = {cagr_pt*100:.2f}%  CI95=[{cg_lo*100:.2f}%, {cg_hi*100:.2f}%]\n"
            f"    MaxDD  = {dd_pt*100:.2f}%  CI95=[{dd_lo*100:.2f}%, {dd_hi*100:.2f}%]"
        )

        if period == "oos":
            assets_dir = out_dir / "assets"
            assets_dir.mkdir(parents=True, exist_ok=True)
            fig, ax = plt.subplots(figsize=(8, 4.5))
            ax.hist(boot["sharpe"], bins=60, color="steelblue", edgecolor="white", alpha=0.85)
            ax.axvline(sharpe_pt, color="black", linestyle="-", linewidth=2, label=f"point = {sharpe_pt:.3f}")
            ax.axvline(sh_lo, color="firebrick", linestyle="--", linewidth=1.5, label=f"CI95 lo = {sh_lo:.3f}")
            ax.axvline(sh_hi, color="firebrick", linestyle="--", linewidth=1.5, label=f"CI95 hi = {sh_hi:.3f}")
            ax.axvline(0, color="gray", linestyle=":", linewidth=1)
            ax.set_xlabel("Annualised Sharpe (resample)")
            ax.set_ylabel("Frequency")
            ax.set_title(f"{symbol} OOS — Bollinger MR Sharpe bootstrap (n={n_resamples})")
            ax.legend(loc="upper right", fontsize=9)
            fig.tight_layout()
            fig.savefig(assets_dir / f"sharpe_hist_{symbol.lower()}.png", dpi=110)
            plt.close(fig)

    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="MC bootstrap on Bollinger MR winner trades")
    ap.add_argument("--trades-dir", type=Path, default=Path("reports/bollinger_mr_trades"))
    ap.add_argument(
        "--symbols", nargs="+",
        default=["SPY", "XLK", "XLE"],
        help="Tickers to process; CSVs must exist in --trades-dir",
    )
    ap.add_argument("--oos-start", default="2025-01-01")
    ap.add_argument("--oos-end", default="2026-04-15")
    ap.add_argument("--cash", type=float, default=100_000.0)
    ap.add_argument(
        "--risk-pct", type=float, default=0.95,
        help="Position sizing as fraction of equity per trade (matches BollingerMRStrategy default)",
    )
    ap.add_argument("--block-mean", type=int, default=5)
    ap.add_argument("--n-resamples", type=int, default=10_000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out-dir", type=Path, default=Path("reports/bollinger_mr_mc_bootstrap"))
    args = ap.parse_args(argv)

    args.out_dir.mkdir(parents=True, exist_ok=True)

    all_summaries = {}
    for sym in args.symbols:
        csv = args.trades_dir / f"{sym}_{args.oos_start}_{args.oos_end}.csv"
        if not csv.exists():
            print(f"ERROR: missing {csv}", file=sys.stderr)
            return 1
        summary = process_ticker(
            csv,
            cash=args.cash,
            risk_pct=args.risk_pct,
            block_mean=args.block_mean,
            n_resamples=args.n_resamples,
            seed=args.seed,
            out_dir=args.out_dir,
        )
        all_summaries[sym] = summary
        json_path = args.out_dir / f"{sym.lower()}_ci.json"
        json_path.write_text(json.dumps(summary, indent=2))
        print(f"  → {json_path}")

    # Summary markdown
    lines: list[str] = [
        "# Bollinger MR — MC Bootstrap CI (Politis-Romano stationary)",
        "",
        f"Bootstrap params: `block_mean={args.block_mean}`, `n_resamples={args.n_resamples}`, `seed={args.seed}`.",
        f"OOS window: `{args.oos_start} → {args.oos_end}`. Cash: ${args.cash:,.0f}. risk_pct: {args.risk_pct}.",
        "",
        "**Sharpe** is annualised from per-trade price returns (`(exit-entry)/entry`, signed by side); "
        "**CAGR** and **MaxDD** compound returns at `risk_pct × ret` per trade — matches `BollingerMRStrategy`'s sizing.",
        "Sharpe is leverage-invariant (risk_pct cancels in `mean/std`); CAGR/MaxDD scale with `risk_pct`.",
        "",
        "Citations: `[advances_fin_ml, p.196-202, ch.11]` — Sharpe CI; Politis & Romano (1994) — stationary bootstrap.",
        "",
        "## Per-ticker OOS Sharpe / CAGR / MaxDD with 95% CI",
        "",
        "| Ticker | N | Years | Sharpe (point) | Sharpe CI95 | CAGR (point) | CAGR CI95 | MaxDD (point) | MaxDD CI95 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for sym in args.symbols:
        s = all_summaries[sym].get("oos")
        if s is None:
            lines.append(f"| {sym} | — | — | — | — | — | — | — | — |")
            continue
        sh = s["point"]["sharpe"]
        sh_ci = s["ci_95"]["sharpe"]
        cg = s["point"]["cagr"] * 100
        cg_ci = [c * 100 for c in s["ci_95"]["cagr"]]
        dd = s["point"]["max_dd"] * 100
        dd_ci = [c * 100 for c in s["ci_95"]["max_dd"]]
        lines.append(
            f"| {sym} | {s['n_trades']} | {s['years']:.2f} "
            f"| {sh:.3f} | [{sh_ci[0]:.3f}, {sh_ci[1]:.3f}] "
            f"| {cg:.2f}% | [{cg_ci[0]:.2f}%, {cg_ci[1]:.2f}%] "
            f"| {dd:.2f}% | [{dd_ci[0]:.2f}%, {dd_ci[1]:.2f}%] |"
        )

    lines += [
        "",
        "## Train (2021-2024) baseline for comparison",
        "",
        "| Ticker | N | Years | Sharpe (point) | Sharpe CI95 | CAGR (point) | CAGR CI95 | MaxDD (point) | MaxDD CI95 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for sym in args.symbols:
        s = all_summaries[sym].get("train")
        if s is None:
            lines.append(f"| {sym} | — | — | — | — | — | — | — | — |")
            continue
        sh = s["point"]["sharpe"]
        sh_ci = s["ci_95"]["sharpe"]
        cg = s["point"]["cagr"] * 100
        cg_ci = [c * 100 for c in s["ci_95"]["cagr"]]
        dd = s["point"]["max_dd"] * 100
        dd_ci = [c * 100 for c in s["ci_95"]["max_dd"]]
        lines.append(
            f"| {sym} | {s['n_trades']} | {s['years']:.2f} "
            f"| {sh:.3f} | [{sh_ci[0]:.3f}, {sh_ci[1]:.3f}] "
            f"| {cg:.2f}% | [{cg_ci[0]:.2f}%, {cg_ci[1]:.2f}%] "
            f"| {dd:.2f}% | [{dd_ci[0]:.2f}%, {dd_ci[1]:.2f}%] |"
        )

    lines += [
        "",
        "## Verdict",
        "",
        "Lower bound of OOS Sharpe CI95 must be `> 0` for the edge to be statistically",
        "non-trivial even before López de Prado deflation (DSR). If any ticker fails this,",
        "its single-block OOS validation rests on luck, not reproducible structure.",
        "",
        "## Histograms",
        "",
    ]
    for sym in args.symbols:
        lines.append(f"![{sym} sharpe hist](assets/sharpe_hist_{sym.lower()}.png)")
        lines.append("")

    summary_path = args.out_dir / "summary.md"
    summary_path.write_text("\n".join(lines))
    print(f"\n✓ Wrote {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
