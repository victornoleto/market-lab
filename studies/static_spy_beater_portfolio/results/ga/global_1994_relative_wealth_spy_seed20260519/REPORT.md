# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `global_1994`
- Fitness: `relative_wealth_spy`
- Seed: `20260519`
- Common window: `1994-05-05` to `2026-04-17`
- Unique evaluated portfolios: `1132`
- GA rolling step: `126` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `20` portfolios
- Benchmark rolling step: `1`
- Generations completed: `33` / `40`
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

- Fitness value: `2.612816`
- Weights: `{"RSSTSIM": 0.1, "TMFSIM": 0.45, "TQQQSIM": 0.4, "UGLSIM": 0.05}`
- Effective exposure: `{"cash": -0.1, "gold": 0.1, "long_treasury": 1.35, "managed_futures": 0.1, "nasdaq_equity": 1.2000000000000002, "us_large_equity": 0.1}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                          |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:-------------------------------------------------------------------------------------------------|
|      1 |         2.61282 |    0.211665 |  -0.863819 |      0.731267 |       1.02441  |      0.245034 |                   2.61282 |        -0.45364  | {"RSSTSIM": 0.1, "TMFSIM": 0.45, "TQQQSIM": 0.4, "UGLSIM": 0.05}                                 |
|      2 |         2.6009  |    0.204609 |  -0.806973 |      0.752247 |       1.06482  |      0.253551 |                   2.6009  |        -0.384499 | {"RSSTSIM": 0.05, "TMFSIM": 0.45, "TQQQSIM": 0.35, "UGLSIM": 0.15}                               |
|      3 |         2.55984 |    0.214727 |  -0.873835 |      0.747474 |       1.03955  |      0.245729 |                   2.55984 |        -0.377864 | {"RSSTSIM": 0.1, "TMFSIM": 0.35, "TQQQSIM": 0.4, "UGLSIM": 0.15}                                 |
|      4 |         2.55157 |    0.211204 |  -0.822633 |      0.771016 |       1.08345  |      0.256741 |                   2.55157 |        -0.378894 | {"RSSTSIM": 0.15, "TMFSIM": 0.4, "TQQQSIM": 0.35, "UGLSIM": 0.1}                                 |
|      5 |         2.52961 |    0.216914 |  -0.877778 |      0.749148 |       1.04028  |      0.247117 |                   2.52961 |        -0.375054 | {"RSSTSIM": 0.15, "TMFSIM": 0.35, "TQQQSIM": 0.4, "UGLSIM": 0.1}                                 |
|      6 |         2.52769 |    0.217776 |  -0.911221 |      0.720133 |       0.995162 |      0.238993 |                   2.52769 |        -0.400711 | {"RSSTSIM": 0.1, "TMFSIM": 0.35, "TQQQSIM": 0.45, "UGLSIM": 0.1}                                 |
|      7 |         2.52563 |    0.206609 |  -0.895417 |      0.693517 |       0.968961 |      0.230741 |                   2.52563 |        -0.508193 | {"TMFSIM": 0.45, "TQQQSIM": 0.45, "UGLSIM": 0.05, "ZROZSIM": 0.05}                               |
|      8 |         2.50856 |    0.213228 |  -0.827591 |      0.771408 |       1.08228  |      0.257649 |                   2.50856 |        -0.381707 | {"RSSTSIM": 0.2, "TMFSIM": 0.4, "TQQQSIM": 0.35, "UGLSIM": 0.05}                                 |
|      9 |         2.50853 |    0.21476  |  -0.833553 |      0.781374 |       1.09162  |      0.257645 |                   2.50853 |        -0.34325  | {"RSSTSIM": 0.2, "TMFSIM": 0.35, "TQQQSIM": 0.35, "UGLSIM": 0.1}                                 |
|     10 |         2.47735 |    0.210573 |  -0.902613 |      0.703646 |       0.978136 |      0.233293 |                   2.47735 |        -0.473062 | {"RSSTSIM": 0.05, "TMFSIM": 0.4, "TQQQSIM": 0.45, "UGLSIM": 0.05, "ZROZSIM": 0.05}               |
|     11 |         2.47434 |    0.214676 |  -0.862499 |      0.757712 |       1.05432  |      0.248901 |                   2.47434 |        -0.368136 | {"QLDSIM": 0.05, "RSSTSIM": 0.15, "TMFSIM": 0.35, "TQQQSIM": 0.35, "UGLSIM": 0.1}                |
|     12 |         2.47343 |    0.217778 |  -0.882661 |      0.753172 |       1.04194  |      0.246729 |                   2.47343 |        -0.321889 | {"RSSTSIM": 0.15, "TMFSIM": 0.3, "TQQQSIM": 0.4, "UGLSIM": 0.15}                                 |
|     13 |         2.47007 |    0.208705 |  -0.83496  |      0.756609 |       1.06134  |      0.249959 |                   2.47007 |        -0.393875 | {"QLDSIM": 0.1, "RSSTSIM": 0.1, "TMFSIM": 0.4, "TQQQSIM": 0.3, "UGLSIM": 0.1}                    |
|     14 |         2.45409 |    0.212652 |  -0.863495 |      0.751129 |       1.04535  |      0.246269 |                   2.45409 |        -0.374353 | {"GDESIM": 0.05, "QLDSIM": 0.05, "RSSTSIM": 0.1, "TMFSIM": 0.35, "TQQQSIM": 0.35, "UGLSIM": 0.1} |
|     15 |         2.44334 |    0.207648 |  -0.764349 |      0.803192 |       1.13726  |      0.271667 |                   2.44334 |        -0.30501  | {"RSSTSIM": 0.2, "TMFSIM": 0.4, "TQQQSIM": 0.3, "UGLSIM": 0.1}                                   |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   gold |   long_treasury |   managed_futures |   nasdaq_equity |   us_large_equity |
|-------:|----------------:|-------:|-------:|----------------:|------------------:|----------------:|------------------:|
|      1 |         2.61282 |  -0.1  |    0.1 |            1.35 |              0.1  |            1.2  |              0.1  |
|      2 |         2.6009  |  -0.05 |    0.3 |            1.35 |              0.05 |            1.05 |              0.05 |
|      3 |         2.55984 |  -0.1  |    0.3 |            1.05 |              0.1  |            1.2  |              0.1  |
|      4 |         2.55157 |  -0.15 |    0.2 |            1.2  |              0.15 |            1.05 |              0.15 |
|      5 |         2.52961 |  -0.15 |    0.2 |            1.05 |              0.15 |            1.2  |              0.15 |

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
