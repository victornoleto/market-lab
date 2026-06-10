"""Load macro indicators for Phase 2 crash-protection risk-signal overlay.

Data provenance (cached in ``data/external/macro/``):

* **EBP** (Excess Bond Premium) — Gilchrist & Zakrajšek 2012, monthly,
  1973-present. Source:
  ``federalreserve.gov/econres/notes/feds-notes/ebp_csv.csv``.
  Strong AER-backed recession predictor.
* **T10Y3M** (term spread, 10-year minus 3-month T-bill) — daily,
  1982-present. Source: ``fred.stlouisfed.org/series/T10Y3M``.
  Estrella-Mishkin 1998 probit backbone.
* **CAPE** (Shiller P-E, 10-year real-earnings smoothed) — monthly,
  1881-2023-09. Source: Yale Shiller ``ie_data.xls``.
  Campbell-Shiller 1988 valuation ratio.
* **VIX** (CBOE Volatility Index) — daily, 1990-present. Source:
  FRED ``VIXCLS`` (already cached at ``data/phase3_7/vix/``).

Honest-alignment lags (see spec §4.2; prevent look-ahead bias):

* EBP: 21 trading days (published ~30 calendar days after month end).
* T10Y3M: 1 trading day (available t+1).
* CAPE: 32 trading days (~45 calendar days for earnings to be reported).
* VIX: 0 (published same day at market close).

All loaders return a :class:`pd.Series` indexed by date, value-only. Use
:func:`resample_to_daily_with_lag` to align monthly series to a trading
calendar and apply the appropriate publish lag in one step.

Citations
---------
* Gilchrist & Zakrajšek (2012), AER 102(4). `[crashes_sp500_e_indicadores_preditivos.md]`
* Estrella & Mishkin (1998).
* Campbell & Shiller (1988).
* Honest alignment: ``[advances_fin_ml, p.31-34]``.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DEFAULT_CACHE = Path("data/external/macro")

# Publish lags (trading days). See module docstring for sources.
EBP_LAG_TD = 21
TERM_SPREAD_LAG_TD = 1
CAPE_LAG_TD = 32
VIX_LAG_TD = 0
# UNRATE: BLS Employment Situation for reference month m is released on the
# first Friday of month m+1 (~23 trading days after the FRED first-of-month
# stamp); 25 adds a 2-day buffer. Vintage caveat: FRED serves revised data.
UNRATE_LAG_TD = 25

__all__ = [
    "DEFAULT_CACHE",
    "EBP_LAG_TD",
    "TERM_SPREAD_LAG_TD",
    "CAPE_LAG_TD",
    "VIX_LAG_TD",
    "UNRATE_LAG_TD",
    "load_unrate_monthly",
    "apply_publish_lag",
    "align_monthly_to_daily",
    "resample_to_daily_with_lag",
    "load_ebp_monthly",
    "load_term_spread_daily",
    "load_cape_monthly",
    "load_vix_daily",
    "load_all_indicators",
]


def apply_publish_lag(series: pd.Series, n_trading_days: int) -> pd.Series:
    """Shift a daily series by ``n_trading_days`` bars to the right.

    ``n_trading_days == 0`` returns the input unchanged. Positive values
    introduce NaN for the first ``n_trading_days`` bars — the caller
    must drop or tolerate these rows (the base simulator already warms
    up with NaN MA values).
    """
    if n_trading_days < 0:
        raise ValueError(f"n_trading_days must be >= 0, got {n_trading_days}")
    if n_trading_days == 0:
        return series.copy()
    return series.shift(n_trading_days)


def align_monthly_to_daily(
    monthly: pd.Series, daily_index: pd.DatetimeIndex
) -> pd.Series:
    """Forward-fill a monthly series onto a daily trading calendar.

    ``monthly`` must be indexed by the first-of-month (or any consistent
    monthly stamp). Each daily bar inherits the most recent prior
    monthly value. Bars before the first monthly stamp become NaN.
    """
    daily = monthly.reindex(daily_index.union(monthly.index).sort_values()).ffill()
    return daily.reindex(daily_index)


def resample_to_daily_with_lag(
    monthly: pd.Series,
    daily_index: pd.DatetimeIndex,
    n_trading_days: int,
) -> pd.Series:
    """Align monthly → daily then apply publish lag.

    The lag is applied AFTER the daily ffill so each trading day ``t``
    observes the value that was public at ``t − n_trading_days``. This
    is the honest-alignment convention used throughout the project
    (see ``[advances_fin_ml, p.31-34]``).
    """
    daily = align_monthly_to_daily(monthly, daily_index)
    return apply_publish_lag(daily, n_trading_days)


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


def load_ebp_monthly(*, cache_dir: Path = DEFAULT_CACHE) -> pd.Series:
    """EBP monthly, indexed at first-of-month."""
    path = cache_dir / "ebp_monthly.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"EBP cache not found at {path}. Run the Phase 2 data-fetch step."
        )
    df = pd.read_parquet(path)
    if "ebp" not in df.columns:
        raise ValueError(
            f"EBP parquet missing 'ebp' column; got {df.columns.tolist()}"
        )
    s = df["ebp"].astype(float).copy()
    s.index = pd.DatetimeIndex(df.index).tz_localize(None)
    s.name = "ebp"
    return s.sort_index()


def load_term_spread_daily(*, cache_dir: Path = DEFAULT_CACHE) -> pd.Series:
    """T10Y3M daily, already in trading-day resolution."""
    path = cache_dir / "t10y3m_daily.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"T10Y3M cache not found at {path}. Run the Phase 2 data-fetch step."
        )
    df = pd.read_parquet(path)
    if "term_spread" not in df.columns:
        raise ValueError(
            f"T10Y3M parquet missing 'term_spread' column; got {df.columns.tolist()}"
        )
    s = df["term_spread"].astype(float).copy()
    s.index = pd.DatetimeIndex(df.index).tz_localize(None)
    s.name = "term_spread"
    return s.sort_index().dropna()


def load_cape_monthly(*, cache_dir: Path = DEFAULT_CACHE) -> pd.Series:
    """Shiller CAPE monthly, indexed at first-of-month."""
    path = cache_dir / "cape_monthly.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"CAPE cache not found at {path}. Run the Phase 2 data-fetch step."
        )
    df = pd.read_parquet(path)
    if "CAPE" not in df.columns:
        raise ValueError(
            f"CAPE parquet missing 'CAPE' column; got {df.columns.tolist()}"
        )
    s = df["CAPE"].astype(float).copy()
    s.index = pd.DatetimeIndex(df.index).tz_localize(None)
    s.name = "cape"
    return s.sort_index().dropna()


def load_unrate_monthly(*, cache_dir: Path = DEFAULT_CACHE) -> pd.Series:
    """UNRATE monthly (civilian unemployment rate, SA), first-of-month stamps.

    Source: FRED ``UNRATE`` via ``scripts/data_sprint/ingest_unrate_fred.py``.
    Use :data:`UNRATE_LAG_TD` with :func:`resample_to_daily_with_lag` for the
    honest publication alignment (BLS releases ~first Friday of the following
    month). Vintage caveat: FRED serves the latest revised series, not
    point-in-time ALFRED data.
    """
    path = cache_dir / "unrate_monthly.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"UNRATE cache not found at {path}. "
            "Run scripts/data_sprint/ingest_unrate_fred.py first."
        )
    df = pd.read_parquet(path)
    if "unrate" not in df.columns:
        raise ValueError(
            f"UNRATE parquet missing 'unrate' column; got {df.columns.tolist()}"
        )
    s = df["unrate"].astype(float).copy()
    s.index = pd.DatetimeIndex(df.index).tz_localize(None)
    s.name = "unrate"
    return s.sort_index().dropna()


def load_vix_daily(*, cache_dir: Path = DEFAULT_CACHE) -> pd.Series:
    """VIXCLS daily close."""
    path = cache_dir / "vix_daily.parquet"
    if not path.exists():
        # Fall back to phase3_7 legacy cache.
        legacy = Path("data/phase3_7/vix/VIXCLS.parquet")
        if legacy.exists():
            path = legacy
        else:
            raise FileNotFoundError(
                f"VIX cache not found at {path} or {legacy}. "
                "Run the Phase 2 data-fetch step."
            )
    df = pd.read_parquet(path)
    col = None
    for c in ("VIX", "close"):
        if c in df.columns:
            col = c
            break
    if col is None:
        raise ValueError(
            f"VIX parquet missing VIX/close column; got {df.columns.tolist()}"
        )
    s = df[col].astype(float).copy()
    s.index = pd.DatetimeIndex(df.index).tz_localize(None)
    s.name = "vix"
    return s.sort_index().dropna()


def load_all_indicators(
    daily_index: pd.DatetimeIndex, *, cache_dir: Path = DEFAULT_CACHE
) -> dict[str, pd.Series]:
    """Load the 4 indicators and align them to ``daily_index``.

    Each series is (a) forward-filled / reindexed to the daily trading
    calendar and (b) shifted by its publish lag. Returned series may
    contain leading NaN up to ``max(lag)`` bars.
    """
    out: dict[str, pd.Series] = {}
    # EBP — monthly with 21 TD lag.
    ebp = load_ebp_monthly(cache_dir=cache_dir)
    out["ebp"] = resample_to_daily_with_lag(ebp, daily_index, EBP_LAG_TD)

    # Term spread — daily with 1 TD lag.
    term = load_term_spread_daily(cache_dir=cache_dir)
    # Daily series doesn't need month alignment; reindex + lag.
    term_daily = term.reindex(daily_index.union(term.index).sort_values()).ffill()
    term_daily = term_daily.reindex(daily_index)
    out["term_spread"] = apply_publish_lag(term_daily, TERM_SPREAD_LAG_TD)

    # CAPE — monthly with 32 TD lag.
    cape = load_cape_monthly(cache_dir=cache_dir)
    out["cape"] = resample_to_daily_with_lag(cape, daily_index, CAPE_LAG_TD)

    # VIX — daily, no lag.
    vix = load_vix_daily(cache_dir=cache_dir)
    vix_daily = vix.reindex(daily_index.union(vix.index).sort_values()).ffill()
    vix_daily = vix_daily.reindex(daily_index)
    out["vix"] = apply_publish_lag(vix_daily, VIX_LAG_TD)

    return out
