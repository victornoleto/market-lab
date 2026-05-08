"""Iter 039 backtest: F2-US-Factor-only (Phase 2 finalist construction).

Tests pure factor philosophy: equity via vanilla VTI + AVUV small-value +
SPMO momentum, diversified by KMLM/TLT/GLD. No stacking ETFs, no leverage.
4 configs sweep balanced vs factor-heavy vs sleeve-tilted weights.

KILL #4 (frankenstein degradation) is evaluated post-run by comparing best
F2 Sharpe to mean of best AVUV + SPMO Phase 1 Sharpes per dataset.

Citations:
- [risk_parity, ch.2, p.37-41] Fama-French factor framework
- [stocks_on_the_move, p.21-30] Clenow momentum + Frazzini-Israel-
  Moskowitz 2018 long-only capture coefficient ~0.60.
"""
from pathlib import Path

from studies.long_term_portfolio.run_iter import run_iter_full


CONFIGS = {
    "f2_balanced":     {"VTISIM": 0.35, "AVUVSIM": 0.15, "SPMOSIM": 0.10, "KMLMSIM": 0.20, "TLTSIM": 0.10, "GLDSIM": 0.10},
    "f2_factor_heavy": {"VTISIM": 0.25, "AVUVSIM": 0.25, "SPMOSIM": 0.15, "KMLMSIM": 0.15, "TLTSIM": 0.10, "GLDSIM": 0.10},
    "f2_avuv_heavy":   {"VTISIM": 0.30, "AVUVSIM": 0.25, "SPMOSIM": 0.05, "KMLMSIM": 0.20, "TLTSIM": 0.10, "GLDSIM": 0.10},
    "f2_spmo_heavy":   {"VTISIM": 0.30, "AVUVSIM": 0.10, "SPMOSIM": 0.20, "KMLMSIM": 0.20, "TLTSIM": 0.10, "GLDSIM": 0.10},
}


if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=39,
        iter_dir=iter_dir,
        hypothesis_slug="F2-US-Factor-only",
        primary_citation="[risk_parity, ch.2, p.37-41] + [stocks_on_the_move, p.21-30]",
        configs=CONFIGS,
        cumulative_n_trials=140,  # 136 + 4
    )
    print(
        f"iter 039: status={verdict['status']}, "
        f"score={verdict['total_score']}, "
        f"sel={verdict['selected_config']}"
    )
