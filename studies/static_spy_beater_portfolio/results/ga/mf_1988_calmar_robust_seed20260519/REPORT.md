# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `mf_1988`
- Fitness: `calmar_robust`
- Seed: `20260519`
- Common window: `1988-01-04` to `2026-04-17`
- Unique evaluated portfolios: `309`
- GA rolling step: `126` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `20` portfolios
- Benchmark rolling step: `1`
- Generations completed: `8` / `40`
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

- Fitness value: `0.362546`
- Weights: `{"BNDSIM": 0.8, "KMLMSIM": 0.15, "TLTSIM": 0.05}`
- Effective exposure: `{"aggregate_bond": 0.8, "long_treasury": 0.05, "managed_futures": 0.15}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                                                                                                                            |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 |     0.362546    |   0.0591342 |  -0.114434 |      1.194    |       1.74155  |      0.516754 |              -0.34558     |     -0.771314    | {"BNDSIM": 0.8, "KMLMSIM": 0.15, "TLTSIM": 0.05}                                                                                                                                                   |
|      2 |     0.170898    |   0.109995  |  -0.317378 |      0.964902 |       1.3809   |      0.346574 |               0.106041    |     -0.400465    | {"GLDSIM": 0.1, "KMLMSIM": 0.05, "SPYSIM": 0.4, "TLTSIM": 0.1, "TMFSIM": 0.1, "VTISIM": 0.1, "ZROZSIM": 0.15}                                                                                      |
|      3 |     0.152165    |   0.0916788 |  -0.220842 |      1.02077  |       1.42985  |      0.415134 |              -0.117247    |     -0.441861    | {"CASHX": 0.25, "GDESIM": 0.2, "GLDSIM": 0.05, "KMLMSIM": 0.05, "QQQSIM": 0.1, "SSOSIM": 0.05, "TLTSIM": 0.25, "VTSIM": 0.05}                                                                      |
|      4 |     0.124417    |   0.0758867 |  -0.187662 |      0.963737 |       1.29636  |      0.404379 |              -0.231091    |     -0.632605    | {"BNDSIM": 0.45, "CASHX": 0.05, "GLDSIM": 0.4, "RSSTSIM": 0.05, "UPROSIM": 0.05}                                                                                                                   |
|      5 |     0.112244    |   0.204254  |  -0.597665 |      0.917667 |       1.31876  |      0.341753 |               2.29159     |     -0.13542     | {"QLDSIM": 0.3, "RSSTSIM": 0.3, "TMFSIM": 0.4}                                                                                                                                                     |
|      6 |     0.106581    |   0.11318   |  -0.422278 |      0.873278 |       1.25221  |      0.268022 |               0.170372    |     -0.461464    | {"CASHX": 0.45, "GLDSIM": 0.05, "SSOSIM": 0.15, "TMFSIM": 0.3, "TQQQSIM": 0.05}                                                                                                                    |
|      7 |     0.0755701   |   0.149608  |  -0.519548 |      0.820961 |       1.09348  |      0.287958 |               0.40555     |     -0.0267718   | {"IEFSIM": 0.1, "NTSXSIM": 0.2, "RSSTSIM": 0.3, "SPYSIM": 0.1, "TLTSIM": 0.05, "UPROSIM": 0.15, "VTISIM": 0.05, "VTSIM": 0.05}                                                                     |
|      8 |     0.05303     |   0.13627   |  -0.45383  |      0.869629 |       1.25115  |      0.300267 |               0.579268    |     -0.210028    | {"GDESIM": 0.05, "IEFSIM": 0.2, "QLDSIM": 0.05, "RSSBSIM": 0.05, "SPYSIM": 0.05, "SSOSIM": 0.1, "TMFSIM": 0.2, "TQQQSIM": 0.05, "UGLSIM": 0.15, "VTSIM": 0.05, "ZROZSIM": 0.05}                    |
|      9 |     0.0436519   |   0.129614  |  -0.334345 |      0.866158 |       1.21164  |      0.387666 |               0.435862    |     -0.349611    | {"BNDSIM": 0.05, "CASHX": 0.05, "GDESIM": 0.05, "GLDSIM": 0.1, "QLDSIM": 0.1, "RSSTSIM": 0.15, "TLTSIM": 0.1, "TMFSIM": 0.05, "UGLSIM": 0.25, "UPROSIM": 0.05, "ZROZSIM": 0.05}                    |
|     10 |     0.0106458   |   0.105549  |  -0.419441 |      0.808065 |       1.09007  |      0.251642 |              -0.00620598  |     -0.319893    | {"GDESIM": 0.1, "GLDSIM": 0.1, "KMLMSIM": 0.05, "NTSXSIM": 0.05, "SSOSIM": 0.1, "TLTSIM": 0.25, "UPROSIM": 0.05, "VTSIM": 0.3}                                                                     |
|     11 |    -8.00079e-16 |   0.114583  |  -0.551413 |      0.691024 |       0.884039 |      0.207798 |              -1.61249e-15 |     -8.54872e-15 | {"SPYSIM": 1.0}                                                                                                                                                                                    |
|     12 |    -0.014596    |   0.0996421 |  -0.307475 |      0.796204 |       1.0785   |      0.324066 |               0.0393231   |     -0.610562    | {"CASHX": 0.05, "GLDSIM": 0.15, "IEFSIM": 0.05, "KMLMSIM": 0.05, "NTSXSIM": 0.05, "QQQSIM": 0.05, "RSSBSIM": 0.1, "RSSTSIM": 0.05, "SPYSIM": 0.1, "UGLSIM": 0.25, "VTISIM": 0.05, "ZROZSIM": 0.05} |
|     13 |    -0.0326343   |   0.160544  |  -0.822457 |      0.704331 |       0.95798  |      0.195201 |               0.669203    |     -0.115734    | {"GLDSIM": 0.3, "QLDSIM": 0.45, "SSOSIM": 0.1, "TLTSIM": 0.05, "ZROZSIM": 0.1}                                                                                                                     |
|     14 |    -0.032829    |   0.147225  |  -0.707095 |      0.693516 |       0.919591 |      0.208211 |               0.346321    |     -0.111255    | {"GLDSIM": 0.25, "RSSTSIM": 0.05, "SPYSIM": 0.15, "SSOSIM": 0.1, "TLTSIM": 0.15, "TQQQSIM": 0.1, "UPROSIM": 0.2}                                                                                   |
|     15 |    -0.0383916   |   0.165551  |  -0.876307 |      0.673375 |       0.906663 |      0.188919 |               0.632133    |     -0.146344    | {"BNDSIM": 0.1, "KMLMSIM": 0.1, "QLDSIM": 0.5, "QQQSIM": 0.1, "RSSBSIM": 0.05, "UGLSIM": 0.1, "VTSIM": 0.05}                                                                                       |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   aggregate_bond |   long_treasury |   managed_futures |   gold |   us_large_equity |   us_total_equity |   zero_coupon_treasury |   cash |   global_equity |   nasdaq_equity |
|-------:|----------------:|-----------------:|----------------:|------------------:|-------:|------------------:|------------------:|-----------------------:|-------:|----------------:|----------------:|
|      1 |        0.362546 |             0.8  |            0.05 |              0.15 |   0    |              0    |               0   |                   0    |   0    |            0    |             0   |
|      2 |        0.170898 |             0    |            0.4  |              0.05 |   0.1  |              0.4  |               0.1 |                   0.15 |   0    |            0    |             0   |
|      3 |        0.152165 |             0    |            0.25 |              0.05 |   0.23 |              0.28 |               0   |                   0    |   0.09 |            0.05 |             0.1 |
|      4 |        0.124417 |             0.45 |            0    |              0.05 |   0.4  |              0.2  |               0   |                   0    |   0    |            0    |             0   |
|      5 |        0.112244 |             0    |            1.2  |              0.3  |   0    |              0.3  |               0   |                   0    |  -0.3  |            0    |             0.6 |

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
