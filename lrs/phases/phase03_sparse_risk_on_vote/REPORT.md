# Phase 3A - Sparse Risk-On Confirmation Vote

Status: research-only confirmation-filter sweep over the Phase 2 geometry. This report does not authorize deployment, paper trading or a mandate change.

Method references: the base remains the Gayed SMA200 weekly LRS signal plus a realized-vol throttle `[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.4-7]`. Each row ANDs at most ONE structurally distinct confirmation filter onto that base and is compared against a `none` control; filters are not combined (no vote-of-K yet), keeping the panel small to limit overfit risk `[trading_systems_methods, p.939]`, `[advances_fin_ml, p.208-211]`. Filter families: trend quality (Clenow annualized slope x R^2) `[stocks_on_the_move, p.70-77, p.98]`; simple momentum / ROC `[stocks_on_the_move, p.58, p.60]`; SMA hysteresis band (asymmetric entry/exit to filter whipsaws) `[trading_systems_methods, p.383]`; and trend strength via ADX `[trading_systems_methods, p.387]`.

ADX caveat: the cache stores close-only equity curves (no intraday high/low), so ADX is a DEGRADED close-only proxy (true range ~ |dclose|). Any ADX-driven read is weaker than the other three families and must not be over-interpreted.

## Executive Conclusion

Phase 3A evaluated `324` rows: SPY/QQQ x 3 branch-specific bases x 9 filters (incl. `none`) x lags `0..5`. Top score row: `SPY` base `spy_top` filter `none` L`2.00` lag `3` with after-tax CAGR 15.44%, MDD -39.28%, Calmar 0.393, terminal 12.28x vs underlying. The overall top row uses the `none` control. Does any non-`none` filter beat `none` on the same top base (by score)? QQQ: no, SPY: no. Practical-pass rows (`MDD >= -50%` and after-tax underlying outperformance): `242`. Preferred drawdown rows (`MDD >= -40%`): `55`. QQQ practical-pass rows: `120`.

Practical read: the `none` control is not beaten on every branch, so added filter complexity is not yet justified `[trading_systems_methods, p.939]`.

Structurally redundant filters (identical to `none` on every base+lag): hyst band5%, hyst band8%. ANDing these onto the SMA200 gate cannot extend risk-on; their only distinct behaviour (e.g. a hysteresis band holding through a dip below the SMA) lives on days the SMA gate already blocks, so the AND erases it. Testing those mechanisms properly requires REPLACING the SMA gate, not ANDing onto it - deferred to a future phase.

## Source And Rules

| Item | Value |
|---|---|
| Data | `data/testfolio/cache/history.parquet` (close-only equity curves) |
| Base signal | `underlying.shift(1) > SMA200.shift(1)` AND realized-vol gate |
| Confirmation filter | at most one of {clenow, roc, hysteresis, adx}, ANDed; `none` = control |
| Target leverage | adjacent ETF ladder, no negative cash |
| Settlement lag | `n = 0..5` daily bars in `CASHX` before entering the new sleeve |
| Tax | annual 15% DARF on realized net gains plus final liquidation |
| ADX | close-only proxy (no intraday high/low available) |


## Test Windows

| Branch | Start | End | Years | Underlying CAGR | Underlying MDD |
|---|---|---|---|---|---|
| QQQ | 1986-01-03 | 2026-05-21 | 40.4 | 14.36% | -82.97% |
| SPY | 1968-04-02 | 2026-05-21 | 58.1 | 10.56% | -55.14% |

## Plots

| Plot | File |
|---|---|
| SPY best score | [plots/phase03_spy_spy_top_none_lag3.png](plots/phase03_spy_spy_top_none_lag3.png) |
| QQQ best score | [plots/phase03_qqq_qqq_top_hyst_band8pct_lag0.png](plots/phase03_qqq_qqq_top_hyst_band8pct_lag0.png) |
| Frontier by filter family | [plots/phase03_frontier.png](plots/phase03_frontier.png) |
| Filter sensitivity (top base) | [plots/phase03_filter_sensitivity.png](plots/phase03_filter_sensitivity.png) |

## Top Ranked Rows

| Branch | Base | Filter | L | Lag | Tier | CAGR | MDD | Calmar | Spread vs U | Terminal/U | Hit 10y | Pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | spy_top | none | 2.00 | 3 | preferred | 15.44% | -39.28% | 0.393 | +4.88pp | 12.28x | 98.0% | yes |
| SPY | spy_top | hyst band5% | 2.00 | 3 | preferred | 15.44% | -39.28% | 0.393 | +4.88pp | 12.28x | 98.0% | yes |
| SPY | spy_top | hyst band8% | 2.00 | 3 | preferred | 15.44% | -39.28% | 0.393 | +4.88pp | 12.28x | 98.0% | yes |
| SPY | spy_alt_off | none | 2.00 | 3 | tolerable | 15.72% | -40.19% | 0.391 | +5.16pp | 14.14x | 98.5% | yes |
| SPY | spy_alt_off | hyst band5% | 2.00 | 3 | tolerable | 15.72% | -40.19% | 0.391 | +5.16pp | 14.14x | 98.5% | yes |
| SPY | spy_alt_off | hyst band8% | 2.00 | 3 | tolerable | 15.72% | -40.19% | 0.391 | +5.16pp | 14.14x | 98.5% | yes |
| SPY | spy_top | none | 2.00 | 5 | tolerable | 14.85% | -41.02% | 0.362 | +4.29pp | 9.10x | 93.1% | yes |
| SPY | spy_top | hyst band5% | 2.00 | 5 | tolerable | 14.85% | -41.02% | 0.362 | +4.29pp | 9.10x | 93.1% | yes |
| SPY | spy_top | hyst band8% | 2.00 | 5 | tolerable | 14.85% | -41.02% | 0.362 | +4.29pp | 9.10x | 93.1% | yes |
| SPY | spy_top | none | 2.00 | 4 | tolerable | 15.28% | -40.43% | 0.378 | +4.72pp | 11.31x | 96.5% | yes |
| SPY | spy_top | hyst band5% | 2.00 | 4 | tolerable | 15.28% | -40.43% | 0.378 | +4.72pp | 11.31x | 96.5% | yes |
| SPY | spy_top | hyst band8% | 2.00 | 4 | tolerable | 15.28% | -40.43% | 0.378 | +4.72pp | 11.31x | 96.5% | yes |
| SPY | spy_lower_lev | none | 1.75 | 3 | preferred | 14.60% | -37.38% | 0.391 | +4.04pp | 8.05x | 93.2% | yes |
| SPY | spy_lower_lev | hyst band5% | 1.75 | 3 | preferred | 14.60% | -37.38% | 0.391 | +4.04pp | 8.05x | 93.2% | yes |
| SPY | spy_lower_lev | hyst band8% | 1.75 | 3 | preferred | 14.60% | -37.38% | 0.391 | +4.04pp | 8.05x | 93.2% | yes |
| SPY | spy_alt_off | none | 2.00 | 5 | tolerable | 15.15% | -41.34% | 0.367 | +4.59pp | 10.64x | 94.5% | yes |
| SPY | spy_alt_off | hyst band5% | 2.00 | 5 | tolerable | 15.15% | -41.34% | 0.367 | +4.59pp | 10.64x | 94.5% | yes |
| SPY | spy_alt_off | hyst band8% | 2.00 | 5 | tolerable | 15.15% | -41.34% | 0.367 | +4.59pp | 10.64x | 94.5% | yes |
| SPY | spy_lower_lev | none | 1.75 | 4 | preferred | 14.47% | -37.21% | 0.389 | +3.91pp | 7.51x | 91.2% | yes |
| SPY | spy_lower_lev | hyst band5% | 1.75 | 4 | preferred | 14.47% | -37.21% | 0.389 | +3.91pp | 7.51x | 91.2% | yes |
| SPY | spy_lower_lev | hyst band8% | 1.75 | 4 | preferred | 14.47% | -37.21% | 0.389 | +3.91pp | 7.51x | 91.2% | yes |
| SPY | spy_lower_lev | none | 1.75 | 5 | preferred | 14.05% | -38.32% | 0.367 | +3.49pp | 6.08x | 84.8% | yes |
| SPY | spy_lower_lev | hyst band5% | 1.75 | 5 | preferred | 14.05% | -38.32% | 0.367 | +3.49pp | 6.08x | 84.8% | yes |
| SPY | spy_lower_lev | hyst band8% | 1.75 | 5 | preferred | 14.05% | -38.32% | 0.367 | +3.49pp | 6.08x | 84.8% | yes |
| SPY | spy_lower_lev | clenow>0 w120 | 1.75 | 0 | tolerable | 13.79% | -41.12% | 0.335 | +3.23pp | 5.32x | 88.5% | yes |
| SPY | spy_alt_off | none | 2.00 | 4 | tolerable | 15.65% | -40.69% | 0.385 | +5.09pp | 13.67x | 97.6% | yes |
| SPY | spy_alt_off | hyst band5% | 2.00 | 4 | tolerable | 15.65% | -40.69% | 0.385 | +5.09pp | 13.67x | 97.6% | yes |
| SPY | spy_alt_off | hyst band8% | 2.00 | 4 | tolerable | 15.65% | -40.69% | 0.385 | +5.09pp | 13.67x | 97.6% | yes |
| QQQ | qqq_top | none | 1.75 | 0 | tolerable | 19.46% | -42.58% | 0.457 | +5.10pp | 5.82x | 66.8% | yes |
| QQQ | qqq_top | hyst band5% | 1.75 | 0 | tolerable | 19.46% | -42.58% | 0.457 | +5.10pp | 5.82x | 66.8% | yes |

## Best Row By Branch

| Branch | Base | Filter | L | Lag | Tier | CAGR | MDD | Calmar | Terminal/U |
|---|---|---|---|---|---|---|---|---|---|
| QQQ | qqq_top | hyst band8% | 1.75 | 0 | tolerable | 19.46% | -42.58% | 0.457 | 5.82x |
| SPY | spy_top | none | 2.00 | 3 | preferred | 15.44% | -39.28% | 0.393 | 12.28x |

## Best Row By Filter

| Branch | Filter | Family | Base | Lag | Tier | CAGR | MDD | Calmar | Score |
|---|---|---|---|---|---|---|---|---|---|
| QQQ | hyst band8% | hysteresis | qqq_top | 0 | tolerable | 19.46% | -42.58% | 0.457 | 3.830 |
| QQQ | hyst band5% | hysteresis | qqq_top | 0 | tolerable | 19.46% | -42.58% | 0.457 | 3.830 |
| QQQ | none | none | qqq_top | 0 | tolerable | 19.46% | -42.58% | 0.457 | 3.830 |
| QQQ | roc252>0 | roc | qqq_top | 0 | tolerable | 18.87% | -42.56% | 0.443 | 3.656 |
| QQQ | clenow>0 w90 | clenow | qqq_top | 0 | tolerable | 17.88% | -42.56% | 0.420 | 3.520 |
| QQQ | roc126>0 | roc | qqq_top | 0 | tolerable | 19.19% | -45.01% | 0.426 | 3.518 |
| QQQ | clenow>0 w120 | clenow | qqq_lower_lev | 4 | preferred | 17.07% | -39.88% | 0.428 | 3.488 |
| QQQ | adx>20 | adx | qqq_alt_vol | 0 | preferred | 13.03% | -34.14% | 0.382 | 2.732 |
| QQQ | adx>25 | adx | qqq_lower_lev | 0 | tolerable | 9.48% | -46.79% | 0.203 | 1.566 |
| SPY | none | none | spy_top | 3 | preferred | 15.44% | -39.28% | 0.393 | 3.951 |
| SPY | hyst band8% | hysteresis | spy_top | 3 | preferred | 15.44% | -39.28% | 0.393 | 3.951 |
| SPY | hyst band5% | hysteresis | spy_top | 3 | preferred | 15.44% | -39.28% | 0.393 | 3.951 |
| SPY | clenow>0 w120 | clenow | spy_lower_lev | 0 | tolerable | 13.79% | -41.12% | 0.335 | 3.845 |
| SPY | roc252>0 | roc | spy_top | 3 | preferred | 13.86% | -39.28% | 0.353 | 3.663 |
| SPY | roc126>0 | roc | spy_alt_off | 0 | preferred | 12.80% | -39.31% | 0.326 | 3.489 |
| SPY | clenow>0 w90 | clenow | spy_lower_lev | 1 | tolerable | 13.21% | -44.73% | 0.295 | 2.987 |
| SPY | adx>20 | adx | spy_lower_lev | 5 | tolerable | 10.66% | -42.69% | 0.250 | 2.385 |
| SPY | adx>25 | adx | spy_lower_lev | 4 | tolerable | 9.63% | -43.10% | 0.223 | 2.134 |

## Filter vs `none` (top base per branch, best lag)

| Branch | Base | Filter | Lag | CAGR | dCAGR vs none | MDD | dMDD vs none | dScore vs none |
|---|---|---|---|---|---|---|---|---|
| QQQ | qqq_top | none | 0 | 19.46% | +0.00pp | -42.58% | +0.00pp | 0.000 |
| QQQ | qqq_top | clenow>0 w90 | 0 | 17.88% | -1.57pp | -42.56% | +0.01pp | -0.310 |
| QQQ | qqq_top | clenow>0 w120 | 4 | 18.35% | -1.10pp | -45.03% | -2.46pp | -0.548 |
| QQQ | qqq_top | roc126>0 | 0 | 19.19% | -0.27pp | -45.01% | -2.43pp | -0.312 |
| QQQ | qqq_top | roc252>0 | 0 | 18.87% | -0.59pp | -42.56% | +0.01pp | -0.174 |
| QQQ | qqq_top | hyst band5% | 0 | 19.46% | +0.00pp | -42.58% | +0.00pp | 0.000 |
| QQQ | qqq_top | hyst band8% | 0 | 19.46% | +0.00pp | -42.58% | +0.00pp | 0.000 |
| QQQ | qqq_top | adx>20 | 0 | 13.20% | -6.25pp | -41.29% | +1.28pp | -1.284 |
| QQQ | qqq_top | adx>25 | 0 | 9.83% | -9.62pp | -49.99% | -7.41pp | -2.495 |
| SPY | spy_top | none | 3 | 15.44% | +0.00pp | -39.28% | +0.00pp | 0.000 |
| SPY | spy_top | clenow>0 w90 | 5 | 13.13% | -2.31pp | -48.39% | -9.10pp | -1.361 |
| SPY | spy_top | clenow>0 w120 | 0 | 14.40% | -1.04pp | -44.35% | -5.06pp | -0.306 |
| SPY | spy_top | roc126>0 | 0 | 12.58% | -2.86pp | -40.55% | -1.26pp | -0.556 |
| SPY | spy_top | roc252>0 | 3 | 13.86% | -1.58pp | -39.28% | -0.00pp | -0.288 |
| SPY | spy_top | hyst band5% | 3 | 15.44% | +0.00pp | -39.28% | +0.00pp | 0.000 |
| SPY | spy_top | hyst band8% | 3 | 15.44% | +0.00pp | -39.28% | +0.00pp | 0.000 |
| SPY | spy_top | adx>20 | 0 | 10.73% | -4.71pp | -45.69% | -6.40pp | -1.652 |
| SPY | spy_top | adx>25 | 0 | 9.79% | -5.65pp | -47.65% | -8.37pp | -1.885 |

## Rolling Hit Rates (top row per branch)

| Branch | Base | Filter | Hit 3y | Hit 5y | Hit 10y | Hit 15y | Hit 20y |
|---|---|---|---|---|---|---|---|
| QQQ | qqq_top | hyst band8% | 59.5% | 61.6% | 66.8% | 80.0% | 90.5% |
| SPY | spy_top | none | 71.3% | 82.8% | 98.0% | 99.8% | 100.0% |

## Operational / Tax (top row per branch)

| Branch | Base | Filter | Turnover/yr | Trades | Risk-on days | Tax paid % init |
|---|---|---|---|---|---|---|
| QQQ | qqq_top | hyst band8% | 3.00 | 121 | 71.2% | 20650.0% |
| SPY | spy_top | none | 5.58 | 370 | 71.3% | 64883.5% |

## Phase Verdict

| Question | Verdict |
|---|---|
| Did any non-`none` filter beat the control on both branches? | No (QQQ: no, SPY: no). |
| Is the overall top row a filter or the control? | Control (`none`). |
| Did any row meet the <=50% MDD practical target and beat underlying? | Yes. |
| Did any row meet preferred <=40% MDD? | Yes. |
| Is this deployment-ready? | No. This is a diagnostic confirmation-vote phase only. No deploy, no paper-trade label, no mandate change. |

Next step: do not add filter complexity as an AND-gate; if a trend-hold mechanism is still wanted, test hysteresis as a REPLACEMENT for the SMA gate, otherwise revisit risk-off / bear-sleeve mechanisms or close the family pending the validation gates `[advances_fin_ml, p.208-211]`.
