# Trade log — Plano A winner (`gayed_ema100_L2_off_gld`)

Reconstructed by re-running `simulate_plano_a_rotation` with the winner config from `gayed_ema100_L2_off_gld.json` (deterministic). Each row = one continuous hold segment per leg (entry when weight 0→positive, exit when positive→0).

> **Data caveat:** `GLD` first bar is `2004-11-18`; the strategy ran 883 bars (14.1% of history) before that. Off-regime days in that window earned **0%** (silent cash fallback) rather than the intended `GLD` return. Post-inception behaviour is authentic.

## Summary

- Total segments: **489**
- By leg: {'GLD': 180, 'QQQ': 151, 'SPY': 158}
- By split: {'FWD': 30, 'FWD*open': 2, 'IS': 343, 'OOS': 114}
- Win rate (leveraged return > 0): **34.6%**
- Median hold days by leg: {'GLD': 4.0, 'QQQ': 8.0, 'SPY': 7.5}
- Mean gross return % by leg (underlying): {'GLD': 0.409, 'QQQ': 1.669, 'SPY': 0.828}
- Mean leveraged return % by leg (× L applied on risk-on): {'GLD': 0.409, 'QQQ': 3.339, 'SPY': 1.655}

**Cross-check vs gate JSON:** n_switches_total = 616 (SPY=315, QQQ=301). Each risk-on trade = 2 switches (entry + exit), so expected SPY trades ≈ 158 and QQQ trades ≈ 151. Observed in this log: SPY=158, QQQ=151.

## First 10 trades (chronological)

| leg | entry_date | exit_date | hold_days | weight | entry_price | exit_price | gross_ret_pct | leveraged_ret_pct | split |
|---|---|---|---|---|---|---|---|---|---|
| GLD | 2001-05-14 | 2001-11-13 | 183 | 1.0 | nan | nan | 0.0 | 0.0 | IS |
| QQQ | 2001-11-06 | 2002-01-16 | 71 | 1.0 | 38.19 | 38.78 | 1.5449 | 3.0898 | IS |
| SPY | 2001-11-13 | 2001-11-28 | 15 | 1.0 | 114.55 | 113.34 | -1.0563 | -2.1126 | IS |
| GLD | 2001-11-28 | 2001-11-29 | 1 | 0.5 | nan | nan | 0.0 | 0.0 | IS |
| SPY | 2001-11-29 | 2001-12-03 | 4 | 1.0 | 114.87 | 113.37 | -1.3058 | -2.6116 | IS |
| GLD | 2001-12-03 | 2001-12-04 | 1 | 0.5 | nan | nan | 0.0 | 0.0 | IS |
| SPY | 2001-12-04 | 2001-12-13 | 9 | 1.0 | 115.29 | 112.06 | -2.8016 | -5.6033 | IS |
| GLD | 2001-12-13 | 2001-12-17 | 4 | 0.5 | nan | nan | 0.0 | 0.0 | IS |
| SPY | 2001-12-17 | 2002-01-14 | 28 | 1.0 | 114.3 | 114.22 | -0.07 | -0.14 | IS |
| GLD | 2002-01-14 | 2002-01-15 | 1 | 0.5 | nan | nan | 0.0 | 0.0 | IS |

## Last 10 trades

| leg | entry_date | exit_date | hold_days | weight | entry_price | exit_price | gross_ret_pct | leveraged_ret_pct | split |
|---|---|---|---|---|---|---|---|---|---|
| GLD | 2026-02-23 | 2026-02-24 | 1 | 0.5 | 481.28 | 474.61 | -1.3859 | -1.3859 | FWD |
| QQQ | 2026-02-24 | 2026-03-03 | 7 | 1.0 | 607.87 | 601.58 | -1.0348 | -2.0695 | FWD |
| GLD | 2026-03-03 | 2026-03-04 | 1 | 0.5 | 468.14 | 471.8 | 0.7818 | 0.7818 | FWD |
| QQQ | 2026-03-04 | 2026-03-06 | 2 | 1.0 | 610.75 | 599.75 | -1.8011 | -3.6021 | FWD |
| GLD | 2026-03-06 | 2026-03-09 | 3 | 1.0 | 473.51 | 472.53 | -0.207 | -0.207 | FWD |
| QQQ | 2026-03-09 | 2026-03-12 | 3 | 1.0 | 607.76 | 597.26 | -1.7277 | -3.4553 | FWD |
| SPY | 2026-03-09 | 2026-03-10 | 1 | 1.0 | 678.27 | 677.18 | -0.1607 | -0.3214 | FWD |
| GLD | 2026-03-10 | 2026-04-08 | 29 | 0.5 | 477.86 | 434.53 | -9.0675 | -9.0675 | FWD |
| QQQ | 2026-04-08 | 2026-04-14 | 6 | 1.0 | 606.09 | 628.6 | 3.714 | 7.4279 | FWD*open |
| SPY | 2026-04-08 | 2026-04-14 | 6 | 1.0 | 676.01 | 694.46 | 2.7292 | 5.4585 | FWD*open |

## Top 10 by |leveraged_ret_pct|

| leg | entry_date | exit_date | hold_days | weight | entry_price | exit_price | gross_ret_pct | leveraged_ret_pct | split |
|---|---|---|---|---|---|---|---|---|---|
| QQQ | 2020-04-13 | 2021-03-04 | 325 | 1.0 | 203.03 | 304.1 | 49.7808 | 99.5616 | OOS |
| QQQ | 2003-04-01 | 2004-03-08 | 342 | 1.0 | 25.45 | 35.77 | 40.5501 | 81.1002 | IS |
| QQQ | 2009-04-01 | 2010-01-29 | 303 | 1.0 | 30.77 | 42.79 | 39.064 | 78.128 | IS |
| QQQ | 2016-12-05 | 2018-02-08 | 430 | 1.0 | 116.6 | 153.45 | 31.6038 | 63.2075 | IS |
| SPY | 2020-11-02 | 2021-09-30 | 332 | 1.0 | 330.2 | 429.14 | 29.9637 | 59.9273 | OOS |
| SPY | 2003-04-14 | 2004-03-22 | 343 | 1.0 | 88.95 | 109.65 | 23.2715 | 46.543 | IS |
| SPY | 2016-11-08 | 2018-02-05 | 454 | 1.0 | 214.11 | 263.93 | 23.2684 | 46.5368 | IS |
| QQQ | 2023-03-13 | 2023-09-21 | 192 | 1.0 | 290.69 | 357.86 | 23.1071 | 46.2142 | OOS |
| QQQ | 2013-06-26 | 2014-04-04 | 282 | 1.0 | 70.87 | 86.37 | 21.871 | 43.7421 | IS |
| QQQ | 2025-05-08 | 2025-11-20 | 196 | 1.0 | 488.29 | 585.67 | 19.9431 | 39.8861 | FWD |

## Full log

See `trade_log.csv` for all 489 rows.