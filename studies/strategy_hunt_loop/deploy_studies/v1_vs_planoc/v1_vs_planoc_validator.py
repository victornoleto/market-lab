"""V1 NTSX+GDE 67/33 vs Plano C V3_1 v3.5 — empirical comparison.

Compares the user's two paradigms head-to-head on long-window synth data:

  V1: 67% NTSX_synth + 33% GDESIM
      - Capital efficiency philosophy (WisdomTree return-stacking)
      - 2 ETFs total
      - No factor tilts, no international diversification

  V3_1 v3.5: 11-ETF factor-investing portfolio (Plano C accumulation 30-45)
      - 25% GDE + 12% AVUS + 20% AVDE + 13% AVEM
      - 15% SCV (10% AVUV + 5% AVDV)
      - 10% Momentum (7% SPMO + 3% IDMO)
      - 5% BTGD (gold+BTC stacked)
      - Total notional 125% via GDE+BTGD overlays

Window: 1994-05-04 → 2026-04-17 (~32 years; bounded by VWOSIM inception).

Proxies for V3_1 components without synth analog
-------------------------------------------------
  AVUS → SPYSIM            (Avantis US large core; very close to S&P)
  AVDE → VEASIM            (DM developed)
  AVEM → VWOSIM            (EM)
  AVUV → VBRSIM            (US small cap value — exact academic proxy)
  AVDV → 0.5*VEASIM+0.5*VBRSIM  (rough — no intl SCV synth available)
  SPMO → SPYSIM            (no Mom factor synth — understates ~+0.5-1pp/yr)
  IDMO → VEASIM            (same caveat)
  BTGD → GLDSIM            (no BTC synth pre-2014 — understates by ~50-200 bps/yr
                            given BTC's dominant contribution post-2014)

GDESIM and BTGD proxies impact is bounded since allocations are small
(BTGD only 5%). NTSX synth uses the testfolio-validated formula:
  NTSX_synth = 0.90 × SPYSIM + 0.60 × IEFSIM - 0.50 × CASHX
This represents: 90% S&P (no financing) + 60% Treasury futures (financed
at cash rate via -0.60 × CASH) + 10% cash collateral on margin (+0.10 × CASH)
→ net cash leg = -0.50 × CASH. Mechanically correct futures-financing model.
User validated this matches real NTSX behavior in testfolio (2026-04-26).

Citations
---------
* WisdomTree (2018). NTSX prospectus — 90% S&P 500 + 60% Treasury futures.
* Asness, Frazzini, Pedersen (2013). "Quality Minus Junk." — factor premium ranges.
* Campbell-Viceira (2010). "Bonds, Bills, and Stocks." JoF — bonds-in-consumption-currency.
* `[advances_fin_ml, p.196-202]` — bootstrap CI G6.
* `[advances_fin_ml, p.31-34]` — cross-library parity.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
TF_PATH = ROOT / "data/testfolio/cache/history.parquet"
OUT_DIR = Path(__file__).resolve().parent

TRADING_DAYS = 252
COST_BPS_INITIAL = 0.0002

# Window choice: bounded by VWOSIM inception 1994-05-04 (need EM proxy)
WINDOW_START = "1994-05-04"


# --- Synth construction ------------------------------------------------------


def returns_from_prices(p: pd.Series) -> pd.Series:
    return p.pct_change().dropna()


def synth_ntsx(r_spy: pd.Series, r_ief: pd.Series, r_cash: pd.Series) -> pd.Series:
    """NTSX = 90% SPY + 60% IEF - 0.50 × CASHX (testfolio-validated formula).

    Mechanics: 90% cash equity + 60% Treasury futures financed at cash rate
    + 10% cash collateral on margin → net cash leg = -0.50 × CASH.
    User validated 2026-04-26 that this matches real NTSX in testfolio.
    """
    common = r_spy.index.intersection(r_ief.index).intersection(r_cash.index)
    return (0.90 * r_spy.loc[common]
            + 0.60 * r_ief.loc[common]
            - 0.50 * r_cash.loc[common])


# --- Strategies --------------------------------------------------------------


def strat_v1(df: pd.DataFrame) -> pd.Series:
    """V1: 67% NTSX_synth + 33% GDESIM (real)."""
    r_spy = returns_from_prices(df["SPYSIM"])
    r_ief = returns_from_prices(df["IEFSIM"])
    r_cash = returns_from_prices(df["CASHX"])
    r_gde = returns_from_prices(df["GDESIM"])
    r_ntsx = synth_ntsx(r_spy, r_ief, r_cash)
    common = r_ntsx.index.intersection(r_gde.index)
    return (0.67 * r_ntsx.loc[common] + 0.33 * r_gde.loc[common]).rename("V1_NTSX_GDE")


def strat_v3_1(df: pd.DataFrame) -> pd.Series:
    """Plano C V3_1 v3.5 with proxies for AVUS/AVDE/AVEM/AVUV/AVDV/SPMO/IDMO/BTGD."""
    r_gde = returns_from_prices(df["GDESIM"])
    r_spy = returns_from_prices(df["SPYSIM"])    # AVUS proxy
    r_vea = returns_from_prices(df["VEASIM"])    # AVDE proxy
    r_vwo = returns_from_prices(df["VWOSIM"])    # AVEM proxy
    r_vbr = returns_from_prices(df["VBRSIM"])    # AVUV proxy (US SCV)
    r_avdv = 0.5 * r_vea + 0.5 * r_vbr            # AVDV rough mix
    r_spmo = r_spy                                 # SPMO = SPY (no Mom synth)
    r_idmo = r_vea                                 # IDMO = VEA (no Mom synth)
    r_btgd = returns_from_prices(df["GLDSIM"])    # BTGD ≈ gold (no BTC synth)

    # Portfolio weights from V3_1 v3.5 TLDR
    weights = {
        "GDE": 0.25, "AVUS": 0.12, "AVDE": 0.20, "AVEM": 0.13,
        "AVUV": 0.10, "AVDV": 0.05, "SPMO": 0.07, "IDMO": 0.03, "BTGD": 0.05,
    }
    assert abs(sum(weights.values()) - 1.0) < 1e-9, "weights must sum to 1.0"

    returns_map = {
        "GDE": r_gde, "AVUS": r_spy, "AVDE": r_vea, "AVEM": r_vwo,
        "AVUV": r_vbr, "AVDV": r_avdv, "SPMO": r_spmo, "IDMO": r_idmo, "BTGD": r_btgd,
    }
    common = None
    for r in returns_map.values():
        common = r.index if common is None else common.intersection(r.index)
    aligned = {k: r.reindex(common).fillna(0.0) for k, r in returns_map.items()}
    total = sum(weights[k] * aligned[k] for k in weights)
    return total.dropna().rename("V3_1_PlanoC")


# --- Metrics + rolling -------------------------------------------------------


def metrics(r: pd.Series, name: str = "") -> dict:
    eq = (1.0 + r).cumprod()
    years = len(r) / TRADING_DAYS
    sd = r.std(ddof=1)
    sharpe = float(np.sqrt(TRADING_DAYS) * r.mean() / sd) if sd > 0 else float("nan")
    cagr = float(eq.iloc[-1] ** (1 / years) - 1) if years > 0 else float("nan")
    mdd = float((1 - eq / eq.cummax()).max())
    return {"name": name, "n_bars": len(r), "sharpe": sharpe, "cagr": cagr, "mdd": mdd,
            "start": str(r.index[0].date()), "end": str(r.index[-1].date())}


def rolling_window_metrics(r: pd.Series, window_years: int) -> pd.DataFrame:
    """Rolling Sharpe/CAGR/MDD for window_years windows, stepped daily."""
    win = window_years * TRADING_DAYS
    if len(r) < win:
        return pd.DataFrame()
    out_idx = r.index[win - 1:]
    sharpes, cagrs, mdds = [], [], []
    arr = r.values
    for i in range(len(out_idx)):
        seg = arr[i:i + win]
        sd = seg.std(ddof=1)
        s = (np.sqrt(TRADING_DAYS) * seg.mean() / sd) if sd > 0 else np.nan
        eq = (1 + seg).cumprod()
        c = eq[-1] ** (1 / window_years) - 1
        m = (1 - eq / np.maximum.accumulate(eq)).max()
        sharpes.append(s); cagrs.append(c); mdds.append(m)
    return pd.DataFrame({"sharpe": sharpes, "cagr": cagrs, "mdd": mdds},
                        index=out_idx[:len(sharpes)])


def yearly_returns(r: pd.Series) -> pd.Series:
    return r.groupby(r.index.year).apply(lambda x: (1 + x).prod() - 1)


def stress_window(r: pd.Series, start: str, end: str) -> dict:
    seg = r.loc[start:end]
    if len(seg) == 0:
        return {"return": np.nan, "mdd": np.nan, "n_bars": 0}
    ret = (1 + seg).prod() - 1
    eq = (1 + seg).cumprod()
    mdd = (eq / eq.cummax() - 1).min()
    return {"return": float(ret), "mdd": float(mdd), "n_bars": len(seg)}


# --- Bootstrap CI ------------------------------------------------------------


def bootstrap_sharpe_ci(r: pd.Series, n_boot: int = 5000,
                        ci=(0.0005, 0.9995), seed: int = 42) -> dict:
    rng = np.random.default_rng(seed)
    n = len(r)
    block = max(1, int(np.sqrt(n)))
    arr = r.values
    out = np.empty(n_boot)
    for i in range(n_boot):
        idx = []
        while len(idx) < n:
            start = rng.integers(0, n)
            length = rng.geometric(1.0 / block)
            idx.extend(range(start, min(start + length, n)))
        idx = np.array(idx[:n])
        sample = arr[idx]
        sd = sample.std(ddof=1)
        out[i] = (np.sqrt(TRADING_DAYS) * sample.mean() / sd) if sd > 0 else 0.0
    return {"sharpe_low": float(np.quantile(out, ci[0])),
            "sharpe_high": float(np.quantile(out, ci[1])),
            "passes_g6": bool(np.quantile(out, ci[0]) > 0.0)}


# --- Main --------------------------------------------------------------------


def main() -> None:
    df = pd.read_parquet(TF_PATH)
    df.index = pd.to_datetime(df.index)
    print(f"Loaded synth: {df.index.min().date()} → {df.index.max().date()}")

    # Trim to common-data window for V3_1 (bounded by VWOSIM)
    required = ["SPYSIM", "IEFSIM", "GDESIM", "VEASIM", "VWOSIM",
                "VBRSIM", "GLDSIM", "CASHX"]
    df_aligned = df[required].dropna()
    print(f"Aligned window: {df_aligned.index.min().date()} → "
          f"{df_aligned.index.max().date()} ({len(df_aligned)} bars)")

    # Compute strategies
    r_v1 = strat_v1(df_aligned).dropna()
    r_v3 = strat_v3_1(df_aligned).dropna()

    # Align both to common dates
    common = r_v1.index.intersection(r_v3.index)
    r_v1 = r_v1.loc[common]
    r_v3 = r_v3.loc[common]
    print(f"Final common window: {common.min().date()} → {common.max().date()} "
          f"({len(common)} bars, {len(common)/TRADING_DAYS:.1f}y)")

    # Benchmark: SPYSIM same window
    r_spy = returns_from_prices(df_aligned["SPYSIM"]).reindex(common).dropna()

    # === Full-window metrics ===
    bench = metrics(r_spy, "SPYSIM b&h")
    m_v1 = metrics(r_v1, "V1_NTSX_GDE_67_33")
    m_v3 = metrics(r_v3, "V3_1_PlanoC")

    print(f"\n=== Full window ({len(common)/TRADING_DAYS:.1f}y) ===")
    for m in [bench, m_v1, m_v3]:
        print(f"  {m['name']}: Sharpe {m['sharpe']:.3f} | CAGR {m['cagr']*100:.2f}% | "
              f"MDD {m['mdd']*100:.2f}%")

    # Bootstrap CIs
    boot_v1 = bootstrap_sharpe_ci(r_v1)
    boot_v3 = bootstrap_sharpe_ci(r_v3)
    print(f"\nV1 99.9% Sharpe CI: [{boot_v1['sharpe_low']:.3f}, {boot_v1['sharpe_high']:.3f}]")
    print(f"V3_1 99.9% Sharpe CI: [{boot_v3['sharpe_low']:.3f}, {boot_v3['sharpe_high']:.3f}]")

    # === Rolling windows ===
    rolling_5y_v1 = rolling_window_metrics(r_v1, 5)
    rolling_5y_v3 = rolling_window_metrics(r_v3, 5)
    rolling_10y_v1 = rolling_window_metrics(r_v1, 10)
    rolling_10y_v3 = rolling_window_metrics(r_v3, 10)

    print(f"\n=== Rolling 5y (n={len(rolling_5y_v1)} windows) ===")
    print(f"  V1 mean Sharpe: {rolling_5y_v1['sharpe'].mean():.3f} | "
          f"V1 < V3_1 in {(rolling_5y_v1['sharpe'] < rolling_5y_v3['sharpe']).mean()*100:.1f}% windows")
    print(f"  V1 mean CAGR: {rolling_5y_v1['cagr'].mean()*100:.2f}% | "
          f"V3_1 mean CAGR: {rolling_5y_v3['cagr'].mean()*100:.2f}%")

    print(f"\n=== Rolling 10y (n={len(rolling_10y_v1)} windows) ===")
    print(f"  V1 mean Sharpe: {rolling_10y_v1['sharpe'].mean():.3f} | "
          f"V1 < V3_1 in {(rolling_10y_v1['sharpe'] < rolling_10y_v3['sharpe']).mean()*100:.1f}% windows")
    print(f"  V1 mean CAGR: {rolling_10y_v1['cagr'].mean()*100:.2f}% | "
          f"V3_1 mean CAGR: {rolling_10y_v3['cagr'].mean()*100:.2f}%")

    # === Yearly returns ===
    yr_v1 = yearly_returns(r_v1)
    yr_v3 = yearly_returns(r_v3)
    yr_spy = yearly_returns(r_spy)

    # === Stress tests ===
    stress_periods = {
        "2000_dotcom": ("2000-01-01", "2002-12-31"),
        "2008_GFC": ("2007-10-01", "2009-03-31"),
        "2011_eurozone": ("2011-05-01", "2011-12-31"),
        "2020_COVID": ("2020-02-15", "2020-04-30"),
        "2022_rate_cycle": ("2022-01-01", "2022-12-31"),
        "2008_full_year": ("2008-01-01", "2008-12-31"),
    }
    stress_results = {}
    print("\n=== Stress tests ===")
    for name, (s, e) in stress_periods.items():
        sv1 = stress_window(r_v1, s, e)
        sv3 = stress_window(r_v3, s, e)
        sspy = stress_window(r_spy, s, e)
        stress_results[name] = {"V1": sv1, "V3_1": sv3, "SPYSIM": sspy,
                                 "window": [s, e]}
        print(f"  {name} ({s} → {e}):")
        print(f"     V1     ret {sv1['return']*100:+6.2f}% | MDD {sv1['mdd']*100:+6.2f}%")
        print(f"     V3_1   ret {sv3['return']*100:+6.2f}% | MDD {sv3['mdd']*100:+6.2f}%")
        print(f"     SPYSIM ret {sspy['return']*100:+6.2f}% | MDD {sspy['mdd']*100:+6.2f}%")

    # === Save ===
    out_returns = pd.DataFrame({
        "V1_NTSX_GDE_67_33": r_v1,
        "V3_1_PlanoC": r_v3,
        "SPYSIM_bench": r_spy,
    })
    out_returns.to_parquet(OUT_DIR / "v1_vs_planoc_returns.parquet")

    rolling_5y_v1.to_parquet(OUT_DIR / "rolling_5y_v1.parquet")
    rolling_5y_v3.to_parquet(OUT_DIR / "rolling_5y_v3.parquet")
    rolling_10y_v1.to_parquet(OUT_DIR / "rolling_10y_v1.parquet")
    rolling_10y_v3.to_parquet(OUT_DIR / "rolling_10y_v3.parquet")

    out_data = {
        "window": {"start": str(common.min().date()), "end": str(common.max().date()),
                   "years": len(common) / TRADING_DAYS, "bars": len(common)},
        "metrics": {"SPYSIM_bench": bench, "V1": m_v1, "V3_1": m_v3,
                    "V1_g6": boot_v1, "V3_1_g6": boot_v3},
        "rolling_5y": {
            "V1_mean": {"sharpe": float(rolling_5y_v1["sharpe"].mean()),
                         "cagr": float(rolling_5y_v1["cagr"].mean()),
                         "mdd": float(rolling_5y_v1["mdd"].mean())},
            "V3_1_mean": {"sharpe": float(rolling_5y_v3["sharpe"].mean()),
                           "cagr": float(rolling_5y_v3["cagr"].mean()),
                           "mdd": float(rolling_5y_v3["mdd"].mean())},
            "V1_better_sharpe_pct": float((rolling_5y_v1["sharpe"] > rolling_5y_v3["sharpe"]).mean()),
            "V1_better_cagr_pct": float((rolling_5y_v1["cagr"] > rolling_5y_v3["cagr"]).mean()),
            "n_windows": len(rolling_5y_v1),
        },
        "rolling_10y": {
            "V1_mean": {"sharpe": float(rolling_10y_v1["sharpe"].mean()),
                         "cagr": float(rolling_10y_v1["cagr"].mean()),
                         "mdd": float(rolling_10y_v1["mdd"].mean())},
            "V3_1_mean": {"sharpe": float(rolling_10y_v3["sharpe"].mean()),
                           "cagr": float(rolling_10y_v3["cagr"].mean()),
                           "mdd": float(rolling_10y_v3["mdd"].mean())},
            "V1_better_sharpe_pct": float((rolling_10y_v1["sharpe"] > rolling_10y_v3["sharpe"]).mean()),
            "V1_better_cagr_pct": float((rolling_10y_v1["cagr"] > rolling_10y_v3["cagr"]).mean()),
            "n_windows": len(rolling_10y_v1),
        },
        "yearly_returns": {
            "V1": {str(y): float(v) for y, v in yr_v1.items()},
            "V3_1": {str(y): float(v) for y, v in yr_v3.items()},
            "SPYSIM": {str(y): float(v) for y, v in yr_spy.items()},
        },
        "stress_tests": stress_results,
    }
    out_json = OUT_DIR / "V1_VS_PLANOC_VALIDATION.json"
    out_json.write_text(json.dumps(out_data, indent=2, default=str))
    print(f"\nWrote {out_json}")


if __name__ == "__main__":
    main()
