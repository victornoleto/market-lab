# Stage 1 Local Search Results

Status: exact one-edit neighborhood diagnostic. This is not a deploy verdict.

Branch: `SPY`
Risk-on: `UPRO_3x`
Off leg: `ZROZSIM`
Base k: `5`
Base signals: `px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0`
Neighbor subsets: 216
Configs tested: 1,531
Elapsed seconds: 1.3

## Base Incumbent

|   fitness |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                              |
|----------:|----:|----:|----------:|-------:|---------:|--------:|---------:|:-------------------------------------------------------------------------------------|
|    0.8649 |   7 |   5 |    0.8498 | 0.1707 |   0.6276 | -0.7185 |   0.2376 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0 |

## Top Local Candidates

| neighborhood   | change                        |   fitness |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                                              |
|:---------------|:------------------------------|----------:|----:|----:|----------:|-------:|---------:|--------:|---------:|:-----------------------------------------------------------------------------------------------------|
| swap1          | -roc20_gt_0+rv21_pct_lt_70    |    1.0694 |   7 |   5 |    1.0094 | 0.2195 |   0.7408 | -0.6893 |   0.3185 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0|rv21_pct_lt_70             |
| swap1          | -px_gt_sma20+rv21_pct_lt_70   |    1.0458 |   7 |   5 |    0.9878 | 0.2149 |   0.7270 | -0.6825 |   0.3148 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rv21_pct_lt_70              |
| swap1          | -px_gt_sma10+rv21_pct_lt_70   |    1.0276 |   7 |   4 |    0.9662 | 0.2166 |   0.7112 | -0.6743 |   0.3213 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rv21_pct_lt_70              |
| swap1          | -px_gt_ema100+rv21_pct_lt_70  |    1.0221 |   7 |   4 |    0.9597 | 0.2111 |   0.7045 | -0.6526 |   0.3235 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rv21_pct_lt_70               |
| add1           | +rv21_pct_lt_70               |    1.0202 |   8 |   5 |    0.9733 | 0.2134 |   0.7151 | -0.6823 |   0.3127 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rv21_pct_lt_70  |
| swap1          | -px_gt_ema200+rv21_pct_lt_70  |    1.0142 |   7 |   4 |    0.9509 | 0.2086 |   0.6995 | -0.6409 |   0.3255 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0|rv21_pct_lt_70               |
| swap1          | -roc20_gt_0+px_gt_ema20       |    1.0110 |   7 |   4 |    0.9540 | 0.2151 |   0.7065 | -0.6876 |   0.3129 | px_gt_sma10|px_gt_sma20|px_gt_ema20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0                |
| swap1          | -px_gt_ema200+sma50_gt_sma150 |    1.0085 |   7 |   4 |    0.9570 | 0.2155 |   0.7082 | -0.7121 |   0.3027 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|sma50_gt_sma150|roc20_gt_0|roc60_gt_0              |
| swap1          | -roc20_gt_0+px_gt_ema50       |    1.0072 |   7 |   5 |    0.9651 | 0.2103 |   0.7156 | -0.7353 |   0.2860 | px_gt_sma10|px_gt_sma20|px_gt_ema50|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0                |
| swap1          | -roc20_gt_0+rv21_pct_lt_50    |    1.0063 |   7 |   5 |    0.9569 | 0.1995 |   0.7032 | -0.6678 |   0.2988 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0|rv21_pct_lt_50             |
| swap1          | -roc20_gt_0+px_gt_sma250      |    1.0062 |   7 |   5 |    0.9527 | 0.2106 |   0.7054 | -0.6874 |   0.3064 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc60_gt_0               |
| swap1          | -roc20_gt_0+sma100_gt_sma250  |    1.0030 |   7 |   5 |    0.9443 | 0.2072 |   0.6994 | -0.6543 |   0.3166 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma100_gt_sma250|roc60_gt_0           |
| swap1          | -px_gt_sma20+px_gt_ema50      |    1.0019 |   7 |   5 |    0.9520 | 0.2047 |   0.7031 | -0.6827 |   0.2999 | px_gt_sma10|px_gt_ema50|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -roc20_gt_0+rv21_lt_40        |    1.0018 |   7 |   5 |    0.9521 | 0.2129 |   0.7067 | -0.7111 |   0.2995 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0|rv21_lt_40                 |
| swap1          | -roc20_gt_0+px_gt_sma150      |    1.0018 |   7 |   5 |    0.9499 | 0.2092 |   0.7025 | -0.6894 |   0.3035 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma150|px_gt_ema200|px_gt_ema250|roc60_gt_0               |
| swap1          | -roc20_gt_0+px_gt_sma200      |    1.0009 |   7 |   5 |    0.9494 | 0.2096 |   0.7040 | -0.6922 |   0.3028 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma200|px_gt_ema200|px_gt_ema250|roc60_gt_0               |
| swap1          | -roc60_gt_0+rv21_pct_lt_70    |    0.9978 |   7 |   4 |    0.9439 | 0.2056 |   0.6914 | -0.6691 |   0.3073 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|rv21_pct_lt_70             |
| swap1          | -px_gt_sma10+sma100_gt_sma250 |    0.9959 |   7 |   5 |    0.9441 | 0.2060 |   0.6967 | -0.6793 |   0.3032 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma100_gt_sma250|roc20_gt_0|roc60_gt_0            |
| drop1          | -roc20_gt_0                   |    0.9914 |   6 |   4 |    0.9355 | 0.2081 |   0.6954 | -0.7111 |   0.2926 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0                            |
| swap1          | -roc20_gt_0+sma50_gt_sma150   |    0.9912 |   7 |   5 |    0.9413 | 0.2059 |   0.6971 | -0.6872 |   0.2997 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma50_gt_sma150|roc60_gt_0            |
| add1           | +px_gt_sma150                 |    0.9861 |   8 |   5 |    0.9400 | 0.2073 |   0.6931 | -0.6653 |   0.3115 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0    |
| swap1          | -px_gt_ema250+rv21_pct_lt_70  |    0.9847 |   7 |   4 |    0.9329 | 0.2028 |   0.6864 | -0.6687 |   0.3032 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0|rv21_pct_lt_70               |
| swap1          | -roc20_gt_0+px_gt_sma100      |    0.9833 |   7 |   5 |    0.9438 | 0.2086 |   0.7006 | -0.7407 |   0.2816 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0               |
| swap1          | -roc20_gt_0+ar1_30_gt_0       |    0.9803 |   7 |   4 |    0.9410 | 0.2172 |   0.7083 | -0.7707 |   0.2818 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0|ar1_30_gt_0                |
| swap1          | -px_gt_ema200+roc120_gt_0     |    0.9794 |   7 |   4 |    0.9351 | 0.2086 |   0.6938 | -0.7198 |   0.2898 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0                  |
| swap1          | -px_gt_sma20+sma100_gt_sma250 |    0.9793 |   7 |   5 |    0.9348 | 0.2035 |   0.6906 | -0.7016 |   0.2900 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma100_gt_sma250|roc20_gt_0|roc60_gt_0            |
| add1           | +sma50_gt_sma150              |    0.9764 |   8 |   5 |    0.9352 | 0.2062 |   0.6914 | -0.6821 |   0.3023 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma50_gt_sma150|roc20_gt_0|roc60_gt_0 |
| swap1          | -px_gt_ema200+px_gt_sma150    |    0.9753 |   7 |   4 |    0.9330 | 0.2074 |   0.6905 | -0.7246 |   0.2863 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma150|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma10+rsi14_gt_50      |    0.9738 |   7 |   4 |    0.9330 | 0.2060 |   0.6872 | -0.7264 |   0.2836 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50                 |
| swap1          | -px_gt_sma20+px_gt_sma200     |    0.9727 |   7 |   5 |    0.9322 | 0.2030 |   0.6895 | -0.7175 |   0.2830 | px_gt_sma10|px_gt_ema100|px_gt_sma200|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                |
| swap1          | -roc20_gt_0+stochrsi14_gt_50  |    0.9726 |   7 |   4 |    0.9284 | 0.2086 |   0.6904 | -0.7206 |   0.2895 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0|stochrsi14_gt_50           |
| swap1          | -px_gt_ema250+sma50_gt_sma150 |    0.9715 |   7 |   4 |    0.9275 | 0.2059 |   0.6865 | -0.7121 |   0.2891 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|sma50_gt_sma150|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_ema200+px_gt_sma100    |    0.9715 |   7 |   4 |    0.9345 | 0.2072 |   0.6906 | -0.7474 |   0.2773 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| add1           | +sma50_gt_sma200              |    0.9710 |   8 |   5 |    0.9313 | 0.2053 |   0.6890 | -0.6856 |   0.2994 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma50_gt_sma200|roc20_gt_0|roc60_gt_0 |
| swap1          | -px_gt_sma10+px_gt_sma200     |    0.9706 |   7 |   5 |    0.9294 | 0.2016 |   0.6867 | -0.7098 |   0.2840 | px_gt_sma20|px_gt_ema100|px_gt_sma200|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                |
| swap1          | -px_gt_sma10+px_gt_ema50      |    0.9676 |   7 |   4 |    0.9163 | 0.2025 |   0.6787 | -0.6695 |   0.3025 | px_gt_sma20|px_gt_ema50|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma10+stochrsi14_gt_50 |    0.9674 |   7 |   4 |    0.9254 | 0.2049 |   0.6838 | -0.7171 |   0.2858 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|stochrsi14_gt_50            |
| add1           | +px_gt_sma200                 |    0.9668 |   8 |   5 |    0.9259 | 0.2033 |   0.6845 | -0.6736 |   0.3017 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma200|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0    |
| swap1          | -roc60_gt_0+px_gt_sma150      |    0.9652 |   7 |   4 |    0.9186 | 0.2074 |   0.6866 | -0.7057 |   0.2939 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma150|px_gt_ema200|px_gt_ema250|roc20_gt_0               |
| swap1          | -px_gt_sma10+sma50_gt_sma150  |    0.9640 |   7 |   5 |    0.9250 | 0.1999 |   0.6830 | -0.7135 |   0.2802 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma50_gt_sma150|roc20_gt_0|roc60_gt_0             |
| swap1          | -px_gt_ema200+px_gt_sma200    |    0.9639 |   7 |   4 |    0.9226 | 0.2042 |   0.6833 | -0.7183 |   0.2843 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma10+px_gt_sma250     |    0.9636 |   7 |   5 |    0.9248 | 0.2002 |   0.6825 | -0.7155 |   0.2798 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0                |
| swap1          | -px_gt_sma10+px_gt_sma150     |    0.9625 |   7 |   5 |    0.9223 | 0.1992 |   0.6795 | -0.7058 |   0.2823 | px_gt_sma20|px_gt_ema100|px_gt_sma150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                |
| swap1          | -px_gt_sma20+sma50_gt_sma150  |    0.9623 |   7 |   5 |    0.9257 | 0.2007 |   0.6849 | -0.7266 |   0.2762 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma50_gt_sma150|roc20_gt_0|roc60_gt_0             |
| swap1          | -px_gt_sma10+sma50_gt_sma200  |    0.9613 |   7 |   5 |    0.9210 | 0.1991 |   0.6807 | -0.7049 |   0.2825 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma50_gt_sma200|roc20_gt_0|roc60_gt_0             |
| swap1          | -px_gt_sma20+stochrsi14_gt_50 |    0.9612 |   7 |   4 |    0.9155 | 0.2034 |   0.6799 | -0.6959 |   0.2923 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|stochrsi14_gt_50            |
| swap1          | -px_gt_sma20+ar1_30_gt_0      |    0.9612 |   7 |   5 |    0.9291 | 0.1971 |   0.6890 | -0.7345 |   0.2683 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|ar1_30_gt_0                 |
| swap1          | -px_gt_sma20+macd_gt_signal   |    0.9611 |   7 |   4 |    0.9103 | 0.2010 |   0.6752 | -0.6666 |   0.3016 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|macd_gt_signal|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_sma20+macd_hist_gt_0   |    0.9611 |   7 |   4 |    0.9103 | 0.2010 |   0.6752 | -0.6666 |   0.3016 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|macd_hist_gt_0|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_sma10+rv21_pct_lt_70   |    0.9603 |   7 |   5 |    0.9228 | 0.1939 |   0.6783 | -0.6992 |   0.2773 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rv21_pct_lt_70              |

## Best By Neighborhood

| neighborhood   | change                     |   fitness |   n |   k |   sortino |   cagr |     mdd | signals                                                                                             |
|:---------------|:---------------------------|----------:|----:|----:|----------:|-------:|--------:|:----------------------------------------------------------------------------------------------------|
| swap1          | -roc20_gt_0+rv21_pct_lt_70 |    1.0694 |   7 |   5 |    1.0094 | 0.2195 | -0.6893 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0|rv21_pct_lt_70            |
| add1           | +rv21_pct_lt_70            |    1.0202 |   8 |   5 |    0.9733 | 0.2134 | -0.6823 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rv21_pct_lt_70 |
| drop1          | -roc20_gt_0                |    0.9914 |   6 |   4 |    0.9355 | 0.2081 | -0.7111 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0                           |
| base           | none                       |    0.9164 |   7 |   4 |    0.8840 | 0.1914 | -0.7134 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                |

## Method Notes

- Neighborhood = base, one-signal drops, one-signal additions, and one-for-one swaps.
- All valid `k=1..n` thresholds are evaluated for every neighbor.
- Signals are lagged one trading day before earning returns to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.
- This is candidate discovery only; final claims require PBO/DSR/WF/OOS/FWD/bootstrap gates `[advances_fin_ml, p.208-211]`.
