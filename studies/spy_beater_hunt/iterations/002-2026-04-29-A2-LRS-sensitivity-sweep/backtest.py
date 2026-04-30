"""Iter 002 driver: A2 LRS sensitivity sweep.

6 configs varying signal filter, window, threshold buffer, and leverage to
target the MDD bar. See hypothesis.md for the rationale per config.

Run from repo root with .venv active:
    PYTHONPATH=. python studies/spy_beater_hunt/iterations/002-2026-04-29-A2-LRS-sensitivity-sweep/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 2
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "A2-LRS-sensitivity-sweep"
PRIMARY_CITATION = (
    "[leverage_for_the_long_run, ch.3-4, p.40-60] + "
    "studies/_archive/ema_sma_threshold_nasdaq_real (prior project sweep)"
)

# Cumulative: prior iter 001 contributed 4 trials.
PRIOR_CUMULATIVE_N_TRIALS = 4
N_CONFIGS = 6
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 10

CONFIGS = {
    "a2_sma100_3xupro": {
        "type": "lrs",
        "filter": "sma",
        "sma_window": 100,
        "buffer_pct": 0.0,
        "on_weights": {"UPROSIM": 1.0},
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "SPYSIM",
        "lag_days": 1,
    },
    "a2_sma200_th2_3xupro": {
        "type": "lrs",
        "filter": "sma",
        "sma_window": 200,
        "buffer_pct": 0.02,
        "on_weights": {"UPROSIM": 1.0},
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "SPYSIM",
        "lag_days": 1,
    },
    "a2_sma200_th5_3xupro": {
        "type": "lrs",
        "filter": "sma",
        "sma_window": 200,
        "buffer_pct": 0.05,
        "on_weights": {"UPROSIM": 1.0},
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "SPYSIM",
        "lag_days": 1,
    },
    "a2_ema150_th2_3xupro": {
        "type": "lrs",
        "filter": "ema",
        "sma_window": 150,
        "buffer_pct": 0.02,
        "on_weights": {"UPROSIM": 1.0},
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "SPYSIM",
        "lag_days": 1,
    },
    "a2_sma150_2xsso": {
        "type": "lrs",
        "filter": "sma",
        "sma_window": 150,
        "buffer_pct": 0.0,
        "on_weights": {"SSOSIM": 1.0},
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "SPYSIM",
        "lag_days": 1,
    },
    "a2_ema100_th2_2xsso": {
        "type": "lrs",
        "filter": "ema",
        "sma_window": 100,
        "buffer_pct": 0.02,
        "on_weights": {"SSOSIM": 1.0},
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
        datasets_to_test=("lh_56y", "vt_real", "ndx_real"),
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
    print("All configs (mean CAGR / mean MDD across 3 datasets):")
    for cfg, ds_metrics in verdict["all_configs_metrics"].items():
        cagrs = [ds_metrics[ds]["cagr"] for ds in ds_metrics]
        mean_cagr = sum(cagrs) / len(cagrs)
        mdds = [ds_metrics[ds]["mdd"] for ds in ds_metrics]
        mean_mdd = sum(mdds) / len(mdds)
        bar_pass = "✓" if mean_cagr >= 0.1380 and mean_mdd <= 0.4085 else "✗"
        print(
            f"  {bar_pass} {cfg:>22s}: CAGR mean {mean_cagr*100:+.2f}%  "
            f"MDD mean {mean_mdd*100:.2f}%"
        )
