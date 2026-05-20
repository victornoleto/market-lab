# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `mf_1988`
- Fitness: `cagr_robust`
- Seed: `20260519`
- Common window: `1988-01-04` to `2026-04-17`
- Unique evaluated portfolios: `1183`
- GA rolling step: `126` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `20` portfolios
- Benchmark rolling step: `1`
- Generations completed: `38` / `40`
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

- Fitness value: `0.098546`
- Weights: `{"QLDSIM": 0.05, "RSSTSIM": 0.35, "TMFSIM": 0.3, "TQQQSIM": 0.3}`
- Effective exposure: `{"cash": -0.35, "long_treasury": 0.8999999999999999, "managed_futures": 0.35, "nasdaq_equity": 0.9999999999999999, "us_large_equity": 0.35}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                         |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:--------------------------------------------------------------------------------|
|      1 |       0.0985455 |    0.229255 |  -0.837017 |      0.831179 |        1.15793 |      0.273895 |                   2.72385 |        -0.250651 | {"QLDSIM": 0.05, "RSSTSIM": 0.35, "TMFSIM": 0.3, "TQQQSIM": 0.3}                |
|      2 |       0.0980246 |    0.230789 |  -0.880273 |      0.79335  |        1.09893 |      0.262178 |                   2.66795 |        -0.267611 | {"QLDSIM": 0.05, "RSSTSIM": 0.3, "TMFSIM": 0.3, "TQQQSIM": 0.35}                |
|      3 |       0.0976679 |    0.224489 |  -0.803824 |      0.839929 |        1.17963 |      0.279277 |                   2.73318 |        -0.293932 | {"QLDSIM": 0.1, "RSSTSIM": 0.3, "TMFSIM": 0.35, "TQQQSIM": 0.25}                |
|      4 |       0.0974397 |    0.224741 |  -0.831603 |      0.829423 |        1.15668 |      0.27025  |                   2.66132 |        -0.253747 | {"QLDSIM": 0.05, "RSSTSIM": 0.3, "TMFSIM": 0.3, "TQQQSIM": 0.3, "UGLSIM": 0.05} |
|      5 |       0.0973401 |    0.228554 |  -0.865303 |      0.803845 |        1.11544 |      0.264132 |                   2.63399 |        -0.265136 | {"QLDSIM": 0.1, "RSSTSIM": 0.3, "TMFSIM": 0.3, "TQQQSIM": 0.3}                  |
|      6 |       0.0972433 |    0.226592 |  -0.817268 |      0.84341  |        1.17766 |      0.277256 |                   2.65845 |        -0.247897 | {"QLDSIM": 0.1, "RSSTSIM": 0.35, "TMFSIM": 0.3, "TQQQSIM": 0.25}                |
|      7 |       0.0967668 |    0.229229 |  -0.906244 |      0.758061 |        1.04991 |      0.252944 |                   2.66985 |        -0.347024 | {"QLDSIM": 0.05, "RSSTSIM": 0.2, "TMFSIM": 0.35, "TQQQSIM": 0.4}                |
|      8 |       0.0967395 |    0.218985 |  -0.768598 |      0.842521 |        1.19239 |      0.284915 |                   2.72744 |        -0.27855  | {"QLDSIM": 0.15, "RSSTSIM": 0.25, "TMFSIM": 0.4, "TQQQSIM": 0.2}                |
|      9 |       0.096604  |    0.23226  |  -0.888835 |      0.791806 |        1.0914  |      0.261308 |                   2.53841 |        -0.214588 | {"QLDSIM": 0.05, "RSSTSIM": 0.35, "TMFSIM": 0.25, "TQQQSIM": 0.35}              |
|     10 |       0.0965966 |    0.222395 |  -0.782124 |      0.855346 |        1.20578 |      0.284347 |                   2.68367 |        -0.27827  | {"KMLMSIM": 0.05, "RSSTSIM": 0.3, "TMFSIM": 0.35, "TQQQSIM": 0.3}               |
|     11 |       0.0965878 |    0.221555 |  -0.826096 |      0.805022 |        1.13117 |      0.268195 |                   2.7454  |        -0.350506 | {"QLDSIM": 0.15, "RSSTSIM": 0.2, "TMFSIM": 0.4, "TQQQSIM": 0.25}                |
|     12 |       0.0965466 |    0.22031  |  -0.692503 |      0.911649 |        1.29698 |      0.318136 |                   2.70081 |        -0.178447 | {"QLDSIM": 0.05, "RSSTSIM": 0.4, "TMFSIM": 0.35, "TQQQSIM": 0.2}                |
|     13 |       0.0964582 |    0.224092 |  -0.837351 |      0.81204  |        1.13521 |      0.26762  |                   2.6859  |        -0.314125 | {"QLDSIM": 0.15, "RSSTSIM": 0.25, "TMFSIM": 0.35, "TQQQSIM": 0.25}              |
|     14 |       0.0964562 |    0.223983 |  -0.793543 |      0.851084 |        1.19558 |      0.282256 |                   2.65106 |        -0.266969 | {"RSSTSIM": 0.35, "TMFSIM": 0.3, "TQQQSIM": 0.3, "ZROZSIM": 0.05}               |
|     15 |       0.0964008 |    0.221612 |  -0.781516 |      0.851994 |        1.1996  |      0.283566 |                   2.66219 |        -0.277365 | {"QLDSIM": 0.15, "RSSTSIM": 0.3, "TMFSIM": 0.35, "TQQQSIM": 0.2}                |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   long_treasury |   managed_futures |   nasdaq_equity |   us_large_equity |   gold |
|-------:|----------------:|-------:|----------------:|------------------:|----------------:|------------------:|-------:|
|      1 |       0.0985455 |  -0.35 |            0.9  |              0.35 |            1    |              0.35 |    0   |
|      2 |       0.0980246 |  -0.3  |            0.9  |              0.3  |            1.15 |              0.3  |    0   |
|      3 |       0.0976679 |  -0.3  |            1.05 |              0.3  |            0.95 |              0.3  |    0   |
|      4 |       0.0974397 |  -0.3  |            0.9  |              0.3  |            1    |              0.3  |    0.1 |
|      5 |       0.0973401 |  -0.3  |            0.9  |              0.3  |            1.1  |              0.3  |    0   |

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
