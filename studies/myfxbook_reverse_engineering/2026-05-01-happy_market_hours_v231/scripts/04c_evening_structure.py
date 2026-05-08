"""P2 EDA part 3 — evening session structure.

Tests:
- Trades per (date, pair) — is it 1 or many?
- Trades per (date, all pairs) — multi-pair simultaneous fires?
- Direction within a single evening: random, all-same, or pattern?
- Spacing between consecutive opens within an evening (if multiple)
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent.parent
PARQUET = HERE / "data" / "trades_1407880.parquet"


def main() -> None:
    df = pd.read_parquet(PARQUET)
    trades = df[df["is_trade"]].copy().sort_values("open_dt_utc").reset_index(drop=True)
    # Define "session date" = the date of the broker session opening at 23:00 UTC
    # If hour < 12, it's still the "previous day's session" — use date_open with hour <12 → roll back 1 day
    # Simpler: use date_open as-is (UTC date)
    trades["session_date"] = trades["open_dt_utc"].dt.date

    print("="*72); print("## Trades per (session, pair)"); print("="*72)
    g = trades.groupby(["session_date", "symbol"]).size()
    print(f"  Distinct (session, pair) groups: {len(g)}")
    print(f"  Distribution of trades per (session, pair):")
    print(g.value_counts().sort_index())

    print("\n" + "="*72); print("## Trades per (session date) — all pairs combined"); print("="*72)
    g2 = trades.groupby("session_date").size()
    print(f"  Distinct sessions: {len(g2)}")
    print(f"  P50: {g2.median()} | P95: {g2.quantile(0.95):.0f} | max: {g2.max()}")
    print(f"  Sessions with single trade: {(g2 == 1).sum()}")
    print(f"  Sessions with 2-3 trades: {((g2 >= 2) & (g2 <= 3)).sum()}")
    print(f"  Sessions with 4-6 trades: {((g2 >= 4) & (g2 <= 6)).sum()}")
    print(f"  Sessions with 7+ trades: {(g2 >= 7).sum()}")

    print("\n" + "="*72); print("## Pairs traded per session — diversification"); print("="*72)
    pairs_per = trades.groupby("session_date")["symbol"].nunique()
    print(pairs_per.value_counts().sort_index())

    print("\n" + "="*72); print("## Direction consistency within (session, pair)"); print("="*72)
    multi = trades.groupby(["session_date", "symbol"]).agg(
        n=("action", "count"),
        n_buys=("action", lambda s: (s == "Buy").sum()),
        n_sells=("action", lambda s: (s == "Sell").sum()),
    ).reset_index()
    multi_only = multi[multi["n"] >= 2]
    print(f"  (session, pair) groups with 2+ trades: {len(multi_only)}")
    if len(multi_only) > 0:
        all_same = multi_only[(multi_only["n_buys"] == multi_only["n"]) | (multi_only["n_sells"] == multi_only["n"])]
        mixed = multi_only[(multi_only["n_buys"] > 0) & (multi_only["n_sells"] > 0)]
        print(f"  All same direction within group: {len(all_same)} ({100*len(all_same)/len(multi_only):.1f}%)")
        print(f"  Mixed direction within group: {len(mixed)} ({100*len(mixed)/len(multi_only):.1f}%)")

    print("\n" + "="*72); print("## Spacing between consecutive opens (same session, same pair)"); print("="*72)
    trades_sorted = trades.sort_values(["session_date", "symbol", "open_dt_utc"]).reset_index(drop=True)
    trades_sorted["prev_open_same_pair"] = trades_sorted.groupby(["session_date", "symbol"])["open_dt_utc"].shift(1)
    trades_sorted["minutes_to_prev"] = (trades_sorted["open_dt_utc"] - trades_sorted["prev_open_same_pair"]).dt.total_seconds() / 60.0
    spacing = trades_sorted["minutes_to_prev"].dropna()
    if len(spacing) > 0:
        print(f"  Pairs with consecutive same-session entries: {len(spacing)}")
        print(f"  Spacing P25: {spacing.quantile(0.25):.1f} min | P50: {spacing.median():.1f} | P95: {spacing.quantile(0.95):.1f} | max: {spacing.max():.0f}")

    print("\n" + "="*72); print("## Direction following loss — does it FLIP after a losing trade?"); print("="*72)
    # In the same (session, pair) group, after a losing trade, does the next entry flip direction?
    trades_grp = trades.sort_values(["session_date", "symbol", "open_dt_utc"]).reset_index(drop=True)
    trades_grp["prev_action"] = trades_grp.groupby(["session_date", "symbol"])["action"].shift(1)
    trades_grp["prev_pips"] = trades_grp.groupby(["session_date", "symbol"])["pips"].shift(1)
    trades_grp["prev_was_loss"] = trades_grp["prev_pips"] < 0
    trades_grp["dir_changed"] = (trades_grp["action"] != trades_grp["prev_action"]) & trades_grp["prev_action"].notna()
    cond = trades_grp["prev_action"].notna() & trades_grp["prev_was_loss"]
    after_loss = trades_grp[cond]
    if len(after_loss) > 0:
        flip_rate = after_loss["dir_changed"].mean()
        print(f"  Trades preceded by loss in same (session, pair): {len(after_loss)}")
        print(f"  Direction flip rate after loss: {100*flip_rate:.1f}% (50% = random; >70% = anti-martingale)")

    print("\n" + "="*72); print("## Sample evenings — pairs and direction together"); print("="*72)
    # Show 5 representative evenings
    sample_dates = sorted(trades["session_date"].unique())[::500][:5]
    for d in sample_dates:
        sub = trades[trades["session_date"] == d].sort_values("open_dt_utc")
        print(f"\n  {d}:")
        for _, row in sub.iterrows():
            print(f"    {row['open_dt_utc'].strftime('%H:%M')} {row['symbol']:7s} {row['action']:4s} lots={row['lots']:5.2f} pips={row['pips']:+5.1f} dur={row['duration']}")


if __name__ == "__main__":
    main()
