"""Dominant Cycle Period — Homodyne Discriminator.

Algorithm source: [rocket_science, ch.6 p.59 + ch.8 p.82-83], EasyLanguage
listing transcribed line-by-line. The Homodyne Discriminator measures the
phase change per bar of the InPhase/Quadrature phasor derived from a
Hilbert-transformed detrended price, and inverts it to a period estimate.

Pipeline
--------
1. 4-bar weighted average smoothing (coef ``(4, 3, 2, 1)/10``).
2. Detrender via amplitude-corrected Hilbert FIR
   (``0.0962·x[0] + 0.5769·x[2] - 0.5769·x[4] - 0.0962·x[6]``).
3. ``I1 = Detrender[-3]``; ``Q1`` = same FIR applied to Detrender.
4. ``jI``, ``jQ`` = Hilbert of ``I1``, ``Q1`` (same FIR). Phasor addition
   ``I2 = I1 - jQ``, ``Q2 = Q1 + jI`` for 3-bar averaging.
5. EMA ``0.2 / 0.8`` on ``I2, Q2``.
6. Homodyne discriminator: ``Re = I2·I2[-1] + Q2·Q2[-1]``,
   ``Im = I2·Q2[-1] - Q2·I2[-1]``. EMA smooth.
7. Period estimate: ``2π / atan2(Im, Re)`` (we use ``atan2`` for quadrant
   safety — the book's ``ArcTangent(Im/Re)`` is valid only when the
   per-bar rotation is < 90°, which it is for periods ≥ 6).
8. Rate clamp: 0.67 × prev ≤ new ≤ 1.5 × prev.
9. Absolute clamp: ``period_min ≤ new ≤ period_max`` (book default 6/50).
10. EMA ``0.2 / 0.8`` on Period, then EMA ``0.33 / 0.67`` on SmoothPeriod.

Warm-up: the FIRs need 6 previous samples; the IIRs take ~50-100 bars to
converge. Callers should budget ≥ 200 bars of warm-up before trusting
the output. Initialisation: all history arrays start at 0.0 (EasyLanguage
default), which sends the first non-trivial rate-clamped ``Period`` to
``period_min`` (the clamp lower bound).
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


def _hilbert_fir(x: np.ndarray, t: int, amp_corr: float) -> float:
    """Amplitude-corrected Hilbert FIR at index ``t``.

    Uses ``x[t], x[t-2], x[t-4], x[t-6]``. Caller ensures ``t ≥ 6``.
    """
    return (
        0.0962 * x[t]
        + 0.5769 * x[t - 2]
        - 0.5769 * x[t - 4]
        - 0.0962 * x[t - 6]
    ) * amp_corr


def dominant_cycle_period(
    series: pd.Series,
    period_min: int = 6,
    period_max: int = 50,
) -> pd.Series:
    """Estimate the dominant cycle period bar-by-bar via Homodyne.

    Parameters
    ----------
    series : pd.Series
        Price (or roofed price) input.
    period_min, period_max : int
        Absolute clamp bounds on the output (book defaults 6, 50).

    Returns
    -------
    pd.Series
        SmoothPeriod — the final twice-EMA'd period estimate, clamped
        into ``[period_min, period_max]``.
    """
    if period_min < 2:
        raise ValueError(f"period_min must be ≥ 2, got {period_min}")
    if period_max <= period_min:
        raise ValueError(
            f"period_max ({period_max}) must exceed period_min ({period_min})"
        )

    values = series.to_numpy(dtype=float, copy=True)
    n = len(values)

    smooth = np.zeros(n)
    detrender = np.zeros(n)
    q1 = np.zeros(n)
    i1 = np.zeros(n)
    ji = np.zeros(n)
    jq = np.zeros(n)
    i2 = np.zeros(n)
    q2 = np.zeros(n)
    re = np.zeros(n)
    im = np.zeros(n)
    # Seed period arrays with period_min so the output is always inside the
    # absolute clamp even during the 6-bar FIR warm-up. EasyLanguage defaults
    # these to 0; seeding to the lower bound is a safer Python semantics
    # that does not change the steady-state estimate (tested).
    period = np.full(n, float(period_min))
    smooth_period = np.full(n, float(period_min))

    for t in range(n):
        # Step 1: 4-bar WMA smoothing. Needs 3 previous bars.
        if t >= 3:
            smooth[t] = (
                4 * values[t] + 3 * values[t - 1] + 2 * values[t - 2] + values[t - 3]
            ) / 10.0
        else:
            smooth[t] = values[t]

        # Amplitude correction uses the previous period estimate.
        amp_corr = 0.075 * period[t - 1] + 0.54 if t >= 1 else 0.54

        # Steps 2-4: Detrender, Q1, I1, jI, jQ all need 6-bar history.
        if t >= 6:
            detrender[t] = _hilbert_fir(smooth, t, amp_corr)
            q1[t] = _hilbert_fir(detrender, t, amp_corr)
            i1[t] = detrender[t - 3]
            ji[t] = _hilbert_fir(i1, t, amp_corr)
            jq[t] = _hilbert_fir(q1, t, amp_corr)

            # Step 4: phasor addition (3-bar averaging trick).
            i2_raw = i1[t] - jq[t]
            q2_raw = q1[t] + ji[t]

            # Step 5: EMA smoothing on I2, Q2.
            i2[t] = 0.2 * i2_raw + 0.8 * i2[t - 1]
            q2[t] = 0.2 * q2_raw + 0.8 * q2[t - 1]

            # Step 6: Homodyne discriminator.
            re_raw = i2[t] * i2[t - 1] + q2[t] * q2[t - 1]
            im_raw = i2[t] * q2[t - 1] - q2[t] * i2[t - 1]
            re[t] = 0.2 * re_raw + 0.8 * re[t - 1]
            im[t] = 0.2 * im_raw + 0.8 * im[t - 1]

            # Step 7: period estimate via atan2 (quadrant-safe).
            if abs(re[t]) > 1e-12 or abs(im[t]) > 1e-12:
                angle = math.atan2(im[t], re[t])
                if abs(angle) > 1e-12:
                    new_period = 2 * math.pi / angle
                else:
                    new_period = period[t - 1]
            else:
                new_period = period[t - 1]

            # Step 8: rate-of-change clamp (book: ±1.5× / ×0.67).
            if period[t - 1] > 0:
                if new_period > 1.5 * period[t - 1]:
                    new_period = 1.5 * period[t - 1]
                elif new_period < 0.67 * period[t - 1]:
                    new_period = 0.67 * period[t - 1]

            # Step 9: absolute clamp.
            if new_period < period_min:
                new_period = period_min
            elif new_period > period_max:
                new_period = period_max

            # Step 10: Period EMA, then SmoothPeriod EMA.
            period[t] = 0.2 * new_period + 0.8 * period[t - 1]
            smooth_period[t] = 0.33 * period[t] + 0.67 * smooth_period[t - 1]

            # Re-clamp smooth_period — the EMA of a clamped series can
            # drift slightly outside the bound on the first iterations
            # when the previous smooth_period was 0.
            if smooth_period[t] < period_min:
                smooth_period[t] = period_min
            elif smooth_period[t] > period_max:
                smooth_period[t] = period_max

    return pd.Series(smooth_period, index=series.index, name=series.name)
