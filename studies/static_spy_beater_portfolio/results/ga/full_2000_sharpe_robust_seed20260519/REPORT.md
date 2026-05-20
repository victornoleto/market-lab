# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `full_2000`
- Fitness: `sharpe_robust`
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

- Fitness value: `0.560958`
- Weights: `{"BNDSIM": 0.15, "CASHX": 0.25, "DBMFSIM": 0.1, "GLDSIM": 0.05, "IEFSIM": 0.1, "KMLMSIM": 0.1, "QQQSIM": 0.1, "TLTSIM": 0.1, "VTISIM": 0.05}`
- Effective exposure: `{"aggregate_bond": 0.15, "cash": 0.25, "gold": 0.05, "intermediate_treasury": 0.1, "long_treasury": 0.1, "managed_futures": 0.2, "nasdaq_equity": 0.1, "us_total_equity": 0.05}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                                                                                        |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 |        0.560958 |   0.0544621 | -0.0744094 |       1.19167 |        1.70214 |      0.731926 |                 -0.391709 |        -0.718409 | {"BNDSIM": 0.15, "CASHX": 0.25, "DBMFSIM": 0.1, "GLDSIM": 0.05, "IEFSIM": 0.1, "KMLMSIM": 0.1, "QQQSIM": 0.1, "TLTSIM": 0.1, "VTISIM": 0.05}                   |
|      2 |        0.535931 |   0.0633309 | -0.0883202 |       1.15836 |        1.64741 |      0.71706  |                 -0.332192 |        -0.67487  | {"BNDSIM": 0.1, "CASHX": 0.15, "DBMFSIM": 0.1, "GLDSIM": 0.1, "IEFSIM": 0.15, "KMLMSIM": 0.1, "QQQSIM": 0.1, "SPYSIM": 0.1, "TLTSIM": 0.1}                     |
|      3 |        0.530949 |   0.0651361 | -0.0939594 |       1.16991 |        1.66866 |      0.693236 |                 -0.320638 |        -0.675512 | {"BNDSIM": 0.15, "CASHX": 0.15, "DBMFSIM": 0.1, "GLDSIM": 0.1, "IEFSIM": 0.15, "KMLMSIM": 0.1, "NTSXSIM": 0.1, "QQQSIM": 0.1, "ZROZSIM": 0.05}                 |
|      4 |        0.517844 |   0.0703959 | -0.150426  |       1.02486 |        1.42355 |      0.467977 |                 -0.257282 |        -0.60223  | {"BNDSIM": 0.1, "CASHX": 0.1, "DBMFSIM": 0.2, "GLDSIM": 0.1, "IEFSIM": 0.1, "KMLMSIM": 0.05, "QQQSIM": 0.2, "SPYSIM": 0.05, "TLTSIM": 0.1}                     |
|      5 |        0.507233 |   0.0612039 | -0.0874913 |       1.14852 |        1.63414 |      0.699542 |                 -0.348591 |        -0.690518 | {"BNDSIM": 0.1, "CASHX": 0.25, "DBMFSIM": 0.1, "GDESIM": 0.05, "GLDSIM": 0.05, "IEFSIM": 0.1, "KMLMSIM": 0.1, "QQQSIM": 0.1, "RSSBSIM": 0.05, "TLTSIM": 0.1}   |
|      6 |        0.507203 |   0.0705929 | -0.123731  |       1.06207 |        1.50249 |      0.570533 |                 -0.259805 |        -0.618319 | {"BNDSIM": 0.1, "CASHX": 0.05, "DBMFSIM": 0.15, "GLDSIM": 0.1, "IEFSIM": 0.1, "KMLMSIM": 0.1, "QQQSIM": 0.15, "SPYSIM": 0.05, "TLTSIM": 0.15, "VTISIM": 0.05}  |
|      7 |        0.501741 |   0.0687098 | -0.0980612 |       1.15998 |        1.62418 |      0.700683 |                 -0.298148 |        -0.651064 | {"BNDSIM": 0.1, "CASHX": 0.1, "DBMFSIM": 0.15, "GLDSIM": 0.1, "IEFSIM": 0.1, "KMLMSIM": 0.1, "NTSXSIM": 0.1, "QQQSIM": 0.05, "TLTSIM": 0.1, "VTISIM": 0.1}     |
|      8 |        0.498172 |   0.0675117 | -0.107331  |       1.09822 |        1.54737 |      0.629003 |                 -0.2965   |        -0.643073 | {"BNDSIM": 0.1, "CASHX": 0.1, "DBMFSIM": 0.1, "GLDSIM": 0.1, "IEFSIM": 0.1, "KMLMSIM": 0.15, "QQQSIM": 0.1, "SPYSIM": 0.05, "TLTSIM": 0.1, "VTISIM": 0.1}      |
|      9 |        0.497961 |   0.0693446 | -0.124865  |       1.06586 |        1.49578 |      0.555355 |                 -0.275535 |        -0.61646  | {"BNDSIM": 0.05, "CASHX": 0.15, "DBMFSIM": 0.1, "GLDSIM": 0.1, "IEFSIM": 0.1, "KMLMSIM": 0.1, "NTSXSIM": 0.1, "QQQSIM": 0.1, "TLTSIM": 0.1, "VTISIM": 0.1}     |
|     10 |        0.496725 |   0.0644253 | -0.0830172 |       1.19069 |        1.66998 |      0.776048 |                 -0.333479 |        -0.685996 | {"BNDSIM": 0.2, "CASHX": 0.15, "DBMFSIM": 0.15, "GDESIM": 0.1, "IEFSIM": 0.1, "KMLMSIM": 0.1, "NTSXSIM": 0.05, "QQQSIM": 0.05, "TLTSIM": 0.1}                  |
|     11 |        0.495182 |   0.0701871 | -0.127902  |       1.10435 |        1.57614 |      0.548756 |                 -0.276163 |        -0.646954 | {"BNDSIM": 0.1, "CASHX": 0.1, "DBMFSIM": 0.2, "GLDSIM": 0.1, "IEFSIM": 0.15, "QQQSIM": 0.15, "TLTSIM": 0.1, "VBRSIM": 0.05, "ZROZSIM": 0.05}                   |
|     12 |        0.495168 |   0.0554035 | -0.0991983 |       1.07091 |        1.52857 |      0.558512 |                 -0.374103 |        -0.698212 | {"BNDSIM": 0.2, "CASHX": 0.15, "DBMFSIM": 0.1, "IEFSIM": 0.1, "KMLMSIM": 0.15, "QQQSIM": 0.1, "SPYSIM": 0.1, "TLTSIM": 0.1}                                    |
|     13 |        0.494828 |   0.0641451 | -0.104543  |       1.08406 |        1.5355  |      0.613574 |                 -0.317074 |        -0.654915 | {"BNDSIM": 0.1, "CASHX": 0.15, "DBMFSIM": 0.15, "GDESIM": 0.05, "IEFSIM": 0.1, "KMLMSIM": 0.15, "NTSXSIM": 0.05, "QQQSIM": 0.1, "SPYSIM": 0.05, "TLTSIM": 0.1} |
|     14 |        0.494106 |   0.0662469 | -0.113713  |       1.09073 |        1.53006 |      0.582581 |                 -0.30733  |        -0.646105 | {"BNDSIM": 0.1, "CASHX": 0.15, "DBMFSIM": 0.1, "GLDSIM": 0.1, "IEFSIM": 0.05, "KMLMSIM": 0.15, "QQQSIM": 0.1, "SPYSIM": 0.05, "TLTSIM": 0.1, "VTISIM": 0.1}    |
|     15 |        0.492906 |   0.0703198 | -0.138816  |       1.05146 |        1.50337 |      0.506569 |                 -0.258616 |        -0.623961 | {"BNDSIM": 0.05, "CASHX": 0.1, "DBMFSIM": 0.15, "IEFSIM": 0.2, "KMLMSIM": 0.05, "NTSXSIM": 0.1, "QQQSIM": 0.15, "TLTSIM": 0.15, "UGLSIM": 0.05}                |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   aggregate_bond |   cash |   gold |   intermediate_treasury |   long_treasury |   managed_futures |   nasdaq_equity |   us_total_equity |   us_large_equity |   zero_coupon_treasury |   global_equity |
|-------:|----------------:|-----------------:|-------:|-------:|------------------------:|----------------:|------------------:|----------------:|------------------:|------------------:|-----------------------:|----------------:|
|      1 |        0.560958 |             0.15 |   0.25 |  0.05  |                    0.1  |             0.1 |              0.2  |             0.1 |              0.05 |             0     |                   0    |            0    |
|      2 |        0.535931 |             0.1  |   0.15 |  0.1   |                    0.15 |             0.1 |              0.2  |             0.1 |              0    |             0.1   |                   0    |            0    |
|      3 |        0.530949 |             0.15 |   0.1  |  0.1   |                    0.21 |             0   |              0.2  |             0.1 |              0    |             0.09  |                   0.05 |            0    |
|      4 |        0.517844 |             0.1  |   0.1  |  0.1   |                    0.1  |             0.1 |              0.25 |             0.2 |              0    |             0.05  |                   0    |            0    |
|      5 |        0.507233 |             0.15 |   0.16 |  0.095 |                    0.1  |             0.1 |              0.2  |             0.1 |              0    |             0.045 |                   0    |            0.05 |

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
