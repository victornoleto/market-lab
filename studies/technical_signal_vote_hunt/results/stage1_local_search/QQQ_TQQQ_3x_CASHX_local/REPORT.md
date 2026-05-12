# Stage 1 Local Search Results

Status: exact one-edit neighborhood diagnostic. This is not a deploy verdict.

Branch: `QQQ`
Risk-on: `TQQQ_3x`
Off leg: `CASHX`
Base k: `5`
Base signals: `px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0`
Neighbor subsets: 216
Configs tested: 1,531
Elapsed seconds: 1.3

## Base Incumbent

|   fitness |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                              |
|----------:|----:|----:|----------:|-------:|---------:|--------:|---------:|:-------------------------------------------------------------------------------------|
|    0.9914 |   7 |   5 |    0.8799 | 0.3139 |   0.8355 | -0.7758 |   0.4046 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0 |

## Top Local Candidates

| neighborhood   | change                         |   fitness |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                                              |
|:---------------|:-------------------------------|----------:|----:|----:|----------:|-------:|---------:|--------:|---------:|:-----------------------------------------------------------------------------------------------------|
| swap1          | -px_gt_ema100+roc120_gt_0      |    1.0368 |   7 |   5 |    0.8846 | 0.3141 |   0.8384 | -0.6302 |   0.4985 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0                  |
| add1           | +roc120_gt_0                   |    1.0364 |   8 |   6 |    0.8777 | 0.3106 |   0.8394 | -0.5701 |   0.5448 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0     |
| base           | none                           |    0.9914 |   7 |   5 |    0.8799 | 0.3139 |   0.8355 | -0.7758 |   0.4046 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| drop1          | -px_gt_sma10                   |    0.9864 |   6 |   5 |    0.8214 | 0.2833 |   0.8035 | -0.5418 |   0.5229 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                             |
| swap1          | -px_gt_sma10+rsi14_gt_50       |    0.9824 |   7 |   5 |    0.8614 | 0.3015 |   0.8156 | -0.7036 |   0.4285 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50                 |
| swap1          | -px_gt_sma10+px_gt_ema10       |    0.9804 |   7 |   5 |    0.8788 | 0.3138 |   0.8359 | -0.8151 |   0.3850 | px_gt_ema10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema100+px_gt_sma250     |    0.9789 |   7 |   5 |    0.8588 | 0.3028 |   0.8175 | -0.7103 |   0.4262 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma20+rsi14_gt_50       |    0.9769 |   7 |   5 |    0.8689 | 0.3068 |   0.8214 | -0.7682 |   0.3993 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50                 |
| swap1          | -px_gt_ema200+roc120_gt_0      |    0.9761 |   7 |   5 |    0.8618 | 0.3028 |   0.8178 | -0.7320 |   0.4136 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0                  |
| swap1          | -px_gt_ema100+px_gt_sma100     |    0.9754 |   7 |   5 |    0.8621 | 0.3045 |   0.8217 | -0.7410 |   0.4109 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema250+roc120_gt_0      |    0.9752 |   7 |   5 |    0.8616 | 0.3019 |   0.8161 | -0.7320 |   0.4124 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0|roc120_gt_0                  |
| swap1          | -px_gt_sma10+px_gt_ema20       |    0.9739 |   7 |   5 |    0.8666 | 0.3055 |   0.8219 | -0.7671 |   0.3982 | px_gt_sma20|px_gt_ema20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma10+px_gt_ema150      |    0.9701 |   7 |   6 |    0.8171 | 0.2811 |   0.7994 | -0.5418 |   0.5188 | px_gt_sma20|px_gt_ema100|px_gt_ema150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                |
| swap1          | -px_gt_sma20+stochrsi14_gt_50  |    0.9659 |   7 |   5 |    0.8569 | 0.3008 |   0.8116 | -0.7466 |   0.4029 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|stochrsi14_gt_50            |
| add1           | +px_gt_sma50                   |    0.9651 |   8 |   6 |    0.8348 | 0.2884 |   0.8033 | -0.5999 |   0.4807 | px_gt_sma10|px_gt_sma20|px_gt_sma50|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0     |
| swap1          | -px_gt_ema200+px_gt_sma250     |    0.9626 |   7 |   5 |    0.8610 | 0.3047 |   0.8202 | -0.7876 |   0.3868 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -roc60_gt_0+roc120_gt_0        |    0.9618 |   7 |   5 |    0.8324 | 0.2839 |   0.7834 | -0.6240 |   0.4550 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc120_gt_0                |
| swap1          | -px_gt_sma20+px_gt_ema20       |    0.9613 |   7 |   5 |    0.8560 | 0.3022 |   0.8146 | -0.7655 |   0.3948 | px_gt_sma10|px_gt_ema20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma20+macd_gt_signal    |    0.9607 |   7 |   5 |    0.8526 | 0.2977 |   0.8091 | -0.7411 |   0.4018 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|macd_gt_signal|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_sma20+macd_hist_gt_0    |    0.9607 |   7 |   5 |    0.8526 | 0.2977 |   0.8091 | -0.7411 |   0.4018 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|macd_hist_gt_0|roc20_gt_0|roc60_gt_0              |
| add1           | +px_gt_sma250                  |    0.9591 |   8 |   6 |    0.8460 | 0.2967 |   0.8143 | -0.6821 |   0.4350 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0    |
| swap1          | -roc60_gt_0+px_gt_sma100       |    0.9584 |   7 |   5 |    0.8572 | 0.2998 |   0.8092 | -0.7743 |   0.3872 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0               |
| swap1          | -px_gt_sma10+px_gt_sma250      |    0.9581 |   7 |   6 |    0.8078 | 0.2779 |   0.7954 | -0.5418 |   0.5130 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0                |
| swap1          | -px_gt_ema250+px_gt_sma250     |    0.9573 |   7 |   5 |    0.8573 | 0.3027 |   0.8167 | -0.7876 |   0.3843 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_sma250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema100+sma50_gt_sma200  |    0.9540 |   7 |   5 |    0.8402 | 0.2938 |   0.8030 | -0.7078 |   0.4151 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|sma50_gt_sma200|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_sma10+px_gt_sma100      |    0.9524 |   7 |   6 |    0.8066 | 0.2785 |   0.8020 | -0.5568 |   0.5003 | px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                |
| drop1          | -px_gt_ema100                  |    0.9503 |   6 |   4 |    0.8598 | 0.3025 |   0.8044 | -0.8689 |   0.3481 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                              |
| swap1          | -px_gt_ema200+px_gt_sma200     |    0.9490 |   7 |   5 |    0.8513 | 0.2975 |   0.8079 | -0.7813 |   0.3808 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema100+px_gt_sma150     |    0.9472 |   7 |   5 |    0.8551 | 0.2991 |   0.8125 | -0.8092 |   0.3696 | px_gt_sma10|px_gt_sma20|px_gt_sma150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema100+sma50_gt_sma150  |    0.9471 |   7 |   5 |    0.8263 | 0.2832 |   0.7879 | -0.6516 |   0.4347 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|sma50_gt_sma150|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_ema200+sma50_gt_sma200  |    0.9451 |   7 |   5 |    0.8460 | 0.2975 |   0.8084 | -0.7758 |   0.3834 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|sma50_gt_sma200|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_sma10+sma20_gt_sma100   |    0.9430 |   7 |   6 |    0.8098 | 0.2845 |   0.8214 | -0.6126 |   0.4644 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma20_gt_sma100|roc20_gt_0|roc60_gt_0             |
| swap1          | -px_gt_ema200+px_gt_sma100     |    0.9405 |   7 |   5 |    0.8340 | 0.2900 |   0.7943 | -0.7237 |   0.4007 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema100+px_gt_sma200     |    0.9385 |   7 |   5 |    0.8438 | 0.2918 |   0.7995 | -0.7758 |   0.3761 | px_gt_sma10|px_gt_sma20|px_gt_sma200|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema250+px_gt_sma200     |    0.9380 |   7 |   5 |    0.8439 | 0.2927 |   0.7993 | -0.7813 |   0.3746 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma200|px_gt_ema200|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma10+roc120_gt_0       |    0.9365 |   7 |   6 |    0.8001 | 0.2772 |   0.7961 | -0.5824 |   0.4759 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0                 |
| swap1          | -px_gt_ema250+sma50_gt_sma200  |    0.9358 |   7 |   5 |    0.8398 | 0.2935 |   0.8014 | -0.7758 |   0.3783 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|sma50_gt_sma200|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_sma10+px_gt_sma200      |    0.9348 |   7 |   6 |    0.7911 | 0.2704 |   0.7817 | -0.5418 |   0.4990 | px_gt_sma20|px_gt_ema100|px_gt_sma200|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                |
| add1           | +sma50_gt_sma200               |    0.9313 |   8 |   6 |    0.8254 | 0.2867 |   0.7975 | -0.6793 |   0.4221 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma50_gt_sma200|roc20_gt_0|roc60_gt_0 |
| swap1          | -px_gt_ema100+sma20_gt_sma100  |    0.9311 |   7 |   5 |    0.8370 | 0.2924 |   0.8046 | -0.7803 |   0.3747 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|sma20_gt_sma100|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_ema250+sma100_gt_sma250 |    0.9296 |   7 |   5 |    0.8348 | 0.2919 |   0.7994 | -0.7758 |   0.3762 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|sma100_gt_sma250|roc20_gt_0|roc60_gt_0             |
| swap1          | -px_gt_sma10+stochrsi14_gt_50  |    0.9295 |   7 |   5 |    0.8356 | 0.2886 |   0.7928 | -0.7695 |   0.3750 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|stochrsi14_gt_50            |
| swap1          | -px_gt_ema100+px_gt_ema150     |    0.9276 |   7 |   5 |    0.8441 | 0.2937 |   0.8019 | -0.8285 |   0.3545 | px_gt_sma10|px_gt_sma20|px_gt_ema150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema200+px_gt_sma150     |    0.9268 |   7 |   5 |    0.8424 | 0.2920 |   0.7988 | -0.8193 |   0.3564 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma150|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma10+px_gt_sma150      |    0.9254 |   7 |   6 |    0.8006 | 0.2759 |   0.7924 | -0.6170 |   0.4471 | px_gt_sma20|px_gt_ema100|px_gt_sma150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                |
| swap1          | -px_gt_sma10+sma100_gt_sma250  |    0.9253 |   7 |   6 |    0.7838 | 0.2679 |   0.7800 | -0.5418 |   0.4944 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma100_gt_sma250|roc20_gt_0|roc60_gt_0            |
| swap1          | -px_gt_ema250+px_gt_sma100     |    0.9249 |   7 |   5 |    0.8233 | 0.2835 |   0.7828 | -0.7237 |   0.3918 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0                 |
| add1           | +rv21_pct_lt_70                |    0.9246 |   8 |   5 |    0.8470 | 0.2795 |   0.7573 | -0.7666 |   0.3645 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rv21_pct_lt_70  |
| add1           | +px_gt_sma100                  |    0.9238 |   8 |   6 |    0.8324 | 0.2899 |   0.7995 | -0.7433 |   0.3900 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0    |
| swap1          | -px_gt_sma10+macd_gt_signal    |    0.9235 |   7 |   5 |    0.8364 | 0.2882 |   0.7974 | -0.7960 |   0.3621 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|macd_gt_signal|roc20_gt_0|roc60_gt_0              |

## Best By Neighborhood

| neighborhood   | change                    |   fitness |   n |   k |   sortino |   cagr |     mdd | signals                                                                                          |
|:---------------|:--------------------------|----------:|----:|----:|----------:|-------:|--------:|:-------------------------------------------------------------------------------------------------|
| swap1          | -px_gt_ema100+roc120_gt_0 |    1.0368 |   7 |   5 |    0.8846 | 0.3141 | -0.6302 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0              |
| add1           | +roc120_gt_0              |    1.0364 |   8 |   6 |    0.8777 | 0.3106 | -0.5701 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0 |
| base           | none                      |    0.9914 |   7 |   5 |    0.8799 | 0.3139 | -0.7758 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0             |
| drop1          | -px_gt_sma10              |    0.9864 |   6 |   5 |    0.8214 | 0.2833 | -0.5418 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                         |

## Method Notes

- Neighborhood = base, one-signal drops, one-signal additions, and one-for-one swaps.
- All valid `k=1..n` thresholds are evaluated for every neighbor.
- Signals are lagged one trading day before earning returns to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.
- This is candidate discovery only; final claims require PBO/DSR/WF/OOS/FWD/bootstrap gates `[advances_fin_ml, p.208-211]`.
