# V2-L6 vol breakout — `vol_donch100_atr3x_ls` (iter 77)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (4 gates)
**Config:** Donchian entry=100d, exit=trailing_atr_3x (ATR 3.0× on 20d), direction=long/short
**Universe:** SPY, QQQ, DIA, IWM, GLD, SLV, USO, UNG, TLT, HYG (10/10 active)
**Window:** 2014-01-02 → 2026-04-14 (3088 bars, equal-weight 1/N)

## Split metrics (portfolio)

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2014-01-02 → 2021-12-31 | 2015 | 0.239 | 1.87% | -25.08% | 1.159 |
| OOS | 2022-01-01 → 2024-12-31 | 753 | -0.644 | -2.99% | -11.94% | 0.913 |
| FWD | 2025-01-01 → 2026-04-14 | 320 | 1.139 | 7.09% | -3.69% | 1.091 |

## Walk-forward (8 windows)

- Profitable windows: **0.62** (target ≥ 0.75)
- Max window drawdown: **25.1%** (cap 25%)
- Pass: **NO**

## Hold / trade diagnostics (per ticker)

- Portfolio median hold: **22.5 days** (target ≥ 3d, V2 spec §1)
- Total trades across tickers: 811

| Ticker | Bars | Trades | Med hold (d) | Final eq | Sharpe (full) |
|--------|-----:|-------:|-------------:|---------:|--------------:|
| SPY | 3088 | 82 | 22.0 | 1.763 | 0.465 |
| QQQ | 3088 | 56 | 36.5 | 2.236 | 0.549 |
| DIA | 3088 | 94 | 23.0 | 1.313 | 0.252 |
| IWM | 3088 | 79 | 27.0 | 1.442 | 0.284 |
| GLD | 3088 | 42 | 21.0 | 1.419 | 0.383 |
| SLV | 3088 | 40 | 19.5 | 1.468 | 0.288 |
| USO | 3088 | 34 | 46.0 | 0.473 | 0.191 |
| UNG | 3088 | 8 | 173.5 | -2.927 | -0.149 |
| TLT | 3088 | 160 | 16.0 | 0.462 | -0.497 |
| HYG | 3088 | 216 | 10.0 | 0.766 | -0.271 |

## Cost model (Pepperstone Razor retail, Share CFD)

- Spread half: 2.0 bps | Slippage: 1.0 bps/side | Swap long: 0.0050%/day | Swap short: 0.0020%/day
- Weighting: equal_weight_1_over_N
- Citation: pepperstone razor tier (Phase 3.5a-V2 spec §3)

## Subset-gate verdict (per-config; PBO/DSR at aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | -0.644 | ❌ |
| fwd_sharpe_gt_0 | 1.139 | ✅ |
| wf_pass | 6/8 | ❌ |
| median_hold_ge_3d | 22.5d | ✅ |
| oos_cagr_ge_30pct | -3.0% | ❌ |
| oos_sharpe_ge_2 | -0.644 | ❌ |
| oos_maxdd_le_25pct | -11.9% | ✅ |

**Failed gates:** oos_sharpe_gt_0, wf_pass, oos_cagr_ge_30pct, oos_sharpe_ge_2

## Citations

- Donchian channel breakout 20/10 canonical: `[trading_systems_methods, p.353]`.
- Chandelier trailing ATR exit: `[volatility_trading]`.
- 1/N multi-asset trend-follow discipline: `[trend_following_covel]`.
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`.
- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.
