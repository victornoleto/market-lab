# V2-L6 vol breakout — `vol_donch20_opp_ls` (iter 71)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (4 gates)
**Config:** Donchian entry=20d, exit=opposite_channel (opposite 10d channel), direction=long/short
**Universe:** SPY, QQQ, DIA, IWM, GLD, SLV, USO, UNG, TLT, HYG (10/10 active)
**Window:** 2014-01-02 → 2026-04-14 (3088 bars, equal-weight 1/N)

## Split metrics (portfolio)

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2014-01-02 → 2021-12-31 | 2015 | 0.316 | 2.92% | -28.71% | 1.258 |
| OOS | 2022-01-01 → 2024-12-31 | 753 | -0.728 | -5.51% | -17.51% | 0.844 |
| FWD | 2025-01-01 → 2026-04-14 | 320 | 0.599 | 5.35% | -5.91% | 1.068 |

## Walk-forward (8 windows)

- Profitable windows: **0.75** (target ≥ 0.75)
- Max window drawdown: **28.7%** (cap 25%)
- Pass: **NO**

## Hold / trade diagnostics (per ticker)

- Portfolio median hold: **31.5 days** (target ≥ 3d, V2 spec §1)
- Total trades across tickers: 659

| Ticker | Bars | Trades | Med hold (d) | Final eq | Sharpe (full) |
|--------|-----:|-------:|-------------:|---------:|--------------:|
| SPY | 3088 | 51 | 52.0 | 2.132 | 0.520 |
| QQQ | 3088 | 58 | 32.5 | 1.809 | 0.369 |
| DIA | 3088 | 53 | 46.0 | 2.280 | 0.573 |
| IWM | 3088 | 53 | 35.0 | 1.454 | 0.258 |
| GLD | 3088 | 106 | 20.0 | 0.863 | -0.035 |
| SLV | 3088 | 108 | 22.0 | 0.541 | -0.090 |
| USO | 3088 | 58 | 30.5 | 1.004 | 0.243 |
| UNG | 3088 | 9 | 172.0 | -4.273 | -0.143 |
| TLT | 3088 | 74 | 21.5 | 0.665 | -0.174 |
| HYG | 3088 | 89 | 15.0 | 0.727 | -0.314 |

## Cost model (Pepperstone Razor retail, Share CFD)

- Spread half: 2.0 bps | Slippage: 1.0 bps/side | Swap long: 0.0050%/day | Swap short: 0.0020%/day
- Weighting: equal_weight_1_over_N
- Citation: pepperstone razor tier (Phase 3.5a-V2 spec §3)

## Subset-gate verdict (per-config; PBO/DSR at aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | -0.728 | ❌ |
| fwd_sharpe_gt_0 | 0.599 | ✅ |
| wf_pass | 6/8 | ❌ |
| median_hold_ge_3d | 31.5d | ✅ |
| oos_cagr_ge_30pct | -5.5% | ❌ |
| oos_sharpe_ge_2 | -0.728 | ❌ |
| oos_maxdd_le_25pct | -17.5% | ✅ |

**Failed gates:** oos_sharpe_gt_0, wf_pass, oos_cagr_ge_30pct, oos_sharpe_ge_2

## Citations

- Donchian channel breakout 20/10 canonical: `[trading_systems_methods, p.353]`.
- Chandelier trailing ATR exit: `[volatility_trading]`.
- 1/N multi-asset trend-follow discipline: `[trend_following_covel]`.
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`.
- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.
