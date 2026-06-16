# Finalist Evolution — `us_stocks`

Status: **research-only**, `promotion_eligible=false`. The Postgres universe plus survivorship filters *mitigate* but do not *eliminate* bias — the yfinance feed never captured most fully delisted names, so historical screens stay inflated `[advances_fin_ml, p.208-211]`. Main rankings are after Brazil's annual 15% realized-gain tax, gross of transaction costs/slippage. Benchmark: SPY.

Finalists are selected by after-tax Sharpe and Calmar (return/risk-adjusted lens). Evolutions add MA overlays (SPY SMA200 monthly/daily, stock SMA100, combos) and fixed/staggered offsets; these are literature-grounded stress diagnostics tested after the broad map, so the effective trial count exceeds this file `[advances_fin_ml, p.273-275]`.

## Scope

- Start: `2000-01-01`
- Rows: `144`

## Key readings

- Best after-tax Sharpe: `evo_momv2_us_stocks_raw_13612_lb6_top20_reb3_off0_staggered_stock_sma100` — Sharpe `1.214`, CAGR `43.76%`, MDD `-63.17%`, overlay `stock_sma100`.
- Best after-tax Calmar: `evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_staggered_none` — Calmar `1.096`, CAGR `72.05%`, MDD `-65.72%`, overlay `none`.

## Plots

- [evo_momv2_us_stocks_raw_13612_lb6_top20_reb3_off0_staggered_stock_sma100_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_lb6_top20_reb3_off0_staggered_stock_sma100_vs_SPY.png)
- [evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb3_off0_staggered_stock_sma100_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb3_off0_staggered_stock_sma100_vs_SPY.png)
- [evo_momv2_us_stocks_raw_13612_lb6_top20_reb3_off0_staggered_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_lb6_top20_reb3_off0_staggered_none_vs_SPY.png)
- [evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb3_off0_staggered_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb3_off0_staggered_none_vs_SPY.png)
- [evo_momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top20_reb3_off0_fixed_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top20_reb3_off0_fixed_none_vs_SPY.png)
- [evo_momv2_us_stocks_raw_13612_lb6_top20_reb3_off0_staggered_market_sma200_daily_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_lb6_top20_reb3_off0_staggered_market_sma200_daily_vs_SPY.png)
- [evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb3_off0_staggered_market_sma200_daily_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb3_off0_staggered_market_sma200_daily_vs_SPY.png)
- [evo_momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top20_reb3_off0_fixed_stock_sma100_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top20_reb3_off0_fixed_stock_sma100_vs_SPY.png)
- [evo_momv2_us_stocks_raw_13612_lb6_top20_reb3_off0_fixed_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_lb6_top20_reb3_off0_fixed_none_vs_SPY.png)
- [evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb3_off0_fixed_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb3_off0_fixed_none_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_fixed_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_fixed_none_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_staggered_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_staggered_none_vs_SPY.png)

## Top 25 by after-tax Sharpe

| Name | Overlay | Offsets | CAGR | MDD | Sharpe | Calmar | RollRel | GFC MDD |
|---|---|---|---|---|---|---|---|---|
| evo_momv2_us_stocks_raw_13612_lb6_top20_reb3_off0_staggered_stock_sma100 | stock_sma100 | staggered | 43.76% | -63.17% | 1.214 | 0.693 | 95.68% | -63.17% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb3_off0_staggered_stock_sma100 | stock_sma100 | staggered | 43.76% | -63.17% | 1.214 | 0.693 | 95.68% | -63.17% |
| evo_momv2_us_stocks_raw_13612_lb6_top20_reb3_off0_staggered_none | none | staggered | 50.29% | -64.93% | 1.174 | 0.775 | 95.63% | -64.93% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb3_off0_staggered_none | none | staggered | 50.29% | -64.93% | 1.174 | 0.775 | 95.63% | -64.93% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top20_reb3_off0_fixed_none | none | fixed | 43.28% | -64.69% | 1.163 | 0.669 | 95.07% | -64.69% |
| evo_momv2_us_stocks_raw_13612_lb6_top20_reb3_off0_fixed_none | none | fixed | 50.01% | -58.27% | 1.148 | 0.858 | 94.55% | -58.27% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb3_off0_fixed_none | none | fixed | 50.01% | -58.27% | 1.148 | 0.858 | 94.55% | -58.27% |
| evo_momv2_us_stocks_raw_13612_lb6_top20_reb3_off0_fixed_stock_sma100 | stock_sma100 | fixed | 41.99% | -56.10% | 1.142 | 0.749 | 94.15% | -56.10% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb3_off0_fixed_stock_sma100 | stock_sma100 | fixed | 41.99% | -56.10% | 1.142 | 0.749 | 94.15% | -56.10% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_fixed_none | none | fixed | 42.93% | -58.00% | 1.133 | 0.740 | 94.52% | -58.00% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_staggered_none | none | staggered | 42.93% | -58.00% | 1.133 | 0.740 | 94.52% | -58.00% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0_fixed_none | none | fixed | 42.93% | -58.00% | 1.133 | 0.740 | 94.52% | -58.00% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0_staggered_none | none | staggered | 42.93% | -58.00% | 1.133 | 0.740 | 94.52% | -58.00% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0_fixed_none | none | fixed | 47.49% | -58.94% | 1.128 | 0.806 | 94.31% | -58.94% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0_staggered_none | none | staggered | 47.49% | -58.94% | 1.128 | 0.806 | 94.31% | -58.94% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top20_reb3_off0_staggered_none | none | staggered | 39.64% | -67.08% | 1.118 | 0.591 | 94.51% | -67.08% |
| evo_momv2_us_stocks_raw_13612_lb6_top20_reb3_off0_staggered_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | staggered | 33.63% | -45.03% | 1.116 | 0.747 | 93.25% | -21.18% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb3_off0_staggered_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | staggered | 33.63% | -45.03% | 1.116 | 0.747 | 93.25% | -21.18% |
| evo_momv2_us_stocks_raw_13612_lb6_top20_reb3_off0_staggered_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | staggered | 32.33% | -45.87% | 1.115 | 0.705 | 93.63% | -20.71% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb3_off0_staggered_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | staggered | 32.33% | -45.87% | 1.115 | 0.705 | 93.63% | -20.71% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top20_reb3_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 32.35% | -41.24% | 1.085 | 0.784 | 92.94% | -23.11% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0_fixed_market_sma200_monthly | market_sma200_monthly | fixed | 39.37% | -45.59% | 1.084 | 0.863 | 92.82% | -17.57% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 39.37% | -45.59% | 1.084 | 0.863 | 92.82% | -17.57% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_fixed_market_sma200_monthly | market_sma200_monthly | fixed | 35.08% | -49.85% | 1.083 | 0.704 | 92.88% | -14.75% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 35.08% | -49.85% | 1.083 | 0.704 | 92.88% | -14.75% |

## Top 25 by after-tax Calmar

| Name | Overlay | Offsets | CAGR | MDD | Sharpe | Calmar | RollRel | GFC MDD |
|---|---|---|---|---|---|---|---|---|
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_staggered_none | none | staggered | 72.05% | -65.72% | 0.798 | 1.096 | 94.43% | -65.52% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top5_reb6_off0_staggered_none | none | staggered | 72.05% | -65.72% | 0.798 | 1.096 | 94.43% | -65.52% |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 56.82% | -52.53% | 0.681 | 1.082 | 91.80% | -26.08% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top5_reb6_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 56.82% | -52.53% | 0.681 | 1.082 | 91.80% | -26.08% |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_fixed_none | none | fixed | 68.70% | -66.81% | 0.787 | 1.028 | 92.82% | -66.81% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top5_reb6_off0_fixed_none | none | fixed | 68.70% | -66.81% | 0.787 | 1.028 | 92.82% | -66.81% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb3_6_12_top10_reb3_off0_fixed_none | none | fixed | 64.44% | -63.94% | 0.680 | 1.008 | 93.54% | -63.94% |
| evo_momv2_us_stocks_raw_13612_lb3_6_12_top10_reb3_off0_fixed_none | none | fixed | 64.44% | -63.94% | 0.680 | 1.008 | 93.54% | -63.94% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb1_3_6_12_top10_reb3_off0_fixed_none | none | fixed | 67.10% | -66.68% | 0.695 | 1.006 | 93.35% | -65.97% |
| evo_momv2_us_stocks_raw_13612_lb1_3_6_12_top10_reb3_off0_fixed_none | none | fixed | 67.10% | -66.68% | 0.695 | 1.006 | 93.35% | -65.97% |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_fixed_stock_sma100 | stock_sma100 | fixed | 65.17% | -64.90% | 0.766 | 1.004 | 93.04% | -63.66% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top5_reb6_off0_fixed_stock_sma100 | stock_sma100 | fixed | 65.17% | -64.90% | 0.766 | 1.004 | 93.04% | -63.66% |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_staggered_stock_sma100 | stock_sma100 | staggered | 65.06% | -64.88% | 1.052 | 1.003 | 94.30% | -64.68% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top5_reb6_off0_staggered_stock_sma100 | stock_sma100 | staggered | 65.06% | -64.88% | 1.052 | 1.003 | 94.30% | -64.68% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb1_3_6_12_top10_reb3_off0_staggered_none | none | staggered | 70.20% | -70.12% | 1.017 | 1.001 | 93.83% | -70.12% |
| evo_momv2_us_stocks_raw_13612_lb1_3_6_12_top10_reb3_off0_staggered_none | none | staggered | 70.20% | -70.12% | 1.017 | 1.001 | 93.83% | -70.12% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb3_6_12_top10_reb3_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 52.67% | -52.65% | 0.862 | 1.000 | 91.06% | -22.19% |
| evo_momv2_us_stocks_raw_13612_lb3_6_12_top10_reb3_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 52.67% | -52.65% | 0.862 | 1.000 | 91.06% | -22.19% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb3_6_12_top10_reb3_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 52.59% | -52.85% | 0.865 | 0.995 | 91.31% | -24.84% |
| evo_momv2_us_stocks_raw_13612_lb3_6_12_top10_reb3_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 52.59% | -52.85% | 0.865 | 0.995 | 91.31% | -24.84% |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 58.30% | -59.09% | 0.693 | 0.987 | 94.18% | -23.50% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top5_reb6_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 58.30% | -59.09% | 0.693 | 0.987 | 94.18% | -23.50% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb1_3_6_12_top10_reb3_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 54.33% | -55.37% | 0.878 | 0.981 | 91.72% | -22.40% |
| evo_momv2_us_stocks_raw_13612_lb1_3_6_12_top10_reb3_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 54.33% | -55.37% | 0.878 | 0.981 | 91.72% | -22.40% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb3_6_12_top10_reb3_off0_staggered_none | none | staggered | 67.46% | -69.68% | 0.994 | 0.968 | 93.37% | -69.68% |

## PBO summary

| group | pbo | n_configs | n_configs_total | sampled | pass |
|---|---|---|---|---|---|
| all | 0.5079365079365079 | 144 | 144 | False | False |
| mechanism:clenow_trend | 0.373015873015873 | 24 | 24 | False | True |
| mechanism:clenow_trend_abs_cash | 0.25793650793650796 | 12 | 12 | False | True |
| mechanism:raw_13612 | 0.3134920634920635 | 48 | 48 | False | True |
| mechanism:raw_13612_abs_cash | 0.3134920634920635 | 48 | 48 | False | True |
| mechanism:raw_13612_inverse_vol | 0.6428571428571429 | 12 | 12 | False | False |
