# Stage 1 GA Results

Status: genetic-search output. This is not a deploy verdict.

Branch: `QQQ`
Risk-on: `QLD_2x`
Off leg: `ZROZSIM`
Signals available: 33
n range: 2..8
Population/generations: 24/5
Evaluations: 120
Elapsed seconds: 0.1

## Top Final Candidates

|   fitness | branch   | risk_on   |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                                   |
|----------:|:---------|:----------|----:|----:|----------:|-------:|---------:|--------:|---------:|:------------------------------------------------------------------------------------------|
|    1.3176 | QQQ      | QLD_2x    |   6 |   5 |    1.1898 | 0.2634 |   0.8627 | -0.6059 |   0.4348 | px_gt_sma150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|ar1_30_gt_0                  |
|    1.3058 | QQQ      | QLD_2x    |   4 |   4 |    1.1878 | 0.2495 |   0.8540 | -0.5999 |   0.4160 | px_gt_sma150|px_gt_ema200|sma20_gt_sma100|roc20_gt_0                                      |
|    1.2622 | QQQ      | QLD_2x    |   6 |   5 |    1.1518 | 0.2348 |   0.8278 | -0.5833 |   0.4025 | px_gt_sma10|px_gt_ema50|px_gt_ema150|px_gt_ema200|roc20_gt_0|ar1_30_gt_0                  |
|    1.2510 | QQQ      | QLD_2x    |   6 |   5 |    1.1369 | 0.2495 |   0.8293 | -0.6130 |   0.4070 | px_gt_ema100|px_gt_sma150|px_gt_ema200|sma20_gt_sma100|roc20_gt_0|ar1_30_gt_0             |
|    1.2371 | QQQ      | QLD_2x    |   6 |   5 |    1.1353 | 0.2464 |   0.8270 | -0.6489 |   0.3797 | px_gt_sma50|px_gt_sma150|px_gt_sma200|px_gt_ema200|roc20_gt_0|ar1_30_gt_0                 |
|    1.2123 | QQQ      | QLD_2x    |   4 |   4 |    1.1333 | 0.1905 |   0.7657 | -0.5607 |   0.3397 | px_gt_ema150|px_gt_ema200|roc20_gt_0|ar1_30_gt_0                                          |
|    1.2082 | QQQ      | QLD_2x    |   4 |   3 |    1.1106 | 0.2511 |   0.8165 | -0.6792 |   0.3697 | px_gt_ema100|px_gt_ema150|roc20_gt_0|ar1_30_gt_0                                          |
|    1.2017 | QQQ      | QLD_2x    |   5 |   3 |    1.1010 | 0.2635 |   0.8125 | -0.7052 |   0.3737 | px_gt_ema100|px_gt_ema150|px_gt_ema250|roc20_gt_0|ar1_30_gt_0                             |
|    1.1976 | QQQ      | QLD_2x    |   5 |   5 |    1.1203 | 0.1865 |   0.7570 | -0.5547 |   0.3361 | px_gt_sma50|px_gt_sma150|px_gt_ema200|roc20_gt_0|ar1_30_gt_0                              |
|    1.1595 | QQQ      | QLD_2x    |   6 |   5 |    1.0690 | 0.2151 |   0.7728 | -0.5950 |   0.3615 | px_gt_ema10|px_gt_ema100|px_gt_sma150|px_gt_ema200|roc20_gt_0|ar1_30_gt_0                 |
|    1.1527 | QQQ      | QLD_2x    |   5 |   5 |    1.0802 | 0.1763 |   0.7303 | -0.5397 |   0.3267 | px_gt_sma150|px_gt_ema200|sma20_gt_sma100|roc20_gt_0|ar1_30_gt_0                          |
|    1.1519 | QQQ      | QLD_2x    |   4 |   4 |    1.0812 | 0.1808 |   0.7362 | -0.5608 |   0.3223 | px_gt_ema100|px_gt_sma200|roc20_gt_0|ar1_30_gt_0                                          |
|    1.1481 | QQQ      | QLD_2x    |   7 |   5 |    1.0706 | 0.2365 |   0.7822 | -0.6735 |   0.3512 | px_gt_ema10|px_gt_ema100|px_gt_ema150|px_gt_ema200|sma20_gt_sma100|roc20_gt_0|ar1_30_gt_0 |
|    1.1408 | QQQ      | QLD_2x    |   3 |   3 |    1.0609 | 0.1814 |   0.7312 | -0.5292 |   0.3428 | px_gt_ema100|roc20_gt_0|ar1_30_gt_0                                                       |
|    1.1280 | QQQ      | QLD_2x    |   4 |   4 |    1.0613 | 0.1764 |   0.7218 | -0.5619 |   0.3140 | px_gt_ema100|px_gt_ema150|roc20_gt_0|ar1_30_gt_0                                          |
|    1.1201 | QQQ      | QLD_2x    |   7 |   5 |    1.0643 | 0.2285 |   0.7799 | -0.7365 |   0.3102 | px_gt_sma50|px_gt_sma150|px_gt_ema200|macd_gt_signal|roc20_gt_0|rv21_lt_40|ar1_30_gt_0    |
|    1.1172 | QQQ      | QLD_2x    |   4 |   3 |    1.0392 | 0.2089 |   0.7556 | -0.6234 |   0.3351 | px_gt_sma100|roc20_gt_0|rv21_pct_lt_70|ar1_30_gt_0                                        |
|    1.1143 | QQQ      | QLD_2x    |   7 |   4 |    1.0546 | 0.2476 |   0.7789 | -0.7822 |   0.3165 | px_gt_ema100|px_gt_sma150|px_gt_ema150|px_gt_ema200|macd_hist_gt_0|roc20_gt_0|ar1_30_gt_0 |
|    1.1143 | QQQ      | QLD_2x    |   5 |   5 |    1.0509 | 0.1616 |   0.7019 | -0.5260 |   0.3073 | px_gt_ema10|px_gt_ema100|px_gt_sma150|stochrsi14_gt_50|ar1_30_gt_0                        |
|    1.1136 | QQQ      | QLD_2x    |   4 |   3 |    1.0567 | 0.2277 |   0.7857 | -0.7723 |   0.2948 | px_gt_sma10|px_gt_ema100|roc20_gt_0|ar1_30_gt_0                                           |

## Method Notes

- GA chromosome = signal inclusion mask + `k` vote threshold.
- Fitness = Sortino + weighted CAGR/Calmar - MDD/complexity penalties.
- Signals are lagged one day in the shared simulator to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.
- Final candidates still require PBO/DSR/WF/OOS/FWD/bootstrap validation `[advances_fin_ml, p.208-211]`.
