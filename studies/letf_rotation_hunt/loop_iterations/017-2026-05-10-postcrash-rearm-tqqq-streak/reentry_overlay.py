"""Post-crash re-arm overlay for iter 017.

Stacks a TIME-domain re-arm window onto iter 014's mechanism-mix-diverse
graded blend frame. The overlay strictly *adds* upgrade-gate activation
during a fixed-duration window opened by an OFF→ON master-signal
transition that follows a sufficiently long OFF stretch.

Mechanism (no look-ahead; all signals computable by close of day t):

  1. Track every transition where the master `on_signal` (vote-K=2 entry
     on QLD) flips OFF→ON at day t.
  2. If, at the flip, the prior contiguous OFF stretch lasted >= T_crash
     days, the day t qualifies as a "post-crash flip".
  3. The re-arm gate is 1 at day t and at the (d_arm - 1) subsequent days
     (i.e., d_arm consecutive days starting at the qualifying flip).
  4. After the strategy lag-shift (signals lagged 1 day inside the
     mechanism-mix returns helper), upgrade is applied at days
     t+1 ... t+d_arm — d_arm consecutive trading days of forced upgrade
     starting the day after the flip is detected.

Citations
---------
- [leverage_for_the_long_run, p.6-7, ch.3]: Husson-Trifoni — above MA
  positive autocorrelation/streaks; below MA seesawing. The MA flip-ON
  is the empirical regime onset for streak harvesting (PRIMARY).
- [leverage_for_the_long_run, p.4, ch.2]: "High volatility and seesawing
  action are the enemies of leverage while low volatility and streaks in
  performance are its friends."
- [stocks_on_the_move, p.98]: Clenow trend-strength (re-establishment of
  trend after long OFF stretch).
- [volatility_trading, p.58-60]: Sinclair vol cone (low realised-vol
  regime onset).
- [systematic_trading, p.212, ch.13]: Carver semi-automatic stop re-arm
  (conceptual time-domain memory analogue applied here to ENTRY leverage).
- [advances_fin_ml, p.208-211]: PBO via CSCV (mechanism-mix-diversity).
- [advances_fin_ml, p.222-223]: DSR cumulative n_trials.

Iter-local helper (`loop_iterations/017-.../`); does NOT modify shared
modules per LOOP_PROTOCOL §"Scope limits".
"""
from __future__ import annotations

import pandas as pd


def build_postcrash_rearm_gate(
    on_signal: pd.Series,
    t_crash: int,
    d_arm: int,
) -> pd.Series:
    """Return a 0/1 gate marking the re-arm window after qualifying flips.

    Parameters
    ----------
    on_signal:
        Master ON/OFF signal {0, 1, NaN}. NaN rows are treated as
        non-counting (not OFF, not ON) — the OFF-stretch counter does NOT
        accumulate during NaN warmup.
    t_crash:
        Minimum prior OFF-stretch length (in trading days) that qualifies a
        flip as post-crash. Must be > 0; a non-positive value disables the
        overlay (returns all-zero).
    d_arm:
        Re-arm window length in trading days, inclusive of the flip-detection
        day. Must be > 0; non-positive disables.

    Returns
    -------
    pd.Series
        Float series aligned to `on_signal.index` containing 0.0 / 1.0.
    """
    idx = on_signal.index
    if t_crash <= 0 or d_arm <= 0:
        return pd.Series(0.0, index=idx)

    valid = on_signal.notna()
    is_on = ((on_signal == 1.0) & valid).astype(int)
    is_off = ((on_signal == 0.0) & valid).astype(int)

    # OFF-stretch counter — accumulates within valid OFF runs only.
    # Group identifier increments at every change of is_on (or at NaN→valid
    # transitions); within each OFF run, cumsum of is_off gives the stretch.
    change = (is_on != is_on.shift(1)).astype(int)
    change.iloc[0] = 1
    grp = change.cumsum()
    off_stretch = is_off.groupby(grp).cumsum()

    # OFF→ON flip at day t with off_stretch[t-1] >= t_crash qualifies.
    is_on_prev = is_on.shift(1, fill_value=0)
    flip = (is_on == 1) & (is_on_prev == 0)
    off_stretch_prev = off_stretch.shift(1, fill_value=0)
    qualified = flip & (off_stretch_prev >= t_crash)

    # Re-arm gate = 1 if a qualified flip happened within the last d_arm
    # days (inclusive of today). Implemented as rolling sum of indicator.
    flip_ind = qualified.astype(int)
    rearm = flip_ind.rolling(window=d_arm, min_periods=1).sum() > 0
    return rearm.astype(float)


def diagnose_rearm_events(
    on_signal: pd.Series,
    t_crash: int,
    d_arm: int,
) -> dict:
    """Return diagnostic counts for KILL_LOOP and SUMMARY reporting.

    Counts the number of qualified flips, total active rearm days, and
    the activation percentage relative to the valid-signal window.
    """
    rearm = build_postcrash_rearm_gate(on_signal, t_crash, d_arm)
    valid = on_signal.notna()
    n_valid = int(valid.sum())
    if n_valid == 0:
        return {
            "n_qualified_flips": 0,
            "n_active_rearm_days": 0,
            "rearm_active_pct": 0.0,
            "t_crash": int(t_crash),
            "d_arm": int(d_arm),
        }

    is_on = ((on_signal == 1.0) & valid).astype(int)
    is_off = ((on_signal == 0.0) & valid).astype(int)
    change = (is_on != is_on.shift(1)).astype(int)
    change.iloc[0] = 1
    grp = change.cumsum()
    off_stretch = is_off.groupby(grp).cumsum()
    is_on_prev = is_on.shift(1, fill_value=0)
    flip = (is_on == 1) & (is_on_prev == 0)
    off_stretch_prev = off_stretch.shift(1, fill_value=0)
    qualified = flip & (off_stretch_prev >= t_crash)

    return {
        "n_qualified_flips": int(qualified.sum()),
        "n_active_rearm_days": int((rearm > 0).sum()),
        "rearm_active_pct": float(((rearm > 0) & valid).sum() / n_valid),
        "t_crash": int(t_crash),
        "d_arm": int(d_arm),
    }
