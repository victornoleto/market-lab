# Factor Core Comparison Data Audit

Status: generated from sanitized Testfol.io payload. No authorization header or Bearer token is stored in this folder.

Primary case: `us_short_live_yearly` with `Yearly` rebalance. Sensitivity case: `us_short_live_monthly` with `Monthly` rebalance.

Common aligned window: `2022-03-17` to `2026-06-12` (`1064` daily bars).

## Raw Coverage

| portfolio | first_non_null | last_non_null | bars |
|---|---|---|---|
| AVUS | 2022-03-17 | 2026-06-12 | 1064 |
| AVUV | 2022-03-17 | 2026-06-12 | 1064 |
| SPMO | 2022-03-17 | 2026-06-12 | 1064 |
| AVUS_AVUV_SPMO_60_20_20 | 2022-03-17 | 2026-06-12 | 1064 |
| RSC_US_TRACKING | 2022-03-17 | 2026-06-12 | 1064 |

## Saved Artifacts

- `payloads/us_short_live_yearly.json`: sanitized request body only.
- `raw/us_short_live_yearly.json`: Testfol.io response, if fetch succeeded.
- `results/us_short_live_yearly_metrics.csv`: metrics table.
- `results/us_short_live_yearly_equity.csv`: normalized aligned equity curves.
- `results/us_short_live_yearly_returns.csv`: daily returns from aligned equity.
- `results/us_short_live_yearly_relative_to_rsc.csv`: terminal/min/max relative wealth vs RSC.
- `results/us_short_live_yearly_correlations.csv`: return correlation matrix.
- `payloads/us_short_live_monthly.json`: sanitized monthly-sensitivity request body only.
- `raw/us_short_live_monthly.json`: Testfol.io response, if fetch succeeded.
- `results/us_short_live_monthly_metrics.csv`: monthly-sensitivity metrics table.
- `results/us_short_live_monthly_equity.csv`: monthly-sensitivity normalized aligned equity curves.
- `results/us_short_live_monthly_returns.csv`: monthly-sensitivity daily returns from aligned equity.
- `results/us_short_live_monthly_relative_to_rsc.csv`: monthly-sensitivity terminal/min/max relative wealth vs RSC.
- `results/us_short_live_monthly_correlations.csv`: monthly-sensitivity return correlation matrix.

## Caveats

- Common window is determined by the youngest live ETF/proxy in the payload, so this is a short-window implementation diagnostic.
- The primary payload uses yearly rebalance because that was the user-provided comparison. Monthly rebalance is recorded as a sensitivity, not selected as an optimized setting `[testing_tuning, p.327-335]`.
- Testfol.io output is treated as an external-engine artifact. It is not a substitute for long-history proxy work or mandate gates `[advances_fin_ml, p.208-211]`.
