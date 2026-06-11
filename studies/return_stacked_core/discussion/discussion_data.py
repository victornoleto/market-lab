"""Data layer for the RSC discussion sub-study.

Single source of truth for loading aligned daily-return matrices used by
all sNN scripts. Merges three stores:

1. ``data/testfolio/cache/history.parquet`` — slim testfolio price cache
   (SPYSIM/SSOSIM/UPROSIM 1885+, GLDSIM 1968+, IEFSIM/ZROZSIM 1962+, CASHX).
2. ``us_core/series/remote_prices.parquet`` — saved Testfol.io pulls
   (GDESIM 1968+, NTSXSIM 1962+, KMLMSIM 1988+, DBMFSIM 2000+, BTCSIM 2010-07+).
3. ``us_core/series/return_stacked_core_sleeve_returns.parquet`` — canonical
   aligned daily RETURNS matrix 2000-01-04..2026-05-21 (master calendar for
   the primary window).

Deliberately does NOT use ``datasets.load_prices`` — the slim cache lacks
KMLMSIM, so that loader raises KeyError (verified 2026-06-10).

Capital-efficient stacking and financing conventions follow the repo's
stacked-proxy model: weighted daily returns minus excess-notional CASHX
financing `[leverage_for_the_long_run, p.13]`, `[risk_parity, ch.5]`.

All loaders return daily simple returns unless the name says otherwise.
CASHX is an equity curve in the source stores — financing legs always use
``pct_change()`` of it, never assume zero.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

DISC_DIR = Path(__file__).resolve().parent
STUDY_DIR = DISC_DIR.parent
REPO_ROOT = STUDY_DIR.parents[1]

CACHE_PARQUET = REPO_ROOT / "data/testfolio/cache/history.parquet"
REMOTE_PARQUET = STUDY_DIR / "us_core/series/remote_prices.parquet"
SLEEVE_PARQUET = STUDY_DIR / "us_core/series/return_stacked_core_sleeve_returns.parquet"
AQR_CARRY_CSV = REPO_ROOT / "data/external/aqr/carry_monthly.csv"
KEN_FRENCH_DIR = REPO_ROOT / "data/ken_french"

SERIES_DIR = DISC_DIR / "series"
TABLES_DIR = DISC_DIR / "tables"
FIGURES_DIR = DISC_DIR / "figures"

# Mirrors export_sleeve_returns.py: RSST internal MF sleeve split and the
# Testfol.io payload financing convention (100% CASHX?E=-2 → 2.00%/yr drag).
RSST_DBMF_WEIGHT = 0.70
RSST_KMLM_WEIGHT = 0.30
FINANCING_SPREAD_ANNUAL = 0.0200
TRADING_DAYS = 252

# Master calendar bounds (sleeve matrix; cache ends one day later — trimmed).
PRIMARY_START = "2000-01-04"
PRIMARY_END = "2026-05-21"
EXTENDED_START = "1970-01-02"


def _pct(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.sort_index().pct_change()


def load_sleeve_returns() -> pd.DataFrame:
    """Canonical aligned daily returns 2000-01-04..2026-05-21 (master calendar)."""
    df = pd.read_parquet(SLEEVE_PARQUET).sort_index()
    return df


def load_cache_returns(columns: list[str]) -> pd.DataFrame:
    prices = pd.read_parquet(CACHE_PARQUET, columns=columns)
    return _pct(prices)


def load_remote_returns(columns: list[str]) -> pd.DataFrame:
    prices = pd.read_parquet(REMOTE_PARQUET, columns=columns)
    return _pct(prices)


def load_primary_returns() -> pd.DataFrame:
    """Daily returns matrix on the sleeve-matrix calendar (2000+).

    Columns: GDESIM, RSSTSIM, ZROZSIM, SPYSIM, KMLMSIM, DBMFSIM, GLDSIM,
    CASHX (sleeve matrix) + SSOSIM, UPROSIM, IEFSIM (cache) + NTSXSIM,
    BTCSIM (remote) + MFBLEND helper. NaNs are kept per-column (BTC starts
    2010-07); dropna policy is per-analysis, never global.
    """
    base = load_sleeve_returns()
    cache = load_cache_returns(["SSOSIM", "UPROSIM", "IEFSIM"])
    remote = load_remote_returns(["NTSXSIM", "BTCSIM"])
    out = base.join(cache, how="left").join(remote, how="left")
    out["MFBLEND"] = (
        RSST_DBMF_WEIGHT * out["DBMFSIM"] + RSST_KMLM_WEIGHT * out["KMLMSIM"]
    )
    return out


def ken_french_available() -> bool:
    return (
        (KEN_FRENCH_DIR / "F-F_Momentum_Factor_daily.csv").exists()
        and (KEN_FRENCH_DIR / "F-F_Research_Data_Factors_daily.csv").exists()
    )


def load_extended_returns() -> pd.DataFrame:
    """Daily returns 1970-01-02..2026-05-21 for the LOW-fidelity extended window.

    KMLM_SPLICED uses the Ken French UMD+RF academic momentum proxy pre-1988
    chained into remote KMLMSIM `[stocks_on_the_move, p.21-30]`. The splice
    overstates KMLM-like Sharpe pre-1988 (~3x, see datasets.py warning), so
    consumers must also build a haircut variant. Gold price was administered
    until 1971-08 (Bretton Woods) — disclose in any artifact using GLDSIM
    near the window start.

    Raises FileNotFoundError if the Ken French CSVs are absent (callers must
    check ken_french_available() and skip LOUDLY).
    """
    if not ken_french_available():
        raise FileNotFoundError(
            "Ken French CSVs missing in data/ken_french/ — extended window "
            "unavailable. See discussion/README.md for the one-time download."
        )
    from studies.return_stacked_core.ff_momentum_proxy import splice_kmlm_pre_1988

    cache = load_cache_returns(
        ["SPYSIM", "GLDSIM", "ZROZSIM", "IEFSIM", "CASHX", "SSOSIM", "UPROSIM"]
    )
    remote_prices = pd.read_parquet(
        REMOTE_PARQUET, columns=["GDESIM", "NTSXSIM", "KMLMSIM"]
    ).sort_index()
    remote = _pct(remote_prices[["GDESIM", "NTSXSIM"]])
    kmlm_spliced = splice_kmlm_pre_1988(remote_prices["KMLMSIM"].dropna())

    out = cache.join(remote, how="left")
    out["KMLM_SPLICED"] = kmlm_spliced.reindex(out.index)
    out = out.loc[EXTENDED_START:PRIMARY_END]
    return out


def load_carry_monthly() -> pd.Series:
    """AQR 'Century of Factor Premia' All Macro Carry, monthly excess returns.

    Multi-asset carry composite (equity indices, fixed income, currencies,
    commodities) — the closest long-history academic analog of RSSY's
    futures-yield sleeve. Excess returns are self-financing, so they stack
    onto SPY without a CASHX financing leg `[risk_parity, ch.5]`.
    Source: AQR Data Library, research-use with attribution (see METHODS.md).
    """
    if not AQR_CARRY_CSV.exists():
        raise FileNotFoundError(
            f"{AQR_CARRY_CSV} missing — run s01b_fetch_aqr_carry.py (network)."
        )
    df = pd.read_csv(AQR_CARRY_CSV, parse_dates=["Date"]).set_index("Date")
    return df["All Macro Carry"].dropna().sort_index()


def monthly_returns(daily: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    """Compound daily simple returns into calendar-month returns."""
    return (1.0 + daily).resample("ME").prod() - 1.0
