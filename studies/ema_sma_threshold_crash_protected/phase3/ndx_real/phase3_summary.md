# Phase 3 — ndx_real

> Window: **2010-02-12→2026-04-20**

## Scope

- bases: 20
- combinations: 4
- total sims: 80
- gates: evaluated on top-5 survivors within ΔCAGR ≥ −5 pp corridor


## Average effect by combination

| combo | avg ΔCAGR | avg ΔMDD | frac MDD-down |
|---|---|---|---|
| sl20_cool21_cape05 | -3.88% | +2.60% | 75.0% |
| sl20_cool21_composite05 | -4.95% | +2.80% | 80.0% |
| sl30_rec10_cape05 | -5.06% | -0.81% | 40.0% |
| sl30_rec10_composite05 | -4.65% | +0.33% | 60.0% |

## Top-5 survivors + 7-gate verdict

> Selected by max ΔMDD within ΔCAGR ≥ −5 pp corridor.

| # | base | combo | CAGR | ΔCAGR | MDD | ΔMDD | Sharpe | G1 PBO | G2 DSR | G3 WF | G4 OOS | G5 FWD | G6 BS | G7 XLib | total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `EMA_N200_th2_bL2_sL0` (#16) | sl30_rec10_cape05 | +19.27% | -2.29% | +36.09% | +10.02% | 0.77 | ❌ (0.60) | ❌ (p=0.694) | ❌ | ✅ | ✅ | ✅ | ✅ (Δ0.1pp) | **4/7** |
| 2 | `EMA_N200_th2_bL2_sL0` (#16) | sl30_rec10_composite05 | +19.91% | -1.65% | +36.56% | +9.55% | 0.82 | ❌ (0.60) | ❌ (p=0.633) | ❌ | ✅ | ✅ | ✅ | ✅ (Δ0.1pp) | **4/7** |
| 3 | `SMA_N150_th0_bL2_sL0` (#1) | sl20_cool21_composite05 | +20.99% | -4.34% | +31.89% | +8.64% | 0.88 | ❌ (0.60) | ❌ (p=0.542) | ❌ | ✅ | ✅ | ✅ | ✅ (Δ0.0pp) | **4/7** |
| 4 | `SMA_N150_th0_bL2_sL0` (#1) | sl20_cool21_cape05 | +20.71% | -4.62% | +32.61% | +7.92% | 0.86 | ❌ (0.60) | ❌ (p=0.569) | ❌ | ✅ | ✅ | ✅ | ✅ (Δ0.0pp) | **4/7** |
| 5 | `SMA_N150_th2_bL2_sL0` (#7) | sl20_cool21_composite05 | +18.53% | -3.39% | +33.26% | +7.45% | 0.80 | ❌ (0.60) | ❌ (p=0.665) | ❌ | ✅ | ✅ | ✅ | ✅ (Δ0.0pp) | **4/7** |

## Baselines (no overlay) for reference

| rank | cfg | CAGR | MDD |
|---|---|---|---|
| 1 | `SMA_N150_th0_bL2_sL0` | +25.32% | +40.53% |
| 2 | `SMA_N150_th0_bL3_sL0` | +35.76% | +55.08% |
| 3 | `EMA_N150_th5_bL2_sL0` | +23.82% | +41.45% |
| 4 | `EMA_N150_th0_bL2_sL0` | +23.11% | +41.04% |
| 5 | `EMA_N150_th0_bL3_sL0` | +32.26% | +55.33% |
| 6 | `EMA_N150_th5_bL3_sL0` | +32.45% | +56.28% |
| 7 | `SMA_N150_th2_bL2_sL0` | +21.93% | +40.71% |
| 8 | `SMA_N150_th2_bL3_sL0` | +29.75% | +55.30% |
| 9 | `SMA_N200_th0_bL2_sL0` | +21.70% | +42.72% |
| 10 | `EMA_N150_th2_bL2_sL0` | +21.57% | +43.53% |
| 11 | `SMA_N200_th0_bL3_sL0` | +29.58% | +56.96% |
| 12 | `SMA_N150_th0_bL1_sL0` | +13.85% | +22.34% |
| 13 | `EMA_N100_th0_bL3_sL0` | +26.55% | +47.41% |
| 14 | `EMA_N150_th2_bL3_sL0` | +29.18% | +58.93% |
| 15 | `EMA_N150_th5_bL1_sL0` | +13.70% | +23.11% |
| 16 | `EMA_N200_th2_bL2_sL0` | +21.56% | +46.11% |
| 17 | `EMA_N150_th0_bL1_sL0` | +12.80% | +22.85% |
| 18 | `EMA_N200_th2_bL3_sL0` | +28.95% | +61.11% |
| 19 | `SMA_N150_th0_bL3_sL-1` | +28.99% | +61.57% |
| 20 | `SMA_N150_th2_bL1_sL0` | +12.64% | +22.79% |