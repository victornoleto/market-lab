# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `core_1986`
- Fitness: `balanced_spy_beater`
- Seed: `8`
- Common window: `1986-12-12` to `2026-04-17`
- Unique evaluated portfolios: `7`
- GA rolling step: `252` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `1` portfolios
- Benchmark rolling step: `1`
- Generations completed: `1` / `3`
- Early stop: `True` (`no_improvement_for_1_generations`)
- Patience: `1`, min_delta: `1e-09`

This is discovery output only. It is not a validated winner or a mandate change.
GA search breadth must be carried into later DSR/PBO accounting
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Best Portfolio

- Fitness value: `0.122788`
- Weights: `{"BNDSIM": 0.05, "IEFSIM": 0.1, "QQQSIM": 0.05, "RSSBSIM": 0.2, "SSOSIM": 0.1, "TQQQSIM": 0.05, "UGLSIM": 0.05, "UPROSIM": 0.05, "VTISIM": 0.1, "ZROZSIM": 0.25}`
- Effective exposure: `{"aggregate_bond": 0.25, "cash": -0.2, "global_equity": 0.2, "gold": 0.1, "intermediate_treasury": 0.1, "nasdaq_equity": 0.2, "us_large_equity": 0.35000000000000003, "us_total_equity": 0.1, "zero_coupon_treasury": 0.25}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                                                                                          |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 |        0.122788 |    0.121927 |  -0.447884 |      0.772279 |        1.06899 |      0.272229 |                  0.273941 |        -0.142766 | {"BNDSIM": 0.05, "IEFSIM": 0.1, "QQQSIM": 0.05, "RSSBSIM": 0.2, "SSOSIM": 0.1, "TQQQSIM": 0.05, "UGLSIM": 0.05, "UPROSIM": 0.05, "VTISIM": 0.1, "ZROZSIM": 0.25} |

## Benchmark Portfolios

| benchmark    |    cagr |       mdd |   sharpe |   sortino |   calmar |   terminal_wealth |
|:-------------|--------:|----------:|---------:|----------:|---------:|------------------:|
| equal_weight | 0.13058 | -0.549186 | 0.790668 |   1.07283 | 0.237771 |           124.828 |

## Pareto Plots

- `plots/full_cagr_vs_full_mdd.png`
- `plots/full_cagr_vs_full_sharpe.png`
- `plots/full_cagr_vs_full_calmar.png`
- `plots/fit_relative_wealth_spy_vs_full_mdd.png`
- `plots/fit_relative_wealth_qqq_vs_full_mdd.png`
- `plots/fit_balanced_spy_beater_vs_fit_min_regret.png`

## Notes

- `full_mdd` is less negative when better, so Pareto plots maximize it.
- If `finalist_exact > 0`, `top.csv` and this report use the exact re-rank with all possible rolling windows.
- `top_sampled.csv` preserves the faster GA discovery ranking.
- Relative wealth scores are rolling-window aggregate ratios minus 1 versus the named benchmark.
- The rolling score combines mean, median and p10 to penalize bad-regime fragility.
