"""Exploratory data analysis for a parsed system: timing, exit, sizing, decay, direction.

Merges 04_eda.py (timing/exit/sizing), 04b_direction_decay.py (Buy/Sell + yearly
decay + cost-model-net), and 04c_evening_structure.py (per-session grouping)
into a single `compute_eda` returning a structured dict. Outputs are
DataFrames keyed by axis, ready for assertion in smoke tests or formatting
in markdown reports.

Citations:
- [evidence_based_ta, Aronson, p.367-380] — hour-of-day FX session effects
- [carver_systematic_trading] — direction-signal hypothesis (breakout vs MR)
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from . import config

DOW_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@dataclass
class EDAStats:
    system_id: str
    entry_hour: pd.Series  # index = 0..23, values = counts
    entry_hour_minute_top20: pd.Series  # MultiIndex (hour, min_bucket) → count
    dow_counts: pd.Series  # Monday..Sunday
    per_pair_hour_peak: pd.DataFrame  # symbol → peak_hour, peak_n, total, pct_peak, hours_active
    exit_kind: pd.Series  # near_SL/near_TP/manual_or_time → counts
    exit_hour: pd.Series  # 0..23
    hold_min_hist: pd.Series  # bin → count
    sl_tp_by_year: pd.DataFrame
    pnl_by_pair_gross: pd.DataFrame
    pnl_by_year_gross: pd.DataFrame
    pnl_by_year_net: pd.DataFrame
    pnl_by_pair_net: pd.DataFrame
    direction_by_pair: pd.DataFrame
    direction_by_hour: pd.DataFrame
    direction_by_dow: pd.DataFrame
    yearly_decay: pd.DataFrame
    sessions_per_pair_dist: pd.Series  # n_trades_in_pair_session → count
    sessions_total_dist: dict[str, int]  # bucket label → count
    pairs_per_session_dist: pd.Series
    direction_consistency: dict[str, int]  # all_same, mixed
    spacing_minutes: dict[str, float]
    flip_rate_after_loss: float | None
    round_number_within_5pips_pct: float


def _hist_minutes(durations_min: pd.Series, bins: list[int]) -> pd.Series:
    cuts = pd.cut(durations_min.clip(upper=bins[-1]), bins=bins, include_lowest=True, right=False)
    return cuts.value_counts().sort_index()


def _direction_table(trades: pd.DataFrame, by: str) -> pd.DataFrame:
    bs = trades.groupby([by, "action"]).size().unstack(fill_value=0)
    bs["total"] = bs.sum(axis=1)
    bs["buy_pct"] = (100 * bs.get("Buy", 0) / bs["total"]).round(1)
    return bs


def compute_eda(
    trades_df: pd.DataFrame,
    system_id: int | str,
    cost_model: config.CostModel | None = None,
) -> EDAStats:
    cm = cost_model or config.pepperstone_razor_2025()
    df = trades_df
    trades = df[df["is_trade"]].copy().sort_values("close_dt_utc").reset_index(drop=True)
    trades["open_hour_utc"] = trades["open_dt_utc"].dt.hour
    trades["open_min_utc"] = trades["open_dt_utc"].dt.minute
    trades["close_hour_utc"] = trades["close_dt_utc"].dt.hour
    trades["dow_name"] = trades["open_dt_utc"].dt.day_name()
    trades["year"] = trades["close_dt_utc"].dt.year
    trades["session_date"] = trades["open_dt_utc"].dt.date

    entry_hour = trades.groupby("open_hour_utc").size().reindex(range(24), fill_value=0)
    hm_index = [trades["open_hour_utc"], trades["open_min_utc"] // 5 * 5]
    entry_hm_top20 = trades.groupby(hm_index).size().sort_values(ascending=False).head(20)

    dow_counts = trades.groupby("dow_name").size().reindex(DOW_ORDER, fill_value=0)

    rows = []
    for sym in sorted(trades["symbol"].unique()):
        sub = trades[trades["symbol"] == sym]
        hr = sub.groupby("open_hour_utc").size()
        peak_hr = int(hr.idxmax())
        peak_n = int(hr.max())
        total = len(sub)
        rows.append({
            "symbol": sym,
            "n": total,
            "peak_hour": peak_hr,
            "peak_n": peak_n,
            "pct_peak": round(100 * peak_n / total, 1),
            "hours_active": int(hr.gt(0).sum()),
        })
    per_pair_hour_peak = pd.DataFrame(rows).set_index("symbol")

    trades["close_kind"] = "manual_or_time"
    trades.loc[trades["pips"] <= trades["sl_pips"] + 2, "close_kind"] = "near_SL"
    trades.loc[trades["pips"] >= trades["tp_pips"] - 2, "close_kind"] = "near_TP"
    exit_kind = trades["close_kind"].value_counts()
    exit_hour = trades.groupby("close_hour_utc").size().reindex(range(24), fill_value=0)

    dur_min = (trades["duration_sec"] / 60.0)
    hold_hist = _hist_minutes(dur_min, list(range(0, 245, 15)))

    sl_tp_by_year = trades.groupby("year").agg(
        n=("pips", "count"),
        sl_pips_med=("sl_pips", "median"),
        tp_pips_med=("tp_pips", "median"),
        sl_pips_p95=("sl_pips", lambda s: s.quantile(0.95)),
        tp_pips_p95=("tp_pips", lambda s: s.quantile(0.95)),
    ).round(1)

    pnl_by_pair_gross = trades.groupby("symbol").agg(
        n=("pips", "count"),
        win_pct=("pips", lambda s: 100 * (s > 0).mean()),
        avg_pips=("pips", "mean"),
        median_pips=("pips", "median"),
        total_pips=("pips", "sum"),
        total_profit_usd=("profit", "sum"),
    ).round(2).sort_values("total_pips", ascending=False)

    pnl_by_year_gross = trades.groupby("year").agg(
        n=("pips", "count"),
        win_pct=("pips", lambda s: 100 * (s > 0).mean()),
        avg_pips=("pips", "mean"),
        total_pips=("pips", "sum"),
        total_profit_usd=("profit", "sum"),
    ).round(2)

    trades["cost_pips"] = trades["symbol"].map(lambda s: cm.cost_for(s))
    trades["net_pips"] = trades["pips"] - trades["cost_pips"]

    yr_net = trades.groupby("year").agg(
        n=("net_pips", "count"),
        gross_avg=("pips", "mean"),
        cost_avg=("cost_pips", "mean"),
        net_avg=("net_pips", "mean"),
        net_total=("net_pips", "sum"),
        win_pct_net=("net_pips", lambda s: (s > 0).mean() * 100),
    ).round(2)
    net_std_year = trades.groupby("year")["net_pips"].std()
    yr_net["sharpe_net"] = (yr_net["net_avg"] / net_std_year).round(3)

    pl_net = trades.groupby("symbol").agg(
        n=("net_pips", "count"),
        gross_avg=("pips", "mean"),
        cost=("cost_pips", "first"),
        net_avg=("net_pips", "mean"),
        net_total=("net_pips", "sum"),
        win_pct_net=("net_pips", lambda s: (s > 0).mean() * 100),
    ).round(2).sort_values("net_avg", ascending=False)

    direction_by_pair = _direction_table(trades, "symbol")
    direction_by_hour = _direction_table(trades, "open_hour_utc")
    dd = _direction_table(trades, "dow_name")
    direction_by_dow = dd.reindex([d for d in DOW_ORDER if d in dd.index])

    yearly = trades.groupby("year").agg(
        n=("pips", "count"),
        win_pct=("pips", lambda s: (s > 0).mean() * 100),
        avg_pips=("pips", "mean"),
        std_pips=("pips", "std"),
        median_pips=("pips", "median"),
        total_pips=("pips", "sum"),
    ).round(2)
    yearly["sharpe_naive"] = (yearly["avg_pips"] / yearly["std_pips"]).round(3)

    sessions_per_pair = trades.groupby(["session_date", "symbol"]).size()
    sessions_per_pair_dist = sessions_per_pair.value_counts().sort_index()
    sessions_total = trades.groupby("session_date").size()
    sessions_total_dist = {
        "single": int((sessions_total == 1).sum()),
        "2_to_3": int(((sessions_total >= 2) & (sessions_total <= 3)).sum()),
        "4_to_6": int(((sessions_total >= 4) & (sessions_total <= 6)).sum()),
        "7_plus": int((sessions_total >= 7).sum()),
        "n_distinct_sessions": int(sessions_total.shape[0]),
    }
    pairs_per_session = trades.groupby("session_date")["symbol"].nunique().value_counts().sort_index()

    multi = trades.groupby(["session_date", "symbol"]).agg(
        n=("action", "count"),
        n_buys=("action", lambda s: (s == "Buy").sum()),
        n_sells=("action", lambda s: (s == "Sell").sum()),
    ).reset_index()
    multi_only = multi[multi["n"] >= 2]
    if len(multi_only):
        all_same = ((multi_only["n_buys"] == multi_only["n"]) | (multi_only["n_sells"] == multi_only["n"])).sum()
        mixed = ((multi_only["n_buys"] > 0) & (multi_only["n_sells"] > 0)).sum()
    else:
        all_same = mixed = 0
    direction_consistency = {
        "groups_2plus": int(len(multi_only)),
        "all_same": int(all_same),
        "mixed": int(mixed),
    }

    sorted_t = trades.sort_values(["session_date", "symbol", "open_dt_utc"]).reset_index(drop=True)
    sorted_t["prev_open"] = sorted_t.groupby(["session_date", "symbol"])["open_dt_utc"].shift(1)
    spacing = ((sorted_t["open_dt_utc"] - sorted_t["prev_open"]).dt.total_seconds() / 60.0).dropna()
    spacing_stats = {
        "n": float(len(spacing)),
        "p25": float(spacing.quantile(0.25)) if len(spacing) else float("nan"),
        "p50": float(spacing.median()) if len(spacing) else float("nan"),
        "p95": float(spacing.quantile(0.95)) if len(spacing) else float("nan"),
        "max": float(spacing.max()) if len(spacing) else float("nan"),
    }

    sorted_t["prev_action"] = sorted_t.groupby(["session_date", "symbol"])["action"].shift(1)
    sorted_t["prev_pips"] = sorted_t.groupby(["session_date", "symbol"])["pips"].shift(1)
    sorted_t["dir_changed"] = (sorted_t["action"] != sorted_t["prev_action"]) & sorted_t["prev_action"].notna()
    after_loss = sorted_t[sorted_t["prev_action"].notna() & (sorted_t["prev_pips"] < 0)]
    flip_rate = float(after_loss["dir_changed"].mean()) if len(after_loss) else None

    rdist = (trades["open_price"] * 10000) % 50
    within_5 = ((rdist <= 5).sum() + (rdist >= 45).sum()) / len(trades) * 100

    return EDAStats(
        system_id=str(system_id),
        entry_hour=entry_hour,
        entry_hour_minute_top20=entry_hm_top20,
        dow_counts=dow_counts,
        per_pair_hour_peak=per_pair_hour_peak,
        exit_kind=exit_kind,
        exit_hour=exit_hour,
        hold_min_hist=hold_hist,
        sl_tp_by_year=sl_tp_by_year,
        pnl_by_pair_gross=pnl_by_pair_gross,
        pnl_by_year_gross=pnl_by_year_gross,
        pnl_by_year_net=yr_net,
        pnl_by_pair_net=pl_net,
        direction_by_pair=direction_by_pair,
        direction_by_hour=direction_by_hour,
        direction_by_dow=direction_by_dow,
        yearly_decay=yearly,
        sessions_per_pair_dist=sessions_per_pair_dist,
        sessions_total_dist=sessions_total_dist,
        pairs_per_session_dist=pairs_per_session,
        direction_consistency=direction_consistency,
        spacing_minutes=spacing_stats,
        flip_rate_after_loss=flip_rate,
        round_number_within_5pips_pct=float(within_5),
    )


def format_eda_report(stats: EDAStats, *, generated: str | None = None) -> str:
    """Compact markdown summary. Numbers come from EDAStats — text is best-effort."""
    lines: list[str] = []
    lines.append(f"# EDA — system {stats.system_id}")
    if generated:
        lines.append(f"\nGenerated: {generated}\n")
    lines.append("## Entry hour distribution (UTC)")
    for h, n in stats.entry_hour.items():
        lines.append(f"- {int(h):02d}:00  →  {int(n)}")

    lines.append("\n## Day of week")
    for d, n in stats.dow_counts.items():
        lines.append(f"- {d}: {int(n)}")

    lines.append("\n## Per-pair entry hour peak")
    lines.append("```")
    lines.append(stats.per_pair_hour_peak.to_string())
    lines.append("```")

    lines.append("\n## Exit mechanism")
    for k, v in stats.exit_kind.items():
        lines.append(f"- {k}: {int(v)}")

    lines.append("\n## SL/TP setting evolution (per-year)")
    lines.append("```")
    lines.append(stats.sl_tp_by_year.to_string())
    lines.append("```")

    lines.append("\n## PnL by pair (gross)")
    lines.append("```")
    lines.append(stats.pnl_by_pair_gross.to_string())
    lines.append("```")

    lines.append("\n## PnL by year (net, after Pepperstone Razor 2025 cost model)")
    lines.append("```")
    lines.append(stats.pnl_by_year_net.to_string())
    lines.append("```")

    lines.append("\n## PnL by pair (net)")
    lines.append("```")
    lines.append(stats.pnl_by_pair_net.to_string())
    lines.append("```")

    lines.append("\n## Direction by pair (Buy/Sell)")
    lines.append("```")
    lines.append(stats.direction_by_pair.to_string())
    lines.append("```")

    lines.append("\n## Yearly decay (gross)")
    lines.append("```")
    lines.append(stats.yearly_decay.to_string())
    lines.append("```")

    lines.append("\n## Session structure")
    for k, v in stats.sessions_total_dist.items():
        lines.append(f"- {k}: {v}")
    if stats.flip_rate_after_loss is not None:
        lines.append(f"- Direction flip rate after loss: {100*stats.flip_rate_after_loss:.1f}%")

    return "\n".join(lines)


def write_eda_report(
    trades_df: pd.DataFrame,
    system_id: int | str,
    output_path: Path | None = None,
    cost_model: config.CostModel | None = None,
    *,
    generated: str | None = None,
) -> tuple[EDAStats, Path]:
    stats = compute_eda(trades_df, system_id, cost_model)
    path = output_path or config.eda_report_path(system_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_eda_report(stats, generated=generated))
    return stats, path
