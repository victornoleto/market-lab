# Cross-library metric validation (light)

Generated: 2026-04-26T01:47:22.716488

Validates Sharpe / CAGR / MDD across 4 independent methods:
**pandas-native**, **numpy-pure**, **vectorbt**, **quantstats**.

Divergence labels:
- 🟢 GREEN: max relative divergence < 1%
- 🟡 YELLOW: 1-5%
- 🔴 RED: > 5% — METRIC IMPLEMENTATION DISAGREEMENT

Caveat: this catches metric bugs only. NOT engine-level validation. For engine-level cross-validation each strategy would need re-implementation in vectorbt or backtrader from price data — outside scope of this run.

## iter 074 (v2 score 95) — `iter016-iter064-ensemble`

### spy_real (cfg `iter074_ensemble_w016_020`, 4205 bars, 2009-07-28 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.305 | 1.305 | — | 1.305 | 🟢 GREEN |
| **cagr** | 11.49% | 11.49% | — | 11.49% | 🟢 GREEN |
| **mdd** | 17.47% | 17.47% | — | 17.47% | 🟢 GREEN |

### ndx_real (cfg `iter074_ensemble_w016_020`, 4045 bars, 2010-03-17 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.359 | 1.359 | — | 1.359 | 🟢 GREEN |
| **cagr** | 12.23% | 12.23% | — | 12.23% | 🟢 GREEN |
| **mdd** | 16.20% | 16.20% | — | 16.20% | 🟢 GREEN |

### educational (cfg `iter074_ensemble_w016_020`, 5080 bars, 2006-02-03 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.193 | 1.193 | — | 1.193 | 🟢 GREEN |
| **cagr** | 10.67% | 10.67% | — | 10.67% | 🟢 GREEN |
| **mdd** | 17.47% | 17.47% | — | 17.47% | 🟢 GREEN |

## iter 006 (v2 score 86) — `vol-managed-60-40`

### spy_real (cfg `vt15_L21_cap20`, 4205 bars, 2009-07-28 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.000 | 1.000 | — | 1.000 | 🟢 GREEN |
| **cagr** | 16.11% | 16.11% | — | 16.11% | 🟢 GREEN |
| **mdd** | 37.21% | 37.21% | — | 37.21% | 🟢 GREEN |

### ndx_real (cfg `vt15_L21_cap20`, 4045 bars, 2010-03-17 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.021 | 1.021 | — | 1.021 | 🟢 GREEN |
| **cagr** | 17.94% | 17.94% | — | 17.94% | 🟢 GREEN |
| **mdd** | 37.21% | 37.21% | — | 37.21% | 🟢 GREEN |

### educational (cfg `vt15_L63_cap20`, 5904 bars, 2002-10-25 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 0.929 | 0.929 | — | 0.929 | 🟢 GREEN |
| **cagr** | 14.49% | 14.49% | — | 14.49% | 🟢 GREEN |
| **mdd** | 40.10% | 40.10% | — | 40.10% | 🟢 GREEN |

## iter 064 (v2 score 85) — `iter058-qqq-trend-substitution`

### spy_real (cfg `iter046_plus_qqq_trend_w010_lookback200`, 4226 bars, 2009-06-26 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.331 | 1.331 | — | 1.331 | 🟢 GREEN |
| **cagr** | 9.97% | 9.97% | — | 9.97% | 🟢 GREEN |
| **mdd** | 15.33% | 15.33% | — | 15.33% | 🟢 GREEN |

### ndx_real (cfg `iter046_plus_qqq_trend_w010_lookback200`, 4066 bars, 2010-02-16 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.375 | 1.375 | — | 1.375 | 🟢 GREEN |
| **cagr** | 10.25% | 10.25% | — | 10.25% | 🟢 GREEN |
| **mdd** | 14.74% | 14.74% | — | 14.74% | 🟢 GREEN |

### educational (cfg `iter046_plus_qqq_trend_w010_lookback200`, 5101 bars, 2006-01-04 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.217 | 1.217 | — | 1.217 | 🟢 GREEN |
| **cagr** | 9.51% | 9.51% | — | 9.51% | 🟢 GREEN |
| **mdd** | 17.27% | 17.27% | — | 17.27% | 🟢 GREEN |

## iter 069 (v2 score 85) — `iter064-vix-inner-weight-reverse`

### spy_real (cfg `iter064_vix_inner_w_calm005_stress020_vix20`, 4226 bars, 2009-06-26 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.321 | 1.321 | — | 1.321 | 🟢 GREEN |
| **cagr** | 9.89% | 9.89% | — | 9.89% | 🟢 GREEN |
| **mdd** | 14.38% | 14.38% | — | 14.38% | 🟢 GREEN |

### ndx_real (cfg `iter064_vix_inner_w_calm005_stress020_vix20`, 4066 bars, 2010-02-16 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.355 | 1.355 | — | 1.355 | 🟢 GREEN |
| **cagr** | 10.04% | 10.04% | — | 10.04% | 🟢 GREEN |
| **mdd** | 13.33% | 13.33% | — | 13.33% | 🟢 GREEN |

### educational (cfg `iter064_vix_inner_w_calm005_stress020_vix20`, 5101 bars, 2006-01-04 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.212 | 1.212 | — | 1.212 | 🟢 GREEN |
| **cagr** | 9.37% | 9.37% | — | 9.37% | 🟢 GREEN |
| **mdd** | 15.77% | 15.77% | — | 15.77% | 🟢 GREEN |

## iter 070 (v2 score 85) — `iter064-t10y3m-cont-inner-weight`

### spy_real (cfg `iter064_t10y3m_cont_alpha025_lb1260_w005_020`, 4226 bars, 2009-06-26 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.320 | 1.320 | — | 1.320 | 🟢 GREEN |
| **cagr** | 10.23% | 10.23% | — | 10.23% | 🟢 GREEN |
| **mdd** | 14.87% | 14.87% | — | 14.87% | 🟢 GREEN |

### ndx_real (cfg `iter064_t10y3m_cont_alpha025_lb1260_w005_020`, 4066 bars, 2010-02-16 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.358 | 1.358 | — | 1.358 | 🟢 GREEN |
| **cagr** | 10.46% | 10.46% | — | 10.46% | 🟢 GREEN |
| **mdd** | 14.12% | 14.12% | — | 14.12% | 🟢 GREEN |

### educational (cfg `iter064_t10y3m_cont_alpha025_lb1260_w005_020`, 5101 bars, 2006-01-04 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.214 | 1.214 | — | 1.214 | 🟢 GREEN |
| **cagr** | 9.71% | 9.71% | — | 9.71% | 🟢 GREEN |
| **mdd** | 17.09% | 17.09% | — | 17.09% | 🟢 GREEN |

## iter 071 (v2 score 85) — `iter064-plus-spy-mr-rsi2`

### spy_real (cfg `iter064_plus_spy_mr_rsi2_th5_w010`, 4226 bars, 2009-06-26 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.361 | 1.361 | — | 1.361 | 🟢 GREEN |
| **cagr** | 9.39% | 9.39% | — | 9.39% | 🟢 GREEN |
| **mdd** | 13.96% | 13.96% | — | 13.96% | 🟢 GREEN |

### ndx_real (cfg `iter064_plus_spy_mr_rsi2_th5_w010`, 4066 bars, 2010-02-16 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.401 | 1.401 | — | 1.401 | 🟢 GREEN |
| **cagr** | 9.60% | 9.60% | — | 9.60% | 🟢 GREEN |
| **mdd** | 13.42% | 13.42% | — | 13.42% | 🟢 GREEN |

### educational (cfg `iter064_plus_spy_mr_rsi2_th5_w010`, 5101 bars, 2006-01-04 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.251 | 1.251 | — | 1.251 | 🟢 GREEN |
| **cagr** | 8.97% | 8.97% | — | 8.97% | 🟢 GREEN |
| **mdd** | 15.55% | 15.55% | — | 15.55% | 🟢 GREEN |

## iter 046 (v2 score 80) — `iter039-overlay-on-iter041`

### spy_real (cfg `iter039_on_iter041_50_50`, 4226 bars, 2009-06-26 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.323 | 1.323 | — | 1.323 | 🟢 GREEN |
| **cagr** | 9.45% | 9.45% | — | 9.45% | 🟢 GREEN |
| **mdd** | 15.22% | 15.22% | — | 15.22% | 🟢 GREEN |

### ndx_real (cfg `iter039_on_iter041_50_50`, 4066 bars, 2010-02-16 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.381 | 1.381 | — | 1.381 | 🟢 GREEN |
| **cagr** | 9.83% | 9.83% | — | 9.83% | 🟢 GREEN |
| **mdd** | 14.57% | 14.57% | — | 14.57% | 🟢 GREEN |

### educational (cfg `iter039_on_iter041_50_50`, 5101 bars, 2006-01-04 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.202 | 1.202 | — | 1.202 | 🟢 GREEN |
| **cagr** | 9.17% | 9.17% | — | 9.17% | 🟢 GREEN |
| **mdd** | 17.97% | 17.97% | — | 17.97% | 🟢 GREEN |

## iter 058 (v2 score 80) — `iter046-plus-hyg-tsm-w010`

### spy_real (cfg `iter046_plus_hyg_tsm_w010_lookback90`, 4226 bars, 2009-06-26 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.347 | 1.347 | — | 1.347 | 🟢 GREEN |
| **cagr** | 9.01% | 9.01% | — | 9.01% | 🟢 GREEN |
| **mdd** | 13.71% | 13.71% | — | 13.71% | 🟢 GREEN |

### ndx_real (cfg `iter046_plus_hyg_tsm_w010_lookback90`, 4066 bars, 2010-02-16 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.403 | 1.403 | — | 1.403 | 🟢 GREEN |
| **cagr** | 9.33% | 9.33% | — | 9.33% | 🟢 GREEN |
| **mdd** | 13.12% | 13.12% | — | 13.12% | 🟢 GREEN |

### educational (cfg `iter046_plus_hyg_tsm_w010_lookback90`, 4783 bars, 2007-04-12 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.222 | 1.222 | — | 1.222 | 🟢 GREEN |
| **cagr** | 8.70% | 8.70% | — | 8.70% | 🟢 GREEN |
| **mdd** | 16.74% | 16.74% | — | 16.74% | 🟢 GREEN |

## iter 072 (v2 score 80) — `iter064-vix-cond-r-mr-allocation`

### spy_real (cfg `iter064_vix_cond_calm010_stress005`, 4226 bars, 2009-06-26 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.350 | 1.350 | — | 1.350 | 🟢 GREEN |
| **cagr** | 9.57% | 9.57% | — | 9.57% | 🟢 GREEN |
| **mdd** | 14.34% | 14.34% | — | 14.34% | 🟢 GREEN |

### ndx_real (cfg `iter064_vix_cond_calm010_stress005`, 4066 bars, 2010-02-16 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.391 | 1.391 | — | 1.391 | 🟢 GREEN |
| **cagr** | 9.79% | 9.79% | — | 9.79% | 🟢 GREEN |
| **mdd** | 13.77% | 13.77% | — | 13.77% | 🟢 GREEN |

### educational (cfg `iter064_vix_cond_calm010_stress005`, 5101 bars, 2006-01-04 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.230 | 1.230 | — | 1.230 | 🟢 GREEN |
| **cagr** | 9.10% | 9.10% | — | 9.10% | 🟢 GREEN |
| **mdd** | 16.33% | 16.33% | — | 16.33% | 🟢 GREEN |

## iter 076 (v2 score 80) — `iter064-plus-levered-gld-tlt-trend-sleeve`

### spy_real (cfg `iter076_lev_tv015_w015`, 4226 bars, 2009-06-26 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.325 | 1.325 | — | 1.325 | 🟢 GREEN |
| **cagr** | 9.10% | 9.10% | — | 9.10% | 🟢 GREEN |
| **mdd** | 13.99% | 13.99% | — | 13.99% | 🟢 GREEN |

### ndx_real (cfg `iter076_lev_tv015_w015`, 4066 bars, 2010-02-16 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.352 | 1.352 | — | 1.352 | 🟢 GREEN |
| **cagr** | 9.21% | 9.21% | — | 9.21% | 🟢 GREEN |
| **mdd** | 13.48% | 13.48% | — | 13.48% | 🟢 GREEN |

### educational (cfg `iter076_lev_tv015_w015`, 5101 bars, 2006-01-04 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.231 | 1.231 | — | 1.231 | 🟢 GREEN |
| **cagr** | 8.81% | 8.81% | — | 8.81% | 🟢 GREEN |
| **mdd** | 15.74% | 15.74% | — | 15.74% | 🟢 GREEN |

## iter 041 (v2 score 79) — `regime-weights-vix-static-stack`

### spy_real (cfg `regime_weights_vix_lt20_70_40_40_ge20_30_55_55`, 4226 bars, 2009-06-26 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.130 | 1.130 | — | 1.130 | 🟢 GREEN |
| **cagr** | 13.52% | 13.52% | — | 13.52% | 🟢 GREEN |
| **mdd** | 24.65% | 24.65% | — | 24.65% | 🟢 GREEN |

### ndx_real (cfg `regime_weights_vix_lt20_70_40_40_ge20_30_55_55`, 4066 bars, 2010-02-16 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.163 | 1.163 | — | 1.163 | 🟢 GREEN |
| **cagr** | 15.78% | 15.78% | — | 15.78% | 🟢 GREEN |
| **mdd** | 30.84% | 30.84% | — | 30.84% | 🟢 GREEN |

### educational (cfg `regime_weights_vix_lt20_70_40_40_ge20_30_55_55`, 5101 bars, 2006-01-04 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.027 | 1.027 | — | 1.027 | 🟢 GREEN |
| **cagr** | 13.03% | 13.03% | — | 13.03% | 🟢 GREEN |
| **mdd** | 27.60% | 27.60% | — | 27.60% | 🟢 GREEN |

## iter 051 (v2 score 79) — `iter037-plus-iter026-w080`

### spy_real (cfg `iter037_plus_iter026_w080`, 4225 bars, 2009-06-26 → 2026-04-14)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.198 | 1.198 | — | 1.198 | 🟢 GREEN |
| **cagr** | 13.46% | 13.46% | — | 13.46% | 🟢 GREEN |
| **mdd** | 21.48% | 21.48% | — | 21.48% | 🟢 GREEN |

### ndx_real (cfg `iter037_plus_iter026_w080`, 4065 bars, 2010-02-16 → 2026-04-14)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.219 | 1.219 | — | 1.219 | 🟢 GREEN |
| **cagr** | 15.62% | 15.62% | — | 15.62% | 🟢 GREEN |
| **mdd** | 26.96% | 26.96% | — | 26.96% | 🟢 GREEN |

### educational (cfg `iter037_plus_iter026_w080`, 5100 bars, 2006-01-04 → 2026-04-14)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.021 | 1.021 | — | 1.021 | 🟢 GREEN |
| **cagr** | 12.40% | 12.40% | — | 12.40% | 🟢 GREEN |
| **mdd** | 29.30% | 29.30% | — | 29.30% | 🟢 GREEN |

## iter 053 (v2 score 79) — `iter037-plus-iter046-w070`

### spy_real (cfg `iter037_plus_iter046_w070`, 4226 bars, 2009-06-26 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.192 | 1.192 | — | 1.192 | 🟢 GREEN |
| **cagr** | 13.72% | 13.72% | — | 13.72% | 🟢 GREEN |
| **mdd** | 22.27% | 22.27% | — | 22.27% | 🟢 GREEN |

### ndx_real (cfg `iter037_plus_iter046_w070`, 4066 bars, 2010-02-16 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.220 | 1.220 | — | 1.220 | 🟢 GREEN |
| **cagr** | 15.51% | 15.51% | — | 15.51% | 🟢 GREEN |
| **mdd** | 26.95% | 26.95% | — | 26.95% | 🟢 GREEN |

### educational (cfg `iter037_plus_iter046_w070`, 5101 bars, 2006-01-04 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.029 | 1.029 | — | 1.029 | 🟢 GREEN |
| **cagr** | 12.73% | 12.73% | — | 12.73% | 🟢 GREEN |
| **mdd** | 28.72% | 28.72% | — | 28.72% | 🟢 GREEN |

## iter 005 (v2 score 78) — `variance-managed-spy`

### spy_real (cfg `vt20_L21_cap15`, 4208 bars, 2009-07-28 → 2026-04-20)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 0.981 | 0.981 | — | 0.981 | 🟢 GREEN |
| **cagr** | 17.94% | 17.94% | — | 17.94% | 🟢 GREEN |
| **mdd** | 25.67% | 25.67% | — | 25.67% | 🟢 GREEN |

### ndx_real (cfg `vt20_L21_cap15`, 4048 bars, 2010-03-17 → 2026-04-20)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.052 | 1.052 | — | 1.052 | 🟢 GREEN |
| **cagr** | 21.12% | 21.12% | — | 21.12% | 🟢 GREEN |
| **mdd** | 24.20% | 24.20% | — | 24.20% | 🟢 GREEN |

### educational (cfg `vt15_L21_cap15`, 10129 bars, 1986-02-03 → 2026-04-17)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 0.849 | 0.849 | — | 0.849 | 🟢 GREEN |
| **cagr** | 12.46% | 12.46% | — | 12.46% | 🟢 GREEN |
| **mdd** | 46.94% | 46.94% | — | 46.94% | 🟢 GREEN |

## iter 048 (v2 score 78) — `iter046-output-lev-gate`

### spy_real (cfg `iter046_lev_calm14_stress10_vix20`, 4226 bars, 2009-06-26 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.289 | 1.289 | — | 1.289 | 🟢 GREEN |
| **cagr** | 11.21% | 11.21% | — | 11.21% | 🟢 GREEN |
| **mdd** | 17.72% | 17.72% | — | 17.72% | 🟢 GREEN |

### ndx_real (cfg `iter046_lev_calm14_stress10_vix20`, 4066 bars, 2010-02-16 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.344 | 1.344 | — | 1.344 | 🟢 GREEN |
| **cagr** | 11.73% | 11.73% | — | 11.73% | 🟢 GREEN |
| **mdd** | 17.00% | 17.00% | — | 17.00% | 🟢 GREEN |

### educational (cfg `iter046_lev_calm14_stress10_vix20`, 5101 bars, 2006-01-04 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.201 | 1.201 | — | 1.201 | 🟢 GREEN |
| **cagr** | 10.93% | 10.93% | — | 10.93% | 🟢 GREEN |
| **mdd** | 18.48% | 18.48% | — | 18.48% | 🟢 GREEN |

## iter 004 (v2 score 76) — `vol-managed-spy`

### spy_real (cfg `tv20_L21_cap15`, 4208 bars, 2009-07-28 → 2026-04-20)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 0.980 | 0.980 | — | 0.980 | 🟢 GREEN |
| **cagr** | 17.83% | 17.83% | — | 17.83% | 🟢 GREEN |
| **mdd** | 24.98% | 24.98% | — | 24.98% | 🟢 GREEN |

### ndx_real (cfg `tv20_L21_cap15`, 4048 bars, 2010-03-17 → 2026-04-20)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.043 | 1.043 | — | 1.043 | 🟢 GREEN |
| **cagr** | 21.14% | 21.14% | — | 21.14% | 🟢 GREEN |
| **mdd** | 28.87% | 28.87% | — | 28.87% | 🟢 GREEN |

### educational (cfg `tv20_L21_cap20`, 10129 bars, 1986-02-03 → 2026-04-17)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 0.828 | 0.828 | — | 0.828 | 🟢 GREEN |
| **cagr** | 16.44% | 16.44% | — | 16.44% | 🟢 GREEN |
| **mdd** | 58.06% | 58.06% | — | 58.06% | 🟢 GREEN |

## iter 045 (v2 score 76) — `iter039-overlay-on-iter037`

### spy_real (cfg `iter039_on_iter037_50_50`, 4226 bars, 2009-06-26 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.284 | 1.284 | — | 1.284 | 🟢 GREEN |
| **cagr** | 10.43% | 10.43% | — | 10.43% | 🟢 GREEN |
| **mdd** | 16.26% | 16.26% | — | 16.26% | 🟢 GREEN |

### ndx_real (cfg `iter039_on_iter037_50_50`, 4066 bars, 2010-02-16 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.326 | 1.326 | — | 1.326 | 🟢 GREEN |
| **cagr** | 10.71% | 10.71% | — | 10.71% | 🟢 GREEN |
| **mdd** | 15.35% | 15.35% | — | 15.35% | 🟢 GREEN |

### educational (cfg `iter039_on_iter037_50_50`, 5101 bars, 2006-01-04 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.104 | 1.104 | — | 1.104 | 🟢 GREEN |
| **cagr** | 9.75% | 9.75% | — | 9.75% | 🟢 GREEN |
| **mdd** | 22.61% | 22.61% | — | 22.61% | 🟢 GREEN |

## iter 063 (v2 score 76) — `iter058-internal-letf-iter041-only`

### spy_real (cfg `iter058_with_internal_letf_iter041_only`, 4226 bars, 2009-06-26 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.260 | 1.260 | — | 1.260 | 🟢 GREEN |
| **cagr** | 9.67% | 9.67% | — | 9.67% | 🟢 GREEN |
| **mdd** | 15.51% | 15.51% | — | 15.51% | 🟢 GREEN |

### ndx_real (cfg `iter058_with_internal_letf_iter041_only`, 4066 bars, 2010-02-16 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.345 | 1.345 | — | 1.345 | 🟢 GREEN |
| **cagr** | 11.19% | 11.19% | — | 11.19% | 🟢 GREEN |
| **mdd** | 18.01% | 18.01% | — | 18.01% | 🟢 GREEN |

### educational (cfg `iter058_with_internal_letf_iter041_only`, 4783 bars, 2007-04-12 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.171 | 1.171 | — | 1.171 | 🟢 GREEN |
| **cagr** | 9.47% | 9.47% | — | 9.47% | 🟢 GREEN |
| **mdd** | 17.51% | 17.51% | — | 17.51% | 🟢 GREEN |

## iter 075 (v2 score 76) — `iter064-plus-gld-tlt-trend-sleeve`

### spy_real (cfg `iter075_iter064_plus_gld_tlt_w015`, 4226 bars, 2009-06-26 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.339 | 1.339 | — | 1.339 | 🟢 GREEN |
| **cagr** | 8.91% | 8.91% | — | 8.91% | 🟢 GREEN |
| **mdd** | 13.69% | 13.69% | — | 13.69% | 🟢 GREEN |

### ndx_real (cfg `iter075_iter064_plus_gld_tlt_w010`, 4066 bars, 2010-02-16 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.377 | 1.377 | — | 1.377 | 🟢 GREEN |
| **cagr** | 9.46% | 9.46% | — | 9.46% | 🟢 GREEN |
| **mdd** | 13.71% | 13.71% | — | 13.71% | 🟢 GREEN |

### educational (cfg `iter075_iter064_plus_gld_tlt_w020`, 5101 bars, 2006-01-04 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.240 | 1.240 | — | 1.240 | 🟢 GREEN |
| **cagr** | 8.29% | 8.29% | — | 8.29% | 🟢 GREEN |
| **mdd** | 14.75% | 14.75% | — | 14.75% | 🟢 GREEN |

## iter 016 (v2 score 74) — `static-stack-vm-hybrid`

### spy_real (cfg `ntsx_vm_vt15_L21_cap20`, 4205 bars, 2009-07-28 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.138 | 1.138 | — | 1.138 | 🟢 GREEN |
| **cagr** | 17.76% | 17.76% | — | 17.76% | 🟢 GREEN |
| **mdd** | 26.65% | 26.65% | — | 26.65% | 🟢 GREEN |

### ndx_real (cfg `ntsx_vm_vt15_L21_cap20`, 4045 bars, 2010-03-17 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 1.194 | 1.194 | — | 1.194 | 🟢 GREEN |
| **cagr** | 20.75% | 20.75% | — | 20.75% | 🟢 GREEN |
| **mdd** | 23.23% | 23.23% | — | 23.23% | 🟢 GREEN |

### educational (cfg `ntsx_vm_vt15_L21_cap20`, 5080 bars, 2006-02-03 → 2026-04-15)

| metric | pandas | numpy | vectorbt | quantstats | divergence |
|---|---|---|---|---|---|
| **sharpe** | 0.983 | 0.983 | — | 0.983 | 🟢 GREEN |
| **cagr** | 15.05% | 15.05% | — | 15.05% | 🟢 GREEN |
| **mdd** | 31.33% | 31.33% | — | 31.33% | 🟢 GREEN |

## Summary

- 🟢 GREEN cells: 180
- 🟡 YELLOW cells: 0
- 🔴 RED cells: 0

Total cells: 180
