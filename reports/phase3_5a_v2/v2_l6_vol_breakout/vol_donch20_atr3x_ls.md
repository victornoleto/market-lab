# V2-L6 vol breakout — `vol_donch20_atr3x_ls` (iter 69)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (4 gates)
**Config:** Donchian entry=20d, exit=trailing_atr_3x (ATR 3.0× on 20d), direction=long/short
**Universe:** SPY, QQQ, DIA, IWM, GLD, SLV, USO, UNG, TLT, HYG (10/10 active)
**Window:** 2014-01-02 → 2026-04-14 (3088 bars, equal-weight 1/N)

## Split metrics (portfolio)

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2014-01-02 → 2021-12-31 | 2015 | 0.289 | 2.58% | -28.06% | 1.226 |
| OOS | 2022-01-01 → 2024-12-31 | 753 | -0.621 | -4.49% | -18.57% | 0.872 |
| FWD | 2025-01-01 → 2026-04-14 | 320 | 0.968 | 8.14% | -5.15% | 1.105 |

## Walk-forward (8 windows)

- Profitable windows: **0.75** (target ≥ 0.75)
- Max window drawdown: **27.8%** (cap 25%)
- Pass: **NO**

## Hold / trade diagnostics (per ticker)

- Portfolio median hold: **24.0 days** (target ≥ 3d, V2 spec §1)
- Total trades across tickers: 1031

| Ticker | Bars | Trades | Med hold (d) | Final eq | Sharpe (full) |
|--------|-----:|-------:|-------------:|---------:|--------------:|
| SPY | 3088 | 89 | 24.0 | 2.556 | 0.653 |
| QQQ | 3088 | 77 | 26.0 | 2.123 | 0.458 |
| DIA | 3088 | 103 | 24.0 | 2.130 | 0.547 |
| IWM | 3088 | 93 | 28.0 | 2.040 | 0.418 |
| GLD | 3088 | 97 | 21.0 | 0.980 | 0.045 |
| SLV | 3088 | 97 | 22.0 | 0.702 | -0.016 |
| USO | 3088 | 54 | 38.5 | 0.864 | 0.207 |
| UNG | 3088 | 9 | 172.0 | -4.273 | -0.143 |
| TLT | 3088 | 190 | 16.0 | 0.441 | -0.453 |
| HYG | 3088 | 222 | 10.0 | 0.766 | -0.270 |

## Cost model (Pepperstone Razor retail, Share CFD)

- Spread half: 2.0 bps | Slippage: 1.0 bps/side | Swap long: 0.0050%/day | Swap short: 0.0020%/day
- Weighting: equal_weight_1_over_N
- Citation: pepperstone razor tier (Phase 3.5a-V2 spec §3)

## Subset-gate verdict (per-config; PBO/DSR at aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | -0.621 | ❌ |
| fwd_sharpe_gt_0 | 0.968 | ✅ |
| wf_pass | 6/8 | ❌ |
| median_hold_ge_3d | 24.0d | ✅ |
| oos_cagr_ge_30pct | -4.5% | ❌ |
| oos_sharpe_ge_2 | -0.621 | ❌ |
| oos_maxdd_le_25pct | -18.6% | ✅ |

**Failed gates:** oos_sharpe_gt_0, wf_pass, oos_cagr_ge_30pct, oos_sharpe_ge_2

## Citations

- Donchian channel breakout 20/10 canonical: `[trading_systems_methods, p.353]`.
- Chandelier trailing ATR exit: `[volatility_trading]`.
- 1/N multi-asset trend-follow discipline: `[trend_following_covel]`.
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`.
- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.
