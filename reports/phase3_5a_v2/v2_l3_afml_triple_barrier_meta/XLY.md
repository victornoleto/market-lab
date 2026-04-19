# XLY daily — V2-L3 AFML triple-barrier + meta-label (iter 56)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (3 gates)
**Primary:** EMA-50 up-cross  |  **Barriers:** TP=2.0×ATR, SL=1.0×ATR, time=20d
**Meta:** RF(n=100, d=5) on ['ret_5d', 'vol_20d', 'rsi_14d', 'atr_ratio_20d'], threshold p≥0.55
**CV:** CPCV 8 folds × 2 test groups, embargo 1.0%
**Window:** 2014-01-02 → 2026-04-14 (3088 bars, 129 events, 24 taken)

## Split metrics

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2014-01-02 → 2022-08-02 | 2161 | 0.325 | 1.96% | -8.65% | 1.181 |
| OOS | 2022-08-03 → 2025-01-17 | 618 | 0.116 | 0.66% | -13.22% | 1.016 |
| FWD | 2025-01-21 → 2026-04-14 | 309 | 1.153 | 2.44% | 0.00% | 1.030 |

## Walk-forward (8 windows)

- Profitable windows: **0.50** (target ≥ 0.75)
- Max window drawdown: **14.8%** (cap 25%)
- Pass: **NO**

## Hold / event diagnostics

- Median hold: **6.0 days** (target ≥ 3d, V2 spec §1)
- Events total: 129
- Events taken (meta-label p ≥ 0.55): 24
- Per-bin counts (all events): tp=+1: 55, sl=-1: 64, vertical=0: 10

## Cost breakdown (Pepperstone Razor retail)

- Cumulative transaction cost: **3.264%** of starting equity
- Cumulative overnight swap: **0.795%** of starting equity
- Spread half: 2.0 bps | commission RT: 6.6 bps | slippage RT: 3.0 bps | swap daily long: -0.0050%

## Subset-gate verdict (per-config; PBO/DSR deferred to aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 0.116 | ✅ |
| fwd_sharpe_gt_0 | 1.153 | ✅ |
| wf_pass | 6/8 | ❌ |
| median_hold_ge_3d | 6.0d | ✅ |
| oos_cagr_ge_30pct | 0.7% | ❌ |
| oos_sharpe_ge_2 | 0.116 | ❌ |
| oos_maxdd_le_25pct | -13.2% | ✅ |

**Subset FAIL** — 3 gate(s): wf_pass, oos_cagr_ge_30pct, oos_sharpe_ge_2.

## Citations

- Triple-barrier labeling: `[advances_fin_ml, ch.3, p.45-49]`.
- Meta-labeling (primary recall → secondary precision): `[advances_fin_ml, ch.3, p.50-54]`.
- CPCV with embargo: `[advances_fin_ml, ch.7, p.149-154, p.219-222]`.
- Walk-forward 6/8 + MaxDD 25%: `[advances_fin_ml, ch.11]`.
- Hold economics (retail cost amortization): `[systematic_trading, p.185-188]`.
- Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.

