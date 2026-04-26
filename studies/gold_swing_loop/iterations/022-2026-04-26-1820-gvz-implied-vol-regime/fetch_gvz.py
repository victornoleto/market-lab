"""Fetch CBOE Gold ETF Volatility Index (GVZ) daily close from FRED.

GVZ is the gold-equivalent of VIX — an implied-volatility index computed by
CBOE from out-of-the-money GLD options using the same VIX-style methodology.
It is gold's market-implied 30-day option-pricing-derived expected vol.

Output: data/external/macro/gvzcls_daily.parquet, columns=[close], DatetimeIndex.
Idempotent: merges with existing parquet, dedupes by date.

Citations:
  [volatility_trading, p.32-37]    — Sinclair: implied vol indices reflect
                                     option-writer risk premia; low IV often
                                     precedes vol expansions (vol risk premium).
  CBOE GVZ methodology white paper — VIX-style 30-day expected vol from
                                     GLD option chain.
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO = Path(__file__).resolve().parents[4]
OUT_PATH = REPO / "data" / "external" / "macro" / "gvzcls_daily.parquet"
FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
SERIES_ID = "GVZCLS"


def fetch(start: str, end: str) -> pd.DataFrame:
    r = requests.get(
        FRED_URL,
        params={"id": SERIES_ID, "cosd": start, "coed": end},
        timeout=60,
    )
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    cols_lower = {c.lower(): c for c in df.columns}
    date_col = cols_lower.get("observation_date") or cols_lower.get("date") or df.columns[0]
    value_col = cols_lower.get(SERIES_ID.lower(), SERIES_ID)
    df["date"] = pd.to_datetime(df[date_col])
    df = df.set_index("date")
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    df = df.dropna(subset=[value_col])
    df = df[[value_col]].rename(columns={value_col: "close"}).sort_index()
    df = df[~df.index.duplicated(keep="last")]
    return df


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--start", default="2008-01-01")
    ap.add_argument("--end", default="2026-04-26")
    ap.add_argument("--output", default=str(OUT_PATH))
    args = ap.parse_args()

    df = fetch(args.start, args.end)
    print(f"[gvz] fetched n={len(df)} first={df.index.min().date()} last={df.index.max().date()}",
          file=sys.stderr)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        existing = pd.read_parquet(out)
        merged = pd.concat([existing, df])
        merged = merged[~merged.index.duplicated(keep="last")].sort_index()
        print(f"[gvz] merge existing={len(existing)} + new={len(df)} → {len(merged)}", file=sys.stderr)
        merged.to_parquet(out)
    else:
        df.to_parquet(out)
    print(f"[gvz] wrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
