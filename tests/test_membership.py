"""Offline tests for the point-in-time eligibility builders (survivorship diagnostic).

The load-bearing check is *key alignment*: the dict must be keyed so that
``core.eligible_assets_for_date`` resolves it for a rebalance month-end timestamp.
If keys don't align the mask silently no-ops (every month -> empty set -> skipped),
which would look like "membership did nothing" instead of failing loudly.
"""

from __future__ import annotations

import pandas as pd

from studies.momentum_v2.core import eligible_assets_for_date
from studies.momentum_v2.membership import (
    build_ipo_delist_eligibility,
    build_sp500_eligibility,
)

_INDEX = pd.bdate_range("2000-01-03", "2012-12-31")


def _write(path, text):
    path.write_text(text, encoding="utf-8")
    return path


def test_sp500_membership_intervals(tmp_path):
    csv = _write(tmp_path / "sp.csv", (
        "ticker,start_date,end_date\n"
        "AAA,2000-01-01,\n"            # open -> always a member from 2000
        "BBB,2000-01-01,2005-06-15\n"  # leaves mid-2005
        "ccc,2010-03-01,\n"            # joins 2010 (lowercase -> must be uppercased)
    ))
    elig = build_sp500_eligibility(csv, _INDEX)

    early = eligible_assets_for_date(elig, pd.Timestamp("2003-06-30"))
    late = eligible_assets_for_date(elig, pd.Timestamp("2011-01-31"))
    assert early == {"AAA", "BBB"}          # CCC not yet in; key-alignment resolves
    assert late == {"AAA", "CCC"}           # BBB left, CCC joined, case-normalized


def test_ipo_delist_eligibility_and_fallback(tmp_path):
    csv = _write(tmp_path / "av.csv", (
        "symbol,name,exchange,assetType,ipoDate,delistingDate,status\n"
        "ALIVE,Alive Inc,NYSE,Stock,1990-01-01,null,Active\n"
        "LATEIPO,Late Co,NASDAQ,Stock,2008-05-01,null,Active\n"
        "DEAD,Dead Co,NYSE,Stock,1995-01-01,2006-03-20,Delisted\n"
    ))
    assets = ["ALIVE", "LATEIPO", "DEAD", "NOTLISTED"]  # NOTLISTED absent -> fallback eligible
    elig = build_ipo_delist_eligibility(csv, assets, _INDEX)

    early = eligible_assets_for_date(elig, pd.Timestamp("2003-06-30"))
    late = eligible_assets_for_date(elig, pd.Timestamp("2011-01-31"))
    assert early == {"ALIVE", "DEAD", "NOTLISTED"}   # LATEIPO not public yet
    assert late == {"ALIVE", "LATEIPO", "NOTLISTED"}  # DEAD delisted 2006


def test_every_panel_month_has_a_key(tmp_path):
    """No rebalance month may fall through to an empty set by accident."""
    csv = _write(tmp_path / "sp.csv", "ticker,start_date,end_date\nAAA,2000-01-01,\n")
    elig = build_sp500_eligibility(csv, _INDEX)
    for ts in pd.DatetimeIndex(_INDEX).to_period("M").drop_duplicates():
        resolved = eligible_assets_for_date(elig, ts.to_timestamp("M"))
        assert resolved == {"AAA"}
