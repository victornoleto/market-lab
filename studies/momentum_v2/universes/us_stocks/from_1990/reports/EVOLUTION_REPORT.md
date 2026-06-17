# Finalist Evolution — `us_stocks`

Status: **research-only**, `promotion_eligible=false`. The Postgres universe plus survivorship filters *mitigate* but do not *eliminate* bias — the yfinance feed never captured most fully delisted names, so historical screens stay inflated `[advances_fin_ml, p.208-211]`. Main rankings are after Brazil's annual 15% realized-gain tax, gross of transaction costs/slippage. Benchmark: SPY.

Finalists are selected by after-tax Sharpe and Calmar (return/risk-adjusted lens). Evolutions add MA overlays (SPY SMA200 monthly/daily, stock SMA100, combos) and fixed/staggered offsets; these are literature-grounded stress diagnostics tested after the broad map, so the effective trial count exceeds this file `[advances_fin_ml, p.273-275]`.

## Scope

- Start: `1990-01-01`
- Rows: `72`

## Key readings

- Best after-tax Sharpe: `evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_staggered_stock_sma100` — Sharpe `1.193`, CAGR `44.25%`, MDD `-66.77%`, overlay `stock_sma100`.
- Best after-tax Calmar: `evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_fixed_none` — Calmar `0.928`, CAGR `58.61%`, MDD `-63.19%`, overlay `none`.

## Plots

- [evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_staggered_stock_sma100_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_staggered_stock_sma100_vs_SPY.png)
- [evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_staggered_stock_sma100_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_staggered_stock_sma100_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_none_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_none_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_fixed_stock_sma100_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_fixed_stock_sma100_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_fixed_stock_sma100_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_fixed_stock_sma100_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_stock_sma100_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_stock_sma100_vs_SPY.png)
- [evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_stock_sma100_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_stock_sma100_vs_SPY.png)
- [evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_staggered_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_staggered_none_vs_SPY.png)
- [evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_staggered_none_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_staggered_none_vs_SPY.png)
- [evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_fixed_stock_sma100_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_fixed_stock_sma100_vs_SPY.png)
- [evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_fixed_stock_sma100_vs_SPY.png](../plots/evolution/finalists/evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_fixed_stock_sma100_vs_SPY.png)

## Top 25 by after-tax Sharpe

| Name | Overlay | Offsets | CAGR | MDD | Sharpe | Calmar | RollRel | GFC MDD |
|---|---|---|---|---|---|---|---|---|
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_staggered_stock_sma100 | stock_sma100 | staggered | 44.25% | -66.77% | 1.193 | 0.663 | 95.13% | -66.77% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_staggered_stock_sma100 | stock_sma100 | staggered | 44.25% | -66.77% | 1.193 | 0.663 | 95.13% | -66.77% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_none | none | staggered | 52.72% | -61.97% | 1.177 | 0.851 | 95.51% | -61.10% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_none | none | staggered | 52.72% | -61.97% | 1.177 | 0.851 | 95.51% | -61.10% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_fixed_stock_sma100 | stock_sma100 | fixed | 46.99% | -66.86% | 1.168 | 0.703 | 94.30% | -66.86% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_fixed_stock_sma100 | stock_sma100 | fixed | 46.99% | -66.86% | 1.168 | 0.703 | 94.30% | -66.86% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_stock_sma100 | stock_sma100 | staggered | 44.79% | -64.35% | 1.161 | 0.696 | 94.59% | -64.35% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_stock_sma100 | stock_sma100 | staggered | 44.79% | -64.35% | 1.161 | 0.696 | 94.59% | -64.35% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_staggered_none | none | staggered | 51.87% | -66.03% | 1.135 | 0.786 | 95.68% | -66.03% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_staggered_none | none | staggered | 51.87% | -66.03% | 1.135 | 0.786 | 95.68% | -66.03% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_fixed_stock_sma100 | stock_sma100 | fixed | 42.28% | -62.45% | 1.122 | 0.677 | 95.02% | -62.45% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_fixed_stock_sma100 | stock_sma100 | fixed | 42.28% | -62.45% | 1.122 | 0.677 | 95.02% | -62.45% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb1_off0_fixed_stock_sma100 | stock_sma100 | fixed | 42.33% | -60.13% | 1.119 | 0.704 | 94.69% | -59.06% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb1_off0_staggered_stock_sma100 | stock_sma100 | staggered | 42.33% | -60.13% | 1.119 | 0.704 | 94.69% | -59.06% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb1_off0_fixed_stock_sma100 | stock_sma100 | fixed | 42.33% | -60.13% | 1.119 | 0.704 | 94.69% | -59.06% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb1_off0_staggered_stock_sma100 | stock_sma100 | staggered | 42.33% | -60.13% | 1.119 | 0.704 | 94.69% | -59.06% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb1_off0_fixed_none | none | fixed | 49.52% | -60.79% | 1.078 | 0.815 | 95.32% | -58.83% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb1_off0_staggered_none | none | staggered | 49.52% | -60.79% | 1.078 | 0.815 | 95.32% | -58.83% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb1_off0_fixed_none | none | fixed | 49.52% | -60.79% | 1.078 | 0.815 | 95.32% | -58.83% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb1_off0_staggered_none | none | staggered | 49.52% | -60.79% | 1.078 | 0.815 | 95.32% | -58.83% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_staggered_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | staggered | 32.77% | -59.78% | 1.076 | 0.548 | 93.68% | -20.53% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_staggered_market_sma200_daily_stock_sma100 | market_sma200_daily_stock_sma100 | staggered | 32.77% | -59.78% | 1.076 | 0.548 | 93.68% | -20.53% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_staggered_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | staggered | 33.37% | -59.52% | 1.074 | 0.561 | 92.98% | -18.06% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_staggered_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | staggered | 33.37% | -59.52% | 1.074 | 0.561 | 92.98% | -18.06% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_market_sma200_monthly_stock_sma100 | market_sma200_monthly_stock_sma100 | staggered | 34.53% | -62.65% | 1.063 | 0.551 | 91.69% | -23.57% |

## Top 25 by after-tax Calmar

| Name | Overlay | Offsets | CAGR | MDD | Sharpe | Calmar | RollRel | GFC MDD |
|---|---|---|---|---|---|---|---|---|
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_fixed_none | none | fixed | 58.61% | -63.19% | 1.050 | 0.928 | 95.44% | -63.19% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_fixed_none | none | fixed | 58.61% | -63.19% | 1.050 | 0.928 | 95.44% | -63.19% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_none | none | staggered | 52.72% | -61.97% | 1.177 | 0.851 | 95.51% | -61.10% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_none | none | staggered | 52.72% | -61.97% | 1.177 | 0.851 | 95.51% | -61.10% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb1_off0_fixed_none | none | fixed | 49.52% | -60.79% | 1.078 | 0.815 | 95.32% | -58.83% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb1_off0_staggered_none | none | staggered | 49.52% | -60.79% | 1.078 | 0.815 | 95.32% | -58.83% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb1_off0_fixed_none | none | fixed | 49.52% | -60.79% | 1.078 | 0.815 | 95.32% | -58.83% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb1_off0_staggered_none | none | staggered | 49.52% | -60.79% | 1.078 | 0.815 | 95.32% | -58.83% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_staggered_none | none | staggered | 51.87% | -66.03% | 1.135 | 0.786 | 95.68% | -66.03% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_staggered_none | none | staggered | 51.87% | -66.03% | 1.135 | 0.786 | 95.68% | -66.03% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_fixed_none | none | fixed | 48.31% | -65.77% | 1.062 | 0.735 | 95.10% | -65.77% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_fixed_none | none | fixed | 48.31% | -65.77% | 1.062 | 0.735 | 95.10% | -65.77% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb1_off0_fixed_stock_sma100 | stock_sma100 | fixed | 42.33% | -60.13% | 1.119 | 0.704 | 94.69% | -59.06% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb1_off0_staggered_stock_sma100 | stock_sma100 | staggered | 42.33% | -60.13% | 1.119 | 0.704 | 94.69% | -59.06% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb1_off0_fixed_stock_sma100 | stock_sma100 | fixed | 42.33% | -60.13% | 1.119 | 0.704 | 94.69% | -59.06% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb1_off0_staggered_stock_sma100 | stock_sma100 | staggered | 42.33% | -60.13% | 1.119 | 0.704 | 94.69% | -59.06% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_fixed_market_sma200_monthly | market_sma200_monthly | fixed | 42.73% | -60.79% | 0.874 | 0.703 | 93.27% | -34.87% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_fixed_market_sma200_monthly | market_sma200_monthly | fixed | 42.73% | -60.79% | 0.874 | 0.703 | 93.27% | -34.87% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_fixed_stock_sma100 | stock_sma100 | fixed | 46.99% | -66.86% | 1.168 | 0.703 | 94.30% | -66.86% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_fixed_stock_sma100 | stock_sma100 | fixed | 46.99% | -66.86% | 1.168 | 0.703 | 94.30% | -66.86% |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_stock_sma100 | stock_sma100 | staggered | 44.79% | -64.35% | 1.161 | 0.696 | 94.59% | -64.35% |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_stock_sma100 | stock_sma100 | staggered | 44.79% | -64.35% | 1.161 | 0.696 | 94.59% | -64.35% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_fixed_stock_sma100 | stock_sma100 | fixed | 42.28% | -62.45% | 1.122 | 0.677 | 95.02% | -62.45% |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_fixed_stock_sma100 | stock_sma100 | fixed | 42.28% | -62.45% | 1.122 | 0.677 | 95.02% | -62.45% |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_staggered_market_sma200_daily | market_sma200_daily | staggered | 40.08% | -60.22% | 1.011 | 0.666 | 94.64% | -21.97% |

## PBO summary

| group | pbo | n_configs | n_configs_total | sampled | pass |
|---|---|---|---|---|---|
| all | 0.6626984126984127 | 72 | 72 | False | False |
| mechanism:clenow_trend | 0.7023809523809523 | 12 | 12 | False | False |
| mechanism:clenow_trend_abs_cash | 0.7023809523809523 | 12 | 12 | False | False |
| mechanism:raw_13612 | 0.39285714285714285 | 24 | 24 | False | True |
| mechanism:raw_13612_abs_cash | 0.39285714285714285 | 24 | 24 | False | True |
