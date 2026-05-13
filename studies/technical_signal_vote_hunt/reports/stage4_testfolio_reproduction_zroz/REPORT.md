# Stage 4 Testfolio Reproduction

Status: long-history reproduction of the Stage 4 close-only base vote.

Window: `1986-01-03` to `2026-04-17` (10,150 bars)
Off leg: `ZROZSIM`
Base rule: `sma100_gt_sma250|roc10_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70`, `k=3`

## Metrics

| label                              |   sortino |   cagr |   sharpe |     mdd |   calmar |    end_mult |   end_rel_to_benchmark |   pct_above_benchmark |
|:-----------------------------------|----------:|-------:|---------:|--------:|---------:|------------:|-----------------------:|----------------------:|
| Stage4 QLD base vote / ZROZSIM     |    0.9074 | 0.1938 |   0.6685 | -0.7007 |   0.2766 |   1255.5564 |                15.7227 |                0.9544 |
| Stage4 TQQQ base vote / ZROZSIM    |    0.8328 | 0.2148 |   0.6374 | -0.8769 |   0.2449 |   2531.7669 |                31.7040 |                0.8215 |
| SPYSIM buy_hold                    |    0.8418 | 0.1149 |   0.6819 | -0.5514 |   0.2083 |     79.8565 |                 1.0000 |                0.0000 |
| QQQSIM/NDX buy_hold                |    0.8660 | 0.1458 |   0.6583 | -0.8297 |   0.1757 |    240.2137 |                 3.0081 |                0.8537 |
| T3d-K2 canonical QLD/ZROZ          |    1.2575 | 0.3106 |   0.9187 | -0.6450 |   0.4816 |  53860.6336 |               674.4681 |                1.0000 |
| iter030 canonical QLD/ZROZ LRS1.20 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 |              3638.4876 |                1.0000 |

## Relative Summary

|                                    |   end_equity |   end_vs_spy |   end_vs_ndx_qqq |   pct_days_above_spy |   pct_days_above_ndx_qqq |
|:-----------------------------------|-------------:|-------------:|-----------------:|---------------------:|-------------------------:|
| Stage4 QLD base vote / ZROZSIM     |    1255.5564 |      15.7227 |           5.2268 |               0.9532 |                   0.8435 |
| Stage4 TQQQ base vote / ZROZSIM    |    2531.7669 |      31.7040 |          10.5396 |               0.8235 |                   0.6470 |
| SPYSIM buy_hold                    |      79.8565 |       1.0000 |           0.3324 |               0.0000 |                   0.1581 |
| QQQSIM/NDX buy_hold                |     240.2137 |       3.0081 |           1.0000 |               0.8419 |                   0.0000 |
| T3d-K2 canonical QLD/ZROZ          |   53860.6336 |     674.4681 |         224.2196 |               0.9976 |                   0.9974 |
| iter030 canonical QLD/ZROZ LRS1.20 |  290556.7104 |    3638.4876 |        1209.5757 |               0.9976 |                   0.9974 |

## Rolling Windows

| label                              |   window_years |   n_windows |   min_cagr |   median_cagr |   pct_positive_cagr |
|:-----------------------------------|---------------:|------------:|-----------:|--------------:|--------------------:|
| Stage4 QLD base vote / ZROZSIM     |              3 |         448 |    -0.2005 |        0.1787 |              0.8371 |
| Stage4 QLD base vote / ZROZSIM     |              5 |         424 |    -0.0723 |        0.1757 |              0.9292 |
| Stage4 QLD base vote / ZROZSIM     |             10 |         364 |    -0.0111 |        0.1736 |              0.9973 |
| Stage4 QLD base vote / ZROZSIM     |             15 |         304 |     0.0784 |        0.1551 |              1.0000 |
| Stage4 TQQQ base vote / ZROZSIM    |              3 |         448 |    -0.3737 |        0.2184 |              0.7835 |
| Stage4 TQQQ base vote / ZROZSIM    |              5 |         424 |    -0.1435 |        0.1699 |              0.8420 |
| Stage4 TQQQ base vote / ZROZSIM    |             10 |         364 |    -0.0710 |        0.1701 |              0.9478 |
| Stage4 TQQQ base vote / ZROZSIM    |             15 |         304 |     0.0521 |        0.1411 |              1.0000 |
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
