#!/usr/bin/env python3
"""Phase 3.5b addendum — Task C3: rebalance-mode comparison for 2-leg EW.

Mirrors ``run_phase3_5b_task_c2_rebalance_3leg.py`` but on the 2-leg
``LETF+QQQ`` portfolio (Task A's canonical blend). Tests the same 3
rebalance cadences on the QQQ-limited window 2001-05-14 → 2026-04-14.

Hypothesis (memory.md lead C3): with only 2 legs and Pearson ρ=0.555
between them (Task A), inter-leg drift should be structurally smaller
than in the 3-leg case because:

1. Drift sums to zero across legs ⇒ with n=2 legs the max drift is
   bounded by half the total spread, against n=3 where one leg can
   rally 2x harder than the others.
2. QQQ Donchian and LETF-on-SPY are both long-equity strategies; their
   drawdowns overlap (2008, 2020) so the rebalance pressure during
   crises is weaker than in 3-leg where GLD typically moves opposite.

Whether the hypothesis holds empirically is the question this script
answers.

Output
------
``reports/phase3_5b/variants/rebalance_modes/comparison_2leg.md`` with:

* Per-mode metrics table (CAGR / Sharpe / MaxDD / max drift / taxable
  events/yr / IR paid/yr / deposits/yr).
* ``drift_2leg.png`` — max |actual − target| weight per-bar across the
  2 legs under each rebalance mode.
* ``equity_2leg.png`` — equity curves overlay.
* ``summary_2leg.json`` — machine-readable snapshot.

Citations
---------
* Baseline EW / Σ-error-immune weights: ``[advances_fin_ml, p.298-299]``.
* Drift vs tax tradeoff framing: ``[leverage_for_the_long_run, p.17,
  Table 8]``.
* BR 15% IR on realized gains: Investment Mandate §4.
* LETF EMA100/2x winner: jornada
  ``2026-04-17-0055-b1c-letf-rotation-gates-PASS.md``.
* QQQ Donchian 20/10 winner: jornada
  ``2026-04-17-0120-a3b-tsmom-donchian-per-asset-PASS.md``.

Path tag: **[SWING BROKER]**.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import pandas as pd

from ai_trade.backtest.data.spx_tr_loader import load_spx_tr_daily
from ai_trade.backtest.data.tiingo_storage import TiingoStorage
from ai_trade.backtest.metrics.performance import (
    cagr as cagr_fn,
    max_drawdown,
    returns_from_equity,
    sharpe as sharpe_fn,
    volatility as vol_fn,
)
from ai_trade.backtest.metrics.rebalance_modes import (
    RebalanceResult,
    apply_daily_rebalance,
    apply_monthly_cashflow_rebalance,
    apply_monthly_sell_rebalance,
)
from ai_trade.backtest.strategies.letf_rotation import (
    LETFRotationConfig,
    simulate_letf_rotation,
)
from ai_trade.backtest.strategies.tsmom import (
    TSMOMConfig,
    simulate_tsmom,
)

log = logging.getLogger("phase3_5b.task_c3")

LETF_CFG = LETFRotationConfig(
    filter="EMA", lookback=100, band_pct=0.0, leverage=2.0, gold_weight=0.0,
)
QQQ_CFG = TSMOMConfig(entry_lookback=20, exit_lookback=10)

TARGET_WEIGHTS = {"LETF_2x": 1 / 2, "QQQ": 1 / 2}


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/phase3_5b/variants/rebalance_modes"),
    )
    ap.add_argument("--initial-capital", type=float, default=100_000.0)
    ap.add_argument(
        "--monthly-deposit-pct",
        type=float,
        default=0.005,
        help="Monthly deposit as fraction of initial capital (default 0.5%).",
    )
    ap.add_argument(
        "--storage-root", type=Path, default=Path("data/tiingo")
    )
    ap.add_argument("--spx-start", default="1970-01-02")
    ap.add_argument("--spx-end", default="2026-04-14")
    ap.add_argument("--spx-cutoff", default="2001-05-14")
    ap.add_argument("--tax-rate", type=float, default=0.15)
    ap.add_argument("--log-level", default="INFO")
    return ap.parse_args(argv)


def _load_tiingo_hlc(
    storage_root: Path, ticker: str
) -> tuple[pd.Series, pd.Series, pd.Series]:
    storage = TiingoStorage(root=storage_root)
    df = storage.read(ticker, frequency="daily")
    if df.empty:
        raise ValueError(f"{ticker}: empty daily frame")
    raw_close = df["close"].astype(float)
    adj_close = (
        df["adj_close"].astype(float)
        if "adj_close" in df.columns
        else raw_close
    )
    scale = (adj_close / raw_close).replace([pd.NA, pd.NaT], 1.0).fillna(1.0)
    close = adj_close.dropna()
    high = (df["high"].astype(float) * scale).loc[close.index].dropna()
    low = (df["low"].astype(float) * scale).loc[close.index].dropna()
    common = close.index.intersection(high.index).intersection(low.index)
    return close.loc[common], high.loc[common], low.loc[common]


def _build_tr_price(returns: pd.Series) -> pd.Series:
    p = (1.0 + returns).cumprod() * 100.0
    p.name = "spx_tr_price"
    return p


def _build_leg_returns(args: argparse.Namespace) -> pd.DataFrame:
    log.info("loading SPX TR stitched series …")
    spx_returns = load_spx_tr_daily(
        start=args.spx_start,
        end=args.spx_end,
        cutoff_date=pd.Timestamp(args.spx_cutoff),
    )
    spx_prices = _build_tr_price(spx_returns)

    log.info("loading Tiingo QQQ …")
    q_close, q_high, q_low = _load_tiingo_hlc(args.storage_root, "QQQ")

    log.info("simulating legs …")
    letf_r = simulate_letf_rotation(
        spx_returns, spx_prices, LETF_CFG
    ).daily_returns.dropna()
    qqq_r = simulate_tsmom(q_high, q_low, q_close, QQQ_CFG).daily_returns.dropna()

    common = letf_r.index.intersection(qqq_r.index)
    if len(common) == 0:
        raise RuntimeError("legs share no common index")

    df = pd.DataFrame(
        {
            "LETF_2x": letf_r.loc[common].astype(float),
            "QQQ": qqq_r.loc[common].astype(float),
        }
    )
    df = df.dropna()
    log.info(
        "common window: %d bars  %s → %s",
        len(df), df.index[0].date(), df.index[-1].date(),
    )
    return df


def _compute_metrics(result: RebalanceResult, years: float) -> dict:
    eq = result.equity
    rets = returns_from_equity(eq)
    drift_max_per_bar = result.max_drift
    max_abs_drift = float(result.drift.max().max())
    mean_max_drift = float(drift_max_per_bar.mean())

    tax_total = float(result.total_tax_paid)
    deposits_total = float(result.total_deposits)
    n_events = result.n_taxable_events

    return {
        "equity_final": float(eq.iloc[-1]),
        "cagr": float(cagr_fn(eq)),
        "sharpe": float(sharpe_fn(rets)),
        "volatility_ann": float(vol_fn(rets)),
        "max_drawdown": float(max_drawdown(eq)),
        "max_abs_drift": max_abs_drift,
        "mean_max_drift": mean_max_drift,
        "taxable_events": int(n_events),
        "taxable_events_per_year": float(n_events / years) if years > 0 else 0.0,
        "total_tax_paid": tax_total,
        "tax_per_year": float(tax_total / years) if years > 0 else 0.0,
        "total_deposits": deposits_total,
        "deposits_per_year": float(deposits_total / years) if years > 0 else 0.0,
    }


def _render_comparison_md(
    window_start: pd.Timestamp,
    window_end: pd.Timestamp,
    years: float,
    initial_capital: float,
    monthly_deposit: float,
    daily_m: dict,
    sell_m: dict,
    cash_m: dict,
    winner_ref: dict,
) -> str:
    def fmt_money(v: float) -> str:
        return f"${v:,.0f}"

    def fmt_pct(v: float) -> str:
        return f"{v * 100:.2f}%"

    lines = [
        "# Rebalance modes — 2-leg EW (LETF+QQQ)",
        "",
        "**Path tag:** [SWING BROKER]  ",
        f"**Window:** {window_start.date()} → {window_end.date()} "
        f"({years:.2f} yrs, {int(years * 252)} bars ≈).  ",
        f"**Target weights:** EW (1/2, 1/2).  ",
        f"**Initial capital:** {fmt_money(initial_capital)}.  ",
        f"**Monthly deposit (cashflow mode):** "
        f"{fmt_money(monthly_deposit)} ({monthly_deposit / initial_capital:.2%} of initial).  ",
        f"**BR IR rate (realized gains on sells):** 15%.",
        "",
        "## Comparative metrics",
        "",
        "| Metric | Daily (Task A ref) | Monthly sell | Monthly cashflow |",
        "|---|---|---|---|",
        f"| Equity final | {fmt_money(daily_m['equity_final'])} | "
        f"{fmt_money(sell_m['equity_final'])} | "
        f"{fmt_money(cash_m['equity_final'])} |",
        f"| CAGR | {fmt_pct(daily_m['cagr'])} | "
        f"{fmt_pct(sell_m['cagr'])} | {fmt_pct(cash_m['cagr'])} |",
        f"| Sharpe | {daily_m['sharpe']:.3f} | "
        f"{sell_m['sharpe']:.3f} | {cash_m['sharpe']:.3f} |",
        f"| Volatility (ann.) | {fmt_pct(daily_m['volatility_ann'])} | "
        f"{fmt_pct(sell_m['volatility_ann'])} | "
        f"{fmt_pct(cash_m['volatility_ann'])} |",
        f"| MaxDD | {fmt_pct(daily_m['max_drawdown'])} | "
        f"{fmt_pct(sell_m['max_drawdown'])} | "
        f"{fmt_pct(cash_m['max_drawdown'])} |",
        f"| Max drift (any leg) | "
        f"{fmt_pct(daily_m['max_abs_drift'])} | "
        f"{fmt_pct(sell_m['max_abs_drift'])} | "
        f"{fmt_pct(cash_m['max_abs_drift'])} |",
        f"| Mean per-bar max drift | "
        f"{fmt_pct(daily_m['mean_max_drift'])} | "
        f"{fmt_pct(sell_m['mean_max_drift'])} | "
        f"{fmt_pct(cash_m['mean_max_drift'])} |",
        f"| Taxable events / yr | {daily_m['taxable_events_per_year']:.1f} | "
        f"{sell_m['taxable_events_per_year']:.1f} | "
        f"{cash_m['taxable_events_per_year']:.1f} |",
        f"| IR paid / yr (rebal) | "
        f"{fmt_money(daily_m['tax_per_year'])} | "
        f"{fmt_money(sell_m['tax_per_year'])} | "
        f"{fmt_money(cash_m['tax_per_year'])} |",
        f"| Total IR paid | {fmt_money(daily_m['total_tax_paid'])} | "
        f"{fmt_money(sell_m['total_tax_paid'])} | "
        f"{fmt_money(cash_m['total_tax_paid'])} |",
        f"| Total deposits | {fmt_money(daily_m['total_deposits'])} | "
        f"{fmt_money(sell_m['total_deposits'])} | "
        f"{fmt_money(cash_m['total_deposits'])} |",
        "",
        "## 2-leg vs 3-leg drift — observation",
        "",
        "Compare the drift figures above against `comparison_3leg.md` to",
        "see whether the drift-hypothesis holds: 2-leg with ρ=0.555 should",
        "exhibit smaller per-bar max drift than 3-leg because leg returns",
        "co-move more (both long equity). A smaller drift ceiling translates",
        "directly into fewer / smaller taxable rebalance trades.",
        "",
        "The sub-index `rebalance_modes/README.md` surfaces the delta",
        "drift / delta tax between the two variants.",
        "",
        "## Interpretation notes",
        "",
        "* **Daily rebal tax = 0 at this layer.** Matches the C2 convention:",
        "  per-leg trade-level tax (15% BR IR on each profitable exit) is",
        "  already in the Task A 2-leg report; here we isolate *rebalance-",
        "  mechanic* tax incidence.",
        "* **Monthly-sell:** fires at end-of-month only; 15% IR on the",
        "  overweight leg's realized gain (proportional cost basis).",
        "* **Monthly-cashflow:** tax-free at the rebal layer — the monthly",
        "  deposit lands entirely on the most underweight leg.",
        "* **Drift note:** max drift is the worst per-bar deviation *before*",
        "  rebalance. Daily mode resets to zero every bar ⇒ drift ≡ 0.",
        "",
        "## Reference values",
        "",
        "Task A 2-leg (daily rebal, tax_per_leg=15% via trade log):",
        "",
        "| Ref | Value |",
        "|---|---|",
        f"| Sharpe | {winner_ref['sharpe']:.3f} |",
        f"| CAGR | {fmt_pct(winner_ref['cagr_pct'])} |",
        f"| MaxDD | {fmt_pct(winner_ref['max_drawdown_pct'])} |",
        "",
        "The *Daily (Task A ref)* column above reproduces these numbers",
        "from the raw daily_returns cumprod (no per-leg trade tax applied",
        "at the equity layer — matches `letf_qqq_2leg_ew/summary.json`).",
        "",
        "## Citations",
        "",
        "* Baseline reset: `[advances_fin_ml, p.298-299]`.",
        "* Drift vs tax tradeoff: `[leverage_for_the_long_run, p.17,",
        "  Table 8]`.",
        "* BR 15% IR: Investment Mandate §4.",
        "",
        "## Artefacts",
        "",
        "* `drift_2leg.png` — max |actual - target| weight across 2 legs",
        "  for each mode, over the full window.",
        "* `equity_2leg.png` — equity curves overlay (log scale).",
        "* `summary_2leg.json` — structured snapshot.",
        "",
    ]
    return "\n".join(lines)


def _plot_drift(
    path: Path,
    daily_r: RebalanceResult,
    sell_r: RebalanceResult,
    cash_r: RebalanceResult,
) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        sell_r.max_drift.index,
        sell_r.max_drift.values * 100,
        label="monthly_sell",
        color="#1f6feb",
        linewidth=0.8,
    )
    ax.plot(
        cash_r.max_drift.index,
        cash_r.max_drift.values * 100,
        label="monthly_cashflow",
        color="#e85d75",
        linewidth=0.8,
    )
    ax.plot(
        daily_r.max_drift.index,
        daily_r.max_drift.values * 100,
        label="daily (≡ 0)",
        color="#444",
        linewidth=0.7,
        linestyle=":",
    )
    ax.set_title("Per-bar max |actual − target| weight drift — 2-leg EW")
    ax.set_xlabel("Date")
    ax.set_ylabel("Drift (% points)")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def _plot_equity(
    path: Path,
    daily_r: RebalanceResult,
    sell_r: RebalanceResult,
    cash_r: RebalanceResult,
) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(daily_r.equity.index, daily_r.equity.values,
            label="daily", color="#1f6feb", linewidth=1.1)
    ax.plot(sell_r.equity.index, sell_r.equity.values,
            label="monthly_sell", color="#2da44e", linewidth=1.0)
    ax.plot(cash_r.equity.index, cash_r.equity.values,
            label="monthly_cashflow (incl. deposits)",
            color="#e85d75", linewidth=1.0)
    ax.set_yscale("log")
    ax.set_title("Equity curves — 2-leg EW rebalance modes")
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity ($, log scale)")
    ax.legend(loc="upper left")
    ax.grid(True, which="both", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def _load_winner_ref(root: Path) -> dict:
    ref_path = (
        root
        / "reports"
        / "phase3_5b"
        / "variants"
        / "letf_qqq_2leg_ew"
        / "summary.json"
    )
    if not ref_path.exists():
        log.warning("Task A reference missing at %s — using zeros", ref_path)
        return {"sharpe": 0.0, "cagr_pct": 0.0, "max_drawdown_pct": 0.0}
    data = json.loads(ref_path.read_text())
    m = data["metrics"]
    return {
        "sharpe": float(m["sharpe"]),
        "cagr_pct": float(m["cagr_pct"]),
        "max_drawdown_pct": float(m["max_drawdown_pct"]),
    }


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    rdf = _build_leg_returns(args)
    window_start = pd.Timestamp(rdf.index[0])
    window_end = pd.Timestamp(rdf.index[-1])
    n_bars = len(rdf)
    years = n_bars / 252.0

    monthly_deposit = args.initial_capital * args.monthly_deposit_pct

    log.info("applying 3 rebalance modes …")
    daily_r = apply_daily_rebalance(rdf, TARGET_WEIGHTS, args.initial_capital)
    sell_r = apply_monthly_sell_rebalance(
        rdf, TARGET_WEIGHTS,
        initial_capital=args.initial_capital,
        tax_rate=args.tax_rate,
    )
    cash_r = apply_monthly_cashflow_rebalance(
        rdf, TARGET_WEIGHTS,
        monthly_deposit=monthly_deposit,
        initial_capital=args.initial_capital,
    )

    daily_m = _compute_metrics(daily_r, years)
    sell_m = _compute_metrics(sell_r, years)
    cash_m = _compute_metrics(cash_r, years)

    log.info(
        "daily:    CAGR=%.2f%%  Sharpe=%.3f  MaxDD=%.2f%%",
        daily_m["cagr"] * 100, daily_m["sharpe"], daily_m["max_drawdown"] * 100,
    )
    log.info(
        "sell:     CAGR=%.2f%%  Sharpe=%.3f  MaxDD=%.2f%%  IR/yr=$%.0f  ev/yr=%.1f",
        sell_m["cagr"] * 100, sell_m["sharpe"], sell_m["max_drawdown"] * 100,
        sell_m["tax_per_year"], sell_m["taxable_events_per_year"],
    )
    log.info(
        "cashflow: CAGR=%.2f%%  Sharpe=%.3f  MaxDD=%.2f%%  dep/yr=$%.0f",
        cash_m["cagr"] * 100, cash_m["sharpe"], cash_m["max_drawdown"] * 100,
        cash_m["deposits_per_year"],
    )

    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    winner_ref = _load_winner_ref(Path.cwd())

    md = _render_comparison_md(
        window_start=window_start,
        window_end=window_end,
        years=years,
        initial_capital=args.initial_capital,
        monthly_deposit=monthly_deposit,
        daily_m=daily_m,
        sell_m=sell_m,
        cash_m=cash_m,
        winner_ref=winner_ref,
    )
    (out_dir / "comparison_2leg.md").write_text(md, encoding="utf-8")

    summary = {
        "variant": "2leg_ew",
        "window_start": window_start.strftime("%Y-%m-%d"),
        "window_end": window_end.strftime("%Y-%m-%d"),
        "n_bars": n_bars,
        "years": years,
        "initial_capital": args.initial_capital,
        "monthly_deposit": monthly_deposit,
        "tax_rate": args.tax_rate,
        "target_weights": TARGET_WEIGHTS,
        "modes": {
            "daily": daily_m,
            "monthly_sell": sell_m,
            "monthly_cashflow": cash_m,
        },
        "winner_ref": winner_ref,
    }
    (out_dir / "summary_2leg.json").write_text(
        json.dumps(summary, indent=2, default=float), encoding="utf-8"
    )

    _plot_drift(out_dir / "drift_2leg.png", daily_r, sell_r, cash_r)
    _plot_equity(out_dir / "equity_2leg.png", daily_r, sell_r, cash_r)

    log.info("done — wrote %s (md + summary + 2 png)", out_dir)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
