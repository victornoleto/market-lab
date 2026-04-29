# Iter 035 — Final Report — `AVDV-realloc`

**Verdict (NEW SPY-only mandate, 2026-04-29 reframing)**: **STRONG 84/100** — `winner_conditions_met=True`.

**Verdict (LEGACY avg(SPY,VT) + 0.10)**: **STRONG 84/100** — `winner_conditions_met=True`.

**Primary citation**: [ilmanen_expected_returns, ch.19]

---

## Selected config: `avdv10_subGDE`

Weights:

```json
{
  "NTSXSIM": 0.25,
  "GDESIM": 0.15,
  "KMLMSIM": 0.35,
  "TLTSIM": 0.15,
  "AVDVSIM": 0.1
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 1.111 | 10.17% | 19.32% | 6/7 | 5.28e-08 |
| **vt_real** | 0.957 | 8.90% | 18.11% | 6/7 | 7.51e-04 |
| **ndx_real** | 1.092 | 9.47% | 11.86% | 6/7 | 2.42e-04 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|
| avdv10_subNTSX | 1.087 | 0.961 | 1.086 |
| avdv10_subGDE | 1.111 | 0.957 | 1.092 |
| avdv10_subKMLM | 1.052 | 0.953 | 1.106 |

## NEW SPY-only Sharpe edge

| dataset | bench (SPY) | hurdle (+0.05) | candidate | edge | passes? |
|---|---:|---:|---:|---:|:-:|
| lh_56y | 0.680 | 0.730 | 1.111 | +0.431 | [OK] |
| vt_real | 0.900 | 0.950 | 0.957 | +0.057 | [OK] |
| ndx_real | 0.900 | 0.950 | 1.092 | +0.192 | [OK] |

## Robustness (5y rolling Sharpe, anchor dataset)

- bonus_pts: 5/5
- pct_positive_sharpe: 100.00%
- n_windows: 27
- anchor_dataset: lh_56y

## INCOMPLETE flags

- **AVDVSIM** = `VSSSIM + 100bps/y tilt premium`. INCOMPLETE — VSSSIM is passive intl small-cap (no quality screen); 100bps tilt premium estimates Avantis intl small-cap value active edge. Real AVDV live since 2019.

## Substitution source comparison (fixed 10% AVDV weight)

| sub source | NTSX | GDE | KMLM | Sharpe lh_56y | Sharpe vt_real | Sharpe ndx_real | Δ vs iter 023 |
|---|---:|---:|---:|---:|---:|---:|---|
| **subGDE** *(best, selected)* | 25% | 15% | 35% | 1.1113 | 0.9569 | 1.0920 | −0.078 / −0.047 / −0.043 |
| subNTSX | 15% | 25% | 35% | 1.0872 | 0.9614 | 1.0855 | −0.102 / −0.043 / −0.050 |
| subKMLM | 25% | 25% | 25% | 1.0519 | 0.9532 | 1.1063 | −0.137 / −0.051 / −0.029 |

**Iter 023 baseline**: lh_56y=1.189, vt_real=1.004, ndx_real=1.135. **All 3 sub sources beat iter 023 on 0/3 datasets.**

## Phase 1A vs Phase 1B comparison

| metric | Phase 1A iter 029 best (`avdv_lite`, 5%, sub NTSX+KMLM 50/50) | Phase 1B iter 035 best (`avdv10_subGDE`, 10%, sub GDE) |
|---|---|---|
| Sharpe lh_56y | 1.081 | 1.111 |
| Sharpe vt_real | 0.985 | 0.957 |
| Sharpe ndx_real | 1.123 | 1.092 |
| Δ vs iter 023 | −0.108 / −0.019 / −0.012 | −0.078 / −0.047 / −0.043 |
| Datasets beating 023 | 0/3 | 0/3 |

Phase 1B `subGDE` at 10% improves lh_56y (+0.030) but degrades vt_real (−0.028) and ndx_real (−0.031) vs Phase 1A best. Net: lh_56y improvement does not compensate for live-window degradation.

## Lesson

**KILL #1 (no-positive-config) ✅ FIRED again** under all 3 sub sources. AVDV sleeve closure REAFFIRMED.

- **Best sub source**: `subGDE` (selected). Same pattern as iter 033/034 — substituting from GDE preserves long-history KMLM crisis-alpha and NTSX equity carry, so lh_56y benefits most. But intl SCV factor still under-performs the iter 023 wrapper at 1× notional.
- **Worst sub source**: `subKMLM` (lh_56y −0.137). Confirms KMLM is the load-bearing crisis-alpha sleeve.
- **Live windows (vt_real, ndx_real) all 3 sub sources cluster within ~0.02 Sharpe** — confirming intl SCV at 1× under any substitution drags the post-2008 "death of value" + intl underperformance regime.
- **AVDV sleeve closure REAFFIRMED.** F5 Global Factor-only finalist (iter 036 original sweep) cannot proceed via AVDV. Combined with iter 029 (AVDV closed in Phase 1A), iter 028 (AVUV cosmetic-only), and iter 032 (AVEM closed) — all 3 Avantis factor sleeves fail at any sub source. Citation `[ilmanen_expected_returns, ch.19]` framework is honest; the 1× factor exposure cannot beat 1.5×-leveraged stack with KMLM crisis-alpha.
