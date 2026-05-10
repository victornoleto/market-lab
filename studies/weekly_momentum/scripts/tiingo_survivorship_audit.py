#!/usr/bin/env python3
"""Audit and backfill Tiingo coverage for the weekly-momentum PIT universe.

The existing broad Tiingo downloader is useful, but its ``spx500`` bucket can
miss symbols that were added and removed inside the research window. This audit
builds a wider S&P 500 proxy universe from current members, reconstructed
members at the start date, and every Wikipedia selected-change add/remove row in
the window. The goal is to reduce survivorship bias before rerunning the frozen
``lb80/k5`` leads `[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import pandas as pd

from market_lab.backtest.data.tiingo_source import TiingoSource
from market_lab.backtest.data.tiingo_storage import TiingoStorage
from market_lab.backtest.data.wikipedia_spx import WikipediaSPX, constituents_on


DEFAULT_OUT_DIR = Path("studies/weekly_momentum/phase4_tiingo_survivorship_audit")
log = logging.getLogger("weekly_momentum.tiingo_survivorship_audit")


@dataclass(frozen=True)
class AuditRow:
    ticker: str
    in_current_sp500: bool
    in_start_sp500: bool
    appeared_as_added: bool
    appeared_as_removed: bool
    selected_change_dates: str
    likely_removed_or_renamed: bool
    pre_fetch_cached: bool
    attempted_fetch: bool
    fetch_status: str
    first_dt: str | None
    last_dt: str | None
    n_bars: int
    covers_research_start: bool
    covers_research_end: bool
    error: str | None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Tiingo survivorship coverage for weekly momentum")
    parser.add_argument("--start", type=date.fromisoformat, default=date(2013, 1, 1))
    parser.add_argument("--end", type=date.fromisoformat, default=date.today())
    parser.add_argument("--storage-root", type=Path, default=Path("data/tiingo"))
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--fetch", type=int, choices=[0, 1], default=1, help="Call Tiingo API for missing ranges.")
    parser.add_argument("--limit", type=int, default=None, help="Limit tickers for smoke tests.")
    parser.add_argument("--throttle-ms", type=int, default=75)
    parser.add_argument("--use-wiki-cache", type=int, choices=[0, 1], default=1)
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    _setup_logging(args.log_level)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    current, start_members, changes = _load_spx_sets(args.start, bool(args.use_wiki_cache))
    universe = _build_universe(args.start, args.end, current, start_members, changes)
    if args.limit is not None:
        universe = universe[: args.limit]

    storage = TiingoStorage(root=args.storage_root)
    source = TiingoSource(storage=storage)
    rows: list[AuditRow] = []

    log.info("audit universe=%d start=%s end=%s fetch=%s", len(universe), args.start, args.end, args.fetch)
    for idx, ticker in enumerate(universe, start=1):
        log.info("[%d/%d] %s", idx, len(universe), ticker)
        rows.append(_audit_one(ticker, current, start_members, changes, args, storage, source))
        if args.fetch:
            time.sleep(args.throttle_ms / 1000.0)

    audit = pd.DataFrame([asdict(row) for row in rows]).sort_values("ticker")
    universe_df = _universe_frame(universe, current, start_members, changes)
    summary = _summary(audit, args)

    audit.to_csv(args.output_dir / "tiingo_fetch_audit.csv", index=False)
    universe_df.to_csv(args.output_dir / "sp500_pit_tiingo_universe.csv", index=False)
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    _write_report(args.output_dir / "TIINGO_SURVIVORSHIP_AUDIT.md", audit, summary, args)

    print(f"universe={len(universe)}")
    print(f"available={summary['n_available']}")
    print(f"missing_or_error={summary['n_missing_or_error']}")
    print(f"removed_available={summary['n_likely_removed_or_renamed_available']}/{summary['n_likely_removed_or_renamed']}")
    print(f"outputs={args.output_dir}")
    return 0


def _setup_logging(level: str) -> None:
    logging.basicConfig(level=getattr(logging, level), format="%(asctime)s %(levelname)s %(name)s - %(message)s")


def _load_spx_sets(start: date, use_cache: bool) -> tuple[set[str], set[str], pd.DataFrame]:
    wiki = WikipediaSPX()
    current_df, changes = wiki.fetch_tables(use_cache=use_cache)
    symbol_col = next((col for col in current_df.columns if str(col).lower() in {"symbol", "ticker"}), None)
    if symbol_col is None:
        raise ValueError(f"No Symbol/Ticker column in current S&P table: {list(current_df.columns)}")
    current = {_normalize_symbol(ticker) for ticker in current_df[symbol_col].dropna().astype(str)}
    changes = changes.copy()
    changes["added"] = changes["added"].map(_clean_optional_symbol)
    changes["removed"] = changes["removed"].map(_clean_optional_symbol)
    start_members = {_normalize_symbol(ticker) for ticker in constituents_on(start, current, changes)}
    return current, start_members, changes


def _build_universe(
    start: date,
    end: date,
    current: set[str],
    start_members: set[str],
    changes: pd.DataFrame,
) -> list[str]:
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    in_window = changes[(changes["date"] >= start_ts) & (changes["date"] <= end_ts)]
    changed = set(in_window["added"].dropna().astype(str)) | set(in_window["removed"].dropna().astype(str))
    return sorted(current | start_members | {_normalize_symbol(ticker) for ticker in changed if ticker})


def _audit_one(
    ticker: str,
    current: set[str],
    start_members: set[str],
    changes: pd.DataFrame,
    args: argparse.Namespace,
    storage: TiingoStorage,
    source: TiingoSource,
) -> AuditRow:
    pre_fetch_cached = storage.has(ticker, args.start, args.end, frequency="daily")
    attempted_fetch = bool(args.fetch and not pre_fetch_cached)
    fetch_status = "cached" if pre_fetch_cached else "not_requested"
    error = None
    if attempted_fetch:
        try:
            df = source.fetch(ticker, args.start, args.end, asset_class="equity", frequency="daily")
            fetch_status = "empty" if df.empty else "fetched"
        except Exception as exc:  # noqa: BLE001 - audit should continue across API/ticker failures.
            fetch_status = "error"
            error = str(exc)[:500]

    first_dt, last_dt, n_bars = _storage_range(storage, ticker)
    selected_dates = _selected_change_dates(changes, ticker)
    likely_removed = ticker not in current and (_appeared(changes, ticker, "removed") or ticker in start_members)
    return AuditRow(
        ticker=ticker,
        in_current_sp500=ticker in current,
        in_start_sp500=ticker in start_members,
        appeared_as_added=_appeared(changes, ticker, "added"),
        appeared_as_removed=_appeared(changes, ticker, "removed"),
        selected_change_dates=selected_dates,
        likely_removed_or_renamed=likely_removed,
        pre_fetch_cached=pre_fetch_cached,
        attempted_fetch=attempted_fetch,
        fetch_status=fetch_status,
        first_dt=first_dt,
        last_dt=last_dt,
        n_bars=n_bars,
        covers_research_start=_covers_start(first_dt, args.start),
        covers_research_end=_covers_end(last_dt, args.end),
        error=error,
    )


def _storage_range(storage: TiingoStorage, ticker: str) -> tuple[str | None, str | None, int]:
    entry = storage.manifest.get(ticker, {}).get("daily")
    if entry is None:
        return None, None, 0
    return entry.get("first_dt"), entry.get("last_dt"), int(entry.get("n_bars", 0))


def _universe_frame(universe: list[str], current: set[str], start_members: set[str], changes: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ticker": ticker,
                "in_current_sp500": ticker in current,
                "in_start_sp500": ticker in start_members,
                "appeared_as_added": _appeared(changes, ticker, "added"),
                "appeared_as_removed": _appeared(changes, ticker, "removed"),
                "selected_change_dates": _selected_change_dates(changes, ticker),
            }
            for ticker in universe
        ]
    )


def _summary(audit: pd.DataFrame, args: argparse.Namespace) -> dict[str, object]:
    available = audit["n_bars"] > 0
    likely_removed = audit["likely_removed_or_renamed"]
    fetch_errors = audit["fetch_status"].eq("error")
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "start": args.start.isoformat(),
        "end": args.end.isoformat(),
        "fetch_enabled": bool(args.fetch),
        "n_universe": int(len(audit)),
        "n_available": int(available.sum()),
        "pct_available": float(available.mean()) if len(audit) else 0.0,
        "n_missing_or_error": int((~available | fetch_errors).sum()),
        "n_fetch_errors": int(fetch_errors.sum()),
        "n_likely_removed_or_renamed": int(likely_removed.sum()),
        "n_likely_removed_or_renamed_available": int((likely_removed & available).sum()),
        "pct_likely_removed_or_renamed_available": float((likely_removed & available).sum() / likely_removed.sum()) if likely_removed.sum() else 0.0,
        "n_current_available": int((audit["in_current_sp500"] & available).sum()),
        "n_start_available": int((audit["in_start_sp500"] & available).sum()),
    }


def _write_report(out_path: Path, audit: pd.DataFrame, summary: dict[str, object], args: argparse.Namespace) -> None:
    missing = audit[(audit["n_bars"] == 0) | audit["fetch_status"].eq("error")].copy()
    removed = audit[audit["likely_removed_or_renamed"]].copy()
    sample_removed = removed.sort_values(["n_bars", "ticker"], ascending=[False, True]).head(25)
    sample_missing = missing.sort_values("ticker").head(50)
    lines = [
        "# Tiingo Survivorship Coverage Audit",
        "",
        "## Scope",
        "",
        f"- Window: `{args.start}` to `{args.end}`.",
        "- Universe: current S&P 500, reconstructed start-date S&P 500, and all selected-change added/removed tickers in the window.",
        f"- Fetch enabled: `{bool(args.fetch)}`.",
        "- Purpose: determine whether Tiingo can supply removed/delisted/renamed symbols before rerunning the frozen `lb80/k5` leads `[advances_fin_ml, p.208-211]`.",
        "",
        "## Summary",
        "",
        pd.DataFrame([summary]).to_markdown(index=False),
        "",
        "## Removed/Renamed Proxy Sample",
        "",
        sample_removed[["ticker", "fetch_status", "first_dt", "last_dt", "n_bars", "selected_change_dates"]].to_markdown(index=False),
        "",
        "## Missing Or Error Sample",
        "",
        sample_missing[["ticker", "fetch_status", "error", "selected_change_dates"]].to_markdown(index=False) if not sample_missing.empty else "No missing/error rows.",
        "",
        "## Artifacts",
        "",
        "- `sp500_pit_tiingo_universe.csv`: full candidate universe and selected-change provenance.",
        "- `tiingo_fetch_audit.csv`: per-ticker cache/API status and coverage.",
        "- `summary.json`: machine-readable summary.",
        "",
        "## Interpretation Rules",
        "",
        "- High removed/renamed availability supports using Tiingo as the price layer, but it does not make Wikipedia membership exhaustive.",
        "- Missing rows are blockers only if they appear in the PIT universe during high-impact periods; the next backtest must quantify active missing names per signal date.",
        "- Ticker-class and rename cases can still require manual mapping even when Tiingo has the surviving/new ticker.",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def _appeared(changes: pd.DataFrame, ticker: str, column: str) -> bool:
    return bool(changes[column].dropna().astype(str).eq(ticker).any())


def _selected_change_dates(changes: pd.DataFrame, ticker: str) -> str:
    mask = changes["added"].eq(ticker) | changes["removed"].eq(ticker)
    dates = sorted(pd.Timestamp(value).date().isoformat() for value in changes.loc[mask, "date"])
    return ";".join(dates)


def _covers_start(first_dt: str | None, start: date) -> bool:
    if first_dt is None:
        return False
    return pd.Timestamp(first_dt).date() <= start


def _covers_end(last_dt: str | None, end: date) -> bool:
    if last_dt is None:
        return False
    return pd.Timestamp(last_dt).date() >= end


def _clean_optional_symbol(value: object) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    return _normalize_symbol(text) if text else None


def _normalize_symbol(value: object) -> str:
    return str(value).strip().upper()


if __name__ == "__main__":
    raise SystemExit(main())
