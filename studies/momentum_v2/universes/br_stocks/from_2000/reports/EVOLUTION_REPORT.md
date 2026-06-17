# Finalist Evolution — `br_stocks`

Status: **research-only**, `promotion_eligible=false`. The Postgres universe plus survivorship filters *mitigate* but do not *eliminate* bias — the yfinance feed never captured most fully delisted names, so historical screens stay inflated `[advances_fin_ml, p.208-211]`. Main rankings are after Brazil's annual 15% realized-gain tax, gross of transaction costs/slippage. Benchmark: SPY.

Finalists are selected by after-tax Sharpe and Calmar (return/risk-adjusted lens). Evolutions add MA overlays (SPY SMA200 monthly/daily, stock SMA100, combos) and fixed/staggered offsets; these are literature-grounded stress diagnostics tested after the broad map, so the effective trial count exceeds this file `[advances_fin_ml, p.273-275]`.

## Scope

- Start: `2000-01-01`
- Rows: `72`

## Key readings

- Best after-tax Sharpe: `evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_stock_sma100` — Sharpe `1.359`, CAGR `34.15%`, MDD `-45.60%`, overlay `stock_sma100`.
- Best after-tax Calmar: `evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_stock_sma100` — Calmar `0.749`, CAGR `34.15%`, MDD `-45.60%`, overlay `stock_sma100`.

## Plots

- [evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_stock_sma100_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_stock_sma100_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_staggered_stock_sma100_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_staggered_stock_sma100_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_fixed_stock_sma100_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_fixed_stock_sma100_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_staggered_stock_sma100_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_staggered_stock_sma100_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_none_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_none_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_staggered_none_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_staggered_none_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_fixed_none_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_fixed_none_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_staggered_none_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_staggered_none_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb2_off0_staggered_stock_sma100_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb2_off0_staggered_stock_sma100_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb2_off0_staggered_stock_sma100_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb2_off0_staggered_stock_sma100_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb2_off0_staggered_none_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb2_off0_staggered_none_vs_BOVA11.SA.png)
- [evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb2_off0_fixed_none_vs_BOVA11.SA.png](../plots/evolution/finalists/evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb2_off0_fixed_none_vs_BOVA11.SA.png)

## Top 25 by after-tax Sharpe

| Name | Overlay | Offsets | CAGR | MDD | Sharpe | Calmar | RollRel | GFC MDD |
|---|---|---|---|---|---|---|---|---|
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_stock_sma100 | stock_sma100 | fixed | 34.15% | -45.60% | 1.359 | 0.749 | 96.58% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_staggered_stock_sma100 | stock_sma100 | staggered | 34.15% | -45.60% | 1.359 | 0.749 | 96.58% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_fixed_stock_sma100 | stock_sma100 | fixed | 34.10% | -45.60% | 1.358 | 0.748 | 96.57% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_staggered_stock_sma100 | stock_sma100 | staggered | 34.10% | -45.60% | 1.358 | 0.748 | 96.57% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_none | none | fixed | 34.10% | -45.60% | 1.343 | 0.748 | 97.04% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_staggered_none | none | staggered | 34.10% | -45.60% | 1.343 | 0.748 | 97.04% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_fixed_none | none | fixed | 34.09% | -45.60% | 1.342 | 0.748 | 97.04% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_staggered_none | none | staggered | 34.09% | -45.60% | 1.342 | 0.748 | 97.04% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb2_off0_staggered_stock_sma100 | stock_sma100 | staggered | 31.32% | -51.97% | 1.287 | 0.603 | 96.39% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb2_off0_staggered_stock_sma100 | stock_sma100 | staggered | 31.28% | -51.97% | 1.286 | 0.602 | 96.38% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb2_off0_staggered_none | none | staggered | 31.51% | -51.97% | 1.274 | 0.606 | 96.51% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb2_off0_fixed_none | none | fixed | 33.57% | -56.30% | 1.273 | 0.596 | 97.03% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb2_off0_fixed_none | none | fixed | 33.56% | -56.30% | 1.273 | 0.596 | 97.02% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb2_off0_staggered_none | none | staggered | 31.45% | -51.97% | 1.272 | 0.605 | 96.50% | n/a |
| evo_momv2_br_stocks_composite_mom_lowvol_lb1_3_6_12_top10_reb2_off0_fixed_stock_sma100 | stock_sma100 | fixed | 25.05% | -44.61% | 1.265 | 0.561 | 96.94% | n/a |
| evo_momv2_br_stocks_composite_mom_lowvol_abs_cash_lb1_3_6_12_top10_reb2_off0_fixed_stock_sma100 | stock_sma100 | fixed | 25.05% | -44.61% | 1.265 | 0.561 | 96.94% | n/a |
| evo_momv2_br_stocks_composite_mom_lowvol_lb1_3_6_12_top10_reb2_off0_fixed_none | none | fixed | 25.13% | -44.61% | 1.264 | 0.563 | 97.03% | n/a |
| evo_momv2_br_stocks_composite_mom_lowvol_abs_cash_lb1_3_6_12_top10_reb2_off0_fixed_none | none | fixed | 25.13% | -44.61% | 1.264 | 0.563 | 97.03% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb2_off0_fixed_stock_sma100 | stock_sma100 | fixed | 32.13% | -56.30% | 1.246 | 0.571 | 96.82% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb2_off0_fixed_stock_sma100 | stock_sma100 | fixed | 32.13% | -56.30% | 1.246 | 0.571 | 96.82% | n/a |
| evo_momv2_br_stocks_composite_mom_lowvol_lb1_3_6_12_top10_reb2_off0_staggered_none | none | staggered | 23.66% | -44.02% | 1.218 | 0.537 | 95.81% | n/a |
| evo_momv2_br_stocks_composite_mom_lowvol_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_none | none | staggered | 23.66% | -44.02% | 1.218 | 0.537 | 95.81% | n/a |
| evo_momv2_br_stocks_composite_mom_lowvol_lb1_3_6_12_top10_reb2_off0_staggered_stock_sma100 | stock_sma100 | staggered | 23.39% | -44.02% | 1.214 | 0.531 | 95.70% | n/a |
| evo_momv2_br_stocks_composite_mom_lowvol_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_stock_sma100 | stock_sma100 | staggered | 23.39% | -44.02% | 1.214 | 0.531 | 95.70% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_market_sma200_monthly | market_sma200_monthly | fixed | 22.69% | -32.23% | 1.171 | 0.704 | 94.62% | n/a |

## Top 25 by after-tax Calmar

| Name | Overlay | Offsets | CAGR | MDD | Sharpe | Calmar | RollRel | GFC MDD |
|---|---|---|---|---|---|---|---|---|
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_stock_sma100 | stock_sma100 | fixed | 34.15% | -45.60% | 1.359 | 0.749 | 96.58% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_staggered_stock_sma100 | stock_sma100 | staggered | 34.15% | -45.60% | 1.359 | 0.749 | 96.58% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_none | none | fixed | 34.10% | -45.60% | 1.343 | 0.748 | 97.04% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_staggered_none | none | staggered | 34.10% | -45.60% | 1.343 | 0.748 | 97.04% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_fixed_stock_sma100 | stock_sma100 | fixed | 34.10% | -45.60% | 1.358 | 0.748 | 96.57% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_staggered_stock_sma100 | stock_sma100 | staggered | 34.10% | -45.60% | 1.358 | 0.748 | 96.57% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_fixed_none | none | fixed | 34.09% | -45.60% | 1.342 | 0.748 | 97.04% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_staggered_none | none | staggered | 34.09% | -45.60% | 1.342 | 0.748 | 97.04% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 20.34% | -28.87% | 1.078 | 0.705 | 94.28% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 20.34% | -28.87% | 1.078 | 0.705 | 94.28% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_fixed_market_sma200_daily | market_sma200_daily | fixed | 20.34% | -28.87% | 1.078 | 0.705 | 94.28% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 20.34% | -28.87% | 1.078 | 0.705 | 94.28% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_market_sma200_monthly | market_sma200_monthly | fixed | 22.69% | -32.23% | 1.171 | 0.704 | 94.62% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 22.69% | -32.23% | 1.171 | 0.704 | 94.62% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_fixed_market_sma200_monthly | market_sma200_monthly | fixed | 22.69% | -32.23% | 1.171 | 0.704 | 94.62% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_staggered_market_sma200_monthly | market_sma200_monthly | staggered | 22.69% | -32.23% | 1.171 | 0.704 | 94.62% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | fixed | 20.28% | -29.50% | 1.074 | 0.687 | 94.14% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_staggered_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | staggered | 20.28% | -29.50% | 1.074 | 0.687 | 94.14% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_fixed_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | fixed | 20.28% | -29.50% | 1.074 | 0.687 | 94.14% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_staggered_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | staggered | 20.28% | -29.50% | 1.074 | 0.687 | 94.14% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb2_off0_fixed_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | fixed | 19.89% | -30.26% | 1.068 | 0.657 | 94.58% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb2_off0_fixed_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | fixed | 19.89% | -30.26% | 1.068 | 0.657 | 94.58% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_fixed_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | fixed | 21.90% | -35.37% | 1.141 | 0.619 | 94.12% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_staggered_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | staggered | 21.90% | -35.37% | 1.141 | 0.619 | 94.12% | n/a |
| evo_momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_fixed_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | fixed | 21.90% | -35.37% | 1.141 | 0.619 | 94.12% | n/a |

## PBO summary

| group | pbo | n_configs | n_configs_total | sampled | pass |
|---|---|---|---|---|---|
| all | 0.43253968253968256 | 72 | 72 | False | True |
| mechanism:composite_mom_lowvol | 0.23809523809523808 | 12 | 12 | False | True |
| mechanism:composite_mom_lowvol_abs_cash | 0.23809523809523808 | 12 | 12 | False | True |
| mechanism:vol_adjusted_13612 | 0.3055555555555556 | 24 | 24 | False | True |
| mechanism:vol_adjusted_13612_abs_cash | 0.30952380952380953 | 24 | 24 | False | True |
