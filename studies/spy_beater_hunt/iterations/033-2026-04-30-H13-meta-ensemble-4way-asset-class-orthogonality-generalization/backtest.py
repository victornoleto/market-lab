"""Iter 033 driver: H13 META-ENSEMBLE 4-WAY ASSET-CLASS ORTHOGONALITY
GENERALIZATION TEST — varying signal_ticker among {QQQSIM, GLDSIM, TLTSIM,
IEFSIM} at the 4th constituent slot, with filter=momentum and lookback_days=126
held fixed (per iter 032 KILL #135 Principle G filter-type-coupled and iter
031 KILL #130 Principle D lookback inverted-U asset-invariant peak).

Iter 030 KILL #125 FIRED — Principle A: ORTHOGONAL-ASSET-CLASS-TSMOM-SOURCE
BONUS at 4-way meta-ensemble. GLD-momentum-126d signal on TQQQ-stack sleeve
outperforms QQQ-momentum-126d baseline by +1pt (score 71→72, iter 026 H6.1
→ iter 030 H10.4). Mechanism hypothesized: gate-source decorrelation across
asset classes (equity QQQ + equity SPY + always-on stack + orthogonal
commodity Gold) accesses NEW dimension of gate-decorrelation.

Iter 032 KILL #135 FIRED — Principle G: ORTHOGONALITY BONUS IS
FILTER-TYPE-COUPLED to MOMENTUM filter at lookback peak ~6m. SMA/EMA filters
at GLD source LOSE 1-3pt of the bonus. Iter 033 holds filter=momentum +
lookback=126 fixed to isolate the asset-class axis.

Iter 033 directly tests whether Principle A's +1pt bonus is asset-class-
INVARIANT (generalizes from commodity to other orthogonal asset classes
like rates) or COMMODITY-SPECIFIC (requires gold-or-commodity structural
feature beyond asset-class orthogonality).

Four signal_ticker variants tested at the 4th constituent slot (filter
=momentum fixed, lookback_days=126 fixed, sleeve TQQQSIM 30 + QLDSIM 30 +
KMLMSIM 30 + TLTSIM 10 fixed, weight 25% fixed = iter 030 H10.4 baseline):

  - QQQSIM (equity large-cap growth): BASELINE — replicates iter 026 H6.1
    equal-weight 4-way; expected score ~71 (no orthogonality bonus,
    signal-asset matches A2 sleeve class)
  - GLDSIM (commodity gold): ANCHOR — replicates iter 030 H10.4 / iter 031
    H11.2 / iter 032 H12.1 EXACTLY; expected score 72 (Principle A bonus)
  - TLTSIM (rates LT UST 20+y): NEW — rates orthogonality test;
    +1pt if Principle A generalizes to rates
  - IEFSIM (rates intermediate UST 7-10y): NEW — short-duration rates test;
    duration sensitivity within rates orthogonality

Constituents A2, G2, F1 reused VERBATIM from iter 026/029/030/031/032. ONLY
4th constituent's `signal_ticker` parameter changes — isolating
asset-class-orthogonality effect within fixed sleeve composition AND fixed
filter-type AND fixed lookback.

See hypothesis.md for H13.1-H13.4 + pre-committed KILL #139-#144.

NO new infra: reuses 'blend' spec type from iter 018-032 + 'lrs' spec type
with momentum filter from iter 014/026/028/029/030/031 + 'static' spec type
from iter 015. TLTSIM and IEFSIM are in testfolio cache (loaded via
load_testfolio_series). 771 tests baseline preserved.

Run from repo root with .venv active::

    PYTHONPATH=. python studies/spy_beater_hunt/iterations/033-2026-04-30-H13-meta-ensemble-4way-asset-class-orthogonality-generalization/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 33
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "H13-meta-ensemble-4way-asset-class-orthogonality-generalization"
PRIMARY_CITATION = (
    "[advances_fin_ml, ch.16, p.241-256] portfolio construction over "
    "multiple alpha streams (4-way meta-ensemble, 17th iter at meta-axis "
    "with asset-class generalization sub-axis) + "
    "Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 "
    "(TSMOM premium across 58 instruments spanning equities/bonds/FX/"
    "commodities — iter 033 tests rate-signal at meta-ensemble 4-way) + "
    "Asness-Moskowitz-Pedersen (2013) Value and Momentum Everywhere, JoF "
    "68(3):929-985 (momentum pervasive across asset classes — predicts "
    "rates-momentum-126d should carry analogous structure to commodity "
    "gold-momentum-126d) + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate "
    "(A2 + G2 baseline retained) + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking "
    "(F1 stack always-on retained at 3rd constituent — octuple-confirmed "
    "uniquely-Pareto-optimal per iter 032 + iter 028/029/030/031 implicit) + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM in A2/G2 "
    "ON-state) + "
    "Bridgewater All-Weather (Dalio 1996) F1 stack ON-state + "
    "[ivy_portfolio] Faber GTAA — bond-trend signal canonical via 10m MA "
    "(iter 033 tests momentum-equivalent at meta-ensemble 4-way) + "
    "iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way) + "
    "iter 030 KILL #125 (orthogonal-asset-class-TSMOM-source bonus +1pt) — "
    "iter 033 tests generalization beyond commodity to rates + "
    "iter 030 KILL #126 (signal-sleeve incoherence Pareto-neutral, "
    "Principle C) — iter 033 tests with rates source on equity sleeve + "
    "iter 031 KILL #130 (TSMOM-lookback inverted-U asset-invariant peak at "
    "6m) — held fixed at 126d + "
    "iter 032 KILL #135 (orthogonality bonus filter-type-coupled to "
    "momentum, Principle G) — held fixed at filter=momentum + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials = 128 (Bonferroni "
    "3.91e-04) + "
    "[advances_fin_ml, p.208-211] PBO grid-level N=4 stability"
)

# Cumulative: prior iters 001-032 = 124. This iter adds 4 -> 128.
PRIOR_CUMULATIVE_N_TRIALS = 124
N_CONFIGS = 4
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 128


# Constituent A (iter 006 a6_tqqq_split_kmlm30_tlt10) — reused verbatim from
# iter 026/029/030/031/032. Highest-CAGR constituent (~17.33%); CAGR-floor
# anchor. Gate-source: QQQ-200d-SMA.
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
# iter 026/029/030/031/032. Gate-source: SPY-200d-SMA.
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
# Gate-source: always-on (no gate). Reused verbatim from iter 026/029/030/031/032.
F1_STACK_SPEC = {
    "type": "static",
    "weights": {
        "NTSXSIM": 0.35,
        "GDESIM": 0.30,
        "TLTSIM": 0.20,
        "KMLMSIM": 0.15,
    },
}


def _build_e1_mom126_spec(signal_ticker: str) -> dict:
    """Build E1 4th-constituent spec with varying signal_ticker.

    Holds filter=momentum, lookback=126, on/off weights identical to
    iter 030 H10.4 / iter 031 H11.2 / iter 032 H12.1 baseline.

    Args:
        signal_ticker: one of {QQQSIM, GLDSIM, TLTSIM, IEFSIM}.

    Returns:
        LRS spec dict for the 4th constituent.
    """
    return {
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
        "signal_ticker": signal_ticker,
        "lag_days": 1,
    }


# H13.1 — QQQ baseline. Equity (large-cap growth) signal. Replicates iter
# 026 H6.1 equal-weight 4-way. Expected score ~71 (no orthogonality bonus).
E1_QQQ_MOM126_SPEC = _build_e1_mom126_spec("QQQSIM")

# H13.2 — GLD anchor. Commodity gold signal. Replicates iter 030 H10.4 /
# iter 031 H11.2 / iter 032 H12.1 EXACTLY. Expected score 72 (Principle A
# bonus realized — QUADRUPLE-replication anchor point).
E1_GLD_MOM126_SPEC = _build_e1_mom126_spec("GLDSIM")

# H13.3 — TLT NEW. Rates (LT UST 20+y) signal. Tests Principle A's
# generalization beyond commodity to rates asset class. Expected 71-72.
E1_TLT_MOM126_SPEC = _build_e1_mom126_spec("TLTSIM")

# H13.4 — IEF NEW. Rates (intermediate UST 7-10y) signal. Tests duration
# differentiation within rates asset class. Expected 70-72.
E1_IEF_MOM126_SPEC = _build_e1_mom126_spec("IEFSIM")


CONFIGS = {
    # H13.1 — QQQ BASELINE — replicates iter 026 H6.1 (equal-weight 4-way
    # with E1 QQQ-mom-126d at 4th constituent). Expected score ~71. Anchor
    # for Principle A's "no bonus when signal-asset matches sleeve class".
    "h13_meta_4way_25a2_25g2_25f1_25e1qqq_mom126": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_QQQ_MOM126_SPEC},
        ],
    },
    # H13.2 — GLD ANCHOR — replicates iter 030 H10.4 / iter 031 H11.2 /
    # iter 032 H12.1 EXACTLY (selected, score 72). QUADRUPLE-replication
    # anchor for Principle A bonus.
    "h13_meta_4way_25a2_25g2_25f1_25e1gld_mom126": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_GLD_MOM126_SPEC},
        ],
    },
    # H13.3 — TLT NEW — rates LT UST 20+y signal. Tests Principle A's
    # asset-class generalization. KILL #141 fires if score ≥ 72.
    "h13_meta_4way_25a2_25g2_25f1_25e1tlt_mom126": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_TLT_MOM126_SPEC},
        ],
    },
    # H13.4 — IEF NEW — rates intermediate UST 7-10y signal. Tests duration
    # axis within rates orthogonality. KILL #142 fires if |TLT - IEF| ≥ 2pt.
    "h13_meta_4way_25a2_25g2_25f1_25e1ief_mom126": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_IEF_MOM126_SPEC},
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
