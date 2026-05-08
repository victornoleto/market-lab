"""Iter 035 driver: H15 META-ENSEMBLE 4-WAY GLD-mom-126d OFF-STATE COMPOSITION
SUB-AXIS — varying OFF-state composition of E1gld constituent (IEF / KMLM /
TLT / Blend) holding the strategy spec at iter 030 H10.4 apex EXCEPT for the
4th constituent's off_weights parameter.

19th iter at meta-ensemble axis. Tests whether the +1pt Principle A bonus
(iter 030 KILL #125 / iter 033 KILL #144 revised to GOLD-SPECIFIC) for
GLD-mom-126d at 4th depends on off-state composition. Last single-axis
sub-axis around the iter 030 apex without new data infrastructure.

iter 016 G1 hybrid prior (post-impossibility second hybrid sanity check)
established monotonic OFF-state composition dose-response IEF > 50/50 IEF+KMLM
> KMLM for SPY-track stack. H15 tests if this generalizes to GLD-track
3x LETF sleeve.

Linear decomposition prediction (iter 026 KILL #103):
   H15 score = 72 (4-way E1gld baseline iter 030 H10.4)
             + (off-state-axis perturbation Δ)

Falsification: max H15 >= 74 strong-form breach (KILL #152); max H15 = 73
ceiling-tied; max H15 ≤ 71 off-state composition Pareto-degrades baseline.

Four configs:
  - H15.1 (BASELINE): IEF off — replicates iter 030 H10.4 EXACTLY (anchor)
  - H15.2: KMLM off — managed-futures crisis-alpha when GLD trend OFF
  - H15.3: TLT off — long-duration UST when GLD trend OFF
  - H15.4: Blend off (50% IEF + 50% KMLM) — iter 016 G1 hybrid pattern test

A2, G2, F1 specs reused VERBATIM from iter 026/030/031/032/033/034. ONLY the
E1gld constituent's off_weights parameter varies across H15.1-H15.4.

See hypothesis.md for KILL #151-#156.

NO new infra: reuses 'blend' + 'lrs' (sma + momentum filters with
`off_weights` parameter varied) + 'static' spec types from iter 010/014/
015/018-034. 771 tests baseline preserved. TLTSIM, GLDSIM, IEFSIM,
KMLMSIM, QQQSIM, SPYSIM all in testfolio cache.

Run from repo root with .venv active::

    PYTHONPATH=. python studies/spy_beater_hunt/iterations/035-2026-04-30-H15-meta-ensemble-4way-gld-mom-off-state-composition/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 35
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "H15-meta-ensemble-4way-gld-mom-off-state-composition"
PRIMARY_CITATION = (
    "[advances_fin_ml, ch.16, p.241-256] portfolio construction over "
    "multiple alpha streams (4-way meta-ensemble at strategy-level, 19th "
    "iter at meta-axis, NEW sub-axis: off-state composition for GLD "
    "constituent) + "
    "[ilmanen_expected_returns, ch.19] Managed-futures crisis-alpha role "
    "(KMLM off-state hypothesis) + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate "
    "canonical (IEF safe asset off-state baseline) + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking (F1 stack "
    "always-on retained at 3rd constituent — decuple-confirmed uniquely-"
    "Pareto-optimal per iter 034) + "
    "Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 "
    "(E1gld TSMOM-126d gate-source on commodity-class) + "
    "Asness-Moskowitz-Pedersen (2013) Value and Momentum Everywhere, JoF "
    "68(3):929-985 (momentum across asset classes) + "
    "Bridgewater All-Weather (Dalio 1996) F1 stack ON-state composition + "
    "iter 016 G1 hybrid (off-state composition dose-response monotonic IEF > "
    "Blend > KMLM for SPY-track stack) + "
    "iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way) — held "
    "fixed via E1gld at 4th + "
    "iter 026 KILL #103 (linear decomposition principle) — UPPER-BOUND test + "
    "iter 030 KILL #125 / Principle A (orthogonal-asset-class-TSMOM-source "
    "bonus +1pt) — operative + "
    "iter 030 KILL #126 / Principle C (signal-sleeve incoherence Pareto-"
    "positive) — held fixed + "
    "iter 031 KILL #130 / Principle D (TSMOM-lookback inverted-U asset-"
    "invariant peak at 6m / 126d) — held fixed at 126d + "
    "iter 032 KILL #135 / Principle G (orthogonality bonus filter-type-"
    "coupled to momentum) — held fixed at filter=momentum + "
    "iter 033 KILL #144 / Principle J (orthogonality bonus is COMMODITY-"
    "GOLD-SPECIFIC) — operative + "
    "iter 034 KILL #150 / Principle M (rubric score is grid-composition-"
    "dependent via G1 PBO) — caveat for cross-iter score comparison + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials = 136 (Bonferroni "
    "3.68e-04) + "
    "[advances_fin_ml, p.208-211] PBO grid-level N=4 stability"
)

# Cumulative: prior iters 001-034 = 132. This iter adds 4 -> 136.
PRIOR_CUMULATIVE_N_TRIALS = 132
N_CONFIGS = 4
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 136


# ---------------------------------------------------------------------------
# Constituent specs (reused VERBATIM from iter 026/027/030/031/032/033/034)
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
# Gate-source: always-on (no gate). Decuple-confirmed uniquely-Pareto-optimal
# at 3rd position per iter 034.
F1_STACK_SPEC = {
    "type": "static",
    "weights": {
        "NTSXSIM": 0.35,
        "GDESIM": 0.30,
        "TLTSIM": 0.20,
        "KMLMSIM": 0.15,
    },
}

# ---------------------------------------------------------------------------
# E1gld variants — only off_weights parameter varies (iter 035 H15 sub-axis)
# ---------------------------------------------------------------------------

# H15.1 — IEF off (BASELINE — replicates iter 030 H10.4 EXACTLY)
E1_GLD_MOM126_IEF_OFF_SPEC = {
    "type": "lrs",
    "filter": "momentum",
    "lookback_days": 126,
    "on_weights": {
        "TQQQSIM": 0.30,
        "QLDSIM": 0.30,
        "KMLMSIM": 0.30,
        "TLTSIM": 0.10,
    },
    "off_weights": {"IEFSIM": 1.0},  # BASELINE
    "signal_ticker": "GLDSIM",
    "lag_days": 1,
}

# H15.2 — KMLM off (managed-futures crisis-alpha when GLD trend OFF)
E1_GLD_MOM126_KMLM_OFF_SPEC = {
    "type": "lrs",
    "filter": "momentum",
    "lookback_days": 126,
    "on_weights": {
        "TQQQSIM": 0.30,
        "QLDSIM": 0.30,
        "KMLMSIM": 0.30,
        "TLTSIM": 0.10,
    },
    "off_weights": {"KMLMSIM": 1.0},  # 100% MF crisis-alpha
    "signal_ticker": "GLDSIM",
    "lag_days": 1,
}

# H15.3 — TLT off (long-duration UST 20+y when GLD trend OFF)
E1_GLD_MOM126_TLT_OFF_SPEC = {
    "type": "lrs",
    "filter": "momentum",
    "lookback_days": 126,
    "on_weights": {
        "TQQQSIM": 0.30,
        "QLDSIM": 0.30,
        "KMLMSIM": 0.30,
        "TLTSIM": 0.10,
    },
    "off_weights": {"TLTSIM": 1.0},  # 100% long-duration UST
    "signal_ticker": "GLDSIM",
    "lag_days": 1,
}

# H15.4 — Blend off (50% IEF + 50% KMLM) — iter 016 G1 hybrid pattern test
E1_GLD_MOM126_BLEND_OFF_SPEC = {
    "type": "lrs",
    "filter": "momentum",
    "lookback_days": 126,
    "on_weights": {
        "TQQQSIM": 0.30,
        "QLDSIM": 0.30,
        "KMLMSIM": 0.30,
        "TLTSIM": 0.10,
    },
    "off_weights": {"IEFSIM": 0.5, "KMLMSIM": 0.5},  # 50/50 blend
    "signal_ticker": "GLDSIM",
    "lag_days": 1,
}


CONFIGS = {
    # H15.1 — BASELINE / ANCHOR: IEF off — replicates iter 030 H10.4 / iter
    # 031 H11.2 / iter 032 H12.1 / iter 033 H13.2 / iter 034 H14.4 EXACTLY
    # (sextuple-replication test of Principle M). Expected score 72-73 in
    # rubric noise band per Principle M.
    "h15_meta_4way_25a2_25g2_25f1_25e1gld_mom126_ief_off": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_GLD_MOM126_IEF_OFF_SPEC},
        ],
    },
    # H15.2 — KMLM off: managed-futures crisis-alpha when GLD trend OFF.
    # KILL #154 FIRED if H15.2 >= H15.1 by >= 1pt (crisis-alpha bonus).
    "h15_meta_4way_25a2_25g2_25f1_25e1gld_mom126_kmlm_off": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_GLD_MOM126_KMLM_OFF_SPEC},
        ],
    },
    # H15.3 — TLT off: long-duration UST when GLD trend OFF. Tests duration
    # extension at OFF-state. KILL #155 FIRED if H15.3 < H15.1 by >= 1pt
    # (Principle J extension to off-state position).
    "h15_meta_4way_25a2_25g2_25f1_25e1gld_mom126_tlt_off": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_GLD_MOM126_TLT_OFF_SPEC},
        ],
    },
    # H15.4 — Blend off (50% IEF + 50% KMLM): iter 016 G1 hybrid pattern test.
    # Should fall between H15.1 and H15.2 if monotonic IEF > Blend > KMLM
    # pattern generalizes from SPY-track to GLD-track.
    "h15_meta_4way_25a2_25g2_25f1_25e1gld_mom126_blend_off": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_GLD_MOM126_BLEND_OFF_SPEC},
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
            f"  [{bar_pass}] {cfg:>56s}: CAGR {mean_cagr*100:+.2f}%  "
            f"MDD {mean_mdd*100:.2f}%  Sharpe {mean_sharpe:.3f}"
        )
