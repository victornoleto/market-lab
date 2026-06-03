# B4 + evo02 70/30 — Implementation Guide

Status: selected research portfolio for continued study after iter 058.

This document describes how to implement and monitor the portfolio:

```text
70% B4 core
30% evo02 QQQ rolling-repair satellite
```

The strategy is research-only until the evo02 sleeve clears hard validation. PBO/DSR/OOS/WF/bootstrap remain required before any deployment claim `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Allocation

Target weights:

| Sleeve | Weight | Role |
|---|---:|---|
| B4 core | 70% | Defensive capital-efficient long-term core |
| evo02 satellite | 30% | Aggressive alpha/return sleeve |

B4 core definition:

| Asset | Weight inside B4 | Total portfolio weight |
|---|---:|---:|
| NTSX | 25% | 17.50% |
| GDE | 25% | 17.50% |
| RSST | 25% | 17.50% |
| ZROZ | 25% | 17.50% |

Total implemented portfolio:

| Component | Portfolio weight |
|---|---:|
| NTSX | 17.50% |
| GDE | 17.50% |
| RSST | 17.50% |
| ZROZ | 17.50% |
| evo02 sleeve | 30.00% |

B4 uses capital-efficient stacking for diversified equity, bonds, gold and managed-futures exposure `[risk_parity, ch.5, p.10]`. The evo02 sleeve is an active LETF repair sleeve discovered in the repair GA suite; it should be treated as an alpha satellite, not as a passive core.

## Contributions

Base implementation assumptions from iter 058:

| Parameter | Value |
|---|---:|
| Initial capital | USD 10,000 |
| Monthly contribution | USD 1,000 |
| Contribution timing | First trading day of each month |
| Portfolio rebalance | Monthly |

Operational rule:

1. At initial funding, allocate capital to the target weights.
2. On the first trading day of each month, add the new contribution.
3. Rebalance the whole portfolio back to the target weights after the contribution.
4. Do not rebalance intra-month unless a future risk policy explicitly requires it.

## evo02 Sleeve

The evo02 sleeve is:

```text
QQQ_s50_225_vw42_vt0.25_ar30_k3_T20D60_w1.00_lrs1.00_g0.50_rv60_0.70
```

Decoded parameters:

| Parameter | Value | Meaning |
|---|---:|---|
| Signal asset | QQQ | Use QQQ price/returns for regime signal |
| SMA long | 225 | Long trend gate |
| SMA short | 50 | Short trend gate |
| Vol window | 42 | Realized-volatility lookback |
| Vol threshold | 0.25 | Risk-on if realized vol is below threshold |
| AR window | 30 | AR(1) trend/persistence lookback |
| Entry K | 3 | Vote-of-4 entry threshold |
| T crash | 20 | Crash/off persistence trigger |
| D arm | 60 | Post-crash rearm window |
| TQQQ weight | 1.00 | During rearm, turbo leg uses TQQQ rather than QLD |
| LRS factor | 1.00 | No extra LRS multiplier in evo02 |
| Gamma | 0.50 | Mixes ZROZ/CASH in off-leg override |
| Rate-vol window | 60 | Bond rate-volatility gate lookback |
| Rate-vol threshold | 0.70 | Threshold for off-leg CASH override |

Signal mechanics:

1. Build four QQQ-derived gates: `SMA225`, `SMA50`, realized volatility below `25%`, and positive `AR(1)` over 30 days.
2. Risk-on requires at least `3` of the 4 gates to be active.
3. A post-crash rearm gate uses `T20D60`: after sufficient off persistence, re-enter a turbo/rearm window for 60 trading days.
4. During rearm, the on-leg uses TQQQ exposure.
5. The defensive leg uses ZROZ, with a CASH override when the bond rate-volatility regime is adverse.

The trend and rearm logic follows the broad leveraged-equity timing idea from leverage-for-the-long-run research `[leverage_for_the_long_run, p.5-7]`, while trend persistence and momentum-style filtering are consistent with trend-following practice `[stocks_on_the_move, p.21-30]`. The exact parameter set is GA-discovered and therefore must remain validation-gated `[advances_fin_ml, p.208-211]`.

## Backtest Result

Source: `studies/long_term_portfolio/iterations/058-2026-05-13-b4-evo02-satellite/`.

Main comparison, 1988-01-05 to 2026-04-17, monthly rebalance:

| Strategy | CAGR | MDD | Sharpe | Sortino | Final value with contributions | XIRR |
|---|---:|---:|---:|---:|---:|---:|
| 70% B4 + 30% evo02 | 20.01% | -21.60% | 1.2038 | 1.7170 | USD 75.40M | 19.74% |
| 75% B4 + 25% evo02 | 19.15% | -22.58% | 1.1998 | 1.7253 | USD 58.71M | 18.85% |
| 100% B4 | 14.62% | -28.38% | 1.0234 | 1.4597 | USD 15.92M | 14.17% |

Why 70/30 was selected over 75/25:

| Criterion | Winner |
|---|---|
| CAGR | 70/30 |
| MDD | 70/30 |
| Sharpe | 70/30 |
| Final value with contributions | 70/30 |
| XIRR | 70/30 |
| Sortino | 75/25, but only marginally |

The Sortino difference is small, while the return and drawdown improvement favored 70/30. Therefore 70/30 is the selected research allocation.

## Monthly Workflow

Each month:

1. Pull latest adjusted prices for QQQ, QLD, TQQQ, ZROZ and CASH/off-leg proxy.
2. Compute evo02 signals using data available at prior close.
3. Determine current evo02 target holdings for the satellite sleeve.
4. Add monthly contribution.
5. Rebalance total portfolio to 70% B4 and 30% evo02.
6. Within the 70% B4 sleeve, rebalance to equal 25/25/25/25 across NTSX/GDE/RSST/ZROZ.
7. Within the evo02 sleeve, hold the current signal-selected on/off exposure.
8. Log final weights, signals, trades and account value.

Do not manually override signals because of narrative macro views. If manual override is ever required, document it as a separate mandate override.

## Monitoring

Monthly metrics to record:

| Metric | Purpose |
|---|---|
| Total account value | Tracks contribution-aware wealth path |
| Pure strategy return | Separates strategy edge from savings rate |
| B4 sleeve return | Confirms core behavior |
| evo02 sleeve return | Monitors alpha satellite behavior |
| Drawdown from peak | Behavioral risk control |
| Rolling 3y/5y CAGR | Detects long stagnation |
| evo02 signal state | Auditability |
| Turnover/trades | Implementation friction |

Review triggers:

| Trigger | Action |
|---|---|
| Portfolio drawdown worse than backtest by >5pp | Review implementation and assumptions |
| evo02 underperforms B4 for 5 rolling years | Re-run validation and consider reducing satellite to 20-25% |
| Signal implementation mismatch | Freeze new trades until reconciled |
| Major ETF structural change/liquidity issue | Re-map instrument or suspend affected sleeve |
| Future hard validation fails badly | Reduce or retire evo02 sleeve |

## Implementation Risks

Main risks:

| Risk | Comment |
|---|---|
| GA overfit | evo02 was selected by search, not yet hard-validated |
| LETF path dependency | TQQQ/QLD exposure can decay in volatile sideways markets `[trading_evolved, p.172-176]` |
| Tax/turnover | Backtest is not a full live tax simulation |
| Data drift | Live adjusted prices may differ from testfolio synths |
| Behavioral risk | 30% active sleeve can still feel large during underperformance |
| Product risk | NTSX/GDE/RSST and LETFs depend on ETF structure continuing as expected |

## Research Next Steps

Before treating this as more than a research portfolio:

1. Validate evo02 with OOS/FWD/WF/bootstrap/PBO/DSR using cumulative trial accounting.
2. Re-run the combined 70/30 portfolio with realistic ETF expenses, spreads and tax assumptions.
3. Produce a live-ready monthly signal sheet.
4. Compare broker-implementable tickers and tax treatment.
5. Add a simple reconciliation test that rebuilds the evo02 signal from raw prices.

## Canonical Files

| File | Purpose |
|---|---|
| `iterations/058-2026-05-13-b4-evo02-satellite/run.py` | Backtest implementation |
| `iterations/058-2026-05-13-b4-evo02-satellite/REPORT.md` | Iter 058 report |
| `iterations/058-2026-05-13-b4-evo02-satellite/tables/performance.csv` | Headline performance |
| `iterations/058-2026-05-13-b4-evo02-satellite/tables/rolling_windows.csv` | Rolling-window results |
| `iterations/058-2026-05-13-b4-evo02-satellite/plots/` | Equity, drawdown and rolling plots |
