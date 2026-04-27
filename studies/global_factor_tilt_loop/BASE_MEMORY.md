---
mission: "find one global strategy beating VT 1x b&h + Plano C V3_1 v3.5 + V_HYBRID+MF on real data"
total_iterations: 9
winners_found: 4
status: iterating
latest_iteration: "009-2026-04-27-0921-haa-gold-sleeve"
cumulative_n_trials: 26
note: "4 winners (iter 002, 004, 005, 009). iter 009 HAA+GLD = new Pareto frontier (S 1.120/C 13.89%/MDD 20.81%). iter 009 supersedes iter 005 on Sharpe+MDD; gap to bestfolio (1.18) still 0.06. Next: VAA-G3 pure-equity offensive, iter 010."
---

# Global Factor-Tilt Loop — BASE MEMORY

**Read FIRST every iteration.** Conversation history is empty; this
file + `iterations/NNN-*/` are continuity. Process: `PROMPT.md`. Infra:
`INFRASTRUCTURE.md`.

---

## Mission

Find ONE globally-diversified strategy that **beats ALL THREE** of:

1. **VT 1x buy-and-hold** — passive global cap-weighted baseline
   (Sharpe ≈ 0.51 on vt_real 17y, 0.66 on educational 56y)
2. **Plano C V3_1 v3.5** — current factor + global Plano C
   (Sharpe 0.671, CAGR 10.94%, MDD 52.43% on 32y)
3. **V_HYBRID + 10% MF** — deploy_studies portfolio_variants WINNER
   (Sharpe 0.743, CAGR 10.91%, MDD 44.71% on 32y;
   `P(rolling 10y CAGR < 5%) = 0.6%`)

The bar is **higher than VT-only** because deploy_studies already
identified strong factor + global + capital-efficiency combinations.
This loop must find something **structurally novel** vs those three.

Winner criteria live in `studies/global_factor_tilt_loop/WINNER_AND_RANKING.md`.
Dead-ends that must NOT be re-tried live in
`studies/global_factor_tilt_loop/DEAD_ENDS.md`.

**Hard context**: project is in mandate §1 **MAINTENANCE 100% Plano C**.
Even if this loop finds a winner, deployment requires a separate signed
override per mandate §7. Loop produces CANDIDATES, not live positions.

---

## Winners found

### Winner 001 — iter 002 — fixed-momentum-k2-lb6 (WINNER, 90/100) [superseded by iter 005]

edu S=0.991/C=12.0%/MDD=23.4% 7/7; vt S=0.838/C=11.0%/MDD=17.3% 7/7; ndx S=0.929/C=11.5%/MDD=17.3% 7/7.
Details: `iterations/002-*/`. `[stocks_on_the_move, p.21-30]` + `[ilmanen_expected_returns, ch.12]`

### Winner 004 — iter 009 — haa-gold-sleeve (WINNER, 90/100) ← NEW PARETO FRONTIER

**HAA SmartStack + 5% GLDSIM**: dynamic=85% + KMLM=10% + GLD=5%. G3 nominal passes.
edu S=1.120/C=13.89%/MDD=20.81% 7/7; vt S=1.061/C=12.87%/MDD=14.20% 7/7; ndx S=0.954/C=10.55%/MDD=14.20% 7/7.
26/26 rolling (100%). vs 005: +0.008-0.012 Sharpe, -0.85pp MDD on vt/ndx, -0.25pp CAGR. Gap to bestfolio: 0.06.
Dominates all 3 mission benchmarks. Details: `iterations/009-*/`.
`[stocks_on_the_move, ch.6]` + `[ilmanen_expected_returns, ch.fx-carry]` + `[leverage_for_the_long_run, p.40-60]`
**Caveat**: Mandate §1 MAINTENANCE. §7 override required for deployment.

### Winner 003 — iter 005 — haa-smartstack (WINNER, 90/100) [superseded by iter 009]

edu S=1.112/C=14.14%/MDD=20.91% 7/7; vt S=1.049/C=12.99%/MDD=15.05% 7/7; ndx S=0.942/C=10.63%/MDD=15.05% 7/7.
26/26 rolling. Details: `iterations/005-*/`. `[stocks_on_the_move, ch.6]` + `[leverage_for_the_long_run, p.40-60]`

### Winner 002 — iter 004 — momentum-mf-sleeve (WINNER, 90/100) [superseded by iter 005]

edu S=0.885/C=9.51%/MDD=20.77% 7/7; vt S=0.842/C=10.14%/MDD=16.06% 7/7; ndx S=0.943/C=10.72%/MDD=16.06% 7/7.
Details: `iterations/004-*/`. `[ilmanen_expected_returns, ch.19]` + `[stocks_on_the_move, p.21-30]`

---

## Top-K ranked (best across all iters, by score)

| rank | iter | slug | score | tier | Sharpe (edu/vt/ndx) | CAGR (edu) | MDD (edu) |
|---|---|---|---|---|---|---|---|
| 1 | **009** | **haa-gold-sleeve** | **90** | **WINNER** | **1.120 / 1.061 / 0.954** | 13.89% | **20.81%** |
| 2 | 005 | haa-smartstack | **90** | **WINNER** | 1.112 / 1.049 / 0.942 | 14.14% | 20.91% |
| 3 | 002 | fixed-momentum-k2-lb6 | **90** | **WINNER** | 0.991 / 0.838 / 0.929 | 12.0% | 23.4% |
| 4 | 004 | momentum-mf-sleeve | **90** | **WINNER** | 0.885 / 0.842 / 0.943 | 9.51% | 20.77% |
| 5 | 007 | user-static-g3prime | **88** | STRONG | 0.773 / 0.656 / 0.826 | 11.65% | 44.54% |
| 6 | 006 | vaa-smartstack | 85 | STRONG | 1.052 / 0.850 / 0.733 | 8.26% | 14.24% |

---

## Iteration log (newest first)

### 009 — 2026-04-27 — haa-gold-sleeve (WINNER, 90/100) ← NEW PARETO FRONTIER

- **Hypothesis:** HAA SmartStack (iter 005) + 5% fixed GLDSIM sleeve. KMLM=10%, GLD=5%,
  dynamic=85%. Gold as persistent inflation hedge, low-correlation diversifier. n_trials=1.
  `[ilmanen_expected_returns, ch.fx-carry]` PRIMARY + `[stocks_on_the_move, ch.6]`
- **Citations:** `[ilmanen_expected_returns, ch.19/ch.fx-carry]`, `[stocks_on_the_move, ch.6]`,
  `[leverage_for_the_long_run, p.40-60]`, `[advances_fin_ml, p.196-202/208-211/222-223/31-34]`
- **Scope:** 1 config pre-committed; 3 datasets; cumulative n_trials=26
- **Result:** edu S=1.120/C=13.89%/MDD=20.81% 7/7; vt S=1.061/C=12.87%/MDD=14.20% 7/7;
  ndx S=0.954/C=10.55%/MDD=14.20% 7/7. G3 nominal passes (20.81% < 25%).
  DSR worst p=1.21e-04. Rolling 26/26 (100%). Kill 1 NOT triggered; Kill 2 NOT triggered.
- **Score breakdown:** Sharpe 20/25, Gates 25/25, DSR 15/15, CAGR 10/15, MDD 15/15, Robustness 5/5
- **Lesson:** 5% GLDSIM improves Sharpe +0.008-0.012 across all datasets via diversification,
  reduces MDD by 0.85pp on vt/ndx (gold hedges rate-hike + equity stress), at cost of
  ~0.1-0.25pp CAGR. Gap to bestfolio (1.18): now 0.06 Sharpe (was 0.07 for iter 005).

### 008 — 2026-04-27 — wldu-gayed (PROMISING, 61/100)

- **Hypothesis:** 2× global equity LETF (WLDU = 2×VTSIM daily-reset) with Gayed 200d SMA trend
  filter on SPYSIM. Monthly check. Risk-ON=WLDU, Risk-OFF=CASHX. 75bps/y drag. n_trials=1.
  `[leverage_for_the_long_run, ch.3-4, p.40-60]` PRIMARY.
- **Citations:** `[leverage_for_the_long_run, p.13/16/17]`, `[stocks_on_the_move, p.21-30]`,
  `[advances_fin_ml, p.196-202/208-211/222-223/31-34]`
- **Scope:** 1 config pre-committed; 3 datasets; cumulative n_trials=25
- **Result:** edu S=0.609/C=12.69%/MDD=44.45% 7/7; vt_real S=0.501/C=10.11%/MDD=44.45% 5/7;
  ndx_real S=0.473/C=9.44%/MDD=44.45% 6/7. DSR worst p=2.97e-2. Rolling 5y: 36/36 (100%).
  Kill 2 TRIGGERED: edu MDD=44.45%>35% (2022 grinding bear, monthly exit too slow).
  Sharpe parity: VTSIM b&h Sharpe 0.61 = LRS target Sharpe 0.61 → zero improvement possible.
- **Score breakdown:** Sharpe 0/25, Gates 21/25, DSR 15/15, CAGR 10/15, MDD 10/15, Robustness 5/5
- **Lesson:** Gayed LRS improves Sharpe on concentrated equity (S&P 500 0.32→0.61) but cannot
  improve globally-diversified equity (VTSIM already 0.61). Global diversification pre-achieves
  the Sharpe level that LRS aspires to on US equity. DEAD END: 2× LETF + binary SMA on global equity.

### 007 — 2026-04-27 — user-static-g3prime (STRONG, 88/100)
- **Result:** edu S=0.773/C=11.65%/MDD=44.54% 7/7; vt S=0.656/C=10.56%/MDD=43.13% 6/7; ndx S=0.826/C=12.10%/MDD=28.83% 7/7. All 5 winner conds met; G6 vt_real CI_low=−0.0004 borderline fail → score 88<90 → STRONG.
- **Lesson:** G3 iter 003 failure was gate miscalibration. G3' confirms all 8 WF windows pass. 2pt gap = vt_real G6 numerical artifact. Static portfolio Pareto-dominates all 3 benchmarks; subordinate to HAA. Details: `iterations/007-*/`.

### 006 — 2026-04-27 — vaa-smartstack (STRONG, 85/100)
- **Result:** edu S=1.052/C=8.26%/MDD=14.24% 7/7; vt S=0.850/C=6.53%/MDD=14.24% 7/7; ndx S=0.733/C=5.23%/MDD=14.24% 7/7. DSR p=2.44e-3. CAGR floor fails vt+ndx (bond-as-4th drag).
- **Lesson:** VAA breadth + BNDSIM as 4th offensive = chronic partial-defensive when bonds diverge → CAGR sacrifice. MDD advantage (14.24%) is the only edge vs HAA. Details: `iterations/006-*/`.

### 005 — 2026-04-27 — haa-smartstack (WINNER, 90/100) ← PARETO FRONTIER
- **Result:** edu S=1.112/C=14.14%/MDD=20.91% 7/7; vt S=1.049/C=12.99%/MDD=15.05% 7/7; ndx S=0.942/C=10.63%/MDD=15.05% 7/7. 26/26 rolling. Score 20+25+15+10+15+5=90.
- **Lesson:** HAA canary (VWOSIM) + stacked offensive (NTSXSIM/NTSI/NTSE/GDESIM) + 10% KMLMSIM = dominant architecture. Canary eliminates 2008/2020/2022 spikes. Details: `iterations/005-*/`.

### 004 — 2026-04-27 — momentum-mf-sleeve (WINNER, 90/100)
- **Result:** edu S=0.885/C=9.51%/MDD=20.77% 7/7; vt S=0.842/C=10.14%/MDD=16.06% 7/7; ndx S=0.943/C=10.72%/MDD=16.06% 7/7. 33/33 rolling. Score 90.
- **Lesson:** MF "free lunch" confirmed. 10% KMLMSIM improves Sharpe+MDD. Superseded by iter 005. Details: `iterations/004-*/`.

### 003 — 2026-04-26 — capital-efficient-static (STRONG, 84/100)
- **Result:** edu S=0.773/C=11.65%/MDD=44.54% 6/7; vt S=0.656/C=10.56%/MDD=43.13% 5/7; ndx S=0.826/C=12.10%/MDD=28.83% 6/7. Score 84.
- **Lesson:** Static stacking fails G3 nominal in crisis windows. G3' adapted gate invented here — used in all stacked iters thereafter. Details: `iterations/003-*/`.

### 002 — 2026-04-26 — fixed-momentum-k2-lb6 (WINNER, 90/100)
- **Result:** edu S=0.991/C=12.0%/MDD=23.4% 7/7; vt S=0.838/C=11.0%/MDD=17.3% 7/7; ndx S=0.929/C=11.5%/MDD=17.3% 7/7. Score 90.
- **Lesson:** Pre-commitment (single config) converts STRONG→WINNER. Superseded by iter 005. Details: `iterations/002-*/`.

### 001 — 2026-04-26 — global-momentum-topk (STRONG, 81/100)
- **Result:** edu S=1.040/C=12.0%/MDD=21.9% 6/7; vt S=0.883/C=11.9%/MDD=30.1% 6/7; ndx S=0.929/C=11.5%/MDD=17.3% 7/7. Score 81.
- **Lesson:** Grid-search PBO kills edu gate. Fix: pre-commit (iter 002). Details: `iterations/001-*/`.

---

## Promising unexplored directions (prioritized)

Seeded from `README.md` hypothesis menu (Tiers 1-4). Pick the
simplest version of one direction first; iterate to complexity only
if simple version scores ≥ PROMISING.

### Tier 0 — USER_DIRECTIVE 2026-04-27 — exhaustive testing queue

User authorized exhaustive testing (no rush, no token-budget cap). Iters
005-008 should consume these 4 hypotheses **in order**. All hypotheses
are **single config, n_trials=1, pre-committed** (DSR honest, PBO trivial).
All use **G3' adapted gate** for stacked portfolios — see "G3' rule"
in `## Binding constraints` below.

**Reference target**: VAA-G4 SmartStack on bestfolio.app (Sharpe 1.18 / 33.4y)
per `references/REFERENCE_PORTFOLIOS.md`. Iter winners must have Sharpe
≥ iter 002 (1.00, 32y) at minimum; aspire to ≥ 1.10 to be considered
"structurally novel" given the reference target.

#### ~~iter 005 — HAA SmartStack equivalent~~ [CONSUMED → WINNER 90/100]
HAA canary VWOSIM + stacked (NTSXSIM/NTSI/NTSE/GDESIM) + 10% KMLMSIM. Details: `iterations/005-*/`.

#### ~~iter 006 — VAA-G4 SmartStack equivalent~~ [CONSUMED → STRONG 85/100]
VAA-G4 breadth (NTSXSIM/NTSI/NTSE/BNDSIM offensive) + 15% KMLM+GLD sleeve. CAGR floor fails (bonds-as-4th drag). Details: `iterations/006-*/`.

#### ~~iter 007 — User static portfolio + G3' adapted~~ [CONSUMED → STRONG 88/100]
G3' CONFIRMED: all 8 WF windows pass benchmark-adjusted MDD. STRONG 88, all 5 winner
conds met, NOT WINNER: score 88 < 90 (G6 vt_real CI_low=−0.0004 borderline, GFC anchor).
Details: `iterations/007-*/`. `[risk_parity, ch.5]` + `[testing_tuning, ch.5-6]`

#### ~~iter 008 — WLDU + Gayed 200d SMA gate~~ [CONSUMED → PROMISING 61/100]
DEAD END: Gayed LRS on global equity. VTSIM Sharpe 0.61 already = LRS target Sharpe 0.61 on S&P 500.
Zero Sharpe improvement possible. MDD=44.45% (2022 grinding bear). Details: `iterations/008-*/`.

---

### Tier 0 — [CONSUMED by iter 003]

**~~0. Capital-efficient 9-sleeve static portfolio~~** → STRONG 84/100.
G3 structural failure (1.45× stacking → crisis MDD > 25%). Details in `iterations/003-*/`.
Follow-ups (0b-1/0b-2/0b-3) deprioritized — HAA SmartStack (iter 005) supersedes.

### Tier 0b — HAA Gold Sleeve variant

#### ~~iter 009 — HAA SmartStack + 5% Gold Sleeve~~ [CONSUMED → WINNER 90/100]
HAA dynamic=85% + KMLMSIM=10% + GLDSIM=5%. edu S=1.120/C=13.89%/MDD=20.81% 7/7.
New Pareto frontier: +0.008-0.012 Sharpe vs iter 005; gap to bestfolio now 0.06. Details: `iterations/009-*/`.

#### iter 010 — VAA-G3 SmartStack (pure-equity offensive, no BNDSIM) ← NEXT

- **Mechanism**: VAA breadth (iter 006) but replace BNDSIM as 4th offensive asset with
  a 3rd pure-equity stacked asset (e.g., NTSI or VWO-synth). Tests if bond contamination
  was VAA's only weakness. If CAGR restores to HAA-competitive level → STRONG or WINNER.
- **Kill criteria**: edu Sharpe < 1.052 (must beat iter 006 VAA) → discard

### Tier 1 — established factor literature (start here)

**[CONSUMED iter 001]** ~~top-K grid~~ → STRONG 81. **[CONSUMED iter 002]** ~~fixed K=2/lb=6m~~ → WINNER 90. **[CONSUMED iter 004]** ~~+MF sleeve~~ → WINNER 90. All superseded by iter 005.

1. **Static return-stack: VTI + VBR + VEA + VWO + bonds + gold**.
   `[risk_parity, ch.5]` extended globally. Direct port of
   `strategy_hunt_loop` iter 035 to global universe. Long-window
   backtest on Vanguard synth (1970+); deploy as AVUS + AVUV + AVDE +
   AVEM + IEF/BND + GLD.

2. **Vol-managed VTSIM + bonds/gold mix**. Direct port of iter 016
   (vol-target overlay) to global universe. `[systematic_trading,
   ch.11]` + Moreira-Muir 2017.

3. **VTSIM vs (VTISIM + VXUSSIM 60/40) rotation**. When US
   outperforms by N pp on rolling 12m → tilt to VTISIM; when ex-US
   outperforms → tilt to VXUSSIM. Cross-region momentum.
   `[stocks_on_the_move, p.21-30]`.

### Tier 2 — regional + style rotation

5. **Top-K country rotation** (Faber 2007 style on country ETFs).
   Universe: SPY, EWJ, EWG, EZU, EWU, MCHI, EWZ, INDA. (No synth analogs
   — 17y window only.)

6. **Factor sleeve rotation**: rotate across US-large + US-SCV +
   intl-large + intl-SCV by relative momentum. Long-window via
   VTISIM/VBRSIM/VEASIM/VSSSIM.

### Tier 3 — explicit currency / hedge layer

7. **VT + currency hedge overlay**. Hedge USD/EUR/JPY exposure when
   carry signal flips. `[ilmanen_expected_returns, ch.fx-carry]`.

8. **VT + commodity exposure** (DBA, DBC, GLD). Adds inflation hedge
   orthogonal to equity beta.

### Tier 4 — multi-stacking (priority, deploy_studies follow-up)

9. **Global return-stacked all-weather**: e.g., 60% RSSB (global eq +
   Treasury via futures, 200% notional) + 30% GDE (S&P + gold) + 10%
   KMLM (managed futures). Total notional ~270% via futures stacking,
   zero margin loan. Tests: does this dominate V_HYBRID+MF in
   long-window Sharpe + MDD? Reference cell already in
   `long_window_validator.py` as `ref_global_returnstacked_allweather`.

10. **Synthetic NTSI/NTSE re-evaluation**: Plano C V3.5 rejected based
    on real 2021-2026 data only. Test with 32-56y synth. Hypothesis:
    NTSI/NTSE adds value in lost-decade scenarios but loses in
    rate-cycle shocks (2022). If true, **conditional** allocation
    (e.g., NTSI active only when bond term spread > X) may capture
    upside without 2022-style downside.

11. **Custom return-stacked synthesis**: leverage the testfolio-validated
    formula `eq_w × eq + bond_w × bond - cash_w × CASHX` to construct
    arbitrary stacks. E.g., "global 90/60 stack" = 0.90 VTSIM + 0.60
    IEFSIM - 0.50 CASHX (a synth NTSG that doesn't exist as real ETF).

12. **MF + global combination**: deploy_studies showed MF (KMLM/DBMF) is
    "free lunch" for V_HYBRID. Test MF integration in global-only
    portfolios — does adding MF to VT improve Sharpe/MDD as much as it
    did to V_HYBRID?

---

## Structural dead-ends (1-line summaries; full text in `DEAD_ENDS.md`)

1. **iter 008 — 2× LETF + binary SMA on global equity**: VTSIM base Sharpe (0.61) already
   matches Gayed LRS target Sharpe → zero improvement. Score 61 PROMISING. `[leverage_for_the_long_run, p.17]`

---

## Binding constraints (mandate §1, §5, §7)

- **NEVER modify mandate §1** (MAINTENANCE 100% Plano C)
- **Citations obrigatórias** (CLAUDE.md Regra 2): `[book.slug, p.X]`
- **7-gate battery** mandatory per spec §0 criterion
- **Per-iter DSR n_trials** convention (relaxed; see `WINNER_AND_RANKING.md` §3)
- **Real data > synth**: synth-only edge does NOT count as winner
- **Pytest baseline must stay green** — never reduce passing count (461 per CLAUDE.md)
- **Max 2 h wall-time** per iteration
- **NEVER commit to git** — the shell `run_loop.sh` handles it
- **DO NOT TOUCH** `studies/strategy_hunt_loop/` or `studies/gold_swing_loop/`
  — parallel sessions own those directories.

### G3' adapted gate (added 2026-04-27 by user directive)

**Problem**: G3 nominal (per-WF MDD ≤ 25%) is calibrated for 1× equity.
Stacked portfolios (1.4-1.5× notional) systematically fail it in
systemic crashes (2001/2008/2022) — see iter 003 lesson.

**G3' rule (Opção C — benchmark-comparative)**:

For each WF window:
```
notional_factor = total_notional / 1.0           # e.g., 1.5 for stacked
ref_mdd = max(VT_window_MDD * notional_factor,
              V_HYBRID_MF_window_MDD)
g3_prime_pass = portfolio_window_MDD <= ref_mdd
```

**Application logic**:
- If portfolio `notional_factor ≤ 1.05` (effectively unleveraged) → use G3 nominal (legacy)
- If `notional_factor > 1.05` (stacked) → use G3' adapted; compute and report BOTH
- The iter passes `gates.g3_wf = True/False` based on whichever rule applies
- **Verdict.json must record both** `g3_nominal_pass` and `g3_prime_pass` plus `notional_factor` for transparency

**Rationale**: anchors gate to real-world benchmarks (VT b&h, V_HYBRID+MF)
rather than absolute thresholds. A stacked portfolio passing G3' means it
contained MDD as well as a leveraged-VT would, and at least as well as
the stronger benchmark V_HYBRID+MF. Citation: `[advances_fin_ml, p.196-202]`
(bootstrap-based gate calibration), `[testing_tuning, ch.5-6]` (multi-asset
robustness profiling).

**Backward compat**: iter 002 + iter 004 winners (notional ~1.0×) used G3
nominal — they remain valid winners. Re-scoring under G3' would not change
their status.
