---
mission: "beat iter 009 HAA+Gold (Sharpe 1.120 edu) and close the gap to bestfolio #1 (Sharpe 1.18)"
total_iterations: 0
winners_found: 0
status: in_progress
latest_iteration: ""
cumulative_n_trials: 0
note: "loop initialized 2026-04-27. benchmark = iter009 HAA+Gold. tax model = AnnualDarfEngine (Lei 14.754/2023). RSIT synth available."
---

# Bestfolio Hunt Loop — BASE MEMORY

**Read FIRST every iteration.** Conversation history is empty; this
file + `iterations/NNN-*/` are continuity. Process: `PROMPT.md`. Infra:
`INFRASTRUCTURE.md`.

---

## Mission

Find ONE strategy that **Pareto-advances iter 009 HAA+Gold** across 3 datasets:

| reference | edu Sharpe | vt_real Sharpe | ndx_real Sharpe |
|---|---|---|---|
| **iter 009 HAA+Gold** ← target | **1.120** | **1.061** | **0.954** |
| Plano C V3_1 v3.5 | — | 0.671 | — |
| VT 1x b&h | 0.66 | 0.51 | — |

**Pareto advance** = beats iter009 Sharpe by ≥ 0.10 on ≥ 2 datasets
(strict winner) OR trades Sharpe for CAGR favorably (CAGR frontier).

**Context from global_factor_tilt_loop (FROZEN, 13 iters):**
- Sharpe frontier: iter 009 HAA+KMLM10+GLD5, S=1.120/C=13.89%/MDD=20.81%
- CAGR frontier: iter 013 HAA+ZROZSIM, S=1.011/C=16.35%/MDD=28.98%
- Net-of-tax: iter 014 annual-DARF rerun, HAA sleeve S≈1.04 vt_real
- Gap to bestfolio #1 (HAA SmartStack, Sharpe 1.18): **−0.06 Sharpe**

**Tax model**: always use `AnnualDarfEngine` (Lei 14.754/2023) from
`studies/global_factor_tilt_loop/tax_engine_v2.py` for any net-of-tax
analysis. NEVER use the old `DarfCostBasisEngine` (monthly DARF — incorrect).

Winner criteria live in `WINNER_AND_RANKING.md`.
Dead-ends live in `DEAD_ENDS.md`.

**Hard context**: mandate §1 MAINTENANCE MODE (2026-04-23). Any winner
here is a candidate requiring mandate §7 override before deployment.

---

## Winners found

*(empty — loop not started)*

| # | iter | slug | status | edu S/C/MDD | note |
|---|---|---|---|---|---|

---

## Top-K ranked

*(empty — loop not started)*

| rank | iter | slug | score | tier | Sharpe (edu/vt/ndx) | CAGR (edu) | MDD (edu) |
|---|---|---|---|---|---|---|---|

---

## Iteration log (newest first)

*(empty — loop not started)*

---

## Promising unexplored directions (prioritized)

### Tier 1 — bestfolio top-15 + user architecture preferences

#### iter 001 — BAA-G12 Balanced Asset Allocation

**Hypothesis**: Bold Asset Allocation (Keller & Keuning, SSRN 4346906)
with 12-asset universe in balanced mode. BAA uses a dual canary (BIL+DBND
safety net) + 12-asset offensive rotation. bestfolio.app reports BAA
balanced Sharpe ~1.13 (33y). Close to our gap.

**Sources**: SSRN 4346906 (Keller & Keuning 2023 — BAA). `[stocks_on_the_move, ch.6]`
(Clenow momentum) for the rotation mechanism. `[advances_fin_ml, p.208-211]` (PBO).

**Why iter 009 misses it**: HAA canary=VWOSIM only; BAA uses dual-canary
(safer) + 12 broader assets including small-cap and commodity ETFs.
The wider asset universe captures crisis opportunities HAA misses.

**Kill criterion**: edu Sharpe ≤ 1.120 (no Pareto advance vs iter 009).

**Implementation**: testfolio synths for BAA-compatible universe:
VTISIM, VEASIM, VWOSIM, VBRSIM, IEFSIM, BNDSIM, GLDSIM, KMLMSIM,
DBMFSIM. For small-cap use VBRSIM (AVUV proxy).

**Priority**: HIGH — bestfolio benchmark evidence, close to gap closure.

---

#### iter 002 — NTSX + GDE + KMLM (static capital-efficient)

**Hypothesis**: User-specified architecture: 40% NTSXSIM + 30% GDESIM +
30% KMLMSIM (static). No rotation. Capital-efficient (notional ~1.8×).
Tesis: low-turnover capital-efficient stack matches HAA Sharpe without
monthly rotation cost (DARF drag, trading cost).

**Sources**: `[risk_parity, ch.5]` (WisdomTree 90/60 capital efficiency).
`[leverage_for_the_long_run, p.40-60]` (futures overlay). `[stocks_on_the_move, p.21-30]`
(managed futures "free lunch"). iter 007 global_factor_tilt_loop (static G3' confirmed, STRONG 88).

**Why iter 009 misses it**: iter 007 user-static scored 88 (not 90; G6 vt_real
CI_low borderline). A clean 40/30/30 split without the iter 007 exact weights
may pass G6. NTSX (90/60) vs NTSXSIM synth: validate.

**Kill criterion**: edu Sharpe ≤ 0.900 (static portfolio; lower kill because
static inherently lower-Sharpe than HAA; raise bar if this is close).

**Priority**: HIGH — explicit user preference; addresses DARF drag question.

---

#### iter 003 — NTSX + GDE + RSST (static, RSST variant)

**Hypothesis**: Replace KMLMSIM with RSSBSIM (global equity + Treasury
return-stacked) or `SPYSIM + KMLMSIM` proxy for RSST. Tesis: RSST adds
explicit MF exposure with equity component — better in bull equity regimes
vs pure MF (KMLM). Compare vs iter 002.

**Sources**: `[risk_parity, ch.5]` (return stacking). SSRN — Newfound/ReSolve
return-stacking papers. `[stocks_on_the_move, p.21-30]` (MF momentum).

**Kill criterion**: edu Sharpe ≤ iter 002 result (compare static variants only).

**Priority**: MEDIUM — variant of iter 002; only run if 002 is STRONG+.

---

#### iter 004 — HAA + global factor tilt (AVDV/VBRSIM offensive)

**Hypothesis**: HAA architecture (iter 009) but replace VEASIM in offensive
with `0.7 VEASIM + 0.3 VBRSIM` (intl + small-cap value tilt). Tests whether
Avantis-style factor tilt on international sleeve adds Sharpe above plain VEA.

**Sources**: Fama-French 1993 (SCV premium). `[stocks_on_the_move, ch.6]`
(canary architecture). `[advances_fin_ml, p.222-223]` (DSR).
AVDV vs VEA: ~+0.8pp/y Avantis live (6.5y track record).

**Kill criterion**: edu Sharpe ≤ 1.120 (must beat iter 009).

**Priority**: MEDIUM — incremental HAA variant; directionally correct per Avantis rationale.

---

#### iter 005 — Composite Momentum Standard (bestfolio #2)

**Hypothesis**: bestfolio.app #2 "Composite Momentum Standard" (Sharpe 1.17,
33y). Dual momentum across multiple lookbacks (3m, 6m, 12m), cross-asset
(equity + bonds + gold + MF), averaging signals rather than single lookback.
`[stocks_on_the_move, p.21-30]` (Clenow momentum). Antonacci *Dual Momentum
Investing* (GEM framework — absolute + relative momentum).

**Kill criterion**: edu Sharpe ≤ 1.120 (must beat iter 009).

**Priority**: MEDIUM — bestfolio evidence supports S=1.17. Second strongest
bestfolio entry behind HAA SmartStack.

---

#### iter 006 — HAA + RSIT synth (deferred, prefer real data at launch)

**Hypothesis**: When RSIT (Return Stacked International Stocks + MF) launches
(~mai/2026), replace VEASIM + KMLMSIM in HAA offensive with RSIT proxy:
`VEASIM × 1.0 + KMLMSIM × 1.0 − 50bps/y`. Tesis: stacking MF on top of
international equity in one sleeve reduces complexity vs separate KMLM
allocation.

**Sources**: `[risk_parity, ch.5]`. SEC 485APOS 2026-02-18 (RSIT filing).
Same team as RSST (Hoffstein + Gordillo + Butler + Philbrick).

**Kill criterion**: edu Sharpe ≤ iter 004 result (must beat plain HAA+VEA).

**Priority**: LOW — deferred. RSIT synth available now but incomplete;
prefer real ETF data. Re-activate after RSIT launches.

**Notes**: RSIT synth = `VEASIM × 1.0 + KMLMSIM × 1.0 − 50bps/y`.
Mark as INCOMPLETE synth in any iter that uses it. See `EXTERNAL_INSTRUMENTS.md`.

---

## Structural dead-ends (carry-over from global_factor_tilt_loop)

These were proven dead-ends in the predecessor loop. Same universe:
full text in `DEAD_ENDS.md`.

1. **2× single-asset global-equity LETF + binary SMA**: VTSIM base Sharpe
   (0.61) already matches Gayed LRS target → zero improvement. `[leverage_for_the_long_run, p.17]`
2. **VAA breadth with higher-notional equity (for Sharpe-max)**: GDESIM
   in offensive adds variance faster than returns; HAA canary dominates
   VAA breadth on Sharpe.

---

## Binding constraints (mandate §1, §5, §7)

- **NEVER modify `docs/investment-mandate.md`** — even a winner is a
  candidate, not auto-deploy.
- **Citations obrigatórias** (CLAUDE.md Regra 2): every decision cites
  `[book.slug, p.X]`.
- **7-gate battery** mandatory per `WINNER_AND_RANKING.md`
- **AnnualDarfEngine only** for net-of-tax: `tax_engine_v2.py`
  (`studies/global_factor_tilt_loop/`). NEVER use `DarfCostBasisEngine`.
- **Pytest baseline (461) stays green** — never reduce passing count
- **Max 2h wall-time** per iteration
- **NEVER `git commit`** — `run_loop.sh` handles commits
- **DO NOT touch** `studies/strategy_hunt_loop/`, `studies/gold_swing_loop/`,
  `studies/global_factor_tilt_loop/` — parallel sessions / frozen loop
