# Phase 1 — spy_real

> Dataset window: **2009-06-26→2026-04-20** · Benchmark: **SPY buy-hold**

## Scope

- Base configs expanded: **20** (top-20 by the source study's composite).
- Variants per base: **43** (1 baseline + 42 stop-loss combinations).
- Total simulations: **860**
- Gates: not evaluated (Phase 1 is exploratory per spec §6.1).

## Baseline (no stop) — reference point

| rank | cfg | CAGR | Sharpe | MDD | n_switches |
|---|---|---|---|---|---|
| 1 | `EMA_N150_th5_bL2_sL0` | +15.10% | 0.71 | +39.11% | 15 |
| 2 | `SMA_N150_th2_bL2_sL0` | +15.10% | 0.73 | +43.43% | 34 |
| 3 | `EMA_N150_th5_bL1_sL0` | +9.20% | 0.79 | +21.15% | 15 |
| 4 | `EMA_N150_th5_bL3_sL0` | +20.25% | 0.70 | +54.23% | 15 |
| 5 | `SMA_N150_th2_bL3_sL0` | +20.36% | 0.71 | +58.21% | 34 |
| 6 | `SMA_N150_th2_bL1_sL0` | +9.00% | 0.80 | +24.06% | 34 |
| 7 | `SMA_N200_th2_bL2_sL0` | +13.73% | 0.66 | +42.13% | 26 |
| 8 | `EMA_N100_th5_bL2_sL0` | +14.50% | 0.70 | +49.71% | 18 |
| 9 | `SMA_N100_th0_bL3_sL0` | +17.67% | 0.66 | +50.23% | 172 |
| 10 | `SMA_N200_th0_bL2_sL0` | +13.25% | 0.65 | +38.96% | 90 |
| 11 | `SMA_N150_th0_bL2_sL0` | +13.32% | 0.66 | +42.66% | 124 |
| 12 | `EMA_N100_th5_bL1_sL0` | +8.78% | 0.77 | +28.27% | 18 |
| 13 | `SMA_N200_th2_bL1_sL0` | +8.45% | 0.74 | +23.52% | 26 |
| 14 | `SMA_N200_th0_bL3_sL0` | +17.82% | 0.65 | +52.42% | 90 |
| 15 | `SMA_N100_th0_bL2_sL0` | +12.62% | 0.65 | +36.68% | 172 |
| 16 | `EMA_N150_th2_bL1_sL0` | +8.70% | 0.76 | +30.75% | 39 |
| 17 | `SMA_N150_th5_bL1_sL0` | +8.33% | 0.73 | +23.93% | 17 |
| 18 | `EMA_N150_th2_bL2_sL0` | +14.34% | 0.69 | +52.64% | 39 |
| 19 | `SMA_N150_th5_bL2_sL0` | +13.41% | 0.65 | +43.26% | 17 |
| 20 | `SMA_N200_th2_bL3_sL0` | +18.19% | 0.65 | +57.43% | 26 |

## Top-20 variants by MDD reduction effectiveness

> *Effectiveness* = Δmdd (pp) / max(|ΔCAGR|, 0.1pp). Positive effectiveness means the stop reduced MDD; a high value means the MDD reduction is large relative to the CAGR sacrificed. Variants that *increased* MDD are excluded.

| # | variant | stop | mode | param | CAGR | ΔCAGR | MDD | ΔMDD | n_stops | longest (d) | eff. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `08_EMA_N100_th5_bL2_sL0_sl25_rec10` | 25% | recovery_trigger | 0.1 | +14.47% | -0.03% | +36.99% | +12.72% | 3 | 58 | 127.20 |
| 2 | `18_EMA_N150_th2_bL2_sL0_sl15_cool21` | 15% | time_cooldown | 21 | +14.44% | +0.10% | +43.51% | +9.13% | 16 | 21 | 91.28 |
| 3 | `19_SMA_N150_th5_bL2_sL0_sl20_cool21` | 20% | time_cooldown | 21 | +13.54% | +0.13% | +32.84% | +10.42% | 7 | 21 | 80.98 |
| 4 | `18_EMA_N150_th2_bL2_sL0_sl15_rec5` | 15% | recovery_trigger | 0.05 | +14.25% | -0.09% | +44.83% | +7.82% | 17 | 76 | 78.16 |
| 5 | `08_EMA_N100_th5_bL2_sL0_sl30_rec10` | 30% | recovery_trigger | 0.1 | +14.54% | +0.04% | +42.07% | +7.63% | 2 | 53 | 76.32 |
| 6 | `19_SMA_N150_th5_bL2_sL0_sl20_rec10` | 20% | recovery_trigger | 0.1 | +13.55% | +0.14% | +32.84% | +10.42% | 7 | 50 | 76.27 |
| 7 | `07_SMA_N200_th2_bL2_sL0_sl25_cool21` | 25% | time_cooldown | 21 | +13.87% | +0.15% | +31.75% | +10.38% | 5 | 21 | 71.14 |
| 8 | `12_EMA_N100_th5_bL1_sL0_sl15_cool63` | 15% | time_cooldown | 63 | +8.74% | -0.04% | +21.76% | +6.51% | 2 | 63 | 65.11 |
| 9 | `19_SMA_N150_th5_bL2_sL0_sl15_cool21` | 15% | time_cooldown | 21 | +13.60% | +0.19% | +32.07% | +11.20% | 15 | 21 | 58.38 |
| 10 | `12_EMA_N100_th5_bL1_sL0_sl15_cool126` | 15% | time_cooldown | 126 | +8.69% | -0.09% | +23.17% | +5.09% | 2 | 126 | 50.94 |
| 11 | `12_EMA_N100_th5_bL1_sL0_sl15_rec15` | 15% | recovery_trigger | 0.15 | +8.65% | -0.13% | +21.76% | +6.51% | 2 | 112 | 49.56 |
| 12 | `08_EMA_N100_th5_bL2_sL0_sl30_cool126` | 30% | time_cooldown | 126 | +14.77% | +0.27% | +36.92% | +12.79% | 2 | 126 | 46.81 |
| 13 | `11_SMA_N150_th0_bL2_sL0_sl35_cool21` | 35% | time_cooldown | 21 | +13.24% | -0.08% | +38.58% | +4.08% | 2 | 21 | 40.75 |
| 14 | `18_EMA_N150_th2_bL2_sL0_sl20_cool63` | 20% | time_cooldown | 63 | +13.90% | -0.44% | +38.56% | +14.08% | 8 | 63 | 31.88 |
| 15 | `12_EMA_N100_th5_bL1_sL0_sl15_rec10` | 15% | recovery_trigger | 0.1 | +9.00% | +0.22% | +21.76% | +6.51% | 2 | 57 | 29.97 |
| 16 | `19_SMA_N150_th5_bL2_sL0_sl20_rec15` | 20% | recovery_trigger | 0.15 | +13.01% | -0.40% | +32.84% | +10.42% | 7 | 163 | 26.18 |
| 17 | `20_SMA_N200_th2_bL3_sL0_sl35_cool21` | 35% | time_cooldown | 21 | +18.68% | +0.50% | +44.55% | +12.88% | 5 | 21 | 25.97 |
| 18 | `16_EMA_N150_th2_bL1_sL0_sl25_cool126` | 25% | time_cooldown | 126 | +8.71% | +0.01% | +28.24% | +2.51% | 1 | 126 | 25.13 |
| 19 | `06_SMA_N150_th2_bL1_sL0_sl20_cool63` | 20% | time_cooldown | 63 | +9.13% | +0.14% | +20.79% | +3.27% | 1 | 63 | 23.99 |
| 20 | `15_SMA_N100_th0_bL2_sL0_sl20_rec10` | 20% | recovery_trigger | 0.1 | +12.81% | +0.19% | +32.22% | +4.46% | 6 | 86 | 23.87 |

## Average effect by mode

> Means across all (base, variant) pairs within the same mode.

| mode | n | ΔCAGR (avg) | ΔMDD (avg) | n_stops (avg) |
|---|---|---|---|---|
| next_signal | 120 | -3.11% | +0.82% | 4.5 |
| time_cooldown | 360 | -2.16% | +1.25% | 5.5 |
| recovery_trigger | 360 | -1.95% | +0.27% | 5.7 |

## Average effect by stop level

| stop_loss_pct | n | ΔCAGR (avg) | ΔMDD (avg) | n_stops (avg) | frac positive (MDD↓) |
|---|---|---|---|---|---|
| 15% | 140 | -5.69% | +1.51% | 13.6 | 62.9% |
| 20% | 140 | -2.82% | +1.93% | 8.0 | 65.7% |
| 25% | 140 | -2.38% | +0.86% | 5.0 | 43.6% |
| 30% | 140 | -0.79% | +0.63% | 3.0 | 36.4% |
| 35% | 140 | -1.04% | +0.20% | 1.9 | 30.0% |
| 40% | 140 | -0.51% | -0.53% | 1.1 | 16.4% |
