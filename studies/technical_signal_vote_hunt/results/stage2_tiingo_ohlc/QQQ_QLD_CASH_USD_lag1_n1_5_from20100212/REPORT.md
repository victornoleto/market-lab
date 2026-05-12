# Stage 2 Tiingo OHLC Grid Results

Status: capped exact-grid discovery. This is not a validation verdict.

Branch: `QQQ`
Risk-ons: `QLD_2x`
Off leg: `CASH_USD`
Extra execution lag days: `1`
Redundant signals allowed: `False`
Date window: `2010-02-12` to `full`
Signal subset range: n=1..5
Estimated/configs tested: 7,067,694 / 7,067,694
Windows: QLD_2x: 2010-02-12..2026-04-14 (4,066 bars)
Elapsed seconds: 1189.5

## Top Configs

| branch   | risk_on   |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                      |
|:---------|:----------|----:|----:|----------:|-------:|---------:|--------:|---------:|:-----------------------------------------------------------------------------|
| QQQ      | QLD_2x    |   5 |   3 |    1.4209 | 0.3626 |   1.1900 | -0.3754 |   0.9659 | sma100_gt_sma250|roc10_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70      |
| QQQ      | QLD_2x    |   5 |   3 |    1.4139 | 0.3591 |   1.1869 | -0.4053 |   0.8859 | sma100_gt_sma250|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70|cci20_gt_0      |
| QQQ      | QLD_2x    |   5 |   3 |    1.4089 | 0.3587 |   1.1836 | -0.3490 |   1.0275 | px_gt_sma20|sma100_gt_sma250|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70     |
| QQQ      | QLD_2x    |   5 |   1 |    1.4067 | 0.3695 |   1.0955 | -0.4111 |   0.8989 | px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|cci20_gt_100             |
| QQQ      | QLD_2x    |   5 |   3 |    1.4049 | 0.3543 |   1.1828 | -0.3053 |   1.1604 | px_gt_ema20|sma100_gt_sma250|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70     |
| QQQ      | QLD_2x    |   5 |   1 |    1.3947 | 0.3653 |   1.0864 | -0.4226 |   0.8643 | px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|cci20_gt_100             |
| QQQ      | QLD_2x    |   5 |   1 |    1.3925 | 0.3642 |   1.0839 | -0.4229 |   0.8612 | px_gt_sma50|px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0              |
| QQQ      | QLD_2x    |   5 |   2 |    1.3821 | 0.3608 |   1.0771 | -0.4229 |   0.8533 | px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|atr14_pct_lt_5           |
| QQQ      | QLD_2x    |   5 |   1 |    1.3821 | 0.3608 |   1.0771 | -0.4229 |   0.8533 | px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|close_gt_prior_high20    |
| QQQ      | QLD_2x    |   5 |   1 |    1.3821 | 0.3608 |   1.0771 | -0.4229 |   0.8533 | px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|close_gt_prior_high55    |
| QQQ      | QLD_2x    |   4 |   1 |    1.3821 | 0.3608 |   1.0771 | -0.4229 |   0.8533 | px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0                          |
| QQQ      | QLD_2x    |   5 |   2 |    1.3749 | 0.3587 |   1.0752 | -0.3824 |   0.9380 | px_gt_sma50|px_gt_ema100|rv21_lt_40|rv21_pct_lt_70|ar1_30_gt_0               |
| QQQ      | QLD_2x    |   5 |   2 |    1.3747 | 0.3581 |   1.0734 | -0.3824 |   0.9364 | px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|atr14_pct_lt_5           |
| QQQ      | QLD_2x    |   4 |   1 |    1.3747 | 0.3581 |   1.0734 | -0.3824 |   0.9364 | px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0                          |
| QQQ      | QLD_2x    |   5 |   1 |    1.3747 | 0.3581 |   1.0734 | -0.3824 |   0.9364 | px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|close_gt_prior_high55    |
| QQQ      | QLD_2x    |   5 |   1 |    1.3747 | 0.3581 |   1.0734 | -0.3824 |   0.9364 | px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|close_gt_prior_high20    |
| QQQ      | QLD_2x    |   5 |   1 |    1.3696 | 0.3575 |   1.0635 | -0.4460 |   0.8016 | px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|stoch14_gt_80            |
| QQQ      | QLD_2x    |   5 |   2 |    1.3667 | 0.3540 |   1.0829 | -0.4881 |   0.7253 | px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80              |
| QQQ      | QLD_2x    |   5 |   3 |    1.3614 | 0.3613 |   1.1030 | -0.3671 |   0.9843 | sma50_gt_sma200|roc20_gt_0|roc120_gt_0|rv21_lt_40|ar1_30_gt_0                |
| QQQ      | QLD_2x    |   5 |   3 |    1.3603 | 0.3362 |   1.1420 | -0.3568 |   0.9424 | px_gt_sma20|px_gt_sma150|sma100_gt_sma250|stochrsi14_gt_50|rv21_pct_lt_70    |
| QQQ      | QLD_2x    |   5 |   1 |    1.3592 | 0.3541 |   1.0567 | -0.4460 |   0.7941 | px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|stoch14_gt_80            |
| QQQ      | QLD_2x    |   5 |   1 |    1.3587 | 0.3577 |   1.0504 | -0.4343 |   0.8236 | px_gt_sma20|px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0              |
| QQQ      | QLD_2x    |   5 |   3 |    1.3575 | 0.3356 |   1.1373 | -0.3834 |   0.8754 | px_gt_sma150|sma100_gt_sma250|roc10_gt_0|stochrsi14_gt_50|rv21_pct_lt_70     |
| QQQ      | QLD_2x    |   5 |   2 |    1.3560 | 0.3566 |   1.0710 | -0.4238 |   0.8414 | px_gt_ema100|roc20_gt_0|rv21_pct_lt_70|ar1_30_gt_0|adx14_gt_20               |
| QQQ      | QLD_2x    |   5 |   1 |    1.3555 | 0.3569 |   1.0490 | -0.4397 |   0.8116 | px_gt_sma20|px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0              |
| QQQ      | QLD_2x    |   5 |   2 |    1.3549 | 0.3517 |   1.0600 | -0.3824 |   0.9197 | px_gt_ema50|px_gt_ema100|rv21_lt_40|rv21_pct_lt_70|ar1_30_gt_0               |
| QQQ      | QLD_2x    |   5 |   2 |    1.3544 | 0.3489 |   1.0788 | -0.5016 |   0.6956 | roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100|bear_power_gt_0           |
| QQQ      | QLD_2x    |   5 |   1 |    1.3540 | 0.3564 |   1.0479 | -0.4729 |   0.7536 | px_gt_sma20|px_gt_ema20|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0              |
| QQQ      | QLD_2x    |   4 |   1 |    1.3537 | 0.3824 |   1.0561 | -0.4718 |   0.8105 | px_gt_ema5|px_gt_sma20|roc120_gt_0|ar1_30_gt_0                               |
| QQQ      | QLD_2x    |   5 |   1 |    1.3537 | 0.3824 |   1.0561 | -0.4718 |   0.8105 | px_gt_ema5|px_gt_sma20|roc120_gt_0|ar1_30_gt_0|cci20_gt_100                  |
| QQQ      | QLD_2x    |   5 |   1 |    1.3537 | 0.3824 |   1.0561 | -0.4718 |   0.8105 | px_gt_ema5|px_gt_sma20|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80                 |
| QQQ      | QLD_2x    |   5 |   1 |    1.3537 | 0.3824 |   1.0561 | -0.4718 |   0.8105 | px_gt_ema5|px_gt_sma20|roc120_gt_0|ar1_30_gt_0|bear_power_gt_0               |
| QQQ      | QLD_2x    |   5 |   1 |    1.3537 | 0.3824 |   1.0561 | -0.4718 |   0.8105 | px_gt_ema5|px_gt_sma20|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high20         |
| QQQ      | QLD_2x    |   5 |   1 |    1.3537 | 0.3824 |   1.0561 | -0.4718 |   0.8105 | px_gt_ema5|px_gt_ema10|px_gt_sma20|roc120_gt_0|ar1_30_gt_0                   |
| QQQ      | QLD_2x    |   5 |   1 |    1.3537 | 0.3824 |   1.0561 | -0.4718 |   0.8105 | px_gt_ema5|px_gt_sma20|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high55         |
| QQQ      | QLD_2x    |   5 |   3 |    1.3534 | 0.3406 |   1.1472 | -0.3425 |   0.9944 | sma100_gt_sma250|roc20_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70      |
| QQQ      | QLD_2x    |   5 |   2 |    1.3530 | 0.3696 |   1.0760 | -0.4838 |   0.7639 | px_gt_sma20|sma50_gt_sma150|roc20_gt_0|roc120_gt_0|ar1_30_gt_0               |
| QQQ      | QLD_2x    |   5 |   2 |    1.3529 | 0.3483 |   1.0760 | -0.5101 |   0.6828 | roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80|bear_power_gt_0          |
| QQQ      | QLD_2x    |   4 |   2 |    1.3526 | 0.3483 |   1.0774 | -0.5054 |   0.6891 | roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0                        |
| QQQ      | QLD_2x    |   5 |   2 |    1.3526 | 0.3483 |   1.0774 | -0.5054 |   0.6891 | roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20|bear_power_gt_0  |
| QQQ      | QLD_2x    |   5 |   2 |    1.3526 | 0.3483 |   1.0774 | -0.5054 |   0.6891 | roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55|bear_power_gt_0  |
| QQQ      | QLD_2x    |   5 |   2 |    1.3524 | 0.3719 |   1.0760 | -0.4701 |   0.7911 | px_gt_sma20|sma50_gt_sma200|roc20_gt_0|roc120_gt_0|ar1_30_gt_0               |
| QQQ      | QLD_2x    |   4 |   1 |    1.3518 | 0.3749 |   1.0609 | -0.5184 |   0.7231 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|bear_power_gt_0                          |
| QQQ      | QLD_2x    |   5 |   1 |    1.3518 | 0.3749 |   1.0609 | -0.5184 |   0.7231 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|cci20_gt_100|bear_power_gt_0             |
| QQQ      | QLD_2x    |   5 |   1 |    1.3518 | 0.3749 |   1.0609 | -0.5184 |   0.7231 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80|bear_power_gt_0            |
| QQQ      | QLD_2x    |   5 |   1 |    1.3518 | 0.3749 |   1.0609 | -0.5184 |   0.7231 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high20|bear_power_gt_0    |
| QQQ      | QLD_2x    |   5 |   1 |    1.3518 | 0.3749 |   1.0609 | -0.5184 |   0.7231 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high55|bear_power_gt_0    |
| QQQ      | QLD_2x    |   5 |   2 |    1.3513 | 0.3489 |   1.0707 | -0.5143 |   0.6783 | px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0            |
| QQQ      | QLD_2x    |   5 |   3 |    1.3507 | 0.3470 |   1.0717 | -0.5113 |   0.6785 | px_gt_ema20|roc20_gt_0|roc120_gt_0|rv21_lt_40|atr14_pct_lt_3                 |
| QQQ      | QLD_2x    |   5 |   1 |    1.3505 | 0.3809 |   1.0532 | -0.4718 |   0.8073 | px_gt_ema5|px_gt_sma20|px_gt_ema20|roc120_gt_0|ar1_30_gt_0                   |
| QQQ      | QLD_2x    |   5 |   3 |    1.3499 | 0.3472 |   1.0759 | -0.5054 |   0.6870 | roc20_gt_0|roc120_gt_0|rv21_lt_40|atr14_pct_lt_3|bear_power_gt_0             |
| QQQ      | QLD_2x    |   5 |   2 |    1.3494 | 0.3494 |   1.0728 | -0.3825 |   0.9135 | px_gt_sma10|px_gt_ema100|sma50_gt_sma150|rv21_pct_lt_70|ar1_30_gt_0          |
| QQQ      | QLD_2x    |   5 |   1 |    1.3493 | 0.3807 |   1.0533 | -0.4602 |   0.8273 | px_gt_ema5|px_gt_ema10|px_gt_ema20|roc120_gt_0|ar1_30_gt_0                   |
| QQQ      | QLD_2x    |   5 |   1 |    1.3490 | 0.3526 |   1.0496 | -0.4310 |   0.8180 | px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|bear_power_gt_0          |
| QQQ      | QLD_2x    |   5 |   1 |    1.3484 | 0.3730 |   1.0566 | -0.5184 |   0.7195 | px_gt_sma20|px_gt_ema20|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80                |
| QQQ      | QLD_2x    |   4 |   1 |    1.3484 | 0.3730 |   1.0566 | -0.5184 |   0.7195 | px_gt_sma20|px_gt_ema20|roc120_gt_0|ar1_30_gt_0                              |
| QQQ      | QLD_2x    |   5 |   1 |    1.3484 | 0.3730 |   1.0566 | -0.5184 |   0.7195 | px_gt_sma20|px_gt_ema20|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high20        |
| QQQ      | QLD_2x    |   5 |   1 |    1.3484 | 0.3730 |   1.0566 | -0.5184 |   0.7195 | px_gt_sma20|px_gt_ema20|roc120_gt_0|ar1_30_gt_0|cci20_gt_100                 |
| QQQ      | QLD_2x    |   5 |   1 |    1.3484 | 0.3730 |   1.0566 | -0.5184 |   0.7195 | px_gt_sma20|px_gt_ema20|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high55        |
| QQQ      | QLD_2x    |   5 |   1 |    1.3482 | 0.3729 |   1.0563 | -0.5184 |   0.7193 | px_gt_sma20|px_gt_ema20|roc120_gt_0|ar1_30_gt_0|bear_power_gt_0              |
| QQQ      | QLD_2x    |   5 |   2 |    1.3477 | 0.3480 |   1.0782 | -0.4656 |   0.7473 | px_gt_ema20|px_gt_ema50|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80             |
| QQQ      | QLD_2x    |   5 |   2 |    1.3473 | 0.3567 |   1.0540 | -0.4376 |   0.8152 | px_gt_sma50|px_gt_ema50|roc120_gt_0|rv21_lt_40|ar1_30_gt_0                   |
| QQQ      | QLD_2x    |   5 |   2 |    1.3470 | 0.3475 |   1.0772 | -0.4637 |   0.7494 | px_gt_ema20|px_gt_ema50|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0           |
| QQQ      | QLD_2x    |   5 |   2 |    1.3456 | 0.3632 |   1.0509 | -0.5616 |   0.6468 | px_gt_sma20|roc120_gt_0|rv21_lt_40|ar1_30_gt_0|cci20_gt_0                    |
| QQQ      | QLD_2x    |   5 |   2 |    1.3450 | 0.3822 |   1.0688 | -0.4086 |   0.9353 | px_gt_ema250|sma100_gt_sma250|rsi14_rising|ar1_30_gt_0|cci20_gt_100          |
| QQQ      | QLD_2x    |   5 |   2 |    1.3449 | 0.3755 |   1.0324 | -0.4802 |   0.7820 | sma100_gt_sma250|roc10_gt_0|rsi14_gt_50|rv21_lt_40|ar1_30_gt_0               |
| QQQ      | QLD_2x    |   5 |   2 |    1.3436 | 0.3612 |   1.0431 | -0.5650 |   0.6394 | px_gt_sma10|px_gt_sma20|roc120_gt_0|rv21_lt_40|ar1_30_gt_0                   |
| QQQ      | QLD_2x    |   5 |   2 |    1.3423 | 0.3432 |   1.0629 | -0.5054 |   0.6791 | px_gt_ema50|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0            |
| QQQ      | QLD_2x    |   4 |   1 |    1.3422 | 0.3712 |   1.0537 | -0.5198 |   0.7141 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80                            |
| QQQ      | QLD_2x    |   5 |   1 |    1.3422 | 0.3712 |   1.0537 | -0.5198 |   0.7141 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|cci20_gt_100|close_gt_prior_high20       |
| QQQ      | QLD_2x    |   4 |   1 |    1.3422 | 0.3712 |   1.0537 | -0.5198 |   0.7141 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high20                    |
| QQQ      | QLD_2x    |   5 |   1 |    1.3422 | 0.3712 |   1.0537 | -0.5198 |   0.7141 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80|close_gt_prior_high20      |
| QQQ      | QLD_2x    |   5 |   1 |    1.3422 | 0.3712 |   1.0537 | -0.5198 |   0.7141 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|cci20_gt_100|close_gt_prior_high55       |
| QQQ      | QLD_2x    |   5 |   1 |    1.3422 | 0.3712 |   1.0537 | -0.5198 |   0.7141 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80|cci20_gt_100               |
| QQQ      | QLD_2x    |   4 |   1 |    1.3422 | 0.3712 |   1.0537 | -0.5198 |   0.7141 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|cci20_gt_100                             |
| QQQ      | QLD_2x    |   3 |   1 |    1.3422 | 0.3712 |   1.0537 | -0.5198 |   0.7141 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0                                          |
| QQQ      | QLD_2x    |   4 |   1 |    1.3422 | 0.3712 |   1.0537 | -0.5198 |   0.7141 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high55                    |
| QQQ      | QLD_2x    |   5 |   1 |    1.3422 | 0.3712 |   1.0537 | -0.5198 |   0.7141 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80|close_gt_prior_high55      |
| QQQ      | QLD_2x    |   5 |   2 |    1.3422 | 0.3599 |   1.0506 | -0.5184 |   0.6943 | px_gt_sma20|roc120_gt_0|rv21_lt_40|ar1_30_gt_0|bear_power_gt_0               |
| QQQ      | QLD_2x    |   5 |   2 |    1.3420 | 0.3412 |   1.0623 | -0.4601 |   0.7415 | px_gt_ema50|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100               |
| QQQ      | QLD_2x    |   5 |   1 |    1.3412 | 0.3693 |   1.0386 | -0.4747 |   0.7780 | px_gt_sma20|px_gt_ema20|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0               |
| QQQ      | QLD_2x    |   5 |   1 |    1.3411 | 0.3517 |   1.0382 | -0.4729 |   0.7437 | px_gt_sma20|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|bear_power_gt_0          |
| QQQ      | QLD_2x    |   4 |   1 |    1.3407 | 0.3515 |   1.0380 | -0.4744 |   0.7411 | px_gt_sma20|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0                          |
| QQQ      | QLD_2x    |   5 |   1 |    1.3407 | 0.3515 |   1.0380 | -0.4744 |   0.7411 | px_gt_sma20|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|close_gt_prior_high55    |
| QQQ      | QLD_2x    |   5 |   1 |    1.3407 | 0.3515 |   1.0380 | -0.4744 |   0.7411 | px_gt_sma20|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|cci20_gt_100             |
| QQQ      | QLD_2x    |   5 |   1 |    1.3407 | 0.3515 |   1.0380 | -0.4744 |   0.7411 | px_gt_sma20|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|stoch14_gt_80            |
| QQQ      | QLD_2x    |   5 |   1 |    1.3407 | 0.3515 |   1.0380 | -0.4744 |   0.7411 | px_gt_sma20|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|close_gt_prior_high20    |
| QQQ      | QLD_2x    |   5 |   2 |    1.3404 | 0.3460 |   1.0627 | -0.5333 |   0.6489 | px_gt_sma20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0            |
| QQQ      | QLD_2x    |   5 |   2 |    1.3395 | 0.3542 |   1.0489 | -0.4376 |   0.8094 | px_gt_sma50|roc120_gt_0|rv21_lt_40|ar1_30_gt_0|cci20_gt_100                  |
| QQQ      | QLD_2x    |   5 |   2 |    1.3394 | 0.3642 |   1.0690 | -0.4602 |   0.7915 | px_gt_ema50|sma50_gt_sma200|roc20_gt_0|roc120_gt_0|ar1_30_gt_0               |
| QQQ      | QLD_2x    |   4 |   1 |    1.3393 | 0.3730 |   1.0558 | -0.5320 |   0.7011 | roc10_gt_0|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high20                     |
| QQQ      | QLD_2x    |   3 |   1 |    1.3393 | 0.3730 |   1.0558 | -0.5320 |   0.7011 | roc10_gt_0|roc120_gt_0|ar1_30_gt_0                                           |
| QQQ      | QLD_2x    |   5 |   1 |    1.3393 | 0.3730 |   1.0558 | -0.5320 |   0.7011 | roc10_gt_0|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80|close_gt_prior_high20       |
| QQQ      | QLD_2x    |   5 |   1 |    1.3393 | 0.3730 |   1.0558 | -0.5320 |   0.7011 | roc10_gt_0|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80|close_gt_prior_high55       |
| QQQ      | QLD_2x    |   4 |   1 |    1.3393 | 0.3730 |   1.0558 | -0.5320 |   0.7011 | roc10_gt_0|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high55                     |
| QQQ      | QLD_2x    |   5 |   1 |    1.3393 | 0.3730 |   1.0558 | -0.5320 |   0.7011 | roc10_gt_0|roc120_gt_0|ar1_30_gt_0|cci20_gt_100|close_gt_prior_high20        |
| QQQ      | QLD_2x    |   4 |   1 |    1.3393 | 0.3730 |   1.0558 | -0.5320 |   0.7011 | roc10_gt_0|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80                             |
| QQQ      | QLD_2x    |   5 |   1 |    1.3393 | 0.3730 |   1.0558 | -0.5320 |   0.7011 | roc10_gt_0|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80|cci20_gt_100                |
| QQQ      | QLD_2x    |   5 |   1 |    1.3393 | 0.3730 |   1.0558 | -0.5320 |   0.7011 | roc10_gt_0|roc120_gt_0|ar1_30_gt_0|cci20_gt_100|close_gt_prior_high55        |
| QQQ      | QLD_2x    |   4 |   1 |    1.3393 | 0.3730 |   1.0558 | -0.5320 |   0.7011 | roc10_gt_0|roc120_gt_0|ar1_30_gt_0|cci20_gt_100                              |
| QQQ      | QLD_2x    |   5 |   2 |    1.3390 | 0.3734 |   1.0286 | -0.4827 |   0.7735 | sma100_gt_sma250|roc10_gt_0|rv21_lt_40|ar1_30_gt_0|cci20_gt_0                |
| QQQ      | QLD_2x    |   5 |   3 |    1.3389 | 0.3481 |   1.0773 | -0.5250 |   0.6630 | px_gt_sma10|sma100_gt_sma250|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3           |
| QQQ      | QLD_2x    |   5 |   1 |    1.3387 | 0.3492 |   1.0429 | -0.4310 |   0.8103 | px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|bear_power_gt_0          |
| QQQ      | QLD_2x    |   5 |   1 |    1.3386 | 0.3581 |   1.0289 | -0.4745 |   0.7547 | px_gt_ema5|px_gt_sma20|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0               |
| QQQ      | QLD_2x    |   5 |   2 |    1.3386 | 0.3447 |   1.0632 | -0.5076 |   0.6790 | px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100               |
| QQQ      | QLD_2x    |   5 |   2 |    1.3382 | 0.3615 |   1.0430 | -0.5953 |   0.6073 | px_gt_sma10|roc10_gt_0|roc120_gt_0|rv21_lt_40|ar1_30_gt_0                    |
| QQQ      | QLD_2x    |   5 |   2 |    1.3378 | 0.3538 |   1.0474 | -0.4376 |   0.8084 | px_gt_ema50|roc120_gt_0|rv21_lt_40|ar1_30_gt_0|cci20_gt_100                  |
| QQQ      | QLD_2x    |   5 |   2 |    1.3377 | 0.3642 |   1.0677 | -0.4602 |   0.7914 | px_gt_sma20|px_gt_ema50|sma50_gt_sma200|roc120_gt_0|ar1_30_gt_0              |
| QQQ      | QLD_2x    |   5 |   2 |    1.3377 | 0.3446 |   1.0579 | -0.5142 |   0.6701 | px_gt_sma20|px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                |
| QQQ      | QLD_2x    |   5 |   3 |    1.3375 | 0.3326 |   1.1246 | -0.3139 |   1.0596 | px_gt_ema150|sma100_gt_sma250|macd_hist_gt_0|roc10_gt_0|rv21_pct_lt_70       |
| QQQ      | QLD_2x    |   5 |   3 |    1.3372 | 0.3392 |   1.0769 | -0.3390 |   1.0004 | px_gt_ema20|px_gt_ema50|px_gt_ema250|roc120_gt_0|atr14_pct_lt_3              |
| QQQ      | QLD_2x    |   5 |   2 |    1.3368 | 0.3441 |   1.0618 | -0.5113 |   0.6729 | px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55      |
| QQQ      | QLD_2x    |   5 |   2 |    1.3368 | 0.3441 |   1.0618 | -0.5113 |   0.6729 | px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20      |
| QQQ      | QLD_2x    |   4 |   2 |    1.3368 | 0.3441 |   1.0618 | -0.5113 |   0.6729 | px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                            |
| QQQ      | QLD_2x    |   4 |   1 |    1.3366 | 0.3462 |   1.0489 | -0.4111 |   0.8421 | px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|cci20_gt_100                         |
| QQQ      | QLD_2x    |   5 |   1 |    1.3366 | 0.3462 |   1.0489 | -0.4111 |   0.8421 | px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|cci20_gt_100|close_gt_prior_high55   |
| QQQ      | QLD_2x    |   5 |   1 |    1.3366 | 0.3462 |   1.0489 | -0.4111 |   0.8421 | px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|cci20_gt_100|close_gt_prior_high20   |
| QQQ      | QLD_2x    |   5 |   2 |    1.3365 | 0.3438 |   1.0620 | -0.3446 |   0.9976 | px_gt_ema10|px_gt_ema100|sma50_gt_sma150|rv21_pct_lt_70|ar1_30_gt_0          |
| QQQ      | QLD_2x    |   5 |   2 |    1.3364 | 0.3575 |   1.0462 | -0.5015 |   0.7128 | px_gt_sma20|roc120_gt_0|rv21_lt_40|ar1_30_gt_0|stoch14_gt_80                 |
| QQQ      | QLD_2x    |   5 |   2 |    1.3359 | 0.3844 |   1.0334 | -0.4860 |   0.7910 | sma100_gt_sma250|roc10_gt_0|roc120_gt_0|ar1_30_gt_0|atr14_pct_lt_5           |
| QQQ      | QLD_2x    |   5 |   1 |    1.3356 | 0.3740 |   1.0302 | -0.4602 |   0.8127 | px_gt_ema5|px_gt_sma20|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0                |
| QQQ      | QLD_2x    |   5 |   3 |    1.3355 | 0.3262 |   1.1276 | -0.3138 |   1.0394 | px_gt_ema20|px_gt_sma150|sma100_gt_sma250|stochrsi14_gt_50|rv21_pct_lt_70    |
| QQQ      | QLD_2x    |   5 |   2 |    1.3355 | 0.3429 |   1.0584 | -0.5113 |   0.6706 | px_gt_ema20|px_gt_ema50|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                |
| QQQ      | QLD_2x    |   5 |   1 |    1.3355 | 0.3660 |   1.0376 | -0.5184 |   0.7059 | px_gt_sma20|px_gt_ema20|roc120_gt_0|rv21_pct_lt_50|ar1_30_gt_0               |
| QQQ      | QLD_2x    |   5 |   2 |    1.3352 | 0.3472 |   1.0558 | -0.5522 |   0.6288 | px_gt_sma20|roc10_gt_0|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                 |
| QQQ      | QLD_2x    |   5 |   1 |    1.3343 | 0.3753 |   1.0409 | -0.4602 |   0.8156 | px_gt_ema5|px_gt_sma10|px_gt_ema20|roc120_gt_0|ar1_30_gt_0                   |
| QQQ      | QLD_2x    |   5 |   2 |    1.3343 | 0.3440 |   1.0616 | -0.4934 |   0.6973 | px_gt_sma20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80              |
| QQQ      | QLD_2x    |   5 |   2 |    1.3339 | 0.3467 |   1.0552 | -0.5309 |   0.6530 | roc10_gt_0|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0                  |
| QQQ      | QLD_2x    |   5 |   3 |    1.3339 | 0.3235 |   1.1251 | -0.2878 |   1.1242 | px_gt_sma150|sma100_gt_sma250|roc20_gt_0|stochrsi14_gt_50|rv21_pct_lt_70     |
| QQQ      | QLD_2x    |   5 |   2 |    1.3339 | 0.3723 |   1.0287 | -0.4917 |   0.7572 | sma100_gt_sma250|roc10_gt_0|rv21_lt_40|ar1_30_gt_0|stoch14_gt_80             |
| QQQ      | QLD_2x    |   5 |   1 |    1.3334 | 0.3722 |   1.0320 | -0.4718 |   0.7889 | px_gt_ema5|px_gt_sma20|roc120_gt_0|rv21_pct_lt_50|ar1_30_gt_0                |
| QQQ      | QLD_2x    |   5 |   1 |    1.3334 | 0.3486 |   1.0373 | -0.4097 |   0.8509 | px_gt_ema20|px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0              |
| QQQ      | QLD_2x    |   5 |   2 |    1.3333 | 0.3422 |   1.0641 | -0.3492 |   0.9799 | px_gt_sma20|px_gt_ema100|sma50_gt_sma150|rv21_pct_lt_70|ar1_30_gt_0          |
| QQQ      | QLD_2x    |   5 |   2 |    1.3328 | 0.3512 |   1.0501 | -0.4426 |   0.7935 | px_gt_ema10|px_gt_ema100|sma100_gt_sma250|rv21_pct_lt_70|ar1_30_gt_0         |
| QQQ      | QLD_2x    |   5 |   2 |    1.3328 | 0.3493 |   1.0547 | -0.4060 |   0.8605 | px_gt_sma20|px_gt_ema100|sma100_gt_sma250|rv21_pct_lt_70|ar1_30_gt_0         |
| QQQ      | QLD_2x    |   5 |   2 |    1.3328 | 0.3732 |   1.0502 | -0.4246 |   0.8788 | sma100_gt_sma250|rv21_lt_40|ar1_30_gt_0|cci20_gt_100|close_gt_prior_high55   |
| QQQ      | QLD_2x    |   4 |   2 |    1.3328 | 0.3732 |   1.0502 | -0.4246 |   0.8788 | sma100_gt_sma250|rv21_lt_40|ar1_30_gt_0|cci20_gt_100                         |
| QQQ      | QLD_2x    |   5 |   2 |    1.3326 | 0.3528 |   1.0356 | -0.3660 |   0.9639 | px_gt_ema50|roc120_gt_0|rv21_lt_40|rv21_pct_lt_70|ar1_30_gt_0                |
| QQQ      | QLD_2x    |   5 |   1 |    1.3326 | 0.3744 |   1.0390 | -0.4955 |   0.7556 | px_gt_ema5|px_gt_sma20|px_gt_ema50|roc120_gt_0|ar1_30_gt_0                   |
| QQQ      | QLD_2x    |   5 |   2 |    1.3323 | 0.3596 |   1.0648 | -0.4602 |   0.7813 | px_gt_sma20|px_gt_ema50|sma50_gt_sma150|roc120_gt_0|ar1_30_gt_0              |
| QQQ      | QLD_2x    |   5 |   1 |    1.3321 | 0.3674 |   1.0437 | -0.5269 |   0.6974 | px_gt_sma20|px_gt_ema20|px_gt_ema50|roc120_gt_0|ar1_30_gt_0                  |
| QQQ      | QLD_2x    |   5 |   2 |    1.3315 | 0.3427 |   1.0562 | -0.5174 |   0.6623 | px_gt_sma20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80              |
| QQQ      | QLD_2x    |   5 |   1 |    1.3314 | 0.3745 |   1.0435 | -0.4852 |   0.7719 | px_gt_ema5|px_gt_ema10|roc120_gt_0|ar1_30_gt_0|cci20_gt_100                  |
| QQQ      | QLD_2x    |   5 |   1 |    1.3314 | 0.3745 |   1.0435 | -0.4852 |   0.7719 | px_gt_ema5|px_gt_ema10|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high20         |
| QQQ      | QLD_2x    |   5 |   1 |    1.3314 | 0.3745 |   1.0435 | -0.4852 |   0.7719 | px_gt_ema5|px_gt_ema10|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80                 |
| QQQ      | QLD_2x    |   4 |   1 |    1.3314 | 0.3745 |   1.0435 | -0.4852 |   0.7719 | px_gt_ema5|px_gt_ema10|roc120_gt_0|ar1_30_gt_0                               |
| QQQ      | QLD_2x    |   5 |   1 |    1.3314 | 0.3745 |   1.0435 | -0.4852 |   0.7719 | px_gt_ema5|px_gt_ema10|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high55         |
| QQQ      | QLD_2x    |   5 |   2 |    1.3313 | 0.3551 |   1.0416 | -0.5001 |   0.7101 | px_gt_ema20|roc120_gt_0|rv21_lt_40|ar1_30_gt_0|stoch14_gt_80                 |
| QQQ      | QLD_2x    |   5 |   2 |    1.3312 | 0.3708 |   1.0233 | -0.5144 |   0.7208 | px_gt_sma20|sma100_gt_sma250|roc10_gt_0|rv21_lt_40|ar1_30_gt_0               |
| QQQ      | QLD_2x    |   5 |   1 |    1.3312 | 0.3735 |   1.0371 | -0.5069 |   0.7369 | px_gt_ema5|px_gt_sma20|px_gt_sma50|roc120_gt_0|ar1_30_gt_0                   |
| QQQ      | QLD_2x    |   5 |   3 |    1.3311 | 0.3431 |   1.0784 | -0.4387 |   0.7819 | px_gt_ema20|sma50_gt_sma200|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0            |
| QQQ      | QLD_2x    |   5 |   1 |    1.3311 | 0.3481 |   1.0364 | -0.4525 |   0.7692 | px_gt_ema20|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|bear_power_gt_0          |
| QQQ      | QLD_2x    |   5 |   1 |    1.3308 | 0.3548 |   1.0265 | -0.4403 |   0.8058 | px_gt_ema5|px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0               |
| QQQ      | QLD_2x    |   5 |   2 |    1.3308 | 0.3424 |   1.0637 | -0.4126 |   0.8298 | px_gt_ema20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80              |
| QQQ      | QLD_2x    |   5 |   1 |    1.3308 | 0.3666 |   1.0418 | -0.5376 |   0.6819 | px_gt_sma20|px_gt_ema20|px_gt_sma50|roc120_gt_0|ar1_30_gt_0                  |
| QQQ      | QLD_2x    |   5 |   2 |    1.3308 | 0.3376 |   1.0550 | -0.4817 |   0.7008 | px_gt_ema50|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55      |
| QQQ      | QLD_2x    |   4 |   2 |    1.3308 | 0.3376 |   1.0550 | -0.4817 |   0.7008 | px_gt_ema50|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                            |
| QQQ      | QLD_2x    |   5 |   2 |    1.3308 | 0.3376 |   1.0550 | -0.4817 |   0.7008 | px_gt_ema50|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20      |
| QQQ      | QLD_2x    |   5 |   1 |    1.3306 | 0.3735 |   1.0377 | -0.4869 |   0.7672 | px_gt_ema5|px_gt_ema10|px_gt_sma50|roc120_gt_0|ar1_30_gt_0                   |
| QQQ      | QLD_2x    |   5 |   2 |    1.3305 | 0.3335 |   1.0928 | -0.4074 |   0.8185 | macd_hist_gt_0|roc10_gt_0|roc120_gt_0|rv21_pct_lt_70|stoch14_gt_80           |
| QQQ      | QLD_2x    |   5 |   2 |    1.3305 | 0.3432 |   1.0614 | -0.4390 |   0.7818 | px_gt_ema20|px_gt_ema50|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3                |
| QQQ      | QLD_2x    |   5 |   2 |    1.3304 | 0.3570 |   1.0372 | -0.5290 |   0.6749 | roc10_gt_0|roc120_gt_0|rv21_lt_40|ar1_30_gt_0|cci20_gt_0                     |
| QQQ      | QLD_2x    |   5 |   2 |    1.3302 | 0.3555 |   1.0327 | -0.5861 |   0.6065 | px_gt_ema10|px_gt_sma20|roc120_gt_0|rv21_lt_40|ar1_30_gt_0                   |
| QQQ      | QLD_2x    |   4 |   2 |    1.3302 | 0.3416 |   1.0693 | -0.4405 |   0.7754 | px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80                         |
| QQQ      | QLD_2x    |   5 |   2 |    1.3302 | 0.3416 |   1.0693 | -0.4405 |   0.7754 | px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80|close_gt_prior_high20   |
| QQQ      | QLD_2x    |   5 |   2 |    1.3302 | 0.3416 |   1.0693 | -0.4405 |   0.7754 | px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80|cci20_gt_100            |
| QQQ      | QLD_2x    |   5 |   2 |    1.3302 | 0.3416 |   1.0693 | -0.4405 |   0.7754 | px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80|close_gt_prior_high55   |
| QQQ      | QLD_2x    |   4 |   2 |    1.3301 | 0.3426 |   1.0586 | -0.4934 |   0.6944 | px_gt_sma20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3                            |
| QQQ      | QLD_2x    |   5 |   2 |    1.3301 | 0.3426 |   1.0586 | -0.4934 |   0.6944 | px_gt_sma20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100               |
| QQQ      | QLD_2x    |   5 |   2 |    1.3301 | 0.3426 |   1.0586 | -0.4934 |   0.6944 | px_gt_sma20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55      |
| QQQ      | QLD_2x    |   5 |   2 |    1.3301 | 0.3426 |   1.0586 | -0.4934 |   0.6944 | px_gt_sma20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20      |
| QQQ      | QLD_2x    |   5 |   2 |    1.3301 | 0.3417 |   1.0659 | -0.4563 |   0.7488 | px_gt_ema20|px_gt_ema50|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100              |
| QQQ      | QLD_2x    |   5 |   2 |    1.3300 | 0.3542 |   1.0552 | -0.3813 |   0.9290 | px_gt_sma20|sma100_gt_sma250|roc60_gt_0|rv21_pct_lt_70|ar1_30_gt_0           |
| QQQ      | QLD_2x    |   5 |   1 |    1.3298 | 0.3477 |   1.0355 | -0.4165 |   0.8348 | px_gt_ema20|px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0              |
| QQQ      | QLD_2x    |   5 |   2 |    1.3298 | 0.3623 |   1.0738 | -0.4602 |   0.7872 | sma50_gt_sma200|roc20_gt_0|roc120_gt_0|ar1_30_gt_0|cci20_gt_100              |
| QQQ      | QLD_2x    |   5 |   2 |    1.3297 | 0.3697 |   1.0235 | -0.4938 |   0.7486 | px_gt_sma20|sma100_gt_sma250|rv21_lt_40|ar1_30_gt_0|bear_power_gt_0          |
| QQQ      | QLD_2x    |   4 |   2 |    1.3295 | 0.3412 |   1.0683 | -0.4386 |   0.7779 | px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0                       |
| QQQ      | QLD_2x    |   5 |   2 |    1.3295 | 0.3412 |   1.0683 | -0.4386 |   0.7779 | px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20|bear_power_gt_0 |
| QQQ      | QLD_2x    |   5 |   2 |    1.3295 | 0.3412 |   1.0683 | -0.4386 |   0.7779 | px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55|bear_power_gt_0 |
| QQQ      | QLD_2x    |   5 |   2 |    1.3295 | 0.3412 |   1.0683 | -0.4386 |   0.7779 | px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100|bear_power_gt_0          |
| QQQ      | QLD_2x    |   5 |   1 |    1.3295 | 0.3639 |   1.0372 | -0.4602 |   0.7907 | px_gt_sma50|px_gt_ema50|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0               |
| QQQ      | QLD_2x    |   5 |   3 |    1.3292 | 0.3281 |   1.1130 | -0.3834 |   0.8560 | px_gt_ema150|sma100_gt_sma250|roc10_gt_0|stochrsi14_gt_50|rv21_pct_lt_70     |
| QQQ      | QLD_2x    |   5 |   1 |    1.3291 | 0.3638 |   1.0377 | -0.4602 |   0.7905 | px_gt_sma50|px_gt_ema100|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0              |
| QQQ      | QLD_2x    |   5 |   2 |    1.3290 | 0.3692 |   1.0232 | -0.4760 |   0.7757 | px_gt_sma20|sma100_gt_sma250|rv21_lt_40|ar1_30_gt_0|stoch14_gt_80            |
| QQQ      | QLD_2x    |   5 |   1 |    1.3289 | 0.3646 |   1.0294 | -0.4747 |   0.7680 | px_gt_sma20|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0|bear_power_gt_0           |
| QQQ      | QLD_2x    |   4 |   1 |    1.3286 | 0.3645 |   1.0292 | -0.4762 |   0.7654 | px_gt_sma20|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0                           |
| QQQ      | QLD_2x    |   5 |   1 |    1.3286 | 0.3645 |   1.0292 | -0.4762 |   0.7654 | px_gt_sma20|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0|close_gt_prior_high20     |
| QQQ      | QLD_2x    |   5 |   1 |    1.3286 | 0.3645 |   1.0292 | -0.4762 |   0.7654 | px_gt_sma20|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0|cci20_gt_100              |
| QQQ      | QLD_2x    |   5 |   1 |    1.3286 | 0.3645 |   1.0292 | -0.4762 |   0.7654 | px_gt_sma20|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0|stoch14_gt_80             |
| QQQ      | QLD_2x    |   5 |   1 |    1.3286 | 0.3645 |   1.0292 | -0.4762 |   0.7654 | px_gt_sma20|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0|close_gt_prior_high55     |
| QQQ      | QLD_2x    |   5 |   2 |    1.3283 | 0.3411 |   1.0645 | -0.4604 |   0.7408 | px_gt_ema20|px_gt_ema50|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55     |
| QQQ      | QLD_2x    |   4 |   2 |    1.3283 | 0.3411 |   1.0645 | -0.4604 |   0.7408 | px_gt_ema20|px_gt_ema50|roc120_gt_0|atr14_pct_lt_3                           |
| QQQ      | QLD_2x    |   5 |   2 |    1.3283 | 0.3411 |   1.0645 | -0.4604 |   0.7408 | px_gt_ema20|px_gt_ema50|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20     |
| QQQ      | QLD_2x    |   5 |   2 |    1.3283 | 0.3613 |   1.0671 | -0.4602 |   0.7851 | px_gt_ema20|px_gt_ema50|sma50_gt_sma200|roc120_gt_0|ar1_30_gt_0              |
| QQQ      | QLD_2x    |   5 |   3 |    1.3282 | 0.3319 |   1.1086 | -0.3229 |   1.0280 | px_gt_sma10|px_gt_ema20|sma100_gt_sma250|sma50_gt_sma150|rv21_pct_lt_70      |
| QQQ      | QLD_2x    |   5 |   1 |    1.3281 | 0.3729 |   1.0359 | -0.4718 |   0.7903 | px_gt_ema5|px_gt_sma10|px_gt_sma20|roc120_gt_0|ar1_30_gt_0                   |
| QQQ      | QLD_2x    |   5 |   2 |    1.3280 | 0.3426 |   1.0602 | -0.5205 |   0.6582 | px_gt_sma20|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0|bear_power_gt_0            |
| QQQ      | QLD_2x    |   5 |   2 |    1.3278 | 0.3418 |   1.0562 | -0.5299 |   0.6450 | px_gt_sma20|px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0                |
| QQQ      | QLD_2x    |   5 |   2 |    1.3278 | 0.3401 |   1.0675 | -0.3328 |   1.0219 | px_gt_ema20|px_gt_ema100|sma50_gt_sma150|rv21_pct_lt_70|ar1_30_gt_0          |
| QQQ      | QLD_2x    |   5 |   1 |    1.3272 | 0.3488 |   1.0297 | -0.5099 |   0.6841 | px_gt_sma20|px_gt_ema100|roc20_gt_0|rv21_pct_lt_70|ar1_30_gt_0               |

## Method Notes

- Top rows are retained by Sortino, then CAGR, then Calmar.
- Signals are lagged one base bar before returns to avoid same-close look-ahead; `extra_lag_days` adds operational execution delay `[advances_fin_ml, p.31-34]`.
- Redundant signal groups are excluded by default, including equivalent MACD forms and nested thresholds.
- All evaluated configs must be included in later DSR trial accounting `[advances_fin_ml, p.222-223]`.
