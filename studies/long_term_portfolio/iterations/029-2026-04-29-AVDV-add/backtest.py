"""Iter 029 backtest: AVDV factor add on iter 023 base.

Citation: [ilmanen_expected_returns, ch.19] intl factor diversification
+ [risk_parity, ch.2, p.37-41] Fama-French SCV.
"""
from pathlib import Path

from studies.long_term_portfolio.run_iter import run_iter_full


CONFIGS = {
    "avdv_lite":  {"NTSXSIM": 0.225, "GDESIM": 0.25, "KMLMSIM": 0.325, "TLTSIM": 0.15, "AVDVSIM": 0.05},
    "avdv_mod":   {"NTSXSIM": 0.200, "GDESIM": 0.25, "KMLMSIM": 0.300, "TLTSIM": 0.15, "AVDVSIM": 0.10},
    "avdv_med":   {"NTSXSIM": 0.175, "GDESIM": 0.25, "KMLMSIM": 0.275, "TLTSIM": 0.15, "AVDVSIM": 0.15},
    "avdv_heavy": {"NTSXSIM": 0.150, "GDESIM": 0.25, "KMLMSIM": 0.250, "TLTSIM": 0.15, "AVDVSIM": 0.20},
}


if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=29,
        iter_dir=iter_dir,
        hypothesis_slug="AVDV-add",
        primary_citation="[ilmanen_expected_returns, ch.19]",
        configs=CONFIGS,
        cumulative_n_trials=106,  # 102 + 4
    )
    print(
        f"iter 029: status={verdict['status']}, "
        f"score={verdict['total_score']}, "
        f"sel={verdict['selected_config']}"
    )
