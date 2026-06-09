# Four-Asset Monthly Grid

Status: research-only diagnostic. No deployment, paper-trade label or mandate change.

## Summary

- Window: `2000-01-03..2026-06-08`.
- Assets: `NTSXSIM, GDESIM, RSST70_30, ZROZSIM`.
- Grid: `5%` increments, `1,771` portfolios, monthly rebalance.
- Best by rank-based fitness: **40% GDESIM + 25% RSST70_30 + 35% ZROZSIM**, score `90.95`, CAGR `12.15%`, MDD `-27.80%`, Sharpe `0.851`, Calmar `0.437`.

## Method

The Testfol.io payload downloads `NTSXSIM`, `GDESIM`, `ZROZSIM`, and an `RSST70_30` tracking sleeve defined as `100% SPYSIM + 70% DBMFSIM + 30% KMLMSIM - 100% CASHX?E=-2`. The grid then simulates monthly rebalanced portfolio returns across all `[a,b,c,d]` weights where each component is a multiple of 5% and sums to 100%. Monthly rebalance is the requested cadence and matches the RSC research convention for turnover/friction discipline `[systematic_trading, p.185-188]`, `[risk_parity, p.80-81]`.

Correction note: an earlier run used `CASHX?E=2`; that was a financing-sign error. The current canonical four-asset grid uses `CASHX?E=-2`, matching the correct RSST tracking payload `[systematic_trading, p.185-188]`.

Fitness is a rank blend: 25% Calmar, 20% Sharpe, 15% Sortino, 20% CAGR, 10% drawdown safety and 10% volatility safety. Rank scoring avoids mixing raw metric scales and keeps the result as a screening heuristic, not a validation gate `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

## Top 20

| rank | portfolio | fitness_score | cagr | mdd | vol | sharpe | sortino | calmar | terminal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 40% GDESIM / 25% RSST70_30 / 35% ZROZSIM | 90.95 | 12.15% | -27.80% | 14.76% | 0.851 | 1.225 | 0.437 | 20.571 |
| 2 | 35% GDESIM / 30% RSST70_30 / 35% ZROZSIM | 90.71 | 11.90% | -26.40% | 14.50% | 0.848 | 1.221 | 0.451 | 19.388 |
| 3 | 40% GDESIM / 30% RSST70_30 / 30% ZROZSIM | 90.46 | 12.36% | -28.78% | 15.08% | 0.848 | 1.219 | 0.430 | 21.618 |
| 4 | 45% GDESIM / 20% RSST70_30 / 35% ZROZSIM | 90.35 | 12.39% | -29.23% | 15.07% | 0.851 | 1.226 | 0.424 | 21.788 |
| 5 | 45% GDESIM / 25% RSST70_30 / 30% ZROZSIM | 90.33 | 12.61% | -29.68% | 15.36% | 0.850 | 1.222 | 0.425 | 22.909 |
| 6 | 35% GDESIM / 35% RSST70_30 / 30% ZROZSIM | 90.16 | 12.11% | -27.90% | 14.84% | 0.844 | 1.213 | 0.434 | 20.364 |
| 7 | 50% GDESIM / 20% RSST70_30 / 30% ZROZSIM | 90.11 | 12.85% | -30.57% | 15.68% | 0.849 | 1.222 | 0.420 | 24.236 |
| 8 | 5% NTSXSIM / 40% GDESIM / 25% RSST70_30 / 30% ZROZSIM | 90.06 | 12.25% | -28.83% | 14.96% | 0.847 | 1.219 | 0.425 | 21.059 |
| 9 | 30% GDESIM / 35% RSST70_30 / 35% ZROZSIM | 90.01 | 11.64% | -25.04% | 14.29% | 0.842 | 1.211 | 0.465 | 18.243 |
| 10 | 5% NTSXSIM / 35% GDESIM / 30% RSST70_30 / 30% ZROZSIM | 89.98 | 12.00% | -27.93% | 14.71% | 0.844 | 1.214 | 0.430 | 19.849 |
| 11 | 5% NTSXSIM / 45% GDESIM / 20% RSST70_30 / 30% ZROZSIM | 89.95 | 12.49% | -29.74% | 15.26% | 0.848 | 1.221 | 0.420 | 22.305 |
| 12 | 50% GDESIM / 15% RSST70_30 / 35% ZROZSIM | 89.78 | 12.63% | -30.64% | 15.42% | 0.849 | 1.224 | 0.412 | 23.037 |
| 13 | 5% NTSXSIM / 35% GDESIM / 25% RSST70_30 / 35% ZROZSIM | 89.74 | 11.78% | -27.90% | 14.40% | 0.846 | 1.219 | 0.422 | 18.881 |
| 14 | 5% NTSXSIM / 50% GDESIM / 15% RSST70_30 / 30% ZROZSIM | 89.71 | 12.73% | -30.64% | 15.60% | 0.847 | 1.219 | 0.416 | 23.584 |
| 15 | 10% NTSXSIM / 40% GDESIM / 20% RSST70_30 / 30% ZROZSIM | 89.59 | 12.13% | -28.89% | 14.86% | 0.845 | 1.217 | 0.420 | 20.501 |
| 16 | 10% NTSXSIM / 35% GDESIM / 25% RSST70_30 / 30% ZROZSIM | 89.46 | 11.89% | -27.99% | 14.60% | 0.842 | 1.213 | 0.425 | 19.333 |
| 17 | 5% NTSXSIM / 40% GDESIM / 20% RSST70_30 / 35% ZROZSIM | 89.43 | 12.03% | -29.33% | 14.68% | 0.848 | 1.222 | 0.410 | 20.021 |
| 18 | 10% NTSXSIM / 45% GDESIM / 15% RSST70_30 / 30% ZROZSIM | 89.40 | 12.38% | -29.90% | 15.17% | 0.845 | 1.217 | 0.414 | 21.702 |
| 19 | 5% NTSXSIM / 30% GDESIM / 30% RSST70_30 / 35% ZROZSIM | 89.38 | 11.53% | -26.50% | 14.18% | 0.841 | 1.211 | 0.435 | 17.775 |
| 20 | 55% GDESIM / 15% RSST70_30 / 30% ZROZSIM | 89.34 | 13.08% | -31.58% | 16.05% | 0.847 | 1.218 | 0.414 | 25.596 |

## Reference Rows

| portfolio | fitness_score | cagr | mdd | vol | sharpe | sortino | calmar | terminal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 25% NTSXSIM / 25% GDESIM / 25% RSST70_30 / 25% ZROZSIM | 81.32 | 11.23% | -29.26% | 14.33% | 0.814 | 1.171 | 0.384 | 16.558 |
| 35% GDESIM / 40% RSST70_30 / 25% ZROZSIM | 86.24 | 12.29% | -30.76% | 15.38% | 0.831 | 1.190 | 0.400 | 21.278 |
| 100% NTSXSIM | 9.51 | 8.90% | -46.07% | 16.92% | 0.589 | 0.838 | 0.193 | 9.485 |
| 100% GDESIM | 47.91 | 15.86% | -52.71% | 24.06% | 0.733 | 1.042 | 0.301 | 48.516 |
| 100% RSST70_30 | 19.50 | 10.82% | -42.64% | 20.76% | 0.599 | 0.844 | 0.254 | 15.013 |
| 100% ZROZSIM | 0.06 | 5.61% | -62.94% | 23.68% | 0.349 | 0.502 | 0.089 | 4.222 |

## Artifacts

- Raw response: `studies/return_stacked_core/us_core/four_asset_grid/raw/testfolio_four_asset_response.json`.
- Payload: `studies/return_stacked_core/us_core/four_asset_grid/raw/testfolio_four_asset_payload.json`.
- Asset equity curves: `studies/return_stacked_core/us_core/four_asset_grid/results/asset_equity_curves.csv`.
- Full grid: `studies/return_stacked_core/us_core/four_asset_grid/results/four_asset_monthly_grid.csv`.

- Walk-forward anti-overfit report: `studies/return_stacked_core/us_core/four_asset_grid/WF_REPORT.md`.

- Robustness/PBO report: `studies/return_stacked_core/us_core/four_asset_grid/ROBUSTNESS_REPORT.md`.

## Caveats

This is a Testfol.io simulation screen. `RSST70_30` is a tracking proxy, not a live RSST ETF backfill. The grid does not include tax, implementation friction, DSR, bootstrap or cross-library gates. The separate walk-forward and PBO robustness reports test the full-sample weight-selection overfit risk and must be read before treating the top-20 as anything beyond research leads `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
