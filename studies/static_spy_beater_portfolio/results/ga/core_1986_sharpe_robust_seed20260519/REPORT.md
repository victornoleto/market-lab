# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `core_1986`
- Fitness: `sharpe_robust`
- Seed: `20260519`
- Common window: `1986-12-12` to `2026-04-17`
- Unique evaluated portfolios: `1299`
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

- Fitness value: `1.242043`
- Weights: `{"CASHX": 0.75, "IEFSIM": 0.15, "NTSXSIM": 0.1}`
- Effective exposure: `{"cash": 0.7, "intermediate_treasury": 0.21, "us_large_equity": 0.09000000000000001}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                        |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:-------------------------------------------------------------------------------|
|      1 |         1.24204 |   0.0442867 | -0.0529114 |       2.19049 |        3.04352 |      0.836997 |                 -0.469768 |        -0.756634 | {"CASHX": 0.75, "IEFSIM": 0.15, "NTSXSIM": 0.1}                                |
|      2 |         1.22018 |   0.0447967 | -0.0552455 |       2.17502 |        2.98176 |      0.810866 |                 -0.466663 |        -0.753519 | {"CASHX": 0.7, "IEFSIM": 0.2, "VTISIM": 0.1}                                   |
|      3 |         1.19945 |   0.0458906 | -0.0507857 |       2.15428 |        2.95719 |      0.903612 |                 -0.463681 |        -0.742667 | {"CASHX": 0.7, "GLDSIM": 0.05, "IEFSIM": 0.15, "VTISIM": 0.1}                  |
|      4 |         1.17244 |   0.0469869 | -0.0601442 |       2.087   |        2.87066 |      0.781236 |                 -0.455688 |        -0.740429 | {"BNDSIM": 0.05, "CASHX": 0.65, "GLDSIM": 0.05, "IEFSIM": 0.15, "VTISIM": 0.1} |
|      5 |         1.16841 |   0.0468545 | -0.0595154 |       2.09214 |        2.8309  |      0.787267 |                 -0.457217 |        -0.74098  | {"BNDSIM": 0.1, "CASHX": 0.65, "GLDSIM": 0.05, "IEFSIM": 0.1, "VTISIM": 0.1}   |
|      6 |         1.16461 |   0.0458888 | -0.0644292 |       2.08202 |        2.84929 |      0.712237 |                 -0.458731 |        -0.750632 | {"BNDSIM": 0.05, "CASHX": 0.65, "IEFSIM": 0.2, "VTISIM": 0.1}                  |
|      7 |         1.15913 |   0.0471167 | -0.060774  |       2.06616 |        2.88703 |      0.775277 |                 -0.454178 |        -0.739921 | {"CASHX": 0.65, "GLDSIM": 0.05, "IEFSIM": 0.2, "VTISIM": 0.1}                  |
|      8 |         1.13835 |   0.0460152 | -0.0653203 |       2.04462 |        2.83221 |      0.704454 |                 -0.457279 |        -0.750116 | {"CASHX": 0.65, "IEFSIM": 0.25, "VTISIM": 0.1}                                 |
|      9 |         1.12003 |   0.0427336 | -0.0648513 |       2.06453 |        2.94716 |      0.658947 |                 -0.469964 |        -0.768265 | {"CASHX": 0.65, "IEFSIM": 0.3, "VTISIM": 0.05}                                 |
|     10 |         1.09064 |   0.048333  | -0.0708729 |       1.95927 |        2.76775 |      0.681967 |                 -0.444461 |        -0.73728  | {"CASHX": 0.6, "GLDSIM": 0.05, "IEFSIM": 0.25, "VTISIM": 0.1}                  |
|     11 |         1.07915 |   0.0437948 | -0.0583451 |       2.03354 |        2.88349 |      0.750618 |                 -0.474924 |        -0.75505  | {"CASHX": 0.7, "GLDSIM": 0.05, "IEFSIM": 0.15, "VTSIM": 0.1}                   |
|     12 |         1.07761 |   0.0471018 | -0.0744262 |       1.95343 |        2.69607 |      0.632865 |                 -0.449173 |        -0.748127 | {"BNDSIM": 0.05, "CASHX": 0.6, "IEFSIM": 0.25, "VTISIM": 0.1}                  |
|     13 |         1.04303 |   0.0472238 | -0.0753115 |       1.91046 |        2.66377 |      0.627046 |                 -0.447668 |        -0.747621 | {"CASHX": 0.6, "IEFSIM": 0.3, "VTISIM": 0.1}                                   |
|     14 |         1.04061 |   0.0494182 | -0.080263  |       1.88361 |        2.64913 |      0.615703 |                 -0.43608  |        -0.735214 | {"BNDSIM": 0.05, "CASHX": 0.55, "GLDSIM": 0.05, "IEFSIM": 0.25, "VTISIM": 0.1} |
|     15 |         1.02557 |   0.0438137 | -0.0745938 |       1.92982 |        2.74115 |      0.587364 |                 -0.46205  |        -0.766426 | {"BNDSIM": 0.05, "CASHX": 0.6, "IEFSIM": 0.3, "VTISIM": 0.05}                  |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   intermediate_treasury |   us_large_equity |   us_total_equity |   gold |   aggregate_bond |
|-------:|----------------:|-------:|------------------------:|------------------:|------------------:|-------:|-----------------:|
|      1 |         1.24204 |   0.7  |                    0.21 |              0.09 |               0   |   0    |             0    |
|      2 |         1.22018 |   0.7  |                    0.2  |              0    |               0.1 |   0    |             0    |
|      3 |         1.19945 |   0.7  |                    0.15 |              0    |               0.1 |   0.05 |             0    |
|      4 |         1.17244 |   0.65 |                    0.15 |              0    |               0.1 |   0.05 |             0.05 |
|      5 |         1.16841 |   0.65 |                    0.1  |              0    |               0.1 |   0.05 |             0.1  |

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
