# Stage 4 Regime-Gated Bridge

Status: economic-first research report. PBO/DSR are intentionally not used to block `economic_pass`; mandate deployment remains blocked without them.

Branch: `QQQ`
Risk-on: `QLD_2x` (`QLD`)
Off leg: `CASH_USD`
Extra lag days: `1`
Window: `2010-02-12` to `2026-04-14` (4,066 bars)
Base rule: `sma100_gt_sma250|roc10_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70`, `k=3`
Candidates: 10
Bootstrap paths: 500
Elapsed seconds: 1.0

## Top Economic Results

| label                               | gate                       | gate_family       | economic_pass   |   sortino |   cagr |   sharpe |     mdd |   calmar |   end_mult |   wf_pass_windows |   bootstrap_ci_low_sharpe |   rolling_3y_pct_pos |   rolling_5y_pct_pos |   rolling_10y_pct_pos |   rolling_15y_pct_pos |
|:------------------------------------|:---------------------------|:------------------|:----------------|----------:|-------:|---------:|--------:|---------:|-----------:|------------------:|--------------------------:|---------------------:|---------------------:|----------------------:|----------------------:|
| base_and_none                       | none                       | none              | True            |    1.4209 | 0.3626 |   1.1900 | -0.3754 |   0.9659 |   147.2869 |                 7 |                    0.6050 |               1.0000 |               1.0000 |                1.0000 |                1.0000 |
| base_and_dd252_gt_m30               | dd252_gt_m30               | crash_distance    | True            |    1.4157 | 0.3608 |   1.2025 | -0.3754 |   0.9610 |   144.1333 |                 7 |                    0.6306 |               1.0000 |               1.0000 |                1.0000 |                1.0000 |
| base_and_dd252_gt_m20               | dd252_gt_m20               | crash_distance    | True            |    1.3467 | 0.3383 |   1.1593 | -0.3754 |   0.9011 |   110.1267 |                 7 |                    0.6085 |               1.0000 |               1.0000 |                1.0000 |                1.0000 |
| base_and_sma200_slope_21_gt_0       | sma200_slope_21_gt_0       | trend_slope       | False           |    1.1571 | 0.2824 |   1.0286 | -0.3725 |   0.7581 |    55.3017 |                 5 |                    0.4584 |               1.0000 |               1.0000 |                1.0000 |                1.0000 |
| base_and_px_gt_ema200               | px_gt_ema200               | trend             | False           |    1.1508 | 0.2709 |   1.0212 | -0.3362 |   0.8060 |    47.8699 |                 5 |                    0.4654 |               0.9937 |               1.0000 |                1.0000 |                1.0000 |
| base_and_px_gt_sma200               | px_gt_sma200               | trend             | False           |    1.0936 | 0.2551 |   0.9830 | -0.3037 |   0.8399 |    39.0907 |                 4 |                    0.4407 |               0.9937 |               1.0000 |                1.0000 |                1.0000 |
| base_and_px_gt_sma250               | px_gt_sma250               | trend             | False           |    1.0421 | 0.2418 |   0.9349 | -0.3319 |   0.7284 |    32.9157 |                 5 |                    0.3254 |               0.9747 |               1.0000 |                1.0000 |                1.0000 |
| base_and_qqq_spy_rs_sma50_gt_sma200 | qqq_spy_rs_sma50_gt_sma200 | relative_strength | False           |    0.8330 | 0.1950 |   0.8226 | -0.4368 |   0.4464 |    17.7158 |                 3 |                    0.2923 |               0.9620 |               1.0000 |                1.0000 |                1.0000 |
| base_and_rv21_pct_lt_70             | rv21_pct_lt_70             | volatility        | False           |    0.8109 | 0.1737 |   0.7877 | -0.3434 |   0.5058 |    13.2524 |                 2 |                    0.1917 |               0.9937 |               1.0000 |                1.0000 |                1.0000 |
| base_and_rv21_pct_lt_50             | rv21_pct_lt_50             | volatility        | False           |    0.6503 | 0.1277 |   0.7110 | -0.3683 |   0.3466 |     6.9490 |                 3 |                    0.1986 |               0.9747 |               0.9851 |                1.0000 |                1.0000 |

## Economic Gate Summary

| label                               | gate                       | oos_pass   | fwd_pass   | wf_pass   | bootstrap_pass   | rolling_economic_pass   | economic_pass   | mandate_pass   |
|:------------------------------------|:---------------------------|:-----------|:-----------|:----------|:-----------------|:------------------------|:----------------|:---------------|
| base_and_none                       | none                       | True       | True       | True      | True             | True                    | True            | False          |
| base_and_px_gt_sma200               | px_gt_sma200               | True       | True       | False     | True             | True                    | False           | False          |
| base_and_px_gt_sma250               | px_gt_sma250               | True       | True       | False     | True             | True                    | False           | False          |
| base_and_px_gt_ema200               | px_gt_ema200               | True       | True       | False     | True             | True                    | False           | False          |
| base_and_sma200_slope_21_gt_0       | sma200_slope_21_gt_0       | True       | True       | False     | True             | True                    | False           | False          |
| base_and_dd252_gt_m20               | dd252_gt_m20               | True       | True       | True      | True             | True                    | True            | False          |
| base_and_dd252_gt_m30               | dd252_gt_m30               | True       | True       | True      | True             | True                    | True            | False          |
| base_and_rv21_pct_lt_70             | rv21_pct_lt_70             | True       | True       | False     | True             | True                    | False           | False          |
| base_and_rv21_pct_lt_50             | rv21_pct_lt_50             | True       | True       | False     | True             | True                    | False           | False          |
| base_and_qqq_spy_rs_sma50_gt_sma200 | qqq_spy_rs_sma50_gt_sma200 | True       | True       | False     | True             | True                    | False           | False          |

## Rolling Window Detail

| label                               | gate                       |   window_years |   n_windows |   min_cagr |   median_cagr |   pct_positive_cagr |   worst_mdd |   min_sharpe |
|:------------------------------------|:---------------------------|---------------:|------------:|-----------:|--------------:|--------------------:|------------:|-------------:|
| base_and_none                       | none                       |              3 |         158 |     0.1320 |        0.3275 |              1.0000 |     -0.3754 |       0.5794 |
| base_and_none                       | none                       |              5 |         134 |     0.0984 |        0.3687 |              1.0000 |     -0.3754 |       0.4888 |
| base_and_none                       | none                       |             10 |          74 |     0.2576 |        0.3724 |              1.0000 |     -0.3754 |       0.9851 |
| base_and_none                       | none                       |             15 |          14 |     0.3165 |        0.3493 |              1.0000 |     -0.3754 |       1.0754 |
| base_and_px_gt_sma200               | px_gt_sma200               |              3 |         158 |    -0.0132 |        0.2786 |              0.9937 |     -0.3037 |       0.0575 |
| base_and_px_gt_sma200               | px_gt_sma200               |              5 |         134 |     0.0813 |        0.2923 |              1.0000 |     -0.3037 |       0.4408 |
| base_and_px_gt_sma200               | px_gt_sma200               |             10 |          74 |     0.1891 |        0.3067 |              1.0000 |     -0.3037 |       0.8445 |
| base_and_px_gt_sma200               | px_gt_sma200               |             15 |          14 |     0.2505 |        0.2640 |              1.0000 |     -0.3037 |       0.9671 |
| base_and_px_gt_sma250               | px_gt_sma250               |              3 |         158 |    -0.0487 |        0.2790 |              0.9747 |     -0.3319 |      -0.1025 |
| base_and_px_gt_sma250               | px_gt_sma250               |              5 |         134 |     0.0908 |        0.2800 |              1.0000 |     -0.3319 |       0.4649 |
| base_and_px_gt_sma250               | px_gt_sma250               |             10 |          74 |     0.1666 |        0.2985 |              1.0000 |     -0.3319 |       0.7605 |
| base_and_px_gt_sma250               | px_gt_sma250               |             15 |          14 |     0.2231 |        0.2480 |              1.0000 |     -0.3319 |       0.8799 |
| base_and_px_gt_ema200               | px_gt_ema200               |              3 |         158 |    -0.0118 |        0.2952 |              0.9937 |     -0.3362 |       0.0676 |
| base_and_px_gt_ema200               | px_gt_ema200               |              5 |         134 |     0.0880 |        0.3148 |              1.0000 |     -0.3362 |       0.4618 |
| base_and_px_gt_ema200               | px_gt_ema200               |             10 |          74 |     0.1859 |        0.3180 |              1.0000 |     -0.3362 |       0.8291 |
| base_and_px_gt_ema200               | px_gt_ema200               |             15 |          14 |     0.2536 |        0.2751 |              1.0000 |     -0.3362 |       0.9716 |
| base_and_sma200_slope_21_gt_0       | sma200_slope_21_gt_0       |              3 |         158 |     0.0737 |        0.2894 |              1.0000 |     -0.3725 |       0.4152 |
| base_and_sma200_slope_21_gt_0       | sma200_slope_21_gt_0       |              5 |         134 |     0.1310 |        0.3104 |              1.0000 |     -0.3725 |       0.6418 |
| base_and_sma200_slope_21_gt_0       | sma200_slope_21_gt_0       |             10 |          74 |     0.2127 |        0.3357 |              1.0000 |     -0.3725 |       0.8959 |
| base_and_sma200_slope_21_gt_0       | sma200_slope_21_gt_0       |             15 |          14 |     0.2737 |        0.2904 |              1.0000 |     -0.3725 |       1.0010 |
| base_and_dd252_gt_m20               | dd252_gt_m20               |              3 |         158 |     0.1414 |        0.3047 |              1.0000 |     -0.3754 |       0.6545 |
| base_and_dd252_gt_m20               | dd252_gt_m20               |              5 |         134 |     0.0984 |        0.3358 |              1.0000 |     -0.3754 |       0.4888 |
| base_and_dd252_gt_m20               | dd252_gt_m20               |             10 |          74 |     0.2725 |        0.3440 |              1.0000 |     -0.3754 |       1.0509 |
| base_and_dd252_gt_m20               | dd252_gt_m20               |             15 |          14 |     0.3102 |        0.3295 |              1.0000 |     -0.3754 |       1.0733 |
| base_and_dd252_gt_m30               | dd252_gt_m30               |              3 |         158 |     0.1414 |        0.3275 |              1.0000 |     -0.3754 |       0.6545 |
| base_and_dd252_gt_m30               | dd252_gt_m30               |              5 |         134 |     0.0984 |        0.3687 |              1.0000 |     -0.3754 |       0.4888 |
| base_and_dd252_gt_m30               | dd252_gt_m30               |             10 |          74 |     0.2725 |        0.3724 |              1.0000 |     -0.3754 |       1.0509 |
| base_and_dd252_gt_m30               | dd252_gt_m30               |             15 |          14 |     0.3340 |        0.3536 |              1.0000 |     -0.3754 |       1.1207 |
| base_and_rv21_pct_lt_70             | rv21_pct_lt_70             |              3 |         158 |    -0.0071 |        0.1875 |              0.9937 |     -0.3434 |       0.0849 |
| base_and_rv21_pct_lt_70             | rv21_pct_lt_70             |              5 |         134 |     0.0644 |        0.1703 |              1.0000 |     -0.3434 |       0.4237 |
| base_and_rv21_pct_lt_70             | rv21_pct_lt_70             |             10 |          74 |     0.1208 |        0.1830 |              1.0000 |     -0.3434 |       0.5996 |
| base_and_rv21_pct_lt_70             | rv21_pct_lt_70             |             15 |          14 |     0.1625 |        0.1790 |              1.0000 |     -0.3434 |       0.7511 |
| base_and_rv21_pct_lt_50             | rv21_pct_lt_50             |              3 |         158 |    -0.0214 |        0.1159 |              0.9747 |     -0.3683 |      -0.0795 |
| base_and_rv21_pct_lt_50             | rv21_pct_lt_50             |              5 |         134 |    -0.0047 |        0.1169 |              0.9851 |     -0.3683 |       0.0638 |
| base_and_rv21_pct_lt_50             | rv21_pct_lt_50             |             10 |          74 |     0.0803 |        0.1074 |              1.0000 |     -0.3683 |       0.5239 |
| base_and_rv21_pct_lt_50             | rv21_pct_lt_50             |             15 |          14 |     0.1164 |        0.1342 |              1.0000 |     -0.3683 |       0.6653 |
| base_and_qqq_spy_rs_sma50_gt_sma200 | qqq_spy_rs_sma50_gt_sma200 |              3 |         158 |    -0.0466 |        0.1756 |              0.9620 |     -0.4368 |      -0.0427 |
| base_and_qqq_spy_rs_sma50_gt_sma200 | qqq_spy_rs_sma50_gt_sma200 |              5 |         134 |     0.0284 |        0.1795 |              1.0000 |     -0.4368 |       0.2484 |
| base_and_qqq_spy_rs_sma50_gt_sma200 | qqq_spy_rs_sma50_gt_sma200 |             10 |          74 |     0.1539 |        0.2546 |              1.0000 |     -0.4368 |       0.7369 |
| base_and_qqq_spy_rs_sma50_gt_sma200 | qqq_spy_rs_sma50_gt_sma200 |             15 |          14 |     0.1933 |        0.2053 |              1.0000 |     -0.4368 |       0.8085 |

## Method Notes

- Regime gates are simple overlays on the fixed modern vote, not a new broad optimization grid.
- Signals earn returns only after `1 + extra_lag_days` bars to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.
- `economic_pass` requires OOS, FWD, WF, bootstrap and rolling-window coverage. It deliberately ignores PBO/DSR for this exploratory view.
- `mandate_pass` is always false in this runner because deployment still requires PBO and DSR elsewhere `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.
