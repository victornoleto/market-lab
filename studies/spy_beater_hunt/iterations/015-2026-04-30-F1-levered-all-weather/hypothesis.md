# spy_beater_hunt iter 015 — F1: Levered All-Weather (Dalio risk-parity, NEW 7th architectural family)

**Date**: 2026-04-30
**Type**: Post-impossibility 7th-family sanity check on KILL #33 (architectural ceiling). NEW family not tested in any prior iter: ALWAYS-ON balanced multi-asset (stocks + bonds + gold + managed-futures), leveraged via stacking or LETFs.
**Slug**: `F1-levered-all-weather`
**Status of hunt entering this iter**: `closed_no_winner` (iter 011 IMPOSSIBILITY_RESULT, iters 012/013/014 reinforced 6 fams + 1 hybrid)

---

## Why this iter exists (context)

The spy_beater architectural ceiling at score 67 has been confirmed across:

| family | best score | architecture |
|:---|---:|:---|
| A (Gayed LRS UPRO/TQQQ-track + KMLM/TLT) | 67 | regime-gated leveraged equity, BOND-LIGHT |
| B (HFEA UPRO+TMF ± KMLM) | 63 | always-on leveraged 60/40, NO commodities/gold |
| C (vol-targeted SSO) | 60 | dynamic leverage, SINGLE asset |
| D (concentrated NDX + TSMOM gate) | 59 | concentrated equity + gate |
| D2 (stacked equity NTSX+UPRO+AVUV) | 52 | always-on stacked equity, NO bonds/gold/MF |
| E (cross-product hybrid TSMOM × TQQQ-track) | 65 | gate × concentrated-equity sleeve |

**What's missing**: a TRUE multi-asset balanced (Dalio All-Weather / Asness "Why Not 100% Equities?") family with stocks + bonds + gold + managed-futures, leveraged via stacking OR LETF mix. **No iter has tested this family**. B1/B2 has stocks + LTT only (no gold, no commodities). D2 has stocks + AVUV only (no bonds, no gold, no MF). C1 is single-asset. A/D/E are gated.

This iter explicitly adds the **7th architectural family** to fully exhaust the formal architectural taxonomy before declaring the spy_beater hunt CLOSED.

---

## Hypothesis

**H₁ (primary)**: A leveraged All-Weather balanced portfolio (stocks + bonds + gold + MF) at ~2× notional via LETF mix scores **strictly above** the 67 ceiling because:
- Diversification across 4 asset classes reduces MDD vs concentrated equity (D2 52 → F1 ?)
- Leverage lifts CAGR closer to SPY benchmark (1× All-Weather ~7% → 2× ~14%)
- Crisis-alpha (KMLM) absorbs equity drawdowns regardless of regime gate

If H₁ holds: predicted score 65-72, possibly ≥ 70 → KILL #47 path.

**H₂ (alternative — multi-asset dilution)**: Multi-asset balance DILUTES equity contribution; 2.25× notional with only ~55% equity is equivalent to ~1.4× pure equity exposure. CAGR caps at ~10-12% (below SPY 11.21% bar). Score caps at ≤ 67.

If H₂ holds: KILL #46 fires, hunt remains CLOSED with 7-family + 1-hybrid evidence.

**H₃ (tertiary)**: 1× All-Weather (canonical Dalio) FAILS CAGR bar (mean CAGR < 11.21%). Confirms that pure risk-parity without leverage cannot beat SPY in CAGR — KILL #49 fires. This is a baseline-anchor test, not a hunt-reopening hypothesis.

**H₄ (quaternary)**: Leverage dose-response on All-Weather is monotonic positive on CAGR (1× → 1.5× → 2.25×). KILL #48 fires if both datasets show monotonic. Tests whether the leverage-decay tradeoff is binding only at extreme leverage.

---

## Configs (3 — keep cumulative n_trials low)

| name              | architecture                                                              | notional ~ | gate | thesis                                                     |
|-------------------|---------------------------------------------------------------------------|-----------:|------|------------------------------------------------------------|
| f1_aw_baseline_1x | 30 SPY + 55 TLT + 15 GLD                                                  | 1.00×      | none | Classic Dalio All-Weather 1× baseline (anchor, KILL #49)  |
| f1_aw_stack_15x   | 35 NTSX + 30 GDE + 20 TLT + 15 KMLM                                       | ~1.41×     | none | Capital-efficient stacking (no LETF decay)                |
| f1_aw_letf_2x     | 30 UPRO + 25 TMF + 15 IEF + 15 UGL + 15 KMLM                              | ~2.25×     | none | LETF-heavy aggressive (highest CAGR potential, decay drag)|

All 3 use `type=static` (no regime gate, no vol-target). All synths in cache (TMFSIM added by iter 008; NTSXSIM/GDESIM via long_term_portfolio.proxies). No new module required.

**Cumulative n_trials**: prior 44 (iter 014) + 3 = **47**.

### Notional leverage breakdown for `f1_aw_letf_2x`

| ticker  | leverage | weight | notional contribution |
|:--------|---------:|-------:|----------------------:|
| UPROSIM | 3× SPY   | 0.30   | 0.90× SPY             |
| TMFSIM  | 3× LTT   | 0.25   | 0.75× LTT             |
| IEFSIM  | 1× ITT   | 0.15   | 0.15× ITT             |
| UGLSIM  | 2× Gold  | 0.15   | 0.30× Gold            |
| KMLMSIM | 1× MF    | 0.15   | 0.15× MF              |
| **total**| -       | 1.00   | **2.25× notional**    |

LETF decay drag estimate: ~3-4%/yr (UPRO ~2%/yr, TMF ~1%/yr, UGL ~1%/yr per `[leverage_for_the_long_run, ch.3-4, p.40-60]`).

### Notional leverage breakdown for `f1_aw_stack_15x`

| ticker  | leverage | weight | notional contribution                         |
|:--------|---------:|-------:|----------------------------------------------:|
| NTSXSIM | 0.9× SPY + 0.6× IEF | 0.35 | 0.315× SPY + 0.21× IEF                |
| GDESIM  | 0.9× SPY + 0.9× Gold | 0.30 | 0.27× SPY + 0.27× Gold                |
| TLTSIM  | 1× LTT   | 0.20   | 0.20× LTT                                     |
| KMLMSIM | 1× MF    | 0.15   | 0.15× MF                                      |
| **total**| -       | 1.00   | **1.41× notional** (~0.585 SPY + 0.21 IEF + 0.20 LTT + 0.27 Gold + 0.15 MF) |

NO LETF daily-reset decay (NTSX/GDE use futures stacking, not LETFs).

---

## Pre-committed KILL conditions

KILLs #1-#45 already declared. Numbering continues at #46.

### KILL #46 (F1 reinforces KILL #33 — Levered All-Weather caps ≤ 67)

**Definition**: If best F1 config score ≤ 67 across all 3 configs, architectural ceiling claim from iter 011 is **strengthened from "6 fams + 1 hybrid" to "7 fams + 1 hybrid"**. The Dalio All-Weather family — the most literature-canonical balanced-multi-asset architecture — joins the rejected list.

**Trigger**: `max_score(f1_aw_baseline_1x, f1_aw_stack_15x, f1_aw_letf_2x) ≤ 67`.

**Action if FIRED**: update BASE_MEMORY frontmatter `architectural_ceiling: confirmed_7_families_plus_hybrid`. F1+SPLIT remains deploy fallback. Mandate §1 100% Plano C unchanged.

### KILL #47 (F1 breaks ceiling — KILL #33 INVALIDATED)

**Definition**: If best F1 config score ≥ 70 with all 3 bars met, KILL #33 was an architectural-search limitation, NOT a true ceiling. Hunt **REOPENS** for iter 016+ extending All-Weather variants.

**Trigger**: `max_score_f1 ≥ 70 AND all 3 bars met for that config`.

**Action if FIRED**: revert BASE_MEMORY status to `hunting`, plan iter 016+ extending All-Weather sweep (other leverage levels, MF/duration/Gold dose-response).

### KILL #48 (Leverage dose-response on All-Weather is monotonic positive on CAGR)

**Definition**: CAGR scales monotonically with leverage (1× → 1.5× → 2.25×) on BOTH datasets. Tests whether multi-asset diversification preserves CAGR linearity at higher leverage.

**Trigger**: `CAGR(f1_aw_baseline_1x) < CAGR(f1_aw_stack_15x) < CAGR(f1_aw_letf_2x)` on BOTH `lh_56y` AND `spy_real`.

**Action if FIRED**: document direction has clear CAGR-leverage scaling (no inflection). If CAGR scales sublinearly (NOT FIRED), document leverage-dilution effect.

### KILL #49 (Pure 1× All-Weather fails CAGR bar — Dalio canonical insufficient)

**Definition**: `f1_aw_baseline_1x` mean CAGR < 11.21% bar. Confirms that pure risk-parity without leverage cannot beat SPY in CAGR — anchored finding consistent with 30+ years of Dalio All-Weather literature (Bridgewater All-Weather published CAGR ~7-8% historical).

**Trigger**: `mean_cagr(f1_aw_baseline_1x) < 0.1121`.

**Action if FIRED**: confirms KILL #6 at All-Weather family — pure risk-parity is structurally subordinate to SPY in CAGR-anchored rubric. Closes the "no leverage" path.

---

## Expected outcomes (priors)

| config              | expected mean CAGR | expected mean MDD | expected score | bar pass?    |
|---------------------|-------------------:|------------------:|---------------:|--------------|
| f1_aw_baseline_1x   | 6-8%               | 18-22%            | 35-45          | FAIL (CAGR)  |
| f1_aw_stack_15x     | 9-11%              | 22-28%            | 50-58          | likely FAIL CAGR borderline |
| f1_aw_letf_2x       | 12-15%             | 38-50%            | 60-68          | maybe 3/3    |

Most likely outcome: **best F1 config scores 60-68**, KILL #46 fires (≤ 67) AND KILL #49 fires (1× FAIL CAGR). KILL #48 may fire (CAGR monotonic). KILL #47 unlikely (~10-15%).

Probability KILL #47 fires (hunt reopens): ~10-15% — Dalio All-Weather has historically been Sharpe-superior but CAGR-inferior to SPY; even at 2× leverage the ceiling on multi-asset CAGR is around 12-14%, which scores ~60-65.

---

## INCOMPLETE flags

- **PBO N=3 warning** persists (CSCV statistically unstable with N<4); pre-existing infra warning.
- **TMFSIM synth** uses 1.5%/yr daily-reset decay assumption (added in iter 008). Real TMF (Direxion) historical decay is ~1-2%/yr; estimate is conservative-mid range.
- **UGLSIM** is in testfolio cache (2× gold ETF synth). Gold has lower vol than equity → UGL decay is less severe than UPRO/TMF (~0.5-1%/yr).
- **GDESIM stacking** uses 90% SPY + 90% Gold via futures; assumes 0.5% rolling cost, no decay (capital-efficient like NTSX).
- **All-Weather is ALWAYS-ON**: no regime gate, no vol-target. This is intentional to isolate the multi-asset-diversification effect from the gate effect.
- **NEW module: NONE**. Reuses existing static-portfolio infra; no LRS engine, no vol-target, no momentum gate. 765 → 765 tests baseline preserved.
- **Crisis-alpha is KMLM only** (managed futures); does NOT include DBMF or commodities directly. KMLM proxies broad commodity-trend exposure.

---

## Citations

- **Bridgewater All-Weather** (Dalio 1996, public papers 2011) — risk-parity multi-asset balanced portfolio, foundation of $150B+ AUM strategy.
- **Asness, Cliff (1996) "Why Not 100% Equities?" Journal of Portfolio Management** — early articulation of "leverage a balanced portfolio" thesis (cite as Asness 1996).
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking baseline (NTSX/GDE rationale; F1+SPLIT incumbent fallback).
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — LETF decay magnitude (UPRO/TMF/UGL); F1 LETF variant explicitly subject to this drag.
- `[ilmanen_expected_returns, ch.19]` — MF crisis-alpha role (KMLM); diversification benefit beyond stocks+bonds.
- `[advances_fin_ml, p.31-34]` factor framework — risk-parity as "risk-balanced" portfolio construction, distinct from cap-weighted or vol-targeted.
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials = 47; preserves statistical integrity.
- `[advances_fin_ml, p.208-211]` PBO grid-level — 3-config × 2-dataset = 6-cell grid (PBO N=3 warning persists).
- `[advances_fin_ml, p.196-202]` bootstrap CI — gate G6 99.9% CI low > 0 required.

---

## What this iter does NOT test

- **Levered All-Weather + REGIME GATE** — combining F1 with A1's 200d SMA gate would be a cross-product hybrid (potential iter 016 if KILL #47 fires). Current iter intentionally isolates "always-on" balanced multi-asset.
- **Levered All-Weather + DBMF** — DBMF is alternative MF proxy; would inflate n_trials without orthogonal information given KMLM correlation.
- **All-Weather with INTERNATIONAL equity** (VEA, VWO) — different exposure axis; out of scope for spy_beater (US-centric benchmark).
- **All-Weather with TIPS / commodities futures** — not in synth cache; would require new infra.
- **C2 CAPE-timing** — flagged low-credibility per PROMISING_DIRECTIONS.md; no CAPE infra. Untested as last Tier 3 family.

---

## Decision tree post-iter

| outcome                                       | action                                                             | KILL fired      |
|-----------------------------------------------|--------------------------------------------------------------------|-----------------|
| All F1 configs score ≤ 67                     | Reinforce KILL #33 across 7 fams + 1 hybrid. CLOSED.               | #46             |
| Any config scores 68-69                       | Document marginal lift; hunt remains CLOSED at 67-cap              | none            |
| Any config scores ≥ 70 + 3 bars               | INVALIDATE KILL #33. Reopen hunt for iter 016+.                    | #47             |
| CAGR monotonic 1×→2.25× both datasets         | Document leverage-CAGR scaling clean                               | #48             |
| 1× baseline mean CAGR < 11.21%                | Confirms Dalio canonical insufficient for CAGR mission             | #49             |

Most likely path: **KILL #46 + #49 fire** (best F1 ≤ 67 AND 1× fails CAGR). KILL #48 may or may not fire. Hunt remains CLOSED. F1+SPLIT (long_term_portfolio incumbent) remains deploy fallback. Mandate §1 100% Plano C unchanged.

Lower-likelihood path (~10-15%): **KILL #47 fires**, hunt reopens, iter 016+ extends All-Weather sweep.

---

## Why this iter is worth doing despite hunt being CLOSED

The iter 011 → 012 → 013 → 014 sanity-check chain tested 6 single-axis families + 1 cross-product hybrid. The architectural taxonomy in `PROMISING_DIRECTIONS.md` originally listed Dalio All-Weather as a foundational reference architecture, but **no iter has explicitly tested it as a family**. Closing this gap:

1. Strengthens the negative-result policy claim from "6 fams + 1 hybrid" to "7 fams + 1 hybrid".
2. Tests the highest-AUM real-world strategy ($150B+ Bridgewater All-Weather) directly within the spy_beater rubric.
3. Validates or refutes the Asness 1996 "leverage a balanced portfolio" thesis empirically — a foundational asset-allocation literature claim.
4. The 1× baseline (KILL #49 path) provides an anchored "no leverage" reference for CAGR-anchored rubric.

Cumulative n_trials = **47** after this iter; worst p-value bar at p=0.05 still has comfortable margin (iter 014 worst was 4.44e-3 << 0.05).
