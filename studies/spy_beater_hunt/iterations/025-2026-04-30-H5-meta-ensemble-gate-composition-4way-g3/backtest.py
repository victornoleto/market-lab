"""Iter 025 driver: H5 META-ENSEMBLE GATE-COMPOSITION 4-WAY (A2 + G2 IEF + F1 stack + G3 4040).

Tests whether the meta-ensemble axis ceiling extends beyond iter-019's 71 by
substituting / adding G3 4040 (iter 024 cross-product hybrid family ceiling
at 66, KILL #94 NEW PRINCIPLE: gate composition has TWO orthogonal effects —
bear-avoidance + effective-leverage reduction via time-averaged exposure).

Constituent A (A2): iter 006 a6_tqqq_split_kmlm30_tlt10 (closest-to-winner
score 67). LRS QQQ-gated 3x LETF + KMLM crisis-alpha + TLT.

Constituent B (G2 IEF): iter 017 g2_f1_letf_2x_sma200_ief (3rd-best CAGR-
passer, mid-Sharpe 0.97 + good MDD 33.72%). LRS SPY-gated 2.25x LETF F1
All-Weather + IEF defensive.

Constituent C (F1 stack): iter 015 f1_aw_stack_15x (always-on multi-asset
stack 1.41x; Sharpe 1.018, MDD 26.82%, score 61).

Constituent D (G3 4040 — NEW for iter 025): iter 024 g3_gated_hfea_4040
(gated HFEA classical 300% notional with KMLM aug; score 66 cross-product
hybrid family ceiling, CAGR 15.79% / MDD 44.71% / Sharpe 0.895). Tests if
KILL #94's effective-leverage-reduction mechanism stacks with meta-axis
decorrelation.

H5 META-ENSEMBLE explores 4-way axis with cross-product-hybrid integration
(vs iter 020's 4-way with G1 IEF non-CAGR-passer). Per [advances_fin_ml,
ch.16, p.241-256] portfolio construction + [risk_parity, ch.5, p.10] Carlson
capital-efficient stacking generalized to strategy-level.

See hypothesis.md for H5.1-H5.5 + pre-committed KILL #95-#100.

NO new infra: reuses 'blend' spec type from iter 018-021 + 'lrs' spec type
from iter 024 + 'static' spec type from iter 015; 771 tests baseline preserved.

Run from repo root with .venv active::

    PYTHONPATH=. python studies/spy_beater_hunt/iterations/025-2026-04-30-H5-meta-ensemble-gate-composition-4way-g3/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 25
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "H5-meta-ensemble-gate-composition-4way-g3"
PRIMARY_CITATION = (
    "[advances_fin_ml, ch.16, p.241-256] portfolio construction over "
    "multiple alpha streams (4-way meta-ensemble at strategy-level with "
    "cross-product-hybrid integration) + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking "
    "generalized to 4-way strategy-level diversification + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate "
    "(A2 QQQ-track + G2/G3 SPY-track constituents — triple-gate-source meta-blend) + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM in all 4 "
    "constituents) + Bridgewater All-Weather (Dalio 1996) F1 stack ON-state "
    "+ HFEA Bogleheads 2019 leveraged-barbell (G3 sleeve) + "
    "[advances_fin_ml, p.31-34] factor framework — meta-ensemble axis "
    "9th iter (gate-composition stacking test) + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials = 96 + "
    "[advances_fin_ml, p.208-211] PBO grid-level N=5 stability"
)

# Cumulative: prior iters 001-024 = 91. This iter adds 5 -> 96.
PRIOR_CUMULATIVE_N_TRIALS = 91
N_CONFIGS = 5
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 96


# Constituent A (iter 006 a6_tqqq_split_kmlm30_tlt10) — same as iter 018-021.
# Highest-CAGR constituent (~17.33%); CAGR-floor anchor.
A2_CLOSEST_SPEC = {
    "type": "lrs",
    "filter": "sma",
    "sma_window": 200,
    "buffer_pct": 0.0,
    "on_weights": {
        "TQQQSIM": 0.30,
        "QLDSIM": 0.30,
        "KMLMSIM": 0.30,
        "TLTSIM": 0.10,
    },
    "off_weights": {"IEFSIM": 1.0},
    "signal_ticker": "QQQSIM",
    "lag_days": 1,
}

# Constituent B (iter 017 g2_f1_letf_2x_sma200_ief) — same as iter 018-021.
G2_IEF_SPEC = {
    "type": "lrs",
    "on_weights": {
        "UPROSIM": 0.30,
        "TMFSIM": 0.25,
        "IEFSIM": 0.15,
        "UGLSIM": 0.15,
        "KMLMSIM": 0.15,
    },
    "off_weights": {"IEFSIM": 1.0},
    "signal_ticker": "SPYSIM",
    "sma_window": 200,
    "filter": "sma",
    "lag_days": 1,
}

# Constituent C (iter 015 f1_aw_stack_15x) — always-on multi-asset stack.
F1_STACK_SPEC = {
    "type": "static",
    "weights": {
        "NTSXSIM": 0.35,
        "GDESIM": 0.30,
        "TLTSIM": 0.20,
        "KMLMSIM": 0.15,
    },
}

# Constituent D (iter 024 g3_gated_hfea_4040) — NEW for iter 025.
# Gated HFEA classical 300% notional + KMLM aug; cross-product hybrid family
# ceiling at 66. KILL #94 NEW PRINCIPLE: gate composition has TWO orthogonal
# effects — bear-avoidance + effective-leverage reduction via time-averaged
# exposure (gated-300% behaves like static-225% in MF-effectiveness terms).
G3_4040_SPEC = {
    "type": "lrs",
    "on_weights": {
        "UPROSIM": 0.40,
        "TMFSIM": 0.40,
        "KMLMSIM": 0.20,
    },
    "off_weights": {"IEFSIM": 1.0},
    "signal_ticker": "SPYSIM",
    "sma_window": 200,
    "filter": "sma",
    "lag_days": 1,
}


CONFIGS = {
    # H5.1 — equal-weight 4-way (CORE TEST adding G3 to iter-019's 3-way).
    # Linear-mean: CAGR 15.16%, MDD 35.31%, Sharpe 0.958.
    # Tests: does 4-way w/ CAGR-passing G3 lift over iter-020 4-way w/ G1 IEF (67)?
    "h5_meta_4way_25a2_25g2_25f1_25g3": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": G3_4040_SPEC},
        ],
    },
    # H5.2 — 3-way substitute F1 stack with G3 (gate-composition replaces always-on).
    # Linear-mean: CAGR 15.72%, MDD 38.21%, Sharpe 0.938.
    # Tests KILL #97: G3 vs F1 stack as 3rd constituent in iter-019's 33/33/34.
    "h5_meta_3way_33a2_33g2_34g3": {
        "type": "blend",
        "constituents": [
            {"weight": 0.33, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.33, "spec": G2_IEF_SPEC},
            {"weight": 0.34, "spec": G3_4040_SPEC},
        ],
    },
    # H5.3 — 3-way substitute G2 IEF with G3 (replace LETF gate w/ HFEA gate).
    # Linear-mean: CAGR 15.52%, MDD 35.75%, Sharpe 0.955.
    # Tests KILL #98: SPY-200d-LETF vs SPY-200d-HFEA gate substitutability.
    "h5_meta_3way_33a2_33g3_34f1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.33, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.33, "spec": G3_4040_SPEC},
            {"weight": 0.34, "spec": F1_STACK_SPEC},
        ],
    },
    # H5.4 — asymmetric 4-way preserving A2 tilt + minor G3 dose.
    # Linear-mean: CAGR 15.25%, MDD 34.88%, Sharpe 0.961.
    # Lower G3 dose 20% → less MDD-axis dilution, preserves CAGR via A2 tilt.
    "h5_meta_4way_30a2_25g2_25f1_20g3": {
        "type": "blend",
        "constituents": [
            {"weight": 0.30, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.20, "spec": G3_4040_SPEC},
        ],
    },
    # H5.5 — 3-way A2+G3+F1 with F1 dominance (boost F1 to compensate G3 MDD).
    # Linear-mean: CAGR 15.34%, MDD 34.94%, Sharpe 0.961.
    # F1 dominance compensates G3's MDD penalty; G3 substitutes G2.
    "h5_meta_3way_30a2_30g3_40f1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.30, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.30, "spec": G3_4040_SPEC},
            {"weight": 0.40, "spec": F1_STACK_SPEC},
        ],
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
    print(f"Score:    {verdict['total_score']}/100  (net: {verdict.get('net_total_score', 'n/a')}/100)")
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
    print("All configs (mean CAGR / mean MDD / mean Sharpe across datasets):")
    for cfg, ds_metrics in verdict["all_configs_metrics"].items():
        cagrs = [ds_metrics[ds]["cagr"] for ds in ds_metrics]
        mean_cagr = sum(cagrs) / len(cagrs)
        mdds = [ds_metrics[ds]["mdd"] for ds in ds_metrics]
        mean_mdd = sum(mdds) / len(mdds)
        sharpes = [ds_metrics[ds]["sharpe"] for ds in ds_metrics]
        mean_sharpe = sum(sharpes) / len(sharpes)
        bar_pass = "PASS" if mean_cagr >= 0.1121 and mean_mdd <= 0.5517 else "FAIL"
        print(
            f"  [{bar_pass}] {cfg:>40s}: CAGR {mean_cagr*100:+.2f}%  "
            f"MDD {mean_mdd*100:.2f}%  Sharpe {mean_sharpe:.3f}"
        )
