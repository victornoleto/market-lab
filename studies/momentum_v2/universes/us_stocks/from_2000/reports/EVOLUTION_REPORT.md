# Finalist Evolution — `us_stocks`

Status: **research-only**, `promotion_eligible=false`. The Postgres universe plus survivorship filters *mitigate* but do not *eliminate* bias — the yfinance feed never captured most fully delisted names, so historical screens stay inflated `[advances_fin_ml, p.208-211]`. Main rankings are after Brazil's annual 15% realized-gain tax, gross of transaction costs/slippage. Benchmark: SPY.

Finalists are selected by after-tax Sharpe and Calmar (return/risk-adjusted lens). Evolutions add MA overlays (SPY SMA200 monthly/daily, stock SMA100, combos) and fixed/staggered offsets; these are literature-grounded stress diagnostics tested after the broad map, so the effective trial count exceeds this file `[advances_fin_ml, p.273-275]`.

## Scope

- Start: `2000-01-01`
- Rows: `72`

## Key readings

- Best after-tax Sharpe: `evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_none` — Sharpe `1.134`, CAGR `51.96%`, MDD `-61.10%`, overlay `none`.
- Best after-tax Calmar: `evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_fixed_none` — Calmar `0.941`, CAGR `59.47%`, MDD `-63.19%`, overlay `none`.

## Plots

- [evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_none_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_none_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_fixed_stock_sma100_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_fixed_stock_sma100_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_fixed_stock_sma100_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_fixed_stock_sma100_vs_SPY.png)
- [evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_staggered_stock_sma100_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_staggered_stock_sma100_vs_SPY.png)
- [evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_staggered_stock_sma100_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_staggered_stock_sma100_vs_SPY.png)
- [evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0_fixed_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0_fixed_none_vs_SPY.png)
- [evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0_staggered_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0_staggered_none_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_stock_sma100_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_stock_sma100_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_stock_sma100_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_stock_sma100_vs_SPY.png)
- [evo_momv2_us_stocks_raw_13612_lb6_12_top15_reb3_off0_fixed_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_lb6_12_top15_reb3_off0_fixed_none_vs_SPY.png)
- [evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0_staggered_market_sma200_daily_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0_staggered_market_sma200_daily_vs_SPY.png)

## Top 25 by after-tax Sharpe

| Name | Overlay | Offsets | CAGR | MDD | Sharpe | Calmar | RollRel | GFC MDD |
|---|---|---|---|---|---|---|---|---|
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_none | none | staggered | 51.96% | -61.10% | 1.134 | 0.850 | 95.08% | -61.10% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_none | none | staggered | 51.96% | -61.10% | 1.134 | 0.850 | 95.08% | -61.10% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_fixed_stock_sma100 | stock_sma100 | fixed | 45.48% | -66.86% | 1.132 | 0.680 | 94.00% | -66.86% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_fixed_stock_sma100 | stock_sma100 | fixed | 45.48% | -66.86% | 1.132 | 0.680 | 94.00% | -66.86% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_staggered_stock_sma100 | stock_sma100 | staggered | 41.26% | -66.77% | 1.116 | 0.618 | 94.68% | -66.77% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_staggered_stock_sma100 | stock_sma100 | staggered | 41.26% | -66.77% | 1.116 | 0.618 | 94.68% | -66.77% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0_fixed_none | none | fixed | 42.41% | -60.37% | 1.114 | 0.702 | 94.71% | -60.37% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0_staggered_none | none | staggered | 39.83% | -67.97% | 1.112 | 0.586 | 94.50% | -67.97% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_stock_sma100 | stock_sma100 | staggered | 42.68% | -64.35% | 1.110 | 0.663 | 94.05% | -64.35% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_stock_sma100 | stock_sma100 | staggered | 42.68% | -64.35% | 1.110 | 0.663 | 94.05% | -64.35% |
| evo_momv2_us_stocks_raw_13612_lb6_12_top15_reb3_off0_fixed_none | none | fixed | 54.19% | -63.37% | 1.088 | 0.855 | 94.69% | -63.37% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 31.39% | -44.13% | 1.071 | 0.711 | 93.35% | -20.41% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0_staggered_stock_sma100 | stock_sma100 | staggered | 36.86% | -65.73% | 1.068 | 0.561 | 94.25% | -65.73% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_staggered_none | none | staggered | 49.92% | -66.03% | 1.061 | 0.756 | 95.18% | -66.03% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_staggered_none | none | staggered | 49.92% | -66.03% | 1.061 | 0.756 | 95.18% | -66.03% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0_fixed_stock_sma100 | stock_sma100 | fixed | 38.63% | -55.83% | 1.058 | 0.692 | 94.46% | -55.83% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_fixed_stock_sma100 | stock_sma100 | fixed | 39.62% | -62.45% | 1.053 | 0.634 | 94.87% | -62.45% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_fixed_stock_sma100 | stock_sma100 | fixed | 39.62% | -62.45% | 1.053 | 0.634 | 94.87% | -62.45% |
| evo_momv2_us_stocks_raw_13612_lb6_12_top15_reb3_off0_staggered_stock_sma100 | stock_sma100 | staggered | 38.27% | -67.03% | 1.052 | 0.571 | 93.54% | -67.03% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 31.32% | -46.60% | 1.043 | 0.672 | 92.82% | -20.53% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_staggered_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | staggered | 31.53% | -53.10% | 1.037 | 0.594 | 92.81% | -20.53% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_staggered_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | staggered | 31.53% | -53.10% | 1.037 | 0.594 | 92.81% | -20.53% |
| evo_momv2_us_stocks_raw_13612_lb6_12_top15_reb3_off0_staggered_none | none | staggered | 48.70% | -68.46% | 1.035 | 0.711 | 93.80% | -68.46% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | staggered | 33.56% | -46.17% | 1.031 | 0.727 | 90.15% | -23.57% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | staggered | 33.56% | -46.17% | 1.031 | 0.727 | 90.15% | -23.57% |

## Top 25 by after-tax Calmar

| Name | Overlay | Offsets | CAGR | MDD | Sharpe | Calmar | RollRel | GFC MDD |
|---|---|---|---|---|---|---|---|---|
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_fixed_none | none | fixed | 59.47% | -63.19% | 1.010 | 0.941 | 95.21% | -63.19% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_fixed_none | none | fixed | 59.47% | -63.19% | 1.010 | 0.941 | 95.21% | -63.19% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 41.07% | -47.31% | 1.029 | 0.868 | 92.25% | -23.65% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 41.07% | -47.31% | 1.029 | 0.868 | 92.25% | -23.65% |
| evo_momv2_us_stocks_raw_13612_lb6_12_top15_reb3_off0_fixed_none | none | fixed | 54.19% | -63.37% | 1.088 | 0.855 | 94.69% | -63.37% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_none | none | staggered | 51.96% | -61.10% | 1.134 | 0.850 | 95.08% | -61.10% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_none | none | staggered | 51.96% | -61.10% | 1.134 | 0.850 | 95.08% | -61.10% |
| evo_momv2_us_stocks_raw_13612_lb6_12_top15_reb3_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 36.89% | -43.83% | 0.912 | 0.842 | 91.59% | -24.68% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_fixed_market_sma200_monthly | market_sma200_monthly | fixed | 45.06% | -53.55% | 0.852 | 0.841 | 92.77% | -34.87% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_fixed_market_sma200_monthly | market_sma200_monthly | fixed | 45.06% | -53.55% | 0.852 | 0.841 | 92.77% | -34.87% |
| evo_momv2_us_stocks_raw_13612_lb6_12_top15_reb3_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 36.85% | -45.95% | 0.902 | 0.802 | 90.73% | -23.91% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 43.60% | -54.53% | 0.842 | 0.800 | 94.11% | -29.29% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 43.60% | -54.53% | 0.842 | 0.800 | 94.11% | -29.29% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 38.31% | -48.49% | 0.991 | 0.790 | 92.88% | -26.03% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 38.31% | -48.49% | 0.991 | 0.790 | 92.88% | -26.03% |
| evo_momv2_us_stocks_raw_13612_lb6_12_top15_reb3_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 40.36% | -51.59% | 0.951 | 0.782 | 93.47% | -28.17% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 38.91% | -50.32% | 0.935 | 0.773 | 92.67% | -18.30% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 38.91% | -50.32% | 0.935 | 0.773 | 92.67% | -18.30% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_staggered_none | none | staggered | 49.92% | -66.03% | 1.061 | 0.756 | 95.18% | -66.03% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_staggered_none | none | staggered | 49.92% | -66.03% | 1.061 | 0.756 | 95.18% | -66.03% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 40.01% | -53.51% | 0.962 | 0.748 | 93.92% | -21.97% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 40.01% | -53.51% | 0.962 | 0.748 | 93.92% | -21.97% |
| evo_momv2_us_stocks_raw_13612_lb6_12_top15_reb3_off0_fixed_market_sma200_monthly | market_sma200_monthly | fixed | 40.09% | -54.09% | 0.912 | 0.741 | 92.24% | -32.75% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | staggered | 33.56% | -46.17% | 1.031 | 0.727 | 90.15% | -23.57% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | staggered | 33.56% | -46.17% | 1.031 | 0.727 | 90.15% | -23.57% |

## PBO summary

| group | pbo | n_configs | n_configs_total | sampled | pass |
|---|---|---|---|---|---|
| all | 0.8849206349206349 | 72 | 72 | False | False |
| mechanism:clenow_trend | 0.6468253968253969 | 12 | 12 | False | False |
| mechanism:clenow_trend_abs_cash | 0.6468253968253969 | 12 | 12 | False | False |
| mechanism:raw_13612 | 0.7658730158730159 | 24 | 24 | False | False |
| mechanism:raw_13612_abs_cash | 0.5992063492063492 | 12 | 12 | False | False |
| mechanism:raw_13612_inverse_vol | 0.626984126984127 | 12 | 12 | False | False |
