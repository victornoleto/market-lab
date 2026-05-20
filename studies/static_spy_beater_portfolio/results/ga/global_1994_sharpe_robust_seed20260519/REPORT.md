# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `global_1994`
- Fitness: `sharpe_robust`
- Seed: `20260519`
- Common window: `1994-05-05` to `2026-04-17`
- Unique evaluated portfolios: `548`
- GA rolling step: `126` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `20` portfolios
- Benchmark rolling step: `1`
- Generations completed: `15` / `40`
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

- Fitness value: `0.505728`
- Weights: `{"BNDSIM": 0.2, "CASHX": 0.15, "GDESIM": 0.1, "GLDSIM": 0.05, "IEFSIM": 0.2, "KMLMSIM": 0.1, "QLDSIM": 0.05, "RSSTSIM": 0.1, "ZROZSIM": 0.05}`
- Effective exposure: `{"aggregate_bond": 0.2, "cash": -0.030000000000000027, "gold": 0.14, "intermediate_treasury": 0.2, "managed_futures": 0.2, "nasdaq_equity": 0.1, "us_large_equity": 0.19, "zero_coupon_treasury": 0.05}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                                                                                        |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 |        0.505728 |   0.0900177 |  -0.134597 |       1.24729 |        1.77587 |      0.668796 |                -0.119592  |        -0.594801 | {"BNDSIM": 0.2, "CASHX": 0.15, "GDESIM": 0.1, "GLDSIM": 0.05, "IEFSIM": 0.2, "KMLMSIM": 0.1, "QLDSIM": 0.05, "RSSTSIM": 0.1, "ZROZSIM": 0.05}                  |
|      2 |        0.502895 |   0.0713897 |  -0.125645 |       1.26416 |        1.7894  |      0.568187 |                -0.250298  |        -0.691013 | {"BNDSIM": 0.2, "CASHX": 0.15, "GDESIM": 0.1, "IEFSIM": 0.2, "KMLMSIM": 0.15, "NTSXSIM": 0.05, "RSSBSIM": 0.1, "TLTSIM": 0.05}                                 |
|      3 |        0.500339 |   0.0768709 |  -0.134336 |       1.26476 |        1.76858 |      0.572228 |                -0.220696  |        -0.658578 | {"BNDSIM": 0.2, "CASHX": 0.15, "GLDSIM": 0.1, "IEFSIM": 0.15, "KMLMSIM": 0.1, "NTSXSIM": 0.15, "RSSBSIM": 0.1, "RSSTSIM": 0.05}                                |
|      4 |        0.496325 |   0.0828289 |  -0.108139 |       1.2917  |        1.84638 |      0.765949 |                -0.177639  |        -0.656782 | {"BNDSIM": 0.2, "CASHX": 0.15, "GDESIM": 0.1, "IEFSIM": 0.25, "KMLMSIM": 0.1, "RSSTSIM": 0.15, "ZROZSIM": 0.05}                                                |
|      5 |        0.492397 |   0.080769  |  -0.120811 |       1.27121 |        1.76154 |      0.668556 |                -0.187896  |        -0.647589 | {"BNDSIM": 0.15, "CASHX": 0.1, "GLDSIM": 0.1, "IEFSIM": 0.1, "KMLMSIM": 0.15, "RSSBSIM": 0.05, "RSSTSIM": 0.05, "SPYSIM": 0.1, "TLTSIM": 0.1, "VBRSIM": 0.1}   |
|      6 |        0.487123 |   0.0691953 |  -0.155791 |       1.21356 |        1.69867 |      0.444155 |                -0.266074  |        -0.702292 | {"BNDSIM": 0.3, "CASHX": 0.15, "IEFSIM": 0.25, "NTSXSIM": 0.1, "RSSTSIM": 0.1, "VXUSSIM": 0.05, "ZROZSIM": 0.05}                                               |
|      7 |        0.479872 |   0.093879  |  -0.173058 |       1.21466 |        1.71515 |      0.542471 |                -0.0976735 |        -0.551314 | {"BNDSIM": 0.1, "CASHX": 0.1, "GDESIM": 0.05, "GLDSIM": 0.1, "IEFSIM": 0.15, "KMLMSIM": 0.1, "QQQSIM": 0.1, "RSSTSIM": 0.1, "SPYSIM": 0.1, "TLTSIM": 0.1}      |
|      8 |        0.47923  |   0.0875878 |  -0.12612  |       1.26661 |        1.78607 |      0.694478 |                -0.151195  |        -0.611102 | {"BNDSIM": 0.1, "CASHX": 0.15, "GDESIM": 0.05, "GLDSIM": 0.1, "IEFSIM": 0.15, "KMLMSIM": 0.1, "RSSTSIM": 0.15, "SPYSIM": 0.1, "TLTSIM": 0.1}                   |
|      9 |        0.479188 |   0.0805477 |  -0.146316 |       1.26713 |        1.76063 |      0.550504 |                -0.200795  |        -0.651091 | {"BNDSIM": 0.2, "CASHX": 0.1, "GLDSIM": 0.1, "IEFSIM": 0.15, "KMLMSIM": 0.1, "RSSTSIM": 0.1, "SPYSIM": 0.15, "TLTSIM": 0.05, "VWOSIM": 0.05}                   |
|     10 |        0.478731 |   0.0935625 |  -0.159204 |       1.20777 |        1.70647 |      0.587688 |                -0.0934045 |        -0.562832 | {"BNDSIM": 0.25, "CASHX": 0.15, "GDESIM": 0.15, "IEFSIM": 0.15, "KMLMSIM": 0.1, "QLDSIM": 0.05, "RSSTSIM": 0.1, "ZROZSIM": 0.05}                               |
|     11 |        0.476821 |   0.0844985 |  -0.13006  |       1.26735 |        1.78813 |      0.649688 |                -0.176774  |        -0.632102 | {"BNDSIM": 0.15, "CASHX": 0.15, "GLDSIM": 0.1, "IEFSIM": 0.1, "KMLMSIM": 0.1, "RSSBSIM": 0.05, "RSSTSIM": 0.15, "SPYSIM": 0.1, "TLTSIM": 0.1}                  |
|     12 |        0.474282 |   0.0948828 |  -0.183539 |       1.22648 |        1.73349 |      0.516962 |                -0.101522  |        -0.558177 | {"BNDSIM": 0.15, "CASHX": 0.1, "GLDSIM": 0.1, "IEFSIM": 0.1, "KMLMSIM": 0.1, "QQQSIM": 0.1, "RSSTSIM": 0.15, "SPYSIM": 0.1, "TLTSIM": 0.1}                     |
|     13 |        0.473235 |   0.0737037 |  -0.139435 |       1.20768 |        1.70369 |      0.528588 |                -0.240138  |        -0.659783 | {"BNDSIM": 0.15, "CASHX": 0.2, "GLDSIM": 0.1, "IEFSIM": 0.1, "KMLMSIM": 0.1, "NTSXSIM": 0.1, "RSSBSIM": 0.1, "SPYSIM": 0.1, "ZROZSIM": 0.05}                   |
|     14 |        0.473005 |   0.0934998 |  -0.170563 |       1.19515 |        1.69925 |      0.548183 |                -0.0941695 |        -0.559402 | {"BNDSIM": 0.2, "CASHX": 0.05, "GLDSIM": 0.1, "IEFSIM": 0.15, "KMLMSIM": 0.1, "QLDSIM": 0.05, "RSSTSIM": 0.1, "SPYSIM": 0.15, "TLTSIM": 0.05, "ZROZSIM": 0.05} |
|     15 |        0.470389 |   0.0821003 |  -0.127823 |       1.23414 |        1.75479 |      0.642296 |                -0.182365  |        -0.640911 | {"BNDSIM": 0.15, "CASHX": 0.15, "GLDSIM": 0.1, "IEFSIM": 0.1, "KMLMSIM": 0.1, "RSSTSIM": 0.1, "SPYSIM": 0.1, "VTSIM": 0.1, "ZROZSIM": 0.1}                     |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   aggregate_bond |   cash |   gold |   intermediate_treasury |   managed_futures |   nasdaq_equity |   us_large_equity |   zero_coupon_treasury |   global_equity |   long_treasury |   us_small_value_equity |
|-------:|----------------:|-----------------:|-------:|-------:|------------------------:|------------------:|----------------:|------------------:|-----------------------:|----------------:|----------------:|------------------------:|
|      1 |        0.505728 |              0.2 | -0.03  |   0.14 |                    0.2  |              0.2  |             0.1 |             0.19  |                   0.05 |            0    |            0    |                     0   |
|      2 |        0.502895 |              0.3 | -0.055 |   0.09 |                    0.23 |              0.15 |             0   |             0.135 |                   0    |            0.1  |            0.05 |                     0   |
|      3 |        0.500339 |              0.3 | -0.075 |   0.1  |                    0.24 |              0.15 |             0   |             0.185 |                   0    |            0.1  |            0    |                     0   |
|      4 |        0.496325 |              0.2 | -0.08  |   0.09 |                    0.25 |              0.25 |             0   |             0.24  |                   0.05 |            0    |            0    |                     0   |
|      5 |        0.492397 |              0.2 |  0     |   0.1  |                    0.1  |              0.2  |             0   |             0.15  |                   0    |            0.05 |            0.1  |                     0.1 |

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
