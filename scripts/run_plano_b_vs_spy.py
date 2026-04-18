#!/usr/bin/env python3
"""Plano B 3-leg EW (production config) vs SPY buy&hold.

Runs the production winner — LETF EMA100/2x + QQQ Donchian 20/10 +
GLD Donchian 40/20 — with **threshold-5pp rebalance** (the default
recommended in ``reports/phase3_5b/PRODUCTION.md`` §2, not the
theoretical daily ceiling) and compares the resulting equity curve
against SPY buy-and-hold on the same window.

Emits under ``reports/plano_b_vs_spy/``:

* ``equity_vs_spy.png`` — log-scale equity comparison (strategy vs SPY).
* ``drawdown_vs_spy.png`` — underwater curves side-by-side.
* ``summary.json`` — CAGR / Sharpe / MaxDD for both + spread.
* ``rebalance_events.csv`` — every cross-leg rebal that fired.

Usage
-----
::

    .venv/bin/python scripts/run_plano_b_vs_spy.py \\
        --threshold-pp 5.0 --initial-capital 100000

Citations
---------
* Winner configs + threshold 5pp default:
  ``reports/phase3_5b/PRODUCTION.md`` (Phase 3.5b Task C4).
* Threshold-rebalance mechanics: ``[advances_fin_ml, p.275-278]``.
* LETF rotation (EMA strict cross, band 0): ``[leverage_for_the_long_run, p.8, p.13]``.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from ai_trade.backtest.data.spx_tr_loader import load_spx_tr_daily
from ai_trade.backtest.data.tiingo_storage import TiingoStorage
from ai_trade.backtest.metrics.rebalance_modes import apply_threshold_rebalance
from ai_trade.backtest.metrics.standard_report import (
    build_spy_benchmark,
    load_spy_series,
)
from ai_trade.backtest.strategies.letf_rotation import (
    LETFRotationConfig,
    simulate_letf_rotation,
)
from ai_trade.backtest.strategies.tsmom import TSMOMConfig, simulate_tsmom

log = logging.getLogger("plano_b_vs_spy")

LETF_CFG = LETFRotationConfig(
    filter="EMA", lookback=100, band_pct=0.0, leverage=2.0, gold_weight=0.0
)
QQQ_CFG = TSMOMConfig(entry_lookback=20, exit_lookback=10)
GLD_CFG = TSMOMConfig(entry_lookback=40, exit_lookback=20)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--output-dir", type=Path,
                    default=Path("reports/plano_b_vs_spy"))
    ap.add_argument("--initial-capital", type=float, default=100_000.0)
    ap.add_argument("--threshold-pp", type=float, default=5.0,
                    help="Drift in percentage points that triggers rebal.")
    ap.add_argument("--tax-rate", type=float, default=0.15)
    ap.add_argument("--storage-root", type=Path, default=Path("data/tiingo"))
    ap.add_argument("--spx-start", default="1970-01-02")
    ap.add_argument("--spx-end", default="2026-04-14")
    ap.add_argument("--spx-cutoff", default="2001-05-14")
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
        if "adj_close" in df.columns else raw_close
    )
    scale = (adj_close / raw_close).replace([pd.NA, pd.NaT], 1.0).fillna(1.0)
    close = adj_close.dropna()
    high = (df["high"].astype(float) * scale).loc[close.index].dropna()
    low = (df["low"].astype(float) * scale).loc[close.index].dropna()
    common = close.index.intersection(high.index).intersection(low.index)
    return close.loc[common], high.loc[common], low.loc[common]


def _tr_price(returns: pd.Series) -> pd.Series:
    price = (1.0 + returns).cumprod() * 100.0
    price.name = "spx_tr_price"
    return price


def _metrics(equity: pd.Series, periods: int = 252) -> dict:
    e = equity.sort_index().astype(float)
    rets = e.pct_change().dropna()
    v0, vT = float(e.iloc[0]), float(e.iloc[-1])
    years = (e.index[-1] - e.index[0]).days / 365.25
    cagr = (vT / v0) ** (1.0 / years) - 1.0 if years > 0 and v0 > 0 else 0.0
    vol = float(rets.std()) * np.sqrt(periods) if len(rets) > 1 else 0.0
    sharpe = (float(rets.mean()) * periods) / vol if vol > 0 else 0.0
    peak = e.cummax()
    dd = (peak - e) / peak
    max_dd = float(dd.max())
    return {
        "start": e.index[0].strftime("%Y-%m-%d"),
        "end": e.index[-1].strftime("%Y-%m-%d"),
        "years": round(years, 2),
        "total_return_pct": round((vT / v0 - 1.0) * 100.0, 2),
        "cagr_pct": round(cagr * 100.0, 2),
        "sharpe": round(sharpe, 3),
        "max_drawdown_pct": round(max_dd * 100.0, 2),
        "final_equity": round(vT, 2),
    }


def _plot(
    out_dir: Path,
    strat_eq: pd.Series,
    spy_eq: pd.Series,
    strat_m: dict,
    spy_m: dict,
    threshold_pp: float,
) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Panel 1 — log-scale equity comparison
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(
        strat_eq.index, strat_eq.values,
        label=(f"Plano B 3-leg EW (threshold {threshold_pp:.0f}pp) — "
               f"CAGR {strat_m['cagr_pct']:.2f}%  Sharpe {strat_m['sharpe']:.2f}  "
               f"MaxDD {strat_m['max_drawdown_pct']:.2f}%"),
        color="#1f6feb", linewidth=1.3,
    )
    ax.plot(
        spy_eq.index, spy_eq.values,
        label=(f"SPY buy&hold — "
               f"CAGR {spy_m['cagr_pct']:.2f}%  Sharpe {spy_m['sharpe']:.2f}  "
               f"MaxDD {spy_m['max_drawdown_pct']:.2f}%"),
        color="#8b949e", linewidth=1.1, linestyle="--",
    )
    ax.set_yscale("log")
    ax.set_title(
        f"Plano B (SSO + QQQ + GLD) vs SPY buy&hold  "
        f"— {strat_m['start']} → {strat_m['end']} ({strat_m['years']}y)"
    )
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity (USD, log scale)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, which="both", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "equity_vs_spy.png", dpi=130)
    plt.close(fig)

    # Panel 2 — drawdown underwater
    fig, ax = plt.subplots(figsize=(11, 4))
    for eq, color, label in (
        (strat_eq, "#1f6feb", f"Plano B (MaxDD {strat_m['max_drawdown_pct']:.1f}%)"),
        (spy_eq, "#8b949e", f"SPY B&H (MaxDD {spy_m['max_drawdown_pct']:.1f}%)"),
    ):
        peak = eq.cummax()
        dd_pct = (peak - eq) / peak * -100.0
        ax.fill_between(eq.index, dd_pct.values, 0.0,
                        alpha=0.35, color=color, label=label)
    ax.set_title("Drawdown (underwater curve)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown (%)")
    ax.legend(loc="lower left", fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "drawdown_vs_spy.png", dpi=130)
    plt.close(fig)


def _write_events_csv(path: Path, events: list) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "leg", "proceeds_usd", "cost_basis_sold_usd",
                    "realized_gain_usd", "tax_paid_usd"])
        for e in events:
            w.writerow([
                pd.Timestamp(e.date).strftime("%Y-%m-%d"),
                e.leg,
                round(float(e.proceeds), 2),
                round(float(e.cost_basis_sold), 2),
                round(float(e.realized_gain), 2),
                round(float(e.tax_paid), 2),
            ])


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)

    log.info("loading SPX TR stitched series …")
    spx_returns = load_spx_tr_daily(
        start=args.spx_start,
        end=args.spx_end,
        cutoff_date=pd.Timestamp(args.spx_cutoff),
    )
    spx_prices = _tr_price(spx_returns)
    log.info("SPX TR: %d bars %s → %s",
             len(spx_returns),
             spx_returns.index[0].date(),
             spx_returns.index[-1].date())

    log.info("loading Tiingo HLC for QQQ, GLD …")
    q_close, q_high, q_low = _load_tiingo_hlc(args.storage_root, "QQQ")
    g_close, g_high, g_low = _load_tiingo_hlc(args.storage_root, "GLD")
    log.info("QQQ: %d bars  GLD: %d bars", len(q_close), len(g_close))

    log.info("simulating LETF rotation EMA100/2x …")
    letf = simulate_letf_rotation(spx_returns, spx_prices, LETF_CFG)
    log.info("simulating QQQ Donchian 20/10 …")
    qqq = simulate_tsmom(q_high, q_low, q_close, QQQ_CFG)
    log.info("simulating GLD Donchian 40/20 …")
    gld = simulate_tsmom(g_high, g_low, g_close, GLD_CFG)

    # Align on common window (portfolio tradeable only when all 3 legs exist).
    rdf = pd.DataFrame({
        "SSO": letf.daily_returns,
        "QQQ": qqq.daily_returns,
        "GLD": gld.daily_returns,
    }).dropna()
    log.info("common window: %d bars  %s → %s",
             len(rdf), rdf.index[0].date(), rdf.index[-1].date())

    log.info("applying threshold-%.1fpp rebalance (tax %.0f%%) …",
             args.threshold_pp, args.tax_rate * 100.0)
    result = apply_threshold_rebalance(
        returns_df=rdf,
        target_weights={"SSO": 1 / 3, "QQQ": 1 / 3, "GLD": 1 / 3},
        threshold_pp=args.threshold_pp,
        initial_capital=args.initial_capital,
        tax_rate=args.tax_rate,
    )
    log.info("rebal events: %d  total tax paid: $%.2f",
             result.n_taxable_events, result.total_tax_paid)

    log.info("loading SPY buy&hold benchmark …")
    spy_series = load_spy_series()
    spy_bench = build_spy_benchmark(
        spy_series,
        initial_capital=args.initial_capital,
        window_start=pd.Timestamp(result.equity.index[0]),
        window_end=pd.Timestamp(result.equity.index[-1]),
    )

    strat_m = _metrics(result.equity)
    spy_m = _metrics(spy_bench.equity_curve)

    log.info("=== Plano B 3-leg EW (threshold %.1fpp) ===", args.threshold_pp)
    log.info("  CAGR    %.2f%% (SPY %.2f%%  ⇒ +%.2f pp)",
             strat_m["cagr_pct"], spy_m["cagr_pct"],
             strat_m["cagr_pct"] - spy_m["cagr_pct"])
    log.info("  Sharpe  %.3f  (SPY %.3f)",
             strat_m["sharpe"], spy_m["sharpe"])
    log.info("  MaxDD   %.2f%% (SPY %.2f%%)",
             strat_m["max_drawdown_pct"], spy_m["max_drawdown_pct"])
    log.info("  Final   $%s  (SPY $%s)",
             f"{strat_m['final_equity']:,.0f}",
             f"{spy_m['final_equity']:,.0f}")

    _plot(args.output_dir, result.equity, spy_bench.equity_curve,
          strat_m, spy_m, args.threshold_pp)
    _write_events_csv(args.output_dir / "rebalance_events.csv",
                      result.taxable_events)

    summary = {
        "config": {
            "threshold_pp": args.threshold_pp,
            "tax_rate": args.tax_rate,
            "initial_capital": args.initial_capital,
            "legs": {
                "SSO": f"LETF EMA{LETF_CFG.lookback}/band"
                       f"{LETF_CFG.band_pct:.2f}/lev{LETF_CFG.leverage}x",
                "QQQ": f"Donchian {QQQ_CFG.entry_lookback}/"
                       f"{QQQ_CFG.exit_lookback}",
                "GLD": f"Donchian {GLD_CFG.entry_lookback}/"
                       f"{GLD_CFG.exit_lookback}",
            },
        },
        "strategy": strat_m,
        "spy_buy_hold": spy_m,
        "excess": {
            "cagr_pp": round(strat_m["cagr_pct"] - spy_m["cagr_pct"], 2),
            "sharpe_delta": round(strat_m["sharpe"] - spy_m["sharpe"], 3),
            "maxdd_delta_pp": round(
                strat_m["max_drawdown_pct"] - spy_m["max_drawdown_pct"], 2),
        },
        "rebalance_events": result.n_taxable_events,
        "rebalance_tax_paid_usd": round(result.total_tax_paid, 2),
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    log.info("wrote artefacts → %s", args.output_dir)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
