"""Consolidate raw JSON batches into trades_1407880.parquet.

Schema is the inline-extracted records from the MyFxBook history table
(see 01 fetcher in plan / inline JS in browser_evaluate). Output keeps
both broker and user timestamps, plus typed numeric columns.

Reference: spec /home/victor/.claude/plans/dreamy-crunching-hamming.md (P1, P2).
"""
from __future__ import annotations

import glob
import json
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
RAW = HERE / "data" / "raw"
OUT = HERE / "data" / "trades_1407880.parquet"


def _parse_duration(s) -> float | None:
    if s is None or not isinstance(s, str) or not s.strip():
        return None
    total = 0
    for amount, unit in re.findall(r"(\d+)\s*([dhms])", s):
        n = int(amount)
        total += {"d": 86400, "h": 3600, "m": 60, "s": 1}[unit] * n
    return float(total) if total else None


def _to_float(s):
    if s is None or s == "" or s == "-":
        return None
    s = str(s).replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def _to_pct(s):
    if not s or s == "-":
        return None
    s = str(s).replace("%", "").replace(",", "")
    try:
        return float(s) / 100.0
    except ValueError:
        return None


def main() -> None:
    files = sorted(glob.glob(str(RAW / "batch*.json")))
    if not files:
        raise SystemExit(f"No batches in {RAW}")
    rows: list[dict] = []
    for f in files:
        d = json.loads(Path(f).read_text())
        rows.extend(d["trades"])
    df = pd.DataFrame(rows)
    print(f"Loaded {len(df)} raw rows from {len(files)} batches")

    df["opentime_ms"] = pd.to_numeric(df["opentime_ms"], errors="coerce")
    df["closetime_ms"] = pd.to_numeric(df["closetime_ms"], errors="coerce")
    df["open_dt_utc"] = pd.to_datetime(df["opentime_ms"], unit="ms", utc=True)
    df["close_dt_utc"] = pd.to_datetime(df["closetime_ms"], unit="ms", utc=True)

    for col in ["lots", "sl_price", "sl_pips", "sl_profit",
                "tp_price", "tp_pips", "tp_profit",
                "open_price", "close_price", "pips", "profit"]:
        df[col] = df[col].apply(_to_float)
    df["pct"] = df["pct"].apply(_to_pct)
    df["duration_sec"] = df["duration"].apply(_parse_duration)

    df["is_deposit"] = df["action"].fillna("").str.lower().eq("deposit")
    df["is_trade"] = df["action"].fillna("").str.lower().isin({"buy", "sell"})

    df = df.sort_values(["close_dt_utc", "open_dt_utc"]).reset_index(drop=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT, compression="snappy")
    print(f"Wrote {OUT} with {len(df)} rows")
    print(f"  trades: {df['is_trade'].sum()} | deposits: {df['is_deposit'].sum()} | other: {len(df) - df['is_trade'].sum() - df['is_deposit'].sum()}")
    print(f"  date range: {df['open_dt_utc'].min()} → {df['close_dt_utc'].max()}")
    print(f"  symbols: {sorted(df.loc[df['is_trade'], 'symbol'].unique().tolist())}")


if __name__ == "__main__":
    main()
