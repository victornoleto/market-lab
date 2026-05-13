# Stage 2 Tiingo OHLC Local Results

Status: real-inception Tiingo OHLC diagnostic. This is not a validation verdict.

Branch: `QQQ`
Risk-on: `QLD_2x` (`QLD`)
Off leg: `CASH_USD`
Extra lag days: `1`
Window: `2010-02-12` to `2026-04-14` (4,066 bars)
Signals: 47 total, 14 OHLC-derived
Configs tested: 1,086
Elapsed seconds: 0.5

## Base Replay

| neighborhood   | change   |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                                          |
|:---------------|:---------|----:|----:|----------:|-------:|---------:|--------:|---------:|:-------------------------------------------------------------------------------------------------|
| base           | none     |   8 |   6 |    0.9697 | 0.2163 |   0.9034 | -0.3982 |   0.5433 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50 |

## Top Local Candidates

| neighborhood   | change                        |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                                                         |
|:---------------|:------------------------------|----:|----:|----------:|-------:|---------:|--------:|---------:|:----------------------------------------------------------------------------------------------------------------|
| swap1_ohlc     | -rsi14_gt_50+atr14_pct_lt_5   |   8 |   1 |    1.2058 | 0.3351 |   0.9188 | -0.6368 |   0.5262 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|atr14_pct_lt_5             |
| add1_ohlc      | +atr14_pct_lt_5               |   9 |   1 |    1.1999 | 0.3325 |   0.9139 | -0.6368 |   0.5221 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_5 |
| swap1_ohlc     | -px_gt_ema200+atr14_pct_lt_5  |   8 |   1 |    1.1999 | 0.3325 |   0.9139 | -0.6368 |   0.5221 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_5              |
| swap1_ohlc     | -px_gt_sma250+atr14_pct_lt_5  |   8 |   1 |    1.1999 | 0.3325 |   0.9139 | -0.6368 |   0.5221 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_5              |
| swap1_ohlc     | -px_gt_ema250+atr14_pct_lt_5  |   8 |   1 |    1.1999 | 0.3325 |   0.9139 | -0.6368 |   0.5221 | px_gt_sma10|px_gt_ema200|px_gt_sma250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_5              |
| swap1_ohlc     | -roc20_gt_0+atr14_pct_lt_5    |   8 |   1 |    1.1999 | 0.3325 |   0.9139 | -0.6368 |   0.5221 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_5            |
| swap1_ohlc     | -roc60_gt_0+atr14_pct_lt_5    |   8 |   1 |    1.1999 | 0.3325 |   0.9139 | -0.6368 |   0.5221 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_5            |
| swap1_ohlc     | -roc120_gt_0+adx14_gt_25      |   8 |   5 |    1.1839 | 0.2928 |   1.0312 | -0.3445 |   0.8498 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|adx14_gt_25                |
| swap1_ohlc     | -px_gt_sma10+atr14_pct_lt_5   |   8 |   1 |    1.1759 | 0.3233 |   0.9006 | -0.6368 |   0.5076 | px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_5             |
| swap1_ohlc     | -roc120_gt_0+atr14_pct_lt_5   |   8 |   1 |    1.1727 | 0.3221 |   0.8962 | -0.6368 |   0.5058 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|atr14_pct_lt_5             |
| swap1_ohlc     | -px_gt_sma250+adx14_gt_20     |   8 |   5 |    1.1628 | 0.2872 |   0.9985 | -0.4185 |   0.6862 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20                 |
| swap1_ohlc     | -roc120_gt_0+bear_power_gt_0  |   8 |   5 |    1.1622 | 0.2695 |   1.0512 | -0.2739 |   0.9841 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|bear_power_gt_0            |
| swap1_ohlc     | -roc120_gt_0+adx14_gt_20      |   8 |   5 |    1.1571 | 0.2839 |   0.9895 | -0.3445 |   0.8239 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|adx14_gt_20                |
| swap1_ohlc     | -px_gt_ema200+adx14_gt_20     |   8 |   5 |    1.1566 | 0.2863 |   0.9940 | -0.4185 |   0.6840 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20                 |
| swap1_ohlc     | -px_gt_ema200+atr14_pct_lt_3  |   8 |   5 |    1.1559 | 0.2768 |   0.9687 | -0.3945 |   0.7017 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3              |
| swap1_ohlc     | -px_gt_sma250+atr14_pct_lt_3  |   8 |   5 |    1.1420 | 0.2720 |   0.9573 | -0.3945 |   0.6896 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3              |
| swap1_ohlc     | -px_gt_ema250+atr14_pct_lt_3  |   8 |   5 |    1.1353 | 0.2705 |   0.9542 | -0.3936 |   0.6873 | px_gt_sma10|px_gt_ema200|px_gt_sma250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3              |
| swap1_ohlc     | -rsi14_gt_50+adx14_gt_20      |   8 |   1 |    1.1322 | 0.3196 |   0.8861 | -0.6742 |   0.4741 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|adx14_gt_20                |
| swap1_ohlc     | -roc60_gt_0+adx14_gt_20       |   8 |   1 |    1.1299 | 0.3187 |   0.8844 | -0.6742 |   0.4728 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20               |
| swap1_ohlc     | -px_gt_sma250+adx14_gt_25     |   8 |   5 |    1.1265 | 0.2765 |   0.9888 | -0.4196 |   0.6588 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_25                 |
| swap1_ohlc     | -roc60_gt_0+atr14_pct_lt_3    |   8 |   5 |    1.1257 | 0.2735 |   0.9324 | -0.5248 |   0.5211 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3            |
| swap1_ohlc     | -roc120_gt_0+cci20_gt_100     |   8 |   5 |    1.1249 | 0.2583 |   1.0225 | -0.2927 |   0.8825 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|cci20_gt_100               |
| swap1_ohlc     | -px_gt_ema250+adx14_gt_20     |   8 |   5 |    1.1238 | 0.2750 |   0.9674 | -0.4177 |   0.6584 | px_gt_sma10|px_gt_ema200|px_gt_sma250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20                 |
| swap1_ohlc     | -roc120_gt_0+atr14_pct_lt_3   |   8 |   6 |    1.1223 | 0.2581 |   1.0324 | -0.2870 |   0.8993 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|atr14_pct_lt_3             |
| swap1_ohlc     | -px_gt_sma10+adx14_gt_20      |   8 |   1 |    1.1214 | 0.3152 |   0.8775 | -0.6686 |   0.4714 | px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20                |
| add1_ohlc      | +adx14_gt_20                  |   9 |   1 |    1.1184 | 0.3138 |   0.8749 | -0.6742 |   0.4654 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20    |
| swap1_ohlc     | -px_gt_ema200+adx14_gt_20     |   8 |   1 |    1.1184 | 0.3138 |   0.8749 | -0.6742 |   0.4654 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20                 |
| swap1_ohlc     | -px_gt_sma250+adx14_gt_20     |   8 |   1 |    1.1184 | 0.3138 |   0.8749 | -0.6742 |   0.4654 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20                 |
| swap1_ohlc     | -px_gt_ema250+adx14_gt_20     |   8 |   1 |    1.1184 | 0.3138 |   0.8749 | -0.6742 |   0.4654 | px_gt_sma10|px_gt_ema200|px_gt_sma250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20                 |
| swap1_ohlc     | -roc120_gt_0+adx14_gt_20      |   8 |   1 |    1.1184 | 0.3138 |   0.8749 | -0.6742 |   0.4654 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|adx14_gt_20                |
| swap1_ohlc     | -px_gt_ema200+bull_power_gt_0 |   8 |   4 |    1.1110 | 0.2700 |   0.9200 | -0.5480 |   0.4927 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|bull_power_gt_0             |
| add1_ohlc      | +atr14_pct_lt_3               |   9 |   6 |    1.1095 | 0.2629 |   0.9414 | -0.3571 |   0.7363 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3 |
| swap1_ohlc     | -roc120_gt_0+stoch14_gt_80    |   8 |   5 |    1.1069 | 0.2533 |   1.0060 | -0.2929 |   0.8645 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|stoch14_gt_80              |
| add1_ohlc      | +adx14_gt_20                  |   9 |   6 |    1.1049 | 0.2696 |   0.9609 | -0.3714 |   0.7258 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20    |
| swap1_ohlc     | -roc60_gt_0+adx14_gt_20       |   8 |   5 |    1.1031 | 0.2826 |   0.9517 | -0.4982 |   0.5673 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20               |
| swap1_ohlc     | -rsi14_gt_50+ultosc_gt_50     |   8 |   4 |    1.1025 | 0.2789 |   0.9218 | -0.4428 |   0.6297 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|ultosc_gt_50               |
| swap1_ohlc     | -px_gt_sma250+bear_power_gt_0 |   8 |   5 |    1.1023 | 0.2541 |   1.0022 | -0.3340 |   0.7607 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|bear_power_gt_0             |
| swap1_ohlc     | -px_gt_sma250+atr14_pct_lt_3  |   8 |   6 |    1.0972 | 0.2512 |   1.0146 | -0.2937 |   0.8552 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3              |
| swap1_ohlc     | -roc120_gt_0+cci20_gt_0       |   8 |   5 |    1.0966 | 0.2492 |   0.9843 | -0.3057 |   0.8151 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|cci20_gt_0                 |
| swap1_ohlc     | -px_gt_ema200+atr14_pct_lt_3  |   8 |   4 |    1.0943 | 0.2677 |   0.8901 | -0.5889 |   0.4545 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3              |

## Method Notes

- Tiingo OHLC is adjusted with `adj_close / close` before high/low indicators `[quant_trading_chan, p.37]`.
- Vote signals are lagged one bar before earning returns to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.
- This is local discovery on a shorter real-ETF window; final claims still require DSR/PBO/WF/OOS/FWD/bootstrap `[advances_fin_ml, p.208-211]`.
