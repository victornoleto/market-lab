# XLE daily — V2-L3 AFML triple-barrier + meta-label (iter 50)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (3 gates)
**Primary:** EMA-50 up-cross  |  **Barriers:** TP=2.0×ATR, SL=1.0×ATR, time=20d
**Meta:** RF(n=100, d=5) on ['ret_5d', 'vol_20d', 'rsi_14d', 'atr_ratio_20d'], threshold p≥0.55
**CV:** CPCV 8 folds × 2 test groups, embargo 1.0%
**Window:** 2003-08-20 → 2026-04-14 (5698 bars, 222 events, 39 taken)

## Split metrics

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2003-08-20 → 2019-06-24 | 3988 | 0.371 | 1.85% | -10.49% | 1.337 |
| OOS | 2019-06-25 → 2024-01-03 | 1140 | 0.789 | 6.90% | -9.12% | 1.353 |
| FWD | 2024-01-04 → 2026-04-14 | 570 | 0.873 | 7.87% | -7.62% | 1.187 |

## Walk-forward (8 windows)

- Profitable windows: **0.62** (target ≥ 0.75)
- Max window drawdown: **10.5%** (cap 25%)
- Pass: **NO**

## Hold / event diagnostics

- Median hold: **9.0 days** (target ≥ 3d, V2 spec §1)
- Events total: 222
- Events taken (meta-label p ≥ 0.55): 39
- Per-bin counts (all events): tp=+1: 103, sl=-1: 104, vertical=0: 15

## Cost breakdown (Pepperstone Razor retail)

- Cumulative transaction cost: **5.304%** of starting equity
- Cumulative overnight swap: **1.385%** of starting equity
- Spread half: 2.0 bps | commission RT: 6.6 bps | slippage RT: 3.0 bps | swap daily long: -0.0050%

## Subset-gate verdict (per-config; PBO/DSR deferred to aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 0.789 | ✅ |
| fwd_sharpe_gt_0 | 0.873 | ✅ |
| wf_pass | 6/8 | ❌ |
| median_hold_ge_3d | 9.0d | ✅ |
| oos_cagr_ge_30pct | 6.9% | ❌ |
| oos_sharpe_ge_2 | 0.789 | ❌ |
| oos_maxdd_le_25pct | -9.1% | ✅ |

**Subset FAIL** — 3 gate(s): wf_pass, oos_cagr_ge_30pct, oos_sharpe_ge_2.

## Citations

- Triple-barrier labeling: `[advances_fin_ml, ch.3, p.45-49]`.
- Meta-labeling (primary recall → secondary precision): `[advances_fin_ml, ch.3, p.50-54]`.
- CPCV with embargo: `[advances_fin_ml, ch.7, p.149-154, p.219-222]`.
- Walk-forward 6/8 + MaxDD 25%: `[advances_fin_ml, ch.11]`.
- Hold economics (retail cost amortization): `[systematic_trading, p.185-188]`.
- Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.

