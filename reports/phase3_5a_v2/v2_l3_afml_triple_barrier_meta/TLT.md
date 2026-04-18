# TLT daily — V2-L3 AFML triple-barrier + meta-label (iter 49)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (4 gates)
**Primary:** EMA-50 up-cross  |  **Barriers:** TP=2.0×ATR, SL=1.0×ATR, time=20d
**Meta:** RF(n=100, d=5) on ['ret_5d', 'vol_20d', 'rsi_14d', 'atr_ratio_20d'], threshold p≥0.55
**CV:** CPCV 8 folds × 2 test groups, embargo 1.0%
**Window:** 2002-07-26 → 2026-04-15 (5968 bars, 260 events, 37 taken)

## Split metrics

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2002-07-26 → 2019-02-28 | 4177 | 0.637 | 1.60% | -3.85% | 1.302 |
| OOS | 2019-03-01 → 2023-11-24 | 1194 | -0.166 | -0.36% | -4.14% | 0.983 |
| FWD | 2023-11-27 → 2026-04-15 | 597 | 0.828 | 2.02% | -2.18% | 1.048 |

## Walk-forward (8 windows)

- Profitable windows: **0.62** (target ≥ 0.75)
- Max window drawdown: **3.8%** (cap 25%)
- Pass: **NO**

## Hold / event diagnostics

- Median hold: **7.0 days** (target ≥ 3d, V2 spec §1)
- Events total: 260
- Events taken (meta-label p ≥ 0.55): 37
- Per-bin counts (all events): tp=+1: 101, sl=-1: 148, vertical=0: 11

## Cost breakdown (Pepperstone Razor retail)

- Cumulative transaction cost: **5.032%** of starting equity
- Cumulative overnight swap: **1.090%** of starting equity
- Spread half: 2.0 bps | commission RT: 6.6 bps | slippage RT: 3.0 bps | swap daily long: -0.0050%

## Subset-gate verdict (per-config; PBO/DSR deferred to aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | -0.166 | ❌ |
| fwd_sharpe_gt_0 | 0.828 | ✅ |
| wf_pass | 6/8 | ❌ |
| median_hold_ge_3d | 7.0d | ✅ |
| oos_cagr_ge_30pct | -0.4% | ❌ |
| oos_sharpe_ge_2 | -0.166 | ❌ |
| oos_maxdd_le_25pct | -4.1% | ✅ |

**Subset FAIL** — 4 gate(s): oos_sharpe_gt_0, wf_pass, oos_cagr_ge_30pct, oos_sharpe_ge_2.

## Citations

- Triple-barrier labeling: `[advances_fin_ml, ch.3, p.45-49]`.
- Meta-labeling (primary recall → secondary precision): `[advances_fin_ml, ch.3, p.50-54]`.
- CPCV with embargo: `[advances_fin_ml, ch.7, p.149-154, p.219-222]`.
- Walk-forward 6/8 + MaxDD 25%: `[advances_fin_ml, ch.11]`.
- Hold economics (retail cost amortization): `[systematic_trading, p.185-188]`.
- Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.

