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
"""
from __future__ import annotations

import pandas as pd

from market_lab.backtest.data.testfolio_loader import load_testfolio_series

TICKERS = ("SPYSIM", "SSOSIM", "UPROSIM")


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
