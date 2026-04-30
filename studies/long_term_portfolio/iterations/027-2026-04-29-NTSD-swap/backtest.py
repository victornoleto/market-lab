"""Iter 027 backtest: NTSD swap on iter 023 base.

Citation: [risk_parity, ch.5, p.10] Carlson cap-efficient stacking +
WisdomTree NTSD prospectus 2026-03-19.
"""
from pathlib import Path

from studies.long_term_portfolio.run_iter import run_iter_full


CONFIGS = {
    "ntsd_lite_2055":  {"NTSXSIM": 0.20, "NTSDSIM": 0.05, "GDESIM": 0.25, "KMLMSIM": 0.35, "TLTSIM": 0.15},
    "ntsd_mod_15105":  {"NTSXSIM": 0.15, "NTSDSIM": 0.10, "GDESIM": 0.25, "KMLMSIM": 0.35, "TLTSIM": 0.15},
    "ntsd_med_10155":  {"NTSXSIM": 0.10, "NTSDSIM": 0.15, "GDESIM": 0.25, "KMLMSIM": 0.35, "TLTSIM": 0.15},
    "ntsd_heavy_5205": {"NTSXSIM": 0.05, "NTSDSIM": 0.20, "GDESIM": 0.25, "KMLMSIM": 0.35, "TLTSIM": 0.15},
}


if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=27,
        iter_dir=iter_dir,
        hypothesis_slug="NTSD-swap",
        primary_citation="[risk_parity, ch.5, p.10]",
        configs=CONFIGS,
        cumulative_n_trials=98,  # 94 (post-iter-026) + 4 (this iter)
    )
    print(
        f"iter 027: status={verdict['status']}, "
        f"score={verdict['total_score']}, "
        f"sel={verdict['selected_config']}"
    )
