# Iter030 Parameter GA Candidate Diagnostics

Status: economic-first diagnostics for the strict Pareto candidates from the small GA run.

## Verdict

The best GA candidate is an economic improvement over iter030 on full-period CAGR and terminal equity, but the evidence is not robust enough to replace the baseline.
The main reason is that the improvement is a narrow mutation of the same mechanism (`T35D60` to longer `D120`, sometimes lower LRS/TQQQ weight), found after optimization on the same full history. Formal validation in `validation/REPORT.md` closed 0/7 PASS because all candidates failed DSR and the 195-gene PBO panel failed (`0.619`) `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.

## Strict Pareto Set

| label                                                                       |   cagr |   sortino |     mdd |   calmar |    end_mult |   delta_cagr |   delta_sortino |   delta_mdd |   t_crash |   d_arm |   tqqq_weight |   lrs_factor |   vol_threshold |
|:----------------------------------------------------------------------------|-------:|----------:|--------:|---------:|------------:|-------------:|----------------:|------------:|----------:|--------:|--------------:|-------------:|----------------:|
| ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w1.00_lrs1.20_g0.25_rv60_0.70 | 0.3901 |    1.2074 | -0.5548 |   0.7032 | 577835.2849 |       0.0235 |          0.0001 |      0.0000 |        20 |     120 |        1.0000 |       1.2000 |          0.4000 |
| ga_s100_250_vw21_vt0.50_ar30_k2_rearm_T35D120_w0.50_lrs1.15_g0.25_rv60_0.70 | 0.3750 |    1.2661 | -0.5396 |   0.6949 | 372013.0916 |       0.0084 |          0.0588 |      0.0151 |        35 |     120 |        0.5000 |       1.1500 |          0.5000 |
| ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T35D120_w1.00_lrs1.20_g0.25_rv60_0.70 | 0.3871 |    1.2177 | -0.5548 |   0.6977 | 528830.5971 |       0.0205 |          0.0104 |      0.0000 |        35 |     120 |        1.0000 |       1.2000 |          0.4000 |
| ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T35D120_w1.00_lrs1.15_g0.25_rv60_0.70 | 0.3774 |    1.2275 | -0.5373 |   0.7024 | 398773.7199 |       0.0108 |          0.0202 |      0.0175 |        35 |     120 |        1.0000 |       1.1500 |          0.4000 |
| ga_s100_250_vw21_vt0.50_ar30_k2_rearm_T35D60_w1.00_lrs1.15_g0.25_rv60_0.70  | 0.3709 |    1.2455 | -0.5378 |   0.6898 | 330137.6617 |       0.0043 |          0.0382 |      0.0170 |        35 |      60 |        1.0000 |       1.1500 |          0.5000 |
| ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w0.75_lrs1.20_g0.25_rv60_0.70 | 0.3794 |    1.2127 | -0.5482 |   0.6922 | 423260.9643 |       0.0128 |          0.0054 |      0.0066 |        20 |     120 |        0.7500 |       1.2000 |          0.4000 |

## Rolling Min CAGR

| label                                                                       |   min_3y_cagr |   min_5y_cagr |   min_10y_cagr |   min_15y_cagr |
|:----------------------------------------------------------------------------|--------------:|--------------:|---------------:|---------------:|
| ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w0.75_lrs1.20_g0.25_rv60_0.70 |       -0.1521 |        0.0214 |         0.0970 |         0.1808 |
| ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w1.00_lrs1.20_g0.25_rv60_0.70 |       -0.1658 |        0.0194 |         0.1018 |         0.1859 |
| ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T35D120_w1.00_lrs1.15_g0.25_rv60_0.70 |       -0.1502 |        0.0078 |         0.0906 |         0.1806 |
| ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T35D120_w1.00_lrs1.20_g0.25_rv60_0.70 |       -0.1658 |       -0.0008 |         0.0875 |         0.1827 |
| ga_s100_250_vw21_vt0.50_ar30_k2_rearm_T35D120_w0.50_lrs1.15_g0.25_rv60_0.70 |       -0.1316 |       -0.0120 |         0.0957 |         0.1826 |
| ga_s100_250_vw21_vt0.50_ar30_k2_rearm_T35D60_w1.00_lrs1.15_g0.25_rv60_0.70  |       -0.1429 |        0.0116 |         0.1026 |         0.1780 |
| iter030_baseline                                                            |       -0.1527 |        0.0148 |         0.0876 |         0.1689 |

## Annual Diagnostics

| label                                                                       |   positive_years_pct |   min_year |   min_return |   median_return |
|:----------------------------------------------------------------------------|---------------------:|-----------:|-------------:|----------------:|
| iter030_baseline                                                            |               0.8293 |       2022 |      -0.3729 |          0.3392 |
| ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w1.00_lrs1.20_g0.25_rv60_0.70 |               0.8293 |       2022 |      -0.3922 |          0.3861 |
| ga_s100_250_vw21_vt0.50_ar30_k2_rearm_T35D120_w0.50_lrs1.15_g0.25_rv60_0.70 |               0.8293 |       2022 |      -0.4028 |          0.4282 |
| ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T35D120_w1.00_lrs1.20_g0.25_rv60_0.70 |               0.8293 |       2022 |      -0.3729 |          0.3943 |
| ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T35D120_w1.00_lrs1.15_g0.25_rv60_0.70 |               0.8293 |       2022 |      -0.3594 |          0.3772 |
| ga_s100_250_vw21_vt0.50_ar30_k2_rearm_T35D60_w1.00_lrs1.15_g0.25_rv60_0.70  |               0.8293 |       2022 |      -0.4315 |          0.3974 |
| ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w0.75_lrs1.20_g0.25_rv60_0.70 |               0.8293 |       2022 |      -0.3758 |          0.3349 |

## Regime Metrics

| regime            | label                                                                       |   cagr |     mdd |   end_mult |
|:------------------|:----------------------------------------------------------------------------|-------:|--------:|-----------:|
| 1990_1994_whipsaw | iter030_baseline                                                            | 0.2607 | -0.5002 |     3.1779 |
| 1990_1994_whipsaw | ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w1.00_lrs1.20_g0.25_rv60_0.70 | 0.3049 | -0.5002 |     3.7749 |
| 1990_1994_whipsaw | ga_s100_250_vw21_vt0.50_ar30_k2_rearm_T35D120_w0.50_lrs1.15_g0.25_rv60_0.70 | 0.2736 | -0.4322 |     3.3442 |
| 1990_1994_whipsaw | ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T35D120_w1.00_lrs1.20_g0.25_rv60_0.70 | 0.2713 | -0.5002 |     3.3136 |
| 1990_1994_whipsaw | ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T35D120_w1.00_lrs1.15_g0.25_rv60_0.70 | 0.2658 | -0.4868 |     3.2424 |
| 1990_1994_whipsaw | ga_s100_250_vw21_vt0.50_ar30_k2_rearm_T35D60_w1.00_lrs1.15_g0.25_rv60_0.70  | 0.2736 | -0.4322 |     3.3442 |
| 1990_1994_whipsaw | ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w0.75_lrs1.20_g0.25_rv60_0.70 | 0.2826 | -0.4952 |     3.4629 |
| 2000_2002_bear    | iter030_baseline                                                            | 0.0075 | -0.5548 |     1.0227 |
| 2000_2002_bear    | ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w1.00_lrs1.20_g0.25_rv60_0.70 | 0.0075 | -0.5548 |     1.0227 |
| 2000_2002_bear    | ga_s100_250_vw21_vt0.50_ar30_k2_rearm_T35D120_w0.50_lrs1.15_g0.25_rv60_0.70 | 0.0351 | -0.5245 |     1.1088 |
| 2000_2002_bear    | ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T35D120_w1.00_lrs1.20_g0.25_rv60_0.70 | 0.0075 | -0.5548 |     1.0227 |
| 2000_2002_bear    | ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T35D120_w1.00_lrs1.15_g0.25_rv60_0.70 | 0.0205 | -0.5373 |     1.0627 |
| 2000_2002_bear    | ga_s100_250_vw21_vt0.50_ar30_k2_rearm_T35D60_w1.00_lrs1.15_g0.25_rv60_0.70  | 0.0205 | -0.5373 |     1.0627 |
| 2000_2002_bear    | ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w0.75_lrs1.20_g0.25_rv60_0.70 | 0.0156 | -0.5482 |     1.0474 |
| 2008_2009_gfc     | iter030_baseline                                                            | 0.1380 | -0.3209 |     1.2943 |
| 2008_2009_gfc     | ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w1.00_lrs1.20_g0.25_rv60_0.70 | 0.1764 | -0.3209 |     1.3830 |
| 2008_2009_gfc     | ga_s100_250_vw21_vt0.50_ar30_k2_rearm_T35D120_w0.50_lrs1.15_g0.25_rv60_0.70 | 0.0527 | -0.4427 |     1.1079 |
| 2008_2009_gfc     | ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T35D120_w1.00_lrs1.20_g0.25_rv60_0.70 | 0.1764 | -0.3209 |     1.3830 |
| 2008_2009_gfc     | ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T35D120_w1.00_lrs1.15_g0.25_rv60_0.70 | 0.1715 | -0.3075 |     1.3715 |
| 2008_2009_gfc     | ga_s100_250_vw21_vt0.50_ar30_k2_rearm_T35D60_w1.00_lrs1.15_g0.25_rv60_0.70  | 0.0750 | -0.4512 |     1.1552 |
| 2008_2009_gfc     | ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w0.75_lrs1.20_g0.25_rv60_0.70 | 0.1686 | -0.2988 |     1.3647 |
| 2010_2026_modern  | iter030_baseline                                                            | 0.3231 | -0.4255 |    95.4102 |
| 2010_2026_modern  | ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w1.00_lrs1.20_g0.25_rv60_0.70 | 0.3567 | -0.4433 |   143.6508 |
| 2010_2026_modern  | ga_s100_250_vw21_vt0.50_ar30_k2_rearm_T35D120_w0.50_lrs1.15_g0.25_rv60_0.70 | 0.3604 | -0.4423 |   150.1201 |
| 2010_2026_modern  | ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T35D120_w1.00_lrs1.20_g0.25_rv60_0.70 | 0.3668 | -0.4255 |   162.0368 |
| 2010_2026_modern  | ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T35D120_w1.00_lrs1.15_g0.25_rv60_0.70 | 0.3547 | -0.4105 |   140.1026 |
| 2010_2026_modern  | ga_s100_250_vw21_vt0.50_ar30_k2_rearm_T35D60_w1.00_lrs1.15_g0.25_rv60_0.70  | 0.3425 | -0.4734 |   121.0369 |
| 2010_2026_modern  | ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w0.75_lrs1.20_g0.25_rv60_0.70 | 0.3433 | -0.4246 |   122.1770 |

## Plots

![Pareto relative to iter030](plots/pareto_relative_to_iter030.png)

![10-year rolling CAGR](plots/pareto_rolling_10y_cagr.png)

## Next Validation

- Treat `ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w1.00_lrs1.20_g0.25_rv60_0.70` as an economic sensitivity, not a winner.
- Do not expand this local GA without a pre-registered validation design or a different hypothesis; the first honest validation already fails DSR/PBO.
- If revisited, prefer an explicit local sensitivity table around `T{20,35,45}D{60,90,120}` before any larger GA.
