"""Iter 032 driver: H12 META-ENSEMBLE 4-WAY GLD-FILTER-TYPE AXIS — signal-
asset fixed at GLDSIM (per iter 030 KILL #125 ceiling-breach), lookback
held at ~6m peak (per iter 031 KILL #130 asset-invariant inverted-U), varying
filter-type {momentum, sma, ema} at 4th constituent slot.

Iter 030 KILL #125 FIRED — ORTHOGONAL-ASSET-CLASS-TSMOM-SOURCE BONUS at
4-way meta-ensemble: GLD-momentum-126d signal on TQQQ-stack sleeve outperforms
QQQ-momentum-126d baseline by +1pt at score axis. First ceiling-breach in 9
sequential meta-axis iters.

Iter 031 KILL #130 FIRED — TSMOM-LOOKBACK INVERTED-U IS ASSET-INVARIANT
(Principle D): 6m is the local maximum on lookback dimension regardless of
signal-asset choice (QQQ + GLD pair tested).

Iter 030 KILL #124 NOT FIRED ESTABLISHED — TRIPLE-GRANULARITY DISTINCTNESS
(Principle B): signal-source-distinctness operates at 3 axes (asset × filter
× lookback). SPY-momentum-126d preserved bonus DESPITE asset-axis match
because filter-type AND lookback distinct from G2 (2/3 axes distinct).

Iter 032 directly tests Principle B at GLD-source by varying filter-type at
the 4th constituent slot — testing whether asset-class-orthogonality bonus
is FILTER-TYPE-INVARIANT (1/3 axis sufficient) or FILTER-TYPE-COUPLED
(≥ 2/3 axes required).

Four filter-type variants tested at the 4th constituent slot (signal_ticker
= GLDSIM fixed, sleeve TQQQSIM 30 + QLDSIM 30 + KMLMSIM 30 + TLTSIM 10
fixed, weight 25% fixed = iter 030 H10.4 baseline):

  - GLD-momentum-126d: BASELINE replicates iter 030 H10.4 / iter 031 H11.2
    (3/3 axes distinct: asset GLD vs equity, filter momentum vs SMA, lookback
    126d vs 200d)
  - GLD-SMA-126d: 2/3 axes distinct (asset+lookback distinct, filter MATCHES
    A2/G2 SMA)
  - GLD-EMA-126d: 3/3 axes distinct (asset+filter EMA-not-SMA+lookback distinct)
  - GLD-SMA-200d: 1/3 axes distinct (asset only — Faber GTAA commodity gate)

Constituents A2, G2, F1 reused verbatim from iter 026/029/030/031. Only 4th
constituent's `filter` and `sma_window`/`lookback_days` parameters change —
isolating filter-type effect within fixed sleeve composition AND fixed
signal_ticker (GLDSIM).

Per iter 030 KILL #124 NOT FIRED: filter-type AND lookback together preserve
distinctness even when signal-asset matches. Per iter 031 KILL #130: lookback
peak is asset-invariant at 6m. Iter 032 tests if filter-type axis ALONE is
sufficient distinctness when asset matches OR if asset+filter+lookback joint
distinctness is required.

See hypothesis.md for H12.1-H12.4 + pre-committed KILL #133-#138.

NO new infra: reuses 'blend' spec type from iter 018-031 + 'lrs' spec type
with {sma, ema, momentum} filter from iter 014/024/026/028/029/030/031 +
'static' spec type from iter 015. 771 tests baseline preserved.

Run from repo root with .venv active::

    PYTHONPATH=. python studies/spy_beater_hunt/iterations/032-2026-04-30-H12-meta-ensemble-4way-gld-filter-type-axis/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 32
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "H12-meta-ensemble-4way-gld-filter-type-axis"
PRIMARY_CITATION = (
    "[advances_fin_ml, ch.16, p.241-256] portfolio construction over "
    "multiple alpha streams (4-way meta-ensemble at strategy-level with "
    "GLD-source filter-type sub-axis exploration — 16th iter at meta-axis) + "
    "[ivy_portfolio] Faber GTAA single-asset 6-10m moving average "
    "(commodity proxy DBC-10m; iter 032 tests GLD-SMA-200d as Faber commodity "
    "gate equivalent) + "
    "Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 "
    "(GLD-momentum-126d retained as baseline; filter-type axis substitutes "
    "with sma/ema canonical alternatives) + "
    "[asness_value_momentum] momentum-everywhere across asset classes "
    "(commodity TSMOM premium structure preserved across filter-types) + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate "
    "(A2 + G2 baseline retained — both equity-track 200d-SMA) + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking "
    "(F1 stack always-on retained at 3rd constituent — septuple-confirmed "
    "uniquely-Pareto-optimal per iter 027 KILL #110 + iter 028/029/030/031 "
    "implicit) + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM in A2/G2/E1 "
    "ON-state) + "
    "Bridgewater All-Weather (Dalio 1996) F1 stack ON-state + "
    "iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way) + "
    "iter 030 KILL #124 NOT FIRED — Principle B (triple-granularity "
    "distinctness asset × filter × lookback) + "
    "iter 030 KILL #125 (orthogonal-asset-class-TSMOM-source bonus +1pt) + "
    "iter 031 KILL #130 (TSMOM-lookback inverted-U asset-invariant peak at 6m) + "
    "[advances_fin_ml, p.31-34] factor framework — meta-ensemble axis "
    "16th iter (GLD-source filter-type sub-axis exploration) + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials = 124 (Bonferroni "
    "4.03e-04) + "
    "[advances_fin_ml, p.208-211] PBO grid-level N=4 stability"
)

# Cumulative: prior iters 001-031 = 120. This iter adds 4 -> 124.
PRIOR_CUMULATIVE_N_TRIALS = 120
N_CONFIGS = 4
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 124


# Constituent A (iter 006 a6_tqqq_split_kmlm30_tlt10) — reused verbatim from
# iter 026/029/030/031. Highest-CAGR constituent (~17.33%); CAGR-floor anchor.
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
# iter 026/029/030/031. Gate-source: SPY-200d-SMA.
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
# Gate-source: always-on (no gate). Reused verbatim from iter 026/029/030/031.
F1_STACK_SPEC = {
    "type": "static",
    "weights": {
        "NTSXSIM": 0.35,
        "GDESIM": 0.30,
        "TLTSIM": 0.20,
        "KMLMSIM": 0.15,
    },
}

# Constituent D — iter 032 NEW GLD-FILTER-TYPE variants. Signal-asset FIXED
# at GLDSIM (per iter 030 KILL #125 ceiling-breach). ON-sleeve identical to
# iter 030 H10.4 / iter 031 H11.2 to isolate filter-type effect.
#
# E1_GLD_MOM126 — BASELINE — replicates iter 030 H10.4 / iter 031 H11.2 selected
# config (score 72). Provides anchor for KILL #133/#134 and filter-type-axis
# variations.
E1_GLD_MOM126_SPEC = {
    "type": "lrs",
    "filter": "momentum",
    "lookback_days": 126,  # ~6 calendar months — iter 031 KILL #130 peak
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

# E1_GLD_SMA126 — SMA filter at 126d on GLDSIM signal. Tests 2/3-axis
# distinctness: asset (GLD) + lookback (126d distinct from 200d) but filter
# MATCHES A2/G2's SMA. Per Principle B (iter 030 KILL #124), 2/3 axes
# distinct should preserve the orthogonality bonus.
E1_GLD_SMA126_SPEC = {
    "type": "lrs",
    "filter": "sma",
    "sma_window": 126,  # ~6 calendar months SMA
    "buffer_pct": 0.0,
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

# E1_GLD_EMA126 — EMA filter at 126d on GLDSIM signal. Tests 3/3-axis
# distinctness via EMA-not-SMA filter type. Should preserve bonus per
# Principle B.
E1_GLD_EMA126_SPEC = {
    "type": "lrs",
    "filter": "ema",
    "sma_window": 126,  # ~6 calendar months EMA span
    "buffer_pct": 0.0,
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

# E1_GLD_SMA200 — Faber GTAA canonical commodity 10m moving average. Tests
# 1/3-axis distinctness — only asset (GLD) is distinct from A2/G2 (filter
# SMA matches; lookback 200d matches). Per Principle B's strict
# interpretation, bonus should be LOST (≤ 71). Per Principle B's relaxed
# interpretation (asset-class alone sufficient), bonus retained (= 72).
E1_GLD_SMA200_SPEC = {
    "type": "lrs",
    "filter": "sma",
    "sma_window": 200,  # ~10 calendar months — Faber GTAA canonical
    "buffer_pct": 0.0,
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
    # H12.1 — BASELINE — replicates iter 030 H10.4 / iter 031 H11.2 selected
    # config (score 72). Tests KILL #133/#134 (ceiling) and provides anchor
    # for KILL #135/#136/#137/#138.
    "h12_meta_4way_25a2_25g2_25f1_25e1gld_mom126": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_GLD_MOM126_SPEC},
        ],
    },
    # H12.2 — GLD-SMA-126d at 4th constituent. Tests 2/3-axis distinctness
    # (asset + lookback distinct, filter matches A2/G2 SMA). Per Principle B,
    # bonus should be preserved.
    "h12_meta_4way_25a2_25g2_25f1_25e1gld_sma126": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_GLD_SMA126_SPEC},
        ],
    },
    # H12.3 — GLD-EMA-126d at 4th constituent. Tests 3/3-axis distinctness
    # via EMA-not-SMA filter. Should preserve bonus.
    "h12_meta_4way_25a2_25g2_25f1_25e1gld_ema126": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_GLD_EMA126_SPEC},
        ],
    },
    # H12.4 — GLD-SMA-200d at 4th constituent. Faber GTAA canonical commodity
    # 10m gate. Tests 1/3-axis distinctness — only asset distinct from A2/G2.
    # If KILL #138 fires (score < 72) → Principle B requires ≥ 2/3 axes. If
    # H12.4 = 72 → Principle B relaxes to 1/3 axis sufficient (asset alone).
    "h12_meta_4way_25a2_25g2_25f1_25e1gld_sma200": {
        "type": "blend",
        "constituents": [
            {"weight": 0.25, "spec": A2_CLOSEST_SPEC},
            {"weight": 0.25, "spec": G2_IEF_SPEC},
            {"weight": 0.25, "spec": F1_STACK_SPEC},
            {"weight": 0.25, "spec": E1_GLD_SMA200_SPEC},
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
