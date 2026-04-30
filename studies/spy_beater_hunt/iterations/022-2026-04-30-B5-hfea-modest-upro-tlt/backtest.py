"""Iter 022 driver: B5 HFEA-modest (3x UPRO + 1x TLT static barbell).

Pivot from meta-axis (saturated at gross 71 across 4 sequential iters
018-021) to the static-barbell axis with 1x duration replacement.
KILL #24 closed UPRO+TMF (3x+3x) on MDD bar (mean MDD 67-72%);
KILL #27 closed HFEA+KMLM on MDD bar even with crisis-alpha.
This iter tests UPRO+TLT (3x+1x) which is architecturally distinct:
eliminates TMF daily-reset decay (~1.5%/y) and reduces 2022
stagflation MDD (TLT -31% vs TMF -70%).

Critically: static spec.type -> tax drag ~0.66pp vs blend's ~1.91pp.
A gross score >=65 lands net >=64, potentially TYING/BEATING the
meta-ensemble net rank-1.

See hypothesis.md for H1-H5 + pre-committed KILL #77 through KILL #82.

Run from repo root with .venv active:
    PYTHONPATH=. python studies/spy_beater_hunt/iterations/022-2026-04-30-B5-hfea-modest-upro-tlt/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 22
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "B5-hfea-modest-upro-tlt"
PRIMARY_CITATION = (
    "HFEA Bogleheads 2019 canonical 55/45 anchor + modest-leverage variant + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed LETF decay rationale "
    "(1x TLT eliminates TMF 1.5%/y daily-reset decay) + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking "
    "(B5 50/50 = 150% SPY notional + 50% UST notional) + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha role + "
    "[advances_fin_ml, p.31-34] factor framework + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials = 80 + "
    "[advances_fin_ml, p.208-211] PBO via CSCV N=6 + "
    "WINNER_AND_RANKING.md structural net-rubric advantage 1.5pp for buy-hold static"
)

# Cumulative: prior iters 001-021 = 74. This iter adds 6 -> 80.
PRIOR_CUMULATIVE_N_TRIALS = 74
N_CONFIGS = 6
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 80

CONFIGS = {
    # H1, H2 anchor — 50/50 UPRO/TLT (modest-HFEA canonical)
    # 50% x 3x SPY + 50% x 1x LTT = 150% SPY notional + 50% UST notional
    # Direct analogue to iter 008 b1_balanced_5050 (50% UPRO + 50% TMF)
    # but with 1x duration leg eliminating TMF 1.5%/y decay
    "b5_5050_upro_tlt": {
        "type": "static",
        "weights": {
            "UPROSIM": 0.50,
            "TLTSIM": 0.50,
        },
    },
    # H2 defensive end — 40/60
    # Lower UPRO -> lower CAGR but lower MDD; tests 5pp reduction in
    # equity arm to see if MDD margin extends without breaking CAGR bar
    "b5_4060_upro_tlt": {
        "type": "static",
        "weights": {
            "UPROSIM": 0.40,
            "TLTSIM": 0.60,
        },
    },
    # H2 offensive end — 60/40
    # Higher UPRO -> higher CAGR, higher MDD; tests whether offensive
    # leverage breaks MDD bar (KILL #81)
    "b5_6040_upro_tlt": {
        "type": "static",
        "weights": {
            "UPROSIM": 0.60,
            "TLTSIM": 0.40,
        },
    },
    # H3 KMLM addition — 40/40/20 (counter-test to KILL #27)
    # KMLM at 20% replaces 10pp UPRO + 10pp TLT
    # On HFEA classical (165% UPRO + 135% TMF), KMLM was Sharpe-flat
    # On modest-HFEA (150% UPRO + 50% TLT), KMLM should diversify
    "b5_4040_kmlm20": {
        "type": "static",
        "weights": {
            "UPROSIM": 0.40,
            "TLTSIM": 0.40,
            "KMLMSIM": 0.20,
        },
    },
    # H3 KMLM addition — 50/30/20 (more equity, more KMLM substitution for TLT)
    # Tests KMLM-on-modest-HFEA dose-response at higher UPRO weight
    "b5_5030_kmlm20": {
        "type": "static",
        "weights": {
            "UPROSIM": 0.50,
            "TLTSIM": 0.30,
            "KMLMSIM": 0.20,
        },
    },
    # H4 DBMF substitution test — same structure as b5_4040_kmlm20 with DBMF
    # DBMF (iMGP DBi Managed Futures) is broader CTA basket vs KMLM (KFA)
    # Tests whether KILL #27's KMLM finding transfers across MF substitutes
    "b5_4040_dbmf20": {
        "type": "static",
        "weights": {
            "UPROSIM": 0.40,
            "TLTSIM": 0.40,
            "DBMFSIM": 0.20,
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
