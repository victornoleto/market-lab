"""Plots for the 8-way LETF portfolio comparison (Reddit follow-up post)."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = Path(__file__).resolve().parent
TRADING_DAYS = 252

COLORS = {
    "P1_SPY_100":                  "#7f7f7f",   # gray
    "P2_NTSX":                     "#1f77b4",   # blue
    "P3_NTSX_GDE_blend":           "#2ca02c",   # green (incumbent)
    "P4_GDE_100":                  "goldenrod", # gold
    "P5_SSO_ZROZ_GLD":             "#d62728",   # red
    "P6_NTSX_GDE_KMLM_50_35_15":   "#ff7f0e",   # orange (conservative MF)
    "P7_NTSX_GDE_KMLM_40_35_25":   "#9467bd",   # purple (aggressive MF)
    "P8_RSSB_GDE_KMLM_50_30_20":   "#8c564b",   # brown (RSSB stack)
}
LABELS = {
    "P1_SPY_100":                  "SPY 100%",
    "P2_NTSX":                     "NTSX (1.5x SPY/IEF)",
    "P3_NTSX_GDE_blend":           "NTSX+GDE blend",
    "P4_GDE_100":                  "GDE 100%",
    "P5_SSO_ZROZ_GLD":             "SSO/ZROZ/GLD 50/25/25",
    "P6_NTSX_GDE_KMLM_50_35_15":   "NTSX+GDE+KMLM 50/35/15",
    "P7_NTSX_GDE_KMLM_40_35_25":   "NTSX+GDE+KMLM 40/35/25",
    "P8_RSSB_GDE_KMLM_50_30_20":   "RSSB+GDE+KMLM 50/30/20",
}


def metrics_str(r: pd.Series) -> str:
    eq = (1 + r).cumprod()
    years = len(r) / TRADING_DAYS
    cagr = eq.iloc[-1] ** (1 / years) - 1
    sharpe = np.sqrt(TRADING_DAYS) * r.mean() / r.std(ddof=1)
    mdd = (eq / eq.cummax() - 1).min()
    return f"Sh {sharpe:.2f} / CAGR {cagr*100:.1f}% / MDD {mdd*100:.0f}%"


def rolling_cagr(r: pd.Series, win_y: int) -> pd.Series:
    win = win_y * TRADING_DAYS
    if len(r) < win:
        return pd.Series(dtype=float)
    out, idx = [], r.index[win - 1:]
    arr = r.values
    for i in range(len(idx)):
        seg = arr[i:i + win]
        eq = (1 + seg).cumprod()
        out.append(eq[-1] ** (1 / win_y) - 1)
    return pd.Series(out, index=idx[:len(out)])


def rolling_sharpe(r: pd.Series, win_y: int) -> pd.Series:
    win = win_y * TRADING_DAYS
    if len(r) < win:
        return pd.Series(dtype=float)
    out, idx = [], r.index[win - 1:]
    arr = r.values
    for i in range(len(idx)):
        seg = arr[i:i + win]
        sd = seg.std(ddof=1)
        out.append(np.sqrt(TRADING_DAYS) * seg.mean() / sd if sd > 0 else np.nan)
    return pd.Series(out, index=idx[:len(out)])


def main() -> None:
    series = pd.read_parquet(OUT_DIR / "letfs_8way_returns.parquet")
    print(f"Window: {series.index.min().date()} → {series.index.max().date()}")
    yspan = f"{series.index.min().year}-{series.index.max().year}"
    n_years = (series.index.max() - series.index.min()).days / 365.25

    # === Figure 1: Equity log scale ===
    fig, ax = plt.subplots(figsize=(13, 7.5))
    for col in series.columns:
        eq = (1 + series[col]).cumprod()
        ax.plot(eq.index, eq.values, color=COLORS[col], linewidth=1.5,
                label=f"{LABELS[col]}: {metrics_str(series[col])}", alpha=0.92)
    ax.set_yscale("log")
    ax.set_title(f"Equity, $1 → ... — {yspan} (testfolio synth, {n_years:.1f}y)",
                 fontsize=12, weight="bold")
    ax.set_ylabel("Equity (log scale)")
    ax.set_xlabel("Year")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "LETFS_8WAY_equity.png", dpi=110)
    plt.close(fig)
    print("Wrote LETFS_8WAY_equity.png")

    # === Figure 2: Drawdowns ===
    fig, ax = plt.subplots(figsize=(13, 6))
    for col in series.columns:
        eq = (1 + series[col]).cumprod()
        dd = (eq / eq.cummax() - 1) * 100
        ax.plot(dd.index, dd.values, color=COLORS[col], linewidth=1.0,
                label=LABELS[col], alpha=0.85)
    ax.axhline(-25, color="orange", linewidth=0.7, linestyle=":", alpha=0.6)
    ax.axhline(-50, color="red", linewidth=0.7, linestyle=":", alpha=0.6)
    ax.set_title(f"Drawdowns from peak — {yspan}", fontsize=12, weight="bold")
    ax.set_ylabel("Drawdown %")
    ax.set_xlabel("Year")
    ax.legend(loc="lower left", fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "LETFS_8WAY_drawdowns.png", dpi=110)
    plt.close(fig)
    print("Wrote LETFS_8WAY_drawdowns.png")

    # === Figure 3: Rolling 10y CAGR ===
    fig, ax = plt.subplots(figsize=(13, 6.5))
    for col in series.columns:
        rcg = rolling_cagr(series[col], 10) * 100
        if rcg.empty:
            continue
        ax.plot(rcg.index, rcg.values, color=COLORS[col], linewidth=1.4,
                label=f"{LABELS[col]} (mean {rcg.mean():.1f}%, min {rcg.min():.1f}%)",
                alpha=0.9)
    ax.axhline(5, color="gray", linewidth=0.7, linestyle="--", alpha=0.6,
               label="5% line")
    ax.axhline(0, color="red", linewidth=0.5, alpha=0.5)
    ax.set_title('Rolling 10y CAGR — "what would my last 10y have looked like?"',
                 fontsize=12, weight="bold")
    ax.set_ylabel("Trailing 10y CAGR %")
    ax.set_xlabel("End of window")
    ax.legend(loc="lower left", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "LETFS_8WAY_rolling10y.png", dpi=110)
    plt.close(fig)
    print("Wrote LETFS_8WAY_rolling10y.png")

    # === Figure 4: Rolling 5y Sharpe ===
    fig, ax = plt.subplots(figsize=(13, 6.5))
    for col in series.columns:
        rs = rolling_sharpe(series[col], 5)
        if rs.empty:
            continue
        ax.plot(rs.index, rs.values, color=COLORS[col], linewidth=1.3,
                label=f"{LABELS[col]} (mean {rs.mean():.2f})", alpha=0.9)
    ax.axhline(0.5, color="orange", linewidth=0.6, linestyle="--", alpha=0.6)
    ax.axhline(1.0, color="green", linewidth=0.6, linestyle="--", alpha=0.6)
    ax.axhline(0, color="red", linewidth=0.5, alpha=0.5)
    ax.set_title("Rolling 5y Sharpe — risk-adjusted consistency",
                 fontsize=12, weight="bold")
    ax.set_ylabel("Trailing 5y Sharpe")
    ax.set_xlabel("End of window")
    ax.legend(loc="lower left", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "LETFS_8WAY_rolling5y_sharpe.png", dpi=110)
    plt.close(fig)
    print("Wrote LETFS_8WAY_rolling5y_sharpe.png")

    # === Figure 5: Rolling 20y CAGR distribution ===
    fig, ax = plt.subplots(figsize=(13, 6.5))
    bins = np.arange(4, 17, 0.4)
    for col in series.columns:
        rcg = rolling_cagr(series[col], 20) * 100
        if rcg.empty:
            continue
        ax.hist(rcg.values, bins=bins, color=COLORS[col], alpha=0.40,
                label=f"{LABELS[col]} (mean {rcg.mean():.1f}%, min {rcg.min():.1f}%)",
                edgecolor="black", linewidth=0.4)
    ax.set_title("Rolling 20y CAGR distribution",
                 fontsize=12, weight="bold")
    ax.set_xlabel("20y CAGR %")
    ax.set_ylabel("Number of windows")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "LETFS_8WAY_rolling20y_hist.png", dpi=110)
    plt.close(fig)
    print("Wrote LETFS_8WAY_rolling20y_hist.png")

    # === Figure 6: Stress 4-panel ===
    stress = [
        ("2000-03-24", "2003-03-31", "Dot-com bear (2000-03 → 2003-03)"),
        ("2007-10-09", "2010-03-31", "GFC + recovery (2007-10 → 2010-03)"),
        ("2020-02-19", "2020-12-31", "COVID crash + bounce (2020)"),
        ("2022-01-01", "2023-12-31", "2022 rate cycle (2022-2023)"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(15.5, 10.5))
    for ax, (s, e, title) in zip(axes.flat, stress):
        for col in series.columns:
            r = series[col].loc[s:e]
            if len(r) == 0:
                continue
            eq = (1 + r).cumprod()
            eq = eq / eq.iloc[0]
            cagr = eq.iloc[-1] ** (1 / max(len(r) / TRADING_DAYS, 1e-9)) - 1
            mdd = (eq / eq.cummax() - 1).min()
            ax.plot(eq.index, eq.values, color=COLORS[col], linewidth=1.5,
                    label=f"{LABELS[col]}: CAGR {cagr*100:+.1f}% / MDD {mdd*100:.0f}%",
                    alpha=0.92)
        ax.axhline(1.0, color="black", linewidth=0.5, alpha=0.7)
        ax.set_title(title, fontsize=11, weight="bold")
        ax.set_ylabel("Equity (start = $1)")
        ax.legend(loc="best", fontsize=7)
        ax.grid(True, alpha=0.3)
    fig.suptitle("Stress periods — 8-way LETF portfolio comparison",
                 fontsize=13, weight="bold", y=1.00)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "LETFS_8WAY_stress.png", dpi=110)
    plt.close(fig)
    print("Wrote LETFS_8WAY_stress.png")


if __name__ == "__main__":
    main()
