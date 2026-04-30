"""Iter 017 driver: G2 Regime-Gated Levered All-Weather LETF 2x (third cross-product hybrid).

Third cross-product hybrid sanity check on KILL #33 (architectural ceiling
at 67). Bridges iter 014 (E1 hybrid, 3x LETF, decay-dominated, gate x
sleeve NEGATIVE) and iter 016 (G1 hybrid, 1.41x stack, no-decay, gate x
sleeve MIXED). Tests intermediate decay regime: 2.25x LETF, ~3-4%/y decay
drag.

ON-state weights identical to iter 015 f1_aw_letf_2x (which standalone
passed all 3 strict bars: CAGR 16.36%, MDD 43.53%, Sharpe 0.90):
  30 UPRO + 25 TMF + 15 IEF + 15 UGL + 15 KMLM = 2.25x notional.

Gate fixed at canonical 200d SMA on SPYSIM signal, lag T+1 (identical to
iter 016 G1 for direct leverage-axis comparison).

Three configs sweep off-state defensive composition (matching iter 016
G1 dose-response IEF / KMLM / 50-50 blend).

Iter 016 path-to-90 analysis explicitly enumerated this iter as the
untested prediction: 'Adding regime gate to LETF 2x F1: predicted CAGR
up ~1pp via bear miss, MDD down ~5-10pp, Sharpe down ~0.05 (LETF
whipsaw). Net G1-LETF estimated 60-65 - same architectural ceiling.'

See hypothesis.md for H1/H2/H3/H4/H5 + pre-committed KILL #54/#55/#56/#57.

All assets in cache (UPROSIM/TMFSIM/IEFSIM/UGLSIM/KMLMSIM/SPYSIM all
direct in testfolio cache). NO new modules; reuses ``lrs`` strategy type
(added iter 001) + portfolio_returns_from_config. 765 -> 765 tests
baseline preserved.

Run from repo root with .venv active:
    PYTHONPATH=. python studies/spy_beater_hunt/iterations/017-2026-04-30-G2-regime-gated-levered-all-weather-letf2x/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 17
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "G2-regime-gated-levered-all-weather-letf2x"
PRIMARY_CITATION = (
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate + "
    "Bridgewater All-Weather (Dalio 1996) F1 LETF 2x ON-state composition + "
    "Asness (1996) 'Why Not 100% Equities?' JPM leverage-balanced thesis at moderate decay + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking baseline + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM defensive) + "
    "[advances_fin_ml, p.31-34] factor framework - gate x sleeve orthogonality "
    "explicitly tested at THIRD decay regime (2.25x LETF, moderate decay) "
    "complementing iter 014 (3x LETF, decay-dominated) and iter 016 (1.41x stack, no decay) + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials"
)

# Cumulative: prior iters 001-016 = 50.
# This iter adds 3 -> 53.
PRIOR_CUMULATIVE_N_TRIALS = 50
N_CONFIGS = 3
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 53

# F1 LETF 2x ON-state (from iter 015 f1_aw_letf_2x, which passed all 3 bars
# standalone: CAGR 16.36%, MDD 43.53%, Sharpe 0.897/0.910).
# Effective notional 2.25x with LETF decay drag ~3-4%/y.
F1_LETF_2X_ON_WEIGHTS = {
    "UPROSIM": 0.30,   # 3x SPY -> 0.90x SPY
    "TMFSIM":  0.25,   # 3x LTT -> 0.75x LTT
    "IEFSIM":  0.15,   # 1x ITT -> 0.15x ITT
    "UGLSIM":  0.15,   # 2x Gold -> 0.30x Gold
    "KMLMSIM": 0.15,   # 1x MF -> 0.15x MF
}

CONFIGS = {
    # G2.1: Classical Gayed defensive (100% IEF when off). Direct apples-to-
    # apples vs iter 016 g1_f1_stack_sma200_ief at 1.41x stack. Tests whether
    # the 2.25x LETF leverage AND moderate decay change the gate x sleeve
    # interaction sign.
    "g2_f1_letf_2x_sma200_ief": {
        "type": "lrs",
        "on_weights": F1_LETF_2X_ON_WEIGHTS,
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "SPYSIM",
        "sma_window": 200,
        "filter": "sma",
        "lag_days": 1,
    },
    # G2.2: Aggressive defensive (100% KMLM when off). Tests whether iter 016
    # finding "IEF > KMLM monotonic on all metrics" transfers to moderate-
    # decay regime. KMLM has positive 2008 + 2022 returns via trend-following
    # but standalone Sharpe is moderate; could underperform IEF in slow
    # bear markets at higher leverage.
    "g2_f1_letf_2x_sma200_kmlm": {
        "type": "lrs",
        "on_weights": F1_LETF_2X_ON_WEIGHTS,
        "off_weights": {"KMLMSIM": 1.0},
        "signal_ticker": "SPYSIM",
        "sma_window": 200,
        "filter": "sma",
        "lag_days": 1,
    },
    # G2.3: Balanced defensive (50 IEF + 50 KMLM when off). Tests whether
    # the iter 016 monotonic dose-response pattern (IEF > 50/50 > KMLM)
    # holds at LETF 2x.
    "g2_f1_letf_2x_sma200_blend": {
        "type": "lrs",
        "on_weights": F1_LETF_2X_ON_WEIGHTS,
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
    print(f"Iter {ITER_N:03d} - {HYPOTHESIS_SLUG}")
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
