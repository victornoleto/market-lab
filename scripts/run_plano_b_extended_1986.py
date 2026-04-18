#!/usr/bin/env python3
"""Task X2 — Plano B 3-leg EW on extended 1986-2026 window via testfol.io.

Re-runs the **current production winner** (LETF EMA100 band0 lev2x +
QQQ Donchian 20/10 + GLD Donchian 40/20) over the full testfol.io
SPYSIM / QQQSIM / GLDSIM history (1986-01-02 → 2026-04-17, 40 yr)
and compares the equity curve to SPYSIM buy&hold.

**This is a supplementary stress test**, not a replacement baseline.
Results feed ``reports/plano_b_extended_window/`` and do NOT retroactively
invalidate the gate-passing verdict established on 2004-2026 in
``reports/phase3_5b/PRODUCTION.md``.

Caveats explicitly documented with the output:

1. **Close-only Donchian.** testfol.io exports only close-equivalent
   equity curves (no HLC), so Donchian signals trigger on close
   breakouts rather than canonical high/low breakouts. Drops some
   sensitivity to intraday spikes; direction of the approximation is
   "slightly less whippy".
2. **Modelled, not measured.** Pre-1999 QQQSIM and pre-2004 GLDSIM are
   testfol.io simulations from index returns + ETF drag, not live
   ETF prices.
3. **Pre-1999 QQQ not retail-tradeable.** NDX was institutional-only
   pre-QQQ IPO 1999-03-10.
4. **Modern-era costs only.** We apply the same 15 bps round-trip used
   post-2010; discount-broker commissions were 50-100 bps pre-2000.
   Result is therefore optimistic for the pre-2000 leg — flagged.

Emits under ``reports/plano_b_extended_window/``:

* ``equity_vs_spy.png`` — strategy vs SPYSIM buy&hold, log-scale.
* ``drawdown_vs_spy.png`` — underwater curves.
* ``summary.json`` — metrics table + caveat block.
* ``rebalance_events.csv`` — cross-leg rebals fired.

Citations
---------
* Winner configs frozen: ``reports/phase3_5b/PRODUCTION.md`` §1.
* Threshold rebalance mechanics: ``[advances_fin_ml, p.275-278]``.
* testfol.io as simulation source: Phase 3.5b Task 7a.
* LETF rotation canonical (EMA strict cross): ``[leverage_for_the_long_run, p.8, p.13]``.
* Donchian 20/40 canonical: ``[trading_systems_methods, p.353]``.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from ai_trade.backtest.data.testfolio_loader import (
    load_testfolio_returns,
    load_testfolio_series,
)
from ai_trade.backtest.metrics.rebalance_modes import apply_threshold_rebalance
from ai_trade.backtest.strategies.letf_rotation import (
    LETFRotationConfig,
    simulate_letf_rotation,
)
from ai_trade.backtest.strategies.tsmom import TSMOMConfig, simulate_tsmom

log = logging.getLogger("plano_b_extended")

LETF_CFG = LETFRotationConfig(
    filter="EMA", lookback=100, band_pct=0.0, leverage=2.0, gold_weight=0.0
)
QQQ_CFG = TSMOMConfig(entry_lookback=20, exit_lookback=10)
GLD_CFG = TSMOMConfig(entry_lookback=40, exit_lookback=20)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--output-dir", type=Path,
                    default=Path("reports/plano_b_extended_window"))
    ap.add_argument("--initial-capital", type=float, default=100_000.0)
    ap.add_argument("--threshold-pp", type=float, default=10.0,
                    help="User-selected production default (Phase 3.5b post-review).")
    ap.add_argument("--tax-rate", type=float, default=0.15)
    ap.add_argument("--log-level", default="INFO")
    return ap.parse_args(argv)


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
    strat_eq: pd.Series,
    spy_eq: pd.Series,
    strat_m: dict,
    spy_m: dict,
    threshold_pp: float,
) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        strat_eq.index, strat_eq.values,
        label=(f"Plano B 3-leg EW (thr {threshold_pp:g}pp) — "
               f"CAGR {strat_m['cagr_pct']:.2f}%  Sharpe {strat_m['sharpe']:.2f}  "
               f"MaxDD {strat_m['max_drawdown_pct']:.2f}%"),
        color="#1f6feb", linewidth=1.3,
    )
    ax.plot(
        spy_eq.index, spy_eq.values,
        label=(f"SPYSIM buy&hold — "
               f"CAGR {spy_m['cagr_pct']:.2f}%  Sharpe {spy_m['sharpe']:.2f}  "
               f"MaxDD {spy_m['max_drawdown_pct']:.2f}%"),
        color="#8b949e", linewidth=1.1, linestyle="--",
    )
    # Mark major stress events.
    for date_s, label in [
        ("1987-10-19", "Black Monday"),
        ("2000-03-24", "dot-com peak"),
        ("2008-09-15", "Lehman"),
        ("2020-02-19", "COVID"),
        ("2022-01-03", "2022 drawdown"),
    ]:
        ts = pd.Timestamp(date_s)
        if strat_eq.index[0] <= ts <= strat_eq.index[-1]:
            ax.axvline(ts, color="#d4691a", linewidth=0.5,
                       linestyle=":", alpha=0.6)
            ax.text(ts, ax.get_ylim()[1] * 0.97, label,
                    rotation=90, fontsize=7, alpha=0.7,
                    verticalalignment="top")
    ax.set_yscale("log")
    ax.set_title(
        f"Plano B 3-leg EW — extended window stress test via testfol.io  "
        f"({strat_m['start']} → {strat_m['end']}, {strat_m['years']}y)"
    )
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity (USD, log scale)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, which="both", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "equity_vs_spy.png", dpi=130)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 4.5))
    for eq, color, label in (
        (strat_eq, "#1f6feb",
         f"Plano B (MaxDD {strat_m['max_drawdown_pct']:.1f}%)"),
        (spy_eq, "#8b949e",
         f"SPYSIM B&H (MaxDD {spy_m['max_drawdown_pct']:.1f}%)"),
    ):
        peak = eq.cummax()
        dd_pct = (peak - eq) / peak * -100.0
        ax.fill_between(eq.index, dd_pct.values, 0.0,
                        alpha=0.35, color=color, label=label)
    ax.set_title(
        "Drawdown underwater (extended 1986-2026 via testfol.io)"
    )
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

    log.info("loading testfol.io cache …")
    spy = load_testfolio_series("SPYSIM")
    qqq = load_testfolio_series("QQQSIM")
    gld = load_testfolio_series("GLDSIM")
    log.info("SPYSIM %d bars  QQQSIM %d bars  GLDSIM %d bars  "
             "common %s → %s", len(spy), len(qqq), len(gld),
             spy.index[0].date(), spy.index[-1].date())

    log.info("simulating LETF rotation EMA100/2x on SPYSIM …")
    # simulate_letf_rotation requires returns and prices share an index.
    # testfol.io equity starts at a fixed $10k → day-0 return is 0, not NaN.
    spy_returns = spy.pct_change().fillna(0.0)
    letf = simulate_letf_rotation(spy_returns, spy, LETF_CFG)
    log.info("  LETF daily returns: %d bars (warmup=%d)",
             len(letf.daily_returns.dropna()), LETF_CFG.lookback)

    log.info("simulating QQQ Donchian 20/10 on QQQSIM (close-only HLC) …")
    qqq_sim = simulate_tsmom(qqq, qqq, qqq, QQQ_CFG)
    log.info("simulating GLD Donchian 40/20 on GLDSIM (close-only HLC) …")
    gld_sim = simulate_tsmom(gld, gld, gld, GLD_CFG)

    rdf = pd.DataFrame({
        "SSO": letf.daily_returns,
        "QQQ": qqq_sim.daily_returns,
        "GLD": gld_sim.daily_returns,
    }).dropna()
    log.info("common 3-leg window: %d bars  %s → %s",
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
    log.info("rebal events: %d  total rebal-layer tax: $%.2f",
             result.n_taxable_events, result.total_tax_paid)

    # SPYSIM buy&hold benchmark on the same window (strategy window wins).
    spy_window = spy.loc[
        (spy.index >= result.equity.index[0])
        & (spy.index <= result.equity.index[-1])
    ]
    spy_equity = args.initial_capital * spy_window / float(spy_window.iloc[0])
    spy_equity.name = "SPYSIM_buy_hold"

    strat_m = _metrics(result.equity)
    spy_m = _metrics(spy_equity)

    log.info("=== 3-leg EW vs SPYSIM B&H (1986-2026) ===")
    log.info("  Strategy  CAGR %.2f%%  Sharpe %.3f  MaxDD %.2f%%  "
             "Final $%s",
             strat_m["cagr_pct"], strat_m["sharpe"],
             strat_m["max_drawdown_pct"],
             f"{strat_m['final_equity']:,.0f}")
    log.info("  SPYSIM    CAGR %.2f%%  Sharpe %.3f  MaxDD %.2f%%  "
             "Final $%s",
             spy_m["cagr_pct"], spy_m["sharpe"],
             spy_m["max_drawdown_pct"],
             f"{spy_m['final_equity']:,.0f}")
    log.info("  Δ CAGR +%.2f pp  Δ Sharpe +%.3f  Δ MaxDD %+.1f pp",
             strat_m["cagr_pct"] - spy_m["cagr_pct"],
             strat_m["sharpe"] - spy_m["sharpe"],
             strat_m["max_drawdown_pct"] - spy_m["max_drawdown_pct"])

    _plot(args.output_dir, result.equity, spy_equity,
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
            "data_source": "testfol.io SPYSIM/QQQSIM/GLDSIM",
        },
        "strategy": strat_m,
        "spy_buy_hold_SPYSIM": spy_m,
        "excess": {
            "cagr_pp": round(strat_m["cagr_pct"] - spy_m["cagr_pct"], 2),
            "sharpe_delta": round(strat_m["sharpe"] - spy_m["sharpe"], 3),
            "maxdd_delta_pp": round(
                strat_m["max_drawdown_pct"] - spy_m["max_drawdown_pct"], 2),
        },
        "rebalance_events": result.n_taxable_events,
        "rebalance_tax_paid_usd": round(result.total_tax_paid, 2),
        "caveats": [
            "Supplementary stress test — does NOT replace the gate-passing "
            "2004-2026 verdict in PRODUCTION.md.",
            "Donchian uses close-only breakout (testfol.io has no HLC).",
            "Pre-1999 QQQSIM & pre-2004 GLDSIM are simulated, not measured.",
            "Pre-1999 QQQ was not retail-tradeable — signal validity only.",
            "Modern-era costs (15 bps) applied; pre-2000 costs were 50-100 bps.",
        ],
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    log.info("wrote artefacts → %s", args.output_dir)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
