# Iter 054 — Satellite Funding Policy

**Date:** 2026-05-03
**Satellite basket:** 10% AVUV / 5% SPMO / 5% FMTM / 5% BTC.
**Status:** live-window screen only; FMTM constrains common history to ~1.1y.

## Ranking

| strategy | window | CAGR | MDD | Sharpe |
|---|---|---:|---:|---:|
| sat_25_from_zroz_only | 2025-03-20 -> 2026-05-01 (1.11y) | 38.77% | -15.15% | 1.603 |
| sat_25_from_zroz_ntsx | 2025-03-20 -> 2026-05-01 (1.11y) | 34.97% | -14.21% | 1.553 |
| sat_25_keep_rsst_20zroz | 2025-03-20 -> 2026-05-01 (1.11y) | 32.99% | -14.15% | 1.518 |
| sat_25_from_zroz_gde | 2025-03-20 -> 2026-05-01 (1.11y) | 31.03% | -14.09% | 1.477 |
| sat_25_prorata_b4 | 2025-03-20 -> 2026-05-01 (1.11y) | 28.41% | -12.76% | 1.448 |
| sat_20_no_fmtm | 2025-03-20 -> 2026-05-01 (1.11y) | 29.82% | -13.85% | 1.436 |
| B4_base | 2025-03-20 -> 2026-05-01 (1.11y) | 27.49% | -12.63% | 1.402 |
| B4_btc5 | 2025-03-20 -> 2026-05-01 (1.11y) | 28.04% | -12.94% | 1.379 |
| SPY | 2025-03-20 -> 2026-05-01 (1.11y) | 25.81% | -13.73% | 1.330 |
| SSO | 2025-03-20 -> 2026-05-01 (1.11y) | 43.59% | -26.21% | 1.194 |

## Interpretation

Because FMTM forces the common window to 2025-03-20 -> 2026-05-01, this test cannot approve a permanent allocation. It can only compare funding mechanics in the current regime.

Funding all 25% from ZROZ is too aggressive structurally: it removes most of the long-duration crash convexity. A pro-rata 75% B4 core is cleaner, but it cuts RSST and GDE, the two sleeves that make B4 different from a simple equity/factor bet.

Preferred compromise if the user explicitly wants the 25% satellite: keep RSST at 25%, keep at least 10-12.5% ZROZ, and fund from NTSX/GDE/ZROZ rather than only from ZROZ.
