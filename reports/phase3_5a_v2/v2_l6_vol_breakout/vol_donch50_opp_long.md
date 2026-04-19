# V2-L6 vol breakout — `vol_donch50_opp_long` (iter 74)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (3 gates)
**Config:** Donchian entry=50d, exit=opposite_channel (opposite 25d channel), direction=long-only
**Universe:** SPY, QQQ, DIA, IWM, GLD, SLV, USO, UNG, TLT, HYG (10/10 active)
**Window:** 2014-01-02 → 2026-04-14 (3088 bars, equal-weight 1/N)

## Split metrics (portfolio)

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2014-01-02 → 2021-12-31 | 2015 | 0.722 | 4.07% | -8.43% | 1.376 |
| OOS | 2022-01-01 → 2024-12-31 | 753 | -0.254 | -1.97% | -12.96% | 0.942 |
| FWD | 2025-01-01 → 2026-04-14 | 320 | 1.756 | 16.48% | -6.03% | 1.214 |

## Walk-forward (8 windows)

- Profitable windows: **0.88** (target ≥ 0.75)
- Max window drawdown: **15.1%** (cap 25%)
- Pass: **YES**

## Hold / trade diagnostics (per ticker)

- Portfolio median hold: **44.2 days** (target ≥ 3d, V2 spec §1)
- Total trades across tickers: 407

| Ticker | Bars | Trades | Med hold (d) | Final eq | Sharpe (full) |
|--------|-----:|-------:|-------------:|---------:|--------------:|
| SPY | 3088 | 47 | 51.0 | 2.054 | 0.546 |
| QQQ | 3088 | 39 | 56.0 | 3.186 | 0.752 |
| DIA | 3088 | 53 | 31.0 | 1.838 | 0.461 |
| IWM | 3088 | 41 | 66.0 | 1.567 | 0.318 |
| GLD | 3088 | 26 | 64.5 | 2.077 | 0.598 |
| SLV | 3088 | 30 | 29.0 | 1.205 | 0.182 |
| USO | 3088 | 13 | 48.0 | 1.896 | 0.413 |
| UNG | 3088 | 4 | 40.5 | 0.878 | -0.012 |
| TLT | 3088 | 66 | 21.0 | 0.643 | -0.211 |
| HYG | 3088 | 88 | 15.0 | 0.718 | -0.328 |

## Cost model (Pepperstone Razor retail, Share CFD)

- Spread half: 2.0 bps | Slippage: 1.0 bps/side | Swap long: 0.0050%/day | Swap short: 0.0020%/day
- Weighting: equal_weight_1_over_N
- Citation: pepperstone razor tier (Phase 3.5a-V2 spec §3)

## Subset-gate verdict (per-config; PBO/DSR at aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | -0.254 | ❌ |
| fwd_sharpe_gt_0 | 1.756 | ✅ |
| wf_pass | 6/8 | ✅ |
| median_hold_ge_3d | 44.2d | ✅ |
| oos_cagr_ge_30pct | -2.0% | ❌ |
| oos_sharpe_ge_2 | -0.254 | ❌ |
| oos_maxdd_le_25pct | -13.0% | ✅ |

**Failed gates:** oos_sharpe_gt_0, oos_cagr_ge_30pct, oos_sharpe_ge_2

## Citations

- Donchian channel breakout 20/10 canonical: `[trading_systems_methods, p.353]`.
- Chandelier trailing ATR exit: `[volatility_trading]`.
- 1/N multi-asset trend-follow discipline: `[trend_following_covel]`.
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`.
- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.
