# Static SPY-Beater Portfolio GA Report

## Run

- Universe: `core_1986`
- Fitness: `min_regret`
- Seed: `20260519`
- Common window: `1986-12-12` to `2026-04-17`
- Unique evaluated portfolios: `1109`
- GA rolling step: `126` (`21` means monthly-sampled discovery windows)
- Finalist exact re-rank: `20` portfolios
- Benchmark rolling step: `1`
- Generations completed: `32` / `40`
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

- Fitness value: `-0.014620`
- Weights: `{"NTSXSIM": 0.4, "SPYSIM": 0.3, "SSOSIM": 0.1, "VTISIM": 0.2}`
- Effective exposure: `{"cash": -0.2, "intermediate_treasury": 0.24, "us_large_equity": 0.8600000000000001, "us_total_equity": 0.2}`

## Top 15

|   rank |   fitness_value |   full_cagr |   full_mdd |   full_sharpe |   full_sortino |   full_calmar |   fit_relative_wealth_spy |   fit_min_regret | weights                                                                                          |
|-------:|----------------:|------------:|-----------:|--------------:|---------------:|--------------:|--------------------------:|-----------------:|:-------------------------------------------------------------------------------------------------|
|      1 |      -0.0146197 |    0.120484 |  -0.559124 |      0.687729 |       0.85965  |      0.215488 |                  0.119099 |       -0.0146197 | {"NTSXSIM": 0.4, "SPYSIM": 0.3, "SSOSIM": 0.1, "VTISIM": 0.2}                                    |
|      2 |      -0.015377  |    0.121757 |  -0.556624 |      0.690763 |       0.864515 |      0.218741 |                  0.125891 |       -0.015377  | {"GDESIM": 0.05, "NTSXSIM": 0.35, "SPYSIM": 0.4, "SSOSIM": 0.1, "VTISIM": 0.1}                   |
|      3 |      -0.0160277 |    0.11911  |  -0.537439 |      0.703478 |       0.882991 |      0.221625 |                  0.108433 |       -0.0160277 | {"CASHX": 0.05, "NTSXSIM": 0.4, "QQQSIM": 0.05, "SPYSIM": 0.15, "SSOSIM": 0.1, "VTISIM": 0.25}   |
|      4 |      -0.0161376 |    0.124958 |  -0.545272 |      0.70673  |       0.891061 |      0.229166 |                  0.176558 |       -0.0161376 | {"GDESIM": 0.05, "NTSXSIM": 0.45, "QQQSIM": 0.05, "SPYSIM": 0.25, "SSOSIM": 0.1, "VTISIM": 0.1}  |
|      5 |      -0.016212  |    0.120384 |  -0.559686 |      0.690737 |       0.862604 |      0.215093 |                  0.124187 |       -0.016212  | {"NTSXSIM": 0.4, "SPYSIM": 0.1, "SSOSIM": 0.1, "VTISIM": 0.4}                                    |
|      6 |      -0.0164088 |    0.12267  |  -0.556948 |      0.692659 |       0.869201 |      0.220254 |                  0.143511 |       -0.0164088 | {"NTSXSIM": 0.4, "QQQSIM": 0.05, "SPYSIM": 0.3, "SSOSIM": 0.1, "VTISIM": 0.15}                   |
|      7 |      -0.0165673 |    0.120229 |  -0.536226 |      0.707137 |       0.889287 |      0.224213 |                  0.124301 |       -0.0165673 | {"BNDSIM": 0.05, "NTSXSIM": 0.4, "QQQSIM": 0.05, "SPYSIM": 0.2, "SSOSIM": 0.1, "VTISIM": 0.2}    |
|      8 |      -0.0167614 |    0.119913 |  -0.538238 |      0.705117 |       0.886141 |      0.222788 |                  0.119667 |       -0.0167614 | {"IEFSIM": 0.05, "NTSXSIM": 0.35, "QQQSIM": 0.05, "SPYSIM": 0.2, "SSOSIM": 0.1, "VTISIM": 0.25}  |
|      9 |      -0.0167981 |    0.119642 |  -0.5325   |      0.708026 |       0.890971 |      0.22468  |                  0.117304 |       -0.0167981 | {"CASHX": 0.05, "NTSXSIM": 0.45, "QQQSIM": 0.05, "SPYSIM": 0.15, "SSOSIM": 0.1, "VTISIM": 0.2}   |
|     10 |      -0.0168087 |    0.120466 |  -0.533166 |      0.708687 |       0.892923 |      0.225945 |                  0.12765  |       -0.0168087 | {"IEFSIM": 0.05, "NTSXSIM": 0.4, "QQQSIM": 0.05, "SPYSIM": 0.25, "SSOSIM": 0.1, "VTISIM": 0.15}  |
|     11 |      -0.0168606 |    0.123161 |  -0.552483 |      0.698536 |       0.87779  |      0.222923 |                  0.15652  |       -0.0168606 | {"NTSXSIM": 0.45, "QQQSIM": 0.05, "SPYSIM": 0.2, "SSOSIM": 0.1, "VTISIM": 0.2}                   |
|     12 |      -0.0171792 |    0.119887 |  -0.538382 |      0.705891 |       0.886691 |      0.222679 |                  0.120859 |       -0.0171792 | {"IEFSIM": 0.05, "NTSXSIM": 0.35, "QQQSIM": 0.05, "SPYSIM": 0.15, "SSOSIM": 0.1, "VTISIM": 0.3}  |
|     13 |      -0.0176297 |    0.124202 |  -0.543009 |      0.707742 |       0.892782 |      0.228729 |                  0.177169 |       -0.0176297 | {"NTSXSIM": 0.55, "QQQSIM": 0.05, "SPYSIM": 0.15, "SSOSIM": 0.1, "VTISIM": 0.15}                 |
|     14 |      -0.0176443 |    0.123904 |  -0.554715 |      0.697421 |       0.875984 |      0.223364 |                  0.154684 |       -0.0176443 | {"GDESIM": 0.05, "NTSXSIM": 0.35, "QQQSIM": 0.05, "SPYSIM": 0.3, "SSOSIM": 0.1, "VTISIM": 0.15}  |
|     15 |      -0.0179143 |    0.122946 |  -0.55001  |      0.69964  |       0.882764 |      0.223533 |                  0.156121 |       -0.0179143 | {"NTSXSIM": 0.45, "QQQSIM": 0.05, "RSSBSIM": 0.05, "SPYSIM": 0.25, "SSOSIM": 0.1, "VTISIM": 0.1} |

## Effective Exposure Summary (Top 5)

|   rank |   fitness_value |   cash |   intermediate_treasury |   us_large_equity |   us_total_equity |   gold |   nasdaq_equity |
|-------:|----------------:|-------:|------------------------:|------------------:|------------------:|-------:|----------------:|
|      1 |      -0.0146197 | -0.2   |                    0.24 |              0.86 |              0.2  |  0     |            0    |
|      2 |      -0.015377  | -0.215 |                    0.21 |              0.96 |              0.1  |  0.045 |            0    |
|      3 |      -0.0160277 | -0.15  |                    0.24 |              0.71 |              0.25 |  0     |            0.05 |
|      4 |      -0.0161376 | -0.265 |                    0.27 |              0.9  |              0.1  |  0.045 |            0.05 |
|      5 |      -0.016212  | -0.2   |                    0.24 |              0.66 |              0.4  |  0     |            0    |

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
