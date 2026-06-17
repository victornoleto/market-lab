# Broad Momentum Screen — `us_stocks`

Status: **research-only**, `promotion_eligible=false`. The Postgres universe plus survivorship filters *mitigate* but do not *eliminate* bias — the yfinance feed never captured most fully delisted names, so historical screens stay inflated `[advances_fin_ml, p.208-211]`. Main rankings are after Brazil's annual 15% realized-gain tax, gross of transaction costs/slippage. Benchmark: SPY.

The broad phase is a **diagnostic map**, not a promotion claim. Honest gates run only on the small validate-phase finalist set.

## Scope

- Start: `2000-01-01`
- Configs: `840`
- Sampled PBO (all): `0.734` over `840`/`840` configs.

## Key readings

- Best rolling dominance: `momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb12_off0` — score `84.91%`, CAGR `15.69%`, MDD `-57.53%`.
- Best after-tax Sharpe: `momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb6_off0` — CAGR `21.98%`, Sharpe `0.775`, MDD `-74.32%`.
- Best after-tax Calmar: `momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top3_reb6_off0` — Calmar `0.378`, CAGR `22.06%`, MDD `-58.39%`.

## Plots

_No plots._

## Top 20 by rolling dominance

| Name | Mechanism | LB | Top-N | Reb | CAGR | MDD | Sharpe | RollRel | GFC MDD | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|
| momv2_us_stocks_raw_13612_inverse_vol_lb6_top15_reb12_off0 | raw_13612_inverse_vol | lb6 | 15 | 12 | 15.69% | -57.53% | 0.693 | 84.91% | -56.16% | 0.939 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb12_off0 | clenow_trend | lb1_3_6_12 | 20 | 12 | 15.38% | -53.77% | 0.703 | 84.78% | -53.40% | 0.924 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top15_reb1_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 15 | 1 | 13.49% | -56.49% | 0.661 | 84.74% | -56.49% | 5.466 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top20_reb12_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 20 | 12 | 14.92% | -49.97% | 0.712 | 84.43% | -49.69% | 0.943 |
| momv2_us_stocks_raw_13612_lb6_top15_reb12_off0 | raw_13612 | lb6 | 15 | 12 | 16.24% | -59.65% | 0.694 | 83.51% | -58.31% | 0.916 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top15_reb1_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 15 | 1 | 13.74% | -58.70% | 0.642 | 82.92% | -58.70% | 4.917 |
| momv2_us_stocks_raw_13612_inverse_vol_lb6_top20_reb12_off0 | raw_13612_inverse_vol | lb6 | 20 | 12 | 14.29% | -55.78% | 0.670 | 82.39% | -53.46% | 0.925 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top15_reb12_off0 | clenow_trend | lb1_3_6_12 | 15 | 12 | 15.16% | -59.45% | 0.669 | 82.35% | -58.30% | 0.939 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb12_off0 | raw_13612_abs_cash | lb6 | 15 | 12 | 16.11% | -59.65% | 0.692 | 82.31% | -58.31% | 0.918 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top15_reb12_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 15 | 12 | 14.85% | -57.08% | 0.679 | 82.12% | -55.96% | 0.956 |
| momv2_us_stocks_raw_13612_lb6_top20_reb12_off0 | raw_13612 | lb6 | 20 | 12 | 14.95% | -57.80% | 0.672 | 81.73% | -56.36% | 0.903 |
| momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top3_reb6_off0 | raw_13612_inverse_vol | lb1_3_6_12 | 3 | 6 | 22.06% | -58.39% | 0.735 | 81.06% | -58.39% | 1.613 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb12_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 20 | 12 | 14.91% | -53.77% | 0.690 | 80.93% | -53.40% | 0.928 |
| momv2_us_stocks_raw_13612_lb3_6_12_top15_reb1_off0 | raw_13612 | lb3_6_12 | 15 | 1 | 15.38% | -62.08% | 0.678 | 80.58% | -62.08% | 4.471 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top20_reb1_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 20 | 1 | 12.54% | -55.32% | 0.650 | 80.49% | -55.32% | 5.233 |
| momv2_us_stocks_raw_13612_inverse_vol_lb3_6_12_top5_reb1_off0 | raw_13612_inverse_vol | lb3_6_12 | 5 | 1 | 18.53% | -62.81% | 0.697 | 80.46% | -62.81% | 5.465 |
| momv2_us_stocks_raw_13612_abs_cash_lb3_6_12_top15_reb1_off0 | raw_13612_abs_cash | lb3_6_12 | 15 | 1 | 15.25% | -63.00% | 0.676 | 79.62% | -59.96% | 4.495 |
| momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top20_reb1_off0 | clenow_trend_abs_cash | lb1_3_6_12 | 20 | 1 | 13.01% | -54.57% | 0.641 | 79.58% | -54.57% | 4.702 |
| momv2_us_stocks_raw_13612_inverse_vol_lb3_6_12_top3_reb6_off0 | raw_13612_inverse_vol | lb3_6_12 | 3 | 6 | 20.47% | -55.42% | 0.697 | 79.58% | -55.22% | 1.589 |
| momv2_us_stocks_raw_13612_lb3_6_12_top5_reb1_off0 | raw_13612 | lb3_6_12 | 5 | 1 | 18.48% | -65.20% | 0.680 | 79.18% | -65.20% | 4.829 |

## Top 20 by after-tax Sharpe

| Name | Mechanism | LB | Top-N | Reb | CAGR | MDD | Sharpe | RollRel | GFC MDD | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|
| momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb6_off0 | raw_13612_inverse_vol | lb6 | 5 | 6 | 21.98% | -74.32% | 0.775 | 75.01% | -74.32% | 1.872 |
| momv2_us_stocks_vol_adjusted_13612_lb6_top5_reb6_off0 | vol_adjusted_13612 | lb6 | 5 | 6 | 17.20% | -61.99% | 0.771 | 61.22% | -61.99% | 1.952 |
| momv2_us_stocks_vol_adjusted_13612_abs_cash_lb6_top5_reb6_off0 | vol_adjusted_13612_abs_cash | lb6 | 5 | 6 | 17.20% | -61.99% | 0.771 | 61.22% | -61.99% | 1.952 |
| momv2_us_stocks_vol_adjusted_13612_inverse_vol_lb6_top5_reb6_off0 | vol_adjusted_13612_inverse_vol | lb6 | 5 | 6 | 15.27% | -59.80% | 0.746 | 55.18% | -59.80% | 1.960 |
| momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top3_reb6_off0 | raw_13612_inverse_vol | lb1_3_6_12 | 3 | 6 | 22.06% | -58.39% | 0.735 | 81.06% | -58.39% | 1.613 |
| momv2_us_stocks_raw_13612_lb6_top5_reb6_off0 | raw_13612 | lb6 | 5 | 6 | 21.02% | -72.15% | 0.734 | 76.41% | -72.15% | 1.844 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top5_reb6_off0 | raw_13612_abs_cash | lb6 | 5 | 6 | 21.02% | -72.15% | 0.734 | 76.41% | -72.15% | 1.844 |
| momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb3_off0 | raw_13612_inverse_vol | lb6 | 5 | 3 | 19.91% | -76.33% | 0.731 | 72.91% | -76.33% | 3.154 |
| momv2_us_stocks_raw_13612_lb6_top5_reb3_off0 | raw_13612 | lb6 | 5 | 3 | 20.01% | -77.58% | 0.714 | 71.47% | -77.58% | 2.995 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top5_reb3_off0 | raw_13612_abs_cash | lb6 | 5 | 3 | 20.01% | -77.58% | 0.714 | 71.47% | -77.58% | 2.995 |
| momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb12_off0 | raw_13612_inverse_vol | lb6 | 5 | 12 | 19.15% | -72.19% | 0.713 | 70.45% | -67.58% | 0.968 |
| momv2_us_stocks_clenow_trend_inverse_vol_lb1_3_6_12_top20_reb12_off0 | clenow_trend_inverse_vol | lb1_3_6_12 | 20 | 12 | 14.92% | -49.97% | 0.712 | 84.43% | -49.69% | 0.943 |
| momv2_us_stocks_vol_adjusted_13612_abs_cash_lb6_top15_reb6_off0 | vol_adjusted_13612_abs_cash | lb6 | 15 | 6 | 13.82% | -59.89% | 0.707 | 47.02% | -59.89% | 1.893 |
| momv2_us_stocks_raw_13612_lb6_top5_reb12_off0 | raw_13612 | lb6 | 5 | 12 | 19.64% | -73.08% | 0.706 | 72.37% | -68.32% | 0.950 |
| momv2_us_stocks_raw_13612_abs_cash_lb6_top5_reb12_off0 | raw_13612_abs_cash | lb6 | 5 | 12 | 19.64% | -73.08% | 0.706 | 72.37% | -68.32% | 0.950 |
| momv2_us_stocks_vol_adjusted_13612_lb6_top15_reb6_off0 | vol_adjusted_13612 | lb6 | 15 | 6 | 13.83% | -61.77% | 0.705 | 47.22% | -61.77% | 1.893 |
| momv2_us_stocks_vol_adjusted_13612_abs_cash_lb6_top15_reb3_off0 | vol_adjusted_13612_abs_cash | lb6 | 15 | 3 | 13.64% | -61.86% | 0.705 | 60.36% | -61.86% | 3.101 |
| momv2_us_stocks_clenow_trend_lb1_3_6_12_top20_reb12_off0 | clenow_trend | lb1_3_6_12 | 20 | 12 | 15.38% | -53.77% | 0.703 | 84.78% | -53.40% | 0.924 |
| momv2_us_stocks_vol_adjusted_13612_inverse_vol_lb6_top15_reb6_off0 | vol_adjusted_13612_inverse_vol | lb6 | 15 | 6 | 12.69% | -56.62% | 0.699 | 48.44% | -56.62% | 1.910 |
| momv2_us_stocks_vol_adjusted_13612_lb6_top15_reb3_off0 | vol_adjusted_13612 | lb6 | 15 | 3 | 13.54% | -63.65% | 0.698 | 58.41% | -63.65% | 3.099 |

## PBO summary

| group | pbo | n_configs | n_configs_total | sampled | pass |
|---|---|---|---|---|---|
| all | 0.7341269841269841 | 840 | 840 | False | False |
| mechanism:clenow_trend | 0.6944444444444444 | 20 | 20 | False | False |
| mechanism:clenow_trend_abs_cash | 0.8214285714285714 | 20 | 20 | False | False |
| mechanism:clenow_trend_inverse_vol | 0.8293650793650794 | 20 | 20 | False | False |
| mechanism:composite_mom_lowvol | 0.8293650793650794 | 80 | 80 | False | False |
| mechanism:composite_mom_lowvol_abs_cash | 0.8293650793650794 | 80 | 80 | False | False |
| mechanism:composite_mom_lowvol_inverse_vol | 0.7658730158730159 | 80 | 80 | False | False |
| mechanism:mom_12_1 | 0.8373015873015873 | 20 | 20 | False | False |
| mechanism:mom_12_1_abs_cash | 0.8412698412698413 | 20 | 20 | False | False |
| mechanism:mom_12_1_inverse_vol | 0.7658730158730159 | 20 | 20 | False | False |
| mechanism:raw_13612 | 0.7222222222222222 | 80 | 80 | False | False |
| mechanism:raw_13612_abs_cash | 0.7301587301587301 | 80 | 80 | False | False |
| mechanism:raw_13612_inverse_vol | 0.7063492063492064 | 80 | 80 | False | False |
| mechanism:vol_adjusted_13612 | 0.7182539682539683 | 80 | 80 | False | False |
| mechanism:vol_adjusted_13612_abs_cash | 0.7142857142857143 | 80 | 80 | False | False |
| mechanism:vol_adjusted_13612_inverse_vol | 0.8055555555555556 | 80 | 80 | False | False |
