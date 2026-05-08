"""Shared report-rendering helpers for the real-ETF sweep studies.

The SPY-real and NDX-real studies share the same artifact layout:
  - configs.csv (aggregate metrics + gates)
  - summary.json
  - FINAL.md (ranked top-K + archetypes + narrative)
  - configs/NN_<cfg_id>/summary.md + equity.png + trades.csv

This module centralises the rendering so each study CLI is a thin
wrapper that only differs in market data + axes.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ai_trade.backtest.grid.ema_sma_threshold_grid import (
    ConfigMetrics,
    EMASMAThresholdAxes,
    GateFlags,
    cartesian_configs,
    compute_composite_scores,
    compute_config_metrics,
    evaluate_gates,
)
from ai_trade.backtest.grid.real_etf_regime_runner import (
    RealETFMarket,
    benchmark_signal_buy_hold,
    build_data_bundle,
    simulate_config_with_real_legs,
)
from ai_trade.backtest.strategies.ema_sma_threshold_educational import (
    EMASMAThresholdConfig,
    ThresholdResult,
)

TRADING_DAYS_PER_TEXT = 252


def _fmt_pct(x: float, digits: int = 2) -> str:
    if x is None or np.isnan(x) or np.isinf(x):
        return "—"
    return f"{x * 100:+.{digits}f}%"


def _fmt_num(x: float, digits: int = 2) -> str:
    if x is None or np.isnan(x) or np.isinf(x):
        return "—"
    return f"{x:.{digits}f}"


def run_one_sweep_real(
    configs: list[EMASMAThresholdConfig],
    bundle: dict,
    *,
    tax_rate: float,
    apply_gates: bool,
) -> tuple[list[ThresholdResult], list[ConfigMetrics], np.ndarray, list[GateFlags]]:
    """Run a sweep at a fixed tax_rate against the real-ETF bundle."""
    results: list[ThresholdResult] = []
    metrics: list[ConfigMetrics] = []
    for base_cfg in configs:
        cfg = replace(base_cfg, tax_rate=tax_rate)
        res = simulate_config_with_real_legs(cfg, bundle)
        results.append(res)
        metrics.append(compute_config_metrics(cfg, res))
    composite = compute_composite_scores(metrics)

    if apply_gates:
        flags = evaluate_gates(
            metrics, results,
            bundle["signal_prices"], bundle["signal_returns"],
            n_trials=len(configs),
        )
    else:
        flags = [
            GateFlags(False, False, False, False, False, False, False)
            for _ in configs
        ]
    return results, metrics, composite, flags


def _render_equity_plot(
    result_pure: ThresholdResult,
    result_tax: ThresholdResult,
    signal_prices: pd.Series,
    cfg: EMASMAThresholdConfig,
    bench_name: str,
    out_path: Path,
) -> None:
    bench_eq = signal_prices.reindex(result_pure.equity.index).ffill()
    bench_eq = bench_eq / bench_eq.iloc[0]

    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=120)
    ax.plot(result_pure.equity.index, result_pure.equity.values,
            label="Strategy (pure, tax=0)", color="#1f77b4", linewidth=1.4)
    ax.plot(result_tax.equity.index, result_tax.equity.values,
            label="Strategy (tax=15%)", color="#ff7f0e", linewidth=1.4)
    ax.plot(bench_eq.index, bench_eq.values,
            label=bench_name, color="#808080", linewidth=1.2, linestyle="--")
    ax.set_yscale("log")
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity (log, start=1.0)")
    ax.set_title(
        f"{cfg.cfg_id}  —  {cfg.filter}({cfg.lookback}) "
        f"threshold ±{cfg.threshold_pct*100:.0f}%  "
        f"buy×{cfg.buy_leverage:g}  sell×{cfg.sell_leverage:g}  (REAL ETFs)"
    )
    ax.grid(True, alpha=0.3, which="both")
    ax.legend(loc="upper left", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _write_trades_csv(
    result_pure: ThresholdResult,
    result_tax: ThresholdResult,
    out_path: Path,
) -> None:
    n = min(len(result_pure.trades), len(result_tax.trades))
    rows = []
    for k in range(n):
        tp = result_pure.trades[k]
        tt = result_tax.trades[k]
        rows.append({
            "regime": "+1 long" if tp.regime == 1 else "-1 short/cash",
            "entry_date": tp.entry_date.date().isoformat(),
            "exit_date": tp.exit_date.date().isoformat(),
            "bars_held": tp.bars_held,
            "pure_entry_equity": tp.entry_equity,
            "pure_exit_equity": tp.exit_equity,
            "pure_net_pnl_pct": tp.net_pnl_pct,
            "tax15_entry_equity": tt.entry_equity,
            "tax15_exit_equity": tt.exit_equity,
            "tax15_tax_paid": tt.tax_paid,
            "tax15_net_pnl_pct": tt.net_pnl_pct,
        })
    pd.DataFrame(rows).to_csv(out_path, index=False)


def _gate_row(label: str, passed: bool, cite: str) -> str:
    return f"| {label} | {'PASS' if passed else 'FAIL'} | `{cite}` |"


def _render_config_summary_md(
    cfg: EMASMAThresholdConfig,
    m_pure: ConfigMetrics,
    m_tax: ConfigMetrics,
    result_pure: ThresholdResult,
    result_tax: ThresholdResult,
    flags: GateFlags,
    benchmark: ConfigMetrics,
    rank: int,
    n_total: int,
    market: RealETFMarket,
    buy_ticker: str,
    out_path: Path,
) -> None:
    tax_drag = m_pure.cagr - m_tax.cagr
    tax_drag_sharpe = m_pure.sharpe - m_tax.sharpe

    n_trades = len(result_pure.trades)
    n_long = sum(1 for t in result_pure.trades if t.regime == 1)
    n_short = n_trades - n_long
    n_long_win = sum(1 for t in result_pure.trades if t.regime == 1 and t.net_pnl_pct > 0)
    n_short_win = sum(1 for t in result_pure.trades if t.regime == -1 and t.net_pnl_pct > 0)
    avg_hold_long = (
        np.mean([t.bars_held for t in result_pure.trades if t.regime == 1])
        if n_long > 0 else 0.0
    )
    avg_hold_short = (
        np.mean([t.bars_held for t in result_pure.trades if t.regime == -1])
        if n_short > 0 else 0.0
    )

    lines: list[str] = []
    lines.append(f"# Config {cfg.cfg_id} — rank {rank}/{n_total}  (REAL {market.name})\n")
    lines.append("> Real-ETF validation of the SPYSIM synth study. "
                 "Buy leg uses **real Tiingo returns**; sell leg is cash or synth inverse "
                 "(inverse LETFs absent from cache). Educational — not production.\n")

    sell_desc = (
        f"cash ({cfg.cash_rate_annual*100:.1f}% annual)"
        if cfg.sell_leverage == 0
        else f"synth ×{cfg.sell_leverage:g} inverse of {market.signal_ticker}"
    )
    lines.append("## Parameters\n")
    lines.append(
        "| param | value | source |\n|---|---|---|\n"
        f"| MA filter | {cfg.filter} | `[leverage_for_the_long_run, p.8]` |\n"
        f"| lookback | {cfg.lookback} bars | `[leverage_for_the_long_run, p.14, Table 6]` |\n"
        f"| threshold | ±{cfg.threshold_pct*100:.0f}% | `[leverage_for_the_long_run, p.11]` |\n"
        f"| buy leg | ×{cfg.buy_leverage:g} = **{buy_ticker}** (real Tiingo) | Tiingo storage |\n"
        f"| sell leg | ×{cfg.sell_leverage:g} = {sell_desc} | synth via `[p.16, fn.22]` if <0 |\n"
        f"| annual fee (synth sell only) | {cfg.fee*100:.2f}% | `[p.16, fn.23]` |\n"
        f"| switch cost | {cfg.switch_cost_bps:.0f} bps/transition | mirror `letf_rotation.py` |\n"
    )

    lines.append("## Metrics — pure vs tax=15% vs "
                 f"{market.signal_ticker} buy-hold\n")
    lines.append(
        "| metric | pure | tax=15% | "
        f"{market.signal_ticker} B&H | tax drag |\n"
        "|---|---|---|---|---|\n"
        f"| CAGR | {_fmt_pct(m_pure.cagr)} | {_fmt_pct(m_tax.cagr)} | {_fmt_pct(benchmark.cagr)} | {_fmt_pct(tax_drag)} |\n"
        f"| Sharpe | {_fmt_num(m_pure.sharpe)} | {_fmt_num(m_tax.sharpe)} | {_fmt_num(benchmark.sharpe)} | {_fmt_num(tax_drag_sharpe)} |\n"
        f"| Max Drawdown | {_fmt_pct(m_pure.max_drawdown)} | {_fmt_pct(m_tax.max_drawdown)} | {_fmt_pct(benchmark.max_drawdown)} | — |\n"
        f"| Calmar | {_fmt_num(m_pure.calmar)} | {_fmt_num(m_tax.calmar)} | {_fmt_num(benchmark.calmar)} | — |\n"
        f"| Sortino | {_fmt_num(m_pure.sortino)} | {_fmt_num(m_tax.sortino)} | {_fmt_num(benchmark.sortino)} | — |\n"
        f"| Volatility | {_fmt_pct(m_pure.volatility)} | {_fmt_pct(m_tax.volatility)} | {_fmt_pct(benchmark.volatility)} | — |\n"
        f"| n_switches | {m_pure.n_switches} | {m_tax.n_switches} | 0 | — |\n"
    )

    if m_pure.cagr > 0:
        drag_frac = tax_drag / m_pure.cagr
        lines.append(f"*Tax drag = {_fmt_pct(tax_drag)} CAGR = "
                     f"{drag_frac*100:.1f}% of the pure edge.*\n")

    lines.append("## Gates (informational; evaluated on PURE sweep, signal "
                 f"returns = real {market.signal_ticker})\n")
    lines.append(
        "| gate | verdict | citation |\n|---|---|---|\n"
        + _gate_row("G1 PBO < 0.5", flags.g1_pbo, "[advances_fin_ml, p.208-211]") + "\n"
        + _gate_row("G2 DSR p < 0.05", flags.g2_dsr, "[advances_fin_ml, p.222-223]") + "\n"
        + _gate_row("G3 Walk-Forward 6/8 + MDD<25%", flags.g3_walk_forward, "[advances_fin_ml, ch.12]") + "\n"
        + _gate_row("G4 OOS 70/30 Sharpe > 0", flags.g4_oos_sharpe, "mandate §5") + "\n"
        + _gate_row("G5 FWD stress post-2020 Sharpe > 0", flags.g5_fwd_stress, "mandate §5") + "\n"
        + _gate_row("G6 Bootstrap 99.9% CI low > 0", flags.g6_bootstrap_ci, "[advances_fin_ml, p.196-202]") + "\n"
        + _gate_row("G7 Cross-lib ±3pp CAGR", flags.g7_cross_lib, "[advances_fin_ml, p.31-34]") + "\n"
    )
    lines.append(f"\n**Gates passed: {flags.n_passed}/7**\n")

    lines.append("## Trade summary (regime blocks)\n")
    lines.append(
        f"- **Total trades**: {n_trades} ({n_long} long, {n_short} short/cash)\n"
        f"- **Long-leg profitable**: {n_long_win}/{n_long} "
        f"({n_long_win/max(n_long,1)*100:.1f}%)\n"
        f"- **Short-leg profitable**: {n_short_win}/{n_short} "
        f"({n_short_win/max(n_short,1)*100:.1f}%)\n"
        f"- **Avg hold — long**: {avg_hold_long:.0f} bars "
        f"({avg_hold_long/TRADING_DAYS_PER_TEXT:.1f} years)\n"
        f"- **Avg hold — short/cash**: {avg_hold_short:.0f} bars "
        f"({avg_hold_short/TRADING_DAYS_PER_TEXT:.1f} years)\n"
        f"- **Cumulative tax paid (tax=15%)**: "
        f"{result_tax.cum_tax_pct:.4f} (absolute equity units)\n"
    )
    lines.append("\nSee `trades.csv` for the complete regime-block ledger.\n")
    lines.append("## Plot\n")
    lines.append("![equity curve](equity.png)\n")

    lines.append("---\n")
    lines.append(
        f"*Real-data source: Tiingo daily prices for {buy_ticker} "
        f"(buy) + {market.signal_ticker} (signal). Inverse LETFs absent "
        "from cache → synth fallback for sell_leverage < 0.*"
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def _render_final_md(
    configs: list[EMASMAThresholdConfig],
    m_pure: list[ConfigMetrics],
    m_tax: list[ConfigMetrics],
    composite: np.ndarray,
    flags: list[GateFlags],
    benchmark: ConfigMetrics,
    axes: EMASMAThresholdAxes,
    top_k: int,
    market: RealETFMarket,
    bundle_meta: pd.Series,
    out_path: Path,
) -> None:
    from scipy import stats as _stats
    n_total = len(configs)
    order = np.argsort(-composite)

    bench_tk = market.signal_ticker

    lines: list[str] = []
    lines.append(f"# FINAL — Best strategies on REAL {market.name} data\n")
    lines.append(
        f"> Real-ETF validation of the SPYSIM synth study. Data window: "
        f"**{bundle_meta['start'].date()} → {bundle_meta['end'].date()}** "
        f"({bundle_meta['n_bars']} bars, ~{bundle_meta['n_bars']/252:.1f} years).  \n"
        f"> Signal asset: `{market.signal_ticker}`. Buy tickers: "
        f"{', '.join(f'L{k}={v}' for k,v in market.buy_tickers.items())}. "
        "Sell leg with L<0 uses synth inverse (absent in Tiingo cache).  \n"
        "> Educational / experimental — does NOT claim PASS on the mandate.\n"
    )

    lines.append(f"## Benchmark: {bench_tk} buy-and-hold over the same window\n")
    lines.append(
        "| CAGR | Sharpe | Max DD | Calmar | Volatility |\n"
        "|---|---|---|---|---|\n"
        f"| {_fmt_pct(benchmark.cagr)} | {_fmt_num(benchmark.sharpe)} | "
        f"{_fmt_pct(benchmark.max_drawdown)} | {_fmt_num(benchmark.calmar)} | "
        f"{_fmt_pct(benchmark.volatility)} |\n"
    )

    lines.append(f"## Top-{top_k} by composite (PURE sweep)\n")
    lines.append(
        "| rank | cfg_id | CAGR pure | Sharpe pure | MDD | CAGR tax15 | "
        f"Δ CAGR tax | gates | excess vs {bench_tk} |\n"
        "|---|---|---|---|---|---|---|---|---|"
    )
    for rank, i in enumerate(order[:top_k], start=1):
        cfg = configs[i]
        mp = m_pure[i]; mt = m_tax[i]
        drag = mp.cagr - mt.cagr
        excess = mp.cagr - benchmark.cagr
        lines.append(
            f"| {rank} | `{cfg.cfg_id}` | {_fmt_pct(mp.cagr)} | {_fmt_num(mp.sharpe)} | "
            f"{_fmt_pct(mp.max_drawdown)} | {_fmt_pct(mt.cagr)} | {_fmt_pct(drag)} | "
            f"{flags[i].n_passed}/7 | {_fmt_pct(excess)} |"
        )
    lines.append("")

    # Top-K by tax composite.
    cagrs_tax = np.array([mt.cagr for mt in m_tax])
    sharpes_tax = np.array([mt.sharpe for mt in m_tax])
    mdds_tax = np.array([mt.max_drawdown for mt in m_tax])
    composite_tax = (
        0.4 * (_stats.rankdata(cagrs_tax) / n_total)
        + 0.4 * (_stats.rankdata(sharpes_tax) / n_total)
        + 0.2 * (_stats.rankdata(-np.abs(mdds_tax)) / n_total)
    )
    order_tax = np.argsort(-composite_tax)

    lines.append(f"## Top-{top_k} by composite (TAX=15% sweep)\n")
    lines.append(
        "| rank | cfg_id | CAGR tax15 | Sharpe tax15 | MDD | CAGR pure | "
        f"Δ CAGR tax | gates | excess vs {bench_tk} |\n"
        "|---|---|---|---|---|---|---|---|---|"
    )
    for rank, i in enumerate(order_tax[:top_k], start=1):
        cfg = configs[i]
        mp = m_pure[i]; mt = m_tax[i]
        drag = mp.cagr - mt.cagr
        excess = mt.cagr - benchmark.cagr
        lines.append(
            f"| {rank} | `{cfg.cfg_id}` | {_fmt_pct(mt.cagr)} | {_fmt_num(mt.sharpe)} | "
            f"{_fmt_pct(mt.max_drawdown)} | {_fmt_pct(mp.cagr)} | {_fmt_pct(drag)} | "
            f"{flags[i].n_passed}/7 | {_fmt_pct(excess)} |"
        )
    lines.append("")

    # Gate pass rates.
    lines.append(f"## Gate pass rates (out of {n_total}, evaluated on PURE sweep)\n")
    gate_names = [
        ("g1_pbo", "G1 PBO < 0.5"),
        ("g2_dsr", "G2 DSR p < 0.05"),
        ("g3_walk_forward", "G3 Walk-Forward 6/8"),
        ("g4_oos_sharpe", "G4 OOS 70/30 Sharpe > 0"),
        ("g5_fwd_stress", "G5 FWD post-2020 Sharpe > 0"),
        ("g6_bootstrap_ci", "G6 Bootstrap 99.9% CI > 0"),
        ("g7_cross_lib", "G7 Cross-lib ±3pp CAGR"),
    ]
    lines.append("| gate | pass count | pass rate |\n|---|---|---|")
    for key, label in gate_names:
        c = sum(1 for f in flags if getattr(f, key))
        lines.append(f"| {label} | {c}/{n_total} | {c/n_total*100:.1f}% |")
    lines.append("")

    counts_by_n = {k: 0 for k in range(8)}
    for f in flags:
        counts_by_n[f.n_passed] += 1
    lines.append("### Distribution of `gates_passed`\n")
    for k in range(7, -1, -1):
        lines.append(f"- **{k}/7**: {counts_by_n[k]} configs")
    lines.append("")

    # Archetypes in top-K pure.
    lines.append(f"## Archetypes in the top-{top_k} (PURE)\n")
    by_fb: dict[tuple[str, float], int] = {}
    for i in order[:top_k]:
        cfg = configs[i]
        by_fb[(cfg.filter, cfg.buy_leverage)] = by_fb.get((cfg.filter, cfg.buy_leverage), 0) + 1
    lines.append("**By (filter, buy_leverage):**\n")
    for (f, bl), c in sorted(by_fb.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"- {f} + buy×{bl:g}: {c} configs in the top-{top_k}")
    by_th: dict[float, int] = {}
    for i in order[:top_k]:
        by_th[configs[i].threshold_pct] = by_th.get(configs[i].threshold_pct, 0) + 1
    lines.append("\n**By threshold:**\n")
    for th, c in sorted(by_th.items()):
        lines.append(f"- threshold {th*100:.0f}%: {c} configs")
    by_sl: dict[float, int] = {}
    for i in order[:top_k]:
        by_sl[configs[i].sell_leverage] = by_sl.get(configs[i].sell_leverage, 0) + 1
    labels = {0.0: "cash", -1.0: "-1x synth", -2.0: "-2x synth", -3.0: "-3x synth"}
    lines.append("\n**By sell leg:**\n")
    for sl, c in sorted(by_sl.items(), reverse=True):
        lines.append(f"- {labels.get(sl, f'{sl:g}')}: {c} configs")
    lines.append("")

    # Narrative.
    lines.append("## Narrative conclusions\n")
    best_pure = configs[int(order[0])]
    best_tax = configs[int(order_tax[0])]
    best_pure_m = m_pure[int(order[0])]
    best_tax_m = m_tax[int(order_tax[0])]

    lines.append(f"### 1. Best config PURE: `{best_pure.cfg_id}`\n")
    lines.append(
        f"- CAGR {_fmt_pct(best_pure_m.cagr)} vs {bench_tk} B&H "
        f"{_fmt_pct(benchmark.cagr)} -> excess "
        f"{_fmt_pct(best_pure_m.cagr - benchmark.cagr)}.\n"
        f"- Sharpe {_fmt_num(best_pure_m.sharpe)} vs "
        f"{_fmt_num(benchmark.sharpe)}.\n"
        f"- MDD {_fmt_pct(best_pure_m.max_drawdown)} vs {_fmt_pct(benchmark.max_drawdown)}.\n"
        f"- Gates: {flags[int(order[0])].n_passed}/7.\n"
    )

    if int(order[0]) == int(order_tax[0]):
        lines.append("### 2. Best config after 15% swing tax\n")
        lines.append(f"- Same as PURE (`{best_tax.cfg_id}`) — tax doesn't swap "
                     "the winner (few taxable events in this config).\n")
    else:
        lines.append(f"### 2. Best config after 15% swing tax: `{best_tax.cfg_id}`\n")
        lines.append(
            f"- CAGR tax15 {_fmt_pct(best_tax_m.cagr)} vs {bench_tk} "
            f"{_fmt_pct(benchmark.cagr)} -> excess "
            f"{_fmt_pct(best_tax_m.cagr - benchmark.cagr)}.\n"
        )

    lines.append("### 3. Real vs synth comparison caveat\n")
    lines.append(
        "Results on this window (short ~14-17y, post-GFC bull-heavy) are "
        "naturally more optimistic for long-only leveraged configs than "
        "the 40-year SPYSIM synth. Use both studies **together** — "
        "synth (40y) captures multi-regime history; real (this) captures "
        "actual ETF tracking vs the daily-rebal theoretical formula. "
        "Expect ~2-3pp CAGR drag in real UPRO/TQQQ vs theoretical daily-L × "
        "signal per `[leverage_for_the_long_run, p.21, Table 12]`.\n"
    )

    lines.append("### 4. Honest caveats\n")
    lines.append(
        f"- **{bundle_meta['n_bars']} bars (~{bundle_meta['n_bars']/252:.1f} years)** = "
        "far shorter than the 40y synth study. G3 Walk-Forward still needs "
        "≥ 8 OOS windows (2y IS + 6mo OOS stride 6mo) — "
        f"this gives only {max(0, (bundle_meta['n_bars'] - 504) // 126 - 1)} "
        "windows, many still MDD > 25% for leveraged configs.\n"
        "- Bull bias of 2009-2026 (post-GFC recovery + AI rally): SPY CAGR "
        f"{_fmt_pct(benchmark.cagr)} vs long-term ~10%. Inflates any "
        "momentum/trend-following rule.\n"
        "- Real SSO/UPRO/QLD/TQQQ have tracking error vs theoretical daily-L "
        "that shows up here (compare synth study ranks to real study ranks).\n"
        "- **Does NOT change the mandate.** 100% Plano C maintenance remains "
        "the production decision.\n"
    )

    lines.append("---\n")
    lines.append(
        "*Real data: Tiingo parquet cache. Synth inverse formula: "
        "`[leverage_for_the_long_run, p.16, fn.22]`. Gates: PBO "
        "`[advances_fin_ml, p.208-211]`, DSR `[p.222-223]`, bootstrap "
        "`[p.196-202]`, cross-lib `[p.31-34]`.*"
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def emit_all_artifacts(
    axes: EMASMAThresholdAxes,
    market: RealETFMarket,
    bundle: dict,
    study_dir: Path,
    *,
    apply_gates: bool = True,
    top_k: int = 20,
) -> tuple[list[EMASMAThresholdConfig], list[ThresholdResult], list[ThresholdResult],
           list[ConfigMetrics], list[ConfigMetrics], np.ndarray, list[GateFlags],
           ConfigMetrics]:
    """End-to-end: sweep pure + tax, emit configs.csv, summary.json, FINAL.md,
    per-config subfolders. Returns the computed data for further analyses."""
    configs = cartesian_configs(axes)

    # Pure sweep (gates evaluated here).
    res_pure, m_pure, composite, flags = run_one_sweep_real(
        configs, bundle, tax_rate=0.0, apply_gates=apply_gates,
    )
    # Tax sweep (metrics only).
    res_tax, m_tax, _, _ = run_one_sweep_real(
        configs, bundle, tax_rate=0.15, apply_gates=False,
    )

    benchmark = benchmark_signal_buy_hold(bundle)

    # Clean + recreate configs/ subdirs.
    configs_dir = study_dir / "configs"
    if configs_dir.exists():
        for child in configs_dir.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
    configs_dir.mkdir(parents=True, exist_ok=True)

    # Aggregate CSV.
    rows = []
    for i, cfg in enumerate(configs):
        mp = m_pure[i]; mt = m_tax[i]; fl = flags[i]
        rows.append({
            "cfg_id": cfg.cfg_id,
            "filter": cfg.filter, "lookback": cfg.lookback,
            "threshold_pct": cfg.threshold_pct,
            "buy_leverage": cfg.buy_leverage, "sell_leverage": cfg.sell_leverage,
            "buy_ticker": market.buy_tickers[int(cfg.buy_leverage)],
            "pure_cagr": mp.cagr, "pure_sharpe": mp.sharpe,
            "pure_max_drawdown": mp.max_drawdown, "pure_calmar": mp.calmar,
            "pure_sortino": mp.sortino, "pure_volatility": mp.volatility,
            "pure_n_switches": mp.n_switches,
            "tax15_cagr": mt.cagr, "tax15_sharpe": mt.sharpe,
            "tax15_max_drawdown": mt.max_drawdown, "tax15_calmar": mt.calmar,
            "tax15_sortino": mt.sortino, "tax15_volatility": mt.volatility,
            "tax15_n_switches": mt.n_switches,
            "tax_drag_cagr": mp.cagr - mt.cagr,
            "composite_pure": float(composite[i]),
            "g1_pbo": fl.g1_pbo, "g2_dsr": fl.g2_dsr,
            "g3_walk_forward": fl.g3_walk_forward,
            "g4_oos_sharpe": fl.g4_oos_sharpe,
            "g5_fwd_stress": fl.g5_fwd_stress,
            "g6_bootstrap_ci": fl.g6_bootstrap_ci,
            "g7_cross_lib": fl.g7_cross_lib,
            "gates_passed": fl.n_passed,
        })
    df = pd.DataFrame(rows).sort_values("composite_pure", ascending=False).reset_index(drop=True)
    df.insert(0, "rank", df.index + 1)
    df.to_csv(study_dir / "configs.csv", index=False)

    meta = bundle["_meta"]
    (study_dir / "summary.json").write_text(json.dumps({
        "schema_version": 2,
        "market": market.name,
        "signal_ticker": market.signal_ticker,
        "buy_tickers": market.buy_tickers,
        "data_start": meta["start"].date().isoformat(),
        "data_end": meta["end"].date().isoformat(),
        "n_bars": int(meta["n_bars"]),
        "n_configs": len(configs),
        "axes": {
            "filters": list(axes.filters),
            "lookbacks": list(axes.lookbacks),
            "thresholds": list(axes.thresholds),
            "buy_leverages": list(axes.buy_leverages),
            "sell_leverages": list(axes.sell_leverages),
        },
        "benchmark_buy_hold": {
            "cagr": benchmark.cagr,
            "sharpe": benchmark.sharpe,
            "max_drawdown": benchmark.max_drawdown,
        },
        "top_k": df.head(top_k).to_dict(orient="records"),
    }, indent=2, default=str), encoding="utf-8")

    # Per-config subfolders for top-K.
    order = np.argsort(-composite)
    for rank, i in enumerate(order[:top_k], start=1):
        cfg = configs[i]
        cfg_dir = configs_dir / f"{rank:02d}_{cfg.cfg_id}"
        cfg_dir.mkdir(parents=True, exist_ok=True)

        _render_equity_plot(
            res_pure[i], res_tax[i], bundle["signal_prices"], cfg,
            bench_name=f"{market.signal_ticker} buy-hold",
            out_path=cfg_dir / "equity.png",
        )
        _write_trades_csv(res_pure[i], res_tax[i], cfg_dir / "trades.csv")
        buy_tk = market.buy_tickers[int(cfg.buy_leverage)]
        _render_config_summary_md(
            cfg, m_pure[i], m_tax[i], res_pure[i], res_tax[i], flags[i], benchmark,
            rank=rank, n_total=len(configs),
            market=market, buy_ticker=buy_tk,
            out_path=cfg_dir / "summary.md",
        )

    _render_final_md(
        configs, m_pure, m_tax, composite, flags, benchmark, axes,
        top_k=top_k, market=market, bundle_meta=meta,
        out_path=study_dir / "FINAL.md",
    )

    return configs, res_pure, res_tax, m_pure, m_tax, composite, flags, benchmark
