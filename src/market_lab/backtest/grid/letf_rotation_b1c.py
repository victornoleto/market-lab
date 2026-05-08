"""LETF rotation Lead B1c — gate aggregation over the full grid.

Consumes per-config net daily-return series produced by
:func:`market_lab.backtest.strategies.letf_rotation.simulate_letf_rotation`
on the full 1970-2026 SPX TR window, and applies the Phase 3 gates in
order:

1. **PBO** (CSCV) over the full (T, N) returns matrix — must be < 0.5.
2. **DSR** per config over the OOS block with ``n_trials = N`` — p < 0.05.
3. **Walk-forward** 8 equal chunks over the full period — ≥ 6/8 profitable
   and MaxDD ≤ 25% in every window.
4. **Single-block OOS** — OOS Sharpe > 0 on the canonical Gayed window
   (2001-2015).
5. **Forward-window stress** — Stress Sharpe > 0 on 2016-2026.
6. **Stationary block bootstrap** (Politis-Romano 1994) — 99.9% CI lower
   bound of OOS Sharpe > 0 (gates survivors only, for speed).

Keeping the heavy lifting in pure helpers so the orchestrator script
stays declarative and the test surface is minimal.

Citations
---------

* PBO / CSCV and overfit threshold 0.5: ``[advances_fin_ml, p.208-211]``.
* DSR / PSR framework: ``[advances_fin_ml, p.196-202]``,
  ``[advances_fin_ml, p.273-275]``.
* Walk-forward ≥ 6/8 gate: Pardo (2008) ch.10-11 + market-lab rule #5.
* Stationary block bootstrap for Sharpe CI on serially-correlated trades:
  ``[advances_fin_ml, p.196-202, ch.11]``.
* Gayed canonical splits (IS 1970-2000 / OOS 2001-2015):
  ``[leverage_for_the_long_run, p.13, p.14, Table 5-6]``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np
import pandas as pd

from market_lab.backtest.strategies.letf_rotation import (
    LETFRotationConfig,
    RotationResult,
)
from market_lab.backtest.validation.bootstrap import stationary_bootstrap_trades
from market_lab.backtest.validation.dsr import dsr, sharpe_periodic
from market_lab.backtest.validation.pbo import pbo as cscv_pbo


log = logging.getLogger(__name__)

__all__ = [
    "TRADING_DAYS",
    "SplitMetrics",
    "ConfigEvaluation",
    "B1cGateVerdict",
    "compute_split_metrics",
    "split_into_windows",
    "walk_forward_verdict_from_returns",
    "bootstrap_sharpe_ci",
    "evaluate_b1c_gates",
]


TRADING_DAYS = 252
"""Trading days per year for Sharpe / CAGR annualization (equity)."""


@dataclass(frozen=True)
class SplitMetrics:
    """Performance metrics for a named date-range slice of a daily series."""

    name: str
    n_bars: int
    sharpe: float
    cagr: float
    max_drawdown: float
    final_equity_from_unit: float


@dataclass
class ConfigEvaluation:
    """All per-config outputs the gate step needs."""

    config_id: int
    config: LETFRotationConfig
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
                "filter": c.filter,
                "lookback": c.lookback,
                "band_pct": c.band_pct,
                "leverage": c.leverage,
                "gold_weight": c.gold_weight,
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
class B1cGateVerdict:
    """Top-level grid outcome."""

    pbo_value: float
    pbo_pass: bool
    n_configs: int
    n_passing_configs: int
    winner_config_id: int | None
    evaluations: list[ConfigEvaluation]

    def to_dict(self) -> dict:
        return {
            "pbo": self.pbo_value,
            "pbo_pass": self.pbo_pass,
            "n_configs": self.n_configs,
            "n_passing": self.n_passing_configs,
            "winner_config_id": self.winner_config_id,
            "evaluations": [e.to_dict() for e in self.evaluations],
        }


def compute_split_metrics(
    name: str,
    returns: pd.Series,
    periods_per_year: int = TRADING_DAYS,
) -> SplitMetrics:
    """Annualized Sharpe / CAGR / MaxDD on the net daily returns of a slice.

    Sharpe uses ``ddof=1`` (sample std) to align with
    :meth:`RotationResult.sharpe`.
    """
    r = returns.dropna().astype(float)
    if r.empty:
        return SplitMetrics(name, 0, 0.0, 0.0, 0.0, 1.0)

    mu = float(r.mean())
    sigma = float(r.std(ddof=1))
    sharpe = (mu / sigma * np.sqrt(periods_per_year)) if sigma > 0 else 0.0

    equity = (1.0 + r).cumprod()
    final = float(equity.iloc[-1])
    years = len(r) / periods_per_year
    cagr = (final ** (1.0 / years) - 1.0) if years > 0 and final > 0 else 0.0

    peak = equity.cummax()
    mdd = float((equity / peak - 1.0).min())

    return SplitMetrics(
        name=name,
        n_bars=int(len(r)),
        sharpe=float(sharpe),
        cagr=float(cagr),
        max_drawdown=float(mdd),
        final_equity_from_unit=final,
    )


def split_into_windows(
    returns: pd.Series, n_windows: int = 8
) -> list[pd.Series]:
    """Split a daily returns series into ``n_windows`` contiguous chunks.

    Chunks are returned in index order; the last chunk absorbs the
    remainder if ``len(returns) % n_windows != 0``.
    """
    if n_windows < 1:
        raise ValueError(f"n_windows must be >= 1, got {n_windows}")
    r = returns.dropna()
    n = len(r)
    if n < n_windows:
        raise ValueError(
            f"too few bars ({n}) for {n_windows} walk-forward windows"
        )
    size = n // n_windows
    out: list[pd.Series] = []
    for i in range(n_windows):
        start = i * size
        end = (i + 1) * size if i < n_windows - 1 else n
        out.append(r.iloc[start:end])
    return out


def walk_forward_verdict_from_returns(
    returns: pd.Series,
    n_windows: int = 8,
    min_profitable_ratio: float = 6 / 8,
    max_drawdown_cap: float = 0.25,
) -> tuple[float, float, bool]:
    """Walk-forward verdict directly from a daily returns series.

    Returns ``(profitable_ratio, max_window_drawdown, pass)``:

    * ``profitable_ratio`` — fraction of the ``n_windows`` chunks whose
      total compound return is > 0.
    * ``max_window_drawdown`` — largest drawdown *magnitude* (positive
      number, e.g. 0.31 = -31%) observed inside any of the chunks.
    * ``pass`` — True iff profitable_ratio ≥ ``min_profitable_ratio`` AND
      no window's MaxDD exceeds ``max_drawdown_cap``.
    """
    windows = split_into_windows(returns, n_windows=n_windows)
    profitable = 0
    max_dd = 0.0
    for w in windows:
        eq = (1.0 + w).cumprod()
        if float(eq.iloc[-1]) > 1.0:
            profitable += 1
        peak = eq.cummax()
        dd_mag = float(-(eq / peak - 1.0).min())
        max_dd = max(max_dd, dd_mag)
    ratio = profitable / n_windows
    passed = (ratio >= min_profitable_ratio) and (max_dd <= max_drawdown_cap)
    return ratio, max_dd, passed


def bootstrap_sharpe_ci(
    returns: pd.Series | np.ndarray,
    alpha: float = 0.001,
    block_mean: int = 5,
    n_resamples: int = 2000,
    seed: int = 42,
    periods_per_year: int = TRADING_DAYS,
) -> tuple[float, float]:
    """Stationary-bootstrap CI for the annualized Sharpe.

    ``alpha = 0.001`` → 99.9% two-sided CI (quantiles 0.0005 and 0.9995).
    Politis-Romano (1994) block resampling preserves short-range serial
    dependence; ``block_mean=5`` is the default for mild autocorrelation
    per ``[advances_fin_ml, p.196-202]``.
    """
    r = np.asarray(
        returns.dropna() if isinstance(returns, pd.Series) else returns,
        dtype=float,
    )
    if r.size < 3:
        return float("nan"), float("nan")
    boot = stationary_bootstrap_trades(
        r, block_mean=block_mean, n_resamples=n_resamples, seed=seed
    )
    mu = boot.mean(axis=1)
    sigma = boot.std(axis=1, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        sharpes = np.where(sigma > 0, mu / sigma * np.sqrt(periods_per_year), 0.0)
    lo = float(np.quantile(sharpes, alpha / 2.0))
    hi = float(np.quantile(sharpes, 1.0 - alpha / 2.0))
    return lo, hi


def _slice_by_date(
    series: pd.Series, start: str, end: str
) -> pd.Series:
    s = pd.Timestamp(start)
    e = pd.Timestamp(end)
    return series.loc[(series.index >= s) & (series.index <= e)]


def evaluate_b1c_gates(
    configs: Sequence[LETFRotationConfig],
    results: Sequence[RotationResult],
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
) -> B1cGateVerdict:
    """Apply all B1c gates to an aligned grid of rotation results.

    ``configs`` and ``results`` are parallel sequences: ``results[i]``
    is :func:`simulate_letf_rotation` applied to ``configs[i]`` over the
    full period (IS + OOS + Stress concatenated). All results must share
    the same daily index.

    The gate order is:

    1. PBO (grid-level, applied to the stacked returns matrix). A failing
       PBO marks ALL configs as ``FAIL_PBO``; the per-config gates are
       still reported for introspection.
    2. Per-config: DSR p-value < ``dsr_alpha`` on OOS returns.
    3. Per-config: WF 8-window gate on full-period returns.
    4. Per-config: OOS Sharpe > 0 AND Stress Sharpe > 0.
    5. Per-config (survivors of 2-4 only): bootstrap 99.9% CI lower
       bound > 0 on OOS Sharpe.

    The winner is the passing config with the highest OOS Sharpe; if
    none passes, ``winner_config_id`` is ``None``.
    """
    if len(configs) != len(results):
        raise ValueError("configs and results must have equal length")
    if not results:
        raise ValueError("at least one (config, result) pair required")

    # Align the (T, N) matrix of daily returns.
    index = results[0].daily_returns.index
    for r in results[1:]:
        if not r.daily_returns.index.equals(index):
            raise ValueError("all results must share the same daily index")
    matrix = np.column_stack(
        [r.daily_returns.to_numpy(dtype=float) for r in results]
    )

    # --- Gate 1: PBO (grid-level) ---
    try:
        pbo_res = cscv_pbo(matrix, n_blocks=pbo_n_blocks)
        pbo_value = float(pbo_res.pbo)
    except ValueError as exc:
        log.warning("PBO failed: %s", exc)
        pbo_value = float("nan")
    pbo_pass = bool(np.isfinite(pbo_value) and pbo_value < 0.5)

    evaluations: list[ConfigEvaluation] = []
    for i, (cfg, result) in enumerate(zip(configs, results)):
        full_net = result.daily_returns

        is_rets = _slice_by_date(full_net, *is_range)
        oos_rets = _slice_by_date(full_net, *oos_range)
        stress_rets = _slice_by_date(full_net, *stress_range)

        is_m = compute_split_metrics("IS", is_rets)
        oos_m = compute_split_metrics("OOS", oos_rets)
        stress_m = compute_split_metrics("Stress", stress_rets)

        # --- Gate 2: DSR (per-config on OOS) ---
        dsr_p = float("nan")
        if len(oos_rets) >= 3 and len(configs) >= 2:
            try:
                dsr_res = dsr(oos_rets.to_numpy(dtype=float), n_trials=len(configs))
                dsr_p = float(dsr_res.p_value)
            except ValueError as exc:
                log.warning(
                    "DSR failed for config %d: %s", i, exc
                )

        # --- Gate 3: Walk-forward on full period ---
        wf_ratio, wf_max_dd, wf_pass = walk_forward_verdict_from_returns(
            full_net,
            n_windows=wf_n_windows,
            min_profitable_ratio=wf_min_profitable_ratio,
            max_drawdown_cap=wf_max_dd_cap,
        )

        eval_obj = ConfigEvaluation(
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

        # --- Gate 5: Bootstrap 99.9% CI on OOS (survivors only) ---
        if not failed:
            lo, hi = bootstrap_sharpe_ci(
                oos_rets,
                alpha=bootstrap_alpha,
                block_mean=bootstrap_block_mean,
                n_resamples=bootstrap_n_resamples,
                seed=bootstrap_seed,
            )
            eval_obj.bootstrap_sharpe_lo = lo
            eval_obj.bootstrap_sharpe_hi = hi
            if not (np.isfinite(lo) and lo > 0):
                failed.append(f"bootstrap_lo={lo:.3f}<=0")

        eval_obj.failed_gates = failed
        eval_obj.verdict = "PASS" if not failed else "FAIL"
        evaluations.append(eval_obj)

    passers = [e for e in evaluations if e.verdict == "PASS"]
    if passers:
        winner = max(passers, key=lambda e: e.oos_metrics.sharpe)
        winner_id: int | None = winner.config_id
    else:
        winner_id = None

    return B1cGateVerdict(
        pbo_value=pbo_value,
        pbo_pass=pbo_pass,
        n_configs=len(configs),
        n_passing_configs=len(passers),
        winner_config_id=winner_id,
        evaluations=evaluations,
    )
