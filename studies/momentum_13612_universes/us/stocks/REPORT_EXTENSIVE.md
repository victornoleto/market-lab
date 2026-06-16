# Extensive Momentum 13612 US Grid Report

Status: research-only. No deployment, paper-trade label or mandate change.

## Verdict

Screen-only FAIL: yfinance/current-universe data are non-promotable, and overall PBO is 0.321.

## Grid

- Universes: `us_stocks`
- Top-N: `1,3,5,10,15,20`
- Rebalance frequencies: `1,3,6,12` months, all offsets
- Mechanisms: `raw_equal, voladj_equal, clenow_equal, composite_equal, raw_inverse_vol, raw_abs_cash`
- Rows: `792`
- Ranking metric: after-tax strategy returns under Brazil's annual 15% realized-gain rule
- Benchmark: SPY adjusted close as S&P 500 proxy

## Key Findings

- Top-N funcionou para risco: mediana de vol caiu de `63.29%` em top1 para `26.96%` em top20; MDD mediano caiu de `-86.33%` para `-59.68%`.
- Melhor Sharpe after-tax: `mom13612_us_stocks_raw_inverse_vol_top3_reb3_off0`, CAGR `65.67%`, MDD `-78.50%`, Sharpe `1.359`.
- Melhor `us_stocks` por Sharpe after-tax: `mom13612_us_stocks_raw_inverse_vol_top3_reb3_off0`, CAGR `65.67%`, MDD `-78.50%`, Sharpe `1.359`.
- Score shaping reduziu risco: raw mediano MDD `-70.39%`/vol `35.50%`; vol-adjusted `-61.68%`/`27.66%`; composite `-47.76%`/`18.36%`.
- Frequência com maior Sharpe mediano: `1m`; menor turnover mediano: `12m`.
- PBO: all `0.321`, us_stocks `0.321` sobre retornos after-tax. Tudo segue screen-only yfinance/current-universe `[advances_fin_ml, p.208-211]`.

## Aggregate Plots

- [all_configs_cagr_vs_mdd.png](plots/extensive/all_configs_cagr_vs_mdd.png)
- [boxplot_excess_cagr_by_frequency.png](plots/extensive/boxplot_excess_cagr_by_frequency.png)
- [best_sharpe_by_mechanism_freq.png](plots/extensive/best_sharpe_by_mechanism_freq.png)
- [median_vol_by_mechanism_freq.png](plots/extensive/median_vol_by_mechanism_freq.png)
- [median_mdd_by_topn_frequency.png](plots/extensive/median_mdd_by_topn_frequency.png)

## Top 20 By After-Tax Sharpe

| Name | Universe | Mechanism | Top-N | Reb | Off | CAGR | Gross CAGR | Tax Drag | SPY CAGR | Excess | MDD | Vol | Sharpe | Calmar | Turnover/yr | Above SPY |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mom13612_us_stocks_raw_inverse_vol_top3_reb3_off0 | us_stocks | raw_inverse_vol | 3 | 3 | 0 | 65.67% | 72.08% | 6.41% | 8.91% | 56.76% | -78.50% | 44.48% | 1.359 | 0.837 | 2.426 | 100.00% |
| mom13612_us_stocks_raw_equal_top3_reb3_off0 | us_stocks | raw_13612 | 3 | 3 | 0 | 66.45% | 72.73% | 6.28% | 8.91% | 57.54% | -78.33% | 45.71% | 1.345 | 0.848 | 2.227 | 100.00% |
| mom13612_us_stocks_raw_abs_cash_top3_reb3_off0 | us_stocks | raw_abs_cash | 3 | 3 | 0 | 66.45% | 72.73% | 6.28% | 8.91% | 57.54% | -78.33% | 45.71% | 1.345 | 0.848 | 2.227 | 100.00% |
| mom13612_us_stocks_raw_inverse_vol_top3_reb1_off0 | us_stocks | raw_inverse_vol | 3 | 1 | 0 | 61.55% | 68.53% | 6.98% | 8.91% | 52.64% | -68.63% | 43.48% | 1.322 | 0.897 | 5.430 | 100.00% |
| mom13612_us_stocks_raw_equal_top3_reb1_off0 | us_stocks | raw_13612 | 3 | 1 | 0 | 62.33% | 68.96% | 6.64% | 8.91% | 53.42% | -74.36% | 45.07% | 1.301 | 0.838 | 4.816 | 100.00% |
| mom13612_us_stocks_raw_abs_cash_top3_reb1_off0 | us_stocks | raw_abs_cash | 3 | 1 | 0 | 62.33% | 68.96% | 6.64% | 8.91% | 53.42% | -74.36% | 45.07% | 1.301 | 0.838 | 4.816 | 100.00% |
| mom13612_us_stocks_clenow_equal_top10_reb1_off0 | us_stocks | clenow_trend | 10 | 1 | 0 | 41.10% | 46.09% | 4.98% | 8.48% | 32.62% | -58.19% | 30.83% | 1.272 | 0.706 | 4.696 | 100.00% |
| mom13612_us_stocks_raw_inverse_vol_top3_reb6_off3 | us_stocks | raw_inverse_vol | 3 | 6 | 3 | 59.11% | 65.09% | 5.99% | 9.33% | 49.78% | -81.93% | 44.50% | 1.268 | 0.721 | 1.535 | 100.00% |
| mom13612_us_stocks_raw_inverse_vol_top5_reb3_off0 | us_stocks | raw_inverse_vol | 5 | 3 | 0 | 48.67% | 54.03% | 5.36% | 8.91% | 39.76% | -56.23% | 36.75% | 1.264 | 0.866 | 2.635 | 100.00% |
| mom13612_us_stocks_raw_equal_top5_reb3_off0 | us_stocks | raw_13612 | 5 | 3 | 0 | 50.70% | 56.00% | 5.30% | 8.91% | 41.79% | -63.80% | 38.49% | 1.259 | 0.795 | 2.369 | 100.00% |
| mom13612_us_stocks_raw_abs_cash_top5_reb3_off0 | us_stocks | raw_abs_cash | 5 | 3 | 0 | 50.70% | 56.00% | 5.30% | 8.91% | 41.79% | -63.80% | 38.49% | 1.259 | 0.795 | 2.369 | 100.00% |
| mom13612_us_stocks_raw_equal_top5_reb1_off0 | us_stocks | raw_13612 | 5 | 1 | 0 | 50.06% | 55.38% | 5.32% | 8.91% | 41.15% | -65.14% | 38.16% | 1.256 | 0.769 | 4.908 | 100.00% |
| mom13612_us_stocks_raw_abs_cash_top5_reb1_off0 | us_stocks | raw_abs_cash | 5 | 1 | 0 | 50.06% | 55.38% | 5.32% | 8.91% | 41.15% | -65.14% | 38.16% | 1.256 | 0.769 | 4.908 | 100.00% |
| mom13612_us_stocks_raw_inverse_vol_top5_reb1_off0 | us_stocks | raw_inverse_vol | 5 | 1 | 0 | 47.05% | 52.30% | 5.25% | 8.91% | 38.14% | -58.45% | 36.28% | 1.245 | 0.805 | 5.638 | 100.00% |
| mom13612_us_stocks_raw_equal_top5_reb6_off3 | us_stocks | raw_13612 | 5 | 6 | 3 | 50.93% | 56.11% | 5.18% | 9.33% | 41.60% | -76.95% | 39.36% | 1.244 | 0.662 | 1.421 | 100.00% |
| mom13612_us_stocks_raw_abs_cash_top5_reb6_off3 | us_stocks | raw_abs_cash | 5 | 6 | 3 | 50.93% | 56.11% | 5.18% | 9.33% | 41.60% | -76.95% | 39.36% | 1.244 | 0.662 | 1.421 | 100.00% |
| mom13612_us_stocks_raw_equal_top3_reb6_off3 | us_stocks | raw_13612 | 3 | 6 | 3 | 59.08% | 64.81% | 5.73% | 9.33% | 49.75% | -84.38% | 45.90% | 1.243 | 0.700 | 1.453 | 100.00% |
| mom13612_us_stocks_raw_abs_cash_top3_reb6_off3 | us_stocks | raw_abs_cash | 3 | 6 | 3 | 59.08% | 64.81% | 5.73% | 9.33% | 49.75% | -84.38% | 45.90% | 1.243 | 0.700 | 1.453 | 100.00% |
| mom13612_us_stocks_raw_inverse_vol_top5_reb6_off3 | us_stocks | raw_inverse_vol | 5 | 6 | 3 | 47.89% | 53.01% | 5.12% | 9.33% | 38.56% | -72.05% | 37.57% | 1.231 | 0.665 | 1.529 | 100.00% |
| mom13612_us_stocks_raw_equal_top5_reb6_off2 | us_stocks | raw_13612 | 5 | 6 | 2 | 49.64% | 54.44% | 4.79% | 9.75% | 39.89% | -74.56% | 38.95% | 1.231 | 0.666 | 1.448 | 100.00% |

## Top 20 By After-Tax Excess CAGR

| Name | Universe | Mechanism | Top-N | Reb | Off | CAGR | Gross CAGR | Tax Drag | SPY CAGR | Excess | MDD | Vol | Sharpe | Calmar | Turnover/yr | Above SPY |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mom13612_us_stocks_raw_equal_top3_reb3_off0 | us_stocks | raw_13612 | 3 | 3 | 0 | 66.45% | 72.73% | 6.28% | 8.91% | 57.54% | -78.33% | 45.71% | 1.345 | 0.848 | 2.227 | 100.00% |
| mom13612_us_stocks_raw_abs_cash_top3_reb3_off0 | us_stocks | raw_abs_cash | 3 | 3 | 0 | 66.45% | 72.73% | 6.28% | 8.91% | 57.54% | -78.33% | 45.71% | 1.345 | 0.848 | 2.227 | 100.00% |
| mom13612_us_stocks_raw_inverse_vol_top3_reb3_off0 | us_stocks | raw_inverse_vol | 3 | 3 | 0 | 65.67% | 72.08% | 6.41% | 8.91% | 56.76% | -78.50% | 44.48% | 1.359 | 0.837 | 2.426 | 100.00% |
| mom13612_us_stocks_raw_equal_top3_reb1_off0 | us_stocks | raw_13612 | 3 | 1 | 0 | 62.33% | 68.96% | 6.64% | 8.91% | 53.42% | -74.36% | 45.07% | 1.301 | 0.838 | 4.816 | 100.00% |
| mom13612_us_stocks_raw_abs_cash_top3_reb1_off0 | us_stocks | raw_abs_cash | 3 | 1 | 0 | 62.33% | 68.96% | 6.64% | 8.91% | 53.42% | -74.36% | 45.07% | 1.301 | 0.838 | 4.816 | 100.00% |
| mom13612_us_stocks_raw_inverse_vol_top3_reb1_off0 | us_stocks | raw_inverse_vol | 3 | 1 | 0 | 61.55% | 68.53% | 6.98% | 8.91% | 52.64% | -68.63% | 43.48% | 1.322 | 0.897 | 5.430 | 100.00% |
| mom13612_us_stocks_raw_inverse_vol_top3_reb6_off3 | us_stocks | raw_inverse_vol | 3 | 6 | 3 | 59.11% | 65.09% | 5.99% | 9.33% | 49.78% | -81.93% | 44.50% | 1.268 | 0.721 | 1.535 | 100.00% |
| mom13612_us_stocks_raw_equal_top3_reb6_off3 | us_stocks | raw_13612 | 3 | 6 | 3 | 59.08% | 64.81% | 5.73% | 9.33% | 49.75% | -84.38% | 45.90% | 1.243 | 0.700 | 1.453 | 100.00% |
| mom13612_us_stocks_raw_abs_cash_top3_reb6_off3 | us_stocks | raw_abs_cash | 3 | 6 | 3 | 59.08% | 64.81% | 5.73% | 9.33% | 49.75% | -84.38% | 45.90% | 1.243 | 0.700 | 1.453 | 100.00% |
| mom13612_us_stocks_raw_equal_top1_reb3_off1 | us_stocks | raw_13612 | 1 | 3 | 1 | 58.86% | 64.93% | 6.07% | 9.37% | 49.49% | -83.78% | 66.53% | 1.027 | 0.703 | 2.787 | 100.00% |
| mom13612_us_stocks_raw_inverse_vol_top1_reb3_off1 | us_stocks | raw_inverse_vol | 1 | 3 | 1 | 58.86% | 64.93% | 6.07% | 9.37% | 49.49% | -83.78% | 66.53% | 1.027 | 0.703 | 2.787 | 100.00% |
| mom13612_us_stocks_raw_abs_cash_top1_reb3_off1 | us_stocks | raw_abs_cash | 1 | 3 | 1 | 58.86% | 64.93% | 6.07% | 9.37% | 49.49% | -83.78% | 66.53% | 1.027 | 0.703 | 2.787 | 100.00% |
| mom13612_us_stocks_raw_equal_top1_reb6_off3 | us_stocks | raw_13612 | 1 | 6 | 3 | 56.05% | 62.17% | 6.11% | 9.33% | 46.72% | -84.91% | 61.15% | 1.034 | 0.660 | 1.612 | 100.00% |
| mom13612_us_stocks_raw_inverse_vol_top1_reb6_off3 | us_stocks | raw_inverse_vol | 1 | 6 | 3 | 56.05% | 62.17% | 6.11% | 9.33% | 46.72% | -84.91% | 61.15% | 1.034 | 0.660 | 1.612 | 100.00% |
| mom13612_us_stocks_raw_abs_cash_top1_reb6_off3 | us_stocks | raw_abs_cash | 1 | 6 | 3 | 56.05% | 62.17% | 6.11% | 9.33% | 46.72% | -84.91% | 61.15% | 1.034 | 0.660 | 1.612 | 100.00% |
| mom13612_us_stocks_voladj_equal_top1_reb6_off0 | us_stocks | vol_adjusted_13612 | 1 | 6 | 0 | 53.58% | 58.18% | 4.59% | 8.91% | 44.67% | -72.25% | 56.20% | 1.046 | 0.742 | 1.794 | 100.00% |
| mom13612_us_stocks_raw_equal_top3_reb3_off1 | us_stocks | raw_13612 | 3 | 3 | 1 | 52.44% | 58.54% | 6.11% | 9.37% | 43.07% | -74.15% | 44.35% | 1.173 | 0.707 | 2.392 | 100.00% |
| mom13612_us_stocks_raw_abs_cash_top3_reb3_off1 | us_stocks | raw_abs_cash | 3 | 3 | 1 | 52.44% | 58.54% | 6.11% | 9.37% | 43.07% | -74.15% | 44.35% | 1.173 | 0.707 | 2.392 | 100.00% |
| mom13612_us_stocks_clenow_equal_top3_reb1_off0 | us_stocks | clenow_trend | 3 | 1 | 0 | 51.33% | 57.15% | 5.82% | 8.48% | 42.85% | -64.29% | 42.56% | 1.187 | 0.798 | 5.413 | 100.00% |
| mom13612_us_stocks_raw_equal_top1_reb6_off1 | us_stocks | raw_13612 | 1 | 6 | 1 | 51.84% | 57.38% | 5.54% | 9.37% | 42.47% | -86.22% | 66.04% | 0.962 | 0.601 | 1.720 | 100.00% |

## Finalists With Individual Plots

| Name | Universe | Mechanism | Top-N | Reb | Off | CAGR | Excess | MDD | Sharpe | Turnover/yr | Above SPY | Plot |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mom13612_us_stocks_raw_inverse_vol_top3_reb3_off0 | us_stocks | raw_inverse_vol | 3 | 3 | 0 | 65.67% | 56.76% | -78.50% | 1.359 | 2.426 | 100.00% | [mom13612_us_stocks_raw_inverse_vol_top3_reb3_off0_vs_SPY.png](plots/extensive/finalists/mom13612_us_stocks_raw_inverse_vol_top3_reb3_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_equal_top3_reb3_off0 | us_stocks | raw_13612 | 3 | 3 | 0 | 66.45% | 57.54% | -78.33% | 1.345 | 2.227 | 100.00% | [mom13612_us_stocks_raw_equal_top3_reb3_off0_vs_SPY.png](plots/extensive/finalists/mom13612_us_stocks_raw_equal_top3_reb3_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_abs_cash_top3_reb3_off0 | us_stocks | raw_abs_cash | 3 | 3 | 0 | 66.45% | 57.54% | -78.33% | 1.345 | 2.227 | 100.00% | [mom13612_us_stocks_raw_abs_cash_top3_reb3_off0_vs_SPY.png](plots/extensive/finalists/mom13612_us_stocks_raw_abs_cash_top3_reb3_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_inverse_vol_top3_reb1_off0 | us_stocks | raw_inverse_vol | 3 | 1 | 0 | 61.55% | 52.64% | -68.63% | 1.322 | 5.430 | 100.00% | [mom13612_us_stocks_raw_inverse_vol_top3_reb1_off0_vs_SPY.png](plots/extensive/finalists/mom13612_us_stocks_raw_inverse_vol_top3_reb1_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_equal_top3_reb1_off0 | us_stocks | raw_13612 | 3 | 1 | 0 | 62.33% | 53.42% | -74.36% | 1.301 | 4.816 | 100.00% | [mom13612_us_stocks_raw_equal_top3_reb1_off0_vs_SPY.png](plots/extensive/finalists/mom13612_us_stocks_raw_equal_top3_reb1_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_abs_cash_top3_reb1_off0 | us_stocks | raw_abs_cash | 3 | 1 | 0 | 62.33% | 53.42% | -74.36% | 1.301 | 4.816 | 100.00% | [mom13612_us_stocks_raw_abs_cash_top3_reb1_off0_vs_SPY.png](plots/extensive/finalists/mom13612_us_stocks_raw_abs_cash_top3_reb1_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_inverse_vol_top5_reb3_off0 | us_stocks | raw_inverse_vol | 5 | 3 | 0 | 48.67% | 39.76% | -56.23% | 1.264 | 2.635 | 100.00% | [mom13612_us_stocks_raw_inverse_vol_top5_reb3_off0_vs_SPY.png](plots/extensive/finalists/mom13612_us_stocks_raw_inverse_vol_top5_reb3_off0_vs_SPY.png) |
| mom13612_us_stocks_raw_equal_top1_reb3_off1 | us_stocks | raw_13612 | 1 | 3 | 1 | 58.86% | 49.49% | -83.78% | 1.027 | 2.787 | 100.00% | [mom13612_us_stocks_raw_equal_top1_reb3_off1_vs_SPY.png](plots/extensive/finalists/mom13612_us_stocks_raw_equal_top1_reb3_off1_vs_SPY.png) |
| mom13612_us_stocks_raw_inverse_vol_top1_reb3_off1 | us_stocks | raw_inverse_vol | 1 | 3 | 1 | 58.86% | 49.49% | -83.78% | 1.027 | 2.787 | 100.00% | [mom13612_us_stocks_raw_inverse_vol_top1_reb3_off1_vs_SPY.png](plots/extensive/finalists/mom13612_us_stocks_raw_inverse_vol_top1_reb3_off1_vs_SPY.png) |
| mom13612_us_stocks_raw_equal_top1_reb12_off9 | us_stocks | raw_13612 | 1 | 12 | 9 | 51.96% | 41.66% | -86.44% | 1.006 | 0.954 | 100.00% | [mom13612_us_stocks_raw_equal_top1_reb12_off9_vs_SPY.png](plots/extensive/finalists/mom13612_us_stocks_raw_equal_top1_reb12_off9_vs_SPY.png) |
| mom13612_us_stocks_raw_inverse_vol_top1_reb12_off9 | us_stocks | raw_inverse_vol | 1 | 12 | 9 | 51.96% | 41.66% | -86.44% | 1.006 | 0.954 | 100.00% | [mom13612_us_stocks_raw_inverse_vol_top1_reb12_off9_vs_SPY.png](plots/extensive/finalists/mom13612_us_stocks_raw_inverse_vol_top1_reb12_off9_vs_SPY.png) |
| mom13612_us_stocks_raw_abs_cash_top1_reb12_off9 | us_stocks | raw_abs_cash | 1 | 12 | 9 | 51.96% | 41.66% | -86.44% | 1.006 | 0.954 | 100.00% | [mom13612_us_stocks_raw_abs_cash_top1_reb12_off9_vs_SPY.png](plots/extensive/finalists/mom13612_us_stocks_raw_abs_cash_top1_reb12_off9_vs_SPY.png) |

## PBO Summary

| group | pbo | n_configs | n_obs | n_combinations | pass |
|---|---|---|---|---|---|
| all | 0.32142857142857145 | 792 | 6153 | 252 | True |
| universe:us_stocks | 0.32142857142857145 | 792 | 6153 | 252 | True |

## Mechanism Summary

| Group | N | Max CAGR | Median CAGR | Median MDD | Median Vol | Max Sharpe | Median Tax Drag | Median Turnover |
|---|---|---|---|---|---|---|---|---|
| clenow_trend | 132 | 51.33% | 30.50% | -68.31% | 33.52% | 1.272 | 3.51% | 0.971 |
| composite_mom_lowvol | 132 | 17.76% | 10.11% | -47.76% | 18.36% | 0.842 | 1.41% | 1.008 |
| raw_13612 | 132 | 66.45% | 33.98% | -70.39% | 35.50% | 1.345 | 3.76% | 0.953 |
| raw_abs_cash | 132 | 66.45% | 33.98% | -70.39% | 35.50% | 1.345 | 3.76% | 0.953 |
| raw_inverse_vol | 132 | 65.67% | 30.64% | -68.61% | 33.79% | 1.359 | 3.57% | 0.960 |
| vol_adjusted_13612 | 132 | 53.58% | 22.57% | -61.68% | 27.66% | 1.172 | 2.73% | 1.000 |

## Rebalance Frequency Summary

| Group | N | Max CAGR | Median CAGR | Median MDD | Median Vol | Max Sharpe | Median Tax Drag | Median Turnover |
|---|---|---|---|---|---|---|---|---|
| 1.0 | 36 | 62.33% | 31.35% | -59.09% | 30.13% | 1.322 | 3.91% | 5.425 |
| 3.0 | 108 | 66.45% | 32.36% | -63.59% | 30.80% | 1.359 | 3.81% | 2.800 |
| 6.0 | 216 | 59.11% | 29.60% | -67.42% | 31.26% | 1.268 | 3.33% | 1.702 |
| 12.0 | 432 | 51.96% | 26.30% | -65.74% | 30.54% | 1.216 | 2.96% | 0.932 |

## Top-N Summary

| Group | N | Max CAGR | Median CAGR | Median MDD | Median Vol | Max Sharpe | Median Tax Drag | Median Turnover |
|---|---|---|---|---|---|---|---|---|
| 1.0 | 132 | 58.86% | 29.46% | -86.33% | 63.29% | 1.046 | 3.26% | 1.013 |
| 3.0 | 132 | 66.45% | 36.83% | -73.90% | 42.54% | 1.359 | 4.00% | 0.997 |
| 5.0 | 132 | 50.93% | 36.06% | -68.79% | 36.65% | 1.264 | 3.84% | 0.990 |
| 10.0 | 132 | 41.10% | 29.60% | -62.11% | 30.95% | 1.272 | 3.36% | 0.981 |
| 15.0 | 132 | 36.19% | 26.24% | -61.30% | 28.43% | 1.205 | 2.98% | 0.969 |
| 20.0 | 132 | 31.41% | 24.19% | -59.68% | 26.96% | 1.116 | 2.82% | 0.963 |

## Caveats

- All rows are yfinance/current-universe screens and `promotion_eligible=false` until PIT/delisted validation exists `[advances_fin_ml, p.208-211]`.
- The grid is intentionally broad; PBO/DSR are diagnostics against data-mining and not optional `[advances_fin_ml, p.273-275]`.
- Main rankings are after-tax for realized capital gains, but still gross of transaction costs/slippage.
- Tax model nets realized gains/losses annually at 15% and does not force a final liquidation of unrealized positions.
- Individual finalist plots are diagnostic picks, not winners.
