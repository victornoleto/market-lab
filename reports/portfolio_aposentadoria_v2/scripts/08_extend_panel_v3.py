"""Extend returns_monthly.parquet with v3 assets:
- BR fixed income ETFs (B5P211, IMAB11, LFTS11, DEBB11, FIXA11)
- BR equity ref (BOVA11) and BRL-hedged S&P (IVVB11)
- CDI_BR wealth index (2000+) for long-history BR FI proxy
- New US stacked alts (GDE, RSSX, BTGD)
- Synthetic versions for pre-inception long-history:
  - GDE_syn = 0.9*SPY + 0.9*GLD (since 2004)
  - BTGD_syn = 1.0*GLD + 1.0*BTC_USD (since 2014)
  - RSSX_syn = 1.0*SPY + 0.5*GLD + 0.5*BTC_USD (since 2014)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("/var/www/pessoal/ai-trade")
DATA_DIR = REPO / "reports" / "portfolio_aposentadoria_v2" / "data"


def load(ticker: str) -> pd.Series | None:
    p = DATA_DIR / f"{ticker}.parquet"
    if not p.exists():
        return None
    df = pd.read_parquet(p)
    if "return" not in df.columns:
        return None
    s = df["return"].dropna()
    s.name = ticker
    s.index = pd.to_datetime(s.index).tz_localize(None)
    return s


def daily_to_monthly(rets: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    if isinstance(rets, pd.Series):
        count = rets.resample("ME").count()
        monthly = (1 + rets).resample("ME").prod() - 1
        return monthly.where(count > 0)
    count = rets.resample("ME").count()
    monthly = (1 + rets).resample("ME").prod() - 1
    return monthly.where(count > 0)


def main() -> None:
    # Load existing panel
    existing = pd.read_parquet(DATA_DIR / "returns_daily.parquet")
    existing.index = pd.to_datetime(existing.index).tz_localize(None)
    print(f"Existing panel: {existing.shape}")

    # Add v3 assets (daily)
    new_assets = {}

    # Real BR ETFs + cash proxy
    for t in ["B5P211", "IMAB11", "LFTS11", "DEBB11", "FIXA11", "BOVA11", "IVVB11",
              "CDI_BR", "BTC_USD", "GDE", "RSSX", "BTGD"]:
        s = load(t)
        if s is not None:
            new_assets[t] = s
            print(f"  +{t}: {len(s)} rows")
        else:
            print(f"  MISSING: {t}")

    # Synthetic stacked ETFs (long-history proxies)
    if "SPY" in existing.columns and "GLD" in existing.columns:
        # GDE_syn = 0.9*SPY + 0.9*GLD (since GLD 2004-11)
        spy = existing["SPY"]
        gld = existing["GLD"]
        joint = pd.concat([spy.rename("spy"), gld.rename("gld")], axis=1).dropna()
        gde_syn = 0.9 * joint["spy"] + 0.9 * joint["gld"]
        gde_syn.name = "GDE_syn"
        new_assets["GDE_syn"] = gde_syn
        print(f"  +GDE_syn (synthetic): {len(gde_syn)} rows from {gde_syn.index.min().date()}")

    if "BTC_USD" in new_assets and "GLD" in existing.columns:
        btc = new_assets["BTC_USD"]
        gld = existing["GLD"]
        joint = pd.concat([btc.rename("btc"), gld.rename("gld")], axis=1).dropna()
        # BTGD_syn = 1.0 BTC + 1.0 GLD (2x exposure since 2014)
        btgd_syn = 1.0 * joint["btc"] + 1.0 * joint["gld"]
        btgd_syn.name = "BTGD_syn"
        new_assets["BTGD_syn"] = btgd_syn
        print(f"  +BTGD_syn (synthetic): {len(btgd_syn)} rows from {btgd_syn.index.min().date()}")

    if "BTC_USD" in new_assets and "GLD" in existing.columns and "SPY" in existing.columns:
        btc = new_assets["BTC_USD"]
        gld = existing["GLD"]
        spy = existing["SPY"]
        joint = pd.concat([btc.rename("btc"), gld.rename("gld"), spy.rename("spy")], axis=1).dropna()
        # RSSX_syn = 1.0 SPY + 0.5 GLD + 0.5 BTC (100/100 stock + gold-btc blend)
        rssx_syn = 1.0 * joint["spy"] + 0.5 * joint["gld"] + 0.5 * joint["btc"]
        rssx_syn.name = "RSSX_syn"
        new_assets["RSSX_syn"] = rssx_syn
        print(f"  +RSSX_syn (synthetic): {len(rssx_syn)} rows from {rssx_syn.index.min().date()}")

    # Build new panel by concatenating with existing (preserving existing columns)
    new_df = pd.DataFrame(new_assets)
    # Align indices and combine with existing
    combined = existing.join(new_df, how="outer")
    combined = combined.sort_index()

    combined.to_parquet(DATA_DIR / "returns_daily.parquet")
    print(f"\nExtended panel: {combined.shape}")

    # Monthly panel
    monthly = daily_to_monthly(combined)
    monthly.to_parquet(DATA_DIR / "returns_monthly.parquet")
    print(f"Monthly panel: {monthly.shape}")

    # Sanity CAGR per new asset
    print("\n=== CAGR sanity check (daily) ===")
    for col in new_assets:
        s = combined[col].dropna()
        if len(s) > 252:
            yrs = (s.index.max() - s.index.min()).days / 365.25
            cagr = (1 + s).prod() ** (1 / yrs) - 1
            vol = s.std() * np.sqrt(252)
            print(f"  {col:20s}: {s.index.min().date()} → {s.index.max().date()} "
                  f"({yrs:5.1f}y) CAGR={cagr:.2%} vol={vol:.2%}")


if __name__ == "__main__":
    main()
