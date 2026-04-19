"""Allocation comparison — EW vs IVP vs HRP vs RP vs MV for 3-leg blends.

Purpose
-------
Phase 3.5b Task 7d: re-blend the three Phase 3 winner-leg daily-return
streams (LETF rotation EMA100/2x, QQQ Donchian 20/10, GLD Donchian
40/20) under five static weighting schemes and compare them on the
common-window OOS split. The mandated decision: keep EW as the
production default unless an alternative beats it on OOS Sharpe AND
Diversification Ratio simultaneously.

The five schemes
----------------

* ``equal_weight`` — naive 1/n. Immune to Σ estimation error
  [advances_fin_ml, p.298-299].
* ``ivp_static`` — Inverse-Variance Portfolio
  ``wⱼ = (1/σⱼ²) / Σ (1/σᵢ²)`` [advances_fin_ml, p.307-308].
* ``hrp`` — Hierarchical Risk Parity, López de Prado Listing 16.2
  [advances_fin_ml, p.308].
* ``risk_parity`` — Equal Risk Contribution (Maillard-Roncalli 2010
  fixed-point on IS Σ): the weights ``w`` such that
  ``wᵢ · (Σw)ᵢ = wⱼ · (Σw)ⱼ`` for all i,j. Iterative form
  ``w ← 1/(Σw)`` (re-normalise) converges to the ERC solution under
  positive-definite Σ [advances_fin_ml, p.297-298].
* ``min_variance`` — long-only minimum-variance solved via SLSQP on
  IS Σ subject to ``Σw = 1, w ≥ 0`` [advances_fin_ml, p.297-298].

All four non-EW schemes fit weights on the **IS slice only** (data
strictly before ``is_end``) so that OOS metrics never see post-IS
information — same protocol as the existing
:func:`ai_trade.backtest.grid.portfolio_3leg.blend_ivp_static_3` and
:func:`blend_hrp_3`.

Path tag: **[SWING BROKER]** — winner legs already carry BR 15%
capital-gains tax in their daily returns; this module only blends
post-tax return streams (no extra tax at the blend level).

Citations
---------
* Spec: ``specs/phase_3_5b_winners_validation.md`` §Task 7d.
* Maillard, Roncalli, Teïletche (2010) "On the properties of equally-
  weighted risk contributions portfolios", JPM 36(4), 60-70.
* López de Prado (2018) ``[advances_fin_ml, p.297-313]``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np
import pandas as pd

from ai_trade.backtest.grid.portfolio_3leg import (
    align_returns_3,
    blend_equal_weight_3,
    blend_hrp_3,
    blend_ivp_static_3,
    diversification_ratio_3,
)
from ai_trade.backtest.metrics._fmt import _fmt_num, _fmt_pct
from ai_trade.backtest.metrics.performance import (
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    returns_from_equity,
    sharpe as _sharpe,
    volatility as _volatility,
)

__all__ = [
    "AllocationRow",
    "AllocationComparison",
    "blend_min_variance_3",
    "blend_risk_parity_3",
    "compare_allocations_3",
    "erc_weights",
    "min_variance_weights",
    "render_allocation_comparison_markdown",
    "select_default_allocation",
]


# ---------------------------------------------------------------------------
# Optimisers
# ---------------------------------------------------------------------------


def erc_weights(
    cov: np.ndarray,
    *,
    max_iter: int = 500,
    ftol: float = 1e-14,
) -> np.ndarray:
    """Equal Risk Contribution weights via the convex log-barrier program.

    Solves the unconstrained convex problem ``min ½ wᵀΣw − (1/n) Σᵢ log wᵢ``
    over ``wᵢ > 0`` and normalises the optimum to sum to one. KKT
    stationarity ``Σw − (1/n)/w = 0`` yields ``w_i (Σw)_i = 1/n``, i.e.
    the ERC condition ``w_i (Σw)_i = const ∀ i, j``. Equivalent
    formulation in [Maillard-Roncalli 2010]; convex form per Spinu
    (2013) and Bourgeron et al. (2018).

    The naive fixed-point ``w ← 1/(Σw)`` is known to **oscillate** for
    diagonal Σ (it flips between EW and IVP each iteration), so we
    rely on L-BFGS-B with the log barrier instead.

    Parameters
    ----------
    cov : np.ndarray
        ``n×n`` symmetric positive-definite covariance matrix.
    max_iter, ftol : optimiser knobs.

    Raises
    ------
    ValueError
        If ``cov`` is not square, has a non-positive diagonal, or the
        optimiser fails to converge.
    """
    from scipy.optimize import minimize

    cov = np.asarray(cov, dtype=float)
    if cov.ndim != 2 or cov.shape[0] != cov.shape[1]:
        raise ValueError(f"cov must be a square 2D matrix, got shape {cov.shape}")
    n = cov.shape[0]
    if n == 0:
        raise ValueError("cov must have at least one row/column")
    if np.any(np.diag(cov) <= 0):
        raise ValueError("cov has non-positive diagonal — degenerate vol")

    inv_n = 1.0 / n

    def objective(w: np.ndarray) -> float:
        return 0.5 * float(w @ cov @ w) - inv_n * float(np.sum(np.log(w)))

    def gradient(w: np.ndarray) -> np.ndarray:
        return cov @ w - inv_n / w

    # Initialise at inverse-vol (a common warm start for ERC) so that
    # the optimiser starts near the typical solution shape.
    sigmas = np.sqrt(np.diag(cov))
    w0 = (1.0 / sigmas) / float(np.sum(1.0 / sigmas))
    res = minimize(
        objective,
        w0,
        jac=gradient,
        method="L-BFGS-B",
        bounds=[(1e-12, None)] * n,
        options={"ftol": ftol, "maxiter": max_iter, "gtol": 1e-12},
    )
    if not res.success:
        raise ValueError(f"ERC log-barrier solver failed: {res.message}")
    w = np.asarray(res.x, dtype=float)
    total = float(w.sum())
    if total <= 0 or not np.isfinite(total):
        raise ValueError("ERC weights summed to non-positive")
    return w / total


def min_variance_weights(
    cov: np.ndarray,
    *,
    max_iter: int = 200,
    ftol: float = 1e-12,
) -> np.ndarray:
    """Long-only minimum-variance weights via SLSQP.

    Solves ``min wᵀΣw  s.t.  Σwᵢ = 1, 0 ≤ wᵢ ≤ 1``. SLSQP is the
    standard scipy quadratic-with-bounds choice.

    Parameters
    ----------
    cov : np.ndarray
        Symmetric PSD covariance matrix (``n×n``).
    max_iter, ftol : optimiser knobs.

    Raises
    ------
    ValueError
        If the optimiser fails to converge.
    """
    from scipy.optimize import minimize

    cov = np.asarray(cov, dtype=float)
    if cov.ndim != 2 or cov.shape[0] != cov.shape[1]:
        raise ValueError(f"cov must be a square 2D matrix, got shape {cov.shape}")
    n = cov.shape[0]
    if n == 0:
        raise ValueError("cov must have at least one row/column")

    w0 = np.ones(n) / n
    cons = ({"type": "eq", "fun": lambda w: float(np.sum(w) - 1.0)},)
    bounds = tuple((0.0, 1.0) for _ in range(n))
    res = minimize(
        lambda w: float(w @ cov @ w),
        w0,
        method="SLSQP",
        constraints=cons,
        bounds=bounds,
        options={"ftol": ftol, "maxiter": max_iter, "disp": False},
    )
    if not res.success:
        raise ValueError(f"min-variance SLSQP failed: {res.message}")
    w = np.asarray(res.x, dtype=float)
    total = float(w.sum())
    if total <= 0 or not np.isfinite(total):
        raise ValueError("min-variance weights summed to non-positive")
    return w / total


# ---------------------------------------------------------------------------
# Blenders
# ---------------------------------------------------------------------------


def blend_risk_parity_3(
    r1: pd.Series, r2: pd.Series, r3: pd.Series, is_end: pd.Timestamp
) -> pd.Series:
    """ERC blend for 3 legs — IS-only Σ, applied forward to full window.

    Mirrors the contract of
    :func:`ai_trade.backtest.grid.portfolio_3leg.blend_ivp_static_3`:
    the returned Series carries ``attrs['weights']`` and a descriptive
    ``name``.
    """
    a, b, c = align_returns_3(r1, r2, r3)
    is_mask = a.index <= is_end
    df_is = pd.concat(
        [a.loc[is_mask], b.loc[is_mask], c.loc[is_mask]], axis=1
    ).dropna()
    if df_is.shape[0] < 2:
        raise ValueError("IS slice too small for risk-parity (< 2 bars)")
    cov = df_is.cov().to_numpy()
    if np.any(~np.isfinite(cov)):
        raise ValueError("non-finite cov in IS slice — cannot fit ERC")
    w = erc_weights(cov)
    w1, w2, w3 = float(w[0]), float(w[1]), float(w[2])
    blended = w1 * a + w2 * b + w3 * c
    blended.name = f"risk_parity_3(w={w1:.3f},{w2:.3f},{w3:.3f})"
    blended.attrs["weights"] = (w1, w2, w3)
    return blended


def blend_min_variance_3(
    r1: pd.Series, r2: pd.Series, r3: pd.Series, is_end: pd.Timestamp
) -> pd.Series:
    """Long-only Min-Variance blend for 3 legs — IS-only Σ.

    Same contract as :func:`blend_risk_parity_3`.
    """
    a, b, c = align_returns_3(r1, r2, r3)
    is_mask = a.index <= is_end
    df_is = pd.concat(
        [a.loc[is_mask], b.loc[is_mask], c.loc[is_mask]], axis=1
    ).dropna()
    if df_is.shape[0] < 2:
        raise ValueError("IS slice too small for min-variance (< 2 bars)")
    cov = df_is.cov().to_numpy()
    if np.any(~np.isfinite(cov)):
        raise ValueError("non-finite cov in IS slice — cannot fit MV")
    w = min_variance_weights(cov)
    w1, w2, w3 = float(w[0]), float(w[1]), float(w[2])
    blended = w1 * a + w2 * b + w3 * c
    blended.name = f"min_variance_3(w={w1:.3f},{w2:.3f},{w3:.3f})"
    blended.attrs["weights"] = (w1, w2, w3)
    return blended


# ---------------------------------------------------------------------------
# Row + comparison
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AllocationRow:
    """Per-method full-window + IS/OOS metrics."""

    method: str
    weights: tuple[float, float, float]
    bars: int
    full_sharpe: float
    full_cagr_pct: float
    full_volatility_ann_pct: float
    full_max_drawdown_pct: float
    is_sharpe: float
    oos_sharpe: float
    diversification_ratio: float
    final_equity: float

    def to_dict(self) -> dict:
        return {
            "method": self.method,
            "weights": list(self.weights),
            "bars": int(self.bars),
            "full_sharpe": float(self.full_sharpe),
            "full_cagr_pct": float(self.full_cagr_pct),
            "full_volatility_ann_pct": float(self.full_volatility_ann_pct),
            "full_max_drawdown_pct": float(self.full_max_drawdown_pct),
            "is_sharpe": float(self.is_sharpe),
            "oos_sharpe": float(self.oos_sharpe),
            "diversification_ratio": float(self.diversification_ratio),
            "final_equity": float(self.final_equity),
        }


@dataclass(frozen=True)
class AllocationComparison:
    """Full Task 7d verdict — all 5 methods + the recommended default."""

    leg_names: tuple[str, str, str]
    is_end: pd.Timestamp
    rows: tuple[AllocationRow, ...]
    default_method: str
    rationale: str

    def to_dict(self) -> dict:
        return {
            "leg_names": list(self.leg_names),
            "is_end": str(self.is_end.date()),
            "default_method": self.default_method,
            "rationale": self.rationale,
            "rows": [r.to_dict() for r in self.rows],
        }


def _row_from_blend(
    method: str,
    blended: pd.Series,
    legs: tuple[pd.Series, pd.Series, pd.Series],
    is_end: pd.Timestamp,
) -> AllocationRow:
    """Build an :class:`AllocationRow` from a blended returns Series."""
    weights = blended.attrs["weights"]
    series = blended.dropna()
    eq = (1.0 + series).cumprod()
    is_mask = series.index <= is_end
    is_slice = series.loc[is_mask]
    oos_slice = series.loc[~is_mask]

    return AllocationRow(
        method=method,
        weights=(float(weights[0]), float(weights[1]), float(weights[2])),
        bars=int(len(series)),
        full_sharpe=_sharpe(series),
        full_cagr_pct=_cagr(eq),
        full_volatility_ann_pct=_volatility(series),
        full_max_drawdown_pct=_max_drawdown(eq),
        is_sharpe=_sharpe(is_slice) if len(is_slice) > 1 else 0.0,
        oos_sharpe=_sharpe(oos_slice) if len(oos_slice) > 1 else 0.0,
        diversification_ratio=diversification_ratio_3(
            legs[0], legs[1], legs[2], tuple(weights)
        ),
        final_equity=float(eq.iloc[-1]),
    )


def compare_allocations_3(
    r1: pd.Series,
    r2: pd.Series,
    r3: pd.Series,
    *,
    is_end: pd.Timestamp,
    leg_names: tuple[str, str, str],
) -> AllocationComparison:
    """Run all 5 weighting methods and emit a comparable verdict.

    Returns rows in fixed order: EW, IVP, HRP, RP, MV. The ``default_method``
    is selected via :func:`select_default_allocation`.
    """
    a, b, c = align_returns_3(r1, r2, r3)
    legs = (a, b, c)

    blends: list[tuple[str, pd.Series]] = [
        ("equal_weight", blend_equal_weight_3(a, b, c)),
        ("ivp_static", blend_ivp_static_3(a, b, c, is_end)),
        ("hrp", blend_hrp_3(a, b, c, is_end)),
        ("risk_parity", blend_risk_parity_3(a, b, c, is_end)),
        ("min_variance", blend_min_variance_3(a, b, c, is_end)),
    ]

    rows = tuple(
        _row_from_blend(name, blended, legs, is_end) for name, blended in blends
    )
    default_method, rationale = select_default_allocation(rows)
    return AllocationComparison(
        leg_names=leg_names,
        is_end=pd.Timestamp(is_end),
        rows=rows,
        default_method=default_method,
        rationale=rationale,
    )


def select_default_allocation(
    rows: Sequence[AllocationRow],
    *,
    incumbent: str = "equal_weight",
    sharpe_margin: float = 0.05,
    dr_margin: float = 0.05,
) -> tuple[str, str]:
    """Decide which method to recommend as the production default.

    Rule (Phase 3.5b §Task 7d):
      EW remains default unless **another method beats it on BOTH**
      OOS Sharpe (by ≥ ``sharpe_margin``) **AND** Diversification Ratio
      (by ≥ ``dr_margin``). The double-margin rule guards against
      cosmetic gains that vanish under estimation noise — see
      [advances_fin_ml, p.298-299] on why naive 1/n is the right
      Bayesian prior absent strong evidence.

    Returns
    -------
    (method_name, human_rationale)
    """
    by_method = {r.method: r for r in rows}
    if incumbent not in by_method:
        raise ValueError(f"incumbent '{incumbent}' not in rows")
    inc = by_method[incumbent]
    challengers = [r for r in rows if r.method != incumbent]

    winners = [
        r
        for r in challengers
        if r.oos_sharpe >= inc.oos_sharpe + sharpe_margin
        and r.diversification_ratio >= inc.diversification_ratio + dr_margin
    ]
    if not winners:
        return (
            incumbent,
            (
                f"EW kept (OOS Sharpe={inc.oos_sharpe:.3f}, DR="
                f"{inc.diversification_ratio:.3f}); no challenger improves "
                f"BOTH OOS Sharpe by ≥{sharpe_margin:+.2f} AND DR by "
                f"≥{dr_margin:+.2f}."
            ),
        )
    best = max(winners, key=lambda r: r.oos_sharpe)
    return (
        best.method,
        (
            f"{best.method} promoted (OOS Sharpe {best.oos_sharpe:.3f} vs "
            f"EW {inc.oos_sharpe:.3f}; DR {best.diversification_ratio:.3f} "
            f"vs EW {inc.diversification_ratio:.3f}); both margins exceeded."
        ),
    )


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _row_to_md(row: AllocationRow, leg_names: tuple[str, str, str]) -> str:
    w = row.weights
    weights_str = (
        f"{leg_names[0]}={w[0]:.3f}, {leg_names[1]}={w[1]:.3f}, "
        f"{leg_names[2]}={w[2]:.3f}"
    )
    return (
        f"| {row.method} | {weights_str} | {row.bars} | "
        f"{_fmt_num(row.full_sharpe)} | {_fmt_pct(row.full_cagr_pct)} | "
        f"{_fmt_pct(row.full_volatility_ann_pct)} | "
        f"{_fmt_pct(row.full_max_drawdown_pct)} | "
        f"{_fmt_num(row.is_sharpe)} | {_fmt_num(row.oos_sharpe)} | "
        f"{_fmt_num(row.diversification_ratio)} | "
        f"{_fmt_num(row.final_equity)} |"
    )


def render_allocation_comparison_markdown(
    comparison: AllocationComparison,
    title: str = "Phase 3.5b Task 7d — Allocation comparison (3-leg portfolio)",
) -> str:
    """Render the full comparison + default-method block to Markdown."""
    leg_names = comparison.leg_names
    parts: list[str] = [f"# {title}", ""]
    parts.append(
        "Five weighting schemes on the LETF + QQQ + GLD common-window "
        "daily-return streams (post-tax, post-cost). All non-EW schemes "
        "fit weights on the **IS slice only** (≤ "
        f"`{comparison.is_end.date()}`); OOS metrics never see post-IS "
        "Σ. EW is the production incumbent."
    )
    parts.append("")
    cols = (
        "method",
        "weights",
        "bars",
        "Sharpe (full)",
        "CAGR (full)",
        "Vol ann (full)",
        "Max DD (full)",
        "Sharpe IS",
        "Sharpe OOS",
        "DR (full)",
        "Final equity (×)",
    )
    parts.append("| " + " | ".join(cols) + " |")
    parts.append("| " + " | ".join("---" for _ in cols) + " |")
    for row in comparison.rows:
        parts.append(_row_to_md(row, leg_names))
    parts.append("")
    parts.append("## Decision")
    parts.append("")
    parts.append(f"**Default allocation: `{comparison.default_method}`**")
    parts.append("")
    parts.append(comparison.rationale)
    parts.append("")
    parts.append(
        "Decision rule: EW is kept unless a challenger improves BOTH OOS "
        "Sharpe (≥ +0.05) and Diversification Ratio (≥ +0.05). Margins "
        "guard against estimation-noise gains [advances_fin_ml, p.298-299]."
    )
    parts.append("")
    return "\n".join(parts)
