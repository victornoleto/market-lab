# Momentum Study Report

Status: research-only. No deployment, paper-trade label or mandate change.

## Verdict

Research-only screen: results use local yfinance/current-universe cache and are not promotion-eligible. Overall PBO = `0.052` sampled `1000/7488`..

## Run

- Config: `studies/momentum/config/us_stocks.yaml`
- Phase: `broad`
- Successful rows: `7488`
- Trial count used in DSR: `7488`
- Data source: local Postgres `yf_tickers`/`yf_daily_prices`

## Top 30 By Sharpe

| Name | Universe | Mechanism | Top-N | Reb | Off | Stag | CAGR | Excess | MDD | Sharpe | Calmar | DSR p | WF | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mom_us_stocks_mom_3_6_12_equal_top50_reb1_off0 | us_stocks | mom_3_6_12+equal | 50 | 1 | 0 | False | 46.91% | 38.60% | -55.54% | 1.327 | 0.845 | 0.001 | 8/8 | 4.161 |
| mom_us_stocks_mom_3_6_12_equal_top50_reb1_off0_stag | us_stocks | mom_3_6_12+equal+staggered | 50 | 1 | 0 | True | 46.91% | 38.60% | -55.54% | 1.327 | 0.845 | 0.001 | 8/8 | 4.161 |
| mom_us_stocks_mom_3_6_12_equal_top50_reb1_off0_abs | us_stocks | mom_3_6_12+equal+abs | 50 | 1 | 0 | False | 46.91% | 38.60% | -55.54% | 1.327 | 0.845 | 0.001 | 8/8 | 4.161 |
| mom_us_stocks_mom_3_6_12_equal_top50_reb1_off0_abs_stag | us_stocks | mom_3_6_12+equal+abs+staggered | 50 | 1 | 0 | True | 46.91% | 38.60% | -55.54% | 1.327 | 0.845 | 0.001 | 8/8 | 4.161 |
| mom_us_stocks_mom_3_6_12_equal_top50_reb3_off0_stag | us_stocks | mom_3_6_12+equal+staggered | 50 | 3 | 0 | True | 45.68% | 37.37% | -61.93% | 1.320 | 0.738 | 0.001 | 7/8 | 2.306 |
| mom_us_stocks_mom_3_6_12_equal_top50_reb3_off0_abs_stag | us_stocks | mom_3_6_12+equal+abs+staggered | 50 | 3 | 0 | True | 45.68% | 37.37% | -61.93% | 1.320 | 0.738 | 0.001 | 7/8 | 2.306 |
| mom_us_stocks_raw_13612_equal_top50_reb3_off0_stag | us_stocks | raw_13612+equal+staggered | 50 | 3 | 0 | True | 44.91% | 36.36% | -60.44% | 1.304 | 0.743 | 0.001 | 8/8 | 2.396 |
| mom_us_stocks_raw_13612_equal_top50_reb3_off0_abs_stag | us_stocks | raw_13612+equal+abs+staggered | 50 | 3 | 0 | True | 44.91% | 36.36% | -60.44% | 1.304 | 0.743 | 0.001 | 8/8 | 2.396 |
| mom_us_stocks_raw_13612_equal_top30_reb3_off0_stag | us_stocks | raw_13612+equal+staggered | 30 | 3 | 0 | True | 52.73% | 44.19% | -61.48% | 1.303 | 0.858 | 0.001 | 8/8 | 2.468 |
| mom_us_stocks_raw_13612_equal_top30_reb3_off0_abs_stag | us_stocks | raw_13612+equal+abs+staggered | 30 | 3 | 0 | True | 52.73% | 44.19% | -61.48% | 1.303 | 0.858 | 0.001 | 8/8 | 2.468 |
| mom_us_stocks_mom_3_6_12_equal_top50_reb3_off1 | us_stocks | mom_3_6_12+equal | 50 | 3 | 1 | False | 45.61% | 37.15% | -64.21% | 1.294 | 0.710 | 0.002 | 7/8 | 2.265 |
| mom_us_stocks_mom_3_6_12_equal_top50_reb3_off1_abs | us_stocks | mom_3_6_12+equal+abs | 50 | 3 | 1 | False | 45.61% | 37.15% | -64.21% | 1.294 | 0.710 | 0.002 | 7/8 | 2.265 |
| mom_us_stocks_mom_3_6_12_inverse_vol_top50_reb1_off0 | us_stocks | mom_3_6_12+inverse_vol | 50 | 1 | 0 | False | 43.91% | 35.61% | -56.29% | 1.292 | 0.780 | 0.002 | 8/8 | 4.842 |
| mom_us_stocks_mom_3_6_12_inverse_vol_top50_reb1_off0_stag | us_stocks | mom_3_6_12+inverse_vol+staggered | 50 | 1 | 0 | True | 43.91% | 35.61% | -56.29% | 1.292 | 0.780 | 0.002 | 8/8 | 4.842 |
| mom_us_stocks_mom_3_6_12_inverse_vol_top50_reb1_off0_abs | us_stocks | mom_3_6_12+inverse_vol+abs | 50 | 1 | 0 | False | 43.91% | 35.61% | -56.29% | 1.292 | 0.780 | 0.002 | 8/8 | 4.842 |
| mom_us_stocks_mom_3_6_12_inverse_vol_top50_reb1_off0_abs_stag | us_stocks | mom_3_6_12+inverse_vol+abs+staggered | 50 | 1 | 0 | True | 43.91% | 35.61% | -56.29% | 1.292 | 0.780 | 0.002 | 8/8 | 4.842 |
| mom_us_stocks_mom_3_6_12_capped_inverse_vol_top50_reb1_off0 | us_stocks | mom_3_6_12+capped_inverse_vol | 50 | 1 | 0 | False | 43.91% | 35.61% | -56.29% | 1.292 | 0.780 | 0.002 | 8/8 | 4.842 |
| mom_us_stocks_mom_3_6_12_capped_inverse_vol_top50_reb1_off0_stag | us_stocks | mom_3_6_12+capped_inverse_vol+staggered | 50 | 1 | 0 | True | 43.91% | 35.61% | -56.29% | 1.292 | 0.780 | 0.002 | 8/8 | 4.842 |
| mom_us_stocks_mom_3_6_12_capped_inverse_vol_top50_reb1_off0_abs | us_stocks | mom_3_6_12+capped_inverse_vol+abs | 50 | 1 | 0 | False | 43.91% | 35.61% | -56.29% | 1.292 | 0.780 | 0.002 | 8/8 | 4.842 |
| mom_us_stocks_mom_3_6_12_capped_inverse_vol_top50_reb1_off0_abs_stag | us_stocks | mom_3_6_12+capped_inverse_vol+abs+staggered | 50 | 1 | 0 | True | 43.91% | 35.61% | -56.29% | 1.292 | 0.780 | 0.002 | 8/8 | 4.842 |
| mom_us_stocks_raw_13612_inverse_vol_top30_reb3_off0 | us_stocks | raw_13612+inverse_vol | 30 | 3 | 0 | False | 45.88% | 37.58% | -56.91% | 1.290 | 0.806 | 0.003 | 8/8 | 2.680 |
| mom_us_stocks_raw_13612_inverse_vol_top30_reb3_off0_abs | us_stocks | raw_13612+inverse_vol+abs | 30 | 3 | 0 | False | 45.88% | 37.58% | -56.91% | 1.290 | 0.806 | 0.003 | 8/8 | 2.680 |
| mom_us_stocks_raw_13612_capped_inverse_vol_top30_reb3_off0 | us_stocks | raw_13612+capped_inverse_vol | 30 | 3 | 0 | False | 45.88% | 37.58% | -56.91% | 1.290 | 0.806 | 0.003 | 8/8 | 2.680 |
| mom_us_stocks_raw_13612_capped_inverse_vol_top30_reb3_off0_abs | us_stocks | raw_13612+capped_inverse_vol+abs | 30 | 3 | 0 | False | 45.88% | 37.58% | -56.91% | 1.290 | 0.806 | 0.003 | 8/8 | 2.680 |
| mom_us_stocks_raw_13612_equal_top50_reb1_off0 | us_stocks | raw_13612+equal | 50 | 1 | 0 | False | 44.91% | 36.37% | -54.41% | 1.278 | 0.825 | 0.002 | 8/8 | 4.749 |
| mom_us_stocks_raw_13612_equal_top50_reb1_off0_stag | us_stocks | raw_13612+equal+staggered | 50 | 1 | 0 | True | 44.91% | 36.37% | -54.41% | 1.278 | 0.825 | 0.002 | 8/8 | 4.749 |
| mom_us_stocks_raw_13612_equal_top50_reb1_off0_abs | us_stocks | raw_13612+equal+abs | 50 | 1 | 0 | False | 44.91% | 36.37% | -54.41% | 1.278 | 0.825 | 0.002 | 8/8 | 4.749 |
| mom_us_stocks_raw_13612_equal_top50_reb1_off0_abs_stag | us_stocks | raw_13612+equal+abs+staggered | 50 | 1 | 0 | True | 44.91% | 36.37% | -54.41% | 1.278 | 0.825 | 0.002 | 8/8 | 4.749 |
| mom_us_stocks_raw_13612_inverse_vol_top30_reb3_off0_stag | us_stocks | raw_13612+inverse_vol+staggered | 30 | 3 | 0 | True | 45.86% | 37.32% | -62.80% | 1.273 | 0.730 | 0.002 | 8/8 | 2.708 |
| mom_us_stocks_raw_13612_inverse_vol_top30_reb3_off0_abs_stag | us_stocks | raw_13612+inverse_vol+abs+staggered | 30 | 3 | 0 | True | 45.86% | 37.32% | -62.80% | 1.273 | 0.730 | 0.002 | 8/8 | 2.708 |

## Top 30 By Excess CAGR

| Name | Universe | Mechanism | Top-N | Reb | Off | Stag | CAGR | Excess | MDD | Sharpe | Calmar | DSR p | WF | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mom_us_stocks_raw_13612_equal_top5_reb3_off1 | us_stocks | raw_13612+equal | 5 | 3 | 1 | False | 95.00% | 86.46% | -75.42% | 0.823 | 1.260 | 0.218 | 7/8 | 2.628 |
| mom_us_stocks_raw_13612_equal_top5_reb3_off1_abs | us_stocks | raw_13612+equal+abs | 5 | 3 | 1 | False | 95.00% | 86.46% | -75.42% | 0.823 | 1.260 | 0.218 | 7/8 | 2.628 |
| mom_us_stocks_mom_3_6_12_equal_top3_reb6_off3 | us_stocks | mom_3_6_12+equal | 3 | 6 | 3 | False | 92.25% | 83.94% | -80.31% | 0.474 | 1.149 | 1.000 | 6/8 | 1.665 |
| mom_us_stocks_mom_3_6_12_equal_top3_reb6_off3_abs | us_stocks | mom_3_6_12+equal+abs | 3 | 6 | 3 | False | 92.25% | 83.94% | -80.31% | 0.474 | 1.149 | 1.000 | 6/8 | 1.665 |
| mom_us_stocks_mom_12_1_equal_top3_reb6_off5 | us_stocks | mom_12_1+equal | 3 | 6 | 5 | False | 93.26% | 83.86% | -85.04% | 0.651 | 1.097 | 0.918 | 7/8 | 1.610 |
| mom_us_stocks_mom_12_1_equal_top3_reb6_off5_abs | us_stocks | mom_12_1+equal+abs | 3 | 6 | 5 | False | 93.26% | 83.86% | -85.04% | 0.651 | 1.097 | 0.918 | 7/8 | 1.610 |
| mom_us_stocks_raw_13612_equal_top3_reb6_off0_stag | us_stocks | raw_13612+equal+staggered | 3 | 6 | 0 | True | 92.23% | 83.68% | -68.55% | 0.682 | 1.345 | 0.695 | 7/8 | 1.663 |
| mom_us_stocks_raw_13612_equal_top3_reb6_off0_abs_stag | us_stocks | raw_13612+equal+abs+staggered | 3 | 6 | 0 | True | 92.23% | 83.68% | -68.55% | 0.682 | 1.345 | 0.695 | 7/8 | 1.663 |
| mom_us_stocks_mom_12_1_capped_inverse_vol_top3_reb6_off5 | us_stocks | mom_12_1+capped_inverse_vol | 3 | 6 | 5 | False | 91.42% | 82.02% | -84.80% | 0.637 | 1.078 | 0.916 | 7/8 | 1.655 |
| mom_us_stocks_mom_12_1_capped_inverse_vol_top3_reb6_off5_abs | us_stocks | mom_12_1+capped_inverse_vol+abs | 3 | 6 | 5 | False | 91.42% | 82.02% | -84.80% | 0.637 | 1.078 | 0.916 | 7/8 | 1.655 |
| mom_us_stocks_raw_13612_equal_top1_reb12_off0_stag | us_stocks | raw_13612+equal+staggered | 1 | 12 | 0 | True | 90.43% | 81.89% | -66.60% | 0.626 | 1.358 | 0.853 | 7/8 | 1.011 |
| mom_us_stocks_raw_13612_equal_top1_reb12_off0_abs_stag | us_stocks | raw_13612+equal+abs+staggered | 1 | 12 | 0 | True | 90.43% | 81.89% | -66.60% | 0.626 | 1.358 | 0.853 | 7/8 | 1.011 |
| mom_us_stocks_raw_13612_inverse_vol_top1_reb12_off0_stag | us_stocks | raw_13612+inverse_vol+staggered | 1 | 12 | 0 | True | 90.43% | 81.89% | -66.60% | 0.626 | 1.358 | 0.853 | 7/8 | 1.011 |
| mom_us_stocks_raw_13612_inverse_vol_top1_reb12_off0_abs_stag | us_stocks | raw_13612+inverse_vol+abs+staggered | 1 | 12 | 0 | True | 90.43% | 81.89% | -66.60% | 0.626 | 1.358 | 0.853 | 7/8 | 1.011 |
| mom_us_stocks_raw_13612_capped_inverse_vol_top1_reb12_off0_stag | us_stocks | raw_13612+capped_inverse_vol+staggered | 1 | 12 | 0 | True | 90.43% | 81.89% | -66.60% | 0.626 | 1.358 | 0.853 | 7/8 | 1.011 |
| mom_us_stocks_raw_13612_capped_inverse_vol_top1_reb12_off0_abs_stag | us_stocks | raw_13612+capped_inverse_vol+abs+staggered | 1 | 12 | 0 | True | 90.43% | 81.89% | -66.60% | 0.626 | 1.358 | 0.853 | 7/8 | 1.011 |
| mom_us_stocks_raw_13612_equal_top3_reb6_off3 | us_stocks | raw_13612+equal | 3 | 6 | 3 | False | 89.50% | 81.20% | -81.24% | 0.469 | 1.102 | 1.000 | 6/8 | 1.665 |
| mom_us_stocks_raw_13612_equal_top3_reb6_off3_abs | us_stocks | raw_13612+equal+abs | 3 | 6 | 3 | False | 89.50% | 81.20% | -81.24% | 0.469 | 1.102 | 1.000 | 6/8 | 1.665 |
| mom_us_stocks_raw_13612_equal_top3_reb3_off1 | us_stocks | raw_13612+equal | 3 | 3 | 1 | False | 89.17% | 80.63% | -82.97% | 0.654 | 1.075 | 0.852 | 7/8 | 2.707 |
| mom_us_stocks_raw_13612_equal_top3_reb3_off1_abs | us_stocks | raw_13612+equal+abs | 3 | 3 | 1 | False | 89.17% | 80.63% | -82.97% | 0.654 | 1.075 | 0.852 | 7/8 | 2.707 |
| mom_us_stocks_raw_13612_equal_top3_reb3_off0_stag | us_stocks | raw_13612+equal+staggered | 3 | 3 | 0 | True | 89.00% | 80.45% | -81.77% | 0.644 | 1.088 | 0.889 | 7/8 | 2.749 |
| mom_us_stocks_raw_13612_equal_top3_reb3_off0_abs_stag | us_stocks | raw_13612+equal+abs+staggered | 3 | 3 | 0 | True | 89.00% | 80.45% | -81.77% | 0.644 | 1.088 | 0.889 | 7/8 | 2.749 |
| mom_us_stocks_mom_3_6_12_capped_inverse_vol_top3_reb6_off3 | us_stocks | mom_3_6_12+capped_inverse_vol | 3 | 6 | 3 | False | 87.88% | 79.58% | -79.26% | 0.523 | 1.109 | 0.999 | 6/8 | 1.718 |
| mom_us_stocks_mom_3_6_12_capped_inverse_vol_top3_reb6_off3_abs | us_stocks | mom_3_6_12+capped_inverse_vol+abs | 3 | 6 | 3 | False | 87.88% | 79.58% | -79.26% | 0.523 | 1.109 | 0.999 | 6/8 | 1.718 |
| mom_us_stocks_raw_13612_equal_top5_reb12_off10 | us_stocks | raw_13612+equal | 5 | 12 | 10 | False | 87.86% | 78.92% | -72.68% | 0.738 | 1.209 | 0.567 | 7/8 | 0.975 |
| mom_us_stocks_raw_13612_equal_top5_reb12_off10_abs | us_stocks | raw_13612+equal+abs | 5 | 12 | 10 | False | 87.86% | 78.92% | -72.68% | 0.738 | 1.209 | 0.567 | 7/8 | 0.975 |
| mom_us_stocks_raw_13612_equal_top5_reb3_off0_stag | us_stocks | raw_13612+equal+staggered | 5 | 3 | 0 | True | 87.26% | 78.72% | -66.89% | 0.809 | 1.305 | 0.256 | 7/8 | 2.692 |
| mom_us_stocks_raw_13612_equal_top5_reb3_off0_abs_stag | us_stocks | raw_13612+equal+abs+staggered | 5 | 3 | 0 | True | 87.26% | 78.72% | -66.89% | 0.809 | 1.305 | 0.256 | 7/8 | 2.692 |
| mom_us_stocks_mom_3_6_12_equal_top5_reb3_off1 | us_stocks | mom_3_6_12+equal | 5 | 3 | 1 | False | 86.49% | 78.03% | -80.31% | 0.782 | 1.077 | 0.350 | 7/8 | 2.600 |
| mom_us_stocks_mom_3_6_12_equal_top5_reb3_off1_abs | us_stocks | mom_3_6_12+equal+abs | 5 | 3 | 1 | False | 86.49% | 78.03% | -80.31% | 0.782 | 1.077 | 0.350 | 7/8 | 2.600 |

## PBO Summary

| group | pbo | n_configs | n_configs_total | sampled | n_obs | n_combinations | pass |
|---|---|---|---|---|---|---|---|
| all | 0.051587301587301584 | 1000 | 7488 | True | 6153 | 252 | True |
| universe:us_stocks | 0.051587301587301584 | 1000 | 7488 | True | 6153 | 252 | True |
| mechanism:clenow_trend+capped_inverse_vol | 0.5238095238095238 | 176 | 176 | False | 6297 | 252 | False |
| mechanism:clenow_trend+capped_inverse_vol+abs | 0.5238095238095238 | 176 | 176 | False | 6297 | 252 | False |
| mechanism:clenow_trend+capped_inverse_vol+abs+staggered | 0.7301587301587301 | 32 | 32 | False | 6527 | 252 | False |
| mechanism:clenow_trend+capped_inverse_vol+staggered | 0.7301587301587301 | 32 | 32 | False | 6527 | 252 | False |
| mechanism:clenow_trend+equal | 0.43253968253968256 | 176 | 176 | False | 6297 | 252 | True |
| mechanism:clenow_trend+equal+abs | 0.43253968253968256 | 176 | 176 | False | 6297 | 252 | True |
| mechanism:clenow_trend+equal+abs+staggered | 0.6785714285714286 | 32 | 32 | False | 6527 | 252 | False |
| mechanism:clenow_trend+equal+staggered | 0.6785714285714286 | 32 | 32 | False | 6527 | 252 | False |
| mechanism:clenow_trend+inverse_vol | 0.5238095238095238 | 176 | 176 | False | 6297 | 252 | False |
| mechanism:clenow_trend+inverse_vol+abs | 0.5238095238095238 | 176 | 176 | False | 6297 | 252 | False |
| mechanism:clenow_trend+inverse_vol+abs+staggered | 0.6468253968253969 | 32 | 32 | False | 6527 | 252 | False |
| mechanism:clenow_trend+inverse_vol+staggered | 0.6468253968253969 | 32 | 32 | False | 6527 | 252 | False |
| mechanism:mom_12_1+capped_inverse_vol | 0.48412698412698413 | 176 | 176 | False | 6153 | 252 | True |
| mechanism:mom_12_1+capped_inverse_vol+abs | 0.48412698412698413 | 176 | 176 | False | 6153 | 252 | True |
| mechanism:mom_12_1+capped_inverse_vol+abs+staggered | 0.5 | 32 | 32 | False | 6380 | 252 | False |
| mechanism:mom_12_1+capped_inverse_vol+staggered | 0.5 | 32 | 32 | False | 6380 | 252 | False |
| mechanism:mom_12_1+equal | 0.2976190476190476 | 176 | 176 | False | 6153 | 252 | True |
| mechanism:mom_12_1+equal+abs | 0.2976190476190476 | 176 | 176 | False | 6153 | 252 | True |
| mechanism:mom_12_1+equal+abs+staggered | 0.376984126984127 | 32 | 32 | False | 6380 | 252 | True |
| mechanism:mom_12_1+equal+staggered | 0.376984126984127 | 32 | 32 | False | 6380 | 252 | True |
| mechanism:mom_12_1+inverse_vol | 0.503968253968254 | 176 | 176 | False | 6153 | 252 | False |
| mechanism:mom_12_1+inverse_vol+abs | 0.503968253968254 | 176 | 176 | False | 6153 | 252 | False |
| mechanism:mom_12_1+inverse_vol+abs+staggered | 0.4642857142857143 | 32 | 32 | False | 6380 | 252 | True |
| mechanism:mom_12_1+inverse_vol+staggered | 0.4642857142857143 | 32 | 32 | False | 6380 | 252 | True |
| mechanism:mom_3_6_12+capped_inverse_vol | 0.023809523809523808 | 176 | 176 | False | 6338 | 252 | True |
| mechanism:mom_3_6_12+capped_inverse_vol+abs | 0.023809523809523808 | 176 | 176 | False | 6338 | 252 | True |
| mechanism:mom_3_6_12+capped_inverse_vol+abs+staggered | 0.04365079365079365 | 32 | 32 | False | 6570 | 252 | True |
| mechanism:mom_3_6_12+capped_inverse_vol+staggered | 0.04365079365079365 | 32 | 32 | False | 6570 | 252 | True |
| mechanism:mom_3_6_12+equal | 0.051587301587301584 | 176 | 176 | False | 6338 | 252 | True |
| mechanism:mom_3_6_12+equal+abs | 0.051587301587301584 | 176 | 176 | False | 6338 | 252 | True |
| mechanism:mom_3_6_12+equal+abs+staggered | 0.023809523809523808 | 32 | 32 | False | 6570 | 252 | True |
| mechanism:mom_3_6_12+equal+staggered | 0.023809523809523808 | 32 | 32 | False | 6570 | 252 | True |
| mechanism:mom_3_6_12+inverse_vol | 0.023809523809523808 | 176 | 176 | False | 6338 | 252 | True |
| mechanism:mom_3_6_12+inverse_vol+abs | 0.023809523809523808 | 176 | 176 | False | 6338 | 252 | True |
| mechanism:mom_3_6_12+inverse_vol+abs+staggered | 0.015873015873015872 | 32 | 32 | False | 6570 | 252 | True |
| mechanism:mom_3_6_12+inverse_vol+staggered | 0.015873015873015872 | 32 | 32 | False | 6570 | 252 | True |
| mechanism:mom_lowvol_composite+capped_inverse_vol | 0.6984126984126984 | 176 | 176 | False | 6275 | 252 | False |
| mechanism:mom_lowvol_composite+capped_inverse_vol+abs | 0.6984126984126984 | 176 | 176 | False | 6275 | 252 | False |
| mechanism:mom_lowvol_composite+capped_inverse_vol+abs+staggered | 0.75 | 32 | 32 | False | 6507 | 252 | False |
| mechanism:mom_lowvol_composite+capped_inverse_vol+staggered | 0.75 | 32 | 32 | False | 6507 | 252 | False |
| mechanism:mom_lowvol_composite+equal | 0.753968253968254 | 176 | 176 | False | 6275 | 252 | False |
| mechanism:mom_lowvol_composite+equal+abs | 0.753968253968254 | 176 | 176 | False | 6275 | 252 | False |
| mechanism:mom_lowvol_composite+equal+abs+staggered | 0.75 | 32 | 32 | False | 6507 | 252 | False |
| mechanism:mom_lowvol_composite+equal+staggered | 0.75 | 32 | 32 | False | 6507 | 252 | False |
| mechanism:mom_lowvol_composite+inverse_vol | 0.6865079365079365 | 176 | 176 | False | 6275 | 252 | False |
| mechanism:mom_lowvol_composite+inverse_vol+abs | 0.6865079365079365 | 176 | 176 | False | 6275 | 252 | False |
| mechanism:mom_lowvol_composite+inverse_vol+abs+staggered | 0.6904761904761905 | 32 | 32 | False | 6507 | 252 | False |
| mechanism:mom_lowvol_composite+inverse_vol+staggered | 0.6904761904761905 | 32 | 32 | False | 6507 | 252 | False |
| mechanism:raw_13612+capped_inverse_vol | 0.031746031746031744 | 176 | 176 | False | 6380 | 252 | True |
| mechanism:raw_13612+capped_inverse_vol+abs | 0.031746031746031744 | 176 | 176 | False | 6380 | 252 | True |
| mechanism:raw_13612+capped_inverse_vol+abs+staggered | 0.24206349206349206 | 32 | 32 | False | 6613 | 252 | True |
| mechanism:raw_13612+capped_inverse_vol+staggered | 0.24206349206349206 | 32 | 32 | False | 6613 | 252 | True |
| mechanism:raw_13612+equal | 0.03571428571428571 | 176 | 176 | False | 6380 | 252 | True |
| mechanism:raw_13612+equal+abs | 0.03571428571428571 | 176 | 176 | False | 6380 | 252 | True |
| mechanism:raw_13612+equal+abs+staggered | 0.20634920634920634 | 32 | 32 | False | 6613 | 252 | True |
| mechanism:raw_13612+equal+staggered | 0.20634920634920634 | 32 | 32 | False | 6613 | 252 | True |
| mechanism:raw_13612+inverse_vol | 0.027777777777777776 | 176 | 176 | False | 6380 | 252 | True |
| mechanism:raw_13612+inverse_vol+abs | 0.027777777777777776 | 176 | 176 | False | 6380 | 252 | True |
| mechanism:raw_13612+inverse_vol+abs+staggered | 0.14285714285714285 | 32 | 32 | False | 6613 | 252 | True |
| mechanism:raw_13612+inverse_vol+staggered | 0.14285714285714285 | 32 | 32 | False | 6613 | 252 | True |
| mechanism:vol_adjusted+capped_inverse_vol | 0.6547619047619048 | 176 | 176 | False | 6275 | 252 | False |
| mechanism:vol_adjusted+capped_inverse_vol+abs | 0.6547619047619048 | 176 | 176 | False | 6275 | 252 | False |
| mechanism:vol_adjusted+capped_inverse_vol+abs+staggered | 0.7579365079365079 | 32 | 32 | False | 6507 | 252 | False |
| mechanism:vol_adjusted+capped_inverse_vol+staggered | 0.7579365079365079 | 32 | 32 | False | 6507 | 252 | False |
| mechanism:vol_adjusted+equal | 0.4365079365079365 | 176 | 176 | False | 6275 | 252 | True |
| mechanism:vol_adjusted+equal+abs | 0.4365079365079365 | 176 | 176 | False | 6275 | 252 | True |
| mechanism:vol_adjusted+equal+abs+staggered | 0.40476190476190477 | 32 | 32 | False | 6507 | 252 | True |
| mechanism:vol_adjusted+equal+staggered | 0.40476190476190477 | 32 | 32 | False | 6507 | 252 | True |
| mechanism:vol_adjusted+inverse_vol | 0.6587301587301587 | 176 | 176 | False | 6275 | 252 | False |
| mechanism:vol_adjusted+inverse_vol+abs | 0.6587301587301587 | 176 | 176 | False | 6275 | 252 | False |
| mechanism:vol_adjusted+inverse_vol+abs+staggered | 0.503968253968254 | 32 | 32 | False | 6507 | 252 | False |
| mechanism:vol_adjusted+inverse_vol+staggered | 0.503968253968254 | 32 | 32 | False | 6507 | 252 | False |

## Plots

- [`plots/all_configs_cagr_vs_mdd.png`](plots/all_configs_cagr_vs_mdd.png)
- [`plots/boxplot_sharpe_by_universe.png`](plots/boxplot_sharpe_by_universe.png)
- [`plots/median_mdd_by_topn_rebalance.png`](plots/median_mdd_by_topn_rebalance.png)
- [`plots/finalists/mom_us_stocks_mom_3_6_12_equal_top50_reb1_off0.png`](plots/finalists/mom_us_stocks_mom_3_6_12_equal_top50_reb1_off0.png)
- [`plots/finalists/mom_us_stocks_mom_3_6_12_equal_top50_reb1_off0_stag.png`](plots/finalists/mom_us_stocks_mom_3_6_12_equal_top50_reb1_off0_stag.png)
- [`plots/finalists/mom_us_stocks_mom_3_6_12_equal_top50_reb1_off0_abs.png`](plots/finalists/mom_us_stocks_mom_3_6_12_equal_top50_reb1_off0_abs.png)
- [`plots/finalists/mom_us_stocks_mom_3_6_12_equal_top50_reb1_off0_abs_stag.png`](plots/finalists/mom_us_stocks_mom_3_6_12_equal_top50_reb1_off0_abs_stag.png)
- [`plots/finalists/mom_us_stocks_mom_3_6_12_equal_top50_reb3_off0_stag.png`](plots/finalists/mom_us_stocks_mom_3_6_12_equal_top50_reb3_off0_stag.png)
- [`plots/finalists/mom_us_stocks_mom_3_6_12_equal_top50_reb3_off0_abs_stag.png`](plots/finalists/mom_us_stocks_mom_3_6_12_equal_top50_reb3_off0_abs_stag.png)
- [`plots/finalists/mom_us_stocks_raw_13612_equal_top50_reb3_off0_stag.png`](plots/finalists/mom_us_stocks_raw_13612_equal_top50_reb3_off0_stag.png)
- [`plots/finalists/mom_us_stocks_raw_13612_equal_top50_reb3_off0_abs_stag.png`](plots/finalists/mom_us_stocks_raw_13612_equal_top50_reb3_off0_abs_stag.png)
- [`plots/finalists/mom_us_stocks_raw_13612_equal_top5_reb3_off1.png`](plots/finalists/mom_us_stocks_raw_13612_equal_top5_reb3_off1.png)
- [`plots/finalists/mom_us_stocks_raw_13612_equal_top5_reb3_off1_abs.png`](plots/finalists/mom_us_stocks_raw_13612_equal_top5_reb3_off1_abs.png)
- [`plots/finalists/mom_us_stocks_raw_13612_equal_top3_reb6_off0_stag.png`](plots/finalists/mom_us_stocks_raw_13612_equal_top3_reb6_off0_stag.png)
- [`plots/finalists/mom_us_stocks_raw_13612_equal_top3_reb6_off0_abs_stag.png`](plots/finalists/mom_us_stocks_raw_13612_equal_top3_reb6_off0_abs_stag.png)
- [`plots/finalists/mom_us_stocks_mom_12_1_equal_top3_reb6_off5.png`](plots/finalists/mom_us_stocks_mom_12_1_equal_top3_reb6_off5.png)
- [`plots/finalists/mom_us_stocks_mom_12_1_equal_top3_reb6_off5_abs.png`](plots/finalists/mom_us_stocks_mom_12_1_equal_top3_reb6_off5_abs.png)
- [`plots/finalists/mom_us_stocks_raw_13612_equal_top1_reb12_off0_stag.png`](plots/finalists/mom_us_stocks_raw_13612_equal_top1_reb12_off0_stag.png)
- [`plots/finalists/mom_us_stocks_raw_13612_equal_top1_reb12_off0_abs_stag.png`](plots/finalists/mom_us_stocks_raw_13612_equal_top1_reb12_off0_abs_stag.png)
- [`plots/finalists/mom_us_stocks_raw_13612_inverse_vol_top1_reb12_off0_stag.png`](plots/finalists/mom_us_stocks_raw_13612_inverse_vol_top1_reb12_off0_stag.png)
- [`plots/finalists/mom_us_stocks_raw_13612_inverse_vol_top1_reb12_off0_abs_stag.png`](plots/finalists/mom_us_stocks_raw_13612_inverse_vol_top1_reb12_off0_abs_stag.png)
- [`plots/finalists/mom_us_stocks_raw_13612_capped_inverse_vol_top1_reb12_off0_stag.png`](plots/finalists/mom_us_stocks_raw_13612_capped_inverse_vol_top1_reb12_off0_stag.png)
- [`plots/finalists/mom_us_stocks_raw_13612_capped_inverse_vol_top1_reb12_off0_abs_stag.png`](plots/finalists/mom_us_stocks_raw_13612_capped_inverse_vol_top1_reb12_off0_abs_stag.png)
- [`plots/finalists/mom_us_stocks_mom_3_6_12_equal_top3_reb6_off3.png`](plots/finalists/mom_us_stocks_mom_3_6_12_equal_top3_reb6_off3.png)
- [`plots/finalists/mom_us_stocks_mom_3_6_12_equal_top3_reb6_off3_abs.png`](plots/finalists/mom_us_stocks_mom_3_6_12_equal_top3_reb6_off3_abs.png)

## Errors / Skips

_No run errors._

## Caveats

- yfinance/current-universe rows remain screen-only `[advances_fin_ml, p.208-211]`.
- Broad grids must pay multiple-testing costs `[advances_fin_ml, p.273-275]`.
- Results are gross of transaction costs and taxes in this scaffold.
- CAGR/MDD are warning tiers under the mandate, not promotion gates.
