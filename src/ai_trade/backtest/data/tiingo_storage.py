"""Persistent OHLCV storage for Tiingo data — survives subscription cancellation.

Layout under ``root/``::

    prices/{ticker}.parquet     # canonical 6-col OHLCV
    meta/{ticker}.json          # optional metadata (sector, exchange, ...)
    manifest.json               # {ticker → {first_date, last_date, n_bars,
                                #            asset_class, fetched_at}}

Design notes
------------
* **Single-writer convention.** The bulk download script is the writer; the
  backtest reads. No locking; if you need concurrent writers, consider
  DuckDB or Postgres instead.
* **Idempotent writes.** ``write(ticker, df)`` merges with any existing
  parquet for the ticker, dedup'ing by date (latest write wins on overlap).
  This makes the bulk download safely resumable.
* **Manifest as source of truth for ranges.** ``has(ticker, start, end)``
  consults the manifest only — it does not open the parquet, so it is O(1).
* **Asset class taxonomy** — ``equity``, ``etf``, ``index``, ``crypto``,
  ``forex``. Drives endpoint routing in ``TiingoSource`` and lets the bulk
  CLI filter by bucket.
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


@dataclass
class TiingoStorage:
    """Parquet-per-ticker store + JSON manifest.

    Parameters
    ----------
    root : Path
        Root directory. Created if missing. Recommended:
        ``Path("data/tiingo")`` (project-relative, gitignored under
        ``data/tiingo/prices/`` and ``data/tiingo/meta/`` while the
        manifest itself MAY be committed for traceability).
    """

    root: Path

    def __post_init__(self) -> None:
        self.root = Path(self.root)
        (self.root / _PRICES_DIR).mkdir(parents=True, exist_ok=True)
        (self.root / _META_DIR).mkdir(parents=True, exist_ok=True)
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

    def _price_path(self, ticker: str) -> Path:
        safe = ticker.replace("/", "_")
        return self.root / _PRICES_DIR / f"{safe}.parquet"

    # -- query --------------------------------------------------------------

    _COVERAGE_SLACK = timedelta(days=7)

    def has(self, ticker: str, start: date, end: date) -> bool:
        """True iff the manifest range for ``ticker`` covers ``[start, end]``.

        A 7-day slack is applied on each edge so requests bracketed by
        weekends/holidays (e.g. ``start=2014-01-01``, New Year's Day) are
        still considered covered by data that begins on the next trading
        day. Without this, a ``--start 2014-01-01`` bulk run would re-fetch
        every ticker on resume because ``first_date=2014-01-02``.
        """
        entry = self._manifest.get(ticker)
        if entry is None:
            return False
        first = date.fromisoformat(entry["first_date"])
        last = date.fromisoformat(entry["last_date"])
        return first <= start + self._COVERAGE_SLACK and last + self._COVERAGE_SLACK >= end

    def list_tickers(self, asset_class: str | None = None) -> list[str]:
        if asset_class is None:
            return sorted(self._manifest.keys())
        return sorted(
            t for t, e in self._manifest.items()
            if e.get("asset_class") == asset_class
        )

    # -- read/write ---------------------------------------------------------

    def read(
        self,
        ticker: str,
        start: date | None = None,
        end: date | None = None,
    ) -> pd.DataFrame:
        """Return the cached parquet, optionally sliced to ``[start, end]``."""
        if ticker not in self._manifest:
            raise KeyError(f"ticker {ticker!r} not in storage manifest")
        df = pd.read_parquet(self._price_path(ticker))
        if start is None and end is None:
            return df
        lo = pd.Timestamp(start) if start is not None else df.index.min()
        hi = pd.Timestamp(end) if end is not None else df.index.max()
        mask = (df.index >= lo) & (df.index <= hi)
        return df.loc[mask]

    def write(
        self,
        ticker: str,
        df: pd.DataFrame,
        asset_class: str,
    ) -> None:
        """Persist ``df`` for ``ticker``, merging with any existing data.

        On row-level overlap the new ``df`` wins (latest write).
        """
        if df.empty:
            log.warning("skipping empty write for %s", ticker)
            return

        path = self._price_path(ticker)
        if path.exists():
            existing = pd.read_parquet(path)
            # Concatenate then drop duplicates keeping last (= the new data)
            merged = pd.concat([existing, df])
            merged = merged[~merged.index.duplicated(keep="last")]
            merged = merged.sort_index()
        else:
            merged = df.sort_index()

        merged.to_parquet(path)

        self._manifest[ticker] = {
            "first_date": merged.index.min().date().isoformat(),
            "last_date": merged.index.max().date().isoformat(),
            "n_bars": int(len(merged)),
            "asset_class": asset_class,
            "fetched_at": datetime.now().isoformat(timespec="seconds"),
        }
        self._save_manifest()
