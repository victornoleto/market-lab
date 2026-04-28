"""Long-window equity curves: top-3 strategies vs SPYSIM/QQQSIM 40y.

Renders 1 panel × 2 datasets = 2 PNGs comparing iter 035 (max-CAGR
champion) and iter 016 (max-Sharpe champion) and iter 006 (defensive
champion) against the 40y SPYSIM b&h benchmark. Uses the same
unified driver as `long_window_validator.py`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "studies/strategy_hunt_loop"))

from long_window_validator import (load_synth, returns_from_prices,  # noqa: E402
                                    strat_iter004_vol_managed_spy,
                                    strat_iter006_vol_managed_60_40,
                                    strat_iter015_ntsx_static_90_60,
                                    strat_iter016_static_stack_vm,
                                    strat_iter035_static_stack_3leg,
                                    metrics)

OUT_DIR = ROOT / "studies/strategy_hunt_loop"


def equity(r: pd.Series) -> pd.Series:
    return (1.0 + r).cumprod()


def main() -> None:
    df = load_synth()
    bench_spy = returns_from_prices(df["SPYSIM"])
    bench_qqq = returns_from_prices(df["QQQSIM"])

    strategies = [
        ("iter 035 — static_stack_90_60_spy_gld", strat_iter035_static_stack_3leg(df), "#d35400"),
        ("iter 016 — static_stack_vm_hybrid",     strat_iter016_static_stack_vm(df),    "#1f6feb"),
        ("iter 006 — vol_managed_60_40",          strat_iter006_vol_managed_60_40(df),  "#27ae60"),
        ("iter 015 — ntsx_static_90_60",          strat_iter015_ntsx_static_90_60(df),  "#8e44ad"),
        ("iter 004 — vol_managed_spy",            strat_iter004_vol_managed_spy(df),    "#16a085"),
    ]

    # Plot: equity curves vs SPYSIM
    fig, ax = plt.subplots(figsize=(13, 7))
    eq_b = equity(bench_spy)
    ax.plot(eq_b.index, eq_b.values, color="#888", lw=1.5, ls="--",
            label=f"SPYSIM b&h (Sh {metrics(bench_spy)['sharpe']:.2f}, "
                  f"CAGR {metrics(bench_spy)['cagr']*100:.1f}%, "
                  f"MDD {metrics(bench_spy)['mdd']*100:.1f}%)")
    for label, r, color in strategies:
        m = metrics(r)
        eq = equity(r)
        ax.plot(eq.index, eq.values, color=color, lw=1.6,
                label=f"{label} (Sh {m['sharpe']:.2f}, CAGR {m['cagr']*100:.1f}%, "
                      f"MDD {m['mdd']*100:.1f}%)")
    ax.set_yscale("log")
    ax.set_ylabel("Equity (growth of $1, log scale)")
    ax.set_xlabel("Date")
    ax.set_title("Top-5 strategies vs SPYSIM b&h — 40-year synthetic (1986-2026)")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    out = OUT_DIR / "LONG_WINDOW_TOP5_vs_SPYSIM.png"
    fig.savefig(out, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")

    # Plot 2: drawdown comparison
    fig, ax = plt.subplots(figsize=(13, 6))
    eq_b = equity(bench_spy)
    dd_b = (eq_b / eq_b.cummax() - 1) * 100
    ax.plot(dd_b.index, dd_b.values, color="#888", lw=1.5, ls="--", label="SPYSIM b&h")
    ax.fill_between(dd_b.index, dd_b.values, 0, color="#888", alpha=0.15)
    for label, r, color in strategies[:3]:  # top 3 for clarity
        eq = equity(r)
        dd = (eq / eq.cummax() - 1) * 100
        ax.plot(dd.index, dd.values, color=color, lw=1.4, label=label)
    ax.set_ylabel("Drawdown (%)")
    ax.set_xlabel("Date")
    ax.set_title("Drawdown comparison — top-3 strategies vs SPYSIM b&h (40y synth)")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="lower left", fontsize=10)
    ax.axhline(-25, color="#aa3333", lw=0.7, ls=":", alpha=0.5)
    ax.text(dd_b.index[10], -25.5, "−25% line (Plano A bound)", fontsize=8, color="#aa3333")
    fig.tight_layout()
    out2 = OUT_DIR / "LONG_WINDOW_TOP3_DRAWDOWN.png"
    fig.savefig(out2, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out2}")


if __name__ == "__main__":
    main()
