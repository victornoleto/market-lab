"""SPY drawdown-depth conditional rearm gate (iter 020).

Adds a depth filter to iter 017's post-crash rearm primitive: a
qualifying flip becomes "MDD-qualified" only if SPY trailing 200d max
drawdown at t-1 is at or below `-mdd_threshold` (e.g., -0.15). The
T_crash duration filter is unchanged from iter 017.

Mechanism (no look-ahead; all signals computable by close of day t):

  1. Track every transition where the master `on_signal` flips OFF→ON
     at day t and the prior contiguous OFF stretch lasted >= T_crash.
  2. NEW: at day t, compute SPY 200d trailing max drawdown using prices
     up to and including day t-1 only (lagged 1d to avoid look-ahead).
  3. If `mdd_200d[t-1] <= -mdd_threshold`, the flip is MDD-qualified.
  4. The rearm gate is 1 at day t and at the (D_arm - 1) subsequent
     trading days (D_arm consecutive days starting at the qualifying
     flip), identical to iter 017's primitive.

Citations
---------
- [leverage_for_the_long_run, p.4-7, ch.2-3]: Husson-Trifoni — high
  volatility / seesawing kills leverage; deeper drawdowns precede
  stronger streak harvest. PRIMARY.
- [regime_change, p.44-46, ch.4]: Chen-Tsang abnormal-regime (Regime 2)
  follows significant external events; MDD breach as deterministic
  regime-confirmation analogue.
- [regime_change, p.70-71, ch.5]: B-Strict decision rule (require
  posterior > 0.8 to conclude Regime 2); MDD threshold ≤ -15% is the
  deterministic analogue.
- [advances_fin_ml, p.208-211]: PBO via CSCV (mechanism-mix-diversity).

Iter-local helper (`loop_iterations/020-.../`); does NOT modify shared
modules per LOOP_PROTOCOL §"Scope limits".
"""
from __future__ import annotations

import pandas as pd


def compute_trailing_mdd(
    price_or_returns: pd.Series,
    window: int,
    is_returns: bool = True,
) -> pd.Series:
    """Return rolling-window max drawdown (signed, <= 0) per day.

    Computed from a daily compounded equity built off the input series.
    For each day t, the value is the minimum of (equity[s]/peak[s] - 1)
    over the window ending at t.

    Parameters
    ----------
    price_or_returns:
        Daily series of returns (default) or prices (if `is_returns=False`).
    window:
        Rolling window length in trading days (e.g., 200).
    is_returns:
        If True, treat input as daily returns and build cumulative equity.
        If False, treat input as raw prices.
    """
    if is_returns:
        equity = (1.0 + price_or_returns.fillna(0.0)).cumprod()
    else:
        equity = price_or_returns.astype(float)
    rolling_peak = equity.rolling(window=window, min_periods=1).max()
    dd = (equity / rolling_peak) - 1.0
    return dd.rolling(window=window, min_periods=1).min()


def build_mdd_gated_rearm_gate(
    on_signal: pd.Series,
    spy_returns: pd.Series,
    t_crash: int,
    d_arm: int,
    mdd_window: int,
    mdd_threshold: float,
) -> pd.Series:
    """Return 0/1 gate for the MDD-gated post-crash rearm window.

    Parameters
    ----------
    on_signal:
        Master ON/OFF signal {0, 1, NaN}.
    spy_returns:
        Daily SPY (or SPYSIM) returns. Used to compute trailing
        `mdd_window`-day max drawdown.
    t_crash:
        Minimum prior OFF-stretch length (in trading days) to qualify a
        flip. Must be > 0; non-positive disables (returns all-zero).
    d_arm:
        Re-arm window length in trading days. Must be > 0; non-positive
        disables.
    mdd_window:
        Trailing window for SPY MDD computation (e.g., 200).
    mdd_threshold:
        Positive depth threshold; MDD must be <= -mdd_threshold to
        qualify (e.g., 0.15 for ≤ -15%). A value <= 0 disables the depth
        filter (gate matches iter 017's unconditional T_crash filter).
    """
    idx = on_signal.index
    if t_crash <= 0 or d_arm <= 0:
        return pd.Series(0.0, index=idx)

    valid = on_signal.notna()
    is_on = ((on_signal == 1.0) & valid).astype(int)
    is_off = ((on_signal == 0.0) & valid).astype(int)

    change = (is_on != is_on.shift(1)).astype(int)
    change.iloc[0] = 1
    grp = change.cumsum()
    off_stretch = is_off.groupby(grp).cumsum()

    is_on_prev = is_on.shift(1, fill_value=0)
    flip = (is_on == 1) & (is_on_prev == 0)
    off_stretch_prev = off_stretch.shift(1, fill_value=0)
    duration_qualified = flip & (off_stretch_prev >= t_crash)

    # SPY MDD aligned to on_signal index, lagged 1 day (no look-ahead).
    spy_mdd = compute_trailing_mdd(spy_returns, mdd_window, is_returns=True)
    spy_mdd_aligned = spy_mdd.reindex(idx).ffill()
    spy_mdd_lagged = spy_mdd_aligned.shift(1)

    if mdd_threshold > 0:
        depth_qualified = spy_mdd_lagged <= -mdd_threshold
        qualified = duration_qualified & depth_qualified.fillna(False)
    else:
        qualified = duration_qualified

    flip_ind = qualified.astype(int)
    rearm = flip_ind.rolling(window=d_arm, min_periods=1).sum() > 0
    return rearm.astype(float)


def diagnose_mdd_gated_rearm_events(
    on_signal: pd.Series,
    spy_returns: pd.Series,
    t_crash: int,
    d_arm: int,
    mdd_window: int,
    mdd_threshold: float,
) -> dict:
    """Return diagnostic counts for KILL_LOOP and SUMMARY reporting."""
    idx = on_signal.index
    valid = on_signal.notna()
    n_valid = int(valid.sum())
    if n_valid == 0:
        return {
            "n_duration_qualified_flips": 0,
            "n_mdd_qualified_flips": 0,
            "n_active_rearm_days": 0,
            "rearm_active_pct": 0.0,
            "t_crash": int(t_crash),
            "d_arm": int(d_arm),
            "mdd_window": int(mdd_window),
            "mdd_threshold": float(mdd_threshold),
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
    duration_qualified = flip & (off_stretch_prev >= t_crash)

    spy_mdd = compute_trailing_mdd(spy_returns, mdd_window, is_returns=True)
    spy_mdd_aligned = spy_mdd.reindex(idx).ffill()
    spy_mdd_lagged = spy_mdd_aligned.shift(1)

    if mdd_threshold > 0:
        depth_qualified = spy_mdd_lagged <= -mdd_threshold
        qualified = duration_qualified & depth_qualified.fillna(False)
    else:
        qualified = duration_qualified

    rearm = build_mdd_gated_rearm_gate(
        on_signal=on_signal,
        spy_returns=spy_returns,
        t_crash=t_crash,
        d_arm=d_arm,
        mdd_window=mdd_window,
        mdd_threshold=mdd_threshold,
    )
    return {
        "n_duration_qualified_flips": int(duration_qualified.sum()),
        "n_mdd_qualified_flips": int(qualified.sum()),
        "n_active_rearm_days": int((rearm > 0).sum()),
        "rearm_active_pct": float(((rearm > 0) & valid).sum() / n_valid),
        "t_crash": int(t_crash),
        "d_arm": int(d_arm),
        "mdd_window": int(mdd_window),
        "mdd_threshold": float(mdd_threshold),
    }
