"""Iter 021 — Short-put-credit-spread VRP-harvest overlay on iter 016 base.

Semantic-opposite of iter 020: instead of BUYING a 5/10% OTM put
spread as tail hedge, SELL the same spread as a variance-risk-premium
(VRP) harvest overlay. Every strike, roll schedule, IV source, and
cost parameter is identical to iter 020 — the ONLY change is the
overlay stream is SUBTRACTED (short writer's P&L) instead of ADDED
(long holder's P&L):

    r_eq_hedged[t] = r_eq[t] + (+1.0) * put_spread_return[t]   (iter 020)
    r_eq_hedged[t] = r_eq[t] - (+1.0) * put_spread_return[t]   (iter 021)

Because iter 020's overlay stream averages to −3.0/−3.0/−4.1 %/yr
across the three datasets (long-holder pays theta), the inverted
stream averages to +3.0/+3.0/+4.1 %/yr — the variance-risk-premium
iter 020 PAID is what iter 021 COLLECTS. Tail loss is capped at
``(k_long_pct - k_short_pct) - net_credit ≈ 4%`` of per-roll notional
(the long 10% OTM put caps downside below −10 %).

Implementation reuses iter 020's `compute_put_spread_daily_returns`
(option-pricing primitive) and iter 016's
`apply_static_stack_vol_managed` (backbone). Iter 020's top-level
function asserts ``hedge_notional_ratio ≥ 0``; we call the primitives
directly to avoid that guard while preserving every downstream
computation identically.

Citations
---------

* `[volatility_trading, ch.3]` — variance risk premium mechanics.
* `[volatility_trading, p.11]` — Black-Scholes pricing used for MtM.
* `[volatility_trading, p.41]` — SPX kurtosis 21.3 justifies capped
  (credit-spread) vs uncapped short put.
* `[risk_parity, p.10-11, ch.1]` — iter 016 base stack (unchanged).
* `[systematic_trading, p.40, ch.2]` — vol standardisation primitive
  (applied by the iter 016 sub-call, unchanged).
* Bondarenko, O. (2014). "Why Are Put Options So Expensive?"
  QJF 4(3) — empirical VRP ≈ 2-3 %/yr for SPX put writers.
* Carr & Madan (1999). "Towards a Theory of Volatility Trading" —
  structural orthogonality between theta-sellers and buyers.
* Moreira & Muir (2017). JoF 72(4), 1611-1644 — inherited vol-target.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_016_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / "016-2026-04-24-1729-static-stack-vm-hybrid"
ITER_020_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / "020-2026-04-24-1850-put-spread-tail-hedge"
for p in (ITER_016_DIR, ITER_020_DIR):
    if str(p) not in sys.path:
        sys.path.append(str(p))

from put_spread_hedge import compute_put_spread_daily_returns  # noqa: E402
from static_stack_vm import apply_static_stack_vol_managed  # noqa: E402


def apply_short_credit_spread_stack(
    r_eq: pd.Series,
    r_bd: pd.Series,
    prices_eq: pd.Series,
    iv_series: pd.Series,
    *,
    eq_weight: float,
    bd_weight: float,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    k_long_pct: float = 0.95,
    k_short_pct: float = 0.90,
    dte_days: int = 21,
    rf: float = 0.02,
    iv_scale: float = 1.0,
    cost_bps_per_roll: float = 5.0,
    harvest_notional_ratio: float = 1.0,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """Iter 021 pipeline: short-credit-spread VRP harvest on iter 016 stack.

    Mirrors iter 020's ``apply_put_spread_hedged_stack`` line-for-line,
    except the overlay is SUBTRACTED (short writer's P&L). All
    parameter semantics — including the ``k_*_pct`` strike conventions
    — match iter 020.

    Parameters
    ----------
    harvest_notional_ratio : float
        Non-negative multiplier on the overlay stream. Default 1.0 =
        full notional short writer. Must be ≥ 0; sign flip (short
        side) is applied internally.

    Returns
    -------
    (net_returns, pos_eq, pos_bd, scale, short_spread_returns)
        ``short_spread_returns`` is the short writer's daily P&L as a
        fraction of per-roll notional (i.e. iter 020's overlay stream
        multiplied by −1).
    """
    if harvest_notional_ratio < 0:
        raise ValueError(
            f"harvest_notional_ratio must be >= 0; "
            f"got {harvest_notional_ratio}. Use positive magnitude — "
            f"the sign flip to short-side is applied internally."
        )

    # 1. Option-pricing overlay (LONG holder's P&L, same as iter 020).
    long_overlay = compute_put_spread_daily_returns(
        prices_eq, iv_series,
        k_long_pct=k_long_pct,
        k_short_pct=k_short_pct,
        dte_days=dte_days,
        rf=rf,
        iv_scale=iv_scale,
        cost_bps_per_roll=cost_bps_per_roll,
    )
    # 2. Short writer's P&L = negated long P&L.
    short_overlay = -long_overlay
    short_overlay.name = "short_spread_return"

    # 3. Align equity + bond + overlay on a common index.
    common = r_eq.index.intersection(r_bd.index).intersection(
        short_overlay.index,
    )
    r_eq_a = r_eq.loc[common].astype(float)
    r_bd_a = r_bd.loc[common].astype(float)
    overlay_a = short_overlay.loc[common].astype(float)

    # 4. Add overlay to equity leg (non-negative harvest multiplier).
    r_eq_harvested = r_eq_a + harvest_notional_ratio * overlay_a
    r_eq_harvested.name = r_eq.name if r_eq.name else "r_eq_harvested"

    # 5. Run iter 016's identical vol-managed stack on the harvested
    #    equity stream and unchanged bond stream.
    net, pos_eq, pos_bd, scale = apply_static_stack_vol_managed(
        r_eq_harvested, r_bd_a,
        eq_weight=eq_weight,
        bd_weight=bd_weight,
        target_vol=target_vol,
        lookback=lookback,
        max_leverage=max_leverage,
        periods_per_year=periods_per_year,
        cost_bps_per_leg=cost_bps_per_leg,
    )
    return net, pos_eq, pos_bd, scale, overlay_a.loc[net.index]
