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
