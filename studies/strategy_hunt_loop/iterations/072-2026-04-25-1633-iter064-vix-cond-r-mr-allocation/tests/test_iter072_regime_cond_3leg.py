"""TDD spec for iter 072 VIX-conditional 3-leg combiner.

The combiner extends iter 068's VIX-conditional inner-weight idea to a
3-stream blend (r_046, r_qqqt, r_mr) where the r_mr (calm-aggressive
mean-reversion) weight is regime-conditional:

    w_mr[t]    = w_mr_calm   if VIX[t-1] <  threshold
                 w_mr_stress if VIX[t-1] >= threshold
    w_046[t]   = (1 - w_mr[t]) * 0.90      # preserve iter 064 9:1 base
    w_qqqt[t]  = (1 - w_mr[t]) * 0.10
    cost[t]    = cost_bps * 1e-4 * |w_mr[t] - w_mr[t-1]|
    r_072[t]   = w_046[t]·r_046 + w_qqqt[t]·r_qqqt + w_mr[t]·r_mr - cost

Citations
---------
* `[algo_trading_chan, p.95, p.153-154]` — momentum filter on MR + MR/momentum
  complementarity in regime-based portfolio allocation.
* Whaley (2009) JPM 35(3) — VIX threshold = 20.
* `[advances_fin_ml, p.162-164]` — strict shift(1) on regime signal (no peek).
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ITER_DIR))

from regime_conditional_3leg import combine_regime_cond_3leg  # noqa: E402
from numpy_reference_iter072 import combine_regime_cond_3leg_np  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_synth_streams(
    n: int = 400, seed: int = 31
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """Synthetic 3 return streams + a VIX path with both calm and stress."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    r_046 = pd.Series(rng.normal(0.0003, 0.008, size=n), index=idx, name="r_046")
    r_qqqt = pd.Series(rng.normal(0.0004, 0.011, size=n), index=idx, name="r_qqq_trend")
    r_mr = pd.Series(rng.normal(0.0002, 0.006, size=n), index=idx, name="r_spy_mr")
    # VIX path: alternating regime windows (calm 80 bars, stress 40 bars, repeat)
    vix_vals = np.empty(n)
    period = 120
    for i in range(n):
        vix_vals[i] = 14.0 if (i % period) < 80 else 25.0
    vix = pd.Series(vix_vals, index=idx, name="VIX")
    return r_046, r_qqqt, r_mr, vix


def _build_constant_calm_streams(
    n: int = 200, seed: int = 7
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """Streams + VIX held at calm regime throughout (no flips)."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    r_046 = pd.Series(rng.normal(0.0003, 0.008, size=n), index=idx)
    r_qqqt = pd.Series(rng.normal(0.0004, 0.011, size=n), index=idx)
    r_mr = pd.Series(rng.normal(0.0002, 0.006, size=n), index=idx)
    vix = pd.Series(np.full(n, 14.0), index=idx)
    return r_046, r_qqqt, r_mr, vix


# ---------------------------------------------------------------------------
# 1. Weight invariants
# ---------------------------------------------------------------------------

def test_weight_sum_invariant_every_bar() -> None:
    """w_046 + w_qqqt + w_mr must equal 1.0 every bar (within 1e-12)."""
    r_046, r_qqqt, r_mr, vix = _build_synth_streams()
    out = combine_regime_cond_3leg(
        r_046, r_qqqt, r_mr, vix,
        w_mr_calm=0.10, w_mr_stress=0.0, vix_threshold=20.0,
        return_diagnostics=True,
    )
    diag = out.attrs["diagnostics"]
    sums = diag["w_046"] + diag["w_qqqt"] + diag["w_mr"]
    assert np.max(np.abs(sums - 1.0)) < 1e-12


def test_w_046_qqqt_ratio_preserved_at_9_to_1() -> None:
    """w_046 : w_qqqt must be 9:1 every bar (preserves iter 064 base)."""
    r_046, r_qqqt, r_mr, vix = _build_synth_streams()
    out = combine_regime_cond_3leg(
        r_046, r_qqqt, r_mr, vix,
        w_mr_calm=0.15, w_mr_stress=0.05, vix_threshold=20.0,
        return_diagnostics=True,
    )
    diag = out.attrs["diagnostics"]
    ratio = diag["w_046"] / diag["w_qqqt"]
    assert np.allclose(ratio, 9.0, atol=1e-12)


# ---------------------------------------------------------------------------
# 2. Recovery of prior iters (compositional sanity)
# ---------------------------------------------------------------------------

def test_w_mr_eq_zero_recovers_iter064_static() -> None:
    """w_mr_calm = w_mr_stress = 0 → output = 0.9·r_046 + 0.1·r_qqqt (iter 064)."""
    r_046, r_qqqt, r_mr, vix = _build_synth_streams()
    out = combine_regime_cond_3leg(
        r_046, r_qqqt, r_mr, vix,
        w_mr_calm=0.0, w_mr_stress=0.0, vix_threshold=20.0,
    )
    expected = 0.9 * r_046 + 0.1 * r_qqqt
    common = out.index.intersection(expected.index)
    np.testing.assert_allclose(
        out.loc[common].values, expected.loc[common].values, atol=1e-14,
    )


def test_w_mr_calm_eq_w_mr_stress_recovers_iter071_static() -> None:
    """w_mr_calm == w_mr_stress → identical to iter 071 static blend (no regime flips)."""
    r_046, r_qqqt, r_mr, vix = _build_synth_streams()
    w_mr = 0.05
    out = combine_regime_cond_3leg(
        r_046, r_qqqt, r_mr, vix,
        w_mr_calm=w_mr, w_mr_stress=w_mr, vix_threshold=20.0,
    )
    expected = (
        (1.0 - w_mr) * 0.9 * r_046
        + (1.0 - w_mr) * 0.1 * r_qqqt
        + w_mr * r_mr
    )
    common = out.index.intersection(expected.index)
    # No regime flips, so cost = 0; output ≡ static blend exactly.
    np.testing.assert_allclose(
        out.loc[common].values, expected.loc[common].values, atol=1e-14,
    )


# ---------------------------------------------------------------------------
# 3. No-peek discipline
# ---------------------------------------------------------------------------

def test_vix_uses_lagged_value_no_peek() -> None:
    """VIX[t-1] determines weight at bar t (strict shift(1)).

    Build a deterministic VIX where calm/stress flips at exactly bar k.
    Confirm that w_mr at bar k still uses the PREVIOUS bar's regime
    (i.e., the flip materialises at bar k+1, not bar k).
    """
    n = 50
    idx = pd.date_range("2010-01-04", periods=n, freq="B")
    r_046 = pd.Series(np.full(n, 0.001), index=idx)
    r_qqqt = pd.Series(np.full(n, 0.001), index=idx)
    r_mr = pd.Series(np.full(n, 0.001), index=idx)
    # Flip at bar k=20: VIX is 14 for [0, 20), then 25 for [20, n).
    vix_vals = np.where(np.arange(n) < 20, 14.0, 25.0)
    vix = pd.Series(vix_vals, index=idx)

    out = combine_regime_cond_3leg(
        r_046, r_qqqt, r_mr, vix,
        w_mr_calm=0.10, w_mr_stress=0.0, vix_threshold=20.0,
        return_diagnostics=True,
    )
    diag = out.attrs["diagnostics"]
    w_mr = diag["w_mr"]
    # Bar 20: VIX[19]=14 (calm) → w_mr=0.10 still.
    # Bar 21: VIX[20]=25 (stress) → w_mr=0.0.
    assert w_mr[20] == pytest.approx(0.10, abs=1e-12), (
        f"bar 20 should still use calm regime (VIX[19]=14); got w_mr={w_mr[20]}"
    )
    assert w_mr[21] == pytest.approx(0.0, abs=1e-12), (
        f"bar 21 should use stress regime (VIX[20]=25); got w_mr={w_mr[21]}"
    )


# ---------------------------------------------------------------------------
# 4. Flip-cost accounting
# ---------------------------------------------------------------------------

def test_flip_cost_charged_only_on_regime_transitions() -> None:
    """Cost > 0 only on bars where w_mr changes (regime flip)."""
    r_046, r_qqqt, r_mr, vix = _build_synth_streams()
    out = combine_regime_cond_3leg(
        r_046, r_qqqt, r_mr, vix,
        w_mr_calm=0.10, w_mr_stress=0.0, vix_threshold=20.0, cost_bps=10.0,
        return_diagnostics=True,
    )
    diag = out.attrs["diagnostics"]
    cost = diag["cost"]
    delta_w_mr = diag["delta_w_mr"]
    # Cost is 0 iff delta_w_mr is 0; else proportional.
    nonzero_mask = delta_w_mr > 1e-12
    assert np.all(cost[~nonzero_mask] == 0.0)
    assert np.all(cost[nonzero_mask] > 0.0)


def test_zero_cost_in_constant_calm_regime() -> None:
    """If VIX is always calm (never crosses threshold), total cost = 0."""
    r_046, r_qqqt, r_mr, vix = _build_constant_calm_streams()
    out = combine_regime_cond_3leg(
        r_046, r_qqqt, r_mr, vix,
        w_mr_calm=0.10, w_mr_stress=0.0, vix_threshold=20.0, cost_bps=10.0,
        return_diagnostics=True,
    )
    diag = out.attrs["diagnostics"]
    assert diag["cost"].sum() == pytest.approx(0.0, abs=1e-12)


def test_cost_scales_with_cost_bps() -> None:
    """Doubling cost_bps must double total cost (linearity check)."""
    r_046, r_qqqt, r_mr, vix = _build_synth_streams()
    out_5 = combine_regime_cond_3leg(
        r_046, r_qqqt, r_mr, vix,
        w_mr_calm=0.10, w_mr_stress=0.0, vix_threshold=20.0, cost_bps=5.0,
        return_diagnostics=True,
    )
    out_10 = combine_regime_cond_3leg(
        r_046, r_qqqt, r_mr, vix,
        w_mr_calm=0.10, w_mr_stress=0.0, vix_threshold=20.0, cost_bps=10.0,
        return_diagnostics=True,
    )
    cost5 = out_5.attrs["diagnostics"]["cost"].sum()
    cost10 = out_10.attrs["diagnostics"]["cost"].sum()
    assert cost10 == pytest.approx(2.0 * cost5, rel=1e-12)


# ---------------------------------------------------------------------------
# 5. Indexing (inner-join contract)
# ---------------------------------------------------------------------------

def test_inner_join_index_is_intersection() -> None:
    """Output index is intersection of all 3 stream indices."""
    n = 200
    idx_full = pd.date_range("2010-01-04", periods=n, freq="B")
    r_046 = pd.Series(np.full(n, 0.001), index=idx_full)
    # r_qqqt missing first 30 bars
    r_qqqt = pd.Series(np.full(n - 30, 0.0008), index=idx_full[30:])
    # r_mr missing last 20 bars
    r_mr = pd.Series(np.full(n - 20, 0.0006), index=idx_full[:n - 20])
    vix = pd.Series(np.full(n, 16.0), index=idx_full)

    out = combine_regime_cond_3leg(
        r_046, r_qqqt, r_mr, vix,
        w_mr_calm=0.10, w_mr_stress=0.0, vix_threshold=20.0,
    )
    expected_idx = idx_full[30:n - 20]
    pd.testing.assert_index_equal(out.index, expected_idx)


def test_vix_alignment_handles_missing_days() -> None:
    """VIX missing intermediate days handled by ffill().bfill() — no NaN in output."""
    r_046, r_qqqt, r_mr, _ = _build_synth_streams()
    vix_full = pd.Series(np.full(len(r_046), 14.0), index=r_046.index)
    # Drop every other VIX bar to simulate a sparse macro feed.
    vix_sparse = vix_full.iloc[::2].copy()

    out = combine_regime_cond_3leg(
        r_046, r_qqqt, r_mr, vix_sparse,
        w_mr_calm=0.10, w_mr_stress=0.0, vix_threshold=20.0,
    )
    assert not out.isna().any()


# ---------------------------------------------------------------------------
# 6. Validation
# ---------------------------------------------------------------------------

def test_value_error_on_negative_w_mr_calm() -> None:
    r_046, r_qqqt, r_mr, vix = _build_synth_streams()
    with pytest.raises(ValueError, match="w_mr_calm"):
        combine_regime_cond_3leg(
            r_046, r_qqqt, r_mr, vix,
            w_mr_calm=-0.01, w_mr_stress=0.0, vix_threshold=20.0,
        )


def test_value_error_on_w_mr_stress_above_one() -> None:
    r_046, r_qqqt, r_mr, vix = _build_synth_streams()
    with pytest.raises(ValueError, match="w_mr_stress"):
        combine_regime_cond_3leg(
            r_046, r_qqqt, r_mr, vix,
            w_mr_calm=0.10, w_mr_stress=1.5, vix_threshold=20.0,
        )


def test_value_error_on_negative_cost_bps() -> None:
    r_046, r_qqqt, r_mr, vix = _build_synth_streams()
    with pytest.raises(ValueError, match="cost_bps"):
        combine_regime_cond_3leg(
            r_046, r_qqqt, r_mr, vix,
            w_mr_calm=0.10, w_mr_stress=0.0, cost_bps=-1.0, vix_threshold=20.0,
        )


# ---------------------------------------------------------------------------
# 7. Cross-library parity (G7)
# ---------------------------------------------------------------------------

def test_numpy_reference_matches_pandas_engine_bit_identical() -> None:
    """G7 cross-lib parity: pandas vs numpy implementations agree to 1e-12."""
    r_046, r_qqqt, r_mr, vix = _build_synth_streams()
    pd_out = combine_regime_cond_3leg(
        r_046, r_qqqt, r_mr, vix,
        w_mr_calm=0.12, w_mr_stress=0.02, vix_threshold=20.0, cost_bps=5.0,
    )
    # Pre-align inputs to common index for the numpy reference (it expects arrays).
    common = pd_out.index
    a = r_046.loc[common].to_numpy()
    b = r_qqqt.loc[common].to_numpy()
    c = r_mr.loc[common].to_numpy()
    v = vix.reindex(common).ffill().bfill().to_numpy()

    np_out = combine_regime_cond_3leg_np(
        a, b, c, v,
        w_mr_calm=0.12, w_mr_stress=0.02, vix_threshold=20.0, cost_bps=5.0,
    )
    np.testing.assert_allclose(pd_out.to_numpy(), np_out, atol=1e-12)


def test_diagnostics_arrays_have_correct_shape() -> None:
    """When return_diagnostics=True, all diag arrays are length-n."""
    r_046, r_qqqt, r_mr, vix = _build_synth_streams()
    out = combine_regime_cond_3leg(
        r_046, r_qqqt, r_mr, vix,
        w_mr_calm=0.10, w_mr_stress=0.0, vix_threshold=20.0,
        return_diagnostics=True,
    )
    n = len(out)
    diag = out.attrs["diagnostics"]
    for k in ("w_046", "w_qqqt", "w_mr", "is_stress", "delta_w_mr", "cost", "vix_lag"):
        assert k in diag, f"missing diagnostic key: {k}"
        assert len(diag[k]) == n, f"{k} has len {len(diag[k])}, expected {n}"


# ---------------------------------------------------------------------------
# 8. Regime-conditional structural property
# ---------------------------------------------------------------------------

def test_w_mr_takes_calm_value_in_calm_regime() -> None:
    """During calm regime (VIX[t-1] < threshold), w_mr equals w_mr_calm."""
    r_046, r_qqqt, r_mr, vix = _build_synth_streams()
    out = combine_regime_cond_3leg(
        r_046, r_qqqt, r_mr, vix,
        w_mr_calm=0.10, w_mr_stress=0.02, vix_threshold=20.0,
        return_diagnostics=True,
    )
    diag = out.attrs["diagnostics"]
    is_stress = diag["is_stress"].astype(bool)
    w_mr = diag["w_mr"]
    assert np.all(w_mr[~is_stress] == pytest.approx(0.10, abs=1e-12))
    assert np.all(w_mr[is_stress] == pytest.approx(0.02, abs=1e-12))
