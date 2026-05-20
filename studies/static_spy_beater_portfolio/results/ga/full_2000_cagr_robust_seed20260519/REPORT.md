# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `full_2000`
- Fitness: `cagr_robust`
- Seed: `20260519`
- Common window: `2000-01-04` to `2026-04-17`
- Unique evaluated portfolios: `680`
- GA rolling step: `126` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `20` portfolios
- Benchmark rolling step: `1`
- Generations completed: `19` / `40`
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

- Fitness value: `0.101482`
- Weights: `{"GDESIM": 0.35, "RSSTSIM": 0.05, "TMFSIM": 0.1, "TQQQSIM": 0.4, "UGLSIM": 0.1}`
- Effective exposure: `{"cash": -0.32999999999999996, "gold": 0.515, "long_treasury": 0.30000000000000004, "managed_futures": 0.05, "nasdaq_equity": 1.2000000000000002, "us_large_equity": 0.365}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                          |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:-------------------------------------------------------------------------------------------------|
|      1 |       0.101482  |    0.138147 |  -0.920741 |      0.534206 |       0.712426 |      0.150039 |                   2.81913 |        -0.263752 | {"GDESIM": 0.35, "RSSTSIM": 0.05, "TMFSIM": 0.1, "TQQQSIM": 0.4, "UGLSIM": 0.1}                  |
|      2 |       0.100323  |    0.147594 |  -0.87756  |      0.582582 |       0.783684 |      0.168187 |                   2.72706 |        -0.204583 | {"GDESIM": 0.3, "RSSTSIM": 0.05, "TMFSIM": 0.15, "TQQQSIM": 0.35, "UGLSIM": 0.15}                |
|      3 |       0.100236  |    0.15074  |  -0.873864 |      0.591086 |       0.796467 |      0.172498 |                   2.76746 |        -0.20444  | {"GDESIM": 0.3, "TMFSIM": 0.15, "TQQQSIM": 0.35, "UGLSIM": 0.2}                                  |
|      4 |       0.099823  |    0.145564 |  -0.883301 |      0.57214  |       0.768934 |      0.164795 |                   2.70861 |        -0.214063 | {"GDESIM": 0.4, "TMFSIM": 0.15, "TQQQSIM": 0.35, "UGLSIM": 0.1}                                  |
|      5 |       0.0997196 |    0.147768 |  -0.868109 |      0.587959 |       0.79512  |      0.170218 |                   2.7769  |        -0.207526 | {"GDESIM": 0.3, "TMFSIM": 0.2, "TQQQSIM": 0.35, "UGLSIM": 0.15}                                  |
|      6 |       0.0992999 |    0.145155 |  -0.87313  |      0.578057 |       0.780571 |      0.166246 |                   2.74291 |        -0.207555 | {"GDESIM": 0.35, "TMFSIM": 0.2, "TQQQSIM": 0.35, "UGLSIM": 0.1}                                  |
|      7 |       0.0992437 |    0.141555 |  -0.895406 |      0.553327 |       0.742323 |      0.158091 |                   2.67698 |        -0.240277 | {"GDESIM": 0.35, "TMFSIM": 0.15, "TQQQSIM": 0.35, "UGLSIM": 0.1, "UPROSIM": 0.05}                |
|      8 |       0.0986289 |    0.14431  |  -0.8753   |      0.574503 |       0.77552  |      0.164869 |                   2.70906 |        -0.210634 | {"GDESIM": 0.25, "SSOSIM": 0.05, "TMFSIM": 0.2, "TQQQSIM": 0.35, "UGLSIM": 0.15}                 |
|      9 |       0.0984381 |    0.134809 |  -0.922137 |      0.525806 |       0.700684 |      0.146192 |                   2.68065 |        -0.267546 | {"GDESIM": 0.35, "TMFSIM": 0.1, "TQQQSIM": 0.4, "UGLSIM": 0.1, "VTISIM": 0.05}                   |
|     10 |       0.0979028 |    0.125538 |  -0.942249 |      0.496604 |       0.658616 |      0.133232 |                   2.77439 |        -0.3024   | {"DBMFSIM": 0.05, "GDESIM": 0.35, "TMFSIM": 0.1, "TQQQSIM": 0.45, "UGLSIM": 0.05}                |
|     11 |       0.0975062 |    0.145304 |  -0.884461 |      0.57023  |       0.76382  |      0.164286 |                   2.54142 |        -0.207032 | {"GDESIM": 0.3, "RSSTSIM": 0.05, "TMFSIM": 0.1, "TQQQSIM": 0.35, "UGLSIM": 0.15, "VBRSIM": 0.05} |
|     12 |       0.0973224 |    0.14328  |  -0.895887 |      0.557829 |       0.74679  |      0.159931 |                   2.55562 |        -0.227699 | {"GDESIM": 0.3, "GLDSIM": 0.05, "TMFSIM": 0.1, "TQQQSIM": 0.35, "UGLSIM": 0.15, "UPROSIM": 0.05} |
|     13 |       0.0969605 |    0.143112 |  -0.886316 |      0.566972 |       0.758901 |      0.161469 |                   2.51268 |        -0.210798 | {"GDESIM": 0.3, "GLDSIM": 0.05, "RSSTSIM": 0.1, "TMFSIM": 0.1, "TQQQSIM": 0.35, "UGLSIM": 0.1}   |
|     14 |       0.0965515 |    0.145998 |  -0.857418 |      0.589346 |       0.797551 |      0.170276 |                   2.60866 |        -0.197301 | {"GDESIM": 0.35, "QLDSIM": 0.05, "TMFSIM": 0.2, "TQQQSIM": 0.3, "UGLSIM": 0.1}                   |
|     15 |       0.0964232 |    0.145232 |  -0.856195 |      0.589727 |       0.797605 |      0.169625 |                   2.58764 |        -0.197411 | {"GDESIM": 0.3, "QLDSIM": 0.05, "RSSTSIM": 0.05, "TMFSIM": 0.2, "TQQQSIM": 0.3, "UGLSIM": 0.1}   |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   gold |   long_treasury |   managed_futures |   nasdaq_equity |   us_large_equity |
|-------:|----------------:|-------:|-------:|----------------:|------------------:|----------------:|------------------:|
|      1 |       0.101482  |  -0.33 |  0.515 |            0.3  |              0.05 |            1.2  |             0.365 |
|      2 |       0.100323  |  -0.29 |  0.57  |            0.45 |              0.05 |            1.05 |             0.32  |
|      3 |       0.100236  |  -0.24 |  0.67  |            0.45 |              0    |            1.05 |             0.27  |
|      4 |       0.099823  |  -0.32 |  0.56  |            0.45 |              0    |            1.05 |             0.36  |
|      5 |       0.0997196 |  -0.24 |  0.57  |            0.6  |              0    |            1.05 |             0.27  |

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
