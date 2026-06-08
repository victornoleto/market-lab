# Phase 2 - Target Leverage And Volatility Throttle

Status: research-only leverage/throttle sweep. This report does not authorize deployment, paper trading or a mandate change.

Method references: the LRS rule remains Gayed SMA200 risk-on/risk-off `[leverage_for_the_long_run, p.13]`. The volatility throttle uses Gayed's observation that high volatility is the enemy of leveraged compounding and that above roughly 40% annualized volatility the constant leverage trap dominates `[leverage_for_the_long_run, p.4-7]`. Target leverage and vol scaling follow the broader position-sizing principle that leverage should be reduced when risk rises `[systematic_trading, p.137-148]`.

## Executive Conclusion

Phase 2 evaluated `2,400` rows: SPY/QQQ x 8 target leverages x 5 risk-off sleeves x 5 volatility filters x lags `0..5`. Top score row: `SPY` L`2.00` risk-off `50 ZROZ / 25 GLD / 25 CASH` vol `RV21 <= 30%` lag `3` with after-tax CAGR 15.44%, MDD -39.28%, Calmar 0.393, terminal 12.28x vs underlying. Practical-pass rows (`MDD >= -50%` and after-tax underlying outperformance): `875`. Preferred drawdown rows (`MDD >= -40%`): `394`. QQQ practical-pass rows: `303`.

Practical read: this phase determines whether drawdown can be reduced by changing exposure geometry before adding multi-indicator votes.

## Source And Rules

| Item | Value |
|---|---|
| Data | `data/testfolio/cache/history.parquet` |
| Signal | `underlying.shift(1) > SMA200.shift(1)` plus optional realized-vol gate |
| Target leverage | `1.25x..3.00x`, adjacent ETF ladder, no negative cash |
| Risk-off sleeves | selected Phase 1 sleeves |
| Settlement lag | `n = 0..5` daily bars in `CASHX` before entering the new sleeve |
| Tax | annual 15% DARF on realized net gains plus final liquidation |


## Test Windows

| Branch | Start | End | Years | Underlying CAGR | Underlying MDD |
|---|---|---|---|---|---|
| QQQ | 1986-01-03 | 2026-05-21 | 40.4 | 14.36% | -82.97% |
| SPY | 1968-04-02 | 2026-05-21 | 58.1 | 10.56% | -55.14% |

## Plots

| Plot | File |
|---|---|
| SPY best score | [plots/phase02_spy_l2.00_lag3_50_zroz___25_gld___25_cash_rv21_le_30pct.png](plots/phase02_spy_l2.00_lag3_50_zroz___25_gld___25_cash_rv21_le_30pct.png) |
| QQQ best score | [plots/phase02_qqq_l1.75_lag0_40_zroz___40_gld___20_ief_rv63_le_40pct.png](plots/phase02_qqq_l1.75_lag0_40_zroz___40_gld___20_ief_rv63_le_40pct.png) |
| Risk/return frontier | [plots/phase02_frontier.png](plots/phase02_frontier.png) |
| Best by target leverage | [plots/phase02_best_by_leverage.png](plots/phase02_best_by_leverage.png) |

## Top Ranked Rows

| Branch | L | Risk-Off | Vol | Lag | Tier | CAGR | MDD | Calmar | Spread vs U | Terminal/U | Hit 10y | Pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 2.00 | 50 ZROZ / 25 GLD / 25 CASH | RV21 <= 30% | 3 | preferred | 15.44% | -39.28% | 0.393 | +4.88pp | 12.28x | 98.0% | yes |
| SPY | 1.75 | 40 ZROZ / 40 GLD / 20 IEF | RV63 <= 40% | 5 | preferred | 14.63% | -39.00% | 0.375 | +4.07pp | 8.14x | 91.3% | yes |
| SPY | 1.75 | 50 ZROZ / 25 GLD / 25 CASH | RV63 <= 40% | 5 | preferred | 14.31% | -38.37% | 0.373 | +3.75pp | 6.93x | 89.5% | yes |
| SPY | 1.75 | 50 ZROZ / 25 GLD / 25 CASH | RV63 <= 40% | 3 | preferred | 14.82% | -37.40% | 0.396 | +4.26pp | 8.97x | 95.5% | yes |
| SPY | 2.00 | 40 ZROZ / 40 GLD / 20 IEF | RV63 <= 40% | 5 | tolerable | 15.45% | -41.34% | 0.374 | +4.89pp | 12.31x | 96.6% | yes |
| SPY | 1.75 | 50 ZROZ / 25 GLD / 25 CASH | none | 3 | preferred | 14.74% | -37.38% | 0.394 | +4.18pp | 8.64x | 94.2% | yes |
| SPY | 1.75 | 50 ZROZ / 25 GLD / 25 CASH | RV21 <= 40% | 3 | preferred | 14.74% | -37.38% | 0.394 | +4.18pp | 8.64x | 94.2% | yes |
| SPY | 1.75 | 40 ZROZ / 40 GLD / 20 IEF | RV63 <= 40% | 3 | preferred | 15.10% | -38.33% | 0.394 | +4.54pp | 10.37x | 96.2% | yes |
| SPY | 2.00 | 40 ZROZ / 40 GLD / 20 IEF | RV21 <= 30% | 3 | tolerable | 15.72% | -40.19% | 0.391 | +5.16pp | 14.14x | 98.5% | yes |
| SPY | 1.75 | 40 ZROZ / 40 GLD / 20 IEF | none | 3 | preferred | 15.03% | -38.31% | 0.392 | +4.47pp | 9.97x | 95.9% | yes |
| SPY | 1.75 | 40 ZROZ / 40 GLD / 20 IEF | RV21 <= 40% | 3 | preferred | 15.03% | -38.31% | 0.392 | +4.47pp | 9.97x | 95.9% | yes |
| SPY | 2.00 | 50 ZROZ / 25 GLD / 25 CASH | RV21 <= 30% | 5 | tolerable | 14.85% | -41.02% | 0.362 | +4.29pp | 9.10x | 93.1% | yes |
| SPY | 2.00 | 40 ZROZ / 40 GLD / 20 IEF | none | 5 | tolerable | 15.23% | -41.34% | 0.368 | +4.67pp | 11.03x | 95.0% | yes |
| SPY | 2.00 | 40 ZROZ / 40 GLD / 20 IEF | RV21 <= 40% | 5 | tolerable | 15.23% | -41.34% | 0.368 | +4.67pp | 11.03x | 95.0% | yes |
| SPY | 1.75 | 50 ZROZ / 25 GLD / 25 CASH | none | 5 | preferred | 14.12% | -38.32% | 0.368 | +3.56pp | 6.29x | 85.3% | yes |
| SPY | 1.75 | 50 ZROZ / 25 GLD / 25 CASH | RV21 <= 40% | 5 | preferred | 14.12% | -38.32% | 0.368 | +3.56pp | 6.29x | 85.3% | yes |
| SPY | 2.00 | 50 ZROZ / 25 GLD / 25 CASH | RV21 <= 30% | 4 | tolerable | 15.28% | -40.43% | 0.378 | +4.72pp | 11.31x | 96.5% | yes |
| SPY | 1.75 | 40 ZROZ / 40 GLD / 20 IEF | none | 5 | preferred | 14.43% | -38.95% | 0.371 | +3.87pp | 7.38x | 86.4% | yes |
| SPY | 1.75 | 40 ZROZ / 40 GLD / 20 IEF | RV21 <= 40% | 5 | preferred | 14.43% | -38.95% | 0.371 | +3.87pp | 7.38x | 86.4% | yes |
| SPY | 1.75 | 50 ZROZ / 25 GLD / 25 CASH | RV21 <= 30% | 3 | preferred | 14.60% | -37.38% | 0.391 | +4.04pp | 8.05x | 93.2% | yes |
| SPY | 1.75 | 40 ZROZ / 40 GLD / 20 IEF | RV63 <= 40% | 4 | preferred | 14.97% | -38.93% | 0.385 | +4.41pp | 9.69x | 93.9% | yes |
| SPY | 2.00 | 40 ZROZ / 40 GLD / 20 IEF | RV21 <= 30% | 5 | tolerable | 15.15% | -41.34% | 0.367 | +4.59pp | 10.64x | 94.5% | yes |
| SPY | 2.00 | 50 ZROZ / 25 GLD / 25 CASH | RV63 <= 40% | 5 | tolerable | 15.12% | -41.99% | 0.360 | +4.56pp | 10.47x | 95.5% | yes |
| SPY | 1.75 | 50 ZROZ / 50 GLD | RV63 <= 40% | 5 | tolerable | 14.86% | -41.18% | 0.361 | +4.30pp | 9.18x | 91.4% | yes |
| SPY | 1.75 | 50 ZROZ / 25 GLD / 25 CASH | RV21 <= 30% | 4 | preferred | 14.47% | -37.21% | 0.389 | +3.91pp | 7.51x | 91.2% | yes |
| SPY | 1.75 | 50 ZROZ / 50 GLD | RV63 <= 40% | 3 | tolerable | 15.34% | -40.56% | 0.378 | +4.78pp | 11.66x | 96.6% | yes |
| SPY | 1.75 | 50 ZROZ / 50 GLD | RV63 <= 40% | 4 | tolerable | 15.25% | -40.33% | 0.378 | +4.69pp | 11.18x | 94.2% | yes |
| SPY | 1.75 | 50 ZROZ / 25 GLD / 25 CASH | RV21 <= 30% | 5 | preferred | 14.05% | -38.32% | 0.367 | +3.49pp | 6.08x | 84.8% | yes |
| SPY | 1.75 | 50 ZROZ / 25 GLD / 25 CASH | RV63 <= 40% | 4 | preferred | 14.60% | -39.28% | 0.372 | +4.04pp | 8.02x | 92.2% | yes |
| SPY | 1.75 | 40 ZROZ / 40 GLD / 20 IEF | none | 4 | preferred | 14.94% | -38.93% | 0.384 | +4.38pp | 9.52x | 93.4% | yes |
| SPY | 1.75 | 40 ZROZ / 40 GLD / 20 IEF | RV21 <= 40% | 4 | preferred | 14.94% | -38.93% | 0.384 | +4.38pp | 9.52x | 93.4% | yes |
| SPY | 2.00 | 40 ZROZ / 40 GLD / 20 IEF | RV21 <= 30% | 4 | tolerable | 15.65% | -40.69% | 0.385 | +5.09pp | 13.67x | 97.6% | yes |
| SPY | 1.75 | 40 ZROZ / 40 GLD / 20 IEF | RV21 <= 30% | 5 | preferred | 14.36% | -38.95% | 0.369 | +3.80pp | 7.11x | 84.7% | yes |
| SPY | 1.75 | 50 ZROZ / 50 GLD | none | 3 | tolerable | 15.26% | -40.54% | 0.376 | +4.70pp | 11.21x | 96.5% | yes |
| SPY | 1.75 | 50 ZROZ / 50 GLD | RV21 <= 40% | 3 | tolerable | 15.26% | -40.54% | 0.376 | +4.70pp | 11.21x | 96.5% | yes |

## Best Row By Branch

| Branch | L | Risk-Off | Vol | Lag | Tier | CAGR | MDD | Calmar | Terminal/U |
|---|---|---|---|---|---|---|---|---|---|
| QQQ | 1.75 | 40 ZROZ / 40 GLD / 20 IEF | RV63 <= 40% | 0 | tolerable | 19.46% | -42.58% | 0.457 | 5.82x |
| SPY | 2.00 | 50 ZROZ / 25 GLD / 25 CASH | RV21 <= 30% | 3 | preferred | 15.44% | -39.28% | 0.393 | 12.28x |

## Best Row By Target Leverage

| Branch | L | Risk-Off | Vol | Lag | Tier | CAGR | MDD | Calmar |
|---|---|---|---|---|---|---|---|---|
| QQQ | 1.25 | 50 ZROZ / 25 GLD / 25 CASH | RV63 <= 40% | 0 | preferred | 16.27% | -37.80% | 0.431 |
| QQQ | 1.50 | 40 ZROZ / 40 GLD / 20 IEF | RV63 <= 40% | 0 | tolerable | 17.96% | -40.63% | 0.442 |
| QQQ | 1.75 | 40 ZROZ / 40 GLD / 20 IEF | RV63 <= 40% | 0 | tolerable | 19.46% | -42.58% | 0.457 |
| QQQ | 2.00 | 50 ZROZ / 50 GLD | RV63 <= 40% | 0 | tolerable | 20.97% | -45.95% | 0.456 |
| QQQ | 2.25 | 40 ZROZ / 40 GLD / 20 IEF | RV63 <= 40% | 0 | warning | 21.86% | -51.02% | 0.428 |
| QQQ | 2.50 | 40 ZROZ / 40 GLD / 20 IEF | RV63 <= 40% | 0 | warning | 22.79% | -55.82% | 0.408 |
| QQQ | 2.75 | 50 ZROZ / 25 GLD / 25 CASH | RV63 <= 40% | 0 | warning | 23.59% | -59.91% | 0.394 |
| QQQ | 3.00 | 50 ZROZ / 25 GLD / 25 CASH | RV63 <= 40% | 0 | warning | 24.26% | -63.42% | 0.383 |
| SPY | 1.25 | 40 ZROZ / 40 GLD / 20 IEF | RV21 <= 40% | 0 | preferred | 12.29% | -32.80% | 0.375 |
| SPY | 1.50 | 50 ZROZ / 25 GLD / 25 CASH | RV63 <= 40% | 3 | preferred | 13.88% | -35.26% | 0.394 |
| SPY | 1.75 | 40 ZROZ / 40 GLD / 20 IEF | RV63 <= 40% | 5 | preferred | 14.63% | -39.00% | 0.375 |
| SPY | 2.00 | 50 ZROZ / 25 GLD / 25 CASH | RV21 <= 30% | 3 | preferred | 15.44% | -39.28% | 0.393 |
| SPY | 2.25 | 40 ZROZ / 40 GLD / 20 IEF | RV21 <= 30% | 3 | tolerable | 16.46% | -43.83% | 0.376 |
| SPY | 2.50 | 50 ZROZ / 50 GLD | RV21 <= 30% | 3 | tolerable | 17.38% | -48.54% | 0.358 |
| SPY | 2.75 | 50 ZROZ / 25 GLD / 25 CASH | RV21 <= 30% | 5 | warning | 16.74% | -53.06% | 0.316 |
| SPY | 3.00 | 50 ZROZ / 25 GLD / 25 CASH | RV21 <= 30% | 5 | warning | 17.26% | -55.83% | 0.309 |

## Phase Verdict

| Question | Verdict |
|---|---|
| Did any row meet the <=50% MDD practical target and beat underlying? | Yes. |
| Did any row meet preferred <=40% MDD? | Yes. |
| Did QQQ leave ruin territory under the practical target? | Yes. |
| Is this deployment-ready? | No. This is an exposure-geometry discovery phase only. |

Next step: use the best exposure geometry as the base for either a bear-market inverse sleeve or a small pre-registered indicator vote.
