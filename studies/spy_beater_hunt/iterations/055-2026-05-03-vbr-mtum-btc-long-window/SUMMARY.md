# Iter 055 — VBR/MTUM Proxy Satellite

**Date:** 2026-05-03
**Purpose:** test the satellite idea using long proxies: `VBRSIM` for SCV and `MTUMSIM` for the combined SPMO/FMTM momentum sleeve.

## with_btc_2010

Window: 2010-07-20 -> 2026-04-17 (15.74y)

| strategy | CAGR | MDD | Sharpe |
|---|---:|---:|---:|
| B4_btc5 | 23.18% | -27.26% | 1.472 |
| proxy_sat_prorata_b4 | 22.53% | -27.81% | 1.441 |
| proxy_sat_keep_rsst_bal | 24.02% | -29.51% | 1.412 |
| proxy_sat_from_zroz_ntsx | 24.40% | -29.90% | 1.412 |
| proxy_sat_from_zroz_only | 25.49% | -33.57% | 1.351 |
| B4_base | 14.64% | -25.84% | 1.091 |
| SPY | 14.71% | -33.70% | 0.893 |

## no_btc_long

Window: 2000-01-04 -> 2026-04-17 (26.28y)

| strategy | CAGR | MDD | Sharpe |
|---|---:|---:|---:|
| B4_base | 12.27% | -29.02% | 0.881 |
| proxy_sat20_prorata_no_btc | 11.98% | -34.79% | 0.844 |
| proxy_sat20_from_zroz_ntsx | 12.68% | -37.74% | 0.836 |
| proxy_sat20_keep_rsst_bal | 12.31% | -37.56% | 0.826 |
| proxy_sat20_from_zroz | 12.78% | -43.34% | 0.774 |
| SPY | 8.28% | -55.20% | 0.509 |

## Interpretation

The 2010+ BTC-limited test answers whether the proposed 10% SCV / 10% momentum / 5% BTC satellite works when BTC history is included. The no-BTC long test answers whether VBRSIM/MTUMSIM improve B4 without relying on Bitcoin's adoption path.
