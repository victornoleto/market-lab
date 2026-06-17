# Validate Gates — `us_stocks`

Status: **research-only**, `promotion_eligible=false`. The Postgres universe plus survivorship filters *mitigate* but do not *eliminate* bias — the yfinance feed never captured most fully delisted names, so historical screens stay inflated `[advances_fin_ml, p.208-211]`. Main rankings are after Brazil's annual 15% realized-gain tax, gross of transaction costs/slippage. Benchmark: SPY.

Hard gates (zero bypass) `[advances_fin_ml, p.208-211, p.273-275]`: PBO<0.5, DSR p<0.05, WF>=6/8 profitable windows, bootstrap CI-low Sharpe>0, cross-library CAGR within +/-3pp. MDD is a warning-only tier (mandate §5), so it does **not** block the WF gate here. A FAIL is still the honest, expected outcome for survivorship-biased screens.

## Verdict

- Honest trial count: `1332`
- Set PBO: `0.548` (pass=False)
- **Overall: FAIL**

## Per-config gates

| Name | DSR p | DSR | WF | Boot CI low | xlib Δpp | All gates |
|---|---|---|---|---|---|---|
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_fixed_none | 0.0099 | pass | 8/8 pass | 0.696 | 0.013 | PASS |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_fixed_none | 0.0099 | pass | 8/8 pass | 0.696 | 0.013 | PASS |
| evo_momv2_us_stocks_raw_13612_lb6_top15_reb2_off0_staggered_none | 0.0027 | pass | 8/8 pass | 0.657 | 0.010 | PASS |
| evo_momv2_us_stocks_raw_13612_abs_cash_lb6_top15_reb2_off0_staggered_none | 0.0027 | pass | 8/8 pass | 0.657 | 0.010 | PASS |
| evo_momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb2_off0_staggered_none | 0.0006 | pass | 8/8 pass | 0.775 | 0.013 | PASS |
| evo_momv2_us_stocks_clenow_trend_abs_cash_lb1_3_6_12_top10_reb2_off0_staggered_none | 0.0006 | pass | 8/8 pass | 0.775 | 0.013 | PASS |
