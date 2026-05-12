# Stage 1 Local Search Results

Status: exact one-edit neighborhood diagnostic. This is not a deploy verdict.

Branch: `QQQ`
Risk-on: `TQQQ_3x`
Off leg: `ZROZSIM`
Base k: `5`
Base signals: `px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0`
Neighbor subsets: 216
Configs tested: 1,531
Elapsed seconds: 1.3

## Base Incumbent

|   fitness |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                              |
|----------:|----:|----:|----------:|-------:|---------:|--------:|---------:|:-------------------------------------------------------------------------------------|
|    1.4426 |   7 |   5 |    1.2478 | 0.4031 |   0.9473 | -0.7222 |   0.5581 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0 |

## Top Local Candidates

| neighborhood   | change                         |   fitness |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                                              |
|:---------------|:-------------------------------|----------:|----:|----:|----------:|-------:|---------:|--------:|---------:|:-----------------------------------------------------------------------------------------------------|
| add1           | +roc120_gt_0                   |    1.4570 |   8 |   6 |    1.2557 | 0.3971 |   0.9469 | -0.6558 |   0.6055 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0     |
| base           | none                           |    1.4426 |   7 |   5 |    1.2478 | 0.4031 |   0.9473 | -0.7222 |   0.5581 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema100+roc120_gt_0      |    1.4392 |   7 |   5 |    1.2502 | 0.3988 |   0.9428 | -0.7305 |   0.5460 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0                  |
| swap1          | -px_gt_ema100+px_gt_sma100     |    1.4298 |   7 |   5 |    1.2253 | 0.3900 |   0.9300 | -0.6591 |   0.5917 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma10+px_gt_ema20       |    1.4160 |   7 |   5 |    1.2229 | 0.3887 |   0.9265 | -0.6915 |   0.5621 | px_gt_sma20|px_gt_ema20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma20+macd_gt_signal    |    1.4120 |   7 |   5 |    1.2149 | 0.3855 |   0.9222 | -0.6709 |   0.5747 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|macd_gt_signal|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_sma20+macd_hist_gt_0    |    1.4120 |   7 |   5 |    1.2149 | 0.3855 |   0.9222 | -0.6709 |   0.5747 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|macd_hist_gt_0|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_ema200+px_gt_sma250     |    1.4116 |   7 |   5 |    1.2254 | 0.3920 |   0.9311 | -0.7222 |   0.5428 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema200+roc120_gt_0      |    1.4102 |   7 |   5 |    1.2141 | 0.3826 |   0.9177 | -0.6669 |   0.5738 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0                  |
| swap1          | -px_gt_ema250+roc120_gt_0      |    1.4096 |   7 |   5 |    1.2139 | 0.3822 |   0.9170 | -0.6669 |   0.5731 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0|roc120_gt_0                  |
| swap1          | -px_gt_sma10+px_gt_ema10       |    1.4093 |   7 |   5 |    1.2385 | 0.3988 |   0.9413 | -0.7938 |   0.5023 | px_gt_ema10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema250+px_gt_sma250     |    1.4070 |   7 |   5 |    1.2219 | 0.3905 |   0.9287 | -0.7222 |   0.5406 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_sma250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma10+rsi14_gt_50       |    1.4024 |   7 |   5 |    1.2005 | 0.3754 |   0.9065 | -0.6312 |   0.5947 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50                 |
| add1           | +px_gt_sma250                  |    1.4020 |   8 |   6 |    1.2215 | 0.3847 |   0.9272 | -0.6897 |   0.5578 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0    |
| swap1          | -px_gt_ema100+px_gt_sma150     |    1.3988 |   7 |   5 |    1.2235 | 0.3880 |   0.9270 | -0.7488 |   0.5181 | px_gt_sma10|px_gt_sma20|px_gt_sma150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma20+rsi14_gt_50       |    1.3985 |   7 |   5 |    1.2140 | 0.3869 |   0.9211 | -0.7151 |   0.5411 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50                 |
| swap1          | -px_gt_ema100+px_gt_sma250     |    1.3979 |   7 |   5 |    1.2171 | 0.3865 |   0.9229 | -0.7260 |   0.5324 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma20+px_gt_ema20       |    1.3960 |   7 |   5 |    1.2106 | 0.3865 |   0.9216 | -0.7109 |   0.5437 | px_gt_sma10|px_gt_ema20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema100+sma20_gt_sma100  |    1.3898 |   7 |   5 |    1.2101 | 0.3803 |   0.9185 | -0.7134 |   0.5331 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|sma20_gt_sma100|roc20_gt_0|roc60_gt_0              |
| add1           | +px_gt_sma50                   |    1.3885 |   8 |   6 |    1.1998 | 0.3681 |   0.9053 | -0.6232 |   0.5907 | px_gt_sma10|px_gt_sma20|px_gt_sma50|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0     |
| swap1          | -roc60_gt_0+px_gt_sma100       |    1.3797 |   7 |   5 |    1.1976 | 0.3788 |   0.9091 | -0.7018 |   0.5397 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0               |
| add1           | +px_gt_sma200                  |    1.3773 |   8 |   6 |    1.1955 | 0.3702 |   0.9050 | -0.6493 |   0.5702 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma200|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0    |
| swap1          | -px_gt_ema200+px_gt_sma200     |    1.3746 |   7 |   5 |    1.2000 | 0.3773 |   0.9090 | -0.7227 |   0.5220 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| add1           | +px_gt_sma100                  |    1.3718 |   8 |   6 |    1.1976 | 0.3748 |   0.9098 | -0.6847 |   0.5474 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0    |
| swap1          | -px_gt_ema100+px_gt_sma200     |    1.3711 |   7 |   5 |    1.1969 | 0.3734 |   0.9043 | -0.7143 |   0.5228 | px_gt_sma10|px_gt_sma20|px_gt_sma200|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema250+sma100_gt_sma250 |    1.3686 |   7 |   5 |    1.1944 | 0.3765 |   0.9088 | -0.7222 |   0.5213 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|sma100_gt_sma250|roc20_gt_0|roc60_gt_0             |
| swap1          | -px_gt_ema200+sma50_gt_sma200  |    1.3664 |   7 |   5 |    1.1932 | 0.3752 |   0.9062 | -0.7222 |   0.5195 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|sma50_gt_sma200|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_ema250+px_gt_sma200     |    1.3663 |   7 |   5 |    1.1940 | 0.3743 |   0.9042 | -0.7227 |   0.5178 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma200|px_gt_ema200|roc20_gt_0|roc60_gt_0                 |
| drop1          | -px_gt_sma10                   |    1.3662 |   6 |   5 |    1.1805 | 0.3531 |   0.8891 | -0.6564 |   0.5379 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                             |
| swap1          | -px_gt_sma10+sma20_gt_sma100   |    1.3648 |   7 |   6 |    1.1848 | 0.3488 |   0.8951 | -0.6318 |   0.5520 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma20_gt_sma100|roc20_gt_0|roc60_gt_0             |
| add1           | +px_gt_ema150                  |    1.3641 |   8 |   6 |    1.2009 | 0.3776 |   0.9135 | -0.7283 |   0.5185 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0    |
| swap1          | -px_gt_ema200+px_gt_sma100     |    1.3631 |   7 |   5 |    1.1744 | 0.3659 |   0.8911 | -0.6477 |   0.5649 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| add1           | +px_gt_sma150                  |    1.3584 |   8 |   6 |    1.1974 | 0.3732 |   0.9077 | -0.7244 |   0.5152 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0    |
| swap1          | -px_gt_ema250+sma50_gt_sma200  |    1.3554 |   7 |   5 |    1.1853 | 0.3712 |   0.9001 | -0.7222 |   0.5140 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|sma50_gt_sma200|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_ema100+sma50_gt_sma200  |    1.3543 |   7 |   5 |    1.1858 | 0.3706 |   0.8995 | -0.7260 |   0.5104 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|sma50_gt_sma200|roc20_gt_0|roc60_gt_0              |
| add1           | +px_gt_ema50                   |    1.3536 |   8 |   6 |    1.1717 | 0.3618 |   0.8909 | -0.6279 |   0.5762 | px_gt_sma10|px_gt_sma20|px_gt_ema50|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0     |
| drop1          | -px_gt_ema100                  |    1.3517 |   6 |   4 |    1.1953 | 0.3846 |   0.9084 | -0.8457 |   0.4548 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                              |
| swap1          | -px_gt_ema200+sma100_gt_sma250 |    1.3515 |   7 |   5 |    1.1818 | 0.3707 |   0.8996 | -0.7222 |   0.5132 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|sma100_gt_sma250|roc20_gt_0|roc60_gt_0             |
| swap1          | -px_gt_sma10+macd_gt_signal    |    1.3514 |   7 |   5 |    1.1866 | 0.3665 |   0.8976 | -0.7277 |   0.5036 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|macd_gt_signal|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_sma10+macd_hist_gt_0    |    1.3514 |   7 |   5 |    1.1866 | 0.3665 |   0.8976 | -0.7277 |   0.5036 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|macd_hist_gt_0|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_ema250+px_gt_sma100     |    1.3495 |   7 |   5 |    1.1646 | 0.3611 |   0.8836 | -0.6477 |   0.5575 | px_gt_sma10|px_gt_sma20|px_gt_sma100|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema100+sma50_gt_sma150  |    1.3488 |   7 |   5 |    1.1820 | 0.3640 |   0.8930 | -0.7143 |   0.5096 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|sma50_gt_sma150|roc20_gt_0|roc60_gt_0              |
| swap1          | -px_gt_sma20+px_gt_ema10       |    1.3473 |   7 |   5 |    1.1780 | 0.3721 |   0.8994 | -0.7275 |   0.5115 | px_gt_sma10|px_gt_ema10|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema100+px_gt_ema150     |    1.3469 |   7 |   5 |    1.1940 | 0.3758 |   0.9073 | -0.7959 |   0.4721 | px_gt_sma10|px_gt_sma20|px_gt_ema150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_ema200+px_gt_sma150     |    1.3462 |   7 |   5 |    1.1898 | 0.3711 |   0.9000 | -0.7702 |   0.4819 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_sma150|px_gt_ema250|roc20_gt_0|roc60_gt_0                 |
| swap1          | -px_gt_sma10+px_gt_ema150      |    1.3462 |   7 |   6 |    1.1744 | 0.3502 |   0.8845 | -0.6613 |   0.5295 | px_gt_sma20|px_gt_ema100|px_gt_ema150|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                |
| add1           | +sma50_gt_sma200               |    1.3459 |   8 |   6 |    1.1813 | 0.3645 |   0.8968 | -0.6897 |   0.5286 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|sma50_gt_sma200|roc20_gt_0|roc60_gt_0 |
| swap1          | -px_gt_sma20+stochrsi14_gt_50  |    1.3411 |   7 |   5 |    1.1702 | 0.3657 |   0.8896 | -0.7048 |   0.5188 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|stochrsi14_gt_50            |
| swap1          | -roc60_gt_0+roc120_gt_0        |    1.3401 |   7 |   5 |    1.1774 | 0.3648 |   0.8892 | -0.7305 |   0.4995 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc120_gt_0                |
| swap1          | -px_gt_sma10+px_gt_sma250      |    1.3384 |   7 |   6 |    1.1645 | 0.3448 |   0.8770 | -0.6410 |   0.5379 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0                |

## Best By Neighborhood

| neighborhood   | change                    |   fitness |   n |   k |   sortino |   cagr |     mdd | signals                                                                                          |
|:---------------|:--------------------------|----------:|----:|----:|----------:|-------:|--------:|:-------------------------------------------------------------------------------------------------|
| add1           | +roc120_gt_0              |    1.4570 |   8 |   6 |    1.2557 | 0.3971 | -0.6558 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0 |
| base           | none                      |    1.4426 |   7 |   5 |    1.2478 | 0.4031 | -0.7222 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0             |
| swap1          | -px_gt_ema100+roc120_gt_0 |    1.4392 |   7 |   5 |    1.2502 | 0.3988 | -0.7305 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0              |
| drop1          | -px_gt_sma10              |    1.3662 |   6 |   5 |    1.1805 | 0.3531 | -0.6564 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                         |

## Method Notes

- Neighborhood = base, one-signal drops, one-signal additions, and one-for-one swaps.
- All valid `k=1..n` thresholds are evaluated for every neighbor.
- Signals are lagged one trading day before earning returns to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.
- This is candidate discovery only; final claims require PBO/DSR/WF/OOS/FWD/bootstrap gates `[advances_fin_ml, p.208-211]`.
