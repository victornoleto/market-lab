"""Iter 020 — Monthly-rolled put-spread tail hedge overlay on iter 016 equity.

Wraps iter 016's ``apply_static_stack_vol_managed`` by first adding a
daily Black-Scholes-priced put-spread P&L stream to the equity leg,
then running the exact same vol-target stacking on the hedged returns.

Mechanics
---------

1. Open a put spread on the FIRST bar of the aligned (price, IV)
   dataset:
   - Long 1 put at strike ``K_long = k_long_pct * S_0``
   - Short 1 put at strike ``K_short = k_short_pct * S_0`` (where
     ``k_short_pct < k_long_pct``, e.g. 0.90 vs 0.95 for 5%/10% OTM)
   - Expiry = ``dte_days`` trading days from open

2. Each bar mark the spread to market using BS with the bar's IV:
   ``value_t = BS_put(S_t, K_long, T, σ_t, r) - BS_put(S_t, K_short,
   T, σ_t, r)`` (intrinsic value at expiry, T=0).

3. Daily return of the overlay, expressed as a fraction of the
   per-position entry notional ``S_entry``:
   ``ret[t] = (value_t - value_{t-1}) / S_entry``

4. At expiry (every ``dte_days`` bars): close the old position at its
   intrinsic value, pay ``cost_bps_per_roll`` transaction cost, open a
   new position at the new spot. The premium paid for the new position
   is automatically accounted for by subsequent MtM decay (sum of daily
   changes over the life of a position equals realized P&L).

The hedge contribution is then added to the equity leg as
``r_eq_hedged = r_eq + h * put_spread_return`` (where ``h`` =
``hedge_notional_ratio``, default 1.0 = full notional hedged).

Citations
---------
* `[volatility_trading, p.11]` — BSM pricing, IV defined as the σ
  making BS reproduce market price.
* `[volatility_trading, p.41]` — SPX excess kurtosis 21.3 justifies
  tail hedge.
* `[risk_parity, p.10-11, ch.1]` — iter 016 base (static 60:40 stack).
* `[systematic_trading, p.40, ch.2]` — vol standardisation primitive.
* `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag discipline; IV is
  contemporaneous but pricing uses same-bar close (no future bar
  accessed in put-spread daily return).
* Moreira & Muir (2017) JoF 72(4), 1611-1644 — vol-target scaling.
* Carr & Madan (1999) "Towards a Theory of Volatility Trading" —
  static replication of convex payoffs from European options (structural
  orthogonality argument).
"""

from __future__ import annotations

import sys
from math import erf, log, sqrt
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_016_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / "016-2026-04-24-1729-static-stack-vm-hybrid"
# Append (not insert) so iter 016's dir lives at end of sys.path,
# avoiding collision with iter 020's run_backtests.py
if str(ITER_016_DIR) not in sys.path:
    sys.path.append(str(ITER_016_DIR))

from static_stack_vm import apply_static_stack_vol_managed  # noqa: E402


SQRT_2 = sqrt(2.0)


def _norm_cdf(x: float) -> float:
    """Standard normal CDF via erf (no scipy dep — matches numpy ref)."""
    return 0.5 * (1.0 + erf(x / SQRT_2))


def black_scholes_put(
    S: float, K: float, T: float, sigma: float, r: float = 0.0,
) -> float:
    """Black-Scholes European put price (continuous dividend = 0).

    Parameters
    ----------
    S : float
        Spot price (> 0).
    K : float
        Strike (> 0).
    T : float
        Time to expiry in years (>= 0). T = 0 returns intrinsic value.
    sigma : float
        Annualised volatility (> 0). sigma = 0 returns intrinsic discounted.
    r : float
        Risk-free rate (continuously compounded). Default 0.0.

    Returns
    -------
    Put value in same units as S and K.
    """
    if S <= 0 or K <= 0:
        raise ValueError(f"S and K must be > 0; got S={S}, K={K}")
    if T < 0:
        raise ValueError(f"T must be >= 0; got T={T}")
    if sigma < 0:
        raise ValueError(f"sigma must be >= 0; got sigma={sigma}")

    # At expiry or zero vol: intrinsic (discounted for K if sigma=0 but T>0)
    if T <= 1e-10:
        return max(K - S, 0.0)
    if sigma <= 1e-10:
        # Put is K*e^{-rT} - S if ITM forward, else 0.
        return max(K * np.exp(-r * T) - S, 0.0)

    sigma_sqrt_T = sigma * sqrt(T)
    d1 = (log(S / K) + (r + 0.5 * sigma * sigma) * T) / sigma_sqrt_T
    d2 = d1 - sigma_sqrt_T
    return K * np.exp(-r * T) * _norm_cdf(-d2) - S * _norm_cdf(-d1)


def _price_put_spread(
    S: float, K_long: float, K_short: float,
    T: float, sigma: float, r: float,
) -> float:
    """Value of (long K_long put - short K_short put) at spot S."""
    p_long = black_scholes_put(S, K_long, T, sigma, r)
    p_short = black_scholes_put(S, K_short, T, sigma, r)
    return p_long - p_short


def compute_put_spread_daily_returns(
    prices: pd.Series,
    iv_series: pd.Series,
    *,
    k_long_pct: float = 0.95,
    k_short_pct: float = 0.90,
    dte_days: int = 21,
    rf: float = 0.02,
    iv_scale: float = 1.0,
    cost_bps_per_roll: float = 5.0,
) -> pd.Series:
    """Daily fractional returns of a rolled put-spread overlay.

    Parameters
    ----------
    prices : pd.Series
        Equity adj_close (positive, float). Index is trading-day dates.
    iv_series : pd.Series
        Implied volatility as a percentage (e.g. VIX in %). Will be
        divided by 100 and scaled by ``iv_scale`` to get decimal σ.
    k_long_pct : float
        Long put strike as fraction of entry spot (protection starts
        here; default 0.95 = 5% OTM).
    k_short_pct : float
        Short put strike as fraction of entry spot (default 0.90 =
        10% OTM; must be < k_long_pct).
    dte_days : int
        Days-to-expiry in trading days. Roll frequency = this many bars.
    rf : float
        Risk-free rate, constant. Default 0.02.
    iv_scale : float
        Multiplier applied to iv_series / 100 (use 1.0 for SPY+VIX,
        ~1.1 for QQQ since NDX IV runs ~10% higher).
    cost_bps_per_roll : float
        Transaction cost per roll in bps of current notional. Default 5.

    Returns
    -------
    pd.Series of daily fractional hedge returns aligned to input index
    (after dropping any rows missing price or IV).

    Raises
    ------
    ValueError if fewer than 2 aligned bars, or param bounds violated.
    """
    if k_short_pct >= k_long_pct:
        raise ValueError(
            f"k_short_pct must be < k_long_pct; "
            f"got k_short={k_short_pct}, k_long={k_long_pct}"
        )
    if not (0 < k_short_pct < 1 and 0 < k_long_pct < 1):
        raise ValueError("strike pcts must be in (0, 1)")
    if dte_days < 2:
        raise ValueError(f"dte_days must be >= 2; got {dte_days}")
    if cost_bps_per_roll < 0:
        raise ValueError(f"cost_bps must be >= 0; got {cost_bps_per_roll}")
    if iv_scale <= 0:
        raise ValueError(f"iv_scale must be > 0; got {iv_scale}")

    aligned = pd.concat(
        {"price": prices.astype(float), "iv_raw": iv_series.astype(float)},
        axis=1, join="inner",
    ).dropna()
    n = len(aligned)
    if n < 2:
        raise ValueError(f"need >= 2 aligned bars, got {n}")

    prices_arr = aligned["price"].to_numpy()
    iv_arr = aligned["iv_raw"].to_numpy() * iv_scale / 100.0
    dates = aligned.index

    ret = np.zeros(n)
    cost_frac = cost_bps_per_roll / 10000.0

    # Open initial position at i=0
    S_entry = float(prices_arr[0])
    K_long = k_long_pct * S_entry
    K_short = k_short_pct * S_entry
    entry_idx = 0
    expiry_idx = min(entry_idx + dte_days, n - 1)

    T_0 = dte_days / 252.0
    sigma_0 = max(float(iv_arr[0]), 1e-6)
    prev_value = _price_put_spread(S_entry, K_long, K_short, T_0, sigma_0, rf)

    # Opening cost on day 0
    ret[0] = -cost_frac

    for i in range(1, n):
        S_t = float(prices_arr[i])
        sigma_t = max(float(iv_arr[i]), 1e-6)

        # MtM current position at today's prices
        T_remaining = max(0, expiry_idx - i) / 252.0
        current_value = _price_put_spread(
            S_t, K_long, K_short, T_remaining, sigma_t, rf,
        )
        ret[i] = (current_value - prev_value) / S_entry

        # Is this the roll day? At or past expiry bar
        if i >= expiry_idx and i < n - 1:
            # Close old at its current value (already counted in ret[i]),
            # pay transaction cost for closing + opening,
            # open new position at today's spot.
            ret[i] -= cost_frac
            S_entry = S_t
            K_long = k_long_pct * S_entry
            K_short = k_short_pct * S_entry
            entry_idx = i
            expiry_idx = min(entry_idx + dte_days, n - 1)
            # New premium is the new position's value today.
            prev_value = _price_put_spread(
                S_entry, K_long, K_short, T_0, sigma_t, rf,
            )
        else:
            prev_value = current_value

    return pd.Series(ret, index=dates, name="put_spread_return")


def apply_put_spread_hedged_stack(
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
    hedge_notional_ratio: float = 1.0,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """Iter 020 full pipeline: put-spread overlay on iter 016 equity leg.

    Steps
    -----
    1. Compute daily put-spread overlay return stream from ``prices_eq``
       and ``iv_series``.
    2. Align with r_eq, r_bd (drop any rows missing any input).
    3. Build hedged equity returns:
       ``r_eq_hedged = r_eq + hedge_notional_ratio * put_spread_return``
    4. Run iter 016's ``apply_static_stack_vol_managed`` on
       (r_eq_hedged, r_bd) with identical scaling params.

    Returns
    -------
    (net_returns, pos_eq, pos_bd, scale, put_spread_returns)
      - ``net_returns`` : final daily net returns of the hedged stack
      - ``pos_eq, pos_bd, scale`` : same semantics as iter 016
      - ``put_spread_returns`` : the overlay return stream (for audit)
    """
    if hedge_notional_ratio < 0:
        raise ValueError(
            f"hedge_notional_ratio must be >= 0; got {hedge_notional_ratio}"
        )

    overlay = compute_put_spread_daily_returns(
        prices_eq, iv_series,
        k_long_pct=k_long_pct,
        k_short_pct=k_short_pct,
        dte_days=dte_days,
        rf=rf,
        iv_scale=iv_scale,
        cost_bps_per_roll=cost_bps_per_roll,
    )

    # Align all three: r_eq, r_bd, overlay
    common = r_eq.index.intersection(r_bd.index).intersection(overlay.index)
    r_eq_a = r_eq.loc[common].astype(float)
    r_bd_a = r_bd.loc[common].astype(float)
    overlay_a = overlay.loc[common].astype(float)

    r_eq_hedged = r_eq_a + hedge_notional_ratio * overlay_a
    r_eq_hedged.name = r_eq.name if r_eq.name else "r_eq_hedged"

    net, pos_eq, pos_bd, scale = apply_static_stack_vol_managed(
        r_eq_hedged, r_bd_a,
        eq_weight=eq_weight,
        bd_weight=bd_weight,
        target_vol=target_vol,
        lookback=lookback,
        max_leverage=max_leverage,
        periods_per_year=periods_per_year,
        cost_bps_per_leg=cost_bps_per_leg,
    )
    return net, pos_eq, pos_bd, scale, overlay_a.loc[net.index]
