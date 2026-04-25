"""Iter 040 — Pure-numpy reference for vol-managed VRP basket (G7 parity).

Replicates ``vrp_basket_vm.compute_vrp_basket_vm_returns`` using only
numpy + math.erf (no pandas), so iter 040 can satisfy G7 (cross-library
±3 pp CAGR).

Reuses iter 039's per-leg pure-numpy overlay primitive
``_compute_long_overlay_np`` (re-implemented here for self-containment;
identical to iter 020 / iter 026 / iter 039).

Citations
---------
* `[volatility_trading, p.11]` — Black-Scholes pricing identity.
* Moreira & Muir (2017) JoF 72(4) 1611-1644 — vol-target scaling.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline.
* `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag (no look-ahead).
"""

from __future__ import annotations

from math import erf, exp, log, sqrt

import numpy as np

SQRT_2 = sqrt(2.0)


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / SQRT_2))


def _bs_put(S: float, K: float, T: float, sigma: float, r: float) -> float:
    """Black-Scholes European put price. Matches iter 020 / 026 / 039 primitive."""
    if S <= 0 or K <= 0:
        raise ValueError(f"S,K must be > 0; got S={S} K={K}")
    if T < 0:
        raise ValueError(f"T must be >= 0; got T={T}")
    if sigma < 0:
        raise ValueError(f"sigma must be >= 0; got sigma={sigma}")
    if T <= 1e-10:
        return max(K - S, 0.0)
    if sigma <= 1e-10:
        return max(K * exp(-r * T) - S, 0.0)
    sigma_sqrt_T = sigma * sqrt(T)
    d1 = (log(S / K) + (r + 0.5 * sigma * sigma) * T) / sigma_sqrt_T
    d2 = d1 - sigma_sqrt_T
    return K * exp(-r * T) * _norm_cdf(-d2) - S * _norm_cdf(-d1)


def _put_spread_value(
    S: float, K_long: float, K_short: float,
    T: float, sigma: float, r: float,
) -> float:
    return _bs_put(S, K_long, T, sigma, r) - _bs_put(S, K_short, T, sigma, r)


def _compute_long_overlay_np(
    prices: np.ndarray,
    iv_raw: np.ndarray,
    *,
    k_long_pct: float,
    k_short_pct: float,
    dte_days: int,
    rf: float,
    iv_scale: float,
    cost_bps_per_roll: float,
) -> np.ndarray:
    """Pure-numpy replica of `compute_put_spread_daily_returns` (iter 020)."""
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

    n = len(prices)
    if n < 2:
        raise ValueError(f"need >= 2 aligned bars, got {n}")

    iv_arr = iv_raw * iv_scale / 100.0
    ret = np.zeros(n)
    cost_frac = cost_bps_per_roll / 10000.0

    S_entry = float(prices[0])
    K_long = k_long_pct * S_entry
    K_short = k_short_pct * S_entry
    entry_idx = 0
    expiry_idx = min(entry_idx + dte_days, n - 1)
    T_0 = dte_days / 252.0
    sigma_0 = max(float(iv_arr[0]), 1e-6)
    prev_value = _put_spread_value(S_entry, K_long, K_short, T_0, sigma_0, rf)
    ret[0] = -cost_frac

    for i in range(1, n):
        S_t = float(prices[i])
        sigma_t = max(float(iv_arr[i]), 1e-6)
        T_remaining = max(0, expiry_idx - i) / 252.0
        current_value = _put_spread_value(
            S_t, K_long, K_short, T_remaining, sigma_t, rf,
        )
        ret[i] = (current_value - prev_value) / S_entry
        if i >= expiry_idx and i < n - 1:
            ret[i] -= cost_frac
            S_entry = S_t
            K_long = k_long_pct * S_entry
            K_short = k_short_pct * S_entry
            entry_idx = i
            expiry_idx = min(entry_idx + dte_days, n - 1)
            prev_value = _put_spread_value(
                S_entry, K_long, K_short, T_0, sigma_t, rf,
            )
        else:
            prev_value = current_value

    return ret


def _rolling_var_np(x: np.ndarray, window: int) -> np.ndarray:
    """Rolling population (ddof=0) variance. NaN for bars < window."""
    n = len(x)
    out = np.full(n, np.nan, dtype=float)
    if n < window:
        return out
    for i in range(window - 1, n):
        w = x[i - window + 1 : i + 1]
        out[i] = float(np.var(w, ddof=0))
    return out


def compute_vrp_basket_vm_returns_np(
    prices: dict[str, np.ndarray],
    iv_raw: np.ndarray,
    *,
    rf: float = 0.02,
    harvest_notional: float = 1.0,
    weights: dict[str, float] | None = None,
    iv_scales: dict[str, float] | None = None,
    k_long_pct: float = 0.95,
    k_short_pct: float = 0.90,
    dte_days: int = 21,
    cost_bps_per_roll: float = 5.0,
    target_vol: float = 0.05,
    lookback: int = 21,
    max_lev: float = 2.0,
    periods_per_year: int = 252,
) -> np.ndarray:
    """Pure-numpy replica of ``compute_vrp_basket_vm_returns``.

    All input arrays MUST already be aligned on the same index. Returns
    a 1-D numpy array of daily strategy returns; the first
    ``lookback + 1`` bars are NaN-stripped at the END (matches the
    pandas wrapper's `.dropna()` behaviour after .shift(1)).
    """
    if harvest_notional < 0:
        raise ValueError(
            f"harvest_notional must be >= 0; got {harvest_notional}"
        )
    if not prices:
        raise ValueError("prices dict is empty")
    if target_vol <= 0:
        raise ValueError(f"target_vol must be > 0; got {target_vol}")
    if lookback < 2:
        raise ValueError(f"lookback must be >= 2; got {lookback}")
    if max_lev <= 0:
        raise ValueError(f"max_lev must be > 0; got {max_lev}")

    tickers = list(prices.keys())
    if weights is None:
        weights = {t: 1.0 / len(tickers) for t in tickers}
    if iv_scales is None:
        default_iv = {"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25}
        iv_scales = {t: default_iv.get(t, 1.0) for t in tickers}

    n = len(iv_raw)
    weighted_long = np.zeros(n)
    for t in tickers:
        arr = prices[t]
        if len(arr) != n:
            raise ValueError(
                f"prices[{t}] length {len(arr)} != iv_raw length {n}"
            )
        overlay = _compute_long_overlay_np(
            arr, iv_raw,
            k_long_pct=k_long_pct,
            k_short_pct=k_short_pct,
            dte_days=dte_days,
            rf=rf,
            iv_scale=iv_scales[t],
            cost_bps_per_roll=cost_bps_per_roll,
        )
        weighted_long = weighted_long + weights[t] * overlay

    short_overlay = (-harvest_notional) * weighted_long

    # Rolling annualised variance, then shift(1) → σ̂²_{t-1}.
    var = _rolling_var_np(short_overlay, lookback) * periods_per_year
    shifted_var = np.empty(n, dtype=float)
    shifted_var[0] = np.nan
    shifted_var[1:] = var[:-1]
    shifted_var = np.where(shifted_var < 0, 0.0, shifted_var)

    target_var = target_vol ** 2
    scale_full = np.full(n, np.nan, dtype=float)
    mask_valid = ~np.isnan(shifted_var)
    pos_mask = mask_valid & (shifted_var > 0)
    zero_mask = mask_valid & (shifted_var == 0)
    scale_full[pos_mask] = target_var / shifted_var[pos_mask]
    scale_full[zero_mask] = max_lev
    scale_full = np.clip(scale_full, 0.0, max_lev)

    rf_daily = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    strat_full = rf_daily + scale_full * short_overlay

    # Strip leading NaN bars (parity with pandas .dropna()).
    valid_mask = ~np.isnan(scale_full)
    return strat_full[valid_mask]
