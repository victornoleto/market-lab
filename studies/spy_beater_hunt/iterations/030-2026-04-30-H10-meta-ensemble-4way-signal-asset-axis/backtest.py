"""Iter 030 driver: H10 META-ENSEMBLE 4-WAY SIGNAL-ASSET AXIS — TSMOM-6m
fixed lookback, varying signal_ticker (QQQ baseline / SPY redundancy /
GLD orthogonal) at 4th constituent slot.

Iter 029 KILL #119 established TSMOM-LOOKBACK INVERTED-U for QQQ-TSMOM
gate at 4th constituent slot, peak at ~6m, with explicit generalization:
"lookback-peak-optimum may differ for other signal-asset combinations".
Iter 030 directly tests SIGNAL-ASSET sub-axis at fixed 6m lookback to
isolate signal-source effect from lookback-effect.

Three signal-source variants tested (4 configs total):

  - QQQ-TSMOM-6m: BASELINE replicates iter 026 H6.4 (expected ≈71)
  - SPY-TSMOM-6m: signal-source DUPLICATES G2's SPY-200d-SMA (expected
    score loss via gate-source-redundancy → tests KILL #124)
  - GLD-TSMOM-6m: signal-source ORTHOGONAL equity (expected gate-source-
    distinctness preserved/strengthened, but signal-sleeve mismatch risk
    on TQQQ-stack — KILL #126)

Constituents A2, G2, F1 reused verbatim from iter 026/029. Only 4th
constituent's `signal_ticker` parameter changes — isolating signal-asset
effect within fixed sleeve composition AND fixed lookback (126 days).

Per Moskowitz-Ooi-Pedersen (2012) JFE 104(2):228-250, TSMOM is robust
across asset classes (equity / bond / commodity / FX). Gold-TSMOM is a
canonical TSMOM signal-source. Faber GTAA (ivy_portfolio) uses 5-asset
multi-signal moving averages including DBC commodity proxy.

See hypothesis.md for H10.1-H10.4 + pre-committed KILL #121-#126.

NO new infra: reuses 'blend' spec type from iter 018-029 + 'lrs' spec
type with 'momentum' filter from iter 014/024/026/028/029 (varied
signal_ticker only) + 'static' spec type from iter 015. 771 tests
baseline preserved.

Run from repo root with .venv active::

    PYTHONPATH=. python studies/spy_beater_hunt/iterations/030-2026-04-30-H10-meta-ensemble-4way-signal-asset-axis/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 30
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "H10-meta-ensemble-4way-signal-asset-axis"
PRIMARY_CITATION = (
    "[advances_fin_ml, ch.16, p.241-256] portfolio construction over "
    "multiple alpha streams (4-way meta-ensemble at strategy-level with "
    "signal-asset sub-axis exploration — 14th iter at meta-axis) + "
    "Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 "
    "(TSMOM robustness across equity/bond/commodity/FX asset classes; "
    "iter 030 tests QQQ vs SPY vs GLD signal-source at fixed 6m lookback) + "
    "[ivy_portfolio] Faber GTAA multi-asset moving averages (5-asset breadth "
    "SPY+EFA+VWO+IEF+DBC; iter 030 tests 3 signal sources within meta-axis) + "
    "[asness_value_momentum] momentum-everywhere across asset classes + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate "
    "(A2 QQQ-track + G2 SPY-track LETF F1 constituents preserved) + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking "
    "(F1 stack always-on retained at 3rd constituent — quintuple-confirmed "
    "uniquely-Pareto-optimal per iter 027 KILL #110 + iter 028/029 implicit) + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM in A2/G2/E1 "
    "ON-state) + "
    "Bridgewater All-Weather (Dalio 1996) F1 stack ON-state + "
    "iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way) + "
    "iter 029 KILL #119 (TSMOM-lookback inverted-U; signal-asset generalization) + "
    "[advances_fin_ml, p.31-34] factor framework — meta-ensemble axis "
    "14th iter (signal-asset sub-axis exploration) + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials = 116 (Bonferroni "
    "4.31e-04) + "
    "[advances_fin_ml, p.208-211] PBO grid-level N=4 stability"
)

# Cumulative: prior iters 001-029 = 112. This iter adds 4 -> 116.
PRIOR_CUMULATIVE_N_TRIALS = 112
N_CONFIGS = 4
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 116


# Constituent A (iter 006 a6_tqqq_split_kmlm30_tlt10) — reused verbatim from
# iter 026/029. Highest-CAGR constituent (~17.33%); CAGR-floor anchor.
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
# iter 026/029. Gate-source: SPY-200d-SMA.
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
# Gate-source: always-on (no gate). Reused verbatim from iter 026/029.
F1_STACK_SPEC = {
    "type": "static",
    "weights": {
        "NTSXSIM": 0.35,
        "GDESIM": 0.30,
        "TLTSIM": 0.20,
        "KMLMSIM": 0.15,
    },
}

# Constituent D — iter 030 NEW signal-asset variants. Lookback FIXED at
# 126 (~6m) per iter 029 KILL #119 peak. ON-sleeve identical to iter 026
# H6.4 E1 to isolate signal-asset effect.
#
# E1_QQQ — BASELINE — replicates iter 026 H6.4 (signal=QQQSIM).
E1_QQQ_TSMOM6M_SPEC = {
    "type": "lrs",
    "filter": "momentum",
    "lookback_days": 126,  # ~6 calendar months — iter 029 KILL #119 peak
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

# E1_SPY — SPY-source — duplicates G2's SPY-200d-SMA gate-source.
# Tests KILL #124 (signal-source-redundancy).
E1_SPY_TSMOM6M_SPEC = {
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
    "signal_ticker": "SPYSIM",
    "lag_days": 1,
}

# E1_GLD — GLD-source — orthogonal to equity gate-sources.
# Tests KILL #125 (orthogonal-source bonus) AND KILL #126 (sleeve mismatch).
E1_GLD_TSMOM6M_SPEC = {
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


CONFIGS = {
    # H10.1 — BASELINE — replicates iter 026 H6.4 with QQQ-TSMOM-6m signal.
    # Tests KILL #121/#122 (ceiling) and provides anchor for KILL #123/#124/#125.
    "h10_meta_4way_30a2_25g2_25f1_20e1qqq": {
        "type": "blend",
        "constituents": [
            {"weight": 0.30, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.20, "spec": E1_QQQ_TSMOM6M_SPEC},
        ],
    },
    # H10.2 — SPY-source — SPY-TSMOM-6m duplicates G2 SPY-200d-SMA.
    # Tests KILL #124 (signal-source-redundancy).
    "h10_meta_4way_30a2_25g2_25f1_20e1spy": {
        "type": "blend",
        "constituents": [
            {"weight": 0.30, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.20, "spec": E1_SPY_TSMOM6M_SPEC},
        ],
    },
    # H10.3 — GLD-source — orthogonal to equity gate-sources.
    # Tests KILL #125 (orthogonal-source bonus) and KILL #126 (sleeve mismatch).
    "h10_meta_4way_30a2_25g2_25f1_20e1gld": {
        "type": "blend",
        "constituents": [
            {"weight": 0.30, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.20, "spec": E1_GLD_TSMOM6M_SPEC},
        ],
    },
    # H10.4 — equal-weight 4-way 25/25/25/25 with GLD-TSMOM-6m at 4th.
    # Higher dose of orthogonal-source variant — magnifies KILL #126 risk.
    "h10_meta_4way_25a2_25g2_25f1_25e1gld": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_GLD_TSMOM6M_SPEC},
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
