# Iter 035 — H15 META-ENSEMBLE 4-WAY GLD-MOM OFF-STATE COMPOSITION SUB-AXIS

**Slug**: `H15-meta-ensemble-4way-gld-mom-off-state-composition`
**Date**: 2026-04-30
**Cumulative n_trials before**: 132 (iter 034 ended at 132)
**Cumulative n_trials after**: 136 (iter 035 adds 4)

---

## Hypothesis

**H15 — does the +1pt Principle A bonus (iter 030 KILL #125 → revised to GOLD-SPECIFIC per Principle J iter 033 KILL #144) for GLD-mom-126d at 4th constituent depend on the OFF-state composition of that constituent?**

This sub-axis is UNTESTED across 18 prior meta-axis iters. iter 030/031/032/033/034 all hold off_weights = {"IEFSIM": 1.0} for the E1gld constituent. The OFF-state composition of the constituent is the LAST untested single-axis variation around the iter 030 H10.4 strategy-level apex without new data infrastructure.

### Mechanism + linear-decomposition prediction

When GLD 6-month momentum is negative (gate OFF), the constituent allocates 100% to off-state assets. iter 030 H10.4 uses IEFSIM (intermediate UST 7-10y) as the safe asset.

iter 016 G1 hybrid (post-impossibility second hybrid sanity check) found a monotonic OFF-state composition dose-response for SPY-track stack: IEF > 50/50 IEF+KMLM > KMLM on Sharpe + MDD + CAGR axes — meaning IEF was DOMINANT off-state for SPY-track gate-decision. Generalization to GLD-track is the open question.

**Mechanism-level predictions**:

1. **GLD trend OFF coincides with equity BULL markets historically** (1995-2000 dot-com, 2013-2015 secular gold bear, 2018, 2022 partial). During these periods, IEF cash-equivalent matches stock returns with low vol; KMLM tends to LAG (mediocre returns in bull regimes); TLT exposes duration risk during rate-tightening cycles (2018, 2022).

2. **GLD trend OFF can coincide with USD strength regimes** (gold-down typically inverse-DXY-up). USD strength regimes can pressure both equity multinationals AND commodity-linked positions. KMLM may benefit from FX trends; TLT can benefit from disinflation.

3. **Crisis-alpha hypothesis**: if GLD-OFF coincides with stress regime where multi-asset crisis-alpha pays (rare — gold typically outperforms in stress), KMLM off may provide MDD-axis bonus. But empirically gold-OFF and stress-regime are NOT correlated.

Linear decomposition (iter 026 KILL #103 generalization):

```
H15 score = 72 (4-way E1gld baseline iter 030 H10.4)
          + (off-state-axis perturbation Δ)
```

If off-state-axis is rubric-saturated (variation < 2pt), the H15 spread is < 2pt = 9th class of RUBRIC SATURATION. If KMLM-off provides crisis-alpha bonus that survives the GLD-OFF regime alignment, max H15 may exceed 73.

**Falsification criteria**:
- IF max H15 score ≥ 74 → strong-form falsification: ceiling 73 BROKEN at off-state-axis (KILL #152)
- IF max H15 score = 73 → ceiling-tied: off-state composition Pareto-positive vs IEF baseline
- IF max H15 score = 72 (anchor matches iter 030 H10.4 in current grid) → off-state composition Pareto-neutral
- IF max H15 score ≤ 71 → off-state composition matters NEGATIVELY (KMLM/TLT/Blend all degrade IEF baseline)

This addresses iter 034's strategic option D (test off-state composition) — the only feasible single-axis test without new data infrastructure (Options A/B/C/E require user permission, methodology refactor, or new synth integration NOT in testfolio cache).

NOTE on Principle M caveat: per iter 034, cross-iter score comparisons are CONFOUNDED by G1 PBO grid-composition. The H15.1 IEF anchor will replicate iter 030 H10.4's per-dataset metrics (Sharpe / CAGR / MDD / DSR) to 4 decimal places, but its score may shift ±1pt vs iter 034's H14.4 reading due to new sibling configs. Treat H15.1 as the within-iter baseline.

---

## Citations

- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction over multiple alpha streams (4-way meta-ensemble at strategy-level, **19th iter at meta-axis**, NEW sub-axis: off-state composition for GLD constituent)
- `[ilmanen_expected_returns, ch.19]` Managed-futures crisis-alpha role — KMLM off-state hypothesis
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed 200d SMA gate canonical — IEF safe asset off-state baseline
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking (F1 stack always-on retained — decuple-confirmed uniquely-Pareto-optimal at 3rd position per iter 034)
- Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 (E1gld TSMOM-126d gate-source on commodity-class)
- Asness-Moskowitz-Pedersen (2013) Value and Momentum Everywhere, JoF 68(3):929-985 (momentum across asset classes)
- Bridgewater All-Weather (Dalio 1996) F1 stack ON-state composition
- iter 016 G1 hybrid (off-state composition dose-response monotonic IEF > Blend > KMLM for SPY-track stack)
- iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way) — held fixed via E1gld at 4th
- iter 026 KILL #103 (linear decomposition principle) — UPPER-BOUND prediction model
- iter 030 KILL #125 / Principle A (orthogonal-asset-class-TSMOM-source bonus +1pt) — operative for GLD-mom-126d at 4th
- iter 030 KILL #126 / Principle C (signal-sleeve incoherence Pareto-positive) — held fixed (sleeve unchanged)
- iter 031 KILL #130 / Principle D (TSMOM-lookback inverted-U asset-invariant peak at 6m / 126d) — held fixed at 126d
- iter 032 KILL #135 / Principle G (orthogonality bonus filter-type-coupled to momentum) — held fixed at filter=momentum
- iter 033 KILL #144 / Principle J (orthogonality bonus is COMMODITY-GOLD-SPECIFIC) — operative for GLD-mom-126d
- iter 034 KILL #150 / Principle M (rubric score is grid-composition-dependent via G1 PBO) — caveat for cross-iter score comparison
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 136, Bonferroni threshold 0.05/136 = 3.68e-04
- `[advances_fin_ml, p.208-211]` PBO grid-level N=4 stability

---

## Configs (4)

Naming follows iter 030 H10.4 base spec extended with off-state suffix `_offX`.

### H15.1 — IEF off (BASELINE — replicates iter 030 H10.4 EXACTLY, anchor)

```
h15_meta_4way_25a2_25g2_25f1_25e1gld_mom126_ief_off
```

25% A2 (QQQ-200d-SMA, off=IEF) + 25% G2 IEF (SPY-200d-SMA, off=IEF) + 25% F1 stack (always-on) + 25% E1gld (GLD-mom-126d, off=IEF [BASELINE])

QUINTUPLE-PLUS-replication anchor of iter 030 H10.4 / iter 031 H11.2 / iter 032 H12.1 / iter 033 H13.2 / iter 034 H14.4. Should produce score ≈ 72-73 (rubric noise band per Principle M).

### H15.2 — KMLM off (managed-futures crisis-alpha when GLD trend OFF)

```
h15_meta_4way_25a2_25g2_25f1_25e1gld_mom126_kmlm_off
```

25% A2 + 25% G2 IEF + 25% F1 stack + 25% E1gld (off=KMLMSIM — managed-futures crisis-alpha)

Tests if crisis-alpha at OFF-state for the orthogonal-asset-class constituent provides Pareto-positive vs IEF baseline. Mechanism: KMLM trends could outperform IEF during USD-strength / equity-stress periods that may overlap with GLD trend OFF.

### H15.3 — TLT off (long-duration treasury when GLD trend OFF)

```
h15_meta_4way_25a2_25g2_25f1_25e1gld_mom126_tlt_off
```

25% A2 + 25% G2 IEF + 25% F1 stack + 25% E1gld (off=TLTSIM — 20+y UST)

Tests duration extension at OFF-state — TLT vs IEF is more vol but higher carry on disinflation. iter 033 KILL #144 closed rates ORTHOGONALITY (TLT/IEF as gate-source) but here TLT is OFF-STATE asset (different mechanism — passive duration exposure during gate-OFF period).

### H15.4 — Blend off (50% IEF + 50% KMLM)

```
h15_meta_4way_25a2_25g2_25f1_25e1gld_mom126_blend_off
```

25% A2 + 25% G2 IEF + 25% F1 stack + 25% E1gld (off=50% IEFSIM + 50% KMLMSIM)

Linear interpolation between H15.1 and H15.2. iter 016 G1 hybrid found monotonic dose-response IEF > Blend > KMLM for SPY-track. Tests if pattern replicates for GLD-track.

---

## KILL conditions pre-committed

Numbering follows iter 034 (last used: KILL #150). Iter 035 uses #151-#156.

### KILL #151 — META-AXIS CEILING 73 19th confirmation (off-state-axis)

**Trigger**: max H15 score ≤ 73.

**Implication**: 19th meta-axis confirmation across 15 sequential meta-axis iters (sequence 018→035 = 70→71→67→70→70→71→70→69→69→**72**→**72**→**72**→**72**→**73**→**?**). Off-state composition does NOT extend ceiling above 73. The +1pt iter 030/iter 034 breach remains attributable to JOINT optimum (4-way × GOLD × momentum × 126d × IEF off) NOT extensible by varying off-state composition.

### KILL #152 — STRONG-FORM FALSIFICATION (off-state breaks ceiling 73)

**Trigger**: max H15 score ≥ 74 (strict-greater-than 73).

**Implication**: ceiling 73 BROKEN at off-state-axis. NEW Pareto frontier; reopens off-state composition exploration across other constituents. Linear decomposition principle FALSIFIED on positive side at off-state interaction.

### KILL #153 — OFF-STATE-AXIS RUBRIC-SATURATED (9th class of RUBRIC SATURATION)

**Trigger**: max(H15) − min(H15) ≤ 2pt.

**Implication**: Off-state composition is rubric-saturated for GLD constituent. NEW EMPIRICAL PRINCIPLE: at 25% constituent weight within 4-way meta-ensemble, the off-state composition (IEF / KMLM / TLT / Blend) contributes < 2pt to the rubric → 9th class of RUBRIC SATURATION. Mechanism: off-state contributes 25% × (gate_off_freq × off_state_perf_diff); at gate_off_freq ~0.3-0.4 and off-state perf diff ~1-2%/y, the rubric-axis contribution is < 2pt.

### KILL #154 — CRISIS-ALPHA OFF-STATE PROVIDES BONUS (NEW PRINCIPLE TEST)

**Trigger**: H15.2 (KMLM off) ≥ H15.1 (IEF off) by ≥ 1pt.

**Implication**: NEW EMPIRICAL PRINCIPLE: managed-futures crisis-alpha as OFF-STATE asset for orthogonal-asset-class constituent provides Pareto-positive vs IEF baseline at meta-ensemble 4-way structure. Suggests gate-OFF correlation with stress-regime is empirically meaningful for commodity-class signals (gold momentum OFF often during USD-strength regimes that pressure both equities and bond duration).

NOT FIRED if H15.2 < H15.1 → consistent with iter 016 G1 hybrid finding (IEF dominates KMLM at OFF-state for SPY-track) — generalizes to GLD-track.

### KILL #155 — DURATION OFF-STATE DEGRADES (Principle J extension)

**Trigger**: H15.3 (TLT off) < H15.1 (IEF off) by ≥ 1pt.

**Implication**: Long-duration UST (TLT) at OFF-state degrades vs intermediate UST (IEF). Consistent with iter 033 KILL #144 / Principle J that rates orthogonality is sub-rubric — duration extension exposes interest-rate cycle volatility that Pareto-degrades the safe-asset role.

NOT FIRED if H15.3 ≥ H15.1 within ±1pt → duration extension is rubric-neutral at OFF-state position.

### KILL #156 — H15.1 ANCHOR REPRODUCIBILITY SEXTUPLE-REPLICATION (Principle M test)

**Trigger**: H15.1 per-dataset Sharpe matches iter 030 H10.4 (1.041 / 1.037) to 3 decimal places AND CAGR (17.03% / 16.14%) to 2 decimal places AND MDD (33.77% / 33.77%) to 2 decimal places.

**Implication**: Per-config raw metrics confirmed reproducible across SIX independent iters (030/031/032/033/034/035) — strengthens Principle M empirical foundation. Score may shift ±1pt due to grid-composition (iter 034 H14.4 was 73 due to 5-way sibling configs flipping G1 PBO).

NOT FIRED if H15.1 deviates by ≥ 0.01 Sharpe or ≥ 0.05% CAGR or ≥ 0.05% MDD → reproducibility-issue flag (would invalidate iter 030/031/032/033/034 ANCHOR claims under FIXED-STRATEGY assumption).

---

## Expected outcomes

| Config | Expected score | Mechanism |
|---|---:|---|
| H15.1 (IEF off — anchor) | 72-73 | Replicates iter 030 H10.4 strategy spec; rubric noise band per Principle M |
| H15.2 (KMLM off) | 70-72 | iter 016 G1 hybrid pattern: IEF dominates KMLM at OFF-state for SPY-track; expected ≤ IEF baseline |
| H15.3 (TLT off) | 71-73 | Duration extension; depends on rate-cycle alignment with GLD-OFF periods |
| H15.4 (50% IEF + 50% KMLM off) | 71-72 | Linear interpolation between H15.1 and H15.2 |

---

## INCOMPLETE flags

- **Off-state composition for GLD constituent at 4-way meta-ensemble**: NEW interaction-axis empirically untested at this strategy specification; iter 016 G1 hybrid tested off-state for SPY-track stack (no decay) not for GLD-track 3× LETF sleeve.
- **Sleeve INCOHERENCE preserved**: H15.2 / H15.3 / H15.4 still apply GLD-momentum signal to TQQQ-LETF sleeve when ON, only varying OFF-state. Principle C (signal-sleeve incoherence Pareto-positive) held fixed.
- **DSR Bonferroni at n_trials=136**: threshold 0.05/136 = 3.68e-04. Worst per-config DSR p in iter 034 was 6.55e-05 → would PASS Bonferroni 3.68e-04 with **5.61× margin** (slight reduction from iter 034's 5.79× margin due to n_trials 132→136 inflation).
- **PBO grid stability at N=4**: same as iter 026/030/031/032/033/034 (N=4 stabilized PBO). Both datasets PBO PASS strict <0.5 likely preserved. Note Principle M caveat: G1 PBO is grid-level statistic; H15 sibling configs are off-state variants (not 5-way structure changes), so PBO drift may be smaller than iter 034's 0.69→0.11 swing.
- **Tax classification**: meta-blend with E1gld (lrs+momentum at 4th constituent) → annual_realize. Drag observed ~2.0-2.2pp for IEF-off baseline; KMLM/TLT off may shift drag by ±0.1-0.3pp due to different off-state asset return profiles.
- **Synth coverage**: All synths (TQQQSIM, QLDSIM, KMLMSIM, TLTSIM, GLDSIM, IEFSIM, UPROSIM, TMFSIM, UGLSIM, NTSXSIM, GDESIM, SSOSIM, SPYSIM, QQQSIM) in testfolio cache or covered by long_term_portfolio synths. Same coverage as iter 030/031/032/033/034. lh_56y window 1986+ preserved; spy_real 2003+ preserved.
- **No new infra**: reuses 'blend' + 'lrs' (sma + momentum filters with `off_weights` parameter varied) + 'static' spec types from iter 010/014/015/018-034. **771 tests baseline must remain unchanged**. No new TDD required.

---

## Run command

```bash
PYTHONPATH=. python studies/spy_beater_hunt/iterations/035-2026-04-30-H15-meta-ensemble-4way-gld-mom-off-state-composition/backtest.py
```
