# V2-L6 vol breakout — `vol_donch50_atr3x_long` (iter 72)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (3 gates)
**Config:** Donchian entry=50d, exit=trailing_atr_3x (ATR 3.0× on 20d), direction=long-only
**Universe:** SPY, QQQ, DIA, IWM, GLD, SLV, USO, UNG, TLT, HYG (10/10 active)
**Window:** 2014-01-02 → 2026-04-14 (3088 bars, equal-weight 1/N)

## Split metrics (portfolio)

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2014-01-02 → 2021-12-31 | 2015 | 0.696 | 3.56% | -8.38% | 1.323 |
| OOS | 2022-01-01 → 2024-12-31 | 753 | -0.249 | -1.55% | -12.36% | 0.955 |
| FWD | 2025-01-01 → 2026-04-14 | 320 | 1.945 | 11.57% | -4.42% | 1.149 |

## Walk-forward (8 windows)

- Profitable windows: **0.75** (target ≥ 0.75)
- Max window drawdown: **13.3%** (cap 25%)
- Pass: **YES**

## Hold / trade diagnostics (per ticker)

- Portfolio median hold: **21.2 days** (target ≥ 3d, V2 spec §1)
- Total trades across tickers: 814

| Ticker | Bars | Trades | Med hold (d) | Final eq | Sharpe (full) |
|--------|-----:|-------:|-------------:|---------:|--------------:|
| SPY | 3088 | 85 | 24.0 | 2.111 | 0.585 |
| QQQ | 3088 | 58 | 35.5 | 2.961 | 0.776 |
| DIA | 3088 | 97 | 24.0 | 1.717 | 0.429 |
| IWM | 3088 | 82 | 29.5 | 1.680 | 0.369 |
| GLD | 3088 | 36 | 22.0 | 1.666 | 0.553 |
| SLV | 3088 | 36 | 20.5 | 1.625 | 0.353 |
| USO | 3088 | 19 | 20.0 | 1.413 | 0.299 |
| UNG | 3088 | 6 | 15.0 | 0.907 | -0.042 |
| TLT | 3088 | 176 | 16.5 | 0.461 | -0.458 |
| HYG | 3088 | 219 | 10.0 | 0.764 | -0.274 |

## Cost model (Pepperstone Razor retail, Share CFD)

- Spread half: 2.0 bps | Slippage: 1.0 bps/side | Swap long: 0.0050%/day | Swap short: 0.0020%/day
- Weighting: equal_weight_1_over_N
- Citation: pepperstone razor tier (Phase 3.5a-V2 spec §3)

## Subset-gate verdict (per-config; PBO/DSR at aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | -0.249 | ❌ |
| fwd_sharpe_gt_0 | 1.945 | ✅ |
| wf_pass | 6/8 | ✅ |
| median_hold_ge_3d | 21.2d | ✅ |
| oos_cagr_ge_30pct | -1.5% | ❌ |
| oos_sharpe_ge_2 | -0.249 | ❌ |
| oos_maxdd_le_25pct | -12.4% | ✅ |

**Failed gates:** oos_sharpe_gt_0, oos_cagr_ge_30pct, oos_sharpe_ge_2

## Citations

- Donchian channel breakout 20/10 canonical: `[trading_systems_methods, p.353]`.
- Chandelier trailing ATR exit: `[volatility_trading]`.
- 1/N multi-asset trend-follow discipline: `[trend_following_covel]`.
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`.
- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.
