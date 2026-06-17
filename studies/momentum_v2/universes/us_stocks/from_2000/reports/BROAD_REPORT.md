# Broad Momentum Screen — `us_stocks`

Status: **research-only**, `promotion_eligible=false`. The Postgres universe plus survivorship filters *mitigate* but do not *eliminate* bias — the yfinance feed never captured most fully delisted names, so historical screens stay inflated `[advances_fin_ml, p.208-211]`. Main rankings are after Brazil's annual 15% realized-gain tax, gross of transaction costs/slippage. Benchmark: SPY.

The broad phase is a **diagnostic map**, not a promotion claim. Honest gates run only on the small validate-phase finalist set.

## Scope

- Start: `2000-01-01`
- Configs: `1260`
- Sampled PBO (all): `0.139` over `1000`/`1260` configs.

## Key readings

- Best rolling dominance: `momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0` — score `95.21%`, CAGR `59.47%`, MDD `-63.19%`.
- Best after-tax Sharpe: `momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top10_reb2_off0` — CAGR `49.36%`, Sharpe `1.192`, MDD `-67.01%`.
- Best after-tax Calmar: `momv2_us_stocks_raw_13612_lb6_top5_reb4_off0` — Calmar `1.209`, CAGR `70.71%`, MDD `-58.47%`.

## Plots

- [all_configs_cagr_vs_mdd.png](../plots/broad/all_configs_cagr_vs_mdd.png)
- [heatmap_sharpe.png](../plots/broad/heatmap_sharpe.png)
- [heatmap_mdd.png](../plots/broad/heatmap_mdd.png)
- [heatmap_rolling_rel.png](../plots/broad/heatmap_rolling_rel.png)
- [momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_vs_SPY.png)
- [momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_lb6_12_top15_reb3_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_lb6_12_top15_reb3_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_abs_cash_lb6_12_top15_reb3_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_abs_cash_lb6_12_top15_reb3_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_lb6_top15_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_lb6_top15_reb1_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb1_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb1_off0_vs_SPY.png)
- [momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top10_reb3_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top10_reb3_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_lb1_3_6_12_top15_reb3_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_lb1_3_6_12_top15_reb3_off0_vs_SPY.png)
- [momv2_us_stocks_raw_13612_abs_cash_lb1_3_6_12_top15_reb3_off0_vs_SPY.png](../plots/broad/finalists/momv2_us_stocks_raw_13612_abs_cash_lb1_3_6_12_top15_reb3_off0_vs_SPY.png)

## Top 20 by rolling dominance

| Name | Mechanism | LB | Top-N | Reb | CAGR | MDD | Sharpe | RollRel | GFC MDD | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0 | clenow_trend | lb1_3_6_12 | 10 | 2 | 59.47% | -63.19% | 1.010 | 95.21% | -63.19% | 4.275 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 10 | 2 | 59.47% | -63.19% | 1.010 | 95.21% | -63.19% | 4.275 |
| momv2_us_stocks_raw_13612_lb6_top15_reb2_off0 | raw_13612 | lb6 | 15 | 2 | 46.34% | -65.77% | 0.994 | 94.82% | -65.77% | 3.689 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0 | raw_13612_abs_cash | lb6 | 15 | 2 | 46.34% | -65.77% | 0.994 | 94.82% | -65.77% | 3.689 |
| momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0 | raw_13612_inverse_vol | lb6 | 15 | 3 | 42.41% | -60.37% | 1.114 | 94.71% | -60.37% | 3.134 |
| momv2_us_stocks_raw_13612_lb6_12_top15_reb3_off0 | raw_13612 | lb6_12 | 15 | 3 | 54.19% | -63.37% | 1.088 | 94.69% | -63.37% | 2.256 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_12_top15_reb3_off0 | raw_13612_abs_cash | lb6_12 | 15 | 3 | 54.19% | -63.37% | 1.088 | 94.69% | -63.37% | 2.256 |
| momv2_us_stocks_raw_13612_lb6_top15_reb1_off0 | raw_13612 | lb6 | 15 | 1 | 47.23% | -58.83% | 1.005 | 94.59% | -58.83% | 5.423 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb1_off0 | raw_13612_abs_cash | lb6 | 15 | 1 | 47.23% | -58.83% | 1.005 | 94.59% | -58.83% | 5.423 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top10_reb3_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 10 | 3 | 45.47% | -58.14% | 1.103 | 94.57% | -58.14% | 3.527 |
| momv2_us_stocks_raw_13612_lb1_3_6_12_top15_reb3_off0 | raw_13612 | lb1_3_6_12 | 15 | 3 | 62.95% | -67.39% | 0.835 | 94.53% | -67.39% | 2.493 |
| momv2_us_stocks_raw_13612_abs_cash_lb1_3_6_12_top15_reb3_off0 | raw_13612_abs_cash | lb1_3_6_12 | 15 | 3 | 62.95% | -67.39% | 0.835 | 94.53% | -67.39% | 2.493 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0 | clenow_trend | lb1_3_6_12 | 15 | 1 | 42.93% | -58.00% | 1.133 | 94.52% | -58.00% | 4.994 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 15 | 1 | 42.93% | -58.00% | 1.133 | 94.52% | -58.00% | 4.994 |
| momv2_us_stocks_raw_13612_lb6_12_top15_reb4_off0 | raw_13612 | lb6_12 | 15 | 4 | 50.42% | -63.94% | 1.041 | 94.46% | -63.94% | 1.999 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_12_top15_reb4_off0 | raw_13612_abs_cash | lb6_12 | 15 | 4 | 50.42% | -63.94% | 1.041 | 94.46% | -63.94% | 1.999 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top15_reb1_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 15 | 1 | 38.87% | -55.76% | 1.084 | 94.44% | -55.76% | 5.744 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top10_reb2_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 10 | 2 | 49.36% | -67.01% | 1.192 | 94.43% | -67.01% | 4.598 |
| momv2_us_stocks_raw_13612_lb3_6_12_top15_reb3_off0 | raw_13612 | lb3_6_12 | 15 | 3 | 61.95% | -66.27% | 0.827 | 94.42% | -66.27% | 2.445 |
| momv2_us_stocks_raw_13612_abs_cash_lb3_6_12_top15_reb3_off0 | raw_13612_abs_cash | lb3_6_12 | 15 | 3 | 61.95% | -66.27% | 0.827 | 94.42% | -66.27% | 2.445 |

## Top 20 by after-tax Sharpe

| Name | Mechanism | LB | Top-N | Reb | CAGR | MDD | Sharpe | RollRel | GFC MDD | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top10_reb2_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 10 | 2 | 49.36% | -67.01% | 1.192 | 94.43% | -67.01% | 4.598 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb1_off0 | clenow_trend | lb1_3_6_12 | 15 | 1 | 42.93% | -58.00% | 1.133 | 94.52% | -58.00% | 4.994 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 15 | 1 | 42.93% | -58.00% | 1.133 | 94.52% | -58.00% | 4.994 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0 | clenow_trend | lb1_3_6_12 | 10 | 1 | 47.49% | -58.94% | 1.128 | 94.31% | -58.94% | 5.212 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb1_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 10 | 1 | 47.49% | -58.94% | 1.128 | 94.31% | -58.94% | 5.212 |
| momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top15_reb3_off0 | raw_13612_inverse_vol | lb1_3_6_12 | 15 | 3 | 44.11% | -71.24% | 1.116 | 91.58% | -71.24% | 2.752 |
| momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb3_off0 | raw_13612_inverse_vol | lb6 | 15 | 3 | 42.41% | -60.37% | 1.114 | 94.71% | -60.37% | 3.134 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top10_reb3_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 10 | 3 | 45.47% | -58.14% | 1.103 | 94.57% | -58.14% | 3.527 |
| momv2_us_stocks_raw_13612_inverse_vol_lb3_6_12_top15_reb3_off0 | raw_13612_inverse_vol | lb3_6_12 | 15 | 3 | 42.87% | -68.46% | 1.099 | 93.98% | -68.46% | 2.703 |
| momv2_us_stocks_raw_13612_lb6_12_top15_reb3_off0 | raw_13612 | lb6_12 | 15 | 3 | 54.19% | -63.37% | 1.088 | 94.69% | -63.37% | 2.256 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_12_top15_reb3_off0 | raw_13612_abs_cash | lb6_12 | 15 | 3 | 54.19% | -63.37% | 1.088 | 94.69% | -63.37% | 2.256 |
| momv2_us_stocks_raw_13612_lb6_top15_reb3_off0 | raw_13612 | lb6 | 15 | 3 | 53.15% | -61.16% | 1.087 | 93.78% | -61.16% | 2.923 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb3_off0 | raw_13612_abs_cash | lb6 | 15 | 3 | 53.15% | -61.16% | 1.087 | 93.78% | -61.16% | 2.923 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top15_reb1_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 15 | 1 | 38.87% | -55.76% | 1.084 | 94.44% | -55.76% | 5.744 |
| momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top15_reb4_off0 | raw_13612_inverse_vol | lb1_3_6_12 | 15 | 4 | 40.72% | -66.22% | 1.080 | 91.74% | -66.22% | 2.295 |
| momv2_us_stocks_raw_13612_inverse_vol_lb6_12_top15_reb3_off0 | raw_13612_inverse_vol | lb6_12 | 15 | 3 | 40.44% | -65.47% | 1.072 | 94.03% | -65.47% | 2.526 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top15_reb2_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 15 | 2 | 37.97% | -66.44% | 1.069 | 91.03% | -66.44% | 4.469 |
| momv2_us_stocks_raw_13612_lb1_3_6_12_top15_reb4_off0 | raw_13612 | lb1_3_6_12 | 15 | 4 | 52.19% | -60.78% | 1.061 | 93.67% | -60.67% | 2.119 |
| momv2_us_stocks_raw_13612_abs_cash_lb1_3_6_12_top15_reb4_off0 | raw_13612_abs_cash | lb1_3_6_12 | 15 | 4 | 52.19% | -60.78% | 1.061 | 93.67% | -60.67% | 2.119 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top5_reb1_off0 | clenow_trend | lb1_3_6_12 | 5 | 1 | 54.50% | -63.08% | 1.060 | 91.72% | -54.35% | 5.382 |

## PBO summary

| group | pbo | n_configs | n_configs_total | sampled | pass |
|---|---|---|---|---|---|
| all | 0.1388888888888889 | 1000 | 1260 | True | True |
| mechanism:clenow_trend | 0.023809523809523808 | 30 | 30 | False | True |
| mechanism:clenow_trend_abs_cash | 0.023809523809523808 | 30 | 30 | False | True |
| mechanism:clenow_trend_inverse_vol | 0.05555555555555555 | 30 | 30 | False | True |
| mechanism:composite_mom_lowvol | 0.7936507936507936 | 120 | 120 | False | False |
| mechanism:composite_mom_lowvol_abs_cash | 0.7936507936507936 | 120 | 120 | False | False |
| mechanism:composite_mom_lowvol_inverse_vol | 0.8095238095238095 | 120 | 120 | False | False |
| mechanism:mom_12_1 | 0.18253968253968253 | 30 | 30 | False | True |
| mechanism:mom_12_1_abs_cash | 0.18253968253968253 | 30 | 30 | False | True |
| mechanism:mom_12_1_inverse_vol | 0.27380952380952384 | 30 | 30 | False | True |
| mechanism:raw_13612 | 0.12698412698412698 | 120 | 120 | False | True |
| mechanism:raw_13612_abs_cash | 0.12698412698412698 | 120 | 120 | False | True |
| mechanism:raw_13612_inverse_vol | 0.23412698412698413 | 120 | 120 | False | True |
| mechanism:vol_adjusted_13612 | 0.48412698412698413 | 120 | 120 | False | True |
| mechanism:vol_adjusted_13612_abs_cash | 0.48412698412698413 | 120 | 120 | False | True |
| mechanism:vol_adjusted_13612_inverse_vol | 0.4523809523809524 | 120 | 120 | False | True |
