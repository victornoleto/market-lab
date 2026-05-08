"""Iter 008 driver: B1 HFEA classical (UPRO + TMF leveraged barbell).

Pivot from A2 TQQQ-track (saturated at ~67) to a different return/risk
geometry. Tests Bogleheads canonical 55/45 ± 5pp UPRO weight sweep.
TMFSIM synth = 3× TLTSIM − 1.5%/y daily-reset decay (already validated
by 3 tests in tests/test_studies_spy_beater_hunt.py).

See hypothesis.md for H₁/H₂/H₃ + pre-committed KILL #24/#25/#26.

Run from repo root with .venv active:
    PYTHONPATH=. python studies/spy_beater_hunt/iterations/008-2026-04-30-B1-hfea-classical/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 8
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "B1-hfea-classical"
PRIMARY_CITATION = (
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed LETF decay rationale + "
    "HFEA Bogleheads 2019 canonical 55/45 + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking + "
    "[advances_fin_ml, p.31-34] factor framework (leveraged duration as distinct factor)"
)

# Cumulative: prior iters 001-007 = 26. This iter adds 3 → 29.
PRIOR_CUMULATIVE_N_TRIALS = 26
N_CONFIGS = 3
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 29

CONFIGS = {
    # Canonical Bogleheads HFEA (55% UPRO + 45% TMF). Risk-parity claim:
    # both legs contribute similar dollar volatility at this weighting.
    "b1_classic_5545": {
        "type": "static",
        "weights": {
            "UPROSIM": 0.55,
            "TMFSIM": 0.45,
        },
    },
    # Equity-tilted HFEA (60/40). Reduces TMF (worst leg in 2022) — should
    # raise CAGR + raise MDD; tests H₂ monotonic dose-response on UPRO weight.
    "b1_modern_6040": {
        "type": "static",
        "weights": {
            "UPROSIM": 0.60,
            "TMFSIM": 0.40,
        },
    },
    # Duration-tilted HFEA (50/50). More TMF — historically lower MDD pre-2022
    # but worst-case in 2022 stress. Maps the dose-response curve at 5pp
    # spacing around the 55/45 anchor.
    "b1_balanced_5050": {
        "type": "static",
        "weights": {
            "UPROSIM": 0.50,
            "TMFSIM": 0.50,
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
