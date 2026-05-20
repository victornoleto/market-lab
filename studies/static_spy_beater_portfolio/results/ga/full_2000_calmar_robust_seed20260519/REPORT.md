# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `full_2000`
- Fitness: `calmar_robust`
- Seed: `20260519`
- Common window: `2000-01-04` to `2026-04-17`
- Unique evaluated portfolios: `312`
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

- Fitness value: `0.221941`
- Weights: `{"BNDSIM": 0.05, "DBMFSIM": 0.05, "GDESIM": 0.05, "GLDSIM": 0.05, "KMLMSIM": 0.1, "NTSXSIM": 0.05, "QLDSIM": 0.05, "QQQSIM": 0.15, "RSSTSIM": 0.1, "SPYSIM": 0.1, "TLTSIM": 0.2, "VBRSIM": 0.05}`
- Effective exposure: `{"aggregate_bond": 0.05, "cash": -0.165, "gold": 0.095, "intermediate_treasury": 0.03, "long_treasury": 0.2, "managed_futures": 0.25, "nasdaq_equity": 0.25, "us_large_equity": 0.29000000000000004, "us_small_value_equity": 0.05}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                                                                                                                          |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 |      0.221941   |   0.0922362 |  -0.365478 |      0.786739 |       1.0798   |      0.252371 |                 0.0483488 |       -0.279517  | {"BNDSIM": 0.05, "DBMFSIM": 0.05, "GDESIM": 0.05, "GLDSIM": 0.05, "KMLMSIM": 0.1, "NTSXSIM": 0.05, "QLDSIM": 0.05, "QQQSIM": 0.15, "RSSTSIM": 0.1, "SPYSIM": 0.1, "TLTSIM": 0.2, "VBRSIM": 0.05} |
|      2 |      0.171993   |   0.120846  |  -0.478215 |      0.713779 |       0.991405 |      0.252703 |                 0.474104  |       -0.116486  | {"QLDSIM": 0.05, "RSSBSIM": 0.15, "RSSTSIM": 0.7, "ZROZSIM": 0.1}                                                                                                                                |
|      3 |      0.120098   |   0.112575  |  -0.60658  |      0.621699 |       0.843014 |      0.18559  |                 0.570642  |       -0.0735561 | {"DBMFSIM": 0.1, "QLDSIM": 0.05, "RSSBSIM": 0.1, "RSSTSIM": 0.4, "TQQQSIM": 0.1, "VBRSIM": 0.05, "VTSIM": 0.05, "VXUSSIM": 0.05, "ZROZSIM": 0.1}                                                 |
|      4 |      0.117942   |   0.100913  |  -0.303094 |      0.829546 |       1.1267   |      0.332944 |                 0.0150891 |       -0.415364  | {"BNDSIM": 0.1, "IEFSIM": 0.1, "KMLMSIM": 0.2, "QQQSIM": 0.15, "SPYSIM": 0.05, "UGLSIM": 0.2, "UPROSIM": 0.05, "VTISIM": 0.05, "VWOSIM": 0.1}                                                    |
|      5 |      0.101467   |   0.0787457 |  -0.243818 |      0.839219 |       1.14414  |      0.322968 |                -0.210505  |       -0.594522  | {"CASHX": 0.05, "DBMFSIM": 0.05, "EFVSIM": 0.1, "IEFSIM": 0.2, "KMLMSIM": 0.05, "NTSESIM": 0.05, "NTSXSIM": 0.05, "RSSTSIM": 0.15, "VBRSIM": 0.05, "VEASIM": 0.05, "VTSIM": 0.1, "ZROZSIM": 0.1} |
|      6 |      0.0887101  |   0.134174  |  -0.654179 |      0.663043 |       0.885459 |      0.205103 |                 0.925311  |       -0.116799  | {"BNDSIM": 0.25, "GDESIM": 0.55, "TQQQSIM": 0.15, "UGLSIM": 0.05}                                                                                                                                |
|      7 |      0.0702328  |   0.125091  |  -0.505986 |      0.683532 |       0.94984  |      0.247221 |                 0.788673  |       -0.24874   | {"GLDSIM": 0.2, "RSSTSIM": 0.05, "SSOSIM": 0.4, "TMFSIM": 0.3, "TQQQSIM": 0.05}                                                                                                                  |
|      8 |      0.050126   |   0.0972425 |  -0.441767 |      0.680122 |       0.945794 |      0.220121 |                 0.154013  |       -0.334287  | {"SPYSIM": 0.7, "TMFSIM": 0.3}                                                                                                                                                                   |
|      9 |      0.0380605  |   0.10535   |  -0.547983 |      0.580847 |       0.760133 |      0.19225  |                 0.30204   |       -0.0283325 | {"IEFSIM": 0.1, "NTSXSIM": 0.2, "RSSTSIM": 0.3, "SPYSIM": 0.1, "UPROSIM": 0.15, "VBRSIM": 0.05, "VTISIM": 0.05, "VXUSSIM": 0.05}                                                                 |
|     10 |      0.0281788  |   0.144091  |  -0.533547 |      0.725139 |       0.953987 |      0.270062 |                 0.669533  |       -0.233056  | {"GDESIM": 0.75, "NTSESIM": 0.2, "VTSIM": 0.05}                                                                                                                                                  |
|     11 |      0.0273081  |   0.0950398 |  -0.567779 |      0.565404 |       0.746148 |      0.167389 |                 0.165434  |       -0.0551122 | {"GLDSIM": 0.15, "KMLMSIM": 0.25, "SPYSIM": 0.25, "SSOSIM": 0.05, "TQQQSIM": 0.05, "UPROSIM": 0.15, "VEASIM": 0.1}                                                                               |
|     12 |      0.0169008  |   0.101323  |  -0.491823 |      0.621611 |       0.828305 |      0.206015 |                 0.189575  |       -0.169899  | {"BNDSIM": 0.1, "QLDSIM": 0.1, "QQQSIM": 0.05, "RSSBSIM": 0.5, "UGLSIM": 0.1, "VBRSIM": 0.1, "VTSIM": 0.05}                                                                                      |
|     13 |     -0.00310814 |   0.108758  |  -0.695992 |      0.544999 |       0.721291 |      0.156264 |                 0.43594   |       -0.0930414 | {"GDESIM": 0.35, "NTSESIM": 0.1, "QLDSIM": 0.2, "VEASIM": 0.35}                                                                                                                                  |
|     14 |     -0.0104716  |   0.0868539 |  -0.396688 |      0.695674 |       0.908082 |      0.218948 |                -0.120792  |       -0.484701  | {"BNDSIM": 0.15, "DBMFSIM": 0.1, "GDESIM": 0.05, "RSSBSIM": 0.05, "RSSTSIM": 0.05, "SSOSIM": 0.1, "TLTSIM": 0.1, "UGLSIM": 0.05, "VBRSIM": 0.05, "VEASIM": 0.15, "VWOSIM": 0.1, "VXUSSIM": 0.05} |
|     15 |     -0.0118284  |   0.0844226 |  -0.518512 |      0.557324 |       0.725021 |      0.162817 |                -0.0304867 |       -0.200127  | {"CASHX": 0.3, "EFVSIM": 0.05, "GLDSIM": 0.2, "NTSESIM": 0.05, "SPYSIM": 0.15, "TQQQSIM": 0.05, "UPROSIM": 0.15, "VXUSSIM": 0.05}                                                                |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   aggregate_bond |   cash |   gold |   intermediate_treasury |   long_treasury |   managed_futures |   nasdaq_equity |   us_large_equity |   us_small_value_equity |   global_equity |   zero_coupon_treasury |   intl_equity |   em_equity |   us_total_equity |   intl_developed_equity |   intl_value_equity |
|-------:|----------------:|-----------------:|-------:|-------:|------------------------:|----------------:|------------------:|----------------:|------------------:|------------------------:|----------------:|-----------------------:|--------------:|------------:|------------------:|------------------------:|--------------------:|
|      1 |        0.221941 |             0.05 | -0.165 |  0.095 |                    0.03 |             0.2 |              0.25 |            0.25 |             0.29  |                    0.05 |            0    |                    0   |          0    |       0     |              0    |                    0    |                 0   |
|      2 |        0.171993 |             0.15 | -0.85  |  0     |                    0    |             0   |              0.7  |            0.1  |             0.7   |                    0    |            0.15 |                    0.1 |          0    |       0     |              0    |                    0    |                 0   |
|      3 |        0.120098 |             0.1  | -0.5   |  0     |                    0    |             0   |              0.5  |            0.4  |             0.4   |                    0.05 |            0.15 |                    0.1 |          0.05 |       0     |              0    |                    0    |                 0   |
|      4 |        0.117942 |             0.1  |  0     |  0.4   |                    0.1  |             0   |              0.2  |            0.15 |             0.2   |                    0    |            0    |                    0   |          0    |       0.1   |              0.05 |                    0    |                 0   |
|      5 |        0.101467 |             0    | -0.15  |  0     |                    0.26 |             0   |              0.25 |            0    |             0.195 |                    0.05 |            0.1  |                    0.1 |          0    |       0.045 |              0    |                    0.05 |                 0.1 |

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
