# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `global_1994`
- Fitness: `balanced_spy_beater`
- Seed: `20260519`
- Common window: `1994-05-05` to `2026-04-17`
- Unique evaluated portfolios: `1370`
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

- Fitness value: `1.088787`
- Weights: `{"RSSTSIM": 0.05, "TMFSIM": 0.45, "TQQQSIM": 0.4, "UGLSIM": 0.1}`
- Effective exposure: `{"cash": -0.05, "gold": 0.2, "long_treasury": 1.35, "managed_futures": 0.05, "nasdaq_equity": 1.2000000000000002, "us_large_equity": 0.05}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                            |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:-------------------------------------------------------------------|
|      1 |         1.08879 |    0.209566 |  -0.859859 |      0.729632 |       1.02407  |      0.243722 |                   2.64032 |        -0.451356 | {"RSSTSIM": 0.05, "TMFSIM": 0.45, "TQQQSIM": 0.4, "UGLSIM": 0.1}   |
|      2 |         1.07737 |    0.211665 |  -0.863819 |      0.731267 |       1.02441  |      0.245034 |                   2.61282 |        -0.45364  | {"RSSTSIM": 0.1, "TMFSIM": 0.45, "TQQQSIM": 0.4, "UGLSIM": 0.05}   |
|      3 |         1.0767  |    0.202586 |  -0.801246 |      0.738768 |       1.04848  |      0.252838 |                   2.60367 |        -0.397531 | {"RSSTSIM": 0.05, "TMFSIM": 0.5, "TQQQSIM": 0.35, "UGLSIM": 0.1}   |
|      4 |         1.07664 |    0.213494 |  -0.868672 |      0.741043 |       1.0344   |      0.245771 |                   2.60498 |        -0.419658 | {"RSSTSIM": 0.1, "TMFSIM": 0.4, "TQQQSIM": 0.4, "UGLSIM": 0.1}     |
|      5 |         1.07303 |    0.208808 |  -0.817674 |      0.767901 |       1.08124  |      0.255368 |                   2.57797 |        -0.373051 | {"RSSTSIM": 0.1, "TMFSIM": 0.4, "TQQQSIM": 0.35, "UGLSIM": 0.15}   |
|      6 |         1.0704  |    0.209234 |  -0.865887 |      0.737223 |       1.03003  |      0.241641 |                   2.59503 |        -0.387335 | {"TMFSIM": 0.35, "TQQQSIM": 0.4, "UGLSIM": 0.25}                   |
|      7 |         1.06977 |    0.206044 |  -0.812721 |      0.761996 |       1.07499  |      0.253524 |                   2.57381 |        -0.367461 | {"RSSTSIM": 0.05, "TMFSIM": 0.4, "TQQQSIM": 0.35, "UGLSIM": 0.2}   |
|      8 |         1.06713 |    0.212166 |  -0.86987  |      0.743509 |       1.03662  |      0.243906 |                   2.58207 |        -0.385419 | {"RSSTSIM": 0.05, "TMFSIM": 0.35, "TQQQSIM": 0.4, "UGLSIM": 0.2}   |
|      9 |         1.05782 |    0.202914 |  -0.80778  |      0.753325 |       1.06522  |      0.251199 |                   2.55196 |        -0.363716 | {"TMFSIM": 0.4, "TQQQSIM": 0.35, "UGLSIM": 0.25}                   |
|     10 |         1.05537 |    0.209882 |  -0.823208 |      0.774983 |       1.0873   |      0.254956 |                   2.53185 |        -0.34285  | {"RSSTSIM": 0.1, "TMFSIM": 0.35, "TQQQSIM": 0.35, "UGLSIM": 0.2}   |
|     11 |         1.05166 |    0.206889 |  -0.818481 |      0.767496 |       1.07915  |      0.252772 |                   2.52916 |        -0.343618 | {"RSSTSIM": 0.05, "TMFSIM": 0.35, "TQQQSIM": 0.35, "UGLSIM": 0.25} |
|     12 |         1.03737 |    0.217776 |  -0.911221 |      0.720133 |       0.995162 |      0.238993 |                   2.52769 |        -0.400711 | {"RSSTSIM": 0.1, "TMFSIM": 0.35, "TQQQSIM": 0.45, "UGLSIM": 0.1}   |
|     13 |         1.032   |    0.210362 |  -0.830106 |      0.777515 |       1.08688  |      0.253415 |                   2.47678 |        -0.305677 | {"RSSTSIM": 0.1, "TMFSIM": 0.3, "TQQQSIM": 0.35, "UGLSIM": 0.25}   |
|     14 |         1.02853 |    0.213214 |  -0.835101 |      0.783711 |       1.0928   |      0.255315 |                   2.46326 |        -0.302469 | {"RSSTSIM": 0.15, "TMFSIM": 0.3, "TQQQSIM": 0.35, "UGLSIM": 0.2}   |
|     15 |         1.02615 |    0.207142 |  -0.825095 |      0.768446 |       1.07645  |      0.251053 |                   2.47097 |        -0.30882  | {"RSSTSIM": 0.05, "TMFSIM": 0.3, "TQQQSIM": 0.35, "UGLSIM": 0.3}   |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   gold |   long_treasury |   managed_futures |   nasdaq_equity |   us_large_equity |
|-------:|----------------:|-------:|-------:|----------------:|------------------:|----------------:|------------------:|
|      1 |         1.08879 |  -0.05 |    0.2 |            1.35 |              0.05 |            1.2  |              0.05 |
|      2 |         1.07737 |  -0.1  |    0.1 |            1.35 |              0.1  |            1.2  |              0.1  |
|      3 |         1.0767  |  -0.05 |    0.2 |            1.5  |              0.05 |            1.05 |              0.05 |
|      4 |         1.07664 |  -0.1  |    0.2 |            1.2  |              0.1  |            1.2  |              0.1  |
|      5 |         1.07303 |  -0.1  |    0.3 |            1.2  |              0.1  |            1.05 |              0.1  |

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
