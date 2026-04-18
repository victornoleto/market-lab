# V2-L6 vol breakout — `vol_donch100_opp_long` (iter 78)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (3 gates)
**Config:** Donchian entry=100d, exit=opposite_channel (opposite 50d channel), direction=long-only
**Universe:** SPY, QQQ, DIA, IWM, GLD, SLV, USO, UNG, TLT, HYG (10/10 active)
**Window:** 2014-01-02 → 2026-04-14 (3088 bars, equal-weight 1/N)

## Split metrics (portfolio)

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2014-01-02 → 2021-12-31 | 2015 | 0.683 | 3.73% | -7.23% | 1.340 |
| OOS | 2022-01-01 → 2024-12-31 | 753 | -0.238 | -1.46% | -9.49% | 0.957 |
| FWD | 2025-01-01 → 2026-04-14 | 320 | 1.064 | 8.98% | -5.86% | 1.115 |

## Walk-forward (8 windows)

- Profitable windows: **0.88** (target ≥ 0.75)
- Max window drawdown: **12.1%** (cap 25%)
- Pass: **YES**

## Hold / trade diagnostics (per ticker)

- Portfolio median hold: **56.8 days** (target ≥ 3d, V2 spec §1)
- Total trades across tickers: 359

| Ticker | Bars | Trades | Med hold (d) | Final eq | Sharpe (full) |
|--------|-----:|-------:|-------------:|---------:|--------------:|
| SPY | 3088 | 40 | 62.5 | 2.093 | 0.583 |
| QQQ | 3088 | 31 | 103.0 | 2.661 | 0.667 |
| DIA | 3088 | 45 | 51.0 | 1.860 | 0.491 |
| IWM | 3088 | 37 | 71.0 | 1.031 | 0.086 |
| GLD | 3088 | 21 | 67.0 | 2.047 | 0.609 |
| SLV | 3088 | 16 | 36.5 | 1.712 | 0.320 |
| USO | 3088 | 9 | 67.0 | 1.741 | 0.369 |
| UNG | 3088 | 4 | 4.5 | 0.631 | -0.466 |
| TLT | 3088 | 67 | 18.0 | 0.538 | -0.351 |
| HYG | 3088 | 89 | 15.0 | 0.713 | -0.336 |

## Cost model (Pepperstone Razor retail, Share CFD)

- Spread half: 2.0 bps | Slippage: 1.0 bps/side | Swap long: 0.0050%/day | Swap short: 0.0020%/day
- Weighting: equal_weight_1_over_N
- Citation: pepperstone razor tier (Phase 3.5a-V2 spec §3)

## Subset-gate verdict (per-config; PBO/DSR at aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | -0.238 | ❌ |
| fwd_sharpe_gt_0 | 1.064 | ✅ |
| wf_pass | 6/8 | ✅ |
| median_hold_ge_3d | 56.8d | ✅ |
| oos_cagr_ge_30pct | -1.5% | ❌ |
| oos_sharpe_ge_2 | -0.238 | ❌ |
| oos_maxdd_le_25pct | -9.5% | ✅ |

**Failed gates:** oos_sharpe_gt_0, oos_cagr_ge_30pct, oos_sharpe_ge_2

## Citations

- Donchian channel breakout 20/10 canonical: `[trading_systems_methods, p.353]`.
- Chandelier trailing ATR exit: `[volatility_trading]`.
- 1/N multi-asset trend-follow discipline: `[trend_following_covel]`.
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`.
- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.
