# Phase 1 - Risk-Off Alternatives

Status: research-only risk-off sweep. This report does not authorize deployment, paper trading or a mandate change.

Method references: the LRS premise is still Gayed SMA200 risk-on/risk-off `[leverage_for_the_long_run, p.13]`. This phase changes only the defensive sleeve because high-volatility drawdowns and path dependency are the main enemies of leverage `[leverage_for_the_long_run, p.4-7]`. Weekly lag and rolling diagnostics remain implementation checks `[testing_tuning, p.327-335]`.

## Executive Conclusion

Phase 1 evaluated `264` rows: 4 branches x 11 risk-off sleeves x lags `0..5`. Top score row: `SPY_2x` risk-off `40 ZROZ / 40 GLD / 20 IEF` lag `5` with after-tax CAGR 15.23%, MDD -41.34%, Calmar 0.368, terminal 11.03x vs underlying. Rows at or below the 50% MDD target with positive underlying outperformance: `34`. Rows outside ruin territory (`MDD >= -65%` by the restart tiers): `90`.

Practical read: if this phase still has no practical-pass rows, the next evolution must combine better risk-off with lower leverage, volatility throttle or bear-market sleeve rather than adding many indicators.

## Source And Rules

| Item | Value |
|---|---|
| Data | `data/testfolio/cache/history.parquet` |
| Signal | `underlying.shift(1) > SMA200.shift(1)` |
| Cadence | first trading day of each week |
| Settlement lag | `n = 0..5` daily bars in `CASHX` before entering the new sleeve |
| Risk-off assets | `CASHX`, underlying, `GLDSIM`, `IEFSIM`, `ZROZSIM`, baskets and momentum off-leg |
| Tax | annual 15% DARF on realized net gains plus final liquidation |


## Test Windows

Analysis: Phase 1 uses a common branch window including GLD/IEF/ZROZ/CASH so every risk-off candidate in the same branch is comparable. This intentionally shortens the SPY branch versus Phase 0's cash-only 1885+ baseline.

| Branch | Start | End | Years | Underlying CAGR | Underlying MDD | LETF B&H CAGR | LETF B&H MDD |
|---|---|---|---|---|---|---|---|
| QQQ_2x | 1986-01-03 | 2026-05-21 | 40.4 | 14.36% | -82.97% | 17.30% | -98.85% |
| QQQ_3x | 1986-01-03 | 2026-05-21 | 40.4 | 14.36% | -82.97% | 12.44% | -99.98% |
| SPY_2x | 1968-04-02 | 2026-05-21 | 58.1 | 10.56% | -55.14% | 11.60% | -88.27% |
| SPY_3x | 1968-04-02 | 2026-05-21 | 58.1 | 10.56% | -55.14% | 9.20% | -98.31% |

## Plots

| Plot | File |
|---|---|
| SPY_2x best score | [plots/phase01_spy_2x_lag5_40_zroz___40_gld___20_ief.png](plots/phase01_spy_2x_lag5_40_zroz___40_gld___20_ief.png) |
| SPY_3x best score | [plots/phase01_spy_3x_lag5_50_zroz___50_gld.png](plots/phase01_spy_3x_lag5_50_zroz___50_gld.png) |
| QQQ_2x best score | [plots/phase01_qqq_2x_lag0_zroz.png](plots/phase01_qqq_2x_lag0_zroz.png) |
| QQQ_3x best score | [plots/phase01_qqq_3x_lag0_zroz.png](plots/phase01_qqq_3x_lag0_zroz.png) |
| Risk-off frontier | [plots/phase01_risk_off_frontier.png](plots/phase01_risk_off_frontier.png) |

## Top Ranked Rows

Analysis: score now penalizes ruin-level drawdown. This is a research ranking, not a validation gate.

| Branch | Risk-Off | Lag | Tier | CAGR | MDD | Calmar | Spread vs U | Terminal/U | Hit 10y | Turn/Yr | Pass |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY_2x | 40 ZROZ / 40 GLD / 20 IEF | 5 | tolerable | 15.23% | -41.34% | 0.368 | +4.67pp | 11.03x | 95.0% | 4.20 | yes |
| SPY_2x | 50 ZROZ / 25 GLD / 25 CASH | 5 | tolerable | 14.91% | -41.99% | 0.355 | +4.35pp | 9.40x | 92.8% | 3.69 | yes |
| SPY_2x | 50 ZROZ / 25 GLD / 25 CASH | 3 | tolerable | 15.59% | -41.78% | 0.373 | +5.03pp | 13.27x | 98.5% | 5.40 | yes |
| SPY_2x | 40 ZROZ / 40 GLD / 20 IEF | 3 | tolerable | 15.88% | -41.64% | 0.381 | +5.32pp | 15.31x | 99.4% | 6.17 | yes |
| SPY_2x | 50 ZROZ / 50 GLD | 5 | tolerable | 15.47% | -42.94% | 0.360 | +4.91pp | 12.45x | 95.3% | 4.20 | yes |
| SPY_2x | 50 ZROZ / 50 GLD | 3 | tolerable | 16.11% | -42.35% | 0.381 | +5.55pp | 17.22x | 99.6% | 6.17 | yes |
| SPY_2x | 60 ZROZ / 40 GLD | 3 | tolerable | 16.12% | -43.66% | 0.369 | +5.56pp | 17.25x | 99.4% | 6.17 | yes |
| SPY_2x | 60 ZROZ / 40 GLD | 5 | tolerable | 15.42% | -44.52% | 0.346 | +4.86pp | 12.18x | 94.7% | 4.20 | yes |
| SPY_2x | IEF | 5 | tolerable | 14.14% | -41.94% | 0.337 | +3.58pp | 6.37x | 91.2% | 4.20 | yes |
| SPY_2x | 50 ZROZ / 50 GLD | 4 | tolerable | 16.04% | -44.49% | 0.361 | +5.48pp | 16.60x | 98.1% | 5.89 | yes |
| SPY_2x | 60 ZROZ / 40 GLD | 4 | tolerable | 15.98% | -44.56% | 0.359 | +5.42pp | 16.12x | 98.4% | 5.89 | yes |
| SPY_2x | 40 ZROZ / 40 GLD / 20 IEF | 4 | tolerable | 15.75% | -44.20% | 0.356 | +5.19pp | 14.38x | 97.9% | 5.89 | yes |
| SPY_2x | CASHX | 5 | tolerable | 13.25% | -42.70% | 0.310 | +2.69pp | 4.03x | 83.8% | 2.15 | yes |
| SPY_2x | IEF | 3 | tolerable | 14.81% | -42.47% | 0.349 | +4.25pp | 8.93x | 97.1% | 6.17 | yes |
| SPY_2x | 50 ZROZ / 25 GLD / 25 CASH | 4 | tolerable | 15.38% | -44.91% | 0.342 | +4.82pp | 11.90x | 96.4% | 5.16 | yes |
| SPY_2x | 60 ZROZ / 40 GLD | 2 | tolerable | 15.88% | -45.49% | 0.349 | +5.32pp | 15.32x | 98.7% | 6.17 | yes |
| SPY_2x | 50 ZROZ / 50 GLD | 2 | tolerable | 15.80% | -45.70% | 0.346 | +5.24pp | 14.74x | 98.7% | 6.17 | yes |
| SPY_2x | 40 ZROZ / 40 GLD / 20 IEF | 2 | tolerable | 15.60% | -45.38% | 0.344 | +5.04pp | 13.30x | 98.3% | 6.17 | yes |
| SPY_2x | 50 ZROZ / 25 GLD / 25 CASH | 2 | tolerable | 15.37% | -45.83% | 0.335 | +4.81pp | 11.83x | 96.9% | 5.40 | yes |
| SPY_2x | CASHX | 3 | tolerable | 13.76% | -44.89% | 0.306 | +3.20pp | 5.23x | 89.9% | 3.08 | yes |
| SPY_2x | GLD | 5 | tolerable | 15.39% | -46.25% | 0.333 | +4.83pp | 11.95x | 80.3% | 4.20 | yes |
| SPY_2x | GLD | 4 | tolerable | 16.00% | -45.84% | 0.349 | +5.44pp | 16.23x | 82.2% | 5.89 | yes |
| SPY_2x | IEF | 2 | tolerable | 14.65% | -44.60% | 0.328 | +4.09pp | 8.22x | 95.2% | 6.17 | yes |
| SPY_2x | 60 ZROZ / 40 GLD | 1 | tolerable | 15.13% | -45.81% | 0.330 | +4.57pp | 10.50x | 95.3% | 6.17 | yes |
| SPY_2x | 50 ZROZ / 50 GLD | 1 | tolerable | 15.01% | -45.84% | 0.327 | +4.45pp | 9.89x | 95.2% | 6.17 | yes |
| SPY_2x | 40 ZROZ / 40 GLD / 20 IEF | 1 | tolerable | 14.81% | -45.75% | 0.324 | +4.25pp | 8.92x | 94.7% | 6.17 | yes |
| SPY_2x | 50 ZROZ / 25 GLD / 25 CASH | 1 | tolerable | 14.63% | -46.41% | 0.315 | +4.07pp | 8.15x | 93.3% | 5.40 | yes |
| SPY_2x | GLD | 3 | tolerable | 15.75% | -46.37% | 0.340 | +5.19pp | 14.36x | 83.7% | 6.17 | yes |
| SPY_2x | IEF | 4 | tolerable | 14.48% | -45.59% | 0.317 | +3.92pp | 7.54x | 94.9% | 5.89 | yes |
| SPY_2x | CASHX | 4 | tolerable | 13.43% | -47.51% | 0.283 | +2.87pp | 4.44x | 85.4% | 2.95 | yes |

## Best Row By Branch

| Branch | Best Risk-Off | Lag | Tier | CAGR | MDD | Calmar | Terminal/U |
|---|---|---|---|---|---|---|---|
| QQQ_2x | ZROZ | 0 | ruin | 21.77% | -71.32% | 0.305 | 12.61x |
| QQQ_3x | ZROZ | 0 | ruin | 24.45% | -88.31% | 0.277 | 30.42x |
| SPY_2x | 40 ZROZ / 40 GLD / 20 IEF | 5 | tolerable | 15.23% | -41.34% | 0.368 | 11.03x |
| SPY_3x | 50 ZROZ / 50 GLD | 5 | warning | 17.90% | -61.04% | 0.293 | 41.84x |

## Best Row By Risk-Off Sleeve

| Risk-Off | Best Branch | Lag | Tier | CAGR | MDD | Calmar | Terminal/U |
|---|---|---|---|---|---|---|---|
| 40 ZROZ / 40 GLD / 20 IEF | SPY_2x | 5 | tolerable | 15.23% | -41.34% | 0.368 | 11.03x |
| 50 ZROZ / 25 GLD / 25 CASH | SPY_2x | 5 | tolerable | 14.91% | -41.99% | 0.355 | 9.40x |
| 50 ZROZ / 50 GLD | SPY_2x | 5 | tolerable | 15.47% | -42.94% | 0.360 | 12.45x |
| 60 ZROZ / 40 GLD | SPY_2x | 3 | tolerable | 16.12% | -43.66% | 0.369 | 17.25x |
| CASHX | SPY_2x | 5 | tolerable | 13.25% | -42.70% | 0.310 | 4.03x |
| GLD | SPY_2x | 5 | tolerable | 15.39% | -46.25% | 0.333 | 11.95x |
| IEF | SPY_2x | 5 | tolerable | 14.14% | -41.94% | 0.337 | 6.37x |
| MOM126 ZROZ/IEF/GLD/CASH | SPY_2x | 5 | warning | 14.03% | -58.15% | 0.241 | 6.02x |
| MOM63 ZROZ/IEF/GLD | SPY_2x | 2 | tolerable | 14.34% | -49.24% | 0.291 | 7.03x |
| UNDERLYING | SPY_2x | 5 | warning | 13.37% | -62.05% | 0.215 | 4.29x |
| ZROZ | SPY_2x | 5 | warning | 15.03% | -50.69% | 0.297 | 10.00x |

## Phase Verdict

| Question | Verdict |
|---|---|
| Did any row meet the <=50% MDD practical target and beat underlying? | Yes. |
| Did any row exit ruin territory (`MDD >= -65%`)? | Yes. |
| Is this deployment-ready? | No. This is a risk-off discovery phase only. |

Next step: if drawdown remains excessive, test lower target leverage and volatility/bear-market throttles before expanding to broad multi-indicator votes.
