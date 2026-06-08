from __future__ import annotations

import numpy as np
import pandas as pd

from lrs.lib.indicators import (
    acf_decay_half_life,
    adaptive_vol_window,
    ewma_span_from_half_life,
)


def test_acf_decay_half_life_recovers_known_ar1() -> None:
    # AR(1) x_t = phi x_{t-1} + e has ACF(k)=phi^k, so half-life = ln0.5/ln(phi).
    phi = 0.9
    rng = np.random.default_rng(0)
    n = 200_000
    x = np.empty(n)
    x[0] = 0.0
    e = rng.standard_normal(n)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + e[t]
    s = pd.Series(x)

    hl = acf_decay_half_life(s, n_lags=10)

    expected = np.log(0.5) / np.log(phi)  # ~6.58
    assert abs(hl - expected) / expected < 0.20


def test_acf_decay_half_life_nan_for_white_noise() -> None:
    rng = np.random.default_rng(1)
    s = pd.Series(rng.standard_normal(50_000))

    hl = acf_decay_half_life(s, n_lags=10)

    # White noise has no positive decaying autocorrelation to fit.
    assert np.isnan(hl)


def test_ewma_span_from_half_life_matches_pandas_decay() -> None:
    # A span-N EWMA has alpha=2/(N+1); its half-life is ln0.5/ln(1-alpha).
    span = 100
    alpha = 2.0 / (span + 1)
    half_life = np.log(0.5) / np.log(1 - alpha)

    recovered = ewma_span_from_half_life(half_life)

    assert abs(recovered - span) < 1.0


def test_adaptive_vol_window_clips_and_is_lagged() -> None:
    rv = pd.Series([np.nan, 0.60, 0.05, 0.15], index=pd.RangeIndex(4))

    w = adaptive_vol_window(rv, w_base=200, vol_target=0.15, w_min=50, w_max=400)

    # raw = round(200*0.15/rv) = [nan, 50, 600, 200]; shift(1) -> [nan,nan,50,600];
    # warmup->w_base, clip to [50,400] -> [200, 200, 50, 400].
    assert w.tolist() == [200, 200, 50, 400]
    assert w.min() >= 50 and w.max() <= 400
    assert w.dtype.kind == "i"


def test_calmar_plateau_flat_surface_is_robust_and_contains_200() -> None:
    from lrs.phases.phase03c_lookback_study.run import calmar_plateau

    windows = np.array([50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 350, 400])
    calmar = np.full(len(windows), 0.40)  # perfectly flat
    calmar[6] = 0.41  # tiny bump at 200

    v = calmar_plateau(windows, calmar)

    assert v["has_plateau"] is True
    assert v["contains_target"] is True
    assert v["band_width"] >= 150
    assert v["is_fragile"] is False


def test_calmar_plateau_narrow_peak_is_fragile() -> None:
    from lrs.phases.phase03c_lookback_study.run import calmar_plateau

    windows = np.array([50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 350, 400])
    calmar = np.full(len(windows), 0.10)
    calmar[5] = 0.50  # sharp isolated peak at window 175, neighbours << 0.45

    v = calmar_plateau(windows, calmar)

    assert v["has_plateau"] is False
    assert v["is_fragile"] is True
    assert v["argmax_window"] == 175
