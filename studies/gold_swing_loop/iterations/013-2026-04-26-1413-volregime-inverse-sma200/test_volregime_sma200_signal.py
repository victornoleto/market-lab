"""TDD tests for iter 013 — inverse vol-regime gate AND close > SMA(200).

Validates:
1. ``sma_simple`` — pandas rolling mean vs hand-rolled numpy parity (G7 anchor).
2. ``vol_regime_inverse_with_sma200_flag`` returns 0 in warmup and 0 when
   either condition is missing.
3. Subset relation: new flag is a SUBSET of iter 011's flag
   (every bar with new_flag=1 must also have iter011_flag=1).
4. Constructed series with controlled vol + price regime → flag fires
   ONLY when both conditions hold.

Citations
---------
* `[short_term_trading_strategies, p.106]` — Connors SMA(200) regime gate
* `[volatility_trading, p.58-59]` — Sinclair vol cone (iter 011 base)
* `[trading_systems_methods, p.131]` — Kaufman ER = stdev(C,n)/stdev(C,m)
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ITER_011_DIR = ITER_DIR.parent / "011-2026-04-26-1334-vol-regime-gate-inverse"


def _load_module(label: str, path: Path):
    """Load a Python file as a uniquely-named module so iter 011 + iter 013's
    same-filename ``run_backtest.py`` don't shadow each other in sys.modules."""
    spec = importlib.util.spec_from_file_location(label, path)
    assert spec is not None and spec.loader is not None, f"failed to spec {path}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[label] = mod
    parent = str(path.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    spec.loader.exec_module(mod)
    return mod


_ITER013 = _load_module("iter013_run_backtest", ITER_DIR / "run_backtest.py")
_ITER011 = _load_module("iter011_run_backtest", ITER_011_DIR / "run_backtest.py")

sma_simple = _ITER013.sma_simple
sma_simple_numpy = _ITER013.sma_simple_numpy
vol_regime_inverse_with_sma200_flag = _ITER013.vol_regime_inverse_with_sma200_flag
vol_regime_inverse_with_sma200_position = _ITER013.vol_regime_inverse_with_sma200_position
realized_vol = _ITER013.realized_vol  # re-exported from iter 011 primitive
iter011_flag = _ITER011.vol_regime_inverse_flag


# ---------------------------------------------------------------------------
# sma_simple — pandas / numpy parity (G7 anchor for the new primitive)
# ---------------------------------------------------------------------------


def test_sma_simple_basic():
    """SMA of constant series equals the constant after warmup."""
    prices = pd.Series([100.0] * 300,
                       index=pd.date_range("2020-01-01", periods=300, freq="D"))
    sma = sma_simple(prices, window=200)
    valid = sma.dropna()
    assert (valid - 100.0).abs().max() < 1e-9


def test_sma_simple_pandas_numpy_parity():
    """SMA pandas vs hand-rolled numpy must agree to 1e-10 (G7 anchor)."""
    rng = np.random.default_rng(13)
    prices = pd.Series(
        100.0 * np.exp(np.cumsum(rng.normal(0.0, 0.01, size=400))),
        index=pd.date_range("2020-01-01", periods=400, freq="D"),
    )
    sma_pd = sma_simple(prices, window=200).dropna()
    sma_np = sma_simple_numpy(prices.values, window=200)
    sma_np_aligned = pd.Series(sma_np, index=prices.index).dropna()
    common = sma_pd.index.intersection(sma_np_aligned.index)
    diff = (sma_pd.loc[common] - sma_np_aligned.loc[common]).abs().max()
    assert diff < 1e-10, f"pandas-numpy SMA parity drift: {diff}"


def test_sma_simple_warmup_returns_nan():
    """First (window-1) bars must be NaN."""
    prices = pd.Series([100.0 + i for i in range(250)],
                       index=pd.date_range("2020-01-01", periods=250, freq="D"))
    sma = sma_simple(prices, window=200)
    assert sma.iloc[:199].isna().all()
    assert sma.iloc[199:].notna().all()


# ---------------------------------------------------------------------------
# vol_regime_inverse_with_sma200_flag — semantic correctness
# ---------------------------------------------------------------------------


def test_flag_warmup_is_zero():
    """During warmup (before σ_252 OR SMA_200 are defined) flag must be 0."""
    rng = np.random.default_rng(13)
    prices = pd.Series(
        100.0 * np.exp(np.cumsum(rng.normal(0.0001, 0.01, size=400))),
        index=pd.date_range("2010-01-01", periods=400, freq="D"),
    )
    flag = vol_regime_inverse_with_sma200_flag(prices)
    # First 252 bars: σ_252 undefined → flag must be 0.
    assert (flag.iloc[:252] == 0).all()


def test_flag_zero_when_below_sma200_even_if_inverse_vol():
    """Construct a price series where σ_60<σ_252 holds but price<SMA(200) →
    flag must be 0 (the new gate's whole purpose).

    Strategy: build a series with high early vol that compresses + drifts
    DOWN. σ_60<σ_252 should hold for the back half, but price stays below
    SMA(200) (which is dominated by the higher early prices).
    """
    n = 600
    idx = pd.date_range("2010-01-01", periods=n, freq="D")
    # First 200 bars: high vol oscillation around 100; back 400 bars:
    # quiet drift down from 90 to 70.
    rng = np.random.default_rng(42)
    early = 100.0 + rng.normal(0.0, 5.0, size=200).cumsum() * 0.05
    late_starts = early[-1]
    late = late_starts + np.linspace(0, -25.0, 400) + rng.normal(
        0.0, 0.05, size=400,
    )
    prices = pd.Series(np.concatenate([early, late]), index=idx)

    flag = vol_regime_inverse_with_sma200_flag(prices)
    sma200 = sma_simple(prices, window=200)
    sigma_60 = realized_vol(prices, window=60, ann_factor=252)
    sigma_252 = realized_vol(prices, window=252, ann_factor=252)

    # In the back half, σ_60 < σ_252 should hold (quiet drift).
    back_idx = prices.index[400:]
    inverse_holds = (sigma_60.loc[back_idx] < sigma_252.loc[back_idx]).fillna(False)
    below_sma = (prices.loc[back_idx] < sma200.loc[back_idx]).fillna(False)
    # There MUST be at least some bars where both inverse AND price<SMA(200).
    bear_low_vol_count = int((inverse_holds & below_sma).sum())
    # Flag must be 0 on EVERY bar where price < SMA(200), even when σ inverse holds.
    flag_in_bear_lowvol = flag.loc[back_idx][inverse_holds & below_sma]
    assert (flag_in_bear_lowvol == 0).all(), (
        f"flag fired on {(flag_in_bear_lowvol == 1).sum()} of {bear_low_vol_count} "
        "bear-low-vol bars; SMA(200) gate not enforced"
    )
    # Sanity: there were genuinely some bear-low-vol bars (constructed to be).
    assert bear_low_vol_count > 0, (
        "test setup degenerate: no bear-low-vol bars present in back half"
    )


def test_flag_one_when_both_conditions_hold():
    """Construct a price series where σ_60<σ_252 AND price>SMA(200): flag=1."""
    # Quiet uptrend after a noisy start.
    n = 600
    idx = pd.date_range("2010-01-01", periods=n, freq="D")
    rng = np.random.default_rng(7)
    # First 200: noisy 100. Back 400: quiet drift UP from 100 to 130.
    early = 100.0 + rng.normal(0.0, 3.0, size=200).cumsum() * 0.05
    late_starts = early[-1]
    late = late_starts + np.linspace(0, 30.0, 400) + rng.normal(
        0.0, 0.05, size=400,
    )
    prices = pd.Series(np.concatenate([early, late]), index=idx)

    flag = vol_regime_inverse_with_sma200_flag(prices)
    sma200 = sma_simple(prices, window=200)
    sigma_60 = realized_vol(prices, window=60, ann_factor=252)
    sigma_252 = realized_vol(prices, window=252, ann_factor=252)

    back_idx = prices.index[400:]
    inverse_holds = (sigma_60.loc[back_idx] < sigma_252.loc[back_idx]).fillna(False)
    above_sma = (prices.loc[back_idx] > sma200.loc[back_idx]).fillna(False)
    bull_low_vol = inverse_holds & above_sma
    n_bull_low_vol = int(bull_low_vol.sum())
    assert n_bull_low_vol > 0, "test setup degenerate: no bull-low-vol bars"

    # Every bar where (σ inverse AND price>SMA200) must have flag=1.
    flag_in_bull_lowvol = flag.loc[back_idx][bull_low_vol]
    assert (flag_in_bull_lowvol == 1).all(), (
        f"flag missed {(flag_in_bull_lowvol == 0).sum()}/{n_bull_low_vol} "
        "bull-low-vol bars"
    )


def test_flag_subset_of_iter_011():
    """New flag MUST be a subset of iter 011's flag (no new fires; only
    removals from iter 011's set). Bar-by-bar: every bar with new_flag=1
    must have iter011_flag=1."""
    rng = np.random.default_rng(2026)
    log_ret = rng.normal(0.0, 0.012, size=1500)
    prices = pd.Series(
        100.0 * np.exp(np.cumsum(log_ret)),
        index=pd.date_range("2010-01-01", periods=1500, freq="D"),
    )
    flag_new = vol_regime_inverse_with_sma200_flag(prices)
    flag_old = iter011_flag(prices, window_short=60, window_long=252, ann_factor=252)
    # Subset: new=1 implies old=1.
    violations = ((flag_new == 1) & (flag_old != 1)).sum()
    assert violations == 0, (
        f"new flag fires on {violations} bars where iter 011 flag was OFF — "
        "SMA(200) gate is supposed to be ADDITIVE-restrictive, not new-firing"
    )
    # Sanity: new flag fires LESS OR EQUAL to iter 011 (otherwise SMA(200) does nothing).
    assert flag_new.sum() <= flag_old.sum()


def test_position_matches_flag_as_float():
    """Position is just the flag cast to float (long-only, full size)."""
    rng = np.random.default_rng(99)
    prices = pd.Series(
        100.0 * np.exp(np.cumsum(rng.normal(0.0, 0.01, size=600))),
        index=pd.date_range("2010-01-01", periods=600, freq="D"),
    )
    flag = vol_regime_inverse_with_sma200_flag(prices)
    pos = vol_regime_inverse_with_sma200_position(prices)
    assert pos.dtype == np.float64 or pos.dtype == float
    pd.testing.assert_series_equal(pos, flag.astype(float).rename("position"))
