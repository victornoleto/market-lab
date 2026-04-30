"""Iter 035 backtest: AVDV-realloc — Phase 1B substitution source variation.

Citation: [ilmanen_expected_returns, ch.19] intl factor diversification.

Phase 1B retest of AVDV (intl SCV) at fixed 10% under 3 alternative
sub sources (NTSX-only, GDE-only, KMLM-only). Tests whether Phase 1A
KILL #1+#2 firings (iter 029) were sub-source artifact.
"""
from pathlib import Path

from studies.long_term_portfolio.run_iter import run_iter_full


CONFIGS = {
    "avdv10_subNTSX": {"NTSXSIM": 0.15, "GDESIM": 0.25, "KMLMSIM": 0.35, "TLTSIM": 0.15, "AVDVSIM": 0.10},
    "avdv10_subGDE":  {"NTSXSIM": 0.25, "GDESIM": 0.15, "KMLMSIM": 0.35, "TLTSIM": 0.15, "AVDVSIM": 0.10},
    "avdv10_subKMLM": {"NTSXSIM": 0.25, "GDESIM": 0.25, "KMLMSIM": 0.25, "TLTSIM": 0.15, "AVDVSIM": 0.10},
}


if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=35,
        iter_dir=iter_dir,
        hypothesis_slug="AVDV-realloc",
        primary_citation="[ilmanen_expected_returns, ch.19]",
        configs=CONFIGS,
        cumulative_n_trials=127,  # 124 + 3
    )
    print(
        f"iter 035: status={verdict['status']}, "
        f"score={verdict['total_score']}, "
        f"sel={verdict['selected_config']}"
    )
