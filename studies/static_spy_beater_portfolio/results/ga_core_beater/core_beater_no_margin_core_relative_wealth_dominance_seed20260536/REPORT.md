# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `core_beater_no_margin`
- Fitness: `core_relative_wealth_dominance`
- Seed: `20260536`
- Common window: `1988-01-04` to `2026-04-17`
- Unique evaluated portfolios: `3606`
- GA rolling step: `21` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `100` portfolios
- Benchmark rolling step: `1`
- Generations completed: `39` / `120`
- Early stop: `True` (`no_improvement_for_25_generations`)
- Patience: `25`, min_delta: `1e-06`
- Log every: `5` generations
- Eval log every: `500` unique portfolios
- Fast discovery: `True`
- Jobs: `4`

This is discovery output only. It is not a validated winner or a mandate change.
GA search breadth must be carried into later DSR/PBO accounting
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Best Portfolio

- Fitness value: `0.350000`
- Weights: `{"GDESIM": 0.35, "RSSTSIM": 0.4, "ZROZSIM": 0.25}`
- Effective exposure: `{"cash": -0.6799999999999999, "gold": 0.315, "managed_futures": 0.4, "us_large_equity": 0.7150000000000001, "zero_coupon_treasury": 0.25}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                          |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:---------------------------------------------------------------------------------|
|      1 |       0.35      |    0.156997 |  -0.299406 |      1.0399   |        1.48432 |      0.524363 |                  0.799946 |       -0.0983805 | {"GDESIM": 0.35, "RSSTSIM": 0.4, "ZROZSIM": 0.25}                                |
|      2 |       0.134894  |    0.165636 |  -0.400387 |      1.01401  |        1.4315  |      0.41369  |                  0.932985 |       -0.0596178 | {"GDESIM": 0.35, "QLDSIM": 0.05, "RSSTSIM": 0.4, "ZROZSIM": 0.2}                 |
|      3 |       0.124188  |    0.16519  |  -0.419606 |      0.996741 |        1.41514 |      0.393678 |                  0.953488 |       -0.0666792 | {"GDESIM": 0.35, "RSSTSIM": 0.35, "TQQQSIM": 0.05, "ZROZSIM": 0.25}              |
|      4 |       0.118242  |    0.163525 |  -0.379119 |      1.03307  |        1.47409 |      0.43133  |                  0.911316 |       -0.0795221 | {"GDESIM": 0.3, "QLDSIM": 0.05, "RSSTSIM": 0.4, "ZROZSIM": 0.25}                 |
|      5 |       0.116368  |    0.162984 |  -0.39909  |      1.00953  |        1.44763 |      0.408388 |                  0.929159 |       -0.0944129 | {"GDESIM": 0.3, "RSSTSIM": 0.35, "TQQQSIM": 0.05, "ZROZSIM": 0.3}                |
|      6 |       0.0929234 |    0.168181 |  -0.425166 |      1.01338  |        1.44248 |      0.395566 |                  0.997791 |       -0.0664762 | {"GDESIM": 0.3, "RSSTSIM": 0.4, "TQQQSIM": 0.05, "ZROZSIM": 0.25}                |
|      7 |       0.0893664 |    0.170514 |  -0.426859 |      1.00489  |        1.40823 |      0.399462 |                  0.99386  |       -0.0572567 | {"GDESIM": 0.35, "QLDSIM": 0.05, "RSSTSIM": 0.45, "ZROZSIM": 0.15}               |
|      8 |       0.087433  |    0.170229 |  -0.445094 |      0.994581 |        1.40126 |      0.382457 |                  1.02177  |       -0.051822  | {"GDESIM": 0.35, "RSSTSIM": 0.4, "TQQQSIM": 0.05, "ZROZSIM": 0.2}                |
|      9 |       0.0849013 |    0.162085 |  -0.329687 |      1.03869  |        1.47191 |      0.491633 |                  0.862306 |       -0.0806885 | {"GDESIM": 0.35, "RSSTSIM": 0.45, "ZROZSIM": 0.2}                                |
|     10 |       0.0810224 |    0.168562 |  -0.406203 |      1.02931  |        1.45838 |      0.41497  |                  0.974463 |       -0.0611714 | {"GDESIM": 0.3, "QLDSIM": 0.05, "RSSTSIM": 0.45, "ZROZSIM": 0.2}                 |
|     11 |       0.0691558 |    0.161482 |  -0.420888 |      0.994701 |        1.42305 |      0.38367  |                  0.903117 |       -0.0898739 | {"GDESIM": 0.3, "QLDSIM": 0.1, "RSSTSIM": 0.3, "ZROZSIM": 0.3}                   |
|     12 |       0.0601611 |    0.165902 |  -0.404939 |      1.02447  |        1.47211 |      0.409695 |                  0.976424 |       -0.0957385 | {"GDESIM": 0.25, "RSSTSIM": 0.4, "TQQQSIM": 0.05, "ZROZSIM": 0.3}                |
|     13 |       0.0534212 |    0.17318  |  -0.450452 |      1.00932  |        1.42663 |      0.384457 |                  1.06426  |       -0.053039  | {"GDESIM": 0.3, "RSSTSIM": 0.45, "TQQQSIM": 0.05, "ZROZSIM": 0.2}                |
|     14 |       0.0493075 |    0.166704 |  -0.446111 |      0.999367 |        1.41853 |      0.373683 |                  0.972661 |       -0.0651258 | {"GDESIM": 0.3, "QLDSIM": 0.1, "RSSTSIM": 0.35, "ZROZSIM": 0.25}                 |
|     15 |       0.0466974 |    0.165937 |  -0.464455 |      0.974175 |        1.38908 |      0.357272 |                  0.989269 |       -0.0761583 | {"GDESIM": 0.3, "QLDSIM": 0.05, "RSSTSIM": 0.3, "TQQQSIM": 0.05, "ZROZSIM": 0.3} |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   gold |   managed_futures |   us_large_equity |   zero_coupon_treasury |   nasdaq_equity |
|-------:|----------------:|-------:|-------:|------------------:|------------------:|-----------------------:|----------------:|
|      1 |        0.35     |  -0.68 |  0.315 |              0.4  |             0.715 |                   0.25 |            0    |
|      2 |        0.134894 |  -0.68 |  0.315 |              0.4  |             0.715 |                   0.2  |            0.1  |
|      3 |        0.124188 |  -0.63 |  0.315 |              0.35 |             0.665 |                   0.25 |            0.15 |
|      4 |        0.118242 |  -0.64 |  0.27  |              0.4  |             0.67  |                   0.25 |            0.1  |
|      5 |        0.116368 |  -0.59 |  0.27  |              0.35 |             0.62  |                   0.3  |            0.15 |

## Benchmark Portfolios

| benchmark     |     cagr |       mdd |   sharpe |   sortino |   calmar |   terminal_wealth |
|:--------------|---------:|----------:|---------:|----------:|---------:|------------------:|
| core_35_40_25 | 0.156997 | -0.299406 | 1.0399   |  1.48432  | 0.524363 |          265.443  |
| equal_weight  | 0.155872 | -0.718361 | 0.755334 |  1.01787  | 0.216983 |          255.737  |
| qqq_buy_hold  | 0.148737 | -0.829711 | 0.66842  |  0.893506 | 0.179264 |          201.78   |
| spy_buy_hold  | 0.114583 | -0.551413 | 0.691024 |  0.884039 | 0.207798 |           63.5573 |

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
