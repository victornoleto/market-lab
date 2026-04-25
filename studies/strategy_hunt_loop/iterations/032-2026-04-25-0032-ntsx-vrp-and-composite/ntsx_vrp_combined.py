"""Iter 032 — NTSX 90/60 SPY+IEF static stack + iter 031 AND-composite VRP overlay.

Composes two STRONG-tier mechanisms from prior iterations:

* **iter 015 base** (`apply_static_stack`): 0.9 SPY + 0.6 IEF static
  fixed-weight return-stack (top-K #4, STRONG 77).
* **iter 031 overlay** (`compute_vrp_and_composite_returns` minus
  `rf_daily`): short put-credit-spread harvest gated by AND-composite of
  R-1 (VIX≥35 for 3 consecutive days) and R-2 (z-score(VIX,60d)≥2);
  top-K #5 tied at STRONG 76.

Mechanics
---------

For aligned series (SPY/QQQ prices, IEF prices, VIX, vix_zscore):

1. Inner-join all four on date, drop NaN on price/iv (z may be NaN
   during warmup — handled inside iter 031).
2. ``r_eq = eq_prices.pct_change()`` and ``r_bd = bd_prices.pct_change()``;
   the leading NaN is dropped.
3. ``ntsx_net, _, _ = apply_static_stack(r_eq, r_bd, eq_w, bd_w, cost_bps_per_leg)``
   → daily net of leveraged base.
4. ``vrp_full = compute_vrp_and_composite_returns(...)`` → daily total
   (rf_daily + harvest_notional × −overlay).
5. Subtract ``rf_daily = (1 + rf)^(1/252) − 1`` → ``harvest = vrp_full − rf_daily``.
6. ``combined = ntsx_net + harvest`` on the intersected index.

The funding cost on the implicit 0.5x leverage is NOT modeled (matches
iter 015 convention; iter 018 quantified the omission as ≈ −93 to
−148 bps/yr Sharpe haircut). The combined strategy IS economically
implementable with NTSX-style futures stacking + Reg-T option margin.

Reductions (proven in TDD):

* ``harvest_notional = 0`` → reduces to iter 015 NTSX exactly.
* ``eq_w = bd_w = 0`` → reduces to iter 031 overlay alone.
* ``vix_threshold = 1e9`` → AND vacuous → harvest = iter 026 − rf_daily;
  combined = NTSX + (iter 026 − rf_daily).

Citations
---------
* `[risk_parity, p.5, p.10-11, ch.1]` — Asness-Frazzini-Pedersen 2012;
  iter 015 base (NTSX 90/60 fixed-weight stack).
* `[volatility_trading, p.41, ch.3]` — VRP mechanics + SPX kurtosis 21.3.
* `[volatility_trading, p.217-218]` — Sinclair (2013) level + sustained
  short-vol-writer warning regime.
* `[volatility_trading, p.39, p.58-59]` — VIX vol-of-vol + 60-day cone.
* `[leverage_for_the_long_run, p.19-20]` — leverage on diversified base.
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
* `[advances_fin_ml, p.222-223]` — DSR cumulative n_trials.
* WisdomTree NTSX prospectus — 90/60 SPY+IEF weights (manufacturer).
* Bondarenko (2014). "Why Are Put Options So Expensive?" QJF 4(3).
* Carr & Wu (2009). "Variance Risk Premiums." RFS 22(3).
* Whaley (2009). "Understanding the VIX." JPM 35(3).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_015_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "015-2026-04-24-1704-return-stacked-static-ntsx"
ITER_031_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "031-2026-04-24-2322-vix-and-composite-vrp-primary"
for p in (ITER_015_DIR, ITER_031_DIR):
    if str(p) not in sys.path:
        sys.path.append(str(p))

from synth_stacked_etf import apply_static_stack  # noqa: E402
from vrp_and_composite import compute_vrp_and_composite_returns  # noqa: E402


def compute_ntsx_vrp_combined_returns(
    eq_prices: pd.Series,
    bd_prices: pd.Series,
    iv_series: pd.Series,
    vix_zscore: pd.Series,
    *,
    eq_w: float = 0.9,
    bd_w: float = 0.6,
    cost_bps_per_leg: float = 0.0002,
    rf: float = 0.02,
    harvest_notional: float = 1.0,
    k_long_pct: float = 0.95,
    k_short_pct: float = 0.90,
    dte_days: int = 21,
    iv_scale: float = 1.0,
    cost_bps_per_roll: float = 5.0,
    vix_threshold: float = 35.0,
    persistence_days: int = 3,
    z_threshold: float = 2.0,
) -> pd.Series:
    """Daily fractional returns of the combined NTSX + AND-composite VRP portfolio.

    Parameters
    ----------
    eq_prices, bd_prices : pd.Series
        Equity and bond adjusted-close levels. Inner-joined to a common
        DatetimeIndex.
    iv_series : pd.Series
        Implied-volatility series (% units, e.g. VIX) — used by the
        BS pricer in the harvest leg.
    vix_zscore : pd.Series
        Pre-computed rolling-60d z-score of the IV series. May contain
        NaN during warmup; iter 031 treats NaN as default-False
        (composite OPEN).
    eq_w, bd_w : float
        Static fixed weights for the NTSX leg. Defaults 0.9 / 0.6
        (NTSX prospectus). Both must be ≥ 0.
    cost_bps_per_leg : float
        Linear cost per unit of per-leg position change in the NTSX
        layer. Default 2 bps (matches iter 015).
    rf : float
        Annualized risk-free rate. Default 0.02. Used for both BS pricing
        and the rf_daily subtraction that converts iter 031's full
        return into harvest-only.
    harvest_notional : float
        Non-negative scaling on the short-writer overlay. 1.0 = one
        full spread sold per unit capital. Default 1.0.
    k_long_pct, k_short_pct, dte_days, iv_scale, cost_bps_per_roll :
        Inherited from iter 020/026/031. Defaults match iter 031.
    vix_threshold, persistence_days, z_threshold :
        AND-composite gate params. Defaults match iter 031.

    Returns
    -------
    pd.Series of daily combined strategy returns aligned to the
    intersection of the NTSX (post-pct_change) and harvest indices.

    Raises
    ------
    ValueError
        If ``eq_w < 0`` or ``bd_w < 0`` or ``harvest_notional < 0``;
        propagates ValueError from inner functions for invalid harvest
        params (vix_threshold, persistence_days, z_threshold, k_*).
    """
    if eq_w < 0:
        raise ValueError(f"eq_w must be >= 0; got {eq_w}")
    if bd_w < 0:
        raise ValueError(f"bd_w must be >= 0; got {bd_w}")
    if harvest_notional < 0:
        raise ValueError(
            f"harvest_notional must be >= 0; got {harvest_notional}"
        )

    aligned = pd.concat(
        {"eq": eq_prices, "bd": bd_prices, "iv": iv_series, "z": vix_zscore},
        axis=1,
        join="inner",
    ).dropna(subset=["eq", "bd", "iv"])
    if len(aligned) < 2:
        raise ValueError(f"need >= 2 aligned bars, got {len(aligned)}")

    r_eq = aligned["eq"].pct_change().dropna()
    r_bd = aligned["bd"].pct_change().dropna()
    ntsx_net, _, _ = apply_static_stack(
        r_eq, r_bd, eq_w=eq_w, bd_w=bd_w, cost_bps_per_leg=cost_bps_per_leg,
    )

    vrp_full = compute_vrp_and_composite_returns(
        aligned["eq"],
        aligned["iv"],
        aligned["z"],
        rf=rf,
        harvest_notional=harvest_notional,
        k_long_pct=k_long_pct,
        k_short_pct=k_short_pct,
        dte_days=dte_days,
        iv_scale=iv_scale,
        cost_bps_per_roll=cost_bps_per_roll,
        vix_threshold=vix_threshold,
        persistence_days=persistence_days,
        z_threshold=z_threshold,
    )
    rf_daily = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    harvest = vrp_full - rf_daily

    common = ntsx_net.index.intersection(harvest.index)
    combined = ntsx_net.loc[common] + harvest.loc[common]
    combined.name = "ntsx_vrp_combined_return"
    return combined
