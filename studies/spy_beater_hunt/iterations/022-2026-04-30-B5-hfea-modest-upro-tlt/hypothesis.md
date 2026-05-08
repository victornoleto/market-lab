# spy_beater_hunt iter 022 — Hypothesis — `B5-hfea-modest-upro-tlt`

**Slug**: `B5-hfea-modest-upro-tlt`
**Created**: 2026-04-30
**Cumulative n_trials**: prior 74 (iter 021) + 6 this iter = **80**
**Continuation rationale**: per iter 021 final_report, the **meta-axis
ceiling is DEFINITIVELY ESTABLISHED at gross 71** across 4 sequential
iters (018→019→020→021 = 70→71→67→70). All meta-ensembles use
`spec.type = "blend"` with LRS constituents → annual_realize tax
classification → drag 1.91-2.07pp → net rank-1 = 64.

The **WINNER_AND_RANKING.md final ranking** explicitly flags a
**structural net-rubric advantage of ~1.5pp for buy-hold static**
strategies (drag 0.59-0.74pp vs 1.63-2.35pp for LRS/blend). It also
recommends "future hunt iters should consider buy-hold portfolios
with concentrated growth (closer to SPY CAGR without LRS gate cost)".

Iter 022 pivots OFF the meta-axis (exhausted) and OFF the LRS-gate axis
(tested 12 fams + 3 hybrids + 3-axis meta) to a **fundamentally NEW
static-barbell architecture not yet tested**: **3× UPRO + 1× TLT**
(no leveraged duration leg). KILL #24 from iter 008 closed the **3× UPRO
+ 3× TMF** family for failing MDD bar (mean MDD 67-72%). KILL #27 from
iter 009 closed **HFEA + KMLM** for failing MDD bar even with crisis-alpha.
But the **1× TLT replacement of 3× TMF has NEVER been tested** in
this hunt — it's architecturally distinct because:

1. Eliminates TMF daily-reset decay (~1.5%/y headwind on duration leg).
2. Reduces 2022 stagflation MDD: TMF lost ~70%, TLT lost ~31% — a
   2.3× reduction in 2022 MDD contribution per dollar of duration.
3. Halves duration leverage from 165% (3× × 55%) to 50-60% (1× ×
   50-60%) → reduces compounding of bond drawdowns.

If this saves the MDD bar (≤ 55.17% mean), CAGR could land 14-18%
mean (UPRO 50-60% × ~25%/y + TLT 40-50% × ~3-5%/y), passing CAGR
bar comfortably.

**Critically**: a static-barbell config at gross score ≥ 65 with
drag ~0.66pp lands net score ≥ 64 — **TIES or BEATS iter-018's
meta-ensemble net rank-1**. This is the most defensible NEW direction
within the spy_beater architectural taxonomy that maintains rubric-
respecting trade-offs while exploiting the static tax-efficiency.

---

## Hypothesis

**H₁ (HFEA-modest clears MDD bar)**: replacing 3× TMF with 1× TLT
in the leveraged barbell (50% UPRO + 50% TLT) reduces mean MDD from
67-72% (iter 008 HFEA classical) to ≤ 55.17% (the spy_beater bar)
because:
- 2022 binding regime: 50% × −50% UPRO + 50% × −31% TLT = −40.5%
  (vs HFEA classical 50/50 UPRO/TMF: 50% × −50% + 50% × −70% = −60%)
- 2008 GFC: 50% × −85% UPRO + 50% × +25% TLT = −30%
- 2000-02 dot-com: 50% × −95% UPRO + 50% × +25% TLT = −35%

Mean MDD likely 35-50%, comfortably PASSING bar. CAGR likely 14-17%
also PASSING bar. Sharpe likely 0.85-1.0 (better than HFEA classical
0.74 because TLT decay-free).

**H₂ (UPRO-weight monotonic dose-response)**: UPRO 40% → 50% → 60%
should monotonically lift CAGR AND lift MDD. This is the canonical
HFEA dose-response BUT at modest-leverage (1× duration). The 5pp
spacing maps the 50/50 anchor's neighborhood within the rubric.

**H₃ (KMLM addition lifts Sharpe in modest-HFEA, opposite of
KILL #27 on classical HFEA)**: at HFEA classical (50/50 UPRO/TMF,
165% UPRO notional, 135% TMF notional) KMLM 15-25% addition was
FLAT-to-NEGATIVE on Sharpe (KILL #27 fired iter 009). At HFEA-modest
(50% UPRO, 50% TLT — 150% UPRO notional, 50% TLT notional) the
duration leg is much smaller, so KMLM addition should genuinely
DIVERSIFY rather than dilute. We test KMLM 20% addition at two
weights (b5_4040_kmlm20, b5_5030_kmlm20) to see if KILL #27 transfers.

**H₄ (DBMF-vs-KMLM transfer)**: DBMF (broader CTA basket) vs KMLM
(KFA Mount Lucas Managed Futures Index) at same 20% weight should
produce similar Sharpe (both MF crisis-alpha) but slightly different
MDD profile (DBMF basket more diversified). Tests whether KILL #27's
KMLM-specific finding transfers across MF substitutes.

**H₅ (net-rubric rank-1 challenge)**: best B5 config gross score ≥ 65
with drag 0.66pp → net score ≥ 64, TYING iter-018 net rank-1. If
B5 best ≥ 70 gross, net ≥ 69 → BEATS meta-ensemble net rank-1 by ≥ 5pts.

Citations:
- HFEA Bogleheads 2019 (canonical 55/45 anchor, modest-leverage
  variant explored in subsequent threads but not academically dominant)
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — LETF decay
  on duration leg compounds; modest-leverage variant predicted to
  reduce decay materially
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking
  baseline (NTSX is 90% SPY + 60% UST = 150% notional; B5 50/50
  UPRO/TLT is 150% SPY notional + 50% UST = 200% notional)
- `[ilmanen_expected_returns, ch.19]` — MF crisis-alpha role on
  modest-leverage barbell (KMLM/DBMF tests at 20%)
- `[advances_fin_ml, p.31-34]` factor framework — leveraged equity
  (UPRO) + non-leveraged duration (TLT) + MF (KMLM/DBMF) is a
  3-factor stack with clean factor decomposition
- `[advances_fin_ml, p.222-223]` DSR with cumulative_n_trials = 80
- `[advances_fin_ml, p.208-211]` PBO via CSCV
- WINNER_AND_RANKING.md "Future hunt iters should consider buy-hold
  portfolios with concentrated growth (closer to SPY CAGR without
  LRS gate cost)" + "structural net-rubric advantage of ~1.5pp"

---

## Configs (6, naming `b5_*`)

### 1. `b5_5050_upro_tlt` — canonical modest-HFEA (50/50)

```json
{
  "type": "static",
  "weights": {
    "UPROSIM": 0.50,
    "TLTSIM": 0.50
  }
}
```

Tests: H₁, H₂. Anchor config: 50% × 3× SPY + 50% × 1× LTT = 150% SPY
notional + 50% UST notional. Direct analogue to iter 008 b1_balanced_5050
(50% UPRO + 50% TMF) — replaces 3× TMF with 1× TLT, eliminates LETF
duration decay.

### 2. `b5_4060_upro_tlt` — defensive modest-HFEA (40/60)

```json
{
  "type": "static",
  "weights": {
    "UPROSIM": 0.40,
    "TLTSIM": 0.60
  }
}
```

Tests: H₂ defensive end. Lower UPRO → lower CAGR but lower MDD; tests
whether reducing equity arm 50→40% saves another 5-10pp MDD without
breaking CAGR bar (predicted CAGR 12-14%).

### 3. `b5_6040_upro_tlt` — offensive modest-HFEA (60/40)

```json
{
  "type": "static",
  "weights": {
    "UPROSIM": 0.60,
    "TLTSIM": 0.40
  }
}
```

Tests: H₂ offensive end. Higher UPRO → higher CAGR, higher MDD;
tests whether 60% UPRO blows past MDD bar (predicted MDD 50-60%).

### 4. `b5_4040_kmlm20` — modest-HFEA + KMLM crisis-alpha 20%

```json
{
  "type": "static",
  "weights": {
    "UPROSIM": 0.40,
    "TLTSIM": 0.40,
    "KMLMSIM": 0.20
  }
}
```

Tests: H₃. Replaces 10pp UPRO + 10pp TLT with 20% KMLM. Predicted
to LIFT Sharpe vs b5_5050 (more diversification) and LOWER MDD via
crisis-alpha. Counter-test to KILL #27 (which closed KMLM on
HFEA classical 165% UPRO notional).

### 5. `b5_5030_kmlm20` — modest-HFEA + KMLM 20% (more equity)

```json
{
  "type": "static",
  "weights": {
    "UPROSIM": 0.50,
    "TLTSIM": 0.30,
    "KMLMSIM": 0.20
  }
}
```

Tests: H₃ at higher UPRO. Maps the KMLM-on-modest-HFEA dose-response
at 50% UPRO weight. Higher CAGR potential than b5_4040_kmlm20.

### 6. `b5_4040_dbmf20` — modest-HFEA + DBMF 20% (alternative MF)

```json
{
  "type": "static",
  "weights": {
    "UPROSIM": 0.40,
    "TLTSIM": 0.40,
    "DBMFSIM": 0.20
  }
}
```

Tests: H₄. Same structure as b5_4040_kmlm20 but DBMF instead of KMLM.
DBMF is iMGP DBi Managed Futures Strategy ETF (proxy of SocGen CTA
Index, broader CTA basket). Should produce similar profile with
slightly different MDD characteristics.

---

## Pre-committed KILL conditions

KILL numbering continues from #76 (last used in iter 021). New: #77, #78, #79, #80, #81, #82.

### KILL #6 (standing — CAGR floor)

If best config across the iter has CAGR mean < 11.21%, the strategy
class is structurally subordinate. Direction CLOSED.

### KILL #77 — B5 ceiling matches meta-axis

If max B5 selected score ≤ 71, the static-barbell axis matches the
meta-axis ceiling within the spy_beater rubric — confirms the 71
ceiling is **architecturally invariant across spec-type** (LRS-blend,
LRS-mono, static-barbell). Direction B5 CLOSED, hunt's 71 ceiling
strengthens to "spec-type-invariant".

**Rationale**: meta-axis 4-iter trajectory established 71 ceiling
within blend(LRS) constituents. If B5 static-barbell also caps at 71,
the rubric structurally limits scoring at 71 regardless of spec-type
— mandate §7 rubric-revision case strengthens further.

### KILL #78 — Pure 50/50 UPRO/TLT MDD bar reachable

If `b5_5050_upro_tlt` mean MDD ≤ 55.17%, the MDD bar is reachable
via 1× duration replacement (vs HFEA classical's 67-72% mean MDD).
Confirms TMF→TLT replacement is the architectural pivot the static
family needed.

**Rationale**: KILL #24 closed UPRO+TMF on MDD bar. KILL #78 tests
whether the issue was TMF leverage specifically (vs UPRO leverage
or barbell structure). If FIRES, the result is positive empirical
finding: the binding 2022-MDD constraint was TMF's 70% loss, not
UPRO's 50% loss.

### KILL #79 — KMLM-on-modest-HFEA Sharpe lift (counter to KILL #27)

If `b5_4040_kmlm20` Sharpe > `b5_4060_upro_tlt` Sharpe AND
`b5_5030_kmlm20` Sharpe > `b5_5050_upro_tlt` Sharpe on ≥ 1 dataset,
KMLM addition LIFTS Sharpe at modest-leverage barbell — directly
opposite of KILL #27's finding on HFEA classical.

**Rationale**: at 165% UPRO + 135% TMF notional (HFEA classical),
the barbell already has high notional leverage; KMLM dilutes notional
without enough decorrelation lift. At 150-180% UPRO + 30-40% TLT
notional (B5), there's room for KMLM to genuinely diversify.

### KILL #80 — Net-rubric rank-1 displacement

If best B5 net_score ≥ 65, the static-barbell axis displaces
iter-018's meta-ensemble at net rank-1 (current net 64).
Confirms WINNER_AND_RANKING.md's structural prediction that
buy-hold static has 1.5pp net advantage.

**Rationale**: gross-vs-net trade matters for deploy-readiness.
A gross 67 static config (drag 0.66pp → net 66) outranks a gross
70 blend config (drag 1.91pp → net 64) under net rubric. This
directly supports mandate §7 review: best-deployable strategy may
not be best-gross-scored strategy.

### KILL #81 — Offensive 60/40 fails MDD bar

If `b5_6040_upro_tlt` mean MDD > 55.17%, the offensive end of the
B5 family fails MDD bar — leverage cap is stricter at 50% UPRO,
not 60%. Useful for mapping the dose-response inflection.

### KILL #82 — STRONG tier reachable via static path

If best B5 gross score ≥ 75 + bars 3/3, the STRONG tier is reachable
via the static-barbell axis. Hunt status changes from "PROMISING ceiling
71" to "STRONG ceiling 75+". WINNER tier (≥ 90) still requires further
work but viable architectural path identified.

**Rationale**: HFEA Bogleheads 2019 + Gayed monotonic-decay literature
predict modest-leverage barbells should outperform classical HFEA on
MDD-adjusted return. If empirically confirmed at score ≥ 75, the
rubric-revision pressure becomes stronger (this is a deployable
candidate, not just rubric-suboptimal noise).

---

## Expected outcomes

| config              | expected CAGR mean | expected MDD mean | expected Sharpe |
|---------------------|-------------------:|------------------:|----------------:|
| b5_5050_upro_tlt    | 14-17%             | 35-50%            | 0.85-1.05       |
| b5_4060_upro_tlt    | 11-14%             | 28-42%            | 0.85-1.05       |
| b5_6040_upro_tlt    | 16-19%             | 45-60%            | 0.80-1.00       |
| b5_4040_kmlm20      | 12-15%             | 30-42%            | 0.95-1.15       |
| b5_5030_kmlm20      | 14-17%             | 32-45%            | 0.95-1.10       |
| b5_4040_dbmf20      | 12-15%             | 30-42%            | 0.95-1.10       |

**Score outlook** (selected ≈ b5_4040_kmlm20 or b5_5050_upro_tlt
depending on max-Sharpe-rule):

- 1. CAGR 30 × clamp((0.14 − 0.05)/0.15, 0, 1) ≈ 18 pts
- 2. MDD 20 × clamp((0.50 − 0.40)/0.40, 0, 1) ≈ 5 pts (if MDD ~40%)
  OR up to 8 pts (if MDD ~30%)
- 3. Gates likely 10-13 pts (G3 walk-forward MDD<25% threshold —
  modest-HFEA at ~40% MDD likely fails by 10-15pp; G7 cross-lib
  ±3pp likely passes since static-barbell is well-defined)
- 4. DSR n=80 worst p estimated < 0.001 → 10 pts
- 5. Sharpe ≈ 0.95-1.05 → 3-4 pts
- 6. Robustness ≈ 6-9 pts (modest-HFEA more stable across regimes
  than HFEA classical because no TMF 2022-disaster)
- 7. Extra 0
- **Total expected**: ~52-65 gross / ~51-64 net (drag ~0.66pp = ~1pt)

**Score-90 path**: improbable in this iter alone. Best-case ~65-70
gross (rivals iter-008/009 HFEA family at 63 + adds Sharpe lift
from MDD relief). Net rank could displace meta-axis at 64.

This iter's value is **structural diagnostic + tax-rubric pivot**:
it maps the modest-leverage barbell geometry against the rubric,
tests whether the static path can reach gross ≥ 65 (and net ≥ 64),
and either confirms or falsifies the WINNER_AND_RANKING.md prediction
that buy-hold has structural net advantage.

---

## INCOMPLETE flags

1. **TLTSIM cache pre-1986 backfill**: TLTSIM cache covers 1962+ via
   testfolio's LTT yield curve reconstruction. Within `lh_56y` (1986+)
   the historical backfill is well-validated; outside of scope for
   spy_beater_hunt.

2. **UPROSIM cache pre-2009 synth**: real UPRO inception 2009-06;
   pre-2009 data is testfolio's SPY × 3 daily-reset decay synth. The
   2008 GFC stress test on lh_56y is fully synthetic — no real 3×
   LETF traded actual GFC.

3. **No transaction costs / no quarterly rebalance**: HFEA Bogleheads
   classical assumes quarterly rebalance; we use daily rebalance.
   Real-world rebalance friction ~0.1-0.3%/y; impact on net ranking
   negligible.

4. **PBO N=6**: maintained per iter-019 KILL #64 resolution. CSCV
   stable at N=6.

5. **DBMFSIM is direct cache** (not synth): testfolio cache contains
   DBMFSIM. KMLMSIM also direct. No synth construction needed.

6. **Tax model classification**: all 6 configs are `spec.type = "static"`,
   classified as buy_hold (terminal DARF settlement) per `tax_layer.py`.
   Drag estimate 0.59-0.74pp per `WINNER_AND_RANKING.md` "Final ranking".

7. **Cross-lib gate G7**: static-barbell is mathematically well-defined
   (no LRS gate logic, no vol-target rebalance feedback loop), so
   cross-lib drift ≤ 3pp predicted with high confidence (the engine
   numerical precision is the only contributor).

---

## Next-iter sketch (depending on outcome)

- **If b5_5050 or b5_4040_kmlm20 score ≥ 70 gross AND ≥ 65 net**:
  iter 023 sensitivity sweep around the winning config (45/55, 35/45/20
  KMLM, etc) + test 2× SSO replacement of 3× UPRO for further leverage
  reduction.
- **If KILL #77 fires (B5 ≤ 71)**: meta-axis ceiling confirmed
  spec-type-invariant; iter 023 either (a) tests one more axis
  (e.g., 2× SSO + 1× TLT + KMLM at multiple weights), (b) declares
  effective hunt closure with structural ceiling at 71, or (c)
  pivots to mandate §7 rubric-revision request.
- **If KILL #78 fires (5050 MDD ≤ 55.17%) AND KILL #80 fires
  (net rank-1 displacement)**: critical empirical finding — net
  rubric matters for deploy. Iter 023 stress-tests the candidate
  via 2008/2022 single-window detail + WF-MDD analysis.
- **If KILL #82 fires (≥ 75 STRONG)**: CRITICAL FINDING — first
  STRONG-tier strategy in entire 22-iter hunt. Iter 023 sensitivity
  + jornada full deep-dive + mandate §7 review case strengthens to
  near-deployable.
- **If MDD bar fails for ALL 6 configs**: B5 family CLOSED via KILL
  #6. Iter 023 pivots to last unsearched direction (C2 CAPE-timing
  or 2× SSO + UBT-2× synth) OR closes hunt at iter 022.

---

## Citations

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — LETF decay
  rationale; replacing 3× TMF with 1× TLT eliminates 1.5%/y duration-
  leg decay.
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking;
  B5 50/50 UPRO/TLT = 150% SPY notional + 50% UST.
- HFEA Bogleheads 2019 — canonical 55/45 anchor; modest-leverage
  variants discussed in subsequent threads but not academically
  dominant.
- `[ilmanen_expected_returns, ch.19]` — MF crisis-alpha (KMLM/DBMF)
  role on modest-leverage barbell.
- `[advances_fin_ml, p.31-34]` factor framework — UPRO + TLT + KMLM
  is a clean 3-factor stack.
- `[advances_fin_ml, p.222-223]` DSR with cumulative n_trials = 80.
- `[advances_fin_ml, p.208-211]` PBO via CSCV (N=6 stable).
- `[advances_fin_ml, p.196-202]` bootstrap CI 99.9% low > 0.
- `WINNER_AND_RANKING.md` "Final ranking — gross vs net" — structural
  net-rubric advantage 1.5pp for buy-hold static.
- studies/long_term_portfolio/synths.py existing UPROSIM, TLTSIM,
  KMLMSIM, DBMFSIM (all direct cache, no synth construction needed).
