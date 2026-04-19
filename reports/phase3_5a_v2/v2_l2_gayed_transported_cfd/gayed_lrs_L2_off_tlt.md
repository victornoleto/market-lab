# V2-L2 Gayed-CFD rotation — `gayed_lrs_L2_off_tlt` (iter 35)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (3 gates)
**Config:** signal=lrs, leverage=2x, off-regime=tlt, risk-on=SPY,QQQ, daily close rebalance
**Window:** 2001-05-14 → 2026-04-14 (6266 bars, 578 regime switches)

## Split metrics

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2001-05-14 → 2017-12-31 | 4185 | 2.171 | 59.14% | -17.75% | 2244.224 |
| OOS | 2018-01-01 → 2023-12-31 | 1509 | 1.911 | 64.11% | -26.15% | 19.421 |
| FWD | 2024-01-01 → 2026-04-14 | 572 | 1.760 | 53.00% | -14.72% | 2.625 |

## Walk-forward (8 windows)

- Profitable windows: **1.00** (target ≥ 0.75)
- Max window drawdown: **26.2%** (cap 25%)
- Pass: **NO**

## Hold / switch diagnostics

- Median hold: **5.5 days** (target ≥ 3d, V2 spec §1)
- Total regime switches: 578
- Switches by ticker: SPY=287, QQQ=291

## Cost breakdown (Pepperstone Razor retail)

- Cumulative transaction cost: **118.048%** of starting equity
- Cumulative overnight swap: **-44.275%** of starting equity
- Spread half: 2.0 bps | commission RT: 6.6 bps | slippage RT: 3.0 bps | swap daily long: -0.0050%

## Subset-gate verdict (per-config; PBO/DSR deferred to aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 1.911 | ✅ |
| fwd_sharpe_gt_0 | 1.760 | ✅ |
| wf_pass | 6/8 | ❌ |
| median_hold_ge_3d | 5.5d | ✅ |
| oos_cagr_ge_30pct | 64.1% | ✅ |
| oos_sharpe_ge_2 | 1.911 | ❌ |
| oos_maxdd_le_25pct | -26.2% | ❌ |

**Failed gates:** wf_pass, oos_sharpe_ge_2, oos_maxdd_le_25pct

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
