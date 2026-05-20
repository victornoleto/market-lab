# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `full_2000`
- Fitness: `relative_wealth_qqq`
- Seed: `20260519`
- Common window: `2000-01-04` to `2026-04-17`
- Unique evaluated portfolios: `1229`
- GA rolling step: `126` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `20` portfolios
- Benchmark rolling step: `1`
- Generations completed: `36` / `40`
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

- Fitness value: `1.941721`
- Weights: `{"TMFSIM": 0.2, "TQQQSIM": 0.6, "UGLSIM": 0.2}`
- Effective exposure: `{"gold": 0.4, "long_treasury": 0.6000000000000001, "nasdaq_equity": 1.7999999999999998}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                          |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:-----------------------------------------------------------------|
|      1 |         1.94172 |   0.111487  |  -0.973262 |      0.460493 |       0.608216 |     0.114549  |                   3.84977 |        -0.408265 | {"TMFSIM": 0.2, "TQQQSIM": 0.6, "UGLSIM": 0.2}                   |
|      2 |         1.93979 |   0.114324  |  -0.974496 |      0.466061 |       0.615001 |     0.117316  |                   3.85706 |        -0.393016 | {"TMFSIM": 0.15, "TQQQSIM": 0.6, "UGLSIM": 0.25}                 |
|      3 |         1.92939 |   0.0997352 |  -0.983063 |      0.440478 |       0.579431 |     0.101453  |                   3.92039 |        -0.441982 | {"TMFSIM": 0.15, "TQQQSIM": 0.65, "UGLSIM": 0.2}                 |
|      4 |         1.92843 |   0.0968307 |  -0.982234 |      0.434561 |       0.572023 |     0.0985821 |                   3.90488 |        -0.4485   | {"TMFSIM": 0.2, "TQQQSIM": 0.65, "UGLSIM": 0.15}                 |
|      5 |         1.92454 |   0.108063  |  -0.972001 |      0.45368  |       0.600354 |     0.111176  |                   3.80161 |        -0.412579 | {"TMFSIM": 0.25, "TQQQSIM": 0.6, "UGLSIM": 0.15}                 |
|      6 |         1.90787 |   0.121188  |  -0.958553 |      0.483183 |       0.642451 |     0.126428  |                   3.69995 |        -0.356598 | {"TMFSIM": 0.25, "TQQQSIM": 0.55, "UGLSIM": 0.2}                 |
|      7 |         1.90655 |   0.127303  |  -0.962206 |      0.494748 |       0.655487 |     0.132303  |                   3.73688 |        -0.348205 | {"TMFSIM": 0.15, "TQQQSIM": 0.55, "UGLSIM": 0.3}                 |
|      8 |         1.90256 |   0.116568  |  -0.975701 |      0.47041  |       0.620831 |     0.119471  |                   3.82665 |        -0.387064 | {"TMFSIM": 0.1, "TQQQSIM": 0.6, "UGLSIM": 0.3}                   |
|      9 |         1.88701 |   0.104061  |  -0.970714 |      0.445634 |       0.591024 |     0.107201  |                   3.72007 |        -0.415206 | {"TMFSIM": 0.3, "TQQQSIM": 0.6, "UGLSIM": 0.1}                   |
|     10 |         1.87339 |   0.11409   |  -0.969411 |      0.465974 |       0.615955 |     0.11769   |                   3.71678 |        -0.392943 | {"QLDSIM": 0.05, "TMFSIM": 0.2, "TQQQSIM": 0.55, "UGLSIM": 0.2}  |
|     11 |         1.8561  |   0.120678  |  -0.961711 |      0.481208 |       0.637514 |     0.125482  |                   3.64654 |        -0.366721 | {"RSSTSIM": 0.05, "TMFSIM": 0.2, "TQQQSIM": 0.55, "UGLSIM": 0.2} |
|     12 |         1.83769 |   0.132708  |  -0.939566 |      0.516198 |       0.690152 |     0.141244  |                   3.56231 |        -0.305    | {"TMFSIM": 0.25, "TQQQSIM": 0.5, "UGLSIM": 0.25}                 |
|     13 |         1.82946 |   0.1138    |  -0.958525 |      0.466993 |       0.622029 |     0.118724  |                   3.54591 |        -0.375312 | {"GDESIM": 0.05, "TMFSIM": 0.3, "TQQQSIM": 0.55, "UGLSIM": 0.1}  |
|     14 |         1.82153 |   0.107711  |  -0.973244 |      0.453004 |       0.597664 |     0.110672  |                   3.64166 |        -0.409619 | {"GLDSIM": 0.05, "TMFSIM": 0.2, "TQQQSIM": 0.6, "UGLSIM": 0.15}  |
|     15 |         1.80723 |   0.116535  |  -0.965055 |      0.471752 |       0.624178 |     0.120755  |                   3.57928 |        -0.377384 | {"QLDSIM": 0.1, "TMFSIM": 0.2, "TQQQSIM": 0.5, "UGLSIM": 0.2}    |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   gold |   long_treasury |   nasdaq_equity |
|-------:|----------------:|-------:|----------------:|----------------:|
|      1 |         1.94172 |    0.4 |            0.6  |            1.8  |
|      2 |         1.93979 |    0.5 |            0.45 |            1.8  |
|      3 |         1.92939 |    0.4 |            0.45 |            1.95 |
|      4 |         1.92843 |    0.3 |            0.6  |            1.95 |
|      5 |         1.92454 |    0.3 |            0.75 |            1.8  |

## Benchmark Portfolios

| benchmark    |      cagr |       mdd |   sharpe |   sortino |   calmar |   terminal_wealth |
|:-------------|----------:|----------:|---------:|----------:|---------:|------------------:|
| b4           | 0.121202  | -0.279216 | 0.882281 |  1.23885  | 0.434078 |          20.1098  |
| equal_weight | 0.0975615 | -0.461271 | 0.659838 |  0.886617 | 0.211506 |          11.4978  |
| qqq_buy_hold | 0.0830434 | -0.829711 | 0.431434 |  0.56349  | 0.100087 |           8.10781 |
| spy_buy_hold | 0.0823563 | -0.551413 | 0.505935 |  0.643555 | 0.149355 |           7.97396 |

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
