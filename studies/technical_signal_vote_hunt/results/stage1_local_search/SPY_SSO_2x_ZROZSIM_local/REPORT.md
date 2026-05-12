# Stage 1 Local Search Results

Status: exact one-edit neighborhood diagnostic. This is not a deploy verdict.

Branch: `SPY`
Risk-on: `SSO_2x`
Off leg: `ZROZSIM`
Base k: `5`
Base signals: `px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0`
Neighbor subsets: 216
Configs tested: 1,531
Elapsed seconds: 1.3

## Base Incumbent

|   fitness |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                              |
|----------:|----:|----:|----------:|-------:|---------:|--------:|---------:|:-------------------------------------------------------------------------------------|
|    0.9972 |   7 |   5 |    0.9695 | 0.1588 |   0.6890 | -0.6192 |   0.2564 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0 |

## Top Local Candidates

| neighborhood   | change                         |   fitness |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                                               |
|:---------------|:-------------------------------|----------:|----:|----:|----------:|-------:|---------:|--------:|---------:|:------------------------------------------------------------------------------------------------------|
| swap1          | -roc20_gt_0+rv21_pct_lt_70     |    1.1707 |   7 |   5 |    1.1101 | 0.1904 |   0.7888 | -0.5925 |   0.3213 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0|rv21_pct_lt_70              |
| swap1          | -px_gt_sma10+rv21_pct_lt_70    |    1.1559 |   7 |   4 |    1.0889 | 0.1920 |   0.7759 | -0.5735 |   0.3348 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rv21_pct_lt_70               |
| swap1          | -roc20_gt_0+px_gt_ema50        |    1.1465 |   7 |   5 |    1.0965 | 0.1902 |   0.7839 | -0.6341 |   0.2999 | px_gt_sma10|px_gt_sma20|px_gt_ema50|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0                 |
| swap1          | -px_gt_sma20+px_gt_ema50       |    1.1395 |   7 |   5 |    1.0795 | 0.1851 |   0.7695 | -0.5779 |   0.3203 | px_gt_sma10|px_gt_ema50|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                  |
| swap1          | -px_gt_ema200+rv21_pct_lt_70   |    1.1348 |   7 |   4 |    1.0670 | 0.1853 |   0.7602 | -0.5488 |   0.3376 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0|rv21_pct_lt_70                |
| add1           | +rv21_pct_lt_70                |    1.1342 |   8 |   5 |    1.0834 | 0.1872 |   0.7705 | -0.5814 |   0.3221 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rv21_pct_lt_70   |
| swap1          | -roc20_gt_0+px_gt_ema20        |    1.1310 |   7 |   4 |    1.0697 | 0.1897 |   0.7670 | -0.5875 |   0.3230 | px_gt_sma10|px_gt_sma20|px_gt_ema20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0                 |
| swap1          | -px_gt_ema100+rv21_pct_lt_70   |    1.1301 |   7 |   4 |    1.0682 | 0.1852 |   0.7597 | -0.5706 |   0.3245 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rv21_pct_lt_70                |
| swap1          | -px_gt_sma20+rv21_pct_lt_70    |    1.1295 |   7 |   5 |    1.0751 | 0.1840 |   0.7664 | -0.5956 |   0.3089 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rv21_pct_lt_70               |
| swap1          | -px_gt_ema200+sma50_gt_sma150  |    1.1173 |   7 |   4 |    1.0577 | 0.1867 |   0.7590 | -0.5843 |   0.3196 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|sma50_gt_sma150|roc20_gt_0|roc60_gt_0               |
| swap1          | -roc20_gt_0+rv21_pct_lt_50     |    1.1145 |   7 |   5 |    1.0628 | 0.1773 |   0.7548 | -0.5845 |   0.3034 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0|rv21_pct_lt_50              |
| swap1          | -roc20_gt_0+ar1_30_gt_0        |    1.1079 |   7 |   4 |    1.0624 | 0.1930 |   0.7732 | -0.6621 |   0.2916 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0|ar1_30_gt_0                 |
| swap1          | -roc20_gt_0+rv21_lt_40         |    1.1076 |   7 |   5 |    1.0547 | 0.1854 |   0.7576 | -0.6062 |   0.3059 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0|rv21_lt_40                  |
| swap1          | -px_gt_ema200+px_gt_sma100     |    1.1066 |   7 |   4 |    1.0515 | 0.1845 |   0.7526 | -0.5942 |   0.3104 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0                  |
| swap1          | -roc20_gt_0+px_gt_sma200       |    1.1061 |   7 |   5 |    1.0497 | 0.1828 |   0.7533 | -0.5842 |   0.3129 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma200|px_gt_ema200|px_gt_ema250|roc60_gt_0                |
| swap1          | -px_gt_sma10+px_gt_ema50       |    1.1060 |   7 |   5 |    1.0488 | 0.1770 |   0.7437 | -0.5617 |   0.3151 | px_gt_sma20|px_gt_ema50|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                  |
| swap1          | -px_gt_ema250+rv21_pct_lt_70   |    1.1056 |   7 |   4 |    1.0478 | 0.1809 |   0.7465 | -0.5722 |   0.3161 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0|rv21_pct_lt_70                |
| swap1          | -roc20_gt_0+px_gt_sma150       |    1.1055 |   7 |   5 |    1.0516 | 0.1826 |   0.7525 | -0.5932 |   0.3079 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma150|px_gt_ema200|px_gt_ema250|roc60_gt_0                |
| swap1          | -roc60_gt_0+rv21_pct_lt_70     |    1.1037 |   7 |   4 |    1.0482 | 0.1807 |   0.7450 | -0.5811 |   0.3110 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|rv21_pct_lt_70              |
| swap1          | -roc20_gt_0+px_gt_sma250       |    1.1013 |   7 |   5 |    1.0453 | 0.1818 |   0.7496 | -0.5821 |   0.3123 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc60_gt_0                |
| swap1          | -px_gt_ema200+px_gt_sma150     |    1.1005 |   7 |   4 |    1.0415 | 0.1828 |   0.7468 | -0.5738 |   0.3185 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma150|px_gt_ema250|roc20_gt_0|roc60_gt_0                  |
| drop1          | -roc20_gt_0                    |    1.0997 |   6 |   4 |    1.0393 | 0.1823 |   0.7477 | -0.6062 |   0.3008 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0                             |
| swap1          | -px_gt_sma10+rsi14_gt_50       |    1.0982 |   7 |   4 |    1.0470 | 0.1829 |   0.7469 | -0.6049 |   0.3023 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50                  |
| swap1          | -roc20_gt_0+sma100_gt_sma250   |    1.0969 |   7 |   5 |    1.0384 | 0.1798 |   0.7448 | -0.5661 |   0.3175 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma100_gt_sma250|roc60_gt_0            |
| swap1          | -roc20_gt_0+stochrsi14_gt_50   |    1.0968 |   7 |   4 |    1.0453 | 0.1856 |   0.7524 | -0.6128 |   0.3030 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0|stochrsi14_gt_50            |
| swap1          | -px_gt_ema200+roc120_gt_0      |    1.0936 |   7 |   4 |    1.0435 | 0.1836 |   0.7500 | -0.6117 |   0.3002 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0                   |
| swap1          | -roc20_gt_0+px_gt_sma100       |    1.0903 |   7 |   5 |    1.0487 | 0.1828 |   0.7528 | -0.6439 |   0.2839 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0                |
| swap1          | -roc20_gt_0+sma50_gt_sma150    |    1.0889 |   7 |   5 |    1.0372 | 0.1790 |   0.7433 | -0.5901 |   0.3034 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma50_gt_sma150|roc60_gt_0             |
| swap1          | -roc60_gt_0+px_gt_sma150       |    1.0873 |   7 |   4 |    1.0262 | 0.1831 |   0.7434 | -0.5670 |   0.3229 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma150|px_gt_ema200|px_gt_ema250|roc20_gt_0                |
| add1           | +px_gt_sma150                  |    1.0855 |   8 |   5 |    1.0376 | 0.1805 |   0.7419 | -0.5707 |   0.3163 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0     |
| swap1          | -px_gt_sma10+sma100_gt_sma250  |    1.0851 |   7 |   5 |    1.0326 | 0.1778 |   0.7387 | -0.5830 |   0.3050 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma100_gt_sma250|roc20_gt_0|roc60_gt_0             |
| swap1          | -px_gt_sma10+stochrsi14_gt_50  |    1.0780 |   7 |   4 |    1.0312 | 0.1804 |   0.7381 | -0.6139 |   0.2939 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|stochrsi14_gt_50             |
| swap1          | -px_gt_sma10+px_gt_ema50       |    1.0765 |   7 |   4 |    1.0218 | 0.1789 |   0.7336 | -0.5777 |   0.3097 | px_gt_sma20|px_gt_ema50|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                  |
| swap1          | -px_gt_sma20+ar1_30_gt_0       |    1.0763 |   7 |   5 |    1.0367 | 0.1752 |   0.7406 | -0.6261 |   0.2798 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|ar1_30_gt_0                  |
| swap1          | -px_gt_ema200+sma20_gt_sma100  |    1.0743 |   7 |   4 |    1.0224 | 0.1786 |   0.7343 | -0.5881 |   0.3037 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|sma20_gt_sma100|roc20_gt_0|roc60_gt_0               |
| add1           | +sma50_gt_sma200               |    1.0741 |   8 |   5 |    1.0301 | 0.1793 |   0.7383 | -0.5816 |   0.3082 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma50_gt_sma200|roc20_gt_0|roc60_gt_0  |
| swap1          | -px_gt_ema200+px_gt_sma200     |    1.0741 |   7 |   4 |    1.0258 | 0.1794 |   0.7362 | -0.6048 |   0.2966 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma200|px_gt_ema250|roc20_gt_0|roc60_gt_0                  |
| swap1          | -px_gt_ema250+px_gt_sma100     |    1.0733 |   7 |   4 |    1.0244 | 0.1785 |   0.7337 | -0.5992 |   0.2979 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0                  |
| swap1          | -roc20_gt_0+rv21_pct_lt_70     |    1.0723 |   7 |   4 |    1.0307 | 0.1807 |   0.7393 | -0.6370 |   0.2837 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0|rv21_pct_lt_70              |
| swap1          | -px_gt_ema250+px_gt_sma150     |    1.0723 |   7 |   4 |    1.0179 | 0.1776 |   0.7305 | -0.5751 |   0.3089 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma150|px_gt_ema200|roc20_gt_0|roc60_gt_0                  |
| swap1          | -px_gt_ema200+sma100_gt_sma250 |    1.0720 |   7 |   4 |    1.0154 | 0.1778 |   0.7298 | -0.5671 |   0.3136 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|sma100_gt_sma250|roc20_gt_0|roc60_gt_0              |
| add1           | +sma50_gt_sma150               |    1.0718 |   8 |   5 |    1.0283 | 0.1787 |   0.7371 | -0.5819 |   0.3071 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma50_gt_sma150|roc20_gt_0|roc60_gt_0  |
| swap1          | -px_gt_sma20+px_gt_sma150      |    1.0703 |   7 |   4 |    1.0166 | 0.1818 |   0.7377 | -0.5913 |   0.3074 | px_gt_sma10|px_gt_ema100|px_gt_sma150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema200+rv21_lt_40       |    1.0698 |   7 |   4 |    1.0231 | 0.1821 |   0.7369 | -0.6202 |   0.2936 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0|rv21_lt_40                    |
| add1           | +px_gt_sma200                  |    1.0698 |   8 |   5 |    1.0233 | 0.1776 |   0.7331 | -0.5667 |   0.3134 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma200|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0     |
| swap1          | -roc20_gt_0+px_gt_sma150       |    1.0694 |   7 |   4 |    1.0210 | 0.1836 |   0.7422 | -0.6186 |   0.2968 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma150|px_gt_ema200|px_gt_ema250|roc60_gt_0                |
| swap1          | -px_gt_ema250+sma50_gt_sma150  |    1.0694 |   7 |   4 |    1.0219 | 0.1788 |   0.7340 | -0.6059 |   0.2951 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|sma50_gt_sma150|roc20_gt_0|roc60_gt_0               |
| swap1          | -roc20_gt_0+px_gt_sma50        |    1.0690 |   7 |   5 |    1.0332 | 0.1754 |   0.7381 | -0.6430 |   0.2728 | px_gt_sma10|px_gt_sma20|px_gt_sma50|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0                 |
| add1           | +stochrsi14_gt_50              |    1.0689 |   8 |   5 |    1.0303 | 0.1745 |   0.7343 | -0.5874 |   0.2971 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|stochrsi14_gt_50 |
| add1           | +ar1_30_gt_0                   |    1.0689 |   8 |   5 |    1.0395 | 0.1777 |   0.7426 | -0.6358 |   0.2795 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|ar1_30_gt_0      |

## Best By Neighborhood

| neighborhood   | change                     |   fitness |   n |   k |   sortino |   cagr |     mdd | signals                                                                                             |
|:---------------|:---------------------------|----------:|----:|----:|----------:|-------:|--------:|:----------------------------------------------------------------------------------------------------|
| swap1          | -roc20_gt_0+rv21_pct_lt_70 |    1.1707 |   7 |   5 |    1.1101 | 0.1904 | -0.5925 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0|rv21_pct_lt_70            |
| add1           | +rv21_pct_lt_70            |    1.1342 |   8 |   5 |    1.0834 | 0.1872 | -0.5814 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rv21_pct_lt_70 |
| drop1          | -roc20_gt_0                |    1.0997 |   6 |   4 |    1.0393 | 0.1823 | -0.6062 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc60_gt_0                           |
| base           | none                       |    1.0222 |   7 |   4 |    0.9853 | 0.1700 | -0.6197 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                |

## Method Notes

- Neighborhood = base, one-signal drops, one-signal additions, and one-for-one swaps.
- All valid `k=1..n` thresholds are evaluated for every neighbor.
- Signals are lagged one trading day before earning returns to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.
- This is candidate discovery only; final claims require PBO/DSR/WF/OOS/FWD/bootstrap gates `[advances_fin_ml, p.208-211]`.
