# Phase 3A-2 - Alternative Regime Signals (Replacement)

Status: research-only regime-signal sweep over the Phase 2 geometry. This report does not authorize deployment, paper trading or a mandate change.

Method references: each row REPLACES the Gayed SMA200 trend gate with an alternative regime signal `G`, keeping the realized-vol throttle and exposure geometry of Phase 2 (`signal = G & vol_gate`) `[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.4-7]`. This follows directly from the Phase 3A finding that ANDing a trend-hold filter onto `price > SMA200` can only further restrict risk-on; to test a trend mechanism it must replace the SMA gate, not AND onto it `[trading_systems_methods, p.939]`, `[advances_fin_ml, p.208-211]`. Lookback is held FIXED at 200 across all forms to isolate signal *form* from *window* (the window question is Phase 3C's). Regime forms: SMA200 control `[leverage_for_the_long_run, p.13]`; EMA200 `[systematic_trading, p.283]`; SMA hysteresis band as a state machine `[trading_systems_methods, p.383]`; ROC200 momentum `[stocks_on_the_move, p.58, p.60]`; Clenow annualized slope x R^2 `[stocks_on_the_move, p.70-77, p.98]`.

SMA200 control sanity vs Phase 2: matched `36` base+lag rows, max abs diff in after-tax CAGR/MDD `8.33e-17` (expected ~0, reproduces `lrs/results/phase02_target_leverage_vol.csv`).

## Executive Conclusion

Phase 3A-2 evaluated `216` rows: SPY/QQQ x 3 branch-specific bases x 6 regime forms x lags `0..5`. Top score row: `SPY` base `spy_top` form `SMA200` L`2.00` lag `3` with after-tax CAGR 15.44%, MDD -39.28%, Calmar 0.393, terminal 12.28x vs underlying. The overall top row uses the SMA200 control. Does any non-control form beat SMA200 on the same top base (by score)? QQQ: no, SPY: no. Practical-pass rows (`MDD >= -50%` and after-tax underlying outperformance): `64`. Preferred drawdown rows (`MDD >= -40%`): `7`. QQQ practical-pass rows: `36`.

Practical read: the SMA200 control is not beaten on every branch, so an alternative regime form is not yet justified `[trading_systems_methods, p.939]`.

## Source And Rules

| Item | Value |
|---|---|
| Data | `data/testfolio/cache/history.parquet` (close-only equity curves) |
| Signal | `G(underlying) & realized-vol gate`, G REPLACES the SMA trend gate |
| Regime form G | one of {SMA200 control, EMA200, hyst200 band5%/8%, ROC200>0, Clenow200>0} |
| Lookback | fixed at 200 for every form (window study deferred to Phase 3C) |
| Target leverage | adjacent ETF ladder, no negative cash |
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
| SPY best score | [plots/phase03b_spy_spy_top_sma200_lag3.png](plots/phase03b_spy_spy_top_sma200_lag3.png) |
| QQQ best score | [plots/phase03b_qqq_qqq_top_sma200_lag0.png](plots/phase03b_qqq_qqq_top_sma200_lag0.png) |
| Frontier by regime family | [plots/phase03b_frontier.png](plots/phase03b_frontier.png) |
| Regime-form sensitivity (top base) | [plots/phase03b_form_sensitivity.png](plots/phase03b_form_sensitivity.png) |

## Top Ranked Rows

| Branch | Base | Form | L | Lag | Tier | CAGR | MDD | Calmar | Spread vs U | Terminal/U | Hit 10y | Pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | spy_top | SMA200 | 2.00 | 3 | preferred | 15.44% | -39.28% | 0.393 | +4.88pp | 12.28x | 98.0% | yes |
| SPY | spy_alt_off | SMA200 | 2.00 | 3 | tolerable | 15.72% | -40.19% | 0.391 | +5.16pp | 14.14x | 98.5% | yes |
| SPY | spy_top | SMA200 | 2.00 | 5 | tolerable | 14.85% | -41.02% | 0.362 | +4.29pp | 9.10x | 93.1% | yes |
| SPY | spy_top | SMA200 | 2.00 | 4 | tolerable | 15.28% | -40.43% | 0.378 | +4.72pp | 11.31x | 96.5% | yes |
| SPY | spy_lower_lev | SMA200 | 1.75 | 3 | preferred | 14.60% | -37.38% | 0.391 | +4.04pp | 8.05x | 93.2% | yes |
| SPY | spy_alt_off | SMA200 | 2.00 | 5 | tolerable | 15.15% | -41.34% | 0.367 | +4.59pp | 10.64x | 94.5% | yes |
| SPY | spy_lower_lev | SMA200 | 1.75 | 4 | preferred | 14.47% | -37.21% | 0.389 | +3.91pp | 7.51x | 91.2% | yes |
| SPY | spy_lower_lev | SMA200 | 1.75 | 5 | preferred | 14.05% | -38.32% | 0.367 | +3.49pp | 6.08x | 84.8% | yes |
| SPY | spy_alt_off | SMA200 | 2.00 | 4 | tolerable | 15.65% | -40.69% | 0.385 | +5.09pp | 13.67x | 97.6% | yes |
| QQQ | qqq_top | SMA200 | 1.75 | 0 | tolerable | 19.46% | -42.58% | 0.457 | +5.10pp | 5.82x | 66.8% | yes |
| QQQ | qqq_alt_vol | EMA200 | 1.75 | 0 | tolerable | 20.20% | -44.37% | 0.455 | +5.84pp | 7.48x | 78.6% | yes |
| SPY | spy_lower_lev | SMA200 | 1.75 | 2 | preferred | 14.45% | -37.60% | 0.384 | +3.89pp | 7.45x | 91.9% | yes |
| QQQ | qqq_lower_lev | SMA200 | 1.50 | 0 | tolerable | 17.96% | -40.63% | 0.442 | +3.60pp | 3.50x | 52.3% | yes |
| QQQ | qqq_top | EMA200 | 1.75 | 0 | tolerable | 20.82% | -46.15% | 0.451 | +6.46pp | 9.19x | 71.9% | yes |
| SPY | spy_alt_off | SMA200 | 2.00 | 2 | tolerable | 15.46% | -42.03% | 0.368 | +4.90pp | 12.40x | 97.7% | yes |
| SPY | spy_lower_lev | SMA200 | 1.75 | 1 | preferred | 13.79% | -38.39% | 0.359 | +3.23pp | 5.31x | 86.5% | yes |
| SPY | spy_top | SMA200 | 2.00 | 2 | tolerable | 15.23% | -43.12% | 0.353 | +4.67pp | 11.07x | 96.6% | yes |
| QQQ | qqq_lower_lev | EMA200 | 1.50 | 0 | tolerable | 19.22% | -43.55% | 0.441 | +4.86pp | 5.37x | 52.7% | yes |
| QQQ | qqq_alt_vol | SMA200 | 1.75 | 0 | tolerable | 18.32% | -42.80% | 0.428 | +3.96pp | 3.95x | 67.3% | yes |
| QQQ | qqq_top | EMA200 | 1.75 | 5 | tolerable | 19.62% | -43.16% | 0.455 | +5.27pp | 6.16x | 59.9% | yes |
| QQQ | qqq_lower_lev | EMA200 | 1.50 | 5 | tolerable | 18.19% | -40.19% | 0.453 | +3.83pp | 3.78x | 43.6% | yes |
| QQQ | qqq_top | SMA200 | 1.75 | 1 | tolerable | 19.53% | -42.70% | 0.457 | +5.17pp | 5.97x | 62.4% | yes |
| QQQ | qqq_lower_lev | SMA200 | 1.50 | 3 | preferred | 17.56% | -39.73% | 0.442 | +3.21pp | 3.05x | 55.0% | yes |
| SPY | spy_alt_off | SMA200 | 2.00 | 1 | tolerable | 14.63% | -42.81% | 0.342 | +4.07pp | 8.14x | 93.1% | yes |
| QQQ | qqq_lower_lev | SMA200 | 1.50 | 1 | tolerable | 18.07% | -40.52% | 0.446 | +3.72pp | 3.64x | 51.2% | yes |
| QQQ | qqq_top | SMA200 | 1.75 | 2 | tolerable | 19.04% | -42.49% | 0.448 | +4.68pp | 5.05x | 60.6% | yes |
| QQQ | qqq_top | SMA200 | 1.75 | 3 | tolerable | 18.95% | -42.62% | 0.445 | +4.59pp | 4.91x | 63.2% | yes |
| SPY | spy_top | SMA200 | 2.00 | 1 | tolerable | 14.45% | -44.07% | 0.328 | +3.89pp | 7.46x | 91.7% | yes |
| QQQ | qqq_lower_lev | SMA200 | 1.50 | 2 | tolerable | 17.63% | -40.54% | 0.435 | +3.27pp | 3.12x | 50.3% | yes |
| QQQ | qqq_top | SMA200 | 1.75 | 5 | tolerable | 19.32% | -45.36% | 0.426 | +4.96pp | 5.55x | 60.8% | yes |

## Best Row By Branch

| Branch | Base | Form | L | Lag | Tier | CAGR | MDD | Calmar | Terminal/U |
|---|---|---|---|---|---|---|---|---|---|
| QQQ | qqq_top | SMA200 | 1.75 | 0 | tolerable | 19.46% | -42.58% | 0.457 | 5.82x |
| SPY | spy_top | SMA200 | 2.00 | 3 | preferred | 15.44% | -39.28% | 0.393 | 12.28x |

## Best Row By Regime Form

| Branch | Form | Family | Base | Lag | Tier | CAGR | MDD | Calmar | Score |
|---|---|---|---|---|---|---|---|---|---|
| QQQ | SMA200 | control | qqq_top | 0 | tolerable | 19.46% | -42.58% | 0.457 | 3.830 |
| QQQ | EMA200 | ema | qqq_alt_vol | 0 | tolerable | 20.20% | -44.37% | 0.455 | 3.828 |
| QQQ | hyst200 band8% | hysteresis | qqq_lower_lev | 0 | warning | 17.70% | -50.62% | 0.350 | 3.157 |
| QQQ | hyst200 band5% | hysteresis | qqq_lower_lev | 0 | warning | 17.69% | -53.14% | 0.333 | 2.853 |
| QQQ | ROC200>0 | roc | qqq_lower_lev | 0 | warning | 16.11% | -53.28% | 0.302 | 2.273 |
| QQQ | Clenow200>0 | clenow | qqq_lower_lev | 0 | ruin | 15.85% | -66.77% | 0.237 | 1.365 |
| SPY | SMA200 | control | spy_top | 3 | preferred | 15.44% | -39.28% | 0.393 | 3.951 |
| SPY | EMA200 | ema | spy_lower_lev | 5 | tolerable | 13.35% | -44.95% | 0.297 | 3.028 |
| SPY | hyst200 band5% | hysteresis | spy_lower_lev | 0 | warning | 13.72% | -54.51% | 0.252 | 2.747 |
| SPY | ROC200>0 | roc | spy_lower_lev | 0 | warning | 12.72% | -54.51% | 0.233 | 2.484 |
| SPY | hyst200 band8% | hysteresis | spy_lower_lev | 0 | warning | 12.18% | -55.12% | 0.221 | 2.440 |
| SPY | Clenow200>0 | clenow | spy_lower_lev | 3 | warning | 12.28% | -54.46% | 0.225 | 2.367 |

## Form vs SMA200 control (top base per branch, best lag)

| Branch | Base | Form | Lag | CAGR | dCAGR vs SMA200 | MDD | dMDD vs SMA200 | dScore vs SMA200 |
|---|---|---|---|---|---|---|---|---|
| QQQ | qqq_top | SMA200 | 0 | 19.46% | +0.00pp | -42.58% | +0.00pp | 0.000 |
| QQQ | qqq_top | EMA200 | 0 | 20.82% | +1.36pp | -46.15% | -3.57pp | -0.123 |
| QQQ | qqq_top | hyst200 band5% | 0 | 18.95% | -0.50pp | -61.58% | -19.00pp | -1.424 |
| QQQ | qqq_top | hyst200 band8% | 5 | 20.45% | +0.99pp | -58.23% | -15.65pp | -1.005 |
| QQQ | qqq_top | ROC200>0 | 0 | 17.29% | -2.17pp | -59.57% | -16.99pp | -1.831 |
| QQQ | qqq_top | Clenow200>0 | 0 | 16.90% | -2.56pp | -73.75% | -31.17pp | -2.830 |
| SPY | spy_top | SMA200 | 3 | 15.44% | +0.00pp | -39.28% | +0.00pp | 0.000 |
| SPY | spy_top | EMA200 | 5 | 13.85% | -1.59pp | -48.15% | -8.86pp | -1.093 |
| SPY | spy_top | hyst200 band5% | 0 | 14.18% | -1.26pp | -58.87% | -19.59pp | -1.483 |
| SPY | spy_top | hyst200 band8% | 0 | 12.54% | -2.90pp | -58.87% | -19.59pp | -1.803 |
| SPY | spy_top | ROC200>0 | 0 | 13.38% | -2.06pp | -58.87% | -19.59pp | -1.731 |
| SPY | spy_top | Clenow200>0 | 3 | 12.82% | -2.62pp | -58.87% | -19.59pp | -1.854 |

## Rolling Hit Rates (top row per branch)

| Branch | Base | Form | Hit 3y | Hit 5y | Hit 10y | Hit 15y | Hit 20y |
|---|---|---|---|---|---|---|---|
| QQQ | qqq_top | SMA200 | 59.5% | 61.6% | 66.8% | 80.0% | 90.5% |
| SPY | spy_top | SMA200 | 71.3% | 82.8% | 98.0% | 99.8% | 100.0% |

## Operational / Tax (top row per branch)

| Branch | Base | Form | Turnover/yr | Trades | Risk-on days | Tax paid % init |
|---|---|---|---|---|---|---|
| QQQ | qqq_top | SMA200 | 3.00 | 121 | 71.2% | 20650.0% |
| SPY | spy_top | SMA200 | 5.58 | 370 | 71.3% | 64883.5% |

## Phase Verdict

| Question | Verdict |
|---|---|
| Did any non-control form beat SMA200 on both branches? | No (QQQ: no, SPY: no). |
| Is the overall top row the control or an alternative form? | Control (SMA200). |
| Did the SMA200 control reproduce Phase 2 (sanity)? | Yes (max diff `8.33e-17` over `36` rows). |
| Did any row meet the <=50% MDD practical target and beat underlying? | Yes. |
| Did any row meet preferred <=40% MDD? | Yes. |
| Is this deployment-ready? | No. This is a diagnostic regime-form phase only. No deploy, no paper-trade label, no mandate change. |

Next step: Phase 3C studies SMA + EMA (and hysteresis only if promoted here); the SMA200 level remains the control `[advances_fin_ml, p.208-211]`.
