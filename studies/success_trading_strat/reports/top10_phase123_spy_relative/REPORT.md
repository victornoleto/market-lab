# Top 10 Strategies By Equity / SPY

## Verdict

This is an economic ranking across `success_trading_strat` Phases 1, 2 and 3. The score is terminal relative wealth, `strategy_equity / SPY_equity`, on aligned available dates. It is not a validation ranking and does not override failed MCPT/PBO/DSR gates `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

No strategy in this Top 10 is deploy-authorized. Mandate remains 100% Plano C.

## Files

- `all_phase123_spy_relative_candidates.csv`: all candidates with computable SPY-relative wealth.
- `top10_spy_relative.csv`: selected Top 10.
- `top10_returns.csv`: return series for Top 10 members with saved curves.
- `top10_rolling_relative.csv`: rolling relative-window diagnostics.
- `plots/top10_equity_over_spy_bar.png`: terminal relative wealth ranking.
- `plots/top10_equity_log.png`: available Top 10 equity curves.
- `plots/top10_equity_over_spy.png`: available Top 10 relative wealth curves.
- `plots/top10_drawdowns.png`: available Top 10 drawdowns.

## Ranking Method

For candidates with saved `returns.csv`, SPY is recomputed over the exact strategy return dates. For Phase 1 candidates without per-iteration returns, the script uses the saved `overnight_30_iter_review` selected-return curves when available. Metrics-only rows without an aligned SPY terminal are excluded from the Top 10 because the requested criterion is explicitly `equity/equity_spy`.

## Top 10

| phase | iteration | status | best_config | start | end | equity_over_spy_terminal | terminal_wealth | spy_terminal_wealth | cagr | spy_cagr | max_drawdown | sharpe | pbo | dsr_p | failed_gates |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| phase01 | 013-2026-05-14-crypto-donchian-trend | fail | eth_don20 | 2016-02-04 | 2026-05-13 | 38.9 | 179.9 | 4.625 | 66.12% | 16.15% | -35.51% | 1.364 | 0.2857 | 0.003641 | fwd_63d;walk_forward |
| phase03 | 013-2026-05-14-nasdaq-drawdown-rearm-booster | economic_beater_not_validated | qld_tqqq_dd25_recover_sma50_rv40 | 2010-02-12 | 2026-05-13 | 16.19 | 148.7 | 9.183 | 36.12% | 14.65% | -67.15% | 0.9299 | 0.4603 | 0.1932 | is_mcpt;wf_mcpt;dsr |
| phase03 | 027-2026-05-14-qld-vol-throttle-sleeve | economic_beater_not_validated | qld70_tlt15_gld15_rv126_q30_70_b50_c20 | 2007-01-12 | 2026-05-13 | 10.5 | 78.26 | 7.452 | 25.34% | 10.97% | -57.17% | 0.8453 | 0.377 | 0.2121 | is_mcpt;wf_mcpt;dsr |
| phase03 | 003-2026-05-14-semis-letf-vol-target | economic_beater_not_validated | tecl_vt40_rv63 | 2010-06-14 | 2026-05-13 | 9.421 | 84.93 | 9.015 | 32.25% | 14.84% | -49.24% | 0.8892 | 0.2063 | 0.1636 | is_mcpt;wf_mcpt;dsr |
| phase03 | 024-2026-05-14-qld-migration-sleeve | economic_beater_not_validated | qld70_tlt15_gld15_dd25_boost50 | 2007-01-12 | 2026-05-13 | 8.045 | 59.95 | 7.452 | 23.62% | 10.97% | -80.45% | 0.7382 | 0.1349 | 0.3668 | mdd_not_extreme_vs_primary;is_mcpt;wf_mcpt;dsr |
| phase03 | 019-2026-05-14-letf-light-gross-rotation | economic_beater_not_validated | top2_m126_g125 | 2007-08-02 | 2026-05-13 | 7.597 | 54.51 | 7.175 | 23.77% | 11.08% | -79.28% | 0.7047 | 0.5913 | 0.4351 | is_mcpt;wf_mcpt;pbo;dsr;bootstrap |
| phase03 | 022-2026-05-14-qqq-core-qld-overlay | economic_beater_not_validated | mom126_vol63_cap25 | 2007-01-12 | 2026-05-13 | 7.517 | 56.02 | 7.452 | 23.19% | 10.97% | -63.92% | 0.7983 | 0.7381 | 0.2723 | is_mcpt;wf_mcpt;pbo;dsr;bootstrap |
| phase03 | 018-2026-05-14-vxx-crash-rearm | economic_beater_not_validated | qqq_tqqq_vxx95_norm70_h126 | 2010-02-12 | 2026-05-13 | 6.648 | 61.04 | 9.183 | 28.85% | 14.65% | -35.38% | 1.021 | 0.7897 | 0.1111 | is_mcpt;wf_mcpt;pbo;dsr |
| phase03 | 008-2026-05-14-drawdown-adaptive-high-beta | economic_beater_not_validated | top2_m63_dd15_boost125_cap150 | 2001-10-19 | 2026-05-13 | 4.373 | 47.19 | 10.79 | 17.02% | 10.19% | -66.42% | 0.6636 | 0.623 | 0.3293 | is_mcpt;wf_mcpt;pbo;dsr |
| phase03 | 001-2026-05-14-nasdaq-letf-vol-target | economic_beater_not_validated | qld_vt35_rv21_dd25_half | 2010-05-17 | 2026-05-13 | 3.898 | 33.85 | 8.682 | 24.68% | 14.50% | -38.61% | 0.9296 | 0.4206 | 0.1472 | is_mcpt;wf_mcpt;dsr |

## Plots

![Top 10 terminal relative wealth](plots/top10_equity_over_spy_bar.png)

![Top 10 equity curves](plots/top10_equity_log.png)

![Top 10 equity over SPY](plots/top10_equity_over_spy.png)

![Top 10 drawdowns](plots/top10_drawdowns.png)

## Rolling Relative Diagnostics

| label | window_years | median_relative_end_ratio | min_relative_end_ratio | share_windows_beating_spy |
| --- | --- | --- | --- | --- |
| phase01 013 eth_don20 | 1 | 1.22 | 0.534 | 73.0% |
| phase01 013 eth_don20 | 3 | 2.27 | 0.58 | 66.9% |
| phase01 013 eth_don20 | 5 | 2.09 | 0.678 | 96.5% |
| phase01 013 eth_don20 | 10 | 21.5 | 18.8 | 100.0% |
| phase03 013 qld_tqqq_dd25_recover_sma50_rv40 | 1 | 1.21 | 0.422 | 80.4% |
| phase03 013 qld_tqqq_dd25_recover_sma50_rv40 | 3 | 1.61 | 0.857 | 96.0% |
| phase03 013 qld_tqqq_dd25_recover_sma50_rv40 | 5 | 2.17 | 1.18 | 100.0% |
| phase03 013 qld_tqqq_dd25_recover_sma50_rv40 | 10 | 4.82 | 3.07 | 100.0% |
| phase03 013 qld_tqqq_dd25_recover_sma50_rv40 | 15 | 10.1 | 7.06 | 100.0% |
| phase03 027 qld70_tlt15_gld15_rv126_q30_70_b50_c20 | 1 | 1.13 | 0.609 | 83.1% |
| phase03 027 qld70_tlt15_gld15_rv126_q30_70_b50_c20 | 3 | 1.55 | 0.857 | 95.0% |
| phase03 027 qld70_tlt15_gld15_rv126_q30_70_b50_c20 | 5 | 1.96 | 0.992 | 99.9% |
| phase03 027 qld70_tlt15_gld15_rv126_q30_70_b50_c20 | 10 | 3.98 | 2.54 | 100.0% |
| phase03 027 qld70_tlt15_gld15_rv126_q30_70_b50_c20 | 15 | 6.6 | 4.54 | 100.0% |
| phase03 003 tecl_vt40_rv63 | 1 | 1.13 | 0.668 | 65.7% |
| phase03 003 tecl_vt40_rv63 | 3 | 1.59 | 0.875 | 96.8% |
| phase03 003 tecl_vt40_rv63 | 5 | 2.26 | 0.978 | 99.9% |
| phase03 003 tecl_vt40_rv63 | 10 | 5.13 | 3.46 | 100.0% |
| phase03 003 tecl_vt40_rv63 | 15 | 7 | 5.18 | 100.0% |
| phase03 024 qld70_tlt15_gld15_dd25_boost50 | 1 | 1.13 | 0.443 | 80.3% |
| phase03 024 qld70_tlt15_gld15_dd25_boost50 | 3 | 1.35 | 0.793 | 91.9% |
| phase03 024 qld70_tlt15_gld15_dd25_boost50 | 5 | 1.69 | 0.976 | 99.9% |
| phase03 024 qld70_tlt15_gld15_dd25_boost50 | 10 | 3.05 | 1.62 | 100.0% |
| phase03 024 qld70_tlt15_gld15_dd25_boost50 | 15 | 5.1 | 2.44 | 100.0% |
| phase03 019 top2_m126_g125 | 1 | 1.16 | 0.443 | 68.9% |
| phase03 019 top2_m126_g125 | 3 | 1.33 | 0.687 | 95.5% |
| phase03 019 top2_m126_g125 | 5 | 1.73 | 0.873 | 95.9% |
| phase03 019 top2_m126_g125 | 10 | 2.67 | 1.63 | 100.0% |
| phase03 019 top2_m126_g125 | 15 | 4.71 | 1.7 | 100.0% |
| phase03 022 mom126_vol63_cap25 | 1 | 1.11 | 0.691 | 73.1% |
| phase03 022 mom126_vol63_cap25 | 3 | 1.4 | 0.949 | 99.6% |
| phase03 022 mom126_vol63_cap25 | 5 | 1.73 | 1.09 | 100.0% |
| phase03 022 mom126_vol63_cap25 | 10 | 3.05 | 2.3 | 100.0% |
| phase03 022 mom126_vol63_cap25 | 15 | 4.97 | 3.07 | 100.0% |
| phase03 018 qqq_tqqq_vxx95_norm70_h126 | 1 | 1.07 | 0.725 | 77.8% |
| phase03 018 qqq_tqqq_vxx95_norm70_h126 | 3 | 1.29 | 0.767 | 93.5% |
| phase03 018 qqq_tqqq_vxx95_norm70_h126 | 5 | 1.56 | 0.969 | 99.9% |
| phase03 018 qqq_tqqq_vxx95_norm70_h126 | 10 | 3.8 | 1.9 | 100.0% |
| phase03 018 qqq_tqqq_vxx95_norm70_h126 | 15 | 5.69 | 4.26 | 100.0% |
| phase03 008 top2_m63_dd15_boost125_cap150 | 1 | 1.04 | 0.645 | 64.4% |
| phase03 008 top2_m63_dd15_boost125_cap150 | 3 | 1.17 | 0.632 | 76.9% |
| phase03 008 top2_m63_dd15_boost125_cap150 | 5 | 1.28 | 0.567 | 77.8% |
| phase03 008 top2_m63_dd15_boost125_cap150 | 10 | 1.68 | 0.788 | 86.2% |
| phase03 008 top2_m63_dd15_boost125_cap150 | 15 | 1.85 | 1.08 | 100.0% |
| phase03 001 qld_vt35_rv21_dd25_half | 1 | 1.08 | 0.758 | 68.3% |
| phase03 001 qld_vt35_rv21_dd25_half | 3 | 1.38 | 0.91 | 97.0% |
| phase03 001 qld_vt35_rv21_dd25_half | 5 | 1.61 | 0.985 | 99.7% |
| phase03 001 qld_vt35_rv21_dd25_half | 10 | 2.87 | 1.82 | 100.0% |
| phase03 001 qld_vt35_rv21_dd25_half | 15 | 3.35 | 3.02 | 100.0% |

## Interpretation

The ranking is dominated by high-upside engines: crypto trend/momentum from Phase 1 and LETF/high-beta mechanisms from Phase 3. That is expected because relative terminal wealth rewards convex upside and high beta. It also means the ranking must be read with drawdown and gate failures visible: several high-ranked candidates failed FWD, WF MCPT, PBO or DSR, so they remain research diagnostics only `[leverage_for_the_long_run, p.13]`, `[testing_tuning, p.327-335]`.

## Recommendation

Use this Top 10 as a research shortlist for visual comparison only. Do not paper trade or deploy from this ranking; any future continuation must pre-register a new validation/stress question and keep cumulative trial accounting.
