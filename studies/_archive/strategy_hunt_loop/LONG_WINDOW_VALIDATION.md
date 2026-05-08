# Long-window (40y synth) validation

Generated: 2026-04-25T23:25:41.686491

Re-runs select strategies on testfolio synthetic data from 1986-01-02 → 2026-04-17 (40y, 10 151 bars). Includes 1987 crash, 1990 recession, 2000 dot-com, 2008 GFC, 2020 COVID, 2022 rates, 2024-2025 — far more regime variety than the 17y SPY-Tiingo window the hunt loop uses.

Strategies with HYG/IEF-direct/VIX/EBP/T10Y3M dependencies are skipped (no synth analog). Bond-leg substituted with **ZROZSIM** (zero-coupon long bond) where the original used TLT or IEF.

## Benchmarks (40y synth b&h)

| asset | Sharpe | CAGR | MDD | bars |
|---|---|---|---|---|
| SPYSIM | 0.682 | 11.49% | 55.14% | 10150 |
| QQQSIM | 0.658 | 14.58% | 82.97% | 10150 |

## Strategy results (40y synth)

| strategy | Sharpe (Δ) | CAGR (Δ) | MDD (Δ) | dominates? |
|---|---|---|---|---|
| `iter004_vol_managed_spy_SPYSIM` | 0.811 (+0.129) | 14.40% (+2.91pp) | 56.08% (+0.94pp) | ✅ Sharpe+CAGR |
| `iter005_variance_managed_spy_SPYSIM` | 0.792 (+0.110) | 13.96% (+2.47pp) | 59.71% (+4.57pp) | ✅ Sharpe+CAGR |
| `iter006_vol_managed_60_40_SPYSIM_ZROZSIM` | 0.932 (+0.250) | 14.41% (+2.92pp) | 34.70% (-20.44pp) | ✅ Sharpe+CAGR |
| `iter015_ntsx_static_90_60_SPYSIM_ZROZSIM` | 0.840 (+0.158) | 16.95% (+5.46pp) | 48.81% (-6.33pp) | ✅ Sharpe+CAGR |
| `iter016_static_stack_vm_SPYSIM_ZROZSIM` | 0.951 (+0.269) | 15.13% (+3.64pp) | 34.62% (-20.53pp) | ✅ Sharpe+CAGR |
| `iter035_static_stack_3leg_SPYSIM_ZROZSIM_GLDSIM` | 0.922 (+0.240) | 19.60% (+8.11pp) | 46.18% (-8.96pp) | ✅ Sharpe+CAGR |
| `iter074_ensemble_SIMPLIFIED_to_iter016` | 0.951 (+0.269) | 15.13% (+3.64pp) | 34.62% (-20.53pp) | ✅ Sharpe+CAGR |

## Strategies skipped (synth-unavailable inputs)

| iter | reason |
|---|---|
| `iter064_qqq_trend_substitution` | needs IEF+HYG (no synth analog) |
| `iter069_vix_inner_weight_reverse` | needs IEF+HYG+VIX |
| `iter070_t10y3m_cont_inner_weight` | needs IEF+HYG+T10Y3M |
| `iter071_iter064_plus_spy_mr_rsi2` | needs IEF+HYG+RSI2 path |
| `iter058_iter046_plus_hyg_tsm_w010` | needs HYG |
| `iter041_regime_weights_vix_static_stack` | needs VIX |
| `iter046_iter039_overlay_on_iter041` | needs IEF |
| `iter048_iter046_output_lev_gate` | needs IEF |
| `iter063_iter058_internal_letf_iter041_only` | needs VIX |
| `iter072_iter064_vix_cond_r_mr_allocation` | needs VIX |
| `iter073_gayed_ma_gate_on_iter016` | needs Gayed-MA gate (UTIL/SPY ratio) |
| `iter051_iter037_plus_iter026_w080` | needs IEF+VIX |
| `iter053_iter037_plus_iter046_w070` | needs IEF |

## Reading the table

- **✅ Sharpe+CAGR**: dominates SPY/QQQ b&h on BOTH risk-adjusted and raw return — strongest evidence the edge is real.
- **🟡 Sharpe-only**: better risk-adjusted but lower raw return — defensive stance; valid for sleep-well portfolios but trades CAGR.
- **❌ neither**: edge does not survive the longer window.

Caveat: synth data has perfect liquidity, no slippage, idealized dividend reinvestment. Real-world execution would haircut these numbers by ~50-150 bps CAGR depending on rebalance frequency.
