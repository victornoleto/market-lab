"""Iter 001 driver: A1 Gayed LRS UPRO + 200d SMA gate.

Run from repo root with .venv active:
    python studies/spy_beater_hunt/iterations/001-2026-04-29-A1-Gayed-LRS-UPRO/backtest.py

Produces verdict.json + results.json + final_report.md in the iter dir.
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 1
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "A1-Gayed-LRS-UPRO"
PRIMARY_CITATION = "[leverage_for_the_long_run, ch.3-4, p.40-60]"

# Cumulative n_trials BEFORE this iter (BASE_MEMORY.md frontmatter)
PRIOR_CUMULATIVE_N_TRIALS = 0
N_CONFIGS = 4
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS

# StrategySpec: each config rotates between on_weights and off_weights via
# Gayed 200d SMA gate on SPYSIM.
CONFIGS = {
    "a1_pure_lrs": {
        "type": "lrs",
        "on_weights": {"UPROSIM": 1.0},
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "SPYSIM",
        "sma_window": 200,
        "lag_days": 1,
    },
    "a1_lrs_cash": {
        "type": "lrs",
        "on_weights": {"UPROSIM": 1.0},
        "off_weights": {"CASHX": 1.0},
        "signal_ticker": "SPYSIM",
        "sma_window": 200,
        "lag_days": 1,
    },
    "a1_lrs_split": {
        "type": "lrs",
        "on_weights": {"UPROSIM": 0.5, "SSOSIM": 0.5},
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "SPYSIM",
        "sma_window": 200,
        "lag_days": 1,
    },
    "a1_lrs_kmlm_off": {
        "type": "lrs",
        "on_weights": {"UPROSIM": 1.0},
        "off_weights": {"IEFSIM": 0.5, "KMLMSIM": 0.5},
        "signal_ticker": "SPYSIM",
        "sma_window": 200,
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
    print("All configs CAGR (mean across 3 datasets):")
    for cfg, ds_metrics in verdict["all_configs_metrics"].items():
        cagrs = [ds_metrics[ds]["cagr"] for ds in ds_metrics]
        mean_cagr = sum(cagrs) / len(cagrs)
        mdds = [ds_metrics[ds]["mdd"] for ds in ds_metrics]
        mean_mdd = sum(mdds) / len(mdds)
        print(
            f"  {cfg:>20s}: CAGR mean {mean_cagr*100:+.2f}%  "
            f"MDD mean {mean_mdd*100:.2f}%"
        )
