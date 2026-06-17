"""Point-in-time eligibility universes for the momentum_v2 funnel.

Builds the `eligible_by_date` mask consumed at `core.eligible_assets_for_date`
(`core.py:293`) from FREE survivorship data, so each rebalance only ranks tickers
that were actually tradeable on that date. This attacks the *universe-selection*
slice of survivorship bias `[advances_fin_ml, p.208-211]`: today we apply "today's
surviving tickers" across all history. It does NOT add the prices of names that
died (panel stays survivor-only) -- that is a separate, deferred backfill.

Keys are `pd.Period("M").to_timestamp("M")` to match the fallback lookup in
`eligible_assets_for_date` exactly, so every rebalance month-end resolves.

Sources (both free, no API key for sp500). The CSVs live under
``studies/momentum_v2/data/`` and are gitignored (``studies/**/*.csv``) -- fetch them:

- sp500 (`fja05680/sp500`, MIT, ticker -> [start,end] in index, 1996+):
    curl -sL https://raw.githubusercontent.com/fja05680/sp500/master/sp500_ticker_start_end.csv \
      -o studies/momentum_v2/data/sp500_ticker_start_end.csv
- ipo_delist (Alpha Vantage `LISTING_STATUS`; needs a free key):
    curl "https://www.alphavantage.co/query?function=LISTING_STATUS&state=active&apikey=$ALPHAVANTAGE_API_KEY" \
      -o studies/momentum_v2/data/listing_status_active.csv
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

EligibleByDate = dict[pd.Timestamp, set[str]]


def _month_periods(prices_index) -> pd.PeriodIndex:
    """Unique calendar months spanning the price panel, as a PeriodIndex('M')."""
    return pd.DatetimeIndex(prices_index).to_period("M").drop_duplicates().sort_values()


def build_sp500_eligibility(csv_path: str | Path, prices_index) -> EligibleByDate:
    """Point-in-time S&P 500 membership from fja05680's ticker->interval CSV.

    A ticker is eligible in month `m` iff `start <= m <= end` (blank end = still a
    member). Multiple stints per ticker (e.g. AAL 1996-97 and 2015+) are separate
    rows and handled naturally. Symbols are uppercased to match the engine.
    """
    df = pd.read_csv(csv_path)
    start = pd.to_datetime(df["start_date"]).dt.to_period("M")
    end = pd.to_datetime(df["end_date"], errors="coerce").dt.to_period("M")  # NaT = open
    sym = df["ticker"].astype(str).str.upper()
    out: EligibleByDate = {}
    for per in _month_periods(prices_index):
        active = (start <= per) & (end.isna() | (per <= end))
        out[per.to_timestamp("M")] = set(sym[active])
    return out


def build_ipo_delist_eligibility(
    csv_path: str | Path, assets, prices_index
) -> EligibleByDate:
    """IPO/delisting eligibility for our own tickers from Alpha Vantage LISTING_STATUS.

    Eligible in month `m` iff `ipoDate <= m <= delistingDate` (missing dates = open).
    Tickers absent from the listing file stay eligible -- panel data availability
    already gates them, so we never *narrow* below what we can price.
    """
    universe = {str(a).upper() for a in assets}
    df = pd.read_csv(csv_path)
    df = df.assign(sym=df["symbol"].astype(str).str.upper())
    df = df[df["sym"].isin(universe)]
    ipo = pd.to_datetime(df["ipoDate"], errors="coerce").dt.to_period("M")
    delist = pd.to_datetime(df["delistingDate"], errors="coerce").dt.to_period("M")
    listed = set(df["sym"])
    fallback = universe - listed  # not in the listing file -> always eligible
    out: EligibleByDate = {}
    for per in _month_periods(prices_index):
        active = (ipo.isna() | (ipo <= per)) & (delist.isna() | (per <= delist))
        out[per.to_timestamp("M")] = set(df["sym"][active]) | fallback
    return out
