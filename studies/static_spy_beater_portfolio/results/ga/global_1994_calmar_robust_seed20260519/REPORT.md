# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `global_1994`
- Fitness: `calmar_robust`
- Seed: `20260519`
- Common window: `1994-05-05` to `2026-04-17`
- Unique evaluated portfolios: `311`
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

- Fitness value: `0.173215`
- Weights: `{"CASHX": 0.15, "EFVSIM": 0.05, "IEFSIM": 0.15, "KMLMSIM": 0.05, "NTSESIM": 0.05, "NTSXSIM": 0.05, "RSSTSIM": 0.05, "TLTSIM": 0.2, "VBRSIM": 0.05, "VEASIM": 0.05, "VXUSSIM": 0.05, "ZROZSIM": 0.1}`
- Effective exposure: `{"cash": 0.049999999999999996, "em_equity": 0.045000000000000005, "intermediate_treasury": 0.21, "intl_developed_equity": 0.05, "intl_equity": 0.05, "intl_value_equity": 0.05, "long_treasury": 0.2, "managed_futures": 0.1, "us_large_equity": 0.095, "us_small_value_equity": 0.05, "zero_coupon_treasury": 0.1}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                                                                                                                             |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 |      0.173215   |    0.072799 |  -0.215455 |      0.976347 |       1.38559  |      0.337885 |                -0.202297  |       -0.698163  | {"CASHX": 0.15, "EFVSIM": 0.05, "IEFSIM": 0.15, "KMLMSIM": 0.05, "NTSESIM": 0.05, "NTSXSIM": 0.05, "RSSTSIM": 0.05, "TLTSIM": 0.2, "VBRSIM": 0.05, "VEASIM": 0.05, "VXUSSIM": 0.05, "ZROZSIM": 0.1} |
|      2 |      0.166304   |    0.12771  |  -0.294633 |      0.981087 |       1.36831  |      0.433454 |                 0.263892  |       -0.361344  | {"EFVSIM": 0.1, "RSSTSIM": 0.4, "TLTSIM": 0.15, "TMFSIM": 0.1, "VTISIM": 0.05, "VTSIM": 0.05, "VXUSSIM": 0.15}                                                                                      |
|      3 |      0.124251   |    0.10946  |  -0.293138 |      0.934911 |       1.27262  |      0.373407 |                 0.0584392 |       -0.376153  | {"BNDSIM": 0.1, "IEFSIM": 0.1, "KMLMSIM": 0.2, "QQQSIM": 0.15, "SPYSIM": 0.05, "UGLSIM": 0.2, "UPROSIM": 0.05, "VEASIM": 0.1, "VTISIM": 0.05}                                                       |
|      4 |      0.103831   |    0.108068 |  -0.390404 |      0.893638 |       1.22465  |      0.27681  |                 0.043486  |       -0.34732   | {"BNDSIM": 0.05, "EFVSIM": 0.05, "GDESIM": 0.05, "GLDSIM": 0.05, "KMLMSIM": 0.1, "NTSXSIM": 0.05, "QLDSIM": 0.05, "QQQSIM": 0.15, "SPYSIM": 0.1, "TLTSIM": 0.2, "VBRSIM": 0.05, "VEASIM": 0.1}      |
|      5 |      0.0937742  |    0.121839 |  -0.441767 |      0.817826 |       1.14983  |      0.275799 |                 0.334051  |       -0.302364  | {"SPYSIM": 0.7, "TMFSIM": 0.3}                                                                                                                                                                      |
|      6 |      0.0865237  |    0.164862 |  -0.632507 |      0.81394  |       1.10299  |      0.260649 |                 0.685035  |       -0.0540681 | {"EFVSIM": 0.1, "QLDSIM": 0.05, "RSSBSIM": 0.1, "RSSTSIM": 0.4, "TQQQSIM": 0.1, "VBRSIM": 0.05, "VTSIM": 0.05, "VWOSIM": 0.05, "ZROZSIM": 0.1}                                                      |
|      7 |      0.079429   |    0.136014 |  -0.5217   |      0.835703 |       1.15556  |      0.260712 |                 0.394616  |       -0.0939441 | {"BNDSIM": 0.05, "CASHX": 0.05, "GDESIM": 0.05, "GLDSIM": 0.05, "QLDSIM": 0.15, "RSSBSIM": 0.15, "RSSTSIM": 0.15, "SSOSIM": 0.05, "TMFSIM": 0.05, "VEASIM": 0.15, "ZROZSIM": 0.1}                   |
|      8 |      0.0787739  |    0.157157 |  -0.505986 |      0.817018 |       1.14716  |      0.310596 |                 0.908543  |       -0.161141  | {"GLDSIM": 0.2, "RSSTSIM": 0.05, "SSOSIM": 0.4, "TMFSIM": 0.3, "TQQQSIM": 0.05}                                                                                                                     |
|      9 |      0.0419487  |    0.14249  |  -0.552111 |      0.749745 |       0.983836 |      0.258082 |                 0.318358  |       -0.0271978 | {"EFVSIM": 0.05, "IEFSIM": 0.1, "NTSXSIM": 0.2, "RSSTSIM": 0.3, "SPYSIM": 0.1, "UPROSIM": 0.15, "VTISIM": 0.05, "VWOSIM": 0.05}                                                                     |
|     10 |      0.0287523  |    0.158036 |  -0.654179 |      0.762762 |       1.02831  |      0.241579 |                 0.744383  |       -0.157922  | {"BNDSIM": 0.25, "GDESIM": 0.55, "TQQQSIM": 0.15, "UGLSIM": 0.05}                                                                                                                                   |
|     11 |      0.0280794  |    0.155037 |  -0.602309 |      0.739775 |       1.05425  |      0.257405 |                 1.18372   |       -0.318273  | {"QLDSIM": 0.3, "TMFSIM": 0.4, "VWOSIM": 0.3}                                                                                                                                                       |
|     12 |      0.0208842  |    0.128906 |  -0.567779 |      0.732475 |       0.969866 |      0.227035 |                 0.160814  |       -0.0607043 | {"GLDSIM": 0.15, "KMLMSIM": 0.25, "SPYSIM": 0.25, "SSOSIM": 0.05, "TQQQSIM": 0.05, "UPROSIM": 0.15, "VEASIM": 0.1}                                                                                  |
|     13 |      0.00981593 |    0.12107  |  -0.491823 |      0.740392 |       0.990891 |      0.246165 |                 0.243313  |       -0.166229  | {"BNDSIM": 0.1, "QLDSIM": 0.1, "QQQSIM": 0.05, "RSSBSIM": 0.5, "UGLSIM": 0.1, "VBRSIM": 0.1, "VTSIM": 0.05}                                                                                         |
|     14 |     -0.0240856  |    0.140173 |  -0.533547 |      0.733206 |       0.95888  |      0.262718 |                 0.567999  |       -0.359221  | {"GDESIM": 0.75, "NTSESIM": 0.2, "VTSIM": 0.05}                                                                                                                                                     |
|     15 |     -0.0301082  |    0.105689 |  -0.52391  |      0.678835 |       0.884893 |      0.201731 |                -0.0305352 |       -0.2052    | {"CASHX": 0.3, "GLDSIM": 0.2, "NTSESIM": 0.05, "SPYSIM": 0.15, "TQQQSIM": 0.05, "UPROSIM": 0.15, "VWOSIM": 0.05, "VXUSSIM": 0.05}                                                                   |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   em_equity |   intermediate_treasury |   intl_developed_equity |   intl_equity |   intl_value_equity |   long_treasury |   managed_futures |   us_large_equity |   us_small_value_equity |   zero_coupon_treasury |   global_equity |   us_total_equity |   aggregate_bond |   gold |   nasdaq_equity |
|-------:|----------------:|-------:|------------:|------------------------:|------------------------:|--------------:|--------------------:|----------------:|------------------:|------------------:|------------------------:|-----------------------:|----------------:|------------------:|-----------------:|-------:|----------------:|
|      1 |       0.173215  |  0.05  |       0.045 |                    0.21 |                    0.05 |          0.05 |                0.05 |            0.2  |               0.1 |             0.095 |                    0.05 |                    0.1 |            0    |              0    |             0    |  0     |            0    |
|      2 |       0.166304  | -0.4   |       0     |                    0    |                    0    |          0.15 |                0.1  |            0.45 |               0.4 |             0.4   |                    0    |                    0   |            0.05 |              0.05 |             0    |  0     |            0    |
|      3 |       0.124251  |  0     |       0     |                    0.1  |                    0.1  |          0    |                0    |            0    |               0.2 |             0.2   |                    0    |                    0   |            0    |              0.05 |             0.1  |  0.4   |            0.15 |
|      4 |       0.103831  | -0.065 |       0     |                    0.03 |                    0.1  |          0    |                0.05 |            0.2  |               0.1 |             0.19  |                    0.05 |                    0   |            0    |              0    |             0.05 |  0.095 |            0.25 |
|      5 |       0.0937742 |  0     |       0     |                    0    |                    0    |          0    |                0    |            0.9  |               0   |             0.7   |                    0    |                    0   |            0    |              0    |             0    |  0     |            0    |

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
