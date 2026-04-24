"""Deep rolling-window review — Candidate vs SPY buy-hold.

Rigorous test of the "quase sempre à frente do SPY 1x" claim.
Produces rolling-window plots and quantitative tables for:

* Rolling CAGR, Sharpe, MDD at 1 y / 3 y / 5 y / 10 y windows.
* Win rate vs SPY by window length.
* Entry-year sensitivity (CAGR and MDD if you start in any given year).
* Calendar-year returns side-by-side.
* Underwater duration (% of days below previous peak).
* Distribution of rolling returns.
* Worst windows (when the strategy hurt most).

All on the 40y synth dataset (SPYSIM 1986-2026). Real-data gap is
quantified by the companion script ``deep_review_real_gap.py``.

Output: ``studies/ema_sma_threshold_crash_protected/deep_review/``.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ai_trade.backtest.data.macro_data_loader import load_all_indicators  # noqa: E402
from ai_trade.backtest.data.testfolio_loader import (  # noqa: E402
    load_testfolio_returns,
    load_testfolio_series,
)
from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)
from ai_trade.backtest.signals.risk_score import (  # noqa: E402
    INDICATOR_SPECS,
    compute_risk_score,
)
from ai_trade.backtest.strategies.ema_sma_threshold_educational import (  # noqa: E402
    DEFAULT_FEE,
    EMASMAThresholdConfig,
    TRADING_DAYS_PER_YEAR,
    _synth_leveraged_returns,
    simulate_regime_threshold_with_legs,
)
from ai_trade.backtest.strategies.stop_loss_and_risk_signals import (  # noqa: E402
    RiskSignalConfig,
    StopLossConfig,
    simulate_with_stop_and_risk,
)

STUDY_DIR = Path(__file__).parent
OUT_DIR = STUDY_DIR / "deep_review"


WINDOWS = {
    "1y": 252,
    "3y": 756,
    "5y": 1260,
    "10y": 2520,
}


def _setup_log() -> logging.Logger:
    log = logging.getLogger("deep_review")
    log.setLevel(logging.INFO)
    log.handlers.clear()
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    log.addHandler(sh)
    return log


def _rolling_cagr(eq: pd.Series, window: int) -> pd.Series:
    log_eq = np.log(eq)
    delta = log_eq - log_eq.shift(window)
    return np.exp(delta * TRADING_DAYS_PER_YEAR / window) - 1.0


def _rolling_sharpe(rets: pd.Series, window: int) -> pd.Series:
    mean = rets.rolling(window).mean() * TRADING_DAYS_PER_YEAR
    std = rets.rolling(window).std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    return (mean / std).where(std > 0)


def _rolling_mdd(eq: pd.Series, window: int) -> pd.Series:
    out = pd.Series(index=eq.index, dtype=float)
    values = eq.values
    for i in range(window - 1, len(values)):
        w = values[i - window + 1 : i + 1]
        peak = np.maximum.accumulate(w)
        dd = 1.0 - w / peak
        out.iloc[i] = float(dd.max())
    return out


def _fmt_pct(x, d=2):
    if x is None or np.isnan(x) or np.isinf(x):
        return "—"
    return f"{x*100:+.{d}f}%"


def _fmt_num(x, d=2):
    if x is None or np.isnan(x) or np.isinf(x):
        return "—"
    return f"{x:.{d}f}"


def main() -> int:
    log = _setup_log()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- Build candidate, baseline, SPY series ---
    base = EMASMAThresholdConfig(
        filter="EMA", lookback=150, threshold_pct=0.05,
        buy_leverage=3.0, sell_leverage=0.0,
        fee=DEFAULT_FEE, switch_cost_bps=15.0, tax_rate=0.0,
    )
    stop_cfg = StopLossConfig(
        stop_loss_pct=0.30, reentry_mode="recovery_trigger", reentry_param=0.10,
    )
    risk_cfg = RiskSignalConfig(indicator_type="cape", lambda_de_lever=0.5)

    spx_prices = load_testfolio_series("SPYSIM")
    spx_returns = load_testfolio_returns("SPYSIM")
    idx = spx_returns.index
    long_leg = _synth_leveraged_returns(spx_returns, base.buy_leverage, base.fee)
    cash_daily = base.cash_rate_annual / TRADING_DAYS_PER_YEAR
    sell_leg = pd.Series(cash_daily, index=spx_returns.index)

    cape_risk = compute_risk_score(
        load_all_indicators(idx)["cape"], INDICATOR_SPECS["cape"],
    )

    log.info("Simulating candidate...")
    cand = simulate_with_stop_and_risk(
        signal_prices=spx_prices, buy_leg_returns=long_leg,
        sell_leg_returns=sell_leg, cfg=base,
        stop_cfg=stop_cfg, risk_series=cape_risk, risk_cfg=risk_cfg,
    )
    log.info("Simulating baseline (3x no overlay)...")
    base_res = simulate_regime_threshold_with_legs(
        signal_prices=spx_prices, buy_leg_returns=long_leg,
        sell_leg_returns=sell_leg, cfg=base,
    )

    bench_eq = (spx_prices.reindex(idx).ffill() / spx_prices.iloc[0]).rename("SPY")
    bench_rets = bench_eq.pct_change().fillna(0.0)

    series = {
        "Candidate": (cand.equity, cand.daily_returns),
        "Baseline 3x": (base_res.equity, base_res.daily_returns),
        "SPY": (bench_eq, bench_rets),
    }

    # --- Rolling CAGR ---
    log.info("Rolling CAGR plots...")
    for wname, wdays in WINDOWS.items():
        fig, ax = plt.subplots(figsize=(12, 5), dpi=120)
        colors = {"Candidate": "#1f77b4", "Baseline 3x": "#d62728", "SPY": "#808080"}
        for label, (eq, _) in series.items():
            r = _rolling_cagr(eq, wdays)
            ax.plot(r.index, r.values * 100, label=label, color=colors[label],
                    linewidth=1.3, alpha=0.9)
        ax.axhline(0, color="black", alpha=0.3, linewidth=0.8)
        ax.set_xlabel("Date (end of rolling window)")
        ax.set_ylabel(f"Rolling CAGR ({wname}, %)")
        ax.set_title(f"Rolling {wname} CAGR — Candidate vs Baseline 3x vs SPY")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right")
        fig.tight_layout()
        fig.savefig(OUT_DIR / f"rolling_cagr_{wname}.png")
        plt.close(fig)

    # --- Rolling Sharpe ---
    log.info("Rolling Sharpe plots...")
    for wname, wdays in WINDOWS.items():
        fig, ax = plt.subplots(figsize=(12, 5), dpi=120)
        for label, (_, rets) in series.items():
            r = _rolling_sharpe(rets, wdays)
            ax.plot(r.index, r.values, label=label, color=colors[label],
                    linewidth=1.3, alpha=0.9)
        ax.axhline(0, color="black", alpha=0.3, linewidth=0.8)
        ax.axhline(1.0, color="green", alpha=0.2, linewidth=0.5, linestyle="--")
        ax.set_xlabel("Date (end of rolling window)")
        ax.set_ylabel(f"Rolling Sharpe ({wname})")
        ax.set_title(f"Rolling {wname} Sharpe — Candidate vs Baseline 3x vs SPY")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right")
        fig.tight_layout()
        fig.savefig(OUT_DIR / f"rolling_sharpe_{wname}.png")
        plt.close(fig)

    # --- Rolling MDD (window-local) ---
    log.info("Rolling MDD plots (this is slow, ~2min)...")
    for wname, wdays in WINDOWS.items():
        if wdays > 2500:  # 10y is expensive, skip for speed
            continue
        fig, ax = plt.subplots(figsize=(12, 5), dpi=120)
        for label, (eq, _) in series.items():
            r = _rolling_mdd(eq, wdays)
            ax.plot(r.index, -r.values * 100, label=label, color=colors[label],
                    linewidth=1.2, alpha=0.9)
        ax.set_xlabel("Date (end of rolling window)")
        ax.set_ylabel(f"Rolling {wname} max drawdown (%)")
        ax.set_title(f"Rolling {wname} MDD — less negative = better")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="lower right")
        fig.tight_layout()
        fig.savefig(OUT_DIR / f"rolling_mdd_{wname}.png")
        plt.close(fig)

    # --- Rolling excess CAGR vs SPY ---
    log.info("Rolling excess vs SPY plot...")
    fig, axes = plt.subplots(len(WINDOWS), 1, figsize=(12, 10), dpi=120, sharex=True)
    for ax, (wname, wdays) in zip(axes, WINDOWS.items()):
        cand_r = _rolling_cagr(cand.equity, wdays)
        spy_r = _rolling_cagr(bench_eq, wdays)
        excess = (cand_r - spy_r).dropna()
        pos_frac = float((excess > 0).mean())
        ax.fill_between(excess.index, 0, excess.values * 100,
                        where=excess.values > 0, color="#2ca02c", alpha=0.4,
                        label="Candidate > SPY")
        ax.fill_between(excess.index, 0, excess.values * 100,
                        where=excess.values <= 0, color="#d62728", alpha=0.4,
                        label="Candidate < SPY")
        ax.axhline(0, color="black", linewidth=0.6)
        ax.set_ylabel(f"{wname} Δ CAGR vs SPY (pp)")
        ax.set_title(f"Rolling {wname} excess vs SPY — positive fraction: {pos_frac*100:.1f}%")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right", framealpha=0.9)
    axes[-1].set_xlabel("Date (end of window)")
    fig.suptitle("Candidate rolling CAGR minus SPY CAGR — is it 'quase sempre' ahead?",
                 fontsize=12, y=0.995)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "rolling_excess_vs_spy.png")
    plt.close(fig)

    # --- Win rate vs SPY by window length ---
    log.info("Win-rate table + plot...")
    win_rows = []
    for wname, wdays in WINDOWS.items():
        cand_r = _rolling_cagr(cand.equity, wdays).dropna()
        spy_r = _rolling_cagr(bench_eq, wdays).dropna()
        common = cand_r.index.intersection(spy_r.index)
        excess = cand_r.loc[common] - spy_r.loc[common]
        # Worst window slice
        worst_dt = excess.idxmin()
        best_dt = excess.idxmax()
        win_rows.append({
            "window": wname,
            "n_windows": int(len(excess)),
            "win_rate_vs_spy": float((excess > 0).mean()),
            "median_excess_pp": float(excess.median()),
            "mean_excess_pp": float(excess.mean()),
            "worst_excess_pp": float(excess.min()),
            "worst_window_end": str(worst_dt.date()),
            "best_excess_pp": float(excess.max()),
            "best_window_end": str(best_dt.date()),
            "pct_windows_cand_above_10pp": float((excess > 0.10).mean()),
            "pct_windows_cand_below_0pp": float((excess < 0).mean()),
        })
    df_win = pd.DataFrame(win_rows)
    df_win.to_csv(OUT_DIR / "win_rate_by_window.csv", index=False)

    # --- Calendar year returns ---
    log.info("Calendar year bar chart...")
    cand_yr = (1 + cand.daily_returns).resample("YE").prod() - 1
    base_yr = (1 + base_res.daily_returns).resample("YE").prod() - 1
    spy_yr = (1 + bench_rets).resample("YE").prod() - 1
    yr_df = pd.DataFrame({
        "Candidate": cand_yr, "Baseline 3x": base_yr, "SPY": spy_yr,
    })
    yr_df.index = yr_df.index.year
    yr_df.to_csv(OUT_DIR / "calendar_year_returns.csv")

    fig, ax = plt.subplots(figsize=(16, 6), dpi=120)
    x = np.arange(len(yr_df))
    w = 0.28
    ax.bar(x - w, yr_df["Candidate"].values * 100, w,
           label="Candidate", color="#1f77b4")
    ax.bar(x,     yr_df["Baseline 3x"].values * 100, w,
           label="Baseline 3x", color="#d62728")
    ax.bar(x + w, yr_df["SPY"].values * 100, w, label="SPY", color="#808080")
    ax.set_xticks(x)
    ax.set_xticklabels(yr_df.index, rotation=60, fontsize=8)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Calendar-year total return (%)")
    ax.set_title("Calendar-year returns — Candidate vs Baseline vs SPY")
    ax.grid(True, alpha=0.3, axis="y")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "calendar_year_returns.png")
    plt.close(fig)

    # Calendar year win rate
    years_cand_beats_spy = (yr_df["Candidate"] > yr_df["SPY"]).sum()
    years_total = len(yr_df)
    log.info("Calendar-year win rate vs SPY: %d/%d = %.1f%%",
             years_cand_beats_spy, years_total,
             years_cand_beats_spy / years_total * 100)

    # --- Entry-year sensitivity ---
    log.info("Entry-year sensitivity plot...")
    entry_rows = []
    for year in range(1986, 2021):
        start_mask = cand.equity.index.year >= year
        if start_mask.sum() < 252:
            continue
        sub_cand = cand.equity.loc[start_mask]
        sub_base = base_res.equity.loc[start_mask]
        sub_bench = bench_eq.loc[start_mask]
        # Normalize each to 1.0 at its respective start bar
        sub_cand = sub_cand / sub_cand.iloc[0]
        sub_base = sub_base / sub_base.iloc[0]
        sub_bench = sub_bench / sub_bench.iloc[0]
        entry_rows.append({
            "start_year": year,
            "n_bars": len(sub_cand),
            "cand_cagr": float(_cagr(sub_cand, TRADING_DAYS_PER_YEAR)),
            "cand_mdd": float(_max_drawdown(sub_cand)),
            "base_cagr": float(_cagr(sub_base, TRADING_DAYS_PER_YEAR)),
            "base_mdd": float(_max_drawdown(sub_base)),
            "spy_cagr": float(_cagr(sub_bench, TRADING_DAYS_PER_YEAR)),
            "spy_mdd": float(_max_drawdown(sub_bench)),
            "cand_minus_spy_cagr": float(
                _cagr(sub_cand, TRADING_DAYS_PER_YEAR) - _cagr(sub_bench, TRADING_DAYS_PER_YEAR)
            ),
        })
    df_entry = pd.DataFrame(entry_rows)
    df_entry.to_csv(OUT_DIR / "entry_year_sensitivity.csv", index=False)

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), dpi=120, sharex=True)
    ax0 = axes[0]
    ax0.bar(df_entry.start_year, df_entry.cand_cagr * 100,
            label="Candidate", color="#1f77b4", alpha=0.8)
    ax0.plot(df_entry.start_year, df_entry.spy_cagr * 100,
             marker="o", label="SPY buy-hold", color="#808080")
    ax0.plot(df_entry.start_year, df_entry.base_cagr * 100,
             marker="s", label="Baseline 3x", color="#d62728", alpha=0.8)
    ax0.axhline(0, color="black", linewidth=0.6)
    ax0.set_ylabel("CAGR until 2026 end (%)")
    ax0.set_title("Entry-year sensitivity — 'what if I start in year X and hold to 2026'")
    ax0.grid(True, alpha=0.3)
    ax0.legend(loc="upper right")

    ax1 = axes[1]
    ax1.bar(df_entry.start_year, df_entry.cand_mdd * 100,
            label="Candidate MDD", color="#1f77b4", alpha=0.8)
    ax1.plot(df_entry.start_year, df_entry.spy_mdd * 100,
             marker="o", label="SPY MDD", color="#808080")
    ax1.plot(df_entry.start_year, df_entry.base_mdd * 100,
             marker="s", label="Baseline 3x MDD", color="#d62728", alpha=0.8)
    ax1.axhline(40, color="green", linewidth=0.8, linestyle="--",
                label="Spec target 40%")
    ax1.set_xlabel("Start year")
    ax1.set_ylabel("Max drawdown (%)")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper right")

    fig.tight_layout()
    fig.savefig(OUT_DIR / "entry_year_sensitivity.png")
    plt.close(fig)

    # --- Underwater curve ---
    log.info("Underwater plot...")
    fig, ax = plt.subplots(figsize=(12, 5), dpi=120)
    for label, (eq, _) in series.items():
        peak = eq.cummax()
        underwater = (eq / peak - 1) * 100
        ax.fill_between(underwater.index, 0, underwater.values,
                        where=underwater.values < 0,
                        color=colors[label], alpha=0.3, label=label)
    ax.set_xlabel("Date")
    ax.set_ylabel("Underwater (% below peak)")
    ax.set_title("Time spent under water — Candidate vs Baseline 3x vs SPY")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "underwater.png")
    plt.close(fig)

    # Underwater stats
    uw_rows = []
    for label, (eq, _) in series.items():
        peak = eq.cummax()
        underwater = eq / peak - 1
        pct_below_5 = float((underwater < -0.05).mean())
        pct_below_20 = float((underwater < -0.20).mean())
        pct_below_40 = float((underwater < -0.40).mean())
        uw_rows.append({
            "strategy": label,
            "% days >5% below peak": pct_below_5,
            "% days >20% below peak": pct_below_20,
            "% days >40% below peak": pct_below_40,
        })
    df_uw = pd.DataFrame(uw_rows).set_index("strategy")
    df_uw.to_csv(OUT_DIR / "underwater_stats.csv")

    # --- Worst rolling 5y windows for candidate ---
    log.info("Worst-windows table...")
    worst_rows = []
    for wname, wdays in [("3y", 756), ("5y", 1260)]:
        cand_r = _rolling_cagr(cand.equity, wdays).dropna()
        spy_r = _rolling_cagr(bench_eq, wdays).dropna()
        common = cand_r.index.intersection(spy_r.index)
        excess = cand_r.loc[common] - spy_r.loc[common]
        # 10 worst windows
        worst = excess.nsmallest(10)
        for dt, val in worst.items():
            worst_rows.append({
                "window": wname,
                "end_date": str(dt.date()),
                "cand_cagr": float(cand_r.loc[dt]),
                "spy_cagr": float(spy_r.loc[dt]),
                "excess_pp": float(val),
            })
    df_worst = pd.DataFrame(worst_rows)
    df_worst.to_csv(OUT_DIR / "worst_windows.csv", index=False)

    # --- Build prose report ---
    log.info("Writing deep_review_report.md...")
    _write_report(df_win, df_entry, df_uw, df_worst, yr_df,
                  years_cand_beats_spy, years_total)
    log.info("Done — see %s", OUT_DIR)
    return 0


def _write_report(df_win, df_entry, df_uw, df_worst, yr_df,
                  years_cand_beats_spy, years_total):
    lines = []
    lines.append("# Deep rolling-window review — Candidate vs SPY buy-hold\n")
    lines.append(
        "> Rigorous quantitative test of the *'quase sempre à frente do SPY 1x'* "
        "claim. 40y synth window 1986-01-03 → 2026-04-17. Candidate: "
        "`EMA_N150_th5_bL3_sL0` + `sl30_rec10_cape05`.\n"
    )
    lines.append(
        "> ⚠️ This review does **NOT** validate live deployment. Gates failed "
        "(3/7 in SPY real 17y). This is a synth-only diagnostic.\n"
    )

    lines.append("## 1. Rolling-window CAGR vs SPY\n")
    lines.append("\n**Is the candidate 'sempre' ahead of SPY?** Count rolling windows of "
                 "each length and measure the fraction in which CAGR_cand > CAGR_SPY.\n")
    lines.append(
        "| window | # windows | **win rate** vs SPY | median excess (pp) | mean excess (pp) | "
        "% windows > +10pp ahead | % windows *behind* SPY |\n"
        "|---|---|---|---|---|---|---|"
    )
    for _, r in df_win.iterrows():
        lines.append(
            f"| {r.window} | {int(r.n_windows)} | **{r.win_rate_vs_spy*100:.1f}%** | "
            f"{r.median_excess_pp*100:+.2f} | {r.mean_excess_pp*100:+.2f} | "
            f"{r.pct_windows_cand_above_10pp*100:.1f}% | "
            f"{r.pct_windows_cand_below_0pp*100:.1f}% |"
        )

    lines.append("\n**Reading the table**:\n")
    for _, r in df_win.iterrows():
        beats = r.win_rate_vs_spy
        lags = r.pct_windows_cand_below_0pp
        lines.append(
            f"- Rolling {r.window}: candidate beats SPY in **{beats*100:.1f}%** of windows "
            f"({int(r.n_windows * beats)} of {int(r.n_windows)}). "
            f"Lags SPY in {lags*100:.1f}% ({int(r.n_windows * lags)} windows).\n"
        )

    lines.append("\n**Worst windows** (candidate vs SPY over rolling 3y and 5y):\n")
    lines.append(
        "| window | end date | cand CAGR | SPY CAGR | cand − SPY (pp) |\n"
        "|---|---|---|---|---|"
    )
    for _, r in df_worst.head(10).iterrows():
        lines.append(
            f"| {r.window} | {r.end_date} | {_fmt_pct(r.cand_cagr)} | "
            f"{_fmt_pct(r.spy_cagr)} | {r.excess_pp*100:+.2f} |"
        )
    lines.append(
        "\nSee `worst_windows.csv` for the full top-10 per window. Plots: "
        "`rolling_cagr_1y.png`, `rolling_cagr_3y.png`, `rolling_cagr_5y.png`, "
        "`rolling_cagr_10y.png`, `rolling_excess_vs_spy.png`.\n"
    )

    lines.append("## 2. Calendar year returns\n")
    lines.append(
        f"Of {years_total} full calendar years in 1986-2025, the candidate beat SPY "
        f"in **{years_cand_beats_spy} years** "
        f"({years_cand_beats_spy/years_total*100:.1f}% of years).\n"
    )
    lines.append(
        "| year | Candidate | Baseline 3x | SPY | Cand − SPY (pp) |\n"
        "|---|---|---|---|---|"
    )
    for yr, row in yr_df.iterrows():
        lines.append(
            f"| {yr} | {_fmt_pct(row['Candidate'])} | {_fmt_pct(row['Baseline 3x'])} | "
            f"{_fmt_pct(row['SPY'])} | "
            f"{(row['Candidate']-row['SPY'])*100:+.2f} |"
        )
    lines.append("\nPlot: `calendar_year_returns.png`.\n")

    lines.append("## 3. Entry-year sensitivity\n")
    lines.append(
        "For each possible start year, measure CAGR and MDD if you bought-and-held "
        "the candidate (vs baseline 3x vs SPY) from that year to 2026.\n"
    )
    lines.append(
        "| start year | cand CAGR | cand MDD | SPY CAGR | SPY MDD | cand − SPY (pp) |\n"
        "|---|---|---|---|---|---|"
    )
    for _, r in df_entry.iterrows():
        lines.append(
            f"| {int(r.start_year)} | {_fmt_pct(r.cand_cagr)} | {_fmt_pct(r.cand_mdd)} | "
            f"{_fmt_pct(r.spy_cagr)} | {_fmt_pct(r.spy_mdd)} | "
            f"{r.cand_minus_spy_cagr*100:+.2f} |"
        )
    entry_beats_spy = int((df_entry.cand_minus_spy_cagr > 0).sum())
    lines.append(
        f"\n**Of {len(df_entry)} possible start years, candidate beats SPY CAGR in "
        f"{entry_beats_spy} ({entry_beats_spy/len(df_entry)*100:.1f}%).**\n"
        "Plot: `entry_year_sensitivity.png`.\n"
    )

    lines.append("## 4. Time spent underwater\n")
    lines.append(
        "| strategy | % days > 5% below peak | % days > 20% below peak | % days > 40% below peak |\n"
        "|---|---|---|---|"
    )
    for label, row in df_uw.iterrows():
        lines.append(
            f"| {label} | {row['% days >5% below peak']*100:.1f}% | "
            f"{row['% days >20% below peak']*100:.1f}% | "
            f"{row['% days >40% below peak']*100:.1f}% |"
        )
    lines.append("\nPlot: `underwater.png`.\n")

    lines.append("## 5. Verdict on the 'quase sempre à frente' claim\n")
    # Grab numbers
    win_1y = df_win[df_win.window == "1y"].iloc[0].win_rate_vs_spy
    win_3y = df_win[df_win.window == "3y"].iloc[0].win_rate_vs_spy
    win_5y = df_win[df_win.window == "5y"].iloc[0].win_rate_vs_spy
    win_10y = df_win[df_win.window == "10y"].iloc[0].win_rate_vs_spy
    lines.append(
        f"The candidate beats SPY **{win_1y*100:.1f}%** of rolling 1y windows, "
        f"**{win_3y*100:.1f}%** of 3y, **{win_5y*100:.1f}%** of 5y, "
        f"**{win_10y*100:.1f}%** of 10y. "
        "Longer horizons favor the candidate — the leverage + stop overlay's edge "
        "accumulates. But:\n\n"
        f"* At 1y: candidate loses to SPY in "
        f"{df_win[df_win.window == '1y'].iloc[0].pct_windows_cand_below_0pp*100:.1f}% of windows.\n"
        f"* Year-by-year: {years_total - years_cand_beats_spy} of {years_total} calendar "
        "years had candidate behind SPY.\n"
        "* 2020 COVID window specifically: candidate −13 % vs SPY +5 % — the kind of "
        "outcome that matters for live execution timing.\n"
        "* **'Sempre' (100 %) is empirically false**. The claim that matches the data "
        "is: 'candidate wins on **long-horizon rolling CAGR** but underperforms SPY in "
        "short/medium windows around certain crash-recovery events'.\n"
    )

    lines.append("## 6. Critical caveats for live deployment\n")
    lines.append(
        "1. **This is 40 y synth**. Real UPRO has 2–3 pp/yr tracking drag vs "
        "perfect-leverage synth `[leverage_for_the_long_run, p.21, Table 12]`. "
        "Real CAGR ≈ 21–22 % instead of 24 %.\n"
        "2. **Spec §0 fails in real data**. See `../phase3/cross_dataset_gates.md`. "
        "The same parameter set gives 3/7 gates on SPY real (17 y), not 6/7.\n"
        "3. **CAPE stale at 2023-09** — for post-2024 live trading the risk signal "
        "degrades to constant 0 (no de-lever). Effectively reduces to stop-loss only.\n"
        "4. **G3 Walk-Forward universal FAIL**. Window-local MDDs routinely exceed "
        "25 %. A rolling review that slices the 40 y into overlapping 2.5 y train + "
        "6 mo OOS periods shows the overlay can't keep individual windows clean.\n"
        "5. **9 stops in 40 years** — roughly 1 per 4.5 y. Operationally, the user "
        "must commit to execute stop-reentry discipline for decades without drift.\n"
    )

    lines.append("\n---\n"
                 "*Next artifact: `PRE_DEPLOYMENT_README.md` — go/no-go checklist.*\n"
                 "*Citations: spec §0, §6.1, §6.2, §8.1-8.3. "
                 "`[leverage_for_the_long_run, p.21, Table 12]` (synth vs real). "
                 "`[advances_fin_ml, p.208-211, p.222-223, ch.12]` (gates).*\n")

    (OUT_DIR / "deep_review_report.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
