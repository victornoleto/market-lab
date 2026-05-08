"""Iter 012 driver: D2 Stacked Equity Heavy (NTSX + UPRO + AVUV).

Post-impossibility Tier 3 sanity check on KILL #33 (architectural ceiling).
Tests whether a 5th distinct architectural family (pure stacking + factor
tilt + LETF, no regime gate) can break the score-67 ceiling found across
4 control families in iters 001-010.

See hypothesis.md for H1/H2/H3 + pre-committed KILL #36/#37/#38.

Configs use ``static`` strategy type (delegated to
``portfolio_returns_from_config``); no new modules needed. Tickers
NTSXSIM (proxies blueprint), UPROSIM (testfolio cache), AVUVSIM
(synth) all already wired in long_term_portfolio.run_iter.

Run from repo root with .venv active:
    PYTHONPATH=. python studies/spy_beater_hunt/iterations/012-2026-04-30-D2-stacked-equity-heavy/backtest.py
"""
from __future__ import annotations

from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 12
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "D2-stacked-equity-heavy"
PRIMARY_CITATION = (
    "[risk_parity, ch.5, p.10] Carlson capital-efficient stacking + "
    "[advances_fin_ml, p.31-34] factor framework (AVUV SCV factor) + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed LETF decay (UPRO leg) + "
    "[advances_fin_ml, p.222-223] DSR cumulative_n_trials"
)

# Cumulative: prior iters 001-011 = 35 (iter 011 meta-iter preserved 35).
# This iter adds 3 → 38.
PRIOR_CUMULATIVE_N_TRIALS = 35
N_CONFIGS = 3
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 38

CONFIGS = {
    # Stacking + factor, no extra LETF. NTSX = 90% S&P + 60% IEF effective
    # (1.5x notional via futures stacking, no daily-reset decay). AVUV = SCV
    # factor tilt (Avantis/FF SmB+HmL). Mean equity exposure ~0.95x SPY +
    # 0.30x IEF + 0.50x SCV. Conservative variant — likely passes 3/3 bars
    # but CAGR-caps below 14% (H3 prediction).
    "d2_ntsx_avuv": {
        "type": "static",
        "weights": {
            "NTSXSIM": 0.50,
            "AVUVSIM": 0.50,
        },
    },
    # Mixed stacking + LETF + factor. ~1.65x equity notional + factor tilt.
    # Most aggressive D2 variant. Tests whether *combining* stacking with
    # LETF concentration delivers regime-gate-equivalent CAGR uplift WITHOUT
    # the gate. Likely scores 60-68 — the candidate that could plausibly
    # break the 67-ceiling.
    "d2_ntsx_upro_avuv": {
        "type": "static",
        "weights": {
            "NTSXSIM": 0.35,
            "UPROSIM": 0.35,
            "AVUVSIM": 0.30,
        },
    },
    # Pure LETF + factor, no bonds. ~1.5x equity notional + SCV concentrate.
    # Tests H2: pure equity LETF + factor fails MDD bar in 2008/2022 stress.
    # Likely fires KILL #38 (mean MDD > 55%).
    "d2_upro_avuv": {
        "type": "static",
        "weights": {
            "UPROSIM": 0.50,
            "AVUVSIM": 0.50,
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
