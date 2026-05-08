# V2-L1 TSMOM multi-asset — `tsmom_lb06m_vt15` (iter 9)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (5 gates)
**Config:** lookback=126d, vol_target=15%, binary long/flat, monthly EOM rebalance, 30-asset universe
**Window:** 2001-05-14 → 2026-04-17 (6386 bars, 300 rebalances)

## Split metrics

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2001-05-14 → 2017-12-31 | 4221 | -0.200 | -1.45% | -32.97% | 0.784 |
| OOS | 2018-01-01 → 2023-12-31 | 1565 | -0.285 | -0.83% | -11.50% | 0.949 |
| FWD | 2024-01-01 → 2026-04-14 | 597 | -2.033 | -12.13% | -28.52% | 0.736 |

## Walk-forward (8 windows)

- Profitable windows: **0.25** (target ≥ 0.75)
- Max window drawdown: **26.2%** (cap 25%)
- Pass: **NO**

## Hold / trade diagnostics

- Median hold: **128.0 days** (target ≥ 3d, V2 spec §1)
- Long bar-positions: 23,347
- Rebalances: 300

## Cost breakdown

- Cumulative transaction cost: **3.569%** of starting equity
- Cumulative overnight swap: **118.666%** of starting equity
- Daily swap (long): 5.0 bps | round-trip: ETF 10.0 bps, FX 8.0 bps, commodity-ETF 13.0 bps, crypto 20.0 bps

## Subset-gate verdict (per-config; PBO/DSR deferred to aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | -0.285 | ❌ |
| fwd_sharpe_gt_0 | -2.033 | ❌ |
| wf_pass | 6/8 | ❌ |
| median_hold_ge_3d | 128.0d | ✅ |
| oos_cagr_ge_30pct | -0.8% | ❌ |
| oos_sharpe_ge_2 | -0.285 | ❌ |
| oos_maxdd_le_25pct | -11.5% | ✅ |

**Failed gates:** oos_sharpe_gt_0, fwd_sharpe_gt_0, wf_pass, oos_cagr_ge_30pct, oos_sharpe_ge_2

## Last-bar long positions

| Ticker | Weight |
|--------|------:|
| EURUSD | 0.6667 |
| GBPUSD | 0.6667 |
| USDJPY | 0.5471 |

## Citations

- Time-series momentum family: `[algo_trading_chan, p.133, ch.6]`, `[systematic_trading, ch.8-9]` (Carver), `[trend_following_covel, ch.5-6]`.
- Vol-target no-look-ahead sizing: `[advances_fin_ml, p.162-164]`.
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`, Pardo (2008) ch.10-11, market-lab gate convention.
- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.
