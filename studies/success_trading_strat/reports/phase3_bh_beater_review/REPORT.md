# Phase 3 Buy-And-Hold Beater Review

## Verdict

Phase 3 closed with no validated strategy: zero `strict_winner`, zero `candidate_watchlist`, zero `paper_trade_candidate` and zero `winner=true`. Seventeen iterations found economic beaters, but every one failed at least one hard validation gate, mainly MCPT and DSR. This is research-only and does not authorize paper/live deployment; mandate capital remains 100% Plano C `[testing_tuning, p.318-320]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Files

- `phase3_summary_table.csv`: one row per Phase 3 iteration.
- `curve_metrics.csv`: recomputed metrics for selected plotted candidates versus aligned SPY.
- `rolling_windows.csv`: rolling 1/3/5/10/15y diagnostics for selected candidates versus SPY.
- `selected_candidate_returns.csv`: selected best-config return series used in plots.
- Plot metrics are recomputed from each iteration's saved `returns.csv`; the canonical economic verdicts remain the per-iteration `RESULTS.json` rows above.
- `plots/selected_equity_log.png`: selected equity curves.
- `plots/selected_drawdowns.png`: selected drawdown curves.
- `plots/selected_relative_vs_spy.png`: selected relative wealth versus SPY.
- `plots/excess_cagr_ranking.png`: excess CAGR ranking.
- `plots/economics_vs_robustness.png`: economics versus gate pass count.
- `plots/gate_fail_counts.png`: strict gate failure counts.
- `plots/status_counts.png`: final status counts.

## Totals

- Iterations: `30`.
- Phase-local strategy trials: `96`.
- Global cumulative trial accounting after Phase 3: `312`.
- Status counts: `{'economic_beater_not_validated': 17, 'fail': 12, 'data_blocked': 1}`.
- Strict winners: `0`.

## Plots

![Selected equity curves](plots/selected_equity_log.png)

![Selected drawdowns](plots/selected_drawdowns.png)

![Relative wealth vs SPY](plots/selected_relative_vs_spy.png)

![Excess CAGR ranking](plots/excess_cagr_ranking.png)

![Economics vs robustness](plots/economics_vs_robustness.png)

![Gate fail counts](plots/gate_fail_counts.png)

## Iteration Table

| iteration | family | status | n_trials | best_config | cagr | benchmark_cagr | excess_cagr | terminal_wealth | benchmark_terminal_wealth | max_drawdown | sharpe | pbo | dsr_p | failed_core_gates |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 001-2026-05-14-nasdaq-letf-vol-target | nasdaq-letf-vol-target | economic_beater_not_validated | 6 | qld_vt35_rv21_dd25_half | 22.12% | 17.16% | 4.96% | 52.01 | 22.9 | -48.14% | 0.8698 | 0.4206 | 0.1472 | is_mcpt;wf_mcpt;dsr |
| 002-2026-05-14-sp500-letf-vol-target | sp500-letf-vol-target | economic_beater_not_validated | 6 | upro_vt40_rv63_dd30_half | 20.54% | 14.57% | 5.97% | 22.19 | 9.557 | -46.48% | 0.7175 | 0.2063 | 0.4551 | is_mcpt;wf_mcpt;dsr;bootstrap |
| 003-2026-05-14-semis-letf-vol-target | semis-letf-vol-target | economic_beater_not_validated | 6 | tecl_vt40_rv63 | 34.00% | 27.89% | 6.11% | 148.1 | 66.76 | -49.24% | 0.9217 | 0.2063 | 0.1636 | is_mcpt;wf_mcpt;dsr |
| 004-2026-05-14-nasdaq-crash-rearm | nasdaq-crash-rearm | economic_beater_not_validated | 6 | qqq_qld_rearm_dd35_sma100_h189 | 18.64% | 16.39% | 2.24% | 27.79 | 19.18 | -62.20% | 0.8309 | 0.2302 | 0.2006 | is_mcpt;wf_mcpt;dsr |
| 005-2026-05-14-sp500-crash-rearm | sp500-crash-rearm | economic_beater_not_validated | 6 | spy_sso_rearm_dd35_sma100_h189 | 13.05% | 11.05% | 2.00% | 10.87 | 7.687 | -55.20% | 0.6912 | 0.7778 | 0.4147 | is_mcpt;wf_mcpt;pbo;dsr;bootstrap |
| 006-2026-05-14-high-beta-relative-rotation | high-beta-relative-rotation | economic_beater_not_validated | 6 | top2_m63 | 15.98% | 15.50% | 0.48% | 37.92 | 34.28 | -59.48% | 0.6804 | 0.3452 | 0.2983 | is_mcpt;wf_mcpt;dsr |
| 007-2026-05-14-crypto-equity-rotation | crypto-equity-rotation | data_blocked | 0 |  |  |  |  |  |  |  |  |  |  |  |
| 008-2026-05-14-drawdown-adaptive-high-beta | drawdown-adaptive-high-beta | economic_beater_not_validated | 4 | top2_m63_dd15_boost125_cap150 | 17.02% | 15.50% | 1.51% | 47.19 | 34.28 | -66.42% | 0.6636 | 0.623 | 0.3293 | is_mcpt;wf_mcpt;pbo;dsr |
| 009-2026-05-14-high-beta-long-short | high-beta-long-short | fail | 4 | ls_m63_top1_bottom1_g100 | -3.77% | 19.18% | -22.94% | 0.4813 | 28.26 | -63.51% | -0.4578 | 0.4325 | 1 | is_mcpt;wf_mcpt;dsr;wf_windows;bootstrap |
| 010-2026-05-14-levered-balanced-sleeve | levered-balanced-sleeve | economic_beater_not_validated | 4 | upro50_tlt25_gld25_quarterly | 24.13% | 18.59% | 5.54% | 38.16 | 17.68 | -44.80% | 1.016 | 0.3571 | 0.09769 | wf_mcpt;dsr |
| 011-2026-05-14-sso-balanced-sleeve-stress | sso-balanced-sleeve-stress | economic_beater_not_validated | 4 | sso75_tlt15_gld10_quarterly | 14.76% | 12.06% | 2.70% | 14.27 | 9.003 | -71.22% | 0.6439 | 0.3889 | 0.5123 | is_mcpt;wf_mcpt;dsr;bootstrap |
| 012-2026-05-14-hfea-levered-sleeve | hfea-levered-sleeve | economic_beater_not_validated | 4 | upro50_tmf30_gld20_quarterly | 24.43% | 18.53% | 5.90% | 39.43 | 17.43 | -58.69% | 0.9957 | 0.0873 | 0.1149 | is_mcpt;wf_mcpt;dsr;fwd_63d |
| 013-2026-05-14-nasdaq-drawdown-rearm-booster | nasdaq-drawdown-rearm-booster | economic_beater_not_validated | 4 | qld_tqqq_dd25_recover_sma50_rv40 | 36.12% | 34.08% | 2.04% | 148.7 | 116.3 | -67.15% | 0.9299 | 0.4603 | 0.1932 | is_mcpt;wf_mcpt;dsr |
| 014-2026-05-14-upro-tlt-gross-spread | upro-tlt-gross-spread | economic_beater_not_validated | 4 | upro125_tlt25_sma200 | 17.76% | 15.33% | 2.43% | 15.7 | 11.05 | -64.92% | 0.5952 | 0.381 | 0.6641 | is_mcpt;wf_mcpt;dsr;bootstrap |
| 015-2026-05-14-letf-light-dual-momentum | letf-light-dual-momentum | fail | 4 | top1_m252_monthly | 13.74% | 16.43% | -2.69% | 12.01 | 18.84 | -59.93% | 0.5627 | 0.8373 | 0.6558 | is_mcpt;wf_mcpt;pbo;dsr;bootstrap |
| 016-2026-05-14-inception-stress-economic-beaters | inception-stress-economic-beaters | fail | 0 |  |  |  |  |  |  |  |  |  |  |  |
| 017-2026-05-14-rolling-window-economic-beaters | rolling-window-economic-beaters | fail | 0 |  |  |  |  |  |  |  |  |  |  |  |
| 018-2026-05-14-vxx-crash-rearm | vxx-crash-rearm | economic_beater_not_validated | 4 | qqq_tqqq_vxx95_norm70_h126 | 28.85% | 19.84% | 9.01% | 61.04 | 18.83 | -35.38% | 1.021 | 0.7897 | 0.1111 | is_mcpt;wf_mcpt;pbo;dsr |
| 019-2026-05-14-letf-light-gross-rotation | letf-light-gross-rotation | economic_beater_not_validated | 4 | top2_m126_g125 | 23.77% | 21.42% | 2.35% | 54.51 | 38.05 | -79.28% | 0.7047 | 0.5913 | 0.4351 | is_mcpt;wf_mcpt;pbo;dsr;bootstrap |
| 020-2026-05-14-dynamic-risk-parity-letf | dynamic-risk-parity-letf | fail | 4 | upro_rp126_g125 | 12.13% | 14.20% | -2.08% | 6.477 | 8.738 | -33.61% | 0.865 | 0 | 0.2752 | is_mcpt;wf_mcpt;dsr;fwd_63d;bootstrap |
| 021-2026-05-14-phase3-consolidation-audit | phase3-consolidation-audit | fail | 0 |  |  |  |  |  |  |  |  |  |  |  |
| 022-2026-05-14-qqq-core-qld-overlay | qqq-core-qld-overlay | economic_beater_not_validated | 4 | mom126_vol63_cap25 | 23.19% | 16.31% | 6.88% | 56.02 | 18.46 | -63.92% | 0.7983 | 0.7381 | 0.2723 | is_mcpt;wf_mcpt;pbo;dsr;bootstrap |
| 023-2026-05-14-semis-leadership-overlay | semis-leadership-overlay | fail | 4 | soxx_qqq_m126_v63_tecl25 | 20.93% | 26.80% | -5.88% | 21.48 | 46.22 | -35.12% | 1.003 | 0.3333 | 0.1319 | wf_mcpt;dsr |
| 024-2026-05-14-qld-migration-sleeve | qld-migration-sleeve | economic_beater_not_validated | 4 | qld70_tlt15_gld15_dd25_boost50 | 23.62% | 16.31% | 7.32% | 59.95 | 18.46 | -80.45% | 0.7382 | 0.1349 | 0.3668 | is_mcpt;wf_mcpt;dsr |
| 025-2026-05-14-economic-beater-financing-stress | economic-beater-financing-stress | fail | 0 |  |  |  |  |  |  |  |  |  |  |  |
| 026-2026-05-14-phase3-gate-consolidation | phase3-gate-consolidation | fail | 0 |  |  |  |  |  |  |  |  |  |  |  |
| 027-2026-05-14-qld-vol-throttle-sleeve | qld-vol-throttle-sleeve | economic_beater_not_validated | 4 | qld70_tlt15_gld15_rv126_q30_70_b50_c20 | 25.34% | 16.28% | 9.07% | 78.26 | 18.37 | -57.17% | 0.8453 | 0.377 | 0.2121 | is_mcpt;wf_mcpt;dsr |
| 028-2026-05-14-qld-vol-throttle-stress | qld-vol-throttle-stress | fail | 0 | qld70_tlt15_gld15_rv126_q30_70_b50_c20 |  |  |  |  |  |  |  |  |  |  |
| 029-2026-05-14-economic-beater-gate-audit | economic-beater-gate-audit | fail | 0 |  |  |  |  |  |  |  |  |  |  |  |
| 030-2026-05-14-phase3-closure-audit | phase3-closure-audit | fail | 0 |  |  |  |  |  |  |  |  |  |  |  |

## Ranking By Excess CAGR

| iteration | best_config | status | cagr | benchmark_label | benchmark_cagr | excess_cagr | terminal_wealth | benchmark_terminal_wealth | failed_core_gates |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 027-2026-05-14-qld-vol-throttle-sleeve | qld70_tlt15_gld15_rv126_q30_70_b50_c20 | economic_beater_not_validated | 25.34% | qqq_bh | 16.28% | 9.07% | 78.26 | 18.37 | is_mcpt;wf_mcpt;dsr |
| 018-2026-05-14-vxx-crash-rearm | qqq_tqqq_vxx95_norm70_h126 | economic_beater_not_validated | 28.85% | qqq_bh | 19.84% | 9.01% | 61.04 | 18.83 | is_mcpt;wf_mcpt;pbo;dsr |
| 024-2026-05-14-qld-migration-sleeve | qld70_tlt15_gld15_dd25_boost50 | economic_beater_not_validated | 23.62% | qqq_bh | 16.31% | 7.32% | 59.95 | 18.46 | is_mcpt;wf_mcpt;dsr |
| 022-2026-05-14-qqq-core-qld-overlay | mom126_vol63_cap25 | economic_beater_not_validated | 23.19% | qqq_bh | 16.31% | 6.88% | 56.02 | 18.46 | is_mcpt;wf_mcpt;pbo;dsr;bootstrap |
| 003-2026-05-14-semis-letf-vol-target | tecl_vt40_rv63 | economic_beater_not_validated | 34.00% | semis_bh | 27.89% | 6.11% | 148.1 | 66.76 | is_mcpt;wf_mcpt;dsr |
| 002-2026-05-14-sp500-letf-vol-target | upro_vt40_rv63_dd30_half | economic_beater_not_validated | 20.54% | spy_bh | 14.57% | 5.97% | 22.19 | 9.557 | is_mcpt;wf_mcpt;dsr;bootstrap |
| 012-2026-05-14-hfea-levered-sleeve | upro50_tmf30_gld20_quarterly | economic_beater_not_validated | 24.43% | ew_bh | 18.53% | 5.90% | 39.43 | 17.43 | is_mcpt;wf_mcpt;dsr;fwd_63d |
| 010-2026-05-14-levered-balanced-sleeve | upro50_tlt25_gld25_quarterly | economic_beater_not_validated | 24.13% | ew_bh | 18.59% | 5.54% | 38.16 | 17.68 | wf_mcpt;dsr |
| 001-2026-05-14-nasdaq-letf-vol-target | qld_vt35_rv21_dd25_half | economic_beater_not_validated | 22.12% | qqq_bh | 17.16% | 4.96% | 52.01 | 22.9 | is_mcpt;wf_mcpt;dsr |
| 011-2026-05-14-sso-balanced-sleeve-stress | sso75_tlt15_gld10_quarterly | economic_beater_not_validated | 14.76% | ew_bh | 12.06% | 2.70% | 14.27 | 9.003 | is_mcpt;wf_mcpt;dsr;bootstrap |

## Ranking By Robustness

| iteration | best_config | status | core_pass_count | core_gate_count | excess_cagr | pbo | dsr_p | failed_core_gates |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 010-2026-05-14-levered-balanced-sleeve | upro50_tlt25_gld25_quarterly | economic_beater_not_validated | 7 | 9 | 5.54% | 0.3571 | 0.09769 | wf_mcpt;dsr |
| 023-2026-05-14-semis-leadership-overlay | soxx_qqq_m126_v63_tecl25 | fail | 7 | 9 | -5.88% | 0.3333 | 0.1319 | wf_mcpt;dsr |
| 027-2026-05-14-qld-vol-throttle-sleeve | qld70_tlt15_gld15_rv126_q30_70_b50_c20 | economic_beater_not_validated | 6 | 9 | 9.07% | 0.377 | 0.2121 | is_mcpt;wf_mcpt;dsr |
| 024-2026-05-14-qld-migration-sleeve | qld70_tlt15_gld15_dd25_boost50 | economic_beater_not_validated | 6 | 9 | 7.32% | 0.1349 | 0.3668 | is_mcpt;wf_mcpt;dsr |
| 003-2026-05-14-semis-letf-vol-target | tecl_vt40_rv63 | economic_beater_not_validated | 6 | 9 | 6.11% | 0.2063 | 0.1636 | is_mcpt;wf_mcpt;dsr |
| 001-2026-05-14-nasdaq-letf-vol-target | qld_vt35_rv21_dd25_half | economic_beater_not_validated | 6 | 9 | 4.96% | 0.4206 | 0.1472 | is_mcpt;wf_mcpt;dsr |
| 004-2026-05-14-nasdaq-crash-rearm | qqq_qld_rearm_dd35_sma100_h189 | economic_beater_not_validated | 6 | 9 | 2.24% | 0.2302 | 0.2006 | is_mcpt;wf_mcpt;dsr |
| 013-2026-05-14-nasdaq-drawdown-rearm-booster | qld_tqqq_dd25_recover_sma50_rv40 | economic_beater_not_validated | 6 | 9 | 2.04% | 0.4603 | 0.1932 | is_mcpt;wf_mcpt;dsr |
| 006-2026-05-14-high-beta-relative-rotation | top2_m63 | economic_beater_not_validated | 6 | 9 | 0.48% | 0.3452 | 0.2983 | is_mcpt;wf_mcpt;dsr |
| 018-2026-05-14-vxx-crash-rearm | qqq_tqqq_vxx95_norm70_h126 | economic_beater_not_validated | 5 | 9 | 9.01% | 0.7897 | 0.1111 | is_mcpt;wf_mcpt;pbo;dsr |

## Status Buckets

- `strict_winner`: none
- `economic_beater_not_validated`: `001 qld_vt35_rv21_dd25_half`, `002 upro_vt40_rv63_dd30_half`, `003 tecl_vt40_rv63`, `004 qqq_qld_rearm_dd35_sma100_h189`, `005 spy_sso_rearm_dd35_sma100_h189`, `006 top2_m63`, `008 top2_m63_dd15_boost125_cap150`, `010 upro50_tlt25_gld25_quarterly`, `011 sso75_tlt15_gld10_quarterly`, `012 upro50_tmf30_gld20_quarterly`, `013 qld_tqqq_dd25_recover_sma50_rv40`, `014 upro125_tlt25_sma200`, `018 qqq_tqqq_vxx95_norm70_h126`, `019 top2_m126_g125`, `022 mom126_vol63_cap25`, `024 qld70_tlt15_gld15_dd25_boost50`, `027 qld70_tlt15_gld15_rv126_q30_70_b50_c20`
- `candidate_watchlist`: none.
- `paper_trade_candidate`: none.
- `fail`: `009 ls_m63_top1_bottom1_g100`, `015 top1_m252_monthly`, `016 inception-stress-economic-beaters`, `017 rolling-window-economic-beaters`, `020 upro_rp126_g125`, `021 phase3-consolidation-audit`, `023 soxx_qqq_m126_v63_tecl25`, `025 economic-beater-financing-stress`, `026 phase3-gate-consolidation`, `028 qld70_tlt15_gld15_rv126_q30_70_b50_c20`, `029 economic-beater-gate-audit`, `030 phase3-closure-audit`
- `data_blocked`: `007 crypto-equity-rotation`

## Beaters That Failed Validation

The economically strongest families were LETF/controlled-leverage sleeves, semiconductor/technology LETF exposure, crash-rearm overlays and high-beta rotation. They beat the aligned B&H benchmark in CAGR and terminal wealth, but none survived the full validation stack. This is exactly the failure mode the Phase 3 spec was designed to expose: leverage can create attractive CAGR, but without MCPT/DSR/PBO robustness it remains a backtest artifact candidate rather than a strategy `[leverage_for_the_long_run, p.13]`, `[leverage_space, p.149-167]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.

Common blockers:

- MCPT failures: the observed result was not sufficiently extreme versus permuted-path nulls `[testing_tuning, p.318-320]`.
- DSR failures: after cumulative trial accounting, Sharpe was not statistically defensible `[advances_fin_ml, p.222-223]`.
- PBO failures in several stress/overlay variants: parameter selection risk remained too high `[advances_fin_ml, p.208-211]`.
- Rolling/inception stress failures: some economic beaters depended on favorable asset-inception windows or specific 3y/5y regimes `[testing_tuning, p.327-335]`.

## No Validated Strategy Passed

No candidate passed the strict combination of economic gates plus IS MCPT, WF MCPT, PBO, DSR, WF windows, OOS, FWD, bootstrap and cross-lib. Therefore Phase 3 cannot justify Phase 4, paper trading or deployment. Under the mandate, any hard-gate failure blocks promotion; there is no `almost passed` override `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Lessons

- Beating B&H requires an upside engine: the best economic results came from embedded leverage and high-beta participation, not defensive long/flat filters `[systematic_trading, p.40]`, `[leverage_for_the_long_run, p.13]`.
- Simple balanced leverage sleeves can be economically strong, especially `UPRO/TLT/GLD`, but their validation failures suggest historical sequencing risk rather than robust edge.
- More local tuning is not justified: the dominant blockers are MCPT/DSR/PBO and rolling stress, not a missing nearby lookback threshold `[testing_tuning, p.327-335]`.
- If future work resumes, it should start from a new pre-registered mechanism or independent data regime, not another Phase 3 local sweep.

## Recommendation

Stop the Phase 3 hunt. Do not open Phase 4 from these results. Do not paper trade any Phase 3 candidate. Keep the project mandate unchanged: no deploy implication and 100% Plano C remains the only active allocation.
