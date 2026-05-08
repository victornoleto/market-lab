"""Iter 029 driver: H9 META-ENSEMBLE 4-WAY GATE-LOOKBACK AXIS — TSMOM lookback
variation (E2 TSMOM-12m / E3 TSMOM-3m at 4th constituent slot vs iter 026 H6
E1 TSMOM-6m baseline).

Tests gate-lookback sub-axis within meta-axis 4-way structure. iter 026's
H6.4 (4-way 30a2_25g2_25f1_20e1) Pareto-co-apex at score 71 used E1 with
TSMOM-6m-QQQ gate (lookback_days=126). Iter 029 varies the lookback to
TSMOM-12m (E2, lookback=252) and TSMOM-3m (E3, lookback=63) to map gate-
lookback sub-axis.

Constituents A2, G2, F1 reused verbatim from iter 026. Only the 4th
constituent's TSMOM lookback parameter changes — isolating gate-lookback
effect within fixed sleeve composition.

Per Moskowitz-Ooi-Pedersen (2012) JFE 104(2):228-250, 12m is canonical
TSMOM lookback with 1m/3m/6m/9m robustness checks. For Faber-GTAA-equivalent
single-asset timing, 6-10m is canonical (Faber, ivy_portfolio). E2 (12m) and
E3 (3m) bracket E1 (6m) on the lookback axis.

Position-invariance from iter 028 KILL #114 applied: 4th-position weight
20% (H9.1, H9.2) or 25% (H9.3, H9.4) is NEUTRAL with respect to constituent
permutation (iter 028 H8.4 INVERTED proved meta-axis rubric symmetric under
constituent-position swaps). Selection rule "max mean(Sharpe / SPY_Sharpe)"
preserved.

See hypothesis.md for H9.1-H9.4 + pre-committed KILL #116-#120.

NO new infra: reuses 'blend' spec type from iter 018-028 + 'lrs' spec type
with 'momentum' filter from iter 014/024/026/028 (varied lookback_days
parameter only) + 'static' spec type from iter 015. 771 tests baseline
preserved.

Run from repo root with .venv active::

    PYTHONPATH=. python studies/spy_beater_hunt/iterations/029-2026-04-30-H9-meta-ensemble-4way-tsmom-lookback-axis/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 29
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "H9-meta-ensemble-4way-tsmom-lookback-axis"
PRIMARY_CITATION = (
    "[advances_fin_ml, ch.16, p.241-256] portfolio construction over "
    "multiple alpha streams (4-way meta-ensemble at strategy-level with "
    "gate-lookback sub-axis exploration — 13th iter at meta-axis) + "
    "Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 "
    "(canonical TSMOM-12m lookback, with 1m/3m/6m/9m robustness checks; "
    "E2 12m vs E3 3m vs iter 026 E1 6m baseline) + "
    "[ivy_portfolio] Faber GTAA single-asset 6-10m moving average "
    "(E1 6m / E2 12m bracket) + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate "
    "(A2 QQQ-track + G2 SPY-track LETF F1 constituents preserved) + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking "
    "(F1 stack always-on retained at 3rd constituent — quadruple-confirmed "
    "uniquely-Pareto-optimal per iter 027 KILL #110) + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM in A2/G2/E2/E3 "
    "ON-state) + "
    "Bridgewater All-Weather (Dalio 1996) F1 stack ON-state + "
    "[advances_fin_ml, p.31-34] factor framework — meta-ensemble axis "
    "13th iter (gate-lookback sub-axis exploration) + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials = 112 (Bonferroni "
    "4.46e-04) + "
    "[advances_fin_ml, p.208-211] PBO grid-level N=4 stability"
)

# Cumulative: prior iters 001-028 = 108. This iter adds 4 -> 112.
PRIOR_CUMULATIVE_N_TRIALS = 108
N_CONFIGS = 4
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 112


# Constituent A (iter 006 a6_tqqq_split_kmlm30_tlt10) — reused verbatim from
# iter 026. Highest-CAGR constituent (~17.33%); CAGR-floor anchor.
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

# Constituent B (iter 017 g2_f1_letf_2x_sma200_ief) — reused verbatim from iter 026.
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
# Gate-source: always-on (no gate). Reused verbatim from iter 026.
F1_STACK_SPEC = {
    "type": "static",
    "weights": {
        "NTSXSIM": 0.35,
        "GDESIM": 0.30,
        "TLTSIM": 0.20,
        "KMLMSIM": 0.15,
    },
}

# Constituent D — iter 029 NEW gate-lookback variants.
#
# E2 TSMOM-12m: lookback_days=252 (~12 calendar months) — Moskowitz-Ooi-
# Pedersen 2012 canonical. ON-sleeve identical to A2 / iter 026 E1 to
# isolate gate-lookback effect.
E2_TSMOM12M_SPEC = {
    "type": "lrs",
    "filter": "momentum",
    "lookback_days": 252,  # ~12 calendar months — Moskowitz-Ooi-Pedersen canonical
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

# E3 TSMOM-3m: lookback_days=63 (~3 calendar months) — short-lookback
# robustness check from Moskowitz et al. 2012 (1m/3m/6m/9m/12m sweep).
E3_TSMOM3M_SPEC = {
    "type": "lrs",
    "filter": "momentum",
    "lookback_days": 63,  # ~3 calendar months — short-lookback robustness
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
    # H9.1 — asymmetric 4-way 30/25/25/20 with E2 TSMOM-12m at 4th position.
    # Direct iter 026 H6.4 variant: only swaps E1 (6m) → E2 (12m).
    # Tests KILL #116/#117 (ceiling), KILL #118 (12m dominance), KILL #119 (6m
    # optimality), KILL #120 (rubric saturation).
    "h9_meta_4way_30a2_25g2_25f1_20e2": {
        "type": "blend",
        "constituents": [
            {"weight": 0.30, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.20, "spec": E2_TSMOM12M_SPEC},
        ],
    },
    # H9.2 — asymmetric 4-way 30/25/25/20 with E3 TSMOM-3m at 4th position.
    # Direct iter 026 H6.4 variant: only swaps E1 (6m) → E3 (3m).
    # Tests short-lookback whipsaw cost vs 6m baseline.
    "h9_meta_4way_30a2_25g2_25f1_20e3": {
        "type": "blend",
        "constituents": [
            {"weight": 0.30, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.20, "spec": E3_TSMOM3M_SPEC},
        ],
    },
    # H9.3 — equal-weight 4-way 25/25/25/25 with E2 TSMOM-12m at 4th position.
    # Direct iter 026 H6.1 variant: only swaps E1 (6m) → E2 (12m).
    # Tests gate-lookback rubric-effect at higher 4th-constituent dose.
    "h9_meta_4way_25a2_25g2_25f1_25e2": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E2_TSMOM12M_SPEC},
        ],
    },
    # H9.4 — equal-weight 4-way 25/25/25/25 with E3 TSMOM-3m at 4th position.
    # Direct iter 026 H6.1 variant: only swaps E1 (6m) → E3 (3m).
    # Tests short-lookback at higher 4th-constituent dose.
    "h9_meta_4way_25a2_25g2_25f1_25e3": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E3_TSMOM3M_SPEC},
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
