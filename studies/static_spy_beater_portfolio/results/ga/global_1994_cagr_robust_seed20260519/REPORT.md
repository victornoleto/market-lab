# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `global_1994`
- Fitness: `cagr_robust`
- Seed: `20260519`
- Common window: `1994-05-05` to `2026-04-17`
- Unique evaluated portfolios: `1316`
- GA rolling step: `126` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `20` portfolios
- Benchmark rolling step: `1`
- Generations completed: `38` / `40`
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

- Fitness value: `0.084571`
- Weights: `{"GDESIM": 0.1, "QLDSIM": 0.1, "RSSTSIM": 0.1, "TMFSIM": 0.45, "TQQQSIM": 0.25}`
- Effective exposure: `{"cash": -0.18000000000000002, "gold": 0.09000000000000001, "long_treasury": 1.35, "managed_futures": 0.1, "nasdaq_equity": 0.95, "us_large_equity": 0.19}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                          |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:-------------------------------------------------------------------------------------------------|
|      1 |       0.0845714 |    0.202098 |  -0.781969 |      0.761643 |        1.07748 |      0.258448 |                   2.33781 |        -0.360284 | {"GDESIM": 0.1, "QLDSIM": 0.1, "RSSTSIM": 0.1, "TMFSIM": 0.45, "TQQQSIM": 0.25}                  |
|      2 |       0.083366  |    0.211022 |  -0.832524 |      0.790368 |        1.09386 |      0.253472 |                   2.11145 |        -0.244775 | {"GDESIM": 0.05, "QLDSIM": 0.2, "RSSTSIM": 0.2, "TMFSIM": 0.25, "TQQQSIM": 0.2, "UGLSIM": 0.1}   |
|      3 |       0.0825197 |    0.213838 |  -0.862324 |      0.771346 |        1.0598  |      0.247979 |                   2.05934 |        -0.193975 | {"GDESIM": 0.1, "QLDSIM": 0.15, "RSSTSIM": 0.2, "TMFSIM": 0.2, "TQQQSIM": 0.25, "UGLSIM": 0.1}   |
|      4 |       0.0823152 |    0.208709 |  -0.807693 |      0.809527 |        1.11988 |      0.258401 |                   2.04041 |        -0.175447 | {"GDESIM": 0.1, "QLDSIM": 0.15, "RSSTSIM": 0.2, "TMFSIM": 0.2, "TQQQSIM": 0.2, "UGLSIM": 0.15}   |
|      5 |       0.0822956 |    0.207834 |  -0.782557 |      0.823592 |        1.14508 |      0.265583 |                   2.02469 |        -0.224763 | {"GDESIM": 0.1, "QLDSIM": 0.2, "RSSTSIM": 0.25, "TMFSIM": 0.25, "TQQQSIM": 0.15, "UGLSIM": 0.05} |
|      6 |       0.0819091 |    0.202677 |  -0.785117 |      0.776362 |        1.09396 |      0.258148 |                   2.16022 |        -0.340519 | {"GDESIM": 0.05, "QLDSIM": 0.25, "RSSTSIM": 0.15, "TMFSIM": 0.4, "TQQQSIM": 0.15}                |
|      7 |       0.0816402 |    0.211374 |  -0.845379 |      0.782429 |        1.07684 |      0.250035 |                   2.00563 |        -0.189962 | {"GDESIM": 0.1, "QLDSIM": 0.2, "RSSTSIM": 0.2, "TMFSIM": 0.2, "TQQQSIM": 0.2, "UGLSIM": 0.1}     |
|      8 |       0.081583  |    0.206158 |  -0.794078 |      0.795567 |        1.10769 |      0.25962  |                   2.04403 |        -0.285053 | {"GDESIM": 0.1, "QLDSIM": 0.15, "RSSTSIM": 0.2, "TMFSIM": 0.3, "TQQQSIM": 0.2, "VBRSIM": 0.05}   |
|      9 |       0.0814613 |    0.203077 |  -0.820458 |      0.752639 |        1.05548 |      0.247516 |                   2.16769 |        -0.386657 | {"GDESIM": 0.05, "QLDSIM": 0.3, "RSSTSIM": 0.1, "TMFSIM": 0.4, "TQQQSIM": 0.15}                  |
|     10 |       0.0814428 |    0.204796 |  -0.819493 |      0.757891 |        1.06314 |      0.249905 |                   2.16102 |        -0.383233 | {"QLDSIM": 0.3, "RSSTSIM": 0.15, "TMFSIM": 0.4, "TQQQSIM": 0.15}                                 |
|     11 |       0.0812128 |    0.209276 |  -0.810704 |      0.794122 |        1.105   |      0.258141 |                   2.05028 |        -0.291603 | {"GDESIM": 0.05, "QLDSIM": 0.25, "RSSTSIM": 0.25, "TMFSIM": 0.3, "TQQQSIM": 0.15}                |
|     12 |       0.0811489 |    0.213207 |  -0.881859 |      0.746904 |        1.02735 |      0.24177  |                   2.08804 |        -0.273859 | {"GDESIM": 0.1, "QLDSIM": 0.2, "RSSTSIM": 0.15, "TMFSIM": 0.25, "TQQQSIM": 0.25, "UGLSIM": 0.05} |
|     13 |       0.0810586 |    0.208222 |  -0.830573 |      0.767271 |        1.07009 |      0.250697 |                   2.1085  |        -0.352942 | {"QLDSIM": 0.3, "RSSTSIM": 0.2, "TMFSIM": 0.35, "TQQQSIM": 0.15}                                 |
|     14 |       0.0810543 |    0.206547 |  -0.821453 |      0.778349 |        1.08222 |      0.251441 |                   2.06376 |        -0.302865 | {"GDESIM": 0.1, "QLDSIM": 0.1, "RSSTSIM": 0.2, "TMFSIM": 0.3, "TQQQSIM": 0.25, "VWOSIM": 0.05}   |
|     15 |       0.0810153 |    0.20478  |  -0.832823 |      0.756716 |        1.05494 |      0.245887 |                   2.11814 |        -0.360077 | {"GDESIM": 0.1, "QLDSIM": 0.3, "RSSTSIM": 0.1, "TMFSIM": 0.35, "TQQQSIM": 0.15}                  |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   gold |   long_treasury |   managed_futures |   nasdaq_equity |   us_large_equity |
|-------:|----------------:|-------:|-------:|----------------:|------------------:|----------------:|------------------:|
|      1 |       0.0845714 |  -0.18 |  0.09  |            1.35 |              0.1  |            0.95 |             0.19  |
|      2 |       0.083366  |  -0.24 |  0.245 |            0.75 |              0.2  |            1    |             0.245 |
|      3 |       0.0825197 |  -0.28 |  0.29  |            0.6  |              0.2  |            1.05 |             0.29  |
|      4 |       0.0823152 |  -0.28 |  0.39  |            0.6  |              0.2  |            0.9  |             0.29  |
|      5 |       0.0822956 |  -0.33 |  0.19  |            0.75 |              0.25 |            0.85 |             0.34  |

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
