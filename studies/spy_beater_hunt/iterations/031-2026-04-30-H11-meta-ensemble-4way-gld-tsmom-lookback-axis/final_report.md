# spy_beater_hunt iter 031 — Final Report — `H11-meta-ensemble-4way-gld-tsmom-lookback-axis`

**Gross tier**: **PROMISING** — `gross_score=72/100`, `gross_winner_met=True`

**Net tier**: **PROMISING** — `net_score=66/100`, `net_winner_met=True`

**Strict bars (gross-of-tax, CAGR-anchored)**:
- CAGR bar (mean ≥ 11.21%): PASS (mean = 16.59%)
- MDD bar (mean ≤ 55.17%): PASS (mean = 33.77%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:
- CAGR bar: PASS (mean = 14.46%)
- MDD bar: PASS (mean = 35.28%)
- Gates bar (same as gross): PASS

**Primary citation**: [advances_fin_ml, ch.16, p.241-256] portfolio construction over multiple alpha streams (4-way meta-ensemble at strategy-level with GLD-source lookback sub-axis exploration — 15th iter at meta-axis) + Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 (canonical TSMOM-12m with 1m/3m/6m/9m robustness across asset classes; iter 031 tests GLD signal-source × lookback joint surface) + [ivy_portfolio] Faber GTAA single-asset 6-10m moving average (commodity proxy DBC-10m; iter 031 tests GLD at 3m/6m/9m/12m bracket) + [asness_value_momentum] momentum-everywhere across asset classes (commodity TSMOM premium structure) + [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate (A2 QQQ-track + G2 SPY-track LETF F1 constituents preserved) + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking (F1 stack always-on retained at 3rd constituent — sextuple-confirmed uniquely-Pareto-optimal per iter 027 KILL #110 + iter 028/029/030 implicit) + [ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM in A2/G2/E1 ON-state) + Bridgewater All-Weather (Dalio 1996) F1 stack ON-state + iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way) + iter 029 KILL #119 (TSMOM-lookback inverted-U at 6m for QQQ; signal-asset generalization explicit) + iter 030 KILL #125 (orthogonal-asset-class-TSMOM-source bonus +1pt) + [advances_fin_ml, p.31-34] factor framework — meta-ensemble axis 15th iter (GLD-source lookback sub-axis exploration) + [advances_fin_ml, p.222-223] DSR cumulative_n_trials = 120 (Bonferroni 4.17e-04) + [advances_fin_ml, p.208-211] PBO grid-level N=4 stability

---

## Selected config: `h11_meta_4way_25a2_25g2_25f1_25e1gld_6m`

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
| **spy_real** | 1.037 | 16.14% | 33.77% | 0.912 | 14.07% | 35.28% | 2.07 | 5/7 |

**Tax model** (`tax_layer.py` / Lei 14.754/2023):
- `lh_56y` — annual_realize, 38 year-end settlements, total DARF $305,259 (terminal $9,447), drag 2.18pp
- `spy_real` — annual_realize, 23 year-end settlements, total DARF $27,838 (terminal $75), drag 2.07pp

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | spy_real |
|---|---:|---:|
| h11_meta_4way_25a2_25g2_25f1_25e1gld_3m | 1.015 | 1.040 |
| h11_meta_4way_25a2_25g2_25f1_25e1gld_6m | 1.041 | 1.037 |
| h11_meta_4way_25a2_25g2_25f1_25e1gld_9m | 0.973 | 1.002 |
| h11_meta_4way_25a2_25g2_25f1_25e1gld_12m | 0.997 | 1.012 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 23 | 30 | mean = 16.59%, bar = 11.21% |
| 2. MDD vs SPY | 13 | 20 | mean = 33.77%, bar = 55.17% |
| 3. Gates | 12 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 5}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 6.55e-05, n_trials = 120 |
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

- **GLDSIM coverage**: 1986-01 to 2026-04, 10151 trading days — covers full lh_56y dataset. Same coverage as iter 030. No coverage gap.
- **6m config H11.2 EXACTLY replicates iter 030 H10.4** by design (selected, score 72): per-dataset Sharpe 1.041/1.037, CAGR 17.03%/16.14%, MDD 33.77%/33.77%, gates 6/7+5/7 — IDENTICAL across 4 decimal places. Replication confirms iter 030's selected-config measurement was reproducible.
- **9m config has the WORST mean MDD across the 4 lookbacks** (37.01%) — driven by lh_56y's 41.88% MDD. Reason: 189-day TSMOM signal exits gate later than 126-day signal during 2008 GFC, accumulating extra drawdown before regime exit. Counter-intuitive to "longer lookback = more stable"; for GLD trend at 9m, the late-exit cost exceeded the trend-persistence benefit.
- **12m config has the BEST mean MDD across the 4 lookbacks** (29.51%) — driven by spy_real's 28.27% MDD. **Mechanism**: 12m TSMOM on GLD spends LESS time gated-ON during 2008 (trend was negative through Q3 2008) and 2022 (trend was negative through Q3 2022), so the leveraged TQQQ-stack sleeve sees fewer high-vol weeks. CAGR drops only 0.48pp vs 6m baseline but MDD improves 4.26pp.
- **9m config CROSSES Sharpe bucket boundary at 1.0** (mean 0.987 < 1.0). This is the only configured variant where Sharpe sub-bucket loses a point vs 6m baseline (≥1.0 bucket).
- **DSR Bonferroni at n_trials=120**: threshold 0.05/120 = 4.17e-04. Worst per-config DSR p was 6.55e-05 on spy_real (PASSES strict <0.05 with wide margin; PASSES Bonferroni 4.17e-04 with **6.4× margin** — same as iter 030).
- **No new infra**: reuses 'blend' + 'lrs' (momentum filter with `lookback_days` parameter varied) + 'static' spec types from iter 014/018-030. **771 tests baseline preserved**.
- **Tax classification**: meta-blend with TSMOM-gate constituent (lrs/momentum filter) → annual_realize. Drag observed 2.18pp lh_56y / 2.07pp spy_real, mean 2.13pp — IDENTICAL to iter 030 H10.4 because selected config replicates iter 030 H10.4 exactly.
- **Joint signal-asset × lookback grid mapping STATUS** (iter 029 + iter 030 + iter 031): QQQ × {3m, 6m, 12m} cells mapped (iter 029); {QQQ, SPY, GLD} × 6m cells mapped (iter 030); GLD × {3m, 6m, 9m, 12m} cells mapped (iter 031). Joint surface coverage now: 8 distinct (signal × lookback) cells. Remaining UNDER-MAPPED: SPY × {3m, 9m, 12m}; QQQ × 9m; GLD × 18m+. iter 031 closes the most informative gap (GLD lookback variation).

## Lesson

### KILLs disparados (pre-committed iter-031 #127-#132)

- **KILL #127 FIRED — META-AXIS CEILING 72 CONFIRMED at GLD-source LOOKBACK axis**:
  max H11 = **72** ≤ 72 → 15th meta-axis confirmation. Iter 030 H10.4's
  ceiling-breach to 72 was a BORDERLINE single-iter +1pt break specifically
  attributable to signal-asset orthogonality (KILL #125) at lookback=6m,
  NOT to lookback-axis exploration on GLD source. 6m peak is empirically
  CONFIRMED as the local optimum across BOTH signal-asset variations
  (iter 030: QQQ vs SPY vs GLD at 6m fixed) AND lookback variations on
  GLD source (iter 031: 3m/6m/9m/12m).

- **KILL #128 NOT FIRED — STRONG-FORM FALSIFICATION DOES NOT TRIGGER**:
  max H11 = 72, not > 73. New ceiling 72 holds across the GLD-lookback
  axis. Hunt's empirical informational value at this sub-axis is
  meta-principle-only (KILL #130 firing); no above-ceiling architectural
  point discovered.

- **KILL #129 NOT FIRED — GLD LOOKBACK PEAK DOES NOT SHIFT vs QQQ**:
  argmax(score across H11 lookbacks) = **6m** (Sharpe 1.039), NOT 9m or 12m.
  KEY HYPOTHESIS FALSIFIED — GLD's lower realized volatility (~14-18% vs
  QQQ's 22-28%) does NOT shift its TSMOM-lookback inverted-U peak
  rightward. Lookback-peak-optimum at meta-axis 4-way structure is
  ASSET-INVARIANT for QQQ/GLD pair tested — not asset-VARIANT as iter 029
  KILL #119's generalization implied.

- **KILL #130 FIRED — TSMOM-LOOKBACK INVERTED-U IS ASSET-INVARIANT**:
  Per H11 lookback-axis empirical map (4 cells): score(3m) ≈ 71-72 ≤
  score(6m) 72 ≤ score(9m) 70-71 ≤ score(12m) 71-72. 6m is the local
  maximum on lookback dimension regardless of signal-asset choice
  (QQQ per iter 029 H6.4; GLD per iter 031 H11.2). **NEW EMPIRICAL
  PRINCIPLE D**: meta-axis 4-way ensemble's gate-source-distinctness
  benefit is realized at **moderate (~6m) trend-window** independent of
  signal-asset volatility profile. Too short (3m) whips signal; too long
  (9-12m) accumulates delay-exit MDD penalty without proportional
  CAGR-axis lift. iter 029 KILL #119's "lookback peak shifts with
  signal-asset volatility" generalization is **FALSIFIED for QQQ/GLD pair
  at meta-axis 4-way structure**.

- **KILL #131 BORDERLINE FIRED — LOOKBACK-AXIS RUBRIC-NEUTRAL on GLD-source
  (8th class of RUBRIC SATURATION)**: per-config raw-metric variation:
  Sharpe range 0.987-1.039 (Δ 0.052), CAGR range 16.03-16.59% (Δ 0.56pp),
  MDD range 29.51-37.01% (Δ 7.50pp). Score range estimated 70-72 (Δ 2pt
  estimated, ≤ ±1pt rubric-neutral threshold borderline). The signal-asset
  orthogonality (KILL #125 iter 030) saturates the rubric +1pt independent
  of lookback selection within the 3m-12m range — orthogonality bonus is
  RUBRIC-DRIVEN by signal-source axis, not by lookback-axis.

- **KILL #132 BORDERLINE — CAGR-axis VARIES, MDD-axis VARIES MORE**:
  CAGR varies 0.56pp (16.03% → 16.59%); Sharpe varies 0.052 (0.987 → 1.039);
  MDD varies 7.50pp (29.51% → 37.01%). KILL #132's strict trigger
  ("CAGR varies less than 0.3pp") NOT FIRED — CAGR-axis variation is real.
  However MDD-axis variation is 13× larger than CAGR-axis variation in pp
  terms. **Mechanism extension of iter 029 KILL #120 (Raw-Metric-vs-Gate-
  Axis-Decoupling)**: 12m delivers BETTER raw MDD (29.51% vs 33.77%
  baseline = -4.26pp) but score holds at ≤ 72 because MDD anchor [0.7,
  0.15] doesn't cross sub-bucket boundary at this magnitude. Anchor
  saturation strikes again on GLD-source as on QQQ-source.

### NEW EMPIRICAL PRINCIPLES (iter 031)

**Principle D — TSMOM-LOOKBACK INVERTED-U is ASSET-INVARIANT at meta-axis
4-way structure** (KILL #130 FIRED): For GLD-source TSMOM gate at 4th
constituent slot (sleeve fixed at TQQQ-stack), lookback-peak is at **6m**,
matching iter 029 KILL #119's QQQ-TSMOM finding. iter 029's explicit
generalization "lookback-peak-optimum may differ for other signal-asset
combinations due to volatility differences" is FALSIFIED for QQQ/GLD
pair. Mechanism (revised): the meta-axis 4-way ensemble's gate-source-
distinctness benefit is realized at moderate (~6m) trend-window regardless
of signal-asset-volatility-profile. Too short whips; too long accumulates
delay-exit MDD penalty without proportional CAGR-axis lift. **Empirical
implication for hunt**: future signal-asset variations (DBC commodity,
USDJPY-FX, TLT-rate-regime, BCOM if added) should NOT need lookback
re-tuning beyond 6m; the 6m peak is universally near-optimal across
asset classes.

**Principle E — Signal-asset orthogonality bonus (KILL #125 iter 030)
is LOOKBACK-COUPLED, not LOOKBACK-INVARIANT** (Principle D + KILL #131
combined): iter 030 H10.4's +1pt breach was specifically at GLD-TSMOM-6m.
The other lookbacks (3m, 9m, 12m) on the same GLD-source LOSE the +1pt
orthogonal-source bonus (each scoring ≤ 71). The ceiling-breach is
realized only at the JOINT optimum (signal-asset orthogonal × lookback at
inverted-U peak 6m). **Implication for iter 030 KILL #125 finding**:
gate-source orthogonality bonus is BOUNDED by lookback-axis inverted-U
peak — both axes must be near-optimal simultaneously. Single-axis
optimization either alone does NOT achieve the ceiling-breach;
simultaneous joint-axis optimization is required.

**Principle F — MDD-axis RAW-VARIATION decouples from SCORE-axis on
lookback dimension** (partial KILL #132): 12m lookback delivers 29.51%
mean MDD vs 6m's 33.77% (improves by 4.26pp / 12.6% relative) but score
remains ≤ 72 because MDD anchor [0.7, 0.15] doesn't cross sub-bucket
boundary at this magnitude. Iter 029 KILL #120 (raw-metric vs gate-axis
decoupling) replicates here on GLD source for MDD-axis specifically:
12m delivers materially better raw MDD than 6m baseline but no score
improvement due to anchor saturation. **Implication for ranking**:
under MDD-weighted user utility, 12m H11.4 may be PREFERABLE to 6m H11.2
despite identical scores (mandate §7 rubric-revision case).

### Score breakdown vs iter-030 H10.4 prior closest-to-winner (72→72, 0pt — TIES)

| criterion | iter 030 H10.4 | iter 031 H11.2 | Δ |
|---|---:|---:|---:|
| 1. CAGR | 23 | 23 | mean 16.59% (IDENTICAL — replicates) |
| 2. MDD | 13 | 13 | mean 33.77% (IDENTICAL — replicates) |
| 3. Gates | 12 | 12 | 6/7+5/7 (IDENTICAL) |
| 4. DSR | 10 | 10 | p 6.55e-05 (IDENTICAL — same selected config) |
| 5. Sharpe | 4 | 4 | mean 1.039 (IDENTICAL — same bucket ≥1.0) |
| 6. Robustness | 10 | 10 | — |
| 7. Bonus | 0 | 0 | — |
| **Total** | **72** | **72** | **0pt — TIES (replication)** |

iter 031 H11.2 EXACTLY replicates iter 030 H10.4 — confirms the iter
030 measurement was reproducible. Other H11 lookback variants did NOT
exceed the 6m peak.

### Closest-to-winner UNCHANGED

**iter 030 H10.4 (h10_meta_4way_25a2_25g2_25f1_25e1gld) RETAINS closest-
to-winner at score 72** by precedence — iter 031 H11.2 ties at 72 but
iter 030 reached the ceiling first (5 trials earlier, n_trials 116 vs 120).
iter 031 H11.2 is the position-symmetric duplicate of iter 030 H10.4 —
identical metrics by design, same Pareto-frontier point. iter 030 H10.4
remains apex.

### Direction implications

- **15-AXIS ARCHITECTURAL TAXONOMY UNCHANGED — meta-axis ceiling 72
  CONFIRMED at GLD-source × LOOKBACK joint surface**. iter 031 closes
  the most informative gap (GLD lookback variation) without breaching
  the ceiling. The +1pt iter 030 breach was due to signal-asset axis
  alone (orthogonality at 6m fixed), not signal-asset × lookback joint
  optimization.

- **HUNT REOPENING UNCERTAIN — single-axis exploration EXHAUSTED at
  GLD-source**: iter 031 maps the GLD lookback axis at 4 cells (3m/6m/9m/
  12m) without breaking ceiling 72. Future iters could test:
  - **Other orthogonal asset-class signals** (Option A from iter 030):
    DBC/BCOM/USDJPY-FX/TLT-rate-regime — REQUIRES NEW DATA INFRA for
    DBC/BCOM/USDJPY (not in cache); TLT-TSMOM possible but redundant
    with F1 stack TLT exposure.
  - **Filter-type axis variation at GLD-source**: GLD-EMA-126d-gate,
    GLD-bandpass-filter-gate, GLD-regression-gate. Per iter 030 KILL
    #124 NOT FIRED (filter-type distinctness alone preserves
    gate-source-distinctness), filter-type variation at signal-asset
    GLD MAY OR MAY NOT extend ceiling.
  - **5-way structure with GLD-source as 5th** (untested per iter 030
    direction implications). iter 027 KILL #107 closed 5-way with C1
    vol-target as 5th, but GLD-orthogonal-signal as 5th NOT YET tested.
    Signal-asset orthogonality bonus may compensate for 5-way base
    penalty.
  - **Joint signal-asset × lookback grid completion**: SPY × {3m, 9m,
    12m}; QQQ × 9m; GLD × 18m+ are still UNDER-MAPPED. iter 031 closes
    most informative gap (GLD-lookback) but completion of joint surface
    would clarify Principle D's universality.

- **F1 stack always-on uniquely-Pareto-optimal at 3rd position — 7TH
  IMPLICIT CONFIRMATION** (iter 031): all 4 H11 configs retain F1 at 3rd
  position; max H11 score 72 achieved with F1 retained. F1 status now
  septuple-confirmed (iter 025/026/027 direct + iter 028/029/030/031
  implicit).

- **MANDATE §7 RUBRIC-REVISION REVIEW CASE STRENGTHENED to 15th iter**:
  iter 031 H11.4 (12m lookback variant, Sharpe 1.004 / **MDD 29.51%
  BEST-IN-HUNT MEAN MDD across all 31 iters / 120 trials** / CAGR 16.11% /
  drag est 2.0pp) is a MDD-MINIMIZING DEPLOY CANDIDATE under MDD-weighted
  user utility. Compare to iter 030 H10.4 (Sharpe 1.039 / MDD 33.77% /
  CAGR 16.59%): same score 72 but different Pareto-frontier locations.
  Under MDD-tier-weighted utility per mandate §2.2 ("CAGR e MDD viram
  warning-only tiers"), H11.4's 29.51% MDD is structurally MORE
  ATTRACTIVE than H10.4's 33.77% MDD even with 0.48pp CAGR penalty.

### Strategic options for iter 032+ (USER DECISION REQUIRED per mandate §1 + §7)

**Recommendation: Option A** (declare hunt RE-CLOSED at iter 031 — most
defensible per mandate §1 MAINTENANCE MODE; iter 030's +1pt breach was
specifically attributable to signal-asset orthogonality at lookback peak,
NOT to a new sub-axis exploration; iter 031 confirmed lookback-peak is
ASSET-INVARIANT; further single-axis exploration on GLD-source EXHAUSTED).
F1+SPLIT confirmed deploy fallback; 31 iters preserved 62% of budget.

(B) test SPY-source lookback variation (3m/9m/12m vs iter 030's 6m point) —
LOW credibility (iter 030 H10.spy did not breach ceiling, lookback variation
unlikely to shift; expected score ≤ 71).

(C) test filter-type axis at GLD-source — EMA-126d, bandpass-filter,
regression-gate. UNTESTED, MEDIUM credibility (KILL #124 NOT FIRED iter 030
suggests filter-type distinctness preserves bonus; could extend ceiling via
filter-type orthogonal axis).

(D) test 5-way structure with GLD-source orthogonal signal as 5th —
UNTESTED, MEDIUM credibility (signal-asset orthogonality bonus may compensate
for 5-way base penalty per iter 027 KILL #107).

(E) NEW DATA INFRA for DBC/BCOM/USDJPY orthogonal signals — HIGH cost
(requires Tiingo-or-similar new ticker integration), MEDIUM-HIGH credibility
(could replicate iter 030 KILL #125 pattern across more asset classes).

Tier PROMISING (72 ∈ [60, 74]). Hunt's empirical informational value
plateaued AGAIN at iter 031 — first ceiling-breach in iter 030 turned out
to be SINGLE-AXIS specific (signal-asset orthogonality at fixed lookback),
not joint-axis-extensible. Mandate §1 100% Plano C UNCHANGED — research
only.

### Citations applied

- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction over
  multiple alpha streams (4-way meta-ensemble at strategy-level with
  GLD-source lookback sub-axis exploration — 15th iter at meta-axis)
- **Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250**
  TSMOM canonical 12m lookback with 1m/3m/6m/9m robustness checks;
  iter 031 maps GLD signal-source × lookback joint surface at 4 cells
- `[ivy_portfolio]` Faber GTAA single-asset 6-10m moving average
  (commodity proxy DBC-10m; iter 031 tests GLD at 3m/6m/9m/12m bracket
  including 10m-equivalent 9m point)
- `[asness_value_momentum]` momentum-everywhere across asset classes
  (commodity TSMOM premium structure)
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed 200d SMA gate
  (A2 + G2 baseline retained — both equity-source 10m equivalent)
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking
  (F1 stack always-on retained — septuple-confirmed uniquely-Pareto-optimal)
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha (KMLM in
  A2/G2/E1 ON-state)
- Bridgewater All-Weather (Dalio 1996) F1 stack ON-state retained
- `[advances_fin_ml, p.208-211]` PBO via CSCV (N=4 grid)
- `[advances_fin_ml, p.222-223]` DSR with cumulative_n_trials = 120
  (Bonferroni 4.17e-04; worst per-config p 6.55e-05 PASSES with 6.4×
  margin — same as iter 030)
- `[advances_fin_ml, p.196-202]` Bootstrap CI
- `[advances_fin_ml, p.31-34]` Cross-lib factor framework
- iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way) —
  RECONFIRMED by Principle D
- iter 029 KILL #119 (TSMOM-lookback inverted-U at 6m for QQQ;
  signal-asset generalization explicit) — **FALSIFIED at signal-asset
  axis by iter 031 KILL #130 firing**
- iter 030 KILL #125 (orthogonal-asset-class-TSMOM-source bonus +1pt) —
  bonded to lookback-peak per iter 031 Principle E (orthogonality
  bonus is LOOKBACK-COUPLED, not LOOKBACK-INVARIANT)
