#!/usr/bin/env python3
"""Audit local Tiingo cache coverage for the success_trading_strat study.

The audit is intentionally storage-only: it reads `data/tiingo/manifest.json`
and does not call Tiingo. It supports the final-subscription-day workflow by
separating critical tickers into covered, stale and missing buckets before any
network download is attempted.

Validation rationale: every downstream strategy must know its actual data
range before optimization; otherwise OOS/WF claims can be silently window-fit
or survivorship-biased `[advances_fin_ml, p.196-202]`, `[testing_tuning, p.143-144]`.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any


DEFAULT_STORAGE_ROOT = Path("data/tiingo")
DEFAULT_REPORT_DIR = Path("studies/success_trading_strat/reports/tiingo_final_day_audit")

CRITICAL_TICKERS: dict[str, list[tuple[str, str]]] = {
    "broad_us_etfs": [
        ("SPY", "etf"), ("IVV", "etf"), ("VOO", "etf"), ("VTI", "etf"),
        ("QQQ", "etf"), ("DIA", "etf"), ("IWM", "etf"),
    ],
    "international_etfs": [
        ("EFA", "etf"), ("EEM", "etf"), ("VEA", "etf"), ("VWO", "etf"),
    ],
    "defensive_and_macro_etfs": [
        ("TLT", "etf"), ("IEF", "etf"), ("AGG", "etf"), ("LQD", "etf"),
        ("HYG", "etf"), ("SHV", "etf"), ("GLD", "etf"), ("SLV", "etf"),
        ("USO", "etf"), ("UNG", "etf"), ("VXX", "etf"),
    ],
    "leveraged_and_tactical_etfs": [
        ("SSO", "etf"), ("QLD", "etf"), ("UPRO", "etf"), ("TQQQ", "etf"),
        ("SOXL", "etf"), ("SMH", "etf"), ("DRAM", "etf"), ("AIS", "etf"),
        ("POW", "etf"),
    ],
    "crypto_daily": [
        ("btcusd", "crypto"), ("ethusd", "crypto"), ("bnbusd", "crypto"),
        ("xrpusd", "crypto"), ("adausd", "crypto"), ("solusd", "crypto"),
        ("dogeusd", "crypto"), ("avaxusd", "crypto"), ("maticusd", "crypto"),
        ("dotusd", "crypto"),
    ],
    "forex_and_metals": [
        ("eurusd", "forex"), ("gbpusd", "forex"), ("usdjpy", "forex"),
        ("usdchf", "forex"), ("audusd", "forex"), ("usdcad", "forex"),
        ("nzdusd", "forex"), ("xauusd", "forex"), ("xagusd", "forex"),
    ],
}


@dataclass(frozen=True)
class CoverageRow:
    group: str
    ticker: str
    expected_asset_class: str
    frequency: str
    status: str
    first_dt: str | None
    last_dt: str | None
    n_bars: int | None
    fetched_at: str | None
    requested_start: str | None
    requested_end: str | None


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.fromisoformat(value).date()


def _row_status(entry: dict[str, Any] | None, min_last_dt: date) -> str:
    if entry is None:
        return "missing"
    last_dt = _parse_date(entry.get("last_dt") or entry.get("last_date"))
    if last_dt is None:
        return "invalid_manifest_entry"
    return "covered" if last_dt >= min_last_dt else "stale"


def _load_manifest(path: Path) -> dict[str, dict[str, dict[str, Any]]]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def _summarize_manifest(manifest: dict[str, dict[str, dict[str, Any]]]) -> dict[str, Any]:
    by_class: Counter[str] = Counter()
    by_frequency: Counter[str] = Counter()
    last_dates: dict[str, Counter[str]] = defaultdict(Counter)
    for freqs in manifest.values():
        for frequency, entry in freqs.items():
            asset_class = entry.get("asset_class", "unknown")
            by_class[asset_class] += 1
            by_frequency[frequency] += 1
            last_dt = (entry.get("last_dt") or entry.get("last_date") or "unknown")[:10]
            last_dates[asset_class][last_dt] += 1
    return {
        "n_tickers": len(manifest),
        "by_asset_class": dict(sorted(by_class.items())),
        "by_frequency": dict(sorted(by_frequency.items())),
        "top_last_dates_by_asset_class": {
            asset_class: counter.most_common(12)
            for asset_class, counter in sorted(last_dates.items())
        },
    }


def _critical_rows(
    manifest: dict[str, dict[str, dict[str, Any]]],
    *,
    min_last_dt: date,
) -> list[CoverageRow]:
    rows: list[CoverageRow] = []
    for group, tickers in CRITICAL_TICKERS.items():
        for ticker, asset_class in tickers:
            entry = manifest.get(ticker, {}).get("daily")
            status = _row_status(entry, min_last_dt)
            rows.append(
                CoverageRow(
                    group=group,
                    ticker=ticker,
                    expected_asset_class=asset_class,
                    frequency="daily",
                    status=status,
                    first_dt=(entry or {}).get("first_dt") or (entry or {}).get("first_date"),
                    last_dt=(entry or {}).get("last_dt") or (entry or {}).get("last_date"),
                    n_bars=(entry or {}).get("n_bars"),
                    fetched_at=(entry or {}).get("fetched_at"),
                    requested_start=(entry or {}).get("requested_start"),
                    requested_end=(entry or {}).get("requested_end"),
                )
            )
    return rows


def _write_markdown(report: dict[str, Any], path: Path) -> None:
    rows = report["critical_rows"]
    counts = Counter(row["status"] for row in rows)
    lines = [
        "# Tiingo Final-Day Coverage Audit",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Storage root: `{report['storage_root']}`",
        f"Freshness threshold: `{report['min_last_dt']}`",
        "",
        "## Manifest Summary",
        "",
        f"- Tickers in manifest: `{report['manifest_summary']['n_tickers']}`",
        f"- By asset class: `{report['manifest_summary']['by_asset_class']}`",
        f"- By frequency: `{report['manifest_summary']['by_frequency']}`",
        "",
        "## Critical Coverage",
        "",
        f"- Covered: `{counts.get('covered', 0)}`",
        f"- Stale: `{counts.get('stale', 0)}`",
        f"- Missing: `{counts.get('missing', 0)}`",
        f"- Invalid: `{counts.get('invalid_manifest_entry', 0)}`",
        "",
        "| group | ticker | status | first_dt | last_dt | bars |",
        "|---|---:|---|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {group} | `{ticker}` | {status} | {first_dt} | {last_dt} | {n_bars} |".format(
                group=row["group"],
                ticker=row["ticker"],
                status=row["status"],
                first_dt=row.get("first_dt") or "",
                last_dt=row.get("last_dt") or "",
                n_bars=row.get("n_bars") or "",
            )
        )
    lines.extend(
        [
            "",
            "## Download Priority",
            "",
            "1. Fetch missing critical ETFs/crypto/forex while Tiingo access remains active.",
            "2. Refresh stale critical daily data to the current date.",
            "3. Create a compressed backup of `data/tiingo/` after downloads complete.",
            "",
            "This audit is storage-only and makes no strategy claim. It exists to prevent",
            "window-fit or stale-data research before optimization `[advances_fin_ml, p.196-202]`.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit local Tiingo cache coverage.")
    parser.add_argument("--storage-root", type=Path, default=DEFAULT_STORAGE_ROOT)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--min-last-dt", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()

    manifest_path = args.storage_root / "manifest.json"
    manifest = _load_manifest(manifest_path)
    rows = _critical_rows(manifest, min_last_dt=args.min_last_dt)
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "storage_root": str(args.storage_root),
        "min_last_dt": args.min_last_dt.isoformat(),
        "manifest_summary": _summarize_manifest(manifest),
        "critical_rows": [row.__dict__ for row in rows],
    }

    args.report_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.report_dir / "coverage_audit.json"
    md_path = args.report_dir / "REPORT.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    _write_markdown(report, md_path)

    counts = Counter(row.status for row in rows)
    print(
        f"wrote {md_path} and {json_path}; "
        f"covered={counts.get('covered', 0)} stale={counts.get('stale', 0)} "
        f"missing={counts.get('missing', 0)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
