"""Iter 024 driver: G3 LRS-gated HFEA classical (8th cross-product hybrid).

Tests SMA-200d gate × HFEA-leverage-barbell sleeve (UPRO + TMF) — bridges
G1 (1.41× stack no-decay) and G2 (2.25× LETF moderate-decay) at the
300%-notional-leveraged-duration-decay regime. iter 008 B1 tested HFEA
STATIC (score 63, MDD ~67% catastrophic FAIL). G3 hypothesis: gate's
2008/2022 bear-avoidance rescues HFEA's MDD bar failure.

See hypothesis.md for KILLs #89-#94 (architectural-ceiling +
inverse-leverage-gate-composition tests).

Run from repo root with .venv active:
    PYTHONPATH=. python studies/spy_beater_hunt/iterations/024-2026-04-30-G3-lrs-gated-hfea/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 24
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "G3-lrs-gated-hfea"
PRIMARY_CITATION = (
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed LRS rationale + "
    "HFEA Bogleheads 2019 canonical 55/45 + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking + "
    "[ilmanen_expected_returns, ch.19] MF crisis-alpha for KMLM aug + "
    "[advances_fin_ml, p.31-34] factor framework"
)

# Cumulative: prior iters 001-023 = 86. This iter adds 5 → 91.
PRIOR_CUMULATIVE_N_TRIALS = 86
N_CONFIGS = 5
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 91

CONFIGS = {
    # G3.1 — Bogleheads canonical 55/45 with LRS gate
    "g3_gated_hfea_5545": {
        "type": "lrs",
        "on_weights": {"UPROSIM": 0.55, "TMFSIM": 0.45},
        "off_weights": {"IEFSIM": 1.00},
        "signal_ticker": "SPYSIM",
        "sma_window": 200,
        "lag_days": 1,
    },
    # G3.2 — Duration-tilted 50/50 with LRS gate (B1 5050 best static Sharpe 0.74)
    "g3_gated_hfea_5050": {
        "type": "lrs",
        "on_weights": {"UPROSIM": 0.50, "TMFSIM": 0.50},
        "off_weights": {"IEFSIM": 1.00},
        "signal_ticker": "SPYSIM",
        "sma_window": 200,
        "lag_days": 1,
    },
    # G3.3 — HFEA + 15% KMLM crisis-alpha with LRS gate
    "g3_gated_hfea_kmlm15": {
        "type": "lrs",
        "on_weights": {"UPROSIM": 0.50, "TMFSIM": 0.35, "KMLMSIM": 0.15},
        "off_weights": {"IEFSIM": 1.00},
        "signal_ticker": "SPYSIM",
        "sma_window": 200,
        "lag_days": 1,
    },
    # G3.4 — Modest HFEA 40/40/20 (B5-style sleeve) GATED
    "g3_gated_hfea_4040": {
        "type": "lrs",
        "on_weights": {"UPROSIM": 0.40, "TMFSIM": 0.40, "KMLMSIM": 0.20},
        "off_weights": {"IEFSIM": 1.00},
        "signal_ticker": "SPYSIM",
        "sma_window": 200,
        "lag_days": 1,
    },
    # G3.5 — Defensive off-state with KMLM (replicate iter 016 G1 BLEND off pattern at 300%)
    "g3_gated_hfea_5545_blend_off": {
        "type": "lrs",
        "on_weights": {"UPROSIM": 0.55, "TMFSIM": 0.45},
        "off_weights": {"IEFSIM": 0.50, "KMLMSIM": 0.50},
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
        cumulative_n_trials=CUMULATIVE_N_TRIALS,
    )

    print("\n" + "=" * 78)
    print(f"iter {ITER_N:03d} — {HYPOTHESIS_SLUG} — VERDICT")
    print("=" * 78)
    print(f"Tier:       {verdict['tier']}")
    print(f"Score:      {verdict['total_score']}/100  (net: {verdict.get('net_total_score', 'n/a')}/100)")
    print(f"Bars met:   {verdict['bars']}")
    print(f"Winner met: {verdict['winner_conditions_met']}")
    print(f"Selected:   {verdict['selected_config']}")
    print()
    print("Per-dataset metrics (selected config):")
    for ds, m in verdict["metrics_used"].items():
        print(
            f"  {ds:10s}  Sharpe={m['sharpe']:.3f}  "
            f"CAGR={m['cagr']*100:.2f}%  MDD={m['mdd']*100:.2f}%  "
            f"DSR_p={m['dsr_p_value']:.2e}"
        )
    print()
    print("All configs (Sharpe per dataset):")
    for cfg in CONFIGS:
        ds_metrics = verdict["all_configs_metrics"][cfg]
        per_ds = "  ".join(
            f"{ds}={ds_metrics[ds]['sharpe']:.3f}"
            for ds in ds_metrics
        )
        print(f"  {cfg:35s}  {per_ds}")
