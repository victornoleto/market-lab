"""Iter 010 driver: C1 vol-targeted SPY (Carver canonical, dynamic leverage).

Pivot rationale: leveraged-barbell architectures (B1 HFEA classical iter
008, B2 HFEA + KMLM iter 009) CLOSED via KILL #24 + KILL #27 — both
fail spy_beater MDD bar. A2 TQQQ-track saturated at score 67 (iter 006/
007). C1 vol-targeted is the only Tier 1-2 architecture not yet tested
(per iter 009 final_report.md "Where the score-90 path goes from here").

The lever is **state-dependent leverage scaling** (Carver canonical:
``weight_t = target_vol_annual / (factor × realised_vol_signal_t)``)
applied to a leveraged underlying (SSO 2× or UPRO 3×) versus IEF cash.
Vol-targeting is structurally conservative in stress regimes (vol
spikes 2008/2020/2022) → automatic de-risking that static barbells
lack and trend gates only achieve via lagged signal.

3 configs, mirroring iter 009's count to slow cumulative n_trials
growth (32 → 35):
  - c1_vt20_sso : target 20%, SSO factor 2 — most conservative ~1.25× SPY
  - c1_vt22_upro: target 22%, UPRO factor 3 — mid ~1.375× SPY
  - c1_vt25_upro: target 25%, UPRO factor 3 — most aggressive ~1.56× SPY

See hypothesis.md for H₁/H₂/H₃ + pre-committed KILL #30/#31/#32.

Run from repo root with .venv active::

    PYTHONPATH=. python studies/spy_beater_hunt/iterations/\\
        010-2026-04-30-C1-vol-targeted/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 10
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "C1-vol-targeted"
PRIMARY_CITATION = (
    "[systematic_trading, ch.10] Carver vol-targeting canonical + "
    "[advances_fin_ml, p.31-34] factor framework (vol as state variable) + "
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking via dynamic weight + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed LETF decay rationale"
)

# Cumulative: prior iters 001-009 = 32. This iter adds 3 → 35.
PRIOR_CUMULATIVE_N_TRIALS = 32
N_CONFIGS = 3
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 35

# Shared params for all 3 vol-target configs.
_SHARED = {
    "type": "vol_target",
    "cash_weights": {"IEFSIM": 1.0},
    "signal_ticker": "SPYSIM",
    "vol_window": 60,
    "vol_lag_days": 1,
    "weight_min": 0.0,
    "weight_max": 1.0,
}

CONFIGS = {
    # Most conservative: 20% target on SSO 2× → mean weight ~0.625 →
    # ~1.25× SPY effective exposure. Tests KILL #31 (defensive variant
    # MDD bar). Lowest CAGR, cleanest MDD.
    "c1_vt20_sso": {
        **_SHARED,
        "underlying_weights": {"SSOSIM": 1.0},
        "underlying_leverage_factor": 2.0,
        "target_vol_annual": 0.20,
    },
    # Mid: 22% target on UPRO 3× → mean weight ~0.458 →
    # ~1.375× SPY effective. Closest to a1_lrs_split's 1.5× notional but
    # via dynamic vol-target instead of trend gate.
    "c1_vt22_upro": {
        **_SHARED,
        "underlying_weights": {"UPROSIM": 1.0},
        "underlying_leverage_factor": 3.0,
        "target_vol_annual": 0.22,
    },
    # Most aggressive: 25% target on UPRO 3× → mean weight ~0.521 →
    # ~1.56× SPY effective. Tests KILL #32 (Sharpe regression at high
    # target_vol dose).
    "c1_vt25_upro": {
        **_SHARED,
        "underlying_weights": {"UPROSIM": 1.0},
        "underlying_leverage_factor": 3.0,
        "target_vol_annual": 0.25,
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
