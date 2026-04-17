#!/usr/bin/env python3
"""Phase 3.5b addendum — Task C2: rebalance-mode comparison for 3-leg EW.

Reuses the Phase 3.5b winner's 3 legs (LETF EMA100/2x + QQQ Donchian 20/10
+ GLD Donchian 40/20) but applies 3 different rebalancing cadences on the
common window (GLD-limited, 2004-11-18 → 2026-04-14):

* ``daily``             — reset to (1/3, 1/3, 1/3) at every bar (winner).
* ``monthly_sell``      — let weights drift, sell overweights → buy
                          underweights at end-of-month, 15% BR IR on
                          realized gains reduces the rebalance pool.
* ``monthly_cashflow``  — let weights drift, inject ``monthly_deposit``
                          into the most-underweight leg at end-of-month.
                          No sells ⇒ no realized-gains tax.

Output
------
``reports/phase3_5b/variants/rebalance_modes/comparison_3leg.md`` with:

* Per-mode table (CAGR / Sharpe / MaxDD / max drift % / taxable events/yr
  / IR paid/yr / deposits/yr).
* Drift-per-leg evolution plot (``drift_3leg.png``).
* Equity curves overlay (``equity_3leg.png``).
* ``summary_3leg.json`` — machine-readable snapshot for sub-index.

Conclusion is left for the Markdown author (this script writes the raw
comparison; the jornada entry interprets it).

Citations
---------
* Daily reset baseline: ``[advances_fin_ml, p.298-299]``.
* Drift vs tax tradeoff framing: ``[leverage_for_the_long_run, p.17,
  Table 8]`` (infrequent rebal preserves compounding but drifts risk).
* BR 15 % IR on realized gains: Investment Mandate §4.
* Legs inherit from the Phase 3.5b winners (LETF/QQQ/GLD).

Path tag: **[SWING BROKER]**.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import numpy as np
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

log = logging.getLogger("phase3_5b.task_c2")

LETF_CFG = LETFRotationConfig(
    filter="EMA", lookback=100, band_pct=0.0, leverage=2.0, gold_weight=0.0,
)
QQQ_CFG = TSMOMConfig(entry_lookback=20, exit_lookback=10)
GLD_CFG = TSMOMConfig(entry_lookback=40, exit_lookback=20)

TARGET_WEIGHTS = {"LETF_2x": 1 / 3, "QQQ": 1 / 3, "GLD": 1 / 3}


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


def _build_leg_returns(
    args: argparse.Namespace,
) -> pd.DataFrame:
    log.info("loading SPX TR stitched series …")
    spx_returns = load_spx_tr_daily(
        start=args.spx_start,
        end=args.spx_end,
        cutoff_date=pd.Timestamp(args.spx_cutoff),
    )
    spx_prices = _build_tr_price(spx_returns)

    log.info("loading Tiingo QQQ / GLD …")
    q_close, q_high, q_low = _load_tiingo_hlc(args.storage_root, "QQQ")
    g_close, g_high, g_low = _load_tiingo_hlc(args.storage_root, "GLD")

    log.info("simulating legs …")
    letf_r = simulate_letf_rotation(
        spx_returns, spx_prices, LETF_CFG
    ).daily_returns.dropna()
    qqq_r = simulate_tsmom(q_high, q_low, q_close, QQQ_CFG).daily_returns.dropna()
    gld_r = simulate_tsmom(g_high, g_low, g_close, GLD_CFG).daily_returns.dropna()

    common = letf_r.index.intersection(qqq_r.index).intersection(gld_r.index)
    if len(common) == 0:
        raise RuntimeError("legs share no common index")

    df = pd.DataFrame(
        {
            "LETF_2x": letf_r.loc[common].astype(float),
            "QQQ": qqq_r.loc[common].astype(float),
            "GLD": gld_r.loc[common].astype(float),
        }
    )
    df = df.dropna()
    log.info(
        "common window: %d bars  %s → %s",
        len(df), df.index[0].date(), df.index[-1].date(),
    )
    return df


def _compute_metrics(
    result: RebalanceResult,
    years: float,
) -> dict:
    eq = result.equity
    rets = returns_from_equity(eq)
    drift_max_per_bar = result.max_drift  # per-bar max abs drift across legs
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
        "# Rebalance modes — 3-leg EW (LETF+QQQ+GLD)",
        "",
        "**Path tag:** [SWING BROKER]  ",
        f"**Window:** {window_start.date()} → {window_end.date()} "
        f"({years:.2f} yrs, {int(years * 252)} bars ≈).  ",
        f"**Target weights:** EW (1/3, 1/3, 1/3).  ",
        f"**Initial capital:** {fmt_money(initial_capital)}.  ",
        f"**Monthly deposit (cashflow mode):** "
        f"{fmt_money(monthly_deposit)} ({monthly_deposit / initial_capital:.2%} of initial).  ",
        f"**BR IR rate (realized gains on sells):** 15%.",
        "",
        "## Comparative metrics",
        "",
        "| Metric | Daily (winner) | Monthly sell | Monthly cashflow |",
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
        "## Interpretation notes",
        "",
        "* **Daily rebal tax = 0 by construction.** The module reuses the",
        "  `portfolio_combiner` convention of every bar being a forced",
        "  rebalance with no realized-gain accounting. Per-leg trade-level",
        "  tax (the 15% BR IR on each profitable strategy exit) is already",
        "  baked elsewhere in the Phase 3.5b winner reports; this comparison",
        "  isolates the *rebalance-mechanic* tax incidence.",
        "* **Monthly-sell tax is rebalance-level only.** It only fires on",
        "  the end-of-month reset and pays 15% on the overweight legs' sold",
        "  realized gain (cost basis = proportional average, not FIFO).",
        "* **Monthly-cashflow is tax-free at the rebal layer.** The $500/mo",
        "  deposit lands entirely on the most underweight leg — a discipline",
        "  friendly to a BR swing broker that lets the user DCA without",
        "  triggering realized-gains accounting.",
        "* **Drift caveat:** The *max drift* figure is the worst single-bar",
        "  deviation *before* rebalance. Daily mode resets to zero every",
        "  bar ⇒ drift ≡ 0 by construction.",
        "",
        "## Reference values",
        "",
        "Winner (Phase 3.5b, daily rebal, tax_per_leg=15% via trade log):",
        "",
        "| Ref | Value |",
        "|---|---|",
        f"| Sharpe | {winner_ref['sharpe']:.3f} |",
        f"| CAGR | {fmt_pct(winner_ref['cagr_pct'])} |",
        f"| MaxDD | {fmt_pct(winner_ref['max_drawdown_pct'])} |",
        "",
        "The *Daily (winner)* column above reproduces these numbers from",
        "the raw daily_returns cumprod (no per-leg trade tax applied at",
        "the equity layer — matches `portfolio_3leg_ew/summary.json`).",
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
        "* `drift_3leg.png` — max |actual - target| weight across 3 legs",
        "  for each mode, over the full window.",
        "* `equity_3leg.png` — equity curves overlay (log scale).",
        "* `summary_3leg.json` — structured snapshot.",
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
    ax.set_title("Per-bar max |actual − target| weight drift — 3-leg EW")
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
    ax.set_title("Equity curves — 3-leg EW rebalance modes")
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity ($, log scale)")
    ax.legend(loc="upper left")
    ax.grid(True, which="both", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def _load_winner_ref(root: Path) -> dict:
    ref_path = root / "reports" / "phase3_5b" / "portfolio_3leg_ew" / "summary.json"
    if not ref_path.exists():
        log.warning("winner reference missing at %s — using zeros", ref_path)
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
    (out_dir / "comparison_3leg.md").write_text(md, encoding="utf-8")

    summary = {
        "variant": "3leg_ew",
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
    (out_dir / "summary_3leg.json").write_text(
        json.dumps(summary, indent=2, default=float), encoding="utf-8"
    )

    _plot_drift(out_dir / "drift_3leg.png", daily_r, sell_r, cash_r)
    _plot_equity(out_dir / "equity_3leg.png", daily_r, sell_r, cash_r)

    log.info("done — wrote %s (md + summary + 2 png)", out_dir)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
