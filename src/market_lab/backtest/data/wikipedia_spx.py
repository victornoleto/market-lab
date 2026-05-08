"""Point-in-time SPX 500 constituents via Wikipedia scraping.

Source page:
    https://en.wikipedia.org/wiki/List_of_S%26P_500_companies

Two tables relevant to us:
    0. Current constituents — today's membership.
    1. Selected changes    — historical additions/removals, reasonably covered
       from ~2000 onward.

Reconstruction algorithm (see `constituents_on`):
    start = current_constituents
    for change in future_changes (where change.date > target_date, desc by date):
        if change.added_ticker:   result.discard(change.added_ticker)
        if change.removed_ticker: result.add(change.removed_ticker)

Intuition: start from today and "undo" every change that happened after the
target date, walking backwards through time.

Limitations — document in every backtest report that uses this source:

* The "Selected changes" table is **not exhaustive**. Pre-2000 coverage is
  thin and mid-history gaps exist. Bound backtest windows to 2000+ and
  document the residual bias (some stocks that were added and later removed
  within the window may be missing entirely).
* Ticker symbol reuse / rename events (e.g., GOOG vs GOOGL after the 2014
  split, FB→META in 2022) are not reconciled here. A strategy using this
  output must be robust to those gaps.
* Mergers / spin-offs may be listed as "removed" without clearly flagging
  the surviving entity.
* Wikipedia table structure may change without notice — this module is
  **brittle by design** until we migrate to a paid survivorship-free feed.
"""

from __future__ import annotations

import io
import logging
import urllib.request
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)

_USER_AGENT = (
    "market-lab/0.1 (+https://github.com/VictorNoleto/market-lab; research use)"
)

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_CACHE_DIR = _PROJECT_ROOT / ".cache" / "wikipedia"

WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"


def _flatten_changes_table(raw: pd.DataFrame) -> pd.DataFrame:
    """Convert the raw "Selected changes" table to [date, added, removed] rows.

    The Wikipedia changes table has a two-row header:
        Date | Added         | Removed       | Reason
             | Ticker | Security | Ticker | Security |

    `pandas.read_html(..., header=[0, 1])` produces MultiIndex columns like
    ("Date", "Date"), ("Added", "Ticker"), ("Added", "Security"),
    ("Removed", "Ticker"), ("Removed", "Security"), ("Reason", "Reason").
    We keep only the ticker columns.
    """
    df = raw.copy()
    if not isinstance(df.columns, pd.MultiIndex):
        raise ValueError(
            "Expected MultiIndex columns from read_html(header=[0,1]); "
            "Wikipedia table structure may have changed."
        )

    # Wikipedia has used both "Date" and "Effective Date" over time; match
    # anything whose top-level header *contains* "date".
    date_cols = [c for c in df.columns if "date" in c[0].lower()]
    added_cols = [c for c in df.columns if "added" in c[0].lower()]
    removed_cols = [c for c in df.columns if "removed" in c[0].lower()]
    if not date_cols or not added_cols or not removed_cols:
        raise ValueError(
            "Expected Date/Added/Removed groups in changes table; got "
            f"{list(df.columns)}"
        )

    added_ticker = next((c for c in added_cols if "ticker" in c[1].lower()), added_cols[0])
    removed_ticker = next((c for c in removed_cols if "ticker" in c[1].lower()), removed_cols[0])

    out = pd.DataFrame({
        "date": pd.to_datetime(df[date_cols[0]], errors="coerce"),
        "added": df[added_ticker].astype("string"),
        "removed": df[removed_ticker].astype("string"),
    })
    out = out.dropna(subset=["date"]).reset_index(drop=True)
    out["added"] = out["added"].where(out["added"].notna(), None)
    out["removed"] = out["removed"].where(out["removed"].notna(), None)
    return out


def constituents_on(
    target_date: date,
    current: set[str],
    changes: pd.DataFrame,
) -> set[str]:
    """Reconstruct the SPX 500 constituent set on `target_date`.

    `changes` columns: date (datetime64), added (str|None), removed (str|None).
    """
    required = {"date", "added", "removed"}
    if not required.issubset(changes.columns):
        raise ValueError(f"changes is missing columns: {required - set(changes.columns)}")

    target_ts = pd.Timestamp(target_date)
    future = changes[changes["date"] > target_ts]
    result = set(current)
    for _, row in future.iterrows():
        added = row["added"]
        removed = row["removed"]
        if isinstance(added, str) and added:
            result.discard(added)
        if isinstance(removed, str) and removed:
            result.add(removed)
    return result


@dataclass
class WikipediaSPX:
    """Scrape Wikipedia's SPX 500 page, cache the tables, reconstruct.

    Cached as parquet so re-runs are offline-friendly and deterministic.
    """

    cache_dir: Path = field(default_factory=lambda: DEFAULT_CACHE_DIR)

    def __post_init__(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @property
    def current_path(self) -> Path:
        return self.cache_dir / "spx_current.parquet"

    @property
    def changes_path(self) -> Path:
        return self.cache_dir / "spx_changes.parquet"

    def fetch_tables(self, use_cache: bool = True) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Return (current_constituents, changes) DataFrames from Wikipedia.

        Current: columns include "Symbol" and "Security" (company name).
        Changes: [date, added, removed] after `_flatten_changes_table`.
        """
        if use_cache and self.current_path.exists() and self.changes_path.exists():
            return (
                pd.read_parquet(self.current_path),
                pd.read_parquet(self.changes_path),
            )

        log.info("fetching Wikipedia SPX tables: %s", WIKIPEDIA_URL)
        # Wikipedia returns 403 to the default urllib User-Agent, so we fetch
        # the HTML once with a descriptive UA and feed the cached string to
        # read_html twice (cheaper than two round-trips anyway).
        req = urllib.request.Request(WIKIPEDIA_URL, headers={"User-Agent": _USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8")
        current_tables = pd.read_html(io.StringIO(html), header=0)
        changes_tables = pd.read_html(io.StringIO(html), header=[0, 1])

        current = current_tables[0]
        changes = _flatten_changes_table(changes_tables[1])

        if use_cache:
            current.to_parquet(self.current_path)
            changes.to_parquet(self.changes_path)
        return current, changes

    def current_tickers(self, use_cache: bool = True) -> set[str]:
        current, _ = self.fetch_tables(use_cache=use_cache)
        symbol_col = next(
            (c for c in current.columns if str(c).lower() in {"symbol", "ticker"}),
            None,
        )
        if symbol_col is None:
            raise ValueError(
                f"Expected Symbol/Ticker column in current table; got {list(current.columns)}"
            )
        return set(current[symbol_col].dropna().astype(str))

    def constituents_on(self, target_date: date, use_cache: bool = True) -> set[str]:
        """End-to-end: fetch + reconstruct on target_date."""
        current = self.current_tickers(use_cache=use_cache)
        _, changes = self.fetch_tables(use_cache=use_cache)
        return constituents_on(target_date, current, changes)
