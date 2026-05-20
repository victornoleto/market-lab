# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `mf_1988`
- Fitness: `sharpe_robust`
- Seed: `20260519`
- Common window: `1988-01-04` to `2026-04-17`
- Unique evaluated portfolios: `1362`
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

- Fitness value: `1.048157`
- Weights: `{"BNDSIM": 0.4, "CASHX": 0.45, "GLDSIM": 0.05, "KMLMSIM": 0.05, "QQQSIM": 0.05}`
- Effective exposure: `{"aggregate_bond": 0.4, "cash": 0.45, "gold": 0.05, "managed_futures": 0.05, "nasdaq_equity": 0.05}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                      |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:---------------------------------------------------------------------------------------------|
|      1 |        1.04816  |   0.0516999 | -0.0717787 |       1.96219 |        2.76044 |      0.720268 |                 -0.417219 |        -0.755958 | {"BNDSIM": 0.4, "CASHX": 0.45, "GLDSIM": 0.05, "KMLMSIM": 0.05, "QQQSIM": 0.05}              |
|      2 |        1.03402  |   0.0505736 | -0.0639167 |       1.9995  |        2.74776 |      0.791242 |                 -0.433283 |        -0.756855 | {"BNDSIM": 0.35, "CASHX": 0.5, "KMLMSIM": 0.05, "SPYSIM": 0.1}                               |
|      3 |        0.99555  |   0.0518149 | -0.0716593 |       1.92931 |        2.63093 |      0.723073 |                 -0.423614 |        -0.754938 | {"BNDSIM": 0.4, "CASHX": 0.45, "KMLMSIM": 0.05, "SPYSIM": 0.05, "VTISIM": 0.05}              |
|      4 |        0.975961 |   0.0499876 | -0.046548  |       1.96986 |        2.8231  |      1.07389  |                 -0.429902 |        -0.771938 | {"BNDSIM": 0.4, "CASHX": 0.45, "KMLMSIM": 0.1, "SPYSIM": 0.05}                               |
|      5 |        0.973193 |   0.0557535 | -0.0626503 |       1.88354 |        2.66276 |      0.889916 |                 -0.39762  |        -0.740211 | {"BNDSIM": 0.3, "CASHX": 0.4, "GLDSIM": 0.05, "IEFSIM": 0.05, "KMLMSIM": 0.1, "SPYSIM": 0.1} |
|      6 |        0.957504 |   0.0547282 | -0.0658447 |       1.89906 |        2.66048 |      0.83117  |                 -0.404514 |        -0.751517 | {"BNDSIM": 0.4, "CASHX": 0.4, "KMLMSIM": 0.1, "VTISIM": 0.1}                                 |
|      7 |        0.95659  |   0.0541417 | -0.0766003 |       1.87378 |        2.61206 |      0.706809 |                 -0.409961 |        -0.744975 | {"BNDSIM": 0.4, "CASHX": 0.45, "KMLMSIM": 0.05, "QQQSIM": 0.05, "SPYSIM": 0.05}              |
|      8 |        0.955126 |   0.0529239 | -0.0790485 |       1.86969 |        2.60987 |      0.669512 |                 -0.414677 |        -0.750967 | {"BNDSIM": 0.4, "CASHX": 0.45, "KMLMSIM": 0.05, "QQQSIM": 0.05, "VTSIM": 0.05}               |
|      9 |        0.951999 |   0.0521378 | -0.0512902 |       1.88147 |        2.65804 |      1.01653  |                 -0.414181 |        -0.760238 | {"BNDSIM": 0.4, "CASHX": 0.4, "GLDSIM": 0.05, "KMLMSIM": 0.1, "SPYSIM": 0.05}                |
|     10 |        0.936633 |   0.0546217 | -0.0664685 |       1.87807 |        2.65367 |      0.821768 |                 -0.406585 |        -0.750368 | {"BNDSIM": 0.4, "CASHX": 0.4, "KMLMSIM": 0.1, "SPYSIM": 0.1}                                 |
|     11 |        0.932259 |   0.0532682 | -0.0807693 |       1.8354  |        2.54434 |      0.659511 |                 -0.41242  |        -0.752012 | {"BNDSIM": 0.35, "CASHX": 0.4, "IEFSIM": 0.1, "KMLMSIM": 0.05, "SPYSIM": 0.1}                |
|     12 |        0.930462 |   0.0567805 | -0.0708086 |       1.82068 |        2.54907 |      0.801887 |                 -0.390012 |        -0.737359 | {"BNDSIM": 0.4, "CASHX": 0.35, "GLDSIM": 0.05, "KMLMSIM": 0.1, "SPYSIM": 0.1}                |
|     13 |        0.910407 |   0.0559164 | -0.0699643 |       1.82814 |        2.55329 |      0.799214 |                 -0.395387 |        -0.749314 | {"BNDSIM": 0.45, "CASHX": 0.35, "KMLMSIM": 0.1, "VTISIM": 0.1}                               |
|     14 |        0.907739 |   0.0569993 | -0.0719912 |       1.83907 |        2.58455 |      0.791754 |                 -0.391366 |        -0.747321 | {"BNDSIM": 0.45, "CASHX": 0.4, "KMLMSIM": 0.05, "RSSTSIM": 0.05, "SPYSIM": 0.05}             |
|     15 |        0.907581 |   0.0511744 | -0.0519053 |       1.8713  |        2.67253 |      0.98592  |                 -0.421258 |        -0.769886 | {"BNDSIM": 0.45, "CASHX": 0.4, "KMLMSIM": 0.1, "SPYSIM": 0.05}                               |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   aggregate_bond |   cash |   gold |   managed_futures |   nasdaq_equity |   us_large_equity |   us_total_equity |   intermediate_treasury |
|-------:|----------------:|-----------------:|-------:|-------:|------------------:|----------------:|------------------:|------------------:|------------------------:|
|      1 |        1.04816  |             0.4  |   0.45 |   0.05 |              0.05 |            0.05 |              0    |              0    |                    0    |
|      2 |        1.03402  |             0.35 |   0.5  |   0    |              0.05 |            0    |              0.1  |              0    |                    0    |
|      3 |        0.99555  |             0.4  |   0.45 |   0    |              0.05 |            0    |              0.05 |              0.05 |                    0    |
|      4 |        0.975961 |             0.4  |   0.45 |   0    |              0.1  |            0    |              0.05 |              0    |                    0    |
|      5 |        0.973193 |             0.3  |   0.4  |   0.05 |              0.1  |            0    |              0.1  |              0    |                    0.05 |

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
