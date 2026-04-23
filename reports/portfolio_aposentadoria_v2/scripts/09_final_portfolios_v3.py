"""V3 carteiras finais — redesenhadas pós feedback 2026-04-23:

1. Bonds sleeve agora em BRL (B5P211 / IMAB11 / LFTS11 / DINF11) em vez de
   US Treasuries (TLT/IEF/SHV). Fundamentação: Campbell-Viceira 2010, PWL
   Capital, Vanguard 2018/2023 — bonds devem ser na moeda de consumo.
2. Gold/BTC sleeve expandido com return-stacking: GDE (90%SPX+90%gold,
   inception 2022), BTGD (100%BTC+100%gold, inception 2024), RSSX
   (100%SPX+100%gold/BTC, inception 2025). ISBG descartado (muito novo,
   AUM <$5M, option-heavy).
3. NTSX family ainda usada como core (90%eq+60%Treasury é capital
   efficiency, bonds internos como overlay — não violação do princípio
   home-currency se entender como "instrumento" em vez de "asset class").

Fee model atualizado:
- BR FI ETFs: ER + 15% capital gains on sale ≈ 0.40-0.80%/ano drag
- DINF11: ER 0.60% + 0% tax (isento Lei 12.431) = 0.60%
- GDE: ER 0.20% (pré-dividend); baixo drag (gold no dividend, equity low yield)
- BTGD/RSSX: ER 1.0%+ + 15% DARF BR
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

# ---------------------------------------------------------------------------
# Extended fee table v3
# ---------------------------------------------------------------------------
FEES_V3 = {
    # BR Fixed Income (ER + ~0.2% tax drag on annual realization; zero for DINF11)
    "B5P211": 0.0040, "IMAB11": 0.0045, "LFTS11": 0.0040, "DEBB11": 0.0080,
    "DINF11": 0.0060, "FIXA11": 0.0050,
    "BOVA11": 0.0055,  # BR equity ref
    "IVVB11": 0.0050,  # BR-listed S&P
    # BR FI long-history proxy — CDI wealth index (15% tax on capital gains;
    # no come-cotas; assume 0.3% annual drag for deferred realization)
    "CDI_BR": 0.0030,
    # New stacked alts
    "GDE": 0.0030,     # ER 0.20% + minimal dividends (gold 0, equity low)
    "RSSX": 0.0080,    # ER 0.68% + futures contango drag
    "BTGD": 0.0130,    # ER 1.05% + futures drag
    # Synthetic long-history proxies (no fees applied — pure math)
    "GDE_syn": 0.0030, "BTGD_syn": 0.0000, "RSSX_syn": 0.0000,
    "BTC_USD": 0.0000,
}


# ---------------------------------------------------------------------------
# 4 final portfolios v3
# ---------------------------------------------------------------------------
FINAL_V3 = {
    # --------------- Portfolio 1 v3: Max CAGR ---------------
    # Max leverage via GDE (equity+gold stacked) + NTSX family + SSO extra.
    # No BR FI (opportunity cost — FI drags CAGR).
    "FINAL_V3_1_MAX_CAGR": {
        "name": "Leveraged Growth Engine v3.4 (Max CAGR)",
        "objective": "maximize 30y CAGR; accept historical MDD up to ~50%",
        "weights_real": {
            "GDE": 0.25,    # 90% SPX + 90% gold stacked — reduzido de 30 pra diminuir gold notional
            "AVUS": 0.12,   # US core (Avantis, com tilts modestos) — preenche equity US
            "NTSI": 0.20,   # Int 90/60 stacked
            "NTSE": 0.08,   # EM 90/60 stacked
            "AVEM": 0.05,   # EM core (com tilts Avantis; sem Momentum)
            "AVUV": 0.10,   # US SCV
            "AVDV": 0.05,   # Int SCV (15% total SCV)
            "SPMO": 0.07,   # US Momentum
            "IDMO": 0.03,   # Int Momentum (10% total Mom — 25% factor total 60/40 SCV/Mom)
            "BTGD": 0.05,   # BTC+gold stacked (única fonte de BTC; tudo stacked)
        },
        "weights_proxy": {
            "GDE_syn": 0.25,           # GDE real (2004+ via sintético)
            "AVUS_syn_3f": 0.12,       # AVUS syn via Fama-French (1926+)
            "NTSI_syn": 0.20,          # NTSI syn = 0.9*VEA + 0.6*IEF (2007+)
            "NTSE_syn": 0.08,          # NTSE syn = 0.9*VWO + 0.6*IEF (2006+)
            "VWO": 0.05,               # AVEM proxy
            "AVUV_syn_3f": 0.17,       # AVUV (10) + SPMO (7) lumped
            "VEA": 0.08,               # AVDV (5) + IDMO (3) lumped
            "BTGD_syn": 0.05,          # BTGD syn (2014+)
        },
        "embedded_leverage_approx": 1.39,
        "rationale": (
            "v3.4 redesign (2026-04-23 final): CONSOLIDAÇÃO de gold/BTC via "
            "stacking puro — removido GLDM 10% e IBIT 2% standalone. Tudo que "
            "envolve gold/BTC agora via GDE (stacked eq+gold) ou BTGD (stacked "
            "BTC+gold). Gold notional reduzido de 40% pra 27,5%. "
            "GEOGRAFIA: target US/DM/EM = 55/30/15 (Plano C original), "
            "atingido via GDE 25 + AVUS 12 + AVUV 10 + SPMO 7 (US 55%), "
            "NTSI 20 + AVDV 5 + IDMO 3 (DM 28%), NTSE 8 + AVEM 5 (EM 13%). "
            "FACTOR TILT: 25% total (15% SCV + 10% Mom, ratio 60/40 AQR-optimal). "
            "Trade-off vs v3.3 (30% factor + heavy gold): -1.9pp CAGR backtest "
            "2014-26 (preço do gold reduzido + mais broad US). Leverage 1.39× "
            "tudo via stacked overlay descorrelacionado."
        ),
    },

    # --------------- Portfolio 2 v3: Max Sharpe ---------------
    # Heavy BR FI (home-currency bonds) + GDE + DBMF/KMLM diversifier.
    "FINAL_V3_2_MAX_SHARPE": {
        "name": "Diversified Factor + BR FI v3 (Max Sharpe)",
        "objective": "maximize Sharpe; accept CAGR cost for better path",
        "weights_real": {
            "GDE": 0.20,      # equity + gold stacked
            "NTSI": 0.10,     # Int capital efficient
            "AVUV": 0.10,
            "AVDV": 0.05,
            "DBMF": 0.10,     # US MF
            "KMLM": 0.05,     # 2nd MF
            "B5P211": 0.15,   # BR IPCA+ short (stabilizer)
            "IMAB11": 0.10,   # BR IPCA+ long (duration)
            "DINF11": 0.10,   # BR debênture isenta (tax-efficient)
            "GLDM": 0.05,
        },
        "weights_proxy": {
            "GDE_syn": 0.20,
            "NTSX_syn": 0.10,
            "AVUV_syn_3f": 0.10,
            "VEA": 0.05,
            "CDI_BR": 0.35,  # BR FI combined proxy (B5P211+IMAB11+DINF11)
            "GLD": 0.20,     # crisis-alpha proxy (DBMF+KMLM+GLDM combined)
        },
        "embedded_leverage_approx": 1.25,
        "rationale": (
            "Home-currency bonds 35% (B5P211+IMAB11+DINF11). GDE 20% capital "
            "efficient equity+gold. 15% managed futures as crisis alpha. "
            "Factor tilt 15%. Gold 5% extra. FI denominado em BRL elimina FX "
            "risk sobre stabilizer; DINF11 é isento IR. Target Sharpe 0.65-0.80."
        ),
    },

    # --------------- Portfolio 3 v3: Max TW/MDD≤50% ---------------
    # Middle ground: factor tilts + some BR FI + gold stacking.
    "FINAL_V3_3_MAX_TW_MDD50": {
        "name": "Bounded Growth + BR FI v3 (Max TW, MDD ≤ 50%)",
        "objective": "maximize p50 terminal wealth; historical MDD ≤ 50%",
        "weights_real": {
            "GDE": 0.20,
            "NTSI": 0.15,
            "NTSE": 0.05,
            "AVUV": 0.15,
            "AVDV": 0.10,
            "AVEM": 0.05,
            "SPMO": 0.05,
            "DBMF": 0.05,
            "B5P211": 0.10,   # BR IPCA+ short
            "IMAB11": 0.05,   # BR IPCA+ long
            "DINF11": 0.03,   # BR isenta
            "GLDM": 0.02,
        },
        "weights_proxy": {
            "GDE_syn": 0.20,
            "NTSX_syn": 0.20,         # NTSI+NTSE
            "AVUV_syn_3f": 0.20,      # AVUV+SPMO
            "VEA": 0.10,              # AVDV
            "VWO": 0.05,              # AVEM
            "CDI_BR": 0.18,           # BR FI combined
            "GLD": 0.07,              # DBMF+GLDM
        },
        "embedded_leverage_approx": 1.35,
        "rationale": (
            "Strong factor tilt 35%, NTSX family 40% capital efficient core, "
            "BR FI 18%, MF 5%, gold 2%. Target CAGR 9-10% com MDD 30-45%. "
            "BR FI pequena o suficiente pra não drag CAGR, suficiente pra "
            "rebalancear na queda de equity."
        ),
    },

    # --------------- Portfolio 4 v3: Max SWR (retirement) ---------------
    # Heavy BR FI (stabilizer) + small equity + gold. NO US bonds.
    "FINAL_V3_4_MAX_SWR": {
        "name": "Retirement Income BR v3 (Max SWR)",
        "objective": "maximize 30y SWR at 95%; end-state of glidepath",
        "weights_real": {
            "GDE": 0.15,
            "AVUV": 0.08,
            "AVDV": 0.05,
            "DBMF": 0.10,
            "KMLM": 0.05,
            "B5P211": 0.20,   # BR IPCA+ short (dominant stabilizer)
            "IMAB11": 0.15,   # BR IPCA+ long (income duration)
            "LFTS11": 0.10,   # BR Selic cash buffer
            "DINF11": 0.07,   # BR isenta (free tax)
            "GLDM": 0.05,
        },
        "weights_proxy": {
            "GDE_syn": 0.15,
            "AVUV_syn_3f": 0.08,
            "VEA": 0.05,
            "CDI_BR": 0.52,         # BR FI heavy (B5P211+IMAB11+LFTS11+DINF11)
            "GLD": 0.20,            # MF proxy + GLDM
        },
        "embedded_leverage_approx": 1.15,
        "rationale": (
            "BR FI 52% (stabilizer + income). Equity ~40% effective via GDE. "
            "Gold 25% (via GLD proxy incl MF). Factor tilt 13% residual. "
            "Zero US bonds — Campbell-Viceira + Vanguard + PWL all agree. "
            "Target SWR 4-5%; MDD ≤ 20% em BRL terms."
        ),
    },
}


def run(panel: pd.DataFrame) -> dict:
    results = {}
    WINDOWS = {
        "real_recent":  ("2023-01-31", "2026-03-31", "real_etf"),   # real ETFs only
        "syn_2007_2026": ("2007-07-31", "2026-03-31", "proxy"),     # common window
        "syn_long_2000": ("2000-02-28", "2026-03-31", "proxy"),     # 26-year with CDI
    }

    for pid, p in FINAL_V3.items():
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
        tr, tp = sum(p["weights_real"].values()), sum(p["weights_proxy"].values())
        assert abs(tr - 1.0) < 1e-6, f"{pid} real {tr}"
        assert abs(tp - 1.0) < 1e-6, f"{pid} proxy {tp}"

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
            actual_start = sub_clean.index.min().strftime("%Y-%m-%d")
            actual_end = sub_clean.index.max().strftime("%Y-%m-%d")
            try:
                config = pm.SimConfig(
                    start=actual_start, end=actual_end, initial_wealth=10_000.0,
                    rebalance="monthly",
                    use_letf_proxy_fees=(which == "proxy"),
                    fees_override=FEES_V3,
                )
                r = pm.simulate(weights, panel, config)
                entry["backtests"][wk] = {
                    "status": "OK",
                    "actual_start": actual_start, "actual_end": actual_end,
                    "cagr": r.cagr, "vol": r.vol_ann, "sharpe": r.sharpe,
                    "mdd": r.max_dd, "worst_12m": r.worst_12m,
                    "terminal_10k": r.terminal_wealth, "n_months": int(len(r.returns)),
                }
                print(f"  {wk:16s}: [{actual_start}→{actual_end}] "
                      f"CAGR={r.cagr:.2%} Sharpe={r.sharpe:.2f} MDD={r.max_dd:.2%} vol={r.vol_ann:.2%}")
            except Exception as e:
                entry["backtests"][wk] = {"status": "ERROR", "error": str(e)}

        # SWR + bootstrap (first working window with enough data)
        for wk, (start, end, which) in WINDOWS.items():
            weights = p["weights_proxy"] if which == "proxy" else p["weights_real"]
            missing = [a for a in weights if a not in panel.columns]
            if missing:
                continue
            sub = panel[list(weights)].loc[start:end]
            sub_clean = sub.dropna(how="any")
            if len(sub_clean) < 60:
                continue
            actual_start = sub_clean.index.min().strftime("%Y-%m-%d")
            actual_end = sub_clean.index.max().strftime("%Y-%m-%d")
            try:
                cfg = pm.SimConfig(start=actual_start, end=actual_end,
                                   initial_wealth=10_000.0, rebalance="monthly",
                                   use_letf_proxy_fees=(which == "proxy"),
                                   fees_override=FEES_V3)
                r = pm.simulate(weights, panel, cfg)
                wr, diag = pm.swr_test(r.returns, horizon_years=30,
                                        initial_wealth=1_000_000, n_paths=2000,
                                        success_threshold=0.95, block_size=12)
                entry["swr"] = {"window": wk, "swr_95pct": float(wr),
                                "success_at_swr": float(diag["success_rate_at_wr"])}
                paths = pm.block_bootstrap_paths(r.returns, n_paths=2000,
                                                  horizon_months=360, block_size=12)
                terminals, mdds = [], []
                for i in range(paths.shape[0]):
                    w_ = 10_000; peak = w_; path_dd = 0.0
                    for t in range(paths.shape[1]):
                        w_ = w_ * (1 + paths[i, t]) + 1_000
                        peak = max(peak, w_); path_dd = min(path_dd, (w_ - peak) / peak)
                    terminals.append(w_); mdds.append(path_dd)
                terminals = np.array(terminals); mdds = np.array(mdds)
                entry["bootstrap"] = {
                    "window": wk, "initial_wealth": 10_000, "monthly_contrib": 1_000,
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
                print(f"  SWR: {wr:.2%}  Bootstrap 30y: "
                      f"p25=${tw['p25']/1e6:.2f}M p50=${tw['p50']/1e6:.2f}M "
                      f"p95=${tw['p95']/1e6:.2f}M  "
                      f"P(MDD>50%)={entry['bootstrap']['prob_mdd_gt_50pct']:.1%}")
                break
            except Exception as e:
                entry["swr"] = {"status": "ERROR", "error": str(e)}
        results[pid] = entry
    return results


if __name__ == "__main__":
    panel = pd.read_parquet(DATA_DIR / "returns_monthly.parquet")
    print(f"Panel loaded: {panel.shape}")
    results = run(panel)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUT_DIR / "final_portfolios_v3.json").open("w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nWrote {OUT_DIR}/final_portfolios_v3.json")
