# V2-L1 TSMOM multi-asset — `tsmom_lb01m_vt10` (iter 3)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (5 gates)
**Config:** lookback=21d, vol_target=10%, binary long/flat, monthly EOM rebalance, 30-asset universe
**Window:** 2001-05-14 → 2026-04-17 (6386 bars, 300 rebalances)

## Split metrics

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2001-05-14 → 2017-12-31 | 4221 | -0.382 | -1.59% | -25.28% | 0.765 |
| OOS | 2018-01-01 → 2023-12-31 | 1565 | -1.128 | -2.54% | -17.42% | 0.853 |
| FWD | 2024-01-01 → 2026-04-14 | 597 | -1.201 | -4.93% | -11.50% | 0.887 |

## Walk-forward (8 windows)

- Profitable windows: **0.00** (target ≥ 0.75)
- Max window drawdown: **14.4%** (cap 25%)
- Pass: **NO**

## Hold / trade diagnostics

- Median hold: **41.0 days** (target ≥ 3d, V2 spec §1)
- Long bar-positions: 20,869
- Rebalances: 300

## Cost breakdown

- Cumulative transaction cost: **6.247%** of starting equity
- Cumulative overnight swap: **73.751%** of starting equity
- Daily swap (long): 5.0 bps | round-trip: ETF 10.0 bps, FX 8.0 bps, commodity-ETF 13.0 bps, crypto 20.0 bps

## Subset-gate verdict (per-config; PBO/DSR deferred to aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | -1.128 | ❌ |
| fwd_sharpe_gt_0 | -1.201 | ❌ |
| wf_pass | 6/8 | ❌ |
| median_hold_ge_3d | 41.0d | ✅ |
| oos_cagr_ge_30pct | -2.5% | ❌ |
| oos_sharpe_ge_2 | -1.128 | ❌ |
| oos_maxdd_le_25pct | -17.4% | ✅ |

**Failed gates:** oos_sharpe_gt_0, fwd_sharpe_gt_0, wf_pass, oos_cagr_ge_30pct, oos_sharpe_ge_2

## Last-bar long positions

| Ticker | Weight |
|--------|------:|
| EURUSD | 0.4868 |
| GBPUSD | 0.4922 |
| USDJPY | 0.3648 |

## Citations

- Time-series momentum family: `[algo_trading_chan, p.133, ch.6]`, `[systematic_trading, ch.8-9]` (Carver), `[trend_following_covel, ch.5-6]`.
- Vol-target no-look-ahead sizing: `[advances_fin_ml, p.162-164]`.
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`, Pardo (2008) ch.10-11, ai-trade gate convention.
- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.
