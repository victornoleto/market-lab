"""Iter 037 backtest: IDMO-realloc — Phase 1B substitution source variation.

Citation: [ilmanen_expected_returns, ch.19] + [stocks_on_the_move, p.21-30]
intl momentum overlay.

Phase 1B retest of IDMO at fixed 10% under 3 alternative sub sources.
Tests if sub-source variation amplifies Phase 1A's cosmetic ndx_real
+0.005 edge or recovers lh_56y drag.

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
print(f"[iter-037] KILL #3 check: IDMO standalone Sharpe = {idmo_sharpe:.3f} (< 1.5 OK)")


CONFIGS = {
    "idmo10_subNTSX": {"NTSXSIM": 0.15, "GDESIM": 0.25, "KMLMSIM": 0.35, "TLTSIM": 0.15, "IDMOSIM": 0.10},
    "idmo10_subGDE":  {"NTSXSIM": 0.25, "GDESIM": 0.15, "KMLMSIM": 0.35, "TLTSIM": 0.15, "IDMOSIM": 0.10},
    "idmo10_subKMLM": {"NTSXSIM": 0.25, "GDESIM": 0.25, "KMLMSIM": 0.25, "TLTSIM": 0.15, "IDMOSIM": 0.10},
}


if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=37,
        iter_dir=iter_dir,
        hypothesis_slug="IDMO-realloc",
        primary_citation="[ilmanen_expected_returns, ch.19] + [stocks_on_the_move, p.21-30]",
        configs=CONFIGS,
        cumulative_n_trials=133,  # 130 + 3
    )
    print(
        f"iter 037: status={verdict['status']}, "
        f"score={verdict['total_score']}, "
        f"sel={verdict['selected_config']}"
    )
