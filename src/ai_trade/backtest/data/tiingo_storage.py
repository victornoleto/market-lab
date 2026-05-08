"""Persistent OHLCV storage for Tiingo data — survives subscription cancellation.

Layout under ``root/``::

    {frequency}/prices/{ticker}.parquet     # canonical 6-col OHLCV per freq
    {frequency}/meta/{ticker}.json          # optional metadata per freq
    manifest.json                           # nested:
                                            #   {ticker: {freq: entry}}
                                            # entry: {first_dt, last_dt,
                                            #         n_bars, asset_class,
                                            #         fetched_at,
                                            #         requested_start,
                                            #         requested_end}
    .migration.lock                         # presence ⇒ migration half-done,
                                            # refuse init until rollback.

Design notes
------------
* **Single-writer convention.** The bulk download script is the writer; the
  backtest reads. No locking; if you need concurrent writers, consider
  DuckDB or Postgres instead.
* **Idempotent writes.** ``write(ticker, df, frequency=...)`` merges with any
  existing parquet for the (ticker, frequency) pair, dedup'ing by timestamp
  (latest write wins on overlap). This makes the bulk download safely
  resumable.
* **Manifest as source of truth for ranges.** ``has(ticker, start, end,
  frequency=...)`` consults the manifest only — it does not open the
  parquet, so it is O(1). Per-(asset_class, frequency) coverage slack
  absorbs weekend/holiday edges (daily) and overnight gaps (intraday).
* **Asset class taxonomy** — ``equity``, ``etf``, ``index``, ``crypto``,
  ``forex``. Drives endpoint routing in ``TiingoSource`` and the
  `_COVERAGE_SLACK` lookup in ``has()``.
* **Nested manifest** lets the same ticker hold multiple frequencies
  (e.g. ``SPY/daily`` + ``SPY/1hour``) without collision, which §2.5 of
  the intraday pivot needs.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)


_MANIFEST_NAME = "manifest.json"
_PRICES_DIR = "prices"
_META_DIR = "meta"
_LOCKFILE = ".migration.lock"


# Per-(asset_class, frequency) slack tolerance for ``has()`` coverage
# matching. Values chosen so typical weekend/holiday/overnight gaps do not
# force refetch of already-cached data, but genuinely-missing ranges still
# miss. Rationale:
# * Equity/ETF/index daily: 7d covers the longest holiday cluster (Xmas
#   week or Thanksgiving+Black Friday).
# * Crypto daily: 2d — crypto trades 24/7, gaps beyond a weekend are real
#   missing data.
# * Forex daily: 4d — weekend + bank holiday (e.g. US Monday).
# * Equity/ETF 1hour: 12h — covers the US overnight gap (16:00→09:30).
# * Crypto 1hour: 6h — tighter because 24/7.
# * Forex 1hour: 48h — weekend shutdown (Fri 17:00 → Sun 17:00 NY).
# Citation: project choice, not book-sourced — documented here so the
# slack values are auditable.
_COVERAGE_SLACK: dict[tuple[str, str], timedelta] = {
    ("equity", "daily"):  timedelta(days=7),
    ("etf",    "daily"):  timedelta(days=7),
    ("index",  "daily"):  timedelta(days=7),
    ("crypto", "daily"):  timedelta(days=2),
    ("forex",  "daily"):  timedelta(days=4),
    ("equity", "1hour"):  timedelta(hours=12),
    ("etf",    "1hour"):  timedelta(hours=12),
    ("index",  "1hour"):  timedelta(hours=12),
    ("crypto", "1hour"):  timedelta(hours=6),
    ("forex",  "1hour"):  timedelta(hours=48),
}

# Default slack used when the (asset_class, frequency) pair is absent from
# the lookup table — matches legacy behaviour for unknown combos.
_DEFAULT_SLACK = timedelta(days=7)


@dataclass
class TiingoStorage:
    """Parquet-per-ticker store + nested JSON manifest.

    Parameters
    ----------
    root : Path
        Root directory. Created if missing. Recommended:
        ``Path("data/tiingo")`` (project-relative, gitignored under
        ``data/tiingo/{freq}/prices/`` and ``data/tiingo/{freq}/meta/``
        while the manifest itself MAY be committed for traceability).
    """

    root: Path

    def __post_init__(self) -> None:
        self.root = Path(self.root)
        self._lockfile_path = self.root / _LOCKFILE
        if self._lockfile_path.exists():
            raise RuntimeError(
                f"migração incompleta detectada em {self.root} "
                f"(lockfile {_LOCKFILE} presente); execute rollback antes de usar."
            )
        # Default subdirs for the canonical `daily` frequency so first-time
        # init produces a usable layout. Other frequencies get their
        # subdirs lazily on first write (`_price_path().parent.mkdir(...)`).
        (self.root / "daily" / _PRICES_DIR).mkdir(parents=True, exist_ok=True)
        (self.root / "daily" / _META_DIR).mkdir(parents=True, exist_ok=True)
        self._manifest_path = self.root / _MANIFEST_NAME
        self._manifest: dict[str, dict] = self._load_manifest()

    # -- manifest I/O -------------------------------------------------------

    def _load_manifest(self) -> dict[str, dict]:
        if not self._manifest_path.exists():
            return {}
        try:
            return json.loads(self._manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"corrupt manifest at {self._manifest_path}: {exc}"
            ) from exc

    def _save_manifest(self) -> None:
        self._manifest_path.write_text(
            json.dumps(self._manifest, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    @property
    def manifest(self) -> dict[str, dict]:
        return self._manifest

    # -- price file paths ---------------------------------------------------

    def _price_path(self, ticker: str, frequency: str = "daily") -> Path:
        """Absolute path to the parquet for ``(ticker, frequency)``.

        Layout: ``root/{frequency}/prices/{ticker}.parquet``. Slash in
        ticker (e.g. forex ``eur/usd``) is normalized to underscore.
        """
        safe = ticker.replace("/", "_")
        return self.root / frequency / _PRICES_DIR / f"{safe}.parquet"

    # -- query --------------------------------------------------------------

    def has(
        self,
        ticker: str,
        start: date | datetime,
        end: date | datetime,
        frequency: str = "daily",
    ) -> bool:
        """True iff the manifest range for ``(ticker, frequency)`` covers
        ``[start, end]``.

        A per-(asset_class, frequency) slack is applied on each edge so
        requests bracketed by weekends/holidays/overnight are still
        considered covered by data whose first/last sample sits inside
        those gaps. See module-level ``_COVERAGE_SLACK`` for the table.
        """
        entry = self._manifest.get(ticker, {}).get(frequency)
        if entry is None:
            return False

        asset_class = entry.get("asset_class", "equity")
        slack = _COVERAGE_SLACK.get(
            (asset_class, frequency), _DEFAULT_SLACK,
        )

        first_dt = datetime.fromisoformat(entry["first_dt"])
        last_dt = datetime.fromisoformat(entry["last_dt"])

        start_is_date_only = not isinstance(start, datetime)
        end_is_date_only = not isinstance(end, datetime)

        start_dt = (
            start if isinstance(start, datetime)
            else datetime.combine(start, datetime.min.time())
        )
        # For a date-only end edge, expand to end-of-day so same-day
        # intraday bars still count as coverage.
        end_dt = (
            end if isinstance(end, datetime)
            else datetime.combine(end, datetime.max.time())
        )

        # When the caller passes date-only edges, they are asking "cover
        # this day" — a full trading-day slack (>= 24h) is the natural
        # interpretation so an intraday bar anywhere inside the day
        # counts as coverage. Intraday configured slacks (e.g. 12h for
        # equity 1h) stay tight when the caller uses datetime.
        effective_slack = slack
        if start_is_date_only or end_is_date_only:
            effective_slack = max(slack, timedelta(hours=24))

        return (
            first_dt <= start_dt + effective_slack
            and last_dt + effective_slack >= end_dt
        )

    def list_tickers(self, asset_class: str | None = None) -> list[str]:
        """Tickers present in the manifest, optionally filtered.

        A ticker matches ``asset_class`` iff ANY of its frequency entries
        has that class — in practice the class is invariant across
        frequencies for the same symbol, so this is a simple OR.
        """
        if asset_class is None:
            return sorted(self._manifest.keys())
        out = []
        for t, freq_entries in self._manifest.items():
            for entry in freq_entries.values():
                if entry.get("asset_class") == asset_class:
                    out.append(t)
                    break
        return sorted(out)

    # -- read/write ---------------------------------------------------------

    def read(
        self,
        ticker: str,
        start: date | datetime | None = None,
        end: date | datetime | None = None,
        frequency: str = "daily",
    ) -> pd.DataFrame:
        """Return the cached parquet for ``(ticker, frequency)``,
        optionally sliced to ``[start, end]``."""
        entry = self._manifest.get(ticker, {}).get(frequency)
        if entry is None:
            raise KeyError(
                f"ticker {ticker!r} (freq={frequency!r}) not in storage manifest"
            )
        df = pd.read_parquet(self._price_path(ticker, frequency))
        if start is None and end is None:
            return df
        # Expand date-only edges: date(D) as `end` means "end of day D" so
        # intraday bars at 14:00/15:00 on D still slice in; daily rows at
        # 00:00 also pass because lo stays at midnight. Mirror of `has()`.
        start_is_date_only = start is not None and not isinstance(start, datetime)
        end_is_date_only = end is not None and not isinstance(end, datetime)
        lo = (
            pd.Timestamp(datetime.combine(start, datetime.min.time()))
            if start_is_date_only
            else pd.Timestamp(start) if start is not None
            else df.index.min()
        )
        hi = (
            pd.Timestamp(datetime.combine(end, datetime.max.time()))
            if end_is_date_only
            else pd.Timestamp(end) if end is not None
            else df.index.max()
        )
        mask = (df.index >= lo) & (df.index <= hi)
        return df.loc[mask]

    def write(
        self,
        ticker: str,
        df: pd.DataFrame,
        asset_class: str,
        frequency: str = "daily",
        requested_start: date | datetime | None = None,
        requested_end: date | datetime | None = None,
    ) -> None:
        """Persist ``df`` for ``(ticker, frequency)``, merging with any
        existing data.

        On row-level overlap the new ``df`` wins (latest write). The
        ``requested_start``/``requested_end`` kwargs capture what the
        CALLER asked for (as opposed to ``first_dt``/``last_dt`` which
        reflect what the API actually returned). They are recorded in
        the manifest so §2.5 partial-fetch detection can warn when the
        returned range is narrower than the request.
        """
        if df.empty:
            log.warning("skipping empty write for %s (freq=%s)", ticker, frequency)
            return

        path = self._price_path(ticker, frequency)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Ensure meta subdir exists alongside prices so downstream callers
        # can write sidecar JSON without another mkdir.
        (self.root / frequency / _META_DIR).mkdir(parents=True, exist_ok=True)

        if path.exists():
            existing = pd.read_parquet(path)
            # Concatenate then drop duplicates keeping last (= the new data)
            merged = pd.concat([existing, df])
            merged = merged[~merged.index.duplicated(keep="last")]
            merged = merged.sort_index()
        else:
            merged = df.sort_index()

        merged.to_parquet(path)

        first_ts = pd.Timestamp(merged.index.min())
        last_ts = pd.Timestamp(merged.index.max())
        # Normalize to tz-naive — legacy storage was always naive (date-
        # indexed); intraday sources may come tz-aware from Tiingo.
        if first_ts.tzinfo is not None:
            first_ts = first_ts.tz_localize(None)
        if last_ts.tzinfo is not None:
            last_ts = last_ts.tz_localize(None)
        first_dt = first_ts.to_pydatetime()
        last_dt = last_ts.to_pydatetime()

        req_start_iso = _to_iso(requested_start) if requested_start is not None else first_dt.isoformat()
        req_end_iso = _to_iso(requested_end) if requested_end is not None else last_dt.isoformat()

        ticker_entry = self._manifest.setdefault(ticker, {})
        ticker_entry[frequency] = {
            "first_dt": first_dt.isoformat(),
            "last_dt": last_dt.isoformat(),
            "n_bars": int(len(merged)),
            "asset_class": asset_class,
            "fetched_at": datetime.now().isoformat(timespec="seconds"),
            "requested_start": req_start_iso,
            "requested_end": req_end_iso,
        }
        self._save_manifest()


def _to_iso(dt: date | datetime) -> str:
    """Coerce ``date | datetime`` to ISO string at midnight for plain dates."""
    if isinstance(dt, datetime):
        return dt.isoformat()
    return datetime.combine(dt, datetime.min.time()).isoformat()
