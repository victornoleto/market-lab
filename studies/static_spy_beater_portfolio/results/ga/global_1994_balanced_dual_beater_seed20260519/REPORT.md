# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `global_1994`
- Fitness: `balanced_dual_beater`
- Seed: `20260519`
- Common window: `1994-05-05` to `2026-04-17`
- Unique evaluated portfolios: `845`
- GA rolling step: `126` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `20` portfolios
- Benchmark rolling step: `1`
- Generations completed: `24` / `40`
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

- Fitness value: `0.577925`
- Weights: `{"RSSTSIM": 0.1, "TMFSIM": 0.45, "TQQQSIM": 0.35, "UGLSIM": 0.1}`
- Effective exposure: `{"cash": -0.1, "gold": 0.2, "long_treasury": 1.35, "managed_futures": 0.1, "nasdaq_equity": 1.0499999999999998, "us_large_equity": 0.1}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                         |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:--------------------------------------------------------------------------------|
|      1 |        0.577925 |    0.207143 |  -0.812157 |      0.756656 |       1.06869  |      0.255053 |                   2.59373 |        -0.388581 | {"RSSTSIM": 0.1, "TMFSIM": 0.45, "TQQQSIM": 0.35, "UGLSIM": 0.1}                |
|      2 |        0.576758 |    0.209242 |  -0.859798 |      0.718573 |       1.01074  |      0.243362 |                   2.59029 |        -0.478659 | {"RSSTSIM": 0.1, "TMFSIM": 0.5, "TQQQSIM": 0.4}                                 |
|      3 |        0.573896 |    0.210382 |  -0.896784 |      0.695842 |       0.972837 |      0.234596 |                   2.60966 |        -0.52219  | {"RSSTSIM": 0.05, "TMFSIM": 0.5, "TQQQSIM": 0.45}                               |
|      4 |        0.570955 |    0.213389 |  -0.867872 |      0.730818 |       1.02254  |      0.245876 |                   2.5454  |        -0.455505 | {"RSSTSIM": 0.15, "TMFSIM": 0.45, "TQQQSIM": 0.4}                               |
|      5 |        0.565362 |    0.202048 |  -0.801209 |      0.724124 |       1.02905  |      0.252179 |                   2.53511 |        -0.417583 | {"RSSTSIM": 0.1, "TMFSIM": 0.55, "TQQQSIM": 0.35}                               |
|      6 |        0.56003  |    0.217029 |  -0.876952 |      0.74004  |       1.03055  |      0.247481 |                   2.4906  |        -0.417072 | {"RSSTSIM": 0.2, "TMFSIM": 0.4, "TQQQSIM": 0.4}                                 |
|      7 |        0.553865 |    0.198781 |  -0.736707 |      0.762389 |       1.08969  |      0.269823 |                   2.45879 |        -0.314988 | {"RSSTSIM": 0.1, "TMFSIM": 0.5, "TQQQSIM": 0.3, "UGLSIM": 0.1}                  |
|      8 |        0.553317 |    0.210795 |  -0.835857 |      0.767337 |       1.07234  |      0.25219  |                   2.46488 |        -0.355482 | {"GDESIM": 0.1, "RSSTSIM": 0.1, "TMFSIM": 0.35, "TQQQSIM": 0.35, "UGLSIM": 0.1} |
|      9 |        0.552285 |    0.214878 |  -0.83254  |      0.769231 |       1.07779  |      0.258099 |                   2.43472 |        -0.385609 | {"RSSTSIM": 0.25, "TMFSIM": 0.4, "TQQQSIM": 0.35}                               |
|     10 |        0.548526 |    0.21151  |  -0.834534 |      0.759572 |       1.0636   |      0.253446 |                   2.45317 |        -0.393177 | {"GDESIM": 0.1, "RSSTSIM": 0.15, "TMFSIM": 0.4, "TQQQSIM": 0.35}                |
|     11 |        0.546633 |    0.209097 |  -0.863626 |      0.726256 |       1.01664  |      0.242115 |                   2.47319 |        -0.455433 | {"GLDSIM": 0.05, "RSSTSIM": 0.1, "TMFSIM": 0.45, "TQQQSIM": 0.4}                |
|     12 |        0.543245 |    0.210563 |  -0.877763 |      0.718006 |       1.00308  |      0.239886 |                   2.45953 |        -0.468489 | {"QLDSIM": 0.1, "RSSTSIM": 0.1, "TMFSIM": 0.45, "TQQQSIM": 0.35}                |
|     13 |        0.542412 |    0.209739 |  -0.770783 |      0.803538 |       1.13583  |      0.272112 |                   2.40343 |        -0.314453 | {"RSSTSIM": 0.25, "TMFSIM": 0.4, "TQQQSIM": 0.3, "UGLSIM": 0.05}                |
|     14 |        0.538225 |    0.211631 |  -0.882122 |      0.713267 |       0.995508 |      0.239911 |                   2.4445  |        -0.472003 | {"RSSTSIM": 0.1, "TMFSIM": 0.45, "TQQQSIM": 0.4, "UPROSIM": 0.05}               |
|     15 |        0.536878 |    0.20994  |  -0.877975 |      0.716919 |       1.00143  |      0.239118 |                   2.43666 |        -0.469054 | {"QQQSIM": 0.05, "RSSTSIM": 0.1, "TMFSIM": 0.45, "TQQQSIM": 0.4}                |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   gold |   long_treasury |   managed_futures |   nasdaq_equity |   us_large_equity |
|-------:|----------------:|-------:|-------:|----------------:|------------------:|----------------:|------------------:|
|      1 |        0.577925 |  -0.1  |    0.2 |            1.35 |              0.1  |            1.05 |              0.1  |
|      2 |        0.576758 |  -0.1  |    0   |            1.5  |              0.1  |            1.2  |              0.1  |
|      3 |        0.573896 |  -0.05 |    0   |            1.5  |              0.05 |            1.35 |              0.05 |
|      4 |        0.570955 |  -0.15 |    0   |            1.35 |              0.15 |            1.2  |              0.15 |
|      5 |        0.565362 |  -0.1  |    0   |            1.65 |              0.1  |            1.05 |              0.1  |

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
