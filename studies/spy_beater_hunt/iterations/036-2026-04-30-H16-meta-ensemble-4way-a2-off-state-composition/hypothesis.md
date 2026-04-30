# spy_beater_hunt iter 036 — Hypothesis

**Slug**: `H16-meta-ensemble-4way-a2-off-state-composition`

**Cumulative n_trials**: 136 (prior) → **140** (after this iter, +4 configs)

**Date**: 2026-04-30

---

## Hypothesis

H16 tests whether the off-state composition Principle N (iter 035 KILL #154 —
KMLM off > IEF off by +2pt for GLD-track gate-decision) GENERALIZES to A2's
QQQ-track gate-decision OR is gate-source-asset-class-COUPLED.

20th iter at meta-ensemble axis. First iter testing off-state composition
sub-axis at the A2 (1st-position) constituent. Last single-axis sub-axis
around the iter 035 H15.2 strategy-level apex (74) without new data
infrastructure.

iter 035 found Principle N (off-state crisis-alpha is asset-class-conditional):
- For GLD-track gate-decisions (iter 035 H15): KMLM > Blend > IEF on Sharpe /
  CAGR / MDD all axes — KMLM dominates because GLD-trend-OFF coincides with
  USD-strength / global-macro-trend regimes where MF crisis-alpha catches.
- For SPY-track gate-decisions (iter 016 G1 hybrid): IEF > Blend > KMLM —
  IEF dominates because SPY-trend-OFF = equity-bear regimes where passive
  duration is matched-vol safe-asset.

A2 = QQQ-track 200d-SMA gate. A2-OFF coincides with NDX-equity-bear regimes
(2000-02 dotcom -78%, 2008 GFC, 2022 inflation, 2020 COVID). Per Principle N
mechanism (off-state asset must align with gate-source's regime structure):
- If Principle N is CONSTITUENT-COUPLED via gate-source asset-class:
  → equity-track (QQQ) OFF should prefer IEF (matches SPY-track iter 016
    pattern) over KMLM crisis-alpha;
  → A2 KMLM off should DEGRADE score by ≥1pt vs A2 IEF off baseline.
- If Principle N is CONSTITUENT-AXIS-INDEPENDENT (KMLM off universally
  positive): A2 KMLM off should match or exceed A2 IEF off — would imply
  KMLM crisis-alpha dominates passive duration regardless of gate-source.

**Linear decomposition prediction (iter 026 KILL #103 + Principle N)**:
   H16 score = 74 (4-way E1gld+KMLM-off baseline iter 035 H15.2)
             + (A2 off-state-axis perturbation Δ)

Falsification thresholds:
- max H16 ≥ 75 strong-form breach KILL #158 (constituent-axis-independent)
- max H16 = 74 ceiling-tied (constituent-coupled OR off-state-axis rubric-
  saturated at A2 position)
- max H16 ≤ 73 off-state composition Pareto-degrades baseline at A2 position
  (Principle N reverse-confirmed for equity-track via constituent-coupling)

---

## Configs (4 — naming consistent w/ iter 035 H15)

A2_BASE_SPEC, G2_IEF_SPEC, F1_STACK_SPEC reused VERBATIM from iter
026/030/031/032/033/034/035. E1_GLD_MOM126_KMLM_OFF_SPEC reused VERBATIM
from iter 035 H15.2 (apex). ONLY A2's `off_weights` parameter varies across
H16.1-H16.4.

### H16.1 — A2 IEF off (BASELINE — replicates iter 035 H15.2 EXACTLY)

`{IEFSIM: 1.0}` for A2's off_weights.

Anchor / sextuple-replication test. Should produce identical raw metrics
to iter 035 H15.2 (Sharpe 1.066, CAGR 17.09%, MDD 30.22%, score 74).

Slug: `h16_meta_4way_25a2_25g2_25f1_25e1gld_mom126_kmlm_off_a2_ief_off`

### H16.2 — A2 KMLM off (managed-futures crisis-alpha for QQQ-trend OFF)

`{KMLMSIM: 1.0}` for A2's off_weights (TESTS Principle N CONSTITUENT-
INDEPENDENCE).

Per iter 016 G1 hybrid for SPY-track, KMLM off-state DEGRADED IEF baseline by
~1pt. Predicted: H16.2 ≤ H16.1 by ≥ 1pt (Principle N constituent-coupled —
equity-track requires IEF, commodity-track requires KMLM).

Slug: `h16_meta_4way_25a2_25g2_25f1_25e1gld_mom126_kmlm_off_a2_kmlm_off`

### H16.3 — A2 TLT off (long-duration UST 20+y for QQQ-trend OFF)

`{TLTSIM: 1.0}` for A2's off_weights.

Per iter 035 H15.3 finding (TLT Pareto-neutral within ±1pt of IEF baseline
at GLD position): predicted similar pattern at A2 position. Tests duration
extension at OFF for equity-track gate.

Slug: `h16_meta_4way_25a2_25g2_25f1_25e1gld_mom126_kmlm_off_a2_tlt_off`

### H16.4 — A2 Blend off (50% IEF + 50% KMLM)

`{IEFSIM: 0.5, KMLMSIM: 0.5}` for A2's off_weights.

iter 016 G1 hybrid pattern test at A2 position. If H16.4 falls between
H16.1 and H16.2, off-state composition is approximately ADDITIVE within
blend at A2 position (per iter 035 H15.4 confirming for GLD position).

Slug: `h16_meta_4way_25a2_25g2_25f1_25e1gld_mom126_kmlm_off_a2_blend_off`

---

## KILL conditions (pre-committed; numbered from #156 as last used in iter 035)

- **KILL #157 — META-AXIS CEILING 74 NOT confirmed**: if max H16 ≤ 74
  (consistent with iter 035 H15.2 strategy-level apex; A2 off-state-axis
  NOT a new ceiling-breach axis). Note: this is the base condition; KILL
  #157 fires when max H16 = 74 ceiling-tied without strong-form breach.

- **KILL #158 — STRONG-FORM FALSIFICATION**: if max H16 ≥ 75 strict
  (+1pt over iter 035 H15.2 strategy-level apex 74 via A2 off-state
  alternative). Would falsify constituent-coupling claim and confirm
  off-state composition is universally optimizable across constituents.

- **KILL #159 — H16.1 ANCHOR REPRODUCIBILITY**: H16.1 per-config raw metrics
  must match iter 035 H15.2 to 2-4 decimal places (validates Principle M
  per-config reproducibility). If H16.1 deviates from iter 035 H15.2 by
  > 0.5pt score → REPRODUCIBILITY-ISSUE FLAG TRIGGERED (Principle M
  generalization to grid-shifted measurement).

- **KILL #160 — PRINCIPLE N CONSTITUENT-COUPLING TEST (the headline KILL)**:
  - If H16.2 (A2 KMLM off) < H16.1 (A2 IEF off) by ≥ 1pt
    → **PRINCIPLE N IS CONSTITUENT-COUPLED via gate-source asset-class** —
      equity-track (SPY/QQQ) gate REQUIRES IEF off-state; commodity-class
      (GLD) gate REQUIRES KMLM off-state. Strengthens Principle N's
      asset-class-conditional formulation. Linear decomposition: A2's
      off-state choice is INDEPENDENT of E1gld's off-state choice; each
      constituent's off-state-axis has its own optimum determined by
      gate-source asset-class.
  - If H16.2 (A2 KMLM off) ≥ H16.1 (A2 IEF off) by < 1pt (within ±1pt)
    → Principle N is partially DECOUPLED — KMLM off-state at equity-track
      position is rubric-neutral vs IEF baseline at A2 position; suggests
      Principle N's GLD-specific +2pt was driven by GLD-mom orthogonality
      INTERACTION with KMLM off-state, NOT KMLM off-state intrinsic merit.
  - If H16.2 (A2 KMLM off) > H16.1 (A2 IEF off) by ≥ 1pt
    → **PRINCIPLE N IS CONSTITUENT-AXIS-INDEPENDENT** — KMLM off-state is
      Pareto-positive at all constituent positions regardless of
      gate-source asset-class. MAJOR architectural finding: would
      generalize beyond GLD-track and reopen full off-state cross-product.

- **KILL #161 — TLT OFF-STATE A2 EXTENSION TEST**: if |H16.3 − H16.1| ≤ 1pt
  → TLT Pareto-neutral pattern from iter 035 H15.3 generalizes to A2
  position (TLT is constituent-axis-independent rubric-neutral baseline).
  Confirms duration-axis extension at off-state position is gate-source-
  agnostic (orthogonal to Principle N's asset-class-conditional choice).

- **KILL #162 — A2 OFF-STATE-AXIS RUBRIC SATURATION**: if max H16 - min H16
  ≤ 1pt → rubric-saturated (Principle N's effect at A2 position is
  smaller than rubric resolution; off-state composition at A2 position is
  NOT a meaningful axis for rubric-driven optimization).

---

## Expected outcomes

### Most-likely scenario (high prior — Principle N CONSTITUENT-COUPLED)

- H16.1 IEF off: Sharpe 1.066, CAGR 17.09%, MDD 30.22%, score 74 (replicates
  iter 035 H15.2 EXACTLY).
- H16.2 KMLM off: Sharpe ~1.04, CAGR ~16.5%, MDD ~32-35%, score est ~72-73
  (DEGRADES baseline by 1-2pt at A2 equity-track position — Principle N
  reverse-confirmed for equity-track).
- H16.3 TLT off: Sharpe ~1.06, CAGR ~16.9%, MDD ~33%, score est ~73-74
  (Pareto-neutral within ±1pt vs baseline).
- H16.4 Blend off: Sharpe ~1.05, CAGR ~16.8%, MDD ~31-32%, score est ~73
  (between H16.1 and H16.2, linear interpolation).
- KILL #157 FIRED, KILL #160 FIRED (constituent-coupled).
- max H16 = 74 (ceiling-tied at H16.1).

### Alternative scenario A (Principle N constituent-axis-independent)

- H16.2 KMLM off: score ≥ 75 (KMLM off-state universally positive).
- KILL #158 FIRED, KILL #160 (constituent-axis-independent branch).
- max H16 ≥ 75 (strong-form breach over iter 035 H15.2).
- MAJOR architectural finding: cross-product KMLM off-state across all
  constituents would be the new APEX direction.

### Alternative scenario B (rubric saturation at A2 off-state-axis)

- All H16 configs within ±0.5pt → KILL #162 FIRED.
- A2 off-state-axis is NOT a meaningful rubric axis for optimization at
  current strategy-level baseline — Principle N's effect is GLD-specific.

---

## INCOMPLETE flags

- A2_BASE_SPEC reused VERBATIM from iter 026/030/031/032/033/034/035 (only
  off_weights parameter varies). Spec definition: A2 = iter 006 a6_tqqq_
  split_kmlm30_tlt10 with QQQ-200d-SMA gate, on_weights {TQQQSIM 0.30,
  QLDSIM 0.30, KMLMSIM 0.30, TLTSIM 0.10}, off_weights {IEFSIM 1.0}.
- E1_GLD_MOM126_KMLM_OFF_SPEC reused VERBATIM from iter 035 H15.2 apex
  (signal=GLDSIM, filter=momentum, lookback_days=126, on_weights identical
  to A2's, off_weights {KMLMSIM 1.0}).
- G2_IEF_SPEC and F1_STACK_SPEC reused VERBATIM from iter 026/030/...
- N_CONFIGS = 4. cumulative_n_trials goes 136 → 140 (DSR Bonferroni
  threshold tightens slightly: 0.05/140 = 3.57e-04 vs prior 3.68e-04).
- 'blend' + 'lrs' (sma + momentum filters) + 'static' spec types — NO new
  infra. 771 tests baseline preserved.
- All sims (TQQQSIM, QLDSIM, KMLMSIM, TLTSIM, IEFSIM, UPROSIM, TMFSIM,
  UGLSIM, NTSXSIM, GDESIM, QQQSIM, SPYSIM, GLDSIM) in testfolio cache.
- Mandate §1 100% Plano C UNCHANGED — research only. No deploy implication.

---

## Citations applied

- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction over multiple
  alpha streams (4-way meta-ensemble at strategy-level — 20th iter at meta-
  axis with A2 off-state composition sub-axis exploration)
- `[advances_fin_ml, p.208-211]` PBO via CSCV (N=4 grid)
- `[advances_fin_ml, p.222-223]` DSR with cumulative_n_trials = 140
  (Bonferroni 3.57e-04)
- `[advances_fin_ml, p.196-202]` Bootstrap CI
- `[advances_fin_ml, p.31-34]` Cross-lib factor framework
- Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250
  (E1gld TSMOM-126d gate-source on commodity-class — held fixed at apex)
- Asness-Moskowitz-Pedersen (2013) Value and Momentum Everywhere, JoF
  68(3):929-985 (momentum across asset classes)
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed 200d SMA gate
  canonical (A2 + G2 baseline retained; A2 off_weights varied)
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking (F1 stack
  always-on retained at 3rd position — undecuple-confirmed)
- `[ilmanen_expected_returns, ch.19]` Managed-futures crisis-alpha role
  (Principle N source — KMLM off-state hypothesis at equity-track tested)
- iter 016 G1 hybrid finding (off-state IEF > Blend > KMLM for SPY-track
  stack — predicts H16 same pattern at A2 QQQ-track if Principle N is
  constituent-coupled)
- iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way) — held fixed
- iter 026 KILL #103 (linear decomposition principle) — UPPER-BOUND test
- iter 030 KILL #125 / Principle A (orthogonal-asset-class-TSMOM-source
  bonus +1pt) — held fixed via E1gld at 4th
- iter 030 KILL #126 / Principle C (signal-sleeve incoherence Pareto-
  positive) — held fixed
- iter 031 KILL #130 / Principle D (TSMOM-lookback inverted-U asset-
  invariant peak at 6m / 126d) — held fixed at 126d
- iter 032 KILL #135 / Principle G (orthogonality bonus filter-type-
  coupled to momentum) — held fixed at filter=momentum
- iter 033 KILL #144 / Principle J (orthogonality bonus is COMMODITY-
  GOLD-SPECIFIC) — operative
- iter 034 KILL #150 / Principle M (rubric score is grid-composition-
  dependent via G1 PBO) — caveat for cross-iter score comparison
- iter 035 KILL #154 / Principle N (off-state crisis-alpha is asset-class-
  conditional — KMLM > IEF for GLD-track gate) — CONSTITUENT-COUPLING
  test is the headline of this iter
- iter 035 KILL #156 (H15.1 sextuple-replication via Principle M) — H16.1
  septuple-replication test (now 7 independent measurements of iter 030
  H10.4 spec embedded in iter 035 H15.2 + iter 036 H16.1)
