# Broad Momentum Screen — `br_stocks`

Status: **research-only**, `promotion_eligible=false`. The Postgres universe plus survivorship filters *mitigate* but do not *eliminate* bias — the yfinance feed never captured most fully delisted names, so historical screens stay inflated `[advances_fin_ml, p.208-211]`. Main rankings are after Brazil's annual 15% realized-gain tax, gross of transaction costs/slippage. Benchmark: SPY.

The broad phase is a **diagnostic map**, not a promotion claim. Honest gates run only on the small validate-phase finalist set.

## Scope

- Start: `2000-01-01`
- Configs: `840`
- Sampled PBO (all): `0.857` over `840`/`840` configs.

## Key readings

- Best rolling dominance: `momv2_br_stocks_composite_mom_lowvol_lb6_top20_reb6_off0` — score `96.83%`, CAGR `23.83%`, MDD `-47.09%`.
- Best after-tax Sharpe: `momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb1_off0` — CAGR `35.27%`, Sharpe `1.312`, MDD `-56.13%`.
- Best after-tax Calmar: `momv2_br_stocks_vol_adjusted_13612_lb6_12_top3_reb1_off0` — Calmar `0.739`, CAGR `36.52%`, MDD `-49.40%`.

## Plots

- [all_configs_cagr_vs_mdd.png](../plots/broad/all_configs_cagr_vs_mdd.png)
- [heatmap_sharpe.png](../plots/broad/heatmap_sharpe.png)
- [heatmap_mdd.png](../plots/broad/heatmap_mdd.png)
- [heatmap_rolling_rel.png](../plots/broad/heatmap_rolling_rel.png)
- [momv2_br_stocks_composite_mom_lowvol_lb6_top20_reb6_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_composite_mom_lowvol_lb6_top20_reb6_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_composite_mom_lowvol_abs_cash_lb6_top20_reb6_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_composite_mom_lowvol_abs_cash_lb6_top20_reb6_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_raw_13612_inverse_vol_lb6_top5_reb1_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_raw_13612_inverse_vol_lb6_top5_reb1_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_raw_13612_inverse_vol_lb6_12_top20_reb1_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_raw_13612_inverse_vol_lb6_12_top20_reb1_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_composite_mom_lowvol_inverse_vol_lb6_top20_reb6_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_composite_mom_lowvol_inverse_vol_lb6_top20_reb6_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_raw_13612_inverse_vol_lb3_6_12_top15_reb1_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_raw_13612_inverse_vol_lb3_6_12_top15_reb1_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_raw_13612_inverse_vol_lb6_12_top15_reb1_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_raw_13612_inverse_vol_lb6_12_top15_reb1_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_composite_mom_lowvol_lb6_top15_reb6_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_composite_mom_lowvol_lb6_top15_reb6_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_composite_mom_lowvol_abs_cash_lb6_top15_reb6_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_composite_mom_lowvol_abs_cash_lb6_top15_reb6_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_vol_adjusted_13612_lb6_top5_reb6_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_vol_adjusted_13612_lb6_top5_reb6_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_composite_mom_lowvol_lb6_12_top15_reb1_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_composite_mom_lowvol_lb6_12_top15_reb1_off0_vs_BOVA11.SA.png)
- [momv2_br_stocks_composite_mom_lowvol_abs_cash_lb6_12_top15_reb1_off0_vs_BOVA11.SA.png](../plots/broad/finalists/momv2_br_stocks_composite_mom_lowvol_abs_cash_lb6_12_top15_reb1_off0_vs_BOVA11.SA.png)

## Top 20 by rolling dominance

| Name | Mechanism | LB | Top-N | Reb | CAGR | MDD | Sharpe | RollRel | GFC MDD | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|
| momv2_br_stocks_composite_mom_lowvol_lb6_top20_reb6_off0 | composite_mom_lowvol | lb6 | 20 | 6 | 23.83% | -47.09% | 1.174 | 96.83% | n/a | 1.330 |
| momv2_br_stocks_composite_mom_lowvol_abs_cash_lb6_top20_reb6_off0 | composite_mom_lowvol_abs_cash | lb6 | 20 | 6 | 23.83% | -47.09% | 1.174 | 96.83% | n/a | 1.330 |
| momv2_br_stocks_raw_13612_inverse_vol_lb6_top5_reb1_off0 | raw_13612_inverse_vol | lb6 | 5 | 1 | 33.99% | -57.75% | 1.198 | 96.78% | n/a | 5.567 |
| momv2_br_stocks_raw_13612_inverse_vol_lb6_12_top20_reb1_off0 | raw_13612_inverse_vol | lb6_12 | 20 | 1 | 24.22% | -47.80% | 1.139 | 96.77% | n/a | 3.178 |
| momv2_br_stocks_composite_mom_lowvol_inverse_vol_lb6_top20_reb6_off0 | composite_mom_lowvol_inverse_vol | lb6 | 20 | 6 | 22.36% | -45.06% | 1.153 | 96.58% | n/a | 1.383 |
| momv2_br_stocks_raw_13612_inverse_vol_lb3_6_12_top15_reb1_off0 | raw_13612_inverse_vol | lb3_6_12 | 15 | 1 | 26.66% | -49.15% | 1.197 | 96.52% | n/a | 3.902 |
| momv2_br_stocks_raw_13612_inverse_vol_lb6_12_top15_reb1_off0 | raw_13612_inverse_vol | lb6_12 | 15 | 1 | 26.59% | -50.56% | 1.180 | 96.51% | n/a | 3.473 |
| momv2_br_stocks_composite_mom_lowvol_lb6_top15_reb6_off0 | composite_mom_lowvol | lb6 | 15 | 6 | 21.83% | -44.34% | 1.118 | 96.50% | n/a | 1.449 |
| momv2_br_stocks_composite_mom_lowvol_abs_cash_lb6_top15_reb6_off0 | composite_mom_lowvol_abs_cash | lb6 | 15 | 6 | 21.83% | -44.34% | 1.118 | 96.50% | n/a | 1.449 |
| momv2_br_stocks_vol_adjusted_13612_lb6_top5_reb6_off0 | vol_adjusted_13612 | lb6 | 5 | 6 | 29.75% | -59.56% | 1.126 | 96.46% | n/a | 1.674 |
| momv2_br_stocks_composite_mom_lowvol_lb6_12_top15_reb1_off0 | composite_mom_lowvol | lb6_12 | 15 | 1 | 23.25% | -44.64% | 1.207 | 96.43% | n/a | 3.005 |
| momv2_br_stocks_composite_mom_lowvol_abs_cash_lb6_12_top15_reb1_off0 | composite_mom_lowvol_abs_cash | lb6_12 | 15 | 1 | 23.25% | -44.64% | 1.207 | 96.43% | n/a | 3.005 |
| momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb6_off0 | vol_adjusted_13612_abs_cash | lb6 | 5 | 6 | 29.59% | -59.56% | 1.122 | 96.42% | n/a | 1.674 |
| momv2_br_stocks_clenow_trend_lb1_3_6_12_top20_reb1_off0 | clenow_trend | lb1_3_6_12 | 20 | 1 | 21.85% | -51.43% | 1.013 | 96.36% | n/a | 2.963 |
| momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb1_off0 | vol_adjusted_13612_abs_cash | lb6 | 5 | 1 | 35.27% | -56.13% | 1.312 | 96.31% | n/a | 4.889 |
| momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0 | vol_adjusted_13612_abs_cash | lb6_12 | 5 | 1 | 33.44% | -45.60% | 1.284 | 96.29% | n/a | 3.843 |
| momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0 | vol_adjusted_13612 | lb6_12 | 5 | 1 | 33.41% | -45.60% | 1.284 | 96.29% | n/a | 3.804 |
| momv2_br_stocks_composite_mom_lowvol_lb1_3_6_12_top15_reb1_off0 | composite_mom_lowvol | lb1_3_6_12 | 15 | 1 | 22.64% | -43.92% | 1.199 | 96.27% | n/a | 3.751 |
| momv2_br_stocks_composite_mom_lowvol_abs_cash_lb1_3_6_12_top15_reb1_off0 | composite_mom_lowvol_abs_cash | lb1_3_6_12 | 15 | 1 | 22.64% | -43.92% | 1.199 | 96.27% | n/a | 3.751 |
| momv2_br_stocks_raw_13612_lb6_top5_reb1_off0 | raw_13612 | lb6 | 5 | 1 | 33.40% | -59.50% | 1.136 | 96.25% | n/a | 4.766 |

## Top 20 by after-tax Sharpe

| Name | Mechanism | LB | Top-N | Reb | CAGR | MDD | Sharpe | RollRel | GFC MDD | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|
| momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb1_off0 | vol_adjusted_13612_abs_cash | lb6 | 5 | 1 | 35.27% | -56.13% | 1.312 | 96.31% | n/a | 4.889 |
| momv2_br_stocks_vol_adjusted_13612_lb6_top5_reb1_off0 | vol_adjusted_13612 | lb6 | 5 | 1 | 35.16% | -56.13% | 1.308 | 96.23% | n/a | 4.858 |
| momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top5_reb1_off0 | vol_adjusted_13612_abs_cash | lb6_12 | 5 | 1 | 33.44% | -45.60% | 1.284 | 96.29% | n/a | 3.843 |
| momv2_br_stocks_vol_adjusted_13612_lb6_12_top5_reb1_off0 | vol_adjusted_13612 | lb6_12 | 5 | 1 | 33.41% | -45.60% | 1.284 | 96.29% | n/a | 3.804 |
| momv2_br_stocks_composite_mom_lowvol_inverse_vol_lb3_6_12_top5_reb1_off0 | composite_mom_lowvol_inverse_vol | lb3_6_12 | 5 | 1 | 25.80% | -37.03% | 1.280 | 94.37% | n/a | 4.842 |
| momv2_br_stocks_composite_mom_lowvol_lb3_6_12_top5_reb1_off0 | composite_mom_lowvol | lb3_6_12 | 5 | 1 | 26.34% | -41.09% | 1.277 | 94.35% | n/a | 4.403 |
| momv2_br_stocks_composite_mom_lowvol_abs_cash_lb3_6_12_top5_reb1_off0 | composite_mom_lowvol_abs_cash | lb3_6_12 | 5 | 1 | 26.34% | -41.09% | 1.277 | 94.35% | n/a | 4.403 |
| momv2_br_stocks_vol_adjusted_13612_lb6_12_top3_reb1_off0 | vol_adjusted_13612 | lb6_12 | 3 | 1 | 36.52% | -49.40% | 1.264 | 95.22% | n/a | 4.211 |
| momv2_br_stocks_vol_adjusted_13612_abs_cash_lb6_12_top3_reb1_off0 | vol_adjusted_13612_abs_cash | lb6_12 | 3 | 1 | 36.50% | -49.40% | 1.263 | 95.22% | n/a | 4.211 |
| momv2_br_stocks_composite_mom_lowvol_inverse_vol_lb6_12_top5_reb1_off0 | composite_mom_lowvol_inverse_vol | lb6_12 | 5 | 1 | 25.00% | -36.74% | 1.243 | 94.46% | n/a | 4.539 |
| momv2_br_stocks_vol_adjusted_13612_abs_cash_lb1_3_6_12_top10_reb1_off0 | vol_adjusted_13612_abs_cash | lb1_3_6_12 | 10 | 1 | 27.84% | -52.57% | 1.231 | 95.71% | n/a | 4.230 |
| momv2_br_stocks_vol_adjusted_13612_lb1_3_6_12_top10_reb1_off0 | vol_adjusted_13612 | lb1_3_6_12 | 10 | 1 | 27.84% | -52.57% | 1.231 | 95.70% | n/a | 4.206 |
| momv2_br_stocks_composite_mom_lowvol_lb1_3_6_12_top10_reb1_off0 | composite_mom_lowvol | lb1_3_6_12 | 10 | 1 | 23.76% | -42.79% | 1.229 | 95.52% | n/a | 4.328 |
| momv2_br_stocks_composite_mom_lowvol_abs_cash_lb1_3_6_12_top10_reb1_off0 | composite_mom_lowvol_abs_cash | lb1_3_6_12 | 10 | 1 | 23.76% | -42.79% | 1.229 | 95.52% | n/a | 4.328 |
| momv2_br_stocks_composite_mom_lowvol_lb3_6_12_top10_reb1_off0 | composite_mom_lowvol | lb3_6_12 | 10 | 1 | 23.53% | -42.79% | 1.225 | 95.58% | n/a | 3.808 |
| momv2_br_stocks_composite_mom_lowvol_abs_cash_lb3_6_12_top10_reb1_off0 | composite_mom_lowvol_abs_cash | lb3_6_12 | 10 | 1 | 23.53% | -42.79% | 1.225 | 95.58% | n/a | 3.808 |
| momv2_br_stocks_vol_adjusted_13612_abs_cash_lb3_6_12_top5_reb1_off0 | vol_adjusted_13612_abs_cash | lb3_6_12 | 5 | 1 | 31.99% | -52.44% | 1.222 | 94.83% | n/a | 4.064 |
| momv2_br_stocks_vol_adjusted_13612_lb3_6_12_top5_reb1_off0 | vol_adjusted_13612 | lb3_6_12 | 5 | 1 | 31.95% | -52.44% | 1.221 | 94.80% | n/a | 4.032 |
| momv2_br_stocks_composite_mom_lowvol_inverse_vol_lb6_12_top10_reb6_off0 | composite_mom_lowvol_inverse_vol | lb6_12 | 10 | 6 | 24.45% | -43.46% | 1.219 | 96.04% | n/a | 1.388 |
| momv2_br_stocks_composite_mom_lowvol_inverse_vol_lb6_12_top10_reb1_off0 | composite_mom_lowvol_inverse_vol | lb6_12 | 10 | 1 | 22.36% | -39.43% | 1.209 | 94.66% | n/a | 3.959 |

## PBO summary

| group | pbo | n_configs | n_configs_total | sampled | pass |
|---|---|---|---|---|---|
| all | 0.8571428571428571 | 840 | 840 | False | False |
| mechanism:clenow_trend | 0.6507936507936508 | 20 | 20 | False | False |
| mechanism:clenow_trend_abs_cash | 0.6388888888888888 | 20 | 20 | False | False |
| mechanism:clenow_trend_inverse_vol | 0.7817460317460317 | 20 | 20 | False | False |
| mechanism:composite_mom_lowvol | 0.5436507936507936 | 80 | 80 | False | False |
| mechanism:composite_mom_lowvol_abs_cash | 0.5436507936507936 | 80 | 80 | False | False |
| mechanism:composite_mom_lowvol_inverse_vol | 0.5317460317460317 | 80 | 80 | False | False |
| mechanism:mom_12_1 | 0.3531746031746032 | 20 | 20 | False | True |
| mechanism:mom_12_1_abs_cash | 0.35714285714285715 | 20 | 20 | False | True |
| mechanism:mom_12_1_inverse_vol | 0.38492063492063494 | 20 | 20 | False | True |
| mechanism:raw_13612 | 0.5515873015873016 | 80 | 80 | False | False |
| mechanism:raw_13612_abs_cash | 0.5436507936507936 | 80 | 80 | False | False |
| mechanism:raw_13612_inverse_vol | 0.6111111111111112 | 80 | 80 | False | False |
| mechanism:vol_adjusted_13612 | 0.7023809523809523 | 80 | 80 | False | False |
| mechanism:vol_adjusted_13612_abs_cash | 0.7142857142857143 | 80 | 80 | False | False |
| mechanism:vol_adjusted_13612_inverse_vol | 0.4246031746031746 | 80 | 80 | False | True |
