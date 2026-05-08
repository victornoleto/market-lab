# Iter 033 — H13 META-ENSEMBLE 4-WAY ASSET-CLASS ORTHOGONALITY GENERALIZATION

**Slug**: `H13-meta-ensemble-4way-asset-class-orthogonality-generalization`
**Date**: 2026-04-30
**Cumulative n_trials**: 124 (before) → **128** (after, +4 configs)

---

## Hypothesis

**Principle A** (iter 030 KILL #125 FIRED) demonstrated that GLD-momentum-126d
signal at the 4th constituent slot of a meta-ensemble 4-way structure
delivers a +1pt orthogonal-asset-class-TSMOM-source bonus over QQQ-momentum-126d
baseline (iter 026 H6.1 71 → iter 030 H10.4 72). The bonus mechanism was
hypothesized to be asset-class decorrelation: equity QQQ + equity SPY +
always-on stack + orthogonal **commodity** Gold accesses a NEW dimension of
gate-source decorrelation.

**Iter 032 KILL #135 FIRED — Principle G** refined this: the bonus is
specifically COUPLED to the MOMENTUM filter type at lookback peak ~6m. SMA
and EMA filters at GLD source LOSE 1-3pt of the bonus.

**Iter 033 directly tests Principle A's GENERALIZATION beyond commodity to a
DIFFERENT orthogonal asset class — RATES (TLT long-duration UST + IEF
intermediate-duration UST)** — under filter=momentum / lookback=126d held
fixed (per Principle G + Principle D inverted-U peak).

If TLT-momentum-126d signal scores ≥ 72 → **Principle A is asset-class-INVARIANT**
(orthogonal-asset-class bonus generalizes from commodity to rates).
If TLT-momentum-126d signal scores < 71 → **Principle A is COMMODITY-SPECIFIC**
(bonus requires gold-or-commodity-specific structural feature, not just
asset-class orthogonality alone).

Per Moskowitz-Ooi-Pedersen (2012, *JFE 104(2):228-250*) Time Series Momentum,
TSMOM premium structure was empirically demonstrated across 58 instruments
spanning equities, bonds, currencies, AND commodities — implying TSMOM signals
on rates SHOULD carry similar predictive structure as on commodities. Per
Asness-Moskowitz-Pedersen (2013, *JoF 68(3):929-985*) "Value and Momentum
Everywhere", momentum is a pervasive cross-asset-class phenomenon. Iter 033
tests whether this empirical regularity translates to the spy_beater_hunt
rubric's score-axis at the meta-ensemble 4-way structure.

---

## Configurations (4 configs)

All configs hold A2 (closest-to-winner LRS-mono QQQ-200d-SMA), G2 (IEF
SPY-200d-LETF), F1 (stack always-on Carlson-style) IDENTICAL to iter 030/031/032.
ONLY the 4th constituent's `signal_ticker` varies among {QQQSIM, GLDSIM,
TLTSIM, IEFSIM}, with `filter=momentum`, `lookback_days=126`, on/off weights
identical (iter 030 H10.4 baseline TQQQ 30 + QLD 30 + KMLM 30 + TLT 10 ON,
IEF 100% OFF).

| Config slug | 4th constituent signal | Asset class | Hypothesis |
|---|---|---|---|
| `h13_meta_4way_25a2_25g2_25f1_25e1qqq_mom126` | QQQSIM | Equity (large-cap growth) | BASELINE — replicates iter 026 H6.1 equal-weight 4-way; expected score ~71 (no orthogonality bonus, signal-asset matches A2 sleeve class) |
| `h13_meta_4way_25a2_25g2_25f1_25e1gld_mom126` | GLDSIM | Commodity (gold) | ANCHOR — replicates iter 030 H10.4 EXACTLY (TRIPLE-already replicated in 030/031/032); expected score 72 — Principle A bonus realized |
| `h13_meta_4way_25a2_25g2_25f1_25e1tlt_mom126` | TLTSIM | Rates (LT UST 20+y) | NEW — rates orthogonality test; +1pt if Principle A generalizes |
| `h13_meta_4way_25a2_25g2_25f1_25e1ief_mom126` | IEFSIM | Rates (intermediate UST 7-10y) | NEW — short-duration rates test; tests duration sensitivity within rates orthogonality |

---

## Pre-committed KILL conditions (extending iter 032's KILL #138)

### KILL #139 — META-AXIS CEILING 17th confirmation

**FIRED if**: `max(score across H13 configs) ≤ 72`
**Implies**: Meta-axis ceiling 72 holds across 17 sequential meta-axis iters
(018→019→020→021→025→026→027→028→029→030→031→032→033 = 70→71→67→70→70→71→
70→69→69→72→72→72→?). 13 sequential iters at meta-axis confirmed when ceiling
holds.

### KILL #140 — STRONG-FORM FALSIFICATION

**FIRED if**: `max(score across H13 configs) > 72`
**Implies**: SECOND ceiling-breach beyond iter 030's discovery; ceiling
re-evaluates upward. Would imply rates orthogonality bonus stacks
super-additively with existing constituents.

### KILL #141 — RATES ORTHOGONALITY GENERALIZATION (Principle A → A')

**FIRED if**: `score(h13_e1tlt_mom126) ≥ 72` (TIES or exceeds GLD anchor)
**Implies**: Principle A is asset-class-INVARIANT. Promotes Principle A to
A': "+1pt orthogonal-asset-class-TSMOM-source bonus generalizes across
non-equity asset classes (commodity AND rates)". Future hunts should explore
FX/carry signals at 4th constituent.

**NOT FIRED if**: `score(h13_e1tlt_mom126) < 72` → Principle A may be
commodity-specific (or commodity+rates-asymmetric); see KILL #144.

### KILL #142 — DURATION DIFFERENTIATION

**FIRED if**: `|score(h13_e1tlt_mom126) − score(h13_e1ief_mom126)| ≥ 2pt`
**Implies**: Within the rates asset class, duration-axis is rubric-relevant.
TLT (20+y) and IEF (7-10y) produce materially different gating decisions.

**NOT FIRED if**: `|Δ| < 2pt` → duration-axis is rubric-saturated within rates.

### KILL #143 — SIGNAL-SLEEVE INCOHERENCE STRENGTH (rates-on-equity-LETF)

**FIRED if**: `score(h13_e1tlt_mom126) ≥ 71` AND `score(h13_e1ief_mom126) ≥ 71`
**Implies**: Per Principle C (iter 030 KILL #126 NEW), rates-trend signal
applied to TQQQ-stack equity sleeve does NOT degrade rubric — confirms
Principle C extends from commodity-on-equity (gold→TQQQ) to
rates-on-equity (UST→TQQQ).

**NOT FIRED if**: either rates config scores < 70 → signal-sleeve
incoherence DOES degrade rubric for rates source.

### KILL #144 — RATES PRINCIPLE A FALSIFICATION (commodity-specificity)

**FIRED if**: `max(score(tlt), score(ief)) < 71` (BOTH rates configs LOSE
the +1pt bonus AND fall below QQQ baseline)
**Implies**: Principle A is COMMODITY-SPECIFIC, NOT a general
orthogonal-asset-class principle. Bonus requires gold-or-commodity-specific
structural feature beyond asset-class orthogonality alone.

**NOT FIRED if**: `max(score(tlt), score(ief)) ≥ 71` → at least partial
generalization (rates retain at least the QQQ baseline).

---

## Expected outcomes (pre-commit estimates)

| Config | Expected Sharpe | Expected CAGR | Expected MDD | Expected score |
|---|---:|---:|---:|---:|
| `h13_e1qqq_mom126` (QQQ baseline) | ~0.956 | ~15.85% | ~32.3% | ~71 (replicates iter 026 H6.1) |
| `h13_e1gld_mom126` (GLD anchor) | 1.039 | 16.59% | 33.77% | **72** (TRIPLE-replicates iter 030/031/032) |
| `h13_e1tlt_mom126` (TLT NEW) | 0.95-1.05 | 15-17% | 30-37% | **71-72** (uncertainty band; Principle A generalization is the hypothesis to test) |
| `h13_e1ief_mom126` (IEF NEW) | ≈ TLT or slightly lower | 14-16% | 28-33% | **70-72** (uncertainty; lower-vol IEF may produce smoother gating) |

---

## INCOMPLETE flags

- **TLTSIM coverage**: TLTSIM is in testfolio cache (1986+ via daily-reset
  decay model with TLT real returns 2002+). Coverage matches lh_56y full
  window. No coverage gap.
- **IEFSIM coverage**: IEFSIM is in testfolio cache (synthetic UST 7-10y
  proxy 1986+ via SHY/IEF real-data extension). Same window as lh_56y.
- **Selected config H13.2 gld_mom126** EXACTLY replicates iter 030 H10.4 /
  iter 031 H11.2 / iter 032 H12.1 — expected QUADRUPLE replication anchor
  point at score 72.
- **Asset-class orthogonality precise definition**: A2 sleeve = TQQQ/QLD
  (equity-LETF) + KMLM (managed-futures, multi-asset) + TLT (rates LT). G2
  sleeve = UPRO/TMF/UGL/KMLM/IEF (mixed asset). F1 sleeve = NTSX/GDE/TLT/KMLM
  (stacked equity+rates+commodity). The 4th constituent's signal_ticker
  defines the GATING ASSET CLASS (where TSMOM is computed); the SLEEVE assets
  may overlap. TLT-mom-126d signal on TQQQ-stack sleeve = "rates-trend
  signal applied to equity-trend sleeve" — orthogonal in SIGNAL space, NOT
  in sleeve space.
- **No new infra**: reuses 'blend' + 'lrs' (momentum filter) + 'static' spec
  types from iter 014/018-032. **771 tests baseline preserved**.
- **DSR Bonferroni at n_trials=128**: threshold 0.05/128 = 3.91e-04
  (slightly tighter than iter 032's 4.03e-04). Need worst per-config DSR p
  ≤ 3.91e-04 to PASS Bonferroni strict.

---

## Citations

- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction over multiple
  alpha streams (4-way meta-ensemble, 17th iter at meta-axis with
  asset-class generalization sub-axis)
- **Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250**
  — TSMOM premium across 58 instruments spanning equities/bonds/FX/commodities
  (rate momentum included in original universe; iter 033 tests rate signal
  at meta-ensemble 4-way structure)
- **Asness-Moskowitz-Pedersen (2013) Value and Momentum Everywhere, JoF
  68(3):929-985** — momentum is a pervasive cross-asset-class phenomenon;
  predicts TSMOM signal on rates SHOULD carry similar structure as on
  commodities
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed 200d SMA gate (A2 + G2
  baseline retained)
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking (F1 stack
  always-on retained — octuple-confirmed uniquely-Pareto-optimal at 3rd
  position per iter 032 KILL #110 octuple-confirmation)
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha (KMLM in A2/G2 ON-state)
- Bridgewater All-Weather (Dalio 1996) F1 stack ON-state
- `[ivy_portfolio]` Faber GTAA — bond-trend signal canonical via 10m moving
  average (iter 033's TLT-mom-126d is a momentum-equivalent of Faber's
  TLT-SMA-200d gate)
- iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way)
- iter 030 KILL #125 (orthogonal-asset-class-TSMOM-source bonus +1pt) —
  iter 033 tests generalization to rates
- iter 030 KILL #126 (signal-sleeve incoherence Pareto-neutral, Principle C)
  — iter 033 tests with rates source on equity sleeve
- iter 031 KILL #130 (TSMOM-lookback inverted-U asset-invariant peak at 6m)
  — held fixed at 126d
- iter 032 KILL #135 (orthogonality bonus filter-type-coupled to momentum,
  Principle G) — held fixed at filter=momentum
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 128 (Bonferroni
  3.91e-04)
- `[advances_fin_ml, p.208-211]` PBO grid-level N=4 stability
- `[advances_fin_ml, p.31-34]` factor framework — meta-ensemble axis
  17th iter (asset-class generalization sub-axis)
