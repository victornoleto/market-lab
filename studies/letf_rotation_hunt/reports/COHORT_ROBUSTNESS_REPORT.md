# LETF Cohort Robustness — Top-3 Swing Strategies

_Generated 2026-05-11T01:11:19.632143+00:00_

Spec: pre-publication agent spec removed from the public tree.

## 1. Cohort entry-date analysis (worst + control)

Per-cohort plots in `cohort_robustness/cohort_<NN>_<date>.png` (8 PNGs).

**Forward 5y CAGR by cohort × config:**

|                                                                         |   SPY |   qld_voteK2_sma250_100_vol21_40_ar30_off_zroz |   qld_vote_k2_off_zroz |   tqqq_voteK2_off_zroz |
|:------------------------------------------------------------------------|------:|-----------------------------------------------:|-----------------------:|-----------------------:|
| ('01', '1987-08-25', 'S&P 500 ATH before Black Monday', 'worst')        |  7.6% |                                          24.3% |                  25.6% |                  31.2% |
| ('02', '2000-03-24', 'NDX dotcom peak', 'worst')                        | -3.7% |                                          -1.5% |                 -12.7% |                 -11.9% |
| ('03', '2007-10-09', 'S&P 500 GFC peak', 'worst')                       |  0.6% |                                          15.4% |                  20.4% |                  32.0% |
| ('04', '2020-02-19', 'S&P 500 COVID peak', 'worst')                     | 14.5% |                                          21.7% |                  18.2% |                  15.4% |
| ('05', '2021-12-27', 'S&P 500 ATH before 2022 rate cycle', 'worst')     | 11.3% |                                           8.2% |                   5.4% |                  11.2% |
| ('06', '2003-03-11', 'S&P 500 dotcom trough (recovery)', 'control')     | 12.6% |                                          10.1% |                  10.8% |                   4.9% |
| ('07', '2009-03-09', 'S&P 500 GFC trough (recovery)', 'control')        | 25.3% |                                          33.5% |                  41.0% |                  65.5% |
| ('08', '2022-10-12', 'S&P 500 2022 rates trough (recovery)', 'control') | 23.4% |                                          41.9% |                  32.9% |                  48.3% |

**Time to beat SPY (days from entry):**

|                      |   qld_voteK2_sma250_100_vol21_40_ar30_off_zroz |   qld_vote_k2_off_zroz |   tqqq_voteK2_off_zroz |
|:---------------------|-----------------------------------------------:|-----------------------:|-----------------------:|
| ('01', '1987-08-25') |                                             16 |                     16 |                      6 |
| ('02', '2000-03-24') |                                            838 |                   3136 |                   1263 |
| ('03', '2007-10-09') |                                              3 |                      3 |                      3 |
| ('04', '2020-02-19') |                                             19 |                     19 |                     33 |
| ('05', '2021-12-27') |                                           1075 |                     25 |                   1401 |
| ('06', '2003-03-11') |                                            118 |                      7 |                      6 |
| ('07', '2009-03-09') |                                            927 |                    535 |                    437 |
| ('08', '2022-10-12') |                                             56 |                     56 |                     56 |

## 2. Regime-stratified entry analysis

![Regime violin](cohort_robustness/regime_stratified_violin.png)

| regime     | config_name                                  |   n |   median_sharpe |   p10_sharpe |   p90_sharpe |   pct_beat_spy |
|:-----------|:---------------------------------------------|----:|----------------:|-------------:|-------------:|---------------:|
| All-on     | qld_voteK2_sma250_100_vol21_40_ar30_off_zroz | 113 |           0.936 |        0.510 |        1.244 |          0.956 |
| All-on     | qld_vote_k2_off_zroz                         | 113 |           0.868 |        0.479 |        1.261 |          0.947 |
| All-on     | tqqq_voteK2_off_zroz                         | 113 |           0.804 |        0.378 |        1.150 |          0.850 |
| Borderline | qld_voteK2_sma250_100_vol21_40_ar30_off_zroz |  84 |           0.882 |        0.512 |        1.253 |          0.964 |
| Borderline | qld_vote_k2_off_zroz                         |  84 |           0.866 |        0.483 |        1.281 |          0.905 |
| Borderline | tqqq_voteK2_off_zroz                         |  84 |           0.766 |        0.343 |        1.261 |          0.869 |
| Mostly-on  | qld_voteK2_sma250_100_vol21_40_ar30_off_zroz | 173 |           0.822 |        0.416 |        1.233 |          0.925 |
| Mostly-on  | qld_vote_k2_off_zroz                         | 173 |           0.791 |        0.404 |        1.316 |          0.884 |
| Mostly-on  | tqqq_voteK2_off_zroz                         | 173 |           0.753 |        0.360 |        1.157 |          0.832 |
| Risk-off   | qld_voteK2_sma250_100_vol21_40_ar30_off_zroz |  56 |           0.726 |        0.553 |        1.171 |          0.982 |
| Risk-off   | qld_vote_k2_off_zroz                         |  56 |           0.675 |        0.496 |        1.183 |          0.964 |
| Risk-off   | tqqq_voteK2_off_zroz                         |  56 |           0.525 |        0.282 |        1.295 |          0.875 |

## 3. Forward-N-year Sharpe heatmap

![qld_vote_k2_off_zroz](cohort_robustness/heatmap_qld_vote_k2_off_zroz.png)

![qld_voteK2_sma250_100_vol21_40_ar30_off_zroz](cohort_robustness/heatmap_qld_voteK2_sma250_100_vol21_40_ar30_off_zroz.png)

![tqqq_voteK2_off_zroz](cohort_robustness/heatmap_tqqq_voteK2_off_zroz.png)

## 4. Synthesis

Path-dependence empirical findings — auto-generated. Cross-reference cohort table for individual entry dates and regime table for aggregate behavior across all monthly entries.

## Citations

- `[advances_fin_ml, p.31-34, p.222-223]` — multi-window backtest validation.
- `[leverage_for_the_long_run, p.16, p.21]` — LETF path-dependence.
- `[trading_systems_methods, ch.21]` — regime sensitivity testing.
- Parent study protocol: `README.md`, `BASE_MEMORY.md` and `KILL_RULES.md`.