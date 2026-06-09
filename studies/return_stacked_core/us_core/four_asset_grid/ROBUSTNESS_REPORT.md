# Four-Asset Grid Robustness: WF Sensitivity, Stability, CPCV/PBO

Status: research-only diagnostic. No deployment, paper-trade label or mandate change.

## Summary

- PBO over the full `1,771`-portfolio grid: `0.655` -> `reject`. Gate reference: reject when PBO >= 0.5 `[advances_fin_ml, p.208-211]`.
- CPCV split selection beat fixed RSC-like `35/40/25` in `7/28` splits; 75% consistency would require `21/28`.
- CPCV selected `20` unique portfolios across `28` splits; median OOS rank percentile `44.41%`; mean train/test Spearman `0.031`.
- WF sensitivity does not rescue optimization: no scenario reaches the 75% beat-RSC consistency threshold.
- Best fixed rule in default OOS comparison is `rsc_like_35_40_25` with OOS CAGR `12.63%` and MDD `-30.76%`; RSC-like is OOS CAGR `12.63%`, MDD `-30.76%`.

Interpretation: the grid is useful as a neighborhood/stress screen, but the weight optimizer itself is unstable. The robust action is to keep a simple fixed allocation thesis rather than reselecting weights from the same grid `[testing_tuning, p.318-320]`, `[testing_tuning, p.327-335]`, `[systematic_trading, p.185-188]`.

## WF Sensitivity

| scenario | n_windows | wf_cagr | wf_mdd | wf_sharpe | rsc_cagr | rsc_mdd | windows_beat_rsc_like | pass_vs_rsc_like_75pct | unique_selected_portfolios | mean_train_test_fitness_spearman |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rolling_5y_1y | 21 | 11.51% | -33.52% | 0.755 | 13.25% | -30.76% | 8 | FAIL | 21 | -0.000 |
| rolling_8y_2y | 9 | 12.57% | -34.47% | 0.821 | 12.63% | -30.76% | 3 | FAIL | 9 | 0.144 |
| rolling_10y_2y | 8 | 11.80% | -33.76% | 0.852 | 14.29% | -24.85% | 1 | FAIL | 7 | 0.177 |
| rolling_12y_3y | 4 | 8.06% | -34.61% | 0.639 | 11.30% | -24.85% | 0 | FAIL | 4 | -0.112 |
| expanding_8y_2y | 9 | 10.98% | -30.16% | 0.760 | 12.63% | -30.76% | 2 | FAIL | 7 | 0.150 |

## CPCV/PBO

| pbo | pbo_gate | n_blocks | n_combinations | logit_mean | logit_median | logit_p10 | logit_p90 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.655 | reject | 10 | 252 | -0.170 | -0.424 | -1.658 | 1.736 |

| split | selected_portfolio | test_cagr | test_mdd | test_rank_pct | beat_rsc_like | train_test_fitness_spearman |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 40% GDESIM / 30% RSST70_30 / 30% ZROZSIM | 8.81% | -23.15% | 27.22% | PASS | 0.025 |
| 2 | 10% NTSXSIM / 45% GDESIM / 25% RSST70_30 / 20% ZROZSIM | 4.82% | -35.05% | 46.02% | FAIL | -0.529 |
| 3 | 40% GDESIM / 35% RSST70_30 / 25% ZROZSIM | 8.03% | -25.90% | 44.27% | PASS | -0.331 |
| 4 | 55% GDESIM / 15% RSST70_30 / 30% ZROZSIM | 5.69% | -22.58% | 47.54% | FAIL | -0.456 |
| 5 | 35% GDESIM / 35% RSST70_30 / 30% ZROZSIM | 4.52% | -23.35% | 38.85% | PASS | -0.198 |
| 6 | 10% NTSXSIM / 40% GDESIM / 15% RSST70_30 / 35% ZROZSIM | 4.78% | -30.83% | 24.28% | FAIL | 0.181 |
| 7 | 35% GDESIM / 35% RSST70_30 / 30% ZROZSIM | 9.31% | -23.35% | 13.95% | PASS | 0.518 |
| 8 | 35% GDESIM / 35% RSST70_30 / 30% ZROZSIM | 14.54% | -27.90% | 7.51% | PASS | 0.606 |
| 9 | 30% GDESIM / 35% RSST70_30 / 35% ZROZSIM | 16.22% | -17.52% | 32.58% | FAIL | 0.503 |
| 10 | 45% GDESIM / 20% RSST70_30 / 35% ZROZSIM | 14.85% | -18.93% | 62.11% | FAIL | 0.076 |
| 11 | 35% GDESIM / 30% RSST70_30 / 35% ZROZSIM | 11.97% | -20.01% | 56.07% | FAIL | 0.160 |
| 12 | 5% NTSXSIM / 35% GDESIM / 15% RSST70_30 / 45% ZROZSIM | 9.96% | -32.67% | 73.29% | FAIL | -0.208 |

## Top-Decile Stability Map

Top-decile stability uses the default `8y` IS windows and records portfolios that land in the train top 10%. This asks for a stable region, not a single lucky argmax.

| sleeve | mean | p10 | p25 | median | p75 | p90 |
| --- | --- | --- | --- | --- | --- | --- |
| ntsx | 25.225 | 0.000 | 5.000 | 20.000 | 40.000 | 60.000 |
| gde | 27.203 | 5.000 | 10.000 | 25.000 | 40.000 | 55.000 |
| rsst70_30 | 14.619 | 0.000 | 5.000 | 10.000 | 20.000 | 30.000 |
| zroz | 32.953 | 10.000 | 20.000 | 35.000 | 45.000 | 50.000 |
| rsc_like_top_decile_windows | 0.000 | n/a | n/a | n/a | n/a | n/a |

Most frequent exact top-decile portfolios:

| portfolio | n_top_decile_windows | share_windows | avg_rank | ntsx_pct | gde_pct | rsst70_30_pct | zroz_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 30% GDESIM / 25% RSST70_30 / 45% ZROZSIM | 5 | 55.56% | 56.000 | 0 | 30 | 25 | 45 |
| 5% NTSXSIM / 30% GDESIM / 20% RSST70_30 / 45% ZROZSIM | 5 | 55.56% | 61.000 | 5 | 30 | 20 | 45 |
| 10% NTSXSIM / 30% GDESIM / 15% RSST70_30 / 45% ZROZSIM | 5 | 55.56% | 67.800 | 10 | 30 | 15 | 45 |
| 30% GDESIM / 20% RSST70_30 / 50% ZROZSIM | 5 | 55.56% | 75.600 | 0 | 30 | 20 | 50 |
| 25% GDESIM / 30% RSST70_30 / 45% ZROZSIM | 5 | 55.56% | 81.200 | 0 | 25 | 30 | 45 |
| 5% NTSXSIM / 25% GDESIM / 25% RSST70_30 / 45% ZROZSIM | 5 | 55.56% | 81.800 | 5 | 25 | 25 | 45 |
| 10% NTSXSIM / 25% GDESIM / 20% RSST70_30 / 45% ZROZSIM | 5 | 55.56% | 85.800 | 10 | 25 | 20 | 45 |
| 30% GDESIM / 30% RSST70_30 / 40% ZROZSIM | 5 | 55.56% | 91.200 | 0 | 30 | 30 | 40 |
| 5% NTSXSIM / 30% GDESIM / 25% RSST70_30 / 40% ZROZSIM | 5 | 55.56% | 93.200 | 5 | 30 | 25 | 40 |
| 15% NTSXSIM / 25% GDESIM / 15% RSST70_30 / 45% ZROZSIM | 5 | 55.56% | 97.000 | 15 | 25 | 15 | 45 |
| 10% NTSXSIM / 30% GDESIM / 20% RSST70_30 / 40% ZROZSIM | 5 | 55.56% | 97.400 | 10 | 30 | 20 | 40 |
| 30% NTSXSIM / 30% GDESIM / 40% ZROZSIM | 5 | 55.56% | 111.000 | 30 | 30 | 0 | 40 |
| 15% NTSXSIM / 25% GDESIM / 20% RSST70_30 / 40% ZROZSIM | 5 | 55.56% | 111.600 | 15 | 25 | 20 | 40 |
| 20% NTSXSIM / 25% GDESIM / 15% RSST70_30 / 40% ZROZSIM | 5 | 55.56% | 117.000 | 20 | 25 | 15 | 40 |
| 10% NTSXSIM / 20% GDESIM / 25% RSST70_30 / 45% ZROZSIM | 5 | 55.56% | 126.200 | 10 | 20 | 25 | 45 |

## Fixed Rules

| rule | portfolio | full_cagr | full_mdd | oos_cagr | oos_mdd | oos_sharpe | oos_terminal |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rsc_like_35_40_25 | 35% GDESIM / 40% RSST70_30 / 25% ZROZSIM | 12.29% | -30.76% | 12.63% | -30.76% | 0.840 | 8.447 |
| gde_tilt_40_30_30 | 40% GDESIM / 30% RSST70_30 / 30% ZROZSIM | 12.36% | -28.78% | 12.42% | -28.78% | 0.842 | 8.168 |
| full_grid_top_40_25_35 | 40% GDESIM / 25% RSST70_30 / 35% ZROZSIM | 12.15% | -27.80% | 11.95% | -26.95% | 0.828 | 7.571 |
| mf_tilt_30_40_30 | 30% GDESIM / 40% RSST70_30 / 30% ZROZSIM | 11.85% | -27.25% | 11.94% | -27.25% | 0.833 | 7.560 |
| defensive_35_30_35 | 35% GDESIM / 30% RSST70_30 / 35% ZROZSIM | 11.90% | -26.40% | 11.71% | -25.94% | 0.826 | 7.292 |
| b4_equal_25 | 25% NTSXSIM / 25% GDESIM / 25% RSST70_30 / 25% ZROZSIM | 11.23% | -29.26% | 11.65% | -29.26% | 0.828 | 7.216 |

## Artifacts

- WF sensitivity: `studies/return_stacked_core/us_core/four_asset_grid/results/robustness_wf_sensitivity.csv`.
- Top-decile portfolios: `studies/return_stacked_core/us_core/four_asset_grid/results/robustness_top_decile_portfolios.csv`.
- Top-decile weight distribution: `studies/return_stacked_core/us_core/four_asset_grid/results/robustness_top_decile_weight_distribution.csv`.
- CPCV splits: `studies/return_stacked_core/us_core/four_asset_grid/results/robustness_cpcv_splits.csv`.
- PBO summary: `studies/return_stacked_core/us_core/four_asset_grid/results/robustness_pbo_summary.csv`.
- Fixed rules: `studies/return_stacked_core/us_core/four_asset_grid/results/robustness_fixed_rules.csv`.
