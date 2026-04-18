#!/usr/bin/env python3
"""Task X3 — SSO/ZROZ/GLD static risk-parity variants on 1986-2026.

Tests a fundamentally different philosophy from the current 3-leg
winner: **static strategic allocation** (no signals, just threshold
rebalance) of 2× leveraged S&P + long-duration Treasuries + gold.
Inspired by Bridgewater All Weather + Hedgefundie HFEA, but with
lower leverage (SSO 2× vs UPRO 3×) and unlevered duration (ZROZ vs
TMF 3×).

Variants tested (all 3-leg, % of portfolio):

* **SA (Super Aggressive)**  60 SSO / 20 ZROZ / 20 GLD
* **A  (Aggressive)**        50 SSO / 25 ZROZ / 25 GLD
* **M  (Moderate)**          40 SSO / 30 ZROZ / 30 GLD
* **C  (Conservative)**      30 SSO / 35 ZROZ / 35 GLD

Rebalance at threshold ``--threshold-pp`` (default 10 pp, matching
the user's preference for the tactical 3-leg).

**Critical caveats (reported in summary.json + this docstring):**

1. **No regime filter.** Unlike the tactical 3-leg (EMA100 + Donchian),
   this variant has **zero signal-driven exits**. In 2008 SSO stayed
   long and took the full -50% leveraged move.
2. **ZROZ/duration risk.** 1986-2021 was a secular disinflation regime
   (30Y UST yield 10% → 0.9%). ZROZSIM benefited enormously from this
   regime — it is NOT a guarantee of future correlation behaviour.
   2022 was the stress: ZROZSIM lost ~-47% while SSO also fell.
3. **Gate verdict pending.** This script produces descriptive metrics,
   not a PASS/FAIL verdict. The same 5-gate pipeline (CPCV/PBO/DSR/WF/
   bootstrap) used in Phase 3 b1c should be applied before any
   real-capital decision.

Output under ``reports/static_sso_zroz_gld/``:

* ``equity_vs_spy.png`` — 4 variants + SPYSIM on log scale.
* ``drawdown_vs_spy.png`` — underwater curves.
* ``summary.json`` — per-variant metrics.

Citations
---------
* Static risk-parity lineage: Bridgewater All Weather (Dalio),
  Hedgefundie Excellent Adventure (HFEA).
* LETF synthesis: ``[leverage_for_the_long_run, p.16]``.
* Threshold rebalance: ``[advances_fin_ml, p.275-278]``.
* testfol.io as long-history source: Phase 3.5b Task 7a.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from ai_trade.backtest.data.testfolio_loader import load_testfolio_series
from ai_trade.backtest.helpers.synthetic_letf import synthesize_letf_returns
from ai_trade.backtest.metrics.rebalance_modes import apply_threshold_rebalance

log = logging.getLogger("static_sso_zroz_gld")

VARIANTS: dict[str, dict[str, float]] = {
    "SA_60_20_20": {"SSO": 0.60, "ZROZ": 0.20, "GLD": 0.20},
    "A_50_25_25":  {"SSO": 0.50, "ZROZ": 0.25, "GLD": 0.25},
    "M_40_30_30":  {"SSO": 0.40, "ZROZ": 0.30, "GLD": 0.30},
    "C_30_35_35":  {"SSO": 0.30, "ZROZ": 0.35, "GLD": 0.35},
}

# Distinct colors: aggressiveness → warmer hue.
VARIANT_COLORS = {
    "SA_60_20_20": "#e11d48",
    "A_50_25_25":  "#d4691a",
    "M_40_30_30":  "#2ea043",
    "C_30_35_35":  "#1f6feb",
}

SSO_LEVERAGE = 2.0
SSO_ANNUAL_FEE = 0.01   # Gayed p.16 default for synthetic LETF drag.


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--output-dir", type=Path,
                    default=Path("reports/static_sso_zroz_gld"))
    ap.add_argument("--initial-capital", type=float, default=100_000.0)
    ap.add_argument("--threshold-pp", type=float, default=10.0)
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
    runs: list[tuple[str, pd.Series, dict, int]],
    spy_eq: pd.Series,
    spy_m: dict,
    threshold_pp: float,
) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(12, 6))
    for name, eq, m, n_rebal in runs:
        color = VARIANT_COLORS.get(name, "#333333")
        ax.plot(
            eq.index, eq.values,
            label=(f"{name} — CAGR {m['cagr_pct']:.2f}%  "
                   f"Sharpe {m['sharpe']:.2f}  "
                   f"MaxDD {m['max_drawdown_pct']:.2f}%  ({n_rebal} rebals)"),
            color=color, linewidth=1.2,
        )
    ax.plot(
        spy_eq.index, spy_eq.values,
        label=(f"SPYSIM buy&hold — CAGR {spy_m['cagr_pct']:.2f}%  "
               f"Sharpe {spy_m['sharpe']:.2f}  "
               f"MaxDD {spy_m['max_drawdown_pct']:.2f}%"),
        color="#8b949e", linewidth=1.0, linestyle="--",
    )
    for date_s, label in [
        ("1987-10-19", "Black Monday"),
        ("2000-03-24", "dot-com peak"),
        ("2008-09-15", "Lehman"),
        ("2020-02-19", "COVID"),
        ("2022-01-03", "2022"),
    ]:
        ts = pd.Timestamp(date_s)
        if spy_eq.index[0] <= ts <= spy_eq.index[-1]:
            ax.axvline(ts, color="#555555", linewidth=0.5,
                       linestyle=":", alpha=0.5)
            ax.text(ts, ax.get_ylim()[1] * 0.97, label,
                    rotation=90, fontsize=7, alpha=0.6,
                    verticalalignment="top")
    ax.set_yscale("log")
    ax.set_title(
        f"Static SSO/ZROZ/GLD — 4 variants vs SPYSIM B&H  "
        f"(threshold {threshold_pp:g}pp, {spy_m['start']} → {spy_m['end']}, "
        f"{spy_m['years']}y)"
    )
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity (USD, log scale)")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, which="both", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "equity_vs_spy.png", dpi=130)
    plt.close(fig)

    # Underwater
    fig, ax = plt.subplots(figsize=(12, 5))
    for name, eq, m, _ in runs:
        color = VARIANT_COLORS.get(name, "#333333")
        peak = eq.cummax()
        dd_pct = (peak - eq) / peak * -100.0
        ax.plot(eq.index, dd_pct.values,
                color=color, linewidth=1.0,
                label=f"{name} (MaxDD {m['max_drawdown_pct']:.1f}%)")
    peak = spy_eq.cummax()
    spy_dd = (peak - spy_eq) / peak * -100.0
    ax.fill_between(spy_eq.index, spy_dd.values, 0.0,
                    alpha=0.2, color="#8b949e",
                    label=f"SPYSIM B&H (MaxDD {spy_m['max_drawdown_pct']:.1f}%)")
    ax.set_title("Drawdown underwater — all variants + SPYSIM")
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown (%)")
    ax.legend(loc="lower left", fontsize=8)
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

    log.info("loading testfol.io cache …")
    spy = load_testfolio_series("SPYSIM")
    zroz = load_testfolio_series("ZROZSIM")
    gld = load_testfolio_series("GLDSIM")

    log.info("synthesizing SSO = 2× SPYSIM with %.1f%% annual fee drag …",
             SSO_ANNUAL_FEE * 100)
    spy_returns = spy.pct_change().fillna(0.0)
    sso_returns = synthesize_letf_returns(
        spy_returns, leverage=SSO_LEVERAGE, annual_fee=SSO_ANNUAL_FEE
    )
    zroz_returns = zroz.pct_change().fillna(0.0)
    gld_returns = gld.pct_change().fillna(0.0)

    rdf = pd.DataFrame({
        "SSO": sso_returns,
        "ZROZ": zroz_returns,
        "GLD": gld_returns,
    }).dropna()
    log.info("common window: %d bars  %s → %s",
             len(rdf), rdf.index[0].date(), rdf.index[-1].date())

    # SPYSIM buy&hold benchmark on matching window.
    spy_window = spy.loc[
        (spy.index >= rdf.index[0]) & (spy.index <= rdf.index[-1])
    ]
    spy_equity = args.initial_capital * spy_window / float(spy_window.iloc[0])
    spy_m = _metrics(spy_equity)
    log.info("SPYSIM B&H  CAGR %.2f%%  Sharpe %.3f  MaxDD %.2f%%",
             spy_m["cagr_pct"], spy_m["sharpe"], spy_m["max_drawdown_pct"])

    runs: list[tuple[str, pd.Series, dict, int]] = []
    per_variant: list[dict] = []

    for name, weights in VARIANTS.items():
        log.info("→ %s  weights=%s", name, weights)
        result = apply_threshold_rebalance(
            returns_df=rdf,
            target_weights=weights,
            threshold_pp=args.threshold_pp,
            initial_capital=args.initial_capital,
            tax_rate=args.tax_rate,
        )
        m = _metrics(result.equity)
        runs.append((name, result.equity, m, result.n_taxable_events))
        per_variant.append({
            "variant": name,
            "weights": weights,
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
        log.info("  CAGR %.2f%%  Sharpe %.3f  MaxDD %.2f%%  "
                 "rebals=%d  tax=$%.0f",
                 m["cagr_pct"], m["sharpe"], m["max_drawdown_pct"],
                 result.n_taxable_events, result.total_tax_paid)

    _plot(args.output_dir, runs, spy_equity, spy_m, args.threshold_pp)

    summary = {
        "config": {
            "threshold_pp": args.threshold_pp,
            "tax_rate": args.tax_rate,
            "initial_capital": args.initial_capital,
            "sso_synthesis": {
                "leverage": SSO_LEVERAGE,
                "annual_fee": SSO_ANNUAL_FEE,
                "source": "synthesize_letf_returns(SPYSIM)",
            },
            "data_source": "testfol.io SPYSIM/ZROZSIM/GLDSIM",
            "window": {
                "start": rdf.index[0].strftime("%Y-%m-%d"),
                "end": rdf.index[-1].strftime("%Y-%m-%d"),
                "bars": int(len(rdf)),
            },
        },
        "spy_buy_hold_SPYSIM": spy_m,
        "variants": per_variant,
        "caveats": [
            "No regime filter — leveraged SSO stays long in 2008/2000 crashes.",
            "ZROZ/duration risk — backtest window had secular disinflation; "
            "regime may not persist.",
            "Descriptive only — does NOT replace the 5-gate validation "
            "required before real-capital deployment.",
            "testfol.io ZROZSIM pre-2009 is simulated from yield curve.",
            "Modern-era costs (15 bps) applied; pre-2000 costs were higher.",
        ],
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    log.info("wrote artefacts → %s", args.output_dir)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
