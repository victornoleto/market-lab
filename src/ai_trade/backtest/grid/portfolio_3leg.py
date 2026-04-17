"""Phase 3 Lead A3d — 3-strategy portfolio combiner + gates.

Extends the 2-leg :mod:`portfolio_combiner` (iter 37) to three daily-
return streams. Target use-case:

* Leg 1 — LETF rotation EMA100/0%/2x (Path B winner, iter 32)
* Leg 2 — QQQ Donchian 20/10   (Path B winner, iter 36)
* Leg 3 — 3rd-leg candidate (TLT Donchian 55/20 or GLD Donchian 40/20)

Goal: find a 3rd leg whose |ρ| with the LETF leg is < 0.2 AND whose
Sharpe > 0 on the common window, then blend via HRP/IVP to push the
Diversification Ratio above **1.3**. A3c (2-leg LETF+QQQ) already
confirmed EW/IVP beat baseline on Sharpe but failed DR=1.124 < 1.2 due
to ρ=0.555 (both long-equity US). Adding an uncorrelated long-duration
(TLT) or precious-metal (GLD) regime-switch leg is the mandated next
move per the mandate + ``[advances_fin_ml, p.302-313, ch.16]``.

Blending families
-----------------

1. **equal_weight** — static 1/3 each. Naive benchmark, immune to Σ
   estimation error [advances_fin_ml, p.298-299].
2. **ivp_static** — IS-only IVP ``wⱼ = (1/σⱼ²) / Σ (1/σᵢ²)``
   [advances_fin_ml, p.307-308].
3. **hrp_static** — López de Prado Hierarchical Risk Parity:
   single-linkage cluster on ``d = √((1-ρ)/2)``, quasi-diagonalize,
   recursive bisection by cluster variance. For 3 assets the tree is
   [[X, Y], Z] or [X, [Y, Z]] — HRP assigns weights `α` at the top split
   and IVP within the 2-asset cluster. Listing 16.2 implementation
   [advances_fin_ml, p.308].

Diversification Ratio (Choueifaty-Coignard 2008)
-------------------------------------------------

``DR = (Σ wᵢ σᵢ) / σ_portfolio``. Gate threshold for A3d = **1.3** (vs
A3c's 1.2 — we require a bigger diversification gain since we're now
paying for 3 legs of costs/taxes).

Path tag: **[SWING BROKER]** — BR 15% capital-gains tax baked into each
leg's daily returns; no blend-layer tax.
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
    "align_returns_3",
    "blend_equal_weight_3",
    "blend_ivp_static_3",
    "blend_hrp_3",
    "diversification_ratio_3",
    "BlendEvaluation3",
    "A3dGateVerdict",
    "evaluate_a3d_gates",
]


def align_returns_3(
    r1: pd.Series, r2: pd.Series, r3: pd.Series
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Intersect three daily-return series on common non-NaN dates.

    Drops any date where any leg is NaN. Raises if the intersection is
    empty.
    """
    common = r1.index.intersection(r2.index).intersection(r3.index)
    if len(common) == 0:
        raise ValueError("three series share no common index")
    a = r1.loc[common].astype(float)
    b = r2.loc[common].astype(float)
    c = r3.loc[common].astype(float)
    mask = ~(a.isna() | b.isna() | c.isna())
    a = a.loc[mask]
    b = b.loc[mask]
    c = c.loc[mask]
    if a.empty:
        raise ValueError("no overlapping non-NaN bars across three legs")
    return a, b, c


def blend_equal_weight_3(
    r1: pd.Series, r2: pd.Series, r3: pd.Series
) -> pd.Series:
    """Static 1/3/1/3/1/3 blend of three aligned daily-return series."""
    a, b, c = align_returns_3(r1, r2, r3)
    blended = (a + b + c) / 3.0
    blended.name = "equal_weight_3"
    blended.attrs["weights"] = (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)
    return blended


def _sigma(returns: pd.Series) -> float:
    s = float(returns.dropna().std(ddof=1))
    if s == 0.0 or np.isnan(s):
        raise ValueError("zero/NaN volatility — cannot weight leg")
    return s


def blend_ivp_static_3(
    r1: pd.Series, r2: pd.Series, r3: pd.Series, is_end: pd.Timestamp
) -> pd.Series:
    """Inverse Variance Portfolio blend for 3 legs, IS-only σ².

    ``wⱼ = (1/σⱼ²) / Σ (1/σᵢ²)`` — the general-k formula that collapses
    to the 2-asset A3c one under k=2. Applied forward to the full common
    window so OOS/Stress never see post-IS σ.

    [advances_fin_ml, p.307-308].
    """
    a, b, c = align_returns_3(r1, r2, r3)
    is_mask = a.index <= is_end
    is_slices = [a.loc[is_mask], b.loc[is_mask], c.loc[is_mask]]
    if any(s.empty for s in is_slices):
        raise ValueError("IS slice empty for at least one leg — cannot fit IVP")
    sigmas = np.array([_sigma(s) for s in is_slices])
    inv_var = 1.0 / (sigmas ** 2)
    weights = inv_var / inv_var.sum()
    w1, w2, w3 = float(weights[0]), float(weights[1]), float(weights[2])
    blended = w1 * a + w2 * b + w3 * c
    blended.name = f"ivp_static_3(w={w1:.3f},{w2:.3f},{w3:.3f})"
    blended.attrs["weights"] = (w1, w2, w3)
    return blended


def _cluster_var(cov: np.ndarray, items: list[int]) -> float:
    """Cluster variance under IVP within the cluster, per Prado Listing 16.2.

    Given ``cov`` (k×k) and ``items`` (subset of indices), compute
    ``w' · cov_sub · w`` where ``w`` is the inverse-variance portfolio
    restricted to ``items`` [advances_fin_ml, p.308].
    """
    sub = cov[np.ix_(items, items)]
    ivp = 1.0 / np.diag(sub)
    ivp = ivp / ivp.sum()
    return float(ivp @ sub @ ivp)


def _quasi_diagonal_order(corr: np.ndarray) -> list[int]:
    """Return a leaf ordering via single-linkage on HRP distance.

    Distance ``d_{ij} = √((1 - ρ_{ij}) / 2)``. Returns the leaf index
    list produced by ``scipy.cluster.hierarchy.leaves_list``. Requires
    scipy; error surfaces upstream if missing.
    """
    from scipy.cluster.hierarchy import leaves_list, linkage
    from scipy.spatial.distance import squareform

    dist = np.sqrt(np.clip((1.0 - corr) / 2.0, 0.0, 1.0))
    condensed = squareform(dist, checks=False)
    link = linkage(condensed, method="single")
    return [int(i) for i in leaves_list(link)]


def blend_hrp_3(
    r1: pd.Series, r2: pd.Series, r3: pd.Series, is_end: pd.Timestamp
) -> pd.Series:
    """Hierarchical Risk Parity blend for 3 legs (Listing 16.2, p.308).

    Steps:

    1. Align + slice IS only (no look-ahead).
    2. Compute IS correlation + covariance.
    3. Distance ``d = √((1-ρ)/2)``; single-linkage agglomerate.
    4. Quasi-diagonalize via ``leaves_list``.
    5. Recursive bisection: split the ordered list in halves, weight
       each cluster by inverse cluster-variance, descend.

    For k=3 the top split is always [1, 2] (one leaf on one side, two on
    the other), and the 2-leaf cluster receives IVP weights internally.
    """
    a, b, c = align_returns_3(r1, r2, r3)
    is_mask = a.index <= is_end
    df_is = pd.concat(
        [a.loc[is_mask], b.loc[is_mask], c.loc[is_mask]], axis=1
    ).dropna()
    if df_is.shape[0] < 2:
        raise ValueError("IS slice too small for HRP (< 2 bars)")
    corr = df_is.corr().to_numpy()
    cov = df_is.cov().to_numpy()
    if np.any(~np.isfinite(corr)) or np.any(~np.isfinite(cov)):
        raise ValueError("non-finite corr/cov in IS slice — cannot run HRP")

    order = _quasi_diagonal_order(corr)

    w = np.ones(3, dtype=float)
    clusters: list[list[int]] = [order]
    while clusters:
        new_clusters: list[list[int]] = []
        for cl in clusters:
            if len(cl) > 1:
                half = len(cl) // 2
                new_clusters.append(cl[:half])
                new_clusters.append(cl[half:])
        for i in range(0, len(new_clusters), 2):
            c0 = new_clusters[i]
            c1 = new_clusters[i + 1]
            v0 = _cluster_var(cov, c0)
            v1 = _cluster_var(cov, c1)
            denom = v0 + v1
            alpha = 1.0 - v0 / denom if denom > 0 else 0.5
            for idx in c0:
                w[idx] *= alpha
            for idx in c1:
                w[idx] *= 1.0 - alpha
        clusters = [cl for cl in new_clusters if len(cl) > 1]

    total = w.sum()
    if total <= 0 or not np.isfinite(total):
        raise ValueError("HRP weights summed to non-positive — cannot normalise")
    w = w / total
    w1, w2, w3 = float(w[0]), float(w[1]), float(w[2])
    blended = w1 * a + w2 * b + w3 * c
    blended.name = f"hrp_3(w={w1:.3f},{w2:.3f},{w3:.3f})"
    blended.attrs["weights"] = (w1, w2, w3)
    blended.attrs["hrp_order"] = tuple(order)
    return blended


def diversification_ratio_3(
    r1: pd.Series,
    r2: pd.Series,
    r3: pd.Series,
    weights: tuple[float, float, float],
) -> float:
    """Choueifaty-Coignard DR for 3 legs on the full aligned window.

    ``DR = (w₁·σ₁ + w₂·σ₂ + w₃·σ₃) / σ_portfolio``. Value > 1 means the
    blend's volatility is below the weighted average of individual vols.
    """
    a, b, c = align_returns_3(r1, r2, r3)
    sigmas = np.array([_sigma(a), _sigma(b), _sigma(c)])
    w = np.array(weights, dtype=float)
    if w.shape != (3,):
        raise ValueError("weights must be a 3-tuple")
    port = w[0] * a + w[1] * b + w[2] * c
    sp = _sigma(port)
    if sp <= 0:
        raise ValueError("portfolio σ non-positive — cannot compute DR")
    return float((w @ sigmas) / sp)


@dataclass
class BlendEvaluation3:
    """Per-blend metrics for a 3-leg combination method."""

    name: str
    weights: tuple[float, float, float]
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
    diversification_ratio_full: float = float("nan")
    diversification_ratio_is: float = float("nan")
    pearson_pairs_full: dict[str, float] = field(default_factory=dict)
    verdict: str = "PENDING"
    failed_gates: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "weights": [float(w) for w in self.weights],
            "is": _metrics_dict(self.is_metrics),
            "oos": _metrics_dict(self.oos_metrics),
            "stress": _metrics_dict(self.stress_metrics),
            "wf_profitable_ratio": self.wf_profitable_ratio,
            "wf_max_window_drawdown": self.wf_max_window_drawdown,
            "wf_pass": self.wf_pass,
            "dsr_p_value": self.dsr_p_value,
            "bootstrap_sharpe_lo": self.bootstrap_sharpe_lo,
            "bootstrap_sharpe_hi": self.bootstrap_sharpe_hi,
            "diversification_ratio_full": self.diversification_ratio_full,
            "diversification_ratio_is": self.diversification_ratio_is,
            "pearson_pairs_full": dict(self.pearson_pairs_full),
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
class A3dGateVerdict:
    """Top-level A3d verdict — all 3-leg blends vs the best single-leg baseline."""

    baseline_sharpe_oos: float
    baseline_leg_name: str
    leg_metrics: dict[str, dict]
    leg_correlations: dict[str, float]
    screening_pass: dict[str, bool]
    blends: list[BlendEvaluation3]
    winner_blend: str | None

    def to_dict(self) -> dict:
        return {
            "baseline_sharpe_oos": self.baseline_sharpe_oos,
            "baseline_leg_name": self.baseline_leg_name,
            "leg_metrics": self.leg_metrics,
            "leg_correlations": self.leg_correlations,
            "screening_pass": self.screening_pass,
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


def evaluate_a3d_gates(
    r1: pd.Series,
    r2: pd.Series,
    r3: pd.Series,
    leg_names: tuple[str, str, str],
    is_range: tuple[str, str],
    oos_range: tuple[str, str],
    stress_range: tuple[str, str],
    *,
    dr_threshold: float = 1.3,
    dsr_alpha: float = 0.05,
    wf_n_windows: int = 8,
    wf_min_profitable_ratio: float = 6 / 8,
    wf_max_dd_cap: float = 0.25,
    bootstrap_alpha: float = 0.001,
    bootstrap_n_resamples: int = 2000,
    bootstrap_block_mean: int = 5,
    bootstrap_seed: int = 42,
    screening_corr_threshold: float = 0.2,
) -> A3dGateVerdict:
    """Blend ``r1,r2,r3`` via EW/IVP/HRP, gate each blend vs baseline.

    Baseline Sharpe = max of the three legs' OOS Sharpes on the common-
    window OOS split. A blend passes iff:

    * OOS Sharpe > baseline AND
    * DR (full common window) > ``dr_threshold`` AND
    * DSR p < ``dsr_alpha`` on OOS AND
    * WF profitable ratio ≥ threshold AND WF max MaxDD ≤ cap AND
    * OOS Sharpe > 0 AND Stress Sharpe > 0 AND
    * Bootstrap 99.9% CI lower bound of OOS Sharpe > 0.

    Screening (pair ρ < ``screening_corr_threshold`` with leg 1) is
    reported separately but does NOT gate; this is documentation of
    whether the lead's "|ρ|<0.2" hypothesis holds per leg.
    """
    a, b, c = align_returns_3(r1, r2, r3)
    is_end = pd.Timestamp(is_range[1])

    leg_blocks = {
        leg_names[0]: _leg_split_block(a, is_range, oos_range, stress_range),
        leg_names[1]: _leg_split_block(b, is_range, oos_range, stress_range),
        leg_names[2]: _leg_split_block(c, is_range, oos_range, stress_range),
    }
    oos_sharpes = {
        leg_names[i]: leg_blocks[leg_names[i]]["oos"]["sharpe"]
        for i in range(3)
    }
    baseline_leg = max(oos_sharpes, key=lambda k: oos_sharpes[k])
    baseline_sharpe = oos_sharpes[baseline_leg]

    df_full = pd.concat(
        [a, b, c], axis=1, keys=leg_names
    ).dropna()
    corr_full = df_full.corr()
    leg_correlations = {
        f"{leg_names[0]}__{leg_names[1]}": float(
            corr_full.iloc[0, 1]
        ),
        f"{leg_names[0]}__{leg_names[2]}": float(
            corr_full.iloc[0, 2]
        ),
        f"{leg_names[1]}__{leg_names[2]}": float(
            corr_full.iloc[1, 2]
        ),
    }
    screening_pass = {
        leg_names[1]: (
            abs(leg_correlations[f"{leg_names[0]}__{leg_names[1]}"])
            < screening_corr_threshold
            and oos_sharpes[leg_names[1]] > 0
        ),
        leg_names[2]: (
            abs(leg_correlations[f"{leg_names[0]}__{leg_names[2]}"])
            < screening_corr_threshold
            and oos_sharpes[leg_names[2]] > 0
        ),
    }

    blends_raw: list[tuple[str, pd.Series]] = [
        ("equal_weight_3", blend_equal_weight_3(a, b, c)),
        ("ivp_static_3", blend_ivp_static_3(a, b, c, is_end)),
        ("hrp_3", blend_hrp_3(a, b, c, is_end)),
    ]

    n_trials = len(blends_raw)
    evaluations: list[BlendEvaluation3] = []
    for name, series in blends_raw:
        is_m = compute_split_metrics("IS", _slice_by_range(series, is_range))
        oos_m = compute_split_metrics(
            "OOS", _slice_by_range(series, oos_range)
        )
        st_m = compute_split_metrics(
            "Stress", _slice_by_range(series, stress_range)
        )

        wf_ratio, wf_maxdd, wf_ok = walk_forward_verdict_from_returns(
            series.dropna(),
            n_windows=wf_n_windows,
            min_profitable_ratio=wf_min_profitable_ratio,
            max_drawdown_cap=wf_max_dd_cap,
        )

        oos_vec = _slice_by_range(series, oos_range).dropna().to_numpy(float)
        dsr_p = float("nan")
        if oos_vec.size > 1 and np.std(oos_vec, ddof=1) > 0:
            try:
                dsr_p = float(dsr(oos_vec, n_trials=n_trials).p_value)
            except Exception as exc:  # pragma: no cover
                log.warning("DSR failed for %s: %s", name, exc)

        weights = series.attrs["weights"]
        dr_full = diversification_ratio_3(a, b, c, weights)
        is_a = a.loc[a.index <= is_end]
        is_b = b.loc[b.index <= is_end]
        is_c = c.loc[c.index <= is_end]
        dr_is = diversification_ratio_3(is_a, is_b, is_c, weights)

        failed: list[str] = []
        if oos_m.sharpe <= baseline_sharpe:
            failed.append(f"SHARPE_LE_BASELINE({baseline_sharpe:.3f})")
        if dr_full <= dr_threshold:
            failed.append(f"DR_LE_{dr_threshold}")
        if not (np.isfinite(dsr_p) and dsr_p < dsr_alpha):
            failed.append("DSR")
        if not wf_ok:
            failed.append("WF")
        if oos_m.sharpe <= 0:
            failed.append("OOS_SHARPE_LE_0")
        if st_m.sharpe <= 0:
            failed.append("STRESS_SHARPE_LE_0")

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
            if not (np.isfinite(lo) and lo > 0):
                failed.append("BOOTSTRAP_LO_LE_0")

        verdict = "PASS" if not failed else "FAIL"
        evaluations.append(
            BlendEvaluation3(
                name=name,
                weights=tuple(float(w) for w in weights),
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
                diversification_ratio_full=float(dr_full),
                diversification_ratio_is=float(dr_is),
                pearson_pairs_full=dict(leg_correlations),
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

    return A3dGateVerdict(
        baseline_sharpe_oos=float(baseline_sharpe),
        baseline_leg_name=baseline_leg,
        leg_metrics=leg_blocks,
        leg_correlations=leg_correlations,
        screening_pass=screening_pass,
        blends=evaluations,
        winner_blend=winner,
    )
