"""Iter 006 driver: A2 TQQQ-track + 200d SMA gate on QQQ.

Pivots from SPY-track (UPRO+SSO) to NDX-track (TQQQ+QLD) per iter 005
final_report Option B. Ports the iter 004 closest-to-winner architecture
(split LRS + 30% KMLM) and the iter 005 best-Sharpe blend (KMLM30+TLT10)
to the NDX side, plus a pure A2 baseline for direct comparison with
iter 001 ``a1_lrs_split``.

See hypothesis.md for rationale per config and pre-committed KILL #19/#20/#21.

Run from repo root with .venv active:
    PYTHONPATH=. python studies/spy_beater_hunt/iterations/006-2026-04-30-A2-tqqq-track-split/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 6
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "A2-tqqq-track-split"
PRIMARY_CITATION = (
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed gate (asset-agnostic) + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking (KMLM transfer) + "
    "[advances_fin_ml, p.31-34] factor framework (NDX as US-Large-growth tilt)"
)

# Cumulative: prior iters 001 (4) + 002 (6) + 003 (4) + 004 (3) + 005 (3) = 20.
PRIOR_CUMULATIVE_N_TRIALS = 20
N_CONFIGS = 3
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 23

CONFIGS = {
    # Pure A2 baseline — analog of iter 001 a1_lrs_split on the NDX side.
    "a6_tqqq_split_lrs": {
        "type": "lrs",
        "filter": "sma",
        "sma_window": 200,
        "buffer_pct": 0.0,
        "on_weights": {"TQQQSIM": 0.5, "QLDSIM": 0.5},
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "QQQSIM",
        "lag_days": 1,
    },
    # Port iter 004 closest-to-winner (a4_lrs_split_kmlm30) to NDX side.
    "a6_tqqq_split_kmlm30": {
        "type": "lrs",
        "filter": "sma",
        "sma_window": 200,
        "buffer_pct": 0.0,
        "on_weights": {"TQQQSIM": 0.35, "QLDSIM": 0.35, "KMLMSIM": 0.30},
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "QQQSIM",
        "lag_days": 1,
    },
    # Port iter 005 best-Sharpe blend (a5_lrs_split_kmlm30_tlt10) to NDX side.
    "a6_tqqq_split_kmlm30_tlt10": {
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
            f"  [{bar_pass}] {cfg:>30s}: CAGR mean {mean_cagr*100:+.2f}%  "
            f"MDD mean {mean_mdd*100:.2f}%"
        )
