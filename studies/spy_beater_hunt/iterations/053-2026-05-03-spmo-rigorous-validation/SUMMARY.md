# Iter 053 — SPMO rigorous validation

**Date:** 2026-05-03
**Candidate:** 25% NTSX / 25% GDE / 25% RSST / 15% ZROZ / 5% BTC / 5% SPMO.
**Verdict:** research-promising, not gate-equivalent.

## Live Candidate

Window: 2022-03-17 -> 2026-05-01 (4.12y)

| row | CAGR | MDD | Sharpe |
|---|---:|---:|---:|
| B4+BTC5+5% SPMO | 14.23% | -25.15% | 0.872 |
| B4+BTC5 baseline | 12.28% | -25.98% | 0.782 |

Delta versus baseline:

- CAGR: +1.95pp
- MDD: 0.84pp improvement
- Sharpe: +0.090

## Bootstrap Excess Return

Block bootstrap on daily excess returns versus B4+BTC5 baseline.

| metric | value |
|---|---:|
| mean_annual_excess_pct | 1.6555% |
| ci_5_pct | 0.6187% |
| ci_1_pct | 0.1771% |
| ci_0p1_pct | -0.2624% |
| prob_excess_gt_0 | 0.9952 |

## OOS Split

| split | candidate | baseline | delta CAGR | delta Sharpe | MDD improvement |
|---|---:|---:|---:|---:|---:|
| train70 | 10.19% / -25.15% / 0.689 | 8.15% / -25.98% / 0.576 | 2.04pp | 0.113 | 0.84pp |
| oos30 | 23.47% / -16.36% / 1.205 | 21.73% / -15.42% / 1.164 | 1.74pp | 0.041 | -0.94pp |

## Rolling Windows

| window | n | CAGR win-rate | MDD no-worse rate | both rate |
|---:|---:|---:|---:|---:|
| 1y | 783 | 100.00% | 44.44% | 44.44% |
| 2y | 531 | 100.00% | 49.15% | 49.15% |
| 3y | 279 | 100.00% | 37.99% | 37.99% |

## Neighborhood Rank

| rank | strategy | CAGR | MDD | Sharpe |
|---:|---|---:|---:|---:|
| 1 | B4_btc5_spmo5_from_zroz | 14.23% | -25.15% | 0.872 |
| 2 | B4_btc5_mtum5_from_zroz | 13.87% | -25.41% | 0.851 |
| 3 | B4_btc5_vbr5_from_zroz | 13.54% | -25.25% | 0.836 |
| 4 | B4_btc5_spmo2p5_from_zroz | 13.26% | -25.57% | 0.828 |
| 5 | B4_btc5 | 12.28% | -25.98% | 0.782 |

## Long Proxy Without BTC

Uses local testfol.io synthetic cache with MTUMSIM as a longer momentum proxy. This does not prove SPMO and excludes BTC, but it tests whether momentum survives outside the short live SPMO window.

| strategy | window | CAGR | MDD | Sharpe |
|---|---|---:|---:|---:|
| B4_rsst7030_baseline | 2000-01-03 -> 2026-05-01 (26.32y) | 11.00% | -29.60% | 0.805 |
| B4_scv10_from_zroz | 2000-01-03 -> 2026-05-01 (26.32y) | 11.36% | -37.20% | 0.771 |
| B4_scv10_from_ntsx | 2000-01-03 -> 2026-05-01 (26.32y) | 11.23% | -31.06% | 0.814 |
| B4_mtum10_from_zroz | 2000-01-03 -> 2026-05-01 (26.32y) | 11.21% | -37.09% | 0.763 |

## Decision

The candidate improves the observed live B4+BTC5 window and ranks best in the small fixed neighborhood. However, it is not a formal winner because SPMO constrains the actual sleeve test to 2022+ and the full 7-gate battery cannot be honestly completed. Keep as a pre-registered research candidate, not as an automatic replacement for the current B4+BTC5 live candidate.
