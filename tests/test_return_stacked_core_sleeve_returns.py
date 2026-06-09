from __future__ import annotations

import pandas as pd
import pytest

from studies.return_stacked_core.export_sleeve_returns import (
    RSST_DBMF_WEIGHT,
    RSST_FINANCING_SPREAD_ANNUAL,
    RSST_KMLM_WEIGHT,
    TRADING_DAYS,
    build_sleeve_returns,
)


def test_rsc_sleeve_returns_include_core_columns() -> None:
    frame = build_sleeve_returns()

    assert {"GDESIM", "RSSTSIM", "ZROZSIM", "SPYSIM", "KMLMSIM", "DBMFSIM", "CASHX"}.issubset(frame.columns)
    assert frame.index[0] <= pd.Timestamp("2000-01-04")
    assert frame.index[-1] >= pd.Timestamp("2026-05-21")
    assert not frame[["GDESIM", "RSSTSIM", "ZROZSIM"]].isna().any().any()


def test_rsst_proxy_uses_dbmf_kmlm_and_cashx_e_minus_2() -> None:
    frame = build_sleeve_returns()
    expected = (
        frame["SPYSIM"]
        + RSST_DBMF_WEIGHT * frame["DBMFSIM"]
        + RSST_KMLM_WEIGHT * frame["KMLMSIM"]
        - (frame["CASHX"] + RSST_FINANCING_SPREAD_ANNUAL / TRADING_DAYS)
    )

    pd.testing.assert_series_equal(frame["RSSTSIM"], expected, check_names=False)
    assert frame["RSSTSIM"].iloc[0] == pytest.approx(expected.iloc[0])
