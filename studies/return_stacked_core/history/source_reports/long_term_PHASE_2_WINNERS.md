# Phase 2 Provisional Ranking + MF Sensitivity Target

**Date:** 2026-04-30  
**Sweep:** iter 039-041 per `SWEEP_PLAN_iter_027_to_039.md`  
**Cumulative DSR n_trials:** 148 (148 Phase 1A+1B+2; 12 trials this Phase = 4 configs × 3 iters)

---

## All 4 finalists (Phase 2 + F1 baseline)

| F | iter | slug | best config | ETFs | Notional | Sharpe lh / vt / ndx | Δ vs iter 023 | CAGR lh / vt / ndx | MDD lh / vt / ndx | Score NEW | Tier |
|---|---|---|---|---:|---:|---|---|---|---|---:|---|
| **F1** | 023 | iter011-plus-TLT-sleeve | tlt_mod_25_25_35_15 | 4 | 132% | 1.189 / 1.004 / 1.135 | (baseline) | 11.50% / 10.13% / 10.62% | 21.13% / 17.40% / 11.76% | 86 | STRONG |
| **F2** | 039 | F2-US-Factor-only | f2_spmo_heavy | 6 | 100% | 1.086 / 0.874 / 1.087 | −0.103 / −0.130 / −0.048 | ~12.5% / ~10.4% / ~10.3% | ~30% / ~25% / ~28% | 85 | STRONG |
| **F3** | 040 | F3-US-Hybrid-SPMO | f3_spmo_5_subKMLM | 5 | 135% | 1.107 / 1.008 / 1.173 | −0.082 / **+0.004** / **+0.038** | ~11.7% / ~10.5% / ~11.4% | ~22% / ~18% / ~12% | 88 | STRONG |
| **F7** | 041 | F7-US-Stacked-MF | f7_lite | 5 | 150% | 1.072 / 0.978 / 1.144 | −0.117 / −0.026 / +0.009 | **12.73% / 11.90% / 12.86%** | ~25% / ~21% / ~14% | **91** | **WINNER** |

(F4 Gl-Stk, F5 Gl-Fct, F6 Gl-Hyb skipped per Phase 1 routing.)

---

## Multi-criteria provisional scoring preview

Pre-final-report scoring (full multi-criteria in Task 23):

| F | C1 Sharpe (25) | C2 CAGR (12) | C3 MDD (13) | C4 Simpl (15) | C5 Expense (10) | C6 Robust (10) | C7 Deploy (15) | TOTAL |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| F1 | **22-23** | 6-8 | 11-13 | **15** (4 ETFs) | 7-8 | 8-9 | TBD | ~75-77 |
| F2 | 17-18 | 7-8 | 8-10 | 12 (6 ETFs) | **10** (lowest TER) | 7-8 | TBD | ~65-68 |
| F3 | 21-22 | 6-8 | 11-12 | 14 (5 ETFs) | 7-8 | 8-9 | TBD | ~73-76 |
| F7 | 18-19 | **10-11** (highest CAGR) | 9-11 | 13 (5 ETFs) | 6-7 (RSST 0.98%) | 8-9 | TBD | ~71-74 |

**Provisional ranking** (with C7 Inter Internacional pending user fill):
1. **F1 (iter 023)** — Sharpe + simplicity leader
2. **F3 (iter 040 SPMO)** — close 2nd; ndx_real edge
3. **F7 (iter 041 RSST)** — CAGR leader, score-gate winner
4. **F2 (iter 039 pure factor)** — clearly weakest

**Provisional winner**: **F1 or F3** depending on regime weighting.

---

## Phase 3 MF sleeve sensitivity target

**Decision:** run iter 042 MF sensitivity on **F1 (iter 023 baseline)**.

**Rationale:**
1. F1 is the architectural baseline. Result generalizes to F3 (same NTSX/GDE/KMLM/TLT structure with SPMO sleeve added).
2. F7 uses RSST (which embeds MF internally) + smaller standalone KMLM (10-20%). Test on F7 separately if F7 wins multi-criteria.
3. F2 is non-competitive — no value testing MF sub there.

**Iter 042 configs** (substitute KMLM 35% in iter 023 with each MF candidate):

| config | MF substitution | rationale |
|---|---|---|
| mf_kmlm | KMLMSIM (baseline) | published index, transparent, 38y |
| mf_dbmf | DBMFSIM | 5× AUM ($3.2B), SG CTA Index proxy, 26y window |
| mf_split | 50% KMLMSIM + 50% DBMFSIM | engine + AUM diversification |
| mf_cta_proxy | KMLMSIM scaled (CTA Simplify proxy) | INCOMPLETE flag prominent |

**Expected outcome:**
- KMLM/DBMF/split similar Sharpe (~1.1-1.2 lh_56y, validated by Phase 1)
- Best deploy choice = DBMF (highest AUM = lowest closure risk for 20-30y) or split (engine diversification).

---

## Update to BASE_MEMORY.md

Frontmatter updates:
- `phase_2_complete: true`
- `phase_2_finalists: [F1=iter023, F2=039, F3=040, F7=041]`
- `phase_2_skipped: [F4, F5, F6 — no surviving global sleeves]`
- `provisional_winner_iter: "023"` (subject to multi-criteria final scoring)
- `mf_sensitivity_target: "F1 (iter 023)"`
- `cumulative_n_trials: 148`

---

## Next: Phase 3

Execute iter 042 MF sleeve sensitivity (Task 22). Then Task 23 produces FINAL_REPORT_seven_portfolios.md (4 finalists actually) with full multi-criteria scoring. Task 24 user decision.
