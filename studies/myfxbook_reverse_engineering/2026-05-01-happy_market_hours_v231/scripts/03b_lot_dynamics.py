"""Deeper analysis of lot dynamics — distinguish equity-scaling from martingale.

If lots grow monotonically with cumulative equity, that's % risk sizing
(expected). If lots spike within short windows after losses, that's
martingale (kill K1).

Reference: spec /home/victor/.claude/plans/dreamy-crunching-hamming.md (P1).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent.parent
PARQUET = HERE / "data" / "trades_1407880.parquet"


def main() -> None:
    df = pd.read_parquet(PARQUET)
    trades = df[df["is_trade"]].copy().sort_values("close_dt_utc").reset_index(drop=True)
    trades["year"] = trades["close_dt_utc"].dt.year

    # Lot stats per year
    print("Lot distribution per year:")
    yr = trades.groupby("year")["lots"].agg(["count", "min", "median", "max"]).round(2)
    print(yr)

    # Cumulative profit (equity proxy) — assumes profit column is in account currency
    trades["cum_profit"] = trades["profit"].fillna(0).cumsum()
    # Equity proxy: starts at some initial deposit (~$1000 typical), accumulates profit + deposits
    deposits = df[df["is_deposit"]][["close_dt_utc", "profit"]].copy()
    print(f"\nDeposits: {len(deposits)} entries, total = {deposits['profit'].sum() if 'profit' in deposits else 'unknown'}")

    # Same-day lot doubling test (within 24h of any prior trade, lot >= 1.7×)
    trades["prev_close"] = trades["close_dt_utc"].shift(1)
    trades["hours_since_prev"] = (trades["open_dt_utc"] - trades["prev_close"]).dt.total_seconds() / 3600.0
    # Same-day = within 24h
    sameday = trades["hours_since_prev"] <= 24
    trades["prev_lot"] = trades["lots"].shift(1)
    trades["prev_pips"] = trades["pips"].shift(1)
    trades["prev_was_loss"] = trades["prev_pips"] < 0
    trades["lot_ratio_to_prev"] = trades["lots"] / trades["prev_lot"]
    martingale_classic = (sameday & trades["prev_was_loss"] & (trades["lot_ratio_to_prev"] >= 1.7))
    print(f"\nClassic martingale (sameday + prev=loss + lot>=1.7×prev): {martingale_classic.sum()} trades")

    # Lot trajectory: rolling median over 100-trade windows, see if it grows ~smoothly
    rolling_med = trades["lots"].rolling(100, min_periods=20).median()
    rolling_max_per_100 = trades["lots"].rolling(100, min_periods=20).max()
    rolling_p99_per_100 = trades["lots"].rolling(100, min_periods=20).quantile(0.99)

    print("\nRolling 100-trade window (lots):")
    for label, q in [("first 100", 100), ("trade 1000", 1000), ("trade 2000", 2000), ("trade 3000", 3000), ("last 100", len(trades) - 1)]:
        if q < len(trades):
            print(f"  {label}: median={rolling_med.iloc[q]:.2f} | max={rolling_max_per_100.iloc[q]:.2f} | p99={rolling_p99_per_100.iloc[q]:.2f}")

    # Within-session ratio: per (yr, month), max_lot / median_lot
    trades["yyyymm"] = trades["close_dt_utc"].dt.to_period("M").astype(str)
    per_month = trades.groupby("yyyymm")["lots"].agg(["count", "median", "max"]).round(2)
    per_month["max_to_med"] = (per_month["max"] / per_month["median"]).round(2)
    print(f"\nPer-month max/median ratios (P95): {per_month['max_to_med'].quantile(0.95):.2f} (target < 3 = no within-month martingale)")
    print(f"Per-month max/median ratios (max): {per_month['max_to_med'].max():.2f}")

    # PnL distribution
    pips = trades["pips"].dropna()
    print(f"\nPip P&L distribution (n={len(pips)}):")
    print(f"  median={pips.median():.1f} | P05={pips.quantile(0.05):.1f} | P95={pips.quantile(0.95):.1f}")
    print(f"  count >= +100 pips (full TP hit): {(pips >= 100).sum()} ({100*(pips >= 100).sum()/len(pips):.1f}%)")
    print(f"  count <= -50 pips (full SL hit): {(pips <= -50).sum()} ({100*(pips <= -50).sum()/len(pips):.1f}%)")
    print(f"  count near zero (-5..+5): {((pips >= -5) & (pips <= 5)).sum()} ({100*((pips >= -5) & (pips <= 5)).sum()/len(pips):.1f}%)")

    # Win rate and expectancy
    wins = (pips > 0).sum()
    losses = (pips < 0).sum()
    flats = (pips == 0).sum()
    avg_win_pips = pips[pips > 0].mean()
    avg_loss_pips = pips[pips < 0].mean()
    print(f"\nWin/Loss: wins={wins} ({100*wins/len(pips):.1f}%), losses={losses} ({100*losses/len(pips):.1f}%), flat={flats}")
    print(f"  Avg win: {avg_win_pips:.1f} pips | Avg loss: {avg_loss_pips:.1f} pips")
    print(f"  Expectancy: {pips.mean():.2f} pips/trade")


if __name__ == "__main__":
    main()
