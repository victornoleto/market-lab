"""Iter 036 driver: H16 META-ENSEMBLE 4-WAY A2 OFF-STATE COMPOSITION SUB-AXIS
— varying OFF-state composition of A2 constituent (IEF / KMLM / TLT / Blend)
holding the strategy spec at iter 035 H15.2 strategy-level apex EXCEPT for
the A2 (1st-position) constituent's off_weights parameter.

20th iter at meta-ensemble axis. Tests whether Principle N (iter 035 KILL
#154 — KMLM off > IEF off by +2pt for GLD-track gate-decision) generalizes
to A2's QQQ-track gate-decision OR is gate-source-asset-class-COUPLED.

Per Principle N mechanism (off-state asset must align with gate-source's
regime structure):
  - A2 = QQQ-track 200d-SMA gate. A2-OFF = NDX-equity-bear regimes
    (2000-02 dotcom -78%, 2008 GFC, 2022 inflation, 2020 COVID).
  - Per iter 016 G1 hybrid (SPY-track): IEF > Blend > KMLM at OFF.
  - Predicted: A2 KMLM off ≤ A2 IEF off (Principle N reverses for
    equity-track via constituent-coupling).

Linear decomposition prediction (iter 026 KILL #103 + Principle N):
   H16 score = 74 (4-way E1gld+KMLM-off baseline iter 035 H15.2)
             + (A2 off-state-axis perturbation Δ)

Falsification:
  - max H16 ≥ 75 strong-form breach (KILL #158)
  - max H16 = 74 ceiling-tied (constituent-coupled OR rubric-saturated)
  - max H16 ≤ 73 off-state composition Pareto-degrades baseline at A2

Four configs:
  - H16.1 (BASELINE): A2 IEF off — replicates iter 035 H15.2 EXACTLY (anchor)
  - H16.2: A2 KMLM off — managed-futures crisis-alpha when QQQ trend OFF
  - H16.3: A2 TLT off — long-duration UST when QQQ trend OFF
  - H16.4: A2 Blend off (50% IEF + 50% KMLM) — iter 016 G1 hybrid pattern

G2, F1, E1gld+KMLM-off specs reused VERBATIM from iter 035 H15.2 apex. ONLY
the A2 constituent's off_weights parameter varies across H16.1-H16.4.

See hypothesis.md for KILL #157-#162.

NO new infra: reuses 'blend' + 'lrs' (sma + momentum filters with
`off_weights` parameter varied) + 'static' spec types from iter 010/014/
015/018-035. 771 tests baseline preserved. TLTSIM, GLDSIM, IEFSIM, KMLMSIM,
QQQSIM, SPYSIM all in testfolio cache.

Run from repo root with .venv active::

    PYTHONPATH=. python studies/spy_beater_hunt/iterations/036-2026-04-30-H16-meta-ensemble-4way-a2-off-state-composition/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 36
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "H16-meta-ensemble-4way-a2-off-state-composition"
PRIMARY_CITATION = (
    "[advances_fin_ml, ch.16, p.241-256] portfolio construction over "
    "multiple alpha streams (4-way meta-ensemble at strategy-level, 20th "
    "iter at meta-axis, NEW sub-axis: A2 off-state composition test of "
    "Principle N constituent-coupling) + "
    "[ilmanen_expected_returns, ch.19] Managed-futures crisis-alpha role "
    "(Principle N source — KMLM off-state hypothesis at equity-track) + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate "
    "canonical (A2 QQQ-track + G2 SPY-track + IEF off-state default) + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking (F1 stack "
    "always-on retained at 3rd constituent — undecuple-confirmed) + "
    "Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 "
    "(E1gld TSMOM-126d held fixed at apex) + "
    "Asness-Moskowitz-Pedersen (2013) Value and Momentum Everywhere, JoF "
    "68(3):929-985 + "
    "Bridgewater All-Weather (Dalio 1996) F1 stack ON-state composition + "
    "iter 016 G1 hybrid (off-state IEF > Blend > KMLM for SPY-track stack — "
    "predicts H16 same pattern at A2 QQQ-track if Principle N constituent-"
    "coupled) + "
    "iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way) — held "
    "fixed via E1gld at 4th + "
    "iter 026 KILL #103 (linear decomposition principle) — UPPER-BOUND test + "
    "iter 030 KILL #125 / Principle A (orthogonal-asset-class-TSMOM-source "
    "bonus +1pt) — held fixed + "
    "iter 030 KILL #126 / Principle C (signal-sleeve incoherence Pareto-"
    "positive) — held fixed + "
    "iter 031 KILL #130 / Principle D (TSMOM-lookback inverted-U asset-"
    "invariant peak at 6m / 126d) — held fixed at 126d + "
    "iter 032 KILL #135 / Principle G (orthogonality bonus filter-type-"
    "coupled to momentum) — held fixed at filter=momentum + "
    "iter 033 KILL #144 / Principle J (orthogonality bonus is COMMODITY-"
    "GOLD-SPECIFIC) — operative + "
    "iter 034 KILL #150 / Principle M (rubric score is grid-composition-"
    "dependent via G1 PBO) — caveat + "
    "iter 035 KILL #154 / Principle N (off-state crisis-alpha is asset-"
    "class-conditional) — CONSTITUENT-COUPLING TEST is the headline + "
    "iter 035 KILL #156 (H15.1 sextuple-replication via Principle M) — "
    "H16.1 septuple-replication test (7 independent measurements) + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials = 140 (Bonferroni "
    "3.57e-04) + "
    "[advances_fin_ml, p.208-211] PBO grid-level N=4 stability"
)

# Cumulative: prior iters 001-035 = 136. This iter adds 4 -> 140.
PRIOR_CUMULATIVE_N_TRIALS = 136
N_CONFIGS = 4
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 140


# ---------------------------------------------------------------------------
# A2 variants — only off_weights parameter varies (iter 036 H16 sub-axis)
# ---------------------------------------------------------------------------

# H16.1 — A2 IEF off (BASELINE — replicates iter 035 H15.2 EXACTLY)
A2_IEF_OFF_SPEC = {
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
    "off_weights": {"IEFSIM": 1.0},  # BASELINE
    "signal_ticker": "QQQSIM",
    "lag_days": 1,
}

# H16.2 — A2 KMLM off (managed-futures crisis-alpha when QQQ trend OFF)
A2_KMLM_OFF_SPEC = {
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
    "off_weights": {"KMLMSIM": 1.0},  # 100% MF crisis-alpha
    "signal_ticker": "QQQSIM",
    "lag_days": 1,
}

# H16.3 — A2 TLT off (long-duration UST 20+y when QQQ trend OFF)
A2_TLT_OFF_SPEC = {
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
    "off_weights": {"TLTSIM": 1.0},  # 100% long-duration UST
    "signal_ticker": "QQQSIM",
    "lag_days": 1,
}

# H16.4 — A2 Blend off (50% IEF + 50% KMLM) — iter 016 G1 hybrid pattern test
A2_BLEND_OFF_SPEC = {
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
    "off_weights": {"IEFSIM": 0.5, "KMLMSIM": 0.5},  # 50/50 blend
    "signal_ticker": "QQQSIM",
    "lag_days": 1,
}

# ---------------------------------------------------------------------------
# Constituent specs (reused VERBATIM from iter 026/027/030/031/032/033/034/035)
# ---------------------------------------------------------------------------

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
# Gate-source: always-on (no gate). Undecuple-confirmed uniquely-Pareto-optimal
# at 3rd position per iter 035.
F1_STACK_SPEC = {
    "type": "static",
    "weights": {
        "NTSXSIM": 0.35,
        "GDESIM": 0.30,
        "TLTSIM": 0.20,
        "KMLMSIM": 0.15,
    },
}

# Constituent D (iter 035 H15.2 apex) — E1gld with KMLM off-state.
# Gate-source: GLD-mom-126d (Principle A operative; Principle N apex).
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
    "off_weights": {"KMLMSIM": 1.0},  # iter 035 H15.2 APEX (Principle N)
    "signal_ticker": "GLDSIM",
    "lag_days": 1,
}


CONFIGS = {
    # H16.1 — BASELINE / ANCHOR: A2 IEF off — replicates iter 035 H15.2
    # EXACTLY. Septuple-replication test of Principle M (now 7 independent
    # measurements: iter 030/031/032/033/034 H10.4-H14.4 baseline anchor +
    # iter 035 H15.1 IEF anchor + iter 036 H16.1 IEF anchor).
    # Expected score 74 ±1pt rubric noise band per Principle M.
    "h16_meta_4way_25a2_25g2_25f1_25e1gld_mom126_kmlm_off_a2_ief_off": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_IEF_OFF_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_GLD_MOM126_KMLM_OFF_SPEC},
        ],
    },
    # H16.2 — A2 KMLM off: managed-futures crisis-alpha when QQQ trend OFF.
    # PRINCIPLE N CONSTITUENT-COUPLING TEST (the headline KILL #160).
    # If H16.2 < H16.1 by ≥ 1pt → constituent-coupled (equity-track requires
    # IEF; commodity-track requires KMLM). If H16.2 ≥ H16.1 by ≥ 1pt →
    # constituent-axis-independent (KMLM off universally Pareto-positive).
    "h16_meta_4way_25a2_25g2_25f1_25e1gld_mom126_kmlm_off_a2_kmlm_off": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_KMLM_OFF_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_GLD_MOM126_KMLM_OFF_SPEC},
        ],
    },
    # H16.3 — A2 TLT off: long-duration UST when QQQ trend OFF. Tests
    # duration extension at OFF-state at A2 position. KILL #161 NOT FIRED if
    # within ±1pt vs H16.1 (TLT Pareto-neutral pattern from iter 035 H15.3
    # generalizes to A2 position).
    "h16_meta_4way_25a2_25g2_25f1_25e1gld_mom126_kmlm_off_a2_tlt_off": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_TLT_OFF_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_GLD_MOM126_KMLM_OFF_SPEC},
        ],
    },
    # H16.4 — A2 Blend off (50% IEF + 50% KMLM): iter 016 G1 hybrid pattern
    # test at A2 position. Should fall between H16.1 and H16.2 if linear
    # interpolation HOLDS at A2 position (per iter 035 H15.4 confirming for
    # GLD position).
    "h16_meta_4way_25a2_25g2_25f1_25e1gld_mom126_kmlm_off_a2_blend_off": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_BLEND_OFF_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_GLD_MOM126_KMLM_OFF_SPEC},
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
            f"  [{bar_pass}] {cfg:>72s}: CAGR {mean_cagr*100:+.2f}%  "
            f"MDD {mean_mdd*100:.2f}%  Sharpe {mean_sharpe:.3f}"
        )
