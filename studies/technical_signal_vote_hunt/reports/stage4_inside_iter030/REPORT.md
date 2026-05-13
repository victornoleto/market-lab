# Stage4 Turbo Inside Iter030

Status: test of Stage4 as the QLD->TQQQ upgrade gate inside iter030's defensive shell.

Window: `1986-01-03` to `2026-04-17` (10,150 bars)
Stage4 rule: `sma100_gt_sma250|roc10_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70`, `k=3`

## Metrics

| label                            |   sortino |   cagr |   sharpe |     mdd |   calmar |    end_mult |   pct_above_benchmark |
|:---------------------------------|----------:|-------:|---------:|--------:|---------:|------------:|----------------------:|
| iter030 canonical replica        |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 |                1.0000 |
| inside_rearm_and_stage4          |    1.1911 | 0.3542 |   0.9508 | -0.5548 |   0.6385 | 201407.0254 |                1.0000 |
| inside_rearm_or_stage4           |    1.0838 | 0.3846 |   0.8721 | -0.6454 |   0.5959 | 492025.4559 |                1.0000 |
| inside_rearm_then_stage4_confirm |    1.0838 | 0.3846 |   0.8721 | -0.6454 |   0.5959 | 492025.4559 |                1.0000 |
| inside_stage4_only               |    1.0636 | 0.3720 |   0.8589 | -0.6312 |   0.5894 | 341060.3851 |                1.0000 |
| QQQSIM buy_hold                  |    0.8660 | 0.1458 |   0.6583 | -0.8297 |   0.1757 |    240.2137 |                0.8537 |
| SPYSIM buy_hold                  |    0.8418 | 0.1149 |   0.6819 | -0.5514 |   0.2083 |     79.8565 |                0.0000 |

## Upgrade Stats

| label                            |   upgrade_active_pct |   on_active_pct |   switches |
|:---------------------------------|---------------------:|----------------:|-----------:|
| iter030 canonical replica        |               0.0691 |          0.7258 |         36 |
| inside_stage4_only               |               0.6324 |          0.7258 |        717 |
| inside_rearm_or_stage4           |               0.6570 |          0.7258 |        587 |
| inside_rearm_and_stage4          |               0.0444 |          0.7258 |        164 |
| inside_rearm_then_stage4_confirm |               0.6570 |          0.7258 |        531 |

## Rolling Windows

| label                            |   window_years |   n_windows |   min_cagr |   median_cagr |   pct_positive_cagr |
|:---------------------------------|---------------:|------------:|-----------:|--------------:|--------------------:|
| iter030 canonical replica        |              3 |         448 |    -0.0821 |        0.3127 |              0.9955 |
| iter030 canonical replica        |              5 |         424 |     0.0299 |        0.3294 |              1.0000 |
| iter030 canonical replica        |             10 |         364 |     0.0965 |        0.3520 |              1.0000 |
| iter030 canonical replica        |             15 |         304 |     0.1782 |        0.3293 |              1.0000 |
| inside_rearm_and_stage4          |              3 |         448 |    -0.0946 |        0.3042 |              0.9933 |
| inside_rearm_and_stage4          |              5 |         424 |     0.0126 |        0.3247 |              1.0000 |
| inside_rearm_and_stage4          |             10 |         364 |     0.0725 |        0.3517 |              1.0000 |
| inside_rearm_and_stage4          |             15 |         304 |     0.1573 |        0.3111 |              1.0000 |
| inside_rearm_or_stage4           |              3 |         448 |    -0.1018 |        0.3433 |              0.9621 |
| inside_rearm_or_stage4           |              5 |         424 |    -0.0310 |        0.3625 |              0.9976 |
| inside_rearm_or_stage4           |             10 |         364 |     0.0709 |        0.4056 |              1.0000 |
| inside_rearm_or_stage4           |             15 |         304 |     0.1975 |        0.3462 |              1.0000 |
| inside_rearm_then_stage4_confirm |              3 |         448 |    -0.1018 |        0.3433 |              0.9621 |
| inside_rearm_then_stage4_confirm |              5 |         424 |    -0.0310 |        0.3625 |              0.9976 |
| inside_rearm_then_stage4_confirm |             10 |         364 |     0.0709 |        0.4056 |              1.0000 |
| inside_rearm_then_stage4_confirm |             15 |         304 |     0.1975 |        0.3462 |              1.0000 |
| inside_stage4_only               |              3 |         448 |    -0.1141 |        0.3350 |              0.9509 |
| inside_stage4_only               |              5 |         424 |    -0.0610 |        0.3537 |              0.9858 |
| inside_stage4_only               |             10 |         364 |     0.0475 |        0.3943 |              1.0000 |
| inside_stage4_only               |             15 |         304 |     0.1762 |        0.3258 |              1.0000 |
| QQQSIM buy_hold                  |              3 |         448 |    -0.3800 |        0.1558 |              0.8839 |
| QQQSIM buy_hold                  |              5 |         424 |    -0.1986 |        0.1579 |              0.8774 |
| QQQSIM buy_hold                  |             10 |         364 |    -0.0775 |        0.1432 |              0.9231 |
| QQQSIM buy_hold                  |             15 |         304 |     0.0032 |        0.1306 |              1.0000 |
| SPYSIM buy_hold                  |              3 |         448 |    -0.1464 |        0.1241 |              0.8638 |
| SPYSIM buy_hold                  |              5 |         424 |    -0.0575 |        0.1263 |              0.8797 |
| SPYSIM buy_hold                  |             10 |         364 |    -0.0299 |        0.1092 |              0.9423 |
| SPYSIM buy_hold                  |             15 |         304 |     0.0373 |        0.0955 |              1.0000 |

## Plot

![Equity curves](plots/equity_curves.png)

## Method Notes

- Iter030's ON/OFF, LRS1.20, rearm plumbing and rate-vol CASHX off override are preserved.
- Variants only change the ON-leg upgrade gate that selects QLD versus TQQQ.
- This is economic-first exploration, not a mandate pass.
