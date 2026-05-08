"""Iter 031 driver: H11 META-ENSEMBLE 4-WAY GLD-TSMOM LOOKBACK AXIS — signal-
asset fixed at GLD (per iter 030 KILL #125 ceiling-breach), varying TSMOM
lookback (3m/6m/9m/12m) at 4th constituent slot.

Iter 030 KILL #125 FIRED — ORTHOGONAL-ASSET-CLASS-TSMOM-SOURCE BONUS at
4-way meta-ensemble: GLD-TSMOM-6m signal on TQQQ-stack sleeve outperforms
QQQ-TSMOM-6m baseline by +1pt (+0.74pp CAGR / +0.083 Sharpe at 25% dose).
First ceiling-breach in 9 sequential meta-axis iters.

Iter 029 KILL #119 FIRED — TSMOM-LOOKBACK INVERTED-U for QQQ-TSMOM at 4th
constituent slot, peak at ~6m. Generalization explicitly noted: "lookback-
peak-optimum may differ for other signal-asset combinations".

Iter 031 directly tests the joint surface — holding signal-asset fixed at
GLD (per iter 030 ceiling-breach) and varying TSMOM lookback (3m/6m/9m/12m).
GLD has lower realized volatility than QQQ (~14-18% vs ~22-28%) → lower-vol
asset trends are typically slower-decaying → optimal lookback may be
LONGER than QQQ's 6m peak.

Four lookback variants tested at 4th constituent slot (signal_ticker=GLDSIM
fixed, sleeve TQQQSIM 30 + QLDSIM 30 + KMLMSIM 30 + TLTSIM 10 fixed,
weight 25% fixed = iter 030 H10.4 baseline):

  - GLD-TSMOM-3m: short-lookback whipsaw test
  - GLD-TSMOM-6m: BASELINE replicates iter 030 H10.4 (expected ≈72)
  - GLD-TSMOM-9m: KEY HYPOTHESIS — GLD lower-vol → longer trend
  - GLD-TSMOM-12m: Moskowitz canonical TSMOM lookback

Constituents A2, G2, F1 reused verbatim from iter 026/029/030. Only 4th
constituent's `lookback_days` parameter changes — isolating lookback effect
within fixed sleeve composition AND fixed signal_ticker (GLDSIM).

Per Moskowitz-Ooi-Pedersen (2012) JFE 104(2):228-250, TSMOM-12m is canonical
with 1m/3m/6m/9m robustness checks. Per Faber GTAA, single-asset 6-10m
moving averages are canonical (DBC commodity proxy 10m).

See hypothesis.md for H11.1-H11.4 + pre-committed KILL #127-#132.

NO new infra: reuses 'blend' spec type from iter 018-030 + 'lrs' spec
type with 'momentum' filter from iter 014/024/026/028/029/030 (varied
lookback_days only) + 'static' spec type from iter 015. 771 tests
baseline preserved.

Run from repo root with .venv active::

    PYTHONPATH=. python studies/spy_beater_hunt/iterations/031-2026-04-30-H11-meta-ensemble-4way-gld-tsmom-lookback-axis/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 31
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "H11-meta-ensemble-4way-gld-tsmom-lookback-axis"
PRIMARY_CITATION = (
    "[advances_fin_ml, ch.16, p.241-256] portfolio construction over "
    "multiple alpha streams (4-way meta-ensemble at strategy-level with "
    "GLD-source lookback sub-axis exploration — 15th iter at meta-axis) + "
    "Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 "
    "(canonical TSMOM-12m with 1m/3m/6m/9m robustness across asset classes; "
    "iter 031 tests GLD signal-source × lookback joint surface) + "
    "[ivy_portfolio] Faber GTAA single-asset 6-10m moving average "
    "(commodity proxy DBC-10m; iter 031 tests GLD at 3m/6m/9m/12m bracket) + "
    "[asness_value_momentum] momentum-everywhere across asset classes "
    "(commodity TSMOM premium structure) + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate "
    "(A2 QQQ-track + G2 SPY-track LETF F1 constituents preserved) + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking "
    "(F1 stack always-on retained at 3rd constituent — sextuple-confirmed "
    "uniquely-Pareto-optimal per iter 027 KILL #110 + iter 028/029/030 implicit) + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM in A2/G2/E1 "
    "ON-state) + "
    "Bridgewater All-Weather (Dalio 1996) F1 stack ON-state + "
    "iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way) + "
    "iter 029 KILL #119 (TSMOM-lookback inverted-U at 6m for QQQ; "
    "signal-asset generalization explicit) + "
    "iter 030 KILL #125 (orthogonal-asset-class-TSMOM-source bonus +1pt) + "
    "[advances_fin_ml, p.31-34] factor framework — meta-ensemble axis "
    "15th iter (GLD-source lookback sub-axis exploration) + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials = 120 (Bonferroni "
    "4.17e-04) + "
    "[advances_fin_ml, p.208-211] PBO grid-level N=4 stability"
)

# Cumulative: prior iters 001-030 = 116. This iter adds 4 -> 120.
PRIOR_CUMULATIVE_N_TRIALS = 116
N_CONFIGS = 4
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 120


# Constituent A (iter 006 a6_tqqq_split_kmlm30_tlt10) — reused verbatim from
# iter 026/029/030. Highest-CAGR constituent (~17.33%); CAGR-floor anchor.
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

# Constituent B (iter 017 g2_f1_letf_2x_sma200_ief) — reused verbatim from
# iter 026/029/030. Gate-source: SPY-200d-SMA.
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
# Gate-source: always-on (no gate). Reused verbatim from iter 026/029/030.
F1_STACK_SPEC = {
    "type": "static",
    "weights": {
        "NTSXSIM": 0.35,
        "GDESIM": 0.30,
        "TLTSIM": 0.20,
        "KMLMSIM": 0.15,
    },
}

# Constituent D — iter 031 NEW GLD-TSMOM lookback variants. Signal-asset
# FIXED at GLDSIM (per iter 030 KILL #125 ceiling-breach). ON-sleeve
# identical to iter 030 H10.4 E1_GLD to isolate lookback effect.
#
# E1_GLD_3M — short-lookback whipsaw test (replicates iter 029 H9.4 pattern
# but on GLD signal source instead of QQQ).
E1_GLD_TSMOM3M_SPEC = {
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
    "signal_ticker": "GLDSIM",
    "lag_days": 1,
}

# E1_GLD_6M — BASELINE replicates iter 030 H10.4 (selected closest-to-winner
# at score 72). Provides anchor for KILL #127/#128 and lookback-axis
# variations.
E1_GLD_TSMOM6M_SPEC = {
    "type": "lrs",
    "filter": "momentum",
    "lookback_days": 126,  # ~6 calendar months — iter 030 H10.4 selected baseline
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

# E1_GLD_9M — KEY HYPOTHESIS — GLD lower-vol → longer trend persistence.
# Tests KILL #129 (asset-variant lookback peak).
E1_GLD_TSMOM9M_SPEC = {
    "type": "lrs",
    "filter": "momentum",
    "lookback_days": 189,  # ~9 calendar months — lower-vol asset trend persistence
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

# E1_GLD_12M — Moskowitz canonical TSMOM-12m lookback applied to GLD source.
# Tests longer-lookback robustness on commodity TSMOM premium per
# [asness_value_momentum].
E1_GLD_TSMOM12M_SPEC = {
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
    "signal_ticker": "GLDSIM",
    "lag_days": 1,
}


CONFIGS = {
    # H11.1 — equal-weight 4-way 25/25/25/25 with E1_GLD_3M at 4th constituent.
    # Tests short-lookback whipsaw cost on GLD signal source. Inverts iter
    # 029 H9.4 pattern (QQQ-3m at 25%) by changing signal-asset to GLD.
    "h11_meta_4way_25a2_25g2_25f1_25e1gld_3m": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_GLD_TSMOM3M_SPEC},
        ],
    },
    # H11.2 — BASELINE — replicates iter 030 H10.4 selected config (score 72).
    # Tests KILL #127/#128 (ceiling) and provides anchor for KILL #129/#130/
    # #131/#132.
    "h11_meta_4way_25a2_25g2_25f1_25e1gld_6m": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_GLD_TSMOM6M_SPEC},
        ],
    },
    # H11.3 — KEY HYPOTHESIS — GLD-TSMOM-9m at 4th constituent.
    # Lower-vol asset trend persistence test. If H11.3 > H11.2 by ≥ 1pt →
    # KILL #129 fires (asset-variant lookback peak).
    "h11_meta_4way_25a2_25g2_25f1_25e1gld_9m": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_GLD_TSMOM9M_SPEC},
        ],
    },
    # H11.4 — Moskowitz canonical TSMOM-12m on GLD signal source.
    # Tests longer-lookback robustness on commodity TSMOM premium.
    "h11_meta_4way_25a2_25g2_25f1_25e1gld_12m": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_GLD_TSMOM12M_SPEC},
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
            f"  [{bar_pass}] {cfg:>50s}: CAGR {mean_cagr*100:+.2f}%  "
            f"MDD {mean_mdd*100:.2f}%  Sharpe {mean_sharpe:.3f}"
        )
