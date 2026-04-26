"""Long-window (40y synth) re-validation of select top-N strategies.

Re-runs simple, well-understood strategies on the SPYSIM / QQQSIM /
ZROZSIM / GLDSIM 40-year synthetic data from testfolio cache. Confirms
that the post-2009 edge survives in a longer window that includes the
1987 crash, the 2000 dot-com, and the 2008 GFC.

Strategies re-implemented here (matching their original iter logic):

  * iter 004 — vol-managed SPY (`σ⁻¹` Carver form)
  * iter 005 — variance-managed SPY (`σ⁻²` Moreira-Muir form)
  * iter 015 — static NTSX 90/60 SPY+ZROZSIM (TLT proxy)
  * iter 016 — static stack + vol-target overlay
  * iter 035 — static stack 90/60 SPY+ZROZSIM+GLDSIM (3-leg)
  * iter 006 — vol-managed 60/40 SPY+ZROZSIM
  * iter 074 — ensemble of iter 016 and iter 064-style trend (uses 016 only,
              since iter 064 needs IEF+HYG which have no synth analog)

Strategies with HYG, IEF, VIX, EBP, T10Y3M dependencies (iter 064/069/070/071
family) are documented as "synth-unavailable" — long-window re-test would
require building synth analogs for those macro series first.

Citations: same as the source iterations.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TF_PATH = ROOT / "data/testfolio/cache/history.parquet"
TRADING_DAYS = 252
COST_BPS = 0.0002  # 2 bps per scale change (matches iter 004+ convention)


# --- Data ---------------------------------------------------------------------


def load_synth() -> pd.DataFrame:
    df = pd.read_parquet(TF_PATH)
    df.index = pd.to_datetime(df.index)
    return df


def returns_from_prices(p: pd.Series) -> pd.Series:
    return p.pct_change().dropna()


# --- Metrics ------------------------------------------------------------------


def metrics(r: pd.Series, name: str = "") -> dict:
    eq = (1.0 + r).cumprod()
    years = len(r) / TRADING_DAYS
    sd = r.std(ddof=1)
    sharpe = float(np.sqrt(TRADING_DAYS) * r.mean() / sd) if sd > 0 else float("nan")
    cagr = float(eq.iloc[-1] ** (1 / years) - 1) if years > 0 else float("nan")
    mdd = float((1 - eq / eq.cummax()).max())
    return {"name": name, "n_bars": len(r), "sharpe": sharpe, "cagr": cagr, "mdd": mdd,
            "start": str(r.index[0].date()), "end": str(r.index[-1].date())}


# --- Sizing primitives --------------------------------------------------------


def vol_target_scale(returns: pd.Series, target_vol: float, lookback: int,
                     max_leverage: float) -> pd.Series:
    """Carver-style vol scaling: s_t = target_vol / σ̂_{t-1} (lagged)."""
    realized_vol = returns.rolling(lookback).std() * np.sqrt(TRADING_DAYS)
    scale = target_vol / realized_vol.shift(1)
    return scale.clip(upper=max_leverage).fillna(0.0)


def variance_target_scale(returns: pd.Series, target_vol: float, lookback: int,
                          max_leverage: float) -> pd.Series:
    """Moreira-Muir: s_t = target_vol² / σ̂²_{t-1}."""
    realized_var = (returns.rolling(lookback).std() ** 2) * TRADING_DAYS
    scale = (target_vol ** 2) / realized_var.shift(1)
    return scale.clip(upper=max_leverage).fillna(0.0)


def apply_scale(returns: pd.Series, scale: pd.Series, cost: float = COST_BPS) -> pd.Series:
    """Apply ex-ante scale with per-unit-of-scale-change cost."""
    aligned_scale = scale.reindex(returns.index).fillna(0.0)
    gross = aligned_scale * returns
    turnover = aligned_scale.diff().abs()
    net = gross - cost * turnover
    return net.dropna()


# --- Strategies ---------------------------------------------------------------


def strat_iter004_vol_managed_spy(prices: pd.DataFrame, target_vol=0.20,
                                   lookback=21, max_leverage=1.5) -> pd.Series:
    r_spy = returns_from_prices(prices["SPYSIM"])
    s = vol_target_scale(r_spy, target_vol, lookback, max_leverage)
    return apply_scale(r_spy, s)


def strat_iter005_variance_managed_spy(prices: pd.DataFrame, target_vol=0.20,
                                        lookback=21, max_leverage=1.5) -> pd.Series:
    r_spy = returns_from_prices(prices["SPYSIM"])
    s = variance_target_scale(r_spy, target_vol, lookback, max_leverage)
    return apply_scale(r_spy, s)


def strat_iter015_ntsx_static_90_60(prices: pd.DataFrame, eq_w=0.90, bd_w=0.60) -> pd.Series:
    r_eq = returns_from_prices(prices["SPYSIM"])
    r_bd = returns_from_prices(prices["ZROZSIM"])
    common = r_eq.index.intersection(r_bd.index)
    return (eq_w * r_eq.loc[common] + bd_w * r_bd.loc[common]).dropna()


def strat_iter016_static_stack_vm(prices: pd.DataFrame, target_vol=0.15,
                                   lookback=21, max_leverage=2.0) -> pd.Series:
    r_blend = strat_iter015_ntsx_static_90_60(prices)
    s = vol_target_scale(r_blend, target_vol, lookback, max_leverage)
    return apply_scale(r_blend, s)


def strat_iter035_static_stack_3leg(prices: pd.DataFrame, eq_w=0.90, bd_w=0.60,
                                     gld_w=0.30) -> pd.Series:
    r_eq = returns_from_prices(prices["SPYSIM"])
    r_bd = returns_from_prices(prices["ZROZSIM"])
    r_gd = returns_from_prices(prices["GLDSIM"])
    common = r_eq.index.intersection(r_bd.index).intersection(r_gd.index)
    return (eq_w * r_eq.loc[common] + bd_w * r_bd.loc[common] + gld_w * r_gd.loc[common]).dropna()


def strat_iter006_vol_managed_60_40(prices: pd.DataFrame, target_vol=0.15,
                                     lookback=21, max_leverage=2.0) -> pd.Series:
    r_eq = returns_from_prices(prices["SPYSIM"])
    r_bd = returns_from_prices(prices["ZROZSIM"])
    common = r_eq.index.intersection(r_bd.index)
    r_blend = (0.6 * r_eq.loc[common] + 0.4 * r_bd.loc[common]).dropna()
    s = vol_target_scale(r_blend, target_vol, lookback, max_leverage)
    return apply_scale(r_blend, s)


# Iter 074: 50/50 ensemble of iter 016 and a iter-064-like trend strategy.
# Since iter 064 needs IEF+HYG (no synth), we approximate iter 074 as JUST
# iter 016 here (and document the simplification).

def strat_iter074_ensemble_simplified(prices: pd.DataFrame) -> pd.Series:
    return strat_iter016_static_stack_vm(prices)


STRATEGIES = {
    "iter004_vol_managed_spy_SPYSIM": (strat_iter004_vol_managed_spy, "SPYSIM"),
    "iter005_variance_managed_spy_SPYSIM": (strat_iter005_variance_managed_spy, "SPYSIM"),
    "iter006_vol_managed_60_40_SPYSIM_ZROZSIM": (strat_iter006_vol_managed_60_40, "SPYSIM"),
    "iter015_ntsx_static_90_60_SPYSIM_ZROZSIM": (strat_iter015_ntsx_static_90_60, "SPYSIM"),
    "iter016_static_stack_vm_SPYSIM_ZROZSIM": (strat_iter016_static_stack_vm, "SPYSIM"),
    "iter035_static_stack_3leg_SPYSIM_ZROZSIM_GLDSIM": (strat_iter035_static_stack_3leg, "SPYSIM"),
    "iter074_ensemble_SIMPLIFIED_to_iter016": (strat_iter074_ensemble_simplified, "SPYSIM"),
}

# Strategies that require macro/credit data with no synth analog
SYNTH_UNAVAILABLE = {
    "iter064_qqq_trend_substitution": "needs IEF+HYG (no synth analog)",
    "iter069_vix_inner_weight_reverse": "needs IEF+HYG+VIX",
    "iter070_t10y3m_cont_inner_weight": "needs IEF+HYG+T10Y3M",
    "iter071_iter064_plus_spy_mr_rsi2": "needs IEF+HYG+RSI2 path",
    "iter058_iter046_plus_hyg_tsm_w010": "needs HYG",
    "iter041_regime_weights_vix_static_stack": "needs VIX",
    "iter046_iter039_overlay_on_iter041": "needs IEF",
    "iter048_iter046_output_lev_gate": "needs IEF",
    "iter063_iter058_internal_letf_iter041_only": "needs VIX",
    "iter072_iter064_vix_cond_r_mr_allocation": "needs VIX",
    "iter073_gayed_ma_gate_on_iter016": "needs Gayed-MA gate (UTIL/SPY ratio)",
    "iter051_iter037_plus_iter026_w080": "needs IEF+VIX",
    "iter053_iter037_plus_iter046_w070": "needs IEF",
}


def main() -> None:
    df = load_synth()
    print(f"Loaded synth: {df.index.min()} → {df.index.max()}, "
          f"{len(df)} bars, columns: {list(df.columns)}")

    bench_spy = metrics(returns_from_prices(df["SPYSIM"]), "SPYSIM b&h")
    bench_qqq = metrics(returns_from_prices(df["QQQSIM"]), "QQQSIM b&h")
    print(f"\n=== Benchmarks (40y synth) ===")
    print(f"  SPYSIM b&h: Sharpe {bench_spy['sharpe']:.3f} | CAGR {bench_spy['cagr']*100:.2f}% | MDD {bench_spy['mdd']*100:.2f}%")
    print(f"  QQQSIM b&h: Sharpe {bench_qqq['sharpe']:.3f} | CAGR {bench_qqq['cagr']*100:.2f}% | MDD {bench_qqq['mdd']*100:.2f}%")

    print(f"\n=== Long-window strategy results (40y synth) ===")
    out_rows = []
    for slug, (fn, primary_bench) in STRATEGIES.items():
        try:
            r = fn(df)
        except Exception as e:
            print(f"  {slug}: FAILED ({e})")
            continue
        m = metrics(r, slug)
        bench = bench_spy if primary_bench == "SPYSIM" else bench_qqq
        sharpe_delta = m["sharpe"] - bench["sharpe"]
        cagr_delta_pp = (m["cagr"] - bench["cagr"]) * 100
        mdd_delta_pp = (m["mdd"] - bench["mdd"]) * 100
        out_rows.append({
            **m,
            "primary_bench": primary_bench,
            "sharpe_delta": sharpe_delta,
            "cagr_delta_pp": cagr_delta_pp,
            "mdd_delta_pp": mdd_delta_pp,
        })
        print(f"  {slug}:")
        print(f"     Sharpe {m['sharpe']:.3f} (Δ vs {primary_bench} {sharpe_delta:+.3f}) | "
              f"CAGR {m['cagr']*100:.2f}% (Δ {cagr_delta_pp:+.2f}pp) | "
              f"MDD {m['mdd']*100:.2f}% (Δ {mdd_delta_pp:+.2f}pp)")

    # Write report
    out = ROOT / "studies/strategy_hunt_loop/LONG_WINDOW_VALIDATION.md"
    with out.open("w") as fh:
        fh.write("# Long-window (40y synth) validation\n\n")
        fh.write(f"Generated: {pd.Timestamp.now().isoformat()}\n\n")
        fh.write("Re-runs select strategies on testfolio synthetic data from "
                 "1986-01-02 → 2026-04-17 (40y, 10 151 bars). Includes 1987 crash, "
                 "1990 recession, 2000 dot-com, 2008 GFC, 2020 COVID, 2022 rates, "
                 "2024-2025 — far more regime variety than the 17y SPY-Tiingo "
                 "window the hunt loop uses.\n\n")
        fh.write("Strategies with HYG/IEF-direct/VIX/EBP/T10Y3M dependencies are "
                 "skipped (no synth analog). Bond-leg substituted with **ZROZSIM** "
                 "(zero-coupon long bond) where the original used TLT or IEF.\n\n")

        fh.write("## Benchmarks (40y synth b&h)\n\n")
        fh.write("| asset | Sharpe | CAGR | MDD | bars |\n|---|---|---|---|---|\n")
        fh.write(f"| SPYSIM | {bench_spy['sharpe']:.3f} | {bench_spy['cagr']*100:.2f}% | {bench_spy['mdd']*100:.2f}% | {bench_spy['n_bars']} |\n")
        fh.write(f"| QQQSIM | {bench_qqq['sharpe']:.3f} | {bench_qqq['cagr']*100:.2f}% | {bench_qqq['mdd']*100:.2f}% | {bench_qqq['n_bars']} |\n\n")

        fh.write("## Strategy results (40y synth)\n\n")
        fh.write("| strategy | Sharpe (Δ) | CAGR (Δ) | MDD (Δ) | dominates? |\n")
        fh.write("|---|---|---|---|---|\n")
        for row in out_rows:
            sh_str = f"{row['sharpe']:.3f} ({row['sharpe_delta']:+.3f})"
            cg_str = f"{row['cagr']*100:.2f}% ({row['cagr_delta_pp']:+.2f}pp)"
            md_str = f"{row['mdd']*100:.2f}% ({row['mdd_delta_pp']:+.2f}pp)"
            dominates_sharpe = row["sharpe_delta"] > 0
            dominates_cagr = row["cagr_delta_pp"] > 0
            dom = "✅ Sharpe+CAGR" if (dominates_sharpe and dominates_cagr) else (
                  "🟡 Sharpe-only" if dominates_sharpe else "❌ neither")
            fh.write(f"| `{row['name']}` | {sh_str} | {cg_str} | {md_str} | {dom} |\n")

        fh.write("\n## Strategies skipped (synth-unavailable inputs)\n\n")
        fh.write("| iter | reason |\n|---|---|\n")
        for slug, reason in SYNTH_UNAVAILABLE.items():
            fh.write(f"| `{slug}` | {reason} |\n")

        fh.write("\n## Reading the table\n\n")
        fh.write("- **✅ Sharpe+CAGR**: dominates SPY/QQQ b&h on BOTH risk-adjusted "
                 "and raw return — strongest evidence the edge is real.\n")
        fh.write("- **🟡 Sharpe-only**: better risk-adjusted but lower raw return — "
                 "defensive stance; valid for sleep-well portfolios but trades CAGR.\n")
        fh.write("- **❌ neither**: edge does not survive the longer window.\n\n")
        fh.write("Caveat: synth data has perfect liquidity, no slippage, idealized "
                 "dividend reinvestment. Real-world execution would haircut these "
                 "numbers by ~50-150 bps CAGR depending on rebalance frequency.\n")

    (ROOT / "studies/strategy_hunt_loop/LONG_WINDOW_VALIDATION.json").write_text(
        json.dumps({"benchmarks": {"SPYSIM": bench_spy, "QQQSIM": bench_qqq},
                    "strategies": out_rows,
                    "skipped": SYNTH_UNAVAILABLE}, indent=2, default=str)
    )

    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
