# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `full_2000`
- Fitness: `relative_wealth_spy`
- Seed: `20260519`
- Common window: `2000-01-04` to `2026-04-17`
- Unique evaluated portfolios: `1390`
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

- Fitness value: `3.890039`
- Weights: `{"TMFSIM": 0.15, "TQQQSIM": 0.8, "UGLSIM": 0.05}`
- Effective exposure: `{"gold": 0.1, "long_treasury": 0.44999999999999996, "nasdaq_equity": 2.4000000000000004}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                          |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:---------------------------------------------------------------------------------|
|      1 |         3.89004 |   0.0464277 |  -0.99591  |      0.381176 |       0.498529 |     0.0466184 |                   3.89004 |        -0.585396 | {"TMFSIM": 0.15, "TQQQSIM": 0.8, "UGLSIM": 0.05}                                 |
|      2 |         3.86058 |   0.0770421 |  -0.987834 |      0.404952 |       0.531907 |     0.0779909 |                   3.86058 |        -0.499091 | {"TMFSIM": 0.25, "TQQQSIM": 0.7, "UGLSIM": 0.05}                                 |
|      3 |         3.83583 |   0.05917   |  -0.992192 |      0.385278 |       0.50495  |     0.0596356 |                   3.83583 |        -0.544793 | {"TMFSIM": 0.25, "TQQQSIM": 0.75}                                                |
|      4 |         3.75682 |   0.0729305 |  -0.987261 |      0.397352 |       0.52269  |     0.0738715 |                   3.75682 |        -0.511464 | {"TMFSIM": 0.3, "TQQQSIM": 0.7}                                                  |
|      5 |         3.71749 |   0.0748885 |  -0.990003 |      0.406363 |       0.53296  |     0.0756448 |                   3.71749 |        -0.513291 | {"GDESIM": 0.1, "TMFSIM": 0.15, "TQQQSIM": 0.7, "UGLSIM": 0.05}                  |
|      6 |         3.71121 |   0.0774392 |  -0.990485 |      0.412032 |       0.540133 |     0.0781831 |                   3.71121 |        -0.512277 | {"GDESIM": 0.1, "TMFSIM": 0.1, "TQQQSIM": 0.7, "UGLSIM": 0.1}                    |
|      7 |         3.70989 |   0.0577438 |  -0.994253 |      0.391404 |       0.511905 |     0.0580775 |                   3.70989 |        -0.554261 | {"QLDSIM": 0.1, "TMFSIM": 0.1, "TQQQSIM": 0.7, "UGLSIM": 0.1}                    |
|      8 |         3.68663 |   0.0887068 |  -0.983863 |      0.421464 |       0.554371 |     0.0901618 |                   3.68663 |        -0.466516 | {"GDESIM": 0.1, "TMFSIM": 0.2, "TQQQSIM": 0.65, "UGLSIM": 0.05}                  |
|      9 |         3.68518 |   0.0717568 |  -0.98951  |      0.4      |       0.524888 |     0.0725176 |                   3.68518 |        -0.516415 | {"GDESIM": 0.1, "TMFSIM": 0.2, "TQQQSIM": 0.7}                                   |
|     10 |         3.68304 |   0.0590219 |  -0.994162 |      0.393723 |       0.515367 |     0.0593685 |                   3.68304 |        -0.556235 | {"GDESIM": 0.1, "TMFSIM": 0.1, "TQQQSIM": 0.75, "UGLSIM": 0.05}                  |
|     11 |         3.61367 |   0.0717548 |  -0.991361 |      0.404189 |       0.529342 |     0.0723801 |                   3.61367 |        -0.519286 | {"GDESIM": 0.05, "QLDSIM": 0.1, "TMFSIM": 0.1, "TQQQSIM": 0.65, "UGLSIM": 0.1}   |
|     12 |         3.6133  |   0.0785727 |  -0.988431 |      0.409515 |       0.537323 |     0.0794923 |                   3.6133  |        -0.496769 | {"GDESIM": 0.1, "QLDSIM": 0.05, "TMFSIM": 0.15, "TQQQSIM": 0.65, "UGLSIM": 0.05} |
|     13 |         3.60565 |   0.0876112 |  -0.985344 |      0.421424 |       0.553893 |     0.0889143 |                   3.60565 |        -0.473139 | {"GDESIM": 0.15, "TMFSIM": 0.15, "TQQQSIM": 0.65, "UGLSIM": 0.05}                |
|     14 |         3.58819 |   0.0597606 |  -0.993598 |      0.39204  |       0.512999 |     0.0601456 |                   3.58819 |        -0.550606 | {"RSSBSIM": 0.05, "TMFSIM": 0.1, "TQQQSIM": 0.75, "UGLSIM": 0.1}                 |
|     15 |         3.58783 |   0.0605461 |  -0.992721 |      0.390303 |       0.511282 |     0.0609901 |                   3.58783 |        -0.543798 | {"GDESIM": 0.1, "QLDSIM": 0.05, "TMFSIM": 0.15, "TQQQSIM": 0.7}                  |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   gold |   long_treasury |   nasdaq_equity |   cash |   us_large_equity |
|-------:|----------------:|-------:|----------------:|----------------:|-------:|------------------:|
|      1 |         3.89004 |   0.1  |            0.45 |            2.4  |   0    |              0    |
|      2 |         3.86058 |   0.1  |            0.75 |            2.1  |   0    |              0    |
|      3 |         3.83583 |   0    |            0.75 |            2.25 |   0    |              0    |
|      4 |         3.75682 |   0    |            0.9  |            2.1  |   0    |              0    |
|      5 |         3.71749 |   0.19 |            0.45 |            2.1  |  -0.08 |              0.09 |

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
