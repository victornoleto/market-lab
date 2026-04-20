"""Benchmark fetchers + equity curve normalizer.

Series:
- spy_usd            → Tiingo cache reuse (data/tiingo/SPY.csv)
- ivvb11_brl         → yfinance (IVVB11.SA)
- ibov_brl           → yfinance (^BVSP)
- ipca_pct_monthly   → BCB SGS 433
- selic_daily_pct    → BCB SGS 11
- selic_meta_annual  → BCB SGS 1178
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

import pandas as pd
import requests

from ops.core import fx, storage
from ops.core.models import BenchmarkPoint

BCB_SERIES_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"
BCB_TIMEOUT = 10.0


def _fetch_bcb_series(code: int, series_id: str, source: str) -> list[BenchmarkPoint]:
    resp = requests.get(BCB_SERIES_URL.format(code=code), timeout=BCB_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, list):
        return []
    out: list[BenchmarkPoint] = []
    now = datetime.now(timezone.utc)
    for item in data:
        d_str = item["data"]  # DD/MM/YYYY
        d = date(int(d_str[6:10]), int(d_str[3:5]), int(d_str[0:2]))
        out.append(BenchmarkPoint(
            date=d, series_id=series_id, value=Decimal(str(item["valor"])),
            source=source, fetched_at=now,
        ))
    return out


def _known_dates(series_id: str) -> set[date]:
    return {p.date for p in storage.read_benchmark_points() if p.series_id == series_id}


def _incremental_append(series_id: str, new_points: list[BenchmarkPoint]) -> None:
    known = _known_dates(series_id)
    to_add = [p for p in new_points if p.date not in known]
    if to_add:
        storage.append_benchmark_points(to_add)


def fetch_ipca() -> None:
    points = _fetch_bcb_series(433, "ipca_pct_monthly", "bcb_sgs_433")
    _incremental_append("ipca_pct_monthly", points)


def fetch_selic_daily() -> None:
    points = _fetch_bcb_series(11, "selic_daily_pct", "bcb_sgs_11")
    _incremental_append("selic_daily_pct", points)


def fetch_selic_meta() -> None:
    points = _fetch_bcb_series(1178, "selic_meta_annual", "bcb_sgs_1178")
    _incremental_append("selic_meta_annual", points)


def fetch_ibov() -> None:
    """IBOV via yfinance. No-op on network error (fail-soft for benchmarks)."""
    try:
        import yfinance as yf
    except ImportError:
        return
    try:
        df = yf.Ticker("^BVSP").history(period="max")
    except Exception:
        return
    now = datetime.now(timezone.utc)
    points = [
        BenchmarkPoint(
            date=idx.date(), series_id="ibov_brl",
            value=Decimal(str(row["Close"])),
            source="yfinance", fetched_at=now,
        )
        for idx, row in df.iterrows()
        if not pd.isna(row["Close"])
    ]
    _incremental_append("ibov_brl", points)


def fetch_ivvb11() -> None:
    """IVVB11.SA via yfinance. No-op on network error."""
    try:
        import yfinance as yf
    except ImportError:
        return
    try:
        df = yf.Ticker("IVVB11.SA").history(period="max")
    except Exception:
        return
    now = datetime.now(timezone.utc)
    points = [
        BenchmarkPoint(
            date=idx.date(), series_id="ivvb11_brl",
            value=Decimal(str(row["Close"])),
            source="yfinance", fetched_at=now,
        )
        for idx, row in df.iterrows()
        if not pd.isna(row["Close"])
    ]
    _incremental_append("ivvb11_brl", points)


def fetch_spy_usd_from_tiingo_cache() -> None:
    """Import data/tiingo/SPY.csv if present."""
    from pathlib import Path
    repo_root = Path(__file__).resolve().parents[2]
    tiingo_spy = repo_root / "data" / "tiingo" / "SPY.csv"
    if not tiingo_spy.exists():
        return
    df = pd.read_csv(tiingo_spy, parse_dates=["date"])
    now = datetime.now(timezone.utc)
    value_col = "adjClose" if "adjClose" in df.columns else "close"
    points = [
        BenchmarkPoint(
            date=row["date"].date(), series_id="spy_usd",
            value=Decimal(str(row[value_col])),
            source="tiingo", fetched_at=now,
        )
        for _, row in df.iterrows()
    ]
    _incremental_append("spy_usd", points)


def fetch_all() -> None:
    """Refresh all benchmark series; failures per-series logged but don't halt."""
    for fn in (fetch_ipca, fetch_selic_daily, fetch_selic_meta,
               fetch_ibov, fetch_ivvb11, fetch_spy_usd_from_tiingo_cache):
        try:
            fn()
        except Exception as exc:
            print(f"[WARN] {fn.__name__} failed: {exc}")


def equity_curve_brl(
    series_id: str,
    inception_date: date,
    end_date: date,
    base_value_brl: Decimal,
) -> pd.DataFrame:
    """Normalized equity curve reindexed to base_value_brl at inception_date.

    Convention: each bar's return accrues on its own date.
    """
    points = sorted(
        [p for p in storage.read_benchmark_points() if p.series_id == series_id],
        key=lambda p: p.date,
    )
    points = [p for p in points if inception_date <= p.date <= end_date]
    if not points:
        return pd.DataFrame(columns=["date", "value"])

    rows = [{"date": p.date, "raw": float(p.value)} for p in points]
    df = pd.DataFrame(rows)

    if series_id in ("selic_daily_pct",):
        df["factor"] = 1 + df["raw"] / 100.0
        df["cumul"] = df["factor"].cumprod()
        df["value"] = df["cumul"] * float(base_value_brl)
    elif series_id == "ipca_pct_monthly":
        df["factor"] = 1 + df["raw"] / 100.0
        df["cumul"] = df["factor"].cumprod()
        df["value"] = df["cumul"] * float(base_value_brl)
    elif series_id in ("spy_usd",):
        # Convert USD price via PTAX then normalize from first available point
        df["ptax"] = [float(fx.get_ptax(d)) for d in df["date"]]
        df["brl"] = df["raw"] * df["ptax"]
        df["value"] = df["brl"] / df["brl"].iloc[0] * float(base_value_brl)
    else:
        # ibov_brl, ivvb11_brl, etc: raw close price in BRL, rebase
        df["value"] = df["raw"] / df["raw"].iloc[0] * float(base_value_brl)

    return df[["date", "value"]].copy()
