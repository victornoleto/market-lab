# V2-L6 vol breakout — `vol_donch20_atr3x_long` (iter 68)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (3 gates)
**Config:** Donchian entry=20d, exit=trailing_atr_3x (ATR 3.0× on 20d), direction=long-only
**Universe:** SPY, QQQ, DIA, IWM, GLD, SLV, USO, UNG, TLT, HYG (10/10 active)
**Window:** 2014-01-02 → 2026-04-14 (3088 bars, equal-weight 1/N)

## Split metrics (portfolio)

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2014-01-02 → 2021-12-31 | 2015 | 0.769 | 4.49% | -9.41% | 1.421 |
| OOS | 2022-01-01 → 2024-12-31 | 753 | -0.217 | -1.81% | -14.68% | 0.947 |
| FWD | 2025-01-01 → 2026-04-14 | 320 | 1.527 | 10.58% | -4.19% | 1.136 |

## Walk-forward (8 windows)

- Profitable windows: **0.88** (target ≥ 0.75)
- Max window drawdown: **15.9%** (cap 25%)
- Pass: **YES**

## Hold / trade diagnostics (per ticker)

- Portfolio median hold: **20.5 days** (target ≥ 3d, V2 spec §1)
- Total trades across tickers: 906

| Ticker | Bars | Trades | Med hold (d) | Final eq | Sharpe (full) |
|--------|-----:|-------:|-------------:|---------:|--------------:|
| SPY | 3088 | 86 | 24.0 | 2.735 | 0.714 |
| QQQ | 3088 | 66 | 34.5 | 2.988 | 0.702 |
| DIA | 3088 | 101 | 24.0 | 2.338 | 0.616 |
| IWM | 3088 | 88 | 28.5 | 2.083 | 0.447 |
| GLD | 3088 | 61 | 21.0 | 1.334 | 0.291 |
| SLV | 3088 | 56 | 20.0 | 1.690 | 0.343 |
| USO | 3088 | 26 | 20.0 | 1.458 | 0.279 |
| UNG | 3088 | 10 | 12.5 | 0.680 | -0.172 |
| TLT | 3088 | 190 | 16.0 | 0.442 | -0.453 |
| HYG | 3088 | 222 | 10.0 | 0.766 | -0.270 |

## Cost model (Pepperstone Razor retail, Share CFD)

- Spread half: 2.0 bps | Slippage: 1.0 bps/side | Swap long: 0.0050%/day | Swap short: 0.0020%/day
- Weighting: equal_weight_1_over_N
- Citation: pepperstone razor tier (Phase 3.5a-V2 spec §3)

## Subset-gate verdict (per-config; PBO/DSR at aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | -0.217 | ❌ |
| fwd_sharpe_gt_0 | 1.527 | ✅ |
| wf_pass | 6/8 | ✅ |
| median_hold_ge_3d | 20.5d | ✅ |
| oos_cagr_ge_30pct | -1.8% | ❌ |
| oos_sharpe_ge_2 | -0.217 | ❌ |
| oos_maxdd_le_25pct | -14.7% | ✅ |

**Failed gates:** oos_sharpe_gt_0, oos_cagr_ge_30pct, oos_sharpe_ge_2

## Citations

- Donchian channel breakout 20/10 canonical: `[trading_systems_methods, p.353]`.
- Chandelier trailing ATR exit: `[volatility_trading]`.
- 1/N multi-asset trend-follow discipline: `[trend_following_covel]`.
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`.
- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.
