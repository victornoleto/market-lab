# XLK daily — V2-L3 AFML triple-barrier + meta-label (iter 53)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (5 gates)
**Primary:** EMA-50 up-cross  |  **Barriers:** TP=2.0×ATR, SL=1.0×ATR, time=20d
**Meta:** RF(n=100, d=5) on ['ret_5d', 'vol_20d', 'rsi_14d', 'atr_ratio_20d'], threshold p≥0.55
**CV:** CPCV 8 folds × 2 test groups, embargo 1.0%
**Window:** 2003-08-20 → 2026-04-14 (5698 bars, 213 events, 7 taken)

## Split metrics

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2003-08-20 → 2019-06-24 | 3988 | -0.010 | -0.04% | -5.44% | 0.994 |
| OOS | 2019-06-25 → 2024-01-03 | 1140 | 0.000 | 0.00% | 0.00% | 1.000 |
| FWD | 2024-01-04 → 2026-04-14 | 570 | -0.270 | -1.31% | -5.90% | 0.971 |

## Walk-forward (8 windows)

- Profitable windows: **0.25** (target ≥ 0.75)
- Max window drawdown: **5.9%** (cap 25%)
- Pass: **NO**

## Hold / event diagnostics

- Median hold: **7.0 days** (target ≥ 3d, V2 spec §1)
- Events total: 213
- Events taken (meta-label p ≥ 0.55): 7
- Per-bin counts (all events): tp=+1: 82, sl=-1: 118, vertical=0: 13

## Cost breakdown (Pepperstone Razor retail)

- Cumulative transaction cost: **0.952%** of starting equity
- Cumulative overnight swap: **0.200%** of starting equity
- Spread half: 2.0 bps | commission RT: 6.6 bps | slippage RT: 3.0 bps | swap daily long: -0.0050%

## Subset-gate verdict (per-config; PBO/DSR deferred to aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 0.000 | ❌ |
| fwd_sharpe_gt_0 | -0.270 | ❌ |
| wf_pass | 6/8 | ❌ |
| median_hold_ge_3d | 7.0d | ✅ |
| oos_cagr_ge_30pct | 0.0% | ❌ |
| oos_sharpe_ge_2 | 0.000 | ❌ |
| oos_maxdd_le_25pct | 0.0% | ✅ |

**Subset FAIL** — 5 gate(s): oos_sharpe_gt_0, fwd_sharpe_gt_0, wf_pass, oos_cagr_ge_30pct, oos_sharpe_ge_2.

## Citations

- Triple-barrier labeling: `[advances_fin_ml, ch.3, p.45-49]`.
- Meta-labeling (primary recall → secondary precision): `[advances_fin_ml, ch.3, p.50-54]`.
- CPCV with embargo: `[advances_fin_ml, ch.7, p.149-154, p.219-222]`.
- Walk-forward 6/8 + MaxDD 25%: `[advances_fin_ml, ch.11]`.
- Hold economics (retail cost amortization): `[systematic_trading, p.185-188]`.
- Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.

