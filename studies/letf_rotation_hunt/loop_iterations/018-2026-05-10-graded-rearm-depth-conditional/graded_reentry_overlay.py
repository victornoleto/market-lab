"""Graded depth-proportional rearm overlay for iter 018.

Extends iter 017's fixed-window rearm primitive to a graded variant in which
the harvest window length D_arm SCALES with the prior OFF stretch length
T_off observed at the qualifying flip. Tests whether deeper crashes warrant
proportionally longer recovery windows per
`[leverage_for_the_long_run, p.4-7, ch.2-3]` Husson-Trifoni — "longer
below-MA stretches → stronger above-MA streaks" thesis (depth-proportional
streak harvesting).

Mechanism (no look-ahead; all signals computable by close of day t):

  1. Track every transition where the master `on_signal` flips OFF→ON at
     day t. Let T_off(t) be the contiguous OFF-stretch length immediately
     preceding the flip (in trading days).
  2. If T_off(t) >= t_crash_min the flip qualifies as post-crash (same
     gating logic as iter 017's `build_postcrash_rearm_gate`).
  3. The graded D_arm at qualifying flip t is computed as:
        D_arm(t) = clamp(round(coefficient * T_off(t)), d_arm_min, d_arm_max)
     i.e., D_arm scales linearly with T_off, clamped to a pre-committed
     range to avoid degenerate or over-long windows.
  4. The rearm gate is 1 at days t, t+1, ..., t+D_arm(t)-1 (D_arm(t)
     consecutive days starting at the flip). After the strategy's standard
     1-day signal lag, upgrade applies at t+1 ... t+D_arm(t).

The key contrast vs iter 017 is **per-event D_arm(t)** instead of a fixed
constant D_arm. The clamp values are pre-committed in hypothesis.md.

Citations
---------
- [leverage_for_the_long_run, p.4-7, ch.2-3]: Husson-Trifoni — streaks-vs-
  seesawing asymmetry. Longer below-MA stretches → stronger above-MA
  streaks (PRIMARY).
- [leverage_for_the_long_run, p.7]: "performance over time has nothing to
  do with time itself, but rather: 1) trend, 2) streaks vs seesawing, 3)
  vol regime" — direct support for graded harvest length.
- [stocks_on_the_move, p.98]: Clenow trend re-establishment.
- [volatility_trading, p.58-60]: Sinclair vol cone.
- [systematic_trading, p.212, ch.13]: Carver re-arm hysteresis (time-domain
  memory analogue).
- [advances_fin_ml, p.208-211]: PBO via CSCV mechanism-mix-diversity.
- [advances_fin_ml, p.222-223]: DSR cumulative n_trials.

Iter-local helper (`loop_iterations/018-.../`); does NOT modify shared
modules per LOOP_PROTOCOL §"Scope limits".
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _compute_off_stretch(on_signal: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Helper: compute is_on, off_stretch series matching iter 017 semantics.

    Returns
    -------
    is_on : 0/1 series, NaN-aware (NaN warmup → 0).
    off_stretch : cumulative OFF-day count within each contiguous OFF run.
                  Resets at every is_on change.
    """
    valid = on_signal.notna()
    is_on = ((on_signal == 1.0) & valid).astype(int)
    is_off = ((on_signal == 0.0) & valid).astype(int)
    change = (is_on != is_on.shift(1)).astype(int)
    change.iloc[0] = 1
    grp = change.cumsum()
    off_stretch = is_off.groupby(grp).cumsum()
    return is_on, off_stretch


def build_graded_rearm_gate(
    on_signal: pd.Series,
    t_crash_min: int,
    coefficient: float,
    d_arm_min: int,
    d_arm_max: int,
) -> pd.Series:
    """Return a 0/1 gate marking the depth-proportional rearm windows.

    Parameters
    ----------
    on_signal:
        Master ON/OFF signal {0, 1, NaN}. NaN rows are treated as
        non-counting (not OFF, not ON).
    t_crash_min:
        Minimum prior OFF-stretch length (trading days) required for a flip
        to qualify as post-crash. Below threshold → flip ignored. Must be
        > 0; non-positive disables the overlay.
    coefficient:
        Linear multiplier mapping T_off → raw D_arm. E.g., 0.75 means
        "D_arm = 75% of the prior OFF stretch length". Must be > 0.
    d_arm_min:
        Lower clamp on D_arm(t) — minimum harvest length for any qualifying
        flip. Must be > 0.
    d_arm_max:
        Upper clamp on D_arm(t) — maximum harvest length. Must be >= d_arm_min.

    Returns
    -------
    pd.Series
        Float series aligned to `on_signal.index` containing 0.0 / 1.0.

    Notes
    -----
    Implementation: build a per-flip remaining-window counter that starts at
    D_arm(t) at the qualifying flip and decrements by 1 each subsequent day,
    saturating at 0. The gate is 1 wherever the counter > 0.
    """
    idx = on_signal.index
    if t_crash_min <= 0 or coefficient <= 0 or d_arm_min <= 0 or d_arm_max < d_arm_min:
        return pd.Series(0.0, index=idx)

    is_on, off_stretch = _compute_off_stretch(on_signal)

    # Detect OFF→ON flips (today ON, yesterday OFF or NaN — treated as not-on).
    is_on_prev = is_on.shift(1, fill_value=0)
    flip = (is_on == 1) & (is_on_prev == 0)
    off_stretch_prev = off_stretch.shift(1, fill_value=0)
    qualified = flip & (off_stretch_prev >= t_crash_min)

    # Compute D_arm(t) per qualifying flip.
    raw_d_arm = np.round(coefficient * off_stretch_prev).astype(int)
    clamped_d_arm = raw_d_arm.clip(lower=d_arm_min, upper=d_arm_max)
    # Zero out non-qualifying rows.
    d_arm_at_flip = clamped_d_arm.where(qualified, other=0)

    # Build a remaining-window counter via reverse iteration:
    # counter[t] = max(d_arm_at_flip[t], counter[t+1] - 1, 0)? No — forward.
    # Forward iteration: counter[t] = max(counter[t-1] - 1, d_arm_at_flip[t]).
    # Equivalently: gate = 1 when t is within [flip_t, flip_t + D_arm(flip_t) - 1].
    counter = np.zeros(len(d_arm_at_flip), dtype=int)
    d_vals = d_arm_at_flip.to_numpy()
    prev = 0
    for i, d in enumerate(d_vals):
        cur = max(prev - 1, 0)
        if d > 0:
            cur = max(cur, int(d))
        counter[i] = cur
        prev = cur

    gate = pd.Series((counter > 0).astype(float), index=idx)
    return gate


def diagnose_graded_rearm_events(
    on_signal: pd.Series,
    t_crash_min: int,
    coefficient: float,
    d_arm_min: int,
    d_arm_max: int,
) -> dict:
    """Return diagnostic counts for KILL_LOOP and SUMMARY reporting.

    Counts qualified flips, total active rearm days, activation %, and the
    distribution (mean/min/max) of per-event D_arm(t).
    """
    idx = on_signal.index
    n_valid = int(on_signal.notna().sum())
    if n_valid == 0 or t_crash_min <= 0 or coefficient <= 0:
        return {
            "n_qualified_flips": 0,
            "n_active_rearm_days": 0,
            "rearm_active_pct": 0.0,
            "t_crash_min": int(t_crash_min),
            "coefficient": float(coefficient),
            "d_arm_min": int(d_arm_min),
            "d_arm_max": int(d_arm_max),
            "d_arm_per_event_mean": 0.0,
            "d_arm_per_event_min": 0,
            "d_arm_per_event_max": 0,
        }

    is_on, off_stretch = _compute_off_stretch(on_signal)
    is_on_prev = is_on.shift(1, fill_value=0)
    flip = (is_on == 1) & (is_on_prev == 0)
    off_stretch_prev = off_stretch.shift(1, fill_value=0)
    qualified = flip & (off_stretch_prev >= t_crash_min)

    raw_d_arm = np.round(coefficient * off_stretch_prev).astype(int)
    clamped = raw_d_arm.clip(lower=d_arm_min, upper=d_arm_max)
    qualified_d_arm = clamped[qualified]

    gate = build_graded_rearm_gate(
        on_signal, t_crash_min, coefficient, d_arm_min, d_arm_max,
    )
    valid = on_signal.notna()
    n_active = int(((gate > 0) & valid).sum())

    if len(qualified_d_arm) > 0:
        d_mean = float(qualified_d_arm.mean())
        d_min = int(qualified_d_arm.min())
        d_max = int(qualified_d_arm.max())
    else:
        d_mean, d_min, d_max = 0.0, 0, 0

    return {
        "n_qualified_flips": int(qualified.sum()),
        "n_active_rearm_days": n_active,
        "rearm_active_pct": float(n_active / n_valid),
        "t_crash_min": int(t_crash_min),
        "coefficient": float(coefficient),
        "d_arm_min": int(d_arm_min),
        "d_arm_max": int(d_arm_max),
        "d_arm_per_event_mean": d_mean,
        "d_arm_per_event_min": d_min,
        "d_arm_per_event_max": d_max,
    }
