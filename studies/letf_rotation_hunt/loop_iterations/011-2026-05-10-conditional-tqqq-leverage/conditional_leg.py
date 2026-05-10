"""Conditional ON-leg leverage scaling — iter 011 helper.

Substitutes TQQQSIM (3× NDX) for QLDSIM (2× NDX) only when an upgrade gate
fires. The K=2 entry signal still gates ON vs OFF; the upgrade gate gates
QLD vs TQQQ within the ON state. When ON state is OFF (defensive), the
strategy is in OFF leg (typically ZROZSIM) regardless of upgrade gate.

Citations
---------
- [leverage_for_the_long_run, ch.4-5, p.40-60]: LRS leverage scaling — leverage
  pumps when trend is firm AND vol is low.
- [stocks_on_the_move, p.98]: Clenow trend-strength filter (full vote count
  is the cleanest "high conviction" signal).
- [volatility_trading, p.58-60]: Sinclair vol cone — lowest realised-vol
  percentile = pump leverage regime.

This helper is iter-local (`loop_iterations/011-.../`). It does NOT modify any
study-shared module per LOOP_PROTOCOL §"Scope limits".
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.signals import (
    ar1_coefficient,
    realized_vol_gate,
    sma_gate,
    vote_of_k,
)


# ---------------------------------------------------------------------------
# Vote-count helpers (4 individual signals — same as iter 022 winner)
# ---------------------------------------------------------------------------


def _individual_signals(
    prices: pd.Series,
    returns: pd.Series,
    sma_long: int = 250,
    sma_short: int = 100,
    vol_window: int = 21,
    vol_threshold: float = 0.40,
    ar_window: int = 30,
) -> list[pd.Series]:
    """Return the 4 binary signals used by the iter 022 winner vote-K=2."""
    s1 = sma_gate(prices, period=sma_long)
    s2 = sma_gate(prices, period=sma_short)
    s3 = realized_vol_gate(returns, window=vol_window, threshold=vol_threshold)
    ar1 = ar1_coefficient(returns, window=ar_window)
    s4 = (ar1 > 0).astype(float)
    s4[ar1.isna()] = np.nan
    return [s1, s2, s3, s4]


def entry_signal_K2(prices: pd.Series, returns: pd.Series) -> pd.Series:
    """K=2 entry signal — exact iter 022 winner vote-of-K replica."""
    return vote_of_k(_individual_signals(prices, returns), k=2)


def upgrade_signal_K4(prices: pd.Series, returns: pd.Series) -> pd.Series:
    """Upgrade gate: 1 when ALL 4 individual signals are bullish (K=4 of 4).

    Strictly stronger than K=2 — when this fires, the entry signal is also
    on. Captures the highest-conviction risk-on regimes within the iter 022
    winner architecture.

    Returns
    -------
    pd.Series
        {0, 1, NaN}. NaN propagated from any input NaN (warmup max(SMAs) =
        250 days).
    """
    return vote_of_k(_individual_signals(prices, returns), k=4)


def upgrade_signal_lowvol25(
    returns: pd.Series,
    vol_window: int = 21,
    pct_window: int = 1260,
    pct_threshold: float = 0.25,
) -> pd.Series:
    """Upgrade gate: 1 when realised vol_21d is in the lowest pct_threshold
    of its trailing pct_window-day distribution (defaults: 21d vol, 5y window,
    25th percentile).

    `[volatility_trading, p.58-60]` Sinclair: low realised-vol percentile
    regimes are mean-reverting and structurally favorable for added leverage.

    Parameters
    ----------
    returns:
        Daily simple returns of the underlying (e.g., QLD return).
    vol_window:
        Rolling sigma window in days. Default 21 (matches the 40% binary
        gate inside the K=2 vote — same raw input, different metric).
    pct_window:
        Trailing distribution window. Default 1260 (5y).
    pct_threshold:
        Percentile bound; gate fires when current vol < this percentile.
        Default 0.25.

    Returns
    -------
    pd.Series
        {0, 1, NaN}. NaN during warmup (vol_window + pct_window - 1 bars).
    """
    sigma = returns.rolling(vol_window, min_periods=vol_window).std() * np.sqrt(252.0)
    pct_rank = sigma.rolling(pct_window, min_periods=pct_window).rank(pct=True)
    gate = (pct_rank < pct_threshold).astype(float)
    gate[pct_rank.isna()] = np.nan
    return gate


def combine_AND(a: pd.Series, b: pd.Series) -> pd.Series:
    """Logical AND of two binary signals; NaN propagated from either input."""
    df = pd.concat({"a": a, "b": b}, axis=1)
    out = ((df["a"] == 1.0) & (df["b"] == 1.0)).astype(float)
    out[df.isna().any(axis=1)] = np.nan
    return out


def combine_OR(a: pd.Series, b: pd.Series) -> pd.Series:
    """Logical OR of two binary signals; NaN propagated from either input."""
    df = pd.concat({"a": a, "b": b}, axis=1)
    out = ((df["a"] == 1.0) | (df["b"] == 1.0)).astype(float)
    out[df.isna().any(axis=1)] = np.nan
    return out


# ---------------------------------------------------------------------------
# Strategy returns: QLD/TQQQ swap conditional on upgrade gate
# ---------------------------------------------------------------------------


def build_conditional_strategy_returns(
    on_signal: pd.Series,
    qld_returns: pd.Series,
    tqqq_returns: pd.Series,
    off_returns: pd.Series,
    upgrade_gate: pd.Series,
) -> pd.Series:
    """Swap QLDSIM ↔ TQQQSIM in the ON state conditional on upgrade gate.

    Behavior (all signals lagged 1 day):
      on_signal = 1 AND upgrade = 1 → tqqq_returns
      on_signal = 1 AND upgrade = 0 → qld_returns
      on_signal = 1 AND upgrade NaN → qld_returns (warmup fallback to baseline)
      on_signal = 0                  → off_returns (defensive — upgrade ignored)

    Parameters
    ----------
    on_signal:
        K=2 entry gate (exact iter 022 winner replica).
    qld_returns, tqqq_returns:
        Daily simple returns of QLDSIM and TQQQSIM.
    off_returns:
        Daily simple returns of OFF leg (typically ZROZSIM).
    upgrade_gate:
        Binary {0, 1, NaN} signal; 1 means use TQQQ during ON state.

    Returns
    -------
    pd.Series
        Strategy daily returns. Index = aligned business days (rows where
        all required return streams + on_signal are non-NaN).
    """
    aligned = pd.concat({
        "on_sig": on_signal.shift(1),
        "upg": upgrade_gate.shift(1),
        "ret_qld": qld_returns,
        "ret_tqqq": tqqq_returns,
        "ret_off": off_returns,
    }, axis=1).dropna(subset=["ret_qld", "ret_tqqq", "ret_off"])

    on_state = aligned["on_sig"].fillna(0.0)
    # Default ON-leg = QLD; upgrade NaN treated as no-upgrade.
    upg = aligned["upg"].fillna(0.0)

    on_qld = (on_state == 1.0) & (upg != 1.0)
    on_tqqq = (on_state == 1.0) & (upg == 1.0)
    off_state = on_state != 1.0

    out = pd.Series(0.0, index=aligned.index)
    out[on_qld] = aligned.loc[on_qld, "ret_qld"]
    out[on_tqqq] = aligned.loc[on_tqqq, "ret_tqqq"]
    out[off_state] = aligned.loc[off_state, "ret_off"]
    return out


def conditional_turnover(
    on_signal: pd.Series,
    upgrade_gate: pd.Series,
) -> float:
    """Approximate annualised turnover from ON↔OFF flips + QLD↔TQQQ flips.

    Each ON↔OFF flip = 100% turnover (whole portfolio swap from leveraged
    equity to bond/cash). Each QLD↔TQQQ flip while ON = 100% turnover (full
    swap of the ON leg).
    """
    on_lag = on_signal.shift(1).fillna(0.0)
    upg_lag = upgrade_gate.shift(1).fillna(0.0)

    state = on_lag * (1 + upg_lag)  # 0=off, 1=on-qld, 2=on-tqqq
    flips = (state.diff().abs() > 0).astype(int)
    n_years = len(state) / 252.0
    if n_years <= 0:
        return 0.0
    return float(flips.sum() / n_years)
