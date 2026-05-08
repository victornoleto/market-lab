"""Iter 034 backtest: AVUV-realloc — Phase 1B substitution source variation.

Citation: [risk_parity, ch.2, p.37-41] Fama-French SCV factor framework
+ FF 1993 size+value premia.

Phase 1B retest of AVUV sleeve at fixed 10% weight under 3 alternative
substitution sources (from NTSX-only, GDE-only, KMLM-only) to test if
Phase 1A KILL #2 firing (monotonic regression, iter 028) was due to
suboptimal balanced-50/50 substitution from NTSX+KMLM.
"""
from pathlib import Path

from studies.long_term_portfolio.run_iter import run_iter_full


CONFIGS = {
    "avuv10_subNTSX": {"NTSXSIM": 0.15, "GDESIM": 0.25, "KMLMSIM": 0.35, "TLTSIM": 0.15, "AVUVSIM": 0.10},
    "avuv10_subGDE":  {"NTSXSIM": 0.25, "GDESIM": 0.15, "KMLMSIM": 0.35, "TLTSIM": 0.15, "AVUVSIM": 0.10},
    "avuv10_subKMLM": {"NTSXSIM": 0.25, "GDESIM": 0.25, "KMLMSIM": 0.25, "TLTSIM": 0.15, "AVUVSIM": 0.10},
}


if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=34,
        iter_dir=iter_dir,
        hypothesis_slug="AVUV-realloc",
        primary_citation="[risk_parity, ch.2, p.37-41]",
        configs=CONFIGS,
        cumulative_n_trials=124,  # 121 + 3
    )
    print(
        f"iter 034: status={verdict['status']}, "
        f"score={verdict['total_score']}, "
        f"sel={verdict['selected_config']}"
    )
