# spy_beater_hunt iter 009 — Hypothesis — `B2-hfea-kmlm`

**Slug**: `B2-hfea-kmlm`
**Created**: 2026-04-30
**Cumulative n_trials**: prior 29 + 3 this iter = **32**
**Continuation rationale**: per iter 008 final_report "Suggested iter 009"
+ BASE_MEMORY.direction_status, B1 HFEA classical CLOSED via KILL #24
(spy_real MDD 67.13% > 65% bar; all 3 weights in [50, 60] UPRO range
fail MDD bar at mean 67-72%). The iter 008 lesson identified 2022
inflation regime as the structural killer of the leveraged-barbell
architecture: TMF lost ~−70% concurrent with UPRO ~−50%. The literature-
aware response is to add **MF/CTA crisis-alpha** to the HFEA backbone
— specifically KMLM, whose dose-response was empirically validated on
both SPY-track (iter 003-005) AND TQQQ-track (iter 007) showing
**monotonic positive Sharpe through 40% KMLM with <2pp CAGR drag**.

This iter is the **first crisis-alpha-augmented HFEA test**. If iter 009
caps near ~70 too, iter 010 pivots to **C1 vol-targeted** (different
geometry — dynamic leverage scaling rather than static barbell trade).

---

## Hypothesis

**H₁ (HFEA + 15% KMLM clears the 3 strict bars)**: `b2_hfea_kmlm15`
(50% UPRO + 35% TMF + 15% KMLM) achieves mean CAGR ≥ 11.21% AND mean
MDD ≤ 55.17% AND ≥ 5/5 cross-met gates across (lh_56y, spy_real). The
HFEA leveraged-barbell with 165% UPRO + 105% TMF notional carries
strong CAGR (iter 008 b1_balanced_5050 mean 19.68%); replacing 10pp
TMF with 15pp KMLM reduces concentrated rates-rising risk while adding
trend-following crisis-alpha. KMLM SPY-track empirical (iter 003-005):
+15-30pp KMLM cuts MDD by 10-15pp at <1.5pp CAGR drag. If the same
applies to HFEA, target MDD 50-55% may be reachable, lifting
criterion 2 from 0 → 8-10 pts.

**H₂ (KMLM dose-response monotonic positive on Sharpe through 25%)**:
Pushing KMLM 15% → 20% → 25% (with TMF complement 35% → 30% → 25%)
lifts Sharpe monotonically AND drops MDD monotonically. This mirrors
the iter 003-005 SPY-track KMLM dose-response curve and iter 007
TQQQ-track curve. We expect concave dose-response: marginal MDD relief
slowing at 20-25% but Sharpe still positive. CAGR drag should be
~0.5-1.0pp per +5pp KMLM (consistent with crisis-alpha negative carry).

**H₃ (KMLM crisis-alpha REPLACES TMF cleanly without leverage loss)**:
The KMLM-for-TMF substitution preserves total notional notion (UPRO at
3× equity is the dominant CAGR driver; TMF and KMLM both serve as
diversifiers). If H₃ holds, mean CAGR stays in 17-19% range across
all 3 configs (KMLM has ~3-4% nominal CAGR vs TMF's higher nominal
CAGR but much higher 2022 drawdown). If KMLM-for-TMF causes >3pp
CAGR loss across the dose, the substitution is structurally subordinate
to keeping more TMF (KILL #29 fires).

Citation: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed LETF
decay — TMF decay is regime-dependent, especially severe in 2022.
HFEA Bogleheads 2019 — canonical 55/45 tested in iter 008 (CLOSED).
`[ilmanen_expected_returns, ch.19]` MF crisis-alpha — canonical role
as recession/inflation hedge with ~3-4% nominal CAGR but +α in stress.
`[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking — KMLM
adds diversifying factor exposure without leverage cost. `[advances_fin_ml, p.31-34]`
factor framework — leveraged duration (TMF) and trend-following (KMLM)
are distinct factors with different regime betas; combining mitigates
single-factor concentration. `[advances_fin_ml, p.222-223]` DSR with
cumulative n_trials=32; worst p target < 0.05.

---

## Configs (3, naming `b2_*`)

### 1. `b2_hfea_kmlm15` — anchor (50% UPRO + 35% TMF + 15% KMLM)

```json
{
  "type": "static",
  "weights": {
    "UPROSIM": 0.50,
    "TMFSIM": 0.35,
    "KMLMSIM": 0.15
  }
}
```

Tests: H₁, H₃. Anchor recommendation from iter 008 final_report.
50% × 3× SPY = 150% equity notional + 35% × 3× LTT = 105% duration
notional + 15% × 1× MF = 15% MF notional. Total ~270% notional with
crisis-alpha buffer. The 15pp KMLM is the minimum dose tested in
iter 003 SPY-track (which scored 64 there).

### 2. `b2_hfea_kmlm20` — steeper KMLM dose (50% UPRO + 30% TMF + 20% KMLM)

```json
{
  "type": "static",
  "weights": {
    "UPROSIM": 0.50,
    "TMFSIM": 0.30,
    "KMLMSIM": 0.20
  }
}
```

Tests: H₂. KMLM up 5pp, TMF down 5pp. SPY-track iter 003 KMLM 20% was
the closest-to-winner at the time (Sharpe 0.719/0.692). On HFEA backbone
expected to lower MDD ~3pp and shave ~0.5pp CAGR.

### 3. `b2_hfea_kmlm25` — maximum KMLM dose (50% UPRO + 25% TMF + 25% KMLM)

```json
{
  "type": "static",
  "weights": {
    "UPROSIM": 0.50,
    "TMFSIM": 0.25,
    "KMLMSIM": 0.25
  }
}
```

Tests: H₂ extension. KMLM 25%, TMF 25%. Tests upper bound of crisis-alpha
dose on HFEA — does the marginal MDD relief slow (concave) or invert
(KILL #28 = Sharpe drops)? SPY-track curve from iter 005 monotonic
positive through 40% KMLM, but at HFEA's 165% UPRO notional the
relative MDD geometry differs.

---

## Pre-committed KILL conditions

KILL numbering continues from #26 (last used in iter 008). New: #27, #28, #29.

### KILL #6 (standing — CAGR floor)

If best config across the iter has CAGR mean < 11.21% (the spy_beater
bar), the strategy class is structurally subordinate to SPY buy-hold.
Direction CLOSED.

**Citation**: `WINNER_AND_RANKING.md` Bar 1.

### KILL #27 — KMLM dose insufficient on HFEA backbone

If `b2_hfea_kmlm15` spy_real MDD > 55% AND `b2_hfea_kmlm25` spy_real MDD
> 55%, the KMLM crisis-alpha at 15-25% dose is **insufficient** to
hedge HFEA's 2022 stress. Direction B2 architecturally subordinate to
LRS-style regime-gated strategies on the 2022 stress. Pivot to C1
vol-targeted (iter 010).

**Rationale**: iter 008 spy_real MDD 67.48% on HFEA classical. Need
KMLM dose to cut MDD by >12pp to reach the 55% bar. SPY-track
iter 003-005 showed 30% KMLM cuts 14-18pp; on HFEA's 165% UPRO
notional the geometry is different (UPRO drives 2022 −50% baseline).
If 25% KMLM at HFEA can't reach 55%, **at any reasonable dose** it
won't, because pushing further would require dropping UPRO weight
(which would defeat the high-CAGR rationale of using HFEA backbone
instead of A3 SPY-track in the first place).

### KILL #28 — KMLM dose hurts Sharpe vs HFEA 50/50 baseline

If `b2_hfea_kmlm25` mean Sharpe < 0.740 (iter 008 b1_balanced_5050 Sharpe
mean 0.740) AND `b2_hfea_kmlm20` mean Sharpe < 0.740 on either dataset,
the KMLM-for-TMF substitution **degrades** Sharpe at the dose level.
This would falsify H₂ (monotonic positive on Sharpe through 25%) and
suggest the iter 008 50/50 HFEA Sharpe IS the local optimum — adding
crisis-alpha via KMLM doesn't help because TMF was already the
diversifier doing the work.

**Rationale**: SPY-track iter 003-005 showed KMLM dose monotonic
positive on Sharpe through 40% (Sharpe lifted from 0.65 → 0.82 across
0-40%). If the same pattern applies to HFEA, kmlm25 should be Sharpe
> 0.740 baseline. Failure suggests HFEA's TMF-dominated backbone has
**negative cross-correlation** with KMLM that doesn't transfer cleanly.

### KILL #29 — KMLM-for-TMF substitution kills CAGR

If `b2_hfea_kmlm25` mean CAGR < 13.80% (the F1+SPLIT comparison anchor
and Bogleheads HFEA ~22% CAGR target), the KMLM-for-TMF substitution
is too defensive — falls toward LRS-style returns without LRS-style
regime gate efficiency. Direction CLOSED for HFEA + KMLM blend at
KMLM ≥ 25%; iter 010 pivots to **C1 vol-targeted** or to dialing
KMLM back to 10-15% range (less hedge, retain HFEA CAGR profile).

**Rationale**: HFEA's value proposition is CAGR ~20% via 3× leveraged
equity + 3× LTT. If KMLM substitution drags CAGR below 13.80% (SPY
mean target benchmark), the architecture is no longer differentiated
from A3 SPY-track + KMLM (which scored 66 at iter 004). Direction B2
becomes redundant.

---

## Expected outcomes

| config              | expected CAGR mean | expected MDD mean | expected Sharpe |
|---------------------|-------------------:|------------------:|----------------:|
| b2_hfea_kmlm15      | 17-19%             | 55-60%            | 0.75-0.85       |
| b2_hfea_kmlm20      | 16-18%             | 50-57%            | 0.78-0.88       |
| b2_hfea_kmlm25      | 15-17%             | 47-54%            | 0.80-0.90       |

**Score outlook** (selected ≈ b2_hfea_kmlm25 if monotonic dose holds
and MDD bar barely passes):
- 1. CAGR 30 × clamp((0.16 − 0.05)/0.15, 0, 1) ≈ 22 pts (similar to iter 006)
- 2. MDD 20 × clamp((0.50 − 0.50)/0.40, 0, 1) ≈ 0-12 pts (range — bar pass = 5-12)
- 3. Gates likely 12-13 pts (cross_met = True if MDD < 55%)
- 4. DSR n=32 worst p estimated < 0.01 → 10 pts
- 5. Sharpe ≈ 0.80 → 2-3 pts
- 6. Robustness ≈ 9-10 pts (HFEA + KMLM hybrid pre-2022 strong; 2022 single-window erodes 5y pass-rate but less than HFEA-only)
- 7. Extra 0
- **Total expected**: ~58-72 (range driven by MDD outcome)

**Score-90 path**: structurally improbable in this iter unless KMLM
crisis-alpha cuts MDD substantially below 50%. The most realistic
upside is to score 70-72 (matching/exceeding iter 006's 67), which
would make B2 the new closest-to-winner. The downside (KILL #27 fire)
gives score ~55 and CLOSES B2 direction → iter 010 pivots to C1.

---

## INCOMPLETE flags

1. **TMFSIM synth approximation**: real TMF (Direxion Daily 20+ Year
   Treasury Bull 3×) has variable daily-reset decay depending on
   realised vol. Our synth uses constant 1.5%/y annualised decay
   (`tmf_synth_returns_from_cache`). In high-vol regimes (2022 had
   TLT vol ~22% annualised) real decay was closer to 3-5%/y; our synth
   understates the 2022 drag. The MDD measurement on spy_real may
   underestimate true 2022 HFEA pain by 5-10pp — implying the real
   KILL #27 trigger is even sharper than our synth shows.

2. **KMLMSIM synth scope**: KMLMSIM in testfolio cache from 1986+ uses
   Fama-French momentum factor 1986-1988 + KFA Mount Lucas Index Strategy
   replication 1988+. Real KMLM ETF inception 2020-12; pre-2020 is
   index-replicated synth. Our spy_real (2003+) uses synth from 2003-
   2020 then index 2020+; the 2022 stress test is synth + index hybrid.
   The synth captures the documented MF+CTA crisis-alpha pattern
   (positive in 2008, 2022, 1973-74) but real implementation slippage
   (~0.5-1.0%/y management fee + tracking error) is not modelled.

3. **TLT cache pre-1980 backfill**: TLTSIM cache starts 1962 but
   pre-1986 bars are testfolio's index synth. Within `lh_56y` (1986+)
   this is irrelevant.

4. **UPROSIM cache pre-2009**: real UPRO inception 2009-06; pre-2009
   is testfolio's SPY × 3 with daily-reset decay synth. The 2008 GFC
   stress test on lh_56y is fully synthetic.

5. **No transaction costs / no quarterly rebalance friction**: B2
   assumes daily rebalance (instantaneous); real quarterly HFEA + KMLM
   rebalance has ~0.1-0.3%/y spread + slippage cost. Tax drag on
   rebalance not modelled (iter 008 also INCOMPLETE).

6. **PBO N=3 warning likely**: CSCV statistically unstable below N=4.
   PBO informative-only at this iter level; cumulative `n_trials=32`
   cross-iter grid carries the anti-overfit weight (DSR worst p
   target < 0.05).

7. **2022 stress regime is the falsifiability test for B2**: spy_real
   contains 2022 explicitly; lh_56y synth also captures it. KILL #27
   directly addresses whether KMLM dose at 15-25% can hedge the 2022
   regime stress. The synth+real hybrid captures the documented HFEA
   2022 stress (≈−65% peak-to-trough); KMLM 2022 was +30-35% on the
   real index — that's the specific regime KMLM exists to hedge.

---

## Next-iter sketch (depending on outcome)

- **If `b2_hfea_kmlm25` clears all 3 bars AND scores ≥ 67**: iter 010
  extends with **B2 KMLM 30-35% extreme** (50% UPRO + 20% TMF + 30%
  KMLM and 50% UPRO + 15% TMF + 35% KMLM) to map the dose-response
  curve further. If still monotonic positive Sharpe, may push to score
  72-75.
- **If KILL #27 fires (KMLM dose insufficient on spy_real MDD)**:
  iter 010 pivots to **C1 vol-targeted** (1.5× SPY when 60d vol < 15%,
  else 0.5× → IEF). Different geometry: dynamic leverage, no TMF.
- **If KILL #28 fires (Sharpe regression at KMLM 20-25%)**:
  iter 010 dials KMLM back to 10-15% range AND adds bond complement
  (TLT 5-10pp), testing whether dual diversification (KMLM + TLT) is
  better than single diversification (KMLM alone) on HFEA.
- **If KILL #29 fires (CAGR < 13.80%)**: B2 direction CLOSED;
  iter 010 pivots to C1 or to A3 KMLM-extension on TQQQ-track at
  KMLM 35-40% (already tested but maybe with different leverage).
- **If `b2_hfea_kmlm15` scores ≥ 70 AND winner_conditions_met TRUE**:
  iter 010 sensitivity sweep around 50/35/15 anchor (test 45/40/15,
  55/30/15 to confirm UPRO insensitivity).

---

## Citations

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — LETF decay
  rationale; even with regime gate, leveraged duration is fragile in
  rising-rate regimes (2022) — motivates KMLM crisis-alpha addition.
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking;
  KMLM adds factor diversification at near-zero leverage cost.
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha — canonical role
  as recession/inflation hedge with ~3-4% nominal CAGR but +α in
  stress; +30% in 2022 vs UPRO −50% / TMF −70%.
- HFEA Bogleheads 2019 — canonical 55/45 tested in iter 008 (CLOSED).
- `[advances_fin_ml, p.31-34]` factor framework — leveraged duration
  (TMF) and trend-following (KMLM) are distinct factors with
  different regime betas.
- `[advances_fin_ml, p.222-223]` DSR with cumulative n_trials=32.
- `[advances_fin_ml, p.208-211]` PBO via CSCV (informative at N=3).
- `[advances_fin_ml, p.196-202]` bootstrap CI 99.9% low > 0.
- studies/long_term_portfolio/synths.py `tmf_synth_returns` —
  3× TLT − 1.5%/y daily-reset decay (validated by 3 existing tests,
  standalone Sharpe 1986+ ≈ 0.49).
- studies/spy_beater_hunt/iterations/008-2026-04-30-B1-hfea-classical/
  final_report.md — iter 008 Lesson section recommended B2 HFEA + KMLM
  as iter 009 with KILL sketch matching this hypothesis.
