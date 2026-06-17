# Finalist Evolution — `us_stocks`

Status: **research-only**, `promotion_eligible=false`. The Postgres universe plus survivorship filters *mitigate* but do not *eliminate* bias — the yfinance feed never captured most fully delisted names, so historical screens stay inflated `[advances_fin_ml, p.208-211]`. Main rankings are after Brazil's annual 15% realized-gain tax, gross of transaction costs/slippage. Benchmark: SPY.

Finalists are selected by after-tax Sharpe and Calmar (return/risk-adjusted lens). Evolutions add MA overlays (SPY SMA200 monthly/daily, stock SMA100, combos) and fixed/staggered offsets; these are literature-grounded stress diagnostics tested after the broad map, so the effective trial count exceeds this file `[advances_fin_ml, p.273-275]`.

## Scope

- Start: `2000-01-01`
- Rows: `132`

## Key readings

- Best after-tax Sharpe: `evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb6_off0_fixed_market_sma200_monthly` — Sharpe `0.949`, CAGR `26.31%`, MDD `-42.73%`, overlay `market_sma200_monthly`.
- Best after-tax Calmar: `evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_fixed_market_sma200_monthly` — Calmar `0.620`, CAGR `25.55%`, MDD `-41.17%`, overlay `market_sma200_monthly`.

## Plots

_No plots._

## Top 25 by after-tax Sharpe

| Name | Overlay | Offsets | CAGR | MDD | Sharpe | Calmar | RollRel | GFC MDD |
|---|---|---|---|---|---|---|---|---|
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb6_off0_fixed_market_sma200_monthly | market_sma200_monthly | fixed | 26.31% | -42.73% | 0.949 | 0.616 | 79.47% | -27.66% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb6_off0_fixed_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | fixed | 25.69% | -42.73% | 0.936 | 0.601 | 79.18% | -27.66% |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_fixed_market_sma200_monthly | market_sma200_monthly | fixed | 25.55% | -41.17% | 0.913 | 0.620 | 78.74% | -27.53% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb6_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 20.33% | -39.63% | 0.889 | 0.513 | 76.93% | -10.86% |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_fixed_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | fixed | 24.45% | -41.17% | 0.888 | 0.594 | 77.08% | -27.53% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb6_off0_fixed_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | fixed | 19.71% | -41.41% | 0.874 | 0.476 | 76.25% | -10.86% |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 19.52% | -39.99% | 0.842 | 0.488 | 75.85% | -11.45% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb6_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 18.11% | -36.00% | 0.817 | 0.503 | 76.47% | -28.88% |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_fixed_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | fixed | 18.52% | -42.46% | 0.814 | 0.436 | 74.09% | -11.45% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb6_off0_staggered_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | staggered | 17.77% | -35.08% | 0.808 | 0.507 | 74.93% | -28.88% |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 18.26% | -39.17% | 0.803 | 0.466 | 78.16% | -29.50% |
| evo_momv2_us_stocks_vol_adjusted_13612_lb6_top5_reb6_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 14.15% | -29.44% | 0.803 | 0.481 | 56.32% | -12.76% |
| evo_momv2_us_stocks_vol_adjusted_13612_lb6_top5_reb6_off0_fixed_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | fixed | 14.15% | -29.44% | 0.803 | 0.481 | 56.32% | -12.76% |
| evo_momv2_us_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb6_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 14.15% | -29.44% | 0.803 | 0.481 | 56.32% | -12.76% |
| evo_momv2_us_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb6_off0_fixed_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | fixed | 14.15% | -29.44% | 0.803 | 0.481 | 56.32% | -12.76% |
| evo_momv2_us_stocks_vol_adjusted_13612_lb6_top5_reb6_off0_fixed_market_sma200_monthly | market_sma200_monthly | fixed | 16.62% | -47.48% | 0.795 | 0.350 | 49.12% | -28.30% |
| evo_momv2_us_stocks_vol_adjusted_13612_lb6_top5_reb6_off0_fixed_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | fixed | 16.62% | -47.48% | 0.795 | 0.350 | 49.12% | -28.30% |
| evo_momv2_us_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb6_off0_fixed_market_sma200_monthly | market_sma200_monthly | fixed | 16.62% | -47.48% | 0.795 | 0.350 | 49.12% | -28.30% |
| evo_momv2_us_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb6_off0_fixed_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | fixed | 16.62% | -47.48% | 0.795 | 0.350 | 49.12% | -28.30% |
| evo_momv2_us_stocks_vol_adjusted_13612_lb6_top5_reb6_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 13.66% | -37.17% | 0.794 | 0.368 | 56.33% | -23.78% |
| evo_momv2_us_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb6_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 13.66% | -37.17% | 0.794 | 0.368 | 56.33% | -23.78% |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_staggered_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | staggered | 17.85% | -37.56% | 0.793 | 0.475 | 76.44% | -29.50% |
| evo_momv2_us_stocks_vol_adjusted_13612_lb6_top5_reb6_off0_staggered_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | staggered | 13.59% | -37.17% | 0.791 | 0.366 | 56.14% | -23.78% |
| evo_momv2_us_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb6_off0_staggered_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | staggered | 13.59% | -37.17% | 0.791 | 0.366 | 56.14% | -23.78% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb3_6_12_top3_reb6_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 19.51% | -45.53% | 0.788 | 0.428 | 78.90% | -28.20% |

## Top 25 by after-tax Calmar

| Name | Overlay | Offsets | CAGR | MDD | Sharpe | Calmar | RollRel | GFC MDD |
|---|---|---|---|---|---|---|---|---|
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_fixed_market_sma200_monthly | market_sma200_monthly | fixed | 25.55% | -41.17% | 0.913 | 0.620 | 78.74% | -27.53% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb6_off0_fixed_market_sma200_monthly | market_sma200_monthly | fixed | 26.31% | -42.73% | 0.949 | 0.616 | 79.47% | -27.66% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb6_off0_fixed_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | fixed | 25.69% | -42.73% | 0.936 | 0.601 | 79.18% | -27.66% |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_fixed_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | fixed | 24.45% | -41.17% | 0.888 | 0.594 | 77.08% | -27.53% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb6_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 20.33% | -39.63% | 0.889 | 0.513 | 76.93% | -10.86% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb6_off0_staggered_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | staggered | 17.77% | -35.08% | 0.808 | 0.507 | 74.93% | -28.88% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb6_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 18.11% | -36.00% | 0.817 | 0.503 | 76.47% | -28.88% |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 19.52% | -39.99% | 0.842 | 0.488 | 75.85% | -11.45% |
| evo_momv2_us_stocks_vol_adjusted_13612_lb6_top5_reb6_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 14.15% | -29.44% | 0.803 | 0.481 | 56.32% | -12.76% |
| evo_momv2_us_stocks_vol_adjusted_13612_lb6_top5_reb6_off0_fixed_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | fixed | 14.15% | -29.44% | 0.803 | 0.481 | 56.32% | -12.76% |
| evo_momv2_us_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb6_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 14.15% | -29.44% | 0.803 | 0.481 | 56.32% | -12.76% |
| evo_momv2_us_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb6_off0_fixed_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | fixed | 14.15% | -29.44% | 0.803 | 0.481 | 56.32% | -12.76% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb6_off0_fixed_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | fixed | 19.71% | -41.41% | 0.874 | 0.476 | 76.25% | -10.86% |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_staggered_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | staggered | 17.85% | -37.56% | 0.793 | 0.475 | 76.44% | -29.50% |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 18.26% | -39.17% | 0.803 | 0.466 | 78.16% | -29.50% |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_fixed_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | fixed | 18.52% | -42.46% | 0.814 | 0.436 | 74.09% | -11.45% |
| evo_momv2_us_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb6_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 11.55% | -26.72% | 0.752 | 0.432 | 38.01% | -14.06% |
| evo_momv2_us_stocks_vol_adjusted_13612_lb6_top5_reb6_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 11.53% | -26.72% | 0.750 | 0.431 | 37.49% | -14.06% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb3_6_12_top3_reb6_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 19.51% | -45.53% | 0.788 | 0.428 | 78.90% | -28.20% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb3_6_12_top3_reb6_off0_staggered_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | staggered | 19.36% | -45.52% | 0.787 | 0.425 | 78.40% | -28.16% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top3_reb6_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 19.06% | -44.89% | 0.778 | 0.425 | 77.55% | -27.49% |
| evo_momv2_us_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb6_off0_staggered_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | staggered | 11.31% | -26.72% | 0.739 | 0.423 | 36.60% | -14.06% |
| evo_momv2_us_stocks_vol_adjusted_13612_lb6_top5_reb6_off0_staggered_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | staggered | 11.29% | -26.72% | 0.737 | 0.422 | 36.05% | -14.06% |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top3_reb6_off0_staggered_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | staggered | 18.92% | -44.88% | 0.779 | 0.422 | 77.38% | -27.46% |
| evo_momv2_us_stocks_vol_adjusted_13612_inverse_vol_lb6_top5_reb6_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 12.18% | -29.40% | 0.757 | 0.414 | 49.80% | -12.74% |

## PBO summary

| group | pbo | n_configs | n_configs_total | sampled | pass |
|---|---|---|---|---|---|
| all | 0.6428571428571429 | 132 | 132 | False | False |
| mechanism:raw_13612 | 0.6706349206349206 | 36 | 36 | False | False |
| mechanism:raw_13612_abs_cash | 0.8015873015873016 | 24 | 24 | False | False |
| mechanism:raw_13612_inverse_vol | 0.623015873015873 | 36 | 36 | False | False |
| mechanism:vol_adjusted_13612 | 0.8968253968253969 | 12 | 12 | False | False |
| mechanism:vol_adjusted_13612_abs_cash | 0.9007936507936508 | 12 | 12 | False | False |
| mechanism:vol_adjusted_13612_inverse_vol | 0.8849206349206349 | 12 | 12 | False | False |
