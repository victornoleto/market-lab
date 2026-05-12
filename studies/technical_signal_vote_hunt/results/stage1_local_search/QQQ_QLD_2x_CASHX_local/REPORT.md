# Stage 1 Local Search Results

Status: exact one-edit neighborhood diagnostic. This is not a deploy verdict.

Branch: `QQQ`
Risk-on: `QLD_2x`
Off leg: `CASHX`
Base k: `5`
Base signals: `px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0`
Neighbor subsets: 216
Configs tested: 1,531
Elapsed seconds: 1.3

## Base Incumbent

|   fitness |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                              |
|----------:|----:|----:|----------:|-------:|---------:|--------:|---------:|:-------------------------------------------------------------------------------------|
|    1.0312 |   7 |   5 |    0.9273 | 0.2434 |   0.8803 | -0.5965 |   0.4081 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0 |

## Top Local Candidates

| neighborhood   | change                         |   fitness |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                                              |
|:---------------|:-------------------------------|----------:|----:|----:|----------:|-------:|---------:|--------:|---------:|:-----------------------------------------------------------------------------------------------------|
| add1           | +roc120_gt_0                   |    1.0870 |   8 |   6 |    0.9257 | 0.2399 |   0.8851 | -0.3969 |   0.6043 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0     |
| swap1          | -px_gt_ema100+roc120_gt_0      |    1.0849 |   7 |   5 |    0.9323 | 0.2431 |   0.8834 | -0.4489 |   0.5415 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0                  |
| drop1          | -px_gt_sma10                   |    1.0335 |   6 |   5 |    0.8696 | 0.2207 |   0.8503 | -0.3923 |   0.5625 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                             |
| swap1          | -px_gt_sma10+rsi14_gt_50       |    1.0331 |   7 |   5 |    0.9092 | 0.2353 |   0.8606 | -0.5082 |   0.4630 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50                 |
| base           | none                           |    1.0312 |   7 |   5 |    0.9273 | 0.2434 |   0.8803 | -0.5965 |   0.4081 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema100+px_gt_sma250     |    1.0238 |   7 |   5 |    0.9063 | 0.2362 |   0.8624 | -0.5307 |   0.4451 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema200+roc120_gt_0      |    1.0231 |   7 |   5 |    0.9094 | 0.2361 |   0.8627 | -0.5423 |   0.4353 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0                  |
| swap1          | -px_gt_ema250+roc120_gt_0      |    1.0226 |   7 |   5 |    0.9093 | 0.2355 |   0.8611 | -0.5423 |   0.4343 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0|roc120_gt_0                  |
| add1           | +px_gt_sma50                   |    1.0222 |   8 |   6 |    0.8827 | 0.2253 |   0.8492 | -0.4137 |   0.5445 | px_gt_sma10|px_gt_sma20|px_gt_sma50|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0     |
| swap1          | -px_gt_ema100+px_gt_sma100     |    1.0193 |   7 |   5 |    0.9096 | 0.2371 |   0.8667 | -0.5584 |   0.4246 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma10+px_gt_ema20       |    1.0192 |   7 |   5 |    0.9141 | 0.2380 |   0.8668 | -0.5765 |   0.4128 | px_gt_sma20|px_gt_ema20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma20+rsi14_gt_50       |    1.0191 |   7 |   5 |    0.9164 | 0.2393 |   0.8661 | -0.5885 |   0.4066 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50                 |
| swap1          | -px_gt_sma10+px_gt_ema150      |    1.0178 |   7 |   6 |    0.8652 | 0.2192 |   0.8462 | -0.3923 |   0.5589 | px_gt_sma20|px_gt_ema100|px_gt_ema150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                |
| swap1          | -roc60_gt_0+roc120_gt_0        |    1.0177 |   7 |   5 |    0.8803 | 0.2244 |   0.8283 | -0.4424 |   0.5073 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc120_gt_0                |
| swap1          | -px_gt_sma10+px_gt_ema10       |    1.0170 |   7 |   5 |    0.9262 | 0.2434 |   0.8808 | -0.6433 |   0.3783 | px_gt_ema10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma20+stochrsi14_gt_50  |    1.0115 |   7 |   5 |    0.9044 | 0.2355 |   0.8565 | -0.5626 |   0.4185 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|stochrsi14_gt_50            |
| swap1          | -px_gt_sma20+macd_gt_signal    |    1.0076 |   7 |   5 |    0.9003 | 0.2330 |   0.8541 | -0.5547 |   0.4201 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|macd_gt_signal|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_sma20+macd_hist_gt_0    |    1.0076 |   7 |   5 |    0.9003 | 0.2330 |   0.8541 | -0.5547 |   0.4201 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|macd_hist_gt_0|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_sma10+px_gt_sma100      |    1.0071 |   7 |   6 |    0.8546 | 0.2166 |   0.8494 | -0.3863 |   0.5608 | px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                |
| swap1          | -px_gt_sma10+px_gt_sma250      |    1.0060 |   7 |   6 |    0.8558 | 0.2169 |   0.8423 | -0.3923 |   0.5530 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0                |
| swap1          | -px_gt_ema200+px_gt_sma250     |    1.0049 |   7 |   5 |    0.9083 | 0.2375 |   0.8651 | -0.6050 |   0.3926 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| add1           | +px_gt_sma250                  |    1.0047 |   8 |   6 |    0.8937 | 0.2313 |   0.8599 | -0.5063 |   0.4568 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0    |
| swap1          | -px_gt_sma20+px_gt_ema20       |    1.0043 |   7 |   5 |    0.9033 | 0.2362 |   0.8594 | -0.5854 |   0.4035 | px_gt_sma10|px_gt_ema20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -roc60_gt_0+px_gt_sma100       |    1.0021 |   7 |   5 |    0.9047 | 0.2349 |   0.8539 | -0.5942 |   0.3954 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0               |
| swap1          | -px_gt_ema250+px_gt_sma250     |    1.0001 |   7 |   5 |    0.9046 | 0.2363 |   0.8616 | -0.6050 |   0.3905 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_sma250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema100+sma50_gt_sma200  |    0.9999 |   7 |   5 |    0.8876 | 0.2304 |   0.8480 | -0.5307 |   0.4341 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|sma50_gt_sma200|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_ema100+sma50_gt_sma150  |    0.9975 |   7 |   5 |    0.8742 | 0.2230 |   0.8333 | -0.4774 |   0.4671 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|sma50_gt_sma150|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_ema200+px_gt_sma100     |    0.9935 |   7 |   5 |    0.8811 | 0.2282 |   0.8390 | -0.5247 |   0.4350 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema200+px_gt_sma200     |    0.9935 |   7 |   5 |    0.8988 | 0.2329 |   0.8527 | -0.5978 |   0.3896 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma10+roc120_gt_0       |    0.9915 |   7 |   6 |    0.8476 | 0.2162 |   0.8431 | -0.4054 |   0.5333 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0                 |
| swap1          | -px_gt_ema200+sma50_gt_sma200  |    0.9882 |   7 |   5 |    0.8932 | 0.2328 |   0.8533 | -0.5965 |   0.3903 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|sma50_gt_sma200|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_ema100+px_gt_sma150     |    0.9870 |   7 |   5 |    0.9028 | 0.2336 |   0.8576 | -0.6384 |   0.3659 | px_gt_sma10|px_gt_sma20|px_gt_sma150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| drop1          | -px_gt_ema100                  |    0.9855 |   6 |   4 |    0.9067 | 0.2382 |   0.8481 | -0.7136 |   0.3338 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                              |
| swap1          | -px_gt_sma10+px_gt_sma200      |    0.9842 |   7 |   6 |    0.8389 | 0.2121 |   0.8287 | -0.3923 |   0.5407 | px_gt_sma20|px_gt_ema100|px_gt_sma200|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                |
| swap1          | -px_gt_sma10+sma20_gt_sma100   |    0.9840 |   7 |   6 |    0.8575 | 0.2193 |   0.8695 | -0.4585 |   0.4784 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma20_gt_sma100|roc20_gt_0|roc60_gt_0             |
| swap1          | -px_gt_sma10+rv21_pct_lt_50    |    0.9838 |   7 |   5 |    0.8505 | 0.2095 |   0.7915 | -0.4154 |   0.5043 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rv21_pct_lt_50              |
| swap1          | -px_gt_ema250+px_gt_sma200     |    0.9837 |   7 |   5 |    0.8915 | 0.2299 |   0.8442 | -0.5978 |   0.3846 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma200|px_gt_ema200|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema100+px_gt_sma200     |    0.9833 |   7 |   5 |    0.8916 | 0.2290 |   0.8446 | -0.5970 |   0.3836 | px_gt_sma10|px_gt_sma20|px_gt_sma200|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| add1           | +rv21_pct_lt_70                |    0.9813 |   8 |   5 |    0.8955 | 0.2257 |   0.8005 | -0.5725 |   0.3943 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rv21_pct_lt_70  |
| swap1          | -px_gt_sma10+px_gt_sma150      |    0.9803 |   7 |   6 |    0.8483 | 0.2155 |   0.8394 | -0.4339 |   0.4968 | px_gt_sma20|px_gt_ema100|px_gt_sma150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                |
| swap1          | -px_gt_ema250+sma50_gt_sma200  |    0.9800 |   7 |   5 |    0.8871 | 0.2303 |   0.8463 | -0.5965 |   0.3861 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|sma50_gt_sma200|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_ema250+px_gt_sma100     |    0.9794 |   7 |   5 |    0.8706 | 0.2242 |   0.8276 | -0.5247 |   0.4272 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0                 |
| add1           | +sma50_gt_sma200               |    0.9782 |   8 |   6 |    0.8730 | 0.2248 |   0.8432 | -0.5063 |   0.4440 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma50_gt_sma200|roc20_gt_0|roc60_gt_0 |
| swap1          | -px_gt_sma10+stochrsi14_gt_50  |    0.9755 |   7 |   5 |    0.8832 | 0.2273 |   0.8379 | -0.5897 |   0.3854 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|stochrsi14_gt_50            |
| swap1          | -px_gt_sma10+sma100_gt_sma250  |    0.9748 |   7 |   6 |    0.8315 | 0.2100 |   0.8272 | -0.3923 |   0.5355 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma100_gt_sma250|roc20_gt_0|roc60_gt_0            |
| swap1          | -px_gt_ema250+sma100_gt_sma250 |    0.9738 |   7 |   5 |    0.8819 | 0.2292 |   0.8444 | -0.5965 |   0.3842 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|sma100_gt_sma250|roc20_gt_0|roc60_gt_0             |
| swap1          | -px_gt_ema100+sma20_gt_sma100  |    0.9736 |   7 |   5 |    0.8844 | 0.2288 |   0.8500 | -0.6055 |   0.3779 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|sma20_gt_sma100|roc20_gt_0|roc60_gt_0              |
| add1           | +sma50_gt_sma150               |    0.9721 |   8 |   6 |    0.8606 | 0.2178 |   0.8285 | -0.4688 |   0.4647 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma50_gt_sma150|roc20_gt_0|roc60_gt_0 |
| swap1          | -px_gt_sma10+sma50_gt_sma200   |    0.9710 |   7 |   6 |    0.8277 | 0.2101 |   0.8290 | -0.3923 |   0.5357 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma50_gt_sma200|roc20_gt_0|roc60_gt_0             |
| add1           | +px_gt_sma100                  |    0.9700 |   8 |   6 |    0.8797 | 0.2273 |   0.8448 | -0.5619 |   0.4046 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0    |

## Best By Neighborhood

| neighborhood   | change                    |   fitness |   n |   k |   sortino |   cagr |     mdd | signals                                                                                          |
|:---------------|:--------------------------|----------:|----:|----:|----------:|-------:|--------:|:-------------------------------------------------------------------------------------------------|
| add1           | +roc120_gt_0              |    1.0870 |   8 |   6 |    0.9257 | 0.2399 | -0.3969 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0 |
| swap1          | -px_gt_ema100+roc120_gt_0 |    1.0849 |   7 |   5 |    0.9323 | 0.2431 | -0.4489 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0              |
| drop1          | -px_gt_sma10              |    1.0335 |   6 |   5 |    0.8696 | 0.2207 | -0.3923 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                         |
| base           | none                      |    1.0312 |   7 |   5 |    0.9273 | 0.2434 | -0.5965 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0             |

## Method Notes

- Neighborhood = base, one-signal drops, one-signal additions, and one-for-one swaps.
- All valid `k=1..n` thresholds are evaluated for every neighbor.
- Signals are lagged one trading day before earning returns to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.
- This is candidate discovery only; final claims require PBO/DSR/WF/OOS/FWD/bootstrap gates `[advances_fin_ml, p.208-211]`.
