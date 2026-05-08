"""Tests for the Stage-2 validation helper (Phase 3.5e Tiingo-first fix)."""
from __future__ import annotations

import pandas as pd
import pytest

from studies._archive.phase_3_5c.reports.cross_lib.stage2_validation import (
    Stage2Result,
    load_testfolio_returns,
    run_stage2,
)


def test_spy_based_letfs_have_testfolio_reference() -> None:
    """SSO, UPRO, SPXL map to testfol.io SPY 2x/3x equity series."""
    for ticker in ("SSO", "UPRO", "SPXL"):
        returns = load_testfolio_returns(ticker)
        assert returns is not None, f"{ticker} must have a testfol.io reference"
        assert not returns.empty
        assert returns.index.min() <= pd.Timestamp("1885-03-23")  # first return after 1885-03-20


def test_non_spy_letfs_return_na() -> None:
    """QLD/TQQQ/UGL/TMF have no QQQSIM/GLDSIM/TLTSIM — Stage-2 is N/A."""
    for ticker in ("QLD", "TQQQ", "UGL", "TMF"):
        assert load_testfolio_returns(ticker) is None


def test_na_result_for_missing_ticker() -> None:
    result = run_stage2("QLD", cagr_stage1=0.15)
    assert result.status == "na"
    assert result.cagr_stage2 is None
    assert "QQQSIM" in result.reason or "No independent" in result.reason


def test_concordant_buy_hold_sso() -> None:
    """Buy-hold CAGR of testfol.io spy_2x_equity should be reproducible within tolerance.

    We use a known 10-year window and verify that passing the same CAGR back
    yields ΔCAGR ≈ 0 (concordance).
    """
    returns = load_testfolio_returns("SSO")
    assert returns is not None

    window_start = "2015-01-02"
    window_end = "2025-01-02"
    sub = returns.loc[window_start:window_end]
    total = float((1.0 + sub).prod())
    years = (sub.index[-1] - sub.index[0]).days / 365.25
    expected_cagr = total ** (1.0 / years) - 1.0

    result = run_stage2(
        "SSO",
        cagr_stage1=expected_cagr,
        window_start=window_start,
        window_end=window_end,
    )
    assert result.status == "concordant"
    assert result.cagr_delta_pp is not None and result.cagr_delta_pp < 0.01


def test_divergent_trips_gate() -> None:
    """A deliberately-wrong CAGR must produce divergent status."""
    returns = load_testfolio_returns("UPRO")
    assert returns is not None

    # Compute real CAGR on a window, then pretend Stage-1 was 10pp off.
    window_start = "2015-01-02"
    window_end = "2025-01-02"
    sub = returns.loc[window_start:window_end]
    total = float((1.0 + sub).prod())
    years = (sub.index[-1] - sub.index[0]).days / 365.25
    real_cagr = total ** (1.0 / years) - 1.0

    result = run_stage2(
        "UPRO",
        cagr_stage1=real_cagr + 0.10,
        window_start=window_start,
        window_end=window_end,
    )
    assert result.status == "divergent"
    assert result.cagr_delta_pp is not None and result.cagr_delta_pp >= 9.0


def test_custom_strategy_cagr_fn() -> None:
    """The strategy_cagr_fn hook lets callers reproduce non-buy-hold rules."""
    returns = load_testfolio_returns("SSO")
    assert returns is not None

    # Trivial "hold-nothing" strategy — CAGR should be 0.
    def zero_cagr(r: pd.Series) -> float:
        return 0.0

    result = run_stage2(
        "SSO",
        cagr_stage1=0.0,
        strategy_cagr_fn=zero_cagr,
        window_start="2020-01-02",
        window_end="2024-12-31",
    )
    assert result.status == "concordant"
    assert result.cagr_stage2 == 0.0
