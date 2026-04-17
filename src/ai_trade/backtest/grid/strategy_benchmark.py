"""Phase 3 Lead B2 — cross-strategy benchmark helpers [SWING BROKER].

Decide whether two gate-passing Path-B strategies should coexist
(risk-parity blend), operate as independent lanes, or whether one
should replace the other.

Applied to the Phase 3 winners:

* **LETF rotation** (Lead B1c winner — EMA100 band=0 lev=2x on
  synthetic SPX TR): canonical Gayed LRS with BR 15% tax on RISK_ON
  exits already baked into :class:`LETFRotationConfig` (default
  ``tax_rate=0.15``).
* **ETFRotation top-1** (Lead Phase A winner — Clenow monthly
  momentum on SPY/QQQ/IWM/GLD/TLT).

All helpers operate on **daily net-of-cost return series** — so the
call-site must already have applied fees, swap/tax, and leverage.
The module is deliberately framework-agnostic (no bar engine, no
Tiingo) to keep the test surface tight.

Metrics
-------

* Pearson / Spearman correlation on the aligned daily returns.
* Rolling 252-day Pearson correlation (stability → the decision is
  only useful if the correlation regime is stable).
* Annualized Sharpe, CAGR, Max-DD, MAR = CAGR / |MaxDD|.
* Inverse-volatility risk-parity weights and the blended Sharpe /
  CAGR / MaxDD / MAR.
* Diversification ratio `D = w·σ / σ_port` (Choueifaty-Coignard 2008)
  — D > 1 ⇒ the blend improves risk-adjusted performance beyond a
  naive combination.

Decision rules
--------------

* ``REPLACE``  if ``|corr| >= 0.7`` AND ``|sharpe_a - sharpe_b| >=
  dominance_threshold``: the strategies track the same edge and one
  dominates.
* ``COEXIST``  if ``|corr| <= corr_coexist`` AND ``blend.sharpe >=
  max(sharpe_a, sharpe_b) * blend_lift`` AND ``D >= 1.1``: blend
  materially improves both absolute and risk-adjusted return.
* ``INDEPENDENT_LANES`` otherwise: keep both as separate sleeves at
  the portfolio level but do not auto-blend.

Thresholds are conservative defaults; override them in the driver
when the investment mandate calls for a stricter rule.

Citations
---------

* Sharpe annualization / `ddof=1` convention: ``[advances_fin_ml,
  p.196-202]``.
* Clenow monthly rotation (`stocks_on_the_move, p.81, ch.4`) supplies
  the ETFRotation returns.
* Gayed LRS + leverage drag formula: ``[leverage_for_the_long_run,
  p.13, p.16]``.
* Diversification ratio and inverse-vol portfolios: Choueifaty &
  Coignard (2008) — matches the ``ai_trade`` risk-parity convention
  used in :class:`ETFRotationStrategy._vol_scale`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

import numpy as np
import pandas as pd


__all__ = [
    "TRADING_DAYS",
    "BlendResult",
    "BenchmarkVerdict",
    "align_returns",
    "sharpe_from_returns",
    "cagr_from_returns",
    "max_drawdown_from_returns",
    "mar_from_returns",
    "inverse_vol_weights",
    "diversification_ratio",
    "rolling_correlation",
    "compute_blend",
    "decide_blend_vs_replace",
    "run_benchmark",
]


TRADING_DAYS = 252
"""Trading days per year for daily-frequency annualization."""


@dataclass(frozen=True)
class BlendResult:
    """Blended portfolio of two (or more) return streams."""

    weights: dict[str, float]
    daily_returns: pd.Series
    sharpe: float
    cagr: float
    max_drawdown: float
    mar: float
    diversification_ratio: float

    def to_dict(self) -> dict:
        return {
            "weights": dict(self.weights),
            "sharpe": self.sharpe,
            "cagr": self.cagr,
            "max_drawdown": self.max_drawdown,
            "mar": self.mar,
            "diversification_ratio": self.diversification_ratio,
        }


@dataclass(frozen=True)
class BenchmarkVerdict:
    """Full benchmark result including decision."""

    strat_a: str
    strat_b: str
    window_start: pd.Timestamp
    window_end: pd.Timestamp
    n_bars: int
    pearson: float
    spearman: float
    rolling_corr_min: float
    rolling_corr_max: float
    rolling_corr_median: float
    sharpe_a: float
    sharpe_b: float
    cagr_a: float
    cagr_b: float
    mar_a: float
    mar_b: float
    max_dd_a: float
    max_dd_b: float
    blend: BlendResult
    decision: str
    decision_reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "strat_a": self.strat_a,
            "strat_b": self.strat_b,
            "window_start": str(self.window_start.date()),
            "window_end": str(self.window_end.date()),
            "n_bars": self.n_bars,
            "pearson": self.pearson,
            "spearman": self.spearman,
            "rolling_corr": {
                "min": self.rolling_corr_min,
                "max": self.rolling_corr_max,
                "median": self.rolling_corr_median,
            },
            "a": {
                "sharpe": self.sharpe_a,
                "cagr": self.cagr_a,
                "max_drawdown": self.max_dd_a,
                "mar": self.mar_a,
            },
            "b": {
                "sharpe": self.sharpe_b,
                "cagr": self.cagr_b,
                "max_drawdown": self.max_dd_b,
                "mar": self.mar_b,
            },
            "blend": self.blend.to_dict(),
            "decision": self.decision,
            "decision_reasons": list(self.decision_reasons),
        }


def align_returns(returns: Mapping[str, pd.Series]) -> pd.DataFrame:
    """Inner-join return series by date; drop any row with NaN.

    Raises ``ValueError`` if the aligned frame has fewer than 60 rows
    (too little overlap to compute meaningful statistics).
    """
    if not returns:
        raise ValueError("returns mapping must be non-empty")
    df = pd.DataFrame(returns).dropna(how="any")
    if len(df) < 60:
        raise ValueError(
            f"too few overlapping bars ({len(df)}) after alignment"
        )
    return df


def sharpe_from_returns(
    rets: pd.Series, periods_per_year: int = TRADING_DAYS
) -> float:
    """Annualized Sharpe on a daily-return series (ddof=1, zero vol → 0)."""
    r = rets.dropna().astype(float)
    if len(r) < 2:
        return 0.0
    std = float(r.std(ddof=1))
    if std == 0.0:
        return 0.0
    return float(r.mean() / std * np.sqrt(periods_per_year))


def cagr_from_returns(
    rets: pd.Series, periods_per_year: int = TRADING_DAYS
) -> float:
    """Compound annual growth rate from daily returns."""
    r = rets.dropna().astype(float)
    if len(r) < 2:
        return 0.0
    equity = (1.0 + r).cumprod()
    years = len(r) / periods_per_year
    total = float(equity.iloc[-1])
    if years <= 0 or total <= 0:
        return -1.0
    return total ** (1.0 / years) - 1.0


def max_drawdown_from_returns(rets: pd.Series) -> float:
    """Max drawdown as a non-positive fraction (e.g. -0.35 = -35%)."""
    r = rets.dropna().astype(float)
    if r.empty:
        return 0.0
    equity = (1.0 + r).cumprod()
    peak = equity.cummax()
    return float((equity / peak - 1.0).min())


def mar_from_returns(rets: pd.Series) -> float:
    """MAR ratio = CAGR / |MaxDD|. Zero DD → +inf (or 0 if CAGR == 0)."""
    cagr = cagr_from_returns(rets)
    mdd = max_drawdown_from_returns(rets)
    if mdd == 0.0:
        return float("inf") if cagr > 0 else 0.0
    return cagr / abs(mdd)


def inverse_vol_weights(
    returns_df: pd.DataFrame, vol_window: int | None = None
) -> pd.Series:
    """Inverse-volatility weights (``w_i = (1/σ_i) / Σ (1/σ_j)``).

    If ``vol_window`` is given, vol is estimated on the trailing
    window only. Zero-vol legs receive weight 0 and the remainder is
    renormalized.
    """
    source = (
        returns_df.tail(vol_window) if vol_window else returns_df
    ).astype(float)
    vols = source.std(ddof=1)
    with np.errstate(divide="ignore"):
        inv = np.where(vols > 0, 1.0 / vols, 0.0)
    total = float(inv.sum())
    if total == 0.0:
        raise ValueError("all strategies have zero volatility — cannot blend")
    return pd.Series(inv / total, index=returns_df.columns, name="weight")


def diversification_ratio(
    returns_df: pd.DataFrame, weights: pd.Series
) -> float:
    """Choueifaty-Coignard diversification ratio = (w·σ) / σ_port.

    D=1 ⇒ perfect correlation (no diversification benefit); D>1 ⇒
    blend lowers portfolio vol below the weighted-average leg vol.
    """
    df = returns_df.astype(float)
    w = weights.reindex(df.columns).astype(float)
    vols = df.std(ddof=1)
    weighted_avg_vol = float((w * vols).sum())
    port = (df * w).sum(axis=1)
    port_vol = float(port.std(ddof=1))
    if port_vol == 0.0:
        return float("inf") if weighted_avg_vol > 0 else 1.0
    return weighted_avg_vol / port_vol


def rolling_correlation(
    a: pd.Series, b: pd.Series, window: int = TRADING_DAYS
) -> pd.Series:
    """Rolling Pearson correlation between two daily-return series."""
    return a.rolling(window).corr(b)


def compute_blend(
    returns_df: pd.DataFrame, weights: pd.Series | None = None
) -> BlendResult:
    """Risk-parity (inverse-vol) blend with full downstream metrics."""
    df = returns_df.astype(float)
    w = inverse_vol_weights(df) if weights is None else weights.astype(float)
    w = w / w.sum()
    daily = (df * w).sum(axis=1)
    cagr = cagr_from_returns(daily)
    mdd = max_drawdown_from_returns(daily)
    mar = float("inf") if mdd == 0.0 else cagr / abs(mdd)
    return BlendResult(
        weights=w.to_dict(),
        daily_returns=daily,
        sharpe=sharpe_from_returns(daily),
        cagr=cagr,
        max_drawdown=mdd,
        mar=mar,
        diversification_ratio=diversification_ratio(df, w),
    )


def decide_blend_vs_replace(
    pearson: float,
    sharpe_a: float,
    sharpe_b: float,
    blend_sharpe: float,
    diversification: float,
    *,
    mar_a: float | None = None,
    mar_b: float | None = None,
    max_dd_a: float | None = None,
    max_dd_b: float | None = None,
    corr_replace: float = 0.7,
    corr_coexist: float = 0.35,
    dominance_threshold: float = 0.3,
    blend_lift: float = 1.0,
    diversification_coexist: float = 1.1,
) -> tuple[str, list[str]]:
    """Classify the relationship between two strategies.

    Returns ``(decision, reasons)`` where ``decision`` is one of
    ``REPLACE_A_WITH_B``, ``REPLACE_B_WITH_A``, ``COEXIST``, or
    ``INDEPENDENT_LANES`` and ``reasons`` enumerates the criteria
    that fired.

    Rule order (first hit wins):

    1. **Strict dominance + blend disadvantage** — if one leg has
       Sharpe, MAR, and a shallower MaxDD than the other, AND the
       risk-parity blend's Sharpe is < the dominant leg's Sharpe,
       recommend REPLACE regardless of correlation. The optional
       ``mar_*`` / ``max_dd_*`` arguments enable this check; when
       omitted, the rule is skipped.
    2. **Correlated replace** — ``|corr| >= corr_replace`` AND
       ``|Δsharpe| >= dominance_threshold``: dominant leg wins.
    3. **Coexist** — low correlation, blend-Sharpe lift, and strong
       diversification ratio.
    4. **Independent lanes** — otherwise.
    """
    reasons: list[str] = []
    dominance = abs(sharpe_b - sharpe_a)

    if (
        mar_a is not None and mar_b is not None
        and max_dd_a is not None and max_dd_b is not None
    ):
        # NB: max_dd is a non-positive fraction — "shallower" means closer to 0.
        best_single = max(sharpe_a, sharpe_b)
        a_dominates = (
            sharpe_a > sharpe_b
            and mar_a > mar_b
            and max_dd_a > max_dd_b
        )
        b_dominates = (
            sharpe_b > sharpe_a
            and mar_b > mar_a
            and max_dd_b > max_dd_a
        )
        blend_underperforms = blend_sharpe < best_single
        if (a_dominates or b_dominates) and blend_underperforms:
            winner = "A" if a_dominates else "B"
            reasons.append(
                f"strict dominance: leg {winner} beats on Sharpe/MAR/MaxDD "
                f"AND blend_sharpe={blend_sharpe:.3f}<max_single={best_single:.3f}"
            )
            return (
                "REPLACE_B_WITH_A" if winner == "A" else "REPLACE_A_WITH_B",
                reasons,
            )

    if abs(pearson) >= corr_replace and dominance >= dominance_threshold:
        winner = "B" if sharpe_b > sharpe_a else "A"
        reasons.append(
            f"|corr|={abs(pearson):.2f}>={corr_replace} AND "
            f"|Δsharpe|={dominance:.2f}>={dominance_threshold} → dominant leg wins"
        )
        return (
            "REPLACE_A_WITH_B" if winner == "B" else "REPLACE_B_WITH_A",
            reasons,
        )

    best_single = max(sharpe_a, sharpe_b)
    lift_pass = blend_sharpe >= best_single * blend_lift
    corr_pass = abs(pearson) <= corr_coexist
    div_pass = diversification >= diversification_coexist

    if corr_pass and lift_pass and div_pass:
        reasons.append(
            f"|corr|={abs(pearson):.2f}<={corr_coexist} AND "
            f"blend_sharpe={blend_sharpe:.3f}>=max_single*{blend_lift:.2f} AND "
            f"D={diversification:.2f}>={diversification_coexist}"
        )
        return "COEXIST", reasons

    if not corr_pass:
        reasons.append(f"|corr|={abs(pearson):.2f}>{corr_coexist} (not low)")
    if not lift_pass:
        reasons.append(
            f"blend_sharpe={blend_sharpe:.3f}<max_single*{blend_lift:.2f}="
            f"{best_single * blend_lift:.3f}"
        )
    if not div_pass:
        reasons.append(
            f"D={diversification:.2f}<{diversification_coexist}"
        )
    return "INDEPENDENT_LANES", reasons


def run_benchmark(
    strat_a_name: str,
    strat_a_returns: pd.Series,
    strat_b_name: str,
    strat_b_returns: pd.Series,
    *,
    rolling_window: int = TRADING_DAYS,
    **decision_kwargs,
) -> BenchmarkVerdict:
    """End-to-end benchmark: align, compute all metrics, decide."""
    if strat_a_name == strat_b_name:
        raise ValueError("strat_a_name and strat_b_name must differ")

    df = align_returns(
        {strat_a_name: strat_a_returns, strat_b_name: strat_b_returns}
    )
    a = df[strat_a_name]
    b = df[strat_b_name]

    pearson = float(a.corr(b, method="pearson"))
    spearman = float(a.corr(b, method="spearman"))

    roll = rolling_correlation(a, b, window=rolling_window).dropna()
    if roll.empty:
        rc_min = rc_max = rc_median = float("nan")
    else:
        rc_min = float(roll.min())
        rc_max = float(roll.max())
        rc_median = float(roll.median())

    sharpe_a = sharpe_from_returns(a)
    sharpe_b = sharpe_from_returns(b)
    cagr_a = cagr_from_returns(a)
    cagr_b = cagr_from_returns(b)
    mdd_a = max_drawdown_from_returns(a)
    mdd_b = max_drawdown_from_returns(b)
    mar_a = float("inf") if mdd_a == 0.0 else cagr_a / abs(mdd_a)
    mar_b = float("inf") if mdd_b == 0.0 else cagr_b / abs(mdd_b)

    blend = compute_blend(df)
    decision, reasons = decide_blend_vs_replace(
        pearson,
        sharpe_a,
        sharpe_b,
        blend.sharpe,
        blend.diversification_ratio,
        mar_a=mar_a,
        mar_b=mar_b,
        max_dd_a=mdd_a,
        max_dd_b=mdd_b,
        **decision_kwargs,
    )

    return BenchmarkVerdict(
        strat_a=strat_a_name,
        strat_b=strat_b_name,
        window_start=df.index[0],
        window_end=df.index[-1],
        n_bars=len(df),
        pearson=pearson,
        spearman=spearman,
        rolling_corr_min=rc_min,
        rolling_corr_max=rc_max,
        rolling_corr_median=rc_median,
        sharpe_a=sharpe_a,
        sharpe_b=sharpe_b,
        cagr_a=cagr_a,
        cagr_b=cagr_b,
        mar_a=mar_a,
        mar_b=mar_b,
        max_dd_a=mdd_a,
        max_dd_b=mdd_b,
        blend=blend,
        decision=decision,
        decision_reasons=reasons,
    )
