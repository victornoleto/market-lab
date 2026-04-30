"""Iter 027 driver: H7 META-ENSEMBLE 5-WAY with C1 (vol-target SSO) as
ALTERNATIVE 5TH CONSTITUENT — vol-target gate-source-diversity falsification
test of iter 026's linear decomposition principle.

Tests iter 026 KILL #103 generalization to 5-way structure: does adding a
NEW gate-mechanism (Carver vol-target, distinct from SMA-cross and TSMOM-
momentum) provide sufficient gate-source-distinct bonus to compensate the
−2pt 5-way base diversification tax?

Constituent A (A2): iter 006 a6_tqqq_split_kmlm30_tlt10 (closest-to-winner
score 67). LRS QQQ-200d-SMA gate × 3x LETF + KMLM30 + TLT10. Solo CAGR
~17.33%. Gate-source: QQQ-200d-SMA.

Constituent B (G2 IEF): iter 017 g2_f1_letf_2x_sma200_ief (3rd-best CAGR-
passer, mid-Sharpe 0.97 + good MDD 33.72%). LRS SPY-200d-SMA gate × 2.25x
LETF F1 All-Weather + IEF defensive. Gate-source: SPY-200d-SMA.

Constituent C (F1 stack): iter 015 f1_aw_stack_15x (always-on multi-asset
stack 1.41x; Sharpe 1.018, MDD 26.82%, score 61). Gate-source: always-on.

Constituent D (E1): iter 014 e1_tqqq_split_kmlm30_tlt10_tsmom6m. LRS TSMOM-
6m-QQQ gate × 3x LETF + KMLM30 + TLT10. Solo CAGR 17.20%. Gate-source:
TSMOM-6m-QQQ (distinct mechanism from SMA-cross and always-on).

Constituent E (C1 — NEW for iter 027): iter 010 c1_vt20_sso. Carver vol-
target on SSO 2x, target 20% annualized vol, 60d realized vol signal,
SPYSIM signal-ticker. Solo CAGR 13.54% / Sharpe 0.72 / MDD 41.86%. Gate-
source: realized-vol-state — DIFFERENT mechanism from SMA-cross / TSMOM-
momentum / always-on.

Quintuple gate-source diversity: A2 (QQQ-200d-SMA) × G2 (SPY-200d-SMA) ×
F1 (always-on) × E1 (TSMOM-6m-QQQ) × C1 (vol-target NEW). Tests whether
linear decomposition principle (iter 026) extends predictably to 5-way
structure or breaks ceiling 71.

H7 META-ENSEMBLE explores 5-way axis with vol-target-axis integration vs
iter 026's 4-way with E1 TSMOM-axis. Per [advances_fin_ml, ch.16, p.241-
256] portfolio construction + [systematic_trading, ch.10] Carver vol-
target canonical + [risk_parity, ch.5, p.10] Carlson capital-efficient
stacking generalized to 5 distinct gate-sources.

See hypothesis.md for H7.1-H7.4 + pre-committed KILL #106-#110.

NO new infra: reuses 'blend' spec type from iter 018-026 + 'lrs' spec type
with both 'sma' and 'momentum' filters from iter 014/024/026 + 'static'
spec type from iter 015 + 'vol_target' spec type from iter 010; 771 tests
baseline preserved.

Run from repo root with .venv active::

    PYTHONPATH=. python studies/spy_beater_hunt/iterations/027-2026-04-30-H7-meta-ensemble-5way-vol-target-gate-source-diversity/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 27
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "H7-meta-ensemble-5way-vol-target-gate-source-diversity"
PRIMARY_CITATION = (
    "[advances_fin_ml, ch.16, p.241-256] portfolio construction over "
    "multiple alpha streams (5-way meta-ensemble at strategy-level with "
    "vol-target gate-source-diversity falsification test) + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking "
    "generalized to 5 distinct gate-sources + "
    "[systematic_trading, ch.10] Carver vol-targeting canonical (C1 5th "
    "constituent — NEW gate-mechanism: realized-vol-state) + "
    "Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-"
    "250 (E1 TSMOM 6m gate-source) + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate "
    "(A2 QQQ-track + G2 SPY-track LETF F1 — SMA gate-source family) + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM in A2/G2/E1 "
    "ON-state) + "
    "Bridgewater All-Weather (Dalio 1996) F1 stack ON-state + "
    "[advances_fin_ml, p.31-34] factor framework — meta-ensemble axis "
    "11th iter (5-way vol-target gate-source-diversity test) + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials = 104 "
    "(Bonferroni 4.81e-04) + "
    "[advances_fin_ml, p.208-211] PBO grid-level N=4 stability"
)

# Cumulative: prior iters 001-026 = 100. This iter adds 4 -> 104.
PRIOR_CUMULATIVE_N_TRIALS = 100
N_CONFIGS = 4
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 104


# Constituent A (iter 006 a6_tqqq_split_kmlm30_tlt10) — same as iter 018-026.
# Highest-CAGR LRS-mono constituent (~17.33% solo); CAGR-floor anchor.
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

# Constituent B (iter 017 g2_f1_letf_2x_sma200_ief) — same as iter 018-026.
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

# Constituent D (iter 014 e1_tqqq_split_kmlm30_tlt10_tsmom6m) — same as iter 026.
# Gate-source: TSMOM-6m-QQQ (~126d momentum on QQQSIM signal).
E1_TSMOM6M_SPEC = {
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

# Constituent E (iter 010 c1_vt20_sso) — NEW for iter 027.
# Carver vol-target SSO 2x, target 20% annualized vol, 60d realized-vol signal.
# Solo CAGR 13.54% (mean lh+spy) / Sharpe 0.72 / MDD 41.86%. Most conservative
# C1 variant (lowest MDD; cleanest gate-source signature).
# Gate-source: realized-vol-state — DIFFERENT mechanism from SMA-cross
# (A2/G2), TSMOM-momentum (E1), and always-on (F1 stack).
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
    # H7.1 — equal-weight 5-way (CORE FALSIFICATION TEST).
    # Linear decomposition predicts: 71 − 2 base + 1 (E1) + 1 (C1) = 71.
    # If actual ≥ 72: KILL #106 FIRED, principle FALSIFIED, ceiling broken.
    # If actual = 71: KILL #108 FIRED, principle VALIDATED.
    # If actual ≤ 70: KILL #107 FIRED, principle CONFIRMED as upper bound.
    "h7_meta_5way_20a2_20g2_20f1_20e1_20c1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.20, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.20, "spec": G2_IEF_SPEC},
            {"weight": 0.20, "spec": F1_STACK_SPEC},
            {"weight": 0.20, "spec": E1_TSMOM6M_SPEC},
            {"weight": 0.20, "spec": C1_VT20_SSO_SPEC},
        ],
    },
    # H7.2 — asymmetric 5-way preserving A2 closest-to-winner tilt.
    # Tests if asymmetric weights can recover 5-way base tax via A2 dominance.
    # Lower E1+C1 dose minimizes their lower-Sharpe drag on blend.
    "h7_meta_5way_30a2_20g2_20f1_15e1_15c1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.30, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.20, "spec": G2_IEF_SPEC},
            {"weight": 0.20, "spec": F1_STACK_SPEC},
            {"weight": 0.15, "spec": E1_TSMOM6M_SPEC},
            {"weight": 0.15, "spec": C1_VT20_SSO_SPEC},
        ],
    },
    # H7.3 — 4-way with C1 substituting E1 (vol-target gate vs TSMOM gate).
    # Tests KILL #109: is vol-target gate-mechanism preferred over TSMOM at 4-way?
    # Direct comparison vs iter 026 H6.1 (4-way with E1 instead of C1, score 71).
    "h7_meta_4way_25a2_25g2_25f1_25c1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": C1_VT20_SSO_SPEC},
        ],
    },
    # H7.4 — 3-way with C1 substituting F1 stack.
    # Tests KILL #110: does vol-target gate match always-on stack value as 3rd
    # constituent? Direct test of iter 025 KILL #97 / iter 026 KILL #104
    # generalization on F1 stack's natural-diversification advantage.
    "h7_meta_3way_33a2_33g2_34c1": {
        "type": "blend",
        "constituents": [
            {"weight": 0.33, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.33, "spec": G2_IEF_SPEC},
            {"weight": 0.34, "spec": C1_VT20_SSO_SPEC},
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
            f"  [{bar_pass}] {cfg:>45s}: CAGR {mean_cagr*100:+.2f}%  "
            f"MDD {mean_mdd*100:.2f}%  Sharpe {mean_sharpe:.3f}"
        )
