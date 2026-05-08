"""Iter 040 backtest: F3-US-Hybrid-SPMO (Phase 2 finalist construction).

Tests iter 023 (NTSX+GDE+KMLM+TLT) + SPMO at 4 weights (5/10/15/20%)
with KMLM as sole substitution source. Phase 1+1B confirmed SPMO is
the only validated sleeve add and KMLM-substitution is best for
ndx_real (+0.044 delta vs iter 023 in iter 036 spmo10_subKMLM).

KILL #4 evaluated post-run vs iter 023 baseline (1.189/1.004/1.135).

Citations:
- [risk_parity, ch.5, p.10] Carlson cap-efficient stacking baseline
- [stocks_on_the_move, p.21-30] Clenow time-series momentum.
"""
from pathlib import Path

from studies.long_term_portfolio.run_iter import run_iter_full


CONFIGS = {
    "f3_spmo_5_subKMLM":  {"NTSXSIM": 0.25, "GDESIM": 0.25, "KMLMSIM": 0.30, "TLTSIM": 0.15, "SPMOSIM": 0.05},
    "f3_spmo_10_subKMLM": {"NTSXSIM": 0.25, "GDESIM": 0.25, "KMLMSIM": 0.25, "TLTSIM": 0.15, "SPMOSIM": 0.10},
    "f3_spmo_15_subKMLM": {"NTSXSIM": 0.25, "GDESIM": 0.25, "KMLMSIM": 0.20, "TLTSIM": 0.15, "SPMOSIM": 0.15},
    "f3_spmo_20_subKMLM": {"NTSXSIM": 0.25, "GDESIM": 0.25, "KMLMSIM": 0.15, "TLTSIM": 0.15, "SPMOSIM": 0.20},
}


if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=40,
        iter_dir=iter_dir,
        hypothesis_slug="F3-US-Hybrid-SPMO",
        primary_citation="[risk_parity, ch.5, p.10] + [stocks_on_the_move, p.21-30]",
        configs=CONFIGS,
        cumulative_n_trials=144,  # 140 + 4
    )
    print(
        f"iter 040: status={verdict['status']}, "
        f"score={verdict['total_score']}, "
        f"sel={verdict['selected_config']}"
    )
