from __future__ import annotations

import json
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from market_lab.backtest.data.testfolio_loader import load_testfolio_frame  # noqa: E402


US_CORE = ROOT / "studies/return_stacked_core/us_core"
REMOTE_PRICES = US_CORE / "series/remote_prices.parquet"
OUT_PARQUET = US_CORE / "series/return_stacked_core_sleeve_returns.parquet"
OUT_META = US_CORE / "series/return_stacked_core_sleeve_returns.meta.json"

TRADING_DAYS = 252
RSST_FINANCING_SPREAD_ANNUAL = 0.0200
RSST_DBMF_WEIGHT = 0.70
RSST_KMLM_WEIGHT = 0.30


def build_sleeve_returns() -> pd.DataFrame:
    """Build the canonical RSC sleeve-return matrix used for exact reruns.

    `GDESIM`, `DBMFSIM` and `KMLMSIM` come from saved Testfol.io remote prices
    preserved in the RSC study. `RSSTSIM` is reconstructed from the user-provided
    Testfol.io tracking payload: 100% SPY + 70% DBMF + 30% KMLM - 100%
    `CASHX?E=-2`. Locally, `CASHX?E=-2` is represented as `CASHX + 2%/year`, so a
    -100% allocation subtracts cash financing plus a 200 bps spread. This is a
    tracking proxy for RSST, not a live ETF backfill `[risk_parity, p.80-81]`,
    `[systematic_trading, p.185-188]`.
    """

    remote = pd.read_parquet(REMOTE_PRICES).sort_index()
    cache = load_testfolio_frame().sort_index()
    required_remote = ["GDESIM", "KMLMSIM", "DBMFSIM"]
    required_cache = ["SPYSIM", "ZROZSIM", "CASHX", "GLDSIM"]
    missing_remote = [column for column in required_remote if column not in remote.columns]
    missing_cache = [column for column in required_cache if column not in cache.columns]
    if missing_remote or missing_cache:
        raise KeyError(f"missing remote={missing_remote}, cache={missing_cache}")

    returns = pd.DataFrame(
        {
            "GDESIM": remote["GDESIM"].pct_change(),
            "KMLMSIM": remote["KMLMSIM"].pct_change(),
            "SPYSIM": cache["SPYSIM"].pct_change(),
            "ZROZSIM": cache["ZROZSIM"].pct_change(),
            "CASHX": cache["CASHX"].pct_change(),
            "GLDSIM": cache["GLDSIM"].pct_change(),
        }
    )
    returns["DBMFSIM"] = remote["DBMFSIM"].pct_change()

    cashx_e_minus_2 = returns["CASHX"] + RSST_FINANCING_SPREAD_ANNUAL / TRADING_DAYS
    returns["RSSTSIM"] = (
        returns["SPYSIM"]
        + RSST_DBMF_WEIGHT * returns["DBMFSIM"]
        + RSST_KMLM_WEIGHT * returns["KMLMSIM"]
        - cashx_e_minus_2
    )
    columns = ["GDESIM", "RSSTSIM", "ZROZSIM", "SPYSIM", "KMLMSIM", "DBMFSIM", "GLDSIM", "CASHX"]
    available = [column for column in columns if column in returns.columns]
    return returns[available].dropna(subset=["GDESIM", "RSSTSIM", "ZROZSIM"])


def write_outputs(frame: pd.DataFrame) -> None:
    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(OUT_PARQUET, compression="snappy")
    non_null = {
        column: {
            "first": str(frame[column].dropna().index[0].date()),
            "last": str(frame[column].dropna().index[-1].date()),
            "n": int(frame[column].notna().sum()),
        }
        for column in frame.columns
        if frame[column].notna().any()
    }
    meta = {
        "generated_by": "studies.return_stacked_core.export_sleeve_returns",
        "source_remote_prices": str(REMOTE_PRICES.relative_to(ROOT)),
        "source_testfolio_cache": "data/testfolio/cache/history.parquet",
        "output_parquet": str(OUT_PARQUET.relative_to(ROOT)),
        "rows": int(len(frame)),
        "columns": list(frame.columns),
        "first_date": str(frame.index[0].date()),
        "last_date": str(frame.index[-1].date()),
        "non_null": non_null,
        "rsst_formula": "RSSTSIM = SPYSIM + 0.70*DBMFSIM + 0.30*KMLMSIM - (CASHX + 0.0200/252)",
        "rsst_tracking_payload": "Testfol.io no-auth audit: RSST vs 100% SPY + 70% DBMF + 30% KMLM - 100% CASHX?E=-2; 2023-09-06..2026-06-08 terminal ratio 1.002547, daily return corr 0.927530.",
        "citations": ["[risk_parity, p.80-81]", "[systematic_trading, p.185-188]"],
        "caveat": "Sleeve-return matrix for RSC reruns in this repository; RSSTSIM is a documented RSST tracking proxy, not a live RSST ETF backfill. DBMFSIM availability starts the core common window in 2000.",
    }
    OUT_META.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def main() -> int:
    frame = build_sleeve_returns()
    write_outputs(frame)
    print(
        f"wrote {OUT_PARQUET.relative_to(ROOT)} rows={len(frame)} "
        f"window={frame.index[0].date()}..{frame.index[-1].date()} cols={len(frame.columns)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
