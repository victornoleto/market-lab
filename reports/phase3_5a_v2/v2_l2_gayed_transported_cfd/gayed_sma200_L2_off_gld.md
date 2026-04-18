# V2-L2 Gayed-CFD rotation — `gayed_sma200_L2_off_gld` (iter 18)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (1 gates)
**Config:** signal=sma200, leverage=2x, off-regime=gld, risk-on=SPY,QQQ, daily close rebalance
**Window:** 2001-05-14 → 2026-04-14 (6266 bars, 310 regime switches)

## Split metrics

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2001-05-14 → 2017-12-31 | 4185 | 1.261 | 31.77% | -23.14% | 97.713 |
| OOS | 2018-01-01 → 2023-12-31 | 1509 | 1.645 | 54.45% | -21.91% | 13.502 |
| FWD | 2024-01-01 → 2026-04-14 | 572 | 1.501 | 48.48% | -20.70% | 2.453 |

## Walk-forward (8 windows)

- Profitable windows: **1.00** (target ≥ 0.75)
- Max window drawdown: **22.6%** (cap 25%)
- Pass: **YES**

## Hold / switch diagnostics

- Median hold: **5.0 days** (target ≥ 3d, V2 spec §1)
- Total regime switches: 310
- Switches by ticker: SPY=159, QQQ=151

## Cost breakdown (Pepperstone Razor retail)

- Cumulative transaction cost: **63.376%** of starting equity
- Cumulative overnight swap: **-45.955%** of starting equity
- Spread half: 2.0 bps | commission RT: 6.6 bps | slippage RT: 3.0 bps | swap daily long: -0.0050%

## Subset-gate verdict (per-config; PBO/DSR deferred to aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 1.645 | ✅ |
| fwd_sharpe_gt_0 | 1.501 | ✅ |
| wf_pass | 6/8 | ✅ |
| median_hold_ge_3d | 5.0d | ✅ |
| oos_cagr_ge_30pct | 54.4% | ✅ |
| oos_sharpe_ge_2 | 1.645 | ❌ |
| oos_maxdd_le_25pct | -21.9% | ✅ |

**Failed gates:** oos_sharpe_ge_2

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
