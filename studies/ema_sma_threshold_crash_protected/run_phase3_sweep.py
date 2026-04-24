"""Phase 3 — combined stop-loss + risk-signal sweep + 7-gate battery.

Driver for the final experimental stage of the crash-protection study
(see ``studies/SPEC_crash_protection_evolution.md`` §5.3).

What this script does
---------------------

1. Take the 4 combinations selected at the end of Phase 2::

        (sl20_cool21, composite λ=0.5)
        (sl20_cool21, cape λ=0.5)
        (sl30_rec10,  composite λ=0.5)
        (sl30_rec10,  cape λ=0.5)

   and the top-20 base configs per dataset. 4 × 20 = 80 variants per
   dataset; 240 sims total across 3 datasets.

2. Simulate each variant with
   :func:`simulate_with_stop_and_risk`.

3. Compute metrics + deltas vs the λ=0 stop=None baseline of the same
   base config.

4. Select top-5 survivors per dataset by MDD reduction within the
   CAGR corridor (ΔCAGR ≥ −5 pp).

5. Run the full 7-gate battery on those survivors:

   * G1 PBO (grid-level) — applied to the 80-variant Phase 3 grid.
   * G2 DSR with ``n_trials = 4020`` (Phase 1 + 2 + 3 cumulative).
   * G3 Walk-Forward 6/8 windows.
   * G4 OOS 70/30 Sharpe > 0.
   * G5 FWD stress post-2020 Sharpe > 0.
   * G6 Bootstrap 99.9% CI low > 0.
   * G7 Cross-lib ±3 pp CAGR (numpy-pure vs vectorised).

6. Emit per-dataset CSV + summary, and compile ``phase3_FINAL.md``
   with the verdict.

Usage
-----

::

    .venv/bin/python studies/ema_sma_threshold_crash_protected/run_phase3_sweep.py
    .venv/bin/python studies/ema_sma_threshold_crash_protected/run_phase3_sweep.py --smoke

Citations
---------

* PBO `[advances_fin_ml, p.208-211]`, DSR `[p.222-223]`, WF `[ch.12]`,
  bootstrap `[p.196-202]`, cross-lib `[p.31-34]`.
* Spec §6.1 (gate battery), §6.2 (n_trials accounting).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass
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
    StopAndRiskResult,
    StopLossConfig,
    simulate_with_stop_and_risk,
)
from ai_trade.backtest.strategies.stop_loss_and_risk_signals_numpy import (
    simulate_with_stop_and_risk_numpy,
)
from ai_trade.backtest.grid.letf_rotation_b1c import bootstrap_sharpe_ci
from ai_trade.backtest.validation.dsr import dsr
from ai_trade.backtest.validation.pbo import pbo
from ai_trade.backtest.validation.walk_forward import (
    walk_forward_gate,
    walk_forward_splits,
)

STUDY_DIR = Path(__file__).parent
LOG_PATH = Path("logs/crash_protection_phase3.log")
REPO_ROOT = Path(__file__).resolve().parents[2]

# Cumulative n_trials for DSR (spec §6.2).
N_TRIALS_CUMULATIVE = 2_580 + 1_200 + 240  # = 4 020


# ---------------------------------------------------------------------------
# Combinations — fixed per Phase 2 conclusions
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CombinationSpec:
    label: str
    stop_cfg: StopLossConfig
    risk_indicator: str
    risk_lambda: float

    @property
    def tag(self) -> str:
        return self.label


PHASE3_COMBOS: tuple[CombinationSpec, ...] = (
    CombinationSpec(
        label="sl20_cool21_composite05",
        stop_cfg=StopLossConfig(
            stop_loss_pct=0.20, reentry_mode="time_cooldown", reentry_param=21,
        ),
        risk_indicator="composite",
        risk_lambda=0.5,
    ),
    CombinationSpec(
        label="sl20_cool21_cape05",
        stop_cfg=StopLossConfig(
            stop_loss_pct=0.20, reentry_mode="time_cooldown", reentry_param=21,
        ),
        risk_indicator="cape",
        risk_lambda=0.5,
    ),
    CombinationSpec(
        label="sl30_rec10_composite05",
        stop_cfg=StopLossConfig(
            stop_loss_pct=0.30, reentry_mode="recovery_trigger", reentry_param=0.10,
        ),
        risk_indicator="composite",
        risk_lambda=0.5,
    ),
    CombinationSpec(
        label="sl30_rec10_cape05",
        stop_cfg=StopLossConfig(
            stop_loss_pct=0.30, reentry_mode="recovery_trigger", reentry_param=0.10,
        ),
        risk_indicator="cape",
        risk_lambda=0.5,
    ),
)


# ---------------------------------------------------------------------------
# Dataset contexts
# ---------------------------------------------------------------------------


@dataclass
class DatasetContext:
    label: str
    source_study_dir: Path
    daily_index: pd.DatetimeIndex
    window_label: str
    # callable(base_cfg, stop_cfg, risk_series, risk_cfg) -> StopAndRiskResult
    simulate_fn: callable
    # callable(base_cfg, stop_cfg, risk_series, risk_cfg) -> equity (pd.Series)
    simulate_numpy_fn: callable


def _parse_base(row: pd.Series) -> EMASMAThresholdConfig:
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


def _load_top_k(study_dir: Path, top_k: int) -> list[EMASMAThresholdConfig]:
    df = pd.read_csv(study_dir / "configs.csv").sort_values("rank").head(top_k)
    return [_parse_base(r) for _, r in df.iterrows()]


def _build_educational(top_k: int) -> tuple[DatasetContext, list[EMASMAThresholdConfig]]:
    spx_prices = load_testfolio_series("SPYSIM")
    spx_returns = load_testfolio_returns("SPYSIM")
    daily_idx = spx_returns.index

    def _cash_or_synth(base_cfg):
        if base_cfg.sell_leverage == 0.0:
            cash_daily = base_cfg.cash_rate_annual / TRADING_DAYS_PER_YEAR
            return pd.Series(cash_daily, index=spx_returns.index)
        return _synth_leveraged_returns(spx_returns, base_cfg.sell_leverage, base_cfg.fee)

    def _simulate(base, stop_cfg, risk, risk_cfg):
        long_leg = _synth_leveraged_returns(spx_returns, base.buy_leverage, base.fee)
        return simulate_with_stop_and_risk(
            signal_prices=spx_prices, buy_leg_returns=long_leg,
            sell_leg_returns=_cash_or_synth(base), cfg=base,
            stop_cfg=stop_cfg, risk_series=risk, risk_cfg=risk_cfg,
        )

    def _simulate_numpy(base, stop_cfg, risk, risk_cfg):
        long_leg = _synth_leveraged_returns(spx_returns, base.buy_leverage, base.fee)
        return simulate_with_stop_and_risk_numpy(
            signal_prices=spx_prices, buy_leg_returns=long_leg,
            sell_leg_returns=_cash_or_synth(base), cfg=base,
            stop_cfg=stop_cfg, risk_series=risk, risk_cfg=risk_cfg,
        )

    src = REPO_ROOT / "studies" / "ema_sma_threshold_educational"
    top = _load_top_k(src, top_k)
    ctx = DatasetContext(
        label="educational", source_study_dir=src,
        daily_index=daily_idx,
        window_label=f"{daily_idx[0].date()}→{daily_idx[-1].date()} (~40y synth)",
        simulate_fn=_simulate, simulate_numpy_fn=_simulate_numpy,
    )
    return ctx, top


def _build_real(
    market: RealETFMarket, top_k: int, study_label: str,
) -> tuple[DatasetContext, list[EMASMAThresholdConfig]]:
    src = REPO_ROOT / "studies" / study_label
    top = _load_top_k(src, top_k)
    leverages = sorted({int(cfg.buy_leverage) for cfg in top if cfg.buy_leverage > 0})
    bundle = build_data_bundle(market, tuple(float(x) for x in leverages))
    daily_idx = bundle["signal_returns"].index

    def _cash_or_synth(base_cfg):
        signal_returns = bundle["signal_returns"]
        if base_cfg.sell_leverage == 0.0:
            cash_daily = base_cfg.cash_rate_annual / TRADING_DAYS_PER_YEAR
            return pd.Series(cash_daily, index=signal_returns.index)
        return _synth_leveraged_returns(signal_returns, base_cfg.sell_leverage, base_cfg.fee)

    def _simulate(base, stop_cfg, risk, risk_cfg):
        buy_leg = bundle[f"buy_L{int(base.buy_leverage)}"]
        return simulate_with_stop_and_risk(
            signal_prices=bundle["signal_prices"], buy_leg_returns=buy_leg,
            sell_leg_returns=_cash_or_synth(base), cfg=base,
            stop_cfg=stop_cfg, risk_series=risk, risk_cfg=risk_cfg,
        )

    def _simulate_numpy(base, stop_cfg, risk, risk_cfg):
        buy_leg = bundle[f"buy_L{int(base.buy_leverage)}"]
        return simulate_with_stop_and_risk_numpy(
            signal_prices=bundle["signal_prices"], buy_leg_returns=buy_leg,
            sell_leg_returns=_cash_or_synth(base), cfg=base,
            stop_cfg=stop_cfg, risk_series=risk, risk_cfg=risk_cfg,
        )

    meta = bundle["_meta"]
    ctx = DatasetContext(
        label=market.label + "_real", source_study_dir=src,
        daily_index=daily_idx,
        window_label=f"{pd.Timestamp(meta['start']).date()}→{pd.Timestamp(meta['end']).date()}",
        simulate_fn=_simulate, simulate_numpy_fn=_simulate_numpy,
    )
    return ctx, top


# ---------------------------------------------------------------------------
# Risk series
# ---------------------------------------------------------------------------


def _build_risks(daily_index: pd.DatetimeIndex, log: logging.Logger) -> dict[str, pd.Series]:
    raw = load_all_indicators(daily_index, cache_dir=MACRO_CACHE)
    out: dict[str, pd.Series] = {}
    for name in ("ebp", "term_spread", "cape", "vix"):
        spec = INDICATOR_SPECS[name]
        out[name] = compute_risk_score(raw[name], spec)
    out["composite"] = compute_composite_risk(out)
    return out


# ---------------------------------------------------------------------------
# Metrics + deltas
# ---------------------------------------------------------------------------


@dataclass
class Phase3Metrics:
    base_rank: int
    base_cfg_id: str
    base_cfg: EMASMAThresholdConfig
    combo_label: str
    combo_spec: CombinationSpec
    cagr: float
    sharpe: float
    max_drawdown: float
    calmar: float
    sortino: float
    volatility: float
    n_switches: int
    n_stops: int
    mean_position: float
    equity: pd.Series
    daily_returns: pd.Series
    delta_cagr: float = float("nan")
    delta_mdd: float = float("nan")
    effectiveness: float = float("nan")


def _metrics_from_result(
    base_rank: int, base_cfg: EMASMAThresholdConfig,
    combo: CombinationSpec, res: StopAndRiskResult,
) -> Phase3Metrics:
    pos = res.effective_position
    bull = pos.where(res.regime == 1).dropna()
    return Phase3Metrics(
        base_rank=base_rank, base_cfg_id=base_cfg.cfg_id, base_cfg=base_cfg,
        combo_label=combo.label, combo_spec=combo,
        cagr=float(_cagr(res.equity, TRADING_DAYS_PER_YEAR)),
        sharpe=float(_sharpe(res.daily_returns, TRADING_DAYS_PER_YEAR)),
        max_drawdown=float(_max_drawdown(res.equity)),
        calmar=float(_calmar(res.equity, TRADING_DAYS_PER_YEAR)),
        sortino=float(_sortino(res.daily_returns, TRADING_DAYS_PER_YEAR)),
        volatility=float(_volatility(res.daily_returns, TRADING_DAYS_PER_YEAR)),
        n_switches=res.n_switches,
        n_stops=res.n_stops_triggered,
        mean_position=float(bull.mean()) if len(bull) > 0 else float("nan"),
        equity=res.equity,
        daily_returns=res.daily_returns,
    )


def _fill_deltas(
    combo_metrics: list[Phase3Metrics],
    baseline_by_base: dict[str, tuple[float, float]],
) -> None:
    for m in combo_metrics:
        base_cagr, base_mdd = baseline_by_base[m.base_cfg_id]
        m.delta_cagr = m.cagr - base_cagr
        m.delta_mdd = base_mdd - m.max_drawdown
        denom = max(abs(m.delta_cagr), 1e-3)
        m.effectiveness = m.delta_mdd / denom


# ---------------------------------------------------------------------------
# Gate evaluator
# ---------------------------------------------------------------------------


@dataclass
class Phase3Gates:
    g1_pbo: bool
    g2_dsr: bool
    g3_walk_forward: bool
    g4_oos_sharpe: bool
    g5_fwd_stress: bool
    g6_bootstrap: bool
    g7_cross_lib: bool
    # Supporting stats
    pbo_value: float
    dsr_p: float
    cross_lib_diff_pp: float

    @property
    def n_passed(self) -> int:
        return sum([
            self.g1_pbo, self.g2_dsr, self.g3_walk_forward,
            self.g4_oos_sharpe, self.g5_fwd_stress,
            self.g6_bootstrap, self.g7_cross_lib,
        ])


def _g1_pbo_grid(grid_returns: np.ndarray) -> tuple[bool, float]:
    try:
        res = pbo(grid_returns, n_blocks=10)
    except Exception:
        return False, float("nan")
    return bool(res.pbo < 0.5), float(res.pbo)


def _g2_dsr(rets: pd.Series, n_trials: int) -> tuple[bool, float]:
    r = rets.dropna().values
    if len(r) < 30:
        return False, float("nan")
    try:
        res = dsr(r, n_trials=n_trials)
    except Exception:
        return False, float("nan")
    return bool(res.p_value < 0.05), float(res.p_value)


def _g3_walk_forward(rets: pd.Series) -> bool:
    r = rets.dropna()
    n = len(r)
    is_days, oos_days, step_days = 504, 126, 126
    if n < is_days + oos_days:
        return False
    oos_totals: list[float] = []
    oos_dds: list[float] = []
    for _train, test in walk_forward_splits(
        n_obs=n, is_size=is_days, oos_size=oos_days, step=step_days,
    ):
        window = r.iloc[list(test)]
        if window.empty:
            continue
        eq = (1.0 + window).cumprod()
        oos_totals.append(float(eq.iloc[-1] - 1.0))
        peak = eq.cummax()
        dd = 1.0 - (eq / peak).min()
        oos_dds.append(float(dd))
    if len(oos_totals) < 8:
        return False
    verdict = walk_forward_gate(
        oos_totals, oos_dds,
        min_windows=8, min_profitable_ratio=6 / 8, max_drawdown=0.25,
    )
    return verdict == "pass"


def _g4_oos(rets: pd.Series, split_frac: float = 0.7) -> bool:
    r = rets.dropna()
    if len(r) < 100:
        return False
    cut = int(len(r) * split_frac)
    oos = r.iloc[cut:]
    return bool(_sharpe(oos, TRADING_DAYS_PER_YEAR) > 0)


def _g5_fwd(rets: pd.Series, start: str = "2020-01-01") -> bool:
    r = rets.dropna()
    if r.empty:
        return False
    window = r.loc[r.index >= pd.Timestamp(start)]
    if len(window) < 60:
        return False
    return bool(_sharpe(window, TRADING_DAYS_PER_YEAR) > 0)


def _g6_bootstrap(rets: pd.Series, n_resamples: int = 500) -> bool:
    r = rets.dropna()
    if len(r) < 100:
        return False
    lo, _hi = bootstrap_sharpe_ci(
        r, alpha=0.001, block_mean=5, n_resamples=n_resamples, seed=42,
    )
    return bool(not np.isnan(lo) and lo > 0)


def _g7_cross_lib(
    m: Phase3Metrics, ctx: DatasetContext, risks: dict[str, pd.Series],
    tolerance_pp: float = 0.03,
) -> tuple[bool, float]:
    combo = m.combo_spec
    risk_series = risks[combo.risk_indicator]
    risk_cfg = RiskSignalConfig(
        indicator_type=combo.risk_indicator, lambda_de_lever=combo.risk_lambda,
    )
    np_eq = ctx.simulate_numpy_fn(m.base_cfg, combo.stop_cfg, risk_series, risk_cfg)
    np_cagr = float(_cagr(np_eq, TRADING_DAYS_PER_YEAR))
    diff = abs(m.cagr - np_cagr)
    return bool(diff <= tolerance_pp), diff


def _evaluate_gates(
    top5: list[Phase3Metrics], all_metrics: list[Phase3Metrics],
    ctx: DatasetContext, risks: dict[str, pd.Series],
    n_trials: int, log: logging.Logger,
) -> list[Phase3Gates]:
    # G1: grid-level PBO on ALL 80 variants' returns matrix.
    rets_matrix = np.column_stack([
        m.daily_returns.fillna(0.0).values for m in all_metrics
    ])
    g1_pass, pbo_val = _g1_pbo_grid(rets_matrix)
    log.info("    G1 PBO grid-level: %.3f (pass=%s)", pbo_val, g1_pass)

    gates: list[Phase3Gates] = []
    for m in top5:
        g2_pass, dsr_p = _g2_dsr(m.daily_returns, n_trials)
        g3_pass = _g3_walk_forward(m.daily_returns)
        g4_pass = _g4_oos(m.daily_returns)
        g5_pass = _g5_fwd(m.daily_returns)
        g6_pass = _g6_bootstrap(m.daily_returns)
        g7_pass, g7_diff = _g7_cross_lib(m, ctx, risks)
        gates.append(Phase3Gates(
            g1_pbo=g1_pass, g2_dsr=g2_pass, g3_walk_forward=g3_pass,
            g4_oos_sharpe=g4_pass, g5_fwd_stress=g5_pass,
            g6_bootstrap=g6_pass, g7_cross_lib=g7_pass,
            pbo_value=pbo_val, dsr_p=dsr_p, cross_lib_diff_pp=g7_diff,
        ))
    return gates


# ---------------------------------------------------------------------------
# Report emission
# ---------------------------------------------------------------------------


def _fmt_pct(x, digits=2):
    if x is None or np.isnan(x) or np.isinf(x):
        return "—"
    return f"{x * 100:+.{digits}f}%"


def _fmt_num(x, digits=2):
    if x is None or np.isnan(x) or np.isinf(x):
        return "—"
    return f"{x:.{digits}f}"


def _emit_dataset_report(
    ctx: DatasetContext, all_metrics: list[Phase3Metrics],
    top5_with_gates: list[tuple[Phase3Metrics, Phase3Gates]],
    out_dir: Path, log: logging.Logger,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for m in all_metrics:
        rows.append(dict(
            base_rank=m.base_rank, base_cfg_id=m.base_cfg_id,
            combo=m.combo_label,
            stop_loss_pct=m.combo_spec.stop_cfg.stop_loss_pct,
            reentry_mode=m.combo_spec.stop_cfg.reentry_mode,
            reentry_param=m.combo_spec.stop_cfg.reentry_param,
            risk_indicator=m.combo_spec.risk_indicator,
            risk_lambda=m.combo_spec.risk_lambda,
            cagr=m.cagr, sharpe=m.sharpe, max_drawdown=m.max_drawdown,
            calmar=m.calmar, sortino=m.sortino, volatility=m.volatility,
            n_switches=m.n_switches, n_stops=m.n_stops,
            mean_position=m.mean_position,
            delta_cagr=m.delta_cagr, delta_mdd=m.delta_mdd,
            effectiveness=m.effectiveness,
        ))
    pd.DataFrame(rows).to_csv(out_dir / "configs_combined.csv", index=False)
    log.info("    wrote %s", out_dir / "configs_combined.csv")

    md = [f"# Phase 3 — {ctx.label}\n"]
    md.append(f"> Window: **{ctx.window_label}**\n")
    md.append(f"## Scope\n")
    md.append(
        f"- bases: {len({m.base_cfg_id for m in all_metrics})}\n"
        f"- combinations: {len({m.combo_label for m in all_metrics})}\n"
        f"- total sims: {len(all_metrics)}\n"
        f"- gates: evaluated on top-5 survivors within ΔCAGR ≥ −5 pp corridor\n"
    )

    # Best per combo
    md.append("\n## Average effect by combination\n")
    md.append(
        "| combo | avg ΔCAGR | avg ΔMDD | frac MDD-down |\n"
        "|---|---|---|---|"
    )
    by_combo = pd.DataFrame(rows)
    for combo in sorted(by_combo.combo.unique()):
        sub = by_combo[by_combo.combo == combo]
        md.append(
            f"| {combo} | {_fmt_pct(sub.delta_cagr.mean())} | "
            f"{_fmt_pct(sub.delta_mdd.mean())} | "
            f"{100*(sub.delta_mdd > 0).mean():.1f}% |"
        )

    # Top-5 with gates
    md.append("\n## Top-5 survivors + 7-gate verdict\n")
    md.append("> Selected by max ΔMDD within ΔCAGR ≥ −5 pp corridor.\n")
    md.append(
        "| # | base | combo | CAGR | ΔCAGR | MDD | ΔMDD | Sharpe | "
        "G1 PBO | G2 DSR | G3 WF | G4 OOS | G5 FWD | G6 BS | G7 XLib | total |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"
    )
    for i, (m, g) in enumerate(top5_with_gates):
        def _gate_cell(ok, detail=None):
            icon = "✅" if ok else "❌"
            return f"{icon}" + (f" ({detail})" if detail else "")
        md.append(
            f"| {i+1} | `{m.base_cfg_id}` (#{m.base_rank}) | "
            f"{m.combo_label} | {_fmt_pct(m.cagr)} | {_fmt_pct(m.delta_cagr)} | "
            f"{_fmt_pct(m.max_drawdown)} | {_fmt_pct(m.delta_mdd)} | "
            f"{_fmt_num(m.sharpe)} | "
            f"{_gate_cell(g.g1_pbo, f'{g.pbo_value:.2f}')} | "
            f"{_gate_cell(g.g2_dsr, f'p={g.dsr_p:.3f}')} | "
            f"{_gate_cell(g.g3_walk_forward)} | "
            f"{_gate_cell(g.g4_oos_sharpe)} | "
            f"{_gate_cell(g.g5_fwd_stress)} | "
            f"{_gate_cell(g.g6_bootstrap)} | "
            f"{_gate_cell(g.g7_cross_lib, f'Δ{g.cross_lib_diff_pp*100:.1f}pp')} | "
            f"**{g.n_passed}/7** |"
        )

    # Baselines.
    md.append("\n## Baselines (no overlay) for reference\n")
    md.append("| rank | cfg | CAGR | MDD |\n|---|---|---|---|")
    base_by_id: dict[str, Phase3Metrics] = {}
    for m in all_metrics:
        if m.base_cfg_id not in base_by_id:
            base_by_id[m.base_cfg_id] = m
    for cfg_id, m in sorted(base_by_id.items(), key=lambda x: x[1].base_rank):
        bcagr = m.cagr - m.delta_cagr
        bmdd = m.max_drawdown + m.delta_mdd
        md.append(
            f"| {m.base_rank} | `{cfg_id}` | {_fmt_pct(bcagr)} | {_fmt_pct(bmdd)} |"
        )

    (out_dir / "phase3_summary.md").write_text("\n".join(md), encoding="utf-8")
    log.info("    wrote %s", out_dir / "phase3_summary.md")


def _emit_final_report(
    datasets: list[tuple[
        DatasetContext,
        list[Phase3Metrics],
        list[tuple[Phase3Metrics, Phase3Gates]],
    ]],
    out_dir: Path, log: logging.Logger,
) -> None:
    md = ["# Phase 3 — FINAL — Combined stop-loss + risk-signal + gates\n"]
    md.append("> **Educational / experimental.** Mandate §1: MAINTENANCE, "
              "100% Plano C. This study does NOT propose reactivating slot "
              "A/B/D regardless of outcome.\n")

    md.append("## Combinations tested\n")
    md.append("| label | stop | mode | param | indicator | λ |\n"
              "|---|---|---|---|---|---|")
    for combo in PHASE3_COMBOS:
        md.append(
            f"| `{combo.label}` | "
            f"{int(combo.stop_cfg.stop_loss_pct*100)}% | "
            f"{combo.stop_cfg.reentry_mode} | "
            f"{combo.stop_cfg.reentry_param} | "
            f"{combo.risk_indicator} | {combo.risk_lambda} |"
        )

    md.append("\n## Sweep scope\n")
    total_sims = sum(len(m) for _, m, _ in datasets)
    md.append(
        f"- bases/dataset: 20 × 4 combos = 80 variants/dataset\n"
        f"- total sims (Phase 3): {total_sims}\n"
        f"- **n_trials for DSR (cumulative Phase 1+2+3)**: {N_TRIALS_CUMULATIVE}\n"
        f"- top-5 per dataset → gate battery = {len(datasets) * 5} gated candidates\n"
    )

    # Verdict per dataset.
    md.append("\n## Verdict per dataset\n")
    any_winner = False
    for ctx, all_m, top5 in datasets:
        md.append(f"\n### {ctx.label}\n")
        md.append(f"Window: {ctx.window_label}\n")
        if not top5:
            md.append("> **No variant within ΔCAGR ≥ −5 pp corridor.**\n")
            continue
        md.append(
            "| # | base | combo | CAGR | ΔCAGR | MDD | ΔMDD | gates | verdict |\n"
            "|---|---|---|---|---|---|---|---|---|"
        )
        for i, (m, g) in enumerate(top5):
            verdict = (
                "🏆 HONEST WINNER (≥6/7)" if g.n_passed >= 6
                else "⚠️ partial (≥4/7)" if g.n_passed >= 4
                else "❌ rejected"
            )
            if g.n_passed >= 6 and m.max_drawdown <= 0.40:
                any_winner = True
            md.append(
                f"| {i+1} | `{m.base_cfg_id}` | {m.combo_label} | "
                f"{_fmt_pct(m.cagr)} | {_fmt_pct(m.delta_cagr)} | "
                f"{_fmt_pct(m.max_drawdown)} | {_fmt_pct(m.delta_mdd)} | "
                f"**{g.n_passed}/7** | {verdict} |"
            )

    md.append("\n## Central question verdict\n")
    if any_winner:
        md.append(
            "✅ **At least one crash-protected combo passes ≥ 6/7 gates AND reaches "
            "MDD ≤ 40% with ΔCAGR ≥ −5 pp on at least one dataset.** See per-dataset "
            "tables above. This does NOT auto-reactivate any dormant slot — it's a "
            "candidate for a future proposal.\n"
        )
    else:
        md.append(
            "❌ **No combination closed the gap.** Stop-loss alone (Phase 1), signal "
            "alone (Phase 2), and stop+signal combined (Phase 3) all fall short of the "
            "MDD ≤ 40% target with ΔCAGR ≥ −5 pp AND ≥ 6/7 gate pass. The study "
            "closes as *negative result* — crash protection mechanisms within this "
            "family do not salvage the 3x UPRO educational top-1 into production-grade.\n"
        )
        md.append(
            "This is honest evidence — 113/113 FAIL pattern (mandate §1 / MEMORY) "
            "continues. Path forward suggestions:\n"
            "1. Reduce target leverage (bL=2 vs bL=3) — MDD baseline already near "
            "   target, easier for overlays.\n"
            "2. Swap regime filter family (e.g., Ehlers smoothed momentum) before "
            "   re-trying overlays.\n"
            "3. Stay in MAINTENANCE (100% Plano C) per mandate §1; this study remains "
            "   educational material.\n"
        )

    md.append("\n## Next steps (regardless of verdict)\n")
    md.append(
        "* This is a *Phase 3 final* — no Phase 4 unless explicit new mandate.\n"
        "* Artifacts preserved for future reactivation review: "
        "`phase1/` + `phase2/` + `phase3/` CSVs, this `phase3_FINAL.md`, "
        "and the validated simulator modules.\n"
    )

    md.append("\n---\n*Citations:* spec §5.3 (Phase 3 scope), §6.1 (gates), "
              "§6.2 (n_trials accumulation). Gates: PBO "
              "`[advances_fin_ml, p.208-211]`, DSR `[p.222-223]`, WF `[ch.12]`, "
              "bootstrap `[p.196-202]`, cross-lib `[p.31-34]`.\n")
    (out_dir / "phase3_FINAL.md").write_text("\n".join(md), encoding="utf-8")
    log.info("wrote %s", out_dir / "phase3_FINAL.md")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def _setup_logging() -> logging.Logger:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("phase3_combined")
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
    log: logging.Logger,
    *,
    combos: tuple[CombinationSpec, ...] = PHASE3_COMBOS,
    n_trials: int = N_TRIALS_CUMULATIVE,
) -> tuple[list[Phase3Metrics], list[tuple[Phase3Metrics, Phase3Gates]]]:
    log.info("  %s — building risk series", ctx.label)
    risks = _build_risks(ctx.daily_index, log)

    # Compute baseline (no overlay) CAGR/MDD per base for deltas.
    log.info("  %s — baseline sims (no overlay) for delta reference", ctx.label)
    baseline_by_base: dict[str, tuple[float, float]] = {}
    for base in top_configs:
        res = ctx.simulate_fn(
            base, StopLossConfig(stop_loss_pct=None),
            risks["composite"],
            RiskSignalConfig(indicator_type="composite", lambda_de_lever=0.0),
        )
        bcagr = float(_cagr(res.equity, TRADING_DAYS_PER_YEAR))
        bmdd = float(_max_drawdown(res.equity))
        baseline_by_base[base.cfg_id] = (bcagr, bmdd)

    # Phase 3 sims.
    total = len(top_configs) * len(combos)
    log.info("  %s — %d sims (%d bases × %d combos)",
             ctx.label, total, len(top_configs), len(combos))
    metrics: list[Phase3Metrics] = []
    t0 = time.time()
    k = 0
    for rank_zero, base in enumerate(top_configs):
        rank = rank_zero + 1
        for combo in combos:
            risk_cfg = RiskSignalConfig(
                indicator_type=combo.risk_indicator,
                lambda_de_lever=combo.risk_lambda,
            )
            risk_series = risks[combo.risk_indicator]
            res = ctx.simulate_fn(base, combo.stop_cfg, risk_series, risk_cfg)
            metrics.append(_metrics_from_result(rank, base, combo, res))
            k += 1
            if k % max(total // 10, 1) == 0:
                el = time.time() - t0
                rate = k / el if el > 0 else 0.0
                log.info("    [%d/%d] %.1fs, %.1f sims/s", k, total, el, rate)
    log.info("    sweep done in %.1fs", time.time() - t0)

    _fill_deltas(metrics, baseline_by_base)

    # Pick top-5 within CAGR corridor.
    eligible = [m for m in metrics if m.delta_cagr >= -0.05 and m.delta_mdd > 0]
    top5 = sorted(eligible, key=lambda m: -m.delta_mdd)[:5]
    log.info("  %s — eligible (ΔCAGR≥-5pp & ΔMDD>0): %d/%d, running gates on top-5",
             ctx.label, len(eligible), len(metrics))

    t1 = time.time()
    gates = _evaluate_gates(top5, metrics, ctx, risks, n_trials, log)
    log.info("  gate battery done in %.1fs", time.time() - t1)

    top5_with_gates = list(zip(top5, gates))
    _emit_dataset_report(ctx, metrics, top5_with_gates, out_dir, log)
    return metrics, top5_with_gates


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset",
                        choices=("all", "educational", "spy_real", "ndx_real"),
                        default="all")
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    log = _setup_logging()
    t0 = time.time()

    top_k = args.top_k if not args.smoke else 3
    combos = PHASE3_COMBOS if not args.smoke else PHASE3_COMBOS[:2]
    datasets_to_run = (
        ["educational", "spy_real", "ndx_real"]
        if args.dataset == "all" else [args.dataset]
    )
    if args.smoke and args.dataset == "all":
        datasets_to_run = ["educational"]

    results: list[tuple] = []
    for label in datasets_to_run:
        log.info("=== %s ===", label)
        if label == "educational":
            ctx, top = _build_educational(top_k)
        elif label == "spy_real":
            ctx, top = _build_real(SPY_MARKET, top_k, "ema_sma_threshold_spy_real")
        elif label == "ndx_real":
            ctx, top = _build_real(NDX_MARKET, top_k, "ema_sma_threshold_nasdaq_real")
        else:
            raise ValueError(label)
        out_dir = STUDY_DIR / "phase3" / ctx.label
        all_m, top5 = _run_dataset(ctx, top, out_dir, log, combos=combos)
        results.append((ctx, all_m, top5))

    if len(results) > 0:
        _emit_final_report(results, STUDY_DIR, log)

    log.info("TOTAL wall time: %.1fs", time.time() - t0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
