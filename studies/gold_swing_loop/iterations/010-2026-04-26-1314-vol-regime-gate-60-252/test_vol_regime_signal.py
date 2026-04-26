"""TDD tests for iter 010 — realized-vol regime gate (σ_60d > σ_252d).

Validates the signal primitives:
1. ``realized_vol`` — annualized rolling std of log returns
2. ``vol_regime_flag`` — binary flag {0, 1} based on σ_short > σ_long
3. ``vol_regime_position`` — long-only state (no shorts; flag IS position)

Plus a cross-lib parity check (pandas-rolling vs hand-rolled numpy).

Citations
---------
* `[volatility_trading, p.58-59]` — vol cone framework
* `[trading_systems_methods, p.131]` — KAMA Efficiency Ratio = stdev(C,n)/stdev(C,m)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ITER_DIR))

from run_backtest import (  # noqa: E402
    realized_vol,
    realized_vol_numpy,
    vol_regime_flag,
    vol_regime_position,
)


# ---------------------------------------------------------------------------
# realized_vol — annualized rolling std of log returns
# ---------------------------------------------------------------------------


def test_realized_vol_constant_returns_yields_zero():
    """If log returns are constant, σ = 0."""
    prices = pd.Series([100.0 * (1.001) ** i for i in range(300)],
                       index=pd.date_range("2020-01-01", periods=300, freq="D"))
    sigma = realized_vol(prices, window=60, ann_factor=252)
    # First 60 bars NaN (rolling window). After that, std of constant log returns = 0.
    valid = sigma.dropna()
    assert (valid.abs() < 1e-9).all(), f"expected zero σ for constant returns, got {valid.head()}"


def test_realized_vol_annualization_factor():
    """σ_annualized = σ_per_bar × sqrt(ann_factor). Daily bars use 252."""
    np.random.seed(42)
    rng = np.random.default_rng(42)
    log_rets = rng.normal(0.0, 0.01, size=400)  # 1% daily σ
    prices = pd.Series(100.0 * np.exp(np.cumsum(log_rets)),
                       index=pd.date_range("2020-01-01", periods=400, freq="D"))
    sigma = realized_vol(prices, window=252, ann_factor=252)
    valid = sigma.dropna()
    # Expected ann σ ≈ 0.01 × sqrt(252) ≈ 0.1587. Allow 30% tolerance for sample noise.
    expected = 0.01 * np.sqrt(252)
    assert abs(valid.iloc[-1] - expected) < 0.05, (
        f"expected ~{expected:.4f}, got {valid.iloc[-1]:.4f}"
    )


def test_realized_vol_pandas_numpy_parity():
    """Pandas rolling vs hand-rolled numpy must match within 1e-10."""
    rng = np.random.default_rng(7)
    log_rets = rng.normal(0.0, 0.01, size=500)
    prices = pd.Series(100.0 * np.exp(np.cumsum(log_rets)),
                       index=pd.date_range("2020-01-01", periods=500, freq="D"))
    sigma_pd = realized_vol(prices, window=60, ann_factor=252).dropna()
    sigma_np = realized_vol_numpy(prices.values, window=60, ann_factor=252)
    sigma_np_aligned = pd.Series(sigma_np, index=prices.index).dropna()
    diff = (sigma_pd - sigma_np_aligned).abs()
    assert (diff < 1e-10).all(), (
        f"pandas vs numpy parity failure: max diff = {diff.max():.2e}"
    )


# ---------------------------------------------------------------------------
# vol_regime_flag — σ_short > σ_long binary flag
# ---------------------------------------------------------------------------


def test_vol_regime_flag_binary_output():
    """Output is strictly {0, 1}; no NaN passes through to position."""
    rng = np.random.default_rng(1)
    log_rets = rng.normal(0.0, 0.01, size=400)
    prices = pd.Series(100.0 * np.exp(np.cumsum(log_rets)),
                       index=pd.date_range("2020-01-01", periods=400, freq="D"))
    flag = vol_regime_flag(prices, window_short=60, window_long=252, ann_factor=252)
    assert flag.dtype.kind in ("i", "u", "f"), f"unexpected dtype: {flag.dtype}"
    assert set(flag.unique().tolist()).issubset({0, 1}), f"non-binary values: {flag.unique()}"


def test_vol_regime_flag_short_window_warmup():
    """Bars before σ_long has enough data → flag MUST be 0 (no signal yet)."""
    rng = np.random.default_rng(2)
    log_rets = rng.normal(0.0, 0.01, size=400)
    prices = pd.Series(100.0 * np.exp(np.cumsum(log_rets)),
                       index=pd.date_range("2020-01-01", periods=400, freq="D"))
    flag = vol_regime_flag(prices, window_short=60, window_long=252, ann_factor=252)
    # First 251 bars: σ_long NaN, so cannot compare → flag must be 0.
    assert (flag.iloc[:251] == 0).all(), (
        "warmup period must be 0; "
        f"first non-zero index: {(flag.iloc[:251] != 0).idxmax() if (flag.iloc[:251] != 0).any() else 'none'}"
    )


def test_vol_regime_flag_fires_on_vol_spike():
    """When recent returns get more volatile, σ_60 rises above σ_252 → flag=1."""
    rng = np.random.default_rng(3)
    # First 252 bars: low vol (σ=0.005). Next 100 bars: high vol (σ=0.03).
    low_vol = rng.normal(0.0, 0.005, size=252)
    high_vol = rng.normal(0.0, 0.03, size=100)
    log_rets = np.concatenate([low_vol, high_vol])
    prices = pd.Series(100.0 * np.exp(np.cumsum(log_rets)),
                       index=pd.date_range("2020-01-01", periods=352, freq="D"))
    flag = vol_regime_flag(prices, window_short=60, window_long=252, ann_factor=252)
    # By bar 320 (60 bars into high-vol regime), σ_60 should clearly > σ_252.
    assert flag.iloc[320] == 1, (
        f"expected flag=1 deep into high-vol regime; got {flag.iloc[320]}"
    )


def test_vol_regime_flag_off_in_low_vol_regime():
    """Stable low-vol regime → σ_60 ≈ σ_252 → flag mostly 0 (or oscillates)."""
    rng = np.random.default_rng(4)
    log_rets = rng.normal(0.0, 0.01, size=600)  # constant vol
    prices = pd.Series(100.0 * np.exp(np.cumsum(log_rets)),
                       index=pd.date_range("2020-01-01", periods=600, freq="D"))
    flag = vol_regime_flag(prices, window_short=60, window_long=252, ann_factor=252)
    # In a stable-vol regime, flag fires on noise; expect roughly half on / half off.
    p_active = flag.iloc[252:].mean()
    assert 0.20 < p_active < 0.80, (
        f"stable-vol regime should give ~50% flag-on, got {p_active:.2%}"
    )


# ---------------------------------------------------------------------------
# vol_regime_position — long-only state machine (binary)
# ---------------------------------------------------------------------------


def test_vol_regime_position_long_only():
    """Position is exactly the flag (long-only); no shorts ever."""
    rng = np.random.default_rng(5)
    log_rets = rng.normal(0.0, 0.01, size=500)
    prices = pd.Series(100.0 * np.exp(np.cumsum(log_rets)),
                       index=pd.date_range("2020-01-01", periods=500, freq="D"))
    pos = vol_regime_position(prices, window_short=60, window_long=252, ann_factor=252)
    assert (pos >= 0).all(), f"long-only requires pos ≥ 0; min pos = {pos.min()}"
    assert set(pos.unique().tolist()).issubset({0.0, 1.0}), (
        f"non-binary position: {pos.unique()}"
    )


def test_vol_regime_position_zero_during_warmup():
    """Position must be 0 during σ_long warmup (no premature long entries)."""
    rng = np.random.default_rng(6)
    log_rets = rng.normal(0.0, 0.01, size=400)
    prices = pd.Series(100.0 * np.exp(np.cumsum(log_rets)),
                       index=pd.date_range("2020-01-01", periods=400, freq="D"))
    pos = vol_regime_position(prices, window_short=60, window_long=252, ann_factor=252)
    assert (pos.iloc[:251] == 0).all(), "no longs allowed in warmup"


# ---------------------------------------------------------------------------
# Sanity: the flag IS the entry/exit grammar — no |z|>kσ trigger
# ---------------------------------------------------------------------------


def test_vol_regime_no_zscore_trigger():
    """The signal contract: position is determined by σ_short vs σ_long,
    NOT by any |z|>k threshold. This is what sidesteps GS-7/9 entry-dilution.

    Real-world realization: under a *stationary* vol regime (constant σ
    drawn from the SAME distribution throughout), σ_60 ≈ σ_252 within
    sample noise — there is NO regime signal. Even very large price moves
    (high mean drift) do NOT trigger the flag, because the trigger reads
    σ-of-returns, not z-of-price. We verify with a high-drift constant-σ
    process: average flag exposure should be ~50% (pure noise around the
    null), NOT correlated with the drift magnitude.
    """
    rng = np.random.default_rng(101)
    n = 600
    drift = 0.005  # very large drift (~125% / 252 days = strong momentum)
    log_rets = rng.normal(drift, 0.01, size=n)  # constant σ=0.01
    prices = pd.Series(100.0 * np.exp(np.cumsum(log_rets)),
                       index=pd.date_range("2020-01-01", periods=n, freq="D"))
    pos = vol_regime_position(prices, window_short=60, window_long=252, ann_factor=252)
    # Under stationary σ, post-warmup flag exposure is bounded ~25-75% pure
    # noise (Bernoulli-like). The KEY claim: it does NOT track the drift
    # direction or magnitude — verified by checking that mean position is
    # in the noise band, not skewed by the strong drift.
    p_active = pos.iloc[252:].mean()
    assert 0.10 < p_active < 0.90, (
        f"stationary-σ regime should give noise-bounded p_active in [0.10, 0.90]; "
        f"got {p_active:.2%} — signal MAY be leaking drift/z-score info"
    )
