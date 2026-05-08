"""Parse MyFxBook trade-history JSON batches into a typed parquet.

Generalized from 2026-05-01-happy_market_hours_v231/scripts/02_parse_trades.py.
The parsing logic (duration → seconds, pct → fraction, dtype coercion) is
preserved byte-for-byte: smoke test reads the prototype's parquet and the
output here must match per-row.
"""
from __future__ import annotations

import glob
import json
import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

from . import config

_NUMERIC_COLS = (
    "lots",
    "sl_price",
    "sl_pips",
    "sl_profit",
    "tp_price",
    "tp_pips",
    "tp_profit",
    "open_price",
    "close_price",
    "pips",
    "profit",
)


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


def parse_trade_records(records: list[dict]) -> pd.DataFrame:
    """Pure: list-of-dicts → typed DataFrame. No I/O."""
    df = pd.DataFrame(records)
    df["opentime_ms"] = pd.to_numeric(df["opentime_ms"], errors="coerce")
    df["closetime_ms"] = pd.to_numeric(df["closetime_ms"], errors="coerce")
    df["open_dt_utc"] = pd.to_datetime(df["opentime_ms"], unit="ms", utc=True)
    df["close_dt_utc"] = pd.to_datetime(df["closetime_ms"], unit="ms", utc=True)

    for col in _NUMERIC_COLS:
        if col in df.columns:
            df[col] = df[col].apply(_to_float)
    if "pct" in df.columns:
        df["pct"] = df["pct"].apply(_to_pct)
    # 5R-1-hardening R4 (2026-05-02): duration_sec is authoritative from
    # closetime_ms − opentime_ms (always present in symbol-td attrs), not from
    # text(10) — that position breaks on non-FX layouts (crypto/CFD lack the
    # `pips` column, shifting "duration" into the `pct` slot → all-NaN).
    df["duration_sec"] = (df["closetime_ms"] - df["opentime_ms"]) / 1000.0
    # Keep textual `duration` column for backwards-compat audit, but it is no
    # longer the source of truth.
    if "duration" in df.columns:
        df["duration_sec_text"] = df["duration"].apply(_parse_duration)

    df["is_deposit"] = df["action"].fillna("").str.lower().eq("deposit")
    df["is_trade"] = df["action"].fillna("").str.lower().isin({"buy", "sell"})

    return df.sort_values(["close_dt_utc", "open_dt_utc"]).reset_index(drop=True)


def parse_history_html(html: str) -> pd.DataFrame:
    """Parse MyFxBook `paging.html?pt=4` trade-history HTML into typed rows.

    Deposit/withdrawal rows are retained with `is_trade=False`, so downstream
    reports can audit cash flows without contaminating trade-only stats.
    """
    soup = BeautifulSoup(html, "html.parser")
    rows: list[dict] = []
    for tr in soup.select("#tradingHistoryTable tbody tr.commentRow, #tradingHistoryTable tbody tr[data-record]"):
        symbol_td = tr.select_one("td.symbol")
        if not symbol_td:
            continue
        broker_times = [td.get_text(" ", strip=True) for td in tr.select("td.brokerTime")]
        user_times = [td.get_text(" ", strip=True) for td in tr.select("td.userTime")]
        visible = [td for td in tr.find_all("td", recursive=False) if "display:none" not in (td.get("style") or "").replace(" ", "").lower()]

        def text(i: int) -> str:
            return visible[i].get_text(" ", strip=True) if i < len(visible) else ""

        try:
            symbol_idx = visible.index(symbol_td)
        except ValueError:
            symbol_idx = 2

        def text_after_symbol(offset: int) -> str:
            return text(symbol_idx + offset)

        def attr_any(*names: str) -> str | None:
            for name in names:
                value = symbol_td.get(name)
                if value is not None:
                    return value
            return None

        symbol = ""
        sym_link = symbol_td.select_one(".symbolName")
        if sym_link:
            symbol = sym_link.get_text(" ", strip=True)
        else:
            symbol = symbol_td.get_text(" ", strip=True)

        rows.append({
            "record": tr.get("data-record"),
            "opentime_ms": attr_any("opentime", "openTime"),
            "closetime_ms": attr_any("closetime", "closeTime"),
            "broker_open": broker_times[0] if len(broker_times) > 0 else None,
            "broker_close": broker_times[1] if len(broker_times) > 1 else None,
            "user_open": user_times[0] if len(user_times) > 0 else None,
            "user_close": user_times[1] if len(user_times) > 1 else None,
            "symbol": symbol,
            "action": text_after_symbol(1),
            "lots": text_after_symbol(2),
            "open_price": text_after_symbol(3),
            "close_price": text_after_symbol(4),
            "pips": text_after_symbol(5),
            "profit": text_after_symbol(6),
            "duration": text_after_symbol(7),
            "pct": text_after_symbol(8),
            "sl_price": None,
            "sl_pips": None,
            "sl_profit": None,
            "tp_price": None,
            "tp_pips": None,
            "tp_profit": None,
        })
    return parse_trade_records(rows)


def parse_history_html_files_to_parquet(html_files: list[Path], output_path: Path) -> pd.DataFrame:
    """Parse multiple saved history HTML pages and persist one parquet."""
    frames = [parse_history_html(path.read_text()) for path in html_files]
    if not frames:
        raise FileNotFoundError("No history HTML files supplied")
    df = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["record"], keep="first")
    df = df.sort_values(["close_dt_utc", "open_dt_utc"]).reset_index(drop=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, compression="snappy")
    return df


def parse_batches_to_parquet(raw_dir: Path, output_path: Path) -> pd.DataFrame:
    """Concat batch*.json files in raw_dir, parse, write parquet, return DataFrame."""
    files = sorted(glob.glob(str(raw_dir / "batch*.json")))
    if not files:
        raise FileNotFoundError(f"No batch*.json under {raw_dir}")
    rows: list[dict] = []
    for f in files:
        rows.extend(json.loads(Path(f).read_text())["trades"])
    df = parse_trade_records(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, compression="snappy")
    return df


def load_trades(system_id: int | str, parquet_override: Path | None = None) -> pd.DataFrame:
    """Load the system's parsed trades parquet. Override path for legacy/prototype data."""
    path = parquet_override or config.trades_parquet_path(system_id)
    if not path.exists():
        raise FileNotFoundError(f"trades parquet not found at {path} — run parse_batches_to_parquet first")
    return pd.read_parquet(path)
