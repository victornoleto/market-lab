"""Tenta recuperar o direction signal usando SÓ features que já estão
no trade history — sem precisar de 1m OHLC externo.

Hipóteses testadas (cada uma é um classificador candidato Buy/Sell):
H1. Sign-of-prior-open-delta (momentum entry-to-entry, daily freq)
    — Buy se open_price[t, pair] > open_price[t-1, pair]
H2. Inverso de H1 (mean-reversion entry-to-entry)
H3. Sign-of-prior-trade-pnl-same-pair (anti-martingale per pair)
    — Buy se prev trade do mesmo par foi Sell perdedor (etc.)
H4. Day-of-week × pair fixed mapping
H5. Hour-of-day × pair fixed mapping
H6. open_price relative position vs N-trade trailing average (mini-EMA proxy)

Critério de match: % das decisões históricas explicadas pela regra.
Threshold: ≥ 80% explica = signal recuperado sem OHLC.
< 60% = signal precisa de OHLC externo.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent.parent
PARQUET = HERE / "data" / "trades_1407880.parquet"


def main() -> None:
    df = pd.read_parquet(PARQUET)
    trades = df[df["is_trade"]].copy().sort_values("open_dt_utc").reset_index(drop=True)
    trades["dir_int"] = (trades["action"] == "Buy").astype(int)  # 1=Buy, 0=Sell
    trades["hour"] = trades["open_dt_utc"].dt.hour
    trades["dow"] = trades["open_dt_utc"].dt.dayofweek

    print("=" * 72)
    print("BASELINE — chance level (always-Buy + always-Sell)")
    print("=" * 72)
    base_buy_rate = trades["dir_int"].mean()
    print(f"Always-Buy accuracy:  {base_buy_rate:.4f}")
    print(f"Always-Sell accuracy: {1 - base_buy_rate:.4f}")
    print(f"Majority class:       {max(base_buy_rate, 1 - base_buy_rate):.4f}")
    # Any rule must beat this materially to be informative.

    print("\n" + "=" * 72)
    print("H1/H2 — direction follows sign(open_price[t] - prev_open_price[t-1, same pair])")
    print("=" * 72)
    trades["prev_open"] = trades.groupby("symbol")["open_price"].shift(1)
    trades["delta_open"] = trades["open_price"] - trades["prev_open"]
    h1_pred = (trades["delta_open"] > 0).astype(int)  # momentum: price up → Buy
    h2_pred = 1 - h1_pred                              # MR: price up → Sell
    valid = trades["prev_open"].notna() & (trades["delta_open"] != 0)
    if valid.sum() > 0:
        acc_h1 = (h1_pred[valid] == trades["dir_int"][valid]).mean()
        acc_h2 = (h2_pred[valid] == trades["dir_int"][valid]).mean()
        print(f"  H1 (momentum continuation):  {acc_h1:.4f}  on {valid.sum()} trades")
        print(f"  H2 (mean-reversion):         {acc_h2:.4f}  on {valid.sum()} trades")

    print("\n" + "=" * 72)
    print("H3 — anti-martingale on prev trade pnl (same pair)")
    print("=" * 72)
    trades["prev_action"] = trades.groupby("symbol")["action"].shift(1)
    trades["prev_pips"] = trades.groupby("symbol")["pips"].shift(1)
    trades["prev_was_buy"] = (trades["prev_action"] == "Buy").astype(float)
    trades["prev_was_loss"] = (trades["prev_pips"] < 0).astype(float)
    # H3a: flip after loss (anti-martingale — prev was Buy & lost → Sell)
    h3a_pred = trades["prev_was_buy"] * (1 - trades["prev_was_loss"]) + (1 - trades["prev_was_buy"]) * trades["prev_was_loss"]
    # I.e., keep if prev won, flip if prev lost
    valid3 = trades["prev_action"].notna() & trades["prev_pips"].notna()
    if valid3.sum() > 0:
        acc_h3a = (h3a_pred[valid3].astype(int) == trades["dir_int"][valid3]).mean()
        print(f"  H3a (keep if won, flip if lost):  {acc_h3a:.4f}  on {valid3.sum()} trades")
        # H3b: same as prev (continuation)
        h3b_pred = trades["prev_was_buy"]
        acc_h3b = (h3b_pred[valid3].astype(int) == trades["dir_int"][valid3]).mean()
        print(f"  H3b (always same as prev):        {acc_h3b:.4f}  on {valid3.sum()} trades")

    print("\n" + "=" * 72)
    print("H4 — day-of-week × pair fixed mapping (lookup table)")
    print("=" * 72)
    lookup = trades.groupby(["dow", "symbol"])["dir_int"].mean()  # mean = P(Buy)
    print(f"  Number of (dow, pair) cells: {len(lookup)}")
    # If P(Buy) > 0.5 → predict Buy; else predict Sell.
    pred_h4 = trades.set_index(["dow", "symbol"]).index.map(lookup) > 0.5
    acc_h4 = (pred_h4.astype(int) == trades["dir_int"].values).mean()
    print(f"  H4 (in-sample lookup, optimistic): {acc_h4:.4f}")
    # This is in-sample — represents an UPPER BOUND on what static (dow, pair) mapping could explain.

    print("\n" + "=" * 72)
    print("H5 — hour-of-day × pair fixed mapping")
    print("=" * 72)
    lookup5 = trades.groupby(["hour", "symbol"])["dir_int"].mean()
    pred_h5 = trades.set_index(["hour", "symbol"]).index.map(lookup5) > 0.5
    acc_h5 = (pred_h5.astype(int) == trades["dir_int"].values).mean()
    print(f"  H5 (in-sample lookup, optimistic): {acc_h5:.4f}")

    print("\n" + "=" * 72)
    print("H6 — open_price vs N-trade trailing average (per pair)")
    print("=" * 72)
    for n in [3, 5, 10, 20]:
        trades[f"open_ma_{n}"] = trades.groupby("symbol")["open_price"].transform(
            lambda s: s.rolling(n, min_periods=n).mean().shift(1)
        )
        h6_mom = (trades["open_price"] > trades[f"open_ma_{n}"]).astype(int)
        h6_mr = 1 - h6_mom
        valid6 = trades[f"open_ma_{n}"].notna()
        if valid6.sum() > 0:
            acc_h6_mom = (h6_mom[valid6] == trades["dir_int"][valid6]).mean()
            acc_h6_mr = (h6_mr[valid6] == trades["dir_int"][valid6]).mean()
            print(f"  N={n:2d}  momentum:  {acc_h6_mom:.4f} | MR: {acc_h6_mr:.4f}  on {valid6.sum()} trades")

    print("\n" + "=" * 72)
    print("H7 — combined per-pair tree (in-sample lookup of pair × hour × dow)")
    print("=" * 72)
    lookup7 = trades.groupby(["symbol", "hour", "dow"])["dir_int"].mean()
    pred_h7 = trades.set_index(["symbol", "hour", "dow"]).index.map(lookup7) > 0.5
    acc_h7 = (pred_h7.astype(int) == trades["dir_int"].values).mean()
    print(f"  H7 (in-sample 3-way lookup): {acc_h7:.4f}")

    print("\n" + "=" * 72)
    print("VEREDICTO")
    print("=" * 72)
    best_no_ohlc = max(acc_h1, acc_h2, acc_h3a, acc_h3b)
    print(f"Best dynamic rule (no OHLC needed): {best_no_ohlc:.4f}")
    print(f"Best in-sample lookup: H7 = {acc_h7:.4f}")
    print(f"Majority class baseline: {max(base_buy_rate, 1-base_buy_rate):.4f}")
    print()
    if best_no_ohlc >= 0.80:
        print("✅ Direction signal RECUPERÁVEL sem OHLC — usar best rule above")
    elif best_no_ohlc >= 0.60:
        print("⚠ Signal parcialmente recuperável — pode complementar com OHLC mas talvez serve")
    else:
        print("❌ Signal NÃO recuperável só com trade-internal features — precisa OHLC externo")


if __name__ == "__main__":
    main()
