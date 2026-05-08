"""Iter 009 driver: B2 HFEA + KMLM crisis-alpha (UPRO + TMF + KMLM blend).

Pivot from B1 HFEA classical (CLOSED via iter 008 KILL #24 — spy_real MDD
67.13% > 65% bar, all 3 weights in [50, 60] UPRO range fail MDD bar).
The literature-aware response is to add KMLM crisis-alpha (validated
empirically on SPY-track iter 003-005 and TQQQ-track iter 007 — monotonic
positive Sharpe through 40% KMLM with <2pp CAGR drag).

Configs sweep KMLM at 15/20/25% by replacing TMF (the 2022 weak leg).
UPRO held constant at 50% (iter 008 b1_balanced_5050 best Sharpe variant).

See hypothesis.md for H₁/H₂/H₃ + pre-committed KILL #27/#28/#29.

Run from repo root with .venv active:
    PYTHONPATH=. python studies/spy_beater_hunt/iterations/009-2026-04-30-B2-hfea-kmlm/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 9
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "B2-hfea-kmlm"
PRIMARY_CITATION = (
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed LETF decay rationale + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha role + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking + "
    "[advances_fin_ml, p.31-34] factor framework (TMF and KMLM as distinct factors)"
)

# Cumulative: prior iters 001-008 = 29. This iter adds 3 → 32.
PRIOR_CUMULATIVE_N_TRIALS = 29
N_CONFIGS = 3
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 32

CONFIGS = {
    # Anchor: 50% UPRO + 35% TMF + 15% KMLM. Recommendation from iter 008
    # final_report. Minimum KMLM dose tested (matches iter 003 SPY-track).
    "b2_hfea_kmlm15": {
        "type": "static",
        "weights": {
            "UPROSIM": 0.50,
            "TMFSIM": 0.35,
            "KMLMSIM": 0.15,
        },
    },
    # KMLM dose +5pp, TMF -5pp. SPY-track iter 003 KMLM 20% scored
    # closest-to-winner at the time. Tests H₂ monotonic dose-response.
    "b2_hfea_kmlm20": {
        "type": "static",
        "weights": {
            "UPROSIM": 0.50,
            "TMFSIM": 0.30,
            "KMLMSIM": 0.20,
        },
    },
    # Maximum KMLM dose tested. Tests upper bound: does marginal MDD
    # relief slow (concave) or invert (KILL #28)? UPRO fixed; TMF=KMLM.
    "b2_hfea_kmlm25": {
        "type": "static",
        "weights": {
            "UPROSIM": 0.50,
            "TMFSIM": 0.25,
            "KMLMSIM": 0.25,
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
