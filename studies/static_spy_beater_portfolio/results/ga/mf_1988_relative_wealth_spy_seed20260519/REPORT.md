# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `mf_1988`
- Fitness: `relative_wealth_spy`
- Seed: `20260519`
- Common window: `1988-01-04` to `2026-04-17`
- Unique evaluated portfolios: `906`
- GA rolling step: `126` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `20` portfolios
- Benchmark rolling step: `1`
- Generations completed: `28` / `40`
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

- Fitness value: `3.056313`
- Weights: `{"RSSTSIM": 0.1, "TMFSIM": 0.55, "TQQQSIM": 0.35}`
- Effective exposure: `{"cash": -0.1, "long_treasury": 1.6500000000000001, "managed_futures": 0.1, "nasdaq_equity": 1.0499999999999998, "us_large_equity": 0.1}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                            |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:-------------------------------------------------------------------|
|      1 |         3.05631 |    0.21712  |  -0.801209 |      0.770749 |        1.09605 |      0.27099  |                   3.05631 |        -0.34882  | {"RSSTSIM": 0.1, "TMFSIM": 0.55, "TQQQSIM": 0.35}                  |
|      2 |         3.03569 |    0.212807 |  -0.790018 |      0.751415 |        1.07205 |      0.26937  |                   3.03569 |        -0.345112 | {"RSSTSIM": 0.05, "TMFSIM": 0.6, "TQQQSIM": 0.35}                  |
|      3 |         3.01817 |    0.224374 |  -0.822523 |      0.801148 |        1.13036 |      0.272788 |                   3.01817 |        -0.367079 | {"RSSTSIM": 0.2, "TMFSIM": 0.45, "TQQQSIM": 0.35}                  |
|      4 |         3.00496 |    0.218294 |  -0.750675 |      0.817503 |        1.16512 |      0.290797 |                   3.00496 |        -0.276221 | {"RSSTSIM": 0.2, "TMFSIM": 0.5, "TQQQSIM": 0.3}                    |
|      5 |         3.00013 |    0.222443 |  -0.859798 |      0.758442 |        1.06856 |      0.258716 |                   3.00013 |        -0.443216 | {"RSSTSIM": 0.1, "TMFSIM": 0.5, "TQQQSIM": 0.4}                    |
|      6 |         2.99881 |    0.214359 |  -0.736911 |      0.796694 |        1.13893 |      0.290888 |                   2.99881 |        -0.252581 | {"RSSTSIM": 0.15, "TMFSIM": 0.55, "TQQQSIM": 0.3}                  |
|      7 |         2.98379 |    0.221773 |  -0.764208 |      0.834788 |        1.1856  |      0.2902   |                   2.98379 |        -0.285591 | {"RSSTSIM": 0.25, "TMFSIM": 0.45, "TQQQSIM": 0.3}                  |
|      8 |         2.97902 |    0.209972 |  -0.722863 |      0.773151 |        1.10808 |      0.290472 |                   2.97902 |        -0.261561 | {"RSSTSIM": 0.1, "TMFSIM": 0.6, "TQQQSIM": 0.3}                    |
|      9 |         2.95985 |    0.22015  |  -0.843297 |      0.76534  |        1.0804  |      0.261058 |                   2.95985 |        -0.414232 | {"QLDSIM": 0.05, "RSSTSIM": 0.1, "TMFSIM": 0.5, "TQQQSIM": 0.35}   |
|     10 |         2.94245 |    0.209993 |  -0.766542 |      0.755591 |        1.07997 |      0.273948 |                   2.94245 |        -0.303766 | {"QLDSIM": 0.05, "RSSTSIM": 0.05, "TMFSIM": 0.6, "TQQQSIM": 0.3}   |
|     11 |         2.94152 |    0.205139 |  -0.754373 |      0.74768  |        1.07443 |      0.271933 |                   2.94152 |        -0.283273 | {"RSSTSIM": 0.05, "TMFSIM": 0.65, "TQQQSIM": 0.3}                  |
|     12 |         2.94011 |    0.221706 |  -0.8022   |      0.809985 |        1.14559 |      0.276372 |                   2.94011 |        -0.339323 | {"QLDSIM": 0.05, "RSSTSIM": 0.2, "TMFSIM": 0.45, "TQQQSIM": 0.3}   |
|     13 |         2.93138 |    0.224791 |  -0.777211 |      0.847864 |        1.19939 |      0.289228 |                   2.93138 |        -0.288576 | {"RSSTSIM": 0.3, "TMFSIM": 0.4, "TQQQSIM": 0.3}                    |
|     14 |         2.92149 |    0.212091 |  -0.795552 |      0.762587 |        1.08583 |      0.266596 |                   2.92149 |        -0.333083 | {"RSSTSIM": 0.05, "TMFSIM": 0.55, "TQQQSIM": 0.35, "UGLSIM": 0.05} |
|     15 |         2.90679 |    0.228598 |  -0.876952 |      0.777225 |        1.08522 |      0.260674 |                   2.90679 |        -0.381783 | {"RSSTSIM": 0.2, "TMFSIM": 0.4, "TQQQSIM": 0.4}                    |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   long_treasury |   managed_futures |   nasdaq_equity |   us_large_equity |
|-------:|----------------:|-------:|----------------:|------------------:|----------------:|------------------:|
|      1 |         3.05631 |  -0.1  |            1.65 |              0.1  |            1.05 |              0.1  |
|      2 |         3.03569 |  -0.05 |            1.8  |              0.05 |            1.05 |              0.05 |
|      3 |         3.01817 |  -0.2  |            1.35 |              0.2  |            1.05 |              0.2  |
|      4 |         3.00496 |  -0.2  |            1.5  |              0.2  |            0.9  |              0.2  |
|      5 |         3.00013 |  -0.1  |            1.5  |              0.1  |            1.2  |              0.1  |

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
