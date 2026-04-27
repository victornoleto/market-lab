"""Plots for V_HYBRID variants comparison."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = Path(__file__).resolve().parent

# Focus on top performers + baselines
FOCUS = [
    "V1_NTSX_GDE_67_33",
    "V_HYBRID_50_50_with_V1",
    "V_HYBRID_KITCHEN_SINK",
    "V_HYBRID_PLUS_MF",
    "V_HYBRID_baseline",
    "V3_1_PlanoC_v3.5",
]

COLORS = {
    "V1_NTSX_GDE_67_33": "#2ca02c",
    "V_HYBRID_50_50_with_V1": "#17becf",
    "V_HYBRID_KITCHEN_SINK": "#9467bd",
    "V_HYBRID_PLUS_MF": "#ff7f0e",
    "V_HYBRID_RSST_substitute": "#bcbd22",
    "V_HYBRID_GLOBAL_STACK": "#e377c2",
    "V_HYBRID_baseline": "#1f77b4",
    "V3_1_PlanoC_v3.5": "#d62728",
}

LABELS = {
    "V1_NTSX_GDE_67_33": "V1 NTSX+GDE 67/33 (2 ETFs, US-only)",
    "V_HYBRID_50_50_with_V1": "V_HYBRID 50/50 V1 blend (10 ETFs)",
    "V_HYBRID_KITCHEN_SINK": "V_HYBRID KITCHEN SINK (13 ETFs, MF+stack+RSST)",
    "V_HYBRID_PLUS_MF": "V_HYBRID + MF 10% KMLM (12 ETFs)",
    "V_HYBRID_RSST_substitute": "V_HYBRID RSST substitute",
    "V_HYBRID_GLOBAL_STACK": "V_HYBRID GLOBAL STACK (NTSI+NTSE)",
    "V_HYBRID_baseline": "V_HYBRID baseline (11 ETFs)",
    "V3_1_PlanoC_v3.5": "V3_1 Plano C v3.5 (11 ETFs)",
}


def metrics_str(r: pd.Series) -> str:
    eq = (1 + r).cumprod()
    years = len(r) / 252
    cagr = eq.iloc[-1] ** (1 / years) - 1
    sharpe = np.sqrt(252) * r.mean() / r.std(ddof=1)
    mdd = (eq / eq.cummax() - 1).min()
    return f"Sh {sharpe:.2f} / CAGR {cagr*100:.1f}% / MDD {mdd*100:.0f}%"


def main() -> None:
    series = pd.read_parquet(OUT_DIR / "portfolio_variants_returns.parquet")
    print(f"Loaded {series.shape[1]} portfolios")

    # === Figure 1: Equity log-scale (focus group) ===
    fig, ax = plt.subplots(figsize=(13, 7))
    for col in FOCUS:
        if col not in series.columns:
            continue
        eq = (1 + series[col]).cumprod()
        ax.plot(eq.index, eq.values, color=COLORS[col], linewidth=1.4,
                label=f"{LABELS[col]}: {metrics_str(series[col])}", alpha=0.9)
    ax.set_yscale("log")
    ax.set_title("V_HYBRID variants vs V1 vs V3_1 — 32y synth", fontsize=12, weight="bold")
    ax.set_ylabel("Equity (log scale)")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "PORTFOLIO_VARIANTS_equity.png", dpi=110)
    plt.close(fig)
    print("Wrote PORTFOLIO_VARIANTS_equity.png")

    # === Figure 2: Drawdowns ===
    fig, ax = plt.subplots(figsize=(13, 6))
    for col in FOCUS:
        if col not in series.columns:
            continue
        eq = (1 + series[col]).cumprod()
        dd = (eq / eq.cummax() - 1) * 100
        ax.plot(dd.index, dd.values, color=COLORS[col], linewidth=1.0,
                label=LABELS[col], alpha=0.8)
    ax.axhline(-25, color="orange", linewidth=0.7, linestyle=":", alpha=0.6)
    ax.axhline(-50, color="red", linewidth=0.7, linestyle=":", alpha=0.6)
    ax.set_title("Drawdowns — V_HYBRID variants comparison", fontsize=12, weight="bold")
    ax.set_ylabel("Drawdown %")
    ax.legend(loc="lower left", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "PORTFOLIO_VARIANTS_drawdowns.png", dpi=110)
    plt.close(fig)
    print("Wrote PORTFOLIO_VARIANTS_drawdowns.png")

    # === Figure 3: Risk-return scatter (Sharpe vs CAGR with MDD as size) ===
    fig, ax = plt.subplots(figsize=(11, 7))
    for col in series.columns:
        r = series[col]
        eq = (1 + r).cumprod()
        years = len(r) / 252
        cagr = eq.iloc[-1] ** (1 / years) - 1
        sharpe = np.sqrt(252) * r.mean() / r.std(ddof=1)
        mdd = (eq / eq.cummax() - 1).min()
        size = (abs(mdd) * 1000)
        c = COLORS.get(col, "gray")
        ax.scatter(sharpe, cagr * 100, s=size, color=c, alpha=0.65, edgecolor="black",
                   linewidth=1.2)
        ax.annotate(col.replace("_", " "), (sharpe, cagr * 100),
                    fontsize=8, xytext=(5, 5), textcoords="offset points")
    ax.set_xlabel("Sharpe ratio (annualized, daily)")
    ax.set_ylabel("CAGR %")
    ax.set_title("Risk-return scatter (bubble size = MDD)", fontsize=12, weight="bold")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "PORTFOLIO_VARIANTS_scatter.png", dpi=110)
    plt.close(fig)
    print("Wrote PORTFOLIO_VARIANTS_scatter.png")

    # === Figure 4: Rolling 10y Sharpe ===
    def rolling_sharpe(r, win_y):
        win = win_y * 252
        if len(r) < win:
            return pd.Series(dtype=float)
        out = []
        idx = r.index[win - 1:]
        arr = r.values
        for i in range(len(idx)):
            seg = arr[i:i + win]
            sd = seg.std(ddof=1)
            out.append(np.sqrt(252) * seg.mean() / sd if sd > 0 else np.nan)
        return pd.Series(out, index=idx[:len(out)])

    fig, ax = plt.subplots(figsize=(13, 6))
    for col in FOCUS:
        if col not in series.columns:
            continue
        rs = rolling_sharpe(series[col], 10)
        ax.plot(rs.index, rs.values, color=COLORS[col], linewidth=1.2,
                label=f"{col} (mean {rs.mean():.2f})", alpha=0.85)
    ax.axhline(0, color="red", linewidth=0.5, alpha=0.5)
    ax.axhline(0.5, color="gray", linewidth=0.5, linestyle="--", alpha=0.5)
    ax.set_title("Rolling 10y Sharpe — V_HYBRID variants", fontsize=12, weight="bold")
    ax.set_ylabel("10y Sharpe")
    ax.legend(loc="lower left", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "PORTFOLIO_VARIANTS_rolling10y.png", dpi=110)
    plt.close(fig)
    print("Wrote PORTFOLIO_VARIANTS_rolling10y.png")

    # === Figure 5: 2022 stress zoom ===
    fig, ax = plt.subplots(figsize=(13, 6))
    for col in FOCUS:
        if col not in series.columns:
            continue
        r = series[col].loc["2021-12-31":"2024-06-30"]
        eq = (1 + r).cumprod()
        eq = eq / eq.iloc[0]
        cagr = eq.iloc[-1] ** (1 / (len(r) / 252)) - 1
        ax.plot(eq.index, eq.values, color=COLORS[col], linewidth=1.4,
                label=f"{LABELS[col]}: CAGR {cagr*100:+.1f}%", alpha=0.85)
    ax.axhline(1.0, color="black", linewidth=0.5)
    ax.set_title("2022 rate cycle stress — V_HYBRID variants", fontsize=12, weight="bold")
    ax.set_ylabel("Equity (Jan 2022 = $1)")
    ax.legend(loc="best", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "PORTFOLIO_VARIANTS_2022.png", dpi=110)
    plt.close(fig)
    print("Wrote PORTFOLIO_VARIANTS_2022.png")


if __name__ == "__main__":
    main()
