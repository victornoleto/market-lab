"""Iter 063 — Internal-LETF UPRO substitution applied to iter 041.

Builds a regime-weighted 3-leg static stack identical to iter 041 except
that the equity leg returns come from a **synth/real LETF** (UPRO/TQQQ)
instead of the cash equity (SPY/QQQ), with weights re-scaled to
*preserve equity exposure* (UPRO daily exposure = 3 × SPY daily; weight
divides by 3) and the freed NAV redirected equally to the bond and
gold legs (per iter 062's pattern).

Calm regime: original (0.70 SPY, 0.40 IEF, 0.40 GLD) at 1.50× total NAV.
Substituted: 0.2333 UPRO + 0.6333 IEF + 0.6333 GLD = 1.50× total NAV
             (0.2333 × 3 = 0.70 SPY-equiv preserved; 0.4667 NAV freed
             split 50/50 = +0.2333 each diversifier leg)

Stress regime: original (0.30 SPY, 0.55 IEF, 0.55 GLD) at 1.40× total
NAV. Substituted: 0.10 UPRO + 0.65 IEF + 0.65 GLD = 1.40× total NAV
                  (0.10 × 3 = 0.30 SPY-equiv preserved; 0.20 NAV freed
                  split 50/50 = +0.10 each diversifier leg).

iter 039 (VRP basket — options structure) cannot be substituted via
LETF because options on UPRO are NOT linear transforms of options on
SPY (gamma path differs). iter 039 is preserved verbatim via its saved
return stream from iter 046's results.json.

Citations
---------
* `[leverage_for_the_long_run, p.19-25]` — Hsiao-Williams 2017 daily-
  reset LETF formula and preserved-leverage zone.
* `[risk_parity, ch.5]` — multi-leg risk-parity stack with regime
  tilts (iter 041 architecture).
* `[advances_fin_ml, ch.17-18]` — regime detection (iter 041 VIX gate).
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule
  (vacuous for static weights, prior-day VIX).
* Whaley (2009), JPM 35(3) — VIX as regime indicator.
* ProShares UPRO prospectus 2024-2025 — expense ratio 0.91%/yr.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Mapping

import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_041_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "041-2026-04-25-0358-regime-weights-vix-static-stack"
ITER_062_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "062-2026-04-25-1220-iter037-upro-substitution-internal-letf"
for _p in (ITER_041_DIR, ITER_062_DIR):
    if str(_p) not in sys.path:
        sys.path.append(str(_p))

from regime_weights_static_stack import apply_regime_weights_3leg  # noqa: E402
from synth_letf_3leg import (  # noqa: E402
    UPRO_EXPENSE_RATIO_DEFAULT,
    LETF_LEVERAGE_DEFAULT,
    join_real_and_synth_letf,
    synth_upro_returns,
)


# Pre-committed iter 063 weights (preserve iter 041 equity exposure
# under leverage=3, redirect freed NAV equally to diversifiers).
ITER063_CALM_WEIGHTS = {
    "eq_w": 0.70 / 3.0,            # 0.2333... UPRO ≈ 0.70 SPY-equiv
    "bd_w": 0.40 + (0.70 - 0.70 / 3.0) / 2.0,   # 0.6333...
    "gld_w": 0.40 + (0.70 - 0.70 / 3.0) / 2.0,  # 0.6333...
}
ITER063_STRESS_WEIGHTS = {
    "eq_w": 0.30 / 3.0,            # 0.10 UPRO ≈ 0.30 SPY-equiv
    "bd_w": 0.55 + (0.30 - 0.30 / 3.0) / 2.0,   # 0.65
    "gld_w": 0.55 + (0.30 - 0.30 / 3.0) / 2.0,  # 0.65
}


def build_letf_returns(
    spy_returns: pd.Series,
    real_letf_returns: pd.Series | None,
    *,
    leverage: float = LETF_LEVERAGE_DEFAULT,
    expense_ratio: float = UPRO_EXPENSE_RATIO_DEFAULT,
) -> pd.Series:
    """Build the equity-leg LETF return stream over ``spy_returns.index``.

    If ``real_letf_returns`` is provided AND its inception falls within
    the SPY window, returns the joined synth/real series via
    ``join_real_and_synth_letf``. Otherwise, returns pure synth (3·r_SPY
    − expense/252) over the full SPY window.

    Parameters
    ----------
    spy_returns : pd.Series
        Daily SPY (or QQQ) returns over the desired window.
    real_letf_returns : pd.Series or None
        Daily real LETF returns from inception forward. Pass None to
        force pure-synth output.
    leverage, expense_ratio : float
        Forwarded to the synth formula. Defaults: 3×, 0.91%/yr.

    Returns
    -------
    pd.Series
        Daily LETF return stream aligned to the input window.
    """
    if real_letf_returns is None or len(real_letf_returns) == 0:
        return synth_upro_returns(
            spy_returns, leverage=leverage, expense_ratio=expense_ratio,
        )
    real_first = real_letf_returns.index[0]
    if real_first <= spy_returns.index[0]:
        # Real LETF covers the entire window → use real only on the
        # overlap; outside the overlap we have nothing to splice.
        common = real_letf_returns.index.intersection(spy_returns.index)
        if len(common) == 0:
            raise ValueError(
                "real_letf_returns has no overlap with spy_returns index"
            )
        out = real_letf_returns.loc[common].copy()
        out.name = "joined_LETF"
        return out
    return join_real_and_synth_letf(
        spy_returns, real_letf_returns,
        leverage=leverage, expense_ratio=expense_ratio,
    )


def compute_iter041_letf_returns(
    r_letf: pd.Series,
    r_bd: pd.Series,
    r_gld: pd.Series,
    vix: pd.Series,
    *,
    calm_weights: Mapping[str, float] | None = None,
    stress_weights: Mapping[str, float] | None = None,
    vix_threshold: float = 20.0,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.DataFrame, pd.Series, pd.Series]:
    """iter 041's regime-weighted-3leg engine with LETF equity leg.

    Thin wrapper over ``apply_regime_weights_3leg`` that defaults to
    iter 063's preserved-equity weights.

    Parameters
    ----------
    r_letf, r_bd, r_gld : pd.Series
        Daily simple-return streams for the 3 legs (LETF + IEF + GLD).
        Must share identical DatetimeIndex.
    vix : pd.Series
        Daily VIX close for the regime gate (uses VIX[t-1] internally).
    calm_weights, stress_weights : Mapping[str, float] or None
        Defaults to iter 063 ITER063_CALM_WEIGHTS / ITER063_STRESS_WEIGHTS.
    vix_threshold : float
        VIX cutoff between calm (regime=1) and stress (regime=0).
    cost_bps_per_leg : float
        Per-leg ∆position cost in fraction (default 2 bps).

    Returns
    -------
    (net, positions, scale, regime) — same as ``apply_regime_weights_3leg``.
    """
    cw = dict(calm_weights) if calm_weights is not None else dict(ITER063_CALM_WEIGHTS)
    sw = dict(stress_weights) if stress_weights is not None else dict(ITER063_STRESS_WEIGHTS)
    return apply_regime_weights_3leg(
        r_letf, r_bd, r_gld, vix,
        calm_weights=cw,
        stress_weights=sw,
        vix_threshold=vix_threshold,
        cost_bps_per_leg=cost_bps_per_leg,
    )
