# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `global_1994`
- Fitness: `min_regret`
- Seed: `20260519`
- Common window: `1994-05-05` to `2026-04-17`
- Unique evaluated portfolios: `582`
- GA rolling step: `126` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `20` portfolios
- Benchmark rolling step: `1`
- Generations completed: `16` / `40`
- Early stop: `True` (`no_improvement_for_8_generations`)
- Patience: `8`, min_delta: `1e-06`
- Log every: `5` generations
- Eval log every: `100` unique portfolios
- Fast discovery: `True`
- Jobs: `4`

This is discovery output only. It is not a validated winner or a mandate change.
GA search breadth must be carried into later DSR/PBO accounting
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Best Portfolio

- Fitness value: `-0.012578`
- Weights: `{"BNDSIM": 0.05, "NTSXSIM": 0.15, "RSSTSIM": 0.1, "SPYSIM": 0.4, "SSOSIM": 0.15, "VTISIM": 0.05, "VTSIM": 0.05, "VWOSIM": 0.05}`
- Effective exposure: `{"aggregate_bond": 0.05, "cash": -0.175, "em_equity": 0.05, "global_equity": 0.05, "intermediate_treasury": 0.09, "managed_futures": 0.1, "us_large_equity": 0.9349999999999999, "us_total_equity": 0.05}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                                                                                            |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 |      -0.012578  |    0.122634 |  -0.56103  |      0.685506 |       0.882504 |      0.218587 |                  0.126635 |       -0.012578  | {"BNDSIM": 0.05, "NTSXSIM": 0.15, "RSSTSIM": 0.1, "SPYSIM": 0.4, "SSOSIM": 0.15, "VTISIM": 0.05, "VTSIM": 0.05, "VWOSIM": 0.05}                                    |
|      2 |      -0.014466  |    0.140024 |  -0.541225 |      0.742506 |       0.969462 |      0.258717 |                  0.313319 |       -0.014466  | {"GDESIM": 0.05, "NTSXSIM": 0.2, "QQQSIM": 0.05, "RSSTSIM": 0.2, "SPYSIM": 0.15, "SSOSIM": 0.15, "VEASIM": 0.05, "VTISIM": 0.15}                                   |
|      3 |      -0.0148722 |    0.13055  |  -0.546485 |      0.719577 |       0.932006 |      0.23889  |                  0.220837 |       -0.0148722 | {"EFVSIM": 0.05, "GDESIM": 0.1, "NTSXSIM": 0.15, "QQQSIM": 0.05, "RSSTSIM": 0.1, "SPYSIM": 0.4, "SSOSIM": 0.1, "VTSIM": 0.05}                                      |
|      4 |      -0.0150843 |    0.135093 |  -0.563549 |      0.709396 |       0.922276 |      0.239718 |                  0.224458 |       -0.0150843 | {"EFVSIM": 0.05, "NTSXSIM": 0.15, "QLDSIM": 0.05, "RSSTSIM": 0.15, "SPYSIM": 0.5, "SSOSIM": 0.1}                                                                   |
|      5 |      -0.0151439 |    0.134962 |  -0.532502 |      0.74645  |       0.96883  |      0.253449 |                  0.300224 |       -0.0151439 | {"GDESIM": 0.1, "NTSESIM": 0.05, "NTSXSIM": 0.15, "QQQSIM": 0.05, "RSSTSIM": 0.15, "SPYSIM": 0.15, "SSOSIM": 0.1, "VBRSIM": 0.05, "VTISIM": 0.15, "VXUSSIM": 0.05} |
|      6 |      -0.016154  |    0.130681 |  -0.539042 |      0.719963 |       0.937718 |      0.242432 |                  0.197119 |       -0.016154  | {"NTSXSIM": 0.2, "QQQSIM": 0.1, "RSSTSIM": 0.15, "SPYSIM": 0.35, "SSOSIM": 0.1, "VEASIM": 0.05, "VXUSSIM": 0.05}                                                   |
|      7 |      -0.0166608 |    0.148311 |  -0.548671 |      0.752176 |       0.986429 |      0.270309 |                  0.393697 |       -0.0166608 | {"GDESIM": 0.05, "NTSXSIM": 0.2, "QQQSIM": 0.05, "RSSTSIM": 0.25, "SPYSIM": 0.15, "SSOSIM": 0.1, "UPROSIM": 0.05, "VTISIM": 0.15}                                  |
|      8 |      -0.0169201 |    0.135317 |  -0.521852 |      0.750981 |       0.980151 |      0.259301 |                  0.263678 |       -0.0169201 | {"GDESIM": 0.05, "NTSXSIM": 0.2, "QQQSIM": 0.05, "RSSTSIM": 0.2, "SPYSIM": 0.15, "SSOSIM": 0.1, "VEASIM": 0.1, "VTISIM": 0.15}                                     |
|      9 |      -0.0172691 |    0.139037 |  -0.551144 |      0.736167 |       0.96101  |      0.252269 |                  0.307367 |       -0.0172691 | {"BNDSIM": 0.1, "EFVSIM": 0.05, "GDESIM": 0.05, "NTSXSIM": 0.05, "QLDSIM": 0.1, "RSSTSIM": 0.15, "SPYSIM": 0.3, "SSOSIM": 0.1, "VBRSIM": 0.1}                      |
|     10 |      -0.0175728 |    0.140761 |  -0.552998 |      0.734992 |       0.958792 |      0.254542 |                  0.325711 |       -0.0175728 | {"EFVSIM": 0.05, "GDESIM": 0.1, "NTSXSIM": 0.15, "QQQSIM": 0.1, "RSSTSIM": 0.15, "SPYSIM": 0.3, "SSOSIM": 0.15}                                                    |
|     11 |      -0.017637  |    0.138379 |  -0.558626 |      0.721096 |       0.94057  |      0.247713 |                  0.252712 |       -0.017637  | {"NTSXSIM": 0.1, "QLDSIM": 0.05, "RSSTSIM": 0.2, "SPYSIM": 0.45, "SSOSIM": 0.1, "VEASIM": 0.05, "VTISIM": 0.05}                                                    |
|     12 |      -0.0177135 |    0.128936 |  -0.526073 |      0.735118 |       0.961503 |      0.24509  |                  0.216063 |       -0.0177135 | {"BNDSIM": 0.05, "IEFSIM": 0.1, "NTSXSIM": 0.15, "QQQSIM": 0.05, "RSSTSIM": 0.1, "SPYSIM": 0.2, "SSOSIM": 0.25, "UGLSIM": 0.05, "VTSIM": 0.05}                     |
|     13 |      -0.0181827 |    0.147407 |  -0.554455 |      0.745616 |       0.975576 |      0.265859 |                  0.408157 |       -0.0181827 | {"GDESIM": 0.1, "NTSXSIM": 0.2, "QQQSIM": 0.05, "RSSTSIM": 0.2, "SPYSIM": 0.15, "SSOSIM": 0.2, "VTISIM": 0.1}                                                      |
|     14 |      -0.0185281 |    0.144581 |  -0.541846 |      0.752548 |       0.989421 |      0.26683  |                  0.360983 |       -0.0185281 | {"GDESIM": 0.05, "IEFSIM": 0.05, "NTSXSIM": 0.2, "QQQSIM": 0.1, "RSSTSIM": 0.2, "SPYSIM": 0.2, "SSOSIM": 0.2}                                                      |
|     15 |      -0.0203173 |    0.13191  |  -0.527598 |      0.747569 |       0.979172 |      0.250021 |                  0.227837 |       -0.0203173 | {"GLDSIM": 0.1, "NTSXSIM": 0.1, "QQQSIM": 0.15, "RSSTSIM": 0.1, "SPYSIM": 0.45, "SSOSIM": 0.1}                                                                     |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   aggregate_bond |   cash |   em_equity |   global_equity |   intermediate_treasury |   managed_futures |   us_large_equity |   us_total_equity |   gold |   intl_developed_equity |   nasdaq_equity |   intl_value_equity |   intl_equity |   us_small_value_equity |
|-------:|----------------:|-----------------:|-------:|------------:|----------------:|------------------------:|------------------:|------------------:|------------------:|-------:|------------------------:|----------------:|--------------------:|--------------:|------------------------:|
|      1 |      -0.012578  |             0.05 | -0.175 |       0.05  |            0.05 |                    0.09 |              0.1  |             0.935 |              0.05 |  0     |                    0    |            0    |                0    |          0    |                    0    |
|      2 |      -0.014466  |             0    | -0.34  |       0     |            0    |                    0.12 |              0.2  |             0.875 |              0.15 |  0.045 |                    0.05 |            0.05 |                0    |          0    |                    0    |
|      3 |      -0.0148722 |             0    | -0.255 |       0     |            0.05 |                    0.09 |              0.1  |             0.925 |              0    |  0.09  |                    0    |            0.05 |                0.05 |          0    |                    0    |
|      4 |      -0.0150843 |             0    | -0.225 |       0     |            0    |                    0.09 |              0.15 |             0.985 |              0    |  0     |                    0    |            0.1  |                0.05 |          0    |                    0    |
|      5 |      -0.0151439 |             0    | -0.33  |       0.045 |            0    |                    0.12 |              0.15 |             0.725 |              0.15 |  0.09  |                    0    |            0.05 |                0    |          0.05 |                    0.05 |

## Benchmark Portfolios

| benchmark    |     cagr |       mdd |   sharpe |   sortino |   calmar |   terminal_wealth |
|:-------------|---------:|----------:|---------:|----------:|---------:|------------------:|
| b4           | 0.141737 | -0.279216 | 1.0018   |  1.41761  | 0.507624 |           68.7203 |
| equal_weight | 0.123222 | -0.480969 | 0.796465 |  1.07507  | 0.256195 |           40.7841 |
| qqq_buy_hold | 0.148917 | -0.829711 | 0.650464 |  0.868598 | 0.179481 |           83.941  |
| spy_buy_hold | 0.11073  | -0.551413 | 0.651112 |  0.832993 | 0.200812 |           28.5427 |

## Pareto Plots

- `plots/full_cagr_vs_full_mdd.png`
- `plots/full_cagr_vs_full_sharpe.png`
- `plots/full_cagr_vs_full_calmar.png`
- `plots/fit_relative_wealth_spy_vs_full_mdd.png`
- `plots/fit_relative_wealth_qqq_vs_full_mdd.png`
- `plots/fit_short_window_vs_fit_long_window.png`

## Notes

- `full_mdd` is less negative when better, so Pareto plots maximize it.
- If `finalist_exact > 0`, `top.csv` and this report use the exact re-rank with all possible rolling windows.
- `top_sampled.csv` preserves the faster GA discovery ranking.
- If fast discovery was enabled, sampled GA rankings skipped rolling MDD/Calmar (set to NaN, not zero, so the weighted fitness ignores them honestly) and should only be used as search traces.
- Relative wealth scores are rolling-window aggregate ratios minus 1 versus the named benchmark.
- The rolling score combines mean, median and p10 to penalize bad-regime fragility.
- Only `balanced_spy_beater`, `balanced_dual_beater`, `relative_wealth_*` and `min_regret` are CASHX-proof. The simple `*_robust` families are raw clipped spreads and can be maximized by defensive/cash-like portfolios `[testing_tuning, p.327-335]`.
