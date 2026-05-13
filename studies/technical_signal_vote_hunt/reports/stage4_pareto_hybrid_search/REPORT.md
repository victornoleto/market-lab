# Stage4 Pareto Hybrid Search

Status: economic-first search for a hybrid that beats iter030 on CAGR, Sortino and MDD.

Window: `1986-01-03` to `2026-04-17` (10,150 bars)
Candidates tested: 225
Strict Pareto candidates vs iter030: 0

## Top Candidates

| label                                            | gate                          |   weight |   lrs_factor | strict_pareto_vs_iter030   |   sortino |   cagr |   sharpe |     mdd |   calmar |    end_mult |   score |
|:-------------------------------------------------|:------------------------------|---------:|-------------:|:---------------------------|----------:|-------:|---------:|--------:|---------:|------------:|--------:|
| gate_rearm_w1.00_lrs1.00                         | rearm                         |   1.0000 |       1.0000 | False                      |    1.2518 | 0.3282 |   0.9858 | -0.4818 |   0.6812 |  92113.9028 |  0.0021 |
| gate_rearm_w1.00_lrs1.10                         | rearm                         |   1.0000 |       1.1000 | False                      |    1.2281 | 0.3480 |   0.9734 | -0.5193 |   0.6701 | 167367.4541 |  0.0005 |
| gate_rearm_w1.00_lrs1.20                         | rearm                         |   1.0000 |       1.2000 | False                      |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 |  0.0000 |
| gate_rearm_w0.75_lrs1.00                         | rearm                         |   0.7500 |       1.0000 | False                      |    1.2540 | 0.3233 |   0.9836 | -0.4769 |   0.6778 |  79408.7964 | -0.0054 |
| gate_rearm_w0.75_lrs1.10                         | rearm                         |   0.7500 |       1.1000 | False                      |    1.2301 | 0.3428 |   0.9712 | -0.5130 |   0.6682 | 143209.7669 | -0.0069 |
| gate_rearm_w0.75_lrs1.20                         | rearm                         |   0.7500 |       1.2000 | False                      |    1.2091 | 0.3611 |   0.9601 | -0.5482 |   0.6588 | 247108.5125 | -0.0081 |
| gate_rearm_or_stage4_rv_lt_70_w0.75_lrs1.20      | rearm_or_stage4_rv_lt_70      |   0.7500 |       1.2000 | False                      |    1.1737 | 0.3913 |   0.9287 | -0.6051 |   0.6467 | 598646.3718 | -0.0097 |
| gate_rearm_or_stage4_rv_lt_70_w0.50_lrs1.20      | rearm_or_stage4_rv_lt_70      |   0.5000 |       1.2000 | False                      |    1.1867 | 0.3770 |   0.9361 | -0.5769 |   0.6534 | 394028.5943 | -0.0117 |
| gate_rearm_or_stage4_rv_lt_70_w0.75_lrs1.10      | rearm_or_stage4_rv_lt_70      |   0.7500 |       1.1000 | False                      |    1.1933 | 0.3736 |   0.9391 | -0.5754 |   0.6493 | 357004.7473 | -0.0136 |
| gate_rearm_or_stage4_rv_lt_70_w1.00_lrs1.20      | rearm_or_stage4_rv_lt_70      |   1.0000 |       1.2000 | False                      |    1.1586 | 0.4039 |   0.9206 | -0.6319 |   0.6392 | 860155.5242 | -0.0139 |
| gate_rearm_or_stage4_rv_lt_70_w0.50_lrs1.10      | rearm_or_stage4_rv_lt_70      |   0.5000 |       1.1000 | False                      |    1.2071 | 0.3591 |   0.9469 | -0.5482 |   0.6550 | 232707.6668 | -0.0163 |
| gate_rearm_or_stage4_rv_lt_70_w1.00_lrs1.10      | rearm_or_stage4_rv_lt_70      |   1.0000 |       1.1000 | False                      |    1.1775 | 0.3867 |   0.9307 | -0.6014 |   0.6429 | 522702.8537 | -0.0163 |
| gate_rearm_or_stage4_rv_lt_70_w0.75_lrs1.00      | rearm_or_stage4_rv_lt_70      |   0.7500 |       1.0000 | False                      |    1.2160 | 0.3540 |   0.9510 | -0.5442 |   0.6504 | 199887.0743 | -0.0186 |
| gate_rearm_w0.50_lrs1.10                         | rearm                         |   0.5000 |       1.1000 | False                      |    1.2297 | 0.3374 |   0.9679 | -0.5081 |   0.6640 | 121677.5687 | -0.0187 |
| gate_rearm_w0.50_lrs1.20                         | rearm                         |   0.5000 |       1.2000 | False                      |    1.2084 | 0.3554 |   0.9567 | -0.5417 |   0.6560 | 208393.3500 | -0.0195 |
| gate_rearm_or_stage4_rv_lt_70_w1.00_lrs1.00      | rearm_or_stage4_rv_lt_70      |   1.0000 |       1.0000 | False                      |    1.1993 | 0.3672 |   0.9423 | -0.5692 |   0.6451 | 295520.2770 | -0.0207 |
| gate_rearm_w0.50_lrs1.00                         | rearm                         |   0.5000 |       1.0000 | False                      |    1.2537 | 0.3182 |   0.9804 | -0.4769 |   0.6672 |  68059.5943 | -0.0208 |
| gate_rearm_or_stage4_rv_lt_70_w0.25_lrs1.20      | rearm_or_stage4_rv_lt_70      |   0.2500 |       1.2000 | False                      |    1.1959 | 0.3609 |   0.9423 | -0.5474 |   0.6592 | 245333.4614 | -0.0212 |
| gate_rearm_or_stage4_rv_lt_70_w0.50_lrs1.00      | rearm_or_stage4_rv_lt_70      |   0.5000 |       1.0000 | False                      |    1.2305 | 0.3396 |   0.9591 | -0.5182 |   0.6553 | 130101.7229 | -0.0213 |
| gate_rearm_or_stage4_rv_lt_70_w0.25_lrs1.10      | rearm_or_stage4_rv_lt_70      |   0.2500 |       1.1000 | False                      |    1.2170 | 0.3432 |   0.9534 | -0.5199 |   0.6601 | 144791.1945 | -0.0257 |
| gate_rearm_or_stage4_rv_lt_70_w0.25_lrs1.00      | rearm_or_stage4_rv_lt_70      |   0.2500 |       1.0000 | False                      |    1.2410 | 0.3241 |   0.9659 | -0.4913 |   0.6598 |  81495.9637 | -0.0302 |
| gate_rearm_w0.25_lrs1.20                         | rearm                         |   0.2500 |       1.2000 | False                      |    1.2052 | 0.3494 |   0.9522 | -0.5378 |   0.6496 | 174275.0816 | -0.0369 |
| gate_rearm_w0.25_lrs1.10                         | rearm                         |   0.2500 |       1.1000 | False                      |    1.2266 | 0.3317 |   0.9635 | -0.5081 |   0.6529 | 102658.7700 | -0.0386 |
| gate_rearm_w0.25_lrs1.00                         | rearm                         |   0.2500 |       1.0000 | False                      |    1.2508 | 0.3130 |   0.9761 | -0.4769 |   0.6563 |  57995.6365 | -0.0395 |
| gate_rearm_or_stage4_high_strength_w0.25_lrs1.20 | rearm_or_stage4_high_strength |   0.2500 |       1.2000 | False                      |    1.1913 | 0.3581 |   0.9397 | -0.5537 |   0.6467 | 225859.6662 | -0.0405 |

## Top Candidate Switch Stats

| label                                            | gate                          |   weight |   lrs_factor |   upgrade_active_pct |   switches |
|:-------------------------------------------------|:------------------------------|---------:|-------------:|---------------------:|-----------:|
| gate_rearm_w0.25_lrs1.00                         | rearm                         |   0.2500 |       1.0000 |               0.0691 |         36 |
| gate_rearm_w0.25_lrs1.10                         | rearm                         |   0.2500 |       1.1000 |               0.0691 |         36 |
| gate_rearm_w0.25_lrs1.20                         | rearm                         |   0.2500 |       1.2000 |               0.0691 |         36 |
| gate_rearm_w0.50_lrs1.00                         | rearm                         |   0.5000 |       1.0000 |               0.0691 |         36 |
| gate_rearm_w0.50_lrs1.10                         | rearm                         |   0.5000 |       1.1000 |               0.0691 |         36 |
| gate_rearm_w0.50_lrs1.20                         | rearm                         |   0.5000 |       1.2000 |               0.0691 |         36 |
| gate_rearm_w0.75_lrs1.00                         | rearm                         |   0.7500 |       1.0000 |               0.0691 |         36 |
| gate_rearm_w0.75_lrs1.10                         | rearm                         |   0.7500 |       1.1000 |               0.0691 |         36 |
| gate_rearm_w0.75_lrs1.20                         | rearm                         |   0.7500 |       1.2000 |               0.0691 |         36 |
| gate_rearm_w1.00_lrs1.00                         | rearm                         |   1.0000 |       1.0000 |               0.0691 |         36 |
| gate_rearm_w1.00_lrs1.10                         | rearm                         |   1.0000 |       1.1000 |               0.0691 |         36 |
| gate_rearm_w1.00_lrs1.20                         | rearm                         |   1.0000 |       1.2000 |               0.0691 |         36 |
| gate_rearm_or_stage4_rv_lt_70_w0.25_lrs1.00      | rearm_or_stage4_rv_lt_70      |   0.2500 |       1.0000 |               0.5616 |        380 |
| gate_rearm_or_stage4_rv_lt_70_w0.25_lrs1.10      | rearm_or_stage4_rv_lt_70      |   0.2500 |       1.1000 |               0.5616 |        380 |
| gate_rearm_or_stage4_rv_lt_70_w0.25_lrs1.20      | rearm_or_stage4_rv_lt_70      |   0.2500 |       1.2000 |               0.5616 |        380 |
| gate_rearm_or_stage4_rv_lt_70_w0.50_lrs1.00      | rearm_or_stage4_rv_lt_70      |   0.5000 |       1.0000 |               0.5616 |        380 |
| gate_rearm_or_stage4_rv_lt_70_w0.50_lrs1.10      | rearm_or_stage4_rv_lt_70      |   0.5000 |       1.1000 |               0.5616 |        380 |
| gate_rearm_or_stage4_rv_lt_70_w0.50_lrs1.20      | rearm_or_stage4_rv_lt_70      |   0.5000 |       1.2000 |               0.5616 |        380 |
| gate_rearm_or_stage4_rv_lt_70_w0.75_lrs1.00      | rearm_or_stage4_rv_lt_70      |   0.7500 |       1.0000 |               0.5616 |        380 |
| gate_rearm_or_stage4_rv_lt_70_w0.75_lrs1.10      | rearm_or_stage4_rv_lt_70      |   0.7500 |       1.1000 |               0.5616 |        380 |
| gate_rearm_or_stage4_rv_lt_70_w0.75_lrs1.20      | rearm_or_stage4_rv_lt_70      |   0.7500 |       1.2000 |               0.5616 |        380 |
| gate_rearm_or_stage4_rv_lt_70_w1.00_lrs1.00      | rearm_or_stage4_rv_lt_70      |   1.0000 |       1.0000 |               0.5616 |        380 |
| gate_rearm_or_stage4_rv_lt_70_w1.00_lrs1.10      | rearm_or_stage4_rv_lt_70      |   1.0000 |       1.1000 |               0.5616 |        380 |
| gate_rearm_or_stage4_rv_lt_70_w1.00_lrs1.20      | rearm_or_stage4_rv_lt_70      |   1.0000 |       1.2000 |               0.5616 |        380 |
| gate_rearm_or_stage4_high_strength_w0.25_lrs1.20 | rearm_or_stage4_high_strength |   0.2500 |       1.2000 |               0.5243 |        280 |

## Rolling Windows

| label                                       |   window_years |   n_windows |   min_cagr |   median_cagr |   pct_positive_cagr |
|:--------------------------------------------|---------------:|------------:|-----------:|--------------:|--------------------:|
| gate_rearm_w1.00_lrs1.00                    |              3 |         448 |    -0.0282 |        0.2783 |              0.9955 |
| gate_rearm_w1.00_lrs1.00                    |              5 |         424 |     0.0561 |        0.2919 |              1.0000 |
| gate_rearm_w1.00_lrs1.00                    |             10 |         364 |     0.1049 |        0.3052 |              1.0000 |
| gate_rearm_w1.00_lrs1.00                    |             15 |         304 |     0.1680 |        0.2890 |              1.0000 |
| gate_rearm_w1.00_lrs1.10                    |              3 |         448 |    -0.0551 |        0.2948 |              0.9955 |
| gate_rearm_w1.00_lrs1.10                    |              5 |         424 |     0.0435 |        0.3119 |              1.0000 |
| gate_rearm_w1.00_lrs1.10                    |             10 |         364 |     0.1012 |        0.3294 |              1.0000 |
| gate_rearm_w1.00_lrs1.10                    |             15 |         304 |     0.1736 |        0.3096 |              1.0000 |
| gate_rearm_w1.00_lrs1.20                    |              3 |         448 |    -0.0821 |        0.3127 |              0.9955 |
| gate_rearm_w1.00_lrs1.20                    |              5 |         424 |     0.0299 |        0.3294 |              1.0000 |
| gate_rearm_w1.00_lrs1.20                    |             10 |         364 |     0.0965 |        0.3520 |              1.0000 |
| gate_rearm_w1.00_lrs1.20                    |             15 |         304 |     0.1782 |        0.3293 |              1.0000 |
| gate_rearm_w0.75_lrs1.00                    |              3 |         448 |    -0.0192 |        0.2721 |              0.9978 |
| gate_rearm_w0.75_lrs1.00                    |              5 |         424 |     0.0575 |        0.2910 |              1.0000 |
| gate_rearm_w0.75_lrs1.00                    |             10 |         364 |     0.1029 |        0.3004 |              1.0000 |
| gate_rearm_w0.75_lrs1.00                    |             15 |         304 |     0.1664 |        0.2846 |              1.0000 |
| gate_rearm_w0.75_lrs1.10                    |              3 |         448 |    -0.0450 |        0.2884 |              0.9955 |
| gate_rearm_w0.75_lrs1.10                    |              5 |         424 |     0.0454 |        0.3099 |              1.0000 |
| gate_rearm_w0.75_lrs1.10                    |             10 |         364 |     0.0993 |        0.3244 |              1.0000 |
| gate_rearm_w0.75_lrs1.10                    |             15 |         304 |     0.1721 |        0.3053 |              1.0000 |
| gate_rearm_w0.75_lrs1.20                    |              3 |         448 |    -0.0709 |        0.3068 |              0.9955 |
| gate_rearm_w0.75_lrs1.20                    |              5 |         424 |     0.0325 |        0.3268 |              1.0000 |
| gate_rearm_w0.75_lrs1.20                    |             10 |         364 |     0.0947 |        0.3469 |              1.0000 |
| gate_rearm_w0.75_lrs1.20                    |             15 |         304 |     0.1768 |        0.3246 |              1.0000 |
| gate_rearm_or_stage4_rv_lt_70_w0.75_lrs1.20 |              3 |         448 |    -0.0680 |        0.3497 |              0.9911 |
| gate_rearm_or_stage4_rv_lt_70_w0.75_lrs1.20 |              5 |         424 |     0.0034 |        0.3660 |              1.0000 |
| gate_rearm_or_stage4_rv_lt_70_w0.75_lrs1.20 |             10 |         364 |     0.0921 |        0.3977 |              1.0000 |
| gate_rearm_or_stage4_rv_lt_70_w0.75_lrs1.20 |             15 |         304 |     0.2018 |        0.3635 |              1.0000 |
| gate_rearm_or_stage4_rv_lt_70_w0.50_lrs1.20 |              3 |         448 |    -0.0580 |        0.3312 |              0.9955 |
| gate_rearm_or_stage4_rv_lt_70_w0.50_lrs1.20 |              5 |         424 |     0.0102 |        0.3501 |              1.0000 |
| gate_rearm_or_stage4_rv_lt_70_w0.50_lrs1.20 |             10 |         364 |     0.0919 |        0.3774 |              1.0000 |
| gate_rearm_or_stage4_rv_lt_70_w0.50_lrs1.20 |             15 |         304 |     0.1930 |        0.3487 |              1.0000 |
| gate_rearm_or_stage4_rv_lt_70_w0.75_lrs1.10 |              3 |         448 |    -0.0420 |        0.3328 |              0.9955 |
| gate_rearm_or_stage4_rv_lt_70_w0.75_lrs1.10 |              5 |         424 |     0.0143 |        0.3505 |              1.0000 |
| gate_rearm_or_stage4_rv_lt_70_w0.75_lrs1.10 |             10 |         364 |     0.0991 |        0.3741 |              1.0000 |
| gate_rearm_or_stage4_rv_lt_70_w0.75_lrs1.10 |             15 |         304 |     0.1977 |        0.3477 |              1.0000 |
| gate_rearm_or_stage4_rv_lt_70_w1.00_lrs1.20 |              3 |         448 |    -0.0786 |        0.3620 |              0.9844 |
| gate_rearm_or_stage4_rv_lt_70_w1.00_lrs1.20 |              5 |         424 |    -0.0046 |        0.3774 |              0.9976 |
| gate_rearm_or_stage4_rv_lt_70_w1.00_lrs1.20 |             10 |         364 |     0.0910 |        0.4174 |              1.0000 |
| gate_rearm_or_stage4_rv_lt_70_w1.00_lrs1.20 |             15 |         304 |     0.2090 |        0.3761 |              1.0000 |

## Plot

![Pareto equity](plots/pareto_equity.png)

## Method Notes

- The iter030 shell is preserved: ON/OFF signal, ZROZ/CASHX off-leg logic and optional LRS overlay.
- Search only changes the TQQQ turbo gate, turbo blend weight and LRS factor.
- This is economic-first exploration; it is not a mandate pass.
