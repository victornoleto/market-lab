# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `core_1986`
- Fitness: `balanced_spy_beater`
- Seed: `20260519`
- Common window: `1986-12-12` to `2026-04-17`
- Unique evaluated portfolios: `771`
- GA rolling step: `126` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `20` portfolios
- Benchmark rolling step: `1`
- Generations completed: `25` / `40`
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

- Fitness value: `1.232854`
- Weights: `{"TMFSIM": 0.6, "TQQQSIM": 0.4}`
- Effective exposure: `{"long_treasury": 1.7999999999999998, "nasdaq_equity": 1.2000000000000002}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                           |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:--------------------------------------------------|
|      1 |         1.23285 |    0.206552 |  -0.842819 |      0.707829 |       1.00227  |      0.245073 |                   3.0471  |        -0.417577 | {"TMFSIM": 0.6, "TQQQSIM": 0.4}                   |
|      2 |         1.22906 |    0.199776 |  -0.77864  |      0.706825 |       1.00956  |      0.25657  |                   3.02932 |        -0.312321 | {"TMFSIM": 0.65, "TQQQSIM": 0.35}                 |
|      3 |         1.20925 |    0.204134 |  -0.824505 |      0.711463 |       1.00971  |      0.247583 |                   2.98353 |        -0.383502 | {"QLDSIM": 0.05, "TMFSIM": 0.6, "TQQQSIM": 0.35}  |
|      4 |         1.19362 |    0.196875 |  -0.764987 |      0.708645 |       1.01425  |      0.257357 |                   2.93742 |        -0.28986  | {"QLDSIM": 0.05, "TMFSIM": 0.65, "TQQQSIM": 0.3}  |
|      5 |         1.19003 |    0.191143 |  -0.783147 |      0.695731 |       1.00187  |      0.24407  |                   2.92951 |        -0.332265 | {"TMFSIM": 0.7, "TQQQSIM": 0.3}                   |
|      6 |         1.18976 |    0.201717 |  -0.791214 |      0.719987 |       1.02442  |      0.254946 |                   2.92624 |        -0.330164 | {"GDESIM": 0.05, "TMFSIM": 0.6, "TQQQSIM": 0.35}  |
|      7 |         1.18182 |    0.201553 |  -0.804297 |      0.714927 |       1.01651  |      0.250595 |                   2.9103  |        -0.354882 | {"QLDSIM": 0.1, "TMFSIM": 0.6, "TQQQSIM": 0.3}    |
|      8 |         1.18135 |    0.211415 |  -0.890207 |      0.700904 |       0.982948 |      0.237489 |                   2.93047 |        -0.499819 | {"TMFSIM": 0.55, "TQQQSIM": 0.45}                 |
|      9 |         1.17696 |    0.206859 |  -0.847154 |      0.718312 |       1.01482  |      0.244181 |                   2.90427 |        -0.423828 | {"TMFSIM": 0.55, "TQQQSIM": 0.4, "UGLSIM": 0.05}  |
|     10 |         1.17124 |    0.201209 |  -0.804545 |      0.714272 |       1.01558  |      0.25009  |                   2.88484 |        -0.356264 | {"QQQSIM": 0.05, "TMFSIM": 0.6, "TQQQSIM": 0.35}  |
|     11 |         1.17083 |    0.209494 |  -0.87692  |      0.705558 |       0.99138  |      0.238897 |                   2.8993  |        -0.482263 | {"QLDSIM": 0.05, "TMFSIM": 0.55, "TQQQSIM": 0.4}  |
|     12 |         1.1705  |    0.201718 |  -0.801053 |      0.714146 |       1.01322  |      0.251816 |                   2.88267 |        -0.353565 | {"SSOSIM": 0.05, "TMFSIM": 0.6, "TQQQSIM": 0.35}  |
|     13 |         1.16081 |    0.207406 |  -0.862193 |      0.710226 |       1.00002  |      0.240557 |                   2.86928 |        -0.456219 | {"QLDSIM": 0.1, "TMFSIM": 0.55, "TQQQSIM": 0.35}  |
|     14 |         1.15759 |    0.195542 |  -0.766382 |      0.708121 |       1.01131  |      0.25515  |                   2.84618 |        -0.278932 | {"TMFSIM": 0.65, "TQQQSIM": 0.3, "UPROSIM": 0.05} |
|     15 |         1.15711 |    0.193814 |  -0.760711 |      0.71005  |       1.01837  |      0.254781 |                   2.84269 |        -0.285717 | {"QLDSIM": 0.1, "TMFSIM": 0.65, "TQQQSIM": 0.25}  |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   long_treasury |   nasdaq_equity |
|-------:|----------------:|----------------:|----------------:|
|      1 |         1.23285 |            1.8  |            1.2  |
|      2 |         1.22906 |            1.95 |            1.05 |
|      3 |         1.20925 |            1.8  |            1.15 |
|      4 |         1.19362 |            1.95 |            1    |
|      5 |         1.19003 |            2.1  |            0.9  |

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
