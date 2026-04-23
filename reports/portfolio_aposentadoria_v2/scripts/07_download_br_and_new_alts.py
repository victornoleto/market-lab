"""Download Brazilian fixed income ETFs + new US stacked gold/BTC ETFs.

For v3 of the analysis (post user feedback 2026-04-23):
- Replace US bonds (TLT/IEF/SHV) with BR fixed income (B5P211/LFTS11/DEBB11/etc)
- Expand gold/BTC sleeve with return-stacked alternatives (GDE/RSSX/BTGD/ISBG)

Sources:
- yfinance: BR ETFs via .SA suffix
- Tiingo REST: new US ETFs
- BCB API: CDI and IPCA series for long-history BR fixed income proxies
- yfinance BTC-USD: long-history BTC spot for synthetic gold/BTC ETFs
"""
from __future__ import annotations

import json
import os
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv

load_dotenv("/var/www/pessoal/ai-trade/.env")

REPO = Path("/var/www/pessoal/ai-trade")
DATA_DIR = REPO / "reports" / "portfolio_aposentadoria_v2" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
API_KEY = os.getenv("TIINGO_API_KEY")

# Brazilian ETFs (yfinance with .SA suffix)
BR_ETFS = {
    "B5P211.SA":  {"alias": "B5P211",  "desc": "IT Now IMAB-5 P2 — IPCA+ bonds ≤5y, IMA-B 5"},
    "IMAB11.SA":  {"alias": "IMAB11",  "desc": "IT Now IMA-B — full-curve IPCA+ bonds"},
    "LFTS11.SA":  {"alias": "LFTS11",  "desc": "Investo LFT Selic — Selic-linked, cash proxy"},
    "DEBB11.SA":  {"alias": "DEBB11",  "desc": "Investo Debêntures Incentivadas"},
    "FIXA11.SA":  {"alias": "FIXA11",  "desc": "Mirae all-fixed-income BR"},
    "BOVA11.SA":  {"alias": "BOVA11",  "desc": "iShares Ibovespa BR reference"},
    "IVVB11.SA":  {"alias": "IVVB11",  "desc": "iShares S&P500 BR (BRL-hedged exposure)"},
}

# New US ETFs (gold/BTC stacked alternatives)
US_NEW = {
    "GDE":   {"desc": "WisdomTree Efficient Gold Plus Equity — 90% SPX + 90% gold fut"},
    "RSSX":  {"desc": "Return Stacked US Stocks & Gold/Bitcoin — 100% SPX + 100% gold/BTC"},
    "BTGD":  {"desc": "STKd 100% Bitcoin & 100% Gold — 2× leveraged gold+BTC"},
    "ISBG":  {"desc": "IncomeSTKd 1× BTC & 1× Gold Premium — Quantify, + option premium"},
}

# BTC spot proxy (long history via yfinance)
BTC_SPOT = "BTC-USD"


def tiingo_daily(ticker: str, start: str = "2000-01-01", end: str | None = None) -> pd.DataFrame | None:
    if end is None:
        end = date.today().isoformat()
    url = f"https://api.tiingo.com/tiingo/daily/{ticker}/prices"
    for attempt in range(3):
        try:
            r = requests.get(url, params={"startDate": start, "endDate": end, "format": "json"},
                             headers={"Content-Type": "application/json",
                                      "Authorization": f"Token {API_KEY}"},
                             timeout=30)
            if r.status_code != 200:
                return None
            data = r.json()
            if not data:
                return None
            df = pd.DataFrame(data)
            df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
            df = df.set_index("date").sort_index()
            if "adjClose" not in df.columns:
                return None
            return pd.DataFrame({
                "close": df["adjClose"].astype(float),
                "return": df["adjClose"].astype(float).pct_change(),
            })
        except Exception as e:
            print(f"  retry {attempt+1}: {e}")
            time.sleep(1)
    return None


def yf_download(ticker: str, start: str = "2000-01-01") -> pd.DataFrame | None:
    for attempt in range(3):
        try:
            df = yf.download(ticker, start=start, auto_adjust=True,
                             progress=False, threads=False, timeout=30)
            if df is None or df.empty:
                return None
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0] for c in df.columns]
            px = df["Close"].astype(float)
            out = pd.DataFrame({"close": px, "return": px.pct_change()})
            out.index = pd.to_datetime(out.index).tz_localize(None)
            return out
        except Exception as e:
            print(f"  retry {attempt+1}/{ticker}: {e}")
            time.sleep(2)
    return None


def bcb_series(series_id: int, start: str = "2000-01-01", end: str | None = None) -> pd.Series | None:
    """Fetch BCB economic series via SGS API. Returns pd.Series of daily values."""
    if end is None:
        end = date.today().isoformat()
    # BCB API expects DD/MM/YYYY
    s_ddmm = pd.Timestamp(start).strftime("%d/%m/%Y")
    e_ddmm = pd.Timestamp(end).strftime("%d/%m/%Y")
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series_id}/dados"
    try:
        r = requests.get(url, params={"formato": "json", "dataInicial": s_ddmm, "dataFinal": e_ddmm},
                         timeout=60)
        if r.status_code != 200:
            return None
        data = r.json()
        if not data:
            return None
        df = pd.DataFrame(data)
        df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
        df["valor"] = df["valor"].astype(float)
        df = df.set_index("data").sort_index()
        return df["valor"]
    except Exception as e:
        print(f"  BCB {series_id} err: {e}")
        return None


def main() -> None:
    meta = {}

    # 1) Brazilian ETFs
    for yf_tick, info in BR_ETFS.items():
        alias = info["alias"]
        out_path = DATA_DIR / f"{alias}.parquet"
        df = yf_download(yf_tick)
        if df is None or df.empty or len(df) < 30:
            print(f"BR FAIL: {yf_tick}")
            meta[alias] = {"source": "FAIL"}
            continue
        df = df.dropna(subset=["close"])
        df.to_parquet(out_path)
        meta[alias] = {
            "source": "yfinance_BR", "ticker": yf_tick, "desc": info["desc"],
            "start": df.index.min().isoformat(), "end": df.index.max().isoformat(),
            "rows": int(len(df)),
        }
        print(f"BR OK: {alias} — {len(df)} rows {df.index.min().date()} → {df.index.max().date()}")
        time.sleep(0.3)

    # 2) New US gold/BTC stacked ETFs — try Tiingo, fallback yfinance
    for t, info in US_NEW.items():
        out_path = DATA_DIR / f"{t}.parquet"
        if out_path.exists():
            df_exist = pd.read_parquet(out_path)
            print(f"US SKIP exists: {t} ({len(df_exist)} rows)")
            continue
        df = tiingo_daily(t)
        src = "tiingo_api"
        if df is None or df.empty:
            df = yf_download(t)
            src = "yfinance"
        if df is None or df.empty or len(df) < 10:
            print(f"US FAIL: {t}")
            meta[t] = {"source": "FAIL"}
            continue
        df.to_parquet(out_path)
        meta[t] = {
            "source": src, "desc": info["desc"],
            "start": df.index.min().isoformat(), "end": df.index.max().isoformat(),
            "rows": int(len(df)),
        }
        print(f"US OK ({src}): {t} — {len(df)} rows {df.index.min().date()} → {df.index.max().date()}")
        time.sleep(0.2)

    # 3) Long-history BTC spot (for synthetic stacked proxies)
    df = yf_download(BTC_SPOT, start="2014-01-01")
    if df is not None and not df.empty:
        df.to_parquet(DATA_DIR / "BTC_USD.parquet")
        meta["BTC_USD"] = {
            "source": "yfinance_BTC-USD", "desc": "BTC spot from yfinance",
            "start": df.index.min().isoformat(), "end": df.index.max().isoformat(),
            "rows": int(len(df)),
        }
        print(f"BTC OK: {len(df)} rows {df.index.min().date()} → {df.index.max().date()}")

    # 4) BCB CDI (series 12) — daily Selic/CDI rate
    s = bcb_series(12, start="2000-01-01")
    if s is not None:
        # Series is daily rate in PERCENT; convert to decimal daily return
        daily_ret = (s / 100.0)
        df = pd.DataFrame({
            "close": (1 + daily_ret).cumprod() * 100.0,  # wealth index starting at 100
            "return": daily_ret,
        })
        df.index.name = "date"
        df.to_parquet(DATA_DIR / "CDI_BR.parquet")
        meta["CDI_BR"] = {
            "source": "bcb_sgs_12", "desc": "CDI daily BR (BCB series 12, wealth index)",
            "start": df.index.min().isoformat(), "end": df.index.max().isoformat(),
            "rows": int(len(df)),
        }
        print(f"BCB CDI OK: {len(df)} rows {df.index.min().date()} → {df.index.max().date()}")
        print(f"  recent daily rate: {s.iloc[-1]:.4f}%; implied annual: {((1 + s.iloc[-1]/100)**252 - 1)*100:.2f}%")

    # 5) BCB IPCA (series 433) — monthly CPI for real-rate calc
    s = bcb_series(433, start="2000-01-01")
    if s is not None:
        df = pd.DataFrame({"value_pct": s})  # monthly inflation %
        df.index.name = "date"
        df.to_parquet(DATA_DIR / "IPCA_BR.parquet")
        meta["IPCA_BR"] = {
            "source": "bcb_sgs_433", "desc": "IPCA monthly BR (BCB series 433)",
            "start": df.index.min().isoformat(), "end": df.index.max().isoformat(),
            "rows": int(len(df)),
        }
        print(f"BCB IPCA OK: {len(df)} rows {df.index.min().date()} → {df.index.max().date()}")

    # 6) BCB IMA-B index — series unknown off top of head; try a few
    for sid, name in [(12471, "IMA_B"), (11778, "IMA_B_5"), (12478, "IMA_B_5_plus")]:
        s = bcb_series(sid, start="2003-01-01")
        if s is not None and len(s) > 100:
            df = pd.DataFrame({"close": s.astype(float)})
            df["return"] = df["close"].pct_change()
            df.index.name = "date"
            df.to_parquet(DATA_DIR / f"{name}_BR.parquet")
            meta[name] = {
                "source": f"bcb_sgs_{sid}", "desc": f"{name} index BR",
                "start": df.index.min().isoformat(), "end": df.index.max().isoformat(),
                "rows": int(len(df)),
            }
            print(f"BCB {name} OK (sid {sid}): {len(df)} rows {df.index.min().date()} → {df.index.max().date()}")
        else:
            print(f"BCB {name} (sid {sid}) not found or empty")

    # Write consolidated meta
    src_file = DATA_DIR / "_sources.json"
    existing = {}
    if src_file.exists():
        existing = json.loads(src_file.read_text())
    existing.update(meta)
    src_file.write_text(json.dumps(existing, indent=2, default=str))
    print(f"\nUpdated _sources.json with {len(meta)} new entries")


if __name__ == "__main__":
    main()
