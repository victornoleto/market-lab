"""Vol-target position sizing — ex-ante rescaling of portfolio returns.

Purpose
-------
Phase 3.5b Task 7f: rescale the 3-leg EW blended daily-return stream so
that a **rolling ex-ante volatility estimate** targets a fixed annual
vol (default 10%). Compare the rescaled stream against the baseline
(no scaling) and a grid of ``(lookback, max_leverage)`` configurations.

The production default remains baseline (1.0× EW) unless a vol-target
config beats it on BOTH OOS Sharpe AND OOS CAGR by pre-declared
margins — same double-margin discipline as Task 7d allocation
comparison, so a cosmetic gain driven by estimation noise cannot
promote a challenger.

Mechanics
---------
Let ``r_t`` be the blended daily return and ``σ̂_{t-1}`` the annualised
rolling volatility computed from the window ``r_{t-L}..r_{t-1}`` (so
**no look-ahead**: the scale applied on bar ``t`` only depends on
returns strictly before ``t``). The scaled return is::

    s_t = clip(target_vol / σ̂_{t-1}, 0, max_leverage)
    r_scaled_t = s_t · r_t

The rolling std uses ``min_periods=lookback``; the first ``lookback``
bars emit ``NaN`` scale and are dropped. Annualisation factor is
``√252``.

Citations
---------
* ``[systematic_trading_carver, p.107-111]`` — volatility standardisation:
  scale each instrument's return by target_vol / realised_vol to achieve
  a uniform risk contribution. Canonical CTA reference for vol-target.
* ``[advances_fin_ml, p.162-164]`` — position sizing from predicted
  target vs. realised variance; motivates the ``σ̂_{t-1}`` lag.
* ``[advances_fin_ml, p.298-299]`` — 1/n (i.e. *no scaling*) as the
  default Bayesian prior absent strong evidence; justifies the
  double-margin promotion rule.
* Spec: ``specs/phase_3_5b_winners_validation.md`` §Task 7f.

Path tag: **[SWING BROKER]** — operates on post-tax, post-cost
portfolio-level daily returns; no extra tax at the sizing level
(individual-leg tax already baked in).

Design notes
------------
* Pure-function layer: no simulation, no data loading. Callers pass
  the blended returns Series and a list of configs.
* When ``σ̂_{t-1} == 0`` (e.g. a run of zero returns), the scale is
  defined as ``max_leverage`` (infinite demand clipped to the cap).
  In practice this never fires on 3-leg post-cost returns over the
  common window — the default path is well-defined.
* Vol-target in backtests assumes daily rebalance at bar-close with no
  re-sizing cost. This is the standard textbook assumption — if Task
  7c slippage sensitivity continues to PASS under the chosen sizing,
  we read that as "sizing churn is immaterial at the tested levels".
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd

from market_lab.backtest.metrics._fmt import _fmt_num, _fmt_pct
from market_lab.backtest.metrics.performance import (
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
    volatility as _volatility,
)

__all__ = [
    "CANONICAL_TARGET_VOL",
    "CANONICAL_LOOKBACKS",
    "CANONICAL_MAX_LEVERAGES",
    "VolTargetConfig",
    "VolTargetRow",
    "VolTargetComparison",
    "apply_vol_target",
    "compare_vol_target_configs",
    "select_default_sizing",
    "render_vol_target_markdown",
]


# ---------------------------------------------------------------------------
# Canonical knobs
# ---------------------------------------------------------------------------

#: Annualised target vol (fraction of 1.0) mandated by Phase 3.5b §Task 7f.
CANONICAL_TARGET_VOL: float = 0.10

#: Rolling-std lookbacks to sweep (trading days).
CANONICAL_LOOKBACKS: tuple[int, ...] = (63, 126, 252)

#: Leverage caps to sweep.
CANONICAL_MAX_LEVERAGES: tuple[float, ...] = (1.5, 2.0, 3.0)


# ---------------------------------------------------------------------------
# Config dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VolTargetConfig:
    """One vol-target configuration to evaluate."""

    target_vol: float
    lookback: int
    max_leverage: float

    def label(self) -> str:
        return (
            f"vt_target={self.target_vol:.2f}_"
            f"L{int(self.lookback)}_"
            f"cap{self.max_leverage:.1f}"
        )


# ---------------------------------------------------------------------------
# Core: apply_vol_target
# ---------------------------------------------------------------------------


def apply_vol_target(
    returns: pd.Series,
    *,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    periods_per_year: int = 252,
) -> tuple[pd.Series, pd.Series]:
    """Scale ``returns`` so ex-ante vol targets ``target_vol`` annualised.

    The scale on bar ``t`` uses the rolling std over ``[t-lookback, t-1]``
    (``shift(1)`` on a window of ``lookback``, ``min_periods=lookback``).
    This guarantees **no look-ahead**: the sizing decision only sees the
    past. The first ``lookback`` bars have no valid scale and are
    dropped from the output.

    Parameters
    ----------
    returns : pd.Series
        Daily (or per-period) return stream to rescale.
    target_vol : float
        Target annualised volatility as a fraction (e.g. ``0.10`` for 10%).
        Must be positive.
    lookback : int
        Rolling-window length in bars. Must be ≥ 2.
    max_leverage : float
        Upper bound on the per-bar scale factor. Must be > 0. Scales below
        zero are clipped to 0 (vol estimates are non-negative, but the
        clip makes the contract explicit).
    periods_per_year : int
        Annualisation factor for the rolling std. Default 252.

    Returns
    -------
    (scaled_returns, scale_series)
        Both indexed on the valid bars (first ``lookback`` dropped).

    Raises
    ------
    ValueError
        If ``target_vol`` non-positive, ``lookback`` < 2, or
        ``max_leverage`` non-positive.
    """
    if target_vol <= 0:
        raise ValueError(f"target_vol must be > 0, got {target_vol}")
    if lookback < 2:
        raise ValueError(f"lookback must be ≥ 2, got {lookback}")
    if max_leverage <= 0:
        raise ValueError(f"max_leverage must be > 0, got {max_leverage}")

    r = returns.dropna().astype(float)
    if len(r) <= lookback:
        raise ValueError(
            f"need > {lookback} bars to compute a scale, got {len(r)}"
        )

    # Rolling std on past bars, then shift(1) so bar t sees [t-L..t-1].
    ann_vol = r.rolling(lookback, min_periods=lookback).std(ddof=0) * np.sqrt(
        periods_per_year
    )
    ann_vol_prev = ann_vol.shift(1)

    # Scale: target / σ̂_{t-1}, clipped to [0, max_leverage].
    # σ̂ == 0 is mapped to max_leverage (infinite demand, capped).
    raw_scale = pd.Series(index=r.index, dtype=float)
    mask_valid = ann_vol_prev.notna()
    raw_scale.loc[mask_valid & (ann_vol_prev > 0)] = (
        target_vol / ann_vol_prev.loc[mask_valid & (ann_vol_prev > 0)]
    )
    raw_scale.loc[mask_valid & (ann_vol_prev == 0)] = max_leverage

    scale = raw_scale.clip(lower=0.0, upper=max_leverage)
    scale = scale.dropna()
    scaled = (scale * r.loc[scale.index]).astype(float)
    scaled.name = returns.name
    scale.name = "scale"
    return scaled, scale


# ---------------------------------------------------------------------------
# Row + comparison
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VolTargetRow:
    """Metrics for baseline or one vol-target config."""

    label: str
    target_vol: float
    lookback: int
    max_leverage: float
    bars: int
    # Scale factor stats on valid bars.
    scale_mean: float
    scale_median: float
    scale_min: float
    scale_max: float
    scale_cap_hit_frac: float
    # Full-window metrics.
    full_sharpe: float
    full_cagr_pct: float
    full_volatility_ann_pct: float
    full_max_drawdown_pct: float
    # IS/OOS split metrics.
    is_sharpe: float
    is_cagr_pct: float
    oos_sharpe: float
    oos_cagr_pct: float
    oos_max_drawdown_pct: float
    final_equity: float

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "target_vol": float(self.target_vol),
            "lookback": int(self.lookback),
            "max_leverage": float(self.max_leverage),
            "bars": int(self.bars),
            "scale_mean": float(self.scale_mean),
            "scale_median": float(self.scale_median),
            "scale_min": float(self.scale_min),
            "scale_max": float(self.scale_max),
            "scale_cap_hit_frac": float(self.scale_cap_hit_frac),
            "full_sharpe": float(self.full_sharpe),
            "full_cagr_pct": float(self.full_cagr_pct),
            "full_volatility_ann_pct": float(self.full_volatility_ann_pct),
            "full_max_drawdown_pct": float(self.full_max_drawdown_pct),
            "is_sharpe": float(self.is_sharpe),
            "is_cagr_pct": float(self.is_cagr_pct),
            "oos_sharpe": float(self.oos_sharpe),
            "oos_cagr_pct": float(self.oos_cagr_pct),
            "oos_max_drawdown_pct": float(self.oos_max_drawdown_pct),
            "final_equity": float(self.final_equity),
        }


@dataclass(frozen=True)
class VolTargetComparison:
    """Full Task 7f verdict — baseline + grid of vol-target configs."""

    is_end: pd.Timestamp
    rows: tuple[VolTargetRow, ...]
    default_label: str
    rationale: str

    def to_dict(self) -> dict:
        return {
            "is_end": str(self.is_end.date()),
            "default_label": self.default_label,
            "rationale": self.rationale,
            "rows": [r.to_dict() for r in self.rows],
        }


def _summarise_returns(
    label: str,
    returns: pd.Series,
    scale: pd.Series | None,
    *,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    is_end: pd.Timestamp,
    periods_per_year: int = 252,
) -> VolTargetRow:
    """Build a :class:`VolTargetRow` from a returns Series (scaled or not)."""
    r = returns.dropna().astype(float)
    if len(r) < 2:
        raise ValueError(f"{label}: need ≥ 2 valid bars to summarise")

    eq = (1.0 + r).cumprod()
    is_mask = r.index <= is_end
    is_r = r.loc[is_mask]
    oos_r = r.loc[~is_mask]
    is_eq = (1.0 + is_r).cumprod()
    oos_eq = (1.0 + oos_r).cumprod()

    if scale is None:
        scale_mean = 1.0
        scale_median = 1.0
        scale_min = 1.0
        scale_max = 1.0
        scale_cap_hit_frac = 0.0
    else:
        s = scale.dropna()
        scale_mean = float(s.mean())
        scale_median = float(s.median())
        scale_min = float(s.min())
        scale_max = float(s.max())
        scale_cap_hit_frac = float(
            (np.isclose(s.to_numpy(float), max_leverage, rtol=1e-9, atol=1e-12)).mean()
        )

    return VolTargetRow(
        label=label,
        target_vol=float(target_vol),
        lookback=int(lookback),
        max_leverage=float(max_leverage),
        bars=int(len(r)),
        scale_mean=scale_mean,
        scale_median=scale_median,
        scale_min=scale_min,
        scale_max=scale_max,
        scale_cap_hit_frac=scale_cap_hit_frac,
        full_sharpe=_sharpe(r, periods_per_year=periods_per_year),
        full_cagr_pct=_cagr(eq, periods_per_year=periods_per_year),
        full_volatility_ann_pct=_volatility(r, periods_per_year=periods_per_year),
        full_max_drawdown_pct=_max_drawdown(eq),
        is_sharpe=_sharpe(is_r, periods_per_year=periods_per_year) if len(is_r) > 1 else 0.0,
        is_cagr_pct=_cagr(is_eq, periods_per_year=periods_per_year) if len(is_eq) > 1 else 0.0,
        oos_sharpe=_sharpe(oos_r, periods_per_year=periods_per_year) if len(oos_r) > 1 else 0.0,
        oos_cagr_pct=_cagr(oos_eq, periods_per_year=periods_per_year) if len(oos_eq) > 1 else 0.0,
        oos_max_drawdown_pct=_max_drawdown(oos_eq) if len(oos_eq) > 1 else 0.0,
        final_equity=float(eq.iloc[-1]),
    )


def compare_vol_target_configs(
    blended_returns: pd.Series,
    *,
    is_end: pd.Timestamp,
    configs: Sequence[VolTargetConfig] | None = None,
    periods_per_year: int = 252,
) -> VolTargetComparison:
    """Run baseline + each config and emit a comparable verdict.

    The first row is always the unscaled baseline (labelled
    ``"baseline_ew"``). Subsequent rows are one per config in the order
    supplied; if ``configs is None`` the canonical cartesian product
    ``{63,126,252} × {1.5, 2.0, 3.0}`` with ``target_vol =
    CANONICAL_TARGET_VOL`` is used.

    The default sizing is chosen via :func:`select_default_sizing`.
    """
    if configs is None:
        configs = tuple(
            VolTargetConfig(CANONICAL_TARGET_VOL, L, cap)
            for L in CANONICAL_LOOKBACKS
            for cap in CANONICAL_MAX_LEVERAGES
        )

    rows: list[VolTargetRow] = []
    baseline = _summarise_returns(
        label="baseline_ew",
        returns=blended_returns,
        scale=None,
        target_vol=CANONICAL_TARGET_VOL,
        lookback=0,
        max_leverage=1.0,
        is_end=is_end,
        periods_per_year=periods_per_year,
    )
    rows.append(baseline)

    for cfg in configs:
        scaled, scale = apply_vol_target(
            blended_returns,
            target_vol=cfg.target_vol,
            lookback=cfg.lookback,
            max_leverage=cfg.max_leverage,
            periods_per_year=periods_per_year,
        )
        rows.append(
            _summarise_returns(
                label=cfg.label(),
                returns=scaled,
                scale=scale,
                target_vol=cfg.target_vol,
                lookback=cfg.lookback,
                max_leverage=cfg.max_leverage,
                is_end=is_end,
                periods_per_year=periods_per_year,
            )
        )

    default_label, rationale = select_default_sizing(tuple(rows))
    return VolTargetComparison(
        is_end=pd.Timestamp(is_end),
        rows=tuple(rows),
        default_label=default_label,
        rationale=rationale,
    )


def select_default_sizing(
    rows: Sequence[VolTargetRow],
    *,
    incumbent: str = "baseline_ew",
    sharpe_margin: float = 0.05,
    cagr_margin_pct: float = 1.0,
) -> tuple[str, str]:
    """Decide which sizing to recommend as the production default.

    Rule (Phase 3.5b §Task 7f):
      Baseline (1/3/1/3/1/3 EW, no scaling) stays default unless a
      vol-target config beats it on BOTH **OOS Sharpe** by ≥
      ``sharpe_margin`` AND **OOS CAGR (pp)** by ≥ ``cagr_margin_pct``.
      Double-margin guards against estimation-noise gains; see
      ``[advances_fin_ml, p.298-299]``.
    """
    by_label = {r.label: r for r in rows}
    if incumbent not in by_label:
        raise ValueError(f"incumbent '{incumbent}' not in rows")
    inc = by_label[incumbent]
    challengers = [r for r in rows if r.label != incumbent]

    winners = [
        r
        for r in challengers
        if r.oos_sharpe >= inc.oos_sharpe + sharpe_margin
        and r.oos_cagr_pct >= inc.oos_cagr_pct + cagr_margin_pct
    ]
    if not winners:
        return (
            incumbent,
            (
                f"baseline_ew kept (OOS Sharpe={inc.oos_sharpe:.3f}, "
                f"OOS CAGR={inc.oos_cagr_pct:.2%}); no vol-target config "
                f"improves BOTH OOS Sharpe by ≥{sharpe_margin:+.2f} AND "
                f"OOS CAGR by ≥{cagr_margin_pct:+.2f}pp."
            ),
        )
    best = max(winners, key=lambda r: r.oos_sharpe)
    return (
        best.label,
        (
            f"{best.label} promoted (OOS Sharpe {best.oos_sharpe:.3f} vs "
            f"baseline {inc.oos_sharpe:.3f}; OOS CAGR "
            f"{best.oos_cagr_pct:.2%} vs baseline {inc.oos_cagr_pct:.2%}); "
            f"both margins exceeded."
        ),
    )


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _row_to_md(row: VolTargetRow) -> str:
    return (
        f"| {row.label} | "
        f"{_fmt_num(row.target_vol)} | "
        f"{row.lookback} | "
        f"{_fmt_num(row.max_leverage)} | "
        f"{row.bars} | "
        f"{_fmt_num(row.scale_mean)} | "
        f"{_fmt_num(row.scale_median)} | "
        f"{_fmt_pct(row.scale_cap_hit_frac)} | "
        f"{_fmt_num(row.full_sharpe)} | "
        f"{_fmt_pct(row.full_cagr_pct)} | "
        f"{_fmt_pct(row.full_volatility_ann_pct)} | "
        f"{_fmt_pct(row.full_max_drawdown_pct)} | "
        f"{_fmt_num(row.is_sharpe)} | "
        f"{_fmt_num(row.oos_sharpe)} | "
        f"{_fmt_pct(row.oos_cagr_pct)} | "
        f"{_fmt_pct(row.oos_max_drawdown_pct)} | "
        f"{_fmt_num(row.final_equity)} |"
    )


def render_vol_target_markdown(
    comparison: VolTargetComparison,
    title: str = "Phase 3.5b Task 7f — Vol-target sizing (3-leg EW portfolio)",
) -> str:
    """Render the full vol-target sweep + default-sizing block to Markdown."""
    parts: list[str] = [f"# {title}", ""]
    parts.append(
        "Ex-ante vol-target rescaling applied to the EW 3-leg blended "
        "daily-return stream (post-tax, post-cost). The scale on bar `t` "
        "uses the lagged rolling std over `[t-L, t-1]` and is clipped to "
        "`[0, cap]`. Baseline is the unscaled EW blend. "
        "Decision rule: baseline remains default unless a challenger "
        "improves BOTH OOS Sharpe (≥ +0.05) AND OOS CAGR (≥ +1.0 pp). "
        "Reference: `[systematic_trading_carver, p.107-111]`, "
        "`[advances_fin_ml, p.162-164, 298-299]`."
    )
    parts.append("")
    cols = (
        "config",
        "target_vol",
        "L",
        "cap",
        "bars",
        "scale_mean",
        "scale_median",
        "cap_hit%",
        "Sharpe (full)",
        "CAGR (full)",
        "Vol ann (full)",
        "MaxDD (full)",
        "Sharpe IS",
        "Sharpe OOS",
        "CAGR OOS",
        "MaxDD OOS",
        "Final equity (×)",
    )
    parts.append("| " + " | ".join(cols) + " |")
    parts.append("| " + " | ".join("---" for _ in cols) + " |")
    for row in comparison.rows:
        parts.append(_row_to_md(row))
    parts.append("")
    parts.append("## Decision")
    parts.append("")
    parts.append(f"**Default sizing: `{comparison.default_label}`**")
    parts.append("")
    parts.append(comparison.rationale)
    parts.append("")
    parts.append(
        "Decision rule: baseline EW is kept unless a challenger improves "
        "BOTH OOS Sharpe (≥ +0.05) and OOS CAGR (≥ +1.0 pp). Margins "
        "guard against estimation-noise gains "
        "`[advances_fin_ml, p.298-299]`."
    )
    parts.append("")
    return "\n".join(parts)
