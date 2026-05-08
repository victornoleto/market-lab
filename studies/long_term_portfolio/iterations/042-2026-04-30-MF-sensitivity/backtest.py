"""Iter 042 backtest: MF sleeve sensitivity on iter 023 baseline (Phase 3).

Substitutes iter 023's 35% KMLMSIM with 4 MF candidates (KMLM full, DBMF
full, 50/50 split, CTA-proxy=KMLM placeholder). Holds NTSX/GDE/TLT
weights constant. Determines deploy-ready MF sleeve recommendation under
the AUM stability constraint (DBMF $3.2B vs KMLM $600M for 20-30y deploy).

Window caveat: DBMFSIM starts 1999-12-31 (26y window). The 4-config
comparison is fair on the 26y intersection where DBMF data exists.
``run_iter_full`` aligns components via dropna intersection automatically
(see ``run_iter.portfolio_returns_from_config``).

mf_cta_proxy is structurally identical to mf_kmlm (INCOMPLETE flag —
Simplify CTA Altis engine not modeled in testfolio). The config exists
to flag CTA as a deploy alternative requiring future work.

Citations:
- [ilmanen_expected_returns, ch.19] MF crisis-alpha role
- iMGP DBi DBMF prospectus + KFA MLM Index prospectus + Simplify CTA prospectus
"""
from pathlib import Path

from studies.long_term_portfolio.run_iter import run_iter_full


CONFIGS = {
    "mf_kmlm":      {"NTSXSIM": 0.25, "GDESIM": 0.25, "KMLMSIM": 0.35, "TLTSIM": 0.15},  # baseline (iter 023 unchanged)
    "mf_dbmf":      {"NTSXSIM": 0.25, "GDESIM": 0.25, "DBMFSIM": 0.35, "TLTSIM": 0.15},  # full DBMF substitution
    "mf_split":     {"NTSXSIM": 0.25, "GDESIM": 0.25, "KMLMSIM": 0.175, "DBMFSIM": 0.175, "TLTSIM": 0.15},  # 50/50 KMLM + DBMF
    "mf_cta_proxy": {"NTSXSIM": 0.25, "GDESIM": 0.25, "KMLMSIM": 0.35, "TLTSIM": 0.15},  # INCOMPLETE proxy (=mf_kmlm)
}


if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=42,
        iter_dir=iter_dir,
        hypothesis_slug="MF-sensitivity",
        primary_citation="[ilmanen_expected_returns, ch.19]",
        configs=CONFIGS,
        cumulative_n_trials=152,  # 148 + 4
    )
    print(
        f"iter 042 MF sensitivity: best={verdict['selected_config']}, "
        f"score={verdict['total_score']}"
    )
    print(
        "All configs Sharpe (lh_56y): "
        + str([(k, v.get('lh_56y', {}).get('sharpe'))
               for k, v in verdict.get('all_configs_metrics', {}).items()])
    )
