# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `core_1986`
- Fitness: `cagr_robust`
- Seed: `20260519`
- Common window: `1986-12-12` to `2026-04-17`
- Unique evaluated portfolios: `891`
- GA rolling step: `126` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `20` portfolios
- Benchmark rolling step: `1`
- Generations completed: `27` / `40`
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

- Fitness value: `0.097768`
- Weights: `{"TMFSIM": 0.6, "TQQQSIM": 0.4}`
- Effective exposure: `{"long_treasury": 1.7999999999999998, "nasdaq_equity": 1.2000000000000002}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                           |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:------------------------------------------------------------------|
|      1 |       0.0977684 |    0.206552 |  -0.842819 |      0.707829 |       1.00227  |      0.245073 |                   3.0471  |        -0.417577 | {"TMFSIM": 0.6, "TQQQSIM": 0.4}                                   |
|      2 |       0.0966711 |    0.207863 |  -0.852327 |      0.716075 |       1.00928  |      0.243877 |                   2.91099 |        -0.436308 | {"GDESIM": 0.05, "TMFSIM": 0.55, "TQQQSIM": 0.4}                  |
|      3 |       0.0965207 |    0.204134 |  -0.824505 |      0.711463 |       1.00971  |      0.247583 |                   2.98353 |        -0.383502 | {"QLDSIM": 0.05, "TMFSIM": 0.6, "TQQQSIM": 0.35}                  |
|      4 |       0.0964474 |    0.206859 |  -0.847154 |      0.718312 |       1.01482  |      0.244181 |                   2.90427 |        -0.423828 | {"TMFSIM": 0.55, "TQQQSIM": 0.4, "UGLSIM": 0.05}                  |
|      5 |       0.0961935 |    0.211415 |  -0.890207 |      0.700904 |       0.982948 |      0.237489 |                   2.93047 |        -0.499819 | {"TMFSIM": 0.55, "TQQQSIM": 0.45}                                 |
|      6 |       0.0958205 |    0.209494 |  -0.87692  |      0.705558 |       0.99138  |      0.238897 |                   2.8993  |        -0.482263 | {"QLDSIM": 0.05, "TMFSIM": 0.55, "TQQQSIM": 0.4}                  |
|      7 |       0.095743  |    0.205525 |  -0.835016 |      0.720792 |       1.01816  |      0.246133 |                   2.85369 |        -0.402274 | {"GDESIM": 0.05, "QLDSIM": 0.05, "TMFSIM": 0.55, "TQQQSIM": 0.35} |
|      8 |       0.0955657 |    0.207406 |  -0.862193 |      0.710226 |       1.00002  |      0.240557 |                   2.86928 |        -0.456219 | {"QLDSIM": 0.1, "TMFSIM": 0.55, "TQQQSIM": 0.35}                  |
|      9 |       0.095125  |    0.207522 |  -0.859522 |      0.709324 |       0.997108 |      0.241439 |                   2.83796 |        -0.456644 | {"SSOSIM": 0.05, "TMFSIM": 0.55, "TQQQSIM": 0.4}                  |
|     10 |       0.0950989 |    0.208477 |  -0.865865 |      0.706017 |       0.990968 |      0.240773 |                   2.83497 |        -0.468533 | {"TMFSIM": 0.55, "TQQQSIM": 0.4, "UPROSIM": 0.05}                 |
|     11 |       0.0950468 |    0.20707  |  -0.862324 |      0.709694 |       0.999272 |      0.24013  |                   2.84418 |        -0.457353 | {"QQQSIM": 0.05, "TMFSIM": 0.55, "TQQQSIM": 0.4}                  |
|     12 |       0.0950249 |    0.201717 |  -0.791214 |      0.719987 |       1.02442  |      0.254946 |                   2.92624 |        -0.330164 | {"GDESIM": 0.05, "TMFSIM": 0.6, "TQQQSIM": 0.35}                  |
|     13 |       0.0950038 |    0.201553 |  -0.804297 |      0.714927 |       1.01651  |      0.250595 |                   2.9103  |        -0.354882 | {"QLDSIM": 0.1, "TMFSIM": 0.6, "TQQQSIM": 0.3}                    |
|     14 |       0.0948439 |    0.201718 |  -0.801053 |      0.714146 |       1.01322  |      0.251816 |                   2.88267 |        -0.353565 | {"SSOSIM": 0.05, "TMFSIM": 0.6, "TQQQSIM": 0.35}                  |
|     15 |       0.094766  |    0.205968 |  -0.853383 |      0.711602 |       1.00205  |      0.241354 |                   2.81372 |        -0.44039  | {"TMFSIM": 0.55, "TQQQSIM": 0.4, "VTISIM": 0.05}                  |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   long_treasury |   nasdaq_equity |   cash |   gold |   us_large_equity |
|-------:|----------------:|----------------:|----------------:|-------:|-------:|------------------:|
|      1 |       0.0977684 |            1.8  |            1.2  |   0    |  0     |             0     |
|      2 |       0.0966711 |            1.65 |            1.2  |  -0.04 |  0.045 |             0.045 |
|      3 |       0.0965207 |            1.8  |            1.15 |   0    |  0     |             0     |
|      4 |       0.0964474 |            1.65 |            1.2  |   0    |  0.1   |             0     |
|      5 |       0.0961935 |            1.65 |            1.35 |   0    |  0     |             0     |

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
