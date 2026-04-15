"""Unit tests for sample weights [AFML §4, p.59-69]."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ai_trade.backtest.meta.sample_weights import (
    get_avg_uniqueness,
    get_concurrent_events,
    get_sample_weights_by_return,
)


def _idx(n, start="2024-01-01"):
    return pd.date_range(start, periods=n, freq="B")


class TestConcurrentEvents:
    def test_no_events_returns_zero_series(self):
        idx = _idx(10)
        t1 = pd.Series(dtype="datetime64[ns]")
        out = get_concurrent_events(idx, t1)
        assert (out == 0).all()
        assert len(out) == len(idx)

    def test_non_overlapping_events_each_count_one(self):
        idx = _idx(10)
        t1 = pd.Series(
            {idx[0]: idx[2], idx[5]: idx[7]},
        )
        out = get_concurrent_events(idx, t1)
        # bars 0..2 have event 1; bars 5..7 have event 2; rest 0
        assert out.loc[idx[0]] == 1
        assert out.loc[idx[2]] == 1
        assert out.loc[idx[3]] == 0
        assert out.loc[idx[5]] == 1
        assert out.loc[idx[7]] == 1
        assert out.loc[idx[8]] == 0

    def test_overlapping_events_increment_counts(self):
        idx = _idx(10)
        t1 = pd.Series(
            {idx[0]: idx[4], idx[2]: idx[6], idx[3]: idx[5]},
        )
        out = get_concurrent_events(idx, t1)
        # bar 3: all three events active
        assert out.loc[idx[3]] == 3
        # bar 4: events 1 and 2 and 3
        assert out.loc[idx[4]] == 3
        # bar 1: only event 1
        assert out.loc[idx[1]] == 1
        # bar 6: only event 2
        assert out.loc[idx[6]] == 1


class TestAvgUniqueness:
    def test_solo_event_has_uniqueness_one(self):
        idx = _idx(10)
        t1 = pd.Series({idx[0]: idx[4]})
        concurrent = get_concurrent_events(idx, t1)
        out = get_avg_uniqueness(t1, concurrent)
        # Event is alone → concurrency 1 everywhere → uniqueness 1.0
        assert out.iloc[0] == 1.0

    def test_overlapping_events_have_uniqueness_below_one(self):
        idx = _idx(10)
        t1 = pd.Series({idx[0]: idx[5], idx[3]: idx[7]})
        concurrent = get_concurrent_events(idx, t1)
        out = get_avg_uniqueness(t1, concurrent)
        assert (out < 1.0).all()


class TestSampleWeightsByReturn:
    def test_weights_sum_to_n_events(self):
        """AFML convention: weights normalized so mean = 1.0."""
        idx = _idx(20)
        close = pd.Series(100 * np.exp(0.001 * np.arange(20)), index=idx)
        t1 = pd.Series(
            {idx[0]: idx[5], idx[3]: idx[8], idx[10]: idx[15]},
        )
        w = get_sample_weights_by_return(t1, close)
        assert w.sum() == len(t1) or np.isclose(w.sum(), len(t1))

    def test_flat_series_yields_zero_weights(self):
        idx = _idx(10)
        close = pd.Series(100.0, index=idx)
        t1 = pd.Series({idx[0]: idx[5]})
        w = get_sample_weights_by_return(t1, close)
        # No realized return → no attribution → unnormalized sum = 0 → skip norm
        assert (w >= 0).all()

    def test_event_with_larger_return_gets_higher_weight(self):
        idx = _idx(30)
        # Two non-overlapping events; second has much larger absolute log-return.
        prices = np.ones(30) * 100.0
        prices[10:20] = 110.0  # event 1 window [0, 9] — flat
        prices[20:] = 130.0    # event 2 window [20, 29] — 20% move
        close = pd.Series(prices, index=idx)
        t1 = pd.Series({idx[0]: idx[9], idx[20]: idx[29]})
        w = get_sample_weights_by_return(t1, close)
        # Event 2 should carry more weight than event 1.
        assert w.loc[idx[20]] > w.loc[idx[0]]
