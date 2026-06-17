# Broad Momentum Screen — `br_stocks`

Status: **research-only**, `promotion_eligible=false`. The Postgres universe plus survivorship filters *mitigate* but do not *eliminate* bias — the yfinance feed never captured most fully delisted names, so historical screens stay inflated `[advances_fin_ml, p.208-211]`. Main rankings are after Brazil's annual 15% realized-gain tax, gross of transaction costs/slippage. Benchmark: SPY.

The broad phase is a **diagnostic map**, not a promotion claim. Honest gates run only on the small validate-phase finalist set.

## Scope

- Start: `2000-01-01`
- Configs: `1260`
- Sampled PBO (all): `0.853` over `1000`/`1260` configs.

## Key readings

- Best rolling dominance: `momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0` — score `97.04%`, CAGR `34.10%`, MDD `-45.60%`.
- Best after-tax Sharpe: `momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0` — CAGR `34.10%`, Sharpe `1.343`, MDD `-45.60%`.
- Best after-tax Calmar: `momv2_br_stocks_raw_13612_lb3_6_12_top1_reb4_off0` — Calmar `0.806`, CAGR `65.28%`, MDD `-81.01%`.

## Plots

- [all_configs_cagr_vs_mdd.png](../plots/broad/all_configs_cagr_vs_mdd.png)
- [heatmap_sharpe.png](../plots/broad/heatmap_sharpe.png)
- [heatmap_mdd.png](../plots/broad/heatmap_mdd.png)
- [heatmap_rolling_rel.png](../plots/broad/heatmap_rolling_rel.png)
- [momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_composite_mom_lowvol_lb1_3_6_12_top10_reb2_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_composite_mom_lowvol_lb1_3_6_12_top10_reb2_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_composite_mom_lowvol_abs_cash_lb1_3_6_12_top10_reb2_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_composite_mom_lowvol_abs_cash_lb1_3_6_12_top10_reb2_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb2_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb2_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb2_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb2_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_vol_adjusted_13612_lb6_top15_reb6_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_vol_adjusted_13612_lb6_top15_reb6_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_composite_mom_lowvol_inverse_vol_lb1_3_6_12_top10_reb2_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_composite_mom_lowvol_inverse_vol_lb1_3_6_12_top10_reb2_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top15_reb6_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top15_reb6_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_raw_13612_inverse_vol_lb3_6_12_top10_reb2_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_raw_13612_inverse_vol_lb3_6_12_top10_reb2_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_raw_13612_inverse_vol_lb1_3_6_12_top15_reb1_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_raw_13612_inverse_vol_lb1_3_6_12_top15_reb1_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_raw_13612_inverse_vol_lb6_12_top15_reb2_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_raw_13612_inverse_vol_lb6_12_top15_reb2_off0_vs_BOVA11.SA.png)

## Top 20 by rolling dominance

| Name | Mechanism | LB | Top-N | Reb | CAGR | MDD | Sharpe | RollRel | GFC MDD | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|
| momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0 | vol_adjusted_13612 | lb6_12 | 5 | 1 | 34.10% | -45.60% | 1.343 | 97.04% | n/a | 3.717 |
| momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0 | vol_adjusted_13612_abs_cash | lb6_12 | 5 | 1 | 34.09% | -45.60% | 1.342 | 97.04% | n/a | 3.764 |
| momv2_br_stocks_composite_mom_lowvol_lb1_3_6_12_top10_reb2_off0 | composite_mom_lowvol | lb1_3_6_12 | 10 | 2 | 25.13% | -44.61% | 1.264 | 97.03% | n/a | 2.609 |
| momv2_br_stocks_composite_mom_lowvol_abs_cash_lb1_3_6_12_top10_reb2_off0 | composite_mom_lowvol_abs_cash | lb1_3_6_12 | 10 | 2 | 25.13% | -44.61% | 1.264 | 97.03% | n/a | 2.609 |
| momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb2_off0 | vol_adjusted_13612_abs_cash | lb6_12 | 5 | 2 | 33.57% | -56.30% | 1.273 | 97.03% | n/a | 2.542 |
| momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb2_off0 | vol_adjusted_13612 | lb6_12 | 5 | 2 | 33.56% | -56.30% | 1.273 | 97.02% | n/a | 2.542 |
| momv2_br_stocks_vol_adjusted_13612_lb6_top15_reb6_off0 | vol_adjusted_13612 | lb6 | 15 | 6 | 24.08% | -51.18% | 1.089 | 96.80% | n/a | 1.442 |
| momv2_br_stocks_composite_mom_lowvol_inverse_vol_lb1_3_6_12_top10_reb2_off0 | composite_mom_lowvol_inverse_vol | lb1_3_6_12 | 10 | 2 | 23.71% | -44.09% | 1.235 | 96.68% | n/a | 2.831 |
| momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top15_reb6_off0 | vol_adjusted_13612_abs_cash | lb6 | 15 | 6 | 23.47% | -51.18% | 1.072 | 96.66% | n/a | 1.455 |
| momv2_br_stocks_raw_13612_inverse_vol_lb3_6_12_top10_reb2_off0 | raw_13612_inverse_vol | lb3_6_12 | 10 | 2 | 29.89% | -52.61% | 1.207 | 96.63% | n/a | 2.662 |
| momv2_br_stocks_raw_13612_inverse_vol_lb1_3_6_12_top15_reb1_off0 | raw_13612_inverse_vol | lb1_3_6_12 | 15 | 1 | 28.08% | -49.98% | 1.245 | 96.63% | n/a | 4.088 |
| momv2_br_stocks_raw_13612_inverse_vol_lb6_12_top15_reb2_off0 | raw_13612_inverse_vol | lb6_12 | 15 | 2 | 25.61% | -48.45% | 1.145 | 96.61% | n/a | 2.272 |
| momv2_br_stocks_vol_adjusted_13612_lb1_3_6_12_top10_reb2_off0 | vol_adjusted_13612 | lb1_3_6_12 | 10 | 2 | 27.90% | -51.15% | 1.240 | 96.59% | n/a | 2.578 |
| momv2_br_stocks_vol_adjusted_13612_abs_cash_lb1_3_6_12_top10_reb2_off0 | vol_adjusted_13612_abs_cash | lb1_3_6_12 | 10 | 2 | 27.89% | -51.15% | 1.240 | 96.58% | n/a | 2.602 |
| momv2_br_stocks_raw_13612_inverse_vol_lb6_12_top5_reb2_off0 | raw_13612_inverse_vol | lb6_12 | 5 | 2 | 30.41% | -60.56% | 1.083 | 96.55% | n/a | 2.896 |
| momv2_br_stocks_raw_13612_inverse_vol_lb1_3_6_12_top10_reb2_off0 | raw_13612_inverse_vol | lb1_3_6_12 | 10 | 2 | 28.70% | -51.26% | 1.175 | 96.54% | n/a | 2.838 |
| momv2_br_stocks_vol_adjusted_13612_lb6_top10_reb2_off0 | vol_adjusted_13612 | lb6 | 10 | 2 | 27.48% | -50.39% | 1.224 | 96.52% | n/a | 2.833 |
| momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top10_reb2_off0 | vol_adjusted_13612_abs_cash | lb6 | 10 | 2 | 27.47% | -50.39% | 1.223 | 96.52% | n/a | 2.852 |
| momv2_br_stocks_raw_13612_lb1_3_6_12_top10_reb4_off0 | raw_13612 | lb1_3_6_12 | 10 | 4 | 28.86% | -54.01% | 1.133 | 96.51% | n/a | 1.667 |
| momv2_br_stocks_raw_13612_lb6_12_top15_reb2_off0 | raw_13612 | lb6_12 | 15 | 2 | 26.42% | -50.28% | 1.127 | 96.51% | n/a | 1.917 |

## Top 20 by after-tax Sharpe

| Name | Mechanism | LB | Top-N | Reb | CAGR | MDD | Sharpe | RollRel | GFC MDD | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|
| momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0 | vol_adjusted_13612 | lb6_12 | 5 | 1 | 34.10% | -45.60% | 1.343 | 97.04% | n/a | 3.717 |
| momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0 | vol_adjusted_13612_abs_cash | lb6_12 | 5 | 1 | 34.09% | -45.60% | 1.342 | 97.04% | n/a | 3.764 |
| momv2_br_stocks_vol_adjusted_13612_lb1_3_6_12_top10_reb1_off0 | vol_adjusted_13612 | lb1_3_6_12 | 10 | 1 | 29.85% | -52.57% | 1.307 | 96.15% | n/a | 3.969 |
| momv2_br_stocks_vol_adjusted_13612_abs_cash_lb1_3_6_12_top10_reb1_off0 | vol_adjusted_13612_abs_cash | lb1_3_6_12 | 10 | 1 | 29.82% | -52.57% | 1.306 | 96.12% | n/a | 3.993 |
| momv2_br_stocks_composite_mom_lowvol_inverse_vol_lb3_6_12_top5_reb1_off0 | composite_mom_lowvol_inverse_vol | lb3_6_12 | 5 | 1 | 26.40% | -37.99% | 1.300 | 94.39% | n/a | 4.805 |
| momv2_br_stocks_composite_mom_lowvol_lb3_6_12_top5_reb1_off0 | composite_mom_lowvol | lb3_6_12 | 5 | 1 | 26.75% | -40.69% | 1.293 | 94.24% | n/a | 4.450 |
| momv2_br_stocks_composite_mom_lowvol_abs_cash_lb3_6_12_top5_reb1_off0 | composite_mom_lowvol_abs_cash | lb3_6_12 | 5 | 1 | 26.75% | -40.69% | 1.293 | 94.24% | n/a | 4.450 |
| momv2_br_stocks_vol_adjusted_13612_lb6_12_top3_reb1_off0 | vol_adjusted_13612 | lb6_12 | 3 | 1 | 37.54% | -49.40% | 1.293 | 95.32% | n/a | 4.303 |
| momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top3_reb1_off0 | vol_adjusted_13612_abs_cash | lb6_12 | 3 | 1 | 37.54% | -49.40% | 1.293 | 95.32% | n/a | 4.343 |
| momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb1_off0 | vol_adjusted_13612_abs_cash | lb6 | 5 | 1 | 34.10% | -56.13% | 1.291 | 96.06% | n/a | 4.882 |
| momv2_br_stocks_vol_adjusted_13612_lb6_top5_reb1_off0 | vol_adjusted_13612 | lb6 | 5 | 1 | 34.05% | -56.13% | 1.290 | 96.03% | n/a | 4.858 |
| momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb4_off0 | vol_adjusted_13612_abs_cash | lb6_12 | 5 | 4 | 34.67% | -56.39% | 1.280 | 96.50% | n/a | 1.762 |
| momv2_br_stocks_composite_mom_lowvol_lb1_3_6_12_top10_reb1_off0 | composite_mom_lowvol | lb1_3_6_12 | 10 | 1 | 24.95% | -42.79% | 1.277 | 95.93% | n/a | 4.194 |
| momv2_br_stocks_composite_mom_lowvol_abs_cash_lb1_3_6_12_top10_reb1_off0 | composite_mom_lowvol_abs_cash | lb1_3_6_12 | 10 | 1 | 24.95% | -42.79% | 1.277 | 95.93% | n/a | 4.194 |
| momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb4_off0 | vol_adjusted_13612 | lb6_12 | 5 | 4 | 34.57% | -56.39% | 1.276 | 96.50% | n/a | 1.754 |
| momv2_br_stocks_vol_adjusted_13612_lb3_6_12_top5_reb1_off0 | vol_adjusted_13612 | lb3_6_12 | 5 | 1 | 32.65% | -52.44% | 1.275 | 95.58% | n/a | 4.040 |
| momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb2_off0 | vol_adjusted_13612_abs_cash | lb6_12 | 5 | 2 | 33.57% | -56.30% | 1.273 | 97.03% | n/a | 2.542 |
| momv2_br_stocks_vol_adjusted_13612_abs_cash_lb3_6_12_top5_reb1_off0 | vol_adjusted_13612_abs_cash | lb3_6_12 | 5 | 1 | 32.57% | -52.44% | 1.273 | 95.53% | n/a | 4.064 |
| momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb2_off0 | vol_adjusted_13612 | lb6_12 | 5 | 2 | 33.56% | -56.30% | 1.273 | 97.02% | n/a | 2.542 |
| momv2_br_stocks_composite_mom_lowvol_inverse_vol_lb1_3_6_12_top10_reb1_off0 | composite_mom_lowvol_inverse_vol | lb1_3_6_12 | 10 | 1 | 24.06% | -42.10% | 1.271 | 95.66% | n/a | 4.565 |

## PBO summary

| group | pbo | n_configs | n_configs_total | sampled | pass |
|---|---|---|---|---|---|
| all | 0.8531746031746031 | 1000 | 1260 | True | False |
| mechanism:clenow_trend | 0.6904761904761905 | 30 | 30 | False | False |
| mechanism:clenow_trend_abs_cash | 0.6706349206349206 | 30 | 30 | False | False |
| mechanism:clenow_trend_inverse_vol | 0.7103174603174603 | 30 | 30 | False | False |
| mechanism:composite_mom_lowvol | 0.8373015873015873 | 120 | 120 | False | False |
| mechanism:composite_mom_lowvol_abs_cash | 0.8373015873015873 | 120 | 120 | False | False |
| mechanism:composite_mom_lowvol_inverse_vol | 0.6746031746031746 | 120 | 120 | False | False |
| mechanism:mom_12_1 | 0.4603174603174603 | 30 | 30 | False | True |
| mechanism:mom_12_1_abs_cash | 0.46825396825396826 | 30 | 30 | False | True |
| mechanism:mom_12_1_inverse_vol | 0.5 | 30 | 30 | False | False |
| mechanism:raw_13612 | 0.6904761904761905 | 120 | 120 | False | False |
| mechanism:raw_13612_abs_cash | 0.6904761904761905 | 120 | 120 | False | False |
| mechanism:raw_13612_inverse_vol | 0.6547619047619048 | 120 | 120 | False | False |
| mechanism:vol_adjusted_13612 | 0.7777777777777778 | 120 | 120 | False | False |
| mechanism:vol_adjusted_13612_abs_cash | 0.7777777777777778 | 120 | 120 | False | False |
| mechanism:vol_adjusted_13612_inverse_vol | 0.5714285714285714 | 120 | 120 | False | False |
