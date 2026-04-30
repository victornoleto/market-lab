# spy_beater_hunt iter 017 — G2: Regime-Gated Levered All-Weather LETF 2× (THIRD cross-product hybrid)

**Date**: 2026-04-30
**Type**: Post-impossibility 3rd cross-product hybrid sanity check on KILL #33 (architectural ceiling). Bridges iter 014 (3× LETF, decay-heavy, gate × sleeve NEGATIVE) and iter 016 (1.41× stack, no-decay, gate × sleeve MIXED). Tests intermediate decay regime: 2.25× LETF, ~3-4%/y decay drag.
**Slug**: `G2-regime-gated-levered-all-weather-letf2x`
**Status of hunt entering this iter**: `closed_no_winner` (iter 011 IMPOSSIBILITY_RESULT, reinforced through iter 016 across 8 fams + 2 hybrids).

---

## Why this iter exists (context)

Iter 016 (G1 hybrid, SMA × F1-stack at 1.41× no-decay) **path-to-90 analysis explicitly enumerated the untested prediction**:

> "Adding regime gate to LETF 2x F1: predicted CAGR up ~1pp via bear miss,
>  MDD down ~5-10pp, Sharpe down ~0.05 (LETF whipsaw). Net G1-LETF
>  estimated 60-65 — same architectural ceiling."
>  — iter 016 final_report.md (Path to score 90 G1 architecture)

This iter tests that prediction empirically. It also fills a critical gap in the gate × decay interaction surface:

| iter | sleeve         | notional | decay drag | gate × sleeve interaction      | best score |
|:-----|:---------------|---------:|-----------:|:-------------------------------|-----------:|
| 014  | TQQQ split LETF | 3.00×    | ~3-5%/y    | NEGATIVE (cross-prod < union)  | 65         |
| 016  | F1 stack       | 1.41×    | ~0%/y      | MIXED (Sharpe+MDD+Gates +; CAGR+Rob −) | 61 |
| **017** | **F1 LETF 2× (G2)** | **2.25×** | **~3-4%/y** | **? (THIS ITER)**       | **?**      |

The gate × decay interaction surface has TWO data points; iter 017 supplies the THIRD (intermediate-decay regime). If KILL #33 holds across decay axis, the cross-product score will cap ≤ 67 regardless of decay level. If the gate × decay × leverage interaction has a sweet spot at moderate decay, score could break through.

Iter 015 already demonstrated `f1_aw_letf_2x` (always-on, no gate) PASSES all 3 strict bars (CAGR 16.36%, MDD 43.53%, gates 5+5, Sharpe 0.90). Adding a 200d SMA gate to that sleeve probes whether the gate's bear-avoidance complements the multi-asset diversification at moderate-decay LETF leverage.

---

## Hypothesis

**H₁ (primary, KILL #54 path)**: G2 score caps ≤ 67. Architectural ceiling generalizes across the **third decay regime** (2.25× LETF moderate-decay), reinforcing KILL #33 from "8 fams + 2 hybrids" to "8 fams + 3 hybrids".

**H₂ (alternative, KILL #55 path)**: G2 breaks ceiling. The intermediate-decay regime captures the bear-avoidance MDD lift WITHOUT triggering full LETF whipsaw decay (which dominated iter 014 at 3×). If gate adds Sharpe (as in iter 016 at no-decay) AND CAGR is preserved (as in iter 015 LETF 2× standalone), G2 score could reach 70+. If 3 bars met → KILL #55 fires → hunt REOPENS.

**H₃ (CAGR preservation, KILL #56 path)**: At 2.25× LETF, gate cost on CAGR is intermediate (~−1.5pp predicted) vs iter 016's −1.61pp at 1.41× stack. Iter 015 LETF 2× had CAGR 16.36%; minus gate cost ~14.7-15% — **clearly above 11.21% bar**. Tests whether gate preserves CAGR bar at moderate leverage.

**H₄ (Sharpe inflection across decay axis, KILL #57 path)**: Sharpe lift from gate is non-monotonic across decay regime:
- 3× LETF: Sharpe drops (gate's reaction-speed gain consumed by ON-period decay)
- 2.25× LETF: Sharpe ?
- 1.41× stack: Sharpe rises (gate's MDD gain at no-decay is real)

H₄ tests whether the Sharpe inflection lies at moderate-decay (2.25× LETF). If gate × sleeve Sharpe at 2× LETF > 0.95 (close to 1.41× stack's 1.080), the no-decay regime's gate-positive effect partially extends to moderate-decay.

**H₅ (off-state composition transfers from iter 016)**: At iter 016, IEF wins on all metrics over KMLM-defensive and 50/50 blend. At 2.25× LETF, the same pattern is expected — IEF (7-10y Treasury) more reliable cash-equivalent than KMLM during persistent bear-mode.

---

## Configs (3 — keep cumulative n_trials growth slow)

All 3 use `type=lrs` strategy, `signal_ticker=SPYSIM`, `sma_window=200`, `filter=sma`, `lag_days=1` (canonical Gayed gate, identical to iter 016 G1).

ON-state weights (identical to iter 015 `f1_aw_letf_2x`, the F1 family LETF 2× variant that passed all 3 bars standalone):

| ticker  | leverage | weight | notional contribution |
|:--------|---------:|-------:|----------------------:|
| UPROSIM | 3× SPY   | 0.30   | 0.90× SPY             |
| TMFSIM  | 3× LTT   | 0.25   | 0.75× LTT             |
| IEFSIM  | 1× ITT   | 0.15   | 0.15× ITT             |
| UGLSIM  | 2× Gold  | 0.15   | 0.30× Gold            |
| KMLMSIM | 1× MF    | 0.15   | 0.15× MF              |
| **total**| -       | 1.00   | **2.25× notional**    |

OFF-state weights (3 dose-response sweep matching iter 016):

| name                              | OFF-state weights         | thesis                                               |
|-----------------------------------|---------------------------|------------------------------------------------------|
| g2_f1_letf_2x_sma200_ief          | 100% IEFSIM               | Canonical Gayed defensive (best per iter 016 pattern)|
| g2_f1_letf_2x_sma200_kmlm         | 100% KMLMSIM              | Aggressive crisis-alpha defensive                    |
| g2_f1_letf_2x_sma200_blend        | 50% IEFSIM + 50% KMLMSIM  | Balanced defensive                                   |

**Cumulative n_trials**: prior 50 (iter 016) + 3 = **53**.

---

## Pre-committed KILL conditions

KILLs #1-#53 already declared. Numbering continues at #54.

### KILL #54 (G2 reinforces KILL #33 — Regime-gated F1 LETF 2× caps ≤ 67)

**Definition**: If best G2 config score ≤ 67 across all 3 configs, the architectural ceiling claim from iter 011 is **strengthened from "8 fams + 2 hybrids" to "8 fams + 3 hybrids"** (gate × LETF 2× sleeve adds 3rd cross-product hybrid).

**Trigger**: `max_score(g2_*) ≤ 67`.

**Action if FIRED**: update BASE_MEMORY frontmatter `architectural_ceiling: confirmed_8_families_plus_3_hybrids`. Decay-axis gate × sleeve interaction surface now spans 3 points (no-decay, moderate-decay, decay-dominated) — all cap at or below 67. F1+SPLIT remains deploy fallback. Mandate §1 100% Plano C unchanged.

### KILL #55 (G2 breaks ceiling — KILL #33 INVALIDATED)

**Definition**: If best G2 config score ≥ 70 with all 3 strict bars met, the architectural ceiling was an artifact of testing only no-decay or full-decay regimes — moderate-decay regime captures the gate × sleeve sweet spot. Hunt **REOPENS** for iter 018+ extending LETF 2× hybrid sweep.

**Trigger**: `max_score_g2 ≥ 70 AND winner_conditions_met=True for that config`.

**Action if FIRED**: revert BASE_MEMORY status to `hunting`. Plan iter 018+ extending sleeve composition (different LETF leverage levels 1.5×/1.75×/2.5×, off-state composition refinement, ON-state KMLM/UGL dose-response).

### KILL #56 (Gate at 2× LETF preserves CAGR bar)

**Definition**: If at least one G2 config has mean CAGR ≥ 11.21% bar, the gate cost on CAGR at moderate-decay does NOT crash CAGR below the bar (unlike iter 016 G1 which failed by 0.87pp). Confirms predicted "G1-LETF estimated 60-65" path.

**Trigger**: `max_cagr(g2_*) ≥ 0.1121`.

**Action if FIRED**: confirms the leverage axis is the binding CAGR constraint at moderate-decay, separating "gate ⇒ CAGR fails" from "gate-OK at higher leverage". Documents that G1 vs G2 CAGR delta is driven by sleeve leverage, not gate cost.

**Action if NOT FIRED**: **all 3 G2 configs FAIL CAGR bar** — gate cost at 2× LETF is HIGHER than at 1.41× stack (counter-prediction). Would refute H₃ and indicate decay × gate compounding.

### KILL #57 (Gate × Sleeve Sharpe at 2× LETF is intermediate between iter 014 and iter 016)

**Definition**: G2 IEF (canonical defensive) mean Sharpe lies between iter 014 e1_tqqq_split_kmlm30_tlt10_tsmom6m (0.746) and iter 016 g1_f1_stack_sma200_ief (1.080). Tests the Sharpe inflection across decay axis.

**Trigger**: `0.746 ≤ mean_sharpe(g2_f1_letf_2x_sma200_ief) ≤ 1.080`.

**Action if FIRED**: Sharpe response across decay regime is monotonic — gate's whipsaw cost scales with decay drag. Documents the decay × gate Sharpe surface.

**Action if NOT FIRED**: either G2 IEF Sharpe > 1.080 (gate-positive effect at 2× LETF stronger than at no-decay, very surprising) OR G2 IEF Sharpe < 0.746 (decay drag at 2× LETF dominates beyond 3× — extremely surprising). Either way would invalidate the smooth-monotonic decay-axis interpretation.

---

## Expected outcomes (priors)

| config                    | expected mean CAGR | expected mean MDD | expected score | bar pass?           |
|---------------------------|-------------------:|------------------:|---------------:|---------------------|
| g2_f1_letf_2x_sma200_ief  | 13-15%             | 25-35%            | 62-68          | likely PASS 3/3     |
| g2_f1_letf_2x_sma200_kmlm | 11-13%             | 25-35%            | 55-62          | maybe PASS or borderline FAIL CAGR |
| g2_f1_letf_2x_sma200_blend| 12-14%             | 25-32%            | 58-65          | likely PASS 3/3     |

Most likely outcome: **best G2 config scores 62-68** → KILL #54 fires (≤ 67). KILL #55 unlikely (~10-15% probability — would require 2.25× LETF gate to outperform all 8-fam + 2-hybrid prior best).

KILL #56 (CAGR bar preserved): expected to FIRE. Iter 015 LETF 2× standalone CAGR 16.36% gives ample headroom for the predicted ~1.5pp gate cost.

KILL #57 (Sharpe intermediate): 60-70% likely. Gate at moderate decay should be Sharpe-positive but less so than at no-decay; Sharpe ~0.85-1.00 predicted.

Probability KILL #55 fires (hunt REOPENS): **~10-15%** — would require the 2× LETF moderate-decay regime to be the gate × sleeve sweet spot AND simultaneously preserve CAGR bar AND lift gates to 6+/7. Possible but unlikely given E1 (3× LETF) cap at 65 and G1 (1.41× stack) score 61.

---

## INCOMPLETE flags

- **PBO N=3 warning** persists (CSCV statistically unstable with N<4). Iter 016 showed gate construction lowers PBO via decorrelated combinations (lh 0.81→0.167); same effect expected for G2.
- **TMFSIM synth** uses 1.5%/y daily-reset decay assumption (added iter 008). Real TMF (Direxion) historical decay is ~1-2%/y; estimate is conservative-mid range.
- **UGLSIM** is in testfolio cache (2× gold ETF synth). Gold has lower vol than equity → UGL decay is less severe than UPRO/TMF (~0.5-1%/y).
- **UPROSIM/TMFSIM/UGLSIM/IEFSIM/KMLMSIM** all DIRECT in testfolio cache — no synth construction in this iter. SPY signal via SPYSIM cache.
- **Gate fixed at 200d SMA** — this iter does NOT test EMA / TSMOM / faster signals. Iter 002 KILL #7/#8 closed faster signals on SPY-track; iter 014 confirmed TSMOM at 3× LETF is decay-dominated. Canonical Gayed 200d retained for direct iter 016 G1 → iter 017 G2 leverage-axis comparison.
- **2-dataset framework**: lh_56y (40y synth) + spy_real (22.7y Tiingo daily). ndx_real not used per methodology refactor 2026-04-29.
- **NEW module: NONE**. Reuses lrs spec type (added iter 001) + portfolio_returns_from_config + testfolio cache. 765 → 765 tests baseline preserved.

---

## What this iter does NOT test

- **G2 with non-200d SMA gate** (EMA, TSMOM, vol gate) — fixed at 200d SMA for direct iter 016 leverage-axis comparison.
- **Different ON-state composition** (without UGL, without TMF, etc.) — fixed at iter 015 f1_aw_letf_2x weights for direct sleeve-axis comparison.
- **Intermediate leverage (1.75× LETF)** — would be 4th cross-product hybrid; deferred unless KILL #55 fires.
- **C2 CAPE-timing** — flagged low-credibility per PROMISING_DIRECTIONS.md; no CAPE infra. Only Tier 3 family remaining untested in formal taxonomy.

---

## Citations

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d SMA gate canonical; iter 014 + 016 + 017 systematically test gate × sleeve interaction across decay axis.
- **Bridgewater All-Weather (Dalio 1996)** — F1 LETF 2× ON-state derives from canonical risk-parity construction at 2.25× notional.
- **Asness (1996) "Why Not 100% Equities?" JPM** — leverage-balanced thesis; G2 tests whether gate complements the leverage-balanced edge at moderate-decay.
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking baseline (iter 015 stack 1.41× Pareto-dominated LETF 2.25× without gate). Tests whether gate flips the Pareto ordering at LETF 2× → stack 1.41×.
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha (KMLM defensive) — iter 016 found IEF > KMLM > 50/50 monotonic on Sharpe + MDD + CAGR at no-decay; G2 tests whether the same pattern holds at moderate-decay.
- `[advances_fin_ml, p.31-34]` factor framework — gate × sleeve orthogonality empirically tested at THIRD decay regime; KILL #54/#55 binary outcome on hunt-status.
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 53 after this iter; preserves statistical integrity (worst-case p-value still well below 0.05).
- `[advances_fin_ml, p.208-211]` PBO grid-level — 3-config × 2-dataset = 6-cell grid (PBO N=3 warning persists). Iter 016 showed gate construction lowers PBO; same effect expected for G2.
- `[advances_fin_ml, p.196-202]` bootstrap CI — gate G6 99.9% CI low > 0 required.

---

## Decision tree post-iter

| outcome                                         | action                                                                | KILL fired         |
|-------------------------------------------------|-----------------------------------------------------------------------|--------------------|
| All G2 configs score ≤ 67                       | Reinforce KILL #33 across 8 fams + 3 hybrids. CLOSED.                 | #54                |
| Any config scores 68-69                         | Document marginal lift; hunt remains CLOSED at 67-cap                 | none               |
| Any config scores ≥ 70 + 3 bars                 | INVALIDATE KILL #33. Reopen hunt for iter 018+.                       | #55                |
| At least 1 config has mean CAGR ≥ 11.21%        | Confirms gate at 2× LETF preserves CAGR bar                           | #56                |
| G2 IEF mean Sharpe ∈ [0.746, 1.080]             | Sharpe response across decay-axis is monotonic                        | #57                |

Most likely path: **KILL #54 + #56 + #57 fire simultaneously**. Hunt remains CLOSED. F1+SPLIT (long_term_portfolio incumbent) remains deploy fallback. Mandate §1 100% Plano C unchanged.

Lower-likelihood path (~10-15%): **KILL #55 fires**, hunt reopens, iter 018+ extends LETF 2× hybrid sweep.

---

## Why this iter is worth doing despite hunt being CLOSED

1. **Strengthens the architectural-ceiling claim** from "8 fams + 2 hybrids" to "8 fams + 3 hybrids" by closing the moderate-decay regime gap on the gate × sleeve interaction surface.
2. **Tests the explicitly-enumerated prediction** from iter 016 path-to-90 analysis (G1-LETF estimated 60-65). Empirical validation of analytical prediction adds rigor.
3. **Maps the gate × decay interaction surface** to 3 data points (no-decay, moderate-decay, decay-dominated) — sufficient to interpolate the Sharpe + MDD + CAGR responses across the decay axis.
4. **Probes the path that iter 015 f1_aw_letf_2x suggested as next-best CAGR-passer** (16.36% CAGR, 43.53% MDD). Iter 015 selected stack 1.41× because Sharpe was higher; gate could push LETF 2× into best-overall-score territory if MDD lift is substantial.

Cumulative n_trials = **53** after this iter; worst-case DSR p-value bar at p=0.05 still has comfortable margin (iter 016 worst was 1.47e-05, expected G2 worst ~1e-04 to 1e-03 range based on iter 015 LETF 2× standalone metrics).
