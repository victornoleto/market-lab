"""Iter 016 driver: G1 Regime-Gated Levered All-Weather (F1×A2 cross-product hybrid).

Second cross-product hybrid sanity check on KILL #33 (architectural ceiling
at 67). Combines the iter 015 best balanced sleeve (F1 stack: NTSX 35 +
GDE 30 + TLT 20 + KMLM 15, mean Sharpe 1.018, mean MDD 26.82%, 1.41x
notional, NO LETF decay) with the iter 006 best gate (Gayed 200d SMA on
SPY signal). Three configs probe the off-state defensive composition.

Iter 014 (E1 hybrid at 3x LETF, decay-dominated) showed gate x sleeve
interaction was NEGATIVE — cross-product score 65 BELOW union of single-
axis maxima. This iter tests whether the orthogonality assumption flips
back to positive at 1.41x stack (NO decay) — a fundamentally different
empirical regime than iter 014.

See hypothesis.md for H1/H2/H3/H4/H5 + pre-committed KILL #50/#51/#52/#53.

All assets in cache (NTSXSIM/GDESIM via long_term_portfolio.proxies;
TLTSIM/KMLMSIM/IEFSIM/SPYSIM signal direct). NO new modules; reuses
``lrs`` strategy type (added iter 001) + portfolio_returns_from_config.
765 -> 765 tests baseline preserved.

Run from repo root with .venv active:
    PYTHONPATH=. python studies/spy_beater_hunt/iterations/016-2026-04-30-G1-regime-gated-levered-all-weather/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 16
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "G1-regime-gated-levered-all-weather"
PRIMARY_CITATION = (
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate + "
    "Bridgewater All-Weather (Dalio 1996) F1-stack ON-state composition + "
    "Asness (1996) 'Why Not 100% Equities?' JPM leverage-balanced thesis + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking (NTSX/GDE) + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM defensive) + "
    "[advances_fin_ml, p.31-34] factor framework — gate x sleeve orthogonality "
    "explicitly tested at SECOND decay regime (1.41x stack, no decay) "
    "complementing iter 014 (3x LETF, decay-dominated) + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials"
)

# Cumulative: prior iters 001-015 = 47 (iter 015 added 3 to 44).
# This iter adds 3 -> 50.
PRIOR_CUMULATIVE_N_TRIALS = 47
N_CONFIGS = 3
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 50

# F1 stack ON-state (from iter 015 f1_aw_stack_15x — selected, score 61):
# 35 NTSX + 30 GDE + 20 TLT + 15 KMLM. Effective notional 1.41x.
# Mean Sharpe 1.018 (best in hunt), mean MDD 26.82% (best CAGR-pass), CAGR 11.95%.
F1_STACK_ON_WEIGHTS = {
    "NTSXSIM": 0.35,
    "GDESIM": 0.30,
    "TLTSIM": 0.20,
    "KMLMSIM": 0.15,
}

CONFIGS = {
    # G1.1: Classical Gayed defensive (100% IEF when off). Direct apples-to-
    # apples vs iter 015 f1_aw_stack_15x always-on. Tests whether removing
    # the F1 stack during bear regimes lifts CAGR (avoids bear drag) without
    # excessive whipsaw cost.
    "g1_f1_stack_sma200_ief": {
        "type": "lrs",
        "on_weights": F1_STACK_ON_WEIGHTS,
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "SPYSIM",
        "sma_window": 200,
        "filter": "sma",
        "lag_days": 1,
    },
    # G1.2: Aggressive defensive (100% KMLM when off). Crisis-alpha
    # amplification during bear regimes. KMLM has positive 2008 + 2022
    # returns via trend-following on commodities/FX/rates. Trade-off: KMLM
    # standalone MDD 5-10% in low-stress regimes — could underperform IEF
    # in slow bear markets.
    "g1_f1_stack_sma200_kmlm": {
        "type": "lrs",
        "on_weights": F1_STACK_ON_WEIGHTS,
        "off_weights": {"KMLMSIM": 1.0},
        "signal_ticker": "SPYSIM",
        "sma_window": 200,
        "filter": "sma",
        "lag_days": 1,
    },
    # G1.3: Balanced defensive (50 IEF + 50 KMLM when off). Hedges 2008-style
    # (bonds win) and 2022-style (KMLM win) regimes. Predicted to be most
    # robust across the 2-dataset framework with intermediate Sharpe vs
    # G1.1/G1.2.
    "g1_f1_stack_sma200_blend": {
        "type": "lrs",
        "on_weights": F1_STACK_ON_WEIGHTS,
        "off_weights": {"IEFSIM": 0.5, "KMLMSIM": 0.5},
        "signal_ticker": "SPYSIM",
        "sma_window": 200,
        "filter": "sma",
        "lag_days": 1,
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
            f"  [{bar_pass}] {cfg:>32s}: CAGR mean {mean_cagr*100:+.2f}%  "
            f"MDD mean {mean_mdd*100:.2f}%"
        )
