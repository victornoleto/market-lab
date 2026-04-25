"""Iter 045 — 50/50 convex combo of iter 037 (3-leg static stack) + iter 039 (VRP basket).

Out-of-family return-stream addition: layer iter 039's cross-asset VRP basket
(SPY+QQQ+IWM 1/3 short put credit spreads on T-bill collateral) on top of
iter 037's 3-leg static stack (0.6 SPY + 0.45 IEF + 0.45 GLD at 1.5× total
leverage). Combined daily return is a fixed-weight convex average:

    r_combined[t] = w_037 * r_037[t] + w_039 * r_039[t]

where the two return streams are computed independently by their respective
sub-engines, then inner-joined on date and combined.

Reductions (proven in TDD):

* ``w_039 = 0`` → reduces exactly to iter 037 net.
* ``w_037 = 0`` → reduces exactly to iter 039 net.
* ``w_037 = w_039 = 0.5`` → simple arithmetic mean of the two streams.

Differs from iter 032's failed composition (iter 015 + iter 031) by:

1. iter 037 includes GLD (orthogonal to put-spread harvest losses;
   Erb-Harvey 2006).
2. iter 039 is a 3-asset basket (per-leg DD ~7-14% vs iter 031's
   single-SPY ~16%; Driessen-Maenhout-Vilkov 2009).
3. Convex combination (50/50) instead of additive overlay → total
   leverage 1.25× (vs iter 032's 2.5×).

Citations
---------
* `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity stack
  (iter 037 base architecture).
* `[volatility_trading, p.218]` — Sinclair (2013) cross-asset VRP harvest
  (iter 039 basket architecture).
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials; combining
  low-correlation strategies improves the deflated p-value.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
* Erb-Harvey (2006), FAJ 62(2), DOI 10.2469/faj.v62.n2.4084 — gold's
  strategic role in long-horizon portfolios.
* Bondarenko (2014), QJF 4(3) 1450015 — empirical SPX VRP magnitude.
* Carr-Wu (2009), RFS 22(3) 1311-1341 — variance risk premia framework.
* Driessen-Maenhout-Vilkov (2009), JoF 64(4) 1377-1406 — cross-sectional
  decomposition of index VRP.
* Markowitz (1952), JoF 7(1) — convex combination minimum-variance.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_037_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "037-2026-04-25-0224-ntsx-3leg-preserved-lev"
ITER_039_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "039-2026-04-25-0313-vrp-basket-3etf"
for p in (ITER_037_DIR, ITER_039_DIR):
    if str(p) not in sys.path:
        sys.path.append(str(p))

from synth_stacked_etf_3leg import apply_static_stack_3leg  # noqa: E402
from vrp_basket import compute_vrp_basket_returns  # noqa: E402


def compute_combined_returns(
    eq_prices: pd.Series,
    bd_prices: pd.Series,
    gld_prices: pd.Series,
    basket_prices: dict[str, pd.Series],
    iv_series: pd.Series,
    *,
    w_037: float = 0.5,
    w_039: float = 0.5,
    # iter 037 sub-strategy params
    eq_w: float = 0.60,
    bd_short_w: float = 0.45,
    bd_long_w: float = 0.45,
    cost_bps_per_leg: float = 0.0002,
    # iter 039 sub-strategy params
    rf: float = 0.02,
    harvest_notional: float = 1.0,
    weights: dict[str, float] | None = None,
    iv_scales: dict[str, float] | None = None,
    k_long_pct: float = 0.95,
    k_short_pct: float = 0.90,
    dte_days: int = 21,
    cost_bps_per_roll: float = 5.0,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """50/50 (or weighted) convex combo of iter 037 stack + iter 039 VRP basket.

    Parameters
    ----------
    eq_prices, bd_prices, gld_prices : pd.Series
        Adjusted-close levels for the 3-leg static stack (iter 037 input).
        Inner-joined to produce iter 037's net return stream.
    basket_prices : dict[str, pd.Series]
        Mapping of basket ticker → adjusted-close levels (iter 039 input).
        Default 1/3 weights when ``weights is None``.
    iv_series : pd.Series
        Implied-volatility proxy (e.g. VIX) for iter 039's BS pricing.
    w_037, w_039 : float
        Convex combination weights. Both ≥ 0; if their sum is 0 raise.
        For canonical 50/50, both 0.5. The function does NOT enforce
        sum=1: caller may pass non-normalised weights for sensitivity
        runs (the implementation just multiplies and adds).
    eq_w, bd_short_w, bd_long_w, cost_bps_per_leg :
        iter 037 sub-strategy params. Defaults match iter 037
        (`ntsx_3leg_preserved_60_45_45_spy_ief_gld`).
    rf, harvest_notional, weights, iv_scales, k_long_pct, k_short_pct,
        dte_days, cost_bps_per_roll :
        iter 039 sub-strategy params. Defaults match iter 039
        (`vrp_basket_eq3_5_10_1m`).

    Returns
    -------
    (r_combined, r_037, r_039)
        ``r_combined`` : pd.Series of combined daily net returns indexed
        on the inner-join of iter 037 and iter 039 returns.
        ``r_037``, ``r_039`` : per-strategy net return streams aligned
        to the same index, for diagnostic / correlation analysis.

    Raises
    ------
    ValueError
        If ``w_037 < 0`` or ``w_039 < 0`` or their sum is 0.
        Propagates ValueError from inner functions for invalid params
        (negative bond/eq weights, negative harvest_notional, invalid
        strikes, etc.).
    """
    if w_037 < 0:
        raise ValueError(f"w_037 must be >= 0; got {w_037}")
    if w_039 < 0:
        raise ValueError(f"w_039 must be >= 0; got {w_039}")
    if (w_037 + w_039) <= 0:
        raise ValueError(
            f"w_037 + w_039 must be > 0; got {w_037 + w_039}"
        )

    # --- iter 037 net (3-leg static stack on returns) --------------
    r_eq = eq_prices.pct_change().dropna()
    r_bd = bd_prices.pct_change().dropna()
    r_gld = gld_prices.pct_change().dropna()
    common_037 = r_eq.index.intersection(r_bd.index).intersection(r_gld.index)
    if len(common_037) < 2:
        raise ValueError(
            f"iter 037 inputs have <2 overlapping bars after pct_change "
            f"(eq={len(r_eq)}, bd={len(r_bd)}, gld={len(r_gld)})"
        )
    r_037, _, _ = apply_static_stack_3leg(
        r_eq.loc[common_037],
        r_bd.loc[common_037],
        r_gld.loc[common_037],
        eq_w=eq_w,
        bd_short_w=bd_short_w,
        bd_long_w=bd_long_w,
        cost_bps_per_leg=cost_bps_per_leg,
    )

    # --- iter 039 net (VRP basket on prices) -----------------------
    r_039 = compute_vrp_basket_returns(
        basket_prices,
        iv_series,
        rf=rf,
        harvest_notional=harvest_notional,
        weights=weights,
        iv_scales=iv_scales,
        k_long_pct=k_long_pct,
        k_short_pct=k_short_pct,
        dte_days=dte_days,
        cost_bps_per_roll=cost_bps_per_roll,
    )

    # --- Inner-join on the intersection and combine ----------------
    common = r_037.index.intersection(r_039.index)
    if len(common) < 2:
        raise ValueError(
            f"iter 037 and iter 039 streams have <2 overlapping bars "
            f"(037={len(r_037)}, 039={len(r_039)})"
        )
    r_037_aligned = r_037.loc[common]
    r_039_aligned = r_039.loc[common]
    combined = w_037 * r_037_aligned + w_039 * r_039_aligned
    combined.name = "combined_037_039_return"
    r_037_aligned.name = "r_037"
    r_039_aligned.name = "r_039"
    return combined, r_037_aligned, r_039_aligned
