# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `global_1994`
- Fitness: `relative_wealth_qqq`
- Seed: `20260519`
- Common window: `1994-05-05` to `2026-04-17`
- Unique evaluated portfolios: `1044`
- GA rolling step: `126` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `20` portfolios
- Benchmark rolling step: `1`
- Generations completed: `30` / `40`
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

- Fitness value: `1.367865`
- Weights: `{"QLDSIM": 0.05, "RSSTSIM": 0.1, "TMFSIM": 0.35, "TQQQSIM": 0.35, "UGLSIM": 0.15}`
- Effective exposure: `{"cash": -0.1, "gold": 0.3, "long_treasury": 1.0499999999999998, "managed_futures": 0.1, "nasdaq_equity": 1.15, "us_large_equity": 0.1}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                          |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:-------------------------------------------------------------------------------------------------|
|      1 |         1.36786 |    0.212441 |  -0.858107 |      0.755856 |       1.05369  |      0.24757  |                   2.49924 |        -0.371517 | {"QLDSIM": 0.05, "RSSTSIM": 0.1, "TMFSIM": 0.35, "TQQQSIM": 0.35, "UGLSIM": 0.15}                |
|      2 |         1.35281 |    0.214676 |  -0.862499 |      0.757712 |       1.05432  |      0.248901 |                   2.47434 |        -0.368136 | {"QLDSIM": 0.05, "RSSTSIM": 0.15, "TMFSIM": 0.35, "TQQQSIM": 0.35, "UGLSIM": 0.1}                |
|      3 |         1.33259 |    0.208447 |  -0.802334 |      0.7796   |       1.09864  |      0.259801 |                   2.47512 |        -0.355652 | {"QLDSIM": 0.05, "RSSTSIM": 0.15, "TMFSIM": 0.4, "TQQQSIM": 0.3, "UGLSIM": 0.1}                  |
|      4 |         1.32863 |    0.214041 |  -0.886966 |      0.735196 |       1.01956  |      0.241318 |                   2.43462 |        -0.387814 | {"QLDSIM": 0.1, "RSSTSIM": 0.1, "TMFSIM": 0.35, "TQQQSIM": 0.35, "UGLSIM": 0.1}                  |
|      5 |         1.32113 |    0.209986 |  -0.840609 |      0.764609 |       1.06848  |      0.249802 |                   2.44316 |        -0.359781 | {"QLDSIM": 0.1, "RSSTSIM": 0.1, "TMFSIM": 0.35, "TQQQSIM": 0.3, "UGLSIM": 0.15}                  |
|      6 |         1.30887 |    0.207102 |  -0.802983 |      0.784063 |       1.10322  |      0.257916 |                   2.45169 |        -0.327956 | {"QLDSIM": 0.05, "RSSTSIM": 0.1, "TMFSIM": 0.35, "TQQQSIM": 0.3, "UGLSIM": 0.2}                  |
|      7 |         1.307   |    0.210651 |  -0.904512 |      0.711821 |       0.985786 |      0.232889 |                   2.4234  |        -0.412508 | {"QLDSIM": 0.15, "TMFSIM": 0.35, "TQQQSIM": 0.35, "UGLSIM": 0.15}                                |
|      8 |         1.30362 |    0.212075 |  -0.813435 |      0.791245 |       1.10836  |      0.260715 |                   2.42531 |        -0.331665 | {"QLDSIM": 0.05, "RSSTSIM": 0.2, "TMFSIM": 0.35, "TQQQSIM": 0.3, "UGLSIM": 0.1}                  |
|      9 |         1.30206 |    0.214882 |  -0.891509 |      0.738912 |       1.02125  |      0.241032 |                   2.39026 |        -0.338458 | {"QLDSIM": 0.1, "RSSTSIM": 0.1, "TMFSIM": 0.3, "TQQQSIM": 0.35, "UGLSIM": 0.15}                  |
|     10 |         1.29496 |    0.211915 |  -0.872694 |      0.743287 |       1.03263  |      0.242829 |                   2.38443 |        -0.381083 | {"QLDSIM": 0.15, "RSSTSIM": 0.1, "TMFSIM": 0.35, "TQQQSIM": 0.3, "UGLSIM": 0.1}                  |
|     11 |         1.28783 |    0.213184 |  -0.851586 |      0.771892 |       1.07208  |      0.250337 |                   2.35819 |        -0.312149 | {"QLDSIM": 0.1, "RSSTSIM": 0.15, "TMFSIM": 0.3, "TQQQSIM": 0.3, "UGLSIM": 0.15}                  |
|     12 |         1.28661 |    0.2101   |  -0.858024 |      0.752341 |       1.04769  |      0.244865 |                   2.37726 |        -0.373267 | {"GLDSIM": 0.05, "QLDSIM": 0.05, "RSSTSIM": 0.1, "TMFSIM": 0.35, "TQQQSIM": 0.35, "UGLSIM": 0.1} |
|     13 |         1.28454 |    0.206059 |  -0.81588  |      0.76479  |       1.07593  |      0.25256  |                   2.40006 |        -0.374189 | {"QLDSIM": 0.15, "RSSTSIM": 0.1, "TMFSIM": 0.4, "TQQQSIM": 0.25, "UGLSIM": 0.1}                  |
|     14 |         1.27922 |    0.213035 |  -0.820654 |      0.797661 |       1.11215  |      0.259592 |                   2.38808 |        -0.291024 | {"QLDSIM": 0.05, "RSSTSIM": 0.2, "TMFSIM": 0.3, "TQQQSIM": 0.3, "UGLSIM": 0.15}                  |
|     15 |         1.2768  |    0.205525 |  -0.779963 |      0.78842  |       1.11443  |      0.263506 |                   2.38429 |        -0.327552 | {"QLDSIM": 0.1, "RSSTSIM": 0.15, "TMFSIM": 0.4, "TQQQSIM": 0.25, "UGLSIM": 0.1}                  |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   gold |   long_treasury |   managed_futures |   nasdaq_equity |   us_large_equity |
|-------:|----------------:|-------:|-------:|----------------:|------------------:|----------------:|------------------:|
|      1 |         1.36786 |  -0.1  |    0.3 |            1.05 |              0.1  |            1.15 |              0.1  |
|      2 |         1.35281 |  -0.15 |    0.2 |            1.05 |              0.15 |            1.15 |              0.15 |
|      3 |         1.33259 |  -0.15 |    0.2 |            1.2  |              0.15 |            1    |              0.15 |
|      4 |         1.32863 |  -0.1  |    0.2 |            1.05 |              0.1  |            1.25 |              0.1  |
|      5 |         1.32113 |  -0.1  |    0.3 |            1.05 |              0.1  |            1.1  |              0.1  |

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
