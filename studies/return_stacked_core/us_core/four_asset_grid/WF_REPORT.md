# Four-Asset Grid Walk-Forward Analysis

Status: research-only diagnostic. No deployment, paper-trade label or mandate change.

## Summary

- Setup: `8y` in-sample optimize -> `2y` OOS, rolled by `2y`.
- Candidate grid: all `1,771` 5%-step portfolios over `NTSXSIM/GDESIM/RSST70_30/ZROZSIM`.
- Train objective: same rank-based fitness as the full grid, computed only inside each IS window.
- WF selected combined OOS: CAGR `12.57%`, MDD `-34.47%`, Sharpe `0.821`, terminal `8.369x`.
- Beat fixed RSC-like `35/40/25` in `3/9` windows; required `7/9` for the 75% consistency read. Verdict: **FAIL**.
- Selection stability: `9/9` unique selected portfolios; no allocation repeated across OOS windows.
- Median selected OOS rank percentile: `39.53%`; mean train/test fitness Spearman: `0.144`.

This directly tests the overfit concern: the allocation is selected using only prior data, then held in the subsequent OOS block. Walk-forward selection is a robustness diagnostic against choosing parameters on the full sample `[testing_tuning, p.318-320]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

## Combined OOS Metrics

| strategy | cagr | mdd | vol | sharpe | sortino | calmar | terminal | windows_beat_rsc_like | pass_vs_rsc_like_75pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rsc_like_35_40_25 | 12.63% | -30.76% | 15.62% | 0.840 | 1.204 | 0.411 | 8.447 |  |  |
| wf_selected | 12.57% | -34.47% | 15.98% | 0.821 | 1.180 | 0.365 | 8.369 | 3 | FAIL |
| full_grid_top_lookahead | 11.95% | -26.95% | 15.00% | 0.828 | 1.191 | 0.443 | 7.571 |  |  |
| b4_equal_25 | 11.65% | -29.26% | 14.59% | 0.828 | 1.190 | 0.398 | 7.216 |  |  |

## OOS Window Details

| window | test_start | test_end | selected_portfolio | test_cagr | test_mdd | test_rank_pct | rsc_like_cagr | full_top_cagr | beat_rsc_like | train_test_fitness_spearman |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2008-01-03 | 2009-12-31 | 5% NTSXSIM / 45% GDESIM / 50% ZROZSIM | 2.34% | -23.22% | 0.51% | 0.21% | 1.28% | PASS | 0.864 |
| 2 | 2010-01-04 | 2011-12-30 | 45% GDESIM / 55% ZROZSIM | 31.74% | -9.96% | 15.30% | 22.18% | 25.80% | PASS | 0.785 |
| 3 | 2012-01-03 | 2014-01-02 | 40% GDESIM / 10% RSST70_30 / 50% ZROZSIM | 0.15% | -16.10% | 90.91% | 7.25% | 4.08% | FAIL | -0.791 |
| 4 | 2014-01-03 | 2015-12-31 | 15% NTSXSIM / 40% GDESIM / 5% RSST70_30 / 40% ZROZSIM | 10.11% | -13.71% | 73.35% | 12.54% | 11.55% | FAIL | 0.076 |
| 5 | 2016-01-04 | 2018-01-02 | 10% GDESIM / 50% RSST70_30 / 40% ZROZSIM | 11.39% | -14.12% | 85.26% | 15.82% | 15.84% | FAIL | -0.640 |
| 6 | 2018-01-03 | 2020-01-02 | 70% NTSXSIM / 15% GDESIM / 15% ZROZSIM | 12.59% | -13.35% | 18.75% | 12.74% | 13.02% | FAIL | 0.145 |
| 7 | 2020-01-03 | 2021-12-31 | 85% NTSXSIM / 15% ZROZSIM | 20.95% | -22.24% | 39.53% | 23.73% | 21.80% | FAIL | 0.557 |
| 8 | 2022-01-03 | 2024-01-02 | 65% NTSXSIM / 5% GDESIM / 30% ZROZSIM | -9.75% | -34.03% | 81.25% | -2.84% | -5.53% | FAIL | -0.527 |
| 9 | 2024-01-03 | 2026-01-02 | 70% GDESIM / 15% RSST70_30 / 15% ZROZSIM | 42.63% | -15.33% | 4.74% | 25.73% | 23.88% | PASS | 0.824 |

## Selection Stability

| selected_portfolio | n_windows | share_windows | avg_test_cagr | avg_test_mdd | avg_test_rank_pct |
| --- | --- | --- | --- | --- | --- |
| 5% NTSXSIM / 45% GDESIM / 50% ZROZSIM | 1 | 11.11% | 2.34% | -23.22% | 0.51% |
| 45% GDESIM / 55% ZROZSIM | 1 | 11.11% | 31.74% | -9.96% | 15.30% |
| 40% GDESIM / 10% RSST70_30 / 50% ZROZSIM | 1 | 11.11% | 0.15% | -16.10% | 90.91% |
| 15% NTSXSIM / 40% GDESIM / 5% RSST70_30 / 40% ZROZSIM | 1 | 11.11% | 10.11% | -13.71% | 73.35% |
| 10% GDESIM / 50% RSST70_30 / 40% ZROZSIM | 1 | 11.11% | 11.39% | -14.12% | 85.26% |
| 70% NTSXSIM / 15% GDESIM / 15% ZROZSIM | 1 | 11.11% | 12.59% | -13.35% | 18.75% |
| 85% NTSXSIM / 15% ZROZSIM | 1 | 11.11% | 20.95% | -22.24% | 39.53% |
| 65% NTSXSIM / 5% GDESIM / 30% ZROZSIM | 1 | 11.11% | -9.75% | -34.03% | 81.25% |
| 70% GDESIM / 15% RSST70_30 / 15% ZROZSIM | 1 | 11.11% | 42.63% | -15.33% | 4.74% |

## Interpretation

- `wf_selected` is the only non-lookahead optimizer result in this report.
- `full_grid_top_lookahead` is included as a diagnostic benchmark because it is the full-sample winner; it is not a valid selection rule.
- If WF-selected weights fail to beat simple fixed anchors consistently, the full-sample top should be treated as overfit-prone and not as a promoted allocation.
- This still is not full validation: PBO/DSR/bootstrap/cross-library, real implementation costs, taxes and account-level constraints remain absent `[advances_fin_ml, p.208-211]`, `[systematic_trading, p.185-188]`.

## Artifacts

- Windows: `studies/return_stacked_core/us_core/four_asset_grid/results/walk_forward_windows.csv`.
- Summary: `studies/return_stacked_core/us_core/four_asset_grid/results/walk_forward_summary.csv`.
- Equity/returns: `studies/return_stacked_core/us_core/four_asset_grid/results/walk_forward_equity.csv`.
- Selection stability: `studies/return_stacked_core/us_core/four_asset_grid/results/walk_forward_selection_stability.csv`.
