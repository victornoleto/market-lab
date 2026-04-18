#!/usr/bin/env python3
"""Plano B 3-leg EW — threshold sweep vs SPY buy&hold in one chart.

Runs the production winner (LETF EMA100/2x + QQQ Donchian 20/10 + GLD
Donchian 40/20) at multiple rebalance thresholds and overlays all
equity curves on a single log-scale plot against SPY. Defaults to
{5 pp, 10 pp} — the two candidates discussed in
``reports/phase3_5b/PRODUCTION.md`` §2.

Emits under ``reports/phase3_5b/threshold_sweep_full/``:

* ``equity_vs_spy.png`` — all thresholds + SPY on one log-scale panel.
* ``drawdown_vs_spy.png`` — all thresholds + SPY underwater curves.
* ``summary.json`` — metrics table for every threshold.

Citations
---------
* Threshold rebalance decision + sweep table:
  ``reports/phase3_5b/PRODUCTION.md`` §2 (Phase 3.5b Task C4).
* ``[advances_fin_ml, p.275-278]`` — drift-triggered cadences.
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

log = logging.getLogger("plano_b_threshold_compare")

LETF_CFG = LETFRotationConfig(
    filter="EMA", lookback=100, band_pct=0.0, leverage=2.0, gold_weight=0.0
)
QQQ_CFG = TSMOMConfig(entry_lookback=20, exit_lookback=10)
GLD_CFG = TSMOMConfig(entry_lookback=40, exit_lookback=20)

# Distinct palette so overlapping curves stay legible.
PALETTE = ["#1f6feb", "#d4691a", "#2ea043", "#9333ea", "#e11d48"]


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--output-dir", type=Path,
                    default=Path("reports/phase3_5b/threshold_sweep_full"))
    ap.add_argument("--initial-capital", type=float, default=100_000.0)
    ap.add_argument("--thresholds", type=float, nargs="+",
                    default=[5.0, 10.0],
                    help="List of threshold_pp values to run.")
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
    return {
        "start": e.index[0].strftime("%Y-%m-%d"),
        "end": e.index[-1].strftime("%Y-%m-%d"),
        "years": round(years, 2),
        "total_return_pct": round((vT / v0 - 1.0) * 100.0, 2),
        "cagr_pct": round(cagr * 100.0, 2),
        "sharpe": round(sharpe, 3),
        "max_drawdown_pct": round(float(dd.max()) * 100.0, 2),
        "final_equity": round(vT, 2),
    }


def _plot(
    out_dir: Path,
    spy_eq: pd.Series,
    spy_m: dict,
    strat_runs: list[tuple[float, pd.Series, dict, int]],
) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Panel 1 — log-scale equity.
    fig, ax = plt.subplots(figsize=(12, 6))
    for i, (thr, eq, m, n_ev) in enumerate(strat_runs):
        color = PALETTE[i % len(PALETTE)]
        ax.plot(
            eq.index, eq.values,
            label=(f"Plano B threshold {thr:g}pp — "
                   f"CAGR {m['cagr_pct']:.2f}%  Sharpe {m['sharpe']:.2f}  "
                   f"MaxDD {m['max_drawdown_pct']:.2f}%  ({n_ev} rebals)"),
            color=color, linewidth=1.3,
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
        f"Plano B (SSO + QQQ + GLD) — threshold sweep vs SPY buy&hold  "
        f"— {spy_m['start']} → {spy_m['end']} ({spy_m['years']}y)"
    )
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity (USD, log scale)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, which="both", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "equity_vs_spy.png", dpi=130)
    plt.close(fig)

    # Panel 2 — drawdown underwater.
    fig, ax = plt.subplots(figsize=(12, 4.5))
    for i, (thr, eq, m, _) in enumerate(strat_runs):
        color = PALETTE[i % len(PALETTE)]
        peak = eq.cummax()
        dd_pct = (peak - eq) / peak * -100.0
        ax.plot(eq.index, dd_pct.values,
                color=color, linewidth=0.9,
                label=f"Plano B {thr:g}pp (MaxDD {m['max_drawdown_pct']:.1f}%)")
    peak = spy_eq.cummax()
    spy_dd = (peak - spy_eq) / peak * -100.0
    ax.fill_between(spy_eq.index, spy_dd.values, 0.0,
                    alpha=0.25, color="#8b949e",
                    label=f"SPY B&H (MaxDD {spy_m['max_drawdown_pct']:.1f}%)")
    ax.set_title("Drawdown (underwater curve) — all thresholds + SPY")
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown (%)")
    ax.legend(loc="lower left", fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "drawdown_vs_spy.png", dpi=130)
    plt.close(fig)


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

    log.info("loading Tiingo HLC for QQQ, GLD …")
    q_close, q_high, q_low = _load_tiingo_hlc(args.storage_root, "QQQ")
    g_close, g_high, g_low = _load_tiingo_hlc(args.storage_root, "GLD")

    log.info("simulating 3 legs …")
    letf = simulate_letf_rotation(spx_returns, spx_prices, LETF_CFG)
    qqq = simulate_tsmom(q_high, q_low, q_close, QQQ_CFG)
    gld = simulate_tsmom(g_high, g_low, g_close, GLD_CFG)
    rdf = pd.DataFrame({
        "SSO": letf.daily_returns,
        "QQQ": qqq.daily_returns,
        "GLD": gld.daily_returns,
    }).dropna()
    log.info("common window: %d bars  %s → %s",
             len(rdf), rdf.index[0].date(), rdf.index[-1].date())

    log.info("loading SPY buy&hold benchmark …")
    spy_series = load_spy_series()
    spy_bench = build_spy_benchmark(
        spy_series,
        initial_capital=args.initial_capital,
        window_start=pd.Timestamp(rdf.index[0]),
        window_end=pd.Timestamp(rdf.index[-1]),
    )
    spy_m = _metrics(spy_bench.equity_curve)

    strat_runs: list[tuple[float, pd.Series, dict, int]] = []
    per_threshold_summary: list[dict] = []
    for thr in args.thresholds:
        log.info("→ threshold %.1fpp …", thr)
        result = apply_threshold_rebalance(
            returns_df=rdf,
            target_weights={"SSO": 1 / 3, "QQQ": 1 / 3, "GLD": 1 / 3},
            threshold_pp=thr,
            initial_capital=args.initial_capital,
            tax_rate=args.tax_rate,
        )
        m = _metrics(result.equity)
        strat_runs.append((thr, result.equity, m, result.n_taxable_events))
        per_threshold_summary.append({
            "threshold_pp": thr,
            "metrics": m,
            "rebalance_events": result.n_taxable_events,
            "rebalance_tax_paid_usd": round(result.total_tax_paid, 2),
            "excess_vs_spy": {
                "cagr_pp": round(m["cagr_pct"] - spy_m["cagr_pct"], 2),
                "sharpe_delta": round(m["sharpe"] - spy_m["sharpe"], 3),
                "maxdd_delta_pp": round(
                    m["max_drawdown_pct"] - spy_m["max_drawdown_pct"], 2),
            },
        })
        log.info(
            "  CAGR %.2f%%  Sharpe %.3f  MaxDD %.2f%%  rebals=%d  tax=$%.0f",
            m["cagr_pct"], m["sharpe"], m["max_drawdown_pct"],
            result.n_taxable_events, result.total_tax_paid,
        )

    _plot(args.output_dir, spy_bench.equity_curve, spy_m, strat_runs)

    summary = {
        "config": {
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
        "spy_buy_hold": spy_m,
        "thresholds": per_threshold_summary,
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    log.info("wrote artefacts → %s", args.output_dir)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
