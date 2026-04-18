# V2-L1 TSMOM multi-asset — `tsmom_lb12m_vt15` (iter 3)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (5 gates)
**Config:** lookback=252d, vol_target=15%, binary long/flat, monthly EOM rebalance, 30-asset universe
**Window:** 2001-05-14 → 2026-04-17 (6386 bars, 300 rebalances)

## Split metrics

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2001-05-14 → 2017-12-31 | 4221 | -0.321 | -2.88% | -44.83% | 0.613 |
| OOS | 2018-01-01 → 2023-12-31 | 1565 | -0.248 | -0.80% | -13.67% | 0.951 |
| FWD | 2024-01-01 → 2026-04-14 | 597 | -1.469 | -9.48% | -24.46% | 0.790 |

## Walk-forward (8 windows)

- Profitable windows: **0.12** (target ≥ 0.75)
- Max window drawdown: **25.9%** (cap 25%)
- Pass: **NO**

## Hold / trade diagnostics

- Median hold: **159.5 days** (target ≥ 3d, V2 spec §1)
- Long bar-positions: 24,643
- Rebalances: 300

## Cost breakdown

- Cumulative transaction cost: **2.855%** of starting equity
- Cumulative overnight swap: **135.206%** of starting equity
- Daily swap (long): 5.0 bps | round-trip: ETF 10.0 bps, FX 8.0 bps, commodity-ETF 13.0 bps, crypto 20.0 bps

## Subset-gate verdict (per-config; PBO/DSR deferred to aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | -0.248 | ❌ |
| fwd_sharpe_gt_0 | -1.469 | ❌ |
| wf_pass | 6/8 | ❌ |
| median_hold_ge_3d | 159.5d | ✅ |
| oos_cagr_ge_30pct | -0.8% | ❌ |
| oos_sharpe_ge_2 | -0.248 | ❌ |
| oos_maxdd_le_25pct | -13.7% | ✅ |

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
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`, Pardo (2008) ch.10-11, ai-trade gate convention.
- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.
