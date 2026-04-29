"""Iter 033 backtest: NTSD-realloc — Phase 1B substitution source variation.

Citation: [risk_parity, ch.5, p.10] Carlson cap-efficient stacking +
WisdomTree NTSD prospectus 2026-03-19.

Phase 1B retest of NTSD sleeve at fixed 10% weight under 3 alternative
substitution sources (from NTSX-only, GDE-only, KMLM-only) to test if
Phase 1A KILL #1 + KILL #2 firings (iter 027) were due to suboptimal
balanced-50/50 substitution from NTSX+KMLM. KILL #3 not applicable
(NTSDSIM is literal WisdomTree blueprint, not academic overlay).
"""
from pathlib import Path

from studies.long_term_portfolio.run_iter import run_iter_full


CONFIGS = {
    "ntsd10_subNTSX": {"NTSXSIM": 0.15, "NTSDSIM": 0.10, "GDESIM": 0.25, "KMLMSIM": 0.35, "TLTSIM": 0.15},
    "ntsd10_subGDE":  {"NTSXSIM": 0.25, "NTSDSIM": 0.10, "GDESIM": 0.15, "KMLMSIM": 0.35, "TLTSIM": 0.15},
    "ntsd10_subKMLM": {"NTSXSIM": 0.25, "NTSDSIM": 0.10, "GDESIM": 0.25, "KMLMSIM": 0.25, "TLTSIM": 0.15},
}


if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=33,
        iter_dir=iter_dir,
        hypothesis_slug="NTSD-realloc",
        primary_citation="[risk_parity, ch.5, p.10]",
        configs=CONFIGS,
        cumulative_n_trials=121,  # 118 + 3
    )
    print(
        f"iter 033: status={verdict['status']}, "
        f"score={verdict['total_score']}, "
        f"sel={verdict['selected_config']}"
    )
