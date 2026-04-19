# XLV daily — V2-L3 AFML triple-barrier + meta-label (iter 55)

**Path tag:** [SHORT-HOLD CFD]  |  **Status:** ❌ FAIL (4 gates)
**Primary:** EMA-50 up-cross  |  **Barriers:** TP=2.0×ATR, SL=1.0×ATR, time=20d
**Meta:** RF(n=100, d=5) on ['ret_5d', 'vol_20d', 'rsi_14d', 'atr_ratio_20d'], threshold p≥0.55
**CV:** CPCV 8 folds × 2 test groups, embargo 1.0%
**Window:** 2014-01-02 → 2026-04-14 (3088 bars, 142 events, 17 taken)

## Split metrics

| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |
|-------|-------|-------:|-------:|-----:|------:|-------------:|
| IS | 2014-01-02 → 2022-08-02 | 2161 | 0.625 | 1.73% | -5.77% | 1.158 |
| OOS | 2022-08-03 → 2025-01-17 | 618 | 0.101 | 0.33% | -5.87% | 1.008 |
| FWD | 2025-01-21 → 2026-04-14 | 309 | -0.349 | -0.96% | -3.05% | 0.988 |

## Walk-forward (8 windows)

- Profitable windows: **0.62** (target ≥ 0.75)
- Max window drawdown: **5.9%** (cap 25%)
- Pass: **NO**

## Hold / event diagnostics

- Median hold: **12.0 days** (target ≥ 3d, V2 spec §1)
- Events total: 142
- Events taken (meta-label p ≥ 0.55): 17
- Per-bin counts (all events): tp=+1: 53, sl=-1: 73, vertical=0: 16

## Cost breakdown (Pepperstone Razor retail)

- Cumulative transaction cost: **2.312%** of starting equity
- Cumulative overnight swap: **0.660%** of starting equity
- Spread half: 2.0 bps | commission RT: 6.6 bps | slippage RT: 3.0 bps | swap daily long: -0.0050%

## Subset-gate verdict (per-config; PBO/DSR deferred to aggregator)

| Gate | Value | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 0.101 | ✅ |
| fwd_sharpe_gt_0 | -0.349 | ❌ |
| wf_pass | 6/8 | ❌ |
| median_hold_ge_3d | 12.0d | ✅ |
| oos_cagr_ge_30pct | 0.3% | ❌ |
| oos_sharpe_ge_2 | 0.101 | ❌ |
| oos_maxdd_le_25pct | -5.9% | ✅ |

**Subset FAIL** — 4 gate(s): fwd_sharpe_gt_0, wf_pass, oos_cagr_ge_30pct, oos_sharpe_ge_2.

## Citations

- Triple-barrier labeling: `[advances_fin_ml, ch.3, p.45-49]`.
- Meta-labeling (primary recall → secondary precision): `[advances_fin_ml, ch.3, p.50-54]`.
- CPCV with embargo: `[advances_fin_ml, ch.7, p.149-154, p.219-222]`.
- Walk-forward 6/8 + MaxDD 25%: `[advances_fin_ml, ch.11]`.
- Hold economics (retail cost amortization): `[systematic_trading, p.185-188]`.
- Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.

