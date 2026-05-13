# Iter030 Parameter GA Validation

Status: honest validation diagnostic for the strict Pareto candidates from the small parameter GA.

Candidates: 7 including baseline
DSR n_trials: 136,784,569
Bootstrap paths: 2,000
PBO panel size: 195
Elapsed seconds: 115.3

## Gate Summary

| label                                                                       | oos_pass   | fwd_pass   | wf_pass   | bootstrap_pass   | dsr_pass   | pbo_pass   | all_hard_gates_pass   |   dsr_p_value |    pbo |
|:----------------------------------------------------------------------------|:-----------|:-----------|:----------|:-----------------|:-----------|:-----------|:----------------------|--------------:|-------:|
| iter030_baseline                                                            | True       | True       | True      | True             | False      | False      | False                 |        0.3663 | 0.6190 |
| ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w1.00_lrs1.20_g0.25_rv60_0.70 | True       | True       | True      | True             | False      | False      | False                 |        0.3705 | 0.6190 |
| ga_s100_250_vw21_vt0.50_ar30_k2_rearm_T35D120_w0.50_lrs1.15_g0.25_rv60_0.70 | True       | True       | True      | True             | False      | False      | False                 |        0.2985 | 0.6190 |
| ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T35D120_w1.00_lrs1.20_g0.25_rv60_0.70 | True       | True       | True      | True             | False      | False      | False                 |        0.3384 | 0.6190 |
| ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T35D120_w1.00_lrs1.15_g0.25_rv60_0.70 | True       | True       | True      | True             | False      | False      | False                 |        0.3264 | 0.6190 |
| ga_s100_250_vw21_vt0.50_ar30_k2_rearm_T35D60_w1.00_lrs1.15_g0.25_rv60_0.70  | True       | True       | True      | True             | False      | False      | False                 |        0.3212 | 0.6190 |
| ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w0.75_lrs1.20_g0.25_rv60_0.70 | True       | True       | True      | True             | False      | False      | False                 |        0.3711 | 0.6190 |

## Headline Metrics

| label                                                                       |   sortino |   cagr |   sharpe |     mdd |   calmar |    end_mult |
|:----------------------------------------------------------------------------|----------:|-------:|---------:|--------:|---------:|------------:|
| iter030_baseline                                                            |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 |
| ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w1.00_lrs1.20_g0.25_rv60_0.70 |    1.2074 | 0.3901 |   0.9606 | -0.5548 |   0.7032 | 577835.2849 |
| ga_s100_250_vw21_vt0.50_ar30_k2_rearm_T35D120_w0.50_lrs1.15_g0.25_rv60_0.70 |    1.2661 | 0.3750 |   0.9921 | -0.5396 |   0.6949 | 372013.0916 |
| ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T35D120_w1.00_lrs1.20_g0.25_rv60_0.70 |    1.2177 | 0.3871 |   0.9744 | -0.5548 |   0.6977 | 528830.5971 |
| ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T35D120_w1.00_lrs1.15_g0.25_rv60_0.70 |    1.2275 | 0.3774 |   0.9797 | -0.5373 |   0.7024 | 398773.7199 |
| ga_s100_250_vw21_vt0.50_ar30_k2_rearm_T35D60_w1.00_lrs1.15_g0.25_rv60_0.70  |    1.2455 | 0.3709 |   0.9819 | -0.5378 |   0.6898 | 330137.6617 |
| ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w0.75_lrs1.20_g0.25_rv60_0.70 |    1.2127 | 0.3794 |   0.9604 | -0.5482 |   0.6922 | 423260.9643 |

## Interpretation

This validation is intentionally stricter than the economic-first diagnostic: PBO and DSR are hard gates again. A candidate only passes if every hard gate is true `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.
The PBO panel covers the 195 genes evaluated by the small GA, not the full theoretical parameter space, so a pass would still require a larger pre-registered validation panel.
