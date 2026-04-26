"""Iter 001 special-task: measure exact buy-hold benchmarks on the 3 datasets.

Output is hand-pasted into ``studies/gold_swing_loop/scoring.py BENCHMARKS``.
This script is preserved for traceability / future re-measurement when
data is refreshed.

Run:
    .venv/bin/python studies/gold_swing_loop/iterations/001-*/run_benchmarks.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "studies" / "gold_swing_loop"))

from datasets import load_dataset  # noqa: E402


def measure_buyhold(df: pd.DataFrame, label: str, bars_per_year: int) -> dict:
    px = df["close"].astype(float).copy()
    rets = px.pct_change().dropna()
    sharpe = float(rets.mean() / rets.std() * np.sqrt(bars_per_year))
    span_years = (px.index[-1] - px.index[0]).days / 365.25
    cagr = float((px.iloc[-1] / px.iloc[0]) ** (1.0 / span_years) - 1.0)
    cummax = px.cummax()
    dd = (px - cummax) / cummax
    mdd = float(-dd.min())
    print(f"\n=== {label} ===")
    print(f"  span: {px.index[0].date()} → {px.index[-1].date()} ({span_years:.2f} y)")
    print(f"  bars: {len(px)} (annualization {bars_per_year}/yr)")
    print(f"  Sharpe (annualized): {sharpe:.4f}")
    print(f"  CAGR:                {cagr:.4%}")
    print(f"  MDD (positive mag):  {mdd:.4%}")
    return {"sharpe": sharpe, "cagr": cagr, "mdd": mdd, "bars_per_year": bars_per_year}


def main() -> None:
    df_intra = load_dataset("xauusd_intraday")
    span_yr = (df_intra.index[-1] - df_intra.index[0]).days / 365.25
    bars_yr_intra = int(round(len(df_intra) / span_yr))
    print(f"Empirical 1h bars/year: {bars_yr_intra}")

    measure_buyhold(load_dataset("gld_long"),
                    "gld_long  (GLD ETF daily, 21.4y)", 252)
    measure_buyhold(load_dataset("xauusd_real"),
                    "xauusd_real  (XAUUSD spot daily, 6.3y)", 252)
    measure_buyhold(df_intra,
                    f"xauusd_intraday  (XAUUSD spot 1h, 6.3y, {bars_yr_intra}/yr)",
                    bars_yr_intra)


if __name__ == "__main__":
    main()
