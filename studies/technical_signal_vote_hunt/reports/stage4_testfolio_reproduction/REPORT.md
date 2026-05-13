# Stage 4 Testfolio Reproduction

Status: long-history reproduction of the Stage 4 close-only base vote.

Window: `1986-01-03` to `2026-04-17` (10,150 bars)
Off leg: `CASHX`
Base rule: `sma100_gt_sma250|roc10_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70`, `k=3`

## Metrics

| label                              |   sortino |   cagr |   sharpe |     mdd |   calmar |    end_mult |   end_rel_to_benchmark |   pct_above_benchmark |
|:-----------------------------------|----------:|-------:|---------:|--------:|---------:|------------:|-----------------------:|----------------------:|
| Stage4 QLD base vote / CASHX       |    0.7310 | 0.1731 |   0.6507 | -0.7345 |   0.2357 |    621.1313 |                 7.7781 |                0.4824 |
| Stage4 TQQQ base vote / CASHX      |    0.6836 | 0.1937 |   0.6087 | -0.8908 |   0.2175 |   1252.4802 |                15.6841 |                0.3363 |
| SPYSIM buy_hold                    |    0.8418 | 0.1149 |   0.6819 | -0.5514 |   0.2083 |     79.8565 |                 1.0000 |                0.0000 |
| QQQSIM/NDX buy_hold                |    0.8660 | 0.1458 |   0.6583 | -0.8297 |   0.1757 |    240.2137 |                 3.0081 |                0.8537 |
| T3d-K2 canonical QLD/ZROZ          |    1.2575 | 0.3106 |   0.9187 | -0.6450 |   0.4816 |  53860.6336 |               674.4681 |                1.0000 |
| iter030 canonical QLD/ZROZ LRS1.20 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 |              3638.4876 |                1.0000 |

## Relative Summary

|                                    |   end_equity |   end_vs_spy |   end_vs_ndx_qqq |   pct_days_above_spy |   pct_days_above_ndx_qqq |
|:-----------------------------------|-------------:|-------------:|-----------------:|---------------------:|-------------------------:|
| Stage4 QLD base vote / CASHX       |     621.1313 |       7.7781 |           2.5857 |               0.4720 |                   0.2592 |
| Stage4 TQQQ base vote / CASHX      |    1252.4802 |      15.6841 |           5.2140 |               0.3296 |                   0.2618 |
| SPYSIM buy_hold                    |      79.8565 |       1.0000 |           0.3324 |               0.0000 |                   0.1581 |
| QQQSIM/NDX buy_hold                |     240.2137 |       3.0081 |           1.0000 |               0.8419 |                   0.0000 |
| T3d-K2 canonical QLD/ZROZ          |   53860.6336 |     674.4681 |         224.2196 |               0.9976 |                   0.9974 |
| iter030 canonical QLD/ZROZ LRS1.20 |  290556.7104 |    3638.4876 |        1209.5757 |               0.9976 |                   0.9974 |

## Rolling Windows

| label                              |   window_years |   n_windows |   min_cagr |   median_cagr |   pct_positive_cagr |
|:-----------------------------------|---------------:|------------:|-----------:|--------------:|--------------------:|
| Stage4 QLD base vote / CASHX       |              3 |         448 |    -0.2774 |        0.1852 |              0.8371 |
| Stage4 QLD base vote / CASHX       |              5 |         424 |    -0.0829 |        0.1492 |              0.9104 |
| Stage4 QLD base vote / CASHX       |             10 |         364 |    -0.0233 |        0.1530 |              0.9808 |
| Stage4 QLD base vote / CASHX       |             15 |         304 |     0.0643 |        0.1348 |              1.0000 |
| Stage4 TQQQ base vote / CASHX      |              3 |         448 |    -0.4340 |        0.2168 |              0.7790 |
| Stage4 TQQQ base vote / CASHX      |              5 |         424 |    -0.1743 |        0.1582 |              0.7948 |
| Stage4 TQQQ base vote / CASHX      |             10 |         364 |    -0.0841 |        0.1497 |              0.9396 |
| Stage4 TQQQ base vote / CASHX      |             15 |         304 |     0.0233 |        0.1163 |              1.0000 |
| SPYSIM buy_hold                    |              3 |         448 |    -0.1449 |        0.1219 |              0.8661 |
| SPYSIM buy_hold                    |              5 |         424 |    -0.0583 |        0.1246 |              0.8750 |
| SPYSIM buy_hold                    |             10 |         364 |    -0.0304 |        0.1090 |              0.9396 |
| SPYSIM buy_hold                    |             15 |         304 |     0.0380 |        0.0955 |              1.0000 |
| QQQSIM/NDX buy_hold                |              3 |         448 |    -0.3767 |        0.1552 |              0.8817 |
| QQQSIM/NDX buy_hold                |              5 |         424 |    -0.1940 |        0.1573 |              0.8774 |
| QQQSIM/NDX buy_hold                |             10 |         364 |    -0.0769 |        0.1427 |              0.9231 |
| QQQSIM/NDX buy_hold                |             15 |         304 |     0.0051 |        0.1304 |              1.0000 |
| T3d-K2 canonical QLD/ZROZ          |              3 |         448 |    -0.0707 |        0.2796 |              0.9866 |
| T3d-K2 canonical QLD/ZROZ          |              5 |         424 |     0.0199 |        0.2824 |              1.0000 |
| T3d-K2 canonical QLD/ZROZ          |             10 |         364 |     0.0633 |        0.3010 |              1.0000 |
| T3d-K2 canonical QLD/ZROZ          |             15 |         304 |     0.1642 |        0.2797 |              1.0000 |
| iter030 canonical QLD/ZROZ LRS1.20 |              3 |         448 |    -0.0710 |        0.3090 |              0.9955 |
| iter030 canonical QLD/ZROZ LRS1.20 |              5 |         424 |     0.0407 |        0.3288 |              1.0000 |
| iter030 canonical QLD/ZROZ LRS1.20 |             10 |         364 |     0.0923 |        0.3507 |              1.0000 |
| iter030 canonical QLD/ZROZ LRS1.20 |             15 |         304 |     0.1823 |        0.3290 |              1.0000 |

## Plots

![Equity curves](plots/equity_curves.png)

![Relative to SPY](plots/relative_to_spy.png)

![Relative to QQQ/NDX](plots/relative_to_ndx_qqq.png)

## Interpretation

The Stage 4 base vote is reproducible on testfolio because it uses only close-derived signals. This test is stricter than the Tiingo 2010+ view because it includes older crash and whipsaw regimes.
