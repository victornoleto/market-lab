# Iter 028 — H8 META-ENSEMBLE 3-WAY 1st-POSITION GATE-MECHANISM SUBSTITUTION

**Slug**: `H8-meta-ensemble-3way-1st-position-gate-substitution`
**Cumulative n_trials before**: 104. After (4 configs): **108**.
**Date**: 2026-04-30.

---

## Hypothesis

iter 026's H6 demonstrated that adding E1 (TSMOM-6m-QQQ gate, distinct
from SMA-class) as a 4th constituent achieves Pareto-co-apex 71 via
gate-source-distinctness (KILL #102 NEW PRINCIPLE) when 4th solo CAGR is
≥ ~15% (KILL #109 iter 027 SUB-PRINCIPLE: CAGR-runway adequacy).

iter 026 also tested E1 as **3rd-constituent substitute for F1 stack**
(H6.2: score est ~67-68 — KILL #104 NOT FIRED) and **2nd-constituent
substitute for G2 IEF** (H6.3: score est ~69 — KILL #105 BORDERLINE).
Both substitutions at 2nd/3rd positions were strictly inferior to the
iter-019 H2 ceiling (71).

**UNTESTED AXIS**: substituting E1 for **A2 at 1st position** (LRS-mono
TQQQ-track), holding the sleeve composition CONSTANT and varying only
the gate filter (SMA-200 → TSMOM-6m).

A2 spec and E1 spec share identical `on_weights` (TQQQSIM 0.30, QLDSIM
0.30, KMLMSIM 0.30, TLTSIM 0.10), `off_weights` (IEFSIM 1.0), and
`signal_ticker` (QQQSIM). **The ONLY difference is the gate**:
- A2: `filter="sma"`, `sma_window=200`
- E1: `filter="momentum"`, `lookback_days=126`

This makes iter 028 a CLEAN experimental separation of the gate-mechanism
axis at 1st position. It tests whether the +1pt gate-distinctness bonus
established at 4th position (iter 026 KILL #102) is **POSITION-INVARIANT**
or **POSITION-SENSITIVE**.

**Position symmetry hypothesis**: If meta-axis rubric is symmetric in
constituent positions (only constituent identity matters, not which slot
it occupies), then h8_meta_3way_33e1_33g2_34f1 should score within ±1pt
of iter 019 H2 (71).

**Position asymmetry hypothesis**: If A2's high-Sharpe contribution
(solo Sharpe ~1.0 vs E1's solo 0.75) is preferentially captured at
1st-position weight, substituting A2 → E1 at 1st position will cost
1-3 Sharpe-axis points. CAGR-axis may gain +1pt (E1's higher solo CAGR
17.20% vs A2's ~16%), but net should be negative.

---

## Configs (4)

### H8.1 — `h8_meta_3way_33e1_33g2_34f1`

**CORE TEST**: direct A2 → E1 substitution at iter-019 framework.
- 33% E1 (TQQQ + KMLM + TLT, TSMOM-6m gate)
- 33% G2 IEF (UPRO + TMF + IEF + UGL + KMLM, SMA-200 SPY gate)
- 34% F1 stack (NTSX + GDE + TLT + KMLM, always-on)

**Linear-mean prediction** (assuming +0.4pp CAGR lift via E1 vs A2,
+0.5pp MDD degradation, −0.05 Sharpe drag):
- CAGR ~15.5%, MDD ~33%, Sharpe ~0.95-0.97 → score 68-71

### H8.2 — `h8_meta_3way_50e1_25g2_25f1`

**HEAVY E1 dose** — CAGR-amplify dose-response test.
- 50% E1 (heavy gate-mechanism-distinct)
- 25% G2 IEF
- 25% F1 stack

Tests if E1's high solo CAGR (17.20%) at heavy weight overrides Sharpe
loss. Likely FAILS Pareto-frontier due to MDD-axis collapse from E1's
high solo MDD (47.48%) at 50% blend weight.
- CAGR ~16.5%, MDD ~37%, Sharpe ~0.85-0.90 → score 65-68

### H8.3 — `h8_meta_3way_25e1_50g2_25f1`

**HEAVY G2 dose** — light E1 to test gate-distinctness at low dose at
1st position.
- 25% E1 (light)
- 50% G2 IEF (heavy SMA gate, defensive)
- 25% F1 stack

Tests if dilute E1 at 1st position retains the gate-distinctness bonus
or whether the bonus collapses below some critical mass threshold.
- CAGR ~14.5%, MDD ~32%, Sharpe ~0.95-0.97 → score 67-70

### H8.4 — `h8_meta_4way_30e1_25g2_25f1_20a2`

**INVERTED iter 026 H6.4** — swap E1 ↔ A2 weights (E1 as 1st at 30%, A2
as 4th at 20%). Tests **position-symmetry** of iter 026's 4-way
Pareto-co-apex.

If position is invariant → score ≈ 71 (matches iter 026 H6.4).
If A2 is uniquely 1st-constituent → score < 71 by ≥ 1pt.

- 30% E1 (1st position)
- 25% G2 IEF (2nd)
- 25% F1 stack (3rd)
- 20% A2 (4th — inverted from iter 026)

Predicted: CAGR ~15.6%, MDD ~33%, Sharpe ~0.95 → score 69-71.

---

## Pre-committed KILL conditions

(Continuing from #110 last fired in iter 027.)

### KILL #111 — 1st-position gate-mechanism uniqueness

**FIRED if**: max H8 score < 71 by ≥ 1pt → A2 (SMA-200 gate) is
uniquely-Pareto-optimal at 1st position; gate-mechanism distinctness
bonus is POSITION-SENSITIVE (works at 4th position iter 026 +1pt, but
NOT at 1st position; substitution costs Sharpe-axis 1-3pts).

**NOT FIRED if**: max H8 score ≥ 71 → gate-mechanism substitutability
holds at 1st position; A2 not uniquely Pareto-optimal; position is
invariant.

### KILL #112 — Strict ceiling falsification

**FIRED if**: max H8 score ≥ 72 → STRICT FALSIFICATION of meta-axis
ceiling 71 DEFINITIVE; hunt REOPENS; closest-to-winner UPDATES.

**NOT FIRED if**: max H8 ≤ 71 → 12th meta-axis confirmation point;
ceiling 71 DEFINITIVE preserved.

### KILL #113 — E1 dose-response at 1st position

**FIRED if**: h8_meta_3way_50e1_25g2_25f1 score > h8_meta_3way_33e1_33g2_34f1
by ≥ 2pts → CAGR-axis lift via E1-heavy weighting overrides Sharpe-axis
cost at 1st-position; heavy E1 is Pareto-positive.

**NOT FIRED if**: dose-response is flat or negative → E1 is rubric-
saturated at 1st-position weight ≤ 33%; heavy E1 dose adds MDD/Sharpe
cost without CAGR-axis recovery.

### KILL #114 — Position-symmetry test for iter-026 H6.4

**FIRED if**: h8_meta_4way_30e1_25g2_25f1_20a2 score ≥ iter 026 H6.4 (71)
by ≥ 1pt → POSITION DOES NOT MATTER; constituent identity is invariant
under position swap (A2 ↔ E1); meta-axis rubric is symmetric in
constituent permutations.

**NOT FIRED if**: score < 71 by ≥ 1pt → POSITION MATTERS; A2 must be 1st
constituent for ceiling 71; iter-019 H2 ordering is empirically Pareto-
optimal AND not arbitrary.

### KILL #115 — F1 stack 3rd-position 4th-confirmation

**FIRED if**: H8 configs with F1 at 3rd position score ≥ those without
→ FOURTH CONFIRMATION of iter 027 KILL #110 (F1 stack uniquely-Pareto-
optimal as 3rd constituent across 4 alternatives now: G3 iter 025, E1
iter 026, C1 iter 027, **+ E1-substituted-A2 iter 028**).

**NOT FIRED if**: F1 stack absence or relegation does not strictly
under-perform → F1's 3rd-constituent advantage is conditional on iter-019
sleeve composition (A2 + G2), not universal.

---

## Expected outcomes ranking

Expected score ordering (highest first):

1. **H8.4** (4-way inverted iter 026): **70-71** (close to iter 026)
2. **H8.1** (3-way E1 at 1st): **68-71** (varies with KILL #111)
3. **H8.3** (heavy G2 + light E1): **67-70**
4. **H8.2** (heavy E1): **65-68** (Sharpe-MDD-cost)

If max H8 ≥ 72 → unexpected; trigger KILL #112 hunt-reopen.
If max H8 ≤ 67 → 1st-position gate-mechanism substitution cost is
LARGE (≥ 4pts); A2 confirmed uniquely Pareto-optimal as LRS-mono
1st-constituent within meta-axis.

Most likely outcome: **H8.4 ≈ 70-71** (position-symmetric or −1pt
asymmetric); **H8.1 ≈ 68-70** (1st-position E1 substitution costs
1-3pts on Sharpe). Net score 70 PROMISING tier (or 71 PARETO-CO-APEX).

---

## INCOMPLETE flags

- **A2 vs E1 sleeve identity**: A2 and E1 share IDENTICAL on_weights,
  off_weights, signal_ticker. ONLY gate filter differs. This is the
  cleanest possible "gate-mechanism" axis test, but it conflates two
  effects: (1) gate signal latency (SMA-200 ≈ 200d lag vs TSMOM-6m
  ≈ 126d lag — TSMOM responds faster); (2) gate signal smoothness (SMA
  is smooth, TSMOM is binary on momentum sign). Iter 028 cannot
  decompose these two effects.
- **n_trials inflation**: cumulative 104 → 108. Bonferroni boundary
  0.05 / 108 = 4.63e-04. If worst per-config DSR p ≤ 4.63e-04, all
  configs pass strict Bonferroni. iter 027's worst was 1.61e-04 → 8.4×
  margin, likely still passes Bonferroni at iter 028.
- **No new infra**: reuses A2_CLOSEST_SPEC, G2_IEF_SPEC, F1_STACK_SPEC,
  E1_TSMOM6M_SPEC from iter 026 verbatim. 'blend' + 'lrs' (sma + momentum
  filters) + 'static' spec types. 771 tests baseline preserved.
- **Tax classification**: meta-blend with E1 (lrs → annual_realize).
  Drag expected 1.91-2.05pp (between iter 019 1.91pp and iter 026
  2.03pp). Net score expected 64-65.
- **Caveat — iter 026 H6.2 (substitute F1 with E1) and H6.3 (substitute
  G2 with E1) both scored < 71**: this evidence is correlated with iter
  028 H8.1 prediction. If iter 026 inverse-position results predict
  iter 028, expected H8.1 score is ~67-69. But 1st-position has unique
  weight (33%) and may exhibit different behavior than 33% at 3rd
  position due to constituent ordering effects in scoring rubric.

---

## Citations

- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction over
  multiple alpha streams (3-way meta-ensemble at strategy-level with
  1st-position gate-mechanism substitution falsification test)
- Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250
  (E1 TSMOM-6m gate at 1st-constituent position)
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed 200d SMA gate
  (A2 baseline at 1st position iter 019)
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking
  generalized to 1st-position gate-mechanism substitution
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha (KMLM in
  A2/E1/G2 ON-state)
- Bridgewater All-Weather (Dalio 1996) F1 stack (3rd position retained
  across H8 configs — KILL #115 4th-confirmation test)
- `[advances_fin_ml, p.222-223]` DSR with cumulative_n_trials = 108
  (Bonferroni 4.63e-04)
- `[advances_fin_ml, p.208-211]` PBO via CSCV (N=4 grid stable per
  iter 026 pattern)
