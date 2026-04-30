"""Iter 030 backtest: SPMO synth add on iter 023 base.

Citation: [stocks_on_the_move, p.21-30] Clenow time-series momentum +
Jegadeesh-Titman 1993 cross-sectional momentum + Frazzini-Israel-
Moskowitz 2018 (UMD long-only capture coefficient ~0.60).

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
print(f"[iter-030] KILL #3 check: SPMO standalone Sharpe = {spmo_sharpe:.3f} (< 1.5 OK)")


CONFIGS = {
    "spmo_lite":  {"NTSXSIM": 0.225, "GDESIM": 0.25, "KMLMSIM": 0.325, "TLTSIM": 0.15, "SPMOSIM": 0.05},
    "spmo_mod":   {"NTSXSIM": 0.200, "GDESIM": 0.25, "KMLMSIM": 0.300, "TLTSIM": 0.15, "SPMOSIM": 0.10},
    "spmo_med":   {"NTSXSIM": 0.175, "GDESIM": 0.25, "KMLMSIM": 0.275, "TLTSIM": 0.15, "SPMOSIM": 0.15},
    "spmo_heavy": {"NTSXSIM": 0.150, "GDESIM": 0.25, "KMLMSIM": 0.250, "TLTSIM": 0.15, "SPMOSIM": 0.20},
}


if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=30,
        iter_dir=iter_dir,
        hypothesis_slug="SPMO-synth",
        primary_citation="[stocks_on_the_move, p.21-30]",
        configs=CONFIGS,
        cumulative_n_trials=110,  # 106 + 4
    )
    print(
        f"iter 030: status={verdict['status']}, "
        f"score={verdict['total_score']}, "
        f"sel={verdict['selected_config']}"
    )
