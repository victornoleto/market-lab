"""Download daily adjusted prices for all candidate ETFs for Plano C v2 analysis.

Uses yfinance for the ones NOT already in data/tiingo/daily/prices/, and loads
the Tiingo parquet for the ones already cached.

Writes to reports/portfolio_aposentadoria_v2/data/<TICKER>.parquet with columns:
- date (index)
- close (adjusted close)
- return (daily simple return)

Also writes data/_sources.json mapping ticker -> source + first/last date.
"""
from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import yfinance as yf

REPO = Path("/var/www/pessoal/ai-trade")
TIINGO_DIR = REPO / "data" / "tiingo" / "daily" / "prices"
OUT_DIR = REPO / "reports" / "portfolio_aposentadoria_v2" / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TICKERS = {
    # Factor core (Avantis)
    "AVUS": {"desc": "Avantis US Equity (US core + factor tilts)"},
    "AVUV": {"desc": "Avantis US Small Cap Value"},
    "SPMO": {"desc": "Invesco S&P 500 Momentum"},
    "AVDE": {"desc": "Avantis International Equity (DM ex-US)"},
    "IDMO": {"desc": "Invesco S&P Int'l Dev Momentum"},
    "AVDV": {"desc": "Avantis Int'l Small Cap Value"},
    "AVEM": {"desc": "Avantis Emerging Markets"},
    "DFAC": {"desc": "Dimensional US Core Equity 2 (AVUS cousin)"},
    "DFAT": {"desc": "Dimensional US Targeted Value (AVUV cousin)"},
    "AVGV": {"desc": "Avantis All Equity Markets Value"},
    # Leveraged core
    "SSO": {"desc": "ProShares 2x S&P 500"},
    "UPRO": {"desc": "ProShares 3x S&P 500"},
    "QLD": {"desc": "ProShares 2x QQQ"},
    "TQQQ": {"desc": "ProShares 3x QQQ"},
    "EFO": {"desc": "ProShares 2x MSCI EAFE"},
    # Return stacking / efficient core
    "NTSX": {"desc": "WisdomTree 90/60 US Efficient Core (90% SPX + 60% Treasury fut)"},
    "NTSI": {"desc": "WisdomTree 90/60 Int'l Efficient Core"},
    "NTSE": {"desc": "WisdomTree 90/60 EM Efficient Core"},
    "RSST": {"desc": "Return Stacked 100% US Stocks / 100% Managed Futures"},
    "RSSB": {"desc": "Return Stacked 100% Global Stocks / 100% US Bonds"},
    "RSBT": {"desc": "Return Stacked 100% Bonds / 100% Managed Futures"},
    "RSSY": {"desc": "Return Stacked 100% US Stocks / 100% Futures Yield (carry)"},
    "RSBY": {"desc": "Return Stacked 100% Bonds / 100% Futures Yield"},
    # Managed futures
    "DBMF": {"desc": "iMGP DBi Managed Futures"},
    "KMLM": {"desc": "KFA Mount Lucas Managed Futures"},
    "CTA": {"desc": "Simplify Managed Futures Strategy"},
    # Alts
    "IBIT": {"desc": "iShares Bitcoin Trust"},
    "GLDM": {"desc": "SPDR Gold MiniShares"},
    # Broad market proxies (baselines)
    "SPY": {"desc": "SPDR S&P 500"},
    "VTI": {"desc": "Vanguard Total US Market"},
    "VXUS": {"desc": "Vanguard Total Int'l Stock"},
    "VEA": {"desc": "Vanguard FTSE DM ex-US"},
    "VWO": {"desc": "Vanguard FTSE EM"},
    "VT": {"desc": "Vanguard Total World"},
    # Bonds / rates
    "TLT": {"desc": "iShares 20+ Year Treasury"},
    "IEF": {"desc": "iShares 7-10 Year Treasury"},
    "SHV": {"desc": "iShares Short Treasury (cash proxy)"},
    # Long-run S&P 500 TR proxy
    "^SP500TR": {"desc": "S&P 500 Total Return index (yfinance)"},
    "^GSPC": {"desc": "S&P 500 price index"},
}


def load_tiingo(ticker: str) -> pd.DataFrame | None:
    p = TIINGO_DIR / f"{ticker}.parquet"
    if not p.exists():
        return None
    df = pd.read_parquet(p)
    # normalize columns
    if "adjClose" in df.columns:
        px = df["adjClose"]
    elif "close" in df.columns:
        px = df["close"]
    else:
        return None
    if df.index.dtype == "O":
        df.index = pd.to_datetime(df.index)
    out = pd.DataFrame({"close": px.astype(float)})
    out.index = pd.to_datetime(out.index).tz_localize(None)
    out["return"] = out["close"].pct_change()
    return out


def download_yf(ticker: str, start: str = "1990-01-01") -> pd.DataFrame | None:
    for attempt in range(3):
        try:
            df = yf.download(
                ticker,
                start=start,
                auto_adjust=True,
                progress=False,
                threads=False,
                timeout=30,
            )
            if df is None or df.empty:
                return None
            # yf returns multi-level columns sometimes
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0] for c in df.columns]
            px = df["Close"].astype(float)
            out = pd.DataFrame({"close": px})
            out.index = pd.to_datetime(out.index).tz_localize(None)
            out["return"] = out["close"].pct_change()
            return out
        except Exception as e:
            print(f"  retry {attempt+1}/3 for {ticker}: {e}")
            time.sleep(2 * (attempt + 1))
    return None


def main() -> None:
    sources = {}
    for ticker, meta in TICKERS.items():
        out_path = OUT_DIR / f"{ticker.replace('^','_IDX_')}.parquet"
        if out_path.exists():
            df = pd.read_parquet(out_path)
            print(f"SKIP (exists): {ticker} — {len(df)} rows {df.index.min().date()} → {df.index.max().date()}")
            sources[ticker] = {
                "source": "cached",
                "start": df.index.min().isoformat(),
                "end": df.index.max().isoformat(),
                "rows": int(len(df)),
                "desc": meta["desc"],
            }
            continue

        # Try Tiingo first (no-op for non-plain tickers)
        df = None
        src = None
        if not ticker.startswith("^"):
            df = load_tiingo(ticker)
            if df is not None:
                src = "tiingo"

        # Fallback yfinance
        if df is None:
            df = download_yf(ticker)
            if df is not None:
                src = "yfinance"

        if df is None or df.empty:
            print(f"FAIL: {ticker} — no data available")
            sources[ticker] = {"source": "FAIL", "desc": meta["desc"]}
            continue

        df = df.dropna(subset=["close"])
        if len(df) < 30:
            print(f"FAIL: {ticker} — only {len(df)} rows")
            sources[ticker] = {"source": "FAIL", "rows": int(len(df)), "desc": meta["desc"]}
            continue

        df.to_parquet(out_path)
        sources[ticker] = {
            "source": src,
            "start": df.index.min().isoformat(),
            "end": df.index.max().isoformat(),
            "rows": int(len(df)),
            "desc": meta["desc"],
        }
        print(f"OK ({src}): {ticker} — {len(df)} rows {df.index.min().date()} → {df.index.max().date()}")
        if src == "yfinance":
            time.sleep(0.3)  # politeness

    with (OUT_DIR / "_sources.json").open("w") as f:
        json.dump(sources, f, indent=2, default=str)

    # Summary
    ok = sum(1 for v in sources.values() if v.get("source") not in ("FAIL", None))
    fail = sum(1 for v in sources.values() if v.get("source") == "FAIL")
    print(f"\nSummary: {ok} OK / {fail} FAIL of {len(TICKERS)} tickers")


if __name__ == "__main__":
    main()
