# QQQ daily — V2-L3 AFML triple-barrier + meta-label (iter 47)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (2 gates)
**Primary:** EMA-50 up-cross  |  **Barriers:** TP=2.0×ATR, SL=1.0×ATR, time=20d
**Meta:** RF(n=100, d=5) on ['ret_5d', 'vol_20d', 'rsi_14d', 'atr_ratio_20d'], threshold p≥0.55
**CV:** CPCV 8 folds × 2 test groups, embargo 1.0%
**Window:** 2001-05-14 → 2026-04-14 (6266 bars, 243 events, 44 taken)

## Split metrics

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2001-05-14 → 2018-10-17 | 4386 | 0.816 | 3.68% | -9.09% | 1.877 |
| OOS | 2018-10-18 → 2023-10-11 | 1253 | 0.924 | 2.46% | -3.07% | 1.128 |
| FWD | 2023-10-12 → 2026-04-14 | 627 | 1.002 | 2.06% | -1.64% | 1.052 |

## Walk-forward (8 windows)

- Profitable windows: **1.00** (target ≥ 0.75)
- Max window drawdown: **9.1%** (cap 25%)
- Pass: **YES**

## Hold / event diagnostics

- Median hold: **6.5 days** (target ≥ 3d, V2 spec §1)
- Events total: 243
- Events taken (meta-label p ≥ 0.55): 44
- Per-bin counts (all events): tp=+1: 104, sl=-1: 128, vertical=0: 11

## Cost breakdown (Pepperstone Razor retail)

- Cumulative transaction cost: **5.984%** of starting equity
- Cumulative overnight swap: **1.455%** of starting equity
- Spread half: 2.0 bps | commission RT: 6.6 bps | slippage RT: 3.0 bps | swap daily long: -0.0050%

## Subset-gate verdict (per-config; PBO/DSR deferred to aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 0.924 | ✅ |
| fwd_sharpe_gt_0 | 1.002 | ✅ |
| wf_pass | 6/8 | ✅ |
| median_hold_ge_3d | 6.5d | ✅ |
| oos_cagr_ge_30pct | 2.5% | ❌ |
| oos_sharpe_ge_2 | 0.924 | ❌ |
| oos_maxdd_le_25pct | -3.1% | ✅ |

**Subset FAIL** — 2 gate(s): oos_cagr_ge_30pct, oos_sharpe_ge_2.

## Citations

- Triple-barrier labeling: `[advances_fin_ml, ch.3, p.45-49]`.
- Meta-labeling (primary recall → secondary precision): `[advances_fin_ml, ch.3, p.50-54]`.
- CPCV with embargo: `[advances_fin_ml, ch.7, p.149-154, p.219-222]`.
- Walk-forward 6/8 + MaxDD 25%: `[advances_fin_ml, ch.11]`.
- Hold economics (retail cost amortization): `[systematic_trading, p.185-188]`.
- Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.

