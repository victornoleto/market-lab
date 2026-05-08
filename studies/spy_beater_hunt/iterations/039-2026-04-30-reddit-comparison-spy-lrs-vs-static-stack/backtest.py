"""Iter 039: REDDIT POST COMPARISON — SPY vs LRS vs static stack.

Apples-to-apples comparison for r/LETFs Reddit post.

Goal: demonstrate that simple capital-efficient static stacking beats
both SPY 1x buy-hold AND classical Gayed LRS (200d SMA × SSO/UPRO).

7 configs covering 3 reference points + 4 deploy candidates from iter 038:

  REFERENCES:
    R1 spy_1x_buy_hold           — pure SPY (the bar everyone tries to beat)
    R2 sso_lrs_200sma            — 2x SSO LRS Gayed canonical (defensive: IEF off)
    R3 upro_lrs_200sma           — 3x UPRO LRS Gayed (Hedgefundie-lite)

  STATIC STACK CANDIDATES (from iter 038 sweep, NET-of-tax means):
    T1 gold_heavy        — 20 NTSX + 35 GDE + 25 RSST + 20 TMF (max CAGR)
    B2 tmf10_balanced    — 30/30/30/10 (TMF dose-down, balanced)
    B4 zroz_instead      — 25/25/25/25 with ZROZ (best risk-adjusted)
    L2 bogleheads_67ntsx — 67 NTSX + 11/11/11 (sleep-well conservative)

Reuses 'static' + 'lrs' specs. NO new infra. 771 tests baseline preserved.

Run::

    PYTHONPATH=. python studies/spy_beater_hunt/iterations/039-*/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 39
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "reddit-comparison-spy-lrs-vs-static-stack"
PRIMARY_CITATION = (
    "Reddit r/LETFs comparison post + "
    "[leverage_for_the_long_run, ch.3-4] Gayed 200d SMA LRS canonical + "
    "iter 038 sweep results (capital-efficient stacking) + "
    "Bridgewater All-Weather (Dalio) + RiskParityChronicles CEGB"
)

PRIOR_CUMULATIVE_N_TRIALS = 158
N_CONFIGS = 7
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 165


CONFIGS = {
    # --- REFERENCES ---
    "R1_spy_1x_buy_hold": {
        "type": "static",
        "weights": {"SPYSIM": 1.0},
    },
    "R2_sso_lrs_200sma": {
        "type": "lrs",
        "filter": "sma",
        "sma_window": 200,
        "buffer_pct": 0.0,  # Gayed canonical
        "on_weights": {"SSOSIM": 1.0},     # 2x SPY when bullish regime
        "off_weights": {"IEFSIM": 1.0},    # 1x ITT defensive
        "signal_ticker": "SPYSIM",
        "lag_days": 1,
    },
    "R3_upro_lrs_200sma": {
        "type": "lrs",
        "filter": "sma",
        "sma_window": 200,
        "buffer_pct": 0.0,
        "on_weights": {"UPROSIM": 1.0},    # 3x SPY when bullish regime
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "SPYSIM",
        "lag_days": 1,
    },

    # --- STATIC STACK CANDIDATES (from iter 038) ---
    "T1_gold_heavy": {
        "type": "static",
        "weights": {"NTSXSIM": 0.20, "GDESIM": 0.35, "RSSTSIM": 0.25, "TMFSIM": 0.20},
    },
    "B2_tmf10_balanced": {
        "type": "static",
        "weights": {"NTSXSIM": 0.30, "GDESIM": 0.30, "RSSTSIM": 0.30, "TMFSIM": 0.10},
    },
    "B4_zroz_instead": {
        "type": "static",
        "weights": {"NTSXSIM": 0.25, "GDESIM": 0.25, "RSSTSIM": 0.25, "ZROZSIM": 0.25},
    },
    "L2_bogleheads_67ntsx": {
        "type": "static",
        "weights": {"NTSXSIM": 0.67, "GLDSIM": 0.11, "KMLMSIM": 0.11, "ZROZSIM": 0.11},
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

    print(f"\n{'=' * 80}")
    print(f"Iter {ITER_N:03d} — REDDIT comparison")
    print(f"{'=' * 80}")
    print(f"{'config':<24} {'Sh_lh':>6} {'CAGR_lh':>8} {'MDD_lh':>8} {'Sh_spy':>7} {'CAGR_spy':>9} {'MDD_spy':>9}")
    for cfg_name, ds_metrics in verdict["all_configs_metrics"].items():
        lh = ds_metrics["lh_56y"]
        sp = ds_metrics["spy_real"]
        print(
            f"{cfg_name:<24} "
            f"{lh['sharpe']:>6.3f} {lh['cagr']*100:>7.2f}% {lh['mdd']*100:>7.2f}% "
            f"{sp['sharpe']:>7.3f} {sp['cagr']*100:>8.2f}% {sp['mdd']*100:>8.2f}%"
        )
