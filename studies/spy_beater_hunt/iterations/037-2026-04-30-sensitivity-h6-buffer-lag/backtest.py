"""Iter 037: SENSITIVITY TEST on iter 026 H6 (top deploy pick).

NOT a hunt search iter — this is a deploy-readiness sensitivity test
requested by user 2026-04-30 to validate two operational parameters
before any live deploy commitment:

  1. **Buffer 2% on SMA constituents** — iter 002 demonstrated buffer
     2% improves single-asset UPRO 3× MDD by ~12pp. iters 003+ silently
     reverted to canonical Gayed buffer 0% without empirical validation
     in the meta-ensemble context. Test: does buffer 2% transfer to
     4-way meta-ensemble?

  2. **Lag days = 2** — backtest uses `lag_days=1` (T+1 good-faith
     trading at Apex Clearing / Inter Internacional). Real-world Inter
     ops may have occasional T+2 effective settlement (dividend
     crediting delays, support response time ~8d). Test: does pushing
     lag to 2 materially degrade the strategy?

Configs:
  - h6_baseline      : iter 026 H6 EXACT (buffer 0%, lag 1) — anchor
  - h6_buffer2       : H6 with buffer_pct=0.02 on the 2 SMA constituents
  - h6_lag2          : H6 with lag_days=2 on all 3 LRS constituents
  - h6_buffer2_lag2  : both — worst-case operational + best whipsaw filter

The user explicitly noted the threshold is important to avoid
unnecessary entries/exits when SMA crosses are noisy (price dips
below SMA and recovers immediately, or vice-versa) — this directly
tests whether the operational concern translates to a measurable
backtest improvement.

Reuses 'blend' + 'lrs' (sma + momentum filters) + 'static' spec types.
NO new infra. 771 tests baseline preserved.

Run from repo root with .venv active::

    PYTHONPATH=. python studies/spy_beater_hunt/iterations/037-2026-04-30-sensitivity-h6-buffer-lag/backtest.py
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from studies.spy_beater_hunt.run_iter import run_iter_spy_beater


ITER_N = 37
ITER_DIR = Path(__file__).parent
HYPOTHESIS_SLUG = "sensitivity-h6-buffer-lag"
PRIMARY_CITATION = (
    "iter 026 H6 baseline (closest-to-winner Tier A, PBO 0.00) + "
    "iter 002 KILL #8 (buffer >=5% worsens MDD; 2% empirical sweet spot for UPRO 3x) + "
    "[leverage_for_the_long_run, ch.3-4, p.40-60] Gayed canonical 200d SMA + "
    "[advances_fin_ml, p.31-34] gate framework + "
    "Lei 14.754/2023 DARF anual"
)

PRIOR_CUMULATIVE_N_TRIALS = 140  # iter 036 ended at 140
N_CONFIGS = 4
CUMULATIVE_N_TRIALS = PRIOR_CUMULATIVE_N_TRIALS + N_CONFIGS  # = 144


# ---------------------------------------------------------------------------
# Iter 026 H6 components — verbatim from iter 026 verdict
# ---------------------------------------------------------------------------

A2_TQQQ_LRS = {
    "type": "lrs",
    "filter": "sma",
    "sma_window": 200,
    "buffer_pct": 0.0,
    "on_weights": {"TQQQSIM": 0.30, "QLDSIM": 0.30, "KMLMSIM": 0.30, "TLTSIM": 0.10},
    "off_weights": {"IEFSIM": 1.0},
    "signal_ticker": "QQQSIM",
    "lag_days": 1,
}

G2_IEF_LRS = {
    "type": "lrs",
    "filter": "sma",
    "sma_window": 200,
    "buffer_pct": 0.0,
    "on_weights": {"UPROSIM": 0.30, "TMFSIM": 0.25, "IEFSIM": 0.15, "UGLSIM": 0.15, "KMLMSIM": 0.15},
    "off_weights": {"IEFSIM": 1.0},
    "signal_ticker": "SPYSIM",
    "lag_days": 1,
}

F1_STACK_STATIC = {
    "type": "static",
    "weights": {"NTSXSIM": 0.35, "GDESIM": 0.30, "TLTSIM": 0.20, "KMLMSIM": 0.15},
}

E1_TSMOM = {
    "type": "lrs",
    "filter": "momentum",
    "lookback_days": 126,
    "on_weights": {"TQQQSIM": 0.30, "QLDSIM": 0.30, "KMLMSIM": 0.30, "TLTSIM": 0.10},
    "off_weights": {"IEFSIM": 1.0},
    "signal_ticker": "QQQSIM",
    "lag_days": 1,
}


def _h6_with_overrides(
    sma_buffer: float = 0.0,
    sma_lag: int = 1,
    momentum_lag: int = 1,
) -> dict:
    """Build an H6 4-way blend with SMA buffer / lag overrides."""
    a2 = deepcopy(A2_TQQQ_LRS)
    g2 = deepcopy(G2_IEF_LRS)
    e1 = deepcopy(E1_TSMOM)

    a2["buffer_pct"] = sma_buffer
    g2["buffer_pct"] = sma_buffer
    a2["lag_days"] = sma_lag
    g2["lag_days"] = sma_lag
    e1["lag_days"] = momentum_lag

    return {
        "type": "blend",
        "constituents": [
            {"weight": 0.30, "spec": a2},
            {"weight": 0.25, "spec": g2},
            {"weight": 0.25, "spec": deepcopy(F1_STACK_STATIC)},
            {"weight": 0.20, "spec": e1},
        ],
    }


CONFIGS = {
    # Anchor: iter 026 H6 verbatim — should reproduce score 71/net 66.
    "h6_baseline": _h6_with_overrides(sma_buffer=0.0, sma_lag=1, momentum_lag=1),
    # Buffer 2% applied to both SMA gate constituents (A2 + G2 IEF).
    # E1 momentum gate has no buffer (different filter type).
    "h6_buffer2": _h6_with_overrides(sma_buffer=0.02, sma_lag=1, momentum_lag=1),
    # Lag 2 applied to ALL 3 gate constituents (worst-case Inter ops).
    "h6_lag2": _h6_with_overrides(sma_buffer=0.0, sma_lag=2, momentum_lag=2),
    # Combined: best whipsaw filter + worst-case ops lag.
    "h6_buffer2_lag2": _h6_with_overrides(sma_buffer=0.02, sma_lag=2, momentum_lag=2),
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
    print(f"Iter {ITER_N:03d} — SENSITIVITY {HYPOTHESIS_SLUG}")
    print(f"{'=' * 72}")
    print(f"Selected (best Sharpe-edge): {verdict['selected_config']}")
    print(f"Gross score: {verdict['total_score']}/100  Net score: {verdict.get('net_total_score', 'n/a')}/100")
    print()
    print("Per-config metrics (gross):")
    print(f"  {'config':<20} {'Sh_lh':>7} {'CAGR_lh':>9} {'MDD_lh':>9} {'Sh_spy':>7} {'CAGR_spy':>9} {'MDD_spy':>9}")
    for cfg_name, ds_metrics in verdict["all_configs_metrics"].items():
        lh = ds_metrics["lh_56y"]
        sp = ds_metrics["spy_real"]
        print(
            f"  {cfg_name:<20} "
            f"{lh['sharpe']:>7.3f} {lh['cagr']*100:>8.2f}% {lh['mdd']*100:>8.2f}% "
            f"{sp['sharpe']:>7.3f} {sp['cagr']*100:>8.2f}% {sp['mdd']*100:>8.2f}%"
        )
    print()
    print("Per-dataset gates:")
    for ds, gd in verdict["gate_details"].items():
        print(f"  {ds}: PBO={gd['g1_pbo']:.3f} DSR_p={gd['g2_dsr_p']:.2e} WF_max_mdd={gd['g3_max_wf_mdd']*100:.2f}%")
