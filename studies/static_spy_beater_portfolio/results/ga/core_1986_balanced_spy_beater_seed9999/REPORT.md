# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `core_1986`
- Fitness: `balanced_spy_beater`
- Seed: `9999`
- Common window: `1986-12-12` to `2026-04-17`
- Unique evaluated portfolios: `54`
- GA rolling step: `63` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `3` portfolios
- Benchmark rolling step: `1`
- Generations completed: `3` / `3`
- Early stop: `False` (`completed_generations`)
- Patience: `5`, min_delta: `1e-09`
- Log every: `1` generations
- Eval log every: `25` unique portfolios
- Fast discovery: `True`
- Jobs: `1`

This is discovery output only. It is not a validated winner or a mandate change.
GA search breadth must be carried into later DSR/PBO accounting
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Best Portfolio

- Fitness value: `0.370320`
- Weights: `{"GDESIM": 0.25, "GLDSIM": 0.05, "QLDSIM": 0.2, "TLTSIM": 0.1, "TMFSIM": 0.05, "TQQQSIM": 0.1, "UGLSIM": 0.05, "UPROSIM": 0.05, "ZROZSIM": 0.15}`
- Effective exposure: `{"cash": -0.2, "gold": 0.375, "long_treasury": 0.25, "nasdaq_equity": 0.7000000000000001, "us_large_equity": 0.375, "zero_coupon_treasury": 0.15}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                                                                                      |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 |        0.37032  |    0.16422  |  -0.750248 |      0.745286 |       1.02526  |      0.218887 |                  0.906971 |        -0.155988 | {"GDESIM": 0.25, "GLDSIM": 0.05, "QLDSIM": 0.2, "TLTSIM": 0.1, "TMFSIM": 0.05, "TQQQSIM": 0.1, "UGLSIM": 0.05, "UPROSIM": 0.05, "ZROZSIM": 0.15}             |
|      2 |        0.32744  |    0.148063 |  -0.571408 |      0.831127 |       1.16461  |      0.259119 |                  0.7341   |        -0.137622 | {"GDESIM": 0.2, "NTSXSIM": 0.1, "QLDSIM": 0.2, "QQQSIM": 0.1, "TLTSIM": 0.15, "TMFSIM": 0.1, "UGLSIM": 0.1, "ZROZSIM": 0.05}                                 |
|      3 |        0.285317 |    0.165286 |  -0.784644 |      0.692225 |       0.919179 |      0.210651 |                  0.735487 |        -0.134477 | {"BNDSIM": 0.05, "GDESIM": 0.1, "QLDSIM": 0.2, "SPYSIM": 0.1, "TLTSIM": 0.05, "TMFSIM": 0.1, "TQQQSIM": 0.05, "UGLSIM": 0.1, "UPROSIM": 0.2, "VTISIM": 0.05} |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   gold |   long_treasury |   nasdaq_equity |   us_large_equity |   zero_coupon_treasury |   intermediate_treasury |   aggregate_bond |   us_total_equity |
|-------:|----------------:|-------:|-------:|----------------:|----------------:|------------------:|-----------------------:|------------------------:|-----------------:|------------------:|
|      1 |        0.37032  |  -0.2  |  0.375 |            0.25 |            0.7  |             0.375 |                   0.15 |                    0    |             0    |              0    |
|      2 |        0.32744  |  -0.21 |  0.38  |            0.45 |            0.5  |             0.27  |                   0.05 |                    0.06 |             0    |              0    |
|      3 |        0.285317 |  -0.08 |  0.29  |            0.35 |            0.55 |             0.79  |                   0    |                    0    |             0.05 |              0.05 |

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
