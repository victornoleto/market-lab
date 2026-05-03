# Iter 046 — Factor tilts + NDX deleveraged variants

**Date:** 2026-05-03
**Source:** testfol.io API
**Window:** common 2000+ because corrected RSST uses DBMFSIM.
**Tax model:** no DARF applied; these are gross portfolio comparisons. Static portfolios assume lazy accumulation; tactical variants would need annual-realize tax treatment before deploy.

## Ranking By Sharpe

| # | kind | strategy | window | CAGR | MDD | Sharpe | Calmar |
|---:|---|---|---|---:|---:|---:|---:|
| 1 | static | B4_unstacked_mf7030 | 2000-01-03 -> 2026-05-01 (26.32y) | 9.91% | -20.91% | 0.749 | 0.474 |
| 2 | static | L1_cegb_reference | 2000-01-03 -> 2026-05-01 (26.32y) | 9.66% | -25.43% | 0.696 | 0.380 |
| 3 | static | B4_scv10_from_ntsx | 2000-01-03 -> 2026-05-01 (26.32y) | 11.23% | -31.06% | 0.681 | 0.361 |
| 4 | static | B4_rsst7030_baseline | 2000-01-03 -> 2026-05-01 (26.32y) | 11.00% | -29.60% | 0.671 | 0.372 |
| 5 | static | B4_scv10_from_zroz | 2000-01-03 -> 2026-05-01 (26.32y) | 11.36% | -37.20% | 0.648 | 0.306 |
| 6 | static | B4_mtum10_from_zroz | 2000-01-03 -> 2026-05-01 (26.32y) | 11.21% | -37.09% | 0.640 | 0.302 |
| 7 | static | B4_value_mix10_from_zroz | 2000-01-03 -> 2026-05-01 (26.32y) | 11.13% | -37.51% | 0.639 | 0.297 |
| 8 | static | B4_aggressive_scv15 | 2000-01-03 -> 2026-05-01 (26.32y) | 11.86% | -40.89% | 0.639 | 0.290 |
| 9 | static | B4_scv15_from_zroz | 2000-01-03 -> 2026-05-01 (26.32y) | 11.50% | -40.76% | 0.628 | 0.282 |
| 10 | tactical_local | NS3_q140kmlm30iei30_q50iei50 | 2000-01-03 -> 2026-04-17 (26.24y local) | 13.38% | -72.51% | 0.621 | 0.185 |
| 11 | tactical_local | NS2_q140iei60_q50iei50 | 2000-01-03 -> 2026-04-17 (26.24y local) | 12.73% | -74.09% | 0.600 | 0.172 |
| 12 | tactical_local | NS1_q140iei100_q50cash | 2000-01-03 -> 2026-04-17 (26.24y local) | 12.76% | -76.24% | 0.598 | 0.167 |
| 13 | static | SPY_1x | 2000-01-03 -> 2026-05-01 (26.32y) | 8.16% | -55.20% | 0.405 | 0.148 |

## Practical Bars

SPY benchmark in this run: CAGR 8.16% / MDD -55.20% / Sharpe 0.405.
Corrected B4 baseline: CAGR 11.00% / MDD -29.60% / Sharpe 0.671.

### Beats SPY on CAGR and MDD

- B4_unstacked_mf7030: CAGR 9.91%, MDD -20.91%, Sharpe 0.749
- L1_cegb_reference: CAGR 9.66%, MDD -25.43%, Sharpe 0.696
- B4_scv10_from_ntsx: CAGR 11.23%, MDD -31.06%, Sharpe 0.681
- B4_rsst7030_baseline: CAGR 11.00%, MDD -29.60%, Sharpe 0.671
- B4_scv10_from_zroz: CAGR 11.36%, MDD -37.20%, Sharpe 0.648
- B4_mtum10_from_zroz: CAGR 11.21%, MDD -37.09%, Sharpe 0.640
- B4_value_mix10_from_zroz: CAGR 11.13%, MDD -37.51%, Sharpe 0.639
- B4_aggressive_scv15: CAGR 11.86%, MDD -40.89%, Sharpe 0.639
- B4_scv15_from_zroz: CAGR 11.50%, MDD -40.76%, Sharpe 0.628

### Beats corrected B4 on CAGR without worse drawdown

- None.

## Methodology Caveats

- This is not a full `verdict.json` gate run; PBO/DSR/WF/bootstrap were not recomputed from daily internal curves.
- Corrected RSST forces a 2000+ window because DBMFSIM starts in 2000.
- VBR/EFV/MTUM are factor proxies available in testfol.io (`VBRSIM`, `EFVSIM`, `MTUMSIM`), not the Avantis AVUV/AVDV/AVEM live ETFs used elsewhere.
- Tactical NDX variants require annual-realize tax modeling before any deploy comparison.
