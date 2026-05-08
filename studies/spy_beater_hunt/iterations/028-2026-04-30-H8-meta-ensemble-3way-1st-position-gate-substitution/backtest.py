"""Iter 028 driver: H8 META-ENSEMBLE 3-WAY 1st-POSITION GATE-MECHANISM
SUBSTITUTION TEST (A2 SMA-gate → E1 TSMOM-gate at 1st constituent).

Tests POSITION-INVARIANCE of iter 026 KILL #102 NEW PRINCIPLE
(gate-source-distinctness contributes +1pt at 4-way structure when 4th
constituent has DISTINCT gate-source AND solo CAGR ≥ bar). iter 026
tested E1 ADDED at 4th position; iter 026 H6.2/H6.3 tested E1
SUBSTITUTED at 2nd/3rd positions (both score < 71). UNTESTED: E1
substituted at 1st position.

A2 spec and E1 spec share IDENTICAL on_weights (TQQQSIM 0.30, QLDSIM 0.30,
KMLMSIM 0.30, TLTSIM 0.10), off_weights (IEFSIM 1.0), and signal_ticker
(QQQSIM). The ONLY difference: A2 uses filter="sma" sma_window=200 while
E1 uses filter="momentum" lookback_days=126. This makes iter 028 a CLEAN
gate-mechanism axis test at 1st position.

Constituent A1 (E1 — replaces A2 at 1st): iter 014
e1_tqqq_split_kmlm30_tlt10_tsmom6m. Solo CAGR 17.20% / MDD 47.48% /
Sharpe 0.75. Gate-source: TSMOM-6m-QQQ.

Constituent B (G2 IEF): iter 017 g2_f1_letf_2x_sma200_ief. Solo CAGR
14.02% / MDD 33.72% / Sharpe 0.97. Gate-source: SPY-200d-SMA.

Constituent C (F1 stack): iter 015 f1_aw_stack_15x. Solo CAGR ~11.5% /
MDD ~26.82% / Sharpe 1.018. Gate-source: always-on.

Constituent D (A2 — only used in H8.4 INVERTED iter 026): iter 006
a6_tqqq_split_kmlm30_tlt10. Solo CAGR ~16% / MDD ~31% / Sharpe ~1.0.
Gate-source: QQQ-200d-SMA.

H8 META-ENSEMBLE explores 1st-position gate-mechanism substitution at
3-way axis vs iter-019 H2 closest-to-winner. Per [advances_fin_ml,
ch.16, p.241-256] portfolio construction over multiple alpha streams +
Moskowitz-Ooi-Pedersen (2012) TSMOM rationale + iter 026 NEW PRINCIPLE
(gate-source distinctness +1pt at 4-way structure) + iter 027 NEW
SUB-PRINCIPLE (CAGR-runway adequacy 3rd component) — generalize to
1st-position substitution test.

See hypothesis.md for H8.1-H8.4 + pre-committed KILL #111-#115.

NO new infra: reuses 'blend' + 'lrs' (sma + momentum filters) + 'static'
spec types from iter 014/017/019/026. 771 tests baseline preserved.

Run from repo root with .venv active::

    PYTHONPATH=. python studies/spy_beater_hunt/iterations/028-2026-04-30-H8-meta-ensemble-3way-1st-position-gate-substitution/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 28
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "H8-meta-ensemble-3way-1st-position-gate-substitution"
PRIMARY_CITATION = (
    "[advances_fin_ml, ch.16, p.241-256] portfolio construction over "
    "multiple alpha streams (3-way meta-ensemble at strategy-level with "
    "1st-position gate-mechanism substitution falsification test) + "
    "Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 "
    "(E1 TSMOM-6m gate at 1st-constituent position) + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate "
    "(A2 baseline + position-symmetry test for iter 026 H6.4) + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking "
    "generalized to 1st-position gate-mechanism substitution + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM in A2/E1/G2 "
    "ON-state) + "
    "Bridgewater All-Weather (Dalio 1996) F1 stack ON-state (3rd position "
    "retained — KILL #115 4th-confirmation test) + "
    "[advances_fin_ml, p.31-34] factor framework — meta-ensemble axis "
    "12th iter (1st-position gate-mechanism axis) + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials = 108 "
    "(Bonferroni 4.63e-04) + "
    "[advances_fin_ml, p.208-211] PBO grid-level N=4 stability"
)

# Cumulative: prior iters 001-027 = 104. This iter adds 4 -> 108.
PRIOR_CUMULATIVE_N_TRIALS = 104
N_CONFIGS = 4
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 108


# Constituent A2 (iter 006 a6_tqqq_split_kmlm30_tlt10) — used in H8.4 INVERTED
# (relegated from 1st position to 4th position).
# Solo: CAGR ~16.0% / MDD ~31% / Sharpe ~1.0. Gate-source: QQQ-200d-SMA.
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

# Constituent B (iter 017 g2_f1_letf_2x_sma200_ief) — same as iter 018-027.
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
# Gate-source: always-on (no gate). 3rd position retained across H8 (KILL #115).
F1_STACK_SPEC = {
    "type": "static",
    "weights": {
        "NTSXSIM": 0.35,
        "GDESIM": 0.30,
        "TLTSIM": 0.20,
        "KMLMSIM": 0.15,
    },
}

# Constituent E1 — promoted to 1st position in H8.1-H8.3 (substituting A2).
# Same on_weights/off_weights/signal_ticker as A2; ONLY filter differs
# (sma → momentum). Solo: CAGR 17.20% / MDD 47.48% / Sharpe 0.75.
# Gate-source: TSMOM-6m-QQQ.
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
    # H8.1 — CORE TEST: A2 → E1 substitution at iter-019 H2's 33/33/34 framework.
    # Linear-mean: CAGR 15.36%, MDD 32.42%, Sharpe ~0.97 (lower than iter 019's
    # 1.025 due to E1's 0.75 solo Sharpe vs A2's ~1.0).
    # Tests KILL #111: is A2 (SMA gate) uniquely Pareto-optimal at 1st position
    # OR is gate-mechanism substitutable across all 3 positions?
    "h8_meta_3way_33e1_33g2_34f1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.33, "spec": E1_TSMOM6M_SPEC},
            {"weight": 0.33, "spec": G2_IEF_SPEC},
            {"weight": 0.34, "spec": F1_STACK_SPEC},
        ],
    },
    # H8.2 — HEAVY E1 dose (50%); CAGR-amplify dose-response test.
    # Linear-mean: CAGR ~16.5%, MDD ~37%, Sharpe ~0.85-0.90 (heavy E1 drags
    # Sharpe via 0.75 solo).
    # Tests KILL #113: does E1 dose-response at 1st position monotonically
    # improve via CAGR-axis lift, OR does it saturate / regress?
    "h8_meta_3way_50e1_25g2_25f1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.50, "spec": E1_TSMOM6M_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
        ],
    },
    # H8.3 — HEAVY G2 dose (50%) + light E1 (25%) at 1st position.
    # Linear-mean: CAGR ~14.5%, MDD ~32%, Sharpe ~0.95-0.97.
    # Tests gate-distinctness contribution at LOW E1 dose vs H8.1 baseline.
    # If H8.3 score ≈ H8.1, gate-distinctness is dose-INSENSITIVE within
    # 25-33% range; if H8.3 < H8.1, gate-distinctness scales with E1 weight.
    "h8_meta_3way_25e1_50g2_25f1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": E1_TSMOM6M_SPEC},
            {"weight": 0.50, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
        ],
    },
    # H8.4 — INVERTED iter 026 H6.4 (Pareto-co-apex 71). Swap E1 ↔ A2 weights:
    # E1 promoted to 1st position (30%), A2 demoted to 4th position (20%).
    # iter 026 H6.4 was 30% A2 + 25% G2 + 25% F1 + 20% E1 → 71.
    # H8.4 is 30% E1 + 25% G2 + 25% F1 + 20% A2.
    # Linear-mean: CAGR ~15.6%, MDD ~33%, Sharpe ~0.95.
    # Tests KILL #114: position-symmetry of meta-axis rubric. If H8.4 ≈ 71,
    # constituent identity is invariant under position swap. If H8.4 < 71,
    # A2 must be 1st constituent for ceiling.
    "h8_meta_4way_30e1_25g2_25f1_20a2": {
        "type": "blend",
        "constituents": [
            {"weight": 0.30, "spec": E1_TSMOM6M_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.20, "spec": A2_CLOSEST_SPEC},
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
