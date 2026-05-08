"""Iter 021 driver: H4 META-ENSEMBLE — alternative always-on constituents
and asymmetric 3-way weights.

Tests whether the meta-ensemble axis ceiling at 71 (iter-019's 3-way 33/33/34
A2 + G2 IEF + F1 stack) extends by:
  (a) Substituting F1 stack 1.41× always-on with higher-CAGR-runway variants:
      F1 LETF 2.25× (G2 IEF sleeve standalone, no gate), pure NTSX 100%, or
      F1 stack 2× variant (NTSX 50 + GDE 30 + KMLM 20, no TLT).
  (b) Asymmetric 3-way weight perturbations (30/35/35, 35/30/35, 30/40/30)
      around 33/33/34 to map local optimum surface.

Per iter-020 lesson recommendation. Pre-commit KILL #71: if iter-021 max
score ≤ 71, the meta-axis ceiling is **DEFINITIVE at 71** within
spy_beater rubric.

Constituent A (A2): iter 006 ``a6_tqqq_split_kmlm30_tlt10`` (highest-CAGR
constituent at 17.33%). LRS QQQ-gated 3× LETF + KMLM crisis-alpha + TLT.

Constituent C (G2 IEF): iter 017 ``g2_f1_letf_2x_sma200_ief`` (mid-Sharpe
0.97, mid-CAGR 14.02%). LRS SPY-gated 2.25× LETF F1 All-Weather + IEF.

Constituent D (F1 stack): iter 015 ``f1_aw_stack_15x`` (always-on multi-asset
stack 1.41×; Sharpe 1.018, MDD 26.82%, CAGR 11.95%). Used in H4.4-H4.6 as
weight perturbation baseline.

NEW always-on constituents (substitutes F1 stack at H4.1-H4.3):
- D' = F1 LETF 2.25× always-on (UPRO 30 + TMF 25 + IEF 15 + UGL 15 + KMLM 15,
  no gate). Composition same as G2 IEF ON-state.
- D'' = pure NTSX 100% always-on (simplest concentrated equity, 1.5× notional).
- D''' = F1 stack 2× variant (NTSX 50 + GDE 30 + KMLM 20, no TLT, no gate).

H4 META-ENSEMBLE explores alternative always-on axis + asymmetric weight axis.
Per [advances_fin_ml, ch.16, p.241-256] portfolio construction +
[risk_parity, ch.5, p.10] Carlson capital-efficient stacking generalized.

See hypothesis.md for H4.1-H4.6 + pre-committed KILL #71/#72/#73/#74/#75/#76.

NO new infra: reuses "blend" + "lrs" + "static" spec types from iter 018-020.
771 tests baseline preserved.

Run from repo root with .venv active::

    PYTHONPATH=. python studies/spy_beater_hunt/iterations/021-2026-04-30-H4-meta-ensemble-alt-always-on-and-asymmetric-weights/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 21
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "H4-meta-ensemble-alt-always-on-and-asymmetric-weights"
PRIMARY_CITATION = (
    "[advances_fin_ml, ch.16, p.241-256] portfolio construction over "
    "multiple alpha streams — alternative always-on constituent "
    "substitution test at 3-way meta-ensemble axis + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking "
    "generalized to higher-CAGR-runway always-on (F1 LETF 2.25×) vs "
    "no-decay stack (F1 stack 1.41×) + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate "
    "(A2 QQQ-track + G2 SPY-track gated constituents preserved) + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM) — present "
    "in 5 of 6 configs (NTSX 100% H4.2 has no KMLM) + "
    "Bridgewater All-Weather (Dalio 1996) F1 stack composition variants "
    "(with-TLT iter-019 baseline + no-TLT 2× variant H4.3 + LETF variant "
    "H4.1) + [advances_fin_ml, p.31-34] factor framework — meta-ensemble "
    "axis weight + always-on substitution depth probe + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials = 74 + "
    "[advances_fin_ml, p.208-211] PBO grid-level N=6 stability maintained "
    "per iter-019 KILL #64 resolution"
)

# Cumulative: prior iters 001-020 = 68. This iter adds 6 -> 74.
PRIOR_CUMULATIVE_N_TRIALS = 68
N_CONFIGS = 6
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 74


# Constituent A (iter 006 a6_tqqq_split_kmlm30_tlt10) — same as iter 018/019/020.
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

# Constituent C (iter 017 g2_f1_letf_2x_sma200_ief) — same as iter 018/019/020.
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

# Constituent D — F1 stack 1.41× always-on (iter 015 baseline; iter-019 winner).
F1_STACK_SPEC = {
    "type": "static",
    "weights": {
        "NTSXSIM": 0.35,
        "GDESIM": 0.30,
        "TLTSIM": 0.20,
        "KMLMSIM": 0.15,
    },
}

# NEW: F1 LETF 2.25× always-on (G2 IEF ON-state composition without gate).
# Higher-CAGR-runway alternative; tested at H4.1.
F1_LETF_2X_ALWAYS_ON_SPEC = {
    "type": "static",
    "weights": {
        "UPROSIM": 0.30,
        "TMFSIM": 0.25,
        "IEFSIM": 0.15,
        "UGLSIM": 0.15,
        "KMLMSIM": 0.15,
    },
}

# NEW: Pure NTSX 100% always-on (simplest concentrated equity 1.5× notional).
# Tested at H4.2.
NTSX_100_ALWAYS_ON_SPEC = {
    "type": "static",
    "weights": {
        "NTSXSIM": 1.0,
    },
}

# NEW: F1 stack 2× variant always-on (NTSX 50 + GDE 30 + KMLM 20, no TLT).
# Tests TLT marginal contribution. Tested at H4.3.
F1_STACK_NO_TLT_ALWAYS_ON_SPEC = {
    "type": "static",
    "weights": {
        "NTSXSIM": 0.50,
        "GDESIM": 0.30,
        "KMLMSIM": 0.20,
    },
}


CONFIGS = {
    # === GROUP A — Alternative always-on at 33/33/34 baseline ===
    # H4.1 — F1 LETF 2.25× always-on (CORE TEST for H₁: higher-CAGR runway).
    # Linear-mean est: CAGR ~14.5%, MDD ~38%, Sharpe ~0.93.
    "h4_meta_3way_33a2_33g2_34f1letf2x": {
        "type": "blend",
        "constituents": [
            {"weight": 0.33, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.33, "spec": G2_IEF_SPEC},
            {"weight": 0.34, "spec": F1_LETF_2X_ALWAYS_ON_SPEC},
        ],
    },
    # H4.2 — Pure NTSX 100% always-on (simplest concentrated equity).
    # Linear-mean est: CAGR ~14.0%, MDD ~35%, Sharpe ~0.90.
    "h4_meta_3way_33a2_33g2_34ntsx100": {
        "type": "blend",
        "constituents": [
            {"weight": 0.33, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.33, "spec": G2_IEF_SPEC},
            {"weight": 0.34, "spec": NTSX_100_ALWAYS_ON_SPEC},
        ],
    },
    # H4.3 — F1 stack 2× variant (no TLT) — tests TLT marginal contribution.
    # Linear-mean est: CAGR ~13.5%, MDD ~31%, Sharpe ~0.97.
    "h4_meta_3way_33a2_33g2_34f1stack_no_tlt": {
        "type": "blend",
        "constituents": [
            {"weight": 0.33, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.33, "spec": G2_IEF_SPEC},
            {"weight": 0.34, "spec": F1_STACK_NO_TLT_ALWAYS_ON_SPEC},
        ],
    },
    # === GROUP B — Asymmetric 3-way weights with original F1 stack ===
    # H4.4 — 30/35/35 F1-and-G2-heavy (lower A2).
    # Linear-mean: CAGR 14.30%, MDD 36.13%, Sharpe 0.937.
    "h4_meta_3way_30a2_35g2_35f1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.30, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.35, "spec": G2_IEF_SPEC},
            {"weight": 0.35, "spec": F1_STACK_SPEC},
        ],
    },
    # H4.5 — 35/30/35 A2-and-F1-tilt (lower G2).
    # Linear-mean: CAGR 14.45%, MDD 36.86%, Sharpe 0.929.
    "h4_meta_3way_35a2_30g2_35f1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.35, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.30, "spec": G2_IEF_SPEC},
            {"weight": 0.35, "spec": F1_STACK_SPEC},
        ],
    },
    # H4.6 — 30/40/30 G2-heavy.
    # Linear-mean: CAGR 14.40%, MDD 36.42%, Sharpe 0.934.
    "h4_meta_3way_30a2_40g2_30f1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.30, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.40, "spec": G2_IEF_SPEC},
            {"weight": 0.30, "spec": F1_STACK_SPEC},
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
