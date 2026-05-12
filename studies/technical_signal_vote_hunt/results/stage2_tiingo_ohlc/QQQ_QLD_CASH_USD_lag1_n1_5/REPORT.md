# Stage 2 Tiingo OHLC Grid Results

Status: capped exact-grid discovery. This is not a validation verdict.

Branch: `QQQ`
Risk-ons: `QLD_2x`
Off leg: `CASH_USD`
Extra execution lag days: `1`
Redundant signals allowed: `False`
Signal subset range: n=1..5
Estimated/configs tested: 7,067,694 / 7,067,694
Windows: QLD_2x: 2006-06-22..2026-04-14 (4,983 bars)
Elapsed seconds: 1315.9

## Top Configs

| branch   | risk_on   |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                       |
|:---------|:----------|----:|----:|----------:|-------:|---------:|--------:|---------:|:------------------------------------------------------------------------------|
| QQQ      | QLD_2x    |   5 |   2 |    1.3181 | 0.3454 |   1.0408 | -0.5309 |   0.6507 | roc10_gt_0|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0                   |
| QQQ      | QLD_2x    |   5 |   2 |    1.3169 | 0.3449 |   1.0391 | -0.5522 |   0.6247 | px_gt_sma20|roc10_gt_0|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                  |
| QQQ      | QLD_2x    |   5 |   2 |    1.3060 | 0.3395 |   1.0383 | -0.4934 |   0.6882 | px_gt_sma20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100                |
| QQQ      | QLD_2x    |   5 |   2 |    1.3060 | 0.3395 |   1.0383 | -0.4934 |   0.6882 | px_gt_sma20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55       |
| QQQ      | QLD_2x    |   5 |   2 |    1.3060 | 0.3395 |   1.0383 | -0.4934 |   0.6882 | px_gt_sma20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20       |
| QQQ      | QLD_2x    |   4 |   2 |    1.3060 | 0.3395 |   1.0383 | -0.4934 |   0.6882 | px_gt_sma20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3                             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2990 | 0.3389 |   1.0308 | -0.4944 |   0.6856 | px_gt_ema20|roc10_gt_0|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                  |
| QQQ      | QLD_2x    |   4 |   2 |    1.2956 | 0.3374 |   1.0339 | -0.4866 |   0.6934 | roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0                              |
| QQQ      | QLD_2x    |   5 |   2 |    1.2956 | 0.3374 |   1.0339 | -0.4866 |   0.6934 | roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0|close_gt_prior_high20        |
| QQQ      | QLD_2x    |   5 |   2 |    1.2956 | 0.3374 |   1.0339 | -0.4866 |   0.6934 | roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0|close_gt_prior_high55        |
| QQQ      | QLD_2x    |   5 |   2 |    1.2935 | 0.3380 |   1.0317 | -0.5337 |   0.6334 | roc10_gt_0|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0              |
| QQQ      | QLD_2x    |   5 |   2 |    1.2901 | 0.3339 |   1.0271 | -0.5143 |   0.6491 | px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2896 | 0.3344 |   1.0284 | -0.4390 |   0.7618 | px_gt_ema20|px_gt_ema50|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3                 |
| QQQ      | QLD_2x    |   5 |   3 |    1.2895 | 0.3310 |   1.0516 | -0.5409 |   0.6119 | px_gt_ema20|roc120_gt_0|rv21_pct_lt_70|adx14_gt_20|atr14_pct_lt_3             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2891 | 0.3330 |   1.0220 | -0.5299 |   0.6285 | px_gt_sma20|px_gt_ema20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3                 |
| QQQ      | QLD_2x    |   5 |   2 |    1.2890 | 0.3339 |   1.0301 | -0.4441 |   0.7519 | px_gt_ema20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2879 | 0.3332 |   1.0295 | -0.4126 |   0.8075 | px_gt_ema20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80               |
| QQQ      | QLD_2x    |   5 |   2 |    1.2851 | 0.3334 |   1.0214 | -0.5342 |   0.6240 | px_gt_ema20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0                  |
| QQQ      | QLD_2x    |   5 |   2 |    1.2845 | 0.3321 |   1.0270 | -0.4126 |   0.8048 | px_gt_ema20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20       |
| QQQ      | QLD_2x    |   4 |   2 |    1.2845 | 0.3321 |   1.0270 | -0.4126 |   0.8048 | px_gt_ema20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3                             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2845 | 0.3321 |   1.0270 | -0.4126 |   0.8048 | px_gt_ema20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100                |
| QQQ      | QLD_2x    |   5 |   2 |    1.2845 | 0.3321 |   1.0270 | -0.4126 |   0.8048 | px_gt_ema20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55       |
| QQQ      | QLD_2x    |   5 |   2 |    1.2840 | 0.3331 |   1.0214 | -0.4609 |   0.7227 | px_gt_ema20|px_gt_ema100|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3                |
| QQQ      | QLD_2x    |   5 |   2 |    1.2808 | 0.3304 |   1.0135 | -0.5256 |   0.6287 | px_gt_sma20|px_gt_ema50|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3                 |
| QQQ      | QLD_2x    |   5 |   2 |    1.2796 | 0.3299 |   1.0190 | -0.4958 |   0.6653 | px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80               |
| QQQ      | QLD_2x    |   5 |   2 |    1.2791 | 0.3329 |   1.0215 | -0.4934 |   0.6747 | px_gt_sma20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80               |
| QQQ      | QLD_2x    |   5 |   2 |    1.2786 | 0.3312 |   1.0150 | -0.5193 |   0.6379 | px_gt_ema50|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0                  |
| QQQ      | QLD_2x    |   5 |   2 |    1.2752 | 0.3291 |   1.0067 | -0.5441 |   0.6049 | px_gt_sma20|px_gt_ema100|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3                |
| QQQ      | QLD_2x    |   5 |   3 |    1.2743 | 0.3262 |   1.0399 | -0.5901 |   0.5528 | roc20_gt_0|roc120_gt_0|rv21_pct_lt_70|adx14_gt_20|atr14_pct_lt_3              |
| QQQ      | QLD_2x    |   5 |   2 |    1.2735 | 0.3263 |   1.0035 | -0.4934 |   0.6614 | px_gt_sma20|roc10_gt_0|roc120_gt_0|rv21_pct_lt_50|atr14_pct_lt_3              |
| QQQ      | QLD_2x    |   4 |   2 |    1.2721 | 0.3207 |   1.0768 | -0.3341 |   0.9600 | roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70|ar1_30_gt_0                       |
| QQQ      | QLD_2x    |   5 |   2 |    1.2721 | 0.3267 |   1.0063 | -0.5142 |   0.6353 | px_gt_sma20|px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                 |
| QQQ      | QLD_2x    |   5 |   3 |    1.2718 | 0.3169 |   1.0352 | -0.4558 |   0.6954 | px_gt_ema20|roc120_gt_0|rv21_pct_lt_50|adx14_gt_20|atr14_pct_lt_3             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2716 | 0.3305 |   1.0159 | -0.5205 |   0.6350 | px_gt_sma20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2682 | 0.3291 |   0.9986 | -0.6099 |   0.5397 | px_gt_sma20|roc10_gt_0|roc120_gt_0|rv21_pct_lt_70|atr14_pct_lt_3              |
| QQQ      | QLD_2x    |   5 |   2 |    1.2677 | 0.3302 |   1.0160 | -0.4866 |   0.6786 | roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80|cci20_gt_0                |
| QQQ      | QLD_2x    |   5 |   3 |    1.2671 | 0.3415 |   1.0339 | -0.5333 |   0.6404 | px_gt_ema20|roc120_gt_0|rv21_pct_lt_70|adx14_gt_20|atr14_pct_lt_5             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2668 | 0.3426 |   1.0311 | -0.5312 |   0.6450 | px_gt_ema20|roc120_gt_0|rv21_pct_lt_70|adx14_gt_20|close_gt_prior_high20      |
| QQQ      | QLD_2x    |   5 |   2 |    1.2665 | 0.3255 |   1.0018 | -0.4866 |   0.6688 | roc10_gt_0|roc120_gt_0|rv21_pct_lt_50|atr14_pct_lt_3|cci20_gt_0               |
| QQQ      | QLD_2x    |   5 |   3 |    1.2645 | 0.3152 |   1.0303 | -0.5221 |   0.6038 | roc20_gt_0|roc120_gt_0|rv21_pct_lt_50|adx14_gt_20|atr14_pct_lt_3              |
| QQQ      | QLD_2x    |   5 |   2 |    1.2628 | 0.3415 |   1.0292 | -0.5333 |   0.6404 | px_gt_ema20|roc120_gt_0|rv21_pct_lt_70|adx14_gt_20|close_gt_prior_high55      |
| QQQ      | QLD_2x    |   4 |   2 |    1.2628 | 0.3415 |   1.0292 | -0.5333 |   0.6404 | px_gt_ema20|roc120_gt_0|rv21_pct_lt_70|adx14_gt_20                            |
| QQQ      | QLD_2x    |   5 |   2 |    1.2623 | 0.3276 |   1.0003 | -0.5387 |   0.6082 | px_gt_ema20|roc10_gt_0|roc120_gt_0|rv21_pct_lt_70|atr14_pct_lt_3              |
| QQQ      | QLD_2x    |   5 |   2 |    1.2621 | 0.3252 |   1.0122 | -0.4527 |   0.7185 | px_gt_ema50|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2620 | 0.3295 |   1.0430 | -0.5342 |   0.6167 | px_gt_ema20|roc10_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70            |
| QQQ      | QLD_2x    |   5 |   2 |    1.2618 | 0.3244 |   1.0163 | -0.4729 |   0.6860 | px_gt_ema20|px_gt_ema50|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0            |
| QQQ      | QLD_2x    |   5 |   3 |    1.2617 | 0.3215 |   1.0341 | -0.4156 |   0.7735 | px_gt_ema50|roc120_gt_0|rv21_pct_lt_70|adx14_gt_20|atr14_pct_lt_3             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2614 | 0.3283 |   0.9969 | -0.6047 |   0.5429 | roc10_gt_0|roc120_gt_0|rv21_pct_lt_70|atr14_pct_lt_3|cci20_gt_0               |
| QQQ      | QLD_2x    |   5 |   2 |    1.2604 | 0.3255 |   0.9991 | -0.5380 |   0.6049 | px_gt_ema100|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0                 |
| QQQ      | QLD_2x    |   5 |   2 |    1.2596 | 0.3217 |   0.9985 | -0.4126 |   0.7797 | px_gt_ema20|roc10_gt_0|roc120_gt_0|rv21_pct_lt_50|atr14_pct_lt_3              |
| QQQ      | QLD_2x    |   5 |   3 |    1.2592 | 0.3207 |   1.0245 | -0.5754 |   0.5573 | px_gt_sma20|roc120_gt_0|rv21_pct_lt_70|adx14_gt_20|atr14_pct_lt_3             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2584 | 0.3162 |   1.0639 | -0.3518 |   0.8989 | roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70|ar1_30_gt_0|close_gt_prior_high55 |
| QQQ      | QLD_2x    |   5 |   2 |    1.2577 | 0.3218 |   1.0167 | -0.4386 |   0.7339 | px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100|bear_power_gt_0           |
| QQQ      | QLD_2x    |   5 |   2 |    1.2575 | 0.3205 |   1.0125 | -0.4539 |   0.7061 | px_gt_ema50|px_gt_ema100|roc120_gt_0|rv21_pct_lt_70|atr14_pct_lt_3            |
| QQQ      | QLD_2x    |   5 |   2 |    1.2574 | 0.3218 |   1.0169 | -0.4386 |   0.7338 | px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20|bear_power_gt_0  |
| QQQ      | QLD_2x    |   5 |   2 |    1.2574 | 0.3218 |   1.0169 | -0.4386 |   0.7338 | px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55|bear_power_gt_0  |
| QQQ      | QLD_2x    |   4 |   2 |    1.2574 | 0.3218 |   1.0169 | -0.4386 |   0.7338 | px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0                        |
| QQQ      | QLD_2x    |   4 |   2 |    1.2557 | 0.3211 |   1.0107 | -0.5054 |   0.6354 | roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0                         |
| QQQ      | QLD_2x    |   5 |   2 |    1.2557 | 0.3211 |   1.0107 | -0.5054 |   0.6354 | roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55|bear_power_gt_0   |
| QQQ      | QLD_2x    |   5 |   2 |    1.2557 | 0.3211 |   1.0107 | -0.5054 |   0.6354 | roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20|bear_power_gt_0   |
| QQQ      | QLD_2x    |   5 |   2 |    1.2543 | 0.3214 |   1.0026 | -0.5113 |   0.6286 | px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55       |
| QQQ      | QLD_2x    |   4 |   2 |    1.2543 | 0.3214 |   1.0026 | -0.5113 |   0.6286 | px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2543 | 0.3214 |   1.0026 | -0.5113 |   0.6286 | px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20       |
| QQQ      | QLD_2x    |   5 |   2 |    1.2541 | 0.3236 |   0.9963 | -0.5823 |   0.5558 | px_gt_sma20|px_gt_sma50|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3                 |
| QQQ      | QLD_2x    |   5 |   2 |    1.2539 | 0.3415 |   0.9936 | -0.4869 |   0.7014 | px_gt_sma20|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0|adx14_gt_20                |
| QQQ      | QLD_2x    |   5 |   3 |    1.2533 | 0.3265 |   1.0389 | -0.4584 |   0.7124 | sma50_gt_sma200|roc20_gt_0|roc120_gt_0|rv21_lt_40|ar1_30_gt_0                 |
| QQQ      | QLD_2x    |   5 |   1 |    1.2528 | 0.3372 |   0.9831 | -0.5199 |   0.6486 | px_gt_sma50|px_gt_ema100|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0               |
| QQQ      | QLD_2x    |   5 |   2 |    1.2527 | 0.3203 |   1.0079 | -0.5125 |   0.6250 | roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100|bear_power_gt_0            |
| QQQ      | QLD_2x    |   5 |   2 |    1.2521 | 0.3208 |   1.0057 | -0.4847 |   0.6619 | px_gt_ema20|px_gt_ema100|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0           |
| QQQ      | QLD_2x    |   5 |   2 |    1.2517 | 0.3233 |   1.0036 | -0.5205 |   0.6212 | px_gt_sma20|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0|bear_power_gt_0             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2511 | 0.3206 |   1.0000 | -0.5076 |   0.6316 | px_gt_ema20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100                |
| QQQ      | QLD_2x    |   5 |   2 |    1.2507 | 0.3206 |   0.9958 | -0.5113 |   0.6270 | px_gt_ema20|px_gt_ema100|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                |
| QQQ      | QLD_2x    |   5 |   2 |    1.2507 | 0.3190 |   1.0119 | -0.3930 |   0.8117 | px_gt_sma10|px_gt_ema100|sma50_gt_sma150|rv21_pct_lt_70|ar1_30_gt_0           |
| QQQ      | QLD_2x    |   5 |   2 |    1.2505 | 0.3160 |   1.0003 | -0.5193 |   0.6085 | px_gt_ema50|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55       |
| QQQ      | QLD_2x    |   5 |   2 |    1.2505 | 0.3160 |   1.0003 | -0.5193 |   0.6085 | px_gt_ema50|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20       |
| QQQ      | QLD_2x    |   4 |   2 |    1.2505 | 0.3160 |   1.0003 | -0.5193 |   0.6085 | px_gt_ema50|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                             |
| QQQ      | QLD_2x    |   5 |   1 |    1.2502 | 0.3216 |   0.9862 | -0.5657 |   0.5685 | px_gt_sma50|px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0               |
| QQQ      | QLD_2x    |   5 |   1 |    1.2497 | 0.3215 |   0.9854 | -0.5926 |   0.5426 | px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|ar1_30_gt_0|cci20_gt_100              |
| QQQ      | QLD_2x    |   5 |   2 |    1.2496 | 0.3230 |   1.0004 | -0.5284 |   0.6112 | px_gt_ema20|px_gt_sma50|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3                 |
| QQQ      | QLD_2x    |   5 |   2 |    1.2495 | 0.3165 |   0.9974 | -0.4959 |   0.6382 | px_gt_ema50|px_gt_ema100|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                |
| QQQ      | QLD_2x    |   5 |   2 |    1.2494 | 0.3224 |   0.9978 | -0.5348 |   0.6029 | roc10_gt_0|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80                |
| QQQ      | QLD_2x    |   5 |   2 |    1.2489 | 0.3165 |   1.0006 | -0.5450 |   0.5808 | px_gt_ema20|px_gt_sma50|px_gt_ema100|rv21_pct_lt_70|atr14_pct_lt_5            |
| QQQ      | QLD_2x    |   5 |   2 |    1.2489 | 0.3180 |   1.0189 | -0.3587 |   0.8864 | px_gt_ema100|sma50_gt_sma150|roc20_gt_0|rv21_pct_lt_70|ar1_30_gt_0            |
| QQQ      | QLD_2x    |   5 |   2 |    1.2487 | 0.3221 |   0.9998 | -0.5590 |   0.5762 | px_gt_ema20|roc120_gt_0|rv21_pct_lt_70|atr14_pct_lt_3|bear_power_gt_0         |
| QQQ      | QLD_2x    |   5 |   2 |    1.2480 | 0.3188 |   0.9955 | -0.5113 |   0.6235 | px_gt_ema20|px_gt_ema50|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                 |
| QQQ      | QLD_2x    |   5 |   2 |    1.2476 | 0.3147 |   0.9964 | -0.5296 |   0.5943 | px_gt_ema50|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100                |
| QQQ      | QLD_2x    |   5 |   2 |    1.2472 | 0.3227 |   0.9941 | -0.5767 |   0.5595 | px_gt_sma50|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0                  |
| QQQ      | QLD_2x    |   5 |   2 |    1.2471 | 0.3171 |   1.0092 | -0.3776 |   0.8398 | px_gt_ema10|px_gt_ema100|sma50_gt_sma150|rv21_pct_lt_70|ar1_30_gt_0           |
| QQQ      | QLD_2x    |   5 |   1 |    1.2465 | 0.3394 |   0.9824 | -0.5459 |   0.6216 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high55|bear_power_gt_0     |
| QQQ      | QLD_2x    |   5 |   1 |    1.2465 | 0.3394 |   0.9824 | -0.5459 |   0.6216 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|cci20_gt_100|bear_power_gt_0              |
| QQQ      | QLD_2x    |   5 |   1 |    1.2465 | 0.3394 |   0.9824 | -0.5459 |   0.6216 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80|bear_power_gt_0             |
| QQQ      | QLD_2x    |   4 |   1 |    1.2465 | 0.3394 |   0.9824 | -0.5459 |   0.6216 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|bear_power_gt_0                           |
| QQQ      | QLD_2x    |   5 |   1 |    1.2465 | 0.3394 |   0.9824 | -0.5459 |   0.6216 | px_gt_sma20|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high20|bear_power_gt_0     |
| QQQ      | QLD_2x    |   5 |   2 |    1.2462 | 0.3371 |   0.9897 | -0.4639 |   0.7266 | px_gt_ema20|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0|adx14_gt_20                |
| QQQ      | QLD_2x    |   5 |   2 |    1.2460 | 0.3230 |   0.9816 | -0.6101 |   0.5295 | px_gt_sma20|px_gt_ema250|roc10_gt_0|rv21_pct_lt_70|atr14_pct_lt_3             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2459 | 0.3144 |   1.0005 | -0.4901 |   0.6415 | px_gt_ema100|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55      |
| QQQ      | QLD_2x    |   4 |   2 |    1.2459 | 0.3144 |   1.0005 | -0.4901 |   0.6415 | px_gt_ema100|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                            |
| QQQ      | QLD_2x    |   5 |   1 |    1.2455 | 0.3374 |   0.9701 | -0.5267 |   0.6406 | px_gt_sma20|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0|bear_power_gt_0            |
| QQQ      | QLD_2x    |   5 |   2 |    1.2452 | 0.3159 |   0.9974 | -0.4386 |   0.7202 | px_gt_ema20|roc120_gt_0|rv21_pct_lt_50|atr14_pct_lt_3|bear_power_gt_0         |
| QQQ      | QLD_2x    |   5 |   2 |    1.2451 | 0.3173 |   1.0006 | -0.4604 |   0.6891 | px_gt_ema20|px_gt_ema50|px_gt_ema100|roc120_gt_0|atr14_pct_lt_3               |
| QQQ      | QLD_2x    |   4 |   2 |    1.2449 | 0.3176 |   0.9973 | -0.5108 |   0.6218 | px_gt_sma20|px_gt_ema20|roc120_gt_0|atr14_pct_lt_3                            |
| QQQ      | QLD_2x    |   5 |   2 |    1.2449 | 0.3176 |   0.9973 | -0.5108 |   0.6218 | px_gt_sma20|px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20      |
| QQQ      | QLD_2x    |   5 |   2 |    1.2449 | 0.3176 |   0.9973 | -0.5108 |   0.6218 | px_gt_sma20|px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55      |
| QQQ      | QLD_2x    |   5 |   2 |    1.2449 | 0.3176 |   0.9973 | -0.5108 |   0.6218 | px_gt_sma20|px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100               |
| QQQ      | QLD_2x    |   5 |   3 |    1.2449 | 0.3202 |   1.0145 | -0.4643 |   0.6898 | px_gt_ema20|px_gt_ema150|rv21_pct_lt_70|adx14_gt_20|atr14_pct_lt_5            |
| QQQ      | QLD_2x    |   5 |   2 |    1.2449 | 0.3243 |   1.0214 | -0.5248 |   0.6179 | roc10_gt_0|roc20_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2447 | 0.3350 |   0.9744 | -0.4602 |   0.7279 | px_gt_ema20|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0|atr14_pct_lt_5             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2446 | 0.3120 |   0.9912 | -0.4901 |   0.6366 | px_gt_ema100|roc20_gt_0|roc120_gt_0|rv21_pct_lt_50|atr14_pct_lt_3             |
| QQQ      | QLD_2x    |   5 |   1 |    1.2444 | 0.3341 |   0.9763 | -0.5422 |   0.6161 | px_gt_sma50|px_gt_ema50|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0                |
| QQQ      | QLD_2x    |   5 |   1 |    1.2442 | 0.3370 |   0.9696 | -0.5551 |   0.6071 | px_gt_sma20|px_gt_ema20|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0                |
| QQQ      | QLD_2x    |   5 |   2 |    1.2439 | 0.3398 |   1.0091 | -0.4860 |   0.6991 | px_gt_ema20|roc10_gt_0|roc120_gt_0|rv21_pct_lt_70|adx14_gt_25                 |
| QQQ      | QLD_2x    |   5 |   1 |    1.2436 | 0.3378 |   0.9787 | -0.5459 |   0.6188 | px_gt_sma20|px_gt_ema20|roc120_gt_0|ar1_30_gt_0|bear_power_gt_0               |
| QQQ      | QLD_2x    |   5 |   2 |    1.2436 | 0.3243 |   0.9796 | -0.5212 |   0.6223 | px_gt_sma50|px_gt_ema50|roc120_gt_0|rv21_lt_40|ar1_30_gt_0                    |
| QQQ      | QLD_2x    |   5 |   2 |    1.2433 | 0.3112 |   1.0254 | -0.3866 |   0.8051 | px_gt_sma20|px_gt_ema20|roc10_gt_0|roc120_gt_0|rv21_pct_lt_70                 |
| QQQ      | QLD_2x    |   5 |   2 |    1.2433 | 0.3152 |   1.0004 | -0.5085 |   0.6198 | px_gt_ema20|px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|atr14_pct_lt_5            |
| QQQ      | QLD_2x    |   5 |   2 |    1.2432 | 0.3225 |   0.9977 | -0.5439 |   0.5929 | roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0|bear_power_gt_0              |
| QQQ      | QLD_2x    |   5 |   3 |    1.2427 | 0.3141 |   1.0187 | -0.4941 |   0.6357 | px_gt_sma50|roc120_gt_0|rv21_pct_lt_70|adx14_gt_20|atr14_pct_lt_3             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2426 | 0.3191 |   0.9924 | -0.5299 |   0.6023 | px_gt_sma20|px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0                 |
| QQQ      | QLD_2x    |   5 |   2 |    1.2426 | 0.3119 |   1.0026 | -0.4095 |   0.7615 | px_gt_ema50|px_gt_ema100|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100              |
| QQQ      | QLD_2x    |   5 |   3 |    1.2424 | 0.3142 |   1.0114 | -0.5839 |   0.5381 | px_gt_sma20|px_gt_ema250|rv21_pct_lt_70|adx14_gt_20|atr14_pct_lt_3            |
| QQQ      | QLD_2x    |   4 |   2 |    1.2423 | 0.3158 |   1.0014 | -0.4647 |   0.6795 | px_gt_ema20|px_gt_ema50|roc120_gt_0|atr14_pct_lt_3                            |
| QQQ      | QLD_2x    |   5 |   2 |    1.2423 | 0.3158 |   1.0014 | -0.4647 |   0.6795 | px_gt_ema20|px_gt_ema50|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20      |
| QQQ      | QLD_2x    |   5 |   2 |    1.2423 | 0.3158 |   1.0014 | -0.4647 |   0.6795 | px_gt_ema20|px_gt_ema50|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55      |
| QQQ      | QLD_2x    |   5 |   2 |    1.2422 | 0.3152 |   1.0095 | -0.3808 |   0.8279 | px_gt_sma20|px_gt_ema100|sma50_gt_sma150|rv21_pct_lt_70|ar1_30_gt_0           |
| QQQ      | QLD_2x    |   5 |   1 |    1.2421 | 0.3335 |   0.9749 | -0.5096 |   0.6545 | px_gt_sma50|px_gt_sma150|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0               |
| QQQ      | QLD_2x    |   5 |   2 |    1.2421 | 0.3211 |   0.9865 | -0.5830 |   0.5508 | px_gt_sma20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0                  |
| QQQ      | QLD_2x    |   5 |   3 |    1.2419 | 0.3175 |   1.0157 | -0.5601 |   0.5669 | roc10_gt_0|roc120_gt_0|rv21_pct_lt_70|adx14_gt_20|atr14_pct_lt_3              |
| QQQ      | QLD_2x    |   5 |   2 |    1.2416 | 0.3155 |   1.0195 | -0.5714 |   0.5522 | px_gt_ema20|roc20_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70            |
| QQQ      | QLD_2x    |   5 |   2 |    1.2416 | 0.3197 |   0.9914 | -0.5333 |   0.5994 | px_gt_sma20|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0             |
| QQQ      | QLD_2x    |   5 |   1 |    1.2415 | 0.3350 |   0.9707 | -0.5109 |   0.6557 | px_gt_ema20|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0|close_gt_prior_high55      |
| QQQ      | QLD_2x    |   4 |   1 |    1.2415 | 0.3350 |   0.9707 | -0.5109 |   0.6557 | px_gt_ema20|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0                            |
| QQQ      | QLD_2x    |   5 |   1 |    1.2415 | 0.3350 |   0.9707 | -0.5109 |   0.6557 | px_gt_ema20|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0|cci20_gt_100               |
| QQQ      | QLD_2x    |   5 |   1 |    1.2415 | 0.3350 |   0.9707 | -0.5109 |   0.6557 | px_gt_ema20|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0|close_gt_prior_high20      |
| QQQ      | QLD_2x    |   5 |   1 |    1.2412 | 0.3353 |   0.9685 | -0.4781 |   0.7014 | px_gt_ema20|px_gt_sma50|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0                |
| QQQ      | QLD_2x    |   5 |   1 |    1.2411 | 0.3368 |   0.9735 | -0.5376 |   0.6265 | px_gt_sma20|px_gt_sma50|roc120_gt_0|ar1_30_gt_0|bear_power_gt_0               |
| QQQ      | QLD_2x    |   5 |   2 |    1.2411 | 0.3212 |   0.9824 | -0.6223 |   0.5161 | px_gt_sma20|px_gt_sma200|roc10_gt_0|rv21_pct_lt_70|atr14_pct_lt_3             |
| QQQ      | QLD_2x    |   5 |   1 |    1.2410 | 0.3329 |   0.9743 | -0.5422 |   0.6139 | px_gt_sma50|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0|close_gt_prior_high20      |
| QQQ      | QLD_2x    |   5 |   1 |    1.2410 | 0.3329 |   0.9743 | -0.5422 |   0.6139 | px_gt_sma50|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0|close_gt_prior_high55      |
| QQQ      | QLD_2x    |   4 |   1 |    1.2410 | 0.3329 |   0.9743 | -0.5422 |   0.6139 | px_gt_sma50|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0                            |
| QQQ      | QLD_2x    |   5 |   1 |    1.2406 | 0.3368 |   0.9722 | -0.5077 |   0.6633 | px_gt_ema20|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0|bear_power_gt_0            |
| QQQ      | QLD_2x    |   5 |   2 |    1.2406 | 0.3279 |   0.9679 | -0.5290 |   0.6198 | roc10_gt_0|roc120_gt_0|rv21_lt_40|ar1_30_gt_0|cci20_gt_0                      |
| QQQ      | QLD_2x    |   5 |   2 |    1.2402 | 0.3210 |   0.9923 | -0.5635 |   0.5697 | px_gt_sma20|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0                  |
| QQQ      | QLD_2x    |   5 |   2 |    1.2402 | 0.3239 |   0.9804 | -0.5810 |   0.5575 | roc10_gt_0|roc20_gt_0|roc120_gt_0|rv21_lt_40|cci20_gt_0                       |
| QQQ      | QLD_2x    |   5 |   2 |    1.2398 | 0.3109 |   1.0067 | -0.3920 |   0.7930 | px_gt_ema50|px_gt_ema100|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55     |
| QQQ      | QLD_2x    |   4 |   2 |    1.2398 | 0.3109 |   1.0067 | -0.3920 |   0.7930 | px_gt_ema50|px_gt_ema100|roc120_gt_0|atr14_pct_lt_3                           |
| QQQ      | QLD_2x    |   5 |   2 |    1.2395 | 0.3236 |   0.9793 | -0.5989 |   0.5403 | px_gt_sma20|roc10_gt_0|roc20_gt_0|roc120_gt_0|rv21_lt_40                      |
| QQQ      | QLD_2x    |   5 |   2 |    1.2388 | 0.3086 |   0.9973 | -0.3920 |   0.7871 | px_gt_ema50|px_gt_ema100|roc120_gt_0|rv21_pct_lt_50|atr14_pct_lt_3            |
| QQQ      | QLD_2x    |   5 |   2 |    1.2387 | 0.3174 |   1.0126 | -0.3951 |   0.8033 | px_gt_ema100|sma50_gt_sma200|roc20_gt_0|rv21_pct_lt_70|ar1_30_gt_0            |
| QQQ      | QLD_2x    |   5 |   1 |    1.2385 | 0.3358 |   0.9717 | -0.5376 |   0.6246 | px_gt_sma20|px_gt_ema20|px_gt_sma50|roc120_gt_0|ar1_30_gt_0                   |
| QQQ      | QLD_2x    |   5 |   3 |    1.2384 | 0.3155 |   1.0099 | -0.4477 |   0.7048 | px_gt_sma20|roc10_gt_0|roc120_gt_0|adx14_gt_20|atr14_pct_lt_3                 |
| QQQ      | QLD_2x    |   5 |   3 |    1.2382 | 0.3133 |   1.0178 | -0.5555 |   0.5640 | px_gt_ema20|px_gt_sma200|rv21_pct_lt_70|adx14_gt_20|atr14_pct_lt_3            |
| QQQ      | QLD_2x    |   5 |   2 |    1.2382 | 0.3396 |   0.9982 | -0.5512 |   0.6162 | px_gt_ema20|roc10_gt_0|roc120_gt_0|rv21_pct_lt_70|adx14_gt_20                 |
| QQQ      | QLD_2x    |   5 |   2 |    1.2382 | 0.3150 |   0.9905 | -0.5054 |   0.6232 | px_gt_ema100|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0            |
| QQQ      | QLD_2x    |   5 |   3 |    1.2381 | 0.3136 |   1.0009 | -0.5054 |   0.6206 | roc20_gt_0|roc120_gt_0|rv21_lt_40|atr14_pct_lt_3|bear_power_gt_0              |
| QQQ      | QLD_2x    |   5 |   2 |    1.2377 | 0.3153 |   0.9877 | -0.5328 |   0.5918 | px_gt_sma20|px_gt_ema20|px_gt_ema50|roc120_gt_0|atr14_pct_lt_3                |
| QQQ      | QLD_2x    |   5 |   2 |    1.2375 | 0.3129 |   1.0130 | -0.4567 |   0.6851 | px_gt_ema5|px_gt_ema20|roc20_gt_0|roc120_gt_0|rv21_pct_lt_70                  |
| QQQ      | QLD_2x    |   4 |   2 |    1.2374 | 0.3183 |   0.9925 | -0.5283 |   0.6025 | px_gt_sma20|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0                             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2374 | 0.3183 |   0.9925 | -0.5283 |   0.6025 | px_gt_sma20|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0|close_gt_prior_high55       |
| QQQ      | QLD_2x    |   5 |   2 |    1.2374 | 0.3183 |   0.9925 | -0.5283 |   0.6025 | px_gt_sma20|roc120_gt_0|atr14_pct_lt_3|cci20_gt_0|close_gt_prior_high20       |
| QQQ      | QLD_2x    |   5 |   3 |    1.2372 | 0.3203 |   0.9890 | -0.5824 |   0.5499 | px_gt_ema20|roc20_gt_0|roc120_gt_0|rv21_lt_40|atr14_pct_lt_5                  |
| QQQ      | QLD_2x    |   5 |   2 |    1.2370 | 0.3143 |   0.9911 | -0.5522 |   0.5693 | px_gt_ema50|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2369 | 0.3383 |   0.9866 | -0.5881 |   0.5752 | px_gt_sma20|roc20_gt_0|roc120_gt_0|ar1_30_gt_0|adx14_gt_20                    |
| QQQ      | QLD_2x    |   5 |   2 |    1.2366 | 0.3143 |   0.9921 | -0.4988 |   0.6302 | px_gt_sma50|px_gt_ema50|roc120_gt_0|rv21_pct_lt_70|atr14_pct_lt_3             |
| QQQ      | QLD_2x    |   5 |   3 |    1.2363 | 0.3078 |   1.0514 | -0.3341 |   0.9213 | roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70|ar1_30_gt_0|atr14_pct_lt_5        |
| QQQ      | QLD_2x    |   5 |   2 |    1.2362 | 0.3112 |   0.9870 | -0.4688 |   0.6638 | px_gt_ema100|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100               |
| QQQ      | QLD_2x    |   5 |   2 |    1.2362 | 0.3178 |   0.9912 | -0.5283 |   0.6015 | px_gt_sma20|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80|cci20_gt_0               |
| QQQ      | QLD_2x    |   5 |   2 |    1.2359 | 0.3411 |   0.9487 | -0.5422 |   0.6291 | sma100_gt_sma250|macd_hist_gt_0|roc120_gt_0|ar1_30_gt_0|atr14_pct_lt_5        |
| QQQ      | QLD_2x    |   5 |   1 |    1.2358 | 0.3312 |   0.9700 | -0.5462 |   0.6064 | px_gt_sma50|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0|cci20_gt_100               |
| QQQ      | QLD_2x    |   5 |   2 |    1.2355 | 0.3171 |   0.9936 | -0.5108 |   0.6207 | px_gt_sma20|px_gt_ema20|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0            |
| QQQ      | QLD_2x    |   5 |   1 |    1.2354 | 0.3103 |   1.0055 | -0.4253 |   0.7297 | px_gt_sma50|px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|close_gt_prior_high55     |
| QQQ      | QLD_2x    |   5 |   2 |    1.2354 | 0.3103 |   1.0055 | -0.4253 |   0.7297 | px_gt_sma50|px_gt_ema50|px_gt_ema100|rv21_pct_lt_70|atr14_pct_lt_5            |
| QQQ      | QLD_2x    |   4 |   1 |    1.2354 | 0.3103 |   1.0055 | -0.4253 |   0.7297 | px_gt_sma50|px_gt_ema50|px_gt_ema100|rv21_pct_lt_70                           |
| QQQ      | QLD_2x    |   5 |   2 |    1.2354 | 0.3201 |   0.9853 | -0.5534 |   0.5784 | px_gt_ema20|px_gt_sma200|roc10_gt_0|rv21_pct_lt_70|atr14_pct_lt_3             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2351 | 0.3144 |   0.9890 | -0.4447 |   0.7070 | px_gt_ema50|px_gt_ema100|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3                |
| QQQ      | QLD_2x    |   5 |   2 |    1.2350 | 0.3135 |   0.9952 | -0.4865 |   0.6444 | px_gt_ema20|px_gt_ema50|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100               |
| QQQ      | QLD_2x    |   5 |   2 |    1.2349 | 0.3316 |   0.9919 | -0.5968 |   0.5557 | px_gt_sma20|px_gt_ema20|roc120_gt_0|rv21_pct_lt_70|adx14_gt_20                |
| QQQ      | QLD_2x    |   5 |   2 |    1.2349 | 0.3177 |   0.9896 | -0.5559 |   0.5716 | roc10_gt_0|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55        |
| QQQ      | QLD_2x    |   4 |   2 |    1.2349 | 0.3177 |   0.9896 | -0.5559 |   0.5716 | roc10_gt_0|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                              |
| QQQ      | QLD_2x    |   5 |   2 |    1.2349 | 0.3177 |   0.9896 | -0.5559 |   0.5716 | roc10_gt_0|roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20        |
| QQQ      | QLD_2x    |   4 |   2 |    1.2348 | 0.3138 |   0.9918 | -0.4447 |   0.7056 | px_gt_ema50|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3                             |
| QQQ      | QLD_2x    |   5 |   2 |    1.2348 | 0.3138 |   0.9918 | -0.4447 |   0.7056 | px_gt_ema50|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55       |
| QQQ      | QLD_2x    |   5 |   2 |    1.2348 | 0.3138 |   0.9918 | -0.4447 |   0.7056 | px_gt_ema50|roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20       |
| QQQ      | QLD_2x    |   5 |   2 |    1.2348 | 0.3156 |   0.9989 | -0.4536 |   0.6958 | roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|cci20_gt_100|bear_power_gt_0            |
| QQQ      | QLD_2x    |   5 |   2 |    1.2344 | 0.3156 |   0.9990 | -0.4536 |   0.6957 | roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high20|bear_power_gt_0   |
| QQQ      | QLD_2x    |   5 |   2 |    1.2344 | 0.3156 |   0.9990 | -0.4536 |   0.6957 | roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55|bear_power_gt_0   |
| QQQ      | QLD_2x    |   4 |   2 |    1.2344 | 0.3156 |   0.9990 | -0.4536 |   0.6957 | roc10_gt_0|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0                         |
| QQQ      | QLD_2x    |   5 |   3 |    1.2344 | 0.3121 |   0.9921 | -0.5113 |   0.6104 | px_gt_ema20|roc20_gt_0|roc120_gt_0|rv21_lt_40|atr14_pct_lt_3                  |
| QQQ      | QLD_2x    |   5 |   2 |    1.2341 | 0.3150 |   1.0044 | -0.4585 |   0.6870 | px_gt_ema50|px_gt_ema100|px_gt_sma200|rv21_pct_lt_70|atr14_pct_lt_3           |
| QQQ      | QLD_2x    |   5 |   1 |    1.2341 | 0.3304 |   0.9683 | -0.5199 |   0.6355 | px_gt_sma50|px_gt_ema150|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0               |
| QQQ      | QLD_2x    |   5 |   3 |    1.2339 | 0.3132 |   1.0099 | -0.5504 |   0.5691 | px_gt_ema20|roc20_gt_0|roc120_gt_0|adx14_gt_20|atr14_pct_lt_3                 |
| QQQ      | QLD_2x    |   5 |   1 |    1.2335 | 0.3333 |   0.9595 | -0.5253 |   0.6346 | px_gt_sma20|px_gt_sma50|roc120_gt_0|rv21_pct_lt_70|ar1_30_gt_0                |
| QQQ      | QLD_2x    |   3 |   2 |    1.2334 | 0.3099 |   0.9979 | -0.4901 |   0.6324 | roc20_gt_0|roc120_gt_0|atr14_pct_lt_3                                         |
| QQQ      | QLD_2x    |   4 |   2 |    1.2334 | 0.3099 |   0.9979 | -0.4901 |   0.6324 | roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|close_gt_prior_high55                   |
| QQQ      | QLD_2x    |   5 |   2 |    1.2330 | 0.3142 |   0.9813 | -0.5510 |   0.5702 | px_gt_sma20|px_gt_ema20|px_gt_ema100|roc120_gt_0|atr14_pct_lt_3               |
| QQQ      | QLD_2x    |   5 |   2 |    1.2330 | 0.3160 |   0.9942 | -0.5591 |   0.5651 | roc20_gt_0|roc120_gt_0|atr14_pct_lt_3|stoch14_gt_80|bear_power_gt_0           |
| QQQ      | QLD_2x    |   5 |   2 |    1.2327 | 0.3167 |   0.9948 | -0.5620 |   0.5635 | px_gt_ema20|px_gt_sma50|roc120_gt_0|atr14_pct_lt_3|bear_power_gt_0            |
| QQQ      | QLD_2x    |   5 |   1 |    1.2326 | 0.3337 |   0.9708 | -0.5732 |   0.5822 | px_gt_sma20|px_gt_ema20|roc120_gt_0|ar1_30_gt_0|stoch14_gt_80                 |
| QQQ      | QLD_2x    |   5 |   1 |    1.2326 | 0.3337 |   0.9708 | -0.5732 |   0.5822 | px_gt_sma20|px_gt_ema20|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high55         |
| QQQ      | QLD_2x    |   5 |   1 |    1.2326 | 0.3337 |   0.9708 | -0.5732 |   0.5822 | px_gt_sma20|px_gt_ema20|roc120_gt_0|ar1_30_gt_0|cci20_gt_100                  |
| QQQ      | QLD_2x    |   5 |   1 |    1.2326 | 0.3337 |   0.9708 | -0.5732 |   0.5822 | px_gt_sma20|px_gt_ema20|roc120_gt_0|ar1_30_gt_0|close_gt_prior_high20         |

## Method Notes

- Top rows are retained by Sortino, then CAGR, then Calmar.
- Signals are lagged one base bar before returns to avoid same-close look-ahead; `extra_lag_days` adds operational execution delay `[advances_fin_ml, p.31-34]`.
- Redundant signal groups are excluded by default, including equivalent MACD forms and nested thresholds.
- All evaluated configs must be included in later DSR trial accounting `[advances_fin_ml, p.222-223]`.
