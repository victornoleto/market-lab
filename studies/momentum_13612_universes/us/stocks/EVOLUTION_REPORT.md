# US Stocks 13612 Finalist Evolution

Status: research-only. No deployment, paper-trade label or mandate change.

## Scope

- Start: `1990-01-01`
- Base finalists: `6`
- Rows: `72`
- Evolutions: fixed/staggered offsets, SPY SMA200 monthly/daily filters, stock SMA100 filter, and combinations.
- Source: yfinance/current S&P 500 universe; `promotion_eligible=false` until PIT/delisted validation exists `[advances_fin_ml, p.208-211]`.
- PBO all: `0.000`.

## Key Readings

- Best Sharpe: `evo_aggressive_raw_lb6_top5_q_staggered_off0_stock_sma100` with CAGR `55.88%`, MDD `-62.36%`, Sharpe `1.401`.
- Best full-period MDD: `evo_defensive_composite_lb12_top15_y_staggered_off6_market_sma200_daily_stock_sma100` with CAGR `11.15%`, MDD `-23.85%`, Sharpe `0.791`.
- Best GFC MDD: `evo_defensive_composite_lb12_top15_y_fixed_off6_market_sma200_daily` with CAGR `12.30%`, GFC MDD `-6.87%`, full MDD `-25.22%`.

## Plots

- [evolution_cagr_vs_mdd.png](plots/evolution/evolution_cagr_vs_mdd.png)
- [evolution_top_sharpe.png](plots/evolution/evolution_top_sharpe.png)
- [evo_aggressive_raw_lb6_top5_q_fixed_off0_none_vs_SPY.png](plots/evolution/finalists/evo_aggressive_raw_lb6_top5_q_fixed_off0_none_vs_SPY.png)
- [evo_defensive_composite_lb12_top15_y_fixed_off6_market_sma200_daily_vs_SPY.png](plots/evolution/finalists/evo_defensive_composite_lb12_top15_y_fixed_off6_market_sma200_daily_vs_SPY.png)
- [evo_aggressive_ivol_lb6_top5_q_staggered_off0_stock_sma100_vs_SPY.png](plots/evolution/finalists/evo_aggressive_ivol_lb6_top5_q_staggered_off0_stock_sma100_vs_SPY.png)
- [evo_aggressive_raw_lb6_top5_q_staggered_off0_none_vs_SPY.png](plots/evolution/finalists/evo_aggressive_raw_lb6_top5_q_staggered_off0_none_vs_SPY.png)
- [evo_defensive_composite_lb6_12_top20_y_staggered_off6_market_sma200_daily_vs_SPY.png](plots/evolution/finalists/evo_defensive_composite_lb6_12_top20_y_staggered_off6_market_sma200_daily_vs_SPY.png)
- [evo_aggressive_ivol_lb6_top5_q_staggered_off0_none_vs_SPY.png](plots/evolution/finalists/evo_aggressive_ivol_lb6_top5_q_staggered_off0_none_vs_SPY.png)
- [evo_defensive_composite_lb12_top15_y_staggered_off6_market_sma200_daily_stock_sma100_vs_SPY.png](plots/evolution/finalists/evo_defensive_composite_lb12_top15_y_staggered_off6_market_sma200_daily_stock_sma100_vs_SPY.png)
- [evo_aggressive_raw_lb6_top5_q_fixed_off0_stock_sma100_vs_SPY.png](plots/evolution/finalists/evo_aggressive_raw_lb6_top5_q_fixed_off0_stock_sma100_vs_SPY.png)
- [evo_aggressive_raw_lb6_top5_q_staggered_off0_stock_sma100_vs_SPY.png](plots/evolution/finalists/evo_aggressive_raw_lb6_top5_q_staggered_off0_stock_sma100_vs_SPY.png)
- [evo_defensive_composite_lb6_12_top20_y_staggered_off6_market_sma200_daily_stock_sma100_vs_SPY.png](plots/evolution/finalists/evo_defensive_composite_lb6_12_top20_y_staggered_off6_market_sma200_daily_stock_sma100_vs_SPY.png)
- [evo_defensive_composite_lb12_top15_y_staggered_off6_market_sma200_daily_vs_SPY.png](plots/evolution/finalists/evo_defensive_composite_lb12_top15_y_staggered_off6_market_sma200_daily_vs_SPY.png)
- [evo_defensive_composite_lb12_top15_y_fixed_off6_market_sma200_daily_stock_sma100_vs_SPY.png](plots/evolution/finalists/evo_defensive_composite_lb12_top15_y_fixed_off6_market_sma200_daily_stock_sma100_vs_SPY.png)

## Top 20 By After-Tax Sharpe

| Name | Base | Overlay | Offsets | CAGR | MDD | Sharpe | Calmar | GFC MDD | Dotcom MDD | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|
| evo_aggressive_raw_lb6_top5_q_staggered_off0_stock_sma100 | aggressive_raw_lb6_top5_q | stock_sma100 | staggered | 55.88% | -62.36% | 1.401 | 0.896 | -62.36% | -48.99% | 2.787 |
| evo_aggressive_ivol_lb6_top5_q_staggered_off0_stock_sma100 | aggressive_ivol_lb6_top5_q | stock_sma100 | staggered | 52.69% | -57.08% | 1.385 | 0.923 | -57.08% | -47.92% | 2.981 |
| evo_aggressive_raw_lb6_top5_q_fixed_off0_stock_sma100 | aggressive_raw_lb6_top5_q | stock_sma100 | fixed | 58.66% | -57.10% | 1.384 | 1.027 | -57.10% | -49.48% | 2.701 |
| evo_aggressive_ivol_lb6_top5_q_staggered_off0_none | aggressive_ivol_lb6_top5_q | none | staggered | 53.40% | -58.44% | 1.383 | 0.914 | -58.44% | -47.04% | 2.950 |
| evo_aggressive_raw_lb6_top5_q_fixed_off0_none | aggressive_raw_lb6_top5_q | none | fixed | 59.32% | -59.04% | 1.380 | 1.005 | -59.04% | -49.48% | 2.668 |
| evo_aggressive_raw_lb6_top5_q_staggered_off0_none | aggressive_raw_lb6_top5_q | none | staggered | 55.73% | -66.00% | 1.380 | 0.844 | -66.00% | -47.74% | 2.746 |
| evo_aggressive_ivol_lb6_top5_q_fixed_off0_none | aggressive_ivol_lb6_top5_q | none | fixed | 55.87% | -54.99% | 1.356 | 1.016 | -54.99% | -47.99% | 2.905 |
| evo_aggressive_ivol_lb6_top5_q_fixed_off0_stock_sma100 | aggressive_ivol_lb6_top5_q | stock_sma100 | fixed | 54.57% | -57.02% | 1.347 | 0.957 | -57.02% | -47.99% | 2.939 |
| evo_aggressive_raw_lb6_top5_q_staggered_off0_market_sma200_monthly_stock_sma100 | aggressive_raw_lb6_top5_q | market_sma200_monthly_stock_sma100 | staggered | 45.16% | -48.99% | 1.343 | 0.922 | -21.03% | -48.99% | 2.613 |
| evo_aggressive_ivol_lb6_top5_q_staggered_off0_market_sma200_monthly | aggressive_ivol_lb6_top5_q | market_sma200_monthly | staggered | 43.35% | -47.04% | 1.331 | 0.922 | -19.83% | -47.04% | 2.746 |
| evo_aggressive_ivol_lb6_top5_q_staggered_off0_market_sma200_monthly_stock_sma100 | aggressive_ivol_lb6_top5_q | market_sma200_monthly_stock_sma100 | staggered | 43.12% | -47.92% | 1.329 | 0.900 | -19.82% | -47.92% | 2.754 |
| evo_aggressive_raw_lb6_top5_q_staggered_off0_market_sma200_monthly | aggressive_raw_lb6_top5_q | market_sma200_monthly | staggered | 44.75% | -47.74% | 1.329 | 0.937 | -21.04% | -47.74% | 2.595 |
| evo_aggressive_raw_lb6_top5_q_fixed_off0_market_sma200_monthly_stock_sma100 | aggressive_raw_lb6_top5_q | market_sma200_monthly_stock_sma100 | fixed | 49.18% | -49.48% | 1.327 | 0.994 | -26.43% | -49.48% | 2.536 |
| evo_aggressive_raw_lb6_top5_q_staggered_off0_market_sma200_daily_stock_sma100 | aggressive_raw_lb6_top5_q | market_sma200_daily_stock_sma100 | staggered | 42.89% | -48.99% | 1.317 | 0.875 | -15.21% | -48.99% | 8.656 |
| evo_aggressive_raw_lb6_top5_q_fixed_off0_market_sma200_monthly | aggressive_raw_lb6_top5_q | market_sma200_monthly | fixed | 48.53% | -49.48% | 1.310 | 0.981 | -26.43% | -49.48% | 2.536 |
| evo_aggressive_raw_lb6_top5_q_staggered_off0_market_sma200_daily | aggressive_raw_lb6_top5_q | market_sma200_daily | staggered | 42.74% | -47.74% | 1.305 | 0.895 | -15.22% | -47.74% | 8.643 |
| evo_aggressive_ivol_lb6_top5_q_staggered_off0_market_sma200_daily | aggressive_ivol_lb6_top5_q | market_sma200_daily | staggered | 40.81% | -47.04% | 1.299 | 0.868 | -14.08% | -47.04% | 8.811 |
| evo_aggressive_ivol_lb6_top5_q_staggered_off0_market_sma200_daily_stock_sma100 | aggressive_ivol_lb6_top5_q | market_sma200_daily_stock_sma100 | staggered | 40.44% | -47.92% | 1.297 | 0.844 | -14.06% | -47.92% | 8.813 |
| evo_aggressive_ivol_lb6_top5_q_fixed_off0_market_sma200_monthly_stock_sma100 | aggressive_ivol_lb6_top5_q | market_sma200_monthly_stock_sma100 | fixed | 46.33% | -47.99% | 1.294 | 0.965 | -25.35% | -47.99% | 2.716 |
| evo_aggressive_ivol_lb6_top5_q_fixed_off0_market_sma200_monthly | aggressive_ivol_lb6_top5_q | market_sma200_monthly | fixed | 45.74% | -47.99% | 1.278 | 0.953 | -25.35% | -47.99% | 2.722 |

## Top 20 By Full-Period MDD

| Name | Base | Overlay | Offsets | CAGR | MDD | Sharpe | Calmar | GFC MDD | Dotcom MDD | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|
| evo_defensive_composite_lb12_top15_y_staggered_off6_market_sma200_daily_stock_sma100 | defensive_composite_lb12_top15_y | market_sma200_daily_stock_sma100 | staggered | 11.15% | -23.85% | 0.791 | 0.468 | -8.50% | -9.31% | 7.303 |
| evo_defensive_composite_lb12_top15_y_staggered_off6_market_sma200_daily | defensive_composite_lb12_top15_y | market_sma200_daily | staggered | 11.20% | -24.13% | 0.797 | 0.464 | -7.66% | -9.07% | 7.301 |
| evo_defensive_composite_lb6_12_top20_y_staggered_off6_market_sma200_daily | defensive_composite_lb6_12_top20_y | market_sma200_daily | staggered | 11.12% | -24.15% | 0.859 | 0.461 | -8.04% | -8.54% | 7.296 |
| evo_defensive_composite_lb6_12_top20_y_staggered_off6_market_sma200_daily_stock_sma100 | defensive_composite_lb6_12_top20_y | market_sma200_daily_stock_sma100 | staggered | 11.16% | -24.29% | 0.857 | 0.459 | -8.24% | -9.02% | 7.296 |
| evo_defensive_composite_lb12_top15_y_fixed_off6_market_sma200_daily | defensive_composite_lb12_top15_y | market_sma200_daily | fixed | 12.30% | -25.22% | 0.808 | 0.488 | -6.87% | -8.02% | 7.328 |
| evo_defensive_composite_lb12_top15_y_fixed_off6_market_sma200_daily_stock_sma100 | defensive_composite_lb12_top15_y | market_sma200_daily_stock_sma100 | fixed | 11.97% | -25.32% | 0.781 | 0.473 | -12.21% | -8.83% | 7.336 |
| evo_defensive_composite_lb6_12_top20_y_fixed_off6_market_sma200_daily | defensive_composite_lb6_12_top20_y | market_sma200_daily | fixed | 11.59% | -25.47% | 0.831 | 0.455 | -7.31% | -9.29% | 7.326 |
| evo_defensive_composite_lb6_12_top20_y_fixed_off6_market_sma200_daily_stock_sma100 | defensive_composite_lb6_12_top20_y | market_sma200_daily_stock_sma100 | fixed | 11.87% | -25.62% | 0.846 | 0.463 | -8.54% | -9.06% | 7.322 |
| evo_defensive_composite_lb12_top15_y_staggered_off6_market_sma200_monthly_stock_sma100 | defensive_composite_lb12_top15_y | market_sma200_monthly_stock_sma100 | staggered | 12.49% | -30.44% | 0.897 | 0.410 | -15.57% | -9.20% | 0.901 |
| evo_defensive_composite_lb12_top15_y_staggered_off6_market_sma200_monthly | defensive_composite_lb12_top15_y | market_sma200_monthly | staggered | 12.47% | -30.46% | 0.900 | 0.409 | -15.31% | -9.07% | 0.900 |
| evo_defensive_composite_lb6_12_top20_y_staggered_off6_market_sma200_monthly | defensive_composite_lb6_12_top20_y | market_sma200_monthly | staggered | 12.63% | -30.85% | 0.932 | 0.409 | -16.20% | -10.06% | 0.897 |
| evo_defensive_composite_lb6_12_top20_y_staggered_off6_market_sma200_monthly_stock_sma100 | defensive_composite_lb6_12_top20_y | market_sma200_monthly_stock_sma100 | staggered | 12.68% | -30.85% | 0.932 | 0.411 | -16.24% | -10.49% | 0.896 |
| evo_defensive_composite_lb6_12_top20_y_fixed_off6_market_sma200_monthly_stock_sma100 | defensive_composite_lb6_12_top20_y | market_sma200_monthly_stock_sma100 | fixed | 14.95% | -34.22% | 0.887 | 0.437 | -16.05% | -16.16% | 0.911 |
| evo_defensive_composite_lb6_12_top20_y_fixed_off6_market_sma200_monthly | defensive_composite_lb6_12_top20_y | market_sma200_monthly | fixed | 14.74% | -34.22% | 0.879 | 0.431 | -15.03% | -16.18% | 0.915 |
| evo_defensive_composite_lb12_top15_y_fixed_off6_market_sma200_monthly | defensive_composite_lb12_top15_y | market_sma200_monthly | fixed | 15.57% | -34.44% | 0.873 | 0.452 | -14.99% | -13.72% | 0.917 |
| evo_defensive_composite_lb12_top15_y_fixed_off6_none | defensive_composite_lb12_top15_y | none | fixed | 16.90% | -34.44% | 0.897 | 0.491 | -33.66% | -20.75% | 0.920 |
| evo_defensive_composite_lb12_top15_y_fixed_off6_market_sma200_monthly_stock_sma100 | defensive_composite_lb12_top15_y | market_sma200_monthly_stock_sma100 | fixed | 15.10% | -34.44% | 0.837 | 0.438 | -16.62% | -13.16% | 0.926 |
| evo_defensive_composite_lb6_12_top20_y_fixed_off6_none | defensive_composite_lb6_12_top20_y | none | fixed | 16.07% | -38.85% | 0.899 | 0.414 | -37.27% | -19.17% | 0.915 |
| evo_defensive_composite_lb12_top15_y_fixed_off6_stock_sma100 | defensive_composite_lb12_top15_y | stock_sma100 | fixed | 16.42% | -39.19% | 0.863 | 0.419 | -37.76% | -20.64% | 0.932 |
| evo_balanced_voladj_lb6_top5_q_staggered_off0_market_sma200_monthly_stock_sma100 | balanced_voladj_lb6_top5_q | market_sma200_monthly_stock_sma100 | staggered | 26.76% | -39.35% | 1.080 | 0.680 | -17.46% | -39.35% | 3.027 |

## Top 20 By GFC MDD

| Name | Base | Overlay | Offsets | CAGR | MDD | Sharpe | Calmar | GFC MDD | Dotcom MDD | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|
| evo_defensive_composite_lb12_top15_y_fixed_off6_market_sma200_daily | defensive_composite_lb12_top15_y | market_sma200_daily | fixed | 12.30% | -25.22% | 0.808 | 0.488 | -6.87% | -8.02% | 7.328 |
| evo_defensive_composite_lb6_12_top20_y_fixed_off6_market_sma200_daily | defensive_composite_lb6_12_top20_y | market_sma200_daily | fixed | 11.59% | -25.47% | 0.831 | 0.455 | -7.31% | -9.29% | 7.326 |
| evo_defensive_composite_lb12_top15_y_staggered_off6_market_sma200_daily | defensive_composite_lb12_top15_y | market_sma200_daily | staggered | 11.20% | -24.13% | 0.797 | 0.464 | -7.66% | -9.07% | 7.301 |
| evo_defensive_composite_lb6_12_top20_y_staggered_off6_market_sma200_daily | defensive_composite_lb6_12_top20_y | market_sma200_daily | staggered | 11.12% | -24.15% | 0.859 | 0.461 | -8.04% | -8.54% | 7.296 |
| evo_defensive_composite_lb6_12_top20_y_staggered_off6_market_sma200_daily_stock_sma100 | defensive_composite_lb6_12_top20_y | market_sma200_daily_stock_sma100 | staggered | 11.16% | -24.29% | 0.857 | 0.459 | -8.24% | -9.02% | 7.296 |
| evo_defensive_composite_lb12_top15_y_staggered_off6_market_sma200_daily_stock_sma100 | defensive_composite_lb12_top15_y | market_sma200_daily_stock_sma100 | staggered | 11.15% | -23.85% | 0.791 | 0.468 | -8.50% | -9.31% | 7.303 |
| evo_defensive_composite_lb6_12_top20_y_fixed_off6_market_sma200_daily_stock_sma100 | defensive_composite_lb6_12_top20_y | market_sma200_daily_stock_sma100 | fixed | 11.87% | -25.62% | 0.846 | 0.463 | -8.54% | -9.06% | 7.322 |
| evo_balanced_voladj_lb6_top10_m_fixed_off0_market_sma200_daily | balanced_voladj_lb6_top10_m | market_sma200_daily | fixed | 21.82% | -41.54% | 1.039 | 0.525 | -9.59% | -41.54% | 11.525 |
| evo_balanced_voladj_lb6_top10_m_staggered_off0_market_sma200_daily | balanced_voladj_lb6_top10_m | market_sma200_daily | staggered | 21.82% | -41.54% | 1.039 | 0.525 | -9.59% | -41.54% | 11.525 |
| evo_balanced_voladj_lb6_top10_m_fixed_off0_market_sma200_daily_stock_sma100 | balanced_voladj_lb6_top10_m | market_sma200_daily_stock_sma100 | fixed | 21.61% | -41.54% | 1.031 | 0.520 | -9.60% | -41.54% | 11.543 |
| evo_balanced_voladj_lb6_top10_m_staggered_off0_market_sma200_daily_stock_sma100 | balanced_voladj_lb6_top10_m | market_sma200_daily_stock_sma100 | staggered | 21.61% | -41.54% | 1.031 | 0.520 | -9.60% | -41.54% | 11.543 |
| evo_balanced_voladj_lb6_top5_q_fixed_off0_market_sma200_daily | balanced_voladj_lb6_top5_q | market_sma200_daily | fixed | 26.34% | -40.42% | 1.016 | 0.652 | -11.60% | -39.36% | 9.134 |
| evo_balanced_voladj_lb6_top5_q_fixed_off0_market_sma200_daily_stock_sma100 | balanced_voladj_lb6_top5_q | market_sma200_daily_stock_sma100 | fixed | 25.82% | -39.60% | 1.003 | 0.652 | -11.60% | -39.36% | 9.140 |
| evo_balanced_voladj_lb6_top10_m_fixed_off0_market_sma200_monthly_stock_sma100 | balanced_voladj_lb6_top10_m | market_sma200_monthly_stock_sma100 | fixed | 23.88% | -41.54% | 1.087 | 0.575 | -11.70% | -41.54% | 5.996 |
| evo_balanced_voladj_lb6_top10_m_staggered_off0_market_sma200_monthly_stock_sma100 | balanced_voladj_lb6_top10_m | market_sma200_monthly_stock_sma100 | staggered | 23.88% | -41.54% | 1.087 | 0.575 | -11.70% | -41.54% | 5.996 |
| evo_balanced_voladj_lb6_top10_m_fixed_off0_market_sma200_monthly | balanced_voladj_lb6_top10_m | market_sma200_monthly | fixed | 24.04% | -41.54% | 1.092 | 0.579 | -11.70% | -41.54% | 5.980 |
| evo_balanced_voladj_lb6_top10_m_staggered_off0_market_sma200_monthly | balanced_voladj_lb6_top10_m | market_sma200_monthly | staggered | 24.04% | -41.54% | 1.092 | 0.579 | -11.70% | -41.54% | 5.980 |
| evo_defensive_composite_lb12_top15_y_fixed_off6_market_sma200_daily_stock_sma100 | defensive_composite_lb12_top15_y | market_sma200_daily_stock_sma100 | fixed | 11.97% | -25.32% | 0.781 | 0.473 | -12.21% | -8.83% | 7.336 |
| evo_aggressive_ivol_lb6_top5_q_staggered_off0_market_sma200_daily_stock_sma100 | aggressive_ivol_lb6_top5_q | market_sma200_daily_stock_sma100 | staggered | 40.44% | -47.92% | 1.297 | 0.844 | -14.06% | -47.92% | 8.813 |
| evo_aggressive_ivol_lb6_top5_q_staggered_off0_market_sma200_daily | aggressive_ivol_lb6_top5_q | market_sma200_daily | staggered | 40.81% | -47.04% | 1.299 | 0.868 | -14.08% | -47.04% | 8.811 |

## PBO Summary

| group | pbo | n_configs | n_obs | n_combinations | pass |
|---|---|---|---|---|---|
| all | 0.0 | 72 | 8022 | 252 | True |
| universe:us_stocks | 0.0 | 72 | 8022 | 252 | True |
| mechanism:composite_mom_lowvol | 0.7103174603174603 | 24 | 8022 | 252 | False |
| mechanism:raw_13612 | 0.7222222222222222 | 12 | 8147 | 252 | False |
| mechanism:raw_inverse_vol | 0.623015873015873 | 12 | 8147 | 252 | False |
| mechanism:vol_adjusted_13612 | 0.7777777777777778 | 24 | 8147 | 252 | False |
| us_stocks:composite_mom_lowvol | 0.7103174603174603 | 24 | 8022 | 252 | False |
| us_stocks:raw_13612 | 0.7222222222222222 | 12 | 8147 | 252 | False |
| us_stocks:raw_inverse_vol | 0.623015873015873 | 12 | 8147 | 252 | False |
| us_stocks:vol_adjusted_13612 | 0.7777777777777778 | 24 | 8147 | 252 | False |

## Caveats

- These are post-heatmap evolutions of selected finalists; the effective trial count is larger than this file alone.
- The SPY SMA200 and stock SMA100 filters are literature-grounded diagnostics, but still tested here after seeing the heatmap.
- yfinance/current constituents inflate historical stock screens via survivorship bias `[advances_fin_ml, p.208-211]`.
