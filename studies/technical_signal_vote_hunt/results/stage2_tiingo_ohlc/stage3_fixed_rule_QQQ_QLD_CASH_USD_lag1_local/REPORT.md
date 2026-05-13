# Stage 2 Tiingo OHLC Local Results

Status: real-inception Tiingo OHLC diagnostic. This is not a validation verdict.

Branch: `QQQ`
Risk-on: `QLD_2x` (`QLD`)
Off leg: `CASH_USD`
Extra lag days: `1`
Window: `2006-06-22` to `2026-04-14` (4,983 bars)
Signals: 47 total, 14 OHLC-derived
Configs tested: 1,086
Elapsed seconds: 0.5

## Base Replay

| neighborhood   | change   |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                                          |
|:---------------|:---------|----:|----:|----------:|-------:|---------:|--------:|---------:|:-------------------------------------------------------------------------------------------------|
| base           | none     |   8 |   6 |    0.8687 | 0.1909 |   0.8269 | -0.3982 |   0.4795 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50 |

## Top Local Candidates

| neighborhood   | change                              |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                                                         |
|:---------------|:------------------------------------|----:|----:|----------:|-------:|---------:|--------:|---------:|:----------------------------------------------------------------------------------------------------------------|
| swap1_ohlc     | -px_gt_ema250+atr14_pct_lt_3        |   8 |   5 |    1.0600 | 0.2505 |   0.9066 | -0.3936 |   0.6365 | px_gt_sma10|px_gt_ema200|px_gt_sma250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3              |
| swap1_ohlc     | -px_gt_ema200+atr14_pct_lt_3        |   8 |   5 |    1.0587 | 0.2499 |   0.9034 | -0.3945 |   0.6336 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3              |
| swap1_ohlc     | -px_gt_sma250+adx14_gt_20           |   8 |   5 |    1.0475 | 0.2540 |   0.9155 | -0.4185 |   0.6070 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20                 |
| swap1_ohlc     | -px_gt_sma250+atr14_pct_lt_3        |   8 |   5 |    1.0474 | 0.2461 |   0.8940 | -0.3945 |   0.6239 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3              |
| swap1_ohlc     | -px_gt_ema200+adx14_gt_20           |   8 |   5 |    1.0429 | 0.2533 |   0.9119 | -0.4185 |   0.6052 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20                 |
| swap1_ohlc     | -px_gt_ema200+atr14_pct_lt_3        |   8 |   4 |    1.0405 | 0.2530 |   0.8580 | -0.5889 |   0.4296 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3              |
| swap1_ohlc     | -roc120_gt_0+adx14_gt_25            |   8 |   5 |    1.0382 | 0.2504 |   0.9204 | -0.4233 |   0.5916 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|adx14_gt_25                |
| swap1_ohlc     | -px_gt_sma250+atr14_pct_lt_3        |   8 |   4 |    1.0379 | 0.2512 |   0.8546 | -0.5889 |   0.4265 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3              |
| swap1_ohlc     | -px_gt_ema250+adx14_gt_20           |   8 |   5 |    1.0337 | 0.2499 |   0.9050 | -0.4177 |   0.5984 | px_gt_sma10|px_gt_ema200|px_gt_sma250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20                 |
| swap1_ohlc     | -roc120_gt_0+atr14_pct_lt_3         |   8 |   5 |    1.0255 | 0.2393 |   0.8751 | -0.3602 |   0.6642 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|atr14_pct_lt_3             |
| add1_ohlc      | +atr14_pct_lt_3                     |   9 |   5 |    1.0231 | 0.2471 |   0.8595 | -0.4763 |   0.5188 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3 |
| swap1_ohlc     | -px_gt_ema250+atr14_pct_lt_3        |   8 |   4 |    1.0223 | 0.2466 |   0.8459 | -0.5455 |   0.4521 | px_gt_sma10|px_gt_ema200|px_gt_sma250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3              |
| swap1_ohlc     | -px_gt_ema200+atr14_pct_lt_5        |   8 |   4 |    1.0223 | 0.2532 |   0.8495 | -0.6133 |   0.4129 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_5              |
| swap1_ohlc     | -roc60_gt_0+atr14_pct_lt_3          |   8 |   5 |    1.0214 | 0.2435 |   0.8642 | -0.5248 |   0.4639 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3            |
| swap1_ohlc     | -rsi14_gt_50+ultosc_gt_50           |   8 |   4 |    1.0190 | 0.2538 |   0.8671 | -0.4428 |   0.5730 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|ultosc_gt_50               |
| swap1_ohlc     | -px_gt_ema200+cci20_gt_0            |   8 |   3 |    1.0171 | 0.2541 |   0.8384 | -0.6039 |   0.4207 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|cci20_gt_0                  |
| swap1_ohlc     | -roc120_gt_0+adx14_gt_20            |   8 |   5 |    1.0154 | 0.2430 |   0.8857 | -0.4513 |   0.5383 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|adx14_gt_20                |
| swap1_ohlc     | -px_gt_sma250+atr14_pct_lt_5        |   8 |   4 |    1.0147 | 0.2503 |   0.8433 | -0.6049 |   0.4138 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_5              |
| swap1_ohlc     | -px_gt_sma10+atr14_pct_lt_5         |   8 |   1 |    1.0147 | 0.2645 |   0.7786 | -0.7845 |   0.3372 | px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_5             |
| swap1_ohlc     | -px_gt_sma250+adx14_gt_25           |   8 |   5 |    1.0144 | 0.2450 |   0.9052 | -0.4196 |   0.5839 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_25                 |
| swap1_ohlc     | -px_gt_sma250+cci20_gt_0            |   8 |   3 |    1.0143 | 0.2528 |   0.8361 | -0.5942 |   0.4254 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|cci20_gt_0                  |
| swap1_ohlc     | -px_gt_ema200+bull_power_gt_0       |   8 |   4 |    1.0114 | 0.2427 |   0.8473 | -0.5480 |   0.4429 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|bull_power_gt_0             |
| swap1_ohlc     | -rsi14_gt_50+stoch14_gt_50          |   8 |   4 |    1.0068 | 0.2501 |   0.8573 | -0.4803 |   0.5207 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|stoch14_gt_50              |
| swap1_ohlc     | -rsi14_gt_50+willr14_gt_m50         |   8 |   4 |    1.0068 | 0.2501 |   0.8573 | -0.4803 |   0.5207 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|willr14_gt_m50             |
| swap1_ohlc     | -rsi14_gt_50+atr14_pct_lt_3         |   8 |   5 |    1.0054 | 0.2420 |   0.8544 | -0.4642 |   0.5214 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|atr14_pct_lt_3             |
| add1_ohlc      | +atr14_pct_lt_3                     |   9 |   6 |    1.0054 | 0.2342 |   0.8698 | -0.3571 |   0.6560 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3 |
| swap1_ohlc     | -px_gt_ema250+cci20_gt_0            |   8 |   3 |    1.0043 | 0.2493 |   0.8310 | -0.5846 |   0.4264 | px_gt_sma10|px_gt_ema200|px_gt_sma250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|cci20_gt_0                  |
| swap1_ohlc     | -roc120_gt_0+bear_power_gt_0        |   8 |   5 |    1.0032 | 0.2291 |   0.9273 | -0.4240 |   0.5404 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|bear_power_gt_0            |
| swap1_ohlc     | -rsi14_gt_50+cci20_gt_0             |   8 |   2 |    1.0005 | 0.2527 |   0.8180 | -0.6541 |   0.3863 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|cci20_gt_0                 |
| drop1          | -px_gt_ema200                       |   7 |   3 |    0.9999 | 0.2470 |   0.8332 | -0.6133 |   0.4026 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50                             |
| swap1_ohlc     | -px_gt_ema200+close_gt_prior_high20 |   8 |   3 |    0.9999 | 0.2470 |   0.8332 | -0.6133 |   0.4026 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|close_gt_prior_high20       |
| swap1_ohlc     | -px_gt_ema200+close_gt_prior_high55 |   8 |   3 |    0.9999 | 0.2470 |   0.8332 | -0.6133 |   0.4026 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|close_gt_prior_high55       |
| swap1_ohlc     | -roc60_gt_0+adx14_gt_20             |   8 |   5 |    0.9993 | 0.2474 |   0.8762 | -0.4982 |   0.4966 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20               |
| swap1_ohlc     | -rsi14_gt_50+bull_power_gt_0        |   8 |   2 |    0.9958 | 0.2534 |   0.8061 | -0.6577 |   0.3852 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|bull_power_gt_0            |
| swap1_ohlc     | -px_gt_sma250+bull_power_gt_0       |   8 |   4 |    0.9948 | 0.2374 |   0.8346 | -0.5381 |   0.4411 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|bull_power_gt_0             |
| swap1_ohlc     | -px_gt_ema200+adx14_gt_20           |   8 |   4 |    0.9938 | 0.2448 |   0.8341 | -0.6020 |   0.4066 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20                 |
| swap1_ohlc     | -roc20_gt_0+atr14_pct_lt_5          |   8 |   3 |    0.9934 | 0.2458 |   0.8158 | -0.6399 |   0.3842 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_5            |
| swap1_ohlc     | -px_gt_ema250+adx14_gt_20           |   8 |   4 |    0.9923 | 0.2445 |   0.8363 | -0.5503 |   0.4443 | px_gt_sma10|px_gt_ema200|px_gt_sma250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20                 |
| drop1          | -px_gt_sma250                       |   7 |   3 |    0.9923 | 0.2440 |   0.8271 | -0.6049 |   0.4034 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50                             |
| swap1_ohlc     | -px_gt_sma250+close_gt_prior_high20 |   8 |   3 |    0.9923 | 0.2440 |   0.8271 | -0.6049 |   0.4034 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|close_gt_prior_high20       |

## Method Notes

- Tiingo OHLC is adjusted with `adj_close / close` before high/low indicators `[quant_trading_chan, p.37]`.
- Vote signals are lagged one bar before earning returns to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.
- This is local discovery on a shorter real-ETF window; final claims still require DSR/PBO/WF/OOS/FWD/bootstrap `[advances_fin_ml, p.208-211]`.
