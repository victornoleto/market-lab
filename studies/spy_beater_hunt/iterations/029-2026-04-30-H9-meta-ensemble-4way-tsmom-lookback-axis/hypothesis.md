# spy_beater_hunt iter 029 — H9 META-ENSEMBLE 4-WAY GATE-LOOKBACK AXIS — TSMOM lookback variation

**Slug**: `H9-meta-ensemble-4way-tsmom-lookback-axis`
**Date**: 2026-04-30
**Cumulative n_trials**: prior 108 (iter 028) + 4 (this iter) = **112**

---

## Context (state-of-the-hunt at iter 028)

iter 028 introduced the **POSITION-INVARIANCE PRINCIPLE** (KILL #114): meta-axis rubric output (Sharpe / CAGR / MDD / score) depends ONLY on the **constituent set composition** and **total weights**, NOT on which position each constituent occupies. iter 028's H8.4 INVERTED (E1↔A2 swap between 1st-30% and 4th-20% positions in iter 026 H6.4 framework) yielded metrics within numerical noise of iter 026 H6.4 (CAGR Δ −0.01pp, MDD Δ −0.50pp, Sharpe Δ −0.002).

**Current Pareto-frontier at meta-axis ceiling 71** (3 architectural points):
- **iter 019 H2** (3-way 33/33/34): MDD-Sharpe-leaning (Sharpe 1.025, MDD 28.50%, CAGR 15.04%) → 71
- **iter 026 H6.4** (4-way 30a2_25g2_25f1_20e1): CAGR-Robustness-leaning (Sharpe 0.956, MDD 32.57%, CAGR 15.85%) → 71
- **iter 028 H8.4** (4-way 30e1_25g2_25f1_20a2 INVERTED): position-symmetric duplicate of iter 026 H6.4 → ~71

iter 028 closed the position-permutation sub-axis as RUBRIC-NEUTRAL. **Future iters should focus on constituent-set composition or weight-distribution variations within fixed constituent set, OR introduce NEW constituents (gate types not yet tested)**.

iter 028 strategic option (C) **gate-mechanism axis EXPANSION** (E2 TSMOM-12m, E3 TSMOM-3m, breadth/VIX gates) — MEDIUM credibility, LOW-MEDIUM cost — was flagged untested. Iter 029 explores the **TSMOM-lookback sub-axis** within the gate-mechanism axis:

- iter 026 used **E1 = TSMOM-6m-QQQ-gate** (lookback 126 trading days) at 4th constituent position with 20% weight, yielding score 71 (CAGR-Robustness Pareto-co-apex).
- **OPEN question**: does varying the TSMOM lookback (12m, 3m) at the 4th constituent slot move the Pareto-frontier?
- Citation: `[Moskowitz-Ooi-Pedersen, 2012]` Time Series Momentum, JFE 104(2):228-250 — **canonical 12m lookback**, with 1m/3m/6m/9m robustness checks. For single-asset Faber-GTAA-equivalent timing, 6-10m is canonical (Faber `[ivy_portfolio]`).

---

## Hypothesis

**H9 (gate-lookback rubric-effect)**: Varying the TSMOM lookback in the 4th constituent (E1 → E2 = TSMOM-12m / E3 = TSMOM-3m) within iter 026 H6.4's framework (`30a2_25g2_25f1_20e_X`) and iter 026 H6.1's framework (`25a2_25g2_25f1_25e_X`) produces:

1. **Strong-form**: max H9 > 71 strict → 12m or 3m lookback unique-Pareto-superior to 6m → meta-axis ceiling 71 FALSIFIED.
2. **Medium-form**: max H9 within ±1pt of iter 026 H6.4 71 (i.e., {70, 71, 72}) → gate-lookback rubric-saturated within meta-axis; sub-axis CLOSED.
3. **Weak-form**: max H9 < 70 → 6m TSMOM lookback rubric-optimal vs 12m/3m → 6m is the empirical local-optimum.

Mechanism rationale:
- **TSMOM-12m**: longer lookback lags inflection points (slower entry/exit at trend reversals), but smoother (less whipsaw). Per Moskowitz et al. (2012), 12m strongest for cross-asset TSMOM. For single-asset Faber-GTAA equivalent on QQQ, 12m may exit later in 2008/2022 (deeper drawdown captured) but enter later in recoveries.
- **TSMOM-3m**: shorter lookback responds faster to trend shifts, capturing inflection earlier. Cost: noisier signal → more whipsaw, especially in choppy regimes. Solo CAGR likely lower; solo MDD likely higher (deeper drawdowns from late re-entry after whipsaw).
- **TSMOM-6m (E1 baseline)**: middle-ground; preserves Sharpe via moderate lookback but exits late in fast crashes.

Expected outcome under medium-form: 12m and 3m lookbacks yield similar blend metrics to E1 6m within ±1pt rubric tolerance → gate-lookback sub-axis CLOSED at 71.

---

## Pre-committed KILL conditions (numbered after iter 028's #115)

### KILL #116 — META-AXIS CEILING FALSIFICATION (strong form)
**Trigger**: max H9 score > 71 strict (i.e., ≥ 72).
**Implication if FIRED**: meta-axis ceiling 71 FALSIFIED at gate-lookback variation. New ceiling established. closest-to-winner UPDATED if H9 max ≥ 72.

### KILL #117 — META-AXIS CONFIRMATION (13th sequential meta-axis iter)
**Trigger**: max H9 score ≤ 71 (medium-or-weak-form).
**Implication if FIRED**: 13th meta-axis confirmation point (sequence 018→019→020→021→025→026→027→028→**029** = 70→71→67→70→70→71→70→69-selected/71-est→**?**). Ceiling 71 strengthens.

### KILL #118 — TSMOM-12M-DOMINANCE (gate-lookback monotone increase)
**Trigger**: H9.1 (E2 12m, 20% weight) score > H9.3 (E2 12m, 25% weight) AND > E1-equivalent at iter 026 H6.4's 71 by ≥ +1pt.
**Implication if FIRED**: TSMOM-12m at LOW dose (20%) Pareto-dominates over both higher dose AND iter 026 H6.4's 6m baseline → 12m is canonically-superior lookback at the 4th constituent slot, paralleling Moskowitz-Ooi-Pedersen literature.

### KILL #119 — 6M-LOOKBACK-OPTIMAL (gate-lookback inverted-U)
**Trigger**: max H9 < iter 026 H6.4's 71 (i.e., max H9 ≤ 70).
**Implication if FIRED**: TSMOM-6m is empirically near-optimal lookback for the 4th-constituent gate-mechanism slot within meta-axis. 12m too slow / 3m too whippy → 6m is the local Pareto optimum. **NEW PRINCIPLE**: gate-lookback axis follows inverted-U with peak at ~6m for QQQ TSMOM in meta-ensemble blend context.

### KILL #120 — RUBRIC-SATURATION (gate-lookback flat)
**Trigger**: max H9 ∈ {70, 71} (within ±1pt of iter 026 H6.4 71) AND no config exceeds 71 strict.
**Implication if FIRED**: gate-lookback sub-axis is RUBRIC-SATURATED within meta-axis 4-way structure. Further TSMOM-lookback exploration (e.g., 9m, 18m) bounded by ±1pt rubric-noise. Sub-axis CLOSED. **7th class of RUBRIC SATURATION** documented (after iter 020/021/023/024/025/026 prior classes).

---

## Configurations (4 configs — keeps n_trials slow per iter 028 SPEC §NOTE)

All configs use iter 026's `A2_CLOSEST_SPEC` + `G2_IEF_SPEC` + `F1_STACK_SPEC` verbatim, varying only the 4th constituent's TSMOM lookback:

- **E2_TSMOM12M_SPEC**: identical to E1_TSMOM6M_SPEC except `lookback_days=252` (~12 calendar months)
- **E3_TSMOM3M_SPEC**: identical to E1_TSMOM6M_SPEC except `lookback_days=63` (~3 calendar months)

| config | weight A2 | weight G2 | weight F1 | weight E2/E3 | gate-lookback | comparison baseline |
|---|---:|---:|---:|---:|---|---|
| `h9_meta_4way_30a2_25g2_25f1_20e2` | 0.30 | 0.25 | 0.25 | 0.20 (E2 12m) | TSMOM-12m | iter 026 H6.4 71 (CAGR-Robustness Pareto-co-apex) |
| `h9_meta_4way_30a2_25g2_25f1_20e3` | 0.30 | 0.25 | 0.25 | 0.20 (E3 3m)  | TSMOM-3m | iter 026 H6.4 71 |
| `h9_meta_4way_25a2_25g2_25f1_25e2` | 0.25 | 0.25 | 0.25 | 0.25 (E2 12m) | TSMOM-12m | iter 026 H6.1 ~71 (equal-weight CAGR-Robustness) |
| `h9_meta_4way_25a2_25g2_25f1_25e3` | 0.25 | 0.25 | 0.25 | 0.25 (E3 3m)  | TSMOM-3m | iter 026 H6.1 ~71 |

Total: **4 configs, n_trials += 4 → cumulative 112**.

---

## Expected outcomes

| outcome | predicted | KILL fired |
|---|---|---|
| max H9 ≥ 72 | UNLIKELY (~10%) — meta-axis ceiling solid across 8 sequential iters | KILL #116 |
| max H9 = 71 (TIE iter 026) | POSSIBLE (~25%) — gate-lookback rubric-saturated, equivalent contribution | KILL #117, #120 |
| max H9 = 70 | LIKELY (~40%) — moderate degradation from 6m lookback dispersion | KILL #117, #119 |
| max H9 < 70 | POSSIBLE (~25%) — significant degradation if 12m too slow / 3m too whippy | KILL #117, #119 |

**Most likely**: max H9 ∈ {70, 71}, KILL #117 + KILL #120 fire. **NEW EMPIRICAL PRINCIPLE expected**: gate-lookback within meta-axis 4-way structure is **RUBRIC-SATURATED** at ±1pt around the 6m baseline (E1 → E2/E3 within ±1pt). 7th class of rubric saturation.

---

## INCOMPLETE flags

- **Synth caveats**: TQQQSIM/QLDSIM/UPROSIM/TMFSIM/UGLSIM/IEFSIM/KMLMSIM/TLTSIM/NTSXSIM/GDESIM all reused from iter 026 cache. No new synth required.
- **Tax classification**: meta-blend with TSMOM-gate constituent (lrs filter type) → annual_realize per iter 026 H6.4 pattern. Drag expected ~1.86-2.0pp (consistent with iter 019/026/027/028 mean drag).
- **DSR Bonferroni at n_trials=112**: threshold 0.05/112 = 4.46e-04. Worst per-config DSR p must remain < 4.46e-04 for strict-multiple-comparison validity. Single-comparison threshold <0.05 expected with margin.
- **PBO N=4 grid stability**: paralleling iter 026 N=4 (lh 0.0 / spy 0.004 strict <0.5). Expected stable.
- **NO new infra**: reuses 'blend' + 'lrs' (sma + momentum filters with varied lookback_days) + 'static' spec types from iter 014/018-028. **771 tests baseline preserved**.
- **Position-invariance from iter 028 KILL #114 applied**: configs use 4th-position weight 20% / 25% but position assignment is NEUTRAL per iter 028 finding. Selection rule will pick max(Sharpe / SPY_Sharpe).

---

## Citations

- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction over multiple alpha streams (4-way meta-ensemble at strategy-level, 13th iter to meta-axis with gate-lookback sub-axis exploration)
- **Moskowitz-Ooi-Pedersen (2012) Time Series Momentum, JFE 104(2):228-250** — primary citation for E2 TSMOM-12m lookback; canonical 12m test across 1m/3m/6m/9m/12m robustness
- `[ivy_portfolio]` Faber GTAA — single-asset 10-month moving average; 6-12m equivalent for QQQ-track timing (E1 6m / E2 12m bracket)
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed 200d SMA gate — A2 + G2 SMA-200 baseline preserved
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking — F1 stack always-on retained at 3rd constituent (uniquely-Pareto-optimal per iter 027 KILL #110 quadruple confirmation)
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha — KMLM in A2/G2/E2/E3 ON-state
- Bridgewater All-Weather (Dalio 1996) — F1 stack ON-state retained
- `[advances_fin_ml, p.222-223]` DSR with cumulative_n_trials = 112 (Bonferroni 4.46e-04)
- `[advances_fin_ml, p.208-211]` PBO grid-level N=4 stability
- `[advances_fin_ml, p.196-202]` Bootstrap CI (G6 implicit via gates count)
- `[advances_fin_ml, p.31-34]` Cross-lib factor framework (G7 implicit via gates count)

---

## Strategic context (per iter 028 mandate §1 + §7 framing)

This iter explicitly tests the **only remaining credible architectural sub-axis** identified in iter 028 strategic options as Option (C). All other paths (B = CAPE-timing untested but LOW credibility; D = rubric-revision pending user decision) require user-driven directional change. Within mandate §1 MAINTENANCE MODE, this iter executes the LOWEST-cost LOWEST-risk untested sub-axis to definitively close or open the gate-lookback exploration window before recommending hunt closure at iter 030+.

Hunt at 28/50 iters = 56% utilization. Iter 029 + ≤3 follow-up iters (if H9 opens) brings hunt to ~62% utilization with 19/50 iters remaining for any new directions surfaced by user mandate §7 review.
