"""Iter 020 driver: H3 META-ENSEMBLE — 4-way blends + alternative 3-way pairs.

Tests whether the meta-ensemble axis ceiling extends beyond iter-019's 71 by:
  (a) 4-way blends adding G1 IEF (best-in-hunt Sharpe 1.080 + best-in-hunt MDD
      18.57% but FAILS CAGR alone at 10.34%) as a 4th decorrelation source.
  (b) Alternative 3-way pairs replacing G2 IEF with G1 IEF — testing if
      Sharpe-anchored constituent Pareto-dominates iter-019's mid-Sharpe G2 IEF.
  (c) All-gated 3-way (no F1 stack always-on) — testing whether F1 stack is
      essential for meta-blend Pareto-improvement.

Constituent A (A2): iter 006 ``a6_tqqq_split_kmlm30_tlt10`` (closest-to-winner
score 67). LRS QQQ-gated 3x LETF + KMLM crisis-alpha + TLT.

Constituent B (G1 IEF): iter 016 ``g1_f1_stack_sma200_ief`` (best Sharpe 1.080
+ best MDD 18.57% in entire hunt; FAILS CAGR alone at 10.34%). LRS SPY-gated
1.41x F1 stack + IEF defensive.

Constituent C (G2 IEF): iter 017 ``g2_f1_letf_2x_sma200_ief`` (3rd-best
CAGR-passer, mid-Sharpe 0.97 + good MDD 33.72%). LRS SPY-gated 2.25x LETF F1
All-Weather + IEF defensive.

Constituent D (F1 stack): iter 015 ``f1_aw_stack_15x`` (always-on multi-asset
stack 1.41x; Sharpe 1.018, MDD 26.82%, score 61).

H3 META-ENSEMBLE explores the 4-way axis (vs iter 018's 2-way + iter 019's
3-way). Per [advances_fin_ml, ch.16, p.241-256] portfolio construction +
[risk_parity, ch.5, p.10] Carlson capital-efficient stacking generalized to
strategy-level.

See hypothesis.md for H3.1-H3.6 + pre-committed KILL #66/#67/#68/#69/#70.

NO new infra: reuses "blend" spec type from iter 018 (supports any number of
constituents); 771 tests baseline preserved.

Run from repo root with .venv active::

    PYTHONPATH=. python studies/spy_beater_hunt/iterations/020-2026-04-30-H3-meta-ensemble-4way-and-alt-3way-g1-ief/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 20
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "H3-meta-ensemble-4way-and-alt-3way-g1-ief"
PRIMARY_CITATION = (
    "[advances_fin_ml, ch.16, p.241-256] portfolio construction over "
    "multiple alpha streams (4-way meta-ensemble at strategy-level) + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking "
    "generalized to 4-way strategy-level diversification + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate "
    "(A2 QQQ-track + G1/G2 SPY-track constituents — dual-SPY-gated test) + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM in all 4 "
    "constituents) + Bridgewater All-Weather (Dalio 1996) F1 stack ON-state "
    "composition repeated in G1 IEF ON + [advances_fin_ml, p.31-34] factor "
    "framework — meta-ensemble axis 4-way structure depth probe + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials = 68 + "
    "[advances_fin_ml, p.208-211] PBO grid-level N=6 stability maintained "
    "per iter-019 KILL #64 resolution"
)

# Cumulative: prior iters 001-019 = 62. This iter adds 6 -> 68.
PRIOR_CUMULATIVE_N_TRIALS = 62
N_CONFIGS = 6
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 68


# Constituent A (iter 006 a6_tqqq_split_kmlm30_tlt10) — same as iter 018/019.
# Highest-CAGR constituent (17.33%); CAGR-floor anchor.
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

# Constituent B (iter 016 g1_f1_stack_sma200_ief) — NEW for iter 020.
# BEST Sharpe 1.080 + BEST MDD 18.57% in entire hunt; FAILS CAGR alone.
# LRS SPY-200d-SMA gate on F1 stack (1.41× no-decay).
G1_IEF_SPEC = {
    "type": "lrs",
    "on_weights": {
        "NTSXSIM": 0.35,
        "GDESIM": 0.30,
        "TLTSIM": 0.20,
        "KMLMSIM": 0.15,
    },
    "off_weights": {"IEFSIM": 1.0},
    "signal_ticker": "SPYSIM",
    "sma_window": 200,
    "filter": "sma",
    "lag_days": 1,
}

# Constituent C (iter 017 g2_f1_letf_2x_sma200_ief) — same as iter 018/019.
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

# Constituent D (iter 015 f1_aw_stack_15x) — same as iter 019.
# Always-on multi-asset stack 1.41× — structural diversifier (no gate).
F1_STACK_SPEC = {
    "type": "static",
    "weights": {
        "NTSXSIM": 0.35,
        "GDESIM": 0.30,
        "TLTSIM": 0.20,
        "KMLMSIM": 0.15,
    },
}


CONFIGS = {
    # H3.1 — 4-way equal-weight (CORE TEST).
    # Tests H₁: does 4-way break iter-019's 71-cap via 4 decorrelated streams?
    # Linear-mean: CAGR 13.41%, MDD 32.21%, Sharpe 0.968.
    "h3_meta_4way_25a2_25g1_25g2_25f1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G1_IEF_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
        ],
    },
    # H3.2 — 4-way A2-tilted (CAGR-preserving).
    # Linear-mean: CAGR 13.79%, MDD 33.05%, Sharpe 0.952.
    "h3_meta_4way_30a2_20g1_25g2_25f1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.30, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.20, "spec": G1_IEF_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
        ],
    },
    # H3.3 — Alt 3-way: G1 IEF replaces G2 IEF (mirrors iter-019 33/33/34).
    # Tests H₂: does Sharpe-anchored G1 IEF Pareto-dominate iter-019's G2 IEF?
    # Linear-mean: CAGR 13.13%, MDD 31.66%, Sharpe 0.968.
    "h3_meta_3way_33a2_33g1_34f1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.33, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.33, "spec": G1_IEF_SPEC},
            {"weight": 0.34, "spec": F1_STACK_SPEC},
        ],
    },
    # H3.4 — Alt 3-way A2-heavy with G1 IEF (analog of iter-019 50/25/25).
    # Linear-mean: CAGR 14.24%, MDD 36.21%, Sharpe 0.929.
    "h3_meta_3way_50a2_25g1_25f1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.50, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G1_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
        ],
    },
    # H3.5 — All-gated 3-way (no F1 stack).
    # Tests H₃: does dual-gate + LETF substitution work without F1 always-on?
    # Linear-mean: CAGR 13.90%, MDD 34.01%, Sharpe 0.951.
    "h3_meta_3way_33a2_33g1_34g2": {
        "type": "blend",
        "constituents": [
            {"weight": 0.33, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.33, "spec": G1_IEF_SPEC},
            {"weight": 0.34, "spec": G2_IEF_SPEC},
        ],
    },
    # H3.6 — 4-way moderate A2-tilt (smaller G1 IEF dose).
    # Linear-mean: CAGR 14.04%, MDD 33.51%, Sharpe 0.940.
    "h3_meta_4way_35a2_15g1_25g2_25f1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.35, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.15, "spec": G1_IEF_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
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
