# Stage 2 Tiingo OHLC Local Results

Status: real-inception Tiingo OHLC diagnostic. This is not a validation verdict.

Branch: `QQQ`
Risk-on: `TQQQ_3x` (`TQQQ`)
Off leg: `CASH_USD`
Extra lag days: `1`
Window: `2010-02-12` to `2026-04-14` (4,066 bars)
Signals: 47 total, 14 OHLC-derived
Configs tested: 1,086
Elapsed seconds: 0.5

## Base Replay

| neighborhood   | change   |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                                          |
|:---------------|:---------|----:|----:|----------:|-------:|---------:|--------:|---------:|:-------------------------------------------------------------------------------------------------|
| base           | none     |   8 |   6 |    0.9584 | 0.3031 |   0.8934 | -0.5402 |   0.5610 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50 |

## Top Local Candidates

| neighborhood   | change                        |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                                                         |
|:---------------|:------------------------------|----:|----:|----------:|-------:|---------:|--------:|---------:|:----------------------------------------------------------------------------------------------------------------|
| swap1_ohlc     | -rsi14_gt_50+atr14_pct_lt_5   |   8 |   1 |    1.1879 | 0.4374 |   0.9070 | -0.8165 |   0.5356 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|atr14_pct_lt_5             |
| add1_ohlc      | +atr14_pct_lt_5               |   9 |   1 |    1.1826 | 0.4335 |   0.9025 | -0.8165 |   0.5309 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_5 |
| swap1_ohlc     | -px_gt_ema200+atr14_pct_lt_5  |   8 |   1 |    1.1826 | 0.4335 |   0.9025 | -0.8165 |   0.5309 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_5              |
| swap1_ohlc     | -px_gt_sma250+atr14_pct_lt_5  |   8 |   1 |    1.1826 | 0.4335 |   0.9025 | -0.8165 |   0.5309 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_5              |
| swap1_ohlc     | -px_gt_ema250+atr14_pct_lt_5  |   8 |   1 |    1.1826 | 0.4335 |   0.9025 | -0.8165 |   0.5309 | px_gt_sma10|px_gt_ema200|px_gt_sma250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_5              |
| swap1_ohlc     | -roc20_gt_0+atr14_pct_lt_5    |   8 |   1 |    1.1826 | 0.4335 |   0.9025 | -0.8165 |   0.5309 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_5            |
| swap1_ohlc     | -roc60_gt_0+atr14_pct_lt_5    |   8 |   1 |    1.1826 | 0.4335 |   0.9025 | -0.8165 |   0.5309 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_5            |
| swap1_ohlc     | -roc120_gt_0+adx14_gt_25      |   8 |   5 |    1.1715 | 0.4142 |   1.0203 | -0.4814 |   0.8605 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|adx14_gt_25                |
| swap1_ohlc     | -roc120_gt_0+atr14_pct_lt_5   |   8 |   1 |    1.1605 | 0.4202 |   0.8876 | -0.8165 |   0.5146 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|atr14_pct_lt_5             |
| swap1_ohlc     | -px_gt_sma10+atr14_pct_lt_5   |   8 |   1 |    1.1575 | 0.4194 |   0.8885 | -0.8165 |   0.5137 | px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_5             |
| swap1_ohlc     | -px_gt_sma250+adx14_gt_20     |   8 |   5 |    1.1509 | 0.4029 |   0.9879 | -0.5681 |   0.7093 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20                 |
| swap1_ohlc     | -roc120_gt_0+bear_power_gt_0  |   8 |   5 |    1.1502 | 0.3870 |   1.0412 | -0.3903 |   0.9914 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|bear_power_gt_0            |
| swap1_ohlc     | -px_gt_ema200+atr14_pct_lt_3  |   8 |   5 |    1.1461 | 0.3877 |   0.9606 | -0.5399 |   0.7181 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3              |
| swap1_ohlc     | -px_gt_ema200+adx14_gt_20     |   8 |   5 |    1.1443 | 0.4010 |   0.9831 | -0.5681 |   0.7058 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20                 |
| swap1_ohlc     | -roc120_gt_0+adx14_gt_20      |   8 |   5 |    1.1436 | 0.3969 |   0.9780 | -0.4814 |   0.8246 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|adx14_gt_20                |
| swap1_ohlc     | -px_gt_sma250+atr14_pct_lt_3  |   8 |   5 |    1.1320 | 0.3800 |   0.9491 | -0.5399 |   0.7039 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3              |
| swap1_ohlc     | -px_gt_ema250+atr14_pct_lt_3  |   8 |   5 |    1.1254 | 0.3777 |   0.9459 | -0.5391 |   0.7005 | px_gt_sma10|px_gt_ema200|px_gt_sma250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3              |
| swap1_ohlc     | -rsi14_gt_50+adx14_gt_20      |   8 |   1 |    1.1232 | 0.4135 |   0.8783 | -0.8392 |   0.4927 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|adx14_gt_20                |
| swap1_ohlc     | -roc60_gt_0+adx14_gt_20       |   8 |   1 |    1.1206 | 0.4119 |   0.8764 | -0.8392 |   0.4908 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20               |
| swap1_ohlc     | -roc60_gt_0+atr14_pct_lt_3    |   8 |   5 |    1.1177 | 0.3784 |   0.9250 | -0.6836 |   0.5535 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3            |
| swap1_ohlc     | -roc120_gt_0+cci20_gt_100     |   8 |   5 |    1.1146 | 0.3700 |   1.0137 | -0.4124 |   0.8971 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|cci20_gt_100               |
| swap1_ohlc     | -roc120_gt_0+atr14_pct_lt_3   |   8 |   6 |    1.1143 | 0.3714 |   1.0252 | -0.4048 |   0.9176 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|atr14_pct_lt_3             |
| swap1_ohlc     | -px_gt_sma250+adx14_gt_25     |   8 |   5 |    1.1126 | 0.3869 |   0.9766 | -0.5675 |   0.6819 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_25                 |
| swap1_ohlc     | -px_gt_ema250+adx14_gt_20     |   8 |   5 |    1.1119 | 0.3833 |   0.9567 | -0.5674 |   0.6754 | px_gt_sma10|px_gt_ema200|px_gt_sma250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20                 |
| swap1_ohlc     | -px_gt_sma10+adx14_gt_20      |   8 |   1 |    1.1118 | 0.4060 |   0.8694 | -0.8354 |   0.4860 | px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20                |
| add1_ohlc      | +adx14_gt_20                  |   9 |   1 |    1.1090 | 0.4039 |   0.8669 | -0.8392 |   0.4813 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20    |
| swap1_ohlc     | -px_gt_ema200+adx14_gt_20     |   8 |   1 |    1.1090 | 0.4039 |   0.8669 | -0.8392 |   0.4813 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20                 |
| swap1_ohlc     | -px_gt_sma250+adx14_gt_20     |   8 |   1 |    1.1090 | 0.4039 |   0.8669 | -0.8392 |   0.4813 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20                 |
| swap1_ohlc     | -px_gt_ema250+adx14_gt_20     |   8 |   1 |    1.1090 | 0.4039 |   0.8669 | -0.8392 |   0.4813 | px_gt_sma10|px_gt_ema200|px_gt_sma250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20                 |
| swap1_ohlc     | -roc120_gt_0+adx14_gt_20      |   8 |   1 |    1.1090 | 0.4039 |   0.8669 | -0.8392 |   0.4813 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|adx14_gt_20                |
| add1_ohlc      | +atr14_pct_lt_3               |   9 |   6 |    1.0991 | 0.3661 |   0.9325 | -0.5004 |   0.7316 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3 |
| swap1_ohlc     | -roc120_gt_0+stoch14_gt_80    |   8 |   5 |    1.0977 | 0.3622 |   0.9981 | -0.4123 |   0.8784 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|stoch14_gt_80              |
| swap1_ohlc     | -px_gt_ema200+bull_power_gt_0 |   8 |   4 |    1.0972 | 0.3690 |   0.9082 | -0.7093 |   0.5202 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|bull_power_gt_0             |
| swap1_ohlc     | -roc60_gt_0+adx14_gt_20       |   8 |   5 |    1.0930 | 0.3901 |   0.9419 | -0.6563 |   0.5945 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20               |
| swap1_ohlc     | -rsi14_gt_50+ultosc_gt_50     |   8 |   4 |    1.0925 | 0.3807 |   0.9125 | -0.5956 |   0.6392 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|ultosc_gt_50               |
| add1_ohlc      | +adx14_gt_20                  |   9 |   6 |    1.0925 | 0.3753 |   0.9495 | -0.5174 |   0.7252 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|adx14_gt_20    |
| swap1_ohlc     | -px_gt_sma250+bear_power_gt_0 |   8 |   5 |    1.0914 | 0.3621 |   0.9929 | -0.4697 |   0.7709 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|bear_power_gt_0             |
| swap1_ohlc     | -px_gt_sma250+atr14_pct_lt_3  |   8 |   6 |    1.0854 | 0.3588 |   1.0041 | -0.4214 |   0.8514 | px_gt_sma10|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3              |
| swap1_ohlc     | -roc120_gt_0+cci20_gt_0       |   8 |   5 |    1.0845 | 0.3537 |   0.9745 | -0.4321 |   0.8184 | px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|rsi14_gt_50|cci20_gt_0                 |
| swap1_ohlc     | -px_gt_ema200+atr14_pct_lt_3  |   8 |   4 |    1.0829 | 0.3619 |   0.8802 | -0.7476 |   0.4841 | px_gt_sma10|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50|atr14_pct_lt_3              |

## Method Notes

- Tiingo OHLC is adjusted with `adj_close / close` before high/low indicators `[quant_trading_chan, p.37]`.
- Vote signals are lagged one bar before earning returns to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.
- This is local discovery on a shorter real-ETF window; final claims still require DSR/PBO/WF/OOS/FWD/bootstrap `[advances_fin_ml, p.208-211]`.
