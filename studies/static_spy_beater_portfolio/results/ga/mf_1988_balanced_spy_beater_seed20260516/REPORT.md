# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `mf_1988`
- Fitness: `balanced_spy_beater`
- Seed: `20260516`
- Common window: `1988-01-04` to `2026-04-17`
- Unique evaluated portfolios: `10140`
- GA rolling step: `21` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `200` portfolios
- Benchmark rolling step: `1`
- Generations completed: `39` / `400`
- Early stop: `True` (`no_improvement_for_25_generations`)
- Patience: `25`, min_delta: `1e-09`
- Log every: `10` generations
- Eval log every: `500` unique portfolios
- Fast discovery: `True`
- Jobs: `4`

This is discovery output only. It is not a validated winner or a mandate change.
GA search breadth must be carried into later DSR/PBO accounting
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Best Portfolio

- Fitness value: `1.250914`
- Weights: `{"RSSTSIM": 0.15, "TMFSIM": 0.5, "TQQQSIM": 0.35}`
- Effective exposure: `{"cash": -0.15, "long_treasury": 1.5, "managed_futures": 0.15, "nasdaq_equity": 1.0499999999999998, "us_large_equity": 0.15}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                          |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:-----------------------------------------------------------------|
|      1 |         1.25091 |    0.220977 |  -0.812081 |      0.787511 |        1.11552 |      0.272112 |                   3.05219 |        -0.36469  | {"RSSTSIM": 0.15, "TMFSIM": 0.5, "TQQQSIM": 0.35}                |
|      2 |         1.24865 |    0.21712  |  -0.801209 |      0.770749 |        1.09605 |      0.27099  |                   3.05631 |        -0.34882  | {"RSSTSIM": 0.1, "TMFSIM": 0.55, "TQQQSIM": 0.35}                |
|      3 |         1.24133 |    0.218294 |  -0.750675 |      0.817503 |        1.16512 |      0.290797 |                   3.00496 |        -0.276221 | {"RSSTSIM": 0.2, "TMFSIM": 0.5, "TQQQSIM": 0.3}                  |
|      4 |         1.24037 |    0.224374 |  -0.822523 |      0.801148 |        1.13036 |      0.272788 |                   3.01817 |        -0.367079 | {"RSSTSIM": 0.2, "TMFSIM": 0.45, "TQQQSIM": 0.35}                |
|      5 |         1.23689 |    0.221773 |  -0.764208 |      0.834788 |        1.1856  |      0.2902   |                   2.98379 |        -0.285591 | {"RSSTSIM": 0.25, "TMFSIM": 0.45, "TQQQSIM": 0.3}                |
|      6 |         1.23606 |    0.212807 |  -0.790018 |      0.751415 |        1.07205 |      0.26937  |                   3.03569 |        -0.345112 | {"RSSTSIM": 0.05, "TMFSIM": 0.6, "TQQQSIM": 0.35}                |
|      7 |         1.23405 |    0.214359 |  -0.736911 |      0.796694 |        1.13893 |      0.290888 |                   2.99881 |        -0.252581 | {"RSSTSIM": 0.15, "TMFSIM": 0.55, "TQQQSIM": 0.3}                |
|      8 |         1.23066 |    0.218667 |  -0.851482 |      0.744837 |        1.05351 |      0.256808 |                   3.03208 |        -0.444811 | {"RSSTSIM": 0.05, "TMFSIM": 0.55, "TQQQSIM": 0.4}                |
|      9 |         1.22501 |    0.214432 |  -0.842819 |      0.7289   |        1.03506 |      0.254422 |                   3.02726 |        -0.423784 | {"TMFSIM": 0.6, "TQQQSIM": 0.4}                                  |
|     10 |         1.22088 |    0.209972 |  -0.722863 |      0.773151 |        1.10808 |      0.290472 |                   2.97902 |        -0.261561 | {"RSSTSIM": 0.1, "TMFSIM": 0.6, "TQQQSIM": 0.3}                  |
|     11 |         1.22087 |    0.222443 |  -0.859798 |      0.758442 |        1.06856 |      0.258716 |                   3.00013 |        -0.443216 | {"RSSTSIM": 0.1, "TMFSIM": 0.5, "TQQQSIM": 0.4}                  |
|     12 |         1.21951 |    0.218258 |  -0.790673 |      0.794897 |        1.12872 |      0.276041 |                   2.96818 |        -0.327181 | {"QLDSIM": 0.05, "RSSTSIM": 0.15, "TMFSIM": 0.5, "TQQQSIM": 0.3} |
|     13 |         1.21857 |    0.224791 |  -0.777211 |      0.847864 |        1.19939 |      0.289228 |                   2.93138 |        -0.288576 | {"RSSTSIM": 0.3, "TMFSIM": 0.4, "TQQQSIM": 0.3}                  |
|     14 |         1.21517 |    0.208044 |  -0.77864  |      0.730106 |        1.0447  |      0.267189 |                   2.99604 |        -0.330191 | {"TMFSIM": 0.65, "TQQQSIM": 0.35}                                |
|     15 |         1.21507 |    0.214352 |  -0.778677 |      0.776552 |        1.10678 |      0.275277 |                   2.96771 |        -0.321622 | {"QLDSIM": 0.05, "RSSTSIM": 0.1, "TMFSIM": 0.55, "TQQQSIM": 0.3} |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   long_treasury |   managed_futures |   nasdaq_equity |   us_large_equity |
|-------:|----------------:|-------:|----------------:|------------------:|----------------:|------------------:|
|      1 |         1.25091 |  -0.15 |            1.5  |              0.15 |            1.05 |              0.15 |
|      2 |         1.24865 |  -0.1  |            1.65 |              0.1  |            1.05 |              0.1  |
|      3 |         1.24133 |  -0.2  |            1.5  |              0.2  |            0.9  |              0.2  |
|      4 |         1.24037 |  -0.2  |            1.35 |              0.2  |            1.05 |              0.2  |
|      5 |         1.23689 |  -0.25 |            1.35 |              0.25 |            0.9  |              0.25 |

## Benchmark Portfolios

| benchmark    |     cagr |       mdd |   sharpe |   sortino |   calmar |   terminal_wealth |
|:-------------|---------:|----------:|---------:|----------:|---------:|------------------:|
| b4           | 0.144308 | -0.279216 | 1.01761  |  1.44948  | 0.516831 |          174.042  |
| equal_weight | 0.135215 | -0.514257 | 0.862407 |  1.1883   | 0.262932 |          128.246  |
| qqq_buy_hold | 0.148737 | -0.829711 | 0.66842  |  0.893506 | 0.179264 |          201.78   |
| spy_buy_hold | 0.114583 | -0.551413 | 0.691024 |  0.884039 | 0.207798 |           63.5573 |

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
