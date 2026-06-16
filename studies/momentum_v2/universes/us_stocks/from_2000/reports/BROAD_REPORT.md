# Broad Momentum Screen — `us_stocks`

Status: **research-only**, `promotion_eligible=false`. The Postgres universe plus survivorship filters *mitigate* but do not *eliminate* bias — the yfinance feed never captured most fully delisted names, so historical screens stay inflated `[advances_fin_ml, p.208-211]`. Main rankings are after Brazil's annual 15% realized-gain tax, gross of transaction costs/slippage. Benchmark: SPY.

The broad phase is a **diagnostic map**, not a promotion claim. Honest gates run only on the small validate-phase finalist set.

## Scope

- Start: `2000-01-01`
- Configs: `840`
- Sampled PBO (all): `0.183` over `840`/`840` configs.

## Key readings

- Best rolling dominance: `momv2_us_stocks_raw_13612_inverse_vol_lb6_top20_reb3_off0` — score `95.76%`, CAGR `40.35%`, MDD `-56.29%`.
- Best after-tax Sharpe: `momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top20_reb3_off0` — CAGR `43.28%`, Sharpe `1.163`, MDD `-64.69%`.

## Plots

- [all_configs_cagr_vs_mdd.png](../plots/broad/all_configs_cagr_vs_mdd.png)
- [heatmap_sharpe.png](../plots/broad/heatmap_sharpe.png)
- [heatmap_mdd.png](../plots/broad/heatmap_mdd.png)
- [heatmap_rolling_rel.png](../plots/broad/heatmap_rolling_rel.png)
- [momv2_us_stocks_raw_13612_inverse_vol_lb6_top20_reb3_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_inverse_vol_lb6_top20_reb3_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_lb6_top20_reb6_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_lb6_top20_reb6_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb6_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb6_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_lb1_3_6_12_top20_reb3_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_lb1_3_6_12_top20_reb3_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_abs_cash_lb1_3_6_12_top20_reb3_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_abs_cash_lb1_3_6_12_top20_reb3_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top20_reb3_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top20_reb3_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_lb6_top20_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_lb6_top20_reb1_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb1_off0_vs_SPY.png)
- [momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb3_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb3_off0_vs_SPY.png)
- [momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb3_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb3_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_lb6_top15_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_lb6_top15_reb1_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb1_off0_vs_SPY.png)

## Top 20 by rolling dominance

| Name | Mechanism | LB | Top-N | Reb | CAGR | MDD | Sharpe | RollRel | GFC MDD | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|
| momv2_us_stocks_raw_13612_inverse_vol_lb6_top20_reb3_off0 | raw_13612_inverse_vol | lb6 | 20 | 3 | 40.35% | -56.29% | 1.124 | 95.76% | -56.29% | 3.092 |
| momv2_us_stocks_raw_13612_lb6_top20_reb6_off0 | raw_13612 | lb6 | 20 | 6 | 46.24% | -61.33% | 1.091 | 95.35% | -61.33% | 1.859 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb6_off0 | raw_13612_abs_cash | lb6 | 20 | 6 | 46.24% | -61.33% | 1.091 | 95.35% | -61.33% | 1.859 |
| momv2_us_stocks_raw_13612_lb1_3_6_12_top20_reb3_off0 | raw_13612 | lb1_3_6_12 | 20 | 3 | 62.39% | -63.91% | 0.970 | 95.26% | -63.91% | 2.450 |
| momv2_us_stocks_raw_13612_abs_cash_lb1_3_6_12_top20_reb3_off0 | raw_13612_abs_cash | lb1_3_6_12 | 20 | 3 | 62.39% | -63.91% | 0.970 | 95.26% | -63.91% | 2.450 |
| momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top20_reb3_off0 | raw_13612_inverse_vol | lb1_3_6_12 | 20 | 3 | 43.28% | -64.69% | 1.163 | 95.07% | -64.69% | 2.711 |
| momv2_us_stocks_raw_13612_lb6_top20_reb1_off0 | raw_13612 | lb6 | 20 | 1 | 48.69% | -59.22% | 1.054 | 95.04% | -59.22% | 5.268 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb1_off0 | raw_13612_abs_cash | lb6 | 20 | 1 | 48.69% | -59.22% | 1.054 | 95.04% | -59.22% | 5.268 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb3_off0 | clenow_trend | lb1_3_6_12 | 20 | 3 | 42.21% | -59.12% | 1.040 | 94.86% | -59.12% | 3.312 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb3_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 20 | 3 | 42.21% | -59.12% | 1.040 | 94.86% | -59.12% | 3.312 |
| momv2_us_stocks_raw_13612_lb6_top15_reb1_off0 | raw_13612 | lb6 | 15 | 1 | 51.72% | -58.83% | 0.983 | 94.79% | -58.83% | 5.418 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb1_off0 | raw_13612_abs_cash | lb6 | 15 | 1 | 51.72% | -58.83% | 0.983 | 94.79% | -58.83% | 5.418 |
| momv2_us_stocks_raw_13612_lb3_6_12_top20_reb3_off0 | raw_13612 | lb3_6_12 | 20 | 3 | 58.62% | -65.18% | 0.934 | 94.78% | -65.18% | 2.383 |
| momv2_us_stocks_raw_13612_abs_cash_lb3_6_12_top20_reb3_off0 | raw_13612_abs_cash | lb3_6_12 | 20 | 3 | 58.62% | -65.18% | 0.934 | 94.78% | -65.18% | 2.383 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top20_reb3_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 20 | 3 | 35.66% | -57.76% | 1.055 | 94.74% | -57.76% | 3.465 |
| momv2_us_stocks_raw_13612_lb6_12_top20_reb1_off0 | raw_13612 | lb6_12 | 20 | 1 | 46.87% | -65.20% | 1.021 | 94.74% | -65.20% | 4.056 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_12_top20_reb1_off0 | raw_13612_abs_cash | lb6_12 | 20 | 1 | 46.87% | -65.20% | 1.021 | 94.74% | -65.20% | 4.056 |
| momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0 | raw_13612_inverse_vol | lb6 | 15 | 3 | 42.49% | -60.37% | 1.115 | 94.72% | -60.37% | 3.130 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top20_reb1_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 20 | 1 | 36.06% | -58.39% | 1.067 | 94.72% | -58.39% | 5.595 |
| momv2_us_stocks_raw_13612_lb6_12_top15_reb3_off0 | raw_13612 | lb6_12 | 15 | 3 | 54.49% | -63.37% | 1.093 | 94.71% | -63.37% | 2.251 |

## Top 20 by after-tax Sharpe

| Name | Mechanism | LB | Top-N | Reb | CAGR | MDD | Sharpe | RollRel | GFC MDD | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|
| momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top20_reb3_off0 | raw_13612_inverse_vol | lb1_3_6_12 | 20 | 3 | 43.28% | -64.69% | 1.163 | 95.07% | -64.69% | 2.711 |
| momv2_us_stocks_raw_13612_lb6_top20_reb3_off0 | raw_13612 | lb6 | 20 | 3 | 50.01% | -58.27% | 1.148 | 94.55% | -58.27% | 2.879 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb3_off0 | raw_13612_abs_cash | lb6 | 20 | 3 | 50.01% | -58.27% | 1.148 | 94.55% | -58.27% | 2.879 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0 | clenow_trend | lb1_3_6_12 | 15 | 1 | 42.93% | -58.00% | 1.133 | 94.52% | -58.00% | 4.994 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 15 | 1 | 42.93% | -58.00% | 1.133 | 94.52% | -58.00% | 4.994 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0 | clenow_trend | lb1_3_6_12 | 10 | 1 | 47.49% | -58.94% | 1.128 | 94.31% | -58.94% | 5.212 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb1_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 10 | 1 | 47.49% | -58.94% | 1.128 | 94.31% | -58.94% | 5.212 |
| momv2_us_stocks_raw_13612_inverse_vol_lb6_top20_reb3_off0 | raw_13612_inverse_vol | lb6 | 20 | 3 | 40.35% | -56.29% | 1.124 | 95.76% | -56.29% | 3.092 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb1_off0 | clenow_trend | lb1_3_6_12 | 20 | 1 | 39.87% | -59.57% | 1.119 | 94.68% | -59.57% | 4.862 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb1_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 20 | 1 | 39.87% | -59.57% | 1.119 | 94.68% | -59.57% | 4.862 |
| momv2_us_stocks_raw_13612_lb6_12_top20_reb3_off0 | raw_13612 | lb6_12 | 20 | 3 | 48.86% | -65.49% | 1.116 | 94.50% | -65.49% | 2.253 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_12_top20_reb3_off0 | raw_13612_abs_cash | lb6_12 | 20 | 3 | 48.86% | -65.49% | 1.116 | 94.50% | -65.49% | 2.253 |
| momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0 | raw_13612_inverse_vol | lb6 | 15 | 3 | 42.49% | -60.37% | 1.115 | 94.72% | -60.37% | 3.130 |
| momv2_us_stocks_raw_13612_inverse_vol_lb3_6_12_top20_reb3_off0 | raw_13612_inverse_vol | lb3_6_12 | 20 | 3 | 40.48% | -66.85% | 1.114 | 93.79% | -66.85% | 2.652 |
| momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top15_reb3_off0 | raw_13612_inverse_vol | lb1_3_6_12 | 15 | 3 | 43.41% | -71.24% | 1.106 | 91.58% | -71.24% | 2.748 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top10_reb3_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 10 | 3 | 45.47% | -58.14% | 1.103 | 94.57% | -58.14% | 3.527 |
| momv2_us_stocks_raw_13612_lb6_12_top15_reb3_off0 | raw_13612 | lb6_12 | 15 | 3 | 54.49% | -63.37% | 1.093 | 94.71% | -63.37% | 2.251 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_12_top15_reb3_off0 | raw_13612_abs_cash | lb6_12 | 15 | 3 | 54.49% | -63.37% | 1.093 | 94.71% | -63.37% | 2.251 |
| momv2_us_stocks_raw_13612_lb6_top15_reb3_off0 | raw_13612 | lb6 | 15 | 3 | 53.47% | -61.16% | 1.092 | 93.81% | -61.16% | 2.921 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb3_off0 | raw_13612_abs_cash | lb6 | 15 | 3 | 53.47% | -61.16% | 1.092 | 93.81% | -61.16% | 2.921 |

## PBO summary

| group | pbo | n_configs | n_configs_total | sampled | pass |
|---|---|---|---|---|---|
| all | 0.18253968253968253 | 840 | 840 | False | True |
| mechanism:clenow_trend | 0.07539682539682539 | 20 | 20 | False | True |
| mechanism:clenow_trend_abs_cash | 0.07539682539682539 | 20 | 20 | False | True |
| mechanism:clenow_trend_inverse_vol | 0.1984126984126984 | 20 | 20 | False | True |
| mechanism:composite_mom_lowvol | 0.7619047619047619 | 80 | 80 | False | False |
| mechanism:composite_mom_lowvol_abs_cash | 0.7619047619047619 | 80 | 80 | False | False |
| mechanism:composite_mom_lowvol_inverse_vol | 0.7579365079365079 | 80 | 80 | False | False |
| mechanism:mom_12_1 | 0.2777777777777778 | 20 | 20 | False | True |
| mechanism:mom_12_1_abs_cash | 0.2777777777777778 | 20 | 20 | False | True |
| mechanism:mom_12_1_inverse_vol | 0.24603174603174602 | 20 | 20 | False | True |
| mechanism:raw_13612 | 0.2896825396825397 | 80 | 80 | False | True |
| mechanism:raw_13612_abs_cash | 0.2896825396825397 | 80 | 80 | False | True |
| mechanism:raw_13612_inverse_vol | 0.14682539682539683 | 80 | 80 | False | True |
| mechanism:vol_adjusted_13612 | 0.3134920634920635 | 80 | 80 | False | True |
| mechanism:vol_adjusted_13612_abs_cash | 0.3134920634920635 | 80 | 80 | False | True |
| mechanism:vol_adjusted_13612_inverse_vol | 0.3055555555555556 | 80 | 80 | False | True |
