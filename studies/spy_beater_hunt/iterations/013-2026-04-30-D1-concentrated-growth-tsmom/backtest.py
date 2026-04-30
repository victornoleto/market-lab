"""Iter 013 driver: D1 Concentrated Growth + TSMOM Gate (QQQ + 6/12m TSMOM).

Post-impossibility Tier 3 sanity check on KILL #33 (architectural ceiling).
Tests whether a 6th distinct architectural family (concentrated growth on
NDX with time-series momentum gate, single-anchor `price[t] >
price[t-lookback]`) can break the score-67 ceiling found across 5 control
families in iters 001-012.

See hypothesis.md for H1/H2/H3 + pre-committed KILL #39/#40/#41.

Configs use the new ``filter="momentum"`` LRS variant (added to
``lrs_engine.py`` via TDD this iter); ``QQQSIM``, ``QLDSIM``, ``IEFSIM``
all in testfolio cache.

Run from repo root with .venv active:
    PYTHONPATH=. python studies/spy_beater_hunt/iterations/013-2026-04-30-D1-concentrated-growth-tsmom/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 13
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "D1-concentrated-growth-tsmom"
PRIMARY_CITATION = (
    "Moskowitz, Ooi, Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 + "
    "Faber 2007 GTAA (10m TSMOM equivalent at monthly frequency) + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed gate-family rationale + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials"
)

# Cumulative: prior iters 001-012 = 38 (iter 012 added 3 to 35).
# This iter adds 3 → 41.
PRIOR_CUMULATIVE_N_TRIALS = 38
N_CONFIGS = 3
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 41

CONFIGS = {
    # 1× QQQ + 6m TSMOM gate. Faber GTAA equivalent. Canonical TSMOM
    # lookback per practitioner literature. Tests whether unleveraged NDX
    # with TSMOM gate clears spy_beater bars (likely passes 3/3 but
    # CAGR-caps below 14%, scoring ~55-62).
    "d1_qqq_6m_tsmom": {
        "type": "lrs",
        "on_weights": {"QQQSIM": 1.0},
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "QQQSIM",
        "filter": "momentum",
        "lookback_days": 126,  # ~6 calendar months (21 trading days × 6)
        "lag_days": 1,
    },
    # 1× QQQ + 12m TSMOM gate. Moskowitz et al. canonical academic
    # TSMOM lookback. Tests lookback dose-response and lag risk
    # (longer lookback = slower reaction to crashes).
    "d1_qqq_12m_tsmom": {
        "type": "lrs",
        "on_weights": {"QQQSIM": 1.0},
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "QQQSIM",
        "filter": "momentum",
        "lookback_days": 252,  # ~12 calendar months
        "lag_days": 1,
    },
    # 2× QQQ via QLD + 6m TSMOM gate. Moderate leverage variant. Tests
    # whether LETF daily-reset decay (~1-2%/y for 2× LETF) erodes the
    # advantage over plain 1× QQQ. If Sharpe(QLD 6m) > Sharpe(QQQ 6m),
    # leverage adds value here; if worse, decay dominates.
    "d1_qld_6m_tsmom": {
        "type": "lrs",
        "on_weights": {"QLDSIM": 1.0},
        "off_weights": {"IEFSIM": 1.0},
        "signal_ticker": "QQQSIM",  # underlying signal, not LETF price
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
            f"  [{bar_pass}] {cfg:>30s}: CAGR mean {mean_cagr*100:+.2f}%  "
            f"MDD mean {mean_mdd*100:.2f}%"
        )
