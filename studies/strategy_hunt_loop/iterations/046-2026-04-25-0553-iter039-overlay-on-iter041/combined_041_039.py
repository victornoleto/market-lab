"""Iter 046 — 50/50 convex combo of iter 041 (regime-gated stack) + iter 039 (VRP basket).

Same out-of-family return-stream addition mechanism as iter 045, but with
the **regime-gated** static stack (iter 041, TOP-K #1 at score 84) replacing
the un-gated stack (iter 037, score 79). The convex combination is::

    r_combined[t] = w_041 * r_041[t] + w_039 * r_039[t]

where ``r_041`` is the iter 041 binary-VIX-regime weight tilt on
SPY+IEF+GLD (calm vs stress weights at preserved 1.40-1.50× total
leverage) and ``r_039`` is the cross-asset VRP basket on T-bill +
1/3 SPY+QQQ+IWM 5/10% OTM short put credit spreads.

Reductions (proven in TDD):

* ``w_039 = 0`` → reduces exactly to iter 041 net.
* ``w_041 = 0`` → reduces exactly to iter 039 net.
* ``w_041 = w_039 = 0.5`` → simple arithmetic mean of the two streams.
* ``calm_weights == stress_weights`` → reduces to a static-stack baseline
  matching iter 045's iter 037 leg (sanity gate for the regime layer).

Differs from iter 045 by the **base substitution** only:

1. iter 045 uses iter 037 (un-gated 0.6/0.45/0.45 SPY+IEF+GLD).
2. iter 046 uses iter 041 (binary VIX-regime weight tilt:
   {0.70/0.40/0.40} calm vs {0.30/0.55/0.55} stress at threshold 20.0
   with VIX[t-1] lag).

iter 045's empirical result was: corr(r_037, r_039) ≈ 0.58, DSR worst-p
0.222 → 0.096 (57% reduction). iter 046 expected: corr(r_041, r_039)
≈ 0.55-0.60 (similar — both share SPY exposure), DSR worst-p 0.168 →
0.07-0.09 (similar relative reduction on a lower starting baseline).

Citations
---------
* `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity stack
  with regime-conditional weight tilts (iter 041 base architecture).
* `[volatility_trading, p.218]` — Sinclair (2013) cross-asset VRP harvest
  (iter 039 basket architecture).
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials;
  combining low-correlation strategies improves the deflated p-value.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
* `[advances_fin_ml, p.162-164]` — no-lookahead lag rule (iter 041
  uses VIX[t-1]).
* Whaley (2009), JPM 35(3), DOI 10.3905/JPM.2009.35.3.098 — VIX as
  ex-ante risk regime indicator.
* Bondarenko (2014), QJF 4(3) 1450015 — empirical SPX VRP magnitude.
* Carr-Wu (2009), RFS 22(3) 1311-1341 — variance risk premia framework.
* Driessen-Maenhout-Vilkov (2009), JoF 64(4) 1377-1406 — cross-sectional
  decomposition of index VRP.
* Erb-Harvey (2006), FAJ 62(2), DOI 10.2469/faj.v62.n2.4084 — gold's
  strategic role.
* Asness-Moskowitz-Pedersen (2013), JoF 68(3) 929-985 — diversification.
* Markowitz (1952), JoF 7(1) — convex combination minimum-variance.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Mapping

import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_039_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "039-2026-04-25-0313-vrp-basket-3etf"
ITER_041_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "041-2026-04-25-0358-regime-weights-vix-static-stack"
for p in (ITER_039_DIR, ITER_041_DIR):
    if str(p) not in sys.path:
        sys.path.append(str(p))

from regime_weights_static_stack import apply_regime_weights_3leg  # noqa: E402
from vrp_basket import compute_vrp_basket_returns  # noqa: E402


# Default iter 041 cfg (TOP-K #1 weights from BASE_MEMORY)
DEFAULT_CALM_WEIGHTS = {"eq_w": 0.70, "bd_w": 0.40, "gld_w": 0.40}
DEFAULT_STRESS_WEIGHTS = {"eq_w": 0.30, "bd_w": 0.55, "gld_w": 0.55}


def compute_combined_returns(
    eq_prices: pd.Series,
    bd_prices: pd.Series,
    gld_prices: pd.Series,
    basket_prices: dict[str, pd.Series],
    iv_series: pd.Series,
    *,
    w_041: float = 0.5,
    w_039: float = 0.5,
    # iter 041 sub-strategy params
    calm_weights: Mapping[str, float] | None = None,
    stress_weights: Mapping[str, float] | None = None,
    vix_threshold: float = 20.0,
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
    """50/50 (or weighted) convex combo of iter 041 stack + iter 039 VRP basket.

    Parameters
    ----------
    eq_prices, bd_prices, gld_prices : pd.Series
        Adjusted-close levels for the 3-leg static stack (iter 041 input).
        Inner-joined to produce iter 041's net return stream.
    basket_prices : dict[str, pd.Series]
        Mapping of basket ticker → adjusted-close levels (iter 039 input).
        Default 1/3 weights when ``weights is None``.
    iv_series : pd.Series
        Implied-volatility proxy (e.g. VIX) used by **both** legs:
        iter 041 uses VIX_{t-1} for the regime gate; iter 039 uses VIX_t
        for BS pricing of the put credit spreads.
    w_041, w_039 : float
        Convex combination weights. Both ≥ 0; if their sum is 0 raise.
        For canonical 50/50, both 0.5. The function does NOT enforce
        sum=1 (caller may pass non-normalised weights for sensitivity
        runs); the implementation just multiplies and adds.
    calm_weights, stress_weights : Mapping[str, float] | None
        iter 041 regime weights. Each is a dict with keys
        "eq_w", "bd_w", "gld_w" and non-negative values. Default to
        iter 041's TOP-K #1 cfg ({0.70, 0.40, 0.40} calm; {0.30, 0.55,
        0.55} stress at threshold 20.0).
    vix_threshold : float
        VIX level dividing calm from stress regime. Default 20.0.
    cost_bps_per_leg : float
        Linear cost per unit per-leg ∆position (iter 041 leg). Default 2 bps.
    rf, harvest_notional, weights, iv_scales, k_long_pct, k_short_pct,
        dte_days, cost_bps_per_roll :
        iter 039 sub-strategy params. Defaults match iter 039.

    Returns
    -------
    (r_combined, r_041, r_039)
        ``r_combined`` : pd.Series of combined daily net returns indexed
        on the inner-join of iter 041 and iter 039 returns.
        ``r_041``, ``r_039`` : per-strategy net return streams aligned
        to the same index, for diagnostic / correlation analysis.

    Raises
    ------
    ValueError
        If ``w_041 < 0`` or ``w_039 < 0`` or their sum is 0. Propagates
        ValueError from inner functions for invalid params.
    """
    if w_041 < 0:
        raise ValueError(f"w_041 must be >= 0; got {w_041}")
    if w_039 < 0:
        raise ValueError(f"w_039 must be >= 0; got {w_039}")
    if (w_041 + w_039) <= 0:
        raise ValueError(
            f"w_041 + w_039 must be > 0; got {w_041 + w_039}"
        )

    cw = dict(calm_weights) if calm_weights is not None else dict(DEFAULT_CALM_WEIGHTS)
    sw = dict(stress_weights) if stress_weights is not None else dict(DEFAULT_STRESS_WEIGHTS)

    # --- iter 041 net (regime-gated stack on returns) --------------
    r_eq = eq_prices.pct_change().dropna()
    r_bd = bd_prices.pct_change().dropna()
    r_gld = gld_prices.pct_change().dropna()
    common_041 = r_eq.index.intersection(r_bd.index).intersection(r_gld.index)
    if len(common_041) < 2:
        raise ValueError(
            f"iter 041 inputs have <2 overlapping bars after pct_change "
            f"(eq={len(r_eq)}, bd={len(r_bd)}, gld={len(r_gld)})"
        )
    r_041, _, _, _ = apply_regime_weights_3leg(
        r_eq.loc[common_041],
        r_bd.loc[common_041],
        r_gld.loc[common_041],
        iv_series,
        calm_weights=cw,
        stress_weights=sw,
        vix_threshold=vix_threshold,
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
    common = r_041.index.intersection(r_039.index)
    if len(common) < 2:
        raise ValueError(
            f"iter 041 and iter 039 streams have <2 overlapping bars "
            f"(041={len(r_041)}, 039={len(r_039)})"
        )
    r_041_aligned = r_041.loc[common]
    r_039_aligned = r_039.loc[common]
    combined = w_041 * r_041_aligned + w_039 * r_039_aligned
    combined.name = "combined_041_039_return"
    r_041_aligned.name = "r_041"
    r_039_aligned.name = "r_039"
    return combined, r_041_aligned, r_039_aligned
