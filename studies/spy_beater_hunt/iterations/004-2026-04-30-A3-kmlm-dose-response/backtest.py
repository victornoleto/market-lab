"""Iter 004 driver: A3 KMLM dose-response (extend monotonic positive trend).

Extends iter 003 closest-to-winner (a3_lrs_split_kmlm20: 40% UPRO +
40% SSO + 20% KMLM ON, IEF OFF, SMA 200) by probing KMLM dose-response
at 25% and 30%. Includes a head-to-head TLT 20% comparison vs the
KMLM 20% peak from iter 003.

See hypothesis.md for rationale per config.

Run from repo root with .venv active:
    PYTHONPATH=. python studies/spy_beater_hunt/iterations/004-2026-04-30-A3-kmlm-dose-response/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 4
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "A3-kmlm-dose-response"
PRIMARY_CITATION = (
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed gate + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking"
)

# Cumulative: prior iters 001 (4) + 002 (6) + 003 (4) = 14. This iter adds 3.
PRIOR_CUMULATIVE_N_TRIALS = 14
N_CONFIGS = 3
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 17

CONFIGS = {
    "a4_lrs_split_kmlm25": {
        "type": "lrs",
        "filter": "sma",
        "sma_window": 200,
        "buffer_pct": 0.0,
        "on_weights": {"UPROSIM": 0.375, "SSOSIM": 0.375, "KMLMSIM": 0.25},
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "SPYSIM",
        "lag_days": 1,
    },
    "a4_lrs_split_kmlm30": {
        "type": "lrs",
        "filter": "sma",
        "sma_window": 200,
        "buffer_pct": 0.0,
        "on_weights": {"UPROSIM": 0.35, "SSOSIM": 0.35, "KMLMSIM": 0.30},
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "SPYSIM",
        "lag_days": 1,
    },
    "a4_lrs_split_tlt20": {
        "type": "lrs",
        "filter": "sma",
        "sma_window": 200,
        "buffer_pct": 0.0,
        "on_weights": {"UPROSIM": 0.40, "SSOSIM": 0.40, "TLTSIM": 0.20},
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "SPYSIM",
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
            f"  [{bar_pass}] {cfg:>22s}: CAGR mean {mean_cagr*100:+.2f}%  "
            f"MDD mean {mean_mdd*100:.2f}%"
        )
