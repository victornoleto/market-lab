# Phase 3.8-1 — BREADTH_NO_WINNER_B (halt contract §T5)

**Date:** 2026-04-22
**Branch:** `phase3.8/plano-b-winner-hunt-20260422`
**Engine:** F2-patched (prev_weight × return alignment, preserved from Phase 3.7-3 commit `7b90a8f`).
**Pytest:** **908 → 929 passed, 2 skipped, 0 failures** — baseline preserved (+21 new smoke tests, ~4 per B1-B5 family). Note: individual subagent reports quoted 970/983/987 as transient numbers because pytest picked up parallel subagents' uncommitted test files during their own runs; the post-commit canonical baseline is 929.
**Input:** Phase 3.7-3 `BREADTH_NO_WINNER.md` (Wave 3 path R3 extraction — test Gayed canonical + close-family variants under rota B Inter DARF).

---

## 0. Escalation trigger

Per plan §T5: **5/5 Plano B hypothesis families (B1-B5) FAILED honest 13-gate validation** across 5 atomic subagent commits. The Plano B hypothesis space under honest gates + 15% year-end DARF + mutually-exclusive IS/OOS/FWD windows is now **exhausted**.

Each subagent produced AGGREGATE.md + summary.json + jornada + atomic commit + 4-5 smoke tests. No frozen files touched. Mandate §7 and strategy docs untouched. The sole open item is the user decision on path forward (§4 below).

**Cumulative project stat:** Phase 3.5f (6 FAIL) + Phase 3.6 (10 FAIL) + Phase 3.7-3 (8 FAIL) + Phase 3.8-1 (5 FAIL) = **29 honest 13-gate validations across 29 mechanically-distinct paradigms, 0 PASS.**

---

## 1. Comparison table (Wave 1 canonical + Wave 2 close-variants + Wave 3 fallback)

Legend: ✅ pass; ❌ fail; ⚠️ warning-only (mandate §2.2/§2.3 tier framework). Hard gates = 9/10/11/12 (cross-lib, bootstrap 99.9% CI OOS+FULL, PBO, DSR).

| # | Family | Winner config | IS Sharpe | OOS Sharpe | OOS CAGR tier | OOS MDD tier | FWD Sh | WF | Hold | IR | X-lib Δ (HARD) | Bootstrap OOS CI (HARD) | PBO (HARD) | DSR p (HARD) | Cost×2 Sh | Hard | Commit |
|---|---|---|--:|--:|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|
| B1-UPRO | Gayed canonical 1-leg SMA-200 + UPRO/cash | leverage=3, SMA=200 | 0.758 | 0.371 | 6.86% Folclore ⚠️ | -51.2% Reject ⚠️ | +0.710 | 8/8 | 16d ✅ | 0.208 | 0.000pp ✅ | low<0 ❌ | 0.238 ✅ (2-cfg) | 0.491 ❌ | 0.282 ❌ | **2/4** | `9a3e24d` |
| B1-SSO | Gayed canonical 1-leg SMA-200 + SSO/cash | leverage=2, SMA=200 | 0.821 | 0.391 | 6.10% Folclore ⚠️ | -37.0% Warn ⚠️ | +0.727 | 8/8 | 16d ✅ | 0.091 ❌ | 0.000pp ✅ | low<0 ❌ | 0.238 ✅ | 0.459 ❌ | 0.286 ❌ | **2/4** | `9a3e24d` |
| B2 | Gayed MA-robustness sweep (16 cfg = SMA/EMA × 100/125/150/200 × UPRO/SSO) | SMA-200-SSO-2x (same as B1-SSO) | 0.821 | 0.391 | 6.10% Folclore ⚠️ | -37.4% Warn ⚠️ | +0.727 | 8/8 | 16d ✅ | 0.112 ❌ | 0.000pp ✅ | low<0 ❌ | 0.298 ✅ (16-cfg borderline) | 0.590 ❌ | 0.286 ❌ | **2/4** | `14f58d7` |
| B3 | Pauchlyova 2025 static+trend (5-asset 20/40/20/10/10 LETF/TLT/SPY/GLD/SHV) | SSO-static-quarterly | 0.694 | **1.140** | 11.91% Marginal ⚠️ | -17.5% Válido ⚠️ | +0.420 | ≥6/8 | 63d ✅ | -0.31 ❌ | 0.578pp ✅ | low<0 ❌ | **0.524 ❌** (8-cfg >0.5) | 0.150 ❌ | 0.894 ✅ | **3/4** | `f69b468` |
| B4 | Hsieh-Chang-Chen 2025 AR(1) regime (8 cfg = 2 legs × 4 lookbacks {42,63,84,126}) | SSO-2x-L126 (collapsed to quasi-SMA) | 0.529 | 0.493 | 7.68% Folclore ⚠️ | -35.4% Warn ⚠️ | +0.439 | 7/8 | 5d ✅ | 0.164 ❌ | 0.000pp ✅ | low<0 ❌ | 0.183 ✅ | 0.304 ❌ | 0.370 ❌ | **2/4** | `36b5fda` |
| B5 | Faber 10-mo GTAA single-asset SPY (unleveraged, 4 cfg SMA 6/10/12 mo + daily-210) | monthly-SMA10mo canonical | 0.753 | 0.613 | 6.63% Folclore ⚠️ | -18.4% Válido ⚠️ | +0.747 | 8/8 | 211d ✅ | 0.079 ❌ | 0.000pp ✅ | low=-4.5e-5 ❌ | 0.155 ✅ | 0.0835 ❌ | 0.482 ❌ | **2/4** | `1746969` |

**Pattern:** 5/5 families FAIL gate 10 (bootstrap 99.9% CI low > 0 OOS). 5/5 FAIL gate 12 (DSR p < 0.05). 4/5 PASS gate 11 (PBO), 1/5 FAIL (B3 at 0.524 — multi-feature family). 5/5 PASS gate 9 (cross-lib Δ ≤ 3pp; engine clean on 5 more independently-implemented strategies, now 23 total across 3.6/3.7/3.8).

---

## 2. Cross-family patterns

### 2.1 Engine remains clean — this is NOT an implementation artifact

The F2 patch (`prev_weight × return` alignment via `.shift(1).fillna(0.0)`, commit `7b90a8f`) holds across 5 more independently-implemented strategies in 5 distinct paradigms (canonical binary regime / MA sweep / multi-asset static+trend / AR(1) novel / monthly GTAA):

- **Cross-lib Δ = 0.000pp on 4/5 winners** (pandas ≡ vectorbt down to the 4th decimal); **0.578pp on B3** (pandas vs `bt` multi-asset, well under 3pp cap).
- The Phase 3.7-3 observation "F2 engine fix holds across 18 independently-implemented strategies" now extends to **23 strategies** (10 Phase 3.6 + 8 Phase 3.7-3 + 5 Phase 3.8-1).

### 2.2 Overfit is not the primary cause either

PBO values across 5 winners span **0.155 → 0.524**. Four of five PASS the PBO gate (0.3 single-feature for B1/B4/B5, 0.5 multi-feature for B2/B3). The single failure (B3 at 0.524) is a multi-feature grid where rank stability is genuinely weak; the other 4 are "the whole grid is uniformly weak" rather than "IS-best beats OOS" — a signature of universally-null edge, not overfit-to-IS.

This is **the same finding** as Phase 3.6 families B/D/H/J (PBO < 0.35, no winner) and Phase 3.7-3 H1-H3 (PBO 0.024-0.413). The strategies are honestly implemented. They just lack edge after DARF + multiple testing.

### 2.3 The single structural killer across all 5 families

Unlike Phase 3.7-3 (which had 3 distinct paradigm-specific killers, one per wave), **Phase 3.8-1 has ONE killer, consistent across all 5 families**:

**Killer: "gross edge exists but 15% year-end DARF on rota B + Deflated-Sharpe multiple-testing penalty collapses it below statistical significance."**

Evidence:
- IS Sharpe across 5 winners: **0.529 → 0.821** (all PASS gate 1, gross edge real).
- OOS Sharpe: **0.371 → 1.140** (5/5 FAIL gate 2, but B3 passes the soft 1.3 threshold conceptually — still fails hard gates 10/11/12).
- **Gate 10 bootstrap OOS 99.9% CI low**: all 5 winners land at **−4.5e-5 to −5e-4** — barely negative, just enough to cross zero. Under a 95% CI or 99% CI the same strategies would pass; under our 99.9% (stricter) they don't. This is the rigorous tail that matters.
- **Gate 12 DSR p**: span **0.0835 (B5 closest-to-pass) → 0.590 (B2 worst)**. The Deflated Sharpe framework `[advances_fin_ml, p.196-211]` inflates the null proportional to the number of configs tested + variance of OOS Sharpe; across our 2-16 config grids and 5 families, p-values are in the **"indistinguishable from selection-bias noise"** range.

**DARF is not the unique killer** as initially hypothesized (plan §2.3). B5 Faber has turnover **1.39 trades/yr** (essentially tax-minimal) and still fails. B1 canonical has 5.3 trades/yr and fails. **The OOS signal is statistically weak AT ALL turnover levels.**

### 2.4 The "closest to edge": B3 static allocation

B3-SSO-static-quarterly (no trend overlay) is the single strategy with OOS Sharpe > 1.0 and OOS MDD in Válido tier (-17.5%). It fails 3/4 hard gates (bootstrap + PBO + DSR) but this is not accidental:

- Static 20/40/20/10/10 (SSO/TLT/SPY/GLD/SHV) is effectively a **60% SSO + 40% diversified** portfolio — essentially the Ray Dalio All-Weather with LETF equity sleeve, not a signal-driven strategy.
- The "edge" is not the signal (trend overlay HURTS by 4/4 configs) but the passive mean-variance of the base allocation itself, during the compressed 2016-2020 OOS (covid recovery).
- The winner passes gate 13 (cost×2 Sharpe 0.894 > 0.8) — robustness-to-cost is the only gate where it has genuine separation from other families.

**Interpretation:** a **static diversified LETF-sleeve portfolio** has a better risk-adjusted profile than any signal-driven rotation in our search space. This is not a winner by our gates but is a meaningful observation for Plano C framing.

### 2.5 Consistent with Phase 3.5f + 3.6 + 3.7 (29/29 FAIL cumulative)

The Phase 3.5f Plano A V2 revalidation showed the same pattern (6 FAIL, mandate §7 override on CAGR/MDD gates). Phase 3.6 canonical hunt (10 FAIL) confirmed at breadth. Phase 3.7-3 top-tier literature hypothesis families (8 FAIL) confirmed across 3 distinct paradigms with 3 distinct killers. **Phase 3.8-1 adds 5 more FAIL with a unified killer** — bootstrap CI + DSR.

This is the predicted class of result from:
- López de Prado DSR under multiple testing `[advances_fin_ml, p.196-211]`
- Aronson 6,402-rule S&P 500 null `[evidence_based_ta, p.459]`
- Hsu/Kuan 82% post-selection decay `[evidence_based_ta, p.450]`
- Li-Ferreira 2025 state-of-art ML Sharpe 0.35 net `[phase3_7_literature_sprint, §T10]`

---

## 3. What this means

The Phase 3.8-1 plan deliberately targeted **the lowest-turnover, most-canonical literature strategies** specifically chosen to **survive DARF drag** — exactly the subset that Phase 3.7-3 §2.3 Wave 2 killer suggested should survive. The pivot was correct; the result is not what was hoped for.

**Plano B finding:**
- The Gayed LRS gross-edge is real (IS Sharpe 0.5-0.8 on multi-decade data).
- Under rota B Inter (15% DARF year-end realization), even low-turnover versions lose significance at the 99.9% CI + DSR level.
- Multi-asset variants (B3) and novel-signal variants (B4) do not recover.
- Unleveraged single-asset (B5) — the "Faber baseline" — also fails.

**Combined with Phase 3.7-3 Rota A finding:**
- **Rota A (Pepperstone CFD):** 2-day swap cap amputates trend edges (Wave 3 killer).
- **Rota B (Inter equity):** 15% DARF + multiple-testing penalty collapses signal significance.
- **Neither broker rota is broken.** Both work for their canonical use cases (passive Inter, intraday Pepperstone). What does not survive **on either rota** is **actively-traded backtest-derived winners** under our honest 13-gate framework.

**This is the honest default per mandate §4.7.**

---

## 4. Recommendations (per plan §T5)

**Orchestrator does NOT choose; user chooses.** Five concrete paths follow (R1-R5; R5 added based on 2026-04-22 conversation about composer.trade).

### R1 — Paper trading B5 Faber canonical for 6-12 months to collect live data

**What:** Despite B5 failing hard gates 10/12, its profile is structurally the cleanest (turnover 1.39/yr, MDD -18.4% Válido, cost×2 Sharpe still positive 0.48). Paper-trade B5-monthly-SMA10mo live on rota B Inter paper account for 6-12 months. Use the live P&L as a 13th "window" to re-validate under fresh data.

**Prior:** low. If our 56 years of SPX-TR + DARF-honest simulation already say p=0.0835 (gate 12 boundary), 6-12 months of live data won't shift the posterior much. But it's the only way to distinguish "real but weak signal" from "null" in the live regime. Cost: essentially zero (paper trading, no capital at risk). Time: 6-12 months passive observation.

**Risk:** none direct; opportunity cost of not deploying active capital elsewhere.

### R2 — Pivot Plano C 100% passive, abandon Plano B hunting (mandate §4.7)

**What:** Invoke mandate §4.7 fallback. 60-80% passive buy-hold (already decided in mandate §1). Reallocate the 20-40% active bucket to: **30% Plano C passive (pure SPY/world index buy-hold)** + **10% discretionary sleeve for opportunistic manual trades**. No algorithmic Plano B.

**Prior:** this is the **honest default** after 29/29 FAIL. The mandate §4.7 explicitly tolerates this outcome. Phase 3.5b's 3-leg SSO+QLD+UGL "winner" was invalidated by the Phase 3.5c synthetic-LETF bug and never recovered on clean engine. No algorithmic Plano B has cleared honest gates.

**Cost:** immediate, free (rebalance allocation decision).
**Risk:** ambition shrinks below mandate §1's "Strategy B complements Strategy A" framing. But Strategy A (Plano A short-hold) also had no winner in Phase 3.7 (R3 recommendation there). So ambition already shrank.

### R3 — Re-spec mandate §2.2/§2.3 to accept "CDI-líquido-matcher" as Plano B winner tier

**What:** Mandate §2.2 currently sets Plano B tier "Válido" at CAGR 17-25% (above CDI 11% floor). Lower "Válido" to "CAGR ≥ CDI-líquido 11% with MDD ≤ 25%". Under that bar, **B5 Faber canonical would pass as "Válido"** with FWD CAGR 10.81% (borderline) and FWD MDD -33.7% (would still fail the new MDD cap). B3-SSO-static-quarterly would pass OOS CAGR 11.91% + OOS MDD -17.5%.

**Prior:** philosophical shift, not a statistical one. Doesn't address gate 10 (bootstrap CI) or gate 12 (DSR) — still "indistinguishable from null". But reframes "winner" from "edge above CDI" to "matches CDI with equity-like exposure + downside cap".

**Cost:** mandate revision only (user sign-off + §7 entry).
**Risk:** sets precedent for relaxing gates. Mandate §2.4 hard-block gates already survived two prior relaxations (§2.2 CAGR, §2.3 MDD → warning-only in 2026-04-22). A third relaxation removes the gate framework's teeth.

### R4 — Wait 6-12 months, re-run Phase 3.8 with post-2026 data + fresh iteration

**What:** Freeze Plano B hunting. Re-run B1-B5 (or subset) in ~Q3 2026 with 6-12 months more data, updated `self_improve_loop` corpus, and any new literature (esp. 2025 LETF / regime-filter papers).

**Prior:** low expected information gain per Phase 3.7-3 §4 R4 already-argued ("loop ran Phase 3.5e on same corpus, 38/144 trials paused — usable hypothesis space under broker constraints seems exhausted"). 6-12 months is ~2-3% more data; bootstrap CI low won't flip sign from -4.5e-5 to > 0 in that window.

**Cost:** 2-3 weeks re-run + LLM cost.
**Risk:** high cost for low expected information gain.

### R5 — Composer-inspired Phase 3.9 (layered conditionals at weekly/monthly cadence)

**What:** User raised in 2026-04-22 conversation. Composer.trade hosts user-generated decision-tree strategies ("symphonies") with multi-layer conditionals (VIX + RSI + MA + max_dd) typically on TQQQ/SOXL with daily rebalance + claimed CAGRs 75-286%. Extract **arquétipos** (patterns, not specific symphonies) and test under honest gates:

- **B6 arquétipo "3-layer regime":** `if VIX>30 → SHV; elif SPY<SMA-200 → SHV; elif RSI(14)>80 → SHV; else UPRO`. Weekly rebal.
- **B7 arquétipo "sideways deleverage":** `if |price/SMA200-1|<band → 50/50 UPRO/SHV; elif above → UPRO; elif below → SHV`. Monthly rebal.
- **B8 arquétipo "black swan catcher":** Gayed SMA-200 base + 10% VIXY sleeve conditional on VIX > 35.

**Important caveats:**
- Composer strategies have **extreme survivorship bias** (users iterate until backtest is pretty, publish winners only). Cannot be copied — only patterns can inspire testable hypotheses.
- Daily-rebal composer strategies are **DARF-toxic on rota B** (Phase 3.7-3 §2.3 Wave 2 killer). Must convert to weekly/monthly.
- Multi-layer conditionals have **more degrees of freedom** → PBO likely to rise (B3 already hit 0.524 with only 8 configs). Expect gate 11 pressure.
- OOS claims on composer are 2-4y (covid recovery + AI rally 2023-2024), not 16y. Not comparable to our gates.

**Prior:** low-to-moderate. The pattern structure is *the same* as B1-B5 (decision tree, if-then-else), just with richer signals. Our killer (gate 10/12) is unlikely to care whether the decision tree has 1 layer or 3. But testing is legitimate; a null result here closes the layered-conditional family cleanly.

**Cost:** 1-2 weeks per archetype (B6/B7/B8). 2 waves if parallel dispatch; ~12-20h LLM time.
**Risk:** exhausts more of the hypothesis space without new information. If nothing passes, adds 3 more to the 29/29 → 32/32 FAIL count — diminishing value. But the user asked explicitly, so it's honest to include this path.

---

## 5. Orchestrator recommendation (informal, non-binding)

**Two-path recommendation:**

**Primary: R2 (Pivot Plano C 100% passive).** After 29/29 honest FAILs across 4 phases and 3 broker rotas, the honest default is that the active edge in our search space is below the noise floor of our gates. Mandate §4.7 already tolerates this explicitly. Re-allocate cleanly. This is low-risk, immediate, and mandate-compliant.

**Optional concurrent: R1 (paper-trade B5 Faber) + R5 (Phase 3.9 composer-inspired).** If the user wants to keep the Plano B search open: paper-trade B5 for 6-12 months (zero-cost data collection) AND run Phase 3.9 in parallel to close the layered-conditional hypothesis family. If Phase 3.9 also FAILs, combine the live B5 data + 32/32 backtest FAILs into a final mandate §7 entry formalizing "Plano B is null under honest 13-gates".

**Against: R3 (soften gates) and R4 (wait + re-run).** R3 removes the gate framework's integrity (third relaxation); R4 is low expected information gain for the cost.

The user retains full authority to override. In particular, if R5 is preferred over R2, the orchestrator will dispatch the Phase 3.9 plan-write next.

---

## 6. Artifacts for user review

- This file: `reports/phase_3_8/BREADTH_NO_WINNER_B.md`
- Per-family AGGREGATE.md + summary.json:
  - `reports/phase_3_8/b1_gayed_canonical/` (UPRO + SSO variants)
  - `reports/phase_3_8/b2_ma_robustness/` (16-config sweep)
  - `reports/phase_3_8/b3_pauchlyova/` (8-config static+trend)
  - `reports/phase_3_8/b4_hsieh_ar1/` (8-config AR(1))
  - `reports/phase_3_8/b5_faber/` (4-config Faber GTAA)
- Per-family jornada entries: `jornada/2026-04-22-*-phase3.8-b{1,2,3,4,5}-*.md`
- Atomic commits on branch `phase3.8/plano-b-winner-hunt-20260422`:
  - B1: `9a3e24d`
  - B2: `14f58d7`
  - B4: `36b5fda` (order: B1→B2→B4→B3→B5 due to parallel dispatch commit order)
  - B3: `f69b468`
  - B5: `1746969`
- This escalation commit: pending (to be written after this file)

---

## 7. Files NOT modified (invariants preserved)

- `docs/investment-mandate.md` — untouched
- `docs/strategies/*.md` — untouched
- `jornada/README.md` — updated by orchestrator only (this file's commit)
- `docs/self_improvement/*` — untouched
- All frozen reports (`reports/phase_3_5a_v2/*`, `reports/phase_3_5f/*`, `reports/phase_3_6/*`, `reports/phase_3_7/*`, `docs/superpowers/findings/*`) — untouched
- Phase 3.6 / 3.7 strategy files — untouched
- `src/ai_trade/backtest/strategies/letf_rotation.py` — untouched (canonical reference)
- `.claude/CLAUDE.md` — untouched

---

## 8. Citations

- F2 lookahead-fix alignment: `[advances_fin_ml, p.31-34]`
- Deflated Sharpe Ratio (gate 12 basis): `[advances_fin_ml, p.196-211]`
- CSCV / PBO (gate 11 basis): `[advances_fin_ml, p.208-211]`
- Aronson 6,402-rule null: `[evidence_based_ta, p.459]`
- Hsu/Kuan post-selection decay: `[evidence_based_ta, p.450]`
- Gayed canonical LRS (B1): `[leverage_for_the_long_run, p.7-8, p.13, p.17]`
- Gayed MA robustness (B2): `[leverage_for_the_long_run, p.14, Table 6]`
- Pauchlyova 2025 static+trend (B3): `[phase3_7_literature_sprint, §T1]`
- Hsieh-Chang-Chen 2025 AR(1) regime (B4): `[phase3_7_literature_sprint, §T1, arXiv 2504.20116]`
- Faber 2007 GTAA (B5): `[phase3_7_literature_sprint, §T3]` (citation inherited from Phase 3.6 Faber 10-mo implementation)
- Inter rota B cost structure: `[docs/investment-mandate.md §4.6]`
- Mandate CAGR/MDD tier framework + hard gates: `[docs/investment-mandate.md §2.2, §2.3, §2.4, §7]`
- Mandate §4.7 passive-fallback clause: `[docs/investment-mandate.md §4.7]`
- Phase 3.6 precedent: `[reports/phase_3_6/BREADTH_NO_WINNER.md]`
- Phase 3.7-3 precedent: `[reports/phase_3_7/BREADTH_NO_WINNER.md]`

---

**End of BREADTH_NO_WINNER_B.md. User decision pending between R1 / R2 (orchestrator recommendation) / R3 / R4 / R5.**
