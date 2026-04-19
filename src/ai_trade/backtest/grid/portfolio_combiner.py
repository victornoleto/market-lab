"""Phase 3 Lead A3c — 2-strategy portfolio combiner + gates.

Combines two Path B [SWING BROKER] daily return streams into a blended
equity curve and applies the A3c gates defined by the investment
mandate:

* **Portfolio Sharpe > max(single-leg Sharpe)** on the common-window
  OOS split — primary gate.
* **Diversification Ratio DR > 1.2** on the common window — secondary
  gate per the HRP/IVP framework in ``[advances_fin_ml, p.302-313,
  ch.16]`` (Choueifaty-Coignard 2008 DR is the practitioner formula
  that the HRP recursive-bisection logic maximises implicitly).

Supporting robustness gates (reused from Lead B1c to keep the test
surface symmetric):

* DSR p-value < 0.05 on the OOS blended series with ``n_trials =
  len(blends)``.
* Walk-forward ≥ 6/8 windows profitable, MaxDD ≤ 25% per window on
  the full common-window series.
* OOS Sharpe > 0 AND Stress Sharpe > 0 on the mutually-exclusive
  common-window splits.
* Stationary-bootstrap 99.9% CI lower bound of OOS Sharpe > 0.

Blending families
-----------------

1. **equal_weight** — static 50/50. Naive benchmark, immune to
   covariance-estimation error [advances_fin_ml, p.298-299].
2. **ivp_static** — Inverse Variance Portfolio using IS-only σ. For
   two assets HRP collapses to IVP (one split). ``w₁ = σ₂² /
   (σ₁² + σ₂²)`` per ``[advances_fin_ml, p.307-308]``.
3. **ivp_rolling** — rolling 63-day IVP; weight on day ``t`` uses
   ``σ`` from the prior 63-day window (no look-ahead).
4. **mvp_static** — long-only Minimum-Variance Portfolio from IS-only
   Σ. Long-only clip avoids short-side blow-up on correlated legs.

Path tag: **[SWING BROKER]** — BR 15% capital-gains tax baked into
each leg's daily returns by the underlying simulators; no additional
tax adjustment at the blend layer.

Citations
---------

* HRP/IVP family + OOS variance comparison (``σ²_HRP 0.067 <
  σ²_IVP 0.093 < σ²_CLA 0.116``): ``[advances_fin_ml, p.302-313,
  ch.16]``, RULE ``[p.313]``.
* IVP formula ``αⱼ = 1 - σ²ⱼ / (σ²₁ + σ²₂)``: ``[advances_fin_ml,
  p.307-308]``.
* Markowitz instability rationale for preferring naive/IVP blends:
  ``[advances_fin_ml, p.298-299]``.
* PBO / CSCV: ``[advances_fin_ml, p.208-211]``.
* DSR: ``[advances_fin_ml, p.196-202]``, ``[advances_fin_ml,
  p.273-275]``.
* Stationary block bootstrap: ``[advances_fin_ml, p.196-202, ch.11]``.
* Walk-forward ≥ 6/8 gate: Pardo (2008) ch.10-11 + ai-trade rule #5.
* BR 15% swing tax: Investment Mandate §4.
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
from ai_trade.backtest.validation.dsr import dsr

log = logging.getLogger(__name__)

__all__ = [
    "align_returns",
    "blend_equal_weight",
    "blend_ivp_static",
    "blend_ivp_rolling",
    "blend_mvp_static",
    "diversification_ratio",
    "BlendEvaluation",
    "A3cGateVerdict",
    "evaluate_a3c_gates",
]


def align_returns(
    r1: pd.Series, r2: pd.Series
) -> tuple[pd.Series, pd.Series]:
    """Intersect two daily return series on common dates.

    Returns both series reindexed to the common date index. Drops dates
    where either side is NaN (strategies with different warmups will
    simply skip the pre-warmup tail).
    """
    common = r1.index.intersection(r2.index)
    if len(common) == 0:
        raise ValueError("series share no common index")
    a = r1.loc[common].astype(float)
    b = r2.loc[common].astype(float)
    mask = ~(a.isna() | b.isna())
    a = a.loc[mask]
    b = b.loc[mask]
    if a.empty:
        raise ValueError("no overlapping non-NaN bars")
    return a, b


def blend_equal_weight(r1: pd.Series, r2: pd.Series) -> pd.Series:
    """Static 50/50 blend of two aligned daily return series."""
    a, b = align_returns(r1, r2)
    blended = 0.5 * a + 0.5 * b
    blended.name = "equal_weight"
    return blended


def _sigma(returns: pd.Series) -> float:
    s = float(returns.dropna().std(ddof=1))
    if s == 0.0 or np.isnan(s):
        raise ValueError("zero/NaN volatility — cannot weight")
    return s


def blend_ivp_static(
    r1: pd.Series, r2: pd.Series, is_end: pd.Timestamp
) -> pd.Series:
    """Static Inverse Variance Portfolio blend using IS-only σ.

    Per ``[advances_fin_ml, p.307-308]``, IVP weight for asset ``j`` in
    a two-element group is ``αⱼ = 1 - σ²ⱼ / (σ²₁ + σ²₂)``. Applied
    forward to the full common-window series so OOS/Stress never see
    post-IS σ.
    """
    a, b = align_returns(r1, r2)
    is_a = a.loc[a.index <= is_end]
    is_b = b.loc[b.index <= is_end]
    if is_a.empty or is_b.empty:
        raise ValueError("IS slice is empty — cannot fit IVP weights")
    v1 = _sigma(is_a) ** 2
    v2 = _sigma(is_b) ** 2
    w1 = v2 / (v1 + v2)
    w2 = 1.0 - w1
    blended = w1 * a + w2 * b
    blended.name = f"ivp_static(w1={w1:.3f},w2={w2:.3f})"
    blended.attrs["weights"] = (w1, w2)
    return blended


def blend_ivp_rolling(
    r1: pd.Series,
    r2: pd.Series,
    lookback: int = 63,
) -> pd.Series:
    """Rolling IVP with trailing ``lookback``-day σ — no look-ahead.

    Day-``t`` weight uses σ estimated over ``[t-lookback, t-1]``. Before
    warmup, holds 50/50. Produces a single blended return series on the
    common index.
    """
    if lookback < 2:
        raise ValueError(f"lookback must be >= 2, got {lookback}")
    a, b = align_returns(r1, r2)
    sigma_a = a.rolling(window=lookback, min_periods=lookback).std(ddof=1).shift(1)
    sigma_b = b.rolling(window=lookback, min_periods=lookback).std(ddof=1).shift(1)
    var_a = sigma_a.pow(2)
    var_b = sigma_b.pow(2)
    denom = var_a + var_b
    with np.errstate(divide="ignore", invalid="ignore"):
        w1 = np.where(denom > 0, var_b / denom, 0.5)
    w1 = pd.Series(w1, index=a.index).fillna(0.5)
    w2 = 1.0 - w1
    blended = w1 * a + w2 * b
    blended.name = f"ivp_rolling(lookback={lookback})"
    blended.attrs["weights_series"] = (w1, w2)
    return blended


def blend_mvp_static(
    r1: pd.Series,
    r2: pd.Series,
    is_end: pd.Timestamp,
    long_only: bool = True,
) -> pd.Series:
    """Long-only Minimum-Variance Portfolio blend, IS-only Σ.

    Two-asset closed form:

    ``w₁ = (σ₂² - ρ σ₁ σ₂) / (σ₁² + σ₂² - 2 ρ σ₁ σ₂)``

    Clipped to [0, 1] when ``long_only`` — a negative weight here means
    the blend would short a positive-Sharpe leg, which defeats the point
    of combining winners. Preserves the ``[advances_fin_ml, p.298-299]``
    guard against unstable optimizer output.
    """
    a, b = align_returns(r1, r2)
    is_a = a.loc[a.index <= is_end]
    is_b = b.loc[b.index <= is_end]
    if is_a.empty or is_b.empty:
        raise ValueError("IS slice empty — cannot fit MVP weights")
    s1 = _sigma(is_a)
    s2 = _sigma(is_b)
    rho = float(pd.concat([is_a, is_b], axis=1).corr().iloc[0, 1])
    num = s2 * s2 - rho * s1 * s2
    den = s1 * s1 + s2 * s2 - 2.0 * rho * s1 * s2
    if den <= 0.0 or np.isnan(den):
        w1 = 0.5
    else:
        w1 = num / den
    if long_only:
        w1 = float(np.clip(w1, 0.0, 1.0))
    w2 = 1.0 - w1
    blended = w1 * a + w2 * b
    blended.name = f"mvp_static(w1={w1:.3f},w2={w2:.3f})"
    blended.attrs["weights"] = (w1, w2)
    blended.attrs["rho_is"] = rho
    return blended


def diversification_ratio(
    r1: pd.Series,
    r2: pd.Series,
    w1: float,
    w2: float,
) -> float:
    """Choueifaty-Coignard diversification ratio.

    ``DR = (w₁·σ₁ + w₂·σ₂) / σ_portfolio`` — a value > 1 means the
    blend's volatility is below the weighted average of leg volatilities
    (diversification gain). DR = 1 iff legs are perfectly correlated.

    Uses the full-sample σ of each aligned series.
    """
    a, b = align_returns(r1, r2)
    s1 = _sigma(a)
    s2 = _sigma(b)
    port = w1 * a + w2 * b
    sp = _sigma(port)
    if sp <= 0:
        raise ValueError("portfolio σ non-positive — cannot compute DR")
    return float((w1 * s1 + w2 * s2) / sp)


@dataclass
class BlendEvaluation:
    """Per-blend metrics for one combination method."""

    name: str
    weights: tuple[float, float] | str
    blended: pd.Series = field(repr=False)
    is_metrics: SplitMetrics
    oos_metrics: SplitMetrics
    stress_metrics: SplitMetrics
    wf_profitable_ratio: float
    wf_max_window_drawdown: float
    wf_pass: bool
    dsr_p_value: float
    bootstrap_sharpe_lo: float | None = None
    bootstrap_sharpe_hi: float | None = None
    diversification_ratio_is: float = float("nan")
    diversification_ratio_full: float = float("nan")
    pearson_full: float = float("nan")
    verdict: str = "PENDING"
    failed_gates: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        w = self.weights
        if isinstance(w, tuple):
            w_out: list | str = [float(w[0]), float(w[1])]
        else:
            w_out = str(w)
        return {
            "name": self.name,
            "weights": w_out,
            "is": _metrics_dict(self.is_metrics),
            "oos": _metrics_dict(self.oos_metrics),
            "stress": _metrics_dict(self.stress_metrics),
            "wf_profitable_ratio": self.wf_profitable_ratio,
            "wf_max_window_drawdown": self.wf_max_window_drawdown,
            "wf_pass": self.wf_pass,
            "dsr_p_value": self.dsr_p_value,
            "bootstrap_sharpe_lo": self.bootstrap_sharpe_lo,
            "bootstrap_sharpe_hi": self.bootstrap_sharpe_hi,
            "diversification_ratio_is": self.diversification_ratio_is,
            "diversification_ratio_full": self.diversification_ratio_full,
            "pearson_full": self.pearson_full,
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
class A3cGateVerdict:
    """Top-level A3c verdict covering all blends vs the single-leg baseline."""

    baseline_sharpe_oos: float
    baseline_leg_name: str
    leg_metrics: dict[str, dict]
    blends: list[BlendEvaluation]
    winner_blend: str | None

    def to_dict(self) -> dict:
        return {
            "baseline_sharpe_oos": self.baseline_sharpe_oos,
            "baseline_leg_name": self.baseline_leg_name,
            "leg_metrics": self.leg_metrics,
            "winner_blend": self.winner_blend,
            "blends": [b.to_dict() for b in self.blends],
        }


def _slice_by_range(s: pd.Series, rng: tuple[str, str]) -> pd.Series:
    start = pd.Timestamp(rng[0])
    end = pd.Timestamp(rng[1])
    return s.loc[(s.index >= start) & (s.index <= end)]


def _leg_split_block(
    r: pd.Series,
    is_range: tuple[str, str],
    oos_range: tuple[str, str],
    stress_range: tuple[str, str],
) -> dict:
    is_m = compute_split_metrics("IS", _slice_by_range(r, is_range))
    oos_m = compute_split_metrics("OOS", _slice_by_range(r, oos_range))
    st_m = compute_split_metrics("Stress", _slice_by_range(r, stress_range))
    return {
        "is": _metrics_dict(is_m),
        "oos": _metrics_dict(oos_m),
        "stress": _metrics_dict(st_m),
    }


def evaluate_a3c_gates(
    r1: pd.Series,
    r2: pd.Series,
    leg_names: tuple[str, str],
    is_range: tuple[str, str],
    oos_range: tuple[str, str],
    stress_range: tuple[str, str],
    *,
    dr_threshold: float = 1.2,
    dsr_alpha: float = 0.05,
    wf_n_windows: int = 8,
    wf_min_profitable_ratio: float = 6 / 8,
    wf_max_dd_cap: float = 0.25,
    bootstrap_alpha: float = 0.001,
    bootstrap_n_resamples: int = 2000,
    bootstrap_block_mean: int = 5,
    bootstrap_seed: int = 42,
    rolling_lookback: int = 63,
) -> A3cGateVerdict:
    """Blend ``r1`` + ``r2`` via all 4 families, gate each blend.

    The baseline Sharpe for the primary gate is the **max** of the two
    legs' OOS Sharpes on the common-window OOS split. A blend passes
    iff:

    * OOS Sharpe > baseline AND
    * DR (full common window) > ``dr_threshold`` AND
    * DSR p-value < ``dsr_alpha`` on OOS AND
    * WF profitable ratio ≥ ``wf_min_profitable_ratio`` and every WF
      window's MaxDD ≤ ``wf_max_dd_cap`` AND
    * OOS Sharpe > 0 AND Stress Sharpe > 0 AND
    * Bootstrap 99.9% CI lower bound of OOS Sharpe > 0.

    Winner = passing blend with highest OOS Sharpe; ``None`` if no blend
    passes.
    """
    a, b = align_returns(r1, r2)
    if a.empty:
        raise ValueError("no common bars after alignment")
    is_end = pd.Timestamp(is_range[1])

    # --- single-leg metrics on the common-window splits ---
    leg_blocks = {
        leg_names[0]: _leg_split_block(a, is_range, oos_range, stress_range),
        leg_names[1]: _leg_split_block(b, is_range, oos_range, stress_range),
    }
    oos_sharpes = {
        leg_names[0]: leg_blocks[leg_names[0]]["oos"]["sharpe"],
        leg_names[1]: leg_blocks[leg_names[1]]["oos"]["sharpe"],
    }
    baseline_leg = max(oos_sharpes, key=lambda k: oos_sharpes[k])
    baseline_sharpe = oos_sharpes[baseline_leg]

    # --- build blends ---
    blends_raw: list[tuple[str, pd.Series]] = [
        ("equal_weight", blend_equal_weight(a, b)),
        ("ivp_static", blend_ivp_static(a, b, is_end)),
        ("ivp_rolling", blend_ivp_rolling(a, b, lookback=rolling_lookback)),
        ("mvp_static", blend_mvp_static(a, b, is_end, long_only=True)),
    ]

    # --- DSR: per-blend, n_trials = len(blends) ---
    n_trials = len(blends_raw)
    oos_per_blend = {
        name: _slice_by_range(b_series, oos_range).dropna()
        for name, b_series in blends_raw
    }

    evaluations: list[BlendEvaluation] = []
    for name, series in blends_raw:
        is_m = compute_split_metrics(
            "IS", _slice_by_range(series, is_range)
        )
        oos_m = compute_split_metrics(
            "OOS", _slice_by_range(series, oos_range)
        )
        st_m = compute_split_metrics(
            "Stress", _slice_by_range(series, stress_range)
        )

        # Walk-forward on full common-window returns.
        wf_ratio, wf_maxdd, wf_ok = walk_forward_verdict_from_returns(
            series.dropna(),
            n_windows=wf_n_windows,
            min_profitable_ratio=wf_min_profitable_ratio,
            max_drawdown_cap=wf_max_dd_cap,
        )

        # DSR on OOS.
        oos_vec = oos_per_blend[name].to_numpy(dtype=float)
        dsr_p = float("nan")
        if oos_vec.size > 1 and np.std(oos_vec, ddof=1) > 0:
            try:
                dsr_res = dsr(oos_vec, n_trials=n_trials)
                dsr_p = float(dsr_res.p_value)
            except Exception as exc:  # pragma: no cover - defensive
                log.warning("DSR failed for %s: %s", name, exc)

        # IS diversification ratio (weights known for each blend).
        weights_attr = series.attrs.get(
            "weights", series.attrs.get("weights_series", None)
        )
        if isinstance(weights_attr, tuple) and isinstance(
            weights_attr[0], float
        ):
            w1, w2 = weights_attr
            dr_full = diversification_ratio(a, b, w1, w2)
            # IS-only DR uses same weights on IS slice.
            dr_is = diversification_ratio(
                a.loc[a.index <= is_end],
                b.loc[b.index <= is_end],
                w1,
                w2,
            )
            weights_out: tuple[float, float] | str = (float(w1), float(w2))
        else:  # rolling blend — report average weights
            ws = series.attrs.get("weights_series")
            if ws is not None:
                w1_series, w2_series = ws
                w1_mean = float(w1_series.mean())
                w2_mean = float(w2_series.mean())
                dr_full = diversification_ratio(a, b, w1_mean, w2_mean)
                dr_is = diversification_ratio(
                    a.loc[a.index <= is_end],
                    b.loc[b.index <= is_end],
                    w1_mean,
                    w2_mean,
                )
                weights_out = (w1_mean, w2_mean)
            else:  # equal_weight
                dr_full = diversification_ratio(a, b, 0.5, 0.5)
                dr_is = diversification_ratio(
                    a.loc[a.index <= is_end],
                    b.loc[b.index <= is_end],
                    0.5,
                    0.5,
                )
                weights_out = (0.5, 0.5)

        pearson = float(pd.concat([a, b], axis=1).corr().iloc[0, 1])

        # Evaluate gates.
        failed: list[str] = []
        if oos_m.sharpe <= baseline_sharpe:
            failed.append(f"SHARPE_LE_BASELINE({baseline_sharpe:.3f})")
        if dr_full <= dr_threshold:
            failed.append(f"DR_LE_{dr_threshold}")
        if not (dsr_p < dsr_alpha):
            failed.append("DSR")
        if not wf_ok:
            failed.append("WF")
        if oos_m.sharpe <= 0:
            failed.append("OOS_SHARPE_LE_0")
        if st_m.sharpe <= 0:
            failed.append("STRESS_SHARPE_LE_0")

        # Bootstrap only for blends that haven't failed primary gates yet
        # (save runtime; bootstrap is the last reinforcement gate).
        boot_lo: float | None = None
        boot_hi: float | None = None
        if not failed:
            oos_series = _slice_by_range(series, oos_range).dropna()
            lo, hi = bootstrap_sharpe_ci(
                oos_series,
                alpha=bootstrap_alpha,
                n_resamples=bootstrap_n_resamples,
                block_mean=bootstrap_block_mean,
                seed=bootstrap_seed,
            )
            boot_lo, boot_hi = lo, hi
            if not (lo > 0):
                failed.append("BOOTSTRAP_LO_LE_0")

        verdict = "PASS" if not failed else "FAIL"
        evaluations.append(
            BlendEvaluation(
                name=name,
                weights=weights_out,
                blended=series,
                is_metrics=is_m,
                oos_metrics=oos_m,
                stress_metrics=st_m,
                wf_profitable_ratio=wf_ratio,
                wf_max_window_drawdown=wf_maxdd,
                wf_pass=wf_ok,
                dsr_p_value=dsr_p,
                bootstrap_sharpe_lo=boot_lo,
                bootstrap_sharpe_hi=boot_hi,
                diversification_ratio_is=float(dr_is),
                diversification_ratio_full=float(dr_full),
                pearson_full=pearson,
                verdict=verdict,
                failed_gates=failed,
            )
        )

    passing = [e for e in evaluations if e.verdict == "PASS"]
    winner = (
        max(passing, key=lambda e: e.oos_metrics.sharpe).name
        if passing
        else None
    )

    return A3cGateVerdict(
        baseline_sharpe_oos=float(baseline_sharpe),
        baseline_leg_name=baseline_leg,
        leg_metrics=leg_blocks,
        blends=evaluations,
        winner_blend=winner,
    )
