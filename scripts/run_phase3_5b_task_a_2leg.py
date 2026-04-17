#!/usr/bin/env python3
"""Phase 3.5b addendum — Task A: 2-leg LETF+QQQ EW full report.

Produces the 5-artefact standard report pack for the 2-leg EW blend of
the two Path B [SWING BROKER] winners (LETF rotation EMA100/2x +
QQQ Donchian 20/10), on the longest common window QQQ allows
(2001-05-14 → 2026-04-14, 6266 daily bars).

Phase 3 Lead A3c already ran this config and rejected it at the A3c
gate (DR full=1.124 < 1.2 threshold). This script exists to **show
all** metrics end-to-end, not to re-gate — the addendum's rule is
"run to completion, flag failures in flags.md".

Output directory
----------------
``reports/phase3_5b/variants/letf_qqq_2leg_ew/``

Artefacts
---------
* ``standard_report.md`` — backtesting.py-style metrics + SPY benchmark
  + Strategy-vs-SPY comparison.
* ``trade_log.csv`` / ``trade_log.md`` — aggregated per-leg trades,
  scaled to leg_notional = initial_capital / 2.
* ``summary.json`` — machine-readable snapshot with blend metadata.
* ``equity_curve.png`` — log-scale strategy + SPY benchmark.
* ``flags.md`` — decision narrative explaining DR FAIL and the 3-leg
  vs 2-leg tradeoff per ``specs/phase_3_5b_addendum_operational.md``
  §Task A.

Citations
---------
* Blend weights 50/50 (naive, Σ-estimation-error immune):
  ``[advances_fin_ml, p.298-299]``.
* DR formula (Choueifaty-Coignard 2008): ``[advances_fin_ml, p.310]``.
* Path B 15% BR tax per profitable leg-trade: Investment Mandate §4.
* QQQ Donchian winner: jornada
  ``2026-04-17-0120-a3b-tsmom-donchian-per-asset-PASS.md``.
* LETF EMA100/2x winner: jornada
  ``2026-04-17-0055-b1c-letf-rotation-gates-PASS.md``.
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from ai_trade.backtest.data.spx_tr_loader import load_spx_tr_daily
from ai_trade.backtest.data.tiingo_storage import TiingoStorage
from ai_trade.backtest.grid.portfolio_3leg import aggregate_leg_trades
from ai_trade.backtest.grid.portfolio_combiner import (
    align_returns,
    blend_equal_weight,
    diversification_ratio,
)
from ai_trade.backtest.metrics.standard_report import (
    Trade,
    build_spy_benchmark,
    build_standard_report,
    compare_vs_spy,
    load_spy_series,
    render_markdown,
    render_trade_log,
)
from ai_trade.backtest.strategies.letf_rotation import (
    LETFRotationConfig,
    get_trades as letf_get_trades,
    simulate_letf_rotation,
)
from ai_trade.backtest.strategies.tsmom import (
    TSMOMConfig,
    get_trades as tsmom_get_trades,
    simulate_tsmom,
)

log = logging.getLogger("phase3_5b.task_a")

LETF_WINNER_CFG = LETFRotationConfig(
    filter="EMA",
    lookback=100,
    band_pct=0.0,
    leverage=2.0,
    gold_weight=0.0,
)
QQQ_WINNER_CFG = TSMOMConfig(entry_lookback=20, exit_lookback=10)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/phase3_5b/variants/letf_qqq_2leg_ew"),
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
    price = (1.0 + returns).cumprod() * 100.0
    price.name = "spx_tr_price"
    return price


def _scale_equity(equity_unit: pd.Series, initial_capital: float) -> pd.Series:
    if len(equity_unit) == 0:
        raise ValueError("empty equity series")
    e0 = float(equity_unit.iloc[0])
    if e0 <= 0:
        raise ValueError(f"equity[0]={e0} non-positive")
    return initial_capital * equity_unit / e0


def _scale_trades(trades: list[Trade], notional: float) -> list[Trade]:
    return [
        Trade(
            asset=t.asset,
            entry_date=t.entry_date,
            exit_date=t.exit_date,
            entry_price=t.entry_price,
            exit_price=t.exit_price,
            notional=notional,
            direction=t.direction,
        )
        for t in trades
    ]


def _filter_trades_to_window(
    trades: list[Trade],
    window_start: pd.Timestamp,
    window_end: pd.Timestamp,
) -> list[Trade]:
    return [
        t
        for t in trades
        if pd.Timestamp(t.entry_date) >= window_start
        and pd.Timestamp(t.exit_date) <= window_end
    ]


def _plot_equity_curve(
    path: Path,
    title: str,
    strategy_equity: pd.Series,
    spy_equity: pd.Series,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        strategy_equity.index,
        strategy_equity.values,
        label="2-leg LETF+QQQ EW",
        color="#1f6feb",
        linewidth=1.2,
    )
    ax.plot(
        spy_equity.index,
        spy_equity.values,
        label="SPY buy&hold",
        color="#8b949e",
        linewidth=1.0,
        linestyle="--",
    )
    ax.set_yscale("log")
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity (BRL, log scale)")
    ax.legend(loc="upper left")
    ax.grid(True, which="both", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def _render_flags(
    summary: dict,
    blend_meta: dict,
    baseline_3leg_sharpe_oos: float | None = None,
) -> str:
    """Emit flags.md narrative per spec §Task A."""
    dr_full = blend_meta["dr_full"]
    dr_is = blend_meta["dr_is"]
    rho = blend_meta["pearson_full"]
    sharpe_full = summary["metrics"]["sharpe"]
    cagr_pct = summary["metrics"]["cagr_pct"] * 100
    maxdd_pct = summary["metrics"]["max_drawdown_pct"]
    ir = summary["vs_spy"]["information_ratio"]

    lines = [
        "# Flags — 2-leg LETF+QQQ EW (Phase 3.5b addendum Task A)",
        "",
        "## Gate verdicts",
        "",
        "| Gate | Threshold | Measured | Verdict |",
        "|------|-----------|----------|---------|",
        f"| Diversification Ratio (full) | > 1.20 | {dr_full:.3f} | ⚠️ **FAIL** |",
        f"| Diversification Ratio (IS) | > 1.20 | {dr_is:.3f} | ⚠️ **FAIL** |",
        f"| Pearson ρ(LETF, QQQ) | — | {rho:.3f} | — (doubling-down) |",
        "",
        "## Why DR FAIL",
        "",
        "The Diversification Ratio (Choueifaty-Coignard 2008,",
        "`[advances_fin_ml, p.310]`) is `DR = (Σ wᵢ σᵢ) / σ_portfolio`. It",
        "measures how much portfolio vol is reduced relative to the",
        "weighted-average leg vol. DR = 1 iff legs are perfectly correlated;",
        "the Phase 3 A3c gate demanded DR > 1.20 (20% vol compression).",
        "",
        f"With ρ={rho:.3f} (both legs long US equity — LETF riding the",
        "S&P, QQQ riding the Nasdaq-100, which is a subset of S&P), the",
        "compression is mechanically bounded. Adding a second long-equity",
        "US leg is **doubling-down on a single factor** (US large-cap",
        "growth), not genuine diversification across factors.",
        "",
        "## Why ship the report anyway",
        "",
        "The 2-leg blend *does* beat the best single leg on OOS Sharpe",
        "(A3c iter 37 measured 2.098 vs LETF-only 1.990, +0.108). There's",
        "an additive edge — it's just not a *diversification* edge in the",
        "HRP/IVP sense. The addendum rule (`specs/phase_3_5b_addendum_",
        "operational.md` §0) is run-to-completion: show all metrics, flag",
        "failures, let the user compare against the 3-leg default.",
        "",
        "## Full-window metrics (this run)",
        "",
        "| Metric | 2-leg LETF+QQQ EW |",
        "|--------|-------------------|",
        f"| CAGR | {cagr_pct:.2f}% |",
        f"| Sharpe (full window) | {sharpe_full:.3f} |",
        f"| MaxDD | {maxdd_pct*100:.2f}% |",
        f"| Information Ratio vs SPY | {ir:.3f} |",
        "",
        "## Comparison vs 3-leg default (Phase 3.5b winner)",
        "",
        "Reference: `reports/phase3_5b/portfolio_3leg_ew/summary.json` —",
        "the 3-leg EW {LETF+QQQ+GLD} blend is the production default.",
        "",
        "Expected shape from A3c/A3d verdicts:",
        "",
        "* 2-leg OOS Sharpe ≈ 2.098 vs 3-leg OOS Sharpe ≈ 2.251 → 3-leg",
        "  wins by ~7% on OOS Sharpe.",
        "* 2-leg DR=1.12 vs 3-leg DR>1.30 (GLD is the decorrelator).",
        "* 2-leg MaxDD typically worse than 3-leg (GLD dampens equity",
        "  drawdowns during 2008-09, 2020-03, 2022).",
        "",
        "**Decision:** 2-leg is a sub-optimal simplification when GLD is",
        "tradable on the user's broker. Deploy only if (a) broker blocks",
        "GLD or (b) user explicitly prefers pure-equity exposure and",
        "accepts the higher MaxDD.",
        "",
        "## Citations",
        "",
        "* DR formula: `[advances_fin_ml, p.310]`.",
        "* Naive EW immunity to Σ-estimation error: `[advances_fin_ml,",
        "  p.298-299]`.",
        "* IVP/HRP tradeoffs used as rationale for DR gate:",
        "  `[advances_fin_ml, p.302-313, ch.16]`.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    log.info("loading SPX TR stitched series …")
    spx_returns = load_spx_tr_daily(
        start=args.spx_start,
        end=args.spx_end,
        cutoff_date=pd.Timestamp(args.spx_cutoff),
    )
    spx_prices = _build_tr_price(spx_returns)

    log.info("loading Tiingo QQQ …")
    q_close, q_high, q_low = _load_tiingo_hlc(args.storage_root, "QQQ")

    log.info("loading SPY benchmark …")
    spy_series = load_spy_series()

    log.info("simulating LETF rotation EMA100/2x …")
    letf_result = simulate_letf_rotation(spx_returns, spx_prices, LETF_WINNER_CFG)
    letf_trades = letf_get_trades(
        letf_result,
        spx_returns,
        LETF_WINNER_CFG,
        asset_label="LETF_2x",
        notional=args.initial_capital,
    )

    log.info("simulating QQQ Donchian 20/10 …")
    qqq_result = simulate_tsmom(q_high, q_low, q_close, QQQ_WINNER_CFG)
    qqq_trades = tsmom_get_trades(
        qqq_result,
        q_close,
        asset_label="QQQ",
        notional=args.initial_capital,
    )

    log.info("blending 50/50 EW on common daily returns …")
    letf_daily = letf_result.daily_returns.dropna()
    qqq_daily = qqq_result.daily_returns.dropna()
    blend = blend_equal_weight(letf_daily, qqq_daily)

    # Diversification ratio on the aligned common-window series.
    a, b = align_returns(letf_daily, qqq_daily)
    dr_full = diversification_ratio(a, b, 0.5, 0.5)
    pearson_full = float(pd.concat([a, b], axis=1).corr().iloc[0, 1])
    # IS window (same convention as A3c/A3d: IS 60% / OOS 25% / Stress 15%)
    total_n = len(a)
    is_end_idx = int(total_n * 0.60)
    is_end_ts = a.index[is_end_idx - 1]
    dr_is = diversification_ratio(
        a.loc[a.index <= is_end_ts],
        b.loc[b.index <= is_end_ts],
        0.5,
        0.5,
    )
    log.info(
        "  blend common-window: %d bars %s → %s  ρ=%.3f  DR_full=%.3f  DR_IS=%.3f",
        total_n,
        a.index[0].date(),
        a.index[-1].date(),
        pearson_full,
        dr_full,
        dr_is,
    )

    port_equity_unit = (1.0 + blend).cumprod()
    port_equity = _scale_equity(port_equity_unit, args.initial_capital)

    port_window_start = pd.Timestamp(blend.index[0])
    port_window_end = pd.Timestamp(blend.index[-1])
    letf_trades_pw = _filter_trades_to_window(
        letf_trades, port_window_start, port_window_end
    )
    qqq_trades_pw = _filter_trades_to_window(
        qqq_trades, port_window_start, port_window_end
    )

    # Per-leg notional = initial_capital / 2 (EW).
    leg_notional = args.initial_capital / 2.0
    port_trades = aggregate_leg_trades(
        [
            ("LETF_2x", _scale_trades(letf_trades_pw, leg_notional)),
            ("QQQ", _scale_trades(qqq_trades_pw, leg_notional)),
        ]
    )
    log.info(
        "  kept %d/%d LETF trades, %d/%d QQQ trades (aligned to blend window)",
        len(letf_trades_pw),
        len(letf_trades),
        len(qqq_trades_pw),
        len(qqq_trades),
    )

    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_standard_report(
        equity=port_equity,
        trades=port_trades,
        strategy_name="Portfolio 2-leg EW (LETF+QQQ)",
        params="weights=(1/2,1/2) rebalance=daily tax_per_leg=15%",
    )
    spy_bench = build_spy_benchmark(
        spy_series,
        initial_capital=args.initial_capital,
        window_start=port_window_start,
        window_end=port_window_end,
    )
    comparison = compare_vs_spy(port_equity, spy_bench.equity_curve)

    md = render_markdown(report, spy_benchmark=spy_bench, spy_comparison=comparison)
    (out_dir / "standard_report.md").write_text(md, encoding="utf-8")

    csv_text, md_text = render_trade_log(
        port_trades, initial_capital=args.initial_capital, tax_rate=args.tax_rate
    )
    (out_dir / "trade_log.csv").write_text(csv_text, encoding="utf-8")
    (out_dir / "trade_log.md").write_text(md_text, encoding="utf-8")

    metrics_serialisable: dict = {}
    for k, v in asdict(report).items():
        if k == "equity_curve":
            continue
        if isinstance(v, pd.Timestamp):
            metrics_serialisable[k] = v.isoformat()
        elif isinstance(v, (int, float, np.floating, np.integer)):
            metrics_serialisable[k] = float(v)
        else:
            metrics_serialisable[k] = v

    summary = {
        "strategy": "Portfolio 2-leg EW (LETF+QQQ)",
        "params": "weights=(1/2,1/2) rebalance=daily tax_per_leg=15%",
        "window_start": port_window_start.strftime("%Y-%m-%d"),
        "window_end": port_window_end.strftime("%Y-%m-%d"),
        "initial_capital": args.initial_capital,
        "tax_rate": args.tax_rate,
        "metrics": metrics_serialisable,
        "spy_benchmark": {
            "return_pct": spy_bench.return_pct,
            "cagr_pct": spy_bench.cagr_pct,
            "max_drawdown_pct": spy_bench.max_drawdown_pct,
            "sharpe": spy_bench.sharpe,
        },
        "vs_spy": {
            "excess_return_pct": comparison.excess_return_pct,
            "excess_cagr_pct": comparison.excess_cagr_pct,
            "delta_max_dd_pct": comparison.delta_max_dd_pct,
            "information_ratio": comparison.information_ratio,
            "correlation": comparison.correlation,
            "beta": comparison.beta,
        },
        "blend_meta": {
            "pearson_full": pearson_full,
            "dr_full": dr_full,
            "dr_is": dr_is,
            "leg_names": ["LETF_2x", "QQQ"],
            "weights": [0.5, 0.5],
        },
        "n_trades": report.n_trades,
        "n_bars": total_n,
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, default=float), encoding="utf-8"
    )

    _plot_equity_curve(
        out_dir / "equity_curve.png",
        title="Portfolio 2-leg EW (LETF+QQQ)",
        strategy_equity=port_equity,
        spy_equity=spy_bench.equity_curve,
    )

    blend_meta = {
        "dr_full": dr_full,
        "dr_is": dr_is,
        "pearson_full": pearson_full,
    }
    flags_md = _render_flags(summary, blend_meta)
    (out_dir / "flags.md").write_text(flags_md, encoding="utf-8")

    log.info(
        "done — wrote %s (%d trades, Sharpe=%.3f, CAGR=%.2f%%, MaxDD=%.2f%%, DR=%.3f)",
        out_dir,
        report.n_trades,
        report.sharpe,
        report.cagr_pct * 100.0,
        report.max_drawdown_pct * 100.0,
        dr_full,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
