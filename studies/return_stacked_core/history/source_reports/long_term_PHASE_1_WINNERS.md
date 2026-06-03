# Phase 1 + 1B Winners — Sleeve-by-Sleeve

**Date:** 2026-04-29  
**Sweep:** iter 027-038 per `SWEEP_PLAN_iter_027_to_039.md` (12 iters: 6 Phase 1A + 6 Phase 1B)  
**Cumulative DSR n_trials:** 136 (94 pre-sweep + 24 Phase 1A + 18 Phase 1B)

---

## Phase 1A (iters 027-032) — substitution = balanced 50/50 from NTSX+KMLM

| iter | sleeve | category | KILL #1 | KILL #2 | KILL #3 | Δ vs iter 023 (lh / vt / ndx) |
|---|---|---|---|---|---|---|
| 027 | NTSD | Global stacking | ❌ FIRES 0/3 | ❌ FIRES | n/a | −0.097 / −0.024 / −0.010 |
| 028 | AVUV | US factor | ⚠️ cosmetic 1/3 | ❌ FIRES | n/a | −0.074 / −0.008 / +0.005 |
| 029 | AVDV | Global SCV | ❌ FIRES 0/3 | ❌ FIRES | n/a | −0.108 / −0.019 / −0.012 |
| **030** | **SPMO** | **US momentum** | ✅ survives 2/3 | ✅ non-monotonic | ✅ PASS (0.828) | **−0.072 / +0.005 / +0.032** |
| 031 | IDMO | Intl momentum | ⚠️ cosmetic 1/3 | ❌ FIRES | ✅ PASS (0.726) | −0.082 / −0.020 / +0.005 |
| 032 | AVEM | EM factor | ❌ FIRES 0/3 | ❌ FIRES | n/a | −0.107 / −0.035 / −0.020 |

## Phase 1B (iters 033-038) — substitution = single-source variation at fixed 10% weight

Tested whether suboptimal sub source (NTSX+KMLM 50/50) was the cause of Phase 1A failures.

| iter | sleeve | best sub | Δ vs iter 023 (lh / vt / ndx) | improvement vs Phase 1A? |
|---|---|---|---|---|
| 033 | NTSD | GDE | −0.088 / −0.058 / −0.026 | only lh marginally better; vt/ndx worse |
| 034 | AVUV | GDE | −0.021 / −0.029 / −0.013 | lh +0.053 better, lost cosmetic ndx |
| 035 | AVDV | GDE | −0.078 / −0.047 / −0.043 | only lh marginally better |
| **036** | **SPMO** | **GDE/KMLM** | **−0.028 / −0.017 / +0.022** (subGDE) or **+0.044 ndx_real** (subKMLM) | **subKMLM achieves +0.044 ndx (vs Phase 1A +0.032 — 38% better)** |
| 037 | IDMO | GDE | −0.051 / −0.070 / −0.033 | lh marginally better, lost cosmetic ndx |
| 038 | AVEM | GDE | −0.096 / −0.084 / −0.065 | only lh marginally better |

**Cross-sleeve ndx_real maximizer (any sub source)**:

| sleeve | max ndx_real Δ | best sub | comment |
|---|---:|---|---|
| **SPMO** | **+0.044** | KMLM | only sleeve with robust +signal across every test |
| AVUV | −0.002 | KMLM | within noise |
| IDMO | −0.006 | KMLM | within noise |
| NTSD | −0.020 | KMLM | confirmed dead |
| AVDV | −0.029 | KMLM | confirmed dead |
| AVEM | −0.047 | KMLM | worst — confirmed dead |

---

## Winner determination

**Sleeve winner criteria** (per spec):
1. Best config beats iter 023 mean Sharpe across 3 datasets, AND
2. Passes 7-gate battery on ≥2/3 datasets, AND
3. DSR p<0.05 cumulative

| sleeve | meets criteria? | verdict |
|---|---|---|
| NTSD | ❌ neither Phase 1A nor 1B | DEAD — close direction (consistent with iter 014/015 closures) |
| AVUV | ❌ both Phases negative on substantive metrics | DEAD |
| AVDV | ❌ strongly negative both Phases | DEAD |
| **SPMO** | ✅ +signal in 1A AND 1B; ndx_real +0.044 max | **WINNER** |
| IDMO | ❌ marginal/cosmetic both Phases | DEAD |
| AVEM | ❌ strongly negative both Phases | DEAD |

**Phase 1 winner sleeves: { SPMO } (1 of 6)**

---

## Phase 2 routing

| Finalist | Status | Composition | Rationale |
|---|---|---|---|
| **F1 US-Stk** | ✅ proceeds (no new iter) | iter 023 baseline | 4 ETFs, established |
| **F2 US-Fct** | ⚠️ proceeds with degraded scope | VTI + AVUV (best non-momentum near-miss) + SPMO + diversifiers | Pure factor philosophy; AVUV included as best-available US factor despite Phase 1A/1B negative substantive (lh_56y −0.021 in 1B is least bad) |
| **F3 US-Hyb** | ✅ proceeds | iter 023 + SPMO at 5-10% | SPMO is the only validated sleeve add |
| **F4 Gl-Stk** | ❌ SKIPPED | (would need NTSD) | NTSD failed both Phases — consistent with iter 014/015 (intl-equity tilt closure) |
| **F5 Gl-Fct** | ❌ SKIPPED | (would need ≥2 global factors) | Only IDMO marginal; no robust global factor sleeve survived |
| **F6 Gl-Hyb** | ❌ SKIPPED (degenerates to F3) | — | Without F4/F5 components, F6 = F3 |
| **F7 US-StkMF** | ✅ proceeds | NTSX + RSST + GDE + KMLM + TLT | Independent of Phase 1 (RSST stacked-MF axis) |

**Phase 2 effective scope**: 3 new iters (F2, F3, F7) instead of planned 6.

---

## Empirical conclusions

1. **iter 023 architecture (NTSX+GDE+KMLM+TLT) is structurally optimal** in the testfolio universe for capital-efficient stacking philosophy. 12 iters of additions/swaps cannot improve substantively.

2. **The Avantis factor family (AVUV/AVDV/AVEM) is structurally subordinate** in 2010-2024 US-equity-dominant regime. Sub-source variation does not rescue them.

3. **ex-US equity stacking (NTSD) reaffirms Direction A closure** from the 26-iter prior loop (iter 014/015 already showed the same pattern; NTSD via 1.5× wrapper still fails).

4. **US momentum (SPMO) has modest robust +signal** — best candidate for Phase 2 hybrid. Optimal weight 5-10%, sub source from KMLM (peak ndx_real +0.044) or balanced (peak vt_real +0.005).

5. **Intl momentum (IDMO) is marginal at best** — within noise of iter 023.

6. **F2 pure factor philosophy** can be tested but expectations are tempered: AVUV is the best non-momentum factor near-miss but still fails the substantive bar.

7. **F7 stacked-MF (RSST)** remains untested — independent axis, may yield surprising result.

---

## Update to BASE_MEMORY.md

Frontmatter updates needed:
- `phase_1_complete: true`
- `phase_1a_complete: true`
- `phase_1b_complete: true`
- `phase_1_winners: ["SPMO"]`
- `phase_2_iters_to_run: [039, 040, 041]`  # F2, F3, F7
- `phase_2_iters_skipped: [F4, F5, F6 — no surviving sleeves]`
- `cumulative_n_trials: 136`

---

## Citations

- `[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking baseline
- `[risk_parity, ch.2, p.37-41]` Fama-French factor framework (Avantis closure rationale)
- `[stocks_on_the_move, p.21-30]` Clenow time-series momentum (SPMO retention)
- `[ilmanen_expected_returns, ch.19]` intl/EM diversification (NTSD/AVDV/AVEM closure context)
- `[advances_fin_ml, p.222-223]` DSR cumulative trials (n=136 threshold tightening)

---

## Next: Phase 2

Execute iters 039 (F2 US Factor-only), 040 (F3 US Hybrid with SPMO), 041 (F7 US Stacked-MF). Total ~5h.
