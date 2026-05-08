# V2-L6 vol breakout — `vol_donch20_opp_long` (iter 70)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (3 gates)
**Config:** Donchian entry=20d, exit=opposite_channel (opposite 10d channel), direction=long-only
**Universe:** SPY, QQQ, DIA, IWM, GLD, SLV, USO, UNG, TLT, HYG (10/10 active)
**Window:** 2014-01-02 → 2026-04-14 (3088 bars, equal-weight 1/N)

## Split metrics (portfolio)

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2014-01-02 → 2021-12-31 | 2015 | 0.904 | 5.59% | -9.34% | 1.544 |
| OOS | 2022-01-01 → 2024-12-31 | 753 | -0.355 | -2.99% | -17.04% | 0.913 |
| FWD | 2025-01-01 → 2026-04-14 | 320 | 1.393 | 11.42% | -6.19% | 1.147 |

## Walk-forward (8 windows)

- Profitable windows: **0.88** (target ≥ 0.75)
- Max window drawdown: **18.6%** (cap 25%)
- Pass: **YES**

## Hold / trade diagnostics (per ticker)

- Portfolio median hold: **23.5 days** (target ≥ 3d, V2 spec §1)
- Total trades across tickers: 502

| Ticker | Bars | Trades | Med hold (d) | Final eq | Sharpe (full) |
|--------|-----:|-------:|-------------:|---------:|--------------:|
| SPY | 3088 | 49 | 53.0 | 2.263 | 0.572 |
| QQQ | 3088 | 47 | 52.0 | 2.998 | 0.658 |
| DIA | 3088 | 51 | 51.0 | 2.503 | 0.639 |
| IWM | 3088 | 49 | 58.0 | 1.470 | 0.269 |
| GLD | 3088 | 57 | 21.0 | 1.477 | 0.349 |
| SLV | 3088 | 56 | 21.0 | 1.377 | 0.235 |
| USO | 3088 | 22 | 25.0 | 2.635 | 0.602 |
| UNG | 3088 | 9 | 19.0 | 0.690 | -0.119 |
| TLT | 3088 | 73 | 22.0 | 0.673 | -0.167 |
| HYG | 3088 | 89 | 15.0 | 0.727 | -0.314 |

## Cost model (Pepperstone Razor retail, Share CFD)

- Spread half: 2.0 bps | Slippage: 1.0 bps/side | Swap long: 0.0050%/day | Swap short: 0.0020%/day
- Weighting: equal_weight_1_over_N
- Citation: pepperstone razor tier (Phase 3.5a-V2 spec §3)

## Subset-gate verdict (per-config; PBO/DSR at aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | -0.355 | ❌ |
| fwd_sharpe_gt_0 | 1.393 | ✅ |
| wf_pass | 6/8 | ✅ |
| median_hold_ge_3d | 23.5d | ✅ |
| oos_cagr_ge_30pct | -3.0% | ❌ |
| oos_sharpe_ge_2 | -0.355 | ❌ |
| oos_maxdd_le_25pct | -17.0% | ✅ |

**Failed gates:** oos_sharpe_gt_0, oos_cagr_ge_30pct, oos_sharpe_ge_2

## Citations

- Donchian channel breakout 20/10 canonical: `[trading_systems_methods, p.353]`.
- Chandelier trailing ATR exit: `[volatility_trading]`.
- 1/N multi-asset trend-follow discipline: `[trend_following_covel]`.
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`.
- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.
