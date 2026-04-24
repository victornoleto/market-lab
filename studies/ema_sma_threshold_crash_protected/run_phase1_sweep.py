"""Phase 1 — stop-loss sweep on top-20 base configs × 3 datasets.

Driver for the crash-protection evolution study (see
``studies/SPEC_crash_protection_evolution.md``, §5.1).

What this script does
---------------------

For each of the three baseline studies:

* ``ema_sma_threshold_educational`` — SPYSIM synth 1986-2026 (40y)
* ``ema_sma_threshold_spy_real``    — Tiingo SPY/SSO/UPRO 2009-2026 (17y)
* ``ema_sma_threshold_nasdaq_real`` — Tiingo QQQ/QLD/TQQQ 2010-2026 (16y)

we:

1. Load the top-K base configs from the study's ``configs.csv`` (already
   ranked by the composite score the study defined).
2. Expand each base into 43 stop-loss variants via
   :func:`expand_stop_loss_variants` (see module for the axis grid).
3. Simulate each variant with :func:`simulate_with_stop_loss`.
4. Compute CAGR / Sharpe / MDD / Calmar / Sortino / vol plus stop-specific
   stats (n_stops, avg_bars_stopped) and effectiveness deltas vs the
   variant-0 baseline of the same base config.
5. Emit per-dataset CSV + a top-20 markdown summary of the variants
   that reduce MDD most per pp of CAGR sacrificed.

Gates (7 statistical gates of the main sweep) are intentionally **not**
evaluated in Phase 1 — §6.1 reserves them for the final candidates that
survive to Phase 3+. Running 2 580 gate evaluations here would cost
hours and bias parameter choice.

Usage
-----

::

    # Default — all 3 datasets, top-20 bases, 43 variants each (~30 min)
    .venv/bin/python studies/ema_sma_threshold_crash_protected/run_phase1_sweep.py

    # Smoke — top-3 bases × educational only (~1 min)
    .venv/bin/python studies/ema_sma_threshold_crash_protected/run_phase1_sweep.py --smoke

    # One dataset only
    .venv/bin/python studies/ema_sma_threshold_crash_protected/run_phase1_sweep.py --dataset spy_real

Citations
---------
* Drawdown-from-peak stop trade-off: spec §8.1 / §8.2 (whipsaw cost).
* Honest alignment: ``[advances_fin_ml, p.31-34]`` (inherited from base
  simulator).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd

from ai_trade.backtest.data.testfolio_loader import (
    load_testfolio_returns,
    load_testfolio_series,
)
from ai_trade.backtest.grid.real_etf_regime_runner import (
    NDX_MARKET,
    SPY_MARKET,
    RealETFMarket,
    build_data_bundle,
)
from ai_trade.backtest.grid.stop_loss_variants import (
    Variant,
    expand_stop_loss_variants,
)
from ai_trade.backtest.metrics.performance import (
    cagr as _cagr,
    calmar as _calmar,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
    sortino as _sortino,
    volatility as _volatility,
)
from ai_trade.backtest.strategies.ema_sma_threshold_educational import (
    DEFAULT_FEE,
    EMASMAThresholdConfig,
    TRADING_DAYS_PER_YEAR,
    _synth_leveraged_returns,
    simulate_ema_sma_threshold,
)
from ai_trade.backtest.strategies.stop_loss_and_risk_signals import (
    StopLossConfig,
    StopLossResult,
    simulate_with_stop_loss,
)

STUDY_DIR = Path(__file__).parent
LOG_PATH = Path("logs/crash_protection_phase1.log")
REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Dataset adapters — one per base study
# ---------------------------------------------------------------------------


@dataclass
class DatasetContext:
    label: str  # folder slug
    source_study_dir: Path  # where to read top-K base configs from
    simulate_fn: callable  # (base_cfg, stop_cfg) -> StopLossResult
    window_label: str
    benchmark_label: str


def _parse_base_config_from_row(row: pd.Series) -> EMASMAThresholdConfig:
    return EMASMAThresholdConfig(
        filter=str(row["filter"]),
        lookback=int(row["lookback"]),
        threshold_pct=float(row["threshold_pct"]),
        buy_leverage=float(row["buy_leverage"]),
        sell_leverage=float(row["sell_leverage"]),
        fee=DEFAULT_FEE,
        switch_cost_bps=15.0,
        tax_rate=0.0,  # PURE view; tax handled at reporting if needed later.
    )


def _load_top_k_configs(study_dir: Path, top_k: int) -> list[EMASMAThresholdConfig]:
    csv = study_dir / "configs.csv"
    if not csv.exists():
        raise FileNotFoundError(f"configs.csv not found in {study_dir}")
    df = pd.read_csv(csv).sort_values("rank").head(top_k)
    return [_parse_base_config_from_row(row) for _, row in df.iterrows()]


def _build_educational_context(top_k: int) -> tuple[DatasetContext, list[EMASMAThresholdConfig]]:
    spx_prices = load_testfolio_series("SPYSIM")
    spx_returns = load_testfolio_returns("SPYSIM")

    def _simulate(base_cfg: EMASMAThresholdConfig, stop_cfg: StopLossConfig) -> StopLossResult:
        # Wrap synth path: compute legs then call simulate_with_stop_loss.
        long_leg = _synth_leveraged_returns(spx_returns, base_cfg.buy_leverage, base_cfg.fee)
        if base_cfg.sell_leverage == 0.0:
            cash_daily = base_cfg.cash_rate_annual / TRADING_DAYS_PER_YEAR
            sell_leg = pd.Series(cash_daily, index=spx_returns.index)
        else:
            sell_leg = _synth_leveraged_returns(
                spx_returns, base_cfg.sell_leverage, base_cfg.fee
            )
        return simulate_with_stop_loss(
            signal_prices=spx_prices,
            buy_leg_returns=long_leg,
            sell_leg_returns=sell_leg,
            cfg=base_cfg,
            stop_cfg=stop_cfg,
        )

    source_dir = REPO_ROOT / "studies" / "ema_sma_threshold_educational"
    top_configs = _load_top_k_configs(source_dir, top_k)
    ctx = DatasetContext(
        label="educational",
        source_study_dir=source_dir,
        simulate_fn=_simulate,
        window_label=f"{spx_returns.index[0].date()}→{spx_returns.index[-1].date()} (~40y)",
        benchmark_label="SPY buy-hold (synth SPYSIM)",
    )
    return ctx, top_configs


def _build_real_etf_context(
    market: RealETFMarket, top_k: int, study_label: str
) -> tuple[DatasetContext, list[EMASMAThresholdConfig]]:
    source_dir = REPO_ROOT / "studies" / study_label
    top_configs = _load_top_k_configs(source_dir, top_k)

    leverages = sorted({int(cfg.buy_leverage) for cfg in top_configs if cfg.buy_leverage > 0})
    bundle = build_data_bundle(market, tuple(float(x) for x in leverages))

    def _simulate(base_cfg: EMASMAThresholdConfig, stop_cfg: StopLossConfig) -> StopLossResult:
        buy_key = f"buy_L{int(base_cfg.buy_leverage)}"
        buy_leg = bundle[buy_key]
        signal_prices = bundle["signal_prices"]
        signal_returns = bundle["signal_returns"]
        if base_cfg.sell_leverage == 0.0:
            cash_daily = base_cfg.cash_rate_annual / TRADING_DAYS_PER_YEAR
            sell_leg = pd.Series(cash_daily, index=signal_returns.index)
        else:
            sell_leg = _synth_leveraged_returns(
                signal_returns, base_cfg.sell_leverage, base_cfg.fee
            )
        return simulate_with_stop_loss(
            signal_prices=signal_prices,
            buy_leg_returns=buy_leg,
            sell_leg_returns=sell_leg,
            cfg=base_cfg,
            stop_cfg=stop_cfg,
        )

    meta = bundle["_meta"]
    ctx = DatasetContext(
        label=market.label + "_real",
        source_study_dir=source_dir,
        simulate_fn=_simulate,
        window_label=f"{pd.Timestamp(meta['start']).date()}→{pd.Timestamp(meta['end']).date()}",
        benchmark_label=f"{market.signal_ticker} buy-hold",
    )
    return ctx, top_configs


# ---------------------------------------------------------------------------
# Metrics per variant
# ---------------------------------------------------------------------------


@dataclass
class VariantMetrics:
    variant: Variant
    cagr: float
    sharpe: float
    max_drawdown: float
    calmar: float
    sortino: float
    volatility: float
    n_switches: int
    n_stops_triggered: int
    avg_bars_stopped: float  # NaN if no stop triggered
    longest_stop_bars: int
    # Deltas vs baseline (same base_cfg, stop=None) — filled after pass 1.
    delta_cagr: float = float("nan")
    delta_mdd: float = float("nan")
    effectiveness: float = float("nan")


def _compute_variant_metrics(v: Variant, res: StopLossResult) -> VariantMetrics:
    eq = res.equity
    rets = res.daily_returns
    if eq.iloc[0] == 0 or np.isnan(eq.iloc[0]):
        return VariantMetrics(
            variant=v, cagr=float("nan"), sharpe=float("nan"),
            max_drawdown=float("nan"), calmar=float("nan"),
            sortino=float("nan"), volatility=float("nan"),
            n_switches=res.n_switches, n_stops_triggered=res.n_stops_triggered,
            avg_bars_stopped=float("nan"), longest_stop_bars=0,
        )
    bars_stopped = []
    for ev in res.stop_events:
        if ev.reentry_bar is not None:
            bars_stopped.append(ev.reentry_bar - ev.stop_bar)
    longest = int(max(bars_stopped)) if bars_stopped else 0
    avg = float(np.mean(bars_stopped)) if bars_stopped else float("nan")
    return VariantMetrics(
        variant=v,
        cagr=float(_cagr(eq, TRADING_DAYS_PER_YEAR)),
        sharpe=float(_sharpe(rets, TRADING_DAYS_PER_YEAR)),
        max_drawdown=float(_max_drawdown(eq)),
        calmar=float(_calmar(eq, TRADING_DAYS_PER_YEAR)),
        sortino=float(_sortino(rets, TRADING_DAYS_PER_YEAR)),
        volatility=float(_volatility(rets, TRADING_DAYS_PER_YEAR)),
        n_switches=res.n_switches,
        n_stops_triggered=res.n_stops_triggered,
        avg_bars_stopped=avg,
        longest_stop_bars=longest,
    )


def _fill_effectiveness_deltas(metrics: list[VariantMetrics]) -> None:
    """Set delta_cagr / delta_mdd / effectiveness in place.

    Sign convention (both deltas are "improvement over baseline"):

    * ``delta_cagr`` — positive means variant has higher CAGR than
      baseline. Usually negative for stops (they sacrifice CAGR).
    * ``delta_mdd`` — positive means variant has **smaller** MDD
      magnitude than baseline (i.e. the stop *reduced* drawdown). Since
      :func:`max_drawdown` returns a positive magnitude in [0, 1], this
      is ``base - variant``.
    * ``effectiveness`` = ``delta_mdd / max(|delta_cagr|, 1e-3)``.
      Positive effectiveness = MDD reduced per unit of CAGR cost.
      A variant with no CAGR cost but meaningful MDD reduction scores
      very high (denominator floors at 0.1 pp to avoid division blow-up).

    For each variant, baseline = the stop=None variant with the same
    base_cfg.cfg_id (variant_idx == 0).
    """
    baseline_by_id: dict[str, VariantMetrics] = {}
    for m in metrics:
        if m.variant.variant_idx == 0:
            baseline_by_id[m.variant.base_cfg.cfg_id] = m
    for m in metrics:
        base = baseline_by_id[m.variant.base_cfg.cfg_id]
        if m.variant.variant_idx == 0:
            m.delta_cagr = 0.0
            m.delta_mdd = 0.0
            m.effectiveness = 0.0
            continue
        m.delta_cagr = m.cagr - base.cagr
        m.delta_mdd = base.max_drawdown - m.max_drawdown
        denom = max(abs(m.delta_cagr), 1e-3)
        m.effectiveness = m.delta_mdd / denom


# ---------------------------------------------------------------------------
# CSV + MD emission per dataset
# ---------------------------------------------------------------------------


def _metrics_to_dataframe(metrics: list[VariantMetrics]) -> pd.DataFrame:
    rows = []
    for m in metrics:
        v = m.variant
        sl = v.stop_cfg.stop_loss_pct
        rows.append({
            "base_rank": v.base_rank,
            "base_cfg_id": v.base_cfg.cfg_id,
            "variant_idx": v.variant_idx,
            "variant_id": v.variant_id,
            "stop_tag": v.stop_tag,
            "stop_loss_pct": sl if sl is not None else np.nan,
            "reentry_mode": (
                "—" if sl is None else v.stop_cfg.reentry_mode
            ),
            "reentry_param": v.stop_cfg.reentry_param if sl is not None else np.nan,
            "cagr": m.cagr,
            "sharpe": m.sharpe,
            "max_drawdown": m.max_drawdown,
            "calmar": m.calmar,
            "sortino": m.sortino,
            "volatility": m.volatility,
            "n_switches": m.n_switches,
            "n_stops": m.n_stops_triggered,
            "avg_bars_stopped": m.avg_bars_stopped,
            "longest_stop_bars": m.longest_stop_bars,
            "delta_cagr": m.delta_cagr,
            "delta_mdd": m.delta_mdd,
            "effectiveness": m.effectiveness,
            "base_filter": v.base_cfg.filter,
            "base_lookback": v.base_cfg.lookback,
            "base_threshold_pct": v.base_cfg.threshold_pct,
            "base_buy_leverage": v.base_cfg.buy_leverage,
            "base_sell_leverage": v.base_cfg.sell_leverage,
        })
    return pd.DataFrame(rows)


def _fmt_pct(x: float, digits: int = 2) -> str:
    if x is None or np.isnan(x) or np.isinf(x):
        return "—"
    return f"{x * 100:+.{digits}f}%"


def _fmt_num(x: float, digits: int = 2) -> str:
    if x is None or np.isnan(x) or np.isinf(x):
        return "—"
    return f"{x:.{digits}f}"


def _emit_dataset_report(
    ctx: DatasetContext,
    metrics: list[VariantMetrics],
    out_dir: Path,
    log: logging.Logger,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    df = _metrics_to_dataframe(metrics)
    df.to_csv(out_dir / "configs_stop_loss.csv", index=False)
    log.info("    wrote %s (%d rows)", out_dir / "configs_stop_loss.csv", len(df))

    # Best variant per base cfg by lowest MDD (most positive delta_mdd).
    best_by_base = (
        df[df["variant_idx"] != 0]
        .sort_values(["base_rank", "delta_mdd"], ascending=[True, False])
        .groupby("base_rank", as_index=False)
        .first()
    )
    best_by_base.to_csv(out_dir / "best_mdd_reducer_per_base.csv", index=False)

    # Top-20 variants by effectiveness (global, across all bases).
    top_effective = (
        df[(df["variant_idx"] != 0) & (df["delta_mdd"] > 0)]
        .sort_values("effectiveness", ascending=False)
        .head(20)
        .reset_index(drop=True)
    )

    md = [f"# Phase 1 — {ctx.label}\n"]
    md.append(f"> Dataset window: **{ctx.window_label}** · "
              f"Benchmark: **{ctx.benchmark_label}**\n")
    md.append(f"## Scope\n")
    md.append(
        f"- Base configs expanded: **{df['base_rank'].nunique()}** "
        f"(top-{df['base_rank'].nunique()} by the source study's composite).\n"
        f"- Variants per base: **{(df['variant_idx'].nunique())}** "
        "(1 baseline + 42 stop-loss combinations).\n"
        f"- Total simulations: **{len(df)}**\n"
        f"- Gates: not evaluated (Phase 1 is exploratory per spec §6.1).\n"
    )

    # Baseline-only table for reference.
    baselines = df[df["variant_idx"] == 0].sort_values("base_rank")
    md.append("## Baseline (no stop) — reference point\n")
    md.append(
        "| rank | cfg | CAGR | Sharpe | MDD | n_switches |\n"
        "|---|---|---|---|---|---|"
    )
    for _, row in baselines.iterrows():
        md.append(
            f"| {int(row['base_rank'])} | `{row['base_cfg_id']}` | "
            f"{_fmt_pct(row['cagr'])} | {_fmt_num(row['sharpe'])} | "
            f"{_fmt_pct(row['max_drawdown'])} | {int(row['n_switches'])} |"
        )
    md.append("")

    md.append("## Top-20 variants by MDD reduction effectiveness\n")
    md.append(
        "> *Effectiveness* = Δmdd (pp) / max(|ΔCAGR|, 0.1pp). "
        "Positive effectiveness means the stop reduced MDD; a high value "
        "means the MDD reduction is large relative to the CAGR sacrificed. "
        "Variants that *increased* MDD are excluded.\n"
    )
    if len(top_effective) == 0:
        md.append("> **No variant improved MDD over its baseline on this dataset.**\n")
    else:
        md.append(
            "| # | variant | stop | mode | param | CAGR | ΔCAGR | MDD | ΔMDD | n_stops | longest (d) | eff. |\n"
            "|---|---|---|---|---|---|---|---|---|---|---|---|"
        )
        for i, row in top_effective.iterrows():
            md.append(
                f"| {i+1} | `{row['variant_id']}` | "
                f"{int(row['stop_loss_pct']*100)}% | "
                f"{row['reentry_mode']} | {row['reentry_param']:g} | "
                f"{_fmt_pct(row['cagr'])} | {_fmt_pct(row['delta_cagr'])} | "
                f"{_fmt_pct(row['max_drawdown'])} | {_fmt_pct(row['delta_mdd'])} | "
                f"{int(row['n_stops'])} | {int(row['longest_stop_bars'])} | "
                f"{row['effectiveness']:.2f} |"
            )
    md.append("")

    # Breakdown by mode / stop_pct / cooldown / recovery.
    md.append("## Average effect by mode\n")
    md.append("> Means across all (base, variant) pairs within the same mode.\n")
    md.append(
        "| mode | n | ΔCAGR (avg) | ΔMDD (avg) | n_stops (avg) |\n"
        "|---|---|---|---|---|"
    )
    non_base = df[df["variant_idx"] != 0]
    for mode in ("next_signal", "time_cooldown", "recovery_trigger"):
        sub = non_base[non_base["reentry_mode"] == mode]
        if len(sub) == 0:
            continue
        md.append(
            f"| {mode} | {len(sub)} | {_fmt_pct(sub['delta_cagr'].mean())} | "
            f"{_fmt_pct(sub['delta_mdd'].mean())} | "
            f"{sub['n_stops'].mean():.1f} |"
        )
    md.append("")

    md.append("## Average effect by stop level\n")
    md.append(
        "| stop_loss_pct | n | ΔCAGR (avg) | ΔMDD (avg) | n_stops (avg) | frac positive (MDD↓) |\n"
        "|---|---|---|---|---|---|"
    )
    for sl in sorted(non_base["stop_loss_pct"].dropna().unique()):
        sub = non_base[non_base["stop_loss_pct"] == sl]
        frac_pos = float((sub["delta_mdd"] > 0).mean())
        md.append(
            f"| {int(sl*100)}% | {len(sub)} | {_fmt_pct(sub['delta_cagr'].mean())} | "
            f"{_fmt_pct(sub['delta_mdd'].mean())} | "
            f"{sub['n_stops'].mean():.1f} | {frac_pos*100:.1f}% |"
        )
    md.append("")

    (out_dir / "phase1_summary.md").write_text("\n".join(md), encoding="utf-8")
    log.info("    wrote %s", out_dir / "phase1_summary.md")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def _setup_logging() -> logging.Logger:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("phase1_stop_loss")
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


def _run_dataset(
    ctx: DatasetContext,
    top_configs: list[EMASMAThresholdConfig],
    out_dir: Path,
    *,
    smoke: bool,
    log: logging.Logger,
) -> None:
    kwargs = {}
    if smoke:
        kwargs = {
            "stop_levels": (0.25, 0.35),
            "cooldowns": (63,),
            "recovery_pcts": (0.10,),
        }
    variants = expand_stop_loss_variants(top_configs, **kwargs)
    log.info(
        "  %s — %d base × %d variants = %d sims",
        ctx.label, len(top_configs), len(variants) // max(len(top_configs), 1), len(variants),
    )

    metrics: list[VariantMetrics] = []
    t_start = time.time()
    for k, v in enumerate(variants):
        if k % max(len(variants) // 20, 1) == 0 and k > 0:
            elapsed = time.time() - t_start
            rate = k / elapsed if elapsed > 0 else 0.0
            eta = (len(variants) - k) / rate if rate > 0 else 0.0
            log.info(
                "    [%d/%d] %.1fs elapsed, %.1f sims/s, ETA %.0fs",
                k, len(variants), elapsed, rate, eta,
            )
        res = ctx.simulate_fn(v.base_cfg, v.stop_cfg)
        metrics.append(_compute_variant_metrics(v, res))

    log.info(
        "    sweep done in %.1fs (%.1f sims/s)",
        time.time() - t_start,
        len(variants) / max(time.time() - t_start, 1e-9),
    )
    _fill_effectiveness_deltas(metrics)
    _emit_dataset_report(ctx, metrics, out_dir, log)


def _emit_phase1_final(
    dataset_labels: list[str], out_dir: Path, log: logging.Logger
) -> None:
    """Compile the cross-dataset phase1_FINAL.md."""
    # Collect top-10 per dataset and identify variants appearing in top-K of multiple.
    all_df: dict[str, pd.DataFrame] = {}
    for lab in dataset_labels:
        csv = out_dir / "phase1" / lab / "configs_stop_loss.csv"
        if not csv.exists():
            log.warning("missing %s — skipping in FINAL", csv)
            continue
        all_df[lab] = pd.read_csv(csv)

    md = ["# Phase 1 — Stop-loss sweep · FINAL\n"]
    md.append("> Cross-dataset comparison of stop-loss overlays on top-20 base "
              "configs. See per-dataset `phase1/<dataset>/phase1_summary.md` "
              "for the full breakdown.\n")

    md.append("## Scope\n")
    for lab, df in all_df.items():
        md.append(
            f"- **{lab}**: {df['base_rank'].nunique()} bases × "
            f"{df['variant_idx'].nunique()} variants = {len(df)} sims\n"
        )
    md.append("")

    md.append("## Baselines (no stop) across datasets\n")
    md.append(
        "| dataset | top-1 base | CAGR | MDD | top-1 baseline vs. top-20 avg MDD |\n"
        "|---|---|---|---|---|"
    )
    for lab, df in all_df.items():
        base_rows = df[df["variant_idx"] == 0]
        top1 = base_rows[base_rows["base_rank"] == 1].iloc[0]
        avg_mdd = float(base_rows["max_drawdown"].mean())
        md.append(
            f"| {lab} | `{top1['base_cfg_id']}` | "
            f"{_fmt_pct(top1['cagr'])} | {_fmt_pct(top1['max_drawdown'])} | "
            f"top-20 avg MDD: {_fmt_pct(avg_mdd)} |"
        )
    md.append("")

    md.append("## Cross-dataset top variants (appears in top-20 effectiveness in ≥2 datasets)\n")
    top_ids_per_dataset: dict[str, set[str]] = {}
    for lab, df in all_df.items():
        non_base = df[(df["variant_idx"] != 0) & (df["delta_mdd"] > 0)]
        top20 = non_base.nlargest(20, "effectiveness")
        # Key by (stop_tag, base_cfg_id) so it cross-references exact
        # base+stop combos — not just the stop tag.
        top_ids_per_dataset[lab] = set(
            zip(top20["base_cfg_id"].astype(str), top20["stop_tag"].astype(str))
        )

    # Intersect
    if len(top_ids_per_dataset) >= 2:
        from functools import reduce
        from operator import and_
        common = reduce(and_, top_ids_per_dataset.values())
        if common:
            md.append(
                "| base_cfg_id | stop_tag | " +
                " | ".join(f"{lab} ΔCAGR / ΔMDD / eff" for lab in dataset_labels) +
                " |\n" +
                "|---|---|" + "|".join(["---"] * len(dataset_labels)) + "|"
            )
            for base_id, tag in sorted(common):
                cells = [f"`{base_id}`", tag]
                for lab in dataset_labels:
                    row = all_df.get(lab)
                    if row is None:
                        cells.append("—")
                        continue
                    match = row[(row["base_cfg_id"] == base_id) & (row["stop_tag"] == tag)]
                    if len(match) == 0:
                        cells.append("—")
                        continue
                    r = match.iloc[0]
                    cells.append(
                        f"{_fmt_pct(r['delta_cagr'])} / {_fmt_pct(r['delta_mdd'])} / "
                        f"{r['effectiveness']:.2f}"
                    )
                md.append("| " + " | ".join(cells) + " |")
        else:
            md.append("> *No (base_cfg, stop_tag) pair appears in the top-20 "
                      "effectiveness of all listed datasets.* Cross-check which "
                      "stop tags appear in ≥2 datasets using the per-dataset "
                      "summaries.\n")
    md.append("")

    md.append("## Key questions (spec §5.1)\n")
    md.append(
        "- **Does any stop reduce MDD from 54% (educational top-1) to ≤ 40% "
        "without losing more than 3-5pp CAGR?** → see educational top-effectiveness table.\n"
        "- **Which mode dominates** (next_signal / time_cooldown / recovery_trigger)? "
        "→ compare `Average effect by mode` in each per-dataset summary.\n"
        "- **Which stop level (15-40%) gives the best Δmdd / ΔCAGR trade-off?** "
        "→ `Average effect by stop level` per dataset.\n"
    )

    md.append("## Next — Phase 2\n")
    md.append(
        "- Take the top-K base × stop combos that *reduce MDD* in **all 3** "
        "datasets (not just one), carry to Phase 2 (risk-signal de-leveraging).\n"
        "- Phase 3 will fuse the survivors with Phase 2 winners and run the "
        "full 7-gate battery.\n"
    )
    md.append("\n---\n*Citations: spec §3.1 (stop-loss axes) / §5.1 (phase-1 metrics) / "
              "§8.1-8.2 (whipsaw trade-off). Base simulator honest alignment: "
              "`[advances_fin_ml, p.31-34]`.*")

    (out_dir / "phase1_FINAL.md").write_text("\n".join(md), encoding="utf-8")
    log.info("wrote %s", out_dir / "phase1_FINAL.md")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        choices=("all", "educational", "spy_real", "ndx_real"),
        default="all",
    )
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--smoke", action="store_true",
                        help="Top-3 bases × 5 variants each (~1 min total)")
    args = parser.parse_args()

    log = _setup_logging()
    t0 = time.time()

    top_k = args.top_k if not args.smoke else 3
    datasets_to_run = (
        ["educational", "spy_real", "ndx_real"]
        if args.dataset == "all"
        else [args.dataset]
    )
    if args.smoke and args.dataset == "all":
        datasets_to_run = ["educational"]  # smoke = educational only

    completed_labels: list[str] = []
    for label in datasets_to_run:
        log.info("=== %s ===", label)
        if label == "educational":
            ctx, top_cfgs = _build_educational_context(top_k)
        elif label == "spy_real":
            ctx, top_cfgs = _build_real_etf_context(
                SPY_MARKET, top_k, "ema_sma_threshold_spy_real"
            )
        elif label == "ndx_real":
            ctx, top_cfgs = _build_real_etf_context(
                NDX_MARKET, top_k, "ema_sma_threshold_nasdaq_real"
            )
        else:
            raise ValueError(label)
        out_dir = STUDY_DIR / "phase1" / ctx.label
        _run_dataset(ctx, top_cfgs, out_dir, smoke=args.smoke, log=log)
        completed_labels.append(ctx.label)

    if len(completed_labels) > 0:
        _emit_phase1_final(completed_labels, STUDY_DIR, log)

    log.info("TOTAL wall time: %.1fs", time.time() - t0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
