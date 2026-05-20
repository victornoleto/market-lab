# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `full_2000`
- Fitness: `balanced_dual_beater`
- Seed: `20260519`
- Common window: `2000-01-04` to `2026-04-17`
- Unique evaluated portfolios: `718`
- GA rolling step: `126` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `20` portfolios
- Benchmark rolling step: `1`
- Generations completed: `20` / `40`
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

- Fitness value: `0.620754`
- Weights: `{"QLDSIM": 0.1, "RSSTSIM": 0.1, "SSOSIM": 0.05, "TMFSIM": 0.15, "TQQQSIM": 0.45, "UGLSIM": 0.15}`
- Effective exposure: `{"cash": -0.1, "gold": 0.3, "long_treasury": 0.44999999999999996, "managed_futures": 0.1, "nasdaq_equity": 1.55, "us_large_equity": 0.2}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                                            |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:-------------------------------------------------------------------------------------------------------------------|
|      1 |        0.620754 |   0.11614   |  -0.958733 |      0.47189  |       0.623988 |     0.121139  |                   3.09376 |        -0.348715 | {"QLDSIM": 0.1, "RSSTSIM": 0.1, "SSOSIM": 0.05, "TMFSIM": 0.15, "TQQQSIM": 0.45, "UGLSIM": 0.15}                   |
|      2 |        0.616474 |   0.118948  |  -0.960597 |      0.477207 |       0.630621 |     0.123827  |                   3.09943 |        -0.346281 | {"QLDSIM": 0.1, "RSSTSIM": 0.1, "SSOSIM": 0.05, "TMFSIM": 0.1, "TQQQSIM": 0.45, "UGLSIM": 0.2}                     |
|      3 |        0.614086 |   0.122779  |  -0.948275 |      0.490629 |       0.650414 |     0.129477  |                   3.00404 |        -0.325583 | {"QLDSIM": 0.15, "RSSBSIM": 0.05, "RSSTSIM": 0.05, "TMFSIM": 0.15, "TQQQSIM": 0.4, "UGLSIM": 0.2}                  |
|      4 |        0.612986 |   0.131769  |  -0.938582 |      0.514717 |       0.683041 |     0.140392  |                   2.9597  |        -0.281323 | {"NTSXSIM": 0.05, "QLDSIM": 0.1, "RSSTSIM": 0.1, "TMFSIM": 0.1, "TQQQSIM": 0.4, "UGLSIM": 0.25}                    |
|      5 |        0.611632 |   0.129874  |  -0.934402 |      0.512181 |       0.680444 |     0.138992  |                   2.93677 |        -0.292981 | {"QLDSIM": 0.1, "RSSTSIM": 0.1, "TMFSIM": 0.15, "TQQQSIM": 0.4, "UGLSIM": 0.2, "VBRSIM": 0.05}                     |
|      6 |        0.60396  |   0.128477  |  -0.935709 |      0.509175 |       0.676869 |     0.137305  |                   2.91593 |        -0.29413  | {"NTSESIM": 0.05, "QLDSIM": 0.1, "RSSTSIM": 0.1, "TMFSIM": 0.15, "TQQQSIM": 0.4, "UGLSIM": 0.2}                    |
|      7 |        0.600265 |   0.113257  |  -0.951511 |      0.468382 |       0.620539 |     0.119028  |                   2.95753 |        -0.345695 | {"QLDSIM": 0.1, "RSSTSIM": 0.1, "TLTSIM": 0.05, "TMFSIM": 0.2, "TQQQSIM": 0.45, "UGLSIM": 0.1}                     |
|      8 |        0.59625  |   0.12232   |  -0.960338 |      0.4843   |       0.640605 |     0.127372  |                   3.0277  |        -0.332242 | {"GDESIM": 0.05, "QLDSIM": 0.1, "RSSBSIM": 0.05, "RSSTSIM": 0.05, "TMFSIM": 0.05, "TQQQSIM": 0.45, "UGLSIM": 0.25} |
|      9 |        0.591635 |   0.126856  |  -0.94439  |      0.499906 |       0.66265  |     0.134326  |                   2.91041 |        -0.299104 | {"QLDSIM": 0.1, "RSSTSIM": 0.15, "SSOSIM": 0.05, "TMFSIM": 0.1, "TQQQSIM": 0.4, "UGLSIM": 0.2}                     |
|     10 |        0.589711 |   0.12649   |  -0.935898 |      0.504366 |       0.669778 |     0.135153  |                   2.8562  |        -0.297579 | {"NTSXSIM": 0.1, "QLDSIM": 0.1, "RSSTSIM": 0.05, "TMFSIM": 0.15, "TQQQSIM": 0.4, "UGLSIM": 0.2}                    |
|     11 |        0.588495 |   0.0968521 |  -0.976712 |      0.432265 |       0.568063 |     0.0991614 |                   3.14757 |        -0.409278 | {"QLDSIM": 0.15, "RSSTSIM": 0.1, "TMFSIM": 0.1, "TQQQSIM": 0.5, "UGLSIM": 0.1, "ZROZSIM": 0.05}                    |
|     12 |        0.584422 |   0.132096  |  -0.931473 |      0.517584 |       0.687778 |     0.141815  |                   2.83412 |        -0.271259 | {"QLDSIM": 0.05, "RSSTSIM": 0.2, "SSOSIM": 0.05, "TMFSIM": 0.1, "TQQQSIM": 0.4, "UGLSIM": 0.2}                     |
|     13 |        0.576913 |   0.149293  |  -0.889138 |      0.583278 |       0.781093 |     0.167908  |                   2.75037 |        -0.208748 | {"NTSXSIM": 0.05, "QLDSIM": 0.05, "RSSTSIM": 0.1, "TMFSIM": 0.1, "TQQQSIM": 0.35, "UGLSIM": 0.35}                  |
|     14 |        0.571614 |   0.130427  |  -0.926033 |      0.517356 |       0.689332 |     0.140845  |                   2.76851 |        -0.281997 | {"NTSESIM": 0.05, "QLDSIM": 0.05, "RSSTSIM": 0.1, "SSOSIM": 0.05, "TMFSIM": 0.15, "TQQQSIM": 0.4, "UGLSIM": 0.2}   |
|     15 |        0.570491 |   0.112201  |  -0.958353 |      0.463768 |       0.61271  |     0.117077  |                   2.89344 |        -0.349558 | {"GDESIM": 0.05, "QLDSIM": 0.1, "RSSTSIM": 0.1, "TMFSIM": 0.15, "TQQQSIM": 0.45, "UGLSIM": 0.1, "VTSIM": 0.05}     |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   gold |   long_treasury |   managed_futures |   nasdaq_equity |   us_large_equity |   aggregate_bond |   global_equity |   intermediate_treasury |   us_small_value_equity |
|-------:|----------------:|-------:|-------:|----------------:|------------------:|----------------:|------------------:|-----------------:|----------------:|------------------------:|------------------------:|
|      1 |        0.620754 | -0.1   |    0.3 |            0.45 |              0.1  |            1.55 |             0.2   |             0    |            0    |                    0    |                    0    |
|      2 |        0.616474 | -0.1   |    0.4 |            0.3  |              0.1  |            1.55 |             0.2   |             0    |            0    |                    0    |                    0    |
|      3 |        0.614086 | -0.1   |    0.4 |            0.45 |              0.05 |            1.5  |             0.05  |             0.05 |            0.05 |                    0    |                    0    |
|      4 |        0.612986 | -0.125 |    0.5 |            0.3  |              0.1  |            1.4  |             0.145 |             0    |            0    |                    0.03 |                    0    |
|      5 |        0.611632 | -0.1   |    0.4 |            0.45 |              0.1  |            1.4  |             0.1   |             0    |            0    |                    0    |                    0.05 |

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
