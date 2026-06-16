# Broad Momentum Screen — `us_stocks`

Status: **research-only**, `promotion_eligible=false`. The Postgres universe plus survivorship filters *mitigate* but do not *eliminate* bias — the yfinance feed never captured most fully delisted names, so historical screens stay inflated `[advances_fin_ml, p.208-211]`. Main rankings are after Brazil's annual 15% realized-gain tax, gross of transaction costs/slippage. Benchmark: SPY.

The broad phase is a **diagnostic map**, not a promotion claim. Honest gates run only on the small validate-phase finalist set.

## Scope

- Start: `1990-01-01`
- Configs: `840`
- Sampled PBO (all): `0.087` over `840`/`840` configs.

## Key readings

- Best rolling dominance: `momv2_us_stocks_raw_13612_inverse_vol_lb6_top20_reb3_off0` — score `95.49%`, CAGR `40.78%`, MDD `-56.29%`.
- Best after-tax Sharpe: `momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0` — CAGR `46.42%`, Sharpe `1.214`, MDD `-58.29%`.

## Plots

- [all_configs_cagr_vs_mdd.png](../plots/broad/all_configs_cagr_vs_mdd.png)
- [heatmap_sharpe.png](../plots/broad/heatmap_sharpe.png)
- [heatmap_mdd.png](../plots/broad/heatmap_mdd.png)
- [heatmap_rolling_rel.png](../plots/broad/heatmap_rolling_rel.png)
- [momv2_us_stocks_raw_13612_inverse_vol_lb6_top20_reb3_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_inverse_vol_lb6_top20_reb3_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_lb6_top15_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_lb6_top15_reb1_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb1_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_lb6_top20_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_lb6_top20_reb1_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb1_off0_vs_SPY.png)
- [momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb1_off0_vs_SPY.png)
- [momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb1_off0_vs_SPY.png)
- [momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_vs_SPY.png)
- [momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0_vs_SPY.png)
- [momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb3_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb3_off0_vs_SPY.png)
- [momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb3_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb3_off0_vs_SPY.png)
- [momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0_vs_SPY.png)

## Top 20 by rolling dominance

| Name | Mechanism | LB | Top-N | Reb | CAGR | MDD | Sharpe | RollRel | GFC MDD | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|
| momv2_us_stocks_raw_13612_inverse_vol_lb6_top20_reb3_off0 | raw_13612_inverse_vol | lb6 | 20 | 3 | 40.78% | -56.29% | 1.153 | 95.49% | -56.29% | 3.053 |
| momv2_us_stocks_raw_13612_lb6_top15_reb1_off0 | raw_13612 | lb6 | 15 | 1 | 53.05% | -60.79% | 1.048 | 95.47% | -58.83% | 5.340 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb1_off0 | raw_13612_abs_cash | lb6 | 15 | 1 | 53.05% | -60.79% | 1.048 | 95.47% | -58.83% | 5.340 |
| momv2_us_stocks_raw_13612_lb6_top20_reb1_off0 | raw_13612 | lb6 | 20 | 1 | 48.96% | -59.22% | 1.106 | 95.40% | -59.22% | 5.225 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb1_off0 | raw_13612_abs_cash | lb6 | 20 | 1 | 48.96% | -59.22% | 1.106 | 95.40% | -59.22% | 5.225 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb1_off0 | clenow_trend | lb1_3_6_12 | 20 | 1 | 43.03% | -59.57% | 1.201 | 95.21% | -59.57% | 4.776 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb1_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 20 | 1 | 43.03% | -59.57% | 1.201 | 95.21% | -59.57% | 4.776 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0 | clenow_trend | lb1_3_6_12 | 15 | 1 | 46.42% | -58.29% | 1.214 | 95.09% | -58.00% | 4.901 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 15 | 1 | 46.42% | -58.29% | 1.214 | 95.09% | -58.00% | 4.901 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb3_off0 | clenow_trend | lb1_3_6_12 | 20 | 3 | 44.42% | -59.12% | 1.116 | 95.07% | -59.12% | 3.277 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb3_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 20 | 3 | 44.42% | -59.12% | 1.116 | 95.07% | -59.12% | 3.277 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0 | clenow_trend | lb1_3_6_12 | 10 | 1 | 51.13% | -63.00% | 1.201 | 95.03% | -58.94% | 5.097 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb1_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 10 | 1 | 51.13% | -63.00% | 1.201 | 95.03% | -58.94% | 5.097 |
| momv2_us_stocks_raw_13612_lb6_top10_reb1_off0 | raw_13612 | lb6 | 10 | 1 | 58.32% | -65.79% | 0.931 | 94.91% | -65.79% | 5.346 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top10_reb1_off0 | raw_13612_abs_cash | lb6 | 10 | 1 | 58.32% | -65.79% | 0.931 | 94.91% | -65.79% | 5.346 |
| momv2_us_stocks_raw_13612_lb6_top20_reb3_off0 | raw_13612 | lb6 | 20 | 3 | 49.02% | -58.27% | 1.173 | 94.78% | -58.27% | 2.839 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb3_off0 | raw_13612_abs_cash | lb6 | 20 | 3 | 49.02% | -58.27% | 1.173 | 94.78% | -58.27% | 2.839 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top20_reb1_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 20 | 1 | 38.44% | -58.39% | 1.138 | 94.76% | -58.39% | 5.514 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top15_reb1_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 15 | 1 | 42.15% | -57.47% | 1.167 | 94.75% | -55.76% | 5.643 |
| momv2_us_stocks_raw_13612_lb6_top20_reb6_off0 | raw_13612 | lb6 | 20 | 6 | 45.05% | -61.33% | 1.109 | 94.74% | -61.33% | 1.852 |

## Top 20 by after-tax Sharpe

| Name | Mechanism | LB | Top-N | Reb | CAGR | MDD | Sharpe | RollRel | GFC MDD | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0 | clenow_trend | lb1_3_6_12 | 15 | 1 | 46.42% | -58.29% | 1.214 | 95.09% | -58.00% | 4.901 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 15 | 1 | 46.42% | -58.29% | 1.214 | 95.09% | -58.00% | 4.901 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb1_off0 | clenow_trend | lb1_3_6_12 | 20 | 1 | 43.03% | -59.57% | 1.201 | 95.21% | -59.57% | 4.776 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb1_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 20 | 1 | 43.03% | -59.57% | 1.201 | 95.21% | -59.57% | 4.776 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0 | clenow_trend | lb1_3_6_12 | 10 | 1 | 51.13% | -63.00% | 1.201 | 95.03% | -58.94% | 5.097 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb1_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 10 | 1 | 51.13% | -63.00% | 1.201 | 95.03% | -58.94% | 5.097 |
| momv2_us_stocks_raw_13612_lb6_top20_reb3_off0 | raw_13612 | lb6 | 20 | 3 | 49.02% | -58.27% | 1.173 | 94.78% | -58.27% | 2.839 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb3_off0 | raw_13612_abs_cash | lb6 | 20 | 3 | 49.02% | -58.27% | 1.173 | 94.78% | -58.27% | 2.839 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top15_reb1_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 15 | 1 | 42.15% | -57.47% | 1.167 | 94.75% | -55.76% | 5.643 |
| momv2_us_stocks_raw_13612_inverse_vol_lb6_top20_reb3_off0 | raw_13612_inverse_vol | lb6 | 20 | 3 | 40.78% | -56.29% | 1.153 | 95.49% | -56.29% | 3.053 |
| momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0 | raw_13612_inverse_vol | lb6 | 15 | 3 | 43.48% | -60.37% | 1.152 | 94.71% | -60.37% | 3.100 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top20_reb1_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 20 | 1 | 38.44% | -58.39% | 1.138 | 94.76% | -58.39% | 5.514 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top20_reb3_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 20 | 3 | 38.59% | -57.76% | 1.137 | 94.58% | -57.76% | 3.429 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top10_reb1_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 10 | 1 | 44.59% | -63.88% | 1.129 | 94.32% | -59.01% | 5.861 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top5_reb1_off0 | clenow_trend | lb1_3_6_12 | 5 | 1 | 59.08% | -67.79% | 1.124 | 93.22% | -54.35% | 5.298 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top5_reb1_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 5 | 1 | 59.08% | -67.79% | 1.124 | 93.22% | -54.35% | 5.298 |
| momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top20_reb3_off0 | raw_13612_inverse_vol | lb1_3_6_12 | 20 | 3 | 40.61% | -64.69% | 1.119 | 91.99% | -64.69% | 2.660 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb3_off0 | clenow_trend | lb1_3_6_12 | 20 | 3 | 44.42% | -59.12% | 1.116 | 95.07% | -59.12% | 3.277 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb3_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 20 | 3 | 44.42% | -59.12% | 1.116 | 95.07% | -59.12% | 3.277 |
| momv2_us_stocks_raw_13612_lb6_top15_reb3_off0 | raw_13612 | lb6 | 15 | 3 | 51.85% | -61.16% | 1.113 | 93.90% | -61.16% | 2.891 |

## PBO summary

| group | pbo | n_configs | n_configs_total | sampled | pass |
|---|---|---|---|---|---|
| all | 0.0873015873015873 | 840 | 840 | False | True |
| mechanism:clenow_trend | 0.003968253968253968 | 20 | 20 | False | True |
| mechanism:clenow_trend_abs_cash | 0.003968253968253968 | 20 | 20 | False | True |
| mechanism:clenow_trend_inverse_vol | 0.04365079365079365 | 20 | 20 | False | True |
| mechanism:composite_mom_lowvol | 0.6111111111111112 | 80 | 80 | False | False |
| mechanism:composite_mom_lowvol_abs_cash | 0.6111111111111112 | 80 | 80 | False | False |
| mechanism:composite_mom_lowvol_inverse_vol | 0.5714285714285714 | 80 | 80 | False | False |
| mechanism:mom_12_1 | 0.17063492063492064 | 20 | 20 | False | True |
| mechanism:mom_12_1_abs_cash | 0.17063492063492064 | 20 | 20 | False | True |
| mechanism:mom_12_1_inverse_vol | 0.24206349206349206 | 20 | 20 | False | True |
| mechanism:raw_13612 | 0.20634920634920634 | 80 | 80 | False | True |
| mechanism:raw_13612_abs_cash | 0.20634920634920634 | 80 | 80 | False | True |
| mechanism:raw_13612_inverse_vol | 0.12301587301587301 | 80 | 80 | False | True |
| mechanism:vol_adjusted_13612 | 0.13095238095238096 | 80 | 80 | False | True |
| mechanism:vol_adjusted_13612_abs_cash | 0.13095238095238096 | 80 | 80 | False | True |
| mechanism:vol_adjusted_13612_inverse_vol | 0.3373015873015873 | 80 | 80 | False | True |
