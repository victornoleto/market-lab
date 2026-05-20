# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `global_core`
- Fitness: `core_relative_wealth_dominance`
- Seed: `20260540`
- Common window: `2000-01-04` to `2026-04-17`
- Unique evaluated portfolios: `5817`
- GA rolling step: `21` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `100` portfolios
- Benchmark rolling step: `1`
- Generations completed: `43` / `120`
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

- Fitness value: `0.268714`
- Weights: `{"GDESIM": 0.45, "QLDSIM": 0.05, "RSSTSIM": 0.25, "ZROZSIM": 0.25}`
- Effective exposure: `{"cash": -0.6100000000000001, "gold": 0.405, "managed_futures": 0.25, "nasdaq_equity": 0.1, "us_large_equity": 0.655, "zero_coupon_treasury": 0.25}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                           |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:----------------------------------------------------------------------------------|
|      1 |        0.268714 |    0.13776  |  -0.361282 |      0.865489 |        1.20815 |      0.381308 |                  0.706702 |       -0.113042  | {"GDESIM": 0.45, "QLDSIM": 0.05, "RSSTSIM": 0.25, "ZROZSIM": 0.25}                |
|      2 |        0.260419 |    0.140531 |  -0.389006 |      0.853506 |        1.1804  |      0.361258 |                  0.767343 |       -0.0865261 | {"GDESIM": 0.45, "QLDSIM": 0.05, "RSSTSIM": 0.3, "ZROZSIM": 0.2}                  |
|      3 |        0.246968 |    0.137768 |  -0.430675 |      0.821935 |        1.14486 |      0.319888 |                  0.817781 |       -0.0953559 | {"GDESIM": 0.45, "QLDSIM": 0.1, "RSSTSIM": 0.2, "ZROZSIM": 0.25}                  |
|      4 |        0.240834 |    0.138909 |  -0.394654 |      0.853961 |        1.18393 |      0.351976 |                  0.745063 |       -0.08104   | {"GDESIM": 0.4, "QLDSIM": 0.05, "RSSTSIM": 0.35, "ZROZSIM": 0.2}                  |
|      5 |        0.238624 |    0.141898 |  -0.450885 |      0.808316 |        1.11454 |      0.314711 |                  0.902741 |       -0.0741636 | {"GDESIM": 0.5, "QLDSIM": 0.1, "RSSTSIM": 0.2, "ZROZSIM": 0.2}                    |
|      6 |        0.237254 |    0.13914  |  -0.4257   |      0.817146 |        1.13644 |      0.32685  |                  0.836377 |       -0.0988195 | {"GDESIM": 0.5, "QLDSIM": 0.1, "RSSTSIM": 0.15, "ZROZSIM": 0.25}                  |
|      7 |        0.230672 |    0.142041 |  -0.383447 |      0.850285 |        1.17374 |      0.370433 |                  0.7875   |       -0.0912639 | {"GDESIM": 0.5, "QLDSIM": 0.05, "RSSTSIM": 0.25, "ZROZSIM": 0.2}                  |
|      8 |        0.227516 |    0.139221 |  -0.355518 |      0.860251 |        1.1979  |      0.391601 |                  0.726043 |       -0.11927   | {"GDESIM": 0.5, "QLDSIM": 0.05, "RSSTSIM": 0.2, "ZROZSIM": 0.25}                  |
|      9 |        0.226458 |    0.136779 |  -0.378032 |      0.848388 |        1.17452 |      0.361818 |                  0.694073 |       -0.0970082 | {"GDESIM": 0.4, "NTSESIM": 0.05, "QLDSIM": 0.05, "RSSTSIM": 0.3, "ZROZSIM": 0.2}  |
|     10 |        0.220077 |    0.134155 |  -0.417166 |      0.838777 |        1.17401 |      0.321586 |                  0.723469 |       -0.10308   | {"GDESIM": 0.35, "GLDSIM": 0.05, "QLDSIM": 0.1, "RSSTSIM": 0.25, "ZROZSIM": 0.25} |
|     11 |        0.217073 |    0.135649 |  -0.41193  |      0.835743 |        1.16762 |      0.329301 |                  0.743259 |       -0.107969  | {"GDESIM": 0.4, "GLDSIM": 0.05, "QLDSIM": 0.1, "RSSTSIM": 0.2, "ZROZSIM": 0.25}   |
|     12 |        0.213677 |    0.138407 |  -0.437589 |      0.825592 |        1.1434  |      0.316295 |                  0.805176 |       -0.0816812 | {"GDESIM": 0.4, "GLDSIM": 0.05, "QLDSIM": 0.1, "RSSTSIM": 0.25, "ZROZSIM": 0.2}   |
|     13 |        0.211706 |    0.140478 |  -0.455684 |      0.81136  |        1.12053 |      0.308279 |                  0.881471 |       -0.0678156 | {"GDESIM": 0.45, "QLDSIM": 0.1, "RSSTSIM": 0.25, "ZROZSIM": 0.2}                  |
|     14 |        0.211248 |    0.143204 |  -0.449694 |      0.803207 |        1.10577 |      0.318448 |                  0.921028 |       -0.0779251 | {"GDESIM": 0.55, "QLDSIM": 0.1, "RSSTSIM": 0.15, "ZROZSIM": 0.2}                  |
|     15 |        0.209509 |    0.138346 |  -0.369104 |      0.868962 |        1.20501 |      0.374817 |                  0.69593  |       -0.099984  | {"GDESIM": 0.4, "GLDSIM": 0.05, "QLDSIM": 0.05, "RSSTSIM": 0.3, "ZROZSIM": 0.2}   |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   gold |   managed_futures |   nasdaq_equity |   us_large_equity |   zero_coupon_treasury |
|-------:|----------------:|-------:|-------:|------------------:|----------------:|------------------:|-----------------------:|
|      1 |        0.268714 |  -0.61 |  0.405 |              0.25 |             0.1 |             0.655 |                   0.25 |
|      2 |        0.260419 |  -0.66 |  0.405 |              0.3  |             0.1 |             0.705 |                   0.2  |
|      3 |        0.246968 |  -0.56 |  0.405 |              0.2  |             0.2 |             0.605 |                   0.25 |
|      4 |        0.240834 |  -0.67 |  0.36  |              0.35 |             0.1 |             0.71  |                   0.2  |
|      5 |        0.238624 |  -0.6  |  0.45  |              0.2  |             0.2 |             0.65  |                   0.2  |

## Benchmark Portfolios

| benchmark     |      cagr |       mdd |   sharpe |   sortino |   calmar |   terminal_wealth |
|:--------------|----------:|----------:|---------:|----------:|---------:|------------------:|
| b4            | 0.121202  | -0.279216 | 0.882281 |  1.23885  | 0.434078 |          20.1098  |
| core_35_40_25 | 0.133862  | -0.299406 | 0.903544 |  1.26627  | 0.447093 |          26.9986  |
| equal_weight  | 0.0916229 | -0.408591 | 0.673648 |  0.897955 | 0.224241 |           9.97247 |
| qqq_buy_hold  | 0.0830434 | -0.829711 | 0.431434 |  0.56349  | 0.100087 |           8.10781 |
| spy_buy_hold  | 0.0823563 | -0.551413 | 0.505935 |  0.643555 | 0.149355 |           7.97396 |

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
