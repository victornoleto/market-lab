"""AFML meta-labeling primitives.

López de Prado [advances_fin_ml]: rescue weak primary signals by wrapping
them with a secondary classifier trained on *triple-barrier* labels with
*sample weights* accounting for overlapping events and return magnitude.

Modules
-------
* ``triple_barrier``  — AFML §3.4, p.45-49. Labels events by which of the
  profit-taking / stop-loss / vertical barriers is hit first.
* ``sample_weights``  — AFML §4, p.59-69. Down-weights overlapping events
  (``get_concurrent_events``, ``get_avg_uniqueness``) and weights by
  realized-return magnitude (``get_sample_weights_by_return``).
* ``meta_labeler``    — AFML §3.6, p.50-54. Wraps a primary signal source
  with a secondary sklearn-compatible classifier trained on
  triple-barrier labels.

Re-exports purged K-Fold from ``backtest.validation.cpcv`` (already
implemented there) for convenience when training the secondary classifier.
"""

from ai_trade.backtest.meta.triple_barrier import apply_triple_barrier
from ai_trade.backtest.meta.sample_weights import (
    get_avg_uniqueness,
    get_concurrent_events,
    get_sample_weights_by_return,
)
from ai_trade.backtest.meta.meta_labeler import MetaLabeler
from ai_trade.backtest.validation.cpcv import purged_kfold_splits

__all__ = [
    "apply_triple_barrier",
    "get_avg_uniqueness",
    "get_concurrent_events",
    "get_sample_weights_by_return",
    "MetaLabeler",
    "purged_kfold_splits",
]
