# Stage 2 Tiingo OHLC Grid Results

Status: capped exact-grid discovery. This is not a validation verdict.

Branch: `QQQ`
Risk-ons: `TQQQ_3x`
Off leg: `CASH_USD`
Extra execution lag days: `1`
Redundant signals allowed: `False`
Signal subset range: n=1..5
Estimated/configs tested: 7,067,694 / 7,067,694
Windows: TQQQ_3x: 2010-02-12..2026-04-14 (4,066 bars)
Elapsed seconds: 1262.5

## Top Configs

| branch   | risk_on   |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                      |
|:---------|:----------|----:|----:|----------:|-------:|---------:|--------:|---------:|:-----------------------------------------------------------------------------|
| QQQ      | TQQQ_3x   |   5 |   3 |    1.4124 | 0.5300 |   1.1849 | -0.5103 |   1.0386 | sma100_gt_sma250|roc10_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70      |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.4042 | 0.5243 |   1.1809 | -0.5472 |   0.9581 | sma100_gt_sma250|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70|cci20_gt_0      |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3981 | 0.5229 |   1.1770 | -0.4823 |   1.0841 | px_gt_sma20|sma100_gt_sma250|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70     |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3968 | 0.5249 |   1.0880 | -0.5528 |   0.9496 | px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|cci20_gt_100             |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3928 | 0.5160 |   1.1751 | -0.4248 |   1.2145 | px_gt_ema20|sma100_gt_sma250|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70     |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3837 | 0.5172 |   1.0780 | -0.5654 |   0.9148 | px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|cci20_gt_100             |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3819 | 0.5156 |   1.0758 | -0.5653 |   0.9121 | px_gt_sma50|px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0              |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3711 | 0.5099 |   1.0687 | -0.5653 |   0.9020 | px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|close_gt_prior_high20    |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3711 | 0.5099 |   1.0687 | -0.5653 |   0.9020 | px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|close_gt_prior_high55    |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3711 | 0.5099 |   1.0687 | -0.5653 |   0.9020 | px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|atr14_pct_lt_5           |
| QQQ      | TQQQ_3x   |   4 |   1 |    1.3711 | 0.5099 |   1.0687 | -0.5653 |   0.9020 | px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0                          |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3652 | 0.5076 |   1.0677 | -0.5190 |   0.9780 | px_gt_sma50|px_gt_ema100|rv21_lt_40|rv21_pct_lt_70|ar1_30_gt_0               |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3650 | 0.5066 |   1.0660 | -0.5190 |   0.9760 | px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|close_gt_prior_high20    |
| QQQ      | TQQQ_3x   |   4 |   1 |    1.3650 | 0.5066 |   1.0660 | -0.5190 |   0.9760 | px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0                          |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3650 | 0.5066 |   1.0660 | -0.5190 |   0.9760 | px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|close_gt_prior_high55    |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3650 | 0.5066 |   1.0660 | -0.5190 |   0.9760 | px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|atr14_pct_lt_5           |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3606 | 0.5042 |   1.0564 | -0.5916 |   0.8522 | px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|stoch14_gt_80            |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3556 | 0.5021 |   1.0742 | -0.6527 |   0.7693 | px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80              |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3546 | 0.4893 |   1.1341 | -0.5212 |   0.9387 | px_gt_sma150|sma100_gt_sma250|roc10_gt_0|stochrsi14_gt_50|rv21_pct_lt_70     |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3536 | 0.4891 |   1.1362 | -0.4921 |   0.9939 | px_gt_sma20|px_gt_sma150|sma100_gt_sma250|stochrsi14_gt_50|rv21_pct_lt_70    |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3527 | 0.5162 |   1.0963 | -0.5108 |   1.0105 | sma50_gt_sma200|roc20_gt_0|roc120_gt_0|rv21_lt_40|ar1_30_gt_0                |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3499 | 0.4985 |   1.0494 | -0.5916 |   0.8427 | px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|stoch14_gt_80            |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3471 | 0.5008 |   1.0421 | -0.6244 |   0.8021 | px_gt_sma20|px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0              |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3457 | 0.4962 |   1.0717 | -0.6645 |   0.7467 | roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100|bear_power_gt_0           |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3448 | 0.5037 |   1.0628 | -0.5993 |   0.8406 | px_gt_ema100|roc20_gt_0|rv21_pct_lt_70|ar1_30_gt_0|adx14_gt_20               |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3441 | 0.4997 |   1.0408 | -0.6290 |   0.7944 | px_gt_sma20|px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0              |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3440 | 0.4949 |   1.0687 | -0.6746 |   0.7336 | roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80|bear_power_gt_0          |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3439 | 0.4953 |   1.0515 | -0.5190 |   0.9543 | px_gt_ema50|px_gt_ema100|rv21_lt_40|rv21_pct_lt_70|ar1_30_gt_0               |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3437 | 0.4950 |   1.0701 | -0.6686 |   0.7404 | roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55|bear_power_gt_0  |
| QQQ      | TQQQ_3x   |   4 |   2 |    1.3437 | 0.4950 |   1.0701 | -0.6686 |   0.7404 | roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0                        |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3437 | 0.4950 |   1.0701 | -0.6686 |   0.7404 | roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20|bear_power_gt_0  |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3422 | 0.4985 |   1.0393 | -0.6618 |   0.7532 | px_gt_sma20|px_gt_ema20|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0              |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3412 | 0.4935 |   1.0688 | -0.6686 |   0.7382 | roc20_gt_0|roc120_gt_0|rv21_lt_40|atr14_pct_lt_3|bear_power_gt_0             |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3411 | 0.4921 |   1.0639 | -0.6752 |   0.7289 | px_gt_ema20|roc20_gt_0|roc120_gt_0|rv21_lt_40|atr14_pct_lt_3                 |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3403 | 0.4936 |   1.0621 | -0.6791 |   0.7268 | px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0            |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3397 | 0.4953 |   1.0424 | -0.5763 |   0.8593 | px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|bear_power_gt_0          |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3392 | 0.4922 |   1.1378 | -0.4718 |   1.0433 | sma100_gt_sma250|roc20_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70      |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3378 | 0.5013 |   1.0472 | -0.5974 |   0.8390 | px_gt_sma50|px_gt_ema50|roc120_gt_0|rv21_lt_40|ar1_30_gt_0                   |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3375 | 0.4945 |   1.0640 | -0.5439 |   0.9092 | px_gt_sma10|px_gt_ema100|sma50_gt_sma150|rv21_pct_lt_70|ar1_30_gt_0          |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3374 | 0.5212 |   1.0668 | -0.6283 |   0.8296 | px_gt_sma20|sma50_gt_sma200|roc20_gt_0|roc120_gt_0|ar1_30_gt_0               |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3366 | 0.5278 |   1.0451 | -0.6573 |   0.8029 | px_gt_ema5|px_gt_ema10|px_gt_sma20|roc120_gt_0|ar1_30_gt_0                   |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3366 | 0.5278 |   1.0451 | -0.6573 |   0.8029 | px_gt_ema5|px_gt_sma20|roc120_gt_0|ar1_30_gt_0|cci20_gt_100                  |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3366 | 0.5278 |   1.0451 | -0.6573 |   0.8029 | px_gt_ema5|px_gt_sma20|roc120_gt_0|ar1_30_gt_0|bear_power_gt_0               |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3366 | 0.5278 |   1.0451 | -0.6573 |   0.8029 | px_gt_ema5|px_gt_sma20|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high55         |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3366 | 0.5278 |   1.0451 | -0.6573 |   0.8029 | px_gt_ema5|px_gt_sma20|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high20         |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3366 | 0.5278 |   1.0451 | -0.6573 |   0.8029 | px_gt_ema5|px_gt_sma20|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80                 |
| QQQ      | TQQQ_3x   |   4 |   1 |    1.3366 | 0.5278 |   1.0451 | -0.6573 |   0.8029 | px_gt_ema5|px_gt_sma20|roc120_gt_0|ar1_30_gt_0                               |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3363 | 0.5177 |   1.0659 | -0.6402 |   0.8086 | px_gt_sma20|sma50_gt_sma150|roc20_gt_0|roc120_gt_0|ar1_30_gt_0               |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3353 | 0.4928 |   1.0685 | -0.6349 |   0.7762 | px_gt_ema20|px_gt_ema50|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80             |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3348 | 0.4922 |   1.0677 | -0.6327 |   0.7778 | px_gt_ema20|px_gt_ema50|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0           |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3341 | 0.4833 |   1.1210 | -0.4375 |   1.1047 | px_gt_ema150|sma100_gt_sma250|macd_hist_gt_0|roc10_gt_0|rv21_pct_lt_70       |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3341 | 0.5074 |   1.0428 | -0.7262 |   0.6987 | px_gt_sma20|roc120_gt_0|rv21_lt_40|ar1_30_gt_0|cci20_gt_0                    |
| QQQ      | TQQQ_3x   |   4 |   1 |    1.3338 | 0.5198 |   1.0496 | -0.6830 |   0.7610 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|bear_power_gt_0                          |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3338 | 0.5198 |   1.0496 | -0.6830 |   0.7610 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high20|bear_power_gt_0    |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3338 | 0.5198 |   1.0496 | -0.6830 |   0.7610 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high55|bear_power_gt_0    |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3338 | 0.5198 |   1.0496 | -0.6830 |   0.7610 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80|bear_power_gt_0            |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3338 | 0.5198 |   1.0496 | -0.6830 |   0.7610 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|cci20_gt_100|bear_power_gt_0             |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3335 | 0.5254 |   1.0422 | -0.6573 |   0.7993 | px_gt_ema5|px_gt_sma20|px_gt_ema20|roc120_gt_0|ar1_30_gt_0                   |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3334 | 0.4864 |   1.0558 | -0.6686 |   0.7275 | px_gt_ema50|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0            |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3331 | 0.5182 |   1.0242 | -0.6497 |   0.7976 | sma100_gt_sma250|roc10_gt_0|rsi14_gt_50|rv21_lt_40|ar1_30_gt_0               |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3328 | 0.5036 |   1.0353 | -0.7385 |   0.6819 | px_gt_sma10|px_gt_sma20|roc120_gt_0|rv21_lt_40|ar1_30_gt_0                   |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3326 | 0.5332 |   1.0603 | -0.5649 |   0.9439 | px_gt_ema250|sma100_gt_sma250|rsi14_rising|ar1_30_gt_0|cci20_gt_100          |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3320 | 0.4834 |   1.0546 | -0.6203 |   0.7792 | px_gt_ema50|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100               |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3319 | 0.5249 |   1.0421 | -0.6363 |   0.8249 | px_gt_ema5|px_gt_ema10|px_gt_ema20|roc120_gt_0|ar1_30_gt_0                   |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3307 | 0.4976 |   1.0426 | -0.5974 |   0.8329 | px_gt_sma50|roc120_gt_0|rv21_lt_40|ar1_30_gt_0|cci20_gt_100                  |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3307 | 0.5031 |   1.0423 | -0.6830 |   0.7366 | px_gt_sma20|roc120_gt_0|rv21_lt_40|ar1_30_gt_0|bear_power_gt_0               |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3304 | 0.4891 |   1.0548 | -0.6988 |   0.6999 | px_gt_sma20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0            |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3303 | 0.4949 |   1.0706 | -0.6904 |   0.7168 | px_gt_sma10|sma100_gt_sma250|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3           |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3299 | 0.5163 |   1.0448 | -0.6836 |   0.7552 | px_gt_sma20|px_gt_ema20|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high20        |
| QQQ      | TQQQ_3x   |   4 |   1 |    1.3299 | 0.5163 |   1.0448 | -0.6836 |   0.7552 | px_gt_sma20|px_gt_ema20|roc120_gt_0|ar1_30_gt_0                              |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3299 | 0.5163 |   1.0448 | -0.6836 |   0.7552 | px_gt_sma20|px_gt_ema20|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high55        |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3299 | 0.5163 |   1.0448 | -0.6836 |   0.7552 | px_gt_sma20|px_gt_ema20|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80                |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3299 | 0.5163 |   1.0448 | -0.6836 |   0.7552 | px_gt_sma20|px_gt_ema20|roc120_gt_0|ar1_30_gt_0|cci20_gt_100                 |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3296 | 0.5160 |   1.0445 | -0.6836 |   0.7548 | px_gt_sma20|px_gt_ema20|roc120_gt_0|ar1_30_gt_0|bear_power_gt_0              |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3293 | 0.4909 |   1.0297 | -0.6625 |   0.7410 | px_gt_sma20|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|close_gt_prior_high55    |
| QQQ      | TQQQ_3x   |   4 |   1 |    1.3293 | 0.4909 |   1.0297 | -0.6625 |   0.7410 | px_gt_sma20|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0                          |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3293 | 0.4909 |   1.0297 | -0.6625 |   0.7410 | px_gt_sma20|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|close_gt_prior_high20    |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3293 | 0.4909 |   1.0297 | -0.6625 |   0.7410 | px_gt_sma20|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|cci20_gt_100             |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3293 | 0.4909 |   1.0297 | -0.6625 |   0.7410 | px_gt_sma20|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|stoch14_gt_80            |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3292 | 0.4908 |   1.0296 | -0.6618 |   0.7416 | px_gt_sma20|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|bear_power_gt_0          |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3291 | 0.4896 |   1.0354 | -0.5763 |   0.8496 | px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|bear_power_gt_0          |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3283 | 0.4971 |   1.0213 | -0.6450 |   0.7708 | px_gt_ema5|px_gt_sma20|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0               |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3282 | 0.5042 |   1.0357 | -0.7696 |   0.6551 | px_gt_sma10|roc10_gt_0|roc120_gt_0|rv21_lt_40|ar1_30_gt_0                    |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3275 | 0.4870 |   1.0546 | -0.6711 |   0.7257 | px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100               |
| QQQ      | TQQQ_3x   |   4 |   1 |    1.3274 | 0.4874 |   1.0418 | -0.5528 |   0.8817 | px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|cci20_gt_100                         |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3274 | 0.4874 |   1.0418 | -0.5528 |   0.8817 | px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|cci20_gt_100|close_gt_prior_high55   |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3274 | 0.4874 |   1.0418 | -0.5528 |   0.8817 | px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|cci20_gt_100|close_gt_prior_high20   |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3272 | 0.4766 |   1.1106 | -0.5212 |   0.9144 | px_gt_ema150|sma100_gt_sma250|roc10_gt_0|stochrsi14_gt_50|rv21_pct_lt_70     |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3272 | 0.4824 |   1.0684 | -0.4952 |   0.9741 | px_gt_ema20|px_gt_ema50|px_gt_ema250|roc120_gt_0|atr14_pct_lt_3              |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3270 | 0.4955 |   1.0395 | -0.5974 |   0.8294 | px_gt_ema50|roc120_gt_0|rv21_lt_40|ar1_30_gt_0|cci20_gt_100                  |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3263 | 0.4858 |   1.0490 | -0.6807 |   0.7137 | px_gt_sma20|px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3262 | 0.4723 |   1.1194 | -0.4354 |   1.0846 | px_gt_ema20|px_gt_sma150|sma100_gt_sma250|stochrsi14_gt_50|rv21_pct_lt_70    |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3260 | 0.4803 |   1.0891 | -0.5647 |   0.8506 | macd_hist_gt_0|roc10_gt_0|roc120_gt_0|rv21_pct_lt_70|stoch14_gt_80           |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3259 | 0.4898 |   1.0485 | -0.7185 |   0.6817 | px_gt_sma20|roc10_gt_0|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                 |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3258 | 0.5138 |   1.0194 | -0.6519 |   0.7881 | sma100_gt_sma250|roc10_gt_0|rv21_lt_40|ar1_30_gt_0|cci20_gt_0                |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3257 | 0.4861 |   1.0540 | -0.4749 |   1.0236 | px_gt_ema10|px_gt_ema100|sma50_gt_sma150|rv21_pct_lt_70|ar1_30_gt_0          |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3257 | 0.4871 |   1.0547 | -0.6616 |   0.7362 | px_gt_sma20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80              |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3257 | 0.4997 |   1.0385 | -0.6647 |   0.7519 | px_gt_sma20|roc120_gt_0|rv21_lt_40|ar1_30_gt_0|stoch14_gt_80                 |
| QQQ      | TQQQ_3x   |   4 |   2 |    1.3255 | 0.4859 |   1.0531 | -0.6752 |   0.7197 | px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                            |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3255 | 0.4859 |   1.0531 | -0.6752 |   0.7197 | px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20      |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3255 | 0.4859 |   1.0531 | -0.6752 |   0.7197 | px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55      |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3254 | 0.4690 |   1.1172 | -0.4057 |   1.1560 | px_gt_sma150|sma100_gt_sma250|roc20_gt_0|stochrsi14_gt_50|rv21_pct_lt_70     |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3251 | 0.4844 |   1.0504 | -0.6752 |   0.7175 | px_gt_ema20|px_gt_ema50|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3248 | 0.5142 |   1.0428 | -0.6837 |   0.7521 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|cci20_gt_100|close_gt_prior_high20       |
| QQQ      | TQQQ_3x   |   4 |   1 |    1.3248 | 0.5142 |   1.0428 | -0.6837 |   0.7521 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high20                    |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3248 | 0.5142 |   1.0428 | -0.6837 |   0.7521 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80|close_gt_prior_high55      |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3248 | 0.5142 |   1.0428 | -0.6837 |   0.7521 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80|cci20_gt_100               |
| QQQ      | TQQQ_3x   |   4 |   1 |    1.3248 | 0.5142 |   1.0428 | -0.6837 |   0.7521 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80                            |
| QQQ      | TQQQ_3x   |   3 |   1 |    1.3248 | 0.5142 |   1.0428 | -0.6837 |   0.7521 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0                                          |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3248 | 0.5142 |   1.0428 | -0.6837 |   0.7521 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|cci20_gt_100|close_gt_prior_high55       |
| QQQ      | TQQQ_3x   |   4 |   1 |    1.3248 | 0.5142 |   1.0428 | -0.6837 |   0.7521 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high55                    |
| QQQ      | TQQQ_3x   |   4 |   1 |    1.3248 | 0.5142 |   1.0428 | -0.6837 |   0.7521 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|cci20_gt_100                             |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3248 | 0.5142 |   1.0428 | -0.6837 |   0.7521 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80|close_gt_prior_high20      |
| QQQ      | TQQQ_3x   |   4 |   1 |    1.3242 | 0.5181 |   1.0465 | -0.6967 |   0.7435 | roc10_gt_0|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high55                     |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3242 | 0.5181 |   1.0465 | -0.6967 |   0.7435 | roc10_gt_0|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80|cci20_gt_100                |
| QQQ      | TQQQ_3x   |   4 |   1 |    1.3242 | 0.5181 |   1.0465 | -0.6967 |   0.7435 | roc10_gt_0|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80                             |
| QQQ      | TQQQ_3x   |   4 |   1 |    1.3242 | 0.5181 |   1.0465 | -0.6967 |   0.7435 | roc10_gt_0|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high20                     |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3242 | 0.5181 |   1.0465 | -0.6967 |   0.7435 | roc10_gt_0|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80|close_gt_prior_high20       |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3242 | 0.5181 |   1.0465 | -0.6967 |   0.7435 | roc10_gt_0|roc120_gt_0|ar1_30_gt_0|cci20_gt_100|close_gt_prior_high55        |
| QQQ      | TQQQ_3x   |   3 |   1 |    1.3242 | 0.5181 |   1.0465 | -0.6967 |   0.7435 | roc10_gt_0|roc120_gt_0|ar1_30_gt_0                                           |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3242 | 0.5181 |   1.0465 | -0.6967 |   0.7435 | roc10_gt_0|roc120_gt_0|ar1_30_gt_0|cci20_gt_100|close_gt_prior_high20        |
| QQQ      | TQQQ_3x   |   4 |   1 |    1.3242 | 0.5181 |   1.0465 | -0.6967 |   0.7435 | roc10_gt_0|roc120_gt_0|ar1_30_gt_0|cci20_gt_100                              |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3242 | 0.5181 |   1.0465 | -0.6967 |   0.7435 | roc10_gt_0|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80|close_gt_prior_high55       |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3241 | 0.4888 |   1.0476 | -0.6981 |   0.7001 | roc10_gt_0|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0                  |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3237 | 0.4793 |   1.1123 | -0.4605 |   1.0408 | sma100_gt_sma250|macd_hist_gt_0|roc10_gt_0|roc120_gt_0|rv21_pct_lt_70        |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3234 | 0.5084 |   1.0275 | -0.6639 |   0.7657 | px_gt_sma20|px_gt_ema20|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0               |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3233 | 0.4934 |   1.0428 | -0.6154 |   0.8018 | px_gt_ema10|px_gt_ema100|sma100_gt_sma250|rv21_pct_lt_70|ar1_30_gt_0         |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3231 | 0.4928 |   1.0288 | -0.5172 |   0.9527 | px_gt_ema50|roc120_gt_0|rv21_lt_40|rv21_pct_lt_70|ar1_30_gt_0                |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3228 | 0.5093 |   1.0586 | -0.6209 |   0.8203 | px_gt_ema50|sma50_gt_sma200|roc20_gt_0|roc120_gt_0|ar1_30_gt_0               |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3226 | 0.4844 |   1.0491 | -0.6818 |   0.7104 | px_gt_sma20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80              |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3224 | 0.4871 |   1.0291 | -0.6006 |   0.8111 | px_gt_ema20|px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0              |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3219 | 0.4914 |   1.0466 | -0.5765 |   0.8525 | px_gt_sma20|px_gt_ema100|sma100_gt_sma250|rv21_pct_lt_70|ar1_30_gt_0         |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3216 | 0.5092 |   1.0576 | -0.6209 |   0.8201 | px_gt_sma20|px_gt_ema50|sma50_gt_sma200|roc120_gt_0|ar1_30_gt_0              |
| QQQ      | TQQQ_3x   |   4 |   2 |    1.3214 | 0.5193 |   1.0416 | -0.5808 |   0.8941 | sma100_gt_sma250|rv21_lt_40|ar1_30_gt_0|cci20_gt_100                         |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3214 | 0.5193 |   1.0416 | -0.5808 |   0.8941 | sma100_gt_sma250|rv21_lt_40|ar1_30_gt_0|cci20_gt_100|close_gt_prior_high55   |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3214 | 0.5130 |   1.0200 | -0.6746 |   0.7605 | sma100_gt_sma250|roc10_gt_0|rv21_lt_40|ar1_30_gt_0|stoch14_gt_80             |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3213 | 0.4847 |   1.0516 | -0.6616 |   0.7326 | px_gt_sma20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20      |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3213 | 0.4847 |   1.0516 | -0.6616 |   0.7326 | px_gt_sma20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55      |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3213 | 0.4847 |   1.0516 | -0.6616 |   0.7326 | px_gt_sma20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100               |
| QQQ      | TQQQ_3x   |   4 |   2 |    1.3213 | 0.4847 |   1.0516 | -0.6616 |   0.7326 | px_gt_sma20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3                            |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3213 | 0.4841 |   1.0557 | -0.4828 |   1.0027 | px_gt_sma20|px_gt_ema100|sma50_gt_sma150|rv21_pct_lt_70|ar1_30_gt_0          |
| QQQ      | TQQQ_3x   |   4 |   2 |    1.3211 | 0.4778 |   1.0475 | -0.6413 |   0.7449 | px_gt_ema50|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                            |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3211 | 0.4778 |   1.0475 | -0.6413 |   0.7449 | px_gt_ema50|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20      |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3211 | 0.4778 |   1.0475 | -0.6413 |   0.7449 | px_gt_ema50|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55      |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3207 | 0.4866 |   1.0286 | -0.6431 |   0.7567 | px_gt_ema20|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|bear_power_gt_0          |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3203 | 0.4923 |   1.0186 | -0.5886 |   0.8364 | px_gt_ema5|px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0               |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3201 | 0.4976 |   1.0299 | -0.6945 |   0.7165 | roc10_gt_0|roc120_gt_0|rv21_lt_40|ar1_30_gt_0|cci20_gt_0                     |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3200 | 0.4848 |   1.0530 | -0.6073 |   0.7983 | px_gt_ema20|px_gt_ema50|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3                |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3200 | 0.4717 |   1.1125 | -0.5557 |   0.8488 | px_gt_sma150|sma100_gt_sma250|stochrsi14_gt_50|rv21_pct_lt_70|cci20_gt_0     |
| QQQ      | TQQQ_3x   |   4 |   2 |    1.3200 | 0.4773 |   1.0847 | -0.5647 |   0.8452 | macd_hist_gt_0|roc10_gt_0|roc120_gt_0|rv21_pct_lt_70                         |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3200 | 0.4773 |   1.0847 | -0.5647 |   0.8452 | macd_hist_gt_0|roc10_gt_0|roc120_gt_0|rv21_pct_lt_70|close_gt_prior_high55   |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3200 | 0.4773 |   1.0847 | -0.5647 |   0.8452 | macd_hist_gt_0|roc10_gt_0|roc120_gt_0|rv21_pct_lt_70|close_gt_prior_high20   |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3200 | 0.4773 |   1.0847 | -0.5647 |   0.8452 | macd_hist_gt_0|roc10_gt_0|roc120_gt_0|rv21_pct_lt_70|cci20_gt_100            |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3199 | 0.4840 |   1.0550 | -0.5785 |   0.8367 | px_gt_ema20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80              |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3195 | 0.4952 |   1.0330 | -0.6640 |   0.7458 | px_gt_ema20|roc120_gt_0|rv21_lt_40|ar1_30_gt_0|stoch14_gt_80                 |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3190 | 0.5121 |   1.0197 | -0.6472 |   0.7912 | px_gt_ema5|px_gt_sma20|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0                |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3189 | 0.4868 |   1.0689 | -0.6021 |   0.8084 | px_gt_ema20|sma50_gt_sma200|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0            |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3188 | 0.4881 |   1.0913 | -0.5099 |   0.9573 | sma100_gt_sma250|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100|bear_power_gt_0     |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3187 | 0.4942 |   1.0246 | -0.7578 |   0.6521 | px_gt_ema10|px_gt_sma20|roc120_gt_0|rv21_lt_40|ar1_30_gt_0                   |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3187 | 0.4781 |   1.1010 | -0.4472 |   1.0691 | px_gt_sma10|px_gt_ema20|sma100_gt_sma250|sma50_gt_sma150|rv21_pct_lt_70      |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3186 | 0.4855 |   1.0271 | -0.6076 |   0.7990 | px_gt_ema20|px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0              |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3180 | 0.4913 |   1.0655 | -0.5139 |   0.9560 | sma100_gt_sma250|roc10_gt_0|rv21_pct_lt_70|ar1_30_gt_0|cci20_gt_100          |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3179 | 0.4830 |   1.0564 | -0.6236 |   0.7745 | px_gt_ema20|px_gt_ema50|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100              |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3179 | 0.5094 |   1.0140 | -0.6837 |   0.7451 | px_gt_sma20|sma100_gt_sma250|roc10_gt_0|rv21_lt_40|ar1_30_gt_0               |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3178 | 0.4846 |   1.0582 | -0.6923 |   0.7000 | px_gt_sma20|sma100_gt_sma250|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3           |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3176 | 0.4757 |   1.0453 | -0.6413 |   0.7417 | px_gt_ema50|roc20_gt_0|roc120_gt_0|rv21_lt_40|atr14_pct_lt_3                 |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3175 | 0.4840 |   1.0520 | -0.6884 |   0.7032 | px_gt_sma20|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0|bear_power_gt_0            |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3174 | 0.4817 |   1.0344 | -0.5528 |   0.8714 | px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|atr14_pct_lt_5|cci20_gt_100          |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3174 | 0.5244 |   1.0216 | -0.6544 |   0.8012 | sma100_gt_sma250|roc10_gt_0|roc120_gt_0|ar1_30_gt_0|atr14_pct_lt_5           |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3171 | 0.5156 |   1.0296 | -0.6363 |   0.8103 | px_gt_ema5|px_gt_sma10|px_gt_ema20|roc120_gt_0|ar1_30_gt_0                   |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3171 | 0.5040 |   1.0261 | -0.6836 |   0.7372 | px_gt_sma20|px_gt_ema20|roc120_gt_0|rv21_pct_lt_50|ar1_30_gt_0               |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3169 | 0.5106 |   1.0216 | -0.6573 |   0.7768 | px_gt_ema5|px_gt_sma20|roc120_gt_0|rv21_pct_lt_50|ar1_30_gt_0                |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3165 | 0.4752 |   1.0588 | -0.5358 |   0.8869 | px_gt_sma50|px_gt_ema250|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3               |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3164 | 0.4824 |   1.0584 | -0.6081 |   0.7933 | px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80|cci20_gt_100            |
| QQQ      | TQQQ_3x   |   4 |   2 |    1.3164 | 0.4824 |   1.0584 | -0.6081 |   0.7933 | px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80                         |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3164 | 0.4824 |   1.0584 | -0.6081 |   0.7933 | px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80|close_gt_prior_high55   |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3164 | 0.4824 |   1.0584 | -0.6081 |   0.7933 | px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80|close_gt_prior_high20   |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3164 | 0.4810 |   1.0421 | -0.6752 |   0.7125 | px_gt_ema20|px_gt_ema100|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3               |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3163 | 0.5148 |   1.0286 | -0.6808 |   0.7562 | px_gt_ema5|px_gt_sma20|px_gt_ema50|roc120_gt_0|ar1_30_gt_0                   |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3161 | 0.4950 |   1.0442 | -0.5496 |   0.9005 | px_gt_sma20|sma100_gt_sma250|roc60_gt_0|rv21_pct_lt_70|ar1_30_gt_0           |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3160 | 0.4793 |   1.0612 | -0.6822 |   0.7026 | px_gt_ema250|roc10_gt_0|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                |
| QQQ      | TQQQ_3x   |   5 |   3 |    1.3159 | 0.4764 |   1.0576 | -0.5516 |   0.8636 | px_gt_sma50|sma100_gt_sma250|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3           |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3159 | 0.4818 |   1.0548 | -0.6282 |   0.7670 | px_gt_ema20|px_gt_ema50|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20     |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3159 | 0.4818 |   1.0548 | -0.6282 |   0.7670 | px_gt_ema20|px_gt_ema50|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55     |
| QQQ      | TQQQ_3x   |   4 |   2 |    1.3159 | 0.4818 |   1.0548 | -0.6282 |   0.7670 | px_gt_ema20|px_gt_ema50|roc120_gt_0|atr14_pct_lt_3                           |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3159 | 0.4818 |   1.0575 | -0.6058 |   0.7953 | px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55|bear_power_gt_0 |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3159 | 0.4818 |   1.0575 | -0.6058 |   0.7953 | px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20|bear_power_gt_0 |
| QQQ      | TQQQ_3x   |   4 |   2 |    1.3159 | 0.4818 |   1.0575 | -0.6058 |   0.7953 | px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0                       |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3159 | 0.4818 |   1.0575 | -0.6058 |   0.7953 | px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100|bear_power_gt_0          |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3156 | 0.4817 |   1.0519 | -0.5785 |   0.8327 | px_gt_ema20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55      |
| QQQ      | TQQQ_3x   |   4 |   2 |    1.3156 | 0.4817 |   1.0519 | -0.5785 |   0.8327 | px_gt_ema20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3                            |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3156 | 0.4817 |   1.0519 | -0.5785 |   0.8327 | px_gt_ema20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100               |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3156 | 0.4817 |   1.0519 | -0.5785 |   0.8327 | px_gt_ema20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20      |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3155 | 0.4856 |   1.0212 | -0.6980 |   0.6957 | px_gt_sma20|px_gt_ema100|roc20_gt_0|rv21_pct_lt_70|ar1_30_gt_0               |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3151 | 0.5242 |   1.0457 | -0.6209 |   0.8443 | sma100_gt_sma250|roc120_gt_0|rsi14_rising|rv21_pct_lt_70|ar1_30_gt_0         |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3151 | 0.5071 |   1.0133 | -0.6422 |   0.7895 | px_gt_sma20|sma100_gt_sma250|rv21_lt_40|ar1_30_gt_0|stoch14_gt_80            |
| QQQ      | TQQQ_3x   |   5 |   1 |    1.3150 | 0.5133 |   1.0267 | -0.6914 |   0.7424 | px_gt_ema5|px_gt_sma20|px_gt_sma50|roc120_gt_0|ar1_30_gt_0                   |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3150 | 0.5072 |   1.0130 | -0.6618 |   0.7663 | px_gt_sma20|sma100_gt_sma250|rv21_lt_40|ar1_30_gt_0|bear_power_gt_0          |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3150 | 0.4812 |   1.0463 | -0.6980 |   0.6894 | px_gt_sma20|px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0                |
| QQQ      | TQQQ_3x   |   5 |   2 |    1.3146 | 0.5095 |   1.0162 | -0.6874 |   0.7412 | sma100_gt_sma250|roc10_gt_0|rv21_lt_40|ar1_30_gt_0|close_gt_prior_high20     |

## Method Notes

- Top rows are retained by Sortino, then CAGR, then Calmar.
- Signals are lagged one base bar before returns to avoid same-close look-ahead; `extra_lag_days` adds operational execution delay `[advances_fin_ml, p.31-34]`.
- Redundant signal groups are excluded by default, including equivalent MACD forms and nested thresholds.
- All evaluated configs must be included in later DSR trial accounting `[advances_fin_ml, p.222-223]`.
