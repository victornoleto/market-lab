# Phase 1 — educational

> Dataset window: **1986-01-03→2026-04-17 (~40y)** · Benchmark: **SPY buy-hold (synth SPYSIM)**

## Scope

- Base configs expanded: **20** (top-20 by the source study's composite).
- Variants per base: **43** (1 baseline + 42 stop-loss combinations).
- Total simulations: **860**
- Gates: not evaluated (Phase 1 is exploratory per spec §6.1).

## Baseline (no stop) — reference point

| rank | cfg | CAGR | Sharpe | MDD | n_switches |
|---|---|---|---|---|---|
| 1 | `EMA_N150_th5_bL3_sL0` | +27.67% | 0.84 | +53.98% | 25 |
| 2 | `EMA_N150_th5_bL2_sL0` | +19.23% | 0.83 | +39.05% | 25 |
| 3 | `EMA_N100_th5_bL3_sL0` | +26.74% | 0.83 | +62.76% | 32 |
| 4 | `SMA_N200_th2_bL3_sL0` | +24.71% | 0.79 | +57.56% | 56 |
| 5 | `EMA_N100_th5_bL2_sL0` | +18.55% | 0.82 | +47.63% | 32 |
| 6 | `SMA_N150_th5_bL3_sL0` | +25.68% | 0.80 | +62.03% | 31 |
| 7 | `SMA_N150_th5_bL2_sL0` | +17.95% | 0.79 | +44.92% | 31 |
| 8 | `SMA_N200_th2_bL2_sL0` | +17.24% | 0.78 | +42.40% | 56 |
| 9 | `EMA_N150_th5_bL3_sL-1` | +24.45% | 0.75 | +62.26% | 25 |
| 10 | `EMA_N200_th2_bL3_sL0` | +21.31% | 0.71 | +63.29% | 78 |
| 11 | `EMA_N100_th5_bL3_sL-1` | +23.08% | 0.73 | +68.62% | 32 |
| 12 | `SMA_N200_th0_bL3_sL0` | +22.09% | 0.74 | +70.29% | 236 |
| 13 | `SMA_N100_th5_bL3_sL0` | +22.58% | 0.74 | +73.63% | 43 |
| 14 | `SMA_N150_th5_bL3_sL-1` | +21.82% | 0.70 | +67.26% | 31 |
| 15 | `EMA_N200_th0_bL3_sL0` | +20.51% | 0.69 | +66.17% | 276 |
| 16 | `SMA_N200_th5_bL2_sL0` | +16.91% | 0.74 | +63.30% | 25 |
| 17 | `SMA_N100_th5_bL2_sL0` | +15.93% | 0.73 | +56.24% | 43 |
| 18 | `EMA_N150_th5_bL2_sL-1` | +16.23% | 0.67 | +50.14% | 25 |
| 19 | `EMA_N200_th5_bL2_sL0` | +16.76% | 0.73 | +63.65% | 25 |
| 20 | `SMA_N200_th0_bL2_sL0` | +15.28% | 0.71 | +54.18% | 236 |

## Top-20 variants by MDD reduction effectiveness

> *Effectiveness* = Δmdd (pp) / max(|ΔCAGR|, 0.1pp). Positive effectiveness means the stop reduced MDD; a high value means the MDD reduction is large relative to the CAGR sacrificed. Variants that *increased* MDD are excluded.

| # | variant | stop | mode | param | CAGR | ΔCAGR | MDD | ΔMDD | n_stops | longest (d) | eff. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `09_EMA_N150_th5_bL3_sL-1_sl30_next` | 30% | next_signal | nan | +24.42% | -0.03% | +51.92% | +10.35% | 12 | 891 | 103.48 |
| 2 | `19_EMA_N200_th5_bL2_sL0_sl25_next` | 25% | next_signal | nan | +17.00% | +0.24% | +39.05% | +24.60% | 8 | 721 | 101.19 |
| 3 | `19_EMA_N200_th5_bL2_sL0_sl25_cool63` | 25% | time_cooldown | 63 | +16.96% | +0.20% | +44.56% | +19.09% | 9 | 63 | 94.33 |
| 4 | `19_EMA_N200_th5_bL2_sL0_sl25_rec15` | 25% | recovery_trigger | 0.15 | +16.95% | +0.20% | +46.71% | +16.94% | 9 | 174 | 85.53 |
| 5 | `05_EMA_N100_th5_bL2_sL0_sl25_cool21` | 25% | time_cooldown | 21 | +18.44% | -0.12% | +37.91% | +9.71% | 6 | 21 | 81.95 |
| 6 | `16_SMA_N200_th5_bL2_sL0_sl25_rec5` | 25% | recovery_trigger | 0.05 | +17.20% | +0.29% | +43.22% | +20.08% | 10 | 41 | 69.94 |
| 7 | `11_EMA_N100_th5_bL3_sL-1_sl40_cool21` | 40% | time_cooldown | 21 | +23.27% | +0.19% | +57.64% | +10.97% | 7 | 21 | 56.99 |
| 8 | `17_SMA_N100_th5_bL2_sL0_sl35_rec10` | 35% | recovery_trigger | 0.1 | +15.83% | -0.10% | +51.44% | +4.79% | 3 | 133 | 46.73 |
| 9 | `17_SMA_N100_th5_bL2_sL0_sl35_cool126` | 35% | time_cooldown | 126 | +16.04% | +0.10% | +51.44% | +4.79% | 3 | 126 | 46.15 |
| 10 | `01_EMA_N150_th5_bL3_sL0_sl30_rec15` | 30% | recovery_trigger | 0.15 | +27.60% | -0.07% | +49.71% | +4.27% | 14 | 262 | 42.71 |
| 11 | `13_SMA_N100_th5_bL3_sL0_sl40_cool21` | 40% | time_cooldown | 21 | +22.66% | +0.07% | +69.55% | +4.08% | 9 | 21 | 40.79 |
| 12 | `02_EMA_N150_th5_bL2_sL0_sl20_rec15` | 20% | recovery_trigger | 0.15 | +19.37% | +0.13% | +34.18% | +4.87% | 14 | 262 | 36.57 |
| 13 | `16_SMA_N200_th5_bL2_sL0_sl25_cool21` | 25% | time_cooldown | 21 | +17.53% | +0.62% | +43.22% | +20.08% | 10 | 21 | 32.55 |
| 14 | `19_EMA_N200_th5_bL2_sL0_sl25_rec5` | 25% | recovery_trigger | 0.05 | +17.52% | +0.77% | +39.05% | +24.60% | 9 | 41 | 32.05 |
| 15 | `18_EMA_N150_th5_bL2_sL-1_sl20_next` | 20% | next_signal | nan | +16.05% | -0.17% | +44.79% | +5.35% | 12 | 903 | 31.20 |
| 16 | `05_EMA_N100_th5_bL2_sL0_sl40_cool126` | 40% | time_cooldown | 126 | +18.81% | +0.25% | +40.27% | +7.36% | 1 | 126 | 29.32 |
| 17 | `15_EMA_N200_th0_bL3_sL0_sl40_cool126` | 40% | time_cooldown | 126 | +20.56% | +0.05% | +63.51% | +2.66% | 8 | 126 | 26.63 |
| 18 | `19_EMA_N200_th5_bL2_sL0_sl25_rec10` | 25% | recovery_trigger | 0.1 | +17.57% | +0.82% | +42.15% | +21.50% | 9 | 138 | 26.30 |
| 19 | `08_SMA_N200_th2_bL2_sL0_sl20_rec10` | 20% | recovery_trigger | 0.1 | +17.29% | +0.05% | +39.82% | +2.57% | 17 | 170 | 25.74 |
| 20 | `03_EMA_N100_th5_bL3_sL0_sl40_rec10` | 40% | recovery_trigger | 0.1 | +26.51% | -0.23% | +56.92% | +5.84% | 4 | 56 | 25.52 |

## Average effect by mode

> Means across all (base, variant) pairs within the same mode.

| mode | n | ΔCAGR (avg) | ΔMDD (avg) | n_stops (avg) |
|---|---|---|---|---|
| next_signal | 120 | -7.51% | +0.18% | 12.3 |
| time_cooldown | 360 | -5.40% | -2.86% | 20.1 |
| recovery_trigger | 360 | -4.94% | -3.70% | 21.2 |

## Average effect by stop level

| stop_loss_pct | n | ΔCAGR (avg) | ΔMDD (avg) | n_stops (avg) | frac positive (MDD↓) |
|---|---|---|---|---|---|
| 15% | 140 | -13.64% | -6.87% | 45.1 | 30.0% |
| 20% | 140 | -7.80% | -1.99% | 28.2 | 40.0% |
| 25% | 140 | -5.58% | -2.50% | 18.7 | 35.7% |
| 30% | 140 | -2.11% | -2.05% | 11.7 | 31.4% |
| 35% | 140 | -2.36% | -1.86% | 8.1 | 37.1% |
| 40% | 140 | -1.53% | -1.44% | 5.0 | 28.6% |
