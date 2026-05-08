"""testfol.io long-history ETF-proxy loader.

Reads the parquet cache produced by ``scripts/extract_testfolio_json.py``
and returns per-ticker series that match the interface used by the rest
of the backtest module (``pd.Series`` indexed by date, float values).

Ticker coverage in the committed cache (1986-01-02 → 2026-04-17):

* **SPYSIM** — S&P 500 total-return proxy (dividends reinvested).
* **QQQSIM** — NASDAQ-100 total-return proxy.
* **GLDSIM** — LBMA PM gold fix minus ETF storage fee (~0.40%/yr).
* **ZROZSIM** — 25+ year zero-coupon US Treasury proxy.

For SSO (2× leveraged S&P), use
``ai_trade.backtest.strategies.letf_rotation.synthesize_letf_returns``
on ``load_testfolio_returns("SPYSIM")`` — this reuses the same
synthesis formula validated in Task 7a
(``reports/phase3_5b/robustness/testfolio_vs_synthetic_letf.md``).

Caveats
-------
* **Modelled, not measured.** Pre-IPO bars (QQQ pre-1999, GLD pre-2004)
  are simulated by testfol.io from index returns + ETF drag. Treat as
  approximations for stress testing, not tradeable history.
* **Retail trading costs** (spreads + commissions) are NOT modelled
  here; inject them per-strategy downstream.
* **Pre-2000 cost regime.** If extending the 3-leg backtest before
  2000, widen ``commission_bps`` + ``spread_bps`` on the switch layer
  (historical discount broker commissions were 50-100 bps round-trip).

Citations
---------
* testfol.io adopted as long-history source: Phase 3.5b Task 7a
  (cross-check UPROSIM vs our ``synthesize_letf_returns``).
* NDX official inception 1985-01-31; 1986 start matches testfol.io
  chart export default after trimming warmup.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

DEFAULT_CACHE_DIR = Path("data/testfolio/cache")
DEFAULT_HISTORY_PARQUET = DEFAULT_CACHE_DIR / "history.parquet"
DEFAULT_META_JSON = DEFAULT_CACHE_DIR / "history.meta.json"


def load_testfolio_frame(
    path: Path = DEFAULT_HISTORY_PARQUET,
) -> pd.DataFrame:
    """Return all cached testfol.io tickers as one DatetimeIndex frame.

    Columns are ticker labels (e.g. ``SPYSIM``); values are equity curves
    normalised to $10,000 at the first bar.
    """
    if not Path(path).exists():
        raise FileNotFoundError(
            f"{path} not found — run scripts/extract_testfolio_json.py first"
        )
    df = pd.read_parquet(path)
    df.index = pd.DatetimeIndex(df.index)
    return df.sort_index()


def load_testfolio_series(
    ticker: str, path: Path = DEFAULT_HISTORY_PARQUET,
) -> pd.Series:
    """Return the equity curve for ``ticker`` (case-insensitive)."""
    df = load_testfolio_frame(path)
    key = ticker.upper()
    if key not in df.columns:
        raise KeyError(
            f"ticker {ticker!r} not in cache — available: {list(df.columns)}"
        )
    s = df[key].astype(float)
    s.name = key
    return s


def load_testfolio_returns(
    ticker: str, path: Path = DEFAULT_HISTORY_PARQUET,
) -> pd.Series:
    """Daily pct_change for ``ticker``; first bar dropped (no prior)."""
    s = load_testfolio_series(ticker, path)
    return s.pct_change().dropna()


def load_testfolio_meta(path: Path = DEFAULT_META_JSON) -> dict:
    """Provenance metadata (source file, extraction date, labels)."""
    if not Path(path).exists():
        raise FileNotFoundError(f"{path} not found")
    return json.loads(Path(path).read_text(encoding="utf-8"))
