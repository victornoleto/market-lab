# Stage 2 Tiingo OHLC Local Results

Status: real-inception Tiingo OHLC diagnostic. This is not a validation verdict.

Branch: `QQQ`
Risk-on: `TQQQ_3x` (`TQQQ`)
Off leg: `ZROZ`
Window: `2010-02-12` to `2026-04-14` (4,066 bars)
Signals: 47 total, 14 OHLC-derived
Configs tested: 1,086
Elapsed seconds: 0.5

## Base Replay

| neighborhood   | change   |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                                          |
|:---------------|:---------|----:|----:|----------:|-------:|---------:|--------:|---------:|:-------------------------------------------------------------------------------------------------|
| base           | none     |   8 |   6 |    1.2337 | 0.3475 |   0.9444 | -0.6536 |   0.5317 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0 |

## Top Local Candidates

| neighborhood   | change                              |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                                                                |
|:---------------|:------------------------------------|----:|----:|----------:|-------:|---------:|--------:|---------:|:-----------------------------------------------------------------------------------------------------------------------|
| swap1_ohlc     | -roc120_gt_0+atr14_pct_lt_3         |   8 |   6 |    1.3307 | 0.3877 |   1.0141 | -0.6206 |   0.6247 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|atr14_pct_lt_3                    |
| drop1          | -roc120_gt_0                        |   7 |   5 |    1.3168 | 0.3849 |   1.0052 | -0.6206 |   0.6202 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0                                   |
| swap1_ohlc     | -roc120_gt_0+atr14_pct_lt_5         |   8 |   6 |    1.3168 | 0.3849 |   1.0052 | -0.6206 |   0.6202 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|atr14_pct_lt_5                    |
| swap1_ohlc     | -roc120_gt_0+close_gt_prior_high55  |   8 |   5 |    1.3093 | 0.3817 |   0.9996 | -0.6345 |   0.6015 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|close_gt_prior_high55             |
| swap1_ohlc     | -roc120_gt_0+close_gt_prior_high20  |   8 |   5 |    1.2898 | 0.3734 |   0.9847 | -0.6345 |   0.5885 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|close_gt_prior_high20             |
| swap1_ohlc     | -px_gt_ema200+atr14_pct_lt_3        |   8 |   6 |    1.2809 | 0.3638 |   0.9744 | -0.5905 |   0.6160 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|atr14_pct_lt_3                     |
| swap1_ohlc     | -px_gt_ema250+atr14_pct_lt_3        |   8 |   6 |    1.2779 | 0.3624 |   0.9724 | -0.5905 |   0.6137 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0|roc120_gt_0|atr14_pct_lt_3                     |
| drop1          | -px_gt_ema200                       |   7 |   5 |    1.2739 | 0.3640 |   0.9711 | -0.5905 |   0.6163 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0                                    |
| swap1_ohlc     | -px_gt_ema200+atr14_pct_lt_5        |   8 |   6 |    1.2727 | 0.3634 |   0.9700 | -0.5905 |   0.6154 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|atr14_pct_lt_5                     |
| drop1          | -px_gt_ema250                       |   7 |   5 |    1.2698 | 0.3620 |   0.9681 | -0.5905 |   0.6131 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0|roc120_gt_0                                    |
| swap1_ohlc     | -px_gt_ema250+atr14_pct_lt_5        |   8 |   6 |    1.2698 | 0.3620 |   0.9681 | -0.5905 |   0.6131 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0|roc120_gt_0|atr14_pct_lt_5                     |
| swap1_ohlc     | -roc120_gt_0+adx14_gt_20            |   8 |   6 |    1.2687 | 0.3610 |   0.9730 | -0.6099 |   0.5919 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|adx14_gt_20                       |
| swap1_ohlc     | -px_gt_sma10+stoch14_gt_80          |   8 |   6 |    1.2677 | 0.3518 |   0.9675 | -0.6438 |   0.5465 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|stoch14_gt_80                     |
| swap1_ohlc     | -px_gt_ema200+close_gt_prior_high55 |   8 |   5 |    1.2663 | 0.3608 |   0.9655 | -0.6056 |   0.5958 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|close_gt_prior_high55              |
| add1_ohlc      | +cci20_gt_100                       |   9 |   6 |    1.2657 | 0.3599 |   0.9646 | -0.6535 |   0.5508 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|cci20_gt_100          |
| swap1_ohlc     | -px_gt_ema250+close_gt_prior_high55 |   8 |   5 |    1.2622 | 0.3589 |   0.9625 | -0.6056 |   0.5926 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0|roc120_gt_0|close_gt_prior_high55              |
| swap1_ohlc     | -px_gt_ema250+close_gt_prior_high20 |   8 |   5 |    1.2590 | 0.3576 |   0.9599 | -0.6345 |   0.5636 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0|roc120_gt_0|close_gt_prior_high20              |
| swap1_ohlc     | -px_gt_ema200+close_gt_prior_high20 |   8 |   5 |    1.2501 | 0.3543 |   0.9531 | -0.6345 |   0.5584 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|close_gt_prior_high20              |
| add1_ohlc      | +atr14_pct_lt_3                     |   9 |   7 |    1.2416 | 0.3479 |   0.9486 | -0.6536 |   0.5323 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|atr14_pct_lt_3        |
| swap1_ohlc     | -roc60_gt_0+ultosc_gt_50            |   8 |   3 |    1.2406 | 0.4168 |   0.9467 | -0.6725 |   0.6197 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc120_gt_0|ultosc_gt_50                     |
| add1_ohlc      | +close_gt_prior_high55              |   9 |   6 |    1.2392 | 0.3498 |   0.9486 | -0.6440 |   0.5432 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|close_gt_prior_high55 |
| swap1_ohlc     | -px_gt_ema250+cci20_gt_100          |   8 |   5 |    1.2361 | 0.3480 |   0.9420 | -0.6298 |   0.5526 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|roc20_gt_0|roc60_gt_0|roc120_gt_0|cci20_gt_100                       |
| base           | none                                |   8 |   6 |    1.2337 | 0.3475 |   0.9444 | -0.6536 |   0.5317 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0                       |
| add1_ohlc      | +atr14_pct_lt_5                     |   9 |   7 |    1.2337 | 0.3475 |   0.9444 | -0.6536 |   0.5317 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|atr14_pct_lt_5        |
| swap1_ohlc     | -px_gt_sma10+bear_power_gt_0        |   8 |   6 |    1.2324 | 0.3391 |   0.9410 | -0.6438 |   0.5267 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|bear_power_gt_0                   |
| swap1_ohlc     | -roc120_gt_0+cci20_gt_100           |   8 |   5 |    1.2314 | 0.3494 |   0.9404 | -0.6008 |   0.5815 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|cci20_gt_100                      |
| swap1_ohlc     | -px_gt_sma10+cci20_gt_0             |   8 |   6 |    1.2261 | 0.3392 |   0.9372 | -0.6438 |   0.5269 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|cci20_gt_0                        |
| add1_ohlc      | +close_gt_prior_high20              |   9 |   6 |    1.2210 | 0.3423 |   0.9347 | -0.6701 |   0.5108 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|close_gt_prior_high20 |
| swap1_ohlc     | -px_gt_sma20+adx14_gt_25            |   8 |   1 |    1.2176 | 0.4669 |   0.9419 | -0.7922 |   0.5894 | px_gt_sma10|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|adx14_gt_25                       |
| swap1_ohlc     | -px_gt_ema200+cci20_gt_100          |   8 |   5 |    1.2176 | 0.3415 |   0.9285 | -0.6019 |   0.5674 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|cci20_gt_100                       |

## Method Notes

- Tiingo OHLC is adjusted with `adj_close / close` before high/low indicators `[quant_trading_chan, p.37]`.
- Vote signals are lagged one bar before earning returns to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.
- This is local discovery on a shorter real-ETF window; final claims still require DSR/PBO/WF/OOS/FWD/bootstrap `[advances_fin_ml, p.208-211]`.
