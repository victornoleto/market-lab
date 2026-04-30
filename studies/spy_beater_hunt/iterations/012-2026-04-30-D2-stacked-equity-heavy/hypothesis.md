# spy_beater_hunt iter 012 — D2 Stacked Equity Heavy (NTSX + UPRO + AVUV)

**Date**: 2026-04-30
**Type**: Post-impossibility Tier 3 sanity check on KILL #33 (architectural ceiling)
**Slug**: `D2-stacked-equity-heavy`
**Status of hunt entering this iter**: `closed_no_winner` (iter 011 declared IMPOSSIBILITY_RESULT)

---

## Why this iter exists (context)

Iter 011 declared IMPOSSIBILITY_RESULT and fired KILL #33 (structural
architectural ceiling at score 67 across 4 control families). The
final report explicitly flagged Tier 3 directions as **untested**:
"D1 (concentrated growth + monthly momentum), C2 (CAPE-timing), D2
(NTSX + UPRO + AVUV stacked equity heavy)".

This iter tests **D2** as the **5th distinct architectural family** to
either:
- **Reinforce KILL #33** (5th family also caps ≤ 67 → architectural
  ceiling claim strengthened from 4-family to 5-family evidence).
- **Invalidate KILL #33** (D2 surprisingly scores ≥ 75 → ceiling claim
  was premature; hunt reopens for iter 013+).

D2 is the most architecturally distinct from the 4 closed families:
- A1/A3 SPY-track LRS: regime-gated leverage rotation
- A2 TQQQ-track LRS: regime-gated NDX leverage
- B1/B2 HFEA: leveraged barbell (UPRO + TMF)
- C1 vol-target: dynamic leverage on SPY

D2 has **no regime gate**, **no leveraged duration**, **no vol
targeting** — pure stacking + factor tilt + LETF. This isolates
whether structural lift comes from removing the regime-gate framework
entirely.

---

## Hypothesis

**H₁ (primary)**: A static stacking + factor portfolio (NTSX 90/60 +
UPRO 3× SPY + AVUV factor tilt) **cannot exceed score 67** on the
spy_beater rubric on (lh_56y, spy_real). Pure equity exposure with
factor concentration accumulates MDD too fast in 2008/2022 stress
without a regime gate.

**H₂ (secondary)**: Pure LETF + factor (d2_upro_avuv = 50% UPRO + 50%
AVUV with no bonds) **fails MDD bar** (mean MDD > 55.17%) because 1.5×
notional equity exposure with concentrated SCV factor in 2008 stress
drives lh_56y/spy_real MDD > 60%. KILL #38 candidate.

**H₃ (tertiary)**: NTSX-stacking-anchored variant (d2_ntsx_avuv) clears
all 3 bars (NTSX is the long_term_portfolio incumbent baseline, mean
MDD ~17%) but **CAGR-caps below 14%** (since AVUV factor lift is
modest 1-2pp over SPY long-run), scoring ≤ 65.

---

## Configs (3 — keep cumulative n_trials low)

| name                  | NTSX | UPRO | AVUV | thesis                                                                 |
|----------------------|-----:|-----:|-----:|------------------------------------------------------------------------|
| d2_ntsx_avuv         | 0.50 | 0.00 | 0.50 | Stacking + factor, no extra LETF. NTSX = 90% S&P + 60% IEF effective.  |
| d2_ntsx_upro_avuv    | 0.35 | 0.35 | 0.30 | Mixed stacking + LETF + factor. ~1.65× equity notional + factor tilt.  |
| d2_upro_avuv         | 0.00 | 0.50 | 0.50 | Pure LETF + factor, no bonds. ~1.5× equity notional + SCV concentrate. |

**Cumulative n_trials**: prior 35 (preserved from iter 011 meta-iter) + 3 = **38**.

---

## Pre-committed KILL conditions (NEW for this iter)

KILLs #1-#35 already declared. Numbering continues at #36.

### KILL #36 (D2 reinforces KILL #33 — 5th family caps ≤ 67)

**Definition**: If best D2 config score ≤ 67, the architectural
ceiling claim from iter 011 is **strengthened from 4-family to
5-family evidence**. Hunt remains CLOSED.

**Trigger**: `max_score_d2 ≤ 67` AND any single bar fail OR no config
PASSES all 3 bars with score ≥ 75.

**Action if FIRED**: update BASE_MEMORY frontmatter
`architectural_ceiling: confirmed_5_families` and reinforce iter 011
verdict. F1+SPLIT remains deploy fallback.

### KILL #37 (sanity-check breaks ceiling — KILL #33 INVALIDATED)

**Definition**: If best D2 config score ≥ 75 with all 3 bars met, KILL
#33 was premature; ceiling is NOT structural. Hunt **REOPENS**.

**Trigger**: `max_score_d2 ≥ 75 AND all 3 bars met`.

**Action if FIRED**: revert BASE_MEMORY status to `hunting`, plan iter
013+ extending D2 sensitivity sweep, document KILL #33 retraction in
FINAL_REPORT_spy_beater_failed.md.

### KILL #38 (pure equity LETF + factor fails MDD bar)

**Definition**: `d2_upro_avuv` (no bonds, 50% UPRO + 50% AVUV) MDD
mean ≥ 55.17% on (lh_56y, spy_real). Establishes that **regime gate
or stacking is a NECESSARY component** for MDD bar; pure LETF +
factor is structurally subordinate.

**Trigger**: `d2_upro_avuv mean_mdd ≥ 0.5517`.

**Action if FIRED**: confirms architectural framework; **regime gate
or duration sleeve is the binding constraint** for MDD bar in
spy_beater rubric.

---

## Expected outcomes (priors)

| config              | expected mean CAGR | expected mean MDD | expected score | bar pass? |
|---------------------|-------------------:|------------------:|---------------:|-----------|
| d2_ntsx_avuv        | 11-13%             | 25-35%            | 55-62          | likely 3/3|
| d2_ntsx_upro_avuv   | 14-17%             | 45-60%            | 60-68          | maybe 2/3 |
| d2_upro_avuv        | 16-20%             | 60-75%            | 50-65          | maybe 2/3 |

Most likely outcome: **all 3 configs score 50-67**, KILL #36 fires,
ceiling reinforced. ~5% chance any config exceeds 75 (KILL #37 path).

---

## INCOMPLETE flags

- **Tier 3 priority**: D2 was flagged as ~5% lift probability per
  iter 011's premature-closure analysis. This iter is **due
  diligence**, not a primary hunt direction.
- **NTSX coverage**: NTSXSIM is synthesised via proxies.py blueprint
  (90% SPY + 60% IEF − 50% CASHX); 1986+ coverage matches lh_56y. No
  daily-reset decay modelled in proxy (NTSX is futures-stacked, not
  LETF, so this is realistic).
- **AVUV coverage**: AVUVSIM via avuv_synth_returns_from_cache, 1926+
  coverage; SCV factor returns synthesised from FF data 1926-1990s.
- **Plain stacking already exhausted by long_term_portfolio**: F1+SPLIT
  (NTSX 25 + GDE 25 + KMLM 17.5 + DBMF 17.5 + TLT 15) topped out at
  CAGR 10.76%. D2 here adds factor tilt (AVUV) that long_term_portfolio
  iter 027-038 closed as "no edge over F1+SPLIT". This iter's *novel*
  variant is the LETF-heavy d2_ntsx_upro_avuv combining stacking + 3×
  LETF, which long_term_portfolio did NOT test.
- **DSR penalty inflation**: cumulative_n_trials = 38 after this iter;
  worst p-value bar at p=0.05 still has comfortable margin (iter 010
  worst was 5.02e-3 << 0.05).

---

## Citations

- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking —
  NTSX 90/60 leg blueprint; F1+SPLIT incumbent baseline. D2 tests
  whether *equity-heavy* stacking (vs F1+SPLIT's bonds-heavy) clears
  the CAGR bar that F1+SPLIT misses by 0.45pp.
- `[advances_fin_ml, p.31-34]` factor framework — AVUV (SCV) is a
  distinct factor from market beta; tests whether factor tilt + leverage
  achieves what regime-gate + leverage achieved in A1/A2 (CAGR uplift
  with controlled MDD).
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 38;
  preserves statistical integrity for verdict.
- `[advances_fin_ml, p.208-211]` PBO grid-level < 0.5 — selection
  bias controlled at 3-config × 2-dataset = 6-cell grid.
- `[advances_fin_ml, p.196-202]` bootstrap CI — gate G6 99.9% CI low
  > 0 required.
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed LETF decay —
  applies to UPRO leg in d2_ntsx_upro_avuv and d2_upro_avuv (3× SPY
  daily-reset, ~1-3%/y decay drag).
- HFEA Bogleheads 2019 — falsified by iter 008/009; iter 012 tests
  whether *factor + stacking* is a viable substitute for *leveraged
  duration* in the equity-heavy regime.
- Avantis 2019 — AVUV SCV factor mandate.

---

## What this iter does NOT test

- **D1 concentrated growth + monthly momentum** — could be future iter 013
  if KILL #36 fires and user requests further closure.
- **C2 CAPE-timing** — flagged as low-credibility per
  PROMISING_DIRECTIONS.md ("CAPE has been 'high' for 20+ years").
- **GDE-stacked equity** (gold + SPY): partially explored in
  long_term_portfolio F1+SPLIT; redundant.
- **Sensitivity sweep within D2** — only 3 corner-point configs to
  probe the architecture; sensitivity weights deferred unless KILL
  #37 fires.

---

## Decision tree post-iter

| outcome                           | action                                             | KILL fired |
|-----------------------------------|----------------------------------------------------|-----------:|
| All 3 configs score ≤ 67          | Reinforce KILL #33 across 5 families. Hunt CLOSED. | #36        |
| Any config scores 68-74           | Document; hunt remains CLOSED at 67-cap            | none       |
| Any config scores ≥ 75 + 3 bars   | INVALIDATE KILL #33. Reopen hunt for iter 013+.    | #37        |
| `d2_upro_avuv` MDD ≥ 55%          | Confirms regime-gate/stacking necessity for MDD.   | #38        |

Most likely path: KILL #36 + KILL #38 both fire, hunt remains CLOSED,
F1+SPLIT incumbent fallback unchanged. Mandate §1 100% Plano C
unchanged.
