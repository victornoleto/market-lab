"""P2 EDA part 2 — direction signal + edge decay analysis.

Tests:
- Buy/Sell distribution per pair (is direction pair-specific?)
- DOW effect on direction
- Edge decay: yearly Sharpe + avg pips/trade evolution
- Cost-model impact: gross pips - typical Pepperstone spread per pair
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent.parent
PARQUET = HERE / "data" / "trades_1407880.parquet"

# Pepperstone Razor typical spreads (pips, RT) by pair, 2025
# Source: pepperstone.com/en/trading/spreads (current) — used as forward-looking cost model
PEPPERSTONE_SPREAD_PIPS = {
    "EURUSD": 0.13,
    "GBPUSD": 0.50,
    "USDCAD": 0.74,
    "USDCHF": 0.75,
    "EURGBP": 0.75,
    "EURCHF": 1.20,
}
# Commission per lot RT on Razor: $7 (≈ 0.7 pips on majors at 1 std lot $10/pip).
# We model commission as ~0.7 pips additional cost.
PEPPERSTONE_COMMISSION_PIPS = 0.7


def main() -> None:
    df = pd.read_parquet(PARQUET)
    trades = df[df["is_trade"]].copy().sort_values("close_dt_utc").reset_index(drop=True)
    trades["year"] = trades["close_dt_utc"].dt.year
    trades["dow"] = trades["open_dt_utc"].dt.day_name()
    trades["hour"] = trades["open_dt_utc"].dt.hour

    print("="*72)
    print("## Buy/Sell direction per pair")
    print("="*72)
    bs = trades.groupby(["symbol", "action"]).size().unstack(fill_value=0)
    bs["total"] = bs.sum(axis=1)
    bs["buy_pct"] = (100 * bs.get("Buy", 0) / bs["total"]).round(1)
    print(bs)

    print("\n" + "="*72)
    print("## Direction × Hour (entry hour vs Buy/Sell)")
    print("="*72)
    dh = trades.groupby(["hour", "action"]).size().unstack(fill_value=0)
    dh["total"] = dh.sum(axis=1)
    dh["buy_pct"] = (100 * dh.get("Buy", 0) / dh["total"]).round(1)
    print(dh)

    print("\n" + "="*72)
    print("## Direction × Day of week")
    print("="*72)
    dd = trades.groupby(["dow", "action"]).size().unstack(fill_value=0)
    dd["total"] = dd.sum(axis=1)
    dd["buy_pct"] = (100 * dd.get("Buy", 0) / dd["total"]).round(1)
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    print(dd.reindex([d for d in dow_order if d in dd.index]))

    print("\n" + "="*72)
    print("## Edge decay — yearly metrics")
    print("="*72)
    yr = trades.groupby("year").agg(
        n=("pips", "count"),
        win_pct=("pips", lambda s: (s > 0).mean() * 100),
        avg_pips=("pips", "mean"),
        std_pips=("pips", "std"),
        median_pips=("pips", "median"),
        total_pips=("pips", "sum"),
    ).round(2)
    yr["sharpe_naive"] = (yr["avg_pips"] / yr["std_pips"]).round(3)
    print(yr)

    print("\n" + "="*72)
    print("## Cost-model impact: net pips after Pepperstone spread + commission")
    print("="*72)
    print(f"Spread (pips RT) by pair: {PEPPERSTONE_SPREAD_PIPS}")
    print(f"Commission (pips RT): {PEPPERSTONE_COMMISSION_PIPS}")
    trades["pep_cost_pips"] = trades["symbol"].map(PEPPERSTONE_SPREAD_PIPS) + PEPPERSTONE_COMMISSION_PIPS
    trades["net_pips"] = trades["pips"] - trades["pep_cost_pips"]

    print("\nNet pips by year (after Pepperstone Razor cost model):")
    yr_net = trades.groupby("year").agg(
        n=("net_pips", "count"),
        gross_avg=("pips", "mean"),
        cost_avg=("pep_cost_pips", "mean"),
        net_avg=("net_pips", "mean"),
        net_total=("net_pips", "sum"),
        win_pct_net=("net_pips", lambda s: (s > 0).mean() * 100),
    ).round(2)
    yr_net["sharpe_net"] = (yr_net["net_avg"] / trades.groupby("year")["net_pips"].std()).round(3)
    print(yr_net)

    print("\nNet pips by pair (after Pepperstone Razor cost model):")
    pl_net = trades.groupby("symbol").agg(
        n=("net_pips", "count"),
        gross_avg=("pips", "mean"),
        cost=("pep_cost_pips", "first"),
        net_avg=("net_pips", "mean"),
        net_total=("net_pips", "sum"),
        win_pct_net=("net_pips", lambda s: (s > 0).mean() * 100),
    ).round(2)
    print(pl_net.sort_values("net_avg", ascending=False))


if __name__ == "__main__":
    main()
