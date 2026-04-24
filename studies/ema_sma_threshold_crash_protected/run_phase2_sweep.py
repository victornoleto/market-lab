"""Phase 2 — risk-signal de-leveraging sweep on top-20 bases × 3 datasets.

Driver for the crash-protection evolution study (spec §5.2).

What this script does
---------------------

For each of the three baseline studies (educational synth, SPY real,
NDX real):

1. Load the top-K (default 20) base configs from the source study's
   ``configs.csv``.
2. Build a daily trading index from the source data bundle.
3. Load all 4 macro indicators (EBP, term spread, CAPE, VIX) aligned to
   that index with the publish-lags specified in
   :mod:`ai_trade.backtest.data.macro_data_loader`.
4. Compute per-indicator risk scores and the equal-weight composite via
   :mod:`ai_trade.backtest.signals.risk_score`.
5. Expand the cartesian 20 bases × 5 indicators × 4 lambda values → 400
   per-dataset variants (1 200 total across 3 datasets).
6. Simulate each variant with
   :func:`simulate_with_risk_signal`.
7. Compute CAGR / Sharpe / MDD / Calmar + deltas vs the λ=0 baseline
   of the same base-config × indicator pair.
8. Emit per-dataset CSV + markdown summary + cross-dataset
   ``phase2_FINAL.md``.

Gates are intentionally not evaluated — Phase 2 is exploratory
(spec §6.1).

Usage
-----
::

    .venv/bin/python studies/ema_sma_threshold_crash_protected/run_phase2_sweep.py
    .venv/bin/python studies/ema_sma_threshold_crash_protected/run_phase2_sweep.py --smoke
    .venv/bin/python studies/ema_sma_threshold_crash_protected/run_phase2_sweep.py --dataset spy_real

Citations
---------
* spec §3.1-B, §5.2, §8.3, §8.5.
* honest alignment ``[advances_fin_ml, p.31-34]``.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd

from ai_trade.backtest.data.macro_data_loader import (
    DEFAULT_CACHE as MACRO_CACHE,
    load_all_indicators,
)
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
from ai_trade.backtest.metrics.performance import (
    cagr as _cagr,
    calmar as _calmar,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
    sortino as _sortino,
    volatility as _volatility,
)
from ai_trade.backtest.signals.risk_score import (
    INDICATOR_SPECS,
    compute_composite_risk,
    compute_risk_score,
)
from ai_trade.backtest.strategies.ema_sma_threshold_educational import (
    DEFAULT_FEE,
    EMASMAThresholdConfig,
    TRADING_DAYS_PER_YEAR,
    _synth_leveraged_returns,
)
from ai_trade.backtest.strategies.stop_loss_and_risk_signals import (
    RiskSignalConfig,
    RiskSignalResult,
    VALID_INDICATORS,
    simulate_with_risk_signal,
)

STUDY_DIR = Path(__file__).parent
LOG_PATH = Path("logs/crash_protection_phase2.log")
REPO_ROOT = Path(__file__).resolve().parents[2]

LAMBDA_VALUES: tuple[float, ...] = (0.0, 0.3, 0.5, 0.7)
INDICATORS_TO_SWEEP: tuple[str, ...] = ("ebp", "term_spread", "cape", "vix", "composite")


# ---------------------------------------------------------------------------
# Dataset contexts
# ---------------------------------------------------------------------------


@dataclass
class DatasetContext:
    label: str
    source_study_dir: Path
    simulate_fn: callable  # (base_cfg, risk_series, risk_cfg) -> RiskSignalResult
    window_label: str
    daily_index: pd.DatetimeIndex


def _parse_base_config_from_row(row: pd.Series) -> EMASMAThresholdConfig:
    return EMASMAThresholdConfig(
        filter=str(row["filter"]),
        lookback=int(row["lookback"]),
        threshold_pct=float(row["threshold_pct"]),
        buy_leverage=float(row["buy_leverage"]),
        sell_leverage=float(row["sell_leverage"]),
        fee=DEFAULT_FEE,
        switch_cost_bps=15.0,
        tax_rate=0.0,
    )


def _load_top_k_configs(study_dir: Path, top_k: int) -> list[EMASMAThresholdConfig]:
    csv = study_dir / "configs.csv"
    df = pd.read_csv(csv).sort_values("rank").head(top_k)
    return [_parse_base_config_from_row(r) for _, r in df.iterrows()]


def _build_educational_context(top_k: int) -> tuple[DatasetContext, list[EMASMAThresholdConfig]]:
    spx_prices = load_testfolio_series("SPYSIM")
    spx_returns = load_testfolio_returns("SPYSIM")
    daily_idx = spx_returns.index

    def _simulate(base_cfg, risk_series, risk_cfg):
        long_leg = _synth_leveraged_returns(spx_returns, base_cfg.buy_leverage, base_cfg.fee)
        if base_cfg.sell_leverage == 0.0:
            cash_daily = base_cfg.cash_rate_annual / TRADING_DAYS_PER_YEAR
            sell_leg = pd.Series(cash_daily, index=spx_returns.index)
        else:
            sell_leg = _synth_leveraged_returns(
                spx_returns, base_cfg.sell_leverage, base_cfg.fee
            )
        return simulate_with_risk_signal(
            signal_prices=spx_prices, buy_leg_returns=long_leg,
            sell_leg_returns=sell_leg, cfg=base_cfg,
            risk_series=risk_series, risk_cfg=risk_cfg,
        )

    src = REPO_ROOT / "studies" / "ema_sma_threshold_educational"
    top = _load_top_k_configs(src, top_k)
    ctx = DatasetContext(
        label="educational",
        source_study_dir=src,
        simulate_fn=_simulate,
        window_label=f"{daily_idx[0].date()}→{daily_idx[-1].date()} (~40y synth)",
        daily_index=daily_idx,
    )
    return ctx, top


def _build_real_context(
    market: RealETFMarket, top_k: int, study_label: str
) -> tuple[DatasetContext, list[EMASMAThresholdConfig]]:
    src = REPO_ROOT / "studies" / study_label
    top = _load_top_k_configs(src, top_k)
    leverages = sorted({int(cfg.buy_leverage) for cfg in top if cfg.buy_leverage > 0})
    bundle = build_data_bundle(market, tuple(float(x) for x in leverages))
    daily_idx = bundle["signal_returns"].index

    def _simulate(base_cfg, risk_series, risk_cfg):
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
        return simulate_with_risk_signal(
            signal_prices=signal_prices, buy_leg_returns=buy_leg,
            sell_leg_returns=sell_leg, cfg=base_cfg,
            risk_series=risk_series, risk_cfg=risk_cfg,
        )

    meta = bundle["_meta"]
    ctx = DatasetContext(
        label=market.label + "_real",
        source_study_dir=src,
        simulate_fn=_simulate,
        window_label=f"{pd.Timestamp(meta['start']).date()}→{pd.Timestamp(meta['end']).date()}",
        daily_index=daily_idx,
    )
    return ctx, top


# ---------------------------------------------------------------------------
# Build risk-series dict per dataset
# ---------------------------------------------------------------------------


def _build_risk_series(daily_index: pd.DatetimeIndex, log: logging.Logger) -> dict[str, pd.Series]:
    raw = load_all_indicators(daily_index, cache_dir=MACRO_CACHE)
    risks: dict[str, pd.Series] = {}
    for name in ("ebp", "term_spread", "cape", "vix"):
        spec = INDICATOR_SPECS[name]
        series = raw[name]
        # Adaptive window: don't require more window than dataset length.
        effective_window = min(spec.window, max(int(len(series) * 0.25), 30))
        if effective_window != spec.window:
            log.info(
                "    %s: window %d → %d (dataset only %d bars)",
                name, spec.window, effective_window, len(series),
            )
            spec = replace(spec, window=effective_window)
        risks[name] = compute_risk_score(series, spec)
        active = risks[name].notna().sum()
        log.info(
            "    %s: first active=%s, active-bars=%d/%d (%.1f%%)",
            name,
            str(risks[name].dropna().index[0].date()) if active > 0 else "never",
            active, len(daily_index), 100 * active / len(daily_index),
        )

    risks["composite"] = compute_composite_risk(risks)
    active = risks["composite"].notna().sum()
    log.info(
        "    composite: first active=%s, mean=%.3f, max=%.3f",
        str(risks["composite"].dropna().index[0].date()) if active > 0 else "never",
        float(risks["composite"].mean()), float(risks["composite"].max()),
    )
    return risks


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


@dataclass
class Phase2Metrics:
    base_rank: int
    base_cfg_id: str
    indicator: str
    lambda_de_lever: float
    cagr: float
    sharpe: float
    max_drawdown: float
    calmar: float
    sortino: float
    volatility: float
    n_switches: int
    mean_position: float  # average effective position when regime=+1
    delta_cagr: float = float("nan")
    delta_mdd: float = float("nan")
    effectiveness: float = float("nan")


def _compute_metrics(
    base_rank: int, base_cfg: EMASMAThresholdConfig,
    indicator: str, lam: float, res: RiskSignalResult,
) -> Phase2Metrics:
    eq = res.equity
    rets = res.daily_returns
    regime = res.regime
    # Mean position across bull bars
    pos = res.effective_position
    long_pos = pos.where(regime == 1).dropna()
    mean_pos = float(long_pos.mean()) if len(long_pos) > 0 else float("nan")
    return Phase2Metrics(
        base_rank=base_rank,
        base_cfg_id=base_cfg.cfg_id,
        indicator=indicator,
        lambda_de_lever=lam,
        cagr=float(_cagr(eq, TRADING_DAYS_PER_YEAR)),
        sharpe=float(_sharpe(rets, TRADING_DAYS_PER_YEAR)),
        max_drawdown=float(_max_drawdown(eq)),
        calmar=float(_calmar(eq, TRADING_DAYS_PER_YEAR)),
        sortino=float(_sortino(rets, TRADING_DAYS_PER_YEAR)),
        volatility=float(_volatility(rets, TRADING_DAYS_PER_YEAR)),
        n_switches=res.n_switches,
        mean_position=mean_pos,
    )


def _fill_deltas(metrics: list[Phase2Metrics]) -> None:
    """Deltas vs the λ=0 variant of the same (base_cfg_id, indicator) pair.

    With λ=0, the simulation is identical for all indicators — but we
    keep the baseline-per-indicator convention so downstream tables are
    trivially grouped.
    """
    baseline: dict[tuple[str, str], Phase2Metrics] = {}
    for m in metrics:
        if m.lambda_de_lever == 0.0:
            baseline[(m.base_cfg_id, m.indicator)] = m
    for m in metrics:
        base = baseline[(m.base_cfg_id, m.indicator)]
        if m.lambda_de_lever == 0.0:
            m.delta_cagr = 0.0
            m.delta_mdd = 0.0
            m.effectiveness = 0.0
            continue
        m.delta_cagr = m.cagr - base.cagr
        m.delta_mdd = base.max_drawdown - m.max_drawdown
        denom = max(abs(m.delta_cagr), 1e-3)
        m.effectiveness = m.delta_mdd / denom


# ---------------------------------------------------------------------------
# Report emission
# ---------------------------------------------------------------------------


def _metrics_df(metrics: list[Phase2Metrics]) -> pd.DataFrame:
    return pd.DataFrame([
        dict(
            base_rank=m.base_rank, base_cfg_id=m.base_cfg_id,
            indicator=m.indicator, lambda_de_lever=m.lambda_de_lever,
            cagr=m.cagr, sharpe=m.sharpe, max_drawdown=m.max_drawdown,
            calmar=m.calmar, sortino=m.sortino, volatility=m.volatility,
            n_switches=m.n_switches, mean_position=m.mean_position,
            delta_cagr=m.delta_cagr, delta_mdd=m.delta_mdd,
            effectiveness=m.effectiveness,
        )
        for m in metrics
    ])


def _fmt_pct(x: float, digits: int = 2) -> str:
    if x is None or np.isnan(x) or np.isinf(x):
        return "—"
    return f"{x * 100:+.{digits}f}%"


def _fmt_num(x: float, digits: int = 2) -> str:
    if x is None or np.isnan(x) or np.isinf(x):
        return "—"
    return f"{x:.{digits}f}"


def _emit_dataset_report(
    ctx: DatasetContext, metrics: list[Phase2Metrics],
    out_dir: Path, log: logging.Logger,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    df = _metrics_df(metrics)
    df.to_csv(out_dir / "configs_risk_signal.csv", index=False)
    log.info("    wrote %s", out_dir / "configs_risk_signal.csv")

    md = [f"# Phase 2 — {ctx.label}\n"]
    md.append(f"> Window: **{ctx.window_label}**\n")
    md.append(f"## Scope\n")
    md.append(
        f"- bases (top-K): {df.base_rank.nunique()}\n"
        f"- indicators: {df.indicator.nunique()} ({', '.join(sorted(df.indicator.unique()))})\n"
        f"- lambda values: {sorted(df.lambda_de_lever.unique())}\n"
        f"- total sims: {len(df)}\n"
        f"- gates: not evaluated (Phase 2 exploratory per spec §6.1)\n"
    )

    # Per-indicator × lambda aggregate (average across bases).
    md.append("## Average effect by (indicator, λ) — across all 20 bases\n")
    md.append(
        "| indicator | λ | avg ΔCAGR | avg ΔMDD | avg mean_pos | frac MDD-down |\n"
        "|---|---|---|---|---|---|"
    )
    non_base = df[df.lambda_de_lever > 0]
    for ind in sorted(non_base.indicator.unique()):
        for lam in sorted(non_base.lambda_de_lever.unique()):
            sub = non_base[(non_base.indicator == ind) & (non_base.lambda_de_lever == lam)]
            if len(sub) == 0:
                continue
            md.append(
                f"| {ind} | {lam:.1f} | {_fmt_pct(sub.delta_cagr.mean())} | "
                f"{_fmt_pct(sub.delta_mdd.mean())} | "
                f"{_fmt_num(sub.mean_position.mean())} | "
                f"{100*(sub.delta_mdd > 0).mean():.1f}% |"
            )

    md.append("\n## Top-20 variants by effectiveness (ΔMDD / |ΔCAGR|)\n")
    md.append("> Only variants that reduced MDD (ΔMDD > 0) are listed.\n")
    improved = non_base[non_base.delta_mdd > 0].sort_values("effectiveness", ascending=False).head(20)
    if len(improved) == 0:
        md.append("> **No variant reduced MDD on this dataset.**\n")
    else:
        md.append(
            "| # | base | indicator | λ | CAGR | ΔCAGR | MDD | ΔMDD | Sharpe | mean_pos | eff. |\n"
            "|---|---|---|---|---|---|---|---|---|---|---|"
        )
        for i, row in improved.reset_index(drop=True).iterrows():
            md.append(
                f"| {i+1} | `{row.base_cfg_id}` (#{int(row.base_rank)}) | "
                f"{row.indicator} | {row.lambda_de_lever:.1f} | "
                f"{_fmt_pct(row.cagr)} | {_fmt_pct(row.delta_cagr)} | "
                f"{_fmt_pct(row.max_drawdown)} | {_fmt_pct(row.delta_mdd)} | "
                f"{_fmt_num(row.sharpe)} | {_fmt_num(row.mean_position)} | "
                f"{row.effectiveness:.2f} |"
            )

    md.append("\n## Baselines per base (λ=0 reference)\n")
    md.append(
        "| rank | cfg | CAGR | MDD | Sharpe |\n"
        "|---|---|---|---|---|"
    )
    # With λ=0 the 5 indicator baselines are identical — pick first.
    base0 = (
        df[(df.lambda_de_lever == 0.0) & (df.indicator == "composite")]
        .sort_values("base_rank")
    )
    for _, r in base0.iterrows():
        md.append(
            f"| {int(r.base_rank)} | `{r.base_cfg_id}` | {_fmt_pct(r.cagr)} | "
            f"{_fmt_pct(r.max_drawdown)} | {_fmt_num(r.sharpe)} |"
        )

    (out_dir / "phase2_summary.md").write_text("\n".join(md), encoding="utf-8")
    log.info("    wrote %s", out_dir / "phase2_summary.md")


def _emit_phase2_final(
    dataset_labels: list[str], out_dir: Path, log: logging.Logger,
) -> None:
    all_df: dict[str, pd.DataFrame] = {}
    for lab in dataset_labels:
        csv = out_dir / "phase2" / lab / "configs_risk_signal.csv"
        if not csv.exists():
            log.warning("missing %s — skipped in FINAL", csv)
            continue
        all_df[lab] = pd.read_csv(csv)

    md = ["# Phase 2 — Risk-signal de-leveraging · FINAL\n"]
    md.append("> Cross-dataset comparison of continuous de-leveraging via "
              "EBP / term-spread / CAPE / VIX / composite.\n")

    md.append("## Scope\n")
    for lab, df in all_df.items():
        md.append(
            f"- **{lab}**: {df.base_rank.nunique()} bases × "
            f"{df.indicator.nunique()} indicators × {df.lambda_de_lever.nunique()} λ values = {len(df)} sims\n"
        )
    md.append("")

    # Cross-dataset (indicator, λ) winners by avg ΔMDD across datasets
    md.append("## Cross-dataset (indicator, λ) ranking by avg ΔMDD\n")
    md.append("> Mean ΔMDD / ΔCAGR across 20 bases, averaged across datasets.\n")
    combined_rows = []
    for ind in INDICATORS_TO_SWEEP:
        for lam in LAMBDA_VALUES:
            if lam == 0.0:
                continue
            avg_dcagr_parts = []
            avg_dmdd_parts = []
            frac_parts = []
            per_ds = {}
            for lab, df in all_df.items():
                sub = df[(df.indicator == ind) & (df.lambda_de_lever == lam)]
                avg_dcagr_parts.append(sub.delta_cagr.mean())
                avg_dmdd_parts.append(sub.delta_mdd.mean())
                frac_parts.append((sub.delta_mdd > 0).mean())
                per_ds[lab] = (sub.delta_cagr.mean(), sub.delta_mdd.mean())
            combined_rows.append({
                "indicator": ind,
                "lambda": lam,
                "avg_dcagr_across": float(np.mean(avg_dcagr_parts)),
                "avg_dmdd_across": float(np.mean(avg_dmdd_parts)),
                "min_frac_mdd_down": float(np.min(frac_parts)),
                "per_ds": per_ds,
            })
    cross = sorted(combined_rows, key=lambda r: -r["avg_dmdd_across"])
    md.append(
        "| indicator | λ | min frac MDD-down | avg ΔCAGR | avg ΔMDD | "
        + " | ".join(f"{d} ΔCAGR / ΔMDD" for d in all_df.keys())
        + " |\n"
        "|---|---|---|---|---|"
        + "|".join(["---"] * len(all_df))
        + "|"
    )
    for r in cross:
        cells = [
            r["indicator"], f"{r['lambda']:.1f}",
            f"{r['min_frac_mdd_down']*100:.1f}%",
            _fmt_pct(r["avg_dcagr_across"]), _fmt_pct(r["avg_dmdd_across"]),
        ]
        for d in all_df.keys():
            dc, dm = r["per_ds"][d]
            cells.append(f"{_fmt_pct(dc)} / {_fmt_pct(dm)}")
        md.append("| " + " | ".join(cells) + " |")
    md.append("")

    # Top variants per dataset (direct cross-check to Phase 1)
    md.append("## Best variant per dataset (ΔCAGR ≥ −5pp, max MDD reduction)\n")
    for lab, df in all_df.items():
        non_base = df[df.lambda_de_lever > 0]
        eligible = non_base[non_base.delta_cagr >= -0.05]
        if len(eligible) == 0:
            md.append(f"### {lab}: no variant within −5pp CAGR corridor.\n")
            continue
        best = eligible.sort_values("delta_mdd", ascending=False).head(5)
        md.append(f"### {lab}\n")
        md.append(
            "| # | base | indicator | λ | CAGR | ΔCAGR | MDD | ΔMDD | Sharpe |\n"
            "|---|---|---|---|---|---|---|---|---|"
        )
        for i, r in best.reset_index(drop=True).iterrows():
            md.append(
                f"| {i+1} | `{r.base_cfg_id}` (#{int(r.base_rank)}) | "
                f"{r.indicator} | {r.lambda_de_lever:.1f} | "
                f"{_fmt_pct(r.cagr)} | {_fmt_pct(r.delta_cagr)} | "
                f"{_fmt_pct(r.max_drawdown)} | {_fmt_pct(r.delta_mdd)} | "
                f"{_fmt_num(r.sharpe)} |"
            )
        md.append("")

    md.append("## Central question (spec §2) — cross-check with Phase 1\n")
    md.append(
        "- **Target**: MDD ≤ 40 pp on top-1 educational (baseline 54%) "
        "with ΔCAGR ≥ −5 pp.\n"
        "- **Phase 1 best**: `sl30_next` → MDD 47.13% (Δ −6.86), CAGR +0.51 pp. "
        "Still 7 pp above target.\n"
        "- **Phase 2 best on top-1 educational**: see educational table above.\n"
    )

    md.append("\n## Next — Phase 3 (combination)\n")
    md.append(
        "- Take top-5 variants from Phase 1 (stop-only) and top-5 from Phase 2 "
        "(signal-only), combine them (25 candidates).\n"
        "- Run the full 7-gate battery on the survivors — PBO + DSR + WF + OOS + "
        "FWD + bootstrap + cross-lib. DSR penalty uses n_trials = Phase-1 + Phase-2 + "
        "combination grid.\n"
        "- If any combination lands in MDD 25-40% corridor with ΔCAGR ≥ −5 pp AND "
        "passes ≥ 5/7 gates → honest crash-protected winner. Else Phase 4 real-data "
        "validation is moot and the study closes with \"no mechanism closed the "
        "gap\" verdict.\n"
    )

    md.append("\n---\n*Citations:* spec §3.1-B (risk signal design), §5.2 "
              "(Phase 2 scope), §8.3 (sigmoid threshold to avoid 2010s "
              "over-delevering), §8.5 (continuous vs discrete). Honest "
              "alignment: `[advances_fin_ml, p.31-34]`. Gates: `[p.208-211]` "
              "(PBO), `[p.222-223]` (DSR), `[ch.12]` (WF), `[p.196-202]` (bootstrap).")
    (out_dir / "phase2_FINAL.md").write_text("\n".join(md), encoding="utf-8")
    log.info("wrote %s", out_dir / "phase2_FINAL.md")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def _setup_logging() -> logging.Logger:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("phase2_risk_signal")
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
    indicators: tuple[str, ...],
    lambdas: tuple[float, ...],
    log: logging.Logger,
) -> None:
    log.info("  %s — building risk series", ctx.label)
    risks = _build_risk_series(ctx.daily_index, log)

    n_variants = len(top_configs) * len(indicators) * len(lambdas)
    log.info("  %s — %d sims (%d bases × %d indicators × %d λ)",
             ctx.label, n_variants, len(top_configs), len(indicators), len(lambdas))

    metrics: list[Phase2Metrics] = []
    t0 = time.time()
    k = 0
    for rank_zero, base_cfg in enumerate(top_configs):
        rank = rank_zero + 1
        for ind in indicators:
            for lam in lambdas:
                risk_cfg = RiskSignalConfig(indicator_type=ind, lambda_de_lever=lam)
                res = ctx.simulate_fn(base_cfg, risks[ind], risk_cfg)
                metrics.append(_compute_metrics(rank, base_cfg, ind, lam, res))
                k += 1
                if k % max(n_variants // 20, 1) == 0:
                    el = time.time() - t0
                    rate = k / el if el > 0 else 0.0
                    eta = (n_variants - k) / rate if rate > 0 else 0.0
                    log.info("    [%d/%d] %.1fs elapsed, %.1f sims/s, ETA %.0fs",
                             k, n_variants, el, rate, eta)

    log.info("    sweep done in %.1fs", time.time() - t0)
    _fill_deltas(metrics)
    _emit_dataset_report(ctx, metrics, out_dir, log)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset",
                        choices=("all", "educational", "spy_real", "ndx_real"),
                        default="all")
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--smoke", action="store_true",
                        help="Top-3 bases × 2 indicators × 2 λ")
    args = parser.parse_args()

    log = _setup_logging()
    t0 = time.time()

    top_k = args.top_k if not args.smoke else 3
    indicators = INDICATORS_TO_SWEEP if not args.smoke else ("ebp", "composite")
    lambdas = LAMBDA_VALUES if not args.smoke else (0.0, 0.5)
    datasets_to_run = (
        ["educational", "spy_real", "ndx_real"]
        if args.dataset == "all" else [args.dataset]
    )
    if args.smoke and args.dataset == "all":
        datasets_to_run = ["educational"]

    completed: list[str] = []
    for label in datasets_to_run:
        log.info("=== %s ===", label)
        if label == "educational":
            ctx, top = _build_educational_context(top_k)
        elif label == "spy_real":
            ctx, top = _build_real_context(SPY_MARKET, top_k, "ema_sma_threshold_spy_real")
        elif label == "ndx_real":
            ctx, top = _build_real_context(NDX_MARKET, top_k, "ema_sma_threshold_nasdaq_real")
        else:
            raise ValueError(label)
        out_dir = STUDY_DIR / "phase2" / ctx.label
        _run_dataset(ctx, top, out_dir, indicators=indicators, lambdas=lambdas, log=log)
        completed.append(ctx.label)

    if len(completed) > 0:
        _emit_phase2_final(completed, STUDY_DIR, log)

    log.info("TOTAL wall time: %.1fs", time.time() - t0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
