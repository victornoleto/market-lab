"""Fix: the project's Tiingo parquets store 'adj_close' (underscore) not 'adjClose'.

Our download script fell back to 'close' (raw price) which ignores splits/dividends.
This script re-builds the parquets for tickers that came from Tiingo project cache,
using the correct 'adj_close' column.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO = Path("/var/www/pessoal/ai-trade")
TIINGO_DIR = REPO / "data" / "tiingo" / "daily" / "prices"
OUT_DIR = REPO / "reports" / "portfolio_aposentadoria_v2" / "data"


TICKERS_FROM_PROJECT_TIINGO = [
    "SSO", "UPRO", "QLD", "TQQQ", "SPY", "VTI", "VEA", "VWO", "TLT", "IEF", "SHV",
]


def main() -> None:
    for t in TICKERS_FROM_PROJECT_TIINGO:
        src = TIINGO_DIR / f"{t}.parquet"
        if not src.exists():
            print(f"SKIP {t}: no project Tiingo file")
            continue
        df = pd.read_parquet(src)
        if "adj_close" not in df.columns:
            print(f"SKIP {t}: no adj_close column (have: {df.columns.tolist()})")
            continue
        out = pd.DataFrame({"close": df["adj_close"].astype(float)})
        out.index = pd.to_datetime(df.index).tz_localize(None)
        out["return"] = out["close"].pct_change()
        out_path = OUT_DIR / f"{t}.parquet"
        out.to_parquet(out_path)
        # sanity: compute CAGR
        yrs = (out.index.max() - out.index.min()).days / 365.25
        cagr = (out["close"].iloc[-1] / out["close"].iloc[0]) ** (1 / yrs) - 1
        print(f"FIXED {t}: {out['close'].iloc[0]:.2f} → {out['close'].iloc[-1]:.2f} "
              f"over {yrs:.1f}y = {cagr:.2%} CAGR")


if __name__ == "__main__":
    main()
