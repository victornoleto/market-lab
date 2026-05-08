"""SPX total-return daily loader — pre-2001 backfill via Ken French factors.

Tiingo SPY daily history begins 2001-05-14. The Phase 3 Lead B1 grid
demands the canonical Gayed splits

    IS:     1970-01-01 → 2000-12-31
    OOS:    2001-01-01 → 2015-12-31
    Stress: 2016-01-01 → 2026-04-15

so we must extend the SPX total-return series back to 1970 (and ideally
1926 for full Gayed-style robustness checks). The cleanest free,
academic-grade source is Kenneth French's daily factor file: the
``Mkt-RF`` column plus the ``RF`` column reconstructs the daily
value-weighted CRSP US equity total return — a near-perfect proxy for
SPX TR pre-2001 (correlation ~0.99 monthly with SP500-TR over the
post-1972 period; the small-cap tilt of CRSP-VW is the only material
divergence and washes out at monthly timescales).

Data flow
---------

1. ``fetch_ken_french_daily(cache_dir)`` downloads (and caches in
   ``data/ken_french/``) the Tuck/Dartmouth zip and returns a clean
   DataFrame with columns ``[mkt_rf, smb, hml, rf]`` in **decimal**
   format (KF ships percentages — we divide by 100 here so the rest of
   the codebase stays consistent with ``synthetic_letf.synthesize_letf_returns``
   which expects decimal returns).
2. ``compute_market_total_return(kf_df)`` returns ``Series = mkt_rf + rf``
   — daily total return of the US value-weighted equity market.
3. ``load_spx_tr_daily(start, end, cutoff_date, ...)`` stitches the
   pre-cutoff KF Mkt return with post-cutoff Tiingo SPY ``adj_close``
   pct-change. Result: a single, monotone-indexed daily TR series ready
   for :class:`ai_trade.backtest.strategies.letf_rotation.LETFRotationStrategy`.

Stitching rules
---------------

* KF supplies the daily return on every trading day **up to and
  including** ``cutoff_date`` — the cutoff itself is sourced from KF
  because Tiingo's first available *return* (``pct_change`` of
  ``adj_close``) is on ``cutoff_date + 1 trading day`` (the cutoff bar
  itself is the price anchor, not a return).
* Tiingo supplies every daily return strictly **after** ``cutoff_date``.
* No overlap, no gap; verified at the boundary by a unit test.
* No re-scaling at the seam: both inputs are already daily total-return
  decimals. Empirical seam-discontinuity is bounded by the
  CRSP-VW-vs-SPY-TR drift, which is < 1 bp/day on average.

Citations
---------

* Daily LRS uses S&P 500 total return; pre-1988 (when Yahoo's
  ``^SP500TR`` series begins) the standard academic substitute is the
  CRSP value-weighted index, of which Kenneth French's ``Mkt-RF``
  factor is the public proxy: ``[leverage_for_the_long_run, p.13, p.17]``
  (Gayed himself uses CRSP for pre-1990 robustness checks).
* SMA-on-monthly-or-daily as the regime signal (lookback 10 mo ≈ 200
  daily): ``[leverage_for_the_long_run, p.13, p.14, Table 6]``.
* Total-return decimal convention (consistent with
  ``synthetic_letf``): ``[leverage_for_the_long_run, p.16]``.
"""

from __future__ import annotations

import io
import logging
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)

__all__ = [
    "KEN_FRENCH_DAILY_URL",
    "DEFAULT_CACHE_DIR",
    "DEFAULT_TIINGO_CUTOFF",
    "parse_ken_french_csv",
    "fetch_ken_french_daily",
    "compute_market_total_return",
    "load_spx_tr_daily",
]


KEN_FRENCH_DAILY_URL = (
    "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
    "F-F_Research_Data_Factors_daily_CSV.zip"
)
"""Kenneth R. French data library — daily Fama-French 3 factors."""

DEFAULT_CACHE_DIR = Path("data/ken_french")
"""Where to persist the downloaded CSV (one file per fetch, dated)."""

DEFAULT_TIINGO_CUTOFF = pd.Timestamp("2001-05-14")
"""First trading day Tiingo has SPY daily for (per data/tiingo/manifest.json)."""


def parse_ken_french_csv(text: str) -> pd.DataFrame:
    """Parse the Ken French daily factors CSV text into a clean DataFrame.

    The CSV ships with a multi-line title header and a ``Copyright`` footer
    line. The data block starts at the first row whose first field looks
    like ``YYYYMMDD`` and ends at the last such row.

    Returns
    -------
    pd.DataFrame
        Columns: ``mkt_rf``, ``smb``, ``hml``, ``rf`` (all decimal —
        KF ships percent, we divide by 100). Index: pandas DatetimeIndex
        (daily), name ``date``.
    """
    rows: list[tuple[str, float, float, float, float]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        first = line.split(",", 1)[0].strip()
        # data line: YYYYMMDD as 8-digit int
        if len(first) == 8 and first.isdigit():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) != 5:
                continue
            try:
                rows.append(
                    (
                        parts[0],
                        float(parts[1]),
                        float(parts[2]),
                        float(parts[3]),
                        float(parts[4]),
                    )
                )
            except ValueError:
                continue

    if not rows:
        raise ValueError("Ken French CSV: no parseable data rows found")

    df = pd.DataFrame(
        rows, columns=["date", "mkt_rf", "smb", "hml", "rf"]
    )
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    df = df.set_index("date").sort_index()
    # KF ships percent (e.g. 0.09 means +0.09% / day). Convert to decimal.
    for col in ("mkt_rf", "smb", "hml", "rf"):
        df[col] = df[col] / 100.0
    return df


def fetch_ken_french_daily(
    cache_dir: Path | str = DEFAULT_CACHE_DIR,
    force: bool = False,
    timeout: float = 30.0,
) -> pd.DataFrame:
    """Download (and cache) the Ken French daily factors CSV.

    Parameters
    ----------
    cache_dir : Path | str
        Directory to persist the downloaded CSV. Created if missing.
    force : bool
        If True, re-download even if a cached copy exists.
    timeout : float
        HTTP timeout in seconds.

    Returns
    -------
    pd.DataFrame
        See :func:`parse_ken_french_csv`.
    """
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    csv_path = cache_dir / "F-F_Research_Data_Factors_daily.csv"

    if csv_path.exists() and not force:
        text = csv_path.read_text()
    else:
        log.info("Fetching Ken French daily factors from %s", KEN_FRENCH_DAILY_URL)
        with urllib.request.urlopen(KEN_FRENCH_DAILY_URL, timeout=timeout) as resp:
            zip_bytes = resp.read()
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            inner = [n for n in zf.namelist() if n.lower().endswith(".csv")]
            if not inner:
                raise RuntimeError(
                    "Ken French zip does not contain a CSV: "
                    + ", ".join(zf.namelist())
                )
            with zf.open(inner[0]) as f:
                text = f.read().decode("latin-1")
        csv_path.write_text(text)
        log.info("Cached Ken French CSV → %s (%d bytes)", csv_path, len(text))

    return parse_ken_french_csv(text)


def compute_market_total_return(kf_df: pd.DataFrame) -> pd.Series:
    """Daily total return of the US value-weighted equity market (decimal).

    ``mkt_rf`` is the daily excess return of the CRSP value-weighted
    index over the risk-free rate; adding ``rf`` recovers the raw total
    return (Gayed's pre-2001 SPX TR proxy).
    """
    for col in ("mkt_rf", "rf"):
        if col not in kf_df.columns:
            raise ValueError(f"missing required column '{col}' in kf_df")
    series = kf_df["mkt_rf"] + kf_df["rf"]
    series.name = "spx_tr_proxy"
    return series


def load_spx_tr_daily(
    start: str | datetime | pd.Timestamp,
    end: str | datetime | pd.Timestamp,
    cutoff_date: pd.Timestamp = DEFAULT_TIINGO_CUTOFF,
    tiingo_storage_root: Path | str = "data/tiingo",
    spy_ticker: str = "SPY",
    cache_dir: Path | str = DEFAULT_CACHE_DIR,
) -> pd.Series:
    """Stitched daily SPX total-return series 1970→present.

    Parameters
    ----------
    start, end : str | datetime | Timestamp
        Inclusive bounds on the returned series.
    cutoff_date : Timestamp
        Boundary between Ken French (pre) and Tiingo SPY (post). Defaults
        to ``2001-05-14`` (first SPY day in Tiingo manifest as of
        2026-04-16). KF returns indexed strictly **before** this date are
        used; Tiingo returns indexed **on or after** this date are used.
    tiingo_storage_root : Path | str
        Root of the Tiingo cache (the same directory the manifest lives
        in). Read-only here.
    spy_ticker : str
        Tiingo ticker symbol for SPY. Default ``SPY``.
    cache_dir : Path | str
        Where to persist the Ken French CSV.

    Returns
    -------
    pd.Series
        Daily decimal total-return series (e.g. 0.012 means +1.2%),
        DatetimeIndex sorted ascending, no NaN, name ``spx_tr_daily``.
    """
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    if end_ts <= start_ts:
        raise ValueError(f"end ({end_ts}) must be > start ({start_ts})")

    # Pre-cutoff: Ken French market total return.
    kf_df = fetch_ken_french_daily(cache_dir=cache_dir)
    kf_returns = compute_market_total_return(kf_df)
    pre = kf_returns.loc[
        (kf_returns.index >= start_ts) & (kf_returns.index <= cutoff_date)
    ]

    # Post-cutoff: Tiingo SPY adj_close pct_change. Importing here avoids a
    # hard dependency for callers that only use the parser/fetcher.
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage

    storage = TiingoStorage(Path(tiingo_storage_root))
    spy_df = storage.read(spy_ticker, frequency="daily")
    if "adj_close" not in spy_df.columns:
        raise RuntimeError(
            f"Tiingo {spy_ticker} daily missing 'adj_close' column"
        )
    spy_idx = pd.to_datetime(spy_df.index)
    spy_close = pd.Series(spy_df["adj_close"].values, index=spy_idx)
    spy_returns = spy_close.pct_change().dropna()
    post = spy_returns.loc[
        (spy_returns.index > cutoff_date) & (spy_returns.index <= end_ts)
    ]

    stitched = pd.concat([pre, post]).sort_index()
    # Defensive: drop accidental duplicate timestamps at the seam.
    stitched = stitched[~stitched.index.duplicated(keep="last")]
    stitched.name = "spx_tr_daily"
    if stitched.isna().any():
        raise RuntimeError(
            "stitched SPX TR series contains NaN — check seam alignment"
        )
    return stitched
