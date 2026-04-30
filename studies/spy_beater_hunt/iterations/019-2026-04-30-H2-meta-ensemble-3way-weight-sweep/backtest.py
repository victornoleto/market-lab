"""Iter 019 driver: H2 META-ENSEMBLE — 3-way blends + weight sweep.

Confirms / refutes iter 018 score 70 under N=6 PBO grid (vs iter 018
N=3 instability warning). Sweeps 2-way weight axis around 50/50
(45/55, 50/50, 55/45) and tests 3-way blends adding F1 stack always-on
multi-asset diversifier at varying weights.

Constituent A (A2): iter 006 ``a6_tqqq_split_kmlm30_tlt10`` (closest-
to-winner score 67). LRS QQQ-gated 3x LETF + KMLM crisis-alpha + TLT.

Constituent B (G2 IEF): iter 017 ``g2_f1_letf_2x_sma200_ief`` (3rd-best
CAGR-passer, best Sharpe 0.97 + good MDD 33.72% among CAGR-passers).
LRS SPY-gated 2.25x LETF F1 All-Weather + IEF defensive.

Constituent C (F1 stack): iter 015 ``f1_aw_stack_15x`` (always-on
multi-asset stack 1.41x; best Sharpe 1.018, best MDD-among-CAGR-
passers 26.82%, score 61).

H2 META-ENSEMBLE explores 3-way meta-portfolio axis (vs iter 018's
2-way). Per [advances_fin_ml, ch.16, p.241-256] portfolio construction
+ [risk_parity, ch.5, p.10] Carlson capital-efficient stacking
generalized to strategy-level.

See hypothesis.md for H2.1/H2.2/H2.3/H2.4 + pre-committed KILL
#62/#63/#64/#65.

NO new infra: reuses "blend" spec type from iter 018; 768 tests
baseline preserved.

Run from repo root with .venv active::

    PYTHONPATH=. python studies/spy_beater_hunt/iterations/019-2026-04-30-H2-meta-ensemble-3way-weight-sweep/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 19
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "H2-meta-ensemble-3way-weight-sweep"
PRIMARY_CITATION = (
    "[advances_fin_ml, ch.16, p.241-256] portfolio construction over "
    "multiple alpha streams (3-way meta-ensemble at strategy-level) + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking "
    "generalized to strategy-level diversification + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate "
    "(both A2 QQQ-track and G2 SPY-track constituents) + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM in A2, G2, F1) + "
    "Bridgewater All-Weather (Dalio 1996) F1 stack ON-state composition + "
    "[advances_fin_ml, p.31-34] factor framework — meta-ensemble axis "
    "deeper exploration (3-way) + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials = 62 + "
    "[advances_fin_ml, p.208-211] PBO grid-level N=6 stability vs iter-018 N=3"
)

# Cumulative: prior iters 001-018 = 56. This iter adds 6 -> 62.
PRIOR_CUMULATIVE_N_TRIALS = 56
N_CONFIGS = 6
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 62


# Constituent A (iter 006 a6_tqqq_split_kmlm30_tlt10) — same as iter 018.
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

# Constituent B (iter 017 g2_f1_letf_2x_sma200_ief) — same as iter 018.
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


CONFIGS = {
    # H2.1 — Reproducibility check of iter 018 winner under N=6 PBO grid.
    # Same constituents + same weights; deterministic returns. Score may
    # shift +-1pt only via PBO N=6 vs N=3 grid stability.
    "h2_meta_50a2_50g2ief": {
        "type": "blend",
        "constituents": [
            {"weight": 0.50, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.50, "spec": G2_IEF_SPEC},
        ],
    },
    # H2.2a — 2-way weight sweep, slight A2-tilt vs 50/50.
    # Linear-mean: CAGR 15.84%, MDD ~42.4%, Sharpe ~0.88.
    "h2_meta_55a2_45g2ief": {
        "type": "blend",
        "constituents": [
            {"weight": 0.55, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.45, "spec": G2_IEF_SPEC},
        ],
    },
    # H2.2b — 2-way weight sweep, slight G2-tilt vs 50/50.
    # Linear-mean: CAGR 15.51%, MDD ~41.0%, Sharpe ~0.91.
    "h2_meta_45a2_55g2ief": {
        "type": "blend",
        "constituents": [
            {"weight": 0.45, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.55, "spec": G2_IEF_SPEC},
        ],
    },
    # H2.3a — 3-way blend, balanced (A2 40, G2 30, F1 stack 30).
    # Effective leverage when both gates ON ≈ 2.25×; F1 always-on at 1.41×.
    # Linear-mean: CAGR 14.72%, MDD ~36.6%, Sharpe ~0.95.
    "h2_meta_3way_40a2_30g2_30f1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.40, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.30, "spec": G2_IEF_SPEC},
            {"weight": 0.30, "spec": F1_STACK_SPEC},
        ],
    },
    # H2.3b — 3-way blend, A2-heavy (50/25/25). Higher CAGR floor + small
    # F1 stack contribution. Linear-mean: CAGR 15.16%, MDD ~38.9%,
    # Sharpe ~0.92.
    "h2_meta_3way_50a2_25g2_25f1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.50, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
        ],
    },
    # H2.3c — 3-way blend, equal-weight (33/33/34). Most diversified.
    # Linear-mean: CAGR 14.43%, MDD ~36.0%, Sharpe ~0.96.
    "h2_meta_3way_33a2_33g2_34f1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.33, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.33, "spec": G2_IEF_SPEC},
            {"weight": 0.34, "spec": F1_STACK_SPEC},
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
            f"  [{bar_pass}] {cfg:>32s}: CAGR {mean_cagr*100:+.2f}%  "
            f"MDD {mean_mdd*100:.2f}%  Sharpe {mean_sharpe:.3f}"
        )
