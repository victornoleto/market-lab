# Validate Gates — `us_stocks`

Status: **research-only**, `promotion_eligible=false`. The Postgres universe plus survivorship filters *mitigate* but do not *eliminate* bias — the yfinance feed never captured most fully delisted names, so historical screens stay inflated `[advances_fin_ml, p.208-211]`. Main rankings are after Brazil's annual 15% realized-gain tax, gross of transaction costs/slippage. Benchmark: SPY.

Hard gates (zero bypass) `[advances_fin_ml, p.208-211, p.273-275]`: PBO<0.5, DSR p<0.05, WF>=6/8 profitable windows, bootstrap CI-low Sharpe>0, cross-library CAGR within +/-3pp. MDD is a warning-only tier (mandate §5), so it does **not** block the WF gate here. A FAIL is still the honest, expected outcome for survivorship-biased screens.

## Verdict

- Honest trial count: `972`
- Set PBO: `0.639` (pass=False)
- **Overall: FAIL**

## Per-config gates

| Name | DSR p | DSR | WF | Boot CI low | xlib Δpp | All gates |
|---|---|---|---|---|---|---|
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb6_off0_fixed_market_sma200_monthly | 0.0511 | FAIL | 8/8 pass | 0.402 | 0.010 | FAIL |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb6_off0_fixed_market_sma200_monthly_stock_sma100 | 0.0581 | FAIL | 8/8 pass | 0.408 | 0.010 | FAIL |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_fixed_market_sma200_monthly | 0.0736 | FAIL | 8/8 pass | 0.364 | 0.015 | FAIL |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb6_off0_fixed_market_sma200_daily | 0.0439 | pass | 8/8 pass | 0.384 | 0.010 | PASS |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_fixed_market_sma200_monthly_stock_sma100 | 0.0930 | FAIL | 8/8 pass | 0.346 | 0.015 | FAIL |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb6_off0_fixed_market_sma200_daily_stock_sma100 | 0.0513 | FAIL | 8/8 pass | 0.363 | 0.010 | FAIL |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb6_top5_reb6_off0_staggered_market_sma200_monthly_stock_sma100 | 0.1531 | FAIL | 8/8 pass | 0.340 | 0.010 | FAIL |
