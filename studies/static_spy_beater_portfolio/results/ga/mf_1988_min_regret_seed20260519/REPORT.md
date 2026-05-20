# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `mf_1988`
- Fitness: `min_regret`
- Seed: `20260519`
- Common window: `1988-01-04` to `2026-04-17`
- Unique evaluated portfolios: `310`
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

- Fitness value: `-0.000000`
- Weights: `{"SPYSIM": 1.0}`
- Effective exposure: `{"us_large_equity": 1.0}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                                                                                      |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 |    -8.54872e-15 |    0.114583 |  -0.551413 |      0.691024 |       0.884039 |      0.207798 |              -1.61249e-15 |     -8.54872e-15 | {"SPYSIM": 1.0}                                                                                                                                              |
|      2 |    -0.0079744   |    0.120112 |  -0.557334 |      0.702974 |       0.904716 |      0.215511 |               0.0514294   |     -0.0079744   | {"GDESIM": 0.05, "KMLMSIM": 0.05, "SPYSIM": 0.85, "UPROSIM": 0.05}                                                                                           |
|      3 |    -0.00819062  |    0.12724  |  -0.543757 |      0.735527 |       0.952295 |      0.234001 |               0.113453    |     -0.00819062  | {"CASHX": 0.05, "NTSXSIM": 0.05, "QQQSIM": 0.05, "RSSTSIM": 0.1, "SPYSIM": 0.7, "UPROSIM": 0.05}                                                             |
|      4 |    -0.0104449   |    0.125404 |  -0.569424 |      0.709887 |       0.914573 |      0.22023  |               0.115958    |     -0.0104449   | {"GDESIM": 0.05, "NTSXSIM": 0.05, "RSSBSIM": 0.05, "RSSTSIM": 0.05, "SPYSIM": 0.7, "UPROSIM": 0.05, "VTISIM": 0.05}                                          |
|      5 |    -0.0113274   |    0.125331 |  -0.543034 |      0.73285  |       0.944282 |      0.230797 |               0.116551    |     -0.0113274   | {"GDESIM": 0.05, "RSSTSIM": 0.1, "SPYSIM": 0.7, "SSOSIM": 0.05, "VTSIM": 0.1}                                                                                |
|      6 |    -0.0113908   |    0.134349 |  -0.542333 |      0.75741  |       0.983878 |      0.247724 |               0.216229    |     -0.0113908   | {"GDESIM": 0.05, "NTSXSIM": 0.1, "RSSTSIM": 0.15, "SPYSIM": 0.6, "UPROSIM": 0.05, "VTSIM": 0.05}                                                             |
|      7 |    -0.0131403   |    0.132747 |  -0.519597 |      0.77327  |       1.00454  |      0.255481 |               0.207165    |     -0.0131403   | {"GDESIM": 0.05, "NTSXSIM": 0.05, "RSSBSIM": 0.05, "RSSTSIM": 0.15, "SPYSIM": 0.6, "SSOSIM": 0.05, "VTISIM": 0.05}                                           |
|      8 |    -0.0134631   |    0.129734 |  -0.504637 |      0.773891 |       1.00694  |      0.257083 |               0.181989    |     -0.0134631   | {"GDESIM": 0.05, "NTSXSIM": 0.1, "QQQSIM": 0.1, "RSSTSIM": 0.1, "SPYSIM": 0.6, "VTSIM": 0.05}                                                                |
|      9 |    -0.0134747   |    0.133955 |  -0.540974 |      0.761982 |       0.99294  |      0.247618 |               0.220409    |     -0.0134747   | {"BNDSIM": 0.05, "NTSXSIM": 0.2, "QQQSIM": 0.05, "RSSTSIM": 0.15, "SPYSIM": 0.2, "SSOSIM": 0.15, "VTISIM": 0.05, "VTSIM": 0.15}                              |
|     10 |    -0.014608    |    0.132463 |  -0.489145 |      0.798154 |       1.04398  |      0.270806 |               0.238964    |     -0.014608    | {"GDESIM": 0.1, "NTSXSIM": 0.2, "QQQSIM": 0.1, "RSSTSIM": 0.1, "SPYSIM": 0.35, "VTISIM": 0.1, "VTSIM": 0.05}                                                 |
|     11 |    -0.0147237   |    0.13185  |  -0.540278 |      0.756216 |       0.984624 |      0.24404  |               0.200971    |     -0.0147237   | {"NTSXSIM": 0.15, "RSSBSIM": 0.1, "RSSTSIM": 0.15, "SPYSIM": 0.4, "SSOSIM": 0.1, "VTSIM": 0.1}                                                               |
|     12 |    -0.0154021   |    0.130912 |  -0.553522 |      0.74469  |       0.967328 |      0.236508 |               0.195309    |     -0.0154021   | {"BNDSIM": 0.1, "GDESIM": 0.05, "NTSXSIM": 0.15, "QQQSIM": 0.05, "RSSTSIM": 0.1, "SPYSIM": 0.2, "SSOSIM": 0.1, "UPROSIM": 0.05, "VTISIM": 0.1, "VTSIM": 0.1} |
|     13 |    -0.0157542   |    0.128641 |  -0.540326 |      0.745134 |       0.973529 |      0.238079 |               0.181276    |     -0.0157542   | {"BNDSIM": 0.1, "GDESIM": 0.1, "QQQSIM": 0.05, "RSSTSIM": 0.05, "SPYSIM": 0.45, "SSOSIM": 0.1, "UPROSIM": 0.05, "VTISIM": 0.05, "ZROZSIM": 0.05}             |
|     14 |    -0.0160416   |    0.138944 |  -0.522502 |      0.78843  |       1.033    |      0.26592  |               0.280643    |     -0.0160416   | {"BNDSIM": 0.05, "CASHX": 0.05, "GDESIM": 0.05, "NTSXSIM": 0.2, "RSSTSIM": 0.2, "SPYSIM": 0.2, "SSOSIM": 0.2, "VTSIM": 0.05}                                 |
|     15 |    -0.016741    |    0.139675 |  -0.536225 |      0.779452 |       1.02107  |      0.260479 |               0.26788     |     -0.016741    | {"CASHX": 0.05, "NTSXSIM": 0.15, "QQQSIM": 0.1, "RSSTSIM": 0.2, "SPYSIM": 0.25, "SSOSIM": 0.05, "UPROSIM": 0.05, "VTISIM": 0.05, "VTSIM": 0.1}               |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   us_large_equity |   cash |   gold |   managed_futures |   intermediate_treasury |   nasdaq_equity |   aggregate_bond |   global_equity |   us_total_equity |
|-------:|----------------:|------------------:|-------:|-------:|------------------:|------------------------:|----------------:|-----------------:|----------------:|------------------:|
|      1 |    -8.54872e-15 |             1     |  0     |  0     |              0    |                    0    |            0    |             0    |            0    |              0    |
|      2 |    -0.0079744   |             1.045 | -0.04  |  0.045 |              0.05 |                    0    |            0    |             0    |            0    |              0    |
|      3 |    -0.00819062  |             0.995 | -0.075 |  0     |              0.1  |                    0.03 |            0.05 |             0    |            0    |              0    |
|      4 |    -0.0104449   |             0.99  | -0.165 |  0.045 |              0.05 |                    0.03 |            0    |             0.05 |            0.05 |              0.05 |
|      5 |    -0.0113274   |             0.945 | -0.14  |  0.045 |              0.1  |                    0    |            0    |             0    |            0.1  |              0    |

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
