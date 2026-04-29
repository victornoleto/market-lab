"""Iter 043 backtest: F1-TLT-variation (Phase 3B TLT slot variation).

Tests TLT-slot alternatives on the F1+SPLIT recommendation
(NTSX 25 + GDE 25 + KMLM 17.5 + DBMF 17.5 + TLT 15) from
FINAL_REPORT_seven_portfolios.md (score 62.07/100).

Question: TLT 15% reduces drawdown but eats into capital accumulation
(equity > bonds for long horizons). Three alternatives:

1. f1_no_tlt_to_equity — remove TLT, redistribute to equity-stacking
   (NTSX 32.5 + GDE 32.5). Tests "more equity wins long-term".
2. f1_no_tlt_to_mf — remove TLT, redistribute to MF (KMLM 25 + DBMF 25).
   Tests "trend-MF crisis-alpha replaces duration".
3. f1_rssb_replaces_tlt — replace TLT with RSSB (100% global stocks +
   100% Treasury via derivatives). Tests "stacking adds equity AND
   keeps bond hedge inside one ticker".

Citations:
- [risk_parity, ch.5, p.10] Carlson cap-efficient stacking
- [ilmanen_expected_returns, ch.19] duration vs MF crisis-alpha trade-off
- ReSolve/Newfound RSSB methodology (2023)

Window note: RSSBSIM is direct testfolio cache (1885+ → 2026; effective
window 1969+ for the lh_56y dataset). DBMFSIM is the bottleneck at
1999+ (26y window) for configs containing it.
"""
from pathlib import Path

from studies.long_term_portfolio.run_iter import run_iter_full


CONFIGS = {
    # Baseline: current F1+SPLIT recommendation
    "f1_split_baseline": {
        "NTSXSIM": 0.25, "GDESIM": 0.25,
        "KMLMSIM": 0.175, "DBMFSIM": 0.175,
        "TLTSIM": 0.15,
    },
    # Variation 1: remove TLT, redistribute 7.5% each to NTSX + GDE
    "f1_no_tlt_to_equity": {
        "NTSXSIM": 0.325, "GDESIM": 0.325,
        "KMLMSIM": 0.175, "DBMFSIM": 0.175,
    },
    # Variation 2: remove TLT, redistribute 7.5% each to KMLM + DBMF
    "f1_no_tlt_to_mf": {
        "NTSXSIM": 0.25, "GDESIM": 0.25,
        "KMLMSIM": 0.25, "DBMFSIM": 0.25,
    },
    # Variation 3: replace TLT with RSSB (stocks+bonds stacked)
    "f1_rssb_replaces_tlt": {
        "NTSXSIM": 0.25, "GDESIM": 0.25,
        "KMLMSIM": 0.175, "DBMFSIM": 0.175,
        "RSSBSIM": 0.15,
    },
}


if __name__ == "__main__":
    iter_dir = Path(__file__).parent
    verdict = run_iter_full(
        iter_n=43,
        iter_dir=iter_dir,
        hypothesis_slug="F1-TLT-variation",
        primary_citation="[risk_parity, ch.5, p.10]",
        configs=CONFIGS,
        cumulative_n_trials=156,  # 152 + 4
    )
    print(
        f"iter 043 TLT variation: status={verdict['status']}, "
        f"score={verdict['total_score']}, sel={verdict['selected_config']}"
    )
    print()
    print("All configs detailed metrics:")
    for cfg, ds_metrics in verdict.get("all_configs_metrics", {}).items():
        print(f"  {cfg}:")
        for ds, m in ds_metrics.items():
            print(
                f"    {ds}: Sharpe={m.get('sharpe', 0):.3f}, "
                f"CAGR={m.get('cagr', 0) * 100:.2f}%, "
                f"MDD={m.get('mdd', 0) * 100:.2f}%"
            )
