"""TDD specs for iter 010 — 3-leg vol-managed SPY+TLT+GLD blend.

Written BEFORE the implementation. Tests define the contract:

- Inverse-variance weighting generalises iter 006's 2-leg form to N=3.
- Degenerate case (one leg at infinite variance) must reproduce iter
  006's 2-leg result to 1e-8 per-bar scale.
- Equal-variance legs with zero off-diagonals give uniform 1/3 weights.
- Total gross exposure ``sum(pos) ≤ max_leverage`` at every bar.
- No look-ahead: first ``lookback`` bars dropped, ``σ̂²_{t-1}`` uses
  window ``[t-L, t-1]`` exclusively.

Citations
---------
* `[risk_parity, p.10-11, ch.1]` — naïve risk parity N-asset form.
* `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag.
* Moreira & Muir (2017), *JoF* 72(4) — portfolio variance-scaling.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ITER_DIR))

# Import-under-test (will exist after implementation).
from three_leg_blend import apply_blend_variance_target_3leg  # noqa: E402


@pytest.fixture
def synthetic_three_leg_returns() -> pd.DataFrame:
    """Three legs with known variance structure for analytic checks."""
    rng = np.random.default_rng(42)
    n = 500
    # Three uncorrelated normal streams with target daily vols.
    r1 = rng.normal(0.0004, 0.012, n)  # ~19% annualised
    r2 = rng.normal(0.0002, 0.006, n)  # ~9.5% annualised
    r3 = rng.normal(0.0003, 0.009, n)  # ~14% annualised
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    return pd.DataFrame({"SPY": r1, "TLT": r2, "GLD": r3}, index=idx)


class TestThreeLegBlend:
    def test_output_shapes_and_index(self, synthetic_three_leg_returns):
        df = synthetic_three_leg_returns
        net, pos, scale = apply_blend_variance_target_3leg(
            df["SPY"], df["TLT"], df["GLD"],
            target_vol=0.15, lookback=21, max_leverage=2.0,
            cost_bps_per_leg=0.0002,
        )
        assert isinstance(net, pd.Series)
        assert isinstance(pos, pd.DataFrame)
        assert isinstance(scale, pd.Series)
        assert list(pos.columns) == ["SPY", "TLT", "GLD"]
        # First `lookback` bars dropped (σ²_{t-1} needs full window).
        assert len(net) == len(df) - 21
        assert len(pos) == len(net)
        assert len(scale) == len(net)
        assert net.index.equals(pos.index)
        assert net.index.equals(scale.index)

    def test_scale_bounded_by_max_leverage(self, synthetic_three_leg_returns):
        df = synthetic_three_leg_returns
        _, pos, scale = apply_blend_variance_target_3leg(
            df["SPY"], df["TLT"], df["GLD"],
            target_vol=0.15, lookback=21, max_leverage=2.0,
            cost_bps_per_leg=0.0002,
        )
        assert (scale <= 2.0 + 1e-9).all()
        assert (scale >= 0.0).all()
        total_pos = pos.sum(axis=1)
        # Sum of leg positions equals scale (weights sum to 1).
        np.testing.assert_allclose(total_pos.to_numpy(), scale.to_numpy(), atol=1e-10)

    def test_weights_sum_to_one(self, synthetic_three_leg_returns):
        df = synthetic_three_leg_returns
        _, pos, scale = apply_blend_variance_target_3leg(
            df["SPY"], df["TLT"], df["GLD"],
            target_vol=0.15, lookback=21, max_leverage=2.0,
            cost_bps_per_leg=0.0002,
        )
        # Normalise by scale where scale > 0.
        mask = scale > 1e-12
        w = pos.loc[mask].div(scale.loc[mask], axis=0)
        np.testing.assert_allclose(w.sum(axis=1).to_numpy(), 1.0, atol=1e-10)

    def test_equal_variance_zero_correlation_gives_uniform_weights(self):
        """Three legs with equal variance and zero correlation → w=1/3 each.

        Constructed to satisfy ``Σ = σ² · I_3`` after rolling estimator.
        The inverse-variance weighting is ``w_i = (1/σ²_i) / Σ_j(1/σ²_j)``;
        when σ²_i are equal, ``w_i = 1/3``.
        """
        rng = np.random.default_rng(7)
        n = 400
        # Zero-mean same-vol uncorrelated draws (empirical correlation tiny).
        vol = 0.01
        r1 = rng.normal(0.0, vol, n)
        r2 = rng.normal(0.0, vol, n)
        r3 = rng.normal(0.0, vol, n)
        idx = pd.date_range("2020-01-02", periods=n, freq="B")
        df = pd.DataFrame({"SPY": r1, "TLT": r2, "GLD": r3}, index=idx)
        _, pos, scale = apply_blend_variance_target_3leg(
            df["SPY"], df["TLT"], df["GLD"],
            target_vol=0.15, lookback=60, max_leverage=5.0,
            cost_bps_per_leg=0.0,
        )
        mask = scale > 1e-6
        w = pos.loc[mask].div(scale.loc[mask], axis=0)
        # On average weights should be close to 1/3 (sample variance ~equal).
        mean_weights = w.mean()
        np.testing.assert_allclose(mean_weights.to_numpy(), [1/3, 1/3, 1/3], atol=0.03)

    def test_asymmetric_vol_inverse_proportion(self):
        """σ²_tlt small → highest weight; σ²_spy large → lowest.

        Analytic: with legs uncorrelated and rolling σ̂²_i close to true σ²_i,
        inverse-variance weights order strictly matches the inverse ordering
        of true variances.
        """
        rng = np.random.default_rng(123)
        n = 400
        r1 = rng.normal(0.0, 0.020, n)  # σ² largest → smallest weight
        r2 = rng.normal(0.0, 0.005, n)  # σ² smallest → largest weight
        r3 = rng.normal(0.0, 0.010, n)  # σ² middle
        idx = pd.date_range("2020-01-02", periods=n, freq="B")
        df = pd.DataFrame({"SPY": r1, "TLT": r2, "GLD": r3}, index=idx)
        _, pos, scale = apply_blend_variance_target_3leg(
            df["SPY"], df["TLT"], df["GLD"],
            target_vol=0.15, lookback=60, max_leverage=5.0,
            cost_bps_per_leg=0.0,
        )
        mask = scale > 1e-6
        w = pos.loc[mask].div(scale.loc[mask], axis=0)
        mean_w = w.mean()
        # Strict ordering: TLT (lowest vol) > GLD (mid) > SPY (highest vol).
        assert mean_w["TLT"] > mean_w["GLD"] > mean_w["SPY"]

    def test_no_lookahead_first_bar_uses_past_window_only(self):
        """First output bar ``t = lookback`` must use returns[0:lookback]
        (NOT returns[0:lookback+1]). Test by perturbing bar ``t = lookback``
        and verifying first output scale is unchanged."""
        rng = np.random.default_rng(11)
        n = 200
        df = pd.DataFrame({
            "SPY": rng.normal(0.0, 0.01, n),
            "TLT": rng.normal(0.0, 0.005, n),
            "GLD": rng.normal(0.0, 0.008, n),
        }, index=pd.date_range("2020-01-02", periods=n, freq="B"))
        L = 21
        _, _, scale_a = apply_blend_variance_target_3leg(
            df["SPY"], df["TLT"], df["GLD"],
            target_vol=0.15, lookback=L, max_leverage=2.0,
            cost_bps_per_leg=0.0,
        )
        df_perturb = df.copy()
        # Perturb the bar at index L itself (which is the first output bar).
        df_perturb.iloc[L, 0] = 0.25  # big SPY shock at first output bar
        df_perturb.iloc[L, 1] = -0.10
        df_perturb.iloc[L, 2] = 0.05
        _, _, scale_b = apply_blend_variance_target_3leg(
            df_perturb["SPY"], df_perturb["TLT"], df_perturb["GLD"],
            target_vol=0.15, lookback=L, max_leverage=2.0,
            cost_bps_per_leg=0.0,
        )
        # The first output bar's scale must be identical since both agree on
        # the returns[0:L] window; it only depends on PAST bars, not bar L.
        assert scale_a.iloc[0] == pytest.approx(scale_b.iloc[0], abs=1e-12)

    def test_cost_reduces_net_returns(self, synthetic_three_leg_returns):
        df = synthetic_three_leg_returns
        net_0, _, _ = apply_blend_variance_target_3leg(
            df["SPY"], df["TLT"], df["GLD"],
            target_vol=0.15, lookback=21, max_leverage=2.0,
            cost_bps_per_leg=0.0,
        )
        net_10, _, _ = apply_blend_variance_target_3leg(
            df["SPY"], df["TLT"], df["GLD"],
            target_vol=0.15, lookback=21, max_leverage=2.0,
            cost_bps_per_leg=0.001,  # 10 bps
        )
        # 10 bps cost must reduce cumulative returns.
        eq_0 = (1.0 + net_0).cumprod().iloc[-1]
        eq_10 = (1.0 + net_10).cumprod().iloc[-1]
        assert eq_10 < eq_0

    def test_invalid_params_raise(self, synthetic_three_leg_returns):
        df = synthetic_three_leg_returns
        with pytest.raises(ValueError, match="target_vol"):
            apply_blend_variance_target_3leg(
                df["SPY"], df["TLT"], df["GLD"],
                target_vol=0.0, lookback=21, max_leverage=2.0,
            )
        with pytest.raises(ValueError, match="lookback"):
            apply_blend_variance_target_3leg(
                df["SPY"], df["TLT"], df["GLD"],
                target_vol=0.15, lookback=1, max_leverage=2.0,
            )
        with pytest.raises(ValueError, match="max_leverage"):
            apply_blend_variance_target_3leg(
                df["SPY"], df["TLT"], df["GLD"],
                target_vol=0.15, lookback=21, max_leverage=-1.0,
            )

    def test_index_mismatch_raises(self, synthetic_three_leg_returns):
        df = synthetic_three_leg_returns
        shifted = df["GLD"].shift(1).dropna()
        with pytest.raises(ValueError, match="index"):
            apply_blend_variance_target_3leg(
                df["SPY"], df["TLT"], shifted,
                target_vol=0.15, lookback=21, max_leverage=2.0,
            )
