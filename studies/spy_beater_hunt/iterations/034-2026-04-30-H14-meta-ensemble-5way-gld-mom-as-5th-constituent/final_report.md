# spy_beater_hunt iter 034 — Final Report — `H14-meta-ensemble-5way-gld-mom-as-5th-constituent`

**Gross tier**: **PROMISING** — `gross_score=73/100`, `gross_winner_met=True`

**Net tier**: **PROMISING** — `net_score=67/100`, `net_winner_met=True`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 16.59%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 33.77%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 14.46%)
- MDD bar: PASS (mean = 35.28%)
- Gates bar (same as gross): PASS

**Primary citation**: [advances_fin_ml, ch.16, p.241-256] portfolio construction over multiple alpha streams (5-way meta-ensemble at strategy-level, 18th iter at meta-axis, NEW interaction sub-axis 5-way × GOLD) + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking (F1 stack always-on retained at 3rd constituent — nonuple-confirmed uniquely-Pareto-optimal per iter 033) + Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 (E1 TSMOM-126d gate-source on QQQ + GLD stacked at 4th + 5th positions) + Asness-Moskowitz-Pedersen (2013) Value and Momentum Everywhere, JoF 68(3):929-985 (momentum across asset classes — equity-momentum + commodity-gold-momentum stacked) + [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate (A2 + G2 baseline retained) + [ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM in A2/G2/E1 ON-state) + Bridgewater All-Weather (Dalio 1996) F1 stack ON-state + [systematic_trading, ch.10] Carver vol-targeting canonical (C1 in H14.3 only) + iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way) — extended to 5-way × GOLD here + iter 026 KILL #103 (linear decomposition principle) — UPPER-BOUND test + iter 027 KILL #107 (5-way base tax confirmed at C1 substitution) — challenged with GLD as 5th + iter 030 KILL #125 (Principle A — orthogonal-asset-class-TSMOM-source bonus +1pt) — revised to Principle J (GOLD-SPECIFIC) per iter 033 KILL #144 + iter 031 KILL #130 (Principle D — TSMOM-lookback inverted-U asset-invariant peak at 6m / 126d) — held fixed at 126d + iter 032 KILL #135 (Principle G — orthogonality bonus filter-type-coupled to momentum) — held fixed at filter=momentum + iter 033 KILL #144 (Principle J — orthogonality bonus is COMMODITY-GOLD-SPECIFIC) — operative for GLD-mom-126d 5th constituent + [advances_fin_ml, p.222-223] DSR cumulative_n_trials = 132 (Bonferroni 3.79e-04) + [advances_fin_ml, p.208-211] PBO grid-level N=4 stability

---

## Selected config: `h14_meta_4way_25a2_25g2_25f1_25e1gld_mom126`

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
          "IEFSIM": 1.0
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
| **lh_56y** | 1.041 | 17.03% | 33.77% | 0.918 | 14.85% | 35.28% | 2.18 | 6/7 |
| **spy_real** | 1.037 | 16.14% | 33.77% | 0.912 | 14.07% | 35.28% | 2.07 | 6/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — annual_realize, 38 year-end settlements, total DARF $305,259 (terminal $9,447), drag 2.18pp
- `spy_real` — annual_realize, 23 year-end settlements, total DARF $27,838 (terminal $75), drag 2.07pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| h14_meta_5way_20a2_20g2_20f1_20e1qqq_20e1gld_mom126 | 0.994 | 0.988 |
| h14_meta_5way_20a2_20g2_20f1_15e1qqq_25e1gld_mom126 | 1.006 | 0.996 |
| h14_meta_5way_20a2_20g2_20f1_20c1_20e1gld_mom126 | 1.006 | 0.997 |
| h14_meta_4way_25a2_25g2_25f1_25e1gld_mom126 | 1.041 | 1.037 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 23 | 30 | mean = 16.59%, bar = 11.21% |
| 2. MDD vs SPY | 13 | 20 | mean = 33.77%, bar = 55.17% |
| 3. Gates | 13 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 6}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 6.55e-05, n_trials = 132 |
| 5. Sharpe | 4 | 10 | mean = 1.039 |
| 6. Robustness | 10 | 10 | input_bonus = 0 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark

| window | pass-rate (avg across datasets) | worst MDD across datasets |
|---:|---:|---:|
| 5y | 83.3% | 33.77% |
| 10y | 100.0% | 33.77% |
| 15y | 100.0% | 33.77% |
| 20y | 100.0% | 33.77% |

Legacy 5y rolling-Sharpe (anchor `lh_56y`): pct_positive = 100.00%, n_windows = 34

## INCOMPLETE flags

- **Selected H14.4 4-way GLD anchor**: per-dataset Sharpe 1.041/1.037, CAGR
  17.03%/16.14%, MDD 33.77%/33.77% IDENTICAL across iter 030/031/032/033/034
  (5 independent measurements, 4-decimal-precision reproducibility). **The
  STRATEGY is unchanged — only the rubric environment changed**.
- **CRITICAL — score 73 vs iter 030/031/032/033's 72 is a G1 PBO grid-
  composition artifact, NOT a real ceiling-breach.** spy_real G1 PBO sequence
  for the EXACT SAME H14.4 / iter 030 H10.4 strategy across 5 iters: iter
  030 = 0.5159 (FAIL), iter 031 = 0.8214 (FAIL), iter 032 = 0.7421 (FAIL),
  iter 033 = 0.6905 (FAIL), iter 034 = **0.1071 (PASS)**. The shift is
  attributable entirely to grid-composition (different sibling configs
  changing the relative-rank ordering across CV folds), NOT to the
  strategy's intrinsic edge.
- **5-way structural impact (H14.1/H14.2/H14.3 estimated)**: Sharpe 0.991-
  1.001 (all < 1.039 anchor), CAGR 16.12-17.06%, MDD 34.19-35.13%. Estimated
  scores 70-71 (Sharpe-bucket cross at 1.0 + MDD-bucket at 12 instead of 13).
  **The 5-way configs themselves did NOT break ceiling 72** — they
  Pareto-co-tied at ~71 with iter 026 H6.1 baseline.
- **DSR Bonferroni at n_trials=132**: threshold 0.05/132 = 3.79e-04. Worst
  per-config DSR p was 6.55e-05 on spy_real (PASSES strict <0.05; PASSES
  Bonferroni 3.79e-04 with **5.79× margin** — slight reduction from iter
  033's 6.0× margin due to n_trials inflation 128→132).
- **No new infra**: reuses 'blend' + 'lrs' (sma + momentum filters) +
  'static' + 'vol_target' (H14.3 only) spec types from iter 010/014/015/
  018-033. **771 tests baseline preserved**.
- **Tax classification**: meta-blend with E1gld (lrs+momentum at 4th
  constituent for selected H14.4) → annual_realize. Drag observed 2.18pp
  lh_56y / 2.07pp spy_real, mean 2.13pp — IDENTICAL to iter 030/031/032/
  033 because selected config replicates iter 030 H10.4 exactly.

## Lesson

### KILLs disparados (pre-committed iter-034 #145-#150)

- **KILL #145 NOT FIRED — META-AXIS CEILING 72 NOT confirmed**:
  max H14 = 73 > 72. 5-way × GOLD axis exposed an apparent +1pt breach.
  However, see KILL #146 and Principle M below — this breach is a rubric
  grid-composition artifact NOT a strategy-intrinsic finding.

- **KILL #146 FIRED — STRONG-FORM FALSIFICATION (apparent ceiling-breach
  to 73)**:
  max H14 = 73, > 72 strict. Score 73 > prior ceiling 72. **CRITICAL CAVEAT**:
  the breach is in H14.4 4-way ANCHOR (replicates iter 030 H10.4 EXACTLY at
  per-dataset Sharpe 1.041/1.037, CAGR 17.03%/16.14%, MDD 33.77%/33.77% — 5
  independent measurements identical to 4 decimal places). The +1pt is
  ENTIRELY attributable to G1 PBO grid-composition (spy_real PBO 0.69 FAIL
  iter 033 → 0.11 PASS iter 034 for the SAME strategy). Linear decomposition
  principle is NOT falsified at the strategy level; only the rubric's
  measurement environment shifted. **TREAT THIS BREACH AS METHODOLOGICAL
  ARTIFACT, NOT ARCHITECTURAL BREAKTHROUGH**.

- **KILL #147 NOT FIRED — 5-WAY BASE TAX CONFIRMED FOR GLD-MOM**:
  H14.1 (5-way 20/20/20/20/20 with E1qqq+E1gld) estimated score ~71 (Sharpe
  0.991 < 1.0 bucket cross + MDD 34.60% in 12-pt bucket + Gates 13 same
  env). H14.1 < 72 → 5-way base tax (iter 027 KILL #107) DOMINATES even with
  GLD-mom Principle A bonus. The +1pt GLD bonus does NOT overcome the
  effective penalty of the 5-way structural change (Sharpe-bucket cross +
  MDD-axis dilution). NEW EMPIRICAL PRINCIPLE: Principle A bonus is
  CONSTITUENT-COUNT-COUPLED — it survives at 4-way structure (iter 030
  H10.4) but is consumed by 5-way base tax.

- **KILL #148 NOT FIRED — GLD DOSE-RESPONSE AT 5-WAY: BINARY NOT ADDITIVE**:
  H14.2 (GLD at 25%, mean Sharpe 1.001) vs H14.1 (GLD at 20%, mean Sharpe
  0.991) Δ = +0.010 Sharpe; estimated score Δ ≤ 1pt (likely 0pt). The
  dose-response from 20% → 25% GLD weight at 5-way is BELOW the
  rubric-resolution threshold. Consistent with iter 030 H10.3 (20% GLD at
  4-way, score 72) and H10.4 (25% GLD at 4-way, score 72) tying — the
  Principle A bonus is BINARY (presence/absence), NOT dose-additive.

- **KILL #149 NOT FIRED — VOL-TARGET-AT-4TH PARETO-NEUTRAL vs E1qqq-AT-4TH**:
  H14.3 (C1 vol-target@4th + GLD@5th, mean Sharpe 1.001) vs H14.1 (E1qqq@4th
  + GLD@5th, mean Sharpe 0.991) Δ = +0.010 Sharpe; estimated score Δ ≤ 1pt.
  C1 vol-target at 4th does NOT beat E1qqq-mom at 4th by ≥ 1pt when paired
  with GLD-mom-126d at 5th. Reconfirms iter 027 KILL #109 NOT FIRED — gate-
  mechanism diversity (TSMOM-on-QQQ vs realized-vol-state) is rubric-neutral
  at meta-axis when Principle A bonus is held constant via GLD@5th.

- **KILL #150 SUB-CLAUSE FIRED — REPRODUCIBILITY-ISSUE FLAG TRIGGERED**:
  H14.4 (4-way GLD anchor) per-dataset Sharpe IDENTICAL to iter 030 H10.4
  (1.041/1.037 to 3 decimal places PASSES original-confirmation clause), but
  selected score = 73 ≠ 72 (deviation +1pt > 0.5pt threshold) FIRES the
  reproducibility-issue sub-clause. This confirms cross-iter score
  comparisons are GRID-COMPOSITION-DEPENDENT (via G1 PBO).

### NEW EMPIRICAL PRINCIPLE M — RUBRIC SCORE IS GRID-COMPOSITION-DEPENDENT

**Principle M — Cross-iter scoring is CONFOUNDED by grid-composition via G1
PBO sensitivity** (KILL #150 SUB-CLAUSE FIRED): Per-config raw metrics
(Sharpe / CAGR / MDD / DSR) are reproducible across iters to 4 decimal
places when the strategy spec is identical. However, the gate count via G1
PBO (Combinatorially Symmetric CV via [advances_fin_ml, p.208-211]) computes
an iter-level statistic over the entire CV grid of sibling configs in the
iter. When sibling configs change (iter 030 anchor + 3 axis variants vs
iter 034 5-way variants), the relative-rank ordering across CV folds shifts,
producing different PBO values for the SAME strategy.

Empirical evidence: H14.4 = iter 030 H10.4 = iter 031 H11.2 = iter 032
H12.1 = iter 033 H13.2 (5 independent measurements, identical specs,
identical per-dataset metrics to 4 decimals, identical Sharpe to 3
decimals). Yet spy_real G1 PBO took values {0.5159, 0.8214, 0.7421, 0.6905,
0.1071} across the 5 iters → **range Δ = 0.71** for the same strategy. The
last value (iter 034) flipped G1 from FAIL to PASS, lifting Gates points
12→13 and total score 72→73.

**Mechanism**: PBO is grid-level statistic; sibling configs' performance
ranks across CV folds determine the strategy's apparent "overfitness". 5-way
sibling configs (H14.1/H14.2/H14.3) presumably underperformed H14.4 4-way
anchor consistently across folds, giving anchor a "robust top-rank"
signature → low PBO. Earlier iter siblings (4-way axis variants) had
Pareto-frontier-adjacent metrics (different scores 67-72) producing
inconsistent rank orderings → high PBO.

**Implications for hunt methodology**:
1. **Cross-iter score comparisons are NOISY** ±1pt due to grid-composition
   even at IDENTICAL strategy specs. The "ceiling 72" iter 030-033
   quadruple-replication may itself have been a LOW-score artifact (0.69
   PBO FAILing for selected anchor) rather than the strategy's true
   maximum-achievable rubric score.
2. **The +1pt iter 030 breach over iter 026 H6.1 (71 → 72) may have been
   similar grid artifact** at the time, not a true gate-source-distinctness
   bonus. Principle A's empirical foundation is weakened.
3. **Principle J / Principle G / Principle H / Principle I / Principle K /
   Principle L are weakened** — all these principles relied on per-iter
   score comparisons within a single grid; cross-iter score deltas are
   confounded by Principle M.
4. **Adversarial methodological recommendation**: rubric should be
   strategy-level NOT grid-level for G1 PBO. Compute PBO over a FIXED
   reference grid (e.g., the iter 030 grid) for cross-iter comparability.
   This requires a specification refactor (mandate §7 review case).

### Score breakdown vs iter-030 H10.4 prior closest-to-winner (72→73, +1pt — METHODOLOGICAL ARTIFACT)

| criterion | iter 030 H10.4 | iter 031-033 (REPLICATION) | iter 034 H14.4 | Δ vs 030 |
|---|---:|---:|---:|---:|
| 1. CAGR | 23 | 23 (4× IDENTICAL) | 23 | 0 (mean 16.59% IDENTICAL across 5 iters) |
| 2. MDD | 13 | 13 (4× IDENTICAL) | 13 | 0 (mean 33.77% IDENTICAL across 5 iters) |
| 3. Gates | 12 | 12 (4× IDENTICAL) | **13** | **+1 (spy_real PBO grid artifact)** |
| 4. DSR | 10 | 10 | 10 | 0 (worst p 6.55e-05 IDENTICAL across 5 iters) |
| 5. Sharpe | 4 | 4 (4× IDENTICAL) | 4 | 0 (mean 1.039 IDENTICAL) |
| 6. Robustness | 10 | 10 | 10 | — |
| 7. Bonus | 0 | 0 | 0 | — |
| **Total** | **72** | **72 (4× QUADRUPLE-REPLICATION)** | **73** | **+1pt — PBO ARTIFACT** |

Strategy IDENTICAL across 5 iters; only G1 PBO grid-statistic differs.

### Per-config 5-way structural spread (H14.1/H14.2/H14.3 estimated)

| Config | Mean Sharpe | Mean CAGR | Mean MDD | Est. score | Δ vs H14.4 anchor |
|---|---:|---:|---:|---:|---:|
| H14.1 (5-way E1qqq+E1gld 20/20) | 0.991 | 16.93% | 34.60% | ~71 | -2pt (Sharpe < 1.0 + MDD bucket-down) |
| H14.2 (5-way GLD-heavy 15/25) | 1.001 | 17.06% | 35.13% | ~71-72 | -1 to -2pt (Sharpe ~1.0 borderline, MDD bucket-down) |
| H14.3 (5-way C1+E1gld 20/20) | 1.001 | 16.12% | 34.19% | ~71-72 | -1 to -2pt (Sharpe ~1.0, MDD bucket-down) |
| **H14.4 (4-way GLD anchor)** | **1.039** | **16.59%** | **33.77%** | **73 (selected)** | **0 (anchor) — APEX via PBO ARTIFACT** |

5-way configs themselves do NOT break ceiling 72 on intrinsic merit; they
Pareto-co-tie at ~71 with iter 026 H6.1 baseline (4-way E1qqq, score 71).
The +1pt iter 034 breach is exclusively in the 4-way GLD anchor via PBO
grid-shift.

### Closest-to-winner UPDATED — iter 034 H14.4 NOMINAL APEX at score 73

**iter 034 H14.4 (h14_meta_4way_25a2_25g2_25f1_25e1gld_mom126) becomes
NOMINAL closest-to-winner at score 73**, replacing iter 030 H10.4 at 72.

**Caveat**: H14.4 IS iter 030 H10.4 (same blend spec; same per-dataset
metrics; same DSR; same Sharpe; same CAGR; same MDD; same Robustness).
The +1pt is a measurement-environment artifact (PBO grid-composition).
Treat the apex as **iter 030 H10.4 at score 72-73 (rubric noise band)**
rather than a stand-alone iter 034 finding. For deploy-readiness or
mandate §7 override evaluation, the strategy is unchanged from iter 030.

### Direction implications

- **15-AXIS ARCHITECTURAL TAXONOMY UNCHANGED at strategy level**; meta-axis
  ceiling 72 confirmed at strategy level across 13 sequential meta-axis iters
  (018→034). The iter 034 nominal +1pt breach is rubric-environment-only.

- **Principle M (NEW)**: rubric score is grid-composition-dependent at the
  ±1pt level via G1 PBO. Cross-iter score comparisons require fixed-grid
  PBO computation for rigorous comparability.

- **Principle A (iter 030 KILL #125) FOUNDATION WEAKENED**: the +1pt iter
  030 breach over iter 026 H6.1 (71→72) may have been similar grid artifact
  rather than gate-source-distinctness bonus. Empirical evidence:
  iter 030 H10.4 spy_real PBO was 0.5159 (borderline FAIL); iter 026 H6.1's
  PBO would need separate verification. **Future rigorous test would
  recompute both anchors on a FIXED reference grid**.

- **5-way × GOLD interaction**: H14.1/H14.2/H14.3 5-way configs Pareto-co-
  tied at ~71 with iter 026 H6.1 4-way E1qqq baseline. Linear decomposition
  principle (iter 026 KILL #103) holds for strategy-level scoring (5-way
  base tax -1 + GLD bonus +1 ≈ 0 net relative to 4-way E1qqq). Confirms 5-way
  base tax + Principle A bonus are linearly compensating at meta-axis.

- **F1 stack always-on uniquely-Pareto-optimal at 3rd position — 10TH
  IMPLICIT CONFIRMATION** (iter 034): all 4 H14 configs retain F1 at 3rd
  position; max H14 score 73 (nominal) achieved with F1 retained. F1 status
  now decuple-confirmed (iter 025/026/027 direct + iter 028/029/030/031/032/
  033/034 implicit retention).

- **MANDATE §7 RUBRIC-REVISION REVIEW CASE STRENGTHENED to 18th iter +
  EXPANDED to G1 PBO methodology question**: prior 17 iters argued for
  rubric weighting revision under user-utility (Sharpe/MDD-weighted vs
  CAGR-anchored). Iter 034 adds METHODOLOGICAL CASE: G1 PBO grid-composition
  sensitivity introduces ±1pt cross-iter scoring noise that confounds
  closest-to-winner ranking. Mandate §1 100% Plano C UNCHANGED — research
  only. F1+SPLIT remains deploy fallback.

### Strategic options for iter 035+ (USER DECISION REQUIRED per mandate §1 + §7)

**Recommendation: Option A** (declare hunt RE-CLOSED at iter 034 — most
defensible per mandate §1 MAINTENANCE MODE; iter 030 H10.4 strategy spec
remains apex; iter 034 confirmed strategy-level ceiling 72 even at 5-way
structure with GLD-mom-126d as 5th constituent; iter 030's +1pt breach over
iter 026 may itself have been G1 PBO grid artifact (Principle M weakens
prior architectural claims); 5-way base tax + Principle A bonus linearly
compensate at strategy level; F1+SPLIT confirmed deploy fallback; 34 iters
preserved 68% of budget). Recommendation EVEN STRONGER than iter 033 due
to: (a) Principle M reveals all prior cross-iter score deltas have ±1pt
PBO grid-noise floor; (b) the 5-way × GOLD interaction sub-axis maps to
iter 026 H6.1 baseline at strategy level, NOT to a new architectural
breakthrough; (c) further single-axis exploration is structurally
exhausted at meta-axis 4-way × GLD-mom-126d JOINT optimum.

(B) Methodology refactor: implement FIXED-GRID PBO computation in
`scoring.py` to enable rigorous cross-iter score comparability — high
infrastructure cost (modifies all prior iter scores), unclear benefit since
strategy is unchanged from iter 030.

(C) test SILVER (SLVSIM if available) or BROAD-COMMODITY (DBC/BCOM) signal
at meta-ensemble 4-way — MEDIUM credibility per Principle J prediction
(inflation-hedge / dollar-cycle assets should retain bonus); HIGH cost if
not in synth cache.

(D) test FX (DXY-momentum, USDJPY-momentum) signal — UNTESTED, MEDIUM
credibility per Principle J.

(E) NEW DATA INFRA for SLV/DBC/BCOM/DXY — HIGH cost, MEDIUM-HIGH credibility.

Tier PROMISING (73 ∈ [60, 74]). Hunt's empirical informational value
PLATEAUED at strategy level — iter 030 H10.4 remains the best-scoring
strategy spec; iter 031/032/033/034 cumulatively confirmed ceiling at
strategy level via QUINTUPLE replication; iter 034's nominal +1pt breach is
methodological artifact (Principle M) NOT a real architectural finding.
**Mandate §1 100% Plano C UNCHANGED — research only**.

### Citations applied

- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction over multiple
  alpha streams (5-way meta-ensemble at strategy-level — 18th iter at
  meta-axis with 5-way × GOLD interaction sub-axis exploration)
- `[advances_fin_ml, p.208-211]` PBO via CSCV (N=4 grid) — **Principle M
  source**: PBO is grid-level not strategy-level statistic
- `[advances_fin_ml, p.222-223]` DSR with cumulative_n_trials = 132
  (Bonferroni 3.79e-04; worst per-config p 6.55e-05 PASSES with 5.79×
  margin — slight reduction from iter 033's 6.0×)
- `[advances_fin_ml, p.196-202]` Bootstrap CI
- `[advances_fin_ml, p.31-34]` Cross-lib factor framework
- Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250
  (E1qqq + E1gld TSMOM-126d gate-sources stacked at 4th + 5th positions)
- Asness-Moskowitz-Pedersen (2013) Value and Momentum Everywhere, JoF
  68(3):929-985 (momentum across asset classes)
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed 200d SMA gate
  (A2 + G2 baseline retained)
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking
  (F1 stack always-on retained — decuple-confirmed uniquely-Pareto-optimal)
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha (KMLM in
  A2/G2/E1 ON-state)
- `[systematic_trading, ch.10]` Carver vol-targeting canonical (C1 in
  H14.3 only)
- Bridgewater All-Weather (Dalio 1996) F1 stack ON-state retained
- iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way) — **possibly
  PBO grid artifact per Principle M**
- iter 026 KILL #103 (linear decomposition principle) — VALIDATED at
  strategy level (5-way base tax + GLD bonus linearly compensate to ~71)
- iter 027 KILL #107 (5-way base tax) — confirmed (5-way configs at ~71
  even with GLD bonus)
- iter 030 KILL #125 (Principle A — orthogonal-asset-class-TSMOM-source
  bonus +1pt) — **REVISED again per Principle M: empirical foundation
  ±1pt PBO grid-noise; needs FIXED-GRID re-test**
- iter 031 KILL #130 (Principle D — TSMOM-lookback inverted-U asset-
  invariant peak at 6m / 126d) — held fixed at 126d
- iter 032 KILL #135 (Principle G — orthogonality bonus filter-type-
  coupled to momentum) — held fixed at filter=momentum
- iter 033 KILL #144 (Principle J — orthogonality bonus is COMMODITY-
  GOLD-SPECIFIC) — empirical foundation ±1pt PBO grid-noise; needs
  FIXED-GRID re-test
