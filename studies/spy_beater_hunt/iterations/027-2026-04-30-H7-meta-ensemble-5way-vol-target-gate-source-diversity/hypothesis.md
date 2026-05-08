# Iter 027 — H7 META-ENSEMBLE 5-WAY (vol-target as 5th gate-source)

**Slug**: `H7-meta-ensemble-5way-vol-target-gate-source-diversity`
**Date**: 2026-04-30
**Cumulative n_trials before**: 100 (iter 026 added 4 → total 100)
**Cumulative n_trials after**: 104 (iter 027 adds 4)

---

## Hypothesis

**H7 — 5-way meta-ensemble extends iter 026's gate-source-diversity principle**:
adding vol-target gate (C1) as 5th constituent with maximum gate-source
diversity (A2 QQQ-SMA × G2 SPY-SMA × F1 always-on × E1 TSMOM-6m × C1 vol-target).

This iter is a **FALSIFICATION TEST** of iter 026's linear decomposition principle:

```
4-way score = 71 (3-way ceiling) − 1 base tax + (gate-distinct bonus 0/1) + (CAGR-pass bonus 0 or −3)
```

Generalized prediction (iter 026 KILL #103 + Strategic Option C):

```
5-way score = 71 − 2 base tax + Σ(gate-distinct bonuses) + Σ(CAGR-pass conditional)
```

Maximum 5-way recovery per principle:
- −2pt base 5-way diversification tax (vs 3-way ceiling)
- E1 gate-distinct from A2/G2/F1: +1pt
- C1 gate-distinct from A2/G2/F1/E1: +1pt
- All 5 CAGR-pass: 0 penalty (A2 16.99% / G2 11.85% / F1 13.43% / E1 17.20% / C1 13.54%)
- **Net expected score: 71 − 2 + 2 = 71** (Pareto-co-tied at ceiling) IF principle holds

**Falsification criteria**:
- IF actual_score ≥ 72 → linear decomposition FALSIFIED, ceiling BROKEN → NEW PARETO frontier
- IF actual_score ≤ 70 → linear decomposition CONFIRMED, +1pt gate-distinct bonus is sub-additive at 5-way (additional penalty unobserved at 4-way)
- IF actual_score = 71 → linear decomposition VALIDATED, 11th meta-axis confirmation point

This addresses iter 026's Strategic Option (C) under formal hypothesis testing
(**not** a noise-mining attempt to break ceiling — the test produces useful
information regardless of outcome).

---

## Citations

- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction over multiple alpha streams (5-way meta-ensemble at strategy-level)
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking generalized to 5 distinct gate-sources
- `[systematic_trading, ch.10]` Carver vol-targeting canonical (C1 5th constituent — NEW gate-mechanism: realized-vol-state, distinct from SMA-cross / TSMOM-momentum / always-on)
- Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250 (E1 TSMOM-6m gate-source)
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed 200d SMA gate (A2 QQQ-track + G2 SPY-track LETF F1 — SMA gate-source family)
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha (KMLM in A2/G2/E1 ON-state)
- Bridgewater All-Weather (Dalio 1996) F1 stack ON-state composition
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 104, Bonferroni threshold 4.81e-04
- `[advances_fin_ml, p.208-211]` PBO grid-level N=4 stability
- `[advances_fin_ml, p.31-34]` factor framework — meta-ensemble axis 11th iter (5-way gate-source-diversity falsification test)

---

## Configs (4)

Naming follows iter 026's H6 convention: `h7_meta_<structure>_<weights>_<constituents>`.

### H7.1 — Equal-weight 5-way (canonical falsification config)

```
h7_meta_5way_20a2_20g2_20f1_20e1_20c1
```

20% A2 (QQQ-200d-SMA gate) + 20% G2 IEF (SPY-200d-SMA gate) + 20% F1 stack (always-on) + 20% E1 (TSMOM-6m-QQQ gate) + 20% C1 vol-target SSO (vol-target gate)

**Tests primary hypothesis**: 5-way structure with maximum gate-source diversity matches 3-way ceiling 71.

### H7.2 — Asymmetric 5-way (closest-to-winner-leaning weights)

```
h7_meta_5way_30a2_20g2_20f1_15e1_15c1
```

30% A2 + 20% G2 IEF + 20% F1 stack + 15% E1 + 15% C1 vol-target

A2-dominant; preserves iter 026's H6.4 asymmetric pattern (30%-leaning to closest-to-winner LRS-mono) extended to 5-way. Tests if asymmetric weights can recover the 5-way base tax.

### H7.3 — 4-way substituting E1 with C1 (gate-mechanism comparison)

```
h7_meta_4way_25a2_25g2_25f1_25c1
```

25% A2 + 25% G2 IEF + 25% F1 stack + 25% C1 vol-target (no E1; C1 as 4th distinct gate-source)

Tests if vol-target gate as 4th constituent matches E1 TSMOM gate (iter 026 H6.1 reached 71). C1 has lower solo Sharpe (0.72) vs E1 (0.75) but represents a fundamentally distinct gate-mechanism (vol-state vs trend).

### H7.4 — 3-way substituting F1 with C1 (always-on vs vol-target gate test)

```
h7_meta_3way_33a2_33g2_34c1
```

33% A2 + 33% G2 IEF + 34% C1 vol-target (no F1; C1 replaces F1 stack)

Direct test of iter 025 KILL #97 + iter 026 KILL #104 generalization (F1 stack's always-on natural-diversification advantage). Predicts score < 71 if F1 advantage is structural; score = 71 if vol-target gate provides equivalent decorrelation.

---

## KILL conditions pre-committed

Numbering follows iter 026 (last used: KILL #105). Iter 027 uses #106-#110.

### KILL #106 — Linear decomposition FALSIFICATION (HARD test)

**Trigger**: max H7 score ≥ 72 (strict-greater-than 71 ceiling).

**Implication**: linear decomposition principle established in iter 026 is FALSIFIED. Additional gate-sources contribute super-linearly at 5-way structure. NEW PARETO frontier; ceiling no longer at 71. Re-open exploration of 6-way / cross-product hybrids at N≥5 constituent count.

### KILL #107 — Linear decomposition CONFIRMATION (negative case)

**Trigger**: max H7 score ≤ 70.

**Implication**: 5-way structure pays MORE than +1pt per gate-source-distinct bonus (sub-additive). Linear decomposition is an upper-bound, not exact. Ceiling 71 DEFINITIVE across 11 meta-axis iters (10th already confirmed + this 11th). Strengthens mandate §1 case.

### KILL #108 — 5-way equal-weight CEILING-TIE confirmation

**Trigger**: H7.1 (equal-weight 5-way) score ≥ 71.

**Implication**: linear decomposition VALIDATED on positive-axis (gate-source-diversity bonuses can recover 5-way base tax to net 0). Both iter 026 H6.1 (4-way 25/25/25/25 with E1) AND iter 027 H7.1 (5-way 20/20/20/20/20 with E1+C1) TIE 3-way ceiling. The ceiling is robust to constituent-count variations within Pareto-co-apex.

### KILL #109 — Vol-target vs TSMOM as 4th constituent gate-source

**Trigger**: H7.3 (4-way A2/G2/F1/C1) score ≥ H7.1 (5-way A2/G2/F1/E1/C1) by ≥ 1pt.

**Implication**: vol-target gate is structurally PREFERRED over TSMOM gate at 4-way (4-way C1 only > 5-way C1+E1) → iter 026 H6.1's E1 inclusion was sub-optimal vs C1 alternative. Suggests gate-mechanism distinctness (vol-state vs trend-state) > signal-asset distinctness for 4-way decorrelation.

NOT FIRED if H7.3 score < H7.1 by ≥ 1pt → TSMOM-gate ≥ vol-target-gate within meta-axis (iter 026 E1 inclusion validated retrospectively).

### KILL #110 — Vol-target gate substitutability for always-on F1 stack

**Trigger**: H7.4 (3-way w/ C1 substituting F1 stack) score ≥ 71.

**Implication**: vol-target gate provides equivalent natural-diversification to F1 stack's always-on multi-asset structure → F1 stack's natural-diversification advantage (iter 025 KILL #97 / iter 026 KILL #104) is SHARED, not unique. Re-opens question of best 3rd constituent in 3-way meta-ensemble.

NOT FIRED if H7.4 score < 71 by ≥ 1pt → F1 stack's natural-diversification advantage as 3rd constituent confirmed unique-or-Pareto-dominant (iter 025 KILL #97 / iter 026 KILL #104 generalization holds).

---

## Expected outcomes

| Config | Expected score | Mechanism |
|---|---:|---|
| H7.1 (5-way equal) | 70-71 | Linear decomposition: 71 − 2 + 2 (E1 + C1 gate-distinct) |
| H7.2 (5-way asymm) | 70-71 | Same as H7.1 ± weight effect (asymmetric weight may add ~+0pt or ~+1pt MDD-axis) |
| H7.3 (4-way C1) | 70-71 | Per iter 026 KILL #102 generalization: C1 gate-distinct from G2/A2/F1 → +1pt bonus, est 71 |
| H7.4 (3-way C1) | 67-69 | Per iter 025 KILL #97 / iter 026 KILL #104: F1 stack's natural-div advantage as 3rd constituent expects ~−2pts loss |

---

## INCOMPLETE flags

- **C1 vol-target's solo Sharpe (0.72) < E1 (0.75) < G3 (0.895)**: 5-way Sharpe-axis penalty may exceed iter 026's. May trigger Sharpe-axis-saturation iter 026 KILL #102 generalization at 5-way structure. Sharpe blend between 0.95-1.00 likely.
- **C1 solo MDD (46.78% lh / 36.94% spy, mean 41.86%)**: HIGHEST among 5 constituents. Will pull 5-way blend MDD up; may trigger iter 024 MDD-anchor saturation at ~35% blend MDD. MDD-axis penalty −1 to −2pt vs iter 019/026.
- **DSR Bonferroni at n_trials=104**: threshold 0.05/104 = 4.81e-04. Worst per-config DSR p ≤ 2.27e-04 (iter 026 spy_real) likely preserved at 5-way blend (Sharpe ~0.94-0.96 maintained). Should pass strict <0.05 with margin BUT Bonferroni only marginally.
- **PBO grid stability at N=4**: same as iter 026 (N=4 stabilized PBO vs iter 025 N=5). Both datasets PBO PASS strict <0.5 likely preserved.
- **Tax classification**: meta-blend with C1 (vol_target) → annual_realize. Drag observed ~1.91-2.07pp comparable to iter 019/026.
- **Vol-target signal compute time**: each blend evaluation must compute realized vol on 60-day rolling window for SPYSIM lagged 1 day. Backtest runtime may be 10-15% longer vs iter 026.
- **Synth-vs-real consistency**: vol-target on SPYSIM synth pre-2003 has higher noise on 60d realized-vol (vs Tiingo real data 2003+). Cross-lib delta may widen ±0.5pp on lh_56y vs iter 026.

---

## No new infra

Reuses existing spec types from iter 026:
- `blend` (4-way / 3-way) — preserved from iter 026 H6
- `lrs` (sma + momentum filters) — A2 QQQ-track, G2 SPY-track, E1 TSMOM-6m
- `static` — F1 stack
- `vol_target` — C1 (NEW in this iter to meta-ensemble axis; reused from iter 010 standalone)

771 tests baseline must remain unchanged. No new TDD required.

---

## Run command

```bash
PYTHONPATH=. python studies/spy_beater_hunt/iterations/027-2026-04-30-H7-meta-ensemble-5way-vol-target-gate-source-diversity/backtest.py
```
