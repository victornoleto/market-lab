"""Iter 026 driver: H6 META-ENSEMBLE 4-WAY with E1 (TSMOM-gated TQQQ) as
ALTERNATIVE 4TH CONSTITUENT — gate-source-diversity test.

Tests iter 025 NEW PRINCIPLE generalization to gate-source-diversity
dimension. iter 025 mapped 4th-constituent CAGR-axis (G1 IEF FAIL → G3 4040
PASS); iter 026 maps gate-source-axis (G3 4040 same SPY-200d-SMA gate as G2
IEF → E1 NEW TSMOM-6m-QQQ gate, distinct from all 3 prior constituents).

Constituent A (A2): iter 006 a6_tqqq_split_kmlm30_tlt10 (closest-to-winner
score 67). LRS QQQ-200d-SMA gate × 3x LETF + KMLM crisis-alpha + TLT.
Gate-source: QQQ-200d-SMA.

Constituent B (G2 IEF): iter 017 g2_f1_letf_2x_sma200_ief (3rd-best CAGR-
passer, mid-Sharpe 0.97 + good MDD 33.72%). LRS SPY-200d-SMA gate × 2.25x
LETF F1 All-Weather + IEF defensive. Gate-source: SPY-200d-SMA.

Constituent C (F1 stack): iter 015 f1_aw_stack_15x (always-on multi-asset
stack 1.41x; Sharpe 1.018, MDD 26.82%, score 61). Gate-source: always-on.

Constituent D (E1 — NEW for iter 026): iter 014
e1_tqqq_split_kmlm30_tlt10_tsmom6m (cross-product hybrid family member,
score 65). LRS TSMOM 6m (~126d) gate × 3x LETF + KMLM crisis-alpha + TLT.
ON-sleeve identical to A2 (isolating gate-source effect). Gate-source:
TSMOM-6m-QQQ — DIFFERENT from all 3 prior constituents.

Quadruple gate-source diversity: A2 (QQQ-200d-SMA) × G2 (SPY-200d-SMA) ×
F1 (always-on) × E1 (TSMOM-6m-QQQ NEW). Tests if NEW gate-source adds
super-linear decorrelation lift beyond 3-source iter 019 H2 baseline.

H6 META-ENSEMBLE explores 4-way axis with TSMOM-axis integration vs iter
025's 4-way with G3 4040 (same-SMA-source as G2). Per [advances_fin_ml,
ch.16, p.241-256] portfolio construction + Moskowitz-Ooi-Pedersen (2012)
TSMOM rationale + [risk_parity, ch.5, p.10] Carlson capital-efficient
stacking generalized to 4 distinct gate-sources.

See hypothesis.md for H6.1-H6.4 + pre-committed KILL #101-#105.

NO new infra: reuses 'blend' spec type from iter 018-025 + 'lrs' spec type
with both 'sma' and 'momentum' filters from iter 014/024 + 'static' spec
type from iter 015; 771 tests baseline preserved.

Run from repo root with .venv active::

    PYTHONPATH=. python studies/spy_beater_hunt/iterations/026-2026-04-30-H6-meta-ensemble-4way-tsmom-gate-source-diversity/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 26
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "H6-meta-ensemble-4way-tsmom-gate-source-diversity"
PRIMARY_CITATION = (
    "[advances_fin_ml, ch.16, p.241-256] portfolio construction over "
    "multiple alpha streams (4-way meta-ensemble at strategy-level with "
    "gate-source-diversity test) + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking "
    "generalized to 4 distinct gate-sources + "
    "Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 "
    "(E1 TSMOM 6m gate-source) + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate "
    "(A2 QQQ-track + G2 SPY-track LETF F1 constituents — SMA gate-source) + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM in A2/G2/E1 "
    "ON-state; F1 stack always-on) + "
    "Bridgewater All-Weather (Dalio 1996) F1 stack ON-state + "
    "[advances_fin_ml, p.31-34] factor framework — meta-ensemble axis "
    "10th iter (TSMOM gate-source-diversity test) + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials = 100 + "
    "[advances_fin_ml, p.208-211] PBO grid-level N=4 stability"
)

# Cumulative: prior iters 001-025 = 96. This iter adds 4 -> 100.
PRIOR_CUMULATIVE_N_TRIALS = 96
N_CONFIGS = 4
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 100


# Constituent A (iter 006 a6_tqqq_split_kmlm30_tlt10) — same as iter 018-021/025.
# Highest-CAGR constituent (~17.33%); CAGR-floor anchor.
# Gate-source: QQQ-200d-SMA.
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

# Constituent B (iter 017 g2_f1_letf_2x_sma200_ief) — same as iter 018-021/025.
# Gate-source: SPY-200d-SMA.
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
# Gate-source: always-on (no gate).
F1_STACK_SPEC = {
    "type": "static",
    "weights": {
        "NTSXSIM": 0.35,
        "GDESIM": 0.30,
        "TLTSIM": 0.20,
        "KMLMSIM": 0.15,
    },
}

# Constituent D (iter 014 e1_tqqq_split_kmlm30_tlt10_tsmom6m) — NEW for iter 026.
# TSMOM-6m-QQQ gate × 3x LETF + KMLM30 + TLT10. ON-sleeve identical to A2,
# isolating gate-source effect. Solo CAGR 17.20% / MDD 47.48% / Sharpe 0.75.
# Gate-source: TSMOM-6m-QQQ — DIFFERENT from all 3 prior constituents.
E1_TSMOM6M_SPEC = {
    "type": "lrs",
    "filter": "momentum",
    "lookback_days": 126,  # ~6 calendar months (Faber GTAA equivalent)
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


CONFIGS = {
    # H6.1 — equal-weight 4-way (CORE TEST: G3 → E1 substitution at iter 025's 4-way).
    # Linear-mean: CAGR 15.51%, MDD 36.06%, Sharpe 0.945.
    # Tests KILL #102: does E1 (higher solo CAGR + DIFFERENT gate-source) lift over
    # iter 025 H5.1 score 70 (G3 4040 same SPY-SMA source as G2)?
    "h6_meta_4way_25a2_25g2_25f1_25e1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_TSMOM6M_SPEC},
        ],
    },
    # H6.2 — 3-way substitute F1 stack with E1 (TSMOM-axis replaces always-on).
    # Linear-mean: CAGR 16.18%, MDD 39.06%, Sharpe 0.890.
    # Tests KILL #104: does E1 outperform F1 stack as 3rd constituent of iter 019's
    # 33/33/34 framework? Parallels iter 025 KILL #97 (G3 vs F1).
    "h6_meta_3way_33a2_33g2_34e1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.33, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.33, "spec": G2_IEF_SPEC},
            {"weight": 0.34, "spec": E1_TSMOM6M_SPEC},
        ],
    },
    # H6.3 — 3-way substitute G2 IEF with E1 (replace SPY-LETF-SMA gate w/ TSMOM-QQQ gate).
    # Linear-mean: CAGR 15.94%, MDD 36.74%, Sharpe 0.918.
    # Tests KILL #105: is TSMOM-6m-QQQ gate substitutable for SPY-200d-LETF gate
    # within meta-ensemble? Parallels iter 025 KILL #98 (G3 vs G2).
    "h6_meta_3way_33a2_33e1_34f1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.33, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.33, "spec": E1_TSMOM6M_SPEC},
            {"weight": 0.34, "spec": F1_STACK_SPEC},
        ],
    },
    # H6.4 — asymmetric 4-way preserving A2 tilt + minor E1 dose.
    # Linear-mean: CAGR 15.59%, MDD 35.59%, Sharpe 0.953.
    # Lower E1 dose 20% → less MDD-axis dilution from E1's 47.48% solo MDD.
    # Parallel to iter 025 H5.4.
    "h6_meta_4way_30a2_25g2_25f1_20e1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.30, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.20, "spec": E1_TSMOM6M_SPEC},
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
