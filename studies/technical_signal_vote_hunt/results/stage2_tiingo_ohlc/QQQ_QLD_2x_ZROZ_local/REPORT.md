# Stage 2 Tiingo OHLC Local Results

Status: real-inception Tiingo OHLC diagnostic. This is not a validation verdict.

Branch: `QQQ`
Risk-on: `QLD_2x` (`QLD`)
Off leg: `ZROZ`
Window: `2009-11-05` to `2026-04-14` (4,133 bars)
Signals: 47 total, 14 OHLC-derived
Configs tested: 847
Elapsed seconds: 0.5

## Base Replay

| neighborhood   | change   |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                              |
|:---------------|:---------|----:|----:|----------:|-------:|---------:|--------:|---------:|:-------------------------------------------------------------------------------------|
| base           | none     |   7 |   5 |    1.2775 | 0.2631 |   0.9365 | -0.5644 |   0.4661 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0 |

## Top Local Candidates

| neighborhood   | change                              |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                                                    |
|:---------------|:------------------------------------|----:|----:|----------:|-------:|---------:|--------:|---------:|:-----------------------------------------------------------------------------------------------------------|
| add1_ohlc      | +atr14_pct_lt_3                     |   8 |   6 |    1.2870 | 0.2638 |   0.9418 | -0.5644 |   0.4675 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|atr14_pct_lt_3        |
| swap1_ohlc     | -px_gt_ema100+atr14_pct_lt_3        |   7 |   5 |    1.2804 | 0.2647 |   0.9365 | -0.5405 |   0.4898 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|atr14_pct_lt_3                     |
| swap1_ohlc     | -px_gt_sma10+bear_power_gt_0        |   7 |   5 |    1.2798 | 0.2590 |   0.9356 | -0.5565 |   0.4653 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|bear_power_gt_0                   |
| swap1_ohlc     | -px_gt_sma10+cci20_gt_100           |   7 |   5 |    1.2784 | 0.2560 |   0.9301 | -0.5849 |   0.4377 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|cci20_gt_100                      |
| base           | none                                |   7 |   5 |    1.2775 | 0.2631 |   0.9365 | -0.5644 |   0.4661 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                       |
| add1_ohlc      | +atr14_pct_lt_5                     |   8 |   6 |    1.2775 | 0.2631 |   0.9365 | -0.5644 |   0.4661 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|atr14_pct_lt_5        |
| swap1_ohlc     | -px_gt_ema100+stoch14_gt_80         |   7 |   4 |    1.2701 | 0.2667 |   0.9354 | -0.5902 |   0.4519 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|stoch14_gt_80                      |
| add1_ohlc      | +close_gt_prior_high55              |   8 |   5 |    1.2669 | 0.2602 |   0.9291 | -0.5803 |   0.4484 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|close_gt_prior_high55 |
| swap1_ohlc     | -px_gt_sma10+stoch14_gt_80          |   7 |   5 |    1.2607 | 0.2532 |   0.9224 | -0.5849 |   0.4329 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|stoch14_gt_80                     |
| swap1_ohlc     | -px_gt_sma10+cci20_gt_0             |   7 |   5 |    1.2537 | 0.2541 |   0.9191 | -0.5790 |   0.4388 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|cci20_gt_0                        |
| swap1_ohlc     | -px_gt_ema100+cci20_gt_100          |   7 |   4 |    1.2463 | 0.2601 |   0.9180 | -0.5851 |   0.4446 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|cci20_gt_100                       |
| add1_ohlc      | +close_gt_prior_high20              |   8 |   5 |    1.2456 | 0.2545 |   0.9135 | -0.5803 |   0.4386 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|close_gt_prior_high20 |
| add1_ohlc      | +adx14_gt_20                        |   8 |   6 |    1.2440 | 0.2518 |   0.9143 | -0.5565 |   0.4524 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|adx14_gt_20           |
| swap1_ohlc     | -px_gt_sma10+close_gt_prior_high55  |   7 |   5 |    1.2395 | 0.2461 |   0.9052 | -0.5773 |   0.4263 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|close_gt_prior_high55             |
| swap1_ohlc     | -px_gt_ema250+atr14_pct_lt_3        |   7 |   5 |    1.2349 | 0.2506 |   0.9044 | -0.5942 |   0.4217 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0|atr14_pct_lt_3                     |
| drop1          | -px_gt_ema100                       |   6 |   4 |    1.2320 | 0.2554 |   0.9073 | -0.5839 |   0.4375 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                                    |
| swap1_ohlc     | -px_gt_ema100+atr14_pct_lt_5        |   7 |   5 |    1.2308 | 0.2551 |   0.9063 | -0.5839 |   0.4369 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|atr14_pct_lt_5                     |
| drop1          | -px_gt_sma10                        |   6 |   5 |    1.2305 | 0.2438 |   0.8987 | -0.5898 |   0.4134 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                                   |
| swap1_ohlc     | -px_gt_sma10+atr14_pct_lt_5         |   7 |   6 |    1.2305 | 0.2438 |   0.8987 | -0.5898 |   0.4134 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|atr14_pct_lt_5                    |
| swap1_ohlc     | -px_gt_ema200+atr14_pct_lt_3        |   7 |   5 |    1.2271 | 0.2491 |   0.8995 | -0.5720 |   0.4355 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0|atr14_pct_lt_3                     |
| swap1_ohlc     | -px_gt_sma10+atr14_pct_lt_3         |   7 |   6 |    1.2261 | 0.2414 |   0.8960 | -0.5898 |   0.4093 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|atr14_pct_lt_3                    |
| drop1          | -px_gt_ema250                       |   6 |   4 |    1.2259 | 0.2498 |   0.8993 | -0.5942 |   0.4204 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0                                    |
| swap1_ohlc     | -px_gt_ema250+atr14_pct_lt_5        |   7 |   5 |    1.2259 | 0.2498 |   0.8993 | -0.5942 |   0.4204 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0|atr14_pct_lt_5                     |
| swap1_ohlc     | -px_gt_ema250+close_gt_prior_high55 |   7 |   4 |    1.2259 | 0.2498 |   0.8993 | -0.5942 |   0.4204 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0|close_gt_prior_high55              |
| swap1_ohlc     | -px_gt_ema200+cci20_gt_100          |   7 |   4 |    1.2240 | 0.2507 |   0.8988 | -0.5725 |   0.4379 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0|cci20_gt_100                       |
| drop1          | -px_gt_ema200                       |   6 |   4 |    1.2231 | 0.2498 |   0.8985 | -0.5720 |   0.4368 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0                                    |
| swap1_ohlc     | -px_gt_ema200+close_gt_prior_high55 |   7 |   4 |    1.2231 | 0.2498 |   0.8985 | -0.5720 |   0.4368 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0|close_gt_prior_high55              |
| swap1_ohlc     | -px_gt_ema200+atr14_pct_lt_5        |   7 |   5 |    1.2219 | 0.2494 |   0.8975 | -0.5720 |   0.4361 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0|atr14_pct_lt_5                     |
| swap1_ohlc     | -px_gt_ema100+close_gt_prior_high55 |   7 |   4 |    1.2216 | 0.2526 |   0.9000 | -0.5990 |   0.4217 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|close_gt_prior_high55              |
| swap1_ohlc     | -px_gt_ema100+bear_power_gt_0       |   7 |   4 |    1.2191 | 0.2529 |   0.8972 | -0.6616 |   0.3822 | px_gt_sma10|px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|bear_power_gt_0                    |

## Method Notes

- Tiingo OHLC is adjusted with `adj_close / close` before high/low indicators `[quant_trading_chan, p.37]`.
- Vote signals are lagged one bar before earning returns to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.
- This is local discovery on a shorter real-ETF window; final claims still require DSR/PBO/WF/OOS/FWD/bootstrap `[advances_fin_ml, p.208-211]`.
