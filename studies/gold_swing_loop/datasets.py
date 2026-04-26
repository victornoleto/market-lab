"""Pre-committed dataset slicing for the gold swing loop.

Every iteration MUST use the same train/test/forward windows defined
here. Locking them prevents per-iter selection bias on the OOS edge.

Conventions
-----------
* train: in-sample window for parameter selection (NOT used in iter 001
  since the hypothesis is pre-committed; reserved for future ML/HMM iters)
* test:  primary OOS window — the one that drives Sharpe/CAGR/MDD scoring
         and counts toward the 7-gate G4 (OOS 70/30) check
* forward: stress-test window after iter 001 — drives G5 (FWD post-2022)

Citations
---------
* `[advances_fin_ml, p.222-223]` — DSR scoring requires fixed n_trials
  with stable OOS slicing (otherwise re-slicing inflates trial count)
* `[ml_for_algo_trading, ch.4]` — pre-commit windows before testing
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass(frozen=True)
class DatasetSlices:
    """Pre-committed train/test/forward dates for one dataset."""

    name: str
    train_start: str
    train_end: str
    test_start: str
    test_end: str
    forward_start: str
    forward_end: str
    rationale: str


# Daily windows for GLD (longest dataset; 21.4 y allows 10y train + 6y test +
# 5y forward stress). Forward starts 2020-01-01 to capture COVID + Ukraine
# + Indian-rupee weakness regime.
SLICE_GLD_LONG = DatasetSlices(
    name="gld_long",
    train_start="2004-11-18", train_end="2014-12-31",  # 10.1 y
    test_start="2015-01-01",  test_end="2019-12-31",   # 5.0 y (post-2013 stagnation + 2018-19 revival)
    forward_start="2020-01-01", forward_end="2026-04-15",  # 6.3 y (COVID + 2024-25 ATH cycle)
    rationale=(
        "10.1y train (covers 2008 GFC + 2011 peak + 2013 collapse); "
        "5.0y test (mid-cycle stagnation + 2018-19 revival); "
        "6.3y forward (COVID-era inflation hedge + 2024-25 all-time-high run)."
    ),
)

# Daily XAUUSD only goes back to 2020-01-02; 6.3y total. Use 2020-2023 train
# (4y) and 2024-2026 forward (2.3y) — no separate test window. Test = forward.
# Cross-dataset replication on gld_long compensates for short history.
SLICE_XAUUSD_REAL = DatasetSlices(
    name="xauusd_real",
    train_start="2020-01-02", train_end="2023-12-31",  # 4.0 y
    test_start="2024-01-01",  test_end="2026-04-17",   # 2.3 y
    forward_start="2024-01-01", forward_end="2026-04-17",  # = test (no separate forward)
    rationale=(
        "Short history (6.3y) doesn't allow 3-way split. 4y train (COVID + "
        "rates regime) → 2.3y test=forward (Fed pause + 2024 all-time-high run). "
        "Cross-dataset corroboration on gld_long is the primary OOS check."
    ),
)

# 1h XAUUSD: same calendar dates as xauusd_real for direct comparability.
SLICE_XAUUSD_INTRADAY = DatasetSlices(
    name="xauusd_intraday",
    train_start="2020-01-02", train_end="2023-12-31",
    test_start="2024-01-01",  test_end="2026-04-17",
    forward_start="2024-01-01", forward_end="2026-04-17",
    rationale=(
        "Same calendar windows as xauusd_real (same underlying, finer TF). "
        "Allows intraday entry/exit strategies to be compared head-to-head "
        "with the daily-bar version."
    ),
)


SLICES: dict[str, DatasetSlices] = {
    "gld_long":        SLICE_GLD_LONG,
    "xauusd_real":     SLICE_XAUUSD_REAL,
    "xauusd_intraday": SLICE_XAUUSD_INTRADAY,
}


def load_dataset(name: str) -> pd.DataFrame:
    """Load a dataset by name."""
    paths = {
        "gld_long":        "data/tiingo/daily/prices/GLD.parquet",
        "xauusd_real":     "data/tiingo/daily/prices/xauusd.parquet",
        "xauusd_intraday": "data/tiingo/1hour/prices/xauusd.parquet",
    }
    if name not in paths:
        raise KeyError(f"unknown dataset: {name}; valid: {list(paths)}")
    df = pd.read_parquet(paths[name])
    return df


def slice_window(
    df: pd.DataFrame,
    name: str,
    window: str,
) -> pd.DataFrame:
    """Slice a dataset by named window (``train``, ``test``, ``forward``).

    The window is INCLUSIVE on both ends.
    """
    sl = SLICES[name]
    if window == "train":
        start, end = sl.train_start, sl.train_end
    elif window == "test":
        start, end = sl.test_start, sl.test_end
    elif window == "forward":
        start, end = sl.forward_start, sl.forward_end
    elif window == "all":
        return df
    else:
        raise ValueError(f"unknown window: {window}")
    mask = (df.index >= start) & (df.index <= end)
    return df.loc[mask].copy()


__all__ = [
    "DatasetSlices",
    "SLICES",
    "SLICE_GLD_LONG",
    "SLICE_XAUUSD_REAL",
    "SLICE_XAUUSD_INTRADAY",
    "load_dataset",
    "slice_window",
]
