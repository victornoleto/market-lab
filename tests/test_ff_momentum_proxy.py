"""Tests for the Fama-French momentum proxy used as pre-1988 KMLM substitute.

The proxy splices the academic UMD (momentum) factor + risk-free rate into
the lh_56y dataset for the pre-KMLMSIM portion (1970-01-02 → 1987-12-30).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]


def test_ff_momentum_proxy_loads_and_covers_pre_1988() -> None:
    """Series spans at minimum 1970-01-02 → 1987-12-30 (the splice window)."""
    from studies.return_stacked_core.ff_momentum_proxy import ff_momentum_proxy

    s = ff_momentum_proxy()
    assert isinstance(s, pd.Series)
    assert s.index.is_monotonic_increasing
    assert s.index[0] <= pd.Timestamp("1970-01-02")
    assert s.index[-1] >= pd.Timestamp("1987-12-30")


def test_ff_momentum_proxy_daily_values_are_reasonable() -> None:
    """Daily returns are in [-25%, +25%] — sanity check for percent-vs-decimal.

    Bound is wide because the momentum factor experienced extreme drawdowns
    during the 2007/2009 momentum crashes (~-19% daily). Anything beyond
    ±25% would indicate a percent-vs-decimal scaling bug.
    """
    from studies.return_stacked_core.ff_momentum_proxy import ff_momentum_proxy

    s = ff_momentum_proxy()
    assert s.between(-0.25, 0.25).all(), (
        f"out-of-range daily returns: min={s.min()}, max={s.max()}"
    )


def test_ff_momentum_proxy_annualized_stats_are_sensible() -> None:
    """Vol in [4%, 25%]/yr; mean positive — momentum premium has been positive long-term."""
    from studies.return_stacked_core.ff_momentum_proxy import ff_momentum_proxy

    s = ff_momentum_proxy()
    window = s.loc["1970-01-02":"1987-12-30"]
    ann_vol = window.std() * np.sqrt(252)
    ann_mean = window.mean() * 252
    assert 0.04 <= ann_vol <= 0.25, f"unexpected vol: {ann_vol:.4f}"
    assert ann_mean > 0, f"momentum should have positive mean over 1970-1987: {ann_mean:.4f}"


def test_ff_momentum_proxy_no_nans_in_splice_window() -> None:
    """No NaN/missing rows in 1970-01-02 → 1987-12-30."""
    from studies.return_stacked_core.ff_momentum_proxy import ff_momentum_proxy

    s = ff_momentum_proxy()
    window = s.loc["1970-01-02":"1987-12-30"]
    assert not window.isna().any()
    assert len(window) > 4500  # ~252 days * 18y = 4536


def test_ff_momentum_proxy_handles_missing_files_gracefully() -> None:
    """If the source CSVs are missing, raises FileNotFoundError with helpful message."""
    from studies.return_stacked_core.ff_momentum_proxy import ff_momentum_proxy

    bogus = Path("/tmp/does_not_exist_ff_mom.csv")
    with pytest.raises(FileNotFoundError):
        ff_momentum_proxy(mom_csv=bogus)
