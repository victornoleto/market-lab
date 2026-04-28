---
mission: "beat iter 009 HAA+Gold (Sharpe 1.120 edu) and close the gap to bestfolio #1 (Sharpe 1.18)"
total_iterations: 3
winners_found: 0
status: in_progress
latest_iteration: "003-2026-04-28-0148-global-factor-cta-stack"
cumulative_n_trials: 8
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

*(empty — no winners after 3 iterations)*

| # | iter | slug | status | edu S/C/MDD | note |
|---|---|---|---|---|---|

---

## Top-K strategies ranked

| rank | iter | slug | score | tier | Sharpe (edu/vt/ndx) | CAGR (edu) | MDD (edu) |
|---|---|---|---|---|---|---|---|
| 1 | 001 | baa-g12-balanced | 58 | MARGINAL | 0.975/0.792/0.782 | 10.60% | 16.34% |
| 2 | 002 | composite-momentum-standard | 55 | MARGINAL | 0.940/0.958/0.957 | 9.25% | 20.76% |
| 3 | 003 | global-factor-cta-stack | 54 | MARGINAL | 0.823/0.742/0.910 | 12.09% | 41.76% |

---

## Iteration log (newest first)

### 003 — 2026-04-28 — global-factor-cta-stack (MARGINAL, 54/100)

- Hypothesis: A low-turnover static global/factor/CTA stack would improve HAA+Gold by holding persistent `RSSBSIM/GDESIM/KMLMSIM/VBRSIM/VSSSIM/VWOSIM/SPYSIM` exposure instead of paying rotation and defensive-state drag.
- Citations: `[risk_parity, p.1-2, p.10]`; gates `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.
- Scope: 6 pre-committed static configs; selected `stack_gde_heavy` by mean Sharpe / iter009 Sharpe; AnnualDarfEngine net-of-tax; educational/vt_real/ndx_real.
- Result: net Sharpe **0.823 / 0.742 / 0.910**; gates **6/7 / 6/7 / 6/7**; DSR p **5.26e-04 / 3.40e-02 / 1.01e-02**. Kill fired: educational Sharpe <= 1.120 and 0 datasets beat iter009 by +0.10.
- Score breakdown: Sharpe edge 0/25; gates 19/25; DSR 15/15; CAGR floor 15/15; MDD ceiling 0/15; robustness 5/5.
- Lesson: static stacking restores CAGR but loses the HAA canary's drawdown control; drawdowns of 27-42% make the low-turnover tax advantage insufficient for a Sharpe-frontier advance.

### 002 — 2026-04-28 — composite-momentum-standard (MARGINAL, 55/100)

- Hypothesis: Composite Momentum Standard would improve HAA+Gold by using a simpler SPY 200-day regime gate, 8-month top-4 absolute/relative momentum, and inverse-vol sizing.
- Citations: `[stocks_on_the_move, p.21-30]`; gates `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.
- Scope: 1 pre-committed config; risk-on top 4 from `SPYSIM/QQQSIM/VEASIM/TLTSIM/IEFSIM/GLDSIM/KMLMSIM`, inverse 63d vol; risk-off 60% `IEFSIM` + 40% `GLDSIM`; AnnualDarfEngine net-of-tax; educational/vt_real/ndx_real.
- Result: net Sharpe **0.940 / 0.958 / 0.957**; gates **7/7 / 7/7 / 7/7**; DSR p **6.12e-09 / 4.80e-05 / 1.08e-04**. Kill fired: educational Sharpe <= 1.120.
- Score breakdown: Sharpe edge 0/25; gates 25/25; DSR 15/15; CAGR floor 5/15; MDD ceiling 5/15; robustness 5/5.
- Lesson: SPY200 top-4 inverse-vol is statistically robust but return-capped; the IEF/gold risk-off sleeve and annual DARF drag leave too little CAGR to beat HAA+Gold.

### 001 — 2026-04-28 — baa-g12-balanced (MARGINAL, 58/100)

- Hypothesis: BAA-G12 Balanced would improve HAA+Gold by using broader canary breadth and a wider offensive universe.
- Citations: Keller BAA SSRN 4166845; `[stocks_on_the_move, ch.6]`; gates `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.
- Scope: 1 pre-committed config; BAA four-canary 13612W, top-6 offensive SMA(12), top-3 defensive with `CASHX` replacement; AnnualDarfEngine net-of-tax; educational/vt_real/ndx_real.
- Result: net Sharpe **0.975 / 0.792 / 0.782**; gates **7/7 / 7/7 / 6/7**; DSR p **4.85e-08 / 6.78e-04 / 1.37e-03**. Kill fired: educational Sharpe ≤ 1.120.
- Score breakdown: Sharpe edge 0/25; gates 23/25; DSR 15/15; CAGR floor 0/15; MDD ceiling 15/15; robustness 5/5.
- Lesson: plain BAA-G12 is robust but too defensive/tax-dragged; it lowers MDD but sacrifices too much CAGR and never beats iter 009 Sharpe.

---

## Promising unexplored directions (prioritized)

### Tier 1 — bestfolio top-15 + user architecture preferences

#### iter 004 — NTSX + GDE + RSST (static, RSST variant)

**Hypothesis**: Replace KMLMSIM with RSSBSIM (global equity + Treasury
return-stacked) or `SPYSIM + KMLMSIM` proxy for RSST. Tesis: RSST adds
explicit MF exposure with equity component — better in bull equity regimes
vs pure MF (KMLM). Compare vs iter 002.

**Sources**: `[risk_parity, ch.5]` (return stacking). SSRN — Newfound/ReSolve
return-stacking papers. `[stocks_on_the_move, p.21-30]` (MF momentum).

**Kill criterion**: edu Sharpe ≤ iter 002 result (compare static variants only).

**Priority**: MEDIUM — variant of iter 002; only run if 002 is STRONG+.

---

#### iter 005 — HAA + global factor tilt (AVDV/VBRSIM offensive)

**Hypothesis**: HAA architecture (iter 009) but replace VEASIM in offensive
with `0.7 VEASIM + 0.3 VBRSIM` (intl + small-cap value tilt). Tests whether
Avantis-style factor tilt on international sleeve adds Sharpe above plain VEA.

**Sources**: Fama-French 1993 (SCV premium). `[stocks_on_the_move, ch.6]`
(canary architecture). `[advances_fin_ml, p.222-223]` (DSR).
AVDV vs VEA: ~+0.8pp/y Avantis live (6.5y track record).

**Kill criterion**: edu Sharpe ≤ 1.120 (must beat iter 009).

**Priority**: MEDIUM — incremental HAA variant; directionally correct per Avantis rationale.

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
3. **Plain BAA-G12 Balanced in current universe**: robust drawdown reducer
   but too defensive/tax-dragged; net Sharpe 0.975/0.792/0.782 and CAGR
   below 0.8× iter009 on all datasets. `[stocks_on_the_move, ch.6]`
4. **Composite Momentum Standard with SPY200 top-4 inverse-vol**: robust
   7/7 gates × 3 but return-capped; net Sharpe 0.940/0.958/0.957, CAGR
   below HAA+Gold on all datasets, MDD too high on vt/ndx.
5. **Plain static global/factor/CTA stack**: low turnover restores CAGR
   floors but gives up HAA canary drawdown control; net Sharpe
   0.823/0.742/0.910 and MDD 27-42% fail the Sharpe/MDD frontier.

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
