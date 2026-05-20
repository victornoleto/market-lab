# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `full_2000`
- Fitness: `balanced_spy_beater`
- Seed: `20260519`
- Common window: `2000-01-04` to `2026-04-17`
- Unique evaluated portfolios: `1382`
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

- Fitness value: `1.351483`
- Weights: `{"GDESIM": 0.05, "QLDSIM": 0.2, "TMFSIM": 0.2, "TQQQSIM": 0.45, "UGLSIM": 0.1}`
- Effective exposure: `{"cash": -0.04000000000000001, "gold": 0.24500000000000002, "long_treasury": 0.6000000000000001, "nasdaq_equity": 1.75, "us_large_equity": 0.045000000000000005}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                          |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:---------------------------------------------------------------------------------|
|      1 |         1.35148 |   0.104372  |  -0.970629 |      0.446126 |       0.588605 |     0.10753   |                   3.30707 |        -0.403981 | {"GDESIM": 0.05, "QLDSIM": 0.2, "TMFSIM": 0.2, "TQQQSIM": 0.45, "UGLSIM": 0.1}   |
|      2 |         1.32598 |   0.102494  |  -0.974259 |      0.44258  |       0.582307 |     0.105202  |                   3.24945 |        -0.39492  | {"QLDSIM": 0.3, "TMFSIM": 0.15, "TQQQSIM": 0.4, "UGLSIM": 0.15}                  |
|      3 |         1.32495 |   0.103793  |  -0.973219 |      0.445197 |       0.586468 |     0.10665   |                   3.24959 |        -0.398033 | {"GDESIM": 0.1, "QLDSIM": 0.2, "TMFSIM": 0.15, "TQQQSIM": 0.45, "UGLSIM": 0.1}   |
|      4 |         1.29489 |   0.112785  |  -0.959914 |      0.464986 |       0.614816 |     0.117495  |                   3.14755 |        -0.363405 | {"QLDSIM": 0.3, "TMFSIM": 0.2, "TQQQSIM": 0.35, "UGLSIM": 0.15}                  |
|      5 |         1.28989 |   0.0742244 |  -0.987205 |      0.398909 |       0.52251  |     0.0751864 |                   3.20275 |        -0.482203 | {"QLDSIM": 0.35, "TMFSIM": 0.15, "TQQQSIM": 0.45, "UGLSIM": 0.05}                |
|      6 |         1.27984 |   0.105101  |  -0.970524 |      0.447521 |       0.589149 |     0.108293  |                   3.1295  |        -0.37978  | {"QLDSIM": 0.35, "TMFSIM": 0.15, "TQQQSIM": 0.35, "UGLSIM": 0.15}                |
|      7 |         1.27965 |   0.106403  |  -0.969355 |      0.450192 |       0.593424 |     0.109767  |                   3.13184 |        -0.381418 | {"GDESIM": 0.1, "QLDSIM": 0.25, "TMFSIM": 0.15, "TQQQSIM": 0.4, "UGLSIM": 0.1}   |
|      8 |         1.27246 |   0.0870798 |  -0.97948  |      0.414494 |       0.544437 |     0.0889041 |                   3.13642 |        -0.437002 | {"QLDSIM": 0.35, "TMFSIM": 0.2, "TQQQSIM": 0.4, "UGLSIM": 0.05}                  |
|      9 |         1.27119 |   0.112486  |  -0.963375 |      0.463441 |       0.611711 |     0.116763  |                   3.09724 |        -0.36067  | {"GDESIM": 0.05, "QLDSIM": 0.3, "TMFSIM": 0.15, "TQQQSIM": 0.35, "UGLSIM": 0.15} |
|     10 |         1.2681  |   0.0707916 |  -0.986589 |      0.392001 |       0.513752 |     0.0717539 |                   3.15021 |        -0.485073 | {"QLDSIM": 0.35, "TMFSIM": 0.2, "TQQQSIM": 0.45}                                 |
|     11 |         1.26406 |   0.101784  |  -0.969138 |      0.440728 |       0.580885 |     0.105026  |                   3.09024 |        -0.396644 | {"QLDSIM": 0.35, "TMFSIM": 0.2, "TQQQSIM": 0.35, "UGLSIM": 0.1}                  |
|     12 |         1.26359 |   0.0810522 |  -0.988971 |      0.415114 |       0.544141 |     0.0819561 |                   3.14386 |        -0.470839 | {"QLDSIM": 0.35, "TQQQSIM": 0.45, "UGLSIM": 0.2}                                 |
|     13 |         1.26156 |   0.119463  |  -0.954726 |      0.480444 |       0.635905 |     0.125128  |                   3.06269 |        -0.341651 | {"GDESIM": 0.1, "QLDSIM": 0.25, "TMFSIM": 0.15, "TQQQSIM": 0.35, "UGLSIM": 0.15} |
|     14 |         1.26051 |   0.115885  |  -0.948274 |      0.474732 |       0.63129  |     0.122206  |                   3.05315 |        -0.337963 | {"GDESIM": 0.05, "QLDSIM": 0.25, "TMFSIM": 0.25, "TQQQSIM": 0.35, "UGLSIM": 0.1} |
|     15 |         1.25656 |   0.0804813 |  -0.985916 |      0.408268 |       0.534681 |     0.081631  |                   3.11559 |        -0.464034 | {"QLDSIM": 0.4, "TMFSIM": 0.1, "TQQQSIM": 0.4, "UGLSIM": 0.1}                    |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   gold |   long_treasury |   nasdaq_equity |   us_large_equity |
|-------:|----------------:|-------:|-------:|----------------:|----------------:|------------------:|
|      1 |         1.35148 |  -0.04 |  0.245 |            0.6  |            1.75 |             0.045 |
|      2 |         1.32598 |   0    |  0.3   |            0.45 |            1.8  |             0     |
|      3 |         1.32495 |  -0.08 |  0.29  |            0.45 |            1.75 |             0.09  |
|      4 |         1.29489 |   0    |  0.3   |            0.6  |            1.65 |             0     |
|      5 |         1.28989 |   0    |  0.1   |            0.45 |            2.05 |             0     |

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
