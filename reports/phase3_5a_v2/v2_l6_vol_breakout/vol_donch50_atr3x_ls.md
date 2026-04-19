# V2-L6 vol breakout — `vol_donch50_atr3x_ls` (iter 73)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (3 gates)
**Config:** Donchian entry=50d, exit=trailing_atr_3x (ATR 3.0× on 20d), direction=long/short
**Universe:** SPY, QQQ, DIA, IWM, GLD, SLV, USO, UNG, TLT, HYG (10/10 active)
**Window:** 2014-01-02 → 2026-04-14 (3088 bars, equal-weight 1/N)

## Split metrics (portfolio)

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2014-01-02 → 2021-12-31 | 2015 | 0.250 | 1.97% | -24.01% | 1.169 |
| OOS | 2022-01-01 → 2024-12-31 | 753 | -0.677 | -3.86% | -14.74% | 0.889 |
| FWD | 2025-01-01 → 2026-04-14 | 320 | 0.851 | 5.99% | -4.81% | 1.077 |

## Walk-forward (8 windows)

- Profitable windows: **0.75** (target ≥ 0.75)
- Max window drawdown: **24.0%** (cap 25%)
- Pass: **YES**

## Hold / trade diagnostics (per ticker)

- Portfolio median hold: **23.0 days** (target ≥ 3d, V2 spec §1)
- Total trades across tickers: 910

| Ticker | Bars | Trades | Med hold (d) | Final eq | Sharpe (full) |
|--------|-----:|-------:|-------------:|---------:|--------------:|
| SPY | 3088 | 87 | 24.0 | 2.033 | 0.543 |
| QQQ | 3088 | 66 | 28.0 | 2.127 | 0.495 |
| DIA | 3088 | 99 | 23.0 | 1.564 | 0.360 |
| IWM | 3088 | 86 | 28.0 | 1.678 | 0.349 |
| GLD | 3088 | 59 | 22.0 | 1.365 | 0.312 |
| SLV | 3088 | 65 | 21.0 | 0.750 | -0.050 |
| USO | 3088 | 45 | 23.0 | 0.592 | 0.088 |
| UNG | 3088 | 8 | 173.5 | -2.877 | -0.124 |
| TLT | 3088 | 176 | 16.5 | 0.461 | -0.458 |
| HYG | 3088 | 219 | 10.0 | 0.764 | -0.274 |

## Cost model (Pepperstone Razor retail, Share CFD)

- Spread half: 2.0 bps | Slippage: 1.0 bps/side | Swap long: 0.0050%/day | Swap short: 0.0020%/day
- Weighting: equal_weight_1_over_N
- Citation: pepperstone razor tier (Phase 3.5a-V2 spec §3)

## Subset-gate verdict (per-config; PBO/DSR at aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | -0.677 | ❌ |
| fwd_sharpe_gt_0 | 0.851 | ✅ |
| wf_pass | 6/8 | ✅ |
| median_hold_ge_3d | 23.0d | ✅ |
| oos_cagr_ge_30pct | -3.9% | ❌ |
| oos_sharpe_ge_2 | -0.677 | ❌ |
| oos_maxdd_le_25pct | -14.7% | ✅ |

**Failed gates:** oos_sharpe_gt_0, oos_cagr_ge_30pct, oos_sharpe_ge_2

## Citations

- Donchian channel breakout 20/10 canonical: `[trading_systems_methods, p.353]`.
- Chandelier trailing ATR exit: `[volatility_trading]`.
- 1/N multi-asset trend-follow discipline: `[trend_following_covel]`.
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`.
- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.
