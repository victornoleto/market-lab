"""Iter 041 backtest: F7-US-Stacked-MF (Phase 2 finalist construction).

Tests stacked-MF philosophy via RSST (ReturnStacked US Equity & Managed
Futures, 100% SPY + 100% KMLM via 2× notional). 4 configs sweep RSST
15→50% combined with NTSX/GDE/KMLM/TLT. Independent axis from Phase 1
sleeve findings.

KILL #4 evaluated post-run vs iter 023 baseline (no constituent test).
KILL #5 (RSST standalone Sharpe < 1.5) already validated pre-iter 030.

Citations:
- [risk_parity, ch.5] Carlson cap-efficient stacking
- ReSolve/Newfound Return Stacked methodology (2023):
  RSST = 100% SPY + 100% KMLM via 2× gross notional.
"""
from pathlib import Path

from studies.long_term_portfolio.run_iter import run_iter_full


CONFIGS = {
    "f7_lite":       {"NTSXSIM": 0.25, "RSSTSIM": 0.15, "GDESIM": 0.25, "KMLMSIM": 0.20, "TLTSIM": 0.15},
    "f7_balanced":   {"NTSXSIM": 0.15, "RSSTSIM": 0.30, "GDESIM": 0.25, "KMLMSIM": 0.15, "TLTSIM": 0.15},
    "f7_rsst_heavy": {"NTSXSIM": 0.10, "RSSTSIM": 0.40, "GDESIM": 0.25, "KMLMSIM": 0.10, "TLTSIM": 0.15},
    "f7_pure_stack": {"RSSTSIM": 0.50, "GDESIM": 0.25, "KMLMSIM": 0.10, "TLTSIM": 0.15},  # NTSX 0%, sum=1.0
}


if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=41,
        iter_dir=iter_dir,
        hypothesis_slug="F7-US-Stacked-MF",
        primary_citation="[risk_parity, ch.5] + Return Stacked methodology (ReSolve/Newfound 2023)",
        configs=CONFIGS,
        cumulative_n_trials=148,  # 144 + 4
    )
    print(
        f"iter 041: status={verdict['status']}, "
        f"score={verdict['total_score']}, "
        f"sel={verdict['selected_config']}"
    )
