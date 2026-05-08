# SPY daily — V2-L3 AFML triple-barrier + meta-label (iter 48)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (3 gates)
**Primary:** EMA-50 up-cross  |  **Barriers:** TP=2.0×ATR, SL=1.0×ATR, time=20d
**Meta:** RF(n=100, d=5) on ['ret_5d', 'vol_20d', 'rsi_14d', 'atr_ratio_20d'], threshold p≥0.55
**CV:** CPCV 8 folds × 2 test groups, embargo 1.0%
**Window:** 2001-05-14 → 2026-04-14 (6266 bars, 226 events, 57 taken)

## Split metrics

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2001-05-14 → 2018-10-17 | 4386 | 0.061 | 0.17% | -11.61% | 1.030 |
| OOS | 2018-10-18 → 2023-10-11 | 1253 | 0.147 | 0.60% | -6.76% | 1.030 |
| FWD | 2023-10-12 → 2026-04-14 | 627 | 1.305 | 6.82% | -4.28% | 1.178 |

## Walk-forward (8 windows)

- Profitable windows: **0.62** (target ≥ 0.75)
- Max window drawdown: **8.9%** (cap 25%)
- Pass: **NO**

## Hold / event diagnostics

- Median hold: **7.0 days** (target ≥ 3d, V2 spec §1)
- Events total: 226
- Events taken (meta-label p ≥ 0.55): 57
- Per-bin counts (all events): tp=+1: 105, sl=-1: 110, vertical=0: 11

## Cost breakdown (Pepperstone Razor retail)

- Cumulative transaction cost: **7.752%** of starting equity
- Cumulative overnight swap: **1.810%** of starting equity
- Spread half: 2.0 bps | commission RT: 6.6 bps | slippage RT: 3.0 bps | swap daily long: -0.0050%

## Subset-gate verdict (per-config; PBO/DSR deferred to aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 0.147 | ✅ |
| fwd_sharpe_gt_0 | 1.305 | ✅ |
| wf_pass | 6/8 | ❌ |
| median_hold_ge_3d | 7.0d | ✅ |
| oos_cagr_ge_30pct | 0.6% | ❌ |
| oos_sharpe_ge_2 | 0.147 | ❌ |
| oos_maxdd_le_25pct | -6.8% | ✅ |

**Subset FAIL** — 3 gate(s): wf_pass, oos_cagr_ge_30pct, oos_sharpe_ge_2.

## Citations

- Triple-barrier labeling: `[advances_fin_ml, ch.3, p.45-49]`.
- Meta-labeling (primary recall → secondary precision): `[advances_fin_ml, ch.3, p.50-54]`.
- CPCV with embargo: `[advances_fin_ml, ch.7, p.149-154, p.219-222]`.
- Walk-forward 6/8 + MaxDD 25%: `[advances_fin_ml, ch.11]`.
- Hold economics (retail cost amortization): `[systematic_trading, p.185-188]`.
- Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.

