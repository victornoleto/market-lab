"""Independent reimplementation of post-crash rearm gate + PFV20 gate (iter 022).

Phase 4 — iter 017 focused validation/refinement. From-scratch implementation
of the iter 017 rearm primitive (algorithmically equivalent but structurally
distinct from `loop_iterations/017-.../reentry_overlay.py`) plus a NEW
post-flip realised-vol confirmation gate (PFV).

Algorithm parity target
-----------------------
The function `build_postcrash_rearm_gate_independent` is required to
produce **bit-exact identical** outputs to iter 017's
`build_postcrash_rearm_gate` for any (on_signal, t_crash, d_arm) triple.
Iter 022's `backtest.py` runs a hard-fail KILL_LOOP #8 on
`max(abs(diff))` between the two daily gate series.

Differences (intentional, do not affect outputs):
- Explicit Python loop instead of vectorised pandas groupby + rolling sum.
- numpy state encoding (`is_on`, `is_off`, `off_count`) instead of pandas
  Series + groupby.
- Single forward pass; no intermediate `change`/`grp`/`off_stretch_prev`
  series.

PFV gate (NEW)
--------------
`post_flip_vol_confirmation_gate` returns 1 on each day inside a rearm
window iff the **5d realised vol of the rearm-asset (QLD)** measured AT the
qualifying flip's first 5 trading days post-flip is **below** the trailing
1260-day (~5y) `pct_threshold`-percentile of the same 5d-realised-vol time
series. The gate is decided on day t+5 (look-ahead-free w.r.t. percentile
distribution: the percentile uses data up to t-1; the post-flip vol uses
days t..t+4 inclusive). Because the decision is known by close of day t+4,
the AND-combined rearm becomes effective from day t+5 onward (i.e., loses
the first 5 days of the rearm window). Activation% therefore drops vs the
unconditional rearm-only baseline (slot 5).

Citations
---------
- [leverage_for_the_long_run, p.6-7, ch.3]: Husson-Trifoni MA flip-on as
  empirical streak-window onset (motivates rearm primitive). PRIMARY.
- [leverage_for_the_long_run, p.4, ch.2]: streaks vs seesawing — low
  realised vol post-flip is the streak signature. (PFV motivation.)
- [volatility_trading, p.58-60]: Sinclair vol cone — percentile-based vol
  regime gate. (PFV citation.)
- [advances_fin_ml, p.208-211]: CSCV PBO via mechanism-mix-diversity.
- [advances_fin_ml, p.222-223]: DSR cumulative n_trials.

Iter-local helper (`loop_iterations/022-.../`); does NOT modify shared
modules per LOOP_PROTOCOL §"Scope limits".
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def build_postcrash_rearm_gate_independent(
    on_signal: pd.Series,
    t_crash: int,
    d_arm: int,
) -> pd.Series:
    """Independent reimpl of iter 017's `build_postcrash_rearm_gate`.

    Algorithm:
      1. Walk the on_signal one day at a time.
      2. Track `off_count`: contiguous OFF-days before today.
      3. On a flip day (today ON, yesterday OFF), if `off_count >= t_crash`,
         mark today and the next d_arm-1 days as rearm.
      4. Reset `off_count` after each flip; do NOT accumulate during NaN
         or ON days.

    Bit-exact equivalent to iter 017's vectorised version, validated by
    KILL_LOOP #8 inside iter 022's `backtest.py`.
    """
    idx = on_signal.index
    n = len(idx)
    if t_crash <= 0 or d_arm <= 0:
        return pd.Series(0.0, index=idx)

    on_arr = on_signal.values
    is_on = np.where(np.isnan(on_arr), 0, (on_arr == 1.0).astype(int))
    is_off = np.where(np.isnan(on_arr), 0, (on_arr == 0.0).astype(int))

    rearm = np.zeros(n, dtype=float)
    off_count = 0

    for i in range(n):
        prev_on = int(is_on[i - 1]) if i > 0 else 0
        # Detect OFF→ON flip and qualify by prior contiguous OFF stretch.
        if is_on[i] == 1 and prev_on == 0:
            if off_count >= t_crash:
                end = min(i + d_arm, n)
                rearm[i:end] = 1.0
        # Update off_count for next iteration.
        if is_off[i] == 1:
            off_count += 1
        elif is_on[i] == 1:
            off_count = 0
        # NaN day (is_on=0 and is_off=0): preserve off_count (do not
        # accumulate, do not reset) — matches iter 017's groupby semantics
        # where NaN days do not contribute to off_stretch but also do not
        # break the OFF-run identifier.

    return pd.Series(rearm, index=idx)


def diagnose_rearm_events_independent(
    on_signal: pd.Series,
    t_crash: int,
    d_arm: int,
) -> dict:
    """Diagnostic counts for KILL_LOOP and SUMMARY reporting (independent impl)."""
    rearm = build_postcrash_rearm_gate_independent(on_signal, t_crash, d_arm)
    valid = on_signal.notna()
    n_valid = int(valid.sum())
    if n_valid == 0:
        return {
            "n_qualified_flips": 0,
            "n_active_rearm_days": 0,
            "rearm_active_pct": 0.0,
            "t_crash": int(t_crash),
            "d_arm": int(d_arm),
            "impl": "independent",
        }

    n = len(on_signal)
    on_arr = on_signal.values
    is_on = np.where(np.isnan(on_arr), 0, (on_arr == 1.0).astype(int))
    is_off = np.where(np.isnan(on_arr), 0, (on_arr == 0.0).astype(int))
    qualified = 0
    off_count = 0
    for i in range(n):
        prev_on = int(is_on[i - 1]) if i > 0 else 0
        if is_on[i] == 1 and prev_on == 0:
            if off_count >= t_crash:
                qualified += 1
        if is_off[i] == 1:
            off_count += 1
        elif is_on[i] == 1:
            off_count = 0

    return {
        "n_qualified_flips": int(qualified),
        "n_active_rearm_days": int((rearm > 0).sum()),
        "rearm_active_pct": float(((rearm > 0) & valid).sum() / n_valid),
        "t_crash": int(t_crash),
        "d_arm": int(d_arm),
        "impl": "independent",
    }


def post_flip_vol_confirmation_gate(
    on_signal: pd.Series,
    asset_returns: pd.Series,
    t_crash: int,
    d_arm: int,
    confirm_window: int = 5,
    pct_window: int = 1260,
    pct_threshold: float = 0.20,
) -> pd.Series:
    """Return 0/1 PFV-AND-rearm gate: rearm fires only if post-flip vol confirms streak.

    Mechanism:
      1. For each qualifying flip at day t (per iter 017 rearm primitive),
         compute realised vol over days [t, t+confirm_window-1] inclusive
         (5d annualised vol of `asset_returns`).
      2. Compare to the `pct_threshold`-percentile of the trailing
         `pct_window` 5d-realised-vol distribution evaluated at day t-1
         (no look-ahead).
      3. If post-flip vol < trailing percentile, the flip is
         PFV-confirmed; rearm activates from day t+confirm_window through
         day t+d_arm-1 (length d_arm - confirm_window).
      4. If post-flip vol >= trailing percentile (regime is high-vol /
         seesawing), the flip is rejected — no rearm activation.

    The activation start delay (confirm_window days) is information-honest:
    the percentile reference uses data up to t-1, the post-flip vol uses
    days t..t+confirm_window-1; both are known by close of day
    t+confirm_window-1, so the gate switches on at t+confirm_window.

    Returns
    -------
    pd.Series
        Float series aligned to `on_signal.index`, values 0.0 / 1.0.
    """
    idx = on_signal.index
    n = len(idx)
    if t_crash <= 0 or d_arm <= 0 or confirm_window <= 0:
        return pd.Series(0.0, index=idx)
    if d_arm <= confirm_window:
        # Filter would zero out the entire rearm window.
        return pd.Series(0.0, index=idx)

    # 5d realised vol of asset_returns (annualised), aligned to on_signal idx.
    asset_aligned = asset_returns.reindex(idx)
    rolling_std = asset_aligned.rolling(window=confirm_window, min_periods=confirm_window).std()
    realised_vol = rolling_std * np.sqrt(252.0)

    # Trailing-percentile reference of the realised_vol series itself
    # (5d-vol distribution over trailing pct_window days). Lagged 1 day to
    # avoid look-ahead at the flip moment.
    pct_ref = realised_vol.rolling(window=pct_window, min_periods=pct_window // 4).quantile(
        pct_threshold
    )
    pct_ref_lagged = pct_ref.shift(1)

    on_arr = on_signal.values
    is_on = np.where(np.isnan(on_arr), 0, (on_arr == 1.0).astype(int))
    is_off = np.where(np.isnan(on_arr), 0, (on_arr == 0.0).astype(int))

    realised_vol_arr = realised_vol.values
    pct_ref_arr = pct_ref_lagged.values

    gate = np.zeros(n, dtype=float)
    off_count = 0

    for i in range(n):
        prev_on = int(is_on[i - 1]) if i > 0 else 0
        if is_on[i] == 1 and prev_on == 0:
            if off_count >= t_crash:
                # Post-flip vol is determined by close of day i+confirm_window-1.
                vol_eval_day = i + confirm_window - 1
                if vol_eval_day < n:
                    pf_vol = realised_vol_arr[vol_eval_day]
                    pct_ref_at_flip = pct_ref_arr[i]
                    if (
                        not np.isnan(pf_vol)
                        and not np.isnan(pct_ref_at_flip)
                        and pf_vol < pct_ref_at_flip
                    ):
                        # Activate rearm from day i+confirm_window
                        # through day i+d_arm-1 inclusive.
                        start = i + confirm_window
                        end = min(i + d_arm, n)
                        if start < end:
                            gate[start:end] = 1.0
        if is_off[i] == 1:
            off_count += 1
        elif is_on[i] == 1:
            off_count = 0

    return pd.Series(gate, index=idx)


def diagnose_pfv_events(
    on_signal: pd.Series,
    asset_returns: pd.Series,
    t_crash: int,
    d_arm: int,
    confirm_window: int = 5,
    pct_window: int = 1260,
    pct_threshold: float = 0.20,
) -> dict:
    """Diagnostic counts for PFV gate."""
    gate = post_flip_vol_confirmation_gate(
        on_signal=on_signal,
        asset_returns=asset_returns,
        t_crash=t_crash,
        d_arm=d_arm,
        confirm_window=confirm_window,
        pct_window=pct_window,
        pct_threshold=pct_threshold,
    )
    valid = on_signal.notna()
    n_valid = int(valid.sum())
    if n_valid == 0:
        return {
            "n_duration_qualified_flips": 0,
            "n_pfv_qualified_flips": 0,
            "n_active_rearm_days": 0,
            "rearm_active_pct": 0.0,
            "t_crash": int(t_crash),
            "d_arm": int(d_arm),
            "confirm_window": int(confirm_window),
            "pct_window": int(pct_window),
            "pct_threshold": float(pct_threshold),
        }

    asset_aligned = asset_returns.reindex(on_signal.index)
    rolling_std = asset_aligned.rolling(window=confirm_window, min_periods=confirm_window).std()
    realised_vol = (rolling_std * np.sqrt(252.0)).values
    pct_ref = (
        rolling_std.rolling(window=pct_window, min_periods=pct_window // 4)
        .quantile(pct_threshold)
        * np.sqrt(252.0)
    ).shift(1).values

    n = len(on_signal)
    on_arr = on_signal.values
    is_on = np.where(np.isnan(on_arr), 0, (on_arr == 1.0).astype(int))
    is_off = np.where(np.isnan(on_arr), 0, (on_arr == 0.0).astype(int))

    n_dur = 0
    n_pfv = 0
    off_count = 0
    for i in range(n):
        prev_on = int(is_on[i - 1]) if i > 0 else 0
        if is_on[i] == 1 and prev_on == 0:
            if off_count >= t_crash:
                n_dur += 1
                vol_eval_day = i + confirm_window - 1
                if vol_eval_day < n:
                    pf_vol = realised_vol[vol_eval_day]
                    pct_ref_at_flip = pct_ref[i]
                    if (
                        not np.isnan(pf_vol)
                        and not np.isnan(pct_ref_at_flip)
                        and pf_vol < pct_ref_at_flip
                    ):
                        n_pfv += 1
        if is_off[i] == 1:
            off_count += 1
        elif is_on[i] == 1:
            off_count = 0

    return {
        "n_duration_qualified_flips": int(n_dur),
        "n_pfv_qualified_flips": int(n_pfv),
        "n_active_rearm_days": int((gate > 0).sum()),
        "rearm_active_pct": float(((gate > 0) & valid).sum() / n_valid),
        "t_crash": int(t_crash),
        "d_arm": int(d_arm),
        "confirm_window": int(confirm_window),
        "pct_window": int(pct_window),
        "pct_threshold": float(pct_threshold),
    }
