# Iter 049 - No-BTC B4 restricted overlay with DBMF fallback

**Date:** 2026-05-03
**Purpose:** remove the Bitcoin 2010 start-date constraint and test restricted overlays on B4.
**RSST proxy:** `SPYSIM + 70% DBMFSIM?FB=KMLMSIM + 30% KMLMSIM - CASHX?E=-2`.

## Ranking By Sharpe

| # | strategy | window | CAGR | MDD | Sharpe | end value |
|---:|---|---|---:|---:|---:|---:|
| 1 | overlay_200d_12mdd_10pp | 1987-12-31 -> 2026-05-01 (38.33y) | 13.05% | -26.65% | 0.933 | $1,103,235 |
| 2 | overlay_200d_12mdd_5pp | 1987-12-31 -> 2026-05-01 (38.33y) | 12.79% | -28.07% | 0.916 | $1,007,439 |
| 3 | overlay_10m_12mdd_5pp | 1987-12-31 -> 2026-05-01 (38.33y) | 12.79% | -28.07% | 0.916 | $1,007,439 |
| 4 | overlay_200d_24mdd_5pp | 1987-12-31 -> 2026-05-01 (38.33y) | 12.72% | -28.07% | 0.912 | $984,649 |
| 5 | static_b4 | 1987-12-31 -> 2026-05-01 (38.33y) | 12.51% | -29.81% | 0.894 | $916,955 |

## Verdict

Static B4 baseline: 12.51% CAGR / -29.81% MDD / 0.894 Sharpe.
At least one overlay strictly improves CAGR without worse MDD and without lower Sharpe.

## Regime Counts

| strategy | neutral | risk_on | defensive |
|---|---:|---:|---:|
| static_b4 | 462 | 0 | 0 |
| overlay_200d_12mdd_5pp | 53 | 304 | 105 |
| overlay_200d_24mdd_5pp | 70 | 280 | 112 |
| overlay_10m_12mdd_5pp | 53 | 304 | 105 |
| overlay_200d_12mdd_10pp | 53 | 304 | 105 |

## Caveats

- This fallback proxy extends the test, but it is no longer the same as pure live DBMF history before 2000.
- Treat overlay improvements as hypothesis evidence, not deploy approval, until gate-style OOS/PBO checks are added.
