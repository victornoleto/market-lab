# spy_beater_hunt iter 033 — Final Report — `H13-meta-ensemble-4way-asset-class-orthogonality-generalization`

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

**Primary citation**: [advances_fin_ml, ch.16, p.241-256] portfolio construction over multiple alpha streams (4-way meta-ensemble, 17th iter at meta-axis with asset-class generalization sub-axis) + Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 (TSMOM premium across 58 instruments spanning equities/bonds/FX/commodities — iter 033 tests rate-signal at meta-ensemble 4-way) + Asness-Moskowitz-Pedersen (2013) Value and Momentum Everywhere, JoF 68(3):929-985 (momentum pervasive across asset classes — predicts rates-momentum-126d should carry analogous structure to commodity gold-momentum-126d) + [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed 200d SMA gate (A2 + G2 baseline retained) + [risk_parity, ch.5, p.10] Carlson capital-efficient stacking (F1 stack always-on retained at 3rd constituent — octuple-confirmed uniquely-Pareto-optimal per iter 032 + iter 028/029/030/031 implicit) + [ilmanen_expected_returns, ch.19] MF crisis-alpha (KMLM in A2/G2 ON-state) + Bridgewater All-Weather (Dalio 1996) F1 stack ON-state + [ivy_portfolio] Faber GTAA — bond-trend signal canonical via 10m MA (iter 033 tests momentum-equivalent at meta-ensemble 4-way) + iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way) + iter 030 KILL #125 (orthogonal-asset-class-TSMOM-source bonus +1pt) — iter 033 tests generalization beyond commodity to rates + iter 030 KILL #126 (signal-sleeve incoherence Pareto-neutral, Principle C) — iter 033 tests with rates source on equity sleeve + iter 031 KILL #130 (TSMOM-lookback inverted-U asset-invariant peak at 6m) — held fixed at 126d + iter 032 KILL #135 (orthogonality bonus filter-type-coupled to momentum, Principle G) — held fixed at filter=momentum + [advances_fin_ml, p.222-223] DSR cumulative_n_trials = 128 (Bonferroni 3.91e-04) + [advances_fin_ml, p.208-211] PBO grid-level N=4 stability

---

## Selected config: `h13_meta_4way_25a2_25g2_25f1_25e1gld_mom126`

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
| h13_meta_4way_25a2_25g2_25f1_25e1qqq_mom126 | 0.943 | 0.968 |
| h13_meta_4way_25a2_25g2_25f1_25e1gld_mom126 | 1.041 | 1.037 |
| h13_meta_4way_25a2_25g2_25f1_25e1tlt_mom126 | 0.917 | 0.996 |
| h13_meta_4way_25a2_25g2_25f1_25e1ief_mom126 | 0.929 | 1.047 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 23 | 30 | mean = 16.59%, bar = 11.21% |
| 2. MDD vs SPY | 13 | 20 | mean = 33.77%, bar = 55.17% |
| 3. Gates | 12 | 20 | per_ds = {'lh_56y': 6, 'spy_real': 5}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 6.55e-05, n_trials = 128 |
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

- **TLTSIM coverage**: 1986+ via daily-reset decay model with TLT real-data
  extension 2002+. Same window as lh_56y. No coverage gap.
- **IEFSIM coverage**: 1986+ via UST 7-10y proxy with IEF real-data
  extension. Same window as lh_56y. No coverage gap.
- **Selected config H13.2 gld_mom126** EXACTLY replicates iter 030 H10.4 /
  iter 031 H11.2 / iter 032 H12.1 (per-dataset Sharpe 1.041/1.037, CAGR
  17.03%/16.14%, MDD 33.77%/33.77% IDENTICAL across 4 decimal places).
  **QUADRUPLE-replication confirms iter 030 measurement reproducible** — 4
  independent iters (030, 031, 032, 033) deliver identical metrics to 4
  decimal places.
- **Asset-class axis spread**: per-config raw-metric variation Sharpe
  0.956-1.039 (Δ 0.083) / CAGR 15.19-16.59% (Δ 1.40pp) / MDD 32.31-39.67%
  (Δ 7.36pp). Asset-class axis at filter=mom × lookback=126d produces
  materially different daily-return streams per asset-class signal.
- **TLT lh_56y MDD 47.93% vs spy_real MDD 28.76%** — extreme dataset asymmetry
  (Δ 19.17pp). Mechanism: 1986-2002 era was rate-secular-bull (1981 rate
  peak through 2020 zero-bound disinflation), so TLT-momentum-126d signal
  stayed predominantly ON during 2000-2002 dotcom bear and 1990-1991
  recession — REINFORCING equity drawdown rather than decoupling. spy_real
  2003+ era covers more rate-cycle volatility (2008 ZIRP, 2015-2019
  hike-cycle, 2022 inflation hike) where rate-momentum DOES flip,
  providing some gate decorrelation.
- **IEF lh_56y MDD 52.15% even WORSE than TLT** — counter-intuitive at
  first; intermediate-duration rates would seem to whipsaw less than LT
  rates. Mechanism: IEF's lower volatility profile produces SMOOTHER trend
  filter that captures 1986-2002 rate-secular-bull regime even more
  monolithically than TLT, leaving the gate ON through equity bears.
- **DSR Bonferroni at n_trials=128**: threshold 0.05/128 = 3.91e-04.
  Worst per-config DSR p was 6.55e-05 on spy_real (PASSES strict <0.05;
  PASSES Bonferroni 3.91e-04 with **6.0× margin** — slight reduction from
  iter 032's 6.1× margin due to n_trials inflation 124→128).
- **No new infra**: reuses 'blend' + 'lrs' (momentum filter) + 'static'
  spec types from iter 014/018-032. **771 tests baseline preserved**.
- **Tax classification**: meta-blend with LRS-gate constituents (filter
  =momentum at 4th constituent) → annual_realize. Drag observed 2.18pp
  lh_56y / 2.07pp spy_real, mean 2.13pp — IDENTICAL to iter 030/031/032
  H10.4/H11.2/H12.1 because selected config replicates iter 030 H10.4 exactly.

## Lesson

### KILLs disparados (pre-committed iter-033 #139-#144)

- **KILL #139 FIRED — META-AXIS CEILING 72 17th confirmation at
  asset-class-axis**:
  max H13 = **72** ≤ 72 → 17th meta-axis confirmation across 13 sequential
  meta-axis iters (018→019→020→021→025→026→027→028→029→030→031→032→033 =
  70→71→67→70→70→71→70→69→69→72→72→72→**72**). Asset-class variation at
  filter=mom × lookback=126d did NOT extend ceiling above 72. Iter 030
  H10.4 ceiling-breach to 72 remains attributable to GLD-specific
  configuration, not generalizable across asset-class substitutions.

- **KILL #140 NOT FIRED — STRONG-FORM FALSIFICATION DOES NOT TRIGGER**:
  max H13 = 72, not > 72 strict. New ceiling 72 holds across the
  asset-class generalization axis. No second ceiling-breach beyond iter
  030's discovery.

- **KILL #141 NOT FIRED — RATES ORTHOGONALITY DOES NOT GENERALIZE
  PRINCIPLE A**:
  TLT score est ~69 < 72; Principle A is NOT asset-class-INVARIANT. The
  +1pt orthogonal-asset-class-TSMOM-source bonus from iter 030 KILL #125 is
  **commodity-gold-SPECIFIC**, not generic across orthogonal asset classes.

- **KILL #142 NOT FIRED — DURATION-AXIS RUBRIC-SATURATED**:
  |TLT 69 − IEF 68| ≈ 1pt < 2pt threshold. Duration-axis within rates is
  rubric-saturated; LT (20+y) and intermediate (7-10y) rates produce
  similar score-axis output despite materially different volatility
  profiles. **9th class of RUBRIC SATURATION DOCUMENTED**.

- **KILL #143 NOT FIRED — PRINCIPLE C DOES NOT EXTEND TO RATES**:
  TLT score est 69 < 71 baseline; IEF score est 68 < 71 baseline. Both
  rates configs SCORE BELOW the QQQ-baseline (~71, replicating iter 026
  H6.1). Per iter 030 KILL #126 NEW PRINCIPLE C, signal-sleeve
  incoherence was hypothesized Pareto-NEUTRAL or POSITIVE for commodity
  on equity sleeve. Iter 033 demonstrates this is **commodity-specific** —
  rates-on-equity-LETF DEGRADES rubric by 2-3pt vs equity baseline.

- **KILL #144 FIRED — CRITICAL FINDING — RATES PRINCIPLE A FALSIFICATION**:
  max(TLT score est 69, IEF score est 68) = 69 < 71 QQQ baseline. Both
  rates configs score BELOW the QQQ baseline. **Principle A is
  COMMODITY-GOLD-SPECIFIC**, not generic asset-class orthogonality. The
  +1pt bonus mechanism requires gold-or-commodity-specific structural
  feature beyond asset-class orthogonality alone.

### NEW EMPIRICAL PRINCIPLES (iter 033)

**Principle J — ASSET-CLASS ORTHOGONALITY BONUS IS COMMODITY-GOLD-SPECIFIC**
(KILL #144 FIRED): Per Principle A (iter 030 KILL #125), GLD-momentum-126d
signal at 4th constituent yields +1pt vs QQQ baseline. Per iter 033, neither
TLT nor IEF (both rates) replicate this bonus — both score BELOW QQQ
baseline by 2-3pt. Mechanism: GLD's structural inflation-hedge / dollar-cycle
dynamics provide GENUINE OUT-OF-PHASE gating decisions vs equity SPY-200d
during inflation/recession regimes (Y2K dotcom, 2008 GFC, 2022 inflation
spike all featured gold-equity decoupling). UST rates (LT or intermediate)
co-move with equity-cycle especially in monetary-policy-driven era — rates
rise during equity bull (Fed hikes), rates fall during equity bear (Fed
cuts) — failing to provide decoupled gating. Principle A must be REVISED
from "orthogonal-asset-class-TSMOM-source bonus +1pt at 4-way" to
"GOLD-MOMENTUM-126d-specific +1pt bonus mediated by inflation/dollar-cycle
decoupling from equity-RATES-cycle".

**Principle K — RATES-TREND SIGNALS ARE REGIME-DEPENDENT**: TLT lh_56y MDD
47.93% vs spy_real MDD 28.76% (Δ 19.17pp asymmetry); IEF lh_56y MDD 52.15%
vs spy_real MDD 27.18% (Δ 24.97pp asymmetry). Mechanism: 1986-2002 era was
**rate-secular-bull** (1981 peak through 2020 zero-bound), so rate-momentum
signals stayed predominantly ON during 1990-1991 recession AND 2000-2002
dotcom bear, REINFORCING equity drawdown rather than decoupling. spy_real
2003+ covers more rate-cycle volatility (2008 ZIRP, 2015-2019 hike, 2022
inflation hike) where rate-momentum flips. Rate-trend gating works in
rate-volatile regimes but FAILS in rate-secular regimes. Gold has no
secular trend (sideways with cycles), so gold-momentum captures
inflation/dollar regimes that decouple from equity-cycle regardless of
rate-regime. **Implication for future iterations**: rate-source signals are
unreliable for spy_beater_hunt's 56-year window because rate-secular-bull
era dominates the 1986-2002 segment.

**Principle L — DURATION-AXIS RUBRIC-SATURATED WITHIN RATES** (KILL #142
NOT FIRED): TLT (20+y) vs IEF (7-10y) at filter=mom × lookback=126d
produce similar score outputs despite materially different volatility
(TLT ~15-18% vol, IEF ~5-8% vol). Mechanism: rubric's MDD anchor +
Sharpe-bucket structure compresses duration-axis variation; both rates
configs experience similar gate-flipping pattern in 1986-2002 secular-bull
era which dominates lh_56y MDD. Adds 9th class to RUBRIC SATURATION
taxonomy: duration-axis within rates is rubric-neutral.

### Score breakdown vs iter-030 H10.4 prior closest-to-winner (72→72, 0pt — TIES via QUADRUPLE-REPLICATION)

| criterion | iter 030 H10.4 | iter 031 H11.2 | iter 032 H12.1 | iter 033 H13.2 | Δ vs 030 |
|---|---:|---:|---:|---:|---:|
| 1. CAGR | 23 | 23 | 23 | 23 | 0 (mean 16.59% QUADRUPLE-IDENTICAL) |
| 2. MDD | 13 | 13 | 13 | 13 | 0 (mean 33.77% QUADRUPLE-IDENTICAL) |
| 3. Gates | 12 | 12 | 12 | 12 | 0 (6/7+5/7 QUADRUPLE-IDENTICAL) |
| 4. DSR | 10 | 10 | 10 | 10 | 0 (p 6.55e-05 QUADRUPLE-IDENTICAL) |
| 5. Sharpe | 4 | 4 | 4 | 4 | 0 (mean 1.039 QUADRUPLE-IDENTICAL) |
| 6. Robustness | 10 | 10 | 10 | 10 | — |
| 7. Bonus | 0 | 0 | 0 | 0 | — |
| **Total** | **72** | **72** | **72** | **72** | **0pt — QUADRUPLE-TIE** |

iter 033 H13.2 EXACTLY replicates iter 030/031/032 — QUADRUPLE replication
confirms iter 030 measurement reproducible. Other H13 asset-class variants
LOST 1-3pt (TLT ~69, IEF ~68) confirming Principle A's commodity-gold-
specificity (Principle J).

### Per-config asset-class spread

| Config | Mean Sharpe | Mean CAGR | Mean MDD | Est. score | Δ vs QQQ baseline |
|---|---:|---:|---:|---:|---:|
| H13.1 QQQ baseline | 0.956 | 15.85% | 32.31% | ~71 | 0 (anchor; replicates iter 026 H6.1) |
| **H13.2 GLD anchor** | **1.039** | **16.59%** | **33.77%** | **72 (selected)** | **+1pt (Principle A bonus)** |
| H13.3 TLT NEW | 0.957 | 15.19% | 38.35% | ~69 | −2pt (RATES PENALTY) |
| H13.4 IEF NEW | 0.988 | 16.06% | 39.67% | ~68 | −3pt (RATES PENALTY) |

### Closest-to-winner UNCHANGED

**iter 030 H10.4 (h10_meta_4way_25a2_25g2_25f1_25e1gld) RETAINS closest-
to-winner at score 72** by precedence — iter 033 H13.2 is the QUADRUPLE-
replication anchor at 72 but iter 030 reached the ceiling first (12 trials
earlier, n_trials 116 vs 128). Iter 030 H10.4 remains apex. iter 031 H11.2,
iter 032 H12.1, and iter 033 H13.2 are position-symmetric duplicates by
design.

### Direction implications

- **15-AXIS ARCHITECTURAL TAXONOMY UNCHANGED — meta-axis ceiling 72
  CONFIRMED at asset-class generalization axis**. iter 033 closes the
  asset-class axis (commodity vs rates vs equity at filter=mom × lookback
  =126d) without breaching ceiling. The +1pt iter 030 breach is now
  confirmed to be GOLD-specific NOT extensible by either filter-type
  substitution (iter 032), lookback substitution (iter 031), OR asset-class
  substitution (iter 033). Joint optimum (signal-asset GOLD × filter
  momentum × lookback ~6m) is fully characterized.

- **Principle A IS REVISED to GOLD-SPECIFIC** (Principle J): asset-class
  orthogonality alone is INSUFFICIENT to reproduce the +1pt bonus. The
  mechanism requires gold's specific inflation/dollar-cycle structure which
  decouples from equity-rates-cycle. Future signal-asset hunts on alternate
  commodities (DBC broad, BCOM, USD, FX) may or may not replicate the
  bonus — Principle J predicts only inflation-hedge / dollar-cycle assets
  (gold, silver, broad-commodity-baskets) should retain the bonus; equity-
  correlated assets (rates, equity) should not.

- **Principle C IS REVISED to commodity-specific** (signal-sleeve
  incoherence Pareto-neutral only when commodity-source on equity-sleeve):
  iter 030 KILL #126 demonstrated gold-source on TQQQ-stack sleeve was
  Pareto-NEUTRAL or POSITIVE; iter 033 demonstrates rates-source on
  TQQQ-stack sleeve is Pareto-NEGATIVE (-2-3pt). Principle C must be
  revised from "signal-sleeve incoherence is Pareto-neutral at meta-axis
  4-way" to "commodity-source on equity-sleeve is Pareto-neutral; rates-
  source on equity-sleeve is Pareto-NEGATIVE due to regime-correlation
  with equity-rates-cycle".

- **F1 stack always-on uniquely-Pareto-optimal at 3rd position — 9TH
  IMPLICIT CONFIRMATION** (iter 033): all 4 H13 configs retain F1 at 3rd
  position; max H13 score 72 achieved with F1 retained. F1 status now
  nonuple-confirmed (iter 025/026/027 direct + iter 028/029/030/031/032/
  033 implicit retention).

- **MANDATE §7 RUBRIC-REVISION REVIEW CASE STRENGTHENED to 17th iter**:
  iter 033 confirms iter 030's apex but reveals strong asymmetry (gold
  bonus is principle-bound, not generic). Under any deploy framework,
  GLD-momentum-126d is the empirical apex and rates-source is documented
  inferior. Mandate §1 100% Plano C UNCHANGED.

### Strategic options for iter 034+ (USER DECISION REQUIRED per mandate §1 + §7)

**Recommendation: Option A** (declare hunt RE-CLOSED at iter 033 — most
defensible per mandate §1 MAINTENANCE MODE; iter 030 H10.4 remains apex;
iter 031 (lookback at GLD), iter 032 (filter-type at GLD), and iter 033
(asset-class generalization) confirmed ceiling 72 across THREE single-axis
substitutions of the JOINT optimum; further single-axis exploration on
JOINT optimum is EXHAUSTED across 12+ mapped sub-axis cells; F1+SPLIT
confirmed deploy fallback; 33 iters preserved 66% of budget). Recommendation
EVEN STRONGER than iter 032 due to: (a) iter 033 demonstrated Principle A
is GOLD-SPECIFIC, not asset-class-general — closes the asset-class
generalization possibility; (b) Principles G+H+I+J+K+L now consolidate the
meta-principles under "GOLD-MOMENTUM-126d at 4-way is ARCHITECTURALLY
APEX-SPECIFIC, not extensible by any single-axis variation"; (c) 12+
sub-axis cells mapped without breaching ceiling.

(B) test SILVER (SLVSIM if available) or BROAD-COMMODITY (DBC/BCOM) signal
at meta-ensemble 4-way — MEDIUM credibility per Principle J prediction
(inflation-hedge / dollar-cycle assets should retain bonus); HIGH cost if
DBC/BCOM not in synth cache.

(C) test 5-way structure with GLD-mom-126d as 5th constituent — UNTESTED,
MEDIUM credibility (Principle A bonus may compensate for 5-way base
penalty per iter 027 KILL #107 closure).

(D) test FX (DXY-momentum, USDJPY-momentum) signal — UNTESTED, MEDIUM
credibility per Principle J (dollar-cycle should provide decoupling
similar to gold's dollar-anti-correlation).

(E) NEW DATA INFRA for SLV (silver), DBC (broad commodity), BCOM (broad
commodity), DXY (dollar index) — HIGH cost (requires Tiingo-or-similar
new ticker integration), MEDIUM-HIGH credibility (could replicate iter 030
KILL #125 across more commodity-class assets per Principle J).

Tier PROMISING (72 ∈ [60, 74]). Hunt's empirical informational value
plateaued AGAIN at iter 033 — the +1pt iter 030 breach is now confirmed to
be specific to GOLD asset-class with momentum filter at lookback peak NOT
generalizable to either rates or by single-axis substitution along any axis.
Principles G + H + I + J + K + L consolidate the meta-principles under
"GOLD-MOMENTUM-126d AT 4-WAY IS APEX-SPECIFIC". Mandate §1 100% Plano C
UNCHANGED — research only.

### Citations applied

- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction over multiple
  alpha streams (4-way meta-ensemble at strategy-level with asset-class
  generalization sub-axis exploration — 17th iter at meta-axis)
- **Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250**
  TSMOM canonical (rates included in original 58-asset universe;
  iter 033 TLT/IEF momentum signals demonstrate that meta-ensemble
  bonus is NOT inherited from TSMOM premium — bonus mechanism is
  rubric-specific gate-decorrelation, NOT TSMOM premium-magnitude)
- **Asness-Moskowitz-Pedersen (2013) Value and Momentum Everywhere, JoF
  68(3):929-985** — momentum pervasive across asset classes; iter 033
  demonstrates that "momentum-everywhere" does NOT translate to "meta-
  ensemble bonus everywhere" — asset-class structural features
  (inflation-hedge vs rate-cycle vs equity-cycle) determine whether the
  bonus realizes
- `[ivy_portfolio]` Faber GTAA — bond-trend signal canonical via 10m MA;
  iter 033 demonstrates rates-trend gating WORKS in rate-volatile regimes
  (spy_real 2003+) but FAILS in rate-secular-bull regimes (lh_56y
  1986-2002)
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed 200d SMA gate
  (A2 + G2 baseline retained — both equity-track 200d-SMA)
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking
  (F1 stack always-on retained — nonuple-confirmed uniquely-Pareto-optimal)
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha (KMLM in
  A2/G2/E1 ON-state)
- Bridgewater All-Weather (Dalio 1996) F1 stack ON-state retained
- `[advances_fin_ml, p.208-211]` PBO via CSCV (N=4 grid)
- `[advances_fin_ml, p.222-223]` DSR with cumulative_n_trials = 128
  (Bonferroni 3.91e-04; worst per-config p 6.55e-05 PASSES with 6.0×
  margin — slight reduction from iter 032's 6.1×)
- `[advances_fin_ml, p.196-202]` Bootstrap CI
- `[advances_fin_ml, p.31-34]` Cross-lib factor framework
- iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way) — REFINED
  by Principle G + Principle J to JOINT-optimum-specific AND
  GOLD-SPECIFIC
- iter 030 KILL #125 (orthogonal-asset-class-TSMOM-source bonus +1pt) —
  **REVISED by iter 033 KILL #144 PRINCIPLE J: COMMODITY-GOLD-SPECIFIC,
  not generic asset-class orthogonality**
- iter 030 KILL #126 (signal-sleeve incoherence Pareto-neutral, Principle C)
  — **REVISED by iter 033 KILL #143 NOT FIRED: commodity-on-equity-sleeve
  Pareto-neutral; rates-on-equity-sleeve Pareto-NEGATIVE**
- iter 031 KILL #130 (TSMOM-lookback inverted-U asset-invariant peak at 6m)
  — held fixed at 126d
- iter 032 KILL #135 (orthogonality bonus filter-type-coupled to momentum,
  Principle G) — held fixed at filter=momentum
