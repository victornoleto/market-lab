"""Synth vs real parity tests per spec §4.3.

Validates that synthetic LETF series reproduce real ETF post-inception returns
within per-ticker thresholds. Tests skip when Tiingo real-data is unavailable.

Citations
---------
* Tolerance rationale: [leverage_for_the_long_run, p.16, footnote 22-23]
  — 2× LETFs: 1pp CAGR tolerance; 3× LETFs: 3pp (vol-decay premium documented).
* TMF: 1.5pp due to bond duration sensitivity and spread variance.
"""
from __future__ import annotations

import pandas as pd
import pytest


PARITY_THRESHOLDS = {
    "UPRO": 0.03,
    "SSO": 0.01,
    "TQQQ": 0.03,
    "QLD": 0.01,
    "TMF": 0.015,
    "UGL": 0.01,
}


@pytest.mark.parametrize("ticker", list(PARITY_THRESHOLDS.keys()))
def test_synth_vs_real_within_threshold(ticker):
    """Synth CAGR ≈ Real CAGR within tolerance.

    Synth source per ticker (see run_iter_t0.build_synth_equity_curve):
      - UPRO/SSO/TQQQ/QLD → direct testfolio *SIM cache series
      - TMF → re-synth via letf_synth_by_ticker on TLTSIM underlying
        (no TMFSIM in testfolio cache; TLT 20yr is the documented proxy)
      - UGL → re-synth via letf_synth_by_ticker on GLDSIM underlying with
        calibrated ER=0.030 (iter 000 v2 measured ~3pp/yr UGLSIM drift)
    """
    from studies.letf_rotation_hunt.data_loader import load_tiingo_real_etf
    from studies.letf_rotation_hunt.run_iter_t0 import build_synth_equity_curve

    try:
        synth = build_synth_equity_curve(ticker)
        real = load_tiingo_real_etf(ticker)
    except (FileNotFoundError, KeyError, ValueError) as e:
        pytest.skip(f"Data not available for {ticker}: {e}")

    common_start = max(synth.index.min(), real.index.min())
    common_end = min(synth.index.max(), real.index.max())
    if (common_end - common_start).days < 365:
        pytest.skip(f"Insufficient overlap for {ticker}: {common_start} to {common_end}")

    synth_w = synth[common_start:common_end].dropna()
    real_w = real[common_start:common_end].dropna()
    if len(synth_w) < 252 or len(real_w) < 252:
        pytest.skip(f"Too few overlapping data points for {ticker}")

    synth_cagr = _cagr(synth_w)
    real_cagr = _cagr(real_w)

    threshold = PARITY_THRESHOLDS[ticker]
    delta = abs(synth_cagr - real_cagr)
    assert delta <= threshold, (
        f"{ticker}: synth_cagr={synth_cagr:.4f}, real_cagr={real_cagr:.4f}, "
        f"|delta|={delta:.4f} > threshold {threshold}"
    )


def test_build_synth_equity_curve_direct_sim():
    """For UPRO (and other direct-SIM tickers), returns the testfolio *SIM series."""
    from studies.letf_rotation_hunt.data_loader import load_testfolio_series
    from studies.letf_rotation_hunt.run_iter_t0 import build_synth_equity_curve

    series = build_synth_equity_curve("UPRO")
    expected = load_testfolio_series("UPROSIM")
    # Same shape; values may differ if helper normalizes — UPRO direct path
    # should pass-through unchanged.
    assert isinstance(series, pd.Series)
    assert len(series) == len(expected)
    pd.testing.assert_index_equal(series.index, expected.index)


def test_build_synth_equity_curve_tmf_resynth():
    """TMF has no TMFSIM in testfolio; resynthesizes from TLTSIM via FFR-aware formula."""
    from studies.letf_rotation_hunt.run_iter_t0 import build_synth_equity_curve

    series = build_synth_equity_curve("TMF")
    assert isinstance(series, pd.Series)
    series_clean = series.dropna()
    assert len(series_clean) >= 252, f"expected ≥252 obs, got {len(series_clean)}"
    assert (series_clean > 0).all(), "synth equity curve must be strictly positive"
    assert isinstance(series.index, pd.DatetimeIndex)


def test_build_synth_equity_curve_unknown_raises():
    """Unknown ticker (no parity source defined) must raise KeyError."""
    from studies.letf_rotation_hunt.run_iter_t0 import build_synth_equity_curve

    with pytest.raises(KeyError):
        build_synth_equity_curve("DEFINITELY_NOT_A_LETF_XYZ")


def _cagr(prices: pd.Series) -> float:
    """CAGR from price series."""
    n_years = (prices.index[-1] - prices.index[0]).days / 365.25
    if n_years < 0.1 or prices.iloc[0] <= 0:
        return float("nan")
    return (prices.iloc[-1] / prices.iloc[0]) ** (1 / n_years) - 1
