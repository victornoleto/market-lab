# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `core_1986`
- Fitness: `sortino_robust`
- Seed: `20260519`
- Common window: `1986-12-12` to `2026-04-17`
- Unique evaluated portfolios: `1316`
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

- Fitness value: `1.558441`
- Weights: `{"BNDSIM": 0.2, "CASHX": 0.55, "GLDSIM": 0.05, "IEFSIM": 0.1, "TLTSIM": 0.05, "VTISIM": 0.05}`
- Effective exposure: `{"aggregate_bond": 0.2, "cash": 0.55, "gold": 0.05, "intermediate_treasury": 0.1, "long_treasury": 0.05, "us_total_equity": 0.05}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                         |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:------------------------------------------------------------------------------------------------|
|      1 |         1.55844 |   0.0460871 | -0.0870061 |       1.84366 |        2.5943  |      0.5297   |                 -0.449629 |        -0.754341 | {"BNDSIM": 0.2, "CASHX": 0.55, "GLDSIM": 0.05, "IEFSIM": 0.1, "TLTSIM": 0.05, "VTISIM": 0.05}   |
|      2 |         1.52491 |   0.0469658 | -0.0872037 |       1.8402  |        2.59224 |      0.538575 |                 -0.444014 |        -0.753474 | {"BNDSIM": 0.2, "CASHX": 0.5, "GLDSIM": 0.05, "IEFSIM": 0.2, "VTISIM": 0.05}                    |
|      3 |         1.44424 |   0.0476474 | -0.0803838 |       1.7696  |        2.41561 |      0.592749 |                 -0.445459 |        -0.744171 | {"BNDSIM": 0.35, "CASHX": 0.5, "GLDSIM": 0.1, "VTISIM": 0.05}                                   |
|      4 |         1.39648 |   0.0515562 | -0.100065  |       1.73639 |        2.37305 |      0.515226 |                 -0.420188 |        -0.731486 | {"BNDSIM": 0.3, "CASHX": 0.45, "GLDSIM": 0.05, "IEFSIM": 0.1, "NTSXSIM": 0.05, "VTISIM": 0.05}  |
|      5 |         1.37878 |   0.0513051 | -0.098841  |       1.73723 |        2.33477 |      0.519067 |                 -0.423317 |        -0.732561 | {"BNDSIM": 0.4, "CASHX": 0.45, "GLDSIM": 0.05, "NTSXSIM": 0.05, "VTISIM": 0.05}                 |
|      6 |         1.35509 |   0.0524115 | -0.106748  |       1.6958  |        2.31579 |      0.490983 |                 -0.413223 |        -0.729067 | {"BNDSIM": 0.3, "CASHX": 0.4, "GLDSIM": 0.05, "IEFSIM": 0.15, "VTISIM": 0.1}                    |
|      7 |         1.35266 |   0.052288  | -0.106138  |       1.70141 |        2.30489 |      0.49264  |                 -0.414846 |        -0.729632 | {"BNDSIM": 0.35, "CASHX": 0.4, "GLDSIM": 0.05, "IEFSIM": 0.1, "VTISIM": 0.1}                    |
|      8 |         1.34812 |   0.0525325 | -0.107359  |       1.6834  |        2.31803 |      0.489317 |                 -0.41164  |        -0.728566 | {"BNDSIM": 0.25, "CASHX": 0.4, "GLDSIM": 0.05, "IEFSIM": 0.2, "VTISIM": 0.1}                    |
|      9 |         1.34436 |   0.0499735 | -0.100367  |       1.73766 |        2.32116 |      0.497909 |                 -0.428658 |        -0.742869 | {"BNDSIM": 0.35, "CASHX": 0.45, "IEFSIM": 0.1, "VTISIM": 0.1}                                   |
|     10 |         1.34334 |   0.0516525 | -0.101933  |       1.69844 |        2.30355 |      0.50673  |                 -0.419953 |        -0.732274 | {"BNDSIM": 0.4, "CASHX": 0.45, "GLDSIM": 0.05, "NTSXSIM": 0.1}                                  |
|     11 |         1.33365 |   0.0512396 | -0.107126  |       1.67864 |        2.29225 |      0.47831  |                 -0.420999 |        -0.736263 | {"BNDSIM": 0.35, "CASHX": 0.4, "GLDSIM": 0.05, "IEFSIM": 0.1, "VTISIM": 0.05, "VTSIM": 0.05}    |
|     12 |         1.32899 |   0.0489969 | -0.105052  |       1.67006 |        2.31741 |      0.466407 |                 -0.428668 |        -0.749131 | {"BNDSIM": 0.35, "CASHX": 0.4, "GLDSIM": 0.05, "IEFSIM": 0.15, "VTISIM": 0.05}                  |
|     13 |         1.32663 |   0.0514843 | -0.108345  |       1.66121 |        2.30512 |      0.475188 |                 -0.417789 |        -0.735162 | {"BNDSIM": 0.25, "CASHX": 0.4, "GLDSIM": 0.05, "IEFSIM": 0.2, "VTISIM": 0.05, "VTSIM": 0.05}    |
|     14 |         1.29855 |   0.0521269 | -0.0923583 |       1.6699  |        2.24803 |      0.564398 |                 -0.42197  |        -0.721534 | {"BNDSIM": 0.35, "CASHX": 0.45, "GLDSIM": 0.1, "VTISIM": 0.1}                                   |
|     15 |         1.27394 |   0.0499116 | -0.108103  |       1.61425 |        2.26632 |      0.461704 |                 -0.427601 |        -0.74322  | {"BNDSIM": 0.25, "CASHX": 0.45, "GLDSIM": 0.05, "IEFSIM": 0.15, "RSSBSIM": 0.05, "VTSIM": 0.05} |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   aggregate_bond |   cash |   gold |   intermediate_treasury |   long_treasury |   us_total_equity |   us_large_equity |
|-------:|----------------:|-----------------:|-------:|-------:|------------------------:|----------------:|------------------:|------------------:|
|      1 |         1.55844 |             0.2  |  0.55  |   0.05 |                    0.1  |            0.05 |              0.05 |             0     |
|      2 |         1.52491 |             0.2  |  0.5   |   0.05 |                    0.2  |            0    |              0.05 |             0     |
|      3 |         1.44424 |             0.35 |  0.5   |   0.1  |                    0    |            0    |              0.05 |             0     |
|      4 |         1.39648 |             0.3  |  0.425 |   0.05 |                    0.13 |            0    |              0.05 |             0.045 |
|      5 |         1.37878 |             0.4  |  0.425 |   0.05 |                    0.03 |            0    |              0.05 |             0.045 |

## Benchmark Portfolios

| benchmark    |     cagr |       mdd |   sharpe |   sortino |   calmar |   terminal_wealth |
|:-------------|---------:|----------:|---------:|----------:|---------:|------------------:|
| equal_weight | 0.13058  | -0.549186 | 0.790668 |  1.07283  | 0.237771 |          124.828  |
| qqq_buy_hold | 0.14643  | -0.829711 | 0.657356 |  0.866503 | 0.176483 |          215.827  |
| spy_buy_hold | 0.112119 | -0.551413 | 0.666451 |  0.823533 | 0.203331 |           65.3281 |

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
