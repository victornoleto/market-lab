"""Iter 036 backtest: SPMO-realloc — Phase 1B substitution source variation.

Citation: [stocks_on_the_move, p.21-30] Clenow time-series momentum +
Jegadeesh-Titman 1993 cross-sectional momentum + Frazzini-Israel-
Moskowitz 2018 (UMD long-only capture coefficient ~0.60).

Phase 1B retest of SPMO at fixed 10% under 3 alternative sub sources.
Highest-priority Phase 1B iter: SPMO is the only Phase 1A sleeve with
ndx_real +signal substantive (+0.032). Tests whether reallocating sub
source amplifies the +signal further or recovers lh_56y drag.

KILL #3 standalone Sharpe check enforced at top of execution.
"""
from pathlib import Path

import numpy as np

from studies.long_term_portfolio.run_iter import run_iter_full
from studies.long_term_portfolio.synths import spmo_synth_returns_from_cache


# KILL #3 standalone Sharpe check — synth must not exceed 1.5
spmo = spmo_synth_returns_from_cache()
spmo_sharpe = spmo.mean() / spmo.std() * np.sqrt(252)
assert spmo_sharpe < 1.5, (
    f"KILL #3: SPMO standalone Sharpe {spmo_sharpe:.3f} > 1.5"
)
print(f"[iter-036] KILL #3 check: SPMO standalone Sharpe = {spmo_sharpe:.3f} (< 1.5 OK)")


CONFIGS = {
    "spmo10_subNTSX": {"NTSXSIM": 0.15, "GDESIM": 0.25, "KMLMSIM": 0.35, "TLTSIM": 0.15, "SPMOSIM": 0.10},
    "spmo10_subGDE":  {"NTSXSIM": 0.25, "GDESIM": 0.15, "KMLMSIM": 0.35, "TLTSIM": 0.15, "SPMOSIM": 0.10},
    "spmo10_subKMLM": {"NTSXSIM": 0.25, "GDESIM": 0.25, "KMLMSIM": 0.25, "TLTSIM": 0.15, "SPMOSIM": 0.10},
}


if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=36,
        iter_dir=iter_dir,
        hypothesis_slug="SPMO-realloc",
        primary_citation="[stocks_on_the_move, p.21-30]",
        configs=CONFIGS,
        cumulative_n_trials=130,  # 127 + 3
    )
    print(
        f"iter 036: status={verdict['status']}, "
        f"score={verdict['total_score']}, "
        f"sel={verdict['selected_config']}"
    )
