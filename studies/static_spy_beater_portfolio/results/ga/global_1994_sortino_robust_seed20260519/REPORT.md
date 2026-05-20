# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `global_1994`
- Fitness: `sortino_robust`
- Seed: `20260519`
- Common window: `1994-05-05` to `2026-04-17`
- Unique evaluated portfolios: `1393`
- GA rolling step: `126` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `20` portfolios
- Benchmark rolling step: `1`
- Generations completed: `40` / `40`
- Early stop: `False` (`completed_generations`)
- Patience: `8`, min_delta: `1e-06`
- Log every: `5` generations
- Eval log every: `100` unique portfolios
- Fast discovery: `True`
- Jobs: `4`

This is discovery output only. It is not a validated winner or a mandate change.
GA search breadth must be carried into later DSR/PBO accounting
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Best Portfolio

- Fitness value: `1.110873`
- Weights: `{"BNDSIM": 0.25, "CASHX": 0.4, "IEFSIM": 0.1, "KMLMSIM": 0.1, "NTSXSIM": 0.05, "QQQSIM": 0.05, "TLTSIM": 0.05}`
- Effective exposure: `{"aggregate_bond": 0.25, "cash": 0.375, "intermediate_treasury": 0.13, "long_treasury": 0.05, "managed_futures": 0.1, "nasdaq_equity": 0.05, "us_large_equity": 0.045000000000000005}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                                                     |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:----------------------------------------------------------------------------------------------------------------------------|
|      1 |        1.11087  |   0.0518332 | -0.0769109 |       1.55087 |        2.2337  |      0.673939 |                 -0.395165 |        -0.767382 | {"BNDSIM": 0.25, "CASHX": 0.4, "IEFSIM": 0.1, "KMLMSIM": 0.1, "NTSXSIM": 0.05, "QQQSIM": 0.05, "TLTSIM": 0.05}              |
|      2 |        1.091    |   0.0573863 | -0.0826251 |       1.53601 |        2.15243 |      0.694539 |                 -0.358458 |        -0.742949 | {"BNDSIM": 0.25, "CASHX": 0.3, "GLDSIM": 0.05, "IEFSIM": 0.15, "KMLMSIM": 0.1, "NTSXSIM": 0.1, "VTISIM": 0.05}              |
|      3 |        1.09054  |   0.0625288 | -0.0850689 |       1.49457 |        2.138   |      0.735038 |                 -0.325656 |        -0.723372 | {"BNDSIM": 0.15, "CASHX": 0.3, "GLDSIM": 0.1, "IEFSIM": 0.2, "KMLMSIM": 0.1, "NTSXSIM": 0.1, "QQQSIM": 0.05}                |
|      4 |        1.07479  |   0.05645   | -0.0827327 |       1.53103 |        2.12763 |      0.682318 |                 -0.366401 |        -0.74397  | {"BNDSIM": 0.3, "CASHX": 0.35, "GLDSIM": 0.05, "KMLMSIM": 0.1, "NTSXSIM": 0.1, "TLTSIM": 0.05, "VTISIM": 0.05}              |
|      5 |        1.06796  |   0.0614433 | -0.0844614 |       1.49399 |        2.107   |      0.727472 |                 -0.336177 |        -0.724252 | {"BNDSIM": 0.25, "CASHX": 0.35, "GLDSIM": 0.1, "KMLMSIM": 0.1, "NTSXSIM": 0.1, "QQQSIM": 0.05, "TLTSIM": 0.05}              |
|      6 |        1.05788  |   0.0634175 | -0.0933874 |       1.47458 |        2.08793 |      0.679079 |                 -0.317806 |        -0.72101  | {"BNDSIM": 0.25, "CASHX": 0.25, "GLDSIM": 0.1, "IEFSIM": 0.15, "KMLMSIM": 0.1, "NTSXSIM": 0.1, "QQQSIM": 0.05}              |
|      7 |        1.04279  |   0.0624786 | -0.0933876 |       1.46817 |        2.06476 |      0.669024 |                 -0.326357 |        -0.722212 | {"BNDSIM": 0.3, "CASHX": 0.3, "GLDSIM": 0.1, "KMLMSIM": 0.1, "NTSXSIM": 0.1, "QQQSIM": 0.05, "TLTSIM": 0.05}                |
|      8 |        1.03686  |   0.0547173 | -0.0672237 |       1.54696 |        2.14419 |      0.813958 |                 -0.373365 |        -0.756849 | {"BNDSIM": 0.3, "CASHX": 0.35, "GLDSIM": 0.1, "IEFSIM": 0.05, "KMLMSIM": 0.1, "NTSXSIM": 0.1}                               |
|      9 |        1.01778  |   0.0580453 | -0.101947  |       1.42824 |        2.04369 |      0.569368 |                 -0.354344 |        -0.742435 | {"BNDSIM": 0.25, "CASHX": 0.3, "IEFSIM": 0.15, "KMLMSIM": 0.1, "NTSXSIM": 0.1, "QQQSIM": 0.05, "TLTSIM": 0.05}              |
|     10 |        1.00985  |   0.0701294 | -0.0896921 |       1.40664 |        2.01802 |      0.78189  |                 -0.282111 |        -0.693784 | {"BNDSIM": 0.2, "CASHX": 0.2, "GLDSIM": 0.05, "IEFSIM": 0.2, "KMLMSIM": 0.15, "NTSXSIM": 0.1, "QQQSIM": 0.1}                |
|     11 |        1.00377  |   0.0606673 | -0.0879234 |       1.47547 |        2.04486 |      0.690002 |                 -0.33448  |        -0.730866 | {"BNDSIM": 0.3, "CASHX": 0.25, "GLDSIM": 0.1, "IEFSIM": 0.1, "KMLMSIM": 0.1, "NTSXSIM": 0.1, "VTISIM": 0.05}                |
|     12 |        1.00023  |   0.0649701 | -0.0863293 |       1.43916 |        2.06456 |      0.752585 |                 -0.322084 |        -0.716945 | {"BNDSIM": 0.2, "CASHX": 0.3, "IEFSIM": 0.2, "KMLMSIM": 0.1, "NTSXSIM": 0.1, "QQQSIM": 0.05, "RSSTSIM": 0.05}               |
|     13 |        0.992466 |   0.0551239 | -0.0583934 |       1.52013 |        2.1504  |      0.944009 |                 -0.372702 |        -0.763703 | {"BNDSIM": 0.3, "CASHX": 0.3, "GLDSIM": 0.05, "IEFSIM": 0.1, "KMLMSIM": 0.15, "NTSXSIM": 0.1}                               |
|     14 |        0.991081 |   0.0671273 | -0.116647  |       1.35627 |        1.95399 |      0.575474 |                 -0.297686 |        -0.695854 | {"BNDSIM": 0.15, "CASHX": 0.3, "GLDSIM": 0.05, "IEFSIM": 0.1, "KMLMSIM": 0.1, "NTSXSIM": 0.1, "QQQSIM": 0.1, "TLTSIM": 0.1} |
|     15 |        0.987794 |   0.0486311 | -0.100507  |       1.44964 |        2.01812 |      0.483859 |                 -0.404424 |        -0.775391 | {"BNDSIM": 0.3, "CASHX": 0.35, "IEFSIM": 0.2, "KMLMSIM": 0.05, "NTSXSIM": 0.1}                                              |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   aggregate_bond |   cash |   intermediate_treasury |   long_treasury |   managed_futures |   nasdaq_equity |   us_large_equity |   gold |   us_total_equity |
|-------:|----------------:|-----------------:|-------:|------------------------:|----------------:|------------------:|----------------:|------------------:|-------:|------------------:|
|      1 |         1.11087 |             0.25 |  0.375 |                    0.13 |            0.05 |               0.1 |            0.05 |             0.045 |   0    |              0    |
|      2 |         1.091   |             0.25 |  0.25  |                    0.21 |            0    |               0.1 |            0    |             0.09  |   0.05 |              0.05 |
|      3 |         1.09054 |             0.15 |  0.25  |                    0.26 |            0    |               0.1 |            0.05 |             0.09  |   0.1  |              0    |
|      4 |         1.07479 |             0.3  |  0.3   |                    0.06 |            0.05 |               0.1 |            0    |             0.09  |   0.05 |              0.05 |
|      5 |         1.06796 |             0.25 |  0.3   |                    0.06 |            0.05 |               0.1 |            0.05 |             0.09  |   0.1  |              0    |

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
