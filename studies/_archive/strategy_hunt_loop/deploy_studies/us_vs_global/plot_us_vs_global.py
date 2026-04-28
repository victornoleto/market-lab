"""Plots for US vs Global study."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = Path(__file__).resolve().parent

COLORS = {
    "SPY": "#d62728", "VT": "#1f77b4", "VEA": "#2ca02c",
    "VXUS": "#9467bd", "VBR": "#ff7f0e", "GDE": "goldenrod",
    "NTSX_synth": "#17becf",
}


def metrics_label(r: pd.Series, name: str) -> str:
    eq = (1 + r).cumprod()
    years = len(r) / 252
    cagr = eq.iloc[-1] ** (1 / years) - 1
    sharpe = np.sqrt(252) * r.mean() / r.std(ddof=1)
    mdd = (eq / eq.cummax() - 1).min()
    return f"{name}: Sharpe {sharpe:.2f} / CAGR {cagr*100:.1f}% / MDD {mdd*100:.0f}%"


def main() -> None:
    series = pd.read_parquet(OUT_DIR / "us_vs_global_returns.parquet")
    print(f"Loaded series: {series.index.min().date()} → {series.index.max().date()}")

    # Drop NaN before computing equity
    common = series.dropna().index

    # === Figure 1: Equity curves SPY vs VT vs VEA over full window ===
    fig, ax = plt.subplots(figsize=(13, 7))
    for col in ["SPY", "VT", "VEA", "VXUS", "VBR"]:
        r = series[col].dropna()
        eq = (1 + r).cumprod()
        ax.plot(eq.index, eq.values, color=COLORS[col], linewidth=1.4,
                label=metrics_label(r, col), alpha=0.85)
    ax.set_yscale("log")
    ax.set_title("US vs Global equity — long-window (testfolio synth)", fontsize=12, weight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Equity (log scale, $1 → ...)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "US_VS_GLOBAL_equity.png", dpi=110)
    plt.close(fig)
    print("Wrote US_VS_GLOBAL_equity.png")

    # === Figure 2: Rolling 20y CAGR comparison ===
    def rolling_20y(r: pd.Series) -> pd.Series:
        win = 20 * 252
        if len(r) < win:
            return pd.Series(dtype=float)
        out = []
        idx = r.index[win - 1:]
        arr = r.values
        for i in range(len(idx)):
            seg = arr[i:i + win]
            eq = (1 + seg).cumprod()
            out.append(eq[-1] ** (1 / 20) - 1)
        return pd.Series(out, index=idx[:len(out)])

    fig, ax = plt.subplots(figsize=(13, 6))
    for col in ["SPY", "VT", "VEA", "VBR"]:
        r = series[col].dropna()
        rcg = rolling_20y(r) * 100
        if not rcg.empty:
            ax.plot(rcg.index, rcg.values, color=COLORS[col], linewidth=1.4,
                    label=f"{col} (mean {rcg.mean():.1f}%)", alpha=0.85)
    ax.axhline(5, color="gray", linewidth=0.7, linestyle="--", alpha=0.6,
               label="5% real CAGR floor")
    ax.set_title("Rolling 20-year CAGR — US vs Global", fontsize=12, weight="bold")
    ax.set_ylabel("20-year CAGR %")
    ax.legend(loc="lower left", fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "US_VS_GLOBAL_rolling_20y.png", dpi=110)
    plt.close(fig)
    print("Wrote US_VS_GLOBAL_rolling_20y.png")

    # === Figure 3: 2000-2013 "Lost decade" zoom ===
    fig, ax = plt.subplots(figsize=(13, 6))
    for col in ["SPY", "VT", "VEA"]:
        r = series[col].dropna().loc["2000-01-01":"2013-12-31"]
        eq = (1 + r).cumprod()
        eq = eq / eq.iloc[0]
        cagr = eq.iloc[-1] ** (1 / (len(r) / 252)) - 1
        ax.plot(eq.index, eq.values, color=COLORS[col], linewidth=1.6,
                label=f"{col} (CAGR {cagr*100:+.1f}%)", alpha=0.85)
    ax.axhline(1.0, color="black", linewidth=0.5, alpha=0.7)
    ax.set_title("US 'Lost Decade' 2000-2013 — Did global diversification help?",
                 fontsize=12, weight="bold")
    ax.set_ylabel("Equity (Jan 2000 = $1)")
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "US_VS_GLOBAL_lost_decade.png", dpi=110)
    plt.close(fig)
    print("Wrote US_VS_GLOBAL_lost_decade.png")

    # === Figure 4: Histogram of rolling 20y CAGR (where each strategy ends up) ===
    fig, ax = plt.subplots(figsize=(13, 6))
    bins = np.arange(0, 18, 0.5)
    for col in ["SPY", "VT", "VEA", "VBR"]:
        r = series[col].dropna()
        rcg = rolling_20y(r) * 100
        if not rcg.empty:
            ax.hist(rcg.values, bins=bins, color=COLORS[col], alpha=0.5,
                    label=f"{col} (n={len(rcg)})", edgecolor="black", linewidth=0.5)
    ax.axvline(5, color="red", linewidth=1, linestyle="--", alpha=0.7,
               label="5% real CAGR floor")
    ax.set_title("Distribution of rolling 20-year CAGRs (1986-2026)",
                 fontsize=12, weight="bold")
    ax.set_xlabel("20-year CAGR %")
    ax.set_ylabel("Frequency (windows)")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "US_VS_GLOBAL_distribution.png", dpi=110)
    plt.close(fig)
    print("Wrote US_VS_GLOBAL_distribution.png")

    # === Figure 5: 5-way comparison NTSX/B/SPY/VT/GDE ===
    df = pd.read_parquet(ROOT / "data/testfolio/cache/history.parquet")
    df.index = pd.to_datetime(df.index)
    r_spy = df["SPYSIM"].pct_change().dropna()
    r_ief = df["IEFSIM"].pct_change().dropna()
    r_cash = df["CASHX"].pct_change().dropna()
    r_vt = df["VTSIM"].pct_change().dropna()
    r_gde = df["GDESIM"].pct_change().dropna()
    idx = r_spy.index.intersection(r_ief.index).intersection(r_cash.index) \
                    .intersection(r_vt.index).intersection(r_gde.index)
    r_spy, r_ief, r_cash, r_vt, r_gde = [r.reindex(idx) for r in
                                           [r_spy, r_ief, r_cash, r_vt, r_gde]]
    strategies = {
        "A_NTSX_synth": (0.90 * r_spy + 0.60 * r_ief - 0.50 * r_cash, "#17becf"),
        "B_NTSX+GDE_blend": (0.594 * r_spy + 0.396 * r_ief - 0.33 * r_cash + 0.34 * r_gde, "#2ca02c"),
        "C_SPY_100%": (r_spy, "#d62728"),
        "D_VT_global": (r_vt, "#1f77b4"),
        "E_GDE_100%": (r_gde, "goldenrod"),
    }
    fig, ax = plt.subplots(figsize=(13, 7))
    for name, (r, color) in strategies.items():
        eq = (1 + r).cumprod()
        ax.plot(eq.index, eq.values, color=color, linewidth=1.4,
                label=metrics_label(r, name), alpha=0.85)
    ax.set_yscale("log")
    ax.set_title("5-way comparison: NTSX vs NTSX+GDE vs SPY vs VT vs GDE — 40y synth",
                 fontsize=12, weight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Equity (log scale)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "US_VS_GLOBAL_5way.png", dpi=110)
    plt.close(fig)
    print("Wrote US_VS_GLOBAL_5way.png")


if __name__ == "__main__":
    main()
