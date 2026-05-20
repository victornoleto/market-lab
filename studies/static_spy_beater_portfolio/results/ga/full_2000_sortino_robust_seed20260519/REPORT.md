# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `full_2000`
- Fitness: `sortino_robust`
- Seed: `20260519`
- Common window: `2000-01-04` to `2026-04-17`
- Unique evaluated portfolios: `648`
- GA rolling step: `126` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `20` portfolios
- Benchmark rolling step: `1`
- Generations completed: `18` / `40`
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

- Fitness value: `0.810172`
- Weights: `{"CASHX": 0.05, "DBMFSIM": 0.05, "GLDSIM": 0.1, "IEFSIM": 0.35, "KMLMSIM": 0.1, "NTSXSIM": 0.15, "QQQSIM": 0.1, "TLTSIM": 0.1}`
- Effective exposure: `{"cash": -0.024999999999999994, "gold": 0.1, "intermediate_treasury": 0.43999999999999995, "long_treasury": 0.1, "managed_futures": 0.15000000000000002, "nasdaq_equity": 0.1, "us_large_equity": 0.135}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                                                                                                           |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 |        0.810172 |   0.0686072 |  -0.145198 |      1.08864  |        1.58026 |      0.472508 |                 -0.280546 |        -0.650883 | {"CASHX": 0.05, "DBMFSIM": 0.05, "GLDSIM": 0.1, "IEFSIM": 0.35, "KMLMSIM": 0.1, "NTSXSIM": 0.15, "QQQSIM": 0.1, "TLTSIM": 0.1}                                                    |
|      2 |        0.791362 |   0.0645112 |  -0.145642 |      1.01622  |        1.43832 |      0.442945 |                 -0.296855 |        -0.648392 | {"BNDSIM": 0.25, "CASHX": 0.1, "GLDSIM": 0.05, "IEFSIM": 0.2, "KMLMSIM": 0.05, "QQQSIM": 0.15, "RSSTSIM": 0.1, "TLTSIM": 0.1}                                                     |
|      3 |        0.775846 |   0.0762951 |  -0.143353 |      1.05696  |        1.52491 |      0.532219 |                 -0.212781 |        -0.598165 | {"DBMFSIM": 0.05, "GLDSIM": 0.1, "IEFSIM": 0.4, "KMLMSIM": 0.05, "QQQSIM": 0.1, "RSSTSIM": 0.1, "SPYSIM": 0.1, "TLTSIM": 0.05, "ZROZSIM": 0.05}                                   |
|      4 |        0.76621  |   0.056592  |  -0.154387 |      1.01657  |        1.44697 |      0.366558 |                 -0.358309 |        -0.701659 | {"BNDSIM": 0.25, "CASHX": 0.1, "GLDSIM": 0.05, "IEFSIM": 0.2, "KMLMSIM": 0.1, "QQQSIM": 0.15, "TLTSIM": 0.1, "VEASIM": 0.05}                                                      |
|      5 |        0.762582 |   0.0717073 |  -0.129172 |      1.05954  |        1.49333 |      0.55513  |                 -0.254008 |        -0.610945 | {"BNDSIM": 0.15, "CASHX": 0.05, "DBMFSIM": 0.05, "GLDSIM": 0.1, "IEFSIM": 0.15, "KMLMSIM": 0.1, "NTSXSIM": 0.05, "QQQSIM": 0.1, "RSSTSIM": 0.05, "SPYSIM": 0.1, "TLTSIM": 0.1}    |
|      6 |        0.759434 |   0.0734885 |  -0.132151 |      1.06878  |        1.51817 |      0.556096 |                 -0.243162 |        -0.610302 | {"BNDSIM": 0.1, "CASHX": 0.1, "DBMFSIM": 0.05, "GLDSIM": 0.1, "IEFSIM": 0.15, "KMLMSIM": 0.1, "NTSXSIM": 0.1, "QQQSIM": 0.1, "RSSTSIM": 0.1, "TLTSIM": 0.1}                       |
|      7 |        0.753657 |   0.0642376 |  -0.172935 |      0.952924 |        1.34872 |      0.371455 |                 -0.285658 |        -0.626986 | {"BNDSIM": 0.15, "CASHX": 0.1, "GLDSIM": 0.05, "IEFSIM": 0.15, "KMLMSIM": 0.1, "NTSXSIM": 0.1, "QQQSIM": 0.15, "SPYSIM": 0.05, "TLTSIM": 0.15}                                    |
|      8 |        0.753352 |   0.0737156 |  -0.220484 |      0.924118 |        1.3087  |      0.334336 |                 -0.192021 |        -0.572694 | {"BNDSIM": 0.05, "CASHX": 0.05, "DBMFSIM": 0.05, "GLDSIM": 0.1, "IEFSIM": 0.35, "KMLMSIM": 0.1, "QQQSIM": 0.1, "RSSTSIM": 0.05, "TLTSIM": 0.05, "TQQQSIM": 0.05, "ZROZSIM": 0.05} |
|      9 |        0.74671  |   0.0636232 |  -0.101525 |      1.09043  |        1.57771 |      0.626675 |                 -0.325151 |        -0.687326 | {"BNDSIM": 0.1, "CASHX": 0.1, "GLDSIM": 0.1, "IEFSIM": 0.2, "KMLMSIM": 0.2, "NTSXSIM": 0.1, "QQQSIM": 0.1, "TLTSIM": 0.1}                                                         |
|     10 |        0.745794 |   0.0707238 |  -0.154506 |      1.0147   |        1.4582  |      0.457742 |                 -0.254894 |        -0.623579 | {"BNDSIM": 0.05, "CASHX": 0.1, "DBMFSIM": 0.05, "EFVSIM": 0.05, "GLDSIM": 0.1, "IEFSIM": 0.15, "KMLMSIM": 0.1, "NTSXSIM": 0.1, "QQQSIM": 0.15, "TLTSIM": 0.1, "ZROZSIM": 0.05}    |
|     11 |        0.745465 |   0.0769602 |  -0.140013 |      1.06516  |        1.52295 |      0.549667 |                 -0.212494 |        -0.600636 | {"BNDSIM": 0.1, "DBMFSIM": 0.05, "GLDSIM": 0.15, "IEFSIM": 0.1, "KMLMSIM": 0.15, "NTSXSIM": 0.2, "QQQSIM": 0.1, "TLTSIM": 0.15}                                                   |
|     12 |        0.745416 |   0.0778381 |  -0.151167 |      1.03829  |        1.47474 |      0.514916 |                 -0.199895 |        -0.56861  | {"DBMFSIM": 0.05, "GLDSIM": 0.1, "IEFSIM": 0.35, "KMLMSIM": 0.1, "NTSXSIM": 0.05, "QQQSIM": 0.1, "RSSTSIM": 0.1, "SPYSIM": 0.1, "TLTSIM": 0.05}                                   |
|     13 |        0.739207 |   0.0751579 |  -0.132855 |      1.04822  |        1.50217 |      0.565716 |                 -0.224132 |        -0.604432 | {"BNDSIM": 0.1, "CASHX": 0.1, "DBMFSIM": 0.05, "GLDSIM": 0.1, "IEFSIM": 0.1, "KMLMSIM": 0.1, "NTSXSIM": 0.1, "QQQSIM": 0.1, "RSSTSIM": 0.1, "TLTSIM": 0.1, "ZROZSIM": 0.05}       |
|     14 |        0.73495  |   0.0719125 |  -0.174961 |      1.06556  |        1.5271  |      0.41102  |                 -0.25801  |        -0.637291 | {"BNDSIM": 0.1, "CASHX": 0.05, "DBMFSIM": 0.05, "GLDSIM": 0.15, "IEFSIM": 0.2, "KMLMSIM": 0.05, "NTSXSIM": 0.15, "QQQSIM": 0.1, "TLTSIM": 0.15}                                   |
|     15 |        0.734237 |   0.0790461 |  -0.150861 |      1.0548   |        1.51523 |      0.523967 |                 -0.19363  |        -0.589732 | {"BNDSIM": 0.05, "CASHX": 0.05, "DBMFSIM": 0.05, "GLDSIM": 0.15, "IEFSIM": 0.15, "KMLMSIM": 0.05, "NTSXSIM": 0.1, "QQQSIM": 0.1, "RSSTSIM": 0.1, "TLTSIM": 0.2}                   |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   gold |   intermediate_treasury |   long_treasury |   managed_futures |   nasdaq_equity |   us_large_equity |   aggregate_bond |   zero_coupon_treasury |   intl_developed_equity |
|-------:|----------------:|-------:|-------:|------------------------:|----------------:|------------------:|----------------:|------------------:|-----------------:|-----------------------:|------------------------:|
|      1 |        0.810172 | -0.025 |   0.1  |                    0.44 |            0.1  |              0.15 |            0.1  |             0.135 |             0    |                   0    |                    0    |
|      2 |        0.791362 |  0     |   0.05 |                    0.2  |            0.1  |              0.15 |            0.15 |             0.1   |             0.25 |                   0    |                    0    |
|      3 |        0.775846 | -0.1   |   0.1  |                    0.4  |            0.05 |              0.2  |            0.1  |             0.2   |             0    |                   0.05 |                    0    |
|      4 |        0.76621  |  0.1   |   0.05 |                    0.2  |            0.1  |              0.1  |            0.15 |             0     |             0.25 |                   0    |                    0.05 |
|      5 |        0.762582 | -0.025 |   0.1  |                    0.18 |            0.1  |              0.2  |            0.1  |             0.195 |             0.15 |                   0    |                    0    |

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
