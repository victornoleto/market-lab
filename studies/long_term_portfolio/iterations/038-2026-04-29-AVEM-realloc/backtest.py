"""Iter 038 backtest: AVEM-realloc — Phase 1B substitution source variation.

Citation: [ilmanen_expected_returns, ch.19] intl + EM diversification.

Phase 1B retest of AVEM at fixed 10% under 3 alternative sub sources.
WINDOW CAVEAT: VWOSIM (underlying AVEMSIM) starts 1994-05-04 →
effective lh_56y window is 32y (1994-2026), NOT 56y. run_iter_full
internal dropna() alignment handles intersection automatically. Sub
source variation does not change this fundamental window constraint.
"""
from pathlib import Path

from studies.long_term_portfolio.run_iter import run_iter_full


CONFIGS = {
    "avem10_subNTSX": {"NTSXSIM": 0.15, "GDESIM": 0.25, "KMLMSIM": 0.35, "TLTSIM": 0.15, "AVEMSIM": 0.10},
    "avem10_subGDE":  {"NTSXSIM": 0.25, "GDESIM": 0.15, "KMLMSIM": 0.35, "TLTSIM": 0.15, "AVEMSIM": 0.10},
    "avem10_subKMLM": {"NTSXSIM": 0.25, "GDESIM": 0.25, "KMLMSIM": 0.25, "TLTSIM": 0.15, "AVEMSIM": 0.10},
}


if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=38,
        iter_dir=iter_dir,
        hypothesis_slug="AVEM-realloc",
        primary_citation="[ilmanen_expected_returns, ch.19]",
        configs=CONFIGS,
        cumulative_n_trials=136,  # 133 + 3
    )
    print(
        f"iter 038: status={verdict['status']}, "
        f"score={verdict['total_score']}, "
        f"sel={verdict['selected_config']}"
    )
