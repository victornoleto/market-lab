# V2-L6 vol breakout — `vol_donch100_opp_ls` (iter 79)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (4 gates)
**Config:** Donchian entry=100d, exit=opposite_channel (opposite 50d channel), direction=long/short
**Universe:** SPY, QQQ, DIA, IWM, GLD, SLV, USO, UNG, TLT, HYG (10/10 active)
**Window:** 2014-01-02 → 2026-04-14 (3088 bars, equal-weight 1/N)

## Split metrics (portfolio)

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2014-01-02 → 2021-12-31 | 2015 | 0.237 | 1.92% | -26.79% | 1.164 |
| OOS | 2022-01-01 → 2024-12-31 | 753 | -0.550 | -3.24% | -13.21% | 0.906 |
| FWD | 2025-01-01 → 2026-04-14 | 320 | 0.945 | 8.40% | -5.86% | 1.108 |

## Walk-forward (8 windows)

- Profitable windows: **0.75** (target ≥ 0.75)
- Max window drawdown: **26.8%** (cap 25%)
- Pass: **NO**

## Hold / trade diagnostics (per ticker)

- Portfolio median hold: **52.2 days** (target ≥ 3d, V2 spec §1)
- Total trades across tickers: 419

| Ticker | Bars | Trades | Med hold (d) | Final eq | Sharpe (full) |
|--------|-----:|-------:|-------------:|---------:|--------------:|
| SPY | 3088 | 42 | 51.5 | 1.946 | 0.512 |
| QQQ | 3088 | 36 | 78.0 | 1.809 | 0.393 |
| DIA | 3088 | 47 | 45.0 | 1.701 | 0.423 |
| IWM | 3088 | 39 | 71.0 | 0.975 | 0.065 |
| GLD | 3088 | 31 | 53.0 | 1.779 | 0.462 |
| SLV | 3088 | 31 | 31.0 | 1.065 | 0.141 |
| USO | 3088 | 29 | 100.0 | 0.493 | 0.209 |
| UNG | 3088 | 8 | 173.5 | -2.927 | -0.149 |
| TLT | 3088 | 67 | 18.0 | 0.538 | -0.351 |
| HYG | 3088 | 89 | 15.0 | 0.713 | -0.336 |

## Cost model (Pepperstone Razor retail, Share CFD)

- Spread half: 2.0 bps | Slippage: 1.0 bps/side | Swap long: 0.0050%/day | Swap short: 0.0020%/day
- Weighting: equal_weight_1_over_N
- Citation: pepperstone razor tier (Phase 3.5a-V2 spec §3)

## Subset-gate verdict (per-config; PBO/DSR at aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | -0.550 | ❌ |
| fwd_sharpe_gt_0 | 0.945 | ✅ |
| wf_pass | 6/8 | ❌ |
| median_hold_ge_3d | 52.2d | ✅ |
| oos_cagr_ge_30pct | -3.2% | ❌ |
| oos_sharpe_ge_2 | -0.550 | ❌ |
| oos_maxdd_le_25pct | -13.2% | ✅ |

**Failed gates:** oos_sharpe_gt_0, wf_pass, oos_cagr_ge_30pct, oos_sharpe_ge_2

## Citations

- Donchian channel breakout 20/10 canonical: `[trading_systems_methods, p.353]`.
- Chandelier trailing ATR exit: `[volatility_trading]`.
- 1/N multi-asset trend-follow discipline: `[trend_following_covel]`.
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`.
- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.
