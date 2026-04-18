#!/usr/bin/env python3
"""Phase 3.5b addendum — Task C4: threshold rebalance sweep for 3-leg EW.

Extends Task C2 (which benchmarked daily / monthly_sell / monthly_cashflow)
with **drift-triggered** rebalancing. The same 3-leg winner (LETF EMA100/2x
+ QQQ Donchian 20/10 + GLD Donchian 40/20) is run across six cadences:

* ``threshold_5pp``  — rebalance when any leg drifts > 5 pp from target.
* ``threshold_10pp`` — rebalance when any leg drifts > 10 pp.
* ``threshold_15pp`` — rebalance when any leg drifts > 15 pp.
* ``threshold_20pp`` — rebalance when any leg drifts > 20 pp.
* ``annual_only``    — monthly_sell mechanic with ``rebalance_freq="Y"``
                       (end-of-year only).
* ``never``          — pure buy-and-hold (``threshold_pp=1e9``).

All sell-based modes apply the 15 % BR IR on realized gains
``[advances_fin_ml, p.275-278]`` / Investment Mandate §4.

Output
------
``reports/phase3_5b/variants/rebalance_modes/threshold_sweep.md`` +
``threshold_sweep_summary.json`` + ``threshold_sweep_events.png``.

Citations
---------
* Threshold rebalancing as institutional standard:
  ``[advances_fin_ml, p.275-278]``.
* Daily reset baseline (Task C2 reference): ``[advances_fin_ml,
  p.298-299]``.
* BR 15 % IR on realized gains: Investment Mandate §4.

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
    apply_monthly_sell_rebalance,
    apply_threshold_rebalance,
)
from ai_trade.backtest.strategies.letf_rotation import (
    LETFRotationConfig,
    simulate_letf_rotation,
)
from ai_trade.backtest.strategies.tsmom import (
    TSMOMConfig,
    simulate_tsmom,
)

log = logging.getLogger("phase3_5b.task_c4")

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
    drift_max_per_bar = result.max_drift
    max_abs_drift = float(result.drift.max().max())
    mean_max_drift = float(drift_max_per_bar.mean())

    tax_total = float(result.total_tax_paid)
    n_events = result.n_taxable_events
    # Events/yr counts TaxableEvents — each rebal may produce 1 event per
    # overweight leg. Divide by legs-per-event (~1 in 3-leg ≈ 1.0-1.5) to
    # estimate DARFs/yr ≈ rebal-dates/yr. Here we report raw events.
    # Each unique rebalance *date* counts as one DARF, so we also compute:
    unique_event_dates = len({ev.date for ev in result.taxable_events})

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
        "rebalance_dates": int(unique_event_dates),
        "rebalance_dates_per_year": (
            float(unique_event_dates / years) if years > 0 else 0.0
        ),
        "total_tax_paid": tax_total,
        "tax_per_year": float(tax_total / years) if years > 0 else 0.0,
    }


def _run_sweep(
    rdf: pd.DataFrame,
    initial_capital: float,
    tax_rate: float,
) -> dict[str, tuple[RebalanceResult, dict]]:
    years = len(rdf) / 252.0
    log.info("running sweep (years≈%.2f) …", years)

    results: dict[str, tuple[RebalanceResult, dict]] = {}

    daily_r = apply_daily_rebalance(rdf, TARGET_WEIGHTS, initial_capital)
    results["daily"] = (daily_r, _compute_metrics(daily_r, years))

    for pp in (5.0, 10.0, 15.0, 20.0):
        key = f"threshold_{int(pp)}pp"
        r = apply_threshold_rebalance(
            rdf,
            TARGET_WEIGHTS,
            threshold_pp=pp,
            initial_capital=initial_capital,
            tax_rate=tax_rate,
        )
        results[key] = (r, _compute_metrics(r, years))
        log.info(
            "%-16s events=%3d  ev/yr=%.2f  dates/yr=%.2f  Sharpe=%.3f  IR/yr=$%.0f",
            key,
            r.n_taxable_events,
            results[key][1]["taxable_events_per_year"],
            results[key][1]["rebalance_dates_per_year"],
            results[key][1]["sharpe"],
            results[key][1]["tax_per_year"],
        )

    annual_r = apply_monthly_sell_rebalance(
        rdf,
        TARGET_WEIGHTS,
        initial_capital=initial_capital,
        tax_rate=tax_rate,
        rebalance_freq="Y",
    )
    results["annual_only"] = (annual_r, _compute_metrics(annual_r, years))

    never_r = apply_threshold_rebalance(
        rdf,
        TARGET_WEIGHTS,
        threshold_pp=1e9,  # effectively infinite → never triggers
        initial_capital=initial_capital,
        tax_rate=tax_rate,
    )
    results["never"] = (never_r, _compute_metrics(never_r, years))

    return results


def _render_md(
    window_start: pd.Timestamp,
    window_end: pd.Timestamp,
    years: float,
    initial_capital: float,
    tax_rate: float,
    results: dict[str, tuple[RebalanceResult, dict]],
) -> str:
    def fmt_money(v: float) -> str:
        return f"${v:,.0f}"

    def fmt_pct(v: float) -> str:
        return f"{v * 100:.2f}%"

    baseline_sharpe = results["daily"][1]["sharpe"]

    order = [
        "daily",
        "threshold_5pp",
        "threshold_10pp",
        "threshold_15pp",
        "threshold_20pp",
        "annual_only",
        "never",
    ]
    labels = {
        "daily": "daily (winner)",
        "threshold_5pp": "threshold 5pp",
        "threshold_10pp": "threshold 10pp",
        "threshold_15pp": "threshold 15pp",
        "threshold_20pp": "threshold 20pp",
        "annual_only": "annual only (Y)",
        "never": "never (BH)",
    }

    header = [
        "# Threshold rebalance sweep — 3-leg EW (LETF+QQQ+GLD)",
        "",
        "**Path tag:** [SWING BROKER]  ",
        "**Phase:** 3.5b-addendum, Task C4 (drift-triggered variant).  ",
        f"**Window:** {window_start.date()} → {window_end.date()} "
        f"({years:.2f} yrs).  ",
        "**Target weights:** EW (1/3, 1/3, 1/3).  ",
        f"**Initial capital:** {fmt_money(initial_capital)}.  ",
        f"**BR IR rate (realized gains on sells):** "
        f"{tax_rate * 100:.0f}%.",
        "",
        "## Cadences",
        "",
        "| Mode | Rule |",
        "|---|---|",
        "| daily            | reset to target every bar (no rebal-layer tax) |",
        "| threshold 5pp    | rebal only when any leg drifts > 5 pp |",
        "| threshold 10pp   | rebal only when any leg drifts > 10 pp |",
        "| threshold 15pp   | rebal only when any leg drifts > 15 pp |",
        "| threshold 20pp   | rebal only when any leg drifts > 20 pp |",
        "| annual only      | monthly-sell mechanic, freq='Y' (year-end only) |",
        "| never            | pure buy-and-hold (threshold 1e9) |",
        "",
        "## Comparative metrics",
        "",
        "| Mode | CAGR | Sharpe | ΔSharpe vs daily | MaxDD | "
        "Max drift | Mean drift | Events | Dates/yr | IR paid / yr | "
        "Total IR |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    rows = []
    for key in order:
        _, m = results[key]
        delta_sharpe = m["sharpe"] - baseline_sharpe
        rows.append(
            f"| {labels[key]} | {fmt_pct(m['cagr'])} | {m['sharpe']:.3f} | "
            f"{delta_sharpe:+.3f} | {fmt_pct(m['max_drawdown'])} | "
            f"{fmt_pct(m['max_abs_drift'])} | "
            f"{fmt_pct(m['mean_max_drift'])} | {m['taxable_events']} | "
            f"{m['rebalance_dates_per_year']:.2f} | "
            f"{fmt_money(m['tax_per_year'])} | "
            f"{fmt_money(m['total_tax_paid'])} |"
        )

    interp = [
        "",
        "## DARFs/yr — operational translation",
        "",
        "A Brazilian retail investor must file a DARF for each month in",
        "which realized capital gains exceed zero. **DARFs/yr ≈ unique",
        "rebalance dates per year**, because multiple legs sold on the",
        "same date consolidate to a single monthly filing. The 'Dates/yr'",
        "column above is therefore the practical DARF burden from the",
        "rebalance layer — the **inside-leg** trade-level DARFs (~12/yr",
        "from LETF regime flips + QQQ/GLD Donchian breakouts) are",
        "additive and unchanged across cadences.",
        "",
        "| Mode | DARFs/yr (rebal layer) | Total DARFs/yr est. |",
        "|---|---|---|",
    ]
    for key in order:
        _, m = results[key]
        dates_yr = m["rebalance_dates_per_year"]
        # Assume ~12 inside-leg tax-events/yr across the 3 legs (baseline,
        # documented in the Phase 3.5b winner summary).
        total_est = dates_yr + 12.0
        interp.append(f"| {labels[key]} | {dates_yr:.2f} | {total_est:.1f} |")

    # Recommendation narrative (computed from metrics).
    best_threshold = max(
        ("threshold_5pp", "threshold_10pp", "threshold_15pp", "threshold_20pp"),
        key=lambda k: results[k][1]["sharpe"],
    )
    best_thresh_sharpe = results[best_threshold][1]["sharpe"]
    best_thresh_dates = results[best_threshold][1]["rebalance_dates_per_year"]
    never_sharpe = results["never"][1]["sharpe"]
    annual_sharpe = results["annual_only"][1]["sharpe"]
    annual_dates = results["annual_only"][1]["rebalance_dates_per_year"]

    footer = [
        "",
        "## Interpretation",
        "",
        "* **Higher thresholds → fewer events, higher drift.** The",
        "  5 → 20 pp progression trades tax events for weight drift; at",
        "  20 pp the rebalance layer contributes only a handful of",
        "  events over the full ~21-year window.",
        "* **`never` (pure BH)** is the natural lower bound: zero",
        "  rebalance-layer tax, max drift at the maximum observed value.",
        "  Compare its Sharpe to the thresholded variants to see the",
        "  risk-budget erosion from abandoning rebalance.",
        "* **Best threshold (by Sharpe):** `"
        f"{labels[best_threshold]}` at "
        f"Sharpe={best_thresh_sharpe:.3f}, "
        f"{best_thresh_dates:.2f} dates/yr. "
        "This is the operational compromise point.",
        "* **Annual-only** incurs ~1 DARF/yr from the rebal layer; its",
        f"  Sharpe ({annual_sharpe:.3f}) vs `never` ({never_sharpe:.3f})",
        "  quantifies the value of the single end-of-year reset.",
        "",
        "## Operational recommendation",
        "",
        f"For a BR retail swing investor using the 3-leg EW winner, the",
        f"`{labels[best_threshold]}` cadence minimises DARFs/yr from the",
        f"rebalance layer to ~{best_thresh_dates:.1f} while preserving",
        f"{(best_thresh_sharpe / baseline_sharpe) * 100:.1f}% of the",
        f"winner's daily Sharpe. It is the recommended **fallback** for",
        f"users who find daily rebalance operationally prohibitive. The",
        f"**production default remains daily rebalance on the 3-leg**",
        f"winner, per the Phase 3.5b summary; this sweep documents a",
        f"principled, lower-friction alternative rather than a new winner.",
        "",
        "## Citations",
        "",
        "* Threshold rebalancing as institutional practice:",
        "  `[advances_fin_ml, p.275-278]`.",
        "* Daily reset baseline: `[advances_fin_ml, p.298-299]`.",
        "* Drift vs tax tradeoff framing: `[leverage_for_the_long_run,",
        "  p.17, Table 8]`.",
        "* BR 15% IR on realized gains: Investment Mandate §4.",
        "",
        "## Artefacts",
        "",
        "* `threshold_sweep_summary.json` — structured snapshot.",
        "* `threshold_sweep_events.png` — events/yr vs threshold plot.",
        "",
    ]

    return "\n".join(header + rows + interp + footer)


def _plot_events(
    path: Path,
    results: dict[str, tuple[RebalanceResult, dict]],
) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    order = ["threshold_5pp", "threshold_10pp", "threshold_15pp",
             "threshold_20pp", "annual_only", "never"]
    labels = {
        "threshold_5pp": "5pp",
        "threshold_10pp": "10pp",
        "threshold_15pp": "15pp",
        "threshold_20pp": "20pp",
        "annual_only": "annual",
        "never": "never",
    }
    xs = [labels[k] for k in order]
    dates_yr = [results[k][1]["rebalance_dates_per_year"] for k in order]
    sharpes = [results[k][1]["sharpe"] for k in order]

    fig, ax1 = plt.subplots(figsize=(9, 4.8))
    bars = ax1.bar(xs, dates_yr, color="#1f6feb", alpha=0.75,
                   label="Rebal dates / yr")
    ax1.set_ylabel("Rebalance dates / yr", color="#1f6feb")
    ax1.tick_params(axis="y", labelcolor="#1f6feb")
    ax1.set_xlabel("Cadence")

    ax2 = ax1.twinx()
    ax2.plot(xs, sharpes, color="#e85d75", marker="o", linewidth=1.4,
             label="Sharpe")
    ax2.axhline(results["daily"][1]["sharpe"], color="#444",
                linestyle=":", linewidth=0.9, label="daily Sharpe")
    ax2.set_ylabel("Sharpe", color="#e85d75")
    ax2.tick_params(axis="y", labelcolor="#e85d75")

    ax1.set_title("Task C4 — DARFs/yr vs Sharpe across cadences")
    ax1.grid(True, alpha=0.25, axis="y")
    lines1, labs1 = ax1.get_legend_handles_labels()
    lines2, labs2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labs1 + labs2, loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


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

    results = _run_sweep(rdf, args.initial_capital, args.tax_rate)

    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    md = _render_md(
        window_start=window_start,
        window_end=window_end,
        years=years,
        initial_capital=args.initial_capital,
        tax_rate=args.tax_rate,
        results=results,
    )
    (out_dir / "threshold_sweep.md").write_text(md, encoding="utf-8")

    summary = {
        "variant": "3leg_ew_threshold_sweep",
        "window_start": window_start.strftime("%Y-%m-%d"),
        "window_end": window_end.strftime("%Y-%m-%d"),
        "n_bars": n_bars,
        "years": years,
        "initial_capital": args.initial_capital,
        "tax_rate": args.tax_rate,
        "target_weights": TARGET_WEIGHTS,
        "modes": {k: v[1] for k, v in results.items()},
    }
    (out_dir / "threshold_sweep_summary.json").write_text(
        json.dumps(summary, indent=2, default=float), encoding="utf-8"
    )

    _plot_events(out_dir / "threshold_sweep_events.png", results)

    log.info("done — wrote %s (md + summary + png)", out_dir)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
