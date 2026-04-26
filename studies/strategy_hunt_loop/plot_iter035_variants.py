"""Plot iter 035 deployment variants vs SPYSIM benchmark, 40y synth."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "studies/strategy_hunt_loop"
TF_PATH = ROOT / "data/testfolio/cache/history.parquet"


def main() -> None:
    series = pd.read_parquet(OUT_DIR / "iter035_variants_returns.parquet")
    metrics = json.loads((OUT_DIR / "ITER035_VARIANTS_VALIDATION.json").read_text())
    bench = metrics["benchmark"]
    rows = {r["name"]: r for r in metrics["strategies"]}

    # Bench from raw SPYSIM (already in synth)
    df = pd.read_parquet(TF_PATH)
    df.index = pd.to_datetime(df.index)
    spy_r = df["SPYSIM"].pct_change().dropna()
    common_start = max(spy_r.index.min(), series.index.min())
    spy_r = spy_r.loc[common_start:]
    series = series.loc[common_start:]

    spy_eq = (1 + spy_r).cumprod()

    # === Figure 1: Equity curves (log scale) ===
    fig, ax = plt.subplots(figsize=(13, 7))
    colors = {
        "V0_iter035_pure_SPY_ZROZ_GLD_180notional": "#d62728",  # red
        "V1_NTSX_GDE_67_33_Inter_cash": "#2ca02c",  # green
        "V2_SSO_UBT_UGL_BIL_2x_Inter": "#1f77b4",  # blue
        "V3_UPRO_TMF_GLD_BIL_3x_Inter": "#9467bd",  # purple
    }
    labels = {
        "V0_iter035_pure_SPY_ZROZ_GLD_180notional":
            f"V0 iter035 PURE 90/60/30 (margin) — Sh {rows['V0_iter035_pure_SPY_ZROZ_GLD_180notional']['sharpe']:.2f} / "
            f"CAGR {rows['V0_iter035_pure_SPY_ZROZ_GLD_180notional']['cagr']*100:.1f}% / "
            f"MDD {rows['V0_iter035_pure_SPY_ZROZ_GLD_180notional']['mdd']*100:.0f}%",
        "V1_NTSX_GDE_67_33_Inter_cash":
            f"V1 NTSX+GDE 67/33 (Inter cash) — Sh {rows['V1_NTSX_GDE_67_33_Inter_cash']['sharpe']:.2f} / "
            f"CAGR {rows['V1_NTSX_GDE_67_33_Inter_cash']['cagr']*100:.1f}% / "
            f"MDD {rows['V1_NTSX_GDE_67_33_Inter_cash']['mdd']*100:.0f}%",
        "V2_SSO_UBT_UGL_BIL_2x_Inter":
            f"V2 SSO+UBT+UGL+BIL 2× LETF — Sh {rows['V2_SSO_UBT_UGL_BIL_2x_Inter']['sharpe']:.2f} / "
            f"CAGR {rows['V2_SSO_UBT_UGL_BIL_2x_Inter']['cagr']*100:.1f}% / "
            f"MDD {rows['V2_SSO_UBT_UGL_BIL_2x_Inter']['mdd']*100:.0f}%",
        "V3_UPRO_TMF_GLD_BIL_3x_Inter":
            f"V3 UPRO+TMF+GLD+BIL 3× LETF — Sh {rows['V3_UPRO_TMF_GLD_BIL_3x_Inter']['sharpe']:.2f} / "
            f"CAGR {rows['V3_UPRO_TMF_GLD_BIL_3x_Inter']['cagr']*100:.1f}% / "
            f"MDD {rows['V3_UPRO_TMF_GLD_BIL_3x_Inter']['mdd']*100:.0f}%",
    }

    for col in series.columns:
        eq = (1 + series[col].dropna()).cumprod()
        ax.plot(eq.index, eq.values, color=colors.get(col, "gray"),
                linewidth=1.5, label=labels.get(col, col), alpha=0.85)

    ax.plot(spy_eq.index, spy_eq.values, color="black", linewidth=1.2, linestyle="--",
            label=f"SPYSIM b&h — Sh {bench['sharpe']:.2f} / "
                  f"CAGR {bench['cagr']*100:.1f}% / MDD {bench['mdd']*100:.0f}%",
            alpha=0.75)

    ax.set_yscale("log")
    ax.set_title("iter 035 deployment variants vs SPYSIM b&h — 40y synth (1986-2026)",
                 fontsize=13, weight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Equity (log scale, $1 → ...)")
    ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "ITER035_VARIANTS_equity_curves.png", dpi=110)
    plt.close(fig)
    print(f"Wrote ITER035_VARIANTS_equity_curves.png")

    # === Figure 2: Drawdowns ===
    fig, ax = plt.subplots(figsize=(13, 6))
    for col in series.columns:
        r = series[col].dropna()
        eq = (1 + r).cumprod()
        dd = (eq / eq.cummax() - 1) * 100
        ax.plot(dd.index, dd.values, color=colors.get(col, "gray"),
                linewidth=1.0, label=labels.get(col, col), alpha=0.85)

    spy_dd = (spy_eq / spy_eq.cummax() - 1) * 100
    ax.plot(spy_dd.index, spy_dd.values, color="black", linewidth=1.0,
            linestyle="--", label="SPYSIM b&h", alpha=0.75)

    ax.axhline(-25, color="red", linewidth=0.8, linestyle=":", alpha=0.6,
               label="−25% (Plano A bound)")
    ax.axhline(-50, color="orange", linewidth=0.8, linestyle=":", alpha=0.6,
               label="−50% (severe)")
    ax.set_title("Drawdowns — iter 035 variants vs SPYSIM b&h, 40y synth",
                 fontsize=13, weight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Drawdown %")
    ax.legend(loc="lower left", fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "ITER035_VARIANTS_drawdowns.png", dpi=110)
    plt.close(fig)
    print(f"Wrote ITER035_VARIANTS_drawdowns.png")

    # === Figure 3: 2022 zoom (rate-cycle stress test) ===
    fig, ax = plt.subplots(figsize=(13, 6))
    win_start, win_end = "2021-12-31", "2024-12-31"
    for col in series.columns:
        r = series[col].dropna().loc[win_start:win_end]
        if len(r) == 0:
            continue
        eq = (1 + r).cumprod()
        eq = eq / eq.iloc[0]  # normalize start
        ax.plot(eq.index, eq.values, color=colors.get(col, "gray"),
                linewidth=1.5, label=labels.get(col, col), alpha=0.85)

    spy_zoom = spy_r.loc[win_start:win_end]
    spy_zoom_eq = (1 + spy_zoom).cumprod()
    spy_zoom_eq = spy_zoom_eq / spy_zoom_eq.iloc[0]
    ax.plot(spy_zoom_eq.index, spy_zoom_eq.values, color="black",
            linewidth=1.2, linestyle="--", label="SPYSIM b&h", alpha=0.75)

    ax.set_title("2022 rate cycle stress — iter 035 variants (Jan 2022 = $1)",
                 fontsize=13, weight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity (linear)")
    ax.axhline(1.0, color="gray", linewidth=0.5, alpha=0.5)
    ax.legend(loc="best", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "ITER035_VARIANTS_2022_stress.png", dpi=110)
    plt.close(fig)
    print(f"Wrote ITER035_VARIANTS_2022_stress.png")


if __name__ == "__main__":
    main()
