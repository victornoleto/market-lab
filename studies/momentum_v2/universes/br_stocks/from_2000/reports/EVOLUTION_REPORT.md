# Finalist Evolution — `br_stocks`

Status: **research-only**, `promotion_eligible=false`. The Postgres universe plus survivorship filters *mitigate* but do not *eliminate* bias — the yfinance feed never captured most fully delisted names, so historical screens stay inflated `[advances_fin_ml, p.208-211]`. Main rankings are after Brazil's annual 15% realized-gain tax, gross of transaction costs/slippage. Benchmark: SPY.

Finalists are selected by after-tax Sharpe and Calmar (return/risk-adjusted lens). Evolutions add MA overlays (SPY SMA200 monthly/daily, stock SMA100, combos) and fixed/staggered offsets; these are literature-grounded stress diagnostics tested after the broad map, so the effective trial count exceeds this file `[advances_fin_ml, p.273-275]`.

## Scope

- Start: `2000-01-01`
- Rows: `120`

## Key readings

- Best after-tax Sharpe: `evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb1_off0_fixed_none` — Sharpe `1.312`, CAGR `35.27%`, MDD `-56.13%`, overlay `none`.
- Best after-tax Calmar: `evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top3_reb1_off0_fixed_market_sma200_daily` — Calmar `0.876`, CAGR `27.22%`, MDD `-31.08%`, overlay `market_sma200_daily`.

## Plots

- [evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb1_off0_fixed_none_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb1_off0_fixed_none_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb1_off0_staggered_none_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb1_off0_staggered_none_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_lb6_top5_reb1_off0_fixed_none_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_lb6_top5_reb1_off0_fixed_none_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_lb6_top5_reb1_off0_staggered_none_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_lb6_top5_reb1_off0_staggered_none_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_fixed_stock_sma100_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_fixed_stock_sma100_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_staggered_stock_sma100_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_staggered_stock_sma100_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb1_off0_fixed_stock_sma100_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb1_off0_fixed_stock_sma100_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb1_off0_staggered_stock_sma100_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb1_off0_staggered_stock_sma100_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_stock_sma100_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_stock_sma100_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_staggered_stock_sma100_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_staggered_stock_sma100_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_lb6_top5_reb1_off0_fixed_stock_sma100_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_lb6_top5_reb1_off0_fixed_stock_sma100_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_lb6_top5_reb1_off0_staggered_stock_sma100_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_lb6_top5_reb1_off0_staggered_stock_sma100_vs_BOVA11.SA.png)

## Top 25 by after-tax Sharpe

| Name | Overlay | Offsets | CAGR | MDD | Sharpe | Calmar | RollRel | GFC MDD |
|---|---|---|---|---|---|---|---|---|
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb1_off0_fixed_none | none | fixed | 35.27% | -56.13% | 1.312 | 0.628 | 96.31% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb1_off0_staggered_none | none | staggered | 35.27% | -56.13% | 1.312 | 0.628 | 96.31% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_top5_reb1_off0_fixed_none | none | fixed | 35.16% | -56.13% | 1.308 | 0.626 | 96.23% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_top5_reb1_off0_staggered_none | none | staggered | 35.16% | -56.13% | 1.308 | 0.626 | 96.23% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_fixed_stock_sma100 | stock_sma100 | fixed | 33.34% | -45.60% | 1.293 | 0.731 | 95.71% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_staggered_stock_sma100 | stock_sma100 | staggered | 33.34% | -45.60% | 1.293 | 0.731 | 95.71% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb1_off0_fixed_stock_sma100 | stock_sma100 | fixed | 34.46% | -56.13% | 1.292 | 0.614 | 95.98% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb1_off0_staggered_stock_sma100 | stock_sma100 | staggered | 34.46% | -56.13% | 1.292 | 0.614 | 95.98% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_stock_sma100 | stock_sma100 | fixed | 33.28% | -45.60% | 1.291 | 0.730 | 95.70% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_staggered_stock_sma100 | stock_sma100 | staggered | 33.28% | -45.60% | 1.291 | 0.730 | 95.70% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_top5_reb1_off0_fixed_stock_sma100 | stock_sma100 | fixed | 34.38% | -56.13% | 1.289 | 0.613 | 95.90% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_top5_reb1_off0_staggered_stock_sma100 | stock_sma100 | staggered | 34.38% | -56.13% | 1.289 | 0.613 | 95.90% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_fixed_none | none | fixed | 33.44% | -45.60% | 1.284 | 0.733 | 96.29% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_staggered_none | none | staggered | 33.44% | -45.60% | 1.284 | 0.733 | 96.29% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_none | none | fixed | 33.41% | -45.60% | 1.284 | 0.733 | 96.29% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_staggered_none | none | staggered | 33.41% | -45.60% | 1.284 | 0.733 | 96.29% | n/a |
| evo_momv2_br_stocks_composite_mom_lowvol_inverse_vol_lb3_6_12_top5_reb1_off0_fixed_none | none | fixed | 25.80% | -37.03% | 1.280 | 0.697 | 94.37% | n/a |
| evo_momv2_br_stocks_composite_mom_lowvol_inverse_vol_lb3_6_12_top5_reb1_off0_staggered_none | none | staggered | 25.80% | -37.03% | 1.280 | 0.697 | 94.37% | n/a |
| evo_momv2_br_stocks_composite_mom_lowvol_lb3_6_12_top5_reb1_off0_fixed_none | none | fixed | 26.34% | -41.09% | 1.277 | 0.641 | 94.35% | n/a |
| evo_momv2_br_stocks_composite_mom_lowvol_lb3_6_12_top5_reb1_off0_staggered_none | none | staggered | 26.34% | -41.09% | 1.277 | 0.641 | 94.35% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top3_reb1_off0_fixed_none | none | fixed | 36.52% | -49.40% | 1.264 | 0.739 | 95.22% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top3_reb1_off0_staggered_none | none | staggered | 36.52% | -49.40% | 1.264 | 0.739 | 95.22% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top3_reb1_off0_fixed_none | none | fixed | 36.50% | -49.40% | 1.263 | 0.739 | 95.22% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top3_reb1_off0_staggered_none | none | staggered | 36.50% | -49.40% | 1.263 | 0.739 | 95.22% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top3_reb1_off0_fixed_stock_sma100 | stock_sma100 | fixed | 35.70% | -49.40% | 1.251 | 0.723 | 95.11% | n/a |

## Top 25 by after-tax Calmar

| Name | Overlay | Offsets | CAGR | MDD | Sharpe | Calmar | RollRel | GFC MDD |
|---|---|---|---|---|---|---|---|---|
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top3_reb1_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 27.22% | -31.08% | 1.198 | 0.876 | 95.68% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top3_reb1_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 27.22% | -31.08% | 1.198 | 0.876 | 95.68% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top3_reb1_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 27.22% | -31.08% | 1.198 | 0.876 | 95.68% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top3_reb1_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 27.22% | -31.08% | 1.198 | 0.876 | 95.68% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top3_reb1_off0_fixed_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | fixed | 26.24% | -31.08% | 1.167 | 0.844 | 95.53% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top3_reb1_off0_staggered_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | staggered | 26.24% | -31.08% | 1.167 | 0.844 | 95.53% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top3_reb1_off0_fixed_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | fixed | 26.24% | -31.08% | 1.167 | 0.844 | 95.53% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top3_reb1_off0_staggered_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | staggered | 26.24% | -31.08% | 1.167 | 0.844 | 95.53% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 21.52% | -27.75% | 1.093 | 0.775 | 94.17% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 21.52% | -27.75% | 1.093 | 0.775 | 94.17% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 21.52% | -27.75% | 1.093 | 0.775 | 94.17% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 21.52% | -27.75% | 1.093 | 0.775 | 94.17% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb1_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 20.55% | -26.91% | 1.077 | 0.764 | 93.22% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb1_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 20.55% | -26.91% | 1.077 | 0.764 | 93.22% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_top5_reb1_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 20.55% | -26.91% | 1.077 | 0.764 | 93.22% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_top5_reb1_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 20.55% | -26.91% | 1.077 | 0.764 | 93.22% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_fixed_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | fixed | 21.32% | -28.40% | 1.083 | 0.751 | 94.15% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_staggered_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | staggered | 21.32% | -28.40% | 1.083 | 0.751 | 94.15% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | fixed | 21.32% | -28.40% | 1.083 | 0.751 | 94.15% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_staggered_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | staggered | 21.32% | -28.40% | 1.083 | 0.751 | 94.15% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top3_reb1_off0_fixed_none | none | fixed | 36.52% | -49.40% | 1.264 | 0.739 | 95.22% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top3_reb1_off0_staggered_none | none | staggered | 36.52% | -49.40% | 1.264 | 0.739 | 95.22% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top3_reb1_off0_fixed_none | none | fixed | 36.50% | -49.40% | 1.263 | 0.739 | 95.22% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top3_reb1_off0_staggered_none | none | staggered | 36.50% | -49.40% | 1.263 | 0.739 | 95.22% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_fixed_market_sma200_monthly | market_sma200_monthly | fixed | 23.74% | -32.32% | 1.180 | 0.735 | 94.35% | n/a |

## PBO summary

| group | pbo | n_configs | n_configs_total | sampled | pass |
|---|---|---|---|---|---|
| all | 0.7579365079365079 | 120 | 120 | False | False |
| mechanism:composite_mom_lowvol | 0.6587301587301587 | 12 | 12 | False | False |
| mechanism:composite_mom_lowvol_inverse_vol | 0.3531746031746032 | 12 | 12 | False | True |
| mechanism:vol_adjusted_13612 | 0.5555555555555556 | 48 | 48 | False | False |
| mechanism:vol_adjusted_13612_abs_cash | 0.5515873015873016 | 48 | 48 | False | False |
