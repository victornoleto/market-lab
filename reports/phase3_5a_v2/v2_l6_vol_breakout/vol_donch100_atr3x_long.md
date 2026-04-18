# V2-L6 vol breakout — `vol_donch100_atr3x_long` (iter 76)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (3 gates)
**Config:** Donchian entry=100d, exit=trailing_atr_3x (ATR 3.0× on 20d), direction=long-only
**Universe:** SPY, QQQ, DIA, IWM, GLD, SLV, USO, UNG, TLT, HYG (10/10 active)
**Window:** 2014-01-02 → 2026-04-14 (3088 bars, equal-weight 1/N)

## Split metrics (portfolio)

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2014-01-02 → 2021-12-31 | 2015 | 0.630 | 2.96% | -7.26% | 1.262 |
| OOS | 2022-01-01 → 2024-12-31 | 753 | -0.279 | -1.31% | -8.22% | 0.961 |
| FWD | 2025-01-01 → 2026-04-14 | 320 | 1.318 | 7.13% | -4.29% | 1.091 |

## Walk-forward (8 windows)

- Profitable windows: **0.88** (target ≥ 0.75)
- Max window drawdown: **9.9%** (cap 25%)
- Pass: **YES**

## Hold / trade diagnostics (per ticker)

- Portfolio median hold: **19.5 days** (target ≥ 3d, V2 spec §1)
- Total trades across tickers: 746

| Ticker | Bars | Trades | Med hold (d) | Final eq | Sharpe (full) |
|--------|-----:|-------:|-------------:|---------:|--------------:|
| SPY | 3088 | 80 | 23.0 | 1.872 | 0.524 |
| QQQ | 3088 | 52 | 41.0 | 2.602 | 0.736 |
| DIA | 3088 | 92 | 23.5 | 1.479 | 0.342 |
| IWM | 3088 | 77 | 29.0 | 1.250 | 0.207 |
| GLD | 3088 | 29 | 21.0 | 1.488 | 0.467 |
| SLV | 3088 | 22 | 18.0 | 1.906 | 0.489 |
| USO | 3088 | 14 | 16.0 | 1.495 | 0.360 |
| UNG | 3088 | 4 | 7.5 | 0.728 | -0.373 |
| TLT | 3088 | 160 | 16.0 | 0.462 | -0.497 |
| HYG | 3088 | 216 | 10.0 | 0.766 | -0.271 |

## Cost model (Pepperstone Razor retail, Share CFD)

- Spread half: 2.0 bps | Slippage: 1.0 bps/side | Swap long: 0.0050%/day | Swap short: 0.0020%/day
- Weighting: equal_weight_1_over_N
- Citation: pepperstone razor tier (Phase 3.5a-V2 spec §3)

## Subset-gate verdict (per-config; PBO/DSR at aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | -0.279 | ❌ |
| fwd_sharpe_gt_0 | 1.318 | ✅ |
| wf_pass | 6/8 | ✅ |
| median_hold_ge_3d | 19.5d | ✅ |
| oos_cagr_ge_30pct | -1.3% | ❌ |
| oos_sharpe_ge_2 | -0.279 | ❌ |
| oos_maxdd_le_25pct | -8.2% | ✅ |

**Failed gates:** oos_sharpe_gt_0, oos_cagr_ge_30pct, oos_sharpe_ge_2

## Citations

- Donchian channel breakout 20/10 canonical: `[trading_systems_methods, p.353]`.
- Chandelier trailing ATR exit: `[volatility_trading]`.
- 1/N multi-asset trend-follow discipline: `[trend_following_covel]`.
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`.
- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.
