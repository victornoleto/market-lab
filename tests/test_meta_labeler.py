"""Integration smoke tests for MetaLabeler [AFML §3.6, p.50-54].

No sklearn dependency — uses a tiny hand-rolled ``DummyClassifier``
that satisfies the ``fit/predict_proba`` duck-type.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.meta.meta_labeler import MetaLabeler


class DummyClassifier:
    """Trivial "always return 0.5" classifier, for wiring tests only."""

    def __init__(self):
        self._fitted = False

    def fit(self, X, y, sample_weight=None):
        assert len(X) == len(y)
        if sample_weight is not None:
            assert len(sample_weight) == len(X)
            assert (np.asarray(sample_weight) >= 0).all()
        self._fitted = True
        return self

    def predict_proba(self, X):
        assert self._fitted, "classifier not fitted"
        n = len(X)
        # Shape (n, 2): prob of skip, prob of act.
        return np.column_stack([np.full(n, 0.5), np.full(n, 0.5)])


@pytest.fixture
def bullish_events():
    """Generate a tiny primary-signal event set on a gentle uptrend."""
    idx = pd.date_range("2024-01-01", periods=100, freq="B")
    close = pd.Series(100 * np.exp(0.001 * np.arange(100)), index=idx)
    events = pd.DataFrame(
        {
            "t1": [idx[i + 5] for i in (0, 10, 20, 30, 40, 50)],
            "trgt": [0.005] * 6,
            "side": [1] * 6,
        },
        index=[idx[i] for i in (0, 10, 20, 30, 40, 50)],
    )
    return close, events


class TestMetaLabelerWiring:
    def test_labels_cached_on_second_call(self, bullish_events):
        close, events = bullish_events
        ml = MetaLabeler(close=close, primary_events=events, classifier=DummyClassifier())
        a = ml.labels()
        b = ml.labels()
        assert a is b

    def test_weights_cached_on_second_call(self, bullish_events):
        close, events = bullish_events
        ml = MetaLabeler(close=close, primary_events=events, classifier=DummyClassifier())
        a = ml.sample_weights()
        b = ml.sample_weights()
        assert a is b

    def test_fit_passes_weights_through(self, bullish_events):
        close, events = bullish_events
        clf = DummyClassifier()
        ml = MetaLabeler(close=close, primary_events=events, classifier=clf)
        # Features: just use the event ts as a numeric feature (trivial).
        X = pd.DataFrame(
            {"feat": np.arange(len(events), dtype=float)},
            index=events.index,
        )
        ml.fit(X)
        assert clf._fitted

    def test_predict_proba_act_returns_series_with_aligned_index(self, bullish_events):
        close, events = bullish_events
        ml = MetaLabeler(
            close=close, primary_events=events, classifier=DummyClassifier(),
        )
        X = pd.DataFrame(
            {"feat": np.arange(len(events), dtype=float)},
            index=events.index,
        )
        ml.fit(X)
        proba = ml.predict_proba_act(X)
        assert isinstance(proba, pd.Series)
        assert (proba.index == X.index).all()
        assert ((proba >= 0) & (proba <= 1)).all()
        assert proba.name == "p_act"

    def test_end_to_end_on_stationary_data_yields_zero_labels(self):
        """Flat price → no barrier touched ever → all labels = 0."""
        idx = pd.date_range("2024-01-01", periods=50, freq="B")
        close = pd.Series(100.0, index=idx)
        events = pd.DataFrame(
            {
                "t1": [idx[-1], idx[-1]],
                "trgt": [0.02, 0.02],
                "side": [1, 1],
            },
            index=[idx[0], idx[10]],
        )
        ml = MetaLabeler(
            close=close, primary_events=events, classifier=DummyClassifier(),
        )
        labs = ml.labels()
        assert (labs["bin"] == 0).all()
