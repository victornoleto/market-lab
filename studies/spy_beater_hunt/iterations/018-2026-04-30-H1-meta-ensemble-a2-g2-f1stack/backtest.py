"""Iter 018 driver: H1 META-ENSEMBLE — portfolio-of-strategies probe.

Post-impossibility META-LEVEL probe on KILL #33 architectural ceiling.
Tests whether blending two existing closest-to-winner / Pareto-MDD configs
at strategy-level (rather than asset-level) lifts spy_beater score above
the 67-cap.

Constituent A: iter 006 ``a6_tqqq_split_kmlm30_tlt10`` (closest-to-winner,
score 67). LRS QQQ-gated 3x LETF + KMLM crisis-alpha + TLT.

Constituent B (config 1+2): iter 017 ``g2_f1_letf_2x_sma200_ief`` (third
hybrid Pareto-MDD CAGR-passer, score 64). LRS SPY-gated 2.25x LETF F1
All-Weather + IEF defensive.

Constituent B (config 3): iter 015 ``f1_aw_stack_15x`` (best Sharpe 1.018
+ best MDD-among-CAGR-passers 26.82%, score 61). Static always-on F1
stack 1.41x.

H1 META-ENSEMBLE explores a NEW orthogonal architectural axis (meta-
portfolio at strategy level, complementing asset/gate/decay axes already
mapped). Per [advances_fin_ml, ch.16, p.241-256] portfolio construction
over multiple alpha streams + [risk_parity, ch.5, p.10] Carlson capital-
efficient stacking generalized to strategy-level.

See hypothesis.md for H1/H2/H3 + pre-committed KILL #58/#59/#60/#61.

NEW infra: "blend" spec type added to run_iter.returns_from_spec
(iter 018) + 3 TDD tests. 765 -> 768 tests baseline.

Run from repo root with .venv active::

    PYTHONPATH=. python studies/spy_beater_hunt/iterations/018-2026-04-30-H1-meta-ensemble-a2-g2-f1stack/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 18
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "H1-meta-ensemble-a2-g2-f1stack"
PRIMARY_CITATION = (
    "[advances_fin_ml, ch.16, p.241-256] portfolio construction over "
    "multiple alpha streams (meta-ensemble at strategy-level) + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking "
    "generalized to strategy-level diversification + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate "
    "(both A2 QQQ-track and G2 SPY-track constituents) + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM in both A2 30% and G2 15%) + "
    "Bridgewater All-Weather (Dalio 1996) F1 stack ON-state composition + "
    "[advances_fin_ml, p.31-34] factor framework - meta-ensemble axis "
    "added to architectural taxonomy (asset, gate, decay, meta) + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials"
)

# Cumulative: prior iters 001-017 = 53. This iter adds 3 -> 56.
PRIOR_CUMULATIVE_N_TRIALS = 53
N_CONFIGS = 3
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 56


# Constituent A — iter 006 a6_tqqq_split_kmlm30_tlt10 (closest-to-winner)
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

# Constituent B1 — iter 017 g2_f1_letf_2x_sma200_ief (3rd-best CAGR-passer,
# best Sharpe 0.97 + good MDD 33.72% among CAGR-passers).
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

# Constituent B2 — iter 015 f1_aw_stack_15x (always-on multi-asset
# best Sharpe 1.018, best MDD-among-CAGR-passers 26.82%).
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
    # H1.1 — Same-gate-family blend (both LRS) at 50/50.
    # Tests if gate-aligned decorrelation (QQQ vs SPY signal, both 200d
    # SMA) lifts score above 67-ceiling. Linear-mean estimate: CAGR
    # 15.68%, MDD ~41.7%, score ~67-70.
    "h1_meta_50a2_50g2ief": {
        "type": "blend",
        "constituents": [
            {"weight": 0.50, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.50, "spec": G2_IEF_SPEC},
        ],
    },
    # H1.2 — Same-gate-family blend at 70/30 (more A2-weighted, higher
    # CAGR but less MDD relief).
    # Linear-mean estimate: CAGR 16.34%, MDD ~44.9%, score ~67-69.
    "h1_meta_70a2_30g2ief": {
        "type": "blend",
        "constituents": [
            {"weight": 0.70, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.30, "spec": G2_IEF_SPEC},
        ],
    },
    # H1.3 — Mixed-gate blend: A2 LRS-gated + F1 stack always-on.
    # Tests if always-on multi-asset diversifier provides constant CAGR
    # floor + MDD relief during A2's bear-mode IEF defensive phase.
    # Linear-mean estimate: CAGR 15.18%, MDD ~40.6%, score ~66-68.
    "h1_meta_60a2_40f1stack": {
        "type": "blend",
        "constituents": [
            {"weight": 0.60, "spec": A2_CLOSEST_SPEC},
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
