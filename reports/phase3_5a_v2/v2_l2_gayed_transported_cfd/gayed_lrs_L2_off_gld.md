# V2-L2 Gayed-CFD rotation — `gayed_lrs_L2_off_gld` (iter 36)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ✅ PASS subset
**Config:** signal=lrs, leverage=2x, off-regime=gld, risk-on=SPY,QQQ, daily close rebalance
**Window:** 2001-05-14 → 2026-04-14 (6266 bars, 578 regime switches)

## Split metrics

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2001-05-14 → 2017-12-31 | 4185 | 1.764 | 48.66% | -23.28% | 723.695 |
| OOS | 2018-01-01 → 2023-12-31 | 1509 | 2.178 | 74.15% | -21.88% | 27.717 |
| FWD | 2024-01-01 → 2026-04-14 | 572 | 1.795 | 58.24% | -17.35% | 2.834 |

## Walk-forward (8 windows)

- Profitable windows: **1.00** (target ≥ 0.75)
- Max window drawdown: **23.3%** (cap 25%)
- Pass: **YES**

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
| oos_sharpe_gt_0 | 2.178 | ✅ |
| fwd_sharpe_gt_0 | 1.795 | ✅ |
| wf_pass | 6/8 | ✅ |
| median_hold_ge_3d | 5.5d | ✅ |
| oos_cagr_ge_30pct | 74.2% | ✅ |
| oos_sharpe_ge_2 | 2.178 | ✅ |
| oos_maxdd_le_25pct | -21.9% | ✅ |

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
