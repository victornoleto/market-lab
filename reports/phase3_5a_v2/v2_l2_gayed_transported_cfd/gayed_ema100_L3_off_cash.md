# V2-L2 Gayed-CFD rotation — `gayed_ema100_L3_off_cash` (iter 28)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (2 gates)
**Config:** signal=ema100, leverage=3x, off-regime=cash, risk-on=SPY,QQQ, daily close rebalance
**Window:** 2001-05-14 → 2026-04-14 (6266 bars, 616 regime switches)

## Split metrics

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2001-05-14 → 2017-12-31 | 4185 | 2.024 | 85.66% | -18.06% | 29014.755 |
| OOS | 2018-01-01 → 2023-12-31 | 1509 | 2.192 | 115.96% | -29.24% | 100.523 |
| FWD | 2024-01-01 → 2026-04-14 | 572 | 1.950 | 96.63% | -20.56% | 4.640 |

## Walk-forward (8 windows)

- Profitable windows: **1.00** (target ≥ 0.75)
- Max window drawdown: **29.2%** (cap 25%)
- Pass: **NO**

## Hold / switch diagnostics

- Median hold: **6.0 days** (target ≥ 3d, V2 spec §1)
- Total regime switches: 616
- Switches by ticker: SPY=315, QQQ=301

## Cost breakdown (Pepperstone Razor retail)

- Cumulative transaction cost: **167.688%** of starting equity
- Cumulative overnight swap: **-67.395%** of starting equity
- Spread half: 2.0 bps | commission RT: 6.6 bps | slippage RT: 3.0 bps | swap daily long: -0.0050%

## Subset-gate verdict (per-config; PBO/DSR deferred to aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 2.192 | ✅ |
| fwd_sharpe_gt_0 | 1.950 | ✅ |
| wf_pass | 6/8 | ❌ |
| median_hold_ge_3d | 6.0d | ✅ |
| oos_cagr_ge_30pct | 116.0% | ✅ |
| oos_sharpe_ge_2 | 2.192 | ✅ |
| oos_maxdd_le_25pct | -29.2% | ❌ |

**Failed gates:** wf_pass, oos_maxdd_le_25pct

## Last-bar positions

| Leg | Weight |
|-----|------:|
| SPY | 1.5000 |
| QQQ | 1.5000 |

## Citations

- Regime rotation + MA filter + leverage discipline: `[leverage_for_the_long_run, p.7, p.11, p.13, p.14, p.16, p.17, p.21]`.
- Leverage cap cross-check via PoR: `[leverage_space, Vince]`, `[math_money_mgmt, Vince]`.
- Carver CFD cost model + risk budget: `[systematic_trading, ch.8-9]`.
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`.
- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.
