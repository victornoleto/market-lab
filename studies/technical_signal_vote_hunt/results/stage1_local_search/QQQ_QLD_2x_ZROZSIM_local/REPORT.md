# Stage 1 Local Search Results

Status: exact one-edit neighborhood diagnostic. This is not a deploy verdict.

Branch: `QQQ`
Risk-on: `QLD_2x`
Off leg: `ZROZSIM`
Base k: `5`
Base signals: `px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0`
Neighbor subsets: 216
Configs tested: 1,531
Elapsed seconds: 1.5

## Base Incumbent

|   fitness |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                              |
|----------:|----:|----:|----------:|-------:|---------:|--------:|---------:|:-------------------------------------------------------------------------------------|
|    1.5632 |   7 |   5 |    1.3776 | 0.3279 |   0.9954 | -0.5638 |   0.5815 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0 |

## Top Local Candidates

| neighborhood   | change                         |   fitness |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                                              |
|:---------------|:-------------------------------|----------:|----:|----:|----------:|-------:|---------:|--------:|---------:|:-----------------------------------------------------------------------------------------------------|
| base           | none                           |    1.5632 |   7 |   5 |    1.3776 | 0.3279 |   0.9954 | -0.5638 |   0.5815 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema200+px_gt_sma250     |    1.5469 |   7 |   5 |    1.3542 | 0.3204 |   0.9790 | -0.5269 |   0.6080 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema250+px_gt_sma250     |    1.5435 |   7 |   5 |    1.3514 | 0.3196 |   0.9773 | -0.5269 |   0.6065 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_sma250|roc20_gt_0|roc60_gt_0                 |
| add1           | +roc120_gt_0                   |    1.5430 |   8 |   6 |    1.3815 | 0.3217 |   0.9902 | -0.5896 |   0.5456 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0     |
| swap1          | -px_gt_ema100+px_gt_sma100     |    1.5356 |   7 |   5 |    1.3527 | 0.3182 |   0.9768 | -0.5482 |   0.5803 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma10+px_gt_ema10       |    1.5297 |   7 |   5 |    1.3634 | 0.3237 |   0.9868 | -0.6107 |   0.5301 | px_gt_ema10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema100+roc120_gt_0      |    1.5278 |   7 |   5 |    1.3744 | 0.3232 |   0.9864 | -0.6504 |   0.4969 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0                  |
| swap1          | -px_gt_ema100+px_gt_sma150     |    1.5223 |   7 |   5 |    1.3541 | 0.3181 |   0.9763 | -0.5904 |   0.5387 | px_gt_sma10|px_gt_sma20|px_gt_sma150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma20+macd_gt_signal    |    1.5200 |   7 |   5 |    1.3441 | 0.3165 |   0.9714 | -0.5638 |   0.5613 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|macd_gt_signal|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_sma20+macd_hist_gt_0    |    1.5200 |   7 |   5 |    1.3441 | 0.3165 |   0.9714 | -0.5638 |   0.5613 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|macd_hist_gt_0|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_ema250+roc120_gt_0      |    1.5189 |   7 |   5 |    1.3370 | 0.3118 |   0.9610 | -0.5358 |   0.5819 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0|roc120_gt_0                  |
| swap1          | -px_gt_ema200+roc120_gt_0      |    1.5185 |   7 |   5 |    1.3365 | 0.3119 |   0.9612 | -0.5358 |   0.5821 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0                  |
| swap1          | -px_gt_sma10+px_gt_ema20       |    1.5183 |   7 |   5 |    1.3470 | 0.3168 |   0.9719 | -0.5781 |   0.5481 | px_gt_sma20|px_gt_ema20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma20+rsi14_gt_50       |    1.5129 |   7 |   5 |    1.3352 | 0.3153 |   0.9653 | -0.5561 |   0.5670 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50                 |
| swap1          | -px_gt_sma20+px_gt_ema20       |    1.5126 |   7 |   5 |    1.3369 | 0.3162 |   0.9689 | -0.5638 |   0.5609 | px_gt_sma10|px_gt_ema20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| add1           | +px_gt_sma250                  |    1.5080 |   8 |   6 |    1.3496 | 0.3148 |   0.9738 | -0.5817 |   0.5412 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0    |
| swap1          | -px_gt_ema200+px_gt_sma200     |    1.5030 |   7 |   5 |    1.3231 | 0.3087 |   0.9537 | -0.5341 |   0.5780 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema100+sma20_gt_sma100  |    1.5001 |   7 |   5 |    1.3400 | 0.3124 |   0.9665 | -0.6006 |   0.5201 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|sma20_gt_sma100|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_ema250+px_gt_sma200     |    1.4983 |   7 |   5 |    1.3195 | 0.3075 |   0.9509 | -0.5341 |   0.5758 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma200|px_gt_ema200|roc20_gt_0|roc60_gt_0                 |
| add1           | +px_gt_sma100                  |    1.4976 |   8 |   6 |    1.3257 | 0.3081 |   0.9572 | -0.5269 |   0.5847 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0    |
| swap1          | -px_gt_ema200+sma50_gt_sma200  |    1.4947 |   7 |   5 |    1.3139 | 0.3067 |   0.9492 | -0.5269 |   0.5821 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|sma50_gt_sma200|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_ema250+sma100_gt_sma250 |    1.4925 |   7 |   5 |    1.3223 | 0.3097 |   0.9565 | -0.5638 |   0.5493 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|sma100_gt_sma250|roc20_gt_0|roc60_gt_0             |
| swap1          | -px_gt_ema100+px_gt_sma250     |    1.4921 |   7 |   5 |    1.3410 | 0.3157 |   0.9681 | -0.6379 |   0.4949 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| add1           | +px_gt_ema150                  |    1.4890 |   8 |   6 |    1.3319 | 0.3112 |   0.9633 | -0.5764 |   0.5400 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0    |
| swap1          | -roc60_gt_0+px_gt_sma100       |    1.4871 |   7 |   5 |    1.3195 | 0.3099 |   0.9546 | -0.5718 |   0.5420 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0               |
| swap1          | -px_gt_ema250+sma50_gt_sma200  |    1.4852 |   7 |   5 |    1.3066 | 0.3043 |   0.9438 | -0.5269 |   0.5775 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|sma50_gt_sma200|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_ema200+sma100_gt_sma250 |    1.4841 |   7 |   5 |    1.3090 | 0.3058 |   0.9475 | -0.5400 |   0.5663 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|sma100_gt_sma250|roc20_gt_0|roc60_gt_0             |
| add1           | +px_gt_sma150                  |    1.4830 |   8 |   6 |    1.3271 | 0.3076 |   0.9562 | -0.5711 |   0.5387 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0    |
| swap1          | -px_gt_sma20+px_gt_ema10       |    1.4805 |   7 |   5 |    1.3089 | 0.3083 |   0.9504 | -0.5561 |   0.5544 | px_gt_sma10|px_gt_ema10|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma10+rsi14_gt_50       |    1.4794 |   7 |   5 |    1.3152 | 0.3054 |   0.9463 | -0.5706 |   0.5352 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50                 |
| swap1          | -px_gt_ema200+px_gt_ema150     |    1.4740 |   7 |   5 |    1.3079 | 0.3064 |   0.9467 | -0.5677 |   0.5398 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema150|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| add1           | +px_gt_sma50                   |    1.4732 |   8 |   6 |    1.3204 | 0.3011 |   0.9472 | -0.5638 |   0.5340 | px_gt_sma10|px_gt_sma20|px_gt_sma50|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0     |
| swap1          | -px_gt_sma10+macd_gt_signal    |    1.4716 |   7 |   5 |    1.3064 | 0.3006 |   0.9408 | -0.5556 |   0.5410 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|macd_gt_signal|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_sma10+macd_hist_gt_0    |    1.4716 |   7 |   5 |    1.3064 | 0.3006 |   0.9408 | -0.5556 |   0.5410 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|macd_hist_gt_0|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_ema200+px_gt_sma150     |    1.4713 |   7 |   5 |    1.3130 | 0.3046 |   0.9450 | -0.5861 |   0.5197 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma150|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| drop1          | -px_gt_ema100                  |    1.4713 |   6 |   4 |    1.3207 | 0.3162 |   0.9574 | -0.6747 |   0.4687 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                              |
| add1           | +px_gt_sma200                  |    1.4705 |   8 |   6 |    1.3211 | 0.3043 |   0.9506 | -0.5817 |   0.5230 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma200|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0    |
| swap1          | -px_gt_ema100+px_gt_ema150     |    1.4693 |   7 |   5 |    1.3187 | 0.3086 |   0.9538 | -0.6206 |   0.4973 | px_gt_sma10|px_gt_sma20|px_gt_ema150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema250+px_gt_ema150     |    1.4693 |   7 |   5 |    1.3043 | 0.3052 |   0.9439 | -0.5677 |   0.5377 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema150|px_gt_ema200|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema250+px_gt_sma150     |    1.4666 |   7 |   5 |    1.3093 | 0.3034 |   0.9422 | -0.5861 |   0.5177 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma150|px_gt_ema200|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema100+px_gt_sma200     |    1.4647 |   7 |   5 |    1.3209 | 0.3067 |   0.9499 | -0.6379 |   0.4808 | px_gt_sma10|px_gt_sma20|px_gt_sma200|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema200+px_gt_sma100     |    1.4585 |   7 |   5 |    1.2946 | 0.3005 |   0.9349 | -0.5590 |   0.5375 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| add1           | +rv21_lt_40                    |    1.4527 |   8 |   6 |    1.3003 | 0.3007 |   0.9484 | -0.5638 |   0.5333 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rv21_lt_40      |
| add1           | +px_gt_ema50                   |    1.4513 |   8 |   6 |    1.2999 | 0.2995 |   0.9392 | -0.5638 |   0.5312 | px_gt_sma10|px_gt_sma20|px_gt_ema50|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0     |
| drop1          | -px_gt_ema250                  |    1.4509 |   6 |   4 |    1.2905 | 0.3059 |   0.9371 | -0.6143 |   0.4980 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0                              |
| swap1          | -px_gt_ema250+px_gt_sma100     |    1.4492 |   7 |   5 |    1.2873 | 0.2982 |   0.9296 | -0.5590 |   0.5333 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0                 |
| drop1          | -px_gt_ema200                  |    1.4478 |   6 |   4 |    1.2877 | 0.3056 |   0.9360 | -0.6143 |   0.4974 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0                              |
| add1           | +sma50_gt_sma200               |    1.4461 |   8 |   6 |    1.3011 | 0.2989 |   0.9385 | -0.5817 |   0.5137 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma50_gt_sma200|roc20_gt_0|roc60_gt_0 |
| swap1          | -px_gt_ema100+sma50_gt_sma200  |    1.4455 |   7 |   5 |    1.3044 | 0.3033 |   0.9415 | -0.6379 |   0.4756 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|sma50_gt_sma200|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_ema200+sma20_gt_sma100  |    1.4449 |   7 |   5 |    1.2825 | 0.2955 |   0.9267 | -0.5508 |   0.5365 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|sma20_gt_sma100|roc20_gt_0|roc60_gt_0              |

## Best By Neighborhood

| neighborhood   | change                     |   fitness |   n |   k |   sortino |   cagr |     mdd | signals                                                                                          |
|:---------------|:---------------------------|----------:|----:|----:|----------:|-------:|--------:|:-------------------------------------------------------------------------------------------------|
| base           | none                       |    1.5632 |   7 |   5 |    1.3776 | 0.3279 | -0.5638 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0             |
| swap1          | -px_gt_ema200+px_gt_sma250 |    1.5469 |   7 |   5 |    1.3542 | 0.3204 | -0.5269 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0             |
| add1           | +roc120_gt_0               |    1.5430 |   8 |   6 |    1.3815 | 0.3217 | -0.5896 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0 |
| drop1          | -px_gt_ema100              |    1.4713 |   6 |   4 |    1.3207 | 0.3162 | -0.6747 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                          |

## Method Notes

- Neighborhood = base, one-signal drops, one-signal additions, and one-for-one swaps.
- All valid `k=1..n` thresholds are evaluated for every neighbor.
- Signals are lagged one trading day before earning returns to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.
- This is candidate discovery only; final claims require PBO/DSR/WF/OOS/FWD/bootstrap gates `[advances_fin_ml, p.208-211]`.
