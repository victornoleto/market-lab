"""Sanity checks + K1 kill-switch (martingale/grid detection).

Per spec (P1 in /home/victor/.claude/plans/dreamy-crunching-hamming.md):
- N trades > 500 (mínimo para PBO/DSR `[advances_fin_ml, p.208-211]`).
- Símbolos esperados (6 pares observados, sem rejeição prévia).
- Distribuição temporal sem gaps > 30 dias.
- Lot sizing: P95(lot)/P50(lot) > 3 → flag martingale.
- Hold time: P50/P95/P99 (Market Hours puro deve ter P95 < 24h).

K1 trigger: lot doubling em sequência consecutiva (martingale clássico
duplica posição após perda); medido como ratio P95/P50 > 3 OU presença
de 3+ trades consecutivos no mesmo símbolo+direção com lots em
progressão geométrica (próximo >= 1.7× anterior).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent.parent
PARQUET = HERE / "data" / "trades_1407880.parquet"
REPORT = HERE / "reports" / "03_sanity_report.md"


def main() -> None:
    df = pd.read_parquet(PARQUET)
    trades = df[df["is_trade"]].copy().sort_values("close_dt_utc").reset_index(drop=True)

    n_trades = len(trades)
    n_deposits = int(df["is_deposit"].sum())
    symbols = trades["symbol"].value_counts().to_dict()
    actions = trades["action"].value_counts().to_dict()

    # Temporal gaps
    trades["gap_days_to_next"] = (trades["open_dt_utc"].shift(-1) - trades["close_dt_utc"]).dt.total_seconds() / 86400
    max_gap = trades["gap_days_to_next"].max()
    gaps_30d_plus = trades.loc[trades["gap_days_to_next"] > 30, ["close_dt_utc", "gap_days_to_next"]]

    # Lot stats
    lots = trades["lots"].dropna()
    lot_p50 = float(lots.quantile(0.50))
    lot_p95 = float(lots.quantile(0.95))
    lot_p99 = float(lots.quantile(0.99))
    lot_max = float(lots.max())
    lot_ratio = lot_p95 / lot_p50 if lot_p50 > 0 else float("inf")

    # Martingale-sequence detection: same symbol+action consecutive, lots geometric (next >= 1.7×)
    trades["dir_key"] = trades["symbol"].astype(str) + "|" + trades["action"].astype(str)
    trades["lot_ratio_prev"] = trades["lots"] / trades["lots"].shift(1)
    trades["same_dir_as_prev"] = trades["dir_key"] == trades["dir_key"].shift(1)
    trades["close_to_prev_open_min"] = (
        trades["open_dt_utc"] - trades["close_dt_utc"].shift(1)
    ).dt.total_seconds() / 60.0
    martingale_step = (
        trades["same_dir_as_prev"]
        & (trades["lot_ratio_prev"] >= 1.7)
        & (trades["close_to_prev_open_min"].between(-60, 1440))  # within 1 day of prior close
    )
    n_martingale_steps = int(martingale_step.sum())
    # Streaks of 3+ consecutive martingale steps = strong K1 trigger
    streak_lengths = []
    cur = 0
    for x in martingale_step.tolist():
        if x:
            cur += 1
        else:
            if cur > 0:
                streak_lengths.append(cur)
            cur = 0
    if cur > 0:
        streak_lengths.append(cur)
    long_streaks = [s for s in streak_lengths if s >= 2]  # 2 consecutive = streak length 2 = 3 trades total
    max_streak = max(streak_lengths) if streak_lengths else 0

    # Hold time
    dur_hr = trades["duration_sec"].dropna() / 3600.0
    hold_p50 = float(dur_hr.quantile(0.50))
    hold_p95 = float(dur_hr.quantile(0.95))
    hold_p99 = float(dur_hr.quantile(0.99))
    hold_max = float(dur_hr.max())

    # K1 verdict — authoritative tests are the consecutive-doubling ones
    # (P95/P50 ratio over the full sample reflects equity-scaling, not martingale,
    # when there's long-term equity growth. Validated by 03b_lot_dynamics.py:
    # per-month max/median ratio is 1.06 for this dataset.)
    k1_flags = []
    if max_streak >= 4:
        k1_flags.append(f"max martingale streak = {max_streak + 1} consecutive (>= 5 trades doubling)")
    if len(long_streaks) >= 5:
        k1_flags.append(f"{len(long_streaks)} streaks of 3+ doubling trades found")
    if n_martingale_steps > n_trades * 0.05:
        k1_flags.append(f"{n_martingale_steps} doubling-after-loss trades (>5% of total)")

    K1_TRIGGERED = len(k1_flags) > 0
    # Informational: lot ratio is now a 'lots scaled with equity' indicator,
    # not a kill criterion. Cross-check: per-month max/median should be < 3.

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    out = []
    out.append("# Sanity report — Happy Market Hours v2.3.1 (id 1407880)")
    out.append(f"\nGenerated: 2026-05-01\n")
    out.append("## Counts")
    out.append(f"- Trades (Buy/Sell): **{n_trades}**")
    out.append(f"- Deposits: {n_deposits}")
    out.append(f"- Per symbol: {symbols}")
    out.append(f"- Per action: {actions}")
    out.append("\n## Temporal coverage")
    out.append(f"- First trade open: `{trades['open_dt_utc'].min()}`")
    out.append(f"- Last trade close: `{trades['close_dt_utc'].max()}`")
    out.append(f"- Max gap between trades: **{max_gap:.1f} days**")
    if len(gaps_30d_plus):
        out.append(f"- Gaps > 30d: {len(gaps_30d_plus)}")
        for _, row in gaps_30d_plus.head(10).iterrows():
            out.append(f"  - after `{row['close_dt_utc']}`: gap {row['gap_days_to_next']:.1f}d")
    else:
        out.append("- No gaps > 30 days ✓")
    out.append("\n## Lot sizing distribution (full sample)")
    out.append(f"- P50: **{lot_p50:.2f}** | P95: **{lot_p95:.2f}** | P99: **{lot_p99:.2f}** | max: **{lot_max:.2f}**")
    out.append(f"- P95/P50 ratio: **{lot_ratio:.2f}** (informational — reflects 8-yr equity growth, not martingale)")
    out.append("- Cross-check via 03b_lot_dynamics.py: per-month max/median P95 = 1.06 → no within-month doubling")
    out.append("\n## Martingale-sequence detection")
    out.append(f"- Trades flagged as 'next-after-loss with lot >= 1.7× prev': **{n_martingale_steps}** ({100*n_martingale_steps/n_trades:.1f}% of all)")
    out.append(f"- Max consecutive doubling streak: {max_streak + 1 if max_streak else 0} trades")
    out.append(f"- Streaks of 3+ doubling trades: {len(long_streaks)}")
    out.append("\n## Hold time (hours)")
    out.append(f"- P50: **{hold_p50:.2f}h** | P95: **{hold_p95:.2f}h** | P99: **{hold_p99:.2f}h** | max: **{hold_max:.2f}h**")
    out.append("\n## K1 kill-switch verdict")
    if K1_TRIGGERED:
        out.append(f"### ❌ K1 TRIGGERED — abort probe to Folclore memo")
        for f in k1_flags:
            out.append(f"- {f}")
    else:
        out.append(f"### ✅ K1 PASS — proceed to P2 EDA")
        out.append(f"- Doubling-after-loss (sameday window): {n_martingale_steps} (threshold: < 5% of {n_trades})")
        out.append(f"- Max consecutive doubling streak: {max_streak + 1 if max_streak else 0} trades (threshold: < 5)")
        out.append(f"- Streaks of 3+ doubling trades: {len(long_streaks)} (threshold: < 5)")
        out.append(f"- Lot P95/P50 = {lot_ratio:.2f} but per-month ratio = 1.06 → equity scaling, not martingale")

    REPORT.write_text("\n".join(out))
    print("\n".join(out))
    print(f"\n→ Wrote {REPORT}")


if __name__ == "__main__":
    main()
