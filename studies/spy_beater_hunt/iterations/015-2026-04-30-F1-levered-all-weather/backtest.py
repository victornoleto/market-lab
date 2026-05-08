"""Iter 015 driver: F1 Levered All-Weather (Dalio risk-parity, NEW 7th family).

Post-impossibility 7th-architectural-family sanity check on KILL #33
(architectural ceiling at 67). Tests the BALANCED-MULTI-ASSET (stocks +
bonds + gold + managed-futures) family — the most literature-canonical
risk-parity architecture (Dalio Bridgewater All-Weather + Asness 1996
"Why Not 100% Equities?") — which has not been explicitly tested in any
prior spy_beater iter.

Three configs probe the leverage dose-response on All-Weather:
  - 1× baseline (no leverage): KILL #49 anchor (Dalio canonical CAGR)
  - 1.41× capital-efficient stacking via NTSX/GDE (no LETF decay)
  - 2.25× LETF mix via UPRO/TMF/UGL (highest CAGR potential, decay drag)

See hypothesis.md for H₁/H₂/H₃/H₄ + pre-committed KILL #46/#47/#48/#49.

All synths in cache (TMFSIM via iter 008; NTSXSIM/GDESIM via
long_term_portfolio.proxies; UPRO/IEF/UGL/KMLM/TLT/SPY/GLD direct).
NO new modules; reuses ``static`` strategy type + portfolio_returns_from_config.
765 → 765 tests baseline preserved.

Run from repo root with .venv active:
    PYTHONPATH=. python studies/spy_beater_hunt/iterations/015-2026-04-30-F1-levered-all-weather/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 15
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "F1-levered-all-weather"
PRIMARY_CITATION = (
    "Bridgewater All-Weather (Dalio 1996, public papers 2011) risk-parity foundation + "
    "Asness (1996) 'Why Not 100% Equities?' JPM — leverage-balanced thesis + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking (NTSX/GDE rationale) + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed LETF decay magnitude + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM diversification) + "
    "[advances_fin_ml, p.31-34] factor framework (risk-parity construction) + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials"
)

# Cumulative: prior iters 001-014 = 44 (iter 014 added 3 to 41).
# This iter adds 3 → 47.
PRIOR_CUMULATIVE_N_TRIALS = 44
N_CONFIGS = 3
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 47

CONFIGS = {
    # 1x baseline: classic Dalio All-Weather (simplified to 3 assets for
    # synth coverage). 30 SPY + 55 TLT + 15 GLD. No commodities/MF (KMLM
    # absent for clean baseline). Tests KILL #49 — does pure 1x risk-parity
    # achieve CAGR >= 11.21%? Historical Dalio All-Weather ~7-8% CAGR.
    "f1_aw_baseline_1x": {
        "type": "static",
        "weights": {
            "SPYSIM": 0.30,
            "TLTSIM": 0.55,
            "GLDSIM": 0.15,
        },
    },
    # 1.41x capital-efficient stacking: 35 NTSX + 30 GDE + 20 TLT + 15 KMLM.
    # NTSX = 90% SPY + 60% IEF; GDE = 90% SPY + 90% Gold. Total notional
    # ~141% with NO LETF daily-reset decay. Adds KMLM crisis-alpha.
    # Effective exposure: 58.5% SPY + 21% IEF + 20% LTT + 27% Gold + 15% MF.
    "f1_aw_stack_15x": {
        "type": "static",
        "weights": {
            "NTSXSIM": 0.35,
            "GDESIM": 0.30,
            "TLTSIM": 0.20,
            "KMLMSIM": 0.15,
        },
    },
    # 2.25x LETF mix: 30 UPRO + 25 TMF + 15 IEF + 15 UGL + 15 KMLM. Highest
    # CAGR potential among F1 configs but ~3-4%/yr LETF decay drag.
    # Notional: 0.30*3 + 0.25*3 + 0.15*1 + 0.15*2 + 0.15*1 = 2.25x.
    "f1_aw_letf_2x": {
        "type": "static",
        "weights": {
            "UPROSIM": 0.30,
            "TMFSIM": 0.25,
            "IEFSIM": 0.15,
            "UGLSIM": 0.15,
            "KMLMSIM": 0.15,
        },
    },
}


if __name__ == "__main__":
    verdict = run_iter_spy_beater(
        iter_n=ITER_N,
        iter_dir=ITER_DIR,
        hypothesis_slug=HYPOTHESIS_SLUG,
        primary_citation=PRIMARY_CITATION,
        configs=CONFIGS,
        datasets_to_test=("lh_56y", "spy_real"),
        cumulative_n_trials=CUMULATIVE_N_TRIALS,
    )

    print(f"\n{'=' * 72}")
    print(f"Iter {ITER_N:03d} — {HYPOTHESIS_SLUG}")
    print(f"{'=' * 72}")
    print(f"Tier:     {verdict['tier']}")
    print(f"Score:    {verdict['total_score']}/100")
    print(f"Selected: {verdict['selected_config']}")
    print(f"Bars:     {verdict['bars']}")
    print(f"Winner:   {verdict['winner_conditions_met']}")
    print()
    print("Per-dataset metrics (selected config):")
    for ds, m in verdict["metrics_used"].items():
        gates_n = verdict["criteria"]["3_gates"]["per_dataset"][ds]
        print(
            f"  {ds:>10s}: Sharpe {m['sharpe']:+.3f}  "
            f"CAGR {m['cagr']*100:+.2f}%  MDD {m['mdd']*100:.2f}%  "
            f"gates {gates_n}/7"
        )
    print()
    print("All configs (mean CAGR / mean MDD across datasets):")
    for cfg, ds_metrics in verdict["all_configs_metrics"].items():
        cagrs = [ds_metrics[ds]["cagr"] for ds in ds_metrics]
        mean_cagr = sum(cagrs) / len(cagrs)
        mdds = [ds_metrics[ds]["mdd"] for ds in ds_metrics]
        mean_mdd = sum(mdds) / len(mdds)
        bar_pass = "PASS" if mean_cagr >= 0.1121 and mean_mdd <= 0.5517 else "FAIL"
        print(
            f"  [{bar_pass}] {cfg:>30s}: CAGR mean {mean_cagr*100:+.2f}%  "
            f"MDD mean {mean_mdd*100:.2f}%"
        )
