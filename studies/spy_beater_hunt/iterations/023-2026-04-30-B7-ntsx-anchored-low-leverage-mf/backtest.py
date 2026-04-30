"""Iter 023 driver: B7 NTSX-anchored low-leverage static + MF dose-response.

Tests whether the iter 022 KILL #79 finding ("MF crisis-alpha effectiveness
INVERSELY proportional to backbone notional leverage") generalizes to one
step LOWER on the leverage axis: 1.5x notional via NTSX 100% (90/60 internal
SPY/UST stack) vs B5's 2.0x notional (150% UPRO + 50% TLT).

Per [risk_parity, ch.5, p.10] Carlson canonical NTSX formulation. NTSX is
the most capital-efficient SPY-anchored stacking vehicle below the
static-barbell axis; the iter 022 generalization predicts MF lift should be
even more pronounced at 150% notional than at 200% notional.

NO new infra: reuses 'static' spec type from iter 008/022. All 4 assets
(NTSX, KMLM, DBMF, TLT) direct in testfolio cache.

Pre-commit KILL #83 (B7 max <= 65 -> axis CLOSED), KILL #84 (>= 70 ->
hunt reopens at low-leverage axis), KILL #85 (KMLM 20% Sharpe lift >=
0.05 over NTSX 100% baseline -> KILL #79 generalization confirmed at
1.5x notional regime), KILL #86 (NTSX 100% pure passes CAGR bar at
11.21% standalone -> minimum viable static threshold), KILL #87
(multi-source MF KMLM+DBMF Sharpe >= single-source +0.03 -> MF
decorrelation at 1.5x confirmed), KILL #88 (>= 75 -> STRONG tier ->
mandate paragraph 7 override request).

See hypothesis.md for full pre-commitment.

Run from repo root with .venv active:
    PYTHONPATH=. python studies/spy_beater_hunt/iterations/023-2026-04-30-B7-ntsx-anchored-low-leverage-mf/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 23
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "B7-ntsx-anchored-low-leverage-mf"
PRIMARY_CITATION = (
    "[risk_parity, ch.5, p.10] Carlson NTSX 90/60 internal SPY/UST stack "
    "as canonical capital-efficient 1.5x notional vehicle; B7 axis tests "
    "iter 022 KILL #79 generalization (MF effectiveness ~ 1/leverage) at "
    "150% notional regime, one step LOWER than B5 modest-HFEA 200% + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha role + "
    "[advances_fin_ml, p.31-34] factor framework for combining KMLM "
    "(Mount Lucas TF index) + DBMF (broader CTA basket) decorrelated "
    "alpha sources + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials = 86 + "
    "[advances_fin_ml, p.208-211] PBO via CSCV N=6 + "
    "WINNER_AND_RANKING.md structural net-rubric advantage 1.5pp for "
    "buy-hold static (iter 022 B5 confirmed 0.63pp drag for static spec)"
)

# Cumulative: prior iters 001-022 = 80. This iter adds 6 -> 86.
PRIOR_CUMULATIVE_N_TRIALS = 80
N_CONFIGS = 6
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 86

CONFIGS = {
    # H1 anchor: NTSX 100% pure baseline (lowest leverage 150% notional)
    # 90% SPY + 60% UST internal = 150% notional via single ER charge
    # KILL #86 trigger: passes CAGR bar 11.21% standalone?
    "b7_ntsx100": {
        "type": "static",
        "weights": {
            "NTSXSIM": 1.0,
        },
    },
    # H2 KMLM dose: 80/20 (modest MF substitution)
    # Predicted KILL #85 trigger if Sharpe lift >= 0.05 vs ntsx100 baseline
    # Notional drops to 120% via 20pp reduction in NTSX
    "b7_ntsx80_kmlm20": {
        "type": "static",
        "weights": {
            "NTSXSIM": 0.80,
            "KMLMSIM": 0.20,
        },
    },
    # H2 DBMF substitute: 80/20 (DBMF instead of KMLM)
    # Comparable to b5_4040_dbmf20 from iter 022 but at lower leverage
    # iter 022 found KMLM > DBMF at modest-HFEA; tests if hierarchy holds
    "b7_ntsx80_dbmf20": {
        "type": "static",
        "weights": {
            "NTSXSIM": 0.80,
            "DBMFSIM": 0.20,
        },
    },
    # H3 TLT extension: 70% NTSX + 20% KMLM + 10% TLT
    # Adds 1x duration leg on top of NTSX's internal duration
    # Tests if extra duration buffer reduces 2008-style MDD further
    "b7_ntsx70_kmlm20_tlt10": {
        "type": "static",
        "weights": {
            "NTSXSIM": 0.70,
            "KMLMSIM": 0.20,
            "TLTSIM": 0.10,
        },
    },
    # H4 multi-source MF: 70% NTSX + 15% KMLM + 15% DBMF (split 30% MF dose)
    # KILL #87 trigger: split MF >= single-source by Sharpe +0.03?
    # Tests decorrelation among MF families at 1.5x backbone
    "b7_ntsx70_kmlm15_dbmf15": {
        "type": "static",
        "weights": {
            "NTSXSIM": 0.70,
            "KMLMSIM": 0.15,
            "DBMFSIM": 0.15,
        },
    },
    # H5 quad-diversified: 70% NTSX + 10% KMLM + 10% DBMF + 10% TLT
    # Maximum diversification within static-axis constraint
    # Multi-source MF + duration buffer + NTSX backbone
    "b7_ntsx70_kmlm10_dbmf10_tlt10": {
        "type": "static",
        "weights": {
            "NTSXSIM": 0.70,
            "KMLMSIM": 0.10,
            "DBMFSIM": 0.10,
            "TLTSIM": 0.10,
        },
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
            f"  [{bar_pass}] {cfg:>34s}: CAGR {mean_cagr*100:+.2f}%  "
            f"MDD {mean_mdd*100:.2f}%  Sharpe {mean_sharpe:.3f}"
        )
