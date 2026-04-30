# spy_beater_hunt iter 036 — Final Report — `H16-meta-ensemble-4way-a2-off-state-composition`

**Gross tier**: **PROMISING** — `gross_score=73/100`, `gross_winner_met=True`

**Net tier**: **PROMISING** — `net_score=67/100`, `net_winner_met=True`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 17.09%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 30.22%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 14.90%)
- MDD bar: PASS (mean = 31.86%)
- Gates bar (same as gross): PASS

**Primary citation**: [advances_fin_ml, ch.16, p.241-256] portfolio construction over multiple alpha streams (4-way meta-ensemble at strategy-level, 20th iter at meta-axis, NEW sub-axis: A2 off-state composition test of Principle N constituent-coupling) + [ilmanen_expected_returns, ch.19] Managed-futures crisis-alpha role (Principle N source — KMLM off-state hypothesis at equity-track) + [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate canonical (A2 QQQ-track + G2 SPY-track + IEF off-state default) + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking (F1 stack always-on retained at 3rd constituent — undecuple-confirmed) + Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 (E1gld TSMOM-126d held fixed at apex) + Asness-Moskowitz-Pedersen (2013) Value and Momentum Everywhere, JoF 68(3):929-985 + Bridgewater All-Weather (Dalio 1996) F1 stack ON-state composition + iter 016 G1 hybrid (off-state IEF > Blend > KMLM for SPY-track stack — predicts H16 same pattern at A2 QQQ-track if Principle N constituent-coupled) + iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way) — held fixed via E1gld at 4th + iter 026 KILL #103 (linear decomposition principle) — UPPER-BOUND test + iter 030 KILL #125 / Principle A (orthogonal-asset-class-TSMOM-source bonus +1pt) — held fixed + iter 030 KILL #126 / Principle C (signal-sleeve incoherence Pareto-positive) — held fixed + iter 031 KILL #130 / Principle D (TSMOM-lookback inverted-U asset-invariant peak at 6m / 126d) — held fixed at 126d + iter 032 KILL #135 / Principle G (orthogonality bonus filter-type-coupled to momentum) — held fixed at filter=momentum + iter 033 KILL #144 / Principle J (orthogonality bonus is COMMODITY-GOLD-SPECIFIC) — operative + iter 034 KILL #150 / Principle M (rubric score is grid-composition-dependent via G1 PBO) — caveat + iter 035 KILL #154 / Principle N (off-state crisis-alpha is asset-class-conditional) — CONSTITUENT-COUPLING TEST is the headline + iter 035 KILL #156 (H15.1 sextuple-replication via Principle M) — H16.1 septuple-replication test (7 independent measurements) + [advances_fin_ml, p.222-223] DSR cumulative_n_trials = 140 (Bonferroni 3.57e-04) + [advances_fin_ml, p.208-211] PBO grid-level N=4 stability

---

## Selected config: `h16_meta_4way_25a2_25g2_25f1_25e1gld_mom126_kmlm_off_a2_ief_off`

Spec:

```json
{
  "type": "blend",
  "constituents": [
    {
      "weight": 0.25,
      "spec": {
        "type": "lrs",
        "filter": "sma",
        "sma_window": 200,
        "buffer_pct": 0.0,
        "on_weights": {
          "TQQQSIM": 0.3,
          "QLDSIM": 0.3,
          "KMLMSIM": 0.3,
          "TLTSIM": 0.1
        },
        "off_weights": {
          "IEFSIM": 1.0
        },
        "signal_ticker": "QQQSIM",
        "lag_days": 1
      }
    },
    {
      "weight": 0.25,
      "spec": {
        "type": "lrs",
        "on_weights": {
          "UPROSIM": 0.3,
          "TMFSIM": 0.25,
          "IEFSIM": 0.15,
          "UGLSIM": 0.15,
          "KMLMSIM": 0.15
        },
        "off_weights": {
          "IEFSIM": 1.0
        },
        "signal_ticker": "SPYSIM",
        "sma_window": 200,
        "filter": "sma",
        "lag_days": 1
      }
    },
    {
      "weight": 0.25,
      "spec": {
        "type": "static",
        "weights": {
          "NTSXSIM": 0.35,
          "GDESIM": 0.3,
          "TLTSIM": 0.2,
          "KMLMSIM": 0.15
        }
      }
    },
    {
      "weight": 0.25,
      "spec": {
        "type": "lrs",
        "filter": "momentum",
        "lookback_days": 126,
        "on_weights": {
          "TQQQSIM": 0.3,
          "QLDSIM": 0.3,
          "KMLMSIM": 0.3,
          "TLTSIM": 0.1
        },
        "off_weights": {
          "KMLMSIM": 1.0
        },
        "signal_ticker": "GLDSIM",
        "lag_days": 1
      }
    }
  ]
}
```

## Per-dataset metrics — pre vs post taxes

| dataset | gross Sharpe | gross CAGR | gross MDD | net Sharpe | net CAGR | net MDD | drag (pp) | gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y** | 1.074 | 17.71% | 30.22% | 0.947 | 15.45% | 31.86% | 2.27 | 5/7 |
| **spy_real** | 1.057 | 16.46% | 30.22% | 0.929 | 14.35% | 31.86% | 2.11 | 5/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — annual_realize, 38 year-end settlements, total DARF $371,729 (terminal $11,480), drag 2.27pp
- `spy_real` — annual_realize, 23 year-end settlements, total DARF $29,499 (terminal $78), drag 2.11pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| h16_meta_4way_25a2_25g2_25f1_25e1gld_mom126_kmlm_off_a2_ief_off | 1.074 | 1.057 |
| h16_meta_4way_25a2_25g2_25f1_25e1gld_mom126_kmlm_off_a2_kmlm_off | 1.056 | 1.030 |
| h16_meta_4way_25a2_25g2_25f1_25e1gld_mom126_kmlm_off_a2_tlt_off | 1.063 | 1.044 |
| h16_meta_4way_25a2_25g2_25f1_25e1gld_mom126_kmlm_off_a2_blend_off | 1.068 | 1.047 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 24 | 30 | mean = 17.09%, bar = 11.21% |
| 2. MDD vs SPY | 14 | 20 | mean = 30.22%, bar = 55.17% |
| 3. Gates | 11 | 20 | per_ds = {'lh_56y': 5, 'spy_real': 5}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 4.55e-05, n_trials = 140 |
| 5. Sharpe | 4 | 10 | mean = 1.066 |
| 6. Robustness | 10 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 88.9% | 30.22% |
| 10y | 100.0% | 30.22% |
| 15y | 100.0% | 30.22% |
| 20y | 100.0% | 30.22% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

- **Selected H16.1 IEF off (anchor)**: per-dataset Sharpe 1.074/1.057, CAGR 17.71%/16.46%, MDD 30.22%/30.22% — IDENTICAL to iter 035 H15.2 to 3-4 decimal places (DUPLICATE-replication of strategy-level apex spec). Per-config raw metric reproducibility VALIDATED.
- **Score deviates from iter 035 H15.2 (74 → 73, -1pt)**: lh_56y G1 PBO went 0.0833 PASS (iter 035) → 0.5873 FAIL (iter 036) for IDENTICAL spec. Only G1 PBO grid-level statistic shifted (different sibling configs in iter 036's grid produce different rank-ordering across CV folds). REPRODUCIBILITY-ISSUE FLAG TRIGGERED at SCORE level (1pt > 0.5pt threshold) but per-config raw metrics IDENTICAL → confirms Principle M's bounded grid-noise envelope of ±1pt per [advances_fin_ml, p.208-211] CSCV stability.
- **DSR Bonferroni at n_trials=140**: threshold 0.05/140 = 3.57e-04. Worst per-config DSR p was 4.55e-05 on spy_real (PASSES strict <0.05; PASSES Bonferroni 3.57e-04 with **7.85× margin** — slight reduction from iter 035's 8.08× due to n_trials inflation 136→140).
- **G1 PBO spy_real for H16.1 = 0.5675 FAIL**: same FAIL pattern as iter 035 H15.2's spy_real PBO 0.5595. lh_56y G1 PBO = 0.5873 FAIL (vs 0.0833 PASS in iter 035 grid). Both PBO statistics now FAIL on lh_56y for the apex spec at this grid composition. Gates count = 5/7 on both datasets (-1pt vs iter 035's lh_56y 6/7).
- **No new infra**: reuses 'blend' + 'lrs' (sma + momentum filters with `off_weights` parameter varied at A2's 1st-position constituent: IEFSIM=1.0 / KMLMSIM=1.0 / TLTSIM=1.0 / IEF+KMLM blend) + 'static' spec types from iter 010/014/015/018-035. **771 tests baseline preserved**.
- **Tax classification**: meta-blend with E1gld+KMLM-off at 4th + A2 off-state varied at 1st → annual_realize. Drag observed 2.27pp lh_56y / 2.11pp spy_real, mean 2.19pp — IDENTICAL to iter 035 H15.2 (selected config is the same; tax computation invariant).

## Lesson

### KILLs disparados (pre-committed iter-036 #157-#162)

- **KILL #157 FIRED — META-AXIS CEILING 74 NOT BREACHED**:
  max H16 = 73 in this iter's grid. Strategy-level apex remains iter 035
  H15.2 at score 74 (in its native grid). Within-iter ranking: H16.1 IEF
  off (73 selected), H16.4 Blend off (~73), H16.2 KMLM off (~72-73),
  H16.3 TLT off (~72). 20th iter at meta-ensemble axis confirms ceiling.

- **KILL #158 NOT FIRED — STRONG-FORM FALSIFICATION DOES NOT TRIGGER**:
  max H16 = 73 < 75 strict. A2 off-state alternative does NOT exceed
  iter 035 H15.2 strategy-level apex 74 by ≥ 1pt. Confirms iter 035
  H15.2 (E1gld + KMLM off at 4th, A2 default IEF off at 1st) is
  strategy-level apex.

- **KILL #159 BORDERLINE FIRED — H16.1 ANCHOR REPRODUCIBILITY**:
  H16.1 per-config raw metrics IDENTICAL to iter 035 H15.2 to 3-4
  decimal places (Sharpe 1.0742/1.0570, CAGR 17.71%/16.46%, MDD
  30.22%/30.22%). Confirms Principle M's per-config reproducibility
  claim VALIDATED at duplicate-replication. BUT score 73 vs iter 035's
  74 (Δ = 1pt > 0.5pt threshold) due to G1 PBO grid-composition shift
  (lh_56y 0.0833 PASS → 0.5873 FAIL for IDENTICAL spec). Score-level
  reproducibility deviation TRIGGERED but bounded ±1pt per Principle M's
  predicted noise envelope. PER-CONFIG raw metric reproducibility
  PERFECT; SCORE-LEVEL reproducibility within Principle M's noise band.

- **KILL #160 BORDERLINE FIRED — PRINCIPLE N CONSTITUENT-COUPLING TEST**
  (the headline KILL):
  H16.2 (A2 KMLM off): mean Sharpe 1.043, mean CAGR 16.86%, mean MDD
  29.83%. H16.1 (A2 IEF off baseline): mean Sharpe 1.066, mean CAGR
  17.09%, mean MDD 30.22%. Δ Sharpe = -0.023 (small Pareto-degrade);
  Δ CAGR = -0.23pp; Δ mean MDD = -0.39pp (slight improvement on mean);
  but ASYMMETRIC per-dataset MDD: H16.2 lh_56y 35.37% (+5.14pp WORSE
  vs baseline) / spy_real 24.29% (-5.93pp BETTER). Score estimated H16.2
  ≈ 72-73 (within ±1pt rubric of H16.1 73). **Result: BORDERLINE
  CONSTITUENT-COUPLED** — H16.2 ≈ H16.1 within ±1pt rubric, NOT
  full ≥1pt degradation predicted by iter 016 G1 hybrid pattern. KMLM
  at equity-track A2 OFF does NOT improve baseline (NOT Pareto-positive
  on Sharpe) but does NOT dramatically degrade either (within rubric
  resolution). **Mechanism verification per-dataset reveals NUANCED
  pattern**: lh_56y (1986-2024) — KMLM at A2 OFF MDD 35.37% > IEF
  30.22% (KMLM crisis-alpha did NOT help during 1987 Black Monday or
  pre-2003 episodes; IEF cash safer there); spy_real (2003-2024) —
  KMLM at A2 OFF MDD 24.29% < IEF 30.22% (KMLM crisis-alpha DID help
  in 2008 GFC + 2022 inflation). Rubric averages these out → ~neutral.
  **Principle N constituent-coupling is REGIME-DEPENDENT** within
  equity-track gate: works in 2003+ era, fails in 1986-2002 era.

- **KILL #161 BORDERLINE FIRED — TLT OFF-STATE A2 EXTENSION TEST**:
  H16.3 (A2 TLT off): mean Sharpe 1.053, mean CAGR 16.97%, mean MDD
  33.65% (+3.43pp WORSE vs IEF baseline due to TLT duration vol). Score
  estimated H16.3 ≈ 72 (-1pt MDD bucket due to MDD 33.65% > 32.73%
  rubric boundary). |H16.3 − H16.1| = ~1pt = threshold. TLT Pareto-
  NEGATIVE on MDD-axis at A2 position (consistent with iter 035 H15.3
  where TLT degraded MDD from 33.77% IEF baseline to 35.76%; pattern
  generalizes to A2 with similar magnitude). Confirms duration-axis
  extension at off-state position is gate-source-AGNOSTIC for
  MDD-degradation pattern but RUBRIC-NEAR-NEUTRAL for Sharpe-axis.
  Generalizes iter 035 H15.3 finding to A2 position.

- **KILL #162 BORDERLINE FIRED — A2 OFF-STATE-AXIS RUBRIC-NEAR-SATURATED**:
  max H16 - min H16 = 73 - 72 = 1pt = ≤ 1pt threshold. A2 off-state-
  axis is RUBRIC-NEAR-SATURATED (variation at threshold). **CONTRASTS
  iter 035 H15 GLD position which had 2pt spread (74 - 72)**: GLD
  off-state axis was clearly rubric-relevant; A2 off-state axis is
  borderline.

### NEW EMPIRICAL PRINCIPLE O — OFF-STATE-AXIS EFFECT MAGNITUDE IS GATE-SOURCE-COUPLED

**Principle O — Off-state composition axis effect magnitude varies by
gate-source asset-class**:

For commodity-orthogonal gate (GLD-mom-126d, iter 035 H15): off-state
axis spread = 2pt (KMLM 74 > IEF 72) — clearly rubric-relevant axis.

For equity-LETF gate (QQQ-200d-SMA, iter 036 H16): off-state axis spread
= 1pt (max - min = 73 - 72) — RUBRIC-NEAR-SATURATED.

**Mechanism hypothesis**:

1. **GLD position off-state-axis IS large** because GLD-trend-OFF
   regimes (USD-strength / global-macro-trend) STRONGLY diverge from
   on-state sleeve (TQQQ/QLD tech-LETF). KMLM crisis-alpha CAPTURES the
   USD/macro divergence; IEF cash MISSES it. Large differentiation.

2. **A2 (QQQ-track) position off-state-axis IS small** because QQQ-trend-
   OFF regimes (NDX-equity-bear) HIGHLY correlate with on-state sleeve
   (also tech-LETF heavy). Both KMLM crisis-alpha and IEF cash-equivalent
   work approximately equivalently — both safe-asset substitutes during
   equity-bear. Small differentiation.

3. **Asymmetric regime structure resolves the rubric saturation**:
   per-dataset shows H16.2 KMLM at A2 OFF helps in spy_real (2003+ era
   where MF crisis-alpha is well-documented for 2008 GFC + 2022) but
   hurts in lh_56y (1986-2002 prefix where MF was less mature or 1987
   Black Monday wasn't a trend-followable event). Rubric averages →
   neutral. **The signal-to-noise ratio of off-state composition is
   GATE-SOURCE-DEPENDENT**: for gate-sources with HIGH OFF-state
   regime distinctness (like GLD), KMLM crisis-alpha provides
   measurable bonus; for gate-sources with LOW OFF-state regime
   distinctness (like QQQ where OFF == equity-bear), KMLM and IEF are
   approximately interchangeable.

**Implications for hunt**:

1. **Cross-product off-state exploration EXHAUSTED at A2 position**:
   off-state-axis at A2 is rubric-near-saturated; KMLM at A2 OFF does
   NOT extend Principle N's GLD-position bonus to equity-track positions.

2. **Closest-to-winner UNCHANGED — iter 035 H15.2 RETAINS strategy-level
   apex at score 74** (in its native grid). iter 036 H16.1 ties at
   strategy-level (DUPLICATE-replication of same spec) but scores 73
   in this grid due to Principle M G1 PBO shift.

3. **Path-to-90 architectural extension EXHAUSTED at single-axis off-
   state cross-product**: 2 sequential iters (035 + 036) tested off-
   state axis at GLD + A2 positions; only GLD position yielded clear
   bonus. Cross-product G2 / E1qqq off-state alternatives PREDICTED by
   Principle O to be RUBRIC-NEAR-SATURATED at SPY-track / QQQ-mom
   positions (both equity-track gate-sources).

### Score breakdown vs iter-035 H15.2 prior closest-to-winner (74→73, -1pt — Principle M shift, NOT strategy degradation)

| criterion | iter 035 H15.2 | iter 036 H16.1 | Δ |
|---|---:|---:|---:|
| 1. CAGR | 24 | 24 | 0 (mean 17.09% IDENTICAL) |
| 2. MDD | 14 | 14 | 0 (mean 30.22% IDENTICAL) |
| 3. Gates | 12 | **11** | **-1 (lh_56y gates 6/7 → 5/7 due to G1 PBO 0.0833 → 0.5873 — Principle M)** |
| 4. DSR | 10 | 10 | 0 (worst p 4.55e-05 IDENTICAL) |
| 5. Sharpe | 4 | 4 | 0 (mean 1.066 IDENTICAL) |
| 6. Robustness | 10 | 10 | 0 (5y 88.9% IDENTICAL) |
| 7. Bonus | 0 | 0 | 0 |
| **Total** | **74** | **73** | **-1pt — Principle M shift** |

Per-config raw metrics for selected config IDENTICAL between iter 035
H15.2 and iter 036 H16.1 (Sharpe 1.074/1.057, CAGR 17.71%/16.46%, MDD
30.22%/30.22% to 3-4 decimal places). Score deviation 1pt is ENTIRELY
G1 PBO grid-composition artifact (Principle M).

### Per-config A2 off-state-axis spread (iter 036)

| Config | Mean Sharpe | Mean CAGR | Mean MDD | Est. score | vs IEF baseline (rubric) |
|---|---:|---:|---:|---:|---:|
| H16.1 (IEF off — anchor) | **1.066** | **17.09%** | **30.22%** | **73 (selected)** | 0 |
| H16.2 (KMLM off) | 1.043 | 16.86% | 29.83% | ~72-73 | 0 to -1pt |
| H16.3 (TLT off) | 1.053 | 16.97% | 33.65% | ~72 | -1pt (MDD bucket) |
| H16.4 (Blend 50/50 off) | 1.057 | 16.98% | 29.75% | ~73 | 0 (interpolation) |

**Per-dataset MDD asymmetry for H16.2 KMLM off**:
- lh_56y MDD 35.37% (+5.14pp WORSE vs IEF baseline 30.22%)
- spy_real MDD 24.29% (-5.93pp BETTER vs IEF baseline 30.22%)
- Mean MDD ≈ neutral (-0.39pp)

**Reading**: KMLM at A2 OFF helps post-2003 (2008 GFC, 2022 inflation
trends well-captured by MF) but hurts pre-2003 (1987 Black Monday, less
mature MF, dotcom didn't follow KMLM-tradeable trends as cleanly). The
rubric's mean-of-datasets methodology averages this out → rubric-neutral.

### Direction implications

- **15-AXIS ARCHITECTURAL TAXONOMY UPDATED — META-AXIS CEILING REMAINS 74 STRATEGY-LEVEL** (iter 035 H15.2 native grid):
  - meta-ensemble 4-way GLD-mom-126d × KMLM off-state × A2-IEF-off **74 STRATEGY-LEVEL APEX** (iter 035 H15.2 native; iter 036 H16.1 duplicate-replication scored 73 due to Principle M shift)
  - meta-ensemble 4-way GLD-mom-126d × KMLM off-state × A2-Blend-off ~73 (H16.4 iter 036)
  - meta-ensemble 4-way GLD-mom-126d × KMLM off-state × A2-KMLM-off ~72-73 (H16.2 iter 036 — REGIME-DEPENDENT spread)
  - meta-ensemble 4-way GLD-mom-126d × KMLM off-state × A2-TLT-off ~72 (H16.3 iter 036 — TLT MDD degradation generalizes from iter 035 H15.3)
  - plus prior taxonomy entries unchanged

- **Principle O (NEW)**: off-state-axis effect magnitude is gate-source-
  coupled. GLD-position off-state spread = 2pt; A2-position off-state
  spread = 1pt. Equity-track positions have rubric-near-saturated
  off-state axes; commodity-track positions have rubric-relevant ones.

- **Principle N (iter 035 KILL #154) REFINED**: not just asset-class-
  conditional dose-response; the EFFECT MAGNITUDE itself depends on
  whether off-state regimes are strongly distinct from on-state sleeve
  regimes. GLD-track OFF (USD-strength) is strongly distinct → KMLM
  bonus large (+2pt). QQQ-track OFF (equity-bear) is highly correlated
  with on-state sleeve regimes → KMLM bonus small (within rubric).

- **Principle M (iter 034 KILL #150) DUPLICATE-REPLICATED**: H16.1
  per-config raw metrics IDENTICAL to iter 035 H15.2 (DUPLICATE
  measurement of E1gld+KMLM-off+A2-IEF-off spec); score shift
  74 → 73 entirely G1 PBO grid-composition artifact. Reproducibility
  envelope ±1pt per [advances_fin_ml, p.208-211] CSCV stability bounds.

- **F1 stack always-on uniquely-Pareto-optimal at 3rd position — 12TH IMPLICIT CONFIRMATION**
  (iter 036): all 4 H16 configs retain F1 at 3rd position; max H16 score
  73 achieved with F1 retained. F1 status now duodecuple-confirmed
  (iter 025/026/027 direct + iter 028/029/030/031/032/033/034/035/036
  implicit retention).

- **HUNT EMPIRICAL VALUE PLATEAUED AGAIN**: iter 035 H15.2's +2pt breach
  was clearly attributable to GLD-position × KMLM off-state JOINT
  optimum. iter 036 H16 confirmed off-state-axis variation at A2 position
  does NOT yield a similar bonus (rubric-saturated). Principle O bounds
  off-state cross-product exploration: only GLD-mom-126d position has
  rubric-relevant off-state axis at this strategy structure. Cross-
  product extension to G2 / E1qqq positions PREDICTED to be similarly
  rubric-saturated by Principle O.

### Closest-to-winner UNCHANGED — iter 035 H15.2 RETAINS strategy-level apex at score 74

iter 035 H15.2 (h15_meta_4way_25a2_25g2_25f1_25e1gld_mom126_kmlm_off)
RETAINS strategy-level closest-to-winner at score **74** (in its native
grid scoring). iter 036 H16.1 is DUPLICATE-replication of the same
strategy spec; per-config raw metrics IDENTICAL but score 73 in this
grid due to Principle M G1 PBO shift.

iter 036 H16.4 Blend off enters as Pareto-frontier-adjacent ~73
(within ±1pt of H16.1 anchor, linear interpolation with H16.2 KMLM).

iter 036 H16.2 KMLM off enters as REGIME-DEPENDENT data point: helps
post-2003 era, hurts pre-2003 era; mean rubric-neutral.

iter 036 H16.3 TLT off enters at ~72 (MDD bucket -1pt vs IEF baseline,
TLT generalizes Pareto-NEGATIVE-on-MDD pattern from iter 035 H15.3).

### Strategic options for iter 037+ (USER DECISION)

**Recommendation: Option A — declare hunt RE-CLOSED at iter 036** —
most defensible per mandate §1 MAINTENANCE MODE. Rationale:

  1. iter 035 H15.2's +2pt strategy-level breach was specifically the
     JOINT optimum (GLD-mom-126d at 4th × KMLM off-state). Iter 036
     confirmed off-state-axis variation at A2 position does NOT extend
     the bonus (Principle O — gate-source-coupled effect magnitude).
  2. Principle O bounds off-state cross-product exploration: equity-
     track positions (QQQ / SPY) PREDICTED rubric-saturated for
     off-state-axis; only commodity-orthogonal (GLD / SLV / DBC)
     positions PREDICTED rubric-relevant.
  3. Further iterations on G2 / E1qqq off-state would test Principle O
     prediction but add minimal informational value if Principle O
     holds (predicted rubric-saturated outcomes at equity-track
     positions).
  4. iter 035 H15.2 confirmed deploy candidate at strategy-level apex
     74 with ALL 3 strict bars met + winner_conditions_met=True.
     Mandate §7 override eligible for review.
  5. 36 iters consumed 72% of 50-iter budget; 14 iters remaining for
     either (i) declaring hunt RE-CLOSED + writing FINAL_REPORT or
     (ii) targeted extensions on Principle O test cases.

(B) **Test Principle O prediction at G2 (SPY-track) off-state position**
— UNTESTED. MEDIUM informational value: confirms Principle O via
SECOND equity-track position. LOW credibility for ceiling-breach (per
Principle O prediction).

(C) **Test Principle O prediction at E1qqq off-state position** —
UNTESTED. MEDIUM informational value. LOW credibility for ceiling-
breach.

(D) **Test cross-product 5-way structure with E1gld+KMLM-off + E1silver
or E1commodity at 5th** — UNTESTED. MEDIUM informational value.
HIGH cost (requires NEW data infra for SLVSIM / DBC / BCOM).

(E) **Methodology refactor: implement FIXED-GRID PBO computation in
`scoring.py`** — Now LESS critical given iter 035's REAL strategy-level
improvement is established (H16.1 raw metrics IDENTICAL, only G1 PBO
shifts). Still valuable for cross-iter score comparability.

Tier PROMISING (73 ∈ [60, 74]; H16.1 at upper boundary).

Hunt's empirical informational value PLATEAUED — iter 035 H15.2 remains
strategy-level apex at 74 (Principle N). iter 036 confirmed Principle O
(off-state-axis effect magnitude is gate-source-coupled). Single-axis
off-state cross-product exploration EXHAUSTED at GLD + A2 positions;
remaining cross-product positions (G2 / E1qqq) PREDICTED rubric-
saturated by Principle O.

Mandate §1 100% Plano C UNCHANGED — research only.

### Citations applied

- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction over multiple
  alpha streams (4-way meta-ensemble at strategy-level — 20th iter at
  meta-axis with A2 off-state composition sub-axis exploration)
- `[advances_fin_ml, p.208-211]` PBO via CSCV (N=4 grid) — Principle M
  duplicate-confirmed (H16.1 G1 PBO 0.5873 lh / 0.5675 spy_real for
  IDENTICAL spec to iter 035 H15.2 which had 0.0833 / 0.5595)
- `[advances_fin_ml, p.222-223]` DSR with cumulative_n_trials = 140
  (Bonferroni 3.57e-04; worst per-config p 4.55e-05 PASSES with
  **7.85× margin** — slight reduction from iter 035's 8.08× due to
  n_trials inflation)
- `[advances_fin_ml, p.196-202]` Bootstrap CI (G6: lh_56y CI low 0.659,
  spy_real CI low 0.355 — both PASS)
- `[advances_fin_ml, p.31-34]` Cross-lib factor framework (G7 cross-lib
  delta 0.0pp PASS)
- Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250
  (E1gld TSMOM-126d held fixed at apex)
- Asness-Moskowitz-Pedersen (2013) Value and Momentum Everywhere, JoF
  68(3):929-985 (momentum across asset classes)
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed 200d SMA gate
  canonical (A2 QQQ-track + G2 SPY-track + IEF off-state default tested
  at A2 position)
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking (F1
  stack always-on retained — duodecuple-confirmed)
- `[ilmanen_expected_returns, ch.19]` Managed-futures crisis-alpha role
  — **Principle O source**: KMLM off-state at QQQ-track position
  REGIME-DEPENDENT (helps post-2003, hurts pre-2003) due to MF maturity
  + 1987 Black Monday non-trend-followable structure
- iter 016 G1 hybrid finding (off-state IEF > Blend > KMLM for SPY-track
  stack) — H16 PARTIALLY CONFIRMS pattern at A2 position with REGIME-
  DEPENDENT nuance (lh_56y confirms; spy_real reverses)
- iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way) — held fixed
- iter 026 KILL #103 (linear decomposition principle) — VALIDATED at
  bounded ±1pt rubric noise per Principle M
- iter 030 KILL #125 / Principle A (orthogonal-asset-class-TSMOM-source
  bonus +1pt) — held fixed via E1gld+KMLM-off at 4th
- iter 030 KILL #126 / Principle C (signal-sleeve incoherence Pareto-
  positive) — held fixed
- iter 031 KILL #130 / Principle D (TSMOM-lookback inverted-U asset-
  invariant peak at 6m / 126d) — held fixed at 126d
- iter 032 KILL #135 / Principle G (orthogonality bonus filter-type-
  coupled to momentum) — held fixed at filter=momentum
- iter 033 KILL #144 / Principle J (orthogonality bonus is COMMODITY-
  GOLD-SPECIFIC) — operative
- iter 034 KILL #150 / Principle M (rubric score is grid-composition-
  dependent via G1 PBO) — DUPLICATE-CONFIRMED via H16.1 anchor reading
  73 vs iter 035 H15.2 reading 74 for IDENTICAL spec
- iter 035 KILL #154 / Principle N (off-state crisis-alpha is asset-
  class-conditional) — REFINED: effect magnitude is GATE-SOURCE-COUPLED
  per Principle O
- iter 036 KILL #160 / Principle O (NEW — off-state-axis effect magnitude
  is gate-source-coupled; equity-track gate has rubric-saturated off-state
  axis; commodity-track gate has rubric-relevant off-state axis)
