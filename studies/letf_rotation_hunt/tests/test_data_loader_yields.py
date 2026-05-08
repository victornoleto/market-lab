"""Tests for data_loader_yields (yields data fetcher).

T5 expansion adds yield data sources (CMT and dividend yield) backing
the Carver carry forecast in signals_carry.

Citations: spec docs/specs/2026-05-08-t5-expansion-design.md §3.2.
"""
from __future__ import annotations

import pandas as pd
import pytest

from studies.letf_rotation_hunt import data_loader_yields as dly


def test_load_cmt_known_tenors_return_series(monkeypatch, tmp_path):
    monkeypatch.setattr(dly, "_CACHE_DIR", tmp_path)
    fake = pd.Series(
        [0.044, 0.045, 0.046],
        index=pd.date_range("2024-01-02", periods=3, freq="D"),
        name="^TNX",
    )
    monkeypatch.setattr(dly, "_yfinance_fetch_yield", lambda ticker: fake)
    s = dly.load_constant_maturity_yield("10y")
    assert isinstance(s, pd.Series)
    assert (s == fake).all()


def test_load_cmt_unknown_tenor_raises():
    with pytest.raises(ValueError, match="tenor"):
        dly.load_constant_maturity_yield("7y")
