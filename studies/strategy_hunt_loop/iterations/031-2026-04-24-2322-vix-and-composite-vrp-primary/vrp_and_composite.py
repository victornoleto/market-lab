"""Iter 031 — VIX AND-composite VRP-primary (R-1 ∧ R-2):
skip new spread open ONLY when both axes fire simultaneously:

  * R-1: ``vix[i] >= vix_threshold`` for ``persistence_days`` consecutive bars
  * R-2: ``rolling_zscore(vix, z_window)[i] >= z_threshold``

Builds on iter 029 ``vrp_persistence.py`` (R-1 axis) and iter 030
``vrp_zscore.py`` (R-2 axis) by composing both gates with logical AND.
The intersection is strictly more permissive than either axis alone, so:

  * ``vix_threshold = 1e9`` → R-1 never fires → AND never fires →
    reproduces iter 026 exactly.
  * ``z_threshold = 1e9`` → R-2 never fires → AND never fires →
    reproduces iter 026 exactly.
  * Either reduction is a falsifiable property tested in
    ``tests/test_iter031_vix_and_composite.py``.

Mechanics
---------

Convention is identical to iter 020/026/028/029/030 — the internal
``overlay`` array records the **long-holder's** daily P&L (in fractions
of ``S_entry``); costs are charged as negative entries (long pays). The
strategy is then ``rf_daily + harvest_notional * (-overlay)``.

State machine (iter 031 specific):

  * ``OPEN`` — a position is currently held; daily MtM is computed; on
    the natural expiry/roll bar the position is closed (cost charged to
    long-holder) and a new one is opened **only if NOT
    (R-1(i) AND R-2(i))**. Otherwise the strategy transitions to
    ``HOLD-CASH``.
  * ``HOLD-CASH`` — no position; daily ``overlay`` contribution is 0;
    re-evaluation occurs every ``dte_days`` bars.

NaN z (warmup) → R-2 = False → AND = False → default-to-open. This
mirrors iter 029's persistence default-to-open during the persistence
warmup window.

Citations
---------
* `[volatility_trading, p.217]` — Sinclair (2013) ch. 8 §"Hedging short
  volatility positions": VIX < 35 entry filter (level component, R-1).
* `[volatility_trading, p.218]` — Sinclair §"VIX-VXV term structure":
  *sustained* high IV is the warning sign for short-vol writers
  (persistence + z-score motivation, R-2).
* `[volatility_trading, ch.3, p.41]` — VRP mechanics + SPX excess
  kurtosis 21.3 (capped-tail rationale).
* `[volatility_trading, p.39, p.58-59]` — VIX vol-of-vol + cone (z-score).
* `[volatility_trading, p.11]` — BSM pricing identity.
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
* Bondarenko (2014) QJF 4(3) §3 — *both* level AND persistence matter
  (explicit motivation for the AND-composite).
* Carr-Wu (2009) RFS 22(3) — VRP level/persistence/innovation
  decomposition; iter 031 uses level ∧ persistence axes intersection.
* Whaley (2009) JPM 35(3) — VIX innovation (z-score) characterization.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_020_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "020-2026-04-24-1850-put-spread-tail-hedge"
ITER_029_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "029-2026-04-24-2236-vix-persistence-vrp-primary"
ITER_030_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "030-2026-04-24-2259-vix-zscore-vrp-primary"
for p in (ITER_020_DIR, ITER_029_DIR, ITER_030_DIR):
    if str(p) not in sys.path:
        sys.path.append(str(p))

from put_spread_hedge import _price_put_spread  # noqa: E402
from vrp_persistence import is_persistent_high  # noqa: E402
from vrp_zscore import is_z_high  # noqa: E402


def is_and_composite_skip(
    vix: np.ndarray,
    z: np.ndarray,
    i: int,
    vix_threshold: float,
    persistence_days: int,
    z_threshold: float,
) -> bool:
    """True iff R-1(i) AND R-2(i) — the AND-composite of level+persistence and z-score.

    Falls back to False (default-to-open) whenever either axis cannot
    fire: insufficient persistence history (R-1 default-False) or NaN z
    (R-2 default-False). The composite is symmetric — either disabled
    axis kills the AND.

    Parameters
    ----------
    vix : np.ndarray
        Raw VIX series for the R-1 level check.
    z : np.ndarray
        Precomputed rolling-z-score series (NaN during warmup).
    i : int
        Bar index.
    vix_threshold, persistence_days : R-1 axis params (iter 029 helper).
    z_threshold : R-2 axis param (iter 030 helper).

    Returns
    -------
    True iff both axes fire; False otherwise.
    """
    return (
        is_persistent_high(vix, i, vix_threshold, persistence_days)
        and is_z_high(z, i, z_threshold)
    )


def compute_vrp_and_composite_returns(
    prices: pd.Series,
    iv_series: pd.Series,
    vix_zscore: pd.Series,
    *,
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
    """Daily fractional returns of the AND-composite-filtered VRP-primary portfolio.

    Identical to iter 030's ``compute_vrp_zscore_returns`` except the
    open-gate combines R-1 (persistence) and R-2 (z-score) via logical
    AND. Both axes default to False on insufficient data, so the
    composite is permissive whenever either signal is undefined.

    Setting ``vix_threshold = 1e9`` reproduces iter 026 exactly.
    Setting ``z_threshold = 1e9`` reproduces iter 026 exactly.
    Setting ``persistence_days = 1, vix_threshold = 0`` collapses R-1
    to "always fire" → AND collapses to R-2 alone (= iter 030).

    Parameters
    ----------
    prices, iv_series, vix_zscore : pd.Series
        Equity adj_close + IV (% units) + precomputed rolling-z-score.
        Aligned via inner-join.
    rf : float
        Annualised risk-free rate. Default 0.02.
    harvest_notional : float
        Non-negative scaling on the short-writer overlay.
    k_long_pct, k_short_pct, dte_days, iv_scale, cost_bps_per_roll :
        Inherited from iter 020/026/028/029/030.
    vix_threshold : float
        R-1 level threshold. Must be >= 0. Default 35 (Sinclair p.217).
    persistence_days : int
        R-1 persistence window. Must be >= 1. Default 3 (Bondarenko §3).
    z_threshold : float
        R-2 z-score threshold. Must be >= 0. Default 2 (Whaley 2009).

    Returns
    -------
    pd.Series of daily strategy returns aligned to inner-join index.

    Raises
    ------
    ValueError if any param bound is violated.
    """
    if harvest_notional < 0:
        raise ValueError(
            f"harvest_notional must be >= 0; got {harvest_notional}."
        )
    if vix_threshold < 0:
        raise ValueError(
            f"vix_threshold must be >= 0; got {vix_threshold}."
        )
    if persistence_days < 1:
        raise ValueError(
            f"persistence_days must be >= 1; got {persistence_days}."
        )
    if z_threshold < 0:
        raise ValueError(
            f"z_threshold must be >= 0; got {z_threshold}."
        )
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
        {
            "price": prices.astype(float),
            "iv_raw": iv_series.astype(float),
            "vix_z": vix_zscore.astype(float),
        },
        axis=1,
        join="inner",
    )
    aligned = aligned.dropna(subset=["price", "iv_raw"])
    n = len(aligned)
    if n < 2:
        raise ValueError(f"need >= 2 aligned bars, got {n}")

    prices_arr = aligned["price"].to_numpy()
    iv_raw_arr = aligned["iv_raw"].to_numpy()
    iv_priced_arr = iv_raw_arr * iv_scale / 100.0
    z_arr = aligned["vix_z"].to_numpy()
    dates = aligned.index

    rf_daily = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    overlay = np.zeros(n)
    cost_frac = cost_bps_per_roll / 10000.0
    T_0 = dte_days / 252.0

    position_open = False
    S_entry = 0.0
    K_long = 0.0
    K_short = 0.0
    expiry_idx = -1
    prev_value = 0.0

    # --- Bar 0 ---------------------------------------------------------
    if not is_and_composite_skip(
        iv_raw_arr, z_arr, 0,
        vix_threshold, persistence_days, z_threshold,
    ):
        position_open = True
        S_entry = float(prices_arr[0])
        K_long = k_long_pct * S_entry
        K_short = k_short_pct * S_entry
        expiry_idx = min(0 + dte_days, n - 1)
        sigma_0 = max(float(iv_priced_arr[0]), 1e-6)
        prev_value = _price_put_spread(
            S_entry, K_long, K_short, T_0, sigma_0, rf,
        )
        overlay[0] = -cost_frac
    else:
        expiry_idx = min(0 + dte_days, n - 1)

    for i in range(1, n):
        S_t = float(prices_arr[i])
        sigma_t = max(float(iv_priced_arr[i]), 1e-6)

        if position_open:
            T_remaining = max(0, expiry_idx - i) / 252.0
            current_value = _price_put_spread(
                S_t, K_long, K_short, T_remaining, sigma_t, rf,
            )
            overlay[i] = (current_value - prev_value) / S_entry

            if i >= expiry_idx and i < n - 1:
                overlay[i] -= cost_frac
                if not is_and_composite_skip(
                    iv_raw_arr, z_arr, i,
                    vix_threshold, persistence_days, z_threshold,
                ):
                    S_entry = S_t
                    K_long = k_long_pct * S_entry
                    K_short = k_short_pct * S_entry
                    expiry_idx = min(i + dte_days, n - 1)
                    prev_value = _price_put_spread(
                        S_entry, K_long, K_short, T_0, sigma_t, rf,
                    )
                else:
                    position_open = False
                    expiry_idx = min(i + dte_days, n - 1)
                    prev_value = 0.0
            else:
                prev_value = current_value
        else:
            if i >= expiry_idx and i < n - 1:
                if not is_and_composite_skip(
                    iv_raw_arr, z_arr, i,
                    vix_threshold, persistence_days, z_threshold,
                ):
                    position_open = True
                    S_entry = S_t
                    K_long = k_long_pct * S_entry
                    K_short = k_short_pct * S_entry
                    expiry_idx = min(i + dte_days, n - 1)
                    prev_value = _price_put_spread(
                        S_entry, K_long, K_short, T_0, sigma_t, rf,
                    )
                    overlay[i] = -cost_frac
                else:
                    expiry_idx = min(i + dte_days, n - 1)

    strategy = rf_daily + harvest_notional * (-overlay)
    return pd.Series(strategy, index=dates, name="vrp_and_composite_return")
