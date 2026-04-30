# Iter 019 — H2 META-ENSEMBLE — 3-way blends + 2-way weight sweep around iter-018 winner

**Date**: 2026-04-30
**Cumulative n_trials before**: 56 (after iter 018)
**Cumulative n_trials after**: 56 + 6 = **62**
**Hunt status entering iter 019**: REOPENED at meta-ensemble axis (KILL #59 fired iter 018, score 70 PROMISING > 67-cap)

---

## Why iter 019

Iter 018 produced the FIRST score >67 in the entire spy_beater hunt
(score 70 PROMISING for `h1_meta_50a2_50g2ief`, a 50/50 same-gate-family
blend of iter 006 A2 closest-to-winner + iter 017 G2 IEF Pareto-MDD
CAGR-passer). KILL #59 fired and KILL #33 was INVALIDATED at the meta-
portfolio axis, but the result is borderline (+3pts above prior 67-cap)
and rests on N=3 PBO grid (statistically unstable per long-standing
validator warning).

Per iter 018 lesson "Suggested iter 019" section:

> Recommended iter 019:
> - 6 configs (improves PBO N=3 → N=6 statistical stability).
> - 3-way blends: A2 + G2 IEF + F1 stack at varying weights.
> - Weight sweep: 50/50, 60/30, 50/30/20, 40/30/30, 33/33/34, 70/30.
> - Cumulative n_trials: 56 + 6 = 62.
> - Pre-commit KILL: if best iter-019 score still < iter-018 70, the
>   meta-ensemble axis ceiling is at 70 (consolidates KILL #59 with
>   single data point); if best ≥ 75, tier STRONG reachable.

This iter executes that exact plan.

---

## Hypotheses

**H2.1 (reproducibility)**: iter 018 winner `h1_meta_50a2_50g2ief` (score
70) reproduces deterministically; PBO computed on N=6 grid is more
stable than N=3 of iter 018. If reproducibility check fails (deterministic
score differs > 1pt) something is broken.

**H2.2 (weight-axis sensitivity around 50/50)**: small weight perturbations
(45/55, 55/45) reveal whether 50/50 is at a flat plateau or a sharp peak.
Sharpe / score response across (45,50,55) tells us about Pareto-frontier
curvature.

**H2.3 (3-way blend Pareto-improvement)**: adding F1 stack (always-on
multi-asset diversifier, best Sharpe 1.018, best MDD 26.82% among CAGR-
passers) as a 3rd constituent at 20-34% weight could lift Sharpe and
relieve MDD beyond 2-way (h1_meta_50a2_50g2ief at 0.933 / 34.83%). KILL
#60 (iter 018) found that mixed-gate blends (A2 + F1 stack) at 60/40
underperformed same-gate blends; H2.3 tests if a 3-way blend (gated +
gated + always-on) inverts that finding via balanced 3-way decorrelation.

**H2.4 (path to STRONG tier ≥75)**: meta-ensemble axis can lift score
+5pts above iter-018 70 to reach STRONG tier if 3-way blends or weight-
optimized 2-way blends find a Pareto-improvement region. If the best
iter-019 score caps ≤ 70, the meta-ensemble axis is empirically capped
at 70 and tier STRONG (75+) is unreachable.

---

## Configs (6)

All blends use existing iter-006 / iter-015 / iter-017 constituent specs.
No new asset / gate / decay primitives.

| # | config | A2 wt | G2 IEF wt | F1 stack wt | gate behavior |
|---|:-------|------:|----------:|------------:|:-------------|
| 1 | h2_meta_50a2_50g2ief        | 0.50 | 0.50 | 0.00 | both LRS-gated (QQQ/SPY) |
| 2 | h2_meta_55a2_45g2ief        | 0.55 | 0.45 | 0.00 | both LRS-gated, slight A2-tilt |
| 3 | h2_meta_45a2_55g2ief        | 0.45 | 0.55 | 0.00 | both LRS-gated, slight G2-tilt |
| 4 | h2_meta_3way_40a2_30g2_30f1 | 0.40 | 0.30 | 0.30 | gated + gated + always-on (balanced) |
| 5 | h2_meta_3way_50a2_25g2_25f1 | 0.50 | 0.25 | 0.25 | gated + gated + always-on (A2-heavy) |
| 6 | h2_meta_3way_33a2_33g2_34f1 | 0.33 | 0.33 | 0.34 | gated + gated + always-on (equal) |

**Constituent A2** (iter 006 a6_tqqq_split_kmlm30_tlt10):
```json
{
  "type": "lrs", "filter": "sma", "sma_window": 200, "buffer_pct": 0.0,
  "on_weights": {"TQQQSIM": 0.30, "QLDSIM": 0.30, "KMLMSIM": 0.30, "TLTSIM": 0.10},
  "off_weights": {"IEFSIM": 1.0},
  "signal_ticker": "QQQSIM", "lag_days": 1
}
```

**Constituent G2 IEF** (iter 017 g2_f1_letf_2x_sma200_ief):
```json
{
  "type": "lrs", "filter": "sma", "sma_window": 200,
  "on_weights": {"UPROSIM": 0.30, "TMFSIM": 0.25, "IEFSIM": 0.15, "UGLSIM": 0.15, "KMLMSIM": 0.15},
  "off_weights": {"IEFSIM": 1.0},
  "signal_ticker": "SPYSIM", "lag_days": 1
}
```

**Constituent F1 stack** (iter 015 f1_aw_stack_15x):
```json
{
  "type": "static",
  "weights": {"NTSXSIM": 0.35, "GDESIM": 0.30, "TLTSIM": 0.20, "KMLMSIM": 0.15}
}
```

---

## Pre-committed KILL conditions

KILLs #1-#61 prior. New KILLs #62-#65:

### KILL #62 — META-ENSEMBLE ceiling consolidates at 70 (iter-018 score is the cap)

**Trigger**: `max(iter-019 score) ≤ 70`

**Fires if**: NO iter-019 config improves on iter-018 winner score 70.

**Implication if FIRED**: meta-ensemble axis ceiling consolidated at 70
across N=6 configs. KILL #59 reaffirmed but practically the hunt is
capped at 70 PROMISING. Tier STRONG (75+) unreachable at meta-axis.
F1+SPLIT incumbent fallback retains deploy-ready status.

### KILL #63 — META-ENSEMBLE reaches STRONG tier (≥ 75)

**Trigger**: `max(iter-019 score) ≥ 75 AND winner_conditions_met=True`

**Fires if**: any config scores ≥ 75 with all 3 strict bars met.

**Implication if FIRED**: meta-ensemble axis can reach STRONG tier;
hunt exploration deepens with iter 020+ targeting tier WINNER (≥90).
Mandate §7 review case strengthens substantially.

### KILL #64 — Reproducibility check on iter-018 winner (PBO N=6 stability)

**Trigger**: `|iter-019 score(h2_meta_50a2_50g2ief) − 70| > 1`

**Fires if**: deterministic re-run of iter-018 winner under N=6 PBO
grid differs from iter-018's N=3 score by more than 1 point.

**Implication if FIRED**: iter-018 score 70 was N=3 PBO instability
artifact. KILL #59 weakens; meta-ensemble axis re-opening rests on
shaky statistical ground. Hunt may need to revert to CLOSED status.

**Implication if NOT FIRED**: iter-018 result confirmed under N=6 PBO;
KILL #59 strengthens; meta-ensemble axis re-opening is empirically
sound.

Note: gross score is fully deterministic — same input → same output.
But the PBO computation uses the iter's CONFIG GRID; a 6-config grid
yields a different (more stable) PBO grid-level than 3-config. Score
may shift ±1pt due to G1 PBO gate change alone.

### KILL #65 — 3-way blend Pareto-dominates 2-way (F1 stack always-on adds value at 3-way)

**Trigger**: `max(3-way config score) > max(2-way config score)` AND
`max(3-way config Sharpe) > max(2-way config Sharpe)`

**Fires if**: best 3-way blend beats best 2-way blend on BOTH score
AND mean Sharpe.

**Implication if FIRED**: KILL #60 (iter 018: same-gate-family blend
Pareto-dominates mixed-gate) INVALIDATED at 3-way axis. Always-on F1
stack adds value when balanced with 2 gated strategies (not when paired
1:1 with single gated strategy). Architecture lesson: balanced 3-way
decorrelation > tilted 2-way decorrelation in spy_beater rubric.

**Implication if NOT FIRED**: KILL #60 reaffirmed at 3-way axis. Same-
gate-family 2-way blends are the Pareto-optimal meta-ensemble structure
for spy_beater. Always-on diversifier underperforms at all blend counts.

---

## Expected outcomes (analytical, NOT pre-committed KILLs)

**Reproducibility (config 1)**: same as iter 018 winner — score 70 ± 1
under N=6 PBO. Deterministic.

**2-way weight sweep (configs 2,3)**: iter 018 found 50/50 at score 70,
70/30 at ~67-69. Config 2 (55/45) and config 3 (45/55) test the
plateau. Linear-mean estimates:
- 55/45: CAGR 0.55×17.33 + 0.45×14.02 = 15.84%, MDD ~42.4%, Sharpe ~0.88
- 45/55: CAGR 0.45×17.33 + 0.55×14.02 = 15.51%, MDD ~41.0%, Sharpe ~0.91

Likely score 67-69 each. If neither breaks 70, the 50/50 is at a flat
local maximum.

**3-way blends (configs 4,5,6)**: F1 stack contributes CAGR ~11.95% and
MDD ~26.82%. Linear-mean estimates ignoring decorrelation:
- 40/30/30: CAGR 0.40×17.33 + 0.30×14.02 + 0.30×11.95 = 14.72%, MDD ~36.6%, Sharpe ~0.95
- 50/25/25: CAGR 0.50×17.33 + 0.25×14.02 + 0.25×11.95 = 15.16%, MDD ~38.9%, Sharpe ~0.92
- 33/33/34: CAGR 0.33×17.33 + 0.33×14.02 + 0.34×11.95 = 14.43%, MDD ~36.0%, Sharpe ~0.96

If F1 stack's MDD relief and Sharpe lift propagate at decorrelation
levels similar to iter-018, 3-way blends could score 65-72. Path to
75+ requires either (a) >5pts MDD relief beyond linear estimate, or
(b) Sharpe >1.0 lift, or (c) both.

---

## Anti-overfit posture

- **Pre-commit hypothesis BEFORE running** — 4 KILLs documented above.
- **Cumulative n_trials = 62** for DSR penalty. iter 018's worst p =
  1.65e-04 << 0.05 — strong margin should survive 6-trial penalty rise
  per `[advances_fin_ml, p.222-223]`.
- **Constituents are existing iter-006 / iter-015 / iter-017 specs** —
  no new free parameters; iter 019 only adds blend weights.
- **PBO N=6 vs iter-018 N=3** — addresses the long-standing PBO
  validator warning; reproducibility check (config 1) bridges old/new
  PBO grids.
- **Same anchor ranges + 2-dataset framework + 7-gate battery** as iter
  018 — no methodology drift.
- **Honest reporting**: if KILL #62 fires (most likely outcome), the
  meta-ensemble axis ceiling consolidates at 70. If KILL #63 fires
  (less likely but possible per linear-estimate analysis on 3-way),
  hunt exploration deepens.

---

## INCOMPLETE flags (pre-acknowledged)

- **Linear-mean MDD estimates ignore decorrelation** — actual blended
  MDD path-dependent and typically LOWER than linear (iter 018 saw
  6.87pp super-linear MDD relief from gate decorrelation).
- **3-way blends introduce more correlation matrix complexity** —
  decorrelation gain may be sub-linear vs 2-way (e.g., 2 gated + 1
  always-on may not decorrelate as much as 2 gated of different signal).
- **Cumulative n_trials = 62** lifts DSR penalty mildly but worst p
  was 1.65e-04 in iter 018; should survive comfortably.
- **No NEW infra** — reuses "blend" spec type from iter 018. 768 tests
  baseline preserved.
- **Sleeve effective leverage**:
  - 2-way (50/50): A2 (3.0× ON / 1× OFF) × 0.5 + G2 IEF (2.25× ON / 1× OFF) × 0.5 = ~2.6× when both ON.
  - 3-way (40/30/30): same as above × 0.7 + F1 stack 1.41× × 0.3 = ~2.25× when both gates ON.
  - 3-way effectively LOWER leverage than 2-way; expect lower CAGR + lower MDD.
- **F1 stack ALWAYS-ON**: never goes defensive. During 2008/2022 stress,
  F1 stack absorbs full equity drawdown component (offset by TLT/KMLM).
  Iter 015 showed F1 stack standalone MDD 26.82% — much better than A2
  alone but lacks regime-gated bear-avoidance.
- **Plot generation reuses existing run_iter plotting helper**.
- **Re-score iter-006 A2 net-of-tax for apples-to-apples comparison**:
  this was suggested in iter 018 lesson but is OUT OF SCOPE for iter 019
  — net-of-tax was backfilled across iters 001-018 in 2026-04-30
  commits f5f7c68 + cab6c57. Net rankings already in WINNER_AND_RANKING.md.

---

## Why this iter (justification within mandate)

Per CLAUDE.md mandate §1 MAINTENANCE MODE: this hunt operates as
RESEARCH-ONLY with F1+SPLIT (Plano C) deploy-ready. No iter outcome
short of tier WINNER (≥90) alters the mandate. Iter 019 is justified
because:

1. iter 018 KILL #59 fired and the result needs N=6 confirmation
   (iter-018 had N=3 PBO instability warning).
2. iter 018 lesson explicitly recommends iter 019 6-config sweep.
3. 3-way meta-ensemble axis is the only remaining unmapped portion
   of the meta-ensemble axis (2-way mapped at iter 018).
4. Pre-committed KILLs guarantee falsifiable verdict.

---

## Citations

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d SMA gate
  rationale (both A2 QQQ-track and G2 SPY-track use this gate type).
- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction — multiple
  alpha streams blended at meta-level; 3-way extension.
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking
  generalized to strategy-level diversification (F1 stack constituent).
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha (KMLM) — present
  in A2 (30% ON), G2 (15% ON), F1 stack (15%).
- Bridgewater All-Weather (Dalio 1996) — F1 stack ON-state composition.
- HFEA Bogleheads 2019 — barbell logic generalized.
- `[advances_fin_ml, p.31-34]` factor framework — meta-ensemble axis.
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 62 (56 + 6).
- `[advances_fin_ml, p.208-211]` PBO grid-level — N=6 stability vs N=3.
- `[advances_fin_ml, p.196-202]` bootstrap CI G6 expected to pass.
