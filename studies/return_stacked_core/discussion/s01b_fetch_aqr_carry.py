#!/usr/bin/env python3
"""s01b — OPTIONAL network step: fetch the AQR carry dataset for the RSSY proxy.

Downloads AQR's "Century of Factor Premia: Monthly" workbook and extracts the
carry columns (equity indices, fixed income, currencies, commodities, All
Macro composite) to ``data/external/aqr/carry_monthly.csv``.

The CSV is committed to the repo, so the main pipeline never needs network or
openpyxl. Re-run this script only to refresh the data (AQR updates the file
periodically). Reading the xlsx requires openpyxl, which is NOT a project
dependency — run via:

    uv run --with openpyxl python studies/return_stacked_core/discussion/s01b_fetch_aqr_carry.py

Attribution: AQR Capital Management, "Century of Factor Premia" dataset
(Ilmanen, Israel, Moskowitz, Thapar, Wang), AQR Data Library, research use
with attribution. The All Macro Carry composite is the closest long-history
academic analog to RSSY's multi-asset futures-yield sleeve `[risk_parity, ch.5]`.
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
AQR_DIR = REPO_ROOT / "data/external/aqr"
XLSX_PATH = AQR_DIR / "century_factor_premia_monthly.xlsx"
CSV_PATH = AQR_DIR / "carry_monthly.csv"
URL = (
    "https://www.aqr.com/-/media/AQR/Documents/Insights/Data-Sets/"
    "Century-of-Factor-Premia-Monthly.xlsx"
)
SHEET = "Century of Factor Premia"
HEADER_ROW = 18  # 0-indexed; descriptive text above
CARRY_COLS = [
    "Equity indices Carry",
    "Fixed income Carry",
    "Currencies Carry",
    "Commodities Carry",
    "All Macro Carry",
]


def main() -> int:
    import pandas as pd

    AQR_DIR.mkdir(parents=True, exist_ok=True)
    print(f"downloading {URL}")
    urllib.request.urlretrieve(URL, XLSX_PATH)
    print(f"saved {XLSX_PATH} ({XLSX_PATH.stat().st_size:,} bytes)")

    try:
        df = pd.read_excel(XLSX_PATH, sheet_name=SHEET, header=HEADER_ROW)
    except ImportError:
        print(
            "openpyxl missing — re-run with:\n"
            "  uv run --with openpyxl python "
            "studies/return_stacked_core/discussion/s01b_fetch_aqr_carry.py"
        )
        return 1

    out = df[["Date", *CARRY_COLS]].dropna(subset=["Date"]).copy()
    out["Date"] = pd.to_datetime(out["Date"])
    out = out.set_index("Date").sort_index().astype(float)
    out.to_csv(CSV_PATH)
    carry = out["All Macro Carry"].dropna()
    print(
        f"wrote {CSV_PATH}: {carry.index[0].date()} -> {carry.index[-1].date()}"
        f" ({len(carry)} months)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
