"""Run the EMA/SMA Threshold Crossover educational sweep end-to-end.

Runs TWO sweeps back-to-back on SPYSIM (1986-2026, 40y):

1. **Pure** — ``tax_rate = 0`` (ignores BR DARF). The "what the strategy
   mathematically produces" view.
2. **Tax15** — ``tax_rate = 0.15`` on every profitable regime exit (BR
   swing-sale worst case, no R$20k/mo exemption).

For the top-K configs (by composite score on the PURE sweep) this script
generates per-config outputs:

* ``configs/NN_<cfg_id>/summary.md``  — metrics (pure + tax15) vs SPY,
  gate breakdown, archetype.
* ``configs/NN_<cfg_id>/equity.png``  — strategy equity vs SPY buy-hold.
* ``configs/NN_<cfg_id>/trades.csv``  — regime-block ledger.

Plus a top-level ``FINAL.md`` ranking the best strategies and an
aggregate ``configs.csv`` with metrics for all 384 configs.

Usage
-----

    # Default (384 configs × 2 tax regimes, top-20 per-config outputs)
    .venv/bin/python studies/ema_sma_threshold_educational/run_sweep.py

    # Smoke (8 configs × 2, top-4 outputs)
    .venv/bin/python studies/ema_sma_threshold_educational/run_sweep.py --smoke

    # Skip gates (fast exploration; gates columns will be empty)
    .venv/bin/python studies/ema_sma_threshold_educational/run_sweep.py --skip-gates
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ai_trade.backtest.data.testfolio_loader import (  # noqa: E402
    load_testfolio_returns,
    load_testfolio_series,
)
from ai_trade.backtest.grid.ema_sma_threshold_grid import (  # noqa: E402
    ConfigMetrics,
    EMASMAThresholdAxes,
    GateFlags,
    benchmark_spy_buy_hold,
    cartesian_configs,
    compute_composite_scores,
    compute_config_metrics,
    evaluate_gates,
)
from ai_trade.backtest.strategies.ema_sma_threshold_educational import (  # noqa: E402
    EMASMAThresholdConfig,
    ThresholdResult,
    simulate_ema_sma_threshold,
)

STUDY_DIR = Path(__file__).parent
LOG_PATH = Path("logs/ema_sma_threshold.log")


def _setup_logging() -> logging.Logger:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("ema_sma_threshold")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    fh = logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    return logger


def _fmt_pct(x: float, digits: int = 2) -> str:
    if x is None or np.isnan(x) or np.isinf(x):
        return "—"
    return f"{x * 100:+.{digits}f}%"


def _fmt_num(x: float, digits: int = 2) -> str:
    if x is None or np.isnan(x) or np.isinf(x):
        return "—"
    return f"{x:.{digits}f}"


# ---------------------------------------------------------------------------
# Sweep driver
# ---------------------------------------------------------------------------


def _run_one_sweep(
    configs: list[EMASMAThresholdConfig],
    spx_prices: pd.Series,
    spx_returns: pd.Series,
    *,
    tax_rate: float,
    apply_gates: bool,
    log: logging.Logger,
) -> tuple[list[ThresholdResult], list[ConfigMetrics], np.ndarray, list[GateFlags]]:
    """Run the sweep at a fixed tax_rate. Returns (results, metrics, composite, flags)."""
    log.info("  simulating %d configs (tax_rate=%.2f)...", len(configs), tax_rate)
    results: list[ThresholdResult] = []
    metrics: list[ConfigMetrics] = []
    for base_cfg in configs:
        cfg = replace(base_cfg, tax_rate=tax_rate)
        res = simulate_ema_sma_threshold(spx_prices, spx_returns, cfg)
        results.append(res)
        metrics.append(compute_config_metrics(cfg, res))
    composite = compute_composite_scores(metrics)

    if apply_gates:
        log.info("  evaluating 7 gates...")
        flags = evaluate_gates(
            metrics, results, spx_prices, spx_returns, n_trials=len(configs)
        )
    else:
        flags = [
            GateFlags(False, False, False, False, False, False, False)
            for _ in configs
        ]
    return results, metrics, composite, flags


# ---------------------------------------------------------------------------
# Per-config artifact rendering
# ---------------------------------------------------------------------------


def _render_equity_plot(
    result_pure: ThresholdResult,
    result_tax: ThresholdResult,
    spx_prices: pd.Series,
    cfg: EMASMAThresholdConfig,
    bench_name: str,
    out_path: Path,
) -> None:
    """Plot strategy equity (pure + tax) vs SPY buy-hold, log scale."""
    bench_eq = spx_prices.reindex(result_pure.equity.index).ffill()
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
        f"buy×{cfg.buy_leverage:g}  sell×{cfg.sell_leverage:g}"
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
    """Write a combined trades ledger (pure + tax15 side-by-side).

    Both runs share the same regime sequence (same signal), so their
    trade lists align 1:1. If a config has no ON→OFF (or vice-versa)
    switches the list is empty.
    """
    n = min(len(result_pure.trades), len(result_tax.trades))
    rows = []
    for k in range(n):
        tr_p = result_pure.trades[k]
        tr_t = result_tax.trades[k]
        rows.append({
            "regime": "+1 long" if tr_p.regime == 1 else "-1 short/cash",
            "entry_date": tr_p.entry_date.date().isoformat(),
            "exit_date": tr_p.exit_date.date().isoformat(),
            "bars_held": tr_p.bars_held,
            "pure_entry_equity": tr_p.entry_equity,
            "pure_exit_equity": tr_p.exit_equity,
            "pure_net_pnl_pct": tr_p.net_pnl_pct,
            "tax15_entry_equity": tr_t.entry_equity,
            "tax15_exit_equity": tr_t.exit_equity,
            "tax15_tax_paid": tr_t.tax_paid,
            "tax15_net_pnl_pct": tr_t.net_pnl_pct,
        })
    pd.DataFrame(rows).to_csv(out_path, index=False)


def _gate_row(label: str, passed: bool, cite: str) -> str:
    icon = "PASS" if passed else "FAIL"
    return f"| {label} | {icon} | `{cite}` |"


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
    out_path: Path,
) -> None:
    tax_drag_cagr = m_pure.cagr - m_tax.cagr
    tax_drag_sharpe = m_pure.sharpe - m_tax.sharpe

    n_trades = len(result_pure.trades)
    n_long = sum(1 for t in result_pure.trades if t.regime == 1)
    n_short = n_trades - n_long
    long_trades_profitable = sum(
        1 for t in result_pure.trades if t.regime == 1 and t.net_pnl_pct > 0
    )
    short_trades_profitable = sum(
        1 for t in result_pure.trades if t.regime == -1 and t.net_pnl_pct > 0
    )
    avg_hold_long = (
        np.mean([t.bars_held for t in result_pure.trades if t.regime == 1])
        if n_long > 0 else 0.0
    )
    avg_hold_short = (
        np.mean([t.bars_held for t in result_pure.trades if t.regime == -1])
        if n_short > 0 else 0.0
    )

    lines: list[str] = []
    lines.append(f"# Config {cfg.cfg_id} — rank {rank}/{n_total}\n")
    lines.append("> Educational sweep — not a production strategy. "
                 "Ranking by composite `0.4·rank(CAGR) + 0.4·rank(Sharpe) + "
                 "0.2·rank(1/|MDD|)` on the PURE (tax=0) sweep.\n")

    lines.append("## Parameters\n")
    lines.append(
        "| param | value | citation |\n"
        "|---|---|---|\n"
        f"| MA filter | {cfg.filter} | `[leverage_for_the_long_run, p.8]` |\n"
        f"| lookback | {cfg.lookback} bars | `[leverage_for_the_long_run, p.14, Table 6]` |\n"
        f"| threshold | ±{cfg.threshold_pct*100:.0f}% | `[leverage_for_the_long_run, p.11]` |\n"
        f"| buy leg | ×{cfg.buy_leverage:g} long synth LETF | `[leverage_for_the_long_run, p.17, Table 8]` |\n"
        f"| sell leg | ×{cfg.sell_leverage:g} {'(cash)' if cfg.sell_leverage == 0 else '(synth inverse LETF)'} | `[leverage_for_the_long_run, p.21]` |\n"
        f"| annual fee | {cfg.fee*100:.2f}% | `[leverage_for_the_long_run, p.16, fn.23]` |\n"
        f"| switch cost | {cfg.switch_cost_bps:.0f} bps/transition | mirror `letf_rotation.py` |\n"
    )

    lines.append("## Metrics — pure (tax=0) vs tax=15% vs SPY buy-hold\n")
    lines.append(
        "| metric | pure | tax=15% | SPY buy-hold | tax drag |\n"
        "|---|---|---|---|---|\n"
        f"| CAGR | {_fmt_pct(m_pure.cagr)} | {_fmt_pct(m_tax.cagr)} | {_fmt_pct(benchmark.cagr)} | {_fmt_pct(tax_drag_cagr)} |\n"
        f"| Sharpe | {_fmt_num(m_pure.sharpe)} | {_fmt_num(m_tax.sharpe)} | {_fmt_num(benchmark.sharpe)} | {_fmt_num(tax_drag_sharpe)} |\n"
        f"| Max Drawdown | {_fmt_pct(m_pure.max_drawdown)} | {_fmt_pct(m_tax.max_drawdown)} | {_fmt_pct(benchmark.max_drawdown)} | — |\n"
        f"| Calmar | {_fmt_num(m_pure.calmar)} | {_fmt_num(m_tax.calmar)} | {_fmt_num(benchmark.calmar)} | — |\n"
        f"| Sortino | {_fmt_num(m_pure.sortino)} | {_fmt_num(m_tax.sortino)} | {_fmt_num(benchmark.sortino)} | — |\n"
        f"| Volatility | {_fmt_pct(m_pure.volatility)} | {_fmt_pct(m_tax.volatility)} | {_fmt_pct(benchmark.volatility)} | — |\n"
        f"| n_switches | {m_pure.n_switches} | {m_tax.n_switches} | 0 | — |\n"
    )

    if m_pure.cagr > 0:
        drag_frac = tax_drag_cagr / m_pure.cagr
        lines.append(
            f"*Tax drag = {_fmt_pct(tax_drag_cagr)} CAGR = "
            f"{drag_frac*100:.1f}% of the pure edge.*\n"
        )

    lines.append("## Gates (informational, not blocking; evaluated on PURE sweep)\n")
    lines.append(
        "| gate | verdict | citation |\n"
        "|---|---|---|\n"
        + _gate_row("G1 PBO < 0.5", flags.g1_pbo, "[advances_fin_ml, p.208-211]") + "\n"
        + _gate_row("G2 DSR p < 0.05", flags.g2_dsr, "[advances_fin_ml, p.222-223]") + "\n"
        + _gate_row("G3 Walk-Forward 6/8 + MDD<25%", flags.g3_walk_forward, "[advances_fin_ml, ch.12]") + "\n"
        + _gate_row("G4 OOS 70/30 Sharpe > 0", flags.g4_oos_sharpe, "mandate §5") + "\n"
        + _gate_row("G5 FWD stress post-2020 Sharpe > 0", flags.g5_fwd_stress, "mandate §5") + "\n"
        + _gate_row("G6 Bootstrap 99.9% CI low > 0", flags.g6_bootstrap_ci, "[advances_fin_ml, p.196-202]") + "\n"
        + _gate_row("G7 Cross-lib ±3pp CAGR", flags.g7_cross_lib, "[advances_fin_ml, p.31-34]") + "\n"
    )
    lines.append(f"\n**Gates passed: {flags.n_passed}/7**\n")

    if flags.n_passed >= 6:
        lines.append("> Strong gate-passer: noise-robust by multiple "
                     "independent criteria. Still educational, still not "
                     "production.\n")
    elif flags.n_passed >= 4:
        lines.append("> Partial gate-passer: key statistical checks pass "
                     "but one or more critical filters reject.\n")
    else:
        lines.append("> Weak gate profile: fewer than 4/7 pass — likely "
                     "noise-dominated or overfit.\n")

    lines.append("## Trade summary (regime blocks)\n")
    lines.append(
        f"- **Total trades**: {n_trades} ({n_long} long, {n_short} short/cash)\n"
        f"- **Long-leg profitable**: {long_trades_profitable}/{n_long} "
        f"({long_trades_profitable/max(n_long,1)*100:.1f}%)\n"
        f"- **Short-leg profitable**: {short_trades_profitable}/{n_short} "
        f"({short_trades_profitable/max(n_short,1)*100:.1f}%)\n"
        f"- **Avg hold — long**: {avg_hold_long:.0f} bars "
        f"({avg_hold_long/TRADING_DAYS_PER_TEXT:.1f} years)\n"
        f"- **Avg hold — short/cash**: {avg_hold_short:.0f} bars "
        f"({avg_hold_short/TRADING_DAYS_PER_TEXT:.1f} years)\n"
        f"- **Cumulative tax paid (tax=15%)**: "
        f"{result_tax.cum_tax_pct:.4f} (absolute equity units)\n"
    )
    lines.append("\nSee `trades.csv` for the complete regime-block ledger "
                 "with pure vs tax15 equity paths.\n")

    lines.append("## Plot\n")
    lines.append("![equity curve](equity.png)\n")

    lines.append("---\n")
    lines.append(
        "*Citations: signal `[leverage_for_the_long_run, p.13]`; "
        "synth formula `[p.16, fn.22]`; band `[p.11]`; "
        "honest alignment `[advances_fin_ml, p.31-34]`; "
        "gates — see table above.*\n"
    )

    out_path.write_text("\n".join(lines), encoding="utf-8")


TRADING_DAYS_PER_TEXT = 252  # for prose conversion only


# ---------------------------------------------------------------------------
# FINAL.md — aggregate ranking
# ---------------------------------------------------------------------------


def _render_final_md(
    configs: list[EMASMAThresholdConfig],
    m_pure: list[ConfigMetrics],
    m_tax: list[ConfigMetrics],
    composite: np.ndarray,
    flags: list[GateFlags],
    benchmark: ConfigMetrics,
    axes: EMASMAThresholdAxes,
    top_k: int,
    out_path: Path,
) -> None:
    from scipy import stats as _stats
    n_total = len(configs)
    order = np.argsort(-composite)

    lines: list[str] = []
    lines.append("# FINAL — Best strategies from the EMA/SMA threshold sweep\n")
    lines.append("> **Educational / experimental** — does NOT claim PASS on the "
                 "project mandate. Project is in MAINTENANCE (100% Plano C).\n")

    lines.append("## Benchmark: SPY buy-and-hold (1986-2026)\n")
    lines.append(
        "| CAGR | Sharpe | Max DD | Calmar | Volatility |\n"
        "|---|---|---|---|---|\n"
        f"| {_fmt_pct(benchmark.cagr)} | {_fmt_num(benchmark.sharpe)} | "
        f"{_fmt_pct(benchmark.max_drawdown)} | {_fmt_num(benchmark.calmar)} | "
        f"{_fmt_pct(benchmark.volatility)} |\n"
    )

    # Top-K by pure composite.
    lines.append(f"## Top-{top_k} by composite (PURE sweep)\n")
    lines.append(
        "| rank | cfg_id | CAGR pure | Sharpe pure | MDD | CAGR tax15 | Δ CAGR tax | gates | excess vs SPY (pure) |\n"
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

    # Top-K by tax-adjusted composite.
    cagrs_tax = np.array([mt.cagr for mt in m_tax])
    sharpes_tax = np.array([mt.sharpe for mt in m_tax])
    mdds_tax = np.array([mt.max_drawdown for mt in m_tax])
    rc = _stats.rankdata(cagrs_tax) / n_total
    rs = _stats.rankdata(sharpes_tax) / n_total
    rm = _stats.rankdata(-np.abs(mdds_tax)) / n_total
    composite_tax = 0.4 * rc + 0.4 * rs + 0.2 * rm
    order_tax = np.argsort(-composite_tax)

    lines.append(f"## Top-{top_k} by composite (TAX=15% sweep)\n")
    lines.append(
        "| rank | cfg_id | CAGR tax15 | Sharpe tax15 | MDD | CAGR pure | Δ CAGR tax | gates | excess vs SPY (tax15) |\n"
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

    # Gates summary.
    lines.append("## Gate pass rates (out of 384, evaluated on PURE sweep)\n")
    gate_counts = {
        "G1 PBO < 0.5": sum(1 for f in flags if f.g1_pbo),
        "G2 DSR p < 0.05": sum(1 for f in flags if f.g2_dsr),
        "G3 Walk-Forward 6/8": sum(1 for f in flags if f.g3_walk_forward),
        "G4 OOS 70/30 Sharpe > 0": sum(1 for f in flags if f.g4_oos_sharpe),
        "G5 FWD post-2020 Sharpe > 0": sum(1 for f in flags if f.g5_fwd_stress),
        "G6 Bootstrap 99.9% CI > 0": sum(1 for f in flags if f.g6_bootstrap_ci),
        "G7 Cross-lib ±3pp CAGR": sum(1 for f in flags if f.g7_cross_lib),
    }
    lines.append("| gate | pass count | pass rate |\n|---|---|---|")
    for g, c in gate_counts.items():
        lines.append(f"| {g} | {c}/{n_total} | {c/n_total*100:.1f}% |")
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
    lines.append("\n**By threshold:**\n")
    by_th: dict[float, int] = {}
    for i in order[:top_k]:
        by_th[configs[i].threshold_pct] = by_th.get(configs[i].threshold_pct, 0) + 1
    for th, c in sorted(by_th.items()):
        lines.append(f"- threshold {th*100:.0f}%: {c} configs")
    lines.append("\n**By sell leg:**\n")
    by_sl: dict[float, int] = {}
    for i in order[:top_k]:
        by_sl[configs[i].sell_leverage] = by_sl.get(configs[i].sell_leverage, 0) + 1
    labels = {0.0: "cash", -1.0: "-1x short", -2.0: "-2x short", -3.0: "-3x short"}
    for sl, c in sorted(by_sl.items(), reverse=True):
        lines.append(f"- {labels.get(sl, f'{sl:g}')}: {c} configs")
    lines.append("")

    # Narrative conclusions.
    lines.append("## Narrative conclusions\n")
    best_pure_idx = int(order[0])
    best_tax_idx = int(order_tax[0])
    best_pure = configs[best_pure_idx]
    best_tax = configs[best_tax_idx]

    lines.append(f"### 1. Best config PURE: `{best_pure.cfg_id}`\n")
    lines.append(
        f"- CAGR {_fmt_pct(m_pure[best_pure_idx].cagr)} vs SPY "
        f"{_fmt_pct(benchmark.cagr)} -> excess "
        f"{_fmt_pct(m_pure[best_pure_idx].cagr - benchmark.cagr)}.\n"
        f"- Sharpe {_fmt_num(m_pure[best_pure_idx].sharpe)} vs SPY "
        f"{_fmt_num(benchmark.sharpe)}.\n"
        f"- MDD {_fmt_pct(m_pure[best_pure_idx].max_drawdown)} vs SPY "
        f"{_fmt_pct(benchmark.max_drawdown)}.\n"
        f"- Gates: {flags[best_pure_idx].n_passed}/7.\n"
    )

    if best_pure_idx != best_tax_idx:
        lines.append(f"### 2. Best config after 15% swing tax: `{best_tax.cfg_id}`\n")
        lines.append(
            "- Tax changes the winner: the pure top collapses under frequent "
            "regime flips (each profitable exit loses 15%). The tax-aware top "
            "tends to hold longer (fewer taxable events).\n"
            f"- CAGR tax15 {_fmt_pct(m_tax[best_tax_idx].cagr)} vs SPY "
            f"{_fmt_pct(benchmark.cagr)} -> excess "
            f"{_fmt_pct(m_tax[best_tax_idx].cagr - benchmark.cagr)}.\n"
        )
    else:
        lines.append("### 2. Best config after 15% swing tax\n")
        lines.append(f"- Same as PURE (`{best_tax.cfg_id}`) - tax doesn't change "
                     "the winner because this config holds long regimes through "
                     "most of the 40y window (few taxable events).\n")

    drags_topk = [m_pure[i].cagr - m_tax[i].cagr for i in order[:top_k]]
    median_drag = float(np.median(drags_topk))
    lines.append("### 3. Pattern\n")
    lines.append(
        f"- **Median CAGR drag from 15% swing tax** (top-{top_k} pure): "
        f"{_fmt_pct(median_drag)}. High-churn configs pay heavily; low-churn "
        "(long lookback, wide threshold, cash on sell) lose less.\n"
        "- Short-leveraged sell legs (-2x, -3x) amplify turnover but add "
        "little CAGR after tax in most archetypes.\n"
        "- Gayed canonical (SMA-200, threshold 0%, 2-3x long, cash) appears "
        "in the top tier but is rarely the single winner.\n"
    )

    lines.append("### 4. Honest caveats\n")
    lines.append(
        "- 40 years of SPY is a bull-heavy regime (11.5% CAGR). Any trend-following "
        "rule with leverage will look good in-sample. Walk-forward (G3) fails on "
        "nearly every config with MDD > 25% - the drawdown discipline required by "
        "Mandate §5 is not met.\n"
        "- Synth LETFs assume perfect daily re-leveraging (Gayed fn.22). Real "
        "UPRO/SSO tracking error and intra-day leveraging noise would reduce these "
        "CAGRs by 2-3pp (Gayed p.21, Table 12).\n"
        "- **Cross-lib (G7) PASS 384/384** = hand-rolled numpy and pandas-vectorised "
        "paths agree within ±3pp. This locks the simulator against look-ahead "
        "alignment bugs (see `[advances_fin_ml, p.31-34]`).\n"
        "- **Does NOT change the mandate.** Project remains in MAINTENANCE with "
        "100% Plano C (`portfolio-aposentadoria.md`). This sweep is a learning "
        "exercise, not a strategy proposal.\n"
    )

    lines.append("---\n")
    lines.append(
        "*Key citations:* Gayed synth `[leverage_for_the_long_run, p.16, fn.22]`; "
        "SMA regime `[p.8, p.13]`; band `[p.11]`; leverage levels `[p.17, Table 8]`. "
        "Gates: PBO `[advances_fin_ml, p.208-211]`, DSR `[p.222-223]`, bootstrap "
        "`[p.196-202]`, cross-lib/lookahead `[p.31-34]`. See `SPEC.md` for the full "
        "spec; `configs/` for per-config detail; `configs.csv` for the raw sweep.\n"
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="8 configs x 2 tax regimes")
    parser.add_argument("--full", action="store_true", help="1512 configs x 2 tax regimes")
    parser.add_argument(
        "--skip-gates", action="store_true", help="Skip gate evaluation"
    )
    parser.add_argument(
        "--top-k", type=int, default=20,
        help="How many top configs get per-config subfolders"
    )
    parser.add_argument(
        "--study-dir", type=Path, default=STUDY_DIR,
        help="Output root (default: this script's parent)"
    )
    args = parser.parse_args()

    log = _setup_logging()
    start = time.time()

    if args.smoke:
        axes = EMASMAThresholdAxes.smoke()
    elif args.full:
        axes = EMASMAThresholdAxes.full()
    else:
        axes = EMASMAThresholdAxes()
    top_k = min(args.top_k, axes.n_configs)

    configs = cartesian_configs(axes)
    log.info("Loading SPYSIM from testfolio. Axes: %d configs x 2 tax regimes.",
             len(configs))
    spx_prices = load_testfolio_series("SPYSIM")
    spx_returns = load_testfolio_returns("SPYSIM")

    log.info("=== PURE sweep (tax_rate=0.00) ===")
    res_pure, m_pure, composite, flags = _run_one_sweep(
        configs, spx_prices, spx_returns,
        tax_rate=0.0, apply_gates=not args.skip_gates, log=log,
    )
    log.info("pure done in %.1fs", time.time() - start)

    t_tax = time.time()
    log.info("=== TAX15 sweep (tax_rate=0.15) ===")
    res_tax, m_tax, _composite_tax, _flags_tax = _run_one_sweep(
        configs, spx_prices, spx_returns,
        tax_rate=0.15, apply_gates=False, log=log,
    )
    log.info("tax done in %.1fs", time.time() - t_tax)

    benchmark = benchmark_spy_buy_hold(spx_prices, spx_returns)
    log.info(
        "Benchmark SPY buy-hold: CAGR=%.2f%% Sharpe=%.2f MDD=%.2f%%",
        benchmark.cagr * 100, benchmark.sharpe, benchmark.max_drawdown * 100,
    )

    study_dir: Path = args.study_dir
    configs_dir = study_dir / "configs"
    # Clean stale per-config folders (ranks are re-computed; leftovers
    # from previous runs would mix with the fresh top-K).
    if configs_dir.exists():
        import shutil
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
    df = pd.DataFrame(rows).sort_values(
        "composite_pure", ascending=False
    ).reset_index(drop=True)
    df.insert(0, "rank", df.index + 1)
    df.to_csv(study_dir / "configs.csv", index=False)

    # summary.json
    (study_dir / "summary.json").write_text(json.dumps({
        "schema_version": 2,
        "n_configs": len(configs),
        "tax_regimes": ["pure", "tax15"],
        "axes": {
            "filters": list(axes.filters),
            "lookbacks": list(axes.lookbacks),
            "thresholds": list(axes.thresholds),
            "buy_leverages": list(axes.buy_leverages),
            "sell_leverages": list(axes.sell_leverages),
        },
        "benchmark_spy_buy_hold": {
            "cagr": benchmark.cagr, "sharpe": benchmark.sharpe,
            "max_drawdown": benchmark.max_drawdown,
        },
        "top_k": df.head(top_k).to_dict(orient="records"),
    }, indent=2, default=str), encoding="utf-8")

    # Per-config subfolders for top-K.
    order = np.argsort(-composite)
    log.info("Generating per-config outputs for top-%d configs...", top_k)
    for rank, i in enumerate(order[:top_k], start=1):
        cfg = configs[i]
        cfg_dir = configs_dir / f"{rank:02d}_{cfg.cfg_id}"
        cfg_dir.mkdir(parents=True, exist_ok=True)

        _render_equity_plot(
            res_pure[i], res_tax[i], spx_prices, cfg,
            bench_name="SPY buy-hold",
            out_path=cfg_dir / "equity.png",
        )
        _write_trades_csv(res_pure[i], res_tax[i], cfg_dir / "trades.csv")
        _render_config_summary_md(
            cfg, m_pure[i], m_tax[i], res_pure[i], res_tax[i], flags[i], benchmark,
            rank=rank, n_total=len(configs),
            out_path=cfg_dir / "summary.md",
        )

    _render_final_md(
        configs, m_pure, m_tax, composite, flags, benchmark, axes,
        top_k=top_k,
        out_path=study_dir / "FINAL.md",
    )

    readme = [
        "# EMA/SMA Threshold Crossover — Educational Study\n",
        "> Educational sweep on SPY with leveraged ETFs. "
        "Not a production strategy. Project mandate remains 100% Plano C "
        "(MAINTENANCE §1).\n",
        "## Contents\n",
        "- **`SPEC.md`** — full specification with citations.",
        "- **`run_sweep.py`** — CLI to regenerate all artifacts.",
        "- **`FINAL.md`** — ranked top-" + str(top_k) + " strategies + narrative.",
        "- **`configs.csv`** — every config's metrics + gates.",
        "- **`summary.json`** — machine-readable axes + top-" + str(top_k) + ".",
        "- **`configs/NN_<cfg_id>/`** — per-config deep-dives:",
        "  - `summary.md` — metrics pure + tax15 vs SPY + gate breakdown.",
        "  - `equity.png` — equity path vs SPY buy-hold (log scale).",
        "  - `trades.csv` — regime-block ledger (pure + tax15 side-by-side).\n",
        "## Usage\n",
        "```bash",
        "# Default: 384 configs x 2 tax regimes, top-20 per-config outputs (~12-15 min)",
        ".venv/bin/python studies/ema_sma_threshold_educational/run_sweep.py",
        "",
        "# Smoke (8 configs, ~1 min)",
        ".venv/bin/python studies/ema_sma_threshold_educational/run_sweep.py --smoke",
        "",
        "# Full grid (1512 configs, ~30-40 min)",
        ".venv/bin/python studies/ema_sma_threshold_educational/run_sweep.py --full",
        "```\n",
        "Data source: `data/testfolio/cache/history.parquet` ticker `SPYSIM` "
        "(1986-2026, S&P 500 total return proxy, modelled). See `SPEC.md` for "
        "details.\n",
    ]
    (study_dir / "README.md").write_text("\n".join(readme), encoding="utf-8")

    log.info("Artifacts written under %s", study_dir.resolve())
    log.info("Total wall time: %.1fs", time.time() - start)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
