# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `full_2000`
- Fitness: `min_regret`
- Seed: `20260519`
- Common window: `2000-01-04` to `2026-04-17`
- Unique evaluated portfolios: `482`
- GA rolling step: `126` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `20` portfolios
- Benchmark rolling step: `1`
- Generations completed: `13` / `40`
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

- Fitness value: `-0.021865`
- Weights: `{"GDESIM": 0.1, "RSSBSIM": 0.1, "RSSTSIM": 0.25, "SPYSIM": 0.4, "SSOSIM": 0.15}`
- Effective exposure: `{"aggregate_bond": 0.1, "cash": -0.43000000000000005, "global_equity": 0.1, "gold": 0.09000000000000001, "managed_futures": 0.25, "us_large_equity": 1.04}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                                                                                                          |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 |      -0.0218654 |   0.10939   |  -0.535973 |      0.596198 |       0.777101 |      0.204096 |                  0.340843 |       -0.0218654 | {"GDESIM": 0.1, "RSSBSIM": 0.1, "RSSTSIM": 0.25, "SPYSIM": 0.4, "SSOSIM": 0.15}                                                                                                  |
|      2 |      -0.0219566 |   0.113451  |  -0.557352 |      0.610025 |       0.797475 |      0.203554 |                  0.418476 |       -0.0219566 | {"GDESIM": 0.1, "IEFSIM": 0.05, "NTSXSIM": 0.15, "RSSTSIM": 0.2, "SPYSIM": 0.1, "SSOSIM": 0.1, "UPROSIM": 0.1, "VBRSIM": 0.1, "VTISIM": 0.05, "ZROZSIM": 0.05}                   |
|      3 |      -0.0231137 |   0.110174  |  -0.542247 |      0.620155 |       0.807069 |      0.203181 |                  0.310912 |       -0.0231137 | {"DBMFSIM": 0.1, "GDESIM": 0.1, "GLDSIM": 0.1, "NTSXSIM": 0.1, "RSSBSIM": 0.1, "RSSTSIM": 0.1, "SPYSIM": 0.1, "SSOSIM": 0.1, "UPROSIM": 0.1, "VTISIM": 0.05, "VTSIM": 0.05}      |
|      4 |      -0.0232856 |   0.100015  |  -0.560398 |      0.55506  |       0.720216 |      0.178471 |                  0.233889 |       -0.0232856 | {"GDESIM": 0.05, "KMLMSIM": 0.1, "QQQSIM": 0.05, "RSSBSIM": 0.1, "RSSTSIM": 0.1, "SPYSIM": 0.3, "SSOSIM": 0.25, "VBRSIM": 0.05}                                                  |
|      5 |      -0.0240403 |   0.106511  |  -0.506512 |      0.627686 |       0.822644 |      0.210284 |                  0.25244  |       -0.0240403 | {"IEFSIM": 0.1, "NTSXSIM": 0.15, "QQQSIM": 0.05, "RSSTSIM": 0.2, "SPYSIM": 0.1, "UGLSIM": 0.05, "UPROSIM": 0.1, "VBRSIM": 0.1, "VTISIM": 0.1, "VXUSSIM": 0.05}                   |
|      6 |      -0.0241182 |   0.10853   |  -0.533932 |      0.601042 |       0.787342 |      0.203265 |                  0.369946 |       -0.0241182 | {"GDESIM": 0.1, "IEFSIM": 0.1, "NTSXSIM": 0.15, "QQQSIM": 0.05, "RSSBSIM": 0.05, "RSSTSIM": 0.2, "SPYSIM": 0.15, "SSOSIM": 0.15, "UPROSIM": 0.05}                                |
|      7 |      -0.0244586 |   0.115875  |  -0.511093 |      0.646646 |       0.848315 |      0.226721 |                  0.403529 |       -0.0244586 | {"DBMFSIM": 0.05, "GDESIM": 0.1, "GLDSIM": 0.1, "NTSXSIM": 0.15, "RSSBSIM": 0.05, "RSSTSIM": 0.2, "SPYSIM": 0.15, "SSOSIM": 0.15, "UPROSIM": 0.05}                               |
|      8 |      -0.0250348 |   0.108907  |  -0.512064 |      0.619852 |       0.816924 |      0.212682 |                  0.374311 |       -0.0250348 | {"GDESIM": 0.1, "IEFSIM": 0.1, "NTSXSIM": 0.15, "QQQSIM": 0.1, "RSSTSIM": 0.2, "SPYSIM": 0.1, "SSOSIM": 0.05, "TLTSIM": 0.05, "UPROSIM": 0.1, "VBRSIM": 0.05}                    |
|      9 |      -0.0252053 |   0.101756  |  -0.538353 |      0.575812 |       0.750951 |      0.189013 |                  0.248593 |       -0.0252053 | {"IEFSIM": 0.1, "NTSXSIM": 0.15, "RSSBSIM": 0.05, "RSSTSIM": 0.25, "SPYSIM": 0.2, "SSOSIM": 0.15, "UPROSIM": 0.05, "VWOSIM": 0.05}                                               |
|     10 |      -0.0256564 |   0.109162  |  -0.502622 |      0.630873 |       0.832104 |      0.217185 |                  0.379003 |       -0.0256564 | {"DBMFSIM": 0.1, "GDESIM": 0.1, "NTSXSIM": 0.15, "RSSTSIM": 0.15, "SPYSIM": 0.2, "SSOSIM": 0.1, "TQQQSIM": 0.05, "VBRSIM": 0.05, "VTSIM": 0.05, "ZROZSIM": 0.05}                 |
|     11 |      -0.0256734 |   0.104714  |  -0.547013 |      0.592996 |       0.772871 |      0.191428 |                  0.236682 |       -0.0256734 | {"GLDSIM": 0.05, "IEFSIM": 0.1, "NTSXSIM": 0.15, "RSSTSIM": 0.25, "SPYSIM": 0.1, "UPROSIM": 0.15, "VBRSIM": 0.1, "VXUSSIM": 0.1}                                                 |
|     12 |      -0.0257381 |   0.104341  |  -0.547718 |      0.590694 |       0.7722   |      0.190502 |                  0.286651 |       -0.0257381 | {"GDESIM": 0.1, "IEFSIM": 0.1, "KMLMSIM": 0.1, "NTSXSIM": 0.1, "RSSTSIM": 0.1, "SPYSIM": 0.1, "SSOSIM": 0.2, "TLTSIM": 0.05, "UPROSIM": 0.1, "VBRSIM": 0.05}                     |
|     13 |      -0.0259248 |   0.108472  |  -0.508341 |      0.624704 |       0.822881 |      0.213385 |                  0.368451 |       -0.0259248 | {"DBMFSIM": 0.1, "GDESIM": 0.1, "NTSXSIM": 0.1, "RSSTSIM": 0.15, "SPYSIM": 0.25, "SSOSIM": 0.1, "TQQQSIM": 0.05, "VBRSIM": 0.05, "VTSIM": 0.05, "ZROZSIM": 0.05}                 |
|     14 |      -0.0259878 |   0.0948653 |  -0.574211 |      0.544308 |       0.703909 |      0.16521  |                  0.165068 |       -0.0259878 | {"DBMFSIM": 0.05, "EFVSIM": 0.05, "IEFSIM": 0.1, "NTSXSIM": 0.2, "QQQSIM": 0.05, "RSSBSIM": 0.05, "RSSTSIM": 0.1, "SPYSIM": 0.15, "SSOSIM": 0.1, "UPROSIM": 0.1, "VWOSIM": 0.05} |
|     15 |      -0.0267626 |   0.109849  |  -0.611196 |      0.56759  |       0.733837 |      0.179728 |                  0.349898 |       -0.0267626 | {"IEFSIM": 0.05, "NTSXSIM": 0.1, "RSSTSIM": 0.15, "SPYSIM": 0.1, "SSOSIM": 0.15, "UGLSIM": 0.05, "UPROSIM": 0.1, "VBRSIM": 0.15, "VTISIM": 0.15}                                 |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   aggregate_bond |   cash |   global_equity |   gold |   managed_futures |   us_large_equity |   intermediate_treasury |   us_small_value_equity |   us_total_equity |   zero_coupon_treasury |   nasdaq_equity |   intl_equity |
|-------:|----------------:|-----------------:|-------:|----------------:|-------:|------------------:|------------------:|------------------------:|------------------------:|------------------:|-----------------------:|----------------:|--------------:|
|      1 |      -0.0218654 |              0.1 | -0.43  |            0.1  |  0.09  |              0.25 |             1.04  |                    0    |                    0    |              0    |                   0    |            0    |          0    |
|      2 |      -0.0219566 |              0   | -0.355 |            0    |  0.09  |              0.2  |             1.025 |                    0.14 |                    0.1  |              0.05 |                   0.05 |            0    |          0    |
|      3 |      -0.0231137 |              0.1 | -0.33  |            0.15 |  0.19  |              0.2  |             0.88  |                    0.06 |                    0    |              0.05 |                   0    |            0    |          0    |
|      4 |      -0.0232856 |              0.1 | -0.24  |            0.1  |  0.045 |              0.2  |             0.945 |                    0    |                    0.05 |              0    |                   0    |            0.05 |          0    |
|      5 |      -0.0240403 |              0   | -0.275 |            0    |  0.1   |              0.2  |             0.735 |                    0.19 |                    0.1  |              0.1  |                   0    |            0.05 |          0.05 |

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
