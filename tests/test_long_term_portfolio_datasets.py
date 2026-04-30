"""Tests for the long_term_portfolio dataset registry (lh_56y, vt_real, ndx_real)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def test_dataset_registry_lists_expected_datasets() -> None:
    from studies.long_term_portfolio.datasets import DATASETS

    # 2026-04-29: spy_real added for spy_beater_hunt (replaces vt_real/ndx_real
    # in that hunt; long_term_portfolio still uses lh_56y/vt_real/ndx_real).
    assert set(DATASETS.keys()) == {"lh_56y", "vt_real", "ndx_real", "spy_real"}
    for name, meta in DATASETS.items():
        assert "start" in meta and "end" in meta and "benchmark" in meta


def test_lh_56y_window_is_1970_to_2026() -> None:
    from studies.long_term_portfolio.datasets import DATASETS

    meta = DATASETS["lh_56y"]
    assert meta["start"] == "1970-01-02"
    assert meta["end"] >= "2026-04-17"


def test_load_prices_returns_dataframe_with_all_sim_columns() -> None:
    from studies.long_term_portfolio.datasets import load_prices

    df = load_prices("lh_56y")
    assert isinstance(df, pd.DataFrame)
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index[0] >= pd.Timestamp("1970-01-02")
    assert df.index[-1] >= pd.Timestamp("2026-04-17")
    for col in ("VTSIM", "SPYSIM", "IEFSIM", "GDESIM", "KMLMSIM", "CASHX"):
        assert col in df.columns, f"missing {col}"


def test_lh_56y_kmlmsim_column_has_no_nan_pre_1988() -> None:
    """The splice replaces pre-1988 NaNs with FF MoM proxy returns chained as equity."""
    from studies.long_term_portfolio.datasets import load_prices

    df = load_prices("lh_56y")
    pre_1988 = df.loc[:"1987-12-30", "KMLMSIM"]
    assert not pre_1988.isna().any(), "KMLMSIM should be splice-filled pre-1988"
    assert pre_1988.iloc[0] > 0
    # No spurious jumps: any single-day move > 30% would mean splice or scaling bug.
    daily_pct = pre_1988.pct_change().dropna().abs()
    assert daily_pct.max() < 0.30, f"unexpected daily move {daily_pct.max():.4f}"


def test_lh_56y_kmlmsim_pct_change_pre_1988_matches_ff_proxy() -> None:
    """pct_change of spliced KMLMSIM column 1970-1987 should equal FF MoM proxy returns."""
    from studies.long_term_portfolio.datasets import load_prices
    from studies.long_term_portfolio.ff_momentum_proxy import ff_momentum_proxy

    df = load_prices("lh_56y")
    spliced_returns = df["KMLMSIM"].pct_change().dropna()
    proxy = ff_momentum_proxy()
    pre = spliced_returns.loc["1970-01-05":"1987-12-30"]
    proxy_pre = proxy.loc[pre.index]
    assert np.allclose(pre.values, proxy_pre.values, atol=1e-9), \
        "spliced KMLMSIM pct_change should equal FF MoM proxy returns pre-1988"


def test_lh_56y_kmlmsim_post_1988_matches_raw_kmlmsim() -> None:
    """post-1988 KMLMSIM in the spliced frame matches raw testfolio KMLMSIM up to scale."""
    from studies.long_term_portfolio.datasets import load_prices
    from src.ai_trade.backtest.data.testfolio_loader import load_testfolio_series

    df = load_prices("lh_56y")
    raw = load_testfolio_series("KMLMSIM")
    spliced = df["KMLMSIM"].loc["1988-01-01":]
    raw_aligned = raw.loc[spliced.index]
    spliced_returns = spliced.pct_change().dropna()
    raw_returns = raw_aligned.pct_change().dropna()
    common = spliced_returns.index.intersection(raw_returns.index)
    assert np.allclose(
        spliced_returns.loc[common].values, raw_returns.loc[common].values, atol=1e-9
    ), "post-1988 returns should match raw KMLMSIM"


def test_load_prices_unknown_dataset_raises() -> None:
    from studies.long_term_portfolio.datasets import load_prices

    with pytest.raises(KeyError):
        load_prices("does_not_exist")


def test_vt_real_and_ndx_real_windows_unchanged() -> None:
    """Continuity: live-data datasets keep their historical windows."""
    from studies.long_term_portfolio.datasets import DATASETS

    assert DATASETS["vt_real"]["start"] == "2008-06-01"
    assert DATASETS["ndx_real"]["start"] == "2010-02-01"
