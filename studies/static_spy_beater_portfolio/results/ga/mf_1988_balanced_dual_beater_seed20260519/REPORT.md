# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `mf_1988`
- Fitness: `balanced_dual_beater`
- Seed: `20260519`
- Common window: `1988-01-04` to `2026-04-17`
- Unique evaluated portfolios: `887`
- GA rolling step: `126` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `20` portfolios
- Benchmark rolling step: `1`
- Generations completed: `27` / `40`
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

- Fitness value: `0.680176`
- Weights: `{"RSSTSIM": 0.25, "TMFSIM": 0.5, "TQQQSIM": 0.25}`
- Effective exposure: `{"cash": -0.25, "long_treasury": 1.5, "managed_futures": 0.25, "nasdaq_equity": 0.75, "us_large_equity": 0.25}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                          |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:-----------------------------------------------------------------|
|      1 |        0.680176 |    0.214412 |  -0.673011 |      0.847153 |        1.21447 |      0.318586 |                   2.88048 |        -0.191146 | {"RSSTSIM": 0.25, "TMFSIM": 0.5, "TQQQSIM": 0.25}                |
|      2 |        0.67762  |    0.221773 |  -0.764208 |      0.834788 |        1.1856  |      0.2902   |                   2.98379 |        -0.285591 | {"RSSTSIM": 0.25, "TMFSIM": 0.45, "TQQQSIM": 0.3}                |
|      3 |        0.676216 |    0.217969 |  -0.689825 |      0.869208 |        1.24282 |      0.315978 |                   2.87326 |        -0.190648 | {"RSSTSIM": 0.3, "TMFSIM": 0.45, "TQQQSIM": 0.25}                |
|      4 |        0.675748 |    0.224374 |  -0.822523 |      0.801148 |        1.13036 |      0.272788 |                   3.01817 |        -0.367079 | {"RSSTSIM": 0.2, "TMFSIM": 0.45, "TQQQSIM": 0.35}                |
|      5 |        0.666697 |    0.224791 |  -0.777211 |      0.847864 |        1.19939 |      0.289228 |                   2.93138 |        -0.288576 | {"RSSTSIM": 0.3, "TMFSIM": 0.4, "TQQQSIM": 0.3}                  |
|      6 |        0.66592  |    0.227307 |  -0.83254  |      0.811211 |        1.13944 |      0.273028 |                   2.94761 |        -0.351099 | {"RSSTSIM": 0.25, "TMFSIM": 0.4, "TQQQSIM": 0.35}                |
|      7 |        0.66529  |    0.22107  |  -0.706509 |      0.886405 |        1.26364 |      0.312905 |                   2.85416 |        -0.203641 | {"RSSTSIM": 0.35, "TMFSIM": 0.4, "TQQQSIM": 0.25}                |
|      8 |        0.664202 |    0.20935  |  -0.609806 |      0.874309 |        1.25834 |      0.343307 |                   2.72184 |        -0.162318 | {"RSSTSIM": 0.3, "TMFSIM": 0.5, "TQQQSIM": 0.2}                  |
|      9 |        0.663503 |    0.212983 |  -0.607657 |      0.902403 |        1.29755 |      0.350499 |                   2.71755 |        -0.147887 | {"RSSTSIM": 0.35, "TMFSIM": 0.45, "TQQQSIM": 0.2}                |
|     10 |        0.655351 |    0.214468 |  -0.656826 |      0.878784 |        1.25943 |      0.326522 |                   2.75265 |        -0.170529 | {"QLDSIM": 0.05, "RSSTSIM": 0.3, "TMFSIM": 0.45, "TQQQSIM": 0.2} |
|     11 |        0.655153 |    0.216163 |  -0.628666 |      0.925096 |        1.32842 |      0.343844 |                   2.69851 |        -0.137348 | {"RSSTSIM": 0.4, "TMFSIM": 0.4, "TQQQSIM": 0.2}                  |
|     12 |        0.651056 |    0.227343 |  -0.78969  |      0.856227 |        1.20518 |      0.287889 |                   2.85533 |        -0.279578 | {"RSSTSIM": 0.35, "TMFSIM": 0.35, "TQQQSIM": 0.3}                |
|     13 |        0.649002 |    0.229769 |  -0.843937 |      0.817399 |        1.14241 |      0.272259 |                   2.88313 |        -0.309612 | {"RSSTSIM": 0.3, "TMFSIM": 0.35, "TQQQSIM": 0.35}                |
|     14 |        0.648856 |    0.224691 |  -0.813266 |      0.821278 |        1.15629 |      0.276283 |                   2.88493 |        -0.334023 | {"QLDSIM": 0.05, "RSSTSIM": 0.25, "TMFSIM": 0.4, "TQQQSIM": 0.3} |
|     15 |        0.646263 |    0.217619 |  -0.674828 |      0.898253 |        1.28384 |      0.32248  |                   2.73606 |        -0.165028 | {"QLDSIM": 0.05, "RSSTSIM": 0.35, "TMFSIM": 0.4, "TQQQSIM": 0.2} |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   long_treasury |   managed_futures |   nasdaq_equity |   us_large_equity |
|-------:|----------------:|-------:|----------------:|------------------:|----------------:|------------------:|
|      1 |        0.680176 |  -0.25 |            1.5  |              0.25 |            0.75 |              0.25 |
|      2 |        0.67762  |  -0.25 |            1.35 |              0.25 |            0.9  |              0.25 |
|      3 |        0.676216 |  -0.3  |            1.35 |              0.3  |            0.75 |              0.3  |
|      4 |        0.675748 |  -0.2  |            1.35 |              0.2  |            1.05 |              0.2  |
|      5 |        0.666697 |  -0.3  |            1.2  |              0.3  |            0.9  |              0.3  |

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
