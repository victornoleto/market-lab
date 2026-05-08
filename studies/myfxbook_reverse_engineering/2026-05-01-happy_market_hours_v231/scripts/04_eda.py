"""P2 EDA — reverse-engineer entry/exit rules of Happy Market Hours v2.3.1.

Per spec /home/victor/.claude/plans/dreamy-crunching-hamming.md (Phase P2):
- Entry time-of-day distribution (UTC + broker time + DOW)
- Exit mechanism (TP/SL almost never fire — what closes positions?)
- Per-pair behavior consistency
- Entry price vs prior bar (breakout vs mean-reversion vs time-only)

Output: stdout sections + 04_eda_summary.md is written by 04b script.

Citations: [evidence_based_ta, Aronson, p.367-380] hour-of-day FX effects.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent.parent
PARQUET = HERE / "data" / "trades_1407880.parquet"


def section(title: str) -> None:
    print(f"\n{'='*72}\n## {title}\n{'='*72}")


def main() -> None:
    df = pd.read_parquet(PARQUET)
    trades = df[df["is_trade"]].copy().sort_values("close_dt_utc").reset_index(drop=True)
    trades["open_hour_utc"] = trades["open_dt_utc"].dt.hour
    trades["open_min_utc"] = trades["open_dt_utc"].dt.minute
    trades["close_hour_utc"] = trades["close_dt_utc"].dt.hour
    trades["dow"] = trades["open_dt_utc"].dt.dayofweek  # 0=Mon
    trades["dow_name"] = trades["open_dt_utc"].dt.day_name()
    trades["duration_h"] = trades["duration_sec"] / 3600.0

    section("Entry hour distribution (UTC)")
    hr = trades.groupby("open_hour_utc").size().reindex(range(24), fill_value=0)
    for h, n in hr.items():
        bar = "█" * int(50 * n / max(1, hr.max()))
        print(f"  {h:02d}:00 UTC  ({n:4d})  {bar}")

    section("Entry hour:minute distribution (top 20)")
    hm = trades.groupby([trades["open_hour_utc"], trades["open_min_utc"] // 5 * 5]).size().sort_values(ascending=False).head(20)
    for (h, m), n in hm.items():
        print(f"  {h:02d}:{m:02d} UTC  →  {n:4d} trades")

    section("Day of week distribution")
    dow = trades.groupby("dow_name").size().reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], fill_value=0)
    for d, n in dow.items():
        bar = "█" * int(50 * n / max(1, dow.max()))
        print(f"  {d:10s} ({n:4d})  {bar}")

    section("Per-pair entry hour distribution")
    for sym in sorted(trades["symbol"].unique()):
        sub = trades[trades["symbol"] == sym]
        hr_s = sub.groupby("open_hour_utc").size()
        peak_hr = int(hr_s.idxmax())
        peak_n = int(hr_s.max())
        total = len(sub)
        # Concentration: % in top hour
        pct_peak = 100 * peak_n / total
        print(f"  {sym:7s} (n={total:4d})  peak={peak_hr:02d}:00 UTC ({peak_n} trades, {pct_peak:.0f}%)  hours active={hr_s.gt(0).sum()}")

    section("Exit mechanism — what closes positions?")
    # Define classification:
    #  - SL_hit: pips <= sl_pips + 5 (within 5 of SL)
    #  - TP_hit: pips >= tp_pips - 5
    #  - Time/manual: in between
    trades["sl_dist"] = trades["pips"] - trades["sl_pips"]  # negative if past SL
    trades["tp_dist"] = trades["tp_pips"] - trades["pips"]  # negative if past TP
    trades["close_kind"] = "manual_or_time"
    trades.loc[trades["pips"] <= trades["sl_pips"] + 2, "close_kind"] = "near_SL"
    trades.loc[trades["pips"] >= trades["tp_pips"] - 2, "close_kind"] = "near_TP"
    kind = trades["close_kind"].value_counts()
    for k, v in kind.items():
        print(f"  {k:20s}  {v:4d}  ({100*v/len(trades):.1f}%)")

    section("Exit hour distribution — when do positions close?")
    ch = trades.groupby("close_hour_utc").size().reindex(range(24), fill_value=0)
    for h, n in ch.items():
        bar = "█" * int(50 * n / max(1, ch.max()))
        print(f"  {h:02d}:00 UTC  ({n:4d})  {bar}")

    section("Hold time histogram (minutes, capped 240)")
    dur_min = (trades["duration_sec"] / 60.0).clip(upper=240)
    bins = list(range(0, 245, 15))
    cuts = pd.cut(dur_min, bins=bins, include_lowest=True, right=False)
    hist = cuts.value_counts().sort_index()
    for b, n in hist.items():
        bar = "█" * int(40 * n / max(1, hist.max()))
        print(f"  {str(b):20s}  ({n:4d})  {bar}")

    section("SL/TP setting evolution (per-year)")
    trades["year"] = trades["close_dt_utc"].dt.year
    sl_tp = trades.groupby("year").agg(
        n=("pips", "count"),
        sl_pips_med=("sl_pips", "median"),
        tp_pips_med=("tp_pips", "median"),
        sl_pips_p95=("sl_pips", lambda s: s.quantile(0.95)),
        tp_pips_p95=("tp_pips", lambda s: s.quantile(0.95)),
    ).round(1)
    print(sl_tp)

    section("PnL by pair")
    pl = trades.groupby("symbol").agg(
        n=("pips", "count"),
        win_pct=("pips", lambda s: 100*(s > 0).mean()),
        avg_pips=("pips", "mean"),
        median_pips=("pips", "median"),
        total_pips=("pips", "sum"),
        total_profit_usd=("profit", "sum"),
    ).round(2).sort_values("total_pips", ascending=False)
    print(pl)

    section("PnL by year")
    pl_y = trades.groupby("year").agg(
        n=("pips", "count"),
        win_pct=("pips", lambda s: 100*(s > 0).mean()),
        avg_pips=("pips", "mean"),
        total_pips=("pips", "sum"),
        total_profit_usd=("profit", "sum"),
    ).round(2)
    print(pl_y)

    section("Entry vs prior 60-min price (breakout vs MR signal)")
    # Without OHLC data we can't yet test indicator-based; but we can check:
    # are entries near rounded levels (e.g., XX.50, XX.00)?  This would indicate
    # pivots/round-numbers.
    # Round number test: distance of open_price to nearest 0.005 unit
    trades["round_dist_pips"] = (trades["open_price"] * 10000) % 50  # for 4-decimal pairs
    rdist = trades["round_dist_pips"]
    print(f"  Round-number proximity (open price modulo 50 pips):")
    print(f"    P25: {rdist.quantile(0.25):.1f} | P50: {rdist.median():.1f} | P75: {rdist.quantile(0.75):.1f}")
    print(f"    Within 5 pips of 50-pip level: {(rdist <= 5).sum() + (rdist >= 45).sum()} ({100*((rdist <= 5).sum() + (rdist >= 45).sum())/len(trades):.1f}%)")
    # If uniform: ~20% would be within 5 pips of 50-pip level (10/50). Significant excess = round-number effect.

    section("Same-bar grouping — multiple entries in same minute?")
    # Group by (symbol, open_dt_utc rounded to minute) — count of simultaneous opens
    trades["open_min_floor"] = trades["open_dt_utc"].dt.floor("min")
    grp = trades.groupby(["symbol", "open_min_floor"]).size()
    multi = grp[grp > 1]
    print(f"  Distinct entry minutes: {grp.shape[0]}")
    print(f"  Minutes with multiple entries (same symbol): {len(multi)}")
    print(f"  Distribution of simultaneous entries: {multi.value_counts().head().to_dict()}")


if __name__ == "__main__":
    main()
