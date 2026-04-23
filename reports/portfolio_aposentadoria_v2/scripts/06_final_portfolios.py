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
# 4 Final optimized portfolios
# ============================================================================
FINAL = {
    # ---------- Portfolio 1: Max CAGR (accumulation, accept any MDD) ----------
    "FINAL_1_MAX_CAGR": {
        "name": "Leveraged Growth Engine (Max CAGR)",
        "objective": "maximize expected 30-year CAGR; accept historical MDD up to ~60%",
        "weights_real": {
            "NTSX": 0.30,   # 1.5x US 90/60
            "NTSI": 0.15,   # 1.5x DM 90/60
            "RSST": 0.15,   # 100/100 US stocks + MF (leveraged diversifier)
            "AVUV": 0.15,   # SCV tilt
            "AVDV": 0.10,   # Int SCV
            "AVEM": 0.05,   # EM
            "SPMO": 0.05,   # Momentum tilt (US)
            "IBIT": 0.03,
            "GLDM": 0.02,
        },
        "weights_proxy": {
            "NTSX_syn": 0.45,            # NTSX + NTSI combined proxy (no long syn for NTSI)
            "RSST_syn": 0.15,            # short history — use synthetic (2019+)
            "AVUV_syn_3f": 0.15,
            "AVDV": 0.10,                # AVDV real only (2019+)
            "VWO": 0.10,                 # AVEM + SPMO combined proxy
            "GLD": 0.05,                 # IBIT + GLDM combined proxy
        },
        "embedded_leverage_approx": 1.55,  # 90/60 NTSX + 100/100 RSST
        "rationale": (
            "NTSX + NTSI = 45% gives 1.5x capital efficiency on 60/40 beta; "
            "RSST stacks MF on top of US equity (uncorrelated return stream); "
            "35% factor tilts (AVUV+AVDV+AVEM+SPMO); 5% alts. "
            "Embedded leverage ~1.55x. Expected CAGR vs SPY: +2-3pp with modest Sharpe gain."
        ),
    },

    # ---------- Portfolio 2: Max Sharpe (risk-adjusted) ----------
    "FINAL_2_MAX_SHARPE": {
        "name": "Risk Parity with Factor Tilt (Max Sharpe)",
        "objective": "maximize Sharpe ratio; accept CAGR cost for better path",
        "weights_real": {
            "NTSX": 0.25,   # embedded 60/40 US
            "NTSI": 0.15,   # embedded 60/40 DM
            "NTSE": 0.05,   # embedded 60/40 EM
            "AVUV": 0.10,   # SCV
            "AVDV": 0.05,
            "RSBT": 0.15,   # 100/100 bonds + MF — dominant diversifier
            "DBMF": 0.10,   # pure MF as second diversifier
            "GLDM": 0.10,   # gold as tail hedge
            "TLT": 0.05,    # long bonds direct
        },
        "weights_proxy": {
            "NTSX_syn": 0.45,           # all NTSX family
            "AVUV_syn_3f": 0.10,
            "AVDV": 0.05,
            "TLT": 0.20,                # RSBT + direct TLT proxy
            "SPY_1x_sim": 0.10,         # DBMF long-run proxy (imperfect)
            "GLD": 0.10,
        },
        "embedded_leverage_approx": 1.35,
        "rationale": (
            "Heavy diversification via RSBT (bonds + MF stacked) and direct DBMF. "
            "Embedded leverage 1.35x mainly from NTSX family. Lower equity beta, "
            "higher MF exposure. Target Sharpe 0.60+ on 20yr data."
        ),
    },

    # ---------- Portfolio 3: Max terminal wealth with MDD ≤ 50% ----------
    "FINAL_3_MAX_TW_MDD50": {
        "name": "Bounded Growth (Max Terminal Wealth, MDD ≤ 50%)",
        "objective": "maximize p50 terminal wealth subject to historical MDD ≤ 50%",
        "weights_real": {
            "NTSX": 0.25,
            "NTSI": 0.15,
            "NTSE": 0.08,
            "AVUV": 0.12,
            "AVDV": 0.08,
            "AVEM": 0.05,
            "SPMO": 0.05,   # momentum tilt (US)
            "RSBT": 0.08,   # MF + bonds stack
            "DBMF": 0.05,   # direct MF
            "GLDM": 0.05,
            "IBIT": 0.02,
            "TLT": 0.02,
        },
        "weights_proxy": {
            "NTSX_syn": 0.48,           # NTSX + NTSI + NTSE proxy
            "AVUV_syn_3f": 0.12,
            "AVDV": 0.08,
            "VWO": 0.10,                # AVEM + SPMO proxy
            "TLT": 0.05,                # RSBT + TLT direct
            "SPY_1x_sim": 0.05,         # DBMF proxy
            "GLD": 0.10,                # GLDM + IBIT proxy
            "IEF": 0.02,
        },
        "embedded_leverage_approx": 1.30,
        "rationale": (
            "Middle ground: more factor tilt than Portfolio 2, less leverage than "
            "Portfolio 1. Diversified across geographies + factors + MF + alts. "
            "Target MDD < 50% in historical backtest + bootstrap; target CAGR 8-9%."
        ),
    },

    # ---------- Portfolio 4: Max SWR (retirement phase) ----------
    "FINAL_4_MAX_SWR": {
        "name": "Retirement Income Optimizer (Max SWR)",
        "objective": "maximize 30-year SWR at 95% success; end-state of glidepath",
        "weights_real": {
            "NTSX": 0.18,   # lower equity but still levered core
            "NTSI": 0.10,
            "AVUV": 0.08,
            "AVDV": 0.05,
            "DBMF": 0.15,   # heavy MF for crisis alpha
            "KMLM": 0.05,   # second MF with different index (diversify MF itself)
            "RSBT": 0.08,
            "TLT": 0.08,
            "IEF": 0.12,
            "SHV": 0.05,    # near-cash for withdrawal buffer
            "GLDM": 0.05,
            "IBIT": 0.01,
        },
        "weights_proxy": {
            "NTSX_syn": 0.28,
            "AVUV_syn_3f": 0.08,
            "AVDV": 0.05,
            "SPY_1x_sim": 0.20,         # MF long-run proxy (DBMF + KMLM + RSBT partial)
            "TLT": 0.08,
            "IEF": 0.12,
            "SHV": 0.05,
            "GLD": 0.14,
        },
        "embedded_leverage_approx": 1.15,
        "rationale": (
            "End-state retirement allocation: equity ~45% effective (via NTSX), "
            "bonds 25%, MF 28% (heavy), alts 6%, cash 5% buffer. "
            "Target: SWR 4-4.5% at 95% success over 30y retirement. "
            "Not suitable for accumulation — too defensive."
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
            if sub.notna().mean().min() < 0.85:
                entry["backtests"][wk] = {"status": "INSUFFICIENT"}
                continue
            try:
                config = pm.SimConfig(
                    start=start, end=end, initial_wealth=10_000.0, rebalance="monthly",
                    use_letf_proxy_fees=(which == "proxy"),
                )
                r = pm.simulate(weights, panel, config)
                entry["backtests"][wk] = {
                    "status": "OK",
                    "cagr": r.cagr, "vol": r.vol_ann, "sharpe": r.sharpe,
                    "mdd": r.max_dd, "worst_12m": r.worst_12m,
                    "terminal_10k": r.terminal_wealth, "n_months": int(len(r.returns)),
                }
                print(f"  {wk:20s}: CAGR={r.cagr:.2%} Sharpe={r.sharpe:.2f} "
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
            if sub.notna().mean().min() < 0.85:
                continue
            # Use this window
            try:
                config = pm.SimConfig(start=start, end=end, initial_wealth=10_000.0,
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
