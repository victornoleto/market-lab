# Phase 3 — educational

> Window: **1986-01-03→2026-04-17 (~40y synth)**

## Scope

- bases: 20
- combinations: 4
- total sims: 80
- gates: evaluated on top-5 survivors within ΔCAGR ≥ −5 pp corridor


## Average effect by combination

| combo | avg ΔCAGR | avg ΔMDD | frac MDD-down |
|---|---|---|---|
| sl20_cool21_cape05 | -3.92% | +13.75% | 90.0% |
| sl20_cool21_composite05 | -4.52% | +6.57% | 65.0% |
| sl30_rec10_cape05 | -3.90% | +7.48% | 80.0% |
| sl30_rec10_composite05 | -3.78% | +4.63% | 75.0% |

## Top-5 survivors + 7-gate verdict

> Selected by max ΔMDD within ΔCAGR ≥ −5 pp corridor.

| # | base | combo | CAGR | ΔCAGR | MDD | ΔMDD | Sharpe | G1 PBO | G2 DSR | G3 WF | G4 OOS | G5 FWD | G6 BS | G7 XLib | total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `SMA_N200_th5_bL2_sL0` (#16) | sl20_cool21_cape05 | +15.86% | -1.05% | +32.88% | +30.42% | 0.84 | ✅ (0.21) | ❌ (p=0.050) | ❌ | ✅ | ✅ | ✅ | ✅ (Δ0.0pp) | **5/7** |
| 2 | `SMA_N200_th5_bL2_sL0` (#16) | sl20_cool21_composite05 | +16.25% | -0.66% | +33.57% | +29.74% | 0.82 | ✅ (0.21) | ❌ (p=0.058) | ❌ | ✅ | ✅ | ✅ | ✅ (Δ0.0pp) | **5/7** |
| 3 | `EMA_N200_th5_bL2_sL0` (#19) | sl20_cool21_cape05 | +16.24% | -0.51% | +35.77% | +27.88% | 0.85 | ✅ (0.21) | ✅ (p=0.041) | ❌ | ✅ | ✅ | ✅ | ✅ (Δ0.0pp) | **6/7** |
| 4 | `EMA_N200_th5_bL2_sL0` (#19) | sl20_cool21_composite05 | +16.16% | -0.59% | +37.55% | +26.10% | 0.82 | ✅ (0.21) | ❌ (p=0.062) | ❌ | ✅ | ✅ | ✅ | ✅ (Δ0.0pp) | **5/7** |
| 5 | `SMA_N100_th5_bL3_sL0` (#13) | sl20_cool21_cape05 | +18.23% | -4.35% | +52.70% | +20.93% | 0.73 | ✅ (0.21) | ❌ (p=0.163) | ❌ | ✅ | ✅ | ✅ | ✅ (Δ0.0pp) | **5/7** |

## Baselines (no overlay) for reference

| rank | cfg | CAGR | MDD |
|---|---|---|---|
| 1 | `EMA_N150_th5_bL3_sL0` | +27.67% | +53.98% |
| 2 | `EMA_N150_th5_bL2_sL0` | +19.23% | +39.05% |
| 3 | `EMA_N100_th5_bL3_sL0` | +26.74% | +62.76% |
| 4 | `SMA_N200_th2_bL3_sL0` | +24.71% | +57.56% |
| 5 | `EMA_N100_th5_bL2_sL0` | +18.55% | +47.63% |
| 6 | `SMA_N150_th5_bL3_sL0` | +25.68% | +62.03% |
| 7 | `SMA_N150_th5_bL2_sL0` | +17.95% | +44.92% |
| 8 | `SMA_N200_th2_bL2_sL0` | +17.24% | +42.40% |
| 9 | `EMA_N150_th5_bL3_sL-1` | +24.45% | +62.26% |
| 10 | `EMA_N200_th2_bL3_sL0` | +21.31% | +63.29% |
| 11 | `EMA_N100_th5_bL3_sL-1` | +23.08% | +68.62% |
| 12 | `SMA_N200_th0_bL3_sL0` | +22.09% | +70.29% |
| 13 | `SMA_N100_th5_bL3_sL0` | +22.58% | +73.63% |
| 14 | `SMA_N150_th5_bL3_sL-1` | +21.82% | +67.26% |
| 15 | `EMA_N200_th0_bL3_sL0` | +20.51% | +66.17% |
| 16 | `SMA_N200_th5_bL2_sL0` | +16.91% | +63.30% |
| 17 | `SMA_N100_th5_bL2_sL0` | +15.93% | +56.24% |
| 18 | `EMA_N150_th5_bL2_sL-1` | +16.23% | +50.14% |
| 19 | `EMA_N200_th5_bL2_sL0` | +16.76% | +63.65% |
| 20 | `SMA_N200_th0_bL2_sL0` | +15.28% | +54.18% |