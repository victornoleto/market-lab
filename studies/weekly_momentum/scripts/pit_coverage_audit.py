#!/usr/bin/env python3
"""Audit approximate PIT S&P 500 membership coverage in the Tiingo cache.

The goal is to quantify the remaining data-layer risk after switching from
current-only S&P 500 membership to Wikipedia reconstructed membership. This does
not remove survivorship/delisting bias; it identifies how much of the
date-specific membership is actually present in the cached price universe before
the next validation round `[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import pandas as pd

from studies.weekly_momentum.data import load_variation_prices, sp500_pit_universe_provider


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit PIT S&P 500 coverage in Tiingo cache")
    parser.add_argument("--start", default=None)
    parser.add_argument("--end", default=None)
    parser.add_argument("--storage-root", default="data/tiingo")
    parser.add_argument("--sample", choices=["weekly", "monthly", "quarterly"], default="weekly")
    parser.add_argument("--output-dir", default="studies/weekly_momentum/phase3/pit_coverage_audit")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    start = date.fromisoformat(args.start) if args.start else None
    end = date.fromisoformat(args.end) if args.end else None
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    prices = load_variation_prices(
        "stocks",
        storage_root=args.storage_root,
        start=start,
        end=end,
        min_bars=1,
        only_sp500=False,
    )
    if prices.empty:
        raise SystemExit("No stock prices loaded")

    provider = sp500_pit_universe_provider()
    sample_dates = _sample_dates(prices.index, args.sample)
    rows = []
    missing_counter: Counter[str] = Counter()
    cache_symbols = {str(symbol) for symbol in prices.columns}
    for ts in sample_dates:
        members = provider(ts)
        present = members & cache_symbols
        missing = members - cache_symbols
        missing_counter.update(missing)
        rows.append({
            "date": str(pd.Timestamp(ts).date()),
            "pit_members": len(members),
            "cached_members": len(present),
            "missing_members": len(missing),
            "coverage_pct": len(present) / len(members) if members else 0.0,
            "sample_missing": ",".join(sorted(missing)[:20]),
        })

    coverage = pd.DataFrame(rows)
    missing_top = pd.DataFrame(
        [{"symbol": symbol, "missing_sample_count": count} for symbol, count in missing_counter.most_common()]
    )
    coverage.to_csv(out_dir / "coverage_by_date.csv", index=False)
    missing_top.to_csv(out_dir / "missing_symbols.csv", index=False)
    _write_report(out_dir / "PIT_COVERAGE_AUDIT.md", coverage, missing_top, args)

    print(f"dates={len(coverage)}")
    print(f"mean_coverage={coverage['coverage_pct'].mean():.6f}")
    print(f"min_coverage={coverage['coverage_pct'].min():.6f}")
    print(f"outputs={out_dir}")
    return 0


def _sample_dates(index: pd.DatetimeIndex, sample: str) -> pd.DatetimeIndex:
    idx = pd.DatetimeIndex(index).sort_values().unique()
    if sample == "weekly":
        sampled = idx[idx.weekday == 3]
    elif sample == "monthly":
        sampled = idx.to_series().groupby([idx.year, idx.month]).last()
    else:
        sampled = idx.to_series().groupby([idx.year, idx.quarter]).last()
    return pd.DatetimeIndex(sampled)


def _write_report(
    out_path: Path,
    coverage: pd.DataFrame,
    missing_top: pd.DataFrame,
    args: argparse.Namespace,
) -> None:
    worst = coverage.nsmallest(15, "coverage_pct")
    top_missing = missing_top.head(30)
    lines = [
        "# Weekly Momentum PIT Coverage Audit",
        "",
        "## Setup",
        "",
        f"- Sample frequency: `{args.sample}`.",
        "- Universe: approximate S&P 500 PIT membership reconstructed from Wikipedia selected changes.",
        "- Cache: Tiingo daily stock parquet files currently available in this workspace.",
        "- Purpose: quantify residual data-layer risk before promoting PIT validation `[advances_fin_ml, p.208-211]`.",
        "",
        "## Summary",
        "",
        f"- Dates sampled: `{len(coverage)}`.",
        f"- Mean PIT member coverage in cache: `{coverage['coverage_pct'].mean() * 100:.2f}%`.",
        f"- Median PIT member coverage in cache: `{coverage['coverage_pct'].median() * 100:.2f}%`.",
        f"- Worst PIT member coverage in cache: `{coverage['coverage_pct'].min() * 100:.2f}%`.",
        f"- Mean missing members per sampled date: `{coverage['missing_members'].mean():.1f}`.",
        "",
        "## Worst Coverage Dates",
        "",
        worst.to_markdown(index=False),
        "",
        "## Most Frequent Missing Symbols",
        "",
        top_missing.to_markdown(index=False) if not top_missing.empty else "No missing symbols.",
        "",
        "## Interpretation",
        "",
        "- High coverage means the PIT approximation is useful as an intermediate screen.",
        "- Missing symbols still imply residual survivorship, rename and delisting bias; this is not a paid survivorship-free feed.",
        "- If missing symbols cluster in older dates or removed constituents, Phase 3 results may still overstate tradability/selection quality.",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
