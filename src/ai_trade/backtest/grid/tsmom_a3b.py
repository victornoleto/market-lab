"""TSMOM Lead A3b — per-asset gate aggregation for Donchian breakout.

Consumes per-config net daily returns produced by
:func:`ai_trade.backtest.strategies.tsmom.simulate_tsmom` on a SINGLE
asset's full available history and applies the Phase 3 gates:

1. **PBO** (CSCV) over the full (T, N) returns matrix — < 0.5.
2. **DSR** per config over the OOS block with ``n_trials = N`` — p < 0.05.
3. **Walk-forward** 8 equal chunks over full period — ≥ 6/8 profitable
   AND no window MaxDD > cap (default 25%).
4. **Single-block OOS** Sharpe > 0 on the pre-specified OOS range.
5. **Forward-window stress** Sharpe > 0 on the pre-specified stress range.
6. **Stationary block bootstrap** 99.9% CI lower bound of OOS Sharpe > 0
   (survivors only).

Mirrors :mod:`ai_trade.backtest.grid.letf_rotation_b1c` structurally so
any helper can be swapped with minimal friction.

Citations
---------

* PBO / CSCV / 0.5 threshold: ``[advances_fin_ml, p.208-211]``.
* DSR p-value: ``[advances_fin_ml, p.196-202]``,
  ``[advances_fin_ml, p.273-275]``.
* Walk-forward ≥ 6/8 gate: Pardo (2008) ch.10-11 + ai-trade rule #5.
* Stationary bootstrap: ``[advances_fin_ml, p.196-202, ch.11]``.
* Donchian grid family (entry/exit pairs): ``[trading_systems_methods,
  p.353]``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np
import pandas as pd

from ai_trade.backtest.grid.letf_rotation_b1c import (
    TRADING_DAYS,
    SplitMetrics,
    bootstrap_sharpe_ci,
    compute_split_metrics,
    walk_forward_verdict_from_returns,
)
from ai_trade.backtest.strategies.tsmom import TSMOMConfig, TSMOMResult
from ai_trade.backtest.validation.dsr import dsr
from ai_trade.backtest.validation.pbo import pbo as cscv_pbo

log = logging.getLogger(__name__)

__all__ = [
    "TSMOMEvaluation",
    "A3bGateVerdict",
    "default_tsmom_grid",
    "evaluate_tsmom_gates",
]


@dataclass
class TSMOMEvaluation:
    """Per-config outputs for a single asset's grid cell."""

    config_id: int
    config: TSMOMConfig
    is_metrics: SplitMetrics
    oos_metrics: SplitMetrics
    stress_metrics: SplitMetrics
    wf_profitable_ratio: float
    wf_max_window_drawdown: float
    wf_pass: bool
    dsr_p_value: float
    bootstrap_sharpe_lo: float | None = None
    bootstrap_sharpe_hi: float | None = None
    verdict: str = "PENDING"
    failed_gates: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        c = self.config
        return {
            "config_id": self.config_id,
            "config": {
                "entry_lookback": c.entry_lookback,
                "exit_lookback": c.exit_lookback,
                "tax_rate": c.tax_rate,
                "commission_bps": c.commission_bps,
                "spread_bps": c.spread_bps,
            },
            "is": _metrics_dict(self.is_metrics),
            "oos": _metrics_dict(self.oos_metrics),
            "stress": _metrics_dict(self.stress_metrics),
            "wf_profitable_ratio": self.wf_profitable_ratio,
            "wf_max_window_drawdown": self.wf_max_window_drawdown,
            "wf_pass": self.wf_pass,
            "dsr_p_value": self.dsr_p_value,
            "bootstrap_sharpe_lo": self.bootstrap_sharpe_lo,
            "bootstrap_sharpe_hi": self.bootstrap_sharpe_hi,
            "verdict": self.verdict,
            "failed_gates": list(self.failed_gates),
        }


def _metrics_dict(m: SplitMetrics) -> dict:
    return {
        "name": m.name,
        "n_bars": m.n_bars,
        "sharpe": m.sharpe,
        "cagr": m.cagr,
        "max_drawdown": m.max_drawdown,
        "final_equity_from_unit": m.final_equity_from_unit,
    }


@dataclass
class A3bGateVerdict:
    """Per-asset verdict bundle."""

    asset: str
    pbo_value: float
    pbo_pass: bool
    n_configs: int
    n_passing_configs: int
    winner_config_id: int | None
    evaluations: list[TSMOMEvaluation]

    def to_dict(self) -> dict:
        return {
            "asset": self.asset,
            "pbo": self.pbo_value,
            "pbo_pass": self.pbo_pass,
            "n_configs": self.n_configs,
            "n_passing": self.n_passing_configs,
            "winner_config_id": self.winner_config_id,
            "evaluations": [e.to_dict() for e in self.evaluations],
        }


def default_tsmom_grid(
    entry_lookbacks: Sequence[int] = (20, 40, 55, 100),
    exit_lookbacks: Sequence[int] = (10, 20, 50),
    tax_rate: float = 0.15,
) -> list[TSMOMConfig]:
    """Return all (entry, exit) combos where ``exit <= entry``.

    Canonical Turtles pairs (e.g. 20/10, 40/20, 55/20) all included.
    Keeps tax + costs at mandate defaults.
    """
    grid: list[TSMOMConfig] = []
    for e in entry_lookbacks:
        for x in exit_lookbacks:
            if x > e:
                continue
            grid.append(
                TSMOMConfig(
                    entry_lookback=int(e),
                    exit_lookback=int(x),
                    tax_rate=tax_rate,
                )
            )
    return grid


def _slice_by_date(series: pd.Series, start: str, end: str) -> pd.Series:
    s = pd.Timestamp(start)
    e = pd.Timestamp(end)
    return series.loc[(series.index >= s) & (series.index <= e)]


def evaluate_tsmom_gates(
    asset: str,
    configs: Sequence[TSMOMConfig],
    results: Sequence[TSMOMResult],
    is_range: tuple[str, str],
    oos_range: tuple[str, str],
    stress_range: tuple[str, str],
    *,
    pbo_n_blocks: int = 10,
    dsr_alpha: float = 0.05,
    wf_n_windows: int = 8,
    wf_min_profitable_ratio: float = 6 / 8,
    wf_max_dd_cap: float = 0.25,
    bootstrap_alpha: float = 0.001,
    bootstrap_n_resamples: int = 2000,
    bootstrap_block_mean: int = 5,
    bootstrap_seed: int = 42,
) -> A3bGateVerdict:
    """Apply all A3b gates for ONE asset's config grid.

    See module docstring for gate ordering. The winner is the passing
    config with the highest OOS Sharpe; if none passes,
    ``winner_config_id`` is None.
    """
    if len(configs) != len(results):
        raise ValueError("configs and results must have equal length")
    if not results:
        raise ValueError("at least one (config, result) pair required")

    index = results[0].daily_returns.index
    for r in results[1:]:
        if not r.daily_returns.index.equals(index):
            raise ValueError("all results must share the same daily index")
    matrix = np.column_stack(
        [r.daily_returns.to_numpy(dtype=float) for r in results]
    )

    try:
        pbo_res = cscv_pbo(matrix, n_blocks=pbo_n_blocks)
        pbo_value = float(pbo_res.pbo)
    except ValueError as exc:
        log.warning("PBO failed for %s: %s", asset, exc)
        pbo_value = float("nan")
    pbo_pass = bool(np.isfinite(pbo_value) and pbo_value < 0.5)

    evaluations: list[TSMOMEvaluation] = []
    for i, (cfg, result) in enumerate(zip(configs, results)):
        full_net = result.daily_returns
        is_rets = _slice_by_date(full_net, *is_range)
        oos_rets = _slice_by_date(full_net, *oos_range)
        stress_rets = _slice_by_date(full_net, *stress_range)

        is_m = compute_split_metrics("IS", is_rets)
        oos_m = compute_split_metrics("OOS", oos_rets)
        stress_m = compute_split_metrics("Stress", stress_rets)

        dsr_p = float("nan")
        if len(oos_rets) >= 3 and len(configs) >= 2:
            try:
                dsr_res = dsr(
                    oos_rets.to_numpy(dtype=float), n_trials=len(configs)
                )
                dsr_p = float(dsr_res.p_value)
            except ValueError as exc:
                log.warning(
                    "DSR failed for %s config %d: %s", asset, i, exc
                )

        wf_ratio, wf_max_dd, wf_pass = walk_forward_verdict_from_returns(
            full_net,
            n_windows=wf_n_windows,
            min_profitable_ratio=wf_min_profitable_ratio,
            max_drawdown_cap=wf_max_dd_cap,
        )

        eval_obj = TSMOMEvaluation(
            config_id=i,
            config=cfg,
            is_metrics=is_m,
            oos_metrics=oos_m,
            stress_metrics=stress_m,
            wf_profitable_ratio=wf_ratio,
            wf_max_window_drawdown=wf_max_dd,
            wf_pass=wf_pass,
            dsr_p_value=dsr_p,
        )

        failed: list[str] = []
        if not pbo_pass:
            failed.append(f"PBO={pbo_value:.3f}>=0.5")
        if not (np.isfinite(dsr_p) and dsr_p < dsr_alpha):
            failed.append(f"DSR_p={dsr_p:.4f}>={dsr_alpha}")
        if not wf_pass:
            failed.append(
                f"WF ratio={wf_ratio:.2f} max_dd={wf_max_dd:.2%}"
            )
        if oos_m.sharpe <= 0:
            failed.append(f"OOS_Sharpe={oos_m.sharpe:.3f}<=0")
        if stress_m.sharpe <= 0:
            failed.append(f"Stress_Sharpe={stress_m.sharpe:.3f}<=0")

        if not failed:
            lo, hi = bootstrap_sharpe_ci(
                oos_rets,
                alpha=bootstrap_alpha,
                block_mean=bootstrap_block_mean,
                n_resamples=bootstrap_n_resamples,
                seed=bootstrap_seed,
                periods_per_year=TRADING_DAYS,
            )
            eval_obj.bootstrap_sharpe_lo = lo
            eval_obj.bootstrap_sharpe_hi = hi
            if not (np.isfinite(lo) and lo > 0):
                failed.append(f"bootstrap_lo={lo:.3f}<=0")

        eval_obj.failed_gates = failed
        eval_obj.verdict = "PASS" if not failed else "FAIL"
        evaluations.append(eval_obj)

    passers = [e for e in evaluations if e.verdict == "PASS"]
    winner_id: int | None = None
    if passers:
        winner = max(passers, key=lambda e: e.oos_metrics.sharpe)
        winner_id = winner.config_id

    return A3bGateVerdict(
        asset=asset,
        pbo_value=pbo_value,
        pbo_pass=pbo_pass,
        n_configs=len(configs),
        n_passing_configs=len(passers),
        winner_config_id=winner_id,
        evaluations=evaluations,
    )
