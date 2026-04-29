"""Iter 031 backtest: IDMO synth add on iter 023 base.

Citation: [ilmanen_expected_returns, ch.19] intl factor diversification
+ [stocks_on_the_move, p.21-30] Clenow + Jegadeesh-Titman 1993.

KILL #3 standalone Sharpe check enforced at top of execution.
"""
from pathlib import Path

import numpy as np

from studies.long_term_portfolio.run_iter import run_iter_full
from studies.long_term_portfolio.synths import idmo_synth_returns_from_cache


# KILL #3 standalone Sharpe check — synth must not exceed 1.5
idmo = idmo_synth_returns_from_cache()
idmo_sharpe = idmo.mean() / idmo.std() * np.sqrt(252)
assert idmo_sharpe < 1.5, (
    f"KILL #3: IDMO standalone Sharpe {idmo_sharpe:.3f} > 1.5"
)
print(f"[iter-031] KILL #3 check: IDMO standalone Sharpe = {idmo_sharpe:.3f} (< 1.5 OK)")


CONFIGS = {
    "idmo_lite":  {"NTSXSIM": 0.225, "GDESIM": 0.25, "KMLMSIM": 0.325, "TLTSIM": 0.15, "IDMOSIM": 0.05},
    "idmo_mod":   {"NTSXSIM": 0.200, "GDESIM": 0.25, "KMLMSIM": 0.300, "TLTSIM": 0.15, "IDMOSIM": 0.10},
    "idmo_med":   {"NTSXSIM": 0.175, "GDESIM": 0.25, "KMLMSIM": 0.275, "TLTSIM": 0.15, "IDMOSIM": 0.15},
    "idmo_heavy": {"NTSXSIM": 0.150, "GDESIM": 0.25, "KMLMSIM": 0.250, "TLTSIM": 0.15, "IDMOSIM": 0.20},
}


if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=31,
        iter_dir=iter_dir,
        hypothesis_slug="IDMO-synth",
        primary_citation="[ilmanen_expected_returns, ch.19]",
        configs=CONFIGS,
        cumulative_n_trials=114,  # 110 + 4
    )
    print(
        f"iter 031: status={verdict['status']}, "
        f"score={verdict['total_score']}, "
        f"sel={verdict['selected_config']}"
    )
