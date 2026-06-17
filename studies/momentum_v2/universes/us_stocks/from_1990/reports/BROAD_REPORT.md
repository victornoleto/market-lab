# Broad Momentum Screen — `us_stocks`

Status: **research-only**, `promotion_eligible=false`. The Postgres universe plus survivorship filters *mitigate* but do not *eliminate* bias — the yfinance feed never captured most fully delisted names, so historical screens stay inflated `[advances_fin_ml, p.208-211]`. Main rankings are after Brazil's annual 15% realized-gain tax, gross of transaction costs/slippage. Benchmark: SPY.

The broad phase is a **diagnostic map**, not a promotion claim. Honest gates run only on the small validate-phase finalist set.

## Scope

- Start: `1990-01-01`
- Configs: `1260`
- Sampled PBO (all): `0.020` over `1000`/`1260` configs.

## Key readings

- Best rolling dominance: `momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0` — score `95.44%`, CAGR `58.61%`, MDD `-63.19%`.
- Best after-tax Sharpe: `momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0` — CAGR `46.42%`, Sharpe `1.214`, MDD `-58.29%`.
- Best after-tax Calmar: `momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0` — Calmar `0.928`, CAGR `58.61%`, MDD `-63.19%`.

## Plots

- [all_configs_cagr_vs_mdd.png](../plots/broad/all_configs_cagr_vs_mdd.png)
- [heatmap_sharpe.png](../plots/broad/heatmap_sharpe.png)
- [heatmap_mdd.png](../plots/broad/heatmap_mdd.png)
- [heatmap_rolling_rel.png](../plots/broad/heatmap_rolling_rel.png)
- [momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_vs_SPY.png)
- [momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_lb6_top15_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_lb6_top15_reb1_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb1_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_vs_SPY.png)
- [momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0_vs_SPY.png)
- [momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0_vs_SPY.png)
- [momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0_vs_SPY.png)
- [momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb1_off0_vs_SPY.png)
- [momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top15_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top15_reb1_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0_vs_SPY.png)

## Top 20 by rolling dominance

| Name | Mechanism | LB | Top-N | Reb | CAGR | MDD | Sharpe | RollRel | GFC MDD | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0 | clenow_trend | lb1_3_6_12 | 10 | 2 | 58.61% | -63.19% | 1.050 | 95.44% | -63.19% | 4.181 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 10 | 2 | 58.61% | -63.19% | 1.050 | 95.44% | -63.19% | 4.181 |
| momv2_us_stocks_raw_13612_lb6_top15_reb1_off0 | raw_13612 | lb6 | 15 | 1 | 49.52% | -60.79% | 1.078 | 95.32% | -58.83% | 5.344 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb1_off0 | raw_13612_abs_cash | lb6 | 15 | 1 | 49.52% | -60.79% | 1.078 | 95.32% | -58.83% | 5.344 |
| momv2_us_stocks_raw_13612_lb6_top15_reb2_off0 | raw_13612 | lb6 | 15 | 2 | 48.31% | -65.77% | 1.062 | 95.10% | -65.77% | 3.623 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0 | raw_13612_abs_cash | lb6 | 15 | 2 | 48.31% | -65.77% | 1.062 | 95.10% | -65.77% | 3.623 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0 | clenow_trend | lb1_3_6_12 | 15 | 1 | 46.42% | -58.29% | 1.214 | 95.09% | -58.00% | 4.901 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 15 | 1 | 46.42% | -58.29% | 1.214 | 95.09% | -58.00% | 4.901 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0 | clenow_trend | lb1_3_6_12 | 10 | 1 | 51.13% | -63.00% | 1.201 | 95.03% | -58.94% | 5.097 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb1_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 10 | 1 | 51.13% | -63.00% | 1.201 | 95.03% | -58.94% | 5.097 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top15_reb1_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 15 | 1 | 42.15% | -57.47% | 1.167 | 94.75% | -55.76% | 5.643 |
| momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0 | raw_13612_inverse_vol | lb6 | 15 | 3 | 43.41% | -60.37% | 1.151 | 94.70% | -60.37% | 3.103 |
| momv2_us_stocks_raw_13612_lb6_top10_reb1_off0 | raw_13612 | lb6 | 10 | 1 | 53.73% | -65.79% | 0.977 | 94.67% | -65.79% | 5.355 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top10_reb1_off0 | raw_13612_abs_cash | lb6 | 10 | 1 | 53.73% | -65.79% | 0.977 | 94.67% | -65.79% | 5.355 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top10_reb2_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 10 | 2 | 49.39% | -67.01% | 1.208 | 94.64% | -67.01% | 4.510 |
| momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb2_off0 | raw_13612_inverse_vol | lb6 | 15 | 2 | 41.38% | -68.70% | 1.116 | 94.44% | -68.70% | 3.982 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top10_reb1_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 10 | 1 | 44.59% | -63.88% | 1.129 | 94.32% | -59.01% | 5.861 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb3_off0 | clenow_trend | lb1_3_6_12 | 10 | 3 | 49.91% | -62.40% | 0.948 | 94.31% | -58.04% | 3.367 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb3_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 10 | 3 | 49.91% | -62.40% | 0.948 | 94.31% | -58.04% | 3.367 |
| momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb1_off0 | raw_13612_inverse_vol | lb6 | 15 | 1 | 40.45% | -62.14% | 1.099 | 94.28% | -61.03% | 6.123 |

## Top 20 by after-tax Sharpe

| Name | Mechanism | LB | Top-N | Reb | CAGR | MDD | Sharpe | RollRel | GFC MDD | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0 | clenow_trend | lb1_3_6_12 | 15 | 1 | 46.42% | -58.29% | 1.214 | 95.09% | -58.00% | 4.901 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 15 | 1 | 46.42% | -58.29% | 1.214 | 95.09% | -58.00% | 4.901 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top10_reb2_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 10 | 2 | 49.39% | -67.01% | 1.208 | 94.64% | -67.01% | 4.510 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0 | clenow_trend | lb1_3_6_12 | 10 | 1 | 51.13% | -63.00% | 1.201 | 95.03% | -58.94% | 5.097 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb1_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 10 | 1 | 51.13% | -63.00% | 1.201 | 95.03% | -58.94% | 5.097 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top15_reb1_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 15 | 1 | 42.15% | -57.47% | 1.167 | 94.75% | -55.76% | 5.643 |
| momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0 | raw_13612_inverse_vol | lb6 | 15 | 3 | 43.41% | -60.37% | 1.151 | 94.70% | -60.37% | 3.103 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top10_reb1_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 10 | 1 | 44.59% | -63.88% | 1.129 | 94.32% | -59.01% | 5.861 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top5_reb1_off0 | clenow_trend | lb1_3_6_12 | 5 | 1 | 59.08% | -67.79% | 1.124 | 93.22% | -54.35% | 5.298 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top5_reb1_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 5 | 1 | 59.08% | -67.79% | 1.124 | 93.22% | -54.35% | 5.298 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top15_reb2_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 15 | 2 | 39.85% | -66.44% | 1.124 | 91.88% | -66.44% | 4.398 |
| momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb2_off0 | raw_13612_inverse_vol | lb6 | 15 | 2 | 41.38% | -68.70% | 1.116 | 94.44% | -68.70% | 3.982 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top10_reb3_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 10 | 3 | 44.71% | -61.66% | 1.112 | 94.01% | -58.14% | 3.502 |
| momv2_us_stocks_raw_13612_lb6_top15_reb3_off0 | raw_13612 | lb6 | 15 | 3 | 51.60% | -61.16% | 1.110 | 93.88% | -61.16% | 2.893 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb3_off0 | raw_13612_abs_cash | lb6 | 15 | 3 | 51.60% | -61.16% | 1.110 | 93.88% | -61.16% | 2.893 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top15_reb3_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 15 | 3 | 40.08% | -65.22% | 1.108 | 92.80% | -65.22% | 3.479 |
| momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb1_off0 | raw_13612_inverse_vol | lb6 | 15 | 1 | 40.45% | -62.14% | 1.099 | 94.28% | -61.03% | 6.123 |
| momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top15_reb3_off0 | raw_13612_inverse_vol | lb1_3_6_12 | 15 | 3 | 42.33% | -71.24% | 1.094 | 91.44% | -71.24% | 2.699 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb2_off0 | clenow_trend | lb1_3_6_12 | 15 | 2 | 48.02% | -65.57% | 1.082 | 93.83% | -65.57% | 4.060 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb2_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 15 | 2 | 48.02% | -65.57% | 1.082 | 93.83% | -65.57% | 4.060 |

## PBO summary

| group | pbo | n_configs | n_configs_total | sampled | pass |
|---|---|---|---|---|---|
| all | 0.01984126984126984 | 1000 | 1260 | True | True |
| mechanism:clenow_trend | 0.0 | 30 | 30 | False | True |
| mechanism:clenow_trend_abs_cash | 0.0 | 30 | 30 | False | True |
| mechanism:clenow_trend_inverse_vol | 0.007936507936507936 | 30 | 30 | False | True |
| mechanism:composite_mom_lowvol | 0.5952380952380952 | 120 | 120 | False | False |
| mechanism:composite_mom_lowvol_abs_cash | 0.5952380952380952 | 120 | 120 | False | False |
| mechanism:composite_mom_lowvol_inverse_vol | 0.6547619047619048 | 120 | 120 | False | False |
| mechanism:mom_12_1 | 0.19047619047619047 | 30 | 30 | False | True |
| mechanism:mom_12_1_abs_cash | 0.19047619047619047 | 30 | 30 | False | True |
| mechanism:mom_12_1_inverse_vol | 0.25793650793650796 | 30 | 30 | False | True |
| mechanism:raw_13612 | 0.0992063492063492 | 120 | 120 | False | True |
| mechanism:raw_13612_abs_cash | 0.0992063492063492 | 120 | 120 | False | True |
| mechanism:raw_13612_inverse_vol | 0.15079365079365079 | 120 | 120 | False | True |
| mechanism:vol_adjusted_13612 | 0.23015873015873015 | 120 | 120 | False | True |
| mechanism:vol_adjusted_13612_abs_cash | 0.23015873015873015 | 120 | 120 | False | True |
| mechanism:vol_adjusted_13612_inverse_vol | 0.3531746031746032 | 120 | 120 | False | True |
