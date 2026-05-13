# Stage 4 Regime-Gated Bridge

Status: economic-first research report. PBO/DSR are intentionally not used to block `economic_pass`; mandate deployment remains blocked without them.

Branch: `QQQ`
Risk-on: `TQQQ_3x` (`TQQQ`)
Off leg: `CASH_USD`
Extra lag days: `1`
Window: `2010-02-12` to `2026-04-14` (4,066 bars)
Base rule: `sma100_gt_sma250|roc10_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70`, `k=3`
Candidates: 10
Bootstrap paths: 500
Elapsed seconds: 1.1

## Top Economic Results

| label                               | gate                       | gate_family       | economic_pass   |   sortino |   cagr |   sharpe |     mdd |   calmar |   end_mult |   wf_pass_windows |   bootstrap_ci_low_sharpe |   rolling_3y_pct_pos |   rolling_5y_pct_pos |   rolling_10y_pct_pos |   rolling_15y_pct_pos |
|:------------------------------------|:---------------------------|:------------------|:----------------|----------:|-------:|---------:|--------:|---------:|-----------:|------------------:|--------------------------:|---------------------:|---------------------:|----------------------:|----------------------:|
| base_and_none                       | none                       | none              | True            |    1.4124 | 0.5300 |   1.1849 | -0.5103 |   1.0386 |   955.0132 |                 7 |                    0.6084 |               1.0000 |               1.0000 |                1.0000 |                1.0000 |
| base_and_dd252_gt_m30               | dd252_gt_m30               | crash_distance    | True            |    1.4060 | 0.5279 |   1.1958 | -0.5103 |   1.0345 |   933.9301 |                 7 |                    0.6290 |               1.0000 |               1.0000 |                1.0000 |                1.0000 |
| base_and_dd252_gt_m20               | dd252_gt_m20               | crash_distance    | True            |    1.3370 | 0.4917 |   1.1521 | -0.5103 |   0.9635 |   634.3619 |                 7 |                    0.5997 |               1.0000 |               1.0000 |                1.0000 |                1.0000 |
| base_and_px_gt_ema200               | px_gt_ema200               | trend             | False           |    1.1443 | 0.3878 |   1.0148 | -0.4674 |   0.8296 |   197.8700 |                 5 |                    0.4613 |               0.9810 |               1.0000 |                1.0000 |                1.0000 |
| base_and_sma200_slope_21_gt_0       | sma200_slope_21_gt_0       | trend_slope       | False           |    1.1440 | 0.4008 |   1.0192 | -0.5090 |   0.7874 |   229.9503 |                 5 |                    0.4472 |               1.0000 |               1.0000 |                1.0000 |                1.0000 |
| base_and_px_gt_sma200               | px_gt_sma200               | trend             | False           |    1.0854 | 0.3621 |   0.9752 | -0.4273 |   0.8474 |   146.3481 |                 5 |                    0.4332 |               0.9810 |               1.0000 |                1.0000 |                1.0000 |
| base_and_px_gt_sma250               | px_gt_sma250               | trend             | False           |    1.0349 | 0.3401 |   0.9278 | -0.4633 |   0.7342 |   112.5864 |                 5 |                    0.3216 |               0.9684 |               1.0000 |                1.0000 |                1.0000 |
| base_and_qqq_spy_rs_sma50_gt_sma200 | qqq_spy_rs_sma50_gt_sma200 | relative_strength | False           |    0.8199 | 0.2669 |   0.8121 | -0.5944 |   0.4490 |    45.4819 |                 4 |                    0.2779 |               0.9494 |               1.0000 |                1.0000 |                1.0000 |
| base_and_rv21_pct_lt_70             | rv21_pct_lt_70             | volatility        | False           |    0.8022 | 0.2392 |   0.7792 | -0.4756 |   0.5029 |    31.8215 |                 3 |                    0.1796 |               0.9810 |               1.0000 |                1.0000 |                1.0000 |
| base_and_rv21_pct_lt_50             | rv21_pct_lt_50             | volatility        | False           |    0.6408 | 0.1758 |   0.7005 | -0.5084 |   0.3458 |    13.6448 |                 3 |                    0.1805 |               0.9620 |               0.9851 |                1.0000 |                1.0000 |

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
| base_and_none                       | none                       |              3 |         158 |     0.1695 |        0.4852 |              1.0000 |     -0.5103 |       0.5864 |
| base_and_none                       | none                       |              5 |         134 |     0.1208 |        0.5382 |              1.0000 |     -0.5103 |       0.4940 |
| base_and_none                       | none                       |             10 |          74 |     0.3695 |        0.5508 |              1.0000 |     -0.5103 |       0.9870 |
| base_and_none                       | none                       |             15 |          14 |     0.4540 |        0.5078 |              1.0000 |     -0.5103 |       1.0712 |
| base_and_px_gt_sma200               | px_gt_sma200               |              3 |         158 |    -0.0411 |        0.4081 |              0.9810 |     -0.4273 |       0.0524 |
| base_and_px_gt_sma200               | px_gt_sma200               |              5 |         134 |     0.0955 |        0.4210 |              1.0000 |     -0.4273 |       0.4404 |
| base_and_px_gt_sma200               | px_gt_sma200               |             10 |          74 |     0.2672 |        0.4510 |              1.0000 |     -0.4273 |       0.8425 |
| base_and_px_gt_sma200               | px_gt_sma200               |             15 |          14 |     0.3555 |        0.3772 |              1.0000 |     -0.4273 |       0.9606 |
| base_and_px_gt_sma250               | px_gt_sma250               |              3 |         158 |    -0.0903 |        0.4078 |              0.9684 |     -0.4633 |      -0.1009 |
| base_and_px_gt_sma250               | px_gt_sma250               |              5 |         134 |     0.1115 |        0.4088 |              1.0000 |     -0.4633 |       0.4675 |
| base_and_px_gt_sma250               | px_gt_sma250               |             10 |          74 |     0.2324 |        0.4391 |              1.0000 |     -0.4633 |       0.7614 |
| base_and_px_gt_sma250               | px_gt_sma250               |             15 |          14 |     0.3114 |        0.3505 |              1.0000 |     -0.4633 |       0.8750 |
| base_and_px_gt_ema200               | px_gt_ema200               |              3 |         158 |    -0.0353 |        0.4365 |              0.9810 |     -0.4674 |       0.0759 |
| base_and_px_gt_ema200               | px_gt_ema200               |              5 |         134 |     0.1082 |        0.4504 |              1.0000 |     -0.4674 |       0.4688 |
| base_and_px_gt_ema200               | px_gt_ema200               |             10 |          74 |     0.2637 |        0.4682 |              1.0000 |     -0.4674 |       0.8313 |
| base_and_px_gt_ema200               | px_gt_ema200               |             15 |          14 |     0.3609 |        0.3936 |              1.0000 |     -0.4674 |       0.9674 |
| base_and_sma200_slope_21_gt_0       | sma200_slope_21_gt_0       |              3 |         158 |     0.0884 |        0.4144 |              1.0000 |     -0.5090 |       0.4151 |
| base_and_sma200_slope_21_gt_0       | sma200_slope_21_gt_0       |              5 |         134 |     0.1776 |        0.4566 |              1.0000 |     -0.5090 |       0.6453 |
| base_and_sma200_slope_21_gt_0       | sma200_slope_21_gt_0       |             10 |          74 |     0.3002 |        0.4891 |              1.0000 |     -0.5090 |       0.8926 |
| base_and_sma200_slope_21_gt_0       | sma200_slope_21_gt_0       |             15 |          14 |     0.3872 |        0.4128 |              1.0000 |     -0.5090 |       0.9934 |
| base_and_dd252_gt_m20               | dd252_gt_m20               |              3 |         158 |     0.1960 |        0.4513 |              1.0000 |     -0.5103 |       0.6613 |
| base_and_dd252_gt_m20               | dd252_gt_m20               |              5 |         134 |     0.1208 |        0.4872 |              1.0000 |     -0.5103 |       0.4940 |
| base_and_dd252_gt_m20               | dd252_gt_m20               |             10 |          74 |     0.3953 |        0.5053 |              1.0000 |     -0.5103 |       1.0506 |
| base_and_dd252_gt_m20               | dd252_gt_m20               |             15 |          14 |     0.4427 |        0.4774 |              1.0000 |     -0.5103 |       1.0648 |
| base_and_dd252_gt_m30               | dd252_gt_m30               |              3 |         158 |     0.1960 |        0.4852 |              1.0000 |     -0.5103 |       0.6613 |
| base_and_dd252_gt_m30               | dd252_gt_m30               |              5 |         134 |     0.1208 |        0.5382 |              1.0000 |     -0.5103 |       0.4940 |
| base_and_dd252_gt_m30               | dd252_gt_m30               |             10 |          74 |     0.3953 |        0.5508 |              1.0000 |     -0.5103 |       1.0506 |
| base_and_dd252_gt_m30               | dd252_gt_m30               |             15 |          14 |     0.4803 |        0.5160 |              1.0000 |     -0.5103 |       1.1127 |
| base_and_rv21_pct_lt_70             | rv21_pct_lt_70             |              3 |         158 |    -0.0309 |        0.2704 |              0.9810 |     -0.4756 |       0.0831 |
| base_and_rv21_pct_lt_70             | rv21_pct_lt_70             |              5 |         134 |     0.0799 |        0.2438 |              1.0000 |     -0.4756 |       0.4253 |
| base_and_rv21_pct_lt_70             | rv21_pct_lt_70             |             10 |          74 |     0.1631 |        0.2562 |              1.0000 |     -0.4756 |       0.6014 |
| base_and_rv21_pct_lt_70             | rv21_pct_lt_70             |             15 |          14 |     0.2230 |        0.2483 |              1.0000 |     -0.4756 |       0.7449 |
| base_and_rv21_pct_lt_50             | rv21_pct_lt_50             |              3 |         158 |    -0.0400 |        0.1604 |              0.9620 |     -0.5084 |      -0.0831 |
| base_and_rv21_pct_lt_50             | rv21_pct_lt_50             |              5 |         134 |    -0.0175 |        0.1629 |              0.9851 |     -0.5084 |       0.0685 |
| base_and_rv21_pct_lt_50             | rv21_pct_lt_50             |             10 |          74 |     0.1084 |        0.1499 |              1.0000 |     -0.5084 |       0.5225 |
| base_and_rv21_pct_lt_50             | rv21_pct_lt_50             |             15 |          14 |     0.1596 |        0.1856 |              1.0000 |     -0.5084 |       0.6574 |
| base_and_qqq_spy_rs_sma50_gt_sma200 | qqq_spy_rs_sma50_gt_sma200 |              3 |         158 |    -0.0855 |        0.2506 |              0.9494 |     -0.5944 |      -0.0329 |
| base_and_qqq_spy_rs_sma50_gt_sma200 | qqq_spy_rs_sma50_gt_sma200 |              5 |         134 |     0.0227 |        0.2508 |              1.0000 |     -0.5944 |       0.2550 |
| base_and_qqq_spy_rs_sma50_gt_sma200 | qqq_spy_rs_sma50_gt_sma200 |             10 |          74 |     0.2117 |        0.3621 |              1.0000 |     -0.5944 |       0.7329 |
| base_and_qqq_spy_rs_sma50_gt_sma200 | qqq_spy_rs_sma50_gt_sma200 |             15 |          14 |     0.2641 |        0.2821 |              1.0000 |     -0.5944 |       0.7971 |

## Method Notes

- Regime gates are simple overlays on the fixed modern vote, not a new broad optimization grid.
- Signals earn returns only after `1 + extra_lag_days` bars to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.
- `economic_pass` requires OOS, FWD, WF, bootstrap and rolling-window coverage. It deliberately ignores PBO/DSR for this exploratory view.
- `mandate_pass` is always false in this runner because deployment still requires PBO and DSR elsewhere `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.
