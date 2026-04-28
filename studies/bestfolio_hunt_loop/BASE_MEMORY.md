---
mission: "beat iter 009 HAA+Gold (Sharpe 1.120 edu) and close the gap to bestfolio #1 (Sharpe 1.18)"
total_iterations: 7
winners_found: 0
status: in_progress
latest_iteration: "007-2026-04-28-0958-haa-defensive-kmlm-cash"
cumulative_n_trials: 24
note: "loop initialized 2026-04-27. benchmark = iter009 HAA+Gold. tax model = AnnualDarfEngine (Lei 14.754/2023). RSIT synth tested and closed until live data; simple HAA KMLM/CASH defensive swaps closed."
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

*(empty — no winners after 7 iterations)*

| # | iter | slug | status | edu S/C/MDD | note |
|---|---|---|---|---|---|

---

## Top-K strategies ranked

| rank | iter | slug | score | tier | Sharpe (edu/vt/ndx) | CAGR (edu) | MDD (edu) |
|---|---|---|---|---|---|---|---|
| 1 | 007 | haa-defensive-kmlm-cash | 75 | STRONG | 0.983/0.954/0.860 | 12.15% | 20.81% |
| 2 | 006 | haa-rsit-synth | 71 | PROMISING | 0.869/0.897/0.837 | 11.13% | 22.12% |
| 3 | 005 | haa-rsst-rssb-cta | 70 | PROMISING | 0.953/1.028/0.946 | 11.11% | 16.98% |
| 4 | 004 | haa-global-factor-tilt | 69 | PROMISING | 0.990/0.955/0.861 | 12.21% | 20.71% |
| 5 | 001 | baa-g12-balanced | 58 | MARGINAL | 0.975/0.792/0.782 | 10.60% | 16.34% |

---

## Iteration log (newest first)

### 007 — 2026-04-28 — haa-defensive-kmlm-cash (STRONG, 75/100)

- Hypothesis: Keep iter 009 HAA+Gold offensive shell intact but replace only the defensive-state candidates with KMLM/CASH variants to reduce false-defensive Sharpe drag.
- Citations: `[stocks_on_the_move, ch.6]`; `[risk_parity, ch.5]`; gates `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.
- Scope: 4 pre-committed defensive configs; selected `orig_ief_bnd_cash` by mean Sharpe / iter009 Sharpe; AnnualDarfEngine net-of-tax; educational/vt_real/ndx_real.
- Result: net Sharpe **0.983 / 0.954 / 0.860**; gates **7/7 / 7/7 / 7/7**; DSR p **8.88e-06 / 2.36e-03 / 1.15e-02**. Kill fired: educational Sharpe <= 1.120 and 0 datasets beat iter009 by +0.10.
- Score breakdown: Sharpe edge 0/25; gates 25/25; DSR 15/15; CAGR floor 15/15; MDD ceiling 15/15; robustness 5/5.
- Lesson: The original `IEFSIM/BNDSIM/CASHX` defense beat KMLM/CASH swaps; KMLM-heavy defense raised MDD to 27.49%, and cash-only cut CAGR. The missing edge is in canary timing, not simple defensive assets.

### 006 — 2026-04-28 — haa-rsit-synth (PROMISING, 71/100)

- Hypothesis: Keep iter 009 HAA+Gold intact but add synthetic `RSIT_PROXY = VEASIM + KMLMSIM - 50bps/y` as a rankable international-equity + managed-futures offensive sleeve.
- Citations: `[risk_parity, ch.5]`; `[stocks_on_the_move, ch.6]`; gates `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.
- Scope: 4 pre-committed RSIT-centered HAA offensive-set configs; selected `rsit_with_ntsi` by mean Sharpe / iter009 Sharpe; AnnualDarfEngine net-of-tax; educational/vt_real/ndx_real. Marked INCOMPLETE synthetic until live RSIT data exists.
- Result: net Sharpe **0.869 / 0.897 / 0.837**; gates **6/7 / 6/7 / 7/7**; DSR p **1.23e-04 / 4.93e-03 / 1.52e-02**. Kill fired: educational Sharpe <= iter004 0.990 and 0 datasets beat iter009 by +0.10.
- Score breakdown: Sharpe edge 0/25; gates 21/25; DSR 15/15; CAGR floor 15/15; MDD ceiling 15/15; robustness 5/5.
- Lesson: RSIT-style MF-on-international-equity clears CAGR/MDD floors but worsens Sharpe and PBO stability; HAA+Gold already has enough MF convexity, so the missing edge is not another embedded managed-futures layer.

### 005 — 2026-04-28 — haa-rsst-rssb-cta (PROMISING, 70/100)

- Hypothesis: Keep iter 009 HAA+Gold intact but replace the offensive candidates with simple RSST/RSSB/CTA return-stacked sets so HAA can rank the diversifiers instead of holding only fixed KMLM/gold.
- Citations: `[risk_parity, ch.5]`; `[stocks_on_the_move, p.21-30]`; gates `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.
- Scope: 4 pre-committed HAA offensive-set configs; selected `rssb_cta_balanced` by mean Sharpe / iter009 Sharpe; AnnualDarfEngine net-of-tax; educational/vt_real/ndx_real.
- Result: net Sharpe **0.953 / 1.028 / 0.946**; gates **7/7 / 7/7 / 7/7**; DSR p **1.74e-05 / 8.75e-04 / 4.55e-03**. Kill fired: educational Sharpe <= iter004 0.990 and 0 datasets beat iter009 by +0.10.
- Score breakdown: Sharpe edge 0/25; gates 25/25; DSR 15/15; CAGR floor 10/15; MDD ceiling 15/15; robustness 5/5.
- Lesson: HAA can rank stacked sleeves robustly, but extra RSST/RSSB/CTA exposure mostly trades CAGR for lower MDD; after iter009 the missing edge is incremental return, not more diversifier convexity.

### 004 — 2026-04-28 — haa-global-factor-tilt (PROMISING, 69/100)

- Hypothesis: Keep iter 009 HAA+Gold intact but replace the plain international stacked offensive sleeve with a simple `VEASIM/VBRSIM/VSSSIM` small/value tilt ladder.
- Citations: `[stocks_on_the_move, ch.6]`; `[leverage_for_the_long_run, p.40-60]`; gates `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.
- Scope: 4 pre-committed HAA factor-tilt configs; selected `tilt_scv20` by mean Sharpe / iter009 Sharpe; AnnualDarfEngine net-of-tax; educational/vt_real/ndx_real.
- Result: net Sharpe **0.990 / 0.955 / 0.861**; gates **6/7 / 6/7 / 6/7**; DSR p **7.62e-06 / 2.32e-03 / 1.15e-02**. Kill fired: educational Sharpe <= 1.120 and 0 datasets beat iter009 by +0.10.
- Score breakdown: Sharpe edge 0/25; gates 19/25; DSR 15/15; CAGR floor 15/15; MDD ceiling 15/15; robustness 5/5.
- Lesson: HAA's canary still protects drawdown, but simple international small/value tilting mostly reshuffles risk-on equity exposure; PBO 0.885/0.869/0.694 makes the chosen tilt unstable and not a Sharpe-frontier advance.

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

### Tier 1 — active next directions after iter 007

#### Next — dual-canary HAA (`VWOSIM` + `VTISIM`) — CANARY TIMING ONLY

**Hypothesis**: Keep iter 009 HAA+Gold assets unchanged and alter only the
binary HAA risk-on/risk-off trigger. A second broad-equity canary may reduce
false defensive states without diluting offensive/defensive sleeves.

**Sources**: `[stocks_on_the_move, ch.6]` (relative/absolute momentum);
`[advances_fin_ml, p.208-211]` (grid overfit control).

**Kill criterion**: selected educational net Sharpe ≤ 1.120 or zero datasets
beat iter009 by +0.10 Sharpe.

**Priority**: HIGH — directly follows iter 007 lesson; structurally different
from BAA breadth because it preserves a binary HAA switch and the same assets.

#### Next — Gayed trend input as HAA canary, not standalone LETF

**Hypothesis**: Replace or augment `VWOSIM` canary with a simple SPY/VT trend
signal to handle gradual bear markets while keeping HAA+Gold allocation intact.

**Sources**: `[leverage_for_the_long_run, p.40-60]`; `[stocks_on_the_move, ch.6]`.

**Kill criterion**: selected educational net Sharpe ≤ 1.120 or any real-data
window has MDD > iter009 + 5pp.

**Priority**: MEDIUM — structurally different from DE-001 because the trend
signal controls HAA risk state only; it is not a 2x single-asset LETF system.

### Tier 1 — bestfolio top-15 + user architecture preferences

#### Later — NTSX + GDE + RSST (static, RSST variant) — DO NOT RUN AS PLAIN STATIC

**Hypothesis**: Replace KMLMSIM with RSSBSIM (global equity + Treasury
return-stacked) or `SPYSIM + KMLMSIM` proxy for RSST. Tesis: RSST adds
explicit MF exposure with equity component — better in bull equity regimes
vs pure MF (KMLM). Compare vs iter 002.

**Sources**: `[risk_parity, ch.5]` (return stacking). SSRN — Newfound/ReSolve
return-stacking papers. `[stocks_on_the_move, p.21-30]` (MF momentum).

**Kill criterion**: edu Sharpe ≤ iter 002 result (compare static variants only).
Plain static form is closed by DE-005; only revisit with an explicit drawdown
control overlay or a CAGR-first objective.

**Priority**: BLOCKED for the active Sharpe-frontier hunt — do not test as a
pure static stack again.

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
6. **Simple HAA international small/value tilt**: preserves HAA MDD but
   sacrifices Sharpe/CAGR; net Sharpe 0.990/0.955/0.861 and PBO
   0.885/0.869/0.694 show unstable tilt selection. `[stocks_on_the_move, ch.6]`
7. **Simple HAA RSST/RSSB/CTA offensive substitution**: robust 7/7 gates but
   lower-return; net Sharpe 0.953/1.028/0.946 and zero +0.10 Sharpe edges.
   Extra stacked diversifiers trade CAGR for MDD after iter009. `[risk_parity, ch.5]`
8. **Synthetic HAA RSIT offensive sleeve**: clears CAGR/MDD and DSR but loses
   Sharpe badly; net Sharpe 0.869/0.897/0.837 and PBO 0.714/0.845 on global
   windows. More embedded MF on international equity is not the missing edge.
   `[risk_parity, ch.5]`
9. **Simple HAA KMLM/CASH defensive swaps**: statistically robust but no
   improvement; original `IEFSIM/BNDSIM/CASHX` defense was selected with net
   Sharpe 0.983/0.954/0.860, while KMLM-heavy defense raised MDD to 27.49%.
   The next edge must change canary timing, not defensive assets.
   `[stocks_on_the_move, ch.6]`

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
