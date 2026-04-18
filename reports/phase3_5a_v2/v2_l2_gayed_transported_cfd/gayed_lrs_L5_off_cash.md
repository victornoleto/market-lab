# V2-L2 Gayed-CFD rotation — `gayed_lrs_L5_off_cash` (iter 40)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (2 gates)
**Config:** signal=lrs, leverage=5x, off-regime=cash, risk-on=SPY,QQQ, daily close rebalance
**Window:** 2001-05-14 → 2026-04-14 (6266 bars, 578 regime switches)

## Split metrics

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2001-05-14 → 2017-12-31 | 4185 | 1.956 | 148.54% | -29.01% | 3685141.317 |
| OOS | 2018-01-01 → 2023-12-31 | 1509 | 2.108 | 215.02% | -48.76% | 963.960 |
| FWD | 2024-01-01 → 2026-04-14 | 572 | 1.921 | 178.05% | -32.94% | 10.188 |

## Walk-forward (8 windows)

- Profitable windows: **1.00** (target ≥ 0.75)
- Max window drawdown: **48.8%** (cap 25%)
- Pass: **NO**

## Hold / switch diagnostics

- Median hold: **5.5 days** (target ≥ 3d, V2 spec §1)
- Total regime switches: 578
- Switches by ticker: SPY=287, QQQ=291

## Cost breakdown (Pepperstone Razor retail)

- Cumulative transaction cost: **235.960%** of starting equity
- Cumulative overnight swap: **-110.687%** of starting equity
- Spread half: 2.0 bps | commission RT: 6.6 bps | slippage RT: 3.0 bps | swap daily long: -0.0050%

## Subset-gate verdict (per-config; PBO/DSR deferred to aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 2.108 | ✅ |
| fwd_sharpe_gt_0 | 1.921 | ✅ |
| wf_pass | 6/8 | ❌ |
| median_hold_ge_3d | 5.5d | ✅ |
| oos_cagr_ge_30pct | 215.0% | ✅ |
| oos_sharpe_ge_2 | 2.108 | ✅ |
| oos_maxdd_le_25pct | -48.8% | ❌ |

**Failed gates:** wf_pass, oos_maxdd_le_25pct

## Last-bar positions

| Leg | Weight |
|-----|------:|
| SPY | 2.5000 |
| QQQ | 2.5000 |

## Citations

- Regime rotation + MA filter + leverage discipline: `[leverage_for_the_long_run, p.7, p.11, p.13, p.14, p.16, p.17, p.21]`.
- Leverage cap cross-check via PoR: `[leverage_space, Vince]`, `[math_money_mgmt, Vince]`.
- Carver CFD cost model + risk budget: `[systematic_trading, ch.8-9]`.
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`.
- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.
