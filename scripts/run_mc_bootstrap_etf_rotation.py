#!/usr/bin/env python3
"""Monte Carlo bootstrap of ETF Rotation winner monthly returns.

Runs ETFRotationStrategy on IS (2003-01-02 → 2024-12-31) and OOS
(2025-01-01 → 2026-04-14), extracts monthly equity returns, applies
Politis-Romano stationary bootstrap (block_mean=3, quarterly blocks),
and emits 95% CIs for Sharpe / CAGR / MaxDD.

Citations:
- `[advances_fin_ml, p.196-202, ch.11]` — bootstrap CI for Sharpe.
- `[stocks_on_the_move, p.81]` — Clenow momentum score for ranking.
- `[stocks_on_the_move, p.66-67]` — SMA(200) regime filter.
- Politis & Romano (1994) — stationary bootstrap algorithm.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ai_trade.backtest.validation.bootstrap import stationary_bootstrap_trades

SYMBOLS = ["SPY", "QQQ", "IWM", "GLD", "TLT"]


def monthly_returns_from_equity(equity: pd.Series) -> np.ndarray:
    """Resample equity curve to month-end, return monthly pct-change array."""
    monthly = equity.resample("ME").last().dropna()
    pct = monthly.pct_change().dropna()
    return pct.to_numpy(dtype=float)


def compute_metrics(
    returns: np.ndarray,
    cash: float,
    periods_per_year: float,
) -> tuple[float, float, float]:
    """Annualised Sharpe, CAGR, MaxDD from monthly return sequence."""
    mean_r = float(returns.mean())
    std_r = float(returns.std())
    sharpe = (mean_r / std_r) * np.sqrt(periods_per_year) if std_r > 0 else 0.0

    equity = cash * np.cumprod(1.0 + returns)
    years = len(returns) / periods_per_year
    cagr = (equity[-1] / cash) ** (1 / years) - 1 if years > 0 else 0.0
    peak = np.maximum.accumulate(equity)
    dd = (equity - peak) / peak
    max_dd = float(dd.min())
    return sharpe, cagr, max_dd


def bootstrap_metrics(
    returns: np.ndarray,
    cash: float,
    periods_per_year: float,
    block_mean: int,
    n_resamples: int,
    seed: int,
) -> dict[str, np.ndarray]:
    resamples = stationary_bootstrap_trades(
        returns, block_mean=block_mean, n_resamples=n_resamples, seed=seed,
    )
    means = resamples.mean(axis=1)
    stds = resamples.std(axis=1)
    sharpe = np.where(stds > 0, (means / stds) * np.sqrt(periods_per_year), 0.0)

    equity = cash * np.cumprod(1.0 + resamples, axis=1)
    years = resamples.shape[1] / periods_per_year
    cagr = np.power(equity[:, -1] / cash, 1 / years) - 1 if years > 0 else np.zeros(n_resamples)
    peaks = np.maximum.accumulate(equity, axis=1)
    dd = (equity - peaks) / peaks
    max_dd = dd.min(axis=1)
    return {"sharpe": sharpe, "cagr": cagr, "max_dd": max_dd}


def ci_pct(arr: np.ndarray, lo: float = 2.5, hi: float = 97.5) -> tuple[float, float]:
    return float(np.percentile(arr, lo)), float(np.percentile(arr, hi))


def run_strategy(
    src,
    start: date,
    end: date,
    top_n: int,
    cash: float,
    storage_root: Path,
) -> pd.Series:
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    from ai_trade.backtest.engine import ExecutionConfig, ExecutionSimulator, Runner
    from ai_trade.backtest.strategies.etf_rotation import ETFRotationStrategy

    warmup = start - timedelta(days=500)
    raw = src.fetch_many(SYMBOLS, warmup, end, asset_class="etf", frequency="daily")
    data_full = {s: raw[s] for s in SYMBOLS if s in raw}
    data_bounded = {s: df.loc[pd.Timestamp(start):pd.Timestamp(end)] for s, df in data_full.items()}

    strategy = ETFRotationStrategy(
        data=data_full,
        symbols=SYMBOLS,
        index_symbol="SPY",
        top_n=top_n,
    )
    runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
    result = runner.run(strategy=strategy, data=data_bounded, initial_cash=cash)
    return result.equity_curve


def main(argv: list[str] | None = None) -> int:
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage

    ap = argparse.ArgumentParser(description="MC bootstrap on ETF Rotation monthly returns")
    ap.add_argument("--is-start", type=date.fromisoformat, default=date(2003, 1, 2))
    ap.add_argument("--is-end", type=date.fromisoformat, default=date(2024, 12, 31))
    ap.add_argument("--oos-start", type=date.fromisoformat, default=date(2025, 1, 1))
    ap.add_argument("--oos-end", type=date.fromisoformat, default=date(2026, 4, 14))
    ap.add_argument("--top-n", type=int, default=1)
    ap.add_argument("--cash", type=float, default=100_000.0)
    ap.add_argument("--block-mean", type=int, default=3,
                    help="Quarterly blocks for monthly return bootstrap. "
                         "[advances_fin_ml, p.196-202]")
    ap.add_argument("--n-resamples", type=int, default=10_000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--storage-root", type=Path, default=Path("data/tiingo"))
    ap.add_argument("--out-dir", type=Path, default=Path("reports/etf_rotation_mc_bootstrap"))
    args = ap.parse_args(argv)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = args.out_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    src_obj = TiingoSource(storage=TiingoStorage(root=args.storage_root))

    periods_per_year = 12.0  # monthly returns

    all_summaries: dict[str, dict] = {}
    for label, start, end in [("is", args.is_start, args.is_end),
                               ("oos", args.oos_start, args.oos_end)]:
        print(f"\n=== {label.upper()} period: {start} → {end} ===")
        equity = run_strategy(src_obj, start, end, args.top_n, args.cash, args.storage_root)
        monthly = monthly_returns_from_equity(equity)
        n = len(monthly)
        years = n / periods_per_year

        if n < 3:
            print(f"  {label}: only {n} monthly returns — skipping (too few)")
            continue

        sharpe_pt, cagr_pt, dd_pt = compute_metrics(monthly, args.cash, periods_per_year)
        boot = bootstrap_metrics(monthly, args.cash, periods_per_year,
                                 args.block_mean, args.n_resamples, args.seed)
        sh_lo, sh_hi = ci_pct(boot["sharpe"])
        cg_lo, cg_hi = ci_pct(boot["cagr"])
        dd_lo, dd_hi = ci_pct(boot["max_dd"])

        print(
            f"  n_months={n}, years={years:.2f}\n"
            f"  Sharpe = {sharpe_pt:.3f}  CI95=[{sh_lo:.3f}, {sh_hi:.3f}]\n"
            f"  CAGR   = {cagr_pt*100:.2f}%  CI95=[{cg_lo*100:.2f}%, {cg_hi*100:.2f}%]\n"
            f"  MaxDD  = {dd_pt*100:.2f}%  CI95=[{dd_lo*100:.2f}%, {dd_hi*100:.2f}%]"
        )

        all_summaries[label] = {
            "n_months": n,
            "years": round(years, 4),
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
        }

        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.hist(boot["sharpe"], bins=60, color="steelblue", edgecolor="white", alpha=0.85)
        ax.axvline(sharpe_pt, color="black", linestyle="-", linewidth=2,
                   label=f"point = {sharpe_pt:.3f}")
        ax.axvline(sh_lo, color="firebrick", linestyle="--", linewidth=1.5,
                   label=f"CI95 lo = {sh_lo:.3f}")
        ax.axvline(sh_hi, color="firebrick", linestyle="--", linewidth=1.5,
                   label=f"CI95 hi = {sh_hi:.3f}")
        ax.axvline(0, color="gray", linestyle=":", linewidth=1)
        ax.set_xlabel("Annualised Sharpe (resample)")
        ax.set_ylabel("Frequency")
        ax.set_title(f"ETF Rotation top-{args.top_n} — {label.upper()} Sharpe bootstrap (n={args.n_resamples})")
        ax.legend(loc="upper right", fontsize=9)
        fig.tight_layout()
        fig.savefig(assets_dir / f"sharpe_hist_etfrot_{label}.png", dpi=110)
        plt.close(fig)

    json_path = args.out_dir / "etf_rotation_ci.json"
    json_path.write_text(json.dumps(all_summaries, indent=2))
    print(f"\n→ {json_path}")

    # Summary markdown
    lines = [
        "# ETF Rotation top-1 — MC Bootstrap CI (Politis-Romano stationary)",
        "",
        f"Bootstrap params: `block_mean={args.block_mean}` (quarterly), "
        f"`n_resamples={args.n_resamples}`, `seed={args.seed}`.",
        f"IS: `{args.is_start} → {args.is_end}`. OOS: `{args.oos_start} → {args.oos_end}`.",
        "",
        "**Monthly returns** resampled from equity curve end-of-month. "
        "Sharpe annualised with `periods_per_year=12`.",
        "",
        "Citations: `[advances_fin_ml, p.196-202, ch.11]` — bootstrap CI; "
        "`[stocks_on_the_move, p.81, p.66-67]` — strategy.",
        "",
        "| Period | N months | Sharpe (pt) | Sharpe CI95 | CAGR (pt) | CAGR CI95 | MaxDD (pt) | MaxDD CI95 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for label in ("is", "oos"):
        s = all_summaries.get(label)
        if s is None:
            lines.append(f"| {label.upper()} | — | — | — | — | — | — | — |")
            continue
        sh = s["point"]["sharpe"]
        sh_ci = s["ci_95"]["sharpe"]
        cg = s["point"]["cagr"] * 100
        cg_ci = [c * 100 for c in s["ci_95"]["cagr"]]
        dd = s["point"]["max_dd"] * 100
        dd_ci = [c * 100 for c in s["ci_95"]["max_dd"]]
        lines.append(
            f"| {label.upper()} | {s['n_months']} | {sh:.3f} | [{sh_ci[0]:.3f}, {sh_ci[1]:.3f}] "
            f"| {cg:.2f}% | [{cg_ci[0]:.2f}%, {cg_ci[1]:.2f}%] "
            f"| {dd:.2f}% | [{dd_ci[0]:.2f}%, {dd_ci[1]:.2f}%] |"
        )

    lines += [
        "",
        "## Verdict",
        "",
        "IS lower bound must be > 0 for robust edge. OOS CI will be wide (15 months).",
        "",
        "## Histograms",
        "",
        "![IS sharpe hist](assets/sharpe_hist_etfrot_is.png)",
        "",
        "![OOS sharpe hist](assets/sharpe_hist_etfrot_oos.png)",
    ]

    summary_path = args.out_dir / "summary.md"
    summary_path.write_text("\n".join(lines))
    print(f"✓ Wrote {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
