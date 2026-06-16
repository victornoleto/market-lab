# Factor Core Comparison Report

Status: research-only diagnostic. No deployment, paper-trade label, capital allocation change, or mandate override.

Primary case: `us_short_live_yearly` (`Yearly` rebalance, Testfol.io payload).

## Headline

The short live-window factor core `60% AVUS / 20% AVUV / 20% SPMO` beat the RSC-US tracking payload by terminal wealth: `1.125x` versus RSC.

Common window: `2022-03-17` to `2026-06-12` (`4.24` years).

This is a short-window regime result, not validation. It is useful because it tests the live ETF implementation friction of RSC versus live factor ETFs, but it cannot answer the long-horizon expected-return question by itself `[advances_fin_ml, p.208-211]`.

## Metrics

| portfolio | cagr | mdd | vol | sharpe | sortino | calmar | terminal |
|---|---|---|---|---|---|---|---|
| SPMO | 26.40% | -20.13% | 19.87% | 1.284 | 1.779 | 1.311 | 2.699 |
| AVUS_AVUV_SPMO_60_20_20 | 16.58% | -20.47% | 18.11% | 0.942 | 1.308 | 0.810 | 1.916 |
| AVUS | 14.46% | -20.35% | 17.51% | 0.863 | 1.190 | 0.711 | 1.772 |
| RSC_US_TRACKING | 13.39% | -20.23% | 16.77% | 0.836 | 1.164 | 0.662 | 1.703 |
| AVUV | 12.63% | -28.78% | 22.69% | 0.640 | 0.974 | 0.439 | 1.655 |

## Relative To RSC

| portfolio | terminal_vs_rsc | min_vs_rsc | max_vs_rsc | pct_days_above_rsc |
|---|---|---|---|---|
| SPMO | 1.585 | 0.960 | 1.585 | 92.95% |
| AVUS_AVUV_SPMO_60_20_20 | 1.125 | 0.949 | 1.186 | 88.16% |
| AVUS | 1.041 | 0.914 | 1.158 | 76.22% |
| AVUV | 0.972 | 0.812 | 1.188 | 57.33% |

## Monthly Sensitivity

The same fixed weights were rerun with monthly rebalance. This is a sensitivity check, not a new optimized portfolio; rebalance frequency should not be selected from the same short sample `[testing_tuning, p.327-335]`.

| case | factor_cagr | factor_mdd | factor_terminal | rsc_cagr | rsc_mdd | rsc_terminal | factor_terminal_vs_rsc |
|---|---|---|---|---|---|---|---|
| yearly | 16.58% | -20.47% | 1.916 | 13.39% | -20.23% | 1.703 | 1.125 |
| monthly | 16.63% | -20.57% | 1.919 | 12.55% | -22.13% | 1.650 | 1.163 |

Monthly rebalance leaves the factor mix effectively unchanged and makes the RSC tracking comparator slightly worse over this window. The core conclusion therefore does not depend on yearly rebalance noise.

## Stress Windows

| stress_window | portfolio | cagr | mdd | sharpe | terminal |
|---|---|---|---|---|---|
| 2022_rate_cycle | AVUS | -11.39% | -20.35% | -0.369 | 0.909 |
| 2022_rate_cycle | AVUV | -8.15% | -20.04% | -0.168 | 0.935 |
| 2022_rate_cycle | SPMO | -3.69% | -18.78% | -0.065 | 0.971 |
| 2022_rate_cycle | AVUS_AVUV_SPMO_60_20_20 | -9.21% | -19.70% | -0.279 | 0.927 |
| 2022_rate_cycle | RSC_US_TRACKING | -19.31% | -20.23% | -1.136 | 0.844 |
| 2023_recovery | AVUS | 22.92% | -10.77% | 1.541 | 1.226 |
| 2023_recovery | AVUV | 24.40% | -17.15% | 1.107 | 1.240 |
| 2023_recovery | SPMO | 19.77% | -8.63% | 1.442 | 1.195 |
| 2023_recovery | AVUS_AVUV_SPMO_60_20_20 | 22.59% | -9.78% | 1.480 | 1.222 |
| 2023_recovery | RSC_US_TRACKING | 15.91% | -13.11% | 1.242 | 1.157 |
| 2024_2026_recent | AVUS | 21.51% | -19.74% | 1.305 | 1.609 |
| 2024_2026_recent | AVUV | 16.31% | -28.78% | 0.822 | 1.446 |
| 2024_2026_recent | SPMO | 42.80% | -20.13% | 1.777 | 2.387 |
| 2024_2026_recent | AVUS_AVUV_SPMO_60_20_20 | 24.77% | -20.47% | 1.383 | 1.717 |
| 2024_2026_recent | RSC_US_TRACKING | 25.71% | -16.07% | 1.369 | 1.749 |

## Rolling Windows

### 1y Rolling Summary

| portfolio | cagr_median | cagr_min | mdd_min | sharpe_median |
|---|---|---|---|---|
| AVUS | 17.26% | -10.66% | -20.35% | 1.011 |
| AVUS_AVUV_SPMO_60_20_20 | 17.87% | -10.89% | -20.47% | 0.999 |
| AVUV | 11.92% | -17.00% | -28.78% | 0.614 |
| RSC_US_TRACKING | 19.82% | -16.44% | -20.23% | 1.289 |
| SPMO | 29.05% | -12.37% | -20.13% | 1.289 |

### 3y Rolling Summary

| portfolio | cagr_median | cagr_min | mdd_min | sharpe_median |
|---|---|---|---|---|
| AVUS | 18.11% | 3.10% | -20.35% | 1.139 |
| AVUS_AVUV_SPMO_60_20_20 | 19.58% | 4.32% | -20.47% | 1.154 |
| AVUV | 12.84% | -0.23% | -28.78% | 0.650 |
| RSC_US_TRACKING | 21.03% | 0.45% | -20.23% | 1.277 |
| SPMO | 29.98% | 11.89% | -20.13% | 1.502 |

- `5y`: not enough common history.

## Reading

- The factor portfolio is the cleaner live-ETF implementation over this short window: no embedded managed-futures proxy, no GDE/RSST short-history stack, and less dependence on 2022 bond/futures behavior.
- The RSC thesis is still a long-horizon, cross-asset diversification thesis. It should be judged on crisis/rate/inflation regimes and multi-decade sequence risk, not only the post-GDE live window `[risk_parity, p.80-81]`.
- A sub-5-year loss to factor ETFs is not surprising and is not by itself a reason to abandon RSC. It is evidence that the implementation comparison needs a live-window dashboard plus a separate proxy-long study.

## Next Tests

1. Build `proxy_long` using the existing RSC discussion matrix plus explicit factor proxies for AVUS/AVUV/SPMO/AVDE/AVDV/IDMO/AVEM.
2. Add global factor cases: `60/30/10`, historical `55/30/15`, and RSC-Global comparators.
3. Keep all weights fixed/pre-registered; do not optimize the factor mix from this short sample `[testing_tuning, p.327-335]`.
