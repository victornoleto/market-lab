"""Iter 007 driver: A2 TQQQ-track + 200d SMA gate, KMLM/TLT dose extension.

Continues iter 006 — extends KMLM dose 30%→35%→40% on TQQQ-track + an
alternative TLT 15% lever (mirrors iter 005 SPY-track sweep). Tests
H₁ (KMLM monotonic on TQQQ-track), H₂ (TLT-on-top steepness vs KMLM
extension), H₃ (architecture preserves 3 strict bars).

See hypothesis.md for rationale per config and pre-committed KILL #22/#23.

Run from repo root with .venv active:
    PYTHONPATH=. python studies/spy_beater_hunt/iterations/007-2026-04-30-A2-tqqq-track-extreme/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 7
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "A2-tqqq-track-extreme"
PRIMARY_CITATION = (
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed gate (asset-agnostic) + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking (KMLM/TLT extension) + "
    "[advances_fin_ml, p.31-34] factor framework (NDX as US-Large-growth tilt)"
)

# Cumulative: prior iters 001 (4) + 002 (6) + 003 (4) + 004 (3) + 005 (3) + 006 (3) = 23.
PRIOR_CUMULATIVE_N_TRIALS = 23
N_CONFIGS = 3
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 26

CONFIGS = {
    # Push KMLM 30% → 35% on TQQQ-track (analog of iter 005 a5_kmlm35 on SPY-track).
    "a7_tqqq_split_kmlm35_tlt10": {
        "type": "lrs",
        "filter": "sma",
        "sma_window": 200,
        "buffer_pct": 0.0,
        "on_weights": {
            "TQQQSIM": 0.275,
            "QLDSIM": 0.275,
            "KMLMSIM": 0.35,
            "TLTSIM": 0.10,
        },
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "QQQSIM",
        "lag_days": 1,
    },
    # Push KMLM 35% → 40% on TQQQ-track (analog of iter 005 a5_kmlm40 on SPY-track).
    "a7_tqqq_split_kmlm40_tlt10": {
        "type": "lrs",
        "filter": "sma",
        "sma_window": 200,
        "buffer_pct": 0.0,
        "on_weights": {
            "TQQQSIM": 0.25,
            "QLDSIM": 0.25,
            "KMLMSIM": 0.40,
            "TLTSIM": 0.10,
        },
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "QQQSIM",
        "lag_days": 1,
    },
    # Alternative lever: hold KMLM 30%, push TLT 10% → 15% (orthogonal to KMLM dose).
    "a7_tqqq_split_kmlm30_tlt15": {
        "type": "lrs",
        "filter": "sma",
        "sma_window": 200,
        "buffer_pct": 0.0,
        "on_weights": {
            "TQQQSIM": 0.275,
            "QLDSIM": 0.275,
            "KMLMSIM": 0.30,
            "TLTSIM": 0.15,
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
