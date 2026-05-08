# GLD daily — V2-L3 AFML triple-barrier + meta-label (iter 46)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (5 gates)
**Primary:** EMA-50 up-cross  |  **Barriers:** TP=2.0×ATR, SL=1.0×ATR, time=20d
**Meta:** RF(n=100, d=5) on ['ret_5d', 'vol_20d', 'rsi_14d', 'atr_ratio_20d'], threshold p≥0.55
**CV:** CPCV 8 folds × 2 test groups, embargo 1.0%
**Window:** 2004-11-18 → 2026-04-15 (5384 bars, 224 events, 14 taken)

## Split metrics

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2004-11-18 → 2019-11-06 | 3768 | 0.384 | 0.83% | -4.96% | 1.132 |
| OOS | 2019-11-07 → 2024-02-20 | 1077 | -0.097 | -0.12% | -2.17% | 0.995 |
| FWD | 2024-02-21 → 2026-04-15 | 539 | 0.000 | 0.00% | 0.00% | 1.000 |

## Walk-forward (8 windows)

- Profitable windows: **0.38** (target ≥ 0.75)
- Max window drawdown: **5.0%** (cap 25%)
- Pass: **NO**

## Hold / event diagnostics

- Median hold: **6.0 days** (target ≥ 3d, V2 spec §1)
- Events total: 224
- Events taken (meta-label p ≥ 0.55): 14
- Per-bin counts (all events): tp=+1: 85, sl=-1: 132, vertical=0: 7

## Cost breakdown (Pepperstone Razor retail)

- Cumulative transaction cost: **1.904%** of starting equity
- Cumulative overnight swap: **0.490%** of starting equity
- Spread half: 2.0 bps | commission RT: 6.6 bps | slippage RT: 3.0 bps | swap daily long: -0.0050%

## Subset-gate verdict (per-config; PBO/DSR deferred to aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | -0.097 | ❌ |
| fwd_sharpe_gt_0 | 0.000 | ❌ |
| wf_pass | 6/8 | ❌ |
| median_hold_ge_3d | 6.0d | ✅ |
| oos_cagr_ge_30pct | -0.1% | ❌ |
| oos_sharpe_ge_2 | -0.097 | ❌ |
| oos_maxdd_le_25pct | -2.2% | ✅ |

**Subset FAIL** — 5 gate(s): oos_sharpe_gt_0, fwd_sharpe_gt_0, wf_pass, oos_cagr_ge_30pct, oos_sharpe_ge_2.

## Citations

- Triple-barrier labeling: `[advances_fin_ml, ch.3, p.45-49]`.
- Meta-labeling (primary recall → secondary precision): `[advances_fin_ml, ch.3, p.50-54]`.
- CPCV with embargo: `[advances_fin_ml, ch.7, p.149-154, p.219-222]`.
- Walk-forward 6/8 + MaxDD 25%: `[advances_fin_ml, ch.11]`.
- Hold economics (retail cost amortization): `[systematic_trading, p.185-188]`.
- Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.

