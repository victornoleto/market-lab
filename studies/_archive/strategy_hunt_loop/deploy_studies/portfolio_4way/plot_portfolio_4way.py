"""4-way portfolio comparison plots."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = Path(__file__).resolve().parent

COLORS = {
    "V1_NTSX_GDE_67_33": "#2ca02c",
    "V3_1_PlanoC_v3.5": "#d62728",
    "V_HYBRID_NTSX_replaces_AVUS": "#1f77b4",
    "V_HYBRID_SIMPLE_AVNM_proxy": "#9467bd",
}
LABELS = {
    "V1_NTSX_GDE_67_33": "V1 NTSX+GDE 67/33 (2 ETFs)",
    "V3_1_PlanoC_v3.5": "V3_1 Plano C v3.5 (11 ETFs)",
    "V_HYBRID_NTSX_replaces_AVUS": "V_HYBRID (V3_1 + NTSX, 11 ETFs)",
    "V_HYBRID_SIMPLE_AVNM_proxy": "V_HYBRID_SIMPLE (AVNM, 9 ETFs)",
}


def metrics_str(r: pd.Series) -> str:
    eq = (1 + r).cumprod()
    years = len(r) / 252
    cagr = eq.iloc[-1] ** (1 / years) - 1
    sharpe = np.sqrt(252) * r.mean() / r.std(ddof=1)
    mdd = (eq / eq.cummax() - 1).min()
    return f"Sh {sharpe:.2f} / CAGR {cagr*100:.1f}% / MDD {mdd*100:.0f}%"


def main() -> None:
    series = pd.read_parquet(OUT_DIR / "portfolio_4way_returns.parquet")
    print(f"Window: {series.index.min().date()} → {series.index.max().date()}")

    # === Figure 1: Equity log scale ===
    fig, ax = plt.subplots(figsize=(13, 7))
    for col in series.columns:
        eq = (1 + series[col]).cumprod()
        ax.plot(eq.index, eq.values, color=COLORS[col], linewidth=1.4,
                label=f"{LABELS[col]}: {metrics_str(series[col])}", alpha=0.9)
    ax.set_yscale("log")
    ax.set_title("4-way portfolio comparison — 32y synth (1994-2026)",
                 fontsize=12, weight="bold")
    ax.set_ylabel("Equity (log scale, $1 → ...)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "PORTFOLIO_4WAY_equity.png", dpi=110)
    plt.close(fig)
    print("Wrote PORTFOLIO_4WAY_equity.png")

    # === Figure 2: Drawdowns ===
    fig, ax = plt.subplots(figsize=(13, 6))
    for col in series.columns:
        eq = (1 + series[col]).cumprod()
        dd = (eq / eq.cummax() - 1) * 100
        ax.plot(dd.index, dd.values, color=COLORS[col], linewidth=1.0,
                label=LABELS[col], alpha=0.85)
    ax.axhline(-25, color="orange", linewidth=0.7, linestyle=":", alpha=0.6)
    ax.axhline(-50, color="red", linewidth=0.7, linestyle=":", alpha=0.6)
    ax.set_title("Drawdowns — 4-way portfolio comparison", fontsize=12, weight="bold")
    ax.set_ylabel("Drawdown %")
    ax.legend(loc="lower left", fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "PORTFOLIO_4WAY_drawdowns.png", dpi=110)
    plt.close(fig)
    print("Wrote PORTFOLIO_4WAY_drawdowns.png")

    # === Figure 3: Rolling 10y CAGR ===
    def rolling_cagr(r: pd.Series, win_y: int) -> pd.Series:
        win = win_y * 252
        if len(r) < win:
            return pd.Series(dtype=float)
        out = []
        idx = r.index[win - 1:]
        arr = r.values
        for i in range(len(idx)):
            seg = arr[i:i + win]
            eq = (1 + seg).cumprod()
            out.append(eq[-1] ** (1 / win_y) - 1)
        return pd.Series(out, index=idx[:len(out)])

    fig, ax = plt.subplots(figsize=(13, 6))
    for col in series.columns:
        rcg = rolling_cagr(series[col], 10) * 100
        if not rcg.empty:
            ax.plot(rcg.index, rcg.values, color=COLORS[col], linewidth=1.2,
                    label=f"{LABELS[col]} (mean {rcg.mean():.1f}%)", alpha=0.85)
    ax.axhline(5, color="gray", linewidth=0.7, linestyle="--", alpha=0.6)
    ax.axhline(0, color="red", linewidth=0.5, alpha=0.5)
    ax.set_title("Rolling 10-year CAGR — 4-way comparison", fontsize=12, weight="bold")
    ax.set_ylabel("10y CAGR %")
    ax.legend(loc="lower left", fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "PORTFOLIO_4WAY_rolling10y.png", dpi=110)
    plt.close(fig)
    print("Wrote PORTFOLIO_4WAY_rolling10y.png")

    # === Figure 4: Lost decade zoom (2000-2013) + 2022 stress ===
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    for ax, (start, end, title) in zip(axes, [
        ("2000-01-01", "2012-12-31", "US 'Lost Decade' 2000-2013"),
        ("2021-12-31", "2024-06-30", "2022 rate cycle stress"),
    ]):
        for col in series.columns:
            r = series[col].loc[start:end]
            if len(r) == 0:
                continue
            eq = (1 + r).cumprod()
            eq = eq / eq.iloc[0]
            cagr = eq.iloc[-1] ** (1 / (len(r) / 252)) - 1
            ax.plot(eq.index, eq.values, color=COLORS[col], linewidth=1.5,
                    label=f"{LABELS[col]}: CAGR {cagr*100:+.1f}%", alpha=0.9)
        ax.axhline(1.0, color="black", linewidth=0.5, alpha=0.7)
        ax.set_title(title, fontsize=11, weight="bold")
        ax.set_ylabel("Equity (start = $1)")
        ax.legend(loc="best", fontsize=8)
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "PORTFOLIO_4WAY_stress.png", dpi=110)
    plt.close(fig)
    print("Wrote PORTFOLIO_4WAY_stress.png")

    # === Figure 5: Portfolio composition comparison (stacked bars) ===
    composition = {
        "V1 NTSX+GDE 67/33": {
            "US Equity (S&P)": 60.3, "US Bonds (IEF)": 40.2, "Cash short": -33.5,
            "Gold (GDE)": 29.7, "DM Equity": 0, "EM Equity": 0, "BTC": 0,
            "US SCV": 0, "DM SCV": 0, "US Mom": 0, "DM Mom": 0,
        },
        "V3_1 Plano C v3.5": {
            "US Equity (S&P)": 22.5 + 12 + 7,  # GDE S&P + AVUS + SPMO
            "US Bonds (IEF)": 0, "Cash short": 0,
            "Gold (GDE+BTGD)": 22.5 + 2.5,
            "DM Equity": 20 + 3, "EM Equity": 13, "BTC": 2.5,
            "US SCV": 10, "DM SCV": 5, "US Mom": 0, "DM Mom": 0,
        },
        "V_HYBRID (NTSX in V3_1)": {
            "US Equity (S&P)": 22.5 + 0.9 * 12 + 7,  # GDE + NTSX equity + SPMO
            "US Bonds (IEF)": 0.6 * 12,  # NTSX bond leg
            "Cash short": -0.5 * 12,
            "Gold (GDE+BTGD)": 22.5 + 2.5,
            "DM Equity": 20 + 3, "EM Equity": 13, "BTC": 2.5,
            "US SCV": 10, "DM SCV": 5, "US Mom": 0, "DM Mom": 0,
        },
    }
    asset_classes = ["US Equity (S&P)", "US Bonds (IEF)", "Cash short", "Gold (GDE+BTGD)",
                     "DM Equity", "EM Equity", "BTC", "US SCV", "DM SCV"]
    asset_colors = {"US Equity (S&P)": "#d62728", "US Bonds (IEF)": "#1f77b4",
                    "Cash short": "gray", "Gold (GDE+BTGD)": "goldenrod",
                    "DM Equity": "#2ca02c", "EM Equity": "#ff7f0e",
                    "BTC": "#9467bd", "US SCV": "salmon", "DM SCV": "olive",
                    "Gold (GDE)": "goldenrod"}

    fig, ax = plt.subplots(figsize=(12, 7))
    portfolios = list(composition.keys())
    x = np.arange(len(portfolios))
    bottoms = np.zeros(len(portfolios))
    for asset in asset_classes:
        values = []
        for p in portfolios:
            v = composition[p].get(asset, 0)
            if asset == "Gold (GDE+BTGD)" and "Gold (GDE)" in composition[p]:
                v = composition[p]["Gold (GDE)"]
            values.append(v)
        values = np.array(values, dtype=float)
        if np.all(values == 0):
            continue
        # Plot positive only above zero, negative below
        pos = np.where(values > 0, values, 0)
        neg = np.where(values < 0, values, 0)
        if pos.any():
            ax.bar(x, pos, bottom=np.where(bottoms > 0, bottoms, 0),
                   color=asset_colors.get(asset, "gray"),
                   label=asset, edgecolor="black", linewidth=0.4)
        if neg.any():
            ax.bar(x, neg, color=asset_colors.get(asset, "gray"),
                   edgecolor="black", linewidth=0.4)
        bottoms = bottoms + values
    ax.axhline(100, color="black", linewidth=0.7, linestyle="--", alpha=0.6,
               label="100% capital")
    ax.set_xticks(x)
    ax.set_xticklabels(portfolios, fontsize=10)
    ax.set_ylabel("Notional exposure %")
    ax.set_title("Portfolio composition by asset class (notional)",
                 fontsize=12, weight="bold")
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "PORTFOLIO_4WAY_composition.png", dpi=110)
    plt.close(fig)
    print("Wrote PORTFOLIO_4WAY_composition.png")


if __name__ == "__main__":
    main()
