# Validate Gates — `us_stocks`

Status: **research-only**, `promotion_eligible=false`. The Postgres universe plus survivorship filters *mitigate* but do not *eliminate* bias — the yfinance feed never captured most fully delisted names, so historical screens stay inflated `[advances_fin_ml, p.208-211]`. Main rankings are after Brazil's annual 15% realized-gain tax, gross of transaction costs/slippage. Benchmark: SPY.

Hard gates (zero bypass) `[advances_fin_ml, p.208-211, p.273-275]`: PBO<0.5, DSR p<0.05, WF>=6/8 profitable windows, bootstrap CI-low Sharpe>0, cross-library CAGR within +/-3pp. MDD is a warning-only tier (mandate §5), so it does **not** block the WF gate here. A FAIL is still the honest, expected outcome for survivorship-biased screens.

## Verdict

- Honest trial count: `984`
- Set PBO: `0.357` (pass=True)
- **Overall: PASS**

## Per-config gates

| Name | DSR p | DSR | WF | Boot CI low | xlib Δpp | All gates |
|---|---|---|---|---|---|---|
| evo_momv2_us_stocks_raw_13612_lb6_top20_reb3_off0_staggered_stock_sma100 | 0.0003 | pass | 8/8 pass | 0.776 | 0.011 | PASS |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb3_off0_staggered_stock_sma100 | 0.0003 | pass | 8/8 pass | 0.776 | 0.011 | PASS |
| evo_momv2_us_stocks_raw_13612_lb6_top20_reb3_off0_staggered_none | 0.0002 | pass | 8/8 pass | 0.768 | 0.011 | PASS |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top20_reb3_off0_staggered_none | 0.0002 | pass | 8/8 pass | 0.768 | 0.011 | PASS |
| evo_momv2_us_stocks_raw_13612_inverse_vol_lb1_3_6_12_top20_reb3_off0_fixed_none | 0.0010 | pass | 8/8 pass | 0.674 | 0.009 | PASS |
| evo_momv2_us_stocks_raw_13612_lb6_top20_reb3_off0_fixed_none | 0.0004 | pass | 8/8 pass | 0.743 | 0.011 | PASS |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_staggered_none | 0.1150 | FAIL | 8/8 pass | 0.564 | 0.015 | FAIL |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top5_reb6_off0_staggered_none | 0.1150 | FAIL | 8/8 pass | 0.564 | 0.015 | FAIL |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top5_reb6_off0_fixed_none | 0.1121 | FAIL | 8/8 pass | 0.539 | 0.015 | FAIL |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_fixed_none | 0.1121 | FAIL | 8/8 pass | 0.539 | 0.015 | FAIL |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top5_reb6_off0_staggered_market_sma200_monthly | 0.3463 | FAIL | 8/8 pass | 0.459 | 0.015 | FAIL |
| evo_momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_staggered_market_sma200_monthly | 0.3463 | FAIL | 8/8 pass | 0.459 | 0.015 | FAIL |
