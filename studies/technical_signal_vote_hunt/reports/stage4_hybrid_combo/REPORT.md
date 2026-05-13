# Stage 4 Hybrid Combo

Status: first strategy-of-strategies test combining canonical anchors with Stage 4 turbo legs.

Window: `1986-01-03` to `2026-04-17` (10,150 bars)
Stage4 off-leg: `ZROZSIM`
Meta-gate: use Stage4 turbo when its lagged trailing CAGR exceeds the anchor by a threshold.

## Top Metrics

| label                                   |   sortino |   cagr |   sharpe |     mdd |   calmar |    end_mult |   pct_above_benchmark |
|:----------------------------------------|----------:|-------:|---------:|--------:|---------:|------------:|----------------------:|
| T3d-K2 canonical                        |    1.2575 | 0.3106 |   0.9187 | -0.6450 |   0.4816 |  53860.6336 |                1.0000 |
| hybrid_T3d-K2_Stage4QLD_w756_thr0.20    |    1.2575 | 0.3106 |   0.9187 | -0.6450 |   0.4816 |  53860.6336 |                1.0000 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.20   |    1.2575 | 0.3106 |   0.9187 | -0.6450 |   0.4816 |  53860.6336 |                1.0000 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.10   |    1.2575 | 0.3106 |   0.9187 | -0.6450 |   0.4816 |  53860.6336 |                1.0000 |
| hybrid_T3d-K2_Stage4TQQQ_w1260_thr0.20  |    1.2302 | 0.3062 |   0.9015 | -0.6450 |   0.4748 |  47057.3756 |                1.0000 |
| hybrid_T3d-K2_Stage4QLD_w756_thr0.10    |    1.2291 | 0.3004 |   0.8974 | -0.7047 |   0.4263 |  39324.4666 |                1.0000 |
| iter030 canonical                       |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 |                1.0000 |
| hybrid_iter030_Stage4QLD_w756_thr0.20   |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 |                1.0000 |
| hybrid_iter030_Stage4QLD_w1260_thr0.10  |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 |                1.0000 |
| hybrid_iter030_Stage4QLD_w1260_thr0.20  |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 |                1.0000 |
| hybrid_iter030_Stage4TQQQ_w1260_thr0.20 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 |                1.0000 |
| hybrid_T3d-K2_Stage4TQQQ_w756_thr0.20   |    1.2025 | 0.3039 |   0.8841 | -0.7483 |   0.4061 |  43833.9182 |                1.0000 |
| hybrid_iter030_Stage4QLD_w1260_thr0.05  |    1.2002 | 0.3636 |   0.9570 | -0.5548 |   0.6554 | 265965.1672 |                1.0000 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.00   |    1.1976 | 0.2951 |   0.8856 | -0.6537 |   0.4515 |  33391.1472 |                1.0000 |
| hybrid_iter030_Stage4QLD_w504_thr0.20   |    1.1973 | 0.3618 |   0.9542 | -0.5548 |   0.6522 | 252280.3252 |                1.0000 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.05   |    1.1934 | 0.2946 |   0.8837 | -0.6450 |   0.4567 |  32842.0086 |                1.0000 |
| hybrid_iter030_Stage4QLD_w756_thr0.10   |    1.1891 | 0.3583 |   0.9474 | -0.5548 |   0.6459 | 227403.0150 |                1.0000 |
| hybrid_T3d-K2_Stage4TQQQ_w1260_thr0.10  |    1.1881 | 0.3178 |   0.8972 | -0.7043 |   0.4512 |  67212.3229 |                1.0000 |
| hybrid_T3d-K2_Stage4TQQQ_w1260_thr0.00  |    1.1867 | 0.3357 |   0.9076 | -0.7226 |   0.4645 | 115621.3249 |                1.0000 |
| hybrid_iter030_Stage4TQQQ_w756_thr0.20  |    1.1802 | 0.3562 |   0.9412 | -0.5922 |   0.6014 | 213680.8987 |                1.0000 |

## Top Hybrid Switch Stats

| label                                   | anchor            | turbo       |   window_days |   threshold |   turbo_exposure |   switches |
|:----------------------------------------|:------------------|:------------|--------------:|------------:|-----------------:|-----------:|
| hybrid_iter030_Stage4QLD_w504_thr0.20   | iter030 canonical | Stage4 QLD  |           504 |      0.2000 |           0.0061 |         16 |
| hybrid_iter030_Stage4QLD_w756_thr0.10   | iter030 canonical | Stage4 QLD  |           756 |      0.1000 |           0.0013 |         20 |
| hybrid_iter030_Stage4QLD_w756_thr0.20   | iter030 canonical | Stage4 QLD  |           756 |      0.2000 |           0.0000 |          0 |
| hybrid_iter030_Stage4QLD_w1260_thr0.05  | iter030 canonical | Stage4 QLD  |          1260 |      0.0500 |           0.0004 |          4 |
| hybrid_iter030_Stage4QLD_w1260_thr0.10  | iter030 canonical | Stage4 QLD  |          1260 |      0.1000 |           0.0000 |          0 |
| hybrid_iter030_Stage4QLD_w1260_thr0.20  | iter030 canonical | Stage4 QLD  |          1260 |      0.2000 |           0.0000 |          0 |
| hybrid_iter030_Stage4TQQQ_w756_thr0.20  | iter030 canonical | Stage4 TQQQ |           756 |      0.2000 |           0.0039 |         20 |
| hybrid_iter030_Stage4TQQQ_w1260_thr0.20 | iter030 canonical | Stage4 TQQQ |          1260 |      0.2000 |           0.0000 |          0 |
| hybrid_T3d-K2_Stage4QLD_w756_thr0.10    | T3d-K2 canonical  | Stage4 QLD  |           756 |      0.1000 |           0.0094 |         44 |
| hybrid_T3d-K2_Stage4QLD_w756_thr0.20    | T3d-K2 canonical  | Stage4 QLD  |           756 |      0.2000 |           0.0001 |          2 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.00   | T3d-K2 canonical  | Stage4 QLD  |          1260 |      0.0000 |           0.0570 |         61 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.05   | T3d-K2 canonical  | Stage4 QLD  |          1260 |      0.0500 |           0.0148 |         39 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.10   | T3d-K2 canonical  | Stage4 QLD  |          1260 |      0.1000 |           0.0040 |          2 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.20   | T3d-K2 canonical  | Stage4 QLD  |          1260 |      0.2000 |           0.0000 |          0 |
| hybrid_T3d-K2_Stage4TQQQ_w756_thr0.20   | T3d-K2 canonical  | Stage4 TQQQ |           756 |      0.2000 |           0.0289 |         88 |
| hybrid_T3d-K2_Stage4TQQQ_w1260_thr0.00  | T3d-K2 canonical  | Stage4 TQQQ |          1260 |      0.0000 |           0.0871 |         73 |
| hybrid_T3d-K2_Stage4TQQQ_w1260_thr0.10  | T3d-K2 canonical  | Stage4 TQQQ |          1260 |      0.1000 |           0.0468 |         51 |
| hybrid_T3d-K2_Stage4TQQQ_w1260_thr0.20  | T3d-K2 canonical  | Stage4 TQQQ |          1260 |      0.2000 |           0.0121 |         42 |

## Rolling Windows: Top 20

| label                                   |   window_years |   n_windows |   min_cagr |   median_cagr |   pct_positive_cagr |
|:----------------------------------------|---------------:|------------:|-----------:|--------------:|--------------------:|
| T3d-K2 canonical                        |              3 |         448 |    -0.0872 |        0.2823 |              0.9799 |
| T3d-K2 canonical                        |              5 |         424 |     0.0081 |        0.2851 |              1.0000 |
| T3d-K2 canonical                        |             10 |         364 |     0.0642 |        0.3012 |              1.0000 |
| T3d-K2 canonical                        |             15 |         304 |     0.1597 |        0.2809 |              1.0000 |
| hybrid_T3d-K2_Stage4QLD_w756_thr0.20    |              3 |         448 |    -0.0872 |        0.2823 |              0.9799 |
| hybrid_T3d-K2_Stage4QLD_w756_thr0.20    |              5 |         424 |     0.0081 |        0.2851 |              1.0000 |
| hybrid_T3d-K2_Stage4QLD_w756_thr0.20    |             10 |         364 |     0.0642 |        0.3012 |              1.0000 |
| hybrid_T3d-K2_Stage4QLD_w756_thr0.20    |             15 |         304 |     0.1597 |        0.2809 |              1.0000 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.20   |              3 |         448 |    -0.0872 |        0.2823 |              0.9799 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.20   |              5 |         424 |     0.0081 |        0.2851 |              1.0000 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.20   |             10 |         364 |     0.0642 |        0.3012 |              1.0000 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.20   |             15 |         304 |     0.1597 |        0.2809 |              1.0000 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.10   |              3 |         448 |    -0.0872 |        0.2823 |              0.9799 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.10   |              5 |         424 |     0.0081 |        0.2851 |              1.0000 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.10   |             10 |         364 |     0.0642 |        0.3012 |              1.0000 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.10   |             15 |         304 |     0.1597 |        0.2809 |              1.0000 |
| hybrid_T3d-K2_Stage4TQQQ_w1260_thr0.20  |              3 |         448 |    -0.0872 |        0.2694 |              0.9799 |
| hybrid_T3d-K2_Stage4TQQQ_w1260_thr0.20  |              5 |         424 |     0.0081 |        0.2809 |              1.0000 |
| hybrid_T3d-K2_Stage4TQQQ_w1260_thr0.20  |             10 |         364 |     0.0642 |        0.2891 |              1.0000 |
| hybrid_T3d-K2_Stage4TQQQ_w1260_thr0.20  |             15 |         304 |     0.1597 |        0.2741 |              1.0000 |
| hybrid_T3d-K2_Stage4QLD_w756_thr0.10    |              3 |         448 |    -0.0872 |        0.2802 |              0.9554 |
| hybrid_T3d-K2_Stage4QLD_w756_thr0.10    |              5 |         424 |    -0.0039 |        0.2848 |              0.9976 |
| hybrid_T3d-K2_Stage4QLD_w756_thr0.10    |             10 |         364 |     0.0527 |        0.2991 |              1.0000 |
| hybrid_T3d-K2_Stage4QLD_w756_thr0.10    |             15 |         304 |     0.1513 |        0.2691 |              1.0000 |
| iter030 canonical                       |              3 |         448 |    -0.0821 |        0.3127 |              0.9955 |
| iter030 canonical                       |              5 |         424 |     0.0299 |        0.3294 |              1.0000 |
| iter030 canonical                       |             10 |         364 |     0.0965 |        0.3520 |              1.0000 |
| iter030 canonical                       |             15 |         304 |     0.1782 |        0.3293 |              1.0000 |
| hybrid_iter030_Stage4QLD_w756_thr0.20   |              3 |         448 |    -0.0821 |        0.3127 |              0.9955 |
| hybrid_iter030_Stage4QLD_w756_thr0.20   |              5 |         424 |     0.0299 |        0.3294 |              1.0000 |
| hybrid_iter030_Stage4QLD_w756_thr0.20   |             10 |         364 |     0.0965 |        0.3520 |              1.0000 |
| hybrid_iter030_Stage4QLD_w756_thr0.20   |             15 |         304 |     0.1782 |        0.3293 |              1.0000 |
| hybrid_iter030_Stage4QLD_w1260_thr0.10  |              3 |         448 |    -0.0821 |        0.3127 |              0.9955 |
| hybrid_iter030_Stage4QLD_w1260_thr0.10  |              5 |         424 |     0.0299 |        0.3294 |              1.0000 |
| hybrid_iter030_Stage4QLD_w1260_thr0.10  |             10 |         364 |     0.0965 |        0.3520 |              1.0000 |
| hybrid_iter030_Stage4QLD_w1260_thr0.10  |             15 |         304 |     0.1782 |        0.3293 |              1.0000 |
| hybrid_iter030_Stage4QLD_w1260_thr0.20  |              3 |         448 |    -0.0821 |        0.3127 |              0.9955 |
| hybrid_iter030_Stage4QLD_w1260_thr0.20  |              5 |         424 |     0.0299 |        0.3294 |              1.0000 |
| hybrid_iter030_Stage4QLD_w1260_thr0.20  |             10 |         364 |     0.0965 |        0.3520 |              1.0000 |
| hybrid_iter030_Stage4QLD_w1260_thr0.20  |             15 |         304 |     0.1782 |        0.3293 |              1.0000 |
| hybrid_iter030_Stage4TQQQ_w1260_thr0.20 |              3 |         448 |    -0.0821 |        0.3127 |              0.9955 |
| hybrid_iter030_Stage4TQQQ_w1260_thr0.20 |              5 |         424 |     0.0299 |        0.3294 |              1.0000 |
| hybrid_iter030_Stage4TQQQ_w1260_thr0.20 |             10 |         364 |     0.0965 |        0.3520 |              1.0000 |
| hybrid_iter030_Stage4TQQQ_w1260_thr0.20 |             15 |         304 |     0.1782 |        0.3293 |              1.0000 |
| hybrid_T3d-K2_Stage4TQQQ_w756_thr0.20   |              3 |         448 |    -0.1118 |        0.2827 |              0.9531 |
| hybrid_T3d-K2_Stage4TQQQ_w756_thr0.20   |              5 |         424 |    -0.0425 |        0.2890 |              0.9882 |
| hybrid_T3d-K2_Stage4TQQQ_w756_thr0.20   |             10 |         364 |     0.0571 |        0.3074 |              1.0000 |
| hybrid_T3d-K2_Stage4TQQQ_w756_thr0.20   |             15 |         304 |     0.1627 |        0.2752 |              1.0000 |
| hybrid_iter030_Stage4QLD_w1260_thr0.05  |              3 |         448 |    -0.0821 |        0.3051 |              0.9955 |
| hybrid_iter030_Stage4QLD_w1260_thr0.05  |              5 |         424 |     0.0299 |        0.3269 |              1.0000 |
| hybrid_iter030_Stage4QLD_w1260_thr0.05  |             10 |         364 |     0.0965 |        0.3440 |              1.0000 |
| hybrid_iter030_Stage4QLD_w1260_thr0.05  |             15 |         304 |     0.1782 |        0.3235 |              1.0000 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.00   |              3 |         448 |    -0.0954 |        0.2485 |              0.9330 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.00   |              5 |         424 |    -0.0572 |        0.2508 |              0.9811 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.00   |             10 |         364 |     0.0442 |        0.2539 |              1.0000 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.00   |             15 |         304 |     0.1293 |        0.2464 |              1.0000 |
| hybrid_iter030_Stage4QLD_w504_thr0.20   |              3 |         448 |    -0.0821 |        0.3056 |              0.9955 |
| hybrid_iter030_Stage4QLD_w504_thr0.20   |              5 |         424 |     0.0214 |        0.3278 |              1.0000 |
| hybrid_iter030_Stage4QLD_w504_thr0.20   |             10 |         364 |     0.0919 |        0.3422 |              1.0000 |
| hybrid_iter030_Stage4QLD_w504_thr0.20   |             15 |         304 |     0.1750 |        0.3218 |              1.0000 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.05   |              3 |         448 |    -0.1331 |        0.2636 |              0.9621 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.05   |              5 |         424 |    -0.0461 |        0.2783 |              0.9882 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.05   |             10 |         364 |     0.0606 |        0.2865 |              1.0000 |
| hybrid_T3d-K2_Stage4QLD_w1260_thr0.05   |             15 |         304 |     0.1551 |        0.2493 |              1.0000 |
| hybrid_iter030_Stage4QLD_w756_thr0.10   |              3 |         448 |    -0.0821 |        0.3005 |              0.9955 |
| hybrid_iter030_Stage4QLD_w756_thr0.10   |              5 |         424 |     0.0278 |        0.3198 |              1.0000 |
| hybrid_iter030_Stage4QLD_w756_thr0.10   |             10 |         364 |     0.0881 |        0.3387 |              1.0000 |
| hybrid_iter030_Stage4QLD_w756_thr0.10   |             15 |         304 |     0.1673 |        0.3158 |              1.0000 |
| hybrid_T3d-K2_Stage4TQQQ_w1260_thr0.10  |              3 |         448 |    -0.0941 |        0.2741 |              0.9754 |
| hybrid_T3d-K2_Stage4TQQQ_w1260_thr0.10  |              5 |         424 |    -0.0561 |        0.2814 |              0.9882 |
| hybrid_T3d-K2_Stage4TQQQ_w1260_thr0.10  |             10 |         364 |     0.0642 |        0.2932 |              1.0000 |
| hybrid_T3d-K2_Stage4TQQQ_w1260_thr0.10  |             15 |         304 |     0.1597 |        0.2739 |              1.0000 |
| hybrid_T3d-K2_Stage4TQQQ_w1260_thr0.00  |              3 |         448 |    -0.1137 |        0.3030 |              0.9330 |
| hybrid_T3d-K2_Stage4TQQQ_w1260_thr0.00  |              5 |         424 |    -0.0210 |        0.3083 |              0.9882 |
| hybrid_T3d-K2_Stage4TQQQ_w1260_thr0.00  |             10 |         364 |     0.0378 |        0.3342 |              1.0000 |
| hybrid_T3d-K2_Stage4TQQQ_w1260_thr0.00  |             15 |         304 |     0.1399 |        0.2819 |              1.0000 |
| hybrid_iter030_Stage4TQQQ_w756_thr0.20  |              3 |         448 |    -0.0821 |        0.3041 |              0.9955 |
| hybrid_iter030_Stage4TQQQ_w756_thr0.20  |              5 |         424 |     0.0238 |        0.3072 |              1.0000 |
| hybrid_iter030_Stage4TQQQ_w756_thr0.20  |             10 |         364 |     0.0932 |        0.3340 |              1.0000 |
| hybrid_iter030_Stage4TQQQ_w756_thr0.20  |             15 |         304 |     0.1733 |        0.3079 |              1.0000 |

## Plot

![Top hybrid equity curves](plots/equity_curves.png)

## Method Notes

- The meta-gate is lagged one day after trailing-CAGR computation; it does not know future regimes `[advances_fin_ml, p.31-34]`.
- This is economic-first exploration, not a mandate pass.
