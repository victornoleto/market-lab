"""K1 (martingale) kill-switch + lot dynamics + temporal coverage.

Merges 03_sanity.py and 03b_lot_dynamics.py from the prototype. K1 is the
first cheap kill: martingale-style sizing (lot doubling after losses) is a
known catastrophic-tail strategy and disqualifies the system regardless of
on-paper edge `[fooled_by_randomness, Taleb]`.

Per [advances_fin_ml, p.208-211] DSR/PBO require ≥ 500 trades; we flag
sample size here too.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from . import config

MIN_TRADES_FOR_DSR = 500
GAP_DAYS_THRESHOLD = 30
LOT_DOUBLING_RATIO = 1.7
DOUBLING_WITHIN_MIN = 1440  # 24h
PER_MONTH_RATIO_THRESHOLD = 3.0  # > 3.0 = within-month doubling = martingale


@dataclass
class SanityStats:
    system_id: str
    n_trades: int
    n_deposits: int
    n_other: int
    symbols: dict[str, int]
    actions: dict[str, int]
    first_open_utc: pd.Timestamp
    last_close_utc: pd.Timestamp
    max_gap_days: float
    gaps_30d_plus: pd.DataFrame
    lot_p50: float
    lot_p95: float
    lot_p99: float
    lot_max: float
    lot_ratio_p95_p50: float
    per_month_ratio_p95: float
    per_month_ratio_max: float
    n_martingale_steps: int
    max_doubling_streak: int  # # consecutive doubling-after-loss flags
    long_streaks_count: int
    hold_p50_h: float
    hold_p95_h: float
    hold_p99_h: float
    hold_max_h: float
    k1_pass: bool
    k1_flags: list[str] = field(default_factory=list)


def _detect_martingale_steps(trades: pd.DataFrame) -> tuple[pd.Series, int]:
    """Returns (step_flag_series, n_flagged). Step = same dir as prev + lot >=1.7× + within 24h."""
    t = trades.copy()
    t["dir_key"] = t["symbol"].astype(str) + "|" + t["action"].astype(str)
    t["lot_ratio_prev"] = t["lots"] / t["lots"].shift(1)
    t["same_dir_as_prev"] = t["dir_key"] == t["dir_key"].shift(1)
    t["close_to_prev_open_min"] = (t["open_dt_utc"] - t["close_dt_utc"].shift(1)).dt.total_seconds() / 60.0
    flag = (
        t["same_dir_as_prev"]
        & (t["lot_ratio_prev"] >= LOT_DOUBLING_RATIO)
        & (t["close_to_prev_open_min"].between(-60, DOUBLING_WITHIN_MIN))
    )
    return flag.fillna(False), int(flag.sum())


def _streak_lengths(flag: pd.Series) -> list[int]:
    out, cur = [], 0
    for x in flag.tolist():
        if x:
            cur += 1
        elif cur:
            out.append(cur)
            cur = 0
    if cur:
        out.append(cur)
    return out


def compute_sanity(trades_df: pd.DataFrame, system_id: int | str) -> SanityStats:
    """Full sanity stats from raw trades parquet (output of parser.parse_*)."""
    df = trades_df
    trades = df[df["is_trade"]].copy().sort_values("close_dt_utc").reset_index(drop=True)

    n_trades = len(trades)
    n_deposits = int(df["is_deposit"].sum())
    n_other = len(df) - n_trades - n_deposits

    symbols = trades["symbol"].value_counts().to_dict()
    actions = trades["action"].value_counts().to_dict()

    trades["gap_days_to_next"] = (trades["open_dt_utc"].shift(-1) - trades["close_dt_utc"]).dt.total_seconds() / 86400
    max_gap = float(trades["gap_days_to_next"].max())
    gaps_30d_plus = trades.loc[
        trades["gap_days_to_next"] > GAP_DAYS_THRESHOLD,
        ["close_dt_utc", "gap_days_to_next"],
    ].copy()

    lots = trades["lots"].dropna()
    lot_p50 = float(lots.quantile(0.50))
    lot_p95 = float(lots.quantile(0.95))
    lot_p99 = float(lots.quantile(0.99))
    lot_max = float(lots.max())
    lot_ratio = float(lot_p95 / lot_p50) if lot_p50 > 0 else float("inf")

    trades["yyyymm"] = trades["close_dt_utc"].dt.to_period("M").astype(str)
    per_month = trades.groupby("yyyymm")["lots"].agg(["count", "median", "max"]).round(2)
    per_month["max_to_med"] = (per_month["max"] / per_month["median"]).round(2)
    per_month_p95 = float(per_month["max_to_med"].quantile(0.95))
    per_month_max = float(per_month["max_to_med"].max())

    flag, n_steps = _detect_martingale_steps(trades)
    streaks = _streak_lengths(flag)
    max_streak = max(streaks) if streaks else 0
    long_streaks = [s for s in streaks if s >= 2]

    dur_hr = trades["duration_sec"].dropna() / 3600.0
    hold_p50 = float(dur_hr.quantile(0.50))
    hold_p95 = float(dur_hr.quantile(0.95))
    hold_p99 = float(dur_hr.quantile(0.99))
    hold_max = float(dur_hr.max())

    k1_flags: list[str] = []
    if max_streak >= 4:
        k1_flags.append(f"max martingale streak = {max_streak + 1} consecutive (>= 5 trades doubling)")
    if len(long_streaks) >= 5:
        k1_flags.append(f"{len(long_streaks)} streaks of 3+ doubling trades found")
    if n_steps > n_trades * 0.05:
        k1_flags.append(f"{n_steps} doubling-after-loss trades (>5% of total)")
    if per_month_p95 > PER_MONTH_RATIO_THRESHOLD:
        k1_flags.append(
            f"per-month max/median P95 = {per_month_p95:.2f} (> {PER_MONTH_RATIO_THRESHOLD}) — within-month doubling"
        )

    return SanityStats(
        system_id=str(system_id),
        n_trades=n_trades,
        n_deposits=n_deposits,
        n_other=n_other,
        symbols=symbols,
        actions=actions,
        first_open_utc=trades["open_dt_utc"].min(),
        last_close_utc=trades["close_dt_utc"].max(),
        max_gap_days=max_gap,
        gaps_30d_plus=gaps_30d_plus,
        lot_p50=lot_p50,
        lot_p95=lot_p95,
        lot_p99=lot_p99,
        lot_max=lot_max,
        lot_ratio_p95_p50=lot_ratio,
        per_month_ratio_p95=per_month_p95,
        per_month_ratio_max=per_month_max,
        n_martingale_steps=n_steps,
        max_doubling_streak=max_streak,
        long_streaks_count=len(long_streaks),
        hold_p50_h=hold_p50,
        hold_p95_h=hold_p95,
        hold_p99_h=hold_p99,
        hold_max_h=hold_max,
        k1_pass=len(k1_flags) == 0,
        k1_flags=k1_flags,
    )


def format_sanity_report(stats: SanityStats, *, generated: str | None = None) -> str:
    """Markdown rendering of SanityStats. Prefer compute_sanity → assert → write."""
    lines: list[str] = []
    lines.append(f"# Sanity report — system {stats.system_id}")
    if generated:
        lines.append(f"\nGenerated: {generated}\n")
    lines.append("## Counts")
    lines.append(f"- Trades (Buy/Sell): **{stats.n_trades}**")
    lines.append(f"- Deposits: {stats.n_deposits}")
    lines.append(f"- Per symbol: {stats.symbols}")
    lines.append(f"- Per action: {stats.actions}")
    lines.append("\n## Temporal coverage")
    lines.append(f"- First trade open: `{stats.first_open_utc}`")
    lines.append(f"- Last trade close: `{stats.last_close_utc}`")
    lines.append(f"- Max gap between trades: **{stats.max_gap_days:.1f} days**")
    if len(stats.gaps_30d_plus):
        lines.append(f"- Gaps > 30d: {len(stats.gaps_30d_plus)}")
        for _, row in stats.gaps_30d_plus.head(10).iterrows():
            lines.append(f"  - after `{row['close_dt_utc']}`: gap {row['gap_days_to_next']:.1f}d")
    else:
        lines.append("- No gaps > 30 days ✓")
    lines.append("\n## Lot sizing distribution (full sample)")
    lines.append(
        f"- P50: **{stats.lot_p50:.2f}** | P95: **{stats.lot_p95:.2f}** | "
        f"P99: **{stats.lot_p99:.2f}** | max: **{stats.lot_max:.2f}**"
    )
    lines.append(
        f"- P95/P50 ratio: **{stats.lot_ratio_p95_p50:.2f}** "
        f"(informational — long-sample ratio reflects equity scaling, not martingale)"
    )
    lines.append(
        f"- Per-month max/median P95: **{stats.per_month_ratio_p95:.2f}** "
        f"(threshold {PER_MONTH_RATIO_THRESHOLD}); max-month: {stats.per_month_ratio_max:.2f}"
    )
    lines.append("\n## Martingale-sequence detection")
    pct_flag = 100 * stats.n_martingale_steps / stats.n_trades if stats.n_trades else 0.0
    lines.append(
        f"- Trades flagged as 'next-after-loss with lot >= 1.7× prev': **{stats.n_martingale_steps}** "
        f"({pct_flag:.1f}% of all)"
    )
    lines.append(
        f"- Max consecutive doubling streak: {stats.max_doubling_streak + 1 if stats.max_doubling_streak else 0} trades"
    )
    lines.append(f"- Streaks of 3+ doubling trades: {stats.long_streaks_count}")
    lines.append("\n## Hold time (hours)")
    lines.append(
        f"- P50: **{stats.hold_p50_h:.2f}h** | P95: **{stats.hold_p95_h:.2f}h** | "
        f"P99: **{stats.hold_p99_h:.2f}h** | max: **{stats.hold_max_h:.2f}h**"
    )
    lines.append("\n## K1 kill-switch verdict")
    if stats.k1_pass:
        lines.append("### ✅ K1 PASS — proceed to P2 EDA")
        lines.append(
            f"- Doubling-after-loss (sameday window): {stats.n_martingale_steps} (threshold: < 5% of {stats.n_trades})"
        )
        lines.append(
            f"- Max consecutive doubling streak: "
            f"{stats.max_doubling_streak + 1 if stats.max_doubling_streak else 0} trades (threshold: < 5)"
        )
        lines.append(f"- Streaks of 3+ doubling trades: {stats.long_streaks_count} (threshold: < 5)")
        lines.append(
            f"- Lot P95/P50 = {stats.lot_ratio_p95_p50:.2f} but per-month ratio = {stats.per_month_ratio_p95:.2f} "
            f"→ equity scaling, not martingale"
        )
    else:
        lines.append("### ❌ K1 TRIGGERED — abort probe to Folclore memo")
        for f in stats.k1_flags:
            lines.append(f"- {f}")
    if stats.n_trades < MIN_TRADES_FOR_DSR:
        lines.append(
            f"\n⚠ N trades = {stats.n_trades} < {MIN_TRADES_FOR_DSR} → DSR/PBO unreliable "
            f"`[advances_fin_ml, p.208-211]`"
        )
    return "\n".join(lines)


def write_sanity_report(
    trades_df: pd.DataFrame,
    system_id: int | str,
    output_path: Path | None = None,
    *,
    generated: str | None = None,
) -> tuple[SanityStats, Path]:
    stats = compute_sanity(trades_df, system_id)
    path = output_path or config.sanity_report_path(system_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_sanity_report(stats, generated=generated))
    return stats, path
