"""Meta-labeler: wrap a primary signal with a secondary classifier [AFML p.50-54].

Two-model pipeline (López de Prado §3.6):

1. **Primary model** (existing strategy — Ehlers, Clenow, …) emits
   ``side ∈ {-1, 0, +1}``: the direction we'd trade if we took the trade.
   Tuned for **recall**.

2. **Secondary model** (this module) predicts whether to ACT on the
   primary's side: binary ``take / skip``. Tuned for **precision** — it
   filters out false positives from the primary.

The secondary is fit on triple-barrier labels (``bin ≠ 0`` → trade was
profitable, ``bin = 0`` → vertical barrier / skip) with sample weights
from AFML §4. Position sizing can then scale by the secondary's
``predict_proba``.

This module is classifier-agnostic — it duck-types any object with
``fit(X, y, sample_weight)`` and ``predict_proba(X)``. That keeps the
core repo free of a hard sklearn dependency; callers injecting a
RandomForestClassifier pull sklearn on demand.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

import pandas as pd

from market_lab.backtest.meta.sample_weights import (
    get_concurrent_events,
    get_sample_weights_by_return,
)
from market_lab.backtest.meta.triple_barrier import apply_triple_barrier


@runtime_checkable
class _Classifier(Protocol):
    def fit(self, X, y, sample_weight=None): ...
    def predict_proba(self, X): ...


@dataclass
class MetaLabeler:
    """Binary ``take / skip`` classifier layered on primary signals.

    Parameters
    ----------
    close : pd.Series
        Price series for the instrument. Used for triple-barrier
        labeling, sample weights, and return attribution.
    primary_events : pd.DataFrame
        Indexed by ``t0``. Columns required:
          * ``t1``   — vertical barrier timestamp
          * ``trgt`` — volatility target (e.g. ATR/close)
          * ``side`` — ``+1`` long / ``−1`` short from the primary
    pt_sl : (pt, sl)
        Profit-taking and stop-loss multipliers on ``trgt``.
    classifier : _Classifier
        Injected sklearn-compatible estimator. Not fit until ``fit()``.
    """

    close: pd.Series
    primary_events: pd.DataFrame
    classifier: _Classifier
    pt_sl: tuple[float, float] = (1.0, 1.0)

    _labels: pd.DataFrame = field(init=False, default=None, repr=False)
    _weights: pd.Series = field(init=False, default=None, repr=False)

    def labels(self) -> pd.DataFrame:
        """Compute + cache triple-barrier labels."""
        if self._labels is None:
            self._labels = apply_triple_barrier(
                self.close, self.primary_events, self.pt_sl
            )
        return self._labels

    def sample_weights(self) -> pd.Series:
        """Compute + cache combined sample weights."""
        if self._weights is None:
            labs = self.labels()
            t1 = labs["t1_actual"].copy()
            concurrent = get_concurrent_events(self.close.index, t1)
            self._weights = get_sample_weights_by_return(
                t1, self.close, concurrent=concurrent
            )
        return self._weights

    def fit(self, features: pd.DataFrame) -> "MetaLabeler":
        """Train the secondary classifier on triple-barrier labels.

        Parameters
        ----------
        features : pd.DataFrame
            Indexed by event ``t0`` (must align with ``primary_events.index``).
            Columns are whatever state the user wants the classifier to
            consume (oscillator, DCP, regime, sector, etc.).
        """
        labs = self.labels()
        y = (labs["bin"] != 0).astype(int).reindex(features.index).fillna(0)
        w = self.sample_weights().reindex(features.index).fillna(0.0)
        self.classifier.fit(features.to_numpy(), y.to_numpy(), sample_weight=w.to_numpy())
        return self

    def predict_proba_act(self, features: pd.DataFrame) -> pd.Series:
        """Probability the trade is worth taking.

        Returns
        -------
        pd.Series
            Indexed by ``features.index``; values in [0, 1].
        """
        proba = self.classifier.predict_proba(features.to_numpy())
        # Convention: column 1 = positive class (take trade).
        if proba.shape[1] == 1:
            values = proba[:, 0]
        else:
            values = proba[:, 1]
        return pd.Series(values, index=features.index, name="p_act")
