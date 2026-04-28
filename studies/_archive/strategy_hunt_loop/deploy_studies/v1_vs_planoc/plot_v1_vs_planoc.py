"""Plot V1 NTSX+GDE vs Plano C V3_1 — comparison visualizations."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = Path(__file__).resolve().parent

COLORS = {"V1": "#2ca02c", "V3_1": "#d62728", "SPY": "black"}
LABELS = {"V1": "V1 NTSX+GDE 67/33", "V3_1": "Plano C V3_1 v3.5",
          "SPY": "SPYSIM b&h"}


def main() -> None:
    series = pd.read_parquet(OUT_DIR / "v1_vs_planoc_returns.parquet")
    r5_v1 = pd.read_parquet(OUT_DIR / "rolling_5y_v1.parquet")
    r5_v3 = pd.read_parquet(OUT_DIR / "rolling_5y_v3.parquet")
    r10_v1 = pd.read_parquet(OUT_DIR / "rolling_10y_v1.parquet")
    r10_v3 = pd.read_parquet(OUT_DIR / "rolling_10y_v3.parquet")

    # === Figure 1: Equity curves log scale ===
    fig, ax = plt.subplots(figsize=(13, 7))
    for col, key in [("V1_NTSX_GDE_67_33", "V1"), ("V3_1_PlanoC", "V3_1"),
                      ("SPYSIM_bench", "SPY")]:
        eq = (1 + series[col]).cumprod()
        ax.plot(eq.index, eq.values, color=COLORS[key], linewidth=1.4,
                label=f"{LABELS[key]} (final ${eq.iloc[-1]:.1f})", alpha=0.85)
    ax.set_yscale("log")
    ax.set_title("V1 NTSX+GDE 67/33 vs Plano C V3_1 v3.5 vs SPY — 32y synth (1994-2026)",
                 fontsize=12, weight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Equity (log scale, $1 → ...)")
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "V1_VS_PLANOC_equity.png", dpi=110)
    plt.close(fig)
    print("Wrote V1_VS_PLANOC_equity.png")

    # === Figure 2: Drawdowns ===
    fig, ax = plt.subplots(figsize=(13, 6))
    for col, key in [("V1_NTSX_GDE_67_33", "V1"), ("V3_1_PlanoC", "V3_1"),
                      ("SPYSIM_bench", "SPY")]:
        eq = (1 + series[col]).cumprod()
        dd = (eq / eq.cummax() - 1) * 100
        ax.plot(dd.index, dd.values, color=COLORS[key], linewidth=1.0,
                label=LABELS[key], alpha=0.8)
    ax.axhline(-25, color="orange", linewidth=0.8, linestyle=":", alpha=0.6,
               label="−25%")
    ax.axhline(-50, color="red", linewidth=0.8, linestyle=":", alpha=0.6,
               label="−50%")
    ax.set_title("Drawdowns — V1 vs Plano C V3_1 vs SPY, 32y synth", fontsize=12, weight="bold")
    ax.set_ylabel("Drawdown %")
    ax.legend(loc="lower left", fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "V1_VS_PLANOC_drawdowns.png", dpi=110)
    plt.close(fig)
    print("Wrote V1_VS_PLANOC_drawdowns.png")

    # === Figure 3: Rolling 5y Sharpe ===
    fig, ax = plt.subplots(figsize=(13, 5))
    ax.plot(r5_v1.index, r5_v1["sharpe"], color=COLORS["V1"], linewidth=1.0,
            label=f"V1 (mean {r5_v1['sharpe'].mean():.2f})", alpha=0.85)
    ax.plot(r5_v3.index, r5_v3["sharpe"], color=COLORS["V3_1"], linewidth=1.0,
            label=f"V3_1 Plano C (mean {r5_v3['sharpe'].mean():.2f})", alpha=0.85)
    ax.axhline(0, color="gray", linewidth=0.5)
    ax.fill_between(r5_v1.index,
                    r5_v1["sharpe"].values, r5_v3["sharpe"].values,
                    where=(r5_v1["sharpe"].values > r5_v3["sharpe"].values),
                    alpha=0.15, color=COLORS["V1"], label="V1 better")
    ax.fill_between(r5_v1.index,
                    r5_v1["sharpe"].values, r5_v3["sharpe"].values,
                    where=(r5_v1["sharpe"].values < r5_v3["sharpe"].values),
                    alpha=0.15, color=COLORS["V3_1"], label="V3_1 better")
    ax.set_title("Rolling 5y Sharpe ratio — V1 vs Plano C V3_1", fontsize=12, weight="bold")
    ax.set_ylabel("Sharpe (5y rolling)")
    ax.legend(loc="lower right", fontsize=9, ncol=2)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "V1_VS_PLANOC_rolling_5y_sharpe.png", dpi=110)
    plt.close(fig)
    print("Wrote V1_VS_PLANOC_rolling_5y_sharpe.png")

    # === Figure 4: Rolling 10y CAGR ===
    fig, ax = plt.subplots(figsize=(13, 5))
    ax.plot(r10_v1.index, r10_v1["cagr"] * 100, color=COLORS["V1"], linewidth=1.2,
            label=f"V1 (mean {r10_v1['cagr'].mean()*100:.1f}%)", alpha=0.85)
    ax.plot(r10_v3.index, r10_v3["cagr"] * 100, color=COLORS["V3_1"], linewidth=1.2,
            label=f"V3_1 Plano C (mean {r10_v3['cagr'].mean()*100:.1f}%)", alpha=0.85)
    ax.axhline(11, color="gray", linewidth=0.7, linestyle=":", alpha=0.6,
               label="CDI/SPY ~11%")
    ax.set_title("Rolling 10y CAGR — V1 vs Plano C V3_1", fontsize=12, weight="bold")
    ax.set_ylabel("CAGR % (10y rolling)")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "V1_VS_PLANOC_rolling_10y_cagr.png", dpi=110)
    plt.close(fig)
    print("Wrote V1_VS_PLANOC_rolling_10y_cagr.png")

    # === Figure 5: Yearly returns bars ===
    yr_v1 = series["V1_NTSX_GDE_67_33"].groupby(series.index.year).apply(
        lambda x: (1 + x).prod() - 1) * 100
    yr_v3 = series["V3_1_PlanoC"].groupby(series.index.year).apply(
        lambda x: (1 + x).prod() - 1) * 100
    yr_spy = series["SPYSIM_bench"].groupby(series.index.year).apply(
        lambda x: (1 + x).prod() - 1) * 100

    years = yr_v1.index
    width = 0.27
    x = np.arange(len(years))
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.bar(x - width, yr_v1.values, width, color=COLORS["V1"], label=LABELS["V1"], alpha=0.85)
    ax.bar(x, yr_v3.values, width, color=COLORS["V3_1"], label=LABELS["V3_1"], alpha=0.85)
    ax.bar(x + width, yr_spy.values, width, color=COLORS["SPY"], label=LABELS["SPY"], alpha=0.55)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(years, rotation=45, fontsize=8)
    ax.set_title("Yearly returns — V1 vs V3_1 vs SPY, 1994-2026", fontsize=12, weight="bold")
    ax.set_ylabel("Annual return %")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "V1_VS_PLANOC_yearly.png", dpi=110)
    plt.close(fig)
    print("Wrote V1_VS_PLANOC_yearly.png")

    # === Figure 6: 2008 + 2022 stress side-by-side ===
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    for ax, (start, end, title) in zip(axes, [
        ("2007-10-01", "2009-09-30", "2008 GFC + recovery"),
        ("2021-12-31", "2024-12-31", "2022 rate cycle"),
    ]):
        for col, key in [("V1_NTSX_GDE_67_33", "V1"), ("V3_1_PlanoC", "V3_1"),
                          ("SPYSIM_bench", "SPY")]:
            r = series[col].loc[start:end]
            if len(r) == 0:
                continue
            eq = (1 + r).cumprod()
            eq = eq / eq.iloc[0]
            ax.plot(eq.index, eq.values, color=COLORS[key], linewidth=1.5,
                    label=LABELS[key], alpha=0.85)
        ax.axhline(1.0, color="black", linewidth=0.5)
        ax.set_title(title, fontsize=11, weight="bold")
        ax.set_ylabel("Equity (start = $1)")
        ax.legend(loc="best", fontsize=9)
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "V1_VS_PLANOC_stress.png", dpi=110)
    plt.close(fig)
    print("Wrote V1_VS_PLANOC_stress.png")


if __name__ == "__main__":
    main()
