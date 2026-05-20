# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `core_1986`
- Fitness: `calmar_robust`
- Seed: `20260519`
- Common window: `1986-12-12` to `2026-04-17`
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

- Fitness value: `0.129118`
- Weights: `{"CASHX": 0.05, "GDESIM": 0.2, "GLDSIM": 0.05, "QQQSIM": 0.1, "SPYSIM": 0.05, "TLTSIM": 0.25, "TMFSIM": 0.25, "VTSIM": 0.05}`
- Effective exposure: `{"cash": -0.11000000000000003, "global_equity": 0.05, "gold": 0.23000000000000004, "long_treasury": 1.0, "nasdaq_equity": 0.1, "us_large_equity": 0.23000000000000004}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                                                                      |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:---------------------------------------------------------------------------------------------------------------------------------------------|
|      1 |      0.129118   |   0.114356  |  -0.449556 |      0.818552 |       1.18053  |      0.254375 |                 0.322708  |       -0.440234  | {"CASHX": 0.05, "GDESIM": 0.2, "GLDSIM": 0.05, "QQQSIM": 0.1, "SPYSIM": 0.05, "TLTSIM": 0.25, "TMFSIM": 0.25, "VTSIM": 0.05}                 |
|      2 |      0.0982835  |   0.128005  |  -0.441767 |      0.83862  |       1.1507   |      0.289756 |                 0.417319  |       -0.266973  | {"SPYSIM": 0.7, "TMFSIM": 0.3}                                                                                                               |
|      3 |      0.0781031  |   0.0784104 |  -0.257048 |      0.852507 |       1.26538  |      0.305042 |                -0.154343  |       -0.593585  | {"BNDSIM": 0.05, "GLDSIM": 0.35, "IEFSIM": 0.25, "NTSXSIM": 0.1, "VTISIM": 0.05, "ZROZSIM": 0.2}                                             |
|      4 |      0.068217   |   0.0929806 |  -0.317374 |      0.861819 |       1.14717  |      0.292969 |                -0.111378  |       -0.413767  | {"BNDSIM": 0.2, "IEFSIM": 0.3, "NTSXSIM": 0.1, "SPYSIM": 0.15, "TLTSIM": 0.05, "UPROSIM": 0.1, "VTISIM": 0.05, "ZROZSIM": 0.05}              |
|      5 |      0.0644318  |   0.150222  |  -0.519144 |      0.806556 |       1.11118  |      0.289365 |                 0.849054  |       -0.13585   | {"GLDSIM": 0.05, "NTSXSIM": 0.4, "SSOSIM": 0.2, "TMFSIM": 0.3, "TQQQSIM": 0.05}                                                              |
|      6 |      0.054648   |   0.104077  |  -0.427173 |      0.79679  |       1.1271   |      0.243641 |                 0.12307   |       -0.477409  | {"BNDSIM": 0.1, "RSSBSIM": 0.4, "TLTSIM": 0.1, "TMFSIM": 0.15, "VTISIM": 0.15, "VTSIM": 0.05, "ZROZSIM": 0.05}                               |
|      7 |      0.0160979  |   0.130585  |  -0.483129 |      0.753591 |       1.07218  |      0.270291 |                 0.507113  |       -0.142607  | {"QLDSIM": 0.1, "SPYSIM": 0.15, "SSOSIM": 0.1, "TQQQSIM": 0.05, "UGLSIM": 0.05, "VTSIM": 0.05, "ZROZSIM": 0.5}                               |
|      8 |      0.0105968  |   0.090667  |  -0.347066 |      0.839354 |       1.1046   |      0.261239 |                -0.156055  |       -0.491148  | {"BNDSIM": 0.4, "GDESIM": 0.25, "VTSIM": 0.35}                                                                                               |
|      9 |      0.00151371 |   0.165923  |  -0.590851 |      0.784137 |       1.1423   |      0.28082  |                 1.59081   |       -0.213472  | {"QLDSIM": 0.3, "TMFSIM": 0.4, "UGLSIM": 0.3}                                                                                                |
|     10 |     -0.00359336 |   0.144024  |  -0.632154 |      0.728099 |       0.94609  |      0.227831 |                 0.425819  |       -0.0632004 | {"GDESIM": 0.2, "NTSXSIM": 0.5, "RSSBSIM": 0.05, "TQQQSIM": 0.1, "VTISIM": 0.15}                                                             |
|     11 |     -0.040569   |   0.14643   |  -0.829711 |      0.657356 |       0.866503 |      0.176483 |                 0.362732  |       -0.108464  | {"QQQSIM": 1.0}                                                                                                                              |
|     12 |     -0.0416217  |   0.153028  |  -0.821923 |      0.676648 |       0.918102 |      0.186182 |                 0.599422  |       -0.167822  | {"CASHX": 0.05, "IEFSIM": 0.05, "QLDSIM": 0.3, "RSSBSIM": 0.05, "TLTSIM": 0.05, "TQQQSIM": 0.1, "VTISIM": 0.1, "VTSIM": 0.1, "ZROZSIM": 0.2} |
|     13 |     -0.0463676  |   0.0815078 |  -0.424109 |      0.648286 |       0.966374 |      0.192186 |                -0.0504887 |       -0.608438  | {"GLDSIM": 0.15, "NTSXSIM": 0.05, "QLDSIM": 0.05, "TLTSIM": 0.45, "ZROZSIM": 0.3}                                                            |
|     14 |     -0.0490384  |   0.0982476 |  -0.543644 |      0.638984 |       0.93359  |      0.180721 |                 0.208118  |       -0.600146  | {"IEFSIM": 0.15, "RSSBSIM": 0.05, "SPYSIM": 0.15, "TLTSIM": 0.1, "TMFSIM": 0.25, "UGLSIM": 0.05, "VTSIM": 0.05, "ZROZSIM": 0.2}              |
|     15 |     -0.0709217  |   0.163293  |  -0.886451 |      0.618272 |       0.80373  |      0.18421  |                 0.471262  |       -0.303233  | {"GLDSIM": 0.1, "IEFSIM": 0.05, "NTSXSIM": 0.25, "SSOSIM": 0.15, "TQQQSIM": 0.25, "UPROSIM": 0.1, "VTISIM": 0.1}                             |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   global_equity |   gold |   long_treasury |   nasdaq_equity |   us_large_equity |   aggregate_bond |   intermediate_treasury |   us_total_equity |   zero_coupon_treasury |
|-------:|----------------:|-------:|----------------:|-------:|----------------:|----------------:|------------------:|-----------------:|------------------------:|------------------:|-----------------------:|
|      1 |       0.129118  |  -0.11 |            0.05 |   0.23 |            1    |            0.1  |              0.23 |             0    |                    0    |              0    |                   0    |
|      2 |       0.0982835 |   0    |            0    |   0    |            0.9  |            0    |              0.7  |             0    |                    0    |              0    |                   0    |
|      3 |       0.0781031 |  -0.05 |            0    |   0.35 |            0    |            0    |              0.09 |             0.05 |                    0.31 |              0.05 |                   0.2  |
|      4 |       0.068217  |  -0.05 |            0    |   0    |            0.05 |            0    |              0.54 |             0.2  |                    0.36 |              0.05 |                   0.05 |
|      5 |       0.0644318 |  -0.2  |            0    |   0.05 |            0.9  |            0.15 |              0.76 |             0    |                    0.24 |              0    |                   0    |

## Benchmark Portfolios

| benchmark    |     cagr |       mdd |   sharpe |   sortino |   calmar |   terminal_wealth |
|:-------------|---------:|----------:|---------:|----------:|---------:|------------------:|
| equal_weight | 0.13058  | -0.549186 | 0.790668 |  1.07283  | 0.237771 |          124.828  |
| qqq_buy_hold | 0.14643  | -0.829711 | 0.657356 |  0.866503 | 0.176483 |          215.827  |
| spy_buy_hold | 0.112119 | -0.551413 | 0.666451 |  0.823533 | 0.203331 |           65.3281 |

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
