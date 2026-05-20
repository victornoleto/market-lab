# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `mf_1988`
- Fitness: `sortino_robust`
- Seed: `20260519`
- Common window: `1988-01-04` to `2026-04-17`
- Unique evaluated portfolios: `1371`
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

- Fitness value: `2.530546`
- Weights: `{"BNDSIM": 0.25, "CASHX": 0.75}`
- Effective exposure: `{"aggregate_bond": 0.25, "cash": 0.75}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                        |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:-------------------------------------------------------------------------------|
|      1 |         2.53055 |   0.0360933 | -0.0399663 |       2.94317 |        4.08967 |      0.903093 |                 -0.506469 |        -0.803029 | {"BNDSIM": 0.25, "CASHX": 0.75}                                                |
|      2 |         2.45544 |   0.0383012 | -0.0409014 |       2.87447 |        3.84959 |      0.936428 |                 -0.498377 |        -0.791499 | {"BNDSIM": 0.2, "CASHX": 0.75, "VTSIM": 0.05}                                  |
|      3 |         2.42173 |   0.0362556 | -0.0422939 |       2.85799 |        4.07129 |      0.857229 |                 -0.505114 |        -0.803001 | {"BNDSIM": 0.2, "CASHX": 0.75, "IEFSIM": 0.05}                                 |
|      4 |         2.1866  |   0.0389467 | -0.0214749 |       2.70856 |        3.94565 |      1.8136   |                 -0.491563 |        -0.800966 | {"BNDSIM": 0.25, "CASHX": 0.7, "KMLMSIM": 0.05}                                |
|      5 |         2.18285 |   0.0371484 | -0.0290427 |       2.75728 |        4.05203 |      1.2791   |                 -0.501159 |        -0.802705 | {"BNDSIM": 0.1, "CASHX": 0.8, "KMLMSIM": 0.05, "TLTSIM": 0.05}                 |
|      6 |         2.12265 |   0.0382361 | -0.0511577 |       2.451   |        3.39171 |      0.747417 |                 -0.493542 |        -0.792619 | {"BNDSIM": 0.25, "CASHX": 0.7, "GLDSIM": 0.05}                                 |
|      7 |         2.11692 |   0.0372828 | -0.050309  |       2.53919 |        3.52771 |      0.741076 |                 -0.499251 |        -0.801628 | {"BNDSIM": 0.3, "CASHX": 0.7}                                                  |
|      8 |         2.09559 |   0.0411402 | -0.052684  |       2.55362 |        3.42961 |      0.780886 |                 -0.483089 |        -0.784987 | {"BNDSIM": 0.25, "CASHX": 0.7, "NTSXSIM": 0.05}                                |
|      9 |         2.04346 |   0.0374433 | -0.0526048 |       2.48284 |        3.52377 |      0.711786 |                 -0.497835 |        -0.80139  | {"BNDSIM": 0.25, "CASHX": 0.7, "IEFSIM": 0.05}                                 |
|     10 |         2.03288 |   0.0424786 | -0.0563724 |       2.40792 |        3.43847 |      0.753536 |                 -0.476333 |        -0.777356 | {"BNDSIM": 0.15, "CASHX": 0.75, "QQQSIM": 0.05, "TLTSIM": 0.05}                |
|     11 |         1.99717 |   0.0430718 | -0.0545935 |       2.43056 |        3.37451 |      0.788954 |                 -0.474177 |        -0.777213 | {"BNDSIM": 0.25, "CASHX": 0.7, "QQQSIM": 0.05}                                 |
|     12 |         1.9437  |   0.0408486 | -0.0610853 |       2.36292 |        3.20355 |      0.668715 |                 -0.482017 |        -0.788086 | {"BNDSIM": 0.25, "CASHX": 0.65, "IEFSIM": 0.05, "VTSIM": 0.05}                 |
|     13 |         1.89066 |   0.0432156 | -0.0615141 |       2.24113 |        3.03422 |      0.702532 |                 -0.469562 |        -0.77462  | {"BNDSIM": 0.3, "CASHX": 0.65, "GDESIM": 0.05}                                 |
|     14 |         1.86643 |   0.0475875 | -0.0354931 |       2.35738 |        3.42501 |      1.34075  |                 -0.449869 |        -0.77831  | {"BNDSIM": 0.25, "CASHX": 0.65, "KMLMSIM": 0.05, "RSSTSIM": 0.05}              |
|     15 |         1.85608 |   0.0438318 | -0.0664977 |       2.22146 |        3.18782 |      0.659147 |                 -0.467161 |        -0.775318 | {"BNDSIM": 0.15, "CASHX": 0.7, "IEFSIM": 0.05, "QQQSIM": 0.05, "TLTSIM": 0.05} |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   aggregate_bond |   cash |   global_equity |   intermediate_treasury |   managed_futures |   long_treasury |
|-------:|----------------:|-----------------:|-------:|----------------:|------------------------:|------------------:|----------------:|
|      1 |         2.53055 |             0.25 |   0.75 |            0    |                    0    |              0    |            0    |
|      2 |         2.45544 |             0.2  |   0.75 |            0.05 |                    0    |              0    |            0    |
|      3 |         2.42173 |             0.2  |   0.75 |            0    |                    0.05 |              0    |            0    |
|      4 |         2.1866  |             0.25 |   0.7  |            0    |                    0    |              0.05 |            0    |
|      5 |         2.18285 |             0.1  |   0.8  |            0    |                    0    |              0.05 |            0.05 |

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
