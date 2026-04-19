#!/usr/bin/env python3
"""Phase 3.5b addendum — LETF EMA100/0%/Lx leverage-variant report generator.

Parametrized runner for Tasks B2 (L=2.5) and B3 (L=3.0). Emits the
6-artefact standard report pack under
``reports/phase3_5b/variants/letf_leverage_comparison/letf_ema100_<slug>/``
for a single synthetic LETF leverage level, matching the layout of the
canonical ``reports/phase3_5b/letf_rotation_ema100_2x/`` winner bundle
plus a ``flags.md`` narrative that is mandatory for the addendum.

Addendum rule
-------------
Runs end-to-end and **emits the report regardless of gate verdicts**
(per ``specs/phase_3_5b_addendum_operational.md`` §0 and memory.md
constraint §Regra de ouro). Failures become FLAGs, not hard stops:

* L=2.5 → ⚠️ SINTÉTICO — no real 2.5x SPY ETF exists. Implementation
  requires daily-rebalanced swap or 2x+1x stacking.
* L=3.0 → ⚠️ FAIL MaxDD — Gayed B1c gate demanded MaxDD_window ≤ 25%
  per rolling WF window. 3x routinely breaches in 2008 and 2020.

Phase 3 winner (L=2.0, `reports/phase3_5b/letf_rotation_ema100_2x/`)
is **immutable** (memory constraint §4) — this script does not
regenerate it, only references it when computing WF MaxDD deltas for
the side-by-side table rendered by Task B3.

Output layout
-------------
::

    reports/phase3_5b/variants/letf_leverage_comparison/
        letf_ema100_<slug>/
            standard_report.md
            trade_log.csv
            trade_log.md
            summary.json
            equity_curve.png
            flags.md

where ``<slug>`` is ``2_5x`` for L=2.5 and ``3x`` for L=3.0 (matches
the canonical ``2x`` naming).

Citations
---------
* LETF synthetic formula: ``[leverage_for_the_long_run, p.16]``.
* Leverage levels tested (1.25x / 2x / 3x): ``[leverage_for_the_long_run,
  p.17, Table 8]``.
* MaxDD 25% per WF window gate: Phase 3 Lead B1c
  (``reports/letf_rotation_b1c_verdict.json``) + Investment Mandate §5.
* Winner-immutability constraint: memory.md §Constraints invioláveis §4.
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

log = logging.getLogger("phase3_5b.letf_leverage_variant")


WF_WINDOWS_PHASE3 = [
    ("WF1", "1970-01-02", "1977-12-30"),
    ("WF2", "1978-01-02", "1985-12-31"),
    ("WF3", "1986-01-02", "1993-12-31"),
    ("WF4", "1994-01-03", "2001-12-31"),
    ("WF5", "2002-01-02", "2009-12-31"),
    ("WF6", "2010-01-04", "2017-12-29"),
    ("WF7", "2018-01-02", "2025-12-31"),
    ("WF8", "2026-01-02", "2026-04-14"),
]
"""Phase 3 Lead B1c walk-forward windows (8 blocks, 8y each ending
with a partial 2026 block). Source: grid `letf_rotation_b1c.py`
canonical WF schedule. Used here to compute per-window MaxDD so B3's
sub-index can tabulate 2x/2.5x/3x side-by-side."""


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--leverage",
        type=float,
        required=True,
        help="Daily leverage factor (e.g. 2.5 or 3.0).",
    )
    ap.add_argument(
        "--output-root",
        type=Path,
        default=Path(
            "reports/phase3_5b/variants/letf_leverage_comparison"
        ),
    )
    ap.add_argument("--initial-capital", type=float, default=100_000.0)
    ap.add_argument("--spx-start", default="1970-01-02")
    ap.add_argument("--spx-end", default="2026-04-14")
    ap.add_argument("--spx-cutoff", default="2001-05-14")
    ap.add_argument("--tax-rate", type=float, default=0.15)
    ap.add_argument("--annual-fee", type=float, default=0.01)
    ap.add_argument("--log-level", default="INFO")
    return ap.parse_args(argv)


def _leverage_slug(leverage: float) -> str:
    """Return the filesystem slug for the leverage level.

    Matches canonical ``letf_rotation_ema100_2x`` pattern — 2.0 → "2x",
    2.5 → "2_5x", 3.0 → "3x". Fractional levels use underscore-separator
    to stay filesystem-safe across git / mac / linux.
    """
    if float(leverage).is_integer():
        return f"{int(leverage)}x"
    whole = int(leverage)
    frac = int(round((leverage - whole) * 10))
    return f"{whole}_{frac}x"


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
        label=title,
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


def _max_drawdown_pct(equity: pd.Series) -> float:
    eq = equity.dropna()
    if eq.empty:
        return 0.0
    peak = eq.cummax()
    dd = eq / peak - 1.0
    return float(dd.min())


def _wf_maxdd_table(
    equity: pd.Series,
    windows: list[tuple[str, str, str]],
) -> list[dict]:
    """Per walk-forward window MaxDD (as negative fraction, rescaled per
    window so each window has its own peak) — matches B1c grid semantics
    where WF windows are evaluated in isolation for MaxDD gating."""
    rows = []
    for name, lo, hi in windows:
        lo_ts, hi_ts = pd.Timestamp(lo), pd.Timestamp(hi)
        segment = equity.loc[(equity.index >= lo_ts) & (equity.index <= hi_ts)]
        if segment.empty:
            rows.append({"window": name, "start": lo, "end": hi,
                         "n_bars": 0, "maxdd_pct": None})
            continue
        rows.append({
            "window": name,
            "start": lo,
            "end": hi,
            "n_bars": int(len(segment)),
            "maxdd_pct": _max_drawdown_pct(segment),
        })
    return rows


def _render_flags(
    leverage: float,
    summary: dict,
    wf_rows: list[dict],
) -> str:
    slug = _leverage_slug(leverage)
    cagr_pct = summary["metrics"]["cagr_pct"] * 100.0
    sharpe = summary["metrics"]["sharpe"]
    maxdd_pct = summary["metrics"]["max_drawdown_pct"] * 100.0
    ir_vs_spy = summary["vs_spy"]["information_ratio"]
    maxdd_gate_breach = any(
        (r["maxdd_pct"] is not None and r["maxdd_pct"] < -0.25)
        for r in wf_rows
    )

    lines: list[str] = [
        f"# Flags — LETF EMA100/0%/{slug} synthetic "
        "(Phase 3.5b addendum Task B)",
        "",
    ]

    if not float(leverage).is_integer():
        lines += [
            "## ⚠️ FLAG: SINTÉTICO",
            "",
            f"L={leverage:.1f}x **does not correspond to any listed US LETF**",
            "(2024-04). The industry offers 1x/2x/3x only (SSO=2x, UPRO=3x,",
            "SPXL=3x) — there is no 2.5x ETF. Implementation options:",
            "",
            "1. **Daily-rebalanced total-return swap** (Pepperstone/IBKR",
            "   swap desk). Feasible for accounts ≥ $25k with sign-off.",
            "2. **Stacking 2x + 1x** (50% SSO + 50% SPY). Gets L_effective",
            "   = 1.5x, not 2.5x — NOT equivalent.",
            "3. **Stacking 2x + 3x** in weights (0.5, 0.5) → L=2.5x but",
            "   each leg rebalances daily. Tracking error vs theoretical",
            "   ~0.5-1.0% annual drag above Gayed's 1% flat-fee baseline.",
            "",
            "The backtest below uses the theoretical Gayed formula",
            "`r_synth[t] = L·r_SPX_TR[t] - 0.01/252` "
            "(`[leverage_for_the_long_run, p.16]`). Real-world deployment",
            "must budget for the implementation gap above.",
            "",
        ]

    lines += [
        "## Gate verdicts (reference only — addendum does not gate)",
        "",
        "| Gate | Threshold | Measured | Verdict |",
        "|------|-----------|----------|---------|",
        f"| CAGR > CDI (~13%/yr) | > 13% | {cagr_pct:.2f}% | "
        f"{'✅ PASS' if cagr_pct > 13 else '⚠️ FAIL'} |",
        f"| Sharpe > 1.0 | > 1.0 | {sharpe:.3f} | "
        f"{'✅ PASS' if sharpe > 1.0 else '⚠️ FAIL'} |",
        f"| Full-window MaxDD | ≤ 25% | {maxdd_pct:.2f}% | "
        f"{'✅ PASS' if maxdd_pct <= 25.0 else '⚠️ FAIL'} |",
        f"| WF MaxDD ≤ 25% (all windows) | ≤ 25% | see table | "
        f"{'⚠️ FAIL' if maxdd_gate_breach else '✅ PASS'} |",
        "",
        "## Walk-forward MaxDD per window (8-block Phase 3 B1c schedule)",
        "",
        "| Window | Start | End | Bars | MaxDD % | Flag |",
        "|--------|-------|-----|------|---------|------|",
    ]
    for r in wf_rows:
        if r["maxdd_pct"] is None:
            line = f"| {r['window']} | {r['start']} | {r['end']} | 0 | — | — |"
        else:
            mdd = r["maxdd_pct"] * 100.0
            flag = "⚠️ FAIL" if r["maxdd_pct"] < -0.25 else "✅ PASS"
            line = (
                f"| {r['window']} | {r['start']} | {r['end']} | "
                f"{r['n_bars']} | {mdd:.2f}% | {flag} |"
            )
        lines.append(line)
    lines += [
        "",
        "## Summary vs Phase 3 winner (L=2x)",
        "",
        "Reference: `reports/phase3_5b/letf_rotation_ema100_2x/summary.json`",
        "(full-window CAGR 44.69%, Sharpe 1.848, MaxDD 20.55%).",
        "",
        f"- This variant CAGR: **{cagr_pct:.2f}%**",
        f"- This variant Sharpe: **{sharpe:.3f}**",
        f"- This variant MaxDD: **{maxdd_pct:.2f}%**",
        f"- This variant IR vs SPY: **{ir_vs_spy:.3f}**",
        "",
        "Higher leverage buys marginal CAGR at disproportionate MaxDD cost",
        "(Gayed p.17, Table 8 — 3x outperforms 2x on CAGR by <5pp but",
        "doubles worst-decade MaxDD). The 2x winner is the",
        "Sharpe-maximising pick; higher leverage is risk-seeking.",
        "",
        "## Citations",
        "",
        "- Synthetic LETF formula: `[leverage_for_the_long_run, p.16]`.",
        "- Leverage grid (1.25/2/3): `[leverage_for_the_long_run, p.17,",
        "  Table 8]`.",
        "- WF MaxDD ≤ 25% gate: Phase 3 B1c",
        "  (`reports/letf_rotation_b1c_verdict.json`).",
        "- Winner immutability rule: memory.md §Constraints §4.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    slug = _leverage_slug(args.leverage)
    out_dir = args.output_root / f"letf_ema100_{slug}"
    out_dir.mkdir(parents=True, exist_ok=True)
    log.info("output → %s", out_dir)

    log.info("loading SPX TR stitched series …")
    spx_returns = load_spx_tr_daily(
        start=args.spx_start,
        end=args.spx_end,
        cutoff_date=pd.Timestamp(args.spx_cutoff),
    )
    spx_prices = _build_tr_price(spx_returns)
    log.info(
        "SPX TR: %d bars %s → %s",
        len(spx_returns),
        spx_returns.index[0].date(),
        spx_returns.index[-1].date(),
    )

    cfg = LETFRotationConfig(
        filter="EMA",
        lookback=100,
        band_pct=0.0,
        leverage=float(args.leverage),
        gold_weight=0.0,
        annual_fee=args.annual_fee,
        tax_rate=args.tax_rate,
    )
    log.info(
        "simulating LETF rotation EMA100/0%%/%s (fee=%.2f%%, tax=%.0f%%)",
        slug,
        args.annual_fee * 100.0,
        args.tax_rate * 100.0,
    )
    result = simulate_letf_rotation(spx_returns, spx_prices, cfg)
    trades = letf_get_trades(
        result,
        spx_returns,
        cfg,
        asset_label=f"LETF_{slug}",
        notional=args.initial_capital,
    )
    equity = _scale_equity(result.equity, args.initial_capital)

    log.info("loading SPY benchmark …")
    spy_series = load_spy_series()
    spy_bench = build_spy_benchmark(
        spy_series,
        initial_capital=args.initial_capital,
        window_start=pd.Timestamp(equity.index[0]),
        window_end=pd.Timestamp(equity.index[-1]),
    )
    comparison = compare_vs_spy(equity, spy_bench.equity_curve)

    strategy_name = f"LETF Rotation EMA100/0%/{slug} synthetic"
    params = (
        f"filter=EMA lookback=100 band=0.00 leverage={args.leverage:.2f} "
        f"off=CASH annual_fee={args.annual_fee:.3f} "
        f"tax={args.tax_rate:.2f} synthetic_formula=gayed_p16"
    )
    report = build_standard_report(
        equity=equity,
        trades=trades,
        strategy_name=strategy_name,
        params=params,
    )

    md = render_markdown(
        report, spy_benchmark=spy_bench, spy_comparison=comparison
    )
    (out_dir / "standard_report.md").write_text(md, encoding="utf-8")

    csv_text, md_text = render_trade_log(
        trades,
        initial_capital=args.initial_capital,
        tax_rate=args.tax_rate,
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

    wf_rows = _wf_maxdd_table(equity, WF_WINDOWS_PHASE3)

    summary = {
        "strategy": strategy_name,
        "params": params,
        "window_start": pd.Timestamp(equity.index[0]).strftime("%Y-%m-%d"),
        "window_end": pd.Timestamp(equity.index[-1]).strftime("%Y-%m-%d"),
        "initial_capital": args.initial_capital,
        "tax_rate": args.tax_rate,
        "leverage": float(args.leverage),
        "leverage_slug": slug,
        "synthetic": True,
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
        "wf_maxdd": wf_rows,
        "n_trades": report.n_trades,
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, default=float), encoding="utf-8"
    )

    _plot_equity_curve(
        out_dir / "equity_curve.png",
        title=strategy_name,
        strategy_equity=equity,
        spy_equity=spy_bench.equity_curve,
    )

    flags_md = _render_flags(args.leverage, summary, wf_rows)
    (out_dir / "flags.md").write_text(flags_md, encoding="utf-8")

    log.info(
        "done — %d trades, Sharpe=%.3f, CAGR=%.2f%%, MaxDD=%.2f%% → %s",
        report.n_trades,
        report.sharpe,
        report.cagr_pct * 100.0,
        report.max_drawdown_pct * 100.0,
        out_dir,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
