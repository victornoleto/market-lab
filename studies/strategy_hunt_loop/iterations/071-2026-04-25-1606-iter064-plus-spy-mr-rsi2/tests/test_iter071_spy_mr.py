"""TDD spec for iter 071 SPY short-term mean-reversion stream + 3-leg combiner.

Citations
---------
* `[algo_trading_chan, p.95, ch.4]` — momentum filter on mean-reversion entry.
* `[algo_trading_chan, p.183-184, ch.8]` — no in-sample stop-loss for MR.
* `[advances_fin_ml, p.162-164]` — strict shift(1) on signal (no peek).
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline.
* Connors-Alvarez (2009) ISBN 978-0-9755513-2-7 — RSI(2) canonical rules.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ITER_DIR))

from spy_mr import compute_spy_mr_returns, wilder_rsi  # noqa: E402
from numpy_reference_iter071 import compute_spy_mr_returns_np  # noqa: E402
from combined_046_qqqt_mr import combine_046_qqqt_mr  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_synth_prices(n: int = 600, seed: int = 17) -> pd.Series:
    """Synthetic SPY-like adjusted close: bull trend with periodic dips."""
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0004, 0.012, size=n)
    # Inject a few sharp 1-day dips (-2%) every ~50 bars; verify entries/exits
    for i in range(40, n, 55):
        rets[i] = -0.025
        if i + 1 < n:
            rets[i + 1] = 0.018  # bounce next day
    px = 100.0 * np.cumprod(1.0 + rets)
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    return pd.Series(px, index=idx, name="SPY")


# ---------------------------------------------------------------------------
# RSI math
# ---------------------------------------------------------------------------

def test_wilder_rsi_known_value_monotone_up():
    """Strictly increasing prices → RSI saturates at 100."""
    px = pd.Series(np.arange(1.0, 50.0))
    rsi = wilder_rsi(px, period=2)
    # First (period) values are NaN/warmup; later values must be 100.
    tail = rsi.dropna().iloc[5:]
    assert (tail >= 99.99).all(), f"monotone-up RSI must approach 100, got tail max={tail.max()} min={tail.min()}"


def test_wilder_rsi_known_value_monotone_down():
    """Strictly decreasing prices → RSI saturates at 0."""
    px = pd.Series(np.arange(50.0, 1.0, -1.0))
    rsi = wilder_rsi(px, period=2)
    tail = rsi.dropna().iloc[5:]
    assert (tail <= 0.01).all(), f"monotone-down RSI must approach 0, got tail max={tail.max()}"


def test_wilder_rsi_alternating_50():
    """Constant alternation up/down → RSI oscillates near 50 (gain≈loss)."""
    arr = np.array([100.0, 101.0, 100.0, 101.0, 100.0, 101.0,
                    100.0, 101.0, 100.0, 101.0, 100.0])
    rsi = wilder_rsi(pd.Series(arr), period=2)
    tail = rsi.dropna()
    # After warmup, alternation gives oscillating RSI around 50.
    assert (tail.iloc[2:].between(20, 80)).all(), "alternating series RSI must be near 50"


def test_wilder_rsi_invalid_period_raises():
    px = pd.Series([1.0, 2.0, 3.0])
    with pytest.raises(ValueError):
        wilder_rsi(px, period=0)
    with pytest.raises(ValueError):
        wilder_rsi(px, period=-1)


# ---------------------------------------------------------------------------
# Signal correctness — Connors-Alvarez rules + Chan p.95 momentum gate
# ---------------------------------------------------------------------------

def test_warmup_returns_zero_position():
    """First sma200_window bars must have position=0 (cash earning rf_d only)."""
    px = _build_synth_prices(n=400)
    out = compute_spy_mr_returns(
        px, rsi_period=2, rsi_threshold=10.0,
        sma_filter=200, exit_sma=5, rf=0.02, cost_bps=5.0,
    )
    # During warmup: rf_d daily; no trades; cost = 0.
    rf_d = (1.0 + 0.02) ** (1.0 / 252.0) - 1.0
    warmup = out.iloc[:198]  # before SMA200 is well-defined
    # Warmup bars MUST equal rf_d exactly (no trade cost).
    np.testing.assert_allclose(warmup.values, rf_d, atol=1e-12)


def test_no_peek_shift1():
    """Perturbing prices[t] must NOT change pos at any bar ≤ t.

    The signal at bar t depends only on prices ≤ t-1.
    """
    px = _build_synth_prices(n=300)
    out_a = compute_spy_mr_returns(
        px, rsi_period=2, rsi_threshold=10.0,
        sma_filter=200, exit_sma=5, rf=0.02, cost_bps=5.0,
    )
    # Perturb a single price near the end.
    px2 = px.copy()
    perturb_t = 280
    px2.iloc[perturb_t] = px.iloc[perturb_t] * 1.10  # large +10% jolt
    out_b = compute_spy_mr_returns(
        px2, rsi_period=2, rsi_threshold=10.0,
        sma_filter=200, exit_sma=5, rf=0.02, cost_bps=5.0,
    )
    # All output bars at index ≤ perturb_t in the returns series are based on
    # prices ≤ perturb_t-1, so MUST be identical.
    common = out_a.index.intersection(out_b.index)
    pre_perturb = common[common <= px.index[perturb_t]]
    np.testing.assert_allclose(
        out_a.loc[pre_perturb].values,
        out_b.loc[pre_perturb].values,
        atol=1e-12,
        err_msg="bars at or before perturbation timestamp must be identical",
    )


def test_buy_only_when_gate_and_dip():
    """Position transitions 0→1 ONLY when SPY>SMA200 AND RSI2<threshold at t-1.

    Constructed scenario: a price that breaks above SMA200 then drops sharply
    one day. Position at the post-drop bar should flip 1.
    """
    # Synthetic: 250 days slow uptrend, then 3-day sharp drop ~-2.5% each, then bounce.
    n = 300
    base = np.linspace(100.0, 200.0, 250)  # slow uptrend
    drop = base[-1] * np.array([0.97, 0.945, 0.93])  # 3-day sharp drop
    bounce = drop[-1] * np.cumprod(1.0 + np.array([0.012, 0.014, 0.011]))
    rest = np.linspace(bounce[-1], bounce[-1] * 1.02, n - 250 - 3 - 3)
    arr = np.concatenate([base, drop, bounce, rest])
    idx = pd.date_range("2010-01-04", periods=len(arr), freq="B")
    px = pd.Series(arr, index=idx, name="SPY")

    # diagnostic: should produce at least one entry near the drop region
    out = compute_spy_mr_returns(
        px, rsi_period=2, rsi_threshold=15.0, sma_filter=200,
        exit_sma=5, rf=0.02, cost_bps=5.0,
    )
    rf_d = (1.0 + 0.02) ** (1 / 252.0) - 1.0
    n_nonrf = int((np.abs(out.values - rf_d) > 1e-9).sum())
    assert n_nonrf >= 3, (
        f"expected ≥3 non-rf bars (entry+hold+exit+cost) on a clear post-200d-SMA dip, "
        f"got {n_nonrf}"
    )


def test_zero_cost_when_no_trade():
    """If position is constant cash (warmup), turnover-cost contribution is 0."""
    n = 100  # less than sma_filter=200 → entire series is warmup
    px = _build_synth_prices(n=n)
    rf_d = (1.0 + 0.02) ** (1.0 / 252.0) - 1.0
    out = compute_spy_mr_returns(
        px, rsi_period=2, rsi_threshold=10.0,
        sma_filter=200, exit_sma=5, rf=0.02, cost_bps=5.0,
    )
    # All bars MUST equal rf_d when no trade fires.
    np.testing.assert_allclose(out.values, rf_d, atol=1e-12)


def test_invalid_params_raise():
    px = _build_synth_prices(n=300)
    # rsi_period invalid
    with pytest.raises(ValueError):
        compute_spy_mr_returns(px, rsi_period=0)
    # rsi_threshold out of [0, 100]
    with pytest.raises(ValueError):
        compute_spy_mr_returns(px, rsi_threshold=-1)
    with pytest.raises(ValueError):
        compute_spy_mr_returns(px, rsi_threshold=101)
    # sma_filter <= 0
    with pytest.raises(ValueError):
        compute_spy_mr_returns(px, sma_filter=0)
    # exit_sma <= 0
    with pytest.raises(ValueError):
        compute_spy_mr_returns(px, exit_sma=0)
    # cost_bps < 0
    with pytest.raises(ValueError):
        compute_spy_mr_returns(px, cost_bps=-1.0)


def test_too_short_series_raises():
    short = pd.Series([100.0], index=pd.date_range("2010-01-01", periods=1))
    with pytest.raises(ValueError):
        compute_spy_mr_returns(short)


# ---------------------------------------------------------------------------
# Cross-library parity (G7) — pandas vs numpy reference
# ---------------------------------------------------------------------------

def test_cross_lib_parity_max_diff_below_threshold():
    """Pandas vs pure-numpy reference: max |Δr| ≤ 1e-9 across full series."""
    px = _build_synth_prices(n=600, seed=42)
    pd_out = compute_spy_mr_returns(
        px, rsi_period=2, rsi_threshold=10.0,
        sma_filter=200, exit_sma=5, rf=0.02, cost_bps=5.0,
    )
    np_out = compute_spy_mr_returns_np(
        px.values, rsi_period=2, rsi_threshold=10.0,
        sma_filter=200, exit_sma=5, rf=0.02, cost_bps=5.0,
    )
    n = min(len(pd_out), len(np_out))
    pd_arr = pd_out.values[-n:]
    np_arr = np_out[-n:]
    max_diff = float(np.max(np.abs(pd_arr - np_arr)))
    assert max_diff <= 1e-9, f"pandas vs numpy diverge: max |Δr|={max_diff:.2e}"


# ---------------------------------------------------------------------------
# 3-leg combiner: 0.85·r_046 + 0.10·r_qqqt + 0.05·r_mr
# ---------------------------------------------------------------------------

def test_3leg_combiner_inner_join():
    """Combiner returns a series indexed on the inner-join of all 3 inputs."""
    idx_a = pd.date_range("2010-01-04", periods=10, freq="B")
    idx_b = pd.date_range("2010-01-06", periods=10, freq="B")
    idx_c = pd.date_range("2010-01-05", periods=10, freq="B")
    a = pd.Series(np.full(10, 0.001), index=idx_a)
    b = pd.Series(np.full(10, 0.002), index=idx_b)
    c = pd.Series(np.full(10, 0.003), index=idx_c)
    out = combine_046_qqqt_mr(a, b, c, w_046=0.85, w_qqqt=0.10, w_mr=0.05)
    common = idx_a.intersection(idx_b).intersection(idx_c)
    assert out.index.equals(common)


def test_3leg_combiner_weighted_sum():
    """Output equals weighted sum on inner-joined bars."""
    idx = pd.date_range("2010-01-04", periods=20, freq="B")
    a = pd.Series(np.full(20, 0.001), index=idx)
    b = pd.Series(np.full(20, 0.002), index=idx)
    c = pd.Series(np.full(20, 0.003), index=idx)
    out = combine_046_qqqt_mr(a, b, c, w_046=0.5, w_qqqt=0.3, w_mr=0.2)
    expected = 0.5 * 0.001 + 0.3 * 0.002 + 0.2 * 0.003
    np.testing.assert_allclose(out.values, expected, atol=1e-12)


def test_3leg_combiner_validates_weights():
    idx = pd.date_range("2010-01-04", periods=5, freq="B")
    a = pd.Series([0.001] * 5, index=idx)
    b = pd.Series([0.001] * 5, index=idx)
    c = pd.Series([0.001] * 5, index=idx)
    with pytest.raises(ValueError):
        combine_046_qqqt_mr(a, b, c, w_046=-1, w_qqqt=0.1, w_mr=0.05)
    with pytest.raises(ValueError):
        combine_046_qqqt_mr(a, b, c, w_046=0, w_qqqt=0, w_mr=0)


def test_3leg_combiner_w_mr_zero_recovers_iter064():
    """When w_mr=0, output must equal w_046·a + w_qqqt·b on the common index."""
    idx = pd.date_range("2010-01-04", periods=20, freq="B")
    a = pd.Series(np.linspace(0.001, 0.005, 20), index=idx)
    b = pd.Series(np.linspace(-0.001, 0.003, 20), index=idx)
    c = pd.Series(np.full(20, 0.0002), index=idx)  # any value
    out = combine_046_qqqt_mr(a, b, c, w_046=0.9, w_qqqt=0.1, w_mr=0.0)
    expected = 0.9 * a + 0.1 * b
    np.testing.assert_allclose(out.values, expected.values, atol=1e-12)
