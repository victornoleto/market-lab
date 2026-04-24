# Phase 1 — ndx_real

> Dataset window: **2010-02-12→2026-04-20** · Benchmark: **QQQ buy-hold**

## Scope

- Base configs expanded: **20** (top-20 by the source study's composite).
- Variants per base: **43** (1 baseline + 42 stop-loss combinations).
- Total simulations: **860**
- Gates: not evaluated (Phase 1 is exploratory per spec §6.1).

## Baseline (no stop) — reference point

| rank | cfg | CAGR | Sharpe | MDD | n_switches |
|---|---|---|---|---|---|
| 1 | `SMA_N150_th0_bL2_sL0` | +25.32% | 0.91 | +40.53% | 98 |
| 2 | `SMA_N150_th0_bL3_sL0` | +35.76% | 0.91 | +55.08% | 98 |
| 3 | `EMA_N150_th5_bL2_sL0` | +23.82% | 0.86 | +41.45% | 16 |
| 4 | `EMA_N150_th0_bL2_sL0` | +23.11% | 0.84 | +41.04% | 114 |
| 5 | `EMA_N150_th0_bL3_sL0` | +32.26% | 0.85 | +55.33% | 114 |
| 6 | `EMA_N150_th5_bL3_sL0` | +32.45% | 0.85 | +56.28% | 16 |
| 7 | `SMA_N150_th2_bL2_sL0` | +21.93% | 0.82 | +40.71% | 36 |
| 8 | `SMA_N150_th2_bL3_sL0` | +29.75% | 0.81 | +55.30% | 36 |
| 9 | `SMA_N200_th0_bL2_sL0` | +21.70% | 0.80 | +42.72% | 86 |
| 10 | `EMA_N150_th2_bL2_sL0` | +21.57% | 0.80 | +43.53% | 40 |
| 11 | `SMA_N200_th0_bL3_sL0` | +29.58% | 0.80 | +56.96% | 86 |
| 12 | `SMA_N150_th0_bL1_sL0` | +13.85% | 0.94 | +22.34% | 98 |
| 13 | `EMA_N100_th0_bL3_sL0` | +26.55% | 0.77 | +47.41% | 179 |
| 14 | `EMA_N150_th2_bL3_sL0` | +29.18% | 0.80 | +58.93% | 40 |
| 15 | `EMA_N150_th5_bL1_sL0` | +13.70% | 0.92 | +23.11% | 16 |
| 16 | `EMA_N200_th2_bL2_sL0` | +21.56% | 0.79 | +46.11% | 34 |
| 17 | `EMA_N150_th0_bL1_sL0` | +12.80% | 0.87 | +22.85% | 114 |
| 18 | `EMA_N200_th2_bL3_sL0` | +28.95% | 0.79 | +61.11% | 34 |
| 19 | `SMA_N150_th0_bL3_sL-1` | +28.99% | 0.78 | +61.57% | 98 |
| 20 | `SMA_N150_th2_bL1_sL0` | +12.64% | 0.87 | +22.79% | 36 |

## Top-20 variants by MDD reduction effectiveness

> *Effectiveness* = Δmdd (pp) / max(|ΔCAGR|, 0.1pp). Positive effectiveness means the stop reduced MDD; a high value means the MDD reduction is large relative to the CAGR sacrificed. Variants that *increased* MDD are excluded.

| # | variant | stop | mode | param | CAGR | ΔCAGR | MDD | ΔMDD | n_stops | longest (d) | eff. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `09_SMA_N200_th0_bL2_sL0_sl30_rec15` | 30% | recovery_trigger | 0.15 | +21.69% | -0.01% | +37.26% | +5.45% | 5 | 83 | 54.53 |
| 2 | `16_EMA_N200_th2_bL2_sL0_sl25_cool63` | 25% | time_cooldown | 63 | +21.56% | +0.00% | +40.75% | +5.36% | 6 | 63 | 53.55 |
| 3 | `19_SMA_N150_th0_bL3_sL-1_sl40_next` | 40% | next_signal | nan | +28.90% | -0.09% | +56.99% | +4.58% | 5 | 122 | 45.80 |
| 4 | `16_EMA_N200_th2_bL2_sL0_sl40_cool63` | 40% | time_cooldown | 63 | +21.41% | -0.15% | +40.74% | +5.36% | 1 | 63 | 35.45 |
| 5 | `02_SMA_N150_th0_bL3_sL0_sl25_next` | 25% | next_signal | nan | +35.94% | +0.18% | +48.58% | +6.50% | 13 | 392 | 35.44 |
| 6 | `01_SMA_N150_th0_bL2_sL0_sl30_rec15` | 30% | recovery_trigger | 0.15 | +25.50% | +0.17% | +34.65% | +5.88% | 2 | 120 | 34.35 |
| 7 | `16_EMA_N200_th2_bL2_sL0_sl35_rec5` | 35% | recovery_trigger | 0.05 | +21.56% | -0.00% | +43.10% | +3.01% | 2 | 15 | 30.12 |
| 8 | `03_EMA_N150_th5_bL2_sL0_sl30_rec10` | 30% | recovery_trigger | 0.1 | +23.93% | +0.10% | +39.08% | +2.36% | 4 | 58 | 22.87 |
| 9 | `10_EMA_N150_th2_bL2_sL0_sl35_cool21` | 35% | time_cooldown | 21 | +21.68% | +0.12% | +41.41% | +2.12% | 3 | 21 | 18.33 |
| 10 | `04_EMA_N150_th0_bL2_sL0_sl20_cool21` | 20% | time_cooldown | 21 | +23.40% | +0.29% | +35.79% | +5.25% | 13 | 21 | 17.83 |
| 11 | `08_SMA_N150_th2_bL3_sL0_sl40_cool21` | 40% | time_cooldown | 21 | +29.81% | +0.06% | +53.53% | +1.76% | 6 | 21 | 17.61 |
| 12 | `10_EMA_N150_th2_bL2_sL0_sl35_rec5` | 35% | recovery_trigger | 0.05 | +21.44% | -0.13% | +41.41% | +2.12% | 3 | 14 | 16.67 |
| 13 | `18_EMA_N200_th2_bL3_sL0_sl40_rec5` | 40% | recovery_trigger | 0.05 | +29.04% | +0.08% | +59.71% | +1.40% | 5 | 19 | 13.95 |
| 14 | `14_EMA_N150_th2_bL3_sL0_sl25_next` | 25% | next_signal | nan | +29.39% | +0.21% | +56.09% | +2.85% | 15 | 392 | 13.29 |
| 15 | `16_EMA_N200_th2_bL2_sL0_sl30_rec10` | 30% | recovery_trigger | 0.1 | +21.60% | +0.04% | +44.83% | +1.28% | 4 | 70 | 12.76 |
| 16 | `07_SMA_N150_th2_bL2_sL0_sl35_cool21` | 35% | time_cooldown | 21 | +21.62% | -0.30% | +37.03% | +3.68% | 3 | 21 | 12.11 |
| 17 | `09_SMA_N200_th0_bL2_sL0_sl25_cool63` | 25% | time_cooldown | 63 | +22.59% | +0.88% | +32.36% | +10.36% | 6 | 63 | 11.73 |
| 18 | `16_EMA_N200_th2_bL2_sL0_sl40_rec10` | 40% | recovery_trigger | 0.1 | +21.52% | -0.03% | +44.99% | +1.12% | 1 | 34 | 11.21 |
| 19 | `11_SMA_N200_th0_bL3_sL0_sl15_cool21` | 15% | time_cooldown | 21 | +28.25% | -1.33% | +42.63% | +14.33% | 37 | 21 | 10.78 |
| 20 | `09_SMA_N200_th0_bL2_sL0_sl40_rec5` | 40% | recovery_trigger | 0.05 | +21.52% | -0.18% | +40.73% | +1.99% | 2 | 5 | 10.77 |

## Average effect by mode

> Means across all (base, variant) pairs within the same mode.

| mode | n | ΔCAGR (avg) | ΔMDD (avg) | n_stops (avg) |
|---|---|---|---|---|
| next_signal | 120 | -5.41% | +0.49% | 8.1 |
| time_cooldown | 360 | -7.51% | -2.06% | 10.2 |
| recovery_trigger | 360 | -5.38% | -2.14% | 11.4 |

## Average effect by stop level

| stop_loss_pct | n | ΔCAGR (avg) | ΔMDD (avg) | n_stops (avg) | frac positive (MDD↓) |
|---|---|---|---|---|---|
| 15% | 140 | -8.82% | +1.42% | 21.5 | 58.6% |
| 20% | 140 | -11.12% | -4.30% | 16.4 | 32.1% |
| 25% | 140 | -4.87% | -1.78% | 9.8 | 27.1% |
| 30% | 140 | -6.15% | -1.90% | 7.5 | 30.7% |
| 35% | 140 | -4.47% | -2.06% | 4.8 | 26.4% |
| 40% | 140 | -2.37% | -1.76% | 2.7 | 27.9% |
