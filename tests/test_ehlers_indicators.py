"""Tests for Ehlers DSP primitives used by the Band-Pass Swing strategy.

Every filter is a stateful IIR operating on ``pandas.Series``. Tests use
synthetic signals so expected behavior can be stated numerically:

* **Impulse / step / constant** responses to verify IIR warm-up.
* **Sinusoidal inputs** to check frequency-domain behavior (pass/reject).
* **DC rejection** for high-pass and roofing filters.

All formulas are cited against ``books/summaries/cycle_analytics.md`` (Ehlers,
*Cycle Analytics for Traders*, 2013) — primary source of record for this
module.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# SuperSmoother — two-pole Butterworth with zero at Nyquist
# [cycle_analytics, eq. 3-3, p.33, ch.3]
# ---------------------------------------------------------------------------


class TestSuperSmoother:
    """``super_smoother(series, period)`` — [cycle_analytics, p.32-36, ch.3]."""

    def test_shape_and_index_preserved(self):
        from ai_trade.backtest.indicators.ehlers_ss import super_smoother

        idx = pd.date_range("2024-01-01", periods=50, freq="B")
        series = pd.Series(np.linspace(100.0, 110.0, 50), index=idx)

        out = super_smoother(series, period=10)

        assert isinstance(out, pd.Series)
        assert len(out) == len(series)
        assert out.index.equals(series.index)

    def test_constant_input_produces_constant_output(self):
        """DC passes through undistorted (SS has unity DC gain: c1 + c2 + c3 = 1).

        After the 2-bar warm-up, output must equal input exactly — no drift,
        no scale. [cycle_analytics, p.33, ch.3]
        """
        from ai_trade.backtest.indicators.ehlers_ss import super_smoother

        series = pd.Series([42.0] * 30)
        out = super_smoother(series, period=10)

        # Bars 0-1 are seeded with the input itself (IIR warm-up); from bar 2
        # onwards the recursion takes over and must hold the DC level.
        assert out.iloc[2:].values == pytest.approx(42.0, abs=1e-9)

    def test_attenuates_nyquist_oscillation(self):
        """Alternating ±1 signal (period 2 bars = Nyquist) is annihilated.

        SuperSmoother places a zero at Nyquist via the ``(Input + Input[-1])/2``
        numerator term. [cycle_analytics, p.32, ch.3]
        """
        from ai_trade.backtest.indicators.ehlers_ss import super_smoother

        n = 200
        series = pd.Series([1.0 if i % 2 == 0 else -1.0 for i in range(n)])

        out = super_smoother(series, period=10)

        # After the warm-up transient, amplitude must be near zero. The (P+P[-1])/2
        # pair-average alone collapses ±1 alternation to 0 exactly; the IIR
        # recursion then only amplifies tiny numerical residues of its own
        # previous output, so the steady-state amplitude is ~1e-2 order, not ~1.
        tail = out.iloc[50:]
        assert tail.abs().max() < 0.05

    def test_preserves_slow_signal(self):
        """Signal well below cutoff passes nearly unattenuated.

        Cutoff period = 10 bars means periods ≫ 10 are in the passband.
        """
        from ai_trade.backtest.indicators.ehlers_ss import super_smoother

        n = 400
        period = 80  # 8× longer than cutoff
        t = np.arange(n)
        series = pd.Series(np.sin(2 * np.pi * t / period))

        out = super_smoother(series, period=10)

        # After warmup, amplitude of filtered signal is within a few percent
        # of the input amplitude (1.0).
        tail = out.iloc[period:]
        input_tail = series.iloc[period:]
        # Align RMS as a conservative amplitude proxy.
        rms_in = float(np.sqrt((input_tail**2).mean()))
        rms_out = float(np.sqrt((tail**2).mean()))
        assert rms_out == pytest.approx(rms_in, rel=0.05)

    def test_rejects_short_period(self):
        from ai_trade.backtest.indicators.ehlers_ss import super_smoother

        series = pd.Series([1.0, 2.0, 3.0])
        with pytest.raises(ValueError):
            super_smoother(series, period=1)

    def test_attenuation_increases_with_frequency(self):
        """12 dB/octave roll-off: output amplitude for period=5 < period=20.

        Ehlers: ``attenuates aliasing noise at 12 dB per octave``
        [p.32, ch.3]. Period 5 is ~1 octave above cutoff 10; period 20 is
        ~1 octave below.
        """
        from ai_trade.backtest.indicators.ehlers_ss import super_smoother

        n = 400
        t = np.arange(n)
        fast = pd.Series(np.sin(2 * np.pi * t / 5))
        slow = pd.Series(np.sin(2 * np.pi * t / 20))

        fast_out = super_smoother(fast, period=10)
        slow_out = super_smoother(slow, period=10)

        rms_fast = float(np.sqrt((fast_out.iloc[50:] ** 2).mean()))
        rms_slow = float(np.sqrt((slow_out.iloc[50:] ** 2).mean()))

        # Slow passes, fast is attenuated — ratio should reflect the rolloff.
        # 12 dB/octave ≈ 4× amplitude ratio per octave; we are conservative.
        assert rms_slow / max(rms_fast, 1e-9) > 2.0

    def test_formula_matches_closed_form_first_steps(self):
        """Hand-computed first 3 output samples for period=10 must match.

        Given ``a = exp(-√2·π/10)``, ``b = 2·a·cos(√2·π/10)``, ``c2 = b``,
        ``c3 = -a²``, ``c1 = 1 - c2 - c3``:

        With input ``P = [1, 0, 0, 0, ...]`` and seeded ``Output[0]=1``,
        ``Output[1]=0``, the recursion at t=2 gives exactly
        ``Output[2] = c1 * (P[2] + P[1]) / 2 + c2 * Output[1] + c3 * Output[0]``
        = ``c3``.
        """
        from ai_trade.backtest.indicators.ehlers_ss import super_smoother

        period = 10
        a = math.exp(-math.sqrt(2) * math.pi / period)
        b = 2 * a * math.cos(math.sqrt(2) * math.pi / period)
        c3 = -a * a

        series = pd.Series([1.0, 0.0, 0.0, 0.0, 0.0])
        out = super_smoother(series, period=period)

        # Seeded warm-up: first two bars track the input verbatim.
        assert out.iloc[0] == pytest.approx(1.0)
        assert out.iloc[1] == pytest.approx(0.0)
        # Closed form at t=2.
        assert out.iloc[2] == pytest.approx(c3, rel=1e-9)


# ---------------------------------------------------------------------------
# Two-pole high-pass filter — [cycle_analytics, Code Listing 7-3, p.81-82, ch.7]
# ---------------------------------------------------------------------------


class TestHighPass:
    """``high_pass(series, period)`` — two-pole HP, ``.707`` K factor."""

    def test_shape_and_index_preserved(self):
        from ai_trade.backtest.indicators.ehlers_hp import high_pass

        idx = pd.date_range("2024-01-01", periods=50, freq="B")
        series = pd.Series(np.linspace(100.0, 110.0, 50), index=idx)

        out = high_pass(series, period=48)

        assert isinstance(out, pd.Series)
        assert len(out) == len(series)
        assert out.index.equals(series.index)

    def test_rejects_dc_after_warmup(self):
        """Constant input (DC) is zero-mean at the HP output after transient.

        High-pass transfer function has zero at DC by construction.
        """
        from ai_trade.backtest.indicators.ehlers_hp import high_pass

        series = pd.Series([42.0] * 300)
        out = high_pass(series, period=48)

        # Transient dies out within a couple of cutoff periods.
        tail = out.iloc[200:]
        assert tail.abs().max() < 1e-6

    def test_passes_fast_cycle(self):
        """Cycle well shorter than HP cutoff is in the passband → passes."""
        from ai_trade.backtest.indicators.ehlers_hp import high_pass

        n = 400
        period = 10  # much shorter than 48-bar HP cutoff
        t = np.arange(n)
        series = pd.Series(np.sin(2 * np.pi * t / period))

        out = high_pass(series, period=48)

        tail = out.iloc[100:]
        input_tail = series.iloc[100:]
        rms_in = float(np.sqrt((input_tail**2).mean()))
        rms_out = float(np.sqrt((tail**2).mean()))
        # Fast component mostly passes (some attenuation at the corner is OK).
        assert rms_out / rms_in > 0.7

    def test_attenuates_slow_cycle(self):
        """Cycle well longer than HP cutoff is attenuated by the HP."""
        from ai_trade.backtest.indicators.ehlers_hp import high_pass

        n = 800
        period = 200  # much longer than 48-bar HP cutoff
        t = np.arange(n)
        series = pd.Series(np.sin(2 * np.pi * t / period))

        out = high_pass(series, period=48)

        tail = out.iloc[300:]
        input_tail = series.iloc[300:]
        rms_in = float(np.sqrt((input_tail**2).mean()))
        rms_out = float(np.sqrt((tail**2).mean()))
        # Slow component is strongly suppressed.
        assert rms_out / rms_in < 0.3

    def test_rejects_invalid_period(self):
        from ai_trade.backtest.indicators.ehlers_hp import high_pass

        series = pd.Series([1.0] * 10)
        with pytest.raises(ValueError):
            high_pass(series, period=1)

    def test_formula_matches_closed_form_first_step(self):
        """Hand-computed first non-trivial output sample.

        With ``Close = [1, 0, 0]`` and HP[0]=HP[1]=0::

            HP[2] = (1 - α/2)² · (Close[2] - 2·Close[1] + Close[0])
                  = (1 - α/2)² · 1
        """
        from ai_trade.backtest.indicators.ehlers_hp import high_pass

        period = 48
        angle = math.sqrt(2) * math.pi / period
        alpha = (math.cos(angle) + math.sin(angle) - 1) / math.cos(angle)
        expected = (1 - alpha / 2) ** 2

        series = pd.Series([1.0, 0.0, 0.0])
        out = high_pass(series, period=period)

        assert out.iloc[0] == pytest.approx(0.0)
        assert out.iloc[1] == pytest.approx(0.0)
        assert out.iloc[2] == pytest.approx(expected, rel=1e-9)


# ---------------------------------------------------------------------------
# Roofing filter = HP + SuperSmoother — [cycle_analytics, p.88-89, ch.7]
# ---------------------------------------------------------------------------


class TestRoofingFilter:
    """``roofing_filter(series, hp_period, lp_period)`` — preprocessing
    mandatory before any Ehlers indicator [p.88-89, ch.7].
    """

    def test_shape_and_index_preserved(self):
        from ai_trade.backtest.indicators.ehlers_roofing import roofing_filter

        idx = pd.date_range("2024-01-01", periods=100, freq="B")
        series = pd.Series(np.linspace(100.0, 110.0, 100), index=idx)

        out = roofing_filter(series, hp_period=48, lp_period=10)

        assert isinstance(out, pd.Series)
        assert len(out) == len(series)
        assert out.index.equals(series.index)

    def test_removes_dc_component(self):
        """DC is annihilated by the HP stage."""
        from ai_trade.backtest.indicators.ehlers_roofing import roofing_filter

        series = pd.Series([100.0] * 300)
        out = roofing_filter(series, hp_period=48, lp_period=10)

        tail = out.iloc[200:]
        assert tail.abs().max() < 1e-6

    def test_removes_nyquist_noise(self):
        """Bar-by-bar alternation (Nyquist) is killed by the SS stage."""
        from ai_trade.backtest.indicators.ehlers_roofing import roofing_filter

        n = 300
        series = pd.Series([1.0 if i % 2 == 0 else -1.0 for i in range(n)])

        out = roofing_filter(series, hp_period=48, lp_period=10)

        tail = out.iloc[100:]
        # SS numerator zero collapses pair-alternation; IIR residues are tiny.
        assert tail.abs().max() < 0.05

    def test_passes_mid_band_cycle(self):
        """Cycle with period between LP cutoff and HP cutoff survives.

        With HP=48 and LP=10, the passband is roughly 10-48 bars
        [cycle_analytics, p.77, ch.7] — a 20-bar cycle sits squarely in it.
        """
        from ai_trade.backtest.indicators.ehlers_roofing import roofing_filter

        n = 600
        period = 20
        t = np.arange(n)
        series = pd.Series(100.0 + np.sin(2 * np.pi * t / period))  # DC + cycle

        out = roofing_filter(series, hp_period=48, lp_period=10)

        tail = out.iloc[200:]
        # The DC 100 is gone; the cycle amplitude (~1) should survive at
        # least halfway — two cascaded filters each impose some roll-off.
        rms_out = float(np.sqrt((tail**2).mean()))
        assert rms_out > 0.4
        # And the mean after warmup is near-zero (zero-mean preprocessor).
        assert abs(tail.mean()) < 0.05


# ---------------------------------------------------------------------------
# Dominant Cycle Period — Homodyne Discriminator
# [rocket_science, ch.6 p.59 + ch.8 p.82-83, EasyLanguage listing]
# ---------------------------------------------------------------------------


class TestDominantCyclePeriod:
    """``dominant_cycle_period(series, period_min=6, period_max=50)`` —
    Homodyne Discriminator from Ehlers, *Rocket Science for Traders*.
    """

    def test_shape_and_index_preserved(self):
        from ai_trade.backtest.indicators.ehlers_dcp import dominant_cycle_period

        n = 300
        idx = pd.date_range("2024-01-01", periods=n, freq="B")
        series = pd.Series(100.0 + np.sin(2 * np.pi * np.arange(n) / 20), index=idx)

        out = dominant_cycle_period(series)

        assert isinstance(out, pd.Series)
        assert len(out) == len(series)
        assert out.index.equals(series.index)

    def test_converges_on_pure_sine_period_20(self):
        """Pure 20-bar sinusoid → DCP settles in the 18-22 band.

        The heterodyne measures phase change per bar; with noise-free input
        the steady-state estimate is the true period. Tolerance accounts
        for the 0.2/0.8 and 0.33/0.67 EMA smoothing in the algorithm.
        """
        from ai_trade.backtest.indicators.ehlers_dcp import dominant_cycle_period

        n = 600
        t = np.arange(n)
        series = pd.Series(np.sin(2 * np.pi * t / 20))

        out = dominant_cycle_period(series)

        tail = out.iloc[400:]
        assert tail.mean() == pytest.approx(20.0, abs=2.0)

    def test_converges_on_pure_sine_period_30(self):
        from ai_trade.backtest.indicators.ehlers_dcp import dominant_cycle_period

        n = 800
        t = np.arange(n)
        series = pd.Series(np.sin(2 * np.pi * t / 30))

        out = dominant_cycle_period(series)

        tail = out.iloc[500:]
        assert tail.mean() == pytest.approx(30.0, abs=3.0)

    def test_output_always_within_absolute_clamp(self):
        """``[period_min, period_max]`` clamp is enforced unconditionally.

        [rocket_science, ch.8 p.82-83]: ``If Period<6 Then Period=6;
        If Period>50 Then Period=50``.
        """
        from ai_trade.backtest.indicators.ehlers_dcp import dominant_cycle_period

        # Mix of regimes — trend then fast noise then cycle — to stress the
        # clamp logic.
        n = 500
        rng = np.random.default_rng(seed=42)
        trend = np.linspace(100.0, 120.0, 150)
        noise = 100.0 + rng.normal(scale=2.0, size=200)
        cycle = 110.0 + np.sin(2 * np.pi * np.arange(150) / 15)
        series = pd.Series(np.concatenate([trend, noise, cycle]))

        out = dominant_cycle_period(series)

        assert out.min() >= 6.0 - 1e-9
        assert out.max() <= 50.0 + 1e-9

    def test_respects_custom_clamp_range(self):
        """``period_min / period_max`` parameters override defaults."""
        from ai_trade.backtest.indicators.ehlers_dcp import dominant_cycle_period

        n = 400
        rng = np.random.default_rng(seed=7)
        series = pd.Series(100.0 + rng.normal(scale=1.0, size=n))

        out = dominant_cycle_period(series, period_min=10, period_max=30)

        assert out.min() >= 10.0 - 1e-9
        assert out.max() <= 30.0 + 1e-9
