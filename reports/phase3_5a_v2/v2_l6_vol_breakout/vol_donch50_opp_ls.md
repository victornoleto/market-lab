# V2-L6 vol breakout — `vol_donch50_opp_ls` (iter 75)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (4 gates)
**Config:** Donchian entry=50d, exit=opposite_channel (opposite 25d channel), direction=long/short
**Universe:** SPY, QQQ, DIA, IWM, GLD, SLV, USO, UNG, TLT, HYG (10/10 active)
**Window:** 2014-01-02 → 2026-04-14 (3088 bars, equal-weight 1/N)

## Split metrics (portfolio)

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2014-01-02 → 2021-12-31 | 2015 | 0.265 | 2.16% | -25.96% | 1.186 |
| OOS | 2022-01-01 → 2024-12-31 | 753 | -0.584 | -3.99% | -16.75% | 0.885 |
| FWD | 2025-01-01 → 2026-04-14 | 320 | 1.003 | 9.43% | -6.03% | 1.121 |

## Walk-forward (8 windows)

- Profitable windows: **0.75** (target ≥ 0.75)
- Max window drawdown: **26.0%** (cap 25%)
- Pass: **NO**

## Hold / trade diagnostics (per ticker)

- Portfolio median hold: **43.5 days** (target ≥ 3d, V2 spec §1)
- Total trades across tickers: 496

| Ticker | Bars | Trades | Med hold (d) | Final eq | Sharpe (full) |
|--------|-----:|-------:|-------------:|---------:|--------------:|
| SPY | 3088 | 49 | 49.0 | 1.893 | 0.475 |
| QQQ | 3088 | 47 | 44.0 | 2.037 | 0.446 |
| DIA | 3088 | 55 | 30.0 | 1.674 | 0.395 |
| IWM | 3088 | 45 | 61.0 | 1.390 | 0.243 |
| GLD | 3088 | 46 | 43.0 | 1.761 | 0.437 |
| SLV | 3088 | 53 | 29.0 | 0.679 | -0.013 |
| USO | 3088 | 39 | 61.0 | 0.602 | 0.105 |
| UNG | 3088 | 8 | 173.5 | -2.877 | -0.124 |
| TLT | 3088 | 66 | 21.0 | 0.643 | -0.211 |
| HYG | 3088 | 88 | 15.0 | 0.718 | -0.328 |

## Cost model (Pepperstone Razor retail, Share CFD)

- Spread half: 2.0 bps | Slippage: 1.0 bps/side | Swap long: 0.0050%/day | Swap short: 0.0020%/day
- Weighting: equal_weight_1_over_N
- Citation: pepperstone razor tier (Phase 3.5a-V2 spec §3)

## Subset-gate verdict (per-config; PBO/DSR at aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | -0.584 | ❌ |
| fwd_sharpe_gt_0 | 1.003 | ✅ |
| wf_pass | 6/8 | ❌ |
| median_hold_ge_3d | 43.5d | ✅ |
| oos_cagr_ge_30pct | -4.0% | ❌ |
| oos_sharpe_ge_2 | -0.584 | ❌ |
| oos_maxdd_le_25pct | -16.8% | ✅ |

**Failed gates:** oos_sharpe_gt_0, wf_pass, oos_cagr_ge_30pct, oos_sharpe_ge_2

## Citations

- Donchian channel breakout 20/10 canonical: `[trading_systems_methods, p.353]`.
- Chandelier trailing ATR exit: `[volatility_trading]`.
- 1/N multi-asset trend-follow discipline: `[trend_following_covel]`.
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`.
- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.
