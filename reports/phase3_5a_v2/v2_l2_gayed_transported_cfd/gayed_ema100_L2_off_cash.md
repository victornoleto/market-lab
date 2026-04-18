# V2-L2 Gayed-CFD rotation — `gayed_ema100_L2_off_cash` (iter 25)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ✅ PASS subset
**Config:** signal=ema100, leverage=2x, off-regime=cash, risk-on=SPY,QQQ, daily close rebalance
**Window:** 2001-05-14 → 2026-04-14 (6266 bars, 616 regime switches)

## Split metrics

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2001-05-14 → 2017-12-31 | 4185 | 1.999 | 52.05% | -12.34% | 1053.174 |
| OOS | 2018-01-01 → 2023-12-31 | 1509 | 2.171 | 68.96% | -20.13% | 23.121 |
| FWD | 2024-01-01 → 2026-04-14 | 572 | 1.936 | 59.00% | -13.98% | 2.865 |

## Walk-forward (8 windows)

- Profitable windows: **1.00** (target ≥ 0.75)
- Max window drawdown: **20.1%** (cap 25%)
- Pass: **YES**

## Hold / switch diagnostics

- Median hold: **6.0 days** (target ≥ 3d, V2 spec §1)
- Total regime switches: 616
- Switches by ticker: SPY=315, QQQ=301

## Cost breakdown (Pepperstone Razor retail)

- Cumulative transaction cost: **125.800%** of starting equity
- Cumulative overnight swap: **-44.930%** of starting equity
- Spread half: 2.0 bps | commission RT: 6.6 bps | slippage RT: 3.0 bps | swap daily long: -0.0050%

## Subset-gate verdict (per-config; PBO/DSR deferred to aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 2.171 | ✅ |
| fwd_sharpe_gt_0 | 1.936 | ✅ |
| wf_pass | 6/8 | ✅ |
| median_hold_ge_3d | 6.0d | ✅ |
| oos_cagr_ge_30pct | 69.0% | ✅ |
| oos_sharpe_ge_2 | 2.171 | ✅ |
| oos_maxdd_le_25pct | -20.1% | ✅ |

**All subset gates passed.** Final PASS requires aggregator PBO/DSR verdict.

## Last-bar positions

| Leg | Weight |
|-----|------:|
| SPY | 1.0000 |
| QQQ | 1.0000 |

## Citations

- Regime rotation + MA filter + leverage discipline: `[leverage_for_the_long_run, p.7, p.11, p.13, p.14, p.16, p.17, p.21]`.
- Leverage cap cross-check via PoR: `[leverage_space, Vince]`, `[math_money_mgmt, Vince]`.
- Carver CFD cost model + risk budget: `[systematic_trading, ch.8-9]`.
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`.
- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.
