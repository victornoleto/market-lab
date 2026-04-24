# Phase 3 — spy_real

> Window: **2009-06-26→2026-04-20**

## Scope

- bases: 20
- combinations: 4
- total sims: 80
- gates: evaluated on top-5 survivors within ΔCAGR ≥ −5 pp corridor


## Average effect by combination

| combo | avg ΔCAGR | avg ΔMDD | frac MDD-down |
|---|---|---|---|
| sl20_cool21_cape05 | -1.63% | +7.67% | 95.0% |
| sl20_cool21_composite05 | -1.92% | +7.08% | 95.0% |
| sl30_rec10_cape05 | -1.87% | +6.21% | 90.0% |
| sl30_rec10_composite05 | -1.76% | +5.36% | 95.0% |

## Top-5 survivors + 7-gate verdict

> Selected by max ΔMDD within ΔCAGR ≥ −5 pp corridor.

| # | base | combo | CAGR | ΔCAGR | MDD | ΔMDD | Sharpe | G1 PBO | G2 DSR | G3 WF | G4 OOS | G5 FWD | G6 BS | G7 XLib | total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `SMA_N200_th2_bL3_sL0` (#20) | sl30_rec10_composite05 | +17.76% | -0.42% | +38.83% | +18.61% | 0.69 | ❌ (0.78) | ❌ (p=0.784) | ❌ | ✅ | ✅ | ❌ | ✅ (Δ0.0pp) | **3/7** |
| 2 | `SMA_N200_th2_bL3_sL0` (#20) | sl20_cool21_composite05 | +13.86% | -4.33% | +40.86% | +16.57% | 0.60 | ❌ (0.78) | ❌ (p=0.877) | ❌ | ✅ | ✅ | ❌ | ✅ (Δ0.0pp) | **3/7** |
| 3 | `SMA_N200_th2_bL3_sL0` (#20) | sl30_rec10_cape05 | +16.93% | -1.26% | +42.19% | +15.24% | 0.66 | ❌ (0.78) | ❌ (p=0.821) | ❌ | ✅ | ✅ | ❌ | ✅ (Δ0.0pp) | **3/7** |
| 4 | `SMA_N200_th2_bL2_sL0` (#7) | sl20_cool21_composite05 | +13.41% | -0.31% | +27.39% | +14.74% | 0.72 | ❌ (0.78) | ❌ (p=0.746) | ❌ | ✅ | ✅ | ✅ | ✅ (Δ0.0pp) | **4/7** |
| 5 | `SMA_N150_th0_bL2_sL0` (#11) | sl20_cool21_cape05 | +14.42% | +1.10% | +28.39% | +14.27% | 0.76 | ❌ (0.78) | ❌ (p=0.691) | ❌ | ✅ | ✅ | ✅ | ✅ (Δ0.0pp) | **4/7** |

## Baselines (no overlay) for reference

| rank | cfg | CAGR | MDD |
|---|---|---|---|
| 1 | `EMA_N150_th5_bL2_sL0` | +15.10% | +39.11% |
| 2 | `SMA_N150_th2_bL2_sL0` | +15.10% | +43.43% |
| 3 | `EMA_N150_th5_bL1_sL0` | +9.20% | +21.15% |
| 4 | `EMA_N150_th5_bL3_sL0` | +20.25% | +54.23% |
| 5 | `SMA_N150_th2_bL3_sL0` | +20.36% | +58.21% |
| 6 | `SMA_N150_th2_bL1_sL0` | +9.00% | +24.06% |
| 7 | `SMA_N200_th2_bL2_sL0` | +13.73% | +42.13% |
| 8 | `EMA_N100_th5_bL2_sL0` | +14.50% | +49.71% |
| 9 | `SMA_N100_th0_bL3_sL0` | +17.67% | +50.23% |
| 10 | `SMA_N200_th0_bL2_sL0` | +13.25% | +38.96% |
| 11 | `SMA_N150_th0_bL2_sL0` | +13.32% | +42.66% |
| 12 | `EMA_N100_th5_bL1_sL0` | +8.78% | +28.27% |
| 13 | `SMA_N200_th2_bL1_sL0` | +8.45% | +23.52% |
| 14 | `SMA_N200_th0_bL3_sL0` | +17.82% | +52.42% |
| 15 | `SMA_N100_th0_bL2_sL0` | +12.62% | +36.68% |
| 16 | `EMA_N150_th2_bL1_sL0` | +8.70% | +30.75% |
| 17 | `SMA_N150_th5_bL1_sL0` | +8.33% | +23.93% |
| 18 | `EMA_N150_th2_bL2_sL0` | +14.34% | +52.64% |
| 19 | `SMA_N150_th5_bL2_sL0` | +13.41% | +43.26% |
| 20 | `SMA_N200_th2_bL3_sL0` | +18.19% | +57.43% |