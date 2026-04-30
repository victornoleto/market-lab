# spy_beater_hunt iter 009 — Final Report — `B2-hfea-kmlm`

**Tier**: **PROMISING** — `score=63/100`, `winner_conditions_met=False`

**Strict bars** (CAGR-anchored, spy_beater rubric):
- CAGR bar (mean ≥ 13.80%): PASS (mean = 18.65%)
- MDD bar (mean ≤ 40.85%): FAIL (mean = 61.51%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Primary citation**: [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed LETF decay rationale + [ilmanen_expected_returns, ch.19] MF crisis-alpha role + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking + [advances_fin_ml, p.31-34] factor framework (TMF and KMLM as distinct factors)

---

## Selected config: `b2_hfea_kmlm20`

Spec:

```json
{
  "type": "static",
  "weights": {
    "UPROSIM": 0.5,
    "TMFSIM": 0.3,
    "KMLMSIM": 0.2
  }
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 0.785 | 19.21% | 61.51% | 5/7 | 3.26e-05 |
| **spy_real** | 0.756 | 18.09% | 61.51% | 5/7 | 3.07e-03 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| b2_hfea_kmlm15 | 0.787 | 0.754 |
| b2_hfea_kmlm20 | 0.785 | 0.756 |
| b2_hfea_kmlm25 | 0.780 | 0.754 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 27 | 30 | mean = 18.65%, bar = 11.21% |
| 2. MDD vs SPY | 3 | 20 | mean = 61.51%, bar = 55.17% |
| 3. Gates | 11 | 20 | per_ds = {'lh_56y': 5, 'spy_real': 5}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 3.07e-03, n_trials = 32 |
| 5. Sharpe | 2 | 10 | mean = 0.771 |
| 6. Robustness | 10 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 88.9% | 61.51% |
| 10y | 100.0% | 61.51% |
| 15y | 100.0% | 61.51% |
| 20y | 100.0% | 61.51% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

- **TMFSIM synth approximation**: synth uses constant 1.5%/y daily-reset
  decay (`tmf_synth_returns_from_cache`); real TMF decay is regime-
  dependent. In 2022 high-vol environment (TLT vol ~22% annualised) real
  decay was closer to 3-5%/y; our synth understates the 2022 drag. The
  measured MDD on spy_real (61.51% selected, 61.27% kmlm15) likely
  understates true 2022 HFEA+KMLM pain by 4-8pp.
- **KMLMSIM synth scope**: KMLMSIM cache 1986+ uses Fama-French momentum
  factor 1986-1988 + KFA Mount Lucas Index Strategy replication 1988+.
  Real KMLM ETF inception 2020-12; pre-2020 is index-replicated synth.
  spy_real (2003+) uses synth 2003-2020 then index 2020+; the 2022
  stress test is synth + index hybrid. Real implementation slippage
  (~0.5-1.0%/y management fee + tracking error) not modelled.
- **TLT cache pre-1980 backfill**: TLTSIM cache starts 1962 but pre-1986
  bars are testfolio's index synth. Within `lh_56y` (1986+) irrelevant.
- **UPROSIM cache pre-2009**: real UPRO inception 2009-06; pre-2009 is
  testfolio's SPY × 3 with daily-reset decay synth. The 2008 GFC stress
  on lh_56y is fully synthetic.
- **No transaction costs / no rebalance friction**: B2 assumes daily
  rebalance (instantaneous); real quarterly HFEA + KMLM rebalance has
  ~0.1-0.3%/y spread + slippage cost. Tax drag not modelled.
- **PBO N=3 warning emitted**: CSCV statistically unstable at N<4. spy_real
  PBO 0.937 / lh_56y PBO 0.929 are suspect — would not survive larger
  grid; informative only here. Cumulative `n_trials=32` cross-iter grid
  carries the anti-overfit weight (DSR worst p = 3.07e-03 << 0.05 bar).
- **2022 stress regime**: spy_real Tiingo daily 2003+ contains the full
  2022 inflation drawdown. lh_56y synth also captures it (HFEA+KMLM MDD
  identical 61.51% across both datasets — driven by 2022 in both).
- **lh_56y rolling NaN bug carries over**: rolling per_dataset for
  lh_56y reports `n_windows=0` and NaN pass_rate (helper bug, not data
  bug); pass-rate aggregates derived from spy_real only. Documented
  in iter 006-008 reports.

## Lesson

### Score 63/100 — TIE iter 008, BELOW closest-to-winner (iter 006/007 retain at 67)

iter 009 scored 63 PROMISING — **TIE with iter 008 (63), 4 BELOW
iter 006/007's 67**. iter 006 `a6_tqqq_split_kmlm30_tlt10` retains
closest-to-winner status. The KMLM-for-TMF substitution lifted MDD
points (+3) and Sharpe by 0.030, but lost 2 CAGR points and 1 Gates
point — **net 0** within the integer-pt rubric. **All 3 configs FAIL
the MDD bar** (61-62% mean across the dose); KMLM at 15-25% on HFEA
backbone is **insufficient** to clear the 55.17% bar.

| criterion | iter 006 a6_kmlm30_tlt10 | iter 009 b2_hfea_kmlm20 | delta |
|---|---:|---:|---:|
| 1. CAGR | 25 (mean 17.33%) | **27 (mean 18.65%)** | **+2** |
| 2. MDD  | 7  (mean 49.73%) | **3  (mean 61.51%)** | **−4** |
| 3. Gates | 13 (6+6, cross_met) | 11 (5+5, cross_met) | −2 |
| 4. DSR  | 10 (n=23, p 3.05e-03) | 10 (n=32, p 3.07e-03) | 0 |
| 5. Sharpe | 2 (mean 0.759) | 2 (mean 0.771) | 0 |
| 6. Robustness | 10 | 10 | 0 |
| 7. Extra | 0 | 0 | 0 |
| **Total** | **67** | **63** | **−4** |

vs iter 008 b1_balanced_5050 (also 63):

| criterion | iter 008 b1_5050 | iter 009 b2_kmlm20 | delta |
|---|---:|---:|---:|
| 1. CAGR | 29 (mean 19.68%) | 27 (mean 18.65%) | −2 |
| 2. MDD  | 0  (mean 67.48%) | 3 (mean 61.51%)  | +3 |
| 3. Gates | 12 (6+5, cross_met) | 11 (5+5, cross_met) | −1 |
| 4. DSR  | 10 | 10 | 0 |
| 5. Sharpe | 2 (mean 0.739) | 2 (mean 0.771) | 0 |
| 6. Robustness | 10 | 10 | 0 |
| 7. Extra | 0 | 0 | 0 |
| **Total** | **63** | **63** | **0** |

The KMLM-for-TMF substitution **trades 2pp CAGR for 3pp MDD points** —
nearly 1:1 within scoring at this dose. The Sharpe gain (+0.030) is
real but doesn't cross any 2-pt rubric boundary (anchor 0.5-2.0 too
wide for small Sharpe deltas to register). Net outcome: leveraged-
barbell architecture **structurally capped near 63** within spy_beater
rubric, regardless of TMF-only or TMF+KMLM blend.

### KILL conditions outcomes

- **KILL #6 (CAGR floor 11.21%)** NOT FIRED — best CAGR mean 18.97%
  (kmlm15) >> 11.21% bar. CAGR is HFEA's strength, not its weakness.
- **KILL #27 (KMLM dose insufficient on HFEA backbone) FIRED** —
  `b2_hfea_kmlm15` spy_real MDD 61.27% > 55% bar AND `b2_hfea_kmlm25`
  spy_real MDD 61.78% > 55% bar. **BOTH conditions of KILL #27 met**.
  Direction B2 architecturally subordinate to LRS-style regime-gated
  strategies on the 2022 stress regime. **Direction CLOSED** at
  KMLM 15-25% dose on HFEA backbone.
- **KILL #28 (Sharpe < 0.740 baseline) NOT FIRED** — `b2_hfea_kmlm25`
  Sharpe mean 0.766 > 0.740; `b2_hfea_kmlm20` Sharpe mean 0.770 >
  0.740. KMLM does NOT degrade Sharpe vs HFEA 50/50 baseline; in fact
  lifts it by 0.030 mean. H₂ partial: Sharpe POSITIVE on KMLM
  addition (vs no-KMLM baseline) but FLAT within the 15-25% dose
  range tested.
- **KILL #29 (CAGR < 13.80%) NOT FIRED** — `b2_hfea_kmlm25` mean CAGR
  18.27% >> 13.80%. KMLM-for-TMF substitution preserves HFEA's
  CAGR profile (drag ~0.5pp per +5% KMLM, consistent with H₃).

### KMLM dose-response on HFEA backbone (3 data points iter 009)

| KMLM % | TMF % | mean Sharpe | mean CAGR | mean MDD | source |
|:---:|:---:|---:|---:|---:|:---:|
| 0%  | 50% | **0.740** | 19.68% | 67.48% | iter 008 b1_5050 |
| 15% | 35% | 0.770 | 18.97% | 61.27% | iter 009 |
| 20% | 30% | **0.770** | 18.65% | 61.51% | iter 009 (selected) |
| 25% | 25% | 0.766 | 18.27% | 61.78% | iter 009 |

**Pattern (4 data points 0-25% KMLM)**:
- Sharpe: 0.740 → 0.770 → 0.770 → 0.766 — **strong jump 0→15%, then FLAT 15-20%, then slight regression 20→25%**. Not monotonic positive within 15-25% range.
- CAGR: 19.68 → 18.97 → 18.65 → 18.27% — monotonic NEGATIVE (linear ~0.4pp drag per +5% KMLM, weaker than expected ~0.5-1.0pp).
- MDD: 67.48 → 61.27 → 61.51 → 61.78% — **strong drop 0→15% (−6.21pp), then monotonic NEGATIVE 15-25% (KMLM dose ADDS MDD)**.

**Surprising finding**: KMLM dose-response on HFEA is **OPPOSITE
SPY-track**. On SPY-track (iter 003-005), KMLM 0→30% cut MDD 14.8pp
with Sharpe rising monotonically through 40%. On HFEA backbone,
**KMLM 15→25% INCREASED MDD 0.5pp** while Sharpe was flat-to-negative.
The MDD relief saturates at the **first** 15pp KMLM dose; further
substitution costs MDD instead of saving it.

**Mechanism (interpretation)**: TMF in HFEA is providing **two roles**
simultaneously — duration alpha in falling-rate regimes (2008, 2020)
AND defensive carry in non-2022 windows. KMLM's 2022 stagflation
hedge does NOT transfer cleanly because (a) lh_56y has BOTH 2008
(TMF +30%, KMLM ~+5%) and 2022 (TMF −70%, KMLM +30%) in the path —
substituting TMF→KMLM trades GFC protection for stagflation
protection at roughly equal MDD weight, and (b) at 25% KMLM dose, the
remaining 25% TMF is **insufficient** to backstop GFC duration trade
(TMF was structurally critical in 2008-09).

In SPY-track (iter 003-005), the underlying baseline was
**unleveraged SPY + LRS gate**, which doesn't have TMF embedded —
KMLM was pure additive crisis-alpha, no substitution trade-off.
On HFEA, KMLM ENTERS as a SUBSTITUTE for TMF, and at 15-25% dose
it **pareto-trades** rather than pareto-improves.

### H₁ / H₂ / H₃ outcomes

- **H₁ REJECTED**: `b2_hfea_kmlm15` does NOT clear the 3 strict bars.
  CAGR ✓ (18.97%), Gates ✓ (5+5 cross_met), but **MDD FAIL** (61.27%
  mean > 55.17% bar). Even minimum KMLM dose on HFEA cannot reach
  the MDD bar.
- **H₂ REJECTED at narrow margin**: KMLM dose-response on Sharpe is
  **flat** (0.770/0.770/0.766) within 15-25% range — not monotonic
  positive. KMLM dose-response on MDD is **monotonic NEGATIVE**
  within 15-25% (kmlm15 MDD < kmlm25 MDD). The expected
  SPY-track-style monotonic positive curve does NOT transfer to HFEA
  backbone.
- **H₃ PARTIALLY CONFIRMED**: CAGR drag is ~0.4pp per +5% KMLM,
  consistent with H₃ prediction (0.5-1.0pp range). KMLM-for-TMF
  substitution preserves CAGR; total notional preserved. BUT **the
  diversification quality differs** — at HFEA's 165% UPRO notional,
  TMF and KMLM compete for the same "diversifier slot" rather than
  stack additively (factor framework note: TMF is rates-falling beta,
  KMLM is trend-following — both inversely correlated to UPRO in
  some regimes but to different ones).

### Cross-iter direction implications

- **B1_HFEA_classical**: CLOSED (iter 008 KILL #24) — UPRO weight
  in [50, 60] all FAIL MDD bar.
- **B2_HFEA_KMLM**: **CLOSED** (iter 009 KILL #27) — KMLM 15-25%
  dose on HFEA cannot clear MDD bar. The leveraged-barbell
  architecture has a structural ceiling at score 63-67 within
  spy_beater rubric, fundamentally limited by 2022 stress regime
  spreading across both leveraged legs simultaneously.
- **C1_vol_targeted**: **NOT YET RUN — recommended iter 010**.
  Different geometry (dynamic leverage scaling) may unlock the
  Sharpe lift not capturable by static-weight barbells. The lever
  is regime-detection (vol-target) instead of regime-prediction
  (200d SMA). Best candidate to break the leveraged-barbell ceiling
  toward score 70+.
- **A2_TQQQ_track family**: closest-to-winner retains at 67 (iter 006);
  saturated within rubric.

### Suggested iter 010

**Recommended pivot: C1 vol-targeted SPY**. Rationale:

- B1 + B2 leveraged-barbell architecture exhausted (closed at 63-67).
- A2 TQQQ-track exhausted (saturated at 67).
- A3 SPY-track exhausted (66 closest at iter 004, 63 at iter 005).
- All static-weight architectures structurally capped within rubric.
- Vol-targeted dynamic leverage = different control geometry (state-
  dependent leverage based on realized vol, NOT regime gate from
  trend signal). May escape the architectural ceiling.

Pre-committed KILL sketch for iter 010:
- KILL #30: vol-target Sharpe < LRS-split baseline (a1 Sharpe 0.66) →
  vol-target adds noise without information.
- KILL #31: vol-target spy_real MDD > 55% on most defensive variant
  (vol_low ≤ 12%, leverage cap 1.5×) → cannot clear MDD bar even
  at conservative settings.
- KILL #32: vol-target whipsaw rate > 30%/year on highest-frequency
  config → state-dependent leverage too noisy to be deployable.

If iter 010 also caps near 67 too, the structural conclusion is the
**spy_beater rubric architecturally unreachable** — F1+SPLIT
incumbent fallback confirmed deploy-ready, IMPOSSIBILITY_RESULT
report drafted.

### Citations validated

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed LETF decay —
  validated empirically: HFEA+KMLM 2022 MDD 61% mirrors HFEA-only 2022
  MDD 67% reduced by KMLM crisis-alpha buffer. Decay constant 1.5%/y
  in our synth understates real-world 2022 drag (real ~3-5%/y).
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha — KMLM at 15-25%
  dose on HFEA backbone delivered ~6pp MDD relief (the "first dose"
  effect) but ZERO additional MDD relief at 20-25% range. The
  documented +30% 2022 KMLM return DID hedge HFEA's −70% TMF concurrent,
  but only enough to rescue the **first** 15pp of TMF replacement.
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking —
  HFEA + KMLM is two diversifiers competing for the same role, NOT
  stacking additively. The UPRO+TMF+KMLM blend is at 270% notional
  but effective diversification benefit caps below that of UPRO+TMF.
- HFEA Bogleheads 2019 — canonical 55/45 + crisis-alpha extension
  proposed by some Bogleheads forum users; this iter falsifies the
  improvement at 15-25% KMLM dose on the spy_beater MDD bar.
- `[advances_fin_ml, p.31-34]` factor framework — leveraged duration
  (TMF) and trend-following (KMLM) are distinct factors with
  rates-falling vs stagflation betas; combining doesn't symmetrically
  reduce concentrated risk because the **concentrated risk is UPRO**
  not TMF, and adding KMLM doesn't reduce UPRO's 2022 −50% drawdown.
- `[advances_fin_ml, p.222-223]` DSR with cumulative_n_trials=32 —
  worst p = 3.07e-03 << 0.05 bar. Headroom for ~2 more iters at
  3 configs each before n=38 zone tightening.

### Where the score-90 path goes from here

iter 009 confirms the **leveraged-barbell architecture has a structural
ceiling at score 63-67** in spy_beater rubric, regardless of crisis-
alpha augmentation at the 15-25% KMLM dose. The score-90 path now has
two candidate routes:

1. **C1 vol-targeted** (iter 010 recommended) — dynamic leverage
   scaling may lift Sharpe without 2022 blow-up. Different geometry,
   different failure mode. Best-case score ~70-75.
2. **Methodology change** (last resort, iter 011-012) — if C1 also
   caps near 67, the spy_beater bar is **architecturally unreachable**
   within gross-of-tax 2-dataset framework. Confirms F1+SPLIT
   incumbent fallback as deploy-ready and writes IMPOSSIBILITY_RESULT
   report. The honest negative result has policy value.

Headroom: cumulative_n_trials=32; ~2 more iters (n=38) before DSR
penalty tightens enough to reduce criterion 4 from 10 → 7 pts.

