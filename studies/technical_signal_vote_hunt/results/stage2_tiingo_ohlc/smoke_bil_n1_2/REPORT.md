# Stage 2 Tiingo OHLC Grid Results

Status: capped exact-grid discovery. This is not a validation verdict.

Branch: `QQQ`
Risk-ons: `QLD_2x`
Off leg: `BIL`
Signal subset range: n=1..2
Estimated/configs tested: 2,209 / 2,209
Windows: QLD_2x: 2007-05-31..2026-04-14 (4,748 bars)
Elapsed seconds: 0.5

## Top Configs

| branch   | risk_on   |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                    |
|:---------|:----------|----:|----:|----------:|-------:|---------:|--------:|---------:|:---------------------------|
| QQQ      | QLD_2x    |   2 |   1 |    1.2160 | 0.3144 |   1.0208 | -0.5184 |   0.6064 | roc20_gt_0|ar1_30_gt_0     |
| QQQ      | QLD_2x    |   2 |   1 |    1.2123 | 0.3018 |   0.9989 | -0.3792 |   0.7961 | roc20_gt_0|rv21_pct_lt_70  |
| QQQ      | QLD_2x    |   2 |   1 |    1.1699 | 0.2865 |   0.9743 | -0.3527 |   0.8123 | px_gt_sma50|rv21_pct_lt_70 |
| QQQ      | QLD_2x    |   2 |   1 |    1.1254 | 0.2844 |   0.9141 | -0.5118 |   0.5557 | px_gt_ema150|ar1_30_gt_0   |
| QQQ      | QLD_2x    |   2 |   1 |    1.1236 | 0.2843 |   0.9170 | -0.5195 |   0.5472 | px_gt_sma150|ar1_30_gt_0   |
| QQQ      | QLD_2x    |   2 |   1 |    1.1190 | 0.2792 |   0.9130 | -0.5174 |   0.5395 | px_gt_sma150|roc20_gt_0    |
| QQQ      | QLD_2x    |   2 |   1 |    1.1165 | 0.2741 |   0.9181 | -0.4168 |   0.6576 | px_gt_sma20|rv21_pct_lt_70 |
| QQQ      | QLD_2x    |   2 |   1 |    1.1085 | 0.2672 |   0.9124 | -0.4531 |   0.5898 | px_gt_ema20|rv21_pct_lt_70 |
| QQQ      | QLD_2x    |   2 |   1 |    1.1050 | 0.2724 |   0.9453 | -0.4248 |   0.6412 | rv21_pct_lt_70|ar1_30_gt_0 |
| QQQ      | QLD_2x    |   2 |   1 |    1.0982 | 0.2728 |   0.9155 | -0.4953 |   0.5508 | px_gt_sma50|ar1_30_gt_0    |

## Method Notes

- Top rows are retained by Sortino, then CAGR, then Calmar.
- Signals are lagged one bar before returns to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.
- All evaluated configs must be included in later DSR trial accounting `[advances_fin_ml, p.222-223]`.
