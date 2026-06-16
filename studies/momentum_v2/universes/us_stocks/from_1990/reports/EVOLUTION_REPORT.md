# Finalist Evolution — `us_stocks`

Status: **research-only**, `promotion_eligible=false`. The Postgres universe plus survivorship filters *mitigate* but do not *eliminate* bias — the yfinance feed never captured most fully delisted names, so historical screens stay inflated `[advances_fin_ml, p.208-211]`. Main rankings are after Brazil's annual 15% realized-gain tax, gross of transaction costs/slippage. Benchmark: SPY.

Finalists are selected by after-tax Sharpe and Calmar (return/risk-adjusted lens). Evolutions add MA overlays (SPY SMA200 monthly/daily, stock SMA100, combos) and fixed/staggered offsets; these are literature-grounded stress diagnostics tested after the broad map, so the effective trial count exceeds this file `[advances_fin_ml, p.273-275]`.

## Scope

- Start: `1990-01-01`
- Rows: `144`

## Key readings

- Best after-tax Sharpe: `evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_fixed_none` — Sharpe `1.214`, CAGR `46.42%`, MDD `-58.29%`, overlay `none`.
- Best after-tax Calmar: `evo_momv2_us_stocks_raw_13612_lb6_top5_reb3_off0_staggered_none` — Calmar `0.895`, CAGR `65.12%`, MDD `-72.73%`, overlay `none`.

## Plots

- [evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb1_off0_fixed_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb1_off0_fixed_none_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb1_off0_staggered_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb1_off0_staggered_none_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb1_off0_fixed_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb1_off0_fixed_none_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb1_off0_staggered_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb1_off0_staggered_none_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_fixed_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_fixed_none_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_staggered_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_staggered_none_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0_fixed_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0_fixed_none_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0_staggered_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0_staggered_none_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0_fixed_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0_fixed_none_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0_staggered_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0_staggered_none_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb1_off0_fixed_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb1_off0_fixed_none_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb1_off0_staggered_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb1_off0_staggered_none_vs_SPY.png)

## Top 25 by after-tax Sharpe

| Name | Overlay | Offsets | CAGR | MDD | Sharpe | Calmar | RollRel | GFC MDD |
|---|---|---|---|---|---|---|---|---|
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_fixed_none | none | fixed | 46.42% | -58.29% | 1.214 | 0.796 | 95.09% | -58.00% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_staggered_none | none | staggered | 46.42% | -58.29% | 1.214 | 0.796 | 95.09% | -58.00% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0_fixed_none | none | fixed | 46.42% | -58.29% | 1.214 | 0.796 | 95.09% | -58.00% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0_staggered_none | none | staggered | 46.42% | -58.29% | 1.214 | 0.796 | 95.09% | -58.00% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb1_off0_fixed_none | none | fixed | 43.03% | -59.57% | 1.201 | 0.722 | 95.21% | -59.57% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb1_off0_staggered_none | none | staggered | 43.03% | -59.57% | 1.201 | 0.722 | 95.21% | -59.57% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb1_off0_fixed_none | none | fixed | 43.03% | -59.57% | 1.201 | 0.722 | 95.21% | -59.57% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb1_off0_staggered_none | none | staggered | 43.03% | -59.57% | 1.201 | 0.722 | 95.21% | -59.57% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0_fixed_none | none | fixed | 51.13% | -63.00% | 1.201 | 0.812 | 95.03% | -58.94% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0_staggered_none | none | staggered | 51.13% | -63.00% | 1.201 | 0.812 | 95.03% | -58.94% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb1_off0_fixed_none | none | fixed | 51.13% | -63.00% | 1.201 | 0.812 | 95.03% | -58.94% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb1_off0_staggered_none | none | staggered | 51.13% | -63.00% | 1.201 | 0.812 | 95.03% | -58.94% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb1_off0_fixed_stock_sma100 | stock_sma100 | fixed | 40.67% | -63.04% | 1.171 | 0.645 | 94.66% | -63.04% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb1_off0_staggered_stock_sma100 | stock_sma100 | staggered | 40.67% | -63.04% | 1.171 | 0.645 | 94.66% | -63.04% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb1_off0_fixed_stock_sma100 | stock_sma100 | fixed | 40.67% | -63.04% | 1.171 | 0.645 | 94.66% | -63.04% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb1_off0_staggered_stock_sma100 | stock_sma100 | staggered | 40.67% | -63.04% | 1.171 | 0.645 | 94.66% | -63.04% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_fixed_stock_sma100 | stock_sma100 | fixed | 42.32% | -59.80% | 1.154 | 0.708 | 93.75% | -59.80% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_staggered_stock_sma100 | stock_sma100 | staggered | 42.32% | -59.80% | 1.154 | 0.708 | 93.75% | -59.80% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0_fixed_stock_sma100 | stock_sma100 | fixed | 42.32% | -59.80% | 1.154 | 0.708 | 93.75% | -59.80% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0_staggered_stock_sma100 | stock_sma100 | staggered | 42.32% | -59.80% | 1.154 | 0.708 | 93.75% | -59.80% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_fixed_market_sma200_monthly | market_sma200_monthly | fixed | 37.33% | -58.29% | 1.148 | 0.640 | 93.63% | -14.75% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 37.33% | -58.29% | 1.148 | 0.640 | 93.63% | -14.75% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0_fixed_market_sma200_monthly | market_sma200_monthly | fixed | 37.33% | -58.29% | 1.148 | 0.640 | 93.63% | -14.75% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 37.33% | -58.29% | 1.148 | 0.640 | 93.63% | -14.75% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0_fixed_stock_sma100 | stock_sma100 | fixed | 45.57% | -66.65% | 1.130 | 0.684 | 93.59% | -66.65% |

## Top 25 by after-tax Calmar

| Name | Overlay | Offsets | CAGR | MDD | Sharpe | Calmar | RollRel | GFC MDD |
|---|---|---|---|---|---|---|---|---|
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb3_off0_staggered_none | none | staggered | 65.12% | -72.73% | 0.794 | 0.895 | 93.57% | -72.73% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top5_reb3_off0_staggered_none | none | staggered | 65.12% | -72.73% | 0.794 | 0.895 | 93.57% | -72.73% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top10_reb1_off0_fixed_none | none | fixed | 58.32% | -65.79% | 0.931 | 0.886 | 94.91% | -65.79% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top10_reb1_off0_staggered_none | none | staggered | 58.32% | -65.79% | 0.931 | 0.886 | 94.91% | -65.79% |
| evo_momv2_us_stocks_raw_13612_lb6_top10_reb1_off0_fixed_none | none | fixed | 58.32% | -65.79% | 0.931 | 0.886 | 94.91% | -65.79% |
| evo_momv2_us_stocks_raw_13612_lb6_top10_reb1_off0_staggered_none | none | staggered | 58.32% | -65.79% | 0.931 | 0.886 | 94.91% | -65.79% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb1_3_6_12_top10_reb1_off0_fixed_none | none | fixed | 61.97% | -70.54% | 0.958 | 0.879 | 92.58% | -68.88% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb1_3_6_12_top10_reb1_off0_staggered_none | none | staggered | 61.97% | -70.54% | 0.958 | 0.879 | 92.58% | -68.88% |
| evo_momv2_us_stocks_raw_13612_lb1_3_6_12_top10_reb1_off0_fixed_none | none | fixed | 61.97% | -70.54% | 0.958 | 0.879 | 92.58% | -68.88% |
| evo_momv2_us_stocks_raw_13612_lb1_3_6_12_top10_reb1_off0_staggered_none | none | staggered | 61.97% | -70.54% | 0.958 | 0.879 | 92.58% | -68.88% |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb3_off0_fixed_none | none | fixed | 62.56% | -71.27% | 0.788 | 0.878 | 91.79% | -69.58% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top5_reb3_off0_fixed_none | none | fixed | 62.56% | -71.27% | 0.788 | 0.878 | 91.79% | -69.58% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0_fixed_none | none | fixed | 51.13% | -63.00% | 1.201 | 0.812 | 95.03% | -58.94% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0_staggered_none | none | staggered | 51.13% | -63.00% | 1.201 | 0.812 | 95.03% | -58.94% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb1_off0_fixed_none | none | fixed | 51.13% | -63.00% | 1.201 | 0.812 | 95.03% | -58.94% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb1_off0_staggered_none | none | staggered | 51.13% | -63.00% | 1.201 | 0.812 | 95.03% | -58.94% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_fixed_none | none | fixed | 46.42% | -58.29% | 1.214 | 0.796 | 95.09% | -58.00% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_staggered_none | none | staggered | 46.42% | -58.29% | 1.214 | 0.796 | 95.09% | -58.00% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0_fixed_none | none | fixed | 46.42% | -58.29% | 1.214 | 0.796 | 95.09% | -58.00% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0_staggered_none | none | staggered | 46.42% | -58.29% | 1.214 | 0.796 | 95.09% | -58.00% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top10_reb1_off0_fixed_stock_sma100 | stock_sma100 | fixed | 50.16% | -63.49% | 0.969 | 0.790 | 94.86% | -63.49% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top10_reb1_off0_staggered_stock_sma100 | stock_sma100 | staggered | 50.16% | -63.49% | 0.969 | 0.790 | 94.86% | -63.49% |
| evo_momv2_us_stocks_raw_13612_lb6_top10_reb1_off0_fixed_stock_sma100 | stock_sma100 | fixed | 50.16% | -63.49% | 0.969 | 0.790 | 94.86% | -63.49% |
| evo_momv2_us_stocks_raw_13612_lb6_top10_reb1_off0_staggered_stock_sma100 | stock_sma100 | staggered | 50.16% | -63.49% | 0.969 | 0.790 | 94.86% | -63.49% |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb3_off0_staggered_stock_sma100 | stock_sma100 | staggered | 54.43% | -70.55% | 1.067 | 0.771 | 93.56% | -70.55% |

## PBO summary

| group | pbo | n_configs | n_configs_total | sampled | pass |
|---|---|---|---|---|---|
| all | 0.08333333333333333 | 144 | 144 | False | True |
| mechanism:clenow_trend | 0.42857142857142855 | 36 | 36 | False | True |
| mechanism:clenow_trend_abs_cash | 0.42857142857142855 | 36 | 36 | False | True |
| mechanism:raw_13612 | 0.5079365079365079 | 36 | 36 | False | False |
| mechanism:raw_13612_abs_cash | 0.5079365079365079 | 36 | 36 | False | False |
