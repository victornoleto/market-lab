#!/usr/bin/env python3
"""Phase B Lead #6: Regime decomposition for all confirmed Phase A winners.

Decomposes strategy performance by:
  1. Year (full IS history)
  2. VIXY quintile (Q1=calm → Q5=panic; 2021-2026 where VIXY available)
  3. Year × VIXY heatmap (BollingerMR only — enough trades per cell)

Winners analysed:
  - BollingerMR GARCH SPY 1h  [SHORT-HOLD CFD, Path A]
  - ETFRotation monthly top-1  [SWING BROKER, Path B]

Goal: identify pause-trigger thresholds — VIX quintiles or years where
the strategy actively loses money in IS, informing live risk management.

Citations:
  [advances_fin_ml, p.215-219, ch.13] — regime stress / partitioning
  [machine_trading, p.126-127] — EWMA-GARCH vol sizing
  [stocks_on_the_move, p.81/66/95] — ETFRotation canonical params
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import date, timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

log = logging.getLogger("ai_trade.regime_decomp_phase_b")

STORAGE_ROOT = Path("data/tiingo")
REPORTS_DIR = Path("reports/regime_decomp_phase_b")

# ── BollingerMR: IS trade CSV (period="train") ──────────────────────────────
BOLLINGER_TRADES_CSV = Path("reports/bollinger_mr_trades/SPY_garch_2025-01-01_2026-04-14.csv")

# ── ETFRotation canonical params ─────────────────────────────────────────────
ETF_SYMBOLS = ["SPY", "QQQ", "IWM", "GLD", "TLT"]
ETF_INDEX = "SPY"
ETF_IS_START = date(2005, 1, 3)
ETF_IS_END = date(2024, 12, 31)

# ── VIXY availability ─────────────────────────────────────────────────────────
VIXY_START = date(2021, 1, 4)
VIXY_END = date(2026, 4, 15)
N_QUINTILES = 5


# ─────────────────────────────────────────────────────────────────────────────
# Data helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_vixy(storage_root: Path) -> pd.Series:
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    src = TiingoSource(storage=TiingoStorage(root=storage_root))
    df = src.fetch("VIXY", VIXY_START, VIXY_END, asset_class="etf", frequency="daily")
    if df.empty:
        raise RuntimeError("VIXY data not found in Tiingo storage")
    df.index = pd.to_datetime(df.index).normalize()
    series = df["close"].sort_index()
    log.info("VIXY: %d bars [%s → %s], median=%.2f",
             len(series), series.index[0].date(), series.index[-1].date(), float(series.median()))
    return series


def compute_quintile_edges(vixy: pd.Series) -> np.ndarray:
    """Compute quintile breakpoints over the full VIXY series."""
    edges = np.percentile(vixy.values, np.linspace(0, 100, N_QUINTILES + 1))
    edges[0] -= 1e-9
    edges[-1] += 1e-9
    return edges


def assign_quintile(value: float, edges: np.ndarray) -> int | None:
    """Return quintile 1-5 for a value, or None if outside range."""
    for q in range(1, N_QUINTILES + 1):
        if edges[q - 1] <= value < edges[q]:
            return q
    return None


# ─────────────────────────────────────────────────────────────────────────────
# BollingerMR regime analysis
# ─────────────────────────────────────────────────────────────────────────────

def analyse_bollinger_mr(vixy: pd.Series, edges: np.ndarray, out_dir: Path) -> dict:
    """Year × VIX regime decomp for BollingerMR SPY 1h IS trades."""
    log.info("Loading BollingerMR trades from %s", BOLLINGER_TRADES_CSV)
    df = pd.read_csv(BOLLINGER_TRADES_CSV)
    df_is = df[df["period"] == "train"].copy()
    log.info("BollingerMR IS trades: %d (OOS: %d)", len(df_is), (df["period"] == "oos").sum())

    df_is["entry_dt"] = pd.to_datetime(df_is["entry_time"])
    df_is["entry_date"] = df_is["entry_dt"].dt.normalize()
    df_is["year"] = df_is["entry_dt"].dt.year

    # Trade return (long only by design)
    side = df_is["side"].astype(str).str.lower()
    pr = (df_is["exit_price"] - df_is["entry_price"]) / df_is["entry_price"]
    df_is["trade_ret"] = pr.where(side == "long", -pr)

    # Attach VIXY quintile
    df_is = df_is.merge(
        vixy.rename("vixy_close"),
        how="left", left_on="entry_date", right_index=True,
    )
    df_is["vixy_close"] = df_is["vixy_close"].ffill()

    # Trades before VIXY start get NaN quintile
    df_is["quintile"] = df_is["vixy_close"].apply(
        lambda v: assign_quintile(v, edges) if pd.notna(v) else None,
    )

    # ── Year decomp (all years, VIXY not required) ───────────────────────────
    year_rows = []
    for yr in sorted(df_is["year"].unique()):
        sub = df_is[df_is["year"] == yr]
        n = len(sub)
        if n == 0:
            continue
        rets = sub["trade_ret"]
        wr = (rets > 0).mean()
        mean_r = float(rets.mean())
        sh = float(rets.mean() / rets.std() * np.sqrt(50)) if n >= 5 and rets.std() > 0 else np.nan
        year_rows.append({"year": yr, "n": n, "wr": wr, "mean_ret_pct": mean_r * 100, "sharpe": sh})
    year_df = pd.DataFrame(year_rows)

    # ── Quintile decomp (2021+ only) ─────────────────────────────────────────
    df_q = df_is[df_is["quintile"].notna()].copy()
    q_rows = []
    for q in range(1, N_QUINTILES + 1):
        sub = df_q[df_q["quintile"] == q]
        n = len(sub)
        rets = sub["trade_ret"] if n > 0 else pd.Series(dtype=float)
        wr = float((rets > 0).mean()) if n > 0 else np.nan
        mean_r = float(rets.mean()) if n > 0 else np.nan
        sh = (float(rets.mean() / rets.std() * np.sqrt(50))
              if n >= 5 and len(rets) > 1 and rets.std() > 0 else np.nan)
        q_rows.append({
            "quintile": q, "label": ["calm", "low", "mid", "high", "panic"][q - 1],
            "vixy_range": f"{edges[q-1]:.1f}–{edges[q]:.1f}",
            "n": n, "wr": wr, "mean_ret_pct": mean_r * 100 if not np.isnan(mean_r) else np.nan,
            "sharpe": sh,
        })
    q_df = pd.DataFrame(q_rows)

    # ── Year × Quintile heatmap ───────────────────────────────────────────────
    years_q = sorted(df_q["year"].unique())
    heat_data = np.full((len(years_q), N_QUINTILES), np.nan)
    heat_n = np.zeros((len(years_q), N_QUINTILES), dtype=int)
    for i, yr in enumerate(years_q):
        for j, q in enumerate(range(1, N_QUINTILES + 1)):
            sub = df_q[(df_q["year"] == yr) & (df_q["quintile"] == q)]
            n = len(sub)
            heat_n[i, j] = n
            if n >= 5:
                rets = sub["trade_ret"]
                heat_data[i, j] = float(rets.mean() / rets.std() * np.sqrt(50)) if rets.std() > 0 else np.nan

    _plot_heatmap(heat_data, heat_n, years_q, "BollingerMR GARCH SPY 1h",
                  out_dir / "heatmap_bollinger_mr.png")

    # ── Pause-trigger logic ───────────────────────────────────────────────────
    losing_quintiles = [r["quintile"] for _, r in q_df.iterrows()
                        if not np.isnan(r["sharpe"]) and r["sharpe"] < 0 and r["n"] >= 5]
    losing_years = [r["year"] for _, r in year_df.iterrows()
                    if not np.isnan(r["sharpe"]) and r["sharpe"] < 0]

    return {
        "year_df": year_df,
        "quintile_df": q_df,
        "losing_quintiles": losing_quintiles,
        "losing_years": losing_years,
        "n_trades_is": len(df_is),
        "n_trades_with_vixy": len(df_q),
    }


# ─────────────────────────────────────────────────────────────────────────────
# ETFRotation regime analysis
# ─────────────────────────────────────────────────────────────────────────────

def run_etf_rotation_equity(storage_root: Path) -> pd.Series:
    """Run ETFRotation IS backtest and return daily equity curve."""
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    from ai_trade.backtest.engine import ExecutionConfig, ExecutionSimulator, Runner
    from ai_trade.backtest.strategies.etf_rotation import ETFRotationStrategy

    src = TiingoSource(storage=TiingoStorage(root=storage_root))
    warmup = ETF_IS_START - timedelta(days=500)
    log.info("Fetching ETF data %s → %s", warmup, ETF_IS_END)
    raw = src.fetch_many(ETF_SYMBOLS, warmup, ETF_IS_END, asset_class="etf", frequency="daily")
    missing = [s for s in ETF_SYMBOLS if s not in raw or raw[s].empty]
    if missing:
        raise RuntimeError(f"Missing ETF data: {missing}")

    data_full = {sym: raw[sym] for sym in ETF_SYMBOLS}
    data_bounded = {
        sym: df.loc[pd.Timestamp(ETF_IS_START): pd.Timestamp(ETF_IS_END)]
        for sym, df in data_full.items()
    }

    strategy = ETFRotationStrategy(
        data=data_full, symbols=ETF_SYMBOLS, index_symbol=ETF_INDEX,
        lookback=90, sma_index_period=200, sma_stock_period=100, top_n=1,
    )
    runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
    result = runner.run(strategy=strategy, data=data_bounded, initial_cash=100_000.0)
    if result is None:
        raise RuntimeError("ETFRotation backtest returned None")
    eq = result.equity_curve
    log.info("ETFRotation equity curve: %d bars [%s → %s]", len(eq), eq.index[0].date(), eq.index[-1].date())
    return eq


def analyse_etf_rotation(vixy: pd.Series, edges: np.ndarray, out_dir: Path) -> dict:
    """Year + VIX regime decomp for ETFRotation IS equity curve."""
    eq = run_etf_rotation_equity(STORAGE_ROOT)

    # Monthly returns from daily equity curve
    # Use month-start resampling so each monthly bucket represents one rebalance
    eq_monthly_start = eq.resample("MS").first()
    monthly_rets = eq_monthly_start.pct_change().dropna()
    log.info("ETFRotation monthly returns: %d months (%.1f years)",
             len(monthly_rets), len(monthly_rets) / 12)

    # ── Year decomp (all IS years) ────────────────────────────────────────────
    year_rows = []
    for yr in sorted(monthly_rets.index.year.unique()):
        sub = monthly_rets[monthly_rets.index.year == yr]
        n = len(sub)
        if n == 0:
            continue
        sh = (float(sub.mean() / sub.std() * np.sqrt(12))
              if n >= 3 and sub.std() > 0 else np.nan)
        cagr_yr = float((1 + sub).prod() - 1) if n > 0 else np.nan
        year_rows.append({
            "year": yr, "n_months": n,
            "annual_ret_pct": cagr_yr * 100,
            "sharpe_ann": sh,
        })
    year_df = pd.DataFrame(year_rows)

    # ── VIX quintile decomp (2021+) ───────────────────────────────────────────
    # Associate each month with VIXY at month start
    vixy_at_month = monthly_rets.index.map(
        lambda ts: vixy.asof(ts) if ts.date() >= VIXY_START else np.nan
    )
    monthly_with_q = monthly_rets.copy().to_frame("ret")
    monthly_with_q["vixy"] = vixy_at_month
    monthly_with_q["quintile"] = monthly_with_q["vixy"].apply(
        lambda v: assign_quintile(v, edges) if pd.notna(v) else None
    )
    df_q = monthly_with_q[monthly_with_q["quintile"].notna()]

    q_rows = []
    for q in range(1, N_QUINTILES + 1):
        sub = df_q[df_q["quintile"] == q]["ret"]
        n = len(sub)
        sh = (float(sub.mean() / sub.std() * np.sqrt(12))
              if n >= 3 and len(sub) > 1 and sub.std() > 0 else np.nan)
        ann_ret = float((1 + sub).prod() ** (12 / max(n, 1)) - 1) if n > 0 else np.nan
        q_rows.append({
            "quintile": q, "label": ["calm", "low", "mid", "high", "panic"][q - 1],
            "vixy_range": f"{edges[q-1]:.1f}–{edges[q]:.1f}",
            "n_months": n,
            "ann_ret_pct": ann_ret * 100 if not np.isnan(ann_ret) else np.nan,
            "sharpe_ann": sh,
        })
    q_df = pd.DataFrame(q_rows)

    # ── Pause-trigger ─────────────────────────────────────────────────────────
    losing_quintiles = [r["quintile"] for _, r in q_df.iterrows()
                        if not np.isnan(r["sharpe_ann"]) and r["sharpe_ann"] < 0 and r["n_months"] >= 3]
    losing_years = [r["year"] for _, r in year_df.iterrows()
                    if not np.isnan(r["sharpe_ann"]) and r["sharpe_ann"] < 0]

    # ── Year × Quintile bar chart ─────────────────────────────────────────────
    years_q = sorted(df_q.index.year.unique())
    _plot_etf_year_bar(year_df, out_dir / "bar_etf_rotation_year.png")

    return {
        "year_df": year_df,
        "quintile_df": q_df,
        "losing_quintiles": losing_quintiles,
        "losing_years": losing_years,
        "n_months": len(monthly_rets),
        "n_months_with_vixy": len(df_q),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Plotting helpers
# ─────────────────────────────────────────────────────────────────────────────

def _plot_heatmap(data: np.ndarray, n_data: np.ndarray, years: list, title: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, max(4, len(years) * 0.7)))
    vmax = max(np.nanmax(np.abs(data)) if not np.all(np.isnan(data)) else 1.0, 0.1)
    im = ax.imshow(data, vmin=-vmax, vmax=vmax, cmap="RdBu_r", aspect="auto")
    ax.set_xticks(range(N_QUINTILES))
    ax.set_xticklabels([f"Q{q}\n{['calm','low','mid','high','panic'][q-1]}" for q in range(1, N_QUINTILES + 1)])
    ax.set_yticks(range(len(years)))
    ax.set_yticklabels([str(y) for y in years])
    for i in range(len(years)):
        for j in range(N_QUINTILES):
            n = int(n_data[i, j])
            sh = data[i, j]
            if np.isnan(sh):
                ax.text(j, i, f"n={n}", ha="center", va="center", color="gray", fontsize=8)
            else:
                color = "white" if abs(sh) > 0.5 * vmax else "black"
                ax.text(j, i, f"{sh:.2f}\nn={n}", ha="center", va="center", color=color, fontsize=8)
    ax.set_xlabel("VIXY Quintile (regime)")
    ax.set_ylabel("Year")
    ax.set_title(f"{title}\nTrade-level Sharpe (×√50 annualisation)")
    fig.colorbar(im, ax=ax, label="Trade Sharpe")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    log.info("Saved heatmap: %s", path)


def _plot_etf_year_bar(year_df: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4))
    colors = ["#d32f2f" if r < 0 else "#1976d2" for r in year_df["annual_ret_pct"]]
    ax.bar(year_df["year"].astype(str), year_df["annual_ret_pct"], color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Year")
    ax.set_ylabel("Annual Return (%)")
    ax.set_title("ETFRotation monthly top-1 — Annual Return by Year (IS 2005–2024)")
    plt.xticks(rotation=45)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    log.info("Saved ETF year bar: %s", path)


# ─────────────────────────────────────────────────────────────────────────────
# Markdown report
# ─────────────────────────────────────────────────────────────────────────────

def write_report(bm: dict, etf: dict, edges: np.ndarray, out_dir: Path) -> Path:
    lines = [
        "# Phase B Lead #6 — Regime Decomposition",
        "",
        "Analyses both Phase A winners by year and VIX regime (VIXY proxy).",
        "**Goal:** identify pause-trigger conditions for live trading.",
        "",
        "VIX proxy: **VIXY** daily close (Tiingo storage, 2021-01-04 onward).",
        "VIXY quintile edges computed over 2021–2026 universe.",
        "",
        "## Quintile thresholds (VIXY close)",
        "",
        "| Quintile | VIXY range | Regime |",
        "|---|---|---|",
    ]
    for q in range(1, N_QUINTILES + 1):
        label = ["calm", "low", "mid", "high", "panic"][q - 1]
        lines.append(f"| Q{q} | {edges[q-1]:.2f} – {edges[q]:.2f} | {label} |")

    # ── BollingerMR ──────────────────────────────────────────────────────────
    lines += [
        "",
        "---",
        "",
        "## BollingerMR GARCH SPY 1h  [SHORT-HOLD CFD, Path A]",
        "",
        f"IS trades: {bm['n_trades_is']}  |  Trades with VIXY data (2021+): {bm['n_trades_with_vixy']}",
        "",
        "### Year decomp (all IS years, no VIX requirement)",
        "",
        "| Year | n | WR | Mean ret | Sharpe(×√50) |",
        "|---|---|---|---|---|",
    ]
    for _, r in bm["year_df"].iterrows():
        sh_str = f"{r['sharpe']:+.3f}" if not np.isnan(r["sharpe"]) else "n/a"
        wr_str = f"{r['wr']*100:.1f}%" if not np.isnan(r.get("wr", np.nan)) else "—"
        mr_str = f"{r['mean_ret_pct']:+.3f}%" if not np.isnan(r["mean_ret_pct"]) else "—"
        lines.append(f"| {int(r['year'])} | {int(r['n'])} | {wr_str} | {mr_str} | {sh_str} |")

    lines += [
        "",
        "### VIXY quintile decomp (2021-2026 IS trades)",
        "",
        "| Quintile | Range | n | WR | Mean ret | Sharpe(×√50) |",
        "|---|---|---|---|---|---|",
    ]
    for _, r in bm["quintile_df"].iterrows():
        sh_str = f"{r['sharpe']:+.3f}" if not np.isnan(r.get("sharpe", np.nan)) else "n/a (low n)"
        wr_str = f"{r['wr']*100:.1f}%" if not np.isnan(r.get("wr", np.nan)) else "—"
        mr_str = f"{r['mean_ret_pct']:+.3f}%" if not np.isnan(r.get("mean_ret_pct", np.nan)) else "—"
        lines.append(f"| Q{int(r['quintile'])} {r['label']} | {r['vixy_range']} | {int(r['n'])} | {wr_str} | {mr_str} | {sh_str} |")

    lines += [
        "",
        "![BollingerMR heatmap](heatmap_bollinger_mr.png)",
        "",
    ]

    # Pause trigger analysis
    if bm["losing_quintiles"]:
        qs = ", ".join(f"Q{q}" for q in bm["losing_quintiles"])
        lines.append(f"**⚠️ Losing quintiles (n≥5, Sharpe<0):** {qs} → live pause trigger candidates.")
    else:
        lines.append("**✅ No losing quintiles (n≥5, Sharpe<0) in IS.** Strategy edge holds across all VIX regimes.")

    if bm["losing_years"]:
        yrs = ", ".join(str(y) for y in bm["losing_years"])
        lines.append(f"**⚠️ Losing years:** {yrs}")
    else:
        lines.append("**✅ No losing years in IS.**")

    # ── ETFRotation ──────────────────────────────────────────────────────────
    lines += [
        "",
        "---",
        "",
        "## ETFRotation monthly top-1  [SWING BROKER, Path B]",
        "",
        f"IS months: {etf['n_months']} (2005–2024)  |  Months with VIXY data (2021+): {etf['n_months_with_vixy']}",
        "",
        "### Year decomp (all IS years)",
        "",
        "| Year | n_months | Annual ret | Sharpe(ann) |",
        "|---|---|---|---|",
    ]
    for _, r in etf["year_df"].iterrows():
        sh_str = f"{r['sharpe_ann']:+.3f}" if not np.isnan(r.get("sharpe_ann", np.nan)) else "n/a"
        ar_str = f"{r['annual_ret_pct']:+.1f}%" if not np.isnan(r["annual_ret_pct"]) else "—"
        lines.append(f"| {int(r['year'])} | {int(r['n_months'])} | {ar_str} | {sh_str} |")

    lines += [
        "",
        "![ETFRotation annual bar](bar_etf_rotation_year.png)",
        "",
        "### VIXY quintile decomp (2021-2024 months)",
        "",
        "| Quintile | Range | n_months | Ann. ret | Sharpe(ann) |",
        "|---|---|---|---|---|",
    ]
    for _, r in etf["quintile_df"].iterrows():
        sh_str = f"{r['sharpe_ann']:+.3f}" if not np.isnan(r.get("sharpe_ann", np.nan)) else "n/a (low n)"
        ar_str = f"{r['ann_ret_pct']:+.1f}%" if not np.isnan(r.get("ann_ret_pct", np.nan)) else "—"
        lines.append(f"| Q{int(r['quintile'])} {r['label']} | {r['vixy_range']} | {int(r['n_months'])} | {ar_str} | {sh_str} |")

    lines += [""]
    if etf["losing_quintiles"]:
        qs = ", ".join(f"Q{q}" for q in etf["losing_quintiles"])
        lines.append(f"**⚠️ Losing quintiles (n≥3, Sharpe<0):** {qs} → consider pause in these regimes.")
    else:
        lines.append("**✅ No losing quintiles (n≥3) in IS 2021-2024 window.**")

    if etf["losing_years"]:
        yrs = ", ".join(str(y) for y in etf["losing_years"])
        lines.append(f"**⚠️ Losing years (IS):** {yrs}")
    else:
        lines.append("**✅ No losing years in IS 2005-2024.**")

    # ── Cross-winner comparison ───────────────────────────────────────────────
    lines += [
        "",
        "---",
        "",
        "## Cross-winner regime concordance",
        "",
        "Do both strategies lose in the same VIX quintiles?  ",
        "If so, the portfolio blend offers no diversification in that regime.",
        "",
    ]
    bm_bad = set(bm["losing_quintiles"])
    etf_bad = set(etf["losing_quintiles"])
    overlap = bm_bad & etf_bad
    if overlap:
        qs = ", ".join(f"Q{q}" for q in sorted(overlap))
        lines.append(f"**Both strategies lose in:** {qs} → portfolio-level pause trigger.")
    elif not bm_bad and not etf_bad:
        lines.append("**✅ Neither strategy has a losing quintile (n-sufficient) → full regime robustness.**")
    else:
        lines.append("**✅ No overlapping losing quintiles** → blend provides regime diversification.")

    lines += [
        "",
        "## Citations",
        "",
        "- `[advances_fin_ml, p.215-219, ch.13]` — regime stress / partitioning",
        "- `[machine_trading, p.126-127]` — EWMA-GARCH vol sizing",
        "- `[stocks_on_the_move, p.81/66/95]` — ETFRotation canonical params",
    ]

    report_path = out_dir / "summary.md"
    report_path.write_text("\n".join(lines))
    log.info("Wrote report: %s", report_path)
    return report_path


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    log.info("=== Phase B Lead #6: Regime Decomposition ===")

    log.info("Loading VIXY proxy (VIX regime) ...")
    vixy = load_vixy(STORAGE_ROOT)
    edges = compute_quintile_edges(vixy)
    log.info("VIXY quintile edges: %s", [f"{e:.2f}" for e in edges])

    log.info("Analysing BollingerMR GARCH SPY 1h [SHORT-HOLD CFD] ...")
    bm_result = analyse_bollinger_mr(vixy, edges, REPORTS_DIR)

    log.info("Analysing ETFRotation monthly top-1 [SWING BROKER] ...")
    etf_result = analyse_etf_rotation(vixy, edges, REPORTS_DIR)

    report = write_report(bm_result, etf_result, edges, REPORTS_DIR)

    # ── Console summary ───────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("REGIME DECOMPOSITION — Phase B Lead #6")
    print("=" * 65)
    print(f"\nVIXY quintile edges: {[f'{e:.1f}' for e in edges]}")
    print(f"\n{'BollingerMR SPY 1h':}")
    print(f"  IS trades: {bm_result['n_trades_is']}  (with VIXY: {bm_result['n_trades_with_vixy']})")
    print(f"  Losing quintiles (n≥5): {bm_result['losing_quintiles'] or 'none'}")
    print(f"  Losing years: {bm_result['losing_years'] or 'none'}")
    print(f"\n{'ETFRotation monthly top-1':}")
    print(f"  IS months: {etf_result['n_months']}  (with VIXY: {etf_result['n_months_with_vixy']})")
    print(f"  Losing quintiles (n≥3): {etf_result['losing_quintiles'] or 'none'}")
    print(f"  Losing years: {etf_result['losing_years'] or 'none'}")
    print(f"\nReport → {report}")

    # Save JSON for jornada reference
    out_json = REPORTS_DIR / "regime_decomp_results.json"
    out_json.write_text(json.dumps({
        "bollinger_mr": {
            "n_trades_is": bm_result["n_trades_is"],
            "n_trades_with_vixy": bm_result["n_trades_with_vixy"],
            "losing_quintiles": bm_result["losing_quintiles"],
            "losing_years": bm_result["losing_years"],
            "year_table": bm_result["year_df"].to_dict(orient="records"),
            "quintile_table": bm_result["quintile_df"].to_dict(orient="records"),
        },
        "etf_rotation": {
            "n_months": etf_result["n_months"],
            "n_months_with_vixy": etf_result["n_months_with_vixy"],
            "losing_quintiles": etf_result["losing_quintiles"],
            "losing_years": etf_result["losing_years"],
            "year_table": etf_result["year_df"].to_dict(orient="records"),
            "quintile_table": etf_result["quintile_df"].to_dict(orient="records"),
        },
        "vixy_edges": [float(e) for e in edges],
    }, indent=2, default=str))
    log.info("JSON results: %s", out_json)

    return 0


if __name__ == "__main__":
    sys.exit(main())
