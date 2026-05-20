# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `core_beater_factor_no_margin`
- Fitness: `core_relative_wealth_dominance`
- Seed: `20260544`
- Common window: `1994-06-02` to `2026-04-17`
- Unique evaluated portfolios: `4645`
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

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                            |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:-----------------------------------------------------------------------------------|
|      1 |       0.35      |    0.155444 |  -0.299406 |      1.02791  |        1.45013 |      0.519174 |                  0.741214 |       -0.112779  | {"GDESIM": 0.35, "RSSTSIM": 0.4, "ZROZSIM": 0.25}                                  |
|      2 |       0.133988  |    0.159963 |  -0.373085 |      1.00496  |        1.41684 |      0.428758 |                  0.830795 |       -0.0902067 | {"GDESIM": 0.35, "QLDSIM": 0.05, "RSSTSIM": 0.35, "ZROZSIM": 0.25}                 |
|      3 |       0.0989549 |    0.165122 |  -0.400387 |      0.999646 |        1.39644 |      0.412405 |                  0.873643 |       -0.0665675 | {"GDESIM": 0.35, "QLDSIM": 0.05, "RSSTSIM": 0.4, "ZROZSIM": 0.2}                   |
|      4 |       0.0925329 |    0.163714 |  -0.394654 |      0.986819 |        1.37532 |      0.41483  |                  0.883128 |       -0.0687317 | {"GDESIM": 0.4, "QLDSIM": 0.05, "RSSTSIM": 0.35, "ZROZSIM": 0.2}                   |
|      5 |       0.0842809 |    0.16186  |  -0.381289 |      0.992139 |        1.3802  |      0.424507 |                  0.839798 |       -0.0663379 | {"GDESIM": 0.35, "QLDSIM": 0.05, "RSSTSIM": 0.35, "VBRSIM": 0.05, "ZROZSIM": 0.2}  |
|      6 |       0.0768258 |    0.164701 |  -0.419606 |      0.985381 |        1.38771 |      0.392513 |                  0.913278 |       -0.0760488 | {"GDESIM": 0.35, "RSSTSIM": 0.35, "TQQQSIM": 0.05, "ZROZSIM": 0.25}                |
|      7 |       0.0750171 |    0.161391 |  -0.401158 |      0.976656 |        1.37048 |      0.402314 |                  0.879468 |       -0.0796695 | {"GDESIM": 0.35, "RSSTSIM": 0.3, "TQQQSIM": 0.05, "VBRSIM": 0.05, "ZROZSIM": 0.25} |
|      8 |       0.0647033 |    0.160794 |  -0.39909  |      0.995985 |        1.41781 |      0.402901 |                  0.857097 |       -0.106598  | {"GDESIM": 0.3, "RSSTSIM": 0.35, "TQQQSIM": 0.05, "ZROZSIM": 0.3}                  |
|      9 |       0.0488564 |    0.168711 |  -0.421334 |      0.976612 |        1.34904 |      0.40042  |                  0.924126 |       -0.0597548 | {"GDESIM": 0.4, "QLDSIM": 0.05, "RSSTSIM": 0.4, "ZROZSIM": 0.15}                   |
|     10 |       0.0427074 |    0.168374 |  -0.439814 |      0.967763 |        1.34777 |      0.38283  |                  0.967236 |       -0.0573363 | {"GDESIM": 0.4, "RSSTSIM": 0.35, "TQQQSIM": 0.05, "ZROZSIM": 0.2}                  |
|     11 |       0.0408312 |    0.169806 |  -0.445094 |      0.979778 |        1.3675  |      0.381505 |                  0.957386 |       -0.0576165 | {"GDESIM": 0.35, "RSSTSIM": 0.4, "TQQQSIM": 0.05, "ZROZSIM": 0.2}                  |
|     12 |       0.0405041 |    0.157536 |  -0.379955 |      0.988412 |        1.40176 |      0.414618 |                  0.824304 |       -0.112946  | {"GDESIM": 0.3, "RSSTSIM": 0.3, "TQQQSIM": 0.05, "VBRSIM": 0.05, "ZROZSIM": 0.3}   |
|     13 |       0.0399797 |    0.158087 |  -0.359308 |      1.01038  |        1.42121 |      0.439977 |                  0.787671 |       -0.0937384 | {"GDESIM": 0.3, "QLDSIM": 0.05, "RSSTSIM": 0.35, "VBRSIM": 0.05, "ZROZSIM": 0.25}  |
|     14 |       0.0300836 |    0.166059 |  -0.425166 |      0.996225 |        1.40509 |      0.390575 |                  0.903442 |       -0.075554  | {"GDESIM": 0.3, "RSSTSIM": 0.4, "TQQQSIM": 0.05, "ZROZSIM": 0.25}                  |
|     15 |       0.0217532 |    0.165013 |  -0.422039 |      0.958015 |        1.32908 |      0.390989 |                  0.928831 |       -0.0553069 | {"GDESIM": 0.4, "RSSTSIM": 0.3, "TQQQSIM": 0.05, "VBRSIM": 0.05, "ZROZSIM": 0.2}   |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   gold |   managed_futures |   us_large_equity |   zero_coupon_treasury |   nasdaq_equity |   us_small_value_equity |
|-------:|----------------:|-------:|-------:|------------------:|------------------:|-----------------------:|----------------:|------------------------:|
|      1 |       0.35      |  -0.68 |  0.315 |              0.4  |             0.715 |                   0.25 |             0   |                    0    |
|      2 |       0.133988  |  -0.63 |  0.315 |              0.35 |             0.665 |                   0.25 |             0.1 |                    0    |
|      3 |       0.0989549 |  -0.68 |  0.315 |              0.4  |             0.715 |                   0.2  |             0.1 |                    0    |
|      4 |       0.0925329 |  -0.67 |  0.36  |              0.35 |             0.71  |                   0.2  |             0.1 |                    0    |
|      5 |       0.0842809 |  -0.63 |  0.315 |              0.35 |             0.665 |                   0.2  |             0.1 |                    0.05 |

## Benchmark Portfolios

| benchmark     |     cagr |       mdd |   sharpe |   sortino |   calmar |   terminal_wealth |
|:--------------|---------:|----------:|---------:|----------:|---------:|------------------:|
| core_35_40_25 | 0.155444 | -0.299406 | 1.02791  |  1.45013  | 0.519174 |           99.4835 |
| equal_weight  | 0.145457 | -0.655244 | 0.732262 |  0.978094 | 0.221988 |           75.4605 |
| qqq_buy_hold  | 0.149147 | -0.829711 | 0.650882 |  0.869164 | 0.179758 |           83.5987 |
| spy_buy_hold  | 0.110419 | -0.551413 | 0.649218 |  0.830715 | 0.200247 |           28.0658 |

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
