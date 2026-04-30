# Iter 034 — H14 META-ENSEMBLE 5-WAY (GLD-mom-126d as 5th constituent)

**Slug**: `H14-meta-ensemble-5way-gld-mom-as-5th-constituent`
**Date**: 2026-04-30
**Cumulative n_trials before**: 128 (iter 033 ended at 128)
**Cumulative n_trials after**: 132 (iter 034 adds 4)

---

## Hypothesis

**H14 — does GLD-momentum-126d's +1pt bonus (Principle A, iter 030 KILL #125 → revised to GOLD-SPECIFIC per Principle J, iter 033 KILL #144) survive being added as a 5th constituent on top of iter 027's 5-way base tax (KILL #107)?**

This is **Strategic Option C from iter 033 final report** — the only feasible single-axis test without new data infrastructure (Options B/D/E require SLV/DBC/BCOM/DXY synth integration NOT in testfolio cache).

### Mechanism + linear-decomposition prediction

iter 027 H7.1 (5-way 20%A2 + 20%G2 + 20%F1 + 20%E1qqq-mom-6m + 20%C1-vol-target) scored 70 (KILL #107 FIRED, 5-way base tax = -1pt vs 4-way ceiling 71 = expected 70 if linear).

iter 030 H10.4 (4-way 25%A2 + 25%G2 + 25%F1 + 25%E1gld-mom-126) scored 72 (KILL #125 FIRED, +1pt Principle A bonus over iter 026 H6.1 baseline 71).

The H14 prediction under linear decomposition (iter 026 KILL #103 generalization):

```
5-way score = 71 (4-way E1qqq baseline) − 1 base 5-way tax + Σ(gate-distinct bonuses)
            = 71 − 1 + (E1gld GOLD-SPECIFIC bonus +1) = 71  (Pareto-co-tied at 4-way ceiling)
```

If GLD-mom Principle A bonus is dose-additive at 5-way (NOT consumed by 5-way base tax),
score could reach 72 (matching iter 030 4-way apex). If linear decomposition holds with
sub-additive 5-way penalty, score could be 70-71.

**Falsification criteria**:
- IF max H14 score ≥ 73 → strong-form falsification: ceiling 72 BROKEN at 5-way × GOLD axis
- IF max H14 score = 72 → Pareto-co-tied: GLD bonus FULLY survives 5-way base tax
- IF max H14 score = 71 → linear decomposition VALIDATED: GLD bonus +1 partially compensates 5-way -1
- IF max H14 score ≤ 70 → 5-way base tax DOMINATES even with GLD bonus → 5-way structurally inferior

This addresses iter 033's Strategic Option C under formal hypothesis testing
(**not** noise-mining — produces useful information regardless of outcome by mapping
the interaction surface between Principle A bonus and iter 027 KILL #107 5-way base tax).

---

## Citations

- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction over multiple alpha streams (5-way meta-ensemble at strategy-level, **18th iter at meta-axis**, NEW interaction sub-axis: 5-way × GOLD)
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking generalized to 5 distinct gate-sources
- Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 (E1 TSMOM-126d gate-source on QQQ + GLD)
- Asness-Moskowitz-Pedersen (2013) Value and Momentum Everywhere, JoF 68(3):929-985 (momentum across asset classes — gold-momentum vs equity-momentum stacked at 4th + 5th positions)
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed 200d SMA gate (A2 QQQ-track + G2 SPY-track LETF)
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha (KMLM in A2/G2/E1 ON-state)
- Bridgewater All-Weather (Dalio 1996) F1 stack ON-state composition
- `[systematic_trading, ch.10]` Carver vol-targeting canonical (C1 in H14.3 only)
- iter 026 KILL #102 (gate-source-distinctness +1pt at 4-way) — extended to 5-way × GOLD
- iter 026 KILL #103 (linear decomposition principle) — UPPER-BOUND prediction model
- iter 027 KILL #107 (5-way base tax confirmed at C1 substitution) — challenged here with GLD as 5th
- iter 030 KILL #125 (Principle A) — revised to Principle J (GOLD-SPECIFIC) per iter 033 KILL #144
- iter 031 KILL #130 (Principle D — TSMOM-lookback inverted-U asset-invariant peak at 6m / 126d) — held fixed at 126d
- iter 032 KILL #135 (Principle G — orthogonality bonus filter-type-coupled to momentum) — held fixed at filter=momentum
- iter 033 KILL #144 (Principle J — orthogonality bonus is COMMODITY-GOLD-SPECIFIC) — operative for GLD-mom-126d 5th constituent
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 132, Bonferroni threshold 0.05/132 = 3.79e-04
- `[advances_fin_ml, p.208-211]` PBO grid-level N=4 stability

---

## Configs (4)

Naming follows iter 027 H7 convention extended with `gld` suffix to mark GLD-mom-126d 5th constituent.

### H14.1 — 5-way equal-weight (E1qqq@4th + E1gld@5th) — PRIMARY FALSIFICATION TEST

```
h14_meta_5way_20a2_20g2_20f1_20e1qqq_20e1gld_mom126
```

20% A2 (QQQ-200d-SMA gate) + 20% G2 IEF (SPY-200d-SMA gate) + 20% F1 stack (always-on) + 20% E1qqq (TSMOM-126d-QQQ gate) + 20% E1gld (TSMOM-126d-GLD gate)

**Tests primary hypothesis**: does GLD-mom-126d at 5th constituent retain its +1pt Principle A bonus despite 5-way base tax?

### H14.2 — 5-way GLD-heavy (asymmetric)

```
h14_meta_5way_20a2_20g2_20f1_15e1qqq_25e1gld_mom126
```

20% A2 + 20% G2 IEF + 20% F1 stack + 15% E1qqq + 25% E1gld

GLD signal at 25% (vs QQQ signal at 15%) — tests dose-response of Principle A bonus at 5-way structure. If GLD bonus is dose-additive, asymmetric weight should outperform equal-weight.

### H14.3 — 5-way C1 vol-target@4th + E1gld@5th (gate-mechanism comparison)

```
h14_meta_5way_20a2_20g2_20f1_20c1_20e1gld_mom126
```

20% A2 + 20% G2 IEF + 20% F1 stack + 20% C1 (vol-target SSO) + 20% E1gld (GLD-mom-126d)

Replaces E1qqq with C1 vol-target as 4th constituent — distinct gate-mechanism (realized-vol-state) + GLD-mom-126d (TSMOM gate on commodity). Tests if vol-target gate at 4th position pairs better with GLD-orthogonality bonus than QQQ-momentum at 4th. iter 027 H7.1 (with C1+E1qqq) was 70; this config replaces E1qqq with E1gld.

### H14.4 — 4-way ANCHOR replicate (sanity check)

```
h14_meta_4way_25a2_25g2_25f1_25e1gld_mom126
```

25% A2 + 25% G2 IEF + 25% F1 stack + 25% E1gld (TSMOM-126d-GLD)

QUINTUPLE-replication anchor of iter 030 H10.4 / iter 031 H11.2 / iter 032 H12.1 / iter 033 H13.2. Should produce score 72 IDENTICAL to those iters (measurement reproducibility verification across 5 independent iters).

---

## KILL conditions pre-committed

Numbering follows iter 033 (last used: KILL #144). Iter 034 uses #145-#150.

### KILL #145 — META-AXIS CEILING 72 18th confirmation (5-way × GOLD axis)

**Trigger**: max H14 score ≤ 72.

**Implication**: 18th meta-axis confirmation across 14 sequential meta-axis iters (sequence
018→019→020→021→025→026→027→028→029→030→031→032→033→034 = 70→71→67→70→70→71→70→69→69→**72**→**72**→**72**→**72**→**72**). 5-way structure with GLD-mom-126d does NOT extend ceiling above 72. The +1pt iter 030 breach remains attributable to JOINT optimum (4-way × GOLD × momentum × 126d) NOT extensible by adding constituent count.

### KILL #146 — STRONG-FORM FALSIFICATION (5-way breaks ceiling 72)

**Trigger**: max H14 score ≥ 73 (strict-greater-than 72).

**Implication**: ceiling 72 BROKEN at 5-way × GOLD axis. NEW Pareto frontier; reopens N≥5 / cross-product hybrid exploration. Linear decomposition principle FALSIFIED on positive side at 5-way × GOLD interaction.

### KILL #147 — 5-WAY BASE TAX FALSIFIED FOR GLD-MOM (positive case)

**Trigger**: H14.1 (5-way equal-weight 20/20/20/20/20 with E1qqq+E1gld) score ≥ 72.

**Implication**: 5-way base tax (iter 027 KILL #107) is signal-asset-DEPENDENT — GLD-mom Principle A bonus (+1pt) FULLY compensates for 5-way base tax (-1pt). NEW EMPIRICAL PRINCIPLE: 5-way structures with GOLD-SPECIFIC orthogonality at 5th constituent retain ceiling. Generalization: Principle A bonus is constituent-count-invariant.

NOT FIRED if H14.1 < 72 → 5-way base tax CONFIRMED to dominate even with GLD bonus → Principle A is constituent-count-COUPLED.

### KILL #148 — GLD DOSE-RESPONSE AT 5-WAY (NEW PRINCIPLE TEST)

**Trigger**: H14.2 (GLD at 25%) > H14.1 (GLD at 20%) by ≥ 1pt.

**Implication**: Principle A bonus is DOSE-ADDITIVE — heavier GLD weight at 5th amplifies bonus. Suggests +1pt is conservative lower bound; dose-response curve may extend.

NOT FIRED if |H14.2 − H14.1| < 1pt → bonus is BINARY (presence/absence), NOT dose-additive. Consistent with iter 030 H10.3 (20%) and H10.4 (25%) both tying at 72.

### KILL #149 — VOL-TARGET-AT-4TH + GLD-AT-5TH PARETO-COMPARISON

**Trigger**: H14.3 (vol-target+GLD) ≥ H14.1 (E1qqq+GLD) by ≥ 1pt.

**Implication**: vol-target gate-mechanism (realized-vol-state) preserves more 5-way diversity bonus than TSMOM-on-QQQ at 4th position. Suggests gate-mechanism distinctness > signal-asset same-class redundancy. Reopens iter 027 KILL #109 NOT FIRED interpretation under GLD-orthogonality conditioning.

NOT FIRED if H14.3 < H14.1 by ≥ 1pt → TSMOM-on-QQQ preferred over vol-target at 4th when paired with GLD at 5th → Principle A bonus prefers TSMOM-paired-companion.

### KILL #150 — H14.4 SANITY CHECK (4-WAY ANCHOR REPLICATION)

**Trigger**: H14.4 (4-way iter 030 H10.4 replicate) selected score = 72 AND per-dataset Sharpe matches iter 030 H10.4 (1.041 / 1.037) to 3 decimal places.

**Implication**: measurement consistency confirmed across 5 independent iters (iter 030/031/032/033/034). QUINTUPLE-replication establishes iter 030 measurement as REPRODUCIBLE (vs noise / measurement drift).

NOT FIRED if H14.4 deviates by ≥ 0.01 Sharpe or ≥ 0.5pt score → reproducibility-issue flag (would invalidate iter 030/031/032/033 ANCHOR claims).

---

## Expected outcomes

| Config | Expected score | Mechanism |
|---|---:|---|
| H14.1 (5-way E1qqq+E1gld equal) | 71-72 | 71 − 1 base 5-way tax + 1 GLD Principle A bonus = 71 (linear); or 72 if GLD bonus is constituent-count-invariant |
| H14.2 (5-way GLD-heavy 15/25) | 71-72 | Same as H14.1 ± dose-response effect (likely 0 net per iter 030 binary bonus pattern) |
| H14.3 (5-way C1+E1gld equal) | 70-72 | 71 − 1 base 5-way tax + 1 GLD bonus + (vol-target gate-mech bonus 0 to +1) = 70-72 |
| H14.4 (4-way GLD anchor sanity) | 72 (IDENTICAL to iter 030/031/032/033) | QUINTUPLE-replication |

---

## INCOMPLETE flags

- **5-way GLD-mom-126d at 5th constituent**: NEW interaction-axis empirically untested; iter 027 H7.1 tested 5-way with C1 (vol-target) at 5th, NOT GLD. iter 033 tested 4-way with TLT/IEF rates at 4th, NOT 5-way.
- **20% E1qqq + 20% E1gld asymmetry within 5-way**: total signal-source weight at 4th+5th = 40%, vs iter 030 H10.4's 25% E1gld at 4th = 25%. The H14.1 / H14.2 configs OVER-WEIGHT signal-source group vs iter 030 anchor — may amplify or dilute the bonus.
- **DSR Bonferroni at n_trials=132**: threshold 0.05/132 = 3.79e-04. Worst per-config DSR p in iter 033 was 6.55e-05 → would PASS Bonferroni 3.79e-04 with 5.79× margin (slight reduction from iter 033's 6.0× margin due to n_trials 128→132 inflation).
- **PBO grid stability at N=4**: same as iter 026/030/031/032/033 (N=4 stabilized PBO). Both datasets PBO PASS strict <0.5 likely preserved.
- **Tax classification**: meta-blend with E1gld (lrs+momentum) AT 5TH + E1qqq OR C1 at 4th → annual_realize. Drag observed ~2.0-2.2pp comparable to iter 027/030/031/032/033.
- **C1 vol-target signal compute time** (H14.3 only): each blend evaluation must compute realized-vol on 60-day rolling window for SPYSIM lagged 1 day. Backtest runtime may be 5-10% longer than H14.1/H14.2/H14.4 (iter 027 noted 10-15% longer with 5-way C1).
- **Synth coverage**: All synths (TQQQSIM, QLDSIM, KMLMSIM, TLTSIM, GLDSIM, IEFSIM, UPROSIM, TMFSIM, UGLSIM, NTSXSIM, GDESIM, SSOSIM, SPYSIM, QQQSIM) are in testfolio cache or covered by long_term_portfolio synths (TMFSIM via tmf_synth_returns_from_cache). Same coverage as iter 030/031/032/033. lh_56y window 1986+ preserved; spy_real 2003+ preserved.
- **No new infra**: reuses 'blend' + 'lrs' (sma + momentum filters) + 'static' + 'vol_target' (H14.3 only) spec types from iter 010/014/015/018-033. **771 tests baseline must remain unchanged**. No new TDD required.

---

## Run command

```bash
PYTHONPATH=. python studies/spy_beater_hunt/iterations/034-2026-04-30-H14-meta-ensemble-5way-gld-mom-as-5th-constituent/backtest.py
```
