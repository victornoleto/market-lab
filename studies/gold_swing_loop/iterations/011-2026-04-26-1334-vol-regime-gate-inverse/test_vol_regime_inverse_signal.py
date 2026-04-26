"""TDD tests for iter 011 — inverse realized-vol regime gate (σ_60d < σ_252d).

Validates the signal primitives:
1. ``realized_vol`` — annualized rolling std of log returns (same as iter 010)
2. ``vol_regime_inverse_flag`` — binary flag {0, 1} based on σ_short < σ_long
3. ``vol_regime_inverse_position`` — long-only state (no shorts; flag IS position)

Plus a cross-lib parity check (pandas-rolling vs hand-rolled numpy) and a
**complementarity check** vs iter 010's flag (the two flags partition the
non-warmup index, modulo equal-σ ties).

Citations
---------
* `[volatility_trading, p.58-59]` — vol cone framework
* `[trading_systems_methods, p.131]` — KAMA Efficiency Ratio = stdev(C,n)/stdev(C,m)
* `[trading_systems_methods, p.13-14]` — metals = low-noise → trending = LOW vol
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ITER_010_DIR = ITER_DIR.parent / "010-2026-04-26-1314-vol-regime-gate-60-252"


def _load_module(label: str, path: Path):
    """Load a Python file as a uniquely-named module so iter 010 + iter 011's
    same-filename `run_backtest.py` don't shadow each other in sys.modules."""
    spec = importlib.util.spec_from_file_location(label, path)
    assert spec is not None and spec.loader is not None, f"failed to spec {path}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[label] = mod
    # Add the module's directory to sys.path during load so its own internal
    # imports (e.g., `from cost_models import ...`) resolve.
    parent = str(path.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    spec.loader.exec_module(mod)
    return mod


_ITER011 = _load_module("iter011_run_backtest", ITER_DIR / "run_backtest.py")
_ITER010 = _load_module("iter010_run_backtest", ITER_010_DIR / "run_backtest.py")

realized_vol = _ITER011.realized_vol
realized_vol_numpy = _ITER011.realized_vol_numpy
vol_regime_inverse_flag = _ITER011.vol_regime_inverse_flag
vol_regime_inverse_position = _ITER011.vol_regime_inverse_position
iter010_flag = _ITER010.vol_regime_flag


# ---------------------------------------------------------------------------
# realized_vol — sanity (same primitive as iter 010; replicate critical tests)
# ---------------------------------------------------------------------------


def test_realized_vol_constant_returns_yields_zero():
    """If log returns are constant, σ = 0."""
    prices = pd.Series([100.0 * (1.001) ** i for i in range(300)],
                       index=pd.date_range("2020-01-01", periods=300, freq="D"))
    sigma = realized_vol(prices, window=60, ann_factor=252)
    valid = sigma.dropna()
    assert (valid.abs() < 1e-9).all(), f"expected zero σ for constant returns, got {valid.head()}"


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
# vol_regime_inverse_flag — σ_short < σ_long binary flag
# ---------------------------------------------------------------------------


def test_inverse_flag_binary_output():
    """Output is strictly {0, 1}; no NaN passes through to position."""
    rng = np.random.default_rng(1)
    log_rets = rng.normal(0.0, 0.01, size=400)
    prices = pd.Series(100.0 * np.exp(np.cumsum(log_rets)),
                       index=pd.date_range("2020-01-01", periods=400, freq="D"))
    flag = vol_regime_inverse_flag(prices, window_short=60, window_long=252, ann_factor=252)
    assert flag.dtype.kind in ("i", "u", "f"), f"unexpected dtype: {flag.dtype}"
    assert set(flag.unique().tolist()).issubset({0, 1}), f"non-binary values: {flag.unique()}"


def test_inverse_flag_warmup_zero():
    """Bars before σ_long has enough data → flag MUST be 0 (no signal yet)."""
    rng = np.random.default_rng(2)
    log_rets = rng.normal(0.0, 0.01, size=400)
    prices = pd.Series(100.0 * np.exp(np.cumsum(log_rets)),
                       index=pd.date_range("2020-01-01", periods=400, freq="D"))
    flag = vol_regime_inverse_flag(prices, window_short=60, window_long=252, ann_factor=252)
    assert (flag.iloc[:251] == 0).all(), (
        "warmup period must be 0; "
        f"first non-zero index: {(flag.iloc[:251] != 0).idxmax() if (flag.iloc[:251] != 0).any() else 'none'}"
    )


def test_inverse_flag_fires_on_vol_compression():
    """When recent returns get LESS volatile than past, σ_60 < σ_252 → flag=1.

    First 252 bars high vol (σ=0.03). Next 100 bars low vol (σ=0.005).
    By bar 320 (60 bars into low-vol regime), σ_60 should clearly < σ_252.
    """
    rng = np.random.default_rng(3)
    high_vol = rng.normal(0.0, 0.03, size=252)
    low_vol = rng.normal(0.0, 0.005, size=100)
    log_rets = np.concatenate([high_vol, low_vol])
    prices = pd.Series(100.0 * np.exp(np.cumsum(log_rets)),
                       index=pd.date_range("2020-01-01", periods=352, freq="D"))
    flag = vol_regime_inverse_flag(prices, window_short=60, window_long=252, ann_factor=252)
    assert flag.iloc[320] == 1, (
        f"expected flag=1 deep into low-vol regime; got {flag.iloc[320]}"
    )


def test_inverse_flag_off_during_vol_expansion():
    """When recent returns get MORE volatile than past, σ_60 > σ_252 → flag=0
    (the inverse of iter 010's case).
    """
    rng = np.random.default_rng(31)
    low_vol = rng.normal(0.0, 0.005, size=252)
    high_vol = rng.normal(0.0, 0.03, size=100)
    log_rets = np.concatenate([low_vol, high_vol])
    prices = pd.Series(100.0 * np.exp(np.cumsum(log_rets)),
                       index=pd.date_range("2020-01-01", periods=352, freq="D"))
    flag = vol_regime_inverse_flag(prices, window_short=60, window_long=252, ann_factor=252)
    # Deep into the high-vol-expansion regime (after 60 bars of high vol),
    # the inverse signal must be OFF (σ_short > σ_long, not <).
    assert flag.iloc[320] == 0, (
        f"expected flag=0 deep into vol-expansion regime; got {flag.iloc[320]}"
    )


# ---------------------------------------------------------------------------
# vol_regime_inverse_position — long-only state machine (binary)
# ---------------------------------------------------------------------------


def test_inverse_position_long_only():
    """Position is exactly the flag (long-only); no shorts ever."""
    rng = np.random.default_rng(5)
    log_rets = rng.normal(0.0, 0.01, size=500)
    prices = pd.Series(100.0 * np.exp(np.cumsum(log_rets)),
                       index=pd.date_range("2020-01-01", periods=500, freq="D"))
    pos = vol_regime_inverse_position(prices, window_short=60, window_long=252, ann_factor=252)
    assert (pos >= 0).all(), f"long-only requires pos ≥ 0; min pos = {pos.min()}"
    assert set(pos.unique().tolist()).issubset({0.0, 1.0}), (
        f"non-binary position: {pos.unique()}"
    )


def test_inverse_position_zero_during_warmup():
    """Position must be 0 during σ_long warmup."""
    rng = np.random.default_rng(6)
    log_rets = rng.normal(0.0, 0.01, size=400)
    prices = pd.Series(100.0 * np.exp(np.cumsum(log_rets)),
                       index=pd.date_range("2020-01-01", periods=400, freq="D"))
    pos = vol_regime_inverse_position(prices, window_short=60, window_long=252, ann_factor=252)
    assert (pos.iloc[:251] == 0).all(), "no longs allowed in warmup"


# ---------------------------------------------------------------------------
# Complementarity vs iter 010 — the structural binding
# ---------------------------------------------------------------------------


def test_complementarity_vs_iter010_flag():
    """Iter 010 flag (σ_60 > σ_252) XOR iter 011 flag (σ_60 < σ_252) = 1
    on every non-warmup bar (modulo equal-σ ties, vanishingly rare).

    This proves the two iters DO partition the regime space — they are
    not testing the same hypothesis with different parameters; they are
    the two halves of a binary classification.
    """
    rng = np.random.default_rng(11)
    log_rets = rng.normal(0.0, 0.01, size=600)
    prices = pd.Series(100.0 * np.exp(np.cumsum(log_rets)),
                       index=pd.date_range("2020-01-01", periods=600, freq="D"))
    f10 = iter010_flag(prices, window_short=60, window_long=252, ann_factor=252)  # noqa: F405
    f11 = vol_regime_inverse_flag(prices, window_short=60, window_long=252, ann_factor=252)
    # Drop warmup (first 251 bars: both flags are 0 by warmup guard).
    f10_post = f10.iloc[251:]
    f11_post = f11.iloc[251:]
    # XOR must be 1 except at exact-equality bars (random data: never).
    overlap = (f10_post & f11_post).sum()
    both_off = ((f10_post == 0) & (f11_post == 0)).sum()
    assert overlap == 0, (
        f"iter 010 and iter 011 cannot BOTH be active on the same bar; got {overlap}"
    )
    # both_off > 0 only on equal-σ ties — vanishingly rare on random data.
    # Allow up to 1 tie to remain tolerant of float precision.
    assert both_off <= 1, (
        f"iter 010 and iter 011 BOTH off on {both_off} bars (expected 0; equal-σ ties)"
    )


# ---------------------------------------------------------------------------
# Sanity: the flag IS the entry/exit grammar — no |z|>kσ trigger
# ---------------------------------------------------------------------------


def test_inverse_no_zscore_trigger():
    """Position is determined by σ_short < σ_long, NOT by any |z|>k threshold.

    Under stationary σ, σ_60 ≈ σ_252 within sample noise; the inverse flag
    should fire ~50% of the time bounded by sample noise. KEY claim: it
    does NOT track drift direction or magnitude — verified by checking
    that mean position is in the noise band, not skewed by strong drift.
    """
    rng = np.random.default_rng(101)
    n = 600
    drift = 0.005
    log_rets = rng.normal(drift, 0.01, size=n)
    prices = pd.Series(100.0 * np.exp(np.cumsum(log_rets)),
                       index=pd.date_range("2020-01-01", periods=n, freq="D"))
    pos = vol_regime_inverse_position(prices, window_short=60, window_long=252, ann_factor=252)
    p_active = pos.iloc[252:].mean()
    assert 0.10 < p_active < 0.90, (
        f"stationary-σ regime should give noise-bounded p_active in [0.10, 0.90]; "
        f"got {p_active:.2%}"
    )
