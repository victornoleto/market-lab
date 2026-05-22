"""Testfolio data loader for studies.lrs.

Thin wrapper over :func:`market_lab.backtest.data.testfolio_loader.load_testfolio_series`
that returns the three series this study needs (``SPYSIM``, ``SSOSIM``,
``UPROSIM``) aligned on their common date index.

The testfol.io cache must exist at ``data/testfolio/cache/history.parquet``.
Regenerate by pulling SPYSIM, SPYSIM?L=2, SPYSIM?L=3 from testfol.io and
running ``scripts/extract_testfolio_json.py`` (no auth required as of
2026-05-22).

Citations
---------
* testfol.io as long-history backtest source: Phase 3.5b Task 7a
  (cross-check ``UPROSIM`` vs ``synthesize_letf_returns`` in
  ``src/market_lab/backtest/helpers/synthetic_letf.py``).
* SPYSIM = S&P 500 total-return proxy; SSOSIM/UPROSIM = daily 2×/3× proxy
  via Gayed synthesis formula ``r = L·r_SPX − fee/252``
  ``[leverage_for_the_long_run, p.16]``.
* Modern-era cutoff 1980-01-01: post-Bretton-Woods, post-1973-oil-shock,
  stable monetary regime. Excludes the 1929-32 Great Depression, which
  dominates any leveraged-strategy drawdown picture and is not informative
  for a forward-looking allocator.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from market_lab.backtest.data.testfolio_loader import load_testfolio_series

TICKERS = ("SPYSIM", "SSOSIM", "UPROSIM")

MODERN_ERA_START = pd.Timestamp("1980-01-01")


def load_phase0_data() -> pd.DataFrame:
    """Return aligned testfolio equity-curve series for SPY / SSO / UPRO.

    Columns: ``SPYSIM``, ``SSOSIM``, ``UPROSIM`` (equity curves normalised
    to 10,000 at each series' first bar — see testfolio_loader docstring).
    Rows: intersection of the three series' date indices.

    Use the column values to compute daily returns (``pct_change``) for
    each asset. Use ``SPYSIM`` levels directly for the SMA200 signal.
    """
    series = {t: load_testfolio_series(t) for t in TICKERS}
    df = pd.concat(series, axis=1, join="inner").dropna(how="any")
    df.index.name = "date"
    return df.astype(float)


@dataclass(frozen=True)
class ModernData:
    """Result of :func:`load_modern_data`.

    Attributes
    ----------
    full : pd.DataFrame
        All available bars, including the pre-cutoff buffer needed for SMA
        warmup. Use this to compute the regime signal.
    scoring_start : pd.Timestamp
        First trading day on or after the modern-era cutoff. All curves
        and scores should be aligned to this index onwards.
    """

    full: pd.DataFrame
    scoring_start: pd.Timestamp


def load_modern_data(start: pd.Timestamp | str = MODERN_ERA_START) -> ModernData:
    """Load testfolio data with a modern-era scoring start, preserving warmup.

    The full DataFrame keeps pre-``start`` bars so the SMA200 signal has
    its 200-day warmup; scoring code slices from ``scoring_start`` onwards
    (the first trading day on or after the cutoff).
    """
    df = load_phase0_data()
    cutoff = pd.Timestamp(start)
    scoring_start = df.index[df.index.searchsorted(cutoff, side="left")]
    return ModernData(full=df, scoring_start=scoring_start)
