# Phase 3 — Cross-dataset gate verdict

> Gates on every (common_base × combo) pair across all 3 datasets.
> Common bases: ['EMA_N150_th5_bL2_sL0', 'EMA_N150_th5_bL3_sL0', 'SMA_N200_th0_bL2_sL0', 'SMA_N200_th0_bL3_sL0']
> n_trials (DSR, cumulative): 4020


## Results by (base, combo)

Spec §0 criterion: **≥ 5/7 gates in educational AND ≥ 4/7 in each real dataset**.

| base | combo | edu CAGR / ΔCAGR | edu MDD / ΔMDD | edu gates | spy gates | ndx gates | spec §0 met? |
|---|---|---|---|---|---|---|---|
| `EMA_N150_th5_bL2_sL0` | sl20_cool21_composite05 | +17.53% / -1.70% | +31.32% / +7.73% | **6/7** | 3/7 | 3/7 | ❌ |
| `EMA_N150_th5_bL2_sL0` | sl20_cool21_cape05 | +16.88% / -2.35% | +31.68% / +7.36% | **6/7** | 3/7 | 3/7 | ❌ |
| `EMA_N150_th5_bL2_sL0` | sl30_rec10_composite05 | +16.77% / -2.47% | +40.89% / -1.84% | **6/7** | 3/7 | 4/7 | ❌ |
| `EMA_N150_th5_bL2_sL0` | sl30_rec10_cape05 | +15.87% / -3.36% | +40.89% / -1.84% | **5/7** | 3/7 | 4/7 | ❌ |
| `EMA_N150_th5_bL3_sL0` | sl20_cool21_composite05 | +18.78% / -8.89% | +51.13% / +2.85% | **5/7** | 3/7 | 4/7 | ❌ |
| `EMA_N150_th5_bL3_sL0` | sl20_cool21_cape05 | +21.52% / -6.15% | +54.17% / -0.19% | **5/7** | 3/7 | 4/7 | ❌ |
| `EMA_N150_th5_bL3_sL0` | sl30_rec10_composite05 | +23.69% / -3.98% | +46.78% / +7.20% | **6/7** | 3/7 | 4/7 | ❌ |
| `EMA_N150_th5_bL3_sL0` | sl30_rec10_cape05 | +24.01% / -3.66% | +44.55% / +9.43% | **6/7** | 3/7 | 3/7 | ❌ |
| `SMA_N200_th0_bL2_sL0` | sl20_cool21_composite05 | +13.63% / -1.65% | +55.75% / -1.57% | **5/7** | 4/7 | 3/7 | ❌ |
| `SMA_N200_th0_bL2_sL0` | sl20_cool21_cape05 | +12.96% / -2.33% | +45.87% / +8.31% | **5/7** | 3/7 | 3/7 | ❌ |
| `SMA_N200_th0_bL2_sL0` | sl30_rec10_composite05 | +12.61% / -2.67% | +46.06% / +8.12% | **5/7** | 3/7 | 3/7 | ❌ |
| `SMA_N200_th0_bL2_sL0` | sl30_rec10_cape05 | +12.66% / -2.62% | +40.76% / +13.42% | **5/7** | 3/7 | 4/7 | ❌ |
| `SMA_N200_th0_bL3_sL0` | sl20_cool21_composite05 | +15.28% / -6.81% | +72.73% / -2.44% | **5/7** | 3/7 | 3/7 | ❌ |
| `SMA_N200_th0_bL3_sL0` | sl20_cool21_cape05 | +19.09% / -3.01% | +57.06% / +13.23% | **5/7** | 3/7 | 3/7 | ❌ |
| `SMA_N200_th0_bL3_sL0` | sl30_rec10_composite05 | +19.22% / -2.87% | +70.00% / +0.28% | **5/7** | 3/7 | 3/7 | ❌ |
| `SMA_N200_th0_bL3_sL0` | sl30_rec10_cape05 | +18.86% / -3.23% | +52.11% / +18.18% | **5/7** | 3/7 | 3/7 | ❌ |

## Gate-by-gate breakdown (pass/fail matrix)

For each (base, combo) × dataset, which specific gates fail? This matters because G1 PBO is grid-level (same verdict for all configs in a dataset) but G2-G7 are per-config.

| base | combo | dataset | G1 PBO | G2 DSR | G3 WF | G4 OOS | G5 FWD | G6 BS | G7 XLib |
|---|---|---|---|---|---|---|---|---|---|
| `EMA_N150_th5_bL2_sL0` | sl20_cool21_composite05 | educational | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `EMA_N150_th5_bL2_sL0` | sl20_cool21_composite05 | spy_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `EMA_N150_th5_bL2_sL0` | sl20_cool21_composite05 | ndx_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `EMA_N150_th5_bL2_sL0` | sl20_cool21_cape05 | educational | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `EMA_N150_th5_bL2_sL0` | sl20_cool21_cape05 | spy_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `EMA_N150_th5_bL2_sL0` | sl20_cool21_cape05 | ndx_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `EMA_N150_th5_bL2_sL0` | sl30_rec10_composite05 | educational | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `EMA_N150_th5_bL2_sL0` | sl30_rec10_composite05 | spy_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `EMA_N150_th5_bL2_sL0` | sl30_rec10_composite05 | ndx_real | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `EMA_N150_th5_bL2_sL0` | sl30_rec10_cape05 | educational | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `EMA_N150_th5_bL2_sL0` | sl30_rec10_cape05 | spy_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `EMA_N150_th5_bL2_sL0` | sl30_rec10_cape05 | ndx_real | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `EMA_N150_th5_bL3_sL0` | sl20_cool21_composite05 | educational | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `EMA_N150_th5_bL3_sL0` | sl20_cool21_composite05 | spy_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `EMA_N150_th5_bL3_sL0` | sl20_cool21_composite05 | ndx_real | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `EMA_N150_th5_bL3_sL0` | sl20_cool21_cape05 | educational | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `EMA_N150_th5_bL3_sL0` | sl20_cool21_cape05 | spy_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `EMA_N150_th5_bL3_sL0` | sl20_cool21_cape05 | ndx_real | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `EMA_N150_th5_bL3_sL0` | sl30_rec10_composite05 | educational | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `EMA_N150_th5_bL3_sL0` | sl30_rec10_composite05 | spy_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `EMA_N150_th5_bL3_sL0` | sl30_rec10_composite05 | ndx_real | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `EMA_N150_th5_bL3_sL0` | sl30_rec10_cape05 | educational | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `EMA_N150_th5_bL3_sL0` | sl30_rec10_cape05 | spy_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `EMA_N150_th5_bL3_sL0` | sl30_rec10_cape05 | ndx_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `SMA_N200_th0_bL2_sL0` | sl20_cool21_composite05 | educational | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `SMA_N200_th0_bL2_sL0` | sl20_cool21_composite05 | spy_real | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `SMA_N200_th0_bL2_sL0` | sl20_cool21_composite05 | ndx_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `SMA_N200_th0_bL2_sL0` | sl20_cool21_cape05 | educational | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `SMA_N200_th0_bL2_sL0` | sl20_cool21_cape05 | spy_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `SMA_N200_th0_bL2_sL0` | sl20_cool21_cape05 | ndx_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `SMA_N200_th0_bL2_sL0` | sl30_rec10_composite05 | educational | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `SMA_N200_th0_bL2_sL0` | sl30_rec10_composite05 | spy_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `SMA_N200_th0_bL2_sL0` | sl30_rec10_composite05 | ndx_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `SMA_N200_th0_bL2_sL0` | sl30_rec10_cape05 | educational | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `SMA_N200_th0_bL2_sL0` | sl30_rec10_cape05 | spy_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `SMA_N200_th0_bL2_sL0` | sl30_rec10_cape05 | ndx_real | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `SMA_N200_th0_bL3_sL0` | sl20_cool21_composite05 | educational | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `SMA_N200_th0_bL3_sL0` | sl20_cool21_composite05 | spy_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `SMA_N200_th0_bL3_sL0` | sl20_cool21_composite05 | ndx_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `SMA_N200_th0_bL3_sL0` | sl20_cool21_cape05 | educational | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `SMA_N200_th0_bL3_sL0` | sl20_cool21_cape05 | spy_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `SMA_N200_th0_bL3_sL0` | sl20_cool21_cape05 | ndx_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `SMA_N200_th0_bL3_sL0` | sl30_rec10_composite05 | educational | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `SMA_N200_th0_bL3_sL0` | sl30_rec10_composite05 | spy_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `SMA_N200_th0_bL3_sL0` | sl30_rec10_composite05 | ndx_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `SMA_N200_th0_bL3_sL0` | sl30_rec10_cape05 | educational | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| `SMA_N200_th0_bL3_sL0` | sl30_rec10_cape05 | spy_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| `SMA_N200_th0_bL3_sL0` | sl30_rec10_cape05 | ndx_real | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |

## Verdict

❌ **No (base, combo) pair meets spec §0 across all 3 datasets** (≥5/7 edu AND ≥4/7 spy AND ≥4/7 ndx simultaneously).
Per-dataset winners exist (see per-dataset reports) but the cross-dataset honesty bar is not met — any candidate that passes in one dataset fails in another.


---
*Citations: spec §0, §6.1, §6.2. PBO grid-level per dataset. DSR uses cumulative `n_trials = 4020`.*
