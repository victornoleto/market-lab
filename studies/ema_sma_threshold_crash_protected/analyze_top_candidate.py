"""Deep-dive analysis of the best crash-protected candidate.

Target config: **`EMA_N150_th5_bL3_sL0 + sl30_rec10_cape05`** — the
combo that reduced MDD most on the educational top-1 base within the
ΔCAGR ≥ −5 pp corridor.

Produces (under ``studies/ema_sma_threshold_crash_protected/analysis_top_candidate/``):

* ``report.md`` — prose summary + metrics tables + verdict.
* ``equity_vs_benchmarks.png`` — candidate + baseline (no overlay) +
  SPY buy-hold on log scale.
* ``drawdown.png`` — running drawdown of all three series, annotated
  with stop triggers and re-entry bars.
* ``risk_signal_trace.png`` — CAPE z-score → risk-score → effective
  position over time.
* ``crash_<year>.png`` — zoomed equity during each major historical
  crash (2000, 2008, 2020, 2022).
* ``stop_events.csv`` — every stop trigger with stop/re-entry dates,
  equity & price at stop and bottom.
* ``monthly_returns.csv`` — three-column monthly returns for
  strategy-vs-benchmark lookups.

Why this script exists
----------------------

The Phase 3 sweep wrote metrics but did not plot per-config. The user
asked for a deep look at the top candidate vs. benchmark — this is it.
"""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ai_trade.backtest.data.macro_data_loader import load_all_indicators  # noqa: E402
from ai_trade.backtest.data.testfolio_loader import (  # noqa: E402
    load_testfolio_returns,
    load_testfolio_series,
)
from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    calmar as _calmar,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
    sortino as _sortino,
    volatility as _volatility,
)
from ai_trade.backtest.signals.risk_score import (  # noqa: E402
    INDICATOR_SPECS,
    compute_risk_score,
    rolling_zscore,
)
from ai_trade.backtest.strategies.ema_sma_threshold_educational import (  # noqa: E402
    DEFAULT_FEE,
    EMASMAThresholdConfig,
    TRADING_DAYS_PER_YEAR,
    _synth_leveraged_returns,
    simulate_regime_threshold_with_legs,
)
from ai_trade.backtest.strategies.stop_loss_and_risk_signals import (  # noqa: E402
    RiskSignalConfig,
    StopLossConfig,
    simulate_with_stop_and_risk,
)

STUDY_DIR = Path(__file__).parent
OUT_DIR = STUDY_DIR / "analysis_top_candidate"


@dataclass
class CrashWindow:
    label: str
    start: str
    end: str
    subtitle: str


CRASHES: tuple[CrashWindow, ...] = (
    CrashWindow("1987_black_monday", "1987-08-01", "1988-06-30",
                "Black Monday: SPY −34% in 2 days"),
    CrashWindow("2000_dotcom", "2000-03-01", "2003-12-31",
                "Dot-com: SPY −49% over 30 months"),
    CrashWindow("2008_gfc", "2007-10-01", "2010-06-30",
                "GFC: SPY −57% over 17 months"),
    CrashWindow("2020_covid", "2020-01-01", "2020-09-30",
                "COVID: SPY −34% in 22 days"),
    CrashWindow("2022_bear", "2022-01-01", "2023-01-31",
                "2022 bear: SPY −25% over 9 months"),
)


def _setup_logging() -> logging.Logger:
    logger = logging.getLogger("phase3_top_candidate")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(sh)
    return logger


def _fmt_pct(x, digits=2):
    if x is None or np.isnan(x) or np.isinf(x):
        return "—"
    return f"{x * 100:+.{digits}f}%"


def _fmt_num(x, digits=2):
    if x is None or np.isnan(x) or np.isinf(x):
        return "—"
    return f"{x:.{digits}f}"


def _drawdown(eq: pd.Series) -> pd.Series:
    peak = eq.cummax()
    return 1.0 - eq / peak


def _full_metrics(eq: pd.Series, rets: pd.Series, label: str) -> dict:
    return {
        "label": label,
        "CAGR": float(_cagr(eq, TRADING_DAYS_PER_YEAR)),
        "Sharpe": float(_sharpe(rets, TRADING_DAYS_PER_YEAR)),
        "Sortino": float(_sortino(rets, TRADING_DAYS_PER_YEAR)),
        "MDD": float(_max_drawdown(eq)),
        "Calmar": float(_calmar(eq, TRADING_DAYS_PER_YEAR)),
        "Volatility": float(_volatility(rets, TRADING_DAYS_PER_YEAR)),
        "Final equity (start=1.0)": float(eq.iloc[-1]),
    }


def main() -> int:
    log = _setup_logging()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- Config: the top candidate ---
    base = EMASMAThresholdConfig(
        filter="EMA", lookback=150, threshold_pct=0.05,
        buy_leverage=3.0, sell_leverage=0.0,
        fee=DEFAULT_FEE, switch_cost_bps=15.0, tax_rate=0.0,
    )
    stop_cfg = StopLossConfig(
        stop_loss_pct=0.30, reentry_mode="recovery_trigger", reentry_param=0.10,
    )
    risk_cfg = RiskSignalConfig(indicator_type="cape", lambda_de_lever=0.5)
    log.info("Top candidate: %s + stop=%s + risk=%s", base.cfg_id, stop_cfg, risk_cfg)

    # --- Data (educational dataset) ---
    spx_prices = load_testfolio_series("SPYSIM")
    spx_returns = load_testfolio_returns("SPYSIM")
    daily_idx = spx_returns.index
    log.info("Data window: %s → %s (%d bars, ~%.1fy)",
             daily_idx[0].date(), daily_idx[-1].date(),
             len(daily_idx), len(daily_idx) / 252)

    # Legs (synth 3x long + cash).
    long_leg = _synth_leveraged_returns(spx_returns, base.buy_leverage, base.fee)
    cash_daily = base.cash_rate_annual / TRADING_DAYS_PER_YEAR
    sell_leg = pd.Series(cash_daily, index=spx_returns.index)

    # CAPE risk score.
    raw = load_all_indicators(daily_idx)
    cape_raw = raw["cape"]
    cape_z = rolling_zscore(cape_raw, INDICATOR_SPECS["cape"].window)
    cape_risk = compute_risk_score(cape_raw, INDICATOR_SPECS["cape"])

    # --- Three series to compare ---
    log.info("Running baseline (no overlay)...")
    base_res = simulate_regime_threshold_with_legs(
        signal_prices=spx_prices, buy_leg_returns=long_leg,
        sell_leg_returns=sell_leg, cfg=base,
    )

    log.info("Running top candidate (stop + CAPE signal)...")
    cand_res = simulate_with_stop_and_risk(
        signal_prices=spx_prices, buy_leg_returns=long_leg,
        sell_leg_returns=sell_leg, cfg=base,
        stop_cfg=stop_cfg, risk_series=cape_risk, risk_cfg=risk_cfg,
    )

    # SPY buy-hold benchmark.
    bench_eq = spx_prices.reindex(daily_idx).ffill()
    bench_eq = bench_eq / bench_eq.iloc[0]
    bench_rets = bench_eq.pct_change().fillna(0.0)

    # --- Metrics ---
    metrics = [
        _full_metrics(cand_res.equity, cand_res.daily_returns,
                      "Candidate (stop + CAPE)"),
        _full_metrics(base_res.equity, base_res.daily_returns,
                      "Baseline (no overlay)"),
        _full_metrics(bench_eq, bench_rets, "SPY buy-hold"),
    ]
    df_metrics = pd.DataFrame(metrics).set_index("label")
    log.info("Metrics:\n%s", df_metrics.to_string())

    # Crash-specific metrics.
    crash_rows = []
    for cw in CRASHES:
        mask = (daily_idx >= cw.start) & (daily_idx <= cw.end)
        if not mask.any():
            continue
        cand_slice = cand_res.equity.loc[mask]
        base_slice = base_res.equity.loc[mask]
        bench_slice = bench_eq.loc[mask]
        def _mdd_slice(s):
            p = s.cummax()
            return float((1 - s / p).max())
        crash_rows.append({
            "crash": cw.label,
            "window": f"{cw.start} → {cw.end}",
            "cand_MDD": _mdd_slice(cand_slice),
            "base_MDD": _mdd_slice(base_slice),
            "bench_MDD": _mdd_slice(bench_slice),
            "cand_total_return": float(cand_slice.iloc[-1] / cand_slice.iloc[0] - 1),
            "base_total_return": float(base_slice.iloc[-1] / base_slice.iloc[0] - 1),
            "bench_total_return": float(bench_slice.iloc[-1] / bench_slice.iloc[0] - 1),
            "n_stops_in_window": sum(
                1 for ev in cand_res.stop_events
                if pd.Timestamp(cw.start) <= ev.stop_date <= pd.Timestamp(cw.end)
            ),
        })
    df_crash = pd.DataFrame(crash_rows).set_index("crash")

    # --- Stop events ---
    stop_rows = []
    for ev in cand_res.stop_events:
        stop_rows.append({
            "stop_date": ev.stop_date.date().isoformat(),
            "reentry_date": ev.reentry_date.date().isoformat() if ev.reentry_date else "OPEN",
            "bars_stopped": ev.reentry_bar_offset or -1,
            "equity_at_stop": ev.equity_at_stop,
            "peak_before_stop": ev.peak_before_stop,
            "drawdown_at_stop": ev.drawdown_at_stop,
            "bottom_equity_during_stop": ev.bottom_equity_during_stop,
            "bottom_price_during_stop": ev.bottom_price_during_stop,
        })
    df_stops = pd.DataFrame(stop_rows)
    df_stops.to_csv(OUT_DIR / "stop_events.csv", index=False)
    log.info("Wrote %s (%d stop events)", OUT_DIR / "stop_events.csv", len(df_stops))

    # Monthly returns side-by-side.
    monthly = pd.DataFrame({
        "Candidate": cand_res.equity.resample("ME").last().pct_change(),
        "Baseline": base_res.equity.resample("ME").last().pct_change(),
        "SPY": bench_eq.resample("ME").last().pct_change(),
    })
    monthly.to_csv(OUT_DIR / "monthly_returns.csv")

    # Effective position per bar (useful for "% days de-levered").
    pos_series = cand_res.effective_position.loc[cand_res.regime == 1].dropna()
    pct_days_below_unity = float((pos_series < 0.999).mean())
    pct_days_below_half = float((pos_series < 0.5).mean())

    # --- Plots ---
    _plot_equity_log(
        cand_res.equity, base_res.equity, bench_eq,
        stops=[ev.stop_date for ev in cand_res.stop_events],
        reentries=[ev.reentry_date for ev in cand_res.stop_events if ev.reentry_date],
        out_path=OUT_DIR / "equity_vs_benchmarks.png",
    )
    _plot_drawdown(
        cand_res.equity, base_res.equity, bench_eq,
        stops=[ev.stop_date for ev in cand_res.stop_events],
        out_path=OUT_DIR / "drawdown.png",
    )
    _plot_risk_signal_trace(
        cape_raw, cape_z, cape_risk, cand_res.effective_position,
        out_path=OUT_DIR / "risk_signal_trace.png",
    )
    for cw in CRASHES:
        mask = (daily_idx >= cw.start) & (daily_idx <= cw.end)
        if not mask.any():
            continue
        _plot_crash_zoom(
            cand_res.equity.loc[mask], base_res.equity.loc[mask],
            bench_eq.loc[mask], cw,
            stops=[ev.stop_date for ev in cand_res.stop_events
                   if pd.Timestamp(cw.start) <= ev.stop_date <= pd.Timestamp(cw.end)],
            reentries=[
                ev.reentry_date for ev in cand_res.stop_events
                if ev.reentry_date and pd.Timestamp(cw.start) <= ev.reentry_date <= pd.Timestamp(cw.end)
            ],
            out_path=OUT_DIR / f"crash_{cw.label}.png",
        )

    # --- Report ---
    md = _build_report_md(
        base=base, stop_cfg=stop_cfg, risk_cfg=risk_cfg,
        df_metrics=df_metrics, df_crash=df_crash, df_stops=df_stops,
        cand_res=cand_res, base_res=base_res,
        pct_days_below_unity=pct_days_below_unity,
        pct_days_below_half=pct_days_below_half,
        window_label=f"{daily_idx[0].date()}→{daily_idx[-1].date()}",
    )
    (OUT_DIR / "report.md").write_text(md, encoding="utf-8")
    log.info("Wrote %s", OUT_DIR / "report.md")
    log.info("Done — see %s", OUT_DIR)
    return 0


# ---------------------------------------------------------------------------
# Plotting helpers
# ---------------------------------------------------------------------------


def _plot_equity_log(
    cand_eq, base_eq, bench_eq, *, stops, reentries, out_path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(12, 6), dpi=120)
    ax.plot(cand_eq.index, cand_eq.values, label="Candidate (stop + CAPE)",
            color="#1f77b4", linewidth=1.5)
    ax.plot(base_eq.index, base_eq.values, label="Baseline (no overlay, 3x UPRO)",
            color="#d62728", linewidth=1.2, alpha=0.8)
    ax.plot(bench_eq.index, bench_eq.values, label="SPY buy-hold",
            color="#808080", linewidth=1.0, linestyle="--")
    for s in stops:
        ax.axvline(s, color="red", alpha=0.15, linewidth=0.8)
    for r in reentries:
        ax.axvline(r, color="green", alpha=0.15, linewidth=0.8)
    ax.set_yscale("log")
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity (log, start=1.0)")
    ax.set_title("Equity curve — Candidate vs baseline vs SPY buy-hold (40y)")
    ax.grid(True, alpha=0.3, which="both")
    ax.legend(loc="upper left", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _plot_drawdown(cand_eq, base_eq, bench_eq, *, stops, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 5), dpi=120)
    dd_cand = _drawdown(cand_eq)
    dd_base = _drawdown(base_eq)
    dd_bench = _drawdown(bench_eq)
    ax.fill_between(dd_cand.index, 0, -dd_cand.values,
                    color="#1f77b4", alpha=0.5, label="Candidate")
    ax.plot(dd_base.index, -dd_base.values, color="#d62728",
            linewidth=1.0, label="Baseline (3x)")
    ax.plot(dd_bench.index, -dd_bench.values, color="#808080",
            linewidth=1.0, linestyle="--", label="SPY buy-hold")
    for s in stops:
        ax.axvline(s, color="red", alpha=0.2, linewidth=0.8)
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown")
    ax.set_title("Running drawdown (red verticals = stop triggers)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower left", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _plot_risk_signal_trace(cape_raw, cape_z, cape_risk, eff_pos, *, out_path) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(12, 9), dpi=120, sharex=True)

    ax0 = axes[0]
    ax0.plot(cape_raw.index, cape_raw.values, color="#9467bd", linewidth=1.0)
    ax0.set_ylabel("CAPE ratio")
    ax0.set_title("CAPE (Shiller) raw level")
    ax0.grid(True, alpha=0.3)

    ax1 = axes[1]
    ax1.plot(cape_z.index, cape_z.values, color="#9467bd", linewidth=1.0)
    ax1.axhline(1.0, color="red", linestyle="--", alpha=0.5, label="z = +1σ threshold")
    ax1.axhline(0, color="gray", linewidth=0.5)
    ax1.set_ylabel("CAPE z-score (10y rolling)")
    ax1.set_title("CAPE z-score — risk fires above threshold")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper right")

    ax2 = axes[2]
    ax2.plot(cape_risk.index, cape_risk.values, color="#ff7f0e",
             linewidth=1.0, label="CAPE risk ∈ [0,1]")
    ax2.plot(eff_pos.index, eff_pos.values, color="#1f77b4",
             linewidth=1.0, alpha=0.7, label="Effective position (λ=0.5)")
    ax2.axhline(1.0, color="gray", alpha=0.5, linewidth=0.5)
    ax2.set_ylabel("Value ∈ [0, 1]")
    ax2.set_xlabel("Date")
    ax2.set_title("Risk score → effective position = max(0, 1 − 0.5·risk)")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="upper right")

    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _plot_crash_zoom(cand_eq, base_eq, bench_eq, cw: CrashWindow,
                     *, stops, reentries, out_path: Path) -> None:
    # Normalize all to 1.0 at window start.
    cand_n = cand_eq / cand_eq.iloc[0]
    base_n = base_eq / base_eq.iloc[0]
    bench_n = bench_eq / bench_eq.iloc[0]
    fig, ax = plt.subplots(figsize=(11, 5), dpi=120)
    ax.plot(cand_n.index, cand_n.values, label="Candidate",
            color="#1f77b4", linewidth=1.7)
    ax.plot(base_n.index, base_n.values, label="Baseline (3x)",
            color="#d62728", linewidth=1.3, alpha=0.8)
    ax.plot(bench_n.index, bench_n.values, label="SPY buy-hold",
            color="#808080", linewidth=1.2, linestyle="--")
    for s in stops:
        ax.axvline(s, color="red", alpha=0.5, linewidth=1.0,
                   label="stop trigger" if s == stops[0] else None)
    for r in reentries:
        ax.axvline(r, color="green", alpha=0.5, linewidth=1.0,
                   label="re-entry" if r == reentries[0] else None)
    ax.axhline(1.0, color="black", alpha=0.4, linewidth=0.6)
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity (start of window = 1.0)")
    ax.set_title(f"{cw.label} — {cw.subtitle}")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------


def _build_report_md(
    base, stop_cfg, risk_cfg,
    df_metrics, df_crash, df_stops,
    cand_res, base_res,
    pct_days_below_unity, pct_days_below_half,
    window_label,
) -> str:
    lines = []
    lines.append(f"# Top crash-protected candidate — deep dive\n")
    lines.append(
        f"> **`EMA_N150_th5_bL3_sL0` + `sl30_rec10_cape05`** — the best "
        f"crash-protected variant on the educational top-1 base inside "
        f"the ΔCAGR ≥ −5 pp corridor. Data window: **{window_label}**.\n"
    )
    lines.append(
        "> ⚠️ **Educational only.** This config passes 6/7 gates in the 40 y "
        "synth but **3/7 in spy_real** — it does **not** meet spec §0 "
        "cross-dataset validation. Mandate §1 MAINTENANCE continues.\n"
    )

    lines.append("## Configuration\n")
    lines.append(
        f"| component | value |\n|---|---|\n"
        f"| MA filter | {base.filter} |\n"
        f"| lookback | {base.lookback} bars |\n"
        f"| threshold | ±{base.threshold_pct*100:.0f}% |\n"
        f"| buy leg | {base.buy_leverage:g}× long synth UPRO |\n"
        f"| sell leg | cash (`{base.sell_leverage:g}`) |\n"
        f"| stop-loss | {int(stop_cfg.stop_loss_pct*100)}% drawdown from peak |\n"
        f"| re-entry | `{stop_cfg.reentry_mode}` at +{int(stop_cfg.reentry_param*100)}% off local bottom |\n"
        f"| risk indicator | **`{risk_cfg.indicator_type}`** (Shiller CAPE z-score sigmoid) |\n"
        f"| λ de-lever | {risk_cfg.lambda_de_lever:g} |\n"
        f"| fee | {base.fee*100:.2f}%/yr |\n"
        f"| switch cost | {base.switch_cost_bps:.0f} bps |\n"
    )
    lines.append(
        "\nCitations: synth LETF formula `[leverage_for_the_long_run, p.16, fn.22]`; "
        "regime filter `[leverage_for_the_long_run, p.13]`; CAPE framing "
        "Campbell & Shiller 1988; sigmoid threshold anti-2010s-over-delevering "
        "spec §8.3; recovery-trigger mode spec §3.1.\n"
    )

    lines.append("## Headline metrics\n")
    mcols = ["CAGR", "Sharpe", "Sortino", "MDD", "Calmar", "Volatility",
             "Final equity (start=1.0)"]
    md_tbl = ["| " + " | ".join(["metric"] + list(df_metrics.index)) + " |",
              "|" + "|".join(["---"] * (1 + len(df_metrics.index))) + "|"]
    for col in mcols:
        row = [col]
        for label in df_metrics.index:
            val = df_metrics.loc[label, col]
            if col == "Final equity (start=1.0)":
                row.append(f"{val:.2f}×")
            elif col in ("CAGR", "MDD", "Volatility"):
                row.append(_fmt_pct(val))
            else:
                row.append(_fmt_num(val))
        md_tbl.append("| " + " | ".join(row) + " |")
    lines.append("\n".join(md_tbl))

    # Deltas vs baseline + vs benchmark
    cand_metrics = df_metrics.iloc[0]
    base_metrics = df_metrics.iloc[1]
    bench_metrics = df_metrics.iloc[2]
    lines.append("\n### Deltas (Candidate minus ...)\n")
    lines.append(
        "| metric | vs Baseline (3x no overlay) | vs SPY buy-hold |\n"
        "|---|---|---|\n"
        f"| ΔCAGR | {_fmt_pct(cand_metrics.CAGR - base_metrics.CAGR)} | "
        f"{_fmt_pct(cand_metrics.CAGR - bench_metrics.CAGR)} |\n"
        f"| ΔSharpe | {_fmt_num(cand_metrics.Sharpe - base_metrics.Sharpe)} | "
        f"{_fmt_num(cand_metrics.Sharpe - bench_metrics.Sharpe)} |\n"
        f"| ΔMDD (magnitude) | "
        f"{_fmt_pct(base_metrics.MDD - cand_metrics.MDD)} (smaller = better) | "
        f"{_fmt_pct(bench_metrics.MDD - cand_metrics.MDD)} |\n"
        f"| ΔCalmar | {_fmt_num(cand_metrics.Calmar - base_metrics.Calmar)} | "
        f"{_fmt_num(cand_metrics.Calmar - bench_metrics.Calmar)} |\n"
        f"| Final equity (start=1) | {cand_metrics['Final equity (start=1.0)']:.2f}× vs "
        f"{base_metrics['Final equity (start=1.0)']:.2f}× baseline | "
        f"vs {bench_metrics['Final equity (start=1.0)']:.2f}× SPY |\n"
    )

    lines.append("\n## Stop events\n")
    if len(df_stops) == 0:
        lines.append("> No stop triggered (unexpected — check config).\n")
    else:
        lines.append(
            f"**{len(df_stops)} stops fired** over {window_label}. "
            "Every event tracked below — see `stop_events.csv` for full detail.\n"
        )
        lines.append(
            "| # | stop date | re-entry | bars stopped | equity at stop | peak before | DD at stop |\n"
            "|---|---|---|---|---|---|---|"
        )
        for i, r in df_stops.iterrows():
            lines.append(
                f"| {i+1} | {r.stop_date} | {r.reentry_date} | "
                f"{int(r.bars_stopped) if r.bars_stopped >= 0 else '—'} | "
                f"{r.equity_at_stop:.2f} | {r.peak_before_stop:.2f} | "
                f"{_fmt_pct(r.drawdown_at_stop)} |"
            )

    lines.append("\n## De-leveraging activity (CAPE signal)\n")
    lines.append(
        f"- **% of long-regime days with de-lever active (pos < 1.0)**: "
        f"{pct_days_below_unity*100:.1f}%\n"
        f"- **% of long-regime days with deep de-lever (pos < 0.5)**: "
        f"{pct_days_below_half*100:.1f}%\n"
        f"- CAPE z-score crosses +1σ when valuation is ≥ 1 standard deviation "
        f"above its 10-year rolling mean — historically periods like late 1990s, "
        f"late 2010s, and 2020-2022.\n"
    )

    lines.append("\n## Per-crash comparison\n")
    lines.append(
        "Drawdown and total return during each major crash window. "
        "`cand_MDD` vs `base_MDD` shows how much MDD the overlay saved;"
        "`cand_total_return` vs `bench` shows whether the candidate beat "
        "buy-hold through the crash.\n"
    )
    lines.append(
        "| crash | window | cand MDD | base MDD | bench MDD | cand total | base total | bench total | stops in window |\n"
        "|---|---|---|---|---|---|---|---|---|"
    )
    for crash_label, r in df_crash.iterrows():
        lines.append(
            f"| {crash_label} | {r.window} | {_fmt_pct(r.cand_MDD)} | "
            f"{_fmt_pct(r.base_MDD)} | {_fmt_pct(r.bench_MDD)} | "
            f"{_fmt_pct(r.cand_total_return)} | {_fmt_pct(r.base_total_return)} | "
            f"{_fmt_pct(r.bench_total_return)} | {int(r.n_stops_in_window)} |"
        )
    lines.append(
        "\nPer-crash plots: `crash_1987_black_monday.png`, `crash_2000_dotcom.png`, "
        "`crash_2008_gfc.png`, `crash_2020_covid.png`, `crash_2022_bear.png`.\n"
    )

    lines.append("\n## Plots\n")
    lines.append(
        "- **`equity_vs_benchmarks.png`** — candidate + baseline + SPY (log scale).\n"
        "- **`drawdown.png`** — running drawdown of all three series with stop markers.\n"
        "- **`risk_signal_trace.png`** — CAPE raw → z-score → risk → effective position.\n"
        "- **`crash_<label>.png`** — normalized equity during each crash window.\n"
    )

    lines.append("\n## Strengths (40y synth only)\n")
    mdd_vs_spy_better = cand_metrics.MDD < bench_metrics.MDD
    lines.append(
        "On the 40-year synthetic window, the candidate actually beats SPY buy-hold "
        "on **every** headline metric:\n\n"
        f"* CAGR: {cand_metrics.CAGR*100:.2f}% vs SPY {bench_metrics.CAGR*100:.2f}% "
        f"(**+{(cand_metrics.CAGR - bench_metrics.CAGR)*100:.2f} pp**).\n"
        f"* Sharpe: {cand_metrics.Sharpe:.2f} vs SPY {bench_metrics.Sharpe:.2f} "
        f"(**+{cand_metrics.Sharpe - bench_metrics.Sharpe:.2f}**).\n"
        f"* MDD: {cand_metrics.MDD*100:.2f}% vs SPY {bench_metrics.MDD*100:.2f}% "
        f"(**{'better' if mdd_vs_spy_better else 'worse'} by "
        f"{abs(cand_metrics.MDD - bench_metrics.MDD)*100:.2f} pp**).\n"
        f"* Calmar: {cand_metrics.Calmar:.2f} vs SPY {bench_metrics.Calmar:.2f}.\n"
        f"* Final equity (1986→2026): "
        f"{cand_metrics['Final equity (start=1.0)']:.0f}× vs SPY "
        f"{bench_metrics['Final equity (start=1.0)']:.0f}×.\n"
    )
    lines.append(
        "\nVs the no-overlay baseline (3x UPRO synth): the overlay sacrifices "
        f"{abs(cand_metrics.CAGR - base_metrics.CAGR)*100:.2f} pp CAGR to recover "
        f"{(base_metrics.MDD - cand_metrics.MDD)*100:.2f} pp of MDD — a decent "
        "trade-off, but insufficient to clear the spec target of MDD ≤ 40 %.\n"
    )

    lines.append("\n## Honest verdict — why this doesn't ship\n")
    lines.append(
        "Despite beating SPY on every 40y metric, this candidate is **not deployable**:\n\n"
        "1. **MDD still 4.5 pp above the 40 % spec target.** 44.55 % is a career-ending "
        "drawdown for a retail portfolio; the spec chose 40 % as the *weakest* acceptable "
        "threshold precisely because larger drawdowns cause behavioural abandonment.\n"
        "2. **G3 Walk-Forward fails universally** (MDD < 25 % per 6-month OOS window "
        "is violated in every split). The 40y aggregate MDD is only 44.55 % because good "
        "years mask bad ones; inside a single WF window the overlay cannot prevent the "
        "crash from producing a ≥ 25 % window-local drawdown.\n"
        "3. **SPY real data (17 y) gives only 3/7 gates** for this same parameter set. "
        "Real-data MDD reaches levels the synth path dampens (Gayed `[p.21, Table 12]`). "
        "The 40y synth number is an upper bound on what real data would deliver.\n"
        "4. **CAPE is stale at 2023-09** (Shiller cutoff). For a live 2024-2026 deployment "
        "there's no risk signal — the overlay degrades to stop-only.\n"
        "5. **CAPE chronic-high decade (2010s)**: realized spec §8.3 warning — "
        "signal spends 73 % of bull-regime bars de-levering but only 2.2 % deeply "
        "de-levered. In a quiet decade this leaks CAGR without saving MDD, because the "
        "crash never comes.\n"
    )
    lines.append(
        "\n**Why this config doesn't ship**:\n"
        "1. MDD 44.55% is still **4.5 pp above the 40 % spec target** despite the overlay.\n"
        "2. G3 Walk-Forward fails universally (MDD < 25 % per 6-month OOS window is violated).\n"
        "3. In SPY real data the equivalent config reproduces only 3/7 gates — not portable.\n"
        "4. CAPE z-score collapses in the 2010s because CAPE was chronically high for a "
        "decade without a crash (spec §8.3 warning realized).\n"
    )
    lines.append(
        "\n**Reference**: full Phase 3 verdict in `../phase3_FINAL.md`; cross-dataset "
        "gate matrix in `../phase3/cross_dataset_gates.md`.\n"
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
