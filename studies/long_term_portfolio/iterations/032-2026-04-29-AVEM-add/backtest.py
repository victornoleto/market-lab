"""Iter 032 backtest: AVEM EM factor add on iter 023 base.

Citation: [ilmanen_expected_returns, ch.19] intl + EM diversification +
[risk_parity, ch.2, p.37-41] Fama-French factor framework.

WINDOW CAVEAT: VWOSIM (EM equity underlying AVEMSIM) starts 1994-05-04.
AVEM-using configs cannot run lh_56y fully; effective window is 32y
(1994-2026), not 56y. run_iter_full internal dropna() alignment handles
the intersection automatically. See hypothesis.md for full caveat.
"""
from pathlib import Path

from studies.long_term_portfolio.run_iter import run_iter_full


CONFIGS = {
    "avem_lite":  {"NTSXSIM": 0.225, "GDESIM": 0.25, "KMLMSIM": 0.325, "TLTSIM": 0.15, "AVEMSIM": 0.05},
    "avem_mod":   {"NTSXSIM": 0.200, "GDESIM": 0.25, "KMLMSIM": 0.300, "TLTSIM": 0.15, "AVEMSIM": 0.10},
    "avem_med":   {"NTSXSIM": 0.175, "GDESIM": 0.25, "KMLMSIM": 0.275, "TLTSIM": 0.15, "AVEMSIM": 0.15},
    "avem_heavy": {"NTSXSIM": 0.150, "GDESIM": 0.25, "KMLMSIM": 0.250, "TLTSIM": 0.15, "AVEMSIM": 0.20},
}


if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=32,
        iter_dir=iter_dir,
        hypothesis_slug="AVEM-add",
        primary_citation="[ilmanen_expected_returns, ch.19]",
        configs=CONFIGS,
        cumulative_n_trials=118,  # 114 + 4
    )
    print(
        f"iter 032: status={verdict['status']}, "
        f"score={verdict['total_score']}, "
        f"sel={verdict['selected_config']}"
    )
