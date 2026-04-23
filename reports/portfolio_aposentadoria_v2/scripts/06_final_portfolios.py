"""The 4 final optimized portfolios, one per objective function.

These are synthesized from the learnings of the candidate backtests in
script 05. Each is hand-optimized within constraints:

- Use return stacking (NTSX family + Return Stacked ETFs) over raw LETFs
  wherever possible
- Keep factor tilts on equity sleeve (AVUV/AVDV/AVEM)
- Use managed futures (DBMF/KMLM + embedded in RSST/RSBT) as diversifier
- Gold/BTC as tail hedge in measured doses
"""
from __future__ import annotations

import json
import sys
from importlib import import_module
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

pm = import_module("03_portfolio_sim")

REPO = Path("/var/www/pessoal/ai-trade")
DATA_DIR = REPO / "reports" / "portfolio_aposentadoria_v2" / "data"
OUT_DIR = REPO / "reports" / "portfolio_aposentadoria_v2" / "results"


# ============================================================================
# 4 Final optimized portfolios (redesigned 2026-04-23 after user caught
# CAGR-ordering inconsistency: FINAL_3 had higher CAGR than FINAL_1).
# Root causes addressed:
#   1. Fixed NaN-fill bug in daily_to_monthly (02_build_returns_panel.py)
#   2. Redesigned proxy weights to use ONLY long-history assets (no RSST_syn
#      which truncated window to 2019+)
#   3. Made portfolios more structurally differentiated (leverage/diversification)
# ============================================================================
FINAL = {
    # ---------- Portfolio 1: Max CAGR ----------
    # Design: HEAVY leverage (NTSX + raw SSO/QLD) + factor tilts.
    # NO managed futures (MF dilutes CAGR in bull periods).
    "FINAL_1_MAX_CAGR": {
        "name": "Leveraged Growth Engine (Max CAGR)",
        "objective": "maximize expected 30-year CAGR; accept historical MDD up to ~60%",
        "weights_real": {
            "NTSX": 0.25,
            "NTSI": 0.15,
            "SSO": 0.15,
            "QLD": 0.05,
            "AVUV": 0.15,
            "AVDV": 0.10,
            "AVEM": 0.05,
            "SPMO": 0.05,
            "IBIT": 0.03,
            "GLDM": 0.02,
        },
        "weights_proxy": {
            "NTSX_syn": 0.40,
            "SPY_2x_sim": 0.20,
            "AVUV_syn_3f": 0.15,
            "VEA": 0.10,
            "VWO": 0.10,
            "GLD": 0.05,
        },
        "embedded_leverage_approx": 1.65,
        "rationale": (
            "Aggressive leverage: NTSX family 40% (1.5x US+DM) + SSO+QLD 20% "
            "(proxy SPY_2x 20% at 2x) = high equity beta. Factor tilts 35% "
            "(AVUV+AVDV+AVEM+SPMO). 5% alts. NO managed futures — MF dilutes "
            "CAGR. Embedded leverage ~1.65x."
        ),
    },

    # ---------- Portfolio 2: Max Sharpe ----------
    # Design: heavy bond/gold diversification via NTSX + direct TLT/IEF + GLD.
    # No raw LETF (adds vol without adding Sharpe).
    "FINAL_2_MAX_SHARPE": {
        "name": "Risk-Parity Factor Core (Max Sharpe)",
        "objective": "maximize Sharpe ratio; accept CAGR cost for better path",
        "weights_real": {
            "NTSX": 0.30,
            "NTSI": 0.15,
            "AVUV": 0.08,
            "AVDV": 0.05,
            "RSBT": 0.10,
            "DBMF": 0.07,
            "TLT": 0.10,
            "IEF": 0.10,
            "GLDM": 0.05,
        },
        "weights_proxy": {
            "NTSX_syn": 0.45,
            "AVUV_syn_3f": 0.08,
            "VEA": 0.05,
            "TLT": 0.17,
            "IEF": 0.15,
            "GLD": 0.10,
        },
        "embedded_leverage_approx": 1.27,
        "rationale": (
            "Diversification-first. NTSX family 45% (1.5x 60/40); direct bonds "
            "17% TLT + 10% IEF for duration extension; gold 10% tail hedge. "
            "No raw LETF — vol hurts Sharpe. Target Sharpe 0.6-0.75."
        ),
    },

    # ---------- Portfolio 3: Max TW with MDD ≤ 50% ----------
    # Middle ground. Strong factor tilt + moderate leverage.
    "FINAL_3_MAX_TW_MDD50": {
        "name": "Bounded Growth (Max TW, MDD ≤ 50%)",
        "objective": "maximize p50 terminal wealth subject to historical MDD ≤ 50%",
        "weights_real": {
            "NTSX": 0.30,
            "NTSI": 0.15,
            "NTSE": 0.05,
            "AVUV": 0.15,
            "AVDV": 0.10,
            "AVEM": 0.05,
            "SPMO": 0.05,
            "RSBT": 0.05,
            "DBMF": 0.03,
            "TLT": 0.04,
            "GLDM": 0.03,
        },
        "weights_proxy": {
            "NTSX_syn": 0.50,
            "AVUV_syn_3f": 0.15,
            "VEA": 0.10,
            "VWO": 0.10,
            "TLT": 0.09,
            "GLD": 0.06,
        },
        "embedded_leverage_approx": 1.40,
        "rationale": (
            "Middle ground. Strong factor tilt (35% SCV+Momentum+EM), NTSX family "
            "core 50% = 1.4x effective. Modest bond+MF+gold buffer ~15%. "
            "Target CAGR 8-10% with MDD 30-45%."
        ),
    },

    # ---------- Portfolio 4: Max SWR (retirement end-state) ----------
    "FINAL_4_MAX_SWR": {
        "name": "Retirement Income Optimizer (Max SWR)",
        "objective": "maximize 30-year SWR at 95% success; end-state of glidepath",
        "weights_real": {
            "NTSX": 0.20,
            "NTSI": 0.08,
            "AVUV": 0.06,
            "AVDV": 0.04,
            "DBMF": 0.10,
            "KMLM": 0.05,
            "RSBT": 0.05,
            "TLT": 0.10,
            "IEF": 0.15,
            "SHV": 0.08,
            "GLDM": 0.08,
            "IBIT": 0.01,
        },
        "weights_proxy": {
            "NTSX_syn": 0.28,
            "AVUV_syn_3f": 0.06,
            "VEA": 0.04,
            "TLT": 0.15,
            "IEF": 0.27,
            "GLD": 0.20,
        },
        "embedded_leverage_approx": 1.12,
        "rationale": (
            "End-state retirement. Equity ~45% effective (NTSX + direct), "
            "bonds 30%, cash 12%, gold 20%, factor tilt 10%. Low vol (~7-9%), "
            "low MDD (~15-25%), target SWR 4-5% at 95%. NOT for accumulation."
        ),
    },
}


def run_final(panel: pd.DataFrame) -> dict:
    """Run all 4 finals across windows + SWR + bootstrap."""
    from importlib import import_module
    cand = import_module("04_candidate_portfolios")

    results = {}
    WINDOWS = {
        "real_2020_2026": ("2020-01-31", "2026-03-31", "real_etf"),
        "syn_2006_2026":  ("2006-02-28", "2026-03-31", "proxy"),
        "syn_long_1926":  ("1926-07-31", "2026-02-28", "proxy"),
    }

    for pid, p in FINAL.items():
        print(f"\n=== {pid}: {p['name']} ===")
        entry = {
            "name": p["name"],
            "objective": p["objective"],
            "weights_real": p["weights_real"],
            "weights_proxy": p["weights_proxy"],
            "embedded_leverage_approx": p["embedded_leverage_approx"],
            "rationale": p["rationale"],
            "backtests": {},
            "swr": None,
            "bootstrap": None,
        }
        total_r = sum(p["weights_real"].values())
        total_p = sum(p["weights_proxy"].values())
        assert abs(total_r - 1.0) < 1e-6, f"{pid} real weights don't sum to 1: {total_r}"
        assert abs(total_p - 1.0) < 1e-6, f"{pid} proxy weights don't sum to 1: {total_p}"

        for wk, (start, end, which) in WINDOWS.items():
            weights = p["weights_real"] if which == "real_etf" else p["weights_proxy"]
            missing = [a for a in weights if a not in panel.columns]
            if missing:
                entry["backtests"][wk] = {"status": "MISSING", "missing": missing}
                continue
            sub = panel[list(weights)].loc[start:end]
            sub_clean = sub.dropna(how="any")
            if len(sub_clean) < 24:
                entry["backtests"][wk] = {"status": "INSUFFICIENT",
                                          "months_after_intersect": int(len(sub_clean))}
                continue
            try:
                actual_start = sub_clean.index.min().strftime("%Y-%m-%d")
                actual_end = sub_clean.index.max().strftime("%Y-%m-%d")
                config = pm.SimConfig(
                    start=actual_start, end=actual_end, initial_wealth=10_000.0,
                    rebalance="monthly",
                    use_letf_proxy_fees=(which == "proxy"),
                )
                r = pm.simulate(weights, panel, config)
                entry["backtests"][wk] = {
                    "status": "OK",
                    "actual_start": actual_start, "actual_end": actual_end,
                    "cagr": r.cagr, "vol": r.vol_ann, "sharpe": r.sharpe,
                    "mdd": r.max_dd, "worst_12m": r.worst_12m,
                    "terminal_10k": r.terminal_wealth, "n_months": int(len(r.returns)),
                }
                print(f"  {wk:20s}: [{actual_start}→{actual_end}] "
                      f"CAGR={r.cagr:.2%} Sharpe={r.sharpe:.2f} "
                      f"MDD={r.max_dd:.2%} vol={r.vol_ann:.2%}")
            except Exception as e:
                entry["backtests"][wk] = {"status": "ERROR", "error": str(e)}

        # SWR using best-available window
        for wk, (start, end, which) in WINDOWS.items():
            weights = p["weights_proxy"] if which == "proxy" else p["weights_real"]
            missing = [a for a in weights if a not in panel.columns]
            if missing:
                continue
            sub = panel[list(weights)].loc[start:end]
            sub_clean = sub.dropna(how="any")
            if len(sub_clean) < 60:  # need ≥5y for meaningful SWR bootstrap
                continue
            actual_start = sub_clean.index.min().strftime("%Y-%m-%d")
            actual_end = sub_clean.index.max().strftime("%Y-%m-%d")
            try:
                config = pm.SimConfig(start=actual_start, end=actual_end,
                                      initial_wealth=10_000.0,
                                      rebalance="monthly",
                                      use_letf_proxy_fees=(which == "proxy"))
                r = pm.simulate(weights, panel, config)
                wr, diag = pm.swr_test(r.returns, horizon_years=30, initial_wealth=1_000_000,
                                       n_paths=2000, success_threshold=0.95, block_size=12)
                entry["swr"] = {
                    "window": wk, "swr_95pct": float(wr),
                    "success_at_swr": float(diag["success_rate_at_wr"]),
                }
                print(f"  SWR (95%, 30y, {wk}): {wr:.2%}")

                # Bootstrap terminal wealth
                paths = pm.block_bootstrap_paths(r.returns, n_paths=2000,
                                                  horizon_months=360, block_size=12)
                terminals, mdds = [], []
                for i in range(paths.shape[0]):
                    w = 10_000
                    peak = w
                    path_dd = 0.0
                    for t in range(paths.shape[1]):
                        w = w * (1 + paths[i, t]) + 1_000
                        peak = max(peak, w)
                        path_dd = min(path_dd, (w - peak) / peak)
                    terminals.append(w)
                    mdds.append(path_dd)
                terminals = np.array(terminals)
                mdds = np.array(mdds)
                entry["bootstrap"] = {
                    "window": wk,
                    "initial_wealth": 10_000,
                    "monthly_contrib": 1_000,
                    "horizon_years": 30,
                    "terminal_wealth": {
                        "p05": float(np.percentile(terminals, 5)),
                        "p25": float(np.percentile(terminals, 25)),
                        "p50": float(np.percentile(terminals, 50)),
                        "p75": float(np.percentile(terminals, 75)),
                        "p95": float(np.percentile(terminals, 95)),
                        "mean": float(np.mean(terminals)),
                    },
                    "mdd_distribution": {
                        "p05": float(np.percentile(mdds, 5)),
                        "p50": float(np.percentile(mdds, 50)),
                        "p95": float(np.percentile(mdds, 95)),
                    },
                    "prob_mdd_gt_50pct": float((mdds < -0.50).mean()),
                    "prob_mdd_gt_70pct": float((mdds < -0.70).mean()),
                }
                tw = entry["bootstrap"]["terminal_wealth"]
                print(f"  Bootstrap 30y terminal (10k + 1k/mo): "
                      f"p25=${tw['p25']/1e6:.2f}M p50=${tw['p50']/1e6:.2f}M "
                      f"p95=${tw['p95']/1e6:.2f}M")
                print(f"  P(MDD > 50%) = {entry['bootstrap']['prob_mdd_gt_50pct']:.1%}")
                break  # use first working window
            except Exception as e:
                entry["swr"] = {"status": "ERROR", "error": str(e)}
        results[pid] = entry

    return results


if __name__ == "__main__":
    panel = pd.read_parquet(DATA_DIR / "returns_monthly.parquet")
    print(f"Panel loaded: {panel.shape}")
    results = run_final(panel)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUT_DIR / "final_portfolios.json").open("w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nWrote {OUT_DIR}/final_portfolios.json")
