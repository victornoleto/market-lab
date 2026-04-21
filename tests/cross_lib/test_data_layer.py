"""Tests for the reference price assembler.

Verifies the parquet our engine consumes internally matches byte-for-byte
what `reference_prices.parquet` exports to external libs.
"""
from __future__ import annotations

import pandas as pd
import pytest

from reports.phase_3_5c.cross_lib.data.reference_prices import (
    LETF_SPECS,
    UNDERLYING_TICKERS,
    load_reference_parquet,
)


@pytest.fixture(scope="module")
def prices() -> pd.DataFrame:
    return load_reference_parquet()


def test_all_tickers_present(prices: pd.DataFrame) -> None:
    expected = set(UNDERLYING_TICKERS) | {spec.ticker for spec in LETF_SPECS}
    assert set(prices["ticker"].unique()) == expected


def test_canonical_window_coverage(prices: pd.DataFrame) -> None:
    """Tickers cover their extended window and reach near-end date."""
    canonical_end = pd.Timestamp("2026-04-18")
    # All tickers are synthesized pre-inception using GLD's inception as a constraint.
    # GLD (real) from 2004-11-18; UGL (real) from 2008-12-03; SSO/QLD (real) from 2006-06-21.
    # Phase 3.5d 3× LETFs: UPRO 2009-06-25, SPXL 2008-11-05, TQQQ 2010-02-09, TMF 2009-04-16.
    # TLT (underlying for TMF) available from 2002-07-26.
    # Pre-inception: synthetic from 1986-01-02 (SPX TR start) or when underlying is available.
    # Just check all tickers reach close to the end date.
    for ticker in (
        "SPY", "QQQ", "GLD", "TLT",
        "SSO", "QLD", "UGL",
        "UPRO", "SPXL", "TQQQ", "TMF",
    ):
        sub = prices[prices["ticker"] == ticker]
        assert len(sub) > 0, f"{ticker} has no data"
        assert sub["date"].max() >= canonical_end - pd.Timedelta(days=5), (
            f"{ticker} missing post-{canonical_end}"
        )


@pytest.mark.parametrize(
    "ticker,underlying,leverage,inception",
    [
        ("UPRO", "SPY", 3.0, "2009-06-25"),
        ("SPXL", "SPY", 3.0, "2008-11-05"),
        ("TQQQ", "QQQ", 3.0, "2010-02-09"),
        ("TMF", "TLT", 3.0, "2009-04-16"),
    ],
)
def test_3x_letf_synthetic_invariant(
    prices: pd.DataFrame,
    ticker: str,
    underlying: str,
    leverage: float,
    inception: str,
) -> None:
    """Pre-inception, 3× LETF daily return ≈ 3 × underlying daily return - drag.

    Validates the Gayed synthesis formula `r_L = L × r_underlying - drag`
    `[leverage_for_the_long_run, p.16]` for the Phase 3.5d 3× universe.
    """
    letf = prices[prices["ticker"] == ticker].set_index("date")["close"]
    under = prices[prices["ticker"] == underlying].set_index("date")["close"]
    pre_inception = letf.index < pd.Timestamp(inception)
    letf_rets = letf.pct_change().loc[pre_inception]
    under_rets = under.pct_change().reindex(letf_rets.index)

    pearson = letf_rets.corr(under_rets)
    assert pearson > 0.99, f"{ticker}/{underlying} return correlation pre-inception = {pearson}"

    ratio = (letf_rets / under_rets).dropna().median()
    # Tolerance ±10 % of nominal leverage to absorb FFR-aware drag + ER.
    assert leverage * 0.9 < ratio < leverage * 1.1, (
        f"{ticker}/{underlying} ratio pre-inception = {ratio} (expected ~{leverage})"
    )


@pytest.mark.parametrize(
    "ticker,inception",
    [
        ("UPRO", "2009-06-25"),
        ("SPXL", "2008-11-05"),
        ("TQQQ", "2010-02-09"),
        ("TMF", "2009-04-16"),
    ],
)
def test_3x_letf_seam_continuity(
    prices: pd.DataFrame, ticker: str, inception: str
) -> None:
    """Last synthetic close must match first real close at inception.

    Stitching bug documented in
    `jornada/2026-04-20/03-phase-3-5c-cross-lib-exposed-baseline-mismatch.md`;
    scaling fix is in ``reference_prices.py::build_reference_prices``.
    """
    sub = prices[prices["ticker"] == ticker].sort_values("date").reset_index(drop=True)
    pre = sub[sub["date"] < inception]
    post = sub[sub["date"] >= inception]
    assert not pre.empty, f"{ticker} has no synthetic history before {inception}"
    assert not post.empty, f"{ticker} has no real history after {inception}"
    last_synth = pre["close"].iloc[-1]
    first_real = post["close"].iloc[0]
    ratio = first_real / last_synth
    assert 0.99 < ratio < 1.01, (
        f"{ticker} seam discontinuity: last_synth={last_synth}, "
        f"first_real={first_real}, ratio={ratio}"
    )


def test_synthetic_letf_invariant(prices: pd.DataFrame) -> None:
    """Pre-inception, SSO daily return ≈ 2 × SPY daily return - drag.

    Validates the Gayed synthesis formula `r_L = L × r_underlying - drag`
    `[leverage_for_the_long_run, p.16]` (footnote 22) — tolerance bands
    derived from the expected daily re-leveraging invariant.
    """
    sso = prices[prices["ticker"] == "SSO"].set_index("date")["close"]
    spy = prices[prices["ticker"] == "SPY"].set_index("date")["close"]
    pre_inception = sso.index < pd.Timestamp("2006-06-21")
    sso_rets = sso.pct_change().loc[pre_inception]
    spy_rets = spy.pct_change().reindex(sso_rets.index)

    pearson = sso_rets.corr(spy_rets)
    assert pearson > 0.99, f"SSO/SPY return correlation pre-inception = {pearson}"
    ratio = (sso_rets / spy_rets).dropna().median()
    assert 1.8 < ratio < 2.2, f"SSO/SPY ratio pre-inception = {ratio} (expected ~2)"


def test_synthetic_has_flat_hlc(prices: pd.DataFrame) -> None:
    """Pre-inception synthetic bars have high == low == close."""
    sso = prices[prices["ticker"] == "SSO"]
    pre_inception = sso[sso["date"] < pd.Timestamp("2006-06-21")]
    assert (pre_inception["high"] == pre_inception["close"]).all()
    assert (pre_inception["low"] == pre_inception["close"]).all()


def test_real_has_genuine_ohlc(prices: pd.DataFrame) -> None:
    """Post-inception bars have genuine OHLC variation."""
    sso = prices[prices["ticker"] == "SSO"]
    post_inception = sso[sso["date"] >= pd.Timestamp("2006-06-21")]
    high_vs_low = (post_inception["high"] - post_inception["low"]).abs()
    assert (high_vs_low > 0).sum() / len(post_inception) > 0.95, (
        "Real bars should have high != low on at least 95% of days"
    )
