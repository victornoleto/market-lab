# Iter 048 - Restricted regime overlay on B4 + 5% BTC

**Date:** 2026-05-03
**Purpose:** test whether a simple walk-forward/regime overlay improves the selected live candidate without free weight optimization.
**Method:** monthly rebalance, saved/fetched testfol.io single-sleeve curves, SPY trend/drawdown state, pre-defined +/-5pp or +/-10pp tilts.

## Ranking By Sharpe

| # | strategy | window | CAGR | MDD | Sharpe | end value |
|---:|---|---|---:|---:|---:|---:|
| 1 | overlay_200d_12mdd_10pp | 2010-07-19 -> 2026-05-01 (15.78y) | 22.09% | -27.31% | 1.408 | $233,433 |
| 2 | overlay_200d_12mdd_5pp | 2010-07-19 -> 2026-05-01 (15.78y) | 21.81% | -27.40% | 1.402 | $225,057 |
| 3 | overlay_10m_12mdd_5pp | 2010-07-19 -> 2026-05-01 (15.78y) | 21.81% | -27.40% | 1.402 | $225,057 |
| 4 | overlay_200d_24mdd_5pp | 2010-07-19 -> 2026-05-01 (15.78y) | 21.80% | -27.40% | 1.401 | $224,774 |
| 5 | static_b4_btc5 | 2010-07-19 -> 2026-05-01 (15.78y) | 21.53% | -28.16% | 1.384 | $217,169 |

## Verdict

Static B4+5% BTC baseline: 21.53% CAGR / -28.16% MDD / 1.384 Sharpe.
At least one overlay strictly improves CAGR without worse MDD and without lower Sharpe.

## Regime Counts

| strategy | neutral | risk_on | defensive |
|---|---:|---:|---:|
| static_b4_btc5 | 191 | 0 | 0 |
| overlay_200d_12mdd_5pp | 29 | 130 | 32 |
| overlay_200d_24mdd_5pp | 43 | 122 | 26 |
| overlay_10m_12mdd_5pp | 29 | 130 | 32 |
| overlay_200d_12mdd_10pp | 29 | 130 | 32 |

## Interpretation

This is an overlay test, not a new live recommendation unless it beats the static allocation on the full trade-off. Prior iter 043 already showed unrestricted walk-forward optimization overfits weights; this iter only tests small, pre-defined regime tilts.
