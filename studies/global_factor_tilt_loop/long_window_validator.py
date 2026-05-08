"""Long-window (56y synth) re-validation for global factor-tilt loop.

Re-runs select strategies on testfolio synthetic data — VTSIM (Total
World 1970+) + VTISIM/VBRSIM/VEASIM/VXUSSIM/VWOSIM/IEFSIM/BNDSIM/
ZROZSIM/GLDSIM/RSSBSIM/GDESIM/KMLMSIM/DBMFSIM. Confirms post-2008 edge
survives in a 56y window covering 1973-74 oil shock, 1987 crash,
1990 recession, 2000 dot-com (US+intl), 2008 GFC, 2020 COVID, 2022
rate hikes, 2024-25.

Usage::

    uv run python studies/global_factor_tilt_loop/long_window_validator.py

Strategies are populated AS iter winners emerge; initial state is the
benchmark-only baseline (VTSIM + multi-stacking reference cells from
deploy_studies for sanity).

Citations: see source iter for each strategy entry below.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TF_PATH = ROOT / "data/testfolio/cache/history.parquet"
TRADING_DAYS = 252
COST_BPS = 0.0002


def load_synth() -> pd.DataFrame:
    df = pd.read_parquet(TF_PATH)
    df.index = pd.to_datetime(df.index)
    return df


def returns_from_prices(p: pd.Series) -> pd.Series:
    return p.pct_change().dropna()


def metrics(r: pd.Series, name: str = "") -> dict:
    eq = (1.0 + r).cumprod()
    years = len(r) / TRADING_DAYS
    sd = r.std(ddof=1)
    sharpe = float(np.sqrt(TRADING_DAYS) * r.mean() / sd) if sd > 0 else float("nan")
    cagr = float(eq.iloc[-1] ** (1 / years) - 1) if years > 0 else float("nan")
    mdd = float((1 - eq / eq.cummax()).max())
    return {"name": name, "n_bars": len(r), "sharpe": sharpe, "cagr": cagr, "mdd": mdd,
            "start": str(r.index[0].date()), "end": str(r.index[-1].date())}


# --- Reference strategies (deploy_studies winners — for cross-comparison) ----


def strat_v_hybrid_plus_mf(prices: pd.DataFrame) -> pd.Series:
    """V_HYBRID + 10% Managed Futures (deploy_studies portfolio_variants WINNER).

    25% GDE + 12% NTSX_synth + 20% AVDE_proxy + 13% AVEM_proxy + 10% AVUV_proxy
    + 5% AVDV_proxy + 7% SPMO_proxy + 3% IDMO_proxy + 5% BTGD_proxy + 10% KMLM
    — all weights × 0.90, plus 10% KMLMSIM.

    Avantis tickers proxied via Vanguard cap-weight equivalents (we don't
    have AVUS/AVDE/AVEM synth in cache):
      AVUS_proxy = VTISIM, AVDE_proxy = VEASIM, AVEM_proxy = VWOSIM,
      AVUV_proxy = VBRSIM (US small-cap value).
      AVDV_proxy = VSSSIM (intl developed small-cap; no SCV synth).
      SPMO/IDMO/BTGD synth not built — leg approximated as SPYSIM/VEASIM/GLDSIM.

    NTSX_synth via testfolio formula: 0.90 SPYSIM + 0.60 IEFSIM - 0.50 CASHX.

    Caveat: this is an approximation to the deploy_studies V_HYBRID+MF
    cell. Use as a SANITY REFERENCE, not a precise reproduction.
    """
    needed = ["GDESIM", "SPYSIM", "IEFSIM", "CASHX", "VEASIM", "VWOSIM",
              "VBRSIM", "VSSSIM", "GLDSIM", "KMLMSIM"]
    for c in needed:
        if c not in prices.columns:
            raise KeyError(f"long_window_validator: testfolio cache missing {c}")
    common = prices.dropna(subset=needed).index
    p = prices.loc[common, needed]

    r = {c: returns_from_prices(p[c]) for c in needed}
    common = r["GDESIM"].index
    for c in needed[1:]:
        common = common.intersection(r[c].index)
    for c in needed:
        r[c] = r[c].loc[common]

    # NTSX_synth = 0.90 SPYSIM + 0.60 IEFSIM - 0.50 CASHX
    ntsx_synth = 0.90 * r["SPYSIM"] + 0.60 * r["IEFSIM"] - 0.50 * r["CASHX"]

    # V_HYBRID core × 0.90, plus 10% KMLM
    weights = {
        "GDESIM": 0.225, "ntsx": 0.108,
        "VEASIM": 0.180, "VWOSIM": 0.117,
        "VBRSIM": 0.090, "VSSSIM": 0.045,
        "SPYSIM_spmo": 0.063, "VEASIM_idmo": 0.027, "GLDSIM_btgd": 0.045,
        "KMLMSIM": 0.10,
    }
    blended = (
        weights["GDESIM"]      * r["GDESIM"] +
        weights["ntsx"]        * ntsx_synth +
        weights["VEASIM"]      * r["VEASIM"] +
        weights["VWOSIM"]      * r["VWOSIM"] +
        weights["VBRSIM"]      * r["VBRSIM"] +
        weights["VSSSIM"]      * r["VSSSIM"] +
        weights["SPYSIM_spmo"] * r["SPYSIM"] +
        weights["VEASIM_idmo"] * r["VEASIM"] +
        weights["GLDSIM_btgd"] * r["GLDSIM"] +
        weights["KMLMSIM"]     * r["KMLMSIM"]
    )
    return blended.dropna()


def strat_global_returnstacked_allweather(prices: pd.DataFrame) -> pd.Series:
    """Multi-stacking thesis (README Tier 4 hypothesis #9).

    60% RSSB (global eq + Treasury via futures, 200% notional)
    + 30% GDE (S&P + gold, 180% notional)
    + 10% KMLM (managed futures)
    = ~270%+ notional via futures stacking, zero margin loan.

    Uses RSSBSIM + GDESIM + KMLMSIM testfolio synths.
    """
    for c in ("RSSBSIM", "GDESIM", "KMLMSIM"):
        if c not in prices.columns:
            raise KeyError(f"long_window_validator: testfolio cache missing {c}")
    r_rssb = returns_from_prices(prices["RSSBSIM"])
    r_gde  = returns_from_prices(prices["GDESIM"])
    r_kmlm = returns_from_prices(prices["KMLMSIM"])
    common = r_rssb.index.intersection(r_gde.index).intersection(r_kmlm.index)
    return (0.60 * r_rssb.loc[common] + 0.30 * r_gde.loc[common] +
            0.10 * r_kmlm.loc[common]).dropna()


STRATEGIES = {
    "ref_v_hybrid_plus_mf_synth_proxy": strat_v_hybrid_plus_mf,
    "ref_global_returnstacked_allweather": strat_global_returnstacked_allweather,
    # Iter winners are appended here as they emerge (with citation comment).
}


def main() -> None:
    df = load_synth()
    print(f"Loaded synth: {df.index.min()} → {df.index.max()}, "
          f"{len(df)} bars, columns: {list(df.columns)}")

    bench_vt = metrics(returns_from_prices(df["VTSIM"]), "VTSIM b&h")
    print(f"\n=== Benchmark (56y synth) ===")
    print(f"  VTSIM b&h: Sharpe {bench_vt['sharpe']:.3f} | "
          f"CAGR {bench_vt['cagr']*100:.2f}% | MDD {bench_vt['mdd']*100:.2f}%")

    print(f"\n=== Long-window strategy results ===")
    out_rows = []
    for slug, fn in STRATEGIES.items():
        try:
            r = fn(df)
        except Exception as e:
            print(f"  {slug}: FAILED ({e})")
            continue
        m = metrics(r, slug)
        sharpe_delta = m["sharpe"] - bench_vt["sharpe"]
        cagr_delta_pp = (m["cagr"] - bench_vt["cagr"]) * 100
        mdd_delta_pp = (m["mdd"] - bench_vt["mdd"]) * 100
        out_rows.append({
            **m,
            "primary_bench": "VTSIM",
            "sharpe_delta": sharpe_delta,
            "cagr_delta_pp": cagr_delta_pp,
            "mdd_delta_pp": mdd_delta_pp,
        })
        print(f"  {slug}:")
        print(f"     Sharpe {m['sharpe']:.3f} (Δ vs VTSIM {sharpe_delta:+.3f}) | "
              f"CAGR {m['cagr']*100:.2f}% (Δ {cagr_delta_pp:+.2f}pp) | "
              f"MDD {m['mdd']*100:.2f}% (Δ {mdd_delta_pp:+.2f}pp)")

    out = ROOT / "studies/global_factor_tilt_loop/LONG_WINDOW_VALIDATION.md"
    with out.open("w") as fh:
        fh.write("# Long-window (56y synth) validation — global factor-tilt loop\n\n")
        fh.write(f"Generated: {pd.Timestamp.now().isoformat()}\n\n")
        fh.write("Re-runs select strategies on testfolio synthetic data over the\n")
        fh.write(f"VTSIM 56y window ({bench_vt['start']} → {bench_vt['end']}). Includes\n")
        fh.write("1973-74 oil shock, 1987 crash, 1990 recession, 2000 dot-com (US+intl),\n")
        fh.write("2008 GFC, 2020 COVID, 2022 rate hikes, 2024-25.\n\n")
        fh.write("Initial reference strategies are deploy_studies winners (sanity\n")
        fh.write("baselines). Iter winners are appended to STRATEGIES dict as they\n")
        fh.write("emerge.\n\n")

        fh.write("## Benchmark (56y synth b&h)\n\n")
        fh.write("| asset | Sharpe | CAGR | MDD | bars |\n|---|---|---|---|---|\n")
        fh.write(f"| VTSIM | {bench_vt['sharpe']:.3f} | {bench_vt['cagr']*100:.2f}% | "
                 f"{bench_vt['mdd']*100:.2f}% | {bench_vt['n_bars']} |\n\n")

        fh.write("## Strategy results\n\n")
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

        fh.write("\nCaveat: synth data has perfect liquidity, no slippage, idealized\n")
        fh.write("dividend reinvestment. Real-world execution would haircut these\n")
        fh.write("numbers by ~50-150 bps CAGR depending on rebalance frequency.\n")

    (ROOT / "studies/global_factor_tilt_loop/LONG_WINDOW_VALIDATION.json").write_text(
        json.dumps({"benchmarks": {"VTSIM": bench_vt},
                    "strategies": out_rows}, indent=2, default=str)
    )

    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
