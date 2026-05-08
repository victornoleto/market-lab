# spy_beater_hunt iter 014 — E1 Hybrid: TSMOM Gate × TQQQ-track Sleeve + KMLM Crisis-Alpha

**Date**: 2026-04-30
**Type**: Cross-product hybrid sanity check on KILL #33 (architectural ceiling). NEW combination: best-MDD gate (D1 TSMOM, iter 013) × best-CAGR sleeve (A2 TQQQ-track + KMLM30 + TLT10, iter 006).
**Slug**: `E1-tsmom-gate-tqqq-crisis-alpha`
**Status of hunt entering this iter**: `closed_no_winner` (iter 011 IMPOSSIBILITY_RESULT, iter 012/013 6-family reinforcement)

---

## Why this iter exists (context)

Iter 013 surfaced an **unexpected positive artefact**: `d1_qqq_6m_tsmom`
achieved the **best mean MDD in the entire hunt** (35.27% vs 49.73% in
iter 006 closest-to-winner). The TSMOM gate's slower reaction (vs daily
SMA cross) helps MDD by avoiding false-positive re-entries during bear
rallies. However D1 capped at score 59 because it sacrificed CAGR (1×
QQQ rather than 3× TQQQ split).

Conversely, iter 006 closest-to-winner (`a6_tqqq_split_kmlm30_tlt10`,
score 67) achieved best CAGR (17.33%) via 60% TQQQ-equivalent leverage
+ KMLM crisis alpha + TLT extension, but its 200d SMA gate left mean
MDD at 49.73% — close to the 55.17% bar but not great.

**Open question that motivates this iter**: does the cross-product
"D1's gate (best MDD) × A2's sleeve (best CAGR)" break the score-67
ceiling? Per `[advances_fin_ml, p.31-34]` factor framework, gate and
sleeve are nominally orthogonal axes; if they truly are orthogonal,
cross-product gains should equal the union of marginal gains.

This iter EXPLICITLY tests the orthogonality assumption that has been
implicit across iters 001-013. KILL #33 fired across 6 single-axis
families; the **cross-product hybrid** has not been tested.

---

## Hypothesis

**H₁ (primary)**: A TSMOM-gated TQQQ+KMLM+TLT sleeve scores **strictly
above** the 67 ceiling because gate and sleeve axes are partially
independent — TSMOM gives ~+5pp MDD relief over 200d SMA on TQQQ-track
(the same direction observed in 1× QQQ in iter 013), while preserving
the same CAGR uplift the TQQQ+KMLM+TLT sleeve produces.

If H₁ holds, expected score lift over iter 006 (67):
- MDD points: +5 to +8 (mean MDD 49.73% → ~42-44% via TSMOM-gate slower
  reaction, anchor 50%/10% range gives ~+3pp on score-axis per +6pp MDD)
- CAGR points: −1 to −2 (TSMOM 6m on TQQQ tends to skip ~5% of late-bull
  upticks vs SMA cross — minor CAGR drag)
- Net: +2 to +6 → predicted score 69-73, possibly 70+ tier (KILL #43 path).

**H₂ (alternative — orthogonality violation)**: Gate and sleeve are
**not** orthogonal — TSMOM's MDD gain on 1× QQQ does NOT transfer to
3× TQQQ at scale because daily-reset decay (3× LETF ≈ 3-5%/y) is the
DOMINANT MDD driver at high leverage, and gate reaction speed only
matters at the margins. In this case mean MDD stays ~50%, CAGR drops
slightly, score caps at ≤ 67. H₂ → KILL #42 path.

**H₃ (tertiary)**: Pure TSMOM-gated TQQQ (no KMLM, no TLT) **fails MDD
bar** (mean MDD > 55.17%) because 3× LETF decay during 2000-02 dot-com
overwhelms even the slower TSMOM gate. Confirms (or refutes)
`d1_qld_6m_tsmom` finding (62.28% MDD on 2× QLD with TSMOM gate).

---

## Configs (3 — keep cumulative n_trials low)

| name                                | ON sleeve                                        | OFF sleeve | gate            | thesis                                                        |
|-------------------------------------|--------------------------------------------------|------------|-----------------|----------------------------------------------------------------|
| e1_tqqq_split_kmlm30_tlt10_tsmom6m  | 30% TQQQ + 30% QLD + 30% KMLM + 10% TLT          | 100% IEF   | TSMOM 126d      | iter 006 best sleeve + 6m TSMOM gate (cross-product hybrid)   |
| e1_tqqq_split_kmlm30_tlt10_tsmom12m | 30% TQQQ + 30% QLD + 30% KMLM + 10% TLT          | 100% IEF   | TSMOM 252d      | same sleeve + 12m TSMOM (Moskowitz canonical lookback)        |
| e1_tqqq_pure_tsmom6m                | 100% TQQQ                                        | 100% IEF   | TSMOM 126d      | Pure TSMOM-gated TQQQ — H₃ test (LETF decay ↔ slower gate)   |

All 3 use:
- **signal_ticker**: `QQQSIM` (NDX total return cache, same as iter 006 + iter 013)
- **lag_days**: 1 (T+1 execution lag, no peek-ahead)
- **filter**: `momentum` (existing module from iter 013, no new infra)

**Cumulative n_trials**: prior 41 (iter 013) + 3 = **44**.

---

## Pre-committed KILL conditions

KILLs #1-#41 already declared. Numbering continues at #42.

### KILL #42 (E1 hybrid reinforces KILL #33 — gate × sleeve cross-product caps ≤ 67)

**Definition**: If best E1 config score ≤ 67 across both `e1_tqqq_split_*`
variants, the architectural ceiling claim from iter 011 is
**strengthened from 6-family to "6 families + 1 cross-product hybrid"
evidence**. The orthogonality assumption underlying single-axis
exploration is empirically validated as a NULL effect.

**Trigger**: `max_score(e1_tqqq_split_kmlm30_tlt10_tsmom6m,
e1_tqqq_split_kmlm30_tlt10_tsmom12m) ≤ 67`.

**Action if FIRED**: update BASE_MEMORY frontmatter
`architectural_ceiling: confirmed_6_families_plus_hybrid` and reinforce
iter 011 verdict. F1+SPLIT remains deploy fallback.

### KILL #43 (cross-product hybrid breaks ceiling — KILL #33 INVALIDATED)

**Definition**: If best E1 config score ≥ 70 with all 3 bars met, KILL
#33 was a single-axis-exploration limitation, NOT a true ceiling. Hunt
**REOPENS** for iter 015+ (extend cross-product sweep).

**Trigger**: `max_score_e1 ≥ 70 AND all 3 bars met for that config`.

**Action if FIRED**: revert BASE_MEMORY status to `hunting`, plan iter
015+ extending cross-product sweep (other gate × sleeve combinations:
band-gated TQQQ, EMA-gated TQQQ, etc.); document KILL #33 retraction
in FINAL_REPORT_spy_beater_failed.md (renamed to _success.md).

### KILL #44 (TSMOM lookback dose-response on TQQQ-track is monotonic)

**Definition**: Sharpe is **monotonic** (strictly positive OR strictly
negative) across lookback dose 6m → 12m on the TQQQ split sleeve on
BOTH datasets. Tests whether the dataset-regime-dependent dose-response
seen in 1× QQQ (iter 013 KILL #41 NOT FIRED) persists or flips at 3×
leverage.

**Trigger**: `Sharpe(e1_tqqq_split_kmlm30_tlt10_tsmom6m) >
Sharpe(e1_tqqq_split_kmlm30_tlt10_tsmom12m)` on both datasets OR vice
versa.

**Action if FIRED**: document direction has clear lookback preference
at 3× leverage — distinct from 1× finding (iter 013 mixed). No further
TSMOM lookback sweep needed.

### KILL #45 (pure TSMOM-gated TQQQ fails MDD bar — H₃)

**Definition**: `e1_tqqq_pure_tsmom6m` mean MDD > 55.17% bar. Confirms
that 3× LETF decay overwhelms TSMOM gate's slower reaction during
2000-02 dot-com regime, mirroring the finding from `d1_qld_6m_tsmom`
(62.28% mean MDD on 2× QLD).

**Trigger**: `mean_mdd(e1_tqqq_pure_tsmom6m) > 0.5517`.

**Action if FIRED**: confirms KILL #38 finding (regime gate alone
without crisis-alpha is insufficient on pure LETF) AT TSMOM gate, not
just SMA. Pure-LETF + slow-gate path closed.

---

## Expected outcomes (priors)

| config                                | expected mean CAGR | expected mean MDD | expected score | bar pass? |
|---------------------------------------|-------------------:|------------------:|---------------:|-----------|
| e1_tqqq_split_kmlm30_tlt10_tsmom6m    | 16-19%             | 42-50%            | 65-72          | likely 3/3|
| e1_tqqq_split_kmlm30_tlt10_tsmom12m   | 15-18%             | 45-55%            | 62-68          | maybe 3/3 |
| e1_tqqq_pure_tsmom6m                  | 18-25%             | 60-80%            | 50-58          | FAIL (MDD)|

Most likely outcome: **best E1 config scores 65-72**, KILL #42 fires
(if ≤ 67) or KILL #43 fires (if ≥ 70). KILL #45 likely fires for
pure variant. Real outcome depends on gate × sleeve orthogonality —
literature is mixed (Moskowitz cites near-additive effects; Gayed cites
sleeve-dependent effects).

Probability KILL #43 fires (hunt reopens): ~15-25% — TSMOM's MDD gain
on 1× translated linearly to 3× would yield ~+6 score pts which would
land at 73 > 70 threshold. Decay-dominated outcome (H₂) caps at 67.

---

## INCOMPLETE flags

- **TSMOM at 3× LETF leverage**: literature (Moskowitz 2012) studies
  TSMOM at 1× equity. Behaviour at 3× LETF with daily-reset decay is
  empirical extrapolation. Decay-dominated MDD may erase TSMOM's
  marginal gain over SMA.
- **PBO N=3 warning**: CSCV statistically unstable with N<4; pre-existing
  infra warning, unchanged by this iter.
- **No new synth required**: TQQQSIM, QLDSIM, KMLMSIM, TLTSIM, IEFSIM,
  QQQSIM all in cache.
- **No new module**: reuses `momentum_gate` from `lrs_engine.py` (iter
  013) and `lrs_strategy_returns`. 765 → 765 tests baseline preserved
  (no change).
- **Orthogonality assumption**: gate and sleeve are nominally
  independent axes per `[advances_fin_ml, p.31-34]`. This iter is the
  first explicit test of that assumption in spy_beater_hunt.

---

## Citations

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d SMA on
  LETFs canonical; this iter swaps to TSMOM gate.
- Moskowitz, Ooi, Pedersen (2012) "Time Series Momentum" JFE
  104(2):228-250 — TSMOM 12m canonical, factor-orthogonal claim.
- Faber 2007 GTAA — 6m TSMOM at monthly frequency, daily adaptation.
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking
  (KMLM crisis-alpha role).
- `[ilmanen_expected_returns, ch.19]` — MF crisis-alpha (KMLM, DBMF).
- `[advances_fin_ml, p.31-34]` factor framework — gate axis × sleeve
  axis orthogonality assumption explicitly tested here.
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 44; preserves
  statistical integrity for verdict.
- `[advances_fin_ml, p.208-211]` PBO grid-level — 3-config × 2-dataset
  = 6-cell grid (PBO N=3 warning persists).
- `[advances_fin_ml, p.196-202]` bootstrap CI — gate G6 99.9% CI low > 0
  required.

---

## What this iter does NOT test

- **EMA gate × TQQQ-track sleeve** — orthogonality test on different
  gate family (EMA vs TSMOM); could be future iter 015 if KILL #43 fires.
- **Band-gated TQQQ × KMLM** — hysteresis-band gate (closed iter 002
  KILL #8 on SPY-track for buffer ≥ 5%); not yet tested on TQQQ-track.
- **C2 CAPE-timing** — flagged low-credibility per
  PROMISING_DIRECTIONS.md. No CAPE data infra in project; non-trivial
  to add. Untested as last Tier 3 family.
- **TSMOM with 3m or 24m lookback** — only canonical 6m and 12m tested
  to constrain n_trials.

---

## Decision tree post-iter

| outcome                              | action                                                | KILL fired      |
|--------------------------------------|-------------------------------------------------------|-----------------:|
| All E1 configs score ≤ 67            | Reinforce KILL #33 across 6 fams + 1 hybrid. CLOSED.  | #42             |
| Any config scores 68-69              | Document marginal lift; hunt remains CLOSED at 67-cap | none            |
| Any config scores ≥ 70 + 3 bars      | INVALIDATE KILL #33. Reopen hunt for iter 015+.       | #43             |
| Sharpe monotonic 6m → 12m on split   | TSMOM dose-response on 3× direction closed            | #44             |
| Pure TQQQ fails MDD bar              | Confirms KILL #38 at TSMOM gate                       | #45             |

Most likely path: **KILL #42 fires** (split configs ≤ 67), KILL #45
fires (pure variant fails MDD). KILL #44 may or may not fire. Hunt
remains CLOSED. F1+SPLIT incumbent fallback unchanged. Mandate §1
100% Plano C unchanged.

Lower-likelihood path (~15-25%): **KILL #43 fires**, hunt reopens,
iter 015+ extends cross-product sweep.

---

## Why this iter is worth doing despite hunt being CLOSED

The iter 011 → 012 → 013 sanity-check chain tested 5 → 6 single-axis
architectural families. The 6-family ceiling claim (KILL #33) implicitly
assumes gate and sleeve axes are orthogonal — that the union of
single-axis maxima equals the cross-product maximum. **This assumption
has not been empirically tested**. Iter 014 closes that gap with the
single most-likely cross-product (best-MDD-gate × best-CAGR-sleeve).

If KILL #42 fires (most likely): negative-result policy claim
strengthened from "6 families ≤ 67" to "6 families + 1 cross-product
hybrid ≤ 67" — a stronger architectural-ceiling statement.

If KILL #43 fires (less likely but high-value): hunt reopens with a
clear motivation to extend cross-product sweep, mandate §1 review
warranted.

DSR cumulative_n_trials = **44** after this iter; worst p-value bar at
p=0.05 still has comfortable margin (iter 013 worst was 2.99e-3 << 0.05).
