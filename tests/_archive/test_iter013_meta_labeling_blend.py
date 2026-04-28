"""Iter 013 TDD tests — meta-labeling classifier on vol-managed blend.

Focus of this spec: no look-ahead in features or training, and numpy-
reference parity with the pandas engine. The classifier itself (scikit-
learn LogisticRegression) is treated as a trusted dependency; tests
exercise the SHAPE of the pipeline, not sklearn's numerical behavior.

Citations
---------
* `[advances_fin_ml, ch.3, p.50-56]` — meta-labeling principle.
* `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag rule, extended to
  feature lagging.
* `[advances_fin_ml, p.31-34]` — cross-lib parity principle for G7.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = (
    Path(__file__).resolve().parent.parent
    / "studies"
    / "strategy_hunt_loop"
    / "iterations"
    / "013-2026-04-24-1619-meta-labeling-blend"
)
sys.path.insert(0, str(ITER_DIR))


# ---------------------------------------------------------------------------
# Feature engineering tests
# ---------------------------------------------------------------------------


class TestFeatureLag:
    """Feature computation must never use bar-t data to size bar t."""

    def test_correlation_feature_is_lagged(self):
        from meta_labeling import compute_features

        rng = np.random.default_rng(42)
        idx = pd.date_range("2010-01-04", periods=500, freq="B")
        r_spy = pd.Series(rng.normal(0.0005, 0.01, 500), index=idx)
        r_tlt = pd.Series(rng.normal(0.0002, 0.008, 500), index=idx)
        vix = pd.Series(rng.normal(18.0, 3.0, 500), index=idx)

        features = compute_features(r_spy, r_tlt, vix)

        # The feature for bar t must NOT contain bar-t data. Verify by
        # flipping bar t's returns and checking the feature at bar t
        # is unchanged (only bar t+1 and later should change).
        r_spy_flipped = r_spy.copy()
        flip_idx = 300
        r_spy_flipped.iloc[flip_idx] = -0.5  # huge perturbation
        features_flipped = compute_features(r_spy_flipped, r_tlt, vix)

        # Feature at bar flip_idx must be identical (uses data up to flip_idx-1).
        pd.testing.assert_series_equal(
            features.iloc[:flip_idx + 1]["rho_60"],
            features_flipped.iloc[:flip_idx + 1]["rho_60"],
            check_names=False,
        )
        # Feature at bar flip_idx+1 MUST differ — the perturbation is now in
        # the training window.
        assert (
            features.iloc[flip_idx + 1]["rho_60"]
            != features_flipped.iloc[flip_idx + 1]["rho_60"]
        )

    def test_vix_zscore_feature_is_lagged(self):
        from meta_labeling import compute_features

        rng = np.random.default_rng(0)
        idx = pd.date_range("2010-01-04", periods=400, freq="B")
        r_spy = pd.Series(rng.normal(0.0, 0.01, 400), index=idx)
        r_tlt = pd.Series(rng.normal(0.0, 0.008, 400), index=idx)
        vix = pd.Series(20.0 + rng.normal(0.0, 2.0, 400), index=idx)

        features = compute_features(r_spy, r_tlt, vix)

        vix_flip = vix.copy()
        flip_idx = 300
        vix_flip.iloc[flip_idx] = 80.0  # COVID-scale shock
        features_flip = compute_features(r_spy, r_tlt, vix_flip)

        assert (
            features.iloc[flip_idx]["vix_z"]
            == features_flip.iloc[flip_idx]["vix_z"]
        ), "vix_z at bar flip_idx must use data from < flip_idx"
        assert (
            features.iloc[flip_idx + 1]["vix_z"]
            != features_flip.iloc[flip_idx + 1]["vix_z"]
        ), "vix_z at bar flip_idx+1 must reflect the shock"

    def test_features_have_no_nan_after_warmup(self):
        from meta_labeling import compute_features, FEATURE_WARMUP_BARS

        rng = np.random.default_rng(1)
        idx = pd.date_range("2010-01-04", periods=600, freq="B")
        r_spy = pd.Series(rng.normal(0.0005, 0.01, 600), index=idx)
        r_tlt = pd.Series(rng.normal(0.0002, 0.008, 600), index=idx)
        vix = pd.Series(rng.normal(20.0, 3.0, 600), index=idx)

        features = compute_features(r_spy, r_tlt, vix)

        post_warmup = features.iloc[FEATURE_WARMUP_BARS:]
        assert not post_warmup.isna().any().any(), (
            "Features must be free of NaN past warmup"
        )


# ---------------------------------------------------------------------------
# Meta-labeling pipeline tests
# ---------------------------------------------------------------------------


class TestMetaLabelingPipeline:
    """Train/predict loop must respect temporal ordering (no leakage)."""

    def test_prediction_independent_of_future_bars(self):
        """Predictions at bar t must not depend on bars strictly after t.

        Strategy: perturb bar t=2500 (in the FUTURE of bar 1500). The
        model active at bar 1501 and its features at that bar should
        both be computed only from data ≤ bar 1500. Therefore the
        prediction at bar 1501 should be IDENTICAL whether or not bar
        2500's return is perturbed. This is the canonical no-look-ahead
        invariant.
        """
        from meta_labeling import apply_blend_with_meta

        rng = np.random.default_rng(42)
        n = 3000
        idx = pd.date_range("2008-01-02", periods=n, freq="B")
        r_spy = pd.Series(rng.normal(0.0005, 0.01, n), index=idx)
        r_tlt = pd.Series(rng.normal(0.0002, 0.008, n), index=idx)
        vix = pd.Series(20.0 + rng.normal(0.0, 3.0, n), index=idx)

        _, _, _, _, meta_ref = apply_blend_with_meta(
            r_spy, r_tlt, vix,
            target_vol=0.15, lookback=21, max_leverage=2.0,
            cost_bps_per_leg=0.0002,
            train_window=1000, retrain_cadence=252,
            warmup_bars=1260, decision_threshold=0.5,
            random_state=42,
        )

        r_spy_flipped = r_spy.copy()
        r_spy_flipped.iloc[2500] = 0.3  # future perturbation

        _, _, _, _, meta_flip = apply_blend_with_meta(
            r_spy_flipped, r_tlt, vix,
            target_vol=0.15, lookback=21, max_leverage=2.0,
            cost_bps_per_leg=0.0002,
            train_window=1000, retrain_cadence=252,
            warmup_bars=1260, decision_threshold=0.5,
            random_state=42,
        )

        # All predictions at bars ≤ 2499 (in scale.index) must match.
        ref_probs = meta_ref["p_act"]
        flip_probs = meta_flip["p_act"]
        # Find the scale-index position that corresponds to original
        # r_spy index 2499. Drop NaN prefix from p_act to get the
        # model-prediction region.
        aligned = pd.concat(
            [ref_probs, flip_probs], axis=1, keys=["ref", "flip"]
        ).dropna()
        # Compare all rows up to idx < date at r_spy iloc 2499.
        cutoff_date = idx[2499]
        past_mask = aligned.index <= cutoff_date
        assert (
            aligned.loc[past_mask, "ref"] == aligned.loc[past_mask, "flip"]
        ).all(), (
            "Meta-predictions at bars ≤ 2499 must not depend on future bar 2500"
        )


# ---------------------------------------------------------------------------
# Numpy parity tests (G7)
# ---------------------------------------------------------------------------


class TestCrossLibParity:
    """G7 parity: numpy reference must match pandas engine CAGR within 3 pp."""

    def test_numpy_reference_agrees_on_small_synthetic(self):
        from meta_labeling import apply_blend_with_meta
        from meta_labeling_numpy_reference import apply_blend_with_meta_np

        rng = np.random.default_rng(7)
        n = 2500
        idx = pd.date_range("2010-01-04", periods=n, freq="B")
        r_spy = pd.Series(rng.normal(0.0005, 0.01, n), index=idx)
        r_tlt = pd.Series(rng.normal(0.0002, 0.008, n), index=idx)
        vix = pd.Series(20.0 + np.abs(rng.normal(0.0, 3.0, n)), index=idx)

        net_pd, _, _, _, _ = apply_blend_with_meta(
            r_spy, r_tlt, vix,
            target_vol=0.15, lookback=21, max_leverage=2.0,
            cost_bps_per_leg=0.0002,
            train_window=1000, retrain_cadence=252,
            warmup_bars=1260, decision_threshold=0.5,
            random_state=42,
        )
        eq_pd = (1.0 + net_pd).cumprod()
        cagr_pd = eq_pd.iloc[-1] ** (252.0 / len(net_pd)) - 1.0

        net_np = apply_blend_with_meta_np(
            r_spy.to_numpy(), r_tlt.to_numpy(), vix.to_numpy(),
            target_vol=0.15, lookback=21, max_leverage=2.0,
            cost_bps_per_leg=0.0002,
            train_window=1000, retrain_cadence=252,
            warmup_bars=1260, decision_threshold=0.5,
            random_state=42,
        )
        eq_np = np.cumprod(1.0 + net_np)
        cagr_np = eq_np[-1] ** (252.0 / len(net_np)) - 1.0

        # 3 pp tolerance per G7 spec.
        assert abs(cagr_pd - cagr_np) < 0.03, (
            f"pandas CAGR {cagr_pd:.4f} vs numpy CAGR {cagr_np:.4f} "
            f"differ by more than 3 pp"
        )
