# US Stocks 13612 Heatmap Diagnostics

Status: research-only. No deployment, paper-trade label or mandate change.

## Scope

- Start: `1990-01-01`
- US stock universe: `sp500`
- Max US stocks: `9999`
- Rows: `4092`
- Lookbacks: `3,6,12,3_6_12,6_12,1_3_6_12`
- Top-N: `1,3,5,10,15,20`
- Rebalance months: `1,3,6,12` with all offsets
- Source caveat: yfinance/current-universe screen; `promotion_eligible=false` until PIT/delisted validation exists `[advances_fin_ml, p.208-211]`.

## Best After-Tax Sharpe

`mom13612_us_stocks_raw_equal_lb6_top5_reb3_off0`: CAGR `59.24%`, MDD `-59.04%`, Sharpe `1.379`, GFC MDD `-59.04%`.

## Best Rolling Relative Dominance

`mom13612_us_stocks_raw_equal_lb1_3_6_12_top15_reb3_off0`: score `96.75%`, p25 `96.08%`, min `32.32%`.

## Interactive Output

- [HEATMAP.html](HEATMAP.html)
- [heatmap_after_tax_sharpe.png](plots/heatmap/heatmap_after_tax_sharpe.png)
- [heatmap_after_tax_cagr.png](plots/heatmap/heatmap_after_tax_cagr.png)
- [heatmap_after_tax_mdd.png](plots/heatmap/heatmap_after_tax_mdd.png)
- [heatmap_rolling_relative_score.png](plots/heatmap/heatmap_rolling_relative_score.png)
- [heatmap_gfc_mdd.png](plots/heatmap/heatmap_gfc_mdd.png)
- [heatmap_dotcom_mdd.png](plots/heatmap/heatmap_dotcom_mdd.png)

## Top 20 By After-Tax Sharpe

| Name | Mechanism | Lookback | Top-N | Reb | Off | CAGR | MDD | Sharpe | RollRel | RollP25 | GFC MDD | Dotcom MDD | Turnover | Plot |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mom13612_us_stocks_raw_equal_lb6_top5_reb3_off0 | raw_13612 | lb6 | 5 | 3 | 0 | 59.24% | -59.04% | 1.379 | 96.28% | 95.17% | -59.04% | -49.48% | 2.667 | [mom13612_us_stocks_raw_equal_lb6_top5_reb3_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_equal_lb6_top5_reb3_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_abs_cash_lb6_top5_reb3_off0 | raw_abs_cash | lb6 | 5 | 3 | 0 | 59.24% | -59.04% | 1.379 | 96.28% | 95.17% | -59.04% | -49.48% | 2.667 | [mom13612_us_stocks_raw_abs_cash_lb6_top5_reb3_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_abs_cash_lb6_top5_reb3_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_inverse_vol_lb6_top5_reb3_off0 | raw_inverse_vol | lb6 | 5 | 3 | 0 | 55.80% | -54.99% | 1.355 | 96.61% | 95.38% | -54.99% | -47.99% | 2.905 | [mom13612_us_stocks_raw_inverse_vol_lb6_top5_reb3_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_inverse_vol_lb6_top5_reb3_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_equal_lb6_top5_reb1_off0 | raw_13612 | lb6 | 5 | 1 | 0 | 57.12% | -66.31% | 1.348 | 94.63% | 93.89% | -63.52% | -55.42% | 5.276 | [mom13612_us_stocks_raw_equal_lb6_top5_reb1_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_equal_lb6_top5_reb1_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_abs_cash_lb6_top5_reb1_off0 | raw_abs_cash | lb6 | 5 | 1 | 0 | 57.12% | -66.31% | 1.348 | 94.63% | 93.89% | -63.52% | -55.42% | 5.276 | [mom13612_us_stocks_raw_abs_cash_lb6_top5_reb1_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_abs_cash_lb6_top5_reb1_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_inverse_vol_lb6_top5_reb1_off0 | raw_inverse_vol | lb6 | 5 | 1 | 0 | 52.91% | -57.63% | 1.317 | 95.11% | 94.10% | -55.62% | -53.80% | 6.018 | [mom13612_us_stocks_raw_inverse_vol_lb6_top5_reb1_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_inverse_vol_lb6_top5_reb1_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_equal_lb6_top10_reb1_off0 | raw_13612 | lb6 | 10 | 1 | 0 | 45.50% | -59.49% | 1.315 | 94.88% | 94.00% | -59.49% | -46.97% | 5.059 | [mom13612_us_stocks_raw_equal_lb6_top10_reb1_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_equal_lb6_top10_reb1_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_abs_cash_lb6_top10_reb1_off0 | raw_abs_cash | lb6 | 10 | 1 | 0 | 45.42% | -59.96% | 1.314 | 94.80% | 94.00% | -59.49% | -46.97% | 5.059 | [mom13612_us_stocks_raw_abs_cash_lb6_top10_reb1_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_abs_cash_lb6_top10_reb1_off0_vs_SPY.png) |
| mom13612_us_stocks_clenow_equal_trend126d_top10_reb1_off0 | clenow_trend | trend126d | 10 | 1 | 0 | 43.51% | -58.19% | 1.295 | 96.69% | 95.44% | -58.19% | -39.11% | 4.622 | [mom13612_us_stocks_clenow_equal_trend126d_top10_reb1_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_clenow_equal_trend126d_top10_reb1_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_equal_lb6_top10_reb3_off1 | raw_13612 | lb6 | 10 | 3 | 1 | 44.51% | -67.09% | 1.286 | 94.26% | 94.11% | -67.09% | -43.58% | 2.593 | [mom13612_us_stocks_raw_equal_lb6_top10_reb3_off1_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_equal_lb6_top10_reb3_off1_vs_SPY.png) |
| mom13612_us_stocks_raw_abs_cash_lb6_top10_reb3_off1 | raw_abs_cash | lb6 | 10 | 3 | 1 | 44.43% | -67.21% | 1.284 | 94.18% | 94.11% | -67.09% | -43.58% | 2.593 | [mom13612_us_stocks_raw_abs_cash_lb6_top10_reb3_off1_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_abs_cash_lb6_top10_reb3_off1_vs_SPY.png) |
| mom13612_us_stocks_raw_equal_lb1_3_6_12_top5_reb1_off0 | raw_13612 | lb1_3_6_12 | 5 | 1 | 0 | 54.21% | -65.14% | 1.283 | 94.01% | 92.62% | -63.70% | -56.80% | 4.707 | [mom13612_us_stocks_raw_equal_lb1_3_6_12_top5_reb1_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_equal_lb1_3_6_12_top5_reb1_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_abs_cash_lb1_3_6_12_top5_reb1_off0 | raw_abs_cash | lb1_3_6_12 | 5 | 1 | 0 | 54.21% | -65.14% | 1.283 | 94.01% | 92.62% | -63.70% | -56.80% | 4.707 | [mom13612_us_stocks_raw_abs_cash_lb1_3_6_12_top5_reb1_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_abs_cash_lb1_3_6_12_top5_reb1_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_equal_lb6_top15_reb1_off0 | raw_13612 | lb6 | 15 | 1 | 0 | 39.63% | -58.10% | 1.281 | 95.99% | 94.35% | -58.10% | -40.96% | 4.819 | [mom13612_us_stocks_raw_equal_lb6_top15_reb1_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_equal_lb6_top15_reb1_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_abs_cash_lb6_top15_reb1_off0 | raw_abs_cash | lb6 | 15 | 1 | 0 | 39.42% | -58.14% | 1.276 | 95.81% | 94.34% | -58.10% | -40.96% | 4.829 | [mom13612_us_stocks_raw_abs_cash_lb6_top15_reb1_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_abs_cash_lb6_top15_reb1_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_equal_lb6_top3_reb1_off0 | raw_13612 | lb6 | 3 | 1 | 0 | 62.09% | -68.98% | 1.273 | 93.76% | 92.15% | -68.98% | -59.05% | 5.654 | [mom13612_us_stocks_raw_equal_lb6_top3_reb1_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_equal_lb6_top3_reb1_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_abs_cash_lb6_top3_reb1_off0 | raw_abs_cash | lb6 | 3 | 1 | 0 | 62.09% | -68.98% | 1.273 | 93.76% | 92.15% | -68.98% | -59.05% | 5.654 | [mom13612_us_stocks_raw_abs_cash_lb6_top3_reb1_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_abs_cash_lb6_top3_reb1_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_equal_lb3_6_12_top5_reb1_off0 | raw_13612 | lb3_6_12 | 5 | 1 | 0 | 53.63% | -69.92% | 1.270 | 93.06% | 90.83% | -64.98% | -61.32% | 4.249 | [mom13612_us_stocks_raw_equal_lb3_6_12_top5_reb1_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_equal_lb3_6_12_top5_reb1_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_abs_cash_lb3_6_12_top5_reb1_off0 | raw_abs_cash | lb3_6_12 | 5 | 1 | 0 | 53.63% | -69.92% | 1.270 | 93.06% | 90.83% | -64.98% | -61.32% | 4.249 | [mom13612_us_stocks_raw_abs_cash_lb3_6_12_top5_reb1_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_abs_cash_lb3_6_12_top5_reb1_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_equal_lb1_3_6_12_top10_reb1_off0 | raw_13612 | lb1_3_6_12 | 10 | 1 | 0 | 44.21% | -59.68% | 1.268 | 95.90% | 95.24% | -59.68% | -53.28% | 4.554 | [mom13612_us_stocks_raw_equal_lb1_3_6_12_top10_reb1_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_equal_lb1_3_6_12_top10_reb1_off0_vs_SPY.png) |


## Top 20 By Rolling Relative Score

| Name | Mechanism | Lookback | Top-N | Reb | Off | RollRel | RollP25 | RollMin | CAGR | MDD | Sharpe | Terminal/SPY | 20y Above | Plot |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mom13612_us_stocks_raw_equal_lb1_3_6_12_top15_reb3_off0 | raw_13612 | lb1_3_6_12 | 15 | 3 | 0 | 96.75% | 96.08% | 32.32% | 38.34% | -57.13% | 1.203 | 1608.303 | 98.91% | [mom13612_us_stocks_raw_equal_lb1_3_6_12_top15_reb3_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_equal_lb1_3_6_12_top15_reb3_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_abs_cash_lb1_3_6_12_top15_reb3_off0 | raw_abs_cash | lb1_3_6_12 | 15 | 3 | 0 | 96.75% | 96.08% | 32.32% | 38.34% | -57.13% | 1.203 | 1608.303 | 98.91% | [mom13612_us_stocks_raw_abs_cash_lb1_3_6_12_top15_reb3_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_abs_cash_lb1_3_6_12_top15_reb3_off0_vs_SPY.png) |
| mom13612_us_stocks_clenow_equal_trend126d_top10_reb1_off0 | clenow_trend | trend126d | 10 | 1 | 0 | 96.69% | 95.44% | 40.53% | 43.51% | -58.19% | 1.295 | 5453.818 | 98.84% | [mom13612_us_stocks_clenow_equal_trend126d_top10_reb1_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_clenow_equal_trend126d_top10_reb1_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_inverse_vol_lb1_3_6_12_top15_reb3_off0 | raw_inverse_vol | lb1_3_6_12 | 15 | 3 | 0 | 96.63% | 95.33% | 26.78% | 34.15% | -57.26% | 1.152 | 575.851 | 98.89% | [mom13612_us_stocks_raw_inverse_vol_lb1_3_6_12_top15_reb3_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_inverse_vol_lb1_3_6_12_top15_reb3_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_inverse_vol_lb6_top5_reb3_off0 | raw_inverse_vol | lb6 | 5 | 3 | 0 | 96.61% | 95.38% | 20.11% | 55.80% | -54.99% | 1.355 | 84598.527 | 99.18% | [mom13612_us_stocks_raw_inverse_vol_lb6_top5_reb3_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_inverse_vol_lb6_top5_reb3_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_equal_lb3_6_12_top15_reb3_off0 | raw_13612 | lb3_6_12 | 15 | 3 | 0 | 96.52% | 95.69% | 34.04% | 38.12% | -55.00% | 1.196 | 1524.440 | 98.83% | [mom13612_us_stocks_raw_equal_lb3_6_12_top15_reb3_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_equal_lb3_6_12_top15_reb3_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_abs_cash_lb3_6_12_top15_reb3_off0 | raw_abs_cash | lb3_6_12 | 15 | 3 | 0 | 96.52% | 95.69% | 34.04% | 38.12% | -55.00% | 1.196 | 1524.440 | 98.83% | [mom13612_us_stocks_raw_abs_cash_lb3_6_12_top15_reb3_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_abs_cash_lb3_6_12_top15_reb3_off0_vs_SPY.png) |
| mom13612_us_stocks_clenow_equal_trend126d_top15_reb1_off0 | clenow_trend | trend126d | 15 | 1 | 0 | 96.40% | 95.09% | 10.95% | 36.21% | -60.91% | 1.226 | 957.919 | 98.85% | [mom13612_us_stocks_clenow_equal_trend126d_top15_reb1_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_clenow_equal_trend126d_top15_reb1_off0_vs_SPY.png) |
| mom13612_us_stocks_clenow_equal_trend126d_top20_reb1_off0 | clenow_trend | trend126d | 20 | 1 | 0 | 96.39% | 95.30% | 19.13% | 32.31% | -58.72% | 1.183 | 363.159 | 98.87% | [mom13612_us_stocks_clenow_equal_trend126d_top20_reb1_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_clenow_equal_trend126d_top20_reb1_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_inverse_vol_lb3_6_12_top10_reb3_off0 | raw_inverse_vol | lb3_6_12 | 10 | 3 | 0 | 96.38% | 95.49% | 25.59% | 37.56% | -55.68% | 1.158 | 1330.491 | 98.81% | [mom13612_us_stocks_raw_inverse_vol_lb3_6_12_top10_reb3_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_inverse_vol_lb3_6_12_top10_reb3_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_equal_lb3_top15_reb3_off1 | raw_13612 | lb3 | 15 | 3 | 1 | 96.31% | 95.05% | 23.15% | 35.65% | -55.95% | 1.195 | 835.593 | 98.95% | [mom13612_us_stocks_raw_equal_lb3_top15_reb3_off1_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_equal_lb3_top15_reb3_off1_vs_SPY.png) |
| mom13612_us_stocks_raw_abs_cash_lb3_top15_reb3_off1 | raw_abs_cash | lb3 | 15 | 3 | 1 | 96.31% | 95.05% | 23.15% | 35.65% | -55.95% | 1.195 | 835.593 | 98.95% | [mom13612_us_stocks_raw_abs_cash_lb3_top15_reb3_off1_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_abs_cash_lb3_top15_reb3_off1_vs_SPY.png) |
| mom13612_us_stocks_raw_equal_lb3_top10_reb12_off3 | raw_13612 | lb3 | 10 | 12 | 3 | 96.31% | 94.90% | 11.38% | 35.27% | -61.53% | 1.128 | 760.502 | 98.87% | [mom13612_us_stocks_raw_equal_lb3_top10_reb12_off3_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_equal_lb3_top10_reb12_off3_vs_SPY.png) |
| mom13612_us_stocks_raw_abs_cash_lb3_top10_reb12_off3 | raw_abs_cash | lb3 | 10 | 12 | 3 | 96.31% | 94.90% | 11.38% | 35.27% | -61.53% | 1.128 | 760.502 | 98.87% | [mom13612_us_stocks_raw_abs_cash_lb3_top10_reb12_off3_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_abs_cash_lb3_top10_reb12_off3_vs_SPY.png) |
| mom13612_us_stocks_raw_inverse_vol_lb3_6_12_top15_reb3_off0 | raw_inverse_vol | lb3_6_12 | 15 | 3 | 0 | 96.30% | 95.04% | 29.82% | 33.83% | -54.15% | 1.138 | 531.692 | 98.77% | [mom13612_us_stocks_raw_inverse_vol_lb3_6_12_top15_reb3_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_inverse_vol_lb3_6_12_top15_reb3_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_equal_lb6_top5_reb3_off0 | raw_13612 | lb6 | 5 | 3 | 0 | 96.28% | 95.17% | 19.18% | 59.24% | -59.04% | 1.379 | 175174.044 | 99.19% | [mom13612_us_stocks_raw_equal_lb6_top5_reb3_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_equal_lb6_top5_reb3_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_abs_cash_lb6_top5_reb3_off0 | raw_abs_cash | lb6 | 5 | 3 | 0 | 96.28% | 95.17% | 19.18% | 59.24% | -59.04% | 1.379 | 175174.044 | 99.19% | [mom13612_us_stocks_raw_abs_cash_lb6_top5_reb3_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_abs_cash_lb6_top5_reb3_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_equal_lb3_top15_reb3_off2 | raw_13612 | lb3 | 15 | 3 | 2 | 96.23% | 95.17% | 34.17% | 34.00% | -65.84% | 1.151 | 555.369 | 98.45% | [mom13612_us_stocks_raw_equal_lb3_top15_reb3_off2_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_equal_lb3_top15_reb3_off2_vs_SPY.png) |
| mom13612_us_stocks_raw_abs_cash_lb3_top15_reb3_off2 | raw_abs_cash | lb3 | 15 | 3 | 2 | 96.23% | 95.17% | 34.17% | 34.00% | -65.84% | 1.151 | 555.369 | 98.45% | [mom13612_us_stocks_raw_abs_cash_lb3_top15_reb3_off2_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_abs_cash_lb3_top15_reb3_off2_vs_SPY.png) |
| mom13612_us_stocks_raw_equal_lb1_3_6_12_top10_reb3_off0 | raw_13612 | lb1_3_6_12 | 10 | 3 | 0 | 96.22% | 95.59% | 25.86% | 41.80% | -59.68% | 1.199 | 3660.783 | 98.74% | [mom13612_us_stocks_raw_equal_lb1_3_6_12_top10_reb3_off0_vs_SPY.png](plots/heatmap/finalists/mom13612_us_stocks_raw_equal_lb1_3_6_12_top10_reb3_off0_vs_SPY.png) |

## Notes

- Dot-com/GFC/COVID windows are stress diagnostics, not fitted gates `[testing_tuning, p.327-335]`.
- Re-running to 1990 with current S&P 500 constituents is more biased than a PIT universe because delisted losers are absent `[advances_fin_ml, p.208-211]`.
