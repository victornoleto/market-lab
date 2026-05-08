"""Iter 034 driver: H14 META-ENSEMBLE 5-WAY with GLD-momentum-126d as 5th
constituent (Strategic Option C from iter 033 final report).

Tests whether GLD-mom-126d's +1pt Principle A bonus (iter 030 KILL #125, revised
to GOLD-SPECIFIC per iter 033 KILL #144 Principle J) survives being added as a
5th constituent on top of iter 027's 5-way base tax (KILL #107 FIRED — 5-way
with C1 at 5th scored 70 vs 4-way ceiling 71, base tax = -1pt).

Linear decomposition prediction (iter 026 KILL #103):
   5-way score = 71 (4-way E1qqq baseline) − 1 base 5-way tax + 1 GLD Principle
   A bonus = 71 (Pareto-co-tied at 4-way ceiling). Falsification: ≥73 strong-form
   breach; =72 GLD bonus survives base tax; ≤70 base tax dominates.

Four configs:
  - H14.1 (PRIMARY): 5-way 20/20/20/20/20 with E1qqq@4th + E1gld@5th
  - H14.2: 5-way GLD-heavy 20/20/20/15/25 (dose-response test)
  - H14.3: 5-way 20/20/20/20/20 with C1 vol-target@4th + E1gld@5th
  - H14.4 (SANITY): 4-way 25/25/25/25 GLD anchor — replicates iter 030 H10.4

A2, G2, F1, E1qqq, E1gld, C1 specs reused VERBATIM from iter 026/027/030/031/
032/033 (no parameter changes; ONLY constituent count + weight pattern change).

See hypothesis.md for KILL #145-#150.

NO new infra: reuses 'blend' + 'lrs' (sma + momentum filters) + 'static' +
'vol_target' spec types from iter 010/014/015/018-033. 771 tests baseline
preserved. TLTSIM, GLDSIM, IEFSIM, QQQSIM, SPYSIM, SSOSIM all in testfolio
cache.

Run from repo root with .venv active::

    PYTHONPATH=. python studies/spy_beater_hunt/iterations/034-2026-04-30-H14-meta-ensemble-5way-gld-mom-as-5th-constituent/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 34
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "H14-meta-ensemble-5way-gld-mom-as-5th-constituent"
PRIMARY_CITATION = (
    "[advances_fin_ml, ch.16, p.241-256] portfolio construction over "
    "multiple alpha streams (5-way meta-ensemble at strategy-level, 18th "
    "iter at meta-axis, NEW interaction sub-axis 5-way × GOLD) + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking (F1 stack "
    "always-on retained at 3rd constituent — nonuple-confirmed uniquely-"
    "Pareto-optimal per iter 033) + "
    "Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 "
    "(E1 TSMOM-126d gate-source on QQQ + GLD stacked at 4th + 5th positions) + "
    "Asness-Moskowitz-Pedersen (2013) Value and Momentum Everywhere, JoF "
    "68(3):929-985 (momentum across asset classes — equity-momentum + "
    "commodity-gold-momentum stacked) + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate "
    "(A2 + G2 baseline retained) + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM in A2/G2/E1 "
    "ON-state) + "
    "Bridgewater All-Weather (Dalio 1996) F1 stack ON-state + "
    "[systematic_trading, ch.10] Carver vol-targeting canonical (C1 in "
    "H14.3 only) + "
    "iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way) — extended "
    "to 5-way × GOLD here + "
    "iter 026 KILL #103 (linear decomposition principle) — UPPER-BOUND test + "
    "iter 027 KILL #107 (5-way base tax confirmed at C1 substitution) — "
    "challenged with GLD as 5th + "
    "iter 030 KILL #125 (Principle A — orthogonal-asset-class-TSMOM-source "
    "bonus +1pt) — revised to Principle J (GOLD-SPECIFIC) per iter 033 "
    "KILL #144 + "
    "iter 031 KILL #130 (Principle D — TSMOM-lookback inverted-U asset-"
    "invariant peak at 6m / 126d) — held fixed at 126d + "
    "iter 032 KILL #135 (Principle G — orthogonality bonus filter-type-"
    "coupled to momentum) — held fixed at filter=momentum + "
    "iter 033 KILL #144 (Principle J — orthogonality bonus is COMMODITY-"
    "GOLD-SPECIFIC) — operative for GLD-mom-126d 5th constituent + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials = 132 (Bonferroni "
    "3.79e-04) + "
    "[advances_fin_ml, p.208-211] PBO grid-level N=4 stability"
)

# Cumulative: prior iters 001-033 = 128. This iter adds 4 -> 132.
PRIOR_CUMULATIVE_N_TRIALS = 128
N_CONFIGS = 4
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 132


# ---------------------------------------------------------------------------
# Constituent specs (reused VERBATIM from iter 026/027/030/031/032/033)
# ---------------------------------------------------------------------------

# Constituent A (iter 006 a6_tqqq_split_kmlm30_tlt10) — highest-CAGR
# constituent (~17.33%); CAGR-floor anchor. Gate-source: QQQ-200d-SMA.
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

# Constituent B (iter 017 g2_f1_letf_2x_sma200_ief). Gate-source: SPY-200d-SMA.
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
# Gate-source: always-on (no gate). Nonuple-confirmed uniquely-Pareto-optimal
# at 3rd position per iter 033.
F1_STACK_SPEC = {
    "type": "static",
    "weights": {
        "NTSXSIM": 0.35,
        "GDESIM": 0.30,
        "TLTSIM": 0.20,
        "KMLMSIM": 0.15,
    },
}

# Constituent D-qqq (E1 TSMOM-126d-QQQ) — 4th constituent in iter 026 H6.1
# baseline (4-way 25/25/25/25 score 71). Gate-source: QQQ-momentum-126d.
E1_QQQ_MOM126_SPEC = {
    "type": "lrs",
    "filter": "momentum",
    "lookback_days": 126,
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

# Constituent D-gld (E1 TSMOM-126d-GLD) — Principle A / Principle J bonus
# constituent (iter 030 KILL #125 / iter 033 KILL #144). Gate-source:
# GLD-momentum-126d (orthogonal commodity asset-class).
E1_GLD_MOM126_SPEC = {
    "type": "lrs",
    "filter": "momentum",
    "lookback_days": 126,
    "on_weights": {
        "TQQQSIM": 0.30,
        "QLDSIM": 0.30,
        "KMLMSIM": 0.30,
        "TLTSIM": 0.10,
    },
    "off_weights": {"IEFSIM": 1.0},
    "signal_ticker": "GLDSIM",
    "lag_days": 1,
}

# Constituent E (iter 010 c1_vt20_sso) — Carver vol-target SSO 2x, target 20%
# annualized vol, 60d realized-vol signal. Gate-source: realized-vol-state.
# Reused from iter 027 H7. Distinct gate-mechanism from SMA-cross / TSMOM /
# always-on.
C1_VT20_SSO_SPEC = {
    "type": "vol_target",
    "underlying_weights": {"SSOSIM": 1.0},
    "underlying_leverage_factor": 2.0,
    "cash_weights": {"IEFSIM": 1.0},
    "signal_ticker": "SPYSIM",
    "vol_window": 60,
    "vol_lag_days": 1,
    "target_vol_annual": 0.20,
    "weight_min": 0.0,
    "weight_max": 1.0,
}


CONFIGS = {
    # H14.1 — PRIMARY FALSIFICATION TEST: 5-way equal-weight 20/20/20/20/20
    # with E1qqq@4th + E1gld@5th. Linear decomposition predicts: 71 - 1 base
    # 5-way tax + 1 GLD Principle A bonus = 71 (Pareto-co-tied at 4-way
    # ceiling). KILL #147 FIRED if score >= 72 (5-way base tax falsified for
    # GOLD-SPECIFIC bonus).
    "h14_meta_5way_20a2_20g2_20f1_20e1qqq_20e1gld_mom126": {
        "type": "blend",
        "constituents": [
            {"weight": 0.20, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.20, "spec": G2_IEF_SPEC},
            {"weight": 0.20, "spec": F1_STACK_SPEC},
            {"weight": 0.20, "spec": E1_QQQ_MOM126_SPEC},
            {"weight": 0.20, "spec": E1_GLD_MOM126_SPEC},
        ],
    },
    # H14.2 — 5-way GLD-heavy 20/20/20/15/25 (dose-response test). KILL #148
    # FIRED if H14.2 > H14.1 by >= 1pt (GLD bonus dose-additive).
    "h14_meta_5way_20a2_20g2_20f1_15e1qqq_25e1gld_mom126": {
        "type": "blend",
        "constituents": [
            {"weight": 0.20, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.20, "spec": G2_IEF_SPEC},
            {"weight": 0.20, "spec": F1_STACK_SPEC},
            {"weight": 0.15, "spec": E1_QQQ_MOM126_SPEC},
            {"weight": 0.25, "spec": E1_GLD_MOM126_SPEC},
        ],
    },
    # H14.3 — 5-way 20/20/20/20/20 with C1 vol-target@4th + E1gld@5th. Tests
    # whether vol-target gate-mechanism pairs better with GLD orthogonality
    # than QQQ-momentum at 4th. Compare to iter 027 H7.1 (with E1qqq+C1 = 70).
    # KILL #149 FIRED if H14.3 >= H14.1 by >= 1pt.
    "h14_meta_5way_20a2_20g2_20f1_20c1_20e1gld_mom126": {
        "type": "blend",
        "constituents": [
            {"weight": 0.20, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.20, "spec": G2_IEF_SPEC},
            {"weight": 0.20, "spec": F1_STACK_SPEC},
            {"weight": 0.20, "spec": C1_VT20_SSO_SPEC},
            {"weight": 0.20, "spec": E1_GLD_MOM126_SPEC},
        ],
    },
    # H14.4 — 4-way ANCHOR replicate (sanity check). Replicates iter 030
    # H10.4 / iter 031 H11.2 / iter 032 H12.1 / iter 033 H13.2 EXACTLY.
    # Should produce score 72 IDENTICAL. KILL #150 FIRED if matches; NOT
    # FIRED if deviation >= 0.01 Sharpe or >= 0.5pt score.
    "h14_meta_4way_25a2_25g2_25f1_25e1gld_mom126": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_GLD_MOM126_SPEC},
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
            f"  [{bar_pass}] {cfg:>54s}: CAGR {mean_cagr*100:+.2f}%  "
            f"MDD {mean_mdd*100:.2f}%  Sharpe {mean_sharpe:.3f}"
        )
