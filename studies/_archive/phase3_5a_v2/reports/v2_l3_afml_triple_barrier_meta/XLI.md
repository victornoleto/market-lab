# XLI daily — V2-L3 AFML triple-barrier + meta-label (iter 52)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (3 gates)
**Primary:** EMA-50 up-cross  |  **Barriers:** TP=2.0×ATR, SL=1.0×ATR, time=20d
**Meta:** RF(n=100, d=5) on ['ret_5d', 'vol_20d', 'rsi_14d', 'atr_ratio_20d'], threshold p≥0.55
**CV:** CPCV 8 folds × 2 test groups, embargo 1.0%
**Window:** 2014-01-02 → 2026-04-14 (3088 bars, 117 events, 34 taken)

## Split metrics

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2014-01-02 → 2022-08-02 | 2161 | 0.520 | 3.43% | -14.19% | 1.336 |
| OOS | 2022-08-03 → 2025-01-17 | 618 | 0.945 | 3.55% | -6.61% | 1.089 |
| FWD | 2025-01-21 → 2026-04-14 | 309 | 2.139 | 11.27% | -0.88% | 1.140 |

## Walk-forward (8 windows)

- Profitable windows: **0.62** (target ≥ 0.75)
- Max window drawdown: **9.4%** (cap 25%)
- Pass: **NO**

## Hold / event diagnostics

- Median hold: **8.5 days** (target ≥ 3d, V2 spec §1)
- Events total: 117
- Events taken (meta-label p ≥ 0.55): 34
- Per-bin counts (all events): tp=+1: 50, sl=-1: 62, vertical=0: 5

## Cost breakdown (Pepperstone Razor retail)

- Cumulative transaction cost: **4.624%** of starting equity
- Cumulative overnight swap: **1.300%** of starting equity
- Spread half: 2.0 bps | commission RT: 6.6 bps | slippage RT: 3.0 bps | swap daily long: -0.0050%

## Subset-gate verdict (per-config; PBO/DSR deferred to aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 0.945 | ✅ |
| fwd_sharpe_gt_0 | 2.139 | ✅ |
| wf_pass | 6/8 | ❌ |
| median_hold_ge_3d | 8.5d | ✅ |
| oos_cagr_ge_30pct | 3.5% | ❌ |
| oos_sharpe_ge_2 | 0.945 | ❌ |
| oos_maxdd_le_25pct | -6.6% | ✅ |

**Subset FAIL** — 3 gate(s): wf_pass, oos_cagr_ge_30pct, oos_sharpe_ge_2.

## Citations

- Triple-barrier labeling: `[advances_fin_ml, ch.3, p.45-49]`.
- Meta-labeling (primary recall → secondary precision): `[advances_fin_ml, ch.3, p.50-54]`.
- CPCV with embargo: `[advances_fin_ml, ch.7, p.149-154, p.219-222]`.
- Walk-forward 6/8 + MaxDD 25%: `[advances_fin_ml, ch.11]`.
- Hold economics (retail cost amortization): `[systematic_trading, p.185-188]`.
- Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.

