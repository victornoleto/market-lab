"""Iter 028 backtest: AVUV factor add on iter 023 base.

Citation: [risk_parity, ch.2, p.37-41] Fama-French SCV factor framework
+ [advances_fin_ml, p.31-34] factor cross-validation.
"""
from pathlib import Path

from studies.long_term_portfolio.run_iter import run_iter_full


CONFIGS = {
    "avuv_lite":  {"NTSXSIM": 0.225, "GDESIM": 0.25, "KMLMSIM": 0.325, "TLTSIM": 0.15, "AVUVSIM": 0.05},
    "avuv_mod":   {"NTSXSIM": 0.200, "GDESIM": 0.25, "KMLMSIM": 0.300, "TLTSIM": 0.15, "AVUVSIM": 0.10},
    "avuv_med":   {"NTSXSIM": 0.175, "GDESIM": 0.25, "KMLMSIM": 0.275, "TLTSIM": 0.15, "AVUVSIM": 0.15},
    "avuv_heavy": {"NTSXSIM": 0.150, "GDESIM": 0.25, "KMLMSIM": 0.250, "TLTSIM": 0.15, "AVUVSIM": 0.20},
}


if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=28,
        iter_dir=iter_dir,
        hypothesis_slug="AVUV-add",
        primary_citation="[risk_parity, ch.2, p.37-41]",
        configs=CONFIGS,
        cumulative_n_trials=102,  # 98 (post-iter-027) + 4 (this iter)
    )
    print(
        f"iter 028: status={verdict['status']}, "
        f"score={verdict['total_score']}, "
        f"sel={verdict['selected_config']}"
    )
