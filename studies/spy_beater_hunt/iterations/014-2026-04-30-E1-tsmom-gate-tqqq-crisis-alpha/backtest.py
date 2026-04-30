"""Iter 014 driver: E1 Hybrid — TSMOM Gate × TQQQ-track Sleeve + KMLM Crisis-Alpha.

Cross-product sanity check on KILL #33 (architectural ceiling). Combines
the best-MDD gate (D1 TSMOM 6m, iter 013 d1_qqq_6m_tsmom mean MDD 35.27%)
with the best-CAGR sleeve (A2 TQQQ-track + KMLM30 + TLT10, iter 006
a6_tqqq_split_kmlm30_tlt10 mean CAGR 17.33%, score 67 closest-to-winner).

Tests whether the implicit orthogonality assumption underlying KILL #33
holds: if gate and sleeve axes are truly independent, the cross-product
hybrid should yield the union of single-axis gains (predicted score
69-73, possibly ≥70 → KILL #43 path). If decay-dominated, MDD gain
from TSMOM does NOT transfer to 3× LETF and score caps at ≤67 → KILL
#42 path.

See hypothesis.md for H1/H2/H3 + pre-committed KILL #42/#43/#44/#45.

Configs reuse the existing ``filter="momentum"`` LRS variant (added in
iter 013); no new modules. All synths (TQQQSIM, QLDSIM, KMLMSIM, TLTSIM,
IEFSIM, QQQSIM signal) are in the testfolio cache.

Run from repo root with .venv active:
    PYTHONPATH=. python studies/spy_beater_hunt/iterations/014-2026-04-30-E1-tsmom-gate-tqqq-crisis-alpha/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 14
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "E1-tsmom-gate-tqqq-crisis-alpha"
PRIMARY_CITATION = (
    "Moskowitz, Ooi, Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed gate-family rationale + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking (KMLM transfer) + "
    "[advances_fin_ml, p.31-34] factor framework — gate axis × sleeve axis "
    "orthogonality assumption explicitly tested + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials"
)

# Cumulative: prior iters 001-013 = 41 (iter 013 added 3 to 38).
# This iter adds 3 → 44.
PRIOR_CUMULATIVE_N_TRIALS = 41
N_CONFIGS = 3
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 44

CONFIGS = {
    # Cross-product 1: iter 006 best sleeve (TQQQ split + KMLM30 + TLT10)
    # × iter 013 best gate (TSMOM 6m on QQQSIM signal). Tests whether
    # gate axis (D1) × sleeve axis (A2) orthogonality holds. Predicted
    # score 65-72: TSMOM gives ~+5 MDD pts, costs ~−1 CAGR pt over iter
    # 006 67-baseline.
    "e1_tqqq_split_kmlm30_tlt10_tsmom6m": {
        "type": "lrs",
        "on_weights": {
            "TQQQSIM": 0.30,
            "QLDSIM": 0.30,
            "KMLMSIM": 0.30,
            "TLTSIM": 0.10,
        },
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "QQQSIM",
        "filter": "momentum",
        "lookback_days": 126,  # ~6 calendar months (Faber GTAA equivalent)
        "lag_days": 1,
    },
    # Cross-product 2: same sleeve, longer TSMOM lookback (12m
    # Moskowitz canonical). Tests dose-response on TSMOM lookback at 3×
    # leverage; iter 013 found dose-response was dataset-regime-dependent
    # at 1× — does that finding persist or flip at 3× LETF?
    "e1_tqqq_split_kmlm30_tlt10_tsmom12m": {
        "type": "lrs",
        "on_weights": {
            "TQQQSIM": 0.30,
            "QLDSIM": 0.30,
            "KMLMSIM": 0.30,
            "TLTSIM": 0.10,
        },
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "QQQSIM",
        "filter": "momentum",
        "lookback_days": 252,  # ~12 calendar months (Moskowitz canonical)
        "lag_days": 1,
    },
    # Pure variant: 100% TQQQ ON, IEF OFF, TSMOM 6m. Tests H₃: does 3×
    # LETF decay during 2000-02 dot-com overwhelm even slower TSMOM gate?
    # Mirror of d1_qld_6m_tsmom (iter 013) which failed MDD at 62.28%
    # on 2× QLD; if 3× TQQQ also fails, KILL #45 fires. If passes, decay
    # narrative for spy_beater rubric is more nuanced than current model.
    "e1_tqqq_pure_tsmom6m": {
        "type": "lrs",
        "on_weights": {"TQQQSIM": 1.0},
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "QQQSIM",
        "filter": "momentum",
        "lookback_days": 126,
        "lag_days": 1,
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
    print(f"Iter {ITER_N:03d} — {HYPOTHESIS_SLUG}")
    print(f"{'=' * 72}")
    print(f"Tier:     {verdict['tier']}")
    print(f"Score:    {verdict['total_score']}/100")
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
    print("All configs (mean CAGR / mean MDD across datasets):")
    for cfg, ds_metrics in verdict["all_configs_metrics"].items():
        cagrs = [ds_metrics[ds]["cagr"] for ds in ds_metrics]
        mean_cagr = sum(cagrs) / len(cagrs)
        mdds = [ds_metrics[ds]["mdd"] for ds in ds_metrics]
        mean_mdd = sum(mdds) / len(mdds)
        bar_pass = "PASS" if mean_cagr >= 0.1121 and mean_mdd <= 0.5517 else "FAIL"
        print(
            f"  [{bar_pass}] {cfg:>40s}: CAGR mean {mean_cagr*100:+.2f}%  "
            f"MDD mean {mean_mdd*100:.2f}%"
        )
